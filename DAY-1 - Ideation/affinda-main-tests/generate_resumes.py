"""
generate_resumes.py — Robust PDF generation engine for the 20 synthetic resumes
(Categories A, D, E, F) used to evaluate Affinda's Resume Parser.

Design goals (per project brief, Phase 2):
  * No hard-coded vertical positions for variable-length text in the flowing
    layouts: ReportLab Platypus handles wrapping, dynamic section heights,
    paragraph/line spacing, page breaks and overflow automatically.
  * Explicit, calculated layout regions (not per-candidate coordinate fiddling)
    for the two-column and unusual-order PDFs, built with PyMuPDF.
  * Unicode-safe rendering (Helvetica / WinAnsi covers the Latin-1 accented
    characters used in the fictional names).

Outputs resumes/<ID>.pdf for all 20 candidates and writes _build_report.json.

Usage:
    python generate_resumes.py
"""
from __future__ import annotations

import io
import json
import os
import sys

import fitz  # PyMuPDF — rendering, two-column/scanned/unusual-order layouts

from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, BaseDocTemplate, PageTemplate, Frame, FrameBreak,
    Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable, KeepTogether, PageBreak, Flowable,
)

from candidates import CANDIDATES, BY_ID

HERE = os.path.dirname(os.path.abspath(__file__))
RESUMES = os.path.join(HERE, "resumes")
os.makedirs(RESUMES, exist_ok=True)

PAGE_W, PAGE_H = LETTER
INK = colors.HexColor("#1a1a1a")
GREY = colors.HexColor("#555555")
RULE = colors.HexColor("#b0b0b0")
ACCENT = colors.HexColor("#2b4c7e")


# --------------------------------------------------------------------------- #
#  Shared text helpers
# --------------------------------------------------------------------------- #
def contact_line(c, include_emails=True):
    bits = []
    if include_emails:
        bits.extend(c.get("emails", []))
    if c.get("phone"):
        bits.append(c["phone"])
    if c.get("location"):
        bits.append(c["location"])
    for label, url in c.get("links", {}).items():
        bits.append(f"{label}: {url}")
    return "  |  ".join(bits)


def date_range(exp):
    start = exp.get("start", "")
    end = exp.get("end", "")
    if start and end:
        return f"{start} – {end}"
    if start and not end:
        return f"{start} –"      # D04: start only, deliberately no end
    return end or start


# --------------------------------------------------------------------------- #
#  Platypus styles
# --------------------------------------------------------------------------- #
def build_styles():
    ss = getSampleStyleSheet()
    styles = {
        "name": ParagraphStyle("name", parent=ss["Title"], fontName="Helvetica-Bold",
                               fontSize=20, leading=24, textColor=INK, spaceAfter=2,
                               alignment=TA_LEFT),
        "title": ParagraphStyle("jobtitle", parent=ss["Normal"], fontName="Helvetica",
                                fontSize=12, leading=15, textColor=ACCENT, spaceAfter=4),
        "contact": ParagraphStyle("contact", parent=ss["Normal"], fontName="Helvetica",
                                  fontSize=8.5, leading=12, textColor=GREY, spaceAfter=2),
        "section": ParagraphStyle("section", parent=ss["Heading2"], fontName="Helvetica-Bold",
                                  fontSize=11, leading=14, textColor=ACCENT,
                                  spaceBefore=10, spaceAfter=2),
        "role": ParagraphStyle("role", parent=ss["Normal"], fontName="Helvetica-Bold",
                               fontSize=10.5, leading=13, textColor=INK),
        "dates": ParagraphStyle("dates", parent=ss["Normal"], fontName="Helvetica",
                                fontSize=9, leading=13, textColor=GREY, alignment=TA_RIGHT),
        "org": ParagraphStyle("org", parent=ss["Normal"], fontName="Helvetica-Oblique",
                              fontSize=9.5, leading=12, textColor=GREY, spaceAfter=2),
        "body": ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica",
                               fontSize=9.5, leading=13, textColor=INK, spaceAfter=2),
        "bullet": ParagraphStyle("bullet", parent=ss["Normal"], fontName="Helvetica",
                                 fontSize=9.5, leading=12.5, textColor=INK),
        "small": ParagraphStyle("small", parent=ss["Normal"], fontName="Helvetica",
                                fontSize=9, leading=12, textColor=INK, spaceAfter=1),
    }
    return styles


