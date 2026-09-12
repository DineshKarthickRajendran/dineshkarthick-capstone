# ADR-0001: Capstone Framing - Knowledge Assistant

- **Status:** Draft v1
- **Date:** 2026-08-16
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

Planned document set (15–20 documents):

1. Employee handbook and code of conduct
2. Anti-harassment and respectful workplace policy
3. Equal employment opportunity and non-discrimination policy
4. Recruitment and selection process guide
5. Onboarding and probation guide
6. Working hours, attendance, and timekeeping policy
7. Leave and time-off policy
8. Sick leave and reasonable accommodation process
9. Flexible and remote work policy
10. Compensation and payroll FAQ
11. Benefits enrollment and eligibility guide
12. Performance management and review guide
13. Learning, development, and training policy
14. Internal mobility and promotion process
15. Grievance, complaint, and investigation process
16. Disciplinary and corrective-action process
17. Resignation, termination, and offboarding guide
18. Workplace health, safety, and emergency contacts
19. Data privacy and HR-records handling policy
20. HR systems and service-desk escalation guide

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