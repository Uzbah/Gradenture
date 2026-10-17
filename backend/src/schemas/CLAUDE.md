# backend/src/schemas

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

Pydantic v2 request models. Validation only; no I/O. Enum-like fields use `Literal[...]` and must match the Postgres `CHECK` constraints in `supabase/migrations`.

- `common.py` — reusable field types: `UUIDStr` (validated id, kept as `str`), `HttpUrlStr` (http/https only, ≤ 500), `DateStr` (real ISO date), `MonthStr` (`YYYY-MM-01`, real month).
- `auth_schema.py` — Register/Login/ForgotPassword/ResendVerification/ResetPassword (`current_password` optional; the service requires it unless the session came from a recovery link). Emails are trimmed + lowercased in a `before` validator; passwords 8–128 chars.
- `user.py` — `OnboardingSchema` (domain UUID, skill_level, goal, university 2–100).
- `question_schema.py` — `QuestionSchema` (text ≥ 20, notes ≤ 500, role ≤ 100, `asked_date` `MonthStr`, ids `UUIDStr`), `QuestionEditSchema` (resubmit), `FlagSchema` (reason 5–500, shared with reviews).
- `review_schema.py` — `ReviewSchema` (text ≥ 50, `interview_date` `MonthStr`, ids `UUIDStr`), `ReviewEditSchema`.
- `application_schema.py` — `ApplicationSchema`, `ApplicationUpdateSchema` (partial: dump with `exclude_unset`; explicit null clears dates/link/notes and is rejected for name/role/status).
- `company_schema.py` — user proposal, admin create/update, merge, manager grant, manager edit request (deliberately has no `status`), edit decision.
- `admin_schema.py` — `ModerateSchema`, `UpdateRoleSchema`, `FlagActionSchema`.
- `__init__.py` — empty.

`website`, `logo_url`, `job_url` are `HttpUrlStr`: they render as `<a href>`, so `javascript:` must never get in.
