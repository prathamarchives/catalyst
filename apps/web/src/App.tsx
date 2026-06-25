import React, { useEffect, useState } from "react";
import { api } from "./api";
import Onboarding from "./Onboarding";
import Workspace from "./Workspace";

export default function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [view, setView] = useState<"onboarding" | "workspace">("onboarding");

  useEffect(() => {
    api.status()
      .then((s) => { if (s.brains && s.brains.length > 0) setView("workspace"); })
      .catch((err) => setError(err?.message || "Could not reach the local Catalyst API."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="app">
      <header className="header">
        <div className="brand">catalyst <span className="dot">· judgment for your AI</span></div>
        <div className="row">
          {view === "workspace"
            ? <button className="btn btn-ghost btn-sm" onClick={() => setView("onboarding")}>Connect</button>
            : <button className="btn btn-ghost btn-sm" onClick={() => setView("workspace")}>Workspace</button>}
        </div>
      </header>
      {loading ? (
        <div className="container"><p className="muted">Loading Catalyst local...</p></div>
      ) : error ? (
        <div className="container">
          <div className="card">
            <div className="eyebrow">Local API unavailable</div>
            <h1 className="t">Catalyst is running, but the dashboard cannot reach the server.</h1>
            <p className="muted">{error}</p>
            <button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button>
          </div>
        </div>
      ) : view === "onboarding" ? (
        <Onboarding onDone={() => setView("workspace")} />
      ) : (
        <Workspace />
      )}
    </div>
  );
}
