"""
targeted_candidates.py — Single source of truth for the 45 targeted probe resumes
(T01-T45) investigating three confirmed Affinda weaknesses:

  Phase 1  T01-T15  Ongoing-employment date expressions      (controlled: date wording / layout)
  Phase 2  T16-T30  Employer attribution for non-standard work (controlled: employer label / order / layout)
  Phase 3  T31-T45  Education completion status               (controlled: status wording / layout)

Design rule: within each phase, everything is held fixed EXCEPT the controlled
variable, so any behaviour change is attributable to that variable. Ground truth
(expectations, acceptable alternates, confirmed-failure / inconclusive criteria)
is defined here from the synthetic source, never from PDF extraction.

Each test dict:
  id, phase, layout, controlled, source_evidence,
  name,title,email,phone,location,links,summary,
  experience=[{title,org,location,date_display,bullets}],
  education=[{degree,institution,location,date_display,note}],
  skills=[...],
  expected={...}, acceptable=[...], confirmed_failure_if=str, inconclusive_if=str,
  expected_pages=int
"""
from __future__ import annotations


def _exp(title, org, location, date_display, bullets):
    return {"title": title, "org": org, "location": location,
            "date_display": date_display, "bullets": bullets}


def _edu(degree, institution, location, date_display, note=""):
    return {"degree": degree, "institution": institution, "location": location,
            "date_display": date_display, "note": note}


# ============================================================================ #
#  PHASE 1 — Ongoing employment dates (T01-T15)
# ============================================================================ #
_P1_PRIOR = _exp("Systems Administrator", "Borough Systems", "San Francisco, CA",
                 "Feb 2018 – Sep 2021",
                 ["Administered Linux fleets and on-call rotations.",
                  "Automated patching across 120 servers."])
_P1_EDU = [_edu("B.Eng. in Software Engineering", "University of Manchester",
                "Manchester, UK", "2013 – 2017")]
_P1_SKILLS = ["Docker", "Kubernetes", "Terraform", "AWS", "CI/CD", "Linux", "Python"]
_P1_BULLETS = ["Maintain CI/CD across 40+ repositories.",
               "Own infrastructure-as-code for the platform team.",
               "Lead incident response and postmortems."]


def _p1(tid, date_display, controlled, expected, acceptable, fail_if, inconc,
        layout="flow", extra_roles=None):
    exp = [_exp("DevOps Engineer", "Thamesworks Cloud", "San Francisco, CA",
                date_display, _P1_BULLETS)]
    if extra_roles:
        exp += extra_roles
    exp.append(_P1_PRIOR)
    return {
        "id": tid, "phase": 1, "layout": layout, "controlled": controlled,
        "source_evidence": f'DevOps Engineer — Thamesworks Cloud, "{date_display}"',
        "name": "Jordan Avery", "title": "DevOps Engineer",
        "email": "jordan.avery@examplemail.com", "phone": "+1 (415) 555-0110",
        "location": "San Francisco, CA",
        "links": {"LinkedIn": "linkedin.com/in/jordanavery"},
        "summary": "DevOps engineer focused on reliable delivery pipelines and "
                   "infrastructure-as-code.",
        "experience": exp, "education": _P1_EDU, "skills": _P1_SKILLS,
        "expected": expected, "acceptable": acceptable,
        "confirmed_failure_if": fail_if, "inconclusive_if": inconc,
        "expected_pages": 1,
    }


_CURRENT_EXPECT = {"start_iso": "2021-10", "end": "null", "current": True}
_CURRENT_ACCEPT = ["current=true with no end date", "endDate null / ongoing"]
_CURRENT_FAIL = ("a concrete end date is invented (e.g. end == start, or any "
                 "end date despite an explicit current-employment keyword)")
_CURRENT_INCONC = "current flag absent but end date also left null/absent"

