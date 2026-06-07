import bleach

from src.config.supabase import supabase
from src.dependencies.exceptions import AppError
from src.schemas.user import OnboardingSchema


def get_me(user: dict) -> dict:
    user_id = user["sub"]
    result = (
        supabase.table("users")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise AppError(404, {"error": "User not found"})
    return {"data": result.data}


def get_domains() -> dict:
    result = (
        supabase.table("domains")
        .select("id, name, slug")
        .order("name")
        .execute()
    )
    return {"data": result.data, "count": len(result.data)}


def complete_onboarding(user: dict, data: OnboardingSchema) -> dict:
    clean_university = bleach.clean(data.university, tags=[], strip=True)

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
