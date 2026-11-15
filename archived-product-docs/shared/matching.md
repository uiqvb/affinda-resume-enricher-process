# `shared/matching.py` — the text helpers

The finder ([`locator.md`](locator.md)) is the **brain**. This file is the **hands**:
the small helpers that clean messy resume text and search it.

Why it's needed: Affinda gives us a clean word like `SQL`, but the resume text is
messy — odd spacing, punctuation, line breaks. These helpers tidy it up so the word
can be found, and remember where everything came from so highlights stay exact.

> **First, a myth to kill:** cleaning does **not** jam words together.
> `"this line is dumb"` → `"this line is dumb"` (unchanged — the single spaces stay).
> It only *lowercases* and *squeezes runs of spaces/punctuation down to one space*.
> (The only place spaces are fully removed is inside the fuzzy backup search.)

---

## The four helpers at a glance

| Helper | Plain job |
|--------|-----------|
| `normalize` | clean a small search word |
| `normalize_mapped` | clean the big resume text **and** return the index map |
| `exact_token_find` | find a word as a **whole** word (not inside another) |
| `fuzzy_spaceless_find` | backup: find a word split by spaces, like `S Q L` |

Our running example for the pictures below is the messy snippet **`Go,  SQL!`**
(note: capitals, a comma, **two** spaces, and a trailing `!`).

---

## Each helper, with the text shown changing

### `normalize(word)` — clean a search word
Turns a messy item name into one plain lowercase word. Watch it:
```
Python (Programming Language).      ← start
Python .                            ← drop the (...) chunk
python .                            ← lowercase
python                              ← punctuation/extra spaces -> gone; trimmed
```
- **Takes:** a small word (an item name).  **Gives back:** the clean word (`python`).
- **Used for:** the thing we search *for* (the needle). No index map needed.
- **How:** it just reuses `normalize_mapped` and throws the map away.

### `normalize_mapped(text)` — clean the resume text + remember positions
Same cleaning, but on the big text, and it also hands back the **index map**.
Watch `Go,  SQL!` go through it:
```
original :  G   o   ,   ␣   ␣   S   Q   L   !
position :  0   1   2   3   4   5   6   7   8

cleaned  :  g   o   ␣           s   q   l
from pos :  0   1   2           5   6   7
```
What happened, character by character:
- `G o` → `g o` (just lowercased)
- `,` (pos 2) → became the single space
- the two real spaces (pos 3, 4) → **collapsed away** (we already had a space)
- `S Q L` → `s q l`
- `!` (pos 8) → a trailing separator → dropped

So it gives back **two things**: the cleaned text `"go sql"`, and the index map
**`[0, 1, 2, 5, 6, 7]`** (the "from pos" row).

### `exact_token_find(text, word)` — find a whole word
```
find "sql" in "go sql"          ->  found, starts at position 3
find "c"   in "communication"   ->  NOT found  (the c is inside a word)   ✓
find "c"   in "c and java"      ->  found       (the c stands alone)
```
- **Gives back:** the start position, or `-1`.
- **Why whole-word:** so a short word can't hide inside a bigger one.

### `fuzzy_spaceless_find(text, word)` — the backup for split-up words
```
find "sql" in "s q l"   ->  squeeze the spaces out of both:
                            "sql" in "sql"   ->  found   ✓
```
- **Gives back:** the `(start, end)` range, or `None`.
- **Guardrail:** only runs for words of **3+ letters**, so tiny tokens can't match
  random letters.

---

## The index map — why it exists

Cleaning made the text **shorter** (the comma became a space, two spaces collapsed, the
`!` dropped). So "position 3 in the cleaned text" is **not** "position 3 in the
original." The index map is the **translation list** that fixes this:

```
cleaned position :  0   1   2   3   4   5
cleaned char     :  g   o   ␣   s   q   l
original position:  0   1   2   5   6   7     ← this list IS the index map
```

See the jump from 2 → 5? That's where the collapsed spaces/comma were. Look up any
cleaned position in this list and you get its real spot in the original.

---

## Putting it together — one full find

```
we search for   :  "SQL"
normalize it    :  "sql"

find "sql" in cleaned "go sql"   ->  starts at cleaned position 3

translate back with the index map:
    cleaned 3  ->  original 5
    cleaned 5  ->  original 7
    so the original span is (5, 8)

check: original "Go,  SQL!"[5:8]  =  "SQL"   ✓  exact, despite all the mess
```

That exact `(5, 8)` is what becomes the highlight (the `Evidence`). This is the whole
reason the index map exists.

---

## The exact cleaning rules (for reference)
- lowercase everything
- turn every **run** of spaces/punctuation into **one** space
- keep the single spaces between words (words are never jammed together)
- `normalize` (the search word only) also drops `(...)` notes first

---

## Known limitations (honest notes for later)

- **Very short, punctuation-heavy names** (`C++`, `C#`, `.NET`) clean down to `c`, `c`,
  `net`. We can still find them as whole words, but they're easy to confuse, so the
  fuzzy backup is switched off for them. A future version can special-case these.
- **A word inside a bigger name** (finding `SQL` when the text says `MySQL`) can
  mis-match via the fuzzy backup. Rare, noted for later.

Neither ever gives a **wrong highlight** — the index map keeps positions exact. At
worst they find the wrong *occurrence*, which the sentence step can tolerate.
