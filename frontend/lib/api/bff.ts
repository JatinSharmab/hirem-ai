import "server-only";
import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { ApiError, normalizedError } from "@/lib/errors";
import { MAX_UPLOAD_BYTES } from "@/lib/schemas";
import {
  cookieName,
  createSession,
  verifySession,
} from "@/lib/workspace/session";
import { fastApiFetch } from "./server-client";
import { resolveOperation } from "./operations";

const privateHeaders = {
  "Cache-Control": "no-store, private",
  Vary: "Cookie",
  "X-Content-Type-Options": "nosniff",
};
function json(body: unknown, status = 200) {
  return NextResponse.json(body, { status, headers: privateHeaders });
}

export function requireSameOrigin(request: NextRequest): void {
  const origin = request.headers.get("origin");
  const allowed = new Set<string>();
  for (const value of [
    process.env.SERVER_ONLY_SITE_ORIGIN,
    process.env.VERCEL_URL && `https://${process.env.VERCEL_URL}`,
    process.env.VERCEL_PROJECT_PRODUCTION_URL &&
      `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`,
  ]) {
    if (value) {
      try {
        allowed.add(new URL(value).origin);
      } catch {
        /* Invalid configuration is never an allowed origin. */
      }
    }
  }
  if (
    !origin ||
    !allowed.has(origin) ||
    request.headers.get("sec-fetch-site") === "cross-site"
  )
    throw new ApiError(
      403,
      "Open this action from the HireMe AI website.",
      "GATEWAY",
    );
}

async function boundedBody(
  request: NextRequest,
  limit: number,
): Promise<Uint8Array<ArrayBuffer>> {
  const declared = Number(request.headers.get("content-length"));
  if (Number.isFinite(declared) && declared > limit) throw normalizedError(413);
  const reader = request.body?.getReader();
  if (!reader) return new Uint8Array();
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > limit) {
        await reader.cancel();
        throw normalizedError(413);
      }
      chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }
  const result = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) {
    result.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return result;
}

async function uploadBody(request: NextRequest): Promise<FormData> {
  const type = request.headers.get("content-type") ?? "";
  if (!type.startsWith("multipart/form-data;")) throw normalizedError(400);
  const raw = await boundedBody(request, MAX_UPLOAD_BYTES + 65536);
  const form = await new Response(raw, {
    headers: { "Content-Type": type },
  }).formData();
  const file = form.get("file");
  if (form.get("consent") !== "true")
    throw new ApiError(
      422,
      "Consent is required before resume text is sent to Gemini.",
      "VALIDATION",
    );
  if (!(file instanceof File) || !file.size || file.size > MAX_UPLOAD_BYTES)
    throw normalizedError(
      file instanceof File && file.size > MAX_UPLOAD_BYTES ? 413 : 422,
    );
  if (!/\.(pdf|docx)$/i.test(file.name))
    throw new ApiError(422, "Choose a PDF or DOCX resume.", "VALIDATION");
  const forwarded = new FormData();
  forwarded.append("file", file, file.name.slice(-200));
  return forwarded;
}

export async function handleBff(
  request: NextRequest,
  segments: string[],
): Promise<NextResponse> {
  try {
    if (!["GET", "HEAD"].includes(request.method)) requireSameOrigin(request);
    if (request.nextUrl.search)
      throw new ApiError(
        400,
        "Use the supported form fields for this action.",
        "VALIDATION",
      );
    if (segments.join("/") === "health" && request.method === "GET") {
      const result = z
        .object({ status: z.literal("ok") })
        .parse(await fastApiFetch("/health", { timeoutMs: 8000 }));
      return json({ status: result.status === "ok" ? "ready" : "waking" });
    }
    const token = request.cookies.get(cookieName())?.value;
    if (segments.join("/") === "workspace" && request.method === "POST") {
      const current = token
        ? { session: verifySession(token), token }
        : createSession();
      const response = json({
        expiresAt: new Date(current.session.expires * 1000).toISOString(),
      });
      response.cookies.set(cookieName(), current.token, {
        httpOnly: true,
        secure:
          process.env.VERCEL === "1" || request.nextUrl.protocol === "https:",
        sameSite: "lax",
        path: "/",
        maxAge: Math.max(
          1,
          current.session.expires - Math.floor(Date.now() / 1000),
        ),
      });
      return response;
    }
    const operation = resolveOperation(request.method, segments);
    if (!operation)
      return json(
        {
          error: {
            code: "NOT_FOUND",
            message: "This API operation is not available.",
          },
        },
        404,
      );
    if (!token)
      throw new ApiError(
        401,
        "Start a workspace session before using this action. Refresh the page to begin.",
        "SESSION",
      );
    const session = verifySession(token);
    let body: BodyInit | undefined;
    let path = operation.path;
    if (operation.upload) body = await uploadBody(request);
    else if (operation.schema) {
      if (!request.headers.get("content-type")?.startsWith("application/json"))
        throw normalizedError(400);
      const raw = await boundedBody(request, 600000);
      let input: unknown;
      try {
        input = JSON.parse(new TextDecoder().decode(raw));
      } catch {
        throw normalizedError(400);
      }
      const payload = operation.schema.parse(input);
      if (operation.query) {
        const params = new URLSearchParams();
        for (const [key, value] of Object.entries(
          payload as Record<string, unknown>,
        ))
          if (typeof value === "string") params.set(key, value);
        path += `?${params.toString()}`;
      } else body = JSON.stringify(payload);
    }
    const result = await fastApiFetch(path, {
      method: operation.method,
      workspace: session.id,
      body,
    });
    if (operation.exportFormat) {
      const data = z
        .object({
          content: z
            .string()
            .max(5500000)
            .regex(/^[A-Za-z0-9+/]*={0,2}$/),
        })
        .parse(result);
      const content = Buffer.from(data.content, "base64");
      if (content.length > MAX_UPLOAD_BYTES)
        throw new ApiError(
          502,
          "The export exceeded this frontend's delivery limit.",
          "PROVIDER",
        );
      return new NextResponse(content, {
        headers: {
          ...privateHeaders,
          "Content-Type":
            operation.exportFormat === "pdf"
              ? "application/pdf"
              : "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          "Content-Disposition": `attachment; filename="hireme-extract.${operation.exportFormat}"`,
        },
      });
    }
    // Configuration stays private; only presentation settings go to the browser.
    if (segments.join("/") === "settings") {
      const settings = z
        .object({
          mode: z.enum(["live", "demo"]),
          public_site: z.boolean(),
          retention_hours: z.number(),
          visitor_ai_limit: z.number(),
          live_discovery: z.boolean(),
        })
        .parse(result);
      return json(settings);
    }
    return json(result);
  } catch (error) {
    const safe =
      error instanceof ApiError
        ? error
        : error instanceof z.ZodError
          ? normalizedError(422)
          : normalizedError(500);
    const response = json(
      { error: { code: safe.code, message: safe.message } },
      safe.status,
    );
    if (safe.code === "SESSION")
      response.cookies.set(cookieName(), "", {
        httpOnly: true,
        secure: process.env.VERCEL === "1",
        sameSite: "lax",
        path: "/",
        maxAge: 0,
      });
    return response;
  }
}
