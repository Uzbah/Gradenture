from typing import Annotated

from fastapi import APIRouter, Path, Query

from backend.app.admin.schema.company_admin import (
    CompanyEditDecisionParam,
    CreateCompanyAdminParam,
    GetCompanyEditDetail,
    GetManagerDetail,
    GrantManagerParam,
    MergeCompanyParam,
    MergeResultDetail,
    UpdateCompanyParam,
)
from backend.app.admin.service.company_admin_service import company_admin_service
from backend.app.career.schema.company import GetCompanyDetail
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_code import CustomResponse, CustomResponseCode
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.permission import AdminDep, DependsAdmin

router = APIRouter(prefix='/admin', tags=['Admin'])


@router.get('/companies', summary='List every company, including pending', dependencies=[DependsAdmin])
def get_admin_companies_paginated(
    params: DependsPagination,
    q: Annotated[str | None, Query(description='Substring match on the company name')] = None,
    status: Annotated[str | None, Query(description='Restrict to one registry status')] = None,
) -> ResponseSchemaModel[PageData[GetCompanyDetail]]:
    page = company_admin_service.get_list(params=params, q=q, status=status)
    return response_base.success(data=page)


@router.post('/companies', summary='Create an approved company', status_code=201)
def create_admin_company(user: AdminDep, obj: CreateCompanyAdminParam) -> ResponseSchemaModel[GetCompanyDetail]:
    company = company_admin_service.create(user=user, obj=obj)
    return response_base.success(res=CustomResponseCode.HTTP_201, data=company)


@router.patch('/companies/{pk}', summary='Edit or approve a company')
def update_company(
    user: AdminDep,
    pk: Annotated[str, Path(description='Company ID')],
    obj: UpdateCompanyParam | None = None,
) -> ResponseSchemaModel[GetCompanyDetail]:
    company = company_admin_service.update(user=user, pk=pk, obj=obj)
    return response_base.success(res=CustomResponse(code=200, msg='Company updated'), data=company)


@router.post('/companies/{pk}/merge', summary='Fold a duplicate company into another')
def merge_company(
    user: AdminDep,
    pk: Annotated[str, Path(description='ID of the duplicate to remove')],
    obj: MergeCompanyParam,
) -> ResponseSchemaModel[MergeResultDetail]:
    result = company_admin_service.merge(user=user, pk=pk, obj=obj)
    message = f'Merged {result["merged_name"]} into {result["into_name"]}'
    return response_base.success(res=CustomResponse(code=200, msg=message), data=result)


@router.get('/companies/{pk}/managers', summary="List a company's managers", dependencies=[DependsAdmin])
def get_company_managers(
    pk: Annotated[str, Path(description='Company ID')],
) -> ResponseSchemaModel[list[GetManagerDetail]]:
    managers = company_admin_service.get_managers(pk=pk)
    return response_base.success(data=managers)


@router.post('/companies/{pk}/managers', summary='Grant management rights', status_code=201)
def grant_company_manager(
    user: AdminDep,
    pk: Annotated[str, Path(description='Company ID')],
    obj: GrantManagerParam,
) -> ResponseModel:
    message = company_admin_service.grant_manager(user=user, pk=pk, obj=obj)
    return response_base.success(res=CustomResponse(code=201, msg=message))


@router.delete('/companies/{pk}/managers/{user_id}', summary='Revoke management rights')
def revoke_company_manager(
    user: AdminDep,
    pk: Annotated[str, Path(description='Company ID')],
    user_id: Annotated[str, Path(description='Manager to remove')],
) -> ResponseModel:
    message = company_admin_service.revoke_manager(user=user, pk=pk, user_id=user_id)
    return response_base.success(res=CustomResponse(code=200, msg=message))


@router.get('/company-edits', summary='List proposed profile edits', dependencies=[DependsAdmin])
def get_company_edits() -> ResponseSchemaModel[list[GetCompanyEditDetail]]:
    edits = company_admin_service.get_edit_requests()
    return response_base.success(data=edits)


@router.patch('/company-edits/{pk}', summary='Decide a proposed profile edit')
def decide_company_edit(
    user: AdminDep,
    pk: Annotated[str, Path(description='Edit request ID')],
    obj: CompanyEditDecisionParam,
) -> ResponseModel:
    message = company_admin_service.decide_edit(user=user, pk=pk, obj=obj)
    return response_base.success(res=CustomResponse(code=200, msg=message))
