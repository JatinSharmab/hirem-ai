"""Production start: serialize additive migrations, then serve one bounded API worker."""

import os
import sys
from pathlib import Path

import uvicorn
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from hireme_ai.core.config import get_settings
from hireme_ai.core.db_tls import database_connect_args
from hireme_ai.db import models  # noqa: F401
from hireme_ai.db.base import Base


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))
    os.chdir(project_root)
    settings = get_settings()  # Fail closed before binding a public socket.
    migration_engine = create_engine(
        settings.database_url.replace("+asyncpg", "+psycopg"),
        connect_args=database_connect_args(settings, asynchronous=False),
    )
    try:
        with migration_engine.connect() as connection:
            acquired = connection.scalar(text("SELECT pg_try_advisory_lock(812740001)"))
            if not acquired:
                raise RuntimeError("Another migration is running. Retry deployment shortly.")
            try:
                command.upgrade(Config("alembic.ini"), "head")
                if settings.app_env == "production":
                    # The API connects as table owner. Browser-facing database roles
                    # must never bypass the application's workspace isolation.
                    roles = connection.scalars(
                        text(
                            "SELECT rolname FROM pg_roles "
                            "WHERE rolname IN ('anon', 'authenticated')"
                        )
                    ).all()
                    quote = connection.dialect.identifier_preparer.quote
                    for table in [*Base.metadata.tables, "alembic_version"]:
                        qualified = "public." + quote(table)
                        connection.execute(
                            text(f"ALTER TABLE {qualified} ENABLE ROW LEVEL SECURITY")
                        )
                        for role in roles:
                            connection.execute(
                                text(f"REVOKE ALL ON TABLE {qualified} FROM {quote(role)}")
                            )
                    connection.commit()
            finally:
                connection.execute(text("SELECT pg_advisory_unlock(812740001)"))
    finally:
        migration_engine.dispose()
    uvicorn.run(
        "apps.api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        workers=1,
        limit_concurrency=40,
        timeout_keep_alive=5,
        proxy_headers=False,
    )


if __name__ == "__main__":
    main()
