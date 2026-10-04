from backend.app.admin.crud.crud_audit import audit_dao
from backend.app.admin.crud.crud_company_admin import company_admin_dao
from backend.app.admin.crud.crud_user import user_dao
from backend.app.admin.schema.company_admin import (
    CompanyEditDecisionParam,
    CreateCompanyAdminParam,
    GrantManagerParam,
    MergeCompanyParam,
    UpdateCompanyParam,
)
from backend.app.career.crud.crud_company import company_dao
from backend.app.career.service.company_service import slugify
from backend.common.dataclasses import CurrentUser
from backend.common.enums import CompanyStatus
from backend.common.exception import errors
from backend.common.pagination import PageData, PageParams, paginate
from backend.common.response.response_code import CustomErrorCode, StandardResponseCode
from backend.utils.sanitize import clean_text


class CompanyAdminService:
    """Administration of the company registry: approval, edits, merges and managers."""

    @staticmethod
    def get_list(*, params: PageParams, q: str | None = None, status: str | None = None) -> PageData:
        """One page of companies, including pending ones.

        :param params: page and size
        :param q: substring match on the name
        :param status: restrict to one registry status
        """
        return paginate(company_admin_dao.select_all(q, status), params)

    @staticmethod
    def create(*, user: CurrentUser, obj: CreateCompanyAdminParam) -> dict:
        """Add a company directly, already approved.

        :param user: the admin
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

        company = company_admin_dao.create(
            {
                **obj.model_dump(exclude_none=True),
                'name': name,
                'slug': slugify(name),
                # Admin-created companies skip the queue.
                'status': CompanyStatus.APPROVED,
            }
        )
        audit_dao.record(user.sub, 'company_created', 'company', company['id'], {'name': name})
        return company

    @staticmethod
    def update(*, user: CurrentUser, pk: str, obj: UpdateCompanyParam | None = None) -> dict:
        """Edit a company, or approve it.

        An empty body approves, which is what the queue's approve button sends.

        :param user: the admin
        :param pk: company ID
        :param obj: the changes, if any
        """
        fields = obj.model_dump(exclude_none=True) if obj else {}
        fields.setdefault('status', CompanyStatus.APPROVED)

        if 'name' in fields:
            fields['name'] = fields['name'].strip()
            fields['slug'] = slugify(fields['name'])

        company = company_admin_dao.update(pk, fields)
        if not company:
            raise errors.NotFoundError(msg='Company not found')

        action = 'company_updated' if len(fields) > 1 else 'company_approved'
        audit_dao.record(user.sub, action, 'company', pk, fields)
        return company

    @staticmethod
    def merge(*, user: CurrentUser, pk: str, obj: MergeCompanyParam) -> dict:
        """Fold a duplicate company into another.

        Repointing the content, deleting the duplicate and recording the merge all
        happen in one transaction.

        :param user: the admin
        :param pk: the duplicate to remove
        :param obj: the company to keep
        """
        if pk == obj.into_id:
            raise errors.RequestError(msg='Cannot merge a company into itself')

        result = company_admin_dao.merge(pk, obj.into_id, user.sub)
        if not result:
            raise errors.NotFoundError(msg='Company not found')
        return result

    # --- managers ---

    @staticmethod
    def get_managers(*, pk: str) -> list[dict]:
        """Who may edit this company's profile.

        :param pk: company ID
        """
        return company_admin_dao.get_managers(pk)

    @staticmethod
    def grant_manager(*, user: CurrentUser, pk: str, obj: GrantManagerParam) -> str:
        """Give a user management rights over a company.

        :param user: the admin
        :param pk: company ID
        :param obj: the user's email
        """
        if not company_dao.exists(pk):
            raise errors.NotFoundError(msg='Company not found')

        target = user_dao.get_by_email(obj.email.strip())
        if not target:
            raise errors.NotFoundError(msg='No user with that email')

        if company_admin_dao.is_manager(pk, target['id']):
            raise errors.ConflictError(msg='Already a manager of this company')

        company_admin_dao.grant_manager(pk, target['id'], user.sub)
        audit_dao.record(
            user.sub,
            'company_manager_granted',
            'company',
            pk,
            {'user_id': target['id'], 'email': target['email']},
        )
        return f'{target["email"]} can now manage this company'

    @staticmethod
    def revoke_manager(*, user: CurrentUser, pk: str, user_id: str) -> str:
        """Take management rights away.

        :param user: the admin
        :param pk: company ID
        :param user_id: the manager to remove
        """
        if not company_admin_dao.revoke_manager(pk, user_id):
            raise errors.NotFoundError(msg='Not a manager of this company')

        audit_dao.record(user.sub, 'company_manager_revoked', 'company', pk, {'user_id': user_id})
        return 'Manager access revoked'

    # --- profile edit requests ---

    @staticmethod
    def get_edit_requests() -> list[dict]:
        """Profile edits proposed by managers and awaiting a decision."""
        return company_admin_dao.get_pending_edits()

    @staticmethod
    def decide_edit(*, user: CurrentUser, pk: str, obj: CompanyEditDecisionParam) -> str:
        """Approve or reject a proposed profile edit.

        Approving applies the changes, closes the request and audits it in one
        transaction, so a company cannot end up changed with the request still open.

        :param user: the admin
        :param pk: request ID
        :param obj: the decision and any note
        """
        admin_note = clean_text(obj.admin_note or '') or None

        if not company_admin_dao.decide_edit(pk, obj.status, admin_note, user.sub):
            raise errors.NotFoundError(msg='Pending edit request not found')

        return f'Edit request {obj.status}'


company_admin_service: CompanyAdminService = CompanyAdminService()
