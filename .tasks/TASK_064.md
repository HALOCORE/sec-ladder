# TASK_064 — p47, constant-time compare: the security property the whole ladder is blind to

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then **`.memory/06-catalogue.md`'s p47 entry — it carries a feasibility argument
and two hazards, both settled before this task was written** — then
`.memory/03-measurement.md` (**the `div` pricing at `:434`, the `rep`-string
counting at `:411`, "name the routine" at `:551`, the two `Ir` conventions, the
INLINE-MODE rule, the DOMAIN rule**), `.memory/01-ladder.md` (**finding 18 (p10)
and finding 19 (p27)** — both had an unsearched R4 side, two patterns running),
then **`patterns/p27-handle-table/` and `patterns/p10-fir-stencil/`** as
templates.

## Why this pattern is different from every other one here

**The adversary is the OPTIMISER, and the security property is one Verus cannot
state at all.** Every pattern so far asks "what does safety cost?". p47 asks a
question the ladder is structurally unable to answer, and **that is the result**:

- **R5 can prove the comparison CORRECT and has no vocabulary for timing**, so
  the top rung of this project's ladder **certifies a leaking kernel**. That
  mirrors p17 (*provably memory-safe and still leaking*) one level up, and it is
  a **clean negative this project can state precisely** rather than a stall.
- **Safe Rust's idiomatic equality is the LEAKING one.** `a == b` on slices
  lowers to a `memcmp`-shaped early exit. So the safe language hands you the
  insecure default, and no amount of memory safety helps. ⚠ **Verify that
  lowering before building on it** — it is the load-bearing claim and I have not
  measured it.

## The measurement, which is unusually good here — and the two ways it lies

**This box has no hardware counters** (`perf_event_paranoid = 3`) and the
wall-clock floor is wide enough that two published `ns` rows are withdrawn. **p47
does not need either.**

> **`Ir` under callgrind IS the side channel** — deterministic, noise-free, and
> a function of the input. Build inputs whose **first mismatch is at position
> `k`** and sweep `k`. The finding is *"`Ir(k)` is CONSTANT in `k`"* versus
> *"`Ir(k)` is LINEAR in `k`"*, measured to the instruction. **No other pattern
> here has a metric that is literally the harm.**

**And the other half is static**: *did the optimiser put the branch back?*
`harness/asm.py` answers that exactly, at zero measurement cost.

⚠ **Two ways `Ir` lies here, both already measured on this project:**

1. **Callgrind counts a `rep`-string instruction ONCE PER REPETITION**
   (`:411`) and **prices a hardware `div` at 1** (`:434`). A `memcmp` lowered to
   `repe cmpsb` and one lowered to a SIMD loop are **not comparable in this
   metric**. **Name the routine beside every rate** (`:551`) and check the
   lowering before reading any slope. This is the single most likely way to
   publish a wrong p47 number.
2. **A text pin binds the SOURCE, not the object** — p13's finding. The
   constant-time rung must survive the optimiser **in the shipped build**, not in
   a probe. **Disassemble the shipped cell and show there is no early exit**;
   `forbidden` entries cannot establish it.

## §0 — settle the bug class, the wire format, and the SWEEP first

`.memory/06-catalogue.md` calls it *"timing side channel — compiler may
reintroduce a branch"*. **Treat that as a prior**; four patterns overturned their
row and two upheld it. §0's deliverable is a written decision in `NOTES.md` §0:
the bug, the wire format, what each cell does, and **why the rejected candidates
were rejected**.

⚠ **§0 has a second deliverable, and it is the sweep design.** `Ir(k)` is the
whole pattern, so the input set is not an afterthought:

- inputs must vary **`k` (first-mismatch position)** across the full length,
  including `k = 0` and "equal" (no mismatch);
- ⚠ **`k` is one structural parameter and there is almost certainly a second** —
  length, alignment, or whether the mismatching byte differs in one bit or many.
  p10 went **3 → 4 → 6** parameters and p18 needed two where the manager named
  one. **If you can find two that vary independently, ADDITIVITY EXTRAPOLATION is
  available** — fit where they never co-occur, predict where both fire. It is the
  only out-of-sample test on this project that has ever been able to fail.
- **A law owes its DOMAIN, and the domain is usually a MISSING COLUMN.**

## The rungs, and where I think this collapses

My proposal — **argue with it, and measure before adopting it:**

