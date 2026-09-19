from typing import Annotated

from fastapi import APIRouter, Path, Query

from backend.app.career.schema.company import (
    CreateCompanyParam,
    GetCompanyDetail,
    RequestCompanyEditParam,
    SubmittedDetail,
)
from backend.app.career.service.company_service import company_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_code import CustomResponseCode
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import CurrentUserDep, DependsJwtAuth
from backend.common.security.permission import CompanyManagerDep

router = APIRouter(prefix='/companies', tags=['Companies'])


@router.get('/', summary='List approved companies')
def get_companies_paginated(
    params: DependsPagination,
    q: Annotated[str | None, Query(description='Substring match on the company name')] = None,
) -> ResponseSchemaModel[PageData[GetCompanyDetail]]:
    page = company_service.get_list(params=params, q=q)
    return response_base.success(data=page)


# Declared before /{pk} so the literal path is not swallowed by the parameter.
@router.get('/managed', summary='List companies the caller may edit')
def get_managed_companies(user: CurrentUserDep) -> ResponseSchemaModel[list[GetCompanyDetail]]:
    companies = company_service.get_managed(user=user)
    return response_base.success(data=companies)


@router.get('/{pk}', summary='Get one company')
def get_company(pk: Annotated[str, Path(description='Company ID')]) -> ResponseSchemaModel[GetCompanyDetail]:
    company = company_service.get(pk=pk)
    return response_base.success(data=company)


@router.post('/', summary='Submit a company to the registry', status_code=201, dependencies=[DependsJwtAuth])
def create_company(obj: CreateCompanyParam) -> ResponseSchemaModel[SubmittedDetail]:
    company = company_service.create(obj=obj)
    return response_base.success(res=CustomResponseCode.HTTP_201, data=company)


@router.post('/{company_id}/edit-request', summary='Propose changes to a company profile', status_code=201)
def request_company_edit(
    user: CompanyManagerDep,
    company_id: Annotated[str, Path(description='Company ID')],
    obj: RequestCompanyEditParam,
) -> ResponseSchemaModel[SubmittedDetail]:
    request = company_service.request_edit(user=user, pk=company_id, obj=obj)
    return response_base.success(res=CustomResponseCode.HTTP_201, data=request)
