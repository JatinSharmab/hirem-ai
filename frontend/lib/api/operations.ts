import { z } from "zod";
import {
  applicationCreateSchema,
  applicationUpdateSchema,
  discoverSchema,
  exportSchema,
  importJobSchema,
  matchSchema,
  tailorSchema,
} from "@/lib/schemas";

export type Operation = {
  path: string;
  method: string;
  schema?: z.ZodType;
  query?: boolean;
  upload?: boolean;
  exportFormat?: "pdf" | "docx";
};
const idPattern = /^[A-Za-z0-9_-]{1,100}$/;
export function resolveOperation(
  method: string,
  segments: string[],
): Operation | null {
  if (segments.some((segment) => !idPattern.test(segment))) return null;
  const path = segments.join("/");
  const simple: Record<string, Operation> = {
    "GET settings": { path: "/api/v1/settings", method: "GET" },
    "POST profile/parse": {
      path: "/api/v1/profile/parse?consent=true",
      method: "POST",
      upload: true,
    },
    "GET jobs": { path: "/api/v1/jobs", method: "GET" },
    "POST jobs/import": {
      path: "/api/v1/jobs/import",
      method: "POST",
      schema: importJobSchema,
    },
    "POST jobs/discover": {
      path: "/api/v1/jobs/discover",
      method: "POST",
      schema: discoverSchema,
      query: true,
    },
    "POST matches": {
      path: "/api/v1/matches",
      method: "POST",
      schema: matchSchema,
    },
    "POST resumes/tailor": {
      path: "/api/v1/resumes/tailor",
      method: "POST",
      schema: tailorSchema,
    },
    "GET applications": { path: "/api/v1/applications", method: "GET" },
    "POST applications": {
      path: "/api/v1/applications",
      method: "POST",
      schema: applicationCreateSchema,
      query: true,
    },
    "GET insights/skills": { path: "/api/v1/insights/skills", method: "GET" },
    "DELETE workspace": { path: "/api/v1/workspace", method: "DELETE" },
  };
  if (simple[`${method} ${path}`]) return simple[`${method} ${path}`];
  if (segments[0] === "jobs" && segments.length === 2 && method === "GET")
    return { path: `/api/v1/jobs/${segments[1]}`, method };
  if (
    segments[0] === "jobs" &&
    segments.length === 3 &&
    ((segments[2] === "analyze" && method === "POST") ||
      (segments[2] === "requirements" && method === "GET"))
  )
    return { path: `/api/v1/jobs/${segments[1]}/${segments[2]}`, method };
  if (
    segments[0] === "applications" &&
    segments.length === 2 &&
    method === "PATCH"
  )
    return {
      path: `/api/v1/applications/${segments[1]}`,
      method,
      schema: applicationUpdateSchema,
      query: true,
    };
  if (
    segments[0] === "resumes" &&
    segments[1] === "export" &&
    segments.length === 3 &&
    ["pdf", "docx"].includes(segments[2]) &&
    method === "POST"
  )
    return {
      path: `/api/v1/resumes/export/${segments[2]}`,
      method,
      schema: exportSchema,
      exportFormat: segments[2] as "pdf" | "docx",
    };
  return null;
}
