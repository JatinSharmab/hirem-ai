import httpx

from hireme_ai.jobs.adapters.base import JobSourceAdapter
from hireme_ai.schemas.job import JobRecord, JobStatus


class AshbyAdapter(JobSourceAdapter):
    name = "ashby"

    def __init__(self, organization: str, timeout: float = 15.0) -> None:
        self.organization = organization
        self.timeout = timeout

    async def discover(self, query: str, limit: int = 20) -> list[JobRecord]:
        url = f"https://api.ashbyhq.com/posting-api/job-board/{self.organization}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
        jobs = []
        for raw in response.json().get("jobs", []):
            searchable = f"{raw.get('title', '')} {raw.get('descriptionPlain', '')}"
            if query.lower() not in searchable.lower():
                continue
            jobs.append(
                JobRecord(
                    id=f"ashby:{raw['id']}",
                    source=self.name,
                    external_job_id=raw.get("id"),
                    title=raw.get("title", "Unknown"),
                    company=self.organization,
                    location=raw.get("location"),
                    description=raw.get("descriptionPlain", ""),
                    canonical_url=raw.get("jobUrl"),
                    status=JobStatus.UNKNOWN,
                )
            )
            if len(jobs) >= limit:
                break
        return jobs

    async def fetch(self, external_job_id: str) -> JobRecord:
        jobs = await self.discover("", 500)
        return next(job for job in jobs if job.external_job_id == external_job_id)
