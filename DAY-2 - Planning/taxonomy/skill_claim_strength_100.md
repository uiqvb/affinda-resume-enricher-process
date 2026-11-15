# Skill Claim Strength — 100 variations

The realistic **proficiency spectrum** (denial is the far end, only 10 rows). The `distractor_fp_trap` rows measure **precision** — the affirmed skill must survive.

*100 variations · grouped by category · generated from `skill_claim_strength_100.csv`.*

| Category | Count | Realism |
|---|:--:|---|
| expert | 8 | very common |
| proficient | 8 | very common |
| working | 8 | common |
| basic | 10 | very common |
| exposure | 12 | very common |
| learning | 10 | common |
| theoretical | 6 | common |
| historical | 8 | common |
| denied | 10 | rare |
| scoped_exclusion | 8 | occasional |
| interest | 4 | occasional |
| cert_vs_use | 2 | occasional |
| distractor_fp_trap | 6 | occasional |


## expert — 8 · very common · **positive control**

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| S001 | Expert in Python | extract (optionally tag strong) | 'Python' missing from skills (should be present) |
| S002 | 8+ years of Java | extract (optionally tag strong) | 'Java' missing from skills (should be present) |
| S003 | Advanced SQL | extract (optionally tag strong) | 'SQL' missing from skills (should be present) |
| S004 | Expert in AWS | extract (optionally tag strong) | 'AWS' missing from skills (should be present) |
| S005 | 8+ years of Azure | extract (optionally tag strong) | 'Azure' missing from skills (should be present) |
| S006 | Advanced Kubernetes | extract (optionally tag strong) | 'Kubernetes' missing from skills (should be present) |
| S007 | Expert in Docker | extract (optionally tag strong) | 'Docker' missing from skills (should be present) |
| S008 | 8+ years of React | extract (optionally tag strong) | 'React' missing from skills (should be present) |

## proficient — 8 · very common · **positive control**

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| S009 | Proficient in Go | extract (optionally tag strong) | 'Go' missing from skills (should be present) |
| S010 | Strong Tableau experience | extract (optionally tag strong) | 'Tableau' missing from skills (should be present) |
| S011 | Solid Spark | extract (optionally tag strong) | 'Spark' missing from skills (should be present) |
| S012 | Proficient in TypeScript | extract (optionally tag strong) | 'TypeScript' missing from skills (should be present) |
| S013 | Strong Python experience | extract (optionally tag strong) | 'Python' missing from skills (should be present) |
| S014 | Solid Java | extract (optionally tag strong) | 'Java' missing from skills (should be present) |
| S015 | Proficient in SQL | extract (optionally tag strong) | 'SQL' missing from skills (should be present) |
| S016 | Strong AWS experience | extract (optionally tag strong) | 'AWS' missing from skills (should be present) |

## working — 8 · common

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| S017 | Working knowledge of Azure | extract, tag moderate | 'Azure' missing from skills (should be present) |
| S018 | Hands-on Kubernetes | extract, tag moderate | 'Kubernetes' missing from skills (should be present) |
| S019 | Comfortable with Docker | extract, tag moderate | 'Docker' missing from skills (should be present) |
| S020 | Working knowledge of React | extract, tag moderate | 'React' missing from skills (should be present) |
| S021 | Hands-on Go | extract, tag moderate | 'Go' missing from skills (should be present) |
| S022 | Comfortable with Tableau | extract, tag moderate | 'Tableau' missing from skills (should be present) |
| S023 | Working knowledge of Spark | extract, tag moderate | 'Spark' missing from skills (should be present) |
| S024 | Hands-on TypeScript | extract, tag moderate | 'TypeScript' missing from skills (should be present) |

## basic — 10 · very common

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| S025 | Basic Python | extract, tag weak | 'Python' extracted identical to an expert-level claim (no strength signal) |
| S026 | Familiar with Java | extract, tag weak | 'Java' extracted identical to an expert-level claim (no strength signal) |
| S027 | Some SQL | extract, tag weak | 'SQL' extracted identical to an expert-level claim (no strength signal) |
| S028 | Basic AWS | extract, tag weak | 'AWS' extracted identical to an expert-level claim (no strength signal) |
| S029 | Familiar with Azure | extract, tag weak | 'Azure' extracted identical to an expert-level claim (no strength signal) |
| S030 | Some Kubernetes | extract, tag weak | 'Kubernetes' extracted identical to an expert-level claim (no strength signal) |
| S031 | Basic Docker | extract, tag weak | 'Docker' extracted identical to an expert-level claim (no strength signal) |
| S032 | Familiar with React | extract, tag weak | 'React' extracted identical to an expert-level claim (no strength signal) |
| S033 | Some Go | extract, tag weak | 'Go' extracted identical to an expert-level claim (no strength signal) |
| S034 | Basic Tableau | extract, tag weak | 'Tableau' extracted identical to an expert-level claim (no strength signal) |

