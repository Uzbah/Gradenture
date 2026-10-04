from typing import Any

from backend.common.enums import CompanyStatus
from backend.common.tables import COMPANIES, COMPANY_ADMINS, COMPANY_EDIT_REQUESTS
from backend.database.supabase import maybe_row, supabase


class CRUDCompany:
    """Queries against companies and the tables hanging off them."""

    @staticmethod
    def select_approved(q: str | None = None) -> Any:
        """Query builder for the public registry, by name."""
        query = supabase.table(COMPANIES).select('*', count='exact').eq('status', CompanyStatus.APPROVED)
        if q:
            query = query.ilike('name', f'%{q}%')
        return query.order('name')

    @staticmethod
    def get_approved(company_id: str) -> dict | None:
        return maybe_row(
            supabase.table(COMPANIES).select('*').eq('id', company_id).eq('status', CompanyStatus.APPROVED)
        )

    @staticmethod
    def exists(company_id: str) -> bool:
        return bool(maybe_row(supabase.table(COMPANIES).select('id').eq('id', company_id)))

    @staticmethod
    def get_by_name(name: str) -> dict | None:
        """Case-insensitive exact-name lookup, for the duplicate check on submission."""
        return maybe_row(supabase.table(COMPANIES).select('id').ilike('name', name))

    @staticmethod
    def create(payload: dict) -> dict:
        result = supabase.table(COMPANIES).insert(payload).execute()
        return result.data[0]

    @staticmethod
    def get_managed_by(user_id: str) -> list[dict]:
        """Companies this user has been granted management rights over."""
        rows = (supabase.table(COMPANY_ADMINS).select('companies(*)').eq('user_id', user_id).execute()).data or []
        return [row['companies'] for row in rows if row.get('companies')]

    @staticmethod
    def get_pending_edit(company_id: str) -> dict | None:
        """The open edit request for a company, if there is one.

        One at a time: a second proposal while the first is unreviewed would make
        the approved changes depend on the order an admin happened to click in.
        """
        return maybe_row(
            supabase.table(COMPANY_EDIT_REQUESTS).select('id').eq('company_id', company_id).eq('status', 'pending')
        )

    @staticmethod
    def create_edit_request(payload: dict) -> dict:
        result = supabase.table(COMPANY_EDIT_REQUESTS).insert(payload).execute()
        return result.data[0]


company_dao: CRUDCompany = CRUDCompany()
