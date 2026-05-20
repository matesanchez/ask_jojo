"use client";

import { useEffect, useState } from "react";
import type { ModelsConfig } from "../../app/(tabs)/settings/types";

const TIERS = [
  { value: "haiku-4-5", label: "Haiku 4.5", description: "Fastest, cheapest. Best for routing and simple queries." },
  { value: "sonnet-4-6", label: "Sonnet 4.6", description: "Balanced. Default for Q&A synthesis." },
  { value: "opus-4-6", label: "Opus 4.6", description: "Highest quality. Best for contradiction checks and complex syntheses. Most expensive." },
];

const TASKS = [
  { key: "synthesis", label: "synthesis" },
  { key: "nightly-lint", label: "nightly-lint" },
  { key: "weekly-contradiction", label: "weekly-contradiction" },
  { key: "compile-absorb", label: "compile-absorb" },
  { key: "format-classify", label: "format-classify" },
];

const DEFAULT_PER_TASK: Record<string, string> = {
  synthesis: "sonnet-4-6",
  "nightly-lint": "sonnet-4-6",
  "weekly-contradiction": "opus-4-6",
  "compile-absorb": "sonnet-4-6",
  "format-classify": "haiku-4-5",
};

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, { cache: "no-store", ...init });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`${r.status} ${r.statusText}${text ? ` — ${text}` : ""}`);
  }
  return r.json() as Promise<T>;
}

interface Props {
  onDirtyChange: (dirty: boolean) => void;
}

export default function ModelsSection({ onDirtyChange }: Props) {
  const [config, setConfig] = useState<ModelsConfig>({
    default_tier: "sonnet-4-6",
    per_task: { ...DEFAULT_PER_TASK },
  });
  const [saved, setSaved] = useState<ModelsConfig>({
    default_tier: "sonnet-4-6",
    per_task: { ...DEFAULT_PER_TASK },
  });
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    fetchJSON<ModelsConfig>("/api/settings/models")
      .then((c) => {
        setConfig(c);
        setSaved(c);
      })
      .catch(() => {});
  }, []);

  function isDirty(): boolean {
    if (config.default_tier !== saved.default_tier) return true;
    for (const t of TASKS) {
      if ((config.per_task[t.key] ?? "") !== (saved.per_task[t.key] ?? "")) return true;
    }
    return false;
  }

  function setDefaultTier(tier: string) {
    const next = { ...config, default_tier: tier };
    setConfig(next);
    onDirtyChange(next.default_tier !== saved.default_tier || TASKS.some((t) => (next.per_task[t.key] ?? "") !== (saved.per_task[t.key] ?? "")));
  }

  function setPerTask(key: string, value: string) {
    const next = { ...config, per_task: { ...config.per_task, [key]: value } };
    setConfig(next);
    onDirtyChange(next.default_tier !== saved.default_tier || TASKS.some((t) => (next.per_task[t.key] ?? "") !== (saved.per_task[t.key] ?? "")));
  }

  async function handleSave() {
    setSaving(true);
    try {
      await fetchJSON<ModelsConfig>("/api/settings/models", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      setSaved({ ...config, per_task: { ...config.per_task } });
      onDirtyChange(false);
      setToast("Model settings saved.");
      setTimeout(() => setToast(null), 4000);
    } catch (e) {
      setToast(`Save failed: ${e instanceof Error ? e.message : String(e)}`);
      setTimeout(() => setToast(null), 4000);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section id="models" className="settings-section">
      <h2 className="settings-section-title">
        Model tier
        {isDirty() && <span className="settings-dirty-dot" aria-label="Unsaved changes" />}
      </h2>

      {toast && (
        <div className="settings-toast" role="status">
          {toast}
        </div>
      )}

      <div className="settings-field-group">
        <fieldset className="settings-fieldset">
          <legend className="settings-label">Default tier</legend>
          <div className="settings-radio-group">
            {TIERS.map((t) => (
              <label key={t.value} className="settings-radio-label">
                <input
                  type="radio"
                  name="default-tier"
                  value={t.value}
                  checked={config.default_tier === t.value}
                  onChange={() => setDefaultTier(t.value)}
                  className="settings-radio"
                />
                <span className="settings-radio-text">
                  <strong>{t.label}</strong>
                  <span className="settings-radio-desc">{t.description}</span>
                </span>
              </label>
            ))}
          </div>
        </fieldset>
      </div>

      <div className="settings-field-group">
        <p className="settings-label">Per-task overrides</p>
        <table className="settings-table">
          <thead>
            <tr>
              <th className="settings-th">Task</th>
              <th className="settings-th">Model</th>
            </tr>
          </thead>
          <tbody>
            {TASKS.map((task) => (
              <tr key={task.key} className="settings-tr">
                <td className="settings-td">
                  <code>{task.label}</code>
                </td>
                <td className="settings-td">
                  <select
                    className="settings-select"
                    value={config.per_task[task.key] ?? DEFAULT_PER_TASK[task.key]}
                    onChange={(e) => setPerTask(task.key, e.target.value)}
                  >
                    {TIERS.map((t) => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
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
