import re

from hireme_ai.schemas.candidate import CandidateFact
from hireme_ai.schemas.resume import GeneratedResumeBullet, VerificationStatus

NUMBER_RE = re.compile(r"(?<!\w)(\d+(?:\.\d+)?%?)(?!\w)")


def verify_bullet(
    bullet: GeneratedResumeBullet, facts: list[CandidateFact]
) -> GeneratedResumeBullet:
    fact_map = {f.id: f for f in facts}
    notes: list[str] = []
    if not bullet.source_fact_ids:
        notes.append("No provenance fact IDs supplied")
    missing = [fid for fid in bullet.source_fact_ids if fid not in fact_map]
    if missing:
        notes.append(f"Unknown fact IDs: {', '.join(missing)}")
    linked = [fact_map[fid] for fid in bullet.source_fact_ids if fid in fact_map]
    if any(not f.verified_by_user for f in linked):
        notes.append("Source facts require candidate review")
    # Fail closed: this demo supports exact excerpts and a narrow skill template.
    # Arbitrary semantic rewrites need a separate, evaluated verification system.
    supported = {f.source_text.strip() for f in linked if f.source_text}
    supported.update(f"Verified skill: {f.value}" for f in linked if f.category == "skill")
    if bullet.text.strip() not in supported:
        notes.append("Wording is not a supported exact excerpt or verified skill statement")
    allowed_text = " ".join(
        f"{f.subject} {f.predicate} {f.value} {f.source_text or ''}"
        for f in facts
        if f.id in bullet.source_fact_ids
    ).lower()
    for number in NUMBER_RE.findall(bullet.text):
        if number.lower() not in NUMBER_RE.findall(allowed_text):
            notes.append(f"Unsupported numeric claim: {number}")
    status = VerificationStatus.FAILED if notes else VerificationStatus.PASSED
    return bullet.model_copy(update={"verification_status": status, "verifier_notes": notes})


def verify_resume(
    bullets: list[GeneratedResumeBullet], facts: list[CandidateFact]
) -> list[GeneratedResumeBullet]:
    return [verify_bullet(b, facts) for b in bullets]
