"""
analyse_round4.py — Score actual Affinda responses for the 60 round-4 probes against
ground_truth_round4.json, to confirm / narrow / disprove Round 3's findings.

Reads real responses from results/ (per-test JSON R401.json… or a combined list). Inspects
ACTUAL fields; never invents data. For every category it checks the relevant EXISTING field
before claiming a gap, and distinguishes:
  correct | confirmed (failure) | partial (information loss) | ambiguous | unsupported (schema
  does not model the concept) | miss (not matched) | inconsistent (within-response).
Separates literal text mentions from semantic claims. Writes findings/round4_data.json +
findings/round4_summary.md. With results/ empty, reports that and exits (no report fabricated).
"""
from __future__ import annotations

import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, "ground_truth_round4.json")
RESULTS = os.path.join(HERE, "results")
FINDINGS = os.path.join(HERE, "findings")


def norm(s):
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def data_of(r):
    return r.get("data", r) if isinstance(r, dict) else {}


def skills_pool(d):
    pool = []
    for s in d.get("skills") or []:
        if isinstance(s, dict):
            pool += [norm(s.get("name")), norm(s.get("text"))]
    return [p for p in pool if p]


def skill_present(d, skill):
    base = norm(skill).split(" (")[0]
    return any(base == p or base in p.split() or base in p for p in skills_pool(d))


# ---------------- scorers ---------------- #
def sc_negated(g, d):
    exp = g["correct_intended_interpretation"]
    rows, verdict = [], "correct"
    for sk in exp.get("skills_denied", []):
        present = skill_present(d, sk)
        rows.append({"skill": sk, "should_be_absent": True, "extracted": present,
                     "result": "confirmed" if present else "correct"})
        if present:
            verdict = "confirmed"
    for sk in exp.get("skills_affirmed", []):
        present = skill_present(d, sk)
        rows.append({"skill": sk, "should_be_present": True, "extracted": present,
                     "result": "correct" if present else "miss"})
        if not present and verdict != "confirmed":
            verdict = "partial"
    if "n/a" in json.dumps(g["confirmed_failure_if"]).lower() and verdict == "correct":
        verdict = "ambiguous"
    return {"verdict": verdict, "skills": rows, "existing_field": "skills",
            "note": "literal-mention vs claimed-capability: provenance not modelled in skills[]"}


def sc_ownership(g, d):
    exp = g["correct_intended_interpretation"]
    skill, owner = exp.get("skill"), exp.get("true_owner")
    attributed = skill_present(d, skill)
    has_sources = any(isinstance(s, dict) and s.get("sources") for s in (d.get("skills") or []))
    if owner == "candidate":
        return {"verdict": "correct" if attributed else "partial", "skill": skill,
                "attributed": attributed, "detail": "personal skill " + ("attributed" if attributed else "missed")}
    return {"verdict": "ambiguous", "skill": skill, "true_owner": owner, "attributed_to_candidate": attributed,
            "has_sources": has_sources,
            "detail": f"{owner}-owned skill {'attributed to candidate (over-attribution)' if attributed else 'not attributed'}; "
                      "ownership not modelled — provenance gap, not a hard failure"}


def sc_cert(g, d):
    certs = d.get("certifications") or []
    exp = g["correct_intended_interpretation"]
    status = exp.get("status")
    name = norm(exp.get("certification")).split(" —")[0].split(" -")[0]
    captured = None
    for c in certs:
        if name[:10] in norm(json.dumps(c, default=str)):
            captured = c; break
    status_field = isinstance(captured, dict) and any(
        k.lower() in ("status", "expiry", "expirydate", "valid", "isactive", "state", "revoked")
        for k in captured.keys())
    if status in ("active",):
        return {"verdict": "correct" if captured else "miss", "captured": captured,
                "detail": "active cert " + ("captured" if captured else "missing")}
    if status_field:
        return {"verdict": "correct", "captured": captured, "detail": "status/validity field present"}
    if captured is None:
        return {"verdict": "miss", "detail": f"'{status}' certification not matched in certifications field"}
    return {"verdict": "partial", "captured": captured,
            "detail": f"certification captured but '{status}' status not represented (no status/validity field)"}


def sc_classification(g, d):
    we = d.get("workExperience") or []
    et = [w.get("employmentType") for w in we if isinstance(w, dict)]
    exp = g["correct_intended_interpretation"]
    dims = exp.get("dimensions", {})
    # the enum is a SINGLE value; independent dims (schedule/relationship/permanence) compress
    top = et[0] if et else None
    if exp.get("label", "").lower().startswith("permanent, full"):
        return {"verdict": "correct", "employmentType": et, "detail": f"permanent control; {top}"}
    rel = dims.get("relationship"); sched = dims.get("schedule")
    reflects = top and (norm(rel or "") in norm(top) or norm(sched or "") in norm(top)
                        or (rel == "contractor" and "self" in norm(top)))
    # compression check: multiple independent dims but one enum value
    n_dims = sum(1 for k in ("schedule", "relationship", "permanence") if dims.get(k))
    verdict = "correct" if reflects else "unsupported"
    return {"verdict": verdict, "employmentType": et, "expected_dims": dims,
            "detail": f"employmentType={top!r}; {n_dims} independent dimensions in source; "
                      + ("reflected" if reflects else "compressed to one enum / not reflected")}


