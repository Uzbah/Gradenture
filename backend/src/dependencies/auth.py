import json
import os
import time
from typing import Annotated

import jwt
import requests
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.algorithms import ECAlgorithm

from src.services.auth_helpers import get_user_role, is_user_banned

_bearer = HTTPBearer(auto_error=False)

_jwks_state: dict = {"keys": {}, "fetched_at": 0.0}
JWKS_TTL_SEC = 3600


def _fetch_jwks_keys(force: bool = False) -> dict:
    now = time.time()
    if (
        not force
        and _jwks_state["keys"]
        and now - _jwks_state["fetched_at"] < JWKS_TTL_SEC
    ):
        return _jwks_state["keys"]

    url = f"{os.getenv('SUPABASE_URL')}/auth/v1/.well-known/jwks.json"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    keys = {}
    for key in resp.json().get("keys", []):
        keys[key["kid"]] = ECAlgorithm.from_jwk(json.dumps(key))
    _jwks_state["keys"] = keys
    _jwks_state["fetched_at"] = now
    return keys


def _decode_token(token: str) -> dict:
    header = jwt.get_unverified_header(token)
    alg = header.get("alg", "HS256")

    if alg == "HS256":
        return jwt.decode(
            token,
            os.getenv("SUPABASE_JWT_SECRET"),
            algorithms=["HS256"],
            options={"verify_aud": False},
        )

    try:
        keys = _fetch_jwks_keys()
    except requests.RequestException as exc:
        raise jwt.InvalidTokenError("JWKS unavailable") from exc

    public_key = keys.get(header.get("kid"))
    if not public_key:
        try:
            keys = _fetch_jwks_keys(force=True)
            public_key = keys.get(header.get("kid"))
        except requests.RequestException as exc:
            raise jwt.InvalidTokenError("JWKS unavailable") from exc
        if not public_key:
            raise jwt.InvalidTokenError("Unknown key id")

    return jwt.decode(
        token,
        public_key,
        algorithms=["ES256"],
        options={"verify_aud": False},
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> dict:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail={"error": "Unauthorized"})

    token = credentials.credentials.strip()
    if not token:
        raise HTTPException(status_code=401, detail={"error": "Unauthorized"})

    try:
        payload = _decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail={"error": "Token expired"})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail={"error": "Invalid token"})

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail={"error": "Invalid token"})

    if is_user_banned(user_id):
        raise HTTPException(status_code=403, detail={"error": "Account suspended"})

    role = get_user_role(user_id)

    return {
        "sub":           user_id,
        "email":         payload.get("email"),
        "role":          role,
        "user_metadata": payload.get("user_metadata", {}),
        "token":         token,
    }


def require_admin(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    if user.get("role") not in ("admin", "super_admin"):
        raise HTTPException(status_code=403, detail={"error": "Forbidden"})
    return user


def require_super_admin(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    if user.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail={"error": "Forbidden"})
    return user
