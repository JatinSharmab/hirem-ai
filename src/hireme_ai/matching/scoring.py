from pathlib import Path

import yaml

from hireme_ai.schemas.match import ScoreBreakdown

COMPONENTS = [
    "required_skill_coverage",
    "relevant_evidence",
    "semantic_role_alignment",
    "responsibility_alignment",
    "experience_alignment",
    "preferred_skill_coverage",
    "location_work_mode",
]


def load_weights(path: str = "config/scoring.yaml") -> dict[str, float]:
    data = yaml.safe_load(Path(path).read_text())
    return {k: float(v) for k, v in data["weights"].items()}


def calculate_score(
    components: dict[str, float], weights: dict[str, float] | None = None
) -> ScoreBreakdown:
    weights = weights or load_weights()
    values = {key: max(0.0, min(100.0, float(components.get(key, 0)))) for key in COMPONENTS}
    total = sum(values[key] * weights[key] for key in COMPONENTS)
    return ScoreBreakdown(**values, total=round(total, 2))