| rung | spelling | expected |
|---|---|---|
| R1 | `memcmp(secret, input, n) == 0` | **leaks**: `Ir` linear in `k` |
| R1h | the volatile-accumulate idiom, `acc \|= a[i] ^ b[i]` | constant |
| R2 | `a == b` on slices | **leaks** — the safe default |
| R3 | `a.iter().zip(b).fold(0, \|acc, (x, y)\| acc \| (x ^ y)) == 0` | constant, **if the optimiser lets it** |
| R4 | the same with `get_unchecked` | constant |
| R5 | R4 plus a proof of **correctness only** | identical machine code; **silent on the leak** |

**Where it collapses, and settle each in `§0` before building six rungs:**

- **If LLVM short-circuits the fold**, R3 leaks too and the pattern becomes *"you
  cannot write constant-time code in safe Rust at `-O3` without `black_box` or a
  crate"* — **which is a stronger result, not a weaker one.** Do not treat it as
  a failure; measure it and say so.
- **If R2's `==` does NOT lower to an early exit**, the "safe default leaks"
  claim dies and the pattern is smaller. **Check first.**
- **If R1 and R2 lower to the same libc routine**, their comparison is a library
  result, not a language one (`:551`, and p13's whole lesson).

## What p47 must have regardless

- **Record the `slb-contract` sha256 in `NOTES.md` before building any cell**, and
  ⚠ **read the shared named-spelling paragraph from a DONOR `spec.md` if you write
  a contract generator — never embed it** (`.memory/05-layout.md`: p27's
  generator silently deleted it, and only the new gate check caught that).
- **Search the R4 side.** *"Degenerate as far as this task searched"* has been
  **false on two consecutive patterns**, and both times it flattered the safe
  rung. Publish the fixed-R4 bound **and** the span, "cheapest found", input named.
- **NAME THE INLINE MODE at every figure** — p10 fitted both and its regressors
  **swapped roles**.
- **Attribute per-iteration `Ir` mnemonic by mnemonic**, and **check the panic
  pads** before calling anything a safety cost.
- **No `ns` claim without a layout population**; port `controls/clayout.py`.
- **Adversarial rows per rung with distinct harms in distinct columns.** ⚠ Here
  the "harm" is a *timing difference*, not a crash — so say what an adversarial
  row even means for this pattern. That is a genuine design question and I do
  not know the answer.
- **Two proof mutants that FAIL.**

## Verus

Budget **one session**. **The expected result is that R5 proves correctness and
cannot express the leak — that is the deliverable, not a failure.** State it
precisely: what *can* be proved, what cannot, and why (Verus has no cost model;
the property is about the *trace*, not the value). Use `~/tools/verus/vstd/` —
**not** `../LearnVeri/_VERUS_DOC_/vstd/`, an older snapshot missing specs that
exist. `global size_of usize == 8;` may be needed for `usize` arithmetic
(`.memory/04-verus.md`). **TCB: one number plus the U-license / V-gap / infra
classification, and prose saying how the rung reaches unchecked memory.**

## Done when

The p27 checklist, plus §0's two decisions. Complete green `check.py p47`;
checksums against an independent `model.py`; the `idiom` block written **before**
the cells, **carrying the shared paragraph**; sweep with its fitter under
`controls/`; both R3 numbers; two failing proof mutants; TCB equal to the gate's
own `tcb_items`; `measure.py --check-stale` clean. **Paste actual output.**

## Constraints

No root; no `/tmp` (scratch `.temp/p47/`); **no `git add`/`git commit`**; do not
edit `pilot/`, `.memory/`, `harness/`, `common/`, or any existing pattern. **If
p47 seems to need a `harness/` change, STOP and report it.** Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**. Measurements in
the FOREGROUND, interleaved by cell, per-PID scratch paths. **You are the only
agent running.** `harness/check.py p47` only. Delete binaries and blobs once
green; **keep every generator.**

Notes to `.temp/p47/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** The running
count is **118**, and the last four tasks contributed eleven of them — including
one where I wrote *"zeroing the table is not optional"* and it was dead code,
refuted by 144 comparisons with zero mismatches.

**What I am least sure of is the entire rung table above.** I have not verified
that R2's `==` lowers to an early exit, nor that R3's fold survives `-O3`, nor
that R1 and R2 use different routines. **Measure those three before building
anything on them.** If the fold does not survive, say so plainly — *"constant-time
code is not expressible in safe Rust at `-O3`"* is a **better** result than the
one I specced, and it is the kind of finding this project exists to produce.
