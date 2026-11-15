# Certification Status — 100 variations

Held certs extract fine; the gap is the **validity status**. `cert_domain` flags compliance-sensitive certs where a wrong signal is a liability, not just wasted time.

*100 variations · grouped by category · generated from `certification_status_100.csv`.*

| Category | Count | Realism |
|---|:--:|---|
| active | 8 | very common |
| renewed | 6 | common |
| expired | 16 | very common |
| revoked | 12 | rare |
| suspended | 8 | rare |
| pending_scheduled | 10 | occasional |
| failed | 6 | occasional |
| expires_future_valid | 10 | common |
| no_status | 8 | common |
| held_out_formats | 8 | common |
| multi_mixed | 8 | occasional |


## active — 8 · very common · **positive control**

| ID | Domain | Résumé line | Should return | Fails if |
|---|---|---|---|---|
| C001 | cloud | AWS Certified Solutions Architect — active, valid through 2027 | active | valid cert dropped, or shown as expired |
| C002 | project-mgmt | PMP (current) | active | valid cert dropped, or shown as expired |
| C003 | security | CISSP — in good standing | active | valid cert dropped, or shown as expired |
| C004 | healthcare-regulated | Registered Nurse (RN) license — active, valid through 2027 | active | valid cert dropped, or shown as expired |
| C005 | finance-regulated | CPA (current) | active | valid cert dropped, or shown as expired |
| C006 | healthcare-regulated | Medical license — in good standing | active | valid cert dropped, or shown as expired |
| C007 | trade | Forklift operator licence — active, valid through 2027 | active | valid cert dropped, or shown as expired |
| C008 | government | Security Clearance (Baseline) (current) | active | valid cert dropped, or shown as expired |

## renewed — 6 · common · **positive control**

| ID | Domain | Résumé line | Should return | Fails if |
|---|---|---|---|---|
| C009 | safety | CPR / First Aid certification — renewed 2021 (current) | active | valid cert dropped, or shown as expired |
| C010 | legal-regulated | Bar admission, recertified 2022 | active | valid cert dropped, or shown as expired |
| C011 | networking | CCNA — renewed 2018 (current) | active | valid cert dropped, or shown as expired |
| C012 | quality | Six Sigma Black Belt, recertified 2019 | active | valid cert dropped, or shown as expired |
| C013 | cloud | AWS Certified Solutions Architect — renewed 2020 (current) | active | valid cert dropped, or shown as expired |
| C014 | project-mgmt | PMP, recertified 2021 | active | valid cert dropped, or shown as expired |

## expired — 16 · very common

| ID | Domain | Résumé line | Should return | Fails if |
|---|---|---|---|---|
| C015 | security | CISSP — expired 2022 | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C016 | healthcare-regulated | Registered Nurse (RN) license, lapsed 2018 | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C017 | finance-regulated | CPA — no longer valid | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C018 | healthcare-regulated | Medical license (expired) | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C019 | trade | Forklift operator licence — expired, renewal pending | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C020 | government | Security Clearance (Baseline) — expired 2022 | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C021 | safety | CPR / First Aid certification, lapsed 2018 | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C022 | legal-regulated | Bar admission — no longer valid | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C023 | networking | CCNA (expired) | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C024 | quality | Six Sigma Black Belt — expired, renewal pending | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C025 | cloud | AWS Certified Solutions Architect — expired 2022 | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C026 | project-mgmt | PMP, lapsed 2018 | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C027 | security | CISSP — no longer valid | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C028 | healthcare-regulated | Registered Nurse (RN) license (expired) | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C029 | finance-regulated | CPA — expired, renewal pending | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C030 | healthcare-regulated | Medical license — expired 2022 | expired | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |

## revoked — 12 · rare

