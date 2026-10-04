# ADR-0001: Capstone Framing - Knowledge Assistant

- **Status:** Draft v2
- **Date:** 2026-09-30
- **Author:** Dinesh Karthick

## Context

This capstone will build a knowledge assistant for employees, people managers, and HR
operations staff who need quick, evidence-based answers to routine HR policy and
process questions. The assistant will answer from a curated corpus of 15–20 HR
documents and will use the existing questionnaire datasets as evaluation seeds,
with additional HR questions added for coverage. It is intended to reduce time
spent searching policy documents; it is not an autonomous decision-maker and must
not replace HR, legal, payroll, or employee-relations review.

### Initial corpus plan

The first release will use public, synthetic, or organisation-approved documents
with an owner and review date recorded for each source. No employee records,
performance reviews, medical information, compensation data, or other sensitive
personal data will be indexed in the capstone corpus.

Planned document set (20 documents, matching `data/corpus/`):

1. Leave Policy (`01_leave_policy.md`)
2. Expense Reimbursement Policy (`02_expense_policy.md`)
3. Work From Home Policy (`03_wfh_policy.md`)
4. Bring Your Own Device Policy (`04_byod_policy.md`)
5. Workplace Dress Code (`05_dress_code.md`)
6. Attendance and Punctuality Policy (`06_attendance_policy.md`)
7. Employee Code of Conduct (`07_code_of_conduct.md`)
8. Remote Work Security Policy (`08_remote_security_policy.md`)
9. Recruitment and Hiring Policy (`09_recruitment_policy.md`)
10. Employee Onboarding Policy (`10_onboarding_policy.md`)
11. Performance Management Policy (`11_performance_management.md`)
12. Promotion and Internal Mobility Policy (`12_promotion_policy.md`)
13. Learning and Development Policy (`13_training_development_policy.md`)
14. Employee Grievance Policy (`14_grievance_policy.md`)
15. Anti-Harassment and Respectful Workplace Policy (`15_harassment_policy.md`)
16. Confidentiality and Information Handling Policy (`16_confidentiality_policy.md`)
17. IT Acceptable Use Policy (`17_it_acceptable_use_policy.md`)
18. Business Travel Policy (`18_travel_policy.md`)
19. Employee Data Privacy Policy (`19_employee_data_privacy.md`)
20. Employee Offboarding Policy (`20_offboarding_policy.md`)

The existing `data/questions.csv` and `data/questions_w3.csv` files will remain
useful as baseline questions about RAG, APIs, and agent behavior. They will be
supplemented with an HR evaluation set covering policy lookup, eligibility,
multi-document synthesis, citation accuracy, ambiguous questions, and unsafe or
out-of-scope requests.

## Decision — Solution Framing Canvas

| Box | Your Answer |
|-----|-------------|
| **Inputs** | A natural-language HR question; optionally a conversation turn or a document version filter. File uploads and employee-specific records are out of scope for v1. |
| **Outputs** | A concise answer grounded in retrieved policy passages, citations to source documents and sections, a confidence signal, and an escalation message when the evidence is missing or the topic is sensitive. |
| **Tools** | Document loader and parser, chunker, embedding model, vector store/retriever, optional reranker, LLM, and structured logging/evaluation store. |
| **Memory** | No durable personal memory in v1. The assistant may use the current conversation context, but must not retain employee-identifying details as user memory. |
| **Autonomy level** | Retrieval-augmented assistant with limited agent behavior: it may classify a question, retrieve and compare sources, and compose a cited response. It does not execute HR actions or make employment decisions. |
| **Decision boundaries** | It may explain published policy, identify relevant forms/processes, compare applicable rules, and suggest the correct HR channel. A human must handle legal interpretation, complaints, investigations, accommodations, disciplinary action, termination, pay disputes, exceptions, and any decision about an individual. |

## Consequences

### Positive

- Provides a single searchable interface over a small, reviewable HR knowledge base.
- Grounds answers in citations, making them easier to verify and audit than free-form chat.
- Creates a repeatable evaluation set from the existing questionnaires plus HR-specific questions.
- Makes uncertainty and escalation explicit instead of encouraging confident guesses.

### Negative / Risks

- HR policies change; stale documents can produce materially wrong answers unless ownership and review dates are maintained.
- Similar policies may conflict by country, worker type, or effective date, so metadata filtering and source precedence are required.
- Sensitive questions need careful privacy handling, refusal language, and human escalation; the assistant must not present guidance as legal or employment advice.
- Retrieval failures and incomplete corpus coverage can cause plausible but unsupported answers, so citation and abstention tests are required.

