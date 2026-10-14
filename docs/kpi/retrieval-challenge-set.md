# Retrieval Challenge Set

`data/golden_set_challenge.jsonl` is a tougher, versioned evaluation set. The original `data/golden_set.jsonl` remains unchanged so prior run results stay comparable.

## What makes it harder

- All 20 questions require evidence from at least two expected policy documents.
- Questions combine policy areas, distinguish similar rules, test conflicting or overbroad premises, and include unsupported details where the correct response must avoid inventing a rule.
- Each entry includes `expected_sources` and `must_mention` so retrieval and answer quality can be evaluated separately.

## Retrieval metrics

The evaluation report includes three source metrics:

- **Any-source hit@3:** at least one expected document is retrieved. Keep this for continuity, but it is permissive.
- **Complete-source hit@3:** every expected document for the question appears in the top three. This is the strict pass/fail measure for multi-document retrieval.
- **Expected-source coverage@3:** the fraction of expected documents retrieved, averaged across questions. This gives partial credit when a query requires multiple sources.

Retrieved chunk IDs are normalized to their parent document IDs before scoring.

## Run

Use a fresh label for each run; the runner rejects a reused report path or run label.

```bash
.conda/bin/python scripts/run_eval.py \
  --golden-set data/golden_set_challenge.jsonl \
  --db data/answers.db \
  --api-url http://localhost:8000 \
  --judge-model gpt-4o \
  --label eval-run-challenge-small-20261014
```

Use a distinct label for each embedding model or prompt version, for example `eval-run-challenge-large-20261014`.

## First run: small embeddings

Run `eval-run-challenge-small-20261014` completed all 20 questions against the
default `text-embedding-3-small` Qdrant collection:

| Measure | Result |
|---|---:|
| Mean accuracy | 2.15 / 4 |
| Mean groundedness | 2.20 / 4 |
| Mean format | 3.00 / 4 |
| Any-source hit@3 | 19/20 (95.0%) |
| Complete-source hit@3 | 9/20 (45.0%) |
| Mean expected-source coverage@3 | 70.8% |
| Candidate cost total / average | $0.00214724 / $0.00010736 per question |
| Candidate latency median (p50) | 3047.5 ms |

The 95% any-source result alone still looks high, but complete-source hit@3
shows the tougher retrieval gap: fewer than half the questions retrieved all
expected policy documents in the top three. The weakest case was c006, which
retrieved none of its expected sources. The detailed answers and per-question
metrics are in `docs/eval-run-challenge-small-20261014.md`.
