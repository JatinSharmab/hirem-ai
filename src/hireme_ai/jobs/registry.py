from pathlib import Path

import yaml


def load_source_registry(path: str = "config/job_sources.yaml") -> dict[str, object]:
    return yaml.safe_load(Path(path).read_text()) or {}
