-- ============================================================
-- CareerBridge — Initial Schema
-- ============================================================

-- Domains (seeded, not user-created)
CREATE TABLE IF NOT EXISTS public.domains (
  id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name  text NOT NULL UNIQUE,
  slug  text NOT NULL UNIQUE
);

INSERT INTO public.domains (name, slug) VALUES
  ('Software Engineering',   'software-engineering'),
  ('Data Science & AI',      'data-science-ai'),
  ('Finance & Banking',      'finance-banking'),
  ('Marketing & Sales',      'marketing-sales'),
  ('Product Management',     'product-management'),
  ('Human Resources',        'human-resources'),
  ('Accounting',             'accounting'),
  ('Consulting',             'consulting')
ON CONFLICT (slug) DO NOTHING;

-- Users (mirrors auth.users, extended with profile fields)
CREATE TABLE IF NOT EXISTS public.users (
  id                  uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email               text NOT NULL,
  role                text NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'super_admin')),
  domain_id           uuid REFERENCES public.domains(id),
  skill_level         text CHECK (skill_level IN ('beginner', 'intermediate', 'advanced')),
  goal                text CHECK (goal IN ('first_job', 'switch_career', 'level_up', 'internship')),
  university          text CHECK (char_length(university) BETWEEN 2 AND 100),
  onboarding_complete boolean NOT NULL DEFAULT false,
  created_at          timestamptz NOT NULL DEFAULT now(),
  updated_at          timestamptz NOT NULL DEFAULT now()
);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
  BEFORE UPDATE ON public.users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- RLS
ALTER TABLE public.domains ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users   ENABLE ROW LEVEL SECURITY;

-- Domains: public read, no writes from client
CREATE POLICY "domains_public_read" ON public.domains
  FOR SELECT USING (true);

-- Users: each user can only read/update their own row
CREATE POLICY "users_own_row_select" ON public.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "users_own_row_update" ON public.users
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "users_own_row_insert" ON public.users
  FOR INSERT WITH CHECK (auth.uid() = id);
