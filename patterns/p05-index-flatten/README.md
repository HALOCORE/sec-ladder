# p05 — 2-D index flattening

**The pattern.** A window carries a header declaring a matrix — `nrow × ncol`,
two little-endian `u16` — and then the data. The kernel folds
`data[i*ncol + j]`, which is what performance-critical numerical C actually
looks like.

**The bug (CWE-129, with CWE-190 one width down).** The declared dimensions are
trusted against the buffer that actually arrived. R1 walks `nrow*ncol` elements
without checking that many are there:

```c
nrow = buf[off] + 256*buf[off+1];
ncol = buf[off+2] + 256*buf[off+3];
avail = len - 4;
/* R1h has `if (nrow * ncol > avail) return 0;` here.  R1 does not. */
for (i = 0; i < nrow; i++) {
    uint32_t row = 0;
    for (j = 0; j < ncol; j++)
        row = row + buf[off + 4 + i*ncol + j];      /* the flattened index */
    acc = acc * 31 + row;
}
return acc * 31 + nrow * ncol;
```

Unlike p16 (unsigned underflow, walks forward for ever) and p17 (signed
underflow, reads backwards), the index here is formed by **multiplication**.
That has two consequences and both are the point:

1. the proof needs **nonlinear** reasoning — `i*ncol + j < nrow*ncol` is not
   something Z3 finds;
2. **the check itself can overflow.** `nrow*ncol` is at most
   65535·65535 = 4 294 836 225, which fits `uint32_t` and exceeds `INT_MAX`, so
   the same line written with `int` dimensions wraps to −131 071 and waves the
   attack through while looking exactly right. `adversarial-ovf.bin` is that
   input; `NOTES.md` §6a builds the wrong-width cell and shows UBSan naming the
   overflow and ASan naming the read that follows.

## Why this pattern, out of catalogue order

**Every fold this project had measured was a serial Horner chain.** p16 and p17
both fold with `acc = acc*31 + b`, so the safe-vs-unsafe gap had only ever been
measured on a *scalar loop on both sides*. p16 quantified what a bounds check
costs when it blocks a 4× unroll. Nobody had measured what it costs when it can
block **vectorisation**.

p05's inner loop is an associative sum precisely so that it can vectorise, while
the Horner step happens once per *row* so the result still depends on row order.
It is the first kernel in this repo whose measured loop carries a vector
register in all 16 `-O3` cells.

## The result

*(Corrected at TASK_013_REVIEW — see `NOTES.md` §12. Every number here
reproduced exactly; two framing claims did not survive.)*

**Inside the vector body the bounds check is free.** c-clang, safe-naive,
safe-tuned, unsafe and verus all fold an element in **1.375000** Ir (= 11
instructions / 8 elements, the SSE2 vector body), with identical mnemonics; gcc,
at a 16-element body, in **1.062500**. Zero-residue lag pairs, exact to six
decimals, two independent bands.

**But the check does not disappear — it moves.** It is hoisted into a
22-instruction per-row trip-count computation and survives in the scalar
epilogue at 8 Ir/element against R4's 5. The cost is `O(nrow)`; the average gap
on shipped inputs is ~34%. **And wider lanes make it worse**: at AVX2 the gap is
**4.58×** against SSE2's 1.42×, with safe Rust absolutely slower, because the
scalar peel is one vector width long.

**Switch the vectoriser off and the same rungs pay 4.2500 Ir per element** —
p16's and p17's constant, on a third kernel and the first whose fold is not a
Horner chain. p05's own no-op control splits it further: **2.00 check + 2.25
foreclosed unroll**, the same split derived on p16.

**Why the check survives at all is the deepest result here.** The kernel already
checks `nrow*ncol <= avail`, so the panic is dead on every execution — but LLVM
cannot eliminate it, because `nrow*ncol <= avail ⟹ i*ncol + j < avail` is
**nonlinear**, which is exactly the obligation R5 discharges with
`lemma_mul_inequality`. **The cost of safety here is the price of the optimiser
failing the lemma the proof proves.**

What survives vectorisation is a cost **per row**, not per element:

```
R2 - R4  =  35  +  nrow * f(ncol mod 8),   f = [84, 32, 35, 38, 41, 44, 47, 50]
R3 - R4  =   9  +  nrow * 6
```

fitted on two `nrow` bands (128 points, zero residual) and **predicting a third,
held-out band to 0.0000 Ir over 16 points** — and derivable from the listings
with **zero fitted parameters**, so `f` absorbs nothing. Domain: `ncol > 8`.
`f(0) = 84` against `f(1) = 32` is explained by
`mov $0x8,%r11d ; cmove %r11,%r8`: a remainder of **zero is forced to a full
vector width**, because R2's loop is multi-exit and must keep a scalar epilogue.
**Every power-of-two `ncol` therefore pays an extra vector iteration it does not
need** — the residue trap of `.memory/01-ladder.md` finding 3, at a vector width.

**And here the instructions become time.** p16 measured +72% `Ir` → +0.27% time
and said the null was a property of its latency-bound chain. p05 measures
**+34.4% `Ir` → +32.9% time** on `large` (the review's remeasurement; the
delivered +30.5% was over-precise), because independent vector lanes leave no
idle issue slots for the check to fill. **R3 is not free here**: +4.7% `Ir` at
`large` but **+16.7% at `ncol = 8`** — an `O(nrow)` cost, and the end of the
"R3 is free" streak at five patterns.

R4 and R5 are **byte-identical at `-O3`** (`md5_fn 4a28657ae7e4`) — the first
time this project's byte-identity result covers a vectorised kernel, a scalar
epilogue and a nonlinear proof.

## Files

| file | what |
|---|---|
| `spec.md` | the contract every rung implements, and the `slb-contract` pin block |
| `model.py` | the independent Python reference the gate drives |
| `inputs/gen.py` | deterministic input generation, `--sweep` for the `ncol` sweep |
| `c/kernel.c` | R1 — no size check. The bug. |
| `c/kernel_hardened.c` | R1h — the same, plus the one line |
| `c/main.c` | the C driver |
| `safe_naive.rs` | R2 — indexed, zero `unsafe` |
| `safe_tuned.rs` | R3 — per-row reslice + iterator, zero `unsafe` |
| `unsafe.rs` | R4 — `get_unchecked` |
| `verus.rs` | R5 — R4's exec code + 12 discharged obligations |
| `NOTES.md` | the measurements, the TCB tally, the mutants, what is not claimed |

**Read `NOTES.md` §1 before quoting anything.** The kernel folds each row into a
`u32` accumulator rather than the `u64` TASK_013 specified, and that is not
cosmetic: with a `u64` row accumulator LLVM's cost model declines to vectorise at
the flags this project builds with, in C and in all four Rust rungs, and p05
would have measured nothing.
