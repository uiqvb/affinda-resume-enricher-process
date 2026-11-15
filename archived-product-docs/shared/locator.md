# `shared/locator.py` — the finder

**In one line:** hand it a word (like `SQL`) and the resume text; it gives back the
**sentence** around that word and its **exact spot** — or says "not found."

---

## Who calls it, and when

The resume parser (Affinda) extracts the list of skills, degrees and certificates.
The finder is called **once per item** in those lists.

> Affinda decides **which** items exist.
> `locate` finds **where** each one is, and the sentence around it.

It doesn't care what a word means — `SQL`, `Juris Doctor`, `AWS Certified` are all
just "a word to find."

---

## What it gives back

`locate(word, resume_text)` returns one of:

| Result | Meaning |
|--------|---------|
| `(sentence, sentenceStart, spot)` | found it — the sentence, where that sentence begins in the resume, and the exact (start, end) of the word |
| `(None, None, None)` | not found — the caller then stays safe (no guess, no highlight) |

- The **sentence** is the small window the rules will read later.
- The **sentenceStart** is where that sentence begins in the whole resume. The rules
  later find a cue *inside* the sentence (say at position 8); adding `sentenceStart`
  turns that into the cue's spot in the whole resume — which is how the cue's
  highlight stays exact. (See `build_evidence` in [`models.md`](models.md).)
- The **spot** is where the *word itself* sits — used as the highlight only when no
  cue words are found (a "plain" item).

---

## What it borrows from `matching.py`

The finder is the "brain"; it leans on four helpers (the "hands") from
[`matching.md`](matching.md):

| Helper (from `matching.py`) | What it does here |
|------------------------------|-------------------|
| `normalize` | cleans the small search word |
| `normalize_mapped` | cleans the big resume text **and** returns the index map |
| `exact_token_find` | finds the word as a whole word |
| `fuzzy_spaceless_find` | backup: finds a word split by spaces, like `S Q L` |

---

## How it works — in plain steps

1. **Clean the search word.** `SQL` → `sql`.  *(uses `normalize`)*
2. **Clean the resume text, and keep the index map.**  *(uses `normalize_mapped`)*
3. **Look for the word** in the cleaned text, as a whole word.  *(uses `exact_token_find`)*
   - If that fails, try the backup for spaced-out words like `S Q L`.  *(uses `fuzzy_spaceless_find`)*
   - If it still isn't there → return `(None, None)`. We never guess.
4. **Translate the position back** to the original text, using the index map.
5. **Grab the sentence** around that spot, and note where that sentence begins.  *(uses `clause_around`)*
6. **Return** the sentence, its start position, and the `(start, end)` spot of the word.

> **The index map (steps 2 & 4).** Cleaning changes the text's length, so a position
> in the cleaned text isn't the same as in the original. The index map is just a
> translation list — *cleaned position → original position* — so the highlight lands
> exactly right. Full walkthrough in [`matching.md`](matching.md).

`clause_around` simply grows outward from the spot until it hits a sentence boundary
or about 120 characters. It also reports where the trimmed sentence begins in the
original text (so a cue found inside it can be traced back exactly).

**Two boundary sets (important).** `locate()` takes an optional `boundaries` set:
- **Default** (`.  ;  !  ?  newline  |  —  –  •  ·`) — used by **skills**, because
  résumés list skills as `Git — Linux — Agile` and each must stay separate.
- **`STATUS_BOUNDARIES`** (`.  ;  !  ?  newline  |`, *no dashes/bullets*) — used by
  **education & certification**, because those entries put the qualifier *after* a
  dash: `CISSP — expired 2022`, `BSc … — currently enrolled`. Stopping at the dash
  would hide the status word. (This single change lifted edu/cert recall from ~30%
  to ~76–87% in `eval/results/REPORT.md`.)

---

## Examples (the actual tested cases)

| Resume text | We search | Result |
|-------------|-----------|--------|
| `No experience   with SQL.` | `SQL` | found, spot is exact even with the 3 extra spaces |
| `Proficiency: S Q L` | `SQL` | found via the spaced-out backup |
| `Strong communication skills` | `C++` | **not** found (won't match the `c` inside a word) |
| `Skills: SQL, Python` | `Kubernetes` | not found → stays safe |
| `BSc Computer Science (withdrew 2016). More.` | `BSc Computer Science` | found; sentence stops at the `.` |

---

## Why this matters
Every feature (skill, education, certification) starts by calling `locate`. The
**sentence** it returns is the small window the rules read — the first thing that
stops a neighbouring item's words leaking in. The **spot** it returns is the proof in
every `Evidence`.
