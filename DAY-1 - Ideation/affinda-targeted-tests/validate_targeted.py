"""
validate_targeted.py — Structural + visual validation for the 45 targeted resumes.

Per file: opens, 1 page, no blank page, name + email + required sections present,
the CONTROLLED test wording present, and (on the 150-DPI render) no overlapping
paragraphs, no clipped text, no broken characters. Renders previews and a contact
sheet. Writes validation_report.json. Never silently passes a broken file.

Usage:  python validate_targeted.py
"""
from __future__ import annotations

import json
import os

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

from targeted_candidates import CANDIDATES

HERE = os.path.dirname(os.path.abspath(__file__))
RESUMES = os.path.join(HERE, "resumes")
PREVIEWS = os.path.join(HERE, "previews")
os.makedirs(PREVIEWS, exist_ok=True)
DPI = 150
ZOOM = DPI / 72.0


def _ov(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def line_boxes(page):
    out = []
    for bi, block in enumerate(page.get_text("dict").get("blocks", [])):
        if block.get("type", 0) != 0:
            continue
        for line in block.get("lines", []):
            txt = "".join(s["text"] for s in line.get("spans", [])).strip()
            if txt:
                out.append((fitz.Rect(line["bbox"]), txt, bi))
    return out


def detect_overlaps(page):
    lines = line_boxes(page)
    probs = []
    for i in range(len(lines)):
        ri, ti, bi = lines[i]
        hi = ri.height or 1.0
        for j in range(i + 1, len(lines)):
            rj, tj, bj = lines[j]
            if bi == bj:
                continue
            v = _ov(ri.y0, ri.y1, rj.y0, rj.y1)
            h = _ov(ri.x0, ri.x1, rj.x0, rj.x1)
            if v > 0.45 * min(hi, rj.height or 1.0) and h > 0.25 * (min(ri.width, rj.width) or 1.0):
                probs.append(f"overlap: '{ti[:30]}' vs '{tj[:30]}'")
    return probs


def detect_clipping(page):
    pr = page.rect
    probs = []
    for r, txt, _ in line_boxes(page):
        if r.x0 < pr.x0 - 2 or r.y0 < pr.y0 - 2 or r.x1 > pr.x1 + 2 or r.y1 > pr.y1 + 2:
            probs.append(f"clipped: '{txt[:30]}'")
    return probs


def detect_broken(page):
    t = page.get_text()
    return [f"replacement_char x{t.count(chr(0xFFFD))}"] if "�" in t else []


def page_blank(page):
    return not (page.get_text().strip() or page.get_images() or page.get_drawings())


def controlled_present(c, text):
    """Check the controlled test variable actually rendered."""
    norm = " ".join(text.split())
    if c["phase"] == 1:
        words = c["experience"][0]["date_display"].split()
        return all(w in norm for w in words), "date expression"
    if c["phase"] == 3:
        note = c["education"][0].get("note", "")
        return all(w in norm for w in note.split()), "education status note"
    # phase 2: employer label (or deliberate absence for T20)
    e0 = c["experience"][0]
    if e0["org"] == "":
        return True, "no-employer (by design)"
    return (e0["org"] in norm), "employer label"


def validate_one(c):
    path = os.path.join(RESUMES, f"{c['id']}.pdf")
    res = {"id": c["id"], "phase": c["phase"], "layout": c["layout"],
           "controlled": c["controlled"], "status": "PASS", "problems": [], "notes": []}
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        res["status"] = "FAIL"; res["problems"].append("missing/empty file"); return res, []
    res["size_bytes"] = os.path.getsize(path)
    doc = fitz.open(path)
    res["page_count"] = doc.page_count
    if doc.page_count != c["expected_pages"]:
        res["problems"].append(f"page count {doc.page_count} != {c['expected_pages']}")
    text = "\n".join(p.get_text() for p in doc)
    up = text.upper()
    # name + email + sections
    if c["name"].split()[-1].upper() not in up:
        res["problems"].append("candidate surname not found")
    if c["email"].upper() not in up:
        res["problems"].append("email not found")
    if not ("EXPERIENCE" in up or "EMPLOYMENT" in up):
        res["problems"].append("no experience/employment section")
    if "EDUCATION" not in up:
        res["problems"].append("no education section")
    # controlled variable
    ok, what = controlled_present(c, text)
    if not ok:
        res["problems"].append(f"controlled {what} not fully present")
    else:
        res["notes"].append(f"controlled {what} present")
    # blanks + geometry
    previews = []
    mat = fitz.Matrix(ZOOM, ZOOM)
    for i, page in enumerate(doc):
        if page_blank(page):
            res["problems"].append(f"page {i+1} blank")
        res["problems"] += detect_overlaps(page) + detect_clipping(page) + detect_broken(page)
        p = os.path.join(PREVIEWS, f"{c['id']}.png" if doc.page_count == 1 else f"{c['id']}_p{i+1}.png")
        page.get_pixmap(matrix=mat, alpha=False).save(p)
        previews.append(p)
    doc.close()
    if res["problems"]:
        res["status"] = "FAIL"
    return res, previews


def contact_sheet(items, out, cols=6, tw=210):
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except Exception:  # noqa
        font = ImageFont.load_default()
    thumbs = []
    for label, p in items:
        im = Image.open(p).convert("RGB")
        th = int(im.height * (tw / im.width))
        im = im.resize((tw, th), Image.LANCZOS)
        cap = 20
        canv = Image.new("RGB", (tw, th + cap), "white")
        canv.paste(im, (0, cap))
        d = ImageDraw.Draw(canv)
        d.rectangle([0, 0, tw, cap], fill=(35, 74, 125))
        d.text((5, 3), label, fill="white", font=font)
        d.rectangle([0, 0, tw - 1, th + cap - 1], outline=(185, 185, 185))
        thumbs.append(canv)
    rows = (len(thumbs) + cols - 1) // cols
    cw, ch = tw + 8, max(t.height for t in thumbs) + 8
    sheet = Image.new("RGB", (cols * cw + 8, rows * ch + 8), "white")
    for i, t in enumerate(thumbs):
        r, cc = divmod(i, cols)
        sheet.paste(t, (8 + cc * cw, 8 + r * ch))
    sheet.save(out)
    return out


def main():
    results, items = [], []
    for c in CANDIDATES:
        res, prev = validate_one(c)
        results.append(res)
        for i, p in enumerate(prev):
            items.append((c["id"] if len(prev) == 1 else f"{c['id']}p{i+1}", p))
        d = "" if res["status"] == "PASS" else "  :: " + "; ".join(res["problems"][:2])
        print(f"  {res['id']} [{res['layout']:<11}] {res['status']}{d}")
    sheet = contact_sheet(items, os.path.join(HERE, "contact_sheet.png"))
    summary = {"total": len(results),
               "pass": sum(1 for r in results if r["status"] == "PASS"),
               "fail": sum(1 for r in results if r["status"] == "FAIL")}
    json.dump({"summary": summary, "render_dpi": DPI, "contact_sheet": sheet,
               "results": results}, open(os.path.join(HERE, "validation_report.json"), "w",
               encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\n  {summary['pass']} PASS / {summary['fail']} FAIL of {summary['total']}")
    print(f"  contact sheet -> {sheet}")
    return summary


if __name__ == "__main__":
    main()
