"""Fine-tune dataset generation for JoJo Bot v2.0.

Reads wiki pages via ``jojo_qa.index_loader``, then asks Claude to
produce synthetic training examples in three flavours:

- ``paraphrase``  — restate the first 400 chars of a page in one sentence.
- ``fill_blank``  — a fill-in-the-blank sentence drawn from the page.
- ``synthesis``   — a multi-hop question that requires two pages to answer.

Output is written as line-delimited JSON (JSONL) to ``data/finetune/``.

Dry-run mode (``dry_run=True``) produces deterministic records without any
API call, so tests and CI work without credentials.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

from jojo_core import config

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


class WikiPage(TypedDict):
    """A single wiki page record, as yielded by ``walk_wiki``."""

    slug: str
    title: str
    body: str


class FinetuneExample(TypedDict):
    """One training record in JSONL output."""

    id: str           # uuid4 hex
    type: str         # "paraphrase" | "fill_blank" | "synthesis"
    citation: list[str]  # wiki slugs (1 for paraphrase/fill_blank, 2+ for synthesis)
    input: str        # prompt sent to model
    output: str       # expected completion
    created_at: str   # ISO 8601


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

GENERATION_PROMPTS: dict[str, dict[str, str]] = {
    "paraphrase": {
        "system": (
            "You are a scientific writing assistant helping to create training data "
            "for an internal knowledge base assistant. "
            "Respond with exactly one sentence. No preamble, no suffix."
        ),
        "user": (
            "Paraphrase the following text in one concise sentence:\n\n{snippet}"
        ),
    },
    "fill_blank": {
        "system": (
            "You are a scientific writing assistant helping to create training data "
            "for an internal knowledge base assistant. "
            "Produce a single fill-in-the-blank sentence where the blank replaces "
            "the most informative noun or phrase. Format: include '___' as the blank. "
            "No preamble, no suffix."
        ),
        "user": (
            "Create a fill-in-the-blank sentence drawn from this text:\n\n{snippet}"
        ),
    },
    "synthesis": {
        "system": (
            "You are a scientific writing assistant helping to create training data "
            "for an internal knowledge base assistant. "
            "Produce a question that requires reading BOTH provided pages to answer "
            "correctly, followed by a concise answer. "
            "Format:\nQ: <question>\nA: <answer>"
        ),
        "user": (
            "Page A — {title_a}:\n{snippet_a}\n\n"
            "Page B — {title_b}:\n{snippet_b}\n\n"
            "Write a question that can only be answered by reading both pages, "
            "and then write the answer."
        ),
    },
}

# Model used for generation — Haiku for cost efficiency.
_GENERATION_MODEL = "claude-haiku-4-5-20251001"

# Minimum body length (chars) for a page to be included.
_MIN_BODY_CHARS = 200

# How many chars of body text to pass to the model per page.
_SNIPPET_CHARS = 400


# ---------------------------------------------------------------------------
# walk_wiki
# ---------------------------------------------------------------------------


def walk_wiki(wiki_root: Path) -> list[WikiPage]:
    """Enumerate pages from ``_index.md`` and return those with body >= 200 chars.

    Uses ``jojo_qa.index_loader.load_index`` for slug/title/path enumeration,
    then reads each page body from disk.

    Args:
        wiki_root: path to the ``ask_jojo_wiki/`` directory.

    Returns:
        List of ``WikiPage`` dicts in index order, excluding short pages.
    """
    from jojo_qa import index_loader

    entries = index_loader.load_index(wiki_root)
    pages: list[WikiPage] = []
    for entry in entries:
        page_path = wiki_root / entry.path
        try:
            body = page_path.read_text(encoding="utf-8")
        except OSError:
            continue
        if len(body) < _MIN_BODY_CHARS:
            continue
        pages.append(WikiPage(slug=entry.slug, title=entry.title, body=body))
    return pages


# ---------------------------------------------------------------------------
# Individual generators (live API path)
# ---------------------------------------------------------------------------


def generate_paraphrase(page: WikiPage, client: object) -> FinetuneExample:
    """Ask the model to paraphrase the first 400 chars of ``page.body``.

    Args:
        page:   wiki page dict.
        client: ``anthropic.Anthropic`` client instance.

    Returns:
        ``FinetuneExample`` with ``type="paraphrase"``.
    """
    snippet = page["body"][:_SNIPPET_CHARS].strip()
    tmpl = GENERATION_PROMPTS["paraphrase"]
    user_msg = tmpl["user"].format(snippet=snippet)

    resp = client.messages.create(  # type: ignore[union-attr]
        model=_GENERATION_MODEL,
        max_tokens=256,
        system=tmpl["system"],
        messages=[{"role": "user", "content": user_msg}],
    )
    output = resp.content[0].text.strip()

    return FinetuneExample(
        id=uuid.uuid4().hex,
        type="paraphrase",
        citation=[page["slug"]],
        input=user_msg,
        output=output,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def generate_fill_blank(page: WikiPage, client: object) -> FinetuneExample:
    """Ask the model for a fill-in-the-blank sentence from ``page.body``.

    Args:
        page:   wiki page dict.
        client: ``anthropic.Anthropic`` client instance.

    Returns:
        ``FinetuneExample`` with ``type="fill_blank"``.
    """
    snippet = page["body"][:_SNIPPET_CHARS].strip()
    tmpl = GENERATION_PROMPTS["fill_blank"]
    user_msg = tmpl["user"].format(snippet=snippet)

    resp = client.messages.create(  # type: ignore[union-attr]
        model=_GENERATION_MODEL,
        max_tokens=256,
        system=tmpl["system"],
        messages=[{"role": "user", "content": user_msg}],
    )
    output = resp.content[0].text.strip()

    return FinetuneExample(
        id=uuid.uuid4().hex,
        type="fill_blank",
        citation=[page["slug"]],
        input=user_msg,
        output=output,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def generate_synthesis(
    page_a: WikiPage, page_b: WikiPage, client: object
) -> FinetuneExample:
    """Ask the model for a multi-hop question drawing on two pages.

    Args:
        page_a: first wiki page dict.
        page_b: second wiki page dict.
        client: ``anthropic.Anthropic`` client instance.

    Returns:
        ``FinetuneExample`` with ``type="synthesis"``.
    """
    snippet_a = page_a["body"][:_SNIPPET_CHARS].strip()
    snippet_b = page_b["body"][:_SNIPPET_CHARS].strip()
    tmpl = GENERATION_PROMPTS["synthesis"]
    user_msg = tmpl["user"].format(
        title_a=page_a["title"],
        snippet_a=snippet_a,
        title_b=page_b["title"],
        snippet_b=snippet_b,
    )

    resp = client.messages.create(  # type: ignore[union-attr]
        model=_GENERATION_MODEL,
        max_tokens=512,
        system=tmpl["system"],
        messages=[{"role": "user", "content": user_msg}],
    )
    output = resp.content[0].text.strip()

    return FinetuneExample(
        id=uuid.uuid4().hex,
        type="synthesis",
        citation=[page_a["slug"], page_b["slug"]],
        input=user_msg,
        output=output,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# Dry-run generators (deterministic, no API)
# ---------------------------------------------------------------------------


def _first_sentence(text: str) -> str:
    """Return the first sentence of ``text`` (up to the first period/newline)."""
    # Strip frontmatter if present
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:].lstrip()
    # Take first sentence
    match = re.search(r"[.!?]", text)
    if match:
        return text[: match.start() + 1].strip()
    return text[:120].strip()


def _dry_paraphrase(page: WikiPage) -> FinetuneExample:
    sentence = _first_sentence(page["body"])
    snippet = page["body"][:_SNIPPET_CHARS].strip()
    tmpl = GENERATION_PROMPTS["paraphrase"]
    user_msg = tmpl["user"].format(snippet=snippet)
    return FinetuneExample(
        id=uuid.uuid4().hex,
        type="paraphrase",
        citation=[page["slug"]],
        input=user_msg,
        output=sentence,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _dry_fill_blank(page: WikiPage) -> FinetuneExample:
    sentence = _first_sentence(page["body"])
    # Blank the last content word before punctuation
    words = sentence.rstrip(".!?").split()
    if len(words) >= 2:
        blanked = " ".join(words[:-1]) + " ___."
    else:
        blanked = "___ " + sentence
    snippet = page["body"][:_SNIPPET_CHARS].strip()
    tmpl = GENERATION_PROMPTS["fill_blank"]
    user_msg = tmpl["user"].format(snippet=snippet)
    return FinetuneExample(
        id=uuid.uuid4().hex,
        type="fill_blank",
        citation=[page["slug"]],
        input=user_msg,
        output=blanked,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _dry_synthesis(page_a: WikiPage, page_b: WikiPage) -> FinetuneExample:
    question = f"What connects {page_a['title']} and {page_b['title']}?"
    answer = (
        f"{page_a['title']} and {page_b['title']} are both described in the "
        f"JoJo Bot wiki."
    )
    snippet_a = page_a["body"][:_SNIPPET_CHARS].strip()
    snippet_b = page_b["body"][:_SNIPPET_CHARS].strip()
    tmpl = GENERATION_PROMPTS["synthesis"]
    user_msg = tmpl["user"].format(
        title_a=page_a["title"],
        snippet_a=snippet_a,
        title_b=page_b["title"],
        snippet_b=snippet_b,
    )
    return FinetuneExample(
        id=uuid.uuid4().hex,
        type="synthesis",
        citation=[page_a["slug"], page_b["slug"]],
        input=user_msg,
        output=f"Q: {question}\nA: {answer}",
        created_at=datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

EXAMPLE_TYPES = ["paraphrase", "fill_blank", "synthesis"]


def generate_dataset(
    wiki_root: Path,
    output_path: Path,
    n: int = 100,
    *,
    api_key: str | None = None,
    dry_run: bool = False,
) -> list[FinetuneExample]:
    """Generate ``n`` training examples and write them as JSONL to ``output_path``.

    Args:
        wiki_root:   path to ``ask_jojo_wiki/``.
        output_path: destination ``.jsonl`` file.
        n:           total number of examples to generate (approximate).
        api_key:     Anthropic API key. Falls back to ``config.get("anthropic_api_key")``.
        dry_run:     when True, produce records deterministically without API calls.

    Returns:
        The list of ``FinetuneExample`` dicts written.

    Raises:
        ValueError: if ``api_key`` is missing and ``dry_run=False``.
        RuntimeError: if the wiki has fewer than 2 pages (synthesis is impossible).
    """
    pages = walk_wiki(wiki_root)
    if len(pages) < 2:
        raise RuntimeError(
            f"Wiki at {wiki_root!r} has fewer than 2 eligible pages "
            f"(found {len(pages)}); cannot generate synthesis examples."
        )

    client = None
    if not dry_run:
        key = api_key or config.get("anthropic_api_key", None)
        if not key:
            raise ValueError(
                "api_key is required for live generation. "
                "Pass api_key= or set anthropic_api_key in config. "
                "Use dry_run=True for tests."
            )
        import anthropic  # noqa: PLC0415 — lazy import, optional dep

        client = anthropic.Anthropic(api_key=key)

    examples: list[FinetuneExample] = []
    # Distribute n evenly across types: ~1/3 each.
    per_type = max(1, n // 3)
    remainder = n - per_type * 2  # synthesis gets the rest

    # Paraphrase examples
    for i in range(per_type):
        page = pages[i % len(pages)]
        if dry_run:
            examples.append(_dry_paraphrase(page))
        else:
            examples.append(generate_paraphrase(page, client))

    # Fill-blank examples
    for i in range(per_type):
        page = pages[(i + 1) % len(pages)]
        if dry_run:
            examples.append(_dry_fill_blank(page))
        else:
            examples.append(generate_fill_blank(page, client))

    # Synthesis examples
    for i in range(remainder):
        page_a = pages[i % len(pages)]
        page_b = pages[(i + 1) % len(pages)]
        if dry_run:
            examples.append(_dry_synthesis(page_a, page_b))
        else:
            examples.append(generate_synthesis(page_a, page_b, client))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        for ex in examples:
            fh.write(json.dumps(ex) + "\n")

    return examples
