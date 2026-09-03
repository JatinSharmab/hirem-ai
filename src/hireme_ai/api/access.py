import hmac
from collections.abc import Awaitable, Callable
from uuid import UUID

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from hireme_ai.core.config import get_settings
from hireme_ai.core.workspace import workspace_id


async def workspace_access(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    settings = get_settings()
    public_path = request.url.path in {"/health", "/ready"}
    if settings.app_env == "production" and not public_path:
        supplied = request.headers.get("authorization", "")
        if not hmac.compare_digest(
            supplied.encode(), ("Bearer " + (settings.api_gateway_key or "")).encode()
        ):
            return JSONResponse(
                status_code=401,
                content={"detail": "Use the public website to access this service."},
            )
    owner = request.headers.get("x-workspace-id", "")
    if owner:
        try:
            parsed = UUID(owner)
            if parsed.version != 4:
                raise ValueError
            owner = str(parsed)
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "Invalid visitor session."})
    elif settings.app_env == "production" and not public_path:
        return JSONResponse(status_code=400, content={"detail": "Visitor session is required."})
    else:
        owner = "legacy-local"
    token = workspace_id.set(owner)
    try:
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    finally:
        workspace_id.reset(token)
