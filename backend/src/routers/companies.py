from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.auth import get_current_user, require_company_manager
from src.schemas.company_schema import CompanyEditRequestSchema, CompanySchema
from src.services import companies_service

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("/")
def list_companies(page: int = 1, limit: int = 20, q: str | None = None) -> dict:
    return companies_service.list_companies(page, limit, q)


@router.get("/managed")
def list_managed(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    return companies_service.list_managed(user)


@router.get("/{company_id}")
def get_company(company_id: str) -> dict:
    return companies_service.get_company(company_id)


@router.post("/", status_code=201)
def submit_company(
    body: CompanySchema,
    _user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return companies_service.submit_company(body)


@router.post("/{company_id}/edit-request", status_code=201)
def request_edit(
    company_id: str,
    body: CompanyEditRequestSchema,
    user: Annotated[dict, Depends(require_company_manager)],
) -> dict:
    return companies_service.request_edit(user, company_id, body)
