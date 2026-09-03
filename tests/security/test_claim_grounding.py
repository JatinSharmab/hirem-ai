import pytest

from hireme_ai.resume.verifier import verify_bullet
from hireme_ai.schemas.candidate import CandidateFact
from hireme_ai.schemas.resume import GeneratedResumeBullet


@pytest.mark.parametrize(
    "text",
    [
        "Used Python and Kubernetes",
        "Worked at Google",
        "Earned a PhD in 2025",
        "Managed a team",
        "Reduced latency by 40%",
        "Applied Python in production",
    ],
)
def test_added_claims_fail(text: str) -> None:
    fact = CandidateFact(
        id="F",
        category="skill",
        subject="Candidate",
        predicate="lists",
        value="Python",
        source_text="Python",
        verified_by_user=True,
    )
    assert (
        verify_bullet(
            GeneratedResumeBullet(text=text, source_fact_ids=["F"]), [fact]
        ).verification_status
        == "FAILED"
    )


def test_unreviewed_fact_fails() -> None:
    fact = CandidateFact(
        id="F", category="skill", subject="Candidate", predicate="lists", value="Python"
    )
    assert (
        verify_bullet(
            GeneratedResumeBullet(text="Verified skill: Python", source_fact_ids=["F"]), [fact]
        ).verification_status
        == "FAILED"
    )
