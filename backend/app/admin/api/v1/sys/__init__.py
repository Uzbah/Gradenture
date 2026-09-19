from fastapi import APIRouter

from backend.app.admin.api.v1.sys.company_admin import router as company_admin_router
from backend.app.admin.api.v1.sys.flag import router as flag_router
from backend.app.admin.api.v1.sys.moderation import router as moderation_router
from backend.app.admin.api.v1.sys.user import router as user_router
from backend.app.admin.api.v1.sys.user_admin import router as user_admin_router

router = APIRouter()

router.include_router(user_router)
router.include_router(moderation_router)
router.include_router(flag_router)
router.include_router(company_admin_router)
router.include_router(user_admin_router)
