from typing import Annotated

from fastapi import APIRouter, Path, Query, Request

from backend.app.career.schema.flag import CreateFlagParam
from backend.app.career.schema.question import (
    CreateQuestionDetail,
    CreateQuestionParam,
    GetQuestionDetail,
    QuestionUpvoteDetail,
)
from backend.app.career.service.question_service import question_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_code import CustomResponseCode
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import CurrentUserDep
from backend.core.conf import settings
from backend.utils.limiter import limiter, user_rate_key

router = APIRouter(prefix='/questions', tags=['Questions'])


@router.get('/', summary='List approved questions')
def get_questions_paginated(
    params: DependsPagination,
    domain_id: Annotated[str | None, Query(description='Restrict to one domain')] = None,
    company_id: Annotated[str | None, Query(description='Restrict to one company')] = None,
    difficulty: Annotated[str | None, Query(description='Restrict to one difficulty')] = None,
    question_type: Annotated[str | None, Query(description='Restrict to one question type')] = None,
) -> ResponseSchemaModel[PageData[GetQuestionDetail]]:
    page = question_service.get_list(
        params=params,
        domain_id=domain_id,
        company_id=company_id,
        difficulty=difficulty,
        question_type=question_type,
    )
    return response_base.success(data=page)


@router.get('/{pk}', summary='Get one question')
def get_question(
    pk: Annotated[str, Path(description='Question ID')],
) -> ResponseSchemaModel[GetQuestionDetail]:
    question = question_service.get(pk=pk)
    return response_base.success(data=question)


@router.post('/', summary='Submit a question for moderation', status_code=201)
@limiter.limit(settings.RATE_LIMIT_SUBMISSION, key_func=user_rate_key)
def create_question(
    request: Request,
    user: CurrentUserDep,
    obj: CreateQuestionParam,
) -> ResponseSchemaModel[CreateQuestionDetail]:
    # `request` is unused here but required: slowapi reads the limit key off it.
    question = question_service.create(user=user, obj=obj)
    return response_base.success(res=CustomResponseCode.HTTP_201, data=question)


@router.post('/{pk}/upvote', summary='Toggle an upvote')
def upvote_question(
    user: CurrentUserDep,
    pk: Annotated[str, Path(description='Question ID')],
) -> ResponseSchemaModel[QuestionUpvoteDetail]:
    result = question_service.toggle_upvote(user=user, pk=pk)
    return response_base.success(data=result)


@router.post('/{pk}/flag', summary='Report a question to the moderators', status_code=201)
@limiter.limit(settings.RATE_LIMIT_FLAG, key_func=user_rate_key)
def flag_question(
    request: Request,
    user: CurrentUserDep,
    pk: Annotated[str, Path(description='Question ID')],
    obj: CreateFlagParam,
) -> ResponseModel:
    question_service.flag(user=user, pk=pk, obj=obj)
    return response_base.success(res=CustomResponseCode.HTTP_201)
