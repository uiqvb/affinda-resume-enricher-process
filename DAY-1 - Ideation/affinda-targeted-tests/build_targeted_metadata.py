"""
build_targeted_metadata.py — Phase 4/5 metadata for the 45 targeted tests.

Writes:
  ground_truth_targeted.json   (expectations derived from targeted_candidates.py)
  test_manifest_targeted.csv

Ground truth comes from the synthetic source, never from PDF extraction.
"""
from __future__ import annotations

import csv
import json
import os

from targeted_candidates import CANDIDATES

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE_NAME = {1: "ongoing-employment-dates", 2: "employer-attribution",
              3: "education-completion-status"}


def _expected_work(c):
    out = []
    for e in c["experience"]:
        out.append({"jobTitle": e["title"], "employer_as_written": e["org"],
                    "date_display": e["date_display"], "location": e.get("location", "")})
    return out


def _expected_education(c):
    out = []
    for ed in c["education"]:
        out.append({"qualification": ed["degree"], "institution": ed["institution"],
                    "date_display": ed["date_display"], "status_note": ed.get("note", "")})
    return out


def build_ground_truth():
    gt = {}
    for c in CANDIDATES:
        gt[c["id"]] = {
            "test_id": c["id"], "filename": f"{c['id']}.pdf",
            "phase": c["phase"], "category": PHASE_NAME[c["phase"]],
            "layout": c["layout"],
            "candidate_identity": {"name": c["name"], "title": c["title"],
                                   "email": c["email"], "phone": c.get("phone", ""),
                                   "location": c.get("location", "")},
            "expected_work_experience": _expected_work(c),
            "expected_education": _expected_education(c),
            "controlled_variable": c["controlled"],
            "exact_source_evidence": c["source_evidence"],
            "expected_parser_behaviour": c["expected"],
            "acceptable_alternate_interpretations": c["acceptable"],
            "confirmed_failure_if": c["confirmed_failure_if"],
            "inconclusive_if": c["inconclusive_if"],
            "expected_pages": c["expected_pages"],
        }
    path = os.path.join(HERE, "ground_truth_targeted.json")
    json.dump(gt, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    return path, gt


def build_manifest():
    path = os.path.join(HERE, "test_manifest_targeted.csv")
    cols = ["test_id", "filename", "phase", "category", "layout",
            "controlled_variable", "exact_source_evidence",
            "expected_parser_behaviour", "acceptable_alternates",
            "confirmed_failure_if", "inconclusive_if", "expected_pages"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for c in CANDIDATES:
            w.writerow({
                "test_id": c["id"], "filename": f"{c['id']}.pdf", "phase": c["phase"],
                "category": PHASE_NAME[c["phase"]], "layout": c["layout"],
                "controlled_variable": c["controlled"],
                "exact_source_evidence": c["source_evidence"],
                "expected_parser_behaviour": json.dumps(c["expected"], ensure_ascii=False),
                "acceptable_alternates": " | ".join(c["acceptable"]),
                "confirmed_failure_if": c["confirmed_failure_if"],
                "inconclusive_if": c["inconclusive_if"],
                "expected_pages": c["expected_pages"],
            })
    return path


def main():
    gp, gt = build_ground_truth()
    mp = build_manifest()
    print(f"ground_truth_targeted.json -> {gp} ({len(gt)} entries)")
    print(f"test_manifest_targeted.csv -> {mp}")


if __name__ == "__main__":
    main()
