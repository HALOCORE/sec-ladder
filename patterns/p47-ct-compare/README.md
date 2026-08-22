# p47 — constant-time tag comparison

**The pattern where the ladder's top rung certifies a leaking kernel, and it is
not because the proof is weak.**

`spec.md` is the contract. `NOTES.md` has every measurement. This file is the
summary.

## What it is

A window declares `ntag` comparisons of `tlen`-byte tags; each comparison holds
a secret and an attacker-supplied candidate; the kernel folds the *verdict* of
each. The fold never sees a tag byte, so **two windows with the same verdict
sequence and different first-mismatch positions produce the same checksum in
every rung.**

| rung | comparison | leaks in `Ir`? |
|---|---|---|
| R1 `c-gcc` / `c-clang` | `memcmp(a, b, tlen) == 0` | **yes** |
| R1h `c-gcc-h` / `c-clang-h` | `d \|= a[i] ^ b[i]` over every byte | no |
| R2 `safe_naive` | `a == b` on two slices | **yes** |
| R3 `safe_tuned` | `iter().zip().fold(0u8, \|acc,(x,y)\| acc \| (x^y))` | no |
| R4 `unsafe` | the same accumulate with `get_unchecked` | no |
| R5 `verus` | R4 plus a proof of **correctness only** | no — **and the proof does not say why** |

⚠ **Read the "no" column as `Ir(k)` constant, which is a NECESSARY condition and
not a sufficient one** — `NOTES.md` §14 has the full scoping and it belongs
here too, because this file is the one that gets quoted. What p47 measures
exactly is that the instruction count does not depend on the secret. **Cache and
port pressure are unmeasured**, and there is no branch-misprediction column on
this box (`perf_event_paranoid = 3`). The other half of the usual constant-time
argument — the five "no" rungs are branchless in the tag loop and their
addresses are data-independent, every one reading all `2·tlen` bytes in order —
is **read off the disassembly** in `NOTES.md` §1a rather than assumed. Neither
half is a proof of constant *time* on real hardware.

**The safety column and the security column are uncorrelated**, and that is the
pattern: `{R1 safe, R1h safe, R2 safe, R3 safe, R4 unsafe+proved, R5
unsafe+proved}` against `{R1 leaks, R1h no, R2 leaks, R3 no, R4 no, R5 no}`.

## The result, in one table

35 blobs, `tlen = 256`, `ncmp = 4`, everything held constant except where the
first differing byte is. Whole-program marginal `Ir` per kernel call.

| rung | Ir @ k=0 | Ir @ k=255 | **spread over the whole band** |
|---|---:|---:|---:|
| `c-gcc` | 221.000 | 405.000 | **184.000** |
| `c-clang` | 197.000 | 381.000 | **184.000** |
| `safe_naive` | 324.000 | 508.000 | **184.000** |
| `c-gcc-h` | 694.000 | 694.000 | **0.000** |
| `c-clang-h` | 618.000 | 618.000 | **0.000** |
| `safe_tuned` | 700.000 | 700.000 | **0.000** |
| `unsafe` | 626.000 | 626.000 | **0.000** |
| `verus` | 625.000 | 625.000 | **0.000** |

`0.000` is exact, not "small", and the same table at `-O3 whole` gives the same
`184.000` and the same `0.000`. **`Ir` under callgrind is not a proxy for the
harm here — it *is* the harm**, and no other pattern in this project has a
metric that is. ⚠ In the direction that matters: a non-zero spread **is** a
leak, measured; a zero spread is the *necessary* condition above and not a
clean bill of health.

## Six things worth knowing

1. **The catalogue's bug class is overturned.** It predicted *"the compiler may
   reintroduce a branch"*. Five accumulate spellings × {gcc 13.3, clang 22.1} ×
   `-O1 -O2 -O3 -Os -Oz`, plus rustc at five opt levels, inlined into a caller
   that branches on the result and not — **not one grew a data-dependent exit**.
   TASK_064_REVIEW then ran a strictly larger search on the same claim —
   16 binaries, 7 C and 4 Rust spellings, under **LTO**, under **PGO trained
   100% on mismatch-at-byte-0**, under AVX2 and AVX-512, with
   `__builtin_expect` in three placements — and got
   `Ir(k=0) − Ir(k=n−1) = 0` **exactly**, per function, everywhere, against a
   detector that fires at **+18 448 Ir** on a leaking control. The adversary is
   the *idiom*, not the optimiser.
2. **`c-clang` and `safe_naive` call the same libc routine.** clang rewrites
   `memcmp(a,b,n) == 0` into `bcmp`, which is exactly what rustc emits for
   `a == b`. Their difference is a library result, not a language one.
3. **The leak is a 32-byte staircase, not a line**, and above 128 bytes not even
   a staircase — glibc's size-class dispatch makes some positions leak more than
   others. Per comparison, relative to `k < 32`: `+7 +14 +19 +40 +43 +46 +46`.
4. **Additivity extrapolation: 40 of 40 exact, in both inline modes.** Fit the
   `k` effect where no comparison matches and the `nmatch` effect where `k = 0`;
   predict where both fire. `max|resid| = 0.000000` on all eight rungs.
5. **`volatile` — the received hardening advice — costs 6.75× and buys
   nothing.** The plain accumulate is already exactly constant in `k`.