PHASE1 = [
    _p1("T01", "October 2021 – Present", "explicit 'Present'",
        _CURRENT_EXPECT, _CURRENT_ACCEPT, _CURRENT_FAIL, _CURRENT_INCONC),
    _p1("T02", "Oct 2021 – Current", "explicit 'Current'",
        _CURRENT_EXPECT, _CURRENT_ACCEPT, _CURRENT_FAIL, _CURRENT_INCONC),
    _p1("T03", "October 2021 –", "open-ended dash, NO keyword (ambiguous)",
        {"start_iso": "2021-10", "end": "unknown", "current": "unknown"},
        ["current=true", "endDate null / unknown (ideal for an open-ended date)"],
        "a specific end date is invented (e.g. end == start month)",
        "end left unknown/null AND current not set — acceptable, not a failure"),
    _p1("T04", "Oct 2021 to date", "'to date' idiom",
        _CURRENT_EXPECT, _CURRENT_ACCEPT, _CURRENT_FAIL, _CURRENT_INCONC),
    _p1("T05", "Since October 2021", "'Since' prefix, no range",
        _CURRENT_EXPECT, _CURRENT_ACCEPT, _CURRENT_FAIL, _CURRENT_INCONC),
    _p1("T06", "2021 – Present", "year-only start + 'Present'",
        {"start_iso": "2021", "end": "null", "current": True},
        ["current=true, start year precision 2021"],
        "end date invented despite 'Present'",
        "current absent and end null"),
    _p1("T07", "Oct 2021 – Ongoing", "'Ongoing' keyword",
        _CURRENT_EXPECT, _CURRENT_ACCEPT, _CURRENT_FAIL, _CURRENT_INCONC),
    _p1("T08", "October 2021 onwards", "'onwards' keyword",
        _CURRENT_EXPECT, _CURRENT_ACCEPT, _CURRENT_FAIL, _CURRENT_INCONC),
    _p1("T09", "Started October 2021; currently employed",
        "prose 'currently employed'",
        _CURRENT_EXPECT, _CURRENT_ACCEPT, _CURRENT_FAIL, _CURRENT_INCONC),
    _p1("T10", "October 2021 – Now", "'Now' keyword",
        _CURRENT_EXPECT, _CURRENT_ACCEPT, _CURRENT_FAIL, _CURRENT_INCONC),
    _p1("T11", "October 2021 – October 2024", "COMPLETED control (explicit end)",
        {"start_iso": "2021-10", "end": "2024-10", "current": False},
        ["end 2024-10, current false"],
        "end date wrong (not 2024-10) or current=true",
        "n/a"),
    _p1("T12", "October 2021", "single date only (ambiguous)",
        {"start_iso": "2021-10", "end": "unknown", "current": "unknown"},
        ["endDate unknown/null", "role treated as single-point or ongoing"],
        "a second (end) date is invented",
        "end left unknown — acceptable, not a failure"),
    _p1("T13", "Oct 2021 – Present", "clear current INSIDE two-column layout",
        _CURRENT_EXPECT, _CURRENT_ACCEPT, _CURRENT_FAIL, _CURRENT_INCONC,
        layout="two-column"),
    _p1("T14", "Oct 2021 – Present", "clear current INSIDE employment table",
        _CURRENT_EXPECT, _CURRENT_ACCEPT, _CURRENT_FAIL, _CURRENT_INCONC,
        layout="table"),
    _p1("T15", "Oct 2021 – Present", "clear current WITH a second overlapping role",
        _CURRENT_EXPECT, _CURRENT_ACCEPT,
        "either current role gets an invented end date, or the two roles are merged",
        "current absent on either role",
        layout="flow",
        extra_roles=[_exp("Platform Engineer (Part-Time)", "Cirrus Labs",
                          "Remote", "Jan 2022 – Present",
                          ["Part-time platform work, concurrent with the main role."])]),
]