def header_block(c, styles, include_emails=True):
    """Identity + contact header as a list of flowables."""
    flow = [
        Paragraph(c["name"], styles["name"]),
        Paragraph(c["title"], styles["title"]),
        Paragraph(contact_line(c, include_emails=include_emails), styles["contact"]),
        Spacer(1, 4),
        HRFlowable(width="100%", thickness=1, color=RULE, spaceAfter=4),
    ]
    return flow


def section_title(text, styles):
    return [Paragraph(text, styles["section"]),
            HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=4)]


def role_header(exp, styles):
    """Two-column role/date row using a Table (keeps dates right-aligned, no overlap)."""
    t = Table(
        [[Paragraph(exp["title"], styles["role"]),
          Paragraph(date_range(exp), styles["dates"])]],
        colWidths=[None, 1.6 * inch],
    )
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def experience_flow(c, styles, bullets=True):
    flow = section_title("EXPERIENCE", styles)
    for exp in c["experience"]:
        block = [role_header(exp, styles)]
        org_line = exp["org"]
        if exp.get("location"):
            org_line += f"  ·  {exp['location']}"
        block.append(Paragraph(org_line, styles["org"]))
        if bullets and exp.get("bullets"):
            items = [ListItem(Paragraph(b, styles["bullet"]), leftIndent=10)
                     for b in exp["bullets"]]
            block.append(ListFlowable(items, bulletType="bullet", start="•",
                                      leftIndent=12, bulletColor=GREY, spaceBefore=1))
        block.append(Spacer(1, 6))
        # KeepTogether avoids a role header being orphaned at a page bottom.
        flow.append(KeepTogether(block))
    return flow


def education_flow(c, styles):
    flow = section_title("EDUCATION", styles)
    for ed in c["education"]:
        dates = date_range({"start": ed.get("start", ""), "end": ed.get("end", "")})
        t = Table(
            [[Paragraph(ed["degree"], styles["role"]),
              Paragraph(dates, styles["dates"])]],
            colWidths=[None, 1.6 * inch],
        )
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        block = [t]
        inst = ed["institution"]
        if ed.get("location"):
            inst += f"  ·  {ed['location']}"
        block.append(Paragraph(inst, styles["org"]))
        if ed.get("note"):
            block.append(Paragraph(ed["note"], styles["small"]))
        block.append(Spacer(1, 5))
        flow.append(KeepTogether(block))
    return flow


def skills_flow(c, styles):
    if not c.get("skills"):
        return []
    flow = section_title("SKILLS", styles)
    flow.append(Paragraph("  ·  ".join(c["skills"]), styles["body"]))
    return flow


def certs_flow(c, styles):
    if not c.get("certifications"):
        return []
    flow = section_title("CERTIFICATIONS", styles)
    items = [ListItem(Paragraph(x, styles["bullet"]), leftIndent=10)
             for x in c["certifications"]]
    flow.append(ListFlowable(items, bulletType="bullet", start="•",
                             leftIndent=12, bulletColor=GREY))
    return flow


def summary_flow(c, styles):
    if not c.get("summary"):
        return []
    flow = section_title("SUMMARY", styles)
    flow.append(Paragraph(c["summary"], styles["body"]))
    # F01: surface the conflicting profile line inside the summary section.
    if c.get("conflict_note"):
        flow.append(Spacer(1, 2))
        flow.append(Paragraph(
            "Profile: HR Business Partner since 2020, partnering across business units.",
            styles["small"]))
    return flow


def _doc(path, title, author):
    return SimpleDocTemplate(
        path, pagesize=LETTER,
        leftMargin=0.8 * inch, rightMargin=0.8 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title=title, author=author,
    )


