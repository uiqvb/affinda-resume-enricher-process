"""
round4_candidates.py — 60 synthetic probe resumes (R401-R460) for Round 4:
independent confirmation / narrowing / falsification of Round 3's findings.

Six categories, 10 each, each isolating one semantic variable where possible.
Ground truth (expectations, acceptable alternates, confirmed-failure / partial-loss /
inconclusive criteria, paired-test links, existing Affinda field to check first) is
defined here from the synthetic source — never from parser output.

REFERENCE_DATE is the single documented date for all duration expectations.
"""
from __future__ import annotations

REFERENCE_DATE = "2026-11-12"


def _exp(title, org, date_display, bullets, location="Sydney, NSW", emp_type_label=""):
    return {"title": title, "org": org, "location": location,
            "date_display": date_display, "bullets": bullets, "emp_type_label": emp_type_label}


def _edu(degree, institution, date_display, location="Sydney, NSW", note=""):
    return {"degree": degree, "institution": institution, "location": location,
            "date_display": date_display, "note": note}


def T(id, category, controlled, source_evidence, name, title, summary, experience,
      skills, expected, acceptable, fail_if, partial_if, inconc, existing_field,
      certifications=None, work_auth=None, skills_line_note=None, paired_with=None,
      multi_variable=False, location="Sydney, NSW", phone="+61 2 5550 0100"):
    return {
        "id": id, "category": category, "controlled": controlled,
        "source_evidence": source_evidence, "layout": "flow",
        "name": name, "title": title,
        "email": name.lower().replace(" ", ".") + "@examplemail.com",
        "phone": phone, "location": location, "links": {},
        "summary": summary, "experience": experience,
        "education": [_edu("B.S. in Computer Science", "State University", "2010 – 2014", location)],
        "skills": skills, "certifications": certifications or [], "work_auth": work_auth,
        "skills_line_note": skills_line_note,
        "expected": expected, "acceptable": acceptable,
        "confirmed_failure_if": fail_if, "partial_loss_if": partial_if, "inconclusive_if": inconc,
        "existing_field_to_check": existing_field, "paired_with": paired_with,
        "multi_variable": multi_variable, "expected_pages": 1,
    }


_ENG = [_exp("Software Engineer", "Brightwave Labs", "2018 – Present",
             ["Build backend services and data pipelines."])]

# ====================== A. NEGATED SKILLS (R401-R410) ======================
# existing field: skills (+ skills[].sources). Determine literal-mention vs claimed-capability.
def _neg(id, stmt, denied, affirmed, fail_if, partial_if, inconc, name, note_in="summary",
         multi=False, paired=None):
    summ = "Engineer. " + (stmt if note_in == "summary" else "")
    sln = stmt if note_in == "skills" else None
    return T(id, "negated_skills", f'negation: "{stmt}"', f'"{stmt}"', name,
             "Software Engineer", summ.strip(), _ENG, affirmed,
             {"skills_affirmed": affirmed, "skills_denied": denied},
             ["denied skills absent, or present but tagged negative/low; affirmed skills present"],
             fail_if, partial_if, inconc, "skills (+ sources / provenance)",
             skills_line_note=sln, multi_variable=multi, paired_with=paired)


