from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from hireme_ai.core.config import get_settings
from hireme_ai.core.db_tls import database_connect_args
from hireme_ai.db import models  # noqa: F401
from hireme_ai.db.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
config.set_main_option(
    "sqlalchemy.url", get_settings().database_url.replace("+asyncpg", "+psycopg").replace("%", "%%")
)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=database_connect_args(get_settings(), asynchronous=False),
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_offline() if context.is_offline_mode() else run_migrations_online()
