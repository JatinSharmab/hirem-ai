import httpx

from hireme_ai.jobs.adapters.base import JobSourceAdapter
from hireme_ai.schemas.job import JobRecord, JobStatus


class LeverAdapter(JobSourceAdapter):
    name = "lever"

    def __init__(self, company: str, timeout: float = 15.0) -> None:
        self.company = company
        self.timeout = timeout

    async def discover(self, query: str, limit: int = 20) -> list[JobRecord]:
        url = f"https://api.lever.co/v0/postings/{self.company}?mode=json"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
        jobs = []
        for raw in response.json():
            searchable = f"{raw.get('text', '')} {raw.get('descriptionPlain', '')}"
            if query.lower() not in searchable.lower():
                continue
            categories = raw.get("categories") or {}
            jobs.append(
                JobRecord(
                    id=f"lever:{raw['id']}",
                    source=self.name,
                    external_job_id=raw["id"],
                    title=raw.get("text", "Unknown"),
                    company=self.company,
                    location=categories.get("location"),
                    description=raw.get("descriptionPlain", ""),
                    canonical_url=raw.get("hostedUrl"),
                    status=JobStatus.UNKNOWN,
                )
            )
            if len(jobs) >= limit:
                break
        return jobs

    async def fetch(self, external_job_id: str) -> JobRecord:
        jobs = await self.discover("", 500)
        return next(job for job in jobs if job.external_job_id == external_job_id)
