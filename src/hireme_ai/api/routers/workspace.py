from fastapi import APIRouter

from hireme_ai.api.routers.applications import STORE
from hireme_ai.core.config import get_settings
from hireme_ai.core.workspace import workspace_id
from hireme_ai.db.repositories import workspaces

router = APIRouter(prefix="/api/v1/workspace", tags=["workspace"])


@router.delete("")
async def clear_workspace() -> dict[str, str]:
    if get_settings().app_mode == "live":
        await workspaces.erase()
    else:
        STORE.pop(workspace_id.get(), None)
    return {"status": "deleted"}
