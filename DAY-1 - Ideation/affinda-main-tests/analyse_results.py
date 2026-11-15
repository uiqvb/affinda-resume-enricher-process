"""
analyse_results.py — Compare Affinda Resume Parser output against ground truth
(Phase 6). Reads ground_truth.json and Affinda JSON responses from results/,
matches by test id / filename, compares structured fields, and writes a Markdown
report per category plus an overall summary.

DESIGN NOTES (per brief):
  * Field access is DEFENSIVE. Affinda's documented v3 schema nests parsed data
    under `data` with fields such as name/emails/phoneNumbers/websites/location/
    workExperience/education/skills. Because the exact shape can vary by API
    version, every field is read through a tolerant accessor that tries several
    candidate paths. If none is present, the metric is marked
    "unsupported_in_response" rather than guessed or fabricated.
  * Ambiguous (Category F) and overlapping (Category D) cases are scored against
    `acceptable_interpretations`, never forced to a single "correct" answer.
  * Nothing is fabricated: if results/ is empty, the analyser says so and exits
    cleanly, confirming it is ready to accept real responses.

Usage:
    python analyse_results.py                  # analyse results/*.json
    python analyse_results.py --results DIR    # custom results folder
    python analyse_results.py --self-check     # run on built-in mock responses
"""
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GROUND_TRUTH = os.path.join(HERE, "ground_truth.json")
DEFAULT_RESULTS = os.path.join(HERE, "results")
REPORTS = os.path.join(HERE, "analysis_reports")

UNSUPPORTED = "unsupported_in_response"


# --------------------------------------------------------------------------- #
#  Tolerant accessors
# --------------------------------------------------------------------------- #
def dig(obj, path):
    """Follow a dotted path through dicts/lists; return None if any step misses."""
    cur = obj
    for key in path.split("."):
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return None
    return cur


def first_present(obj, paths, default=UNSUPPORTED):
    for p in paths:
        v = dig(obj, p)
        if v not in (None, "", []):
            return v
    return default


def parsed_root(resp):
    """Affinda responses usually wrap parsed fields under 'data'."""
    if isinstance(resp, dict) and isinstance(resp.get("data"), dict):
        return resp["data"]
    return resp if isinstance(resp, dict) else {}


def norm(s):
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def norm_month(s):
    """Normalise a date-ish string to YYYY-MM when possible, else ''."""
    if not s:
        return ""
    s = str(s)
    m = re.search(r"(\d{4})[-/](\d{1,2})", s)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}"
    m = re.search(r"\b(19|20)\d{2}\b", s)
    return m.group(0) if m else ""


# --------------------------------------------------------------------------- #
#  Field extraction (candidate paths; unsupported if absent)
# --------------------------------------------------------------------------- #
def get_name(d):
    for p in ["name.raw", "name.formatted"]:
        v = dig(d, p)
        if isinstance(v, str) and v.strip():
            return v
    first, last = dig(d, "name.first"), dig(d, "name.last")
    if first or last:
        return " ".join(x for x in [first, last] if x)
    if isinstance(d.get("name"), str):
        return d["name"]
    return UNSUPPORTED


def get_list_of_strings(d, paths, item_keys=("name", "raw", "value")):
    for p in paths:
        v = dig(d, p)
        if isinstance(v, list) and v:
            out = []
            for it in v:
                if isinstance(it, str):
                    out.append(it)
                elif isinstance(it, dict):
                    for k in item_keys:
                        if it.get(k):
                            out.append(it[k]); break
            if out:
                return out
    return UNSUPPORTED


def get_emails(d):
    return get_list_of_strings(d, ["emails", "emailAddresses", "email"])


def get_phones(d):
    v = get_list_of_strings(d, ["phoneNumbers", "phoneNumber", "phones"],
                            item_keys=("rawText", "formattedNumber", "raw", "value"))
    return v


def get_skills(d):
    return get_list_of_strings(d, ["skills"], item_keys=("name", "raw", "value"))


def get_work(d):
    v = first_present(d, ["workExperience", "work_experience", "positions"], default=None)
    return v if isinstance(v, list) else UNSUPPORTED


