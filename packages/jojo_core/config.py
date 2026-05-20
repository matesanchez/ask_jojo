"""DPAPI-encrypted config loader for JoJo Bot.

Stores secrets and operational config at ``%APPDATA%\\JojoBot\\config.json``
on Windows (encrypted with DPAPI under the current user's scope) and at
``~/.config/JojoBot/config.json`` on other platforms (plaintext -- DPAPI
is Windows-only and we don't want to add a crypto dep to the dev install
just to keep the loader tests green).

This module has *zero* external runtime dependencies. DPAPI is invoked via
``ctypes`` against ``crypt32.dll`` rather than pywin32, so we don't bloat
the dev extras.

Design notes
------------
- Every stored key has a matching environment variable (see ``ENV_MAP``),
  so existing callers can keep reading from env while production flips
  over to config.json one key at a time. ``get()`` does config -> env ->
  default without the caller knowing or caring.
- Writes are atomic (rename-into-place) so a crash mid-save can't leave
  a half-written config.
- The envelope wraps the payload with an ``encryption`` field so we can
  migrate between modes later (e.g., add a ``keyring`` mode on macOS)
  without breaking old files.

See ``ADR 0004`` and ``ADR 0009`` for the rationale.
"""

from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path
from typing import Any

# -- public key names ------------------------------------------------------
# Every key stored in config.json also has a matching environment variable.
# Callers should use these constants rather than hardcoding names so a
# rename touches exactly one spot.
KEY_ANTHROPIC_API_KEY = "anthropic_api_key"
KEY_GRAPH_ACCESS_TOKEN = "graph_access_token"
KEY_SHAREPOINT_SITES = "sharepoint_sites"
KEY_ONEDRIVE_PATH = "onedrive_path"
KEY_PUBLIC_DRIVE_PATH = "public_drive_path"
KEY_RAW_ROOT = "raw_root"
KEY_UPLOAD_DIR = "upload_dir"
KEY_REDIS_URL = "redis_url"
KEY_MSAL_CLIENT_ID = "msal_client_id"
KEY_MSAL_TENANT_ID = "msal_tenant_id"
KEY_GRAPH_AUTH_MODE = "graph_auth_mode"
KEY_MODEL_DEFAULT_TIER = "model_default_tier"
KEY_MODEL_PER_TASK = "model_per_task"
KEY_LINT_NIGHTLY_TIME = "lint_nightly_time"
KEY_LINT_WEEKLY_DAY = "lint_weekly_day"
KEY_LINT_WEEKLY_TIME = "lint_weekly_time"
KEY_LINT_NIGHTLY_ENABLED = "lint_nightly_enabled"
KEY_LINT_WEEKLY_ENABLED = "lint_weekly_enabled"
KEY_FINETUNE_WIKI_ROOT = "finetune_wiki_root"
KEY_FINETUNE_DATASET_PATH = "finetune_dataset_path"
KEY_FINETUNE_BENCHMARK_PATH = "finetune_benchmark_path"
KEY_FINETUNE_BACKEND = "finetune_backend"

ENV_MAP: dict[str, str] = {
    KEY_ANTHROPIC_API_KEY:  "ANTHROPIC_API_KEY",
    KEY_GRAPH_ACCESS_TOKEN: "JOJO_GRAPH_ACCESS_TOKEN",
    KEY_SHAREPOINT_SITES:   "JOJO_SHAREPOINT_SITES",
    KEY_ONEDRIVE_PATH:      "JOJO_ONEDRIVE_PATH",
    KEY_PUBLIC_DRIVE_PATH:  "JOJO_PUBLIC_DRIVE_PATH",
    KEY_RAW_ROOT:           "JOJO_RAW_ROOT",
    KEY_UPLOAD_DIR:         "JOJO_UPLOAD_DIR",
    KEY_REDIS_URL:          "JOJO_REDIS_URL",
    KEY_MSAL_CLIENT_ID:     "JOJO_MSAL_CLIENT_ID",
    KEY_MSAL_TENANT_ID:     "JOJO_MSAL_TENANT_ID",
    KEY_GRAPH_AUTH_MODE:    "JOJO_GRAPH_AUTH_MODE",
    KEY_MODEL_DEFAULT_TIER:  "JOJO_MODEL_DEFAULT_TIER",
    KEY_MODEL_PER_TASK:      "JOJO_MODEL_PER_TASK",
    KEY_LINT_NIGHTLY_TIME:   "JOJO_LINT_NIGHTLY_TIME",
    KEY_LINT_WEEKLY_DAY:     "JOJO_LINT_WEEKLY_DAY",
    KEY_LINT_WEEKLY_TIME:    "JOJO_LINT_WEEKLY_TIME",
    KEY_LINT_NIGHTLY_ENABLED:   "JOJO_LINT_NIGHTLY_ENABLED",
    KEY_LINT_WEEKLY_ENABLED:    "JOJO_LINT_WEEKLY_ENABLED",
    KEY_FINETUNE_WIKI_ROOT:     "JOJO_FINETUNE_WIKI_ROOT",
    KEY_FINETUNE_DATASET_PATH:  "JOJO_FINETUNE_DATASET_PATH",
    KEY_FINETUNE_BENCHMARK_PATH: "JOJO_FINETUNE_BENCHMARK_PATH",
    KEY_FINETUNE_BACKEND:       "JOJO_FINETUNE_BACKEND",
}

