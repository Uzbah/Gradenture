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
API base URL (dev): http://localhost:5000/api/v1


Monorepo Layout
careerbridge/
├── backend/
│   ├── app.py                      ← Flask app factory
│   ├── run.py                      ← Dev entrypoint
│   ├── requirements.txt
│   ├── .env                        ← never commit
│   └── src/
│       ├── config/
│       │   ├── supabase.py
│       │   ├── email.py
│       │   └── rate_limiter.py
│       ├── middleware/
│       │   ├── authenticate.py
│       │   ├── require_admin.py
│       │   ├── require_super_admin.py
│       │   └── error_handler.py
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── users.py
│       │   ├── questions.py
│       │   ├── reviews.py
│       │   ├── companies.py
│       │   ├── applications.py
│       │   └── admin.py
│       ├── controllers/
│       │   ├── users_controller.py
│       │   ├── questions_controller.py
│       │   ├── reviews_controller.py
│       │   ├── companies_controller.py
│       │   ├── applications_controller.py
│       │   └── admin_controller.py
│       ├── services/
│       │   ├── email_service.py
│       │   ├── moderation_service.py
│       │   └── upload_service.py
│       ├── schemas/
│       │   ├── question_schema.py
│       │   ├── review_schema.py
│       │   ├── application_schema.py
│       │   └── user_schema.py
│       └── types/
│           └── __init__.py
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
PackageVersionPurposePython3.11+RuntimeFlask3.xREST API frameworkPydanticv2Request validation & serializationsupabase-py2.xDB operationsPyJWT2.xJWT verificationFlask-Mail0.10+Transactional emailFlask-Limiter3.xRate limitingpython-dotenv1.xEnvironment variablesgunicorn21.xProduction WSGI server
Frontend
PackageVersionPurposeReact18+UIVitelatestBuild toolTypeScript5.xType safetyTanStack Queryv5Server state / cachingZustandv4Client UI stateTailwind CSSv3StylingReact Routerv6RoutingZodv3Form validation@hello-pangea/dndlatestKanban drag & drop
Infrastructure
ServicePurposeSupabase (Postgres 15)Primary DB, Auth, Storage, RealtimeVercelFrontend hostingRailwayBackend API hostingGitHub ActionsCI/CD

Architecture Rules — Read Before Writing Any Code
Read vs Write Split
This is the most important architectural rule.

React → Supabase directly (anon client): read-only, non-sensitive queries — listing approved questions, browsing companies, domain pages.
React → Flask API (with JWT): ALL writes, ALL mutations, sensitive reads — submitting questions, moderation, application tracking, profile updates.

Never write directly to Supabase from React for mutations. Never proxy a simple public read through Flask unnecessarily.
Authentication Flow

Supabase Auth issues a JWT on login (handled client-side by supabase-js).
JWT is stored in Zustand authStore + localStorage.
Every Flask request includes Authorization: Bearer <jwt> header.
Flask authenticate decorator verifies the token using SUPABASE_JWT_SECRET.
Admin routes additionally run require_admin which checks user_metadata.role.

The Flask API does not issue JWTs — only Supabase does. Flask only verifies them.
Role System
Roles live in two places and must match:

auth.users.user_metadata.role (Supabase Auth metadata)
public.users.role (application DB)

Valid roles: user | admin | super_admin
Only super_admin can assign/revoke admin roles (POST /admin/users/:id/role).

Backend Conventions
Route → Controller → Service Pattern

