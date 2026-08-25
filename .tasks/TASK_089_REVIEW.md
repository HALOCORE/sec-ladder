# TASK_089_REVIEW — attack `p46`, and attack the blast radius it opened

**Role: research reviewer.** Adversarial by design. **A review that says "looks
good" without having tried to break something is a failed review.** You report;
you do not fix. Read `.tasks/PROTOCOL.md` (Reviewer checklist, Severity), then
`.tasks/TASK_089.md`, `.tasks/TASK_089_REPORT.md`, then
`patterns/p46-bignum-mac/NOTES.md` and `spec.md`.

Scratch in `.temp/r89/`. **You may run `harness/check.py p46`.** Do not run a
full sweep. `--check-stale` is read-only and fine. **No other agent is running.**
p46 is committed at `591fcec`; the tree is clean. **If you plant, snapshot by
bytes, restore in a `finally:`, and verify `git status --porcelain` empty.**

---

## What landed

The 24th pattern. `PASS`, Verus **21/0** (twin 24), `identity` O3 `exact`, 24
records / 0 failures / 0 STALE. ⚠ **All three of the manager's named least-sure
calls were contradicted with measurements, and the engineer also caught two of
its OWN pre-build probes being wrong.** Both are disclosed with mechanisms.

✅ **Already manager-verified, do not re-derive:** 24 records and their verdicts;
`controls/census.py --ensures` (159 conjuncts, 151 equalities);
`controls/sweep_ir.py --check` (exit 0).

---

## ⚠⚠ A1 — THE HEADLINE IS THE FLATTERING-DIRECTION TRAP'S SIXTH APPEARANCE

**`safe_naive` < `safe_tuned` < `unsafe`, and the per-MAC safety tax is
`0.00000`.** That is *"safe Rust beats unsafe"* — the sentence that was **wrong
in the flattering direction on p10, p27, p38 and p22 (510×)**, and whose mirror
image caught **p36**.

**The engineer's defence is specific and you should test each limb:**
3 levers per side, **both spans degenerate** (R4 3 flat, R3 2 flat); and a
**rolled-vs-rolled control giving `R2 − R4 = +2.00·n·m` exactly**, i.e. the
advantage is **100 % an unroll decision**.

**Attack it:**
- **Is the lever search comparable?** Count them yourself. p36's mirror-image
  failure was *"searched R4 properly and left R3 with ONE lever."*
- **Is `0.00000` per-MAC real, or hoisted?** The claim is that LLVM proves
  `i+j < 96` and **deletes all three bounds checks**. **Disassemble and confirm
  the safe MAC loop has no conditional branch but its own `jne`.** If a check
  survives anywhere — the epilogue, the outer loop, a reslice — the `0.00000`
  is scoped and must say so.
- **Does the rolled-vs-rolled control isolate what it claims?** `-unroll-count=1`
  on *both* sides is the p16/p05 recipe; verify it was applied symmetrically and
  that the two rolled kernels are otherwise mnemonic-identical.

### ⚠⚠ A2 — THE BLAST RADIUS THE ENGINEER OPENED AND EXPLICITLY DID NOT CHECK

p46's probe was wrong **in sign** because it wrapped its dimensions in
**`black_box`**, withholding the `u8` range on `n`,`m` so LLVM could not prove
`i+j < 96`. **The shipped kernel proves it and deletes the checks.** The
engineer's own words: *"this finding is p46's own and has NOT been checked
against any other pattern's probe. It may not generalise — and every row in
`TASK_086`'s queue was measured the same way."*

⚠ **This is the highest-value hour of your session, because it governs FOUR
UNBUILT ROWS.** `TASK_086`'s `cost.rs` is at `.temp/t86/` (⚠ `ls` it first).
**Does it use `black_box`, and does it hide a range fact for `p23`, `p24`, `p26`
or `p35`?** ⚠ **Note `p28`'s probe (TASK_091) is the ONE that validated itself
differently — each `Ir`/victim equals the static loop-body count to three
decimals — so it is the control, not a suspect.** **Say which rows are affected
and which are not.**

