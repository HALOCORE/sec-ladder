# PITFALLS.md — things that did not work here, and cost real sessions

**Read this before writing prose or touching the renderer.** Every entry is
something that actually happened in this repository, was believed by a competent
agent at the time, and had to be undone. Most were found by a reader, not by a
check.

The entries are ordered by how much they cost. The first four are the same
mistake wearing different clothes, and they are the reason five framings of the
report were rejected.

---

## 1. WRITING — where almost all the damage was

### 1.1 ⚠⚠⚠ You will write a proof. You are supposed to be teaching.

**The single most expensive lesson in this repo.** This project's research
culture is `CLAIMS.md`, the gate, *"every number ships its scope"*, *"cheapest
found, never minimum"*. That discipline is **correct for the research** and is a
**disease in the write-up**.

What it produces:

> claim → scope → denominator → counterexample → qualification → qualification of
> the qualification

What teaching needs:

> ### Claim. One concrete picture. So what.

A cold reader's verdict on the fully-qualified version: *"**No number in this
document survives its own paragraph**, so I stopped trying to carry any of them
out. Four things out of maybe eighty stayed with me — and they are the ones that
arrived **without** an immediate qualifier."*

✅ **The corollary that resolves it, and it is now binding:** if a figure needs a
qualifier it cannot carry, **cut the figure, not the qualifier.** Thirty
unqualified numbers retain better than eighty qualified ones. A reader should
leave with three or four things; if your document has fifty findings each
perfectly scoped, they leave with nothing.

### 1.2 ⚠⚠⚠ "The reader was confused by X" does not mean "explain X better"

**This is how every fix round made the document worse.** Four rounds in a row,
a reader said something was unclear and the response was another clause. The word
count went 7,158 → 9,209 → 8,085 while *length* was one of the three things the
reader had docked it for.

The worst instance: a reader complained our denominators did not reconcile
(27 → 26 → 22 → 9 → 9 → 4). The "fix" was a sentence reading *"Do not add those
up — they are overlapping descriptions, not boxes. One of the four cheaper ones
is also one of the flat nine, and one program answers to none of them."*

> ✅ **They did not want the machinery explained. They wanted it gone.** The
> repair was one sentence with no denominators in it at all.

⚠ **A fix that makes the primary complaint worse is not a fix.** Check the
complaint you are answering against the diff you just wrote.

### 1.3 ⚠⚠ Front-loading is not motivating

A cold read found four things *used before they were given*, so four fixes each
said "move it earlier". Nobody re-read the destination. **The setup slide ended
up carrying seven topics** — the six versions, two tool definitions, the build
count, the machine, the reference implementation, the attack count, the unit, the
inlining convention, and a promise about stopwatches. Owner's verdict, in
capitals: *"WHAT OVERCOMPLICATED MESS WITHOUT MOTIVATION"*.

✅ A fact belongs where the audience needs it **and has a reason to want it**.
The fix for use-before-define is usually **one clause at the point of use**, not
a paragraph moved to the front.
✅ **After any move, re-read the destination.**

### 1.4 ⚠⚠ Organise by OBJECTION, not by FINDING

Four framings (`ver_A`–`ver_D`) were rejected for this, and it took the owner
saying it four times. A section named after a result has to argue for its own
relevance before it can start — which is the abstract throat-clearing that got
each version rejected. **A finding carries no motivation. An objection carries
its own, because the reader supplied it.**

### 1.5 ⚠⚠ Apply your new test to the whole document, not to the example you were given

> "I said this is problematic **DOES NOT MEAN this is the only problematic.**"

Twice, a specific defect was named and fixed in place while the same defect sat
in twenty other slides. **When told something is broken, audit every instance of
the property that broke it before replying.**

### 1.6 ⚠⚠ The say-it-out-loud test — apply it to the QUESTIONS too

A whole pass fixed the *answers* into the reader's world and never checked the
*questions*. A third of them were questions a **peer reviewer** asks about a
method: *"What does the corpus say?"* · *"How hard did you look?"* · *"Is that
zero real?"* · *"Is your corpus even representative?"* They pass every structural
check and still make the document unreadable.

