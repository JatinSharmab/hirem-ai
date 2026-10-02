"use client";
import { useState } from "react";
import {
  Badge,
  Button,
  Card,
  Empty,
  ErrorNotice,
  Notice,
  PageHeading,
} from "@/components/common/ui";
import { JobPicker } from "@/components/jobs/job-picker";
import { useWorkspace } from "@/components/layout/workspace-provider";
import { useTask } from "@/hooks/use-task";
import { api, saveDownload } from "@/lib/api/browser-client";
import type { ResumeVersion } from "@/types";
export default function ResumePage() {
  const workspace = useWorkspace();
  const task = useTask();
  const download = useTask();
  const [consent, setConsent] = useState(false);
  const [approved, setApproved] = useState(false);
  const [activeId, setActiveId] = useState<string | null>(null);
  const { candidate } = workspace;
  const job = workspace.jobs.find((item) => item.id === workspace.selectedJob);
  const requirement = workspace.requirements[workspace.selectedJob];
  const reviewed =
    candidate?.facts.filter((fact) => fact.verified_by_user).length ?? 0;
  const active =
    workspace.versions.find((item) => item.version.id === activeId) ??
    workspace.versions[0];
  const version = active?.version;
  const passed =
    version?.verification_status === "PASSED" &&
    version.bullets.length > 0 &&
    version.bullets.every((bullet) => bullet.verification_status === "PASSED");
  function exportResume(format: "pdf" | "docx") {
    if (!active || !approved || !passed) return;
    void download.run(async () => {
      const blob = await api<Blob>(`resumes/export/${format}`, {
        method: "POST",
        body: { candidate: active.candidate, version: active.version },
        download: true,
      });
      saveDownload(blob, `hireme-resume-extract.${format}`);
    });
  }
  return (
    <>
      <PageHeading
        eyebrow="04 / TAILOR & VERIFY"
        title="Relevant experience. Traceable claims."
      >
        Build a job-specific resume extract from reviewed facts. Every bullet
        retains its evidence and verification result.
      </PageHeading>
      {!candidate ? (
        <Empty
          title="Your resume starts with reviewed evidence"
          href="/profile"
          action="Build my profile"
        >
          Upload and review your profile before selecting facts for a target
          job.
        </Empty>
      ) : (
        <div className="stack">
          <Card title="Choose your target role">
            <JobPicker />
            <Notice>
              {reviewed} reviewed facts available. Gemini selects up to 15 fact
              IDs. Python constructs and verifies the bullets; this is a resume
              extract, not a complete redesigned resume.
            </Notice>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={consent}
                onChange={(event) => setConsent(event.target.checked)}
              />
              I agree to send my reviewed evidence and this job’s requirements
              to Gemini for fact selection.
            </label>
            <div className="actions">
              <Button
                busy={task.busy}
                disabled={
                  !job ||
                  !requirement ||
                  !reviewed ||
                  !consent ||
                  workspace.status !== "ready"
                }
                onClick={() =>
                  void task.run(async () => {
                    const snapshot = structuredClone(candidate);
                    const result = await api<ResumeVersion>("resumes/tailor", {
                      method: "POST",
                      body: {
                        candidate: snapshot,
                        requirement,
                        job_id: job?.id,
                        company: job?.company,
                        consent: true,
                      },
                    });
                    workspace.addVersion({
                      version: result,
                      candidate: snapshot,
                      createdAt: new Date().toISOString(),
                    });
                    setActiveId(result.id);
                    setApproved(false);
                  })
                }
              >
                {task.busy
                  ? "Selecting and verifying evidence…"
                  : "Create verified resume extract"}
              </Button>
            </div>
            <ErrorNotice message={task.error} />
          </Card>
          {active && version && (
            <div className="grid-main">
              <div className="stack">
                <div className="resume-paper">
                  <div className="row-between">
                    <p className="eyebrow">RESUME EXTRACT</p>
                    <Badge value={version.verification_status} />
                  </div>
                  <h2 style={{ marginTop: 20 }}>{active.candidate.name}</h2>
                  <p className="small muted">
                    Prepared for {version.company || "your target role"}
                  </p>
                  <hr />
                  <ul>
                    {version.bullets.map((bullet, index) => (
                      <li key={index}>
                        <p>{bullet.text}</p>
                        <div className="row-between" style={{ marginTop: 8 }}>
                          <code>
                            {bullet.source_fact_ids.join(" · ") ||
                              "No source fact IDs"}
                          </code>
                          <Badge value={bullet.verification_status} />
                        </div>
                        <details>
                          <summary>Inspect provenance & verification</summary>
                          <p className="small muted">
                            Transformation: {bullet.transformation_type}
                          </p>
                          {bullet.source_fact_ids.map((id) => {
                            const fact = active.candidate.facts.find(
                              (item) => item.id === id,
                            );
                            return (
                              <blockquote className="source-quote" key={id}>
                                <strong>{id}</strong> ·{" "}
                                {fact?.value ?? "Source fact unavailable"}
                                <br />
                                {fact?.source_text ?? "No source excerpt"}
                              </blockquote>
                            );
                          })}
                          <p className="small muted">
                            {bullet.verifier_notes.length
                              ? bullet.verifier_notes.join(" · ")
                              : "No additional verifier notes."}
                          </p>
                        </details>
                      </li>
                    ))}
                  </ul>
                  {!version.bullets.length && (
                    <Notice>
                      No bullets were returned. Export is unavailable.
                    </Notice>
                  )}
                </div>
                <Card title="Review before downloading">
                  <Notice>
                    Verification checks support and provenance. It does not
                    prove that your original resume or reviewed facts are true.
                    You remain responsible for the final content.
                  </Notice>
                  <label className="checkbox">
                    <input
                      type="checkbox"
                      checked={approved}
                      disabled={!passed}
                      onChange={(event) => setApproved(event.target.checked)}
                    />
                    I reviewed this extract and approve these claims for export.
                  </label>
                  {!passed && (
                    <ErrorNotice message="This version did not pass every verification check. It cannot be exported." />
                  )}
                  <div className="actions">
                    <Button
                      disabled={
                        !passed || !approved || workspace.status !== "ready"
                      }
                      busy={download.busy}
                      onClick={() => exportResume("pdf")}
                    >
                      Download PDF
                    </Button>
                    <Button
                      variant="secondary"
                      disabled={
                        !passed || !approved || workspace.status !== "ready"
                      }
                      busy={download.busy}
                      onClick={() => exportResume("docx")}
                    >
                      Download DOCX
                    </Button>
                  </div>
                  <ErrorNotice message={download.error} />
                </Card>
              </div>
              <Card title="Versions in this tab">
                <p className="small muted" style={{ marginBottom: 18 }}>
                  Versions keep the candidate facts used when they were created.
                  Reloading clears this local history.
                </p>
                <div className="stack-small">
                  {workspace.versions.map((item, index) => (
                    <button
                      className={`version-option ${item.version.id === version.id ? "active" : ""}`}
                      key={item.version.id}
                      onClick={() => {
                        setActiveId(item.version.id);
                        setApproved(false);
                      }}
                    >
                      <strong>
                        {item.version.company || "Resume extract"}
                      </strong>
                      <small>
                        Version {workspace.versions.length - index} ·{" "}
                        {new Date(item.createdAt).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </small>
                      <br />
                      <Badge value={item.version.verification_status} />
                    </button>
                  ))}
                </div>
              </Card>
            </div>
          )}
        </div>
      )}
    </>
  );
}
