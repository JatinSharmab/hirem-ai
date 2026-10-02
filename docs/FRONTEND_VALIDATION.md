# Frontend migration validation

Reviewed **October 3, 2026 (Asia/Kolkata)**. This records actual checks, not a blanket guarantee that every future request will succeed.

## Passing checks

| Layer | Result |
|---|---|
| Next.js production build | Passed; overview and page shells pre-rendered; private BFF remains a server route |
| Frontend lint | Passed |
| Strict TypeScript / route generation | Passed |
| Vitest unit, component and mocked BFF | **39 passed** |
| Playwright browser suite | **10 passed**, using local production build and installed Edge |
| Backend pytest | **77 passed**; a local OneDrive pytest-cache permission warning did not affect tests |
| Backend ruff check / formatting | Passed; 182 Python files already formatted |
| Backend mypy | Passed; **97 source files** |
| Deterministic golden evaluation | **3 synthetic cases** passed; not a broad accuracy evaluation |
| Existing static homepage Node tests | **5 passed** |
| Browser-bundle credential scan | No private `.env.deploy` credential/database values found in `.next/static` |
| Dependency audit | Zero known vulnerabilities reported by npm during the reviewed installation |
| Live Next.js → Render → Gemini/Supabase acceptance | **25 checks passed**, including cleanup |

Do not combine these into an accuracy percentage. Test counts and the small golden set measure different things.

## Browser interaction and layout

The complete mocked workflow passed at **1366px and 390px**, including upload consent, review, job import/analysis, score display, resume approval, both downloads, application creation/status update, insights and clear-data.

All primary pages were checked at **1920×1080, 1440×900, 1366×768, 1024×768, 768×1024 and 390×844**. No page-wide horizontal overflow was observed. Mobile navigation opens/closes; collapsed navigation is hidden from keyboard focus; Escape closes it. Overview screenshots were visually inspected, as were populated profile/match/resume views. Reduced-motion styles are present.

These are desktop-browser viewport checks, not physical iPad/iPhone Safari certification. Actual-device Safari testing remains a release gate before retiring the fallback.

## Live acceptance: actual external systems

Target frontend: `http://127.0.0.1:3000`, running the production build. Its **server-side BFF** used `https://hirem-ai-api.onrender.com`, the existing production Supabase project and real Gemini. This is local-frontend/live-backend acceptance, not a Vercel-hosted test.

The passing run checked:

1. Homepage renders independently; session initializes and backend becomes ready.
2. BFF returns public presentation settings without model/key configuration.
3. A synthetic PDF is parsed and candidate facts extracted by real Gemini.
4. Every synthetic fact is reviewed through the interface.
5. Manual JD is persisted in hosted PostgreSQL.
6. A second clean browser session cannot list/read the first session’s job.
7. Explicit Gemini analysis returns structured requirements.
8. Python score and requirement-to-evidence map render.
9. Real Gemini evidence selection passes Python verification.
10. Actual PDF and DOCX exports download with correct file signatures.
11. A populated resume view fits a 390px viewport.
12. Application creation and status update persist; the second session cannot see them.
13. Workspace skill insights render.
14. Greenhouse (`stripe`), Lever (`zoox`) and Ashby (`linear`) each import real jobs, at most 20, preserving UNKNOWN status; imported details are readable.
15. Malformed PDF and malformed DOCX receive Python validation errors.
16. An unknown job returns a safe 404.
17. Clearing the first workspace removes its jobs/applications without removing the second workspace’s job.
18. No browser runtime exceptions occurred; both synthetic workspaces were cleaned up.

The script records 25 individual checks because downloads, ATS sources, invalid files and cleanup are counted separately. The passing run used three Gemini calls and three ATS requests. An earlier run used three Gemini calls before finding the application navigation race; its workspaces were also cleaned. No personal resume was used.

The script now writes to ignored `frontend/artifacts/live/` so later Playwright runs cannot erase its files. The initially inspected run wrote to the older `test-results/live/` location, which a later browser run cleaned; this dated report preserves the observed outcomes. Run `npm run acceptance:live` explicitly when a fresh raw artifact set is needed.

## Error/security checks

| Case | How checked |
|---|---|
| Backend sleeping / hanging / HTML gateway page | Mocked BFF responses and fake-clock browser test; bounded stop and Retry |
| Gemini timeout | Mocked upstream timeout; safe 504 and no automatic mutation retry |
| Invalid PDF / malformed DOCX | Real hosted Python parser, plus BFF-safe error tests |
| Oversized file / absent consent | Browser controls and streamed BFF size/consent rejection |
| Quota exceeded | Mocked 429, visible recovery and restored submit controls |
| Database unavailable | Mocked 503; public database was not intentionally disabled |
| Unknown job | Live 404 and safe error translation |
| Invalid workspace / tampered or expired cookie | Signature/expiry tests; reject and clear cookie |
| Cross-site write / visitor-supplied gateway header | Rejected origin; server-controlled headers verified |
| Arbitrary proxy destination or route | Finite allowlist and query rejection tests |
| Sensitive backend exception | Test response contains fake database/secret text; none reaches browser |
| Export bypass | Existing Python verifier tests; BFF binary response and browser approval controls |

## Failures corrected during this migration

- Updated test locators to match accessible field labels and avoid Next.js’s separate route-announcer alert.
- Fixed the real application-creation race: a user could navigate before the database save completed. Completion now invalidates the application list. A 600ms delayed-save regression passes on desktop and phone.
- Limited hidden mobile navigation’s focusability and made Escape close the menu.
- Added an absolute two-minute wake-up deadline in addition to attempt/backoff limits.
- Prevented late client responses from restoring cleared profile/match/version state.
- Retained compatible TypeScript 5.9 for OpenAPI generation. ESLint 10 failed the current Next.js React plugin; ESLint 9.39.5 is pinned until that plugin supports the newer API. This is a development-tool maintenance item, not a reason to force an incompatible install.

## Remaining release gates

- Vercel account authentication/token, preview creation and preview acceptance.
- Production Vercel environment/origin/domain confirmation, deployment and hosted acceptance.
- Exact Render frontend/CORS origin update once the Vercel URL exists; BFF server-to-server calls already work independently of browser CORS.
- Acceptance of the documented 4 MiB frontend upload difference and physical Safari checks before Streamlit retirement.

No paid hosting was enabled. No Render service was suspended or deleted. See [deployment steps](NEXTJS_MIGRATION.md) and [feature limits](MIGRATION_MATRIX.md).
