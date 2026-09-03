# Run HireMe AI yourself with a real Gemini key

## What is now connected

Live mode uses actual Gemini API calls for:
- Structured extraction from your uploaded PDF/DOCX resume.
- Structured requirements from a real job description.
- Selecting relevant reviewed facts for a job-specific resume extract.

Real jobs can be pasted manually or imported from public Greenhouse, Lever and Ashby boards.
Jobs and model-specific requirement analysis are stored in PostgreSQL. Repeating the
same import updates the same job; repeated analysis reuses the stored result.

Matching and verification remain deterministic. Gemini cannot assign the score or
write arbitrary unsupported resume claims. Resume output uses exact source excerpts
and verified skill statements, not a complete freely rewritten CV.

## 1. Get the key (one time)

1. Open [Google AI Studio keys](https://aistudio.google.com/apikey).
2. Sign in and create/select the Google project for your API key.
3. Create an API key and copy it locally.
4. Check your project's model access, quota and billing in AI Studio.
   An API account is separate from merely using the Gemini consumer app.
   No fixed free quota is promised; calls can consume quota or incur cost on paid accounts.
5. Never paste the key in chat, a browser form in HireMe AI, a Git commit or a screenshot.

Official references: [API keys](https://ai.google.dev/gemini-api/docs/api-key),
[model documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite),
[rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

## 2. Configure this project (one time)

Open PowerShell:
```powershell
cd C:\Users\USER\OneDrive\Desktop\hireme-ai
notepad .env
```

The file already exists. Do not overwrite it with .env.example.
Set these values, replacing the placeholder with YOUR key:
```dotenv
APP_MODE=live
GEMINI_API_KEY=your_actual_key
LLM_MODEL=gemini-3.1-flash-lite
ENABLE_LIVE_JOB_DISCOVERY=true
```

Keep your existing DATABASE_URL. Save and close Notepad.
APP_MODE=live and live discovery were already set during this change.
No key was inserted or displayed by the assistant.

Use a different LLM_MODEL if your project does not have access to gemini-3.1-flash-lite.
Model availability changes; use a documented text model with structured-output support.
The backend reads .env on startup, so restart it after edits.

## 3. Start PostgreSQL (each time Docker has stopped)

Open Docker Desktop and wait until its engine is ready, then:
```powershell
cd C:\Users\USER\OneDrive\Desktop\hireme-ai
docker compose up -d postgres
docker compose ps
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
```

Expected: PostgreSQL healthy; Alembic at head; no new upgrade operations detected.
Your existing database schema already supports this change; no new migration was required.

## 4. Start API (terminal 1)

If old background servers are occupying the ports, stop only this project's servers:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/stop-local.ps1
```

Then:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/start-local.ps1 api
```

Keep this terminal open. Expected: Uvicorn running on http://127.0.0.1:8000.

Direct equivalent:
```powershell
.\.venv\Scripts\python.exe -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
```

## 5. Start frontend (terminal 2)

```powershell
cd C:\Users\USER\OneDrive\Desktop\hireme-ai
powershell -ExecutionPolicy Bypass -File scripts/start-local.ps1 ui
```

Open http://localhost:8501. Refresh the page. Keep this terminal open too.

## 6. Verify configuration (terminal 3 / browser)

```powershell
cd C:\Users\USER\OneDrive\Desktop\hireme-ai
powershell -ExecutionPolicy Bypass -File scripts/check-local.ps1
```

Expected: process healthy, database ready, mode live, key configured.
The settings response shows only whether the key exists, never the key itself.
This command does not contact Gemini.

In the UI open **Settings → Test Gemini connection**.
This sends a small real generation request with no resume data.
Expected: “Gemini responded successfully.”
This is the first check that proves YOUR key, quota and model access work together.

## 7. Use your own resume

1. Candidate Profile → upload a text-based PDF or DOCX (maximum 5 MB by default).
2. Tick the consent box allowing resume text to be sent to Google Gemini.
3. Click Extract profile and wait for the model.
4. Review name, experience years, locations, and every source quote.
5. Tick Confirmed only for facts that are true and correctly interpreted.
6. Click Save reviewed facts.

Facts with invented/non-exact source quotes are rejected automatically.
Human review remains necessary: an exact quote alone cannot prove the model's interpretation.
Scanned/image-only PDFs require OCR outside the app first.
Raw resume files are not stored by this workflow; extracted candidate data remains in your
Streamlit browser session and is sent to Gemini when you explicitly consent.

## 8. Bring a real job

**Recommended first check: paste a JD**
1. Job Discovery → Import a real job → Paste job description.
2. Enter the actual title, company, optional location, and full description.
3. Click Save job.
4. On its card, click Analyze with Gemini.
5. Wait for analysis to be saved, then click Explore fit.

Pasting works even when a company's ATS is unsupported.

**Optional: public ATS discovery**
1. Open the employer's official careers page.
2. Identify its public board URL and company slug:
   - Greenhouse: boards.greenhouse.io/COMPANY or job-boards.greenhouse.io/COMPANY
   - Lever: jobs.lever.co/COMPANY
   - Ashby: jobs.ashbyhq.com/COMPANY
3. Select that provider in Public ATS board, enter COMPANY (not the entire URL),
   optionally enter a role keyword, and click Fetch real jobs.
4. Up to 20 matching jobs are imported per request.
5. Analyze the jobs you want with Gemini.

No LinkedIn/Indeed/Naukri scraping or automated applications are performed.
Imported jobs stay UNKNOWN until independently verified; a retrieved page is not proof
the job is accepting applications. Check the official careers site yourself.

## 9. Match, review, export

1. Job Match → choose an analyzed job → Calculate Career Fit Score.
2. Inspect evidence, missing skills and eligibility warnings.
3. Resume Studio → allow Gemini to receive your reviewed facts and JD requirements.
4. Click Create verified skill extract. Gemini selects relevant IDs only.
5. Review the exact-excerpt preview and provenance.
6. Approve downloading and export PDF/DOCX.
7. Track a status manually in Applications if useful.

Requirement analysis is cached by job text, title and model. UI reruns do not generate new
Gemini calls. Profile extraction, the connection test and each new resume version do
make calls. Exporting a previously generated extract does not make a Gemini call.

## 10. Check the code independently

Offline tests (no paid API calls):
```powershell
powershell -ExecutionPolicy Bypass -File scripts/start-local.ps1 check
```

Real database repository check, with all test writes rolled back:
```powershell
.\.venv\Scripts\python.exe scripts/check_live_storage.py
```

Restart the API, then revisit Job Discovery: imported jobs and analyzed requirements should remain.
Candidate/session history and applications are NOT yet durable. Save your exported files.

If a future fresh machine lacks dependencies:
```powershell
uv sync --locked --extra dev
```
On this machine the local uv copy is .tools\uv\uv.exe.
The existing .venv is ready; no reinstall is needed for these changes.

## 11. Stop and restart

Ctrl+C in each server terminal stops the corresponding server.
Alternatively use scripts/stop-local.ps1 for this workspace's servers on ports 8000/8501.
To stop PostgreSQL without deleting its volume:
```powershell
docker compose stop postgres
```
Do not use docker compose down -v unless you intend to delete the database volume.

## Troubleshooting

| Symptom | Action |
|---|---|
| Key missing | Edit .env; set GEMINI_API_KEY; restart API |
| Mode still Demo | Set APP_MODE=live; stop old API; restart; refresh frontend |
| Gemini 400/401/403 | Check key/project permissions, model access and input |
| Model unavailable/404 | Set an accessible documented LLM_MODEL; restart |
| Quota/rate limit/429 | Check AI Studio quota/billing; wait; do not repeatedly click |
| Timeout/504 | Retry later or use a shorter document |
| Database 503 | Start Docker; check DATABASE_URL and Alembic |
| No jobs | Import a JD or fetch a real public board; live mode has no fixtures |
| Analyze job first/409 | Click Analyze with Gemini on its Discovery card |
| Export blocked | Confirm supported facts; ensure relevant content exists |
| API unreachable | Start API terminal; check port 8000 and API_BASE_URL |
| Port already in use | Stop old project servers with stop-local.ps1 |
| Data disappears | Only jobs/JD analysis are durable; other state is currently temporary |

## What remains before calling the whole project complete

This change completes a usable local, single-user live Gemini path. It does not complete
the original production master prompt.

Next engineering milestones:
1. Persist reviewed profiles, facts, resume versions and applications with proper ownership.
2. Authentication and isolation before any public real-data deployment.
3. Full factual resume composition and layout, beyond verified extracts.
4. Actual embedding-based semantic scoring and calibrated eligibility rules.
5. Durable LangGraph execution, approval checkpoints, retries and execution traces.
6. Source-specific active-job verification, broader adapter tests and ingestion scheduling.
7. Privacy retention/deletion, operational monitoring and production security hardening.

Keep this local while testing real personal data. See the deployment guide only after
the applicable production blockers are completed.
