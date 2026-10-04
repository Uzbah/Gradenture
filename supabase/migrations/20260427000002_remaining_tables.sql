-- ============================================================
-- CareerBridge — Remaining Tables
-- ============================================================

-- Companies
CREATE TABLE IF NOT EXISTS public.companies (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name        text NOT NULL UNIQUE,
  slug        text NOT NULL UNIQUE,
  logo_url    text,
  website     text,
  industry    text,
  status      text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved')),
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER companies_updated_at
  BEFORE UPDATE ON public.companies
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Interview Questions
CREATE TABLE IF NOT EXISTS public.interview_questions (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  submitted_by  uuid REFERENCES public.users(id) ON DELETE SET NULL,
  domain_id     uuid NOT NULL REFERENCES public.domains(id),
  company_id    uuid NOT NULL REFERENCES public.companies(id),
  role_title    text NOT NULL CHECK (char_length(role_title) BETWEEN 1 AND 100),
  question_text text NOT NULL CHECK (char_length(question_text) >= 20),
  question_type text NOT NULL CHECK (question_type IN ('technical', 'behavioural', 'hr', 'case_study')),
  difficulty    text NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
  asked_date    date NOT NULL,
  notes         text CHECK (char_length(notes) <= 500),
  is_anonymous  boolean NOT NULL DEFAULT false,
  status        text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'needs_edit')),
  admin_note    text,
  reviewed_by   uuid REFERENCES public.users(id),
  reviewed_at   timestamptz,
  upvotes       integer NOT NULL DEFAULT 0,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER interview_questions_updated_at
  BEFORE UPDATE ON public.interview_questions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Interview Reviews
CREATE TABLE IF NOT EXISTS public.interview_reviews (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  submitted_by   uuid REFERENCES public.users(id) ON DELETE SET NULL,
  company_id     uuid NOT NULL REFERENCES public.companies(id),
  domain_id      uuid REFERENCES public.domains(id),
  role_title     text NOT NULL CHECK (char_length(role_title) BETWEEN 1 AND 100),
  review_text    text NOT NULL CHECK (char_length(review_text) >= 50),
  interview_date date NOT NULL,
  difficulty     text CHECK (difficulty IN ('easy', 'medium', 'hard')),
  outcome        text CHECK (outcome IN ('offer', 'rejected', 'ghosted', 'withdrew', 'pending')),
  is_anonymous   boolean NOT NULL DEFAULT false,
  status         text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'needs_edit')),
  admin_note     text,
  reviewed_by    uuid REFERENCES public.users(id),
  reviewed_at    timestamptz,
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER interview_reviews_updated_at
  BEFORE UPDATE ON public.interview_reviews
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Question Upvotes (composite PK prevents double upvoting)
CREATE TABLE IF NOT EXISTS public.question_upvotes (
  question_id  uuid NOT NULL REFERENCES public.interview_questions(id) ON DELETE CASCADE,
  user_id      uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  created_at   timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (question_id, user_id)
);

-- Content Flags
CREATE TABLE IF NOT EXISTS public.content_flags (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  reported_by  uuid NOT NULL REFERENCES public.users(id),
  content_type text NOT NULL CHECK (content_type IN ('question', 'review')),
  content_id   uuid NOT NULL,
  reason       text NOT NULL CHECK (char_length(reason) >= 5),
  status       text NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'dismissed')),
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER content_flags_updated_at
  BEFORE UPDATE ON public.content_flags
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Applications (Job Tracker)
CREATE TABLE IF NOT EXISTS public.applications (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  company_name text NOT NULL CHECK (char_length(company_name) BETWEEN 1 AND 100),
  role_title   text NOT NULL CHECK (char_length(role_title) BETWEEN 1 AND 100),
  status       text NOT NULL DEFAULT 'applied' CHECK (status IN ('applied', 'interview', 'offer', 'rejected', 'closed')),
  applied_date date,
  deadline     date,
  job_url      text,
  notes        text CHECK (char_length(notes) <= 1000),
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER applications_updated_at
  BEFORE UPDATE ON public.applications
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Prep Progress
CREATE TABLE IF NOT EXISTS public.prep_progress (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  domain_id  uuid NOT NULL REFERENCES public.domains(id),
  topic      text NOT NULL,
  completed  boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_id, domain_id, topic)
);

-- RLS
ALTER TABLE public.companies          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.interview_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.interview_reviews   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.question_upvotes    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_flags       ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.applications        ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prep_progress       ENABLE ROW LEVEL SECURITY;

-- Companies: public read approved only
CREATE POLICY "companies_public_read" ON public.companies
  FOR SELECT USING (status = 'approved');

-- Questions: public read approved only
CREATE POLICY "questions_public_read" ON public.interview_questions
  FOR SELECT USING (status = 'approved');

CREATE POLICY "questions_auth_insert" ON public.interview_questions
  FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "questions_submitter_update" ON public.interview_questions
  FOR UPDATE USING (auth.uid() = submitted_by AND status = 'needs_edit');

-- Reviews: public read approved only
CREATE POLICY "reviews_public_read" ON public.interview_reviews
  FOR SELECT USING (status = 'approved');

CREATE POLICY "reviews_auth_insert" ON public.interview_reviews
  FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- Upvotes: authenticated users only
CREATE POLICY "upvotes_auth" ON public.question_upvotes
  FOR ALL USING (auth.uid() = user_id);

-- Flags: authenticated insert
CREATE POLICY "flags_auth_insert" ON public.content_flags
  FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- Applications: users see only their own rows
CREATE POLICY "applications_own_rows" ON public.applications
  FOR ALL USING (auth.uid() = user_id);

-- Prep progress: users see only their own rows
CREATE POLICY "prep_progress_own_rows" ON public.prep_progress
  FOR ALL USING (auth.uid() = user_id);
