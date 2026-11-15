#!/usr/bin/env python3
"""Pick vivid before/after examples from the real responses for the visual page."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
L = lambda p: json.load(open(os.path.join(HERE, p), encoding="utf-8"))
def M(p): return {it["fileName"]: it for it in L(p)}
def D(it): return it["response"].get("data", it["response"])

eR = M("education/results/education-responses-100.json"); eG = L("education/ground_truth_education.json")
cR = M("certification/results/certification-responses-100.json"); cG = L("certification/ground_truth_certification.json")
sR = M("skill/results/skill-responses-100.json"); sG = L("skill/ground_truth_skill.json")

examples = []

# ---- EDUCATION ----
def edu_pick(cat, want_end, skip_cert=True):
    for tid, g in eG.items():
        if tid == "_meta" or g["status_category"] != cat: continue
        if skip_cert and "Certificate" in g["qualification"]: continue
        eds = D(eR[tid + ".pdf"]).get("education") or []
        if not eds or not eds[0].get("qualification"): continue
        end = (eds[0].get("dateRange") or {}).get("end")
        has = bool(isinstance(end, dict) and end.get("date"))
        if has == want_end:
            return tid, g, eds[0]
    return None

edu_specs = [
    ("expected", True, "status", "expected",
     "The parser turned the future graduation year into an END date, so a degree the person hasn't earned yet looks already conferred."),
    ("withdrawn", True, "status", "incomplete_withdrawn",
     "The year they LEFT became a conferral end date, so a dropped-out degree looks completed."),
    ("in_progress", False, "status", "in_progress",
     "No fake date this time (good) — but there is still no field saying it's in progress, so a filter can't tell it from a finished degree."),
]
for cat, we, field, val, why in edu_specs:
    r = edu_pick(cat, we)
    if not r: continue
    tid, g, e = r
    before = {"qualification": e.get("qualification"), "institution": e.get("institution"),
              "level": e.get("level"), "dateRange": e.get("dateRange")}
    after = dict(before)
    after["__resumeGuard"] = {"completionStatus": val,
                              "evidence": g["exact_source_line"]}
    examples.append({"issue": "Education", "id": tid, "category": g["status_category"],
                     "resume_line": g["exact_source_line"], "why": why,
                     "before": before, "after": after, "field": "completionStatus"})

# ---- CERTIFICATION ----
def cert_pick(cat, name_contains=None):
    for tid, g in cG.items():
        if tid == "_meta" or g["validity_category"] != cat: continue
        if name_contains and name_contains.lower() not in g["cert_name"].lower(): continue
        certs = D(cR[tid + ".pdf"]).get("certifications") or []
        if certs:
            return tid, g, certs[0]
    return None

cert_specs = [
    ("expired", "AWS", "expired",
     "The cert comes back with just a name and date — the word 'expired' is gone, so an invalid cert looks valid."),
    ("revoked", None, "revoked",
     "A revoked credential returns identical to an active one. In a licensed role that's a compliance liability."),
    ("pending_scheduled", None, "pending_not_held",
     "An exam only SCHEDULED comes back looking like a credential the person already holds."),
]
for cat, nc, val, why in cert_specs:
    r = cert_pick(cat, nc)
    if not r: continue
    tid, g, c = r
    before = {k: c.get(k) for k in ("name", "date", "issuer") if c.get(k) is not None}
    after = dict(before)
    after["__resumeGuard"] = {"validityStatus": val, "evidence": g["exact_source_line"]}
    examples.append({"issue": "Certification", "id": tid, "category": g["validity_category"],
                     "resume_line": g["exact_source_line"], "why": why,
                     "before": before, "after": after, "field": "validityStatus"})

# ---- SKILL ----
def skill_entry(tid, skill):
    skills = D(sR[tid + ".pdf"]).get("skills") or []
    import re
    alias = {"SQL":["sql"],"AWS":["aws"],"Kubernetes":["kubernetes"],"Docker":["docker"],
             "Python":["python"],"Java":["java"],"React":["react"],"Go":["go"]}
    pats = alias.get(skill, [skill.lower()])
    for s in skills:
        hay = (s.get("name","")+" | "+s.get("text","")).lower()
        if any(re.search(r"\b"+re.escape(p)+r"\b", hay) for p in pats):
            return s
    return None

def skill_pick(cat, skill_pref):
    for tid, g in sG.items():
        if tid == "_meta" or g["claim_strength"] != cat: continue
        if skill_pref and g["skill"] != skill_pref: continue
        e = skill_entry(tid, g["skill"])
        if e: return tid, g, e
    # fallback any
    for tid, g in sG.items():
        if tid == "_meta" or g["claim_strength"] != cat: continue
        e = skill_entry(tid, g["skill"])
        if e: return tid, g, e
    return None

skill_specs = [
    ("denied", "SQL", "denied",
     "The resume literally says NO experience with this skill — but it still shows up in the skills list as if they have it."),
    ("exposure", None, "weak_exposure",
     "'Limited exposure to X' is extracted identical to '8-year expert in X' — the strength is gone, so ranking treats them the same."),
    ("learning", None, "aspirational_learning",
     "'Currently learning X' becomes a possessed skill — a goal is counted as a capability."),
]
for cat, pref, val, why in skill_specs:
    r = skill_pick(cat, pref)
    if not r: continue
    tid, g, e = r
    before = {"name": e.get("name"), "text": e.get("text")}
    after = dict(before)
    after["__resumeGuard"] = {"claimStrength": val, "evidence": g["exact_source_line"]}
    examples.append({"issue": "Skill", "id": tid, "category": g["claim_strength"],
                     "resume_line": g["exact_source_line"], "why": why,
                     "before": before, "after": after, "field": "claimStrength"})

# ---- distractor (precision) special case ----
for tid, g in sG.items():
    if tid == "_meta" or g["claim_strength"] != "distractor_fp_trap": continue
    s, s2 = g["skill"], g["secondary_skill"]
    e1, e2 = skill_entry(tid, s), skill_entry(tid, s2)
    if e1 and e2:
        before = {"skills": [e1.get("name"), e2.get("name")]}
        after = {"skills": [
            {"name": e1.get("name"), "__resumeGuard": {"claimStrength": "affirmed"}},
            {"name": e2.get("name"), "__resumeGuard": {"claimStrength": "denied"}}]}
        examples.append({"issue": "Skill", "id": tid, "category": "distractor_fp_trap",
                         "resume_line": g["exact_source_line"],
                         "why": "The parser keeps BOTH the affirmed and the denied skill, with no way to tell them apart. The enrichment keeps both too — but labels which is real. (This is the precision trap our detector must not fail.)",
                         "before": before, "after": after, "field": "claimStrength"})
        break

json.dump(examples, open(os.path.join(HERE, "findings/examples_before_after.json"), "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)
print("wrote", len(examples), "examples")
for e in examples:
    print(" ", e["issue"], e["id"], e["category"], "::", e["resume_line"][:50])
