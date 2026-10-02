"""Real Streamlit script execution, with API calls served by FastAPI TestClient."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest

from apps.api.main import app

sys.path.insert(0, str(Path("apps/ui").resolve()))
from client.api import HireMeAPI  # noqa: E402

client = TestClient(app)


def test_public_client_refuses_plaintext_gateway(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(ValueError, match="HTTPS"):
        HireMeAPI("http://example.com")


def test_public_privacy_page_hides_local_controls() -> None:
    def public_request(self, method, path, **kwargs):
        result = request(self, method, path, **kwargs)
        if path == "/api/v1/settings":
            result["public_site"] = True
        return result

    with patch.object(HireMeAPI, "request", public_request):
        page = AppTest.from_file(Path("apps/ui/Home.py").resolve(), default_timeout=30).run()
        page.switch_page("pages/9_Settings.py").run()
        assert not page.exception
        assert not any(b.label == "Test Gemini connection" for b in page.button)
        clear = next(b for b in page.button if b.label == "Clear my data")
        assert clear.disabled
        page.checkbox[0].check().run()
        next(b for b in page.button if b.label == "Clear my data").click().run()
        assert not page.exception
        assert any("cleared" in message.value for message in page.success)


def request(self, method, path, **kwargs):
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    return response.json()


def test_ui_demo_pages() -> None:
    with patch.object(HireMeAPI, "request", request):
        profile = AppTest.from_file(Path("apps/ui/Home.py").resolve(), default_timeout=30).run()
        profile.switch_page("pages/1_Candidate_Profile.py").run()
        next(b for b in profile.button if b.label == "Try Demo Candidate").click().run()
        assert not profile.exception
        next(b for b in profile.button if b.label == "Save reviewed facts").click().run()
        assert not profile.exception
        candidate = profile.session_state["candidate"]
        for filename in [
            "2_Job_Discovery.py",
            "3_Job_Match.py",
            "4_Resume_Studio.py",
            "5_Applications.py",
            "6_Market_Insights.py",
            "7_Developer_Trace.py",
            "8_Architecture.py",
        ]:
            page = AppTest.from_file(Path("apps/ui/Home.py").resolve(), default_timeout=30)
            page.session_state["candidate"] = candidate
            page.run()
            page.switch_page("pages/" + filename).run()
            assert not page.exception, filename
            if filename in ("3_Job_Match.py", "4_Resume_Studio.py", "5_Applications.py"):
                page.button[0].click().run()
                assert not page.exception, filename
            if filename == "4_Resume_Studio.py":
                page.checkbox[0].check().run()
                assert not page.exception
                assert len(page.get("download_button")) == 2


def test_saved_jobs_and_selected_role_flow() -> None:
    with patch.object(HireMeAPI, "request", request):
        page = AppTest.from_file(Path("apps/ui/Home.py").resolve(), default_timeout=30)
        page.session_state["candidate"] = client.post("/api/v1/profile/demo").json()
        page.run().switch_page("pages/2_Job_Discovery.py").run()
        page.button(key="save-demo-job-1").click().run()
        assert page.session_state["saved_jobs"] == ["demo-job-1"]
        page.selectbox[0].select("Saved jobs").run()
        assert len([b for b in page.button if b.label.startswith("Explore fit")]) == 1
        page.text_input[0].set_value("no-such-role").run()
        assert not page.exception
        assert any("No roles" in heading.value for heading in page.subheader)
        page.text_input[0].set_value("").run()
        page.button(key="fit-demo-job-1").click().run()
        assert page.session_state["selected_job_id"] == "demo-job-1"
        assert not page.exception
        # AppTest needs an explicit page selection after a programmatic redirect.
        page.switch_page("pages/3_Job_Match.py").run()
        next(b for b in page.button if b.label == "Calculate Career Fit Score").click().run()
        assert page.metric[0].label == "Career Fit Score"
        page.switch_page("pages/4_Resume_Studio.py").run()
        assert page.selectbox[0].value["id"] == "demo-job-1"
        page.button[0].click().run()
        assert not page.exception
        assert page.session_state["versions"][0]["version"]["target_job_id"] == "demo-job-1"
