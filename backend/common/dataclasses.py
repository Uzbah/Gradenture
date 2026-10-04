import dataclasses

from backend.common.enums import UserRole


@dataclasses.dataclass(frozen=True, slots=True)
class CurrentUser:
    """The authenticated caller, resolved from the Supabase access token.

    Replaces the untyped dict the old dependency returned, so services read
    ``user.sub`` rather than ``user["sub"]``.
    """

    sub: str
    email: str | None
    role: UserRole
    metadata: dict
    token: str

    @property
    def is_admin(self) -> bool:
        return self.role in UserRole.admin_roles()

    @property
    def is_super_admin(self) -> bool:
        return self.role == UserRole.SUPER_ADMIN
