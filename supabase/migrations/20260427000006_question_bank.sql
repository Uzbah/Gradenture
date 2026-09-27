-- ============================================================
-- CareerBridge — Curated question bank + UI/UX and QA domains
-- ============================================================

INSERT INTO public.domains (name, slug) VALUES
  ('UI/UX Design',      'ui-ux-design'),
  ('Quality Assurance', 'quality-assurance')
ON CONFLICT (slug) DO NOTHING;

-- Admin-curated questions, imported by backend/scripts/ingest_questions.py.
-- Deliberately separate from interview_questions (community submissions):
-- no submitter, no asked_date, no moderation lifecycle.
CREATE TABLE IF NOT EXISTS public.question_bank (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  domain_id     uuid NOT NULL REFERENCES public.domains(id),
  company_id    uuid REFERENCES public.companies(id),
  role_title    text NOT NULL CHECK (char_length(role_title) BETWEEN 1 AND 100),
  question_text text NOT NULL CHECK (char_length(question_text) >= 20),
  question_type text NOT NULL CHECK (question_type IN ('technical', 'behavioural', 'hr', 'case_study')),
  difficulty    text CHECK (difficulty IN ('easy', 'medium', 'hard')),
  source        text NOT NULL,   -- import batch tag; DELETE ... WHERE source = x undoes a batch
  content_hash  text NOT NULL,   -- sha256 of normalised text, for idempotent re-imports
  search        tsvector GENERATED ALWAYS AS (to_tsvector('english', question_text)) STORED,
  created_at    timestamptz NOT NULL DEFAULT now(),
  -- Same question at two companies is signal, not a duplicate. NULLS NOT DISTINCT
  -- so company-less rows still dedupe.
  CONSTRAINT question_bank_unique UNIQUE NULLS NOT DISTINCT (domain_id, company_id, content_hash)
);

CREATE INDEX IF NOT EXISTS question_bank_search_idx ON public.question_bank USING gin (search);

ALTER TABLE public.question_bank ENABLE ROW LEVEL SECURITY;

CREATE POLICY "question_bank_public_read" ON public.question_bank
  FOR SELECT USING (true);

-- Imports are audited like every other admin action.
ALTER TABLE public.admin_audit_log DROP CONSTRAINT IF EXISTS admin_audit_log_target_type_check;
ALTER TABLE public.admin_audit_log ADD CONSTRAINT admin_audit_log_target_type_check
  CHECK (target_type IN ('question', 'review', 'company', 'user', 'flag', 'question_bank'));