## exposure — 12 · very common

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| S035 | Exposure to Spark | extract, tag weak/low | 'Spark' extracted identical to an expert-level claim (no strength signal) |
| S036 | Limited exposure to TypeScript | extract, tag weak/low | 'TypeScript' extracted identical to an expert-level claim (no strength signal) |
| S037 | Brief exposure to Python | extract, tag weak/low | 'Python' extracted identical to an expert-level claim (no strength signal) |
| S038 | Exposure to Java | extract, tag weak/low | 'Java' extracted identical to an expert-level claim (no strength signal) |
| S039 | Limited exposure to SQL | extract, tag weak/low | 'SQL' extracted identical to an expert-level claim (no strength signal) |
| S040 | Brief exposure to AWS | extract, tag weak/low | 'AWS' extracted identical to an expert-level claim (no strength signal) |
| S041 | Exposure to Azure | extract, tag weak/low | 'Azure' extracted identical to an expert-level claim (no strength signal) |
| S042 | Limited exposure to Kubernetes | extract, tag weak/low | 'Kubernetes' extracted identical to an expert-level claim (no strength signal) |
| S043 | Brief exposure to Docker | extract, tag weak/low | 'Docker' extracted identical to an expert-level claim (no strength signal) |
| S044 | Exposure to React | extract, tag weak/low | 'React' extracted identical to an expert-level claim (no strength signal) |
| S045 | Limited exposure to Go | extract, tag weak/low | 'Go' extracted identical to an expert-level claim (no strength signal) |
| S046 | Brief exposure to Tableau | extract, tag weak/low | 'Tableau' extracted identical to an expert-level claim (no strength signal) |

## learning — 10 · common

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| S047 | Currently learning Spark | extract, tag aspirational (not possessed) | 'Spark' extracted identical to an expert-level claim (no strength signal) |
| S048 | Studying TypeScript | extract, tag aspirational (not possessed) | 'TypeScript' extracted identical to an expert-level claim (no strength signal) |
| S049 | Learning Python in my spare time | extract, tag aspirational (not possessed) | 'Python' extracted identical to an expert-level claim (no strength signal) |
| S050 | Currently learning Java | extract, tag aspirational (not possessed) | 'Java' extracted identical to an expert-level claim (no strength signal) |
| S051 | Studying SQL | extract, tag aspirational (not possessed) | 'SQL' extracted identical to an expert-level claim (no strength signal) |
| S052 | Learning AWS in my spare time | extract, tag aspirational (not possessed) | 'AWS' extracted identical to an expert-level claim (no strength signal) |
| S053 | Currently learning Azure | extract, tag aspirational (not possessed) | 'Azure' extracted identical to an expert-level claim (no strength signal) |
| S054 | Studying Kubernetes | extract, tag aspirational (not possessed) | 'Kubernetes' extracted identical to an expert-level claim (no strength signal) |
| S055 | Learning Docker in my spare time | extract, tag aspirational (not possessed) | 'Docker' extracted identical to an expert-level claim (no strength signal) |
| S056 | Currently learning React | extract, tag aspirational (not possessed) | 'React' extracted identical to an expert-level claim (no strength signal) |

## theoretical — 6 · common

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| S057 | Theoretical knowledge of Go, no practical experience | extract, tag theoretical | 'Go' extracted identical to an expert-level claim (no strength signal) |
| S058 | Academic Tableau only, no production use | extract, tag theoretical | 'Tableau' extracted identical to an expert-level claim (no strength signal) |
| S059 | Theoretical knowledge of Spark, no practical experience | extract, tag theoretical | 'Spark' extracted identical to an expert-level claim (no strength signal) |
| S060 | Academic TypeScript only, no production use | extract, tag theoretical | 'TypeScript' extracted identical to an expert-level claim (no strength signal) |
| S061 | Theoretical knowledge of Python, no practical experience | extract, tag theoretical | 'Python' extracted identical to an expert-level claim (no strength signal) |
| S062 | Academic Java only, no production use | extract, tag theoretical | 'Java' extracted identical to an expert-level claim (no strength signal) |

## historical — 8 · common

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| S063 | Previously used SQL, not in recent years | extract, tag lapsed/historical | 'SQL' extracted identical to an expert-level claim (no strength signal) |
| S064 | Used AWS years ago | extract, tag lapsed/historical | 'AWS' extracted identical to an expert-level claim (no strength signal) |
| S065 | Formerly worked with Azure | extract, tag lapsed/historical | 'Azure' extracted identical to an expert-level claim (no strength signal) |
| S066 | Previously used Kubernetes, not in recent years | extract, tag lapsed/historical | 'Kubernetes' extracted identical to an expert-level claim (no strength signal) |
| S067 | Used Docker years ago | extract, tag lapsed/historical | 'Docker' extracted identical to an expert-level claim (no strength signal) |
| S068 | Formerly worked with React | extract, tag lapsed/historical | 'React' extracted identical to an expert-level claim (no strength signal) |
| S069 | Previously used Go, not in recent years | extract, tag lapsed/historical | 'Go' extracted identical to an expert-level claim (no strength signal) |
| S070 | Used Tableau years ago | extract, tag lapsed/historical | 'Tableau' extracted identical to an expert-level claim (no strength signal) |

