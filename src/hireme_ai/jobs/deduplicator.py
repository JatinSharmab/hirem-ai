from hireme_ai.schemas.job import JobRecord
from hireme_ai.utils.hashing import stable_hash
from hireme_ai.utils.text import normalize_key


def job_fingerprint(job: JobRecord) -> str:
    if job.canonical_url:
        return f"url:{job.canonical_url}"
    if job.external_job_id:
        return f"ext:{job.source}:{job.external_job_id}"
    material = "|".join(
        [
            normalize_key(job.company),
            normalize_key(job.title),
            normalize_key(job.location or ""),
            stable_hash(job.description),
        ]
    )
    return stable_hash(material)


def deduplicate_jobs(jobs: list[JobRecord]) -> list[JobRecord]:
    seen: set[str] = set()
    result: list[JobRecord] = []
    for job in jobs:
        fp = job_fingerprint(job)
        if fp not in seen:
            seen.add(fp)
            result.append(job)
    return result
