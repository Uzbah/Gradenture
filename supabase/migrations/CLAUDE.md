# supabase/migrations

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

Run in order. Filenames are `YYYYMMDDHHMMSS_name.sql`.

| File | Creates |
|------|---------|
| `20260427000001_initial_schema.sql` | `domains` (seeded with 8 rows), `users` (mirrors `auth.users`, holds `role`, onboarding fields), `update_updated_at()` trigger fn. RLS: domains public read; users own-row select/update/insert. |
| `20260427000002_remaining_tables.sql` | `companies`, `interview_questions`, `interview_reviews`, `question_upvotes`, `content_flags`, `applications`, `prep_progress` + triggers. RLS: approved-only public reads; authenticated inserts on questions/reviews/flags; own-row on upvotes/applications/prep. |
| `20260427000003_upvote_functions.sql` | `increment_upvotes(qid)` / `decrement_upvotes(qid)` — `SECURITY DEFINER`, called by the API via RPC. |
| `20260427000004_admin_audit_log.sql` | `admin_audit_log` (RLS on, no policies → service role only); adds `users.suspended_at`. |
| `20260427000005_company_admins.sql` | `company_admins` (per-company managers) and `company_edit_requests` (moderated profile edits). Both RLS on, no policies. |

Status enums live in `CHECK` constraints: submission `pending|approved|rejected|needs_edit`; company `pending|approved`; role `user|admin|super_admin`; application `applied|interview|offer|rejected|closed`.

Known RLS gaps (from the security review, unfixed): `users_own_row_update` allows editing `role`; question/review insert policies don't constrain `status`/`submitted_by`; upvote RPCs are executable by PUBLIC. The API bypasses RLS via service role, so these only bite once a browser client uses the anon key. Fix in a new migration, never by editing these files.
