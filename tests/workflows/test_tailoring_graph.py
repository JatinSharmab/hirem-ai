import pytest

pytest.importorskip("langgraph")
from hireme_ai.workflows.tailoring_graph import build_tailoring_graph


def test_tailoring_graph_verifies() -> None:
    state = {
        "candidate": {
            "name": "Demo",
            "skills": ["Python"],
            "facts": [
                {
                    "id": "F1",
                    "category": "skill",
                    "subject": "Demo",
                    "predicate": "used",
                    "value": "Python",
                    "source_text": "Python",
                    "confidence": 1.0,
                    "verified_by_user": True,
                    "immutable": True,
                }
            ],
        },
        "requirement": {"role_title": "AI Engineer", "mandatory_skills": ["Python"]},
    }
    result = build_tailoring_graph().invoke(state)
    assert result["verified"] is True
