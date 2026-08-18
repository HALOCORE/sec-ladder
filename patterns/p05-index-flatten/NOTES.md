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
| **M2** | trusted `requires` `i < v@.len()` → `i <= v@.len()`, on the item **and** its twin | **`12 verified, 0 errors`** shipped; **`12 verified, 1 errors`** under `--cfg slb_twin` — *precondition not met: index in bounds for this access* | **Verus alone passes the off-by-one; only the verified twin catches it** |
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

It is not *nothing*: §5b's M2 shows the twin is the only mechanism that catches
`i <= v@.len()`, and the gate re-runs that deletion probe every time. But that
is the same demonstration p01 could have given. Manufacturing a multi-clause
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
price of the optimiser failing the lemma the proof proves". What **survives**
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
`6·nrow + 9`"*.

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

## 13. The spelling spread — eleven spellings of one kernel, and which two are p05

**Not the headline.** This section is a result *about method*, published because
the spread is wider than the thing the pattern measures. The number p05
publishes is the matched pair under the idiom `spec.md` declares —
**R3 `safe_tuned.rs` − R4 `unsafe.rs` = `6·nrow + 9`** — and every other row
below is a measurement of a *different* kernel, kept here so nobody re-derives
one and reports it as p05's.

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
