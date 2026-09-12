# ADR-0001: Capstone Framing - Knowledge Assistant

- **Status:** Draft v1
- **Date:** 2026-08-16
- **Author:** Dinesh Karthick

## Context

What problem is this capstone trying to solve, for whom, and why now? (2–3 sentences)

## Decision — Solution Framing Canvas

| Box | Your Answer |
|-----|-------------|
| **Inputs** | What the user / caller sends — text, file uploads, parameters |
| **Outputs** | What the system produces — a text answer, a citation list, a structured result |
| **Tools** | What external services it uses — OpenAI, your retriever, a database, … |
| **Memory** | What the system remembers between calls — nothing, last N turns, durable history |
| **Autonomy level** | On the spectrum from chatbot to agentic system, where this sits and why |
| **Decision boundaries** | What it's allowed to decide on its own, vs. what needs a human |

## Consequences

### Positive

- What this design unlocks (bullet point 1)
- What this design unlocks (bullet point 2)
- What this design unlocks (bullet point 3)

### Negative / Risks

- What's harder / costlier / riskier because of this choice (bullet point 1)
- What's harder / costlier / riskier because of this choice (bullet point 2)
- What's harder / costlier / riskier because of this choice (bullet point 3)

### Things We'll Re-visit

- Specific thing we'll come back to in later ADRs (1)
- Specific thing we'll come back to in later ADRs (2)