# --------------------------------------------------------------------------- #
#  Layout: flowing resume (Categories A, D, F)
# --------------------------------------------------------------------------- #
def build_flow(c, path):
    styles = build_styles()
    story = []
    story += header_block(c, styles)
    story += summary_flow(c, styles)
    story += experience_flow(c, styles)
    story += education_flow(c, styles)
    story += certs_flow(c, styles)
    story += skills_flow(c, styles)   # empty for F04 (no skills section)
    _doc(path, c["id"], c["name"]).build(story)


# --------------------------------------------------------------------------- #
#  Layout: employment history as a table (E02)
# --------------------------------------------------------------------------- #
def build_table(c, path):
    styles = build_styles()
    story = []
    story += header_block(c, styles)
    story += summary_flow(c, styles)

    story += section_title("EMPLOYMENT HISTORY", styles)
    head = ["Job Title", "Employer", "Location", "Dates"]
    rows = [[Paragraph(f"<b>{h}</b>", styles["small"]) for h in head]]
    for exp in c["experience"]:
        rows.append([
            Paragraph(exp["title"], styles["small"]),
            Paragraph(exp["org"], styles["small"]),
            Paragraph(exp.get("location", ""), styles["small"]),
            Paragraph(date_range(exp), styles["small"]),
        ])
    tbl = Table(rows, colWidths=[2.0 * inch, 1.9 * inch, 1.4 * inch, 1.3 * inch], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 8))
    story += education_flow(c, styles)
    story += certs_flow(c, styles)
    story += skills_flow(c, styles)
    _doc(path, c["id"], c["name"]).build(story)


# --------------------------------------------------------------------------- #
#  Layout: three-page academic CV (E04)
# --------------------------------------------------------------------------- #
def build_three_page(c, path):
    styles = build_styles()
    story = []
    # Page 1 — identity, summary, experience, education
    story += header_block(c, styles)
    story += summary_flow(c, styles)
    story += experience_flow(c, styles)
    story += education_flow(c, styles)
    story.append(PageBreak())

    # Page 2 — publications
    story += section_title("SELECTED PUBLICATIONS", styles)
    items = [ListItem(Paragraph(p, styles["bullet"]), leftIndent=10)
             for p in c.get("publications", [])]
    story.append(ListFlowable(items, bulletType="bullet", start="•",
                              leftIndent=12, bulletColor=GREY))
    story += section_title("SKILLS", styles)
    story.append(Paragraph("  ·  ".join(c["skills"]), styles["body"]))
    story.append(PageBreak())

    # Page 3 — grants and references
    story += section_title("GRANTS & FUNDING", styles)
    gitems = [ListItem(Paragraph(g, styles["bullet"]), leftIndent=10)
              for g in c.get("grants", [])]
    story.append(ListFlowable(gitems, bulletType="bullet", start="•",
                              leftIndent=12, bulletColor=GREY))
    story += section_title("REFERENCES", styles)
    ritems = [ListItem(Paragraph(r, styles["bullet"]), leftIndent=10)
              for r in c.get("references", [])]
    story.append(ListFlowable(ritems, bulletType="bullet", start="•",
                              leftIndent=12, bulletColor=GREY))
    _doc(path, c["id"], c["name"]).build(story)


# --------------------------------------------------------------------------- #
#  PyMuPDF helpers for explicit-region layouts
# --------------------------------------------------------------------------- #
HELV = "helv"
HELV_B = "hebo"
HELV_O = "heit"


def _ins(page, rect, text, size, font=HELV, color=(0.1, 0.1, 0.1), align=0):
    """insert_textbox with overflow guard; returns leftover (>=0 ok, <0 overflow)."""
    return page.insert_textbox(rect, text, fontsize=size, fontname=font,
                               color=color, align=align)


