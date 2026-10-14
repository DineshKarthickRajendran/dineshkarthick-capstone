# eval-run-007-W7-cost (20 golden questions)

- run_id: `1791961853`
- avg accuracy:     **3** / 4
- avg groundedness: **3** / 4
- avg format:       **3.2** / 4
- retrieval hit@3:  **20/20 (100%)** (computed retrospectively from persisted source IDs)

Hit@3 counts a question as a hit when at least one expected policy source is
present among the three retrieved sources. Retrieved chunk IDs were normalized
to their parent document IDs before comparison.

## Cost and latency

Candidate latency is end-to-end API request time; judge latency is the local time around the judge call.

- Candidate cost total / average: $0.00152780 / $0.00007639 (20/20 measured)
- Candidate latency average / median (p50): 2637.6 ms / 2614.0 ms
- Judge cost total / average: $0.03907000 / $0.00195350 (20/20 measured)
- Judge latency average / median (p50): 2416.4 ms / 2256.5 ms

| id | acc | grnd | fmt | candidate cost | candidate ms | judge cost | judge ms | candidate |
|----|-----|------|-----|---------------:|-------------:|-----------:|---------:|-----------|
| g001 | 4 | 4 | 4 | $0.00007498 | 3233.1 ms | $0.00173750 | 2353.2 ms | Full-time employees accrue 18 days of annual leave per calendar year [ |
| g002 | 4 | 4 | 3 | $0.00007072 | 2485.7 ms | $0.00180750 | 2292.5 ms | An itemized receipt is required for expenses of $25 or more [02_expens |
| g003 | 4 | 4 | 4 | $0.00007417 | 2399.5 ms | $0.00199000 | 2128.0 ms | You may work remotely up to 3 days per week, subject to manager approv |
| g004 | 4 | 4 | 4 | $0.00006780 | 2326.9 ms | $0.00171250 | 2173.1 ms | You must report the lost or stolen device to IT immediately [04_byod_p |
| g005 | 4 | 4 | 3 | $0.00007171 | 2730.1 ms | $0.00201500 | 2231.5 ms | Yes, casual attire is generally permitted on Fridays when no formal ex |
| g006 | 1 | 1 | 2 | $0.00006680 | 2340.1 ms | $0.00180250 | 1991.7 ms | The provided context does not contain information about the standard w |
| g007 | 2 | 2 | 3 | $0.00008015 | 2892.1 ms | $0.00198000 | 2260.8 ms | Yes, you can report a workplace conduct concern to HR. Employees may r |
| g008 | 1 | 1 | 2 | $0.00006629 | 2356.5 ms | $0.00201250 | 2244.6 ms | Suspected phishing should be reported rather than investigated indepen |
| g009 | 4 | 4 | 4 | $0.00007331 | 2424.6 ms | $0.00189500 | 2189.1 ms | Before recruitment for a new position begins, an approved headcount re |
| g010 | 4 | 4 | 3 | $0.00007462 | 2608.8 ms | $0.00174500 | 2187.3 ms | The first onboarding check-in should take place within the first 30 da |
| g011 | 4 | 4 | 3 | $0.00007777 | 2711.2 ms | $0.00210250 | 3653.7 ms | No, performance feedback should not be given only during the annual re |
| g012 | 4 | 4 | 3 | $0.00006633 | 2486.5 ms | $0.00190000 | 2620.4 ms | Yes, sustained performance is considered when deciding on promotion [1 |
| g013 | 2 | 2 | 3 | $0.00006909 | 2575.2 ms | $0.00173500 | 2195.6 ms | Yes, employees should obtain manager approval before committing compan |
| g014 | 2 | 2 | 3 | $0.00009100 | 2619.3 ms | $0.00206250 | 3373.2 ms | Yes, you can submit a formal grievance without first discussing it inf |
| g015 | 4 | 4 | 4 | $0.00008500 | 2838.4 ms | $0.00200750 | 2217.6 ms | Before booking a hotel for a business trip, the travel must be approve |
| g016 | 2 | 2 | 3 | $0.00007838 | 2730.1 ms | $0.00213000 | 2252.3 ms | No, you should not store company files in your personal cloud drive. R |
| g017 | 4 | 4 | 4 | $0.00007495 | 2498.9 ms | $0.00194250 | 2309.3 ms | Yes, if you work from home, you must work your agreed schedule and rem |
| g018 | 2 | 2 | 3 | $0.00009059 | 2663.7 ms | $0.00207750 | 2354.6 ms | The policy does not provide an exact formula for paying unused annual  |
| g019 | 2 | 2 | 3 | $0.00007595 | 2751.3 ms | $0.00200000 | 2983.0 ms | The provided context does not contain information about the cash amoun |
| g020 | 2 | 2 | 3 | $0.00009819 | 3079.5 ms | $0.00241500 | 2315.7 ms | No, you cannot work from another country on your personal laptop and s |
