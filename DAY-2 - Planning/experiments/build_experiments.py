#!/usr/bin/env python3
"""
build_experiments.py — turn the 300-row ResumeGuard taxonomy (3 CSVs, 100 each)
into 300 realistic synthetic resume PDFs for parsing through the Affinda Sandbox.

One row -> one one-page resume that embeds that row's `exact_source_line` verbatim,
in the row's assigned location/layout, surrounded by ordinary resume content so the
parser behaves normally. We do NOT score here and we do NOT call Affinda — we only
build the PDFs + the ground-truth + manifest so the returned JSON can be scored
reproducibly later (exactly like yesterday's rounds).

Inputs  : ../taxonomy/{education,certification,skill_claim}_*_100.csv
Outputs : experiments/<issue>/resumes/<ID>.pdf
          experiments/<issue>/ground_truth_<issue>.json
          experiments/<issue>/manifest_<issue>.csv
          experiments/_build_report.json

Run     : python build_experiments.py            (all 300)
          python build_experiments.py E001 C040  (named subset)
"""
from __future__ import annotations

import csv
import json
import os
import sys

import fitz  # PyMuPDF, verification only
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable, KeepTogether,
)

HERE = os.path.dirname(os.path.abspath(__file__))
TAXO = os.path.normpath(os.path.join(HERE, "..", "taxonomy"))
REFERENCE_DATE = "2026-11-13"

PAGE_W, PAGE_H = LETTER
INK = colors.HexColor("#1b1b20"); GREY = colors.HexColor("#555560")
RULE = colors.HexColor("#bcc0c7"); ACCENT = colors.HexColor("#234a7d")
SIDEBG = colors.HexColor("#eef1f5")

ISSUES = {
    "education":     ("education_status_100.csv",      "education_status"),
    "certification": ("certification_status_100.csv",  "certification_status"),
    "skill":         ("skill_claim_strength_100.csv",  "skill_claim_strength"),
}

# ----- identity pools (kept unique per resume so the parser never dedupes) ----
FIRST = ["Ada","Noah","Mia","Leo","Zara","Ivan","Priya","Owen","Lena","Omar",
         "Nina","Hugo","Tara","Finn","Ruby","Cole","Esme","Jude","Anya","Theo",
         "Isla","Rhys","Maya","Dean","Vera","Kian","Rosa","Bram","Elsa","Niko",
         "Lola","Seth","Opal","Gage","Wren","Axel","Nova","Pax","Remy","Suri"]
LAST = ["Mercer","Vance","Okafor","Castellano","Nguyen","Barros","Halloran","Rhodes",
        "Fenwick","Delgado","Sorensen","Albright","Kowalski","Montoya","Ashby","Petrov",
        "Udoka","Larsen","Beaumont","Caldwell","Esposito","Farrow","Gallardo","Hearst",
        "Ireland","Jessup","Kirby","Lindqvist","Mathison","Novak","Ortega","Paxton",
        "Quint","Rasmussen","Sato","Trevino","Ulrich","Varga","Whitlock","Yardley"]
TITLES = ["Software Engineer","Project Coordinator","Registered Professional","Data Analyst",
          "Operations Specialist","Network Engineer","Clinical Associate","Finance Associate",
          "Security Analyst","Mechanical Technician"]
CITIES = ["Sydney, NSW","Melbourne, VIC","Brisbane, QLD","Perth, WA","Adelaide, SA"]
NEUTRAL_SKILLS = ["Git","Linux","Agile","REST APIs","Jira","Communication"]
LAYOUTS = ["flow", "bulleted", "table", "two_column"]


