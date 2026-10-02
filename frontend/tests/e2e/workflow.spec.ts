import { expect, test, type Page } from "@playwright/test";
import {
  candidate,
  job,
  requirement,
  match,
  version,
  application,
  runtime,
} from "../fixtures";
import type { Application, Job } from "@/types";

async function mockBackend(page: Page, sleeping = false) {
  let jobs: Job[] = [];
  let applications: Application[] = [];
  let analyzed = false;
  let calls = 0;
  await page.route("**/api/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    const method = route.request().method();
    const respond = (body: unknown, status = 200) =>
      route.fulfill({
        status,
        contentType: "application/json",
        body: JSON.stringify(body),
      });
    if (path === "/api/workspace" && method === "POST")
      return respond({
        expiresAt: new Date(Date.now() + 86400000).toISOString(),
      });
    if (path === "/api/health")
      return sleeping
        ? respond(
            { error: { code: "UNAVAILABLE", message: "Backend is waking" } },
            503,
          )
        : respond({ status: "ready" });
    if (path === "/api/settings") return respond(runtime);
    if (path === "/api/profile/parse") {
      calls++;
      return respond(candidate);
    }
    if (path === "/api/jobs/import") {
      jobs = [job];
      return respond(job);
    }
    if (path === "/api/jobs/discover") {
      jobs = [{ ...job, source: route.request().postDataJSON().source }];
      return respond(jobs);
    }
    if (path === "/api/jobs") return respond(jobs);
    if (path === `/api/jobs/${job.id}`) return respond(job);
    if (path.endsWith("/analyze")) {
      calls++;
      analyzed = true;
      return respond(requirement);
    }
    if (path.endsWith("/requirements"))
      return analyzed
        ? respond(requirement)
        : respond(
            { error: { code: "CONFLICT", message: "Analyze first" } },
            409,
          );
    if (path === "/api/matches") return respond(match);
    if (path === "/api/resumes/tailor") {
      calls++;
      return respond(version);
    }
    if (path.startsWith("/api/resumes/export/"))
      return route.fulfill({
        status: 200,
        contentType: path.endsWith("pdf")
          ? "application/pdf"
          : "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        body: path.endsWith("pdf")
          ? "%PDF synthetic download"
          : "PK synthetic download",
      });
    if (path === "/api/applications" && method === "POST") {
      await new Promise((resolve) => setTimeout(resolve, 600));
      applications = [application];
      return respond(application);
    }
    if (path === "/api/applications" && method === "GET")
      return respond(applications);
    if (path === `/api/applications/${application.id}` && method === "PATCH") {
      applications = [
        { ...application, status: route.request().postDataJSON().status },
      ];
      return respond(applications[0]);
    }
    if (path === "/api/insights/skills")
      return respond({
        source: "live",
        skills: jobs.length ? [{ skill: "Python", job_count: 1 }] : [],
      });
    if (path === "/api/workspace" && method === "DELETE") {
      jobs = [];
      applications = [];
      analyzed = false;
      return respond({ status: "deleted" });
    }
    return respond(
      { error: { code: "NOT_FOUND", message: "Missing record" } },
      404,
    );
  });
  return { aiCalls: () => calls };
}
async function navigate(page: Page, name: string) {
  if (
    await page
      .getByRole("button", { name: "Open navigation", exact: true })
      .isVisible()
  )
    await page
      .getByRole("button", { name: "Open navigation", exact: true })
      .click();
  await page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("link", { name, exact: true })
    .click();
}
for (const workflowWidth of [1366, 390]) {
  test(`complete evidence workflow at ${workflowWidth}px with explicit AI actions and clearing`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: workflowWidth, height: 900 });
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    const backend = await mockBackend(page);
    await page.goto("/");
    await expect(
      page.getByText("Backend ready", { exact: true }),
    ).toBeVisible();
    expect(backend.aiCalls()).toBe(0);
    await page
      .getByRole("link", { name: "Analyze my resume", exact: true })
      .click();
    await page.getByLabel("Resume file").setInputFiles({
      name: "synthetic.pdf",
      mimeType: "application/pdf",
      buffer: Buffer.from("%PDF-test"),
    });
    await expect(
      page.getByRole("button", { name: "Extract my profile" }),
    ).toBeDisabled();
    await page
      .getByRole("checkbox", { name: /I agree to send this resume/ })
      .check();
    await page.getByRole("button", { name: "Extract my profile" }).click();
    await page.getByRole("checkbox", { name: /Review this fact/ }).check();
    await expect(page.getByText("1 / 1 reviewed")).toBeVisible();
    await navigate(page, "Jobs");
    await page.getByLabel("Job title", { exact: true }).fill(job.title);
    await page.getByLabel("Company", { exact: true }).fill(job.company);
    await page
      .getByRole("textbox", { name: /^Job description/ })
      .fill(job.description);
    await page.getByRole("button", { name: "Import job", exact: true }).click();
    await expect(
      page.getByText("Open status has not been independently verified."),
    ).toBeVisible();
    await page.getByRole("link", { name: "View & analyze" }).click();
    expect(backend.aiCalls()).toBe(1);
    await page
      .getByRole("button", { name: "Analyze requirements with Gemini" })
      .click();
    await expect(
      page.getByRole("heading", { name: "Structured job requirements" }),
    ).toBeVisible();
    await page.getByRole("link", { name: "Match my profile" }).click();
    await page
      .getByRole("button", { name: "Calculate Career Fit Score" })
      .click();
    await expect(page.getByText("77.50")).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Requirement-to-evidence map" }),
    ).toBeVisible();
    await navigate(page, "Resume Studio");
    await page
      .getByRole("checkbox", { name: /I agree to send my reviewed/ })
      .check();
    await page
      .getByRole("button", { name: "Create verified resume extract" })
      .click();
    await expect(
      page.getByRole("button", { name: "Download PDF" }),
    ).toBeDisabled();
    await page
      .getByRole("checkbox", { name: /I reviewed this extract/ })
      .check();
    for (const format of ["PDF", "DOCX"]) {
      const download = page.waitForEvent("download");
      await page
        .getByRole("button", { name: `Download ${format}`, exact: true })
        .click();
      expect((await download).suggestedFilename()).toBe(
        `hireme-resume-extract.${format.toLowerCase()}`,
      );
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({
      path: `test-results/resume-${workflowWidth}.png`,
      fullPage: true,
      animations: "disabled",
    });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    expect(backend.aiCalls()).toBe(3);
    await navigate(page, "Jobs");
    await page
      .getByRole("button", { name: "Track application", exact: true })
      .click();
    await navigate(page, "Applications");
    await page.getByLabel("Application stage").selectOption("APPLIED");
    await page.getByRole("button", { name: "Save stage" }).click();
    await expect(
      page.getByRole("button", { name: "Save stage" }),
    ).toBeDisabled();
    await navigate(page, "Insights");
    await expect(
      page.getByRole("heading", { name: "Recognized skill frequency" }),
    ).toBeVisible();
    await page
      .getByRole("link", { name: "Temporary workspace & privacy" })
      .click();
    await page.getByRole("checkbox", { name: /I want to delete/ }).check();
    await page.getByRole("button", { name: "Clear workspace data" }).click();
    await expect(page.getByText(/Workspace data cleared/)).toBeVisible();
    await navigate(page, "Jobs");
    await expect(
      page.getByRole("heading", { name: "Your next role starts here" }),
    ).toBeVisible();
    await navigate(page, "Profile");
    await expect(
      page.getByRole("heading", { name: "Candidate Fact Ledger" }),
    ).toHaveCount(0);
    expect(errors).toEqual([]);
  });
}

