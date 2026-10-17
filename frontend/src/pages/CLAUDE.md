# frontend/src/pages

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

One file per route; forms are inlined as local components in the same file. Pattern: `useState` + `api()` calls, errors shown via `<Notice error={err.message}>`, optimistic update then reconcile. Create forms (question, review, application, admin company) open in a `FormDialog`; tabs are Radix `Tabs`.

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
| `Applications.tsx` | `/applications` | JWT | 5-column kanban, move via `Choice`, delete (confirm dialog) |
| `Prep.tsx` | `/prep` | JWT | topic checklist + `ProgressRing` |
| `Resume.tsx` | `/resume` | JWT | multipart upload → `/resume/analyze` |
| `Profile.tsx` | `/profile` | JWT | My submissions + resubmit, profile details (`/users/onboarding`), password change (needs current password) |
| `Admin.tsx` | `/admin` | admin (API-enforced) | tabs: queue (questions/reviews/companies/profile edits), flags, companies (CRUD/merge/managers), users (role = super_admin only; suspend — plain admins only see it on plain users) |

Flag reasons (min 5 chars) and moderation notes (required for reject / request-edit) use `ReasonDialog`; destructive actions (delete, suspend) use `ConfirmDialog`; company merge picks its target in a dialog. `website` / `job_url` are rendered as `<a href={safeUrl(...)} target="_blank" rel="noreferrer">` — never put a raw user URL in an `href`.
