import json
from pathlib import Path


def main() -> None:
    candidate = json.loads(Path("data/demo/candidate.json").read_text())
    jobs = json.loads(Path("data/demo/jobs.json").read_text())
    print(f"Demo fixtures ready: {candidate['name']} / {len(jobs)} jobs")
    print(
        "Database seeding is intentionally explicit; fixtures are consumed directly in Demo Mode."
    )


if __name__ == "__main__":
    main()
