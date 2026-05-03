from flask import Blueprint, g
from src.middleware.authenticate import authenticate
from src.middleware.validate import validate
from src.schemas.review_schema import ReviewSchema
from src.schemas.question_schema import FlagSchema
from src.controllers.reviews_controller import (
    list_reviews, get_review, submit_review, flag_review
)
from src.config.rate_limiter import limiter

reviews_bp = Blueprint("reviews", __name__)

reviews_bp.get("/")(list_reviews)
reviews_bp.get("/<string:review_id>")(get_review)
reviews_bp.post("/")(
    authenticate(
        limiter.limit("5 per hour", key_func=lambda: g.user["sub"])(
            validate(ReviewSchema)(submit_review)
        )
    )
)
reviews_bp.post("/<string:review_id>/flag")(
    authenticate(
        limiter.limit("10 per hour", key_func=lambda: g.user["sub"])(
            validate(FlagSchema)(flag_review)
        )
    )
)
