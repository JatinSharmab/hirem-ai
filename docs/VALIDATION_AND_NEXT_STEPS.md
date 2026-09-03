# HireMe AI review — 2 October 2026

## Latest live-mode update

See [LOCAL_LIVE_GUIDE.md](LOCAL_LIVE_GUIDE.md) for the current connected path.
Gemini profile/JD extraction, conservative fact selection, real job import and PostgreSQL
job/requirement caching are now connected. The original review below predates those changes.
Candidate/version/application persistence and production authentication are still unfinished.

## Verdict

The original repository was a scaffold with runnable utilities, not the completed
master-prompt product. Local demo startup and important correctness problems have
been repaired. The larger product still requires engineering before deployment.
Missing integration is not something you can fix by supplying API keys alone.

## Implemented repairs

- Installed workspace-local uv, Python 3.12 and .venv dependencies; generated uv.lock.
- Added explicit package build configuration, python-multipart and SQLAlchemy asyncio
  dependencies, fixing clean-install/API-startup failures.
- Connected UI pages to FastAPI: profile upload/review, discovery, matching, conservative
  resume extracts, PDF/DOCX download, session history, temporary tracking, skill counts.
- Added configurable API_BASE_URL, explicit HTTP errors, Windows start/check script,
  UI-only cloud requirements and locked Render build configuration.
- Made verification fail closed for arbitrary wording, unreviewed facts and empty output.
  Skill facts no longer become invented work/project experience. Exports reverify content.
- Matching requires reviewed fact evidence, not unsupported profile skill-list entries.
- Invalid uploads return 422, application statuses are enum-validated and missing records
  return 404. /ready returns 503 when the database is unavailable.
- URL import and verification resolve DNS and do not automatically follow redirects.
  HTTP 200 alone no longer labels a vacancy OPEN.
- Replaced fabricated trace responses and informational re-embedding success with explicit
  unsupported behavior. Replaced the evaluation counter with executed assertions.
- Fixed typing, formatting, model default, migration percent escaping and duplicate
  fact-ID uniqueness declaration. CI now attempts real PostgreSQL migration/drift checks.
- Added regression, UI execution, adapter-fixture and end-to-end export tests.
- Updated README and deployment instructions to match actual behavior.

Formatting touched many existing Python files; this workspace has no .git directory,
so there was no original Git diff/history to inspect or commit.

## Acceptance matrix

| Area | Current evidence / remaining limitation |
|---|---|
| Local startup | API and Streamlit launched; health endpoints respond |
| Profile | PDF/DOCX text parsing, keyword skills, user-review UI; no full structured career extraction |
| Fact ledger | Provenance and review checked; not an immutable database ledger or authenticated review |
| Discovery | Synthetic fixture API/UI; ATS adapters tested against mocked payloads, not live tenants |
| Normalization/dedup | Utility tests pass; no persistent idempotent ingestion |
| Verification | HTTP-level checks are conservative; source-specific active-vacancy checks remain |
| Matching | Deterministic score/evidence/gaps work; semantic and responsibility components are coverage proxies |
| Tailoring | Exact supported excerpts/skill statements only; full CV rewriting and semantic critic remain |
| Exports | PDF/DOCX APIs exercised, text extraction verified; not polished full-length CV layouts |
| Version history | Browser-session history only, not database persistence |
| Application tracking | Local process memory only; no user isolation or controlled transition state machine |
| LangGraph | Definitions and tailoring test work; no durable checkpointing, pause/resume or API orchestration |
| Traces | No persisted execution traces; UI explicitly says unavailable |
| Market analytics | Synthetic keyword counts only |
| AI providers | Adapters exist; live Gemini, embeddings, cache/retries/cost tracking not end-to-end validated |
| PostgreSQL | Models and offline migration SQL validate; no local server/Docker to execute migration |
| CI/deployment | Config repaired; remote CI and hosting not executed |
| Documentation | Original architecture/ADRs largely describe target design; this audit is implementation truth |

## What you need to do next

### 1. Try the local demo now

Open http://localhost:8501 if the review servers are still running. Otherwise use the
two exact commands in README.md. No accounts, API key or payment are needed.
Follow Candidate Profile → Job Discovery → Job Match → Resume Studio → Applications.
Expect a skill extract, not a production-quality tailored resume.

### 2. Set up local PostgreSQL

Install Docker Desktop and start it. Restart the terminal if docker is not found.
Run docker compose up -d postgres, then docker compose ps.
When healthy, run .venv\Scripts\python.exe -m alembic upgrade head and
.venv\Scripts\python.exe -m alembic check.
Visit http://localhost:8000/ready; it should return ready once PostgreSQL is reachable.
Do not treat database readiness as proof that UI records persist.

### 3. Complete the product integrations

Recommended implementation order:

1. Persistent profile/fact/job/resume/application repositories and services, with
   transaction boundaries, candidate-scoped fact IDs and restart-persistence tests.
2. Authentication and ownership, isolated users/sessions, server-controlled fact review.
3. Real profile extraction, preferences and review; prevent untrusted candidate payloads
   from asserting their own provenance.
4. Wire configured ATS sources, requirement extraction, bounded ingestion, idempotency,
   authoritative verification, caching and failure reporting.
5. Connect embeddings and evidence-aware semantic matching; calibrate actual score components.
6. Full factual resume generation/critique with adversarial evaluation and polished exports.
7. Durable LangGraph checkpoints, genuine approval interrupts, retries and persisted traces.
8. Production hardening: bounded response/archive sizes, DNS-rebinding-resistant egress,
   retention/deletion, logging redaction in the actual pipeline, distributed throttling,
   backups and monitoring.

These are coding tasks, not account-configuration tasks.

### 4. Deploy after those checks

Install Git and create a GitHub repository. Later you will need Supabase, Render and
Streamlit accounts; Gemini only for the implemented live AI paths. Follow DEPLOYMENT.md.
Keep secrets out of Git/chat and configure them directly in the hosting dashboards.

## Security/accuracy limits

The conservative verifier checks consistency with user-approved input; it does not prove
real-world truth. Upload extraction can mistake negated skill mentions for skills, so
review is essential. Matching does not yet enforce every desired eligibility constraint.
Arbitrary URL network calls need stronger egress isolation before exposure.
A public real-data launch is blocked by missing authentication and persistent ownership.
The existing security tests cover examples, not a complete penetration audit.
