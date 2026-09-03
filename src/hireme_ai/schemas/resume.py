from enum import StrEnum

from pydantic import BaseModel


class VerificationStatus(StrEnum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"


class GeneratedResumeBullet(BaseModel):
    text: str
    source_fact_ids: list[str]
    transformation_type: str = "rephrase"
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verifier_notes: list[str] = []


class ResumeVersion(BaseModel):
    id: str
    target_job_id: str | None = None
    company: str | None = None
    bullets: list[GeneratedResumeBullet] = []
    verification_status: VerificationStatus = VerificationStatus.PENDING
