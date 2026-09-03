from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from apps.api.main import app
from hireme_ai.core.config import get_settings
from hireme_ai.providers.live import ExtractedFact, ExtractedProfile, extract_profile
from hireme_ai.schemas.job import JobRecord, JobRequirement


def live(monkeypatch):
    monkeypatch.setenv("APP_MODE", "live")
    get_settings.cache_clear()


def test_live_missing_key_and_no_demo(monkeypatch) -> None:
    live(monkeypatch)
    client = TestClient(app)
    assert client.post("/api/v1/profile/demo").status_code == 409
    status = client.get("/api/v1/settings").json()
    assert status["mode"] == "live"
    assert status["gemini_key_configured"] is False
    assert "gemini_api_key" not in status
    assert client.post("/api/v1/settings/check-gemini").status_code == 503
    assert (
        client.post("/api/v1/profile/parse", files={"file": ("x.pdf", b"%PDF")}).status_code == 422
    )


@pytest.mark.asyncio
async def test_grounding_rejects_invented_quotes() -> None:
    response = ExtractedProfile(
        name="Candidate",
        summary="",
        experience_years=0,
        locations=[],
        facts=[
            ExtractedFact(category="skill", value="Python", source_text="Used Python"),
            ExtractedFact(category="skill", value="AWS", source_text="Used AWS"),
            ExtractedFact(category="skill", value="Kubernetes", source_text="Used Python"),
        ],
    )
    with patch("hireme_ai.providers.live.structured", AsyncMock(return_value=response)):
        profile = await extract_profile("Used Python in a project.")
    assert profile.skills == ["Python"]
    assert all(not f.verified_by_user for f in profile.facts)


def test_live_jobs_are_not_fixtures(monkeypatch) -> None:
    live(monkeypatch)
    with patch("hireme_ai.api.routers.jobs.live_jobs.all_jobs", AsyncMock(return_value=[])):
        assert TestClient(app).get("/api/v1/jobs").json() == []


def test_jd_analysis_uses_cache_without_provider(monkeypatch) -> None:
    live(monkeypatch)
    job = JobRecord(id="x", source="manual", title="Engineer", company="Real", description="Python")
    req = JobRequirement(role_title="Engineer", mandatory_skills=["Python"])
    with (
        patch("hireme_ai.api.routers.jobs.live_jobs.find_job", AsyncMock(return_value=job)),
        patch(
            "hireme_ai.api.routers.jobs.live_jobs.cached_requirements", AsyncMock(return_value=req)
        ),
        patch("hireme_ai.api.routers.jobs.extract_requirements", AsyncMock()) as provider,
    ):
        response = TestClient(app).post("/api/v1/jobs/x/analyze")
    assert response.status_code == 200
    provider.assert_not_called()


@pytest.mark.asyncio
async def test_provider_failure_does_not_leak_secret(monkeypatch) -> None:
    from hireme_ai.providers.live import structured

    live(monkeypatch)
    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    get_settings.cache_clear()
    with patch("hireme_ai.providers.live.create_llm", side_effect=RuntimeError("test-secret")):
        with pytest.raises(HTTPException) as error:
            await structured("test", {}, JobRequirement)
    assert "test-secret" not in str(error.value.detail)


@pytest.mark.asyncio
async def test_live_tailoring_cannot_invent_words() -> None:
    from hireme_ai.resume.live import FactSelection, build_live_resume
    from hireme_ai.schemas.candidate import CandidateFact, CandidateProfile

    candidate = CandidateProfile(
        name="Test",
        facts=[
            CandidateFact(
                id="F1",
                category="project",
                subject="Test",
                predicate="built",
                value="API",
                source_text="Built a Python API.",
                verified_by_user=True,
            )
        ],
    )
    with patch(
        "hireme_ai.resume.live.structured", AsyncMock(return_value=FactSelection(fact_ids=["F1"]))
    ):
        version = await build_live_resume(
            candidate, JobRequirement(role_title="Engineer"), None, None
        )
    assert version.bullets[0].text == "Built a Python API."
    assert version.verification_status == "PASSED"
    with patch(
        "hireme_ai.resume.live.structured", AsyncMock(return_value=FactSelection(fact_ids=["FAKE"]))
    ):
        with pytest.raises(HTTPException):
            await build_live_resume(candidate, JobRequirement(role_title="Engineer"), None, None)


def test_gemini_check_only_returns_public_status(monkeypatch) -> None:
    from hireme_ai.api.routers.settings import ConnectionCheck

    live(monkeypatch)
    with patch(
        "hireme_ai.api.routers.settings.structured",
        AsyncMock(return_value=ConnectionCheck(ok=True)),
    ):
        response = TestClient(app).post("/api/v1/settings/check-gemini")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_live_analysis_calls_provider_and_saves(monkeypatch) -> None:
    live(monkeypatch)
    job = JobRecord(id="x", source="manual", title="Engineer", company="Real", description="Python")
    req = JobRequirement(role_title="Engineer", mandatory_skills=["Python"])
    with (
        patch("hireme_ai.api.routers.jobs.live_jobs.find_job", AsyncMock(return_value=job)),
        patch(
            "hireme_ai.api.routers.jobs.live_jobs.cached_requirements", AsyncMock(return_value=None)
        ),
        patch(
            "hireme_ai.api.routers.jobs.extract_requirements", AsyncMock(return_value=req)
        ) as provider,
        patch("hireme_ai.api.routers.jobs.live_jobs.save_requirements", AsyncMock()) as save,
    ):
        response = TestClient(app).post("/api/v1/jobs/x/analyze")
    assert response.status_code == 200
    provider.assert_awaited_once()
    save.assert_awaited_once()


def test_live_ui_has_no_demo_profile_button(monkeypatch) -> None:
    from pathlib import Path

    from client.api import HireMeAPI
    from streamlit.testing.v1 import AppTest

    live(monkeypatch)
    client = TestClient(app)

    def request(self, method, path, **kwargs):
        response = client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()

    with (
        patch.object(HireMeAPI, "request", request),
        patch("hireme_ai.api.routers.jobs.live_jobs.all_jobs", AsyncMock(return_value=[])),
    ):
        page = AppTest.from_file(Path("apps/ui/Home.py").resolve(), default_timeout=30).run()
        page.switch_page("pages/1_Candidate_Profile.py").run()
        assert not page.exception
        assert all(b.label != "Try Demo Candidate" for b in page.button)
        assert page.checkbox[0].value is False
        page.switch_page("pages/2_Job_Discovery.py").run()
        assert not page.exception
        assert any(b.label == "Save job" for b in page.button)
        page.switch_page("pages/9_Settings.py").run()
        assert not page.exception
