# wk11 RAGAS baseline

**Snapshot date:** 2026-11-21  
**Mode:** live  
**KB version reported:** `v1`  
**Golden set:** 20 entries from the W10 policy set  
**Cache mode:** bypassed for the quality evaluation

## Observed results

### RAGAS metrics

| Metric | Aggregate | Tutorial bar | Result |
|---|---:|---:|---|
| Faithfulness | 0.425 | 0.85 | Fail |
| Answer relevance | 0.369 | 0.85 | Fail |
| Context precision | 0.675 | 0.75 | Fail |
| Context recall | 0.552 | 0.80 | Fail |

### 8-KPI dashboard

| KPI | Value |
|---|---:|
| Task success rate | 0.45 (9/20) |
| Grounded response rate | 0.425 |
| Hallucination rate | 0.575 |
| Retrieval hit rate | 0.675 |
| Tool success rate | N/A (W13 - no tools yet) |
| Cost per query (USD) | 0.0 (not measured) |
| Latency p50 / p95 | 0 / 0 ms (not measured) |
| Escalation rate | N/A (W17 - no HITL yet) |

**W11 extensions:** cache hit rate 0.0; cache-hit accuracy 0.0; cache-miss accuracy 0.45; `kb_version=v1`.

The task-success judge requires both accuracy and groundedness scores of at least 3/4. The reported 0.45 means 9 of 20 answers passed that rule. The dashboard's hallucination rate is calculated as `1 - faithfulness`; it is a rough inverse, not an independently adjudicated hallucination rate.

The latest run completed the four RAGAS evaluations and returned finite scores. Logs still warn that one generation was returned where three were requested. The six entries shown with the lowest faithfulness each scored 0.000: g001, g003, g004, g005, g006, and g010.

## 1. Diagnose (the core of the exercise)

| Symptom (which number) | Layer it implicates | Most likely cause | Evidence to pull to confirm |
|---|---|---|---|
| KPI 1: task success is 0.45 (9/20). | Generation / retrieval | More than half the answers miss the judge's accuracy or groundedness bar; incomplete retrieved evidence may be contributing. | Per-row question, answer, ideal answer, retrieved context, and judge accuracy/groundedness/reasoning; group failures by missing evidence versus answer error. |
| KPI 2 is 0.425 and KPI 3 is 0.575. | Generation / retrieval | Answers are not consistently supported by the retrieved context. The 0.575 value is only the dashboard's inverse-faithfulness proxy. | Claim-level comparison of each answer with its retrieved chunks; inspect per-row faithfulness and any unsupported claims. |
| Answer relevance is 0.369. | Generation | Many answers may be indirect, overly broad, or abstain when the retrieved context could answer the question. | Per-row relevance scores alongside the exact question, answer, and context; inspect abstentions separately from off-topic answers. |
| KPI 4 / context precision is 0.675. | Retrieval | Top-3 retrieval contains weakly relevant chunks or ranks the strongest evidence too low. | Compare retrieved chunk IDs, scores, ranks, and source IDs with each W10 entry's `expected_sources`; calculate precision at each rank. |
| Context recall is 0.552. | Retrieval | The retrieved set often omits facts needed for a complete answer, especially when evidence spans sections or policies. | Compare each answer's `must_mention` facts with all retrieved text; measure expected-source and fact coverage at k=3 and larger k. |
| KPI 6 is 0.0 and KPI 7 is 0/0 ms. | Process / reporting | The harness defaults missing `cost_usd` and `latency_ms` fields to zero, so these are missing measurements presented as real values. | Compare the fields returned by `ask_rag` with the harness row fields; add request timing and token-based cost, then verify nonzero per-row telemetry. |
| Cache hit rate is 0.0 and cache-miss accuracy is 0.45. | Cache / process | The quality harness deliberately calls `ask_rag(use_cache=False)`. This run measures fresh-answer quality, not cache performance. | Confirm the bypass flag in the harness; separately run paired cold and warm cache-enabled passes and report their hit rates and answer-quality deltas. |
| The report tags the live run `kb_version=v1`. | Process / reproducibility | The live version is a static label and does not identify the exact corpus or Qdrant collection snapshot used. | Check the deployed collection name, ingestion timestamp, active point count, source manifest, and corpus/index hash against the evaluated W10 set. |
| RAGAS logs say one generation was returned instead of three. | Process / evaluation | The configured judge/model path is not honoring the requested generation count, so the intended multi-generation evaluation is actually single-generation. | Inspect the RAGAS metric strictness/generation configuration and provider response metadata; repeat with a backend that honors the configured count or explicitly configure one. |

