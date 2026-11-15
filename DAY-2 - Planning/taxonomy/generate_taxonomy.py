#!/usr/bin/env python3
"""
Generate the 100-variation test taxonomy for the three ResumeGuard V1 issues:
  1. Education completion status   -> education_status_100.csv
  2. Certification status          -> certification_status_100.csv
  3. Skill claim strength          -> skill_claim_strength_100.csv

Deterministic. Each CSV has exactly 100 rows. One controlled variable per row where
possible; positive controls and false-positive distractors are included on purpose.
No PDFs are built here — this only produces the test matrix (the manifest a later
generator would consume). Run:  python generate_taxonomy.py
"""
import csv, os, itertools

HERE = os.path.dirname(os.path.abspath(__file__))

DEGREES = [
    ("Bachelor of Science in Computer Science", "bachelor"),
    ("Master of Engineering", "master"),
    ("Juris Doctor (JD)", "doctorate-prof"),
    ("Doctor of Medicine (MD)", "doctorate-prof"),
    ("PhD in Chemistry", "doctorate"),
    ("Associate of Arts", "associate"),
    ("MBA", "master"),
    ("Bachelor of Nursing", "bachelor"),
    ("Diploma in Accounting", "diploma"),
    ("Certificate IV in Cybersecurity", "certificate"),
]
INSTITUTIONS = ["Riverside University", "Northgate Institute", "Lakeside College",
                "Summit State University", "Harbour Polytechnic"]
PAST = [2018, 2019, 2020, 2021, 2022]
FUTURE = [2027, 2028, 2029]
LAYOUTS = ["flow", "bulleted", "table", "two_column"]

CERTS = [
    ("AWS Certified Solutions Architect", "cloud"),
    ("PMP", "project-mgmt"),
    ("CISSP", "security"),
    ("Registered Nurse (RN) license", "healthcare-regulated"),
    ("CPA", "finance-regulated"),
    ("Medical license", "healthcare-regulated"),
    ("Forklift operator licence", "trade"),
    ("Security Clearance (Baseline)", "government"),
    ("CPR / First Aid certification", "safety"),
    ("Bar admission", "legal-regulated"),
    ("CCNA", "networking"),
    ("Six Sigma Black Belt", "quality"),
]
SKILLS = ["Python", "Java", "SQL", "AWS", "Azure", "Kubernetes", "Docker",
          "React", "Go", "Tableau", "Spark", "TypeScript"]
SKILL_LOCATIONS = ["skills_list", "summary_prose", "experience_bullet",
                   "proficiency_table", "parenthetical"]


def cyc(seq):
    while True:
        for x in seq:
            yield x


