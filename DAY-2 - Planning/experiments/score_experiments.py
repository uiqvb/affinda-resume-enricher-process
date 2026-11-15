#!/usr/bin/env python3
"""
score_experiments.py — score the three Affinda Sandbox exports against the
synthetic ground truth. Reads each row's intent and emits per-row verdicts plus
rollups by category / realism / control. Nothing is hand-judged.

Outputs: findings/<issue>_scored.json, findings/<issue>_summary.md,
         findings/COMBINED_summary.md
Run    : python score_experiments.py
"""
from __future__ import annotations
import json, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "findings"); os.makedirs(OUT, exist_ok=True)

def load(p): return json.load(open(p, encoding="utf-8"))
def data(it): return it["response"].get("data", it["response"])
def years(s): return set(re.findall(r"\b(19|20)\d{2}\b", s)) or set(re.findall(r"\b\d{4}\b", s))
def yrs(s): return set(re.findall(r"\b\d{4}\b", s))

def resp_map(path):
    return {it["fileName"]: it for it in load(path)}

# ------------------------------------------------------------------ EDUCATION
def score_education():
    gt = load(os.path.join(HERE, "education/ground_truth_education.json"))
    rs = resp_map(os.path.join(HERE, "education/results/education-responses-100.json"))
    none_cats = {"in_progress", "deferred_leave", "abd_partial", "unknown_no_signal"}
    rows = []
    for tid, g in gt.items():
        if tid == "_meta": continue
        it = rs[tid + ".pdf"]; d = data(it); eds = d.get("education") or []
        cat = g["status_category"]; line_years = yrs(g["exact_source_line"])
        extracted = len(eds) > 0
        # Affinda routes certificate/VET-level quals to certifications/skills, not education
        qtok = tok(g["qualification"])
        routed = (not extracted) and (
            any(tok(c.get("name","")) & qtok for c in (d.get("certifications") or [])) or
            any(qtok & tok(s.get("name","")+" "+s.get("text","")) for s in (d.get("skills") or [])))
        end_year = None; status_field = False
        if eds:
            end = (eds[0].get("dateRange") or {}).get("end")
            if isinstance(end, dict) and end.get("date"):
                end_year = end["date"][:4]
            # no Affinda schema field carries completion status; detect any just in case
            status_field = any(k for k in eds[0] if k in ("status", "completionStatus", "completed"))
        conferral = bool(end_year and end_year in line_years)
        # verdict
        if cat == "completed":
            verdict = "PASS_CONTROL" if extracted else "FAIL_CONTROL_dropped"
        elif routed:
            verdict = "ROUTED_qual_to_cert"
        elif not extracted:
            verdict = "MISS_entry_dropped"
        elif cat == "expected":
            verdict = "GAP_future_year_as_conferral" if conferral else "GAP_status_absent"
        elif cat in ("withdrawn", "incomplete_discontinued", "not_awarded"):
            verdict = "GAP_year_reads_conferred" if conferral else "GAP_status_absent_no_date"
        elif cat == "multi_entry":
            end2 = None
            if len(eds) > 1:
                e2 = (eds[1].get("dateRange") or {}).get("end")
                end2 = e2.get("date") if isinstance(e2, dict) else None
            verdict = "PARTIAL_both_kept_no_status" if len(eds) > 1 else "MISS_second_entry"
        else:  # none/present categories
            verdict = "GAP_status_absent"
        rows.append(dict(id=tid, category=cat, realism=g["realism"],
                         is_control=g.get("is_control"), line=g["exact_source_line"],
                         extracted=extracted, end_year=end_year, conferral=conferral,
                         status_field=status_field, n_entries=len(eds), verdict=verdict))
    return rows

# -------------------------------------------------------------- CERTIFICATION
def tok(s): return set(re.findall(r"[a-z]+", s.lower())) - {
    "license","licence","certified","certification","certificate","of","the","in","a"}
def score_certification():
    gt = load(os.path.join(HERE, "certification/ground_truth_certification.json"))
    rs = resp_map(os.path.join(HERE, "certification/results/certification-responses-100.json"))
    rows = []
    for tid, g in gt.items():
        if tid == "_meta": continue
        it = rs[tid + ".pdf"]; certs = data(it).get("certifications") or []
        cat = g["validity_category"]; want = tok(g["cert_name"])
        matched = [c for c in certs if (tok(c.get("name","")) & want)]
        extracted = len(matched) > 0
        validity_field = any(k for c in matched for k in c if k in ("status","validity","state"))
        if cat in ("active", "renewed", "expires_future_valid"):
            verdict = "PASS_CONTROL" if extracted else "FAIL_CONTROL_dropped"
        elif cat in ("expired", "revoked", "suspended"):
            verdict = "GAP_invalid_reads_valid" if extracted else "DROP_invalid_cert"
        elif cat in ("pending_scheduled", "failed"):
            verdict = "OK_omitted" if not extracted else "RISK_not_held_reads_held"
        elif cat == "no_status":
            verdict = "PASS_name_date" if extracted else "DROP"
        elif cat == "held_out_formats":
            verdict = "GAP_validity_lost" if extracted else "DROP_unusual_format"
        elif cat == "multi_mixed":
            verdict = "GAP_statuses_indistinct" if len(matched) >= 1 else "DROP"
            if len(matched) >= 2: verdict = "PARTIAL_both_kept_no_status"
        else:
            verdict = "UNCLASSIFIED"
        rows.append(dict(id=tid, category=cat, realism=g["realism"], domain=g.get("cert_domain"),
                         is_control=g.get("is_control"), line=g["exact_source_line"],
                         extracted=extracted, n_matched=len(matched),
                         validity_field=validity_field, verdict=verdict))
    return rows

