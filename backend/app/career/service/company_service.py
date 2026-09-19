import re

from backend.app.career.crud.crud_company import company_dao
from backend.app.career.schema.company import CreateCompanyParam, RequestCompanyEditParam
from backend.common.dataclasses import CurrentUser
from backend.common.enums import CompanyStatus
from backend.common.exception import errors
from backend.common.pagination import PageData, PageParams, paginate
from backend.common.response.response_code import CustomErrorCode, StandardResponseCode


def slugify(name: str) -> str:
    """URL-safe form of a company name.

    Mirrored in SQL as public.company_slug, used by the edit-approval RPC.
    """
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


class CompanyService:
    """The company registry: browsing, user submissions and manager edit requests."""

    @staticmethod
    def get(*, pk: str) -> dict:
        """One approved company.

        :param pk: company ID
        """
        company = company_dao.get_approved(pk)
        if not company:
            raise errors.NotFoundError(msg='Company not found')
        return company

    @staticmethod
    def get_list(*, params: PageParams, q: str | None = None) -> PageData:
        """One page of approved companies.

        :param params: page and size
        :param q: substring match on the name
        """
        return paginate(company_dao.select_approved(q), params)

    @staticmethod
    def get_managed(*, user: CurrentUser) -> list[dict]:
        """Companies the caller may edit the profile of.

        :param user: the caller
        """
        return company_dao.get_managed_by(user.sub)

    @staticmethod
    def create(*, obj: CreateCompanyParam) -> dict:
        """Submit a company to the registry, for an admin to approve.

        :param obj: the company
        """
        name = obj.name.strip()
        if not name:
            raise errors.RequestError(msg='Invalid company', data={'name': ['must not be empty']})

        if company_dao.get_by_name(name):
            raise errors.CustomError(
                error=CustomErrorCode.COMPANY_EXISTS,
                http_code=StandardResponseCode.HTTP_409,
            )

        company = company_dao.create(
            {
                'name': name,
                'slug': slugify(name),
                'website': obj.website,
                'industry': obj.industry,
                'status': CompanyStatus.PENDING,
            }
        )
        return {
            'id': company['id'],
            'status': CompanyStatus.PENDING,
            'message': 'Company submitted for review',
        }

    @staticmethod
    def request_edit(*, user: CurrentUser, pk: str, obj: RequestCompanyEditParam) -> dict:
        """Propose changes to a company's profile, for an admin to approve.

        Nothing a company writes about itself goes live unreviewed, so this queues
        a request rather than writing to the company.

        :param user: the requesting manager
        :param pk: company ID
        :param obj: the proposed changes
        """
        changes = obj.model_dump(exclude_none=True)
        if not changes:
            raise errors.RequestError(msg='No changes submitted')

        if not company_dao.exists(pk):
            raise errors.NotFoundError(msg='Company not found')

        if company_dao.get_pending_edit(pk):
            raise errors.CustomError(
                error=CustomErrorCode.EDIT_ALREADY_PENDING,
                http_code=StandardResponseCode.HTTP_409,
            )

        request = company_dao.create_edit_request(
            {'company_id': pk, 'requested_by': user.sub, 'changes': changes}
        )
        return {
            'id': request['id'],
            'status': 'pending',
            'message': 'Changes submitted for review',
        }


company_service: CompanyService = CompanyService()
