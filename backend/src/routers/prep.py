from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.dependencies.auth import get_current_user
from src.services import prep_service

router = APIRouter(prefix="/prep", tags=["Prep"])


class ToggleSchema(BaseModel):
    topic:     str
    completed: bool


@router.get("/")
def get_prep(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    return prep_service.get_prep(user)


@router.patch("/")
def toggle_topic(
    body: ToggleSchema,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return prep_service.toggle_topic(user, body.topic, body.completed)
