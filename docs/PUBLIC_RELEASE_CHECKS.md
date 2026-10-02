# Public portfolio review - 2026-10-02

## Implemented

- No login/signup. Random server-side visitor workspaces isolate stored jobs,
  requirement caches and application records.
- Production API gateway credential, HTTPS frontend API configuration, verified
  PostgreSQL TLS and fail-closed startup checks. Credentials remain server-side.
- Database-backed daily AI/ATS/import budgets, request/body/upload limits, PDF
  page/text limits and DOCX archive expansion limits.
- Expiring records, hourly production cleanup and clear-workspace action.
- Public navigation hides developer screens. Privacy controls replace public
  backend configuration. Responsive styles cover phone/tablet/laptop breakpoints.
- Render API/UI blueprint, Linux container recipe, locked backend dependencies,
  startup migrations and updated deployment instructions.

## Verified locally

- 60 automated tests pass, including Streamlit AppTest interactions, API flows,
  gateway rejection, session validation, deletion isolation and upload rejection.
- Ruff and formatting checks pass; mypy checks 97 source files.
- Three deterministic synthetic evaluation cases pass. This is not a general
  accuracy benchmark for Gemini.
- Migration 0002 applied after backing up PostgreSQL; Alembic detects no drift.
- Live PostgreSQL job persistence/cache, two-visitor isolation, expiry, deletion,
  visitor quota and global quota checks pass with rollback of test writes.
- Concurrent quota check admitted exactly 5 of 20 requests with global limit 5.
- Pre-migration backup restored into a separate database, then upgraded to 0002
  with no schema drift. Temporary restore database removed after verification.
- Local API /health and /ready and Streamlit health each return HTTP 200.
- Linux dependency image build passed. Testing the current source in that image
  caught and fixed the startup script's application import path; migration startup,
  /health and /ready then passed in the container.
- A final image containing the updated source and Streamlit configuration passed
  startup and both health checks without source mounts. Local tags:
  hireme-ai:portfolio and hireme-ai:portfolio-checked. Test containers were removed.
- No new paid Gemini calls were made for this release review. Earlier local live
  workflow validation and the user's working Gemini setup remain distinct checks.

Pytest reported an inability to write its optional cache under OneDrive; all
tests completed successfully. Targeted security tests also passed with caching disabled.

## Remaining release gates

- Browser layout/interaction verification at the sizes listed in PUBLIC_DEPLOYMENT.md,
  including actual iPad/iPhone Safari. No browser automation surface was available.
- Hosted database TLS, hosted migration startup, live Gemini on the hosted app,
  two-browser acceptance check and hosting-specific backup restoration.
- Dependency vulnerability audit, broader security review and expected-traffic load
  testing. Local automated checks are not a certification of production security.

The project remains a bounded portfolio experience. Temporary sessions have no
recovery, the full master-prompt product is not implemented, and the export flow
produces verified extracts. The hosting update below records the published release.

## Hosting preparation update - 2026-10-02

- Public GitHub repository published: https://github.com/JatinSharmab/hirem-ai.
  First commit is explicitly labeled as a retrospective import: its author date
  is September 3, 2026, while its actual commit/upload occurred October 2, 2026.
- Existing Supabase hireme-ai project selected by the user; it initially contained
  no public application tables. Created a dedicated hireme_app database login.
- Verified the session pooler's TLS certificate and hostname using Supabase's
  officially published CA. Applied migrations 0001 and 0002; no schema drift.
- Production startup now enables RLS on application tables and revokes privileges
  from Supabase anon/authenticated roles. Verified this for all 17 tables.
- Ran the production API locally against the hosted database: readiness, gateway
  rejection, authenticated settings, empty private workspace and disabled docs passed.
- GitHub and hosting access verified. Deployment credentials remain in ignored
  .env.deploy. Existing Render services were inspected but not modified.
- Render services are live at https://hirem-ai.onrender.com and
  https://hirem-ai-api.onrender.com. Both use free plans in Singapore.
- Hosted synthetic acceptance checks passed: Gemini profile/JD extraction,
  verified resume generation, PDF/DOCX exports, application persistence, isolation
  between visitors and workspace deletion. This used three Gemini calls; synthetic
  test records were removed. No real personal resume was used.
- Public Streamlit pages executed successfully against the hosted API using AppTest;
  local configuration controls are hidden and deletion requires confirmation.
- GitHub CI passed for the initial source and hosting configuration commits.
- Actual visual phone/iPad/Safari checks, traffic load testing, a dependency audit,
  and recovery from a hosted backup remain separate follow-up checks.

## Cold-start recovery fix - 2026-10-02

- Investigated an all-pages HTTP 502 report. Render logs show the API shutting
  down at 12:22 UTC and starting again at 13:17 UTC. Initial external requests
  timed out; after startup, health, readiness and authenticated settings returned
  HTTP 200. Both services remained on their existing free plans.
- The UI previously stopped before applying its styles whenever the initial
  settings request failed. It now styles the page first, displays a connection
  message, and retries transient failures on that read-only settings endpoint
  within a roughly 90-second window. A reload button handles longer outages.
- AI requests, uploads, mutations and requirement-extraction GET requests are
  never automatically retried. Authorization failures and quota rejections are
  not retried. Specific JSON error messages from the API remain visible.
- Fixed an independently observed profile-review crash: a plain checkmark was
  rejected as a toast emoji. It now uses a supported Material icon.
- Local validation: 77 tests pass, including simulated 502/503/504 responses,
  HTML loading pages, timeouts, retry limits, preserved workspace identity,
  reload recovery and saving reviewed facts. Ruff lint and formatting pass.
- These changes improve recovery; they do not make free services always-on.
