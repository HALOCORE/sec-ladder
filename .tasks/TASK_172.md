# TASK_172 — the masked gate failure, and two free repairs

**Role: research engineer.** You are the only agent running.

⚠⚠⚠ **THREE ITEMS. TWO COST NOTHING. THE THIRD IS A SOUNDNESS QUESTION AND YOU
MUST NOT SPEND ANYTHING ON IT UNTIL YOU HAVE ANSWERED IT.**

`TASK_171` verified that `harness/asm.py`'s `main` needle mis-resolves on 33
cells and that the mis-resolution **masks a stage-3a failure** on
`p01 safe_tuned -O0 isolated`. ⚠⚠ **A gate that is green on a stage that should
be failing is a certification problem, not a hygiene item** — which is why this
was NOT retired as a limitation. **But the fix is a full re-measure, and the
proposed repair moves 266 windows, so the question comes before the price.**

Read first: `.tasks/TASK_171_REPORT.md` **item 6 in full**; `RECAP.md` **finding
67(e)** and the START HERE box's open list; `.memory/03-measurement.md` on the
`whole` column; `PROTOCOL.md` **rule 6**'s cost table.

---

## A. ⚠⚠⚠ THE MASKED STAGE-3a FAILURE — ANSWER THE QUESTION BEFORE PRICING THE FIX

**What is established** (`TASK_171`, verified): `p01 safe_tuned -O0 isolated`'s
**real** kernel is **41 instructions with 0 back edges and 0 bulk calls**, while
the `Iterator::fold` window `asm.py` picks instead has **4 back edges** — and
`check.py`'s stage 3a fails exactly the *zero back edges* condition. **So the
stage would fail on the true window and passes on the wrong one.**

⚠⚠⚠ **THE QUESTION THIS TASK EXISTS TO ANSWER, AND IT IS NOT *"how do we fix
`asm.py`"*: IS THE MASKED FAILURE A REAL DEFECT IN `p01`, OR IS STAGE 3a ASKING
THE WRONG QUESTION AT `-O0`?**

**The case that it is the STAGE:** at `-O0` a safe-tuned rung's `fold` body lives
in a `core::iter` symbol, **not in `kernel`** — which is the documented reason
`check_marginal_ir` exists at all and is measured as a *slope* precisely because
it is **symbol-independent** (`.memory/03-measurement.md`). **On that reading a
`kernel` symbol with no back edge at `-O0` is CORRECT and expected, and stage
3a's structural test is a `-O3` test being run at `-O0`.**

**The case that it is `p01`:** stage 3a exists to catch a collapsed loop, and
*"the loop moved to a callee"* and *"the loop is gone"* look identical to it.

✅ **Settle it with a run, and settle it for the WHOLE TREE, not for `p01`:**
- **How many `(pattern, cell, opt, mode)` windows would newly FAIL stage 3a** if
  the needle resolved correctly? ⚠ **`TASK_171` says the mis-resolution is
  `-O0`-only and covers 33 cells — confirm both, and say which patterns.**
- **For each newly-failing window, is the loop in a callee?** ✅ **The instrument
  exists and needs no build: `synthesis/outward_ir.json` names the callee and
  counts the calls.** ⚠ **It carries `-O3` only — say so if that blocks you, and
  say what would not.**
- ⚠ **Does `check_marginal_ir` already pass on those cells?** If the dynamic
  anti-collapse check is green where the structural one would fail, **that is
  the answer**: the structural test is the one that is wrong, and the pattern is
  fine.

**Then, and only then, the disposition — and you may choose it:**
- **If stage 3a is asking the wrong question at `-O0`**, the repair is in
  `check.py` (**gate-only, one sweep, no re-measure**) plus a `.memory/` note
  the manager lands. ✅ **That is the cheap and likely outcome.**
- **If the masked failure is real**, ⚠⚠ **STOP AND REPORT WITH THE PRICE. Do
  NOT start a re-measure.** `asm.py` is measurement-hashed; the repair moves
  **266 windows**; and `.memory/03-measurement.md` already records that the
  `whole` column is not a null. **The manager decides.**
- ⚠ **Either way, report what the 266 moved windows WOULD change** — is any
  *published* figure among them? **The four Results are all `-O3 isolated`, so
  the honest answer may be *"none"*, and that is worth establishing rather than
  assuming.**

⚠⚠ **DO NOT EDIT `harness/asm.py` IN THIS TASK.** Even the "obvious"
exact-match-first repair. **Report it; the manager decides.**

## B. THE `§` MARKER'S CENSUS IS A WHITELIST AND SAYS IT IS A CENSUS

