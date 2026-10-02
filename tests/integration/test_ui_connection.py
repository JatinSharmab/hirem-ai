"""Cold-start recovery must never repeat AI calls, uploads or mutations."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest
from streamlit.testing.v1 import AppTest

sys.path.insert(0, str(Path("apps/ui").resolve()))
from client import api  # noqa: E402

RUNTIME = {"mode": "live", "public_site": True}


@pytest.fixture
def connection(monkeypatch):
    elapsed = [0.0]

    def sleep(seconds):
        elapsed[0] += seconds

    monkeypatch.setattr(api, "time", SimpleNamespace(monotonic=lambda: elapsed[0], sleep=sleep))
    monkeypatch.setattr(api.st, "session_state", {})
    monkeypatch.setenv("API_GATEWAY_KEY", "test-gateway")
    return api.HireMeAPI("https://example.com"), elapsed


def response(status=200, *, payload=None, html=False):
    request = httpx.Request("GET", "https://example.com/api/v1/settings")
    if html:
        return httpx.Response(status, text="<html>Host loading</html>", request=request)
    return httpx.Response(status, json=payload if payload is not None else RUNTIME, request=request)


def test_startup_recovers_from_gateway_errors_and_loading_html(connection):
    client, elapsed = connection
    replies = [response(code, html=True) for code in (502, 503, 504, 200)] + [response()]
    with patch.object(api.httpx, "request", side_effect=replies) as send:
        assert client.get("/api/v1/settings") == RUNTIME
    assert send.call_count == 5
    assert elapsed[0] == 12
    owners = {call.kwargs["headers"]["X-Workspace-ID"] for call in send.call_args_list}
    assert len(owners) == 1
    assert all(
        c.kwargs["headers"]["Authorization"] == "Bearer test-gateway" for c in send.call_args_list
    )


def test_startup_recovers_from_timeout_and_invalid_json_shape(connection):
    client, _ = connection
    with patch.object(
        api.httpx,
        "request",
        side_effect=[httpx.ReadTimeout("asleep"), response(payload=[]), response()],
    ) as send:
        assert client.get("/api/v1/settings") == RUNTIME
    assert send.call_count == 3


def test_startup_wait_is_bounded(connection, monkeypatch):
    client, elapsed = connection
    monkeypatch.setattr(api, "STARTUP_WAIT_SECONDS", 6)
    with patch.object(api.httpx, "request", return_value=response(502, html=True)) as send:
        with pytest.raises(api.ServiceUnavailableError):
            client.get("/api/v1/settings")
    assert elapsed[0] == 6
    assert send.call_count == 2
    assert send.call_args_list[-1].kwargs["timeout"] == 3


@pytest.mark.parametrize("status", [401, 403, 429, 500])
def test_settings_does_not_retry_nontransient_errors(connection, status):
    client, elapsed = connection
    with patch.object(api.httpx, "request", return_value=response(status)) as send:
        with pytest.raises(httpx.HTTPStatusError):
            client.get("/api/v1/settings")
    assert send.call_count == 1
    assert elapsed[0] == 0


@pytest.mark.parametrize(
    ("method", "path"),
    [("POST", "/api/v1/profile/parse"), ("GET", "/api/v1/jobs/job-1/requirements")],
)
@pytest.mark.parametrize("failure", ["gateway", "timeout", "html"])
def test_ai_and_mutating_requests_are_never_repeated(connection, method, path, failure):
    client, elapsed = connection
    result = response(502 if failure == "gateway" else 200, html=True)
    with patch.object(api.httpx, "request") as send:
        if failure == "timeout":
            send.side_effect = httpx.ReadTimeout("connection lost")
        else:
            send.return_value = result
        with pytest.raises(
            (httpx.HTTPStatusError, httpx.RequestError, api.ServiceUnavailableError)
        ):
            client.request(method, path)
    assert send.call_count == 1
    assert elapsed[0] == 0


def test_home_has_styled_recovery_and_preserves_workspace_on_reload():
    def recovered(self, method, path, **kwargs):
        return RUNTIME if path == "/api/v1/settings" else []

    page = AppTest.from_file(Path("apps/ui/Home.py").resolve(), default_timeout=30)
    page.session_state["_workspace_id"] = "retained-workspace"
    with patch.object(api.HireMeAPI, "request", side_effect=api.ServiceUnavailableError()):
        page.run()
    assert not page.exception
    assert "temporarily unavailable" in page.warning[0].value
    assert any("<style>" in element.value for element in page.markdown)
    with patch.object(api.HireMeAPI, "request", recovered):
        page.button(key="reload_after_api_error").click().run()
    assert not page.exception
    assert not page.warning
    assert page.session_state["_workspace_id"] == "retained-workspace"
    assert page.metric[0].label == "Opportunities"


@pytest.mark.parametrize(
    ("reply", "expected"),
    [
        (response(502, html=True), "The service is starting or temporarily unavailable"),
        (response(502, payload={"detail": "Model unavailable."}), "Model unavailable."),
        (response(403, payload=[]), "The request could not be completed"),
    ],
)
def test_gateway_html_is_hidden_but_actionable_api_errors_are_kept(reply, expected):
    error = httpx.HTTPStatusError("failed", request=reply.request, response=reply)
    page = AppTest.from_file(Path("apps/ui/Home.py").resolve(), default_timeout=30)
    with patch.object(api.HireMeAPI, "request", side_effect=error):
        page.run()
    assert not page.exception
    assert expected in page.error[0].value
    assert "<html>" not in page.error[0].value
    assert page.button(key="reload_after_api_error")
