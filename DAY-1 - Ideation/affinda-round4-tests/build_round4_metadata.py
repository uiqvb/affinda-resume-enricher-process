"""build_round4_metadata.py — ground_truth_round4.json + test_manifest_round4.csv."""
from __future__ import annotations

import csv
import json
import os

from round4_candidates import CANDIDATES, REFERENCE_DATE

HERE = os.path.dirname(os.path.abspath(__file__))


def build():
    gt = {"_meta": {"reference_date": REFERENCE_DATE,
                    "note": "Expectations are from synthetic source data, not parser output."}}
    for c in CANDIDATES:
        gt[c["id"]] = {
            "test_id": c["id"], "filename": f"{c['id']}.pdf", "category": c["category"],
            "controlled_variable": c["controlled"], "exact_source_statement": c["source_evidence"],
            "candidate_identity": {"name": c["name"], "title": c["title"], "email": c["email"]},
            "work_experience": [{"jobTitle": e["title"], "employer": e["org"],
                                 "date_display": e["date_display"],
                                 "employment_type_label": e.get("emp_type_label", "")}
                                for e in c["experience"]],
            "skills_affirmed": c.get("skills", []),
            "skills_line_note": c.get("skills_line_note"),
            "certifications": c.get("certifications", []),
            "work_authorisation_text": c.get("work_auth"),
            "correct_intended_interpretation": c["expected"],
            "acceptable_alternate_interpretations": c["acceptable"],
            "relevant_existing_affinda_field": c["existing_field_to_check"],
            "confirmed_failure_if": c["confirmed_failure_if"],
            "partial_information_loss_if": c["partial_loss_if"],
            "inconclusive_if": c["inconclusive_if"],
            "paired_test_id": c.get("paired_with"),
            "multi_variable_cannot_isolate": c.get("multi_variable", False),
            "expected_pages": c["expected_pages"],
        }
    json.dump(gt, open(os.path.join(HERE, "ground_truth_round4.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)

    cols = ["test_id", "filename", "category", "controlled_variable", "exact_source_statement",
            "relevant_existing_affinda_field", "correct_intended_interpretation",
            "acceptable_alternates", "confirmed_failure_if", "partial_information_loss_if",
            "inconclusive_if", "paired_test_id", "multi_variable", "expected_pages"]
    with open(os.path.join(HERE, "test_manifest_round4.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for c in CANDIDATES:
            w.writerow({"test_id": c["id"], "filename": f"{c['id']}.pdf", "category": c["category"],
                        "controlled_variable": c["controlled"], "exact_source_statement": c["source_evidence"],
                        "relevant_existing_affinda_field": c["existing_field_to_check"],
                        "correct_intended_interpretation": json.dumps(c["expected"], ensure_ascii=False),
                        "acceptable_alternates": " | ".join(c["acceptable"]),
                        "confirmed_failure_if": c["confirmed_failure_if"],
                        "partial_information_loss_if": c["partial_loss_if"],
                        "inconclusive_if": c["inconclusive_if"], "paired_test_id": c.get("paired_with") or "",
                        "multi_variable": c.get("multi_variable", False), "expected_pages": c["expected_pages"]})
    print(f"ground_truth_round4.json ({len(CANDIDATES)}) + test_manifest_round4.csv -> {HERE}")


if __name__ == "__main__":
    build()
