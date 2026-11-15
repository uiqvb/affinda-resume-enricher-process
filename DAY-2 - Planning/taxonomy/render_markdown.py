#!/usr/bin/env python3
"""Render the three taxonomy CSVs into readable, grouped Markdown tables.
Groups rows by category (constant fields go in the section heading) so each
table stays narrow. Run:  python render_markdown.py"""
import csv, os
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))


def esc(s):
    return (s or "").replace("|", "\\|").strip()


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def render(csv_name, md_name, title, blurb, cat_key, cols, realism_key="realism",
           extra_head=None):
    """cols: list of (header, csv_field) for the per-row table (narrow)."""
    rows = load(csv_name)
    # group preserving order of first appearance
    groups = OrderedDict()
    for r in rows:
        groups.setdefault(r[cat_key], []).append(r)
    out = [f"# {title}\n", blurb, ""]
    out.append(f"*{len(rows)} variations · grouped by category · "
               f"generated from `{csv_name}`.*\n")
    # table of contents / counts
    out.append("| Category | Count | Realism |")
    out.append("|---|:--:|---|")
    for cat, rs in groups.items():
        out.append(f"| {cat} | {len(rs)} | {rs[0].get(realism_key,'')} |")
    out.append("")
    # per-category tables
    for cat, rs in groups.items():
        realism = rs[0].get(realism_key, "")
        ctl = " · **positive control**" if rs[0].get("is_control") == "True" else ""
        out.append(f"\n## {cat} — {len(rs)} · {realism}{ctl}\n")
        header = "| " + " | ".join(h for h, _ in cols) + " |"
        sep = "|" + "|".join("---" for _ in cols) + "|"
        out.append(header)
        out.append(sep)
        for r in rs:
            cells = []
            for _, field in cols:
                val = esc(r.get(field, ""))
                cells.append(val)
            out.append("| " + " | ".join(cells) + " |")
    text = "\n".join(out) + "\n"
    with open(os.path.join(HERE, md_name), "w", encoding="utf-8") as f:
        f.write(text)
    return len(rows)


if __name__ == "__main__":
    n1 = render(
        "education_status_100.csv", "education_status_100.md",
        "Education Completion Status — 100 variations",
        "Does any phrasing produce a **structured completion status**, and does a terminal "
        "year ever stop being treated as a conferral date? (Prior rounds: 0/16 status.)",
        "status_category",
        [("ID", "test_id"), ("Résumé line", "exact_source_line"),
         ("Should return", "expected_completion_status"), ("Fails if", "failure_if")])

    n2 = render(
        "certification_status_100.csv", "certification_status_100.md",
        "Certification Status — 100 variations",
        "Held certs extract fine; the gap is the **validity status**. `cert_domain` flags "
        "compliance-sensitive certs where a wrong signal is a liability, not just wasted time.",
        "validity_category",
        [("ID", "test_id"), ("Domain", "cert_domain"),
         ("Résumé line", "exact_source_line"),
         ("Should return", "expected_validity_status"), ("Fails if", "failure_if")])

    n3 = render(
        "skill_claim_strength_100.csv", "skill_claim_strength_100.md",
        "Skill Claim Strength — 100 variations",
        "The realistic **proficiency spectrum** (denial is the far end, only 10 rows). The "
        "`distractor_fp_trap` rows measure **precision** — the affirmed skill must survive.",
        "claim_strength",
        [("ID", "test_id"), ("Résumé line", "exact_source_line"),
         ("Should return", "expected_behaviour"), ("Fails if", "failure_if")])

    print(f"education={n1}  certification={n2}  skill={n3}  -> 3 .md files written")
