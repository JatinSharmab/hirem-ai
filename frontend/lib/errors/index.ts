export type ErrorCode =
  | "VALIDATION"
  | "SESSION"
  | "GATEWAY"
  | "NOT_FOUND"
  | "CONFLICT"
  | "QUOTA"
  | "PROVIDER"
  | "UNAVAILABLE"
  | "TIMEOUT"
  | "INTERNAL"
  | "TOO_LARGE";
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code: ErrorCode = "INTERNAL",
  ) {
    super(message);
    this.name = "ApiError";
  }
}
export function normalizedError(status: number): ApiError {
  const map: Record<number, [ErrorCode, string]> = {
    400: ["VALIDATION", "Please check the form and try again."],
    401: [
      "GATEWAY",
      "The service connection needs attention. Please try again later.",
    ],
    403: ["GATEWAY", "This request could not be authorized."],
    404: [
      "NOT_FOUND",
      "This record is missing or has expired. Refresh your workspace.",
    ],
    409: [
      "CONFLICT",
      "This action is not ready yet. Analyze the job first and check the current mode.",
    ],
    413: [
      "TOO_LARGE",
      "This upload is too large. Choose a PDF or DOCX smaller than 4 MB.",
    ],
    422: [
      "VALIDATION",
      "The input could not be validated. Check the file, required fields and reviewed facts.",
    ],
    429: [
      "QUOTA",
      "The current usage limit has been reached. Daily allowances reset at midnight UTC; short-term limits may reset sooner.",
    ],
    502: [
      "PROVIDER",
      "The AI provider or an external job source could not complete this request. Please try again later.",
    ],
    503: [
      "UNAVAILABLE",
      "HireMe AI's backend is starting or temporarily unavailable. Check its status, then try again.",
    ],
    504: [
      "TIMEOUT",
      "The operation took too long. It may still be finishing. Check your records before submitting again.",
    ],
  };
  const entry = map[status] ?? [
    "INTERNAL",
    "Something went wrong. Please try again later.",
  ];
  return new ApiError(status, entry[1], entry[0]);
}
// Only these known parser errors may cross the server boundary. Never echo arbitrary detail.
const parserMessages = new Set([
  "Encrypted PDFs are not supported",
  "Resume must contain at most 50 pages",
  "Resume exceeds 30,000 text characters",
  "Malformed or unreadable PDF",
  "DOCX archive exceeds decompression limits",
  "Encrypted DOCX files are not supported",
  "Malformed or unreadable DOCX",
  "Only PDF and DOCX resumes are supported",
  "Resume contains no extractable text",
  "File extension is PDF but signature is invalid",
  "No grounded facts extracted. Try a text-based resume.",
  "Export requires nonempty, verified content",
]);
export function backendError(status: number, body: unknown): ApiError {
  const error = normalizedError(status);
  if (
    status === 422 &&
    typeof body === "object" &&
    body &&
    "detail" in body &&
    typeof body.detail === "string" &&
    parserMessages.has(body.detail)
  ) {
    return new ApiError(status, body.detail, "VALIDATION");
  }
  return error;
}
export function errorMessage(error: unknown): string {
  return error instanceof ApiError
    ? error.message
    : "Something went wrong. Please try again.";
}
