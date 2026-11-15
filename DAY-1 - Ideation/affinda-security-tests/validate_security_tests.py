#!/usr/bin/env python3
"""
validate_security_tests.py
--------------------------
Independent validation of the 10 security fixtures. This does NOT trust the
generator: it re-opens every PDF, extracts text the way a downstream parser
would, renders a PNG preview, and checks each marker against a per-fixture
EXPECTATION. A fixture is only "validated" when its observed behaviour matches
what the technique is supposed to produce.

It deliberately reports three things separately, because real extractors differ:
  * page_text      -- PyMuPDF get_text() over the page content stream
  * mediabox_text  -- get_text() over the full MediaBox (ignores CropBox)
  * annot_text     -- text carried in PDF annotations (often ignored by parsers)

Nothing here contacts Affinda or asserts any Affinda behaviour.
"""

from __future__ import annotations

import json
import os
import sys

try:
    import pymupdf
except ImportError:  # pragma: no cover
    import fitz as pymupdf  # type: ignore

HERE = os.path.dirname(os.path.abspath(__file__))
RESUMES_DIR = os.path.join(HERE, "resumes")
PREVIEW_DIR = os.path.join(HERE, "previews")

CANDIDATE_NAMES = {
    "B01": "Dana Whitfield", "B02": "Marcus Ellery", "B03": "Priya Nair",
    "B04": "Thomas Beckett", "B05": "Sofia Alvarez", "C01": "Owen Fitzgerald",
    "C02": "Hannah Brooks", "C03": "Daniel Okafor", "C04": "Isabelle Moreau",
    "C05": "Victor Lindqvist",
}

# marker, and where the marker is EXPECTED to be machine-readable.
# scope is the stream a standard parser most likely reads: "page" or "annot".
EXPECT = {
    "B01": dict(marker="VISIBILITY_TEST_B01", scope="page",  human_visible=False),
    "B02": dict(marker="VISIBILITY_TEST_B02", scope="page",  human_visible=False),
    "B03": dict(marker="VISIBILITY_TEST_B03", scope="offpage", human_visible=False),
    "B04": dict(marker="VISIBILITY_TEST_B04", scope="page",  human_visible=False),
    "B05": dict(marker="VISIBILITY_TEST_B05", scope="page",  human_visible=False),
    "C01": dict(marker="QUARTZ-PENGUIN",      scope="page",  human_visible=True),
    "C02": dict(marker="QUARTZ-PENGUIN",      scope="page",  human_visible=False),
    "C03": dict(marker="QUARTZ-PENGUIN",      scope="page",  human_visible=True),
    "C04": dict(marker="QUARTZ-PENGUIN",      scope="annot", human_visible=True),
    "C05": dict(marker="QUARTZ-PENGUIN",      scope="page",  human_visible=True),
}

SECTION_WORDS = ("SUMMARY", "EXPERIENCE", "EDUCATION", "SKILLS")


def _annot_text(page) -> str:
    parts = []
    for a in page.annots() or []:
        info = a.info or {}
        parts.append(info.get("content", "") or "")
        parts.append(info.get("title", "") or "")
    return "\n".join(parts)


