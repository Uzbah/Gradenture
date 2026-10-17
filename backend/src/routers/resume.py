from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from src.dependencies.auth import get_current_user
from src.dependencies.rate_limit import limiter, user_rate_key
from src.services import resume_service

router = APIRouter(prefix="/resume", tags=["Resume"])


# Plain `def` on purpose: parsing + the ~15 s Gemini call are blocking, and an
# `async def` would run them on the event loop and freeze every other request.
# FastAPI runs `def` routes in its threadpool.
@router.post("/analyze")
@limiter.limit("3/hour", key_func=user_rate_key)
def analyze_resume(
    request: Request,
    user: Annotated[dict, Depends(get_current_user)],
    resume: Annotated[UploadFile, File()],
    job_description: Annotated[str | None, Form()] = None,
) -> dict:
    # Read one byte past the cap so oversize files are detected without
    # pulling an arbitrarily large upload into memory.
    content = resume.file.read(resume_service.MAX_FILE_SIZE + 1)
    return resume_service.analyze(content, resume.content_type or "", job_description)
