from postgrest.exceptions import APIError

from src.config.supabase import maybe_row, supabase
from src.dependencies.exceptions import AppError
from src.schemas.question_schema import FlagSchema, QuestionEditSchema, QuestionSchema
from src.services import email_service
from src.utils.sanitize import clean_text

# Whitelist, not "*": keeps submitted_by (even on non-anonymous posts),
# reviewed_by (which admin moderated it) and admin_note out of public responses.
# ponytail: no author shown anywhere, so no author field; add a display name
# (re-attributed to "Anonymous" for anonymous/banned authors) when that UI exists.
PUBLIC_COLUMNS = (
    "id, domain_id, company_id, role_title, question_text, question_type, "
    "difficulty, asked_date, notes, upvotes, created_at"
)


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
        .select(PUBLIC_COLUMNS, count="exact")
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
    return {"data": result.data, "count": result.count}


def get_question(question_id: str) -> dict:
    row = maybe_row(
        supabase.table("interview_questions")
        .select(PUBLIC_COLUMNS)
        .eq("id", question_id)
        .eq("status", "approved")
    )
    if not row:
        raise AppError(404, {"error": "Question not found"})
    return {"data": row}


def submit_question(user: dict, data: QuestionSchema) -> dict:
    payload = data.model_dump()
    result = supabase.table("interview_questions").insert({
        **payload,
        "question_text": clean_text(payload["question_text"]),
        "notes":         clean_text(payload["notes"]) if payload.get("notes") else None,
        "submitted_by":  user["sub"],
        "status":        "pending",
    }).execute()

    email_service.send_submission_confirmation(user.get("email"), "question", payload["question_text"])
    return {
        "id":      result.data[0]["id"],
        "status":  "pending",
        "message": "Question submitted for review",
    }


def resubmit_question(user: dict, question_id: str, data: QuestionEditSchema) -> dict:
    """needs_edit -> pending, owner only (moderation lifecycle)."""
    q = maybe_row(
        supabase.table("interview_questions")
        .select("status, question_text")
        .eq("id", question_id)
        .eq("submitted_by", user["sub"])
    )
    if not q:
        raise AppError(404, {"error": "Question not found"})
    if q["status"] != "needs_edit":
        raise AppError(409, {"error": "Only questions with an edit request can be resubmitted"})

    changes = {k: clean_text(v) for k, v in data.model_dump(exclude_none=True).items()}
    if not changes:
        raise AppError(400, {"error": "No changes submitted"})

    result = (
        supabase.table("interview_questions")
        .update({**changes, "status": "pending"})
        .eq("id", question_id)
        .eq("status", "needs_edit")   # guards a double submit
        .execute()
    )
    if not result.data:
        raise AppError(409, {"error": "Only questions with an edit request can be resubmitted"})

    email_service.send_submission_confirmation(
        user.get("email"), "question", changes.get("question_text", q["question_text"])
    )
    return {"id": question_id, "status": "pending", "message": "Question resubmitted for review"}


def upvote_question(user: dict, question_id: str) -> dict:
    # Atomic in Postgres (row lock + recount); NULL when not approved / missing.
    result = supabase.rpc("toggle_upvote", {"qid": question_id, "uid": user["sub"]}).execute()
    if not result.data:
        raise AppError(404, {"error": "Question not found"})
    return {"upvoted": result.data["upvoted"], "upvotes": result.data["upvotes"]}


_FLAGGABLE = {"question": "interview_questions", "review": "interview_reviews"}


def flag_content(user: dict, content_type: str, content_id: str, data: FlagSchema) -> dict:
    """Shared by questions and reviews. Only live (approved) content is flaggable."""
    if not maybe_row(
        supabase.table(_FLAGGABLE[content_type]).select("id")
        .eq("id", content_id).eq("status", "approved")
    ):
        raise AppError(404, {"error": f"{content_type.capitalize()} not found"})

    try:
        supabase.table("content_flags").insert({
            "reported_by":  user["sub"],
            "content_type": content_type,
            "content_id":   content_id,
            "reason":       clean_text(data.reason),
        }).execute()
    except APIError as e:
        if e.code == "23505":   # content_flags_one_open_per_user
            raise AppError(409, {"error": "You have already flagged this"})
        raise
    return {"message": "Flagged for review"}


def flag_question(user: dict, question_id: str, data: FlagSchema) -> dict:
    return flag_content(user, "question", question_id, data)