NEGATED = [
    _neg("R401", "No hands-on experience with Kubernetes.", ["Kubernetes"], ["Python"],
         "Kubernetes extracted as a possessed skill", "Kubernetes present but no negative provenance",
         "Kubernetes absent — acceptable", "Ada Mercer"),
    _neg("R402", "Python: advanced. Java: none.", ["Java"], ["Python"],
         "Java extracted as a possessed skill despite 'Java: none'",
         "Java present without the 'none' qualifier", "Java absent — acceptable", "Ben Rhodes",
         note_in="skills"),
    _neg("R403", "Experienced in AWS, but have never used Azure.", ["Azure"], ["AWS"],
         "Azure extracted as a possessed skill", "Azure present without negative provenance",
         "Azure absent — acceptable", "Cara Lin"),
    _neg("R404", "Theoretical knowledge of Docker but no practical Docker experience.",
         ["Docker (practical)"], ["Python"],
         "Docker extracted as a hands-on skill with no theoretical/partial qualifier",
         "Docker present but partial/theoretical not distinguished",
         "Docker handled as partial — acceptable; this is a PARTIAL vs ZERO case", "Dev Kapoor"),
    _neg("R405", "Previously used React, but have not used it in five years.", ["React (recent)"],
         ["Python"], "n/a (stale skill — inclusion defensible)",
         "React present without recency qualifier", "React handled either way — ambiguous/partial",
         "Ella Ford"),
    _neg("R406", "Without any SQL background.", ["SQL"], ["Python"],
         "SQL extracted as a possessed skill despite 'without any SQL background'",
         "SQL present without negative provenance", "SQL absent — acceptable", "Finn Oyelaran"),
    _neg("R407", "Not certified in AWS, but use AWS daily.", [], ["AWS"],
         "AWS recorded as a held certification (it is a used skill, NOT a certification)",
         "AWS skill present but 'not certified' not distinguished from certified",
         "AWS as skill (yes) and not as certification — correct", "Gia Romano",
         multi=True),
    _neg("R408", "No experience with JavaScript. Extensive Java experience.", ["JavaScript"],
         ["Java"], "JavaScript extracted as a skill, OR Java/JavaScript conflated",
         "JavaScript present without negative provenance",
         "JavaScript absent and Java present — correct", "Hugo Vance", paired="R402"),
    _neg("R409", "I do not manage Kubernetes clusters, but develop applications deployed to Kubernetes.",
         [], ["Kubernetes"], "n/a (affirmative: develops on Kubernetes)",
         "Kubernetes present but management-vs-development provenance not distinguished",
         "Kubernetes present as a used skill — correct (MULTI-VARIABLE: ownership + affirmation)",
         "Ivy Zhang", multi=True),
]
# R410: clean positive control
NEGATED.append(T("R410", "negated_skills", "positive control (all affirmed)",
               "Expertise in Python, Kubernetes, SQL and Azure.", "Hana Blake",
               "Software Engineer", "Engineer with expertise in Python, Kubernetes, SQL and Azure.",
               _ENG, ["Python", "Kubernetes", "SQL", "Azure"],
               {"skills_affirmed": ["Python", "Kubernetes", "SQL", "Azure"], "skills_denied": []},
               ["all four skills extracted"], "an affirmed skill is missing",
               "an affirmed skill is missing", "n/a", "skills", paired_with="R401"))

# ====================== B. SKILL OWNERSHIP (R411-R420) ======================
def _own(id, controlled, bullet, skill, owner, fail_if, inconc, name, title="Engineering Manager"):
    return T(id, "skill_ownership", controlled, f'"{bullet}"', name, title,
             "Technology professional.",
             [_exp(title, "Northwind Tech", "2017 – Present", [bullet])],
             (["Leadership"] if owner != "candidate" else ["Leadership", skill]),
             {"skill": skill, "true_owner": owner},
             ["ownership not modelled; attribution may be defensible for managers"],
             fail_if,
             "skill attributed to candidate though owned by " + owner + " — record provenance gap",
             inconc, "skills (+ sources); no ownership dimension")