## A3 — the two findings that reach past p46

- **The harm is silent in 6 of 8 plain C cells, and the mechanism is claimed to
  be the ORDER OF TWO AUTOMATIC ARRAYS** — `bl[256]` exactly 96 limbs above
  `out[96]`, so the overflow lands **inside the other scratch**, canary
  untouched, `-fstack-protector-strong` no help; clang `-O0` reverses them and
  SIGSEGVs. **Re-derive the layout yourself.** ⚠ **This is a claim that a
  DEFENCE THE BOX ENABLES BY DEFAULT does not fire — check it carefully.**
- **`r4_mutreslice` beats the shipped R4 and every safe spelling by 697…2597
  `Ir`/call but is not a rung**, because the pinned vstd cannot specify a mutable
  sub-slice: frame provable, **value not**. **Re-run `controls/census.py
  --mutsub`** and confirm the four probes say what the report says. ⚠ **If the
  value IS specifiable by some spelling the engineer missed, the cheapest
  spelling becomes admissible and p46's R4 side moves.**

## A4 — the discrepancy the manager already found

The report says gcc's `R1h − R1` has **"two"** unexplained `+3.00` exceptions,
both `m=48`. **The committed checker prints `+3.00 on 1 … exception(s) at
['24,48']` — ONE.** Minor, but **prose and tool disagree; find which is right.**

## A5 — the ordinary checklist, with what bites here named

- **Constant folding / leaked constants**; is the data genuinely from the file?
- **Are the six rungs semantically equivalent?** `model.py::_fold_bigint` is
  claimed to close the mathematical-product gap **by testing** — ⚠ **is it
  independent, or does it re-encode the kernel's own schoolbook loop?**
- **Is R2 a fair naive port?** It is the **fastest** rung here, which is unusual
  enough to check.
- **TCB tally: recount it.** Are the `ensures` conjuncts load-bearing and the
  `requires` non-tautological?
- ⚠ **`by (bit_vector)` and `by (compute)` are claimed to be the FIRST in the
  tree** (`0 file(s)` before p46). **Verify that grep**, including
  ghost/spec positions, not just executable ones.
- ⚠ **Extract kernel bytes from the LINKED binary.**
- **Rule 6:** the pre-build hash is the **only** evidence on a new pattern.
  Confirm the one disclosed edit changed no `required`/`forbidden`/`identity`.

---

## What I want back

PROTOCOL's report format, severity-ranked, each finding with a **concrete
failure scenario**. **3 real blockers beat 20 nitpicks.** ⚠ **Rule 6: give me
your CLEAN NEGATIVES BY NAME.**

## Constraints

- `.temp/r89/` only. No `/tmp`. Keep the generator, delete the artefact.
- **Notes in `.temp/r89/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- `.memory/` is manager-only. **You review, you do not fix.**
- ⚠ **Do not touch `harness/build.py` or `harness/asm.py`** — measurement-hashed.
- ⚠ **Any edit to `c/kernel.c`/`kernel.h`, a comment included, stales the
  measurement record.**
- Never `pkill`/`killall`. Do not bump the pin. Do not edit `pilot/`.
- ⚠ **Cite `check.py` by FUNCTION NAME, never `check.py:NNNN`.**

---

⚠ **PROTOCOL rule 2's running count is 257.** **Every agent that has contradicted
the manager with a measurement has been right — 257 times.** ⚠ **My prediction
record on which Verus obligation stalls is 0 for 3** (`.memory/04-verus.md`), and
**three of my three named calls on this very pattern were wrong.** My least-sure
call here is **A2** — that the `black_box` artefact generalises to the other
queue rows — **and I have not run it.** **A1 is where I think p46 is most likely
to be wrong.** Carry **257** forward incremented by what you find.
