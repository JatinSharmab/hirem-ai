# HireMe AI: deployed website and next steps

Release verified **October 3, 2026 (Asia/Kolkata)**.

## Open and share this link

**https://hireme-ai-tau.vercel.app**

The website is public and does not require signup. Share this address in your
portfolio and resume. No additional account setup or payment is needed to use
this deployment within the providers' current free allowances.

| Part | Deployment |
|---|---|
| Current frontend | Next.js on Vercel Hobby, project `hireme-ai`, Personal workspace |
| Project dashboard | https://vercel.com/personal-7893/hireme-ai |
| Source | https://github.com/JatinSharmab/hirem-ai |
| Python API | https://hirem-ai-api.onrender.com on Render Free |
| Database | Existing authorized Supabase `hireme-ai` project |
| AI | Existing real Gemini configuration, kept on the API |
| Legacy interface | https://hirem-ai.onrender.com |
| Legacy static homepage | https://hirem-ai-portfolio.onrender.com |

The old links remain available. They have not been redirected, suspended or deleted.

## What was configured

- Linked the GitHub repository to a separate Vercel project. The existing unrelated
  portfolio project was not changed.
- Set root directory `frontend`, Next.js, Node 22.x, `npm ci`, and `npm run build`.
  Functions run in Singapore (`sin1`) with Fluid Compute.
- Installed the backend URL and private gateway credential as server environment
  values. Preview and production use separate workspace signing secrets.
- Set the production site origin and public URL to the exact address above.
- Kept preview deployment authentication enabled. A temporary automation bypass
  was used for testing and revoked after acceptance.
- Set Render `FRONTEND_URL` and `ALLOWED_ORIGINS` to the public Vercel origin and
  redeployed the API. Health and database readiness passed after deployment.
- Kept Gemini and database credentials on Render. The Vercel deployment token
  stays in the ignored local deployment file; it is not a runtime variable.
- Added optional protected-preview support and separate artifact folders to the
  live acceptance script. Cleanup failures now produce a failed exit status.

No paid plan, recurring keep-alive service, database migration or login system
was added for this release.

## What was actually tested

The application source was deployed from commit
`90729b4f91d15edd4d8c8b5a14d5e3671eb185d3`, which passed both GitHub CI jobs.
Later release documentation/test-runner changes do not change application behavior.

Vercel treated the initial deployment from `main` as production. Its protected
deployment URL passed the full workflow first. An explicit protected staging
deployment and the public production domain were then tested separately after
the Render update. This records the actual rollout, rather than implying a
preview promotion occurred before the initial deployment.

| Hosted check | Result |
|---|---|
| Initial production deployment URL | 25 live checks passed |
| Protected preview/staging deployment | 25 live checks passed |
| Public production domain, without an authentication bypass | 25 live checks passed |
| Nine public pages at six viewport sizes | 54 page/layout checks passed |
| Public HTML, security headers, cookies, request boundaries and browser assets | 36 checks passed |
| Preview cookie used against production | Rejected with HTTP 401 |
| Render health and database readiness after environment update | HTTP 200 |
| Exact configured CORS origin on the public health route | Confirmed |

Each complete workflow used a synthetic PDF and three real Gemini calls. It
checked fact review, manual jobs, real Greenhouse/Lever/Ashby discovery, job
analysis, scoring, verified resume selection, PDF/DOCX downloads, application
updates, two-visitor isolation, malformed files and workspace deletion. All test
records were cleaned up. No personal resume was used. No browser runtime
exceptions were observed.

The layouts were checked at 1920x1080, 1440x900, 1366x768, 1024x768, 768x1024 and
390x844. These are Edge viewport checks, not physical iPad/iPhone Safari tests.
The legacy interface stays available while those device checks and acceptance
of the 4 MiB frontend upload limit are outstanding.

Private HTML/JavaScript checks searched for actual deployment credential values;
none were found. Private API responses use `no-store, private`. Anonymous cookies
are Secure, HttpOnly and SameSite=Lax. Missing/cross-site origins and unapproved
proxy paths/queries were rejected.

The ignored local reports are in `frontend/artifacts/vercel-deployment/`,
`vercel-preview/`, `vercel-production/`, `vercel-layout/` and
`frontend/artifacts/public-host-security.json`. See
[FRONTEND_VALIDATION.md](FRONTEND_VALIDATION.md) for earlier automated checks.

## Try it yourself

1. Open the public link in a new browser tab. Explore the overview while the
   backend status changes to **Backend ready**.
2. Open **Profile**, select a text-based PDF or DOCX up to 4 MiB, consent to Gemini
   processing and extract the profile. Review the original source for every fact.
3. Open **Jobs**. Paste a job description or use a supported company board.
   Open a job and explicitly analyze its requirements.
4. Open **Match** and calculate the Career Fit Score. Read the evidence and gaps;
   the score is not an employer ATS score or a hiring probability.
5. Open **Resume Studio**, select the job, consent and create the verified extract.
   Review it before approving and downloading PDF or DOCX.
6. Track the job under **Applications** and save a stage change. **Insights** shows
   recognized skill counts from jobs in your own temporary workspace.
7. Use **Privacy & workspace** to clear your data when finished.

Profiles, fact review and resume versions are held in browser memory and are lost
on reload. Jobs/applications live in the temporary database workspace until
deletion or expiry. This is an anonymous portfolio app, not a permanent account.

## Free hosting and speed

The frontend page shells are served independently of Render. One initial HTTP
sample returned the homepage in about 0.6 seconds; this is not a speed guarantee.
Render can sleep after inactivity, so data/AI actions may still wait around a
minute or longer. The UI shows this state and stops automatic checks after a
bounded period. Use its explicit retry if needed. An instant, always-awake AI
backend is not guaranteed by this free deployment.

If there is a problem:

1. Confirm you are using the public Vercel link, not a protected preview URL.
2. Wait for the backend status; retry after a cold start. Avoid repeatedly
   submitting AI actions because timed-out work may still finish.
3. Check Render's API deployment/events and Vercel's function logs. Do not publish
   logs containing secrets or resume text.
4. Quota errors may come from the app's daily budget or Gemini. Repeated clicks
   do not fix them. Check the relevant provider/dashboard and wait for reset.
5. For a persistent incident, use the legacy interface and follow the existing
   [deployment runbook](PUBLIC_DEPLOYMENT.md).

## Publish later changes

1. Make a Git branch, change the source and run the checks in
   [NEXTJS_MIGRATION.md](NEXTJS_MIGRATION.md).
2. Push the branch and use its protected Vercel preview. Wait for GitHub CI to
   pass and review the UI before merging to `main`.
3. The connected Vercel project deploys `main` to the production domain. Confirm
   its deployment is **Ready**, then check the public domain.
4. Backend updates remain a separate manual Render deployment after backend CI.
   A frontend push does not automatically replace the Python API.
5. Keep production workspace signing secrets stable across normal deployments.
   Changing one invalidates existing sessions. Environment changes require a new
   deployment to take effect.

For frontend rollback, use Vercel's Deployments page to restore a known-good
production deployment. For backend rollback, use Render's deployment history.
Do not roll back database schema or delete data as part of a frontend rollback.
