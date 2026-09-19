from pydantic import Field, field_validator

from backend.common.enums import ApplicationStatus
from backend.common.schema import SchemaBase


class ApplicationSchemaBase(SchemaBase):
    """One row of a user's private application tracker."""

    company_name: str = Field(description='Company applied to, free text')
    role_title: str = Field(description='Role applied for')
    status: ApplicationStatus = Field(ApplicationStatus.APPLIED, description='Kanban column')
    applied_date: str | None = Field(None, description='Date applied')
    deadline: str | None = Field(None, description='Application deadline')
    job_url: str | None = Field(None, description='Link to the posting')
    notes: str | None = Field(None, description='Private notes')

    @field_validator('company_name', 'role_title')
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('must not be empty')
        return v.strip()


class CreateApplicationParam(ApplicationSchemaBase):
    """Add an application to the tracker."""


class UpdateApplicationParam(SchemaBase):
    """Change an application. Every field is optional; omitted fields are left alone."""

    company_name: str | None = Field(None, description='Company applied to')
    role_title: str | None = Field(None, description='Role applied for')
    status: ApplicationStatus | None = Field(None, description='Kanban column')
    applied_date: str | None = Field(None, description='Date applied')
    deadline: str | None = Field(None, description='Application deadline')
    job_url: str | None = Field(None, description='Link to the posting')
    notes: str | None = Field(None, description='Private notes')


class GetApplicationDetail(ApplicationSchemaBase):
    """An application as stored."""

    id: str = Field(description='Application ID')
    user_id: str = Field(description='Owner')
    created_at: str = Field(description='When it was added')
