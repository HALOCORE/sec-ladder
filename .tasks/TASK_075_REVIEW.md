# TASK_075_REVIEW — the synthesis, and a tool that grades its own homework

**Role:** research reviewer. **Adversarial by design.** You do **not** fix; you
report. A review that says "looks good" without having tried to break something
is a failed review.

**Read first:** `.tasks/PROTOCOL.md` (roles, reviewer checklist, severity), then
`.tasks/TASK_075.md`, then **`results/synthesis.md` in full** and
`synthesis/README.md`, then `.memory/03-measurement.md` (**the kernel-exclusive
column section and its TASK_073 widening**) and `.memory/01-ladder.md`
**findings 9 (p11), 14, 18 (p10) and 23 (p36)**.

**Nothing here is gate-checked.** `synthesis/` is outside every hashed glob (⚠
**verify that** — `check.py::main` globs `harness/*.py`, `common/*.py`,
`common/layout/*.py`, `common/driver.*`, `<pdir>/controls/*.py`), so **no stage
of `check.py` validates one number in `results/synthesis.md`.** That is by
design and it is also why this review matters more than usual: **the gate is not
behind you here.**

⚠ **The engineer refuted the argument that scheduled its own task, the manager's
ordering premise, and the p48 report's prescription.** Those are dead. **Attack
the replacements.**

## A0 — the tool grades its own homework, and its score is the headline

`synthesis/licence.py` decides, from the **disassembly**, whether a rung pair's
outward-dispatched work is equal, and `results/synthesis.md` prints that verdict
beside every difference. The engineer scored it against
`synthesis/outward_ir.py`'s **measured** callee costs, 176 pair/blob rows:

```
{'hit': 156, 'false LICENSED': 10, 'false alarm': 0, 'abstain': 10}
```

