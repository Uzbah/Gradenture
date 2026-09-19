from backend.app.admin.crud.crud_user import user_dao
from backend.app.admin.schema.auth import (
    ForgotPasswordParam,
    LoginParam,
    RegisterParam,
    ResendVerificationParam,
    ResetPasswordParam,
)
from backend.common.dataclasses import CurrentUser
from backend.common.enums import UserRole
from backend.common.exception import errors
from backend.common.log import log
from backend.common.response.response_code import CustomErrorCode, StandardResponseCode
from backend.common.security.jwt import is_banned


class AuthService:
    """Registration and sessions, on top of Supabase Auth.

    Supabase owns credentials and tokens; public.users holds the profile and the
    authoritative role. Both sides have to be written, and they are not in the same
    database, so `create` compensates by hand when the second write fails — see the
    comment there.
    """

    @staticmethod
    def create(*, obj: RegisterParam) -> dict:
        """Register an account.

        :param obj: email and password
        """
        user_id = None
        try:
            response = user_dao.sign_up(obj.email, obj.password)
            if response.user is None:
                raise errors.RequestError(msg='Registration failed')

            user_id = response.user.id
            try:
                user_dao.sync_metadata_role(user_id, UserRole.USER)
            except Exception as exc:
                # A stale metadata mirror is recoverable; the authoritative role is
                # the one written to public.users below.
                log.warning('Failed to mirror role into user_metadata for {}: {}', user_id, exc)

            try:
                user_dao.create_profile(
                    {
                        'id': user_id,
                        'email': obj.email,
                        'role': UserRole.USER,
                        'onboarding_complete': False,
                    }
                )
            except Exception:
                # The auth user and the profile row live in different places, so
                # there is no transaction to roll back: delete the auth user by hand
                # rather than leave an account that can log in but has no profile.
                AuthService._rollback_auth_user(user_id)
                log.exception('public.users insert failed during registration')
                raise errors.ServerError(msg='Registration failed') from None

            return {
                'message': 'Registration successful. Please check your email to verify your account.',
                'user_id': user_id,
            }

        except errors.BaseExceptionError:
            raise
        except Exception as exc:
            if user_id:
                AuthService._rollback_auth_user(user_id)
            message = str(exc).lower()
            if 'already registered' in message or 'already been registered' in message:
                raise errors.ConflictError(msg='Email already registered') from exc
            log.exception('Registration failed')
            raise errors.ServerError(msg='Registration failed') from exc

    @staticmethod
    def _rollback_auth_user(user_id: str) -> None:
        """Remove the auth user after a failed registration, to avoid orphans."""
        try:
            user_dao.delete_auth_user(user_id)
        except Exception as exc:
            log.warning('Failed to roll back auth user {}: {}', user_id, exc)

    @staticmethod
    def login(*, obj: LoginParam) -> dict:
        """Exchange credentials for a session.

        :param obj: email and password
        """
        try:
            response = user_dao.sign_in(obj.email, obj.password)
            if response.session is None:
                raise errors.TokenError(msg='Invalid credentials')

            if is_banned(response.user.id):
                raise errors.CustomError(
                    error=CustomErrorCode.ACCOUNT_SUSPENDED,
                    http_code=StandardResponseCode.HTTP_403,
                )

            return {
                'access_token': response.session.access_token,
                'refresh_token': response.session.refresh_token,
                'user': {
                    'id': response.user.id,
                    'email': response.user.email,
                    'role': user_dao.get_role(response.user.id),
                },
            }

        except errors.BaseExceptionError:
            raise
        except errors.TokenError:
            raise
        except Exception as exc:
            message = str(exc).lower()
            if 'invalid login' in message or 'invalid credentials' in message:
                raise errors.TokenError(msg='Invalid email or password') from exc
            if 'email not confirmed' in message:
                raise errors.CustomError(
                    error=CustomErrorCode.EMAIL_NOT_VERIFIED,
                    http_code=StandardResponseCode.HTTP_403,
                ) from exc
            if 'banned' in message or 'user is banned' in message:
                raise errors.CustomError(
                    error=CustomErrorCode.ACCOUNT_SUSPENDED,
                    http_code=StandardResponseCode.HTTP_403,
                ) from exc
            log.exception('Login failed')
            raise errors.ServerError(msg='Login failed') from exc

    @staticmethod
    def logout(*, user: CurrentUser) -> None:
        """End the caller's sessions.

        A failure here is logged and swallowed: the client discards its token
        either way, and reporting an error would only invite a retry that cannot
        succeed.

        :param user: the caller
        """
        try:
            if user.token:
                user_dao.sign_out(user.token)
        except Exception as exc:
            log.warning('Sign-out failed for {}: {}', user.sub, exc)

    @staticmethod
    def resend_verification(*, obj: ResendVerificationParam) -> str:
        """Send another verification email.

        The reply is the same whether or not the address is registered, so this
        cannot be used to discover who has an account.

        :param obj: the address
        """
        try:
            user_dao.resend_verification(obj.email)
        except Exception as exc:
            log.warning('Verification resend failed: {}', exc)
        return 'If this email is registered, a verification link has been sent.'

    @staticmethod
    def forgot_password(*, obj: ForgotPasswordParam) -> str:
        """Send a password reset link.

        Same non-committal reply as above, for the same reason.

        :param obj: the address
        """
        try:
            user_dao.send_password_reset(obj.email)
        except Exception as exc:
            log.warning('Password reset email failed: {}', exc)
        return 'If this email is registered, a password reset link has been sent.'

    @staticmethod
    def reset_password(*, user: CurrentUser, obj: ResetPasswordParam) -> None:
        """Set a new password for the caller.

        The caller is authenticated by the recovery token Supabase put in the reset
        link, so reaching this point is itself the proof of ownership.

        :param user: the caller
        :param obj: the new password
        """
        try:
            user_dao.set_password(user.sub, obj.password)
        except Exception as exc:
            log.warning('Password reset failed for {}: {}', user.sub, exc)
            raise errors.RequestError(msg='Password reset failed. Link may be invalid or expired.') from exc


auth_service: AuthService = AuthService()
