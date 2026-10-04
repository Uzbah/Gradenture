from backend.app.admin.crud.crud_flag import flag_dao
from backend.app.admin.schema.moderation import FlagDecisionParam
from backend.common.dataclasses import CurrentUser
from backend.common.exception import errors


class FlagService:
    """Content reported by readers."""

    @staticmethod
    def get_list() -> list[dict]:
        """Open flags, oldest first, each with the content it points at."""
        flags = flag_dao.get_open()

        # ponytail: one lookup per flag — open flags are few. Batch per
        # content_type if the queue grows.
        for flag in flags:
            flag['content'] = flag_dao.get_flagged_content(flag['content_type'], flag['content_id'])

        return flags

    @staticmethod
    def resolve(*, user: CurrentUser, pk: str, obj: FlagDecisionParam) -> str:
        """Close a flag as resolved or dismissed.

        Only an open flag can be closed, so a double submission is a 404 rather
        than a second audit row.

        :param user: the moderator
        :param pk: flag ID
        :param obj: the decision
        """
        if not flag_dao.resolve(pk, obj.status, user.sub):
            raise errors.NotFoundError(msg='Open flag not found')
        return f'Flag {obj.status}'


flag_service: FlagService = FlagService()
