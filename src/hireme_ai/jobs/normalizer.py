from hireme_ai.schemas.job import JobRecord
from hireme_ai.utils.text import normalize_space
from hireme_ai.utils.urls import canonicalize_url


def normalize_job(job: JobRecord) -> JobRecord:
    data = job.model_dump()
    data["title"] = normalize_space(job.title)
    data["company"] = normalize_space(job.company)
    data["location"] = normalize_space(job.location) if job.location else None
    data["description"] = normalize_space(job.description)
    if job.canonical_url:
        data["canonical_url"] = canonicalize_url(job.canonical_url)
    return JobRecord(**data)
