-- ============================================================
-- Gradenture — RLS lockdown: the API is the only writer
-- ============================================================
-- The anon key is public by design, and PostgREST is reachable at the project
-- URL. With the old policies, anyone holding it plus their own login JWT could
-- PATCH their users.role to super_admin, insert questions/reviews already
-- 'approved', or rewrite their own applications. Every write goes through the
-- FastAPI backend (service role, which bypasses RLS), so clients get read-only
-- access to what is public or their own, and nothing else.

-- users: keep own-row read; no client insert/update (role lives here)
DROP POLICY IF EXISTS "users_own_row_update" ON public.users;
DROP POLICY IF EXISTS "users_own_row_insert" ON public.users;

-- questions / reviews: public read of approved rows stays; no client writes
DROP POLICY IF EXISTS "questions_auth_insert"      ON public.interview_questions;
DROP POLICY IF EXISTS "questions_submitter_update" ON public.interview_questions;
DROP POLICY IF EXISTS "reviews_auth_insert"        ON public.interview_reviews;

-- flags: no client writes
DROP POLICY IF EXISTS "flags_auth_insert" ON public.content_flags;

-- own-row tables: FOR ALL → read-only
DROP POLICY IF EXISTS "upvotes_auth" ON public.question_upvotes;
CREATE POLICY "upvotes_own_read" ON public.question_upvotes
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "applications_own_rows" ON public.applications;
CREATE POLICY "applications_own_read" ON public.applications
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "prep_progress_own_rows" ON public.prep_progress;
CREATE POLICY "prep_progress_own_read" ON public.prep_progress
  FOR SELECT USING (auth.uid() = user_id);

-- The old counter RPCs were SECURITY DEFINER and executable by anon, i.e. an
-- unauthenticated upvote-inflation endpoint. Replaced by toggle_upvote (next
-- migration); dropped here so they stop being callable immediately.
DROP FUNCTION IF EXISTS public.increment_upvotes(uuid);
DROP FUNCTION IF EXISTS public.decrement_upvotes(uuid);
