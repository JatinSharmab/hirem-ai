# Historical deployment notes

**Superseded:** follow [the current public portfolio deployment guide](PUBLIC_DEPLOYMENT.md).
The notes below describe the earlier implementation and are retained as history.

Live local Gemini integration is now available; follow LOCAL_LIVE_GUIDE.md first.
The deployment notes below predate that integration. APP_MODE=live now enables live
resume/JD extraction, and ENABLE_LIVE_JOB_DISCOVERY enables explicit ATS fetch requests.
Jobs/JD analysis persist; candidate and application ownership remain deployment blockers.

This repository currently runs a local demonstration, not the complete master-prompt
product. Read VALIDATION_AND_NEXT_STEPS.md first. Do not expose real candidate data
on the public API: authentication, user isolation and persistent application services
are not implemented. The shared in-memory application tracker is unsuitable for
multiple users. Merely provisioning PostgreSQL does not connect those services.

## Ordered preparation

1. Finish the deployment blockers in the audit: persistence, identity/isolation,
   bounded storage/rate limiting, authoritative source verification and durable workflows.
2. Install Git, create a GitHub repository, and commit source, tests and uv.lock.
   Never commit .env, .venv, .tools or .streamlit/secrets.toml.
3. Create a Supabase project. Get its PostgreSQL connection details from Connect.
   Prefer a connection method reachable from your backend (often the session pooler
   when IPv4 is needed). Use separate least-privilege runtime and migration credentials.
   Percent-encode special characters in the password; use postgresql+asyncpg://
   for this application. Configure and test TLS with the chosen driver and provider.
4. Set DATABASE_URL locally for the target database and run:
   `.venv\Scripts\python.exe -m alembic upgrade head`.
   Verify the vector extension and schema exist. Take backups before later migrations.
   Downgrading revision 0001 deletes the application tables and their data.
5. Import render.yaml in Render. The build consumes the committed uv.lock.
   Set DATABASE_URL and the UI origin in backend environment settings.
   The blueprint deliberately does not run automatic destructive schema operations.
6. Deploy the UI on Streamlit Community Cloud: repository, branch, entrypoint
   apps/ui/Home.py, Python 3.12. The adjacent requirements.txt installs UI-only dependencies.
   Add a top-level secret:
   ```toml
   API_BASE_URL = "https://YOUR-BACKEND.onrender.com"
   ```
   The UI reads this environment variable. Keep database and Gemini credentials backend-only.
7. Check /health (process), /ready (database, 503 on failure), then manually exercise
   profile → discovery → match → verified extract → PDF/DOCX → tracking.
   A green /health is not evidence that persistence or live AI is working.
8. Configure GEMINI_API_KEY only when implementing/testing the live services.
   LLM_MODEL=gemini-3.1-flash-lite is a documented model ID; verify access in your account.
   EMBEDDING_MODEL=gemini-embedding-2 and EMBEDDING_DIM=768 are configurable.
   Setting a key alone does not enable a live workflow in this code.

## Hosting limitations and references

Render free compute may spin down and its filesystem is ephemeral. Browser session
history and API memory are temporary. Free quotas can change; verify each account's
current limits and billing before enabling paid services. No zero-cost guarantee is made.

- [Render free services](https://render.com/docs/free)
- [Render Python version](https://render.com/docs/python-version)
- [Streamlit deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Streamlit secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Supabase connections](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Gemini models](https://ai.google.dev/gemini-api/docs/models)
