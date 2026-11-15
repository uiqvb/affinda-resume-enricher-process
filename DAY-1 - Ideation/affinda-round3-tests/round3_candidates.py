"""
round3_candidates.py — 48 synthetic probe resumes (R301-R348) for third-round gap
discovery. Six categories, 8 each, each isolating ONE semantic variable and
deliberately NOT duplicating the two existing project ideas (hidden-text integrity;
education-status / employment-date verification).

Categories:
  R301-R308  Negated skills       (claimed vs explicitly denied experience)
  R309-R316  Work authorisation   (citizen / PR / sponsorship / expired / unknown / ambiguous)
  R317-R324  Skill ownership      (personal expertise vs managing people who have it)
  R325-R332  Experience duration  (approx / part-time / overlap / gap / explicit claim)
  R333-R340  Certification status (active / expired / pending / failed / revoked / training-only / not-awarded)
  R341-R348  Employment type      (permanent / contract / internship / volunteer / freelance / ambiguous)

Each dict carries independently-defined ground truth and names the EXISTING Affinda
field the analyser should check before claiming a gap (per the brief).
"""
from __future__ import annotations


def _exp(title, org, location, date_display, bullets, emp_type_label=""):
    return {"title": title, "org": org, "location": location,
            "date_display": date_display, "bullets": bullets,
            "emp_type_label": emp_type_label}


def _edu(degree, institution, location, date_display, note=""):
    return {"degree": degree, "institution": institution, "location": location,
            "date_display": date_display, "note": note}


def T(id, category, controlled, source_evidence, name, title, summary, experience,
      skills, expected, acceptable, fail_if, inconc, existing_field,
      education=None, certifications=None, work_auth=None, layout="flow",
      email=None, phone="+1 (415) 555-0100", location="Austin, TX"):
    return {
        "id": id, "category": category, "controlled": controlled,
        "source_evidence": source_evidence, "layout": layout,
        "name": name, "title": title,
        "email": email or (name.lower().replace(" ", ".") + "@examplemail.com"),
        "phone": phone, "location": location, "links": {},
        "summary": summary, "experience": experience,
        "education": education or [_edu("B.S. in Computer Science",
                                        "State University", location, "2010 – 2014")],
        "skills": skills, "certifications": certifications or [], "work_auth": work_auth,
        "expected": expected, "acceptable": acceptable,
        "confirmed_failure_if": fail_if, "inconclusive_if": inconc,
        "existing_field_to_check": existing_field, "expected_pages": 1,
    }


_ENG_EXP = [_exp("Software Engineer", "Brightwave Labs", "Austin, TX", "2018 – Present",
                 ["Build backend services and data pipelines."])]

