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
| `20260427000006_question_bank.sql` | `question_bank` (curated, public read, full-text `search` column) + UI/UX and QA domains. |
| `20261017000001_rls_lockdown.sql` | Drops every client write policy (users role escalation, pre-approved inserts, own-row `FOR ALL`) → clients are read-only; drops `increment_upvotes`/`decrement_upvotes`. |
| `20261017000002_toggle_upvote.sql` | `toggle_upvote(qid, uid)` → jsonb `{upvoted, upvotes}` or NULL; row-locked, recounts; service_role only. Resyncs drifted counters. |
| `20261017000003_integrity_and_indexes.sql` | One open flag per user/item; FKs on flags / edit requests / `reviewed_by` / `granted_by` get `ON DELETE`; `companies.submitted_by`; list indexes. |

Status enums live in `CHECK` constraints: submission `pending|approved|rejected|needs_edit`; company `pending|approved`; role `user|admin|super_admin`; application `applied|interview|offer|rejected|closed`.

RLS model: the API (service role) is the only writer. Client policies are SELECT-only (public approved rows, own rows), because the anon key is public by design. If a browser client ever needs to write, add a narrow policy with a `WITH CHECK` in a new migration — never `FOR ALL`, never on `users.role`. New functions must `REVOKE ... FROM PUBLIC, anon, authenticated` (Supabase grants them by default).
