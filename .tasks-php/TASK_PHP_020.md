# TASK_PHP_020 — how often is the CATALOGUE's mechanism claim wrong? Measure it.

**Role:** research **investigator**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_020_REPORT.md` — **write the FILE** (rule 10).
⚠⚠ **READ-ONLY OUTSIDE YOUR REPORT AND `.temp/php20/`.** You may not edit
`CATALOGUE.md`, `.memory-php/`, `RECAP_PHP.md`, `PROTOCOL_PHP.md`, `PLAN_PHP.md`
or anything under `patterns/`, `patterns-php/`, `harness*/`, `results*/`.
**Two other agents are running**; one writes `patterns-php/ph07-*` and
`harness-php/provenance.py`, the other adjudicates `CATALOGUE.md` **Part C** —
**your population is Part A/B and you must not touch Part C's kills.**
**No `git add` / `git commit`.** ⚠ **`.web/` is a CONCURRENT SESSION — never touch it.**
⚠ Scratch under `.temp/php20/`. **Never `/tmp`.**

Read `.tasks/PROTOCOL.md`, **`.memory-php/`** (authoritative), **`PLAN_PHP.md`
§3–§4**, `patterns-php/CATALOGUE.md` (Parts A and B), `patterns-php/SOURCES.md`,
and `.tasks-php/UPSTREAM_001.md` (the four batch rows are already surveyed
upstream-side — **do not redo it**).

⚠⚠ **`grep -a` ALWAYS.** Plain `grep` here is a shell function dispatching to
`ugrep`, which exits **1 with no output and no stderr** on any of the **41**
corpus files holding a non-UTF-8 byte — `ext/standard/{string,html,reg,formatted_print}.c`
and `ext/calendar/calendar.c` among them, cited by **13** catalogued rows. **An
agent who greps the tarball and finds nothing has learned nothing.** A probe
script under `sh` does not reproduce it. (F35, `PROTOCOL_PHP.md` §F6.)
⚠⚠ **And ask about a FUNCTION, not about text.** `.temp/php17/r1h/fn.py` is a
brace-matching extractor that already exists — **use it.**

---

## §1 Why this task exists

**93 rows are catalogued. Two are built. Every build so far has found the
catalogue's mechanism claim to be wrong or incomplete in some way**, and each
time it was found by the row that had already been chosen:

| | the catalogue said | the C said |
|---|---|---|
| `ph07` | characterised by *its loop* | the loop is bounded by `from`; **the missing bound is on `from`, and the fix is in the CALLER** (F34/F38) |
| `ph92` | *"the `int` overflow is the whole defect"* | `sizeof` yields `size_t`, so the RHS is **64-bit** and is **truncated by the store** — `ph21`'s class, not `ph19`'s (`TASK_PHP_017` §2.2) |
| `ph93` | cited the `:682` arm | `:692` — the row's **entire** distinctness — is **unreachable** in that arm |
| **`ph29`** | *"the allocator truncates `n mod 2^32`"* | ⚠ **UNVERIFIED and doubted**: `to_read` is a `long` and 5.0.0's `emalloc` takes a `size_t`, which on this 64-bit box truncates **nothing** (F36) |

⚠⚠⚠ **Three of those four were found by accident, while doing something else.
Nobody has ever asked how often it happens.** That number decides how much a
catalogue row can be trusted when a build task is written against it — and this
programme's own standing finding is that **an audit which re-examines only what
it doubts measures its own priors** (F21, F37). **So: measure a random sample.**

## §2 The population and the sample — draw it MECHANICALLY, before you read anything

1. **Enumerate Part A** — `grep -c '^| ph[0-9]' patterns-php/CATALOGUE.md` is
   **93** today. Verify it; do not trust this line (`PROTOCOL.md` rule 13).
2. **Draw a seeded random sample of 15** with a committed script under
   `.temp/php20/` (`random.Random(20).sample(...)` or equivalent — **the script
   is the evidence and it stays**). ⚠⚠ **Print the sample BEFORE you open a
   single C file, and put it in the report.** A sample chosen after looking is
   not a sample.
3. **Add the four batch rows** — `ph21 ph16 ph12 ph29` — as a **separately
   reported stratum**, because they are the next things to be built and are
   therefore worth checking whether or not they are in the sample. ⚠ **Report
   the two strata separately and never pool them into one rate** — the batch
   four are chosen, not drawn, and pooling would inflate or deflate the number
   depending on how they land.

## §3 The test, per row

For each row, at the **pinned 5.0.0 tarball** only:

1. **Do the cited `file:line`s resolve** to what Part B quotes? (`ADJUDICATION_001`
   was off by one on three of its own citations — F23.)
2. **Does the C support the stated mechanism?** Read the function, not the line.
   Name what is unchecked, what the attacker controls, in what type the
   arithmetic happens, and **where the value is truncated or the pointer
   escapes**. ⚠ **A store truncation and an expression overflow are different
   mechanisms** — `ph92` was mis-classified for exactly that reason.
3. **Is the stated trigger reachable on the stated arm?** — `ph93`'s was not.
4. **Verdict, one of four:** `SUPPORTED` · `IMPRECISE` (right defect, wrong
   description — say the correction) · `NOT SUPPORTED` (the C does not do this) ·
   `UNDECIDABLE` (say exactly what you would need).

⚠⚠⚠ **YOU ARE MEASURING A RATE, NOT HUNTING FOR ERRORS.** A sample that comes
back **15/15 `SUPPORTED` is an excellent result** and is the one I expect to be
most useful, because it licenses writing build tasks against the catalogue
without a per-row re-verification. **Do not stretch to find a defect, and do not
soften one you find.** ⚠ **Report the time you spent per row**, so the next
reader knows whether a `SUPPORTED` verdict was cheap or hard-won.

## §4 `ph29` — the one row with a live C-side question, and it can decide admission

`CATALOGUE.md` says `ph29`'s mechanism is *"the allocator truncates `n mod
2^32`"*; `ext/standard/streamsfuncs.c:321` is `emalloc(to_read + 1)` with
`to_read` a `long`. **`PLAN_PHP.md` §3 makes this a C-side question, so it can
decide admission** — and `CLAUDE.md` rule 6 makes it the **only** kind of
question that can.

**Settle it, at source, and give the answer as one of:**

- the mechanism is **32-bit-only** (say which `int`/`size_t` boundary, and
  whether the row is still admissible on a 64-bit build — **if it is not
  reproducible in our environment, that is criterion 2 and it decides**);
- the mechanism is **elsewhere** (name the real line — the row is admissible,
  re-catalogued);
- the row is **mis-catalogued and there is no defect** (a kill, C-side and
  legitimate);
- ⭐ or the mechanism is **something better than the catalogue says**. ⚠ Note
  that `.memory-php/00`/F3/F5 record **three separate allocator truncations** in
  5.0.0 — `zend_alloc.c:129`'s `real_size`, `:295`'s `int final_size` in
  `_ecalloc`, and `zend_alloc.h:53`'s `unsigned int size:31`. **Check whether
  `ph29` reaches one of them**; `size:31` in particular truncates a `size_t`
  that `emalloc`'s signature did not.

⚠ **Do NOT decide the row's fate.** Deliver the C and the four-way verdict; the
manager adjudicates.

## §5 Deliverables

1. **The sample-drawing script and its output**, printed before any verdict.
2. **A verdict table** for the 15, and a **separate** one for the batch four.
3. **Two rates**, reported separately, each with the count, and **an explicit
   sentence on what a sample of 15 out of 93 can and cannot support.** ⚠ **Do
   not compute a confidence interval you cannot justify** — this project has
   three findings about numbers that were invented rather than measured (F4,
   F12, F32). *"3 of 15, and 15 is too few to distinguish 10 % from 30 %"* is a
   better sentence than a spurious interval.
4. **Every correction, written as the exact replacement text** for the Part A
   row and Part B block. ⚠ **Do not edit `CATALOGUE.md`** — the manager lands it.
5. ⭐ **A recommendation on build order for the four batch rows, with C-side
   reasons only.** The standing order is `ph21 → ph16 → ph12 → ph29` and it was
   set before `FIXSURVEY_001` and `UPSTREAM_001` existed. **If the C says a
   different order is better, say so and why** — e.g. a row whose mechanism you
   could not settle should not be first.

## §6 What I am least sure of

1. ⚠⚠ **That 15 is the right sample size.** It is a guess at a budget, not a
   power calculation. **If you find the per-row cost is much lower than I
   assumed, draw a second seeded block of 10 and report the two blocks
   separately** — never extend a sample by continuing until the number looks
   right.
2. ⚠ **That `IMPRECISE` and `NOT SUPPORTED` are separable.** `ph92` was *"right
   defect, wrong class"* — is that one bucket or two? **If the distinction
   collapses in practice, say so and report a single "needs correction" count**;
   a category that cannot be applied consistently is worse than a coarser one.
3. ⚠⚠ **That the catalogue is the right thing to audit at all.** The alternative
   reading is that a mechanism description is a *pointer*, the build task reads
   the C anyway, and an error rate here costs nothing. ⭐ **`ph07` is the
   counter-example — its catalogued characterisation sent two agents to the
   wrong function and cost a whole task** — but that is n = 1. **If your sample
   says the descriptions are load-bearing far less often than that, that is the
   finding and it is worth more than the rate.**