# ============================================================================ #
#  1. NEGATED SKILLS (R301-R308)  — existing field: skills
# ============================================================================ #
NEGATED = [
    T("R301", "negated_skills", "positive control: plain skills list",
      "Skills: Python, SQL, Docker", "Dana Reed", "Software Engineer",
      "Engineer proficient in Python and SQL.", _ENG_EXP,
      ["Python", "SQL", "Docker"],
      {"skills_present": ["Python", "SQL", "Docker"], "skills_absent": []},
      ["all three skills extracted"], "a listed skill is missing",
      "n/a", "skills"),
    T("R302", "negated_skills", "negative control: denied skill in prose",
      'Summary says "No experience with Java."', "Omar Diaz", "Software Engineer",
      "Engineer proficient in Python. No experience with Java.", _ENG_EXP,
      ["Python", "SQL"],
      {"skills_present": ["Python"], "skills_absent": ["Java"]},
      ["Java treated as not-a-skill (absent, or marked negated)"],
      "Java is extracted as a candidate skill despite 'No experience with Java'",
      "Java absent AND no negation captured — acceptable (correct outcome)", "skills"),
    T("R303", "negated_skills", "negated proficiency",
      '"Not proficient in C++."', "Lena Park", "Backend Engineer",
      "Backend engineer. Strong in Go. Not proficient in C++.", _ENG_EXP,
      ["Go", "PostgreSQL"],
      {"skills_present": ["Go"], "skills_absent": ["C++"]},
      ["C++ treated as not-a-skill"],
      "C++ extracted as a candidate skill despite 'Not proficient in C++'",
      "C++ absent, negation not captured — acceptable", "skills"),
    T("R304", "negated_skills", "AMBIGUOUS partial exposure",
      '"Limited exposure to Rust."', "Sam Cole", "Engineer",
      "Engineer skilled in Python with limited exposure to Rust.", _ENG_EXP,
      ["Python"],
      {"note": "Rust is partial/limited — either inclusion or exclusion is defensible"},
      ["Rust included OR excluded — both acceptable"],
      "n/a (ambiguous)",
      "Rust handled either way — inconclusive by design", "skills"),
    T("R305", "negated_skills", "paired: expert + denied in one line",
      '"Expert in Python; no experience with R."', "Priya Shah", "Data Engineer",
      "Expert in Python; no experience with R.", _ENG_EXP,
      ["Python"],
      {"skills_present": ["Python"], "skills_absent": ["R"]},
      ["Python extracted; R not extracted"],
      "R extracted as a candidate skill", "R absent, negation not captured — acceptable", "skills"),
    T("R306", "negated_skills", "contrastive 'but not'",
      '"Familiar with AWS, but not Azure."', "Noah Kim", "Cloud Engineer",
      "Cloud engineer familiar with AWS, but not Azure.", _ENG_EXP,
      ["AWS"],
      {"skills_present": ["AWS"], "skills_absent": ["Azure"]},
      ["AWS extracted; Azure not extracted"],
      "Azure extracted as a candidate skill", "Azure absent, negation not captured — acceptable", "skills"),
    T("R307", "negated_skills", "AMBIGUOUS past/discontinued use",
      '"Previously used PHP; no longer work with it."', "Mia Torres", "Engineer",
      "Engineer. Previously used PHP; no longer work with it. Now focused on Node.js.", _ENG_EXP,
      ["Node.js"],
      {"note": "PHP is past/discontinued — inclusion as prior skill is defensible"},
      ["PHP included as prior skill OR excluded — both acceptable"],
      "n/a (ambiguous)", "PHP handled either way — inconclusive", "skills"),
    T("R308", "negated_skills", "negation inside the skills list",
      'Skills line: "Python, SQL (not Tableau)."', "Eli Ross", "Analyst",
      "Analyst skilled in Python and SQL.", _ENG_EXP,
      ["Python", "SQL"],
      {"skills_present": ["Python", "SQL"], "skills_absent": ["Tableau"]},
      ["Python, SQL extracted; Tableau excluded"],
      "Tableau extracted as a skill despite '(not Tableau)'",
      "Tableau absent — acceptable", "skills"),
]
# Encode the exact negation wording so the generator renders it:
NEGATED[1]["skills_line_note"] = "No experience with Java."
NEGATED[2]["skills_line_note"] = "Not proficient in C++."
NEGATED[4]["skills_line_note"] = "Expert in Python; no experience with R."
NEGATED[5]["skills_line_note"] = "Familiar with AWS, but not Azure."
NEGATED[7]["skills_line_note"] = "Python, SQL (not Tableau)."

# ============================================================================ #
#  2. WORK AUTHORISATION (R309-R316) — existing field: workAuthorization? (verify)
# ============================================================================ #
def _wa(id, controlled, wa_text, expected_status, fail_if, inconc,
        name, ambiguous=False):
    return T(id, "work_authorisation", controlled,
             f'Work authorisation line: "{wa_text}"', name, "Operations Analyst",
             "Operations analyst with 6 years of experience.",
             [_exp("Operations Analyst", "Keystone Group", "Austin, TX", "2018 – Present",
                   ["Process improvement and reporting."])],
             ["Process Improvement", "Excel", "SQL"],
             {"work_auth_status": expected_status},
             ["work authorisation represented in a field OR present in rawText"],
             fail_if, inconc, "workAuthorization (verify it exists)",
             work_auth=wa_text)


