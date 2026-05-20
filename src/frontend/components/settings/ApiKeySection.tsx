"use client";

import { useEffect, useRef, useState } from "react";
import type { ApiKeyStatus, TestConnectionResult } from "../../app/(tabs)/settings/types";

const API_KEY_REGEX = /^sk-ant-(api|admin)[0-9]{2}-[A-Za-z0-9_-]{60,}$/;

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

export default function ApiKeySection({ onDirtyChange }: Props) {
  const [keyValue, setKeyValue] = useState("");
  const [revealed, setRevealed] = useState(false);
  const [savedMasked, setSavedMasked] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<TestConnectionResult | null>(null);
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    fetchJSON<ApiKeyStatus>("/api/settings/anthropic-key")
      .then((s) => {
        if (s.configured && s.masked) {
          setSavedMasked(s.masked);
        }
      })
      .catch(() => {});
  }, []);

  function showToast(msg: string) {
    setToast(msg);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 4000);
  }

  function handleChange(value: string) {
    setKeyValue(value);
    setValidationError(null);
    setTestResult(null);
    onDirtyChange(value.trim().length > 0);
  }

  function handleBlur() {
    if (keyValue && !API_KEY_REGEX.test(keyValue)) {
      setValidationError("Key must match pattern sk-ant-(api|admin)##-<60+ chars>");
    }
  }

  async function handleTest() {
    setTesting(true);
    setTestResult(null);
    try {
      const body: Record<string, string> = {};
      if (keyValue) body.key = keyValue;
      const result = await fetchJSON<TestConnectionResult>("/api/settings/test-anthropic", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      setTestResult(result);
    } catch (e) {
      setTestResult({ ok: false, error: e instanceof Error ? e.message : String(e) });
    } finally {
      setTesting(false);
    }
  }

  async function handleSave() {
    if (!API_KEY_REGEX.test(keyValue)) {
      setValidationError("Key must match pattern sk-ant-(api|admin)##-<60+ chars>");
      return;
    }
    setSaving(true);
    try {
      const result = await fetchJSON<ApiKeyStatus>("/api/settings/anthropic-key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key: keyValue }),
      });
      setSavedMasked(result.masked);
      setKeyValue("");
      onDirtyChange(false);
      showToast("API key saved.");
    } catch (e) {
      showToast(`Save failed: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setSaving(false);
    }
  }

  const canSave = keyValue.length > 0 && !validationError && API_KEY_REGEX.test(keyValue);
  const canTest = keyValue.length > 0 || savedMasked !== null;
  const dirty = keyValue.trim().length > 0;

  return (
    <section id="api-key" className="settings-section">
      <h2 className="settings-section-title">
        Anthropic API key
        {dirty && <span className="settings-dirty-dot" aria-label="Unsaved changes" />}
      </h2>

      {toast && (
        <div className="settings-toast" role="status">
          {toast}
        </div>
      )}

      <div className="settings-field-group">
        <label className="settings-label" htmlFor="api-key-input">
          API key
        </label>
        <div className="settings-input-row">
          <input
            id="api-key-input"
            type={revealed ? "text" : "password"}
            className="settings-input"
            placeholder={savedMasked ?? "sk-ant-api03-..."}
            value={keyValue}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={handleBlur}
            autoComplete="off"
            spellCheck={false}
          />
          <button
            type="button"
            className="settings-icon-btn"
            onClick={() => setRevealed((v) => !v)}
            aria-label={revealed ? "Hide key" : "Reveal key"}
            title={revealed ? "Hide" : "Reveal"}
          >
            {revealed ? "Hide" : "Show"}
          </button>
        </div>
        {validationError && (
          <p className="settings-field-error">{validationError}</p>
        )}
        {savedMasked && !keyValue && (
          <p className="settings-field-hint">Currently saved: {savedMasked}</p>
        )}
      </div>

      <div className="settings-action-row">
        <button
          type="button"
          className="settings-btn-secondary"
          onClick={handleTest}
          disabled={testing || !canTest}
        >
          {testing ? "Testing..." : "Test connection"}
        </button>
        <button
          type="button"
          className="settings-btn-primary"
          onClick={handleSave}
          disabled={saving || !canSave}
        >
          {saving ? "Saving..." : "Save"}
        </button>
      </div>

      {testResult && (
        <div className={`settings-test-result ${testResult.ok ? "settings-test-ok" : "settings-test-fail"}`}>
          {testResult.ok
            ? `${testResult.model ?? "Model"} responded in ${testResult.latency_ms ?? "?"}ms`
            : `Error: ${testResult.error ?? "Unknown error"}`}
        </div>
      )}
    </section>
  );
}
