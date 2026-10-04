# backend/utils — small, dependency-light helpers

Nothing here knows about the domain. If a helper needs to know what a question or a
company is, it belongs in that module's service instead.

> Adding, renaming, deleting or repurposing a file in this folder means updating
> the table below in the same commit.

| File | Purpose |
|---|---|
| `sanitize.py` | `clean_text()` — strips HTML tags from user-submitted text. Applied by the service layer to every free-text field before it is stored. |
| `limiter.py` | The slowapi `limiter` and `user_rate_key()`, which keys limits by authenticated user and falls back to the client IP. Limits come from `settings.RATE_LIMIT_*`. |
| `trace_id.py` | The trace id context variable, `X-Request-ID` header name, and helpers used by `StateMiddleware` and the logger. |
| `openapi.py` | `ensure_unique_route_names()` (fails startup on a duplicate route function name) and `simplify_operation_ids()` (readable operation ids for generated clients). |
