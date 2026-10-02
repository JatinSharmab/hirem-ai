"use client";
import { Button, Empty } from "@/components/common/ui";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <>
      <Empty title="This view could not load">
        Your workspace may still be available. Try loading this view again.
      </Empty>
      <Button onClick={reset}>Try again</Button>
    </>
  );
}
