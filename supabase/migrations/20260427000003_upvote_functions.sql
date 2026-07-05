-- Upvote counter RPCs used by the backend (questions_service)
CREATE OR REPLACE FUNCTION public.increment_upvotes(qid uuid)
RETURNS void AS $$
  UPDATE public.interview_questions SET upvotes = upvotes + 1 WHERE id = qid;
$$ LANGUAGE sql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.decrement_upvotes(qid uuid)
RETURNS void AS $$
  UPDATE public.interview_questions SET upvotes = GREATEST(upvotes - 1, 0) WHERE id = qid;
$$ LANGUAGE sql SECURITY DEFINER;
