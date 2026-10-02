"use client";
import { useState, type FormEvent } from "react";
import {
  Button,
  Card,
  Empty,
  ErrorNotice,
  LoadingRows,
  Notice,
  PageHeading,
} from "@/components/common/ui";
import { JobCard } from "@/components/jobs/job-card";
import { useWorkspace } from "@/components/layout/workspace-provider";
import { useJobs } from "@/hooks/use-jobs";
import { useTask } from "@/hooks/use-task";
import { api } from "@/lib/api/browser-client";
import { discoverSchema, importJobSchema } from "@/lib/schemas";
import { ApiError } from "@/lib/errors";
import type { Job } from "@/types";
export default function JobsPage() {
  const workspace = useWorkspace();
  const data = useJobs();
  const importer = useTask();
  const discovery = useTask();
  const [query, setQuery] = useState("");
  const [location, setLocation] = useState("");
  const [savedOnly, setSavedOnly] = useState(false);
  const [discoveryCount, setDiscoveryCount] = useState<number | null>(null);
  async function importJob(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const input = Object.fromEntries(new FormData(form));
    await importer.run(async () => {
      const parsed = importJobSchema.safeParse(input);
      if (!parsed.success)
        throw new ApiError(422, parsed.error.issues[0].message, "VALIDATION");
      const job = await api<Job>("jobs/import", {
        method: "POST",
        body: parsed.data,
      });
      workspace.setJobs([
        job,
        ...workspace.jobs.filter((value) => value.id !== job.id),
      ]);
      workspace.selectJob(job.id);
      form.reset();
    });
  }
  async function discover(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const input = Object.fromEntries(new FormData(event.currentTarget));
    await discovery.run(async () => {
      const parsed = discoverSchema.safeParse(input);
      if (!parsed.success)
        throw new ApiError(422, parsed.error.issues[0].message, "VALIDATION");
      const jobs = await api<Job[]>("jobs/discover", {
        method: "POST",
        body: parsed.data,
      });
      workspace.setJobs([
        ...jobs,
        ...workspace.jobs.filter(
          (value) => !jobs.some((job) => job.id === value.id),
        ),
      ]);
      setDiscoveryCount(jobs.length);
    });
  }
  const visible = data.jobs.filter(
    (job) =>
      `${job.title} ${job.company}`
        .toLowerCase()
        .includes(query.toLowerCase()) &&
      (job.location ?? "").toLowerCase().includes(location.toLowerCase()) &&
      (!savedOnly || workspace.bookmarks.includes(job.id)),
  );
  return (
    <>
      <PageHeading
        eyebrow="02 / DISCOVER"
        title="Find a role worth your evidence."
      >
        Bring a job description or connect to a company’s public ATS board.
        Every job stays connected to its source.
      </PageHeading>
      <div className="grid-two">
        <Card title="Import a job description">
          <form onSubmit={importJob} className="stack-small">
            <div className="form-grid">
              <label className="field">
                Job title
                <input
                  name="title"
                  required
                  maxLength={300}
                  placeholder="Backend Engineer"
                />
              </label>
              <label className="field">
                Company
                <input
                  name="company"
                  required
                  maxLength={300}
                  placeholder="Company name"
                />
              </label>
              <label className="field full">
                Location · optional
                <input
                  name="location"
                  maxLength={300}
                  placeholder="City or remote location from the posting"
                />
              </label>
              <label className="field full">
                Job description
                <textarea
                  name="description"
                  required
                  minLength={50}
                  maxLength={30000}
                  placeholder="Paste the original job description, including requirements and responsibilities."
                />
                <small>
                  50–30,000 characters. Analysis is a separate action.
                </small>
              </label>
            </div>
            <Button
              type="submit"
              busy={importer.busy}
              disabled={workspace.status !== "ready"}
            >
              Import job
            </Button>
            <ErrorNotice message={importer.error} />
          </form>
        </Card>
        <Card title="Discover from a company board">
          <form onSubmit={discover} className="stack-small">
            <label className="field">
              ATS source
              <select name="source">
                <option value="greenhouse">Greenhouse</option>
                <option value="lever">Lever</option>
                <option value="ashby">Ashby</option>
              </select>
            </label>
            <label className="field">
              Company / board identifier
              <input
                name="board"
                required
                maxLength={100}
                pattern="[a-zA-Z0-9_-]+"
                placeholder="Board identifier from its careers URL"
              />
              <small>Use the identifier, not the full URL.</small>
            </label>
            <label className="field">
              Search query · optional
              <input name="query" maxLength={300} placeholder="e.g. engineer" />
            </label>
            <Button
              type="submit"
              busy={discovery.busy}
              disabled={
                workspace.status !== "ready" ||
                workspace.settings?.live_discovery === false
              }
            >
              Discover jobs
            </Button>
            <ErrorNotice message={discovery.error} />
          </form>
          {discoveryCount !== null && (
            <Notice>
              {discoveryCount
                ? `${discoveryCount} jobs returned from this board.`
                : "No matching jobs were returned. Check the identifier or try a broader query."}
            </Notice>
          )}
          <div className="prose">
            <p>
              Up to 20 jobs per request. This searches one company board, not
              the entire internet.
            </p>
            <p>
              Greenhouse uses the token after boards.greenhouse.io/; Lever uses
              the name after jobs.lever.co/; Ashby uses the name after
              jobs.ashbyhq.com/.
            </p>
          </div>
        </Card>
      </div>
      <section className="section-block">
        <div className="section-heading">
          <div>
            <p className="eyebrow">YOUR TEMPORARY WORKSPACE</p>
            <h2>Jobs, with context.</h2>
          </div>
          <Button
            variant="secondary"
            onClick={data.reload}
            disabled={workspace.status !== "ready" || data.loading}
          >
            Refresh jobs
          </Button>
        </div>
        <div className="toolbar">
          <label className="field">
            Search jobs
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Title or company"
            />
          </label>
          <label className="field">
            Filter location
            <input
              value={location}
              onChange={(event) => setLocation(event.target.value)}
              placeholder="Any location"
            />
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={savedOnly}
              onChange={(event) => setSavedOnly(event.target.checked)}
            />
            Bookmarked in this tab
          </label>
        </div>
        <ErrorNotice message={data.error} />
        {data.loading && !data.jobs.length ? (
          <LoadingRows />
        ) : visible.length ? (
          <div className="job-grid">
            {visible.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        ) : (
          <Empty
            title={
              data.jobs.length
                ? "No jobs match these filters"
                : "Your next role starts here"
            }
          >
            {data.jobs.length
              ? "Try another title, company or location."
              : "Import a job above or discover a company board. Your results will appear here once the backend is ready."}
          </Empty>
        )}
      </section>
    </>
  );
}
