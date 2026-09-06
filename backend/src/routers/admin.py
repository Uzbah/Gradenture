from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.auth import require_admin, require_super_admin
from src.schemas.admin_schema import FlagActionSchema, ModerateSchema, UpdateRoleSchema
from src.services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/queue")
def get_queue(_user: Annotated[dict, Depends(require_admin)]) -> dict:
    return admin_service.get_queue()


@router.patch("/questions/{question_id}")
def moderate_question(
    question_id: str,
    body: ModerateSchema,
    user: Annotated[dict, Depends(require_admin)],
) -> dict:
    return admin_service.moderate_question(user, question_id, body)


@router.patch("/reviews/{review_id}")
def moderate_review(
    review_id: str,
    body: ModerateSchema,
    user: Annotated[dict, Depends(require_admin)],
) -> dict:
    return admin_service.moderate_review(user, review_id, body)


@router.patch("/companies/{company_id}")
def moderate_company(
    company_id: str,
    user: Annotated[dict, Depends(require_admin)],
) -> dict:
    return admin_service.moderate_company(user, company_id)


@router.get("/flags")
def list_flags(_user: Annotated[dict, Depends(require_admin)]) -> dict:
    return admin_service.list_flags()


@router.patch("/flags/{flag_id}")
def resolve_flag(
    flag_id: str,
    body: FlagActionSchema,
    user: Annotated[dict, Depends(require_admin)],
) -> dict:
    return admin_service.resolve_flag(user, flag_id, body)


@router.get("/users")
def list_users(
    _user: Annotated[dict, Depends(require_admin)],
    page: int = 1,
    limit: int = 20,
) -> dict:
    return admin_service.list_users(page, limit)


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: str,
    body: UpdateRoleSchema,
    user: Annotated[dict, Depends(require_super_admin)],
) -> dict:
    return admin_service.update_user_role(user, user_id, body)


@router.patch("/users/{user_id}/warn")
def warn_user(
    user_id: str,
    user: Annotated[dict, Depends(require_admin)],
) -> dict:
    return admin_service.warn_user(user, user_id)


@router.patch("/users/{user_id}/suspend")
def suspend_user(
    user_id: str,
    user: Annotated[dict, Depends(require_admin)],
) -> dict:
    return admin_service.suspend_user(user, user_id)


@router.patch("/users/{user_id}/unsuspend")
def unsuspend_user(
    user_id: str,
    user: Annotated[dict, Depends(require_admin)],
) -> dict:
    return admin_service.unsuspend_user(user, user_id)
