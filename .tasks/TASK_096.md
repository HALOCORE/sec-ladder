# TASK_096 — the batched gate sweep, headlined by the ONE RULE THAT BLOCKS TWO PATTERNS

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
`RECAP.md`'s START HERE box and its **"Owed" 0** and **"Owed" 30**, then
`.memory/02-bench-rules.md`'s threat model (top section), then
`.tasks/TASK_084_REVIEW_REPORT.md` (majors 2–3 are yours).

Scratch in **`.temp/t96/`** — free, I checked.

⚠ **This task stales every gate record, so everything in it is batched into ONE
sweep.** That is the whole reason it has been deferred five times. **Budget ~45
minutes for the sweep and do it once, last.**

---

## Why gate work now, when PROTOCOL rule 5 says prefer a pattern

**Because this IS the pattern work.** The catalogue is measured out:

> **48 rows = 24 BUILT + 14 REFUSED + 10 remaining.** Of the ten, **`p23` is the
> only live build candidate and it would be the tree's FIFTEENTH `index >= len`.**
> `p24` needs a new reason, `p26` needs an input band, `p20`/`p21`/`p25` are
> deferred with measured reasons, `p40`/`p41`/`p42` are measured-dead pending
> review.

**And `p35` — the only bug class ABSENT from the built tree, type confusion — is
blocked by exactly one gate rule, together with `p15`.** Fixing it is worth two
patterns. Nothing else on the board is worth one.

---

## §A — ⚠⚠ THE HEADLINE: is `check.py::_scan_unsafe_sites` RIGHT?

**The rule:** every `unsafe` token in a pinned Verus source must sit **inside an
`external_body` item**. So a row whose R4 operation Verus can *discharge* cannot
put the discharged call in a **verified** fn — it must be moved *into* the
counted TCB behind an unwritable twin.

**Two rows die on it and they die for opposite reasons**, which is what makes it
worth deciding rather than patching:

- **`p15`** — `str::from_utf8_unchecked` **has** a vstd spec, and a verified
  UTF-8 validator **closes at the pin**: `ensures res == valid_utf8(b@)`
  bidirectional, **`5 verified, 0 errors`, ZERO trusted items**, end-to-end call
  site `8/0`. The proof discharges the precondition — and the rule then forces
  the call into the TCB anyway.
- **`p35`** — the Rust `union` is **not in vstd at all** (318 `union` hits are
  every one of them `Set::union`), yet **Verus supports it NATIVELY**: the
  correct-variant obligation is **first class in the type system**
  (`1 verified, 1 errors` → `requires v is i` → **`2 verified, 0 errors`**). The
  read is still `unsafe { v.i }` **inside a verified fn**, so the rule fires with
  no vstd spec involved at all.

⚠⚠ **THE MANAGER HAS NOT DECIDED THIS, DELIBERATELY (PROTOCOL rule 3): the gate
is the manager's design and the manager must not clear it.** Your job is to
**investigate and RECOMMEND, with demonstrations**. A different agent will
review your recommendation, and I will decide after that.

**What I want measured, not argued:**

1. ⚠ **The evidence that `p35` is blocked is A CODE READ, not an executed gate.**
   `.temp/t86/scan_unsafe_probe.py` drives HEAD's `_scan_unsafe_sites` against a
   candidate source and prints `host=NONE -> rep.fail(tcb-unsafe)`. **Run the
   real gate on a real minimal pattern** and show the actual verdict. If the
   block does not reproduce end-to-end, **that is the finding and §A is over.**
2. **What is the rule actually FOR?** Read its own docstring and
   `.memory/02-bench-rules.md`'s threat model — *honest mistake, not malicious
   author*. **Ask what honest mistake it prevents**, and whether a narrower rule
   prevents the same mistake while admitting a Verus-discharged `unsafe`.
3. ⚠⚠ **THE HARD QUESTION, and I want it answered before any code changes: if a
   verified `unsafe` is admitted, WHAT COUNTS AS THE TCB?** The TCB column is a
   published number and `.memory/04-verus.md` closed its definition at
   TASK_055_REVIEW — **one number = project-local trusted items, prose beside
   it, and a second "vstd relied upon" column REFUTED with a 402-site census and
   marked "must not be reinstated."** ⚠ **Do not reinstate it.** A verified
   `unsafe` has **zero** trusted items by that definition, which is either the
   right answer or an obvious hole — **say which, and defend it.**
4. **Whichever way you land, produce the ACCEPTANCE TEST first.** ⚠⚠ **ONE
   COMMAND FROM SOURCE TO PUBLISHED NUMBER.** `TASK_084`'s limb 3 was a good test
   that still missed, because it was **verified in two halves and the join was
   never run**; `TASK_084_REVIEW` then reproduced the failure on three routes.
   **Ask which single command carries a change from the source all the way to the
   number a reader quotes — and if there isn't one, that is the test you are
   missing.**

✅ **A recommendation of "leave it alone, and here is the attack that made me
sure" is a complete and welcome answer.** Two rows dying is a cost; a gate hole
is a bigger one.

