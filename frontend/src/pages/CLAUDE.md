# frontend/src/pages

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

One file per route; forms are inlined as local components in the same file. Pattern: `useState` + `api()` calls, errors shown via `err.message`, optimistic update then reconcile.

| File | Route | Auth | Talks to |
|------|-------|------|----------|
| `Login.tsx` | `/login` | public | `/auth/login`, `/auth/resend-verification` |
| `Register.tsx` | `/register` | public | `/auth/register` |
| `ForgotPassword.tsx` | `/forgot-password` | public | `/auth/forgot-password` |
| `ResetPassword.tsx` | `/reset-password` | recovery token from URL hash | `/auth/reset-password` |
| `Onboarding.tsx` | `/onboarding` | JWT | `/domains`, `/users/onboarding` |
| `Dashboard.tsx` | `/` | JWT | applications, latest questions, prep score |
| `Questions.tsx` | `/questions` | JWT | list/filter/submit/upvote/flag + inline "add company" |
| `Reviews.tsx` | `/reviews` | JWT | list/filter/submit/flag |
| `Companies.tsx` | `/companies` | JWT | paginated registry with search |
| `CompanyProfile.tsx` | `/companies/:companyId` | JWT | company + its questions/reviews; managers get a "propose changes" form → `/edit-request` |
| `Applications.tsx` | `/applications` | JWT | 5-column kanban, move via `<select>`, delete |
| `Prep.tsx` | `/prep` | JWT | topic checklist + `ProgressRing` (exported, reused by Dashboard) |
| `Resume.tsx` | `/resume` | JWT | multipart upload → `/resume/analyze` |
| `Admin.tsx` | `/admin` | admin (API-enforced) | tabs: queue (questions/reviews/companies/profile edits), flags, companies (CRUD/merge/managers), users (role = super_admin only, suspend) |

Flag reasons and moderation notes use `window.prompt`. `website` / `job_url` are rendered as `<a href target="_blank" rel="noreferrer">`.
