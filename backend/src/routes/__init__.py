from flask import Flask
from .auth import auth_bp
from .users import users_bp
from .companies import companies_bp
from .questions import questions_bp
from .reviews import reviews_bp
from .applications import applications_bp
from .admin import admin_bp


def register_routes(app: Flask) -> None:
    app.register_blueprint(auth_bp,          url_prefix="/api/v1/auth")
    app.register_blueprint(users_bp,         url_prefix="/api/v1")
    app.register_blueprint(companies_bp,     url_prefix="/api/v1/companies")
    app.register_blueprint(questions_bp,     url_prefix="/api/v1/questions")
    app.register_blueprint(reviews_bp,       url_prefix="/api/v1/reviews")
    app.register_blueprint(applications_bp,  url_prefix="/api/v1/applications")
    app.register_blueprint(admin_bp,         url_prefix="/api/v1/admin")
