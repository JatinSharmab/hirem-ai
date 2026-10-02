import { z } from "zod";

const text = (max = 2000) => z.string().max(max);
const optionalText = (max = 2000) => text(max).nullable().optional();
const textList = z.array(text()).max(200);
export const factSchema = z
  .object({
    id: text(100),
    category: text(100),
    subject: text(300),
    predicate: text(300),
    value: text(2000),
    source_section: optionalText(),
    source_text: optionalText(3000),
    confidence: z.number().min(0).max(1),
    verified_by_user: z.boolean(),
    immutable: z.boolean(),
  })
  .strict();
export const candidateSchema = z
  .object({
    name: text(200).min(1),
    summary: text(4000),
    skills: textList,
    experience_years: z.number().min(0).max(80),
    locations: textList,
    facts: z.array(factSchema).max(200),
  })
  .strict();
export const requirementSchema = z
  .object({
    role_title: text(1000),
    role_family: optionalText(),
    mandatory_skills: textList,
    preferred_skills: textList,
    responsibilities: textList,
    education_requirements: textList,
    minimum_experience: z.number().nullable().optional(),
    maximum_experience: z.number().nullable().optional(),
    location: optionalText(),
    work_mode: optionalText(),
    employment_type: optionalText(),
    domain: optionalText(),
    seniority: optionalText(),
    certifications: textList,
    keywords: textList,
    salary: optionalText(),
    ambiguities: textList,
    confidence: z.number().min(0).max(1),
  })
  .strict();
export const jobSchema = z
  .object({
    id: text(100),
    source: text(100),
    external_job_id: optionalText(),
    title: text(1000),
    company: text(1000),
    location: optionalText(),
    work_mode: optionalText(),
    description: text(30000),
    canonical_url: optionalText(3000),
    posted_at: optionalText(),
    discovered_at: optionalText(),
    last_verified_at: optionalText(),
    status: z.enum(["OPEN", "CLOSED", "UNKNOWN", "STALE", "ERROR"]),
    verification_evidence: optionalText(4000),
  })
  .strict();
export const importJobSchema = z
  .object({
    title: z.string().trim().min(1, "Enter a job title.").max(300),
    company: z.string().trim().min(1, "Enter a company.").max(300),
    location: z.string().trim().max(300).nullable().optional(),
    description: z
      .string()
      .trim()
      .min(50, "Use at least 50 characters of job description.")
      .max(30000),
  })
  .strict();
export const discoverSchema = z
  .object({
    source: z.enum(["greenhouse", "lever", "ashby"]),
    board: z
      .string()
      .min(1)
      .max(100)
      .regex(/^[a-zA-Z0-9_-]+$/, "Use the board identifier, not a full URL."),
    query: z.string().max(300).default(""),
  })
  .strict();
export const applicationStatuses = [
  "DISCOVERED",
  "SHORTLISTED",
  "RESUME_READY",
  "READY_TO_APPLY",
  "APPLIED",
  "RECRUITER_RESPONSE",
  "INTERVIEW",
  "OFFER",
  "REJECTED",
  "WITHDRAWN",
] as const;
export const verificationSchema = z.enum(["PENDING", "PASSED", "FAILED"]);
export const versionSchema = z
  .object({
    id: text(100),
    target_job_id: optionalText(100),
    company: optionalText(1000),
    verification_status: verificationSchema,
    bullets: z
      .array(
        z
          .object({
            text: text(4000),
            source_fact_ids: z.array(text(100)).max(100),
            transformation_type: text(100),
            verification_status: verificationSchema,
            verifier_notes: textList,
          })
          .strict(),
      )
      .max(100),
  })
  .strict();
export const matchSchema = z
  .object({
    candidate: candidateSchema,
    job: jobSchema,
    requirement: requirementSchema,
  })
  .strict();
export const tailorSchema = z
  .object({
    candidate: candidateSchema,
    requirement: requirementSchema,
    job_id: text(100),
    company: text(1000),
    consent: z.literal(true),
  })
  .strict();
export const exportSchema = z
  .object({ candidate: candidateSchema, version: versionSchema })
  .strict();
export const applicationCreateSchema = z
  .object({ job_id: text(100).min(1) })
  .strict();
export const applicationUpdateSchema = z
  .object({ status: z.enum(applicationStatuses) })
  .strict();
export const MAX_UPLOAD_BYTES = 4 * 1024 * 1024;
