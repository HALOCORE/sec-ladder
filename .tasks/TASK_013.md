# TASK_013 — p05, 2-D index flattening: the first vectorisable kernel

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, `.memory/01-ladder.md` (findings 3–5),
`.memory/02-bench-rules.md`, `.memory/04-verus.md`, `.memory/05-layout.md`
("Adding a pattern" **and** "The five demands steps 1–5 predate"), then
**`patterns/p17-http-range/` in full** — p17 is the template you clone. p05 reuses
its payload head, its window/Lemire driver, its `work_per_call = stride`
convention and its trusted accessor unchanged.

The template is mature. This spec is deliberately shorter than p16's and p17's;
where it is silent, **do what p17 did**.

## Why this pattern, and why out of catalogue order

Two reasons, and the first is the important one.

**1. Every fold this project has measured is serial.** p16 and p17 both fold with
`acc = acc*31 + b`, a dependence chain, and both recorded *"nothing vectorises in
any rung"* — so the safe-vs-unsafe gap has only ever been measured on a **scalar
loop on both sides**. p16 quantified what a bounds check costs when it blocks a
4× unroll: 2.25 of 4.25 Ir/byte. **Nobody has measured what it costs when it
blocks vectorisation**, which is a 16–32× wider lane, not a 4× one. If R2 loses
vector codegen here and R4 keeps it, the gap is not +4.25 Ir/byte, it is a
multiple — and that would be the first result in this project where safety is
**not** cheap by any framing, including R3's.

If instead R3 still lands at ~0 per byte on a vectorised loop, that is the
strongest possible version of the project's main finding, and it is the one a
numerical-computing reader will actually care about.

**2. It is the most realistic pattern in the catalogue.** `a[i*ncols + j]` is what
performance-critical C actually looks like. Result transfer is highest here.

## The bug class

CWE-129 / CWE-190: **declared dimensions trusted against the buffer that
actually arrived.** A header says the matrix is `nrow × ncol`; the code walks
`nrow*ncol` elements without checking they are there. This is *not* another
underflow — p16 (unsigned, forward) and p17 (signed, backward) have that covered.
Here the index is computed by **multiplication**, which is why the proof needs
nonlinear reasoning and why the check itself can overflow if written carelessly.

## Kernel contract

| Rung | Signature |
|---|---|
| R1 C, R1h | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

### Window layout and semantics

```
byte 0..2   nrow   u16 LE
byte 2..4   ncol   u16 LE
data_start = 4 ;  avail = len - 4
```

```
if len < 4:                       return 0
nrow, ncol from the header
if nrow == 0 || ncol == 0:        return 0

# >>> THE CHECK. R1 omits exactly this line and nothing else. <<<
if nrow * ncol > avail:           return 0       # computed in u64/size_t

acc = 0
for i in 0 .. nrow:
    row = 0
    for j in 0 .. ncol:
        row = row +64 buf[off + 4 + i*ncol + j]     # ASSOCIATIVE — vectorisable
    acc = acc *64 31 +64 row                        # serial across ROWS only
return acc *64 31 +64 (nrow *64 ncol)
```

**The inner loop is a plain sum on purpose, and this is the whole design.** It is
associative, so LLVM may vectorise it; the Horner step happens once per *row*, so
the result still depends on row order and cannot be re-associated into a flat
scan. That gives a vectorisable inner loop whose bound (`ncol`) comes from the
file but is loop-invariant *within* the inner loop — precisely the "optimiser can
see the loop" case, now with a 2-D index on top.

Load-bearing, do not "improve":

- **`i*ncol + j` stays as written.** Do not strength-reduce it to a running
  pointer in *any* rung — that deletes the pattern. If a rung's compiler does it,
  that is a finding to report, not a reason to change the source.
- **The check is `nrow * ncol > avail` in 64-bit.** Note in `NOTES.md` that the
  same check written in `int`/`u32` can overflow and wave the attack through, and
  say whether you built that variant as a measurement (do — it is one line, and
  it is the "hardened wrong" cell that makes R1h meaningful).
- **`nrow * ncol` is folded into the result**, so a rung that walks a different
  number of elements cannot produce the same checksum.
- Wrapping arithmetic throughout, as every prior pattern.

### Contract

```
requires:  off + len <= buf_len
ensures:   result == grid_fold(buf, off, len)
```

## What to measure that no prior pattern could

Beyond the standard table, **these are the deliverable**:

1. **`vector_regs` per cell, per rung, and the unroll/vector factor from the
   disassembly.** Which rungs vectorise? At what width? `.memory/01-ladder.md`
   records that "nothing vectorises in all 32 cells" was once written and was
   false — it was 23/32, with the 9 exceptions in `whole`-mode `main`. **Report
   kernel-only vector usage and say so explicitly.**