# Which keys carry real secrets vs. operational config. Used to mask
# values in ``show`` and to warn when writing a secret on a platform
# without DPAPI.
SECRET_KEYS: frozenset[str] = frozenset({
    KEY_ANTHROPIC_API_KEY,
    KEY_GRAPH_ACCESS_TOKEN,
})

# Hard-coded defaults for operational config. These are the Nurix well-known
# app registration IDs and the default auth mode. They are baked in so that a
# fresh install works without any config.json or env vars. Callers that need
# the value for a specific key can use `get()`, which checks config.json and
# env vars first and falls through to this dict last.
DEFAULTS: dict[str, str] = {
    KEY_MSAL_CLIENT_ID: "14d82eec-204b-4c2f-b7e8-296a70dab67e",
    KEY_MSAL_TENANT_ID: "1c966021-d551-45e4-89a5-849f81b69208",
    KEY_GRAPH_AUTH_MODE: "device-code",
    KEY_MODEL_DEFAULT_TIER:   "sonnet",
    KEY_LINT_NIGHTLY_TIME:    "02:00",
    KEY_LINT_WEEKLY_DAY:      "Sunday",
    KEY_LINT_WEEKLY_TIME:     "04:00",
    KEY_LINT_NIGHTLY_ENABLED: "true",
    KEY_LINT_WEEKLY_ENABLED:  "true",
    KEY_FINETUNE_BACKEND:     "dry-run",
}

# File-format version. Bump when changing the envelope schema (not the
# payload keys -- those can be added freely).
_FILE_VERSION = 1
_APP_DIR_NAME = "JojoBot"
_CONFIG_FILENAME = "config.json"

# Test hook -- when set, all path logic resolves to this path instead of
# the real %APPDATA% / ~/.config location.
_override_path: Path | None = None


class ConfigError(RuntimeError):
    """Raised for malformed config files or DPAPI failures."""


# -- path resolution -------------------------------------------------------
def config_path() -> Path:
    """Return the canonical config.json location for this platform.

    Resolution order:
      1. in-process override (``set_config_path_for_tests``)
      2. ``JOJO_CONFIG_PATH`` env var (for advanced operators running
         multiple configs, e.g. dev vs. prod on the same laptop)
      3. ``%APPDATA%\\JojoBot\\config.json`` on Windows
      4. ``$XDG_CONFIG_HOME/JojoBot/config.json`` or
         ``~/.config/JojoBot/config.json`` elsewhere
    """
    if _override_path is not None:
        return _override_path
    env_override = os.environ.get("JOJO_CONFIG_PATH")
    if env_override:
        return Path(env_override)
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / _APP_DIR_NAME / _CONFIG_FILENAME


def set_config_path_for_tests(path: Path | None) -> None:
    """Redirect all config I/O to an arbitrary path. Tests only."""
    global _override_path
    _override_path = path


# -- DPAPI (Windows-only) --------------------------------------------------
# These are imported lazily and guarded by ``_use_dpapi()`` so that
# importing this module on Linux/macOS doesn't pull wintypes at all.

def _dpapi_protect(plaintext: bytes) -> bytes:
    """Encrypt ``plaintext`` under the current user's DPAPI scope."""
    import ctypes
    from ctypes import wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [
            ("cbData", wintypes.DWORD),
            ("pbData", ctypes.POINTER(ctypes.c_char)),
        ]

    in_blob = DATA_BLOB(
        len(plaintext),
        ctypes.cast(ctypes.c_char_p(plaintext), ctypes.POINTER(ctypes.c_char)),
    )
    out_blob = DATA_BLOB()
    crypt32 = ctypes.windll.crypt32  # type: ignore[attr-defined]
    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
    ok = crypt32.CryptProtectData(
        ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)
    )
    if not ok:
        raise ConfigError(f"CryptProtectData failed (GetLastError={ctypes.GetLastError()})")
    try:
        return ctypes.string_at(out_blob.pbData, out_blob.cbData)
    finally:
        kernel32.LocalFree(out_blob.pbData)


def _dpapi_unprotect(ciphertext: bytes) -> bytes:
    """Decrypt ``ciphertext`` under the current user's DPAPI scope."""
    import ctypes
    from ctypes import wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [
            ("cbData", wintypes.DWORD),
            ("pbData", ctypes.POINTER(ctypes.c_char)),
        ]

    in_blob = DATA_BLOB(
        len(ciphertext),
        ctypes.cast(ctypes.c_char_p(ciphertext), ctypes.POINTER(ctypes.c_char)),
    )
    out_blob = DATA_BLOB()
    crypt32 = ctypes.windll.crypt32  # type: ignore[attr-defined]
    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
    ok = crypt32.CryptUnprotectData(
        ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)
    )
    if not ok:
        raise ConfigError(
            "CryptUnprotectData failed -- wrong Windows user, or the file is "
            "corrupt. DPAPI ciphertext is bound to the user that encrypted it."
        )
    try:
        return ctypes.string_at(out_blob.pbData, out_blob.cbData)
    finally:
        kernel32.LocalFree(out_blob.pbData)


