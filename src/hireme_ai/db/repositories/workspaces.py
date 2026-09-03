from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from hireme_ai.core.config import get_settings
from hireme_ai.core.workspace import workspace_id
from hireme_ai.db.models.domain import JobModel
from hireme_ai.db.models.public import UsageBucket, WorkspaceItem
from hireme_ai.db.session import SessionLocal


async def put(kind: str, item_id: str, content: str) -> None:
    expiry = datetime.now(UTC) + timedelta(hours=get_settings().workspace_ttl_hours)
    async with SessionLocal() as session:
        stmt = insert(WorkspaceItem).values(
            owner_id=workspace_id.get(),
            kind=kind,
            item_id=item_id,
            content_json=content,
            expires_at=expiry,
        )
        await session.execute(
            stmt.on_conflict_do_update(
                index_elements=["owner_id", "kind", "item_id"],
                set_={"content_json": content, "expires_at": expiry},
            )
        )
        await session.commit()


async def items(kind: str) -> list[str]:
    async with SessionLocal() as session:
        return list(
            await session.scalars(
                select(WorkspaceItem.content_json)
                .where(
                    WorkspaceItem.owner_id == workspace_id.get(),
                    WorkspaceItem.kind == kind,
                    WorkspaceItem.expires_at > datetime.now(UTC),
                )
                .order_by(WorkspaceItem.expires_at.desc())
                .limit(200)
            )
        )


async def get(kind: str, item_id: str) -> str | None:
    async with SessionLocal() as session:
        return await session.scalar(
            select(WorkspaceItem.content_json).where(
                WorkspaceItem.owner_id == workspace_id.get(),
                WorkspaceItem.kind == kind,
                WorkspaceItem.item_id == item_id,
                WorkspaceItem.expires_at > datetime.now(UTC),
            )
        )


async def erase() -> None:
    async with SessionLocal() as session:
        await session.execute(
            delete(WorkspaceItem).where(WorkspaceItem.owner_id == workspace_id.get())
        )
        await session.execute(delete(JobModel).where(JobModel.owner_id == workspace_id.get()))
        await session.commit()


async def consume(category: str, visitor_limit: int, global_limit: int) -> None:
    """Both budgets are charged atomically, including failed provider attempts."""
    now = datetime.now(UTC)
    day = now.strftime("%Y-%m-%d")
    async with SessionLocal() as session:
        for owner, limit in [("global", global_limit), (workspace_id.get(), visitor_limit)]:
            stmt = insert(UsageBucket).values(
                bucket=f"{category}:{day}:{owner}", count=1, expires_at=now + timedelta(days=2)
            )
            result = await session.scalar(
                stmt.on_conflict_do_update(
                    index_elements=["bucket"],
                    set_={"count": UsageBucket.count + 1},
                    where=UsageBucket.count < limit,
                ).returning(UsageBucket.count)
            )
            if result is None:
                raise HTTPException(
                    429, "Today's portfolio usage allowance is exhausted. Try again tomorrow (UTC)."
                )
        await session.commit()


async def cleanup() -> None:
    now = datetime.now(UTC)
    async with SessionLocal() as session:
        await session.execute(delete(WorkspaceItem).where(WorkspaceItem.expires_at <= now))
        await session.execute(delete(JobModel).where(JobModel.expires_at <= now))
        await session.execute(delete(UsageBucket).where(UsageBucket.expires_at <= now))
        await session.commit()