> ✅ **Could somebody say this out loud, having heard only what came before?**

The worst one — *"But I measured a big number"* — had an answer that offered
*"which two versions you subtract"*, which presumes the reader owns our six
versions. **They have their C, a compiler, and a blog post somebody sent them.**
Underneath it was the real objection, *"I've seen benchmarks where Rust is
slower"*, whose answer already existed nine slides away.

### 1.7 ⚠⚠ An audience shown two numbers WILL subtract or divide them

Two slides in a row invited arithmetic that did not close, and the reader stopped
following:
- a headline saying a cost *"vanishes"* over figures showing 626 → 502
- a *"sixty-five-fold span"* that computes to 52 from the numbers on the slide,
  because the dearest of five was never shown
- *"the same total, to the digit"* on a figure with four trailing zeros —
  *"the one place I felt actively worked on"* (it genuinely was not rounded; it
  looked rounded, which is the same thing to a reader)

✅ **Any ratio you state must be derivable from what is on the page, or the
numbers do not go there.** Where the working is shown and closes — *4 off every
pop, 2 onto every dropped push, 118 and 207 pops, 352 dropped* — the same reader
followed it happily.

### 1.8 Prefer a MECHANISM over a MAGNITUDE

The one slide a lost reader believed instantly:

> *"It jumps around the array by a rule the optimiser cannot follow, so there is
> nothing to hoist the test out of and nothing to fold it into. **I've read that
> disassembly. I believed it instantly and I didn't need the numbers.**"*

**Where we explained a mechanism in their vocabulary they believed us without
checking. Where we gave a magnitude they tried to check it and we lost them.**

### 1.9 Speak in the reader's world, and size every number

Banned in prose, because they exist only in our method: **corpus · rung ·
spelling · row · licensed for differencing · in contract · the gate · cell ·
band · pinned contract · identity pin · the model · pattern · the tree.**

And a number nobody can size is noise: *"the median is 24"* → *"about 24
instructions per call — on any function that does real work you will not find
that in a profile."*

⚠ **Translating into plain words is itself a review.** Four claims got visibly
weaker the moment the jargon came off — *"hardening C is cheap"* turned out to be
false as a law once the range had to be said out loud. **If a claim only sounds
strong in your own vocabulary, it is not strong.**

### 1.10 Do not let the title promise something the document does not keep

*"Eight objections"* over twenty-two questions and 5,500 words: *"I budgeted for
eight and got a 5,500-word document. **That mismatch is why I nearly quit.**"*

### 1.11 Never write about earlier versions of the document

A report must be self-contained. *"An earlier draft of this report…"* was in four
places and all four are gone. Version history goes in a collapsed editorial note
**below the references**, never at the top and never in the prose.

---

## 2. EVIDENCE — how false things got in

### 2.1 ⚠⚠⚠ A FACT PACK IS NOT A SOURCE. This happened four times.

Every round, a brief was written summarising the evidence and handed to writers.
Every round, an independent check found errors **that originated in the brief**:

- one round: **13 of the pack's entries** wrong or materially misleading
- one entry stated a tally as "six" and **explicitly forbade the correct "seven"**
- *"0 of 4,104 runs end loud"* — **false**; 109 end in a signal and 8 hang
- *"safe Rust will not compile one, so there is no version to price"* — **false**;
  it is priced at +0.4% / +0.1%
- *"three assertions away"* — **appears nowhere in the research tree**

✅ Verify at the **primary artefact** — the pattern's `NOTES.md` — not at a
summary. ⚠ **`results/SYNTHESIS.md` is a summary.** Reading it is not verifying.

### 2.2 ⚠⚠ `\num{}` keeps a NUMBER live. It does not keep a SENTENCE true.

A 27th pattern landed mid-session. Every live value updated correctly and the
prose went wrong anyway: *"25 of the 26"* rendered as *"25 of the 27"*, silently
asserting two exceptions where the next sentence describes one.

**What changed was the denominator's MEANING, not the number.**

