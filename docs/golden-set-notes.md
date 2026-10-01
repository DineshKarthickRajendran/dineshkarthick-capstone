# Golden Set Notes

## Purpose

This document explains how the 20-entry HR policy golden set was constructed, why each entry belongs in its evaluation bucket, and what makes the harder cases useful for testing retrieval and answer quality.

The golden set was created against the 20 synthetic HR policy documents in the accompanying policy dataset. The goal was not to generate arbitrary questions, but to turn concrete policy statements into realistic user questions that can test whether an HR-policy RAG system retrieves the right evidence and answers without inventing rules that are not present in the source material.

## 1. Sourcing

Each golden-set question was sourced directly from one or more of the 20 policy documents. The documents cover common HR topics such as leave, expenses, work from home, BYOD, attendance, conduct, recruitment, onboarding, performance, promotion, training, grievances, harassment, confidentiality, IT use, travel, employee privacy, and offboarding.

For the happy-path entries, the question normally targets one policy and one clearly stated rule. Examples include:

- Annual leave accrual from the Leave Policy.
- Receipt requirements from the Expense Reimbursement Policy.
- Remote-work eligibility from the Work From Home Policy.
- Lost-device reporting from the BYOD Policy.
- Casual Friday rules from the Dress Code Policy.
- Standard working hours from the Attendance Policy.

For the harder and edge entries, the questions deliberately cross policy boundaries. The expected answer therefore requires combining evidence from multiple documents rather than finding a single matching paragraph.

No policy rule was intentionally added merely to make a question interesting. Where the source documents do not specify an exact answer, the ideal answer explicitly preserves that uncertainty rather than supplying a plausible-sounding rule.

## 2. Bucket Reasoning

The set contains exactly 20 entries:

- **14 happy-path**
- **4 harder / multi-file**
- **2 edge cases**

### Happy-path: 14 entries

The happy-path questions represent normal employee requests that an HR assistant should be able to answer with straightforward retrieval.

These entries were chosen to cover a broad spread of the policy corpus rather than concentrating all questions on leave or expenses. They cover leave, expenses, WFH, BYOD, dress code, attendance, conduct, remote security, recruitment, onboarding, performance, promotion, training, and grievances.

The expected behavior for these questions is:

1. Retrieve the relevant policy.
2. Identify the specific rule.
3. Give a concise answer.
4. Preserve important thresholds, conditions, or approval requirements.

The happy-path questions are phrased as ordinary employee questions rather than as document-search prompts. For example, instead of asking for a section heading, the set asks questions such as:

> "What is the receipt requirement for an expense claim?"

and

> "Do new job openings need approval before recruiting starts?"

This makes the benchmark closer to an actual HR assistant workload.

### Harder: 4 entries

The four harder entries require information from multiple related policies.

**g015 — Business travel + expenses**

The question asks about hotel approval and the applicable spending limit. The answer requires connecting the Business Travel Policy's pre-booking approval requirement with the Expense Reimbursement Policy's $150/night hotel cap.

**g016 — WFH + BYOD**

The question combines remote work with use of a personal laptop. The answer requires both the BYOD security requirements and the rules governing company data storage. This tests whether retrieval can find related security constraints instead of answering only the device-eligibility portion.

**g017 — WFH + attendance**

The question asks whether remote employees remain subject to normal attendance and availability expectations. The answer combines WFH requirements such as agreed schedules, core hours, and required meetings with the general attendance policy.

**g018 — Leave + offboarding**

The question asks how unused leave interacts with final pay. The answer requires both the Leave Policy and Offboarding Policy. Importantly, the documents do not provide a universal numerical payout formula, so the ideal answer does not invent one.

These questions are harder because retrieving only one of the relevant documents can produce an incomplete answer even if the retrieved document is individually relevant.

### Edge cases: 2 entries

The two edge cases are designed to test whether the RAG system knows when the source material is insufficient to support an exact answer.

**g019 — Exact leave payout**

The user supplies a specific employment duration and number of unused leave days and asks for an exact amount of money. The policies establish how leave accrues and state that final pay may include applicable leave adjustments, but they do not specify the formula needed to calculate a cash amount.

A correct system should therefore say that the exact amount cannot be calculated from these policies and direct the employee to HR or Payroll. Producing a precise monetary figure would be a hallucination.

**g020 — International remote work + BYOD + data storage + expenses**

This is intentionally a multi-hop scenario. It combines:

- Working remotely from another country.
- Using a personal laptop.
- Storing company files in personal cloud storage.
- Claiming home internet and other remote-work costs.

The answer requires evidence from WFH, BYOD, confidentiality/data-handling, and expense-related rules. It also tests whether the system can distinguish a policy requirement from an unresolved country-specific question.

The source policies require prior approval for international remote work and identify relevant functions such as HR, Information Security, tax, immigration, and the manager when applicable. They also restrict personal-device use to supported and secure configurations, prohibit storing company files in personal cloud services, and state that household/remote-work costs are not automatically reimbursable.

However, the documents do not establish a country-specific legal or tax outcome or guarantee approval of a particular expense. The golden answer intentionally leaves those questions unresolved.

## 3. What Was Hard

The main challenge was making the questions difficult enough to test retrieval without making them artificial.

