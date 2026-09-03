from hireme_ai.matching.skills import normalize_skill


def test_aliases() -> None:
    assert normalize_skill("Postgres") == "PostgreSQL"
    assert normalize_skill("JS") == "JavaScript"