# ---------------------------------------------------------------------- SKILL
ALIAS = {"SQL":["sql"],"AWS":["aws","amazon web services"],"Azure":["azure"],
         "Kubernetes":["kubernetes","k8s"],"Docker":["docker"],"React":["react"],
         "Go":["go","golang"],"Tableau":["tableau"],"Spark":["spark","apache spark"],
         "TypeScript":["typescript"],"Python":["python"],"Java":["java"]}
def skill_present(skill, skills):
    pats = ALIAS.get(skill, [skill.lower()])
    for s in skills:
        hay = (s.get("name","") + " | " + s.get("text","")).lower()
        if any(re.search(r"\b" + re.escape(p) + r"\b", hay) for p in pats):
            return s
    return None
def score_skill():
    gt = load(os.path.join(HERE, "skill/ground_truth_skill.json"))
    rs = resp_map(os.path.join(HERE, "skill/results/skill-responses-100.json"))
    weak = {"working","basic","exposure","learning","theoretical","historical","interest"}
    rows = []
    for tid, g in gt.items():
        if tid == "_meta": continue
        it = rs[tid + ".pdf"]; skills = data(it).get("skills") or []
        cat = g["claim_strength"]; s = g["skill"]; s2 = g.get("secondary_skill") or ""
        hit = skill_present(s, skills); present = hit is not None
        sec_hit = skill_present(s2, skills) if s2 else None
        sec_present = sec_hit is not None
        # any partial strength signal attached?
        strength_sig = bool(hit and (hit.get("experienceMonths") or hit.get("lastUsed")))
        if cat in ("expert", "proficient"):
            verdict = "PASS_CONTROL" if present else "FAIL_CONTROL_dropped"
        elif cat in weak:
            verdict = "GAP_strength_lost" if present else "DROP_skill_absent"
        elif cat == "denied":
            verdict = "GAP_denied_as_possessed" if present else "OK_suppressed"
        elif cat == "scoped_exclusion":
            verdict = "GAP_excluded_as_possessed" if sec_present else "OK_excluded_absent"
        elif cat == "distractor_fp_trap":
            if sec_present and present: verdict = "GAP_denied_kept_affirmed_kept"
            elif sec_present: verdict = "GAP_denied_surfaced"
            elif not present: verdict = "FAIL_affirmed_dropped"
            else: verdict = "OK_denied_suppressed_affirmed_kept"
        elif cat == "cert_vs_use":
            verdict = "OK_skill_kept" if present else "FAIL_skill_suppressed"
        else:
            verdict = "UNCLASSIFIED"
        rows.append(dict(id=tid, category=cat, realism=g["realism"], skill=s, secondary=s2,
                         is_control=g.get("is_control"), is_distractor=g.get("is_distractor"),
                         line=g["exact_source_line"], present=present, secondary_present=sec_present,
                         strength_signal=strength_sig, verdict=verdict))
    return rows

# ------------------------------------------------------------------- rollups
def rollup(rows, key="category"):
    out = collections.OrderedDict()
    for r in rows:
        out.setdefault(r[key], collections.Counter())[r["verdict"]] += 1
    return out

def write(issue, rows):
    json.dump(rows, open(os.path.join(OUT, f"{issue}_scored.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)

def main():
    edu = score_education(); cert = score_certification(); sk = score_skill()
    for name, rows in [("education", edu), ("certification", cert), ("skill", sk)]:
        write(name, rows)
    report = {"education": edu, "certification": cert, "skill": sk}
    # console summary
    for issue, rows in report.items():
        print(f"\n===== {issue.upper()} ({len(rows)}) =====")
        vc = collections.Counter(r["verdict"] for r in rows)
        for v, n in vc.most_common():
            print(f"  {n:3}  {v}")
    # structural absences
    print("\n--- structural: qualifier field present on ANY entry? ---")
    print("  education completion status:",
          any(r["status_field"] for r in edu))
    print("  certification validity status:",
          any(r["validity_field"] for r in cert))
    print("  skill strength/negation field: (schema has none; partial signals:",
          sum(1 for r in sk if r["strength_signal"]), "skills had experienceMonths/lastUsed)")
    json.dump(report, open(os.path.join(OUT, "ALL_scored.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print("\nwrote findings/ ->", OUT)

if __name__ == "__main__":
    main()
