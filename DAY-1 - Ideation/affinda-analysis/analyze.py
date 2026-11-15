"""
analyze.py — Evidence-based evaluation of Affinda Resume Parser output against
the synthetic ground truth for all 30 fixtures (A/D/E/F main + B/C security).

Reads ONLY local files (no live API calls, no network):
  * ../affinda-resumes.json                    (30 actual Affinda responses)
  * ../affinda-main-tests/ground_truth.json    (A,D,E,F expected answers)
  * ../affinda-security-tests/_build_report.json + generator CANDIDATES (B,C)

Emits affinda-analysis/findings.json (machine-readable) and prints a summary.
Field access matches the OBSERVED schema (schemaVersion 1.0):
  data.contact.emails / .phoneNumbers[].raw / .websites
  data.person.name.{given,family} / .location
  data.workExperience[].{organization,jobTitle,description,dateRange,...}
  data.education[].{institution,qualification,level,fieldsOfStudy,dateRange}
  data.skills[].{name,text,taxonomy}
  data.rawText ; meta.document.extractionQuality.{band,score}
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESP = os.path.join(ROOT, "affinda-resumes.json")
MAIN_GT = os.path.join(ROOT, "affinda-main-tests", "ground_truth.json")
SEC_DIR = os.path.join(ROOT, "affinda-security-tests")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "findings.json")


# --------------------------------------------------------------------------- #
#  Normalisation
# --------------------------------------------------------------------------- #
def norm(s):
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def iso_month(s):
    """Affinda date '2021-03-01' -> '2021-03'; year precision -> 'YYYY'."""
    if not s:
        return ""
    m = re.match(r"(\d{4})-(\d{2})", str(s))
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    m = re.match(r"(\d{4})", str(s))
    return m.group(1) if m else ""


# --------------------------------------------------------------------------- #
#  Schema accessors (observed)
# --------------------------------------------------------------------------- #
def R(resp):
    return resp.get("data", {}) or {}


def get_name(d):
    n = (d.get("person") or {}).get("name") or {}
    given, family = n.get("given", ""), n.get("family", "")
    full = " ".join(x for x in [given, family] if x)
    return full, given, family


def get_emails(d):
    return list((d.get("contact") or {}).get("emails") or [])


def get_phones(d):
    ph = (d.get("contact") or {}).get("phoneNumbers") or []
    out = []
    for p in ph:
        if isinstance(p, dict):
            out.append(p.get("raw") or p.get("formatted") or p.get("nationalNumber") or "")
        else:
            out.append(str(p))
    return [x for x in out if x]


def get_skills(d):
    out = []
    for s in d.get("skills") or []:
        if isinstance(s, dict):
            out.append({"name": s.get("name", ""), "text": s.get("text", "")})
    return out


def get_work(d):
    out = []
    for w in d.get("workExperience") or []:
        dr = w.get("dateRange") or {}
        start = (dr.get("start") or {})
        end = (dr.get("end") or {})
        out.append({
            "org": w.get("organization", "") or "",
            "title": w.get("jobTitle", "") or "",
            "start": iso_month(start.get("date")),
            "end_date": iso_month(end.get("date")),
            "current": bool(end.get("current")),
            "durationMonths": dr.get("durationMonths"),
            "description": w.get("description", "") or "",
        })
    return out


def get_education(d):
    out = []
    for e in d.get("education") or []:
        dr = e.get("dateRange") or {}
        out.append({
            "institution": e.get("institution", "") or "",
            "qualification": e.get("qualification", "") or "",
            "level": e.get("level", "") or "",
            "end": iso_month((dr.get("end") or {}).get("date")),
            "current": bool((dr.get("end") or {}).get("current")),
        })
    return out


def quality(resp):
    doc = (resp.get("meta") or {}).get("document") or {}
    eq = doc.get("extractionQuality") or {}
    cl = doc.get("classification") or {}
    return {"band": eq.get("band"), "score": eq.get("score"),
            "doc_label": cl.get("label"), "doc_confidence": cl.get("confidence")}


# --------------------------------------------------------------------------- #
#  Matching helpers
# --------------------------------------------------------------------------- #
def match_work(gt_emp, parsed):
    """Align each ground-truth role to a parsed role by employer similarity."""
    used, pairs = set(), []
    for g in gt_emp:
        g_org = norm(g["employer"])
        found = None
        for i, p in enumerate(parsed):
            if i in used:
                continue
            if g_org and (g_org in norm(p["org"]) or norm(p["org"]) in g_org):
                found, idx = p, i
                break
        if found is not None:
            used.add(idx)
        pairs.append((g, found))
    extra = [p for i, p in enumerate(parsed) if i not in used]
    return pairs, extra


def skill_eval(expected, parsed_skills):
    pool = []
    for s in parsed_skills:
        pool.append(norm(s["name"]))
        pool.append(norm(s["text"]))
    pool = [p for p in pool if p]
    found = []
    for e in expected:
        ne = norm(e)
        if any(ne == p or ne in p or p in ne for p in pool):
            found.append(e)
    recall = len(found) / len(expected) if expected else None
    # precision: parsed skills that correspond to some expected skill
    matched_parsed = 0
    for s in parsed_skills:
        ns = norm(s["name"]) + " " + norm(s["text"])
        if any(norm(e) in ns or ns.find(norm(e)) >= 0 for e in expected):
            matched_parsed += 1
    precision = matched_parsed / len(parsed_skills) if parsed_skills else None
    f1 = (2 * precision * recall / (precision + recall)
          if precision and recall and (precision + recall) else None)
    return {"expected": len(expected), "returned": len(parsed_skills),
            "matched_expected": len(found), "missing": [e for e in expected if e not in found],
            "recall": recall, "precision": precision, "f1": f1}


# --------------------------------------------------------------------------- #
#  Load security ground truth
# --------------------------------------------------------------------------- #
def load_security_gt():
    sys.path.insert(0, SEC_DIR)
    import generate_security_tests as g  # noqa
    build = json.load(open(os.path.join(SEC_DIR, "_build_report.json"), encoding="utf-8"))
    gt = {}
    for tid, c in g.CANDIDATES.items():
        gt[tid] = {
            "name": c["name"], "emails": [c["email"]], "phone": c["phone"],
            "location": c["location"],
            "employers": [e[1] for e in c["experience"]],
            "titles": [e[0] for e in c["experience"]],
            "skills": c["skills"],
            "marker": build.get(tid, {}).get("marker", ""),
            "technique": build.get(tid, {}).get("technique", ""),
            "category": tid[0],
        }
    return gt


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
def main():
    responses = json.load(open(RESP, encoding="utf-8"))
    by_id = {}
    for it in responses:
        m = re.match(r"([ABCDEF]0[1-9])", it["fileName"].upper())
        if m:
            by_id[m.group(1)] = it
    main_gt = json.load(open(MAIN_GT, encoding="utf-8"))
    sec_gt = load_security_gt()

    findings = {"per_test": {}, "coverage": {}}

    # ---------- MAIN categories A/D/E/F ----------
    for tid, gt in main_gt.items():
        resp = by_id.get(tid)
        if resp is None:
            findings["per_test"][tid] = {"status": "NO_RESPONSE"}
            continue
        d = R(resp["response"])
        full, given, family = get_name(d)
        emails = get_emails(d)
        phones = get_phones(d)
        skills = get_skills(d)
        work = get_work(d)
        edu = get_education(d)
        raw = d.get("rawText") or ""
        q = quality(resp["response"])

        rec = {"category": gt["category"], "layout": gt["layout"],
               "parseMs": resp.get("parseMs"), "quality": q,
               "rawText_chars": len(raw)}

        # name
        exp_last = gt["candidate_name"].split()[-1].lower()
        exp_first = gt["candidate_name"].split()[0].lower()
        rec["name"] = {"expected": gt["candidate_name"], "got": full,
                       "match": exp_last in norm(full) and exp_first in norm(full)}
        # emails
        exp_emails = [e.lower() for e in gt["expected_contact"]["emails"]]
        got_emails = [e.lower() for e in emails]
        rec["emails"] = {"expected": exp_emails, "got": got_emails,
                         "all_found": all(e in got_emails for e in exp_emails),
                         "missing": [e for e in exp_emails if e not in got_emails]}
        # phone
        exp_digits = re.sub(r"\D", "", gt["expected_contact"]["phone"])[-10:]
        got_digits = [re.sub(r"\D", "", p)[-10:] for p in phones]
        rec["phone"] = {"expected": gt["expected_contact"]["phone"], "got": phones,
                        "match": exp_digits in got_digits}
        # work
        pairs, extra = match_work(gt["expected_employment"], work)
        roles = []
        for gemp, p in pairs:
            if p is None:
                roles.append({"employer": gemp["employer"], "matched": False})
                continue
            if gemp["isCurrent"]:
                date_ok = p["current"] or p["end_date"] == ""
                exp_end = "current"
            else:
                exp_end = gemp["endDate_iso"]
                date_ok = (p["end_date"] == exp_end) or (p["end_date"][:4] == exp_end[:4] if p["end_date"] else False)
            roles.append({
                "employer": gemp["employer"], "matched": True,
                "title_expected": gemp["jobTitle"], "title_got": p["title"],
                "title_match": norm(gemp["jobTitle"])[:12] in norm(p["title"]) or norm(p["title"])[:12] in norm(gemp["jobTitle"]),
                "start_expected": gemp["startDate_iso"], "start_got": p["start"],
                "start_match": p["start"] == gemp["startDate_iso"] or p["start"][:4] == gemp["startDate_iso"][:4],
                "end_expected": exp_end, "end_got": "current" if p["current"] else p["end_date"],
                "end_match": date_ok,
            })
        rec["work"] = {"expected_roles": len(gt["expected_employment"]),
                       "returned_roles": len(work), "roles": roles,
                       "extra_roles": [{"org": e["org"], "title": e["title"]} for e in extra]}
        # education
        rec["education"] = {"expected": len(gt["expected_education"]),
                            "returned": len(edu),
                            "institutions_got": [e["institution"] for e in edu],
                            "detail": edu}
        # skills
        rec["skills"] = skill_eval(gt["expected_skills"], skills)
        findings["per_test"][tid] = rec

    # ---------- SECURITY categories B/C ----------
    for tid, gt in sec_gt.items():
        resp = by_id.get(tid)
        if resp is None:
            findings["per_test"][tid] = {"status": "NO_RESPONSE"}
            continue
        d = R(resp["response"])
        raw = d.get("rawText") or ""
        redacted = d.get("redactedText") or ""
        summary = d.get("summary") or ""
        full, _, _ = get_name(d)
        emails = get_emails(d)
        skills = get_skills(d)
        q = quality(resp["response"])
        marker = gt["marker"]
        # where does the marker appear?
        in_raw = marker in raw
        in_summary = marker in (summary or "")
        structured_blob = json.dumps({k: v for k, v in d.items()
                                      if k not in ("rawText", "redactedText")}, default=str)
        in_structured = marker in structured_blob
        rec = {"category": gt["category"], "technique": gt["technique"],
               "marker": marker, "parseMs": resp.get("parseMs"), "quality": q,
               "rawText_chars": len(raw),
               "marker_in_rawText": in_raw,
               "marker_in_structured_fields": in_structured,
               "marker_in_summary_field": in_summary,
               # baseline extraction sanity on these clean resumes:
               "name_got": full, "name_match": gt["name"].split()[-1].lower() in norm(full),
               "emails_got": emails, "email_match": gt["emails"][0].lower() in [e.lower() for e in emails],
               "skills_returned": len(skills)}
        findings["per_test"][tid] = rec

    # ---------- coverage ----------
    findings["coverage"] = {
        "responses_total": len(responses),
        "mapped": len(by_id),
        "main_scored": sum(1 for t in main_gt if by_id.get(t)),
        "security_scored": sum(1 for t in sec_gt if by_id.get(t)),
        "missing_named_files": {
            "ground_truth_security.json": not os.path.exists(os.path.join(SEC_DIR, "ground_truth_security.json")),
            "test_manifest_security.csv": not os.path.exists(os.path.join(SEC_DIR, "test_manifest_security.csv")),
        },
    }

    json.dump(findings, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"findings -> {OUT}")
    return findings


if __name__ == "__main__":
    f = main()
    # concise console summary
    pt = f["per_test"]
    print("coverage:", f["coverage"])
