-- ============================================================
-- CareerBridge — atomic write RPCs
-- ============================================================
-- PostgREST gives the backend no client-side transaction: each .update() /
-- .insert() is its own statement over its own connection. Every multi-statement
-- write below used to be a sequence of those, so a failure between them left the
-- database half-updated — content moderated with no audit row, a company merged
-- but not deleted, an upvote row with no counter change.
--
-- Each function here does the whole write in one statement from the client's
-- point of view, so it commits or rolls back as a unit. They are SECURITY
-- DEFINER because the tables are deny-by-default under RLS; authorization is
-- already enforced in the API layer before any of these is called.

-- Slug used for company names. Mirrors _slug() in the Python company service:
-- lowercase, runs of non-alphanumerics to a single dash, no leading or trailing dash.
CREATE OR REPLACE FUNCTION public.company_slug(p_name text)
RETURNS text AS $$
  SELECT trim(both '-' from regexp_replace(lower(p_name), '[^a-z0-9]+', '-', 'g'));
$$ LANGUAGE sql IMMUTABLE;


-- Toggle an upvote and return the new state.
-- Replaces: select existing -> insert/delete -> increment/decrement RPC -> re-select,
-- four round-trips whose counter could drift from the upvote rows.
CREATE OR REPLACE FUNCTION public.toggle_question_upvote(p_question_id uuid, p_user_id uuid)
RETURNS TABLE (upvoted boolean, upvotes integer) AS $$
DECLARE
  v_deleted integer;
  v_upvotes integer;
BEGIN
  DELETE FROM public.question_upvotes
   WHERE question_id = p_question_id AND user_id = p_user_id;

  GET DIAGNOSTICS v_deleted = ROW_COUNT;

  IF v_deleted > 0 THEN
    UPDATE public.interview_questions
       SET upvotes = GREATEST(interview_questions.upvotes - 1, 0)
     WHERE id = p_question_id
    RETURNING interview_questions.upvotes INTO v_upvotes;
  ELSE
    INSERT INTO public.question_upvotes (question_id, user_id)
    VALUES (p_question_id, p_user_id);

    UPDATE public.interview_questions
       SET upvotes = interview_questions.upvotes + 1
     WHERE id = p_question_id
    RETURNING interview_questions.upvotes INTO v_upvotes;
  END IF;

  IF v_upvotes IS NULL THEN
    RAISE EXCEPTION 'question % not found', p_question_id USING ERRCODE = 'no_data_found';
  END IF;

  RETURN QUERY SELECT v_deleted = 0, v_upvotes;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Moderate a question or review and record the decision in one transaction.
-- Returns false when nothing matched, so the caller can raise 404.
CREATE OR REPLACE FUNCTION public.moderate_content(
  p_kind       text,
  p_content_id uuid,
  p_status     text,
  p_admin_note text,
  p_actor      uuid
)
RETURNS boolean AS $$
DECLARE
  v_updated integer;
BEGIN
  IF p_kind NOT IN ('question', 'review') THEN
    RAISE EXCEPTION 'unknown content kind: %', p_kind USING ERRCODE = 'invalid_parameter_value';
  END IF;

  IF p_kind = 'question' THEN
    UPDATE public.interview_questions
       SET status = p_status, admin_note = p_admin_note, reviewed_by = p_actor, reviewed_at = now()
     WHERE id = p_content_id;
  ELSE
    UPDATE public.interview_reviews
       SET status = p_status, admin_note = p_admin_note, reviewed_by = p_actor, reviewed_at = now()
     WHERE id = p_content_id;
  END IF;

  GET DIAGNOSTICS v_updated = ROW_COUNT;

  IF v_updated = 0 THEN
    RETURN false;
  END IF;

  INSERT INTO public.admin_audit_log (actor_id, action, target_type, target_id, detail)
  VALUES (p_actor, p_kind || '_' || p_status, p_kind, p_content_id,
          jsonb_build_object('note', p_admin_note));

  RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Close a content flag and record who closed it.
CREATE OR REPLACE FUNCTION public.resolve_content_flag(
  p_flag_id uuid,
  p_status  text,
  p_actor   uuid
)
RETURNS boolean AS $$
DECLARE
  v_updated integer;
