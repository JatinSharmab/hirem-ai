from hireme_ai.resume.verifier import verify_bullet
from hireme_ai.schemas.candidate import CandidateFact
from hireme_ai.schemas.resume import GeneratedResumeBullet, VerificationStatus


def test_unsupported_number_rejected() -> None:
    facts = [
        CandidateFact(id="F1", category="skill", subject="c", predicate="used", value="Python")
    ]
    bullet = GeneratedResumeBullet(
        text="Improved latency by 40% using Python", source_fact_ids=["F1"]
    )
    checked = verify_bullet(bullet, facts)
    assert checked.verification_status == VerificationStatus.FAILED
    assert any("40%" in n for n in checked.verifier_notes)


def test_grounded_bullet_passes() -> None:
    facts = [
        CandidateFact(
            id="F1",
            category="skill",
            subject="c",
            predicate="used",
            value="Python",
            source_text="Used Python",
            verified_by_user=True,
        )
    ]
    bullet = GeneratedResumeBullet(text="Verified skill: Python", source_fact_ids=["F1"])
    assert verify_bullet(bullet, facts).verification_status == VerificationStatus.PASSED
