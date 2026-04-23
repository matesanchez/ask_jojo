"""Tests for ``jojo-core config`` CLI subcommands."""

from __future__ import annotations

from pathlib import Path

import pytest

from jojo_core import cli, config


@pytest.fixture(autouse=True)
def _isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    cfg = tmp_path / "config.json"
    config.set_config_path_for_tests(cfg)
    monkeypatch.setenv("JOJO_CONFIG_FORCE_PLAINTEXT", "1")
    for env_name in config.ENV_MAP.values():
        monkeypatch.delenv(env_name, raising=False)
    yield
    config.set_config_path_for_tests(None)


def test_config_path_prints_file_location(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["config", "path"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == str(config.config_path())


def test_config_show_empty_hints_at_path(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["config", "show"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "(empty" in out
    assert str(config.config_path()) in out


def test_config_set_then_show_masks_secrets(capsys: pytest.CaptureFixture[str]) -> None:
    cli.main(["config", "set", config.KEY_ANTHROPIC_API_KEY, "sk-ant-supersecret-1234"])
    capsys.readouterr()  # discard the "set" confirmation
    cli.main(["config", "show"])
    out = capsys.readouterr().out
    # Secret is masked (not the raw value)
    assert "sk-ant-supersecret-1234" not in out
    assert "..." in out


def test_config_show_unmask_reveals_secrets(capsys: pytest.CaptureFixture[str]) -> None:
    cli.main(["config", "set", config.KEY_ANTHROPIC_API_KEY, "sk-ant-supersecret-1234"])
    capsys.readouterr()
    cli.main(["config", "show", "--unmask"])
    out = capsys.readouterr().out
    assert "sk-ant-supersecret-1234" in out


def test_config_set_rejects_unknown_key(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["config", "set", "not_a_real_key", "x"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "unknown key" in err


def test_config_get_returns_value(capsys: pytest.CaptureFixture[str]) -> None:
    config.set(config.KEY_RAW_ROOT, "/some/raw")
    rc = cli.main(["config", "get", config.KEY_RAW_ROOT])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == "/some/raw"


def test_config_get_missing_key_returns_nonzero(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["config", "get", config.KEY_RAW_ROOT])
    err = capsys.readouterr().err
    assert rc == 1
    assert "unset" in err


def test_config_get_env_fallback_by_default(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("JOJO_RAW_ROOT", "/from-env")
    rc = cli.main(["config", "get", config.KEY_RAW_ROOT])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == "/from-env"


def test_config_get_no_env_flag(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("JOJO_RAW_ROOT", "/from-env")
    rc = cli.main(["config", "get", config.KEY_RAW_ROOT, "--no-env"])
    assert rc == 1  # would be 0 if env fallback were enabled


def test_config_delete(capsys: pytest.CaptureFixture[str]) -> None:
    config.set(config.KEY_RAW_ROOT, "/x")
    rc = cli.main(["config", "delete", config.KEY_RAW_ROOT])
    assert rc == 0
    assert config.load() == {}


def test_config_delete_missing_key_nonzero(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["config", "delete", config.KEY_RAW_ROOT])
    assert rc == 1


def test_config_migrate_from_env(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("JOJO_RAW_ROOT", "/raw")
    monkeypatch.setenv("JOJO_REDIS_URL", "redis://r")
    rc = cli.main(["config", "migrate-from-env"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "migrated raw_root" in out
    assert "migrated redis_url" in out


def test_config_set_secret_without_dpapi_warns(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # FORCE_PLAINTEXT is already on via the autouse fixture, so this is a
    # "would be insecure on a real Windows install" scenario.
    rc = cli.main(["config", "set", config.KEY_ANTHROPIC_API_KEY, "sk-x"])
    err = capsys.readouterr().err
    assert rc == 0
    assert "DPAPI" in err
