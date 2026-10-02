import "server-only";
import { ApiError, backendError } from "@/lib/errors";

export function backendUrl(): URL {
  const value = process.env.SERVER_ONLY_BACKEND_URL;
  if (!value)
    throw new ApiError(
      503,
      "The backend connection is not configured yet.",
      "UNAVAILABLE",
    );
  let url: URL;
  try {
    url = new URL(value);
  } catch {
    throw new ApiError(
      503,
      "The backend connection needs attention.",
      "UNAVAILABLE",
    );
  }
  const local =
    process.env.VERCEL !== "1" &&
    ["localhost", "127.0.0.1", "[::1]"].includes(url.hostname);
  if (
    (url.protocol !== "https:" && !(local && url.protocol === "http:")) ||
    url.username ||
    url.password ||
    url.search ||
    url.hash ||
    url.pathname !== "/"
  ) {
    throw new ApiError(
      503,
      "The backend connection needs attention.",
      "UNAVAILABLE",
    );
  }
  return url;
}

export async function fastApiFetch(
  path: string,
  options: {
    method?: string;
    workspace?: string;
    body?: BodyInit;
    timeoutMs?: number;
  } = {},
): Promise<unknown> {
  // Paths originate exclusively in the operation allowlist, never from a URL supplied by a visitor.
  if (!path.startsWith("/") || path.startsWith("//"))
    throw new ApiError(400, "Invalid request.", "VALIDATION");
  const headers = new Headers({ Accept: "application/json" });
  if (options.workspace) {
    const gateway = process.env.SERVER_ONLY_BACKEND_GATEWAY_SECRET;
    if (process.env.VERCEL === "1" && (!gateway || gateway.length < 32))
      throw new ApiError(
        503,
        "The backend connection is not configured yet.",
        "UNAVAILABLE",
      );
    if (gateway) headers.set("Authorization", `Bearer ${gateway}`);
    headers.set("X-Workspace-ID", options.workspace);
  }
  if (typeof options.body === "string")
    headers.set("Content-Type", "application/json");
  let response: Response;
  try {
    response = await fetch(new URL(path, backendUrl()), {
      method: options.method ?? "GET",
      headers,
      body: options.body,
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(options.timeoutMs ?? 90000),
    });
  } catch (error) {
    if (error instanceof ApiError) throw error;
    const timeout =
      error instanceof Error &&
      ["TimeoutError", "AbortError"].includes(error.name);
    throw new ApiError(
      timeout ? 504 : 503,
      timeout
        ? "The operation took too long. It may still be finishing; check your records before trying again."
        : "HireMe AI's backend is starting or temporarily unavailable.",
      timeout ? "TIMEOUT" : "UNAVAILABLE",
    );
  }
  let body: unknown;
  try {
    body = await response.json();
  } catch {
    throw new ApiError(
      503,
      "HireMe AI's backend is starting or temporarily unavailable.",
      "UNAVAILABLE",
    );
  }
  if (!response.ok) throw backendError(response.status, body);
  return body;
}