def _use_dpapi() -> bool:
    """Return True when writes should be DPAPI-encrypted.

    ``JOJO_CONFIG_FORCE_PLAINTEXT=1`` disables DPAPI even on Windows -- useful
    for tests and for operators who want to inspect the file contents.
    """
    if os.environ.get("JOJO_CONFIG_FORCE_PLAINTEXT") == "1":
        return False
    return sys.platform == "win32"


# -- file IO ---------------------------------------------------------------
def load() -> dict[str, Any]:
    """Load and return the config as a dict. Returns ``{}`` if no file exists.

    Raises ``ConfigError`` on malformed JSON, unknown envelope mode, or DPAPI
    decryption failure.
    """
    path = config_path()
    if not path.exists():
        return {}
    try:
        raw = path.read_text(encoding="utf-8")
        envelope = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        raise ConfigError(f"Could not read config at {path}: {e}") from e
    encryption = envelope.get("encryption")
    payload = envelope.get("payload")
    if encryption == "plaintext":
        return payload if isinstance(payload, dict) else {}
    if encryption == "dpapi":
        if not isinstance(payload, str):
            raise ConfigError("dpapi-encrypted config file has a non-string payload")
        plaintext = _dpapi_unprotect(base64.b64decode(payload))
        data = json.loads(plaintext.decode("utf-8"))
        if not isinstance(data, dict):
            raise ConfigError("decrypted dpapi payload is not a JSON object")
        return data
    raise ConfigError(f"Unknown encryption mode: {encryption!r}")


def save(data: dict[str, Any]) -> None:
    """Atomic write of ``data`` to the config file.

    Uses DPAPI on Windows (unless ``JOJO_CONFIG_FORCE_PLAINTEXT=1`` is set)
    and plaintext JSON elsewhere. The parent directory is created if it
    doesn't exist.
    """
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if _use_dpapi():
        ciphertext = _dpapi_protect(json.dumps(data).encode("utf-8"))
        envelope: dict[str, Any] = {
            "version": _FILE_VERSION,
            "encryption": "dpapi",
            "payload": base64.b64encode(ciphertext).decode("ascii"),
        }
    else:
        envelope = {
            "version": _FILE_VERSION,
            "encryption": "plaintext",
            "_warning": (
                "Plaintext: DPAPI not available on this platform. "
                "Keep this file out of version control and shared drives."
            ),
            "payload": data,
        }
    # Atomic write -- ``os.replace`` is atomic on NTFS, ext4, and APFS, so
    # a crash mid-save can never leave a half-written file.
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
    os.replace(tmp, path)


# -- accessors -------------------------------------------------------------
def get(key: str, default: Any = None, *, env_fallback: bool = True) -> Any:
    """Return the value for ``key``.

    Resolution order:
      1. ``config.json`` if the key is present and non-null.
      2. ``ENV_MAP[key]`` environment variable (when ``env_fallback=True``).
      3. ``default``.

    Env fallback can be disabled for strict reads (e.g., "only trust the
    config file, don't let a stale env var sneak in during a scheduled run").
    """
    data = load()
    if key in data and data[key] is not None:
        return data[key]
    if env_fallback:
        env_name = ENV_MAP.get(key)
        if env_name:
            val = os.environ.get(env_name)
            if val:
                return val
    defaults_val = DEFAULTS.get(key)
    if defaults_val is not None:
        return defaults_val
    return default


def set(key: str, value: Any) -> None:  # noqa: A001 -- module-scoped, never shadows builtin in callers
    """Write ``key = value`` to config.json."""
    data = load()
    data[key] = value
    save(data)


def delete(key: str) -> bool:
    """Remove ``key`` from config.json. Returns True if removed, False if absent."""
    data = load()
    if key in data:
        del data[key]
        save(data)
        return True
    return False


def migrate_from_env(*, overwrite: bool = False) -> list[str]:
    """Copy every ``ENV_MAP`` env var set in the current environment into
    config.json. Returns the list of keys migrated.

    With ``overwrite=False`` (the default), keys already present in config
    are left alone -- re-running is safe.
    """
    data = load()
    migrated: list[str] = []
    for key, env_name in ENV_MAP.items():
        env_val = os.environ.get(env_name)
        if not env_val:
            continue
        if key in data and not overwrite:
            continue
        data[key] = env_val
        migrated.append(key)
    if migrated:
        save(data)
    return migrated


def mask(value: Any) -> str:
    """Mask a secret for display: first 3 + last 3 chars with length."""
    if value is None:
        return ""
    s = str(value)
    if len(s) <= 8:
        return "*" * len(s)
    return f"{s[:3]}...{s[-3:]} ({len(s)} chars)"
