# Round 4 — analysis summary

Analysed 60/60

## Verdict tally

- ambiguous: 7
- confirmed: 9
- correct: 25
- miss: 2
- partial: 12
- unsupported: 5

## By category

- **negated_skills**: confirmed 7, correct 2, ambiguous 1
- **skill_ownership**: correct 4, ambiguous 6
- **certification_validity**: correct 3, partial 5, miss 2
- **employment_classification**: correct 5, unsupported 5
- **work_authorisation**: correct 3, partial 7
- **employment_duration**: correct 8, confirmed 2

## Per test

| ID | Category | Controlled | Verdict |
|---|---|---|---|
| R401 | negated_skills | negation: "No hands-on experienc | confirmed |
| R402 | negated_skills | negation: "Python: advanced. Jav | confirmed |
| R403 | negated_skills | negation: "Experienced in AWS, b | confirmed |
| R404 | negated_skills | negation: "Theoretical knowledge | confirmed |
| R405 | negated_skills | negation: "Previously used React | confirmed |
| R406 | negated_skills | negation: "Without any SQL backg | confirmed |
| R407 | negated_skills | negation: "Not certified in AWS, | correct |
| R408 | negated_skills | negation: "No experience with Ja | confirmed |
| R409 | negated_skills | negation: "I do not manage Kuber | ambiguous |
| R410 | negated_skills | positive control (all affirmed) | correct |
| R411 | skill_ownership | personal (positive control) | correct |
| R412 | skill_ownership | managed engineers, no coding | ambiguous |
| R413 | skill_ownership | team used tool; candidate did fi | ambiguous |
| R414 | skill_ownership | personally configured (positive) | correct |
| R415 | skill_ownership | external contractor | ambiguous |
| R416 | skill_ownership | reviewed, did not write | ambiguous |
| R417 | skill_ownership | personal Go (positive) | correct |
| R418 | skill_ownership | managed team, explicitly never u | ambiguous |
| R419 | skill_ownership | both personal and supervised | correct |
| R420 | skill_ownership | competitor-tech mention only | ambiguous |
| R421 | certification_validity | active (positive) | correct |
| R422 | certification_validity | expired | partial |
| R423 | certification_validity | renewed (positive) | correct |
| R424 | certification_validity | revoked | partial |
| R425 | certification_validity | scheduled, not attempted | miss |
| R426 | certification_validity | attempted, failed | miss |
| R427 | certification_validity | training only, no exam | partial |
| R428 | certification_validity | suspended temporarily | partial |
| R429 | certification_validity | two certs: active + expired | correct |
| R430 | certification_validity | expiry date, no validity stateme | partial |
| R431 | employment_classification | permanent full-time (control) | correct |
| R432 | employment_classification | fixed-term full-time contract | correct |
| R433 | employment_classification | permanent part-time | unsupported |
| R434 | employment_classification | unpaid volunteer | unsupported |
| R435 | employment_classification | paid summer internship | correct |
| R436 | employment_classification | independent consulting contract | unsupported |
| R437 | employment_classification | temporary agency employment | unsupported |
| R438 | employment_classification | casual, variable hours | unsupported |
| R439 | employment_classification | volunteer alongside permanent (t | correct |
| R440 | employment_classification | contract-to-permanent conversion | correct |
| R441 | work_authorisation | citizen | correct |
| R442 | work_authorisation | permanent resident | partial |
| R443 | work_authorisation | temp visa with expiry | partial |
| R444 | work_authorisation | expired | correct |
| R445 | work_authorisation | needs sponsorship | partial |
| R446 | work_authorisation | no sponsorship | partial |
| R447 | work_authorisation | hours restriction | partial |
| R448 | work_authorisation | unknown current status | partial |
| R449 | work_authorisation | eligible, not obtained | partial |
| R450 | work_authorisation | CONFLICTING statements | correct |
| R451 | employment_duration | two ENTIRELY overlapping jobs (s | correct |
| R452 | employment_duration | three PARTIALLY overlapping jobs | correct |
| R453 | employment_duration | full-time + freelance weekend wo | correct |
| R454 | employment_duration | multiple short contracts with ga | correct |
| R455 | employment_duration | three promotions, one employer,  | correct |
| R456 | employment_duration | role 2021 – Present (open curren | correct |
| R457 | employment_duration | explicit career break | correct |
| R458 | employment_duration | part-time over five years | correct |
| R459 | employment_duration | concurrent internships + univers | confirmed |
| R460 | employment_duration | one completed + one unspecified  | confirmed |