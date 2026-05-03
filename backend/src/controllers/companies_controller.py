import re
from flask import jsonify, request, g
from src.config.supabase import supabase


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def list_companies():
    """
    List approved companies.
    ---
    tags: [Companies]
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: limit
        type: integer
        default: 20
    responses:
      200:
        description: List of companies
    """
    page  = max(1, int(request.args.get("page", 1)))
    limit = min(50, max(1, int(request.args.get("limit", 20))))
    offset = (page - 1) * limit

    result = (supabase.table("companies")
              .select("*", count="exact")
              .eq("status", "approved")
              .order("name")
              .range(offset, offset + limit - 1)
              .execute())

    return jsonify({"data": result.data, "count": result.count}), 200


def get_company(company_id: str):
    """
    Get a single approved company.
    ---
    tags: [Companies]
    parameters:
      - in: path
        name: company_id
        type: string
        required: true
    responses:
      200:
        description: Company details
      404:
        description: Not found
    """
    result = (supabase.table("companies")
              .select("*")
              .eq("id", company_id)
              .eq("status", "approved")
              .maybe_single()
              .execute())

    if not result.data:
        return jsonify({"error": "Company not found"}), 404
    return jsonify({"data": result.data}), 200


def submit_company():
    """
    Submit a new company for review.
    ---
    tags: [Companies]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [name]
          properties:
            name:
              type: string
            website:
              type: string
            industry:
              type: string
    responses:
      201:
        description: Company submitted
      400:
        description: Validation error
    """
    data = request.validated_data
    name = data["name"].strip()
    if not name:
        return jsonify({"errors": {"name": ["must not be empty"]}}), 400

    existing = (supabase.table("companies")
                .select("id")
                .ilike("name", name)
                .maybe_single()
                .execute())
    if existing.data:
        return jsonify({"error": "Company already exists"}), 409

    result = supabase.table("companies").insert({
        "name":     name,
        "slug":     _slug(name),
        "website":  data.get("website"),
        "industry": data.get("industry"),
        "status":   "pending",
    }).execute()

    return jsonify({"id": result.data[0]["id"], "status": "pending",
                    "message": "Company submitted for review"}), 201
