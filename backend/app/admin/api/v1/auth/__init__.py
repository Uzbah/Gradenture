from fastapi import APIRouter

from backend.app.admin.api.v1.auth.auth import router as auth_router

router = APIRouter(prefix='/auth', tags=['Auth'])

router.include_router(auth_router)
