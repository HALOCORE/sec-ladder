# TASK_PHP_014 — adversarial review of `ph03`, the row every later row will copy

**Role:** research **reviewer**. Adversarial by design.
**Under review:** `patterns-php/ph03-uudecode-bound/` (all five rungs + R1h, its
`spec.md`, `model.py`, `controls/`, records) and
`.tasks-php/TASK_PHP_013_REPORT.md` — **plus the manager decisions in
`RECAP_PHP.md` F29–F32.**
**Report:** `.tasks-php/TASK_PHP_014_REPORT.md` — write the FILE.

> **A review that says "looks good" without having tried to break something is a
> failed review.** Rank `blocker` · `major` · `minor`, each with `file:line` and
> a concrete failure scenario. ⚠ **Name your clean negatives.**

Read `.tasks/PROTOCOL.md` (reviewer checklist), `.tasks-php/PROTOCOL_PHP.md`,
`PLAN_PHP.md` §3–§6, `patterns/p01-array-sum/` (the template `ph03` cloned —
**read, never edit**), and `../LearnVeri/PITFALLS.md` before touching Verus.

⚠⚠ **`RECAP_PHP.md` IS MANAGER-ONLY.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **`.web/` belongs to a CONCURRENT SESSION — never `git add -A`.**

**Bracket**: `harness/measure.py --check-stale` → `66/0` and
`harness-php/gate.py --tool measure --check-stale` → **`4/0`**, first and last.

---

## §0 WHY THIS REVIEW IS WORTH MORE THAN THE ROW

**`ph03` is the template for ninety more rows.** A defect in the row costs one
row; a defect in its *shape* — how the tier is declared, how the oracle is
built, how strong the Verus spec is, what `controls/` is for — is copied
ninety times before anyone notices. ⚠ **Weight your effort toward what will be
COPIED.**

## §1 PRIMARY TARGET — is R5's postcondition actually strong?

`ph03` reports **25 verified, 0 errors** with what the report calls a **"full
functional postcondition"**. ⚠⚠ **A Verus proof that verifies is worth nothing
if its `ensures` is weak, and "25/0" is exactly what a vacuous spec looks like
from outside.**

1. **Read `verus.rs`'s `ensures` and say, in one sentence each, what they
   actually constrain.** Does the postcondition pin the **decoded bytes**, or
   only the length? Only that no panic occurred? ⚠ **A spec that says "the
   output has length `total_len`" and nothing about content is memory-safety
   only, and the report's phrase would be an overclaim.**
2. **Mutate the implementation and confirm the proof FAILS.** Change a shift, a
   mask, an index — if `25/0` survives a wrong decoder, the spec does not
   describe the decoder. ⚠ **`controls/negatives.py` already emits one negative
   (`no2014`); build the ones it does not.**
3. **Is the spec's `requires` reachable?** A precondition no caller can satisfy
   makes any proof trivial. Check what `main.c` actually passes.
4. **`R4 ≡ R5 byte-identical at O3`** — verify it yourself, and say whether that
   is evidence of anything or an artefact of both compiling the same MIR.

## §2 The headline — attack all three proofs of "the 2004 fix is incomplete"

This is the programme's strongest claim and it is **unreviewed**.

- **3a, the count** (144 of 12 600) comes from an *instrumented interpreter*
  written for the task, not from the kernel. ⚠ **Is the interpreter faithful to
  `c/kernel_hardened.c`?** Diff their control flow. An interpreter that models
  the C loosely would produce this number by accident.
- **3b, ASan.** ⚠ The report itself discloses that the source is `malloc`ed at
  **exactly** `src_len`, and that a stack array or over-allocated buffer would
  give the over-read slack to land in and report nothing. **Is the ASan result
  therefore a property of the harness rather than of PHP?** Say plainly whether
  a real PHP zval string would have that slack.
- **3c, Verus.** ⚠ **Confirm `negatives.py --emit no2014` deletes ONLY the 2014
  check** and nothing else. If it removes anything the 2004 fix also had, the
  failure proves less than claimed.