| ID | Domain | Résumé line | Should return | Fails if |
|---|---|---|---|---|
| C031 | trade | Forklift operator licence — revoked 2018 | revoked | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C032 | government | Security Clearance (Baseline) — licence revoked | revoked | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C033 | safety | CPR / First Aid certification — withdrawn by issuer | revoked | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C034 | legal-regulated | Bar admission — revoked 2021 | revoked | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C035 | networking | CCNA — licence revoked | revoked | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C036 | quality | Six Sigma Black Belt — withdrawn by issuer | revoked | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C037 | cloud | AWS Certified Solutions Architect — revoked 2019 | revoked | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C038 | project-mgmt | PMP — licence revoked | revoked | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C039 | security | CISSP — withdrawn by issuer | revoked | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C040 | healthcare-regulated | Registered Nurse (RN) license — revoked 2022 | revoked | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C041 | finance-regulated | CPA — licence revoked | revoked | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C042 | healthcare-regulated | Medical license — withdrawn by issuer | revoked | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |

## suspended — 8 · rare

| ID | Domain | Résumé line | Should return | Fails if |
|---|---|---|---|---|
| C043 | trade | Forklift operator licence — temporarily suspended | suspended | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C044 | government | Security Clearance (Baseline) (under suspension) | suspended | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C045 | safety | CPR / First Aid certification — temporarily suspended | suspended | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C046 | legal-regulated | Bar admission (under suspension) | suspended | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C047 | networking | CCNA — temporarily suspended | suspended | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C048 | quality | Six Sigma Black Belt (under suspension) | suspended | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C049 | cloud | AWS Certified Solutions Architect — temporarily suspended | suspended | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |
| C050 | project-mgmt | PMP (under suspension) | suspended | status absent — the invalid cert is indistinguishable from a valid one (name+date only) |

## pending_scheduled — 10 · occasional

| ID | Domain | Résumé line | Should return | Fails if |
|---|---|---|---|---|
| C051 | security | CISSP — exam scheduled 2029 | pending | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C052 | healthcare-regulated | Registered Nurse (RN) license (pending) | pending | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C053 | finance-regulated | CPA — awaiting results | pending | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C054 | healthcare-regulated | Candidate, Medical license | pending | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C055 | trade | Forklift operator licence — exam scheduled 2027 | pending | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C056 | government | Security Clearance (Baseline) (pending) | pending | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C057 | safety | CPR / First Aid certification — awaiting results | pending | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C058 | legal-regulated | Candidate, Bar admission | pending | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C059 | networking | CCNA — exam scheduled 2028 | pending | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C060 | quality | Six Sigma Black Belt (pending) | pending | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |

## failed — 6 · occasional

| ID | Domain | Résumé line | Should return | Fails if |
|---|---|---|---|---|
| C061 | cloud | AWS Certified Solutions Architect — attempted, did not pass | failed | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C062 | project-mgmt | PMP, unsuccessful attempt 2019 | failed | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C063 | security | CISSP — attempted, did not pass | failed | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C064 | healthcare-regulated | Registered Nurse (RN) license, unsuccessful attempt 2021 | failed | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C065 | finance-regulated | CPA — attempted, did not pass | failed | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |
| C066 | healthcare-regulated | Medical license, unsuccessful attempt 2018 | failed | treated as a held credential (no not-held signal); OR wrongly surfaced in 'has {cert}' matches |

## expires_future_valid — 10 · common · **positive control**

| ID | Domain | Résumé line | Should return | Fails if |
|---|---|---|---|---|
| C067 | trade | Forklift operator licence — valid until 2027 | active | valid cert dropped, or shown as expired |
| C068 | government | Security Clearance (Baseline), expires 2028 | active | valid cert dropped, or shown as expired |
| C069 | safety | CPR / First Aid certification — current, expires 2029 | active | valid cert dropped, or shown as expired |
| C070 | legal-regulated | Bar admission — valid until 2027 | active | valid cert dropped, or shown as expired |
| C071 | networking | CCNA, expires 2028 | active | valid cert dropped, or shown as expired |
| C072 | quality | Six Sigma Black Belt — current, expires 2029 | active | valid cert dropped, or shown as expired |
| C073 | cloud | AWS Certified Solutions Architect — valid until 2027 | active | valid cert dropped, or shown as expired |
| C074 | project-mgmt | PMP, expires 2028 | active | valid cert dropped, or shown as expired |
| C075 | security | CISSP — current, expires 2029 | active | valid cert dropped, or shown as expired |
| C076 | healthcare-regulated | Registered Nurse (RN) license — valid until 2027 | active | valid cert dropped, or shown as expired |

