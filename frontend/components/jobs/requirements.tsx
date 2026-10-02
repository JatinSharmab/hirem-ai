import { Card, Chips, Notice } from "@/components/common/ui";
import type { Requirements } from "@/types";
export function RequirementsView({ value }: { value: Requirements }) {
  const fields = [
    ["Role title", value.role_title],
    ["Role family", value.role_family],
    [
      "Minimum experience",
      value.minimum_experience == null
        ? null
        : `${value.minimum_experience} years`,
    ],
    [
      "Maximum experience",
      value.maximum_experience == null
        ? null
        : `${value.maximum_experience} years`,
    ],
    ["Location", value.location],
    ["Work mode", value.work_mode],
    ["Employment type", value.employment_type],
    ["Seniority", value.seniority],
    ["Domain", value.domain],
    ["Salary", value.salary],
  ];
  const lists = [
    ["Mandatory skills", value.mandatory_skills],
    ["Preferred skills", value.preferred_skills],
    ["Responsibilities", value.responsibilities],
    ["Education", value.education_requirements],
    ["Certifications", value.certifications],
    ["Keywords", value.keywords],
    ["Ambiguities & unknowns", value.ambiguities],
  ] as const;
  return (
    <Card title="Structured job requirements">
      <Notice>
        Structured by Gemini and validated by the backend. Compare the result
        with the original posting; structured output can still be incomplete or
        mistaken.
      </Notice>
      <dl className="definition-grid">
        {fields.map(([title, content]) => (
          <div key={title}>
            <dt>{title}</dt>
            <dd>{content ?? "Not specified"}</dd>
          </div>
        ))}
      </dl>
      {lists.map(([title, values]) => (
        <div key={title} style={{ marginTop: 23 }}>
          <h3 style={{ fontSize: 15, marginBottom: 10 }}>{title}</h3>
          <Chips values={values} />
        </div>
      ))}
    </Card>
  );
}
