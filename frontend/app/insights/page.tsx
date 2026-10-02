"use client";
import { useEffect, useState } from "react";
import {
  Button,
  Card,
  Empty,
  ErrorNotice,
  LoadingRows,
  Notice,
  PageHeading,
} from "@/components/common/ui";
import { useWorkspace } from "@/components/layout/workspace-provider";
import { useJobs } from "@/hooks/use-jobs";
import { api } from "@/lib/api/browser-client";
import { errorMessage } from "@/lib/errors";
import type { SkillInsights } from "@/types";
export default function InsightsPage() {
  const { status } = useWorkspace();
  const data = useJobs();
  const [insights, setInsights] = useState<SkillInsights | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    if (status !== "ready") return;
    const controller = new AbortController();
    void api<SkillInsights>("insights/skills", { signal: controller.signal })
      .then(setInsights)
      .catch((error) => {
        if (!controller.signal.aborted) setError(errorMessage(error));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [status, revision]);
  const maximum = Math.max(
    1,
    ...(insights?.skills.map((item) => item.job_count) ?? []),
  );
  const sources = Object.entries(
    data.jobs.reduce<Record<string, number>>(
      (counts, job) => ({
        ...counts,
        [job.source]: (counts[job.source] ?? 0) + 1,
      }),
      {},
    ),
  );
  return (
    <>
      <PageHeading
        eyebrow="06 / WORKSPACE INSIGHTS"
        title="See patterns in your saved roles."
      >
        Skill frequencies from your imported job descriptions, with a clear view
        of the sample behind them.
      </PageHeading>
      <Notice>
        These are keyword counts within this workspace, not a market-wide trend
        or labor-market forecast. No Gemini call is made for this view.
        {insights?.source === "demo" &&
          " The backend is in demo mode; these counts are demo data."}
      </Notice>
      <div className="section-heading">
        <div>
          <h2>{data.jobs.length} saved jobs</h2>
          <p className="small muted">
            Source counts are calculated from the jobs returned by your backend.
          </p>
        </div>
        <Button
          variant="secondary"
          disabled={status !== "ready" || loading}
          onClick={() => {
            setLoading(true);
            setError(null);
            setRevision((value) => value + 1);
            data.reload();
          }}
        >
          Refresh insights
        </Button>
      </div>
      <ErrorNotice message={error ?? data.error} />
      {loading ? (
        <LoadingRows />
      ) : !insights?.skills.length ? (
        <Empty
          title="Build your sample first"
          href="/jobs"
          action="Import a job"
        >
          Save some roles to see which recognized skills occur in their
          descriptions.
        </Empty>
      ) : (
        <div className="grid-two">
          <Card title="Recognized skill frequency">
            {insights.skills.map((item) => (
              <div key={item.skill} className="factor">
                <div className="row-between">
                  <strong>{item.skill}</strong>
                  <span>
                    {item.job_count} {item.job_count === 1 ? "job" : "jobs"}
                  </span>
                </div>
                <div className="bar">
                  <span
                    style={{ width: `${(item.job_count / maximum) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </Card>
          <Card title="Where your sample comes from">
            {sources.map(([source, count]) => (
              <div className="evidence-item row-between" key={source}>
                <strong className="small">{source}</strong>
                <span className="badge">{count} jobs</span>
              </div>
            ))}
            <div className="prose">
              <p>
                Small samples are easy to misread. A frequently mentioned skill
                here may reflect one company or the roles you chose to import.
              </p>
              <p>
                Use the job’s original description and your match evidence
                before deciding what to learn next.
              </p>
            </div>
          </Card>
        </div>
      )}
    </>
  );
}
