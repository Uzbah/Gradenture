import re
from flask import jsonify, request, g
from src.config.supabase import supabase


def _clean(text: str) -> str:
    return re.sub(r"<[^>]*>", "", text)


def get_queue():
    """
    Get pending moderation queue.
    ---
    tags: [Admin]
    security:
      - Bearer: []
    responses:
      200:
        description: Pending questions and reviews
    """
    questions = (supabase.table("interview_questions")
                 .select("*")
                 .eq("status", "pending")
                 .order("created_at")
                 .execute()).data

    reviews = (supabase.table("interview_reviews")
               .select("*")
               .eq("status", "pending")
               .order("created_at")
               .execute()).data

    return jsonify({"data": {"questions": questions, "reviews": reviews}}), 200


def moderate_question(question_id: str):
    """
    Approve, reject, or request edit on a question.
    ---
    tags: [Admin]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: question_id, type: string, required: true}
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [status]
          properties:
            status:     {type: string, enum: [approved, rejected, needs_edit]}
            admin_note: {type: string}
    responses:
      200:
        description: Question moderated
    """
    body       = request.get_json(force=True, silent=True) or {}
    new_status = body.get("status")
    admin_note = _clean(body.get("admin_note", "") or "")

    if new_status not in ("approved", "rejected", "needs_edit"):
        return jsonify({"errors": {"status": ["must be approved, rejected, or needs_edit"]}}), 400

    q = (supabase.table("interview_questions")
         .select("submitted_by, status")
         .eq("id", question_id)
         .maybe_single()
         .execute())

    if not q.data:
        return jsonify({"error": "Question not found"}), 404

    supabase.table("interview_questions").update({
        "status":      new_status,
        "admin_note":  admin_note or None,
        "reviewed_by": g.user["sub"],
        "reviewed_at": "now()",
    }).eq("id", question_id).execute()

    return jsonify({"message": f"Question {new_status}"}), 200


def moderate_review(review_id: str):
    """
    Approve, reject, or request edit on a review.
    ---
    tags: [Admin]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: review_id, type: string, required: true}
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [status]
          properties:
            status:     {type: string, enum: [approved, rejected, needs_edit]}
            admin_note: {type: string}
    responses:
      200:
        description: Review moderated
    """
    body       = request.get_json(force=True, silent=True) or {}
    new_status = body.get("status")
    admin_note = _clean(body.get("admin_note", "") or "")

    if new_status not in ("approved", "rejected", "needs_edit"):
        return jsonify({"errors": {"status": ["must be approved, rejected, or needs_edit"]}}), 400

    r = (supabase.table("interview_reviews")
         .select("submitted_by")
         .eq("id", review_id)
         .maybe_single()
         .execute())

    if not r.data:
        return jsonify({"error": "Review not found"}), 404

    supabase.table("interview_reviews").update({
        "status":      new_status,
        "admin_note":  admin_note or None,
        "reviewed_by": g.user["sub"],
        "reviewed_at": "now()",
    }).eq("id", review_id).execute()

    return jsonify({"message": f"Review {new_status}"}), 200


def moderate_company(company_id: str):
    """
    Approve a submitted company.
    ---
    tags: [Admin]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: company_id, type: string, required: true}
    responses:
      200:
        description: Company approved
    """
    result = (supabase.table("companies")
              .update({"status": "approved"})
              .eq("id", company_id)
              .execute())
    if not result.data:
        return jsonify({"error": "Company not found"}), 404
    return jsonify({"message": "Company approved"}), 200


def list_users():
    """
    List all users.
    ---
    tags: [Admin]
    security:
      - Bearer: []
    parameters:
      - {in: query, name: page,  type: integer, default: 1}
      - {in: query, name: limit, type: integer, default: 20}
    responses:
      200:
        description: List of users
    """
    page   = max(1, int(request.args.get("page", 1)))
    limit  = min(50, max(1, int(request.args.get("limit", 20))))
    offset = (page - 1) * limit

    result = (supabase.table("users")
              .select("*", count="exact")
              .order("created_at", desc=True)
              .range(offset, offset + limit - 1)
              .execute())
    return jsonify({"data": result.data, "count": result.count}), 200


def update_user_role(user_id: str):
    """
    Change a user's role (super_admin only).
    ---
    tags: [Admin]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: user_id, type: string, required: true}
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [role]
          properties:
            role: {type: string, enum: [user, admin, super_admin]}
    responses:
      200:
        description: Role updated
    """
    body = request.get_json(force=True, silent=True) or {}
    role = body.get("role")
    if role not in ("user", "admin", "super_admin"):
        return jsonify({"errors": {"role": ["must be user, admin, or super_admin"]}}), 400

    supabase.table("users").update({"role": role}).eq("id", user_id).execute()
    supabase.auth.admin.update_user_by_id(user_id, {"user_metadata": {"role": role}})
    return jsonify({"message": f"Role updated to {role}"}), 200


def warn_user(user_id: str):
    """
    Warn a user.
    ---
    tags: [Admin]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: user_id, type: string, required: true}
    responses:
      200:
        description: User warned
    """
    user = supabase.table("users").select("id").eq("id", user_id).maybe_single().execute()
    if not user.data:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User warned"}), 200


def suspend_user(user_id: str):
    """
    Suspend a user (bans them from auth).
    ---
    tags: [Admin]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: user_id, type: string, required: true}
    responses:
      200:
        description: User suspended
    """
    user = supabase.table("users").select("id").eq("id", user_id).maybe_single().execute()
    if not user.data:
        return jsonify({"error": "User not found"}), 404

    supabase.auth.admin.update_user_by_id(user_id, {"ban_duration": "876600h"})
    return jsonify({"message": "User suspended"}), 200
