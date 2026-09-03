from pydantic import BaseModel


class RunEvent(BaseModel):
    node: str
    status: str
    metadata: dict[str, object] = {}


class RunView(BaseModel):
    run_id: str
    workflow: str
    duration_ms: int
    events: list[RunEvent]
