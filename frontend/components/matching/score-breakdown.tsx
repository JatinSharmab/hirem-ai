import { Card, Notice } from "@/components/common/ui";
import { scoreDisplay, scoreFactors } from "@/lib/utils/presentation";
import type { Score } from "@/types";
export function ScoreBreakdown({ score }: { score: Score }) {
  return (
    <Card>
      <div className="score-hero">
        <div className="score-circle">
          <strong>{scoreDisplay(score.total)}</strong>
          <span>out of 100</span>
        </div>
        <div>
          <p className="eyebrow">EXPLAINABLE, BY DESIGN</p>
          <h2 style={{ marginTop: 8 }}>Career Fit Score</h2>
        </div>
      </div>
      <p className="small muted">
        This is HireMe AI’s transparent heuristic score, not an employer ATS
        score or hiring probability.
      </p>
      <Notice>
        55% of score weight comes from required-skill coverage and relevant
        evidence. This is weighting, not a claim about accuracy.
      </Notice>
      {scoreFactors.map((factor) => (
        <div className="factor" key={factor.key}>
          <div className="row-between">
            <strong>
              {factor.title} · {factor.weight}
            </strong>
            <span>{scoreDisplay(score[factor.key])}/100</span>
          </div>
          <div className="bar">
            <span
              style={{
                width: `${Math.max(0, Math.min(100, score[factor.key]))}%`,
              }}
            />
          </div>
          <p>{factor.explanation}</p>
        </div>
      ))}
    </Card>
  );
}
