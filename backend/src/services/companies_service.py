import re

from src.config.supabase import supabase
from src.dependencies.exceptions import AppError
from src.schemas.company_schema import CompanySchema


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
    result = (
        supabase.table("companies")
        .select("*")
        .eq("id", company_id)
        .eq("status", "approved")
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise AppError(404, {"error": "Company not found"})
    return {"data": result.data}


def submit_company(data: CompanySchema) -> dict:
    name = data.name.strip()
    if not name:
        raise AppError(400, {"errors": {"name": ["must not be empty"]}})

    existing = (
        supabase.table("companies")
        .select("id")
        .ilike("name", name)
        .maybe_single()
        .execute()
    )
    if existing.data:
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
