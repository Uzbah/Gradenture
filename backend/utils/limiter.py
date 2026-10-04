import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from backend.core.conf import settings


def user_rate_key(request: Request) -> str:
    """Rate-limit key: the authenticated user, falling back to the client IP.

    The token is decoded without verifying its expiry — an expired token still
    identifies who is calling, and the auth dependency rejects it separately.
    """
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        token = auth.split(' ', 1)[1].strip()
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=['HS256'],
                options={'verify_aud': False, 'verify_exp': False},
            )
        except jwt.InvalidTokenError:
            pass
        else:
            sub = payload.get('sub')
            if sub:
                return sub
    return get_remote_address(request)


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    storage_uri=settings.RATE_LIMIT_STORAGE_URI or None,
    enabled=settings.RATE_LIMIT_ENABLED,
)
