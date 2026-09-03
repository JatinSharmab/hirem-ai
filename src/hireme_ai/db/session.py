from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from hireme_ai.core.config import get_settings
from hireme_ai.core.db_tls import database_connect_args

settings = get_settings()
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=database_connect_args(settings, asynchronous=True),
)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