# --------------------------------------------------------------------------- #
# 1. EDUCATION COMPLETION STATUS
# --------------------------------------------------------------------------- #
def education_rows():
    # (category, [phrasing templates], date_type, expected_status, realism)
    # placeholders: {deg} {inst} {y} past year, {fy} future year, {sy} start year
    blocks = [
        ("completed", 10, "past", "completed", "very common", [
            "{deg}, {inst}, {y}",
            "{deg} — {inst} (graduated {y})",
            "{deg}, {inst}, conferred {y}",
            "{deg} ({y}), {inst}",
        ]),
        ("in_progress", 16, "none_or_present", "in_progress", "very common", [
            "{deg}, {inst} — currently enrolled",
            "{deg} (in progress), {inst}",
            "Pursuing {deg}, {inst}",
            "{deg}, {inst}, {sy}–present",
            "Candidate for {deg}, {inst}",
            "Studying towards {deg}, {inst}",
            "{deg}, {inst} — ongoing",
            "Currently completing {deg}, {inst}",
        ]),
        ("expected", 12, "future", "expected", "very common", [
            "{deg}, {inst} — expected {fy}",
            "{deg}, {inst}, anticipated graduation {fy}",
            "{deg} — expected completion {fy}, {inst}",
            "{deg}, {inst} (graduating {fy})",
            "{deg}, {inst} — due {fy}",
        ]),
        ("incomplete_discontinued", 14, "past", "incomplete", "occasional", [
            "{deg}, {inst} — discontinued before completion",
            "{deg} (incomplete), {inst}",
            "{deg}, {inst} — did not complete",
            "{deg}, {inst}, left before finishing ({y})",
            "Partial {deg}, {inst}",
            "{deg}, {inst} — unfinished",
        ]),
        ("withdrawn", 10, "past", "withdrawn", "occasional", [
            "{deg}, {inst} — withdrawn {y}",
            "{deg}, {inst} — withdrew {y}",
            "{deg}, {inst}, left the program {y}",
            "{deg} (withdrawn {y}), {inst}",
        ]),
        ("not_awarded", 12, "past", "not_awarded", "occasional", [
            "{deg}, {inst} — coursework completed, qualification not awarded",
            "{deg}, {inst} — attended, no degree conferred",
            "{deg}, {inst}, requirements not met ({y})",
            "{deg} — {inst}, exams not passed",
        ]),
        ("deferred_leave", 8, "none_or_present", "deferred", "rare", [
            "{deg}, {inst} — deferred",
            "{deg}, {inst} — on academic leave",
            "{deg}, {inst} — study break since {sy}",
            "{deg}, {inst} (enrolment suspended)",
        ]),
        ("abd_partial", 8, "none_or_present", "in_progress", "rare", [
            "{deg} (ABD — all but dissertation), {inst}",
            "{deg}, {inst} — comprehensive exams passed, dissertation pending",
            "{deg}, {inst} — coursework complete, thesis pending",
            "{deg} — {inst}, candidate (ABD)",
        ]),
        ("unknown_no_signal", 4, "none", "unknown", "common", [
            "{deg}, {inst}",
            "{deg} — {inst}",
        ]),
    ]
    rows = []
    deg = cyc(DEGREES); inst = cyc(INSTITUTIONS); lay = cyc(LAYOUTS)
    py = cyc(PAST); fy = cyc(FUTURE); sy = cyc(PAST)
    n = 0
    for cat, count, date_type, exp_status, realism, templates in blocks:
        tp = cyc(templates)
        for _ in range(count):
            n += 1
            d, level = next(deg)
            line = next(tp).format(deg=d, inst=next(inst), y=next(py),
                                   fy=next(fy), sy=next(sy))
            if date_type == "past":
                date_in = "past terminal year present"
                fail = ("status absent AND the terminal year is emitted as a "
                        "conferral-style end date (looks completed)")
                exp_date = "year must NOT read as a conferral date"
            elif date_type == "future":
                date_in = "future year present"
                fail = ("future year emitted as a conferral end date (looks "
                        "graduated); no in-progress/expected status")
                exp_date = "date flagged expected, not conferred"
            elif date_type == "none":
                date_in = "no date"
                fail = "entry dropped, or silently marked completed"
                exp_date = "no conferral date invented"
            else:
                date_in = "no terminal year / 'present'"
                fail = ("marked completed, or a conferral date invented, or "
                        "entry dropped")
                exp_date = "current/ongoing; no conferral date invented"
            rows.append(dict(
                test_id=f"E{n:03d}", issue="education_status",
                status_category=cat, phrasing=line.split(" — ")[-1][:40],
                exact_source_line=line, qualification=d, level=level,
                date_in_text=date_in, layout=next(lay), is_control=(cat == "completed"),
                paired_with="", expected_completion_status=exp_status,
                expected_date_handling=exp_date, failure_if=fail,
                realism=realism, notes=""))
    # multi-entry block (6): one completed + one in-progress in the SAME resume
    for i in range(6):
        n += 1
        d1, l1 = DEGREES[i % len(DEGREES)]
        d2, l2 = DEGREES[(i + 3) % len(DEGREES)]
        line = (f"{d1}, {next(inst)}, {PAST[i % len(PAST)]}  ||  "
                f"{d2}, {next(inst)} — currently enrolled")
        rows.append(dict(
            test_id=f"E{n:03d}", issue="education_status",
            status_category="multi_entry", phrasing="completed + in_progress",
            exact_source_line=line, qualification=f"{d1} + {d2}", level=f"{l1}+{l2}",
            date_in_text="one past year + one none", layout=LAYOUTS[i % len(LAYOUTS)],
            is_control=False, paired_with="",
            expected_completion_status="completed + in_progress (distinct)",
            expected_date_handling="only the completed one gets a conferral date",
            failure_if="the in-progress entry is shown completed, or either is dropped",
            realism="common", notes="tests per-entry status, not whole-section"))
    assert len(rows) == 100, len(rows)
    return rows


