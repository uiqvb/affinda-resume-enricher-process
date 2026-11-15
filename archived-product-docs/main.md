# `main.py` — the run button

**In one line:** the smallest script that actually *runs* Resume Enricher so you can see
the whole thing work.

---

## How to run it

From inside the `resume_enricher/` folder:

```
python main.py                    # enrich a built-in sample resume
python main.py some_resume.json   # enrich a real Affinda JSON file
```

---

## What it does

```
main():
    if a file was named on the command line:
        load that JSON file as the Affinda input
    else:
        use the built-in SAMPLE (a tiny resume with problems baked in)

    result = enrich(theInput)          // the whole pipeline (app/enrich.py)

    print the enrichmentJSON (the part we added)
    print the summary lines (the warnings, in plain English)
```

It's a thin wrapper around `enrich` — nothing clever. Its only job is to give you a
**run button** and something to look at.

---

## The built-in sample

The `SAMPLE` is hand-made to trigger one of every interesting case, so a single run
shows the tool reacting:

| Item | Resume says | Tool should report |
|------|-------------|--------------------|
| SQL | "no experience with SQL" | `no_experience` ⚠️ |
| Python | "expert in Python" | `strong` (info) — the proof it doesn't over-flag |
| Excel | "learning Excel" | `learning` ⚠️ |
| BSc Computer Science | "(withdrew 2016)" | `incomplete` ⚠️ |
| AWS Certified Solutions Architect | "(expired 2021)" | `expired` ⚠️ |

Python is in there on purpose: it's the control case proving the precision guard
doesn't drag a genuinely-strong skill down just because a denied skill sits in the same
sentence.

---

## Where to look next

- The pipeline it calls: [`app/enrich.md`](app/enrich.md)
- The shapes it prints: [`shared/models.md`](shared/models.md)
- The full tour of every file: [`README.md`](README.md)
