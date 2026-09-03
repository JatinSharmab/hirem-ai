"""Server-side anonymous workspace context; never take identity from request bodies."""

from contextvars import ContextVar

workspace_id: ContextVar[str] = ContextVar("workspace_id", default="legacy-local")
