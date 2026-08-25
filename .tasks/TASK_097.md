# TASK_097 — `_TWIN_BANNED` is the real blocker. Probe it, and fix the `_verus` hole.

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
**`.memory/02-bench-rules.md`'s decision block** (*"`_scan_unsafe_sites` STAYS AS
IT IS"*) and its `_verus` section — both newly landed and **reviewed** — then
`.tasks/TASK_096_REVIEW_REPORT.md` **MAJOR 3, MAJOR 2 and clean negative CN-5**,
then `.memory/06-catalogue.md`'s `p35` row.

Scratch in **`.temp/t97/`** — free, I checked.

⚠ **Both halves edit `harness/check.py`, so they stale every gate record and are
batched into ONE sweep.** Budget ~45 min for it and do it **once, last**.

---

## The situation, so you know what turns on this

**The catalogue is measured out: 48 rows = 24 built + 14 refused + 10
remaining, and `p23` is the only live build candidate.** `p35` — **type
confusion, the only bug class absent from the built tree** — is the one row that
would add something new.

`TASK_096` proposed unblocking it by narrowing `_scan_unsafe_sites`.
**`TASK_096_REVIEW` demonstrated that narrowing is UNSOUND** (a
`#[verifier::external]` fn nested in a verified body: Verus says `2 verified, 0
errors`, the narrowed rule admits it, **the binary reads out of bounds**), and
**the manager has decided the rule stays.** That decision is landed and is not
yours to revisit.

⚠⚠ **But the review named a DIFFERENT blocker, and it is the one that actually
fires — MAJOR 3.** `p35`'s problem is **not** only that a verified `unsafe` is
refused. It is that **the gate's own twin rule leaves no legal spelling**:

- `_TWIN_BANNED` forbids the `unsafe` keyword **in a twin**.
- A pattern whose *operation* is `unsafe` has **no safe spelling** to put there
  — `unsafe { v.i }` has no safe equivalent in Rust at all (`error[E0133]`).
- So the twin must be **justified away**, which is `n_twins == 0` → **hard
  FAIL**.

✅ **The reviewer EXECUTED that limb** (drove `check_trusted_twins` on a
synthetic pdir) rather than reading it: **`p35` has no legal configuration.**

**That is a defect in the twin rule, not a policy question about verified
`unsafe`** — and if it can be fixed, `p35` ships the **comply** way, with the
union read inside a counted `external_body` and **no soundness loosening at
all.**

---

## §A — the `_TWIN_BANNED` probe. THIS IS THE DELIVERABLE.

**Read `_TWIN_BANNED` and `check_trusted_twins` and answer, with runs:**

1. ⚠ **What is the twin FOR?** `.memory/06-catalogue.md`'s T009 entry says the
   verified twin was adjudicated *"worth keeping"* on the ground that **Miri
   never opens `verus.rs`**, so the twin is the only check on a too-weak trusted
   `requires`. **Restate that purpose in your own words before proposing
   anything**, because the fix must preserve it.
2. **Why does `_TWIN_BANNED` forbid `unsafe`?** Find the commit and the reason.
   ⚠ **My guess, and it is a guess: the ban exists so a twin cannot re-introduce
   the very operation it is supposed to be an independent check on.** If that is
   right, then a twin for `p35` is not obviously safe just because the pattern
   needs one — **say so if that is what you find.**
3. ⚠⚠ **IS THERE A LEGAL `p35` UNDER A REPAIRED TWIN RULE?** Build the smallest
   real thing that answers it: a union-read pattern with the `unsafe { v.i }`
   inside an `external_body` accessor, a twin that checks the accessor's
   `requires` is **load-bearing**, and the gate run to prove it. **If the twin
   cannot be written without `unsafe`, say what it would have to contain and why
   that is or is not acceptable.**
4. **If the answer is no — say no.** ⚠ **That closes the catalogue at 24 built
   patterns plus an optional `p23`, and that is a FINE OUTCOME.** Four rows have
   been refused this week and every refusal was the right call. **Do not invent a
   fix to keep a row alive.**

⚠ **Do not touch `_scan_unsafe_sites`.** The decision is landed.

---

## §B — fix the `_verus` return-code hole

✅ **Manager-verified**: `check.py::_verus` regex-matches
`(\d+) verified, (\d+) errors` out of `stdout + stderr` and **never reads
`r.returncode`**, so a file Verus verifies but `rustc` rejects reads as clean.
On `TASK_096`'s real gate run **the twin oracle certified uncompilable source.**

**The fix the review specified, and it is the fix I want:**

> flag `rc != 0` **only when the summary parsed AND `errors == 0`.**