# ============================================================================ #
#  PHASE 2 — Employer attribution (T16-T30)
# ============================================================================ #
_P2_EDU = [_edu("B.F.A. in Design", "California College of the Arts",
                "San Francisco, CA", "2012 – 2016")]
_P2_SKILLS = ["Branding", "Illustration", "Figma", "Art Direction", "Typography"]


def _p2(tid, controlled, experience, expected_roles, acceptable, fail_if,
        layout="flow", source=""):
    return {
        "id": tid, "phase": 2, "layout": layout, "controlled": controlled,
        "source_evidence": source or controlled,
        "name": "Riley Chen", "title": "Designer",
        "email": "riley.chen@examplemail.com", "phone": "+1 (646) 555-0123",
        "location": "Brooklyn, NY", "links": {"Portfolio": "rileychen.example.com"},
        "summary": "Designer and illustrator across brand, editorial and product work.",
        "experience": experience, "education": _P2_EDU, "skills": _P2_SKILLS,
        "expected": {"roles": expected_roles}, "acceptable": acceptable,
        "confirmed_failure_if": fail_if,
        "inconclusive_if": "a role's employer is null/omitted where the source gives no employer",
        "expected_pages": 1,
    }


def _r(title, org, date_display, bullets, location="Brooklyn, NY"):
    return _exp(title, org, location, date_display, bullets)


_PERM = _r("Senior Designer", "Meadowlark Software", "Jan 2019 – Present",
           ["Lead brand and product design for a SaaS platform."])
_FREELANCE_BULLETS = ["Editorial and brand illustration for recurring clients."]