## 2. Prescribe

| Diagnosed problem | One-line fix | Layer touched |
|---|---|---|
| 1. Low task success | Save per-row judge scores and failure reasons, then fix the most frequent missing-fact or unsupported-answer pattern without lowering the pass bar. | Generation / retrieval |
| 2. Low faithfulness / high inverse-faithfulness | Require every substantive answer claim to be supported by retrieved text and abstain when required evidence is absent. | Generation |
| 3. Low answer relevance | In the answer prompt, require a concise response to the exact question first, followed only by relevant conditions from context. | Generation |
| 4. Low context precision | Tune hybrid candidate selection and reranking against W10 expected sources, and promote the supporting chunk ahead of distractors. | Retrieval |
| 5. Low context recall | Increase the candidate pool before reranking and evaluate fact/source recall at k=5 and k=10, especially for multi-source entries. | Retrieval |
| 6. Zero cost and latency | Record elapsed time and actual prompt/completion/embedding cost per query; represent missing telemetry as unavailable, never zero. | Process / reporting |
| 7. Cache metric is not measured | Keep cache bypass for the quality run and add a separate cache-enabled cold/warm benchmark. | Cache / process |
| 8. Ambiguous KB version | Tag each run with the collection name, ingestion version, and corpus/index hash, and fail if the expected snapshot is not active. | Process |
| 9. Generation-count warning | Set RAGAS generation count to one or use a provider that returns the configured three, and record the choice with each run. | Process / evaluation |

## 3. Set defensible thresholds

The tutorial bars (0.85 faithfulness, 0.85 answer relevance, 0.75 context precision, and 0.80 context recall) are not demonstrated by this run; all four metrics fail them. Do not lower bars to sit just below this weak result. For an employee-policy assistant, use risk-based minimums first. After at least three representative, reproducible runs, set regression gates 3-5 percentage points below the stable baseline, but never below the safety floors.

| Measure | Provisional M2 threshold | Rule / evidence needed to finalize |
|---|---:|---|
| Task success | >= 0.90 overall; 1.00 on designated high-risk questions | Accuracy and groundedness must both be >= 3/4; validate on repeated W10 runs and review every high-risk failure. |
| Faithfulness | >= 0.90 | Require claims to be supported; calibrate against a human-reviewed sample and RAGAS variance. |
| Hallucination rate | <= 0.10 | This is the dashboard's `1 - faithfulness` proxy; add claim-level human labels before treating it as a true hallucination rate. |
| Answer relevance | >= 0.85 | Review per-row relevance and abstentions on a representative question mix. |
| Context precision@3 | >= 0.85 | Tune and validate against expected-source labels and per-rank retrieval judgments. |
| Context recall | >= 0.85 | Verify that required facts and all expected sources are retrieved, including multi-hop cases. |
| Cost per query | <= $0.005 (placeholder) | First restore cost telemetry; finalize from measured candidate cost, target volume, and an explicit monthly budget. |
| Latency p50 / p95 | <= 4 s / <= 20 s (provisional) | First restore timing telemetry; these ceilings are anchored to the prior W10 cold baseline and should be replaced by an agreed service target. |
| Cache hit rate | No gate from this run | Measure separately on paired cache-enabled cold/warm passes; do not use the intentional 0.0 bypass rate as a cache-quality result. |
| Tool success / escalation | N/A until implemented | Add thresholds only when tools and human escalation exist and have representative test cases. |

The current 0.45 task-success rate and low retrieval/RAGAS scores are far below these provisional floors. Cost and latency cannot be judged until their instrumentation is fixed.

## 4. The one-paragraph DR #2 statement

This assistant is not ready to ship for M2 as an employee-facing policy assistant. On the 20-question live W10 set, only 9 answers passed the task-success rule; faithfulness was 0.425, answer relevance 0.369, context precision 0.675, and context recall 0.552. I would first improve retrieval coverage and ranking, because missing or noisy evidence limits every downstream answer, then tighten answer generation and review per-row judge failures so responses directly answer the question without unsupported claims. Before making operational claims, I would also repair cost/latency telemetry and version the exact indexed corpus; the current zeros and `v1` tag are not evidence of acceptable performance. I would return for review only after the quality floors pass on repeated, reproducible runs and the operational metrics are measured.
