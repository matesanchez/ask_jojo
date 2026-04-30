# Phase 4 Q&A Queue — JoJo Bot

**Governing ADR:** `docs/ADR/0011-qa-via-cowork-while-api-pending.md`
**Prompt:** `docs/qa/qa-prompt.md`
**Benchmark:** `docs/qa/benchmark-questions.md` (canonical 50-question set; this queue is the operational tracker)
**Answers:** `docs/qa/answers/<date>-<slug>.md`

This file is the operational queue for the Phase 4 Cowork-Q&A loop. Each `## Question N` block is one atomic Cowork session: claim the next unanswered question, run the session, write the answer file, tick the box, commit. Sessions do not straddle questions.

The queue is *not* the benchmark — `benchmark-questions.md` is the canonical 50-question set with expert-approved gold answers. The queue is for ad-hoc Q&A plus the benchmark questions in the order they're worked through. When a queue session produces a gold answer, it gets propagated back to the benchmark file.

## How to add a question

Append a `## Question N` heading at the bottom of the file with:

- the question text in plain prose,
- a route hint (`v1` or `wiki`; if unsure, leave blank — the regex in `router.py` provides the default),
- a candidate-slug list (optional; the deterministic retrieval bundle from `GET /api/qa/retrieve` can populate this),
- the asker (`mateo` for now; will grow once a second operator joins),
- the file destination for the answer (`docs/qa/answers/<date>-<slug>.md`),
- a benchmark hook (`benchmark: q-NNN` if this question maps to a benchmark entry).

Topical clustering helps but is not required at this scale. Unlike the absorb queue (`docs/compile/queue.md`), Q&A questions don't have to converge on a few pages — every session reads `_index.md` from scratch.

---

## Question 1 — CBL-B: NX-1607 vs NX-0255

- **Asked by:** mateo
- **Asked date:** 2026-04-30
- **Route hint:** wiki
- **Candidate slugs:** `cbl-b`, `cbl-b-cmc`, `cbl-b-preclinical-profile`, `cbl-b-ind-pharmacology`
- **Benchmark:** q-001
- **Answer file:** `docs/qa/answers/2026-04-30-cbl-b-nx1607-vs-nx0255.md`

**Question:** What's the difference between NX-1607 and NX-0255, and what's the current clinical status of each?

- [x] Answered 2026-04-30 (session: cowork-2026-04-30-001)

---

## Question 2 — Pellino-1 program: Peli2 redundancy

- **Asked by:** mateo
- **Asked date:** 2026-04-30
- **Route hint:** wiki
- **Candidate slugs:** `pellino-1` (program), `pellino-1` (target), `concepts/cbl-b-genetic-phenotypes` (cross-reference for redundancy framing)
- **Benchmark:** q-002
- **Answer file:** `docs/qa/answers/2026-04-30-pellino-1-peli2-redundancy.md`

**Question:** Did the Weiss lab Peli2 redundancy finding in Jurkat ever change our position on the Pellino-1 program direction?

- [x] Answered 2026-04-30 (session: cowork-2026-04-30-002)

---

## Question 3 — DEL screening at Nurix in 2022

- **Asked by:** mateo
- **Asked date:** 2026-04-30
- **Route hint:** wiki
- **Candidate slugs:** `del-screening`, `del-libraries`, `2022-del-screen-queue`, `dsa-early-discovery-cadence-2022`, `q4-2022-screening-budget`
- **Benchmark:** q-003
- **Answer file:** `docs/qa/answers/2026-04-30-del-screening-2022.md`

**Question:** How was DEL screening organized at Nurix in 2022, and what programs were in the queue?

- [x] Answered 2026-04-30 (session: cowork-2026-04-30-003)

---

## Question 4 — Delphi ACS releases through 2025

- **Asked by:** mateo
- **Asked date:** 2026-04-30
- **Route hint:** wiki
- **Candidate slugs:** `delphi`, `delphi-acs-scope`, `delphi-acs2024-1-release`, `delphi-acs2025-1-release`, `delphi-acs2025-2-release`, `delphi-acs2025-3-release`, `delphi-pre-acs-timeline`
- **Benchmark:** q-004
- **Answer file:** `docs/qa/answers/2026-04-30-delphi-acs-releases-2025.md`

**Question:** Walk me through the major Delphi ACS releases from inception through 2025 — what changed in each, and what was the major decision behind each scope?

- [x] Answered 2026-04-30 (session: cowork-2026-04-30-004)

---

## Question 5 — ÄKTA buffer prep (router test)

- **Asked by:** mateo
- **Asked date:** 2026-04-30
- **Route hint:** v1
- **Candidate slugs:** _(n/a — v1 route)_
- **Benchmark:** q-005 (router test)
- **Answer file:** `docs/qa/answers/2026-04-30-akta-buffer-prep-v1-routing.md`

**Question:** What's the standard buffer prep procedure for an ÄKTA Pure 25 run on the BTK program?

- [x] Answered 2026-04-30 (session: cowork-2026-04-30-005)

---

## Template for new entries

```
## Question N — <short title>

- **Asked by:** <operator>
- **Asked date:** <YYYY-MM-DD>
- **Route hint:** v1 | wiki | (blank for regex-decided)
- **Candidate slugs:** `slug-a`, `slug-b`, ...
- **Benchmark:** q-NNN  (or "ad-hoc" if not in benchmark)
- **Answer file:** `docs/qa/answers/<YYYY-MM-DD>-<slug>.md`

**Question:** <one paragraph>

- [ ] Answered <date> (session: cowork-<date>-NNN)
```