OWNERSHIP = [
    _own("R411", "personal (positive control)", "Personally developed Python services.",
         "Python", "candidate", "Python not attributed (missed personal skill)",
         "Python attributed — correct", "Jade Cole"),
    _own("R412", "managed engineers, no coding", "Managed Python engineers without writing Python.",
         "Python", "team", "n/a (over-attribution expected; record it)",
         "over-attribution of a managed skill — inconclusive", "Kiran Das"),
    _own("R413", "team used tool; candidate did finance",
         "Led a team whose engineers used Kubernetes; my responsibilities were financial management.",
         "Kubernetes", "team", "n/a", "over-attribution — inconclusive", "Lena Ruiz", title="Finance Lead"),
    _own("R414", "personally configured (positive)", "Personally configured Kubernetes clusters.",
         "Kubernetes", "candidate", "Kubernetes not attributed (missed personal skill)",
         "Kubernetes attributed — correct", "Milo Schwarz", title="DevOps Engineer"),
    _own("R415", "external contractor", "Coordinated work performed by an external Java development agency.",
         "Java", "external_contractor", "n/a", "Java attributed to candidate though an external agency did it — provenance gap",
         "Noor Haddad", title="Program Manager"),
    _own("R416", "reviewed, did not write", "Reviewed Java pull requests without writing implementation code.",
         "Java", "team", "n/a", "Java attributed as hands-on though candidate only reviewed — provenance gap",
         "Omar Blake", title="Tech Lead"),
    _own("R417", "personal Go (positive)", "Personally developed backend services in Go.",
         "Go", "candidate", "Go not attributed (missed personal skill)", "Go attributed — correct",
         "Piper Nolan", title="Backend Engineer"),
    _own("R418", "managed team, explicitly never used", "Managed a Go development team but explicitly never used Go.",
         "Go", "team", "n/a (but explicit denial of personal use)",
         "Go attributed to candidate despite explicit 'never used Go' — strongest ownership/negation gap",
         "Quinn Abara", title="Engineering Manager"),
    _own("R419", "both personal and supervised", "Both personally used SQL and supervised SQL analysts.",
         "SQL", "candidate", "SQL not attributed (it IS personal here)",
         "SQL attributed — correct (candidate personally used it)", "Rhea Kapoor", title="Data Lead"),
    _own("R420", "competitor-tech mention only", "Evaluated React only as a competitor technology; no proficiency claimed.",
         "React", "none_context", "React attributed as a candidate skill from a competitor-context mention",
         "React attributed despite no proficiency claim — context/provenance gap", "Sami Oduya",
         title="Product Manager"),
]

# ====================== C. CERTIFICATION VALIDITY (R421-R430) ==============
def _cert(id, controlled, cert_text, status, fail_if, partial_if, inconc, name, positive=False, extra=None):
    certs = [cert_text] + (extra or [])
    return T(id, "certification_validity", controlled, f'Certifications: "{cert_text}"', name,
             "IT Specialist", "IT specialist.",
             [_exp("IT Specialist", "Northwind Tech", "2018 – Present", ["Systems administration."])],
             ["Networking", "Linux"],
             {"certification": cert_text, "status": status},
             ["certification captured; status/validity represented in a field OR preserved in rawText"],
             fail_if, partial_if, inconc, "certifications", certifications=certs)


CERTS = [
    _cert("R421", "active (positive)", "AWS Certified Solutions Architect — active, valid through 2027",
          "active", "certification missing from the certifications field",
          "no status field but active cert captured — acceptable", "n/a", "Tariq Bello", positive=True),
    _cert("R422", "expired", "AWS Certified Solutions Architect — expired 2022", "expired",
          "shown as active/current with expiry dropped", "date captured but no 'expired' status",
          "expiry only in rawText — inconclusive", "Uma Castellano"),
    _cert("R423", "renewed (positive)", "PMP — renewed 2025 (current)", "active",
          "PMP not captured", "no explicit validity field but renewal date captured — acceptable",
          "n/a", "Vikram Shah", positive=True),
    _cert("R424", "revoked", "Chartered Engineer licence — revoked 2024", "revoked",
          "licence shown as currently held", "revocation not represented as status",
          "revocation only in rawText — inconclusive", "Wren Alvarez"),
    _cert("R425", "scheduled, not attempted", "Security+ — exam scheduled, not yet attempted", "pending",
          "shown as a held/earned certification", "pending not distinguished from held",
          "pending only in rawText — inconclusive", "Xena Ford"),
    _cert("R426", "attempted, failed", "Security+ — exam attempted, did not pass", "failed",
          "shown as an earned certification", "failure not represented",
          "failure only in rawText — inconclusive", "Yuki Brenner"),
    _cert("R427", "training only, no exam", "AWS certification training completed; exam never taken", "training_only",
          "recorded as a held certification", "training-vs-certified not distinguished",
          "distinction only in rawText — inconclusive", "Zane Okoro"),
    _cert("R428", "suspended temporarily", "Professional licence — temporarily suspended", "suspended",
          "licence shown as active", "suspension not represented (and not distinguished from revoked)",
          "suspension only in rawText — inconclusive", "Aria Lund"),
    _cert("R429", "two certs: active + expired", "CISSP — active (2026)", "active",
          "the expired one shown as active, or one dropped", "no per-cert status to tell them apart",
          "status only in rawText — inconclusive", "Beau Castellano", positive=True,
          extra=["PMP — expired 2021"]),
    _cert("R430", "expiry date, no validity statement", "ITIL Foundation — expires 2024", "expiry_only",
          "treated as currently valid despite a past expiry date", "no current-validity inference from a past expiry",
          "ambiguous — expiry present, validity unstated", "Cleo Marsh"),
]

