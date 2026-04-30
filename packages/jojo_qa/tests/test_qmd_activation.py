"""Tests for ``jojo_qa.qmd_activation``."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from jojo_qa import qmd_activation


@pytest.fixture()
def fake_wiki(tmp_path: Path) -> Path:
    """Wiki with N pages controlled by ``request.param`` (default 3)."""
    return tmp_path


def _write_index(wiki_root: Path, n: int) -> None:
    lines = ["# Wiki Index", "", "## Program", ""]
    for i in range(n):
        lines.append(f"- [[slug-{i}|Page {i}]] — `programs/p{i}.md`")
    (wiki_root / "_index.md").write_text("\n".join(lines), encoding="utf-8")


def test_check_default_state_dormant(fake_wiki: Path) -> None:
    """Empty wiki, no manual override, no qmd installed -> dormant."""
    _write_index(fake_wiki, 3)
    status = qmd_activation.check(wiki_root=fake_wiki)
    assert status.active is False
    assert status.index_pages == 3
    assert status.index_trigger is False
    assert status.p95_trigger is False
    assert status.miss_trigger is False


def test_check_index_threshold_fires(fake_wiki: Path) -> None:
    _write_index(fake_wiki, 250)
    status = qmd_activation.check(wiki_root=fake_wiki, index_threshold=200)
    assert status.index_trigger is True
    # Active also requires ``qmd`` package; in test env it's not installed.
    assert status.qmd_available is False
    assert status.active is False


def test_check_below_index_threshold(fake_wiki: Path) -> None:
    _write_index(fake_wiki, 199)
    status = qmd_activation.check(wiki_root=fake_wiki, index_threshold=200)
    assert status.index_trigger is False


def test_manual_override_via_config(
    fake_wiki: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``config.qmd_force_active=True`` flips manual override."""
    _write_index(fake_wiki, 10)
    from jojo_core import config as core_config

    monkeypatch.setattr(
        core_config,
        "get",
        lambda k, default=None, **_: True if k == "qmd_force_active" else default,
    )
    status = qmd_activation.check(wiki_root=fake_wiki)
    assert status.manual_override is True


def test_p95_latency_trigger(
    fake_wiki: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``config.qa_p95_latency_sec`` above threshold fires the latency trigger."""
    _write_index(fake_wiki, 10)
    from jojo_core import config as core_config

    monkeypatch.setattr(
        core_config,
        "get",
        lambda k, default=None, **_: 12.0 if k == "qa_p95_latency_sec" else default,
    )
    status = qmd_activation.check(wiki_root=fake_wiki, p95_threshold=8.0)
    assert status.p95_latency_sec == 12.0
    assert status.p95_trigger is True


def test_should_activate_returns_bool(fake_wiki: Path) -> None:
    _write_index(fake_wiki, 3)
    out = qmd_activation.should_activate(wiki_root=fake_wiki)
    assert isinstance(out, bool)


def test_status_summary_shape(fake_wiki: Path) -> None:
    _write_index(fake_wiki, 5)
    summary = qmd_activation.status_summary(wiki_root=fake_wiki)
    assert "active" in summary
    assert "qmd_available" in summary
    assert "manual_override" in summary
    assert "triggers" in summary
    assert "index" in summary["triggers"]
    assert "latency" in summary["triggers"]
    assert "miss_rate" in summary["triggers"]
    assert "reason" in summary


def test_qmd_prefilter_returns_empty_when_inactive(fake_wiki: Path) -> None:
    """Without activation, the prefilter returns empty (caller falls back)."""
    out = qmd_activation.qmd_prefilter("question", fake_wiki)
    assert out == []


def test_activate_deactivate_round_trip() -> None:
    """The activate/deactivate functions toggle a single config flag."""
    from jojo_core import config as core_config

    qmd_activation.activate()
    assert core_config.get("qmd_active") is True
    qmd_activation.deactivate()
    assert core_config.get("qmd_active") is False


def test_is_active_reads_config() -> None:
    qmd_activation.activate()
    assert qmd_activation.is_active() is True
    qmd_activation.deactivate()
    assert qmd_activation.is_active() is False


def test_reason_string_is_human_readable(fake_wiki: Path) -> None:
    _write_index(fake_wiki, 3)
    s = qmd_activation.check(wiki_root=fake_wiki)
    # No triggers fired -> reason mentions dormant.
    assert "dormant" in s.reason.lower() or "no activation" in s.reason.lower()
