import logging
import time
from datetime import datetime, timezone
from threading import Lock

from src.config.supabase import supabase

logger = logging.getLogger(__name__)

_BAN_CACHE: dict[str, tuple[bool, float]] = {}
_BAN_CACHE_TTL = 60
_ban_lock = Lock()


def rollback_auth_user(user_id: str) -> None:
    """Remove auth user when public.users insert fails (avoid orphans)."""
    try:
        supabase.auth.admin.delete_user(user_id)
    except Exception as e:
        logger.warning("Failed to rollback auth user %s: %s", user_id, e)


def sync_user_metadata_role(user_id: str, role: str = "user") -> None:
    try:
        supabase.auth.admin.update_user_by_id(
            user_id, {"user_metadata": {"role": role}}
        )
    except Exception as e:
        logger.warning("Failed to sync user_metadata.role for %s: %s", user_id, e)


def get_user_role(user_id: str) -> str:
    """Authoritative role from public.users (matches admin role updates)."""
    result = (
        supabase.table("users")
        .select("role")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    if result.data and result.data.get("role"):
        return result.data["role"]
    return "user"


def is_user_banned(user_id: str) -> bool:
    now = time.time()
    with _ban_lock:
        cached = _BAN_CACHE.get(user_id)
        if cached and now - cached[1] < _BAN_CACHE_TTL:
            return cached[0]

    banned = _check_banned_from_auth(user_id)

    with _ban_lock:
        _BAN_CACHE[user_id] = (banned, now)
    return banned


def _check_banned_from_auth(user_id: str) -> bool:
    try:
        resp = supabase.auth.admin.get_user_by_id(user_id)
        banned_until = getattr(resp.user, "banned_until", None)
        if not banned_until:
            return False
        if isinstance(banned_until, str):
            dt = datetime.fromisoformat(banned_until.replace("Z", "+00:00"))
        else:
            dt = banned_until
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt > datetime.now(timezone.utc)
    except Exception as e:
        logger.warning("Ban check failed for %s: %s", user_id, e)
        return False


def invalidate_ban_cache(user_id: str) -> None:
    with _ban_lock:
        _BAN_CACHE.pop(user_id, None)
