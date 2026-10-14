# eval-run-009-large-embedding-20261014 (20 golden questions)

- run_id: `1791964143`
- avg accuracy:     **3.15** / 4
- avg groundedness: **3.1** / 4
- avg format:       **3.4** / 4
- retrieval hit@3:  **19/20 (95.0%)**

## Cost and latency

Candidate latency is end-to-end API request time; judge latency is the local time around the judge call.

- Candidate cost total / average: $0.00155695 / $0.00007785 (20/20 measured)
- Candidate latency median (p50): 2986.8 ms
- Judge cost total / average: $0.03905500 / $0.00195275 (20/20 measured)
- Judge latency median (p50): 2172.4 ms

| id | hit@3 | acc | grnd | fmt | retrieved sources | candidate cost | candidate ms | judge cost | judge ms | candidate |
|----|:-----:|-----|------|-----|-------------------|---------------:|-------------:|-----------:|---------:|-----------|
| g001 | yes | 4 | 4 | 4 | 01_leave_policy, 01_leave_policy, 01_leave_policy | $0.00007652 | 4621.6 ms | $0.00172750 | 2939.8 ms | Full-time employees accrue 18 days of annual leave per calendar year [ |
| g002 | yes | 4 | 4 | 3 | 02_expense_policy, 02_expense_policy, 02_expense_policy | $0.00007193 | 2818.5 ms | $0.00186750 | 2092.1 ms | An itemized receipt is required for expenses of $25 or more [02_expens |
| g003 | yes | 4 | 4 | 4 | 03_wfh_policy, 03_wfh_policy, 03_wfh_policy | $0.00007523 | 2821.1 ms | $0.00199000 | 2344.8 ms | You may work remotely up to 3 days per week, subject to manager approv |
| g004 | yes | 4 | 4 | 4 | 04_byod_policy, 08_remote_security_policy, 17_it_acceptable_use_policy | $0.00007155 | 3073.5 ms | $0.00208500 | 2229.4 ms | You must report a lost or stolen device that can access company system |
| g005 | yes | 4 | 4 | 3 | 05_dress_code, 05_dress_code, 05_dress_code | $0.00006929 | 3631.6 ms | $0.00204500 | 2330.4 ms | Yes, casual attire is generally permitted on Fridays when no formal ex |
| g006 | yes | 2 | 2 | 3 | 03_wfh_policy, 06_attendance_policy, 06_attendance_policy | $0.00008515 | 2770.8 ms | $0.00204750 | 2176.2 ms | The standard working hours are 9:00 a.m. to 6:00 p.m., Monday through  |
| g007 | no | 4 | 4 | 3 | 15_harassment_policy, 15_harassment_policy, 14_grievance_policy | $0.00007045 | 2793.3 ms | $0.00191500 | 2289.1 ms | Yes, you may report concerns to HR as one of the designated reporting  |
| g008 | yes | 2 | 2 | 3 | 08_remote_security_policy, 08_remote_security_policy, 15_harassment_policy | $0.00006856 | 2773.7 ms | $0.00166250 | 2044.2 ms | Suspected phishing should be reported to IT Security promptly rather t |
| g009 | yes | 4 | 4 | 4 | 09_recruitment_policy, 09_recruitment_policy, 09_recruitment_policy | $0.00007489 | 2967.2 ms | $0.00189500 | 1887.4 ms | Before recruitment for a new position begins, an approved headcount re |
| g010 | yes | 4 | 4 | 4 | 10_onboarding_policy, 10_onboarding_policy, 10_onboarding_policy | $0.00007583 | 2973.6 ms | $0.00178500 | 2168.5 ms | The first onboarding check-in should take place within the first 30 da |
| g011 | yes | 4 | 4 | 4 | 11_performance_management, 11_performance_management, 11_performance_management | $0.00008393 | 3215.1 ms | $0.00186250 | 2042.6 ms | No, performance feedback should not be given only during the annual re |
| g012 | yes | 1 | 1 | 3 | 12_promotion_policy, 12_promotion_policy, 12_promotion_policy | $0.00006312 | 2877.9 ms | $0.00169500 | 2242.3 ms | The provided context does not mention sustained performance as a facto |
| g013 | yes | 2 | 2 | 3 | 13_training_development_policy, 13_training_development_policy, 13_training_development_policy | $0.00007041 | 2948.5 ms | $0.00172500 | 2127.3 ms | Yes, employees should obtain manager approval before committing compan |
| g014 | yes | 4 | 3 | 3 | 14_grievance_policy, 14_grievance_policy, 15_harassment_policy | $0.00008090 | 5199.4 ms | $0.00171500 | 2117.3 ms | Yes, you can submit a formal grievance without first discussing it inf |
| g015 | yes | 2 | 2 | 3 | 02_expense_policy, 18_travel_policy, 18_travel_policy | $0.00008720 | 3344.1 ms | $0.00212000 | 2183.4 ms | Before booking a hotel for a business trip, documented pre-approval is |
| g016 | yes | 2 | 2 | 3 | 08_remote_security_policy, 03_wfh_policy, 17_it_acceptable_use_policy | $0.00009547 | 4097.8 ms | $0.00240750 | 2496.3 ms | No, you cannot use your personal laptop for remote work and store comp |
| g017 | yes | 4 | 4 | 4 | 03_wfh_policy, 03_wfh_policy, 03_wfh_policy | $0.00008015 | 3000.0 ms | $0.00203250 | 2317.2 ms | Yes, if you work from home, you must work your agreed schedule and rem |
| g018 | yes | 2 | 2 | 3 | 01_leave_policy, 01_leave_policy, 01_leave_policy | $0.00008341 | 2944.9 ms | $0.00216750 | 2013.8 ms | The provided context does not mention an exact formula for paying unus |
| g019 | yes | 2 | 2 | 3 | 01_leave_policy, 01_leave_policy, 01_leave_policy | $0.00007525 | 3002.6 ms | $0.00204000 | 2156.7 ms | The provided context does not contain information about the cash amoun |
| g020 | yes | 4 | 4 | 4 | 03_wfh_policy, 03_wfh_policy, 03_wfh_policy | $0.00009771 | 3162.4 ms | $0.00227000 | 2030.2 ms | No, you cannot work from another country without prior approval from H |
