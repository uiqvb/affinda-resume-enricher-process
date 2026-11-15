"""build_round3_metadata.py — ground_truth_round3.json + test_manifest_round3.csv."""
from __future__ import annotations

import csv
import json
import os

from round3_candidates import CANDIDATES

HERE = os.path.dirname(os.path.abspath(__file__))


def build():
    gt = {}
    for c in CANDIDATES:
        gt[c["id"]] = {
            "test_id": c["id"], "filename": f"{c['id']}.pdf", "category": c["category"],
            "controlled_variable": c["controlled"], "exact_source_evidence": c["source_evidence"],
            "candidate_identity": {"name": c["name"], "title": c["title"], "email": c["email"]},
            "work_experience": [{"jobTitle": e["title"], "employer": e["org"],
                                 "date_display": e["date_display"],
                                 "employment_type_label": e.get("emp_type_label", "")}
                                for e in c["experience"]],
            "skills_claimed": c.get("skills", []),
            "skills_line_note": c.get("skills_line_note", ""),
            "certifications": c.get("certifications", []),
            "work_authorisation_text": c.get("work_auth"),
            "expected_parser_behaviour": c["expected"],
            "acceptable_alternate_interpretations": c["acceptable"],
            "confirmed_failure_if": c["confirmed_failure_if"],
            "inconclusive_if": c["inconclusive_if"],
            "existing_affinda_field_to_check": c["existing_field_to_check"],
            "expected_pages": c["expected_pages"],
        }
    json.dump(gt, open(os.path.join(HERE, "ground_truth_round3.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)

    cols = ["test_id", "filename", "category", "controlled_variable", "exact_source_evidence",
            "existing_affinda_field_to_check", "expected_parser_behaviour",
            "acceptable_alternates", "confirmed_failure_if", "inconclusive_if", "expected_pages"]
    with open(os.path.join(HERE, "test_manifest_round3.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for c in CANDIDATES:
            w.writerow({"test_id": c["id"], "filename": f"{c['id']}.pdf", "category": c["category"],
                        "controlled_variable": c["controlled"], "exact_source_evidence": c["source_evidence"],
                        "existing_affinda_field_to_check": c["existing_field_to_check"],
                        "expected_parser_behaviour": json.dumps(c["expected"], ensure_ascii=False),
                        "acceptable_alternates": " | ".join(c["acceptable"]),
                        "confirmed_failure_if": c["confirmed_failure_if"],
                        "inconclusive_if": c["inconclusive_if"], "expected_pages": c["expected_pages"]})
    print(f"ground_truth_round3.json ({len(gt)}) + test_manifest_round3.csv written -> {HERE}")


if __name__ == "__main__":
    build()
