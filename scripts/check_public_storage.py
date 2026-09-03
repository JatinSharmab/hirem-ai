"""Database isolation, expiry and quota checks; all changes are rolled back."""

import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import async_sessionmaker

from hireme_ai.core.workspace import workspace_id
from hireme_ai.db.models.domain import JobModel
from hireme_ai.db.repositories import live_jobs, workspaces
from hireme_ai.db.session import engine
from hireme_ai.schemas.job import JobRecord


async def main() -> None:
    async with engine.connect() as connection:
        outer = await connection.begin()
        token = workspace_id.set(str(uuid4()))
        try:
            sessions = async_sessionmaker(
                bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
            )
            with (
                patch.object(live_jobs, "SessionLocal", sessions),
                patch.object(workspaces, "SessionLocal", sessions),
            ):
                owner_a = workspace_id.get()
                job = JobRecord(
                    id="test",
                    source="isolation-test",
                    external_job_id="same-job",
                    title="Isolation test",
                    company="Test",
                    description="Synthetic rollback check",
                )
                a = await live_jobs.save_job(job)
                await workspaces.put("application", "one", '{"private":"A"}')
                category = "audit-" + str(uuid4())
                await workspaces.consume(category, 1, 2)
                try:
                    await workspaces.consume(category, 1, 2)
                    raise AssertionError("Visitor limit did not reject")
                except HTTPException as exc:
                    assert exc.status_code == 429
                workspace_id.set(str(uuid4()))
                assert await live_jobs.find_job(a.id) is None
                assert await workspaces.get("application", "one") is None
                b = await live_jobs.save_job(job)
                assert a.id != b.id
                await workspaces.consume(category, 1, 2)
                workspace_id.set(str(uuid4()))
                try:
                    await workspaces.consume(category, 1, 2)
                    raise AssertionError("Global limit did not reject")
                except HTTPException as exc:
                    assert exc.status_code == 429
                workspace_id.set(owner_a)
                await connection.execute(
                    update(JobModel)
                    .where(JobModel.id == a.id)
                    .values(expires_at=datetime.now(UTC) - timedelta(seconds=1))
                )
                assert await live_jobs.find_job(a.id) is None
                await workspaces.erase()
                assert await workspaces.get("application", "one") is None
                print("PASS: two-visitor isolation, expiry, deletion, visitor and global quotas.")
        finally:
            workspace_id.reset(token)
            await outer.rollback()
    await engine.dispose()
    print("All test changes rolled back; no Gemini calls.")


if __name__ == "__main__":
    asyncio.run(main())
