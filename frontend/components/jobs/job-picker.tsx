"use client";
import { useEffect } from "react";
import Link from "next/link";
import { useWorkspace } from "@/components/layout/workspace-provider";
import { useJobs } from "@/hooks/use-jobs";
import { Button, ErrorNotice, Notice } from "@/components/common/ui";
import { useTask } from "@/hooks/use-task";
import { api } from "@/lib/api/browser-client";
import { ApiError } from "@/lib/errors";
import type { Requirements } from "@/types";
export function JobPicker() {
  const workspace = useWorkspace();
  const data = useJobs();
  const task = useTask();
  const id = workspace.selectedJob;
  useEffect(() => {
    if (!id || workspace.status !== "ready" || workspace.requirements[id])
      return;
    let active = true;
    void api<Requirements>(`jobs/${id}/requirements`)
      .then((value) => {
        if (active) workspace.rememberRequirements(id, value);
      })
      .catch((error) => {
        if (!(error instanceof ApiError && [404, 409].includes(error.status))) {
          /* Explicit analyze offers the recoverable error state. */
        }
      });
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, workspace.status]);
  return (
    <div className="stack-small">
      <label className="field">
        Target job
        <select
          value={id}
          onChange={(event) => workspace.selectJob(event.target.value)}
        >
          <option value="">Select a saved job</option>
          {data.jobs.map((job) => (
            <option value={job.id} key={job.id}>
              {job.title} · {job.company}
            </option>
          ))}
        </select>
      </label>
      <ErrorNotice message={data.error ?? task.error} />
      {!data.jobs.length && (
        <p className="small muted">
          Import a role on the{" "}
          <Link className="text-link" href="/jobs">
            Jobs page
          </Link>{" "}
          to start.
        </p>
      )}
      {id && !workspace.requirements[id] && (
        <>
          <Notice>
            This job needs structured requirements before matching or tailoring.
          </Notice>
          <Button
            busy={task.busy}
            disabled={workspace.status !== "ready"}
            onClick={() =>
              void task.run(async () => {
                workspace.rememberRequirements(
                  id,
                  await api<Requirements>(`jobs/${id}/analyze`, {
                    method: "POST",
                  }),
                );
              })
            }
          >
            Analyze job with Gemini
          </Button>
        </>
      )}
      {id && workspace.requirements[id] && (
        <p className="small muted">
          Structured requirements ready.{" "}
          <Link className="text-link" href={`/jobs/${id}`}>
            Inspect analysis
          </Link>
        </p>
      )}
    </div>
  );
}
