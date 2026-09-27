# backend/src/schemas

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

Pydantic v2 request models. Validation only; no I/O. Enum-like fields use `Literal[...]` and must match the Postgres `CHECK` constraints in `supabase/migrations`.

- `auth_schema.py` — Register/Login/ForgotPassword/ResendVerification/ResetPassword. Emails are trimmed + lowercased in a `before` validator; passwords 8–128 chars.
- `user.py` — `OnboardingSchema` (domain UUID, skill_level, goal, university 2–100).
- `question_schema.py` — `QuestionSchema` (text ≥ 20, role ≤ 100, `asked_date` = `YYYY-MM-01`), `QuestionEditSchema` (unused — resubmission endpoint not built), `FlagSchema` (reason ≥ 5, shared with reviews).
- `review_schema.py` — `ReviewSchema` (text ≥ 50, `interview_date` = `YYYY-MM-01`).
- `application_schema.py` — `ApplicationSchema`, `ApplicationUpdateSchema` (all optional).
- `company_schema.py` — user proposal, admin create/update, merge, manager grant, manager edit request (deliberately has no `status`), edit decision.
- `admin_schema.py` — `ModerateSchema`, `UpdateRoleSchema`, `FlagActionSchema`.
- `__init__.py` — empty.

Gap: `website`, `logo_url`, `job_url` are plain `str`; should become `AnyHttpUrl`.
