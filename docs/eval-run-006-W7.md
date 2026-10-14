# eval-run-006-W7 (20 golden questions)

- run_id: `1791958030`
- avg accuracy:     **3.1** / 4
- avg groundedness: **3.1** / 4
- avg format:       **3.3** / 4

## Comparison with eval-run-005

Both runs evaluate the same 20 golden questions. Eval-run-005 is the previous
top-k=3 chunked RAG run; this W7 run uses embedding-based retrieval backed by
Qdrant.

| Metric | eval-run-005 reported | eval-run-006-W7 | Change |
|---|---:|---:|---:|
| Accuracy | 2.85 / 4 | 3.10 / 4 | +0.25 |
| Groundedness | 2.85 / 4 | 3.10 / 4 | +0.25 reported* |
| Format | 3.20 / 4 | 3.30 / 4 | +0.10 reported** |

The W7 run therefore shows higher reported scores across all three dimensions.
Accuracy increased by 0.25 points (6.25 percentage points of the four-point
scale). The largest item-level accuracy and groundedness gains are g007 and
g012, each increasing from 2 to 4; g020 increased from 1 to 2. This is
promising evidence for the W7 retrieval setup, but it does not isolate Qdrant
as the cause: the reports do not establish that all run conditions other than
the vector-store/retrieval change were held constant.

**Remaining gaps:** g006 and g008 still score 1 for accuracy and groundedness.
Several other cases (including g013, g014, g016, g018, and g019) remain at 2,
so the improvement does not resolve all retrieval or answer-quality failures.

\* The per-question groundedness scores in eval-run-005 sum to 58/20 = 2.90,
not the reported 2.85. Using the table-derived baseline, the groundedness gain
is +0.20 rather than +0.25.

\*\* The per-question format scores in eval-run-005 average 3.25; its reported
3.2 is rounded to one decimal. Against that table-derived value, the gain is
+0.05. The W7 per-question format scores average 3.30.

| id | acc | grnd | fmt | candidate |
|----|-----|------|-----|-----------|
| g001 | 4 | 4 | 4 | Full-time employees accrue 18 days of annual leave per calendar year [ |
| g002 | 4 | 4 | 3 | An itemized receipt is required for expenses of $25 or more [02_expens |
| g003 | 4 | 4 | 4 | You may work remotely up to 3 days per week, subject to manager approv |
| g004 | 4 | 4 | 4 | You must report the lost or stolen device to IT immediately [04_byod_p |
| g005 | 4 | 4 | 3 | Yes, casual attire is generally permitted on Fridays when no formal ex |
| g006 | 1 | 1 | 2 | The provided context does not contain information about the standard w |
| g007 | 4 | 4 | 4 | Yes, you can report a workplace conduct concern to HR. Employees may r |
| g008 | 1 | 1 | 2 | Suspected phishing should be reported rather than investigated indepen |
| g009 | 4 | 4 | 4 | Before recruitment for a new position begins, an approved headcount re |
| g010 | 4 | 4 | 4 | The first onboarding check-in should take place within the first 30 da |
| g011 | 4 | 4 | 3 | No, performance feedback should not be given only during the annual re |
| g012 | 4 | 4 | 3 | Yes, sustained performance is considered when deciding on promotion [1 |
| g013 | 2 | 2 | 3 | Yes, employees should obtain manager approval before committing compan |
| g014 | 2 | 2 | 3 | Yes, you can submit a formal grievance without first discussing it inf |
| g015 | 4 | 4 | 4 | Before booking a hotel for a business trip, the travel must be approve |
| g016 | 2 | 2 | 3 | No, you should not store company files in your personal cloud drive. R |
| g017 | 4 | 4 | 4 | Yes, if you work from home, you must work your agreed schedule and rem |
| g018 | 2 | 2 | 3 | The policy does not provide an exact formula for paying unused annual  |
| g019 | 2 | 2 | 3 | The provided context does not contain information about the cash amoun |
| g020 | 2 | 2 | 3 | No, you cannot work from another country on your personal laptop and s |
