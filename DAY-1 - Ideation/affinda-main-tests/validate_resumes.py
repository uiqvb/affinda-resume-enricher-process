"""
validate_resumes.py — Structural + visual-layout validation for the 20 synthetic
resumes (Categories A, D, E, F). Implements Phase 3 of the brief.

For every resume it:
  A. Structural validation — file exists & nonempty, opens, expected page count,
     no blank pages, required sections present, candidate name present.
  B. Visual-layout validation — renders each page to PNG at 150 DPI and checks for:
       * overlapping paragraphs (text lines from different blocks colliding),
         while ACCOUNTING for intentional multi-column layouts;
       * text drawn outside the page boundary (clipping);
       * replacement / broken characters (U+FFFD).
  C. Visual inspection aid — renders previews and a contact sheet of every page
     so a human (or this agent) can eyeball layout issues.
  D. Reports PASS / WARN / FAIL per file; never silently passes a broken file.

Writes previews/<ID>_pN.png, contact_sheet.png, and validation_report.json.

Usage:
    python validate_resumes.py
"""
from __future__ import annotations

import json
import os

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

from candidates import CANDIDATES, BY_ID

HERE = os.path.dirname(os.path.abspath(__file__))
RESUMES = os.path.join(HERE, "resumes")
PREVIEWS = os.path.join(HERE, "previews")
os.makedirs(PREVIEWS, exist_ok=True)

RENDER_DPI = 150
ZOOM = RENDER_DPI / 72.0


# --------------------------------------------------------------------------- #
#  Geometry helpers
# --------------------------------------------------------------------------- #
def _overlap_1d(a0, a1, b0, b1):
    """Length of 1-D overlap between [a0,a1] and [b0,b1]."""
    return max(0.0, min(a1, b1) - max(a0, b0))


def line_boxes(page):
    """Return [(bbox, text, block_no)] for every non-empty text line."""
    out = []
    d = page.get_text("dict")
    for bi, block in enumerate(d.get("blocks", [])):
        if block.get("type", 0) != 0:
            continue  # skip image blocks
        for line in block.get("lines", []):
            txt = "".join(span["text"] for span in line.get("spans", [])).strip()
            if txt:
                out.append((fitz.Rect(line["bbox"]), txt, bi))
    return out


def detect_overlaps(page):
    """Flag pairs of text lines from DIFFERENT blocks that collide both
    vertically and horizontally — the signature of overlapping paragraphs.
    Multi-column layouts are handled naturally: lines in separate columns do
    not overlap horizontally, so they are not flagged."""
    lines = line_boxes(page)
    problems = []
    for i in range(len(lines)):
        ri, ti, bi = lines[i]
        hi = ri.height or 1.0
        for j in range(i + 1, len(lines)):
            rj, tj, bj = lines[j]
            if bi == bj:
                continue  # same block/paragraph: normal line stacking
            v = _overlap_1d(ri.y0, ri.y1, rj.y0, rj.y1)
            h = _overlap_1d(ri.x0, ri.x1, rj.x0, rj.x1)
            min_h = min(hi, rj.height or 1.0)
            min_w = min(ri.width, rj.width) or 1.0
            # Require substantial overlap in BOTH axes to avoid false positives
            # from touching baselines or shared gutters.
            if v > 0.45 * min_h and h > 0.25 * min_w:
                problems.append({
                    "type": "text_overlap",
                    "a": ti[:40], "b": tj[:40],
                    "v_frac": round(v / min_h, 2), "h_frac": round(h / min_w, 2),
                })
    return problems


def detect_clipping(page):
    """Text whose bounding box falls outside the visible page rectangle."""
    pr = page.rect
    tol = 2.0  # points
    problems = []
    for r, txt, _ in line_boxes(page):
        if (r.x0 < pr.x0 - tol or r.y0 < pr.y0 - tol or
                r.x1 > pr.x1 + tol or r.y1 > pr.y1 + tol):
            problems.append({"type": "clipped_text", "text": txt[:40],
                             "bbox": [round(v, 1) for v in (r.x0, r.y0, r.x1, r.y1)]})
    return problems


