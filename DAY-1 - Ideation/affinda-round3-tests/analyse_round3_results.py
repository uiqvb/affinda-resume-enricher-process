"""
analyse_round3_results.py — Score actual Affinda responses for the 48 round-3 probes
against ground_truth_round3.json.

Reads real responses from results/ (per-test JSON like R301.json, or a combined list
[{fileName, response}, ...]). Inspects ACTUAL fields; never invents data. Crucially, it
first checks whether an EXISTING Affinda field already addresses each hypothesis before
reporting a gap (per the brief), and classifies each finding as:
  confirmed | ambiguous | unsupported | correct

Writes findings/round3_data.json + findings/round3_summary.md.
With results/ empty it reports that and exits (no ROUND3_ANALYSIS.md fabricated).
"""
from __future__ import annotations

import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, "ground_truth_round3.json")
RESULTS = os.path.join(HERE, "results")
FINDINGS = os.path.join(HERE, "findings")


def norm(s):
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def data_of(resp):
    return resp.get("data", resp) if isinstance(resp, dict) else {}


def skills_pool(d):
    pool = []
    for s in d.get("skills") or []:
        if isinstance(s, dict):
            pool += [norm(s.get("name")), norm(s.get("text"))]
    return [p for p in pool if p]


def all_keys(d):
    return set(d.keys()) if isinstance(d, dict) else set()


# ---------------- category scorers ---------------- #
def sc_negated(g, d):
    raw = norm(d.get("rawText"))
    pool = skills_pool(d)
    exp = g["expected_parser_behaviour"]
    rows, verdict = [], "correct"
    for sk in exp.get("skills_absent", []):
        present = any(norm(sk) == p or norm(sk) in p.split() for p in pool)
        rows.append({"skill": sk, "should_be_absent": True, "extracted_as_skill": present,
                     "result": "confirmed_failure" if present else "correct"})
        if present:
            verdict = "confirmed"
    for sk in exp.get("skills_present", []):
        present = any(norm(sk) in p for p in pool)
        rows.append({"skill": sk, "should_be_present": True, "extracted_as_skill": present,
                     "result": "correct" if present else "miss"})
        if not present and verdict == "correct":
            verdict = "ambiguous"
    if "note" in exp:
        verdict = "ambiguous"
    return {"verdict": verdict, "skills_checked": rows, "existing_field": "skills"}


def sc_workauth(g, d):
    # does ANY field carry work authorisation? (observed schema: likely none)
    keys = all_keys(d)
    wa_field = next((k for k in keys if "author" in k.lower() or "visa" in k.lower()
                     or "workeligib" in k.lower()), None)
    wa_text = g.get("work_authorisation_text") or ""
    raw = d.get("rawText") or ""
    in_raw = bool(wa_text) and norm(wa_text)[:15] in norm(raw)
    if wa_field:
        return {"verdict": "correct", "existing_field": wa_field,
                "detail": f"work auth captured in field '{wa_field}'"}
    # no dedicated field
    if not wa_text:
        return {"verdict": "correct", "existing_field": None,
                "detail": "no statement in source; none invented (unknown control)"}
    return {"verdict": "unsupported", "existing_field": None,
            "detail": f"no work-authorisation field in response; statement {'present' if in_raw else 'absent'} in rawText only"}


def sc_ownership(g, d):
    pool = skills_pool(d)
    skill = g["expected_parser_behaviour"].get("skill")
    personal = g["expected_parser_behaviour"].get("is_personal")
    attributed = any(norm(skill) in p for p in pool)
    # sources available?
    has_sources = any(isinstance(s, dict) and s.get("sources") for s in (d.get("skills") or []))
    if personal is True:
        return {"verdict": "correct" if attributed else "ambiguous",
                "skill": skill, "attributed": attributed, "has_sources": has_sources,
                "detail": "personal skill " + ("attributed" if attributed else "missed")}
    # managed / ambiguous: over-attribution cannot be a hard failure without an ownership model
    return {"verdict": "ambiguous", "skill": skill, "attributed_to_candidate": attributed,
            "has_sources": has_sources,
            "detail": f"managed/ambiguous skill {'attributed to candidate (over-attribution)' if attributed else 'not attributed'}; "
                      "ownership not modelled — records observation, not a hard failure"}


def sc_duration(g, d):
    we = d.get("workExperience") or []
    metrics = d.get("employmentMetrics")
    emp_types = [w.get("employmentType") for w in we if isinstance(w, dict)]
    durations = [((w.get("dateRange") or {}).get("durationMonths")) for w in we]
    has_metrics = metrics not in (None, {}, [])
    return {"verdict": "ambiguous" if not has_metrics else "correct",
            "employmentMetrics_present": has_metrics, "employmentMetrics": metrics,
            "employmentTypes": emp_types, "durationsMonths": durations,
            "detail": "aggregate/metrics field " + ("present" if has_metrics else "absent")
                      + "; inspect for double-count / part-time / claim-vs-dates"}


