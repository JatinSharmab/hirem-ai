import { Card, Notice, PageHeading } from "@/components/common/ui";
export const metadata = { title: "Architecture" };
export default function ArchitecturePage() {
  return (
    <>
      <PageHeading
        eyebrow="UNDER THE HOOD"
        title="AI extracts. Evidence stays in control."
      >
        A clear separation between the interface, AI assistance, deterministic
        Python logic, and persistent data.
      </PageHeading>
      <div className="architecture-flow">
        <div className="architecture-node">
          <span className="eyebrow">01 / INTERFACE</span>
          <strong>Next.js & React</strong>Pages and forms render independently
          of backend wake-up. Your facts stay in tab memory.
        </div>
        <div className="architecture-node">
          <span className="eyebrow">02 / SERVER BRIDGE</span>
          <strong>Next.js BFF</strong>Validates requests, checks a signed
          workspace cookie, and attaches the private gateway credential.
        </div>
        <div className="architecture-node">
          <span className="eyebrow">03 / BUSINESS LOGIC</span>
          <strong>FastAPI on Render</strong>Python owns parsing, quotas,
          scoring, evidence checks, exports, and data access.
        </div>
        <div className="architecture-node">
          <span className="eyebrow">04 / DEPENDENCIES</span>
          <strong>Supabase · Gemini · ATS</strong>Parallel backend integrations:
          PostgreSQL for records, Gemini for extraction and selection, ATS for
          jobs.
        </div>
      </div>
      <div className="grid-two">
        <Card title="The real workflow">
          <ol className="prose">
            <li>
              Upload PDF or DOCX with consent. Python validates the file and
              extracts text.
            </li>
            <li>
              Gemini extracts structured candidate facts. You inspect and review
              each one.
            </li>
            <li>
              Import a description or discover one company’s Greenhouse, Lever,
              or Ashby board.
            </li>
            <li>
              Explicitly analyze the job. Gemini extracts requirements,
              validated by Pydantic and cached in PostgreSQL.
            </li>
            <li>
              Python calculates the seven-factor Career Fit Score and maps
              requirements to reviewed evidence.
            </li>
            <li>
              Gemini selects reviewed fact IDs. Python constructs and verifies
              each resume bullet.
            </li>
            <li>
              Approve the extract, download PDF or DOCX, and track the
              application yourself.
            </li>
          </ol>
        </Card>
        <Card title="What AI does — and what it cannot approve">
          <div className="prose">
            <p>
              Gemini helps interpret text and choose relevant evidence. Its
              structured responses are validated, but can still be wrong.
            </p>
            <p>
              A human review flag makes a fact eligible for use. Deterministic
              Python checks prevent unsupported fact IDs and reject failed
              exports. They cannot prove the original resume is truthful.
            </p>
            <p>
              The frontend displays the backend’s score. It never calculates a
              competing score or calls Gemini directly.
            </p>
          </div>
        </Card>
        <Card title="Matching, honestly explained">
          <div className="prose">
            <p>
              Seven factors have fixed weights: required skills 30%, relevant
              evidence 25%, role proxy 15%, responsibility proxy 10%, experience
              10%, preferred skills 5%, and location/work mode 5%.
            </p>
            <p>
              The role proxy reuses required-skill coverage. The responsibility
              proxy reuses relevant evidence. Location is compared; work mode is
              not independently matched.
            </p>
            <p>
              Current skill matching uses normalized reviewed skill facts. There
              is no live embedding similarity or production vector retrieval in
              this path.
            </p>
          </div>
          <Notice>
            55% is the combined weighting of required skills and relevant
            evidence. No matching-accuracy percentage has been established.
          </Notice>
        </Card>
        <Card title="Security boundary">
          <div className="prose">
            <p>
              The browser talks to same-origin Next.js endpoints. Only the
              server adds the private Render API gateway secret.
            </p>
            <p>
              A signed, HTTP-only cookie identifies a temporary workspace.
              Backend ownership checks isolate its jobs, cached requirements,
              and application records.
            </p>
            <p>
              Gemini and database credentials stay on the backend. Quotas and
              provider concurrency limits stay in Python.
            </p>
            <p>
              This is anonymous isolation, not an account system. Clearing
              browser cookies can create a new visitor session; site-wide limits
              remain the final usage ceiling.
            </p>
          </div>
        </Card>
        <Card title="Hosting and practical limits">
          <div className="prose">
            <p>
              The Next.js page can load while the free Render API is asleep.
              Bounded checks wake it when you visit. AI actions wait for
              readiness.
            </p>
            <p>
              The interface accepts files up to 4 MB to fit Vercel’s function
              payload limit. The Python parser’s own cap remains 5 MB, 50 PDF
              pages, and 30,000 extracted characters.
            </p>
            <p>
              The backend normally expires saved workspace records after 24
              hours. Cleanup runs when the service is awake. Profile and resume
              history disappear on reload.
            </p>
          </div>
        </Card>
        <Card title="Future architecture, clearly separated">
          <div className="prose">
            <p>
              Vector retrieval, pgvector, durable LangGraph checkpointing, and
              autonomous agent orchestration are not part of the current
              production workflow. Related repository scaffolding is not
              evidence of a deployed feature.
            </p>
            <p>
              Possible next steps include evaluated semantic retrieval,
              account-based persistence, durable background jobs, and a larger
              labeled evaluation set.
            </p>
            <p>
              HireMe AI does not submit applications automatically or search the
              whole internet.
            </p>
          </div>
          <a
            className="text-link"
            href="https://github.com/JatinSharmab/hirem-ai"
            target="_blank"
            rel="noopener noreferrer"
          >
            Inspect the source on GitHub ↗
          </a>
        </Card>
      </div>
    </>
  );
}
