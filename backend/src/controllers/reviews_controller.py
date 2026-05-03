import re
from flask import jsonify, request, g
from src.config.supabase import supabase


def _clean(text: str) -> str:
    return re.sub(r"<[^>]*>", "", text)


def _sanitize(r: dict, is_admin: bool = False) -> dict:
    if not is_admin and r.get("is_anonymous"):
        r.pop("submitted_by", None)
    return r


def list_reviews():
    """
    List approved reviews.
    ---
    tags: [Reviews]
    parameters:
      - {in: query, name: page,       type: integer, default: 1}
      - {in: query, name: limit,      type: integer, default: 20}
      - {in: query, name: company_id, type: string}
      - {in: query, name: domain_id,  type: string}
    responses:
      200:
        description: List of reviews
    """
    page   = max(1, int(request.args.get("page", 1)))
    limit  = min(50, max(1, int(request.args.get("limit", 20))))
    offset = (page - 1) * limit

    query = (supabase.table("interview_reviews")
             .select("*", count="exact")
             .eq("status", "approved")
             .order("created_at", desc=True))

    for field in ("company_id", "domain_id"):
        val = request.args.get(field)
        if val:
            query = query.eq(field, val)

    result = query.range(offset, offset + limit - 1).execute()
    data   = [_sanitize(r) for r in result.data]
    return jsonify({"data": data, "count": result.count}), 200


def get_review(review_id: str):
    """
    Get a single approved review.
    ---
    tags: [Reviews]
    parameters:
      - {in: path, name: review_id, type: string, required: true}
    responses:
      200:
        description: Review detail
      404:
        description: Not found
    """
    result = (supabase.table("interview_reviews")
              .select("*")
              .eq("id", review_id)
              .eq("status", "approved")
              .maybe_single()
              .execute())

    if not result.data:
        return jsonify({"error": "Review not found"}), 404
    return jsonify({"data": _sanitize(result.data)}), 200


def submit_review():
    """
    Submit an interview review.
    ---
    tags: [Reviews]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [company_id, role_title, review_text, interview_date]
          properties:
            company_id:     {type: string}
            domain_id:      {type: string}
            role_title:     {type: string}
            review_text:    {type: string, minLength: 50}
            interview_date: {type: string, description: "YYYY-MM-01"}
            difficulty:     {type: string, enum: [easy, medium, hard]}
            outcome:        {type: string, enum: [offer, rejected, ghosted, withdrew, pending]}
            is_anonymous:   {type: boolean}
    responses:
      201:
        description: Review submitted for review
    """
    data = request.validated_data

    result = supabase.table("interview_reviews").insert({
        **data,
        "review_text":  _clean(data["review_text"]),
        "submitted_by": g.user["sub"],
        "status":       "pending",
    }).execute()

    return jsonify({"id": result.data[0]["id"], "status": "pending",
                    "message": "Review submitted for moderation"}), 201


def flag_review(review_id: str):
    """
    Flag a review for moderation.
    ---
    tags: [Reviews]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: review_id, type: string, required: true}
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
        "content_type": "review",
        "content_id":   review_id,
        "reason":       data["reason"],
    }).execute()
    return jsonify({"message": "Flagged for review"}), 201
