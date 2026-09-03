import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from hireme_ai.api.access import workspace_access
from hireme_ai.api.body_limit import BodyLimitMiddleware
from hireme_ai.api.middleware import request_context_middleware, simple_rate_limit_middleware
from hireme_ai.api.routers import ALL_ROUTERS
from hireme_ai.core.config import get_settings
from hireme_ai.core.logging import configure_logging
from hireme_ai.db.repositories.workspaces import cleanup
from hireme_ai.db.session import engine

settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async def maintenance():
        while True:
            try:
                await cleanup()
            except Exception:
                logging.getLogger(__name__).error("Expired-data cleanup failed; retry in one hour")
            await asyncio.sleep(3600)

    task = asyncio.create_task(maintenance()) if settings.app_env == "production" else None
    try:
        yield
    finally:
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        await engine.dispose()


app = FastAPI(
    title="HireMe AI API",
    version="0.2.0",
    lifespan=lifespan,
    docs_url=None if settings.app_env == "production" else "/docs",
    redoc_url=None if settings.app_env == "production" else "/redoc",
    openapi_url=None if settings.app_env == "production" else "/openapi.json",
)


@app.exception_handler(SQLAlchemyError)
async def database_error(request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": "Database operation failed. Check Docker, DATABASE_URL and migrations."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(BodyLimitMiddleware)
app.middleware("http")(simple_rate_limit_middleware)
app.middleware("http")(request_context_middleware)
app.middleware("http")(workspace_access)
for router in ALL_ROUTERS:
    app.include_router(router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
async def ready() -> JSONResponse:
    try:
        if engine is None:
            return JSONResponse(
                status_code=503, content={"status": "degraded", "database": "driver unavailable"}
            )
        async with engine.connect() as connection:
            revision = await connection.scalar(text("SELECT version_num FROM alembic_version"))
            if revision != "0002":
                return JSONResponse(
                    status_code=503,
                    content={"status": "degraded", "database": "migration required"},
                )
        return JSONResponse(content={"status": "ready"})
    except Exception:
        return JSONResponse(
            status_code=503, content={"status": "degraded", "database": "unavailable"}
        )
