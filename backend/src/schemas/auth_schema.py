from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


def _normalize_email(v: object) -> object:
    if isinstance(v, str):
        return v.strip().lower()
    return v


class RegisterSchema(BaseModel):
    email:    EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: object) -> object:
        return _normalize_email(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("must be at most 128 characters")
        return v


class LoginSchema(BaseModel):
    email:    EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: object) -> object:
        return _normalize_email(v)


class ForgotPasswordSchema(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: object) -> object:
        return _normalize_email(v)


class ResendVerificationSchema(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: object) -> object:
        return _normalize_email(v)


class RefreshSchema(BaseModel):
    refresh_token: str

    @field_validator("refresh_token")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v.strip()


class ResetPasswordSchema(BaseModel):
    password: str
    # Required unless the session came from a recovery link (see auth_service).
    current_password: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("must be at most 128 characters")
        return v
