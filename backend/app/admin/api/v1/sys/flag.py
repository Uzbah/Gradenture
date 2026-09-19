from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.admin.schema.moderation import FlagDecisionParam, GetFlagDetail
from backend.app.admin.service.flag_service import flag_service
from backend.common.response.response_code import CustomResponse
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.permission import AdminDep, DependsAdmin

router = APIRouter(prefix='/admin', tags=['Admin'])


@router.get('/flags', summary='List open content flags', dependencies=[DependsAdmin])
def get_flags() -> ResponseSchemaModel[list[GetFlagDetail]]:
    flags = flag_service.get_list()
    return response_base.success(data=flags)


@router.patch('/flags/{pk}', summary='Close a flag')
def resolve_flag(
    user: AdminDep,
    pk: Annotated[str, Path(description='Flag ID')],
    obj: FlagDecisionParam,
) -> ResponseModel:
    message = flag_service.resolve(user=user, pk=pk, obj=obj)
    return response_base.success(res=CustomResponse(code=200, msg=message))