WORKAUTH = [
    _wa("R309", "citizen", "U.S. Citizen", "citizen",
        "status misrepresented as something other than citizen",
        "status absent from structured fields but present in rawText — inconclusive (no dedicated field)",
        "Grace Hall"),
    _wa("R310", "permanent resident", "Permanent Resident (Green Card holder)", "permanent_resident",
        "status misrepresented", "status only in rawText — inconclusive", "Victor Lee"),
    _wa("R311", "needs sponsorship", "Requires visa sponsorship to work in the U.S.", "sponsorship_required",
        "status inverted (e.g. shown as authorised/no-sponsorship)", "status only in rawText — inconclusive",
        " Amina Yusuf".strip()),
    _wa("R312", "authorised, no sponsorship", "Authorised to work in the U.S.; no sponsorship required",
        "authorised_no_sponsorship", "status inverted", "status only in rawText — inconclusive", "Ben Carter"),
    _wa("R313", "visa with expiry", "H-1B visa (valid through 2026)", "visa_with_expiry",
        "expiry dropped or status shown as permanent", "status/expiry only in rawText — inconclusive", "Kenji Sato"),
    _wa("R314", "expired authorisation", "Work authorisation expired in 2023", "expired",
        "shown as currently authorised (expiry ignored)", "status only in rawText — inconclusive", "Lola Marsh"),
    _wa("R315", "unknown (no statement)", "", "unknown",
        "a work-authorisation status is invented where none is stated",
        "no statement and no field — correct/neutral", "Tomas Vidal"),
]
# ambiguous control R316: a NON-work-auth phrase that must not be read as work auth
WORKAUTH.append(
    _wa("R316", "AMBIGUOUS non-statement", "Open to relocation and flexible work arrangements",
        "not_a_work_auth_statement",
        "the relocation phrase is interpreted as a work-authorisation status",
        "phrase not interpreted as work auth — acceptable", "Rosa Nunez", ambiguous=True))

# ============================================================================ #
#  3. SKILL OWNERSHIP (R317-R324) — existing field: skills + skills[].sources
# ============================================================================ #
def _own(id, controlled, bullet, skill, personal, fail_if, inconc, name):
    expected = {"skill": skill, "is_personal": personal}
    return T(id, "skill_ownership", controlled,
             f'Experience bullet: "{bullet}"', name, "Engineering Manager",
             "Engineering leader.",
             [_exp("Engineering Manager", "Northwind Tech", "Austin, TX", "2017 – Present", [bullet])],
             (["Leadership"] if not personal else ["Leadership", skill]),
             expected, ["ownership distinction is hard; either attribution may be defensible"],
             fail_if, inconc, "skills[].sources / skills (ownership not modelled)")


OWNERSHIP = [
    _own("R317", "personal (positive control)", "Built the data pipeline in Spark myself.",
         "Spark", True, "Spark not attributed to the candidate at all (missed personal skill)",
         "Spark attributed — correct", "Dana Oni"),
    _own("R318", "managed others (negative)", "Managed a team of 5 Python engineers.",
         "Python", False, "n/a (over-attribution is expected-but-not-penalised; record it)",
         "Python attributed to the candidate though they manage, not code — record as over-attribution; "
         "cannot be scored a hard failure without an ownership field", "Raj Mehta"),
    _own("R319", "led team using tool", "Led a team of data scientists using TensorFlow.",
         "TensorFlow", False, "n/a (record over-attribution)",
         "TensorFlow attributed to candidate — over-attribution, inconclusive", "Ivy Chen"),
    _own("R320", "oversaw work by others", "Oversaw a Kubernetes migration performed by the platform team.",
         "Kubernetes", False, "n/a (record over-attribution)",
         "Kubernetes attributed to candidate — over-attribution, inconclusive", "Paul Adebayo"),
    _own("R321", "paired personal", "I personally wrote the service in Go.",
         "Go", True, "Go not attributed (missed personal skill)", "Go attributed — correct", "Sara Blum"),
    _own("R322", "paired managed", "My team wrote the service in Go.",
         "Go", False, "n/a (record over-attribution)",
         "Go attributed to candidate though it was the team's — over-attribution, inconclusive", "Leo Fischer"),
    _own("R323", "AMBIGUOUS responsibility", "Responsible for the Java codebase.",
         "Java", None, "n/a (ambiguous)", "Java attributed either way — inconclusive by design", "Nina Volkov"),
    _own("R324", "mixed in one role", "I code in Python; managed a team of Go developers.",
         "Go", False, "Python (personal) not attributed",
         "Go (managed) attributed to candidate — over-attribution for the managed skill, inconclusive", "Hugo Reyes"),
]

