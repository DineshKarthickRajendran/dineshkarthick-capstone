# DR #1 Summary

## What you built

This capstone is an HR policy knowledge assistant that retrieves from a curated set of 20 HR policy documents and generates concise, evidence-grounded answers. Its primary user is an employee preparing for a 1:1, planning leave, or completing an onboarding or benefits task who needs a clear answer, a source citation, and a next step. The value is faster policy lookup with less repeated searching by employees, managers, and HR, while sensitive or unsupported questions remain routed to a human. The current implementation is a demo API using naive RAG with the top three retrieved chunks; it is not ready for real users because chunking, retrieval quality, and metadata filtering still need work.

## What you measured

W5 `eval-run-001` evaluated 20 golden questions and recorded mean accuracy of **2.5/4**, groundedness of **2.5/4**, and format of **3.15/4**. Format is currently the strongest dimension, while the accuracy and groundedness scores show that answer correctness and evidence support need improvement before real-user use. These are judge scores, not percentages of answers that pass a citation or safety threshold; citation correctness and sensitive-case handling were not measured separately.

## Top 3 things to discuss

1. **Retrieval priority:** Given the 2.5/4 accuracy and groundedness baseline, which W7 change should come first: structure-aware chunking, metadata filtering, or stronger citation enforcement? What evaluation slice would best tell us whether it helped?
2. **Golden-set coverage:** Are 20 questions enough to guide the next iteration? Which specific cases should be added first to cover geography or employee type, ambiguous policy wording, and cross-policy questions?
3. **Sensitive-question handling:** For questions involving complaints, accommodations, or other sensitive topics, where should the assistant abstain and hand off to HR? What should count as a successful refusal or escalation in the evaluation set?

## What you'll defend if asked

- **Why use `gpt-4o-mini` by default?** In the W4 comparison, it averaged **$0.000084 per question** versus **$0.001569** for `gpt-4o`; `gpt-4o` cost about **18.7x more** and took 24.72 seconds versus 20.72 seconds for the mini model. Most answers were similar, while `gpt-4o` showed clearer value on more demanding schema-version reasoning. The decision is to use the mini model for straightforward questions and reserve `gpt-4o` for ambiguous, multi-step, or high-impact cases where its extra quality is worth the cost.
- **Who is the specific user?** An employee preparing for a 1:1, planning leave, or completing an onboarding or benefits task, who may not know the policy title or HR terminology. The assistant explains published policy; it does not decide individual eligibility or replace HR review.
- **Why is the golden set only 20 questions?** It is the current W5 baseline covering the initial policy question set, small enough to run and inspect consistently while the retrieval pipeline is changing. It is a starting point, not evidence of launch readiness; it needs broader coverage for geography and employee type, ambiguity, citations, and sensitive or out-of-scope requests.