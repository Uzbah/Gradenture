from backend.app.admin.crud.crud_audit import audit_dao
from backend.app.admin.crud.crud_user import user_dao
from backend.app.admin.schema.user import UpdateRoleParam
from backend.common.dataclasses import CurrentUser
from backend.common.enums import UserRole
from backend.common.exception import errors
from backend.common.log import log
from backend.common.pagination import PageData, PageParams, paginate
from backend.common.security.jwt import invalidate_ban_cache

# Supabase expresses a permanent ban as a very long duration; 'none' lifts it.
PERMANENT_BAN_DURATION = '876600h'
LIFT_BAN = 'none'


class UserAdminService:
    """Administration of user accounts: roles, warnings and suspensions."""

    @staticmethod
    def get_list(*, params: PageParams) -> PageData:
        """One page of users, newest first.

        :param params: page and size
        """
        return paginate(user_dao.select_all(), params)

    @staticmethod
    def _require_user(user_id: str) -> None:
        if not user_dao.exists(user_id):
            raise errors.NotFoundError(msg='User not found')

    @staticmethod
    def update_role(*, user: CurrentUser, user_id: str, obj: UpdateRoleParam) -> str:
        """Change a user's platform role.

        The actor is a super admin, so refusing to let them demote themselves keeps
        at least one super admin on the platform.

        :param user: the acting super admin
        :param user_id: the user to change
        :param obj: the new role
        """
        if user_id == user.sub and obj.role != UserRole.SUPER_ADMIN:
            raise errors.RequestError(msg='You cannot remove your own super admin role')

        UserAdminService._require_user(user_id)

        user_dao.set_role(user_id, obj.role)
        try:
            user_dao.sync_metadata_role(user_id, obj.role)
        except Exception as exc:
            # public.users is authoritative; the metadata mirror can lag.
            log.warning('Failed to mirror role into user_metadata for {}: {}', user_id, exc)

        audit_dao.record(user.sub, 'role_updated', 'user', user_id, {'role': obj.role})
        return f'Role updated to {obj.role}'

    @staticmethod
    def warn(*, user: CurrentUser, user_id: str) -> str:
        """Record a warning against a user.

        :param user: the admin
        :param user_id: the user warned
        """
        UserAdminService._require_user(user_id)
        # ponytail: recorded only — delivery needs the notification service wired up.
        audit_dao.record(user.sub, 'user_warned', 'user', user_id)
        return 'Warning recorded'

    @staticmethod
    def suspend(*, user: CurrentUser, user_id: str) -> str:
        """Suspend an account.

        :param user: the admin
        :param user_id: the user to suspend
        """
        if user_id == user.sub:
            raise errors.RequestError(msg='You cannot suspend yourself')

        UserAdminService._require_user(user_id)

        # ponytail: permanent only — timed suspensions are listed as remaining work.
        user_dao.set_ban(user_id, PERMANENT_BAN_DURATION)
        user_dao.set_suspended_at(user_id, True)
        invalidate_ban_cache(user_id)

        audit_dao.record(user.sub, 'user_suspended', 'user', user_id)
        return 'User suspended'

    @staticmethod
    def unsuspend(*, user: CurrentUser, user_id: str) -> str:
        """Lift a suspension.

        :param user: the admin
        :param user_id: the user to reinstate
        """
        UserAdminService._require_user(user_id)

        user_dao.set_ban(user_id, LIFT_BAN)
        user_dao.set_suspended_at(user_id, False)
        invalidate_ban_cache(user_id)

        audit_dao.record(user.sub, 'user_unsuspended', 'user', user_id)
        return 'User unsuspended'


user_admin_service: UserAdminService = UserAdminService()
