CLAUDE.md — CareerBridge
This file is the source of truth for AI-assisted development on CareerBridge. Read it fully before writing any code, creating any file, or making any architectural decision.

Project Overview
CareerBridge is a web platform for university students and fresh graduates in Pakistan/South Asia. It provides:

Moderated community interview questions and company reviews
Domain-specific interview preparation (roadmaps + question bank)
A personal job application tracker (Kanban)
Admin moderation panel
Production domain: careerbridge.pk
API base URL (prod): https://api.careerbridge.pk/api/v1
API base URL (dev): http://localhost:3001/api/v1


Monorepo Layout
careerbridge/
├── backend/
│   ├── main.py                     ← FastAPI entry point
│   ├── requirements.txt
│   ├── .env                        ← never commit
│   └── src/
│       ├── config/
│       │   └── supabase.py
│       ├── dependencies/
│       │   ├── auth.py             ← get_current_user, require_admin
│       │   ├── rate_limit.py       ← slowapi limiter
│       │   └── exceptions.py
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── users.py
│       │   ├── questions.py
│       │   ├── reviews.py
│       │   ├── companies.py
│       │   ├── applications.py
│       │   └── admin.py
│       ├── services/
│       │   ├── auth_service.py
│       │   ├── auth_helpers.py
│       │   ├── users_service.py
│       │   ├── questions_service.py
│       │   ├── reviews_service.py
│       │   ├── companies_service.py
│       │   ├── applications_service.py
│       │   ├── admin_service.py
│       │   └── email_service.py
│       ├── schemas/
│       │   ├── auth_schema.py
│       │   ├── question_schema.py
│       │   ├── review_schema.py
│       │   ├── application_schema.py
│       │   ├── company_schema.py
│       │   ├── user.py
│       │   └── admin_schema.py
│       └── utils/
│           └── sanitize.py
└── frontend/
    ├── vite.config.ts
    ├── tsconfig.json
    ├── package.json
    ├── .env                        ← never commit
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── pages/
        │   ├── LandingPage.tsx
        │   ├── Dashboard.tsx
        │   ├── ProfilePage.tsx
        │   ├── auth/
        │   │   ├── Login.tsx
        │   │   ├── Register.tsx
        │   │   └── Verify.tsx
        │   ├── onboarding/
        │   │   ├── OnboardingFlow.tsx
        │   │   └── steps/
        │   │       ├── Step1Domain.tsx
        │   │       ├── Step2SkillLevel.tsx
        │   │       ├── Step3Goal.tsx
        │   │       └── Step4University.tsx
        │   ├── community/
        │   │   ├── CommunityIndex.tsx
        │   │   ├── CompanyProfile.tsx
        │   │   ├── DomainPage.tsx
        │   │   ├── SubmitQuestion.tsx
        │   │   └── SubmitReview.tsx
        │   ├── prep/
        │   │   ├── PrepHome.tsx
        │   │   └── DomainRoadmap.tsx
        │   ├── tracker/
        │   │   ├── OpportunityTracker.tsx
        │   │   └── ApplicationDetail.tsx
        │   └── admin/
        │       ├── AdminDashboard.tsx
        │       ├── ModerationQueue.tsx
        │       ├── UserManagement.tsx
        │       └── AdminAnalytics.tsx
        ├── components/
        │   ├── ui/
        │   ├── layout/
        │   └── forms/
        ├── hooks/
        │   ├── useAuth.ts
        │   ├── useQuestions.ts
        │   └── useApplications.ts
        ├── stores/
        │   ├── authStore.ts
        │   └── uiStore.ts
        ├── lib/
        │   ├── supabase.ts
        │   └── api.ts
        ├── schemas/
        └── types/
            └── index.ts