BEGIN
  UPDATE public.content_flags
     SET status = p_status
   WHERE id = p_flag_id AND status = 'open';

  GET DIAGNOSTICS v_updated = ROW_COUNT;

  IF v_updated = 0 THEN
    RETURN false;
  END IF;

  INSERT INTO public.admin_audit_log (actor_id, action, target_type, target_id)
  VALUES (p_actor, 'flag_' || p_status, 'flag', p_flag_id);

  RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Merge a duplicate company into another: repoint its content, delete it, audit it.
-- Returns null when either company is missing. Previously three separate writes,
-- so a failure could leave content repointed at a company that still existed, or
-- a deleted company whose questions had not moved.
CREATE OR REPLACE FUNCTION public.merge_company(p_from uuid, p_into uuid, p_actor uuid)
RETURNS jsonb AS $$
DECLARE
  v_from_name text;
  v_into_name text;
  v_questions integer;
  v_reviews   integer;
  v_detail    jsonb;
BEGIN
  IF p_from = p_into THEN
    RAISE EXCEPTION 'cannot merge a company into itself' USING ERRCODE = 'invalid_parameter_value';
  END IF;

  SELECT name INTO v_from_name FROM public.companies WHERE id = p_from;
  SELECT name INTO v_into_name FROM public.companies WHERE id = p_into;

  IF v_from_name IS NULL OR v_into_name IS NULL THEN
    RETURN NULL;
  END IF;

  UPDATE public.interview_questions SET company_id = p_into WHERE company_id = p_from;
  GET DIAGNOSTICS v_questions = ROW_COUNT;

  UPDATE public.interview_reviews SET company_id = p_into WHERE company_id = p_from;
  GET DIAGNOSTICS v_reviews = ROW_COUNT;

  DELETE FROM public.companies WHERE id = p_from;

  v_detail := jsonb_build_object(
    'merged_from', p_from,
    'merged_name', v_from_name,
    'into_name', v_into_name,
    'interview_questions', v_questions,
    'interview_reviews', v_reviews
  );

  INSERT INTO public.admin_audit_log (actor_id, action, target_type, target_id, detail)
  VALUES (p_actor, 'company_merged', 'company', p_into, v_detail);

  RETURN v_detail;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Decide a company profile edit request: apply the changes when approving, close
-- the request, and audit it. Returns null when there is no pending request.
CREATE OR REPLACE FUNCTION public.decide_company_edit(
  p_request_id uuid,
  p_status     text,
  p_admin_note text,
  p_actor      uuid
)
RETURNS jsonb AS $$
DECLARE
  v_company_id uuid;
  v_changes    jsonb;
  v_name       text;
BEGIN
  SELECT company_id, changes INTO v_company_id, v_changes
    FROM public.company_edit_requests
   WHERE id = p_request_id AND status = 'pending'
   FOR UPDATE;

  IF v_company_id IS NULL THEN
    RETURN NULL;
  END IF;

  IF p_status = 'approved' THEN
    v_name := btrim(v_changes ->> 'name');
    IF v_name IS NOT NULL AND v_name <> '' THEN
      v_changes := v_changes || jsonb_build_object('name', v_name, 'slug', public.company_slug(v_name));
    END IF;

    UPDATE public.companies AS c
       SET name     = COALESCE(v_changes ->> 'name', c.name),
           slug     = COALESCE(v_changes ->> 'slug', c.slug),
           website  = COALESCE(v_changes ->> 'website', c.website),
           industry = COALESCE(v_changes ->> 'industry', c.industry),
           logo_url = COALESCE(v_changes ->> 'logo_url', c.logo_url)
     WHERE c.id = v_company_id;
  END IF;

  UPDATE public.company_edit_requests
     SET status = p_status, admin_note = p_admin_note, reviewed_by = p_actor, reviewed_at = now()
   WHERE id = p_request_id;

  INSERT INTO public.admin_audit_log (actor_id, action, target_type, target_id, detail)
  VALUES (p_actor, 'company_edit_' || p_status, 'company', v_company_id,
          jsonb_build_object('request_id', p_request_id, 'changes', v_changes));

  RETURN jsonb_build_object('company_id', v_company_id, 'changes', v_changes);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- The two counter RPCs from migration 003 are superseded by
-- toggle_question_upvote; they are left in place so a rollback of the backend
-- does not break against a migrated database.