def sc_cert(g, d):
    certs = d.get("certifications") or []
    status = g["expected_parser_behaviour"].get("status")
    expected_cert = norm(g["expected_parser_behaviour"].get("certification"))
    captured = None
    for c in certs:
        blob = norm(json.dumps(c, default=str)) if isinstance(c, (dict, list)) else norm(c)
        if expected_cert[:10] in blob:
            captured = c
            break
    # does the cert object carry a status / expiry field?
    status_field = False
    if isinstance(captured, dict):
        status_field = any(k.lower() in ("status", "expirydate", "expiry", "valid", "state", "isactive")
                           for k in captured.keys())
    if status in ("active",):  # positive control
        return {"verdict": "correct" if captured is not None else "miss",
                "certifications_field_present": bool(certs), "captured": captured,
                "detail": "active cert " + ("captured" if captured is not None else "missing")}
    # non-active: is the status representable?
    if status_field:
        return {"verdict": "correct", "captured": captured, "detail": "status field present on certification"}
    return {"verdict": "unsupported" if captured is not None else "ambiguous",
            "certifications_field_present": bool(certs), "captured": captured,
            "detail": f"certification {'captured' if captured is not None else 'not matched'} but no "
                      f"status/expiry field — '{status}' recoverable only from text"}


def sc_emptype(g, d):
    we = d.get("workExperience") or []
    et = (we[0].get("employmentType") if we and isinstance(we[0], dict) else None)
    expected = g["expected_parser_behaviour"].get("employment_type_expected")
    if expected == "permanent":
        return {"verdict": "correct", "employmentType": et, "detail": f"permanent control; employmentType={et}"}
    if expected == "ambiguous":
        return {"verdict": "ambiguous", "employmentType": et, "detail": f"ambiguous label; employmentType={et}"}
    # does employmentType distinguish the labelled arrangement?
    matched = et and norm(expected) in norm(et)
    return {"verdict": "correct" if matched else "unsupported", "employmentType": et,
            "expected": expected,
            "detail": f"employmentType={et!r}; expected to reflect '{expected}' "
                      + ("(matched)" if matched else "(not distinguished — may be full_time/generic)")}


SCORERS = {"negated_skills": sc_negated, "work_authorisation": sc_workauth,
           "skill_ownership": sc_ownership, "experience_duration": sc_duration,
           "certification_status": sc_cert, "employment_type": sc_emptype}


def load_results(d):
    found = {}
    for fp in glob.glob(os.path.join(d, "*.json")):
        try:
            obj = json.load(open(fp, encoding="utf-8"))
        except Exception as e:  # noqa
            print(f"  ! {os.path.basename(fp)}: {e}"); continue
        entries = obj if isinstance(obj, list) else [{"fileName": os.path.basename(fp), "response": obj}]
        for it in entries:
            m = re.search(r"(R3\d{2})", str(it.get("fileName", "")).upper()) or \
                re.search(r"(R3\d{2})", os.path.basename(fp).upper())
            if m:
                found[m.group(1)] = it.get("response", it)
    return found


def main():
    gt = json.load(open(GT, encoding="utf-8"))
    responses = load_results(RESULTS)
    if not responses:
        print("No Affinda responses in results/. Upload the 48 PDFs, save JSON into results/ "
              "(R301.json … or one combined list), then re-run. Analyser ready; nothing fabricated.")
        return
    os.makedirs(FINDINGS, exist_ok=True)
    per_test, tally, by_cat = {}, {}, {}
    for tid, g in gt.items():
        resp = responses.get(tid)
        if resp is None:
            per_test[tid] = {"verdict": "no_response"}; tally["no_response"] = tally.get("no_response", 0) + 1
            continue
        out = SCORERS[g["category"]](g, data_of(resp))
        out.update({"category": g["category"], "controlled": g["controlled_variable"]})
        per_test[tid] = out
        tally[out["verdict"]] = tally.get(out["verdict"], 0) + 1
        by_cat.setdefault(g["category"], {}).setdefault(out["verdict"], 0)
        by_cat[g["category"]][out["verdict"]] += 1
    json.dump({"tally": tally, "by_category": by_cat, "per_test": per_test},
              open(os.path.join(FINDINGS, "round3_data.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    lines = ["# Round 3 — analysis summary", "", f"Analysed {len(responses)}/48", "", "## Verdict tally", ""]
    for k, v in sorted(tally.items()):
        lines.append(f"- {k}: {v}")
    lines += ["", "## By category", ""]
    for cat, t in by_cat.items():
        lines.append(f"- **{cat}**: " + ", ".join(f"{k} {v}" for k, v in t.items()))
    lines += ["", "## Per test", "", "| ID | Category | Controlled | Verdict |", "|---|---|---|---|"]
    for tid, v in per_test.items():
        lines.append(f"| {tid} | {v.get('category','')} | {v.get('controlled','')[:34]} | {v.get('verdict')} |")
    open(os.path.join(FINDINGS, "round3_summary.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"tally={tally}")
    print(f"findings -> {FINDINGS}")


if __name__ == "__main__":
    main()
