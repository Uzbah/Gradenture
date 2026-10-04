from pydantic import Field

from backend.common.schema import SchemaBase


class ResumeAnalysisDetail(SchemaBase):
    """The model's assessment of an uploaded resume."""

    score: int = Field(description='Overall quality, 1-10')
    summary: str = Field(description='Two or three sentence assessment')
    strengths: list[str] = Field([], description='Specific strengths')
    weaknesses: list[str] = Field([], description='Specific weaknesses')
    improvements: list[str] = Field([], description='Concrete suggestions')
    keyword_gaps: list[str] = Field([], description='Job-description keywords missing from the resume')
