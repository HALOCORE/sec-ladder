# p05 — findings, adversarial behaviour, TCB tally, sticking points

> **Read §1 first.** p05 was commissioned to answer one question — *what does a
> bounds check cost when it can block **vectorisation** rather than a 4× unroll?*
> — and the kernel as specified would not have answered it. §1 is the
> measurement that forced a one-token change to the design; §2 is the answer;
> §3 is the decomposition that makes the answer attributable.

**The one-line result.** *(Restated at TASK_013_REVIEW. Every number below
reproduced exactly, including on shapes never measured — but the original
one-liner, "the wider the lane, the cheaper safety gets", is **refuted**, and
"0.0000 Ir per element" is true only of the vector steady state. Restated
**again** at TASK_014_REVIEW and TASK_015: the safety-cost half of this section
is retracted, because it prices two *spellings* and not the language. What
follows is the corrected statement; **§12** carries both reviews' own
measurements and the R3 audit.)*

**The bounds check does not vanish on a vectorised loop — it moves from
per-element to per-row.** Inside the vector body it really is free: c-clang,
safe-naive, safe-tuned, unsafe and verus all fold an element in **1.375000 Ir**,
identical mnemonics, six decimals, two bands. But the check is **hoisted into a
22-instruction per-row trip-count computation** and **survives in the scalar
epilogue** at 8 Ir/element against R4's 5. The cost is `O(nrow)`, and on shipped
inputs the average gap is ~34%.

**Wider lanes make it worse, not better.** At AVX2 the gap at `ncol ≡ 0 (mod 32)`
is **14601 Ir/call against SSE2's 4487** — ratio 1.42× → **4.58×** — and safe
Rust is *absolutely slower* (18674 vs 15177). The scalar peel is one vector width
long, so it grows with the lane.

**And the commissioning hypothesis was right in one regime.** At `ncol = 8`, R2's
vector guard is `N >= 9` where R4's is `ncol >= 8`, so there the check **does**
block vectorisation, costing **2.94×**. p05 contains both regimes in one kernel.

**Why the check cannot be eliminated *in these two spellings*.** The
kernel *already* checks `nrow*ncol <= avail`, so R2's panic is **dead on every
execution**. LLVM cannot remove it because `nrow*ncol <= avail ⟹ i*ncol + j <
avail` is **nonlinear** — and that is precisely the obligation R5 discharges,
with `lemma_mul_inequality` and one `by (nonlinear_arith)`. Linearising that
guard in an isolated compilation deletes the entire per-row apparatus
(TASK_014_REVIEW: 5 `cmov` → 0, 166 → 125 instructions, an unchecked epilogue),
so nonlinearity is the blocker **for this kernel written this way**.

~~**The per-row cost is the price of the optimiser failing the lemma the proof
proves.**~~ **Retracted at TASK_014_REVIEW.** It is the price of the *indexed*
and the *hand-resliced* spellings. `data.chunks_exact(ncol)` — zero `unsafe`, no
proof, no lemma — pays none of it, and the sentence is true of the **obligation**
and false as a statement about safety. That is the distinction it elided. §12.

**REINSTATED at TASK_021_REVIEW, restricted to the row-scaled term. These
words, and no wider** (`.memory/01-ladder.md` finding 6 carries the same
sentence verbatim):

> **"On p05, the `O(nrow)` part of the in-contract safety tax is the price of
> the optimiser failing the lemma the proof proves."**

True of *this kernel*, *this declaration* and *this toolchain*, and of the
**row-scaled term only**: the in-contract respelling removes exactly one
instruction per row — `add %rsi,%rax`, the `add` that makes the row base
buffer-absolute — and the five that survive are the reslice's bounds check,
whose deletion needs `(i+1)·ncol <= nrow·ncol`, the nonlinear fact R5
discharges with `lemma_mul_inequality`. It is **not** true of the constants,
which move in *both* rungs and by *different* amounts, and it is **not** a
statement about safety in general. §14g counts every term in the disassembly;
§14f is the record of the R4-side constant moving twice *after* it had been
published as flat, which is exactly why the sentence may not be widened past
the `O(nrow)` term.

Four numbers, and none of them means anything alone. **R3 first**, per
`.memory/01-ladder.md`'s standing rule — *lead with R3 or do not lead*, a rule
this project's own author has broken twice:

| | **R3 safe-tuned** | R2 safe-naive | R4 unsafe / R5 verus |
|---|---:|---:|---:|
| Ir **per element**, `-O3` as shipped (vectorised) | **1.3750** | **1.3750** | **1.3750** |
| Ir **per element**, `-vectorize-loops=false` | 2.3750 | 7.0000 | 2.7500 |
| Ir **per row**, `-O3` as shipped | **6.0000** | 29 + 3·(ncol mod 8), 84 at residue 0 | — |
| Ir **per call**, `-O3` as shipped | **+9** | +35 | — |
| shipped `large`, Ir/call | **+4.7%** | +34.4% | — |
| shipped `large`, wall clock | **+1.3%** | +30.5% | — |

Read across the first two rows: vectorisation removes the check's *per-element*
cost, and the 4.25 Ir/element that p16 and p17 measured is still there underneath
it. **That 4.25 is not "the check" either**: p05's own `-unroll-count=1` control
is a bit-for-bit no-op on R2 (`md5_fn 76d7c2380278`) and splits it
**2.00 check + 2.25 foreclosed unroll** — the identical split TASK_007_REVIEW
derived on p16, so the third reproduction is of the constant *and* its
decomposition.

⚠ **`+30.5%` in the last row is over-precise** — the review's independent
remeasurement gives **+32.9%**.

⚠ **The R3 column above is the cost of *this file's* R3, not of safe Rust, and
the difference is the whole finding.** ~~"R3 is not free on this pattern: +4.7%
at shipped `large` but +16.7% at `ncol = 8`, an O(nrow) cost. The 'R3 is free'
streak ends at five patterns, not six."~~ **Retracted at TASK_014_REVIEW.**
`safe_tuned.rs` reslices each row *by hand*; one idiomatic safe expression,
`data.chunks_exact(ncol)`, pays **`−(nrow − 7)` Ir per call against R4** —
cheaper than the unsafe rung — on every input in both residue classes, with
identical stdout and exit against R4 on all 150 committed inputs. Zero `unsafe`,
no proof, no lemma. **There was no break in the streak.** §12 has the audit, the
third spelling (`split_at`, `+(nrow + 7)`), and the control that says the
remaining ordering is an *idiom* difference and not a safety cost.

⚠ **The model below holds for `ncol > 8` only** (34755 measured against 41699
predicted at 496×8), and it has **zero fitted parameters** when derived from the
listings rather than fitted: `R4 = 37 + nrow·(27+11q+5r)`,
`R3 = 46 + nrow·(33+11q+5r)`, `R2 = 72 + nrow·(56+11V+8e)`. `f` absorbs nothing.
`f(0) = 84` is explained: `mov $0x8,%r11d ; cmove %r11,%r8` forces a remainder of
**zero** to a full vector width, because R2's loop is multi-exit and must keep an
epilogue — so every power-of-two `ncol` pays an extra vector iteration.
Read down the third row: what survives vectorisation is a cost **per row**, not
per element — a shape no earlier pattern in this project has produced, and one
that makes the answer depend on `ncol mod 8`.

And in wall clock, unlike p16: **+34.4% Ir became +30.5% time.** p16's null
(+72% Ir → +0.27% time) was a property of its serial Horner chain, exactly as
its `NOTES.md` said. p05's inner loop has independent iterations, and the
instructions turn into time.

---

## 1. The premise, and the measurement that changed the kernel

TASK_013's pseudocode folds each row into a **`u64`** accumulator. Built that
way, at the flags this project builds with — `-O3`, **no `-march` / `-C
target-cpu`**, i.e. baseline x86-64 = SSE2 — the inner loop **does not
vectorise in any LLVM rung**:

```
$ ~/tools/llvm/bin/clang -std=c99 -O3 -S k.c -Rpass-missed=loop-vectorize
k.c:16:9: remark: the cost-model indicates that vectorization is not beneficial [-Rpass-missed=loop-vectorize]
k.c:16:9: remark: the cost-model indicates that interleaving is not beneficial [-Rpass-missed=loop-vectorize]
```

```
$ for r in r2 r3 r4; do rustc -C opt-level=3 -C debug-assertions=off \
      -C codegen-units=1 --crate-type=lib --emit=asm -o $r.s $r.rs; \
      echo -n "$r.s: xmm="; grep -c xmm $r.s; done
r2.s: xmm=0
r3.s: xmm=0
r4.s: xmm=0
k_clang.s: xmm=0
k_gcc.s: xmm=39
```

clang unrolls the loop 8× **scalar**; rustc emits `xmm`-free code for R2, R3 and
R4 alike. gcc vectorises it anyway. So **p05 as specified would have measured a
null in six of its eight cells**, and the one axis nothing had tested would have
stayed untested.

The cause is the widening. A `u8 → u64` reduction needs three levels of
`punpck` per lane on SSE2, so LLVM's cost model prices 2 elements per vector
against 1 per scalar iteration and declines. Narrowing the **row** accumulator
to `u32` needs two levels, and every back end then vectorises. Measured, same
source otherwise:

| row accumulator | gcc 13.3.0 | clang 22.1.6 | rustc 1.97.1 R2 / R3 / R4 |
|---|---|---|---|
| `u64` (TASK_013's) | vectorised, 16 B/iter, **34** insns (2.13 Ir/B) | **scalar**, 8× unrolled | **scalar** in all three |
| **`u32` (shipped)** | vectorised, 16 B/iter, **17** insns (1.06 Ir/B) | vectorised, 8 B/iter, 11 insns | vectorised, 8 B/iter, 11 insns |
| `u16` | — | — | vectorised, 16 B/iter, 9 insns (0.56 Ir/B) |

`-mavx2` also fixes the `u64` form (`vectorized loop (vectorization width: 4,
interleaved count: 4)`), and `-mavx512bw` gives width 8 — but this project
passes no `-march`, `harness/build.py` is what decides that, and changing it
would move all 47 patterns and break comparability with p01/p02/p16/p17. It is a
harness change, so it was not made.

**So `row` is `u32` and `acc` is `u64`, and that is the one deviation from the
task's pseudocode.** Nothing else about the pattern moves: the fold is still
associative, the index is still `i*ncol + j` written out, the Horner step is
still once per row, the arithmetic is still wrapping, `nrow*ncol` is still
folded into the result, and the check is still `nrow * ncol > avail` in 64 bits.
A 32-bit per-row checksum is also what a real row hash would use.

### 1a. Which cells vectorise, kernel-only — the number is 19 of 32

`.memory/01-ladder.md` records that "nothing vectorises in all 32 cells" was
once written about p16 and was false — it was 23/32, with the 9 exceptions in
`whole`-mode `main`. So this table is **kernel-only in `isolated` and
`main`-only in `whole`**, which is what `harness/check.py` itself reads, and it
says which:

| cell | O0 iso | O0 whole | O3 iso | O3 whole |
|---|---|---|---|---|
| c-gcc | — | — | **xmm** (50) | **xmm** (49) |
| c-clang | — | — | **xmm** (17) | **xmm** (27) |
| c-gcc-h | — | — | **xmm** (50) | **xmm** (49) |
| c-clang-h | — | — | **xmm** (17) | **xmm** (27) |
| safe_naive | — | xmm (2) | **xmm** (17) | **xmm** (27) |
| safe_tuned | — | xmm (2) | **xmm** (17) | **xmm** (27) |
| unsafe | — | xmm (2) | **xmm** (17) | **xmm** (27) |
| verus | — | — | **xmm** (17) | **xmm** (27) |

(counts in brackets are vector-register-bearing instructions in the symbol)

**19 of 32 cells carry a vector register, and all 16 `-O3` cells do.** The three
`O0 whole` hits are exactly two instructions each in the Rust `main`, and they
are

```
movups (%rsp),%xmm0
movaps %xmm0,(%rsp)
```

— a 16-byte stack-slot move of an aggregate, **not the fold** — which is the
same artefact p16's review found and the reason that finding says "quote the
23/32". They are printed here rather than folded into the headline. The `verus`
cell does not have them because its `main` never materialises that aggregate
(`load_input` is `external_body`, so the tuple stays in the callee).

### 1b. The vector body, and that the safe and unsafe ones are the same body

`-O3 isolated`, `harness/asm.py` normalisation. **c-clang, c-clang-h,
safe_naive, safe_tuned, unsafe and verus all emit this, instruction for
instruction:**

```
movd      -0x4(%base,%idx,1),%xmm3      #  8 bytes per iteration
movd      (%base,%idx,1),%xmm4          #  (VW 4 x interleave 2)
punpcklbw %xmm0,%xmm3
punpcklwd %xmm0,%xmm3
paddd     %xmm3,%xmm2
punpcklbw %xmm0,%xmm4
punpcklwd %xmm0,%xmm4
paddd     %xmm4,%xmm1
add       $0x8,%idx
cmp       %idx,%limit
jne       <top>                          # 11 instructions / 8 elements = 1.375
```

gcc's is a different shape and a different width — one `movdqu`, 16 elements per
iteration, 17 instructions = **1.0625 Ir/element** — *plus a second, narrower
vector loop* (`movq`, 8 elements) that serves as its epilogue. **That is why
`inputs/gen.py` checks residues mod 8 and mod 16: the two back ends have
different periods on the same source.**

**The R2 vector loop is instruction-for-instruction R4's — same eleven
mnemonics in the same order, differing only in which general-purpose registers
carry the base and the index — and the check is not in it.** (Not *byte*
identical: the register allocation differs, so the encodings do. The identity
claim that is byte-exact on p05 is R4 ≡ R5, §9.) LLVM
hoists the bound out of the vector body by computing, once per row, how many
iterations are provably in range (the `cmov`/`imul` preamble at the top of R2's
row loop) and sending the rest to a checked scalar epilogue. So the question
"does the check block vectorisation" has a clean answer — *no* — and the real
question becomes what the hoisting costs. §2.

---

## 2. The sweep: Ir per element, per row, and per call

Method: marginal Ir per kernel call = whole-program Ir at `n_iters=200` minus at
`n_iters=100`, over 100 — `harness/check.py` step 3b's method, a difference of
two runs of the same binary, so the one-shot loader terms cancel and it is
symbol-independent. `.temp/p05/sweep_ir.py`. **"every loader and environment
term cancels" is false** and this line used to say it (TASK_019, from
TASK_018_REVIEW M3): the environment block is worth ~0.1 Ir/call on p08 *within
one build* (six environment lengths at TASK_019, 21 at TASK_020, both
7292.12 … 7292.22), and heap alignment ~0.02 on p02, with the kernel's own
self-cost identical in both cases. Across *builds* the level itself moves —
p08's cross-session union is 7292.10 … 7292.30 = 0.20 (TASK_020) — so the
figure to carry is ~0.1 within a build and ~0.2 across sessions. Every
delta below is a within-session difference, which is where the method is
exact; see `patterns/p01-array-sum/spec.md`'s `collapse.note`.