Routes (routes/*.py): register blueprints, attach decorators, define path + HTTP method, call controller. No business logic.
Controllers (controllers/*_controller.py): parse request, call service or Supabase, return response. Thin.
Services (services/*_service.py): business logic spanning multiple DB operations (e.g. approve a question + send email). Use services when a controller action needs more than one step.

python# routes/questions.py
from flask import Blueprint
from src.middleware.authenticate import authenticate
from src.middleware.validate import validate
from src.schemas.question_schema import QuestionSchema
from src.controllers.questions_controller import create

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/', methods=['POST'])
@authenticate
@validate(QuestionSchema)
def create_question():
    return create()
python# controllers/questions_controller.py
from flask import request, jsonify, g
from src.config.supabase import supabase
from src.services.email_service import send_submission_confirmation

def create():
    data = request.validated_data   # set by @validate decorator
    result = supabase.table('interview_questions').insert({
        **data,
        'submitted_by': g.user['sub'],
        'status': 'pending'
    }).execute()
    send_submission_confirmation(g.user['email'])
    return jsonify({'id': result.data[0]['id'], 'status': 'pending', 'message': 'Submitted for review'}), 201
Decorator Order (always this order)
python@blueprint.route('/path', methods=['POST'])
@authenticate
@require_admin          # if needed
@validate(SomeSchema)
def handler():
    ...
Pydantic Validation
All POST/PATCH payloads are validated server-side using Pydantic v2 models. The validate decorator wraps a Pydantic model and returns 400 with structured errors on failure:
python# middleware/validate.py
from functools import wraps
from flask import request, jsonify
from pydantic import ValidationError

def validate(schema_class):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                request.validated_data = schema_class(**request.get_json()).model_dump()
            except ValidationError as e:
                return jsonify({'errors': e.errors()}), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator
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
All controllers use try/except and rely on the global error handler registered in app.py:
python# app.py
from src.middleware.error_handler import handle_exception
app.register_error_handler(Exception, handle_exception)
python# middleware/error_handler.py
from flask import jsonify
import logging

def handle_exception(err):
    logging.exception(err)
    return jsonify({'error': 'Internal server error'}), 500
App Factory (app.py)
python# app.py
from flask import Flask
from src.routes.questions import questions_bp
from src.routes.reviews import reviews_bp
# ... other blueprints
from src.middleware.error_handler import handle_exception

def create_app():
    app = Flask(__name__)

    app.register_blueprint(questions_bp, url_prefix='/api/v1/questions')
    app.register_blueprint(reviews_bp,   url_prefix='/api/v1/reviews')
    # ... register all blueprints

    app.register_error_handler(Exception, handle_exception)
    return app
Supabase Client in Backend
Use the service role key in the backend — it bypasses RLS. This is correct and intentional because the API enforces authorization through middleware, not RLS.
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

Use Flask-Limiter. Config in config/rate_limiter.py.
python# config/rate_limiter.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=['100 per minute'])
Apply per-route:
python@questions_bp.route('/', methods=['POST'])
@authenticate
@limiter.limit('5 per hour', key_func=lambda: g.user['sub'])
@validate(QuestionSchema)
def create_question():
    return create()
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
All emails are sent from email_service.py after moderation actions. Never send email directly in a route handler.
TriggerRecipientWhenQuestion/review submittedSubmitterAfter successful insertQuestion/review approvedSubmitterAfter admin approvesQuestion/review rejectedSubmitterAfter admin rejects (include admin_note)Edit requestedSubmitterAfter needs_edit action (include admin_note)Resubmission receivedAdminsWhen submitter resubmits a needs_edit itemApplication deadlineUser7 days and 1 day before deadlineAccount warnedUserAfter warn actionAccount suspendedUserAfter suspend action
Deadline reminder emails require a background job (cron). Implement as a separate scheduled function — do not block the request lifecycle.
python# config/email.py
from flask_mail import Mail
mail = Mail()

# services/email_service.py
from flask_mail import Message
from src.config.email import mail

def send_submission_confirmation(to_email: str):
    msg = Message('Submission received', recipients=[to_email])
    msg.body = 'Your submission is under review.'
    mail.send(msg)

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
Use g.user (type AuthUser) in all authenticated controllers. Set it in the @authenticate decorator:
python# middleware/authenticate.py
from functools import wraps
from flask import request, jsonify, g
import jwt, os

def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', '').removeprefix('Bearer ')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401
        try:
            g.user = jwt.decode(token, os.environ['SUPABASE_JWT_SECRET'], algorithms=['HS256'])
        except jwt.PyJWTError:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapper

Environment Variables
Backend .env
FLASK_ENV=development
PORT=5000
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key   # never expose to frontend
SUPABASE_JWT_SECRET=your-jwt-secret
MAIL_SERVER=smtp.resend.com
MAIL_PORT=465
MAIL_USERNAME=resend
MAIL_PASSWORD=your-api-key
MAIL_DEFAULT_SENDER=noreply@careerbridge.pk
RATE_LIMIT_STORAGE_URL=memory://
Frontend .env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key             # safe to expose (RLS enforces access)
VITE_API_BASE_URL=http://localhost:5000/api/v1
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
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
flask run --port 5000            # or: python run.py

# 3. Start frontend
cd frontend && npm run dev       # runs Vite on :5173
Local Supabase Studio is available at http://localhost:54323 after supabase start.

Common Mistakes to Avoid

Never use the service role key in the frontend. It bypasses all RLS and exposes the entire database.
Never write mutations directly from React to Supabase. All writes go through Flask.
Never skip Pydantic validation on the backend. Frontend validation is UX only — always re-validate server-side.
Never expose submitted_by for anonymous content. Always strip it in the API response before sending.
Never render question_text or review_text as raw HTML. Always treat user content as plain text to prevent XSS.
Never allow cross-user application access. RLS enforces user_id = auth.uid() but the API should also verify ownership before any update/delete.
Never hardcode role checks in frontend UI only. Backend decorators are the authoritative guard. Frontend role checks are UX convenience only.
Never skip the onboarding_complete redirect. If a user skips onboarding and lands on /dashboard, their profile data will be missing and break personalization logic.
Never put TanStack Query data in Zustand. It creates stale data bugs. Server state lives in TanStack Query, client/UI state lives in Zustand.
The asked_date field is always YYYY-MM-01. If a full date is being stored here, the Pydantic field_validator is missing.
Never send emails directly in a route handler. Always delegate to email_service.py.
Always use @wraps(f) in decorators. Without it, Flask's routing breaks when multiple routes share the same function name.


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