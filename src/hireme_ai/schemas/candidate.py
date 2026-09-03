from pydantic import BaseModel, Field


class CandidateFact(BaseModel):
    id: str
    category: str
    subject: str
    predicate: str
    value: str
    source_section: str | None = None
    source_text: str | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    verified_by_user: bool = False
    immutable: bool = True


class CandidateProfile(BaseModel):
    name: str
    summary: str = ""
    skills: list[str] = []
    experience_years: float = 0
    locations: list[str] = []
    facts: list[CandidateFact] = []
