"""
generate_targeted.py — Build the 45 targeted probe resumes (T01-T45).

ReportLab Platypus for flow / table layouts and the two-column outer table;
PyMuPDF only for page-count / text verification. Unicode-safe, automatic
wrapping, dynamic heights — no hard-coded coordinates for variable text.

Writes resumes/<ID>.pdf and _build_report.json.

Usage:  python generate_targeted.py [T01 T14 ...]
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

from targeted_candidates import CANDIDATES, BY_ID

HERE = os.path.dirname(os.path.abspath(__file__))
RESUMES = os.path.join(HERE, "resumes")
os.makedirs(RESUMES, exist_ok=True)
PAGE_W, PAGE_H = LETTER

INK = colors.HexColor("#1b1b20")
GREY = colors.HexColor("#555560")
RULE = colors.HexColor("#bcc0c7")
ACCENT = colors.HexColor("#234a7d")


def _styles():
    ss = getSampleStyleSheet()
    return {
        "name": ParagraphStyle("name", parent=ss["Title"], fontName="Helvetica-Bold",
                               fontSize=20, leading=24, textColor=INK, spaceAfter=2, alignment=0),
        "title": ParagraphStyle("title", parent=ss["Normal"], fontName="Helvetica",
                                fontSize=12, leading=15, textColor=ACCENT, spaceAfter=3),
        "contact": ParagraphStyle("contact", parent=ss["Normal"], fontName="Helvetica",
                                  fontSize=9, leading=12, textColor=GREY),
        "section": ParagraphStyle("section", parent=ss["Heading2"], fontName="Helvetica-Bold",
                                  fontSize=11, leading=14, textColor=ACCENT, spaceBefore=10, spaceAfter=2),
        "role": ParagraphStyle("role", parent=ss["Normal"], fontName="Helvetica-Bold",
                               fontSize=10.5, leading=13, textColor=INK),
        "dates": ParagraphStyle("dates", parent=ss["Normal"], fontName="Helvetica",
                                fontSize=9, leading=13, textColor=GREY, alignment=2),
        "org": ParagraphStyle("org", parent=ss["Normal"], fontName="Helvetica-Oblique",
                              fontSize=9.5, leading=12, textColor=GREY, spaceAfter=1),
        "body": ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica",
                               fontSize=9.5, leading=13, textColor=INK),
        "bullet": ParagraphStyle("bullet", parent=ss["Normal"], fontName="Helvetica",
                                 fontSize=9.5, leading=12.5, textColor=INK),
        "note": ParagraphStyle("note", parent=ss["Normal"], fontName="Helvetica-Oblique",
                               fontSize=9, leading=12, textColor=colors.HexColor("#7a3b00"), spaceAfter=2),
        "small": ParagraphStyle("small", parent=ss["Normal"], fontName="Helvetica",
                                fontSize=9, leading=12, textColor=INK),
    }


def _contact(c):
    bits = [c["email"], c.get("phone", ""), c.get("location", "")]
    bits += [f"{k}: {v}" for k, v in c.get("links", {}).items()]
    return "  |  ".join(b for b in bits if b)


def _sec(t, st):
    return [Paragraph(t, st["section"]),
            HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=4)]


def _role_row(title, dates, st):
    t = Table([[Paragraph(title, st["role"]), Paragraph(dates, st["dates"])]],
              colWidths=[None, 1.7 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")] +
                          [(p, (0, 0), (-1, -1), 0) for p in
                           ("LEFTPADDING", "RIGHTPADDING", "TOPPADDING", "BOTTOMPADDING")]))
    return t


def _header(c, st):
    return [Paragraph(c["name"], st["name"]), Paragraph(c["title"], st["title"]),
            Paragraph(_contact(c), st["contact"]), Spacer(1, 4),
            HRFlowable(width="100%", thickness=1, color=RULE, spaceAfter=4)]


def _experience(c, st, nested=False):
    flow = _sec("EXPERIENCE", st)
    for e in c["experience"]:
        dd = e["date_display"]
        short = len(dd) <= 20  # short ranges go right-aligned; long/prose get their own line
        block = []
        if short and not nested:
            block.append(_role_row(e["title"], dd, st))
        elif short and nested:
            block.append(Paragraph(f"{e['title']} <font size=8 color='#555560'>&nbsp;|&nbsp; "
                                   f"{dd}</font>", st["role"]))
        else:
            block.append(Paragraph(e["title"], st["role"]))
        # employer / location line
        if e["org"]:
            org = e["org"] + (f"  ·  {e['location']}" if e.get("location") else "")
            block.append(Paragraph(org, st["org"]))
        else:
            block.append(Paragraph(f"<i>(no employer stated)</i>  ·  {e.get('location','')}", st["org"]))
        # long/prose date expression: its own clear line (keeps wording intact & readable)
        if not short:
            block.append(Paragraph(dd, st["org"]))
        if e.get("bullets"):
            items = [ListItem(Paragraph(b, st["bullet"]), leftIndent=10) for b in e["bullets"]]
            block.append(ListFlowable(items, bulletType="bullet", start="•",
                                      leftIndent=12, bulletColor=GREY, spaceBefore=1))
        block.append(Spacer(1, 6))
        # KeepTogether blows up inside a table cell (two-column) — only use it in flow.
        if nested:
            flow.extend(block)
        else:
            flow.append(KeepTogether(block))
    return flow


def _education(c, st):
    flow = _sec("EDUCATION", st)
    for ed in c["education"]:
        flow.append(_role_row(ed["degree"], ed["date_display"], st))
        inst = ed["institution"] + (f"  ·  {ed['location']}" if ed.get("location") else "")
        flow.append(Paragraph(inst, st["org"]))
        if ed.get("note"):
            flow.append(Paragraph(ed["note"], st["note"]))  # the status wording under test
        flow.append(Spacer(1, 4))
    return flow


def _skills(c, st):
    if not c.get("skills"):
        return []
    return _sec("SKILLS", st) + [Paragraph("  ·  ".join(c["skills"]), st["body"])]


def _summary(c, st):
    if not c.get("summary"):
        return []
    return _sec("SUMMARY", st) + [Paragraph(c["summary"], st["body"])]


def _doc(path, c, margins=0.8):
    return SimpleDocTemplate(path, pagesize=LETTER, leftMargin=margins * inch,
                             rightMargin=margins * inch, topMargin=0.7 * inch,
                             bottomMargin=0.7 * inch, title=c["id"], author=c["name"])


# ---- layouts ----
def build_flow(c, path):
    st = _styles()
    story = _header(c, st) + _summary(c, st) + _experience(c, st) + _education(c, st) + _skills(c, st)
    _doc(path, c).build(story)


def build_table(c, path):
    st = _styles()
    story = _header(c, st) + _summary(c, st)
    # employment history as a bordered table
    story += _sec("EMPLOYMENT HISTORY", st)
    rows = [[Paragraph(f"<b>{h}</b>", st["small"]) for h in ("Job Title", "Employer", "Dates")]]
    for e in c["experience"]:
        rows.append([Paragraph(e["title"], st["small"]),
                     Paragraph(e["org"] or "(no employer stated)", st["small"]),
                     Paragraph(e["date_display"], st["small"])])
    tbl = Table(rows, colWidths=[2.5 * inch, 2.6 * inch, 1.8 * inch], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story += [tbl, Spacer(1, 8)]
    # education: for T45 (paired), present education as a table too
    if c["id"] == "T45":
        story += _sec("EDUCATION", st)
        erows = [[Paragraph(f"<b>{h}</b>", st["small"]) for h in ("Qualification", "Institution", "Dates", "Status")]]
        for ed in c["education"]:
            erows.append([Paragraph(ed["degree"], st["small"]),
                          Paragraph(ed["institution"], st["small"]),
                          Paragraph(ed["date_display"], st["small"]),
                          Paragraph(ed.get("note", ""), st["small"])])
        etbl = Table(erows, colWidths=[2.2 * inch, 2.0 * inch, 1.3 * inch, 1.4 * inch], repeatRows=1)
        etbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, RULE),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f7")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        story += [etbl, Spacer(1, 8)]
    else:
        story += _education(c, st)
    story += _skills(c, st)
    _doc(path, c).build(story)


def build_two_column(c, path):
    st = _styles()
    side_name = ParagraphStyle("side_name", parent=st["name"], fontSize=16, leading=19)
    side_h = ParagraphStyle("side_h", parent=st["section"], fontSize=10, spaceBefore=8)
    side_c = ParagraphStyle("side_c", parent=st["small"], fontSize=7.5, leading=10.5)
    side_b = ParagraphStyle("side_b", parent=st["small"], fontSize=8.5, leading=11)
    note_s = ParagraphStyle("note_s", parent=st["note"], fontSize=8)

    side = [Paragraph(c["name"], side_name),
            Paragraph(c["title"], ParagraphStyle("stt", parent=st["title"], fontSize=10)),
            Spacer(1, 6), Paragraph("CONTACT", side_h), Paragraph(c["email"], side_c)]
    if c.get("phone"):
        side.append(Paragraph(c["phone"], side_c))
    if c.get("location"):
        side.append(Paragraph(c["location"], side_c))
    for k, v in c.get("links", {}).items():
        side.append(Paragraph(f"{k}: {v}", side_c))
    side.append(Paragraph("SKILLS", side_h))
    for sk in c["skills"]:
        side.append(Paragraph("• " + sk, side_b))
    side.append(Paragraph("EDUCATION", side_h))
    for ed in c["education"]:
        side.append(Paragraph(f"<b>{ed['degree']}</b>", side_b))
        side.append(Paragraph(f"{ed['institution']} ({ed['date_display']})", side_b))
        if ed.get("note"):
            side.append(Paragraph(ed["note"], note_s))
        side.append(Spacer(1, 3))

    main = _sec("SUMMARY", st) + [Paragraph(c["summary"], st["body"])]
    main += _experience(c, st, nested=True)

    outer = Table([[side, main]], colWidths=[2.35 * inch, 4.75 * inch])
    outer.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#f1f4f8")),
        ("LEFTPADDING", (0, 0), (0, 0), 10), ("RIGHTPADDING", (0, 0), (0, 0), 10),
        ("LEFTPADDING", (1, 0), (1, 0), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    SimpleDocTemplate(path, pagesize=LETTER, leftMargin=0.5 * inch, rightMargin=0.5 * inch,
                      topMargin=0.5 * inch, bottomMargin=0.5 * inch,
                      title=c["id"], author=c["name"]).build([outer])


BUILDERS = {"flow": build_flow, "table": build_table, "two-column": build_two_column}


def build_one(c):
    path = os.path.join(RESUMES, f"{c['id']}.pdf")
    BUILDERS[c["layout"]](c, path)
    d = fitz.open(path)
    pages = d.page_count
    text = "\n".join(p.get_text() for p in d)
    d.close()
    # confirm the controlled wording actually rendered into the PDF text
    # (word-based: long date strings may wrap across lines in the rendered text)
    norm_text = " ".join(text.split())
    if c["phase"] == 1:
        probe = c["experience"][0]["date_display"]
    elif c["phase"] == 3:
        probe = c["education"][0].get("note", "")
    else:
        probe = None
    probe_ok = all(w in norm_text for w in probe.split()) if probe else True
    return {"id": c["id"], "phase": c["phase"], "layout": c["layout"], "path": path,
            "built": True, "pages": pages, "expected_pages": c["expected_pages"],
            "controlled": c["controlled"], "controlled_text_present": probe_ok,
            "text_chars": len(text.strip())}


def main():
    only = sys.argv[1:]
    targets = [BY_ID[i] for i in only] if only else CANDIDATES
    report = {}
    for c in targets:
        try:
            r = build_one(c)
            report[c["id"]] = r
            flag = "" if r["pages"] == r["expected_pages"] else "  <-- PAGES"
            flag += "" if r["controlled_text_present"] else "  <-- CONTROLLED TEXT MISSING"
            print(f"  {c['id']} [{c['layout']:<11}] p{r['pages']} {r['text_chars']}ch  {c['controlled'][:40]}{flag}")
        except Exception as e:  # noqa
            report[c["id"]] = {"id": c["id"], "built": False, "error": repr(e)}
            print(f"  {c['id']} FAILED: {e!r}")
    rp = os.path.join(HERE, "_build_report.json")
    if only and os.path.exists(rp):
        ex = json.load(open(rp, encoding="utf-8")); ex.update(report); report = ex
    json.dump(report, open(rp, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    built = sum(1 for r in report.values() if r.get("built"))
    print(f"\nBuilt {built}/{len(report)} -> {RESUMES}")


if __name__ == "__main__":
    main()
