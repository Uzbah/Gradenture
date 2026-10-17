from typing import Annotated

from fastapi import APIRouter, Depends, Request

from src.dependencies.auth import get_current_user
from src.dependencies.rate_limit import limiter, user_rate_key
from src.schemas.question_schema import FlagSchema
from src.schemas.review_schema import ReviewEditSchema, ReviewSchema
from src.schemas.common import UUIDStr
from src.services import reviews_service

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/")
def list_reviews(
    page: int = 1,
    limit: int = 20,
    company_id: UUIDStr | None = None,
    domain_id: UUIDStr | None = None,
) -> dict:
    return reviews_service.list_reviews(page, limit, company_id, domain_id)


@router.get("/{review_id}")
def get_review(review_id: UUIDStr) -> dict:
    return reviews_service.get_review(review_id)


@router.post("/", status_code=201)
@limiter.limit("5/hour", key_func=user_rate_key)
def submit_review(
    request: Request,
    body: ReviewSchema,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return reviews_service.submit_review(user, body)


@router.patch("/{review_id}")
@limiter.limit("10/hour", key_func=user_rate_key)
def resubmit_review(
    request: Request,
    review_id: UUIDStr,
    body: ReviewEditSchema,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return reviews_service.resubmit_review(user, review_id, body)


@router.post("/{review_id}/flag", status_code=201)
@limiter.limit("10/hour", key_func=user_rate_key)
def flag_review(
    request: Request,
    review_id: UUIDStr,
    body: FlagSchema,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    return reviews_service.flag_review(user, review_id, body)