# --------------------------------------------------------------------------- #
# 2. CERTIFICATION STATUS
# --------------------------------------------------------------------------- #
def certification_rows():
    blocks = [
        ("active", 8, "active", "very common", "held; status must read active", [
            "{c} — active, valid through {fy}",
            "{c} (current)",
            "{c} — in good standing",
        ]),
        ("renewed", 6, "active", "common", "held; status active", [
            "{c} — renewed {y} (current)",
            "{c}, recertified {y}",
        ]),
        ("expired", 16, "expired", "very common", "held-but-invalid; must read expired", [
            "{c} — expired {y}",
            "{c}, lapsed {y}",
            "{c} — no longer valid",
            "{c} (expired)",
            "{c} — expired, renewal pending",
        ]),
        ("revoked", 12, "revoked", "rare", "held-but-invalid; must read revoked", [
            "{c} — revoked {y}",
            "{c} — licence revoked",
            "{c} — withdrawn by issuer",
        ]),
        ("suspended", 8, "suspended", "rare", "held-but-invalid; must read suspended", [
            "{c} — temporarily suspended",
            "{c} (under suspension)",
        ]),
        ("pending_scheduled", 10, "pending", "occasional", "not yet held; omit OR flag pending", [
            "{c} — exam scheduled {fy}",
            "{c} (pending)",
            "{c} — awaiting results",
            "Candidate, {c}",
        ]),
        ("failed", 6, "failed", "occasional", "not held; omit OR flag not-held (defensible)", [
            "{c} — attempted, did not pass",
            "{c}, unsuccessful attempt {y}",
        ]),
        ("expires_future_valid", 10, "active", "common", "held & valid now; expiry in future", [
            "{c} — valid until {fy}",
            "{c}, expires {fy}",
            "{c} — current, expires {fy}",
        ]),
        ("no_status", 8, "unknown", "common", "held; name+date only, no status word", [
            "{c} — {y}",
            "{c}",
        ]),
        ("held_out_formats", 8, "mixed", "common", "generalisation: unusual date/status forms", [
            "{c} — valid {y}–{fy}",
            "{c} (caducado {y})",          # expired, non-English
            "{c} — exp. {y}",              # abbreviation
            "{c}: status inactive",
        ]),
    ]
    rows = []
    c = cyc(CERTS); lay = cyc(LAYOUTS); py = cyc(PAST); fy = cyc(FUTURE)
    n = 0
    for cat, count, exp_status, realism, expectation, templates in blocks:
        tp = cyc(templates)
        for _ in range(count):
            n += 1
            name, domain = next(c)
            line = next(tp).format(c=name, y=next(py), fy=next(fy))
            if cat in ("expired", "revoked", "suspended"):
                fail = ("status absent — the invalid cert is indistinguishable "
                        "from a valid one (name+date only)")
                exp_extract = "cert extracted; status label present"
            elif cat in ("pending_scheduled", "failed"):
                fail = ("treated as a held credential (no not-held signal); OR "
                        "wrongly surfaced in 'has {cert}' matches")
                exp_extract = "omit OR include flagged not-held (both acceptable)"
            elif cat == "no_status":
                fail = "cert dropped, or date misread as validity"
                exp_extract = "cert extracted with name + date"
            elif cat == "held_out_formats":
                fail = "status/validity lost because the form is unusual (format brittleness)"
                exp_extract = "cert extracted; validity parsed from the unusual form"
            else:  # active / renewed / expires_future / suspended-fallthrough
                fail = "valid cert dropped, or shown as expired"
                exp_extract = "cert extracted with name + date; reads valid"
            rows.append(dict(
                test_id=f"C{n:03d}", issue="certification_status",
                validity_category=cat, phrasing=line,
                exact_source_line=line, cert_name=name, cert_domain=domain,
                date_in_text=("future" if cat in ("active", "expires_future_valid", "pending_scheduled")
                              else "past" if cat in ("expired", "revoked", "renewed", "failed", "no_status")
                              else "none"),
                layout=next(lay), is_control=(cat in ("active", "renewed", "expires_future_valid")),
                paired_with="", expected_validity_status=exp_status,
                expected_extraction=exp_extract, failure_if=fail,
                realism=realism, notes=""))
    # multi/mixed block (8): active + expired of the SAME cert in one resume
    for i in range(8):
        n += 1
        name, domain = CERTS[i % len(CERTS)]
        line = f"{name} — active (renewed {FUTURE[i % len(FUTURE)]})  ||  {name} — expired {PAST[i % len(PAST)]}"
        rows.append(dict(
            test_id=f"C{n:03d}", issue="certification_status",
            validity_category="multi_mixed", phrasing="active + expired same cert",
            exact_source_line=line, cert_name=name, cert_domain=domain,
            date_in_text="future + past", layout=LAYOUTS[i % len(LAYOUTS)],
            is_control=False, paired_with="",
            expected_validity_status="active + expired (distinct)",
            expected_extraction="both kept, distinguished by status",
            failure_if="collapsed to one, or valid one dropped, or statuses swapped/absent",
            realism="occasional", notes="the R340-style pairing, now understood"))
    assert len(rows) == 100, len(rows)
    return rows


