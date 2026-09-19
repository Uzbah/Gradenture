# backend/core — application wiring

Settings, filesystem paths, and the one function that builds the FastAPI app.
Nothing here contains business logic; everything here runs once, at startup.

> Adding, renaming, deleting or repurposing a file in this folder means updating
> the table below in the same commit.

| File | Purpose |
|---|---|
| `conf.py` | `Settings` (pydantic-settings) and the `settings` singleton. Every environment variable the backend reads is declared here — no module calls `os.getenv`. Missing required values fail at import time. |
| `path_conf.py` | Filesystem paths derived from the package location: `BASE_PATH`, `REPO_PATH`, `ENV_FILE_PATH`, `LOG_DIR`, `MIGRATION_DIR`, `FRONTEND_DIST_DIR`. |
| `registrar.py` | `register_app()` — the app factory — plus the `register_*` helpers it calls and the `register_init` lifespan. |

## Registration order in `register_app()`

1. `setup_logging()` — before anything that might log.
2. `FastAPI(...)` with `lifespan=register_init`, which opens Redis on startup and
   closes it on shutdown.
3. `register_rate_limiter` — puts the limiter on `app.state`, where slowapi's
   decorators look for it.
4. `register_middleware` — added innermost-first. Starlette runs middleware in
   reverse registration order, so the reading order here is inside-out: access log
   wraps request state, CORS wraps both.
5. `register_router` — builds the `/api/v1` router, includes each module's router,
   then `ensure_unique_route_names` and `simplify_operation_ids`.
6. `register_exception` — handlers are registered after the routes they cover.
7. `register_static_file` — mounts the built frontend at `/`, last, so it never
   shadows an API path.

## Conventions

- Read configuration as `settings.X`. Do not add `os.getenv` calls, and do not call
  `load_dotenv` — pydantic-settings owns `.env`.
- A new setting needs a default here *and* an entry in `backend/.env.example`.
