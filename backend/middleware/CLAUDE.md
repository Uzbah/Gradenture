# backend/middleware — per-request cross-cutting behaviour

> Adding, renaming, deleting or repurposing a file in this folder means updating
> the table below in the same commit.

| File | Purpose |
|---|---|
| `state_middleware.py` | Assigns the request a trace id (reusing an inbound `X-Request-ID` when a proxy sent one), records the client IP on `request.state`, and echoes the id back in the response headers. |
| `access_middleware.py` | Logs one line per request: IP, method, path, status, elapsed ms. |

## Order

Registered in `core/registrar.py:register_middleware`. Starlette runs middleware in
reverse order of registration, so with the current list the outermost is CORS, then
`StateMiddleware`, then `AccessMiddleware`.

`StateMiddleware` must stay outside `AccessMiddleware`: it sets the trace id that the
access log — and every other log line in the request — prints.