PHASE2 = [
    _p2("T16", "freelance labelled 'Self-Employed'",
        [_r("Freelance Illustrator", "Self-Employed", "2017 – Present", _FREELANCE_BULLETS)],
        [{"title": "Freelance Illustrator", "employer_expected": "Self-Employed",
          "employer_kind": "self_employment"}],
        ["employer = 'Self-Employed' / self-employment / null"],
        "a real company name is invented as the employer"),
    _p2("T17", "freelance labelled 'Independent'",
        [_r("Freelance Illustrator", "Independent", "2017 – Present", _FREELANCE_BULLETS)],
        [{"title": "Freelance Illustrator", "employer_expected": "Independent",
          "employer_kind": "self_employment"}],
        ["employer = 'Independent' / self-employment / null"],
        "a real company name is invented as the employer"),
    _p2("T18", "role labelled 'Independent Contractor'",
        [_r("Illustrator", "Independent Contractor", "2017 – Present", _FREELANCE_BULLETS)],
        [{"title": "Illustrator", "employer_expected": "Independent Contractor",
          "employer_kind": "self_employment"}],
        ["employer = 'Independent Contractor' / self-employment / null"],
        "a real company name is invented as the employer"),
    _p2("T19", "role labelled 'Sole Trader'",
        [_r("Illustrator", "Sole Trader", "2017 – Present", _FREELANCE_BULLETS)],
        [{"title": "Illustrator", "employer_expected": "Sole Trader",
          "employer_kind": "self_employment"}],
        ["employer = 'Sole Trader' / self-employment / null"],
        "a real company name is invented as the employer"),
    _p2("T20", "freelance role with NO employer line",
        [_r("Freelance Illustrator", "", "2017 – Present", _FREELANCE_BULLETS)],
        [{"title": "Freelance Illustrator", "employer_expected": None,
          "employer_kind": "unknown"}],
        ["employer null / unknown / 'Freelance'"],
        "an employer name is invented or borrowed from another record"),
    _p2("T21", "freelance ALONGSIDE permanent (perm first)",
        [_PERM, _r("Freelance Illustrator", "Self-Employed", "2017 – Present", _FREELANCE_BULLETS)],
        [{"title": "Senior Designer", "employer_expected": "Meadowlark Software", "employer_kind": "employer"},
         {"title": "Freelance Illustrator", "employer_expected": "Self-Employed", "employer_kind": "self_employment"}],
        ["freelance employer = Self-Employed/null; permanent = Meadowlark Software"],
        "the freelance role is attributed to 'Meadowlark Software' (employer bleed)"),
    _p2("T22", "freelance ABOVE permanent",
        [_r("Freelance Illustrator", "Self-Employed", "2017 – Present", _FREELANCE_BULLETS), _PERM],
        [{"title": "Freelance Illustrator", "employer_expected": "Self-Employed", "employer_kind": "self_employment"},
         {"title": "Senior Designer", "employer_expected": "Meadowlark Software", "employer_kind": "employer"}],
        ["freelance employer = Self-Employed/null; permanent = Meadowlark Software"],
        "the freelance role is attributed to 'Meadowlark Software' (employer bleed)"),
    _p2("T23", "freelance BELOW permanent",
        [_PERM, _r("Freelance Illustrator", "Self-Employed", "2017 – Dec 2018", _FREELANCE_BULLETS)],
        [{"title": "Senior Designer", "employer_expected": "Meadowlark Software", "employer_kind": "employer"},
         {"title": "Freelance Illustrator", "employer_expected": "Self-Employed", "employer_kind": "self_employment"}],
        ["freelance employer = Self-Employed/null; permanent = Meadowlark Software"],
        "the freelance role is attributed to 'Meadowlark Software' (employer bleed)"),
    _p2("T24", "two simultaneous PERMANENT employers",
        [_r("Senior Designer", "Meadowlark Software", "Jan 2019 – Present",
            ["Lead product design."]),
         _r("Design Lecturer (0.4 FTE)", "Pratt Institute", "Sep 2020 – Present",
            ["Teach an evening design course, concurrent with the design role."])],
        [{"title": "Senior Designer", "employer_expected": "Meadowlark Software", "employer_kind": "employer"},
         {"title": "Design Lecturer (0.4 FTE)", "employer_expected": "Pratt Institute", "employer_kind": "employer"}],
        ["both employers distinct and correctly attributed"],
        "the two employers are merged or swapped between roles"),
    _p2("T25", "consulting role with MULTIPLE CLIENTS",
        [_r("Design Consultant", "Self-Employed", "2018 – Present",
            ["Clients: Northwind Retail, Harbor Bank, Cedar Foods.",
             "Delivered brand systems and campaign design."])],
        [{"title": "Design Consultant", "employer_expected": "Self-Employed",
          "employer_kind": "self_employment",
          "clients_not_employer": ["Northwind Retail", "Harbor Bank", "Cedar Foods"]}],
        ["employer = Self-Employed/null; clients are NOT the employer"],
        "a client (e.g. 'Northwind Retail') is extracted as the employer"),
    _p2("T26", "self-employment listed as a BUSINESS NAME",
        [_r("Founder & Designer", "Chen Creative Studio", "2017 – Present",
            ["Sole-proprietor design studio; brand and editorial work."])],
        [{"title": "Founder & Designer", "employer_expected": "Chen Creative Studio",
          "employer_kind": "self_employment_business"}],
        ["employer = 'Chen Creative Studio' (a legitimate business-name employer)"],
        "the business name is dropped or replaced with another record's employer"),
    _p2("T27", "contract THROUGH A STAFFING AGENCY",
        [_r("Contract Designer (via TechStaff Inc.)", "TechStaff Inc.", "2019 – 2021",
            ["Placed at client Harbor Bank for a 2-year engagement."])],
        [{"title": "Contract Designer (via TechStaff Inc.)", "employer_expected": "TechStaff Inc.",
          "employer_kind": "staffing_agency", "client_not_employer": "Harbor Bank"}],
        ["employer = agency 'TechStaff Inc.' (acceptable) OR client 'Harbor Bank' (acceptable) — but consistent"],
        "employer and client are conflated inconsistently or a third org invented"),
    _p2("T28", "THREE concurrent employment records",
        [_r("Senior Designer", "Meadowlark Software", "Jan 2020 – Present", ["Product design."]),
         _r("Freelance Illustrator", "Self-Employed", "2018 – Present", _FREELANCE_BULLETS),
         _r("Design Mentor", "Hatch Collective", "Mar 2021 – Present", ["Mentor junior designers."])],
        [{"title": "Senior Designer", "employer_expected": "Meadowlark Software", "employer_kind": "employer"},
         {"title": "Freelance Illustrator", "employer_expected": "Self-Employed", "employer_kind": "self_employment"},
         {"title": "Design Mentor", "employer_expected": "Hatch Collective", "employer_kind": "employer"}],
        ["all three roles present with correct, distinct employers"],
        "any employer is copied across records or a role is dropped"),
    _p2("T29", "freelance + permanent in TWO-COLUMN layout",
        [_PERM, _r("Freelance Illustrator", "Self-Employed", "2017 – Present", _FREELANCE_BULLETS)],
        [{"title": "Senior Designer", "employer_expected": "Meadowlark Software", "employer_kind": "employer"},
         {"title": "Freelance Illustrator", "employer_expected": "Self-Employed", "employer_kind": "self_employment"}],
        ["freelance employer = Self-Employed/null; permanent = Meadowlark Software"],
        "the freelance role is attributed to 'Meadowlark Software' (employer bleed)",
        layout="two-column"),
    _p2("T30", "SAME records as T29 in SINGLE-COLUMN layout (paired control)",
        [_PERM, _r("Freelance Illustrator", "Self-Employed", "2017 – Present", _FREELANCE_BULLETS)],
        [{"title": "Senior Designer", "employer_expected": "Meadowlark Software", "employer_kind": "employer"},
         {"title": "Freelance Illustrator", "employer_expected": "Self-Employed", "employer_kind": "self_employment"}],
        ["freelance employer = Self-Employed/null; permanent = Meadowlark Software"],
        "the freelance role is attributed to 'Meadowlark Software' (employer bleed)",
        layout="flow"),
]


