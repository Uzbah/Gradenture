from typing import Annotated

from fastapi import APIRouter, Path, Query

from backend.app.career.schema.application import (
    CreateApplicationParam,
    GetApplicationDetail,
    UpdateApplicationParam,
)
from backend.app.career.service.application_service import application_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_code import CustomResponseCode
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import CurrentUserDep

router = APIRouter(prefix='/applications', tags=['Applications'])


@router.get('/', summary="List the caller's applications")
def get_applications_paginated(
    user: CurrentUserDep,
    params: DependsPagination,
    status: Annotated[str | None, Query(description='Restrict to one kanban column')] = None,
) -> ResponseSchemaModel[PageData[GetApplicationDetail]]:
    page = application_service.get_list(user=user, params=params, status=status)
    return response_base.success(data=page)


@router.get('/{pk}', summary='Get one application')
def get_application(
    user: CurrentUserDep,
    pk: Annotated[str, Path(description='Application ID')],
) -> ResponseSchemaModel[GetApplicationDetail]:
    application = application_service.get(user=user, pk=pk)
    return response_base.success(data=application)


@router.post('/', summary='Add an application to the tracker', status_code=201)
def create_application(
    user: CurrentUserDep,
    obj: CreateApplicationParam,
) -> ResponseSchemaModel[GetApplicationDetail]:
    application = application_service.create(user=user, obj=obj)
    return response_base.success(res=CustomResponseCode.HTTP_201, data=application)


@router.patch('/{pk}', summary='Change an application')
def update_application(
    user: CurrentUserDep,
    pk: Annotated[str, Path(description='Application ID')],
    obj: UpdateApplicationParam,
) -> ResponseSchemaModel[GetApplicationDetail]:
    application = application_service.update(user=user, pk=pk, obj=obj)
    return response_base.success(data=application)


@router.delete('/{pk}', summary='Remove an application')
def delete_application(
    user: CurrentUserDep,
    pk: Annotated[str, Path(description='Application ID')],
) -> ResponseModel:
    application_service.delete(user=user, pk=pk)
    return response_base.success()
