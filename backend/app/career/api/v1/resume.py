from typing import Annotated

from fastapi import APIRouter, File, Form, Request, UploadFile
from starlette.concurrency import run_in_threadpool

from backend.app.career.schema.resume import ResumeAnalysisDetail
from backend.app.career.service.resume_service import resume_service
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.utils.limiter import limiter, user_rate_key

router = APIRouter(prefix='/resume', tags=['Resume'])


@router.post('/analyze', summary='Analyze an uploaded resume', dependencies=[DependsJwtAuth])
@limiter.limit('3/hour', key_func=user_rate_key)
async def analyze_resume(
    request: Request,
    resume: Annotated[UploadFile, File(description='PDF or DOCX resume, up to 5MB')],
    job_description: Annotated[str | None, Form(description='Posting to compare against')] = None,
) -> ResponseSchemaModel[ResumeAnalysisDetail]:
    # Async only to await the upload. The analysis itself — PDF parsing and a
    # blocking Gemini call — is offloaded, so it cannot stall the event loop.
    content = await resume.read()
    analysis = await run_in_threadpool(
        resume_service.analyze,
        content=content,
        content_type=resume.content_type or '',
        job_description=job_description,
    )
    return response_base.success(data=analysis)
