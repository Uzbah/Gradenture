import bleach
from flask import jsonify, request, g
from pydantic import ValidationError

from src.config.supabase import supabase
from src.schemas.user import OnboardingSchema


def get_me():
    """
    Get current user profile.
    ---
    tags: [Users]
    security:
      - Bearer: []
    responses:
      200:
        description: User profile
        schema:
          type: object
          properties:
            data:
              type: object
      401:
        description: Unauthorized
      404:
        description: User not found
    """
    user_id = g.user["sub"]
    result = supabase.table("users").select("*").eq("id", user_id).maybe_single().execute()
    if not result.data:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"data": result.data}), 200


def get_domains():
    """
    List all domains.
    ---
    tags: [Domains]
    responses:
      200:
        description: List of domains
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  name:
                    type: string
                  slug:
                    type: string
            count:
              type: integer
    """
    result = supabase.table("domains").select("id, name, slug").order("name").execute()
    return jsonify({"data": result.data, "count": len(result.data)}), 200


def complete_onboarding():
    """
    Complete user onboarding (sets onboarding_complete = true).
    ---
    tags: [Users]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [domain_id, skill_level, goal, university]
          properties:
            domain_id:
              type: string
              format: uuid
            skill_level:
              type: string
              enum: [beginner, intermediate, advanced]
            goal:
              type: string
              enum: [first_job, switch_career, level_up, internship]
            university:
              type: string
              minLength: 2
              maxLength: 100
    responses:
      200:
        description: Onboarding complete
      400:
        description: Validation error
      401:
        description: Unauthorized
    """
    body = request.get_json(force=True, silent=True) or {}

    try:
        data = OnboardingSchema(**body)
    except ValidationError as e:
        errors = {err["loc"][0]: [err["msg"]] for err in e.errors()}
        return jsonify({"errors": errors}), 400

    clean_university = bleach.clean(data.university, tags=[], strip=True)

    supabase.table("users").upsert({
        "id":                  g.user["sub"],
        "email":               g.user["email"],
        "domain_id":           str(data.domain_id),
        "skill_level":         data.skill_level,
        "goal":                data.goal,
        "university":          clean_university,
        "onboarding_complete": True,
    }).execute()

    return jsonify({"message": "Onboarding complete", "onboarding_complete": True}), 200
