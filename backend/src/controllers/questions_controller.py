import re
from flask import jsonify, request, g
from src.config.supabase import supabase


def _clean(text: str) -> str:
    return re.sub(r"<[^>]*>", "", text)


def _sanitize(q: dict, is_admin: bool = False) -> dict:
    if not is_admin and q.get("is_anonymous"):
        q.pop("submitted_by", None)
    return q


def list_questions():
    """
    List approved questions.
    ---
    tags: [Questions]
    parameters:
      - {in: query, name: page,          type: integer, default: 1}
      - {in: query, name: limit,         type: integer, default: 20}
      - {in: query, name: domain_id,     type: string}
      - {in: query, name: company_id,    type: string}
      - {in: query, name: difficulty,    type: string}
      - {in: query, name: question_type, type: string}
    responses:
      200:
        description: List of questions
    """
    page   = max(1, int(request.args.get("page", 1)))
    limit  = min(50, max(1, int(request.args.get("limit", 20))))
    offset = (page - 1) * limit

    query = (supabase.table("interview_questions")
             .select("*", count="exact")
             .eq("status", "approved")
             .order("created_at", desc=True))

    for field in ("domain_id", "company_id", "difficulty", "question_type"):
        val = request.args.get(field)
        if val:
            query = query.eq(field, val)

    result = query.range(offset, offset + limit - 1).execute()
    data   = [_sanitize(q) for q in result.data]
    return jsonify({"data": data, "count": result.count}), 200


def get_question(question_id: str):
    """
    Get a single approved question.
    ---
    tags: [Questions]
    parameters:
      - {in: path, name: question_id, type: string, required: true}
    responses:
      200:
        description: Question detail
      404:
        description: Not found
    """
    result = (supabase.table("interview_questions")
              .select("*")
              .eq("id", question_id)
              .eq("status", "approved")
              .maybe_single()
              .execute())

    if not result.data:
        return jsonify({"error": "Question not found"}), 404
    return jsonify({"data": _sanitize(result.data)}), 200


def submit_question():
    """
    Submit a new interview question.
    ---
    tags: [Questions]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [domain_id, company_id, role_title, question_text, question_type, difficulty, asked_date]
          properties:
            domain_id:     {type: string}
            company_id:    {type: string}
            role_title:    {type: string}
            question_text: {type: string, minLength: 20}
            question_type: {type: string, enum: [technical, behavioural, hr, case_study]}
            difficulty:    {type: string, enum: [easy, medium, hard]}
            asked_date:    {type: string, description: "YYYY-MM-01"}
            notes:         {type: string}
            is_anonymous:  {type: boolean}
    responses:
      201:
        description: Question submitted for review
    """
    data = request.validated_data

    result = supabase.table("interview_questions").insert({
        **data,
        "question_text": _clean(data["question_text"]),
        "notes":         _clean(data["notes"]) if data.get("notes") else None,
        "submitted_by":  g.user["sub"],
        "status":        "pending",
    }).execute()

    return jsonify({"id": result.data[0]["id"], "status": "pending",
                    "message": "Question submitted for review"}), 201


def upvote_question(question_id: str):
    """
    Toggle upvote on a question.
    ---
    tags: [Questions]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: question_id, type: string, required: true}
    responses:
      200:
        description: Upvote toggled
    """
    user_id = g.user["sub"]

    existing = (supabase.table("question_upvotes")
                .select("question_id")
                .eq("question_id", question_id)
                .eq("user_id", user_id)
                .maybe_single()
                .execute())

    if existing.data:
        supabase.table("question_upvotes").delete().eq("question_id", question_id).eq("user_id", user_id).execute()
        supabase.rpc("decrement_upvotes", {"qid": question_id}).execute()
        upvoted = False
    else:
        supabase.table("question_upvotes").insert({"question_id": question_id, "user_id": user_id}).execute()
        supabase.rpc("increment_upvotes", {"qid": question_id}).execute()
        upvoted = True

    q = supabase.table("interview_questions").select("upvotes").eq("id", question_id).single().execute()
    return jsonify({"upvoted": upvoted, "upvotes": q.data["upvotes"]}), 200


def flag_question(question_id: str):
    """
    Flag a question for review.
    ---
    tags: [Questions]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: question_id, type: string, required: true}
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [reason]
          properties:
            reason: {type: string}
    responses:
      201:
        description: Flag submitted
    """
    data = request.validated_data
    supabase.table("content_flags").insert({
        "reported_by":  g.user["sub"],
        "content_type": "question",
        "content_id":   question_id,
        "reason":       data["reason"],
    }).execute()
    return jsonify({"message": "Flagged for review"}), 201
