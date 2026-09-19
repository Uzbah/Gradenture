from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.admin.schema.moderation import GetQueueDetail, ModerateParam
from backend.app.admin.service.moderation_service import moderation_service
from backend.common.enums import ContentType
from backend.common.response.response_code import CustomResponse
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.permission import AdminDep, DependsAdmin

router = APIRouter(prefix='/admin', tags=['Admin'])


@router.get('/queue', summary='Everything awaiting moderation', dependencies=[DependsAdmin])
def get_queue() -> ResponseSchemaModel[GetQueueDetail]:
    queue = moderation_service.get_queue()
    return response_base.success(data=queue)


@router.patch('/questions/{pk}', summary='Decide a submitted question')
def moderate_question(
    user: AdminDep,
    pk: Annotated[str, Path(description='Question ID')],
    obj: ModerateParam,
) -> ResponseModel:
    message = moderation_service.moderate(user=user, kind=ContentType.QUESTION, pk=pk, obj=obj)
    return response_base.success(res=CustomResponse(code=200, msg=message))


@router.patch('/reviews/{pk}', summary='Decide a submitted review')
def moderate_review(
    user: AdminDep,
    pk: Annotated[str, Path(description='Review ID')],
    obj: ModerateParam,
) -> ResponseModel:
    message = moderation_service.moderate(user=user, kind=ContentType.REVIEW, pk=pk, obj=obj)
    return response_base.success(res=CustomResponse(code=200, msg=message))
