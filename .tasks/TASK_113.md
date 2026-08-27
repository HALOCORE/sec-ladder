# TASK_113 — the review debt, starting with the one the SYNTHESIS rests on

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read `.tasks/PROTOCOL.md`, then this file, then `.tasks/TASK_102_REPORT.md` **in
full**, then `RECAP.md` **finding 37**, then `results/SYNTHESIS.md` **§5**.

Scratch in **`.temp/r113/`**.

---

## Why this one first

**Fourteen tasks are unreviewed.** ⚠ **`TASK_102` is the one that matters most,
because a published conclusion rests on it and nothing has attacked it.**

It probed **eight candidate catalogue rows and refused all eight**, and its
generalisation became **RECAP finding 37** and **§5 of the synthesis**:

> **This benchmark can price a safety property IF AND ONLY IF some rung emits it
> as a compare-and-branch and another rung omits it.**

⚠⚠ **That claim is why this project STOPPED BUILDING PATTERNS.** It is the stated
reason the catalogue is "measured out", the reason the box says *do not start a
27th pattern*, and Result 4 of the document an outside reader will quote.
**If it is wrong, the project stopped early on a bad argument.**

## §A — attack finding 37 itself

1. **Re-run the kills that carry the most weight.** The strongest are: the three
   Rust rungs of the recursion candidate calling **the same ICF-merged symbol**
   (R2 = R3 = R4, one rung); `unchecked_div` **not existing at the pin**, so the
   only "unsafe lever" is an annotation; and the unaligned-load and
   double-fetch pairs being **the same program** under probe 2.
   ⚠⚠ **PROBE 2 HAS FOUR KNOWN DEFECTS AND THREE ARE FALSE-NEGATIVES ON THE KILL
   CRITERION** — including one found *in the fix for another*. **`TASK_102`'s
   kills were taken with the tooling as it stood then. Re-run the probe-2-based
   ones with `.temp/t104/probe2.py`**, which keeps `<SELF+0xNN>`. **If a pair it
   called identical is actually two rungs, a refused row comes back.**
2. ⚠ **Is the "iff" earned, or is it an "only if" wearing an "iff"?** The
   evidence is eight refusals — **all of the form *no boundary, so no row***.
   **That supports the ONLY-IF half.** ⚠ **What supports the IF half — that a
   compare-and-branch boundary is SUFFICIENT?** **If nothing does, the claim
   should be stated one-directionally, and that is a real correction to a
   published sentence.**
3. **Is the refusal set biased?** ⚠⚠ **`TASK_111` found that this project's
   correction reflex had produced a one-directional coverage bias nobody was
   watching for.** **Ask the same question here: were candidates that would have
   PASSED as likely to be proposed as ones that failed?** Four of the eight were
   the manager's, whose record on row proposals is **0 for 2 before this and 0
   for 4 within it.**

## §B — triage the rest of the debt, cheaply

**Do not review fourteen tasks.** **Rank them by what published text depends on
them, and say which two or three are worth a task each.** The candidates:

- **`TASK_100`** — the leak-detector correction (`p34`'s kill) and the **`p37`
  refusal-reason refutation**, which left that row *"REFUSED-REASON-REFUTED,
  needs re-triage"* and **nobody has re-triaged it.**
- **`TASK_107`** — three results that changed how the project measures
  (the dep-info union, `MIRIFLAGS` presence costing 4.6×, the env-content pin).
- **`TASK_111`/`112`** — the synthesis review and its landing. ⚠ **Reviewing a
  review has diminishing returns; say if you think it is not worth it.**
- **`088/090/091/092/095/097/106/109/110`** — older, mostly pattern-local.

⚠ **`p37` is the live loose end in the catalogue** and it is cheap to state
precisely: its refusal reason is refuted, its verdict was never re-established,
and `SYNTHESIS.md` §5 counts it among *"15 rows refused, each on a
measurement"*. **Is that count honest with `p37` in it?**

---

## Constraints

- **`.temp/r113/` only. No `/tmp`.** Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `results/`, `synthesis/`, `harness/`,
  `pilot/` or any `patterns/*/` file.** You are a reviewer.
- **You may run `harness/measure.py --check-stale` and read anything. Do not run
  `check.py`, `build.py` or `measure.py` otherwise** — the tree is green.
- ⚠ **Every probe needs an arm that must fire.** The list at the end of
  `.memory/03-measurement.md` holds **six live entries numbered 1–7** (entry 5 is
  retracted). ⚠ **Do not quote its ordinal — doing so is itself a documented
  failure, committed five times by the manager after writing the rule against
  it.**
- Verus via `./verus_run.py` only, single-file mode. Do not bump the pin.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_113_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 414.** ⚠ **`TASK_112` returned it and its
own closing line says 409, which is the value it was LAUNCHED from — the count
lives in the newest task file's closing paragraph and this is now that file.**

**The session that produced the last two patterns ran 299 → 414, and the manager
was the subject of the largest findings in it:** a claim landed in `.memory/` and
refuted within hours; a **true** `.memory/` sentence struck on an unreviewed
mechanism; a control asserted vacuous that had fired; an inverted sign copied
from a report's prose while its own table was right; *"replace the regex with
dep-info"* closing a hole for the wrong compiler; and an arithmetic correction
an engineer refused as selective, shipping something better.

The calls I am least sure of:

1. ⚠⚠ **That finding 37 is right at all.** It is the reason this project stopped
   building, and it has never been attacked. **§A.2 is the specific way I think
   it is overstated — an "only if" written as an "iff".**
2. **That reviewing `TASK_102` beats reviewing `TASK_107`.** `107` changed the
   instrument; `102` changed the *plan*. ⚠ **I chose the plan. Argue if the
   instrument matters more.**
3. **That the debt is worth clearing at all rather than declaring the project
   done.** ⚠ **Fourteen unreviewed tasks is either a real liability or an
   accounting artefact of a fast session. If most of them are pattern-local and
   already superseded by later work, SAY SO** — *"the debt is smaller than it
   looks and here is the subset that matters"* is a perfectly good answer and
   would let the project close.

Carry **414** forward, incremented by what you find.
