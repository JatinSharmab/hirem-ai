from unittest.mock import patch

from fastapi.testclient import TestClient

from apps.api.main import app


def test_readiness_fails_when_database_unavailable() -> None:
    with patch("apps.api.main.engine") as engine:
        engine.connect.side_effect = ConnectionError
        response = TestClient(app).get("/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
