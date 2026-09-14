# MP1 Prompt Strategy Comparison

## Step 5 summary: latest results

The final summary table from Step 5 showed the following comparison across the four prompt strategies:

| Strategy | Accuracy (mean of 3) | Parse rate | Judge score | Total cost ($) | Latency p50 (s) |
|---|---:|---:|---:|---:|---:|
| zero_shot | 2.7 | 1.0 | 3.8 | 0.000 | 1.756 |
| few_shot | 2.9 | 1.0 | 3.9 | 0.001 | 1.886 |
| structured | 2.8 | 1.0 | 3.9 | 0.000 | 2.020 |
| cot | 2.7 | 1.0 | 3.7 | 0.000 | 1.760 |

## Quick takeaways

- The few_shot prompt had the best exact-match accuracy at 2.9 and tied the structured prompt for the highest judge score at 3.9.
- All four strategies had a parse rate of 1.0, so every response produced a parseable extraction in this run.
- The zero_shot prompt was the fastest at 1.756s, closely followed by cot at 1.760s. The structured prompt was slowest at 2.020s.
- The few_shot prompt was the only strategy with a rounded total cost above zero, at $0.001; the other strategies rounded to $0.000.
- The cot strategy had the lowest accuracy and judge score, tying zero-shot on accuracy but scoring lower with the judge.

## Final conclusion from Step 5

From the latest results, the few_shot prompt is the strongest overall choice for this small evaluation because it had the highest accuracy and tied for the highest judge score, while maintaining a 100% parse rate. The structured prompt was close behind and had the same judge score, but it was slower. Zero-shot remains a useful low-latency baseline, while chain-of-thought performed worst on both accuracy and judge score in this run.