# ============================================================================ #
#  PHASE 3 — Education completion status (T31-T45)
# ============================================================================ #
_P3_EXP = [_exp("Analyst", "Keystone Group", "Chicago, IL", "2023 – Present",
                ["Business and data analysis for internal teams."])]
_P3_SKILLS = ["Research", "Data Analysis", "Writing", "Excel"]


def _p3(tid, controlled, education, expected_edu, acceptable, fail_if,
        layout="flow", source="", experience=None):
    return {
        "id": tid, "phase": 3, "layout": layout, "controlled": controlled,
        "source_evidence": source or controlled,
        "name": "Sam Taylor", "title": "Analyst",
        "email": "sam.taylor@examplemail.com", "phone": "+1 (312) 555-0164",
        "location": "Chicago, IL", "links": {},
        "summary": "Analyst with a research background; qualification status noted explicitly.",
        "experience": experience or _P3_EXP, "education": education, "skills": _P3_SKILLS,
        "expected": {"education": expected_edu}, "acceptable": acceptable,
        "confirmed_failure_if": fail_if,
        "inconclusive_if": "status absent from structured output but correct in rawText "
                           "(schema may lack a status field — record as 'status_absent')",
        "expected_pages": 1,
    }


# status categories: completed | in_progress | expected | discontinued | deferred | not_awarded | unknown
_MISLEAD_FAIL = ("a completion/award end date is emitted with NO status marker, so the "
                 "entry reads as a conferred qualification (misleading to a recruiter)")

