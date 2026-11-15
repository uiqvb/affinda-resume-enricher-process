# Round 3 — analysis summary

Analysed 48/48

## Verdict tally

- ambiguous: 12
- confirmed: 5
- correct: 22
- miss: 1
- unsupported: 8

## By category

- **negated_skills**: correct 1, confirmed 5, ambiguous 2
- **work_authorisation**: correct 7, unsupported 1
- **skill_ownership**: correct 2, ambiguous 6
- **experience_duration**: correct 8
- **certification_status**: correct 1, ambiguous 3, unsupported 3, miss 1
- **employment_type**: correct 3, unsupported 4, ambiguous 1

## Per test

| ID | Category | Controlled | Verdict |
|---|---|---|---|
| R301 | negated_skills | positive control: plain skills lis | correct |
| R302 | negated_skills | negative control: denied skill in  | confirmed |
| R303 | negated_skills | negated proficiency | confirmed |
| R304 | negated_skills | AMBIGUOUS partial exposure | ambiguous |
| R305 | negated_skills | paired: expert + denied in one lin | confirmed |
| R306 | negated_skills | contrastive 'but not' | confirmed |
| R307 | negated_skills | AMBIGUOUS past/discontinued use | ambiguous |
| R308 | negated_skills | negation inside the skills list | confirmed |
| R309 | work_authorisation | citizen | correct |
| R310 | work_authorisation | permanent resident | correct |
| R311 | work_authorisation | needs sponsorship | correct |
| R312 | work_authorisation | authorised, no sponsorship | correct |
| R313 | work_authorisation | visa with expiry | correct |
| R314 | work_authorisation | expired authorisation | correct |
| R315 | work_authorisation | unknown (no statement) | correct |
| R316 | work_authorisation | AMBIGUOUS non-statement | unsupported |
| R317 | skill_ownership | personal (positive control) | correct |
| R318 | skill_ownership | managed others (negative) | ambiguous |
| R319 | skill_ownership | led team using tool | ambiguous |
| R320 | skill_ownership | oversaw work by others | ambiguous |
| R321 | skill_ownership | paired personal | correct |
| R322 | skill_ownership | paired managed | ambiguous |
| R323 | skill_ownership | AMBIGUOUS responsibility | ambiguous |
| R324 | skill_ownership | mixed in one role | ambiguous |
| R325 | experience_duration | explicit claim vs computable dates | correct |
| R326 | experience_duration | part-time hours | correct |
| R327 | experience_duration | overlapping roles (double-count ri | correct |
| R328 | experience_duration | career gap | correct |
| R329 | experience_duration | approximate duration | correct |
| R330 | experience_duration | explicit claim contradicts dates | correct |
| R331 | experience_duration | seasonal/intermittent | correct |
| R332 | experience_duration | paired full-time vs part-time (sam | correct |
| R333 | certification_status | active (positive control) | correct |
| R334 | certification_status | expired | ambiguous |
| R335 | certification_status | pending | ambiguous |
| R336 | certification_status | failed | ambiguous |
| R337 | certification_status | revoked | unsupported |
| R338 | certification_status | training only | unsupported |
| R339 | certification_status | coursework, not awarded | unsupported |
| R340 | certification_status | paired active vs expired (same cer | miss |
| R341 | employment_type | permanent (control) | correct |
| R342 | employment_type | contract | unsupported |
| R343 | employment_type | internship | correct |
| R344 | employment_type | volunteer (unpaid) | unsupported |
| R345 | employment_type | freelance | unsupported |
| R346 | employment_type | temporary/seasonal | unsupported |
| R347 | employment_type | AMBIGUOUS 'Consultant' | ambiguous |
| R348 | employment_type | paired: SAME role as internship vs | correct |