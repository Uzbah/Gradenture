import re

from src.config.supabase import maybe_row, supabase
from src.dependencies.exceptions import AppError
from src.schemas.company_schema import CompanyEditRequestSchema, CompanySchema


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def list_companies(page: int = 1, limit: int = 20, q: str | None = None) -> dict:
    page = max(1, page)
    limit = min(50, max(1, limit))
    offset = (page - 1) * limit

    query = (
        supabase.table("companies")
        .select("*", count="exact")
        .eq("status", "approved")
    )
    if q:
        query = query.ilike("name", f"%{q}%")

    result = query.order("name").range(offset, offset + limit - 1).execute()
    return {"data": result.data, "count": result.count}


def get_company(company_id: str) -> dict:
    row = maybe_row(
        supabase.table("companies")
        .select("*")
        .eq("id", company_id)
        .eq("status", "approved")
    )
    if not row:
        raise AppError(404, {"error": "Company not found"})
    return {"data": row}


def submit_company(data: CompanySchema) -> dict:
    name = data.name.strip()
    if not name:
        raise AppError(400, {"errors": {"name": ["must not be empty"]}})

    existing = maybe_row(
        supabase.table("companies").select("id").ilike("name", name)
    )
    if existing:
        raise AppError(409, {"error": "Company already exists"})

    result = supabase.table("companies").insert({
        "name":     name,
        "slug":     _slug(name),
        "website":  data.website,
        "industry": data.industry,
        "status":   "pending",
    }).execute()

    return {
        "id":      result.data[0]["id"],
        "status":  "pending",
        "message": "Company submitted for review",
    }


def list_managed(user: dict) -> dict:
    """Companies this user has been granted management rights over."""
    rows = (
        supabase.table("company_admins")
        .select("companies(*)")
        .eq("user_id", user["sub"])
        .execute()
    ).data
    return {"data": [r["companies"] for r in rows if r.get("companies")]}


def request_edit(user: dict, company_id: str, data: CompanyEditRequestSchema) -> dict:
    changes = data.model_dump(exclude_none=True)
    if not changes:
        raise AppError(400, {"error": "No changes submitted"})

    if not maybe_row(supabase.table("companies").select("id").eq("id", company_id)):
        raise AppError(404, {"error": "Company not found"})

    existing = maybe_row(
        supabase.table("company_edit_requests")
        .select("id")
        .eq("company_id", company_id)
        .eq("status", "pending")
    )
    if existing:
        raise AppError(409, {"error": "An edit for this company is already pending review"})

    result = supabase.table("company_edit_requests").insert({
        "company_id":   company_id,
        "requested_by": user["sub"],
        "changes":      changes,
    }).execute()

    return {
        "id":      result.data[0]["id"],
        "status":  "pending",
        "message": "Changes submitted for review",
    }