### Things We'll Re-visit

- Corpus governance: document owners, effective dates, approval workflow, and expiry/re-indexing rules.
- Metadata and access controls for geography, employment type, and policy audience.
- Retrieval and reranking strategy, chunk size, citation format, and confidence thresholds.
- Privacy, authentication, audit logging, retention, and redaction before any real HR data is introduced.
- Agent tool permissions and human handoff workflow for later agentic releases.

## W6 — Naive RAG live

**Decision:** Naive RAG is now the default answer path. `/ask_batched` retrieves
top-3 chunks from `data/corpus/` before generating.

**Baseline KPIs** (see docs/kpi/wk6-snapshot.md):
- Cost/query: $0.000XXX
- Latency p50: XXX ms
- Grounded response rate: XX%

**Top 3 known limits** (to be addressed W7-W11):
1. Chunking cuts mid-sentence — W7 fixes with structure-aware chunker
2. Retrieval is pure dense — W9 adds BM25 hybrid
3. No metadata filtering — W7 introduces via Qdrant payload

**Status:** In production for the demo API. Not yet suitable for real users;
retrieval quality needs W7-W9 improvements first.

## Section 4 — Decisions locked at M1

| Decision area | M1 evidence | Decision locked |
|---|---|---|
| Default model | Lab 4, 10 questions per model: `gpt-4o-mini` cost $0.000839 total ($0.000084/query average) and took 20.72 s; `gpt-4o` cost $0.015688 total ($0.001569/query average) and took 24.72 s. `gpt-4o` cost about 18.7x more. | Use `gpt-4o-mini` by default for straightforward questions; use `gpt-4o` for high-impact, ambiguous, or multi-step questions when its added quality is justified. |
| M1 answer-quality baseline | W5 eval-run-001: 20 golden questions; mean accuracy 2.5/4, groundedness 2.5/4, and format 3.15/4. | Keep the 20-question golden-set evaluation as the quality baseline and improve accuracy and groundedness before real-user use. |
| Cost and quality trade-off | Lab 4 found similar answers for most questions, with clearer `gpt-4o` gains on schema-version reasoning and somewhat more precise usage reporting. | Do not use the higher-cost model universally; reserve it for cases where reasoning quality matters. |

## Section 5 — Sponsor KPIs

These are three sponsor KPIs selected from the Stakeholder Map. Targets are for W12 / DR #2. Baselines are M1 evidence available on 2026-10-04; items not instrumented are called out explicitly.

| KPI | M1 measurement | W12 target |
|---|---|---|
| Answer quality | W5 eval-run-001: mean accuracy 2.5/4 (62.5% of the maximum); citation correctness and user usefulness were not separately measured. | At least 85% of monthly evaluation answers are supported and correctly cited; at least 80% of sampled users rate answers useful. |
| Safety and governance | No sensitive/out-of-scope red-team cases were reported as run (0 cases measured). Corpus audit: 20/20 documents name a policy owner or responsible function; 0/20 state an explicit review date. | At least 95% of sensitive/out-of-scope tests are correctly refused or escalated; 100% of indexed documents have an owner and review date. |
| Time and HR workload | Stakeholder-map workflow estimate: 10–15 minutes to find an answer through current search and follow-up. Routine HR tickets per 100 employees have no measured M1 baseline. | Median time to a useful answer under 60 seconds; routine HR tickets per 100 employees reduced by 20% within one quarter of launch. |

## Section 6 — Evaluation baseline

W5 `eval-run-001` (`run_id: 1790942211`) evaluated 20 golden questions:

| Aggregate metric | Baseline |
|---|---:|
| Mean accuracy | 2.5 / 4 |
| Mean groundedness | 2.5 / 4 |
| Mean format | 3.15 / 4 |
| Golden questions | 20 |

Source: `docs/eval-run-001.md`. These are judge scores, not percentages of answers passing a citation or safety threshold.

## Section 9 — Open questions

1. What citation correctness rate do employees achieve on real questions, beyond the current aggregate groundedness score?
2. Which sensitive and out-of-scope scenarios must be included in the refusal and escalation test set, and who approves its coverage?
3. What are the measured production baselines for time to a useful answer and routine HR tickets per 100 employees, segmented by geography and employee type?

## Section 10 — DR #1 defence


## Section 11 — Change log

| Date | Change |
|---|---|
| 2026-10-04 | Added M1 model and evaluation decisions, three sponsor KPI baselines and W12 targets, the W5 evaluation aggregate, three open questions, and the reserved DR #1 defence section. |
