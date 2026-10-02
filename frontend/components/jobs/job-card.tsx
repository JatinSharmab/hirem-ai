"use client";
import Link from "next/link";
import { Bookmark } from "lucide-react";
import { Badge, Button, ErrorNotice } from "@/components/common/ui";
import { useWorkspace } from "@/components/layout/workspace-provider";
import { useTask } from "@/hooks/use-task";
import { api } from "@/lib/api/browser-client";
import type { Job } from "@/types";
import { useState } from "react";
export function JobCard({ job }: { job: Job }) {
  const workspace = useWorkspace();
  const task = useTask();
  const [tracked, setTracked] = useState(false);
  const saved = workspace.bookmarks.includes(job.id);
  return (
    <article className="card job-card">
      <div className="row-between">
        <div className="chips">
          <Badge value={job.source} />
          <Badge value={job.status} />
        </div>
        <button
          className={`icon-button ${saved ? "selected" : ""}`}
          aria-label={`${saved ? "Remove bookmark for" : "Bookmark"} ${job.title}`}
          aria-pressed={saved}
          onClick={() => workspace.toggleBookmark(job.id)}
        >
          <Bookmark size={17} fill={saved ? "currentColor" : "none"} />
        </button>
      </div>
      <h3>
        <Link href={`/jobs/${job.id}`}>{job.title}</Link>
      </h3>
      <p className="job-meta">
        {job.company} · {job.location || "Location not specified"}
      </p>
      {job.status === "UNKNOWN" && (
        <p className="small muted">
          Open status has not been independently verified.
        </p>
      )}
      <div className="actions">
        <Link className="button primary" href={`/jobs/${job.id}`}>
          View & analyze
        </Link>
        <Link
          className="button secondary"
          href="/match"
          onClick={() => workspace.selectJob(job.id)}
        >
          Match
        </Link>
        <Link
          className="button secondary"
          href="/resume"
          onClick={() => workspace.selectJob(job.id)}
        >
          Resume
        </Link>
        <Button
          variant="secondary"
          disabled={workspace.status !== "ready" || tracked}
          busy={task.busy}
          onClick={() =>
            void task.run(async () => {
              await api("applications", {
                method: "POST",
                body: { job_id: job.id },
              });
              setTracked(true);
              workspace.applicationsChanged();
            })
          }
        >
          {tracked ? "Tracked" : "Track application"}
        </Button>
      </div>
      <ErrorNotice message={task.error} />
    </article>
  );
}
