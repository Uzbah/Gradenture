from src.config.supabase import supabase
from src.dependencies.exceptions import AppError
from src.schemas.question_schema import QuestionSchema, FlagSchema
from src.utils.sanitize import clean_text


def _sanitize(q: dict, is_admin: bool = False) -> dict:
    if not is_admin and q.get("is_anonymous"):
        q.pop("submitted_by", None)
    return q


def list_questions(
    page: int = 1,
    limit: int = 20,
    domain_id: str | None = None,
    company_id: str | None = None,
    difficulty: str | None = None,
    question_type: str | None = None,
) -> dict:
    page = max(1, page)
    limit = min(50, max(1, limit))
    offset = (page - 1) * limit

    query = (
        supabase.table("interview_questions")
        .select("*", count="exact")
        .eq("status", "approved")
        .order("created_at", desc=True)
    )

    for field, val in (
        ("domain_id", domain_id),
        ("company_id", company_id),
        ("difficulty", difficulty),
        ("question_type", question_type),
    ):
        if val:
            query = query.eq(field, val)

    result = query.range(offset, offset + limit - 1).execute()
    return {"data": [_sanitize(q) for q in result.data], "count": result.count}


def get_question(question_id: str) -> dict:
    result = (
        supabase.table("interview_questions")
        .select("*")
        .eq("id", question_id)
        .eq("status", "approved")
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise AppError(404, {"error": "Question not found"})
    return {"data": _sanitize(result.data)}


def submit_question(user: dict, data: QuestionSchema) -> dict:
    payload = data.model_dump()
    result = supabase.table("interview_questions").insert({
        **payload,
        "question_text": clean_text(payload["question_text"]),
        "notes":         clean_text(payload["notes"]) if payload.get("notes") else None,
        "submitted_by":  user["sub"],
        "status":        "pending",
    }).execute()

    return {
        "id":      result.data[0]["id"],
        "status":  "pending",
        "message": "Question submitted for review",
    }


def upvote_question(user: dict, question_id: str) -> dict:
    user_id = user["sub"]

    existing = (
        supabase.table("question_upvotes")
        .select("question_id")
        .eq("question_id", question_id)
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )

    if existing.data:
        (
            supabase.table("question_upvotes")
            .delete()
            .eq("question_id", question_id)
            .eq("user_id", user_id)
            .execute()
        )
        supabase.rpc("decrement_upvotes", {"qid": question_id}).execute()
        upvoted = False
    else:
        supabase.table("question_upvotes").insert({
            "question_id": question_id,
            "user_id":     user_id,
        }).execute()
        supabase.rpc("increment_upvotes", {"qid": question_id}).execute()
        upvoted = True

    q = (
        supabase.table("interview_questions")
        .select("upvotes")
        .eq("id", question_id)
        .single()
        .execute()
    )
    return {"upvoted": upvoted, "upvotes": q.data["upvotes"]}


def flag_question(user: dict, question_id: str, data: FlagSchema) -> dict:
    supabase.table("content_flags").insert({
        "reported_by":  user["sub"],
        "content_type": "question",
        "content_id":   question_id,
        "reason":       data.reason,
    }).execute()
    return {"message": "Flagged for review"}
