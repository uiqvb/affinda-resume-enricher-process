"""
validate_round3.py — Structural + visual validation for the 48 round-3 resumes.
Opens, 1 page, no blank, name/email/sections present, controlled probe wording
present, and on the 150-DPI render: no overlaps, no clipping, no broken chars.
Renders previews + contact sheet. Writes validation_report.json.
"""
from __future__ import annotations

import json
import os

import fitz
from PIL import Image, ImageDraw, ImageFont

from round4_candidates import CANDIDATES

HERE = os.path.dirname(os.path.abspath(__file__))
RESUMES = os.path.join(HERE, "resumes"); PREVIEWS = os.path.join(HERE, "previews")
os.makedirs(PREVIEWS, exist_ok=True)
DPI = 150; ZOOM = DPI / 72.0


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


def detect(page):
    probs = []
    lines = line_boxes(page)
    for i in range(len(lines)):
        ri, ti, bi = lines[i]
        for j in range(i + 1, len(lines)):
            rj, tj, bj = lines[j]
            if bi == bj:
                continue
            if (_ov(ri.y0, ri.y1, rj.y0, rj.y1) > 0.45 * min(ri.height or 1, rj.height or 1)
                    and _ov(ri.x0, ri.x1, rj.x0, rj.x1) > 0.25 * (min(ri.width, rj.width) or 1)):
                probs.append(f"overlap '{ti[:25]}'|'{tj[:25]}'")
    pr = page.rect
    for r, txt, _ in lines:
        if r.x0 < pr.x0 - 2 or r.y0 < pr.y0 - 2 or r.x1 > pr.x1 + 2 or r.y1 > pr.y1 + 2:
            probs.append(f"clipped '{txt[:25]}'")
    if "�" in page.get_text():
        probs.append("broken_char")
    return probs


def probe_text(c):
    if c.get("skills_line_note"):
        return c["skills_line_note"]
    if c.get("work_auth"):
        return c["work_auth"]
    if c["experience"][0].get("emp_type_label"):
        return c["experience"][0]["emp_type_label"]
    if c.get("certifications"):
        return c["certifications"][0]
    return ""


def validate_one(c):
    path = os.path.join(RESUMES, f"{c['id']}.pdf")
    res = {"id": c["id"], "category": c["category"], "controlled": c["controlled"],
           "status": "PASS", "problems": []}
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        res["status"] = "FAIL"; res["problems"].append("missing/empty"); return res, []
    doc = fitz.open(path); res["page_count"] = doc.page_count; res["size_bytes"] = os.path.getsize(path)
    if doc.page_count != c["expected_pages"]:
        res["problems"].append(f"pages {doc.page_count}!={c['expected_pages']}")
    text = "\n".join(p.get_text() for p in doc); up = text.upper(); norm = " ".join(text.split())
    if c["name"].split()[-1].upper() not in up:
        res["problems"].append("surname missing")
    if c["email"].upper() not in up:
        res["problems"].append("email missing")
    for lbl in ("EXPERIENCE", "EDUCATION"):
        if lbl not in up:
            res["problems"].append(f"{lbl} section missing")
    pt = probe_text(c)
    if pt and not all(w in norm for w in pt.split()):
        res["problems"].append("controlled probe text incomplete")
    previews = []
    mat = fitz.Matrix(ZOOM, ZOOM)
    for i, page in enumerate(doc):
        if not (page.get_text().strip() or page.get_images() or page.get_drawings()):
            res["problems"].append(f"page {i+1} blank")
        res["problems"] += detect(page)
        p = os.path.join(PREVIEWS, f"{c['id']}.png")
        page.get_pixmap(matrix=mat, alpha=False).save(p); previews.append(p)
    doc.close()
    if res["problems"]:
        res["status"] = "FAIL"
    return res, previews


def contact_sheet(items, out, cols=6, tw=205):
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except Exception:  # noqa
        font = ImageFont.load_default()
    thumbs = []
    for label, p in items:
        im = Image.open(p).convert("RGB"); th = int(im.height * (tw / im.width))
        im = im.resize((tw, th), Image.LANCZOS); cap = 20
        canv = Image.new("RGB", (tw, th + cap), "white"); canv.paste(im, (0, cap))
        d = ImageDraw.Draw(canv); d.rectangle([0, 0, tw, cap], fill=(35, 74, 125))
        d.text((5, 3), label, fill="white", font=font)
        d.rectangle([0, 0, tw - 1, th + cap - 1], outline=(185, 185, 185)); thumbs.append(canv)
    rows = (len(thumbs) + cols - 1) // cols; cw, ch = tw + 8, max(t.height for t in thumbs) + 8
    sheet = Image.new("RGB", (cols * cw + 8, rows * ch + 8), "white")
    for i, t in enumerate(thumbs):
        r, cc = divmod(i, cols); sheet.paste(t, (8 + cc * cw, 8 + r * ch))
    sheet.save(out); return out


def main():
    results, items = [], []
    for c in CANDIDATES:
        res, prev = validate_one(c); results.append(res)
        for p in prev:
            items.append((c["id"], p))
        d = "" if res["status"] == "PASS" else "  :: " + "; ".join(res["problems"][:2])
        print(f"  {res['id']} [{res['category']:<20}] {res['status']}{d}")
    sheet = contact_sheet(items, os.path.join(HERE, "contact_sheet.png"))
    summary = {"total": len(results), "pass": sum(r["status"] == "PASS" for r in results),
               "fail": sum(r["status"] == "FAIL" for r in results)}
    json.dump({"summary": summary, "render_dpi": DPI, "contact_sheet": sheet, "results": results},
              open(os.path.join(HERE, "validation_report.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\n  {summary['pass']} PASS / {summary['fail']} FAIL of {summary['total']}")
    print(f"  contact sheet -> {sheet}")


if __name__ == "__main__":
    main()
