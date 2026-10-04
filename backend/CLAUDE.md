# CareerBridge Backend — CLAUDE.md

FastAPI + Supabase (Postgres). The API is served at `/api/v1`, and the built
frontend (`../frontend/dist`) at `/` when it exists.

**Standing rule:** adding, renaming, deleting or repurposing a file means updating
that folder's `CLAUDE.md` table in the same commit.

## Layout

`backend/` is the importable package, so everything imports absolutely as
`backend.<area>` and the app is run from the repository root
(`python -m backend.run`). Each area documents its own files:

```
main.py            # app = register_app(), three lines
run.py             # dev entry point: python -m backend.run
app/
├── admin/         # auth, own profile, moderation, admin ops   -> app/admin/CLAUDE.md
└── career/        # questions, reviews, companies, applications, prep, resume
                   #                                            -> app/career/CLAUDE.md
common/            # response envelope, errors, pagination, security, enums
                   #                                            -> common/CLAUDE.md
core/              # settings, paths, register_app()             -> core/CLAUDE.md
database/          # supabase + redis clients                    -> database/CLAUDE.md
middleware/        # trace id, access log                        -> middleware/CLAUDE.md
utils/             # sanitize, limiter, trace id, openapi        -> utils/CLAUDE.md
scripts/migrate.py # SQL migration runner (status / up / baseline)
tests/             # pytest + httpx ASGI                         -> tests/CLAUDE.md
```

Each feature module is the same four folders: `api/v1/` (routes), `service/`
(rules), `crud/` (data access), `schema/` (pydantic models).

## Layering

| Layer | May import | Must not |
|---|---|---|
| `api/v1/*.py` | schema, service, `common.security`, `common.response`, `common.pagination` | the supabase client, `crud.*` |
| `service/*.py` | crud, other services, `common.exception.errors`, schema | `fastapi`, HTTP status codes, `Request` |
| `crud/*.py` | `database.supabase`, `common.tables` | schemas — it takes and returns dicts |
| `schema/*.py` | pydantic, `common.enums`, `common.schema` | — |

Naming follows fastapi-best-architecture: `crud_question.py` defines
`class CRUDQuestion` and the singleton `question_dao`; `question_service.py`
defines `class QuestionService` and `question_service`; schemas are
`CreateXParam` / `UpdateXParam` / `GetXDetail` / `XSchemaBase`.

## Conventions

- **Every response is `{code, msg, data}`.** Routes return
  `response_base.success(data=...)` and annotate `-> ResponseSchemaModel[XDetail]`;
  list routes return `ResponseSchemaModel[PageData[XDetail]]`. Services return
  plain data and never build an envelope.
- **Errors are raised, not returned.** Services raise from
  `common.exception.errors`; the handlers registered in `register_exception` turn
  them into the same envelope. Validation errors carry `{field: [message, ...]}`
  in `data`.
- **Routes and services are `def`, not `async def`.** supabase-py is synchronous,
  so FastAPI runs them in the threadpool; an `async def` route would block the
  event loop on every PostgREST call. The one `async def` route, `/resume/analyze`,
  is async only to await the upload and offloads the analysis with
  `run_in_threadpool`.
- **Configuration is `settings.X`.** No `os.getenv`, no `load_dotenv` — a new
  setting needs a field in `core/conf.py` and a line in `.env.example`.
- **Multi-statement writes go through a Postgres function**, not a sequence of
  PostgREST calls: there is no client-side transaction. See
  `supabase/migrations/*_atomic_rpcs.sql`.
- **The service role bypasses RLS**, so authorization is enforced entirely in
  `common/security/permission.py` and in CRUD methods that scope by user id.
- **User-submitted text goes through `clean_text()`** before it is stored.

Run: `pip install -r requirements.txt`, then `python -m backend.run` from the
repository root (port 3001, auto-reload when `ENVIRONMENT=dev`). Swagger: `/docs`.
Redis must be reachable — the app exits at startup if it is not.

Check: `pytest backend/tests` (no server or database needed — see
`tests/CLAUDE.md`), `ruff check backend/`, `ruff format backend/`.

