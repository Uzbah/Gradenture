from src.config.supabase import maybe_row, supabase
from src.dependencies.exceptions import AppError
from src.schemas.admin_schema import FlagActionSchema, ModerateSchema, UpdateRoleSchema
from src.schemas.company_schema import (
    CompanyAdminCreateSchema,
    CompanyEditDecisionSchema,
    CompanyManagerGrantSchema,
    CompanyMergeSchema,
    CompanyUpdateSchema,
)
from src.services.companies_service import _slug
from src.services import email_service
from src.services.auth_helpers import invalidate_ban_cache
from src.utils.sanitize import clean_text

_FLAG_TABLES = {"question": "interview_questions", "review": "interview_reviews"}


def _audit(
    actor_id: str,
    action: str,
    target_type: str,
    target_id: str | None,
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


def _email_of(user_id: str | None) -> str | None:
    """Recipient for a notification; None when the user is gone (submitted_by is SET NULL)."""
    if not user_id:
        return None
    row = maybe_row(supabase.table("users").select("email").eq("id", user_id))
    return row["email"] if row else None


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


def _moderate(
    user: dict, kind: str, table: str, text_col: str, item_id: str, data: ModerateSchema
) -> dict:
    """pending -> approved | rejected | needs_edit, and only from pending.

    Re-moderating a decided item (rejected -> approved, approved -> needs_edit)
    would bypass the lifecycle and re-send the decision email.
    """
    item = maybe_row(
        supabase.table(table).select(f"submitted_by, status, {text_col}").eq("id", item_id)
    )
    if not item:
        raise AppError(404, {"error": f"{kind.capitalize()} not found"})
    if item["status"] != "pending":
        raise AppError(409, {"error": f"Only pending {kind}s can be moderated (this one is {item['status']})"})

    admin_note = clean_text(data.admin_note or "")

    result = (
        supabase.table(table).update({
            "status":      data.status,
            "admin_note":  admin_note or None,
            "reviewed_by": user["sub"],
            "reviewed_at": "now()",
        })
        .eq("id", item_id)
        .eq("status", "pending")   # another admin decided it in the meantime
        .execute()
    )
    if not result.data:
        raise AppError(409, {"error": f"This {kind} was already moderated"})

    # ponytail: update and audit are two calls, not one transaction; an audit
    # failure 500s loudly after the change. Move both into one RPC if that bites.
    _audit(user["sub"], f"{kind}_{data.status}", kind, item_id, {"note": admin_note or None})
    email_service.send_moderation_decision(
        _email_of(item["submitted_by"]), kind, item[text_col], data.status, admin_note
    )
    return {"message": f"{kind.capitalize()} {data.status}"}


def moderate_question(user: dict, question_id: str, data: ModerateSchema) -> dict:
    return _moderate(user, "question", "interview_questions", "question_text", question_id, data)


def moderate_review(user: dict, review_id: str, data: ModerateSchema) -> dict:
    return _moderate(user, "review", "interview_reviews", "review_text", review_id, data)


def moderate_company(
    user: dict, company_id: str, data: CompanyUpdateSchema | None = None
) -> dict:
    before = maybe_row(
        supabase.table("companies").select("status, submitted_by").eq("id", company_id)
    )
    if not before:
        raise AppError(404, {"error": "Company not found"})

    fields = data.model_dump(exclude_none=True) if data else {}
    # An empty body still just approves, keeping the queue's behaviour.
    fields.setdefault("status", "approved")
    if "name" in fields:
        _check_new_name(fields, company_id)

    result = (
        supabase.table("companies").update(fields).eq("id", company_id).execute()
    )
    company = result.data[0]

    action = "company_updated" if len(fields) > 1 else "company_approved"
    _audit(user["sub"], action, "company", company_id, fields)
    if before["status"] == "pending" and company["status"] == "approved":
        email_service.send_company_approved(_email_of(before.get("submitted_by")), company["name"])
    return {"message": "Company updated", "data": company}


def _check_new_name(fields: dict, company_id: str | None = None) -> None:
    """Normalise a renamed company and refuse a slug another company holds
    (the UNIQUE constraint would otherwise surface as a 500)."""
    fields["name"] = clean_text(fields["name"]).strip()
    if not fields["name"] or len(fields["name"]) > 100:
        raise AppError(400, {"errors": {"name": ["must be 1-100 characters"]}})
    fields["slug"] = _slug(fields["name"])
    clash = (
        supabase.table("companies").select("id").eq("slug", fields["slug"]).limit(1).execute().data
    )
    if clash and clash[0]["id"] != company_id:
        raise AppError(409, {"error": "Another company already has that name"})


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
    fields = data.model_dump(exclude_none=True)
    _check_new_name(fields)
    name = fields["name"]

    result = supabase.table("companies").insert({
        **fields,
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

    # Only these tables reference companies.id; applications store a name.
    # ponytail: a question_bank row already on the survivor with the same text
    # makes the move hit question_bank_unique (500); dedupe first if that happens.
    moved = {}
    for table in ("interview_questions", "interview_reviews", "question_bank"):
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


def _require_user(user_id: str) -> dict:
    row = maybe_row(supabase.table("users").select("id, role").eq("id", user_id))
    if not row:
        raise AppError(404, {"error": "User not found"})
    return row


def _require_can_discipline(actor: dict, target: dict) -> None:
    """Plain admins may only act on plain users. Otherwise an admin could ban
    every super admin and leave nobody able to manage roles."""
    if target["role"] != "user" and actor["role"] != "super_admin":
        raise AppError(403, {"error": "Only a super admin can do this to an admin"})


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
    _require_can_discipline(actor, _require_user(user_id))
    _audit(actor["sub"], "user_warned", "user", user_id)
    email_service.send_warn(_email_of(user_id))
    return {"message": "Warning recorded"}


def suspend_user(actor: dict, user_id: str) -> dict:
    if user_id == actor["sub"]:
        raise AppError(400, {"error": "You cannot suspend yourself"})

    _require_can_discipline(actor, _require_user(user_id))
    supabase.auth.admin.update_user_by_id(user_id, {"ban_duration": "876600h"})
    # ponytail: display mirror — auth.users stays the source of truth for login blocking.
    supabase.table("users").update({"suspended_at": "now()"}).eq("id", user_id).execute()
    invalidate_ban_cache(user_id)

    _audit(actor["sub"], "user_suspended", "user", user_id)
    email_service.send_suspend(_email_of(user_id))
    return {"message": "User suspended"}


def unsuspend_user(actor: dict, user_id: str) -> dict:
    _require_can_discipline(actor, _require_user(user_id))
    supabase.auth.admin.update_user_by_id(user_id, {"ban_duration": "none"})
    supabase.table("users").update({"suspended_at": None}).eq("id", user_id).execute()
    invalidate_ban_cache(user_id)

    _audit(actor["sub"], "user_unsuspended", "user", user_id)
    return {"message": "User unsuspended"}


# --- company managers -------------------------------------------------------

def list_managers(company_id: str) -> dict:
    rows = (
        supabase.table("company_admins")
        .select("user_id, created_at, users!company_admins_user_id_fkey(email)")
        .eq("company_id", company_id)
        .execute()
    ).data
    return {"data": rows}


def grant_manager(user: dict, company_id: str, data: CompanyManagerGrantSchema) -> dict:
    if not maybe_row(supabase.table("companies").select("id").eq("id", company_id)):
        raise AppError(404, {"error": "Company not found"})

    # eq, not ilike: "_" is an ilike wildcard, so john_doe@ matched john.doe@.
    # Emails are stored lowercased at registration.
    target = maybe_row(
        supabase.table("users").select("id, email").eq("email", data.email.strip().lower())
    )
    if not target:
        raise AppError(404, {"error": "No user with that email"})

    if maybe_row(
        supabase.table("company_admins")
        .select("user_id")
        .eq("company_id", company_id)
        .eq("user_id", target["id"])
    ):
        raise AppError(409, {"error": "Already a manager of this company"})

    supabase.table("company_admins").insert({
        "company_id": company_id,
        "user_id":    target["id"],
        "granted_by": user["sub"],
    }).execute()

    _audit(user["sub"], "company_manager_granted", "company", company_id,
           {"user_id": target["id"], "email": target["email"]})
    return {"message": f"{target['email']} can now manage this company"}


def revoke_manager(user: dict, company_id: str, user_id: str) -> dict:
    result = (
        supabase.table("company_admins")
        .delete()
        .eq("company_id", company_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        raise AppError(404, {"error": "Not a manager of this company"})

    _audit(user["sub"], "company_manager_revoked", "company", company_id,
           {"user_id": user_id})
    return {"message": "Manager access revoked"}


# --- company profile edit requests ------------------------------------------

def list_company_edits() -> dict:
    rows = (
        supabase.table("company_edit_requests")
        .select("*, companies(name)")
        .eq("status", "pending")
        .order("created_at")
        .execute()
    ).data
    return {"data": rows}


def decide_company_edit(
    user: dict, request_id: str, data: CompanyEditDecisionSchema
) -> dict:
    req = maybe_row(
        supabase.table("company_edit_requests")
        .select("*")
        .eq("id", request_id)
        .eq("status", "pending")
    )
    if not req:
        raise AppError(404, {"error": "Pending edit request not found"})

    if data.status == "approved":
        changes = dict(req["changes"])
        if "name" in changes:
            _check_new_name(changes, req["company_id"])
        supabase.table("companies").update(changes).eq("id", req["company_id"]).execute()

    admin_note = clean_text(data.admin_note or "") or None
    supabase.table("company_edit_requests").update({
        "status":      data.status,
        "admin_note":  admin_note,
        "reviewed_by": user["sub"],
        "reviewed_at": "now()",
    }).eq("id", request_id).execute()

    _audit(user["sub"], f"company_edit_{data.status}", "company", req["company_id"],
           {"request_id": request_id, "changes": req["changes"]})
    company = maybe_row(supabase.table("companies").select("name").eq("id", req["company_id"]))
    email_service.send_company_edit_decision(
        _email_of(req["requested_by"]), company["name"] if company else "your company",
        data.status, admin_note,
    )
    return {"message": f"Edit request {data.status}"}
