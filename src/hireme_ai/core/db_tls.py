import ssl
from typing import Any

from hireme_ai.core.config import Settings


def database_connect_args(settings: Settings, *, asynchronous: bool) -> dict[str, Any]:
    if not settings.database_ssl:
        return {}
    if asynchronous:
        return {"ssl": ssl.create_default_context(cafile=settings.database_ssl_ca)}
    return {"sslmode": "verify-full", "sslrootcert": settings.database_ssl_ca or "system"}
