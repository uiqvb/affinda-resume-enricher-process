# Education Completion Status — 100 variations

Does any phrasing produce a **structured completion status**, and does a terminal year ever stop being treated as a conferral date? (Prior rounds: 0/16 status.)

*100 variations · grouped by category · generated from `education_status_100.csv`.*

| Category | Count | Realism |
|---|:--:|---|
| completed | 10 | very common |
| in_progress | 16 | very common |
| expected | 12 | very common |
| incomplete_discontinued | 14 | occasional |
| withdrawn | 10 | occasional |
| not_awarded | 12 | occasional |
| deferred_leave | 8 | rare |
| abd_partial | 8 | rare |
| unknown_no_signal | 4 | common |
| multi_entry | 6 | common |


## completed — 10 · very common · **positive control**

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| E001 | Bachelor of Science in Computer Science, Riverside University, 2018 | completed | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E002 | Master of Engineering — Northgate Institute (graduated 2019) | completed | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E003 | Juris Doctor (JD), Lakeside College, conferred 2020 | completed | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E004 | Doctor of Medicine (MD) (2021), Summit State University | completed | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E005 | PhD in Chemistry, Harbour Polytechnic, 2022 | completed | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E006 | Associate of Arts — Riverside University (graduated 2018) | completed | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E007 | MBA, Northgate Institute, conferred 2019 | completed | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E008 | Bachelor of Nursing (2020), Lakeside College | completed | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E009 | Diploma in Accounting, Summit State University, 2021 | completed | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E010 | Certificate IV in Cybersecurity — Harbour Polytechnic (graduated 2022) | completed | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |

## in_progress — 16 · very common

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| E011 | Bachelor of Science in Computer Science, Riverside University — currently enrolled | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E012 | Master of Engineering (in progress), Northgate Institute | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E013 | Pursuing Juris Doctor (JD), Lakeside College | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E014 | Doctor of Medicine (MD), Summit State University, 2021–present | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E015 | Candidate for PhD in Chemistry, Harbour Polytechnic | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E016 | Studying towards Associate of Arts, Riverside University | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E017 | MBA, Northgate Institute — ongoing | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E018 | Currently completing Bachelor of Nursing, Lakeside College | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E019 | Diploma in Accounting, Summit State University — currently enrolled | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E020 | Certificate IV in Cybersecurity (in progress), Harbour Polytechnic | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E021 | Pursuing Bachelor of Science in Computer Science, Riverside University | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E022 | Master of Engineering, Northgate Institute, 2019–present | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E023 | Candidate for Juris Doctor (JD), Lakeside College | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E024 | Studying towards Doctor of Medicine (MD), Summit State University | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E025 | PhD in Chemistry, Harbour Polytechnic — ongoing | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E026 | Currently completing Associate of Arts, Riverside University | in_progress | marked completed, or a conferral date invented, or entry dropped |

## expected — 12 · very common

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| E027 | MBA, Northgate Institute — expected 2029 | expected | future year emitted as a conferral end date (looks graduated); no in-progress/expected status |
| E028 | Bachelor of Nursing, Lakeside College, anticipated graduation 2027 | expected | future year emitted as a conferral end date (looks graduated); no in-progress/expected status |
| E029 | Diploma in Accounting — expected completion 2028, Summit State University | expected | future year emitted as a conferral end date (looks graduated); no in-progress/expected status |
| E030 | Certificate IV in Cybersecurity, Harbour Polytechnic (graduating 2029) | expected | future year emitted as a conferral end date (looks graduated); no in-progress/expected status |
| E031 | Bachelor of Science in Computer Science, Riverside University — due 2027 | expected | future year emitted as a conferral end date (looks graduated); no in-progress/expected status |
| E032 | Master of Engineering, Northgate Institute — expected 2028 | expected | future year emitted as a conferral end date (looks graduated); no in-progress/expected status |
| E033 | Juris Doctor (JD), Lakeside College, anticipated graduation 2029 | expected | future year emitted as a conferral end date (looks graduated); no in-progress/expected status |
| E034 | Doctor of Medicine (MD) — expected completion 2027, Summit State University | expected | future year emitted as a conferral end date (looks graduated); no in-progress/expected status |
| E035 | PhD in Chemistry, Harbour Polytechnic (graduating 2028) | expected | future year emitted as a conferral end date (looks graduated); no in-progress/expected status |
| E036 | Associate of Arts, Riverside University — due 2029 | expected | future year emitted as a conferral end date (looks graduated); no in-progress/expected status |
| E037 | MBA, Northgate Institute — expected 2027 | expected | future year emitted as a conferral end date (looks graduated); no in-progress/expected status |
| E038 | Bachelor of Nursing, Lakeside College, anticipated graduation 2028 | expected | future year emitted as a conferral end date (looks graduated); no in-progress/expected status |

