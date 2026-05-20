"use client";

import { useEffect, useRef, useState } from "react";
import type { LintCadenceConfig } from "../../app/(tabs)/settings/types";

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, { cache: "no-store", ...init });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`${r.status} ${r.statusText}${text ? ` — ${text}` : ""}`);
  }
  return r.json() as Promise<T>;
}

const DEFAULTS: LintCadenceConfig = {
  nightly_time: "02:00",
  weekly_day: "Sunday",
  weekly_time: "04:00",
  nightly_enabled: true,
  weekly_enabled: true,
};

interface Props {
  onDirtyChange: (dirty: boolean) => void;
  apiKeyConfigured: boolean;
}

export default function LintCadenceSection({ onDirtyChange, apiKeyConfigured }: Props) {
  const [config, setConfig] = useState<LintCadenceConfig>({ ...DEFAULTS });
  const [saved, setSaved] = useState<LintCadenceConfig>({ ...DEFAULTS });
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    fetchJSON<LintCadenceConfig>("/api/settings/lint")
      .then((c) => {
        setConfig(c);
        setSaved(c);
      })
      .catch(() => {});
  }, []);

  function showToast(msg: string) {
    setToast(msg);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 4000);
  }

  function isDirty(): boolean {
    return (
      config.nightly_time !== saved.nightly_time ||
      config.weekly_day !== saved.weekly_day ||
      config.weekly_time !== saved.weekly_time ||
      config.nightly_enabled !== saved.nightly_enabled ||
      config.weekly_enabled !== saved.weekly_enabled
    );
  }

  function update<K extends keyof LintCadenceConfig>(key: K, value: LintCadenceConfig[K]) {
    const next = { ...config, [key]: value };
    setConfig(next);
    onDirtyChange(
      next.nightly_time !== saved.nightly_time ||
      next.weekly_day !== saved.weekly_day ||
      next.weekly_time !== saved.weekly_time ||
      next.nightly_enabled !== saved.nightly_enabled ||
      next.weekly_enabled !== saved.weekly_enabled
    );
  }

  async function handleSave() {
    setSaving(true);
    try {
      await fetchJSON<LintCadenceConfig>("/api/settings/lint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      setSaved({ ...config });
      onDirtyChange(false);
      showToast("Lint cadence saved.");
    } catch (e) {
      showToast(`Save failed: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section id="lint" className="settings-section">
      <h2 className="settings-section-title">
        Lint cadence
        {isDirty() && <span className="settings-dirty-dot" aria-label="Unsaved changes" />}
      </h2>

      {toast && (
        <div className="settings-toast" role="status">
          {toast}
        </div>
      )}

      <div className="settings-field-group">
        <label className="settings-label settings-checkbox-label">
          <input
            type="checkbox"
            className="settings-checkbox"
            checked={config.nightly_enabled}
            onChange={(e) => update("nightly_enabled", e.target.checked)}
          />
          Enable nightly lint
        </label>
      </div>

      <div className="settings-field-group">
        <label className="settings-label" htmlFor="nightly-time">
          Nightly lint time (24h)
        </label>
        <input
          id="nightly-time"
          type="time"
          className="settings-input settings-input-narrow"
          value={config.nightly_time}
          onChange={(e) => update("nightly_time", e.target.value)}
          disabled={!config.nightly_enabled}
        />
      </div>

      <div className="settings-field-group">
        <label className="settings-label settings-checkbox-label">
          <input
            type="checkbox"
            className="settings-checkbox"
            checked={config.weekly_enabled}
            onChange={(e) => update("weekly_enabled", e.target.checked)}
          />
          Enable weekly Opus pass
          {config.weekly_enabled && !apiKeyConfigured && (
            <span className="settings-inline-warn"> (requires Anthropic API key)</span>
          )}
        </label>
      </div>

      <div className="settings-inline-row">
        <div className="settings-field-group">
          <label className="settings-label" htmlFor="weekly-day">
            Weekly day
          </label>
          <select
            id="weekly-day"
            className="settings-select"
            value={config.weekly_day}
            onChange={(e) => update("weekly_day", e.target.value)}
            disabled={!config.weekly_enabled}
          >
            {DAYS.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        <div className="settings-field-group">
          <label className="settings-label" htmlFor="weekly-time">
            Weekly time (24h)
          </label>
          <input
            id="weekly-time"
            type="time"
            className="settings-input settings-input-narrow"
            value={config.weekly_time}
            onChange={(e) => update("weekly_time", e.target.value)}
            disabled={!config.weekly_enabled}
          />
        </div>
      </div>

      <div className="settings-action-row">
        <button
          type="button"
          className="settings-btn-primary"
          onClick={handleSave}
          disabled={saving || !isDirty()}
        >
          {saving ? "Saving..." : "Save"}
        </button>
      </div>
    </section>
  );
}
