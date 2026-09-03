from hireme_ai.jobs.deduplicator import deduplicate_jobs
from hireme_ai.schemas.job import JobRecord


def test_duplicate_urls_collapse() -> None:
    a = JobRecord(
        id="1",
        source="x",
        title="AI",
        company="A",
        description="same",
        canonical_url="https://a.com/j/1",
    )
    b = JobRecord(
        id="2",
        source="x",
        title="AI",
        company="A",
        description="same",
        canonical_url="https://a.com/j/1",
    )
    assert len(deduplicate_jobs([a, b])) == 1
