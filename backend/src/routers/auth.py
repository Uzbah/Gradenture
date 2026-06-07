from typing import Annotated

from fastapi import APIRouter, Depends, Request

from src.dependencies.auth import get_current_user
from src.dependencies.rate_limit import limiter
from src.schemas.auth_schema import (
    RegisterSchema,
    LoginSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    ResendVerificationSchema,
)
from src.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201)
@limiter.limit("10/hour")
def register(request: Request, body: RegisterSchema) -> dict:
    return auth_service.register(body)


@router.post("/login")
@limiter.limit("20/hour")
def login(request: Request, body: LoginSchema) -> dict:
    return auth_service.login(body)


@router.post("/logout")
def logout(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    return auth_service.logout(user)


@router.post("/reset-password")
def reset_password(
    body: ResetPasswordSchema,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return auth_service.reset_password(user, body)


@router.post("/forgot-password")
@limiter.limit("5/hour")
def forgot_password(request: Request, body: ForgotPasswordSchema) -> dict:
    return auth_service.forgot_password(body)


@router.post("/resend-verification")
@limiter.limit("5/hour")
def resend_verification(request: Request, body: ResendVerificationSchema) -> dict:
    return auth_service.resend_verification(body)
