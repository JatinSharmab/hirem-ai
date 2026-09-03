from uuid import uuid4

from hireme_ai.jobs.adapters.base import JobSourceAdapter
from hireme_ai.schemas.job import JobRecord, JobStatus


class ManualAdapter(JobSourceAdapter):
    name = "manual"

    def __init__(self, jobs: list[JobRecord] | None = None) -> None:
        self.jobs = jobs or []

    async def discover(self, query: str, limit: int = 20) -> list[JobRecord]:
        query_lower = query.lower()
        return [j for j in self.jobs if query_lower in (j.title + " " + j.description).lower()][
            :limit
        ]

    async def fetch(self, external_job_id: str) -> JobRecord:
        for job in self.jobs:
            if job.external_job_id == external_job_id or job.id == external_job_id:
                return job
        raise KeyError(external_job_id)

    @staticmethod
    def from_text(
        title: str, company: str, description: str, location: str | None = None
    ) -> JobRecord:
        return JobRecord(
            id=str(uuid4()),
            source="manual",
            title=title,
            company=company,
            location=location,
            description=description,
            status=JobStatus.UNKNOWN,
        )
