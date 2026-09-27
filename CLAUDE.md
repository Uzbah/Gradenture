# CareerBridge (Gradenture) — repo root

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

Monorepo for CareerBridge: interview prep + job-application tracker for students in Pakistan/South Asia. Three parts, each with its own CLAUDE.md:

| Folder | What lives there | Read next |
|--------|------------------|-----------|
| `backend/` | FastAPI API (`/api/v1`), serves the built frontend in prod | `backend/CLAUDE.md` |
| `frontend/` | React 18 + Vite + TypeScript SPA | `frontend/CLAUDE.md` |
| `supabase/` | SQL migrations = the schema and RLS source of truth | `supabase/CLAUDE.md` |

## Files in this folder

- `README.md` — human setup guide (Supabase project, env vars, run, Docker). Keep it and this file in sync.
- `Dockerfile` — production image: builds `frontend/dist`, bakes it into the backend image, one container on port 3001.
- `docker-compose.yml` — dev stack: backend (uvicorn --reload) + frontend (Vite HMR), source bind-mounted. Supabase is hosted, not a container.
- `.dockerignore` — excludes `.env`, `node_modules`, venvs, `dist`, `supabase/` from the prod build context.
- `.gitignore` — `.env*`, deps, build output, `*.tsbuildinfo`.

## Invariants (never break)

- Nothing user-submitted is public until an admin approves it (`pending → approved | rejected | needs_edit`).
- The backend uses the Supabase **service-role** key, so RLS is bypassed for API calls; every authorization check lives in `backend/src`. The RLS policies still matter the day a browser client (supabase-js / anon key) is introduced.
- Secrets only in `backend/.env` / `frontend/.env` (gitignored, dockerignored). Never commit them.

## Status

The original Supabase project was deleted; a new one must be created and the migrations applied before anything DB-backed works (see README). No automated test suite yet; three smoke scripts in `backend/` run against a live dev server.
