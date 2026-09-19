from backend.app.career.crud.crud_application import application_dao
from backend.app.career.schema.application import CreateApplicationParam, UpdateApplicationParam
from backend.common.dataclasses import CurrentUser
from backend.common.exception import errors
from backend.common.pagination import PageData, PageParams, paginate
from backend.utils.sanitize import clean_text


class ApplicationService:
    """A user's private application tracker.

    Every method takes the caller and scopes the query to them: a row that is not
    theirs is a 404, not a 403, so the tracker does not confirm what other people
    have applied to.
    """

    @staticmethod
    def get(*, user: CurrentUser, pk: str) -> dict:
        """One of the caller's applications.

        :param user: the owner
        :param pk: application ID
        """
        application = application_dao.get_own(pk, user.sub)
        if not application:
            raise errors.NotFoundError(msg='Application not found')
        return application

    @staticmethod
    def get_list(*, user: CurrentUser, params: PageParams, status: str | None = None) -> PageData:
        """One page of the caller's applications, newest first.

        :param user: the owner
        :param params: page and size
        :param status: restrict to one kanban column
        """
        return paginate(application_dao.select_for_user(user.sub, status), params)

    @staticmethod
    def create(*, user: CurrentUser, obj: CreateApplicationParam) -> dict:
        """Add an application to the tracker.

        :param user: the owner
        :param obj: the application
        """
        payload = obj.model_dump()
        if payload.get('notes'):
            payload['notes'] = clean_text(payload['notes'])
        return application_dao.create({**payload, 'user_id': user.sub})

    @staticmethod
    def update(*, user: CurrentUser, pk: str, obj: UpdateApplicationParam) -> dict:
        """Change an application. Omitted fields are left alone.

        :param user: the owner
        :param pk: application ID
        :param obj: the changes
        """
        payload = obj.model_dump(exclude_none=True)
        if payload.get('notes'):
            payload['notes'] = clean_text(payload['notes'])

        if not payload:
            return ApplicationService.get(user=user, pk=pk)

        application = application_dao.update_own(pk, user.sub, payload)
        if not application:
            raise errors.NotFoundError(msg='Application not found')
        return application

    @staticmethod
    def delete(*, user: CurrentUser, pk: str) -> None:
        """Remove an application from the tracker.

        :param user: the owner
        :param pk: application ID
        """
        if not application_dao.delete_own(pk, user.sub):
            raise errors.NotFoundError(msg='Application not found')


application_service: ApplicationService = ApplicationService()
