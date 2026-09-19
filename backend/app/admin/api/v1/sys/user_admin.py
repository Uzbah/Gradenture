from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.admin.schema.user import GetUserDetail, UpdateRoleParam
from backend.app.admin.service.user_admin_service import user_admin_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_code import CustomResponse
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.permission import AdminDep, DependsAdmin, SuperAdminDep

router = APIRouter(prefix='/admin', tags=['Admin'])


@router.get('/users', summary='List users', dependencies=[DependsAdmin])
def get_users_paginated(params: DependsPagination) -> ResponseSchemaModel[PageData[GetUserDetail]]:
    page = user_admin_service.get_list(params=params)
    return response_base.success(data=page)


@router.patch('/users/{pk}/role', summary='Change a user\'s role')
def update_user_role(
    user: SuperAdminDep,
    pk: Annotated[str, Path(description='User ID')],
    obj: UpdateRoleParam,
) -> ResponseModel:
    message = user_admin_service.update_role(user=user, user_id=pk, obj=obj)
    return response_base.success(res=CustomResponse(code=200, msg=message))


@router.patch('/users/{pk}/warn', summary='Record a warning')
def warn_user(user: AdminDep, pk: Annotated[str, Path(description='User ID')]) -> ResponseModel:
    message = user_admin_service.warn(user=user, user_id=pk)
    return response_base.success(res=CustomResponse(code=200, msg=message))


@router.patch('/users/{pk}/suspend', summary='Suspend an account')
def suspend_user(user: AdminDep, pk: Annotated[str, Path(description='User ID')]) -> ResponseModel:
    message = user_admin_service.suspend(user=user, user_id=pk)
    return response_base.success(res=CustomResponse(code=200, msg=message))


@router.patch('/users/{pk}/unsuspend', summary='Lift a suspension')
def unsuspend_user(user: AdminDep, pk: Annotated[str, Path(description='User ID')]) -> ResponseModel:
    message = user_admin_service.unsuspend(user=user, user_id=pk)
    return response_base.success(res=CustomResponse(code=200, msg=message))
