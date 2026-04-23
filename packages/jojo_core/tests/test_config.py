"""Tests for jojo_core.config.

Most tests run in plaintext mode (forced via ``JOJO_CONFIG_FORCE_PLAINTEXT``)
since DPAPI is Windows-only and CI runs on Linux. A separate suite of tests
monkey-patches the DPAPI primitives so we can still exercise the Windows
code path on Linux CI.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

from jojo_core import config


@pytest.fixture(autouse=True)
def _isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Point every test at a fresh config.json under tmp_path and force
    plaintext mode so the tests are deterministic regardless of host OS.
    """
    cfg = tmp_path / "config.json"
    config.set_config_path_for_tests(cfg)
    monkeypatch.setenv("JOJO_CONFIG_FORCE_PLAINTEXT", "1")
    # Strip any ambient JOJO_* env vars that would leak into get()/migrate().
    for env_name in config.ENV_MAP.values():
        monkeypatch.delenv(env_name, raising=False)
    yield
    config.set_config_path_for_tests(None)


# ---- path resolution -----------------------------------------------------
def test_config_path_honors_override(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "config.json"
    config.set_config_path_for_tests(target)
    assert config.config_path() == target


def test_config_path_from_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config.set_config_path_for_tests(None)
    monkeypatch.setenv("JOJO_CONFIG_PATH", str(tmp_path / "override.json"))
    assert config.config_path() == tmp_path / "override.json"


# ---- load / save round trips --------------------------------------------
def test_load_missing_file_returns_empty_dict() -> None:
    assert config.load() == {}


def test_save_then_load_round_trips() -> None:
    data = {config.KEY_RAW_ROOT: "/some/path", config.KEY_REDIS_URL: "redis://x"}
    config.save(data)
    assert config.load() == data


def test_save_is_atomic(tmp_path: Path) -> None:
    # After a successful save, no stale .tmp sibling should remain.
    config.save({config.KEY_RAW_ROOT: "/x"})
    siblings = list(tmp_path.glob("config.json*"))
    assert [p.name for p in siblings] == ["config.json"]


def test_plaintext_envelope_schema() -> None:
    config.save({config.KEY_RAW_ROOT: "/x"})
    envelope = json.loads(config.config_path().read_text())
    assert envelope["version"] == 1
    assert envelope["encryption"] == "plaintext"
    assert envelope["payload"] == {config.KEY_RAW_ROOT: "/x"}
    # Plaintext files carry an explicit warning so anyone reading them
    # knows they shouldn't be committed.
    assert "_warning" in envelope


def test_load_raises_on_malformed_json() -> None:
    config.config_path().parent.mkdir(parents=True, exist_ok=True)
    config.config_path().write_text("{not valid json")
    with pytest.raises(config.ConfigError):
        config.load()


def test_load_raises_on_unknown_encryption_mode() -> None:
    path = config.config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": 1, "encryption": "rot13", "payload": {}}))
    with pytest.raises(config.ConfigError, match="Unknown encryption"):
        config.load()


# ---- accessors -----------------------------------------------------------
def test_get_returns_default_when_key_missing() -> None:
    assert config.get(config.KEY_RAW_ROOT, default="fallback") == "fallback"


def test_get_prefers_config_over_env(monkeypatch: pytest.MonkeyPatch) -> None:
    config.save({config.KEY_RAW_ROOT: "from-config"})
    monkeypatch.setenv("JOJO_RAW_ROOT", "from-env")
    assert config.get(config.KEY_RAW_ROOT) == "from-config"


def test_get_falls_back_to_env_when_config_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JOJO_RAW_ROOT", "from-env")
    assert config.get(config.KEY_RAW_ROOT) == "from-env"


def test_get_env_fallback_can_be_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JOJO_RAW_ROOT", "from-env")
    assert config.get(config.KEY_RAW_ROOT, env_fallback=False) is None


def test_get_null_config_value_falls_through_to_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # A null value stored in config should not suppress the env fallback --
    # null means "not configured", not "explicitly disabled".
    config.save({config.KEY_RAW_ROOT: None})
    monkeypatch.setenv("JOJO_RAW_ROOT", "from-env")
    assert config.get(config.KEY_RAW_ROOT) == "from-env"


def test_set_creates_file_and_stores_value() -> None:
    config.set(config.KEY_RAW_ROOT, "/x")
    assert config.load() == {config.KEY_RAW_ROOT: "/x"}


def test_set_preserves_existing_keys() -> None:
    config.set(config.KEY_RAW_ROOT, "/x")
    config.set(config.KEY_REDIS_URL, "redis://r")
    assert config.load() == {
        config.KEY_RAW_ROOT: "/x",
        config.KEY_REDIS_URL: "redis://r",
    }


def test_delete_existing_key_returns_true() -> None:
    config.set(config.KEY_RAW_ROOT, "/x")
    assert config.delete(config.KEY_RAW_ROOT) is True
    assert config.load() == {}


def test_delete_missing_key_returns_false() -> None:
    assert config.delete(config.KEY_RAW_ROOT) is False


# ---- migrate_from_env ----------------------------------------------------
def test_migrate_from_env_pulls_all_set_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JOJO_RAW_ROOT", "/raw")
    monkeypatch.setenv("JOJO_REDIS_URL", "redis://r")
    migrated = config.migrate_from_env()
    assert set(migrated) == {config.KEY_RAW_ROOT, config.KEY_REDIS_URL}
    data = config.load()
    assert data[config.KEY_RAW_ROOT] == "/raw"
    assert data[config.KEY_REDIS_URL] == "redis://r"


def test_migrate_from_env_skips_existing_keys_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config.save({config.KEY_RAW_ROOT: "/already-set"})
    monkeypatch.setenv("JOJO_RAW_ROOT", "/env-value")
    migrated = config.migrate_from_env()
    assert migrated == []
    assert config.get(config.KEY_RAW_ROOT) == "/already-set"


def test_migrate_from_env_overwrite_true(monkeypatch: pytest.MonkeyPatch) -> None:
    config.save({config.KEY_RAW_ROOT: "/already-set"})
    monkeypatch.setenv("JOJO_RAW_ROOT", "/env-value")
    migrated = config.migrate_from_env(overwrite=True)
    assert migrated == [config.KEY_RAW_ROOT]
    assert config.get(config.KEY_RAW_ROOT) == "/env-value"


def test_migrate_from_env_no_vars_set_writes_nothing() -> None:
    # The env fixture already stripped every JOJO_* var, so this is a clean
    # no-op invocation. The config file should not be created.
    migrated = config.migrate_from_env()
    assert migrated == []
    assert not config.config_path().exists()


# ---- mask ----------------------------------------------------------------
def test_mask_long_secret_shows_head_tail_and_length() -> None:
    m = config.mask("abcdefghijklmnop")
    assert m == "abc...nop (16 chars)"


def test_mask_short_secret_is_all_asterisks() -> None:
    assert config.mask("short") == "*****"


def test_mask_none_returns_empty_string() -> None:
    assert config.mask(None) == ""


# ---- DPAPI path (via monkeypatched primitives) --------------------------
class _FakeDpapi:
    """Minimal fake: 'encrypt' with a reversible transform so we can prove
    the load/save code path goes through _dpapi_protect/_unprotect on the
    Windows branch, without actually needing Windows.
    """

    @staticmethod
    def protect(plaintext: bytes) -> bytes:
        # Trivial "encryption": reverse the bytes. Not remotely secure --
        # it's a stand-in for DPAPI's ciphertext so the round-trip works.
        return plaintext[::-1]

    @staticmethod
    def unprotect(ciphertext: bytes) -> bytes:
        return ciphertext[::-1]


def test_dpapi_path_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force the dpapi branch on a non-Windows host and confirm load/save
    flow data through ``_dpapi_protect``/``_dpapi_unprotect``."""
    monkeypatch.delenv("JOJO_CONFIG_FORCE_PLAINTEXT", raising=False)
    monkeypatch.setattr(config, "_use_dpapi", lambda: True)
    monkeypatch.setattr(config, "_dpapi_protect", _FakeDpapi.protect)
    monkeypatch.setattr(config, "_dpapi_unprotect", _FakeDpapi.unprotect)

    data = {config.KEY_ANTHROPIC_API_KEY: "sk-ant-xxxxxxx"}
    config.save(data)

    # On disk the envelope should declare dpapi + have a base64 string payload
    envelope = json.loads(config.config_path().read_text())
    assert envelope["encryption"] == "dpapi"
    assert isinstance(envelope["payload"], str)
    # The payload must be valid base64 (decoding doesn't raise).
    base64.b64decode(envelope["payload"])

    assert config.load() == data


def test_dpapi_load_rejects_non_string_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    path = config.config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"version": 1, "encryption": "dpapi", "payload": {"not": "a string"}})
    )
    with pytest.raises(config.ConfigError, match="non-string payload"):
        config.load()


def test_force_plaintext_env_var_overrides_dpapi(monkeypatch: pytest.MonkeyPatch) -> None:
    # Confirm the escape hatch works: even if _use_dpapi would otherwise
    # return True, JOJO_CONFIG_FORCE_PLAINTEXT wins.
    monkeypatch.setenv("JOJO_CONFIG_FORCE_PLAINTEXT", "1")
    assert config._use_dpapi() is False


# ---- env map integrity --------------------------------------------------
def test_env_map_covers_all_exported_keys() -> None:
    """Every KEY_* constant at module level should have an ENV_MAP entry.
    Catches 'added a new key but forgot to wire the env var' at test time.
    """
    exported_keys = {
        v for k, v in vars(config).items()
        if k.startswith("KEY_") and isinstance(v, str)
    }
    assert exported_keys == set(config.ENV_MAP.keys())
