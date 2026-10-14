# wk7-snapshot.md — Qdrant migration baseline

**Date:** 2026-10-14
**Vector store:** Qdrant Cloud
**Collection:** `capstone_chunks` (point count not recorded; 1536 dimensions, cosine)
**Embedding model:** text-embedding-3-small

## Headline numbers

| Metric | W6 (JSON / eval-run-005) | W7 (Qdrant / eval-run-006-W7) | Change |
|---|---:|---:|---:|
| Average answer cost/query | $0.0008263375 (wk6 snapshot) | Not measured for this run | Not available |
| Latency p50 | Not measured | Not measured | Not available |
| Retrieval hit rate | Not measured | Not measured | Not available |
| Mean accuracy | 2.85 / 4 | 3.10 / 4 | +0.25 |
| Mean groundedness | 2.85 / 4 reported* | 3.10 / 4 | +0.25 reported* |
| Mean format | 3.20 / 4 reported** | 3.30 / 4 | +0.10 reported** |

Both evaluations used the same 20 golden questions. The result is a positive
run-to-run signal for the W7 retrieval setup, not proof that Qdrant alone caused
the score increase; other run conditions are not documented as controlled.

\* The eval-run-005 question-level groundedness scores average 2.90/4, not the
reported 2.85/4. Against the row-derived baseline, the gain is +0.20/4.

\*\* The eval-run-005 question-level format scores average 3.25/4; its reported
3.2 is rounded to one decimal. Against that row-derived baseline, the gain is
+0.05/4.

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
- Compared the 20-question `eval-run-005` chunked JSON-backed RAG run with
  `eval-run-006-W7` against Qdrant; see both reports for per-question scores.
- The $0.0008263375 W6 cost figure is from `wk6-snapshot.md`; a directly
  comparable W7 cost and latency were not recorded.
- The evaluation reports measure judge scores, not retrieval hit rate. No
  retrieval-hit evaluation or p50 latency measurement is available here.

## Embedding-model comparison (from Lab Step 2)
- **Selected:** `text-embedding-3-small` (1536 dimensions), used by the W7
  Qdrant collection.
- The ADR records that `text-embedding-3-large` was rejected due to its higher
  cost (reported as 6.5x) and insufficient quality gain for this corpus.
- Exact correct-retrieval counts and total costs from Lab Step 2 are not
  recorded in the available snapshot, so no numeric model-comparison result is
  claimed here.