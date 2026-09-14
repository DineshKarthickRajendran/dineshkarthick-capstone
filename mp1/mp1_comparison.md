# MP1 Prompt Strategy Comparison

## Step 5 summary

The results below follow the same order as the `STRATEGIES` variable definition: `Zero_shot`, `Few_shot`, `Structured`, and `CoT`.

| Strategy | Accuracy (mean of 3) | Parse rate (%) | Judge score (out of 25) | Total cost ($) | Latency p50 (s) |
|---|---:|---:|---:|---:|---:|
| Zero_shot | 0.00 | 0.00% | 6.25 | 0.00029280 | 1.754 |
| Few_shot | 2.90 | 100.00% | 23.75 | 0.00047760 | 1.724 |
| Structured | 2.80 | 100.00% | 24.38 | 0.00042000 | 1.663 |
| CoT | 2.90 | 100.00% | 25.00 | 0.00042150 | 1.697 |

## Quick takeaways

- CoT and Few_shot tied for the highest accuracy at 2.90 out of 3. CoT had the highest judge score at 25.00 out of 25.
- Few_shot produced a judge score of 23.75 out of 25, while Structured scored 24.38 despite its lower accuracy of 2.80.
- Few_shot, Structured, and CoT all achieved a 100.00% parse rate, while Zero_shot achieved 0.00%.
- Structured had the lowest latency at 1.663 seconds. CoT followed at 1.697 seconds, Few_shot at 1.724 seconds, and Zero_shot at 1.754 seconds.
- Zero_shot had the lowest cost at $0.00029280, but its complete parse failure made that apparent saving operationally meaningless. Few_shot cost the most at $0.00047760.

## Final conclusion from Step 5

CoT is the best overall choice in this run because it combined a perfect judge score of 25.00 out of 25, tied for the highest accuracy at 2.90 out of 3, and maintained a 100.00% parse rate. Structured is the fastest option at 1.663 seconds and scored 24.38 out of 25, making it a strong latency-focused alternative. Few_shot also achieved 2.90 accuracy and may be useful when example-driven behaviour is preferred, although it had the highest cost at $0.00047760. Zero_shot should not be selected for production from this run: its 0.00% parse rate made every downstream extraction unusable despite its low cost. This demonstrates that cost must be evaluated per successful extraction, not in isolation.
