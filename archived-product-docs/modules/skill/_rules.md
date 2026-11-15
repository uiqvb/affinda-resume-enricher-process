# `modules/skill/_rules.py` — the skill cue words

**In one line:** the dictionary of phrases that tell us how strong a skill claim is.
Pure vocabulary — no machinery. The machinery that uses it is
[`_classify.md`](_classify.md).

---

## The seven skill statuses

`SKILL_RULES` is a list, checked **top to bottom, first match wins**. It's ordered
**worst/strongest signal first** on purpose, so a clear negation ("no experience")
beats a weak word that might also appear.

| Order | Status | Severity | Means | Example cue words |
|-------|--------|----------|-------|-------------------|
| 1 | `no_experience` | ⚠️ warning | listed, but denied | "no experience", "never used", "not proficient", ": none" |
| 2 | `learning` | ⚠️ warning | not yet real | "learning", "studying", "interested in", "keen to learn" |
| 3 | `lapsed` | ⚠️ warning | used to, not now | "previously", "used to", "years ago", "no longer use" |
| 4 | `basic` | ⚠️ warning | shallow | "basic", "familiar with", "some", "beginner", "exposure to" |
| 5 | `intermediate` | info | middling | "working knowledge", "hands-on", "comfortable with", "solid" |
| 6 | `strong` | info | genuine strength | "expert", "advanced", "extensive", "proficient", "5+ years" |
| — | `plain` | info | no strength words at all | *(nothing matched)* |

> **Why the four "weak" statuses are warnings.** A recruiter searching for "SQL" wants
> to know the resume actually said *"no experience with SQL"* or *"learning SQL"*. Those
> are the surprises worth surfacing. `intermediate`/`strong`/`plain` are normal — tagged
> `info`, kept for a complete mirror, but not flagged.

---

## How a rule is shaped

```
(status_name, [ list of cue patterns that mean that status ])
```

Each pattern is a small search pattern (a regular expression). A couple of touches
keep them accurate:

- `\b…\b` means **whole word** — so "some" doesn't match inside "**some**thing".
- `\d+\+?\s*years?` catches "5 years", "5+ years", "10 years" → `strong`.

You don't need to read the patterns to understand the tool — the table above is the
real content. The patterns are just how we spell those phrases for the computer.

---

## Changing the vocabulary

This is the file you edit to make the tool smarter about wording. Add a phrase to the
right status's list and it takes effect immediately — no other file changes. The
**order** of the statuses, though, is load-bearing: keep the worst signals on top.

If you add a brand-new status, you must also add it to the menu in
[`../../shared/models.md`](../../shared/models.md) (`STATUS_SEVERITY`), or the tool will
stop loudly the first time it's used — on purpose.
