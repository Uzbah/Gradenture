from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from src.dependencies.auth import get_current_user
from src.dependencies.rate_limit import limiter, user_rate_key
from src.services import resume_service

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post("/analyze")
@limiter.limit("3/hour", key_func=user_rate_key)
async def analyze_resume(
    request: Request,
    user: Annotated[dict, Depends(get_current_user)],
    resume: Annotated[UploadFile, File()],
    job_description: Annotated[str | None, Form()] = None,
) -> dict:
    content = await resume.read()
    return resume_service.analyze(content, resume.content_type or "", job_description)
