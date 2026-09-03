import json
from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from hireme_ai.core.config import get_settings
from hireme_ai.db.repositories import live_jobs
from hireme_ai.db.repositories.workspaces import consume
from hireme_ai.jobs.adapters.ashby import AshbyAdapter
from hireme_ai.jobs.adapters.greenhouse import GreenhouseAdapter
from hireme_ai.jobs.adapters.lever import LeverAdapter
from hireme_ai.jobs.requirements import extract_demo_requirements
from hireme_ai.providers.live import extract_requirements
from hireme_ai.schemas.job import JobRecord, JobRequirement

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


def _demo_jobs() -> list[JobRecord]:
    return [
        JobRecord.model_validate(item)
        for item in json.loads(Path("data/demo/jobs.json").read_text())
    ]


class ImportJob(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    company: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=50, max_length=30000)
    location: str | None = Field(default=None, max_length=300)


@router.post("/import", response_model=JobRecord)
async def import_job(payload: ImportJob) -> JobRecord:
    if get_settings().app_mode != "live":
        raise HTTPException(409, "Job import requires APP_MODE=live.")
    if get_settings().app_env == "production":
        await consume("import", 20, 500)
    job = JobRecord(id=str(uuid4()), source="manual", **payload.model_dump())
    return await live_jobs.save_job(job)


@router.post("/discover", response_model=list[JobRecord])
async def discover(
    query: str = "",
    source: str = "greenhouse",
    board: str = Query(default="", pattern=r"^[a-zA-Z0-9_-]{0,100}$"),
) -> list[JobRecord]:
    settings = get_settings()
    if settings.app_mode == "demo":
        return [j for j in _demo_jobs() if query.lower() in (j.title + " " + j.description).lower()]
    if not settings.enable_live_job_discovery:
        raise HTTPException(
            409, "Enable ENABLE_LIVE_JOB_DISCOVERY in .env and restart, or paste a JD."
        )
    if not board:
        raise HTTPException(422, "Enter a public company ATS board identifier.")
    adapters: dict[str, type[GreenhouseAdapter] | type[LeverAdapter] | type[AshbyAdapter]] = {
        "greenhouse": GreenhouseAdapter,
        "lever": LeverAdapter,
        "ashby": AshbyAdapter,
    }
    if source not in adapters:
        raise HTTPException(422, "Supported sources: greenhouse, lever, ashby.")
    if settings.app_env == "production":
        await consume("ats", 3, 30)
    try:
        jobs = await adapters[source](board).discover(query, limit=20)
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        raise HTTPException(
            502, "ATS request failed. Check source and board identifier, or paste the JD."
        ) from None
    results = []
    for job in jobs:
        # Keep board identity with the source ID to avoid collisions across tenants.
        job = job.model_copy(
            update={
                "external_job_id": f"{board}:{job.external_job_id}",
                "description": job.description[:30000],
            }
        )
        results.append(await live_jobs.save_job(job))
    return results


@router.get("", response_model=list[JobRecord])
async def list_jobs() -> list[JobRecord]:
    return await live_jobs.all_jobs() if get_settings().app_mode == "live" else _demo_jobs()


@router.get("/{job_id}", response_model=JobRecord)
async def get_job(job_id: str) -> JobRecord:
    if get_settings().app_mode == "live":
        job = await live_jobs.find_job(job_id)
        if job:
            return job
    else:
        for job in _demo_jobs():
            if job.id == job_id:
                return job
    raise HTTPException(404, "Job not found")


@router.get("/{job_id}/requirements", response_model=JobRequirement)
async def get_requirements(job_id: str) -> JobRequirement:
    job = await get_job(job_id)
    settings = get_settings()
    if settings.app_mode == "demo":
        return extract_demo_requirements(job)
    cached = await live_jobs.cached_requirements(job, settings.llm_model)
    if cached:
        return cached
    raise HTTPException(409, "Analyze this job with Gemini on Job Discovery first.")


@router.post("/{job_id}/analyze", response_model=JobRequirement)
async def analyze_job(job_id: str) -> JobRequirement:
    job = await get_job(job_id)
    settings = get_settings()
    if settings.app_mode != "live":
        raise HTTPException(409, "Gemini analysis requires live mode.")
    cached = await live_jobs.cached_requirements(job, settings.llm_model)
    if cached:
        return cached
    req = await extract_requirements(job.title, job.description)
    await live_jobs.save_requirements(job, settings.llm_model, req)
    return req
