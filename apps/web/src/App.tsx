import React, { useEffect, useState } from "react";
import { api } from "./api";
import Onboarding from "./Onboarding";
import Workspace from "./Workspace";

export default function App() {
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<"onboarding" | "workspace">("onboarding");
  const [name, setName] = useState("");

  useEffect(() => {
    api.status()
      .then((s) => {
        if (s.brains && s.brains.length > 0) {
          setName(s.brains[0].name);
          setView("workspace");
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="app">
      <header className="header">
        <div className="brand">catalyst <span className="dot">· judgment for your AI</span></div>
        <div className="row">
          {view === "workspace"
            ? <button className="btn btn-ghost btn-sm" onClick={() => setView("onboarding")}>New brain</button>
            : name && <button className="btn btn-ghost btn-sm" onClick={() => setView("workspace")}>Workspace</button>}
        </div>
      </header>
      {loading ? (
        <div className="container"><p className="muted">Loading…</p></div>
      ) : view === "onboarding" ? (
        <Onboarding onDone={(n) => { setName(n); setView("workspace"); }} />
      ) : (
        <Workspace name={name} />
      )}
    </div>
  );
}
