# Phase 7a Token-Reduction Benchmark

Comparing three retrieval strategies by token cost per question:

- **raw_baseline**: every wiki page dumped (pessimistic).
- **index_first**: Phase 4 retrieval bundle.
- **graph_assist**: index_first + 1-hop graph neighbors.

**Wiki:** `/sessions/magical-quirky-shannon/mnt/jojo_bot_v2.0/ask_jojo_wiki`
**Raw-baseline total tokens:** 218047

Exit-criterion threshold: index_first or graph_assist should show >=10x token reduction vs raw_baseline at 500 articles. We'll watch the trend curve as the corpus grows.

## Per-question results

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

## Notes

- `graph_assist` exceeds `index_first` because the 1-hop neighbors add page bodies on top of the candidate set. The expected curve: as corpus grows, the gap between `raw_baseline` and `index_first`/`graph_assist` widens, and the graph-assist advantage over index-first shows up specifically on relational questions where the answer requires multi-page synthesis.
- Re-run the benchmark every time the wiki grows by 50 pages. If the raw_baseline / index_first ratio doesn't grow at least linearly with corpus size, the index-first prompt needs tightening. If the ratio crosses 10x at 500 pages, Phase 7a production-exits.