> ⚠⚠ **BOTH SIDES OF THIS SCORE WERE BUILT BY THE SAME AGENT IN THE SAME
> SESSION, AND THE ORACLE IS THE THING THE TOOL IS SUPPOSED TO REPLACE.**
> PROTOCOL rule 3's shape. **Attack it three ways:**
> - **Is `outward_ir.py` a sound oracle?** It attributes callee `Ir` from
>   callgrind's caller→callee edges. **Does it double-count a callee reached from
>   two call sites, or miss one reached transitively?** Build a case where you
>   know the answer independently.
> - ⚠ **"0 false alarms" is the claim that licenses the whole table.** A false
>   alarm is a row marked `NOT-LIC` that is really fine — harmless. A **false
>   `LICENSED`** is a row the table says you may quote and you may not, and there
>   are **10**. The engineer attributes all 10 to *cost behind an equal name*
>   (glibc `memset` alignment ±7.00, and gcc's 2-instruction PLT thunk).
>   **Verify that attribution exhausts them** — if even one of the 10 is a
>   different mechanism, the class is open and the count is a floor.
> - **The 10 abstains**: `UNDEC` on p27 and p36. **Is abstention the right
>   answer there, or is it a gap that could be closed?**

## A1 — the reproducibility result, which inverts the prescription

**Measured: kernel-exclusive `Ir`/call moved in 0 of 348 (pattern, input, cell)
triples across two independent callgrind sweeps; the outward column moved in
6** — all ±7.00, all glibc `memset` on p03's and p04's `safe_tuned`/`verus`
cells, **sign unstable**. So on the new column, `R5 − R4` reads **−7.00** on p03
and p04: *"the proof costs −7 instructions"* between **byte-identical kernels**.

> ✅ **If this holds it is the most useful thing in the delivery**, because it
> says the callee column is an **addition** and never a **replacement**, and it
> arrived unasked. **So test it hard:**
> - **The two sweeps differ only in the `--callgrind-out-file=` path**, which is
>   part of *valgrind's* argv. **Is that a big enough perturbation to call it a
>   reproducibility test, or is it a single lucky knob?** ⚠ **Vary something
>   else** — environment size, cwd depth, `--callgrind-out-file` held constant
>   across two runs — and see whether 0/348 survives or whether the kernel column
>   moves too.
> - **6 of 348 is a rate, not a mechanism.** `.memory/03-measurement.md` predicts
>   p03's `[0u64; 64]` lowering to a `memset` whose path length moves with
>   alignment. **Confirm the mechanism**, and check whether any *other* pattern
>   is exposed to it and merely did not fire in two runs.

## A2 — the attack on the scheduling argument. Is it complete?

The claim: of the five patterns the p48 report named, **four move by exactly
0.00** and only p11 moves — and **p11's defect was already published**, in
boilerplate present in **22 of 22** `results/tables/*.md` (*"p11's `safe_tuned`
reads 30% cheaper than unsafe here and 21% dearer on the marginal"*), measured
30.2% / 21.3%.

> **That is a strong refutation and it makes the manager's scheduling decision
> partly wrong. Check it is not too strong.**
> - **`0.00` on four patterns is a suspiciously clean result.** Verify at least
>   two independently, from the records, without `outward_ir.py`.
> - ⚠ **The engineer says `.memory/03-measurement.md`'s p13 paragraph is the
>   source of the error** — it groups `R3/R4/R5` together, so the two figures
>   p13's rule actually moved are `gcc-vs-clang` and **`R2 − R4`**, not `R3−R4`.
>   **Is that reading of p13 right?** It is about to be written into `.memory/`.
> - **The tree-wide census says `gcc-clang` is the pair in trouble: 7 `NOT-LIC`
>   + 1 `UNDEC` of 22.** ⚠ **That is a much bigger claim than the one it
>   replaces** — it says a third of the project's C-vs-C comparisons are
>   unlicensed. **Spot-check three of the seven.**

## A3 — four published patterns are said to be wrong, and none is in scope for a fix

The delivery reports, as adjacent findings: **p27's `R3−R4` and `R2−R4`
understated by 120.33 / 130.95** (its `unsafe` dispatches through `call *%r12`);
**p27's `gcc-clang` reverses** on `small` (−25.02 → +15.00); **p09's gcc column
carries `__popcountdi2` at 378.00 / 2625.00 `Ir` per call**; **p47's `R2−R4`
−166/−194 → −77.73/−28.00** (`bcmp`); and **`asm.is_bulk_symbol('bcmp')` is
`False`**, so p47's and p09's records misdescribe their routine lists.

> **Each is a claim about a REVIEWED, SHIPPED pattern.** ⚠ **Verify them
> individually before the manager schedules corrections on four patterns** — that
> is four gate re-runs and possibly a re-measure. **And say for each whether the
> pattern's own `NOTES.md` already discloses it**, as p11's and p47's partly do;
> a defect the pattern already names is a citation fix, not a correction.

## A4 — what the table says about ITSELF

- ⚠ **`R5 − R4 = 0.00` on all 44 rows is scoped as a TAUTOLOGY** — both `exact`
  (21 patterns) and `norel` (p36) force `Ir` equality, so the row is a gate check
  restated, not a measurement. ✅ **The engineer says so.** **Confirm the scoping
  is right**, and check nothing else in the file presents an entailment as a
  finding.
- **`whole` mode: 334 of 350 `None`, and all 16 survivors are gcc
  `kernel.part.0`.** Verify — it is stronger than RECAP's "302 of 318" and
  replaces it.
- ⚠ **`synthesize.py::SEARCH` is a HAND-MAINTAINED table with 8 entries; 14
  patterns print `undeclared`.** The engineer says the lever count cannot be
  derived from committed data (only 8 of 22 expose a `--list`) **and predicts it
  will rot like every constant this project has caught.** **Is there a derivable
  proxy?** If not, say so — a hand table that rots inside a generated file is
  worse than an empty column.
- **The search objection**: `R3−R4` partly measures search effort — p13
  −177/−1054 → **+44/+77, a sign flip**. **Is the correction sound, or does it
  difference two differently-scoped searches?**

## Clean negatives are wanted

PROTOCOL rule 6. Recent reviews returned 32, 35, 38, 48 and 54 named attacks.
**List every attack you ran with its outcome.**

## Constraints

No root; no `/tmp` (scratch **`.temp/p75rev/`** — ⚠ **`ls` any scratch path
before writing to it; `.temp/pNN/` collides between patterns and tasks**; read
`.temp/p75/` but do not modify it); **no `git add`/`git commit`**; do not edit
`pilot/`, `.memory/`, `harness/`, `common/`, **any** file under `patterns/`, or
**anything under `synthesis/`**. You may re-run `synthesis/*.py` — ⚠ **they
rewrite `results/synthesis.md` and the two sidecar `.json`s, so restore with
`git checkout --` and say that you did.** Re-running `harness/check.py` is
allowed on the same terms. clang `~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc`,
valgrind `~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — **none
but gcc on PATH**. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no
`nohup … &`**; **no self-matching `pgrep` wait-loops.** **You are the only agent
running.**

**Write `.tasks/TASK_075_REVIEW_REPORT.md` before you finish** (rule 10), then
return the same content in the report format. Rank findings `blocker` · `major` ·
`minor`, with **file:function** (⚠ **not `file:line`** — that convention was
retracted at TASK_071 after every hint rotted inside one session) and a concrete
failure scenario. **Do not pad.**

**If a premise here is wrong, say so with the measurement.** ⚠ **Running count
174** — 170, plus this delivery's four: the p48 prescription's *"the order is a
dependency"* (**it is not** — the licence settles 19 of 22 rows in ~2 s and the
synthesis exists with no harness change), the scheduling argument's decisive
half (**four of five patterns move by 0.00**), `.memory/03-measurement.md`'s p13
paragraph grouping R3/R4/R5 so that the wrong pair inherited the warning, and
RECAP "Owed" 6's follow-up about p11's `bulk_calls`.

**What I am least sure of, by name: A0 and A1, and they are connected.** The
licence's *"0 false alarms"* is the property that licenses every figure in the
file, and it was scored against an oracle **the same agent wrote in the same
session to replace with the licence**. If the oracle is wrong in the direction
that flatters the licence, the whole table inherits it. And A1's
reproducibility result — which is the delivery's best finding — rests on
**one perturbation knob**. **Both could be right. If either is not, the artefact
should not be quoted from until it is fixed.**