6. **The proved rung can be made to leak and still verify.** `m_leak`
   (generated **and built** by `controls/gen_controls.py --build`, run by
   `controls/proof_mutants.py`) puts the early exit back into `verus.rs`:
   **14 verified, 0 errors**, the same `ensures`, and `kernel`'s own obligation
   count **unchanged at 3** — the two extra are a ghost lemma and its
   bit-vector query. The compiled binary then leaks **+7088 Ir/call** between
   two files with identical checksums. **The diff touches no `requires` and no
   `ensures`**; what the honest proof establishes that `m_leak` does not is an
   *intermediate* fact — the accumulator's exact value, against `m_leak`'s
   zero-ness — and `tag_fold` folds the verdict, never the accumulator, so no
   clause of the contract can tell the two programs apart. **Identical
   contract, strictly stronger intermediate** (`NOTES.md` §9b′).

## Why Verus cannot say it

`ensures r == tag_fold(..)` denotes the **value**. p47's defect does not change
the value — the leaking and the constant-time kernels are extensionally equal,
and `m_leak`'s one-line lemma (`once the accumulator is non-zero it stays
non-zero`) is the proof of exactly that. A timing property is about the
**trace**, and Verus has no term denoting a trace, no cost model, and no way to
quantify over the two executions a non-interference property compares. It is not
hard here; **it is not expressible**. And it is not even a property of the
program — it is a property of the machine code LLVM chooses afterwards.

This is `.memory/01-ladder.md` finding 5 (p17: *provably memory-safe and still
leaking*) one level up, and p09's *invisible to the proof* from the other side:
p09's specification could have been strengthened; p47's logic cannot be.

## Costs

`-O3 isolated`, whole-program marginal Ir/call, `small.bin` / `large.bin`:

- **safety**, at matched constant-time spelling: `R3 − R4 = +90.000 / +142.000`,
  and exactly `54 + 13·ncmp − 0.03125·cbytes` on `tlen ≡ 0 mod 32`
  (`max|resid| 0.00000`, 61 rows). ⚠ At `-O3 whole` it is
  `41 + 9·ncmp + 0.00000·cbytes` — **the per-byte term dies between the inline
  modes**, so name the mode.
- **safe Rust vs hardened C**: `38 + 11·ncmp` per call and **zero per compared
  byte** — the two tag loops are the same eleven SSE2 instructions.
- **security**: constant time costs **+29.6% wall clock** over the leaking safe
  rung — the median over 576 layout cross-pairs — where `Ir` says +47.1%. `Ir`
  overstates it by 1.6×.
- **safe vs unsafe in wall clock**: **+21.6%**, the median over 576 layout
  cross-pairs (+21.95% paired by layout, n = 24). `Ir` says +20.7% — they agree.
  The bands are also disjoint, in all four mode-matched partitions. ⚠ **Quote
  the median, not the separation.** `P(R3>R4) = 1.000` is a *saturated*
  proportion — at 1.000 it says exactly `min(R3) > max(R4)`, which is the
  disjoint-bands statistic `.memory/03-measurement.md` retracts, and the
  flatness measurement that licenses `P(A>B)` was taken at ≈0.58 and does not
  cover the ceiling (`NOTES.md` §11).

Every wall-clock figure is bracketed by a 72-binary layout population
(`controls/clayout.py`); the `large.bin` wall-clock row is **withdrawn** because
its estimator is dominated by the file load.

## Reproducing

```bash
python3 patterns/p47-ct-compare/inputs/gen.py --sweep
harness/check.py p47
python3 patterns/p47-ct-compare/controls/gen_controls.py --build --verus
python3 patterns/p47-ct-compare/controls/loops.py --opt O3 --mode isolated
python3 patterns/p47-ct-compare/controls/loops.py --vecops
python3 patterns/p47-ct-compare/controls/sweep_ir.py --measure --mode isolated \
    --bands k --out .temp/p47/sweep-k-iso.json
python3 patterns/p47-ct-compare/controls/sweep_ir.py --leak .temp/p47/sweep-k-iso.json
python3 patterns/p47-ct-compare/controls/predict.py .temp/p47/sweep-iso.json
python3 patterns/p47-ct-compare/controls/ir_table.py --mode isolated --leak-controls
python3 patterns/p47-ct-compare/controls/clayout.py --build
python3 patterns/p47-ct-compare/controls/clayout.py --time --input small --reps 13
python3 patterns/p47-ct-compare/controls/clayout.py --modes --input small
```

`controls/mkcontract.py` regenerates `spec.md`'s fenced block; it reads the
shared named-spelling paragraph from a **donor** pattern and refuses to write if
the result fails `harness/check.py::named_spelling_problem`.

`gen_controls.py --build` writes **every** control binary this pattern's tables
quote, in both inline modes, `m_leak` included — until TASK_065 it skipped every
`verus`-kind variant, so the `+7088` above rested on a blob the tree could not
rebuild (`NOTES.md` §6a). `ir_table.py --leak-controls` with no `--cells`
prints exactly the twelve rows of `NOTES.md` §6.

⚠ **`Ir` is not obtainable for a `-march=native` build on this box** —
valgrind 3.27.1 SIGILLs on the EVEX encodings all three compilers emit for
Cascade Lake, and *which* build dies depends on the input blob. `NOTES.md` §16
has the table and the rebuild script.
