from hireme_ai.matching.eligibility import check_eligibility
from hireme_ai.matching.evidence import map_requirement_evidence
from hireme_ai.matching.scoring import calculate_score
from hireme_ai.schemas.candidate import CandidateProfile
from hireme_ai.schemas.job import JobRecord, JobRequirement
from hireme_ai.schemas.match import MatchResult


def match_candidate(
    candidate: CandidateProfile, job: JobRecord, req: JobRequirement
) -> MatchResult:
    evidence = map_requirement_evidence(candidate, req)
    mandatory = [e for e in evidence if e.requirement in req.mandatory_skills]
    preferred = [e for e in evidence if e.requirement in req.preferred_skills]
    required_coverage = 100 * sum(e.alignment != "NONE" for e in mandatory) / max(1, len(mandatory))
    preferred_coverage = (
        100 * sum(e.alignment != "NONE" for e in preferred) / max(1, len(preferred))
    )
    relevant_evidence = (
        100 * sum(bool(e.candidate_fact_ids) for e in evidence) / max(1, len(evidence))
    )
    experience_alignment = (
        100.0
        if req.minimum_experience is None or candidate.experience_years >= req.minimum_experience
        else 0.0
    )
    location_alignment = (
        100.0
        if not req.location
        or not candidate.locations
        or any(loc.lower() in req.location.lower() for loc in candidate.locations)
        else 50.0
    )
    score = calculate_score(
        {
            "required_skill_coverage": required_coverage,
            "relevant_evidence": relevant_evidence,
            "semantic_role_alignment": required_coverage,
            "responsibility_alignment": relevant_evidence,
            "experience_alignment": experience_alignment,
            "preferred_skill_coverage": preferred_coverage,
            "location_work_mode": location_alignment,
        }
    )
    eligible, warnings = check_eligibility(candidate, job, req)
    gaps = [
        {
            "skill": e.requirement,
            "priority": "CRITICAL" if e.requirement in req.mandatory_skills else "OPTIONAL",
        }
        for e in evidence
        if e.alignment == "NONE"
    ]
    return MatchResult(
        eligible=eligible, eligibility_warnings=warnings, score=score, evidence=evidence, gaps=gaps
    )
