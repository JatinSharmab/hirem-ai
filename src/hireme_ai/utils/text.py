import re


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", normalize_space(text).lower()).strip()
