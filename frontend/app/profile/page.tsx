"use client";
import Link from "next/link";
import { useState, type FormEvent } from "react";
import { Upload } from "lucide-react";
import {
  ActionLink,
  Button,
  Card,
  Chips,
  ErrorNotice,
  Notice,
  PageHeading,
} from "@/components/common/ui";
import { FactLedger } from "@/components/profile/fact-ledger";
import { useWorkspace } from "@/components/layout/workspace-provider";
import { useTask } from "@/hooks/use-task";
import { api } from "@/lib/api/browser-client";
import { MAX_UPLOAD_BYTES } from "@/lib/schemas";
import type { Candidate } from "@/types";
export default function ProfilePage() {
  const workspace = useWorkspace();
  const task = useTask();
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);
  const candidate = workspace.candidate;
  function submit(event: FormEvent) {
    event.preventDefault();
    if (!file || !consent) return;
    void task.run(async () => {
      const body = new FormData();
      body.append("file", file);
      body.append("consent", "true");
      const profile = await api<Candidate>("profile/parse", {
        method: "POST",
        body,
      });
      workspace.setCandidate(profile);
    });
  }
  return (
    <>
      <PageHeading
        eyebrow="01 / YOUR EVIDENCE"
        title="A profile grounded in you."
      >
        Extract your experience, inspect the source, and decide what becomes
        reviewed evidence.
      </PageHeading>
      <div className="grid-main">
        <Card title="Bring your own resume">
          <form onSubmit={submit} className="stack-small">
            <label className="upload-box">
              <Upload size={27} />
              <strong>Choose a PDF or DOCX resume</strong>
              <p>Up to 4 MB · Text-based PDF · Maximum 50 pages</p>
              <input
                aria-label="Resume file"
                type="file"
                accept=".pdf,.docx"
                disabled={task.busy}
                onChange={(event) => {
                  const picked = event.target.files?.[0] ?? null;
                  const error =
                    picked &&
                    (!/\.(pdf|docx)$/i.test(picked.name)
                      ? "Choose a PDF or DOCX file."
                      : picked.size > MAX_UPLOAD_BYTES
                        ? "Choose a file smaller than 4 MB."
                        : picked.size === 0
                          ? "This file is empty."
                          : null);
                  setFileError(error);
                  setFile(error ? null : picked);
                }}
              />
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={consent}
                onChange={(event) => setConsent(event.target.checked)}
              />
              I agree to send this resume text to the configured Google Gemini
              provider for profile extraction.
            </label>
            <Button
              type="submit"
              busy={task.busy}
              disabled={!file || !consent || workspace.status !== "ready"}
            >
              {task.busy
                ? "Reading and extracting your evidence…"
                : candidate
                  ? "Extract a replacement profile"
                  : "Extract my profile"}
            </Button>
            <ErrorNotice message={fileError ?? task.error} />
          </form>
          {candidate && (
            <p className="small muted" style={{ marginTop: 12 }}>
              A new upload replaces your current profile and match. Earlier
              resume versions keep their original evidence snapshot.
            </p>
          )}
        </Card>
        <Card title="You are the final reviewer">
          <div className="prose">
            <p>
              Resume text may be processed by the configured Gemini provider
              after your consent.
            </p>
            <p>
              Use a resume without confidential details. Scanned PDFs need OCR
              first; HireMe AI reads embedded text.
            </p>
            <p>
              Your profile and resume versions stay in this browser tab’s
              memory. A reload clears them. Imported jobs and application
              records use a temporary workspace.
            </p>
          </div>
          <Link className="text-link" href="/privacy">
            Read how your data is handled
          </Link>
        </Card>
      </div>
      {candidate && (
        <div className="stack section-block">
          <div className="stat-grid">
            <div className="stat">
              <span>Extracted facts</span>
              <strong>{candidate.facts.length}</strong>
            </div>
            <div className="stat">
              <span>User reviewed</span>
              <strong>
                {candidate.facts.filter((fact) => fact.verified_by_user).length}
              </strong>
            </div>
            <div className="stat">
              <span>Experience · years</span>
              <strong>{candidate.experience_years}</strong>
            </div>
          </div>
          <Card title="Your extracted profile">
            <div className="form-grid">
              <label className="field">
                Name
                <input
                  value={candidate.name}
                  maxLength={200}
                  onChange={(event) =>
                    workspace.setCandidate({
                      ...candidate,
                      name: event.target.value,
                    })
                  }
                />
              </label>
              <label className="field">
                Experience in years
                <input
                  type="number"
                  min={0}
                  max={80}
                  step="0.1"
                  value={candidate.experience_years}
                  onChange={(event) =>
                    workspace.setCandidate({
                      ...candidate,
                      experience_years: Number(event.target.value),
                    })
                  }
                />
              </label>
              <label className="field full">
                Locations · comma separated
                <input
                  value={candidate.locations.join(", ")}
                  maxLength={2000}
                  onChange={(event) =>
                    workspace.setCandidate({
                      ...candidate,
                      locations: event.target.value
                        .split(",")
                        .map((value) => value.trim()),
                    })
                  }
                />
              </label>
            </div>
            <p style={{ margin: "20px 0 15px" }} className="small muted">
              {candidate.summary || "No summary extracted."}
            </p>
            <Chips values={candidate.skills} empty="No skills extracted" />
            <Notice>
              Skill chips are extracted suggestions. Matching and tailoring use
              reviewed facts, not these chips alone. Reviewing a fact is not
              identity verification.
            </Notice>
          </Card>
          <FactLedger candidate={candidate} onChange={workspace.setCandidate} />
          <div className="actions">
            <ActionLink href="/jobs">Find a role to compare</ActionLink>
            <ActionLink href="/match" secondary>
              Go to match
            </ActionLink>
          </div>
        </div>
      )}
    </>
  );
}
