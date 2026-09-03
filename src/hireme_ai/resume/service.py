from uuid import uuid4

from hireme_ai.resume.tailoring import deterministic_demo_tailor
from hireme_ai.resume.verifier import verify_resume
from hireme_ai.schemas.candidate import CandidateProfile
from hireme_ai.schemas.job import JobRequirement
from hireme_ai.schemas.resume import ResumeVersion, VerificationStatus


def build_verified_resume(
    candidate: CandidateProfile,
    req: JobRequirement,
    job_id: str | None = None,
    company: str | None = None,
) -> ResumeVersion:
    bullets = verify_resume(deterministic_demo_tailor(candidate, req), candidate.facts)
    status = (
        VerificationStatus.PASSED
        if bullets and all(b.verification_status == VerificationStatus.PASSED for b in bullets)
        else VerificationStatus.FAILED
    )
    return ResumeVersion(
        id=str(uuid4()),
        target_job_id=job_id,
        company=company,
        bullets=bullets,
        verification_status=status,
    )
