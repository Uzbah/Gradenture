from fastapi import APIRouter

from backend.app.career.api.v1.application import router as application_router
from backend.app.career.api.v1.company import router as company_router
from backend.app.career.api.v1.prep import router as prep_router
from backend.app.career.api.v1.question import router as question_router
from backend.app.career.api.v1.resume import router as resume_router
from backend.app.career.api.v1.review import router as review_router

router = APIRouter()

router.include_router(question_router)
router.include_router(review_router)
router.include_router(application_router)
router.include_router(company_router)
router.include_router(prep_router)
router.include_router(resume_router)
