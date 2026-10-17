# backend/src/dependencies

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

FastAPI `Depends` helpers and the app error type.

- `auth.py`
  - `_decode_token` — verifies Supabase JWTs. HS256 via `SUPABASE_JWT_SECRET`; ES256 via the project JWKS (`/auth/v1/.well-known/jwks.json`, cached 1 h, refetched once on unknown `kid`). `aud` must be `authenticated`.
  - `get_current_user` — Bearer token → `{sub, email, role, user_metadata, amr, token}`. Role comes from `public.users` (authoritative), not the JWT. `amr` lists the session's auth methods (`password`, `recovery`, …). Rejects banned users (403) via `auth_helpers.is_user_banned`, which fails closed.
  - `require_admin` (admin | super_admin), `require_super_admin`, `require_company_manager(company_id, user)` (manager of that company, or any platform admin; `company_id` is a `UUIDStr`).
- `rate_limit.py` — slowapi `limiter` keyed by client IP, plus `user_rate_key` (`sub` of a *verified* token via `_decode_token`, HS256 or ES256; falls back to IP, so a forged `sub` can't burn someone else's quota). Behind a proxy set `FORWARDED_ALLOW_IPS`. Only routes decorated with `@limiter.limit(...)` are limited; there is no middleware, so `default_limits` is inert.
- `exceptions.py` — `AppError(status_code, body)`; `main.py` turns it into a JSON response.
- `__init__.py` — empty.

Known gaps: no `iss` check (the smoke scripts mint tokens without one); the role lookup isn't cached (one query per request — caching would delay demotions).
