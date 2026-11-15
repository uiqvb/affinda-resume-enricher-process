# `modules/certification/__init__.py` — the certification module's front door

**In one line:** `run(certificates, resumeText)` → one enrichment for **every**
certificate, by handing the certification cue words to the shared status engine.

---

## A deliberately tiny file

Like its education twin, this file does almost nothing itself. The real work lives in
the shared [`status_engine`](../../shared/status_engine.md). This file just connects
the engine to the certification vocabulary:

```
run(certificates, resumeText):
    return run_status(certificates, resumeText, CERT_RULES, kind = "certification")
```

| It passes | Which is | From |
|-----------|----------|------|
| the certificates | the items to check | Affinda |
| `CERT_RULES` | the certification vocabulary | [`_rules.md`](_rules.md) |
| `"certification"` | which severity menu to use | [`../../shared/models.md`](../../shared/models.md) |

---

## Education vs certification — same engine, different words

```
education/__init__.py     -> run_status(..., EDU_RULES,  "education")
certification/__init__.py -> run_status(..., CERT_RULES, "certification")
                                             └ only these two things differ
```

Both are three-line wrappers. That symmetry is the point: write the machine once, give
it two vocabularies. To change how certificates are judged, edit the words in
[`_rules.md`](_rules.md) — never this file.