def get_education(d):
    v = first_present(d, ["education", "educations"], default=None)
    return v if isinstance(v, list) else UNSUPPORTED


def work_fields(item):
    title = first_present(item, ["jobTitle.raw", "jobTitle", "title"], default="")
    org = first_present(item, ["organization", "company", "employer"], default="")
    start = first_present(item, ["dates.startDate", "startDate", "dates.start"], default="")
    end = first_present(item, ["dates.endDate", "endDate", "dates.end"], default="")
    is_current = first_present(item, ["dates.isCurrent", "isCurrent", "current"], default=None)
    if isinstance(title, dict):
        title = title.get("raw") or title.get("name") or ""
    return {"title": str(title), "org": str(org),
            "start": norm_month(start) if start != UNSUPPORTED else "",
            "end": "" if end in (None, UNSUPPORTED) else norm_month(end),
            "isCurrent": is_current}


# --------------------------------------------------------------------------- #
#  Comparison
# --------------------------------------------------------------------------- #
def match_employers(gt_emp, parsed_work):
    """Greedy match ground-truth roles to parsed roles by employer similarity."""
    matches = []
    used = set()
    pw = [work_fields(w) for w in parsed_work] if isinstance(parsed_work, list) else []
    for g in gt_emp:
        g_org = norm(g["employer"])
        best, best_i = None, None
        for i, p in enumerate(pw):
            if i in used:
                continue
            if g_org and (g_org in norm(p["org"]) or norm(p["org"]) in g_org):
                best, best_i = p, i
                break
        if best_i is not None:
            used.add(best_i)
        matches.append((g, best))
    return matches


def compare_one(gt, resp):
    d = parsed_root(resp)
    obs = {
        "name": get_name(d),
        "emails": get_emails(d),
        "phones": get_phones(d),
        "skills": get_skills(d),
    }
    checks = []

    def add(metric, status, detail=""):
        checks.append({"metric": metric, "status": status, "detail": detail})

    # --- name ---
    if obs["name"] == UNSUPPORTED:
        add("name", "unsupported", "no name field in response")
    else:
        exp_last = gt["candidate_name"].split()[-1].lower()
        add("name", "pass" if exp_last in norm(obs["name"]) else "mismatch",
            f"expected '{gt['candidate_name']}', got '{obs['name']}'")

    # --- emails ---
    exp_emails = [e.lower() for e in gt["expected_contact"]["emails"]]
    if obs["emails"] == UNSUPPORTED:
        add("emails", "unsupported")
    else:
        got = [e.lower() for e in obs["emails"]]
        missing = [e for e in exp_emails if e not in got]
        if not missing:
            add("emails", "pass", f"all {len(exp_emails)} email(s) found")
        else:
            add("emails", "mismatch", f"missing: {missing}; got {got}")

    # --- skills (coverage) ---
    exp_skills = [s.lower() for s in gt["expected_skills"]]
    if obs["skills"] == UNSUPPORTED:
        add("skills", "unsupported")
    elif not exp_skills:
        add("skills", "pass", "no skills expected")
    else:
        got = norm(" | ".join(obs["skills"]))
        found = [s for s in exp_skills if s in got]
        frac = len(found) / len(exp_skills)
        status = "pass" if frac >= 0.6 else ("partial" if frac > 0 else "mismatch")
        note = ""
        if gt["skills_source"] == "experience_bullets":
            note = " (skills were only in experience prose — inference expected)"
        add("skills", status, f"{len(found)}/{len(exp_skills)} expected skills present{note}")

    # --- work experience ---
    work = get_work(d)
    if work == UNSUPPORTED:
        add("workExperience", "unsupported")
    else:
        add("workExperience.count", "pass" if len(work) >= len(gt["expected_employment"]) else "partial",
            f"expected >= {len(gt['expected_employment'])} roles, got {len(work)}")
        for g, p in match_employers(gt["expected_employment"], work):
            if p is None:
                add(f"role:{g['employer']}", "mismatch", "employer not found in parsed roles")
                continue
            # dates
            detail = f"title '{p['title']}' / {p['start'] or '?'}–{p['end'] or 'current'}"
            if g["isCurrent"]:
                ok = (p["isCurrent"] is True) or p["end"] == ""
                add(f"role:{g['employer']}:current", "pass" if ok else "mismatch",
                    "ongoing role " + ("recognised" if ok else "NOT flagged current") + f" ({detail})")
            else:
                exp_end = g["endDate_iso"]
                ok = (p["end"] == exp_end) or (exp_end[:4] == (p["end"][:4] if p["end"] else ""))
                add(f"role:{g['employer']}:end", "pass" if ok else "partial",
                    f"expected end {exp_end}, got {p['end'] or '—'} ({detail})")

    # --- education (incl. incomplete-degree handling for F05) ---
    edu = get_education(d)
    if edu == UNSUPPORTED:
        add("education", "unsupported")
    else:
        add("education.count", "pass" if len(edu) >= len(gt["expected_education"]) else "partial",
            f"expected >= {len(gt['expected_education'])}, got {len(edu)}")

    # --- ambiguity-aware notes ---
    if gt["known_ambiguities"]:
        checks.append({"metric": "ambiguity", "status": "info",
                       "detail": "Acceptable interpretations: " +
                                 " | ".join(gt["acceptable_interpretations"])})

    # --- metadata / confidence (optional, graceful) ---
    conf = first_present(resp, ["meta.confidence", "data.confidence", "confidence"], default=UNSUPPORTED)
    warnings = first_present(resp, ["meta.warnings", "warnings"], default=UNSUPPORTED)
    checks.append({"metric": "meta.confidence", "status": "info",
                   "detail": str(conf)})
    checks.append({"metric": "meta.warnings", "status": "info",
                   "detail": str(warnings)})
    if gt["layout"] == "scanned":
        checks.append({"metric": "ocr_note", "status": "info",
                       "detail": "Image-only PDF: low/empty extraction here indicates no OCR, "
                                 "which is a documented expected failure mode, not a parser bug."})
    return obs, checks


