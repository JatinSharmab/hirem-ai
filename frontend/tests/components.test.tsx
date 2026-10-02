// @vitest-environment jsdom
import { afterEach, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import { FactLedger } from "@/components/profile/fact-ledger";
import { ScoreBreakdown } from "@/components/matching/score-breakdown";
import { Badge, Button, LoadingRows } from "@/components/common/ui";
import { candidate, match } from "./fixtures";
afterEach(cleanup);
it("reviews a fact without altering its provenance", () => {
  const onChange = vi.fn();
  render(<FactLedger candidate={candidate} onChange={onChange} />);
  expect(screen.getByText("0 / 1 reviewed")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("checkbox"));
  expect(onChange.mock.calls[0][0].facts[0]).toEqual({
    ...candidate.facts[0],
    verified_by_user: true,
  });
  expect(screen.getByText("Skills: Python")).toBeInTheDocument();
});
it("can unreview a fact", () => {
  const onChange = vi.fn();
  render(
    <FactLedger
      candidate={{
        ...candidate,
        facts: candidate.facts.map((fact) => ({
          ...fact,
          verified_by_user: true,
        })),
      }}
      onChange={onChange}
    />,
  );
  fireEvent.click(screen.getByRole("checkbox"));
  expect(onChange.mock.calls[0][0].facts[0].verified_by_user).toBe(false);
});
it("shows the returned score, all factors and proxy limits", () => {
  render(<ScoreBreakdown score={match.score} />);
  expect(screen.getByText("77.50")).toBeInTheDocument();
  expect(screen.getByText(/No embedding similarity/)).toBeInTheDocument();
  expect(screen.getByText(/not an employer ATS score/)).toBeInTheDocument();
  expect(
    screen.getByText(/weighting, not a claim about accuracy/),
  ).toBeInTheDocument();
});
it("expresses failed verification with text and prevents a busy button click", () => {
  const click = vi.fn();
  render(
    <>
      <Badge value="FAILED" />
      <Button busy onClick={click}>
        Generate
      </Button>
      <LoadingRows />
    </>,
  );
  expect(screen.getByText("Failed")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button"));
  expect(click).not.toHaveBeenCalled();
  expect(screen.getByRole("status")).toHaveAccessibleName(
    "Loading workspace data",
  );
});
