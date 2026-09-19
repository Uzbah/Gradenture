# CareerBridge (Gradenture)

Interview prep and job application platform for university students and fresh graduates in Pakistan/South Asia.

## Stack

- **Backend:** FastAPI + Python, laid out on
  [fastapi-best-architecture](https://github.com/fastapi-practices/fastapi-best-architecture)
  lines — `api → service → crud`, a unified `{code, msg, data}` response, an app
  factory. See [backend/CLAUDE.md](backend/CLAUDE.md).
- **Frontend:** React 18 + Vite + TypeScript (plain CSS, no UI framework)
- **Database:** Supabase (Postgres + Auth), reached through PostgREST — no ORM
- **Cache:** Redis (ban state, JWKS, rate limits)
- **AI:** Gemini 2.0 Flash (resume analyzer)

## ⚠️ Before anything: Supabase setup

The original Supabase project was deleted, so a new one must be created before
any DB-backed feature works:

1. Create a project at [supabase.com](https://supabase.com)
2. Fill in `backend/.env` (including `DATABASE_URL`) and `frontend/.env` (keys below)
3. Apply the migrations from the repo root:
   ```bash
   python -m backend.scripts.migrate status   # what this database is missing
   python -m backend.scripts.migrate up       # apply it
   ```
   `supabase db push` also works; follow it with `migrate baseline` so the
   tracking table matches.
4. Auth → URL Configuration: add `http://localhost:5173/reset-password` as a redirect URL
5. Create your first super admin — register through the app, then in the SQL editor:
   ```sql
   UPDATE public.users SET role = 'super_admin' WHERE email = 'you@example.com';
   ```

## Backend setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

Copy `backend/.env.example` to `backend/.env` and fill in:

```
SUPABASE_URL=                # Project Settings → API
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWT_SECRET=         # Project Settings → API → JWT
DATABASE_URL=                # Project Settings → Database (migrations only)
GEMINI_API_KEY=              # aistudio.google.com (required for resume analyzer)
```

Redis has to be running — the app exits at startup if it cannot reach one
(`docker compose up redis`, or a local `redis-server`).

Run it **from the repository root**, not from `backend/`: `backend` is the
importable package.

```powershell
python -m backend.run
```

- API: http://localhost:3001/api/v1
- Swagger UI: http://localhost:3001/docs

Tests and linting (no server or database needed):

```powershell
pytest backend/tests
ruff check backend/
ruff format backend/
```

## Frontend setup

```powershell
cd frontend
npm install
```

Copy `.env.example` to `.env` and fill in:

```
VITE_SUPABASE_URL=           # currently unused by code, kept for future OAuth/Realtime
VITE_SUPABASE_ANON_KEY=      # currently unused
VITE_API_BASE_URL=http://localhost:3001/api/v1
```

```powershell
npm run dev    # http://localhost:5173
```

## Serving frontend from backend (prod)

```powershell
cd frontend; npm run build
cd ..; python -m backend.run   # serves both on :3001
```

`frontend/dist` is auto-detected — if present, FastAPI serves it at `/`. No CORS needed in prod
(`.env.production` sets `VITE_API_BASE_URL=/api/v1`).

## Docker

Supabase is a hosted service, not a container here — you still need a Supabase
project and `backend/.env` / `frontend/.env` filled in (see above) before
running either of these.

### Development (hot reload, two containers)

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:3001/api/v1 (Swagger at `/docs`)

Source is bind-mounted into both containers, so edits on your host are picked
up live (Vite HMR, uvicorn `--reload`). Re-run with `--build` whenever
`requirements.txt` or `package.json` changes; otherwise plain `docker compose up`
is enough. Stop with `docker compose down`.

### Production (single container)

The root `Dockerfile` multi-stage builds the frontend and bakes the static
files into the backend image, matching the "serving frontend from backend"
setup above — one container, one process, port 3001:

```bash
docker build -t gradenture .
docker run -p 3001:3001 --env-file backend/.env gradenture
```

## Features

- **Auth & onboarding** — email/password + verification, forgot/reset password, domain/skill/goal/university wizard
- **Community intel** — crowd-sourced interview questions and company reviews, filterable by domain/company/difficulty/type, upvotes, flagging, anonymous submissions; everything gated behind admin moderation
- **Opportunity tracker** — 5-column kanban (Applied / Interview / Offer / Rejected / Closed)
- **Interview prep** — per-domain topic roadmaps with a preparedness score (progress ring)
- **AI resume analyzer** — PDF/DOCX upload + optional job description → score, strengths, weaknesses, keyword gaps (3/hr)
- **Admin panel** — moderation queue (approve / reject / request edit), user management, role assignment (super admin)

Remaining work and known gaps are tracked in [backend/CLAUDE.md](backend/CLAUDE.md) and
[frontend/CLAUDE.md](frontend/CLAUDE.md).

## Project layout

Every backend folder carries its own `CLAUDE.md` listing the files inside it.

```
backend/                     # the importable package — run from the repo root
├── main.py                  # app = register_app()
├── run.py                   # python -m backend.run
├── CLAUDE.md                # layering rules, conventions, remaining work
├── app/
│   ├── admin/               # auth, own profile, moderation, admin operations
│   └── career/              # questions, reviews, companies, applications, prep, resume
│       ├── api/v1/          # routes — thin, typed, no DB access
│       ├── service/         # business rules
│       ├── crud/            # PostgREST queries
│       └── schema/          # pydantic models
├── common/                  # response envelope, errors, pagination, security, enums
├── core/                    # settings, paths, register_app()
├── database/                # supabase + redis clients
├── middleware/              # trace id, access log
├── utils/                   # sanitize, limiter, trace id, openapi
├── scripts/migrate.py       # migration runner
└── tests/                   # pytest + httpx, against an in-memory Supabase
frontend/
├── CLAUDE.md                # conventions + remaining frontend work
├── src/
│   ├── App.tsx              # Routes, nav, auth/onboarding guards
│   ├── api.ts               # Fetch wrapper + shared types
│   ├── auth.tsx             # Auth context
│   ├── lookups.ts           # Domain/company id→name lookups
│   ├── index.css            # All styling
│   └── pages/               # One file per route
└── .env.production          # VITE_API_BASE_URL=/api/v1 (used on npm run build)
supabase/migrations/         # SQL migrations (7 files, applied by scripts/migrate.py)
```

## API endpoints

Every response is `{ code, msg, data }`. List endpoints put a page in `data`:
`{ items, total, page, size, total_pages }`, taking `page` and `size` (max 50).

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/register` | — | Register |
| POST | `/api/v1/auth/login` | — | Login |
| POST | `/api/v1/auth/forgot-password` | — | Send reset email |
| POST | `/api/v1/auth/reset-password` | JWT | Set new password |
| GET | `/api/v1/users/me` | JWT | Current user |
| PATCH | `/api/v1/users/onboarding` | JWT | Complete onboarding |
| GET | `/api/v1/domains` | — | List domains |
| GET | `/api/v1/questions` | — | List approved questions (filters) |
| POST | `/api/v1/questions` | JWT | Submit question (5/hr) |
| POST | `/api/v1/questions/:id/upvote` | JWT | Toggle upvote |
| POST | `/api/v1/questions/:id/flag` | JWT | Flag question |
| GET | `/api/v1/reviews` | — | List approved reviews |
| POST | `/api/v1/reviews` | JWT | Submit review (5/hr) |
| POST | `/api/v1/reviews/:id/flag` | JWT | Flag review |
| GET | `/api/v1/companies` | — | List approved companies |
| POST | `/api/v1/companies` | JWT | Submit company (pending) |
| GET/POST | `/api/v1/applications` | JWT | List / create applications |
| PATCH/DELETE | `/api/v1/applications/:id` | JWT | Update / delete application |
| GET | `/api/v1/prep` | JWT | Prep topics + preparedness score |
| PATCH | `/api/v1/prep` | JWT | Toggle topic completion |
| POST | `/api/v1/resume/analyze` | JWT | AI resume analysis (3/hr) |
| GET | `/api/v1/admin/queue` | Admin | Moderation queue |
| PATCH | `/api/v1/admin/questions/:id` | Admin | Moderate question |
| PATCH | `/api/v1/admin/reviews/:id` | Admin | Moderate review |
| PATCH | `/api/v1/admin/companies/:id` | Admin | Approve company |
| GET | `/api/v1/admin/users` | Admin | List users |
| PATCH | `/api/v1/admin/users/:id/role` | Super admin | Update role |
| PATCH | `/api/v1/admin/users/:id/suspend` | Admin | Suspend user |
| POST | `/api/v1/admin/companies/:id/merge` | Admin | Merge a duplicate company |
| GET/PATCH | `/api/v1/admin/flags`, `/api/v1/admin/flags/:id` | Admin | List / close content flags |
| GET/PATCH | `/api/v1/admin/company-edits` | Admin | Manager-proposed profile edits |

The full surface is 51 routes; `/docs` has all of them.
