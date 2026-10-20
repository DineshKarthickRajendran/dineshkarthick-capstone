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
- Cost/query: $0.0001251
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


## W7 — Qdrant-backed vector store

**Decision:** Use embedding-based retrieval backed by Qdrant Cloud (free tier)
for the W7 RAG path; retain `naive_rag.py` as the W6 reference implementation.

**Evaluation finding:** On the same 20-question golden set, eval-run-006-W7
reported accuracy improving from 2.85/4 in eval-run-005 to 3.1/4 (+0.25),
groundedness from 2.85/4 to 3.1/4 (+0.25 reported), and format from 3.2/4 to
3.3/4 (+0.1 reported). The per-question rows in eval-run-005 instead yield
groundedness 2.90/4 and format 3.25/4, making the row-derived gains +0.20 and
+0.05 respectively. Accuracy gains are concentrated in g007 and g012 (2 to 4
each) and g020 (1 to 2); g006 and g008 remain weak at 1/4 for accuracy and
groundedness. Treat this as a positive run-to-run result, not proof that Qdrant
alone caused the improvement, because the reports do not confirm every other
run condition was held constant.

**Vector stack:**
- Embedding model: text-embedding-3-small (1536 dims, $0.02 per 1M tokens)
- Vector store: Qdrant Cloud
- Distance metric: cosine (programme default; see W7 Track A Day 2 for why)
- Index: HNSW with defaults (m=16, ef_construct=100)

**Rejected alternatives:**
- text-embedding-3-large — 6.5× cost, insufficient quality gain on our corpus (see Lab Step 2)
- FAISS — no service layer; we need persistence + REST
- Chroma — smaller ecosystem, less battle-tested
- pgvector — no existing Postgres; not worth adding

**Operational KPIs** (see docs/kpi/wk7-snapshot.md):
- Persistence: Qdrant-managed (was: JSON file on disk)
- Restart cost: O(1) — no re-load of vectors into memory
- Ready for W8 metadata filtering
- Evaluation: see `docs/eval-run-006-W7.md` for the comparison and remaining low-scoring questions

### Embedding-model comparison

**Final default:** Keep `text-embedding-3-small` for the capstone's default
retrieval path. On the same 20 golden questions and isolated Qdrant collections,
small achieved **20/20 hit@3 (100%)**, compared with **19/20 (95%)** for
`text-embedding-3-large`. Large scored higher on mean accuracy (3.15 vs 2.90),
groundedness (3.10 vs 2.90), and format (3.40 vs 3.20), but missed the expected
code-of-conduct source for g007. It also had higher average query cost
($0.00007785 vs $0.00007675), higher candidate p50 latency (2986.8 vs 2777.5 ms),
and about 6.5x higher corpus indexing cost ($0.00299390 vs $0.00046060).

The default prioritizes complete expected-source retrieval on this evaluation
set, lower latency, and lower index-build cost. Large remains a possible
targeted option if its judge-score advantage is valuable for quality-critical
queries. This is a limited 20-question result, not a universal model ranking;
the small-versus-large run details and hit@3 definition are in
`docs/kpi/w7-comparions.md`.

## W8 — Structure-aware ingestion + PII discipline

**Decision:** Capstone corpus is now ingested via `src/ingest/pipeline.py`,
which parses by extension, chunks recursively (structure-aware where possible),
scrubs PII with regex + Presidio, enriches with the 11-field metadata schema,
and upserts to `capstone_chunks_v2`.

**Ingestion pipeline steps:**
1. Parse (PyMuPDF for PDF, BeautifulSoup for HTML, python-docx for DOCX)
2. Chunk (recursive, max_size=400)
3. Scrub PII (regex + Presidio + audit)
4. Enrich metadata (11 fields: chunk_id, source, doc_type, section_path, page,
   date, language, version, ingested_at, text, pii_flags_count)
5. Embed (text-embedding-3-small)
6. Upsert (Qdrant collection capstone_chunks_v2)

**PII detection:** hybrid regex + Presidio. Regex targets EMAIL, PHONE, and
EMP_ID; Presidio targets PERSON, LOCATION, and ORGANIZATION. The W8 collection
contains 800 chunks from 20 documents. The audit recorded 74 detector flags
across 59 chunks (7.4% of chunks flagged). These are review signals, not
independently verified PII items or a measured false-positive rate. The supplied
10-chunk scroll was the first page, all from one leave-policy document, not a
random corpus sample; see `docs/wk8-pii-audit.md`.

**Evaluation finding:** The same 20 standard golden questions were run against
W7 `capstone_chunks` (`eval-run-008-small-embedding-20261014`) and W8
`capstone_chunks_v2` (`eval-run-w8-chunks-20261017-final`). W8 retained the same
retrieval rates: 20/20 any-source hit@3 (100%), 17/20 complete-source hit@3
(85%), and 91.2% mean expected-source coverage. However, mean accuracy decreased
from 2.90/4 to 2.30/4 (-0.60), groundedness from 2.90/4 to 2.45/4 (-0.45), and
format from 3.20/4 to 3.00/4 (-0.20). Candidate cost/query decreased from
$0.00007675 to $0.00004973 (-35.2%) and candidate latency p50 from 2777.5 ms to
2652.1 ms (-4.5%). These are run-to-run observations, not a controlled ablation:
metadata is stored in W8, but the current retrieval query does not yet apply
metadata filters. Retrieval hit rate did not improve, and retrieving expected
sources did not guarantee a correct, grounded answer. Detailed results are in
`docs/eval-run-w8-chunks-20261017-final.md` and `docs/kpi/wk8-snapshot.md`.

