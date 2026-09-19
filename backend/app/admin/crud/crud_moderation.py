from backend.common.enums import ContentStatus
from backend.common.tables import COMPANIES, INTERVIEW_QUESTIONS, INTERVIEW_REVIEWS
from backend.database.supabase import supabase


class CRUDModeration:
    """The moderation queue, and the decisions taken on it."""

    @staticmethod
    def get_pending(table: str) -> list[dict]:
        """Everything awaiting review in one table, oldest first."""
        return (
            supabase.table(table)
            .select('*')
            .eq('status', ContentStatus.PENDING)
            .order('created_at')
            .execute()
        ).data or []

    @staticmethod
    def get_queue() -> dict:
        """The whole queue: questions, reviews and companies."""
        return {
            'questions': CRUDModeration.get_pending(INTERVIEW_QUESTIONS),
            'reviews': CRUDModeration.get_pending(INTERVIEW_REVIEWS),
            'companies': CRUDModeration.get_pending(COMPANIES),
        }

    @staticmethod
    def moderate(kind: str, content_id: str, status: str, admin_note: str | None, actor_id: str) -> bool:
        """Record a decision and audit it, atomically. False when nothing matched.

        See supabase/migrations/*_atomic_rpcs.sql: the update and the audit row used
        to be separate statements, so content could be moderated with no record of
        who did it.
        """
        result = supabase.rpc(
            'moderate_content',
            {
                'p_kind': kind,
                'p_content_id': content_id,
                'p_status': status,
                'p_admin_note': admin_note,
                'p_actor': actor_id,
            },
        ).execute()
        return bool(result.data)


moderation_dao: CRUDModeration = CRUDModeration()
