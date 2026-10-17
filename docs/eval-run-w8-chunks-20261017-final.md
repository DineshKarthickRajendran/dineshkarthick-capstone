# eval-run-w8-chunks-20261017-final (20 golden questions)

- run_id: `1792200592`
- avg accuracy:     **2.3** / 4
- avg groundedness: **2.45** / 4
- avg format:       **3** / 4
- retrieval hit@3:  **20/20 (100.0%)**
- complete-source hit@3: **17/20 (85.0%)**
- expected-source coverage@3: **91.2%**

## Cost and latency

Candidate latency is end-to-end API request time; judge latency is the local time around the judge call.

- Candidate cost total / average: $0.00099470 / $0.00004973 (20/20 measured)
- Candidate latency median (p50): 2652.1 ms
- Judge cost total / average: $0.03976250 / $0.00198812 (20/20 measured)
- Judge latency median (p50): 2056.7 ms

| id | any hit | all sources | coverage | acc | grnd | fmt | retrieved sources | candidate cost | candidate ms | judge cost | judge ms | candidate |
|----|:-------:|:-----------:|:--------:|-----|------|-----|-------------------|---------------:|-------------:|-----------:|---------:|-----------|
| g001 | yes | yes | 100% | 1 | 1 | 3 | 01_leave_policy, 01_leave_policy, 01_leave_policy | $0.00004873 | 2929.7 ms | $0.00190750 | 2398.6 ms | The context does not specify the exact number of annual leave days tha |
| g002 | yes | yes | 100% | 4 | 4 | 3 | 02_expense_policy, 02_expense_policy, 02_expense_policy | $0.00003952 | 2358.1 ms | $0.00182750 | 2276.8 ms | An itemized receipt is required for expenses of $25 or more [02_expens |
| g003 | yes | yes | 100% | 1 | 2 | 3 | 03_wfh_policy, 03_wfh_policy, 03_wfh_policy | $0.00005527 | 2596.3 ms | $0.00196750 | 2522.5 ms | The context does not specify the number of days per week that you can  |
| g004 | yes | yes | 100% | 4 | 4 | 3 | 04_byod_policy, 04_byod_policy, 04_byod_policy | $0.00004365 | 2775.9 ms | $0.00194000 | 2220.3 ms | You should contact IT immediately if your personal device with company |
| g005 | yes | yes | 100% | 1 | 2 | 3 | 05_dress_code, 05_dress_code, 05_dress_code | $0.00005266 | 2836.3 ms | $0.00215500 | 2170.4 ms | The context does not specify whether casual attire is allowed on Frida |
| g006 | yes | yes | 100% | 1 | 1 | 2 | 06_attendance_policy, 06_attendance_policy, 03_wfh_policy | $0.00003980 | 3006.2 ms | $0.00186750 | 1837.7 ms | The context does not provide specific standard working hours for Monda |
| g007 | yes | yes | 100% | 4 | 4 | 3 | 07_code_of_conduct, 15_harassment_policy, 14_grievance_policy | $0.00005270 | 2467.5 ms | $0.00203000 | 2140.7 ms | Yes, you can report a workplace conduct concern to HR. [07_code_of_con |
| g008 | yes | yes | 100% | 2 | 2 | 3 | 08_remote_security_policy, 08_remote_security_policy, 16_confidentiality_policy | $0.00004409 | 2376.6 ms | $0.00178250 | 1923.8 ms | Suspected phishing should be reported to the relevant security or priv |
| g009 | yes | yes | 100% | 4 | 4 | 4 | 09_recruitment_policy, 09_recruitment_policy, 09_recruitment_policy | $0.00004526 | 2447.8 ms | $0.00199500 | 2059.6 ms | Before recruitment for a new position begins, an approved headcount re |
| g010 | yes | yes | 100% | 1 | 1 | 2 | 10_onboarding_policy, 10_onboarding_policy, 04_byod_policy | $0.00004522 | 2765.0 ms | $0.00185500 | 1844.2 ms | The context does not specify the exact timing for the initial check-in |
| g011 | yes | yes | 100% | 3 | 3 | 3 | 11_performance_management, 11_performance_management, 11_performance_management | $0.00004702 | 3109.2 ms | $0.00185000 | 1801.9 ms | No, performance feedback should not be given only during the annual re |
| g012 | yes | yes | 100% | 2 | 2 | 3 | 12_promotion_policy, 12_promotion_policy, 11_performance_management | $0.00003783 | 2564.8 ms | $0.00161000 | 1922.2 ms | Yes, sustained performance is considered when deciding on promotion [1 |
| g013 | yes | yes | 100% | 2 | 2 | 3 | 13_training_development_policy, 13_training_development_policy, 13_training_development_policy | $0.00004269 | 2481.2 ms | $0.00176250 | 1940.5 ms | Yes, you need manager approval before committing company funds to trai |
| g014 | yes | yes | 100% | 2 | 2 | 3 | 14_grievance_policy, 14_grievance_policy, 14_grievance_policy | $0.00005590 | 2668.3 ms | $0.00197000 | 2053.8 ms | Yes, you can submit a formal grievance without first discussing it inf |
| g015 | yes | yes | 100% | 2 | 2 | 3 | 02_expense_policy, 18_travel_policy, 02_expense_policy | $0.00007810 | 2897.4 ms | $0.00235250 | 2165.3 ms | Before booking a hotel for a business trip, employees should use compa |
| g016 | yes | no | 50% | 2 | 3 | 3 | 04_byod_policy, 08_remote_security_policy, 05_dress_code | $0.00005153 | 2751.3 ms | $0.00224750 | 2034.3 ms | No, you cannot store company files in your personal cloud drive. Corpo |
| g017 | yes | yes | 100% | 4 | 4 | 4 | 03_wfh_policy, 06_attendance_policy, 06_attendance_policy | $0.00005335 | 2636.0 ms | $0.00202250 | 1839.8 ms | Yes, if you work from home, you must follow your agreed schedule and r |
| g018 | yes | yes | 100% | 2 | 2 | 3 | 01_leave_policy, 01_leave_policy, 20_offboarding_policy | $0.00004649 | 2545.7 ms | $0.00218500 | 2154.1 ms | The provided context does not contain information about an exact formu |
| g019 | yes | no | 50% | 2 | 2 | 3 | 01_leave_policy, 01_leave_policy, 01_leave_policy | $0.00004610 | 2318.9 ms | $0.00202750 | 1889.2 ms | The provided context does not contain information about the cash amoun |
| g020 | yes | no | 25% | 2 | 2 | 3 | 03_wfh_policy, 03_wfh_policy, 03_wfh_policy | $0.00006879 | 2834.4 ms | $0.00240750 | 2119.5 ms | No, you cannot work from another country without prior approval from H |
