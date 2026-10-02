import { beforeEach, describe, expect, it, vi } from "vitest";
import { NextRequest } from "next/server";
import {
  createSession,
  verifySession,
  SESSION_SECONDS,
} from "@/lib/workspace/session";
import { handleBff } from "@/lib/api/bff";
import { resolveOperation } from "@/lib/api/operations";
import { backendError } from "@/lib/errors";
import { safeExternalUrl, scoreDisplay } from "@/lib/utils/presentation";
import { candidate, job, requirement, runtime, version } from "./fixtures";
const origin = "https://frontend.example";
function request(
  path: string,
  method = "GET",
  body?: unknown,
  token = createSession().token,
  originValue = origin,
) {
  return new NextRequest(`${origin}/api/${path}`, {
    method,
    headers: {
      origin: originValue,
      cookie: `hireme_workspace=${token}`,
      ...(body ? { "content-type": "application/json" } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
}
beforeEach(() => {
  vi.stubEnv(
    "SERVER_ONLY_WORKSPACE_SECRET",
    "unit-test-signing-key-32-characters-minimum",
  );
  vi.stubEnv("SERVER_ONLY_BACKEND_URL", "https://backend.example");
  vi.stubEnv(
    "SERVER_ONLY_BACKEND_GATEWAY_SECRET",
    "private-gateway-key-that-never-reaches-browser",
  );
  vi.stubEnv("SERVER_ONLY_SITE_ORIGIN", origin);
  vi.stubEnv("VERCEL", "");
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(Response.json({ status: "ok" })),
  );
});
describe("signed workspace", () => {
  it("issues distinct UUIDv4 workspaces and round-trips a signature", () => {
    const a = createSession();
    const b = createSession();
    expect(verifySession(a.token).id).toBe(a.session.id);
    expect(a.session.id).not.toBe(b.session.id);
    expect(a.session.expires - a.session.issued).toBe(SESSION_SECONDS);
  });
  it("rejects tampered, malformed, oversized and expired tokens", () => {
    const a = createSession(1000000);
    for (const token of [
      a.token + "x",
      "bad.token",
      "x".repeat(801),
      a.token.replace(/^./, "x"),
    ])
      expect(() => verifySession(token, 1000000)).toThrow();
    expect(() =>
      verifySession(a.token, 1000000 + SESSION_SECONDS * 1000),
    ).toThrow();
  });
  it("keeps the workspace ID out of the JSON body and marks its cookie HTTP-only", async () => {
    const response = await handleBff(
      new NextRequest(`${origin}/api/workspace`, {
        method: "POST",
        headers: { origin },
      }),
      ["workspace"],
    );
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ expiresAt: expect.any(String) });
    expect(response.headers.get("set-cookie")).toContain("HttpOnly");
    expect(response.headers.get("set-cookie")).toContain("SameSite=lax");
    expect(response.headers.get("cache-control")).toContain("no-store");
  });
  it("uses secure host cookies on Vercel", async () => {
    vi.stubEnv("VERCEL", "1");
    const response = await handleBff(
      new NextRequest(`${origin}/api/workspace`, {
        method: "POST",
        headers: { origin },
      }),
      ["workspace"],
    );
    expect(response.headers.get("set-cookie")).toContain(
      "__Host-hireme_workspace=",
    );
    expect(response.headers.get("set-cookie")).toContain("Secure");
  });
  it("retains a valid workspace on initialization", async () => {
    const token = createSession().token;
    const response = await handleBff(
      request("workspace", "POST", undefined, token),
      ["workspace"],
    );
    expect(response.cookies.get("hireme_workspace")?.value).toBe(token);
  });
});
describe("BFF security boundary", () => {
  it("rejects cross-origin mutation before contacting FastAPI", async () => {
    const result = await handleBff(
      request("jobs/import", "POST", {}, undefined, "https://attacker.example"),
      ["jobs", "import"],
    );
    expect(result.status).toBe(403);
    expect(fetch).not.toHaveBeenCalled();
  });
  it("rejects a spoofed cross-site request even with the expected origin", async () => {
    const req = request("workspace", "POST");
    req.headers.set("sec-fetch-site", "cross-site");
    expect((await handleBff(req, ["workspace"])).status).toBe(403);
  });
  it("rejects unsigned workspace IDs and removes invalid cookies", async () => {
    const result = await handleBff(
      request("jobs", "GET", undefined, "00000000-0000-4000-8000-000000000000"),
      ["jobs"],
    );
    expect(result.status).toBe(401);
    expect(result.headers.get("set-cookie")).toContain("Max-Age=0");
    expect(fetch).not.toHaveBeenCalled();
  });
  it("does not trust incoming gateway or workspace headers", async () => {
    const session = createSession();
    const req = request("jobs", "GET", undefined, session.token);
    req.headers.set("authorization", "Bearer attacker");
    req.headers.set("x-workspace-id", "attacker");
    vi.mocked(fetch).mockResolvedValueOnce(Response.json([]));
    expect((await handleBff(req, ["jobs"])).status).toBe(200);
    const [url, init] = vi.mocked(fetch).mock.calls[0];
    expect(String(url)).toBe("https://backend.example/api/v1/jobs");
    const headers = init?.headers as Headers;
    expect(headers.get("authorization")).toBe(
      "Bearer private-gateway-key-that-never-reaches-browser",
    );
    expect(headers.get("x-workspace-id")).toBe(session.session.id);
    expect(init?.cache).toBe("no-store");
    expect(init?.redirect).toBe("error");
  });
  it("cannot forward arbitrary routes or query strings", async () => {
    for (const segments of [
      ["..", "admin"],
      ["https:", "evil"],
      ["settings", "check-gemini"],
      ["profile", "demo"],
      ["jobs", "id?url=evil"],
    ])
      expect(resolveOperation("POST", segments)).toBeNull();
    const result = await handleBff(
      request("jobs?url=https://attacker.example"),
      ["jobs"],
    );
    expect(result.status).toBe(400);
    expect(fetch).not.toHaveBeenCalled();
  });
  it("validates job import before forwarding", async () => {
    const result = await handleBff(
      request("jobs/import", "POST", {
        title: "Engineer",
        company: "Test",
        description: "too short",
      }),
      ["jobs", "import"],
    );
    expect(result.status).toBe(422);
    expect(fetch).not.toHaveBeenCalled();
  });
  it("encodes ATS inputs and rejects unsupported board URLs", async () => {
    const rejected = await handleBff(
      request("jobs/discover", "POST", {
        source: "lever",
        board: "https://evil.example",
        query: "",
      }),
      ["jobs", "discover"],
    );
    expect(rejected.status).toBe(422);
    vi.mocked(fetch).mockResolvedValueOnce(Response.json([]));
    const response = await handleBff(
      request("jobs/discover", "POST", {
        source: "ashby",
        board: "example-board",
        query: "Python & SQL",
      }),
      ["jobs", "discover"],
    );
    expect(response.status).toBe(200);
    expect(String(vi.mocked(fetch).mock.calls[0][0])).toContain(
      "query=Python+%26+SQL",
    );
  });
  it("exposes presentation settings without provider configuration", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      Response.json({
        ...runtime,
        gemini_key_configured: true,
        model: "private-model",
      }),
    );
    const response = await handleBff(request("settings"), ["settings"]);
    expect(await response.json()).toEqual(runtime);
  });
  it("sends no credentials and invokes no AI on health", async () => {
    const result = await handleBff(request("health"), ["health"]);
    expect(result.status).toBe(200);
    const [url, init] = vi.mocked(fetch).mock.calls[0];
    expect(String(url)).toBe("https://backend.example/health");
    expect((init?.headers as Headers).has("authorization")).toBe(false);
  });
  it("returns binary exports with private caching headers", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      Response.json({
        content: Buffer.from("%PDF synthetic").toString("base64"),
      }),
    );
    const result = await handleBff(
      request("resumes/export/pdf", "POST", { candidate, version }),
      ["resumes", "export", "pdf"],
    );
    expect(result.status).toBe(200);
    expect(result.headers.get("content-type")).toBe("application/pdf");
    expect(await result.text()).toContain("%PDF");
  });
  it("requires tailoring consent", async () => {
    const result = await handleBff(
      request("resumes/tailor", "POST", {
        candidate,
        requirement,
        job_id: job.id,
        company: job.company,
        consent: false,
      }),
      ["resumes", "tailor"],
    );
    expect(result.status).toBe(422);
    expect(fetch).not.toHaveBeenCalled();
  });
  it("keeps the cookie when clearing data so quotas do not reset", async () => {
    const result = await handleBff(request("workspace", "DELETE"), [
      "workspace",
    ]);
    expect(result.status).toBe(200);
    expect(result.headers.has("set-cookie")).toBe(false);
  });
  it.each([400, 401, 404, 409, 422, 429, 500, 502, 503, 504])(
    "normalizes HTTP %s without leaking backend details",
    async (status) => {
      vi.mocked(fetch).mockResolvedValueOnce(
        Response.json(
          { detail: "postgres://password@host trace secret" },
          { status },
        ),
      );
      const result = await handleBff(request("jobs"), ["jobs"]);
      expect(result.status).toBe(status);
      const text = await result.text();
      expect(text).not.toContain("postgres");
      expect(text).not.toContain("password");
      expect(text).toContain("message");
      expect(fetch).toHaveBeenCalledTimes(1);
    },
  );
  it("normalizes hosting HTML and network timeout", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response("<html>Bad gateway</html>", { status: 502 }),
    );
    expect((await handleBff(request("jobs"), ["jobs"])).status).toBe(503);
    vi.mocked(fetch).mockRejectedValueOnce(
      new DOMException("secret details", "TimeoutError"),
    );
    const result = await handleBff(request("jobs"), ["jobs"]);
    expect(result.status).toBe(504);
    expect(await result.text()).not.toContain("secret details");
  });
});
describe("upload bridge", () => {
  function upload(file: File, consent = "true") {
    const body = new FormData();
    body.append("file", file);
    body.append("consent", consent);
    return new NextRequest(`${origin}/api/profile/parse`, {
      method: "POST",
      headers: { origin, cookie: `hireme_workspace=${createSession().token}` },
      body,
    });
  }
  it("forwards consented multipart data for Python validation", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(Response.json(candidate));
    const result = await handleBff(
      upload(new File(["%PDF-test"], "test.pdf", { type: "application/pdf" })),
      ["profile", "parse"],
    );
    expect(result.status).toBe(200);
    const [url, init] = vi.mocked(fetch).mock.calls[0];
    expect(String(url)).toContain("consent=true");
    expect(init?.body).toBeInstanceOf(FormData);
    expect((init?.headers as Headers).has("content-type")).toBe(false);
  });
  it("rejects missing consent, unsupported extensions, empty files and oversized uploads", async () => {
    for (const [file, consent, status] of [
      [new File(["pdf"], "a.pdf"), "false", 422],
      [new File(["bad"], "a.exe"), "true", 422],
      [new File([], "a.pdf"), "true", 422],
      [new File([new Uint8Array(4 * 1024 * 1024 + 1)], "a.pdf"), "true", 413],
    ] as const)
      expect(
        (await handleBff(upload(file, consent), ["profile", "parse"])).status,
      ).toBe(status);
    expect(fetch).not.toHaveBeenCalled();
  });
  it.each(["Malformed or unreadable PDF", "Malformed or unreadable DOCX"])(
    "preserves the safe parser explanation: %s",
    async (detail) => {
      vi.mocked(fetch).mockResolvedValueOnce(
        Response.json({ detail }, { status: 422 }),
      );
      const result = await handleBff(
        upload(new File(["invalid data"], "file.pdf")),
        ["profile", "parse"],
      );
      expect(await result.text()).toContain(detail);
    },
  );
});
describe("presentation helpers", () => {
  it("preserves a backend score without inventing accuracy", () => {
    expect(scoreDisplay(77.5)).toBe("77.50");
    expect(scoreDisplay(90)).toBe("90");
    expect(scoreDisplay(NaN)).toBe("Not available");
  });
  it("blocks script and credential links", () => {
    expect(safeExternalUrl("javascript:alert(1)")).toBeNull();
    expect(safeExternalUrl("https://user:secret@example.com")).toBeNull();
    expect(safeExternalUrl("https://example.com/careers")).toBe(
      "https://example.com/careers",
    );
  });
  it("allows only known error details", () => {
    expect(
      backendError(500, { detail: "Traceback secret" }).message,
    ).not.toContain("Traceback");
  });
});
