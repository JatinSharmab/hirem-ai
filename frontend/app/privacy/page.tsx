"use client";
import { useState } from "react";
import {
  Button,
  Card,
  ErrorNotice,
  Notice,
  PageHeading,
} from "@/components/common/ui";
import { useWorkspace } from "@/components/layout/workspace-provider";
import { useTask } from "@/hooks/use-task";
import { api } from "@/lib/api/browser-client";
export default function PrivacyPage() {
  const workspace = useWorkspace();
  const task = useTask();
  const [confirmed, setConfirmed] = useState(false);
  const [cleared, setCleared] = useState(false);
  return (
    <>
      <PageHeading
        eyebrow="YOUR DATA & YOUR CONTROL"
        title="A temporary workspace, by design."
      >
        No account is required. Use non-confidential information and keep your
        own copies of important work.
      </PageHeading>
      <Notice>
        Your public demo workspace is temporary. Imported jobs and application
        records expire automatically. Resume content is not intended for
        confidential information. The live workflow processes your actual
        inputs; it is not a sample-data demo.
      </Notice>
      <div className="grid-two">
        <Card title="What is stored where">
          <div className="prose">
            <p>
              <strong>In this tab:</strong> your extracted profile, review
              choices, match result, bookmarks, and resume versions are held in
              memory. They are cleared by a reload, closing the tab, session
              expiry, or clearing the workspace.
            </p>
            <p>
              <strong>In PostgreSQL:</strong> imported jobs, cached job
              requirements, and application records belong to your anonymous
              workspace. Their normal lifetime is 24 hours after the last save.
              Cleanup is periodic while the API is awake.
            </p>
            <p>
              <strong>In an HTTP-only cookie:</strong> a random workspace
              identifier, issued/expiry times, and a signature. Browser scripts
              cannot read this cookie. Its session lasts 24 hours.
            </p>
            <p>
              <strong>With Gemini:</strong> resume text or reviewed evidence and
              job requirements are sent only through explicit workflow actions
              with the required consent. Provider processing is subject to the
              provider’s own policies.
            </p>
          </div>
        </Card>
        <Card title="Session & usage">
          <div className="prose">
            <p>
              Session expiry:{" "}
              <strong>
                {workspace.expiresAt
                  ? new Date(workspace.expiresAt).toLocaleString()
                  : "Initializing your temporary session…"}
              </strong>
            </p>
            <p>
              The public backend allows up to 10 AI calls per visitor session
              per UTC day and 100 site-wide. Failed calls can consume the
              allowance.
            </p>
            <p>
              Manual imports: 20 per visitor / 500 site-wide each day. ATS
              discovery: 3 per visitor / 30 site-wide each day. Short-term API
              limits also apply.
            </p>
            <p>
              Limits are enforced by Python, not by this page. A fresh anonymous
              session is not a verified new person.
            </p>
            <p>
              Clearing this workspace preserves its identifier and daily usage
              counters. It does not reset your allowance.
            </p>
          </div>
        </Card>
        <Card title="File handling & limitations">
          <div className="prose">
            <p>
              The Next.js interface accepts PDF and DOCX files up to 4 MB. The
              backend validates the actual file contents, not just the filename,
              and applies its own 5 MB cap.
            </p>
            <p>
              PDFs must have readable text, no encryption, and at most 50 pages.
              Extracted text is limited to 30,000 characters. DOCX archives have
              decompression limits.
            </p>
            <p>
              Profiles and generated resume files are not saved as workspace
              database records by this workflow. Exported copies remain on your
              device until you remove them.
            </p>
            <p>
              This portfolio app makes no compliance certification or
              identity-verification claim.
            </p>
          </div>
        </Card>
        <Card title="Clear this workspace">
          <p className="small muted">
            Remove your imported jobs, cached requirements and application
            records, and clear this tab’s profile, match, bookmarks and resume
            history. This cannot be undone.
          </p>
          <label className="checkbox" style={{ margin: "20px 0" }}>
            <input
              type="checkbox"
              checked={confirmed}
              onChange={(event) => setConfirmed(event.target.checked)}
            />
            I want to delete this workspace’s saved records.
          </label>
          <Button
            variant="danger"
            disabled={!confirmed || workspace.status !== "ready"}
            busy={task.busy}
            onClick={() =>
              void task.run(async () => {
                await api("workspace", { method: "DELETE" });
                workspace.reset();
                setConfirmed(false);
                setCleared(true);
              })
            }
          >
            Clear workspace data
          </Button>
          <ErrorNotice message={task.error} />
          {cleared && (
            <Notice>
              Workspace data cleared. Your current session and usage counters
              remain in place.
            </Notice>
          )}
        </Card>
      </div>
    </>
  );
}
