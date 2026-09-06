-- ============================================================
-- CareerBridge — Admin Audit Log + suspension mirror
-- ============================================================

CREATE TABLE IF NOT EXISTS public.admin_audit_log (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_id    uuid NOT NULL REFERENCES public.users(id),
  action      text NOT NULL,
  target_type text NOT NULL CHECK (target_type IN ('question', 'review', 'company', 'user', 'flag')),
  target_id   uuid,
  detail      jsonb,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS admin_audit_log_created_at_idx
  ON public.admin_audit_log (created_at DESC);

-- Deny-by-default with no policies: readable/writable only by the service role.
ALTER TABLE public.admin_audit_log ENABLE ROW LEVEL SECURITY;

-- Display mirror of the auth.users ban so the admin user list needs no extra
-- auth API calls. auth.users remains the source of truth for login blocking.
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS suspended_at timestamptz;
