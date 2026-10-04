from pydantic import Field

from backend.common.enums import CompanyStatus
from backend.common.schema import SchemaBase


class CompanySchemaBase(SchemaBase):
    """The editable profile of a company."""

    name: str = Field(description='Company name')
    website: str | None = Field(None, description='Company website')
    industry: str | None = Field(None, description='Industry the company operates in')


class CreateCompanyParam(CompanySchemaBase):
    """Submit a company to the registry, for an admin to approve."""


class RequestCompanyEditParam(SchemaBase):
    """Changes a company manager proposes to their own company's profile.

    Deliberately excludes `status`: a manager can never approve their own company,
    and never touches the questions and reviews written about it.
    """

    name: str | None = Field(None, description='Proposed name')
    website: str | None = Field(None, description='Proposed website')
    industry: str | None = Field(None, description='Proposed industry')
    logo_url: str | None = Field(None, description='Proposed logo URL')


class GetCompanyDetail(SchemaBase):
    """A company as returned to a reader."""

    id: str = Field(description='Company ID')
    name: str = Field(description='Company name')
    slug: str = Field(description='URL-safe name')
    website: str | None = Field(None, description='Company website')
    industry: str | None = Field(None, description='Industry')
    logo_url: str | None = Field(None, description='Logo URL')
    status: CompanyStatus = Field(description='Registry status')
    created_at: str | None = Field(None, description='When it was added')


class SubmittedDetail(SchemaBase):
    """Acknowledgement for anything that enters the moderation queue."""

    id: str = Field(description='ID of the submitted record')
    status: str = Field(description='Its status, always pending on submission')
    message: str = Field(description='What happens next')