### A. Avoiding keyword-only questions

A weak benchmark can be solved by matching an obvious keyword to a document title. The questions therefore use natural employee language. For example, an employee might say "I lost my personal phone that has company apps on it" rather than "What is the BYOD lost-device procedure?"

### B. Testing multi-document retrieval

The harder cases were selected where two or more policies contain complementary pieces of the answer. This is important because a RAG system can appear strong on single-document questions while failing when evidence is distributed across documents.

### C. Testing thresholds and conditions

Several questions depend on exact policy details rather than general topic matching:

- 18 annual leave days per year.
- 1.5 annual leave days per completed month.
- $25 receipt threshold.
- $150/night hotel cap.
- 9:00 a.m.–6:00 p.m. standard schedule.
- First 30-day onboarding check-in.

These details make it possible to detect answers that are broadly relevant but numerically wrong.

### D. Testing abstention and uncertainty

The edge cases deliberately ask for information the policies do not fully define. This is important for a real HR assistant: a system should not convert an incomplete policy into a fabricated formula, entitlement, or country-specific legal conclusion.

For g018 and g019, the absence of an exact leave-payout formula is itself part of the expected answer.

### E. Preserving approval chains

Many HR rules depend on approval rather than being absolute permissions. The dataset therefore includes approval-related requirements such as manager approval, approved headcount, HR/Finance/Procurement involvement, and prior approval for international remote work.

### F. Covering different policy domains

The 20 questions intentionally span many documents so that retrieval quality is not measured against one topic alone. This gives reviewers a more realistic view of whether the system can navigate the entire synthetic HR policy corpus.

## 4. What Makes This a Golden Set

Each entry contains five fields:

- `id` — stable identifier for the evaluation case.
- `question` — the user-style query presented to the RAG system.
- `ideal_answer` — the substantive answer expected from the source policies.
- `notes` — the evaluation bucket and, for harder cases, the reason the case requires additional reasoning.
- `must_mention` — key facts that should appear in a successful answer.

The `must_mention` values are not intended to require one exact wording. They identify important facts, constraints, thresholds, or uncertainty that a good answer should preserve.

The ideal answers are also intentionally not over-specified. If the source policies do not establish a fact, the golden answer does not invent it. This is especially important for edge cases because a RAG evaluation set should reward grounded answers rather than confident fabrication.

## 5. Evaluation Philosophy

The golden set is intended to evaluate more than whether a retrieved document looks relevant.

A strong result should demonstrate:

1. **Retrieval relevance** — the system finds the policy documents containing the necessary evidence.
2. **Coverage** — multi-policy questions retrieve all important sources.
3. **Grounded answering** — the final answer stays within the documented policies.
4. **Numerical accuracy** — thresholds, limits, and schedules are reproduced correctly.
5. **Condition awareness** — approval requirements and exceptions are preserved.
6. **Abstention when necessary** — the system does not invent an answer when the corpus does not provide enough information.

This makes the harder and edge cases particularly useful for DR #1 review: they provide evidence that the benchmark is testing retrieval and grounded synthesis rather than simply checking whether a model can repeat isolated policy sentences.

## 6. Summary of the 20 Cases

| ID | Bucket | Main source(s) | What it tests |
|---|---|---|---|
| g001 | Happy | Leave | Annual leave accrual |
| g002 | Happy | Expenses | Receipt threshold and exception |
| g003 | Happy | WFH | Remote-work eligibility |
| g004 | Happy | BYOD | Lost-device response |
| g005 | Happy | Dress Code | Casual Friday conditions |
| g006 | Happy | Attendance | Standard working hours |
| g007 | Happy | Code of Conduct | Reporting channels |
| g008 | Happy | Remote Security | Phishing response |
| g009 | Happy | Recruitment | Headcount/budget approval |
| g010 | Happy | Onboarding | First-30-day check-in |
| g011 | Happy | Performance | Ongoing feedback |
| g012 | Happy | Promotion | Promotion-readiness factors |
| g013 | Happy | Training | Approval before spending |
| g014 | Happy | Grievance | Formal grievance path |
| g015 | Harder | Travel + Expenses | Cross-policy hotel rules |
| g016 | Harder | WFH + BYOD | Device and data-security rules |
| g017 | Harder | WFH + Attendance | Remote attendance expectations |
| g018 | Harder | Leave + Offboarding | Final-pay handling and missing formula |
| g019 | Edge | Leave + Offboarding | Exact payout cannot be derived |
| g020 | Edge | WFH + BYOD + Confidentiality + Expenses | Multi-hop constraints and uncertainty |

## 7. Reviewer Takeaway

The set was constructed from the actual rules in the 20 synthetic source documents, with the difficulty increasing from direct retrieval to multi-document synthesis and finally to cases where the correct behavior is to recognize that the corpus does not contain enough information for an exact answer.

The most important design choice is that the golden set does **not** treat a plausible answer as a correct answer. For the edge cases, a response that confidently invents a payout formula, country-specific rule, or reimbursement entitlement should be considered worse than an answer that explicitly identifies the information gap and points to the appropriate HR/Payroll or approval process.

That distinction is what makes the set useful for evaluating a grounded HR-policy RAG system rather than merely evaluating general question-answering ability.
