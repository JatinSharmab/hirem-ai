import hashlib


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()
