from backend.common.tables import ADMIN_AUDIT_LOG
from backend.database.supabase import supabase


class CRUDAudit:
    """Writes to admin_audit_log.

    Every admin mutation records here. Failures surface loudly, by design: an
    unrecorded moderation decision is worse than a failed one.

    Actions taken through an RPC — moderation, flag resolution, company merges and
    edit decisions — write their own audit row inside the same transaction, so they
    do not call this.
    """

    @staticmethod
    def record(
        actor_id: str,
        action: str,
        target_type: str,
        target_id: str | None = None,
        detail: dict | None = None,
    ) -> None:
        supabase.table(ADMIN_AUDIT_LOG).insert(
            {
                'actor_id': actor_id,
                'action': action,
                'target_type': target_type,
                'target_id': target_id,
                'detail': detail,
            }
        ).execute()


audit_dao: CRUDAudit = CRUDAudit()
