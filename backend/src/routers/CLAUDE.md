# backend/src/routers

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

One file per domain, each exporting `router`; `__init__.py` mounts them all under `/api/v1`. Routers only parse → call a service → return. No DB access here.

| File | Prefix | Auth | Notes |
|------|--------|------|-------|
| `auth.py` | `/auth` | mixed | register (10/h), login (20/h), logout, forgot/reset password, resend verification |
| `users.py` | `/users`, `/domains` | JWT (domains public) | `GET /users/me`, `PATCH /users/onboarding` |
| `questions.py` | `/questions` | list/get public | submit (5/h per user), upvote, flag (10/h) |
| `reviews.py` | `/reviews` | list/get public | submit (5/h per user), flag (10/h) |
| `companies.py` | `/companies` | list/get public | submit proposal (pending), `/managed`, `/{id}/edit-request` (company manager) |
| `applications.py` | `/applications` | JWT | CRUD on the caller's own rows |
| `prep.py` | `/prep` | JWT | roadmap topics + score; `ToggleSchema` is defined inline here |
| `resume.py` | `/resume` | JWT | `POST /analyze` multipart upload (3/h per user); the only `async def` route |
| `admin.py` | `/admin` | admin / super_admin | queue, moderate, companies (CRUD, merge, managers), flags, users (role, warn, suspend) |

Rate limits need `request: Request` as the first parameter (slowapi requirement). Add `@limiter.limit` to any new write endpoint.
