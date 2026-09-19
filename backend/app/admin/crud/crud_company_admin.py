from typing import Any

from backend.common.tables import COMPANIES, COMPANY_ADMINS, COMPANY_EDIT_REQUESTS
from backend.database.supabase import maybe_row, supabase


class CRUDCompanyAdmin:
    """Company administration: the full registry, managers, merges and edit requests.

    The reader-facing company queries live in app/career/crud/crud_company.py; these
    are the ones that see pending rows and change them.
    """

    @staticmethod
    def select_all(q: str | None = None, status: str | None = None) -> Any:
        """Query builder for the admin list: every company, not only approved ones."""
        query = supabase.table(COMPANIES).select('*', count='exact')
        if q:
            query = query.ilike('name', f'%{q}%')
        if status:
            query = query.eq('status', status)
        return query.order('name')

    @staticmethod
    def update(company_id: str, fields: dict) -> dict | None:
        result = supabase.table(COMPANIES).update(fields).eq('id', company_id).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def create(payload: dict) -> dict:
        result = supabase.table(COMPANIES).insert(payload).execute()
        return result.data[0]

    @staticmethod
    def merge(from_id: str, into_id: str, actor_id: str) -> dict | None:
        """Repoint content, delete the duplicate and audit it, atomically.

        None when either company is missing. See
        supabase/migrations/*_atomic_rpcs.sql.
        """
        result = supabase.rpc(
            'merge_company',
            {'p_from': from_id, 'p_into': into_id, 'p_actor': actor_id},
        ).execute()
        return result.data or None

    # --- managers ---

    @staticmethod
    def get_managers(company_id: str) -> list[dict]:
        return (
            supabase.table(COMPANY_ADMINS)
            .select('user_id, created_at, users!company_admins_user_id_fkey(email)')
            .eq('company_id', company_id)
            .execute()
        ).data or []

    @staticmethod
    def is_manager(company_id: str, user_id: str) -> bool:
        return bool(
            maybe_row(
                supabase.table(COMPANY_ADMINS).select('user_id').eq('company_id', company_id).eq('user_id', user_id)
            )
        )

    @staticmethod
    def grant_manager(company_id: str, user_id: str, granted_by: str) -> None:
        supabase.table(COMPANY_ADMINS).insert(
            {'company_id': company_id, 'user_id': user_id, 'granted_by': granted_by}
        ).execute()

    @staticmethod
    def revoke_manager(company_id: str, user_id: str) -> bool:
        result = supabase.table(COMPANY_ADMINS).delete().eq('company_id', company_id).eq('user_id', user_id).execute()
        return bool(result.data)

    # --- profile edit requests ---

    @staticmethod
    def get_pending_edits() -> list[dict]:
        return (
            supabase.table(COMPANY_EDIT_REQUESTS)
            .select('*, companies(name)')
            .eq('status', 'pending')
            .order('created_at')
            .execute()
        ).data or []

    @staticmethod
    def decide_edit(request_id: str, status: str, admin_note: str | None, actor_id: str) -> dict | None:
        """Apply the changes when approving, close the request and audit it, atomically.

        None when there is no pending request with that ID.
        """
        result = supabase.rpc(
            'decide_company_edit',
            {
                'p_request_id': request_id,
                'p_status': status,
                'p_admin_note': admin_note,
                'p_actor': actor_id,
            },
        ).execute()
        return result.data or None


company_admin_dao: CRUDCompanyAdmin = CRUDCompanyAdmin()