# ============================================================================ #
#  4. EXPERIENCE DURATION (R325-R332) — existing field: employmentMetrics / dateRange.durationMonths
# ============================================================================ #
DURATION = [
    T("R325", "experience_duration", "explicit claim vs computable dates",
      'Summary: "10+ years of experience"; dates sum to ~6 years.', "Alan Pierce", "Senior Engineer",
      "Senior engineer with 10+ years of experience.",
      [_exp("Senior Engineer", "Acme Corp", "Austin, TX", "2019 – Present", ["Lead backend work."]),
       _exp("Engineer", "Beta Inc", "Austin, TX", "2016 – 2019", ["Backend services."])],
      ["Python", "AWS"],
      {"claimed_years": "10+", "computable_years_approx": 6},
      ["claim captured in rawText/summary; computed duration reflects actual dates (~6y)"],
      "the 10+ year claim is emitted as a verified total-experience figure that contradicts the dates",
      "no total-experience field exposed — inconclusive", "employmentMetrics / summary"),
    T("R326", "experience_duration", "part-time hours",
      'Role labelled "Part-time (20 hrs/week)".', "Beth Ng", "Analyst",
      "Part-time analyst.",
      [_exp("Analyst", "Keystone Group", "Austin, TX", "2020 – Present",
            ["Reporting and analysis."], emp_type_label="Part-time (20 hrs/week)")],
      ["Excel", "SQL"],
      {"part_time": True},
      ["part-time reflected in employmentType/metrics OR present in rawText"],
      "the role's reduced hours are counted as full-time duration with no part-time signal",
      "no part-time field — inconclusive", "workExperience[].employmentType / employmentMetrics"),
    T("R327", "experience_duration", "overlapping roles (double-count risk)",
      "Two concurrent roles 2020–present.", "Carl Reyes", "Consultant",
      "Consultant holding two concurrent roles.",
      [_exp("Consultant", "Northwind Tech", "Austin, TX", "2020 – Present", ["Advisory work."]),
       _exp("Advisor", "Cedar Foods", "Austin, TX", "2020 – Present", ["Board advisory."])],
      ["Strategy"],
      {"overlap": True, "no_double_count": True},
      ["total experience does NOT double-count the overlap"],
      "total/aggregate experience double-counts the overlapping period",
      "no aggregate figure exposed — inconclusive", "employmentMetrics"),
    T("R328", "experience_duration", "career gap",
      "2-year gap between roles (2017–2019 none).", "Dina Fox", "Engineer",
      "Engineer returning after a career break.",
      [_exp("Engineer", "Acme Corp", "Austin, TX", "2019 – Present", ["Backend."]),
       _exp("Engineer", "Beta Inc", "Austin, TX", "2013 – 2017", ["Backend."])],
      ["Java"],
      {"gap_years": "2017-2019"},
      ["gap inferable from dates; not mis-filled"],
      "the gap is erased by fabricating continuous employment",
      "no gap representation — inconclusive (dates still correct)", "employmentMetrics"),
    T("R329", "experience_duration", "approximate duration",
      '"Approximately 3 years" with no exact dates.', "Evan Blake", "Designer",
      "Designer with approximately 3 years of experience.",
      [_exp("Designer", "Studio Lark", "Austin, TX", "approx. 3 years", ["Brand design."])],
      ["Figma"],
      {"approx": "~3 years", "no_exact_dates": True},
      ["approximate duration captured OR left unknown; no false precise dates invented"],
      "precise start/end dates are fabricated from 'approximately 3 years'",
      "duration left unknown — acceptable", "workExperience[].dateRange"),
    T("R330", "experience_duration", "explicit claim contradicts dates",
      '"5 years at Company X" but dates show 2021–2024 (3 yrs).', "Fiona Webb", "Manager",
      "Manager with 5 years at Company X.",
      [_exp("Manager", "Company X", "Austin, TX", "2021 – 2024", ["Managed operations; '5 years at Company X'."])],
      ["Operations"],
      {"claimed": "5 years", "dates_imply": "3 years"},
      ["dates extracted as 2021–2024; the 5-year claim not emitted as verified duration"],
      "a 5-year duration is emitted for a role whose dates span 3 years",
      "no duration field — inconclusive", "workExperience[].dateRange.durationMonths"),
    T("R331", "experience_duration", "seasonal/intermittent",
      '"Summers 2018–2021" (intermittent).', "Gabe Stone", "Camp Lead",
      "Seasonal camp lead across four summers.",
      [_exp("Camp Lead", "Lakeside Camp", "Austin, TX", "Summers 2018 – 2021", ["Ran summer programs."])],
      ["Leadership"],
      {"intermittent": True},
      ["intermittent nature preserved OR dates left coarse; not inflated to continuous 2018–2021"],
      "the role is counted as continuous 2018–2021 full duration",
      "no intermittency field — inconclusive", "workExperience[].dateRange"),
    T("R332", "experience_duration", "paired full-time vs part-time (same dates)",
      'Same dates, labelled "Full-time" here.', "Hana Lund", "Engineer",
      "Full-time engineer.",
      [_exp("Engineer", "Acme Corp", "Austin, TX", "2020 – 2023", ["Backend."], emp_type_label="Full-time")],
      ["Python"],
      {"full_time": True},
      ["full-time reflected; comparable to R326 part-time"],
      "full-time vs part-time indistinguishable in output AND metrics inflated",
      "no distinction field — inconclusive", "workExperience[].employmentType"),
]