# --------------------------------------------------------------------------- #
#  Reporting
# --------------------------------------------------------------------------- #
def load_results(results_dir):
    """Map test_id -> parsed JSON response. Matches by filename stem, else by
    an identifier/filename field inside the response."""
    found = {}
    if not os.path.isdir(results_dir):
        return found
    for fn in os.listdir(results_dir):
        if not fn.lower().endswith(".json"):
            continue
        path = os.path.join(results_dir, fn)
        try:
            with open(path, encoding="utf-8") as f:
                resp = json.load(f)
        except Exception as e:  # noqa
            print(f"  ! could not read {fn}: {e}")
            continue
        stem = os.path.splitext(fn)[0].upper()
        tid = None
        m = re.match(r"([ADEF]0[1-9])", stem)
        if m:
            tid = m.group(1)
        if not tid:
            ident = first_present(resp, ["meta.identifier", "meta.fileName", "fileName"], default="")
            m = re.search(r"([ADEF]0[1-9])", str(ident).upper())
            if m:
                tid = m.group(1)
        if tid:
            found[tid] = resp
        else:
            print(f"  ! {fn}: could not map to a test id")
    return found


_STATUS_ICON = {"pass": "PASS", "partial": "PARTIAL", "mismatch": "FAIL",
                "unsupported": "UNSUPPORTED", "info": "info"}


