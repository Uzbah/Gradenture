from fastapi import APIRouter

from backend.app.career.schema.prep import GetPrepDetail, ToggleTopicParam
from backend.app.career.service.prep_service import prep_service
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import CurrentUserDep

router = APIRouter(prefix='/prep', tags=['Prep'])


@router.get('/', summary="Get the caller's roadmap and preparedness score")
def get_prep(user: CurrentUserDep) -> ResponseSchemaModel[GetPrepDetail]:
    prep = prep_service.get(user=user)
    return response_base.success(data=prep)


@router.patch('/', summary='Mark a roadmap topic done or not done')
def toggle_prep_topic(user: CurrentUserDep, obj: ToggleTopicParam) -> ResponseSchemaModel[GetPrepDetail]:
    prep = prep_service.toggle_topic(user=user, topic=obj.topic, completed=obj.completed)
    return response_base.success(data=prep)