# ====================== D. EMPLOYMENT CLASSIFICATION (R431-R440) ==========
# Independent dimensions: schedule (full/part/casual), relationship (employee/contractor/intern/volunteer),
# permanence (permanent/fixed-term/temporary). Flag when compressed into one enum.
def _emp(id, controlled, label, dims, fail_if, inconc, name, multi=True, paired=None):
    return T(id, "employment_classification", controlled, f'Role labelled "{label}".', name,
             "Associate", "Associate with varied engagements.",
             [_exp("Associate", "Cedar Foods", "2021 – 2023", ["Project delivery."], emp_type_label=label)],
             ["Project Management"],
             {"label": label, "dimensions": dims},
             ["employmentType reflects as many dimensions as it can; rest preserved in rawText"],
             fail_if,
             "independent dimensions compressed into one enum / mislabelled",
             inconc, "workExperience[].employmentType (single enum — dimensions may compress)",
             multi_variable=multi, paired_with=paired)


EMPLOY = [
    _emp("R431", "permanent full-time (control)", "Permanent, full-time",
         {"schedule": "full_time", "relationship": "employee", "permanence": "permanent"},
         "mis-typed as non-permanent/non-full-time", "n/a", "Dana Pryce", multi=False),
    _emp("R432", "fixed-term full-time contract", "Fixed-term 6-month full-time contract",
         {"schedule": "full_time", "relationship": "contractor", "permanence": "fixed_term"},
         "typed as part_time (schedule) losing the contract/fixed-term dimensions",
         "contract/fixed-term only in rawText — inconclusive", "Ewan Sato"),
    _emp("R433", "permanent part-time", "Permanent, part-time",
         {"schedule": "part_time", "relationship": "employee", "permanence": "permanent"},
         "permanence lost (typed merely part_time with no permanent signal)",
         "permanence only in rawText — inconclusive", "Farah Nolan", paired="R431"),
    _emp("R434", "unpaid volunteer", "Volunteer (unpaid) at a charity",
         {"schedule": "part_time", "relationship": "volunteer", "permanence": "temporary"},
         "volunteer typed as internship or paid employment",
         "volunteer only in rawText — inconclusive", "Gus Rahman"),
    _emp("R435", "paid summer internship", "Paid summer internship",
         {"schedule": "full_time", "relationship": "intern", "permanence": "fixed_term"},
         "internship typed as permanent/full-time employee",
         "internship captured but paid/unpaid not distinguished — inconclusive", "Hira Costa"),
    _emp("R436", "independent consulting contract", "Independent consulting contract",
         {"schedule": "full_time", "relationship": "contractor", "permanence": "fixed_term"},
         "typed as permanent employee", "contractor only in rawText — inconclusive", "Ike Varga"),
    _emp("R437", "temporary agency employment", "Temporary role via staffing agency",
         {"schedule": "full_time", "relationship": "agency_temp", "permanence": "temporary"},
         "typed as permanent; agency/temp lost", "agency/temp only in rawText — inconclusive", "Jina Peral"),
    _emp("R438", "casual, variable hours", "Casual employment, variable hours",
         {"schedule": "casual", "relationship": "employee", "permanence": "ongoing"},
         "casual typed as full_time/part_time losing the casual schedule",
         "casual only in rawText — inconclusive", "Kofi Mensah"),
    _emp("R439", "volunteer alongside permanent (two roles)", "Permanent role + volunteer role",
         {"note": "two roles: one permanent employee, one volunteer"},
         "both roles typed identically (volunteer not distinguished from permanent)",
         "volunteer vs permanent only in rawText — inconclusive", "Lara Pune", multi=True),
    _emp("R440", "contract-to-permanent conversion", "Contract-to-permanent (converted within one employer)",
         {"note": "one employer, converted from contract to permanent"},
         "conversion represented as a single flat type with no transition",
         "conversion only in rawText — inconclusive", "Milan Rost"),
]
# R439 needs two roles
EMPLOY[8]["experience"] = [
    _exp("Operations Associate", "Cedar Foods", "2021 – Present", ["Operations."], emp_type_label="Permanent, full-time"),
    _exp("Community Volunteer", "Helping Hands Charity", "2020 – Present", ["Weekend volunteering."], emp_type_label="Volunteer (unpaid)"),
]
EMPLOY[9]["experience"] = [
    _exp("Analyst", "Cedar Foods", "2021 – Present",
         ["Started as a 12-month contractor; converted to permanent in 2022."],
         emp_type_label="Contract-to-permanent"),
]