Technology Stack
Backend
PackageVersionPurposePython3.10+RuntimeFastAPI0.115+REST API frameworkUvicorn0.34+ASGI serverPydanticv2Request validation & serializationsupabase-py2.xDB operationsPyJWT2.xJWT verificationslowapi0.1+Rate limitingpython-dotenv1.xEnvironment variables
Frontend
PackageVersionPurposeReact18+UIVitelatestBuild toolTypeScript5.xType safetyTanStack Queryv5Server state / cachingZustandv4Client UI stateTailwind CSSv3StylingReact Routerv6RoutingZodv3Form validation@hello-pangea/dndlatestKanban drag & drop
Infrastructure
ServicePurposeSupabase (Postgres 15)Primary DB, Auth, Storage, RealtimeVercelFrontend hostingRailwayBackend API hostingGitHub ActionsCI/CD

Architecture Rules — Read Before Writing Any Code
Read vs Write Split
This is the most important architectural rule.

React → Supabase directly (anon client): read-only, non-sensitive queries — listing approved questions, browsing companies, domain pages.
React → FastAPI (with JWT): ALL writes, ALL mutations, sensitive reads — submitting questions, moderation, application tracking, profile updates.

Never write directly to Supabase from React for mutations. Never proxy a simple public read through the API unnecessarily.
Authentication Flow

Supabase Auth issues a JWT on login (handled client-side by supabase-js).
JWT is stored in Zustand authStore + localStorage.
Every API request includes Authorization: Bearer <jwt> header.
FastAPI get_current_user dependency verifies the token using SUPABASE_JWT_SECRET (HS256) or JWKS (ES256).
Admin routes additionally use require_admin / require_super_admin which check public.users.role.

The API does not issue JWTs — only Supabase does. The API only verifies them.
Role System
Roles live in two places and must match:

auth.users.user_metadata.role (Supabase Auth metadata)
public.users.role (application DB)

Valid roles: user | admin | super_admin
Only super_admin can assign/revoke admin roles (POST /admin/users/:id/role).

Backend Conventions
Router → Service Pattern

