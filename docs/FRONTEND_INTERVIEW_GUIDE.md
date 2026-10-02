# HireMe AI: migration and interview guide

Use this with [the architecture](ARCHITECTURE.md), [feature matrix](MIGRATION_MATRIX.md), and [validation record](FRONTEND_VALIDATION.md). It describes implemented behavior, not every idea in the original master prompt. Say “deployed on Vercel” only after Vercel hosted acceptance passes.

## The project from scratch

1. **Problem:** Candidates need to compare their actual experience with a job. Free-form AI resume rewriting can invent unsupported claims.
2. **Evidence model:** Each Candidate Fact has an ID, value, source excerpt and review flag. This makes later claims traceable.
3. **Python API:** FastAPI and Pydantic define contracts; services own business rules; repositories own data access; providers wrap external APIs.
4. **Controlled AI:** Gemini extracts profiles and requirements, then selects reviewed fact IDs. It does not set the score or approve exports.
5. **Real jobs:** Manual descriptions and three direct ATS adapters produce the same JobRecord shape.
6. **Explainable matching:** Python calculates seven weighted factors and returns supporting evidence, gaps and eligibility warnings.
7. **Verified output:** Python constructs supported resume bullets and reverifies them before generating PDF/DOCX.
8. **Persistence:** PostgreSQL stores owner-scoped jobs, requirement caches and application records. Profiles and resume history stay in temporary UI memory.
9. **Public access:** Anonymous workspaces, a private gateway, quotas, parser limits and verified database TLS constrain access and cost.
10. **Frontend migration:** Next.js replaces the presentation layer while preserving Python behavior. Pages render independently of the sleeping Render API.
11. **Validation:** Tests cover contracts, security, interactions, responsive layouts and a synthetic live workflow against Gemini and hosted storage.

## 1. Next.js pages and responsive shell

**WHAT / WHY:** The public website and navigation. A pre-rendered page can appear while the API wakes; React gives control over the workflow and mobile layout.

**HOW / WHERE:** `frontend/app/` uses the App Router. `components/layout/shell.tsx` supplies navigation and status. Tailwind plus shared CSS tokens control spacing, typography, cards and stacking.

**WHY THIS / WHY NOT:** Next.js combines static pages and server routes in one deployment. A React SPA plus a separate gateway is valid but adds an operational boundary. Streamlit was simpler but tied the interface to a Python UI process.

**SECURITY:** Browser components must not import private server modules. React renders text safely; external links accept HTTP(S), not script URLs.

**FAILURE MODE:** Rendering errors, overflow or an unavailable action. Error boundaries and visible loading/empty/error states give recovery paths.

**TESTING:** Build, strict TypeScript, lint and browser checks at 1920, 1440, 1366, 1024, 768 and 390 pixels. Physical Safari is a separate check.

**INTERVIEW ANSWER:** “I moved presentation to Next.js so the website can appear independently of the API, while keeping the tested Python behavior.”

## 2. Server-side BFF

**WHAT / WHY:** A small server bridge keeps the shared FastAPI gateway credential out of browser JavaScript.

**HOW / WHERE:** `/api/...` reaches `app/api/[...path]/route.ts`, the BFF allowlist and `server-client.ts`. Validated requests get the server credential and a verified workspace UUID before being forwarded to existing Python endpoints.

**WHY THIS / WHY NOT:** Route Handlers fit a finite proxy. Direct browser requests would expose the shared key. Reimplementing Python logic in JavaScript would create competing sources of truth.

**SECURITY:** Exact-origin checks, signed cookies, known routes, bounded request sizes, no redirects, private caching and safe errors. Users cannot choose an arbitrary upstream URL.

**FAILURE MODE:** Wrong credentials, backend cold start, provider timeout or malformed responses. Writes are never automatically retried.

**TESTING:** BFF tests inspect forwarded headers and reject cross-site writes, forged cookies, unsupported routes and unconsented uploads. Live tests check the same path against Render.

**INTERVIEW ANSWER:** “The browser sees same-origin endpoints. The Next.js server holds the gateway secret and forwards a validated workspace request to Python.”

## 3. Anonymous workspace and state

**WHAT / WHY:** A temporary identity isolates saved records without signup. Memory-only state avoids persisting resume evidence unnecessarily in the browser.

**HOW / WHERE:** `lib/workspace/session.ts` signs a UUIDv4 and 24-hour timestamps using HMAC-SHA256. The cookie is HTTP-only, SameSite=Lax, and Secure with a `__Host-` prefix on Vercel. `workspace-provider.tsx` holds profiles, review flags, matches, bookmarks and version snapshots.

