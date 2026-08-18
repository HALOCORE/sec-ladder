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

*(Corrected at TASK_013_REVIEW and again at TASK_014_REVIEW / TASK_015 — see
`NOTES.md` §12. Every number here reproduced exactly, twice; four framing claims
did not survive. **The one that matters: the safety-cost half below prices two
particular `safe_tuned.rs`/`safe_naive.rs` spellings, not safe Rust.**)*

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

**Why the check survives *in these two spellings*.** The kernel already
checks `nrow*ncol <= avail`, so the panic is dead on every execution — but LLVM
cannot eliminate it, because `nrow*ncol <= avail ⟹ i*ncol + j < avail` is
**nonlinear**, which is exactly the obligation R5 discharges with
`lemma_mul_inequality`. ~~**The cost of safety here is the price of the optimiser
failing the lemma the proof proves.**~~ **Retracted at TASK_014_REVIEW.** It is
the price of the indexed and hand-resliced spellings; `data.chunks_exact(ncol)`
pays none of it and needs no lemma. The sentence is true of the **obligation**
and false as a statement about safety.

**REINSTATED at TASK_021_REVIEW, restricted to the row-scaled term — these
words and no wider** (identical in `NOTES.md` §1 and `.memory/01-ladder.md`
finding 6):

> **"On p05, the `O(nrow)` part of the in-contract safety tax is the price of
> the optimiser failing the lemma the proof proves."**

True of *this kernel*, *this declaration* and *this toolchain*, and of the
**row-scaled term only**: the in-contract respelling removes exactly one
instruction per row — `add %rsi,%rax`, the `add` that makes the row base
buffer-absolute — and the five that survive are the reslice's bounds check,
whose deletion needs `(i+1)·ncol <= nrow·ncol`, the nonlinear fact R5 discharges
with `lemma_mul_inequality`. It is **not** true of the constants, which move in
*both* rungs and by *different* amounts, and it is **not** a statement about
safety in general.

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
idle issue slots for the check to fill.

~~**R3 is not free here**: +4.7% `Ir` at `large` but +16.7% at `ncol = 8` — an
`O(nrow)` cost, and the end of the "R3 is free" streak at five patterns.~~
**Retracted.** That is `safe_tuned.rs`'s number, and `safe_tuned.rs` reslices
each row by hand. `data.chunks_exact(ncol)` — zero `unsafe`, no proof — is
**`−(nrow − 7)` Ir per call, i.e. cheaper than the unsafe rung**, on every input
in both residue classes, with identical output on all 150 committed inputs.
**There was no break in the streak.**

~~**But read `NOTES.md` §12c before quoting that as "safe beats unsafe".** R4's
spelling is not optimal either. Rewrite R4 with the same consumed-slice idiom —
one row pointer advanced by `ncol` instead of a flat `i*ncol` index — and unsafe
goes back on top, at **+11.00 Ir per call, flat in `nrow`** (19, 41 and 65 all
give exactly +11). That is p05's honest safety number: *idiom-matched, safety
costs eleven instructions per call on a vectorised 2-D fold, `O(1)` and not
`O(nrow)`.*~~

**Both halves above are retracted, and the retraction of the retraction is the
result.** `spec.md`'s `idiom` block — declared at TASK_013, moved into the
hashed contract at TASK_016 — forbids `chunks_exact` **and** the running row
pointer by name, because either deletes the `i*ncol + j` the pattern is about.
So both spellings that overturned "R3 is not free", and both spellings in the
"+11" pair, are numbers for a different kernel; TASK_014_REVIEW and TASK_015
measured them without citing `spec.md`. And +11 does not survive on its own
terms either: one more unsafe round (`while rp < end`) makes it **`nrow + 9`**,
`O(nrow)`. **p05's number is `R3 − R4 = 6·nrow + 9` under its declared idiom**
(+16.7% at 496×8, +4.7% at `large`), and `NOTES.md` §13 publishes all eleven
measured spellings as a result about *method*.

**And that number is the *shipped pair's*, not a bound on the in-contract tax**
(`NOTES.md` §14, measured at TASK_021 and corrected twice since). Inside the
declaration the shipped R3 is beaten under *both* readings of `required[1]`:
seven textually independent in-contract respellings reach **`5·nrow + 6`
against the shipped R4** with zero residual over 179 sweep points (14 values of
`nrow`, all eight `ncol` residues mod 8), so the published figure overstates
*that* pairing by `nrow + 3`. That is the claim that has held; three others have
not.

**p05 has no measured in-contract minimum, and this file will not quote one.**
Three have been published as one and all three were overturned by the next
search — `5·nrow + 6` (TASK_021, 8 unsafe spellings searched), `5·nrow + 11`
(TASK_021_REVIEW, 28), `5·nrow + 13` (TASK_022, 46) — every time by respelling
one more thing in the *unsafe* rung's prologue, every time on the first lever
the next agent pulled, and every time the refuted value had been reached by
several independent machine-code bodies, which is the evidence that kept being
mistaken for a floor. `min(R3 found) − min(R4 found)` is the difference of two
upper bounds and bounds nothing in either direction. What is quotable is the
**interval**: over the in-contract pairs searched the tax runs `2·nrow − 2` …
`6·nrow + 20` — **36 … 134 at `small`, 128 … 410 at `large`** — with the
published 123 / 399 *inside* it, and 80% / 71% of the published figure living in
spelling the declaration does not pin. (This used to add "against p16's
44% / 55%", i.e. that p05's declaration is the loosest of the set. That compared
a *pair* interval against p16's **R3-side-only** span; p16's own pair interval,
measured at TASK_023, is 111% / 109%. The comparison is withdrawn.) At `nrow = 1`
the bottom of that interval is **exactly 0**, measured: there is an admissible
pair on which safe and unsafe cost the same instruction count.

**The shape survives all three revisions under one stated pairing**, and that
is the durable part: cheapest R3 found against cheapest R4 found, p16's reading
of `required[1]`, gives `5·nrow + b` with only `b` moving (6 → 11 → 13) — same
functional form, same sign, still `O(nrow)`, coefficient still 5. Over *free*
in-contract pairings the coefficient ranges from 2 to 6, so it is a property of
the pairing convention and not of the pattern. The one instruction per row
that the respelling removes is the `add` that makes the row base buffer-absolute;
the five that survive are the reslice's bounds check, and the fact that would
delete them is the nonlinear one R5 discharges with `lemma_mul_inequality`. No
in-contract spelling searched removes those five; an *out-of-contract* linear
row index removes 2 of them.

`chunks_exact`'s advantage is
also `Ir`-only on `small` — it emits a hardware `div` per call that callgrind
prices at one instruction — though the wall-clock evidence for that
(+0.47% / 8.61% spread) did **not** reproduce and must not be quoted.

R4 and R5 are **byte-identical at `-O3`** (`md5_fn 4a28657ae7e4`) — the first
time this project's byte-identity result covers a vectorised kernel, a scalar
epilogue and a nonlinear proof.

## Files

| file | what |
|---|---|
| `spec.md` | the contract every rung implements, and the `slb-contract` pin block |
| `model.py` | the independent Python reference the gate drives |
| `inputs/gen.py` | deterministic input generation; `--sweep` gives the `ncol` sweep (bands A–C) **and the `nrow` sweep (band D, TASK_021)** |
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