- **The 2014 commit** (`1e2818b14376`, bug #67252): fetch it
  (`https://github.com/php/php-src/commit/<sha>.patch`) and confirm it is what
  the report says.

## §3 Fidelity — the `verbatim` claim, and the `-lm` substitution

⚠ **`ph03` declares tier `verbatim` and ships a MACRO SUBSTITUTION for
`floor()`.** `TASK_PHP_012` M4 found **12 of 41** declared tiers wrong, and
since the overlap floor was demoted to a report, **the declared tier is the only
surviving fidelity signal.**

- **Does the substitution belong in the deletion ledger, and is it there?**
- ⚠ **Is `verbatim` still honest with it?** `PLAN_PHP.md` §4's tiers are the
  manager's design and this is the first row to test them. **If a substitution
  that changes no behaviour still breaks `verbatim`, say so — the tier
  definition is what needs fixing, not the row.**
- **Diff `c/kernel.c` against the tarball lines** (`SOURCES.md`'s recipe,
  pinned tarball only) and report every difference, not a summary.

## §4 The oracle, the controls, and what gets copied

- ⚠ **`model.py` is the independent reference.** Is it independent, or was it
  written from `kernel.c`? A model derived from the kernel cannot catch the
  kernel being wrong.
- **`controls/` — do the must-fire controls fire, and do the must-NOT-fire ones
  stay silent?** Run them.
- ⚠ **The report says the row folds an `(allocs, frees)` tally into the `u64`
  checksum, and that this technique "does not carry to an allocator-dependent
  row".** **Is it right for THIS row?** A checksum that mixes the defect with
  the answer can hide a wrong answer behind a right tally.
- **`spec.md`'s pins**: `TASK_PHP_013` §7.1 asked which of the PAT-derived pins
  are meaningless for an extracted kernel. **Check the answer** — a pin filled
  with an invented value is worse than an absent one.

## §5 The measurement

`R2−R4 = +18.9 Ir/group`, `R3−R4 = +6.1`, and the ⭐ claim that **the 2004 check
costs −3.0 `Ir`/line on gcc** because `setae` + two `cmove`s disappear.
**Spot-check the disassembly yourself** — the instruction-count story is the
kind of claim that is right in shape and wrong in attribution.
⚠ **And confirm no `phNN` figure is quoted against any `pNN` figure anywhere in
the row or the report** (open item 9).

## §6 Rules

- **No `git add` / `git commit`.** Read-only git is fine.
- Scratch under `.temp/php14/`. **Never `/tmp`.** ⚠ `.temp/php12/` and
  `.temp/php13/` hold this row's own harnesses — **re-run them unmodified
  before writing anything new.**
- ⚠ **You may PLANT to test a check, but restore in a `finally:` and verify by
  bytes.** The manager will not commit while you run.
- ⚠ **`env -u LD_PRELOAD`** for hand-run sanitizer probes; grep
  `AddressSanitizer`, not `ASan`.
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — exact PID via
  `/proc/<pid>/cmdline`. ⚠ **The last engineer's own `pgrep -f` matched its
  poller shells and reported a gate still running that had finished.**
- Everything claimed must have been **RUN**, output pasted.

## §7 The calls I am least sure of

1. ⚠⚠ **That R5's spec is as strong as the report says** (§1). *"Full
   functional postcondition"* is the report's phrase, not a measurement, and I
   accepted it. **If it is memory-safety-only, F29's Verus limb still stands —
   the `i < v@.len()` failure is real — but the row's headline sentence
   overstates what was proved, and ninety rows would copy the overstatement.**
2. ⚠ **That `verbatim` survives the `-lm` substitution** (§3). Mine to decide
   and I decided it by keeping the workaround. **The tier is now the only
   fidelity signal, so getting this wrong is expensive.**
3. ⚠ **That no harness edit is right for `check_sanitizers_hardened`** (F31).
   I ruled the incomplete-fix evidence can live in `controls/`. **If a reader of
   the gate record would reasonably conclude the fix is complete, my "standing
   limitation, recorded" is not enough.**

---

**Running count: launched from 61.** `TASK_PHP_013` refuted the catalogue's
*"the write fires first"* (it is a property of the source buffer's **slack**,
not the code) and found **four pipeline defects nine reviews could not, because
none of them had a row**. ⚠ It also disclosed against itself: the chain took
**13 commands, not 6**, `contract_sha256` moved twice, and no
`controls/spellings.py` exists — **so no ratio in that report is *the* cost of
safety.** **Reconciliation is the manager's job.**
