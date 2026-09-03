from collections import Counter

import pandas as pd

from hireme_ai.schemas.job import JobRequirement


def skill_demand(requirements: list[JobRequirement]) -> pd.DataFrame:
    counter: Counter[str] = Counter()
    for req in requirements:
        counter.update(req.mandatory_skills)
        counter.update(req.preferred_skills)
    total = max(1, len(requirements))
    rows = [
        {"skill": skill, "jobs": count, "frequency_pct": round(100 * count / total, 1)}
        for skill, count in counter.most_common()
    ]
    return pd.DataFrame(rows)
