from backend.common.tables import CONTENT_FLAGS, FLAGGABLE
from backend.database.supabase import supabase


class CRUDFlag:
    """Queries against content_flags.

    Flags are created by readers (career module) and worked by moderators (admin
    module); both go through here so the shape of a flag is defined in one place.
    """

    @staticmethod
    def create(reported_by: str, content_type: str, content_id: str, reason: str) -> dict:
        result = (
            supabase.table(CONTENT_FLAGS)
            .insert(
                {
                    'reported_by': reported_by,
                    'content_type': content_type,
                    'content_id': content_id,
                    'reason': reason,
                }
            )
            .execute()
        )
        return result.data[0]

    @staticmethod
    def get_open() -> list[dict]:
        return (supabase.table(CONTENT_FLAGS).select('*').eq('status', 'open').order('created_at').execute()).data or []

    @staticmethod
    def get_flagged_content(content_type: str, content_id: str) -> dict | None:
        """The question or review a flag points at."""
        table = FLAGGABLE.get(content_type)
        if not table:
            return None
        result = supabase.table(table).select('*').eq('id', content_id).limit(1).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def resolve(flag_id: str, status: str, actor_id: str) -> bool:
        """Close an open flag and audit it, atomically. False when nothing was open."""
        result = supabase.rpc(
            'resolve_content_flag',
            {'p_flag_id': flag_id, 'p_status': status, 'p_actor': actor_id},
        ).execute()
        return bool(result.data)


flag_dao: CRUDFlag = CRUDFlag()
