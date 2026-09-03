from hireme_ai.schemas.candidate import CandidateProfile
from hireme_ai.schemas.job import JobRecord, JobRequirement, JobStatus


def check_eligibility(
    candidate: CandidateProfile, job: JobRecord, req: JobRequirement
) -> tuple[bool, list[str]]:
    warnings: list[str] = []
    if job.status != JobStatus.OPEN:
        warnings.append(
            f"Job status is {job.status}; open status is required for clean eligibility."
        )
    if req.minimum_experience is not None and candidate.experience_years < req.minimum_experience:
        warnings.append("Candidate experience is below the stated minimum.")
    if (
        req.seniority
        and req.seniority.lower() in {"senior", "staff", "principal", "lead"}
        and candidate.experience_years < 3
    ):
        warnings.append("Seniority appears inconsistent with candidate experience.")
    return (not warnings, warnings)
