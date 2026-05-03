from flask import Blueprint
from src.middleware.authenticate import authenticate
from src.controllers.auth_controller import register, login, logout, reset_password

auth_bp = Blueprint("auth", __name__)

auth_bp.post("/register")(register)
auth_bp.post("/login")(login)
auth_bp.post("/logout")(authenticate(logout))
auth_bp.post("/reset-password")(authenticate(reset_password))
