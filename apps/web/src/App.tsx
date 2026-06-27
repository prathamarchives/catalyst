import React, { useEffect, useState } from "react";
import { api } from "./api";
import Onboarding from "./Onboarding";
import Workspace from "./Workspace";
import { CatalystMark } from "./components";

const GITHUB_URL = "https://github.com/prathamarchives/catalyst";

function useScrollReveal(key: string) {
  useEffect(() => {
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const nodes = Array.from(document.querySelectorAll<HTMLElement>(".reveal"));
    if (reduceMotion || nodes.length === 0) {
      nodes.forEach((node) => node.classList.add("is-visible"));
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        }
      },
      { rootMargin: "0px 0px -12% 0px", threshold: 0.12 },
    );
    nodes.forEach((node) => observer.observe(node));
    return () => observer.disconnect();
  }, [key]);
}

export default function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [view, setView] = useState<"onboarding" | "workspace">("onboarding");

  useEffect(() => {
    api.status()
      .then((s) => {
        if (s.brains && s.brains.length > 0) setView("workspace");
      })
      .catch((err) => setError(err?.message || "Could not reach the local Catalyst API."))
      .finally(() => setLoading(false));
  }, []);

  useScrollReveal(`${view}:${loading}:${error}`);

  function jumpTo(id: string) {
    setView("onboarding");
    window.setTimeout(() => {
      document.getElementById(id)?.scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
        block: "start",
      });
    }, 40);
  }

  return (
    <div className="app">
      <header className="topbar">
        <button className="brand-lockup" type="button" onClick={() => jumpTo("hero")}>
          <CatalystMark />
          <span>
            <strong>Catalyst</strong>
            <small>taste, context, judgment</small>
          </span>
        </button>
        <nav className="nav-links" aria-label="Primary navigation">
          <button type="button" onClick={() => jumpTo("about")}>About</button>
          <button type="button" onClick={() => jumpTo("story")}>How it works</button>
          <button type="button" onClick={() => jumpTo("access")}>OSS</button>
          <button type="button" onClick={() => jumpTo("contact")}>Contact</button>
        </nav>
        <div className="top-actions">
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={() => setView(view === "workspace" ? "onboarding" : "workspace")}
          >
            {view === "workspace" ? "Start" : "Command center"}
          </button>
          <a className="btn btn-primary btn-sm" href={GITHUB_URL} target="_blank" rel="noreferrer">
            Try for Free
          </a>
        </div>
      </header>

      {loading ? (
        <main className="boot-screen">
          <div className="boot-card glass-card reveal is-visible">
            <CatalystMark className="large" />
            <p className="eyebrow">Local command center</p>
            <h1 className="t">Booting Catalyst.</h1>
            <p className="muted">Checking the localhost runtime and local brain state...</p>
          </div>
        </main>
      ) : error ? (
        <main className="container">
          <div className="card error-card reveal is-visible">
            <div className="eyebrow">Local API unavailable</div>
            <h1 className="t">The UI loaded, but the local runtime did not answer.</h1>
            <p className="muted">{error}</p>
            <div className="row wrap">
              <button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button>
              <code className="chip">py catalyst.py --no-open</code>
            </div>
          </div>
        </main>
      ) : view === "onboarding" ? (
        <Onboarding onDone={() => setView("workspace")} />
      ) : (
        <Workspace />
      )}
    </div>
  );
}
