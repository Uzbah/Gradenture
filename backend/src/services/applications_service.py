from src.config.supabase import supabase
from src.dependencies.exceptions import AppError
from src.schemas.application_schema import ApplicationSchema, ApplicationUpdateSchema
from src.utils.sanitize import clean_text


def _own_or_404(app_id: str, user_id: str) -> dict | None:
    result = (
        supabase.table("applications")
        .select("*")
        .eq("id", app_id)
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    return result.data


def list_applications(
    user: dict,
    page: int = 1,
    limit: int = 20,
    status: str | None = None,
) -> dict:
    user_id = user["sub"]
    page = max(1, page)
    limit = min(50, max(1, limit))
    offset = (page - 1) * limit

    query = (
        supabase.table("applications")
        .select("*", count="exact")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
    )

    if status:
        query = query.eq("status", status)

    result = query.range(offset, offset + limit - 1).execute()
    return {"data": result.data, "count": result.count}


def get_application(user: dict, app_id: str) -> dict:
    app = _own_or_404(app_id, user["sub"])
    if not app:
        raise AppError(404, {"error": "Application not found"})
    return {"data": app}


def create_application(user: dict, data: ApplicationSchema) -> dict:
    payload = data.model_dump()
    if payload.get("notes"):
        payload["notes"] = clean_text(payload["notes"])

    result = supabase.table("applications").insert({
        **payload,
        "user_id": user["sub"],
    }).execute()

    return {"data": result.data[0]}


def update_application(user: dict, app_id: str, data: ApplicationUpdateSchema) -> dict:
    if not _own_or_404(app_id, user["sub"]):
        raise AppError(404, {"error": "Application not found"})

    payload = {k: v for k, v in data.model_dump().items() if v is not None}
    if "notes" in payload:
        payload["notes"] = clean_text(payload["notes"])

    result = (
        supabase.table("applications")
        .update(payload)
        .eq("id", app_id)
        .execute()
    )
    return {"data": result.data[0]}


def delete_application(user: dict, app_id: str) -> dict:
    if not _own_or_404(app_id, user["sub"]):
        raise AppError(404, {"error": "Application not found"})

    supabase.table("applications").delete().eq("id", app_id).execute()
    return {"message": "Application deleted"}
