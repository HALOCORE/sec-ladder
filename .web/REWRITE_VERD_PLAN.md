# REWRITE_VERD_PLAN — build `paper_vers/ver_D`

**Written to be executed cold, after the conversation that produced it is gone.**
Resume with: *"resume from REWRITE_VERD_PLAN.md and write ver_D."*

Read order on resume: **this file → `paper_vers/CLAIMS.md` (binding, all versions)
→ `paper_vers/ver_B/sections/` (the best previous opening) → the four cold reads
in `.temp/brief/REVIEW-undergrad{1,2,3,4}.md` if they survive.** ⚠ `.temp/` is
gitignored and may be gone; everything load-bearing is repeated here.

---

## 0. THE ONE-LINE BRIEF

The owner has now rejected three versions in a row, and the third rejection was
the sharpest: **"I don't get what this trash is at all. The first para is safety
number. WHAT safety number? … Can you write even a blogpost that a normal CS
undergrad can understand? … Even ver_B is better than this shit."**

**ver_D is a blog post.** Not a tech report written plainly — a blog post. If a
sentence would look at home in a paper, it does not belong.

---

## 1. WHY ver_C FAILED, MECHANICALLY

ver_C's prose is not the problem. It was rewritten to median-17-word sentences,
zero sentences over 35 words, no coined jargon, and it still scored **5/10** with
an undergraduate reading it cold, across four independent reads (3 → 4 → 5 → 5).

### 1.1 The opening asks the reader to already know the subject

| | first sentence |
|---|---|
| **ver_B** ✅ | *"You have a C or C++ codebase and somebody has proposed rewriting part of it in Rust."* |
| **ver_C** ❌ | *"A safety number is a claim about what caused what, and both halves are usually credited to the wrong thing."* |

ver_B tells you **who you are and why you care** in nineteen words. ver_C asks
you to already know that "a safety number" is a thing, that it has halves, and
that halves get "credited". The owner's reaction — *"WHAT safety number? campus
security phone number?"* — is the correct reaction.

⚠ **This was my own convention applied backwards.** The model was *open on one
instance that already contains the thesis*: a named program, real numbers, one
surprise. ver_C kept the thesis and deleted the instance. **An abstraction in
sentence one is the ver_A failure, and ver_C reintroduced it.**

### 1.2 The scores track ONE variable: how many things the reader holds at once

From the fourth cold read's per-section scores, against what each section asks
the reader to keep in their head:

| section | score | things in the reader's head at once |
|---|---:|---|
| the deleted-line table | **8** | **one program, one change** |
| the running example | **8** | **one program** |
| the retractions | **7–9** | **three stories, told one at a time** |
| the ten-row tally | 6 | ten programs |
| "both endpoints move" | **3** | the whole corpus, abstractly |
| the coverage table | **3** | twelve bug classes × six tools |

**It is not tables — the 8-scoring section has a table and the 3-scoring one has
none.** It is *cardinality*. One program: understood. A corpus: lost.

✅ **The rule that follows, and it is ver_D's spine: never more than one program
in the reader's head at a time, and never a claim about the corpus until they
have seen the program it came from.**

### 1.3 It is a paper wearing plain sentences

ver_C carries numbered findings F1–F6 cited across sections, `\ref`
cross-references, `principle` / `caveat` / `retraction` / `example`
environments, provenance tiers, counting rules, licence rules, and two
denominators for one number. **An undergraduate does not read that apparatus.
A blog post does not have it.**

---

## 2. WHAT ver_D IS

**A blog post for a second-year CS undergraduate**, of about **2,500–3,500 prose
words** — half of ver_B, a third of ver_C.

**Reader:** has written C, knows what a buffer overflow is, has heard Rust is
"safe", has never used a prover or a sanitizer, has never heard of this project,
will not look anything up, and is reading this because someone linked it.

**Register:** second person. Contractions. Paragraphs of two to four sentences.
Code blocks showing the actual line. One number per paragraph at most.

⚠ **ver_D does not have to carry the rigour, because ver_C already does.**
ver_A, ver_B and ver_C all stay on disk. The site has 26 pattern pages, a cost
view, a method view. **ver_D is the front door and it delegates.** When it wants
to say "and here is the full accounting", it links.

**This is the single most freeing fact in this plan.** Every previous version
tried to be complete. ver_D must be *true* and *interesting*, not complete.

---

## 3. THE SPINE — four stories, in this order

