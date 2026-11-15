"""
analyse_targeted_results.py — Score actual Affinda responses for the 45 targeted
tests against ground_truth_targeted.json (Phase 6).

Reads real responses from results/ (one JSON per test, named e.g. T01.json, or a
single combined list like the earlier affinda-resumes.json). Inspects ACTUAL data;
never invents responses. Field access is defensive against the observed schema:
  data.person.name.{given,family} · data.contact.{emails,phoneNumbers}
  data.workExperience[].{organization,jobTitle,dateRange.start/end,description}
  data.education[].{institution,qualification,dateRange} · data.rawText · meta.document

Verdicts per test: pass | acceptable | inconclusive | fail (confirmed failure).
Writes findings/targeted_data.json and findings/targeted_summary.md.
Run `python analyse_targeted_results.py --self-check` to exercise logic on mocks.

NOTE: if results/ is empty, it reports that and exits — it does not fabricate a
findings report. Per the brief, TARGETED_FINDINGS.md is authored only once real
results exist.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, "ground_truth_targeted.json")
RESULTS = os.path.join(HERE, "results")
FINDINGS = os.path.join(HERE, "findings")


# --------------------------- schema accessors ---------------------------- #
def norm(s):
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def iso_month(s):
    if not s:
        return ""
    m = re.match(r"(\d{4})-(\d{2})", str(s))
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    m = re.match(r"(\d{4})", str(s))
    return m.group(1) if m else ""


def data_of(resp):
    return resp.get("data", resp) if isinstance(resp, dict) else {}


def get_work(d):
    out = []
    for w in d.get("workExperience") or []:
        dr = w.get("dateRange") or {}
        s, e = dr.get("start") or {}, dr.get("end") or {}
        out.append({"org": w.get("organization") or "", "title": w.get("jobTitle") or "",
                    "start": iso_month(s.get("date")), "end": iso_month(e.get("date")),
                    "current": bool(e.get("current")), "durationMonths": dr.get("durationMonths"),
                    "description": w.get("description") or ""})
    return out


def get_edu(d):
    out = []
    for ed in d.get("education") or []:
        dr = ed.get("dateRange") or {}
        e = dr.get("end") or {}
        out.append({"institution": ed.get("institution") or "",
                    "qualification": ed.get("qualification") or "",
                    "end": iso_month(e.get("date")), "end_current": bool(e.get("current")),
                    "level": ed.get("level") or "", "raw": json.dumps(ed, default=str)})
    return out


def best_by(items, key_text, field):
    kt = norm(key_text)
    best, bi = None, None
    for i, it in enumerate(items):
        v = norm(it[field])
        if v and (v[:14] in kt or kt[:14] in v or v in kt or kt in v):
            return it, i
    return best, bi


# --------------------------- phase scorers ------------------------------- #
def score_phase1(c_gt, d):
    work = get_work(d)
    target, _ = best_by(work, "Thamesworks Cloud", "org")
    ev = {"parsed_role": target}
    exp = c_gt["expected_parser_behaviour"]
    tid = c_gt["test_id"]
    if target is None:
        return {"verdict": "inconclusive", "reason": "current role not found", "evidence": ev}
    start, end, cur = target["start"], target["end"], target["current"]
    invented_end = bool(end) and (end == start)
    # completed control
    if tid == "T11":
        ok = (end == "2024-10") and not cur
        return {"verdict": "pass" if ok else "fail",
                "reason": f"expected end 2024-10/not-current; got end={end or '—'} current={cur}",
                "evidence": ev}
    # ambiguous open-ended / single-date
    if tid in ("T03", "T12"):
        if invented_end or (end and end != "" and not cur):
            return {"verdict": "fail", "reason": f"invented end date {end} for an open-ended role",
                    "evidence": ev, "pattern": "invented_end_date"}
        return {"verdict": "acceptable",
                "reason": f"open-ended handled without a fabricated end (end={end or 'null'}, current={cur})",
                "evidence": ev}
    # explicit-current variants
    if cur or end == "":
        if invented_end:
            return {"verdict": "fail", "reason": f"end==start ({end}) despite current wording",
                    "evidence": ev, "pattern": "invented_end_date"}
        return {"verdict": "pass", "reason": f"current recognised (current={cur}, end={end or 'null'})",
                "evidence": ev}
    # has an end date despite current wording
    return {"verdict": "fail",
            "reason": f"current wording but end={end} (current={cur}) — "
                      + ("end==start" if invented_end else "unsupported end date"),
            "evidence": ev, "pattern": "invented_end_date" if invented_end else "unsupported_end"}


def score_phase2(c_gt, d):
    work = get_work(d)
    exp_roles = c_gt["expected_parser_behaviour"]["roles"]
    # names present elsewhere in the source (to detect 'bleed')
    other_employers = [norm(r.get("employer_expected") or "") for r in exp_roles
                       if r.get("employer_kind") == "employer"]
    rows, any_fail = [], False
    for er in exp_roles:
        pr, _ = best_by(work, er["title"], "title")
        if pr is None:
            rows.append({"title": er["title"], "result": "fail", "why": "role missing",
                         "pattern": "role_dropped"}); any_fail = True
            continue
        got = norm(pr["org"])
        exp_emp = er.get("employer_expected")
        kind = er.get("employer_kind")
        self_tokens = ["self-employed", "self employed", "independent", "sole trader",
                       "freelance", "contractor"]
        res, why, pat = "pass", f"employer='{pr['org']}'", None
        if kind in ("self_employment",):
            if any(t in got for t in self_tokens) or got == "" or got == norm(exp_emp or ""):
                res = "pass"
            elif got in other_employers:
                res, why, pat = "fail", f"freelance attributed to '{pr['org']}' (employer bleed)", "employer_bleed"
            elif got:
                res, why, pat = "fail", f"invented employer '{pr['org']}'", "invented_employer"
        elif kind == "unknown":  # T20 no employer
            if got == "" or any(t in got for t in self_tokens):
                res = "acceptable"; why = "no employer preserved / self-employment"
            elif got in other_employers:
                res, why, pat = "fail", f"borrowed employer '{pr['org']}'", "employer_bleed"
            elif got:
                res, why, pat = "fail", f"invented employer '{pr['org']}'", "invented_employer"
        else:  # conventional employer
            if norm(exp_emp or "")[:10] in got or got[:10] in norm(exp_emp or ""):
                res = "pass"
            else:
                res, why, pat = "fail", f"expected '{exp_emp}', got '{pr['org']}'", "wrong_employer"
        # client-as-employer check
        for cl in er.get("clients_not_employer", []) + ([er["client_not_employer"]] if er.get("client_not_employer") else []):
            if norm(cl) and norm(cl) in got:
                res, why, pat = "fail", f"client '{cl}' extracted as employer", "client_as_employer"
        if res == "fail":
            any_fail = True
        rows.append({"title": er["title"], "expected_employer": exp_emp,
                     "got_employer": pr["org"], "result": res, "why": why, "pattern": pat})
    return {"verdict": "fail" if any_fail else "pass", "roles": rows}


def score_phase3(c_gt, d):
    edu = get_edu(d)
    raw = d.get("rawText") or ""
    exp_edu = c_gt["expected_parser_behaviour"]["education"]
    rows, any_fail, any_inconc = [], False, False
    for ee in exp_edu:
        pe, _ = best_by(edu, ee["qualification"], "qualification")
        status = ee["status"]
        note_words = [w for w in re.split(r"\W+", c_gt["exact_source_evidence"]) if w]
        if pe is None:
            any_inconc = True
            rows.append({"qualification": ee["qualification"], "result": "inconclusive",
                         "why": "education entry DROPPED (not present in structured output)",
                         "pattern": "education_dropped"}); continue
        end = pe["end"]
        # does any structured field carry a status? (observed schema has none)
        structured_has_status = bool(re.search(r"status|in[_ ]?progress|current|incomplete|expected",
                                               pe["raw"], re.I)) and not re.search(r'"level"', pe["raw"])
        in_rawtext = any(w.lower() in raw.lower() for w in ("progress", "expected", "incomplete",
                                                            "withdrawn", "deferred", "enrolled",
                                                            "not awarded", "ongoing", "candidate"))
        if status == "completed":
            ok = bool(end)
            rows.append({"qualification": ee["qualification"], "result": "pass" if ok else "inconclusive",
                         "why": f"completed control; end={end or '—'}"})
            continue
        # NON-completed qualifications
        if structured_has_status:
            res, why = "pass", "status represented in a structured field"
        elif end:
            res, why = "fail", (f"end date {end} emitted with no status field — reads as conferred "
                                f"(misleading for a '{status}' qualification)")
            any_fail = True
        elif in_rawtext:
            res, why = "inconclusive", "status absent from structured output; recoverable only from rawText"
            any_inconc = True
        else:
            res, why = "inconclusive", "status absent from structured output (no end date)"
            any_inconc = True
        rows.append({"qualification": ee["qualification"], "status_expected": status,
                     "end_got": end, "structured_status": structured_has_status,
                     "status_in_rawtext": in_rawtext, "result": res, "why": why,
                     "pattern": "misleading_completion" if res == "fail" else
                                ("status_absent" if res == "inconclusive" else None)})
    verdict = "fail" if any_fail else ("inconclusive" if any_inconc else "pass")
    return {"verdict": verdict, "education": rows}


# --------------------------- driver -------------------------------------- #
def load_results(results_dir):
    found = {}
    files = glob.glob(os.path.join(results_dir, "*.json"))
    for fp in files:
        try:
            obj = json.load(open(fp, encoding="utf-8"))
        except Exception as e:  # noqa
            print(f"  ! unreadable {os.path.basename(fp)}: {e}"); continue
        entries = obj if isinstance(obj, list) else [{"fileName": os.path.basename(fp), "response": obj}]
        for it in entries:
            fn = it.get("fileName", "")
            resp = it.get("response", it)
            m = re.search(r"(T\d{2})", str(fn).upper()) or re.search(r"(T\d{2})", os.path.basename(fp).upper())
            if m:
                found[m.group(1)] = resp
    return found


SCORERS = {1: score_phase1, 2: score_phase2, 3: score_phase3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=RESULTS)
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    gt = json.load(open(GT, encoding="utf-8"))

    results_dir = args.results
    if args.self_check:
        results_dir = tempfile.mkdtemp(prefix="targeted_mock_")
        for tid, g in gt.items():
            json.dump(_mock(g), open(os.path.join(results_dir, f"{tid}.json"), "w", encoding="utf-8"))
        print(f"[self-check] mock responses in {results_dir}")

    responses = load_results(results_dir)
    if not responses:
        print("No Affinda responses found in results/. Upload the 45 PDFs to the Sandbox, "
              "save each JSON into results/ (e.g. T01.json or one combined list), then re-run.")
        print("Analyser is ready; no findings fabricated.")
        return

    os.makedirs(FINDINGS, exist_ok=True)
    per_test, patterns = {}, {}
    tally = {"pass": 0, "acceptable": 0, "inconclusive": 0, "fail": 0, "no_response": 0}
    for tid, g in gt.items():
        resp = responses.get(tid)
        if resp is None:
            per_test[tid] = {"verdict": "no_response"}; tally["no_response"] += 1; continue
        d = data_of(resp)
        out = SCORERS[g["phase"]](g, d)
        out.update({"phase": g["phase"], "controlled": g["controlled_variable"]})
        per_test[tid] = out
        tally[out["verdict"]] = tally.get(out["verdict"], 0) + 1
        for r in out.get("roles", []) + out.get("education", []):
            if r.get("pattern"):
                patterns[r["pattern"]] = patterns.get(r["pattern"], 0) + 1
        if out.get("pattern"):
            patterns[out["pattern"]] = patterns.get(out["pattern"], 0) + 1

    json.dump({"tally": tally, "patterns": patterns, "per_test": per_test},
              open(os.path.join(FINDINGS, "targeted_data.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)

    lines = ["# Targeted Tests — analysis summary", "",
             f"Responses analysed: {sum(1 for v in per_test.values() if v.get('verdict')!='no_response')}/45",
             "", "## Verdict tally", ""]
    for k in ("pass", "acceptable", "inconclusive", "fail", "no_response"):
        lines.append(f"- {k}: {tally.get(k,0)}")
    lines += ["", "## Failure patterns (by controlled variable)", ""]
    for p, n in sorted(patterns.items(), key=lambda x: -x[1]):
        lines.append(f"- {p}: {n}")
    lines += ["", "## Per-test verdicts", "", "| ID | Phase | Controlled | Verdict |", "|---|---|---|---|"]
    for tid, v in per_test.items():
        lines.append(f"| {tid} | {v.get('phase','')} | {v.get('controlled','')[:40]} | {v.get('verdict')} |")
    open(os.path.join(FINDINGS, "targeted_summary.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"tally={tally} patterns={patterns}")
    print(f"findings -> {FINDINGS}")


def _mock(g):
    """Ideal-ish Affinda-shaped response from ground truth (self-check only; NOT real)."""
    work = []
    for e in g["expected_work_experience"]:
        dd = e["date_display"].lower()
        current = any(k in dd for k in ("present", "current", "now", "ongoing", "onwards",
                                        "to date", "since", "employed"))
        years = re.findall(r"\d{4}", e["date_display"])
        start_obj = {"date": f"{years[0]}-01-01"} if years else {}
        if current:
            end_obj = {"current": True}
        elif len(years) >= 2:
            end_obj = {"date": f"{years[-1]}-01-01"}
        else:
            end_obj = {}
        work.append({"organization": e["employer_as_written"], "jobTitle": e["jobTitle"],
                     "dateRange": {"start": start_obj, "end": end_obj}})
    edu = [{"institution": ed["institution"], "qualification": ed["qualification"],
            "dateRange": {}} for ed in g["expected_education"]]
    raw = g["exact_source_evidence"] + " " + " ".join(ed["status_note"] for ed in g["expected_education"])
    return {"data": {"person": {"name": {"given": g["candidate_identity"]["name"].split()[0],
                                         "family": g["candidate_identity"]["name"].split()[-1]}},
                     "contact": {"emails": [g["candidate_identity"]["email"]]},
                     "workExperience": work, "education": edu, "rawText": raw},
            "meta": {"document": {"extractionQuality": {"band": "high", "score": 0.96}}}}


if __name__ == "__main__":
    main()
