-- ============================================================
-- Gradenture — flag dedupe, deletable users, company proposer, list indexes
-- ============================================================

-- One open flag per user per item. Collapse existing duplicates first (keep the
-- earliest) so the index can be built.
DELETE FROM public.content_flags f
USING public.content_flags g
WHERE f.status = 'open' AND g.status = 'open'
  AND f.reported_by = g.reported_by
  AND f.content_type = g.content_type
  AND f.content_id = g.content_id
  AND (f.created_at, f.id) > (g.created_at, g.id);

CREATE UNIQUE INDEX IF NOT EXISTS content_flags_one_open_per_user
  ON public.content_flags (reported_by, content_type, content_id)
  WHERE status = 'open';

-- These FKs had no ON DELETE, so deleting any user who ever flagged, proposed
-- a company edit, moderated or granted a manager failed. admin_audit_log.actor_id
-- deliberately stays RESTRICT: audit history must not silently lose its actor.
ALTER TABLE public.content_flags
  DROP CONSTRAINT IF EXISTS content_flags_reported_by_fkey,
  ADD  CONSTRAINT content_flags_reported_by_fkey
       FOREIGN KEY (reported_by) REFERENCES public.users(id) ON DELETE CASCADE;

ALTER TABLE public.company_edit_requests
  DROP CONSTRAINT IF EXISTS company_edit_requests_requested_by_fkey,
  ADD  CONSTRAINT company_edit_requests_requested_by_fkey
       FOREIGN KEY (requested_by) REFERENCES public.users(id) ON DELETE CASCADE,
  DROP CONSTRAINT IF EXISTS company_edit_requests_reviewed_by_fkey,
  ADD  CONSTRAINT company_edit_requests_reviewed_by_fkey
       FOREIGN KEY (reviewed_by) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE public.interview_questions
  DROP CONSTRAINT IF EXISTS interview_questions_reviewed_by_fkey,
  ADD  CONSTRAINT interview_questions_reviewed_by_fkey
       FOREIGN KEY (reviewed_by) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE public.interview_reviews
  DROP CONSTRAINT IF EXISTS interview_reviews_reviewed_by_fkey,
  ADD  CONSTRAINT interview_reviews_reviewed_by_fkey
       FOREIGN KEY (reviewed_by) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE public.company_admins
  DROP CONSTRAINT IF EXISTS company_admins_granted_by_fkey,
  ADD  CONSTRAINT company_admins_granted_by_fkey
       FOREIGN KEY (granted_by) REFERENCES public.users(id) ON DELETE SET NULL;

-- Who proposed a company, so the approval can be emailed to them.
ALTER TABLE public.companies
  ADD COLUMN IF NOT EXISTS submitted_by uuid REFERENCES public.users(id) ON DELETE SET NULL;

-- List endpoints: public feeds filter on status and sort by created_at; the
-- company profile and "My submissions" filter on company_id / submitted_by.
CREATE INDEX IF NOT EXISTS interview_questions_status_created_idx
  ON public.interview_questions (status, created_at DESC);
CREATE INDEX IF NOT EXISTS interview_questions_company_idx
  ON public.interview_questions (company_id);
CREATE INDEX IF NOT EXISTS interview_questions_submitted_by_idx
  ON public.interview_questions (submitted_by);

CREATE INDEX IF NOT EXISTS interview_reviews_status_created_idx
  ON public.interview_reviews (status, created_at DESC);
CREATE INDEX IF NOT EXISTS interview_reviews_company_idx
  ON public.interview_reviews (company_id);
CREATE INDEX IF NOT EXISTS interview_reviews_submitted_by_idx
  ON public.interview_reviews (submitted_by);

CREATE INDEX IF NOT EXISTS applications_user_created_idx
  ON public.applications (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS question_bank_company_idx
  ON public.question_bank (company_id);
