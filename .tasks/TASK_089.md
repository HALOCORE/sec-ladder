# TASK_089 — build `p46`, bignum limb add/mul

**Role: research engineer.** Read `.tasks/PROTOCOL.md` first (**Definition of
done**, and **rule 6** — record the `slb-contract` sha256 *before building any
cell*), then this file, then `.tasks/TASK_086_REPORT.md`'s **p46 block**, then
`.tasks/TASK_026.md` §0. `patterns/p19-state-machine/` is the freshest template
and `patterns/p01-array-sum/` is the canonical one.

Scratch in `.temp/t89/` — free, I checked. ⚠ Another agent is running, confined
to `.temp/t90/`; you own `patterns/`, `harness/`, `results/`, `synthesis/`.

---

## 1. What is already measured — and how much of it you may trust

`TASK_086` ranked `p46` **second** of 11. All four probes pass:

- **Boundary:** R3-vs-R4 on the schoolbook inner step — **three** bounds checks
  per MAC (`b[j]`, `out[i+j]` read, `out[i+j]` write).
- **Machine code (linked):** `k46_checked` 296 B `a73eda77…` vs `k46_unchecked`
  126 B `daca171e…`.
- **Cost:** N=64 limbs → 4096 MAC steps/call. `62400.00` vs `41720.00` →
  **+5.05 `Ir` per MAC step, +49.6%**, whole-program marginal, `-O3`,
  **inline mode `isolated`**. Slope in `n·m`.
- **vstd:** `unchecked_mul` / `carrying_add` / `widening_mul` → **0 hits**.
  Ordinary `external_body` route, twin writable. **Not `p15`/`p35`'s obstacle.**
- ✅ **R5 already RUN: `7 verified, 0 errors`** (`.temp/t86/v46_carry.rs`).
  `lemma_mac_fits` (`by (nonlinear_arith)` + `by (compute)`) plus `mac` with a
  **value-level** postcondition `lo + hi·2⁶⁴ == a·b + c + carry`.

⚠⚠ **AND HERE IS THE THING TO GET RIGHT, BECAUSE IT JUST COST `p19` A
CORRECTION TASK: THOSE ARE PROBE NUMBERS, AND ONLY THE SLOPE TRANSFERS.**
`.memory/03-measurement.md`, landed this task: p19 shipped two laws from a
5-length probe and **both intercepts were wrong** — once for the residue class
it never varied, and once for **a fixed per-program offset of `+2` and `+6`,
exact at all ten in-class points, because the probe was a different binary.**
⚠ **That second mode is invisible to a residue-covering band.** **Carry the
`+5.05` slope forward as a PRIOR and re-fit everything from your shipped
cells.** Do not publish any intercept a probe gave you.

---

## 2. The novelty question, stated as a question

`TASK_086` reports p46's `mac` postcondition as **value-level** —
`lo + hi·2⁶⁴ == a·b + c + carry` — and says it is **"stronger than any `ensures`
currently in the tree, all of which are bounds facts."**

⚠⚠ **DO NOT SHIP THAT SENTENCE UNTIL YOU HAVE COUNTED IT.** *"The first
termination proof in the project"* was a manager sentence that was **false** and
shipped into **eight places, two inside `contract_sha256`** — a review and a
re-gate to remove. **Grep every `patterns/*/verus.rs` for `ensures` clauses and
classify them yourself**, then state what you found. p27 ships a functional
postcondition; p09's `_msonly` has one; p13 and p14 have value clauses. **If the
claim survives counting, it is a real result and worth the headline. If it does
not, say so and ship the weaker true sentence.**

## 3. The kill risk, named

**The full product postcondition needs a nested-loop invariant over partial
sums.** The probe proved **the MAC step and the inner loop's length invariant —
not the product.** If §0 promises functional correctness of the multiply, it may
not close in one session.

