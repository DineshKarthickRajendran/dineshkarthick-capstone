# MP1 Prompt Lab Reflection

The strategies are discussed in the same order as the `STRATEGIES` variable: `Zero_shot`, `Few_shot`, `Structured`, and `CoT`.

## 1. Which strategy won, and on what dimension?

CoT was the strongest overall strategy in this run. It tied Few_shot for the highest accuracy at 2.90 out of 3 fields, achieved the highest judge score at 25.00 out of 25, and maintained a 100.00% parse rate. Structured was the fastest at 1.663 seconds and scored 24.38 out of 25, so it was the best choice on latency and a strong alternative for a production pipeline. Few_shot also reached 2.90 accuracy, but its judge score was lower at 23.75 and it had the highest cost at $0.00047760. Zero_shot had the lowest cost at $0.00029280, but its 0.00% parse rate made the output unusable.

Accuracy measures the mean number of correct values among `company_name`, `job_role`, and `minimum_years_experience`. Parse rate measures whether the response could be loaded as valid JSON. Judge score is the evaluator's 1-to-4 result rescaled to 25 points. These metrics show why cost alone is not a useful winner criterion: Zero_shot was cheapest, but it produced no usable records, while CoT provided the best quality and reliable parsing.

## 2. What surprised you?

The biggest surprise was the complete Zero_shot failure. Its cost was only $0.00029280, but its parse rate and accuracy were both 0.00%, and its judge score was only 6.25 out of 25. This shows that a short prompt can be operationally worse than a slightly more detailed prompt when the output contract is not enforced clearly.

It was also notable that CoT performed well despite using a very small number of instructions: it reached 2.90 accuracy, a perfect 25.00 judge score, and a 100.00% parse rate. Structured was not the most accurate strategy, but it was fastest and still scored 24.38 out of 25. For an HR knowledge assistant, the equivalent risk is not only malformed output but also a confident answer based on the wrong policy version, employee group, location, or effective date.

## 3. For your capstone domain, which strategy would you reach for first?

My capstone will be an HR knowledge enterprise assistant that helps employees and HR teams find reliable answers about policies, benefits, leave, onboarding, payroll processes, and compliance procedures. I would reach for CoT first because it produced the best combination of accuracy, judged quality, and parse reliability, which is valuable when the assistant must identify the user's intent, locate the relevant policy, and distinguish exceptions or eligibility conditions. I would use Structured for the final answer contract so every response can include an answer, source citation, policy effective date, confidence, and an escalation flag.

## 4. If you had another day, what would you try next?

I would first build a domain-specific evaluation set for the HR assistant, covering policy version conflicts, location-specific benefits, employee-type differences, leave eligibility, payroll cut-off dates, and questions that should be escalated to HR. I would compare retrieval quality as well as answer quality by measuring citation correctness, groundedness, refusal accuracy, and whether the assistant identifies when the knowledge base does not contain enough information.

I would also test a model with native structured-output or JSON-schema support and compare it with the current model. Finally, I would add deterministic validation and enterprise safeguards: require source citations and policy effective dates, apply role-based access controls to sensitive HR documents, prevent exposure of personal employee data, reject unsupported claims, and route high-risk questions to a human HR specialist. These changes would directly address the Zero_shot failure while making the system appropriate for confidential, policy-sensitive HR use.