# ============================================================================ #
#  5. CERTIFICATION STATUS (R333-R340) — existing field: certifications
# ============================================================================ #
def _cert(id, controlled, cert_text, status, fail_if, inconc, name, positive=False):
    return T(id, "certification_status", controlled,
             f'Certifications: "{cert_text}"', name, "IT Specialist",
             "IT specialist.",
             [_exp("IT Specialist", "Northwind Tech", "Austin, TX", "2018 – Present", ["Systems administration."])],
             ["Networking", "Linux"],
             {"certification": cert_text, "status": status},
             ["certification captured; status represented in a field OR present in rawText"],
             fail_if, inconc, "certifications",
             certifications=[cert_text])


CERTS = [
    _cert("R333", "active (positive control)", "AWS Certified Solutions Architect — valid through 2026",
          "active", "certification missing from the certifications field",
          "status not in a field but cert captured — acceptable for a valid cert", "Ian Frost", positive=True),
    _cert("R334", "expired", "PMP — expired 2022", "expired",
          "certification shown as active/current with the expiry dropped",
          "expiry only in rawText, no status field — inconclusive", "Jade Owens"),
    _cert("R335", "pending", "CISSP — exam scheduled 2025 (pending)", "pending",
          "a pending certification is shown as earned/held",
          "pending only in rawText — inconclusive", "Kyle Barnes"),
    _cert("R336", "failed", "CPA exam — attempted, did not pass", "failed",
          "CPA shown as an earned certification",
          "failure only in rawText — inconclusive", "Lara Simmons"),
    _cert("R337", "revoked", "State license — revoked 2023", "revoked",
          "license shown as currently held",
          "revocation only in rawText — inconclusive", "Mark Levy"),
    _cert("R338", "training only", "AWS training completed (no certification taken)", "training_only",
          "training recorded as a held certification",
          "distinction only in rawText — inconclusive", "Nora Pace"),
    _cert("R339", "coursework, not awarded", "Security+ coursework completed; exam not taken", "not_awarded",
          "Security+ shown as an awarded certification",
          "distinction only in rawText — inconclusive", "Omar Blum"),
    _cert("R340", "paired active vs expired (same cert)", "PMP — active (renewed 2024)", "active",
          "active PMP not captured", "status not in a field — acceptable for an active cert",
          "Pia Nord", positive=True),
]