# ====================== E. WORK AUTHORISATION (R441-R450) ==================
def _wa(id, controlled, wa_text, dims, fail_if, partial_if, inconc, name, conflicting=False):
    return T(id, "work_authorisation", controlled, f'"{wa_text}"', name, "Operations Analyst",
             "Operations analyst.",
             [_exp("Operations Analyst", "Keystone Group", "2018 – Present", ["Reporting."])],
             ["Excel", "SQL"],
             {"stated": wa_text, "dimensions": dims},
             ["workAuthorization field preserves the stated claim's key dimensions"],
             fail_if, partial_if, inconc, "workAuthorization", work_auth=wa_text)


WORKAUTH = [
    _wa("R441", "citizen", "Australian citizen", {"jurisdiction": "AU", "category": "citizen"},
        "status inverted/misclassified", "jurisdiction or category dropped", "field absent — inconclusive", "Nadia Oren"),
    _wa("R442", "permanent resident", "Australian permanent resident", {"jurisdiction": "AU", "category": "permanent_resident"},
        "status inverted", "category dropped", "field absent — inconclusive", "Oscar Blum"),
    _wa("R443", "temp visa with expiry", "Temporary work visa valid until 2028",
        {"category": "temporary_visa", "expiry": "2028"},
        "shown as permanent/unrestricted", "expiry 2028 dropped", "field absent — inconclusive", "Petra Nunez"),
    _wa("R444", "expired", "Work authorisation expired in 2023", {"status": "expired", "expiry": "2023"},
        "shown as currently authorised", "expiry/expired status dropped (as in Round 3 R314)",
        "field absent — inconclusive", "Quincy Hart"),
    _wa("R445", "needs sponsorship", "Requires employer sponsorship", {"sponsorship": "required"},
        "shown as not requiring sponsorship", "sponsorship requirement dropped", "field absent — inconclusive", "Rania Vale"),
    _wa("R446", "no sponsorship", "Does not require sponsorship", {"sponsorship": "not_required"},
        "shown as requiring sponsorship", "sponsorship dimension dropped", "field absent — inconclusive", "Sten Ohara"),
    _wa("R447", "hours restriction", "Work rights restricted to 24 hours per week",
        {"restriction": "24h/week"}, "shown as unrestricted", "the 24h/week restriction dropped",
        "field absent — inconclusive", "Tomi Adeyemi"),
    _wa("R448", "unknown current status", "Previously authorised to work; current status unknown",
        {"status": "unknown"}, "a definite status invented where source says unknown",
        "'unknown' flattened to a definite status", "field absent — inconclusive", "Ula Petit"),
    _wa("R449", "eligible, not obtained", "Eligible for a visa but has not obtained one",
        {"status": "eligible_not_obtained"}, "shown as currently holding a visa",
        "eligible-vs-held distinction dropped", "field absent — inconclusive", "Viktor Mraz"),
    _wa("R450", "CONFLICTING statements", "Authorised to work with no restrictions // Requires sponsorship (conflicting)",
        {"status": "conflicting"}, "silently picks one with no conflict signal",
        "only one statement preserved", "field absent — inconclusive", "Wanda Ilori", conflicting=True),
]