def ident(i: int):
    f = FIRST[i % len(FIRST)]; l = LAST[(i * 7 + i // len(LAST)) % len(LAST)]
    name = f"{f} {l}"
    email = f"{f.lower()}.{l.lower()}{i:03d}@examplemail.com"
    return {"name": name, "email": email,
            "title": TITLES[i % len(TITLES)],
            "phone": f"+61 2 55{i % 100:02d} {1000 + i % 9000:04d}",
            "location": CITIES[i % len(CITIES)]}


# --------------------------------------------------------------------------- #
# styles
# --------------------------------------------------------------------------- #
def styles():
    ss = getSampleStyleSheet()
    S = lambda n, **k: ParagraphStyle(n, parent=ss["Normal"], fontName="Helvetica", **k)
    return {
        "name": ParagraphStyle("name", parent=ss["Title"], fontName="Helvetica-Bold",
                               fontSize=19, leading=23, textColor=INK, spaceAfter=2, alignment=0),
        "title": S("title", fontSize=11.5, leading=14, textColor=ACCENT, spaceAfter=3),
        "contact": S("contact", fontSize=9, leading=12, textColor=GREY),
        "section": ParagraphStyle("section", parent=ss["Heading2"], fontName="Helvetica-Bold",
                                  fontSize=11, leading=14, textColor=ACCENT, spaceBefore=9, spaceAfter=2),
        "sidehead": ParagraphStyle("sidehead", parent=ss["Heading2"], fontName="Helvetica-Bold",
                                   fontSize=10, leading=13, textColor=ACCENT, spaceBefore=8, spaceAfter=2),
        "role": ParagraphStyle("role", parent=ss["Normal"], fontName="Helvetica-Bold",
                               fontSize=10.5, leading=13, textColor=INK),
        "dates": S("dates", fontSize=9, leading=13, textColor=GREY, alignment=2),
        "org": ParagraphStyle("org", parent=ss["Normal"], fontName="Helvetica-Oblique",
                              fontSize=9.5, leading=12, textColor=GREY, spaceAfter=1),
        "body": S("body", fontSize=9.5, leading=13, textColor=INK),
        "bullet": S("bullet", fontSize=9.5, leading=12.5, textColor=INK),
        "side": S("side", fontSize=9, leading=12.5, textColor=INK),
    }


def _sec(t, st, side=False):
    h = st["sidehead" if side else "section"]
    return [Paragraph(t, h), HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=4)]


def _role_row(title, dates, st):
    t = Table([[Paragraph(title, st["role"]), Paragraph(dates, st["dates"])]],
              colWidths=[None, 1.6 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")] +
               [(p, (0, 0), (-1, -1), 0) for p in ("LEFTPADDING", "RIGHTPADDING", "TOPPADDING", "BOTTOMPADDING")]))
    return t


# --------------------------------------------------------------------------- #
# generic "entry section" renderer in 4 layout styles.
# entries: list of dicts {main, sub, note, date}
# --------------------------------------------------------------------------- #
def render_entries(title, entries, layout, st, side=False):
    flow = _sec(title, st, side=side)
    if layout == "bulleted":
        items = []
        for e in entries:
            txt = e["main"]
            if e.get("sub"):
                txt += f" — {e['sub']}"
            if e.get("date"):
                txt += f" ({e['date']})"
            if e.get("note"):
                txt += f". {e['note']}"
            items.append(ListItem(Paragraph(txt, st["bullet"]), leftIndent=10))
        flow.append(ListFlowable(items, bulletType="bullet", start="•",
                                 leftIndent=12, bulletColor=GREY, spaceBefore=1))
    elif layout == "table":
        data = []
        for e in entries:
            left = e["main"] + (f"<br/><i>{e['sub']}</i>" if e.get("sub") else "")
            if e.get("note"):
                left += f"<br/>{e['note']}"
            data.append([Paragraph(left, st["body"]), Paragraph(e.get("date", ""), st["dates"])])
        t = Table(data, colWidths=[None, 1.5 * inch])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (0, -1), 0)]))
        flow.append(t)
    else:  # flow (and default) — also used inside the two-column right pane
        for e in entries:
            if e.get("date") and not side:
                flow.append(_role_row(e["main"], e["date"], st))
            else:
                flow.append(Paragraph(e["main"] + (f"  ({e['date']})" if e.get("date") else ""),
                                      st["side" if side else "role"]))
            if e.get("sub"):
                flow.append(Paragraph(e["sub"], st["org"]))
            if e.get("note"):
                flow.append(Paragraph(e["note"], st["body"]))
            flow.append(Spacer(1, 4))
    return flow


def _experience_block(exp, st):
    flow = _sec("EXPERIENCE", st)
    flow.append(_role_row(exp["title"], exp["date_display"], st))
    flow.append(Paragraph(exp["org"] + f"  ·  {exp['location']}", st["org"]))
    items = [ListItem(Paragraph(b, st["bullet"]), leftIndent=10) for b in exp["bullets"]]
    flow.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=12,
                             bulletColor=GREY, spaceBefore=1))
    flow.append(Spacer(1, 4))
    return flow


def _skills_block(skills, st, side=False):
    flow = _sec("SKILLS", st, side=side)
    if side:
        for s in skills:
            flow.append(Paragraph(s, st["side"]))
    else:
        flow.append(Paragraph("  ·  ".join(skills), st["body"]))
    return flow