## denied — 10 · rare

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| S071 | No experience with Spark | suppress OR tag denied (must NOT list as possessed) | 'Spark' extracted as a plain possessed skill with no negative marker |
| S072 | Not proficient in TypeScript | suppress OR tag denied (must NOT list as possessed) | 'TypeScript' extracted as a plain possessed skill with no negative marker |
| S073 | Python: none | suppress OR tag denied (must NOT list as possessed) | 'Python' extracted as a plain possessed skill with no negative marker |
| S074 | Without any Java background | suppress OR tag denied (must NOT list as possessed) | 'Java' extracted as a plain possessed skill with no negative marker |
| S075 | No experience with SQL | suppress OR tag denied (must NOT list as possessed) | 'SQL' extracted as a plain possessed skill with no negative marker |
| S076 | Not proficient in AWS | suppress OR tag denied (must NOT list as possessed) | 'AWS' extracted as a plain possessed skill with no negative marker |
| S077 | Azure: none | suppress OR tag denied (must NOT list as possessed) | 'Azure' extracted as a plain possessed skill with no negative marker |
| S078 | Without any Kubernetes background | suppress OR tag denied (must NOT list as possessed) | 'Kubernetes' extracted as a plain possessed skill with no negative marker |
| S079 | No experience with Docker | suppress OR tag denied (must NOT list as possessed) | 'Docker' extracted as a plain possessed skill with no negative marker |
| S080 | Not proficient in React | suppress OR tag denied (must NOT list as possessed) | 'React' extracted as a plain possessed skill with no negative marker |

## scoped_exclusion — 8 · occasional

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| S081 | Go, but not AWS | keep Go; suppress/deny AWS | 'AWS' extracted as possessed, and/or 'Go' wrongly dropped |
| S082 | Tableau (not SQL) | keep Tableau; suppress/deny SQL | 'SQL' extracted as possessed, and/or 'Tableau' wrongly dropped |
| S083 | Experienced in Spark; never used Java | keep Spark; suppress/deny Java | 'Java' extracted as possessed, and/or 'Spark' wrongly dropped |
| S084 | TypeScript, but not Python | keep TypeScript; suppress/deny Python | 'Python' extracted as possessed, and/or 'TypeScript' wrongly dropped |
| S085 | Python (not TypeScript) | keep Python; suppress/deny TypeScript | 'TypeScript' extracted as possessed, and/or 'Python' wrongly dropped |
| S086 | Experienced in Java; never used Spark | keep Java; suppress/deny Spark | 'Spark' extracted as possessed, and/or 'Java' wrongly dropped |
| S087 | SQL, but not Tableau | keep SQL; suppress/deny Tableau | 'Tableau' extracted as possessed, and/or 'SQL' wrongly dropped |
| S088 | AWS (not Go) | keep AWS; suppress/deny Go | 'Go' extracted as possessed, and/or 'AWS' wrongly dropped |

## interest — 4 · occasional

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| S089 | Interested in Azure | extract, tag interest (not possessed) | 'Azure' extracted identical to an expert-level claim (no strength signal) |
| S090 | Keen to learn Kubernetes | extract, tag interest (not possessed) | 'Kubernetes' extracted identical to an expert-level claim (no strength signal) |
| S091 | Interested in Docker | extract, tag interest (not possessed) | 'Docker' extracted identical to an expert-level claim (no strength signal) |
| S092 | Keen to learn React | extract, tag interest (not possessed) | 'React' extracted identical to an expert-level claim (no strength signal) |

## cert_vs_use — 2 · occasional

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| S093 | Not certified in Go, but use Go daily | Go kept as possessed (cert denial != skill denial) | 'Go' suppressed because of the certification denial |
| S094 | Not certified in Tableau, but use Tableau daily | Tableau kept as possessed (cert denial != skill denial) | 'Tableau' suppressed because of the certification denial |

## distractor_fp_trap — 6 · occasional

| ID | Résumé line | Should return | Fails if |
|---|---|---|---|
| S095 | No experience with Java; expert in Spark | keep Spark (affirmed); suppress/deny Java | 'Spark' (affirmed) wrongly suppressed, OR 'Java' (denied) extracted as possessed |
| S096 | Migrated away from Python to TypeScript | keep TypeScript (affirmed); suppress/deny Python | 'TypeScript' (affirmed) wrongly suppressed, OR 'Python' (denied) extracted as possessed |
| S097 | Replaced TypeScript with Python across the stack | keep Python (affirmed); suppress/deny TypeScript | 'Python' (affirmed) wrongly suppressed, OR 'TypeScript' (denied) extracted as possessed |
| S098 | No experience with Spark; expert in Java | keep Java (affirmed); suppress/deny Spark | 'Java' (affirmed) wrongly suppressed, OR 'Spark' (denied) extracted as possessed |
| S099 | Migrated away from Tableau to SQL | keep SQL (affirmed); suppress/deny Tableau | 'SQL' (affirmed) wrongly suppressed, OR 'Tableau' (denied) extracted as possessed |
| S100 | Replaced Go with AWS across the stack | keep AWS (affirmed); suppress/deny Go | 'AWS' (affirmed) wrongly suppressed, OR 'Go' (denied) extracted as possessed |
