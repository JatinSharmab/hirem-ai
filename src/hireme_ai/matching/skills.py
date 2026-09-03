from pathlib import Path

import yaml


def load_aliases(path: str = "config/skills.yaml") -> dict[str, str]:
    data = yaml.safe_load(Path(path).read_text()) or {}
    aliases: dict[str, str] = {}
    for canonical, variants in data.get("skills", {}).items():
        aliases[canonical.lower()] = canonical
        for variant in variants:
            aliases[str(variant).lower()] = canonical
    return aliases


def normalize_skill(skill: str, aliases: dict[str, str] | None = None) -> str:
    aliases = aliases or load_aliases()
    return aliases.get(skill.strip().lower(), skill.strip())