def detect_broken_chars(page):
    txt = page.get_text()
    problems = []
    if "�" in txt:
        problems.append({"type": "replacement_char",
                         "count": txt.count("�")})
    return problems


def page_is_blank(page):
    has_text = bool(page.get_text().strip())
    has_images = bool(page.get_images())
    has_draw = bool(page.get_drawings())
    return not (has_text or has_images or has_draw)


# --------------------------------------------------------------------------- #
#  Section / content checks (structural)
# --------------------------------------------------------------------------- #
def required_sections(c):
    req = []
    # Experience heading varies by layout.
    if c["layout"] == "table":
        req.append(("EMPLOYMENT", ["EMPLOYMENT HISTORY", "EMPLOYMENT"]))
    elif c["layout"] == "unusual-order":
        req.append(("EXPERIENCE", ["PROFESSIONAL EXPERIENCE", "EXPERIENCE"]))
    else:
        req.append(("EXPERIENCE", ["EXPERIENCE"]))
    req.append(("EDUCATION", ["EDUCATION"]))
    return req


def structural_check(c, doc, result):
    problems, notes = result["problems"], result["notes"]

    # page count
    if doc.page_count != c["expected_pages"]:
        problems.append(f"page count {doc.page_count} != expected {c['expected_pages']}")

    # blank pages
    for i, page in enumerate(doc):
        if page_is_blank(page):
            problems.append(f"page {i+1} appears blank")

    # Scanned (E03) has no text layer: text-based content checks are N/A.
    full_text = "\n".join(p.get_text() for p in doc)
    result["total_text_chars"] = len(full_text.strip())

    if c["layout"] == "scanned":
        if result["total_text_chars"] > 0:
            problems.append("scanned PDF unexpectedly contains a selectable text layer")
        else:
            notes.append("image-only PDF (no text layer) — content checks rely on OCR; "
                         "this is the intended design for E03.")
        return  # skip text-content assertions for the scanned file

    up = full_text.upper()

    # name present (first + last token)
    first = c["name"].split()[0].upper()
    last = c["name"].split()[-1].upper()
    if first not in up or last not in up:
        problems.append(f"candidate name '{c['name']}' not fully found in text")

    # required section headings
    for label, variants in required_sections(c):
        if not any(v in up for v in variants):
            problems.append(f"required section '{label}' heading not found")

    # at least one employer present
    if not any(exp["org"].upper() in up for exp in c["experience"]):
        problems.append("no employer organisation names found in text")

    # at least one education institution present
    if not any(ed["institution"].upper() in up for ed in c["education"]):
        problems.append("no education institution found in text")

    # skills section: required unless intentionally empty (F04)
    if c.get("skills"):
        if "SKILLS" not in up:
            problems.append("SKILLS section expected but not found")
    else:
        notes.append("no skills section by design (skills embedded in experience).")

    # Primary email(s) present
    for em in c.get("emails", []):
        if em.upper() not in up:
            problems.append(f"email '{em}' not found in text")


# --------------------------------------------------------------------------- #
#  Rendering
# --------------------------------------------------------------------------- #
def render_previews(c, doc):
    mat = fitz.Matrix(ZOOM, ZOOM)
    paths = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=mat, alpha=False)
        p = os.path.join(PREVIEWS, f"{c['id']}_p{i+1}.png")
        pix.save(p)
        paths.append(p)
    return paths