---

## §B — "Owed" 0's SIXTH ROUTE, which is still open

The five body-less trusted forms are closed. The sixth is: **a USED vstd
`assume_specification` reaching `check_miri`'s *"no trusted item ⇒ Miri not
required"* branch.**

⚠ **The manager got this wrong once already and RECAP records it** — I claimed
p19 was *"the only pattern that calls a vstd exec trusted function from its
kernel"*; it was refuted three ways, and one of them is the correction that
matters here: **the literal sixth route has been live in 22 of 23 patterns all
along**, via `bytes.len()` and `bytes.as_slice()`.

**So the question is not "does it exist" but "does it MATTER":** find a pattern
that reaches `check_miri`'s no-trusted-item branch **while depending on a vstd
`assume_specification` that could be wrong**, and show what ships green.
**If nothing does, say so — a clean negative closes the item.**

---

## §C — the smaller batched items

- **`TASK_084_REVIEW` major 2** — `synthesis/synthesize.py`'s §3 prose
  overclaims. (The `22` → computed `_n_named` fix landed; the *overclaim* did
  not.)
- **`TASK_084_REVIEW` major 3** — `check_miri`'s `if not why_required` branch.
- **"Owed" 30** — `check.py::check_marginal_ir`'s **docstring is too strong about
  the ±7 bistable term**, and `p46` is the **fourth** pattern to hit it. It says
  the term is `whole`-mode only and that `isolated` is *"not merely small, it is
  exactly invariant"*. **Weaken it to what four patterns actually show.**
- ⚠ **The 39 `check.py:<line>` citations across 21 files.** The convention is
  `.memory/02-bench-rules.md`'s: **name the FUNCTION, give NO LINE NUMBER AT
  ALL.** The "line as a hint" compromise was tried at TASK_066 and **retracted at
  TASK_071 after every hint rotted inside one session.**
  ⚠⚠ **TWO OF THE 39 ARE INSIDE `patterns/p09-bitset/spec.md`'s FENCED BLOCK**,
  so fixing them **moves `contract_sha256`**. That is legal and expected — but
  **disclose it explicitly in the report**, because a moved contract hash on a
  pattern nobody was building is exactly the kind of thing a reviewer must be
  told rather than discover.

---

## §D — the sweep, and the order is mandatory

Full **24-pattern** sweep, then `synthesis/licence.py --emit
synthesis/licence.json` **BEFORE** `synthesis/synthesize.py`. ⚠ **That order is
mandatory or 24 `LICENCE STALE` verdicts publish.** Then
`harness/measure.py --check-stale`.

⚠ **Expect `PASS` on all 24** (p01 is `PASS-WITH-BLOCKED-ROWS`, a real 180 s
Miri timeout, documented). **If anything turns red, STOP AND REPORT rather than
editing 24 `spec.md` files.**

⚠ **`check_stale` footnote, measured at TASK_088:** the `GEN-ONLY` verdict
**cannot fire on a GATE record**, because gate records carry no `input_sha256`
and they also hash `NOTES.md`/`README.md`/`spec.md`. A `check.py` re-run clears
it.

---

## Constraints

- **`.temp/t96/` only. No `/tmp`.** Keep the generator, delete the artefact.
  **Notes in `.temp/t96/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/` is manager-only.** Report durable facts; I land them after review.
- ⚠⚠ **Do not touch `harness/build.py` or `harness/asm.py`** — measurement-hashed;
  an edit costs a full 43-minute re-measure of every record, and `check.py` costs
  only the gate re-run you are already paying for.
- ⚠ **Every rung `.rs` and `c/kernel.{c,h}` is ALSO measurement-hashed.** There is
  **no cheap doc fix in a rung source**. If §C sends you into one, batch it and
  say what the re-measure cost.
- Do not edit `pilot/`. Do not bump the Verus/vstd pin. Verus via
  `./verus_run.py` only (single-file mode; `--cargo` is not concurrency-safe).
- `timeout <N> <cmd>`; never `pkill`/`killall`.
- ⚠ **Cite `check.py` by FUNCTION NAME, never `check.py:NNNN`** — §C exists
  because the manager did not.

---

⚠ **PROTOCOL rule 2's running count is 274.** **Every agent that has contradicted
me with a measurement has been right — 274 times. The last eight came in three
consecutive tasks, and two of those were against instructions I had written into
the task file**, including one that would have shipped a false declaration into a
hashed contract block. The calls I am least sure of:

1. ⚠⚠ **That `_scan_unsafe_sites` is wrong at all** (§A). I am asking because two
   rows die on it, **which is a motive, not an argument** — and PROTOCOL rule 3
   says I must not be the one who clears it. **If the rule is right, the honest
   outcome is that `p15` and `p35` stay refused and the catalogue is finished.
   Say that if it is what you find.**
2. **That §B's sixth route matters at all** now that the literal form is known to
   be live in 22 of 23 patterns.
3. **That the two `p09` citations are worth a `contract_sha256` move.** If you
   judge not, leave them and say why.

Carry **274** forward, incremented by what you find.
