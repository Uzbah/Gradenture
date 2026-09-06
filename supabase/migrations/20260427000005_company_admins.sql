-- ============================================================
-- CareerBridge — Company managers (per-company RBAC)
-- ============================================================

-- A user granted management rights over ONE company. Scope is deliberately
-- limited to profile metadata: managers can never moderate the questions or
-- reviews written about their own company.
CREATE TABLE IF NOT EXISTS public.company_admins (
  company_id uuid NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
  user_id    uuid NOT NULL REFERENCES public.users(id)     ON DELETE CASCADE,
  granted_by uuid REFERENCES public.users(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (company_id, user_id)
);

CREATE INDEX IF NOT EXISTS company_admins_user_idx ON public.company_admins (user_id);

-- Manager profile edits go through the same moderation lifecycle as every
-- other piece of community content: nothing a company writes about itself
-- goes live without a platform admin approving it.
CREATE TABLE IF NOT EXISTS public.company_edit_requests (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id   uuid NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
  requested_by uuid NOT NULL REFERENCES public.users(id),
  changes      jsonb NOT NULL,
  status       text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  admin_note   text,
  reviewed_by  uuid REFERENCES public.users(id),
  reviewed_at  timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER company_edit_requests_updated_at
  BEFORE UPDATE ON public.company_edit_requests
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE INDEX IF NOT EXISTS company_edit_requests_pending_idx
  ON public.company_edit_requests (created_at) WHERE status = 'pending';

-- Deny-by-default: no policies, so only the service role reaches these.
-- All access is mediated by the API, which checks roles explicitly.
ALTER TABLE public.company_admins        ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.company_edit_requests ENABLE ROW LEVEL SECURITY;
