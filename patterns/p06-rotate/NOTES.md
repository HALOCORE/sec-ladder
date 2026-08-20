# p06 — in-place rotate: findings

Read `spec.md` first; this file records what was measured, in the order it was
measured, and what it cost.

**Two `Ir` conventions appear here and every figure says which**
(`.memory/03-measurement.md`). The **table** column is `results/p06-rotate.json`'s
*kernel-exclusive* `Ir`; every **law and every matched difference** is a
*whole-program marginal*, `(Ir(n_iters=6000) − Ir(n_iters=2000)) / 4000` on the
same blob and the same binary (`controls/sweep_ir.py`), which cancels start-up,
the payload load and the driver's `println!` digit term and — unlike the
kernel-exclusive column — **includes the `memcpy` body**.

⚠ **And on p06 that distinction is load-bearing, p13's blocker 3 on a second
pattern.** The rungs do **not** all call the same libc routines:

| cell | `bulk_calls` in the kernel symbol |
|---|---|
| `c-gcc`, `c-gcc-h` | **none** — gcc inlines the 64-byte copy |
| `c-clang`, `c-clang-h` | `memcpy@plt` |
| `safe_naive`, `safe_tuned`, `unsafe`, `verus` | `memcpy@GLIBC_2.14` |

So the kernel-exclusive column is comparable **within** gcc, **within** clang and
**among the four Rust rungs**, and **not** across those groups: `c-gcc − R4` is
`+853` kernel-exclusive and `+791` whole-program on `small`, a 62-instruction
difference that is entirely gcc's inlined copy. Every gcc-vs-anything figure
below is whole-program. Every same-compiler difference is identical under both
conventions, because the `memcpy` term cancels.

## 0. THE PRE-FLIGHT — three prescriptions settled before five rungs were built on them

TASK_047 named three calls the manager was least sure of and asked for them to be
settled first. All three were, on a standalone six-kernel C probe
(`.temp/p06/probe1_kernel.c`, `probe1_main.c`, `probe1_gen.py`, `probe1_perm.py`,
`probe1_time.py`) with no driver and no pattern. **Two of the three came out
against the prescription, and a fourth prescription was falsified as a bonus.**

### 0a. Does the three-reverse decomposition survive `-O3`? **Yes, both compilers.**

`objdump -d` of the probe's hardened kernel shows **three distinct scalar swap
loops** and nothing else: clang 8 instructions per swap iteration
(`mov,mov,mov,mov,inc,cmp,lea,jb`), gcc 10. No `memmove`, no `call` other than
`memcpy`, no shuffle, no vector register anywhere in the rotate. Re-checked on
the shipped rungs (§1). **Item 3's law is therefore measuring the triple, and the
library axis does not arrive uninvited.**

### 0b. Is the `div` reached at `-O3`? Yes — and `R1h − R1` is SIGN-WRONG under clang