## ⚠️ SETUP REQUIRED (blocking — nothing DB-backed works until done)

The original Supabase project (`bbwoasmiqxuasjokmrpe.supabase.co`) was **deleted**
— its DNS no longer resolves. To get running:

1. Create a new project at supabase.com
2. Update `.env`: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`
   (Project Settings → API / JWT)
3. Set `DATABASE_URL` in `.env` (Project Settings → Database) and apply the
   migrations from the repository root:
   `python -m backend.scripts.migrate up` (`status` first to see what is pending).
   There are seven, applied in filename order:
   - `..._initial_schema.sql` — domains, users, RLS
   - `..._remaining_tables.sql` — companies, questions, reviews, upvotes, flags, applications, prep_progress
   - `..._upvote_functions.sql` — the original counter RPCs, superseded but kept
   - `..._admin_audit_log.sql` — audit log and the suspension mirror
   - `..._company_admins.sql` — per-company managers and profile edit requests
   - `..._atomic_rpcs.sql` — the atomic write functions the backend calls
   - `..._indexes.sql` — indexes for the queries the API runs
   `supabase db push` also works; run `migrate baseline` afterwards so the tracking
   table matches.
4. Supabase Auth → URL Configuration: add `http://localhost:5173/reset-password`
   as a redirect URL (password recovery)
5. Optional keys in `.env`:
   - `SMTP_PASS` — Resend API key (email notifications; currently unused, see below)
   - `GEMINI_API_KEY` — aistudio.google.com (required for `/resume/analyze`)
6. First super admin: register a user, then in SQL editor:
   `UPDATE public.users SET role = 'super_admin' WHERE email = '...';`
   and mirror it: `select auth.uid()` metadata via
   `PATCH /admin/users/:id/role` afterwards handles others.

Redis must also be reachable (`docker compose up redis`, or set `REDIS_HOST`):
the app exits at startup if it is not.

## Implemented

Auth (register/login/logout/forgot/reset, email verification), onboarding,
questions (submit/list/filter/upvote/flag), reviews, companies (user-submitted,
admin-approved), applications tracker, prep roadmaps + preparedness score
(`/prep`), AI resume analyzer (Gemini 2.0 Flash), admin moderation queue,
user/role management, rate limiting, JWT verification (HS256 + JWKS).

## Remaining (PRD features not yet built)

- **Email notifications** — there is no email service any more. The old
  `email_service.py` was never called by anything, so it was dropped rather than
  carried over; wire notifications into `moderation_service.moderate` and
  `company_admin_service.decide_edit` when they are built, and add a deadline
  reminder job.
- **Admin analytics dashboard** (PRD 5.3.6) — no endpoint for submissions/day,
  approval rates, top contributors.
- **Timed suspensions** (PRD 5.3.4) — `user_admin_service.suspend` is a permanent
  ban (`PERMANENT_BAN_DURATION`); no 1/7/30-day options. Unsuspend exists. `warn`
  records to the audit log but delivers nothing until notifications are wired.
- **Company management** (PRD 5.3.5) — no verified badge. Pending companies
  appear in `/admin/queue`; admin create/edit/merge and per-company managers
  are done. Logo is a URL field, not an upload (no Supabase Storage yet).
- **Question resubmission** — `needs_edit` status exists and RLS allows the
  submitter to update, but there's no API endpoint to edit + resubmit
  (`UpdateQuestionParam` exists unused in `app/career/schema/question.py`).
- **Keyword search** on questions (PRD 5.2.3) — filters exist, no text search.
- **Roadmaps in DB** — prep topics are a static dict in
  `app/career/service/prep_service.py` (`ponytail:` comment there); move to an
  admin-curated table when content needs editing without a deploy.
- **Google OAuth** (PRD 5.1.1) — email/password only today.
- **Phase 2**: AI mock interview (Anthropic API), mentorship, leaderboard,
  curated internship listings, Supabase Realtime queue updates.
- **Tests** — `tests/` covers the API surface (103 tests) against an in-memory
  Supabase. Not covered: token verification itself (the tests override the auth
  dependency), the Gemini call in `resume_service`, and the Redis-backed caches.
