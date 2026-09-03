# Validation Report

## Gemini model/schema fix ? 2 October 2026

- Actual provider response: gemini-2.5-flash unavailable to new users despite models.list.
- gemini-3.8-flash returned transient 503 overload on two attempts.
- Switched local/default/example configuration to gemini-3.1-flash-lite after successful
  real structured-generation verification with the configured key.
- Fixed extraction schema rejection by sending a portable response_json_schema and
  retaining all original Pydantic bounds for local response validation.
- Real running API connection test passed. Synthetic DOCX profile extraction returned
  HTTP 200 with three grounded facts, all pending human review. No user resume sent.
- 52 offline tests pass; Ruff, formatting and mypy pass. Backend restarted.
- Updated user-facing errors to distinguish 400 format, 404 model and 503 overload errors.


## Live Gemini integration follow-up ? 2 October 2026

- Explicit APP_MODE=live disables synthetic profile/jobs. Missing/bad keys return clear
  errors without silently falling back to demo content.
- Added consented Gemini profile extraction with exact source-quote checks, real JD
  analysis, and Gemini fact selection with deterministic excerpt verification.
- Added manual JD import and bounded public Greenhouse/Lever/Ashby discovery routes.
- PostgreSQL job upsert/reload and model/content-specific requirement cache tested
  against the real local database; test transactions were rolled back.
- Added Settings connection-test UI and independent start/stop/check guides/scripts.
- 51 tests pass without paid API calls. Ruff, formatting and mypy (90 source files) pass.
- Running API: health and readiness successful, mode live, key presence true.
  Key validity and Gemini quota/model access have NOT been verified by a real API call.
- Live ATS network responses were not tested; adapter fixtures remain the validation basis.
- Existing temporary candidate/version/application state and production blockers remain.

See docs/LOCAL_LIVE_GUIDE.md. Earlier audit entries below are historical.


## Frontend refresh follow-up ? 2 October 2026

- Added a shared teal/light visual theme, dashboard, profile review progress, searchable
  job cards, saved roles, evidence tabs and charts, resume preview/version selector,
  cached exports, pipeline board and interactive skill insights.
- Selected roles carry through discovery, matching and resume creation.
- 42 tests pass, including saved-job filters and cross-page selection; Ruff,
  formatting and backend mypy pass.
- Database now verified: Alembic revision 0001 (head), no schema drift, /ready HTTP 200.
- API and Streamlit restarted on localhost ports 8000 and 8501; health checks pass.
- Browser preview unavailable in this session. UI tested with Streamlit AppTest;
  no screenshot-based visual verification claimed.
- Database availability does not change the existing temporary storage behavior.

The earlier review below is historical; its missing-database status is superseded above.


Reviewed and executed on this Windows workspace on 2 October 2026.

## Passed

- Python 3.12.15 workspace installation and editable package installation.
- Locked dependencies in uv.lock.
- Ruff check: passed.
- Ruff format --check: 150 Python files formatted.
- mypy: no issues in 86 source files.
- pytest: **41 passed**, no skipped tests.
- Offline golden evaluation: 3 cases passed; 3 generated bullets checked;
  unsupported-claim rate 0 on this narrow deterministic sample.
- Streamlit AppTest executed profile loading and every feature page, including matching,
  extract generation, two download controls and application creation.
- API integration covered profile → jobs → requirements → match → tailoring →
  PDF/DOCX export → application update and insights.
- PDF text and DOCX paragraphs extracted successfully from API exports.
- Adversarial tests reject added employer/education/skill/metric/work claims,
  unreviewed facts and empty output.
- ATS adapter payload contracts tested with mocked HTTP, not live services.
- Alembic initial PostgreSQL migration SQL generated successfully offline.
- Fixture-check script ran; it does not seed a database.

## Running process checks

- http://127.0.0.1:8000/health: HTTP 200.
- http://127.0.0.1:8501/_stcore/health: HTTP 200.
- Live local HTTP matching and both exports: HTTP 200.
- Tailoring result for synthetic candidate: PASSED.
- /ready: HTTP 503 because no local PostgreSQL is running.

The API and UI were left running on localhost. Their logs are under .tools/.
These processes may end when the hosting session closes; README has restart commands.

## Not validated or incomplete

- No Docker/Git executable available in the review terminal; no .git repository present.
- No real PostgreSQL/pgvector migration or schema-drift check executed locally.
  CI now includes these checks but remote CI has not run.
- No Supabase, Render or Streamlit Cloud deployment performed.
- No live Gemini/embedding calls or live ATS network discovery tested.
- No dependency vulnerability audit or full security penetration test performed.
- No visual browser screenshot review; UI behavior was checked using Streamlit AppTest.
- Persistent services, identity/user isolation, true semantic scoring, full CV tailoring,
  durable agent approval/resume and real developer traces remain unfinished.

See [the detailed audit](docs/VALIDATION_AND_NEXT_STEPS.md) for the feature matrix,
changes and ordered next steps. Passing tests do not mean the master prompt is complete.