⚠ **You choose the contract, and you may choose the weaker one.** A kernel whose
`ensures` is the *step* plus memory safety is a legitimate pattern; a kernel
promising the whole bignum product is a better one **if it closes**. **Decide in
§0, before building cells, and say which and why.** ⚠ **If you promise the
product and it stalls, do NOT reach for `assume`/`admit`/`external_body` to
close it — weaken the contract and disclose, or REFUSE the row.**

Two traps the probe already hit, so you do not pay for them again: **both casts
need `#[verifier::truncate]`**, and **the `nat`-cast spelling of the u128 hi/lo
split FAILS `by (bit_vector)` while the `u128` + `requires` spelling passes.**

## 4. The bug class

Limb-bound / carry → `index >= len` on `out[i+j]`; **shares with `p05`** (the
`i*n+j` flattened index). **Twelve BUILT patterns carry `index >= len`; p19 made
thirteen; p46 would be the fourteenth.** ⚠ **Name it up front, the way p19 and
p36 do, in `spec.md`, `README.md` and `NOTES.md`.** A fourteenth is not
disqualifying — but the row must say what is *not* `p05`'s. **The value-level
proof obligation is the candidate; §2 decides whether that claim survives.**

## 5. Rules that govern the numbers

- ⚠ **Name the INLINE MODE at every figure.** p10 fitted both and the regressors
  swapped.
- ⚠⚠ **SEARCH BOTH SIDES, and count the levers on each.** The trap has caught
  **five** patterns (p10, p27, p38, p22 at 510×, and p36 in mirror image).
  **p19 did it right: 3 levers per side, all degenerate, and it said so.**
- ⚠ **Never publish a "minimum"** — write *"cheapest found"* and **name the
  input**.
- ⚠ **Do not publish a pair interval.** Both this project ever published were
  built from R4s that are not rungs.
- ⚠ **Extract kernel bytes from the LINKED binary** — a relocated field is zero
  in a `.o`, so two kernels differing only in a call target md5 identically
  there (`TASK_086` #238, manager-verified).
- ⚠ **A law owes its DOMAIN, and check the RESIDUE CLASS of every parameter your
  bands hold constant.** p46 has **two** (`n` and `m`); p38's additivity failure
  was 100% attributable to three missing columns, none of them the one named.
- ⚠ **Ship a sweep band** so every law is re-derivable from committed inputs and
  a hashed generator. **Then actually re-fit from it before publishing** — p19
  shipped a band and published a law it had never re-fitted against.

## 6. Constraints

- `.temp/t89/` only. **No `/tmp`.** Keep the generator, delete the artefact.
- **Notes in `.temp/t89/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- `.memory/` is manager-only. Durable facts go in your report.
- ⚠ **Do not touch `harness/build.py` or `harness/asm.py`** — measurement-hashed;
  an edit costs a full 43-minute re-measure of 17 records.
- Do not edit `pilot/`. Do not bump the Verus/vstd pin.
- `timeout <N> <cmd>` on anything long. Never `pkill`/`killall`.
- ⚠ **Cite `check.py` by FUNCTION NAME, never `check.py:NNNN`.**
- ⚠ **If you edit `c/kernel.c` or `c/kernel.h` after measuring — a COMMENT
  included — the measurement record goes STALE.** There is no comment-only
  escape. Get the C comments right before you measure.

---

⚠ **PROTOCOL rule 2's running count is 253.** **Every agent that has contradicted
the manager with a measurement has been right — 253 times, and the last four were
`TASK_088` correcting this manager's own task file.** My least-sure calls, by
name: **(a)** that the value-level `ensures` claim in §2 survives a count —
**I have not counted it and neither had the probe**; **(b)** that `+5.05 Ir` per
MAC step reproduces on built rungs at all, given §1's warning; and **(c)** that
the product postcondition is out of reach in one session — **the probe guessed
that, it did not measure it.** Contradict any of them plainly. Carry **253**
forward incremented by what you find.
