"""
candidates.py — Single source of truth for the 20 synthetic Affinda test resumes.

All ground-truth data is DERIVED FROM THIS MODULE, never by extracting text from
the generated PDFs. Categories covered here: A, D, E, F (5 each = 20).
Categories B and C are a separate project and are intentionally NOT defined here.

Each candidate is a dict. Date fields carry both a human `start`/`end` display
string and an ISO `start_iso`/`end_iso` (YYYY-MM, or "present"/None) used for
machine-checkable ground truth. For intentionally ambiguous cases, the ambiguity
is recorded explicitly under `known_ambiguities` / `acceptable_interpretations`
rather than being resolved to a single invented answer.
"""
from __future__ import annotations


def _exp(title, org, location, start, end, start_iso, end_iso, bullets):
    return {
        "title": title, "org": org, "location": location,
        "start": start, "end": end,
        "start_iso": start_iso, "end_iso": end_iso,
        "bullets": bullets,
    }


def _edu(degree, institution, location, start, end, note=""):
    return {
        "degree": degree, "institution": institution, "location": location,
        "start": start, "end": end, "note": note,
    }


CANDIDATES = [

    # ============================ CATEGORY A — BASELINE ============================
    {
        "id": "A01", "category": "A", "difficulty": "baseline",
        "layout": "flow",
        "name": "Daniel Okafor",
        "title": "Senior Software Engineer",
        "email": "daniel.okafor@examplemail.com",
        "emails": ["daniel.okafor@examplemail.com"],
        "phone": "+1 (415) 555-0142",
        "location": "San Francisco, CA",
        "links": {"LinkedIn": "linkedin.com/in/danielokafor"},
        "summary": (
            "Senior software engineer with eight years building reliable backend "
            "services and developer tooling. Focused on distributed systems, API "
            "design and mentoring."
        ),
        "experience": [
            _exp("Senior Software Engineer", "Northwind Technologies", "San Francisco, CA",
                 "Mar 2021", "Present", "2021-03", "present",
                 ["Led migration of a monolith to services, cutting p95 latency by 38%.",
                  "Designed an internal API gateway now handling 1.2B requests per month.",
                  "Mentored four engineers; two were promoted within a year."]),
            _exp("Software Engineer", "Brightwave Labs", "Oakland, CA",
                 "Jul 2017", "Feb 2021", "2017-07", "2021-02",
                 ["Built the billing service in Go, supporting 90k paying customers.",
                  "Introduced contract testing, reducing integration defects by 45%."]),
            _exp("Junior Developer", "Cobalt Systems", "San Jose, CA",
                 "Aug 2015", "Jun 2017", "2015-08", "2017-06",
                 ["Developed REST endpoints for the inventory platform.",
                  "Automated deployment scripts, saving roughly six hours per week."]),
        ],
        "education": [
            _edu("B.S. in Computer Science", "University of California, Davis", "Davis, CA",
                 "2011", "2015"),
        ],
        "skills": ["Go", "Python", "PostgreSQL", "Kubernetes", "gRPC", "AWS",
                   "Distributed Systems", "CI/CD"],
        "test_hypothesis": "Parser extracts a conventional single-employer-per-role history cleanly.",
        "intentional_complexity": "None — clean baseline.",
        "known_ambiguities": [],
        "acceptable_interpretations": [],
        "expected_pages": 1,
        "fields_to_inspect": ["name", "emails", "phoneNumbers", "workExperience", "education", "skills"],
    },
    {
        "id": "A02", "category": "A", "difficulty": "baseline",
        "layout": "flow",
        "name": "Priya Nair",
        "title": "Registered Nurse, BSN",
        "email": "priya.nair@examplemail.com",
        "emails": ["priya.nair@examplemail.com"],
        "phone": "+1 (617) 555-0188",
        "location": "Boston, MA",
        "links": {},
        "summary": (
            "Registered nurse with six years of acute-care and med-surg experience. "
            "ACLS and BLS certified. Known for calm patient communication and accurate charting."
        ),
        "experience": [
            _exp("Registered Nurse, Medical-Surgical Unit", "Charles River Medical Center", "Boston, MA",
                 "Jun 2020", "Present", "2020-06", "present",
                 ["Manage a rotating caseload of up to six acute-care patients per shift.",
                  "Precept new graduate nurses through a 12-week onboarding program.",
                  "Maintain a medication-administration accuracy audit score above 99%."]),
            _exp("Staff Nurse, Telemetry", "Granite State Hospital", "Manchester, NH",
                 "Aug 2018", "May 2020", "2018-08", "2020-05",
                 ["Monitored cardiac telemetry for a 24-bed unit.",
                  "Coordinated discharge planning with case managers and families."]),
        ],
        "education": [
            _edu("Bachelor of Science in Nursing (BSN)", "Northeastern University", "Boston, MA",
                 "2014", "2018"),
        ],
        "skills": ["Acute Care", "Telemetry", "IV Therapy", "Patient Education",
                   "Epic EHR", "ACLS", "BLS", "Care Coordination"],
        "test_hypothesis": "Parser handles a healthcare resume with certifications in the summary.",
        "intentional_complexity": "None — clean baseline.",
        "known_ambiguities": [],
        "acceptable_interpretations": [],
        "expected_pages": 1,
        "fields_to_inspect": ["name", "emails", "phoneNumbers", "workExperience", "education", "skills", "certifications"],
    },
    {
        "id": "A03", "category": "A", "difficulty": "baseline",
        "layout": "flow",
        "name": "Thomas Belanger",
        "title": "Financial Analyst",
        "email": "thomas.belanger@examplemail.com",
        "emails": ["thomas.belanger@examplemail.com"],
        "phone": "+1 (212) 555-0173",
        "location": "New York, NY",
        "links": {"LinkedIn": "linkedin.com/in/thomasbelanger"},
        "summary": (
            "Financial analyst with five years in corporate and investment banking. "
            "Strong in financial modelling, variance analysis and board reporting."
        ),
        "experience": [
            _exp("Financial Analyst", "Hudson Capital Partners", "New York, NY",
                 "Sep 2020", "Present", "2020-09", "present",
                 ["Build three-statement models supporting deals up to $400M.",
                  "Automated the monthly reporting pack, cutting close time by two days.",
                  "Present variance analysis to the CFO and department heads."]),
            _exp("Investment Banking Analyst", "Meridian Securities", "New York, NY",
                 "Jul 2018", "Aug 2020", "2018-07", "2020-08",
                 ["Supported M&A execution across six closed transactions.",
                  "Prepared pitch materials and comparable-company analyses."]),
        ],
        "education": [
            _edu("B.B.A. in Finance", "New York University, Stern School of Business", "New York, NY",
                 "2014", "2018"),
        ],
        "skills": ["Financial Modelling", "Valuation", "Excel", "Bloomberg Terminal",
                   "DCF Analysis", "Variance Analysis", "Power BI"],
        "test_hypothesis": "Parser extracts finance roles and B.B.A. education cleanly.",
        "intentional_complexity": "None — clean baseline.",
        "known_ambiguities": [],
        "acceptable_interpretations": [],
        "expected_pages": 1,
        "fields_to_inspect": ["name", "emails", "phoneNumbers", "workExperience", "education", "skills"],
    },
    {
        "id": "A04", "category": "A", "difficulty": "baseline",
        "layout": "flow",
        "name": "Sofia Reyes",
        "title": "Marketing Specialist",
        "email": "sofia.reyes@examplemail.com",
        "emails": ["sofia.reyes@examplemail.com"],
        "phone": "+1 (305) 555-0129",
        "location": "Miami, FL",
        "links": {"Portfolio": "sofiareyes.example.com"},
        "summary": (
            "Marketing specialist with six years running integrated campaigns across "
            "paid, social and email. Data-driven, with a record of measurable pipeline growth."
        ),
        "experience": [
            _exp("Marketing Specialist", "Coral Bay Brands", "Miami, FL",
                 "Jan 2021", "Present", "2021-01", "present",
                 ["Run multi-channel campaigns with an annual budget of $1.5M.",
                  "Grew marketing-qualified leads by 62% year over year.",
                  "Lead a quarterly content calendar across four product lines."]),
            _exp("Digital Marketing Coordinator", "Sunline Media", "Fort Lauderdale, FL",
                 "Mar 2018", "Dec 2020", "2018-03", "2020-12",
                 ["Managed paid social across Meta and LinkedIn.",
                  "Built automated email journeys, lifting open rates to 34%."]),
        ],
        "education": [
            _edu("B.A. in Communications", "University of Florida", "Gainesville, FL",
                 "2013", "2017"),
        ],
        "skills": ["Campaign Management", "SEO", "Google Analytics", "HubSpot",
                   "Paid Social", "Email Marketing", "Copywriting"],
        "test_hypothesis": "Parser handles a marketing resume with a portfolio link.",
        "intentional_complexity": "None — clean baseline.",
        "known_ambiguities": [],
        "acceptable_interpretations": [],
        "expected_pages": 1,
        "fields_to_inspect": ["name", "emails", "phoneNumbers", "websites", "workExperience", "education", "skills"],
    },
    {
        "id": "A05", "category": "A", "difficulty": "baseline",
        "layout": "flow",
        "name": "Marcus Lindqvist",
        "title": "Project Manager, PMP",
        "email": "marcus.lindqvist@examplemail.com",
        "emails": ["marcus.lindqvist@examplemail.com"],
        "phone": "+1 (206) 555-0164",
        "location": "Seattle, WA",
        "links": {"LinkedIn": "linkedin.com/in/marcuslindqvist"},
        "summary": (
            "PMP-certified project manager with nine years delivering cross-functional "
            "programs in software and infrastructure. Certified Scrum Master."
        ),
        "experience": [
            _exp("Senior Project Manager", "Cascade Digital", "Seattle, WA",
                 "Apr 2019", "Present", "2019-04", "present",
                 ["Deliver programs of up to $6M across engineering and operations.",
                  "Introduced a hybrid agile-waterfall model adopted org-wide.",
                  "Maintain an on-time delivery rate of 94% across 20+ projects."]),
            _exp("Project Manager", "Rainier Software", "Bellevue, WA",
                 "Jun 2015", "Mar 2019", "2015-06", "2019-03",
                 ["Managed a portfolio of client implementations.",
                  "Coached three teams through their first agile transitions."]),
        ],
        "education": [
            _edu("B.S. in Industrial Engineering", "University of Washington", "Seattle, WA",
                 "2010", "2014"),
        ],
        "skills": ["Project Management", "Agile", "Scrum", "Stakeholder Management",
                   "Risk Management", "Jira", "MS Project", "Budgeting"],
        "certifications": ["PMP (Project Management Professional)", "Certified ScrumMaster (CSM)"],
        "test_hypothesis": "Parser extracts PM roles and separates named certifications.",
        "intentional_complexity": "None — clean baseline.",
        "known_ambiguities": [],
        "acceptable_interpretations": [],
        "expected_pages": 1,
        "fields_to_inspect": ["name", "emails", "phoneNumbers", "workExperience", "education", "skills", "certifications"],
    },

    # ================== CATEGORY D — COMPLEX EMPLOYMENT HISTORY ==================
    {
        "id": "D01", "category": "D", "difficulty": "complex-history",
        "layout": "flow",
        "name": "Elena Visser",
        "title": "Data Scientist",
        "email": "elena.visser@examplemail.com",
        "emails": ["elena.visser@examplemail.com"],
        "phone": "+31 20 555 0197",
        "location": "Amsterdam, Netherlands",
        "links": {"LinkedIn": "linkedin.com/in/elenavisser"},
        "summary": (
            "Data scientist who, for an 11-month period, held two concurrent roles: a "
            "full-time position and a part-time university lectureship. Both are real and overlap by design."
        ),
        "experience": [
            _exp("Senior Data Scientist", "Tulip Analytics", "Amsterdam, Netherlands",
                 "Feb 2021", "Present", "2021-02", "present",
                 ["Lead forecasting models for a retail client network.",
                  "Own the experimentation platform used by three product teams."]),
            _exp("Part-Time Lecturer, Statistics (0.4 FTE)", "Amsterdam Data Institute", "Amsterdam, Netherlands",
                 "Sep 2022", "Jul 2023", "2022-09", "2023-07",
                 ["Taught an evening applied-statistics course for working professionals.",
                  "Held this role concurrently with the Tulip Analytics position."]),
            _exp("Data Analyst", "Canalpoint BV", "Utrecht, Netherlands",
                 "Jun 2018", "Jan 2021", "2018-06", "2021-01",
                 ["Built dashboards and automated weekly reporting."]),
        ],
        "education": [
            _edu("M.Sc. in Statistics", "Utrecht University", "Utrecht, Netherlands", "2016", "2018"),
            _edu("B.Sc. in Mathematics", "Utrecht University", "Utrecht, Netherlands", "2013", "2016"),
        ],
        "skills": ["Python", "R", "Machine Learning", "SQL", "Forecasting",
                   "Experimentation", "Teaching"],
        "test_hypothesis": "Parser represents two genuinely overlapping positions without merging or dropping one.",
        "intentional_complexity": "Sep 2022–Jul 2023 lectureship overlaps the ongoing Tulip Analytics role (both concurrent and valid).",
        "known_ambiguities": [],
        "acceptable_interpretations": [
            "Both roles listed as separate concurrent positions.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["workExperience", "workExperience[].startDate", "workExperience[].endDate"],
    },
    {
        "id": "D02", "category": "D", "difficulty": "complex-history",
        "layout": "flow",
        "name": "Kwame Mensah",
        "title": "Operations Leader",
        "email": "kwame.mensah@examplemail.com",
        "emails": ["kwame.mensah@examplemail.com"],
        "phone": "+1 (312) 555-0151",
        "location": "Chicago, IL",
        "links": {},
        "summary": (
            "Operations professional promoted three times within the same employer over "
            "seven years, from coordinator to director. A single continuous tenure, three distinct roles."
        ),
        "experience": [
            _exp("Director of Operations", "Lakeshore Logistics", "Chicago, IL",
                 "Jan 2022", "Present", "2022-01", "present",
                 ["Own P&L for a $40M regional distribution operation.",
                  "Promoted from Operations Manager in January 2022."]),
            _exp("Operations Manager", "Lakeshore Logistics", "Chicago, IL",
                 "Mar 2019", "Dec 2021", "2019-03", "2021-12",
                 ["Managed three warehouse teams totalling 60 staff.",
                  "Promoted from Operations Coordinator in March 2019."]),
            _exp("Operations Coordinator", "Lakeshore Logistics", "Chicago, IL",
                 "Jun 2017", "Feb 2019", "2017-06", "2019-02",
                 ["Coordinated inbound scheduling and carrier relationships."]),
        ],
        "education": [
            _edu("B.S. in Supply Chain Management", "University of Illinois", "Urbana-Champaign, IL",
                 "2012", "2016"),
        ],
        "skills": ["Operations Management", "Supply Chain", "P&L Ownership",
                   "Team Leadership", "Process Improvement", "SAP"],
        "test_hypothesis": "Parser recognises three promotions at one employer as one continuous tenure with distinct titles.",
        "intentional_complexity": "Same employer (Lakeshore Logistics) across all three roles; continuous Jun 2017–present.",
        "known_ambiguities": [],
        "acceptable_interpretations": [
            "Three separate positions all under one employer.",
            "One employer grouping with three title/date sub-entries.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["workExperience[].organization", "workExperience[].jobTitle", "workExperience[].startDate"],
    },
    {
        "id": "D03", "category": "D", "difficulty": "complex-history",
        "layout": "flow",
        "name": "Hana Takahashi",
        "title": "UX Designer & Freelance Illustrator",
        "email": "hana.takahashi@examplemail.com",
        "emails": ["hana.takahashi@examplemail.com"],
        "phone": "+1 (408) 555-0138",
        "location": "San Jose, CA",
        "links": {"Portfolio": "hanatakahashi.example.com"},
        "summary": (
            "UX designer holding a permanent full-time role while running an ongoing "
            "freelance illustration practice in parallel. Both are current and intentional."
        ),
        "experience": [
            _exp("Senior UX Designer", "Meadowlark Software", "San Jose, CA",
                 "May 2020", "Present", "2020-05", "present",
                 ["Lead design for a B2B analytics product used by 30k users.",
                  "Run the design-system working group."]),
            _exp("Freelance Illustrator (Self-Employed)", "Independent", "Remote",
                 "Jan 2019", "Present", "2019-01", "present",
                 ["Deliver editorial and brand illustration for recurring clients.",
                  "Operated continuously alongside full-time employment since 2020."]),
            _exp("UX Designer", "Pinecrest Digital", "Santa Clara, CA",
                 "Aug 2017", "Apr 2020", "2017-08", "2020-04",
                 ["Designed onboarding flows that improved activation by 20%."]),
        ],
        "education": [
            _edu("B.F.A. in Interaction Design", "California College of the Arts", "San Francisco, CA",
                 "2013", "2017"),
        ],
        "skills": ["UX Design", "Figma", "Design Systems", "Illustration",
                   "User Research", "Prototyping"],
        "test_hypothesis": "Parser keeps a concurrent permanent role and ongoing freelance practice as two current positions.",
        "intentional_complexity": "Two simultaneously-current roles (one permanent, one self-employed freelance).",
        "known_ambiguities": [],
        "acceptable_interpretations": [
            "Two current positions with overlapping present end dates.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["workExperience", "workExperience[].endDate"],
    },
    {
        "id": "D04", "category": "D", "difficulty": "complex-history",
        "layout": "flow",
        "name": "Oliver Grant",
        "title": "DevOps Engineer",
        "email": "oliver.grant@examplemail.com",
        "emails": ["oliver.grant@examplemail.com"],
        "phone": "+44 20 7946 0320",
        "location": "London, United Kingdom",
        "links": {"LinkedIn": "linkedin.com/in/olivergrant"},
        "summary": (
            "DevOps engineer currently employed with no explicit end date on the current "
            "role, stated only as the start month through the present."
        ),
        "experience": [
            _exp("DevOps Engineer", "Thamesworks Cloud", "London, UK",
                 "Oct 2021", "", "2021-10", "present",
                 ["Maintain CI/CD across 40+ repositories.",
                  "Current role; the resume deliberately states a start date with no end date."]),
            _exp("Systems Administrator", "Borough Systems", "London, UK",
                 "Feb 2018", "Sep 2021", "2018-02", "2021-09",
                 ["Administered Linux fleets and on-call rotations."]),
        ],
        "education": [
            _edu("B.Eng. in Software Engineering", "University of Manchester", "Manchester, UK",
                 "2013", "2017"),
        ],
        "skills": ["Docker", "Kubernetes", "Terraform", "AWS", "CI/CD", "Linux", "Prometheus"],
        "test_hypothesis": "Parser treats a missing end date on the current role as ongoing, not as an error or blank.",
        "intentional_complexity": "Current role shows start month only; no 'Present' label and no end date.",
        "known_ambiguities": [
            "Current role end date is absent (not the word 'Present').",
        ],
        "acceptable_interpretations": [
            "endDate null / ongoing / current.",
            "isCurrent = true.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["workExperience[0].endDate", "workExperience[0].isCurrent"],
    },
    {
        "id": "D05", "category": "D", "difficulty": "complex-history",
        "layout": "flow",
        "name": "Natalia Kowalski",
        "title": "Mechanical Engineer",
        "email": "natalia.kowalski@examplemail.com",
        "emails": ["natalia.kowalski@examplemail.com"],
        "phone": "+48 22 555 0176",
        "location": "Warsaw, Poland",
        "links": {},
        "summary": (
            "Mechanical engineer whose employment dates are written in unusual but "
            "unambiguous formats (quarters, ISO, and apostrophe-year) to test date normalisation."
        ),
        "experience": [
            _exp("Mechanical Engineer", "Vistula Industrial", "Warsaw, Poland",
                 "Q2 2021", "present", "2021-04", "present",
                 ["Design and validate mechanical assemblies for industrial pumps.",
                  "Start date written as 'Q2 2021' (second quarter = Apr 2021)."]),
            _exp("Design Engineer", "Baltic Manufacturing", "Gdansk, Poland",
                 "2018-03", "2021-03", "2018-03", "2021-03",
                 ["CAD design and tolerance analysis for marine components.",
                  "Dates written in ISO 'YYYY-MM' format."]),
            _exp("Graduate Engineer", "Carpathia Motors", "Krakow, Poland",
                 "Sep '16", "Feb '18", "2016-09", "2018-02",
                 ["Rotational graduate programme across three departments.",
                  "Dates written in apostrophe-year format (Sep '16)."]),
        ],
        "education": [
            _edu("M.Sc. in Mechanical Engineering", "Warsaw University of Technology", "Warsaw, Poland",
                 "2011", "2016"),
        ],
        "skills": ["SolidWorks", "FEA", "GD&T", "CAD", "Tolerance Analysis", "Manufacturing"],
        "test_hypothesis": "Parser normalises quarter, ISO and apostrophe-year date formats to real dates.",
        "intentional_complexity": "Three different valid date notations across three roles.",
        "known_ambiguities": [],
        "acceptable_interpretations": [
            "Q2 2021 interpreted as April 2021 (or anywhere Apr–Jun 2021).",
            "Sep '16 interpreted as September 2016.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["workExperience[].startDate", "workExperience[].endDate"],
    },

    # ===================== CATEGORY E — LAYOUT COMPLEXITY =====================
    {
        "id": "E01", "category": "E", "difficulty": "layout-complex",
        "layout": "two-column",
        "name": "Ravi Subramanian",
        "title": "Full-Stack Developer",
        "email": "ravi.subramanian@examplemail.com",
        "emails": ["ravi.subramanian@examplemail.com"],
        "phone": "+1 (737) 555-0119",
        "location": "Austin, TX",
        "links": {"LinkedIn": "linkedin.com/in/ravisubramanian", "GitHub": "github.com/ravisub"},
        "summary": (
            "Full-stack developer presented in a two-column layout. The left sidebar holds "
            "contact, skills and education; the main column holds experience."
        ),
        "experience": [
            _exp("Full-Stack Developer", "Lonestar Apps", "Austin, TX",
                 "Jul 2020", "Present", "2020-07", "present",
                 ["Build React front-ends and Node services for a SaaS platform.",
                  "Own the component library used across four product teams."]),
            _exp("Web Developer", "Hill Country Digital", "Austin, TX",
                 "Jun 2018", "Jun 2020", "2018-06", "2020-06",
                 ["Delivered client websites and e-commerce integrations."]),
        ],
        "education": [
            _edu("B.S. in Computer Science", "University of Texas at Austin", "Austin, TX",
                 "2014", "2018"),
        ],
        "skills": ["JavaScript", "TypeScript", "React", "Node.js", "GraphQL",
                   "PostgreSQL", "Docker", "AWS"],
        "test_hypothesis": "Parser reconstructs correct reading order from a two-column layout.",
        "intentional_complexity": "Two-column layout: sidebar (contact/skills/education) + main (experience).",
        "known_ambiguities": [],
        "acceptable_interpretations": [
            "Sidebar and main-column content both extracted and attributed to the right sections.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["name", "emails", "skills", "education", "workExperience"],
    },
    {
        "id": "E02", "category": "E", "difficulty": "layout-complex",
        "layout": "table",
        "name": "Grace Bennett",
        "title": "Accountant",
        "email": "grace.bennett@examplemail.com",
        "emails": ["grace.bennett@examplemail.com"],
        "phone": "+1 (614) 555-0145",
        "location": "Columbus, OH",
        "links": {},
        "summary": (
            "Accountant whose employment history is presented as a bordered table "
            "(Role | Employer | Dates) rather than as flowing paragraphs."
        ),
        "experience": [
            _exp("Senior Accountant", "Buckeye Financial Group", "Columbus, OH",
                 "Mar 2020", "Present", "2020-03", "present",
                 ["Owns month-end close for three subsidiaries."]),
            _exp("Staff Accountant", "Scioto Advisors", "Columbus, OH",
                 "Jul 2017", "Feb 2020", "2017-07", "2020-02",
                 ["Reconciliations, AP/AR, and audit support."]),
            _exp("Junior Accountant", "Olentangy Books", "Dublin, OH",
                 "Aug 2015", "Jun 2017", "2015-08", "2017-06",
                 ["Bookkeeping and payroll for small-business clients."]),
        ],
        "education": [
            _edu("B.S. in Accounting", "Ohio State University", "Columbus, OH", "2011", "2015"),
        ],
        "skills": ["GAAP", "Month-End Close", "QuickBooks", "Excel", "Audit", "Reconciliation"],
        "certifications": ["CPA (Certified Public Accountant)"],
        "test_hypothesis": "Parser extracts employment rows from a table structure.",
        "intentional_complexity": "Employment history rendered as a bordered table, not paragraphs.",
        "known_ambiguities": [],
        "acceptable_interpretations": [
            "Each table row mapped to a separate work-experience entry.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["workExperience", "workExperience[].jobTitle", "workExperience[].organization"],
    },
    {
        "id": "E03", "category": "E", "difficulty": "layout-complex",
        "layout": "scanned",
        "name": "Jonas Weber",
        "title": "Civil Engineer",
        "email": "jonas.weber@examplemail.com",
        "emails": ["jonas.weber@examplemail.com"],
        "phone": "+49 30 555 0162",
        "location": "Berlin, Germany",
        "links": {},
        "summary": (
            "Civil engineer. This resume is an image-only (scanned) PDF with NO selectable "
            "text layer — all content is a rasterised image, requiring OCR to extract."
        ),
        "experience": [
            _exp("Civil Engineer", "Spree Infrastructure GmbH", "Berlin, Germany",
                 "Apr 2019", "Present", "2019-04", "present",
                 ["Design and supervise bridge and roadworks projects.",
                  "Coordinate structural calculations with external consultants."]),
            _exp("Structural Engineer", "Rhein Bau AG", "Cologne, Germany",
                 "Sep 2015", "Mar 2019", "2015-09", "2019-03",
                 ["Performed load analysis for commercial buildings."]),
        ],
        "education": [
            _edu("Dipl.-Ing. in Civil Engineering", "Technical University of Berlin", "Berlin, Germany",
                 "2009", "2015"),
        ],
        "skills": ["AutoCAD", "Structural Analysis", "Eurocode", "Project Supervision", "Revit"],
        "test_hypothesis": "Parser must OCR an image-only PDF; tests OCR fallback and text-layer detection.",
        "intentional_complexity": "No embedded text layer at all — the page is a single rasterised image.",
        "known_ambiguities": [
            "Extraction depends entirely on the parser's OCR; fields may be degraded.",
        ],
        "acceptable_interpretations": [
            "OCR-based extraction with minor character errors is acceptable.",
            "If the parser has no OCR, near-empty extraction is the expected (documented) failure mode.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["rawText", "name", "workExperience"],
    },
    {
        "id": "E04", "category": "E", "difficulty": "layout-complex",
        "layout": "three-page",
        "name": "Amara Diallo",
        "title": "Research Scientist",
        "email": "amara.diallo@examplemail.com",
        "emails": ["amara.diallo@examplemail.com"],
        "phone": "+1 (919) 555-0183",
        "location": "Durham, NC",
        "links": {"LinkedIn": "linkedin.com/in/amaradiallo"},
        "summary": (
            "Research scientist with a three-page academic CV. Meaningful content appears on "
            "every page: experience, then publications, then grants and references."
        ),
        "experience": [
            _exp("Senior Research Scientist", "Triangle Biosciences", "Durham, NC",
                 "Jan 2020", "Present", "2020-01", "present",
                 ["Lead a lab of six investigating protein-folding kinetics.",
                  "Principal investigator on two NIH-funded studies.",
                  "Published 14 peer-reviewed papers since 2020."]),
            _exp("Postdoctoral Fellow", "Duke University", "Durham, NC",
                 "Aug 2016", "Dec 2019", "2016-08", "2019-12",
                 ["Developed assays for high-throughput screening.",
                  "Mentored four graduate students."]),
        ],
        "education": [
            _edu("Ph.D. in Biochemistry", "Duke University", "Durham, NC", "2011", "2016"),
            _edu("B.S. in Chemistry", "Spelman College", "Atlanta, GA", "2007", "2011"),
        ],
        "skills": ["Molecular Biology", "Protein Purification", "Mass Spectrometry",
                   "Python", "R", "Grant Writing", "Scientific Writing"],
        # Extra long-form content to genuinely fill three pages:
        "publications": [
            "Diallo, A. et al. (2024). Kinetic landscapes of chaperone-assisted folding. J. Mol. Biol.",
            "Diallo, A. & Chen, L. (2023). High-throughput assays for aggregation-prone variants. Nat. Methods.",
            "Diallo, A. et al. (2023). Thermodynamic signatures of misfolding intermediates. Biochemistry.",
            "Diallo, A. et al. (2022). A screening platform for small-molecule stabilisers. ACS Chem. Biol.",
            "Diallo, A. & Okonkwo, R. (2022). Revisiting two-state folding assumptions. Protein Science.",
            "Diallo, A. et al. (2021). Single-molecule FRET of folding transitions. PNAS.",
            "Diallo, A. et al. (2021). Data-driven models of chaperone binding. Bioinformatics.",
            "Diallo, A. et al. (2020). Review: the folding problem, forty years on. Annu. Rev. Biophys.",
        ],
        "grants": [
            "NIH R01 (Principal Investigator), 2022–2027, $1.9M — Mechanisms of chaperone selectivity.",
            "NSF CAREER (PI), 2021–2026, $0.6M — Single-molecule approaches to folding.",
            "Triangle Biosciences Internal Seed Grant, 2020, $75k.",
        ],
        "references": [
            "Prof. Laura Chen, Duke University — l.chen@example.edu",
            "Dr. Robert Okonkwo, Triangle Biosciences — r.okonkwo@example.com",
            "Prof. Maria Alvarez, UNC Chapel Hill — m.alvarez@example.edu",
        ],
        "test_hypothesis": "Parser reads a genuine multi-page CV and does not drop later-page content.",
        "intentional_complexity": "Three pages; experience p1, publications p2, grants/references p3.",
        "known_ambiguities": [],
        "acceptable_interpretations": [
            "Content from all three pages represented; publications may land in a generic section.",
        ],
        "expected_pages": 3,
        "fields_to_inspect": ["workExperience", "education", "publications", "rawText"],
    },
    {
        "id": "E05", "category": "E", "difficulty": "layout-complex",
        "layout": "unusual-order",
        "name": "Felix Andersson",
        "title": "Product Designer",
        "email": "felix.andersson@examplemail.com",
        "emails": ["felix.andersson@examplemail.com"],
        "phone": "+46 8 555 0190",
        "location": "Stockholm, Sweden",
        "links": {"Portfolio": "felixandersson.example.com"},
        "summary": (
            "Product designer in a visually clear but unconventional reading order: the "
            "name and contact sit at the bottom, experience at the top, in clearly labelled blocks."
        ),
        "experience": [
            _exp("Product Designer", "Nordic Interfaces", "Stockholm, Sweden",
                 "Mar 2021", "Present", "2021-03", "present",
                 ["Design end-to-end flows for a fintech mobile app.",
                  "Run usability testing and synthesise findings for the roadmap."]),
            _exp("UX/UI Designer", "Baltic Studio", "Malmo, Sweden",
                 "Jun 2018", "Feb 2021", "2018-06", "2021-02",
                 ["Designed interfaces for client web and mobile products."]),
        ],
        "education": [
            _edu("M.A. in Design", "Konstfack University", "Stockholm, Sweden", "2014", "2018"),
        ],
        "skills": ["Product Design", "Figma", "Prototyping", "Design Systems",
                   "Usability Testing", "Interaction Design"],
        "test_hypothesis": "Parser handles a clear but non-top-down reading order (header block placed low on the page).",
        "intentional_complexity": "Visually clear layout where the identity block is positioned below the experience block.",
        "known_ambiguities": [],
        "acceptable_interpretations": [
            "Name and contact extracted despite being placed lower on the page.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["name", "emails", "phoneNumbers", "workExperience"],
    },

    # ================ CATEGORY F — AMBIGUITY AND CONTRADICTIONS ================
    {
        "id": "F01", "category": "F", "difficulty": "ambiguous",
        "layout": "flow",
        "name": "Isabelle Moreau",
        "title": "HR Business Partner",
        "email": "isabelle.moreau@examplemail.com",
        "emails": ["isabelle.moreau@examplemail.com"],
        "phone": "+33 1 55 50 01 99",
        "location": "Paris, France",
        "links": {},
        "summary": (
            "HR business partner whose resume contains CONFLICTING employment dates for the "
            "same role: the experience section and a later summary line disagree. This is intentional."
        ),
        "experience": [
            _exp("HR Business Partner", "Seine Consulting Group", "Paris, France",
                 "Jan 2019", "Present", "2019-01", "present",
                 ["Partner with three business units on workforce planning.",
                  "NOTE: elsewhere in this document the start of this role is stated as 2020 — the dates deliberately conflict."]),
            _exp("HR Generalist", "Rive Gauche Media", "Paris, France",
                 "Sep 2015", "Dec 2018", "2015-09", "2018-12",
                 ["Managed recruitment and employee relations."]),
        ],
        "education": [
            _edu("Master in Human Resources", "Sorbonne University", "Paris, France", "2011", "2015"),
        ],
        "skills": ["Talent Management", "Employee Relations", "Workforce Planning", "HRIS", "Recruitment"],
        # A contradicting reference to the same role's start date, surfaced in the summary block:
        "conflict_note": "Current role (HR Business Partner) start date stated as Jan 2019 in Experience but as 2020 in the profile line.",
        "test_hypothesis": "Parser must not silently pick one of two conflicting start dates as certain truth.",
        "intentional_complexity": "Same role has two different stated start dates (2019 vs 2020).",
        "known_ambiguities": [
            "HR Business Partner start date is stated as both Jan 2019 and 2020.",
        ],
        "acceptable_interpretations": [
            "Either 2019 or 2020 extracted, ideally with low confidence or a flagged conflict.",
            "NOT acceptable: inventing a third date.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["workExperience[0].startDate"],
    },
    {
        "id": "F02", "category": "F", "difficulty": "ambiguous",
        "layout": "flow",
        "name": "Daniel Park",
        "title": "Sales Manager",
        "email": "daniel.park@examplemail.com",
        "emails": ["daniel.park@examplemail.com", "d.park.work@examplemail.com"],
        "phone": "+1 (213) 555-0147",
        "location": "Los Angeles, CA",
        "links": {},
        "summary": (
            "Sales manager who lists TWO different email addresses (a personal and a work "
            "address). Both are intentional; neither is a typo."
        ),
        "experience": [
            _exp("Sales Manager", "Pacific Crest Solutions", "Los Angeles, CA",
                 "Feb 2020", "Present", "2020-02", "present",
                 ["Lead a team of eight account executives.",
                  "Grew regional revenue 28% year over year."]),
            _exp("Account Executive", "Sunset Systems", "Los Angeles, CA",
                 "Jun 2016", "Jan 2020", "2016-06", "2020-01",
                 ["Closed mid-market SaaS deals across the West region."]),
        ],
        "education": [
            _edu("B.A. in Business Administration", "UCLA", "Los Angeles, CA", "2012", "2016"),
        ],
        "skills": ["B2B Sales", "Account Management", "Salesforce", "Forecasting", "Negotiation"],
        "test_hypothesis": "Parser captures BOTH email addresses rather than only one.",
        "intentional_complexity": "Two distinct, valid email addresses in the contact block.",
        "known_ambiguities": [
            "Which email is 'primary' is not stated.",
        ],
        "acceptable_interpretations": [
            "Both emails extracted.",
            "Either email treated as primary is acceptable; dropping one is a miss.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["emails"],
    },
    {
        "id": "F03", "category": "F", "difficulty": "ambiguous",
        "layout": "flow",
        "name": "Lucia Romano",
        "title": "Communications Lead",
        "email": "lucia.romano@examplemail.com",
        "emails": ["lucia.romano@examplemail.com"],
        "phone": "+39 06 555 0121",
        "location": "Rome, Italy",
        "links": {},
        "summary": (
            "Communications professional whose single continuous employment period is "
            "described with TWO different job titles, reflecting a mid-tenure title change."
        ),
        "experience": [
            _exp("Communications Lead (formerly Communications Manager)", "Tiber Media House", "Rome, Italy",
                 "Mar 2019", "Present", "2019-03", "present",
                 ["Same continuous role since Mar 2019; title changed from 'Communications "
                  "Manager' to 'Communications Lead' in 2022 with no break in employment.",
                  "Own external communications and media relations."]),
            _exp("PR Specialist", "Forum Communications", "Rome, Italy",
                 "Sep 2015", "Feb 2019", "2015-09", "2019-02",
                 ["Managed press releases and media lists."]),
        ],
        "education": [
            _edu("B.A. in Communication Studies", "Sapienza University of Rome", "Rome, Italy", "2011", "2015"),
        ],
        "skills": ["Public Relations", "Media Relations", "Content Strategy", "Crisis Communications"],
        "test_hypothesis": "Parser handles one period with two titles without splitting it into two employers or losing a title.",
        "intentional_complexity": "Two job titles ('Communications Manager' and 'Communications Lead') for one continuous Mar 2019–present tenure.",
        "known_ambiguities": [
            "Whether to record one position with a title change, or two sub-positions, is open.",
        ],
        "acceptable_interpretations": [
            "One continuous position, either title recorded.",
            "Two sub-entries sharing the employer and adjacent dates.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["workExperience[0].jobTitle", "workExperience[0].startDate"],
    },
    {
        "id": "F04", "category": "F", "difficulty": "ambiguous",
        "layout": "flow",
        "name": "Omar Haddad",
        "title": "Software Engineer",
        "email": "omar.haddad@examplemail.com",
        "emails": ["omar.haddad@examplemail.com"],
        "phone": "+1 (647) 555-0115",
        "location": "Toronto, Canada",
        "links": {"GitHub": "github.com/omarhaddad"},
        "summary": (
            "Software engineer with NO dedicated skills section. Every technical skill is "
            "mentioned only inside project and job descriptions, to test skill inference."
        ),
        "experience": [
            _exp("Software Engineer", "Maple Grid Technologies", "Toronto, Canada",
                 "May 2020", "Present", "2020-05", "present",
                 ["Rebuilt the notifications service in Rust, cutting memory use by half.",
                  "Introduced Kafka-based event streaming for order processing.",
                  "Containerised the stack with Docker and deployed on Kubernetes."]),
            _exp("Junior Developer", "Lakeview Software", "Toronto, Canada",
                 "Aug 2018", "Apr 2020", "2018-08", "2020-04",
                 ["Wrote Python data pipelines feeding a PostgreSQL warehouse.",
                  "Built internal dashboards with React and TypeScript."]),
        ],
        "education": [
            _edu("B.A.Sc. in Computer Engineering", "University of Toronto", "Toronto, Canada", "2014", "2018"),
        ],
        "skills": [],  # intentionally empty section
        # The skills a good parser SHOULD infer from the bullets above:
        "skills_embedded_in_experience": ["Rust", "Kafka", "Docker", "Kubernetes",
                                          "Python", "PostgreSQL", "React", "TypeScript"],
        "test_hypothesis": "Parser infers skills from project/job descriptions when no skills section exists.",
        "intentional_complexity": "No skills section; skills appear only inside experience bullets.",
        "known_ambiguities": [
            "Whether the parser infers skills from prose is implementation-dependent.",
        ],
        "acceptable_interpretations": [
            "Skills list populated from inferred terms (Rust, Kafka, Docker, etc.).",
            "Empty skills list is a documented miss, not a contradiction.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["skills", "rawText"],
    },
    {
        "id": "F05", "category": "F", "difficulty": "ambiguous",
        "layout": "flow",
        "name": "Chloe Fitzgerald",
        "title": "Paralegal",
        "email": "chloe.fitzgerald@examplemail.com",
        "emails": ["chloe.fitzgerald@examplemail.com"],
        "phone": "+1 (773) 555-0158",
        "location": "Chicago, IL",
        "links": {},
        "summary": (
            "Paralegal whose education section lists a law degree explicitly marked as "
            "INCOMPLETE (in progress / not conferred), to test handling of unfinished qualifications."
        ),
        "experience": [
            _exp("Senior Paralegal", "Harbor & Vance LLP", "Chicago, IL",
                 "Jan 2019", "Present", "2019-01", "present",
                 ["Manage litigation documents and e-discovery for complex cases.",
                  "Draft pleadings and coordinate with outside counsel."]),
            _exp("Paralegal", "Lakeside Legal", "Chicago, IL",
                 "Jul 2016", "Dec 2018", "2016-07", "2018-12",
                 ["Prepared case files and managed court filings."]),
        ],
        "education": [
            _edu("J.D. (Juris Doctor) — INCOMPLETE, expected 2026", "DePaul University College of Law",
                 "Chicago, IL", "2023", "", "Part-time; degree not yet conferred (in progress)."),
            _edu("B.A. in Political Science", "Loyola University Chicago", "Chicago, IL", "2012", "2016"),
        ],
        "skills": ["Legal Research", "E-Discovery", "Litigation Support", "Westlaw", "Case Management"],
        "test_hypothesis": "Parser marks an in-progress degree as incomplete rather than as completed.",
        "intentional_complexity": "J.D. explicitly marked incomplete/in-progress with no conferral date.",
        "known_ambiguities": [
            "Whether the J.D. is counted as an attained qualification is the point of the test.",
        ],
        "acceptable_interpretations": [
            "J.D. recorded as in-progress / incomplete / no end date.",
            "NOT acceptable: J.D. recorded as a completed, conferred degree.",
        ],
        "expected_pages": 1,
        "fields_to_inspect": ["education", "education[].isCurrent", "education[].endDate"],
    },
]


# Convenience lookups -------------------------------------------------------
BY_ID = {c["id"]: c for c in CANDIDATES}
CATEGORIES = ["A", "D", "E", "F"]


def by_category(cat):
    return [c for c in CANDIDATES if c["category"] == cat]


if __name__ == "__main__":
    # Quick integrity check when run directly.
    assert len(CANDIDATES) == 20, f"expected 20 candidates, got {len(CANDIDATES)}"
    ids = [c["id"] for c in CANDIDATES]
    assert len(set(ids)) == 20, "duplicate candidate ids"
    for cat in CATEGORIES:
        n = len(by_category(cat))
        assert n == 5, f"category {cat} has {n} candidates, expected 5"
    print(f"OK: {len(CANDIDATES)} candidates, 5 per category {CATEGORIES}")
