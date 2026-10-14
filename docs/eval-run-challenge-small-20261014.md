# eval-run-challenge-small-20261014 (20 golden questions)

- run_id: `1791973692`
- avg accuracy:     **2.15** / 4
- avg groundedness: **2.2** / 4
- avg format:       **3** / 4
- retrieval hit@3:  **19/20 (95.0%)**
- complete-source hit@3: **9/20 (45.0%)**
- expected-source coverage@3: **70.8%**

## Cost and latency

Candidate latency is end-to-end API request time; judge latency is the local time around the judge call.

- Candidate cost total / average: $0.00214724 / $0.00010736 (20/20 measured)
- Candidate latency median (p50): 3047.5 ms
- Judge cost total / average: $0.04790250 / $0.00239513 (20/20 measured)
- Judge latency median (p50): 2501.3 ms

| id | any hit | all sources | coverage | acc | grnd | fmt | retrieved sources | candidate cost | candidate ms | judge cost | judge ms | candidate |
|----|:-------:|:-----------:|:--------:|-----|------|-----|-------------------|---------------:|-------------:|-----------:|---------:|-----------|
| c001 | yes | no | 50% | 3 | 3 | 4 | 02_expense_policy, 02_expense_policy, 02_expense_policy | $0.00012940 | 5097.4 ms | $0.00239500 | 2751.6 ms | The standard limit for hotel nights is $150, so your $170 hotel night  |
| c002 | yes | no | 33% | 1 | 1 | 2 | 03_wfh_policy, 03_wfh_policy, 03_wfh_policy | $0.00008190 | 2704.0 ms | $0.00200000 | 2344.6 ms | The context does not provide specific information about using personal |
| c003 | yes | yes | 100% | 2 | 2 | 3 | 17_it_acceptable_use_policy, 04_byod_policy, 08_remote_security_policy | $0.00009084 | 3238.2 ms | $0.00212000 | 2148.1 ms | You must report the lost or stolen device that can access company syst |
| c004 | yes | yes | 100% | 2 | 2 | 3 | 03_wfh_policy, 03_wfh_policy, 06_attendance_policy | $0.00011858 | 3482.7 ms | $0.00254500 | 2247.7 ms | The policies state that employees may work remotely up to 3 days per w |
| c005 | yes | no | 67% | 2 | 2 | 3 | 14_grievance_policy, 15_harassment_policy, 15_harassment_policy | $0.00009895 | 3077.2 ms | $0.00227500 | 2290.8 ms | You do not need to confront the manager informally first before filing |
| c006 | no | no | 0% | 1 | 1 | 2 | 12_promotion_policy, 12_promotion_policy, 14_grievance_policy | $0.00008364 | 2937.8 ms | $0.00231250 | 2619.5 ms | The context does not provide information regarding whether a manager c |
| c007 | yes | no | 50% | 3 | 3 | 3 | 13_training_development_policy, 13_training_development_policy, 13_training_development_policy | $0.00009184 | 2626.1 ms | $0.00208250 | 2530.1 ms | The mandatory privacy training is not optional and must be completed w |
| c008 | yes | no | 50% | 3 | 3 | 4 | 12_promotion_policy, 12_promotion_policy, 12_promotion_policy | $0.00009804 | 3465.5 ms | $0.00231000 | 2454.4 ms | Strong performance alone is not enough for a promotion. A manager must |
| c009 | yes | yes | 100% | 3 | 3 | 3 | 16_confidentiality_policy, 20_offboarding_policy, 01_leave_policy | $0.00009470 | 3027.6 ms | $0.00240250 | 2517.6 ms | No, employees must not retain confidential copies of project files whe |
| c010 | yes | yes | 100% | 2 | 2 | 3 | 18_travel_policy, 03_wfh_policy, 18_travel_policy | $0.00009474 | 2849.8 ms | $0.00238750 | 2583.2 ms | Employees may extend a business trip for personal reasons only when th |
| c011 | yes | no | 50% | 2 | 2 | 3 | 19_employee_data_privacy, 19_employee_data_privacy, 09_recruitment_policy | $0.00009823 | 3067.5 ms | $0.00238750 | 2485.0 ms | Access to employee records should be governed by the principle that re |
| c012 | yes | yes | 100% | 2 | 2 | 3 | 02_expense_policy, 18_travel_policy, 02_expense_policy | $0.00017256 | 4036.5 ms | $0.00268750 | 2360.5 ms | The relevant limits and process rules are as follows:

1. **Receipt Re |
| c013 | yes | no | 50% | 2 | 2 | 3 | 08_remote_security_policy, 08_remote_security_policy, 08_remote_security_policy | $0.00011825 | 2960.4 ms | $0.00269750 | 2655.1 ms | To address physical viewing of your screen, you should position your s |
| c014 | yes | no | 67% | 3 | 3 | 3 | 04_byod_policy, 17_it_acceptable_use_policy, 04_byod_policy | $0.00009563 | 2740.4 ms | $0.00238500 | 2115.6 ms | No, IT support does not permit installing unapproved apps or moving co |
| c015 | yes | yes | 100% | 3 | 3 | 3 | 15_harassment_policy, 07_code_of_conduct, 14_grievance_policy | $0.00012865 | 3277.1 ms | $0.00247250 | 2823.7 ms | HR cannot promise total secrecy because complete confidentiality canno |
| c016 | yes | no | 50% | 2 | 2 | 3 | 03_wfh_policy, 03_wfh_policy, 03_wfh_policy | $0.00009346 | 2909.0 ms | $0.00249000 | 2550.2 ms | The remote-work policy does not allow you to assume that home internet |
| c017 | yes | yes | 100% | 2 | 3 | 3 | 08_remote_security_policy, 04_byod_policy, 08_remote_security_policy | $0.00008471 | 2710.2 ms | $0.00224500 | 2523.9 ms | If an employee has a personal-device security incident while working f |
| c018 | yes | no | 50% | 1 | 1 | 3 | 08_remote_security_policy, 08_remote_security_policy, 03_wfh_policy | $0.00008720 | 2572.1 ms | $0.00243500 | 2441.8 ms | Public Wi-Fi should be avoided for sensitive activity unless an approv |
| c019 | yes | yes | 100% | 2 | 2 | 3 | 19_employee_data_privacy, 19_employee_data_privacy, 10_onboarding_policy | $0.00009088 | 5574.0 ms | $0.00226750 | 2307.5 ms | Access to employee records is restricted to authorized personnel with  |
| c020 | yes | yes | 100% | 2 | 2 | 3 | 07_code_of_conduct, 15_harassment_policy, 14_grievance_policy | $0.00019504 | 4206.0 ms | $0.00300500 | 3074.0 ms | The policies provide several options and protections for the employee  |
