"use client";
import { use, useEffect, useState } from "react";
import {
  ActionLink,
  Badge,
  Button,
  Card,
  ErrorNotice,
  ExternalLink,
  LoadingRows,
  Notice,
  PageHeading,
} from "@/components/common/ui";
import { RequirementsView } from "@/components/jobs/requirements";
import { useWorkspace } from "@/components/layout/workspace-provider";
import { api } from "@/lib/api/browser-client";
import { ApiError, errorMessage } from "@/lib/errors";
import { useTask } from "@/hooks/use-task";
import type { Job, Requirements } from "@/types";
export default function JobDetails({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const workspace = useWorkspace();
  const [job, setJob] = useState<Job | null>(
    workspace.jobs.find((value) => value.id === id) ?? null,
  );
  const [error, setError] = useState<string | null>(null);
  const [tracked, setTracked] = useState(false);
  const task = useTask();
  const trackTask = useTask();
  const requirement = workspace.requirements[id];
  // Only fetch cached data on entry. Gemini is called by the Analyze button.
  useEffect(() => {
    if (workspace.status !== "ready") return;
    let active = true;
    void api<Job>(`jobs/${id}`)
      .then((value) => {
        if (active) setJob(value);
      })
      .catch((error) => {
        if (active) setError(errorMessage(error));
      });
    void api<Requirements>(`jobs/${id}/requirements`)
      .then((value) => {
        if (active) workspace.rememberRequirements(id, value);
      })
      .catch((error) => {
        if (
          active &&
          !(error instanceof ApiError && [404, 409].includes(error.status))
        )
          setError(errorMessage(error));
      });
    return () => {
      active = false;
    };
    // Context callbacks change when state changes; only status/id should trigger reads.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, workspace.status]);
  return (
    <>
      <PageHeading
        eyebrow="JOB / SOURCE & REQUIREMENTS"
        title={job?.title ?? "Job details"}
      >
        {job
          ? `${job.company} · ${job.location || "Location not specified"}`
          : "Your saved job and its structured requirements."}
      </PageHeading>
      <ErrorNotice message={error} />
      {!job ? (
        !error && <LoadingRows />
      ) : (
        <div className="stack">
          <Card>
            <div className="row-between">
              <div className="chips">
                <Badge value={job.source} />
                <Badge value={job.status} />
              </div>
              <ExternalLink url={job.canonical_url}>
                View official posting
              </ExternalLink>
            </div>
            {job.status === "UNKNOWN" && (
              <Notice>
                Open status has not been independently verified. Confirm
                availability on the official posting before applying.
              </Notice>
            )}
            <div className="actions">
              <Button
                busy={task.busy}
                disabled={workspace.status !== "ready"}
                onClick={() =>
                  void task.run(async () => {
                    const result = await api<Requirements>(
                      `jobs/${id}/analyze`,
                      { method: "POST" },
                    );
                    workspace.rememberRequirements(id, result);
                    workspace.selectJob(id);
                  })
                }
              >
                {requirement
                  ? "Load analyzed requirements"
                  : "Analyze requirements with Gemini"}
              </Button>
              <span onClick={() => workspace.selectJob(id)}>
                <ActionLink href="/match" secondary>
                  Match my profile
                </ActionLink>
              </span>
              <span onClick={() => workspace.selectJob(id)}>
                <ActionLink href="/resume" secondary>
                  Tailor resume
                </ActionLink>
              </span>
              <Button
                variant="secondary"
                disabled={workspace.status !== "ready" || tracked}
                busy={trackTask.busy}
                onClick={() =>
                  void trackTask.run(async () => {
                    await api("applications", {
                      method: "POST",
                      body: { job_id: id },
                    });
                    setTracked(true);
                    workspace.applicationsChanged();
                  })
                }
              >
                {tracked ? "Tracked in applications" : "Track application"}
              </Button>
            </div>
            <ErrorNotice message={task.error ?? trackTask.error} />
            <p className="small muted" style={{ marginTop: 12 }}>
              Analysis uses Gemini only when no cached result exists. Viewing a
              job never starts AI analysis.
            </p>
          </Card>
          <div className="grid-two">
            <Card title="Original job description">
              <div className="description">{job.description}</div>
            </Card>
            {requirement ? (
              <RequirementsView value={requirement} />
            ) : (
              <Card title="See the requirements clearly">
                <p className="muted small">
                  Run analysis to extract mandatory and preferred skills,
                  experience, responsibilities and unknowns. This uses your AI
                  allowance.
                </p>
              </Card>
            )}
          </div>
        </div>
      )}
    </>
  );
}