PHASE3 = [
    _p3("T31", "completed (control)",
        [_edu("Bachelor of Science in Economics", "University of Illinois", "Urbana, IL",
              "2019 – 2023", "Completed 2023.")],
        [{"qualification": "Bachelor of Science in Economics", "status": "completed",
          "end_expected": "2023"}],
        ["recorded as completed, end 2023"],
        "shown as in-progress, or end date wrong"),
    _p3("T32", "currently studying",
        [_edu("Bachelor of Science in Economics", "University of Illinois", "Urbana, IL",
              "2022 – present", "Currently studying; degree not yet awarded.")],
        [{"qualification": "Bachelor of Science in Economics", "status": "in_progress",
          "end_expected": None}],
        ["status in-progress / no completion date", "status_absent (recoverable in rawText)"],
        _MISLEAD_FAIL),
    _p3("T33", "expected graduation 2027",
        [_edu("Bachelor of Science in Economics", "University of Illinois", "Urbana, IL",
              "2023 – 2027 (expected)", "Expected graduation 2027; in progress.")],
        [{"qualification": "Bachelor of Science in Economics", "status": "expected",
          "end_expected": "2027 (expected)"}],
        ["status expected/in-progress; 2027 marked as expected not conferred",
         "status_absent (recoverable in rawText)"],
        "end 2027 emitted as a conferred graduation date with no 'expected' marker"),
    _p3("T34", "master in progress",
        [_edu("Master of Engineering", "Northwestern University", "Evanston, IL",
              "2024 – present", "In progress.")],
        [{"qualification": "Master of Engineering", "status": "in_progress", "end_expected": None}],
        ["status in-progress / no completion date", "status_absent (recoverable in rawText)"],
        _MISLEAD_FAIL),
    _p3("T35", "master NOT completed",
        [_edu("Master of Engineering", "Northwestern University", "Evanston, IL",
              "2021 – 2023", "Not completed.")],
        [{"qualification": "Master of Engineering", "status": "discontinued", "end_expected": None}],
        ["status discontinued/not-completed/in-progress (NOT completed)",
         "status_absent (recoverable in rawText)"],
        "recorded as a completed master's with a conferral date"),
    _p3("T36", "J.D. incomplete",
        [_edu("Juris Doctor", "DePaul University College of Law", "Chicago, IL",
              "2021 – 2023", "Incomplete.")],
        [{"qualification": "Juris Doctor", "status": "discontinued", "end_expected": None}],
        ["status incomplete/discontinued/in-progress (NOT completed)",
         "status_absent (recoverable in rawText)"],
        "recorded as a completed J.D. with a conferral date"),
    _p3("T37", "J.D. expected completion 2027",
        [_edu("Juris Doctor", "DePaul University College of Law", "Chicago, IL",
              "2024 – 2027 (expected)", "Expected completion 2027.")],
        [{"qualification": "Juris Doctor", "status": "expected", "end_expected": "2027 (expected)"}],
        ["status expected/in-progress; 2027 marked expected not conferred",
         "status_absent (recoverable in rawText)"],
        "end 2027 emitted as a conferred J.D. date with no 'expected' marker"),
    _p3("T38", "PhD candidate, research ongoing",
        [_edu("PhD candidate in Chemistry", "University of Chicago", "Chicago, IL",
              "2021 – present", "Research ongoing; not yet awarded.")],
        [{"qualification": "PhD candidate in Chemistry", "status": "in_progress", "end_expected": None}],
        ["status in-progress / candidate; no award date", "status_absent (recoverable in rawText)"],
        "recorded as an awarded PhD with a completion date"),
    _p3("T39", "PhD awarded 2024 (control)",
        [_edu("PhD in Chemistry", "University of Chicago", "Chicago, IL",
              "2019 – 2024", "Awarded 2024.")],
        [{"qualification": "PhD in Chemistry", "status": "completed", "end_expected": "2024"}],
        ["recorded as completed/awarded, end 2024"],
        "shown as in-progress, or end date wrong"),
    _p3("T40", "withdrawn",
        [_edu("Bachelor of Commerce", "University of Michigan", "Ann Arbor, MI",
              "2018 – 2020", "Withdrawn.")],
        [{"qualification": "Bachelor of Commerce", "status": "discontinued", "end_expected": None}],
        ["status withdrawn/discontinued (NOT completed)", "status_absent (recoverable in rawText)"],
        "recorded as a completed degree with a conferral date"),
    _p3("T41", "deferred",
        [_edu("Bachelor of Commerce", "University of Michigan", "Ann Arbor, MI",
              "2022 – present", "Deferred.")],
        [{"qualification": "Bachelor of Commerce", "status": "deferred", "end_expected": None}],
        ["status deferred/paused/in-progress (NOT completed)", "status_absent (recoverable in rawText)"],
        "recorded as a completed degree with a conferral date"),
    _p3("T42", "coursework completed, qualification NOT awarded",
        [_edu("Diploma of Information Technology", "RMIT", "Melbourne, VIC",
              "2019 – 2020", "Coursework completed, qualification not awarded.")],
        [{"qualification": "Diploma of Information Technology", "status": "not_awarded", "end_expected": None}],
        ["status not-awarded/incomplete (NOT a conferred qualification)",
         "status_absent (recoverable in rawText)"],
        "recorded as an awarded diploma with a conferral date"),
    _p3("T43", "certificate currently enrolled",
        [_edu("Certificate IV in Cybersecurity", "TAFE NSW", "Sydney, NSW",
              "2024 – present", "Currently enrolled.")],
        [{"qualification": "Certificate IV in Cybersecurity", "status": "in_progress", "end_expected": None}],
        ["status in-progress/enrolled; no completion date", "status_absent (recoverable in rawText)"],
        _MISLEAD_FAIL),
    _p3("T44", "TWO qualifications: one completed + one in progress",
        [_edu("Bachelor of Science in Economics", "University of Illinois", "Urbana, IL",
              "2016 – 2020", "Completed 2020."),
         _edu("Master of Engineering", "Northwestern University", "Evanston, IL",
              "2023 – present", "In progress.")],
        [{"qualification": "Bachelor of Science in Economics", "status": "completed", "end_expected": "2020"},
         {"qualification": "Master of Engineering", "status": "in_progress", "end_expected": None}],
        ["BSc completed 2020; MEng in-progress with no completion date",
         "MEng status_absent (recoverable in rawText)"],
        "the in-progress MEng is recorded as completed with a conferral date"),
    _p3("T45", "SAME as T44 in a TABLE layout (paired control)",
        [_edu("Bachelor of Science in Economics", "University of Illinois", "Urbana, IL",
              "2016 – 2020", "Completed 2020."),
         _edu("Master of Engineering", "Northwestern University", "Evanston, IL",
              "2023 – present", "In progress.")],
        [{"qualification": "Bachelor of Science in Economics", "status": "completed", "end_expected": "2020"},
         {"qualification": "Master of Engineering", "status": "in_progress", "end_expected": None}],
        ["BSc completed 2020; MEng in-progress with no completion date",
         "MEng status_absent (recoverable in rawText)"],
        "the in-progress MEng is recorded as completed with a conferral date",
        layout="table"),
]


CANDIDATES = PHASE1 + PHASE2 + PHASE3
BY_ID = {c["id"]: c for c in CANDIDATES}


if __name__ == "__main__":
    assert len(CANDIDATES) == 45, f"expected 45, got {len(CANDIDATES)}"
    ids = [c["id"] for c in CANDIDATES]
    assert ids == [f"T{i:02d}" for i in range(1, 46)], "ids must be T01..T45 in order"
    for ph, (a, b) in {1: (1, 15), 2: (16, 30), 3: (31, 45)}.items():
        n = sum(1 for c in CANDIDATES if c["phase"] == ph)
        assert n == 15, f"phase {ph} has {n}"
    print(f"OK: {len(CANDIDATES)} tests, 15 per phase, IDs T01..T45")
