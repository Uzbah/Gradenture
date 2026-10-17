-- ============================================================
-- Gradenture — atomic upvote toggle
-- ============================================================
-- Replaces the read-then-write toggle in the API (racy: two clicks could both
-- insert or both increment) and refuses non-approved questions. The question
-- row lock serialises toggles per question, and the counter is recomputed from
-- question_upvotes so it can never drift.
-- Returns NULL when the question is missing or not approved (API → 404).

CREATE OR REPLACE FUNCTION public.toggle_upvote(qid uuid, uid uuid)
RETURNS jsonb
LANGUAGE plpgsql
SET search_path = public
AS $$
DECLARE
  did_upvote boolean;
  total      integer;
BEGIN
  PERFORM 1 FROM interview_questions WHERE id = qid AND status = 'approved' FOR UPDATE;
  IF NOT FOUND THEN
    RETURN NULL;
  END IF;

  DELETE FROM question_upvotes WHERE question_id = qid AND user_id = uid;
  did_upvote := NOT FOUND;
  IF did_upvote THEN
    INSERT INTO question_upvotes (question_id, user_id) VALUES (qid, uid);
  END IF;

  SELECT count(*) INTO total FROM question_upvotes WHERE question_id = qid;
  UPDATE interview_questions SET upvotes = total WHERE id = qid;

  RETURN jsonb_build_object('upvoted', did_upvote, 'upvotes', total);
END;
$$;

-- Service role only (the backend). Supabase's default privileges grant new
-- functions to anon/authenticated, so revoke explicitly.
REVOKE ALL ON FUNCTION public.toggle_upvote(uuid, uuid) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.toggle_upvote(uuid, uuid) TO service_role;

-- Heal any drift the old racy toggle left behind.
UPDATE public.interview_questions q
SET upvotes = (SELECT count(*) FROM public.question_upvotes u WHERE u.question_id = q.id)
WHERE upvotes <> (SELECT count(*) FROM public.question_upvotes u WHERE u.question_id = q.id);
