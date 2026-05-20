"use client";

import { useEffect, useRef, useState } from "react";
import type {
  DeviceCodeFlowStart,
  DeviceCodeStatus,
  GraphStatus,
} from "../../app/(tabs)/settings/types";

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

export default function GraphAuthSection({ onDirtyChange }: Props) {
  const [mode, setMode] = useState<"pasted" | "device-code">("device-code");
  const [savedMode, setSavedMode] = useState<string>("device-code");
  const [pastedToken, setPastedToken] = useState("");
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [deviceFlow, setDeviceFlow] = useState<DeviceCodeFlowStart | null>(null);
  const [deviceStatus, setDeviceStatus] = useState<DeviceCodeStatus | null>(null);
  const [launchingDevice, setLaunchingDevice] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [secondsLeft, setSecondsLeft] = useState(0);
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    fetchJSON<GraphStatus>("/api/settings/graph")
      .then((s) => {
        setMode(s.mode === "pasted" ? "pasted" : "device-code");
        setSavedMode(s.mode);
      })
      .catch(() => {});

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, []);

  function showToast(msg: string) {
    setToast(msg);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 4000);
  }

  function isDirty(): boolean {
    return mode !== savedMode || pastedToken.length > 0;
  }

  function handleModeChange(newMode: "pasted" | "device-code") {
    setMode(newMode);
    onDirtyChange(newMode !== savedMode || pastedToken.length > 0);
  }

  function handleTokenChange(value: string) {
    setPastedToken(value);
    onDirtyChange(mode !== savedMode || value.length > 0);
  }

  async function handleSaveToken() {
    if (!pastedToken.trim()) return;
    setSaving(true);
    try {
      await fetchJSON("/api/settings/graph-token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: pastedToken }),
      });
      setSavedMode("pasted");
      setPastedToken("");
      onDirtyChange(false);
      showToast("Graph token saved.");
    } catch (e) {
      showToast(`Save failed: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setSaving(false);
    }
  }

  function stopPolling() {
    if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
    if (countdownRef.current) { clearInterval(countdownRef.current); countdownRef.current = null; }
  }

  function closeModal() {
    stopPolling();
    setDeviceFlow(null);
    setDeviceStatus(null);
  }

  async function handleStartDeviceCode() {
    setLaunchingDevice(true);
    try {
      const flow = await fetchJSON<DeviceCodeFlowStart>("/api/settings/start-device-code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      setDeviceFlow(flow);
      setDeviceStatus(null);

      const expiresAt = new Date(flow.expires_at).getTime();
      function updateCountdown() {
        setSecondsLeft(Math.max(0, Math.round((expiresAt - Date.now()) / 1000)));
      }
      updateCountdown();
      countdownRef.current = setInterval(updateCountdown, 1000);

      pollRef.current = setInterval(async () => {
        try {
          const s = await fetchJSON<DeviceCodeStatus>(
            `/api/settings/device-code-status?task_id=${flow.task_id}`
          );
          setDeviceStatus(s);
          if (s.status === "complete") {
            stopPolling();
            setSavedMode("device-code");
            onDirtyChange(false);
            setTimeout(() => closeModal(), 3000);
          } else if (s.status === "failed" || s.status === "timeout") {
            stopPolling();
          }
        } catch {
          // non-fatal poll error
        }
      }, 2000);
    } catch (e) {
      showToast(`Could not start device-code flow: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setLaunchingDevice(false);
    }
  }

  return (
    <section id="graph" className="settings-section">
      <h2 className="settings-section-title">
        MS Graph authentication
        {isDirty() && <span className="settings-dirty-dot" aria-label="Unsaved changes" />}
      </h2>

      {toast && (
        <div className="settings-toast" role="status">
          {toast}
        </div>
      )}

      <div className="settings-field-group">
        <fieldset className="settings-fieldset">
          <legend className="settings-label">Auth mode</legend>
          <div className="settings-radio-group">
            <label className="settings-radio-label">
              <input
                type="radio"
                name="graph-auth-mode"
                value="pasted"
                checked={mode === "pasted"}
                onChange={() => handleModeChange("pasted")}
                className="settings-radio"
              />
              <span className="settings-radio-text">
                <strong>Pasted token (Path A)</strong>
                <span className="settings-radio-desc">Short-lived, ~60 min.</span>
              </span>
            </label>
            <label className="settings-radio-label">
              <input
                type="radio"
                name="graph-auth-mode"
                value="device-code"
                checked={mode === "device-code"}
                onChange={() => handleModeChange("device-code")}
                className="settings-radio"
              />
              <span className="settings-radio-text">
                <strong>Device-code login (Path B)</strong>
                <span className="settings-radio-desc">Long-lived, ~90 days.</span>
              </span>
            </label>
          </div>
        </fieldset>
      </div>

      {mode === "pasted" && (
        <div className="settings-field-group">
          <label className="settings-label" htmlFor="graph-token-input">
            Access token
          </label>
          <textarea
            id="graph-token-input"
            className="settings-textarea"
            placeholder="eyJ..."
            value={pastedToken}
            onChange={(e) => handleTokenChange(e.target.value)}
            rows={4}
            spellCheck={false}
            autoComplete="off"
          />
          <div className="settings-action-row">
            <button
              type="button"
              className="settings-btn-primary"
              onClick={handleSaveToken}
              disabled={saving || !pastedToken.trim()}
            >
              {saving ? "Saving..." : "Save token"}
            </button>
          </div>
        </div>
      )}

      {mode === "device-code" && (
        <div className="settings-field-group">
          <button
            type="button"
            className="settings-btn-secondary"
            onClick={handleStartDeviceCode}
            disabled={launchingDevice}
          >
            {launchingDevice ? "Starting..." : "Run device-code login"}
          </button>
        </div>
      )}

      <details className="settings-advanced">
        <summary className="settings-advanced-summary">Advanced (Tenant / Client IDs)</summary>
        <div className="settings-field-group settings-advanced-body">
          <label className="settings-label" htmlFor="graph-tenant-id">
            Tenant ID
          </label>
          <input
            id="graph-tenant-id"
            type="text"
            className="settings-input"
            defaultValue="1c966021-d551-45e4-89a5-849f81b69208"
            spellCheck={false}
          />
          <label className="settings-label" htmlFor="graph-client-id" style={{ marginTop: "0.75rem" }}>
            Client ID
          </label>
          <input
            id="graph-client-id"
            type="text"
            className="settings-input"
            defaultValue="14d82eec-204b-4c2f-b7e8-296a70dab67e"
            spellCheck={false}
          />
        </div>
      </details>

      {deviceFlow && (
        <div className="settings-modal-overlay" role="dialog" aria-modal="true">
          <div className="settings-modal">
            <h3 className="settings-modal-title">Device code login</h3>

            {(!deviceStatus || deviceStatus.status === "pending") && (
              <>
                <p className="settings-modal-body">
                  Open <a href={deviceFlow.verification_uri} target="_blank" rel="noopener noreferrer" className="settings-link">{deviceFlow.verification_uri}</a> and enter:
                </p>
                <p className="settings-device-code">{deviceFlow.user_code}</p>
                <p className="settings-modal-hint">
                  Expires in {secondsLeft}s
                </p>
              </>
            )}

            {deviceStatus?.status === "complete" && (
              <p className="settings-modal-success">
                Login complete
                {deviceStatus.cache_expires ? ` — cache valid until ${new Date(deviceStatus.cache_expires).toLocaleDateString()}` : ""}
                . Closing...
              </p>
            )}

            {(deviceStatus?.status === "failed" || deviceStatus?.status === "timeout") && (
              <p className="settings-modal-error">
                {deviceStatus.status === "timeout" ? "Device code expired." : "Login failed."}
              </p>
            )}

            <button
              type="button"
              className="settings-btn-secondary"
              onClick={closeModal}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
