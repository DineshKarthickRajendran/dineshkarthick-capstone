# eval-run-008-small-embedding-20261014 (20 golden questions)

- run_id: `1791963994`
- avg accuracy:     **2.9** / 4
- avg groundedness: **2.9** / 4
- avg format:       **3.2** / 4
- retrieval hit@3:  **20/20 (100.0%)**

## Cost and latency

Candidate latency is end-to-end API request time; judge latency is the local time around the judge call.

- Candidate cost total / average: $0.00153500 / $0.00007675 (20/20 measured)
- Candidate latency median (p50): 2777.5 ms
- Judge cost total / average: $0.03948000 / $0.00197400 (20/20 measured)
- Judge latency median (p50): 2217.3 ms

| id | hit@3 | acc | grnd | fmt | retrieved sources | candidate cost | candidate ms | judge cost | judge ms | candidate |
|----|:-----:|-----|------|-----|-------------------|---------------:|-------------:|-----------:|---------:|-----------|
| g001 | yes | 4 | 4 | 4 | 01_leave_policy, 01_leave_policy, 01_leave_policy | $0.00007498 | 3153.1 ms | $0.00172750 | 2737.1 ms | Full-time employees accrue 18 days of annual leave per calendar year [ |
| g002 | yes | 4 | 4 | 3 | 02_expense_policy, 02_expense_policy, 02_expense_policy | $0.00007072 | 2516.8 ms | $0.00182750 | 2211.8 ms | An itemized receipt is required for expenses of $25 or more [02_expens |
| g003 | yes | 4 | 4 | 4 | 03_wfh_policy, 03_wfh_policy, 03_wfh_policy | $0.00007417 | 2474.6 ms | $0.00200000 | 2002.7 ms | You may work remotely up to 3 days per week, subject to manager approv |
| g004 | yes | 4 | 4 | 4 | 04_byod_policy, 04_byod_policy, 04_byod_policy | $0.00007080 | 2366.9 ms | $0.00200500 | 2222.8 ms | You must report a lost or stolen device that can access company system |
| g005 | yes | 4 | 4 | 3 | 05_dress_code, 05_dress_code, 05_dress_code | $0.00007171 | 2859.6 ms | $0.00208500 | 2451.8 ms | Yes, casual attire is generally permitted on Fridays when no formal ex |
| g006 | yes | 1 | 1 | 2 | 03_wfh_policy, 03_wfh_policy, 06_attendance_policy | $0.00006680 | 2465.7 ms | $0.00171250 | 1952.8 ms | The provided context does not contain information about the standard w |
| g007 | yes | 2 | 2 | 3 | 07_code_of_conduct, 15_harassment_policy, 15_harassment_policy | $0.00007895 | 2727.0 ms | $0.00195500 | 2273.4 ms | Yes, you can report a workplace conduct concern to HR, as employees ma |
| g008 | yes | 1 | 1 | 2 | 08_remote_security_policy, 15_harassment_policy, 08_remote_security_policy | $0.00006629 | 2563.8 ms | $0.00194250 | 2452.9 ms | Suspected phishing should be reported rather than investigated indepen |
| g009 | yes | 4 | 4 | 4 | 09_recruitment_policy, 12_promotion_policy, 09_recruitment_policy | $0.00007331 | 3737.1 ms | $0.00189500 | 2098.3 ms | Before recruitment for a new position begins, an approved headcount re |
| g010 | yes | 4 | 4 | 3 | 10_onboarding_policy, 10_onboarding_policy, 10_onboarding_policy | $0.00007462 | 2871.7 ms | $0.00189500 | 2043.0 ms | The first onboarding check-in should take place within the first 30 da |
| g011 | yes | 4 | 4 | 3 | 11_performance_management, 11_performance_management, 11_performance_management | $0.00007777 | 2873.6 ms | $0.00184250 | 2340.0 ms | No, performance feedback should not be given only during the annual re |
| g012 | yes | 2 | 2 | 3 | 12_promotion_policy, 12_promotion_policy, 12_promotion_policy | $0.00007173 | 2588.4 ms | $0.00194250 | 2053.7 ms | Yes, sustained performance is considered when deciding on promotions a |
| g013 | yes | 2 | 2 | 3 | 13_training_development_policy, 13_training_development_policy, 13_training_development_policy | $0.00006909 | 2839.1 ms | $0.00184500 | 2052.0 ms | Yes, employees should obtain manager approval before committing compan |
| g014 | yes | 2 | 2 | 3 | 14_grievance_policy, 14_grievance_policy, 04_byod_policy | $0.00009100 | 3053.7 ms | $0.00206250 | 2007.0 ms | Yes, you can submit a formal grievance without first discussing it inf |
| g015 | yes | 4 | 4 | 4 | 02_expense_policy, 18_travel_policy, 18_travel_policy | $0.00008500 | 2828.1 ms | $0.00192750 | 1978.5 ms | Before booking a hotel for a business trip, the travel must be approve |
| g016 | yes | 2 | 2 | 3 | 04_byod_policy, 03_wfh_policy, 16_confidentiality_policy | $0.00007838 | 3017.8 ms | $0.00216000 | 2522.3 ms | No, you should not store company files in your personal cloud drive. R |
| g017 | yes | 4 | 4 | 4 | 03_wfh_policy, 03_wfh_policy, 06_attendance_policy | $0.00007495 | 2498.7 ms | $0.00200250 | 2346.4 ms | Yes, if you work from home, you must work your agreed schedule and rem |
| g018 | yes | 2 | 2 | 3 | 01_leave_policy, 01_leave_policy, 01_leave_policy | $0.00009059 | 2686.8 ms | $0.00212750 | 2272.3 ms | The policy does not provide an exact formula for paying unused annual  |
| g019 | yes | 2 | 2 | 3 | 01_leave_policy, 01_leave_policy, 01_leave_policy | $0.00007595 | 2558.0 ms | $0.00204000 | 2070.4 ms | The provided context does not contain information about the cash amoun |
| g020 | yes | 2 | 2 | 3 | 03_wfh_policy, 17_it_acceptable_use_policy, 03_wfh_policy | $0.00009819 | 3033.1 ms | $0.00248500 | 2352.9 ms | No, you cannot work from another country on your personal laptop and s |
