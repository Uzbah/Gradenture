from flask import Blueprint
from src.middleware.authenticate import authenticate
from src.middleware.require_admin import require_admin, require_super_admin
from src.controllers.admin_controller import (
    get_queue, moderate_question, moderate_review, moderate_company,
    list_users, update_user_role, warn_user, suspend_user
)

admin_bp = Blueprint("admin", __name__)

admin_bp.get("/queue")(authenticate(require_admin(get_queue)))
admin_bp.patch("/questions/<string:question_id>")(authenticate(require_admin(moderate_question)))
admin_bp.patch("/reviews/<string:review_id>")(authenticate(require_admin(moderate_review)))
admin_bp.patch("/companies/<string:company_id>")(authenticate(require_admin(moderate_company)))
admin_bp.get("/users")(authenticate(require_admin(list_users)))
admin_bp.patch("/users/<string:user_id>/role")(authenticate(require_super_admin(update_user_role)))
admin_bp.patch("/users/<string:user_id>/warn")(authenticate(require_admin(warn_user)))
admin_bp.patch("/users/<string:user_id>/suspend")(authenticate(require_admin(suspend_user)))
