from typing import Any

from backend.common.tables import APPLICATIONS
from backend.database.supabase import maybe_row, supabase


class CRUDApplication:
    """Queries against applications.

    Every method is scoped to a user id. The service role bypasses RLS, so an
    unscoped query here would expose one user's tracker to another.
    """

    @staticmethod
    def select_for_user(user_id: str, status: str | None = None) -> Any:
        query = (
            supabase.table(APPLICATIONS)
            .select('*', count='exact')
            .eq('user_id', user_id)
            .order('created_at', desc=True)
        )
        if status:
            query = query.eq('status', status)
        return query

    @staticmethod
    def get_own(application_id: str, user_id: str) -> dict | None:
        return maybe_row(
            supabase.table(APPLICATIONS).select('*').eq('id', application_id).eq('user_id', user_id)
        )

    @staticmethod
    def create(payload: dict) -> dict:
        result = supabase.table(APPLICATIONS).insert(payload).execute()
        return result.data[0]

    @staticmethod
    def update_own(application_id: str, user_id: str, payload: dict) -> dict | None:
        result = (
            supabase.table(APPLICATIONS)
            .update(payload)
            .eq('id', application_id)
            .eq('user_id', user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    @staticmethod
    def delete_own(application_id: str, user_id: str) -> bool:
        result = (
            supabase.table(APPLICATIONS).delete().eq('id', application_id).eq('user_id', user_id).execute()
        )
        return bool(result.data)


application_dao: CRUDApplication = CRUDApplication()