# ============================================================================ #
#  6. EMPLOYMENT TYPE (R341-R348) — existing field: workExperience[].employmentType
# ============================================================================ #
def _emp(id, controlled, label, expected_type, fail_if, inconc, name, positive=False):
    return T(id, "employment_type", controlled,
             f'Role labelled "{label}".', name, "Associate",
             "Associate with varied engagements.",
             [_exp("Associate", "Cedar Foods", "Austin, TX", "2021 – 2023", ["Project delivery."],
                   emp_type_label=label)],
             ["Project Management"],
             {"employment_type_expected": expected_type},
             ["employmentType reflects the labelled arrangement OR it is present in rawText"],
             fail_if, inconc, "workExperience[].employmentType")


EMPTYPE = [
    _emp("R341", "permanent (control)", "Full-time, permanent", "permanent",
         "a permanent role mis-typed as something else", "n/a", "Quinn Tate", positive=True),
    _emp("R342", "contract", "6-month contract", "contract",
         "a contract role typed as permanent with no contract signal",
         "contract only in rawText — inconclusive", "Remy Lanz"),
    _emp("R343", "internship", "Summer Internship", "internship",
         "an internship typed as permanent/full-time employment",
         "internship only in rawText — inconclusive", "Suki Rao"),
    _emp("R344", "volunteer (unpaid)", "Volunteer (unpaid)", "volunteer",
         "unpaid volunteer work typed as paid employment",
         "volunteer only in rawText — inconclusive", "Theo Marsh"),
    _emp("R345", "freelance", "Freelance", "freelance",
         "freelance typed as permanent employment",
         "freelance only in rawText — inconclusive", "Uma Patel"),
    _emp("R346", "temporary/seasonal", "Temporary seasonal", "temporary",
         "a temporary role typed as permanent",
         "temporary only in rawText — inconclusive", "Vince Ortega"),
    _emp("R347", "AMBIGUOUS 'Consultant'", "Consultant", "ambiguous",
         "n/a (ambiguous — could be contract or employee)",
         "either typing acceptable — inconclusive by design", "Wendy Soto"),
    _emp("R348", "paired: SAME role as internship vs permanent", "Internship", "internship",
         "typed identically to the permanent paired control (R341) despite the internship label",
         "internship only in rawText — inconclusive", "Xan Pham"),
]


CANDIDATES = NEGATED + WORKAUTH + OWNERSHIP + DURATION + CERTS + EMPTYPE
BY_ID = {c["id"]: c for c in CANDIDATES}
CATEGORIES = ["negated_skills", "work_authorisation", "skill_ownership",
              "experience_duration", "certification_status", "employment_type"]


if __name__ == "__main__":
    assert len(CANDIDATES) == 48, f"expected 48, got {len(CANDIDATES)}"
    ids = [c["id"] for c in CANDIDATES]
    assert ids == [f"R3{i:02d}" for i in range(1, 49)], ids[:5]
    from collections import Counter
    cc = Counter(c["category"] for c in CANDIDATES)
    for cat in CATEGORIES:
        assert cc[cat] == 8, f"{cat}={cc[cat]}"
    # no duplicate emails
    assert len({c["email"] for c in CANDIDATES}) == 48, "duplicate emails"
    print(f"OK: 48 tests, 8 per category, IDs R301..R348")
