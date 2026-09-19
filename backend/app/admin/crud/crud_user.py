from typing import Any

from backend.common.enums import UserRole
from backend.common.tables import DOMAINS, USERS
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

    @staticmethod
    def exists(user_id: str) -> bool:
        return bool(maybe_row(supabase.table(USERS).select('id').eq('id', user_id)))

    @staticmethod
    def get_by_email(email: str) -> dict | None:
        """Case-insensitive lookup, for granting manager rights by address."""
        return maybe_row(supabase.table(USERS).select('id, email').ilike('email', email))

    @staticmethod
    def select_all() -> Any:
        """Query builder for the admin user list, newest first."""
        return supabase.table(USERS).select('*', count='exact').order('created_at', desc=True)

    @staticmethod
    def get_domains() -> list[dict]:
        return (supabase.table(DOMAINS).select('id, name, slug').order('name').execute()).data or []

    @staticmethod
    def upsert_profile(payload: dict) -> None:
        """Write the onboarding answers onto the user row."""
        supabase.table(USERS).upsert(payload).execute()

    @staticmethod
    def set_role(user_id: str, role: str) -> None:
        """Set the role in public.users, the authoritative copy."""
        supabase.table(USERS).update({'role': role}).eq('id', user_id).execute()

    @staticmethod
    def set_suspended_at(user_id: str, suspended: bool) -> None:
        """Mirror the auth-side ban onto the user row.

        Display only: auth.users stays the source of truth for blocking login, but
        the admin list would otherwise need an auth API call per row.
        """
        supabase.table(USERS).update({'suspended_at': 'now()' if suspended else None}).eq(
            'id', user_id
        ).execute()

    @staticmethod
    def create_profile(payload: dict) -> None:
        supabase.table(USERS).insert(payload).execute()

    # --- Supabase auth admin API ---

    @staticmethod
    def sync_metadata_role(user_id: str, role: str) -> None:
        """Mirror the role into auth user_metadata, for clients reading the token."""
        supabase.auth.admin.update_user_by_id(user_id, {'user_metadata': {'role': role}})

    @staticmethod
    def set_ban(user_id: str, duration: str) -> None:
        """Ban or unban on the auth side. 'none' lifts it."""
        supabase.auth.admin.update_user_by_id(user_id, {'ban_duration': duration})

    @staticmethod
    def set_password(user_id: str, password: str) -> None:
        supabase.auth.admin.update_user_by_id(user_id, {'password': password})

    @staticmethod
    def delete_auth_user(user_id: str) -> None:
        supabase.auth.admin.delete_user(user_id)

    @staticmethod
    def sign_out(token: str) -> None:
        supabase.auth.admin.sign_out(token, scope='global')

    @staticmethod
    def sign_up(email: str, password: str) -> Any:
        return supabase.auth.sign_up({'email': email, 'password': password, 'options': {'data': {'role': 'user'}}})

    @staticmethod
    def sign_in(email: str, password: str) -> Any:
        return supabase.auth.sign_in_with_password({'email': email, 'password': password})

    @staticmethod
    def resend_verification(email: str) -> None:
        supabase.auth.resend({'type': 'signup', 'email': email})

    @staticmethod
    def send_password_reset(email: str) -> None:
        supabase.auth.reset_password_email(email)


user_dao: CRUDUser = CRUDUser()