✅ A paper resolves against **`totals.passing.*`** (gate-passing patterns only)
and against **`totals.passing.analysed`** for anything quoted out of the research
synthesis, which covers fewer patterns than the tree holds. `build_data.py`
parses that document's own *"drawn from N kernels"* and warns when they diverge.

⚠ **The corpus moved 26 → 27 → 26 → 27 within one session.** Never write a
sentence that only reads true at one of them.

### 2.3 ⚠⚠ An escape hatch becomes a silencer

The paper printed *"126 required-but-absent spellings"* with `%%literal-ok 126`
beside it. The real value was **175**, and **the literal-ok was suppressing the
one warning that would have caught it.** A number frozen on purpose and one
frozen by mistake look identical from inside the build.

✅ `build_data.py` now **lists every suppression on every build**. Re-read them
whenever the corpus moves.

### 2.4 ⚠ A guard that only fires on failure goes silent when the thing passes

The first version of the passing/analysed guard warned only while a pattern was
`FAIL`. The day it passed, the warning vanished and the prose went wrong quietly.
✅ Guard the **invariant**, not the symptom.

---

## 3. THE RENDERER — one bug class, found four times

### 3.1 ⚠⚠⚠ EVERY string a reader sees must go through `md()`. Every time.

Four separate discoveries of the same defect:

1. LaTeX-style ` ``quotes'' ` in a `\section` title → literal backticks
2. the paper **outline** pushed `b.text` raw
3. a slide's **question banner**, a quote's **source**, and **column headings**
   pushed raw — four slides shipped literal backticks and asterisks
4. `build_data.py`'s own warning text contained `totals.passing.*` and the bare
   asterisk failed the Method tab's markdown sweep

✅ **The doubling is the diagnostic.** A section title renders **twice** — as the
heading and again in the outline — so seven titles with two backticks each
reported **28**. If a count is exactly twice what the source suggests, look for a
second, rawer path to the page before you touch the prose.
✅ `slides.js` now routes every text field through one `MD()` helper. Add a field
that renders text without it and it *will* ship its own markup.

### 3.2 ⚠⚠ A check that renders one item is not a check

`check.mjs` walked **slide 1 of 52**. Fifty-one slides could have been malformed
and it printed `OK`. It now renders **every slide in both states** and sweeps
each for literal markdown.

### 3.3 ⚠ Bind to `globalThis`, not `window`

`slides.js` originally used `(typeof window !== "undefined" ? window : globalThis)`.
In `check.mjs`'s sandbox `window` is a plain object distinct from the global, so
the deck silently never loaded and the check passed on an empty banner. Match
`syntax.js`: `(typeof globalThis !== "undefined" ? globalThis : this)`.

### 3.4 ⚠ A green render check cannot see CSS, and there is no screenshot on this box

`CLAUDE.md` rule 6, still true. ~120 lines of deck CSS shipped **unlooked at**.
Say so rather than implying it was verified.

---

## 4. PROCESS

### 4.1 Read the result yourself; do not relay a subagent's verdict

Agents reported success on work that a cold read then dismantled. They also
**correctly refused** two of my instructions — one where I asked for a claim
whose source passage was struck through and marked WITHDRAWN, one where my own
correction was worded backwards. ✅ Give a writer the *reasoning* behind a rule
and they will check the rule.

### 4.2 Blind cold reads are the only check that finds these

Structural checks, fact-checks and gates all passed on documents that a reader
could not follow. **Run a persona who reads only the rendered output, at reading
speed, with nothing else** — and ask the two questions that matter:

> **Where did you first get lost? And did you ever recover?**

The second question is what separates a local defect from a structural one. *"Two
slides fully wasted, one half-wasted"* means the flow broke upstream of the slide
they named.

### 4.3 Ask "which way do the gaps point?" — separately, of a finished draft

The highest-yield review in this project. Run against a draft whose every figure
reproduced correctly, it found a **real coverage bias** and diagnosed it:

> *"Its disclosures cluster in the two places the last review looked, and its
> gaps cluster in the three it did not: what the instrument measures, what the
> corpus is made of, and what the proof rung has been measured to fail at."*

**That is a law about review, not about this paper.** You harden where you were
last caught. Audit the places nobody has looked yet.