**Swept, not sampled, and over two full cycles of the widest modulus in play**
(`.memory/01-ladder.md`: "sweep two full cycles: the first sweep design used 16
lengths per band and could not distinguish period 16 from period 64"). 64
consecutive `ncol` per band = 2 cycles of 32, 4 of 16, 8 of 8.

- band A: `nrow = 19`, `ncol` 24…87, 32 windows
- band B: `nrow = 65`, `ncol` 56…119, 512 windows
- band C: `nrow = 41`, `ncol` 24…39 — **held out**, see §2b

### 2a. The result, exactly

Over all 128 points of bands A and B, with **zero residual**:

```
R2 - R4  =  35  +  nrow * f(ncol mod 8),   f = [84, 32, 35, 38, 41, 44, 47, 50]
R3 - R4  =   9  +  nrow * 6
```

**Count the degrees of freedom before believing that.** The R2 model has 16
parameters (8 residues × an intercept and a slope) and they are solved from 16
of the 128 points — the lowest `ncol` of each residue class in each band. The
other **112 points are out-of-sample and every one of them is reproduced
exactly**, and so are the 16 further points of band C at an `nrow` no fitted
point used (§2b). The R3 model has 2 parameters and 126 out-of-sample points.

so, per residue class of `ncol mod 8` (band A / band B):

| `ncol mod 8` | R2−R4 @ nrow=19 | R2−R4 @ nrow=65 | per row |
|---:|---:|---:|---:|
| 0 | 1631.00 | 5495.00 | **84** |
| 1 | 643.00 | 2115.00 | 32 |
| 2 | 700.00 | 2310.00 | 35 |
| 3 | 757.00 | 2505.00 | 38 |
| 4 | 814.00 | 2700.00 | 41 |
| 5 | 871.00 | 2895.00 | 44 |
| 6 | 928.00 | 3090.00 | 47 |
| 7 | 985.00 | 3285.00 | 50 |

R3−R4 is **123.00 at every one of the 64 band-A points and 399.00 at every one
of the 64 band-B points** — flat in `ncol`, flat in the residue, and exactly
`9 + 6·nrow`.

⚠ **Two qualifications on that line, both added at TASK_021 and both measured;
(ii) has itself been corrected twice, at TASK_021_REVIEW and again at
TASK_022.** (i) The `nrow` coefficient rested on the three values bands A–C
supply (19, 41, 65); band D now sweeps `nrow ∈ {1…9, 12, 16}` at three `ncol`
residue classes and the form is reproduced with **zero residual on all 179
measured points** (177 distinct `(nrow, ncol)` pairs — `small` and `large`
repeat `sweep-r19c26` and `sweep-r65c61` with different bytes), so it is a law
and no longer a three-point fit. (ii) `9 + 6·nrow` is the **shipped pair's**
difference and nothing more. Both rungs can be respelled inside the
declaration, both get cheaper when they are, and **p05 has no measured
in-contract minimum**: three have been published as one and all three were
overturned by the next search (§14h). What has not moved under any of them:
against the *shipped* R4 the cheapest R3 found costs `5·nrow + 6`, so
`9 + 6·nrow` overstates *that* pairing by `nrow + 3` at every `nrow` (§14).

Three things follow and they are the finding:

1. **The per-element cost of the check is exactly zero, for R2 as well as R3.**
   Within a residue class R2−R4 does not move at all as `ncol` grows by 8, 16,
   24 … 56. Confirmed directly on **zero-residue lag pairs** (`ncol` and
   `ncol+32`, both ≡ 0 mod 32 and therefore ≡ 0 mod 8 and mod 16, so neither
   epilogue contributes anything to the difference):

   | cell | nrow=19, ncol 32→64 | nrow=65, ncol 64→96 |
   |---|---:|---:|
   | c-gcc | **1.062500** Ir/element | **1.062500** |
   | c-clang | **1.375000** | **1.375000** |
   | safe_naive | **1.375000** | **1.375000** |
   | safe_tuned | **1.375000** | **1.375000** |
   | unsafe | **1.375000** | **1.375000** |

   1.375000 = 11/8, the vector body of §1b, to six decimal places. 1.0625 =
   17/16, gcc's. **Safe and unsafe Rust and same-backend C fold an element at
   precisely the same instruction cost.**

2. **What the check costs instead is per *row*, and it depends on `ncol mod 8`.**
   29 + 3·r for r ≥ 1: a fixed 29 per row (LLVM's hoisted trip-count
   computation) plus **3 Ir per element of the scalar epilogue** — the epilogue
   is where the bounds check survives, and it is `ncol mod 8` elements long.

3. **Residue 0 is the worst case and it is 2.6× the best.** At `ncol ≡ 0 (mod
   8)` R4 has no epilogue at all, but R2 still peels one, so R2 pays 84 per row
   against 32 at residue 1. This is `.memory/01-ladder.md` finding 3's trap
   ("R2's vectoriser peels a 4-element scalar epilogue when `n % 4 == 0`") at
   modulus 8, and it is the fourth time this project has met it. **`small` has
   `ncol = 26` (r = 2) and `large` has `ncol = 61` (r = 5)** — had `gen.py`
   chosen two multiples of 8, the shipped R2−R4 would have been 1631/5495
   instead of 700/2895, an overstatement of 2.33× and 1.90×.

### 2b. The model is a fit, not an interpolation — band C

Two values of `nrow` determine `a + b·nrow` exactly, which
`.memory/01-ladder.md` is explicit is not a prediction. Band C holds `ncol` to
one cycle of 16 and moves `nrow` to **41**, a value neither fitted band used:

```
=== OUT-OF-SAMPLE TEST, nrow=41, ncol 24..39 ===
 ncol  %8  R2-R4 pred  R2-R4 meas    err    R3-R4 pred  R3-R4 meas   err
   24   0     3479.00     3479.00   0.00        255.00      255.00  0.00
   25   1     1347.00     1347.00  -0.00        255.00      255.00  0.00
   ...
   39   7     2085.00     2085.00   0.00        255.00      255.00  0.00
  max |prediction - measurement| over 16 out-of-sample points: 0.0000
```

16 out-of-sample points, **maximum error 0.0000 Ir**.

### 2c. The shipped inputs, `-O3 isolated`, kernel-exclusive `Ir` per call

| rung | small (19×26 = 494 elem) | large (65×61 = 3965 elem) | vs R4 |
|---|---:|---:|---|
| c-gcc / c-gcc-h | 1730.0 / 1737.0 | 9204.0 / 9211.0 | check = **+7 / +7**, flat |
| c-clang / c-clang-h | 1367.0 / 1369.0 | 8422.0 / 8424.0 | check = **+2 / +2**, flat |
| **R2 safe-naive** | **2067.0** | **11317.0** | **+700 (+51.2%) / +2895 (+34.4%)** |
| R3 safe-tuned | 1490.0 | 8821.0 | +123 (+9.0%) / +399 (+4.7%) |
| R4 unsafe / R5 verus | 1367.0 / 1367.0 | 8422.0 / 8422.0 | 0 |

**c-clang, unsafe Rust and verified Rust execute the identical number of
instructions**, 1367.0 and 8422.0 — not "within one", exactly equal, which is
the publishable form of that claim (`.memory/03-measurement.md`).

**R1h costs +7 (gcc) / +2 (clang) instructions per call, flat in the size of the
matrix.** That is what the memory-safety check costs inside C: two instructions.

---

## 3. Decomposition — attribute to a mechanism, never to a comparison

`.memory/01-ladder.md`: *"a safety tax must be attributed to a mechanism, never
to a comparison"*, and *"confirm by construction, do not infer from reading two
disassemblies"*. Two constructions, both run.

**R3 first, again.** The honest sentence about safe Rust on p05 is *idiomatic
safe Rust costs 6 instructions per row and zero per element, which is +4.7%
instructions and +1.3% time on `large`*. Everything below is about why the
*naive indexed* spelling costs more than that, and it must not be read as the
cost of safety.

### 3a. R2 vs R3 isolates the inner loop, by construction

R2 and R3 differ in the inner loop and in **nothing else** — same header
handling, same `nrow == 0 || ncol == 0` guard, same `nrow * ncol > avail` check,
same outer Horner step, same flattened index `off + 4 + i*ncol` — so R2 − R3 is
the cost of the per-element check *given* that the reslice has already moved it
out of the loop. Measured: `26 + nrow·(f(r) − 6)`, i.e. 577 on `small` and 2496
on `large`, and **0.0000 per element**.

That is the whole gap: changing only the inner loop's spelling removes 82.4% of
R2's tax on `small` and 86.2% on `large`, and the remainder is the +9/+35
per-call constant plus R3's own 6 Ir/row reslice.

### 3b. The control that names the mechanism: disable vectorisation

This is p05's analogue of p16's rolled-vs-rolled control. Same sources, same
`-O3`, plus `-C llvm-args=-vectorize-loops=false -C llvm-args=-vectorize-slp=false`
(rustc) / `-fno-vectorize -fno-slp-vectorize` (clang) / `-fno-tree-vectorize`
(gcc). Every variant prints the shipped checksum `1506433241298462329` on
`small.bin` and carries **no vector register at all** (`vector_regs=[]` in all
five). Same zero-residue lag pairs:

```
=== VECTORISATION DISABLED, nrow=19, ncol 32->64 ===   === nrow=65, ncol 64->96 ===
cell         Ir/element                                  Ir/element
safe_naive      7.0000                                      7.0000
safe_tuned      2.3750                                      2.3750
unsafe          2.7500                                      2.7500
c-clang         2.3750                                      2.3750
c-gcc           5.0000                                      5.0000
  R2-R4 per element = 4.2500      R3-R4 per element = -0.3750     (both bands)
```

**R2 − R4 = 4.2500 Ir per element, exactly** — p16's swept constant and p17's,
now on a **third** kernel and a completely different loop shape: an associative
sum rather than a serial Horner chain, with a 2-D index rather than a running
pointer. `.memory/01-ladder.md` says 4.25 "is a property of *rustc's checked
indexed byte fold*, not of p16"; p05 is the third independent confirmation and
the first one where the fold is not a Horner chain at all.

So the mechanism is named by construction:

> **The 4.2500 Ir/element the check costs is exactly what vectorisation removes.**
> Turn the vectoriser off and it is there; turn it on and it is 0.0000, with the
> remainder appearing as 29 + 3·(ncol mod 8) instructions per row.

Two side observations from the same control, both worth keeping. R3 is **cheaper
than R4** without the vectoriser (2.3750 vs 2.7500, i.e. −0.3750/element): the
iterator form still unrolls where the indexed unchecked form does not, so
"unsafe is the floor" is false even at the instruction level. And c-clang
matches R3 exactly at 2.3750, not R4.

---

## 4. Wall clock — and this time the instructions *do* become time

`taskset -c 3`, 31 reps, round-robin interleaved, **per-call time obtained by
differencing `n_iters`** (12 000 → 36 000 on `large`, 25 000 → 75 000 on
`small`) so that process start-up and file reading cancel exactly.
`.memory/03-measurement.md`: never divide a total wall time by an element count.

**`large.bin`, worst raw min-to-median spread 2.3% over all 16 sample sets:**

| rung | ns per call (min) | ns per element | Ir per call | Δ time vs R4 | Δ Ir vs R4 |
|---|---:|---:|---:|---:|---:|
| c-gcc | 575.57 | 0.1452 | 9204 | +4.0% | +9.3% |
| c-clang | 548.74 | 0.1384 | 8422 | −0.8% | 0.0% |
| c-gcc-h | 603.36 | 0.1522 | 9211 | +9.0% | +9.4% |
| c-clang-h | 556.56 | 0.1404 | 8424 | +0.6% | 0.0% |
| **R2 safe-naive** | **722.23** | **0.1822** | 11317 | **+30.5%** | **+34.4%** |
| R3 safe-tuned | 560.39 | 0.1413 | 8821 | +1.3% | +4.7% |
| R4 unsafe | 553.32 | 0.1396 | 8422 | — | — |
| R5 verus | 549.54 | 0.1386 | 8422 | −0.7% | 0.0% |

**This is the result p16 predicted it could not measure.** p16's `NOTES.md` §2
says: *"This is a property of this kernel, not of bounds checks: a kernel with
independent inner iterations would turn the same 4.25 Ir/byte into time."* p05
is that kernel. +34.4% `Ir` → **+30.5%** time, against p16's +72% → +0.27%.
Ir and wall clock agree here to within 4 percentage points, and the reason is
mechanical: p16's fold was latency-bound on a 3-cycle serial chain with idle
issue slots for the check to fill, and p05's is throughput-bound on independent
vector lanes with no slack.

R3 remains free — **+1.3% time for the sixth pattern running** — and R5 is
indistinguishable from R4, as it must be (byte-identical machine code).

`small.bin` is **discarded** for the wall-clock claim: its `safe_naive` sample
set at `n_iters = 25 000` has a 13.8% min-to-median spread, over
`.memory/03-measurement.md`'s 10% threshold. It is printed in
`.temp/p05/wall2-analysis.txt` rather than deleted, and no claim above rests on
it. The `Ir` column for `small` is unaffected — callgrind is deterministic.
**§4b reaches the same verdict from a second direction and makes it much
stronger**: on byte-identical binaries p05's `small` cell has a wider band than
the effect anyone wanted to read off it.

### 4a. Cycles — quotable this time, because the clock was measured interleaved

`.memory/00-environment.md` forbids quoting cycles from a clock measured in
another session. The dependent-`addq` probe was therefore made a **participant
in the same round-robin** as the reps above, one 40 M-iteration window after
every rep:

```
clock probe, INTERLEAVED with these reps (dependent addq, 40 M iters, cpu 3, 31 reps):
  min 3236 MHz  median 3732 MHz  max 3816 MHz
```

At the median 3.732 GHz, R4 folds an element in **0.521 cycles**; over the
probe's full min–max range the figure is **0.452 – 0.533 cycles/element**. That
is ~4.2 cycles per 8-element vector iteration for an 11-instruction body, i.e.
IPC ≈ 2.6, which is what an SSE2 integer loop should do on this core.

Note the probe's own spread — 3236 to 3816 MHz **within one session, on one
pinned core, 31 windows apart** — which is a fresh, first-hand demonstration of
why `.memory/00-environment.md`'s rule exists. Even interleaved, cycles is an
inference with a ±15% band on it, and ns is the measurement.

### 4b. The `small` wall-clock row is WITHDRAWN — and the reason is not code layout

**TASK_030_REVIEW raised this; TASK_031 measured it and the diagnosis changed.**
`results/tables/p05-index-flatten.md`'s `-O3 isolated` `small.bin` minima are
7.24 ms (R2), 5.54 (R3) and 5.32 (R4), i.e. **R2 +36.01%** and **R3 +4.12%** over
`unsafe`. Do not quote either to a decimal. Nothing below touches `large`, which
is where §4's numbers come from.

**First, what it is NOT: p05 has no code-layout mode.** Built at 30 layouts per
rung, no address bit separates p05's timings — best ratios ×1.0031 (R2), ×0.9817
(R3), ×1.0146 (R4), never a perfect split — even though the 32-byte geometry
*does* flip exactly as it does on p01 and p07:

```
unsafe  loop0 [kernel+0x70,+0x124) 180 B  win32[6,7]  jcc32[1,2]
        small x0.9856  x0.9857    large x1.0016  x0.9996
```

One extra 32-byte fetch window, no time. p05's fold is throughput-bound on
independent vector lanes, not front-end-bound, so the grid costs it nothing
(`.memory/03-measurement.md`).

**Second, what TASK_030_REVIEW thought it was, and why that is wrong.** It read
off one 31-binary round-robin that the *shipped* build is the slowest R2 layout
of 31 and the fastest R3 of 31, giving R3-vs-R4 = **−9.91% / −11.57%** against a
published +4.12%, and concluded the published gap was a worst-against-best layout
pairing. **TASK_031 reproduced that entire pattern with no layout variation at
all** — 31 **byte-identical copies** of each shipped rung, distinct inodes, one
layout, timed in the same harness, varying only the *order* of the round-robin
(`.temp/p31/order.py`, `order_p05.log`, `order_p05_pos.log`):

| order | R2 vs R4 (medians) | R3 vs R4 (medians) | R3 vs R4 (slot 0) | slot-0 rank R2 / R3 |
|---|---:|---:|---:|---|
| **alternating** (4 blocks) | +28.08 / +30.85 / +30.32 / +30.56% | +1.21 / +4.64 / +4.22 / +4.43% | +0.63 … +6.64% | mid-field |
| **blocked** (4 blocks) | +6.00 / +5.29 / +18.00 / +18.37% | −4.16 / −1.49 / −0.99 / −0.26% | **−11.70 / −10.77 / −3.68 / −3.92%** | R2 slowest, R3 fastest |

Against the population run it is meant to explain: shipped R2 rank 30/30, shipped
R3 rank 0/30, R3-vs-R4 −9.91% / −11.57%, "population" R2-vs-R4 +7.17% / +6.96%.
**Every one of those readings is reproduced by identical copies of one binary.**

The mechanism is in the harness, not the machine. `.temp/r30/layout_gen.py` times
with `for k, b in bins.items()` over a dict filled **rung by rung**, so each rung
occupies a contiguous third of every rep and the shipped build is slot 0 of its
own rung's block — while `harness/measure.py`'s `wall()`, `.temp/r30/repeat.py`
and `.temp/r30/interleave.py` all *alternate* the rungs, which is what
`.memory/03-measurement.md` asks for ("spreading thermal/neighbour drift across
all cells beats concentrating it in one"). `interleave.py` ruled out the
round-robin's **width** (+33.75 / +31.24 / +29.25 / +30.26% at widths 1/5/15/30);
it did not vary the **order**, and the order is what moves it. Same effect,
smaller, on the "lever bias" that was read as a property of
`--symbol-ordering-file`: on identical copies, slots 10–30 (where the `order`
builds sit) come out **+3.90% / +5.30%** slower than slots 1–9 (the `align`
builds) under blocked order and **−0.98 … +0.36%** under alternating, against
`.temp/r30/lever_bias.log`'s +5.05 / +5.27 / +9.85% for this exact rung
(`.temp/p31/posbias.py`).

**Third, the reason the row really is withdrawn, and it is simpler.** p05's
`small` cell is not measurable to this precision on this box. Over four
(pass × order) blocks, the 31 byte-identical copies of a rung span **5.09% …
45.04%**, above 10% in **17 of 24** rung-blocks. Measured the same way, in the
same session, on the same core:

| pattern, `small` | 31 identical copies | 30 layouts | band / noise |
|---|---|---|---|
| p01 | **0.82 … 3.17%** | 10.42 / 10.15 / 7.74% | ~5–9× |
| p07 | **0.83 … 2.24%** | 31.76 / 17.12 / 8.08% | ~4–20× |
| **p05** | **5.09 … 45.04%** | 14.09 / 8.30 / 9.34% | **< 1×** |

**p05's 30-layout "band" is smaller than its own noise floor on byte-identical
binaries.** There is nothing to attribute to layout because there is nothing
above the noise to attribute.

**What survives, and it is not nothing.** A *median over many binaries* averages
that noise out, and under the project's own alternating protocol the R2 gap is
stable: **+28.08 / +30.85 / +30.32 / +30.56%** (TASK_031, identical copies),
**+28.68 … +32.49%** over 8 independent blocks (`.temp/r30/repeat_p05.log`),
**+29.25 … +33.75%** at four round-robin widths (`interleave_p05.log`). So **R2
really is about +30% slower than R4 on `small`, and the published +36.01% is ~6
points high** — a single-binary min-of-31 read out of a distribution that is 20%
wide. R3-vs-R4 is **+1.21 … +6.88%** over seventeen alternating measurements
(the published cell, 8 `repeat.py` blocks, 4 `interleave.py` widths, 4
`order.py` medians), **every one positive**; it is a few percent and it is not
4.12%.

**Two traps for whoever revisits this.**

- The `small` *`Ir`* column is untouched — callgrind is deterministic and p05's
  instruction laws are exact (§3, §3a).
- A layout population compares **whole-process** minima, but §4's headline
  (+30.5% on `large`) is a **per-call** number with start-up and file reading
  differenced out. They are different statistics on different inputs; the
  population's `large` R2 figure (+15.2%) is not a correction of +30.5% and must
  not be quoted as one.

---

## 5. The proof: 12 obligations, and what each mutant proves

`./verus_run.py patterns/p05-index-flatten/verus.rs` → **`12 verified, 0
errors`**. With `--cfg slb_twin` → **`13 verified, 0 errors`**. Per item, all
measured with `--verify-function <name> --verify-root`:

| item | obligations | why |
|---|---:|---|
| `nrow_at`, `ncol_at`, `grid_fold` | 0 | non-recursive `spec fn` |
| `row_fold`, `grid_walk` | 1 each | recursive: one termination query |
| `get_unchecked`, `load_input`, `emit` | 0 | `external_body` |
| `kernel` | **5** | body + 2 loop bodies + 2 `by (nonlinear_arith)` sub-proofs |
| `main` | **5** | quoted as measured — see below |
| `slb_twin_get_unchecked` (`--cfg slb_twin`) | 1 | one function, no loop, no `by` |

**`main`'s 5 does not decompose from the command line, and p17's `spec.md` has
the same off-by-one on the identical driver.** The by-block rule of thumb
predicts 1 (body) + 1 (loop) + 4 (`by` sub-proofs: two `by (nonlinear_arith)`
and one `by { lemma2_to64_rest() }` in the first ghost block, one
`by (nonlinear_arith)` in the second) = **6**, and Verus reports **5**. p17's
`spec.md` asserts the same decomposition for a character-identical driver and
also lands on 5, so its `obligations_note` is arithmetically wrong in the same
way. Reported rather than fixed — p17 is out of scope for this task —
but it is a real defect in a committed pin's justification.
`.memory/04-verus.md` already says the count "is a checksum over the
function/loop skeleton" and that an unchanged count is evidence of nothing; this
adds that the *published derivation* of one is not reliable either.

### 5a. Sticking points, for the next pattern with a nonlinear index

**The proof cost about twenty minutes and one wrong invariant.** The one thing
that mattered:

> The obligation is `i < nrow && j < ncol && nrow*ncol <= avail  ⟹
> i*ncol + j < avail`, and it is nonlinear in two variables at once. Z3 does not
> find it.

The step that carries it is `(i+1)·ncol <= nrow·ncol` from `i+1 <= nrow`
(`vstd::arithmetic::mul::lemma_mul_inequality`, broadcast) joined to
`(i+1)·ncol == i·ncol + ncol` by one `by (nonlinear_arith)`.

**And the conjunct `i*ncol + ncol <= nrow*ncol` cannot live in the outer loop's
invariant**, which is the mistake that cost the twenty minutes: at `i == nrow`
it is false, so the invariant fails *at the end of the loop body* and *before the
loop*. It has to be established at the **top of the loop body**, where `i < nrow`
is known, and then carried into the inner loop's invariant — because a loop
invariant cuts the pre-loop context (`.memory/04-verus.md`).

Two things p17 needed and p05 did not: **no `isize::MAX` slice-length axiom is
required**, because p05 is unsigned end to end, so the second `requires` clause
and the driver conjunct that discharged it are both absent; and there is no
`continue` problem, because the guard is a size test before the loops rather
than a per-iteration one.

One thing p05 needed and no earlier pattern did: `nrow * ncol` in `usize` must
be shown not to overflow, and Verus models `usize` as *possibly 32-bit*. The
bound is `65535·65535 = 4 294 836 225 <= 0xffff_ffff`, one `by
(nonlinear_arith)` from `nrow <= 65535 && ncol <= 65535`. It is the same
multiplication whose narrower *signed* spelling is the C bug in §6, so the proof
discharges by construction the thing the C rung gets wrong.

### 5b. Mutants — every one run, with its actual verdict

Generated from the shipped `verus.rs` by **exact-string substitution with a
hit-count assertion**, so they cannot drift from it, into `.temp/p05/mirror/`
(`.memory/05-layout.md` demand 11: a Verus control that does not verify cleanly
cannot live in a pattern dir at all — `check.py:1446` requires every `.rs` with
a `verus!` block to be pinned, and `:1549` fails the gate for any pinned file
with errors). The generator:

```sh
mkdir -p .temp/p05/mirror/common .temp/p05/mirror/patterns/p05-index-flatten
cp common/driver.rs .temp/p05/mirror/common/
python3 - <<'PY'
t = open("patterns/p05-index-flatten/verus.rs").read()
def sub(out, pairs):
    s = t
    for old, new in pairs:
        assert s.count(old) == 1, (out, old, s.count(old))
        s = s.replace(old, new)
    open(".temp/p05/mirror/patterns/p05-index-flatten/" + out, "w").write(s)
CHECK = "    if nrow * ncol > avail {\n        return 0;\n    }\n"
ENS   = "        r == grid_fold(buf@, off as int, len as int),\n"
CONS  = "            assert(r == grid_fold(buf@, (k * stride) as int, stride as int));\n"
REQ   = "fn get_unchecked(v: &[u8], i: usize) -> (r: u8)\n    requires\n        i < v@.len(),"
TREQ  = "fn slb_twin_get_unchecked(v: &[u8], i: usize) -> (r: u8)\n    requires\n        i < v@.len(),"
sub("verus_m0_msonly.rs",          [(ENS, "        r == r,\n"), (CONS, "")])
sub("verus_m1_nocheck.rs",         [(CHECK, "")])
sub("verus_m1b_nocheck_msonly.rs", [(CHECK, ""), (ENS, "        r == r,\n"), (CONS, "")])
sub("verus_m2_offbyone.rs",        [(REQ, REQ.replace("i < v@", "i <= v@")),
                                    (TREQ, TREQ.replace("i < v@", "i <= v@"))])
sub("verus_m3_tautology.rs",       [(ENS, "        r == r,\n")])
PY
```

| mutant | what it changes | Verus verdict | what it proves |
|---|---|---|---|
| control | — | `12 verified, 0 errors` | — |
| **M0** | functional spec stripped (`ensures r == r`, consuming `assert` deleted) | `12 verified, 0 errors` | the **negative control** for M1b: stripping the spec is not itself an error |
| **M1** | **the size check deleted from the exec code**, spec untouched | `11 verified, 1 errors` — *invariant not satisfied before loop*, at `nrow * ncol <= avail` | deleting the check fails a **memory-safety** obligation |
| **M1b** | M1 **and** the functional spec stripped | `11 verified, 1 errors` — **the same** invariant | the **positive control** `.memory/04-verus.md` §2b demands: nothing was hiding behind a functional failure |
| **M2** | trusted `requires` `i < v@.len()` → `i <= v@.len()`, on the item **and** its twin | **`12 verified, 0 errors`** shipped; **`12 verified, 1 errors`** under `--cfg slb_twin` — *precondition not met: index in bounds for this access* | **Verus alone passes the off-by-one; the verified twin is the only VERUS-level catcher.** ⚠ Not the only *gate* catcher: `spec.md`'s pin fails too, twice — §10 prints both `[proof-pin]` FAILs. Corrected at TASK_056; this cell used to read *"only the verified twin catches it"* |
| **M3** | kernel `ensures` tautologised to `r == r` | `11 verified, 1 errors` at the driver's consuming `assert` | the `ensures` is load-bearing, not decoration |

**M1 + M1b is the measurement that files p05 with p16 and not with p17.** On p17
the same experiment failed the *functional* `ensures` with every memory-safety
obligation still discharged, because p17's harm was a legal read of the wrong
bytes. p05's harm is an ordinary read past the end, so the obligation that
catches it is the one the trusted accessor's `requires` feeds, and it fails
**with the functional spec removed**. That is the honest way to say "the
accessor precondition is the security property here": by deleting the other
candidate and watching it still fail.

Both M2 and M3 were also run through the whole gate by swapping them into the
pattern dir; §10 has the exact `check.py` failure lines.

---

## 6. The C cells, and the check that looks right

### 6a. The width the check is written in

`adversarial-ovf.bin` declares `nrow = ncol = 65535`. Three widths, same source
otherwise, same `-O3`:

| check | `nrow*ncol` as computed | verdict on `adversarial-ovf` |
|---|---|---|
| `size_t` (shipped R1h) | 4 294 836 225 | rejects, prints `0`, exit 0, **ASan+UBSan clean** |
| `uint32_t` | 4 294 836 225 | rejects — **the product fits**, 4 294 836 225 < 4 294 967 295 |
| **`int` (`.temp/p05/cvar/kernel_intcheck.c`)** | **−131 071** (UB; wraps) | **accepts**, then reads off the end |

```
$ .temp/p05/cvar/gcc-intcheck patterns/p05-index-flatten/inputs/adversarial-ovf.bin
Segmentation fault
$ .temp/p05/cvar/clang-intcheck ...                       # same
$ .temp/p05/cvar/gcc-intcheck-san ...                     # ASan+UBSan, -O1
.temp/p05/cvar/kernel_intcheck.c:53:19: runtime error: signed integer overflow:
    65535 * 65535 cannot be represented in type 'int'
==3557725==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x507000000148
READ of size 1 at 0x507000000148 thread T0
    #0 ... in kernel .temp/p05/cvar/kernel_intcheck.c:59
0x507000000148 is located 0 bytes after 72-byte region [0x507000000100,0x507000000148)
$ .temp/p05/cvar/gcc-h-san ...                            # the SHIPPED 64-bit check
0
```

**So the common phrasing "the same check written in `int`/`u32` can overflow" is
wrong by one type on this format**, and the correction is worth having because it
is the sort of thing a reader will reuse: with **u16** dimension fields the
product cannot exceed `UINT32_MAX`, so an unsigned 32-bit check is sound against
everything the wire can express, and only the *signed* one breaks. It would
break in both if the header fields were u32. "Do it in 64 bits" is the right
advice either way; "do it in an unsigned type" is right here by luck.

### 6b. The zero guard is a DoS guard, and only against one compiler

`if (nrow == 0 || ncol == 0) return 0;` changes **no answer** (§ `spec.md`): an
empty fold returns 0 with or without it. `adversarial-zero.bin` declares
`nrow = 65535, ncol = 0`, so `nrow*ncol == 0` passes the size check and the
outer loop runs 65 535 times doing nothing. Marginal Ir per call, same method as
§2:

| cell | shipped (guard present) | guard removed | ratio |
|---|---:|---:|---:|
| c-gcc-h | 43.00 | **786 482.00** | **18 290×** |
| c-clang-h | 27.00 | 33.00 | 1.2× |

All four print `0`. **gcc leaves the empty loop in and clang deletes it**, so the
same missing guard is an 18 000× attacker-controlled amplification with one
compiler and a no-op with the other. Neither is a memory error and no sanitizer
fires; this is a cost bug, and it is the reason the guard ships even though it is
semantically dead.

### 6c. gcc vs clang, and it goes the other way from p16/p17

On p16 and p17 gcc executed ~36% *more* instructions than clang and needed
`-funroll-loops` to catch up. Here the two facts point in opposite directions
and both are true:

- **per element, gcc is cheaper** — 1.0625 Ir/element against LLVM's 1.375,
  because gcc's vector body takes 16 elements per `movdqu` where LLVM's takes 8
  (§2a, measured on zero-residue lag pairs, exact to six decimals);
- **per call, gcc is dearer** — 9204 vs 8422 on `large` (+9.3%) and 1730 vs 1367
  on `small` (+26.6%), because its per-row prologue is much larger (167 static
  instructions in the kernel against clang's 86) and it emits a *second*,
  narrower vector loop as its epilogue.

So gcc wins the loop and loses the call, and which one shows up depends entirely
on `ncol`: at `ncol = 26` the per-row term dominates, at `ncol = 96` it does not
(8439 gcc vs 10256 clang on band B — gcc **ahead** by 18%). In wall clock on
`large` gcc is +4.0% against clang's −0.8%. **Do not quote a gcc-vs-clang ratio
for p05 without the row shape it was taken at.** No `-funroll-loops` experiment
was run: these loops are vectorised, not unrolled, so p16's
flag-default-vs-capability question does not arise in the same form.

---

## 7. Adversarial behaviour, per rung

`n_iters` is 8 on every adversarial input: R1 is executing undefined behaviour
on two of them and there is nothing to learn from doing it 25 000 times. Every
adversarial input is exactly one window (`n_blob == stride`), so `k` is always 0
and `off` is always 0 — see `spec.md`.

| input | what it declares | R1 c-gcc / c-clang | R1h c-*-h | R2 | R3 | R4 | R5 | ASan/UBSan on R1 |
|---|---|---|---|---|---|---|---|---|
| `adversarial-dims` | 8×64 = 512 elements against `avail` 64 | exit 0, **four different wrong numbers** across the four opt/mode variants (e.g. `14877878885076185856`, `2060641739447621120`) | `0` | `0` | `0` | `0` | `0` | **`heap-buffer-overflow`, fires as declared** |
| `adversarial-ovf` | 65535×65535 | **SIGSEGV (exit −11)**, both compilers | `0` | `0` | `0` | `0` | `0` | **`heap-buffer-overflow`, fires as declared** |
| `adversarial-zero` | `nrow=65535, ncol=0` | `0` | `0` | `0` | `0` | `0` | `0` | clean, exit 0 |
| `adversarial-stride3` | stride 3 < the 4-byte header | `0` (zero kernel calls) | `0` | `0` | `0` | `0` | `0` | clean, exit 0 |

Two details worth keeping.

**R1 on `adversarial-dims` gives four different answers from four builds of the
same source** — `-O0`/`-O3` × `isolated`/`whole`, per compiler. It reads 448
bytes past a 68-byte heap block, and what is there depends on the allocator's
neighbourhood, which the optimisation level changes. `harness/check.py` prints
this as *"opt/mode variants of this rung disagree (4 distinct behaviours)"*.
That is a sharper demonstration than a single wrong number: the bug is not
"C computes something different", it is "C computes something **unrepeatable**".

⚠ **And it is unrepeatable across *runs*, not just across builds — which means
`results/gate/p05-index-flatten.json` is not a byte-reproducible artefact.**
Two consecutive gate runs at TASK_022 on an unchanged tree gave c-clang
`8302005302491293440` then `4459375280355916544`, and c-gcc
`7290004838690324736` then `2395151758988841216`. **Four leaves of the record
churn on every run** — those two `adversarial.*.stdout` values and the two
`sanitizer.*.diagnostic` strings, which carry the ASan process PID and ASLR
addresses. Anyone diffing two p05 gate records to show that an edit moved
nothing should expect **4 leaves of 567 to move anyway**, and should say which
four; a review that reports "6 leaves moved" after a two-file prose edit has
found 2 real ones.

**p16's R1 walked unboundedly and p17's read backwards; p05's reads forwards and
stops.** `nrow*ncol` is bounded by 2^32, so the walk always terminates — it just
terminates outside the allocation. ASan says `0 bytes after` the region, which is
p16's message, not p17's `bytes before`.

Every checked rung — R1h included — returns `0` on every adversarial input, and
`model.py` predicts `0`. So `adversarial-*` is checksum-clean across seven of the
eight cells and only R1 diverges, which is the shape `.memory/02-bench-rules.md`
asks for.

---

## 8. The trusted base

**TCB: 6 lines across 3 items.** Every `external_body` item is counted, not just
the interesting one (`.memory/04-verus.md`: the pilot was published as "one
3-line wrapper" and the true tally was three items, one of which was `main`).

| item | lines in body | contains `unsafe` | `ensures` | why it is trusted |
|---|---:|---|---|---|
| `get_unchecked` | 1 | **yes** | `r == v@[i as int]` | vstd ships no spec for `<[T]>::get_unchecked` |
| `load_input` | 4 | no | none | file I/O and argv are not verifiable |
| `emit` | 1 | no | none | `println!` is not verifiable |

`main` is **not** `external_body` — `./verus_run.py verus.rs --verify-function
main --verify-root` reports `5 verified`, so the kernel's precondition is
discharged at a real, verified call site (`.memory/02-bench-rules.md` rule 2).
`harness/check.py` 5a confirms: *"3 TCB items, all contracts identical to
spec.md"*, and *"scanned for `unsafe` outside a trusted body: ['verus.rs'] +
['common/driver.rs'] (1 token(s) inside a trusted body)"*.

Only `get_unchecked` is inside the twin regime (`external_body` + a non-empty
`ensures` or `unsafe`), so it is the only item with a twin and the only one with
an `SLB-TRUSTED-ARGUMENT` block.

### The twin is idle again — for the fourth pattern running

`.memory/04-verus.md` predicted the verified twin's value would "accrue from p17
on"; that was corrected at TASK_011 to "from the first pattern needing a
**multi-clause** trusted accessor", which is a property of the *intrinsic being
wrapped* and not of the pattern number. **p05 wraps the same single-clause
`<[u8]>::get_unchecked` that p01, p02, p16 and p17 wrap, so its twin is idle
too**, and a green 5c-twin here is not evidence that anything hard was checked.

It is not *nothing*: §5b's M2 shows the twin is the only **Verus-level**
mechanism that catches `i <= v@.len()`, and the gate re-runs that deletion probe
every time. But that is the same demonstration p01 could have given.

⚠ **CORRECTED AT TASK_056: this sentence used to read *"the twin is the only
mechanism that catches `i <= v@.len()`"*, and this file CONTRADICTED ITSELF** —
§10, about twenty lines of prose further on, prints the two `[proof-pin]` FAILs
that the sentence denies, and gets it right. `spec.md`'s `verus.items` pins the
clause text of **`slb_twin_get_unchecked` as well as `get_unchecked`**, so M2
moves **two** pinned clauses and fails stage 5a, which runs **before** 5c-twin.
Re-measured at TASK_056 by re-running this file's own §5b generator and putting
the mutant through `harness/limbs.py`:

```
=== verus.rs                shipped 12/0   twin 13/0   NO LIMB FIRES
=== verus_m2_offbyone.rs    shipped 12/0   twin 12/1
      [5a-clause] get_unchecked.requires          ['i <= v@.len()'] != pinned ['i < v@.len()']
      [5a-clause] slb_twin_get_unchecked.requires ['i <= v@.len()'] != pinned ['i < v@.len()']
      [5ct-run]   --cfg slb_twin: 12 verified, 1 errors
                  error: precondition not met: index in bounds for this access
```

The rule (TASK_054, TASK_056, six patterns): **the twin is the sole catcher only
of a mutant that edits `spec.md` in the same commit.** §10's phrasing — *"the
twin is the only mechanism that would still object if the pin had been edited in
the same commit"* — is the correct form and was already in this file. **The
`identity` pin does not move**: a `requires` is ghost (measured on p12 at
TASK_054 and p03 at TASK_056, byte-identical kernels from equal-length paths).
An exec-code edit — M1, the deleted size check — can move it. Manufacturing a multi-clause
accessor for p05 would be gaming the gate, and p05's index arithmetic — a
product of two attacker `u16`s — does not need one: the precondition it must
discharge is still exactly "the index is below the length".

The mechanism first earns its keep at the raw-pointer families, p27+.

### SLB-TRUSTED-ARGUMENT verus.rs get_unchecked

**(a) Is the twin's body the right checked stand-in for the unchecked
operation?** Yes. The trusted body is `unsafe { *v.get_unchecked(i) }` and the
twin's is `v[i]`. These are the *same* operation modulo the check: the standard
library documents `get_unchecked(i)` as equivalent to `*v.get(i).unwrap_unchecked()`
and states that calling it with `i >= len` is undefined behaviour, so `v[i]` is
its checked counterpart by construction and not by resemblance. The twin does
not reach for `get_unchecked` itself (which would re-use the axiom it exists to
check), does not loop, and is not empty — the three toothless shapes
`.memory/04-verus.md` enumerates. The gate re-derives the substantive half every
run: with `i < v@.len()` deleted from the trusted item's `requires`, the twin
fails at `12 verified, 1 errors`, so the checked implementation genuinely needs
the conjunct rather than merely coexisting with it.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes, and the body is one expression, which is the only reason
this can be asserted rather than argued. `unsafe { *v.get_unchecked(i) }`
performs exactly one unchecked operation — a single-byte read at index `i` — and
the postcondition `r == v@[i as int]` names exactly that byte. There is no
second read, no write, no aliasing obligation, no arithmetic on `i` inside the
body, and no interior mutability (`&[u8]`). This is the blind spot TASK_009_REVIEW
demonstrated with `let _peek = *v.get_unchecked(i + 1)`, which passes the
contract pin, the twin and the `--cfg slb_twin` run unchanged because nothing in
the `ensures` mentions the extra read; the defence here is that the body is one
line long and a reviewer can see all of it at once, plus Miri on R4 across all
six inputs (§9), plus stage 3c byte-identity, which catches R5-only drift. p05
raises the stakes on this specifically: the index handed to this accessor is
`off + 4 + i*ncol + j`, a *product* of two attacker-controlled `u16`s, so an
off-by-one in the trusted contract would not show up as a small constant shift
the way p16's and p17's would — it would scale with `ncol`. That argues for
re-reading these three lines, not for a different mechanism.

**(c) Does each clause mean the same thing in the shipped configuration as in
the twin's?** Yes, and it is checked mechanically rather than asserted. The only
`#[cfg]` in `verus.rs` is the twin's own `#[cfg(slb_twin)]`, and gate stage
5c-twin verifies this before it runs Verus at all: *"the token `slb_twin` occurs
nowhere but on the 1 twin `#[cfg(slb_twin)]` attribute(s), so the shipped
configuration and the `--cfg slb_twin` one differ in nothing but the twin items
themselves"*. That closes TASK_009_REVIEW's `#[cfg]`-varying-`const` bypass,
where `requires in_bounds(v, i)` meant `i < len + 0` in one configuration and
`i < len + 1` in the other. Both clauses here are also literal — `i < v@.len()`
and `r == v@[i as int]` — with no named constant, no macro and no `const fn` in
either, so there is nothing for a configuration to change even if one could.
The obligation counts are pinned in **both** configurations (12 and 13), so an
item that exists only under the cfg, or a twin that quietly lost its body, moves
a pinned number.

---

## 9. Miri, identity, and the gate

**R4 ≡ R5, byte-identical at `-O3`.** `md5_fn = 4a28657ae7e4` for both, `md5_raw`
equal too, 87/83 instructions each, 10 bytes of padding each. At `O0` the level
is `norel` — the crate names differ in length so call displacements differ, which
is link layout and not codegen (`.memory/03-measurement.md`). **This is the first
time in this project that the byte-identity result covers a *vectorised* kernel**
— a vector body, a scalar epilogue and a nonlinear proof, all erasing to nothing.

**Miri: 6 of 6 inputs, no UB.** Required because the pattern has a trusted item,
not because R4 ≠ R5 (`.memory/02-bench-rules.md`, changed at TASK_010). The cost
is 4 iterations × `nrow*ncol` bytes, at most 15 860 against a ~3 M budget, so
nothing blocks — which is an `inputs/gen.py` decision made before the build, per
`.memory/05-layout.md` demand 8.

**`harness/check.py p05`: complete green run**, 32/32 cells, 37 024 kernel calls
with the `requires` evaluated on every one and the `ensures` re-derived
independently on 280. §10 has the transcript.

**`harness/measure.py p05` was run twice, on different cores (cpu 3 and cpu 5),
and every one of the 42 `kernel_exclusive_ir` figures is identical** — 43 250 000
/ 110 448 000 for c-gcc, 34 175 000 / 101 064 000 for c-clang and unsafe and
verus, and so on down the table. That is the reproducibility claim
`.memory/03-measurement.md` asks for, made rather than assumed. The wall-clock
column is not identical between the two runs and is not expected to be: the
second run discarded three `small.bin` cells at 11.8–19.9% spread where the
first discarded one, which is why §4 does not use `small.bin` and why the
per-call figures there come from an `n_iters` difference rather than from this
table.

The `Ir` floor: derived, 124.5 (small) / 992.2 (large) Ir per call from
`work_per_call = stride` × the harness default 0.25, with measured marginal Ir
1380 … 235 040 over 64 cell/probe pairs — *"tightest margin 8.5×"*, i.e. this
stage tolerates an 88% loss of work before it objects. `model.py` declares no
`min_ir_per_work`, and §2a is the justification: the achieved rate is 1.375
(LLVM) / 1.0625 (gcc) Ir per byte in the vector body alone, 4.2× the floor at
worst. **That argument had to be made differently from p16's and p17's**, which
could say "the fold is a serial Horner chain, so no vector form could undercut
the default". p05's *does* vectorise, so the argument is about the width
actually reachable at these flags — an AVX-512 `vpsadbw` form would do 64 bytes
in ~4 instructions (0.0625 Ir/byte, p02's declared floor) and would need a
declaration, but `harness/build.py` passes no `-march` so no rung can get there.

---

## 10. Gate transcript, and the two mutants run through it

Shipped tree:

```
== verdict ===========================================================
    results -> results/gate/p05-index-flatten.json
    note: adversarial-dims.bin/c-gcc: opt/mode variants of this rung disagree (4 distinct behaviours)
    note: adversarial-dims.bin/c-clang: opt/mode variants of this rung disagree (4 distinct behaviours)
check.py: PASS
```

Mutants swapped into `patterns/p05-index-flatten/verus.rs`, gate run, tree
restored (`--no-callgrind`, so the verdict is `PARTIAL` and the run writes
`*.partial.json` rather than clobbering the full record; the `[collapse-ir]`
failure in both logs is that flag, not the mutant).

- **M2** (`i <= v@.len()` on the item *and* its twin — the "too weak by one"
  shape `.memory/04-verus.md` calls the most dangerous hole in the project).
  **Verus alone is happy: stage 5a prints `12 verified, 0 errors`, stage 5c
  finds every `ensures` conjunct load-bearing, and stage 5c-req reports the
  weakened conjunct is "not a tautology".** Three of the four checks pass it.
  What fails:

  ```
  FAIL [proof-pin] verus.rs:183 `get_unchecked` drifted from spec.md --
      requires: ['i <= v@.len()'] != pinned ['i < v@.len()']
  FAIL [proof-pin] verus.rs:215 `slb_twin_get_unchecked` drifted from spec.md --
      requires: ['i <= v@.len()'] != pinned ['i < v@.len()']
  FAIL [twin] verus.rs: with `--cfg slb_twin` Verus reports 12 verified, 1 errors
      (12 verified without the twins). At least one trusted precondition is not
      strong enough to license the checked equivalent ...
    error: precondition not met: index in bounds for this access
       --> patterns/p05-index-flatten/verus.rs:222:5
        |
    222 |     v[i]
  ```

  The `spec.md` pin catches it because the mutation is a source diff a reviewer
  can read; **the twin catches it semantically**, and the twin is the only
  mechanism that would still object if the pin had been edited in the same
  commit — which is exactly the self-certification failure TASK_003_REVIEW
  demonstrated. 5c-req's own log line says so in as many words: *"this stage
  judges TRIVIALITY, not STRENGTH — `i <= v@.len()` is not a tautology and is
  still one byte past the end."*

- **M3** (`ensures r == r`) — 8 failures, and note that the *first* four are
  build failures, because `verus_run.py --compile` refuses a file Verus reports
  errors on, so the cell cannot even be produced:

  ```
  FAIL [build] verus O0 isolated / O0 whole / O3 isolated / O3 whole
  FAIL [proof-pin]    verus.rs:252 `kernel` drifted from spec.md --
      ensures: ['r == r'] != pinned ['r == grid_fold(buf@, off as int, len as int)']
  FAIL [proof-verify] verus.rs: 11 verified, 1 errors
  FAIL [proof-rule2]  `verus --verify-function main` reports 4 verified
  FAIL [clause-mut]   the UNMUTATED copy does not verify (11 verified, 1 errors)
  FAIL [req-mut]      ...same
  ```

  The `[proof-verify]` failure is the driver's consuming `assert` — deleting the
  postcondition's content leaves the ghost line that consumes it unprovable,
  which is precisely why `.memory/04-verus.md` requires that line.

The full logs are `.temp/p05/gate-m2.log` and `.temp/p05/gate-m3.log`. The
shipped `verus.rs` was restored afterwards and re-verified by md5
(`66f680af12cf7afc98ceb43ef67649be`).

---

## 11. What is *not* claimed, and what is left open

- **No claim rests on an `O0` row**, and none on `small.bin`'s wall clock
  (§4, 13.8% spread, discarded and printed).
- **The `u32` row accumulator is a deviation from the commissioning spec**, made
  on the measurement in §1 and flagged in `spec.md`, `c/kernel.c` and every Rust
  rung. Everything the task marked load-bearing is intact. If the manager would
  rather have the `u64` form, the honest result from it is "gcc vectorises, LLVM
  does not, at these flags" and nothing about safety.
- **The 4.2500 Ir/element vectorisation-off control changes both sides at once.**
  p16's rolled control was better in one respect: `-unroll-count=1` was a
  bit-for-bit no-op on R2, so only one side moved. Here every rung vectorises, so
  disabling it moves all of them; the comparison is still controlled (same
  source, same flag, verified same checksum, verified `vector_regs=[]`) but it is
  not a one-sided perturbation and should not be described as one.
- ~~**`f(0) = 84` is measured, not explained.**~~ **Superseded — it was explained
  at TASK_013_REVIEW**, by `mov $0x8,%r11d ; cmove %r11,%r8` forcing a remainder
  of zero to a full vector width. §12a.
- **No hardware counters.** The +32.9% time against +34.4% `Ir` is consistent
  with an issue-limited loop, but IPC, branch misses and cache misses are
  unmeasurable on this box (`perf` absent, `perf_event_paranoid=3`, no root) and
  are not estimated.
- **`work_per_call` is still an author-written knob**, over-stating by exactly
  the 4 header bytes here; the floor's 8.5× margin means the stage tolerates an
  88% loss of work. §9, and `.memory/02-bench-rules.md`'s standing residual.

---

## 12. The two reviews, and the R3 audit — what this pattern's numbers actually price

This section exists because the headline above was corrected twice, both times
by measurement, and both times the correction was about **which spelling** was
measured rather than about the measuring. §1–§11 are unchanged and every number
in them still reproduces; what changes is what they are evidence *for*.

### 12a. TASK_013_REVIEW — the mechanism, and the model with no fitted parameters

- **Where the check went.** Hoisted into a **22-instruction per-row trip-count
  computation** (a `cmova`/`cmovb` min-max chain computing
  `N = min(ncol, len − rowbase)`) and **surviving in the scalar epilogue** at
  8 Ir/element against R4's 5. "Per element" in §2 is a marginal derivative, not
  an average; the average gap on shipped inputs is ~34%.
- **`f(0) = 84` is explained** — §11's "measured, not explained" is superseded:
  `mov $0x8,%r11d ; cmove %r11,%r8` forces a **remainder of zero to a full vector
  width**, because R2's loop is multi-exit and must keep a scalar epilogue.
  `84 = 29 + 64 − 11 + 2`. Every power-of-two `ncol` pays a vector iteration it
  does not need.
- **Zero fitted parameters**, derived from the listings:
  `R4 = 37 + nrow·(27+11q+5r)`, `R3 = 46 + nrow·(33+11q+5r)`,
  `R2 = 72 + nrow·(56+11V+8e)`, reproducing every measured point to the
  instruction. Domain `ncol > 8`.
- **Wall clock: +34.4% Ir → +32.9% time**, not the delivered +30.5%.

### 12b. TASK_014_REVIEW — `chunks_exact` beats the *unsafe* rung, and the retraction

`safe_tuned.rs`'s inner loop replaced by `data.chunks_exact(ncol)`, one
substitution, nothing else touched. `-O3 isolated`, marginal Ir per call
(callgrind, `n_iters` 100 → 200):

| input (nrow×ncol) | R2 | R3 shipped | **R4 unsafe** | **chunks_exact** | chunks − R4 |
|---|---:|---:|---:|---:|---:|
| `small` 19×26 | 2081.00 | 1504.00 | **1381.00** | **1369.00** | **−12.00** |
| `large` 65×61 | 11330.70 | 8834.70 | **8435.70** | **8377.70** | **−58.00** |
| `sweep-r19c24` (≡0 mod 8) | 2784.30 | 1276.30 | 1153.30 | 1141.30 | −12.00 |
| `sweep-r19c25` | 1929.30 | 1409.30 | 1286.30 | 1274.30 | −12.00 |
| `sweep-r41c32` | 6359.41 | 3135.41 | 2880.41 | 2846.41 | −34.00 |
| `sweep-r65c64` | 12891.00 | 7795.00 | 7396.00 | 7338.00 | −58.00 |
| `sweep-r65c65` | 9966.30 | 8250.30 | 7851.30 | 7793.30 | −58.00 |

`chunks − R4 = −(nrow − 7)` exactly, both residue classes; `R3 − R4 = 6·nrow + 9`.
Identical stdout and exit against R4 on **all 150 committed inputs**.
**Every one of these figures was re-measured independently at TASK_015 and
reproduced to the hundredth.**

Mechanism, from the listing: `chunks_exact` hands each row a slice whose length
**is** `ncol` by construction, so R4's *two* row-base registers (`%r11` for the
vector body at `+8`, `%rdx` for the scalar epilogue, both advanced by `ncol`
every row — `add %r9,%r11 ; add %r9,%rdx`) collapse to **one** pointer
(`add %r11,%rdi`). That single `add` per row *is* the `−1·nrow` slope. Against
**R2** the change is larger: R2's five `cmov`s go to zero, the `cmp $0x9` vector
guard and the residue `cmove` disappear, and the epilogue becomes R4's unchecked
5-instruction body. Static, `nm --print-size` extent / objdump grouping:
R2 168/171, R3 shipped 111/125, chunks 105/109, R4 87/97 — `cmov` count
**5 / 0 / 0 / 0**, i.e. the five are R2's alone.

**What is retracted.** "R3 is not free here" and "the `29 + 3r` per row is the
price of the optimiser failing the lemma the proof proves" — the second of
which is **partially reinstated**, restricted to the `O(nrow)` term, at
TASK_021_REVIEW; §1 carries the reinstated sentence in its exact words and §14g
the instruction-by-instruction count behind it. What **survives**
unchanged: the `1.375000` steady state; the `29 + 3r` model *as a model of R2 and
of the shipped spelling*; the AVX2 result; the `f(0) = 84` mechanism; and the
nonlinearity claim **as a statement about the obligation**, which the review
confirmed with a linearisation counterfactual (`probe2.rs`: 5 `cmov` → 0,
166 → 125 instructions, unchecked epilogue). Two caveats on that counterfactual,
both measured: it does **not** survive the shipped binary build — LLVM's
induction-variable simplification re-derives `i*ncol` and the linearised R2
measures **2366 Ir/call against R2's 2081**, *worse* — and `chunks_exact` makes
the question moot, since a spelling with no lemma at all beats R4.

### 12c. TASK_015 — the audit: a third spelling, and the control that reframes it

`.memory/01-ladder.md`'s corollary rule is *write at least two independent R3
spellings and quote the cheaper*. Three were written. Marginal Ir/call,
`-O3 isolated`, same method:

| spelling | vs R4, as a function of `nrow` | small | large |
|---|---|---:|---:|
| R2 indexed `buf[off+4+i*ncol+j]` | `+35 + nrow·(29+3r)` | +700 | +2895 |
| R3 shipped, hand-resliced `buf[base..base+ncol]` | `+6·nrow + 9` | +123 | +399 |
| `split_at(ncol)` on a consumed cursor | `+nrow + 7` | +26 | +72 |
| **`chunks_exact(ncol)`** | **`−nrow + 7`** | **−12** | **−58** |

So consuming the slice by hand recovers `5·nrow + 2` of the shipped spelling's
`6·nrow + 9`, and `chunks_exact` takes the last row-scaled instruction as well.
The spread **across four safe spellings of one kernel is larger than the spread
between safe and unsafe**, which is the transferable point.

**The control that must ship with "safe Rust beat unsafe Rust", because it
reframes it.** R4's spelling is not optimal either: it indexes `buf` flat, which
is what forces the two row bases. `.temp/p05r3/v05/unsafe_consume.rs` is shipped
R4 verbatim except that it advances one row pointer by `ncol` — exactly what
`chunks_exact` gives the safe rung for free. Same checksum on all 150 inputs.

| input | R4 shipped | R3 `chunks_exact` | **R4′ same idiom** | R3 − R4′ |
|---|---:|---:|---:|---:|
| `small` 19×26 | 1381.00 | 1369.00 | **1358.00** | **+11.00** |
| `large` 65×61 | 8435.70 | 8377.70 | **8366.70** | **+11.00** |
| `sweep-r41c32` | 2880.41 | 2846.41 | **2835.41** | **+11.00** |

~~**Unsafe goes back on top the moment both rungs are written the same way, and
the residual safety tax is +11.00 Ir per call, flat in `nrow`** — nrow 19, 41 and
65 all give exactly +11, i.e. `O(1)` per call, not `O(nrow)`. That is p05's
honest safety number: *when the safe and unsafe rungs use the same addressing
idiom, safety costs eleven instructions per call on a vectorised 2-D fold*.~~

**Retracted at TASK_015_REVIEW (B1), twice over, and the table above is not what
is wrong with it.** The **+11.00 reproduces exactly** — swept over all 144
committed blobs, every `ncol` residue, min = max = mean — and so does every
other figure in this section. What does not survive is the conclusion. (a) One
more unsafe round, replacing the `i < nrow` counter with the canonical C test
`while rp < end`, removes one instruction per row and the gap reopens as
**`nrow + 9`**, `O(nrow)` again; a second, textually unrelated unsafe spelling
lands on the identical number. (b) Both rungs in the +11 pair are **excluded by
this pattern's own contract** — `spec.md`'s `idiom` key forbids `chunks_exact`
and the running row pointer by name, and has since TASK_013 — so +11 is a real
number for a kernel that is not p05. §13 is the full spread with the
contract-conformant cells marked; the sentence that replaces this one is
*"idiom-matched safety has no fixed point, and p05's contract-relative cost is
`6·nrow + 9`"* — **and that figure is the shipped pair's, not a bound on the
in-contract tax. §14 respells both rungs inside the declaration and gets an
interval, not a number.**

**And `chunks_exact`'s `Ir` win does not convert to time — there is a `div`.**
`ChunksExact::new` computes `len − len % chunk_size`, and with a runtime `ncol`
that is a real `div %r11d`, once per kernel call, in the prologue:

```
mov %r8d,%eax ; xor %edx,%edx ; div %r11d ; mov %r8,%rax ; sub %rdx,%rax
```

**Callgrind counts a `div` as 1 Ir; the hardware does not.** Interleaved wall
clock (`taskset -c 3`, 31 reps, differenced `n_iters` 25 000 → 75 000 on `small`,
12 000 → 36 000 on `large`, min ns/call):

| cell | small | vs R4 | large | vs R4 |
|---|---:|---:|---:|---:|
| R4 shipped | 84.80 | +0.00% | 546.82 | +0.00% |
| R3 shipped | 92.56 | +9.16% | 543.79 | −0.55% |
| R3 `chunks_exact` | 85.20 | **+0.47%** | 539.89 | −1.27% |
| R4′ consuming | 83.97 | −0.97% | 551.07 | +0.78% |
| R2 safe-naive | 136.89 | +61.43% | 723.33 | +32.28% |

On `small`, `Ir` says `chunks_exact` is **−0.87%** against R4 and ns says
**+0.47%**; its min-to-median spread is **8.61%**, the worst of the five and the
only one near the 10% discard threshold, which is what a variable-latency `div`
looks like. `large` (8.4 MB payload, memory-bound) resolves nothing: every Rust
rung but R2 is inside ±1.3% at 1–2% spreads. **So the `−(nrow − 7)` is a real
instruction-count result and must not be quoted as a time result.** R3 shipped's
`+9.16%` on `small` against `+8.91%` in `Ir` *does* convert, and R2's `+61.43%`
against `+50.7%` converts and then some — the direction-of-conversion claim in §4
is unaffected.

### 12d. Why the shipped R3 is still the shipped R3

`safe_tuned.rs` was **not** replaced with `chunks_exact` at TASK_015, and the
reason is measured rather than editorial:

1. The audit found the *same* defect in p16's and p17's R3 (both beaten, both by
   spellings that also beat their own R4). Swapping p05 alone would make one
   pattern "best-found" and two "first plausible" inside one result set.
2. The R4′ control above says the ordering a swap would publish — safe beats
   unsafe — is an idiom mismatch, not a language fact. Landing it as a cell would
   install a headline that a ten-line control refutes.
3. `chunks_exact`'s advantage is `Ir`-only on `small` (the `div`).
4. `safe_tuned.rs` is load-bearing as this pattern's **decomposition control**:
   it differs from R2 in the inner loop and in nothing else, so `R2 − R3` *is*
   the per-element check cost by construction (§3), which is the rule
   `.memory/01-ladder.md` finding 4 imposes. `chunks_exact` changes the header
   handling, the row addressing and the trip count at once.

What the file therefore claims is the honest form: ~~**§2's R3 column is the cost
of one spelling, this section has three more, and the idiom-matched safe-vs-unsafe
number is +11 Ir per call, flat.**~~ — corrected at TASK_015_REVIEW and TASK_016:
**§2's R3 column is the cost of one spelling, §13 has ten more, and the only
number p05 may headline is the matched pair under the `idiom` block
`spec.md` has declared since TASK_013 — `R3 − R4 = 6·nrow + 9`.** There is no
idiom-matched number outside that declaration, because "same idiom" has no fixed
point: see §13.

**Amended at TASK_021, corrected at TASK_021_REVIEW and corrected again at
TASK_022: that pair is the shipped pair's number, and there is no measured
in-contract minimum to set beside it.** The declaration makes the admissible
class *decidable*, not *singular* (`.memory/01-ladder.md`), and inside it the
shipped R3 is beaten under both readings of `required[1]` — the cheapest R3
found is `5·nrow + 6` against the shipped R4, by seven independent spellings.
~~The R4 side moves too, which TASK_021 reported it did not: **46 in-contract
unsafe spellings over three rounds**, and the cheapest found is **7 Ir/call
flat below the shipped R4**, zero residual on 179 points.~~ **Corrected again at
TASK_028: the R4 side does NOT move.** All 46 spellings were searched and
measured, but every one that moves respells the header read or uses
`from_raw_parts`, and p05's `identity: unsafe ≡ verus, O3 exact` pin admits
neither at the pinned vstd — so the `−7` is a control and not a rung. TASK_021's
conclusion was right for the wrong reason. §14.

## 13. The spelling spread — eleven spellings of one kernel, and which two are p05

**Not the headline.** This section is a result *about method*, published because
the spread is wider than the thing the pattern measures. The number p05
publishes is the matched pair under the idiom `spec.md` declares —
**R3 `safe_tuned.rs` − R4 `unsafe.rs` = `6·nrow + 9`** — and every other row
below is a measurement of a *different* kernel, kept here so nobody re-derives
one and reports it as p05's.

**And that published pair is one point inside an in-contract span — §14 is the
in-contract spread.** This section's rows are out of contract; §14's are in it,
and what a safety claim about p05 has to be made against is the **R3-side
span** with the unsafe rung held at the shipped cell — `5·nrow + 6` …
`6·nrow + 13`, 101 … 127 at `small` and 331 … 403 at `large` (§14h.3) — and not
a single number, because §14 has no measured minimum to offer.
(Until TASK_028 this paragraph quoted a *pair* interval, `2·nrow − 2` …
`6·nrow + 20` = 36 … 134 / 128 … 410. **Withdrawn**: both endpoints were R4
spellings that the `identity` pin excludes, so they are not rungs. §14's head ⚠.)

Mandatory for every pattern that has spellings, from TASK_016 on. Method:
marginal `Ir` per kernel call = (whole-program `Ir` at `n_iters` 200 − at 100)
÷ 100, `-O3 isolated` — §2's method, and the same probe `harness/check.py`
step 3b uses. **The three shipped rows below are the gate's own numbers** —
`results/gate/p05-index-flatten.json`'s `marginal_ir_per_call` reads 2081.0 /
1504.0 / 1381.0 on `small` and 11330.7 / 8834.7 / 8435.7 on `large`, so this
table can be checked against a committed artefact without rebuilding anything.
The variant sources are under `.temp/p05r3/v05/` and `.temp/review015/v05/`;
**none of them is a p05 cell and none may be landed as one.**

`small` = 19×26, `large` = 65×61.

| # | rung | spelling | file | small | large | − R4 shipped |
|---|---|---|---|---:|---:|---|
| 1 | R2 | indexed `buf[off+4+i*ncol+j]` | **`safe_naive.rs` (shipped, IN CONTRACT)** | 2081.00 | 11330.70 | `+35 + nrow·(29+3r)` |
| 2 | R3 | hand-reslice `buf[base..base+ncol]` | **`safe_tuned.rs` (shipped, IN CONTRACT)** | **1504.00** | **8834.70** | **`+6·nrow + 9`** |
| 3 | R3 | index cursor into `data` | `t4_idx.rs` | 1446.00 | 8638.70 | +65 / +203 |
| 4 | R3 | `split_at(ncol)` on a consumed cursor | `tuned_splitat.rs` | 1407.00 | 8507.70 | `+nrow + 7` |
| 5 | R3 | `ChunksExact::fold` | `t3_fold.rs` | 1388.00 | 8442.70 | +7 / +7 |
| 6 | R3 | `chunks_exact(ncol)` for-loop | `tuned_chunks.rs` | 1369.00 | 8377.70 | `−(nrow − 7)` |
| 7 | R3 | `split_at_checked` while-let | `t2_splitchk.rs` | **1365.00** | **8373.70** | `−(nrow − 3)` |
| 8 | R4 | `get_unchecked` flat index | **`unsafe.rs` (shipped, IN CONTRACT)** | **1381.00** | **8435.70** | **0** |
| 9 | R4 | row pointer + `i < nrow` counter | `unsafe_consume.rs` | 1358.00 | 8366.70 | `−(nrow + 4)` |
| 10 | R4 | row pointer, `while rp < end` | `u2_end.rs` | **1337.00** | **8299.70** | `−(2·nrow + 6)` |
| 11 | R4 | `from_raw_parts` per row | `u2_rawslice.rs` | **1337.00** | **8299.70** | `−(2·nrow + 6)` |

Rows 2 and 8 are the pair. Rows 1, 2 and 8 are the only three that satisfy
`spec.md`'s `idiom`: every other row either consumes the slice (3–7) or carries a
strength-reduced running row pointer (9–11), and both are forbidden **by name**
because they delete the `i*ncol + j` multiply that *is* the pattern.

**The spread, and why it is the finding.**

| | range | width |
|---|---|---|
| safe spellings (rows 1–7) | 1365.00 … 2081.00 | **716 Ir = 52% of the cheapest** |
| unsafe spellings (rows 8–11) | 1337.00 … 1381.00 | **44 Ir = 3.3% of the cheapest** |
| the contract-conformant pair (2 − 8) | +123 on `small`, +399 on `large` | `6·nrow + 9` |
| the best out-of-contract pair (7 − 10) | +28 on `small`, +74 on `large` | `nrow + 9` |

Three things follow, and only the first two are about p05.

1. **The safe side is 16× more spelling-sensitive than the unsafe side.** That
   asymmetry is itself publishable and it is not what anyone predicted: the
   received story is that unsafe code is where the tuning lives.
2. **"Same idiom" has no fixed point, so a spread cannot be repaired into a
   number.** Rows 6 and 9 were idiom-matched under TASK_015's own criterion
   ("consume the slice / carry a row base"); row 10 satisfies that criterion too
   and is `nrow + 2` cheaper; row 11 is the *safe* program of row 6 with only its
   checked slice constructions replaced — the most matched unsafe rung it is
   possible to write — and lands on row 10's number to the instruction. The class
   picked out by "same idiom" has members differing by `O(nrow)`.
3. **And a published spread cannot carry a safety claim at all**, which is why
   this section is method and not result: R4 is defined by *permission* rather
   than obligation (`.memory/01-ladder.md`), so every safe program is an
   admissible R4, `inf(R4) ≤ inf(R3)` **by construction**, and the two intervals
   above always overlap with the unsafe one extending lower. That is a theorem,
   not a measurement. Only a matched-pair delta under a *declared* idiom carries
   a safety number — hence the `idiom` key.

**Provenance.** Rows 1, 2, 4, 6, 8, 9 are TASK_015's (`.temp/p05r3/v05/`);
rows 3, 5, 7, 10 and 11 are TASK_015_REVIEW's (`.temp/review015/v05/`). Rows 7,
10, 11 and the
`−(nrow − 3)` / `−(2·nrow + 6)` laws are TASK_015_REVIEW's, swept over **all 144
committed sweep blobs** with zero residual. Rows 3 and 5 were quoted on `small`
only until TASK_016, which measured their `large` column here (`.temp/p16idiom/`)
— so their `− R4` entries are **two-point interpolations, not swept laws**, and
row 3's apparent `3·nrow + 8` in particular has not been checked against a single
other point. Two points cannot distinguish a slope from a residue; this project
has stepped in that trap three times. The controls re-measured in the same
session reproduce exactly (R3 shipped 1504.00 / 8834.70, R4 shipped 1381.00 /
8435.70).

Equivalence: all eleven print the shipped R4 binary's checksum and exit code on
**all 150 committed inputs** — this is a spelling spread, not an algorithm
spread. `.temp/review015/equiv.py`.

**Row 3 is out of contract for the wrong reason, corrected at TASK_021.** The
table above files `t4_idx.rs` under "consumes the slice". It does not consume
anything: it reslices `data[b..b + ncol]` exactly as the shipped R3 does, and
what puts it out is the line below that — `b += ncol`, a running row *index*,
which is `forbidden[1]`'s strength reduction with a `usize` in place of a
pointer. The **verdict** is unchanged (row 3 is out), only the reason. It
matters because it is the one row whose exclusion a reader could otherwise not
reproduce from the source, and because §14 measures what an in-contract
data-relative base actually costs — it is `nrow` *cheaper* than shipped R3, not
`3·nrow + 8` cheaper, so row 3's saving is the strength reduction and not the
reslice.

## 14. The **in-contract** spelling spread (TASK_021, corrected at TASK_021_REVIEW and TASK_022; **the R4 half withdrawn at TASK_028**)

> ⚠ **READ THIS FIRST — the R4 side of this section is measured, was published,
> and is not made of rungs** (TASK_027_REVIEW, seven Verus twins; landed at
> TASK_028).
>
> p05 pins `identity: unsafe ≡ verus, O3 exact`, so an R4 is not merely a
> program that *may* use `unsafe` — **it is a program that must have a
> byte-identical R5 twin that Verus verifies.** Every R4 variant below that
> moves off the shipped cell respells the **header read**, and at the pinned
> vstd every route to that respelling is `is not supported`: `read_unaligned`,
> `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError`, `from_le_bytes`.
> `c4_hu16_nz` (the `−7`) verifies only with **one new trusted item** — exactly
> the cost that disqualified `r4_hdr` on p16 — and `r4_dataslice`
> (the `+3·nrow + 8`) fails on `from_raw_parts`.
>
> **So `−7` and `+3·nrow + 8` are control measurements, not rung measurements,
> and p05's R4 side has never moved by a single admissible instruction.** The
> rows stay: this project's files record refutations, they do not erase them.
> Read them as controls.
>
> **What that costs, inside this section:** §14f's title is wrong; §14h.3's pair
> interval is withdrawn at *both* endpoints; §14h.3's "the bottom is exactly
> zero at `nrow = 1`" free pairing is withdrawn; and the `−7` = `−5` + `−2`
> decomposition is an inference over an inadmissible family whose `−2` half has
> never been compiled. **What survives untouched is the whole R3 side**, which
> holds the unsafe rung at the shipped cell and therefore cannot be moved by any
> of this.

§13 is eleven spellings of this kernel and it answers *"how wide is the spread?"*.
It cannot answer **"is the shipped R3 the cheapest *admissible* one?"**, because
nine of its eleven rows are out of contract and the two that are in it are the
shipped pair. This section answers that question, on both sides of the pair.

**The answer is no on the R3 side. On the R4 side the question was never
answered at all, because nothing that answered it was a rung. What this section
does *not* have is a minimum**, and the way it learned that is the reason to
read it: **three successive values have been published here as "the measured
in-contract minimum" and every one was overturned by the next search**, each
time by respelling one more thing in the *unsafe* rung's prologue, each time on
the first lever the next agent pulled — and **the second and third revisions are
now known to have been made of controls** (TASK_028).

| published as the minimum | by | R4 spellings searched | at `small` / `large` |
|---|---|---:|---|
| `5·nrow + 6` | TASK_021 | 8 | 101 / 331 |
| `5·nrow + 11` | TASK_021_REVIEW | +20 | 106 / 336 |
| `5·nrow + 13` | TASK_022 | +18 | 108 / 338 |

Each is `min(R3 found) − min(R4 found)`, and that difference **is not a bound
in either direction**: both terms are upper bounds on their own infima, and the
difference of two upper bounds bounds nothing. So this file no longer publishes
one.

**And rows 2 and 3 are worse than unbounded — they are not made of rungs**
(TASK_028). Their `min(R4 found)` is the header-respelling family, which the
`identity` pin excludes. Row 1's `min(R4 found)` *is* the shipped cell, so
`5·nrow + 6` is not a pair minimum at all: it is the cheapest R3 found against a
**fixed** R4, which is exactly item 2 below and is the one figure in the table
that survives. What this file publishes instead:

1. **`R3ship − R4ship = 6·nrow + 9` is exact for the shipped pair**, zero
   residual on all 179 measured points, and that has never moved.
2. **Against the *shipped* R4, the cheapest R3 found costs `5·nrow + 6`** — so
   `6·nrow + 9` overstates *that* pairing by `nrow + 3`, at every `nrow ≥ 1`.
   This one is a genuine one-sided statement: it depends on the R3 search only,
   and three rounds of widening the R4 search have not touched it.
3. **The R3-side span**, cheapest-found to dearest-found in contract with R4
   held at the shipped cell: `5·nrow + 6` … `6·nrow + 13`, **101 … 127 at
   `small`, 331 … 403 at `large`**, width `nrow + 7` = 26 / 72, i.e. 21% / 18%
   of the published figure, which sits inside it. §14h.3.

   ~~**Over in-contract *pairs*, the spread searched runs `2·nrow − 2` …
   `6·nrow + 20`** (36 … 134 / 128 … 410), the published `6·nrow + 9` sits
   *inside* it, and its bottom is **exactly 0 at `nrow = 1`**~~ —
   **WITHDRAWN AT TASK_028, at both endpoints and at the `0.00`.** The bottom
   came from `r4_dataslice` and the top from `c4_hu16_nz`, and neither is a
   rung (the ⚠ at the head of this section). Substituting the admissible class
   gives exactly the R3-side span above, so **this project publishes no pair
   interval on p05** — see §14h.3 for why "degenerate" and not "unavailable" is
   the honest word for it, and `spec.md`'s `idiom.why` for the same statement
   across all six patterns.

   What the withdrawal does **not** touch is the observation this item was
   written for: "upper bound on the in-contract safety tax" — how TASK_021 and
   TASK_021_REVIEW both phrased `6·nrow + 9`, and how `spec.md`'s `idiom.why`
   phrased it for all six patterns until TASK_023 — is still **wrong as
   stated**, because the quantity it bounds is `inf(in-contract R3) − R4ship`
   and nothing wider. **`spec.md` was corrected at TASK_023**, byte-identically
   in all six declarations, and **corrected again at TASK_028**, because
   TASK_023's answer to *is p05 special?* — *"no: p16's unsafe rung moves in
   contract by `4·nrec`"* — rested on `r4_hdr`, which is not a p16 rung either.
   The corrected answer is still **no**, and now for a reason that covers every
   pattern: **no pattern's R4 side has moved by an admissible instruction, and
   the `identity` pin is why.** p17, p02, p01 and p08 remain unsearched on the
   R4 side, and searching them is now a Verus question before it is a
   measurement question.
4. **What survives all three revisions** is the *shape* under the pairing this
   file actually reports — cheapest-found R3 against cheapest-found R4, p16's
   reading of `required[1]`: an `nrow` coefficient of **5**, positive, `O(nrow)`.
   Every revision moved the constant; none moved the coefficient. That is the
   claim `.memory/01-ladder.md` finding 6 rests on, and it is why the finding
   is stated about the `O(nrow)` term and not about the number. **Restricted to
   the admissible class the pairing collapses onto item 2** — cheapest R3 found
   against the shipped R4 — where the law is `5·nrow + 6` and the coefficient
   is the same 5.

For comparison: p16's published `+27/+77` was high by 30%/42%, p17's `+32` had
the **wrong sign**, and p02's `+10` was high by 40%/50%. On the *R3 side alone*
p05's declaration is the tightest of the four — §14a says why, in instructions.
This sentence used to continue *"but once both rungs are respelled that
comparison does not hold up either"*, citing p16's pair interval as wider;
**both intervals are withdrawn** (TASK_028), so there is no cross-pattern
looseness comparison here at all — see §14h.3's ⚠, which had already refused to
re-point it on the separate ground that the searches behind two intervals are
never each other's peers.

### 14a. The machine audit cannot settle p05, and that is a measurement

TASK_021's task file says to run `check.idiom_audit` — the stage-`0b` audit — on
each variant before measuring it. **Run against p05 it reports `spellings = 0`**:

```
$ python3 .temp/p21/audit.py
p05 idiom.forbidden: ['chunks_exact', 'a running row pointer']
BACKTICKED SPELLINGS IN p05's DECLARATION: 0
check.idiom_audit on p05 with a variant substituted: spellings=0 pairs=0
    forbidden_hits=0 pins_nothing=0 no_rung=0
  => the machine audit decides NOTHING on p05.
```

p05's four `required` entries and two `forbidden` entries carry **no backticks
at all**, so the named-spelling standard's own trigger — *"where a `required`
entry quotes an expression in backticks it pins THAT SPELLING"* — never fires
here. `spec.md`'s `idiom.why` already says so (*"`required` in p01 and p05
contains no backticks at all, so those two patterns pin no token"*), and
`.memory/01-ladder.md` records it; what is new is that the audit built to
reproduce the standard now confirms it with a count rather than a reading.

So p05's admission test is **prose plus one grep**, and it was applied that way:

| entry | how it was decided |
|---|---|
| `forbidden[0]` `chunks_exact` | `check.spelling_matches("chunks_exact", src)` — **decidable**, 0 hits on all 29 R3 variants and all 8 R4 variants |
| `forbidden[1]` "a running row pointer" | **not greppable in general.** What is: a variable advanced by `ncol` across outer iterations (`x += ncol`, `x = x + ncol`, `p.add(ncol)`). Zero hits on all 37, and it is the grep that would have caught §13's rows 9–11 and `t4_idx.rs` |
| `required[0]` the multiply is written out | `i*ncol` present in whitespace-deleted exec source — true of all 37 |
| `required[1]` the licensed reslice | **human.** The two readings are separated below rather than resolved |
| `required[2]` fit check, `u32`/`u64` widths | **the *property* is true of all 37; the literal grep is not.** ⚠ |
| `required[3]` `nrow*ncol` folded in | **ditto** ⚠ |

⚠ **Corrected at TASK_021_REVIEW (m3).** These two rows said *"greppable, true
of all 37"*, and that was asserted rather than measured. `r3_ds_cells` — one of
the seven spellings that reach the cheapest R3 found — binds `let cells = nrow *
ncol` and then writes `cells > avail` and `cells as u64`, so whitespace-deleted
`nrow*ncol>avail` **misses** and `(nrow*ncol)asu64` **misses**. Same for
TASK_021_REVIEW's `y4_hptr_cells` and TASK_022's `c4_hu16_nz_cells` and
`c3_ds_nz_cells`. The property holds in all of them — `cells` is bound to
`nrow * ncol` one line earlier — so nothing about the measurement changes; what
was wrong is the claim that a grep had settled it. Six of the seven do pass the
literal grep, which is why the figure does not depend on the reading.

### 14b. The variants, and the two readings of `required[1]`

Sources under `.temp/p21/v05/` (TASK_021), `.temp/review021/v05/`
(TASK_021_REVIEW) and `.temp/p22/v05/` (TASK_022), generated by the `mkvar*.py`
beside each; **none is a p05 cell and none may be landed as one.** Every one is
shipped R3 (or shipped R4) with *one* thing respelled and the driver copied
verbatim, so no variant can differ in the measured loop.

`required[1]` reads *"R3 may reslice `[base .. base+ncol]` with
`base = off + 4 + i*ncol` — that moves the CHECK and keeps the MULTIPLY, and it
is the most a rung may do."* Two readings. **The *qualitative* result does not
depend on which is taken; the *number* does, and §14's opening and
`README.md` both stated it unconditionally until TASK_022** (TASK_021_REVIEW
B2). Which reading is meant has never been decided, and this file does not
decide it.

- **strict** — `base` must be spelled `off + 4 + i * ncol`, so only the header
  read, the slice the reslice indexes, and the fold's surface may move;
- **p16's reading** — the reslice may index a *hoisted sub-slice*, so `base` may
  be window-data-relative (`i * ncol` into `&buf[off+4 .. off+4+nrow*ncol]`).
  This is `r3_endslice`/`r3_window`'s move on p16 (`patterns/p16-tlv-walk/NOTES.md`
  §10a) and `.memory/01-ladder.md`'s R3 definition licenses the hoisted length
  assertion it amounts to. The bytes read are identical; only the origin the
  index is expressed against moves.

**Under both readings the shipped R3 is beaten.** Strictly, by `r3_hdrarray`,
which respells nothing but the header read and is **3 cheaper, flat in `nrow`**,
and — for `nrow > 3` — by `r3_get_h1` at `nrow − 3` (the same reslice written
`buf.get(base..base + ncol)`; at `nrow ≤ 3` that one is *dearer*, and the law is
signed and exact at every point including `nrow = 1`). Under p16's reading, by
`r3_ds_h1` at `nrow + 3`.

So, **against the shipped R4**, the cheapest R3 found is `6·nrow + 6` at
`nrow ≤ 6` and `5·nrow + 12` above it under the strict reading, and
`5·nrow + 6` everywhere under p16's; **the shipped figure is not the cheapest
admissible R3 under either.** That is the one claim in §14 that survived all
three rounds untouched, because it holds the R4 side fixed at the shipped cell.

**Both rungs respelled, the reading is worth 6 instructions**, and neither
figure is a minimum (§14h):

| reading of `required[1]` | cheapest R3 found, vs R4ship | both rungs as cheap as found | `small` / `large` |
|---|---|---|---|
| p16's (hoisted sub-slice) | `5·nrow + 6` | `5·nrow + 13` | 108 / 338 |
| strict (`base = off + 4 + i*ncol`) | `min(6·nrow + 6, 5·nrow + 12)` | `min(6·nrow + 13, 5·nrow + 19)` | 114 / 344 |
| — the published shipped pair — | `6·nrow + 9` | — | 123 / 399 |

### 14c. Provenance: the baselines are the shipped cells

`r3_ship.rs` and `r4_ship.rs` are the shipped kernels rebuilt in this session
with `harness/build.py`'s exact `-O3 isolated` rustc flags
(`--edition 2021 -C codegen-units=1 -C opt-level=3 -C debug-assertions=off
--cfg slb_isolated`). They are **byte-identical** to the shipped cells —
`md5_fn 9de0ae49d75a` (`safe_tuned.rs`) and `4a28657ae7e4` (`unsafe.rs`) — and
reproduce `results/gate/p05-index-flatten.json`'s committed marginals to the
instruction: 1504.00 / 8834.70 and 1381.00 / 8435.70. So §14 is one build and
directly comparable with the gate record, which is the cross-build risk §10b of
`patterns/p16-tlv-walk/NOTES.md` had to carry and this section does not.

**Equivalence:** all **37** binaries print the shipped R4 binary's checksum and
exit code on **all 183 committed inputs** — 0 mismatches over 6771 runs
(`.temp/p21/equiv.py`). A spelling spread, not an algorithm spread. The two
later rounds ran the same check on their own variants: 28 binaries × 183 inputs
with 0 mismatches at TASK_021_REVIEW (`.temp/review021/equiv.py`), and 26 × 183
with 0 mismatches at TASK_022 (`.temp/p22/equiv.py`).

**And the baselines reproduce across sessions and across authors.** TASK_022
regenerated the shipped R4, TASK_021's `r3_ds_h1` and TASK_021_REVIEW's
`w4_hu16` from its own templates and got `md5_fn 4a28657ae7e4` /
`e1d625cc9b0e` / `7110dd6bea56` and marginals 1381.00 / 1482.00 / 1376.00 on
`small` — byte for byte and instruction for instruction what the earlier rounds
recorded. Nothing in §14 is one session's artefact.

### 14d. The `nrow` axis had three points. It now ships with fourteen

**Bands A–C sweep `ncol` and *sample* `nrow`.** They give `nrow ∈ {19, 41, 65}`
and nothing else, so **every `a + b·nrow` law this pattern has ever published —
`6·nrow + 9` included — rested on three points**, one degree of freedom against
a two-parameter model. That is the shape that has already cost this project two
retractions (p16's `nrec + 3`; p05's own `+11.00 flat`), and `inputs/gen.py`'s
own band-C comment concedes it: two points cannot be wrong, three can only be
wrong in one direction.

TASK_021 added **band D** to `patterns/p05-index-flatten/inputs/gen.py`:
`nrow ∈ {1…9, 12, 16}` × `ncol ∈ {30, 32, 33}` = **33 blobs**, nine
*consecutive* `nrow` values plus two distant ones for lever arm, at three `ncol`
residue classes mod 8 — `{6, 0, 1}` — so the class LLVM peels a full extra
vector iteration for (`ncol ≡ 0`, §2a) is *in* the band rather than assumed
away. Appended last, and the RNG is drawn sequentially, so **all 150 files that
existed before are byte-identical after** (md5 over all 150: 0 changed).

The sweep is therefore **179 inputs — 14 values of `nrow`, 96 of `ncol` spanning
24…119, all eight residue classes mod 8** — and since TASK_021 `gen.py` is
inside `source_sha256`, a law measured on these blobs is re-derivable from a file
the gate record can see.

⚠ **179 inputs, 177 distinct dimensions** (TASK_021_REVIEW m4). `small` is 19×26
and `large` is 65×61, and `sweep-r19c26.bin` and `sweep-r65c61.bin` both exist,
so two of the 179 shapes are measured twice. The repeats carry different bytes
and are therefore still independent measurements — every law below is checked
on all 179 — but "179 points" must not be read as 179 distinct points of the
model's domain. The `nrow` axis is 14 values either way.

### 14e. The R3 laws — zero residual on every one of 179 points

`-O3 isolated`, marginal `Ir`/call = (whole-program `Ir` at `n_iters` 200 − at
100)/100, `harness/check.py` step 3b's own probe (`.temp/p21/mir.py`), one
session. Checked by `.temp/p21/laws.py`; **residual is exactly 0 at every point
of every row**, not "small".

| spelling | what changed from shipped R3 | `− R4ship` | reading |
|---|---|---|---|
| `r3_ds_h1` ✦ | data region resliced once to `nrow*ncol`, `base = i*ncol`; header via `try_into()` | **`5·nrow + 6`** | p16's |
| `r3_ds_while` ✦ | ditto, `while` outer loop | **`5·nrow + 6`** | p16's |
| `r3_ds_h2` / `_cells` / `_i1` / `_two` / `_copied` ✦ | ditto, five more surfaces | **`5·nrow + 6`** | p16's |
| `r3_ds_h0` | data region resliced once; shipped header | `5·nrow + 9` | p16's |
| `r3_dsget_h1` | ditto + `data.get(..)` instead of the indexing reslice | `5·nrow + 10` | p16's |
| `r3_get_h1` | shipped base, `buf.get(base..base+ncol)`, array header | `5·nrow + 12` | **strict** |
| `r3_hdrarray` | shipped everything, header via `try_into()` | `6·nrow + 6` | **strict** |
| **`safe_tuned.rs` (shipped)** | — | **`6·nrow + 9`** | **strict** |
| `r3_ends_h1` | `&buf[..off+4+nrow*ncol]` hoisted, base absolute, array header | `6·nrow + 10` | **strict** |
| `r3_window` | whole window resliced, `base = 4 + i*ncol` | `6·nrow + 12` | p16's |
| `r3_ends_h0` | as `r3_ends_h1`, shipped header | `6·nrow + 13` | **strict** |

✦ = seven textually independent spellings, **each swept over all 179 points and
each with zero residual against `5·nrow + 6`**. Three of them (`r3_ds_h1`,
`r3_ds_h2`, `r3_ds_copied`) turn out to be the *same binary* — `md5_fn
e1d625cc9b0e`, 113 instructions — and four are not (`d233f48a00ff`,
`9e59f98affaa`, `83d5f8bb96a5`, `cf5784a53206`), so the cheapest R3 found is
reached by **five distinct machine-code bodies**, not four as this paragraph
said until TASK_022 (TASK_021_REVIEW m1 — the count under-read its own
evidence; the five digests are listed right here). It is not one spelling's
luck.

Two spellings that are **not** near it and are worth recording so nobody
re-derives them, both measured on the two shipped inputs only and **not** swept:
`buf[base..][..ncol]` with an absolute base costs **+38 / +130** against shipped
R3 (1542.00 / 8964.70 — two range checks, not one; the same two-step spelling
*over the hoisted data slice*, `r3_ds_two`, is in the cheapest group), and
`buf[base..].iter().take(ncol)` de-vectorises the fold entirely (2010.00 /
10536.70, worse than shipped R2 on `small`).

**Twelve further in-contract R3 spellings have failed to beat `r3_ds_h1`'s
1482.00 / 8766.70.** Seven at TASK_021_REVIEW (`.temp/review021/v05/z3_*`):
`.map(..).fold` (1485), `.rev()` (1867 — de-vectorises), an
`assert!(data.len() == nrow*ncol)` (1485), an explicit in-loop `base + ncol > n`
guard (1489), two separate `u16` `try_into` reads (1487),
`u16::from_le_bytes([buf[off], buf[off+1]])` by direct indexing (1497), and the
array header re-spelt (1482). Five more at TASK_022 (`.temp/p22/v05/c3_*`):
respelling the fit check as `nrow*ncol + 4 > len` is **exactly equal** (1482.00
/ 8766.70), and **dropping the `nrow == 0 || ncol == 0` early return is one
instruction *dearer*** — 1483.00 / 8767.70, alone and crossed with a `cells`
binding, a `while` outer loop and the `+ 4 > len` check alike. `c3_ds_nz` was
swept over all 179 points at zero residual against `r3_ds_h1 + 1`; the other
three are `small`/`large` only.

That last one matters, and it is the sharpest thing in this section: **the
identical respelling is worth −2 on the *unsafe* side (§14f) and +1 on the safe
side.** The same edit helps R4 and hurts R3, which is why the constant does not
cancel between the rungs and why nobody should expect a "both rungs tuned"
figure to be stable.

### 14f. ~~The R4 side moves too~~ — 46 spellings over three rounds, and every one of them that moves is a control

**This heading said "the R4 side moves too" until TASK_028 and that is FALSE.**
Every spelling below that moves off the shipped cell does it by respelling the
**header read** or by `from_raw_parts`, and the `identity` pin makes those
inadmissible at the pinned vstd (the ⚠ at the head of §14). **They are
controls.** The measurements are correct and reproducible and are kept in full —
this file records refutations rather than erasing them — but no number below is
a p05 rung's number except `0`.

Be precise about what *is* established: the only p05 R4 **shown** admissible is
the shipped cell, whose R5 twin verifies today (`12 verified, 0 errors`). Six
round-1 variants measure exactly `0` against it and were never put through
Verus, and at least two of those (`r4_rowslice`, `r4_dataptr`) use the same
`from_raw_parts` / `add` the logs reject — but since they measure `0`, their
admissibility cannot move any endpoint and nobody needs to settle it.

**This section also said the opposite twice before that.** TASK_021 wrote *"the
R4 side has zero in-contract spread"*; TASK_021_REVIEW refuted that and wrote a
new cheapest; TASK_022 refuted *that*; TASK_028 restored TASK_021's conclusion
**for a completely different reason** — not because six agents happened to spell
the header the same way, but because the pin leaves them nothing else to spell it
with. The history is the result, so it is kept in full.

**Round 1 (TASK_021), 8 spellings — the *body* respelled, the *header* never.**

| unsafe spelling | `md5_fn` | `n_fn` | `− R4ship`, 179 points |
|---|---|---:|---|
| `unsafe.rs` (shipped), `get_unchecked(off + 4 + i*ncol + j)` | `4a28657ae7e4` | 87 | — |
| `r4_base`, per-row `base` hoisted | `4a28657ae7e4` | 87 | **0** |
| `r4_for`, `for` loops instead of `while` | `acf0bc406f51` | 87 | **0** |
| `r4_getrange`, `get_unchecked(base..base+ncol)` + iterator fold | `e905e528d7c6` | 87 | **0** |
| `r4_rowslice`, `from_raw_parts` per row | `e905e528d7c6` | 87 | **0** |
| `r4_dsrow`, hoisted data slice + unchecked row reslice | `e905e528d7c6` | 87 | **0** |
| `r4_dataptr`, fixed data pointer, `*dp.add(i*ncol + j)` | `3aa26d8839bc` | 87 | **0** |
| `r4_dataslice`, `from_raw_parts` over the data region, flat index | `5f9513c56b92` | 98 | `+8` at `ncol ≡ 0 (mod 8)`, `+3·nrow + 8` otherwise |

Four distinct machine-code bodies and one executed count at every point, which
this file read as *"the shipped R4 is the cheapest in-contract unsafe spelling"*
and as a **two-sided floor**. **Both readings were wrong, and the reason is
visible in the table**: all eight decode the header the shipped way. The
flatness measured the *header*, which no round-1 variant touched — while §14g,
three paragraphs down, already said the header is worth 3 on the R3 side. The
write-up named the term as header-side and then left it in the difference.

**Round 2 (TASK_021_REVIEW), 20 more measured — respell the header; 13 of them
beat the shipped R4.** In contract: nothing in `required`/`forbidden` mentions
the header, and the shipped R4 already reads it through `get_unchecked`.

| spelling | header | `− R4ship` |
|---|---|---|
| `x4_h1u` | `unsafe { buf.get_unchecked(off..off+4) }.try_into()` → two `u16::from_le_bytes` | **−3**, flat, 179 pts |
| `x4_hptr` | `(buf.as_ptr().add(off) as *const u32).read_unaligned()` | **−3**, flat, 179 pts |
| `y4_hptr_*` × 8, `w4_hptr_g2` | ditto, crossed with every round-1 body | **−3** (`small`/`large` only) |
| **`w4_hu16`**, `w4_hu16_g2` | two unaligned `*const u16` reads | **−5**, flat, 179 pts |

**Round 3 (TASK_022), 18 more — delete the `nrow == 0 || ncol == 0` early
return.** Also in contract: the declaration names no zero test, and the guard is
*semantically redundant* — with either dimension zero the kernel's own
arithmetic already returns 0, which is why all 26 round-3 binaries print the
shipped R4's checksum on all 183 committed inputs.

| spelling | `md5_fn` | `n_fn` | `− R4ship` |
|---|---|---:|---|
| **`c4_hu16_nz`**, two `*const u16` reads **+ no zero guard**; `d4_nz_raw` (no `.to_le()`) | `62f872bbd103` | 82 | **−7**, flat |
| `c4_hu16_nz_fitlen` (`nrow*ncol + 4 > len`) | `a451e96eb339` | 82 | **−7**, flat |
| `c4_hu16_nz_cells` (`cells` bound once) | `5c6584b355a5` | 82 | **−7** |
| `c4_hu16_nz_for` (`for` loops) | `6d6df4f925b1` | 82 | **−7** |
| `c4_hu16_nz_getrange`; `d4_nz_copied`; `d4_nz_rowslice` | `d489a762bc04` | 82 | **−7** |
| `d4_nz_swap` (`ncol` read first) | `25faaa951bf4` | 82 | **−7** |
| `d4_nz_availfirst` (`avail` hoisted above the header) | `2a479fdd099d` | 82 | **−7** |
| `c4_hu16_nz_dsrow`; `d4_nz_rowptr`; `d4_nz_raw_rowptr` | `4410c039d747` | 78 | −6 |
| `d4_nz_dataptr`; `d4_nz_raw_dataptr` | `a0d925311472` | 78 | −6 |
| `c4_hu16arr` / `c4_hu16arr_nz` / `c4_hu16_fitlen` | round-2 digests | 83/87/82 | −3 / −3 / −5 |

**Ten spellings reach −7 across seven distinct machine-code bodies**, all at
`n_fn 82`. **`c4_hu16_nz` is the one swept**: `R4ship − c4_hu16_nz = 7`, flat in
`nrow` and `ncol`, **zero residual on all 179 points**; the other nine are
`small`/`large` only, and are reported as such. Eight further crossings in round
3 failed to go below −7, so it looks like a plateau — which is exactly what −0,
−3 and −5 each looked like on the day each was published, every one of them
reached by several independent bodies. **Reached by many spellings is not
evidence of a floor**; that inference has now failed twice on this one rung, at
−0 and at −5.

Note also that the two −6 bodies are the *smallest* kernels in the table
(`n_fn 78`) and execute *more*. A static count is not a cost model, which is
`harness/asm.py`'s own warning demonstrated inside one section.

The mechanism of the last −2 is in the disassembly. Deleting the zero guard
lets LLVM sink the two zero tests *below* the fit check, where they become the
loops' own entry tests, and the two instructions that were paying for the early
return — `xor %eax,%eax` and a redundant `movzwl %r8w,%eax` forced by testing
the 16-bit subregister — go away.

> ⚠ **The `−7` = `−5` + `−2` decomposition is an INFERENCE, and its `−2` half
> has never been compiled** (TASK_027_REVIEW; landed TASK_028). All 26 of round
> 3's variants pair the zero-guard deletion with `read_unaligned`, so no binary
> in this table isolates the guard. `−2` is `−7` minus `−5`, arithmetic over two
> inadmissible spellings. **It matters because the guard deletion is the one
> half of the lever that is admissible**: transplanted onto the *shipped*
> header and given one lemma and one `proof` block, p05's exec code verifies at
> **`13 verified, 0 errors`, zero new trusted items** — the same code without
> the lemma gives `11 verified, 1 errors`, *postcondition not satisfied*, which
> disqualifies nothing. So **the one admissible p05 R4 that might move has never
> been built**, and building it is the open question this section leaves. Queue
> item 2a; explicitly out of scope for TASK_028.

**The one in-contract R4 that is *dearer*** is still round 1's `r4_dataslice`,
at `+8` / `+3·nrow + 8`; its 1446.00 / 8638.70 are exactly §13 row 3's
`t4_idx.rs`, which is how a *safe* out-of-contract spelling and an *unsafe*
in-contract one land on the same figure. **It is not a rung**: `from_raw_parts`
is `is not supported` at the pinned vstd. It used to be the top of the R4
interval and the reason §14h.3's lower endpoint was `2·nrow − 2` rather than
`5·nrow + 6`; with it out, `5·nrow + 6` is the lower endpoint again and there is
no R4 interval.

### 14g. The mechanism, counted in the disassembly

`.memory/01-ladder.md` finding 6 asks for the mechanism, not the number. Every
term above is a per-row instruction and can be pointed at
(`.temp/p21/asm-r3_ship.txt`, `asm-r3_ds_h1.txt`, `asm-r4_ship.txt`).

The outer-loop latch plus row setup, i.e. everything executed once per row
outside the vector body:

| rung | insns/row | the block |
|---|---:|---|
| **R4 shipped** | **12** | `mov;shl;sub` + `mov;add` (Horner) · `inc` · `add %r9,%r11` + `add %r9,%rdx` (two row pointers LLVM strength-reduced for itself) · `cmp;je` (trip) · `cmp $0x8;jae` (vector guard) |
| **R3 shipped** | **18** | the same 12, **plus** `mov;imul` (re-derive `i*ncol`) · `add %rsi` (add `off + 4`) · `lea (%rax,%r11,1)` (form `base+ncol`) · `cmp %r8;ja` (against `buf.len()`) |
| **R3 `r3_ds_h1`** | **17** | the same, **minus** the `add %rsi` |

So the published `6·nrow` is exactly those six instructions, and the cheapest
in-contract R3 found removes **exactly one of them**: the `add` that turns a
window-relative row base into a buffer-absolute one. Hoisting the reslice to
`&buf[off+4 .. off+4+nrow*ncol]` makes the base already window-relative, and the
`add` disappears. The `+3` is the header: shipped decodes `nrow`/`ncol` with
`movzwl` + two `movzbl` + `shl` + `or`; the array form issues one 4-byte load
and derives the vector guard as `cmp $0x80000,%r9d` — testing `ncol >= 8`
against the *packed* header word without extracting `ncol` at all. **This is
also the term §14f's round 1 left in the difference**: it is header-side, it is
named as header-side right here, and it was applied to R3 and not to R4.

**The surviving five are the bounds check and nothing else**: `mov;imul`
re-derives `i*ncol` — which LLVM has *already* strength-reduced into
`%r8`/`%rsi` two instructions earlier, and re-derives anyway because the check
needs the value and not the pointer — then `lea` forms `base + ncol`, then
`cmp;ja`. The fact needed to delete them is `(i+1)·ncol <= nrow·ncol` for
`i < nrow`, which is **nonlinear**, which is the obligation R5 discharges with
`lemma_mul_inequality` and `by (nonlinear_arith)` (§5), and which §12b's
`probe2.rs` already showed LLVM cannot do.

⚠ **"They cannot be removed by any spelling" is what this paragraph used to
say, and it was never measured** (TASK_021_REVIEW m3). What is measured is
narrower and should be quoted instead: **no in-contract spelling searched
removes them** — 41 R3 spellings over three rounds. Out of contract they
partly go: §13 row 3's `t4_idx` supplies a *linear* row induction variable and
is `3·nrow + 8` cheaper than shipped R4, i.e. it removes the `mov;imul`
re-derivation, **2 of the 5**, while `lea;cmp;ja` survive. That is a sharper
result than the overclaim, because it separates the part of the check that a
linear induction variable can kill from the part that needs the nonlinear fact.

**So the surviving per-row cost and the proof obligation are the same fact**,
and that is a sharper statement of finding 6 than "the optimiser fails the
lemma the proof proves". Note what it does *not* rest on: it is a statement
about the `O(nrow)` term, measured over 14 values of `nrow`, and it survives
every revision §14f records — because those revisions all moved the **constant**
and none of them moved the coefficient.

### 14h. What this establishes — and the one thing it does not

1. **"The shipped R3 is the cheapest admissible spelling" is FALSE for p05
   too** — under *both* readings of `required[1]`, so the reading does not have
   to be settled to reach it. Fourth pattern out of four. **This is the claim
   that has survived all three rounds**, because it holds the R4 side fixed at
   the shipped cell and so cannot be moved by widening the R4 search:
   `r3_hdrarray` is 3 cheaper than shipped R3, flat, at every `nrow`, and
   respells nothing but the header.
2. **`R3ship − R4ship = 6·nrow + 9` is the shipped pair's difference, and there
   is exactly one bound in this section that is a real bound.** Hold the unsafe
   rung at the shipped cell. Then `inf(in-contract R3) − R4ship` is bounded above
   by anything the R3 search finds, because widening a search can only lower a
   minimum — so `6·nrow + 9` is a genuine upper bound on it, and `5·nrow + 6`
   (101 / 331) is a tighter one, `nrow + 3` lower at every `nrow ≥ 1`. **That is
   the whole of what is bounded here**, and it is bounded only because one side
   is *fixed by fiat* rather than minimised.

   This item used to end *"as soon as the R4 side is allowed to move, nothing is
   bounded, because a free in-contract pairing exceeds it (item 3)"*.
   **TASK_028 deletes the escape clause**: the R4 side is *not* allowed to move,
   because the `identity` pin admits no R4 spelling that does. The fixed-R4
   bound is therefore not a fallback that a wider search would take away — it is
   the only pairing p05 has, and it is a real bound.
3. **The in-contract quantity is an R3-SIDE SPAN. There is no pair interval.**
   Over the admissible spellings searched, with the unsafe rung at the shipped
   cell:

   | endpoint | pairing | law | `small` / `large` |
   |---|---|---|---|
   | bottom | cheapest R3 found, R4 shipped | `5·nrow + 6` | 101 / 331 |
   | — | shipped pair, **published** | `6·nrow + 9` | 123 / 399 |
   | top | dearest R3 found (`r3_ends_h0`), R4 shipped | `6·nrow + 13` | 127 / 403 |

   Width `nrow + 7` = 26 / 72, **21% / 18% of the published figure**, which sits
   inside it.

   ⚠ **What this table said until TASK_028, and why it is withdrawn.** It read:

   | endpoint | pairing | law | `small` / `large` |
   |---|---|---|---|
   | ~~bottom~~ | cheapest R3 found, **dearest** R4 found (`r4_dataslice`) | ~~`2·nrow − 2`~~ | ~~36 / 128~~ |
   | ~~top~~ | dearest R3 found, **cheapest** R4 found (`c4_hu16_nz`) | ~~`6·nrow + 20`~~ | ~~134 / 410~~ |

   — a `4·nrow + 22` wide interval, 98 / 282 Ir, "80% and 71% of the published
   tax", with **both endpoints set by R4 spellings that are not rungs**
   (`from_raw_parts` and `read_unaligned`; the ⚠ at the head of §14, seven Verus
   twins in TASK_027_REVIEW). Substituting the admissible class gives exactly
   the R3-side span above — the `nrow + 7` figure that this item was written to
   *replace*. Two tasks of work to arrive back where the R3 side already was.

   ~~**The bottom is exactly zero at `nrow = 1`**~~ — measured at `sweep-r1c30`,
   `0.00`, `r3_ds_h1` and `r4_dataslice` both at 152.30, and **withdrawn**: that
   pairing's R4 is `r4_dataslice`. **Do not quote "p05 has an admissible pair
   whose tax is free".** Evaluating the two laws above at `nrow = 1` puts the
   admissible span at `11 … 19` — arithmetic on published laws, not a fresh
   measurement. (`sweep-r2c30`'s `2.00` and `32.00` go the same way.)

   **Why "degenerate" and not "unavailable" is the right word.** A pair interval
   over the *admissible* class is perfectly computable today; it is the table
   above, because every p05 R4 that could enter it sits at exactly `R4ship`. So
   the R4 endpoint contributes **zero measured width**, and the pair interval
   *is* the R3-side span under a second name. Saying "no pair interval is
   available" would be false and would read as evasion; publishing one as a
   result would claim a two-sided search whose second side has one value. The
   honest statement is that it is degenerate, and that it stops being degenerate
   the day somebody builds an admissible R4 that moves — which, per §14f's ⚠, is
   the unbuilt zero-guard deletion.
   ⚠ **"…and that makes p05's declaration the LOOSEST of the set" was written
   here and is FALSE.** It compared p05's *pair* interval against p16's
   **R3-side-only** span of 44% / 55% — the same one-rung mistake one paragraph
   up.

   ⚠ **The replacement was withdrawn too, at TASK_024, and NOT re-pointed.**
   TASK_023 substituted *"p16's pair interval is 111% / 109%, wider than p05's
   80% / 71%"*. Both halves fail. p16's number is refuted — TASK_023_REVIEW
   measured p16's pair interval at **−239…+236 (1759%) / −2449…+2244 (6095%)**,
   with its bottom **negative on all 24 blobs**, because p16's declaration also
   licenses **unrolling** and that lever is per byte where the two TASK_023
   pulled are per record (`patterns/p16-tlv-walk/NOTES.md` §10a.2). And even
   with the right number the comparison would be invalid: it puts a **2-lever**
   p16 search beside p05's **46-spelling** one, which is the same "one interval
   is not the other's peer" error, one level down, as the claim it replaced.
   **Two intervals are comparable when the searches behind them are, and no two
   searches on this project are.** No "which declaration is loosest" claim is
   asserted anywhere; do not re-derive one from these numbers.

   ⚠ **And at TASK_028 there are no pair intervals left to compare.** p16's
   `−239…+236` is withdrawn on the same ground as p05's: its R4 endpoints are
   `r4_hdr` and the unsafe-side `chunks_exact` folds, and neither family is a
   p16 rung. **Two published, two withdrawn, none replaced.** What the two
   patterns publish is a fixed-R4 bound and an R3-side span each.
4. **There is no measured minimum, and "best found" is not honest enough for
   this pattern.** Three values have been published here as the minimum and all
   three were overturned by the next search — `5·nrow + 6` (8 R4 spellings),
   `5·nrow + 11` (28), `5·nrow + 13` (46) — each time by respelling one more
   thing in the unsafe rung's prologue, each time on the first lever the next
   agent pulled, and each time the refuted value had been reached by *several
   independent machine-code bodies*, which is the evidence that kept being
   mistaken for a floor. ~~`inf(R4) <= inf(R3)` holds by construction
   (`.memory/01-ladder.md` finding 14)~~ — **refuted at TASK_025_REVIEW, and it
   runs the other way**: the `identity` pin bounds the R4 class by what vstd can
   express and leaves the R3 class unbounded, so the two classes are
   *incomparable*, not nested. Neither infimum is measurable by sampling
   spellings either way; `min(R3 found) − min(R4 found)` is the difference of two
   upper bounds and therefore **bounds nothing in either direction**. Quote the
   R3-side span in item 3 and the fixed-R4 pairing in item 2; do not quote a
   minimum, and do not quote a pair interval.
5. **`5·nrow + 13` is not even below the published figure everywhere.** Both
   rungs written as cheaply as the search could manage, the tax is *larger* than
   the shipped pair's for `nrow ≤ 3` (18 against 15 at `nrow = 1`), equal at
   `nrow = 4`, and smaller above — measured at every band-D point. Tuning R4's
   prologue buys 7 and tuning R3's buys only `nrow + 3`. A "minimum" that
   exceeds the published number on a fifth of the sweep's `nrow` axis is a
   pairing convention, not a minimum. **And at TASK_028 it is not even that**:
   the 7 that "tuning R4's prologue buys" is `c4_hu16_nz`, which is not a rung,
   so `5·nrow + 13` is a measurement of two programs one of which p05 cannot
   ship. The surviving version of this item is item 2 — tuning R3 buys `nrow + 3`
   against a fixed R4, and tuning R4 buys **nothing admissible at all**.
6. **What survives all three rounds is the shape, under one stated pairing, and
   that is the durable result.** Take the pairing this file reports — cheapest
   R3 found against cheapest R4 found, p16's reading of `required[1]` — and the
   law is `5·nrow + b`: positive, `O(nrow)`, `nrow` coefficient **5**, with only
   `b` moving (6 → 11 → 13) across three rounds. That restriction mattered while
   free pairings were thought to be available: over them the coefficient ranged
   from 2 to 6 (item 3), so the coefficient looked like a property of the pairing
   convention rather than of the pattern. **At TASK_028 the free pairings are
   gone** — both spellings that produced the 2 and the 6 are inadmissible — so
   over the *admissible* class the pairing collapses to `b = 6` and the
   coefficient 5 is not convention-dependent after all. The caution stays anyway,
   because one unbuilt admissible R4 (§14f's ⚠) could still move `b`.
   p17's spelling audit flipped a *sign* and p16's cut its tax by 42%; p05's
   moved that constant twice and left the functional form, the sign and the
   `O(nrow)` conclusion standing under its stated pairing. §14g says why: the
   declaration pins the multiply, and the multiply is where the row-scaled cost
   is. This — and only this — is what `.memory/01-ladder.md` finding 6's
   reinstated sentence is about.
7. **p05's published `6·nrow + 9` is independently re-derived on a 14-point
   `nrow` axis**, zero residual, where the number it certifies had been a
   three-point fit — and re-derived again in two later sessions by two other
   agents from their own templates. The headline was under-supported and is now
   correct.

**Method.** Round 1 `.temp/p21/{mkvar,mkvar2,mkvar3,mir,equiv,laws,audit}.py`
(37 binaries × 183 inputs); round 2 `.temp/review021/{mkvar,mkvar2,mir,equiv,
laws}.py` (28 × 183); round 3 `.temp/p22/{mkvar,mkvar2,build,mir,equiv,laws}.py`
(26 × 183, 5 binaries × 179 points swept, 7 laws at zero residual). The marginal
probe is `harness/check.py`'s own — whole-program `Ir` at `n_iters` 200 minus at
100, over 100 — re-implemented independently in each round; the three
implementations agree to the instruction on the shared baselines. **No pattern
source was edited in any round**; the only committed file §14 has ever changed
is `inputs/gen.py`, which gained band D at TASK_021.
