# wk10-snapshot.md — Caching + lifecycle baseline

**Date:** 2026-10-29
**Stack (v10):** hybrid + rerank (W9) + semantic cache (0.95 threshold, SQLite)
**Update flow:** tombstone (IsEmpty) → insert → cache.clear()

## Headline numbers

| Metric | W9 (no cache) | W10 cold | W10 warm | Change vs W9 |
|---|---|---|---|---|
| Precision@3 | Not measured¹ | Not measured | Not measured | Not measured |
| Cost/query (avg) | $0.00005168 | ~$0.0000305 | ~$0.0000005 | ~-41% cold; ~-99% warm |
| Latency p50 | 2797.2 ms | 3918 ms | 681 ms | +40.1% cold; -75.7% warm |
| Latency p95² | Not reported | 19284 ms | 830 ms | Not comparable to W9 |
| Grounded response rate | 40% (8/20) | Not measured | Not measured | Not measured |
| Cache hit rate | n/a | 0% (0/20) | 100% (20/20) | Workload-dependent |
| Eval reproducibility | Not assessed | Not assessed | Not assessed | Not assessed |

## Method
- 20 questions from `data/golden_set_w10.jsonl`
- Pass 1 cold: `cache.clear()` first
- Pass 2 warm: rerun immediately; all 20 questions hit the semantic cache
- Costs are script estimates using whitespace-separated word counts for query
  embedding tokens and the configured OpenAI Aug 2026 prices. The script prints
  total costs rounded to five decimal places; per-query values are approximate.
- W9 cost and latency baselines are from `docs/kpi/wk9-snapshot.md`.
- ¹ W9 reports source-level hit@3, not passage-level precision@3; this cache
  measurement did not run a quality evaluation.
- ² For 20 queries, the script's p95 index selects the maximum observed latency.

## Interpretation
Warm-pass cost was 99.1% lower than the cold pass, exceeding the deck's
60–70% expectation. This reflects the intentionally repeated 20-question
golden-set workload: every warm query matched the semantic cache. It should not
be treated as a production hit-rate forecast. Warm p50 latency fell from 3918
ms to 681 ms; cold W10 p50 was slower than the W9 baseline (2797.2 ms).

## Known risks
- False cache hits — none observed on golden set, but production traffic
  will have more variety. Add sample-based monitoring: pull N cache hits per
  day, replay through full RAG, compare answers.
- Cache staleness after doc update — mitigated by clear-on-update in
  ingest_or_update_source(). Verify this is called on EVERY update path.
