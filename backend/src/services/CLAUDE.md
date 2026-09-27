# backend/src/services

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

All business logic and every Supabase query. Each function takes the `user` dict from `dependencies.auth` where auth matters, and raises `AppError` for client errors.

- `auth_service.py` — register (auth sign_up → `public.users` insert, rollback on failure), login (returns access + refresh token, checks ban, reads role), logout (global sign-out), forgot/reset password, resend verification. Reset uses the admin API on `user["sub"]`.
- `auth_helpers.py` — `get_user_role` (from `public.users`), `is_user_banned` (auth admin `banned_until`, 60 s in-memory cache, fails open), `invalidate_ban_cache`, `sync_user_metadata_role`, `rollback_auth_user`.
- `users_service.py` — `get_me`, `get_domains`, `complete_onboarding` (upsert, university cleaned with bleach).
- `questions_service.py` / `reviews_service.py` — public list/get (approved only; `_sanitize` drops `submitted_by` when anonymous), submit (always `pending`, text through `clean_text`), upvote toggle (uses `increment_upvotes`/`decrement_upvotes` RPCs), flag.
- `companies_service.py` — approved list/search (`ilike`), get, user proposal (pending, name uniqueness via `ilike`), `list_managed`, `request_edit` (one pending edit per company). `_slug()` lives here and is reused by admin.
- `applications_service.py` — owner-scoped CRUD via `_own_or_404`.
- `prep_service.py` — static `TOPICS` dict keyed by domain slug (`ponytail:` move to DB later); progress in `prep_progress`.
- `admin_service.py` — moderation queue, moderate question/review/company, company create/merge/managers, flags, users (list, role, warn, suspend/unsuspend), company edit decisions. **Every mutation calls `_audit()`** → `admin_audit_log`.
- `resume_service.py` — PDF/DOCX text extraction (pdfplumber / python-docx, 5 MB cap) → Gemini 2.0 Flash JSON analysis. Synchronous; blocks if called from an async route.
- `email_service.py` — SMTP (Resend) helpers. **Not wired** to any moderation action yet.
- `__init__.py` — empty.

Public serializers currently return `select("*")`; whitelist columns before adding fields that must stay internal.