The `div` is real and survives in both compilers: clang emits `div %r12d` (a
**32-bit** divide), gcc `div %r10` (a **64-bit** one — the more expensive
instruction, and it shows up in §3's clock).

Marginal `Ir` **per record**, differencing `nrec` 8 → 16 so the per-call constant
cancels; `nelem = 32`, `r = 7`, a *perf* input where the reduction is
semantically a no-op:

| cell | the safety line | clang `Ir`/rec | gcc `Ir`/rec |
|---|---|---:|---:|
| `bug` (R1) | *(none)* | 533.02 | 671.02 |
| `zext` (null control) | `rr = (size_t)(uint32_t)rr` | 533.01 | 671.02 |
| `and` (control, **not** a hardening) | `rr &= 63` | 521.02 | 671.02 |
| **`mod` (R1h, textbook — SHIPPED)** | `if (m) rr %= m; else rr = 0` | **522.02** | **672.02** |
| `cmp` (R1h, guarded) | `if (m==0) rr=0; else if (rr>=m) rr %= m` | 526.02 | 675.02 |
| `sub` (R1h, repeated subtract) | `while (rr>=m) rr -= m` | 538.02 | 677.02 |

TASK_047 pre-registered *"`Ir`: +1–3 per record; cycles: 20–40× that"*. The first
half is right for gcc and **wrong in sign for clang**:

```
clang:  mod - bug  =  -11.00  =  -12.00 (narrowing)  +  1.00 (the div)
gcc:    mod - bug  =   +1.00  =    0.00 (narrowing)  +  1.00 (the div)
```

zero residual, and the `and` control is what isolates it: masking `r` to six bits
with no divide is `−12.00 Ir/record` under clang and `0.00` under gcc. **The
mechanism is a lost load-merge, p09's.** In the unreduced kernel clang lowers the
four-byte LE decode of `r` as `movzwl + movzbl + shl + lea + movzbl + shl + or`
because `r` feeds 64-bit address arithmetic with no known range; once `r %= m`
proves `r < m ≤ 64` the value stays 32-bit and the same decode becomes **one**
`mov 0x4(%rdi,%rax,1),%ebp`. gcc's decode is already merged in every cell, so gcc
sees the `+1.00` and nothing else.

**`Ir` prices the hardware divide at exactly 1.00** on both compilers,
reproducing `.memory/03-measurement.md`'s rule on a second kernel.

The clock: 11 reps, interleaved by cell, foreground, `taskset -c 5`,
`t(200000) − t(1)`, and — because `.memory/03-measurement.md` makes a
same-binary cross-cell `ns` comparison a layout suspect — **repeated over 6
permutations of the source order of the six kernels** (`probe1_perm.py`), which
moves every kernel to a different address without changing a byte of code.
ns/call at `nrec = 16`, median of 5 reps per layout, range over the 6 layouts:

| cell | clang ns/call | gcc ns/call |
|---|---|---|
| `bug` (R1) | 652.2 … 684.2 | 878.6 … 949.7 |
| `and` | 634.0 … 636.8 | 880.4 … 928.7 |
| **`mod` (R1h textbook)** | **688.1 … 690.7** | **971.0 … 1020.9** |
| **`cmp` (R1h guarded)** | **633.0 … 638.7** | 880.6 … 933.9 |
| `sub` | 638.3 … 646.7 | 879.1 … 946.2 |

**`mod` is the slowest cell in 12 of 12 (compiler × layout) configurations and
its band does not overlap any other cell's on either compiler.** Everything else
sits inside one noise band. §3 reproduces all of this on the shipped tree with a
proper identical-copy floor.

**Verdict on the prescription the manager was least sure of:** the *premise* —
the safety line is a real hardware divide and `Ir` counts it as ~1 — **holds
exactly**. The *conclusion drawn from it* does not. p06's methodological headline
is not "`Ir` understates the safety tax"; it is **"`Ir` gets its sign wrong"**,
and the mechanism is named and controlled.

### 0c. Is regime 1 identical across all eight cells? Yes — and THE BOUNDARY IS ONE OFF

TASK_047 put the regimes at `m <= r < SCR` and `r >= SCR`. **The boundary is
`r > SCR`.** `reverse(scr, 0, r)` swaps `scr[i]` with `scr[r-1-i]`, so its
highest index is `r − 1`; at `r == SCR == 64` that is 63 and the rung is still
inside the array. `adversarial-inarray.bin`'s third record sits exactly there and
is the boundary from the safe side, p12's `adversarial-exact` analogue.

All eight cells on `adversarial-inarray.bin` (records `(m, r)` = `(16,40)`,
`(32,50)`, `(8,64)`; `model.py` says `5453190234444350336`):

```
c-gcc        12407484466270198528      <- R1, wrong
c-clang      12407484466270198528      <- R1, THE SAME wrong value
c-gcc-h      5453190234444350336
c-clang-h    5453190234444350336
safe_naive   5453190234444350336
safe_tuned   5453190234444350336
unsafe       5453190234444350336
verus        5453190234444350336
```

exit 0 everywhere, no stderr, nothing panics, and the gate's ASan+UBSan stage
reports **clean** on this row while firing on all three `past` rows. §7 has the
delete-the-check controls, which is where the *safe Rust reproduces it
bit-for-bit* claim is actually established.

### 0d. BONUS — item 3's pre-registered law is false, and the correction is exact

TASK_047 §"What to measure" 3: *"Three reverses cost `r + (m − r) + m = 2m`
element-swaps regardless of `r`, so the law predicts no `r` term at all … a
coefficient on `r` that is not zero means the three-reverse decomposition is not
what is executing."*

Probe sweep, `r = 0 … 31` at `m = 32`, `nrec = 16`, clang, `Ir`/call:

```
r = 0            8237.00
r even, r >= 2   8285.00   (exactly, all 15 values)
r odd            8413.00   (exactly, all 16 values)
```

`8413 − 8285 = 128 = 16 records × 8 Ir` — exactly one more swap-loop iteration
per record. At `m = 31` (odd): **8381.03 flat for every `r >= 1`**, 8332.99 at
`r = 0`; no parity term at all.

The task file's arithmetic counts *elements touched*, not *swap iterations*. A
reverse of a half-open range of length `L` runs `ceil(L/2)` iterations, so

```
swaps(m, r) = ceil(r/2) + ceil((m-r)/2) + ceil(m/2) = m + [ m even AND r odd ]
```

zero fitted parameters. **The `r` coefficient is not zero — and the
decomposition is intact and the optimiser rewrote nothing.** The prescribed
falsifier would have fired on a correct build. `r == 0` is a third case and must
never be pooled with "even". §2 is the same law re-measured on the shipped tree.

## 1. The three reverses survive `-O3` in every rung

`objdump` of the shipped `-O3 isolated` kernels: three scalar swap loops in
`c-gcc`, `c-clang`, `safe_naive`, `unsafe` and `verus`; three
`split_at_mut`/`zip`/`swap` loops in `safe_tuned`. `vector_regs` is `['xmm']` in
every cell, and in every cell the only `xmm` use is the 64-byte zero-fill of
`scr` and (in the Rust and clang cells) `memcpy`'s inlined head — **the rotate is
scalar in all eight cells**. `has_loop` true everywhere; `n_backward_branches` 7
(R5/R4) to 9.

The shipped ladder, `-O3 isolated`, **kernel-exclusive** `Ir` per call (read the
caveat at the top of this file before differencing across compilers):

| rung | cell | `n_fn` / nopad | `small` | `large` | `md5_fn` |
|---|---|---|---:|---:|---|
| R1 | c-gcc | 190 / 186 | 3477.00 | 1988.00 | `9aa2c1f4ef67` |
| R1h | c-gcc-h | 200 / 193 | 3518.00 | 2083.00 | `2bc91328d572` |
| R1 | c-clang | 175 / 169 | 2615.00 | 1707.00 | `d79e16a78bd7` |
| R1h | c-clang-h | 171 / 164 | 2570.00 | 1599.00 | `5844f1e091cf` |
| R2 | safe_naive | 303 / 294 | 2797.00 | 2120.00 | `48e508ddf075` |
| R3 | safe_tuned | 279 / 270 | 2958.00 | 1897.00 | `cbf5d997d367` |
| R4 | unsafe | 216 / 208 | 2624.00 | 1725.00 | `897c52ff4005` |
| R5 | verus | 216 / 208 | 2624.00 | 1725.00 | `897c52ff4005` |

`R4 ≡ R5` at `-O3`: **`md5_raw` equal, `md5_fn 897c52ff4005`, 208 instructions,
padding 6/6** — the gate's own stage-3c record. At `-O0` the level is `norel`
(crate names differ in length, so call displacements differ).

## 2. The swap law, swept on the shipped tree

`sweep-r*`, 63 blobs, `nrec = 8`, whole-program marginal `Ir`/call:

| sub-band | `r` | `unsafe` | `safe_naive` |
|---|---|---:|---:|
| `re32` (m = 32, **even**) | `r = 0` | 4217.00 | 4486.00 |
| | `r` even ≥ 2 | **4225.00** (exactly, 15/15) | 4494.00 |
| | `r` odd | **4289.00** (exactly, 16/16) | 4558.00 |
| `ro31` (m = 31, **odd**) | `r = 0` | 4249.00 | 4510.00 |
| | every `r >= 1` | **4257.00** (exactly, 30/30) | 4526.00 |

`4289 − 4225 = 64.00 = 8 records × 8 Ir` = one extra swap per record, and
`4225 − 4217 = 8.00 = 1 Ir/record` is the first reverse loop's preamble that
`r == 0` skips. At odd `m` the `r` term is exactly zero over the whole range.
So on the shipped tree, at `-O3`, with the shipped R4:

> **`swaps(m, r) = m + [m even AND r odd]`, and the `Ir` cost of the extra swap
> is 8.00 under clang/rustc and 10.00 under gcc — the swap-loop body length off
> the listing, not a fitted slope.**

`R2 − R4` is **269.00 on every one of the 63 blobs**, at `m = 31` and `m = 32`
alike: the rotate amount and the rotated extent move R2 and R4 by identical
amounts. That is the first half of §4.

**Why the fold has to be order-sensitive, and p06's independent second reason for
the rule.** TASK_004_REVIEW's reason is **elision**. p06's is **invariance**:
three reverses compose to a *permutation*, so whenever `r <= SCR` the buggy and
the correct scratch hold the **same multiset**, and a sum-fold or an xor-fold
would return the identical checksum on `adversarial-inarray` — the pattern's
central row would silently become a null. The full-extent, order-sensitive Horner
fold is what makes regime 1 observable at all.

## 3. What the safety line costs on the shipped tree — the headline

### 3a. `Ir`, swept and exact

Whole-program marginals over `sweep-n*` (24 blobs, `m = 16`, `r = 2`, `nrec`
1…24) and `sweep-m*` (48 blobs, `nrec = 8`, `r = 2`, `m` 1…48). Every fit is a
two-point exact solve at the band endpoints with the residual of every
intermediate point reported; max residual **0.048** on the C cells and **0.015**
on the Rust cells, which is the `println!` digit-count term
(`.memory/03-measurement.md`: 0.2263 Ir/call/digit) and cancels in every matched
difference.

| quantity | law | domain / residual |
|---|---|---|
| **`R1h − R1`, gcc** | **`+8.00·nrec − 1.00·rzero + 1.00`**, and `0.00000` per byte | **max residual 0.0000 over all 77 blobs** of bands N + M + X, `m` 1…48 including the degenerate `m = 1, 2` |
| **`R1h − R1`, clang** | **`−10.00·nrec` (`m ≡ 0 mod 4`) / `−9.00·nrec` (otherwise) / `−8.00·nrec` (`m <= 2`, where every `r` reduces to 0)**, and `0.00000` per byte | exact per residue class over `m` 1…48; the pooled fit without residue regressors leaves 6.04 |
| `R2 − R4` | `+32.00·nrec + 13.00`, **`0.00000` per byte** | exact; `269.00` flat over all 46 `m` in 3…48 |
| `R3 − R4` | **`2.00000` Ir per byte of the live extent**, plus `α(m mod 8)·nrec + 1` with `α ∈ {3, 5, 19, 22}` | exact for `m >= 4`; `m = 3` is an outlier (§9) |
| `R5 − R4` | **`0.00000` everywhere** | pooled fit over 77 blobs, **all five coefficients exactly 0, max residual 0.0000** |

**So the safety line has NO per-byte term on either compiler.** It executes once
per record and it is priced once per record — which is what a per-record check
should cost, and it is why the sign result below cannot be a size artefact.

On the shipped inputs (whole-program marginal, `small` = 5 records / 157 bytes,
`large` = 12 records / 52 bytes):

| | `small` | `large` |
|---|---:|---:|
| `R1h − R1`, gcc | **+41.00** (+1.17%) | **+95.00** (+4.74%) |
| `R1h − R1`, clang | **−45.00** (−1.67%) | **−108.00** (−5.65%) |

Both are predicted **out of sample, to the instruction**, by the band laws —
`small`'s five records have five *different* `m` (13, 47, 29, 61, 7) and `large`'s
twelve run 1…8, and no band visits any of those shapes:

```
gcc,   small:  8*5  + 1 - 1*0  =  41   measured  +41.00
gcc,   large:  8*12 + 1 - 1*2  =  95   measured  +95.00
clang, small:  -9*5            = -45   measured  -45.00
clang, large:  -(2*10 + 7*9 + 3*8) = -107   measured -108.00   (off by 1)
```

§9.

### 3b. The clock, with the full protocol

`controls/wall_span.py`: **5 byte-identical copies of every binary at distinct
inodes**, one fixed layout, **alternating** schedule (one launch per cell per
round — TASK_031 measured p05 at `+1.21%` alternating and `−4.16%` blocked),
12 reps, `taskset -c 5`, estimator `(t(200000) − t(1)) / 199999`. The
identical-copy noise floor is the spread over the five copies.

| cell | `small` ns/call | floor | `large` ns/call | floor |
|---|---:|---:|---:|---:|
| c-gcc (R1) | 234.42 | 0.45% | 154.32 | 0.91% |
| **c-gcc-h (R1h)** | **280.04** | 0.68% | **242.42** | 0.47% |
| c-clang (R1) | 222.63 | 0.53% | 145.36 | 1.35% |
| **c-clang-h (R1h)** | **244.41** | 0.55% | **160.71** | 0.98% |
| safe_naive (R2) | 250.57 | 0.72% | 190.02 | 2.05% |
| safe_tuned (R3) | 249.41 | 1.06% | 168.59 | 1.14% |
| unsafe (R4) | 235.41 | 1.19% | 167.58 | 0.86% |
| verus (R5) | 242.47 | 1.02% | 165.21 | 0.94% |

**`verus − unsafe` is the null**, because those two binaries carry
byte-identical kernels: **+3.00% on `small` and −1.41% on `large`**. It is
larger than the within-binary identical-copy floor and its **sign flips between
the two inputs**, which is what a null looks like (`.memory/01-ladder.md`, p04).
**Take ±3% as the honest inter-binary floor for every `ns` figure in this file**;
the within-copy floor (0.45–2.05%) is a lower bound on noise, not the whole of
it.

**THE HEADLINE — the two columns and their disagreement:**

| | `Ir`/call | ns/call | |
|---|---|---|---|
| gcc `R1h − R1`, `small` | **+41.00 (+1.17%)** | **+45.63 (+19.46%)** | `Ir` understates **17×** |
| gcc `R1h − R1`, `large` | **+95.00 (+4.74%)** | **+88.10 (+57.09%)** | `Ir` understates **12×** |
| clang `R1h − R1`, `small` | **−45.00 (−1.67%)** | **+21.78 (+9.78%)** | **the signs disagree** |
| clang `R1h − R1`, `large` | **−108.00 (−5.65%)** | **+15.35 (+10.56%)** | **the signs disagree** |
| `R5 − R4` (the null) | 0.00 exactly | +3.00% / −1.41% | the floor |

Every one of the four is a multiple of the ±3% floor. gcc's `large` figure is a
64-bit `div` per record: 88.10 ns over 12 records is **7.34 ns/record**, i.e.
≈ 21–28 cycles at this box's 2.8–3.9 GHz band — squarely Cascade Lake's `div r64`
throughput, and 12 × what `Ir` charges.

> **p06's methodological result, stated once: on a kernel whose safety line is a
> DIVISION, the project's primary metric reports the hardening as FREE (gcc,
> +1.2%) or as a SAVING (clang, −1.7%) while the clock reports +10% to +57%.
> `Ir` is not merely imprecise here — it has the wrong sign, twice, and the
> mechanism for the sign is a lost load-merge that has nothing to do with the
> divide.**

