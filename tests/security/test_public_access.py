from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from apps.api.main import app
from hireme_ai.core.config import Settings, get_settings


def production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_SSL", "true")
    monkeypatch.setenv("APP_MODE", "live")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-not-a-real-key")
    monkeypatch.setenv("API_GATEWAY_KEY", "x" * 40)
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@db.example.com/test")
    get_settings.cache_clear()


def test_production_refuses_missing_gateway() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", app_mode="live", api_gateway_key=None)


def test_gateway_and_workspace_required(monkeypatch) -> None:
    production(monkeypatch)
    client = TestClient(app)
    assert client.get("/api/v1/settings").status_code == 401
    assert (
        client.get("/api/v1/settings", headers={"Authorization": "Bearer wrong"}).status_code == 401
    )
    headers = {"Authorization": "Bearer " + "x" * 40}
    assert client.get("/api/v1/settings", headers=headers).status_code == 400
    headers["X-Workspace-ID"] = "not-a-session"
    assert client.get("/api/v1/settings", headers=headers).status_code == 400
    headers["X-Workspace-ID"] = str(uuid4())
    response = client.get("/api/v1/settings", headers=headers)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert "x" * 40 not in response.text


def test_application_isolation_in_demo() -> None:
    client = TestClient(app)
    a = {"X-Workspace-ID": str(uuid4())}
    b = {"X-Workspace-ID": str(uuid4())}
    item = client.post("/api/v1/applications", params={"job_id": "demo-job-1"}, headers=a).json()
    assert client.get("/api/v1/applications", headers=b).json() == []
    assert (
        client.patch(
            f"/api/v1/applications/{item['id']}", params={"status": "APPLIED"}, headers=b
        ).status_code
        == 404
    )


def test_oversized_body_rejected() -> None:
    response = TestClient(app).post("/api/v1/matches", content=b"x" * (7 * 1024 * 1024))
    assert response.status_code == 413


def test_production_requires_verified_database_tls(monkeypatch) -> None:
    production(monkeypatch)
    with pytest.raises(ValidationError, match="verified TLS"):
        Settings(database_ssl=False)


def test_clear_workspace_only_clears_current_visitor() -> None:
    client = TestClient(app)
    a = {"X-Workspace-ID": str(uuid4())}
    b = {"X-Workspace-ID": str(uuid4())}
    for headers in (a, b):
        assert (
            client.post(
                "/api/v1/applications", params={"job_id": "demo-job-1"}, headers=headers
            ).status_code
            == 200
        )
    assert client.delete("/api/v1/workspace", headers=a).status_code == 200
    assert client.get("/api/v1/applications", headers=a).json() == []
    assert len(client.get("/api/v1/applications", headers=b).json()) == 1
