"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import ApiKeySection from "../../../components/settings/ApiKeySection";
import ConnectorPathsSection from "../../../components/settings/ConnectorPathsSection";
import GraphAuthSection from "../../../components/settings/GraphAuthSection";
import LintCadenceSection from "../../../components/settings/LintCadenceSection";
import ModelsSection from "../../../components/settings/ModelsSection";
import type { SettingsStatus } from "./types";

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, { cache: "no-store", ...init });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`${r.status} ${r.statusText}${text ? ` — ${text}` : ""}`);
  }
  return r.json() as Promise<T>;
}

type SectionKey = "api-key" | "models" | "graph" | "connectors" | "lint";

const SECTIONS: { key: SectionKey; label: string; anchor: string }[] = [
  { key: "api-key", label: "API key", anchor: "#api-key" },
  { key: "models", label: "Models", anchor: "#models" },
  { key: "graph", label: "Graph auth", anchor: "#graph" },
  { key: "connectors", label: "Connectors", anchor: "#connectors" },
  { key: "lint", label: "Lint cadence", anchor: "#lint" },
];

function StatusIcon({ ok, detail }: { ok: boolean; detail: string }) {
  if (ok) {
    return (
      <span className="settings-status-icon settings-status-ok" title={detail}>
        ✓
      </span>
    );
  }
  const isWarn = detail.toLowerCase().includes("warn") || detail.toLowerCase().includes("expired");
  return (
    <span
      className={`settings-status-icon ${isWarn ? "settings-status-warn" : "settings-status-err"}`}
      title={detail}
    >
      {isWarn ? "!" : "✕"}
    </span>
  );
}

function scrollToSection(anchor: string) {
  const id = anchor.replace("#", "");
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
    el.classList.add("settings-section-highlight");
    setTimeout(() => el.classList.remove("settings-section-highlight"), 1500);
  }
}

export default function SettingsPage() {
  const [settingsStatus, setSettingsStatus] = useState<SettingsStatus | null>(null);
  const [restarting, setRestarting] = useState(false);
  const dirtyRef = useRef<Record<SectionKey, boolean>>({
    "api-key": false,
    models: false,
    graph: false,
    connectors: false,
    lint: false,
  });
  const [apiKeyConfigured, setApiKeyConfigured] = useState(false);

  const loadStatus = useCallback(async () => {
    try {
      const s = await fetchJSON<SettingsStatus>("/api/settings/status");
      setSettingsStatus(s);
      setApiKeyConfigured(s.api_key.ok);
    } catch {
      // Non-fatal — sidebar shows stale/empty data.
    }
  }, []);

  useEffect(() => {
    loadStatus();
    const poll = setInterval(loadStatus, 10_000);
    return () => clearInterval(poll);
  }, [loadStatus]);

  useEffect(() => {
    function handleBeforeUnload(e: BeforeUnloadEvent) {
      const anyDirty = Object.values(dirtyRef.current).some(Boolean);
      if (anyDirty) {
        e.preventDefault();
        e.returnValue = "";
      }
    }
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, []);

  function makeDirtyHandler(key: SectionKey) {
    return (dirty: boolean) => {
      dirtyRef.current = { ...dirtyRef.current, [key]: dirty };
    };
  }

  async function handleRestart() {
    setRestarting(true);
    try {
      await fetch("/api/ops/restart", { method: "POST" });
    } catch {
      // Expected — server is going down.
    }
    setTimeout(() => window.location.reload(), 10_000);
  }

  return (
    <div className="settings-page">
      <div className="settings-layout">
        <div className="settings-main">
          <nav className="settings-nav-rail" aria-label="Settings sections">
            {SECTIONS.map((s) => (
              <a
                key={s.key}
                href={s.anchor}
                className="settings-nav-link"
                onClick={(e) => {
                  e.preventDefault();
                  scrollToSection(s.anchor);
                }}
              >
                {s.label}
              </a>
            ))}
          </nav>

          <div className="settings-sections">
            <ApiKeySection onDirtyChange={makeDirtyHandler("api-key")} />
            <ModelsSection onDirtyChange={makeDirtyHandler("models")} />
            <GraphAuthSection onDirtyChange={makeDirtyHandler("graph")} />
            <ConnectorPathsSection onDirtyChange={makeDirtyHandler("connectors")} />
            <LintCadenceSection
              onDirtyChange={makeDirtyHandler("lint")}
              apiKeyConfigured={apiKeyConfigured}
            />
          </div>
        </div>

        <aside className="settings-sidebar">
          <h3 className="settings-sidebar-title">Status</h3>
          <div className="settings-status-list">
            {SECTIONS.map((s) => {
              const entry = settingsStatus
                ? settingsStatus[s.key === "api-key" ? "api_key" : s.key === "graph" ? "graph" : s.key === "connectors" ? "connectors" : s.key === "lint" ? "lint" : "models"]
                : null;
              return (
                <button
                  key={s.key}
                  className="settings-status-row"
                  onClick={() => scrollToSection(s.anchor)}
                  type="button"
                >
                  <span className="settings-status-label">{s.label}</span>
                  {entry ? (
                    <>
                      <StatusIcon ok={entry.ok} detail={entry.detail} />
                      <span className="settings-status-detail">{entry.detail}</span>
                    </>
                  ) : (
                    <span className="settings-status-loading">...</span>
                  )}
                </button>
              );
            })}
          </div>

          <div className="settings-sidebar-footer">
            <button
              type="button"
              className="settings-btn-secondary settings-restart-btn"
              onClick={handleRestart}
              disabled={restarting}
            >
              {restarting ? "Restarting..." : "Restart server"}
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}