2. **If R2 fails to vectorise and R4 succeeds, decompose it.** Is it the bounds
   check, or the `i*ncol + j` multiply defeating LLVM's dependence analysis?
   The control that separates them: R2 with the inner loop rewritten as
   `for b in &buf[base .. base+ncol]` (reslice once per row, index-free inner
   loop). If that recovers vector codegen, the cost is the *per-element* check,
   not the 2-D index. p16's rolled-vs-rolled control is the model — **confirm by
   construction, do not infer from reading two disassemblies.**
3. **Ir per element AND ns per element**, swept. Use a **zero-residue lag pair**
   (`.memory/03-measurement.md`) — a non-zero-residue pair drifts visibly. Vector
   width means the residue modulus here may be 16 or 32, not p16's 4. **Sweep two
   full cycles; never sample two points.**
4. **No cycles/element unless you measure the clock interleaved with the wall
   reps** (`.memory/00-environment.md`). The dependent-chain probe read
   3.80–3.89 GHz in one session and 2.55–2.86 GHz in another on this shared box.
   ns is a measurement here; cycles is an inference.

## Inputs

| stem | shape | purpose |
|---|---|---|
| `small` | L1-resident window, `nrow×ncol` tiling it exactly | perf row |
| `large` | past L2, **different stride and different `ncol`** from `small` | perf row |
| `adversarial-dims` | **one window**, `nrow*ncol` far exceeding `avail` | R1 walks off → ASan must fire |
| `adversarial-ovf` | **one window**, `nrow`/`ncol` chosen so a 32-bit `nrow*ncol` wraps but the 64-bit product does not | the check-written-wrong cell; the correct check must reject |
| `adversarial-zero` | `nrow == 0` or `ncol == 0` | every rung returns 0 |

Adversarial rows are **exactly one window** (`n_blob == stride`), for the reason
p16 and p17 both record: `k` is pseudo-random, so with several windows the
malformed one is hit probabilistically and an overrun from a middle window stays
inside the allocation.

**Also, from p17 and non-obvious: window 0 must serve something.** A window
returning 0 pins `acc` at 0, and `k = (acc*nwin) >> 64` is then 0 for ever — the
driver's Lemire index has an absorbing state. Check your generated inputs
actually visit the windows you think they do.

**`ncol` choice matters for the science.** Give `small` and `large` different
`ncol` residues mod 16 and mod 32 (vector widths), not just mod 4.

Miri: cost is bytes folded per call at ~16 900 B/s against 180 s. Keep strides
well under ~700 KiB.

## Part 0 — two small carry-overs, first

1. **p16's `NOTES.md` may still assert 3.027–3.055 cycles/byte as measured.**
   `.memory/01-ladder.md` now carries the qualification (a TASK_007 wall time
   converted with a TASK_007_REVIEW clock, and this box's clock is set by other
   tenants). Bring p16's `NOTES.md` into line — the ns figures and the null result
   stand; only the cycles conversion is qualified. **Do not re-measure p16.**
2. **p16's `inputs/gen.py --sweep` blobs were never shipped** — the sweep evidence
   lives in `.temp/`. `inputs/*.bin` is gitignored, so this is only about `gen.py`
   being able to regenerate them. Confirm it can; fix it if it cannot.

## Done when

The p17 checklist, unchanged, plus items 1–4 of "What to measure". In particular:
complete green `check.py p05`; checksums against `model.py`; the adversarial table
per rung with `adversarial-dims` firing ASan on R1; the decomposition naming a
loop with **R3 quoted first**; two proof mutants failing the gate; the TCB tally;
the `#[cfg(slb_twin)]` twin with `verus.twin_obligations` **and its arithmetic
written out**; an `SLB-TRUSTED-ARGUMENT` block with labels (a)(b)(c) ≥200 chars;
and an explicit statement of whether the twin is idle again (it will be, if the
accessor is single-clause — say so; do not manufacture a multi-clause one).

**Budget: one session for R5.** A stalled proof reported with its exact Verus
error is the deliverable for that row, not a gap. Expect the nonlinear obligation
`i*ncol + j < nrow*ncol <= avail` to be the work; p17's driver lemmas and
`by (nonlinear_arith)` are the starting point, and `.memory/04-verus.md` warns
that vstd has no `isize::MAX` slice-length axiom.

## Constraints

No root; no `/tmp` (scratch `.temp/p05/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/` (report durable facts; the manager lands them); do not
touch `harness/` or `common/` — if p05 seems to need a change there, **stop and
report it**. Do not edit p01/p02/p17 sources; p16 only per Part 0.
Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`.

Notes to `.temp/p05/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Eleven agents
have now contradicted the manager's written instructions and all eleven were
right — the last three overturned headline claims and one proved two of my
deliverables mutually inconsistent. The least certain thing in this file is the
**prediction that the inner loop vectorises at all**; if it does not in *any*
rung, say so early, because then p05 measures nothing new and I would rather
change the kernel than publish a null I designed for.
