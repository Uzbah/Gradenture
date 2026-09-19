-- ============================================================
-- CareerBridge — indexes for the queries the API actually runs
-- ============================================================
-- Before this migration only three indexes existed outside the primary keys
-- (admin_audit_log.created_at, company_admins.user_id, and the partial index on
-- pending company edits), so every list endpoint fell back to a sequential scan
-- plus a sort. Each index below matches a query in the service layer; the
-- comment names it.
--
-- CREATE INDEX (not CONCURRENTLY): these run inside the migration's transaction.
-- On a table large enough for the write lock to matter, run the equivalent
-- CONCURRENTLY by hand outside a transaction instead.

-- question_service.get_list: status = 'approved' ordered by created_at desc
CREATE INDEX IF NOT EXISTS interview_questions_status_created_idx
  ON public.interview_questions (status, created_at DESC);

-- ... filtered by company, by domain, and by type/difficulty
CREATE INDEX IF NOT EXISTS interview_questions_company_idx
  ON public.interview_questions (company_id);
CREATE INDEX IF NOT EXISTS interview_questions_domain_idx
  ON public.interview_questions (domain_id);

-- merge_company repoints by company_id; moderation reads a submitter's history
CREATE INDEX IF NOT EXISTS interview_questions_submitted_by_idx
  ON public.interview_questions (submitted_by);

-- review_service.get_list, same shapes
CREATE INDEX IF NOT EXISTS interview_reviews_status_created_idx
  ON public.interview_reviews (status, created_at DESC);
CREATE INDEX IF NOT EXISTS interview_reviews_company_idx
  ON public.interview_reviews (company_id);
CREATE INDEX IF NOT EXISTS interview_reviews_submitted_by_idx
  ON public.interview_reviews (submitted_by);

-- company_service.get_list: status = 'approved' ordered by name;
-- the admin list filters on status alone
CREATE INDEX IF NOT EXISTS companies_status_name_idx
  ON public.companies (status, name);

-- company_service.create does an ILIKE duplicate check on the exact name.
-- A plain btree cannot serve ILIKE, so index the folded value the check compares.
CREATE INDEX IF NOT EXISTS companies_lower_name_idx
  ON public.companies (lower(name));

-- flag_service.get_list: status = 'open' ordered by created_at
CREATE INDEX IF NOT EXISTS content_flags_status_created_idx
  ON public.content_flags (status, created_at);

-- flag_service.get_list then looks the flagged content up by id and type
CREATE INDEX IF NOT EXISTS content_flags_content_idx
  ON public.content_flags (content_type, content_id);

-- application_service.get_list: the caller's own rows, optionally by status
CREATE INDEX IF NOT EXISTS applications_user_status_idx
  ON public.applications (user_id, status);

-- prep_service reads every row for one user
CREATE INDEX IF NOT EXISTS prep_progress_user_idx
  ON public.prep_progress (user_id);

-- The composite primary key (question_id, user_id) cannot serve a lookup by user
-- alone, which is what "questions I upvoted" needs.
CREATE INDEX IF NOT EXISTS question_upvotes_user_idx
  ON public.question_upvotes (user_id);

-- user_admin_service.get_list orders by created_at desc
CREATE INDEX IF NOT EXISTS users_created_idx
  ON public.users (created_at DESC);

-- auth_service and grant_company_manager look users up by email, case-insensitively
CREATE INDEX IF NOT EXISTS users_lower_email_idx
  ON public.users (lower(email));
