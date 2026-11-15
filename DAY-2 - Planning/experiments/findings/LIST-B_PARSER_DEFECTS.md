> # 🐞 LIST B — PARSER DEFECTS (bugs to report to Affinda)
> **This file = a side log of genuine parser bugs**, kept so you can raise them with
> Affinda. **These are NOT what the enricher is built on.** The enricher is built on the
> three *missing fields* in **[`LIST-A_RESULTS.md`](LIST-A_RESULTS.md)**. Removing a bug
> from this list (e.g. the old Defect 5) does not affect the product at all.

---

# Parser defects log — to raise with Affinda

*Genuine extraction **mistakes / inconsistencies** found while running the Day-2
experiment (300 synthetic resumes through the Affinda Sandbox, schema v1.0). These are
**separate** from the ResumeGuard "missing qualifier field" gaps (completion status /
validity / claim-strength), which are arguably by-design feature gaps. Everything here
is a case where the parser dropped, truncated, invented, or misfiled a value — the kind
of thing a parser team would treat as a bug. Every ID below is reproducible from the
saved responses in `*/results/`.*

**Honesty note:** synthetic resumes, each parsed once; these are reproducible signals
on these inputs, not measured production rates.

---

## DEFECT 1 — Mid-tier skills extracted inconsistently (salience-sensitive) ⭐ found by review

**What:** Common-but-not-top skills (**Azure, Tableau, Spark**) are extracted
unreliably and depend on surrounding wording, where top-tier skills (Python, Java, SQL,
AWS, Kubernetes, Docker, React, Go, TypeScript) are extracted almost every time in the
same contexts.

**Evidence (present-in-output rate, same 100-resume set):**

| Skill | extracted | | Skill | extracted |
|---|:--:|---|---|:--:|
| Python | 9/9 | | **Spark** | **6/8** |
| Java | 9/9 | | **Tableau** | **4/8** |
| SQL | 9/9 | | **Azure** | **3/8** |
| AWS | 9/9 | | Kubernetes | 8/8 |
| React / Go / TypeScript / Docker | 8/8 | | | |

**The sharp cases (not placement, not a missing word in the PDF):**
- `S041` — **"Exposure to Azure"** in a plain **SKILLS list** → Azure **not extracted**.
  "Azure" is present in `rawText`. Parsed skills: Agile, Computer Science, Git, Linux,
  production systems — no Azure.
- `S046` — **"Brief exposure to Tableau"** in a plain SKILLS list → Tableau **not
  extracted** (present in `rawText`).
- `S005` — **"8+ years of Azure"** (an explicit expert-level claim) → Azure **dropped**,
  while the identical `"8+ years of Java"` elsewhere is kept.
- `S010` — **"Strong Tableau experience"** → Tableau dropped.

**Why it looks like a threshold/confidence issue:** the same skill is extracted fine in
other phrasings (`"Solid Spark"`, `"Working knowledge of Azure"`, `"Basic Tableau"`),
so it isn't "Azure is unknown." It's that for these lower-salience skills, surrounding
tokens ("exposure to", "8+ years of", "strong … experience") seem to push span/confidence
below a threshold and the skill is discarded — behaviour top-tier skills don't show.

**Severity:** medium-high. A candidate with real Azure/Tableau/Spark experience silently
drops out of boolean/skills search. **Not fixable by our enrichment layer** — the skill
is absent from the JSON before we run, so we can only *flag* a likely-missing skill by
scanning `rawText`.

---

## DEFECT 2 — A whole named credential is never extracted ("Bar admission")

**What:** "Bar admission" (a real, licensable legal credential) is **dropped entirely**
in **every** context tried — 7/7 — while the sibling certification in the same resume
category is extracted fine.

**Evidence:** `C010` (recertified), `C022` (expired), `C034` (revoked), `C046`
(suspended), `C058` (pending), `C070` (valid until 2027), `C082` (plain) — in all seven
the `certifications` array comes back **without** any Bar-admission entry. Every other
non-extraction in the 100-cert set is also "Bar admission"; no other cert name was
dropped.

**Severity:** medium. Entire credential missing, not just its status. **Not enrichable**
(nothing in the output to annotate). Looks like a gap in the certification name
vocabulary.

---

## DEFECT 3 — Terminal "left/withdrew" year emitted as a conferral end date

