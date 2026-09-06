import re

from src.config.supabase import maybe_row, supabase
from src.dependencies.exceptions import AppError
from src.schemas.company_schema import CompanySchema


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def list_companies(page: int = 1, limit: int = 20) -> dict:
    page = max(1, page)
    limit = min(50, max(1, limit))
    offset = (page - 1) * limit

    result = (
        supabase.table("companies")
        .select("*", count="exact")
        .eq("status", "approved")
        .order("name")
        .range(offset, offset + limit - 1)
        .execute()
    )
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
