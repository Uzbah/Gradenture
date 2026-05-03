import re
from flask import jsonify, request, g
from src.config.supabase import supabase


def _clean(text: str) -> str:
    return re.sub(r"<[^>]*>", "", text)


def _own_or_404(app_id: str, user_id: str):
    result = (supabase.table("applications")
              .select("*")
              .eq("id", app_id)
              .eq("user_id", user_id)
              .maybe_single()
              .execute())
    return result.data


def list_applications():
    """
    List current user's job applications.
    ---
    tags: [Applications]
    security:
      - Bearer: []
    parameters:
      - {in: query, name: page,   type: integer, default: 1}
      - {in: query, name: limit,  type: integer, default: 20}
      - {in: query, name: status, type: string}
    responses:
      200:
        description: List of applications
    """
    user_id = g.user["sub"]
    page    = max(1, int(request.args.get("page", 1)))
    limit   = min(50, max(1, int(request.args.get("limit", 20))))
    offset  = (page - 1) * limit

    query = (supabase.table("applications")
             .select("*", count="exact")
             .eq("user_id", user_id)
             .order("created_at", desc=True))

    status = request.args.get("status")
    if status:
        query = query.eq("status", status)

    result = query.range(offset, offset + limit - 1).execute()
    return jsonify({"data": result.data, "count": result.count}), 200


def get_application(app_id: str):
    """
    Get a single application (own only).
    ---
    tags: [Applications]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: app_id, type: string, required: true}
    responses:
      200:
        description: Application detail
      404:
        description: Not found
    """
    app = _own_or_404(app_id, g.user["sub"])
    if not app:
        return jsonify({"error": "Application not found"}), 404
    return jsonify({"data": app}), 200


def create_application():
    """
    Create a new job application.
    ---
    tags: [Applications]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [company_name, role_title]
          properties:
            company_name: {type: string}
            role_title:   {type: string}
            status:       {type: string, enum: [applied, interview, offer, rejected, closed]}
            applied_date: {type: string}
            deadline:     {type: string}
            job_url:      {type: string}
            notes:        {type: string}
    responses:
      201:
        description: Application created
    """
    data = request.validated_data
    if data.get("notes"):
        data["notes"] = _clean(data["notes"])

    result = supabase.table("applications").insert({
        **data,
        "user_id": g.user["sub"],
    }).execute()

    return jsonify({"data": result.data[0]}), 201


def update_application(app_id: str):
    """
    Update an application (own only).
    ---
    tags: [Applications]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: app_id, type: string, required: true}
    responses:
      200:
        description: Application updated
      404:
        description: Not found
    """
    if not _own_or_404(app_id, g.user["sub"]):
        return jsonify({"error": "Application not found"}), 404

    data = {k: v for k, v in request.validated_data.items() if v is not None}
    if "notes" in data:
        data["notes"] = _clean(data["notes"])

    result = (supabase.table("applications")
              .update(data)
              .eq("id", app_id)
              .execute())
    return jsonify({"data": result.data[0]}), 200


def delete_application(app_id: str):
    """
    Delete an application (own only).
    ---
    tags: [Applications]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: app_id, type: string, required: true}
    responses:
      200:
        description: Application deleted
      404:
        description: Not found
    """
    if not _own_or_404(app_id, g.user["sub"]):
        return jsonify({"error": "Application not found"}), 404

    supabase.table("applications").delete().eq("id", app_id).execute()
    return jsonify({"message": "Application deleted"}), 200
