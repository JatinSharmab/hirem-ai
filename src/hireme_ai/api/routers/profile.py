import asyncio
import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from hireme_ai.core.config import get_settings
from hireme_ai.core.exceptions import ValidationError
from hireme_ai.profile.extractor import demo_extract_profile
from hireme_ai.profile.parser import parse_resume_bytes
from hireme_ai.providers.live import extract_profile
from hireme_ai.schemas.candidate import CandidateProfile

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


@router.post("/demo", response_model=CandidateProfile)
async def demo_profile() -> CandidateProfile:
    if get_settings().app_mode == "live":
        raise HTTPException(409, "Demo profiles are disabled in live mode.")
    return CandidateProfile.model_validate(json.loads(Path("data/demo/candidate.json").read_text()))


@router.post("/parse", response_model=CandidateProfile)
async def parse_profile(
    file: Annotated[UploadFile, File()], consent: bool = False
) -> CandidateProfile:
    if get_settings().app_mode == "live" and not consent:
        raise HTTPException(422, "Consent is required to send resume text to Gemini.")
    limit = get_settings().max_upload_mb
    content = await file.read(limit * 1024 * 1024 + 1)
    try:
        text = await asyncio.to_thread(
            parse_resume_bytes, file.filename or "resume", content, limit
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if get_settings().app_mode == "live":
        return await extract_profile(text)
    return demo_extract_profile(text)
