import Link from "next/link";
import {
  ArrowRight,
  Check,
  CircleAlert,
  LoaderCircle,
  Sparkles,
  X,
} from "lucide-react";
import type { ButtonHTMLAttributes, ReactNode } from "react";
import { label, safeExternalUrl } from "@/lib/utils/presentation";

export function PageHeading({
  eyebrow,
  title,
  children,
}: {
  eyebrow: string;
  title: string;
  children?: ReactNode;
}) {
  return (
    <header className="page-heading">
      <p className="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      {children && <p className="lede">{children}</p>}
    </header>
  );
}
export function Card({
  title,
  children,
  className = "",
}: {
  title?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`card ${className}`}>
      {title && <h2>{title}</h2>}
      {children}
    </section>
  );
}
export function Button({
  children,
  busy,
  variant = "primary",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  busy?: boolean;
  variant?: "primary" | "secondary" | "danger";
}) {
  return (
    <button
      {...props}
      disabled={props.disabled || busy}
      className={`button ${variant} ${props.className ?? ""}`}
      aria-busy={busy || undefined}
    >
      {busy && <LoaderCircle size={17} className="spin" aria-hidden="true" />}
      {children}
    </button>
  );
}
export function ActionLink({
  href,
  children,
  secondary = false,
}: {
  href: string;
  children: ReactNode;
  secondary?: boolean;
}) {
  return (
    <Link
      href={href}
      className={`button ${secondary ? "secondary" : "primary"}`}
    >
      {children}
      <ArrowRight size={16} aria-hidden="true" />
    </Link>
  );
}
export function ErrorNotice({ message }: { message?: string | null }) {
  return message ? (
    <div className="notice error" role="alert">
      <CircleAlert size={18} aria-hidden="true" />
      <span>{message}</span>
    </div>
  ) : null;
}
export function Notice({ children }: { children: ReactNode }) {
  return <div className="notice">{children}</div>;
}
export function Empty({
  title,
  children,
  href,
  action,
}: {
  title: string;
  children: ReactNode;
  href?: string;
  action?: string;
}) {
  return (
    <div className="empty">
      <Sparkles size={28} aria-hidden="true" />
      <h2>{title}</h2>
      <p>{children}</p>
      {href && <ActionLink href={href}>{action ?? "Get started"}</ActionLink>}
    </div>
  );
}
export function Badge({ value }: { value: string }) {
  return (
    <span
      className={`badge ${["PASSED", "OPEN", "OFFER"].includes(value) ? "positive" : ["FAILED", "CLOSED", "REJECTED", "ERROR"].includes(value) ? "negative" : ""}`}
    >
      {value === "PASSED" && <Check size={12} aria-hidden="true" />}
      {value === "FAILED" && <X size={12} aria-hidden="true" />}
      {label(value)}
    </span>
  );
}
export function Chips({
  values,
  empty = "Not specified",
}: {
  values: string[];
  empty?: string;
}) {
  return values.length ? (
    <div className="chips">
      {values.map((value, index) => (
        <span className="chip" key={`${value}-${index}`}>
          {value}
        </span>
      ))}
    </div>
  ) : (
    <p className="muted">{empty}</p>
  );
}
export function ExternalLink({
  url,
  children,
}: {
  url?: string | null;
  children: ReactNode;
}) {
  const safe = safeExternalUrl(url);
  return safe ? (
    <a
      className="text-link"
      href={safe}
      target="_blank"
      rel="noopener noreferrer"
    >
      {children} ↗
    </a>
  ) : (
    <span className="muted">No official link provided</span>
  );
}
export function LoadingRows() {
  return (
    <div
      role="status"
      aria-label="Loading workspace data"
      className="skeleton-list"
    >
      <div />
      <div />
      <div />
    </div>
  );
}
