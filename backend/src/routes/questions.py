from flask import Blueprint
from src.middleware.authenticate import authenticate
from src.middleware.validate import validate
from src.schemas.question_schema import QuestionSchema, FlagSchema
from src.controllers.questions_controller import (
    list_questions, get_question, submit_question, upvote_question, flag_question
)
from src.config.rate_limiter import limiter
from flask import g

questions_bp = Blueprint("questions", __name__)

questions_bp.get("/")(list_questions)
questions_bp.get("/<string:question_id>")(get_question)
questions_bp.post("/")(
    authenticate(
        limiter.limit("5 per hour", key_func=lambda: g.user["sub"])(
            validate(QuestionSchema)(submit_question)
        )
    )
)
questions_bp.post("/<string:question_id>/upvote")(authenticate(upvote_question))
questions_bp.post("/<string:question_id>/flag")(
    authenticate(
        limiter.limit("10 per hour", key_func=lambda: g.user["sub"])(
            validate(FlagSchema)(flag_question)
        )
    )
)
