from hireme_ai.matching.eligibility import check_eligibility
from hireme_ai.schemas.candidate import CandidateProfile
from hireme_ai.schemas.job import JobRecord, JobRequirement, JobStatus


def test_experience_mismatch_warns() -> None:
    candidate = CandidateProfile(name="x", experience_years=1)
    job = JobRecord(
        id="j", source="demo", title="Senior AI", company="x", description="", status=JobStatus.OPEN
    )
    req = JobRequirement(role_title="Senior AI", seniority="senior", minimum_experience=5)
    eligible, warnings = check_eligibility(candidate, job, req)
    assert not eligible
    assert warnings
