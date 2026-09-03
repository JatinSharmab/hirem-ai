from abc import ABC, abstractmethod

from hireme_ai.schemas.job import JobRecord


class JobSourceAdapter(ABC):
    name: str

    @abstractmethod
    async def discover(self, query: str, limit: int = 20) -> list[JobRecord]: ...

    @abstractmethod
    async def fetch(self, external_job_id: str) -> JobRecord: ...

    async def health_check(self) -> bool:
        return True