Each is one program. Each is a thing that happened. The claims come out of the
stories, never before them.

### Story 1 — the opening. One deleted line, five different failures.

The strongest artefact in the corpus by four independent measurements: every
cold reader called the deleted-line table the best thing in the paper, and one
called it *"understood in one read with no glossary."* **Lead with it.**

A record walker reads a length off the wire and trusts it. Delete one bounds
test — or, in plain C, just never write it, which is what that program ships —
and:

| the same missing check | what happens |
|---|---|
| plain C | crashes, no message |
| unsafe Rust | crashes, **exactly like C** |
| safe Rust | stops: `index out of bounds: the len is 3072 but the index is 3072` |
| safe Rust, tuned differently | stops with a **different** message, naming the length the attacker asked for |
| Rust with a proof | **does not compile** |

**And every one of them prints the right answer on well-formed input.** The bug
is invisible until it isn't.

Everything the report has to say is already in that table. Say so, then spend the
rest of the post earning it.

⚠ Facts that must ship with it: the plain C version **ships without the check** —
that is the pattern's designed bug, not a line we deleted. "Prints the right
answer" is **vacuous** for the proved version, which never compiles and so never
runs. And it is **reproducible from a committed generator**
(`insights/p16_control.py`, `--check` re-runs it) but **certified by no gate**.

### Story 2 — the number you were quoted is about something else.

Same program. What does memory safety cost here? **−2,545, 0, +77, or +17,123
instructions per call**, depending only on which two versions you subtract. And
if you write both versions the same way, the per-byte cost is **exactly zero**.

Then, and only then, one sentence of corpus: *we did this to 26 programs, and on
seven of ten big gaps the bounds check was not the main cost — it was an
iterator checking twice per item, a mask, a missing reslice, the shape of the
data.*

⚠ **One sentence. Not a table.** The ten-row table scored 6; the one-program
story scored 8.

### Story 3 — the one-character bug nothing catches.

A bitset indexes `words[q >> 6]`. Type `q >> 7`. The index is still inside the
array — it is just the **wrong word**. So the bounds check is happy, the
sanitizer is happy, the interpreter is happy, and the proof is happy. The
program returns a wrong answer and everything reports success.

That is the whole coverage argument, in one program, with no table. **The
twelve-row matrix scored 3 and does not go in ver_D.** If ver_D wants the general
point it gets one sentence: *every one of those tools is watching the edges of a
block of memory, and this bug never leaves the block.*

⚠ And the honest half, which is the interesting half: on the **sibling** bug
(`q >> 5`) the bounds check and the sanitizer *do* fire — but only on an input
nobody would write. The proof catches it on every input. Say that; it runs
against the easy story.

### Story 4 — the things we got wrong.

The retraction material scored 7–9 every read. It is the most-liked writing in
three versions of this report. **Keep it nearly as it stands in ver_C's
`70-caughtitself.md`** and make it the ending.

- A control came back byte-identical, and that was quoted as proof nothing moved.
  It was byte-identical because **the checker was reading a different field**. It
  could not have failed. → *a residual of exactly zero is not a strong pass; it
  is the signature of a test that could not fail.*
- A summary reproduced every figure correctly and was still biased, because of
  what it left out. → **coverage bias has no arithmetic signature**; the only
  check is asking *which way do the gaps point?*
- **And this report's own previous version failed that check** — its detector
  table asserted no tool was ever caught missing a bug it was looking for, which
  was true only after six of twelve rows had been dropped. **Quote the withdrawn
  sentence.**

---

## 4. WHAT DOES NOT GO IN — and this is most of the fight

**Banned outright:**

- ❌ Numbered findings (F1…), and any cross-reference between sections.
- ❌ `principle` / `caveat` / `retraction` / `example` environments. A blog post
  has paragraphs. (⚠ `\begin{quote}` for a real quotation is fine.)
- ❌ The twelve-row coverage matrix.
- ❌ The ten-row attribution table.
- ❌ Counting rules, licence rules, "fair to subtract", two denominators for one
  number, threshold sweeps, bucket distributions.
- ❌ Any sentence whose subject is the paper ("this section shows…").
- ❌ Any claim about the corpus that arrives before the program it came from.

**Kept, because they are the reason to trust it:**

