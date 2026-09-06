import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def _init() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    return create_client(url, key)


supabase: Client = _init()


def maybe_row(query) -> dict | None:
    """Single row or None.

    supabase-py 2.x returns None instead of a response object when
    maybe_single() matches no rows, so `.data` on it raises AttributeError.
    """
    result = query.maybe_single().execute()
    return result.data if result else None
