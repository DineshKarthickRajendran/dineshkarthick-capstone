# eval-run-w9-final-20261020 (20 golden questions)

- run_id: `1792469926`
- avg accuracy:     **2.5** / 4
- avg groundedness: **2.55** / 4
- avg format:       **3** / 4
- retrieval hit@3:  **20/20 (100.0%)**
- complete-source hit@3: **18/20 (90.0%)**
- expected-source coverage@3: **95.0%**

## Cost and latency

Candidate latency is end-to-end API request time; judge latency is the local time around the judge call.

- Candidate cost total / average: $0.00103355 / $0.00005168 (20/20 measured)
- Candidate latency median (p50): 2797.2 ms
- Judge cost total / average: $0.03944000 / $0.00197200 (20/20 measured)
- Judge latency median (p50): 2265.4 ms

| id | any hit | all sources | coverage | acc | grnd | fmt | retrieved sources | candidate cost | candidate ms | judge cost | judge ms | candidate |
|----|:-------:|:-----------:|:--------:|-----|------|-----|-------------------|---------------:|-------------:|-----------:|---------:|-----------|
| g001 | yes | yes | 100% | 1 | 1 | 3 | 01_leave_policy, 01_leave_policy, 01_leave_policy | $0.00004873 | 16343.5 ms | $0.00190750 | 2640.0 ms | The context does not specify the exact number of annual leave days tha |
| g002 | yes | yes | 100% | 4 | 4 | 3 | 02_expense_policy, 18_travel_policy, 02_expense_policy | $0.00004237 | 3198.0 ms | $0.00184750 | 2462.8 ms | An itemized receipt is required for expenses of $25 or more [02_expens |
| g003 | yes | yes | 100% | 1 | 1 | 2 | 10_onboarding_policy, 03_wfh_policy, 03_wfh_policy | $0.00003577 | 2571.1 ms | $0.00176250 | 2342.2 ms | The provided context does not specify how many days per week you can w |
| g004 | yes | yes | 100% | 4 | 4 | 3 | 04_byod_policy, 17_it_acceptable_use_policy, 04_byod_policy | $0.00004770 | 2675.2 ms | $0.00192000 | 2196.9 ms | You should contact IT immediately if your personal device with company |
| g005 | yes | yes | 100% | 1 | 2 | 3 | 05_dress_code, 05_dress_code, 05_dress_code | $0.00005326 | 2932.1 ms | $0.00205750 | 2139.1 ms | The context does not specify whether casual attire is allowed on Frida |
| g006 | yes | yes | 100% | 1 | 1 | 2 | 06_attendance_policy, 06_attendance_policy, 05_dress_code | $0.00003290 | 2778.4 ms | $0.00174750 | 1946.3 ms | The context does not provide specific standard working hours for Monda |
| g007 | yes | yes | 100% | 4 | 3 | 3 | 15_harassment_policy, 15_harassment_policy, 07_code_of_conduct | $0.00004460 | 2616.8 ms | $0.00175750 | 2030.0 ms | Yes, you can report a workplace conduct concern to HR. [15_harassment_ |
| g008 | yes | yes | 100% | 1 | 2 | 2 | 08_remote_security_policy, 08_remote_security_policy, 14_grievance_policy | $0.00005084 | 2806.3 ms | $0.00211750 | 2509.6 ms | Suspected phishing should be reported rather than investigated indepen |
| g009 | yes | yes | 100% | 4 | 4 | 4 | 09_recruitment_policy, 10_onboarding_policy, 09_recruitment_policy | $0.00004811 | 2505.0 ms | $0.00198500 | 2096.1 ms | Before recruitment for a new position begins, an approved headcount re |
| g010 | yes | yes | 100% | 1 | 1 | 2 | 10_onboarding_policy, 10_onboarding_policy, 10_onboarding_policy | $0.00004912 | 2750.4 ms | $0.00197000 | 1986.4 ms | The context does not specify the exact timing for when the first onboa |
| g011 | yes | yes | 100% | 4 | 4 | 3 | 11_performance_management, 11_performance_management, 11_performance_management | $0.00005002 | 2772.9 ms | $0.00190250 | 2005.1 ms | No, performance feedback should not be given only during the annual re |
| g012 | yes | yes | 100% | 2 | 2 | 3 | 12_promotion_policy, 11_performance_management, 12_promotion_policy | $0.00004188 | 2729.0 ms | $0.00170000 | 2389.1 ms | Yes, sustained performance is considered when deciding on promotion [1 |
| g013 | yes | yes | 100% | 2 | 2 | 3 | 13_training_development_policy, 13_training_development_policy, 13_training_development_policy | $0.00004344 | 2788.2 ms | $0.00174250 | 2467.9 ms | Yes, you need manager approval before committing company funds to trai |
| g014 | yes | yes | 100% | 2 | 2 | 3 | 14_grievance_policy, 14_grievance_policy, 14_grievance_policy | $0.00005575 | 2901.8 ms | $0.00192000 | 2245.9 ms | Yes, you can submit a formal grievance without first discussing it inf |
| g015 | yes | yes | 100% | 4 | 4 | 4 | 18_travel_policy, 02_expense_policy, 02_expense_policy | $0.00006370 | 3279.9 ms | $0.00206750 | 2416.2 ms | Before booking a hotel for a business trip, the employee must obtain a |
| g016 | yes | yes | 100% | 2 | 2 | 3 | 03_wfh_policy, 04_byod_policy, 17_it_acceptable_use_policy | $0.00007043 | 3524.7 ms | $0.00221250 | 2255.9 ms | No, you cannot use your personal laptop for remote work and store comp |
| g017 | yes | yes | 100% | 4 | 4 | 4 | 03_wfh_policy, 06_attendance_policy, 03_wfh_policy | $0.00005020 | 2836.1 ms | $0.00200250 | 2357.9 ms | Yes, if you work from home, you must work your agreed schedule and rem |
| g018 | yes | yes | 100% | 4 | 4 | 4 | 20_offboarding_policy, 01_leave_policy, 20_offboarding_policy | $0.00006449 | 2844.3 ms | $0.00209750 | 1969.4 ms | The provided context does not contain an exact formula for paying unus |
| g019 | yes | no | 50% | 2 | 2 | 3 | 06_attendance_policy, 01_leave_policy, 01_leave_policy | $0.00005315 | 2641.9 ms | $0.00202750 | 2274.9 ms | The provided context does not contain information about the cash amoun |
| g020 | yes | no | 50% | 2 | 2 | 3 | 03_wfh_policy, 17_it_acceptable_use_policy, 04_byod_policy | $0.00008709 | 2918.6 ms | $0.00269500 | 2728.2 ms | No, you cannot work from another country without prior approval from H |
