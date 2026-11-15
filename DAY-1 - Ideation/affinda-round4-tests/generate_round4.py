"""
generate_round3.py — Build the 48 round-4 probe resumes (R301-R348).

ReportLab Platypus (flow / table / two-column), Unicode-safe, dynamic layout.
Renders the extra probe content each category needs: negation wording, a work-
authorisation line, employment-type labels, and a certifications section.
Writes resumes/<ID>.pdf and _build_report.json.

Usage:  python generate_round3.py [R301 ...]
"""
from __future__ import annotations

import json
import os
import sys

import fitz  # PyMuPDF (verification only)
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable, KeepTogether,
)

from round4_candidates import CANDIDATES, BY_ID

HERE = os.path.dirname(os.path.abspath(__file__))
RESUMES = os.path.join(HERE, "resumes")
os.makedirs(RESUMES, exist_ok=True)
PAGE_W, PAGE_H = LETTER
INK = colors.HexColor("#1b1b20"); GREY = colors.HexColor("#555560")
RULE = colors.HexColor("#bcc0c7"); ACCENT = colors.HexColor("#234a7d")


def _styles():
    ss = getSampleStyleSheet()
    S = lambda n, **k: ParagraphStyle(n, parent=ss["Normal"], fontName="Helvetica", **k)
    return {
        "name": ParagraphStyle("name", parent=ss["Title"], fontName="Helvetica-Bold",
                               fontSize=20, leading=24, textColor=INK, spaceAfter=2, alignment=0),
        "title": S("title", fontSize=12, leading=15, textColor=ACCENT, spaceAfter=3),
        "contact": S("contact", fontSize=9, leading=12, textColor=GREY),
        "wa": S("wa", fontSize=9, leading=12, textColor=colors.HexColor("#7a3b00")),
        "section": ParagraphStyle("section", parent=ss["Heading2"], fontName="Helvetica-Bold",
                                  fontSize=11, leading=14, textColor=ACCENT, spaceBefore=10, spaceAfter=2),
        "role": ParagraphStyle("role", parent=ss["Normal"], fontName="Helvetica-Bold",
                               fontSize=10.5, leading=13, textColor=INK),
        "dates": S("dates", fontSize=9, leading=13, textColor=GREY, alignment=2),
        "org": ParagraphStyle("org", parent=ss["Normal"], fontName="Helvetica-Oblique",
                              fontSize=9.5, leading=12, textColor=GREY, spaceAfter=1),
        "tag": ParagraphStyle("tag", parent=ss["Normal"], fontName="Helvetica-Oblique",
                              fontSize=9, leading=12, textColor=colors.HexColor("#7a3b00"), spaceAfter=1),
        "body": S("body", fontSize=9.5, leading=13, textColor=INK),
        "bullet": S("bullet", fontSize=9.5, leading=12.5, textColor=INK),
        "small": S("small", fontSize=9, leading=12, textColor=INK),
    }


def _sec(t, st):
    return [Paragraph(t, st["section"]), HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=4)]


def _role_row(title, dates, st):
    t = Table([[Paragraph(title, st["role"]), Paragraph(dates, st["dates"])]], colWidths=[None, 1.7 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")] +
                          [(p, (0, 0), (-1, -1), 0) for p in ("LEFTPADDING", "RIGHTPADDING", "TOPPADDING", "BOTTOMPADDING")]))
    return t


def _header(c, st):
    flow = [Paragraph(c["name"], st["name"]), Paragraph(c["title"], st["title"])]
    bits = [c["email"], c.get("phone", ""), c.get("location", "")]
    flow.append(Paragraph("  |  ".join(b for b in bits if b), st["contact"]))
    # work-authorisation line (labelled), except the ambiguous non-statement which stays unlabelled in summary
    wa = c.get("work_auth")
    if wa and "AMBIGUOUS" not in c["controlled"]:
        flow.append(Paragraph(f"Work Authorization: {wa}", st["wa"]))
    flow += [Spacer(1, 4), HRFlowable(width="100%", thickness=1, color=RULE, spaceAfter=4)]
    return flow


def _summary(c, st):
    summ = c.get("summary", "")
    wa = c.get("work_auth")
    if wa and "AMBIGUOUS" in c["controlled"]:   # R316: blend the phrase in naturally, unlabelled
        summ = (summ + " " + wa).strip()
    return _sec("SUMMARY", st) + [Paragraph(summ, st["body"])] if summ else []


