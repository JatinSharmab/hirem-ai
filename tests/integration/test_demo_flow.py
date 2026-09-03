import base64
from io import BytesIO

import pymupdf
from docx import Document
from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_demo_flow_and_exports() -> None:
    candidate = client.post("/api/v1/profile/demo").json()
    job = client.get("/api/v1/jobs").json()[0]
    requirement = client.get(f"/api/v1/jobs/{job['id']}/requirements").json()
    match = client.post(
        "/api/v1/matches", json={"candidate": candidate, "job": job, "requirement": requirement}
    )
    assert match.status_code == 200
    assert match.json()["score"]["total"] > 0
    version = client.post(
        "/api/v1/resumes/tailor", json={"candidate": candidate, "requirement": requirement}
    ).json()
    assert version["verification_status"] == "PASSED"
    for fmt in ("pdf", "docx"):
        response = client.post(
            f"/api/v1/resumes/export/{fmt}", json={"candidate": candidate, "version": version}
        )
        assert response.status_code == 200
        data = base64.b64decode(response.json()["content"])
        if fmt == "pdf":
            with pymupdf.open(stream=data, filetype="pdf") as pdf:
                text = "".join(page.get_text() for page in pdf)
        else:
            text = "\n".join(p.text for p in Document(BytesIO(data)).paragraphs)
        assert "Verified skill:" in text
    version["bullets"][0]["text"] = "Built production Kubernetes systems at Google"
    assert (
        client.post(
            "/api/v1/resumes/export/pdf", json={"candidate": candidate, "version": version}
        ).status_code
        == 422
    )
    record = client.post("/api/v1/applications", params={"job_id": job["id"]}).json()
    assert (
        client.patch(
            f"/api/v1/applications/{record['id']}", params={"status": "SHORTLISTED"}
        ).status_code
        == 200
    )
    assert client.get("/api/v1/insights/skills").json()["skills"]


def test_invalid_requests() -> None:
    assert (
        client.patch("/api/v1/applications/missing", params={"status": "APPLIED"}).status_code
        == 404
    )
    assert (
        client.patch("/api/v1/applications/missing", params={"status": "FAKE"}).status_code == 422
    )
    assert (
        client.post("/api/v1/profile/parse", files={"file": ("bad.pdf", b"not a PDF")}).status_code
        == 422
    )
    assert client.get("/api/v1/runs/nonexistent").status_code == 404


def test_empty_resume_cannot_pass() -> None:
    result = client.post(
        "/api/v1/resumes/tailor",
        json={"candidate": {"name": "Empty"}, "requirement": {"role_title": "Engineer"}},
    )
    assert result.json()["verification_status"] == "FAILED"
