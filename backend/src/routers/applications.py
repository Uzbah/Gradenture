from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.auth import get_current_user
from src.schemas.application_schema import ApplicationSchema, ApplicationUpdateSchema
from src.services import applications_service

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("/")
def list_applications(
    user: Annotated[dict, Depends(get_current_user)],
    page: int = 1,
    limit: int = 20,
    status: str | None = None,
) -> dict:
    return applications_service.list_applications(user, page, limit, status)


@router.get("/{app_id}")
def get_application(
    app_id: str,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return applications_service.get_application(user, app_id)


@router.post("/", status_code=201)
def create_application(
    body: ApplicationSchema,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return applications_service.create_application(user, body)


@router.patch("/{app_id}")
def update_application(
    app_id: str,
    body: ApplicationUpdateSchema,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return applications_service.update_application(user, app_id, body)


@router.delete("/{app_id}")
def delete_application(
    app_id: str,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return applications_service.delete_application(user, app_id)