# --------------------------------------------------------------------------- #
# document assembly
# --------------------------------------------------------------------------- #
def build_pdf(c, path):
    st = styles()
    two_col = (c["layout"] == "two_column")

    header = [Paragraph(c["name"], st["name"]), Paragraph(c["title"], st["title"])]
    contact = "  |  ".join([c["email"], c["phone"], c["location"]])

    if two_col:
        # left sidebar: contact + skills ; right: summary, experience, probe section
        left = [Paragraph("CONTACT", st["sidehead"]),
                HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=4),
                Paragraph(c["email"], st["side"]), Paragraph(c["phone"], st["side"]),
                Paragraph(c["location"], st["side"]), Spacer(1, 4)]
        left += _skills_block(c["skills"], st, side=True)
        right = header + [Spacer(1, 2)]
        if c.get("summary"):
            right += _sec("SUMMARY", st) + [Paragraph(c["summary"], st["body"])]
        right += _experience_block(c["experience"], st)
        for sect in c["sections"]:            # probe-bearing + any extra sections
            right += render_entries(sect["title"], sect["entries"], "flow", st)
        lt = Table([[left, right]], colWidths=[2.15 * inch, None])
        lt.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (0, 0), SIDEBG),
            ("LEFTPADDING", (0, 0), (0, 0), 8), ("RIGHTPADDING", (0, 0), (0, 0), 8),
            ("TOPPADDING", (0, 0), (0, 0), 8),
            ("LEFTPADDING", (1, 0), (1, 0), 12)]))
        story = [lt]
    else:
        story = header + [Paragraph(contact, st["contact"]),
                          Spacer(1, 4), HRFlowable(width="100%", thickness=1, color=RULE, spaceAfter=4)]
        if c.get("summary"):
            story += _sec("SUMMARY", st) + [Paragraph(c["summary"], st["body"])]
        story += _experience_block(c["experience"], st)
        for sect in c["sections"]:
            story += render_entries(sect["title"], sect["entries"], sect.get("layout", "flow"), st)
        if c.get("extra_skills_section"):
            story += _skills_block(c["skills"], st)

    SimpleDocTemplate(path, pagesize=LETTER, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                      topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                      title=c["id"], author=c["name"]).build(story)


# --------------------------------------------------------------------------- #
# composers: CSV row -> candidate dict
# --------------------------------------------------------------------------- #
def _split_multi(line):
    return [p.strip() for p in line.split("||") if p.strip()]


def compose_education(row, idn):
    entries = [{"main": p} for p in _split_multi(row["exact_source_line"])]
    return {
        "id": row["test_id"], "layout": row["layout"], **idn,
        "summary": f"{idn['title']} with academic background listed below.",
        "experience": {"title": idn["title"], "org": "Brightwave Labs",
                       "location": idn["location"], "date_display": "2019 – Present",
                       "bullets": ["Delivered day-to-day responsibilities for the team."]},
        "skills": NEUTRAL_SKILLS[:4],
        "sections": [{"title": "EDUCATION", "entries": entries, "layout": row["layout"]}],
        "extra_skills_section": True,
        "probe_line": row["exact_source_line"],
    }


def compose_certification(row, idn):
    entries = [{"main": p} for p in _split_multi(row["exact_source_line"])]
    return {
        "id": row["test_id"], "layout": row["layout"], **idn,
        "summary": f"{idn['title']} holding the credentials listed below.",
        "experience": {"title": idn["title"], "org": "Northgate Services",
                       "location": idn["location"], "date_display": "2017 – Present",
                       "bullets": ["Carried out duties relevant to the role."]},
        "skills": NEUTRAL_SKILLS[:4],
        "sections": [
            {"title": "EDUCATION", "entries": [{"main": "B.S. in Applied Science",
                                                "sub": "Summit State University", "date": "2015"}],
             "layout": "flow"},
            {"title": "CERTIFICATIONS", "entries": entries, "layout": row["layout"]},
        ],
        "extra_skills_section": True,
        "probe_line": row["exact_source_line"],
    }


def compose_skill(row, idn):
    """Place the exact claim line in the location the taxonomy specifies."""
    loc = row["location"]; line = row["exact_source_line"]
    base = dict(id=row["test_id"], layout=row["layout"], **idn,
                skills=list(NEUTRAL_SKILLS[:4]),
                experience={"title": idn["title"], "org": "Brightwave Labs",
                            "location": idn["location"], "date_display": "2018 – Present",
                            "bullets": ["Build and maintain production systems."]},
                sections=[{"title": "EDUCATION",
                           "entries": [{"main": "B.S. in Computer Science",
                                        "sub": "State University", "date": "2014"}],
                           "layout": "flow"}],
                extra_skills_section=True, probe_line=line)
    summary = f"{idn['title']}."
    if loc == "skills_list":
        base["skills"] = NEUTRAL_SKILLS[:3] + [line]
    elif loc == "summary_prose":
        summary = f"{idn['title']}. {line}."
    elif loc == "experience_bullet":
        base["experience"]["bullets"] = ["Build and maintain production systems.", line]
    elif loc == "proficiency_table":
        base["sections"].insert(0, {"title": "TECHNICAL PROFICIENCY",
                                    "entries": [{"main": line}], "layout": "table"})
    elif loc == "parenthetical":
        summary = f"{idn['title']} ({line})."
    base["summary"] = summary
    return base


