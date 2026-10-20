# W9 Snapshot — Hybrid retrieval + cross-encoder reranking

**Evaluation date:** 2026-10-20  
**Dataset:** 20 questions in `data/golden_set_w9.jsonl`  
**W9 run:** `docs/eval-run-w9-final-20261020.md`  
**W8 comparison:** `docs/eval-run-w8-chunks-20261017-final.md`

## Retrieval stack

BM25 (rank-bm25) + dense Qdrant cosine search using
`text-embedding-3-small`, fused by reciprocal-rank fusion (RRF, k=60).
The top 10 fused candidates are reranked by the local
`cross-encoder/ms-marco-MiniLM-L-6-v2`; the top 3 passages are sent to
generation.

## Headline comparison

| Metric | W8 dense | W9 hybrid + rerank | Change |
|---|---:|---:|---:|
| Any expected source hit@3 | 20/20 (100%) | 20/20 (100%) | 0 pp |
| All expected sources hit@3 | 17/20 (85%) | 18/20 (90%) | +5 pp |
| Expected-source coverage@3 | 91.2% | 95.0% | +3.8 pp |
| Mean answer accuracy (/4) | 2.30 | 2.50 | +0.20 |
| Mean groundedness (/4) | 2.45 | 2.55 | +0.10 |
| Mean format (/4) | 3.00 | 3.00 | no change |
| Grounded responses (groundedness >=3) | 7/20 (35%) | 8/20 (40%) | +5 pp |
| Candidate cost / query | $0.00004973 | $0.00005168 | +$0.00000195 (+3.9%) |
| Candidate latency p50 | 2652.1 ms | 2797.2 ms | +145.1 ms (+5.5%) |

Grounded-response rate is defined here as the fraction of answers with a judge
groundedness score of at least 3/4. Retrieval hit and source coverage use the
expected document/source IDs, not exact relevant-passage labels.

## Interpretation

- The W9 run maintained the already-high any-source hit@3 while improving
  complete multi-source retrieval by 5 percentage points and average
  expected-source coverage by 3.8 points. This is the clearest measured
  retrieval benefit for compositional questions.
- Mean accuracy improved by 0.20/4 and groundedness by 0.10/4; format was
  unchanged. These are modest gains on a small 20-question set, not evidence
  that reranking alone caused the improvement.
- W9 cost increased by about $0.000002/query, and p50 latency increased by
  about 145 ms. The W9 p50 includes a cold first retrieval request and the
  local reranking path.
- Source-level hit@3 does not guarantee the right passage within a source.
  Several answers abstained despite retrieving the expected document. Evaluate
  passage-level relevance and inspect low-scoring cases (notably g001, g003,
  g005, g006, g008, and g010) before tuning the generator.
- The standalone per-question comparison in `docs/wk9-precision-delta.md`
  reports a different W9 P@3 result (19/20 versus 20/20 in the full evaluation).
  Its binary “precision” convention and run/path mismatch make it unsuitable
  as a settled comparison. Precision@5 was not measured in the final evaluation.
  Rerun the precision script against the same collection, endpoint, and
  question set before publishing exact passage-level P@3/P@5.

## Method and caveats

- W8 and W9 headline results come from their saved 20-question evaluation
  reports. The W9 run used the active `src.api.main` `/ask_w9` endpoint and the
  W9-specific golden set.
- The comparison is observational: retrieval, prompt context, and live model
  responses can vary. It does not isolate the BM25 or reranker contribution.
- Source-level metrics are lenient: repeated chunks from one expected source
  can fill the top 3 and count as an any-source hit. Add judged relevant
  chunk IDs to measure true passage precision.
- The W9 candidate cost excludes the separate judge cost. For this run, judge
  cost averaged $0.001972/query and judge p50 latency was 2265.4 ms.