⚠⚠ **A BARE RETURNCODE CHECK IS WRONG AND WOULD BE WORSE THAN THE HOLE.**
**11 call sites, not 12; 6 expect success, not 4** (`_verify_function` and
`_probe_selftest` were omitted from the first count) — **and 5 are mutants that
MUST exit non-zero.** Bolting a returncode check onto those turns the whole
mutant battery green for the wrong reason, which is **the tautology trap, and
this project has now hit it four times.**

- **Count the sites yourself.** The review says 11/6/5; ⚠ **the first count said
  12/4 and was wrong**, so do not trust either number — derive it.
- **Two more rc-blind readers exist** — `check.py::check_verus_contract` (inline)
  and `harness/limbs.py::verus` — ✅ **both backstopped by
  `build.py::build_verus --compile`**, so they are **smaller**, not bigger.
  **Decide whether they are worth touching and say why.**
- ⚠⚠ **Do NOT edit `harness/build.py`** — measurement-hashed; an edit costs a
  full 43-minute re-measure of every record.

**The acceptance test must run source → published number in ONE command**, and
must have an arm that **FAILS**. `.temp/t96/a7_source_to_published.py` is the
model — it moves 8 lines of `results/synthesis.md` including a `PASS → FAIL`.
⚠ **A test with no failing arm is the thing this project keeps catching itself
building.**

---

## §C — the sweep

Full **24-pattern** `check.py`, then `synthesis/licence.py --emit
synthesis/licence.json` **BEFORE** `synthesis/synthesize.py` — ⚠ **mandatory
order or 24 `LICENCE STALE` verdicts publish** — then
`harness/measure.py --check-stale`.

⚠ **`--check-stale` covers BOTH record families** — it globs `results/*.json`
**and** `results/gate/p*.json`, which is why it reports **48 records** against 24
patterns. (RECAP said `results/gate/` had no stale check; **that was false** and
is corrected.)

⚠⚠ **DO NOT EDIT ANYTHING UNDER `harness/` OR `patterns/` ONCE THE SWEEP HAS
STARTED.** `TASK_096` edited `check.py` between p08 and p09 and went **8
STALE**. Finish your edits, then sweep.

**Expect 23 `PASS` + 1 `PASS-WITH-BLOCKED-ROWS`, 0 failures.** **If anything
turns red, STOP AND REPORT** rather than editing 24 `spec.md` files.

---

## §D — small, and only if §A and §B are done

- `patterns/p09-bitset/NOTES.md` now says *"re-cited by FUNCTION **with the line
  as a hint**"* — the sweep deleted the hints and left the sentence describing
  them; and its recorded `contract_sha256` still reads `c391270c673f…` when the
  record says `0a37c0cd1418…` (moved by `9f8fa9d`). ⚠ **`RECAP.md` carries the
  old digest too — report that one, do not fix it; `RECAP.md` is manager-only.**
- `patterns/p12-strcat-fixed/NOTES.md` — a rewrite deleted an opening paren and
  left the closer.
- `patterns/p06-rotate/NOTES.md` cites `check_verus_contract` with
  `vparse.by_name`; it **never calls `by_name`**.
- ⚠ `patterns/p09-bitset/spec.md` says `check.py::exec_code` *"does NOT blank a
  `spec fn` BODY"*. **The claim is false today** — `exec_code` calls
  `_blank_ghost_items` (added TASK_069) and its own docstring lists `spec fn` /
  `proof fn` items. ⚠⚠ **It is INSIDE the hashed contract**, so fixing it moves
  `contract_sha256` again. **Disclose that explicitly if you do it.**

---

## Constraints

- **`.temp/t97/` only. No `/tmp`.** Keep the generator, delete the artefact.
  **Notes in `.temp/t97/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/` is manager-only.** Report durable facts; I land them after review.
- ⚠⚠ **Do not touch `harness/build.py` or `harness/asm.py`**, and remember every
  rung `.rs`, `c/kernel.{c,h}`, **`model.py` and `inputs/gen.py`** are
  measurement-hashed too — `measure.py::measurement_sources` globs them.
- Do not edit `pilot/`. Do not bump the Verus/vstd pin. Verus via
  `./verus_run.py` only (single-file mode; never `--cargo`).
- Cite `check.py` by **FUNCTION NAME, never a line number.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_097_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 286.** **The last three tasks carried it
from 270 to 286 — sixteen contradictions, and five of those were against
instructions I wrote into task files**, including one that would have shipped a
false declaration into a hashed contract block and one premise ("one rule blocks
two rows") that was simply wrong. The calls I am least sure of:

1. ⚠⚠ **That `_TWIN_BANNED` can be repaired at all without giving up what the
   twin is FOR.** I have not read the rule closely and I am guessing at its
   purpose in §A.2. **If the ban is load-bearing, say so and close the row.**
2. **That `p35` is worth this.** It is one pattern. **If §A's answer needs more
   than one session, that itself is the answer.**
3. **That the review's 11/6/5 site partition is right** — the first count was
   12/4 and wrong.

Carry **286** forward, incremented by what you find.