COMPOSERS = {"education": compose_education,
             "certification": compose_certification,
             "skill": compose_skill}


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #
def load_rows(issue):
    csv_name, _ = ISSUES[issue]
    with open(os.path.join(TAXO, csv_name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def verify(path, probe_line):
    d = fitz.open(path); pages = d.page_count
    text = " ".join("\n".join(p.get_text() for p in d).split()); d.close()
    checkable = probe_line.replace("||", " ")
    words = [w for w in checkable.split() if len(w) > 2]
    missing = [w for w in words if w not in text]
    return pages, len(missing) == 0, missing[:5]


def main():
    only = set(sys.argv[1:])
    report = {}
    for issue, (csv_name, issue_tag) in ISSUES.items():
        outdir = os.path.join(HERE, issue)
        resdir = os.path.join(outdir, "resumes")
        os.makedirs(resdir, exist_ok=True)
        rows = load_rows(issue)
        gt = {"_meta": {"reference_date": REFERENCE_DATE, "issue": issue_tag,
                        "note": "Expectations come from synthetic source taxonomy, not parser output."}}
        manifest = []
        built = 0
        for i, row in enumerate(rows):
            tid = row["test_id"]
            if only and tid not in only:
                continue
            idn = ident(i)
            if "layout" not in row or not row["layout"]:
                row["layout"] = LAYOUTS[i % len(LAYOUTS)]  # skills have no layout axis -> cycle for coverage
            c = COMPOSERS[issue](row, idn)
            path = os.path.join(resdir, f"{tid}.pdf")
            try:
                build_pdf(c, path)
                pages, ok, missing = verify(path, c["probe_line"])
                built += 1
                report[tid] = {"id": tid, "issue": issue, "built": True, "pages": pages,
                               "layout": row["layout"], "probe_ok": ok, "missing": missing}
                flag = "" if pages == 1 else f"  <-- {pages}pp"
                flag += "" if ok else f"  <-- PROBE MISSING {missing}"
                print(f"  {tid} [{issue:<13}] {row.get('status_category') or row.get('validity_category') or row.get('claim_strength'):<22} {row['layout']:<11}{flag}")
            except Exception as e:  # noqa
                report[tid] = {"id": tid, "issue": issue, "built": False, "error": repr(e)}
                print(f"  {tid} FAILED: {e!r}")
                continue
            # ground truth row = every CSV field + identity + render facts
            gt[tid] = {**row, "filename": f"{tid}.pdf",
                       "candidate_identity": {"name": idn["name"], "email": idn["email"],
                                              "title": idn["title"]},
                       "rendered_layout": row["layout"]}
            manifest.append({
                "test_id": tid, "filename": f"{tid}.pdf", "issue": issue_tag,
                "category": row.get("status_category") or row.get("validity_category") or row.get("claim_strength"),
                "layout": row["layout"], "realism": row["realism"],
                "is_control": row.get("is_control", ""),
                "is_distractor": row.get("is_distractor", ""),
                "exact_source_line": row["exact_source_line"],
                "failure_if": row["failure_if"],
            })
        if manifest:
            json.dump(gt, open(os.path.join(outdir, f"ground_truth_{issue}.json"), "w",
                               encoding="utf-8"), indent=2, ensure_ascii=False)
            with open(os.path.join(outdir, f"manifest_{issue}.csv"), "w", newline="",
                      encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(manifest[0].keys()))
                w.writeheader(); w.writerows(manifest)
            print(f"[{issue}] built {built}/{len(rows)} -> {resdir}")
    json.dump(report, open(os.path.join(HERE, "_build_report.json"), "w",
                           encoding="utf-8"), indent=2, ensure_ascii=False)
    ok = sum(1 for r in report.values() if r.get("built"))
    probe = sum(1 for r in report.values() if r.get("probe_ok"))
    print(f"\nTOTAL built {ok}/{len(report)}  |  probe-text verified {probe}/{ok}")


if __name__ == "__main__":
    main()
