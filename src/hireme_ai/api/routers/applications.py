from uuid import uuid4

from fastapi import APIRouter, HTTPException

from hireme_ai.api.routers.jobs import get_job
from hireme_ai.core.config import get_settings
from hireme_ai.core.workspace import workspace_id
from hireme_ai.db.repositories import workspaces
from hireme_ai.schemas.application import ApplicationRecord, ApplicationStatus

router = APIRouter(prefix="/api/v1/applications", tags=["applications"])
STORE: dict[str, dict[str, ApplicationRecord]] = {}


@router.get("", response_model=list[ApplicationRecord])
async def list_applications() -> list[ApplicationRecord]:
    if get_settings().app_mode == "live":
        return [
            ApplicationRecord.model_validate_json(raw)
            for raw in await workspaces.items("application")
        ]
    return list(STORE.get(workspace_id.get(), {}).values())


@router.post("", response_model=ApplicationRecord)
async def create_application(job_id: str, official_url: str | None = None) -> ApplicationRecord:
    job = await get_job(job_id)
    for item in await list_applications():
        if item.job_id == job.id:
            return item
    item = ApplicationRecord(id=str(uuid4()), job_id=job.id, official_url=job.canonical_url)
    if get_settings().app_mode == "live":
        await workspaces.put("application", item.id, item.model_dump_json())
    else:
        STORE.setdefault(workspace_id.get(), {})[item.id] = item
    return item


@router.patch("/{application_id}", response_model=ApplicationRecord)
async def update_application(application_id: str, status: ApplicationStatus) -> ApplicationRecord:
    item = next((x for x in await list_applications() if x.id == application_id), None)
    if item is None:
        raise HTTPException(404, "Application not found")
    updated = item.model_copy(update={"status": status})
    if get_settings().app_mode == "live":
        await workspaces.put("application", updated.id, updated.model_dump_json())
    else:
        STORE[workspace_id.get()][updated.id] = updated
    return updated
