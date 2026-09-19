from typing import Any

from backend.common.enums import UserRole
from backend.common.tables import USERS
from backend.database.supabase import maybe_row, supabase


class CRUDUser:
    """Queries against public.users and the Supabase auth admin API."""

    @staticmethod
    def get_role(user_id: str) -> UserRole:
        """The caller's authoritative role.

        public.users.role is the source of truth — auth user_metadata is only a
        mirror kept for clients that read the token directly.
        """
        row = maybe_row(supabase.table(USERS).select('role').eq('id', user_id))
        if row and row.get('role'):
            return UserRole(row['role'])
        return UserRole.USER

    @staticmethod
    def get_auth_user(user_id: str) -> Any:
        """The auth-side user record, which carries the ban state."""
        return supabase.auth.admin.get_user_by_id(user_id)

    @staticmethod
    def get_by_id(user_id: str) -> dict | None:
        return maybe_row(supabase.table(USERS).select('*').eq('id', user_id))


user_dao: CRUDUser = CRUDUser()
