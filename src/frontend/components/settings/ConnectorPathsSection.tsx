"use client";

import { useEffect, useRef, useState } from "react";
import type { ConnectorsConfig } from "../../app/(tabs)/settings/types";

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

export default function ConnectorPathsSection({ onDirtyChange }: Props) {
  const [onedrivePath, setOnedrivePath] = useState("");
  const [publicDrivePath, setPublicDrivePath] = useState("");
  const [sharepointSites, setSharepointSites] = useState("");
  const [saved, setSaved] = useState<ConnectorsConfig>({
    onedrive_path: null,
    public_drive_path: null,
    sharepoint_sites: null,
  });
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    fetchJSON<ConnectorsConfig>("/api/settings/connectors")
      .then((c) => {
        setOnedrivePath(c.onedrive_path ?? "");
        setPublicDrivePath(c.public_drive_path ?? "");
        setSharepointSites(c.sharepoint_sites ?? "");
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
      onedrivePath !== (saved.onedrive_path ?? "") ||
      publicDrivePath !== (saved.public_drive_path ?? "") ||
      sharepointSites !== (saved.sharepoint_sites ?? "")
    );
  }

  function notifyDirty(od: string, pd: string, sp: string) {
    onDirtyChange(
      od !== (saved.onedrive_path ?? "") ||
      pd !== (saved.public_drive_path ?? "") ||
      sp !== (saved.sharepoint_sites ?? "")
    );
  }

  async function handleSave() {
    setSaving(true);
    try {
      const payload: ConnectorsConfig = {
        onedrive_path: onedrivePath || null,
        public_drive_path: publicDrivePath || null,
        sharepoint_sites: sharepointSites || null,
      };
      await fetchJSON<ConnectorsConfig>("/api/settings/connectors", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setSaved(payload);
      onDirtyChange(false);
      showToast("Connector paths saved.");
    } catch (e) {
      showToast(`Save failed: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section id="connectors" className="settings-section">
      <h2 className="settings-section-title">
        Connector paths
        {isDirty() && <span className="settings-dirty-dot" aria-label="Unsaved changes" />}
      </h2>

      {toast && (
        <div className="settings-toast" role="status">
          {toast}
        </div>
      )}

      <div className="settings-field-group">
        <label className="settings-label" htmlFor="onedrive-path">
          OneDrive sync path
        </label>
        <input
          id="onedrive-path"
          type="text"
          className="settings-input"
          placeholder="C:\Users\...\OneDrive - Nurix Therapeutics"
          value={onedrivePath}
          onChange={(e) => {
            setOnedrivePath(e.target.value);
            notifyDirty(e.target.value, publicDrivePath, sharepointSites);
          }}
          spellCheck={false}
        />
      </div>

      <div className="settings-field-group">
        <label className="settings-label" htmlFor="public-drive-path">
          Public drive path
        </label>
        <input
          id="public-drive-path"
          type="text"
          className="settings-input"
          placeholder="P:\"
          value={publicDrivePath}
          onChange={(e) => {
            setPublicDrivePath(e.target.value);
            notifyDirty(onedrivePath, e.target.value, sharepointSites);
          }}
          spellCheck={false}
        />
      </div>

      <div className="settings-field-group">
        <label className="settings-label" htmlFor="sharepoint-sites">
          SharePoint sites (one URL per line)
        </label>
        <textarea
          id="sharepoint-sites"
          className="settings-textarea"
          placeholder={"https://nurixtx.sharepoint.com/sites/..."}
          value={sharepointSites}
          onChange={(e) => {
            setSharepointSites(e.target.value);
            notifyDirty(onedrivePath, publicDrivePath, e.target.value);
          }}
          rows={4}
          spellCheck={false}
        />
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
