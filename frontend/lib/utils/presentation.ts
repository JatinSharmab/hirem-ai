import type { Score } from "@/types";

export function label(value: string): string {
  return value
    .toLowerCase()
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}
export function safeExternalUrl(
  value: string | null | undefined,
): string | null {
  if (!value) return null;
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) &&
      !url.username &&
      !url.password
      ? url.href
      : null;
  } catch {
    return null;
  }
}
export function scoreDisplay(value: number): string {
  return Number.isFinite(value)
    ? value.toFixed(2).replace(/\.00$/, "")
    : "Not available";
}
export const scoreFactors: {
  key: Exclude<keyof Score, "total">;
  title: string;
  weight: string;
  explanation: string;
}[] = [
  {
    key: "required_skill_coverage",
    title: "Required skill coverage",
    weight: "30%",
    explanation: "Mandatory skills supported by reviewed skill facts.",
  },
  {
    key: "relevant_evidence",
    title: "Relevant evidence",
    weight: "25%",
    explanation: "Listed skill requirements linked to candidate fact IDs.",
  },
  {
    key: "semantic_role_alignment",
    title: "Semantic role alignment proxy",
    weight: "15%",
    explanation:
      "Currently reuses required-skill coverage. No embedding similarity is used.",
  },
  {
    key: "responsibility_alignment",
    title: "Responsibility alignment proxy",
    weight: "10%",
    explanation:
      "Currently reuses relevant evidence; this is not separate responsibility matching.",
  },
  {
    key: "experience_alignment",
    title: "Experience alignment",
    weight: "10%",
    explanation: "Whether the minimum experience is met or unspecified.",
  },
  {
    key: "preferred_skill_coverage",
    title: "Preferred skill coverage",
    weight: "5%",
    explanation: "Preferred skills supported by reviewed skill facts.",
  },
  {
    key: "location_work_mode",
    title: "Location / work mode",
    weight: "5%",
    explanation:
      "Current implementation compares location or accepts an unspecified location; it does not independently compare work mode.",
  },
];
