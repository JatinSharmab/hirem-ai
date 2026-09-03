from fastapi import APIRouter
from pydantic import BaseModel

from hireme_ai.matching.service import match_candidate
from hireme_ai.schemas.candidate import CandidateProfile
from hireme_ai.schemas.job import JobRecord, JobRequirement
from hireme_ai.schemas.match import MatchResult

router = APIRouter(prefix="/api/v1/matches", tags=["matches"])


class MatchRequest(BaseModel):
    candidate: CandidateProfile
    job: JobRecord
    requirement: JobRequirement


@router.post("", response_model=MatchResult)
async def create_match(payload: MatchRequest) -> MatchResult:
    return match_candidate(payload.candidate, payload.job, payload.requirement)
