from hireme_ai.matching.skills import normalize_skill
from hireme_ai.schemas.candidate import CandidateProfile
from hireme_ai.schemas.job import JobRequirement
from hireme_ai.schemas.match import EvidenceMatch


def map_requirement_evidence(
    candidate: CandidateProfile, req: JobRequirement
) -> list[EvidenceMatch]:
    results: list[EvidenceMatch] = []
    for skill in req.mandatory_skills + req.preferred_skills:
        canonical = normalize_skill(skill)
        facts = [
            f
            for f in candidate.facts
            if f.verified_by_user
            and f.category == "skill"
            and normalize_skill(f.value).lower() == canonical.lower()
        ]
        match = bool(facts)
        results.append(
            EvidenceMatch(
                requirement=skill,
                candidate_fact_ids=[f.id for f in facts],
                evidence=[f.source_text or f.value for f in facts],
                alignment="STRONG" if match else "NONE",
                confidence=1.0 if match else 0.0,
            )
        )
    return results
