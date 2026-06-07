from src.config.supabase import supabase
from src.dependencies.exceptions import AppError
from src.schemas.admin_schema import ModerateSchema, UpdateRoleSchema
from src.services.auth_helpers import invalidate_ban_cache
from src.utils.sanitize import clean_text


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

    return {"data": {"questions": questions, "reviews": reviews}}


def moderate_question(user: dict, question_id: str, data: ModerateSchema) -> dict:
    q = (
        supabase.table("interview_questions")
        .select("submitted_by, status")
        .eq("id", question_id)
        .maybe_single()
        .execute()
    )
    if not q.data:
        raise AppError(404, {"error": "Question not found"})

    admin_note = clean_text(data.admin_note or "")

    supabase.table("interview_questions").update({
        "status":      data.status,
        "admin_note":  admin_note or None,
        "reviewed_by": user["sub"],
        "reviewed_at": "now()",
    }).eq("id", question_id).execute()

    return {"message": f"Question {data.status}"}


def moderate_review(user: dict, review_id: str, data: ModerateSchema) -> dict:
    r = (
        supabase.table("interview_reviews")
        .select("submitted_by")
        .eq("id", review_id)
        .maybe_single()
        .execute()
    )
    if not r.data:
        raise AppError(404, {"error": "Review not found"})

    admin_note = clean_text(data.admin_note or "")

    supabase.table("interview_reviews").update({
        "status":      data.status,
        "admin_note":  admin_note or None,
        "reviewed_by": user["sub"],
        "reviewed_at": "now()",
    }).eq("id", review_id).execute()

    return {"message": f"Review {data.status}"}


def moderate_company(company_id: str) -> dict:
    result = (
        supabase.table("companies")
        .update({"status": "approved"})
        .eq("id", company_id)
        .execute()
    )
    if not result.data:
        raise AppError(404, {"error": "Company not found"})
    return {"message": "Company approved"}


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


def update_user_role(user_id: str, data: UpdateRoleSchema) -> dict:
    supabase.table("users").update({"role": data.role}).eq("id", user_id).execute()
    supabase.auth.admin.update_user_by_id(
        user_id, {"user_metadata": {"role": data.role}}
    )
    return {"message": f"Role updated to {data.role}"}


def warn_user(user_id: str) -> dict:
    user = (
        supabase.table("users")
        .select("id")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    if not user.data:
        raise AppError(404, {"error": "User not found"})
    return {"message": "User warned"}


def suspend_user(user_id: str) -> dict:
    user = (
        supabase.table("users")
        .select("id")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    if not user.data:
        raise AppError(404, {"error": "User not found"})

    supabase.auth.admin.update_user_by_id(user_id, {"ban_duration": "876600h"})
    invalidate_ban_cache(user_id)
    return {"message": "User suspended"}
