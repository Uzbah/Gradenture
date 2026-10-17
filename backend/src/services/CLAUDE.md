# backend/src/services

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

All business logic and every Supabase query. Each function takes the `user` dict from `dependencies.auth` where auth matters, and raises `AppError` for client errors.

- `auth_service.py` — register (auth sign_up → `public.users` insert, rollback on failure), login (returns access + refresh token, checks ban, reads role), logout (global sign-out), forgot/reset password, resend verification. Forgot-password sends `redirect_to=$APP_URL/reset-password`. Reset uses the admin API on `user["sub"]` and requires `current_password` (checked by a throwaway sign-in) unless the session's `amr` is `recovery`/`otp`/`magiclink`.
- `auth_helpers.py` — `get_user_role` (from `public.users`), `is_user_banned` (auth admin `banned_until`, 60 s in-memory cache, fails closed: auth API errors propagate as a 500 and aren't cached), `invalidate_ban_cache`, `sync_user_metadata_role`, `rollback_auth_user`.
- `users_service.py` — `get_me`, `get_domains`, `complete_onboarding` (upsert, university through `clean_text`).
- `questions_service.py` / `reviews_service.py` — public list/get (approved only, explicit `PUBLIC_COLUMNS` whitelist: no `submitted_by`, `reviewed_by`, `admin_note`), submit (always `pending`, text through `clean_text`), owner resubmit, upvote (`toggle_upvote` RPC: atomic, approved only), flag (`flag_content`, shared: approved targets only, one open flag per user → 409).
- `companies_service.py` — approved list/search (`ilike`), get, user proposal (pending, records `submitted_by`, duplicate check on the slug — not `ilike`, whose `%`/`_` are wildcards), `list_managed`, `request_edit` (one pending edit per company). `_slug()` lives here and is reused by admin.
- `applications_service.py` — owner-scoped CRUD via `_own_or_404`.
- `prep_service.py` — static `TOPICS` dict keyed by domain slug (`ponytail:` move to DB later); progress in `prep_progress`.
- `admin_service.py` — moderation queue, moderate question/review (`_moderate`: only from `pending`, else 409) and company (emails the proposer on approval; renames checked by `_check_new_name`), company create/merge/managers, flags, users (list, role, warn, suspend/unsuspend — plain admins may only act on plain users, `_require_can_discipline`), manager grants by exact email, company edit decisions. **Every mutation calls `_audit()`** → `admin_audit_log`.
- `resume_service.py` — PDF/DOCX text extraction (pdfplumber / python-docx, 5 MB cap, JD ≤ 10k chars) → Gemini JSON analysis via `google-genai` (`GEMINI_MODEL`, default `gemini-3.6-flash`). Synchronous; call only from `def` routes.
- `email_service.py` — SMTP (Resend) helpers on a background thread: submission receipts, moderation decisions, company approved, company-edit decisions, warn, suspend, deadline reminders. Skipped when `SMTP_PASS` is empty.
- `__init__.py` — empty.

Public serializers whitelist columns (`PUBLIC_COLUMNS`); add a column there deliberately, never switch back to `select("*")`.
