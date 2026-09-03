"""Exercise real PostgreSQL persistence inside a rolled-back transaction; no AI calls."""

import asyncio
from unittest.mock import patch

from sqlalchemy.ext.asyncio import async_sessionmaker

from hireme_ai.db.repositories import live_jobs
from hireme_ai.db.session import engine
from hireme_ai.schemas.job import JobRecord, JobRequirement


async def main() -> None:
    async with engine.connect() as conn:
        outer = await conn.begin()
        try:
            sessions = async_sessionmaker(
                bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint"
            )
            with patch.object(live_jobs, "SessionLocal", sessions):
                job = JobRecord(
                    id="check",
                    source="storage-check",
                    external_job_id="isolated-check",
                    title="Storage verification",
                    company="Local check",
                    description="Temporary test record; transaction will roll back.",
                )
                first = await live_jobs.save_job(job)
                second = await live_jobs.save_job(job)
                assert first.id == second.id
                loaded = await live_jobs.find_job(first.id)
                assert loaded and loaded.title == job.title
                req = JobRequirement(role_title=job.title, mandatory_skills=["Python"])
                await live_jobs.save_requirements(first, "test-model", req)
                cached = await live_jobs.cached_requirements(first, "test-model")
                assert cached == req
                assert await live_jobs.cached_requirements(first, "different-model") is None
                print(
                    "PASS: PostgreSQL job upsert, reload, requirements cache and model separation."
                )
        finally:
            await outer.rollback()
    await engine.dispose()
    print("All test writes rolled back. No Gemini request made.")


if __name__ == "__main__":
    asyncio.run(main())
