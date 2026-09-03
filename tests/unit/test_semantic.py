from hireme_ai.matching.semantic import cosine_similarity


def test_cosine_identity() -> None:
    assert cosine_similarity([1, 0], [1, 0]) == 1.0