Routers (routers/*.py): define path + HTTP method, attach Depends() for auth/validation, call service. No business logic.
Services (services/*_service.py): business logic and Supabase calls. Raise AppError for HTTP errors.
Dependencies (dependencies/*.py): get_current_user, require_admin, rate limiting.

python# routers/questions.py
from fastapi import APIRouter, Depends
from src.dependencies.auth import get_current_user
from src.schemas.question_schema import QuestionSchema
from src.services import questions_service

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.post("/", status_code=201)
def submit_question(body: QuestionSchema, user: dict = Depends(get_current_user)):
    return questions_service.submit_question(user, body)
python# services/questions_service.py
from src.config.supabase import supabase
from src.dependencies.exceptions import AppError

def submit_question(user: dict, data: QuestionSchema) -> dict:
    result = supabase.table("interview_questions").insert({
        **data.model_dump(),
        "submitted_by": user["sub"],
        "status": "pending",
    }).execute()
    return {"id": result.data[0]["id"], "status": "pending", "message": "Submitted for review"}
Dependency Order (authenticated + validated routes)
python@router.post("/path")
@limiter.limit("5/hour", key_func=user_rate_key)   # if rate-limited
def handler(
    request: Request,
    body: SomeSchema,                              # Pydantic validates body → 400
    user: dict = Depends(get_current_user),        # JWT auth → 401/403
):
    return some_service.action(user, body)
Pydantic Validation
All POST/PATCH payloads are validated server-side using Pydantic v2 models passed as route parameters. A global exception handler maps RequestValidationError to 400 with `{ "errors": { "field": ["msg"] } }`.
Pydantic Schemas (schemas/)
python# schemas/question_schema.py
from pydantic import BaseModel, field_validator
from typing import Literal
import re

class QuestionSchema(BaseModel):
    domain_id: str
    company_id: str
    role_title: str
    question_text: str
    question_type: Literal['technical', 'behavioural', 'hr', 'case_study']
    difficulty: Literal['easy', 'medium', 'hard']
    asked_date: str
    notes: str | None = None
    is_anonymous: bool = False

    @field_validator('question_text')
    @classmethod
    def validate_question_text(cls, v):
        if len(v) < 20:
            raise ValueError('Must be at least 20 characters')
        return v

    @field_validator('asked_date')
    @classmethod
    def validate_asked_date(cls, v):
        if not re.match(r'^\d{4}-\d{2}-01$', v):
            raise ValueError('Must be YYYY-MM-01')
        return v
Error Handling
Services raise AppError(status_code, body) for expected HTTP errors. Unhandled exceptions are caught by a global handler in main.py returning `{ "error": "Internal server error" }` with 500.
python# main.py
@app.exception_handler(AppError)
async def app_error_handler(_request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content=exc.body)

@app.exception_handler(Exception)
async def unhandled_exception_handler(_request, exc: Exception):
    logger.exception(exc)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})
App Entry Point (main.py)
python# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import api_router

app = FastAPI(title="CareerBridge API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], ...)
app.include_router(api_router)   # prefix /api/v1, includes all sub-routers
Supabase Client in Backend
Use the service role key in the backend — it bypasses RLS. This is correct and intentional because the API enforces authorization through dependencies, not RLS.
python# config/supabase.py
import os
from supabase import create_client, Client

supabase: Client = create_client(
    os.environ['SUPABASE_URL'],
    os.environ['SUPABASE_SERVICE_ROLE_KEY']
)
Rate Limiting
Apply to these routes only:

POST /questions, POST /reviews: 5 per user per hour
POST /*/flag: 10 per user per hour
Global: 100 requests/min/IP

Use slowapi. Config in dependencies/rate_limit.py.
python# dependencies/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
Apply per-route:
python@router.post("/")
@limiter.limit("5/hour", key_func=user_rate_key)
def submit_question(request: Request, body: QuestionSchema, user: dict = Depends(get_current_user)):
    return questions_service.submit_question(user, body)
Input Sanitization
Strip HTML from all text fields before inserting to DB. Use bleach or a simple regex. This prevents XSS in rendered content.
pythonimport re

def clean(text: str) -> str:
    return re.sub(r'<[^>]*>', '', text)
Apply to: question_text, review_text, notes, admin_note.

Frontend Conventions
API Client (lib/api.ts)
Single Axios (or fetch) instance that auto-attaches the JWT from Zustand store:
ts// lib/api.ts
const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL });
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().session?.access_token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
export default api;
Never call axios.post(...) directly from a component. Always use api.post(...).
Supabase Client (lib/supabase.ts)
Uses the anon key. For direct reads from React only:
tsimport { createClient } from '@supabase/supabase-js';
export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);
State Management Rules
State typeToolAuth session, user object, roleZustand authStoreUI state (sidebar, modals, filters)Zustand uiStoreServer data (questions, reviews, etc.)TanStack QueryForm stateReact Hook Form + Zod
Do not put server data in Zustand. Do not put UI state in TanStack Query.
TanStack Query Keys
tsexport const queryKeys = {
  questions:    { all: ['questions'] as const, list: (f) => ['questions', f] as const, detail: (id) => ['questions', id] as const },
  reviews:      { all: ['reviews'] as const, list: (f) => ['reviews', f] as const },
  applications: { all: ['applications'] as const },
  admin:        { queue: ['admin', 'queue'] as const, users: ['admin', 'users'] as const },
};
Route Guards
tsx// In App.tsx routing
<Route element={<PrivateRoute />}>
  <Route element={<OnboardingGuard />}>   {/* redirects to /onboarding if incomplete */}
    <Route path="/dashboard" element={<Dashboard />} />
    ...
  </Route>
</Route>
<Route element={<AdminRoute />}>          {/* checks role === 'admin' || 'super_admin' */}
  <Route path="/admin" element={<AdminDashboard />} />
</Route>
Component Rules

Page components (in pages/) are route-level only. They fetch data and pass props down.
components/ui/ contains only dumb, stateless primitives (Button, Badge, Input, Card, Modal).
components/forms/ contains controlled form components using React Hook Form + Zod resolver.
Never fetch data inside components/ui/ or components/layout/ components.

Tailwind Usage
Use Tailwind utility classes only. No custom CSS files unless absolutely necessary. Keep variants consistent — use sm:, md: breakpoints for responsive layouts.

Database Schema — Key Facts
All tables use:

uuid primary keys (gen_random_uuid())
timestamptz for all timestamps (timezone-aware)
RLS enabled on every table

Critical Column Rules

