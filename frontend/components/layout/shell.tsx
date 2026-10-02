"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  ArrowUpRight,
  BriefcaseBusiness,
  ChartNoAxesCombined,
  FileCheck2,
  Fingerprint,
  GitBranch,
  House,
  Menu,
  ScanLine,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import { useWorkspace } from "./workspace-provider";
const items = [
  ["/", "Overview", House],
  ["/profile", "Profile", Fingerprint],
  ["/jobs", "Jobs", BriefcaseBusiness],
  ["/match", "Match", ScanLine],
  ["/resume", "Resume Studio", FileCheck2],
  ["/applications", "Applications", GitBranch],
  ["/insights", "Insights", ChartNoAxesCombined],
  ["/architecture", "Architecture", Sparkles],
] as const;
export function Shell({ children }: { children: ReactNode }) {
  const path = usePathname();
  const [open, setOpen] = useState(false);
  const menuButton = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (!open) return;
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
        menuButton.current?.focus();
      }
    };
    document.addEventListener("keydown", close);
    return () => document.removeEventListener("keydown", close);
  }, [open]);
  const workspace = useWorkspace();
  const ready = workspace.status === "ready";
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="mobile-header">
        <Link href="/" className="brand">
          <span className="brand-mark">H</span>HireMe AI
          <span className="brand-dot">.</span>
        </Link>
        <button
          ref={menuButton}
          className="icon-button"
          aria-label={open ? "Close navigation" : "Open navigation"}
          aria-expanded={open}
          aria-controls="navigation"
          onClick={() => setOpen(!open)}
        >
          {open ? <X /> : <Menu />}
        </button>
      </header>
      {open && (
        <button
          className="nav-overlay"
          aria-label="Close navigation"
          onClick={() => setOpen(false)}
        />
      )}
      <aside id="navigation" className={`sidebar ${open ? "is-open" : ""}`}>
        <Link href="/" onClick={() => setOpen(false)} className="brand">
          <span className="brand-mark">H</span>HireMe AI
          <span className="brand-dot">.</span>
        </Link>
        <p className="nav-label">CAREER WORKSPACE</p>
        <nav aria-label="Main navigation">
          {items.map(([href, name, Icon]) => (
            <Link
              key={href}
              href={href}
              onClick={() => setOpen(false)}
              className={`nav-item ${(href === "/" ? path === href : path.startsWith(href)) ? "active" : ""}`}
              aria-current={
                (href === "/" ? path === href : path.startsWith(href))
                  ? "page"
                  : undefined
              }
            >
              <Icon size={19} aria-hidden="true" />
              {name}
            </Link>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="workspace-note">
            <ShieldCheck size={20} aria-hidden="true" />
            <strong>Your evidence. Your control.</strong>
            <p>
              Anonymous workspace.
              <br />
              No signup needed.
            </p>
            <Link href="/privacy" onClick={() => setOpen(false)}>
              Privacy & workspace <ArrowUpRight size={14} />
            </Link>
          </div>
          <span className="portfolio-label">
            BUILT FOR EVIDENCE, NOT GUESSWORK
          </span>
        </div>
      </aside>
      <div className="main-column">
        <div className="topbar">
          <span>Evidence-grounded career intelligence</span>
          <div className={`backend-pill ${ready ? "ready" : ""}`} role="status">
            <span className="status-dot" />
            {ready
              ? "Backend ready"
              : workspace.status === "error"
                ? "Temporarily unavailable"
                : workspace.status === "waking"
                  ? "Waking up…"
                  : "Checking backend…"}
          </div>
        </div>
        {!ready && (
          <div className="wake-banner" role="status">
            <div>
              <strong>
                {workspace.status === "error"
                  ? "The backend is temporarily unavailable."
                  : "Waking up HireMe AI backend…"}
              </strong>
              <p>
                {workspace.statusError ??
                  "The AI backend uses portfolio hosting and may take around a minute to wake after inactivity. You can explore and prepare your inputs meanwhile."}
              </p>
            </div>
            {workspace.status === "error" && (
              <button className="button secondary" onClick={workspace.retry}>
                Retry connection
              </button>
            )}
          </div>
        )}
        <main id="main" tabIndex={-1}>
          {children}
        </main>
        <footer className="footer">
          <span>HireMe AI · Discover. Match. Tailor. Verify.</span>
          <Link href="/privacy">Temporary workspace & privacy</Link>
        </footer>
      </div>
    </div>
  );
}
