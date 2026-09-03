from hireme_ai.schemas.candidate import CandidateFact


def index_facts(facts: list[CandidateFact]) -> dict[str, CandidateFact]:
    return {fact.id: fact for fact in facts}


def allowed_fact_text(facts: list[CandidateFact]) -> str:
    return "\n".join(f"{f.id}: {f.subject} {f.predicate} {f.value}" for f in facts)