# --------------------------------------------------------------------------- #
#  Per-file validation
# --------------------------------------------------------------------------- #
def validate_one(c):
    path = os.path.join(RESUMES, f"{c['id']}.pdf")
    result = {
        "id": c["id"], "category": c["category"], "layout": c["layout"],
        "status": "PASS", "problems": [], "notes": [],
        "expected_pages": c["expected_pages"],
    }

    if not os.path.exists(path) or os.path.getsize(path) == 0:
        result["status"] = "FAIL"
        result["problems"].append("file missing or empty")
        return result

    result["size_bytes"] = os.path.getsize(path)
    try:
        doc = fitz.open(path)
    except Exception as e:  # noqa
        result["status"] = "FAIL"
        result["problems"].append(f"failed to open PDF: {e!r}")
        return result

    result["page_count"] = doc.page_count

    # A. structural
    structural_check(c, doc, result)

    # B. visual-layout (skip text-geometry checks on the scanned, text-free file)
    overlaps, clips, broken = [], [], []
    if c["layout"] != "scanned":
        for page in doc:
            overlaps += detect_overlaps(page)
            clips += detect_clipping(page)
            broken += detect_broken_chars(page)
    result["overlaps"] = overlaps
    result["clipped"] = clips
    result["broken_chars"] = broken

    # C. render previews
    result["previews"] = render_previews(c, doc)
    doc.close()

    # Severity: overlaps / clipping / broken chars / blanks / page-count = FAIL.
    hard = list(result["problems"]) + overlaps + clips + broken
    if hard:
        result["status"] = "FAIL"
        # fold geometry problems into the problem list for readability
        for o in overlaps:
            result["problems"].append(f"overlap: '{o['a']}' vs '{o['b']}'")
        for cl in clips:
            result["problems"].append(f"clipped: '{cl['text']}'")
        for b in broken:
            result["problems"].append(f"broken char x{b['count']}")
    return result


# --------------------------------------------------------------------------- #
#  Contact sheet
# --------------------------------------------------------------------------- #
def build_contact_sheet(all_previews, out_path, cols=5, thumb_w=260):
    if not all_previews:
        return None
    thumbs = []
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except Exception:  # noqa
        font = ImageFont.load_default()

    for label, p in all_previews:
        im = Image.open(p).convert("RGB")
        ratio = thumb_w / im.width
        th = int(im.height * ratio)
        im = im.resize((thumb_w, th), Image.LANCZOS)
        # caption bar
        cap_h = 22
        canvas = Image.new("RGB", (thumb_w, th + cap_h), "white")
        canvas.paste(im, (0, cap_h))
        d = ImageDraw.Draw(canvas)
        d.rectangle([0, 0, thumb_w, cap_h], fill=(43, 76, 126))
        d.text((6, 3), label, fill="white", font=font)
        d.rectangle([0, 0, thumb_w - 1, th + cap_h - 1], outline=(180, 180, 180))
        thumbs.append(canvas)

    rows = (len(thumbs) + cols - 1) // cols
    cell_w = thumb_w + 10
    cell_h = max(t.height for t in thumbs) + 10
    sheet = Image.new("RGB", (cols * cell_w + 10, rows * cell_h + 10), "white")
    for idx, t in enumerate(thumbs):
        r, col = divmod(idx, cols)
        sheet.paste(t, (10 + col * cell_w, 10 + r * cell_h))
    sheet.save(out_path)
    return out_path


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
def main():
    results = []
    all_previews = []
    for c in CANDIDATES:
        res = validate_one(c)
        results.append(res)
        for i, p in enumerate(res.get("previews", [])):
            lbl = f"{c['id']} p{i+1}" if c["expected_pages"] > 1 else c["id"]
            all_previews.append((lbl, p))
        status = res["status"]
        detail = "" if status == "PASS" else "  :: " + "; ".join(res["problems"][:3])
        print(f"  {res['id']:<4} [{res['layout']:<13}] {status}{detail}")

    sheet = build_contact_sheet(all_previews, os.path.join(HERE, "contact_sheet.png"))

    summary = {
        "total": len(results),
        "pass": sum(1 for r in results if r["status"] == "PASS"),
        "warn": sum(1 for r in results if r["status"] == "WARN"),
        "fail": sum(1 for r in results if r["status"] == "FAIL"),
    }
    report = {"summary": summary, "render_dpi": RENDER_DPI,
              "contact_sheet": sheet, "results": results}
    out = os.path.join(HERE, "validation_report.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n  Summary: {summary['pass']} PASS / {summary['warn']} WARN / "
          f"{summary['fail']} FAIL  (of {summary['total']})")
    print(f"  Contact sheet -> {sheet}")
    print(f"  Report        -> {out}")
    return summary


if __name__ == "__main__":
    main()