def build_two_column(c, path):
    """E01 — two-column layout: an outer 2-cell table (sidebar | main) built with
    ReportLab so wrapping and Unicode (bullets, en-dashes) are handled correctly.
    Reading order is sidebar-first then main, a realistic parser challenge."""
    styles = build_styles()
    side_name = ParagraphStyle("side_name", parent=styles["name"], fontSize=16, leading=19)
    side_h = ParagraphStyle("side_h", parent=styles["section"], fontSize=10, spaceBefore=8)
    side_b = ParagraphStyle("side_b", parent=styles["small"], fontSize=8.5, leading=11)
    # Contact lines use a smaller font so long emails/URLs fit on one line.
    side_c = ParagraphStyle("side_c", parent=styles["small"], fontSize=7.5, leading=10.5)

    # --- sidebar flowables ---
    side = [Paragraph(c["name"], side_name),
            Paragraph(c["title"], ParagraphStyle("st", parent=styles["title"], fontSize=10)),
            Spacer(1, 6), Paragraph("CONTACT", side_h)]
    for em in c.get("emails", []):
        side.append(Paragraph(em, side_c))
    if c.get("phone"):
        side.append(Paragraph(c["phone"], side_c))
    if c.get("location"):
        side.append(Paragraph(c["location"], side_c))
    for label, url in c.get("links", {}).items():
        side.append(Paragraph(f"{label}: {url}", side_c))
    side.append(Paragraph("SKILLS", side_h))
    for sk in c["skills"]:
        side.append(Paragraph("• " + sk, side_b))
    side.append(Paragraph("EDUCATION", side_h))
    for ed in c["education"]:
        side.append(Paragraph(f"<b>{ed['degree']}</b>", side_b))
        side.append(Paragraph(f"{ed['institution']} "
                              f"({ed.get('start','')}–{ed.get('end','')})", side_b))
        side.append(Spacer(1, 3))

    # --- main-column flowables ---
    # Avoid nested auto-width tables inside a table cell (ReportLab can't size
    # a colWidth=None sub-table there): render role + dates as one paragraph line.
    main = section_title("SUMMARY", styles)
    main.append(Paragraph(c["summary"], styles["body"]))
    main += section_title("EXPERIENCE", styles)
    role_line = ParagraphStyle("role_line", parent=styles["role"])
    for exp in c["experience"]:
        main.append(Paragraph(
            f"{exp['title']} "
            f"<font size=8 color='#555555'>&nbsp;|&nbsp; {date_range(exp)}</font>",
            role_line))
        org_line = exp["org"] + (f"  ·  {exp['location']}" if exp.get("location") else "")
        main.append(Paragraph(org_line, styles["org"]))
        if exp.get("bullets"):
            items = [ListItem(Paragraph(b, styles["bullet"]), leftIndent=10)
                     for b in exp["bullets"]]
            main.append(ListFlowable(items, bulletType="bullet", start="•",
                                     leftIndent=12, bulletColor=GREY, spaceBefore=1))
        main.append(Spacer(1, 6))

    outer = Table([[side, main]], colWidths=[2.35 * inch, 4.75 * inch])
    outer.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#f1f4f8")),
        ("LEFTPADDING", (0, 0), (0, 0), 10),
        ("RIGHTPADDING", (0, 0), (0, 0), 10),
        ("LEFTPADDING", (1, 0), (1, 0), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    doc = SimpleDocTemplate(path, pagesize=LETTER,
                            leftMargin=0.5 * inch, rightMargin=0.5 * inch,
                            topMargin=0.5 * inch, bottomMargin=0.5 * inch,
                            title=c["id"], author=c["name"])
    doc.build([outer])


def build_unusual_order(c, path):
    """E05 — visually clear but non-standard reading order: experience/education/
    skills in an upper frame, the identity block anchored in a lower frame.
    Two ReportLab frames guarantee clean separation with no overlap or clipping."""
    styles = build_styles()
    M = 0.7 * inch
    id_h = 1.15 * inch                      # height of the bottom identity frame
    gap = 0.18 * inch
    top_frame = Frame(M, M + id_h + gap, PAGE_W - 2 * M,
                      PAGE_H - 2 * M - id_h - gap, id="top",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    bot_frame = Frame(M, M, PAGE_W - 2 * M, id_h, id="bottom",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    story = []
    story += experience_flow(c, styles)
    story += education_flow(c, styles)
    story += skills_flow(c, styles)
    story.append(FrameBreak())              # push identity into the bottom frame
    story.append(HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=6))
    story.append(Paragraph(c["name"], styles["name"]))
    story.append(Paragraph(c["title"], styles["title"]))
    story.append(Paragraph(contact_line(c), styles["contact"]))

    doc = BaseDocTemplate(path, pagesize=LETTER, title=c["id"], author=c["name"])
    doc.addPageTemplates([PageTemplate(id="twoframe", frames=[top_frame, bot_frame])])
    doc.build(story)


def build_scanned(c, path):
    """E03 — image-only PDF with NO text layer. Build a normal resume, rasterise it,
    and place the raster as a full-page image on a fresh PDF (no selectable text)."""
    # 1) Build a normal flowing resume into an in-memory PDF.
    buf = io.BytesIO()
    styles = build_styles()
    story = []
    story += header_block(c, styles)
    story += summary_flow(c, styles)
    story += experience_flow(c, styles)
    story += education_flow(c, styles)
    story += skills_flow(c, styles)
    tmp = SimpleDocTemplate(buf, pagesize=LETTER,
                            leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                            title=c["id"], author=c["name"])
    tmp.build(story)
    buf.seek(0)

    # 2) Rasterise every page at 200 DPI.
    src = fitz.open(stream=buf.read(), filetype="pdf")
    out = fitz.open()
    zoom = 200 / 72.0
    mat = fitz.Matrix(zoom, zoom)
    for spage in src:
        pix = spage.get_pixmap(matrix=mat, alpha=False)
        npage = out.new_page(width=spage.rect.width, height=spage.rect.height)
        npage.insert_image(npage.rect, pixmap=pix)   # image only; no text drawn
    out.save(path)
    out.close()
    src.close()


# --------------------------------------------------------------------------- #
#  Dispatch
# --------------------------------------------------------------------------- #
BUILDERS = {
    "flow": build_flow,
    "table": build_table,
    "three-page": build_three_page,
    "two-column": build_two_column,
    "scanned": build_scanned,
    "unusual-order": build_unusual_order,
}


def build_one(c):
    path = os.path.join(RESUMES, f"{c['id']}.pdf")
    builder = BUILDERS[c["layout"]]
    builder(c, path)
    # Verify the file and page count immediately.
    d = fitz.open(path)
    pages = d.page_count
    # Detect whether a text layer exists (E03 must have none).
    text_chars = sum(len(p.get_text().strip()) for p in d)
    d.close()
    return {
        "id": c["id"], "category": c["category"], "layout": c["layout"],
        "path": path, "built": True, "pages": pages,
        "expected_pages": c["expected_pages"],
        "has_text_layer": text_chars > 0, "text_chars": text_chars,
    }


def main():
    only = sys.argv[1:]  # optionally pass IDs to rebuild a subset
    targets = [BY_ID[i] for i in only] if only else CANDIDATES
    report = {}
    for c in targets:
        try:
            report[c["id"]] = build_one(c)
            r = report[c["id"]]
            flag = "" if r["pages"] == r["expected_pages"] else "  <-- PAGE COUNT MISMATCH"
            tl = "no-text(OCR)" if not r["has_text_layer"] else f"{r['text_chars']}ch"
            print(f"  {c['id']} [{c['layout']:<13}] {r['pages']}p / exp {r['expected_pages']}p  {tl}{flag}")
        except Exception as e:  # noqa
            report[c["id"]] = {"id": c["id"], "built": False, "error": repr(e)}
            print(f"  {c['id']} FAILED: {e!r}")
    # Merge into existing report if rebuilding a subset.
    report_path = os.path.join(HERE, "_build_report.json")
    if only and os.path.exists(report_path):
        with open(report_path, encoding="utf-8") as f:
            existing = json.load(f)
        existing.update(report)
        report = existing
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    built = sum(1 for r in report.values() if r.get("built"))
    print(f"\nBuilt {built}/{len(report)} PDFs -> {RESUMES}")
    print(f"Build report -> {report_path}")


if __name__ == "__main__":
    main()
