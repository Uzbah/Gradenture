# backend/database — data sources

The two clients the rest of the backend talks to. There is no ORM: the CRUD layer
addresses tables through PostgREST by name (see `backend/common/tables.py`).

> Adding, renaming, deleting or repurposing a file in this folder means updating
> the table below in the same commit.

| File | Purpose |
|---|---|
| `supabase.py` | The `supabase` client, built with the service-role key, and `maybe_row()` for single-row-or-None queries. |
| `redis.py` | `RedisCli` and the `redis_client` singleton: the shared cache, with `open()` (startup health check), `key()` (namespacing) and `delete_prefix()`. |

## Notes

- **Service role bypasses row level security.** Every authorization rule is enforced
  in application code — see `backend/common/security/permission.py`. A CRUD method
  that forgets a `.eq('user_id', ...)` filter is a data leak, not a bug in the RLS
  policy.
- **`maybe_row` exists for a reason**: supabase-py 2.x returns `None` rather than a
  response object when `maybe_single()` matches nothing, so `.data` raises
  `AttributeError`. Use it instead of `.maybe_single().execute().data`.
- **Both clients are synchronous.** Routes and services are `def`, not `async def`,
  so FastAPI runs them in the threadpool; an `async def` route would block the event
  loop on every PostgREST call.
- **PostgREST has no client-side transactions.** A write that must be atomic across
  statements belongs in a Postgres function called with `supabase.rpc(...)` — see
  `supabase/migrations/*_atomic_rpcs.sql`.

## What lives in Redis

| Key | Written by | TTL |
|---|---|---|
| `cb:jwks` | `common/security/jwt.py` — the Supabase JWKS document | `CACHE_JWKS_TTL` (1h) |
| `cb:ban:<user_id>` | `common/security/jwt.py` — whether the account is suspended | `CACHE_BAN_TTL` (60s) |
| `LIMITER/...` | slowapi, when `RATE_LIMIT_STORAGE_URI` is set | per limit |

These were in-process caches before, which meant a suspension took effect in one
worker at a time. Cache reads and writes are wrapped so a Redis blip degrades to a
direct lookup rather than a failed request.
