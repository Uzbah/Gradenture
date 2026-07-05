# CareerBridge Backend — CLAUDE.md

FastAPI + Supabase (Postgres) backend. Entry point `main.py`, serves the API at
`/api/v1` and the built frontend (`../frontend/dist`) at `/` when it exists.

## Layout

```
main.py                 # FastAPI app, CORS, exception handlers, static mount
src/
├── routers/            # HTTP routes (thin — delegate to services)
├── services/           # Business logic + Supabase queries
├── schemas/            # Pydantic request models
├── dependencies/       # auth.py (JWT), rate_limit.py, exceptions.py
├── config/supabase.py  # Supabase client (service role key)
└── utils/sanitize.py   # bleach wrapper
```

Conventions: routers never touch the DB directly; all responses are
`{"data": ...}` or `{"message": ...}`; errors raise `AppError(status, {"error": msg})`;
user-submitted text goes through `clean_text()` before insert.

## ⚠️ SETUP REQUIRED (blocking — nothing DB-backed works until done)

The original Supabase project (`bbwoasmiqxuasjokmrpe.supabase.co`) was **deleted**
— its DNS no longer resolves. To get running:

1. Create a new project at supabase.com
2. Update `.env`: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`
   (Project Settings → API / JWT)
3. Run all 3 migrations in `../supabase/migrations/` in order
   (`supabase db push` or paste into the SQL editor):
   - `..._initial_schema.sql` — domains, users, RLS
   - `..._remaining_tables.sql` — companies, questions, reviews, upvotes, flags, applications, prep_progress
   - `..._upvote_functions.sql` — `increment_upvotes` / `decrement_upvotes` RPCs
4. Supabase Auth → URL Configuration: add `http://localhost:5173/reset-password`
   as a redirect URL (password recovery)
5. Optional keys in `.env`:
   - `SMTP_PASS` — Resend API key (email notifications; currently unused, see below)
   - `GEMINI_API_KEY` — aistudio.google.com (required for `/resume/analyze`)
6. First super admin: register a user, then in SQL editor:
   `UPDATE public.users SET role = 'super_admin' WHERE email = '...';`
   and mirror it: `select auth.uid()` metadata via
   `PATCH /admin/users/:id/role` afterwards handles others.

Run: `pip install -r requirements.txt` then `python main.py` (port 3001,
auto-reload when `NODE_ENV=development`). Swagger: `/docs`.

## Implemented

Auth (register/login/logout/forgot/reset, email verification), onboarding,
questions (submit/list/filter/upvote/flag), reviews, companies (user-submitted,
admin-approved), applications tracker, prep roadmaps + preparedness score
(`/prep`), AI resume analyzer (Gemini 2.0 Flash), admin moderation queue,
user/role management, rate limiting, JWT verification (HS256 + JWKS).

## Remaining (PRD features not yet built)

- **Email notifications** — `email_service.py` exists but is NOT called on
  moderation decisions (approve/reject/needs_edit) or deadline reminders.
  Wire it into `admin_service.moderate_*` and add a reminder job.
- **Admin analytics dashboard** (PRD 5.3.6) — no endpoint for submissions/day,
  approval rates, top contributors.
- **Timed suspensions** (PRD 5.3.4) — `suspend_user` is a permanent ban
  (`876600h`); no 1/7/30-day options, no unsuspend endpoint. `warn_user` is a
  no-op stub (checks the user exists, sends nothing).
- **Company management** (PRD 5.3.5) — no merge-duplicates, no verified badge;
  pending companies are not surfaced in `/admin/queue` (approve endpoint exists
  but nothing lists them).
- **Flagged content review** (PRD 5.3.3) — flags are inserted into
  `content_flags` but there is no admin endpoint to list/resolve/dismiss them.
- **Question resubmission** — `needs_edit` status exists and RLS allows the
  submitter to update, but there's no API endpoint to edit + resubmit
  (`QuestionEditSchema` exists unused in `question_schema.py`).
- **Keyword search** on questions (PRD 5.2.3) — filters exist, no text search.
- **Roadmaps in DB** — prep topics are a static dict in
  `services/prep_service.py` (`ponytail:` comment there); move to an
  admin-curated table when content needs editing without a deploy.
- **Google OAuth** (PRD 5.1.1) — email/password only today.
- **Phase 2**: AI mock interview (Anthropic API), mentorship, leaderboard,
  curated internship listings, Supabase Realtime queue updates.
- **Tests** — there are none.
