from src.config.supabase import maybe_row, supabase
from src.dependencies.exceptions import AppError
from src.schemas.admin_schema import FlagActionSchema, ModerateSchema, UpdateRoleSchema
from src.schemas.company_schema import (
    CompanyAdminCreateSchema,
    CompanyMergeSchema,
    CompanyUpdateSchema,
)
from src.services.companies_service import _slug
from src.services.auth_helpers import invalidate_ban_cache
from src.utils.sanitize import clean_text

_FLAG_TABLES = {"question": "interview_questions", "review": "interview_reviews"}


def _audit(
    actor_id: str,
    action: str,
    target_type: str,
    target_id: str,
    detail: dict | None = None,
) -> None:
    """Every admin mutation records here. Failures surface loudly, by design."""
    supabase.table("admin_audit_log").insert({
        "actor_id":    actor_id,
        "action":      action,
        "target_type": target_type,
        "target_id":   target_id,
        "detail":      detail,
    }).execute()


def get_queue() -> dict:
    questions = (
        supabase.table("interview_questions")
        .select("*")
        .eq("status", "pending")
        .order("created_at")
        .execute()
    ).data

    reviews = (
        supabase.table("interview_reviews")
        .select("*")
        .eq("status", "pending")
        .order("created_at")
        .execute()
    ).data

    companies = (
        supabase.table("companies")
        .select("*")
        .eq("status", "pending")
        .order("created_at")
        .execute()
    ).data

    return {"data": {"questions": questions, "reviews": reviews, "companies": companies}}


def moderate_question(user: dict, question_id: str, data: ModerateSchema) -> dict:
    q = maybe_row(
        supabase.table("interview_questions")
        .select("submitted_by, status")
        .eq("id", question_id)
    )
    if not q:
        raise AppError(404, {"error": "Question not found"})

    admin_note = clean_text(data.admin_note or "")

    supabase.table("interview_questions").update({
        "status":      data.status,
        "admin_note":  admin_note or None,
        "reviewed_by": user["sub"],
        "reviewed_at": "now()",
    }).eq("id", question_id).execute()

    _audit(user["sub"], f"question_{data.status}", "question", question_id,
           {"note": admin_note or None})
    return {"message": f"Question {data.status}"}


def moderate_review(user: dict, review_id: str, data: ModerateSchema) -> dict:
    r = maybe_row(
        supabase.table("interview_reviews").select("submitted_by").eq("id", review_id)
    )
    if not r:
        raise AppError(404, {"error": "Review not found"})

    admin_note = clean_text(data.admin_note or "")

    supabase.table("interview_reviews").update({
        "status":      data.status,
        "admin_note":  admin_note or None,
        "reviewed_by": user["sub"],
        "reviewed_at": "now()",
    }).eq("id", review_id).execute()

    _audit(user["sub"], f"review_{data.status}", "review", review_id,
           {"note": admin_note or None})
    return {"message": f"Review {data.status}"}


def moderate_company(
    user: dict, company_id: str, data: CompanyUpdateSchema | None = None
) -> dict:
    fields = data.model_dump(exclude_none=True) if data else {}
    # An empty body still just approves, keeping the queue's behaviour.
    fields.setdefault("status", "approved")
    if "name" in fields:
        fields["name"] = fields["name"].strip()
        fields["slug"] = _slug(fields["name"])

    result = (
        supabase.table("companies").update(fields).eq("id", company_id).execute()
    )
    if not result.data:
        raise AppError(404, {"error": "Company not found"})

    action = "company_updated" if len(fields) > 1 else "company_approved"
    _audit(user["sub"], action, "company", company_id, fields)
    return {"message": "Company updated", "data": result.data[0]}


def list_companies(
    page: int = 1, limit: int = 20, q: str | None = None, status: str | None = None
) -> dict:
    """Admin view: every company, not only approved ones."""
    page = max(1, page)
    limit = min(50, max(1, limit))
    offset = (page - 1) * limit

    query = supabase.table("companies").select("*", count="exact")
    if q:
        query = query.ilike("name", f"%{q}%")
    if status:
        query = query.eq("status", status)

    result = query.order("name").range(offset, offset + limit - 1).execute()
    return {"data": result.data, "count": result.count}


def create_company(user: dict, data: CompanyAdminCreateSchema) -> dict:
    name = data.name.strip()
    if not name:
        raise AppError(400, {"errors": {"name": ["must not be empty"]}})
    if maybe_row(supabase.table("companies").select("id").ilike("name", name)):
        raise AppError(409, {"error": "Company already exists"})

    result = supabase.table("companies").insert({
        **data.model_dump(exclude_none=True),
        "name":   name,
        "slug":   _slug(name),
        "status": "approved",   # admin-created companies skip the queue
    }).execute()

    company = result.data[0]
    _audit(user["sub"], "company_created", "company", company["id"], {"name": name})
    return {"data": company, "message": "Company created"}


