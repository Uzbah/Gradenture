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


class ResetPasswordSchema(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("must be at most 128 characters")
        return v
