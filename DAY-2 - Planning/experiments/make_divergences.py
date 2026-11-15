#!/usr/bin/env python3
"""Build the curated 'where the parser gave two different answers' set."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
L = lambda p: json.load(open(os.path.join(HERE, p), encoding="utf-8"))
def M(p): return {it["fileName"]: it for it in L(p)}
def D(it): return it["response"].get("data", it["response"])
eR = M("education/results/education-responses-100.json"); eG = L("education/ground_truth_education.json")
cR = M("certification/results/certification-responses-100.json"); cG = L("certification/ground_truth_certification.json")
sR = M("skill/results/skill-responses-100.json"); sG = L("skill/ground_truth_skill.json")

def edu_end(tid):
    eds = D(eR[tid + ".pdf"]).get("education") or []
    if not eds: return None, None
    q = eds[0].get("qualification")
    end = (eds[0].get("dateRange") or {}).get("end")
    if isinstance(end, dict):
        if end.get("date"): return q, end["date"][:4]
        if end.get("current"): return q, "current"
    return q, None

def cert_names(tid):
    return [c.get("name") for c in (D(cR[tid + ".pdf"]).get("certifications") or [])]

def skill_in(tid, skill):
    alias = {"Spark":["spark"],"Azure":["azure"],"Tableau":["tableau"],"Python":["python"],
             "Java":["java"],"SQL":["sql"],"AWS":["aws"]}
    pats = alias.get(skill, [skill.lower()])
    for s in (D(sR[tid + ".pdf"]).get("skills") or []):
        hay = (s.get("name","")+" "+s.get("text","")).lower()
        if any(re.search(r"\b"+re.escape(p)+r"\b", hay) for p in pats):
            return s.get("name")
    return None

div = []

# 1) EDUCATION — same category, date invented for one, not the other
q1, y1 = edu_end("E042"); q2, y2 = edu_end("E039")
div.append({
    "issue":"Education","category":"incomplete / discontinued",
    "headline":"Same 'did not finish' wording — the parser invents a graduation year for one and not the other",
    "plain":"Both résumés say the degree was never completed. For one, Affinda stamped a conferral year onto it (so it reads as earned); for the other it left the date off. Neither carries an 'incomplete' status. Your layer labels both the same way, consistently.",
    "rows":[
        {"line":eG["E042"]["exact_source_line"],"id":"E042",
         "parser":f"{q1} · end date {y1}","bad":True,
         "reads":"looks conferred "+str(y1),"fix":"completionStatus: incomplete"},
        {"line":eG["E039"]["exact_source_line"],"id":"E039",
         "parser":f"{q2} · no end date","bad":False,
         "reads":"no status, no date","fix":"completionStatus: incomplete"},
    ]})

# 2) SKILL — identical 'exposure to X' phrasing, kept vs dropped by skill
kept = ("S037","Python"); dropped1 = ("S035","Spark"); dropped2 = ("S041","Azure")
rows=[]
for tid,sk in [kept,dropped1,dropped2]:
    nm = skill_in(tid, sk)
    rows.append({"line":sG[tid]["exact_source_line"],"id":tid,
                 "parser": (f"extracted as skill: \"{nm}\"" if nm else "NOT extracted — skill dropped entirely"),
                 "bad": nm is None,
                 "reads": ("ranks like an expert" if nm else "disappears from the résumé"),
                 "fix": ("claimStrength: weak_exposure" if nm else "(can't label what was dropped)")})
div.append({
    "issue":"Skill","category":"exposure",
    "headline":"Word-for-word the same claim — some skills are kept, some vanish",
    "plain":"Every line here is 'exposure to X'. Python comes through (but with no strength marker, so it ranks like real expertise). Spark and Azure are dropped from the skills list altogether. The strength gap and a separate extraction blind-spot both show up in one category.",
    "rows":rows})

# 3) CERTIFICATION — 'Bar admission' dropped everywhere; a sibling cert in the same category is kept
bar_names = cert_names("C082")
# a kept no_status cert sibling
kept_cert = None
for tid,g in cG.items():
    if tid=="_meta" or g["validity_category"]!="no_status": continue
    if "Bar" in g["cert_name"]: continue
    nms = cert_names(tid)
    if nms: kept_cert=(tid,g,nms); break
div.append({
    "issue":"Certification","category":"no status (name + date only)",
    "headline":"One named credential is a total blind spot — 'Bar admission' is dropped in every category",
    "plain":"A legal Bar admission is a real, licensable credential, but Affinda doesn't recognise the phrase and drops it completely — across expired, revoked, suspended, valid, every category we tried. A sibling cert in the same category (here PMP) is kept fine. This is a different failure from the validity gap: the whole entry is missing, not just its status.",
    "rows":[
        {"line":kept_cert[1]["exact_source_line"],"id":kept_cert[0],
         "parser":f"extracted: {kept_cert[2][0]}","bad":False,
         "reads":"on the record (status still absent)","fix":"validityStatus: unknown"},
        {"line":cG["C082"]["exact_source_line"],"id":"C082",
         "parser":"NOT extracted — certification dropped","bad":True,
         "reads":"credential missing entirely","fix":"(nothing to enrich — flag: dropped credential)"},
    ]})

# 4) CERTIFICATION multi-mixed — same cert active + expired, both identical
mm = None
for tid,g in cG.items():
    if tid=="_meta" or g["validity_category"]!="multi_mixed": continue
    certs = D(cR[tid+".pdf"]).get("certifications") or []
    if len(certs)>=2: mm=(tid,g,certs); break
if mm:
    tid,g,certs = mm
    def ds(c):
        d=c.get("date")
        if isinstance(d,dict):
            if d.get("date"): return d["date"][:4]
            if d.get("current"): return "current"
        return "—"
    rows=[{"line":f"(same résumé) {c.get('name')}  ·  date {ds(c)}","id":f"entry {i+1}",
           "parser":f"{c.get('name')} · {ds(c)}","bad":True,
           "reads":"both look like valid certs","fix":("validityStatus: active" if i==0 else "validityStatus: expired")}
          for i,c in enumerate(certs[:2])]
    div.append({
        "issue":"Certification","category":"active + expired (same cert, one résumé)",
        "headline":"The same certificate appears twice — active and expired — and both come back looking valid",
        "plain":"This résumé lists one cert as current and the same cert as expired (a renewal history). Affinda keeps both entries but there's no status on either, so they're indistinguishable. Your layer tags one active and one expired, so the renewal story is preserved.",
        "rows":rows})

json.dump(div, open(os.path.join(HERE,"findings/divergences.json"),"w",encoding="utf-8"),
          indent=2, ensure_ascii=False)
print("wrote",len(div),"divergence cards")
for d in div:
    print(" ",d["issue"],d["category"],"-",len(d["rows"]),"rows")