**Known gaps:** The PII flags have not been manually adjudicated; detector recall
and false-positive rate are unknown. The sample scroll is not representative.
The current top-k retrieval does not filter on metadata. The standard 20-question
evaluation is small, and W8 judge scores declined despite unchanged source-hit
metrics; broaden evaluation and inspect low-scoring answers before attributing
results to recursive chunking or PII scrubbing.

**Data residency:**
- Embeddings computed by: OpenAI API (US)
- Vectors stored at: Qdrant Cloud, AWS `eu-west-1` (based on configured endpoint)
- LLM inference at: OpenAI API; processing region not independently verified
- App layer: local demo/API for this evaluation; production hosting not selected
- Cross-jurisdictional flows: corpus text is sent to OpenAI for embeddings and
  generation; vectors are stored in Qdrant Cloud `eu-west-1`. Confirm provider
  processing, retention, and residency terms before using real employee data.

**Rejected alternatives:**
- Structure-aware chunking on all doc types — DOCX supports it well;
  PDFs would need custom logic per document; not worth it for MVP.
- Semantic chunking as default — cost-prohibitive at corpus scale.
- Presidio only (no regex) — slower; misses obvious patterns Presidio
  weights lower.

**Operational KPIs** (see docs/kpi/wk8-snapshot.md):
- Collection: 800 points, cosine, 1536-dimensional `text-embedding-3-small` vectors
- Payload: 11 fields per chunk; metadata filtering is possible from stored fields
  but is not yet enabled in the retrieval query
- PII detector: 74 flags across 59 chunks; manual adjudication remains open
- Evaluation: any-source hit@3 100%, complete-source hit@3 85%, source coverage
  91.2%; mean accuracy 2.30/4, groundedness 2.45/4, format 3.00/4
- Candidate cost/query $0.00004973 average; candidate p50 latency 2652.1 ms
- Compared with W7, retrieval metrics were unchanged, judge scores declined, and
  cost and latency were lower; this run does not isolate causality

## W9 — Hybrid retrieval + cross-encoder reranking

**Decision:** Capstone retrieval upgrades from pure dense to hybrid+rerank.

**Retrieval stack:**
- BM25 library: rank-bm25 (BM25Okapi)
- Tokenization: lowercase + alphanumeric-with-hyphens-and-slashes (preserves 'AC-1042', '/v2/dashboards')
- Dense model: text-embedding-3-small (1536 dim, unchanged from W7)
- Fusion: RRF with k=60 (Cormack 2009 default)
- Reranker: cross-encoder/ms-marco-MiniLM-L-6-v2 (local CPU, ~80MB)
- Rerank input: top-10 from hybrid retrieve
- Rerank output: top-3 final

**Rejected alternatives:**
- Cohere Rerank API — paid ($1/1000 reranks), no meaningful accuracy lift on our corpus vs local cross-encoder
- Weighted score fusion (instead of RRF) — requires per-corpus weight tuning; RRF is tuning-free
- Larger cross-encoder (ms-marco-MiniLM-L-12-v2, ~120MB) — 2× slower for negligible accuracy lift on English enterprise docs
- LlamaIndex framework — retrieval fits comfortably in ~140 LOC; framework overhead not justified yet (revisit at W12+)

**Operational KPIs** (see docs/kpi/wk9-snapshot.md):
- W9 evaluation: 20 questions via the active `src.api.main` `/ask_w9` endpoint
  and `data/golden_set_w9.jsonl`
- Any expected-source hit@3: 20/20 (100%); complete-source hit@3: 18/20 (90%);
  expected-source coverage@3: 95.0%
- Mean judge scores: accuracy 2.50/4, groundedness 2.55/4, format 3.00/4;
  8/20 answers scored at least 3/4 on groundedness
- Candidate cost/query: $0.00005168 average; candidate p50 latency: 2797.2 ms
- W8 comparison: any-source hit@3 unchanged at 100%; complete-source hit@3
  improved from 85% to 90%, coverage from 91.2% to 95.0%, accuracy from 2.30
  to 2.50, and groundedness from 2.45 to 2.55. Format remained 3.00. Candidate
  cost rose by $0.00000195/query and p50 latency by 145.1 ms.
- This is a 20-question observational comparison, not an ablation. Source-level
  hit@3 does not establish passage-level precision; precision@5 remains
  unmeasured. See `docs/kpi/wk9-snapshot.md` for definitions and caveats.

**Known gaps to revisit:**
- BM25 index rebuilt from Qdrant scroll at process start (~2s for 300 chunks). For larger corpora, persist to disk (W10 caching topic).
- Cross-encoder is CPU-bound; consider GPU or batch reranking if query volume grows.
- Some answers abstained despite retrieving the expected source; improve
  passage-level relevance evaluation and inspect low-scoring questions before
  attributing answer-score changes to the retrieval upgrade.
