from backend.app.admin.crud.crud_moderation import moderation_dao
from backend.app.admin.schema.moderation import ModerateParam
from backend.common.dataclasses import CurrentUser
from backend.common.enums import ContentType
from backend.common.exception import errors
from backend.utils.sanitize import clean_text


class ModerationService:
    """The moderation queue and the decisions taken on it."""

    @staticmethod
    def get_queue() -> dict:
        """Everything awaiting a moderator: questions, reviews and companies."""
        return moderation_dao.get_queue()

    @staticmethod
    def moderate(*, user: CurrentUser, kind: ContentType, pk: str, obj: ModerateParam) -> str:
        """Approve, reject or return a submission for edits.

        The decision and its audit record are written together, so there is no
        moderated content without a record of who decided it.

        :param user: the moderator
        :param kind: question or review
        :param pk: content ID
        :param obj: the decision and any note
        """
        admin_note = clean_text(obj.admin_note or '') or None

        if not moderation_dao.moderate(kind, pk, obj.status, admin_note, user.sub):
            raise errors.NotFoundError(msg=f'{kind.capitalize()} not found')

        return f'{kind.capitalize()} {obj.status}'


moderation_service: ModerationService = ModerationService()