## incomplete_discontinued — 14 · occasional

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| E039 | Diploma in Accounting, Summit State University — discontinued before completion | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E040 | Certificate IV in Cybersecurity (incomplete), Harbour Polytechnic | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E041 | Bachelor of Science in Computer Science, Riverside University — did not complete | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E042 | Master of Engineering, Northgate Institute, left before finishing (2019) | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E043 | Partial Juris Doctor (JD), Lakeside College | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E044 | Doctor of Medicine (MD), Summit State University — unfinished | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E045 | PhD in Chemistry, Harbour Polytechnic — discontinued before completion | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E046 | Associate of Arts (incomplete), Riverside University | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E047 | MBA, Northgate Institute — did not complete | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E048 | Bachelor of Nursing, Lakeside College, left before finishing (2020) | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E049 | Partial Diploma in Accounting, Summit State University | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E050 | Certificate IV in Cybersecurity, Harbour Polytechnic — unfinished | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E051 | Bachelor of Science in Computer Science, Riverside University — discontinued before completion | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E052 | Master of Engineering (incomplete), Northgate Institute | incomplete | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |

## withdrawn — 10 · occasional

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| E053 | Juris Doctor (JD), Lakeside College — withdrawn 2020 | withdrawn | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E054 | Doctor of Medicine (MD), Summit State University — withdrew 2021 | withdrawn | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E055 | PhD in Chemistry, Harbour Polytechnic, left the program 2022 | withdrawn | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E056 | Associate of Arts (withdrawn 2018), Riverside University | withdrawn | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E057 | MBA, Northgate Institute — withdrawn 2019 | withdrawn | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E058 | Bachelor of Nursing, Lakeside College — withdrew 2020 | withdrawn | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E059 | Diploma in Accounting, Summit State University, left the program 2021 | withdrawn | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E060 | Certificate IV in Cybersecurity (withdrawn 2022), Harbour Polytechnic | withdrawn | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E061 | Bachelor of Science in Computer Science, Riverside University — withdrawn 2018 | withdrawn | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E062 | Master of Engineering, Northgate Institute — withdrew 2019 | withdrawn | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |

## not_awarded — 12 · occasional

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| E063 | Juris Doctor (JD), Lakeside College — coursework completed, qualification not awarded | not_awarded | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E064 | Doctor of Medicine (MD), Summit State University — attended, no degree conferred | not_awarded | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E065 | PhD in Chemistry, Harbour Polytechnic, requirements not met (2022) | not_awarded | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E066 | Associate of Arts — Riverside University, exams not passed | not_awarded | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E067 | MBA, Northgate Institute — coursework completed, qualification not awarded | not_awarded | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E068 | Bachelor of Nursing, Lakeside College — attended, no degree conferred | not_awarded | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E069 | Diploma in Accounting, Summit State University, requirements not met (2021) | not_awarded | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E070 | Certificate IV in Cybersecurity — Harbour Polytechnic, exams not passed | not_awarded | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E071 | Bachelor of Science in Computer Science, Riverside University — coursework completed, qualification not awarded | not_awarded | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E072 | Master of Engineering, Northgate Institute — attended, no degree conferred | not_awarded | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E073 | Juris Doctor (JD), Lakeside College, requirements not met (2020) | not_awarded | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |
| E074 | Doctor of Medicine (MD) — Summit State University, exams not passed | not_awarded | status absent AND the terminal year is emitted as a conferral-style end date (looks completed) |

