export interface ApiKeyStatus {
  configured: boolean;
  masked: string | null;
}

export interface TestConnectionResult {
  ok: boolean;
  model?: string;
  latency_ms?: number;
  error?: string;
}

export interface ModelsConfig {
  default_tier: string;
  per_task: Record<string, string>;
}

export interface GraphStatus {
  mode: string;
  configured: boolean;
  cache_expires: string | null;
}

export interface ConnectorsConfig {
  onedrive_path: string | null;
  public_drive_path: string | null;
  sharepoint_sites: string | null;
}

export interface LintCadenceConfig {
  nightly_time: string;
  weekly_day: string;
  weekly_time: string;
  nightly_enabled: boolean;
  weekly_enabled: boolean;
}

export interface SettingsStatusEntry {
  ok: boolean;
  detail: string;
}

export interface SettingsStatus {
  api_key: SettingsStatusEntry;
  models: SettingsStatusEntry;
  graph: SettingsStatusEntry;
  connectors: SettingsStatusEntry;
  lint: SettingsStatusEntry;
}

export interface DeviceCodeFlowStart {
  task_id: string;
  user_code: string;
  verification_uri: string;
  expires_at: string;
}

export interface DeviceCodeStatus {
  status: "pending" | "complete" | "failed" | "timeout";
  cache_expires: string | null;
}
