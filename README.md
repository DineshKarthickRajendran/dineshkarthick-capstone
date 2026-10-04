# Capstone — Knowledge Assistant

A 30-week build of a Q&A assistant over a small document corpus, completed as part of the *Agentic AI & RAG Engineering* programme.

## Corpus

My capstone corpus: 20 HR policy documents in `data/corpus/`, covering leave, expenses, remote work, BYOD, dress code, attendance, conduct, security, recruitment, onboarding, performance, promotion, training, grievances, harassment, confidentiality, acceptable use, travel, employee data privacy, and offboarding. The planned document set is recorded in [the capstone framing ADR](docs/adr/0001-capstone-framing.md).

## Structure

- `src/` — application code
- `docs/adr/` — Architecture Decision Records (one per major design choice)
- `docs/runs/` — saved LLM outputs for evidence and reference

## Week 1

- [x] Set up repo + secrets discipline
- [ ] Build `hellollm.py` (Lab Step 2)
- [ ] Write ADR v1 (Lab Step 3)