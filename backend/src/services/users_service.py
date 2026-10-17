from src.config.supabase import maybe_row, supabase
from src.dependencies.exceptions import AppError
from src.schemas.user import OnboardingSchema
from src.utils.sanitize import clean_text


def get_me(user: dict) -> dict:
    user_id = user["sub"]
    row = maybe_row(supabase.table("users").select("*").eq("id", user_id))
    if not row:
        raise AppError(404, {"error": "User not found"})
    return {"data": row}


def get_my_submissions(user: dict) -> dict:
    """The caller's own questions and reviews in every moderation state."""
    # ponytail: newest 50 of each; paginate when a contributor outgrows that
    questions = (
        supabase.table("interview_questions")
        .select("id, domain_id, company_id, role_title, question_text, notes, "
                "question_type, difficulty, status, admin_note, created_at, updated_at")
        .eq("submitted_by", user["sub"])
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    ).data
    reviews = (
        supabase.table("interview_reviews")
        .select("id, domain_id, company_id, role_title, review_text, outcome, "
                "status, admin_note, created_at, updated_at")
        .eq("submitted_by", user["sub"])
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    ).data
    return {"data": {"questions": questions, "reviews": reviews}}


def get_domains() -> dict:
    result = (
        supabase.table("domains")
        .select("id, name, slug")
        .order("name")
        .execute()
    )
    return {"data": result.data, "count": len(result.data)}


def complete_onboarding(user: dict, data: OnboardingSchema) -> dict:
    # bleach escaped "&" to "&amp;" here, so "Texas A&M" was stored mangled.
    clean_university = clean_text(data.university)

    supabase.table("users").upsert({
        "id":                  user["sub"],
        "email":               user["email"],
        "domain_id":           str(data.domain_id),
        "skill_level":         data.skill_level,
        "goal":                data.goal,
        "university":          clean_university,
        "onboarding_complete": True,
    }).execute()

    return {"message": "Onboarding complete", "onboarding_complete": True}
