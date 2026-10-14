# W7 Embedding Comparison

**Status:** Complete for this 20-question comparison. Both indexes and evaluation runs completed on 2026-10-14.

## Measurement definition

Hit@3 is the percentage of golden questions where at least one expected policy document appears among the three retrieved sources. Retrieved chunk IDs are normalized to document IDs before comparison. Expected document IDs are recorded in `data/golden_set.jsonl`.

## Results

| Embedding model | Eval label | Collection | Questions | Hit@3 | Embedding dimensions | Result |
|---|---|---|---:|---:|---:|---|
| `text-embedding-3-small` | `eval-run-008-small-embedding-20261014` | `capstone_eval_small_20261014` | 20 | 20/20 (100%) | 1536 | Fresh isolated index and live evaluation |
| `text-embedding-3-large` | `eval-run-009-large-embedding-20261014` | `capstone_eval_large_20261014` | 20 | 19/20 (95%) | 3072 | Fresh isolated index and live evaluation |

## Head-to-head results

| Measure | Small | Large | Large minus small |
|---|---:|---:|---:|
| Retrieval hit@3 | 100% (20/20) | 95% (19/20) | -5 percentage points |
| Mean accuracy | 2.90 / 4 | 3.15 / 4 | +0.25 |
| Mean groundedness | 2.90 / 4 | 3.10 / 4 | +0.20 |
| Mean format | 3.20 / 4 | 3.40 / 4 | +0.20 |
| Index build embedding cost | $0.00046060 | $0.00299390 | +$0.00253330 (about 6.5x total) |
| Average candidate cost/query | $0.00007675 | $0.00007785 | +$0.00000110 (about 1.4%) |
| Candidate latency average | 2785.7 ms | 3251.9 ms | +466.2 ms (about 16.7%) |
| Candidate latency median (p50) | 2777.5 ms | 2986.8 ms | +209.3 ms (about 7.5%) |

The only retrieval miss in the large run was **g007**: its top three sources were
harassment and grievance policies, not the expected code-of-conduct policy.
Large improved the mean judge scores, but did not improve source hit rate.

## Decision

Keep `text-embedding-3-small` as the default for this capstone. On the measured
set it retrieved at least one expected source for every question, had lower
index-build cost and lower query latency, and its average query cost was
slightly lower. `text-embedding-3-large` produced higher judge scores (+0.20 to
+0.25 points), so it may be worth a targeted follow-up for quality-critical
queries; however, its source hit@3 was lower and its corpus indexing cost was
about 6.5x higher. The decision prioritizes reliable source retrieval and
operational cost for the default path, not a claim that small wins every
quality dimension.

## Method and caveats

- Both runs used the same 20 golden questions, `gpt-4o-mini` for answers,
  `gpt-4o` for judging, Qdrant cosine search, and top-k=3. Each used an isolated
  collection and unique evaluation label in `data/embedding-comparison-20261014.db`.
- Hit@3 counts a question as a hit when at least one expected document ID from
  `expected_sources` occurs among the top three retrieved sources. Chunk IDs
  are normalized to document IDs.
- The test set has only 20 questions; the measured 100% versus 95% hit rates
  are set-specific and not a guarantee of production performance. The runs
  were sequential rather than randomized, so latency is indicative, not a
  controlled benchmark.
- Corpus embedding costs are for indexing the 280 chunks; query costs are
  averaged over the 20 measured candidate API requests. Judge cost is excluded
  from candidate cost and is available in each detailed run report.

Detailed runs: `docs/eval-run-008-small-embedding-20261014.md` and
`docs/eval-run-009-large-embedding-20261014.md`.
