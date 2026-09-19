from pydantic import EmailStr, Field, field_validator

from backend.common.enums import UserRole
from backend.common.schema import SchemaBase

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


def _normalize_email(v: object) -> object:
    """Fold case and trim, so one address is one account."""
    return v.strip().lower() if isinstance(v, str) else v


def _validate_password(v: str) -> str:
    if len(v) < MIN_PASSWORD_LENGTH:
        raise ValueError(f'must be at least {MIN_PASSWORD_LENGTH} characters')
    if len(v) > MAX_PASSWORD_LENGTH:
        raise ValueError(f'must be at most {MAX_PASSWORD_LENGTH} characters')
    return v


class EmailParam(SchemaBase):
    """Base for the parameters that are just an address."""

    email: EmailStr = Field(description='Account email address')

    @field_validator('email', mode='before')
    @classmethod
    def normalize_email(cls, v: object) -> object:
        return _normalize_email(v)


class RegisterParam(EmailParam):
    """Create an account."""

    password: str = Field(description='Account password')

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password(v)


class LoginParam(EmailParam):
    """Exchange credentials for a session."""

    password: str = Field(description='Account password')


class ForgotPasswordParam(EmailParam):
    """Request a password reset link."""


class ResendVerificationParam(EmailParam):
    """Request another verification email."""


class ResetPasswordParam(SchemaBase):
    """Set a new password, authenticated by the recovery token."""

    password: str = Field(description='New password')

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password(v)


class RegisterDetail(SchemaBase):
    """What a new account gets back."""

    message: str = Field(description='What happens next')
    user_id: str = Field(description='New user ID')


class LoginUserDetail(SchemaBase):
    """The identity carried in a login response."""

    id: str = Field(description='User ID')
    email: str | None = Field(None, description='Account email')
    role: UserRole = Field(description='Platform role')


class LoginDetail(SchemaBase):
    """A session."""

    access_token: str = Field(description='Supabase access token, sent as a bearer token')
    refresh_token: str = Field(description='Supabase refresh token')
    user: LoginUserDetail = Field(description='Who signed in')
