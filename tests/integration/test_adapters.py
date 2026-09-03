from unittest.mock import patch

import httpx
import pytest

from hireme_ai.jobs.adapters.ashby import AshbyAdapter
from hireme_ai.jobs.adapters.greenhouse import GreenhouseAdapter
from hireme_ai.jobs.adapters.lever import LeverAdapter
from hireme_ai.jobs.verifier import verify_job
from hireme_ai.schemas.job import JobRecord


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("adapter", "payload"),
    [
        (
            GreenhouseAdapter("demo"),
            {
                "jobs": [
                    {
                        "id": 1,
                        "title": "Python Engineer",
                        "content": "Python",
                        "absolute_url": "https://example.com/job/1",
                    }
                ]
            },
        ),
        (
            LeverAdapter("demo"),
            [
                {
                    "id": "1",
                    "text": "Python Engineer",
                    "descriptionPlain": "Python",
                    "hostedUrl": "https://example.com/job/1",
                }
            ],
        ),
        (
            AshbyAdapter("demo"),
            {
                "jobs": [
                    {
                        "id": "1",
                        "title": "Python Engineer",
                        "descriptionPlain": "Python",
                        "jobUrl": "https://example.com/job/1",
                    }
                ]
            },
        ),
    ],
)
async def test_adapter_contracts(adapter, payload) -> None:
    async def get(self, url):
        return httpx.Response(200, json=payload, request=httpx.Request("GET", url))

    with patch.object(httpx.AsyncClient, "get", get):
        jobs = await adapter.discover("Python")
    assert len(jobs) == 1
    assert jobs[0].status == "UNKNOWN"
    assert jobs[0].external_job_id == "1"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("code", "expected"),
    [(200, "UNKNOWN"), (302, "UNKNOWN"), (404, "CLOSED"), (410, "CLOSED"), (500, "UNKNOWN")],
)
async def test_page_status_is_not_proof_of_open_job(code, expected) -> None:
    async def get(self, url):
        return httpx.Response(code, request=httpx.Request("GET", url))

    job = JobRecord(
        id="1",
        source="test",
        title="Engineer",
        company="Test",
        description="",
        canonical_url="https://example.com/job",
    )
    with (
        patch.object(httpx.AsyncClient, "get", get),
        patch("hireme_ai.jobs.verifier.validate_public_http_url"),
    ):
        result = await verify_job(job)
    assert result.status == expected
