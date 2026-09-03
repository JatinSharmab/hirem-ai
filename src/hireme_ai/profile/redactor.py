import re

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s()-]{7,}\d)(?!\d)")


def redact_pii(text: str) -> str:
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    return PHONE_RE.sub("[REDACTED_PHONE]", text)
