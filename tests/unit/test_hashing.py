from hireme_ai.utils.hashing import stable_hash


def test_hash_stable() -> None:
    assert stable_hash("x") == stable_hash("x")
    assert stable_hash("x") != stable_hash("y")
