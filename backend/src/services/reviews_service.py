from src.config.supabase import supabase
from src.dependencies.exceptions import AppError
from src.schemas.question_schema import FlagSchema
from src.schemas.review_schema import ReviewSchema
from src.utils.sanitize import clean_text


def _sanitize(r: dict, is_admin: bool = False) -> dict:
    if not is_admin and r.get("is_anonymous"):
        r.pop("submitted_by", None)
    return r


def list_reviews(
    page: int = 1,
    limit: int = 20,
    company_id: str | None = None,
    domain_id: str | None = None,
) -> dict:
    page = max(1, page)
    limit = min(50, max(1, limit))
    offset = (page - 1) * limit

    query = (
        supabase.table("interview_reviews")
        .select("*", count="exact")
        .eq("status", "approved")
        .order("created_at", desc=True)
    )

    for field, val in (("company_id", company_id), ("domain_id", domain_id)):
        if val:
            query = query.eq(field, val)

    result = query.range(offset, offset + limit - 1).execute()
    return {"data": [_sanitize(r) for r in result.data], "count": result.count}


def get_review(review_id: str) -> dict:
    result = (
        supabase.table("interview_reviews")
        .select("*")
        .eq("id", review_id)
        .eq("status", "approved")
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise AppError(404, {"error": "Review not found"})
    return {"data": _sanitize(result.data)}


def submit_review(user: dict, data: ReviewSchema) -> dict:
    payload = data.model_dump()
    result = supabase.table("interview_reviews").insert({
        **payload,
        "review_text":  clean_text(payload["review_text"]),
        "submitted_by": user["sub"],
        "status":       "pending",
    }).execute()

    return {
        "id":      result.data[0]["id"],
        "status":  "pending",
        "message": "Review submitted for moderation",
    }


def flag_review(user: dict, review_id: str, data: FlagSchema) -> dict:
    supabase.table("content_flags").insert({
        "reported_by":  user["sub"],
        "content_type": "review",
        "content_id":   review_id,
        "reason":       data.reason,
    }).execute()
    return {"message": "Flagged for review"}
