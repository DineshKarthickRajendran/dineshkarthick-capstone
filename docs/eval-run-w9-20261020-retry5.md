# eval-run-w9-20261020-retry5 (20 golden questions)

> **Not a valid W9 RAG evaluation.** This run used `run_eval.py`'s default
> `/ask_batched` endpoint, which calls the generic pipeline rather than the W9
> retrieval-and-generation path. Its 0/20 source metrics mean that endpoint
> returned no source metadata; the low answer scores are also from the
> non-W9 candidate pipeline. Rerun with `--endpoint /ask_w9` after restarting
> the API with the W9 endpoint available.

- run_id: `1792468257`
- avg accuracy:     **1.65** / 4
- avg groundedness: **1.65** / 4
- avg format:       **3.05** / 4
- retrieval hit@3:  **0/20 (0.0%)**
- complete-source hit@3: **0/20 (0.0%)**
- expected-source coverage@3: **0.0%**

## Cost and latency

Candidate latency is end-to-end API request time; judge latency is the local time around the judge call.

- Candidate cost total / average: $0.00132525 / $0.00006626 (20/20 measured)
- Candidate latency median (p50): 2025.9 ms
- Judge cost total / average: $0.04336500 / $0.00216825 (20/20 measured)
- Judge latency median (p50): 2528.9 ms

| id | any hit | all sources | coverage | acc | grnd | fmt | retrieved sources | candidate cost | candidate ms | judge cost | judge ms | candidate |
|----|:-------:|:-----------:|:--------:|-----|------|-----|-------------------|---------------:|-------------:|-----------:|---------:|-----------|
| g001 | no | no | 0% | 1 | 1 | 3 |  | $0.00006120 | 2317.1 ms | $0.00190500 | 2946.1 ms | Full-time employees typically accrue between 10 to 20 annual leave day |
| g002 | no | no | 0% | 1 | 1 | 3 |  | $0.00007530 | 2147.1 ms | $0.00228250 | 2787.4 ms | In the U.S., an itemized receipt is typically required for expenses of |
| g003 | no | no | 0% | 1 | 1 | 3 |  | $0.00006630 | 2132.7 ms | $0.00222000 | 2251.4 ms | The number of days per week you can work from home typically depends o |
| g004 | no | no | 0% | 2 | 2 | 3 |  | $0.00006570 | 1967.1 ms | $0.00217000 | 2559.1 ms | If your personal device with company access is lost, you should immedi |
| g005 | no | no | 0% | 2 | 2 | 3 |  | $0.00006165 | 2045.4 ms | $0.00224750 | 3072.7 ms | Yes, casual attire is generally allowed on Fridays in many workplaces, |
| g006 | no | no | 0% | 1 | 1 | 3 |  | $0.00006495 | 1951.5 ms | $0.00211750 | 2654.7 ms | Standard working hours for many office jobs typically range from 9:00  |
| g007 | no | no | 0% | 2 | 2 | 3 |  | $0.00006315 | 2032.6 ms | $0.00211250 | 2372.9 ms | Yes, you can report a workplace conduct concern to Human Resources (HR |
| g008 | no | no | 0% | 1 | 1 | 3 |  | $0.00006570 | 2048.6 ms | $0.00215750 | 2457.6 ms | Suspected phishing should be reported to your email provider, as they  |
| g009 | no | no | 0% | 1 | 1 | 3 |  | $0.00005820 | 1944.7 ms | $0.00215250 | 2457.6 ms | Before recruitment for a new position begins, two essential things are |
| g010 | no | no | 0% | 1 | 1 | 3 |  | $0.00006615 | 1877.2 ms | $0.00225500 | 2347.7 ms | The first onboarding check-in should typically take place within the f |
| g011 | no | no | 0% | 2 | 2 | 3 |  | $0.00005670 | 1815.1 ms | $0.00200000 | 2625.4 ms | No, performance feedback should not be limited to annual reviews; it i |
| g012 | no | no | 0% | 2 | 2 | 3 |  | $0.00006180 | 1942.6 ms | $0.00216000 | 2498.6 ms | Yes, sustained performance is a critical factor in promotion decisions |
| g013 | no | no | 0% | 2 | 2 | 3 |  | $0.00005085 | 1794.7 ms | $0.00195500 | 2198.3 ms | Yes, typically you need manager approval before committing company fun |
| g014 | no | no | 0% | 2 | 2 | 3 |  | $0.00006735 | 1948.0 ms | $0.00217250 | 2659.4 ms | Yes, you can submit a formal grievance without first discussing it inf |
| g015 | no | no | 0% | 1 | 1 | 3 |  | $0.00007185 | 2019.3 ms | $0.00202250 | 2399.1 ms | Before booking a hotel for a business trip, typically, you need approv |
| g016 | no | no | 0% | 2 | 2 | 3 |  | $0.00006990 | 2162.6 ms | $0.00232000 | 4080.3 ms | Using your personal laptop for remote work and storing company files i |
| g017 | no | no | 0% | 4 | 4 | 4 |  | $0.00006105 | 1942.0 ms | $0.00199500 | 2348.2 ms | Yes, if you work from home, you are generally still expected to follow |
| g018 | no | no | 0% | 2 | 2 | 3 |  | $0.00007875 | 2174.0 ms | $0.00240750 | 2392.6 ms | Typically, policies regarding unused annual leave payout upon employee |
| g019 | no | no | 0% | 1 | 1 | 3 |  | $0.00007440 | 2190.8 ms | $0.00211750 | 2668.5 ms | To determine the exact cash amount you will receive for your unused an |
| g020 | no | no | 0% | 2 | 2 | 3 |  | $0.00008430 | 2350.9 ms | $0.00259500 | 2665.9 ms | Whether you can work from another country on your personal laptop and  |
