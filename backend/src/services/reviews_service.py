from src.config.supabase import maybe_row, supabase
from src.dependencies.exceptions import AppError
from src.schemas.question_schema import FlagSchema
from src.schemas.review_schema import ReviewEditSchema, ReviewSchema
from src.services import email_service
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
    row = maybe_row(
        supabase.table("interview_reviews")
        .select("*")
        .eq("id", review_id)
        .eq("status", "approved")
    )
    if not row:
        raise AppError(404, {"error": "Review not found"})
    return {"data": _sanitize(row)}


def submit_review(user: dict, data: ReviewSchema) -> dict:
    payload = data.model_dump()
    result = supabase.table("interview_reviews").insert({
        **payload,
        "review_text":  clean_text(payload["review_text"]),
        "submitted_by": user["sub"],
        "status":       "pending",
    }).execute()

    email_service.send_submission_confirmation(user.get("email"), "review", payload["review_text"])
    return {
        "id":      result.data[0]["id"],
        "status":  "pending",
        "message": "Review submitted for moderation",
    }


def resubmit_review(user: dict, review_id: str, data: ReviewEditSchema) -> dict:
    """needs_edit -> pending, owner only (moderation lifecycle)."""
    r = maybe_row(
        supabase.table("interview_reviews")
        .select("status")
        .eq("id", review_id)
        .eq("submitted_by", user["sub"])
    )
    if not r:
        raise AppError(404, {"error": "Review not found"})
    if r["status"] != "needs_edit":
        raise AppError(409, {"error": "Only reviews with an edit request can be resubmitted"})

    review_text = clean_text(data.review_text)
    result = (
        supabase.table("interview_reviews")
        .update({"review_text": review_text, "status": "pending"})
        .eq("id", review_id)
        .eq("status", "needs_edit")   # guards a double submit
        .execute()
    )
    if not result.data:
        raise AppError(409, {"error": "Only reviews with an edit request can be resubmitted"})

    email_service.send_submission_confirmation(user.get("email"), "review", review_text)
    return {"id": review_id, "status": "pending", "message": "Review resubmitted for moderation"}


def flag_review(user: dict, review_id: str, data: FlagSchema) -> dict:
    supabase.table("content_flags").insert({
        "reported_by":  user["sub"],
        "content_type": "review",
        "content_id":   review_id,
        "reason":       data.reason,
    }).execute()
    return {"message": "Flagged for review"}
