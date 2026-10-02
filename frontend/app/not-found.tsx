import { Empty } from "@/components/common/ui";
export default function NotFound() {
  return (
    <Empty title="Page not found" href="/" action="Back to overview">
      Choose a page from the workspace navigation.
    </Empty>
  );
}
