from typing import Any

from backend.common.enums import ContentStatus
from backend.common.tables import INTERVIEW_REVIEWS
from backend.database.supabase import maybe_row, supabase


class CRUDReview:
    """Queries against interview_reviews."""

    @staticmethod
    def select_approved(company_id: str | None = None, domain_id: str | None = None) -> Any:
        """Query builder for the public list, newest first."""
        query = (
            supabase.table(INTERVIEW_REVIEWS)
            .select('*', count='exact')
            .eq('status', ContentStatus.APPROVED)
            .order('created_at', desc=True)
        )
        for column, value in (('company_id', company_id), ('domain_id', domain_id)):
            if value:
                query = query.eq(column, value)
        return query

    @staticmethod
    def get_approved(review_id: str) -> dict | None:
        return maybe_row(
            supabase.table(INTERVIEW_REVIEWS)
            .select('*')
            .eq('id', review_id)
            .eq('status', ContentStatus.APPROVED)
        )

    @staticmethod
    def create(payload: dict) -> dict:
        result = supabase.table(INTERVIEW_REVIEWS).insert(payload).execute()
        return result.data[0]


review_dao: CRUDReview = CRUDReview()
