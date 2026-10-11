import os
from pathlib import Path

from supabase import ClientOptions, create_client, Client
from dotenv import load_dotenv

# Anchored to backend/.env rather than the CWD (see main.py).
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _init() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    return create_client(url, key)


supabase: Client = _init()


def auth_client() -> Client:
    """Throwaway client for end-user auth calls (sign-up, sign-in, refresh, emails).

    supabase-py swaps a client's Authorization header to the user's JWT on
    SIGNED_IN / TOKEN_REFRESHED. On the shared client above that would make every
    later query from every request run as that user, so user sessions never touch it.
    """
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        options=ClientOptions(auto_refresh_token=False, persist_session=False),
    )


def maybe_row(query) -> dict | None:
    """Single row or None.

    supabase-py 2.x returns None instead of a response object when
    maybe_single() matches no rows, so `.data` on it raises AttributeError.
    """
    result = query.maybe_single().execute()
    return result.data if result else None
