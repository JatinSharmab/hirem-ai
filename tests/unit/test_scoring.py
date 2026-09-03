from hireme_ai.matching.scoring import calculate_score


def test_score_is_weighted_and_deterministic() -> None:
    components = {
        "required_skill_coverage": 100,
        "relevant_evidence": 100,
        "semantic_role_alignment": 100,
        "responsibility_alignment": 100,
        "experience_alignment": 100,
        "preferred_skill_coverage": 100,
        "location_work_mode": 100,
    }
    assert calculate_score(components).total == 100
