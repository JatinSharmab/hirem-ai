from typing import TypedDict


class ProfileState(TypedDict, total=False):
    filename: str
    raw_text: str
    redacted_text: str
    profile: dict[str, object]
    warnings: list[str]


class DiscoveryState(TypedDict, total=False):
    query: str
    jobs: list[dict[str, object]]
    warnings: list[str]


class TailoringState(TypedDict, total=False):
    candidate: dict[str, object]
    requirement: dict[str, object]
    bullets: list[dict[str, object]]
    verified: bool
    approved: bool


class ApplicationState(TypedDict, total=False):
    job_id: str
    package_ready: bool
    approved: bool
    next_action: str
