from typing import Annotated

from fastapi import APIRouter, Path, Query, Request

from backend.app.career.schema.flag import CreateFlagParam
from backend.app.career.schema.review import CreateReviewDetail, CreateReviewParam, GetReviewDetail
from backend.app.career.service.review_service import review_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_code import CustomResponseCode
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import CurrentUserDep
from backend.core.conf import settings
from backend.utils.limiter import limiter, user_rate_key

router = APIRouter(prefix='/reviews', tags=['Reviews'])


@router.get('/', summary='List approved reviews')
def get_reviews_paginated(
    params: DependsPagination,
    company_id: Annotated[str | None, Query(description='Restrict to one company')] = None,
    domain_id: Annotated[str | None, Query(description='Restrict to one domain')] = None,
) -> ResponseSchemaModel[PageData[GetReviewDetail]]:
    page = review_service.get_list(params=params, company_id=company_id, domain_id=domain_id)
    return response_base.success(data=page)


@router.get('/{pk}', summary='Get one review')
def get_review(pk: Annotated[str, Path(description='Review ID')]) -> ResponseSchemaModel[GetReviewDetail]:
    review = review_service.get(pk=pk)
    return response_base.success(data=review)


@router.post('/', summary='Submit a review for moderation', status_code=201)
@limiter.limit(settings.RATE_LIMIT_SUBMISSION, key_func=user_rate_key)
def create_review(
    request: Request,
    user: CurrentUserDep,
    obj: CreateReviewParam,
) -> ResponseSchemaModel[CreateReviewDetail]:
    review = review_service.create(user=user, obj=obj)
    return response_base.success(res=CustomResponseCode.HTTP_201, data=review)


@router.post('/{pk}/flag', summary='Report a review to the moderators', status_code=201)
@limiter.limit(settings.RATE_LIMIT_FLAG, key_func=user_rate_key)
def flag_review(
    request: Request,
    user: CurrentUserDep,
    pk: Annotated[str, Path(description='Review ID')],
    obj: CreateFlagParam,
) -> ResponseModel:
    review_service.flag(user=user, pk=pk, obj=obj)
    return response_base.success(res=CustomResponseCode.HTTP_201)
