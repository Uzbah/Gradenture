from typing import Annotated

from fastapi import APIRouter, Depends, Request

from src.dependencies.auth import get_current_user
from src.dependencies.rate_limit import limiter, user_rate_key
from src.schemas.question_schema import QuestionSchema, FlagSchema
from src.services import questions_service

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("/")
def list_questions(
    page: int = 1,
    limit: int = 20,
    domain_id: str | None = None,
    company_id: str | None = None,
    difficulty: str | None = None,
    question_type: str | None = None,
) -> dict:
    return questions_service.list_questions(
        page, limit, domain_id, company_id, difficulty, question_type
    )


@router.get("/{question_id}")
def get_question(question_id: str) -> dict:
    return questions_service.get_question(question_id)


@router.post("/", status_code=201)
@limiter.limit("5/hour", key_func=user_rate_key)
def submit_question(
    request: Request,
    body: QuestionSchema,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return questions_service.submit_question(user, body)


@router.post("/{question_id}/upvote")
def upvote_question(
    question_id: str,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return questions_service.upvote_question(user, question_id)


@router.post("/{question_id}/flag", status_code=201)
@limiter.limit("10/hour", key_func=user_rate_key)
def flag_question(
    request: Request,
    question_id: str,
    body: FlagSchema,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return questions_service.flag_question(user, question_id, body)