## no_status — 8 · common

| ID | Domain | Résumé line | Should return | Fails if |
|---|---|---|---|---|
| C077 | finance-regulated | CPA — 2019 | unknown | cert dropped, or date misread as validity |
| C078 | healthcare-regulated | Medical license | unknown | cert dropped, or date misread as validity |
| C079 | trade | Forklift operator licence — 2021 | unknown | cert dropped, or date misread as validity |
| C080 | government | Security Clearance (Baseline) | unknown | cert dropped, or date misread as validity |
| C081 | safety | CPR / First Aid certification — 2018 | unknown | cert dropped, or date misread as validity |
| C082 | legal-regulated | Bar admission | unknown | cert dropped, or date misread as validity |
| C083 | networking | CCNA — 2020 | unknown | cert dropped, or date misread as validity |
| C084 | quality | Six Sigma Black Belt | unknown | cert dropped, or date misread as validity |

## held_out_formats — 8 · common

| ID | Domain | Résumé line | Should return | Fails if |
|---|---|---|---|---|
| C085 | cloud | AWS Certified Solutions Architect — valid 2022–2027 | mixed | status/validity lost because the form is unusual (format brittleness) |
| C086 | project-mgmt | PMP (caducado 2018) | mixed | status/validity lost because the form is unusual (format brittleness) |
| C087 | security | CISSP — exp. 2019 | mixed | status/validity lost because the form is unusual (format brittleness) |
| C088 | healthcare-regulated | Registered Nurse (RN) license: status inactive | mixed | status/validity lost because the form is unusual (format brittleness) |
| C089 | finance-regulated | CPA — valid 2021–2028 | mixed | status/validity lost because the form is unusual (format brittleness) |
| C090 | healthcare-regulated | Medical license (caducado 2022) | mixed | status/validity lost because the form is unusual (format brittleness) |
| C091 | trade | Forklift operator licence — exp. 2018 | mixed | status/validity lost because the form is unusual (format brittleness) |
| C092 | government | Security Clearance (Baseline): status inactive | mixed | status/validity lost because the form is unusual (format brittleness) |

## multi_mixed — 8 · occasional

| ID | Domain | Résumé line | Should return | Fails if |
|---|---|---|---|---|
| C093 | cloud | AWS Certified Solutions Architect — active (renewed 2027)  \|\|  AWS Certified Solutions Architect — expired 2018 | active + expired (distinct) | collapsed to one, or valid one dropped, or statuses swapped/absent |
| C094 | project-mgmt | PMP — active (renewed 2028)  \|\|  PMP — expired 2019 | active + expired (distinct) | collapsed to one, or valid one dropped, or statuses swapped/absent |
| C095 | security | CISSP — active (renewed 2029)  \|\|  CISSP — expired 2020 | active + expired (distinct) | collapsed to one, or valid one dropped, or statuses swapped/absent |
| C096 | healthcare-regulated | Registered Nurse (RN) license — active (renewed 2027)  \|\|  Registered Nurse (RN) license — expired 2021 | active + expired (distinct) | collapsed to one, or valid one dropped, or statuses swapped/absent |
| C097 | finance-regulated | CPA — active (renewed 2028)  \|\|  CPA — expired 2022 | active + expired (distinct) | collapsed to one, or valid one dropped, or statuses swapped/absent |
| C098 | healthcare-regulated | Medical license — active (renewed 2029)  \|\|  Medical license — expired 2018 | active + expired (distinct) | collapsed to one, or valid one dropped, or statuses swapped/absent |
| C099 | trade | Forklift operator licence — active (renewed 2027)  \|\|  Forklift operator licence — expired 2019 | active + expired (distinct) | collapsed to one, or valid one dropped, or statuses swapped/absent |
| C100 | government | Security Clearance (Baseline) — active (renewed 2028)  \|\|  Security Clearance (Baseline) — expired 2020 | active + expired (distinct) | collapsed to one, or valid one dropped, or statuses swapped/absent |