**WHY THIS / WHY NOT:** A signed cookie rejects a forged identity. Full accounts offer stronger identity and recovery but are outside this no-signup portfolio scope. localStorage would retain resume data longer than needed.

**SECURITY:** A signature is not encryption or proof of a person. Python owner filters remain essential. New cookies can bypass visitor limits, so global budgets are the final ceiling.

**FAILURE MODE:** Lost/expired cookies cannot be recovered. Reloading clears profile/review/version state. Clear-data keeps usage identity and prevents late responses from restoring cleared client state.

**TESTING:** Forgery/expiry tests, two clean browser sessions, cross-owner 404 responses and deletion isolation.

**INTERVIEW ANSWER:** “I use signed temporary workspaces and owner-filtered database records. It is anonymous isolation, not authentication.”

## 4. Wake-up and loading behavior

**WHAT / WHY:** A checking/waking/ready/unavailable state lets people read and prepare inputs during free-hosting startup.

**HOW / WHERE:** The workspace provider initializes the session, checks BFF health and safely reads settings. The BFF calls cheap FastAPI `/health`. Backoff grows from two to eight seconds; checks stop after eight attempts or two minutes. Retry is explicit.

**WHY THIS / WHY NOT:** Visit-triggered checks are bounded. A continuous pinger consumes allowances and does not fix the interface dependency. Paid always-on compute is an optional future choice.

**SECURITY:** Health checks call no AI. Backend-dependent writes stay disabled during startup.

**FAILURE MODE:** The API may remain down, or the database may fail after process health succeeds. Data actions show separate errors; `/ready` checks dependencies during release validation.

**TESTING:** Fake-clock browser tests verify that navigation remains available and retries stop. BFF tests cover timeout and HTML gateway errors.

**INTERVIEW ANSWER:** “I separated page availability from backend readiness. The user can explore while a bounded health check wakes the free API.”

## 5. Resume upload and Fact Ledger

**WHAT / WHY:** Explicit consent, structured extraction, source inspection and individual review prevent model output from immediately becoming approved evidence.

**HOW / WHERE:** `/profile` sends multipart data through the BFF. Python checks document contents and extracts text. Gemini returns candidate facts. `fact-ledger.tsx` displays IDs, values, categories, source excerpts and review toggles.

**WHY THIS / WHY NOT:** Fact IDs support validation and reuse. Free-form chat output is harder to compare, verify and trace.

**SECURITY:** Consent at both boundaries; Python file validation and decompression limits. The frontend cap is 4 MiB for Vercel; the existing Python cap is 5 MiB.

**FAILURE MODE:** Scans may have no readable text; extraction can miss or misread facts. Human review is still required and does not prove identity.

**TESTING:** Consent, size, malformed-file, review/unreview and live synthetic PDF checks.

**INTERVIEW ANSWER:** “I convert the resume into source-linked facts first. The user reviews those facts before matching or tailoring can use them.”

## 6. Job ingestion and analysis

**WHAT / WHY:** Manual descriptions and Greenhouse, Lever and Ashby boards feed one normalized job contract.

**HOW / WHERE:** `/jobs` imports/discovers; `/jobs/[id]` shows the original description and requirements. Python adapters cap discovery at 20. An explicit Analyze action invokes Gemini only if the backend cache is missing.

**WHY THIS / WHY NOT:** Direct ATS APIs are bounded integrations. Internet-wide scraping creates a different access and reliability problem. Frontend normalization would duplicate Python responsibilities.

**SECURITY:** Validated board identifiers, fixed provider hosts, safe official links, and UNKNOWN status preserved as UNKNOWN.

**FAILURE MODE:** Wrong identifiers, changing provider formats or closed postings. The user must confirm current availability on the official source.

**TESTING:** Adapter tests, encoded BFF queries, cached-vs-explicit analysis and real requests to all three ATS providers.

**INTERVIEW ANSWER:** “I normalized three direct ATS sources and manual descriptions behind one API. Import and AI analysis are separate, and I do not pretend imported roles are independently verified as open.”

## 7. Career Fit Score

**WHAT / WHY:** A deterministic seven-factor score with evidence and gaps, so the number can be explained.

**HOW / WHERE:** `/match` calls Python. `matching/scoring.py` applies weights; the React score component only displays returned values.