interview_questions.question_text: min 20 chars — enforce on both Pydantic schema and DB CHECK constraint.
interview_reviews.review_text: min 50 chars — same.
interview_questions.asked_date and interview_reviews.interview_date: always stored as YYYY-MM-01 (first of month). Enforce in Pydantic with a field_validator.
applications.user_id: RLS policy enforces user_id = auth.uid() — never leak another user's applications.
Anonymous submissions: is_anonymous = true hides submitted_by from all public API responses, but the field is still stored and visible to admins.

Status Enums
interview_questions.status: 'pending' | 'approved' | 'rejected' | 'needs_edit'
interview_reviews.status:   'pending' | 'approved' | 'rejected' | 'needs_edit'
companies.status:           'pending' | 'approved'
applications.status:        'applied' | 'interview' | 'offer' | 'rejected' | 'closed'
content_flags.status:       'open' | 'resolved' | 'dismissed'
RLS Summary
TablePublic read?Who writes?interview_questionsOnly status = approvedAuthenticated users (insert); admins + submitter on needs_edit (update)interview_reviewsOnly status = approvedSame as aboveapplicationsNo — user's own rows onlyOwner onlycontent_flagsNoAuthenticated insert; admin read/updateprep_progressNo — user's own rows onlyOwner only

API Conventions
Response Shape
All endpoints return JSON. Success responses:
json{ "data": { ... } }             // single resource
{ "data": [...], "count": N }   // list with pagination
{ "id": "uuid", "status": "pending", "message": "..." }  // creation confirmation
Error responses:
json{ "error": "Unauthorized" }                  // 401, 403
{ "errors": [{ "loc": [...], "msg": "..." }] }  // 400 Pydantic validation
{ "error": "Internal server error" }         // 500
Pagination
All list endpoints support ?page=1&limit=20 (max 50). Return count for total records.
Anonymous Content
When is_anonymous = true on a question or review, strip submitted_by from the response before sending to the client. Admin endpoints are exempt.
pythondef sanitize(q: dict, is_admin: bool) -> dict:
    if not is_admin and q.get('is_anonymous'):
        q.pop('submitted_by', None)
    return q
Upvote Toggle
POST /questions/:id/upvote is idempotent:

If row exists in question_upvotes → delete it (un-upvote) and decrement counter.
If row does not exist → insert it (upvote) and increment counter.
Return { "upvoted": bool, "upvotes": int }.

Use a Postgres transaction for the check+update to avoid race conditions.

Email Notifications
All emails are sent from email_service.py after moderation actions. Never send email directly in a router handler.
TriggerRecipientWhenQuestion/review submittedSubmitterAfter successful insertQuestion/review approvedSubmitterAfter admin approvesQuestion/review rejectedSubmitterAfter admin rejects (include admin_note)Edit requestedSubmitterAfter needs_edit action (include admin_note)Resubmission receivedAdminsWhen submitter resubmits a needs_edit itemApplication deadlineUser7 days and 1 day before deadlineAccount warnedUserAfter warn actionAccount suspendedUserAfter suspend action
Deadline reminder emails require a background job (cron). Implement as a separate scheduled function — do not block the request lifecycle.
python# services/email_service.py — uses SMTP (resend) via stdlib smtplib
def send_submission_confirmation(to: str) -> None:
    _send(to, "Submission received", "Your submission is under review.")

Real-Time (Admin Queue)
The admin moderation queue uses Supabase Realtime. The subscription is initialized once when an admin loads the queue page and torn down on unmount:
ts// In ModerationQueue.tsx or a custom hook useAdminQueue
useEffect(() => {
  const channel = supabase.channel('admin-queue')
    .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'interview_questions', filter: 'status=eq.pending' },
      () => queryClient.invalidateQueries(queryKeys.admin.queue))
    .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'interview_reviews', filter: 'status=eq.pending' },
      () => queryClient.invalidateQueries(queryKeys.admin.queue))
    .subscribe();
  return () => { supabase.removeChannel(channel); };
}, []);
Do not use Realtime outside the admin panel.