`results/synthesis.md` describes `regime_crossing`'s marked set as **DERIVED**.
⚠⚠ **`TASK_171`: `BULK_REGIME` is THREE HARDCODED KEYS, two of them bare glibc
addresses**, `__memchr_avx2`/`__strlen_avx2` are **unclassified while
contributing asymmetrically on six published `gcc-clang` rows**, and the
marker's stated reason — *"while the other side does not call it at all"* — is
**true by construction**, because gcc cells spell libc callees as client PLT
addresses (`p08 c-gcc` carries the same `memmove` at 39.0 against clang's 39.4,
under a bare-address key).

✅ **The two marked rows are right. Fix the DESCRIPTION and, if you can, the
classifier.** ⚠ **`synthesis/` is in neither digest — no gate, no re-measure.**
- **Say plainly that `BULK_REGIME` is a whitelist**, and print what is in it.
- ⚠ **Widen it if the widening is derivable rather than guessed** — the
  `Ir`/byte signature (`≈1.00` byte-wise, `≈0.10` vector) is a property of the
  measurement and does not need a name. **If a signature-based rule marks rows
  the name-based one misses, that is the fix; if it marks rows that are NOT
  regime crossings, say so and keep the whitelist with an honest caption.**
- ⚠⚠ **And fix the marker's REASON string** — *"the other side does not call it
  at all"* must not be printed where it is an artefact of symbol naming.
- ⚠ **`TASK_169`'s `p27 gcc-clang` is a KNOWN row this census structurally
  cannot see** (both spellings are inline, so there is no callee edge).
  **Either the marker covers inline bulk instructions or it says it does not.**

## C. TWO FALSE COUNTS IN A GENERATED FILE, ONE PARAGRAPH APART

`results/synthesis.md`:
- *"every entry cited to a reviewed artefact — except one, `p06`"* is **false on
  three**: `p01`, `p03` and `p08` cite `RECAP "Owed"`, i.e. **the open
  backlog**, and `n_found` is a residual so they land in the *"SEARCH RESULT"*
  bucket.
- *"Seven of the fourteen"* **lists six**, omitting `p18` and `p38` — the two
  most explicit — and it is a **hardcoded string in a generated file, one
  paragraph below the same defect's own fix.**

✅ **Derive both counts instead of hardcoding them.** ⚠ **That is the actual
repair: a hand-typed count under a computed table is this document's
most-repeated defect** (`RECAP` records it as *"typed under a computed
list"* at least three times). **If a count cannot be derived, print the list and
let the reader count.**

## ⚠ NOT in this task

- **`harness/asm.py`** — investigate only.
- **Any re-measure.** If item A concludes one is needed, **stop and report**.
- **`p05/NOTES.md` §1a's correction** (it says `verus::main` lacks two `xmm`
  instructions and it carries them). ⚠ **Gate-hashed, so it needs a sweep — and
  if item A ends in a `check.py` repair it can ride that sweep. Report it as a
  candidate; do not land it alone.**
- **`.memory/`, `RECAP.md`, `results/SYNTHESIS.md`** — manager-owned.

## Then

1. **Item A answered**, with its disposition and its price.
2. **B and C landed** (`synthesis/`-only), `synthesize.py` re-run.
3. **Only if item A's disposition is a `check.py` repair**: land it with a
   must-fire arm you have seen fail, add `p05/NOTES.md` if it rides along, then
   **one 33-pattern sweep**.
4. `--check-stale` · `composition.py --check` · `temp_citations.py` ·
   `licence.py --emit synthesis/licence.json` · `synthesize.py`.
5. ⚠⚠ **CHECK EACH SCRIPT'S OWN EXIT STATUS.**

## Rules

- `.temp/t172/` for scratch. ⚠ **Do not modify earlier `.temp/t*/` or
  `.temp/mgr*/`**; you may read them. **No `git add`/`git commit`.**
- ⚠⚠ **DO NOT LEAVE A `pgrep -f` WAITER RUNNING.** Use `wait <pid>` or a
  `.done` sentinel.
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log.**
  ⚠ **Expected: `30 PASS + 3 PASS-WITH-BLOCKED-ROWS`, 0 failures, `blocked`
  `p01` 1 / `p35` 3 / `p42` 1.**
- **Keep the generator, delete the artefact.** A string-substituting generator
  **MUST ASSERT ITS SUBSTITUTION COUNT.**
- Report to `.tasks/TASK_172_REPORT.md`. **Write the file before citing it.**

**PROTOCOL rule 2 running count: launched from 948**; `TASK_170` and `TASK_171`
each refuted the manager repeatedly and the manager has not reconciled the
figure — ⚠ **say what you refute and let the manager reconcile.**

⚠⚠ **The call to attack is item A's framing. I have written that the likely
answer is *"stage 3a is asking a `-O3` question at `-O0`"* — and I have run
NOTHING. If the masked failure is real, the cheap disposition I have made
sound likely is the wrong one, and saying so is worth more than confirming
me.**
