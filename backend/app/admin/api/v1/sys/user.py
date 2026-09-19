from fastapi import APIRouter

from backend.app.admin.schema.user import GetDomainDetail, GetUserDetail, OnboardingDetail, OnboardingParam
from backend.app.admin.service.user_service import user_service
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import CurrentUserDep

router = APIRouter()


@router.get('/users/me', summary="Get the caller's profile", tags=['Users'])
def get_me(user: CurrentUserDep) -> ResponseSchemaModel[GetUserDetail]:
    profile = user_service.get_me(user=user)
    return response_base.success(data=profile)


@router.patch('/users/onboarding', summary='Finish onboarding', tags=['Users'])
def complete_onboarding(user: CurrentUserDep, obj: OnboardingParam) -> ResponseSchemaModel[OnboardingDetail]:
    result = user_service.complete_onboarding(user=user, obj=obj)
    return response_base.success(data=result)


@router.get('/domains', summary='List career domains', tags=['Domains'])
def get_domains() -> ResponseSchemaModel[list[GetDomainDetail]]:
    domains = user_service.get_domains()
    return response_base.success(data=domains)
