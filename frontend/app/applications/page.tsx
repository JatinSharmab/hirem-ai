"use client";
import { useEffect, useState } from "react";
import {
  Badge,
  Button,
  Card,
  Empty,
  ErrorNotice,
  ExternalLink,
  LoadingRows,
  Notice,
  PageHeading,
} from "@/components/common/ui";
import { useWorkspace } from "@/components/layout/workspace-provider";
import { useJobs } from "@/hooks/use-jobs";
import { useTask } from "@/hooks/use-task";
import { api } from "@/lib/api/browser-client";
import { errorMessage } from "@/lib/errors";
import { applicationStatuses } from "@/lib/schemas";
import { label } from "@/lib/utils/presentation";
import type { Application, ApplicationStatus, Job } from "@/types";
function ApplicationRow({
  value,
  job,
  onChange,
}: {
  value: Application;
  job?: Job;
  onChange: (value: Application) => void;
}) {
  const { status } = useWorkspace();
  const task = useTask();
  const [selected, setSelected] = useState<ApplicationStatus>(value.status);
  return (
    <article className="application-row">
      <div>
        <div className="chips" style={{ marginBottom: 9 }}>
          <Badge value={value.status} />
        </div>
        <h3>{job?.title ?? "Job no longer in this workspace"}</h3>
        <p>
          {job?.company ?? "Company unavailable"} ·{" "}
          {job?.location || "Location not specified"}
        </p>
        <ExternalLink url={value.official_url}>
          Open official application page
        </ExternalLink>
        {value.notes && <p>Notes: {value.notes}</p>}
        {value.resume_version_id && (
          <p>
            Resume reference: <code>{value.resume_version_id}</code>
          </p>
        )}
        <ErrorNotice message={task.error} />
      </div>
      <div className="stack-small">
        <label className="field">
          Application stage
          <select
            value={selected}
            onChange={(event) =>
              setSelected(event.target.value as ApplicationStatus)
            }
            disabled={task.busy}
          >
            {applicationStatuses.map((item) => (
              <option key={item} value={item}>
                {label(item)}
              </option>
            ))}
          </select>
        </label>
        <Button
          variant="secondary"
          busy={task.busy}
          disabled={selected === value.status || status !== "ready"}
          onClick={() =>
            void task.run(async () => {
              onChange(
                await api<Application>(`applications/${value.id}`, {
                  method: "PATCH",
                  body: { status: selected },
                }),
              );
            })
          }
        >
          Save stage
        </Button>
      </div>
    </article>
  );
}
export default function ApplicationsPage() {
  const { status, applicationsRevision } = useWorkspace();
  const data = useJobs();
  const [records, setRecords] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  const [filter, setFilter] = useState("");
  useEffect(() => {
    if (status !== "ready") return;
    const controller = new AbortController();
    void api<Application[]>("applications", { signal: controller.signal })
      .then(setRecords)
      .catch((error) => {
        if (!controller.signal.aborted) setError(errorMessage(error));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [status, revision, applicationsRevision]);
  const visible = records.filter((item) => !filter || item.status === filter);
  return (
    <>
      <PageHeading
        eyebrow="05 / TRACK YOUR PROGRESS"
        title="Every application has a next step."
      >
        Keep a simple record of your progress, from a promising role to your
        final decision.
      </PageHeading>
      <Notice>
        Tracking never submits an application. Open the official posting and
        apply yourself. Records are temporary; save your important information
        elsewhere.
      </Notice>
      <div className="stat-grid">
        <div className="stat">
          <span>Tracked roles</span>
          <strong>{records.length}</strong>
        </div>
        <div className="stat">
          <span>Applied</span>
          <strong>
            {records.filter((item) => item.status === "APPLIED").length}
          </strong>
        </div>
        <div className="stat">
          <span>Interviews</span>
          <strong>
            {records.filter((item) => item.status === "INTERVIEW").length}
          </strong>
        </div>
      </div>
      <div className="toolbar">
        <label className="field">
          Filter by stage
          <select
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
          >
            <option value="">All stages</option>
            {applicationStatuses.map((item) => (
              <option key={item} value={item}>
                {label(item)}
              </option>
            ))}
          </select>
        </label>
        <Button
          variant="secondary"
          disabled={status !== "ready" || loading}
          onClick={() => {
            setLoading(true);
            setError(null);
            setRevision((value) => value + 1);
          }}
        >
          Refresh applications
        </Button>
      </div>
      <ErrorNotice message={error ?? data.error} />
      {loading ? (
        <LoadingRows />
      ) : visible.length ? (
        <Card title="Your application tracker">
          {visible.map((item) => (
            <ApplicationRow
              key={item.id}
              value={item}
              job={data.jobs.find((job) => job.id === item.job_id)}
              onChange={(value) =>
                setRecords((previous) =>
                  previous.map((record) =>
                    record.id === value.id ? value : record,
                  ),
                )
              }
            />
          ))}
        </Card>
      ) : (
        <Empty
          title={
            records.length
              ? "No applications in this stage"
              : "Give your search some structure"
          }
          href="/jobs"
          action="Explore jobs"
        >
          Choose “Track application” on a job to save it here. Update the stage
          as you make progress.
        </Empty>
      )}
    </>
  );
}
