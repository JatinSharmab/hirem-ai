from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_demo_profile() -> None:
    response = client.post("/api/v1/profile/demo")
    assert response.status_code == 200
    assert "Synthetic Demo Candidate" in response.json()["name"]