def sc_workauth(g, d):
    keys = set(d.keys())
    field = "workAuthorization" if "workAuthorization" in keys else None
    wa_text = g.get("work_authorisation_text") or ""
    exp = g["correct_intended_interpretation"]
    dims = exp.get("dimensions", {})
    val = d.get("workAuthorization") if field else None
    raw = d.get("rawText") or ""
    if not field:
        return {"verdict": "unsupported", "detail": "no workAuthorization field present",
                "in_rawText": norm(wa_text)[:15] in norm(raw)}
    # field exists — does it preserve the key dimension(s)?
    blob = norm(json.dumps(val, default=str))
    preserved = {k: (norm(str(v)) in blob) for k, v in dims.items()}
    allk = all(preserved.values()) if preserved else bool(blob)
    return {"verdict": "correct" if allk else "partial", "field_value": val,
            "dimensions_preserved": preserved,
            "detail": "workAuthorization present; " + ("all key dimensions preserved" if allk
                      else "some dimension(s) dropped: " + ", ".join(k for k, ok in preserved.items() if not ok))}


def sc_duration(g, d):
    we = d.get("workExperience") or []
    m = d.get("employmentMetrics")
    has_m = m not in (None, {}, [])
    # fabricated end date check (Round 2 D04 pattern) on open-ended roles
    fabricated = []
    for w in we:
        dr = w.get("dateRange") or {}
        s, e = (dr.get("start") or {}), (dr.get("end") or {})
        if s.get("date") and e.get("date") and s.get("date") == e.get("date") and not e.get("current"):
            fabricated.append({"org": w.get("organization"), "date": s.get("date")})
    verdict = "correct"
    if fabricated:
        verdict = "confirmed"
    elif not has_m:
        verdict = "ambiguous"
    return {"verdict": verdict, "employmentMetrics_present": has_m, "employmentMetrics": m,
            "role_count": len(we), "fabricated_end_dates": fabricated,
            "detail": ("fabricated end date(s) found" if fabricated else
                       ("metrics present (inspect totals/gaps)" if has_m else "no metrics field"))}


SCORERS = {"negated_skills": sc_negated, "skill_ownership": sc_ownership,
           "certification_validity": sc_cert, "employment_classification": sc_classification,
           "work_authorisation": sc_workauth, "employment_duration": sc_duration}


def load_results(d):
    found = {}
    for fp in glob.glob(os.path.join(d, "*.json")):
        try:
            obj = json.load(open(fp, encoding="utf-8"))
        except Exception as e:  # noqa
            print(f"  ! {os.path.basename(fp)}: {e}"); continue
        entries = obj if isinstance(obj, list) else [{"fileName": os.path.basename(fp), "response": obj}]
        for it in entries:
            m = re.search(r"(R4\d{2})", str(it.get("fileName", "")).upper()) or \
                re.search(r"(R4\d{2})", os.path.basename(fp).upper())
            if m:
                found[m.group(1)] = it.get("response", it)
    return found


def main():
    gt = json.load(open(GT, encoding="utf-8"))
    tests = {k: v for k, v in gt.items() if k != "_meta"}
    responses = load_results(RESULTS)
    if not responses:
        print("No Affinda responses in results/. Upload the 60 PDFs, save JSON into results/ "
              "(R401.json … or one combined list), then re-run. Analyser ready; nothing fabricated.")
        return
    os.makedirs(FINDINGS, exist_ok=True)
    per_test, tally, by_cat = {}, {}, {}
    for tid, g in tests.items():
        resp = responses.get(tid)
        if resp is None:
            per_test[tid] = {"verdict": "no_response"}; tally["no_response"] = tally.get("no_response", 0) + 1
            continue
        out = SCORERS[g["category"]](g, data_of(resp))
        out.update({"category": g["category"], "controlled": g["controlled_variable"],
                    "paired_with": g.get("paired_test_id")})
        per_test[tid] = out
        tally[out["verdict"]] = tally.get(out["verdict"], 0) + 1
        by_cat.setdefault(g["category"], {})
        by_cat[g["category"]][out["verdict"]] = by_cat[g["category"]].get(out["verdict"], 0) + 1
    json.dump({"reference_date": gt.get("_meta", {}).get("reference_date"), "tally": tally,
               "by_category": by_cat, "per_test": per_test},
              open(os.path.join(FINDINGS, "round4_data.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    lines = ["# Round 4 — analysis summary", "", f"Analysed {len(responses)}/60", "", "## Verdict tally", ""]
    for k, v in sorted(tally.items()):
        lines.append(f"- {k}: {v}")
    lines += ["", "## By category", ""]
    for cat, t in by_cat.items():
        lines.append(f"- **{cat}**: " + ", ".join(f"{k} {v}" for k, v in t.items()))
    lines += ["", "## Per test", "", "| ID | Category | Controlled | Verdict |", "|---|---|---|---|"]
    for tid, v in per_test.items():
        lines.append(f"| {tid} | {v.get('category','')} | {v.get('controlled','')[:32]} | {v.get('verdict')} |")
    open(os.path.join(FINDINGS, "round4_summary.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"tally={tally}")
    print(f"findings -> {FINDINGS}")


if __name__ == "__main__":
    main()
