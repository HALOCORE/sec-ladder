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
| **`R1h − R1`, gcc** | **`+8.00·nrec − 1.00·rzero + 1.00`**, and `0.00000` per byte. ⚠ **Only `1.00` of that `8.00` is the divide** — see 3a′, which decomposes it and shows that `1.83` of it is *executed alignment padding* | **max residual 0.0000 over all 77 blobs** of bands N + M + X, `m` 1…48 including the degenerate `m = 1, 2` |
| **`R1h − R1`, clang** | **`−10.00·nrec` (`m ≡ 0 mod 4`) / `−9.00·nrec` (otherwise) / `−8.00·nrec` (`m <= 2`, where every `r` reduces to 0)**, and `0.00000` per byte | exact per residue class over `m` 1…48; the pooled fit without residue regressors leaves 6.04 |
| `R2 − R4` | `+32.00·nrec + 13.00`, **`0.00000` per byte** | exact; `269.00` flat over all 46 `m` in 3…48 |
| `R3ship − R4` | **`2.00000` Ir per byte of the live extent**, plus `α(m mod 4)·nrec + 1` with `α = {0: 19, 1: 3, 2: 22, 3: 5}`. ⚠ **This is ONE SPELLING's law, not R3's** — see 4a; and the residue period is **4, not the 8 published until TASK_048** | exact for `m >= 4`, 45/45; `m = 3` is an outlier (§9) |
| **`c_idx − R4`** — the **cheapest-found in-contract R3 on `small`** | **`0.00000` Ir per byte**, `α′(m mod 4)·nrec + 1` with `α′ = {0: 13, 1: 15, 2: 16, 3: 17}` | exact, 45/45 over `m` 4…48 (§9a) |
| `R5 − R4` | **`0.00000` everywhere** | pooled fit over 77 blobs, **all five coefficients exactly 0, max residual 0.0000** |

**So the safety line has NO per-byte term on either compiler.** It executes once
per record and it is priced once per record — and it is why the sign result below
cannot be a size artefact. ⚠ **What it is NOT is "what a per-record check should
cost"**, which is what this paragraph said until TASK_048; 3a′ decomposes the
`8.00` and only `1.00` of it is the check.

### 3a′. The gcc law decomposed — 23% of it is EXECUTED ALIGNMENT PADDING

TASK_047_REVIEW's M2, re-measured here. Per-instruction callgrind
(`--dump-instr=yes`, `.temp/p48/cg/al.*.out`) on `large`, 12 records/call, at the
gate's own flags. The delta is `+95.00`/call exactly, i.e. `+7.917`/record:

| mnemonic | R1 → R1h, Ir/call | per record | what it is |
|---|---:|---:|---|
| `divq` | 0.00 → 12.00 | **+1.000** | **THE SAFETY LINE** |
| `nopl` + `nop`, net | 13.00 → 35.00 | **+1.833** | **EXECUTED `.p2align` PADDING** |
| `movzbl` | 282.00 → 330.00 | +4.000 | the header decode, re-materialised |
| `movb` | 130.00 → 154.00 | +2.000 | **two byte SPILLS**, named below |
| `xorl` | 29.00 → 40.00 | +0.917 | |
| `movq` | 244.00 → 246.00 | +0.167 | |
| `cmpq` | 174.00 → 162.00 | −1.000 | |
| `jae` | 24.00 → 12.00 | −1.000 | |
| | | **= +7.917** | |

The two spills are not inferred, they are named: `movb %r15b,0x17(%rsp)` at
**12.00/call** and `movb %dl,0x16(%rsp)` at **12.00/call**, both **0.00 in R1**.
The `div` and its zero-guard push gcc into spilling two decoded header bytes.

**A semantics-free flag moves the law by 23%.** Same sources, same inputs, one
gcc flag that changes no semantics and no work:

| gcc flag | R1 Ir/call | R1h Ir/call | Δ | Δ/rec | executed nops R1 / R1h |
|---|---:|---:|---:|---:|---|
| shipped (`-O3`) | 1988.00 | 2083.00 | **+95.00** | +7.917 | 25 / 47 |
| `-fno-align-loops` | 1963.00 | 2036.00 | **+73.00** | +6.083 | 0 / 0 |
| `-falign-loops=1` | 1963.00 | 2036.00 | +73.00 | +6.083 | 0 / 0 |
| `-falign-loops=32` | 2058.00 | 2153.00 | +95.00 | +7.917 | 95 / 117 |

> **A law can be exact, zero-residual and validated out of sample and still be
> 23% alignment padding.** `.memory/03-measurement.md:234` records the *static*
> nop caveat — "the raw count overstates the gap". The **dynamic** one is this:
> executed `.p2align` padding inside a hot loop lands in a published `Ir` law,
> and no residual can see it because it is exactly as reproducible as the work.
> It reaches a second p06 law independently — §9a's `[k > 0]` term is one
> executed `nop` at `0x15a4f`.

**And it reconciles §0b with §3a, which nothing joined until now.** §0b's
standalone probe measures gcc `mod − bug = +1.00`/record and §3a measures
`+8.00`/record on the shipped tree, 8× apart. The honest decomposition of the
8.00 is **1.00 the divide, 1.83 executed padding, and 5.08 the register pressure
the `div` and its guard put on the header decode** (the `movzbl`/`movb`/`xorl`
rows above, net). The probe has no driver, no record loop and no spill, so it
sees the 1.00 and nothing else. Both numbers are right; they measure different
things and the file now says which.

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
**Take ±4.6% as the honest inter-binary floor for every `ns` figure in this
file**; the within-copy floor (0.45–2.05%) is a lower bound on noise, not the
whole of it. ⚠ **This number was ±3% until TASK_050 and ±3% is a slight
UNDER-estimate** (TASK_049_REVIEW m2, measured on a 24-layout population per
cell): p06's own within-cell layout spread is **4.02% (`unsafe`) / 5.10%
(`verus`)** and its `R5 − R4` cross-pair range is **−4.31% … +4.61%**. **Nothing
of p06's falls**: the clang column (+9.78% / +10.56%) still clears ±4.6% at
~2.1×, and p06's 30-layout C population (§3c) defends the headline
independently. ⚠ **Two later sentences in this file still say "the ±3% floor"**
(§3b's *"a multiple of the ±3% floor"* and §11's first bullet); TASK_050 was
scoped to this number alone and did not edit them, and both remain true at
±4.6% — read them against this paragraph.

**THE HEADLINE — the two columns and their disagreement:**

| | `Ir`/call | ns/call | |
|---|---|---|---|
| gcc `R1h − R1`, `small` | **+41.00 (+1.17%)** | **+45.63 (+19.46%)** | `Ir` understates **17×** |
| gcc `R1h − R1`, `large` | **+95.00 (+4.74%)** | **+88.10 (+57.09%)** | `Ir` understates **12×** |
| clang `R1h − R1`, `small` | **−45.00 (−1.67%)** | **+21.78 (+9.78%)** | **the signs disagree** |
| clang `R1h − R1`, `large` | **−108.00 (−5.65%)** | **+15.35 (+10.56%)** | **the signs disagree** |
| `R5 − R4` (the null) | 0.00 exactly | +3.00% / −1.41% | the floor |

Every one of the four is a multiple of the ±3% floor, and **all four survive a
30-layout population** (3c′: gcc `large` +57.87%, clang `large` +11.60%, no sign
flip anywhere, worst-case layout pair still +53.7% on gcc).

