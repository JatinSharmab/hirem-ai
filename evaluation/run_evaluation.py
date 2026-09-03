"""Offline golden evaluation. Any failed invariant exits nonzero."""

import json
from pathlib import Path

from hireme_ai.matching.service import match_candidate
from hireme_ai.resume.service import build_verified_resume
from hireme_ai.schemas.candidate import CandidateFact, CandidateProfile
from hireme_ai.schemas.job import JobRecord, JobRequirement, JobStatus


def main() -> None:
    root = Path(__file__).resolve().parent
    candidates = {x["id"]: x for x in json.loads((root / "golden_candidates.json").read_text())}
    jobs = {x["id"]: x for x in json.loads((root / "golden_jobs.json").read_text())}
    cases = json.loads((root / "matching_cases.json").read_text())
    bullets_checked = 0
    for case in cases:
        raw = candidates[case["candidate"]]
        candidate = CandidateProfile(
            name=raw["id"],
            skills=raw["skills"],
            facts=[
                CandidateFact(
                    id=f"F-{i}",
                    category="skill",
                    subject=raw["id"],
                    predicate="lists",
                    value=skill,
                    source_text=skill,
                    verified_by_user=True,
                )
                for i, skill in enumerate(raw["skills"])
            ],
        )
        raw_job = jobs[case["job"]]
        req = JobRequirement(
            role_title="Synthetic role",
            mandatory_skills=raw_job["mandatory"],
            preferred_skills=raw_job["preferred"],
        )
        job = JobRecord(
            id=raw_job["id"],
            title=req.role_title,
            company="Synthetic",
            description="Golden fixture",
            source="demo",
            status=JobStatus.OPEN,
        )
        match = match_candidate(candidate, job, req)
        if "expected_gap" in case:
            assert case["expected_gap"] in {g["skill"] for g in match.gaps}, case
        if case.get("expected_low_match"):
            assert match.score.total < 40, match
        version = build_verified_resume(candidate, req)
        for bullet in version.bullets:
            assert bullet.text in {f"Verified skill: {s}" for s in candidate.skills}
            assert bullet.verification_status == "PASSED"
            if "must_not_fabricate" in case:
                assert case["must_not_fabricate"] not in bullet.text
            bullets_checked += 1
    print(
        json.dumps(
            {
                "cases_passed": len(cases),
                "bullets_checked": bullets_checked,
                "unsupported_claim_rate": 0.0,
                "scope": "Deterministic synthetic cases only",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