# ====================== F. EMPLOYMENT DURATION (R451-R460) =================
# existing field: employmentMetrics (totals/gaps/tenure), dateRange.durationMonths. Reference date 2026-11-12.
def _dur(id, controlled, experience, expected, fail_if, partial_if, inconc, name, multi=False, paired=None):
    return T(id, "employment_duration", controlled, controlled, name, "Consultant",
             "Experienced professional.", experience, ["Strategy"],
             expected, ["employmentMetrics reflects calendar experience; overlaps not double-counted"],
             fail_if, partial_if, inconc, "employmentMetrics / dateRange.durationMonths",
             multi_variable=multi, paired_with=paired)


DURATION = [
    _dur("R451", "two ENTIRELY overlapping jobs (same dates)",
         [_exp("Consultant", "Northwind Tech", "2020 – 2023", ["Advisory."]),
          _exp("Advisor", "Cedar Foods", "2020 – 2023", ["Advisory."])],
         {"calendar_span": "2020-2023 (~3y)", "no_double_count": True},
         "total experience double-counts (≈6y instead of ≈3y)",
         "both roles kept but total unclear", "no aggregate field — inconclusive", "Xavi Rome"),
    _dur("R452", "three PARTIALLY overlapping jobs",
         [_exp("Lead", "Alpha Co", "2019 – 2023", ["Lead."]),
          _exp("Advisor", "Beta Co", "2021 – 2024", ["Advise."]),
          _exp("Consultant", "Gamma Co", "2022 – Present", ["Consult."])],
         {"calendar_span": "2019-present", "no_double_count": True},
         "total double-counts overlapping spans", "partial handling", "inconclusive", "Yara Cole"),
    _dur("R453", "full-time + freelance weekend work (concurrent)",
         [_exp("Engineer", "Alpha Co", "2019 – Present", ["Full-time engineering."], emp_type_label="Full-time"),
          _exp("Freelance Designer", "Self-Employed", "2019 – Present", ["Weekend freelance."], emp_type_label="Freelance")],
         {"concurrent": True, "fte_vs_calendar": "calendar overlaps; FTE not promised"},
         "calendar experience double-counted for the concurrent freelance",
         "concurrency captured but hours/FTE not", "FTE not promised — do not penalise; inconclusive", "Zola Byrne"),
    _dur("R454", "multiple short contracts with gaps",
         [_exp("Contractor", "Alpha Co", "Jan 2020 – Jun 2020", ["Contract."]),
          _exp("Contractor", "Beta Co", "Jan 2021 – Jun 2021", ["Contract."]),
          _exp("Contractor", "Gamma Co", "Jan 2023 – Jun 2023", ["Contract."])],
         {"gaps_expected": True, "sum_of_tenures": "~18 months across 3 contracts"},
         "gaps erased / continuous employment fabricated", "gaps not surfaced but dates correct",
         "no gap field — inconclusive (dates still correct)", "Aron Diaz"),
    _dur("R455", "three promotions, one employer, continuous",
         [_exp("Director", "Lakeshore Ltd", "2022 – Present", ["Director."]),
          _exp("Manager", "Lakeshore Ltd", "2019 – 2022", ["Manager."]),
          _exp("Coordinator", "Lakeshore Ltd", "2017 – 2019", ["Coordinator."])],
         {"continuous_tenure": "2017-present at one employer", "no_double_count": True},
         "continuous tenure double-counted or employer fragmented",
         "roles kept but tenure mis-aggregated", "inconclusive", "Bina Oke", paired="R451"),
    _dur("R456", "role 2021 – Present (open current)",
         [_exp("Engineer", "Alpha Co", "2021 – Present", ["Engineering."])],
         {"current": True, "no_fabricated_end": True},
         "a fabricated end date (end==start / 1-month) as in Round 2 D04",
         "current but tenure to reference date not computed", "inconclusive", "Caro Vance"),
    _dur("R457", "explicit career break",
         [_exp("Engineer", "Alpha Co", "2022 – Present", ["Engineering."]),
          _exp("Career break (caregiving)", "", "2020 – 2022", ["Explicit career break."]),
          _exp("Engineer", "Beta Co", "2015 – 2020", ["Engineering."])],
         {"gap_or_break": "2020-2022 explicitly labelled a break"},
         "the break is counted as employment", "break not represented but dates correct",
         "no break field — inconclusive", "Dax Oyelaran"),
    _dur("R458", "part-time over five years",
         [_exp("Analyst", "Alpha Co", "2019 – 2024", ["Part-time analysis."], emp_type_label="Part-time")],
         {"calendar": "~5y", "fte_vs_calendar": "calendar 5y; FTE lower, not promised"},
         "n/a (FTE not promised)", "part-time not reflected in type/metrics",
         "FTE not promised — inconclusive", "Effie Lund"),
    _dur("R459", "concurrent internships + university employment",
         [_exp("Intern", "Alpha Co", "Summer 2021", ["Internship."], emp_type_label="Internship"),
          _exp("Research Assistant", "State University", "2020 – 2022", ["Campus employment."], emp_type_label="Part-time"),
          _exp("Intern", "Beta Co", "Summer 2022", ["Internship."], emp_type_label="Internship")],
         {"concurrent_overlaps": True},
         "overlapping internships/university work double-counted",
         "roles kept but overlap handling unclear", "inconclusive", "Fynn Castellano", multi=True),
    _dur("R460", "one completed + one unspecified end date",
         [_exp("Engineer", "Alpha Co", "2023 –", ["Current role, no explicit end date."]),
          _exp("Engineer", "Beta Co", "2019 – 2022", ["Completed role."])],
         {"open_role": "2023 – (no end)", "no_fabricated_end": True},
         "the open-ended role gets a fabricated end date (Round 2 D04 pattern)",
         "open role flagged current but no duration", "inconclusive", "Gaby Nunez", paired="R456"),
]


CANDIDATES = NEGATED + OWNERSHIP + CERTS + EMPLOY + WORKAUTH + DURATION
BY_ID = {c["id"]: c for c in CANDIDATES}
CATEGORIES = ["negated_skills", "skill_ownership", "certification_validity",
              "employment_classification", "work_authorisation", "employment_duration"]


if __name__ == "__main__":
    assert len(CANDIDATES) == 60, f"expected 60, got {len(CANDIDATES)}"
    ids = [c["id"] for c in CANDIDATES]
    assert ids == [f"R4{i:02d}" for i in range(1, 61)], ids[:6]
    from collections import Counter
    cc = Counter(c["category"] for c in CANDIDATES)
    for cat in CATEGORIES:
        assert cc[cat] == 10, f"{cat}={cc[cat]}"
    assert len({c["email"] for c in CANDIDATES}) == 60, "dup emails"
    print(f"OK: 60 tests, 10 per category, IDs R401..R460, reference_date={REFERENCE_DATE}")
