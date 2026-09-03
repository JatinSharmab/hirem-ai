from datetime import UTC, datetime

import httpx

from hireme_ai.core.security import validate_public_http_url
from hireme_ai.schemas.job import JobRecord, JobStatus


async def verify_job(job: JobRecord, timeout: float = 15.0) -> JobRecord:
    if not job.canonical_url:
        return job.model_copy(
            update={"status": JobStatus.UNKNOWN, "verification_evidence": "No canonical URL"}
        )
    validate_public_http_url(job.canonical_url, resolve_dns=True)
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
            response = await client.get(job.canonical_url)
        if response.status_code in {404, 410}:
            status = JobStatus.CLOSED
        elif 200 <= response.status_code < 400:
            status = JobStatus.UNKNOWN
        else:
            status = JobStatus.UNKNOWN
        return job.model_copy(
            update={
                "status": status,
                "last_verified_at": datetime.now(UTC),
                "verification_evidence": (
                    f"HTTP {response.status_code}; "
                    "page availability alone does not prove an active vacancy"
                ),
            }
        )
    except httpx.HTTPError as exc:
        return job.model_copy(
            update={
                "status": JobStatus.ERROR,
                "last_verified_at": datetime.now(UTC),
                "verification_evidence": f"Verification error: {type(exc).__name__}",
            }
        )
