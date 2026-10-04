import sys

from redis import BlockingConnectionPool, Redis
from redis.exceptions import AuthenticationError, RedisError

from backend.common.log import log
from backend.core.conf import settings


class RedisCli(Redis):
    """Redis client for the caches that must be shared between workers.

    Synchronous, like the rest of the data access in this backend: routes are
    ``def`` and run in the threadpool, because supabase-py is synchronous and an
    ``async def`` route would block the event loop on every PostgREST call.
    """

    def __init__(self) -> None:
        pool = BlockingConnectionPool(
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            timeout=settings.REDIS_POOL_TIMEOUT,
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            db=settings.REDIS_DATABASE,
            socket_timeout=settings.REDIS_TIMEOUT,
            socket_connect_timeout=settings.REDIS_TIMEOUT,
            socket_keepalive=True,
            health_check_interval=30,
            decode_responses=True,
        )
        super().__init__(connection_pool=pool)

    def open(self) -> None:
        """Check the connection at startup.

        A cache that is silently missing would degrade auth to one Supabase call per
        request, so this fails the process instead.
        """
        try:
            self.ping()
        except TimeoutError:
            log.error('Redis connection timed out')
            sys.exit(1)
        except AuthenticationError:
            log.error('Redis authentication failed')
            sys.exit(1)
        except RedisError as exc:
            log.error('Redis connection failed: {}', exc)
            sys.exit(1)
        else:
            log.info('Redis connected at {}:{}/{}', settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DATABASE)

    @staticmethod
    def key(*parts: str) -> str:
        """Build a namespaced key, e.g. ``cb:ban:<user_id>``."""
        return ':'.join((settings.REDIS_KEY_PREFIX, *parts))

    def delete_prefix(self, prefix: str) -> int:
        """Delete every key under a namespaced prefix."""
        keys = list(self.scan_iter(match=f'{prefix}*'))
        return self.delete(*keys) if keys else 0


redis_client: RedisCli = RedisCli()