### 3c. The HARDENING-SIDE SPAN — and the honest headline is the cheapest, not the textbook

TASK_047 asked whether the safety line itself has a span. It does; no pattern
here had measured one. Three spellings, all computing the same function, all in
contract (they differ only in *how* `r` is reduced), `small`, same protocol:

| hardening | gcc `Ir` | gcc ns | vs R1 | clang `Ir` | clang ns | vs R1 |
|---|---:|---:|---:|---:|---:|---:|
| *(none — R1, the bug)* | 3491.96 | 235.39 | — | 2691.96 | 222.78 | — |
| **`r %= m` (SHIPPED R1h)** | 3532.96 | 280.82 | **+19.30%** | 2646.96 | 245.14 | **+10.04%** |
| `if (r >= m) r %= m;` (`d_cmp`) | 3542.96 | 238.21 | **+1.20%** | **2646.96** | **224.20** | **+0.64%** |
| `while (r >= m) r -= m;` (`d_sub`) | 3560.96 | 239.51 | +1.75% | 2656.96 | 225.66 | +1.29%

Two things to read off it, and the second is the sharper:

1. **The cheapest in-contract hardening costs +1.20% (gcc) / +0.64% (clang) on
   `small`, against the textbook spelling's +19.30% / +10.04%** — a factor of 16.
   `.memory/02-bench-rules.md` forbids re-shipping a rung because a cheaper
   in-contract spelling was found, so the textbook line ships and both numbers
   are published, labelled, **with the input named**: on an input where `r >= m`
   is common the guarded form pays the branch *and* the divide, and this span is
   a `small`-and-`large`-shaped statement, not a universal one.
2. ⚠ **`d_cmp-clang` and `c-clang-h` execute exactly the same number of
   instructions — 2646.9640 both, to four decimals — and differ by 20.94 ns
   (−8.5%) in wall clock.** They are genuinely two different programs, not one
   binary measured twice: `n_fn_nopad` 167 vs 164, `md5_fn c0965f763fee` vs
   `5844f1e091cf`. One `Ir` figure, an 8.5% time difference, same compiler, same
   input. That is the tightest statement of *"instruction counts are not a cost
   model"* this project has produced, because there is no count difference left
   to explain it with — the 3-instruction static difference is a branch that is
   never taken, and what moves is which of them contains a `div` on the executed
   path.