def _experience(c, st):
    flow = _sec("EXPERIENCE", st)
    for e in c["experience"]:
        dd = e["date_display"]
        short = len(dd) <= 22
        block = [_role_row(e["title"], dd, st) if short else Paragraph(e["title"], st["role"])]
        org = e["org"] + (f"  ·  {e['location']}" if e.get("location") else "")
        block.append(Paragraph(org, st["org"]))
        if not short:
            block.append(Paragraph(dd, st["org"]))
        if e.get("emp_type_label"):
            block.append(Paragraph(f"Employment type: {e['emp_type_label']}", st["tag"]))
        if e.get("bullets"):
            items = [ListItem(Paragraph(b, st["bullet"]), leftIndent=10) for b in e["bullets"]]
            block.append(ListFlowable(items, bulletType="bullet", start="•",
                                      leftIndent=12, bulletColor=GREY, spaceBefore=1))
        block.append(Spacer(1, 6))
        flow.append(KeepTogether(block))
    return flow


def _education(c, st):
    flow = _sec("EDUCATION", st)
    for ed in c["education"]:
        flow.append(_role_row(ed["degree"], ed["date_display"], st))
        flow.append(Paragraph(ed["institution"] + (f"  ·  {ed['location']}" if ed.get("location") else ""), st["org"]))
        if ed.get("note"):
            flow.append(Paragraph(ed["note"], st["tag"]))
        flow.append(Spacer(1, 4))
    return flow


def _skills(c, st):
    if not c.get("skills") and not c.get("skills_line_note"):
        return []
    flow = _sec("SKILLS", st)
    if c.get("skills"):
        flow.append(Paragraph("  ·  ".join(c["skills"]), st["body"]))
    if c.get("skills_line_note"):
        flow.append(Paragraph(c["skills_line_note"], st["body"]))  # negation wording in the skills area
    return flow


def _certs(c, st):
    if not c.get("certifications"):
        return []
    flow = _sec("CERTIFICATIONS", st)
    items = [ListItem(Paragraph(x, st["bullet"]), leftIndent=10) for x in c["certifications"]]
    flow.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=12, bulletColor=GREY))
    return flow


def build_flow(c, path):
    st = _styles()
    story = _header(c, st) + _summary(c, st) + _experience(c, st) + _education(c, st) + _certs(c, st) + _skills(c, st)
    SimpleDocTemplate(path, pagesize=LETTER, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                      topMargin=0.7 * inch, bottomMargin=0.7 * inch, title=c["id"], author=c["name"]).build(story)


def build_one(c):
    path = os.path.join(RESUMES, f"{c['id']}.pdf")
    build_flow(c, path)
    d = fitz.open(path); pages = d.page_count; text = "\n".join(p.get_text() for p in d); d.close()
    norm = " ".join(text.split())
    # verify the controlled probe wording rendered
    probe = ""
    if c.get("skills_line_note"):
        probe = c["skills_line_note"]
    elif c.get("work_auth"):
        probe = c["work_auth"]
    elif c["experience"][0].get("emp_type_label"):
        probe = c["experience"][0]["emp_type_label"]
    elif c.get("certifications"):
        probe = c["certifications"][0]
    probe_ok = all(w in norm for w in probe.split()) if probe else True
    return {"id": c["id"], "category": c["category"], "path": path, "built": True,
            "pages": pages, "expected_pages": c["expected_pages"], "controlled": c["controlled"],
            "controlled_text_present": probe_ok, "text_chars": len(text.strip())}


def main():
    only = sys.argv[1:]
    targets = [BY_ID[i] for i in only] if only else CANDIDATES
    report = {}
    for c in targets:
        try:
            r = build_one(c); report[c["id"]] = r
            flag = "" if r["pages"] == r["expected_pages"] else "  <-- PAGES"
            flag += "" if r["controlled_text_present"] else "  <-- PROBE TEXT MISSING"
            print(f"  {c['id']} [{c['category']:<20}] p{r['pages']} {r['text_chars']}ch  {c['controlled'][:34]}{flag}")
        except Exception as e:  # noqa
            report[c["id"]] = {"id": c["id"], "built": False, "error": repr(e)}
            print(f"  {c['id']} FAILED: {e!r}")
    rp = os.path.join(HERE, "_build_report.json")
    if only and os.path.exists(rp):
        ex = json.load(open(rp, encoding="utf-8")); ex.update(report); report = ex
    json.dump(report, open(rp, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\nBuilt {sum(1 for r in report.values() if r.get('built'))}/{len(report)} -> {RESUMES}")


if __name__ == "__main__":
    main()