# --------------------------------------------------------------------------- #
# 3. SKILL CLAIM STRENGTH
# --------------------------------------------------------------------------- #
def skill_rows():
    # (category, count, [templates], expected_strength, expected_behaviour, realism)
    blocks = [
        ("expert", 8, ["Expert in {s}", "8+ years of {s}", "Advanced {s}"],
         "strong", "extract (optionally tag strong)", "very common", False),
        ("proficient", 8, ["Proficient in {s}", "Strong {s} experience", "Solid {s}"],
         "strong", "extract (optionally tag strong)", "very common", False),
        ("working", 8, ["Working knowledge of {s}", "Hands-on {s}", "Comfortable with {s}"],
         "moderate", "extract, tag moderate", "common", False),
        ("basic", 10, ["Basic {s}", "Familiar with {s}", "Some {s}"],
         "weak", "extract, tag weak", "very common", False),
        ("exposure", 12, ["Exposure to {s}", "Limited exposure to {s}", "Brief exposure to {s}"],
         "weak", "extract, tag weak/low", "very common", False),
        ("learning", 10, ["Currently learning {s}", "Studying {s}", "Learning {s} in my spare time"],
         "aspirational", "extract, tag aspirational (not possessed)", "common", False),
        ("theoretical", 6, ["Theoretical knowledge of {s}, no practical experience",
                            "Academic {s} only, no production use"],
         "aspirational", "extract, tag theoretical", "common", False),
        ("historical", 8, ["Previously used {s}, not in recent years",
                           "Used {s} years ago", "Formerly worked with {s}"],
         "lapsed", "extract, tag lapsed/historical", "common", False),
        ("denied", 10, ["No experience with {s}", "Not proficient in {s}",
                        "{s}: none", "Without any {s} background"],
         "denied", "suppress OR tag denied (must NOT list as possessed)", "rare", False),
        ("scoped_exclusion", 8, ["{s}, but not {s2}", "{s} (not {s2})",
                                 "Experienced in {s}; never used {s2}"],
         "mixed", "keep {s}; suppress/deny {s2}", "occasional", False),
        ("interest", 4, ["Interested in {s}", "Keen to learn {s}"],
         "aspirational", "extract, tag interest (not possessed)", "occasional", False),
        ("cert_vs_use", 2, ["Not certified in {s}, but use {s} daily"],
         "strong", "{s} kept as possessed (cert denial != skill denial)", "occasional", False),
        ("distractor_fp_trap", 6, ["No experience with {s2}; expert in {s}",
                                   "Migrated away from {s2} to {s}",
                                   "Replaced {s2} with {s} across the stack"],
         "trap", "keep {s} (affirmed); suppress/deny {s2}", "occasional", True),
    ]
    rows = []
    sk = cyc(SKILLS); sk2 = cyc(list(reversed(SKILLS))); loc = cyc(SKILL_LOCATIONS)
    n = 0
    for cat, count, templates, exp_strength, exp_beh, realism, is_distr in blocks:
        tp = cyc(templates)
        for _ in range(count):
            n += 1
            s = next(sk); s2 = next(sk2)
            if s2 == s:
                s2 = next(sk2)
            line = next(tp).format(s=s, s2=s2)
            if cat == "denied":
                fail = f"'{s}' extracted as a plain possessed skill with no negative marker"
            elif cat in ("exposure", "learning", "theoretical", "basic", "interest", "historical"):
                fail = f"'{s}' extracted identical to an expert-level claim (no strength signal)"
            elif cat == "scoped_exclusion":
                fail = f"'{s2}' extracted as possessed, and/or '{s}' wrongly dropped"
            elif cat == "distractor_fp_trap":
                fail = f"'{s}' (affirmed) wrongly suppressed, OR '{s2}' (denied) extracted as possessed"
            elif cat == "cert_vs_use":
                fail = f"'{s}' suppressed because of the certification denial"
            else:
                fail = f"'{s}' missing from skills (should be present)"
            rows.append(dict(
                test_id=f"S{n:03d}", issue="skill_claim_strength",
                claim_strength=cat, phrasing=line, skill=s,
                secondary_skill=(s2 if cat in ("scoped_exclusion", "distractor_fp_trap") else ""),
                exact_source_line=line, location=next(loc),
                is_control=(cat in ("expert", "proficient")), is_distractor=is_distr,
                expected_strength=exp_strength,
                expected_behaviour=exp_beh.format(s=s, s2=s2),
                failure_if=fail, realism=realism, notes=""))
    assert len(rows) == 100, len(rows)
    return rows


def write(path, rows):
    cols = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    e = education_rows(); c = certification_rows(); s = skill_rows()
    ne = write(os.path.join(HERE, "education_status_100.csv"), e)
    nc = write(os.path.join(HERE, "certification_status_100.csv"), c)
    ns = write(os.path.join(HERE, "skill_claim_strength_100.csv"), s)
    print(f"education={ne}  certification={nc}  skill={ns}")
    # quick category distribution report
    from collections import Counter
    for name, rows, key in [("EDU", e, "status_category"),
                            ("CERT", c, "validity_category"),
                            ("SKILL", s, "claim_strength")]:
        print(name, dict(Counter(r[key] for r in rows)))
