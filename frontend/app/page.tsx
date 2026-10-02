import Link from "next/link";
import {
  ArrowRight,
  Check,
  FileCheck2,
  Fingerprint,
  ScanLine,
  ShieldCheck,
} from "lucide-react";
import { ActionLink } from "@/components/common/ui";
export default function Overview() {
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">
            <span className="tiny-square" /> EVIDENCE-GROUNDED CAREER
            INTELLIGENCE
          </p>
          <h1>
            Your next move.
            <br />
            <span>Backed by evidence.</span>
          </h1>
          <p className="hero-tagline">Discover. Match. Tailor. Verify.</p>
          <p className="lede">
            Turn your resume into reviewed evidence, compare it with real job
            requirements, understand your fit, and create a verified
            job-specific resume without allowing AI to freely invent experience.
          </p>
          <div className="actions">
            <ActionLink href="/profile">Analyze my resume</ActionLink>
            <ActionLink href="/jobs" secondary>
              Explore jobs
            </ActionLink>
          </div>
          <p className="microcopy">
            <ShieldCheck size={15} /> No signup · You review every fact ·
            Temporary workspace
          </p>
        </div>
        <div
          className="evidence-preview"
          aria-label="Illustration of the evidence workflow"
        >
          <div className="preview-top">
            <span className="eyebrow">THE EVIDENCE LOOP</span>
            <span className="preview-label">Illustration</span>
          </div>
          <div className="preview-document">
            <span className="document-icon">
              <Fingerprint />
            </span>
            <div>
              <strong>Your experience</strong>
              <p>A source, not a prompt to invent.</p>
            </div>
          </div>
          <div className="preview-connector" />
          <div className="preview-ledger">
            <div>
              <span className="step-label">01 / EXTRACT & REVIEW</span>
              <h2>Make every claim traceable.</h2>
            </div>
            <div className="example-fact">
              <Check size={17} />
              <span>Skill from your resume</span>
              <span className="mono">FACT ID</span>
            </div>
            <div className="example-fact">
              <Check size={17} />
              <span>Source text attached</span>
              <span className="mono">EVIDENCE</span>
            </div>
            <div className="example-fact">
              <Check size={17} />
              <span>Reviewed by you</span>
              <span className="mono">CONTROL</span>
            </div>
          </div>
          <div className="preview-outcome">
            <FileCheck2 />
            <div>
              <strong>Relevant. Grounded. Verifiable.</strong>
              <p>Only reviewed evidence enters your resume extract.</p>
            </div>
          </div>
        </div>
      </section>
      <section className="workflow-strip" aria-label="How it works">
        {[
          "Upload resume",
          "Review facts",
          "Import job",
          "Analyze match",
          "Tailor resume",
          "Export",
          "Track application",
        ].map((step, i) => (
          <div key={step}>
            <span>{String(i + 1).padStart(2, "0")}</span>
            <strong>{step}</strong>
            {i < 6 && <ArrowRight size={14} aria-hidden="true" />}
          </div>
        ))}
      </section>
      <section className="section-block">
        <div className="section-heading">
          <div>
            <p className="eyebrow">WHY HIREME AI</p>
            <h2>AI helps. Evidence decides.</h2>
          </div>
          <Link className="text-link" href="/architecture">
            View architecture <ArrowRight size={16} />
          </Link>
        </div>
        <div className="feature-grid">
          {[
            [
              Fingerprint,
              "A fact ledger you control",
              "Inspect the source behind each extracted fact. Review it before it can support a match or resume claim.",
            ],
            [
              ScanLine,
              "A score you can explain",
              "Seven transparent factors, requirement-level evidence, and clear skill gaps. No employer ATS score or hiring probability.",
            ],
            [
              FileCheck2,
              "Resume claims with provenance",
              "Gemini selects reviewed fact IDs. Python builds and verifies the wording before PDF or DOCX export.",
            ],
          ].map(([Icon, title, text]) => {
            const FeatureIcon = Icon as typeof Fingerprint;
            return (
              <article className="feature-card" key={String(title)}>
                <FeatureIcon size={25} />
                <h3>{String(title)}</h3>
                <p>{String(text)}</p>
              </article>
            );
          })}
        </div>
      </section>
      <section className="bottom-callout">
        <div>
          <p className="eyebrow">CONNECTED, WITH CLEAR BOUNDARIES</p>
          <h2>Your career workflow in one place.</h2>
          <p>
            Import a job description or use a company’s Greenhouse, Lever, or
            Ashby board. Keep your application progress in your temporary
            workspace.
          </p>
        </div>
        <ActionLink href="/profile">Start with your evidence</ActionLink>
      </section>
    </>
  );
}
