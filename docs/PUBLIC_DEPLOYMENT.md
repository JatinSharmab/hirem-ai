# Public portfolio deployment

## Existing deployment

The GitHub repository is https://github.com/JatinSharmab/hirem-ai.
Render services have already been provisioned in Singapore:

- UI: https://hirem-ai.onrender.com
- API: https://hirem-ai-api.onrender.com
- [UI dashboard](https://dashboard.render.com/web/srv-davpmdm7bikc73f00lug)
- [API dashboard](https://dashboard.render.com/web/srv-davpm5ou01pc73fm8u0g)

The Supabase hireme-ai project has been migrated and uses a dedicated application
login. Credentials are in the local ignored .env.deploy and Render environment;
never commit that file. Certificate verification and database role isolation pass.
The URLs above become usable when Render reports the deployments as live.
Do not create another Blueprint for this installation. The steps below also serve
as a fresh-install reference. For updates, push code, verify GitHub CI, then deploy
the appropriate existing service from its Render dashboard.

Current guide: 2026-10-02. This supersedes the earlier deployment notes and signup
proposal. Visitors use isolated temporary workspaces without accounts. This is
the current portfolio scope, not the complete original master prompt.

## 1. Review locally

Keep your working .env and Gemini key; leave APP_ENV=development locally.

```powershell
docker compose up -d postgres
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
.\scripts\start-local.ps1 check
```

Run `./scripts/start-local.ps1 api` and `./scripts/start-local.ps1 ui` in separate
terminals. Open http://localhost:8501. Stop old servers first with
`./scripts/stop-local.ps1` if their ports are occupied.
The private backup before migration 0002 is .tools/hireme-before0002.dump.
Legacy records are preserved but inaccessible to new anonymous sessions.

Exercise: upload a consented resume, review facts, import a real job, analyze it,
match, generate a verified extract, download PDF/DOCX, and track an application.
These actions consume Gemini quota. Exports are verified extracts, not a full CV
layout reconstruction. The app tracks applications; it does not submit them.

## 2. Verify the responsive layout

CSS now stacks phone columns, wraps tablet columns, scales text, scrolls tabs,
wraps long content and provides 44px buttons. Visual browser/device checks could
not be performed here and remain a release gate.

In Chrome press F12, then Ctrl+Shift+M. Test 360x800, 390x844, 768x1024, 1024x768,
1366x768 and 1920x1080. On every page check navigation, upload, tabs, long titles,
empty/error states, downloads and absence of page-wide horizontal scrolling.
Check keyboard focus, Tab/Enter and 200% zoom. Also test actual iPad/iPhone Safari.
On the deployed site use normal/private browser windows: jobs and applications
created in one must be absent in the other. Clear one workspace; the other stays.

## 3. Put the source in GitHub

Install Git and create a repository, then run in this project:

```powershell
git init
git add .
git status
git diff --cached --stat
```

Inspect before committing. .env, .venv, .tools, logs, database dumps and
.streamlit/secrets.toml must not be staged. Do not upload personal resumes.
Then use your actual repository URL:

```powershell
git commit -m "Prepare public HireMe AI portfolio"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/hirem-ai.git
git push -u origin main
```

## 4. Create a dedicated Supabase database

Use a separate portfolio project. Select Connect > Session pooler (usually port
5432) for IPv4 compatibility and session-level migration locks. Do not use the
transaction pooler. Replace the URL prefix and percent-encode password characters:

```text
postgresql+asyncpg://postgres.PROJECT:ENCODED_PASSWORD@POOLER_HOST:5432/postgres
```

Do not append sslmode query parameters; the app configures both drivers through
DATABASE_SSL and DATABASE_SSL_CA. Download the project's CA from Database settings.
See [Supabase connections](https://supabase.com/docs/guides/database/connecting-to-postgres)
and [SSL enforcement](https://supabase.com/docs/guides/platform/ssl-enforcement).
The role must create tables and enable pgvector. This dedicated portfolio uses
one role for startup migrations/runtime; separate roles remain a larger-service
hardening step. Disable the Data API on this dedicated project: this app uses
direct PostgreSQL and does not need public database endpoints.
See [Supabase Data API security](https://supabase.com/docs/guides/api/securing-your-api).

## 5. Create the Render services

Select New > Blueprint, connect the GitHub repository and use render.yaml. Review
the two services. No hosted resources were created by this review. Free plans are
for portfolio preview: services sleep and share usage allowances. Use paid
always-on instances if reliable recruiter access is required.
See [Render free-service limitations](https://render.com/docs/free).

Fill backend DATABASE_URL and GEMINI_API_KEY. If the backend URL is not assigned
yet, use https://example.invalid temporarily for frontend API_BASE_URL.
The blueprint sets production/live mode, gemini-3.1-flash-lite, verified database
TLS, a generated gateway secret, 10 AI requests per visitor/day, 100 site-wide/day,
and 24-hour workspace retention. The UI receives the gateway secret through a
service reference. Keep it server-side; Gemini/database credentials belong only
on the API. See [Render blueprint reference](https://render.com/docs/blueprint-spec).

## 6. Add the database CA and deploy the API

On the API service go to Environment > Secret Files. Add supabase-ca.crt with the
exact downloaded certificate. DATABASE_SSL_CA already points to
/etc/secrets/supabase-ca.crt. The first start can fail until this file exists;
save it and redeploy. See [Render secret files](https://render.com/docs/configure-environment-variables).
Startup validates settings, locks migrations, upgrades the schema, then starts
the API. Do not disable TLS to bypass certificate/hostname failures.

On the assigned backend HTTPS URL check:

- /health: 200, status ok.
- /ready: 200, status ready (database reachable and migration 0002 applied).
- /api/v1/settings without gateway credentials: 401, intentionally.
- Production docs/OpenAPI are disabled.

Hosted TLS/migrations have not been tested by the local review.

## 7. Deploy and verify the UI

Set frontend API_BASE_URL to the real backend HTTPS URL without /api/v1. Verify
its API_GATEWAY_KEY reference points to the backend. Redeploy the UI and open its
HTTPS URL. Expect no signup, no developer navigation, and a Privacy & session page.
Complete steps 1 and 2 on the deployed site. Local Gemini test/configuration
controls are intentionally hidden on the public UI.

## 8. Operate the portfolio

Sessions use random identifiers, not recoverable accounts. Closing/reloading or
reconnecting may start a fresh workspace. Save downloads before leaving. Profiles
and previews stay in session memory. Jobs/applications expire in PostgreSQL and
are immediately hidden; cleanup runs hourly while the API runs and at startup.
Sleeping services delay physical deletion. Google retention follows its API terms.
Clear my data deletes workspace records without resetting usage counters.

Visitor limits identify sessions, not humans. A new session can bypass the visitor
limit, but the atomic site-wide daily ceiling still applies. Failed AI attempts
also count. Request limits are not a guaranteed monetary cap: configure provider
quota/budget controls and monitor usage before sharing.

Back up before later migrations and test restoration to a separate database.
Code rollback does not roll back schema. Avoid casual downgrades: initial downgrade
deletes tables; revision 0002 may have duplicates incompatible with the old index.
Monitor /ready, errors, Gemini usage and storage. Manual cleanup with the backend
environment is `python scripts/cleanup_expired.py`.

The local pre-migration backup was restored into a separate test database and
successfully upgraded to revision 0002; its schema check passed. Repeat this with
your hosted backup procedure. Remaining release gates: hosted TLS/migrations/Gemini,
visual checks including Safari, hosted backup recovery, and expected-traffic load
testing. Automated local checks cannot certify these.
