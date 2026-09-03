from fastapi import APIRouter
from pydantic import BaseModel

from hireme_ai.core.config import get_settings
from hireme_ai.providers.live import structured

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


@router.get("")
async def status() -> dict[str, object]:
    settings = get_settings()
    return {
        "mode": settings.app_mode,
        "public_site": settings.app_env == "production",
        "retention_hours": settings.workspace_ttl_hours,
        "visitor_ai_limit": settings.ai_calls_per_visitor,
        "gemini_key_configured": bool(settings.gemini_api_key),
        "model": settings.llm_model,
        "live_discovery": settings.enable_live_job_discovery,
    }


class ConnectionCheck(BaseModel):
    ok: bool


@router.post("/check-gemini")
async def check_gemini() -> dict[str, object]:
    result = await structured("Return ok=true to confirm connectivity.", {}, ConnectionCheck)
    return {"ok": result.ok, "model": get_settings().llm_model}
