from hireme_ai.jobs.adapters.base import JobSourceAdapter
from hireme_ai.jobs.deduplicator import deduplicate_jobs
from hireme_ai.jobs.normalizer import normalize_job
from hireme_ai.schemas.job import JobRecord


async def discover_jobs(
    adapters: list[JobSourceAdapter], query: str, limit: int = 20
) -> list[JobRecord]:
    all_jobs: list[JobRecord] = []
    for adapter in adapters:
        all_jobs.extend(await adapter.discover(query, limit))
    normalized = [normalize_job(job) for job in all_jobs]
    return deduplicate_jobs(normalized)[:limit]
