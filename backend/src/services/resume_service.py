import io
import json
import logging
import os

import pdfplumber
from docx import Document
from google import genai
from google.genai import types

from src.dependencies.exceptions import AppError

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_JD_CHARS = 10_000

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}

# gemini-2.0-flash was shut down on 2026-06-01; Google lists gemini-3.6-flash as
# its replacement. Model ids churn, so it is overridable without a deploy.
DEFAULT_MODEL = "gemini-3.6-flash"

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise AppError(500, {"error": "AI service not configured"})
        _client = genai.Client(api_key=api_key)
    return _client


def _extract_text(content: bytes, content_type: str) -> str:
    file_type = ALLOWED_TYPES.get(content_type)
    if not file_type:
        raise AppError(400, {"error": "Only PDF and DOCX files are supported"})

    try:
        if file_type == "pdf":
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        else:
            doc = Document(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        # content_type is client-supplied; a renamed or corrupt file lands here.
        raise AppError(400, {"error": "Could not read the file. Upload a valid PDF or DOCX."})

    text = text.strip()
    if not text:
        raise AppError(
            422,
            {"error": "Could not extract text from the file. Ensure it is not a scanned image."},
        )

    return text


def _build_prompt(resume_text: str, job_description: str | None) -> str:
    jd_block = f"\n\nJob Description:\n{job_description}" if job_description else ""
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


def analyze(content: bytes, content_type: str, job_description: str | None) -> dict:
    if not content:
        raise AppError(400, {"error": "Uploaded file is empty"})

    if len(content) > MAX_FILE_SIZE:
        raise AppError(413, {"error": "File exceeds 5MB limit"})

    if job_description and len(job_description) > MAX_JD_CHARS:
        raise AppError(400, {"errors": {"job_description": [f"must be at most {MAX_JD_CHARS} characters"]}})

    resume_text = _extract_text(content, content_type)
    prompt = _build_prompt(resume_text, job_description)

    try:
        response = _get_client().models.generate_content(
            model=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL),
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        result = json.loads(response.text or "")
    except AppError:
        raise
    except Exception:
        logger.exception("Gemini resume analysis failed")
        raise AppError(502, {"error": "AI analysis failed. Please try again."})

    return {"data": result}
