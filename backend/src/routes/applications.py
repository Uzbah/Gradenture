from flask import Blueprint
from src.middleware.authenticate import authenticate
from src.middleware.validate import validate
from src.schemas.application_schema import ApplicationSchema, ApplicationUpdateSchema
from src.controllers.applications_controller import (
    list_applications, get_application, create_application,
    update_application, delete_application
)

applications_bp = Blueprint("applications", __name__)

applications_bp.get("/")(authenticate(list_applications))
applications_bp.get("/<string:app_id>")(authenticate(get_application))
applications_bp.post("/")(authenticate(validate(ApplicationSchema)(create_application)))
applications_bp.patch("/<string:app_id>")(authenticate(validate(ApplicationUpdateSchema)(update_application)))
applications_bp.delete("/<string:app_id>")(authenticate(delete_application))
