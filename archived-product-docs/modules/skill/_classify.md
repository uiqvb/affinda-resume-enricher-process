# `modules/skill/_classify.py` — the precision guard

**In one line:** decide a skill's strength by reading **only the piece of the sentence
that belongs to that skill** — never the whole sentence.

This is the single most important idea in the product, so it gets the fullest doc.

---

## The problem it solves

Resumes cram several skills, with different strengths, into one sentence:

```
"no experience with SQL, but expert in Python, learning Excel"
```

If we read that **whole** sentence to judge **SQL**, we'd see the word *"expert"* and
wrongly call SQL `strong`. The cue for one skill leaks onto another. That single
mistake — calling a denied skill "strong" — is exactly the kind of error that makes a
tool untrustworthy.

---

## The fix: walls, and pieces

We never read the whole sentence. We cut it into **pieces** at **walls**, then keep
only the piece that actually contains this skill.

A **wall** is a natural fence between two skills' descriptions:

| Wall kind | Examples |
|-----------|----------|
| punctuation | `,`  `;`  `:`  `|` |
| joining word | `and`  `but`  `however`  `whereas`  `while`  `though`  `also`  `plus` |

Watch the sentence get cut:

```
"no experience with SQL , but expert in Python , learning Excel"
 └──── piece A ────────┘ │   └──── piece B ───┘ │ └── piece C ──┘
                      wall(,)  wall(but)      wall(,)
```

- Judging **SQL** → read **piece A** only → sees *"no experience"* → `no_experience` ✓
- Judging **Python** → read **piece B** only → sees *"expert"* → `strong` ✓
  (the word *"no experience"* is in piece A — it can't reach Python)
- Judging **Excel** → read **piece C** only → sees *"learning"* → `learning` ✓

---

## The three methods

| Method | Plain job |
|--------|-----------|
| `_pieces` | cut the sentence at every wall; remember where each piece starts |
| `_piece_around` | pick the one piece that contains this skill |
| `classify_skill` | match cue words in that piece; return status + the matched words + where they are |

### `_pieces(sentence)` — cut at the walls
Returns a list of `(startPosition, text)` — the start position is kept so a cue found
in a piece can be traced back to its spot in the whole sentence (for an exact
highlight).

```
"no experience with SQL, expert in Python"
   ->  [ (0,  "no experience with SQL"),
         (24, " expert in Python") ]
         └ starts at character 24 in the sentence
```

### `_piece_around(sentence, skill)` — pick the right piece
```
look through the pieces for the one whose text contains the skill name
   found    -> return that piece (and where it starts)
   not found -> fall back to the WHOLE sentence
               (better to read a little too much than to lose the skill)
```

### `classify_skill(sentence, skill)` — the decision
```
piece = the piece around this skill
look at every skill rule in ORDER (strongest/worst signal first):
    if a cue pattern appears in the piece:
        return (that status, the exact words matched, where they start in the sentence)
no cue matched  ->  return ("plain", nothing, nowhere)
```

It returns **three** things now: the status, the matched cue words, and the cue's
**position** — so the proof highlight can point exactly at the cue (see
[`../../shared/models.md`](../../shared/models.md), `build_evidence`).

---

## Worked example (the tested case)

```
sentence : "no experience with SQL, expert in Python, learning Excel"

classify_skill(sentence, "SQL")
   piece  = "no experience with SQL"      (position 0)
   rule   = no_experience matches "no experience"
   return  ("no_experience", "no experience", 0)

classify_skill(sentence, "Python")
   piece  = " expert in Python"           (position 24)
   rule   = strong matches "expert"
   return  ("strong", "expert", 25)       <- NOT no_experience  ✓ the guard worked
```

---

## Honest limitations (for later)

- **Walls are a good-enough heuristic, not grammar.** A sentence like *"SQL and Python,
  both expert"* puts *"and"* as a wall, so each skill reads its own tiny piece and may
  miss the shared *"expert"*. Rare; noted.
- **Exact cue matching only** — a typo like *"experiance"* won't match yet. The
  typo-tolerant "fuzzy" upgrade is deliberately deferred.
- Cue words themselves live next door in
  [`_rules.md`](_rules.md) — this file is only the *machinery*.
