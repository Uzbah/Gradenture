import os

import jwt
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def user_rate_key(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(
                token,
                os.getenv("SUPABASE_JWT_SECRET"),
                algorithms=["HS256"],
                options={"verify_aud": False, "verify_exp": False},
            )
            sub = payload.get("sub")
            if sub:
                return sub
        except jwt.InvalidTokenError:
            pass
    return get_remote_address(request)
