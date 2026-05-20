"""Tests for ``jojo_qa.synthesize``.

The synthesis path is feature-flagged: today it returns the
``api_key_required`` shape with the retrieval bundle attached. This
test file exercises the bundle-building path and the feature flag,
not the model call (which is stubbed until FU-10).
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from jojo_qa import synthesize


@pytest.fixture()
def fake_wiki(tmp_path: Path) -> Path:
    """Three-page wiki with one wikilink to exercise neighborhood retrieval."""
    (tmp_path / "_index.md").write_text(
        textwrap.dedent(
            """\
            # Wiki Index

            ## Program

            - [[cbl-b|CBL-B Program]] — `programs/cbl-b.md`
            - [[del-screening|DEL Screening Program]] — `programs/del-screening.md`

            ## Target

            - [[cbl-b-target|CBL-B Target]] — `targets/cbl-b.md`
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "programs").mkdir()
    (tmp_path / "targets").mkdir()

    (tmp_path / "programs" / "cbl-b.md").write_text(
        "---\nslug: cbl-b\n---\n\nLinks: [[cbl-b-target]] and [[del-screening]].\n",
        encoding="utf-8",
    )
    (tmp_path / "programs" / "del-screening.md").write_text(
        "---\nslug: del-screening\n---\n\nDEL screening at Nurix.\n",
        encoding="utf-8",
    )
    (tmp_path / "targets" / "cbl-b.md").write_text(
        "---\nslug: cbl-b-target\n---\n\nThe CBL-B target is an E3 ligase.\n",
        encoding="utf-8",
    )
    return tmp_path


def test_build_bundle_v1_route_skips_wiki(fake_wiki: Path) -> None:
    """``v1``-route questions don't load wiki candidates."""
    bundle = synthesize.build_retrieval_bundle(
        "What's the AKTA buffer SOP?",
        wiki_root=fake_wiki,
    )
    assert bundle.router_result.route == "v1"
    assert bundle.candidate_entries == []
    assert bundle.candidate_bodies == {}


def test_build_bundle_wiki_route_loads_candidates(fake_wiki: Path) -> None:
    bundle = synthesize.build_retrieval_bundle(
        "What's the difference between CBL-B and DEL screening?",
        wiki_root=fake_wiki,
    )
    assert bundle.router_result.route == "wiki"
    slugs = [e.slug for e in bundle.candidate_entries]
    assert "cbl-b" in slugs
    assert "del-screening" in slugs
    assert "cbl-b" in bundle.candidate_bodies


def test_build_bundle_includes_neighborhood(fake_wiki: Path) -> None:
    """1-hop graph neighborhood is populated when ``include_neighbors=True``."""
    # Build the graph file first.
    from jojo_qa import graph as graph_mod

    g = graph_mod.build(fake_wiki)
    graph_mod.write(g, fake_wiki)

    bundle = synthesize.build_retrieval_bundle(
        "Tell me about CBL-B",
        wiki_root=fake_wiki,
        include_neighbors=True,
    )
    assert "cbl-b" in bundle.graph_neighborhood
    # cbl-b's 1-hop neighbors should include cbl-b-target and del-screening.
    neighbors = bundle.graph_neighborhood["cbl-b"]
    assert "cbl-b-target" in neighbors


def test_build_bundle_truncates_long_bodies(fake_wiki: Path) -> None:
    """Bodies longer than ``max_body_chars`` are truncated."""
    huge = "x" * 50_000
    (fake_wiki / "programs" / "cbl-b.md").write_text(
        "---\nslug: cbl-b\n---\n\n" + huge,
        encoding="utf-8",
    )
    bundle = synthesize.build_retrieval_bundle(
        "Tell me about CBL-B",
        wiki_root=fake_wiki,
        max_body_chars=1_000,
    )
    body = bundle.candidate_bodies.get("cbl-b", "")
    assert len(body) <= 1_500  # truncation marker + limit
    assert "truncated" in body


def test_build_bundle_route_hint_overrides_classifier(fake_wiki: Path) -> None:
    """When the operator provides a route hint, the classifier is bypassed."""
    bundle = synthesize.build_retrieval_bundle(
        "What is the CBL-B Program?",
        wiki_root=fake_wiki,
        route_hint="v1",
    )
    assert bundle.router_result.route == "v1"
    assert "operator-provided" in bundle.router_result.reason


def test_answer_returns_api_key_required_when_no_key(
    fake_wiki: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No API key configured -> answer returns the canonical no-key shape."""
    from jojo_core import config as core_config

    monkeypatch.setattr(core_config, "get", lambda k, default=None, **_: default)
    out = synthesize.answer("What is CBL-B?", wiki_root=fake_wiki)
    assert out["status"] == "api_key_required"
    assert "retrieval_bundle" in out
    assert out["depth"] == "sonnet"


def test_answer_includes_retrieval_bundle(
    fake_wiki: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The api_key_required response carries enough bundle for Cowork handoff."""
    from jojo_core import config as core_config

    monkeypatch.setattr(core_config, "get", lambda k, default=None, **_: default)
    out = synthesize.answer("What is CBL-B?", wiki_root=fake_wiki)
    bundle = out["retrieval_bundle"]
    assert bundle["question"] == "What is CBL-B?"
    assert bundle["router"]["route"] == "wiki"
    assert any(c["slug"] == "cbl-b" for c in bundle["candidates"])


def test_answer_with_api_key_calls_model(
    fake_wiki: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """API key present -> _call_model is invoked; mock Anthropic to avoid real HTTP."""
    import types
    import unittest.mock as mock

    from jojo_core import config as core_config

    monkeypatch.setattr(
        core_config,
        "get",
        lambda k, default=None, **_: "fake-key" if k == "anthropic_api_key" else default,
    )

    fake_content = types.SimpleNamespace(text="CBL-B is an E3 ligase. [cbl-b-target]")
    fake_resp = types.SimpleNamespace(content=[fake_content])
    fake_messages = mock.MagicMock()
    fake_messages.create.return_value = fake_resp
    fake_client = types.SimpleNamespace(messages=fake_messages)
    FakeAnthropic = mock.MagicMock(return_value=fake_client)

    with mock.patch("anthropic.Anthropic", FakeAnthropic):
        out = synthesize.answer("What is CBL-B?", wiki_root=fake_wiki)

    assert out["status"] == "answered"
    assert "CBL-B" in out["answer"]
    assert out["model"] == "claude-sonnet-4-6"
    assert "retrieval_bundle" in out
    # Confirm the client was called with the fake key.
    FakeAnthropic.assert_called_once_with(api_key="fake-key")


def test_api_key_required_response_shape() -> None:
    """The canonical no-key shape has ``status`` and ``message``. The
    qa_router test will rely on this shape staying stable."""
    assert synthesize.API_KEY_REQUIRED_RESPONSE["status"] == "api_key_required"
    assert "message" in synthesize.API_KEY_REQUIRED_RESPONSE