def merge_companies(user: dict, company_id: str, data: CompanyMergeSchema) -> dict:
    """Move all content off company_id onto into_id, then delete the duplicate."""
    if company_id == data.into_id:
        raise AppError(400, {"error": "Cannot merge a company into itself"})

    loser = maybe_row(supabase.table("companies").select("*").eq("id", company_id))
    winner = maybe_row(supabase.table("companies").select("*").eq("id", data.into_id))
    if not loser or not winner:
        raise AppError(404, {"error": "Company not found"})

    # Only these two tables reference companies.id; applications store a name.
    moved = {}
    for table in ("interview_questions", "interview_reviews"):
        rows = (
            supabase.table(table)
            .update({"company_id": data.into_id})
            .eq("company_id", company_id)
            .execute()
        ).data
        moved[table] = len(rows or [])

    supabase.table("companies").delete().eq("id", company_id).execute()

    _audit(user["sub"], "company_merged", "company", data.into_id,
           {"merged_from": company_id, "merged_name": loser["name"], **moved})
    return {"message": f"Merged {loser['name']} into {winner['name']}", "data": moved}


def list_flags() -> dict:
    flags = (
        supabase.table("content_flags")
        .select("*")
        .eq("status", "open")
        .order("created_at")
        .execute()
    ).data

    # ponytail: one lookup per flag — open flags are few. Batch per content_type if the queue grows.
    for flag in flags:
        row = (
            supabase.table(_FLAG_TABLES[flag["content_type"]])
            .select("*")
            .eq("id", flag["content_id"])
            .limit(1)
            .execute()
        )
        flag["content"] = row.data[0] if row.data else None

    return {"data": flags}


def resolve_flag(user: dict, flag_id: str, data: FlagActionSchema) -> dict:
    result = (
        supabase.table("content_flags")
        .update({"status": data.status})
        .eq("id", flag_id)
        .eq("status", "open")
        .execute()
    )
    if not result.data:
        raise AppError(404, {"error": "Open flag not found"})

    _audit(user["sub"], f"flag_{data.status}", "flag", flag_id)
    return {"message": f"Flag {data.status}"}


def list_users(page: int = 1, limit: int = 20) -> dict:
    page = max(1, page)
    limit = min(50, max(1, limit))
    offset = (page - 1) * limit

    result = (
        supabase.table("users")
        .select("*", count="exact")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return {"data": result.data, "count": result.count}


def _require_user(user_id: str) -> None:
    if not maybe_row(supabase.table("users").select("id").eq("id", user_id)):
        raise AppError(404, {"error": "User not found"})


def update_user_role(actor: dict, user_id: str, data: UpdateRoleSchema) -> dict:
    # Keeps at least one super admin: the actor is one and cannot demote themselves.
    if user_id == actor["sub"] and data.role != "super_admin":
        raise AppError(400, {"error": "You cannot remove your own super admin role"})

    _require_user(user_id)
    supabase.table("users").update({"role": data.role}).eq("id", user_id).execute()
    supabase.auth.admin.update_user_by_id(
        user_id, {"user_metadata": {"role": data.role}}
    )

    _audit(actor["sub"], "role_updated", "user", user_id, {"role": data.role})
    return {"message": f"Role updated to {data.role}"}


def warn_user(actor: dict, user_id: str) -> dict:
    _require_user(user_id)
    # ponytail: recorded only — delivery needs the notification service wired up.
    _audit(actor["sub"], "user_warned", "user", user_id)
    return {"message": "Warning recorded"}


def suspend_user(actor: dict, user_id: str) -> dict:
    if user_id == actor["sub"]:
        raise AppError(400, {"error": "You cannot suspend yourself"})

    _require_user(user_id)
    supabase.auth.admin.update_user_by_id(user_id, {"ban_duration": "876600h"})
    # ponytail: display mirror — auth.users stays the source of truth for login blocking.
    supabase.table("users").update({"suspended_at": "now()"}).eq("id", user_id).execute()
    invalidate_ban_cache(user_id)

    _audit(actor["sub"], "user_suspended", "user", user_id)
    return {"message": "User suspended"}


def unsuspend_user(actor: dict, user_id: str) -> dict:
    _require_user(user_id)
    supabase.auth.admin.update_user_by_id(user_id, {"ban_duration": "none"})
    supabase.table("users").update({"suspended_at": None}).eq("id", user_id).execute()
    invalidate_ban_cache(user_id)

    _audit(actor["sub"], "user_unsuspended", "user", user_id)
    return {"message": "User unsuspended"}
