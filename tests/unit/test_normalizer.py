from hireme_ai.jobs.normalizer import normalize_job
from hireme_ai.schemas.job import JobRecord


def test_normalize_job() -> None:
    job = JobRecord(
        id="1",
        source="x",
        title="  AI   Engineer ",
        company="  Acme ",
        description="a  b",
        canonical_url="https://EXAMPLE.com/a/?utm_source=x",
    )
    result = normalize_job(job)
    assert result.title == "AI Engineer"
    assert result.company == "Acme"
    assert result.canonical_url == "https://example.com/a"
