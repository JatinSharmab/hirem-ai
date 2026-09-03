import base64
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from hireme_ai.core.config import get_settings
from hireme_ai.resume.docx_renderer import render_docx
from hireme_ai.resume.live import build_live_resume
from hireme_ai.resume.pdf_renderer import render_pdf
from hireme_ai.resume.service import build_verified_resume
from hireme_ai.resume.verifier import verify_resume
from hireme_ai.schemas.candidate import CandidateProfile
from hireme_ai.schemas.job import JobRequirement
from hireme_ai.schemas.resume import ResumeVersion, VerificationStatus

router = APIRouter(prefix="/api/v1/resumes", tags=["resumes"])


class TailorRequest(BaseModel):
    candidate: CandidateProfile
    requirement: JobRequirement
    job_id: str | None = None
    company: str | None = None
    consent: bool = False


@router.post("/tailor", response_model=ResumeVersion)
async def tailor(payload: TailorRequest) -> ResumeVersion:
    if get_settings().app_mode == "live":
        if not payload.consent:
            raise HTTPException(422, "Consent is required to send reviewed facts to Gemini.")
        return await build_live_resume(
            payload.candidate, payload.requirement, payload.job_id, payload.company
        )
    return build_verified_resume(
        payload.candidate, payload.requirement, payload.job_id, payload.company
    )


class ExportRequest(BaseModel):
    candidate: CandidateProfile
    version: ResumeVersion


@router.post("/export/{format}")
async def export_resume(format: Literal["pdf", "docx"], payload: ExportRequest) -> dict[str, str]:
    checked = verify_resume(payload.version.bullets, payload.candidate.facts)
    if not checked or any(b.verification_status != VerificationStatus.PASSED for b in checked):
        raise HTTPException(status_code=422, detail="Export requires nonempty, verified content")
    render = render_pdf if format == "pdf" else render_docx
    content = render(payload.candidate, checked)
    return {"content": base64.b64encode(content).decode("ascii")}
