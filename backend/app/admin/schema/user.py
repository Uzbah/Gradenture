from uuid import UUID

from pydantic import Field, field_validator

from backend.common.enums import SkillLevel, UserGoal, UserRole
from backend.common.schema import SchemaBase


class OnboardingParam(SchemaBase):
    """Finish onboarding: the answers that pick a roadmap."""

    domain_id: UUID = Field(description='Domain the user is preparing for')
    skill_level: SkillLevel = Field(description='Self-assessed level')
    goal: UserGoal = Field(description='What the user is working towards')
    university: str = Field(description='University attended')

    @field_validator('university')
    @classmethod
    def validate_university(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError('must be at least 2 characters')
        if len(v) > 100:
            raise ValueError('must be at most 100 characters')
        return v


class UpdateRoleParam(SchemaBase):
    """Change a user's platform role."""

    role: UserRole = Field(description='New role')


class GetUserDetail(SchemaBase):
    """A user profile."""

    id: str = Field(description='User ID')
    email: str = Field(description='Account email')
    role: UserRole = Field(description='Platform role')
    domain_id: str | None = Field(None, description='Chosen domain')
    skill_level: SkillLevel | None = Field(None, description='Self-assessed level')
    goal: UserGoal | None = Field(None, description='Stated goal')
    university: str | None = Field(None, description='University attended')
    onboarding_complete: bool = Field(False, description='Whether onboarding is finished')
    suspended_at: str | None = Field(None, description='When the account was suspended, if it is')
    created_at: str | None = Field(None, description='When the account was created')


class OnboardingDetail(SchemaBase):
    """Acknowledgement of a completed onboarding."""

    message: str = Field(description='Confirmation')
    onboarding_complete: bool = Field(description='Always true')


class GetDomainDetail(SchemaBase):
    """A career domain users can choose from."""

    id: str = Field(description='Domain ID')
    name: str = Field(description='Display name')
    slug: str = Field(description='URL-safe name, which keys the prep roadmaps')
