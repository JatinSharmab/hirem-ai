from uuid import uuid4

import httpx

from hireme_ai.core.security import validate_public_http_url
from hireme_ai.jobs.adapters.base import JobSourceAdapter
from hireme_ai.schemas.job import JobRecord, JobStatus


class URLImportAdapter(JobSourceAdapter):
    name = "url"

    def __init__(self, url: str, timeout: float = 15.0) -> None:
        self.url = validate_public_http_url(url)
        self.timeout = timeout

    async def discover(self, query: str, limit: int = 20) -> list[JobRecord]:
        return [await self.fetch(self.url)]

    async def fetch(self, external_job_id: str) -> JobRecord:
        validate_public_http_url(self.url, resolve_dns=True)
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=False) as client:
            response = await client.get(self.url)
            response.raise_for_status()
        return JobRecord(
            id=str(uuid4()),
            source=self.name,
            title="Imported job",
            company="Unknown",
            description=response.text[:100000],
            canonical_url=str(response.url),
            status=JobStatus.UNKNOWN,
        )
