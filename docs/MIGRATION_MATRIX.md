# Streamlit → Next.js feature and API matrix

Migration reviewed October 3, 2026. The Next.js source and local integration replace presentation only. Vercel publication and final cutover are separate release gates; keep the existing Streamlit deployment until those gates pass.

| Existing capability | Next.js surface | FastAPI source of truth | Status / deliberate difference |
|---|---|---|---|
| Home and workflow explanation | `/` | No backend required to render | Static page; visit-triggered wake checks |
| PDF/DOCX extraction + consent | `/profile` | `POST /api/v1/profile/parse?consent=true` | Live Gemini; **4 MiB frontend** versus 5 MiB backend cap |
| Name, summary, experience, locations, skills | `/profile` | `CandidateProfile` | Name/experience/locations editable; source facts stay immutable |
| Fact ledger review/unreview/source | `/profile` | `CandidateFact` and Python matching/verifier | Memory only; never automatically marked reviewed |
| Manual JD import | `/jobs` | `POST /api/v1/jobs/import` | Validated 50–30,000 description characters |
| Greenhouse / Lever / Ashby | `/jobs` | `POST /api/v1/jobs/discover` | One board at a time, up to 20 results; preserve UNKNOWN |
| Job list and details | `/jobs`, `/jobs/[id]` | `GET /api/v1/jobs`, `GET /api/v1/jobs/{id}` | Search/location filter and tab-memory bookmarks added |
| Cached requirements | Job details / job picker | `GET /api/v1/jobs/{id}/requirements` | Read only; 409 means analyze first |
| Explicit job analysis | Job details / job picker | `POST /api/v1/jobs/{id}/analyze` | Backend cache reused; no automatic Gemini calls |
| Career Fit Score, gaps, evidence | `/match` | `POST /api/v1/matches` | Backend score only; seven factors with honest proxy descriptions |
| Resume evidence selection | `/resume` | `POST /api/v1/resumes/tailor` | Consent, reviewed facts, selected IDs and verifier notes |
| Version history | `/resume` | `ResumeVersion` response | Tab memory; each version keeps the original candidate snapshot |
| PDF/DOCX downloads | `/resume` | `POST /api/v1/resumes/export/{format}` | Approval in UI; backend reverifies; BFF converts base64 to binary |
| Application creation | Job card/details | `POST /api/v1/applications?job_id=...` | Deduplicated by backend; no automatic submission |
| Application list/status | `/applications` | `GET /api/v1/applications`, `PATCH /api/v1/applications/{id}?status=...` | All ten enum stages; refreshes after a pending creation finishes |
| Notes/resume reference | `/applications` | Existing response fields | Display when available; no invented editing endpoint or timestamps |
| Skill frequency insights | `/insights` | `GET /api/v1/insights/skills` | Workspace keyword counts; source distribution derived from returned jobs |
| Privacy, expiry, delete | `/privacy` | `GET /api/v1/settings`, `DELETE /api/v1/workspace` | Signed cookie session; deletion preserves usage identity |
| Health / startup recovery | Global shell | Public `GET /health` | Eight attempts or two minutes; no AI, no recurring keep-alive |
| Database/migration readiness | Deployment validation | Public `GET /ready` | Release check, separate from cheap visitor health ping |
| Architecture explanation | `/architecture` | Repository implementation | Current behavior separated from future/scaffold code |
| Local model/key diagnostic | Existing Streamlit local settings / scripts | `POST /api/v1/settings/check-gemini` | Operator-only workflow retained; not added to the public BFF |
| Demo profiles / Developer Trace | Existing development tools | Demo/scaffold routes | Retained in repository; not represented as live public AI functionality |

## Contract and security adaptation

`frontend/contracts/openapi.json` is exported from the actual FastAPI app; `frontend/types/backend.ts` is generated from that snapshot with `npm run contracts`. The BFF has a finite method/path allowlist. Query-based Python operations receive validated JSON from the browser, converted to query parameters on the server.

Browser requests never carry the gateway credential. They use an HTTP-only signed cookie; the BFF supplies the UUID workspace header and server-side credential. Existing Python ownership filters, quotas, database schemas, Gemini provider, and deterministic logic are unchanged.

## Parity limitations that block automatic retirement

- Vercel Functions have a 4.5 MB request/response payload cap. This interface uses a 4 MiB file limit with room for multipart overhead; Python still permits 5 MiB. A larger upload design would need separate staging or a scoped upload mechanism. See [Vercel limits](https://vercel.com/docs/functions/limitations).
- Export delivery is capped at 4 MiB by the BFF. Ordinary fact-based extracts are much smaller; oversized exports receive an explicit error.
- Very large job-list responses can hit Vercel's response cap. The backend currently returns up to 200 jobs with descriptions. Server-side pagination is a future improvement, not silently added frontend business logic.
- Profile/review/resume state is not migrated from a previous Streamlit session. New cookies create separate anonymous workspaces. Download needed work from the old interface before switching.
- Public AI workflows are migrated. Developer scaffolding and local operator diagnostics remain in the Python tooling and legacy UI.
- Desktop/tablet/mobile viewport testing does not replace physical iPad/iPhone Safari testing. Record that check before retiring the fallback.