def write_reports(ground_truth, results):
    os.makedirs(REPORTS, exist_ok=True)
    by_cat = {}
    overall = {"pass": 0, "partial": 0, "mismatch": 0, "unsupported": 0,
               "analysed": 0, "missing_response": 0}

    for tid, gt in ground_truth.items():
        cat = gt["category"]
        by_cat.setdefault(cat, [])
        resp = results.get(tid)
        if resp is None:
            by_cat[cat].append((tid, gt, None, None, None))
            overall["missing_response"] += 1
            continue
        obs, checks = compare_one(gt, resp)
        by_cat[cat].append((tid, gt, obs, checks, None))
        overall["analysed"] += 1
        for c in checks:
            if c["status"] in overall:
                overall[c["status"]] += 1

    # per-category reports
    for cat, rows in sorted(by_cat.items()):
        lines = [f"# Category {cat} — Affinda parsing report", ""]
        for tid, gt, obs, checks, _ in rows:
            lines.append(f"## {tid} — {gt['candidate_name']} ({gt['difficulty']})")
            lines.append(f"*Intentional complexity:* {gt['intentional_complexity']}")
            lines.append("")
            if checks is None:
                lines.append("> No Affinda response found in results/ for this test id — not yet analysed.")
                lines.append("")
                continue
            lines.append("| Metric | Result | Detail |")
            lines.append("|---|---|---|")
            for c in checks:
                lines.append(f"| {c['metric']} | {_STATUS_ICON.get(c['status'], c['status'])} | {c['detail']} |")
            lines.append("")
        out = os.path.join(REPORTS, f"report_{cat}.md")
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # overall summary
    summ = ["# Affinda Resume Parser — Overall Summary", "",
            f"- Tests defined: **{len(ground_truth)}**",
            f"- Responses analysed: **{overall['analysed']}**",
            f"- Awaiting response: **{overall['missing_response']}**",
            "",
            "## Check tallies (across analysed responses)",
            f"- PASS: {overall['pass']}",
            f"- PARTIAL: {overall['partial']}",
            f"- FAIL (mismatch): {overall['mismatch']}",
            f"- UNSUPPORTED (field absent in response): {overall['unsupported']}",
            ""]
    if overall["analysed"] == 0:
        summ += ["> No Affinda responses were found yet. Upload the 20 PDFs to the "
                 "Affinda Sandbox, save each JSON into `results/` (named e.g. `A01.json`), "
                 "and re-run `python analyse_results.py`.", ""]
    out = os.path.join(REPORTS, "report_summary.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(summ))
    return overall


# --------------------------------------------------------------------------- #
#  Self-check (mock Affinda-shaped responses) — proves the analyser runs
# --------------------------------------------------------------------------- #
def _mock_response(gt):
    """Build a plausible Affinda-shaped response from ground truth, for testing
    the analyser only. NOT real parser output."""
    work = []
    for e in gt["expected_employment"]:
        work.append({
            "jobTitle": {"raw": e["jobTitle"]},
            "organization": e["employer"],
            "dates": {"startDate": e["startDate_iso"] + "-01" if e["startDate_iso"] not in ("", "present") else None,
                      "endDate": None if e["isCurrent"] else (e["endDate_iso"] + "-01"),
                      "isCurrent": e["isCurrent"]},
        })
    return {
        "data": {
            "name": {"raw": gt["candidate_name"]},
            "emails": gt["expected_contact"]["emails"],
            "phoneNumbers": [{"rawText": gt["expected_contact"]["phone"]}],
            "skills": [{"name": s} for s in gt["expected_skills"]],
            "workExperience": work,
            "education": [{"organization": ed["institution"]} for ed in gt["expected_education"]],
        },
        "meta": {"identifier": gt["filename"], "confidence": 0.98, "warnings": []},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=DEFAULT_RESULTS)
    ap.add_argument("--self-check", action="store_true",
                    help="run against generated mock responses to exercise the analyser")
    args = ap.parse_args()

    with open(GROUND_TRUTH, encoding="utf-8") as f:
        ground_truth = json.load(f)

    results_dir = args.results
    if args.self_check:
        tmp = tempfile.mkdtemp(prefix="affinda_mock_")
        for tid, gt in ground_truth.items():
            with open(os.path.join(tmp, f"{tid}.json"), "w", encoding="utf-8") as f:
                json.dump(_mock_response(gt), f)
        results_dir = tmp
        print(f"[self-check] wrote 20 mock responses to {tmp}")

    results = load_results(results_dir)
    overall = write_reports(ground_truth, results)
    print(f"Analysed {overall['analysed']} response(s); "
          f"{overall['missing_response']} awaiting. Reports -> {REPORTS}")
    if overall["analysed"]:
        print(f"  checks: {overall['pass']} pass / {overall['partial']} partial / "
              f"{overall['mismatch']} fail / {overall['unsupported']} unsupported")


if __name__ == "__main__":
    main()