**What:** When a degree line gives a year tied to **leaving or withdrawing**, the parser
puts that year in `education[].dateRange.end` — the same field a *graduation* date uses —
so an unfinished degree is structurally indistinguishable from a conferred one.

**Evidence:**
- `E053` — "Juris Doctor (JD), Lakeside College — **withdrawn 2020**" → `end.date =
  2020-01-01`. Reads as conferred 2020.
- Systematic: **9/9** extracted "withdrawn <year>" degrees and **2/12** "incomplete"
  degrees emit the year as an `end` date. (Related, more arguable: **11/11** "expected
  <future year>" degrees emit the *future* year as `end`, e.g. "expected 2029" →
  `end 2029`, which reads as a future graduation.)

**Severity:** medium. This is a *wrong value*, not just a missing field — the end date is
asserted. (Our enrichment can add a `completionStatus`, but the misleading `end` date
stays unless the parser changes it.) Mirrors the open-ended-employment-date issue from
earlier rounds (a date gets invented/implied where none was stated).

---

## DEFECT 4 — Qualification string truncation + level mis-tag

**What:** `E053` "Juris Doctor (JD)" is returned as **`"Juris Doctor (JD"`** — the
closing `)` is dropped — and `level` is tagged **`master`** for a JD (a doctoral-level
professional degree).

**Caveat (from the API docs):** Affinda's *own* published sample response shows the same
kind of truncation — `"qualification": "Bachelor of"`. So partial-qualification strings
look like a known/common parser behaviour, not a one-off. The **level mis-tag** (JD →
`master`) is the firmer half of this one.

**Severity:** low. Cosmetic truncation (apparently common) + a level-classification miss.

---

## NOT A DEFECT — Certificate/VET-level quals appear under `certifications`, not `education`

Earlier logged as a defect; **withdrawn after reading the API docs.** The contract states:
*"An education entry whose level is a course, a certificate or a conference is re-emitted
as a certifications entry. Read certifications for them rather than filtering education
yourself."* So "Certificate IV in Cybersecurity" landing in `certifications` with an
empty `education` is **documented, intended behaviour** (`E020/E040/E060`, ~9 cases).

*Implication for us (not for Affinda):* our education module **must also read
`certifications`**, because certificate-level quals legitimately live there.

---

## Summary for Affinda

| # | Defect | Reproducible IDs | Type | Enrichable? |
|---|---|---|---|---|
| 1 | Mid-tier skills (Azure/Tableau/Spark) dropped inconsistently | S005, S010, S041, S046 (+rate table) | drop / threshold | flag only |
| 2 | "Bar admission" credential never extracted | C010/C022/C034/C046/C058/C070/C082 | drop | no |
| 3 | "withdrawn <year>" emitted as conferral `end` date | E053 (+9/9 withdrawn) | wrong value | partial |
| 4 | "Juris Doctor (JD)" truncated + tagged `master` (truncation looks common per docs) | E053 | truncation / mis-tag | no |

*Defects 1 and 2 are closest to "silently drops a real entry." 3 is a wrong asserted
value. The former "Defect 5" (certificate quals in `certifications`) was **documented
behaviour** and removed. This log will be appended if more are found.*

---

## Does the documented schema already provide our three enrichments? (checked against the v1 contract)

**No.** The published `data` field list for each object has no slot for any of them, and
the docs state the key set is fixed and absent = not-found (so these aren't just empty on
our inputs — the keys don't exist):

| Our field | Documented object fields | Overlap |
|---|---|---|
| education `completionStatus` | institution, qualification, level, fieldsOfStudy, minors, grade, dateRange, location | none (`grade` = award/GPA) |
| certification `validityStatus` | name, issuer, date | none |
| skill `claimStrength` / `denied` | text, name, sources, taxonomy{affindaId,isLanguage,isSoftware,type} | none (live data also exposes `experienceMonths`/`lastUsed` = recency/duration, not proficiency or negation) |

The enrichment layer is not duplicated by the documented parser. Adjacent fields that
*do* exist and we should consume rather than recompute: `meta.extractionQuality.band`,
`meta.document.warnings`, `meta.ocr.truncated` (routing signals), `employmentMetrics`
(for the Problem-D date work), and `workAuthorization` (a V2 idea, already present).