- ✅ **The admission that our own baseline is inflated.** We require the proved
  version to compile to identical machine code, which rules out some faster
  unsafe versions — so every safe-versus-unsafe number here **flatters safe
  Rust**. One short paragraph, in plain words, and say what the rule buys before
  saying what it costs.
- ✅ **No Rust program in this whole corpus ever panicked** on a hostile input —
  not once, across 4,104 runs. So we never actually watched a bounds check save
  anything. The only evidence the check is real is the source code.
- ✅ Every *"we rebuilt this ourselves and no automated gate checks it"*.
- ✅ *"and we cannot explain it"*, which the cold readers named as the single
  sentence that bought the most trust.

---

## 5. THE FORMAT, AND ONE DECISION TO MAKE FIRST

`paper_vers/ver_D/` with `meta.json`, `paper.md`, `sections/*.md`, `refs.json`,
per `paper_vers/README.md`. Set `"current": true` and flip ver_C's to `false`.

⚠ **Four or five files, not nine.** Suggested: `00-opening.md` (story 1),
`10-cost.md` (story 2), `20-coverage.md` (story 3), `30-wrong.md` (story 4),
`99-close.md`. **No `\section` numbering if the renderer permits it**; if it does
not, the titles still carry the argument.

⚠ **Renderer traps that have each cost a session:** emphasis does not nest;
every block marker on ONE line or it vanishes silently with its `\label`;
`\num{path}` for every corpus count — the build **fails** on a bad path and
**warns** on a bare literal ≥100 matching a corpus total (`%%literal-ok <n>` with
a reason where a literal is right).

**The decision to make in the first five minutes:** ver_D will want numbers that
`\num{}` cannot supply (the four costs, the panic strings, the five outcomes).
Those are literals. **Decide once whether they are `%%literal-ok` or whether the
prose is reworded to avoid them, and be consistent.**

---

## 6. THE TEST, AND IT IS THE ONLY ONE THAT COUNTS

**An undergraduate persona reads the WHOLE thing, cold, once, at normal speed,
and rates it 1–10.** Not a summary page — three versions have now passed a
summary-page test and failed the real one.

**Target: 8/10.** ver_C plateaued at 5 across four reads.

Ask them the same four things every time: what is it claiming, in your own words;
what would you do differently; where would you have stopped; and which words did
you not know. ⚠ **Run it on a FRESH reader each time** — a reader who has seen a
previous draft cannot un-see it.

⚠⚠ **The two failure modes that have already burned three versions:**
1. **Glossing our jargon and not the real jargon.** ver_C carefully defined
   `rung` and `spelling` while never once defining **`kernel`**, which appears
   forty times and which a reader took to mean *operating system*.
2. **Every revision round adding words.** Plain phrasing costs ~10% more words
   than nested phrasing, so a readability pass makes the document *longer*.
   **If ver_D grows past 3,500, cut a story — do not shave qualifications.**

---

## 7. PROCESS

**Fewer agents than last time.** ver_C used nine writers and produced nine
voices; the plain-language rewrite then needed three passes to unify them.

1. **One writer for the whole post.** It is 3,000 words. One voice.
2. **One fact-check** against `paper_vers/CLAIMS.md` and the numbers, after the
   draft exists. ⚠ `CLAIMS.md` is binding and its 23 do-not-claim entries are all
   things a draft of this report actually said and had to withdraw.
3. **The cold read.** If it scores under 7, **change the structure, not the
   sentences** — that is the lesson of ver_C's four passes.
4. **Stop at 8.** Do not run a fifth pass to reach 9.

---

## 8. WHAT CARRIES OVER

**From ver_B:** its opening move — the reader's own situation, in the first
sentence, before any number. It is the best opening any version has had and the
owner has now twice said ver_B is more understandable.

**From ver_C:** the retraction section nearly verbatim; the deleted-line table;
the *"and we cannot explain it"*; the `kernel` definition; the four-value legend
wording (**caught / missed / not its job**) if any table survives at all.

**From the cold reads:** the list of words that must be glossed at first use —
`kernel`, `sanitizer`, `prover`, `slice`, `panic`, `control`, `clamp`, and
anything else the writer catches themselves using twice.

**Burned:** ver_C's thesis-first abstract opening; the numbered findings; the
coverage matrix; the attribution table; every counting rule; the apparatus.

⚠ **ver_A, ver_B and ver_C all stay on disk.** A version is a framing. Four
framings over one corpus is what the directory is for, and ver_D is allowed to be
the readable one precisely because the rigorous one is still there.
