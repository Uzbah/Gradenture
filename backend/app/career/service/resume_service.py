import io
import json

import google.generativeai as genai
import pdfplumber
from docx import Document

from backend.common.exception import errors
from backend.common.log import log
from backend.core.conf import settings

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

ALLOWED_TYPES = {
    'application/pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
}

_model = None


class ResumeService:
    """Resume analysis, via Gemini."""

    @staticmethod
    def _get_model() -> genai.GenerativeModel:
        """The Gemini client, built on first use.

        Lazily, so the app starts without an API key: only this one endpoint
        depends on it.
        """
        global _model
        if _model is None:
            if not settings.GEMINI_API_KEY:
                raise errors.ServerError(msg='AI service not configured')
            genai.configure(api_key=settings.GEMINI_API_KEY)
            _model = genai.GenerativeModel(settings.GEMINI_MODEL)
        return _model

    @staticmethod
    def _extract_text(content: bytes, content_type: str) -> str:
        """Plain text from an uploaded PDF or DOCX."""
        file_type = ALLOWED_TYPES.get(content_type)
        if not file_type:
            raise errors.RequestError(msg='Only PDF and DOCX files are supported')

        if file_type == 'pdf':
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
        else:
            document = Document(io.BytesIO(content))
            text = '\n'.join(paragraph.text for paragraph in document.paragraphs)

        text = text.strip()
        if not text:
            # A scanned resume is a PDF of images: there is no text layer to read.
            raise errors.UnprocessableError(
                msg='Could not extract text from the file. Ensure it is not a scanned image.'
            )
        return text

    @staticmethod
    def _build_prompt(resume_text: str, job_description: str | None) -> str:
        """The analysis prompt, with the job description folded in when given."""
        jd_block = f'\n\nJob Description:\n{job_description}' if job_description else ''
        jd_field = (
            '\n- "keyword_gaps": array of important keywords/skills from the job description missing from the resume'
            if job_description
            else '\n- "keyword_gaps": empty array'
        )

        return f"""You are an expert resume reviewer with 10+ years of technical recruiting experience.

Analyze the resume below and return a JSON object with exactly these fields:
- "score": integer 1-10 rating overall resume quality
- "summary": 2-3 sentence overall assessment
- "strengths": array of 3-5 specific strengths (reference actual resume content, not generic praise)
- "weaknesses": array of 3-5 specific weaknesses
- "improvements": array of 3-5 concrete, actionable suggestions{jd_field}

Be direct and specific. Do not give generic advice like "add more details".

Resume:
{resume_text}{jd_block}

Return only valid JSON with no markdown fences or extra text."""

    @staticmethod
    def analyze(*, content: bytes, content_type: str, job_description: str | None) -> dict:
        """Analyze an uploaded resume.

        :param content: the uploaded file
        :param content_type: its declared MIME type
        :param job_description: optional posting to compare the resume against
        """
        if not content:
            raise errors.RequestError(msg='Uploaded file is empty')

        if len(content) > MAX_FILE_SIZE:
            raise errors.PayloadTooLargeError(msg='File exceeds 5MB limit')

        resume_text = ResumeService._extract_text(content, content_type)
        prompt = ResumeService._build_prompt(resume_text, job_description)

        try:
            model = ResumeService._get_model()
            response = model.generate_content(
                prompt,
                generation_config={'response_mime_type': 'application/json'},
            )
            return json.loads(response.text)
        except errors.BaseExceptionError:
            raise
        except Exception as exc:
            log.exception('Gemini resume analysis failed: {}', exc)
            raise errors.GatewayError(msg='AI analysis failed. Please try again.') from exc


resume_service: ResumeService = ResumeService()
