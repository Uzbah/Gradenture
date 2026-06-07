from fastapi import APIRouter

from .admin import router as admin_router
from .applications import router as applications_router
from .auth import router as auth_router
from .companies import router as companies_router
from .questions import router as questions_router
from .reviews import router as reviews_router
from .users import router as users_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(questions_router)
api_router.include_router(reviews_router)
api_router.include_router(applications_router)
api_router.include_router(companies_router)
api_router.include_router(admin_router)