**WHY THIS / WHY NOT:** A heuristic is transparent and testable. An LLM-assigned score is harder to reproduce. A learned ranking model would need labeled evaluation data this project does not yet have.

**SECURITY / CORRECTNESS:** Reviewed skill facts support skill matches, but a user can still supply false input. The score is not an employer ATS score or hiring probability.

**FAILURE MODE:** Normalized exact skills can miss synonyms. The role factor reuses required-skill coverage; responsibility reuses evidence; location/work-mode currently compares location only.

**TESTING:** Deterministic backend tests and a small synthetic golden set. Frontend tests confirm exact score display and honest proxy explanations. No accuracy percentage is inferred.

**INTERVIEW ANSWER:** “Seven fixed factors make the score explainable. Fifty-five percent of total weight comes from required skills and evidence; that is weighting, not accuracy.”

## 8. Resume Studio and exports

**WHAT / WHY:** Job-specific evidence selection and verified resume extracts reduce unsupported AI claims.

**HOW / WHERE:** `/resume` sends reviewed facts and requirements with consent. Gemini chooses up to 15 fact IDs. Python constructs supported wording and verifies it. Each version keeps its original candidate snapshot. Export sends that snapshot back for reverification.

**WHY THIS / WHY NOT:** Restricting the model to IDs narrows its authority. An unconstrained “improve my resume” prompt could invent experience. Browser-only verification can be bypassed.

**SECURITY:** Empty/failed versions cannot export. Downloads are generated in Python; the BFF converts base64 into private binary responses. Source truth still depends on the resume and human review.

**FAILURE MODE:** Empty selection, unsupported IDs, verification failure or a provider error. The UI preserves the status and never marks a failed result ready.

**TESTING:** Backend verifier tests, approval controls, source-ID display and real PDF/DOCX file-signature checks.

**INTERVIEW ANSWER:** “Gemini selects evidence. Python controls supported wording and verifies it again during export. Every bullet retains its source fact IDs.”

## 9. Applications and insights

**WHAT / WHY:** A focused ten-stage tracker and saved-job keyword counts complete the workflow without claiming automatic submissions or global market intelligence.

**HOW / WHERE:** Job actions create records; `/applications` updates backend enum stages. Completion of an in-flight creation invalidates the list even after navigation. `/insights` displays Python keyword counts and source counts derived from returned jobs.

**WHY THIS / WHY NOT:** This uses actual API capabilities. Editable notes, a full Kanban product or employer submission automation would require separate backend scope.

**SECURITY:** Owner-scoped records and user-controlled official links. No automatic employer action.

**FAILURE MODE:** Expired records, small-sample bias and save/navigation races. Clear labels, refresh behavior and empty states make those limits visible.

**TESTING:** A delayed-save regression, real status persistence, second-session isolation and workspace clearing.

**INTERVIEW ANSWER:** “Users track progress and apply themselves. Insights describe only their saved sample. Live testing caught a save-and-navigate race, which I fixed with completion-triggered refresh.”

## 10. Contracts, testing and deployment

**WHAT / WHY:** Generated types, runtime validation, dependency locks and separate test layers reduce integration mistakes.

**HOW / WHERE:** The actual FastAPI OpenAPI snapshot generates TypeScript types. Zod validates BFF inputs. CI runs Python and frontend checks. The opt-in live acceptance script uses synthetic data against real Gemini and hosted storage.

**WHY THIS / WHY NOT:** TypeScript helps during development but does not validate network input. Mocks keep CI deterministic and avoid AI cost; a separate live run verifies real integrations.

**SECURITY:** Secrets stay in ignored files/server environments. Browser bundles are scanned for private values. The live script does not record credential-bearing traces.

**FAILURE MODE:** Hosted root directory, variables, origins, cookies and limits may differ from localhost. Preview and production acceptance are distinct release gates.

**TESTING:** Use the dated validation report instead of repeating old counts. Synthetic success is not proof of broad accuracy or large-scale reliability.

**INTERVIEW ANSWER:** “I tested the security boundary and actual workflow, not just the screens. Deterministic CI and an explicit live release check serve different purposes.”

## Resume-ready bullets

Use these deployment-neutral statements until Vercel is verified:

- Built a decoupled career workflow with Next.js, TypeScript and a server-side BFF while preserving FastAPI, Gemini, Supabase PostgreSQL and three direct ATS integrations.
- Implemented an explainable seven-factor Career Fit Score with 55% of total weight assigned to mandatory-skill coverage and reviewed candidate evidence.
- Built Candidate Fact Ledger review, fact-ID-based resume selection, deterministic claim verification and backend-reverified PDF/DOCX exports.
- Added signed anonymous workspace cookies, owner-scoped access, bounded AI usage, safe error handling and responsive workflow tests.

