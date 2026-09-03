import hashlib
from datetime import UTC, datetime, timedelta
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from hireme_ai.core.config import get_settings
from hireme_ai.core.workspace import workspace_id
from hireme_ai.db.models.domain import JobModel, JobRequirementModel
from hireme_ai.db.session import SessionLocal
from hireme_ai.schemas.job import JobRecord, JobRequirement, JobStatus


def to_record(row: JobModel) -> JobRecord:
    return JobRecord(
        id=row.id,
        source=row.source,
        external_job_id=row.external_job_id,
        title=row.title,
        company=row.company,
        location=row.location,
        description=row.description,
        canonical_url=row.canonical_url,
        status=JobStatus(row.status),
        discovered_at=row.created_at,
        verification_evidence="Imported real job content. Active status has not been verified.",
    )


async def all_jobs() -> list[JobRecord]:
    async with SessionLocal() as session:
        rows = (
            await session.scalars(
                select(JobModel)
                .where(
                    JobModel.owner_id == workspace_id.get(),
                    (JobModel.expires_at.is_(None) | (JobModel.expires_at > datetime.now(UTC))),
                )
                .order_by(JobModel.created_at.desc())
                .limit(200)
            )
        ).all()
        return [to_record(row) for row in rows]


async def find_job(job_id: str) -> JobRecord | None:
    async with SessionLocal() as session:
        row = await session.scalar(
            select(JobModel).where(
                JobModel.id == job_id,
                JobModel.owner_id == workspace_id.get(),
                (JobModel.expires_at.is_(None) | (JobModel.expires_at > datetime.now(UTC))),
            )
        )
        return to_record(row) if row else None


async def save_job(job: JobRecord) -> JobRecord:
    identity = (
        f"{workspace_id.get()}:{job.source}:{job.company}:"
        f"{job.external_job_id or job.canonical_url or job.description}"
    )
    identifier = str(uuid5(NAMESPACE_URL, identity))
    values = dict(
        id=identifier,
        owner_id=workspace_id.get(),
        expires_at=datetime.now(UTC) + timedelta(hours=get_settings().workspace_ttl_hours),
        source=job.source,
        external_job_id=job.external_job_id,
        title=job.title[:300],
        company=job.company[:300],
        location=(job.location or "")[:300] or None,
        description=job.description,
        canonical_url=job.canonical_url,
        description_hash=hashlib.sha256(job.description.encode()).hexdigest(),
        status="UNKNOWN",
    )
    async with SessionLocal() as session:
        statement = insert(JobModel).values(**values)
        await session.execute(
            statement.on_conflict_do_update(
                index_elements=["id"], set_={k: v for k, v in values.items() if k != "id"}
            )
        )
        await session.commit()
    return job.model_copy(update={"id": identifier, "status": JobStatus.UNKNOWN})


async def cached_requirements(job: JobRecord, model: str) -> JobRequirement | None:
    if not await find_job(job.id):
        return None
    # One deterministic cache identity for each job, text revision and model.
    identifier = cache_id(job, model)
    async with SessionLocal() as session:
        row = await session.get(JobRequirementModel, identifier)
        return JobRequirement.model_validate_json(row.raw_json) if row else None


def cache_id(job: JobRecord, model: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"{job.id}:{model}:{job.title}:{job.description}"))


async def save_requirements(job: JobRecord, model: str, req: JobRequirement) -> None:
    if not await find_job(job.id):
        raise ValueError("Job is unavailable in this workspace")
    async with SessionLocal() as session:
        statement = insert(JobRequirementModel).values(
            id=cache_id(job, model),
            job_id=job.id,
            role_family=req.role_family,
            minimum_experience=req.minimum_experience,
            maximum_experience=req.maximum_experience,
            raw_json=req.model_dump_json(),
        )
        await session.execute(statement.on_conflict_do_nothing(index_elements=["id"]))
        await session.commit()
