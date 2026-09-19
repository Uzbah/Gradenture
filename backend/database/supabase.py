from typing import Any

from supabase import Client, create_client

from backend.core.conf import settings


def _init() -> Client:
    """Build the service-role client.

    The service role bypasses row level security, so every authorization rule is
    enforced in application code — see ``backend.common.security.permission``.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


supabase: Client = _init()


def maybe_row(query: Any) -> dict | None:
    """Single row or None.

    supabase-py 2.x returns None instead of a response object when ``maybe_single()``
    matches no rows, so reading ``.data`` on it raises AttributeError.
    """
    result = query.maybe_single().execute()
    return result.data if result else None
