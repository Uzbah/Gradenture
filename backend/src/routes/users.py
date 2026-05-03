from flask import Blueprint
from src.middleware.authenticate import authenticate
from src.controllers.users import get_me, get_domains, complete_onboarding

users_bp = Blueprint("users", __name__)

users_bp.get("/users/me")(authenticate(get_me))
users_bp.get("/domains")(get_domains)
users_bp.patch("/users/onboarding")(authenticate(complete_onboarding))
