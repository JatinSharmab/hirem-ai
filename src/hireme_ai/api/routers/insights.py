from collections import Counter

from fastapi import APIRouter

from hireme_ai.api.routers.jobs import list_jobs
from hireme_ai.core.config import get_settings
from hireme_ai.jobs.requirements import extract_demo_requirements

router = APIRouter(prefix="/api/v1/insights", tags=["insights"])


@router.get("/skills")
async def skills() -> dict[str, object]:
    counts: Counter[str] = Counter()
    for job in await list_jobs():
        req = extract_demo_requirements(job)
        counts.update(set(req.mandatory_skills + req.preferred_skills))
    return {
        "source": get_settings().app_mode,
        "skills": [{"skill": s, "job_count": n} for s, n in counts.most_common()],
    }
