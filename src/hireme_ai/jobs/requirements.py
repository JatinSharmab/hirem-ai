import re

from hireme_ai.profile.extractor import COMMON_SKILLS
from hireme_ai.schemas.job import JobRecord, JobRequirement


def extract_demo_requirements(job: JobRecord) -> JobRequirement:
    """Keyword-only fallback. Unknown experience and work mode remain unknown."""
    mandatory: list[str] = []
    preferred: list[str] = []
    for sentence in re.split(r"[.;\n]", job.description):
        target = (
            preferred
            if re.search(r"\b(preferred|optional|nice to have)\b", sentence, re.I)
            else mandatory
        )
        for skill in COMMON_SKILLS:
            if re.search(rf"\b{re.escape(skill)}\b", sentence, re.I) and skill not in target:
                target.append(skill)
    return JobRequirement(
        role_title=job.title,
        mandatory_skills=mandatory,
        preferred_skills=[s for s in preferred if s not in mandatory],
        location=job.location,
        confidence=0.5,
        ambiguities=[
            "Keyword extraction only; review requirement strength and missing constraints."
        ],
    )
