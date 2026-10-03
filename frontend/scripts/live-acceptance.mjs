/** Explicit release check. Uses three real Gemini calls and three ATS requests. */
import { chromium, expect } from "@playwright/test";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import assert from "node:assert/strict";

if (process.env.ALLOW_LIVE_AI !== "1")
  throw new Error(
    "Set ALLOW_LIVE_AI=1 to authorize the synthetic live acceptance requests.",
  );
const base = process.env.ACCEPTANCE_URL || "http://127.0.0.1:3000";
const artifacts = process.env.ACCEPTANCE_ARTIFACT_DIR || "artifacts/live";
await mkdir(artifacts, { recursive: true });
const results = [];
function pass(name) {
  results.push({ check: name, status: "passed" });
  console.log(`PASS: ${name}`);
}
function syntheticPDF() {
  const lines = [
    "Synthetic Acceptance Candidate",
    "Backend developer with 2 years of experience.",
    "Skills: Python, SQL, FastAPI, PostgreSQL.",
    "Built a Python API using FastAPI and PostgreSQL.",
    "Wrote SQL queries for a sample project.",
  ];
  const content = `BT /F1 12 Tf 50 780 Td ${lines.map((line, index) => `${index ? "0 -22 Td " : ""}(${line}) Tj`).join("\n")} ET`;
  const objects = [
    "<< /Type /Catalog /Pages 2 0 R >>",
    "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    `<< /Length ${Buffer.byteLength(content)} >>\nstream\n${content}\nendstream`,
  ];
  let pdf = "%PDF-1.4\n";
  const offsets = [0];
  objects.forEach((object, index) => {
    offsets.push(Buffer.byteLength(pdf));
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  });
  const xref = Buffer.byteLength(pdf);
  pdf += `xref\n0 6\n0000000000 65535 f \n${offsets
    .slice(1)
    .map((offset) => `${String(offset).padStart(10, "0")} 00000 n \n`)
    .join("")}trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF`;
  return Buffer.from(pdf);
}
const browser = await chromium.launch({
  headless: true,
  ...(process.env.PLAYWRIGHT_EXECUTABLE_PATH
    ? { executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH }
    : {}),
});
const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  acceptDownloads: true,
});
const other = await browser.newContext();
// Restrict preview authentication to the tested origin; never send it to ATS links.
const bypass = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;
if (bypass) {
  for (const session of [context, other]) {
    await session.route("**/*", async (route) => {
      const request = route.request();
      if (new URL(request.url()).origin !== new URL(base).origin)
        return route.continue();
      await route.continue({
        headers: {
          ...request.headers(),
          "x-vercel-protection-bypass": bypass,
        },
      });
    });
  }
}
const page = await context.newPage();
const second = await other.newPage();
page.setDefaultTimeout(110000);
second.setDefaultTimeout(110000);
const consoleErrors = [];
page.on("pageerror", (error) => consoleErrors.push(error.message));
let initialized = false;
let otherInitialized = false;
async function navigate(name) {
  if (
    await page
      .getByRole("button", { name: "Open navigation", exact: true })
      .isVisible()
  )
    await page
      .getByRole("button", { name: "Open navigation", exact: true })
      .click();
  await page
    .getByRole("navigation")
    .getByRole("link", { name, exact: true })
    .click();
}
async function call(target, path, method = "GET", payload) {
  return target.evaluate(
    async ({ path, method, payload }) => {
      const response = await fetch(`/api/${path}`, {
        method,
        ...(payload
          ? {
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload),
            }
          : {}),
      });
      let body;
      try {
        body = await response.json();
      } catch {
        body = null;
      }
      return { status: response.status, body };
    },
    { path, method, payload },
  );
}
try {
  const start = performance.now();
  await page.goto(base, { waitUntil: "domcontentloaded" });
  await expect(
    page.getByRole("heading", { name: /Your next move/ }),
  ).toBeVisible();
  results.push({
    check:
      "Homepage DOM render (local or specified host, not a performance benchmark)",
    status: "passed",
    milliseconds: Math.round(performance.now() - start),
  });
  await expect(page.getByText("Backend ready", { exact: true })).toBeVisible({
    timeout: 180000,
  });
  initialized = true;
  pass("Anonymous session and live backend ready");
  const settings = await call(page, "settings");
  assert.equal(settings.body.mode, "live");
  assert.equal(settings.body.public_site, true);
  assert.equal("model" in settings.body, false);
  pass("Production live configuration is filtered by BFF");
  await navigate("Profile");
  await page.getByLabel("Resume file").setInputFiles({
    name: "synthetic-acceptance.pdf",
    mimeType: "application/pdf",
    buffer: syntheticPDF(),
  });
  await expect(
    page.getByRole("button", { name: "Extract my profile" }),
  ).toBeDisabled();
  await page
    .getByRole("checkbox", { name: /I agree to send this resume/ })
    .check();
  const profileResponse = page.waitForResponse((response) =>
    response.url().endsWith("/api/profile/parse"),
  );
  await page.getByRole("button", { name: "Extract my profile" }).click();
  const parsed = await profileResponse;
  assert.equal(
    parsed.status(),
    200,
    `Profile extraction HTTP ${parsed.status()}`,
  );
  const profile = await parsed.json();
  assert.ok(profile.facts.length);
  pass("Synthetic PDF parsed and candidate facts extracted by real Gemini");
  const review = page.getByRole("checkbox", { name: /Review this fact/ });
  const count = await review.count();
  for (let index = 0; index < count; index++) await review.first().check();
  pass("Every synthetic candidate fact reviewed through the interface");
  await page.screenshot({
    path: `${artifacts}/profile.png`,
    fullPage: true,
    animations: "disabled",
  });
  await navigate("Jobs");
  await page
    .getByLabel("Job title", { exact: true })
    .fill("Synthetic Backend Engineer");
  await page
    .getByLabel("Company", { exact: true })
    .fill("Migration Acceptance");
  await page
    .getByRole("textbox", { name: /^Job description/ })
    .fill(
      "Build backend APIs using Python, FastAPI, SQL and PostgreSQL. Requires two years of relevant software development experience. This is a synthetic acceptance test, not a real job posting.",
    );
  const imported = page.waitForResponse((response) =>
    response.url().endsWith("/api/jobs/import"),
  );
  await page.getByRole("button", { name: "Import job", exact: true }).click();
  const jobResponse = await imported;
  assert.equal(jobResponse.status(), 200);
  const job = await jobResponse.json();
  pass("Manual job persisted through Next.js BFF to hosted PostgreSQL");
  await second.goto(base);
  await expect(second.getByText("Backend ready", { exact: true })).toBeVisible({
    timeout: 180000,
  });
  otherInitialized = true;
  assert.deepEqual((await call(second, "jobs")).body, []);
  assert.equal((await call(second, `jobs/${job.id}`)).status, 404);
  const otherJob = await call(second, "jobs/import", "POST", {
    title: "Other workspace synthetic role",
    company: "Isolation Test",
    description:
      "This synthetic backend engineering role requires Python and SQL. It tests workspace isolation only.",
  });
  assert.equal(otherJob.status, 200);
  pass("Second clean browser session cannot read the first session's job");
  await page.getByRole("link", { name: "View & analyze" }).click();
  const analysisResponse = page.waitForResponse((response) =>
    response.url().endsWith(`/api/jobs/${job.id}/analyze`),
  );
  await page
    .getByRole("button", { name: "Analyze requirements with Gemini" })
    .click();
  assert.equal((await analysisResponse).status(), 200);
  await expect(
    page.getByRole("heading", { name: "Structured job requirements" }),
  ).toBeVisible();
  pass("Explicit Gemini job analysis and structured requirements");
  await page.getByRole("link", { name: "Match my profile" }).click();
  await page
    .getByRole("button", { name: "Calculate Career Fit Score" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Career Fit Score", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Requirement-to-evidence map" }),
  ).toBeVisible();
  pass("Python match score and evidence map rendered");
  await page.screenshot({
    path: `${artifacts}/match.png`,
    fullPage: true,
    animations: "disabled",
  });
  await navigate("Resume Studio");
  await page
    .getByRole("checkbox", { name: /I agree to send my reviewed/ })
    .check();
  const generated = page.waitForResponse((response) =>
    response.url().endsWith("/api/resumes/tailor"),
  );
  await page
    .getByRole("button", { name: "Create verified resume extract" })
    .click();
  const resumeResponse = await generated;
  assert.equal(resumeResponse.status(), 200);
  const version = await resumeResponse.json();
  assert.equal(version.verification_status, "PASSED");
  assert.ok(version.bullets.length);
  pass("Real Gemini evidence selection and Python verification passed");
  await expect(
    page.getByRole("button", { name: "Download PDF" }),
  ).toBeDisabled();
  await page.getByRole("checkbox", { name: /I reviewed this extract/ }).check();
  for (const [format, magic] of [
    ["PDF", "%PDF"],
    ["DOCX", "PK"],
  ]) {
    const pending = page.waitForEvent("download");
    await page
      .getByRole("button", { name: `Download ${format}`, exact: true })
      .click();
    const download = await pending;
    const file = `${artifacts}/resume.${format.toLowerCase()}`;
    await download.saveAs(file);
    assert.ok(
      (await readFile(file))
        .subarray(0, magic.length)
        .equals(Buffer.from(magic)),
    );
    pass(`${format} exported by Python and downloaded in browser`);
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: `${artifacts}/resume-mobile.png`,
    fullPage: true,
    animations: "disabled",
  });
  assert.ok(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  );
  pass("Populated resume view fits a 390px phone viewport");
  await page.setViewportSize({ width: 1440, height: 900 });
  await navigate("Jobs");
  await page
    .getByRole("button", { name: "Track application", exact: true })
    .click();
  await navigate("Applications");
  await page.getByLabel("Application stage").selectOption("APPLIED");
  const savedStage = page.waitForResponse(
    (response) =>
      response.url().includes("/api/applications/") &&
      response.request().method() === "PATCH",
  );
  await page.getByRole("button", { name: "Save stage" }).click();
  assert.equal((await savedStage).status(), 200);
  await expect(page.getByRole("button", { name: "Save stage" })).toBeDisabled();
  assert.equal((await call(page, "applications")).body[0].status, "APPLIED");
  assert.deepEqual((await call(second, "applications")).body, []);
  pass("Application creation, status persistence and cross-session isolation");
  await navigate("Insights");
  await expect(
    page.getByRole("heading", { name: "Recognized skill frequency" }),
  ).toBeVisible();
  pass("Workspace-only skill insights rendered");
  for (const [source, board] of [
    ["greenhouse", "stripe"],
    ["lever", "zoox"],
    ["ashby", "linear"],
  ]) {
    const found = await call(page, "jobs/discover", "POST", {
      source,
      board,
      query: "",
    });
    assert.equal(found.status, 200, `${source}: HTTP ${found.status}`);
    assert.ok(found.body.length > 0 && found.body.length <= 20);
    assert.ok(
      found.body.every(
        (item) => item.source === source && item.status === "UNKNOWN",
      ),
    );
    assert.equal((await call(page, `jobs/${found.body[0].id}`)).status, 200);
    pass(
      `${source}: real ATS jobs imported, capped at 20, status remains UNKNOWN`,
    );
  }
  for (const [filename, contentType] of [
    ["invalid.pdf", "application/pdf"],
    [
      "invalid.docx",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ],
  ]) {
    const code = await page.evaluate(
      async ({ filename, contentType }) => {
        const form = new FormData();
        form.append(
          "file",
          new File(["not a valid document"], filename, { type: contentType }),
        );
        form.append("consent", "true");
        return (
          await fetch("/api/profile/parse", { method: "POST", body: form })
        ).status;
      },
      { filename, contentType },
    );
    assert.equal(code, 422);
    pass(`${filename}: Python parser rejects malformed content`);
  }
  assert.equal((await call(page, "jobs/nonexistent-job")).status, 404);
  pass("Unknown job returns a safe missing-record error");
  await page
    .getByRole("link", { name: "Temporary workspace & privacy" })
    .click();
  await page.getByRole("checkbox", { name: /I want to delete/ }).check();
  await page.getByRole("button", { name: "Clear workspace data" }).click();
  await expect(page.getByText(/Workspace data cleared/)).toBeVisible();
  assert.deepEqual((await call(page, "jobs")).body, []);
  assert.deepEqual((await call(page, "applications")).body, []);
  assert.equal((await call(second, `jobs/${otherJob.body.id}`)).status, 200);
  pass(
    "Clear-data deletes owned records without affecting the other workspace",
  );
  assert.deepEqual(consoleErrors, []);
  pass("No browser runtime exceptions during the live workflow");
} catch (error) {
  // Do not print response bodies or traces that could include credentials or profile data.
  results.push({
    check: "Live acceptance",
    status: "failed",
    reason:
      error instanceof Error
        ? error.message.slice(0, 700)
        : "Unknown test failure",
  });
  await page.screenshot({
    path: `${artifacts}/failure.png`,
    fullPage: true,
    animations: "disabled",
  });
  process.exitCode = 1;
} finally {
  if (initialized) {
    const cleanup = await call(page, "workspace", "DELETE").catch(() => ({
      status: 0,
    }));
    results.push({
      check: "First synthetic workspace cleanup",
      status: cleanup.status === 200 ? "passed" : "failed",
    });
  }
  if (otherInitialized) {
    const cleanup = await call(second, "workspace", "DELETE").catch(() => ({
      status: 0,
    }));
    results.push({
      check: "Second synthetic workspace cleanup",
      status: cleanup.status === 200 ? "passed" : "failed",
    });
  }
  await writeFile(
    `${artifacts}/results.json`,
    JSON.stringify(
      { testedAt: new Date().toISOString(), target: base, results },
      null,
      2,
    ),
  );
  if (results.some((result) => result.status === "failed"))
    process.exitCode = 1;
  console.log(`Acceptance report: ${artifacts}/results.json`);
  await browser.close();
}
