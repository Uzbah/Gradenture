import jwt
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.dependencies.auth import _decode_token

# Behind a reverse proxy, set FORWARDED_ALLOW_IPS to the proxy's address so
# uvicorn trusts X-Forwarded-For; otherwise every client shares the proxy's IP.
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def user_rate_key(request: Request) -> str:
    """Bucket by user id from a *verified* token (HS256 or ES256).

    Unverified decoding would let anyone forge a victim's `sub` and burn their
    quota; an invalid token falls back to IP and is rejected by auth anyway.
    """
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            sub = _decode_token(auth.split(" ", 1)[1].strip()).get("sub")
            if sub:
                return sub
        except (jwt.InvalidTokenError, TypeError):
            pass
    return get_remote_address(request)