Python Types (types/__init__.py)
Mirror the DB schema exactly. Keep in sync manually or generate from Supabase CLI.
python# types/__init__.py
from typing import Literal, TypedDict

UserRole = Literal['user', 'admin', 'super_admin']
QuestionStatus = Literal['pending', 'approved', 'rejected', 'needs_edit']
QuestionType = Literal['technical', 'behavioural', 'hr', 'case_study']
Difficulty = Literal['easy', 'medium', 'hard']

class AuthUser(TypedDict):
    sub: str        # Supabase user UUID
    email: str
    user_metadata: dict   # contains 'role'
Use user dict (from get_current_user) in all authenticated services. Set by the auth dependency:
python# dependencies/auth.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

def get_current_user(credentials = Depends(HTTPBearer())) -> dict:
    payload = _decode_token(credentials.credentials)
    role = get_user_role(payload["sub"])   # authoritative from public.users
    return {"sub": payload["sub"], "email": payload.get("email"), "role": role, "token": credentials.credentials}

Environment Variables
Backend .env
NODE_ENV=development
PORT=3001
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key   # never expose to frontend
SUPABASE_JWT_SECRET=your-jwt-secret
SMTP_HOST=smtp.resend.com
SMTP_PORT=465
SMTP_USER=resend
SMTP_PASS=your-api-key
EMAIL_FROM=noreply@careerbridge.pk
Frontend .env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key             # safe to expose (RLS enforces access)
VITE_API_BASE_URL=http://localhost:3001/api/v1
Critical: SUPABASE_SERVICE_ROLE_KEY must never appear in the frontend or any client-side code. It bypasses all RLS. Only the backend uses it.

Database Migrations

All schema changes go in supabase/migrations/YYYYMMDDHHMMSS_descriptive_name.sql.
Never run raw SQL on production manually.
Run locally with supabase db reset (wipes local) or supabase migration up.
Migrations are applied in CI before API deployment.


CI/CD (GitHub Actions)
TriggerActionPull requestLint (flake8/ruff), type check (mypy), unit tests (pytest)Merge to mainBuild, test, auto-deploy to stagingRelease tag (v*)Deploy frontend to Vercel prod, API to Railway prod, run migrations

Development Startup
bash# 1. Start local Supabase
supabase start

# 2. Start backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py                                      # or: uvicorn main:app --reload --port 3001

# 3. Start frontend
cd frontend && npm run dev       # runs Vite on :5173
Local Supabase Studio: http://localhost:54323
API docs (Swagger): http://localhost:3001/docs

Common Mistakes to Avoid

Never use the service role key in the frontend. It bypasses all RLS and exposes the entire database.
Never write mutations directly from React to Supabase. All writes go through the FastAPI API.
Never skip Pydantic validation on the backend. Frontend validation is UX only — always re-validate server-side.
Never expose submitted_by for anonymous content. Always strip it in the API response before sending.
Never render question_text or review_text as raw HTML. Always treat user content as plain text to prevent XSS.
Never allow cross-user application access. RLS enforces user_id = auth.uid() but the API should also verify ownership before any update/delete.
Never hardcode role checks in frontend UI only. Backend dependencies are the authoritative guard. Frontend role checks are UX convenience only.
Never skip the onboarding_complete redirect. If a user skips onboarding and lands on /dashboard, their profile data will be missing and break personalization logic.
Never put TanStack Query data in Zustand. It creates stale data bugs. Server state lives in TanStack Query, client/UI state lives in Zustand.
The asked_date field is always YYYY-MM-01. If a full date is being stored here, the Pydantic field_validator is missing.
Never send emails directly in a route handler. Always delegate to email_service.py.
Use Depends(get_current_user) for protected routes — never parse JWT manually in routers.


Out of Scope (Do Not Build Yet)
The following are explicitly Phase 2 or Phase 3 and should not be started:

AI Mock Interview (Anthropic API integration)
Preparedness Dashboard (needs user activity data)
Mentorship booking / 1:1 sessions
Native iOS / Android app
Employer-facing portal
Paid premium tiers
Contribution leaderboard
International expansion features

If a feature is not in the Phase 1 spec above, ask before building it.