# backend/src/dependencies

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

FastAPI `Depends` helpers and the app error type.

- `auth.py`
  - `_decode_token` — verifies Supabase JWTs. HS256 via `SUPABASE_JWT_SECRET`; ES256 via the project JWKS (`/auth/v1/.well-known/jwks.json`, cached 1 h, refetched once on unknown `kid`). `aud` is not verified.
  - `get_current_user` — Bearer token → `{sub, email, role, user_metadata, token}`. Role comes from `public.users` (authoritative), not the JWT. Rejects banned users (403) via `auth_helpers.is_user_banned`.
  - `require_admin` (admin | super_admin), `require_super_admin`, `require_company_manager(company_id, user)` (manager of that company, or any platform admin).
- `rate_limit.py` — slowapi `limiter` keyed by client IP, plus `user_rate_key` (JWT `sub`, falls back to IP). Only routes decorated with `@limiter.limit(...)` are limited; there is no middleware, so `default_limits` is inert.
- `exceptions.py` — `AppError(status_code, body)`; `main.py` turns it into a JSON response.
- `__init__.py` — empty.

Known gaps (see security review): ban check fails open on Supabase errors; IP keying breaks behind a proxy; no `aud`/`iss` check.
