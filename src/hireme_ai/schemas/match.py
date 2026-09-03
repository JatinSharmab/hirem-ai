from pydantic import BaseModel, Field


class EvidenceMatch(BaseModel):
    requirement: str
    candidate_fact_ids: list[str] = []
    evidence: list[str] = []
    alignment: str
    confidence: float = Field(ge=0, le=1)


class ScoreBreakdown(BaseModel):
    required_skill_coverage: float = 0
    relevant_evidence: float = 0
    semantic_role_alignment: float = 0
    responsibility_alignment: float = 0
    experience_alignment: float = 0
    preferred_skill_coverage: float = 0
    location_work_mode: float = 0
    total: float = 0


class MatchResult(BaseModel):
    eligible: bool
    eligibility_warnings: list[str] = []
    score: ScoreBreakdown
    evidence: list[EvidenceMatch] = []
    gaps: list[dict[str, str]] = []
