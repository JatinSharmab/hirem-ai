from dataclasses import dataclass, field
from time import perf_counter
from uuid import uuid4


@dataclass
class RunTrace:
    workflow: str
    run_id: str = field(default_factory=lambda: str(uuid4()))
    events: list[dict[str, object]] = field(default_factory=list)
    started_at: float = field(default_factory=perf_counter)

    def add(self, node: str, status: str, **metadata: object) -> None:
        self.events.append({"node": node, "status": status, **metadata})

    @property
    def duration_ms(self) -> int:
        return int((perf_counter() - self.started_at) * 1000)
