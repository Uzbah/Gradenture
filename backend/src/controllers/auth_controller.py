from flask import jsonify, request
from pydantic import ValidationError

from src.config.supabase import supabase
from src.schemas.auth_schema import (
    RegisterSchema, LoginSchema, ForgotPasswordSchema, ResetPasswordSchema
)


def register():
    """
    Register a new user.
    ---
    tags: [Auth]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [email, password]
          properties:
            email:
              type: string
              format: email
            password:
              type: string
              minLength: 8
    responses:
      201:
        description: Registration successful — verification email sent
      400:
        description: Validation error
      409:
        description: Email already registered
    """
    body = request.get_json(force=True, silent=True) or {}
    try:
        data = RegisterSchema(**body)
    except ValidationError as e:
        errors = {err["loc"][0]: [err["msg"]] for err in e.errors()}
        return jsonify({"errors": errors}), 400

    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
        })

        if response.user is None:
            return jsonify({"error": "Registration failed"}), 400

        # Create the public.users row immediately on signup
        supabase.table("users").insert({
            "id":                  response.user.id,
            "email":               data.email,
            "role":                "user",
            "onboarding_complete": False,
        }).execute()

        return jsonify({
            "message": "Registration successful. Please check your email to verify your account.",
            "user_id": response.user.id,
        }), 201

    except Exception as e:
        msg = str(e).lower()
        if "already registered" in msg or "already been registered" in msg:
            return jsonify({"error": "Email already registered"}), 409
        return jsonify({"error": "Registration failed", "detail": str(e)}), 500


def login():
    """
    Log in with email and password.
    ---
    tags: [Auth]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [email, password]
          properties:
            email:
              type: string
              format: email
            password:
              type: string
    responses:
      200:
        description: Login successful — returns JWT
      400:
        description: Validation error
      401:
        description: Invalid credentials
      403:
        description: Email not verified
    """
    body = request.get_json(force=True, silent=True) or {}
    try:
        data = LoginSchema(**body)
    except ValidationError as e:
        errors = {err["loc"][0]: [err["msg"]] for err in e.errors()}
        return jsonify({"errors": errors}), 400

    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password,
        })

        if response.session is None:
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify({
            "access_token":  response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": {
                "id":    response.user.id,
                "email": response.user.email,
                "role":  response.user.user_metadata.get("role", "user"),
            },
        }), 200

    except Exception as e:
        msg = str(e).lower()
        if "invalid login" in msg or "invalid credentials" in msg:
            return jsonify({"error": "Invalid email or password"}), 401
        if "email not confirmed" in msg:
            return jsonify({"error": "Please verify your email before logging in"}), 403
        return jsonify({"error": "Login failed"}), 500


def logout():
    """
    Log out the current user.
    ---
    tags: [Auth]
    security:
      - Bearer: []
    responses:
      200:
        description: Logged out successfully
      401:
        description: Unauthorized
    """
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    return jsonify({"message": "Logged out successfully"}), 200


def resend_verification():
    """
    Resend the email verification link.
    ---
    tags: [Auth]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [email]
          properties:
            email:
              type: string
              format: email
    responses:
      200:
        description: Verification email sent (or silently ignored if email not found)
    """
    body = request.get_json(force=True, silent=True) or {}
    email = str(body.get("email", "")).strip()

    if not email:
        return jsonify({"errors": {"email": ["Email is required"]}}), 400

    try:
        supabase.auth.resend({"type": "signup", "email": email})
    except Exception:
        pass  # Never reveal whether the email exists

    return jsonify({
        "message": "If this email is registered, a verification link has been sent."
    }), 200


def forgot_password():
    """
    Send a password reset email.
    ---
    tags: [Auth]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [email]
          properties:
            email:
              type: string
              format: email
    responses:
      200:
        description: Reset email sent (or silently ignored if email not found)
      400:
        description: Validation error
    """
    body = request.get_json(force=True, silent=True) or {}
    try:
        data = ForgotPasswordSchema(**body)
    except ValidationError as e:
        errors = {err["loc"][0]: [err["msg"]] for err in e.errors()}
        return jsonify({"errors": errors}), 400

    try:
        supabase.auth.reset_password_email(data.email)
    except Exception:
        pass  # Never reveal whether the email exists

    return jsonify({
        "message": "If this email is registered, a password reset link has been sent."
    }), 200


def reset_password():
    """
    Reset password using the token from the reset email.
    ---
    tags: [Auth]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [password]
          properties:
            password:
              type: string
              minLength: 8
    responses:
      200:
        description: Password reset successful
      400:
        description: Validation error or invalid/expired token
      401:
        description: Unauthorized
    """
    body = request.get_json(force=True, silent=True) or {}
    try:
        data = ResetPasswordSchema(**body)
    except ValidationError as e:
        errors = {err["loc"][0]: [err["msg"]] for err in e.errors()}
        return jsonify({"errors": errors}), 400

    try:
        supabase.auth.update_user({"password": data.password})
        return jsonify({"message": "Password reset successful"}), 200
    except Exception:
        return jsonify({"error": "Password reset failed. Link may be invalid or expired."}), 400