After hosted verification, the first bullet can say “Built and deployed … Next.js on Vercel and FastAPI on Render …”. Do not claim vector retrieval, production LangGraph, automatic applications, matching accuracy or unmeasured time savings.

## One-minute explanation

“HireMe AI helps a candidate understand how their real experience fits a job and create a supported resume extract. I start by extracting a resume into a Candidate Fact Ledger. Each fact has an ID and source text, and the user reviews it before use. Jobs come from a pasted description or Greenhouse, Lever and Ashby boards. Gemini extracts requirements, while Python calculates a transparent seven-factor Career Fit Score and shows evidence and skill gaps. For tailoring, Gemini selects reviewed fact IDs; Python controls the wording and verifies it again before PDF or DOCX export. I migrated presentation from Streamlit to Next.js while keeping FastAPI, PostgreSQL and Gemini. A server bridge protects credentials, and the page can load while the free backend wakes up.”

## Two-minute explanation

“The problem was the gap between a resume, a job description and an explanation a candidate can trust. A normal AI resume prompt can invent claims, so I made evidence the core data structure.

Python validates a PDF or DOCX and extracts its text. Gemini produces structured candidate facts, each with a source and ID. The user reviews those facts. Jobs are imported manually or through three direct ATS integrations. Job analysis is explicit and its requirements are cached in PostgreSQL.

Matching is deterministic. Python returns a seven-factor Career Fit Score, requirement-to-fact links and missing skills. I explain the limitations honestly: two factors reuse simpler factors as proxies, and no live vector similarity is used. Fifty-five percent refers to weighting on skills and evidence, not accuracy.

For tailoring, Gemini chooses reviewed fact IDs rather than writing arbitrary claims. Python constructs supported bullets, records provenance and verifies them. Export checks them again. The tracker records user-controlled application progress; it does not apply to employers.

The first frontend was Streamlit on Render. I added Next.js so the interface can render independently of the API cold start. A server-side bridge holds the gateway key, validates operations and forwards a signed workspace identity. Python still owns quotas, security and persistence. I tested security boundaries, responsive interactions, failure states and a synthetic live workflow. The trade-offs include temporary anonymous sessions, provider quotas and free-hosting startup delays.”

## Common interview questions

| Question | Short answer |
|---|---|
| Why not rewrite Python in Next.js? | The business logic already worked and was tested. The migration improves presentation without creating another source of truth. |
| Why BFF rather than CORS? | CORS is a browser policy, not secret storage or authentication. The BFF holds the shared key server-side. |
| Is the cookie an account? | No. It identifies a signed temporary workspace, with no identity proof or recovery. |
| Does review prove truth? | No. It records user approval; the source can still be wrong. |
| Where is RAG used? | It is not part of this live path. Graph/vector-related repository ideas are scaffolding or future work. |
| Does Gemini calculate the score? | No. Python applies fixed weights and returns the evidence map. |
| Is this an ATS score? | No. It is our heuristic, not an employer score or hiring probability. |
| How do you limit hallucination? | Restrict selection to reviewed IDs, construct supported wording in Python, and verify again at export. |
| What survives refresh? | Database jobs/applications until expiry; not the in-memory profile, review or resume history. |
| How do you prevent duplicate requests? | Immediate submission locks and disabled controls; no automatic mutation retries. Durable idempotency is future work. |
| What real bug did testing find? | Navigating during application creation could show an empty list. Completion now triggers a refresh and a delayed-save test covers it. |
| What happens on timeout? | A safe error is shown. The backend may still finish, so users should refresh records before resubmitting. |
| Why only 4 MB uploads? | Vercel has a 4.5 MB function payload cap; multipart overhead needs room. Python keeps its 5 MiB cap. |
| What would you scale first? | Measure bottlenecks, then add server pagination, durable tasks, account-based ownership and distributed limits. Evaluate semantic matching before claiming accuracy. |
| How do you describe release status? | State the actual verified URL. Local integration success is not a completed Vercel deployment. |

## What to demonstrate

Show a synthetic profile, inspect one source fact, analyze a job, explain a score factor and gap, inspect bullet provenance, export a file and show the acceptance report. Use non-confidential data. If the provider is unavailable, show the honest error state rather than presenting a mock result as live.
