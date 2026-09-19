import json

from datetime import datetime, timezone
from typing import Annotated

import jwt
import requests

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.algorithms import ECAlgorithm
from redis.exceptions import RedisError

from backend.app.admin.crud.crud_user import user_dao
from backend.common.dataclasses import CurrentUser
from backend.common.exception.errors import ForbiddenError, TokenError
from backend.common.log import log
from backend.core.conf import settings
from backend.database.redis import redis_client

_bearer = HTTPBearer(auto_error=False)

# Supabase rotates its JWKS rarely; both caches live in Redis so every worker sees
# the same state (a ban must take effect everywhere, not per-process).
_JWKS_CACHE_KEY = redis_client.key('jwks')
_BAN_CACHE_PREFIX = redis_client.key('ban')


def _ban_cache_key(user_id: str) -> str:
    return f'{_BAN_CACHE_PREFIX}:{user_id}'


def _fetch_jwks() -> dict:
    """Fetch the raw JWKS document from Supabase."""
    response = requests.get(settings.SUPABASE_JWKS_URL, timeout=5)
    response.raise_for_status()
    return response.json()


def _jwks_keys(force: bool = False) -> dict:
    """Public keys by key id, cached in Redis.

    :param force: skip the cache, for the case of a token signed with a key id we
        have not seen — Supabase has rotated since the document was cached.
    """
    raw = None
    if not force:
        try:
            raw = redis_client.get(_JWKS_CACHE_KEY)
        except RedisError as exc:
            log.warning('JWKS cache read failed: {}', exc)

    if raw is None:
        try:
            document = _fetch_jwks()
        except requests.RequestException as exc:
            raise jwt.InvalidTokenError('JWKS unavailable') from exc
        raw = json.dumps(document)
        try:
            redis_client.set(_JWKS_CACHE_KEY, raw, ex=settings.CACHE_JWKS_TTL)
        except RedisError as exc:
            log.warning('JWKS cache write failed: {}', exc)

    return {key['kid']: ECAlgorithm.from_jwk(json.dumps(key)) for key in json.loads(raw).get('keys', [])}


def decode_token(token: str) -> dict:
    """Verify a Supabase access token and return its claims.

    Supabase issues HS256 tokens signed with the project's JWT secret, and ES256
    tokens verified against the project's JWKS; both are accepted.
    """
    header = jwt.get_unverified_header(token)
    algorithm = header.get('alg', 'HS256')

    if algorithm == 'HS256':
        return jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=['HS256'],
            options={'verify_aud': False},
        )

    keys = _jwks_keys()
    public_key = keys.get(header.get('kid'))
    if not public_key:
        keys = _jwks_keys(force=True)
        public_key = keys.get(header.get('kid'))
        if not public_key:
            raise jwt.InvalidTokenError('Unknown key id')

    return jwt.decode(token, public_key, algorithms=['ES256'], options={'verify_aud': False})


def is_banned(user_id: str) -> bool:
    """Whether the account is currently suspended, cached briefly in Redis."""
    key = _ban_cache_key(user_id)
    try:
        cached = redis_client.get(key)
    except RedisError as exc:
        log.warning('Ban cache read failed: {}', exc)
        cached = None

    if cached is not None:
        return cached == '1'

    banned = _check_banned(user_id)

    try:
        redis_client.set(key, '1' if banned else '0', ex=settings.CACHE_BAN_TTL)
    except RedisError as exc:
        log.warning('Ban cache write failed: {}', exc)
    return banned


def invalidate_ban_cache(user_id: str) -> None:
    """Drop the cached ban state so a suspension takes effect immediately."""
    try:
        redis_client.delete(_ban_cache_key(user_id))
    except RedisError as exc:
        log.warning('Ban cache invalidation failed: {}', exc)


def _check_banned(user_id: str) -> bool:
    """Read the ban state from Supabase auth.

    A lookup failure is treated as not banned: the alternative locks every user out
    whenever the auth API has a bad minute.
    """
    try:
        response = user_dao.get_auth_user(user_id)
        banned_until = getattr(response.user, 'banned_until', None)
        if not banned_until:
            return False
        if isinstance(banned_until, str):
            expires = datetime.fromisoformat(banned_until.replace('Z', '+00:00'))
        else:
            expires = banned_until
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return expires > datetime.now(timezone.utc)
    except Exception as exc:
        log.warning('Ban check failed for {}: {}', user_id, exc)
        return False


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> CurrentUser:
    """Resolve the caller from the bearer token.

    Raises rather than returning None, so a route that declares this dependency is
    authenticated by construction.
    """
    if credentials is None or not credentials.credentials.strip():
        raise TokenError

    token = credentials.credentials.strip()

    try:
        claims = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise TokenError(msg='Token expired')
    except jwt.InvalidTokenError:
        raise TokenError(msg='Invalid token')

    user_id = claims.get('sub')
    if not user_id:
        raise TokenError(msg='Invalid token')

    if is_banned(user_id):
        raise ForbiddenError(msg='Account suspended')

    return CurrentUser(
        sub=user_id,
        email=claims.get('email'),
        role=user_dao.get_role(user_id),
        metadata=claims.get('user_metadata', {}),
        token=token,
    )


# Declare on a route to require authentication and receive the caller.
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]

# Declare in a route's `dependencies=[...]` to require authentication without using the caller.
DependsJwtAuth = Depends(get_current_user)
