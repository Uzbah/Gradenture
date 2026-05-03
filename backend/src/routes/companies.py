from flask import Blueprint
from src.middleware.authenticate import authenticate
from src.middleware.validate import validate
from src.schemas.company_schema import CompanySchema
from src.controllers.companies_controller import list_companies, get_company, submit_company

companies_bp = Blueprint("companies", __name__)

companies_bp.get("/")(list_companies)
companies_bp.get("/<string:company_id>")(get_company)
companies_bp.post("/")(authenticate(validate(CompanySchema)(submit_company)))
