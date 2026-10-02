import type {
  Application,
  Candidate,
  Job,
  Match,
  Requirements,
  ResumeVersion,
} from "@/types";
export const candidate: Candidate = {
  name: "Synthetic Candidate",
  summary: "Backend developer.",
  experience_years: 2,
  locations: ["Remote"],
  skills: ["Python"],
  facts: [
    {
      id: "FACT-001",
      category: "skill",
      subject: "Candidate",
      predicate: "has_skill",
      value: "Python",
      source_section: "Skills",
      source_text: "Skills: Python",
      confidence: 0.9,
      verified_by_user: false,
      immutable: true,
    },
  ],
};
export const job: Job = {
  id: "job-test-1",
  source: "manual",
  external_job_id: null,
  title: "Backend Engineer",
  company: "Synthetic Company",
  location: "Remote",
  work_mode: null,
  description:
    "Build backend APIs in Python. Two years of experience required. This is a synthetic job used only for testing.",
  canonical_url: "https://example.com/careers/1",
  posted_at: null,
  discovered_at: null,
  last_verified_at: null,
  status: "UNKNOWN",
  verification_evidence: null,
};
export const requirement: Requirements = {
  role_title: "Backend Engineer",
  role_family: null,
  mandatory_skills: ["Python"],
  preferred_skills: ["Docker"],
  responsibilities: ["Build APIs"],
  education_requirements: [],
  minimum_experience: 2,
  maximum_experience: null,
  location: "Remote",
  work_mode: null,
  employment_type: null,
  domain: null,
  seniority: null,
  certifications: [],
  keywords: ["Python"],
  salary: null,
  ambiguities: ["Salary not specified"],
  confidence: 0.9,
};
export const match: Match = {
  eligible: true,
  eligibility_warnings: [],
  score: {
    required_skill_coverage: 100,
    relevant_evidence: 50,
    semantic_role_alignment: 100,
    responsibility_alignment: 50,
    experience_alignment: 100,
    preferred_skill_coverage: 0,
    location_work_mode: 100,
    total: 77.5,
  },
  evidence: [
    {
      requirement: "Python",
      candidate_fact_ids: ["FACT-001"],
      evidence: ["Skills: Python"],
      alignment: "SUPPORTED",
      confidence: 1,
    },
  ],
  gaps: [{ skill: "Docker", priority: "OPTIONAL" }],
};
export const version: ResumeVersion = {
  id: "version-test-1",
  target_job_id: job.id,
  company: job.company,
  verification_status: "PASSED",
  bullets: [
    {
      text: "Python",
      source_fact_ids: ["FACT-001"],
      transformation_type: "rephrase",
      verification_status: "PASSED",
      verifier_notes: [],
    },
  ],
};
export const application: Application = {
  id: "application-test-1",
  job_id: job.id,
  status: "DISCOVERED",
  official_url: job.canonical_url,
  notes: "",
  resume_version_id: null,
};
export const runtime = {
  mode: "live",
  public_site: true,
  retention_hours: 24,
  visitor_ai_limit: 10,
  live_discovery: true,
};
