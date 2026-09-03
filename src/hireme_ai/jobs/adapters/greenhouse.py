import httpx

from hireme_ai.jobs.adapters.base import JobSourceAdapter
from hireme_ai.schemas.job import JobRecord, JobStatus


class GreenhouseAdapter(JobSourceAdapter):
    name = "greenhouse"

    def __init__(self, board_token: str, timeout: float = 15.0) -> None:
        self.board_token = board_token
        self.timeout = timeout

    async def discover(self, query: str, limit: int = 20) -> list[JobRecord]:
        url = f"https://boards-api.greenhouse.io/v1/boards/{self.board_token}/jobs?content=true"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
        jobs = []
        for raw in response.json().get("jobs", []):
            searchable = f"{raw.get('title', '')} {raw.get('content', '')}"
            if query.lower() not in searchable.lower():
                continue
            jobs.append(
                JobRecord(
                    id=f"greenhouse:{raw['id']}",
                    source=self.name,
                    external_job_id=str(raw["id"]),
                    title=raw.get("title", "Unknown"),
                    company=self.board_token,
                    location=(raw.get("location") or {}).get("name"),
                    description=raw.get("content", ""),
                    canonical_url=raw.get("absolute_url"),
                    status=JobStatus.UNKNOWN,
                )
            )
            if len(jobs) >= limit:
                break
        return jobs

    async def fetch(self, external_job_id: str) -> JobRecord:
        jobs = await self.discover("", 500)
        return next(job for job in jobs if job.external_job_id == external_job_id)
