import type { components } from "./backend";

type Models = components["schemas"];
export type Fact = Required<Models["CandidateFact"]>;
export type Candidate = Omit<Required<Models["CandidateProfile"]>, "facts"> & {
  facts: Fact[];
};
export type Job = Required<Models["JobRecord"]>;
export type Requirements = Required<Models["JobRequirement"]>;
export type Score = Required<Models["ScoreBreakdown"]>;
export type Evidence = Required<Models["EvidenceMatch"]>;
export type Match = Omit<
  Required<Models["MatchResult"]>,
  "score" | "evidence"
> & { score: Score; evidence: Evidence[] };
export type Bullet = Required<Models["GeneratedResumeBullet"]>;
export type ResumeVersion = Omit<
  Required<Models["ResumeVersion"]>,
  "bullets"
> & { bullets: Bullet[] };
export type Application = Required<Models["ApplicationRecord"]>;
export type ApplicationStatus = Models["ApplicationStatus"];
export type SavedVersion = {
  version: ResumeVersion;
  candidate: Candidate;
  createdAt: string;
};
export type RuntimeSettings = {
  mode: "demo" | "live";
  public_site: boolean;
  retention_hours: number;
  visitor_ai_limit: number;
  live_discovery: boolean;
};
export type SkillInsights = {
  source: string;
  skills: { skill: string; job_count: number }[];
};
export type BackendState = "checking" | "waking" | "ready" | "error";