test("backend wake-up never blocks navigation or form preparation and stops polling", async ({
  page,
}) => {
  await page.clock.install();
  const backend = await mockBackend(page, true);
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Your next move/ }),
  ).toBeVisible();
  await expect(
    page.getByText("Waking up HireMe AI backend…", { exact: true }),
  ).toBeVisible();
  await navigate(page, "Jobs");
  await page
    .getByLabel("Job title", { exact: true })
    .fill("Prepared while sleeping");
  await expect(
    page.getByRole("button", { name: "Import job", exact: true }),
  ).toBeDisabled();
  await navigate(page, "Architecture");
  await expect(
    page.getByRole("heading", { name: /AI extracts/ }),
  ).toBeVisible();
  for (let i = 0; i < 9; i++) {
    await page.clock.fastForward(10000);
    await page.waitForTimeout(1);
  }
  await expect(
    page.getByRole("button", { name: "Retry connection" }),
  ).toBeVisible();
  expect(backend.aiCalls()).toBe(0);
});
for (const [width, height] of [
  [1920, 1080],
  [1440, 900],
  [1366, 768],
  [1024, 768],
  [768, 1024],
  [390, 844],
]) {
  test(`responsive layout at ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await mockBackend(page);
    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: /Your next move/ }),
    ).toBeVisible();
    for (const name of [
      "Overview",
      "Profile",
      "Jobs",
      "Match",
      "Resume Studio",
      "Applications",
      "Insights",
      "Architecture",
    ]) {
      await navigate(page, name);
      await expect(page.locator("main h1")).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth,
        ),
      ).toBe(true);
      if (width <= 900)
        await expect(
          page.getByRole("button", { name: "Open navigation", exact: true }),
        ).toBeVisible();
    }
    await navigate(page, "Overview");
    await page.screenshot({
      path: `test-results/overview-${width}.png`,
      fullPage: true,
      animations: "disabled",
    });
  });
}
test("upload size feedback and provider quota error are recoverable", async ({
  page,
}) => {
  await mockBackend(page);
  await page.route("**/api/profile/parse", (route) =>
    route.fulfill({
      status: 429,
      contentType: "application/json",
      body: JSON.stringify({
        error: {
          code: "QUOTA",
          message: "The current usage limit has been reached.",
        },
      }),
    }),
  );
  await page.goto("/profile");
  await expect(page.getByText("Backend ready", { exact: true })).toBeVisible();
  await page.getByLabel("Resume file").setInputFiles({
    name: "huge.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.alloc(4 * 1024 * 1024 + 1),
  });
  await expect(page.locator("main").getByRole("alert")).toContainText(
    "smaller than 4 MB",
  );
  await page.getByLabel("Resume file").setInputFiles({
    name: "valid.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from("%PDF-test"),
  });
  await page.getByRole("checkbox", { name: /I agree/ }).check();
  await page.getByRole("button", { name: "Extract my profile" }).click();
  await expect(page.locator("main").getByRole("alert")).toContainText(
    "usage limit",
  );
  await expect(
    page.getByRole("button", { name: "Extract my profile" }),
  ).toBeEnabled();
});
