from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.auth import get_current_user
from src.schemas.user import OnboardingSchema
from src.services import users_service

router = APIRouter(tags=["Users"])


@router.get("/users/me")
def get_me(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    return users_service.get_me(user)


@router.get("/domains", tags=["Domains"])
def get_domains() -> dict:
    return users_service.get_domains()


@router.patch("/users/onboarding")
def complete_onboarding(
    body: OnboardingSchema,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return users_service.complete_onboarding(user, body)
