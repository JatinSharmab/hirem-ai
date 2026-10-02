import type { Metadata } from "next";
import { WorkspaceProvider } from "@/components/layout/workspace-provider";
import { Shell } from "@/components/layout/shell";
import "./globals.css";
export const metadata: Metadata = {
  title: {
    default: "HireMe AI — Evidence-Grounded Career Intelligence",
    template: "%s | HireMe AI",
  },
  description:
    "Review your resume evidence, understand your career fit, and create verified job-specific resume extracts. AI extracts and selects. You stay in control.",
};
export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <WorkspaceProvider>
          <Shell>{children}</Shell>
        </WorkspaceProvider>
      </body>
    </html>
  );
}
