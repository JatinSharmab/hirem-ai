from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"
    STALE = "STALE"
    ERROR = "ERROR"


class JobRequirement(BaseModel):
    role_title: str
    role_family: str | None = None
    mandatory_skills: list[str] = []
    preferred_skills: list[str] = []
    responsibilities: list[str] = []
    education_requirements: list[str] = []
    minimum_experience: float | None = None
    maximum_experience: float | None = None
    location: str | None = None
    work_mode: str | None = None
    employment_type: str | None = None
    domain: str | None = None
    seniority: str | None = None
    certifications: list[str] = []
    keywords: list[str] = []
    salary: str | None = None
    ambiguities: list[str] = []
    confidence: float = Field(default=1.0, ge=0, le=1)


class JobRecord(BaseModel):
    id: str
    source: str
    external_job_id: str | None = None
    title: str
    company: str
    location: str | None = None
    work_mode: str | None = None
    description: str
    canonical_url: str | None = None
    posted_at: datetime | None = None
    discovered_at: datetime | None = None
    last_verified_at: datetime | None = None
    status: JobStatus = JobStatus.UNKNOWN
    verification_evidence: str | None = None
