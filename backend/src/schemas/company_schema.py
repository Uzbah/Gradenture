from pydantic import BaseModel
from typing import Optional


class CompanySchema(BaseModel):
    name:     str
    website:  Optional[str] = None
    industry: Optional[str] = None
