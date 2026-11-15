"""
build_metadata.py — Generate ground_truth.json (Phase 4) and test_manifest.csv
(Phase 5) for the 20 synthetic resumes.

IMPORTANT: ground truth is derived from candidates.py (the original synthetic
candidate data), NOT by extracting text from the generated PDFs.

Usage:
    python build_metadata.py
"""
from __future__ import annotations

import csv
import json
import os

from candidates import CANDIDATES

HERE = os.path.dirname(os.path.abspath(__file__))


def employment_records(c):
    recs = []
    for exp in c["experience"]:
        recs.append({
            "jobTitle": exp["title"],
            "employer": exp["org"],
            "location": exp.get("location", ""),
            "startDate_display": exp.get("start", ""),
            "endDate_display": exp.get("end", "") or ("(none stated)" if exp["end_iso"] == "present" else ""),
            "startDate_iso": exp["start_iso"],
            "endDate_iso": exp["end_iso"],   # "present" => ongoing/current
            "isCurrent": exp["end_iso"] == "present",
        })
    return recs


def education_records(c):
    recs = []
    for ed in c["education"]:
        incomplete = ("INCOMPLETE" in ed["degree"].upper()
                      or "IN PROGRESS" in ed.get("note", "").upper()
                      or (ed.get("end", "") == "" and ed.get("start")))
        recs.append({
            "degree": ed["degree"],
            "institution": ed["institution"],
            "location": ed.get("location", ""),
            "startDate": ed.get("start", ""),
            "endDate": ed.get("end", "") or "(none stated)",
            "note": ed.get("note", ""),
            "isComplete": not incomplete,
        })
    return recs


def expected_skills(c):
    """Skills a correct parser should surface. For F04 the skills live inside
    the experience bullets, so the expected set is the embedded list."""
    if c.get("skills"):
        return list(c["skills"])
    if c.get("skills_embedded_in_experience"):
        return list(c["skills_embedded_in_experience"])
    return []


def build_ground_truth():
    gt = {}
    for c in CANDIDATES:
        gt[c["id"]] = {
            "test_id": c["id"],
            "filename": f"{c['id']}.pdf",
            "category": c["category"],
            "difficulty": c["difficulty"],
            "candidate_name": c["name"],
            "expected_contact": {
                "emails": list(c.get("emails", [])),
                "phone": c.get("phone", ""),
                "location": c.get("location", ""),
                "links": c.get("links", {}),
            },
            "expected_employment": employment_records(c),
            "expected_education": education_records(c),
            "expected_skills": expected_skills(c),
            "skills_source": ("experience_bullets"
                              if not c.get("skills") and c.get("skills_embedded_in_experience")
                              else "skills_section"),
            "intentional_complexity": c["intentional_complexity"],
            "known_ambiguities": c["known_ambiguities"],
            "acceptable_interpretations": c["acceptable_interpretations"],
            "expected_page_count": c["expected_pages"],
            "fields_to_inspect": c["fields_to_inspect"],
            "layout": c["layout"],
        }
    out = os.path.join(HERE, "ground_truth.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(gt, f, indent=2, ensure_ascii=False)
    return out, gt


def _parser_behaviour(c):
    if c["category"] == "A":
        return "Extract all fields accurately with high confidence."
    if c["category"] == "D":
        return "Represent the employment-history challenge without merging, dropping, or contradicting roles."
    if c["category"] == "E":
        if c["layout"] == "scanned":
            return "Requires OCR; degraded extraction acceptable, empty extraction is a documented failure mode."
        return "Reconstruct correct reading order and attribute content to the right sections."
    return "Handle the ambiguity without fabricating false certainty; ideally flag or lower confidence."


def _failure_indicators(c):
    base = {
        "A": "Missing fields, wrong dates, or mis-split roles.",
        "D": "Overlapping/promoted roles merged or dropped; wrong employer grouping; invented end dates.",
        "E": "Content from a column/page/region dropped or interleaved; empty extraction on the scanned file.",
        "F": "Silently picking one of two conflicting values as certain; dropping the second email; marking an incomplete degree as completed.",
    }
    return base[c["category"]]


def build_manifest():
    out = os.path.join(HERE, "test_manifest.csv")
    cols = ["test_id", "filename", "category", "difficulty", "test_hypothesis",
            "expected_pages", "key_fields_to_evaluate", "intentional_ambiguity",
            "expected_parser_behaviour", "potential_failure_indicators"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for c in CANDIDATES:
            ambiguity = "; ".join(c["known_ambiguities"]) if c["known_ambiguities"] else "none"
            w.writerow({
                "test_id": c["id"],
                "filename": f"{c['id']}.pdf",
                "category": c["category"],
                "difficulty": c["difficulty"],
                "test_hypothesis": c["test_hypothesis"],
                "expected_pages": c["expected_pages"],
                "key_fields_to_evaluate": ", ".join(c["fields_to_inspect"]),
                "intentional_ambiguity": ambiguity,
                "expected_parser_behaviour": _parser_behaviour(c),
                "potential_failure_indicators": _failure_indicators(c),
            })
    return out


def main():
    gt_path, gt = build_ground_truth()
    mf_path = build_manifest()
    print(f"ground_truth.json -> {gt_path}  ({len(gt)} entries)")
    print(f"test_manifest.csv -> {mf_path}")


if __name__ == "__main__":
    main()
