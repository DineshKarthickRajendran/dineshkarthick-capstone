# wk7-snapshot.md — Qdrant migration baseline

**Date:** 2026-10-14
**Vector store:** Qdrant Cloud
**Production/default collection:** `capstone_chunks` (1536 dimensions, cosine)
**Default embedding model:** text-embedding-3-small

## Headline numbers

| Metric | W6 (JSON / eval-run-005) | W7 small (`eval-run-008`) | W7 large (`eval-run-009`) |
|---|---:|---:|---:|
| Average candidate cost/query | $0.0008263375 (wk6 snapshot) | $0.00007675 | $0.00007785 |
| Candidate latency p50 | Not measured | 2777.5 ms | 2986.8 ms |
| Retrieval hit@3 | Not measured | 20/20 (100%) | 19/20 (95%) |
| Mean accuracy | 2.85 / 4 | 2.90 / 4 | 3.15 / 4 |
| Mean groundedness | 2.85 / 4 reported* | 2.90 / 4 | 3.10 / 4 |
| Mean format | 3.20 / 4 reported** | 3.20 / 4 | 3.40 / 4 |

For the embedding head-to-head, large minus small is -5 percentage points for
hit@3; +0.25 accuracy, +0.20 groundedness, and +0.20 format points; +$0.00000110
average query cost; and +209.3 ms p50 latency. Index build cost was $0.00046060
for small and $0.00299390 for large (about 6.5x).

The W6 and W7 aggregate judge scores are a historical comparison, not a
controlled estimate of Qdrant's effect. See `w7-comparions.md` for the
embedding-specific method and caveats.

\* The eval-run-005 question-level groundedness scores average 2.90/4, not the
reported 2.85/4.

\*\* The eval-run-005 question-level format scores average 3.25/4; its reported
3.2 is rounded to one decimal.

## Operational deltas

| Property | W6 | W7 |
|---|---|---|
| Persistence | file-based JSON | Qdrant-managed |
| Restart behavior | Load JSON vectors into process memory | Data remains in Qdrant; no JSON-vector reload |
| Filtering | none | ready for W8 metadata |
| Scaling | Limited by application-process memory | HNSW-backed service intended for larger collections; capacity not benchmarked here |

The W7 operational change is confirmed by the implementation design. This
snapshot contains no measured restart-time or scale benchmark.

## Method
- W6/W7 history references `eval-run-005` and `eval-run-006-W7`; embedding
  comparison uses the fresh, isolated `eval-run-008` and `eval-run-009` runs.
- Hit@3 is the fraction of questions whose top-three retrieved sources include
  at least one expected source document recorded in the golden set.
- Cost and latency values are from candidate API calls; judge-call cost is
  excluded. Index build costs are reported separately in `w7-comparions.md`.

## Embedding-model decision
- **Default:** `text-embedding-3-small`; it measured 100% hit@3, lower query
  latency, and about 6.5x lower one-time corpus-indexing cost in this run.
- `text-embedding-3-large` produced higher judge scores but 95% hit@3 and
  higher latency/cost. Keep it as a possible targeted option, not the default.
- Full run labels, deltas, and limitations: `w7-comparions.md`.