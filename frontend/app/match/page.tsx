"use client";
import {
  Button,
  Card,
  Chips,
  Empty,
  ErrorNotice,
  Notice,
  PageHeading,
} from "@/components/common/ui";
import { JobPicker } from "@/components/jobs/job-picker";
import { ScoreBreakdown } from "@/components/matching/score-breakdown";
import { useWorkspace } from "@/components/layout/workspace-provider";
import { useTask } from "@/hooks/use-task";
import { api } from "@/lib/api/browser-client";
import type { Match } from "@/types";
export default function MatchPage() {
  const workspace = useWorkspace();
  const task = useTask();
  const { candidate, match } = workspace;
  const job = workspace.jobs.find(
    (value) => value.id === workspace.selectedJob,
  );
  const requirement = workspace.requirements[workspace.selectedJob];
  const reviewed =
    candidate?.facts.filter((fact) => fact.verified_by_user).length ?? 0;
  return (
    <>
      <PageHeading
        eyebrow="03 / UNDERSTAND YOUR FIT"
        title="See the evidence behind the match."
      >
        Compare reviewed facts with the role’s requirements. Understand the
        strengths, gaps, and limits of the score.
      </PageHeading>
      {!candidate ? (
        <Empty
          title="Start with your evidence"
          href="/profile"
          action="Build my profile"
        >
          Upload your resume and review the extracted facts before matching a
          role.
        </Empty>
      ) : (
        <div className="stack">
          <Card title="Choose your comparison">
            <JobPicker />
            <Notice>
              {reviewed} of {candidate.facts.length} facts reviewed. Skill
              matching uses reviewed skill facts. Changes to your profile or
              target job clear the previous result.
            </Notice>
            <Button
              disabled={
                !job ||
                !requirement ||
                !reviewed ||
                workspace.status !== "ready"
              }
              busy={task.busy}
              onClick={() =>
                void task.run(async () => {
                  workspace.setMatch(
                    await api<Match>("matches", {
                      method: "POST",
                      body: { candidate, job, requirement },
                    }),
                  );
                })
              }
            >
              Calculate Career Fit Score
            </Button>
            <ErrorNotice message={task.error} />
          </Card>
          {match && (
            <div className="grid-main">
              <ScoreBreakdown score={match.score} />
              <div className="stack">
                <Card title="Eligibility & unknowns">
                  <p className="small">
                    {match.eligible
                      ? "Backend eligibility checks passed."
                      : "Some backend eligibility checks did not pass."}
                  </p>
                  <Notice>
                    A score is still shown when eligibility checks fail. It does
                    not override the warnings below.
                  </Notice>
                  <Chips
                    values={match.eligibility_warnings}
                    empty="No eligibility warnings returned."
                  />
                  <h3 style={{ fontSize: 16, margin: "22px 0 12px" }}>
                    Unknowns in the posting
                  </h3>
                  <Chips
                    values={requirement?.ambiguities ?? []}
                    empty="No ambiguities returned. Missing fields still mean not specified."
                  />
                </Card>
                <Card title="Skill gaps">
                  <h3 style={{ fontSize: 16, marginBottom: 12 }}>
                    Missing mandatory skills
                  </h3>
                  <Chips
                    values={match.gaps
                      .filter((gap) => gap.priority === "CRITICAL")
                      .map((gap) => gap.skill)}
                    empty="No mandatory skill gaps returned."
                  />
                  <h3 style={{ fontSize: 16, margin: "22px 0 12px" }}>
                    Missing preferred skills
                  </h3>
                  <Chips
                    values={match.gaps
                      .filter((gap) => gap.priority === "OPTIONAL")
                      .map((gap) => gap.skill)}
                    empty="No preferred skill gaps returned."
                  />
                </Card>
              </div>
              <Card title="Requirement-to-evidence map" className="full">
                <p className="small muted">
                  Strong matches link directly to reviewed candidate facts.
                  Missing evidence is not filled in by the frontend.
                </p>
                {match.evidence.map((item, index) => (
                  <article
                    className="evidence-item"
                    key={`${item.requirement}-${index}`}
                  >
                    <div className="row-between">
                      <h3>{item.requirement}</h3>
                      <span className="badge">{item.alignment}</span>
                    </div>
                    <p>
                      {item.evidence.length
                        ? item.evidence.join(" · ")
                        : "No reviewed evidence returned."}
                    </p>
                    <Chips
                      values={item.candidate_fact_ids}
                      empty="No supporting fact IDs"
                    />
                  </article>
                ))}
                {!match.evidence.length && (
                  <Notice>No requirement evidence was returned.</Notice>
                )}
              </Card>
            </div>
          )}
        </div>
      )}
    </>
  );
}
