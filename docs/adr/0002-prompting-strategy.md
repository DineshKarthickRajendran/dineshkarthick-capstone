# ADR-0002: Prompting Strategy for the HR Knowledge Assistant

- **Status:** Accepted
- **Date:** 2026-09-15
- **Author:** Dinesh Karthick

## Context

The capstone is an HR knowledge assistant for employees, people managers, and
HR operations staff. It must answer questions about policies, benefits, leave,
onboarding, payroll processes, and compliance procedures from a curated,
versioned document corpus. Answers must be useful without becoming unsupported
employment or legal advice.

The MP1 prompt lab compared four strategies on extraction tasks with three
fields: `company_name`, `job_role`, and `minimum_years_experience`.

| Strategy | Accuracy | Judge score | Parse rate | Latency | Cost |
|----------|---------:|------------:|-----------:|--------:|-----:|
| Zero-shot | 0.00 / 3 | 6.25 / 25 | 0.00% | - | $0.00029280 |
| Few-shot | 2.90 / 3 | 23.75 / 25 | - | - | $0.00047760 |
| Structured | - | 24.38 / 25 | - | 1.663 s | - |
| CoT | 2.90 / 3 | 25.00 / 25 | 100.00% | - | - |

The results show that cost alone is not a useful selection criterion. Zero-shot
was the cheapest approach but produced no usable records. CoT produced the best
overall quality and reliability, while Structured was the fastest strong
alternative. In the HR domain, the equivalent failure would be a plausible
answer that uses the wrong policy version, employee group, location, or
effective date.

## Decision

Use a **reasoning-first, structured-output prompt** for the capstone assistant.

### Prompt behavior

The prompt will instruct the model to:

1. Identify the user's intent and any relevant scope such as location,
	 employee type, policy version, or effective date.
2. Use only the retrieved policy passages as evidence.
3. Resolve applicable rules and exceptions before drafting the response.
4. Abstain or escalate when the evidence is missing, conflicting, sensitive,
	 or insufficient to answer safely.
5. Return the final answer in the application schema with source citations and
	 policy metadata.

The model's internal reasoning will not be returned to users or stored in logs.
Users receive the concise conclusion, supporting citations, uncertainty, and
the appropriate HR escalation path.

### Output contract

The preferred response shape is:

```json
{
	"answer": "Concise answer grounded in the retrieved policy.",
	"sources": ["Document title, section"],
	"policy_effective_date": "YYYY-MM-DD",
	"confidence": 0.0,
	"escalation_required": false,
	"escalation_reason": null
}
```

The application will validate the response, reject malformed or unsupported
claims, and require an escalation when the question involves legal
interpretation, complaints, investigations, accommodations, disciplinary
action, termination, pay disputes, exceptions, or an individual employment
decision.

Structured prompting is the production contract even when the model uses
multi-step reasoning internally. A Structured-only prompt remains the fallback
for latency-sensitive requests or models that provide reliable schema support
but do not perform as well on multi-step synthesis. Few-shot examples may be
added selectively for recurring HR formats, but they are not the primary
strategy because they cost more and did not improve judge quality over CoT in
the MP1 run.

## Consequences

### Positive

- Maximizes answer quality and parse reliability based on the MP1 evidence.
- Makes citations, effective dates, confidence, and escalation explicit.
- Supports policy-version and employee-scope checks needed by an HR assistant.
- Allows the UI, API, and evaluation harness to consume a stable response
	schema.
- Keeps reasoning private while preserving a concise, auditable answer.

### Negative / Risks

- Multi-step reasoning can increase latency and token cost compared with a
	short structured prompt.
- Correct prompting cannot compensate for incomplete, stale, or incorrectly
	retrieved policy documents.
- Confidence is a model signal, not proof of correctness; it must be evaluated
	against citation correctness and groundedness.
- Structured output can be syntactically valid while still containing an
	unsupported claim, so schema validation alone is insufficient.

## Evaluation Plan

Before treating the strategy as production-ready, evaluate it on an
HR-specific golden set covering policy lookup, eligibility, multi-document
synthesis, citation accuracy, ambiguous questions, and unsafe or out-of-scope
requests. Track:

- grounded answer accuracy and citation correctness;
- policy effective-date and scope correctness;
- refusal and escalation accuracy;
- JSON/schema parse rate;
- latency, token usage, and cost per request.

The prompting strategy will be revisited if Structured-only prompting matches
CoT quality at materially lower latency or cost, or if domain evaluation shows
that the current prompt produces unsupported answers or misses escalation
cases.
