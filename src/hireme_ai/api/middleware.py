import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from hireme_ai.core.workspace import workspace_id

REQUESTS: dict[str, deque[float]] = defaultdict(deque)


async def request_context_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = str(uuid4())
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


async def simple_rate_limit_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    key = workspace_id.get()
    now = time.monotonic()
    for old_key in list(REQUESTS):
        if not REQUESTS[old_key] or now - REQUESTS[old_key][-1] > 60:
            del REQUESTS[old_key]
    if key not in REQUESTS and len(REQUESTS) >= 10000:
        return JSONResponse(
            status_code=429, content={"detail": "Service busy. Please retry later."}
        )
    queue = REQUESTS[key]
    while queue and now - queue[0] > 60:
        queue.popleft()
    if len(queue) >= 120:
        return JSONResponse(
            status_code=429,
            content={
                "code": "RATE_LIMITED",
                "detail": "Too many requests. Please wait a minute.",
                "request_id": request.headers.get("x-request-id", "unknown"),
                "details": {},
            },
        )
    queue.append(now)
    return await call_next(request)
