import logging
import os

from src.config.supabase import auth_client, supabase
from src.dependencies.exceptions import AppError
from src.schemas.auth_schema import (
    RegisterSchema,
    LoginSchema,
    RefreshSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    ResendVerificationSchema,
)
from src.services.auth_helpers import (
    rollback_auth_user,
    sync_user_metadata_role,
    get_user_role,
    is_user_banned,
)

logger = logging.getLogger(__name__)


def register(data: RegisterSchema) -> dict:
    user_id = None
    try:
        response = auth_client().auth.sign_up({
            "email":    data.email,
            "password": data.password,
            "options":  {"data": {"role": "user"}},
        })

        if response.user is None:
            raise AppError(400, {"error": "Registration failed"})

        user_id = response.user.id
        sync_user_metadata_role(user_id, "user")

        try:
            supabase.table("users").insert({
                "id":                  user_id,
                "email":               data.email,
                "role":                "user",
                "onboarding_complete": False,
            }).execute()
        except Exception:
            rollback_auth_user(user_id)
            logger.exception("public.users insert failed during registration")
            raise AppError(500, {"error": "Registration failed"})

        return {
            "message": "Registration successful. Please check your email to verify your account.",
            "user_id": user_id,
        }

    except AppError:
        raise
    except Exception as e:
        if user_id:
            rollback_auth_user(user_id)
        msg = str(e).lower()
        if "already registered" in msg or "already been registered" in msg:
            raise AppError(409, {"error": "Email already registered"})
        logger.exception("Registration failed")
        raise AppError(500, {"error": "Registration failed"})


def login(data: LoginSchema) -> dict:
    try:
        response = auth_client().auth.sign_in_with_password({
            "email":    data.email,
            "password": data.password,
        })

        if response.session is None:
            raise AppError(401, {"error": "Invalid credentials"})

        if is_user_banned(response.user.id):
            raise AppError(403, {"error": "Account suspended"})

        role = get_user_role(response.user.id)

        return {
            "access_token":  response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": {
                "id":    response.user.id,
                "email": response.user.email,
                "role":  role,
            },
        }

    except AppError:
        raise
    except Exception as e:
        msg = str(e).lower()
        if "invalid login" in msg or "invalid credentials" in msg:
            raise AppError(401, {"error": "Invalid email or password"})
        if "email not confirmed" in msg:
            raise AppError(403, {"error": "Please verify your email before logging in"})
        if "banned" in msg or "user is banned" in msg:
            raise AppError(403, {"error": "Account suspended"})
        logger.exception("Login failed")
        raise AppError(500, {"error": "Login failed"})


def refresh(data: RefreshSchema) -> dict:
    """Swap a refresh token for a new session. Supabase rotates the refresh token,
    so the client must store the new one."""
    try:
        response = auth_client().auth.refresh_session(data.refresh_token)
    except Exception:
        raise AppError(401, {"error": "Session expired, please log in again"})

    if response.session is None or response.user is None:
        raise AppError(401, {"error": "Session expired, please log in again"})
    if is_user_banned(response.user.id):
        raise AppError(403, {"error": "Account suspended"})

    return {
        "access_token":  response.session.access_token,
        "refresh_token": response.session.refresh_token,
    }


def logout(user: dict) -> dict:
    token = user.get("token", "")
    try:
        if token:
            supabase.auth.admin.sign_out(token, scope="global")
    except Exception:
        logger.warning("Logout sign_out failed for user %s", user.get("sub"))

    return {"message": "Logged out successfully"}


def resend_verification(data: ResendVerificationSchema) -> dict:
    try:
        auth_client().auth.resend({"type": "signup", "email": data.email})
    except Exception:
        pass

    return {
        "message": "If this email is registered, a verification link has been sent."
    }


def forgot_password(data: ForgotPasswordSchema) -> dict:
    # Without redirect_to Supabase sends users to the Site URL root, where the
    # SPA bounces them to /login and the recovery token in the hash is lost.
    # The URL must also be in Supabase Auth → URL Configuration → Redirect URLs.
    redirect_to = f"{os.getenv('APP_URL', 'http://localhost:5173').rstrip('/')}/reset-password"
    try:
        auth_client().auth.reset_password_email(data.email, {"redirect_to": redirect_to})
    except Exception:
        pass

    return {
        "message": "If this email is registered, a password reset link has been sent."
    }


# Sessions from these flows already proved control of the inbox, which is what
# the current password would prove. Everything else must re-enter it, so a
# stolen access token alone can't lock the owner out.
_INBOX_PROVEN = {"recovery", "otp", "magiclink"}


def reset_password(user: dict, data: ResetPasswordSchema) -> dict:
    if not _INBOX_PROVEN.intersection(user.get("amr", [])):
        if not data.current_password:
            raise AppError(400, {"errors": {"current_password": ["is required"]}})
        try:
            auth_client().auth.sign_in_with_password({
                "email":    user.get("email") or "",
                "password": data.current_password,
            })
        except Exception:
            # 400, not 401: the frontend logs out on 401.
            raise AppError(400, {"error": "Current password is incorrect"})

    try:
        supabase.auth.admin.update_user_by_id(
            user["sub"], {"password": data.password}
        )
        return {"message": "Password reset successful"}
    except Exception:
        raise AppError(
            400,
            {"error": "Password reset failed. Link may be invalid or expired."},
        )
