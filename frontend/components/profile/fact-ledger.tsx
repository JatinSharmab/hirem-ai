"use client";
import type { Candidate } from "@/types";
import { Badge } from "@/components/common/ui";
export function FactLedger({
  candidate,
  onChange,
}: {
  candidate: Candidate;
  onChange: (candidate: Candidate) => void;
}) {
  const reviewed = candidate.facts.filter(
    (fact) => fact.verified_by_user,
  ).length;
  return (
    <section className="card">
      <div className="row-between">
        <h2>Candidate Fact Ledger</h2>
        <span className="badge positive">
          {reviewed} / {candidate.facts.length} reviewed
        </span>
      </div>
      <p className="muted small" style={{ marginTop: 12 }}>
        Extraction is a starting point. Check each fact against its source
        before marking it reviewed.
      </p>
      {candidate.facts.map((fact) => (
        <article key={fact.id} className="fact-row">
          <div className="row-between">
            <div className="chips">
              <code>{fact.id}</code>
              <Badge value={fact.category} />
            </div>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={fact.verified_by_user}
                onChange={(event) =>
                  onChange({
                    ...candidate,
                    facts: candidate.facts.map((item) =>
                      item.id === fact.id
                        ? { ...item, verified_by_user: event.target.checked }
                        : item,
                    ),
                  })
                }
              />
              {fact.verified_by_user ? "User reviewed" : "Review this fact"}
              <span className="sr-only"> {fact.id}</span>
            </label>
          </div>
          <p className="fact-value">{fact.value}</p>
          <p className="small muted">
            {fact.subject} · {fact.predicate}
          </p>
          <details>
            <summary>Inspect source evidence</summary>
            <p className="small muted">
              {fact.source_section ?? "Section not specified"} · AI extraction
              confidence: {Math.round(fact.confidence * 100)}% (not a truth
              guarantee)
            </p>
            <blockquote className="source-quote">
              {fact.source_text ??
                "No source excerpt provided. Inspect your original resume before reviewing this fact."}
            </blockquote>
          </details>
        </article>
      ))}
    </section>
  );
}
