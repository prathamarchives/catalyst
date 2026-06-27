import React, { useState } from "react";

type BtnProps = React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "default" | "primary" | "ghost" };
export function Button({ variant = "default", className = "", ...rest }: BtnProps) {
  const v = variant === "primary" ? "btn-primary" : variant === "ghost" ? "btn-ghost" : "";
  return <button className={`btn ${v} ${className}`} {...rest} />;
}

export function CatalystMark({ className = "" }: { className?: string }) {
  return (
    <span className={`catalyst-mark ${className}`} aria-hidden="true">
      <span />
      <span />
      <span />
      <span />
      <span />
      <span />
      <span />
      <span />
      <span />
      <span />
      <span />
      <span />
    </span>
  );
}

export function Card({ tight, className = "", ...rest }: { tight?: boolean } & React.HTMLAttributes<HTMLDivElement>) {
  return <div className={`card glass-card ${tight ? "card-tight" : ""} ${className}`} {...rest} />;
}

type FieldProps = {
  label?: string;
  hint?: string;
  textarea?: boolean;
  mono?: boolean;
} & React.InputHTMLAttributes<HTMLInputElement> & React.TextareaHTMLAttributes<HTMLTextAreaElement>;
export function Field({ label, hint, textarea, mono, ...rest }: FieldProps) {
  return (
    <div className="field">
      {label && <label>{label}</label>}
      {textarea
        ? <textarea className={`in ${mono ? "mono-area" : ""}`} {...(rest as any)} />
        : <input className="in" {...(rest as any)} />}
      {hint && <span className="hint">{hint}</span>}
    </div>
  );
}

export function Stepper({ step, total, label }: { step: number; total: number; label?: string }) {
  return (
    <div className="stepper">
      {Array.from({ length: total }).map((_, i) => <div key={i} className={`seg ${i <= step ? "on" : ""}`} />)}
      {label && <span className="lbl">{label}</span>}
    </div>
  );
}

export function CopyButton({ text, label = "Copy", variant = "default" }: { text: string; label?: string; variant?: "default" | "primary" | "ghost" }) {
  const [done, setDone] = useState(false);
  return (
    <Button variant={variant} onClick={async () => {
      try { await navigator.clipboard.writeText(text); } catch { /* clipboard blocked */ }
      setDone(true);
      setTimeout(() => setDone(false), 1600);
    }}>{done ? "Copied" : label}</Button>
  );
}

export function SectionView({ name, body, filled = true }: { name: string; body?: string; filled?: boolean }) {
  return (
    <div className={`section ${filled ? "" : "unfilled"}`}>
      <div className="bar" />
      <div className="grow">
        <div className="name">{name}{!filled && <span className="faint small"> - unfilled</span>}</div>
        {body && <div className="body">{body}</div>}
      </div>
    </div>
  );
}

export function Verdict({ value }: { value: string }) {
  return <span className={`badge ${value}`}><span className="dot" />{value}</span>;
}

export function ReadinessRing({ score, size = 44 }: { score: number; size?: number }) {
  const r = (size - 6) / 2;
  const c = 2 * Math.PI * r;
  const off = c * (1 - Math.max(0, Math.min(1, score)));
  return (
    <div className="ring" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--line)" strokeWidth="3" />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--accent)" strokeWidth="3"
          strokeDasharray={c} strokeDashoffset={off} strokeLinecap="round" />
      </svg>
      <span className="pct">{Math.round(score * 100)}</span>
    </div>
  );
}
