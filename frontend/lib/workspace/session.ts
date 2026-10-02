import "server-only";
import { createHmac, randomUUID, timingSafeEqual } from "node:crypto";
import { z } from "zod";
import { ApiError } from "@/lib/errors";

export const SESSION_SECONDS = 24 * 60 * 60;
export const cookieName = () =>
  process.env.VERCEL === "1" ? "__Host-hireme_workspace" : "hireme_workspace";
const payloadSchema = z
  .object({
    v: z.literal(1),
    id: z.string().uuid(),
    issued: z.number().int(),
    expires: z.number().int(),
  })
  .strict();
export type Session = z.infer<typeof payloadSchema>;

function secret(): string {
  const value = process.env.SERVER_ONLY_WORKSPACE_SECRET;
  if (!value || value.length < 32)
    throw new ApiError(
      503,
      "The workspace service is not configured yet.",
      "UNAVAILABLE",
    );
  return value;
}
function signature(encoded: string): string {
  return createHmac("sha256", secret()).update(encoded).digest("base64url");
}
export function createSession(now = Date.now()): {
  token: string;
  session: Session;
} {
  const issued = Math.floor(now / 1000);
  const session: Session = {
    v: 1,
    id: randomUUID(),
    issued,
    expires: issued + SESSION_SECONDS,
  };
  const encoded = Buffer.from(JSON.stringify(session)).toString("base64url");
  return { token: `${encoded}.${signature(encoded)}`, session };
}
export function verifySession(token: string, now = Date.now()): Session {
  if (token.length > 800)
    throw new ApiError(
      401,
      "Your workspace session is invalid. Refresh to start a new session.",
      "SESSION",
    );
  const [encoded, supplied, extra] = token.split(".");
  const invalid = () =>
    new ApiError(
      401,
      "Your workspace session has expired or is invalid. Refresh to start a new session.",
      "SESSION",
    );
  if (!encoded || !supplied || extra) throw invalid();
  const expected = Buffer.from(signature(encoded));
  const received = Buffer.from(supplied);
  if (
    received.length !== expected.length ||
    !timingSafeEqual(received, expected)
  )
    throw invalid();
  try {
    const data = payloadSchema.parse(
      JSON.parse(Buffer.from(encoded, "base64url").toString("utf8")),
    );
    const seconds = Math.floor(now / 1000);
    if (
      !/^[\da-f]{8}-[\da-f]{4}-4[\da-f]{3}-[89ab][\da-f]{3}-[\da-f]{12}$/i.test(
        data.id,
      ) ||
      data.expires <= seconds ||
      data.issued > seconds + 60 ||
      data.expires - data.issued !== SESSION_SECONDS
    )
      throw invalid();
    return data;
  } catch {
    throw invalid();
  }
}
