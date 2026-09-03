from uuid import uuid4

from fastapi import HTTPException
from pydantic import BaseModel, Field

from hireme_ai.providers.live import structured
from hireme_ai.resume.verifier import verify_resume
from hireme_ai.schemas.candidate import CandidateProfile
from hireme_ai.schemas.job import JobRequirement
from hireme_ai.schemas.resume import GeneratedResumeBullet, ResumeVersion, VerificationStatus


class FactSelection(BaseModel):
    fact_ids: list[str] = Field(max_length=15)


async def build_live_resume(
    candidate: CandidateProfile, req: JobRequirement, job_id: str | None, company: str | None
) -> ResumeVersion:
    facts = {f.id: f for f in candidate.facts if f.verified_by_user}
    if not facts:
        raise HTTPException(422, "Review and confirm candidate facts before tailoring.")
    if len(facts) > 100:
        raise HTTPException(422, "At most 100 reviewed facts are supported per request.")
    selected = await structured(
        "Select up to 15 relevant fact IDs for this role, ordered by relevance. "
        "Use ONLY supplied IDs. Return an empty list if none are relevant. Do not rewrite facts.",
        {"requirements": req.model_dump(), "facts": [f.model_dump() for f in facts.values()]},
        FactSelection,
    )
    if any(fid not in facts for fid in selected.fact_ids):
        raise HTTPException(502, "Gemini selected unsupported evidence; output was blocked.")
    bullets = []
    for fid in dict.fromkeys(selected.fact_ids):
        fact = facts[fid]
        text = f"Verified skill: {fact.value}" if fact.category == "skill" else fact.source_text
        if text:
            bullets.append(
                GeneratedResumeBullet(
                    text=text,
                    source_fact_ids=[fid],
                    transformation_type="gemini_selection_exact_excerpt",
                )
            )
    checked = verify_resume(bullets, list(facts.values()))
    passed = bool(checked) and all(
        b.verification_status == VerificationStatus.PASSED for b in checked
    )
    return ResumeVersion(
        id=str(uuid4()),
        target_job_id=job_id,
        company=company,
        bullets=checked,
        verification_status=VerificationStatus.PASSED if passed else VerificationStatus.FAILED,
    )
