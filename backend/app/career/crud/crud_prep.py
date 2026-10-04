from backend.common.tables import PREP_PROGRESS, USERS
from backend.database.supabase import maybe_row, supabase


class CRUDPrep:
    """Queries against prep_progress."""

    @staticmethod
    def get_user_domain(user_id: str) -> dict | None:
        """The caller's domain id and slug, joined from domains."""
        return maybe_row(supabase.table(USERS).select('domain_id, domains(slug)').eq('id', user_id))

    @staticmethod
    def get_progress(user_id: str, domain_id: str) -> list[dict]:
        return (
            supabase.table(PREP_PROGRESS)
            .select('topic, completed')
            .eq('user_id', user_id)
            .eq('domain_id', domain_id)
            .execute()
        ).data or []

    @staticmethod
    def set_topic(user_id: str, domain_id: str, topic: str, completed: bool) -> None:
        """Upsert on the (user, domain, topic) unique constraint."""
        supabase.table(PREP_PROGRESS).upsert(
            {
                'user_id': user_id,
                'domain_id': domain_id,
                'topic': topic,
                'completed': completed,
            },
            on_conflict='user_id,domain_id,topic',
        ).execute()


prep_dao: CRUDPrep = CRUDPrep()