**gcc's `large` figure IS the divide, and that is now a control rather than an
inference.** The attribution used to rest on a cycle estimate — *"7.34 ns/record,
≈ 21–28 cycles at this box's 2.8–3.9 GHz band"* — which needs a frequency nobody
measured. `d_cmp-gcc` replaces it: it contains the guard **and** the `div`
instruction but never *executes* the `div` on either perf input, because every
`r < m` there. On `large` it costs **+7.58 ns** where `c-gcc-h` costs **+88.01
ns**, so **91.4% of gcc's `large` hardening cost is the executed divide** — 6.70
ns per record for one `div r64`. The throughput column makes it plainer than any
cycle estimate can (whole-program marginal `Ir` over the population's ns):
`c-gcc` **13.17** Ir/ns, `d_cmp-gcc` **13.24** Ir/ns, `c-gcc-h` **8.74** Ir/ns. The two div-free gcc cells run at the *same* instructions per
nanosecond, so there is no anomalous IPC left to explain; the cycle sentence is
withdrawn as unnecessary rather than wrong.

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

⚠ **Until TASK_048 this table existed for `small` only, while p06's largest
published number is the `large` one.** `.memory/02-bench-rules.md`'s two-number
rule is *publish the fixed spelling and the cheapest found, both labelled, with
the input named* — so it was satisfied on one input and not on the one that
carries the headline. **3c′ is the missing half**, and it is where the sharper
result was hiding.

### 3c′. Both inputs, over a 30-LAYOUT POPULATION — and on `large` under clang, HARDENING IS FASTER THAN THE BUG

`controls/clayout.py` (built at TASK_047_REVIEW as clean negative CN-1, moved
into the pattern at TASK_048 so these numbers have a generator in the tree).
`common/layout/order.py:48` and `layout_gen.py:59` hardcode
`CELLS = ["safe_naive","safe_tuned","unsafe"]` and build with `rustc`, so
neither can touch a C cell; the lever here is a **pad object**
(`asm(".text\n.space N")` linked first, `N = 0,16,…,464`), which shifts every
later `.text` symbol without touching a byte of `kernel.o`.

Controls, the same ones `layout_gen` asserts: `n_fn` single-valued per cell
(190 / 200 / 175 / 171 / 205 / 175 / 214 / 175), `md5_fn_norel` single-valued,
**30 distinct kernel addresses** spanning both `addr % 32` residues, and one
stdout per cell. Estimator: median over the 30 layouts of the per-layout min of
5 reps, alternating, `taskset -c 5`, `(t(200000) − t(1))/199999`.

| cell | `small` ns/call | vs R1 | `large` ns/call | vs R1 |
|---|---:|---:|---:|---:|
| `c-gcc` (R1, **the bug**) | 234.40 | — | 152.08 | — |
| **`c-gcc-h` — `r %= m`, SHIPPED** | **278.54** | **+18.83%** | **240.09** | **+57.87%** |
| `d_cmp-gcc` — `if (r >= m) r %= m;` | 235.44 | **+0.44%** | 159.66 | **+4.98%** |
| `d_sub-gcc` — `while (r >= m) r -= m;` | 236.79 | +1.02% | 160.58 | +5.59% |
| `c-clang` (R1, **the bug**) | 219.74 | — | 143.96 | — |
| **`c-clang-h` — SHIPPED** | **242.40** | **+10.31%** | **160.66** | **+11.60%** |
| `d_cmp-clang` | 221.08 | +0.61% | 134.09 | **−6.86%** |
| `d_sub-clang` | 217.25 | **−1.13%** | 136.83 | **−4.95%** |

Three things, and the third is p06's strongest single sentence about cost:

1. **Within gcc, the factor between the shipped hardening and the cheapest found
   is 42.8× on `small` and 11.6× on `large`** (18.83 → 0.44; 57.87 → 4.98).
   Within clang there is no factor to quote, because the cheapest is *negative*
   on both inputs; the pair is (+10.31%, −1.13%) on `small` and (+11.60%,
   −6.86%) on `large`. The 16× quoted in 3c is the gcc statement measured with
   the five-identical-copy protocol rather than the population; both are
   reported, and neither is a universal —
   on an input where `r >= m` is common the guarded form pays the branch *and*
   the divide.
2. `.memory/02-bench-rules.md` forbids re-shipping a rung because a cheaper
   in-contract spelling was found, so **the textbook line ships and both numbers
   are published, labelled, with the input named.**
3. ⚠ **On `large` under clang the cheapest in-contract hardening is 6.9% FASTER
   than the unhardened bug, and on `small` `d_sub-clang` is 1.1% faster.** That
   is not noise and it is not a layout artefact: the worst layout pair —
   `d_cmp-clang`'s slowest layout (139.51) against `c-clang`'s fastest (143.04)
   — is **still 2.5% faster than the bug**. The mechanism is §0b's, arriving in
   the clock: reducing `r` proves `r < m ≤ 64`, which lets LLVM fold the
   four-byte header decode into one `mov`, and on `large` (12 records per call of
   1…8 bytes each) the decode is most of the work. **The safety line does not
   merely cost nothing here; it pays.**

Two more things to read off 3c, and the second is the sharper:

1. **The cheapest in-contract hardening costs +1.20% (gcc) / +0.64% (clang) on
   `small`, against the textbook spelling's +19.30% / +10.04%** — a factor of 16
   under the five-copy protocol, 42.8× under the population. Both numbers are
   published, labelled, **with the input named**.
2. ⚠ **`d_cmp-clang` and `c-clang-h` execute exactly the same number of
   instructions — `2646.9640` both on `small` and `1802.0000` both on `large`,
   to four decimals — and differ by 20.94 ns (−8.5%) on `small` and by
   **26.57 ns (−16.5%)** on `large`.** They are genuinely two different programs,
   not one binary measured twice: `n_fn_nopad` 167 vs 164, `md5_fn c0965f763fee`
   vs `5844f1e091cf`, and distinct `md5_fn_norel` over the whole layout
   population. One `Ir` figure, a 16.5% time difference, same compiler, same
   input. That is the tightest statement of *"instruction counts are not a cost
   model"* this project has produced, because there is no count difference left
   to explain it with — the 3-instruction static difference is a branch that is
   never taken, and what moves is which of them contains a `div` on the executed
   path. **The `large` half is TASK_048's addition and it doubles the effect.**

### 3d. The `identity` pin's price on this pattern

R5's bulk load sits in a free function, so R4 must call the same
`#[inline(always)] fn scr_load` to stay byte-identical. Written **inline** in
`kernel` instead (`c_r4inline`), R4 is **179 instructions
(`md5_fn f7b24db6bfd9`)**; through the helper it is **208 (`897c52ff4005`)** —
LLVM clones the record loop for `nelem >= SCR` and inlines the 64-byte copy as
four `movups`. The *static* delta is +29 instructions; the **executed** delta is
`c_r4inline − R4ship` = **−4.00 Ir/call on `small` and −8.00 on `large`, flat in
`nrec`** (band N: `0.0000/record, −4.0000 flat`). ⚠ **The reason recorded here
until TASK_048 was that R5's load "has to sit inside a
`#[verifier::external_body]` item"; it does not — `scr_load` is verified now
(§6a) — and the helper is still needed, because it is the CALL BOUNDARY and not
the trust that changes LLVM's inlining order. The number is unaffected.**

**And the `identity` pin has a SECOND measured price on p06, of a different
kind.** §6a: because `RangeTo<usize>` has no `SliceIndexSpecImpl` at the pinned
vstd, R5 cannot spell the load `dst[..n].copy_from_slice(...)` at all, and the
pin drags R4 to `split_at_mut` with it. At `-O3` that costs **nothing** in either
rung — the bytes are identical to the pre-TASK_048 ones — and at `-O0` it costs
R4 **+3 static instructions** (416/416 → 419/419) and is what keeps `identity`
at `norel` there. The first price is about *inlining*; this one is about *which
spellings exist*, and it is finding 14 ("the R4 side is chained to the prover")
arriving as an expressiveness constraint rather than a performance one.

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

### 4a. The SHIPPED R3 is `O(n)`. **R3 is not.** — corrected at TASK_048

Until TASK_048 this section read *"**R3, by contrast, IS `O(n)`.** `R3 − R4 =
2.00000 Ir per byte` … the project's second R3 > R2 inversion after p09's"*, and
that published **one spelling's cost as the class's cost** — the exact failure
`.memory/01-ladder.md` finding 3 exists to prevent, and p06 is the **fourth**
pattern to hit it after p02, p16 and p05. Finding 3 needs no correction; p06 did
not follow it. Its rule is *"write at least two independent in-contract R3
spellings and **quote the cheaper**"*, and p06 wrote them (§8) and then quoted
the shipped one in its law table, its prose and its README.

Measured on band M, whole-program marginal, `nrec = 8`, `sum_m` 64 → 384 (a 6×
range), `.temp/p48/r3span_m.json`:

| difference | at `sum_m = 64` | at `sum_m = 384` | **Ir per byte** |
|---|---:|---:|---|
| `safe_naive − unsafe` (R2) | 269.00 | 269.00 | **0.00000** |
| `safe_tuned − unsafe` (**R3 shipped**) | 281.00 | 921.00 | **2.00000** |
| **`c_idx − unsafe`** (in contract, zero `unsafe`) | **105.00** | **105.00** | **0.00000** |
| `c_oneshot − unsafe` | 282.00 | 922.00 | 2.00000 |
| `c_swap − unsafe` | 401.00 | 1361.00 | 3.00000 |

**`c_idx` is in contract** — `spec.md` says in terms that *"the SPELLING OF THE
SWAP is deliberately NOT pinned"* — contains **no `unsafe`**, and agrees with
`model.py` on `small`, `large`, `degenerate` and `adversarial-inarray`. It is
R3's two-step reslice and iterator fold with R2's indexed swap.

So the two numbers, labelled, with the input named (`.memory/02-bench-rules.md`):

> **Fixed-R4 bound (shipped R3):** `+334.00` on `small`, `+172.00` on `large`,
> and `2.00000 Ir` per rotated byte.
> **Cheapest-found in-contract R3 on `small` (`c_idx`):** `+80.00`, and
> **`0.00000 Ir` per rotated byte** — 13…17 `Ir` per *record* and nothing per
> byte, less than half R2's 33.6 per record.
> ⚠ **The cheapest found differs by blob**: on `large` the shipped R3 (`+172`)
> is cheaper than `c_idx` (`+187`). §8 already says so and is right.

**And the `2.00 Ir/byte` contains ZERO bounds checks.** Per-instruction
callgrind on `sweep-m48n08` (384 swap iterations/call, `.temp/p48/cg/*.m48.out`),
the whole of `R3ship − R4` is the `zip`/`Rev` adaptor's **two exhaustion tests
per item**:

```
cmpq +425.00   je +416.00   jne +360.00   jb −391.00   leaq +64.00
movq −60.00    jae +56.00   addq +33.00   movl +32.00        total +921.00
```

≈ +2 instructions per swap against the two-cursor indexed loop's 8. Decoding the
surviving panic pads with p12's `controls/pads.py` `core::panic::Location`
decoder gives `safe_tuned`, `c_idx` and `c_foldidx` the **identical 11 pads at
identical `line:col`** — `66:34` (the `scr_load` reslice), `76:24`/`76:40` (the
two-step window reslice) and the eight header indexes — and **zero pads at any
swap or fold site in any rung**. So p06's per-byte "safety" term contains no
safety.

**The R3 > R2 inversion is `small`-only and spelling-specific.** On `small` the
shipped R3 is dearer than R2 outright (2958 vs 2797 kernel-exclusive); on `large`
it is cheaper (1897 vs 2120); and `c_idx` is cheaper than R2 on both. So p06 is
**not** "the project's second R3 > R2 inversion after p09's" — that sentence is
withdrawn. What p06 has is one *spelling* that inverts on one *input*.

⚠ **Scope, stated so it is not over-claimed. This is an `Ir` result and the wall
clock cannot resolve it.** Re-measured with §3b's protocol (5 identical copies,
alternating, 9 reps, `small`): `safe_naive` 250.86 / `c_foldidx` 251.54 /
`safe_tuned` 249.17 / `c_idx` 247.60 / `verus` 241.96 / `unsafe` 235.52 ns. The
whole R3 spread is **1.6%**, against a `verus − unsafe` null of **+2.73%** on
byte-identical kernels. A 254-instruction `Ir` gap between `R3ship` and `c_idx`
on this input is invisible in time; §11 says which p06 figures clear the floor
and these do not.

## 5. The proof

`./verus_run.py patterns/p06-rotate/verus.rs` → **`18 verified, 0 errors`**;
`--cfg slb_twin` → **`23 verified, 0 errors`**. Both pinned in `spec.md` and
re-derived per item with `--verify-function <name> --verify-root`:

```
SCR 1 + fold_scr 1 + walk 1 + lemma_rev_noop 1 + lemma_rev_step 1
      + lemma_three_reverses 1 + scr_load 1 + kernel 6 + main 5   = 18
twin: 18 + 1 + 1 + 1 + 2 (slb_twin_scr_load has a LOOP)  = 23
```

(It was `17` / `22` until TASK_048. `scr_load`'s `1` is the item that stopped
being `external_body` — §6a.)

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

**Five `external_body` items, 10 body lines**, recounted against the gate's own
`tcb_items` record (`results/gate/p06-rotate.json`), which lists exactly these
five with body-line counts 1, 1, 3, 4, 1:

| item | body lines | `requires` | `unsafe` in the body? | twin? |
|---|---|---|---|---|
| `buf_get_unchecked` | 1 | `i < v@.len()` | **yes** | yes |
| `scr_get_unchecked` | 1 | `i < v@.len()` | **yes** | yes |
| `scr_set_unchecked` | 3 | `i < old(v)@.len()` | **yes** | yes |
| `load_input` | 4 | *(none — it states no `ensures` either)* | no | n/a |
| `emit` | 1 | *(none)* | no | n/a |

### 6a. It was SIX until TASK_048, and the recorded reason for the sixth was FALSE

Until TASK_048 `scr_load` was a sixth `external_body` item, and `verus.rs`, this
file and `TASK_047_REPORT.md` all said that `<[T]>::split_at_mut` *"is the route
that would delete this item; taking it changes the exec text of four rungs"*.
**At `-O3` it changes the exec text of nothing** — and at `-O0` it costs three
instructions, which is the half neither the report nor the review measured, see
below. Measured (TASK_047_REVIEW B1, re-measured at TASK_048):

```
./verus_run.py patterns/p06-rotate/verus.rs                  18 verified, 0 errors   (was 17)
./verus_run.py patterns/p06-rotate/verus.rs --cfg slb_twin   23 verified, 0 errors   (was 22)
```

| `-O3 isolated` binary | `n_fn` / nopad | `md5_raw` | `md5_fn` |
|---|---|---|---|
| `unsafe` (R4) **before and after** | 216 / 208 | `6608a63b5c52` | `897c52ff4005` |
| `verus` (R5) **before** | 216 / 208 | `6608a63b5c52` | `897c52ff4005` |
| **`verus` (R5) after, `scr_load` VERIFIED** | **216 / 208** | **`6608a63b5c52`** | **`897c52ff4005`** |

Checksums identical on `small`, `large`, `degenerate` and `adversarial-inarray`
in all four Rust rungs, and the `identity: unsafe == verus, O3 exact` pin holds
unchanged.

⚠ **It is NOT free at `-O0`, and neither TASK_047_REVIEW's B1 nor TASK_048 said
so, because both compiled only at `-O3`.** The gate found it:

```
FAIL [identity] unsafe vs verus at O0: identity dropped to 'differ', spec.md pins 'norel'
  md5_fn 31bbc50177e9 vs 1a078f179e8f, counts [416, 416, 2445] vs [419, 419, 2471]
```

At `-O0` nothing is inlined, so `split_at_mut` is a real call with a different
argument setup and R5's O0 kernel gains 3 instructions that R4's does not have.
**The repair is not to weaken the O0 pin; it is to give R4 the same three exec
lines**, which is what `verus.rs`'s own opening sentence — *"R4's exec code
verbatim, plus the specs and proofs"* — requires anyway. With that:

| `-O0 isolated` | `n_fn` / nopad | `md5_fn` | `md5_fn_norel` |
|---|---|---|---|
| `unsafe` (R4) **before** | 416 / 416 | `31bbc50177e9` | — |
| **`unsafe` (R4) after** | **419 / 419** | `912ca69aea47` | **`b70799689ce6`** |
| **`verus` (R5) after** | **419 / 419** | `1a078f179e8f` | **`b70799689ce6`** |

`identity` is back at **`norel` at `-O0`** (equal modulo pc-relative
displacements — the crate names differ in length, which is link layout) and
**`exact` at `-O3`**. **So the price of removing the axiom, stated in full: zero
at `-O3` in every rung, and `+3` static instructions in R4's `-O0` kernel.** No
performance claim rests on an O0 row (`.memory/02-bench-rules.md`), and none of
p06's does.

**What that does to the gate's idiom audit, stated because a diff will show it.**
`required_absent` moves **2 → 6** and `required_pins_nothing` stays **0**. The
two pre-existing absences are the bug's own two lines (`r %= m;` and
`if (m != 0)`, both absent from `c/kernel.c` and present in
`c/kernel_hardened.c`); the four new ones are exactly the 2-and-2 receiver
scoping — `dst[..n]` absent from `unsafe.rs` and `verus.rs`, `s.split_at_mut(n)`
absent from `safe_naive.rs` and `safe_tuned.rs` — and the entry's English names
that scope, which is what the `absent` bucket is for. `forbidden_hits` stays 0.
The bulk call itself, `.copy_from_slice(&src[from..from + n]);`, is pinned
**unscoped** and matches all four rungs.

⚠ **Why R2 and R3 do NOT follow, and it is a finding rather than laziness.**
`.memory/01-ladder.md`'s finding 14 is *"the R4 side is chained to the prover"*,
and this is that mechanism in a form the project has not recorded: what
propagates into R4's **source** is not a performance constraint but the
**verifier's expressiveness limit** — `RangeTo<usize>` has no
`SliceIndexSpecImpl`, so the spelling every ordinary Rust programmer writes
cannot appear in R5, and the `identity` pin drags R4 with it. It stops at R4,
because nothing chains R2 and R3 to the prover, and re-spelling them would be a
re-ship of two rungs for no reason the rule allows
(`.memory/02-bench-rules.md`). **This is the second measured price the `identity`
pin has extracted from p06** — the first was 179 → 208 instructions from the
helper boundary (§3d), which is about inlining; this one is about which
spellings exist at all.

**This is NOT a re-ship under `.memory/02-bench-rules.md`, and the rule's text is
about spellings so a reader will reach for it.** That rule forbids moving a
shipped rung *because a cheaper in-contract spelling was found*. Here **no rung's
`-O3` machine code changes and no published `Ir` or `ns` figure moves** — the two
spellings compile to the same bytes. Nothing was selected on cost: the old
spelling is not *dearer*, it is **unverifiable**, which is one of the three
reasons that rule does allow (*"the shipped spelling turns out to be … not the
idiom it claims to be"* — it claims to be the load R5 performs, and it was not).
What moved is an obligation, from *assumed* to *proved*, plus 3 instructions in
R4's `-O0` kernel.

⚠ **The direction test, answered in writing, because a smaller trusted base is
the direction that flatters this project's thesis.** `.memory/01-ladder.md`'s
repaired test: *an edit to a **declaration** is self-certification if it moves the
pattern's own published figure in the direction that flatters the author's
thesis.*

**TASK_048's own reading — "this is a measurement, not a declaration edit" — is
incomplete, and the measurement that shows it is this**: the old body was
`dst[..n].copy_from_slice(&src[from..from + n]);`, which `spec.md`'s
`idiom.required[5]` pins **by name**, and it **cannot be verified at all**.
`..n` is a `RangeTo<usize>`, and at the pinned vstd `RangeTo` has **no**
`SliceIndexSpecImpl` — only `usize` and `Range<usize>` do
(`vstd/std_specs/slice.rs:14,30`) — so the line reports `precondition not
satisfied` at `vstd/std_specs/core.rs:69`. Respelling it `dst[0..n]` on the
reborrowed slice discharges the preconditions and then fails the *post*condition,
because `<[T] as IndexMut<I>>::index_mut`'s `ensures` is a `call_ensures(...)`
Z3 does not instantiate (probes: `.temp/p48/vstd/keepspell.rs`, `keepspell2.rs`).
`split_at_mut` is the only route that closes both ends — **so landing B1 forced
an edit to the idiom block, which is a declaration edit and the test does apply.**

It passes, for three reasons, and the third is the one that generalises:

1. **The edit is forced, not chosen.** An entry naming a spelling the rung it
   scopes to is *unable* to write is a bug in the ruler, not a thumb on the
   scale — p13's middle case ("the exclusion is one layer down"), inverted.
2. **The scoping is priced and the price is zero.** The receiver differs in one
   rung (`verus.rs`) out of four, and the two receivers compile to
   byte-identical machine code. p13's rule is *price every scoped entry and
   dispose of it on what the price says*; this one measures `0.00 Ir` and
   `0` bytes.
3. **The obligation count went UP, 17 → 18 and 22 → 23.** That is the tell. An
   item moving from *assumed* to *proved* adds a query and subtracts an axiom, so
   the against-interest number and the flattering number move together and in
   opposite directions. A TCB reduction with no obligation increase would be the
   suspicious shape; this is not it.

### 6b. The axiom RELOCATES into vstd — and what that does to the TCB column

**`scr_load`'s postcondition is not discharged out of nothing.** Three vstd items
take it over, and naming them is the point:

| vstd item | what it supplies | its own status inside vstd |
|---|---|---|
| `vstd::array::ref_mut_array_unsizing_coercion` (`vstd/array.rs:175`) | the `&mut [u8; 64] → &mut [u8]` reborrow write-back: `out.view() == old(r).view()` **and** `final(out).view() == final(r).view()`. Verus inserts it for the *implicit* coercion, so no hidden API is named | `#[verifier::external_body]` |
| `<[T]>::split_at_mut` (`vstd/std_specs/slice.rs:185`) | the halves' write-back, `final(slice)@ == final(ret.0)@ + final(ret.1)@` | `assume_specification` |
| `<[T]>::copy_from_slice` (`vstd/std_specs/slice.rs:205`) | `final(dst)@ == src@` | `assume_specification` |

**So the trust did not vanish; it moved out of a wrapper this pattern's author
wrote and into specifications vstd ships.** Trusted-base size is one of the five
axes this project compares, so *"can a pattern shrink its published TCB by
choosing a spelling whose axioms live in vstd?"* is a question about the metric
rather than about p06. TASK_048 proposed reporting **two numbers** —
author-written trusted items, and vstd assumed specifications relied upon.

**The second number is not the right one, and here is the measurement.**

*(i) It is not computable per pattern.* The pinned vstd
(`0.2026.08.09.92f466f`) ships **402 `assume_specification` sites, 272
`external_body` items and 545 broadcast axiom lemmas across 44 files**. "Relied
upon" is not decidable from the text: the coercion above is inserted **by Verus**
and never appears in the source, and `broadcast use` pulls in whole families
(`group_slice_axioms`, `group_array_axioms`) at once. A number nobody can recount
is precisely what `.memory/04-verus.md` warns about — it is how the pilot's
"TCB: one 3-line wrapper" hid two more items.

*(ii) It would not distinguish the patterns.* Every rung on this project already
depends on the same vstd core — slice `View`/`len`/index, the integer axioms,
`Vec` in `main`. p06's marginal change is **3 items out of 674**. A column that
is nearly identical for every row is not a comparison axis.

*(iii) It measures the wrong thing.* What makes the two kinds of trust differ is
not *which file the axiom lives in*; it is **who can be wrong and how far the
error travels**. An author-written `ensures` is read by one reviewer and used by
one program: if `scr_load`'s `load_into` had been wrong, p06's proof was wrong
and nothing else was. A vstd `assume_specification` is shared by every Verus
program in existence and is right or wrong independently of this project. That
is a property *of the item*, and it partitions reproducibly.

**So p06 keeps ONE headline number — pattern-local trusted items, exactly what
`harness/check.py`'s `tcb_items` already counts and prints — and classifies it.**
`.temp/p48/tcb_census.py` applies the classification to every pattern's committed
gate record and every pattern's source:

| bucket | test | p06 | project, 14 patterns |
|---|---|---:|---:|
| **U-license** — licenses an operation vstd does not specify | body contains `unsafe` | 3 | **25** |
| **V-gap** — no `unsafe`; trusted only because of a claimed vstd gap | no `unsafe`, non-empty `ensures` | **1 → 0** | **3 → 2** |
| **infra** — `load_input` / `emit`; states no `ensures` at all | no `unsafe`, no `ensures` | 2 | 30 |
| **total** | the gate's own `tcb_items` | **6 → 5** | **58 → 57** items / **119 → 118** body lines |

**And the gameability question is answered by the U-license row, measured.** For
a `U-license` item to relocate into vstd, vstd would have to specify the
operation. For 23 of the 25 it is a `get_unchecked` / `get_unchecked_mut`
wrapper, and this is a probe rather than a memory: `<[T]>::get_unchecked`,
`<[T]>::get_unchecked_mut` and `u64::count_ones` are all **`is not supported`**
at the pinned vstd (`.temp/p48/vstd/{gu,gum,popcnt}.rs`), as are
`core::ptr::copy_nonoverlapping`, `<[T]>::as_ptr`, `<[T]>::as_mut_ptr` and
`<*const T>::add` (`cno.rs`). The other two U-license items are the bulk-copy
wrappers p02's `copy_bytes` and p08's `move_right`, and p02's is the one this
project has now *measured*: its contract discharges from vstd, and taking that
route costs `+9` instructions, `+5.00 Ir`/call and the `identity` pin (p02
`NOTES.md` 5b). So:

> **The exposure was 2 items in 58 — 3.4% — and is now 1 in 57.** Exactly two of
> this project's trusted items were removable by relocating an axiom into vstd:
> p06's `scr_load`, removed here, and p08's `copy_in`. p09's `popcount64` is a
> **real** vstd gap (`count_ones` is unsupported). The remaining 55 cannot move:
> 25 license operations vstd does not specify, and 30 are infrastructure that
> states no `ensures` and therefore cannot axiomatise anything.

What that does to every other pattern's published TCB, computed and **not
applied** (no other pattern's code was edited): **p08 would go 4 → 3 items if its
`copy_in` is respelled the same way and its codegen holds; every other pattern's
number is unchanged.** ⚠ And p02 is the measured counterexample that keeps this honest:
its `copy_bytes` contract *also* discharges (`10 verified, 0 errors`, twin
`13/0`), and the respelling still must not be landed, because p02's R4 body is
`copy_nonoverlapping` and R5 must match it byte for byte — the verified spelling
is 81/79 instructions against R4's 72/70, `+5.00` executed `Ir` per call, one
extra panic pad, and it **breaks `identity: exact`**. p02's `NOTES.md` 5b carries
the measurement. **The discriminator between p06 and p02 is what R4's body is**,
and that is the sentence `.memory/04-verus.md:133` and `:813` should carry
instead of *"there is no vstd spec for `copy_from_slice`"*, which is false in
both halves.

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

⚠ **R3's `+51.00/rec` is the SHIPPED spelling's, and a different in-contract R3
buys the same fact for `13…17`.** `c_idx` (§8) answers the disjointness question
R2's way — momentary indexed accesses — while keeping R3's reslice and fold, and
costs `α′(m mod 4) = 13, 15, 16, 17` `Ir`/record with **no per-byte term** (§4a).
So the honest reading of the R3 row is *"`std`'s `unsafe` is the most expensive
of the four **as p06 spells R3**"*, and the class contains a cheaper member that
answers the question with rustc's bounds check instead. The trusted-base column
does not move with the spelling; the cost column does.

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
**`18 verified, 0 errors`** while `--cfg slb_twin` reports
**`22 verified, 1 errors — precondition not met: index in bounds for this
access`**. So on p06 the twin is the sole **Verus-level** catcher — ⚠ **not the
sole catcher**: `spec.md`'s contract pin fails it too, with two clause diffs, and
§10b measures that and audits the same sentence on p12 and p02. **This is the item p06 exists for** — it is the write
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

### `scr_load` — the item that used to be here, and where its axiom went

Until TASK_048 this was a fourth `SLB-TRUSTED` + `-ARGUMENT` block, because
`scr_load` was `external_body`. It is not any more (6a), so the gate no longer
requires an argument for it and one would be misleading. What is worth keeping is
the part that is still true and the part that was not:

**(a) The checked stand-in.** `slb_twin_scr_load` is kept even though 5c-twin no
longer requires it: it derives `load_into` from an **element-wise indexed loop**
(`dst[j] = src[from + j]`), independently of the three vstd bulk specifications
the shipped body now uses. Two routes to one postcondition, both checked. It
still carries `2 verified` under `--cfg slb_twin` (the loop body is its own
query), which is the `+2` in the 23.

**(b) What the `ensures` says, and it is now PROVED rather than assumed.**
`load_into` is a whole-array equality: slots `[0, n)` become `src[from + i]` and
**every slot from `n` up is the byte that was already there**. The second half is
load-bearing on p06 in a way it is not on p02 — the scratch is *not* re-zeroed
between records, so `scr[m .. SCR)` carries the previous record's bytes and
regime 1 reads exactly those. Verus now checks it.

**(c) What is still trusted, said out loud.** The `&[u8]` / `&mut [u8; 64]`
disjointness `copy_from_slice` needs is discharged by **Rust's own reference
rules**, not by this contract and not by vstd — the two references cannot name
the same allocation in safe Rust. And the three vstd items in 6b are trusted
*inside vstd*. The reduction 6 → 5 is a reduction in **author-written** trusted
items, which is the number `tcb_items` counts, and 6b says exactly what it is
and is not.

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
| `adversarial-past48` | 112 | 48 | **134** canary, ⚠ **stdout not reproducible** | 0, `497` | **101 panic** | **101 panic** | 0, `14544551909971626112` |
| `adversarial-pastfar` | 100000 | 99936 | **139** | **139** | **101 panic** | **101 panic** | **139** |

The safe-Rust panics are `safe_naive.rs:102:25` (`let u: u8 = scr[b - 1];`) and
`safe_tuned.rs:105:40` (`&mut scr[a..b]`) — the index and the *range*
respectively, which is why R3's `if a < b` guard is in the shipped spelling: it
keeps the second reverse's empty range from panicking on the range rather than on
the index and hiding which regime the control is in.

⚠ **`adversarial-past48.bin` / `c-gcc` is the one row in this pattern whose
recorded stdout does not reproduce, and the mechanism is p06's own algebra.**
**every observation so far has been a different answer, and the committed value
will not match your run either.** Five so far: `5645006182206458263` (the record
before TASK_048), `1380113329433944552` (TASK_047_REVIEW),
`8830450532111958723` and `425172236597815642` (two consecutive TASK_048
`check.py` runs), and **no stdout at all** on twelve direct runs
(`rc = -6`, `*** stack smashing detected ***`, with `stdbuf -o0` as well as
without). So **both the value and its presence vary**, and the *exit code and the
stderr are the stable part of that row*. A diff of this field between two
`check.py` runs is expected and means nothing.

Why, from the contract rather than from "uninitialised memory": at `r = 112 > m`
the second reverse is empty, so the triple is `rev(scr, 0, 112)` then
`rev(scr, 0, m)`, and composing them leaves `scr[0 .. 64)` holding the ORIGINAL
bytes `[48 .. 112)` — i.e. **the 48 bytes past `scr`, which include the
stack-protector canary the kernel randomises per `execve` via `AT_RANDOM`**. The
order-sensitive fold then reads exactly those. The canary *slot* meanwhile
receives the original `scr[0 .. 48)` (record data and zeros), which is fixed —
which is why the abort is deterministic while the checksum is not. **Read this
row as "exit 134, canary tripped"; do not diff its stdout.**

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
| `c_foldidx` | R3ship with the fold respelled as R2's indexed loop | +320.00 | +142.00 | yes |
| `c_swap` | `<[T]>::swap(j, n-1-j)` | +490.00 | +286.00 | yes |
| `c_reverse` | `scr[a..b].reverse()` | −358.00 | +320.00 | **FORBIDDEN** |
| `c_copywithin` | `scr.copy_within(r..m, 0)` + a temporary | **−856.00** | **+497.00** | **FORBIDDEN** |
| `c_rotate` | `scr[..m].rotate_left(r)` | −951.00 | +314.00 | **FORBIDDEN** |

- **In-contract R3-side span: `+80.00 … +490.00` on `small`, `+142.00 … +286.00`
  on `large`.** ⚠ **The cheapest found differs between the two blobs** — `c_idx`
  on `small`, `c_foldidx` on `large` (and the *shipped* R3 is `+172.00` there) —
  which is the fifth pattern to reproduce *"a cheapest-found figure must name its
  INPUT as well as its spelling"*. Write "cheapest found", never "minimum".
- ⚠ **The span is a span in the ASYMPTOTIC SHAPE, not only in the constant**, and
  that is §4a: `c_idx` has **no per-byte term at all** while the shipped R3 and
  `c_oneshot` have `2.00000` and `c_swap` has `3.00000`. Quoting the shipped
  spelling's `2.00 Ir/byte` as *R3's* is the mistake TASK_048 corrected.
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
| **`<[T]>::copy_within()`** | ⚠ **SUPPORTED** (`vstd/std_specs/slice.rs:235`; the probe returns `precondition not satisfied`) | **−856 / +497** | **KEEP BY FIAT, AND THIS IS THE PRICE** — p13's *third* bucket. Nothing but this declaration excludes it, so §8's claim that every fiat's price is published is only true with this row in it (TASK_048). |
| `<[T]>::swap()` | **`is not supported`** | +490 / +286 | not forbidden; R3 may use it, and it is the *dearest* in-contract spelling, so nothing turns on it |
| `split_at_mut` | **supported** (`precondition not satisfied` only) | R3's shipped spelling, and R5's `scr_load` since TASK_048 (§6a) | — |
| `core::mem::swap` | **`2 verified, 0 errors`** | R3's shipped spelling | — |

⚠ **`copy_within` is p06's one FIAT exclusion and it was unpriced until
TASK_048.** Two things had to be corrected. First, the stated *reason* was
inaccurate: `spec.md` said `copy_within` *"is the OUT-OF-PLACE rotate (rotate
through a temporary)"*, and it is not — `<[T]>::copy_within` is `ptr::copy`
**within one slice**, a `memmove`, and it cannot rotate on its own at all. What
makes it out of contract is that a rotate *built on* it needs a temporary for the
displaced prefix, so the rung stops being the in-place three-reverse algorithm
p06 measures: `controls/gen_controls.py`'s `c_copywithin` writes
`tmp[..r].copy_from_slice(&scr[..r]); scr.copy_within(r..m, 0);
scr[m - r..m].copy_from_slice(&tmp[..r]);`, which visits every byte twice through
`memmove` instead of `2m` scalar swaps and has **no in-place aliasing question at
all** — and the aliasing question is p06's TCB result. Second, the price: it is
**−856.00 on `small` and +497.00 on `large`**, and on band M its slope is
**−8.075 `Ir` per byte** (it is a `memmove`; it gets *cheaper* per byte as `m`
grows, which no in-contract spelling does). It agrees with `model.py` on `small`,
`large`, `degenerate` and `adversarial-inarray`.

**The direction test on that exclusion passes**, the same way `.reverse()`'s and
`.rotate_left()`'s do: excluding `copy_within` makes p06's published safe-side
figure **larger** on `small` — 936 `Ir`/call larger, cheapest in-contract `+80`
against `−856` — and costs nothing on `large`, where it is the dearest spelling
measured. The exclusion moves the number *against* the author's thesis.

(`.temp/p06/vstdprobe/*.rs`, one spelling per file — a shared probe reports every
spelling's error on every run, because `--verify-function` still type-checks the
whole file. Measured after making exactly that mistake.)

**So p06's forbidden entries fall into TWO of p13's three buckets, not one.**
`.reverse()` and `.rotate_left()` are the middle case — *"keep, the exclusion is
one layer down"*: an R4 could not spell them at the pinned vstd, so forbidding
them on the *safe* side is what keeps the comparison symmetric rather than a
thumb. **`copy_within` is the third case** — *fiat*, because the prover does not
exclude it — and its price is published above. (`from_le_bytes` and
`chunks_exact` are also correctly disposed of one layer down; both re-measured
`is not supported`.)

The price is published for all three, because the numbers are large and
blob-dependent: excluding them costs the safe side **1031 Ir/call on `small`**
(cheapest forbidden `−951` against cheapest in-contract `+80`) and **nothing on
`large`**, where every library form is dearer than every in-contract spelling.
The direction test: each exclusion makes p06's published safety figure
**larger**, i.e. moves it *against* the author's thesis, so none of them is
self-certification under either reading of the test.

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

### 9a. The residue term SOLVED — the period is 4, not 8, and the mechanism is on the listing

Until TASK_048 the `R3ship − R4` law carried `α(m mod 8)` with
`α ∈ {3, 5, 19, 22}` and **no mechanism**; TASK_047_REVIEW recorded it as still
unexplained. It is now decomposed, with zero fitted parameters and **45/45 exact
over the whole of band M, `m` = 4…48** (`.temp/p48/bandm_full.json`,
`controls/sweep_ir.py`):

```
R3ship    − R4  =  2*sum_m + nrec * [ swap(m mod 2) + fold(m mod 4) ] + 1
c_idx     − R4  =            nrec * [      13       + fold(m mod 4) ] + 1
c_foldidx − R4  =  2*sum_m + nrec * [ swap(m mod 2)                 ] + 1

     swap(even) = 19      swap(odd) = 1      fold(k) = k + [k > 0],  k = m mod 4
```

so `α(m mod 4) = {0: 19, 1: 3, 2: 22, 3: 5}` and
`α′(m mod 4) = {0: 13, 1: 15, 2: 16, 3: 17}`. **The eight residue classes were
four, repeated twice**; the period-8 statement was true but over-parameterised,
and the period-4 one points straight at the mechanism.

**What separates the two terms is a control, not an argument.** `c_foldidx`
(family C8, added at TASK_048) is the shipped R3 with **only the fold** respelled
as R2's indexed `while` loop — the two-step reslice and the `zip`/`Rev` swap
untouched. It carries `swap(m mod 2)` and **no `m mod 4` part at all**; `c_idx`
carries `fold(m mod 4)` and no per-byte term; `safe_naive` carries neither
(`269.00` flat). The reslice happens once per *call* and so cannot produce a
per-*record* term in `m`, which leaves the fold — and `c_foldidx` decides it by
measurement rather than by elimination.

**The mechanism for `fold(k) = k + [k > 0]`, read off the disassembly**
(`harness/asm.py`, `-O3 isolated`):

- **Every rung's fold is 4× unrolled.** `c_idx`, `safe_naive` and `unsafe` all
  emit `mov %r13d,%edx ; and $0x7c,%edx`, four Horner steps
  (`movzbl ; shl $0x5 ; sub ; add`), `add $0x4,%rcx ; cmp ; jne`, then
  `test %rax,%rax ; je` into a **scalar epilogue of exactly `k = m mod 4`
  iterations**. *That* is why the period is 4.
- **The `k` term is one instruction per epilogue element.** `c_idx`'s epilogue
  body is **9** instructions — `movzbl, mov, shl, sub, mov, add, inc, cmp, jne` —
  against R4's **8** — `mov, shl, sub, movzbl, add, inc, cmp, jne`. The iterator
  closure needs one extra register copy. `+1 Ir` per epilogue element.
- **The `[k > 0]` term is a single EXECUTED alignment `nop`.** `c_idx` has
  `nop` at `0x15a4f`, immediately before `0x15a50` — which is the epilogue
  loop's own back-edge target (`jne 15a50`). So it is *outside* the loop and runs
  **once**, and only when the epilogue is entered at all. R4 has no pad there.

```
c_idx    0x15a41 test %rax,%rax        R4      0x…963 test %rax,%rax
         0x15a44 je   15a80                    0x…966 je   15970
         0x15a46 add  %rsp,%rcx                0x…968 add  %rsp,%rcx
         0x15a49 add  $0x10,%rcx               0x…96b add  $0x10,%rcx
         0x15a4d xor  %edx,%edx                0x…96f xor  %edx,%edx
         0x15a4f nop                  <<<      (no pad)
         0x15a50 movzbl (%rcx,%rdx,1),%esi     0x…971 mov  %r15,%rsi
         ... 9 instructions, jne 15a50         ... 8 instructions, jne …
```

> **So a second p06 law, independently of §3a′, has an executed `.p2align` pad
> as one of its terms.** `[k > 0]` is literally one `nop`. Two of the three
> published laws in this file contain executed padding, and neither residual can
> see it, because padding is exactly as reproducible as work.

**And the strongest out-of-sample statement is on a shipped input.** `small.bin`
is **length-heterogeneous** — five records with five *different* `m` (13, 47, 29,
61, 7), none of which any band visits — which is queue item 11's missing band
arriving as a *perf row*. The band-fitted laws predict it with zero free
parameters:

```
                         m = 13, 47, 29, 61, 7   ->   m mod 4 = 1, 3, 1, 1, 3
R2      - R4 :  32*5 + 13                        = 173   measured 173.00
R3ship  - R4 :  2*157 + (3+5+3+3+5)        + 1   = 334   measured 334.00
c_idx   - R4 :          (15+17+15+15+17)   + 1   =  80   measured  80.00
c_foldidx-R4 :  2*157 + (1+1+1+1+1)        + 1   = 320   measured 320.00
R1h - R1 (gcc)   :  8*5 + 1 - 1*0                =  41   measured  41.00
R1h - R1 (clang) : -9*5                          = -45   measured -45.00
```

Six laws, six exact hits, on an input outside every band — and the three R3-side
ones use §9a's `α(m mod 4)` / `α′(m mod 4)` / `swap(m mod 2)` decomposition with
**zero** fitted parameters. The gcc law also hits
`large` exactly (`8*12 + 1 - 1*2 = 95`) and the clang one misses it by 1. ⚠ **`large.bin` is
NOT predicted**: its `m` run 1…8, mostly below band M's clean domain, and
`R3 − R4` misses by 47 there. That is the domain statement doing its job, and it
is why both are reported.

## 10. The proof mutants

`controls/gen_controls.py` family B, `controls/verify_controls.sh`, both
configurations:

**Counts moved +1 / +1 at TASK_048** because `scr_load` stopped being
`external_body` and its body became an obligation in every mutant too (§6a); the
*verdicts* did not move. Two runs of `controls/verify_controls.sh`, identical
both times:

| mutant | what changed | shipped | `--cfg slb_twin` | caught by |
|---|---|---|---|---|
| `b_nored` | the reduction **deleted**, contract untouched | **17 / 1** ⚠ `while loop: Resource limit (rlimit) exceeded` | 22 / 1 `invariant not satisfied before loop` | Verus |
| `b_nored_msonly` | deleted **and** the postcondition weakened to memory-safety-only | **17 / 1** `invariant not satisfied before loop` | 22 / 1, the same error | Verus |
| `b_scrmod` | `r %= SCR` (the **wrong modulus**), contract untouched | **17 / 1** `precondition not satisfied` | 22 / 1, the same error | Verus |
| **`b_scrmod_msonly`** | `r %= SCR` **and** memory-safety-only | **18 / 0** | **23 / 0** | **`spec.md`'s contract pin AND the `identity` pin** — see 10b |
| `b_weakreq` | `i < old(v)@.len()` → `i <= …` in the trusted item *and* the twin | **18 / 0** — undetected by Verus | **22 / 1** `precondition not met: index in bounds` | **the twin — and `spec.md`'s contract pin, 2 diffs** — see 10b |
| `b_tautology` | the kernel `ensures` → `r == r`, nothing else | **17 / 1** `assertion failed` | 22 / 1, the same error | the driver's consuming assert **and the contract pin** |

⚠ **`b_nored`'s shipped-configuration failure is a RESOURCE LIMIT, not an
obligation, and TASK_048 measured what moved it there.** `NOTES.md` used to
record `invariant not satisfied before loop` for `b_nored` and
`precondition not satisfied` for `b_scrmod`; TASK_047_REVIEW measured `b_scrmod`
failing by `Resource limit (rlimit) exceeded` twice in a row. **Both records were
right about their own tree.** Regenerating the mutants from the *pre*-TASK_048
`verus.rs` (`.temp/p48/oldctl/`, `git show HEAD:…/verus.rs`) reproduces the old
pair exactly — `b_nored` → `invariant not satisfied before loop`, `b_scrmod` →
`Resource limit (rlimit) exceeded` — while the current tree gives the mirror
image. **Verifying `scr_load` moved the exhaustion from one mutant to the other.**
`--rlimit 30` and `--rlimit 60` do not convert it into an obligation failure
(still `17 / 1`, still the rlimit), so the query genuinely diverges rather than
running out of a budget that could be raised.

**What that costs the controls, stated rather than swept up.** A mutant that dies
of resource exhaustion is a weaker control than one that fails on an obligation:
it shows Verus did not accept the mutant, not that the specification rejected it.
On p06 **every mutant fails on a real obligation in at least one of the two
configurations**, and `b_nored` fails on the invariant under `--cfg slb_twin`, so
the pair (shipped, twin) is what carries the strength claim — not either
configuration alone. The rlimit is a property of the SMT context, and TASK_048
is the measurement that shows how little it takes to move it.

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
   on exactly regime 1's set. `b_scrmod_msonly` therefore **verifies, 18 / 0 and
   twin 23 / 0**, and the compiled binary is a *verified, `unsafe`-using program
   whose memory-safety obligations all discharge* which nonetheless prints
   `415744194194585216` on `adversarial-inarray.bin` where the model says
   `5453190234444350336` — and agrees with the model on `small`, `large` and
   `degenerate`. **That is the mutant that earns its keep**, and it is the
   complement of p09, where the bug went invisible *even to the spec* once the
   spec moved with it: here the two specs disagree on the same program.
3. **`b_weakreq` is the only mutant Verus alone does not catch**, on a weakening
   applied to the item *and* the twin in one edit — which is what a real
   single-commit weakening looks like. It is the first instance on this project
   of that shape on a **write** accessor called twice per iteration. ⚠ **But
   "the twin is the sole catcher" is FALSE at the gate level and 10b measures
   it.**

### 10b. "The twin is the SOLE catcher" and "caught by nothing but `spec.md`'s pin" are both FALSE

Corrected at TASK_048 on TASK_047_REVIEW's M3. The measured *premises* were
right — the shipped Verus configuration really does report `18 / 0` on
`b_weakreq`, and `b_scrmod_msonly` really does verify in both configurations —
and the conclusions drawn about the **gate** did not follow.

`harness/check.py`'s own comparison (`check.py:2200-2240`, `vparse.by_name` +
`norm_clause`) run against `spec.md`'s pinned `verus.items`
(`.temp/p48/pinsim.py`, which is that code and nothing else):

```
SHIPPED verus.rs   0 diffs
b_weakreq          2 diffs   scr_set_unchecked.requires  ['i <= old(v)@.len()'] != pinned ['i < old(v)@.len()']
                             slb_twin_scr_set_unchecked.requires        same
b_scrmod_msonly    1 diff    kernel.ensures ['r == r'] != pinned ['r == rotate_fold(buf@, off as int, len as int)']
b_tautology        1 diff    (same)
b_nored_msonly     1 diff    (same)
b_nored            0 diffs   b_scrmod   0 diffs
```

So **`b_weakreq` fails the `verus_contract` stage, which runs BEFORE
`trusted_twins`.** And `b_scrmod_msonly` **also breaks the `identity` pin**:
compiled at the gate's own flags it is **174 / 166 instructions,
`md5_raw 3f32e343bfa7`, `md5_fn 779c99de203c`** against R4's **216 / 208,
`6608a63b5c52`, `897c52ff4005`**.

**The correct statements:**

> The twin is the sole **Verus-level** catcher of `b_weakreq`. The contract pin
> catches it too, with two clause diffs, and a clause weakening only reaches the
> twin stage if the `spec.md` pin was edited in the same commit — which is
> exactly what TASK_008_REVIEW's original attack did and is why the twin exists.
>
> `b_scrmod_msonly` is caught by the contract pin **and** by the `identity` pin,
> not by "nothing but `spec.md`'s pin".

**Audited on the two other patterns that could carry the same sentence, and they
split** (TASK_048, report only — neither pattern was edited for this):

| pattern | its version of the claim | measured |
|---|---|---|
| **p12** `NOTES.md:1046-1049` | *"one character, and only the TWIN sees it … the two signatures still match and `spec.md`'s item pin does not move"* | ⚠ **FALSE the same way.** `p2_weak_write_requires` gives **2 diffs** against p12's own pin (`dst_set_unchecked.requires` and its twin's). `p3_slotwise_write_ensures` 1 diff, `p4_taut_kernel_ensures` 1 diff, `p1_no_capacity_check` 0, shipped 0. |
| **p02** `NOTES.md:773` | — | **CLEAN.** p02 makes no sole-catcher claim: its table header says the mutants edit *"verus.rs **and** the spec.md pins, one commit"*, and its last row records the twin-left-alone case as *"caught by the signature comparison instead"*. The shape does not reach it. |
4. **`b_tautology` does not verify**, where p02's M7 did. The driver's consuming
   `assert(r == rotate_fold(...))` still names the real spec, so weakening the
   kernel's postcondition breaks the *call site*. That is the
   `ensures`-is-load-bearing property measured rather than argued
   (`.memory/04-verus.md`).

## 10a. When the declaration was written, stated exactly

`spec.md`'s `idiom.why` says this and it is repeated here because p06 is the
first pattern with a **pre-flight**, and "the declaration was written before any
number existed" would be false:

- The `idiom` block was written **after** the five rungs, the R5 proof (`17/0`
  at the time; `18/0` since TASK_048 verified `scr_load`),
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
- ~~**No layout population.**~~ **CLOSED at TASK_047_REVIEW / TASK_048.** There
  is one now: `controls/clayout.py`, 30 layouts per cell via a pad object, with
  `n_fn` and `md5_fn_norel` single-valued per cell and 30 distinct kernel
  addresses spanning both `addr % 32` residues. §3c′ publishes both inputs from
  it. **p06's headline survives it intact** — gcc `large` `+57.87%`, clang
  `large` `+11.60%`, no sign flip at any layout, and the worst layout pair
  (slowest hardened against fastest buggy) is still `+53.7%` on gcc. The old
  entry's *"that is an argument and not a measurement"* is discharged: it is a
  measurement now and it agrees with the argument.
- ~~**`scr_load` should not need to be trusted.**~~ **CLOSED at TASK_048** — it
  is not trusted any more (§6a), at zero codegen cost, and §6b names the three
  vstd items the axiom relocated into and what that does and does not mean for
  the TCB column.
- **p08's `copy_in` is the same removal, unbuilt.** §6b's census says it is the
  one remaining project-local trusted item whose *only* reason to exist is a vstd
  gap that is not there. Nobody has measured whether p08's codegen holds; p02's
  did not (p02 `NOTES.md` 5b), so the answer is not assumable in either
  direction.
- **`b_nored` fails its shipped configuration by a RESOURCE LIMIT** rather than
  by an obligation, and raising `--rlimit` does not fix it (§10). It fails on the
  invariant under `--cfg slb_twin`, so the mutant is not worthless, but the
  shipped half of that row is weaker than the table's other rows.
- **The `Ir`/`ns` sign disagreement is measured on two compilers and one box.**
  It is a property of *this* `div` on *this* microarchitecture; the `Ir` side is
  simulator-exact and portable, the ns side is not.
