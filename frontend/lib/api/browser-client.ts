import { ApiError, type ErrorCode } from "@/lib/errors";

export async function api<T>(
  path: string,
  options: {
    method?: string;
    body?: unknown;
    signal?: AbortSignal;
    download?: boolean;
  } = {},
): Promise<T> {
  const multipart = options.body instanceof FormData;
  let response: Response;
  try {
    response = await fetch(`/api/${path.replace(/^\/+/, "")}`, {
      method: options.method ?? "GET",
      credentials: "same-origin",
      cache: "no-store",
      headers:
        options.body && !multipart
          ? { "Content-Type": "application/json" }
          : undefined,
      body: options.body
        ? multipart
          ? (options.body as FormData)
          : JSON.stringify(options.body)
        : undefined,
      signal: options.signal ?? AbortSignal.timeout(110000),
    });
  } catch (error) {
    if (options.signal?.aborted) throw error;
    throw new ApiError(
      503,
      "Could not reach HireMe AI. Check your connection and backend status.",
      "UNAVAILABLE",
    );
  }
  if (!response.ok) {
    let data: unknown;
    try {
      data = await response.json();
    } catch {
      /* A hosting error can be HTML. */
    }
    if (
      data &&
      typeof data === "object" &&
      "error" in data &&
      data.error &&
      typeof data.error === "object" &&
      "message" in data.error &&
      typeof data.error.message === "string"
    ) {
      throw new ApiError(
        response.status,
        data.error.message,
        ("code" in data.error ? data.error.code : "INTERNAL") as ErrorCode,
      );
    }
    throw new ApiError(
      response.status,
      response.status === 413
        ? "This upload is too large. Choose a file smaller than 4 MB."
        : "The service is temporarily unavailable. Please check backend status.",
      response.status === 413 ? "TOO_LARGE" : "UNAVAILABLE",
    );
  }
  return options.download
    ? ((await response.blob()) as T)
    : ((await response.json()) as T);
}
export function saveDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
