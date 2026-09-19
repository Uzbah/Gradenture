from typing import Any

from backend.common.enums import ContentStatus
from backend.common.tables import INTERVIEW_QUESTIONS
from backend.database.supabase import maybe_row, supabase


class CRUDQuestion:
    """Queries against interview_questions.

    Returns rows as dicts; the service layer decides what a caller may see.
    """

    @staticmethod
    def select_approved(
        domain_id: str | None = None,
        company_id: str | None = None,
        difficulty: str | None = None,
        question_type: str | None = None,
    ) -> Any:
        """Query builder for the public list, newest first.

        Returned unexecuted so `paginate()` can apply the range; selected with
        `count='exact'` so the page total is available.
        """
        query = (
            supabase.table(INTERVIEW_QUESTIONS)
            .select('*', count='exact')
            .eq('status', ContentStatus.APPROVED)
            .order('created_at', desc=True)
        )
        filters = (
            ('domain_id', domain_id),
            ('company_id', company_id),
            ('difficulty', difficulty),
            ('question_type', question_type),
        )
        for column, value in filters:
            if value:
                query = query.eq(column, value)
        return query

    @staticmethod
    def get_approved(question_id: str) -> dict | None:
        """One approved question, or None. Pending and rejected rows stay invisible."""
        return maybe_row(
            supabase.table(INTERVIEW_QUESTIONS)
            .select('*')
            .eq('id', question_id)
            .eq('status', ContentStatus.APPROVED)
        )

    @staticmethod
    def create(payload: dict) -> dict:
        """Insert a question and return the stored row."""
        result = supabase.table(INTERVIEW_QUESTIONS).insert(payload).execute()
        return result.data[0]

    @staticmethod
    def toggle_upvote(question_id: str, user_id: str) -> dict | None:
        """Add or remove the caller's upvote, atomically.

        One RPC rather than select + insert/delete + counter update + re-select, so
        the counter cannot drift from the upvote rows. See
        supabase/migrations/*_atomic_rpcs.sql.
        """
        result = supabase.rpc(
            'toggle_question_upvote',
            {'p_question_id': question_id, 'p_user_id': user_id},
        ).execute()
        rows = result.data or []
        return rows[0] if rows else None


question_dao: CRUDQuestion = CRUDQuestion()