## deferred_leave — 8 · rare

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| E075 | PhD in Chemistry, Harbour Polytechnic — deferred | deferred | marked completed, or a conferral date invented, or entry dropped |
| E076 | Associate of Arts, Riverside University — on academic leave | deferred | marked completed, or a conferral date invented, or entry dropped |
| E077 | MBA, Northgate Institute — study break since 2019 | deferred | marked completed, or a conferral date invented, or entry dropped |
| E078 | Bachelor of Nursing, Lakeside College (enrolment suspended) | deferred | marked completed, or a conferral date invented, or entry dropped |
| E079 | Diploma in Accounting, Summit State University — deferred | deferred | marked completed, or a conferral date invented, or entry dropped |
| E080 | Certificate IV in Cybersecurity, Harbour Polytechnic — on academic leave | deferred | marked completed, or a conferral date invented, or entry dropped |
| E081 | Bachelor of Science in Computer Science, Riverside University — study break since 2018 | deferred | marked completed, or a conferral date invented, or entry dropped |
| E082 | Master of Engineering, Northgate Institute (enrolment suspended) | deferred | marked completed, or a conferral date invented, or entry dropped |

## abd_partial — 8 · rare

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| E083 | Juris Doctor (JD) (ABD — all but dissertation), Lakeside College | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E084 | Doctor of Medicine (MD), Summit State University — comprehensive exams passed, dissertation pending | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E085 | PhD in Chemistry, Harbour Polytechnic — coursework complete, thesis pending | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E086 | Associate of Arts — Riverside University, candidate (ABD) | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E087 | MBA (ABD — all but dissertation), Northgate Institute | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E088 | Bachelor of Nursing, Lakeside College — comprehensive exams passed, dissertation pending | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E089 | Diploma in Accounting, Summit State University — coursework complete, thesis pending | in_progress | marked completed, or a conferral date invented, or entry dropped |
| E090 | Certificate IV in Cybersecurity — Harbour Polytechnic, candidate (ABD) | in_progress | marked completed, or a conferral date invented, or entry dropped |

## unknown_no_signal — 4 · common

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| E091 | Bachelor of Science in Computer Science, Riverside University | unknown | entry dropped, or silently marked completed |
| E092 | Master of Engineering — Northgate Institute | unknown | entry dropped, or silently marked completed |
| E093 | Juris Doctor (JD), Lakeside College | unknown | entry dropped, or silently marked completed |
| E094 | Doctor of Medicine (MD) — Summit State University | unknown | entry dropped, or silently marked completed |

## multi_entry — 6 · common

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| E095 | Bachelor of Science in Computer Science, Harbour Polytechnic, 2018  \|\|  Doctor of Medicine (MD), Riverside University — currently enrolled | completed + in_progress (distinct) | the in-progress entry is shown completed, or either is dropped |
| E096 | Master of Engineering, Northgate Institute, 2019  \|\|  PhD in Chemistry, Lakeside College — currently enrolled | completed + in_progress (distinct) | the in-progress entry is shown completed, or either is dropped |
| E097 | Juris Doctor (JD), Summit State University, 2020  \|\|  Associate of Arts, Harbour Polytechnic — currently enrolled | completed + in_progress (distinct) | the in-progress entry is shown completed, or either is dropped |
| E098 | Doctor of Medicine (MD), Riverside University, 2021  \|\|  MBA, Northgate Institute — currently enrolled | completed + in_progress (distinct) | the in-progress entry is shown completed, or either is dropped |
| E099 | PhD in Chemistry, Lakeside College, 2022  \|\|  Bachelor of Nursing, Summit State University — currently enrolled | completed + in_progress (distinct) | the in-progress entry is shown completed, or either is dropped |
| E100 | Associate of Arts, Harbour Polytechnic, 2018  \|\|  Diploma in Accounting, Riverside University — currently enrolled | completed + in_progress (distinct) | the in-progress entry is shown completed, or either is dropped |