### 3d. The `identity` pin's price on this pattern

R5's bulk load has to sit inside a `#[verifier::external_body]` item, so R4 must
call the same `#[inline(always)] fn scr_load` to stay byte-identical. Written
**inline** in `kernel` instead (`c_r4inline`), R4 is **179 instructions
(`md5_fn f7b24db6bfd9`)**; through the helper it is **208 (`897c52ff4005`)** —
LLVM clones the record loop for `nelem >= SCR` and inlines the 64-byte copy as
four `movups`. The *static* delta is +29 instructions; the **executed** delta is
`c_r4inline − R4ship` = **−4.00 Ir/call on `small` and −8.00 on `large`, flat in
`nrec`** (band N: `0.0000/record, −4.0000 flat`).

p12 published a static `n_fn` delta wearing a per-string label and had to correct
it; the figure to quote here is **4–8 Ir per call, flat**, and it is the second
measured price the `identity` pin has extracted from a shipped cell.

## 4. R2 against R4 — finding 12 does NOT replicate, and the mechanism is on the bytes

TASK_047 item 2 predicted that R2's four checks per swap would kill the bulk
lowering and that *"R2's gap therefore grows linearly in the rotated extent"*.

**It does not.** `R2 − R4 = 32.00·nrec + 13.00`, **`0.00000` Ir per rotated
byte**, `269.00` flat over all 46 values of `m` from 3 to 48 with zero residual,
and identical at `m = 31` and `m = 32`. TASK_047 said *"If it does not, that is a
stronger result; say which"* — it is the stronger result, and the mechanism is
not an inference:

**One loop at a time** (`controls/gen_controls.py` family E — R2's checked
spelling replaced by R4's unchecked one in exactly one loop and nothing else),
band N, 24 blobs:

| control | what is unchecked | `R2 − control` | kernel `md5_fn` |
|---|---|---|---|
| `e_revonly` | the **three reverses** | **0.0000/rec, 0.0000 flat** | `48e508ddf075` — **byte-identical to shipped R2** |
| `e_foldonly` | the **fold** | **0.0000/rec, 0.0000 flat** | `48e508ddf075` — **byte-identical to shipped R2** |
| `e_hdronly` | the **header decode** | **32.0000/rec, +13.0000 flat** | `897c52ff4005` — **byte-identical to shipped R4** |

The three terms sum to `32.0000` against a whole gap of `32.0000`, with no
interaction term. And the identity is on the **raw machine-code bytes**, which is
the only oracle `.memory/03-measurement.md` accepts:

> **Writing `get_unchecked` instead of `scr[a]` in the three reverse loops and in
> the fold produces the IDENTICAL 294-instruction kernel. rustc emits the same
> bytes. The whole of `R2 − R4` is the twelve indexed reads of the record
> header, and R2 with only those unchecked IS R4, byte for byte.**

**Why the rotate's checks are free, and it is the safety line that makes them
so.** `scr` is a `[u8; 64]` whose length is a compile-time constant, and
`r %= m` with `m = min(nelem, SCR)` proves `r < 64`; every cursor in the three
reverses satisfies `a < b <= max(r, m) <= 64`, so LLVM discharges all four checks
per swap. Delete the reduction and it cannot: `a_nored_safe_naive` measures
**408.00/record against shipped R2's 333.00 (+75.00)** and
`a_nored_safe_naive − a_nored_unsafe` is **102.00/record against the shipped
pair's 32.00** — the bounds-check tax **triples**.

> **So the safety line is not only free in `Ir` on the safe side, it is
> *profitable*: `r %= m` is the range hint that lets rustc delete safe Rust's
> bounds checks in the rotate. C pays a divide for it and Rust is paid for it.**
> This is p03's and p04's seeding result arriving on a **modulus by a runtime
> divisor** rather than by a constant, and from the opposite direction: on p03
> the invariant had to be handed to LLVM as dead code, and here the *bug fix*
> supplies it as a side effect.

**R3, by contrast, IS `O(n)`.** `R3 − R4 = 2.00000 Ir per byte of the live
extent`, exact for `m >= 4`. The idiomatic `split_at_mut` + `zip` + `mem::swap`
spelling is **dearer per byte than the naive indexed swap, which is free** — and
on `small` R3 is dearer than R2 outright (2958 vs 2797 kernel-exclusive), the
project's second R3 > R2 inversion after p09's. §8 has the in-contract spellings
that fix it.

## 5. The proof

`./verus_run.py patterns/p06-rotate/verus.rs` → **`17 verified, 0 errors`**;
`--cfg slb_twin` → **`22 verified, 0 errors`**. Both pinned in `spec.md` and
re-derived per item with `--verify-function <name> --verify-root`:

```
SCR 1 + fold_scr 1 + walk 1 + lemma_rev_noop 1 + lemma_rev_step 1
      + lemma_three_reverses 1 + kernel 6 + main 5   = 17
twin: 17 + 1 + 1 + 1 + 2 (slb_twin_scr_load has a LOOP)  = 22
```

**The postcondition is the FUNCTIONAL one** — the scratch ends up rotated left by
`r mod m` — and getting there was cheaper than TASK_047 budgeted for, because of
one design choice:

> **`rev_range` and `rot_left` are CLOSED FORMS (`Seq::new`), not recursions.**
> Every step of the proof is then a pointwise argument that `=~=` discharges, and
> the three lemmas verified **first try** (`5 verified, 0 errors` on the
> standalone scaffolding `.temp/p06/lem.rs`). A recursive `rev_range` would have
> needed an induction per lemma and two more obligations.

The two other choices that paid:

- **`rot_left` is stated with a branch on `i + r < m` instead of a modulo.** On
  the domain `0 <= r <= m` the two are the same function, and the branch keeps
  the entire specification inside **linear arithmetic**: there is no
  `by (nonlinear_arith)` anywhere in the kernel, on the pattern with the most
  loops in the project. p07's zero-nonlinear-arithmetic property, reached by
  choosing the spelling rather than by luck.
- **The cursor guards are subtraction-first** (`len - p < 8`, `len - p < nelem`).
  `p <= len` is maintained by the guards themselves so the subtraction cannot
  wrap; the additive `p + 8 > len` is a `usize` overflow Verus rejects, and
  buying it back costs either a second `requires` (p17's route) or a second
  driver conjunct. **That is what keeps the kernel's `requires` at ONE clause**,
  and all seven rungs use it, so no rung comparison moves on it. p07's lesson on
  a second pattern: the spelling that makes the proof trivial is the one that
  makes the bug impossible.

The only proof step that did not go first try was the `decreases` on the three
reverse loops: `decreases b - a` is rejected (`decreases not satisfied at end of
loop`) because the two cursors cross — at `a = 0, b = 1` the next state is
`a = 1, b = 0` and `b - a` goes negative. `decreases b` is the measure that
works, and it is worth writing down because every two-cursor loop in this project
will hit it.

## 6. The TCB, and the same disjointness fact discharged four ways

**Six `external_body` items, 11 body lines**, recounted against the gate's own
`tcb_items` record (`results/gate/p06-rotate.json`), which lists exactly these
six with body-line counts 1, 1, 3, 1, 4, 1:

| item | body lines | `requires` | twin? |
|---|---|---|---|
| `buf_get_unchecked` | 1 | `i < v@.len()` | yes |
| `scr_get_unchecked` | 1 | `i < v@.len()` | yes |
| `scr_set_unchecked` | 3 | `i < old(v)@.len()` | yes |
| `scr_load` | 1 | `n <= old(dst)@.len()`, `from + n <= src@.len()` | yes |
| `load_input` | 4 | *(none — it states no `ensures` either)* | n/a |
| `emit` | 1 | *(none)* | n/a |

⚠ **`scr_load` is one item more than this pattern should need, and the reason it
is here is NOT the reason TASK_047 and `.memory/04-verus.md` give.** Both say
*"there is no vstd spec for a bulk copy"*. **That is false at the pinned vstd**:

```
~/tools/verus/vstd/std_specs/slice.rs:205
pub assume_specification<T: Copy>[ <[T]>::copy_from_slice ](dst: &mut [T], src: &[T])
    requires old(dst)@.len() == src@.len(),
    ensures  final(dst)@ == src@;
```

Measured (`.temp/p06/vstdprobe/`): with the preconditions established, both of
`copy_from_slice`'s and both range-index preconditions **discharge**
(`cfs4.rs` — the only remaining error is the postcondition). What does *not* go
through is carrying the mutation back from a `&mut [u8]` **reborrowed out of a
`&mut [u8; 64]` by a range index**: `<[T; N]>::index_mut`'s `ensures` is an
existential over the intermediate slice and Z3 does not instantiate it. So the
honest statement is **"vstd specifies the copy; it is the array→slice reborrow
that is unproved here"** — a materially different claim, and it means `scr_load`
axiomatises the *write-back*, not the copy.

**The route that should work and was not taken**, because taking it would have
changed the exec text of four rungs after every number in this file was measured:
`<[T]>::split_at_mut` **is** specified and its `ensures` carries the write-back
explicitly (`final(slice)@ == final(ret.0)@ + final(ret.1)@`,
`slice.rs:185`). Landing it would take p06's TCB from 6 items to 5 and delete an
axiom. **Open, with the probes committed to `.temp/p06/vstdprobe/`.** The same
correction applies to p02, whose `copy_bytes` comment cites the same false claim.

**The four trusted bases for ONE fact.** The disjointness question — *may I hold
`scr[a]` and `scr[b-1]` at once?* — is answered four different ways by the four
Rust rungs, and this is p06's structural result rather than a speed one:

| rung | how the fact is discharged | trusted base | cost (band N) |
|---|---|---|---|
| **R2** | it is never asked: four separate, momentary indexed accesses, each bounds-checked | **zero** | `+32.00/rec` — **and none of it is here** (§4) |
| **R3** | `split_at_mut` proves it in the type system | **`core`'s `unsafe`** — `from_raw_parts_mut` on the two halves, plus `mem::swap` = `ptr::swap_nonoverlapping`; audited by nobody in this repository | `+51.00/rec` |
| **R4** | the programmer asserts it in a comment | **the whole function** | 0 |
| **R5** | `scr_set_unchecked`'s `i < old(v)@.len()`, discharged twice per swap from the loop invariant | **one clause**, 3 body lines | 0 |

Note the shape of that table: **the rung with the smallest trusted base and the
rung with the largest cost are not the same rung, and the rung with `std`'s
unsafe is the most expensive of the four.** R3 pays 51 Ir/record for a fact R2
gets for free and R5 proves for nothing.

### SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

(a) *Is the twin's body the right checked stand-in?* The trusted body is
`unsafe { *v.get_unchecked(i) }` and the twin's is `v[i]`. The two are the same
operation with and without the bounds check that `get_unchecked`'s documented
contract asks the caller to have discharged, so a `requires` too weak to license
the first is too weak to license the second — and Verus can see the second. That
is the whole mechanism, and it is the accessor p01, p02, p03, p05, p07, p11, p12,
p13, p16 and p17 all ship character for character.

(b) *Is the `ensures` complete with respect to every unchecked operation the body
performs?* The body performs exactly one unchecked operation, a read of `v` at
`i`, and returns its value. `r == v@[i as int]` names that value. There is no
second index, no width other than one `u8`, no write, and no state to change: `v`
is a `&[u8]`, so the item cannot mutate anything and the postcondition has
nothing else to say. This is the clause a reviewer should attack first — the
failure mode `.memory/04-verus.md` names is a body that *also* reads `i + 1`,
which would pass the contract pin, the twin and the `--cfg slb_twin` run
unchanged, and the only backstops for it are the O3 identity pin against R4 and
Miri on R4. Both run on p06 and both are green.

(c) *Does each clause mean the same in both configurations?* `i`, `v@.len()` and
`v@[i as int]` are the same spec expressions in both, over the same `&[u8]`
parameter; nothing in the item is `#[cfg]`-dependent and the `slb_twin` token
appears only in the twin's own attribute (the gate checks that). So the two
configurations differ in the body and in nothing else.

### SLB-TRUSTED-ARGUMENT verus.rs scr_get_unchecked

(a) *Is the twin's body the right checked stand-in?* The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[u8; 64]` and the twin's is `v[i]`. Same
argument as `buf_get_unchecked`, on an array rather than a slice: for a
`&[u8; 64]` vstd's `array_len_matches_n` supplies `v@.len() == 64` from the
parameter type alone, so the twin's `v[i]` obligation is `i < 64` and it is
exactly what the trusted `requires` states.

(b) *Is the `ensures` complete?* The body performs one unchecked read of `v` at
`i` and returns it. `r == v@[i as int]` names it. `v` is a shared reference, so
no state can change. Note what this item is used for and why the single conjunct
is enough: it is called twice per swap in each of the three reverse loops and
once per byte in the fold, always at an index the loop invariant bounds by `SCR`.

(c) *Does each clause mean the same in both configurations?* Yes — the
`requires` and `ensures` texts are character-identical between the trusted item
and the twin, over identically-typed parameters, and neither mentions a
`#[cfg]`-varying constant. `SCR` does not appear in either clause; the bound is
`v@.len()`, which is a property of the parameter's type.

### SLB-TRUSTED-ARGUMENT verus.rs scr_set_unchecked

(a) *Is the twin's body the right checked stand-in?* The trusted body is
`unsafe { *v.get_unchecked_mut(i) = x; }` and the twin's is `v[i] = x;`. Verus
gives an indexed store on a `[u8; 64]` an `IndexSetTrustedSpec` obligation of
`i < v@.len()`, which is the same fact `get_unchecked_mut` requires the caller to
have discharged. **Measured, not asserted:** `controls/gen_controls.py`'s
`b_weakreq` weakens the shared `requires` to `i <= old(v)@.len()` in the trusted
item *and* in the twin, and the shipped configuration still reports
**`17 verified, 0 errors`** while `--cfg slb_twin` reports
**`21 verified, 1 errors — precondition not met: index in bounds for this
access`**. So on p06 the twin is the **sole** catcher, which is the third pattern
where that has happened. **This is the item p06 exists for** — it is the write
the buggy C rung performs past `scr[SCR]`, and it is called *twice* per swap, at
`a` and at `b - 1`, so the `requires` has to hold at both ends of every reverse.

(b) *Is the `ensures` complete?* The body performs one unchecked write, of `x`
into slot `i`, and nothing else — no read it returns, no second slot, no
reallocation. The postcondition is a **whole-sequence** equality,
`final(v)@ == old(v)@.update(i as int, x)`, so it says both *"slot `i` became
`x`"* and *"nothing else moved"*. That second half is load-bearing here in a way
it is not elsewhere: `lemma_rev_step` is stated as a composition of two
`update`s, so an `ensures` that pinned only slot `i` would not compose and the
reverse loops' invariant could not be carried at all. It also rules out p08's
failure mode directly — a body that additionally wrote `i + 1` disagrees with
`old(v)@.update(i, x)` at slot `i + 1`. What the clause cannot see is a body that
writes the right value to the right slot by a route with other side effects, and
for that the backstops are the O3 identity pin against R4 and Miri on R4, both
green.

(c) *Does each clause mean the same in both configurations?* Yes. `i`,
`old(v)@.len()`, `final(v)@` and `old(v)@.update(i as int, x)` are the same spec
expressions over the same `&mut [u8; 64]` parameter in both, and no
`#[cfg]`-varying constant appears. `x` carries no precondition and `spec.md`'s
`verus.unsafe_justifications` says why: it is a pure value parameter, stored and
never used as an address, an index or a length, so there is nothing a caller
could usefully be asked to guarantee about it. The gate shouts that justification
every run.

### SLB-TRUSTED-ARGUMENT verus.rs scr_load

(a) *Is the twin's body the right checked stand-in?* The trusted body is
`dst[..n].copy_from_slice(&src[from..from + n]);` and the twin's is an indexed
loop `dst[j] = src[from + j]` for `j` in `0..n`. p02's wrinkle applies: the
checked stand-in for a bulk copy is the element-wise loop, and the loop performs
exactly the reads and writes the bulk call performs, at the same indices, in
checked code. Weaken `from + n <= src@.len()` and the twin fails at
`src[from + j]`; weaken `n <= old(dst)@.len()` and it fails at `dst[j]`. That the
twin *verifies* (`2 verified` under `--cfg slb_twin`) is what rules out the
false-failure reading of this stage.

(b) *Is the `ensures` complete?* The body performs one bulk copy of `n` bytes
from `src[from ..]` into `dst[0 ..]` and nothing else. `load_into` is a
whole-array equality: slots `[0, n)` become `src[from + i]` and **every slot from
`n` up is the byte that was already there**. The second half is load-bearing on
p06 in a way it is not on p02: the scratch is *not* re-zeroed between records, so
`scr[m .. SCR)` carries the previous record's bytes, and regime 1 reads exactly
those. An `ensures` that said nothing about them would leave `walk`'s state
under-determined and the record loop's invariant unprovable. What the clause does
not cover is aliasing between `src` and `dst`: it cannot, because `&[u8]` and
`&mut [u8; 64]` cannot name the same allocation in safe Rust, so the
disjointness `copy_from_slice` needs is discharged by Rust's own reference rules
rather than by this contract. ⚠ **And the part of this item that is a genuine
axiom is narrower than it looks** — see §6's vstd note: the pinned vstd
*specifies* `copy_from_slice`, so what this `ensures` really assumes is the
array→slice reborrow write-back, which `split_at_mut` would discharge. The body
contains **no `unsafe`**; it is TCB anyway, because `.memory/04-verus.md` counts
every `external_body` item.

(c) *Does each clause mean the same in both configurations?* Yes. Both `requires`
and the `ensures` are character-identical between the trusted item and the twin,
over identically-typed parameters, and `load_into` is one `open spec fn` used by
both. The only `#[cfg]` in the pair is the twin's own `#[cfg(slb_twin)]`.

## 7. The two regimes, per rung — and what safe Rust does with the check deleted

The delete-the-check controls (`controls/gen_controls.py` family A: the reduction
removed from `safe_naive.rs`, `safe_tuned.rs` and `unsafe.rs` and **nothing
else**, hit count asserted). All three agree with `model.py` on `small`, `large`
and `degenerate`, where `r < m` makes the reduction a no-op — so they differ from
the shipped rungs **only** where the bug fires.

**REGIME 1** (`adversarial-inarray.bin`, `m <= r <= SCR`):

```
c-gcc  (R1)               exit 0   12407484466270198528
c-clang(R1)               exit 0   12407484466270198528
a_nored_safe_naive        exit 0   12407484466270198528     <- SAFE Rust, zero `unsafe`
a_nored_safe_tuned        exit 0   12407484466270198528     <- SAFE Rust, zero `unsafe`
a_nored_unsafe            exit 0   12407484466270198528
                (model, and all six shipped checked cells: 5453190234444350336)
```

> **Five unchecked programs — C under two compilers, two safe-Rust rungs with no
> `unsafe` anywhere, and unsafe Rust — print the SAME wrong answer, bit for bit,
> on a WRITE bug, with exit 0, no panic, and ASan+UBSan clean.** That is p06's
> strongest single row and it is what the pattern was built to produce. p17's
> "limit" result is a *read*; this one is a write into a fixed local that the
> borrow checker, the bounds checks and both sanitizers all permit, because it
> never leaves the array.

**REGIME 2** (`r > SCR`), the same five programs:

| input | `r` | past `scr` | c-gcc | c-clang | `a_nored_safe_naive` | `a_nored_safe_tuned` | `a_nored_unsafe` |
|---|---:|---:|---|---|---|---|---|
| `adversarial-past1` | 65 | 1 | 0, `231815783968535` | 0, `3511210252634240` | **101 panic** | **101 panic** | 0, `1183642181752691` |
| `adversarial-past48` | 112 | 48 | **134** canary | 0, `497` | **101 panic** | **101 panic** | 0, `14544551909971626112` |
| `adversarial-pastfar` | 100000 | 99936 | **139** | **139** | **101 panic** | **101 panic** | **139** |

The safe-Rust panics are `safe_naive.rs:102:25` (`let u: u8 = scr[b - 1];`) and
`safe_tuned.rs:105:40` (`&mut scr[a..b]`) — the index and the *range*
respectively, which is why R3's `if a < b` guard is in the shipped spelling: it
keeps the second reverse's empty range from panicking on the range rather than on
the index and hiding which regime the control is in.

**Read the two tables together and the separation is exact**: bounds checking
kills regime 2 and is completely blind to regime 1, and the two regimes are one
constant apart in one attacker field. Note also the free discriminator: **the two
C compilers agree with each other in regime 1 and disagree in regime 2**, because
regime 1's excess bytes are the zero-initialised scratch and regime 2's are
whatever the frame held.

**p06 does NOT inherit `.memory/02-bench-rules.md`'s WRITE rule**, and the
threshold test in that section is what decides it: the guard's threshold is
`m = min(nelem, SCR)`, at most and usually strictly *inside* the destination's
extent, so *"the guard fired"* and *"the unguarded rung committed UB"* are
**independent** events and regime 1 is exactly where they separate. p12, p23 and
p25 inherit because their threshold **is** the extent; p06 sits with p24. This is
the first time that test has been applied to a pattern being *built* rather than
one being audited, and it is what makes `adversarial-inarray` possible at all.

## 8. The spelling spread, the priced fiats, and the in-contract R3-side span

`spec.md` deliberately does **not** pin the spelling of the swap — that is the
free parameter this pattern measures, exactly as p12 leaves the copy free. Six
variants (`controls/gen_controls.py` family C), whole-program marginal, against
the **shipped R4 held fixed by fiat**:

| variant | spelling | `small` | `large` | in contract? |
|---|---|---:|---:|---|
| `c_idx` | R3's reslice + fold, R2's indexed swap | **+80.00** | +187.00 | yes |
| **R3ship** | `split_at_mut` + `zip` + `mem::swap` | +334.00 | **+172.00** | yes (shipped) |
| `c_oneshot` | R3ship with `&buf[off..off+len]` | +335.00 | +173.00 | yes |
| `c_swap` | `<[T]>::swap(j, n-1-j)` | +490.00 | +286.00 | yes |
| `c_reverse` | `scr[a..b].reverse()` | −358.00 | +320.00 | **FORBIDDEN** |
| `c_rotate` | `scr[..m].rotate_left(r)` | −951.00 | +314.00 | **FORBIDDEN** |

- **In-contract R3-side span: `+80.00 … +490.00` on `small`, `+172.00 … +286.00`
  on `large`.** ⚠ **The cheapest found differs between the two blobs** — `c_idx`
  on `small`, shipped R3 on `large` — which is the fifth pattern to reproduce
  *"a cheapest-found figure must name its INPUT as well as its spelling"*. Write
  "cheapest found", never "minimum".
- **The fixed-R4 bound is `+334.00 / +172.00`** (`R3ship − R4ship`), and it
  bounds `inf(in-contract R3) − R4ship` from above and **nothing else**.
- **The two-step reslice is worth exactly `1.00 Ir/call`**, on both blobs
  (`c_oneshot` is `+1` on each). `.memory/01-ladder.md` finding 3's p04 lever
  reproduces on a **sixth** pattern, at the same magnitude, and the shipped R3
  already carries it.
- **The R4 side is DEGENERATE**, and that word rather than "unsearched": the one
  R4 variant built (`c_r4inline`) measures `−4.00 / −8.00` and **is not a rung**,
  because it breaks the `identity` pin (179 instructions against R5's 208). So
  the R4 endpoint has zero admissible measured width and the pair interval
  collapses onto the R3-side span. It stops being degenerate the day somebody
  builds an admissible R4 that moves.

### The forbidden spellings, PRICED — and put through the prover, not asserted

`.memory/01-ladder.md`'s newest rule: price every exclusion and dispose of it on
what the price says. p06's exclusions are **whole-pattern**, not scoped to some
rungs — the shape that fired the direction test on p13 is absent by
construction — but a whole-pattern fiat still has a price:

| spelling | at the pinned vstd | measured price | disposition |
|---|---|---|---|
| `<[T]>::reverse()` | **`is not supported`** | −358 / +320 vs R4ship | **KEEP** — the prover already excludes it from R4, so the declaration costs nothing extra. p13's middle case. |
| `<[T]>::rotate_left()` | **`is not supported`** | −951 / +314 | **KEEP** — same. |
| `<[T]>::swap()` | **`is not supported`** | +490 / +286 | not forbidden; R3 may use it, and it is the *dearest* in-contract spelling, so nothing turns on it |
| `split_at_mut` | **supported** (`precondition not satisfied` only) | R3's shipped spelling | — |
| `core::mem::swap` | **`2 verified, 0 errors`** | R3's shipped spelling | — |

(`.temp/p06/vstdprobe/*.rs`, one spelling per file — a shared probe reports every
spelling's error on every run, because `--verify-function` still type-checks the
whole file. Measured after making exactly that mistake.)

**So both forbidden entries fall into p13's "keep — the exclusion is one layer
down" bucket**: an R4 could not spell them at the pinned vstd, so forbidding them
on the *safe* side is what keeps the comparison symmetric rather than a thumb.
The price is published anyway, because the numbers are large and blob-dependent:
excluding them costs the safe side **1031 Ir/call on `small`** (cheapest
forbidden `−951` against cheapest in-contract `+80`) and **nothing on `large`**,
where the library forms are dearer than every in-contract spelling. The direction
test: the exclusion makes p06's published safety figure **larger**, i.e. moves it
*against* the author's thesis, so it is not self-certification under either
reading of the test.

### The C hardening span

§3c. Shipped `r %= m` and cheapest-found `if (r >= m) r %= m;`, both labelled,
input named.

## 9. The sweep, the rank of the pooled design, and the out-of-sample test

`inputs/gen.py --sweep` emits **140 blobs in five bands**, appended last so the
eight matrix blobs stay byte-identical. **Determinism verified as
`.memory/05-layout.md` requires**: generated twice and diffed — *"DETERMINISTIC:
148 blobs byte-identical across two runs"*.

| band | held fixed | swept | n |
|---|---|---|---|
| `sweep-n*` | `m = 16`, `r = 2` | `nrec` 1…24 | 24 |
| `sweep-m*` | `nrec = 8`, `r = 2` | `m` 1…48 | 48 |
| `sweep-r*` | `nrec = 8`, `m = 32` / `m = 31` | `r` over the whole legal range | 63 |
| `sweep-x*` | — | five heterogeneous shapes, **every regressor non-zero at once** | 5 |

**Rank of the pooled design** (`controls/fit.py`, exact rational elimination over
`1, nrec, sum_m, parity, rzero`), reported *before* any coefficient is believed:

```
   m        n= 48  rank=3 of 5
   n        n= 24  rank=2 of 5
   r        n= 63  rank=4 of 5
   x        n=  5  rank=4 of 5
   POOLED   n=140  rank=5 of 5
```

Every band is rank-deficient on its own; **only the pooled design identifies the
terms**, which is p03's shape. Band X is what lifts it, and it carries a
**within-band negative control**: `sweep-x08a` and `sweep-x08b` have identical
regressors and different bytes, and every one of the eight cells measures them
the same to **0.003 Ir** — a predicted delta of 0 and a measured one of 0.003.

**Pooled fits of the matched differences** (bands N + M + X, 77 blobs, rank 5/5):

```
verus - unsafe    : all five coefficients exactly 0, max |residual| 0.0000
c-gcc-h - c-gcc   : 1.00 + 8.00*nrec + 0.00*sum_m + 0.00*parity - 1.00*rzero,
                    max |residual| 0.0000
safe_naive - unsafe: 13.15 + 31.99*nrec - 0.0001*sum_m + 0.54*parity - 0.99*rzero,
                    max |residual| 2.84
```

**LEAVE-ONE-`m`-OUT, which is the out-of-sample test TASK_047 asked for and the
one p13's could not fail.** Drop every band-M blob at one `m`, fit on the rest
over `{sum_m} ∪ {indicator(m mod 8)}` (no separate intercept — the eight
indicators already sum to 1), predict the dropped point:

| difference | worst out-of-sample miss, `m` 4…48 |
|---|---|
| `c-gcc-h − c-gcc` | **0.000** |
| `c-clang-h − c-clang` | **0.000** |
| `safe_naive − unsafe` | **0.000** |
| `safe_tuned − unsafe` | **0.000** |

**The test can fail, and it does.** On the domain `m >= 3` the same test misses
`safe_tuned − unsafe` by **−48.000 at `m = 3`** and by `+7…+12` at every other
member of that residue class, because `m = 3` is a different program: the fold's
4× unroll cannot run and the three reverse ranges are 2/1/3. **So the law's
domain is `m >= 4` and that is measured rather than assumed** — a non-vacuous
out-of-sample test, unlike one that cannot fail.

**And the strongest out-of-sample statement is on a shipped input.** `small.bin`
is **length-heterogeneous** — five records with five *different* `m` (13, 47, 29,
61, 7), none of which any band visits — which is queue item 11's missing band
arriving as a *perf row*. The band-fitted laws predict it with zero free
parameters:

```
R2 - R4 :  32*5 + 13                       = 173   measured 173.00
R3 - R4 :  2*157 + sum(alpha(m mod 8)) + 1 = 334   measured 334.00
R1h - R1 (gcc)   :  8*5 + 1 - 1*0          =  41   measured  41.00
R1h - R1 (clang) : -9*5                    = -45   measured -45.00
```

Four laws, four exact hits, on an input outside every band. The gcc law also hits
`large` exactly (`8*12 + 1 - 1*2 = 95`) and the clang one misses it by 1. ⚠ **`large.bin` is
NOT predicted**: its `m` run 1…8, mostly below band M's clean domain, and
`R3 − R4` misses by 47 there. That is the domain statement doing its job, and it
is why both are reported.

## 10. The proof mutants

`controls/gen_controls.py` family B, `controls/verify_controls.sh`, both
configurations:

| mutant | what changed | shipped | `--cfg slb_twin` | caught by |
|---|---|---|---|---|
| `b_nored` | the reduction **deleted**, contract untouched | **16 / 1** `invariant not satisfied before loop` | 21 / 1 | Verus |
| `b_nored_msonly` | deleted **and** the postcondition weakened to memory-safety-only | **16 / 1**, the same error | 21 / 1 | Verus |
| `b_scrmod` | `r %= SCR` (the **wrong modulus**), contract untouched | **16 / 1** `precondition not satisfied` (at `lemma_three_reverses`) + `assertion failed` (at the driver's consuming assert) | 21 / 1 | Verus |
| **`b_scrmod_msonly`** | `r %= SCR` **and** memory-safety-only | **17 / 0** | **22 / 0** | **nothing but `spec.md`'s contract pin** |
| `b_weakreq` | `i < old(v)@.len()` → `i <= …` in the trusted item *and* the twin | **17 / 0** — undetected | **21 / 1** `precondition not met: index in bounds` | **the twin alone** |
| `b_tautology` | the kernel `ensures` → `r == r`, nothing else | **16 / 1** `assertion failed` | 21 / 1 | the driver's consuming assert |

Four results, and three of them were not what the task file predicted:

1. ⚠ **`b_nored_msonly` FAILS, and that is the sharper finding.** TASK_047
   expected the memory-safety-only spec to *accept* the buggy kernel. It cannot:
   **a proof quantifies over all inputs, and the unreduced kernel is genuinely
   memory-unsafe in regime 2.** A weaker *spec* cannot rescue it. This is p17's
   control-2 lesson arriving on a second pattern — **the separation between
   "functionally wrong" and "memory-unsafe" needs a PROGRAM change, not an input
   and not a weaker postcondition.**
2. **`r %= SCR` is that program change, and it is one identifier from the
   contract.** Memory-safe on every input (`r < 64 == scr.len()`, so every index
   the three reverses touch is in bounds in *both* regimes); functionally wrong
   on exactly regime 1's set. `b_scrmod_msonly` therefore **verifies, 17 / 0 and
   twin 22 / 0**, and the compiled binary is a *verified, `unsafe`-using program
   whose memory-safety obligations all discharge* which nonetheless prints
   `415744194194585216` on `adversarial-inarray.bin` where the model says
   `5453190234444350336` — and agrees with the model on `small`, `large` and
   `degenerate`. **That is the mutant that earns its keep**, and it is the
   complement of p09, where the bug went invisible *even to the spec* once the
   spec moved with it: here the two specs disagree on the same program.
3. **`b_weakreq` is caught by the verified twin and by nothing else**, on a
   weakening applied to the item *and* the twin in one edit — which is what a
   real single-commit weakening looks like. Third pattern where the twin is the
   sole catcher, and the first on a write accessor called twice per iteration.
4. **`b_tautology` does not verify**, where p02's M7 did. The driver's consuming
   `assert(r == rotate_fold(...))` still names the real spec, so weakening the
   kernel's postcondition breaks the *call site*. That is the
   `ensures`-is-load-bearing property measured rather than argued
   (`.memory/04-verus.md`).

## 10a. When the declaration was written, stated exactly

`spec.md`'s `idiom.why` says this and it is repeated here because p06 is the
first pattern with a **pre-flight**, and "the declaration was written before any
number existed" would be false:

- The `idiom` block was written **after** the five rungs, the R5 proof (`17/0`),
  the `identity` pin and the checksums existed, and **before** any p06 *cell* had
  been measured for perf — `harness/measure.py p06` had not been run and no `Ir`
  or `ns` figure for any of the eight cells existed.
- What **did** exist is §0: `Ir` and `ns` for a standalone six-kernel **C probe
  with no driver**, which is what settled TASK_047's three prescriptions before
  five rungs were built on them. That probe is not a cell and none of its numbers
  is published as p06's.
- What the probe influenced is the **choice of pattern shape** — `u8` elements
  rather than the `u32` the task file specifies, because `copy_from_slice` from
  `&[u8]` into `&mut [u32]` does not typecheck and every non-bulk route
  (`chunks_exact`, `from_le_bytes`, `try_into`) is `is not supported` at the
  pinned vstd, so with `u32` elements the load could not have had one spelling in
  every rung and R4 could not have had a verifying twin. The probe also
  established that the change is safe: with `u8` elements the three reverses are
  **still three scalar swap loops** in both compilers, with no `pshufb` and no
  vector register (`.temp/p06/probe2_kernel_u8.c`).
- What the probe did **not** influence is any entry of `required` or `forbidden`,
  every one of which names a line the Semantics block of `spec.md` already had.

## 11. What p06 does not have, and what is open

- **No `ns` claim below the ±3% inter-binary floor.** §3b's `R5 − R4` null is
  `+3.00% / −1.41%` on byte-identical kernels, so `safe_naive − unsafe`
  (`+6.44% / +13.39%`) and `safe_tuned − unsafe` (`+5.95% / +0.60%`) are
  reported and **not** headlined; only the `R1h − R1` figures (+9.8% … +57.1%)
  clear the floor by a comfortable multiple.
- **No layout population.** `common/layout/order.py` knows only the three Rust
  cells and p06's headline is a C-vs-C comparison, so `controls/wall_span.py`
  re-implements the identical-copy floor and the alternating schedule over an
  arbitrary binary list. What it does **not** do is build a 30-layout population
  (`.memory/03-measurement.md`'s `win32`/`jcc32` modes). The `R1h − R1` effects
  are 6–19× the identical-copy floor, so a layout mode could not plausibly
  account for them, but that is an argument and not a measurement.
- **`scr_load` should not need to be trusted.** §6: the pinned vstd *does*
  specify `copy_from_slice`; the unproved step is the `&mut [u8; 64]` → `&mut
  [u8]` range reborrow, and `split_at_mut`'s specification carries exactly the
  write-back that would close it. Landing it takes the TCB from 6 items to 5 and
  changes the exec text of four rungs, so it was not done after the numbers were
  measured. Probes: `.temp/p06/vstdprobe/cfs*.rs`.
- **The `Ir`/`ns` sign disagreement is measured on two compilers and one box.**
  It is a property of *this* `div` on *this* microarchitecture; the `Ir` side is
  simulator-exact and portable, the ns side is not.
