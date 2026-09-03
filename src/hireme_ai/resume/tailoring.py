from hireme_ai.schemas.candidate import CandidateProfile
from hireme_ai.schemas.job import JobRequirement
from hireme_ai.schemas.resume import GeneratedResumeBullet


def deterministic_demo_tailor(
    candidate: CandidateProfile, req: JobRequirement
) -> list[GeneratedResumeBullet]:
    """Safe Demo Mode tailoring: only restates verified skill facts with provenance."""
    bullets: list[GeneratedResumeBullet] = []
    wanted = {s.lower() for s in req.mandatory_skills + req.preferred_skills}
    for fact in candidate.facts:
        if fact.verified_by_user and fact.category == "skill" and fact.value.lower() in wanted:
            bullets.append(
                GeneratedResumeBullet(
                    text=f"Verified skill: {fact.value}",
                    source_fact_ids=[fact.id],
                    transformation_type="verified_rephrase",
                )
            )
    return bullets
