from fastapi import APIRouter, Request

from backend.app.admin.schema.auth import (
    ForgotPasswordParam,
    LoginDetail,
    LoginParam,
    RegisterDetail,
    RegisterParam,
    ResendVerificationParam,
    ResetPasswordParam,
)
from backend.app.admin.service.auth_service import auth_service
from backend.common.response.response_code import CustomResponse, CustomResponseCode
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import CurrentUserDep
from backend.utils.limiter import limiter

router = APIRouter()


@router.post('/register', summary='Register an account', status_code=201)
@limiter.limit('10/hour')
def register(request: Request, obj: RegisterParam) -> ResponseSchemaModel[RegisterDetail]:
    # `request` is unused here but required: slowapi reads the limit key off it.
    user = auth_service.create(obj=obj)
    return response_base.success(res=CustomResponseCode.HTTP_201, data=user)


@router.post('/login', summary='Sign in')
@limiter.limit('20/hour')
def login(request: Request, obj: LoginParam) -> ResponseSchemaModel[LoginDetail]:
    session = auth_service.login(obj=obj)
    return response_base.success(data=session)


@router.post('/logout', summary='Sign out')
def logout(user: CurrentUserDep) -> ResponseModel:
    auth_service.logout(user=user)
    return response_base.success(res=CustomResponse(code=200, msg='Logged out successfully'))


@router.post('/reset-password', summary='Set a new password')
def reset_password(user: CurrentUserDep, obj: ResetPasswordParam) -> ResponseModel:
    auth_service.reset_password(user=user, obj=obj)
    return response_base.success(res=CustomResponse(code=200, msg='Password reset successful'))


@router.post('/forgot-password', summary='Request a password reset link')
@limiter.limit('5/hour')
def forgot_password(request: Request, obj: ForgotPasswordParam) -> ResponseModel:
    message = auth_service.forgot_password(obj=obj)
    return response_base.success(res=CustomResponse(code=200, msg=message))


@router.post('/resend-verification', summary='Request another verification email')
@limiter.limit('5/hour')
def resend_verification(request: Request, obj: ResendVerificationParam) -> ResponseModel:
    message = auth_service.resend_verification(obj=obj)
    return response_base.success(res=CustomResponse(code=200, msg=message))
