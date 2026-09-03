from enum import StrEnum

from pydantic import BaseModel


class ApplicationStatus(StrEnum):
    DISCOVERED = "DISCOVERED"
    SHORTLISTED = "SHORTLISTED"
    RESUME_READY = "RESUME_READY"
    READY_TO_APPLY = "READY_TO_APPLY"
    APPLIED = "APPLIED"
    RECRUITER_RESPONSE = "RECRUITER_RESPONSE"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class ApplicationRecord(BaseModel):
    id: str
    job_id: str
    status: ApplicationStatus = ApplicationStatus.DISCOVERED
    official_url: str | None = None
    notes: str = ""
    resume_version_id: str | None = None
