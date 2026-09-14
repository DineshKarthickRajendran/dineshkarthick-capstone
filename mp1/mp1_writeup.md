# MP1 Prompt Lab Reflection

## 1. Which prompt strategy performed best, and why?

From the Step 5 results, the few-shot prompt performed best on exact-match accuracy, with a mean score of 2.9 out of 3. It also tied the structured prompt for the highest judge score at 3.9. The examples gave the model concrete guidance for identifying company names, roles, and experience requirements. The structured prompt was a close second with 2.8 accuracy and a 3.9 judge score, while zero-shot and chain-of-thought both scored 2.7 on accuracy. All four strategies had a 1.0 parse rate.

## 2. What did you learn about prompt design and model reliability?

I learned that even small prompt changes can make a big difference. When the model is asked to return exact JSON and to use `null` when information is missing, it is much more likely to behave correctly. I also learned that AI models can sometimes sound confident even when they are guessing, which is a big issue in extraction tasks. The Step 5 summary showed that parse success stayed at 1.0 for all strategies, which means the output format was mostly valid, but quality still changed depending on the prompt. That taught me that prompt design is not only about format, but also about reducing hallucinations and making the answer more trustworthy.

## 3. How did the strategies trade off on cost, latency, and parse success?

The final comparison showed a clear trade-off. Zero-shot had the lowest latency at 1.756 seconds, followed closely by chain-of-thought at 1.760 seconds. Few-shot had the highest accuracy and a 1.886-second median latency. Structured had the highest latency at 2.020 seconds, although it matched few-shot's judge score. Few-shot was the only strategy with a rounded total cost of $0.001; the other three rounded to $0.000. Every strategy had a 1.0 parse rate, so formatting reliability did not distinguish them in this run.

## 4. What would I change for a production or follow-up version?

If I were improving this project, I would use the few-shot prompt as the initial default for accuracy, while keeping the structured prompt as a strong alternative when maintainability and explicit instructions matter most. I would add a validation step after every model response: check that the JSON has the required keys and that `years_experience_required` is an integer or `null`. I would also run the comparison over a larger dataset and repeat it across multiple runs, because this evaluation used only 10 snippets and the cost values were rounded. The results show that examples improved accuracy here, but the difference should be tested for statistical stability before making a production decision.
