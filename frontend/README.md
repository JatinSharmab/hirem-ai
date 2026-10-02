# HireMe AI frontend

Next.js App Router, React, strict TypeScript, Tailwind CSS, Zod and Lucide. Python/FastAPI remains the business-logic source of truth.

Read [the migration and deployment guide](../docs/NEXTJS_MIGRATION.md), [feature parity matrix](../docs/MIGRATION_MATRIX.md), and [interview guide](../docs/FRONTEND_INTERVIEW_GUIDE.md).

```powershell
# Node 22.16+ within Node 22
npm ci
Copy-Item .env.example .env.local  # only if .env.local does not already exist
# Fill the server-only values in .env.local; never commit them.
npm run dev
```

Open **http://127.0.0.1:3000**. Use this exact origin when `SERVER_ONLY_SITE_ORIGIN` has that value. The interface loads even without a running backend.

```powershell
npm run lint
npm run typecheck
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```

The normal browser tests mock API responses and use no AI quota. The explicit live acceptance script uses three Gemini requests and three ATS requests, creates synthetic records, downloads synthetic exports and cleans its two workspaces:

```powershell
# Start npm run start in another terminal after building.
$env:ALLOW_LIVE_AI = '1'
npm run acceptance:live
```

`PLAYWRIGHT_EXECUTABLE_PATH` can point to a local Edge/Chrome installation. `ACCEPTANCE_URL` can target an authorized Vercel preview or production URL. Live artifacts are ignored under `artifacts/live/`.

Deploy with Vercel project root `frontend`, framework Next.js, Node 22, `npm ci`, and `npm run build`. Use the Hobby plan for this personal portfolio. No paid service upgrade or periodic keep-alive is configured.

Do not set a static export/output directory: the signed workspace and private BFF require server-side Route Handlers. Do not put the gateway secret, Gemini key or database URL in a `NEXT_PUBLIC_*` variable.