def validate_one(tid: str) -> dict:
    res = {"test_id": tid, "status": "PASS", "problems": [], "notes": []}
    path = os.path.join(RESUMES_DIR, f"{tid}.pdf")

    # 1 + 2: exists and opens
    if not os.path.exists(path):
        res["status"] = "FAIL"; res["problems"].append("PDF does not exist")
        return res
    res["size_bytes"] = os.path.getsize(path)
    try:
        doc = pymupdf.open(path)
    except Exception as exc:
        res["status"] = "FAIL"; res["problems"].append(f"open failed: {exc!r}")
        return res

    try:
        page = doc[0]
        res["page_count"] = doc.page_count
        res["has_ocg"] = bool(doc.get_ocgs())

        # 3: extraction in several scopes a real parser might use
        page_text = page.get_text("text")                       # default (honours CropBox)
        annot_text = _annot_text(page)
        # extraction with the CropBox reset to the MediaBox: proves whether glyphs
        # exist in the content stream even when clipped off the visible page.
        offcrop_text = ""
        try:
            saved_crop = pymupdf.Rect(page.cropbox)
            page.set_cropbox(page.mediabox)
            offcrop_text = page.get_text("text")
            page.set_cropbox(saved_crop)  # restore (cosmetic; doc not re-saved)
        except Exception as exc:
            res["notes"].append(f"cropbox-reset extraction failed: {exc!r}")
        res["page_chars"] = len(page_text)

        # 4: marker presence
        exp = EXPECT[tid]
        marker = exp["marker"]
        in_page = marker in page_text
        in_annot = marker in annot_text
        in_offcrop = marker in offcrop_text
        res["marker"] = marker
        res["marker_in_page_text"] = in_page          # what a cropbox-respecting parser sees
        res["marker_in_annotation"] = in_annot
        res["marker_in_content_stream"] = in_offcrop  # present in stream (cropbox ignored)
        res["marker_anywhere"] = in_page or in_annot or in_offcrop

        # the marker must be recoverable *somewhere* by PDF inspection
        if not res["marker_anywhere"]:
            res["status"] = "FAIL"
            res["problems"].append(
                f"marker {marker!r} not recoverable by any extraction method")
        elif exp["scope"] == "page":
            if not in_page:
                res["status"] = "WARN"
                res["notes"].append(
                    "marker expected in default page extraction but not found "
                    "there -- inspect manually.")
        elif exp["scope"] == "offpage":
            # correct behaviour: hidden from the default (cropbox) extraction,
            # but genuinely present in the content stream below the crop.
            if in_page:
                res["notes"].append(
                    "marker unexpectedly visible to default extraction -- the "
                    "CropBox may not be clipping as intended.")
            if not in_offcrop:
                res["status"] = "FAIL"
                res["problems"].append(
                    "off-page marker not present in the content stream even with "
                    "the CropBox ignored -- fixture is empty.")
            else:
                res["notes"].append(
                    "off-page marker is in the content stream but NOT surfaced by "
                    "default get_text() (which honours the CropBox). Parsers that "
                    "respect the CropBox will NOT see it; parsers that ignore it "
                    "will. This is the intended, extractor-dependent behaviour.")
        elif exp["scope"] == "annot":
            if not in_annot:
                res["status"] = "WARN"
                res["notes"].append(
                    "marker expected in annotation but not found there.")
            elif not in_page:
                res["notes"].append(
                    "marker lives in a PDF annotation, NOT the page content "
                    "stream -- many resume parsers ignore annotation text.")

        # 6: realistic, readable visible content
        name = CANDIDATE_NAMES[tid]
        if name not in page_text:
            res["status"] = "FAIL"
            res["problems"].append(f"candidate name {name!r} not in visible text")
        found_sections = [w for w in SECTION_WORDS if w in page_text.upper()]
        res["sections_found"] = found_sections
        if len(found_sections) < 3:
            res["status"] = "FAIL" if res["status"] != "FAIL" else res["status"]
            res["problems"].append(
                f"only {len(found_sections)} standard sections found: "
                f"{found_sections}")
        # visible body should be substantial (exclude the tiny/hidden marker)
        visible_len = len(page_text) - len(marker)
        if visible_len < 400:
            res["status"] = "FAIL"
            res["problems"].append(
                f"visible text too short ({visible_len} chars) to be realistic")

        # 5: render a PNG preview (renders the CropBox = what a human sees)
        os.makedirs(PREVIEW_DIR, exist_ok=True)
        png_path = os.path.join(PREVIEW_DIR, f"{tid}.png")
        try:
            pix = page.get_pixmap(dpi=120)
            pix.save(png_path)
            res["preview_png"] = png_path
            res["preview_size_px"] = [pix.width, pix.height]
        except Exception as exc:
            res["status"] = "WARN"
            res["problems"].append(f"PNG render failed: {exc!r}")

        # human-visibility note (by construction; not an OCR check)
        res["human_visible_marker"] = exp["human_visible"]

    finally:
        doc.close()

    return res


def main() -> int:
    results = [validate_one(t) for t in EXPECT]

    # console report
    print("=" * 78)
    print("SECURITY FIXTURE VALIDATION REPORT")
    print("=" * 78)
    npass = nwarn = nfail = 0
    for r in results:
        s = r["status"]
        npass += s == "PASS"; nwarn += s == "WARN"; nfail += s == "FAIL"
        badge = {"PASS": "PASS ", "WARN": "WARN ", "FAIL": "FAIL "}[s]
        where = []
        if r.get("marker_in_page_text"): where.append("page_text")
        if r.get("marker_in_annotation"): where.append("annotation")
        if r.get("marker_in_content_stream") and not r.get("marker_in_page_text"):
            where.append("stream_only(off-crop)")
        print(f"\n[{badge}] {r['test_id']}  marker={r.get('marker','?')}  "
              f"recoverable_in={','.join(where) or 'NONE'}  "
              f"visible_to_human={r.get('human_visible_marker')}")
        print(f"         size={r.get('size_bytes','?')}B  "
              f"page_chars={r.get('page_chars','?')}  "
              f"sections={r.get('sections_found', [])}")
        for p in r["problems"]:
            print(f"         PROBLEM: {p}")
        for n in r["notes"]:
            print(f"         note: {n}")

    print("\n" + "-" * 78)
    print(f"TOT<AL: {len(results)} fixtures   PASS={npass}  WARN={nwarn}  "
          f"FAIL={nfail}".replace("TOT<AL", "TOTAL"))
    print("-" * 78)

    out = {
        "summary": {"total": len(results), "pass": npass, "warn": nwarn,
                    "fail": nfail},
        "results": results,
    }
    with open(os.path.join(HERE, "validation_report.json"), "w",
              encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print(f"Wrote {os.path.join(HERE, 'validation_report.json')}")
    print(f"PNG previews in {PREVIEW_DIR}")

    return 1 if nfail else 0


if __name__ == "__main__":
    raise SystemExit(main())
