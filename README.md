# Gradenture

Interview prep and job application platform for university students and fresh graduates in Pakistan/South Asia.

## Stack

- **Backend:** FastAPI + Python
- **Frontend:** React 18 + Vite + TypeScript (plain CSS, no UI framework)
- **Database:** Supabase (Postgres + Auth)
- **AI:** Gemini via `google-genai` (resume analyzer; model set by `GEMINI_MODEL`, default `gemini-3.6-flash`)

## ⚠️ Before anything: Supabase setup

The original Supabase project was deleted, so a new one must be created before
any DB-backed feature works:

1. Create a project at [supabase.com](https://supabase.com)
2. Run all migrations in `supabase/migrations/` in filename order (`supabase db push`, or paste into the SQL editor)
3. Fill in `backend/.env` and `frontend/.env` (keys below)
4. Auth → URL Configuration: add `http://localhost:5173/reset-password` (or `<APP_URL>/reset-password` in prod) as a redirect URL
5. Create your first super admin — register through the app, then in the SQL editor:
   ```sql
   UPDATE public.users SET role = 'super_admin' WHERE email = 'you@example.com';
   ```

> Free-tier Supabase projects **pause after 7 days without activity**. If the
> app suddenly can't reach the database (DNS errors, `getaddrinfo failed`), open
> the Supabase dashboard and click **Restore project**.

## 🚀 Quick start: run everything with one command

Needs [Docker Desktop](https://www.docker.com/products/docker-desktop/) running,
plus `backend/.env` and `frontend/.env` filled in (copy each folder's
`.env.example`, see the setup sections below for the keys).

```powershell
docker compose up --build
```

| What | URL |
|------|-----|
| App (frontend) | http://localhost:5173 |
| API | http://localhost:3001/api/v1 |
| API docs (Swagger) | http://localhost:3001/docs |

- **Edits reload live**: the source folders are mounted into the containers, so
  saving a file restarts the backend / hot-reloads the page. No rebuild needed.
- **Rebuild only when dependencies change**: use `--build` after editing
  `backend/requirements.txt` or `frontend/package.json`; otherwise plain
  `docker compose up` starts in seconds.
- **Run in the background**: `docker compose up -d`, then `docker compose logs -f`
  to watch output.
- **Stop**: `Ctrl+C` (or `docker compose down` if started with `-d`).
- **"Port is already allocated"**: a backend or frontend you started by hand is
  still running. Stop it (`netstat -ano | findstr ":3001 :5173"` shows the PID).

Prefer running without Docker? Follow the two setup sections below and use two
terminals: one for the backend, one for the frontend.

## Backend setup

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in:

```
SUPABASE_URL=                # Project Settings → API
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWT_SECRET=         # Project Settings → API → JWT
APP_URL=http://localhost:5173  # frontend origin; password-reset emails link to $APP_URL/reset-password
SMTP_PASS=                   # Resend API key (optional — emails are skipped until set)
GEMINI_API_KEY=              # aistudio.google.com (required for resume analyzer)
GEMINI_MODEL=                # optional, default gemini-3.6-flash
FORWARDED_ALLOW_IPS=         # optional: reverse-proxy IP(s), so rate limits see real client IPs
```

```powershell
python main.py
```

- API: http://localhost:3001/api/v1
- Swagger UI: http://localhost:3001/docs
- Offline checks (no server/DB): `python check_validation.py`

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
cd ..\backend; python main.py   # serves both on :3001
```

`frontend/dist` is auto-detected — if present, FastAPI serves it at `/`. No CORS needed in prod
(`frontend/.env.production`, committed, sets `VITE_API_BASE_URL=/api/v1`).
Set `APP_URL` in `backend/.env` to the public origin so password-reset links land on it.

## Docker

Supabase is a hosted service, not a container here — you still need a Supabase
project and `backend/.env` / `frontend/.env` filled in (see above) before
running either of these.

### Development (hot reload, two containers)

`docker-compose.yml` is the one-command dev stack described in
[Quick start](#-quick-start-run-everything-with-one-command). Details:

- The frontend waits for the backend's health check (`/api/v1` answering)
  before it starts.
- File watching uses polling (`WATCHFILES_FORCE_POLLING`, `CHOKIDAR_USEPOLLING`)
  because Windows bind mounts don't forward file-change events into containers;
  without it, hot reload silently stops working.
- The containers keep their own Linux `node_modules` and Python packages;
  your Windows `node_modules` and `.venv` are hidden from them (and keeping
  `.venv` out cuts the backend's file polling from ~9k files to ~140).

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

```
backend/
├── main.py                  # FastAPI entry point + static file mount
├── requirements.txt
├── CLAUDE.md                # conventions + remaining backend work
└── src/
    ├── routers/             # HTTP routes (thin)
    ├── services/            # Business logic + Supabase queries
    ├── dependencies/        # Auth (JWT), rate limiting, exceptions
    ├── schemas/             # Pydantic models
    ├── config/              # Supabase client
    └── utils/               # Sanitization
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
supabase/migrations/         # SQL migrations (run in filename order)
```

## API endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/register` | — | Register |
| POST | `/api/v1/auth/login` | — | Login |
| POST | `/api/v1/auth/forgot-password` | — | Send reset email |
| POST | `/api/v1/auth/reset-password` | JWT | Set new password (`current_password` required unless using a recovery link) |
| POST | `/api/v1/auth/refresh` | — | Swap refresh token for a new session |
| GET | `/api/v1/users/me` | JWT | Current user |
| GET | `/api/v1/users/me/submissions` | JWT | Own questions + reviews, all statuses |
| PATCH | `/api/v1/users/onboarding` | JWT | Complete onboarding |
| GET | `/api/v1/domains` | — | List domains |
| GET | `/api/v1/questions` | — | List approved questions (filters) |
| POST | `/api/v1/questions` | JWT | Submit question (5/hr) |
| POST | `/api/v1/questions/:id/upvote` | JWT | Toggle upvote, approved only (60/hr) |
| PATCH | `/api/v1/questions/:id` | JWT (owner) | Edit + resubmit a `needs_edit` question |
| POST | `/api/v1/questions/:id/flag` | JWT | Flag question |
| GET | `/api/v1/reviews` | — | List approved reviews |
| POST | `/api/v1/reviews` | JWT | Submit review (5/hr) |
| PATCH | `/api/v1/reviews/:id` | JWT (owner) | Edit + resubmit a `needs_edit` review |
| POST | `/api/v1/reviews/:id/flag` | JWT | Flag review |
| GET | `/api/v1/companies` | — | List approved companies |
| POST | `/api/v1/companies` | JWT | Submit company (pending, 5/hr) |
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
| PATCH | `/api/v1/admin/users/:id/suspend` | Admin (super admin for admin targets) | Suspend user |
