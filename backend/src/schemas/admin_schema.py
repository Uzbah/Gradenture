from typing import Literal, Optional

from pydantic import BaseModel


class ModerateSchema(BaseModel):
    status:     Literal["approved", "rejected", "needs_edit"]
    admin_note: Optional[str] = None


class UpdateRoleSchema(BaseModel):
    role: Literal["user", "admin", "super_admin"]
