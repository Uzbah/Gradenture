from typing import Annotated

from fastapi import Depends, Path

from backend.common.dataclasses import CurrentUser
from backend.common.exception.errors import ForbiddenError
from backend.common.security.jwt import get_current_user
from backend.common.tables import COMPANY_ADMINS
from backend.database.supabase import maybe_row, supabase


def require_admin(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
    """Platform admin or super admin."""
    if not user.is_admin:
        raise ForbiddenError
    return user


def require_super_admin(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
    """Super admin only — role changes and manager grants."""
    if not user.is_super_admin:
        raise ForbiddenError
    return user


def _is_company_manager(user_id: str, company_id: str) -> bool:
    return bool(
        maybe_row(supabase.table(COMPANY_ADMINS).select('user_id').eq('company_id', company_id).eq('user_id', user_id))
    )


def require_company_manager(
    company_id: Annotated[str, Path(description='Company ID')],
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    """Manager of this company, or any platform admin.

    Scope is the company's own profile metadata — never moderation of the questions
    and reviews written about the company.
    """
    if user.is_admin:
        return user
    if not _is_company_manager(user.sub, company_id):
        raise ForbiddenError
    return user


# Receive the caller, having checked the role.
AdminDep = Annotated[CurrentUser, Depends(require_admin)]
SuperAdminDep = Annotated[CurrentUser, Depends(require_super_admin)]
CompanyManagerDep = Annotated[CurrentUser, Depends(require_company_manager)]

# Declare in a route's `dependencies=[...]` to check the role without using the caller.
DependsAdmin = Depends(require_admin)
DependsSuperAdmin = Depends(require_super_admin)
DependsCompanyManager = Depends(require_company_manager)
