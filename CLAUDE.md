# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

CareerBridge (Gradenture) — interview prep and job application platform for
university students and fresh graduates in Pakistan/South Asia. FastAPI +
Python backend, React 18 + Vite + TypeScript frontend (plain CSS, no UI
framework), Supabase (Postgres + Auth) database, Gemini 2.0 Flash for the
resume analyzer.

Detailed per-side conventions and known gaps live in `backend/CLAUDE.md` and
`frontend/CLAUDE.md` — read the relevant one before working in that
directory. This file covers only what spans both.

## ⚠️ Supabase must be (re)created before anything DB-backed works

The original Supabase project was deleted and its DNS no longer resolves.
Setup, in order:

1. Create a project at supabase.com
2. Run the 3 migrations in `supabase/migrations/` in order (`supabase db push`,
   or paste into the SQL editor) — schema/RLS, then remaining tables, then the
   upvote RPCs
3. Fill in `backend/.env` (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`,
   `SUPABASE_JWT_SECRET`, `GEMINI_API_KEY`) and `frontend/.env`
   (`VITE_API_BASE_URL`)
4. Supabase Auth → URL Configuration: add `http://localhost:5173/reset-password`
   as a redirect URL
5. Register a user through the app, then promote it in the SQL editor:
   `UPDATE public.users SET role = 'super_admin' WHERE email = '...';`

## Commands

Backend (from `backend/`):
```
pip install -r requirements.txt
python main.py                # runs on :3001, Swagger at /docs
```

Frontend (from `frontend/`):
```
npm install
npm run dev                   # :5173
npm run build                 # tsc -b && vite build -> dist/
npm run preview
```

There is no lint or test tooling configured on either side, and no test
files exist yet.

Production: build the frontend first, then run the backend from `backend/`
— `main.py` auto-detects `frontend/dist` and serves it at `/`, so a single
`python main.py` serves both API and UI with no CORS needed
(`frontend/.env.production` sets `VITE_API_BASE_URL=/api/v1` for this case).

## Architecture

**Backend is a strict layered stack**: `routers/` (thin HTTP handlers) →
`services/` (business logic + all Supabase queries) → `config/supabase.py`
(single client, service-role key). Routers never touch the DB directly.
Every response body is `{"data": ...}` or `{"message": ...}`; errors raise
`AppError(status, {"error": msg})` (see `dependencies/exceptions.py`);
user-submitted text is passed through `utils/sanitize.py::clean_text()`
before insert. Auth is JWT-based (`dependencies/auth.py`, HS256 + JWKS) —
Supabase Auth issues the tokens but the frontend never talks to Supabase
directly.

**Frontend talks only to the FastAPI backend**, never to Supabase directly —
`supabase-js` is not used; auth flows go through the API, and the
password-recovery token is read from the URL hash in `ResetPassword.tsx`.
`src/api.ts` is the single fetch wrapper (Bearer token from localStorage,
error-message flattening, auto-logout on 401) and holds the shared TS
types. `src/auth.tsx` is the only piece of app-wide state (React context);
otherwise each route in `src/pages/` is a self-contained file with its
forms inlined — there is no state management library and no UI framework,
just `src/index.css`.

**Data model / moderation flow**: user-submitted content (questions,
reviews, companies) lands in a pending state and is invisible to other
users until an admin approves it via `/admin/queue`
(`admin_service.moderate_*`); rejection/edit-request emails are stubbed
(`services/email_service.py` exists but isn't wired up — see
`backend/CLAUDE.md`). Roles (`user` / `admin` / `super_admin`) gate the
admin endpoints and the frontend Admin page.

**Migrations** (`supabase/migrations/`, run in order): initial schema +
RLS → remaining tables (companies, questions, reviews, upvotes, flags,
applications, prep_progress) → upvote increment/decrement RPCs.
