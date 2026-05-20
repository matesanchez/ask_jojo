# Phase 7a Token-Reduction Benchmark

Comparing three retrieval strategies by token cost per question:

- **raw_baseline**: every wiki page dumped (pessimistic).
- **index_first**: Phase 4 retrieval bundle.
- **graph_assist**: index_first + 1-hop graph neighbors.

Exit-criterion threshold: index_first or graph_assist should show >=10x token reduction vs raw_baseline at 500 articles. We'll watch the trend curve as the corpus grows.

---

## Run 1 — 2026-04-29 (138 pages)

**Wiki:** `/sessions/magical-quirky-shannon/mnt/jojo_bot_v2.0/ask_jojo_wiki`
**Raw-baseline total tokens:** 218047

| ID | Question | index_first | ratio | graph_assist | ratio | candidates |
|---|---|---:|---:|---:|---:|---:|
| q-001 | What's the difference between NX-1607 and NX-0255? | 18400 | 11.9x | 52239 | 4.2x | 8 |
| q-002 | Did the Weiss lab Peli2 redundancy finding change our positi | 5836 | 37.4x | 10919 | 20.0x | 2 |
| q-003 | How was DEL screening organized at Nurix in 2022? | 13237 | 16.5x | 44277 | 4.9x | 8 |
| q-004 | Walk me through the major Delphi ACS releases from inception | 16794 | 13.0x | 28051 | 7.8x | 8 |
| q-005 | What's the standard buffer prep for an AKTA Pure 25 run on t | 0 | n/a | 0 | n/a | 0 |
| q-rel-1 | What's the connection between CBL-B and DEL screening? | 15990 | 13.6x | 55732 | 3.9x | 8 |
| q-rel-2 | How does Pellino-1 relate to ITK? | 9185 | 23.7x | 64937 | 3.4x | 6 |
| q-rel-3 | What's shared between BTK and IRAK4 programs? | 17353 | 12.6x | 34351 | 6.3x | 8 |

---

## Run 2 — 2026-05-19 (148 pages, schema 0.2.0)

**Wiki:** `C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\ask_jojo_wiki`
**Raw-baseline total tokens:** 225378 (+3.4% vs Run 1; +10 pages since Phase 4/5/6 work)

| ID | Question | index_first | ratio | graph_assist | ratio | candidates |
|---|---|---:|---:|---:|---:|---:|
| q-001 | What's the difference between NX-1607 and NX-0255? | 17682 | 12.7x | 52747 | 4.3x | 8 |
| q-002 | Did the Weiss lab Peli2 redundancy finding change our positi | 6137 | 36.7x | 12489 | 18.0x | 2 |
| q-003 | How was DEL screening organized at Nurix in 2022? | 13546 | 16.6x | 48684 | 4.6x | 8 |
| q-004 | Walk me through the major Delphi ACS releases from inception | 17489 | 12.9x | 43197 | 5.2x | 8 |
| q-005 | What's the standard buffer prep for an AKTA Pure 25 run on t | 0 | n/a | 0 | n/a | 0 |
| q-rel-1 | What's the connection between CBL-B and DEL screening? | 16299 | 13.8x | 62391 | 3.6x | 8 |
| q-rel-2 | How does Pellino-1 relate to ITK? | 13534 | 16.7x | 70653 | 3.2x | 6 |
| q-rel-3 | What's shared between BTK and IRAK4 programs? | 17662 | 12.8x | 35795 | 6.3x | 8 |

**Phase 7a threshold status:** The index_first ratios across all answered questions range from 12.7x to 36.7x — all well above the 10x threshold. The Phase 7a exit criterion is still met at 148 pages. As the corpus grows toward 500 pages the raw_baseline will scale with page count while the index_first bundle stays bounded by the k=8 candidate cap, so the ratio should continue to improve.

---

## Notes

- `graph_assist` exceeds `index_first` because the 1-hop neighbors add page bodies on top of the candidate set. The expected curve: as corpus grows, the gap between `raw_baseline` and `index_first`/`graph_assist` widens, and the graph-assist advantage over index-first shows up specifically on relational questions where the answer requires multi-page synthesis.
- Re-run the benchmark every time the wiki grows by 50 pages. If the raw_baseline / index_first ratio doesn't grow at least linearly with corpus size, the index-first prompt needs tightening. If the ratio crosses 10x at 500 pages, Phase 7a production-exits.
- q-005 routes to the v1 path (not wiki retrieval) so index_first = 0 in both runs; this is expected behavior.