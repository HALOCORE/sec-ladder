# p13 — `strncpy` truncation: what was measured

Numbers here were produced by `harness/check.py p13`, `harness/measure.py p13`
and the scripts under `controls/`. Where a number is not reproducible from the
committed tree, that is a defect; say so.

---

## 0. PHASE 0 — the two things settled BEFORE five rungs were built on them

TASK_043 named two calls it was least sure of and asked for the measurement
first. Both were probed with `.temp/p13/phase0/probe.c` + `run.py`: one
translation unit, two `noinline` kernels differing in exactly the one line, the
window built in-process, `DST_CAP = 32`. `d` is recovered by **inverting the
checksum** (`acc == (d*31 + dst0)*31 + 1` at `nstr == 1`), so the consumer loop
is never instrumented and neither codegen nor frame layout is perturbed.

⚠ **The first run of the probe was wrong and self-caught**: gcc reported
**6.28 Ir/call** for 64 strings. `__attribute__((noinline))` does **not** stop
gcc treating a pure call as loop-invariant and CSE-ing it out of the repetition
loop. Fixed with `__asm__ volatile("" : "+r"(w) :: "memory")` inside the probe's
own loop — identical in both modes, so the delta the probe exists for is
unaffected. The shipped driver defeats the same thing with a real data
dependence (`k` comes from `acc`), which is why `spec.md` says the loop cannot
evaporate. **`noinline` is not a barrier.**

### 0a. Is `dst[DST_CAP - 1] = 0` measurable at all? **Yes. +1 instruction, 1.00 Ir per string.**

Static, `body_len` from objdump:

| build | `kernel_r1` | `kernel_r1h` | `body_len` delta | mnemonic delta |
|---|---:|---:|---:|---|
| gcc -O0 | 161 | 162 | +1 | `movb` +1 |
| gcc -O3 | 180 | 180 | **+0** | `movb` +1, `nop`/`cs` −1, `nopl` +1 |
| clang -O0 | 140 | 141 | +1 | `movb` +1, `data16` −1, `nopl` +1 |
| clang -O3 | 95 | 96 | +1 | `movb` +1, `data16` +1, `xchg` −1 |

gcc -O3's `+0` is **alignment padding rearranged, not the store elided**: the
`movb` is there and a multi-byte `nop` shrank to compensate. Read the histogram,
never `body_len` alone.

Whole-program `Ir` marginal (callgrind, `(Ir@200 − Ir@100)/100`), `nstr = 64`,
`slen = 8` — deliberately the path where **the zero-fill DOES run**, which is
where dead-store elimination into the fill was the risk:

```
gcc   -O3  R1 9793.28  R1h 9857.28  delta +64.00 Ir/call = +1.0000 Ir/string
clang -O3  R1 8934.28  R1h 8998.28  delta +64.00 Ir/call = +1.0000 Ir/string
```

**Exactly 1.00 Ir per string, both compilers**, and it is a matched-spelling
difference of two cells printing the same checksum, so it is exact rather than
fitted (`.memory/01-ladder.md`, TASK_026 §0 item 2). Neither compiler sinks the
store into the zero-fill and neither dead-store-eliminates it.

So the manager's worry does not hold: **p13 does have a safety-tax axis**, and it
is this project's first that is a *store* rather than a compare-and-branch.

### 0b. Does C's runaway consumer leave the frame, and is it stable? **Yes, and stability is PER COMPILER+OPT.**

R1, one string of `slen = 40` (no NUL anywhere in `dst`), 200 runs of each build:

| build | `d` observed | stable? | bytes past `dst[31]` |
|---|---|---|---|
| gcc -O0 | 33 ×200 | **yes** | 2 |
| gcc -O3 | 38 ×186, 34 ×3, 35 ×2, 32 ×9 | **NO** | 1…7 |
| clang -O0 | 32 ×200 | **yes** | 1 |
| clang -O3 | 32 ×200 | **yes** | 1 |
| any R1h | 31 | — | 0 (in bounds) |

⚠ **The task file's either/or is wrong in both directions** — it asked whether
p13's overread is *stably* wrong or *ASLR-derived*, and on the probe it is
**both, depending on the build**.

⚠⚠ **And the probe's pattern does NOT transfer to the shipped cells. Do not
quote the table above as a compiler property.** Re-measured on the shipped
binaries, `adversarial-truncate.bin`, 60 runs of each *single* binary
(§7 is where this belongs, but it belongs here too because it refutes the
paragraph above):

| shipped cell | O0 isolated | O0 whole | O3 isolated | O3 whole |
|---|---|---|---|---|
| `c-gcc` | stable | stable | stable | stable |
| `c-clang` | **2 values** | **2 values** | **2 values** | stable |
| `c-gcc-h`, `c-clang-h` | stable & correct | stable & correct | stable & correct | stable & correct |

The probe found gcc unstable and clang stable; the shipped cells are the exact
reverse. **The honest general statement is therefore neither:**

> Whether R1's wrong answer is reproducible is a property of the individual
> binary's frame layout, not of the compiler, not of the optimisation level and
> not of the pattern. It cannot be predicted — only measured, per cell.

That is a stronger result than either of the manager's two hypotheses, and it is
p03's finding generalised: p03 measured that *its* overread was not reproducible
across runs; p13 measures that reproducibility itself moves with the build.
The values also move **between gate runs** of the same source: `.temp/p13/gate3.log`
records `6532223577066343296` / `9752285780024396160` where
`.temp/p13/gate_final.log` records `10949515590204188416` /
`14169577793162241280` / `4509391184288082688` on the same input. **No specific
wrong answer is quoted anywhere in this file, because none of them is a number.**

The overread never leaves the frame far enough to fault: **1 to 7 bytes**. So
p13 has no analogue of p12's magnitude ladder — there is no canary abort and no
SIGSEGV anywhere in this pattern, and **R1 exits 0 with a wrong answer on every
truncating row under both compilers**.

Detection:

- **ASan fires on both compilers**, by name:
  - gcc -O3: `stack-buffer-overflow READ of size 1 at offset 64 ... [32, 64) 'dst' (line 42) ... in kernel_r1`
  - clang -O3: `stack-buffer-overflow READ of size 33 ...` — clang vectorises the
    scan into a **33-byte load**, so its report is one read of 33 bytes where
    gcc's is one read of 1.
- **valgrind memcheck is BLIND to it.** On a `-static` gcc -O3 build with
  `--track-origins=yes`, the only reports are the documented
  `__libc_setup_tls` static-TLS artefacts; nothing is scoped to `kernel_r1`, and
  the program prints `31745` (→ `d = 33`) and exits 0. Expected, and worth
  writing down: this is an overread of **initialised** stack bytes inside the
  same frame, so V-bit tracking has nothing to flag.
  `.memory/00-environment.md`'s memcheck entry answers *"is anybody reading
  memory nobody wrote?"* and **p13's bug is not that**. ASan's redzones are the
  only oracle here.

---

## 1. TWO CORRECTIONS TO THE TASK FILE, both measured

### 1a. The two harms cannot be separated BY INPUT. They separate by RUNG.

TASK_043's input table asks for `adversarial-truncate` = *"truncation that
changes the answer while every rung stays memory-safe"*. **That input does not
exist**, and one equivalence is why:

```
content is lost  <=>  slen >= DST_CAP  <=>  dst holds no NUL  <=>  R1 reads OOB
```

The source scan stops at the first zero byte, so every one of the
`n = min(slen, DST_CAP)` copied bytes is non-zero; the zero-fill
`for i in n .. DST_CAP` is empty exactly when `slen >= DST_CAP`. Truncation and
the missing terminator are **the same event**.

What p13 ships instead is a **controlled triple** that isolates the memory-safe
harm by holding the checked rungs fixed:

| input | strings | dropped bytes/string | checked-rung checksum | R1 |
|---|---|---:|---|---|
| `adversarial-exact` | 4 × 31 B | 0 | `17389639996120294144` | agrees, ASan clean |
| `adversarial-truncate` | the same 31 B **+ 1** | 1 | `17389639996120294144` | reads OOB |
| `adversarial-truncate-alt` | the same 31 B **+ 9** | 9 | `17389639996120294144` | reads OOB |

Three windows, three different amounts of destroyed data, **one checksum**. That
is the p17-shaped harm on its own: *a correct, proven, memory-safe program
cannot tell them apart.* And `exact` is sanitizer-clean where the other two fire,
so the same triple attributes the second harm to the rung that has it.

The three blobs share **one draw** of the four 31-byte heads, so they differ only
in the tails (p11's TASK_034 lesson).

### 1b. `large` cannot have "a different truncation ratio", and neither can `small`

`check.py:1249-1278` binds **every cell, R1 included**, to `model.py`'s checksum
on every non-`sweep-*` matrix input. By 1a, any truncating string puts R1 out of
agreement — and on some builds out of agreement *with itself between runs*
(§0b, §7: 3 of `c-clang`'s 4 builds). So
`small` and `large` are both **0% truncating**; what differs between them is the
length distribution below `DST_CAP` (mean **7.00** against **22.04**, straddling
16), the string count (13 against 24) and the working set (14.8 KiB against
6.90 MiB). The truncation-ratio axis
lives in `sweep-t*`, and R1 is excluded from it exactly as R1 is excluded from
p12's `sweep-a*`.

This is p12's situation with a different mechanism: p12's obstruction is its
**fold** (`dlen` and `dst[0..dlen]` are both folded), p13's is that the harm is
an out-of-bounds **read of memory outside the program's control**. A fold
redesign cannot rescue p13's the way `controls/gen_controls.py` rescued p12's.

---

## 2. TRUSTED ITEMS — the per-item arguments the gate demands

<a id="tcb"></a>
Five `#[verifier::external_body]` items, which is the whole TCB and the number
`results/gate/p13-strncpy-trunc.json` reports as `tcb_items`. Three of them are
accessors with a `requires` and therefore carry a verified `#[cfg(slb_twin)]`
twin; two (`load_input`, `emit`) have no `ensures` and no `unsafe`, so they are
outside the twin regime but **are still TCB and are counted here**
(`.memory/04-verus.md`: the pilot was published as "one 3-line wrapper" and the
true tally was three).

| # | item | `requires` | `ensures` | twin? |
|---|---|---|---|---|
| 1 | `buf_get_unchecked` | `i < v@.len()` | `r == v@[i as int]` | yes |
| 2 | `dst_get_unchecked` | `i < v@.len()` | `r == v@[i as int]` | yes |
| 3 | `dst_set_unchecked` | `i < old(v)@.len()` | `final(v)@ == old(v)@.update(i as int, x)` | yes |
| 4 | `load_input` | — | — | no (`external_body`, no `ensures`, no `unsafe`) |
| 5 | `emit` | — | — | no (same) |

SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

(a) The twin's body is `v[i]`, which is the checked stand-in for
`*v.get_unchecked(i)`: the two compute the same value and differ only in that
the first is a bounds-checked slice index and the second is not, so a `requires`
too weak to license the unchecked read is too weak to license the checked one
and Verus can see the second. The gate measured that: deleting the single
conjunct `i < v@.len()` takes the twin configuration from 20 verified / 0 errors
to 19 / 1.
(b) The `ensures` is complete with respect to every unchecked operation the body
performs. The body performs exactly one: a read of `v` at index `i`. Nothing is
written, nothing is aliased, no length is derived and no pointer escapes, so
`r == v@[i as int]` states the full observable effect. This is the accessor p01,
p02, p03, p05, p07, p11, p12, p16 and p17 ship character for character, and it is
the only item in p13 that touches the **source** buffer.
(c) Each clause means the same in both configurations. `v@.len()` for a `&[u8]`
is `spec_slice_len(v)` in both, and `v@[i as int]` is the same sequence index in
both; no `#[cfg]`-varying constant appears in either clause, and `slb_twin`
appears nowhere in this file except on the twins' own `#[cfg]` attributes, which
the gate checks.

SLB-TRUSTED-ARGUMENT verus.rs dst_get_unchecked

(a) The twin's body is `v[i]` against the trusted `*v.get_unchecked(i)`, on a
`&[u8; 32]` rather than a `&[u8]`. For a fixed-size array the checked index is
still a bounds check against `v@.len()`, which `array_len_matches_n` fixes at 32,
so the stand-in is exact. Deleting `i < v@.len()` takes the twin configuration
from 20/0 to 19/1, which is the gate's own measurement of that.
(b) The `ensures` is complete: the body reads `v` at `i` and does nothing else.
**What makes this item different from item 1 is not its contract, it is its call
site.** Its `requires` is discharged, in the consumer loop, from a fact about the
array's *contents* — `dst@[DST_CAP - 1] == 0` — rather than from any bound on
`d`, because the loop `while dst_get_unchecked(&dst, d) != 0 { d = d + 1; }` has
no bound. That is the two-site obligation this pattern exists for, and the
`ensures` is what makes it work: without `r == v@[i as int]` the loop body could
not learn `dst@[d] != 0` from the condition, and `d != DST_CAP - 1` — the step
that re-establishes `d < DST_CAP` — would not follow.
(c) Each clause means the same in both configurations. `v@.len()` for a
`&[u8; 32]` is 32 in both by `array_len_matches_n`; the second conjunct that
would say so is deliberately **not** written, because it is a tautology from the
parameter type and p03's gate run refused exactly that draft.

SLB-TRUSTED-ARGUMENT verus.rs dst_set_unchecked

(a) The twin's body is `v[i] = x` against the trusted
`*v.get_unchecked_mut(i) = x`. The checked indexed store is the exact stand-in:
same slot, same value, bounds-checked. Deleting `i < old(v)@.len()` takes the
twin configuration from 20/0 to 19/1.
(b) The `ensures` is complete with respect to every unchecked operation the body
performs, and the whole-sequence form is what makes it so:
`final(v)@ == old(v)@.update(i as int, x)` says both *slot `i` became `x`* and
*nothing else moved*. A per-slot `ensures` would be satisfied by a body that also
wrote `i + 1`, which is TASK_009_REVIEW's x4 and is invisible to the contract
pin, to the twin and to the `--cfg slb_twin` run alike. **On p13 the second half
is load-bearing in a way it is not on p12**: this one item performs the copy, the
zero-fill *and* the termination store, so the sentinel the consumer relies on is
a byte written by an earlier call to this item and required to still be there
after `DST_CAP - n` later calls to it. Only "nothing else moved" carries that.
The residual risk this argument does not close is a trusted body that does more
than its `ensures` says; Miri on R4 is the backstop, it is mandatory here, and
`spec.md`'s `miri.reason` says why p13's case is stronger than any earlier
pattern's.
(c) Each clause means the same in both configurations. `old(v)@.len()` is 32 in
both from the `&mut [u8; 32]` parameter type; `Seq::update` is the same spec
function in both; `x` appears in no `requires` in either, for the reason
`spec.md`'s `verus.unsafe_justifications` gives — it is a pure value parameter,
never used as an address, an index or a length.

---

## 3. THE LIBRARY AXIS — six routines, one checksum, and the prediction REFUTED

`controls/library_axis.py`, gcc -O3, `nstr = 32`, one window, `Ir` marginal per
**string**. All six routines carry the termination store and therefore **print
the same checksum**, which is what makes every difference below a library
difference with both routines named (`.memory/01-ladder.md` finding 9).

| `DST_CAP` | `slen` | hand | handnofill | memcpy | `strncpy` | `strlcpy` | `snprintf` |
|---|---:|---:|---:|---:|---:|---:|---:|
| 32 | 1 | 114.98 | 81.92 | 79.92 | **91.92** | 122.92 | 434.07 |
| 32 | 8 | 155.02 | 126.96 | 124.96 | **126.96** | 152.96 | 466.12 |
| 32 | 31 | 274.00 | 261.94 | 259.94 | **235.94** | 266.94 | 579.09 |
| 32 | 64 | 425.00 | 423.94 | 421.94 | **400.94** | 447.94 | 839.09 |
| 256 | 8 | 166.05 | 118.02 | 115.02 | **135.96** | 152.96 | 466.12 |

`hand` is the rungs' spelling; `handnofill` is the same with the zero-fill
deleted; `memcpy` is `handnofill` with the byte copy replaced.

### 3a. The safe routine is the expensive one

At `DST_CAP = 32`, `slen = 8`, matched:

```
strncpy   126.96 Ir/string     does NOT terminate at slen >= DST_CAP   <-- the bug
strlcpy   152.96 Ir/string     always terminates          +26.00  (+20.5%)
snprintf  466.12 Ir/string     always terminates         +339.16  (+267%)
```

**The routine that is unsafe-by-surprise is the cheapest of the three.** The
drop-in that always terminates costs **+26.00 Ir per string** and the
format-string one **+339.16**. `strlcpy` is dearer than `strncpy` despite doing
*no* zero-fill because glibc implements it as `strlen` + `memcpy` — two passes
over the source where `strncpy` makes one.

### 3b. The zero-fill's own cost, exactly isolated

`k_hand − k_handnofill`, same source, same `slen`, same everything else:

| `DST_CAP` | L=1 | L=4 | L=8 | L=16 | L=24 | L=31 | L=32 | L=64 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | +33.06 | +33.06 | +28.06 | +23.06 | +15.06 | +12.06 | +1.06 | +1.06 |
| 256 | +49.03 | +49.03 | +48.03 | +47.03 | +46.03 | +46.03 | +45.03 | +41.03 |

So `strncpy`'s padding is **the largest single per-string term at short source
lengths**: at `DST_CAP = 32` a one-byte string pays **+33.06 Ir** for bytes
nobody asked for, against **+1.06** for a 32-byte one. *The shorter the string,
the more the copy costs.* That is the cost "essentially nobody expects", and it
is now a number.

### 3c. ⚠ TASK_043's prediction is REFUTED IN BOTH HALVES

> "**`strncpy`'s cost is flat in the source length and linear in `DST_CAP`** —
> i.e. copying a 3-byte string into a 32-byte buffer costs the same as copying a
> 31-byte one."

**Not flat in the source length.** At `DST_CAP = 32`, `strncpy` costs
**106.96 Ir/string at `slen = 4` and 235.94 at `slen = 31`** — a factor of
**2.21**, not 1.00. The prediction implicitly assumes the fill dominates; it does
not, because the *kernel around the copy* is `O(slen)` twice over (the source
scan must find the terminator and the consumer must find it again), and those
two terms outrun the fill's decline.

**Not linear in `DST_CAP` either.** 8× the capacity buys far less than 8× the
cost, because both gcc and glibc switch to vectorised fills:

```
slen = 8, DST_CAP 32 -> 256 (an extra 224 bytes to fill):
  strncpy   126.96 -> 135.96   = +9.00 Ir    = +0.0402 Ir per extra DST_CAP byte
  hand      155.02 -> 166.05   = +11.03 Ir   = +0.0492
  strlcpy   152.96 -> 152.96   = +0.0000     (it does not fill: EXACTLY zero)
  snprintf  466.12 -> 466.12   = +0.0000     (ditto)
```

The fill of 255 bytes costs 49.03 Ir where the fill of 31 costs 33.06:
**8× the bytes for 1.48× the instructions.** What *is* exactly linear — at
coefficient **0.0000** — is the DST_CAP-dependence of the two routines that do
not pad, which is the cleanest confirmation available that the term is the fill
and nothing else.

**The largest single effect in the pattern is therefore not `DST_CAP` — it is
the routine.** `snprintf` against `strncpy` is +339.16 Ir/string (3.67×), an
order of magnitude larger than anything the capacity does.

### 3d. The compiler inserts the library call for you — including `strlen`

`objdump` on the probe and on the shipped cells:

| cell | bulk/library calls in the kernel at -O3 |
|---|---|
| `c-gcc` / `c-gcc-h`, isolated | `strlen@plt` |
| `c-gcc` / `c-gcc-h`, whole | `__memcpy_chk@plt`, `strlen@plt` |
| `c-clang` / `c-clang-h` | `memcpy@plt`, `memset@plt`, `strlen@plt` |
| `safe_naive` isolated | `memset@GLIBC_2.2.5` |
| `safe_tuned`, `unsafe`, `verus` | `memcpy@GLIBC_2.14`, `memset@GLIBC_2.2.5` |

⚠ **`strlen(` is in `spec.md`'s `idiom.forbidden` and no C source contains it,
and every C `-O3` cell calls it anyway.** Both compilers recognise
`d = 0; while (dst[d] != 0) d++;` and emit `strlen`. This is a measured limit on
what a text-level idiom pin can buy: **`spelling_matches` constrains the source,
not the object**, and a forbidden routine can arrive through the optimiser. No
Rust cell calls `strlen` — R2's consumer is a bounds-checked index and R3's is a
bounded iterator, and neither is recognisable as C's `strlen`.

That also means the C-vs-Rust consumer comparison carries a library term nobody
wrote, which is exactly why §4 reports the C column separately.

---

## 4. THE LADDER

`-O3`, `isolated`, kernel-symbol **exclusive** `Ir` from callgrind — never the
whole-program `summary:` line (`.memory/03-measurement.md`).

| rung | cell | static (nopad) | `Ir`/call small | `Ir`/call large | `Ir`/string small | `Ir`/string large |
|---|---|---:|---:|---:|---:|---:|
| R1 | `c-gcc` | 175 | 1758.00 | 5062.00 | 135.23 | 210.92 |
| R1h | `c-gcc-h` | 176 | 1771.00 | 5086.00 | 136.23 | 211.92 |
| R1 | `c-clang` | 92 | 1264.00 | 4475.00 | 97.23 | 186.46 |
| R1h | `c-clang-h` | 93 | 1277.00 | 4499.00 | 98.23 | 187.46 |
| R2 | `safe_naive` | 293 | 2710.00 | 9338.00 | 208.46 | 389.08 |
| R3 | `safe_tuned` | 224 | 1374.00 | 5395.00 | 105.69 | 224.79 |
| R4 | `unsafe` | 95 | 1591.00 | 6521.00 | 122.38 | 271.71 |
| R5 | `verus` | 95 | **1591.00** | **6521.00** | 122.38 | 271.71 |

`small` walks 13 strings per call, `large` 24.

### 4a. THE SAFETY TAX — `R1h − R1` is EXACTLY 1.00000 Ir PER STRING

```
small.bin  gcc   1771.00 - 1758.00 = +13.00 Ir/call = 13 strings x 1.00000
small.bin  clang 1277.00 - 1264.00 = +13.00 Ir/call = 13 strings x 1.00000
large.bin  gcc   5086.00 - 5062.00 = +24.00 Ir/call = 24 strings x 1.00000
large.bin  clang 4499.00 - 4475.00 = +24.00 Ir/call = 24 strings x 1.00000
```

and across the sweep (`controls/sweep_fit.py`), on **55 further blobs**:

```
band N (K = 1..24, all strings 8 bytes):  R1h - R1 == K exactly, both compilers
band L (K = 8, L = 1..31):                R1h - R1 == 8.00 on every one of 31 blobs
```

**Per what: per STRING.** Not per truncated string — band L holds no truncating
string below L = 32 and the difference is 8.00 on all of them — and not zero.
The store is unconditional, so it is paid on every string whether or not
`strncpy` would have terminated. It is the project's first safety tax that is a
*store* rather than a compare-and-branch, and it is a five-decimal figure
legitimately, because it is a matched-spelling difference of two cells printing
the same checksum on the same input (TASK_026 §0 item 2) **and** because it is
read off the kernel column rather than a whole-program marginal.

Relative: **+0.74% (gcc, small), +0.47% (gcc, large), +1.03% / +0.54% (clang)**.

### 4b. The bounds-check tax, matched spelling: R2 − R4

`safe_naive` and `unsafe` are the same four byte loops, indexed against
`get_unchecked`. Nothing else differs.

```
small.bin  2710.00 - 1591.00 = +1119.00 Ir/call  (+70.3%)  = +86.08 Ir/string
large.bin  9338.00 - 6521.00 = +2817.00 Ir/call  (+43.2%)  = +117.38 Ir/string
```

and its *per-scanned-byte* component, isolated on band L above the truncation
threshold where the copy, the fill and the consumer are all saturated and only
the source scan grows:

```
d(R2 - R4)/dL = +24.000 Ir per call per unit L over L = 33..48, K = 8
             => +3.00000 Ir per scanned source byte
```

**+3.00 Ir per source byte is the bounds check on the scan, exactly**, against
`unsafe`'s 6.00 Ir/byte for the same loop unchecked — a 50% surcharge on that
loop. This is p13's counter-example to "safety is free": it is not amortised
away by a bigger input, because the check is per byte and so is the work.

### 4c. R3 is CHEAPER THAN R4 — a SPELLING result, not a safety one

```
small.bin  safe_tuned 1374.00 - unsafe 1591.00 = -217.00 Ir/call  (-13.6%)
large.bin  safe_tuned 5395.00 - unsafe 6521.00 = -1126.00 Ir/call (-17.3%)
```

**Safe, bounds-checked Rust beats the unsafe rung by 13.6–17.3%.** Reported as a
spelling difference with the routines named (`.memory/01-ladder.md` finding 9):
R3 spells the copy `copy_from_slice` → `memcpy@GLIBC_2.14`, the fill `fill(0)` →
`memset@GLIBC_2.2.5` and the consumer `position()`, while R4 spells the copy and
the fill as unchecked byte loops. It is **not** a claim that checks are free; it
is a claim that on this kernel the bulk spellings are worth more than the checks
cost, and `controls/spellings.py` v3 prices the same R3 with byte loops at
+642.00 / +1674.00 Ir/call, which puts it back above R4.

### 4d. R4 ≡ R5 — zero in the kernel, −1.00 in `main`

Kernel-exclusive `Ir` is **identical to the instruction**: 95,460,000 both on
small, 130,420,000 both on large, `md5_fn 80d27392b903` both at `-O3`. The
whole-program marginal differs by exactly **−1.00 Ir/call**, and it is
attributable: `main`'s exclusive `Ir` is 780,274 (verus) against 840,275
(unsafe) on small, i.e. 60,001 fewer over 60,000 calls. **The proof costs zero
in the kernel; the one instruction is outside it**, in a `main` that reaches the
file through a trusted wrapper instead of inline. The `identity` pin covers the
kernel symbol and is `exact`.

### 4e. Wall clock — and it SURVIVES, which is unusual here

`common/layout/order.py --pattern p13-strncpy-trunc --input small --copies 15
--reps 15 --orders alt,gen`, 15 byte-identical copies at one layout:

```
identical-copy NOISE FLOOR   0.63% .. 1.86%   (per cell, per pass)
R2 vs R4   +8.60% .. +8.87%   (medians; copy#0 +8.93% .. +9.60%)
R3 vs R4   -6.40% .. -6.46%   (medians; copy#0 -5.96% .. -6.53%)
gen agrees with alt on both, so the shipped scheduler is alternating
```

Both effects are **4.6x to 14x the floor**, so unlike p05's, p01's and p07's,
p13's wall-clock rows are not withdrawn: `Ir` and `ns` agree in sign and roughly
in magnitude (+70% Ir / +8.7% ns for R2−R4 — the ratio is the point: `Ir` is not
a cost model, but here it is not the wrong *sign* either).

⚠ **The `t(n_iters = 1)`-corrected numbers do NOT resolve the termination
store**, and the bar is measured rather than assumed. Correcting
`t(N) − t(1)` (25 reps, median, `taskset -c 3`) and reading the **byte-identical
R4/R5 pair** as the null:

```
verus - unsafe (byte-identical kernels)  -3.66% (small)  +1.34% (large)
c-gcc-h - c-gcc (the termination store)  -2.87% (small)  +3.17% (large)
```

The null pair moves by up to 3.7 points, so the correction's own bar is ±3.7%
and **the store's ns cost is inside it**. Only `Ir` resolves 1.00 per string;
the raw level with the identical-copy protocol resolves the two *large* effects.
This is `.memory/03-measurement.md`'s rule doing its job: quote the raw level
where you can.

---

## 5. THE PROOF — one clause, five loops, and a two-site obligation

`./verus_run.py patterns/p13-strncpy-trunc/verus.rs` → **17 verified, 0 errors**,
first attempt. `--cfg slb_twin` → **20 verified, 0 errors**.

```
DST_CAP 1 + scan_end 1 + copy_into 1 + fill_zero 1 + scan_dst 1 + walk 1
        + kernel 6 + main 5 = 17
```

each measured with `--verify-function <name> --verify-root`. `kernel`'s **6** is
the highest in the project — one body plus **five** loop bodies (the string
walk, the source scan, the copy, the zero-fill and the consumer) against p12's
5, p11's 4, p07's 3 and p03's 2. No `by (nonlinear_arith)` anywhere in the
kernel: every multiplication in it is by a literal.

### 5a. The obligation, and why it is new

The consumer is
`while dst_get_unchecked(&dst, d) != 0 { d = d + 1; }` — **no bound at all**,
character for character C's runaway scan. What licenses the read is

```
invariant  d < DST_CAP,  dst@[DST_CAP - 1] == 0u8,  scan_dst(dst@, d) == scan_dst(dst@, 0)
```

and `d < DST_CAP` is re-established each iteration only from the array's
*contents*: the body runs under `dst@[d] != 0`, which with
`dst@[DST_CAP - 1] == 0` gives `d != DST_CAP - 1`. Every earlier pattern's
unchecked access is licensed by a guard on the index — p03's in the same basic
block, p12's one loop level up. **p13's is licensed by a fact about the array,
established by a different statement, and carried across a store into a loop.**
p11 proved a scan terminates from a sentinel it was *given*; p13 establishes the
sentinel first.

### 5b. One clause, and it cost ONE line, where p12's cost two

`requires off + len <= buf@.len()` is the whole precondition, structural, true
on every shipped input including the adversarial ones. Keeping it at one clause
costs `if (q >= len) break;` before the cursor step — p11's line, for p11's
reason (`q + 1` is `len + 1` when the window ends without a terminator).

**p12's second line has no analogue here, and that is a measurable difference
rather than an omission.** p12 had to buy `slen <= DST_CAP` as a left conjunct
(3.00 Ir per string walked) because `dlen + slen` is a `usize` addition nothing
bounded. p13's `n = min(slen, DST_CAP)` caps the copy against a compile-time
constant *before* any addition happens, so the copy loop's invariant
`i <= n <= DST_CAP` needs no extra program text. **The `min` the library
performs for you is also the proof obligation it discharges for you** — and
p13's `identity` pin therefore extracts **0.00 Ir** from any shipped cell, where
p12's extracts 3.00 per string.

---

## 6. TCB — five items, and the count the gate reports

See §2 for the table and the three `SLB-TRUSTED-ARGUMENT` sections. The declared
TCB is **5 `#[verifier::external_body]` items**, which is what
`results/gate/p13-strncpy-trunc.json` reports as its trusted-item tally; three
of them carry a `requires` and a verified twin, two (`load_input`, `emit`) have
neither an `ensures` nor `unsafe` and so are outside the twin regime while
remaining fully TCB.

### 6a. ⚠ WHAT THE CHECKSUM ORACLE CANNOT SEE — measured, not described

`controls/oracle_hole.py`. `spec.md`'s fold takes `d` and `dst[0]`, so the
contents of `dst[1 .. d]` are observable only through *"is this byte zero?"*.
Substituting `dst[i] = if i == 0 { buf[off + p + i] } else { 0xFF }` into R2's
copy loop:

```
identical on 9/9 shipped inputs  (small, large and all seven adversarial rows)
==> harness/check.py stage 2 (checksum agreement) and stage 5d (the `ensures`
    re-derived on 128 sampled calls) both pass a rung that copies the wrong
    bytes into the destination.
```

This is the price of the fold p13 needs — the `exact`/`truncate`/`truncate-alt`
triple can only collapse onto one answer if bytes past the truncation point stop
mattering — and it must be written down rather than assumed away.

**What does catch it, and it is the sharper half of the result:**

```
verus.rs with the same substitution: 16 verified, 1 errors
  | error: invariant not satisfied at end of loop body
```

**R5's `ensures` discriminates a copy error that the entire checksum apparatus
cannot.** On p13 the proof is strictly stronger than the oracle, which is the
first time this project has been able to say so with a demonstration rather than
an argument.

---

## 7. THE ADVERSARIAL TABLE — per rung, and the two harms in separate columns

Every adversarial row is exactly one window (`n_blob == stride`), so R1's
overread happens on every call deterministically. Columns:
**TRUNC** = content silently discarded (memory-safe wrong answer);
**OOB** = out-of-bounds read of the frame.

| input | shape | TRUNC | OOB | checked rungs (R1h, R2–R5) | R1 `c-gcc` | R1 `c-clang` | ASan+UBSan |
|---|---|---|---|---|---|---|---|
| `adversarial-exact` | 4 × 31 B | no | no | `17389639996120294144` | agrees | agrees | clean |
| `adversarial-truncate` | 4 × 32 B | **1 B/string** | **yes** | `17389639996120294144` | wrong, 2 distinct values over the 4 builds | wrong, 3 distinct | **fires** |
| `adversarial-truncate-alt` | 4 × 40 B | **9 B/string** | **yes** | `17389639996120294144` | wrong, 2 distinct | wrong, 3 distinct | **fires** |
| `adversarial-nonul-dst` | 4 × 96 B | **65 B/string** | **yes** | `1150023818285712768` | wrong, 2 distinct | wrong, 3 distinct | **fires** |
| `adversarial-nonul-src` | 20,20,40 unterminated | **9 B** | **yes** | `17351778568866771200` | wrong, 2 distinct | wrong, 2 distinct | **fires** |
| `adversarial-empty` | 8 × 0 B | no | no | `227437609984` (= `nstr`) | agrees | agrees | clean |
| `adversarial-stride3` | stride 3 | — | — | `0`, zero kernel calls | agrees | agrees | clean |

**No specific wrong answer is quoted, deliberately: none of them is a number.**
The values differ between opt/mode variants of the same rung, and they differ
between *gate runs of the same binary* — `.temp/p13/gate3.log` and
`.temp/p13/gate_final.log` disagree on all four truncating rows.

Read the first three rows together. **`exact`, `truncate` and `truncate-alt`
print the same checksum in every checked rung** while destroying 0, 1 and 9
bytes per string respectively — the memory-safe harm, isolated, and invisible to
a proven program. And `exact` is sanitizer-clean where the other two fire — the
memory-safety harm, attributed to the one rung that has it. **No single input
separates them, so the table does** (§1a).

Two per-cell facts the gate's own notes record:

- **`c-gcc` and `c-clang` disagree with THEMSELVES across opt/mode** on all four
  truncating rows — 2 and 3 distinct behaviours respectively. `check.py` reports
  this as `opt/mode variants of this rung disagree`.
- **And three of `c-clang`'s four builds disagree with themselves across RUNS,
  while all four of `c-gcc`'s are stable** — 60 runs of each single binary on
  `adversarial-truncate.bin`:

  | cell | O0 isolated | O0 whole | O3 isolated | O3 whole |
  |---|---|---|---|---|
  | `c-gcc` | stable | stable | stable | stable |
  | `c-clang` | 2 values (58/2) | 2 values (37/23) | 2 values (33/27) | stable |

  ⚠ This is the **exact reverse** of what the phase-0 probe found on a
  two-kernel translation unit (§0b), which is why the general claim is that
  **reproducibility is a property of the individual binary's frame layout and
  cannot be predicted from the compiler or the optimisation level.** A reviewer
  re-running this will get different *values* than either log records; the
  *counts* of distinct behaviours are what reproduce.
- **Nothing crashes.** Every R1 cell exits 0 on every row. p12's failure ladder
  (silent → canary abort → SIGSEGV) has **no analogue in p13**, because the
  overread is 1–7 bytes into the kernel's own frame and never reaches an unmapped
  page. That makes p13 the *quieter* bug of the two: p12's worst case kills the
  process, p13's worst case is a wrong answer nobody notices.

UBSan's diagnostic, from the gate:
`patterns/p13-strncpy-trunc/c/kernel.c:70:19: runtime error: index 32 out of
bounds for type 'uint8_t [32]'`.

---

## 8. THE SWEPT LAWS — the rank first, and the law that does NOT close

`controls/sweep_fit.py`. Regressors per call: `1`, `K` (strings walked), `S`
(source bytes scanned), `C` (bytes copied), `T` (strings truncated).
`F`, the zero-filled bytes, is **not independent** — `C + F == DST_CAP * K`
identically — and neither is `D`, the consumer's bytes — `D == C - T + K`. Both
identities are asserted per blob by the script rather than argued.

### 8a. The rank, computed BEFORE anything was measured

```
band N   24 blobs   rank 2/5      K = 1..24, all strings 8 B
band L   48 blobs   rank 4/5      K = 8, L = 1..48, CROSSING DST_CAP
band T   17 blobs   rank 2/5      K = 16, t of them 40 B, t = 0..16
POOLED   89 blobs   rank 5/5
pair N+L  rank 5/5     pair L+T  rank 5/5     pair N+T  rank 3/5
FIT SET (N+L)                        rank 5/5   <- identified
FIT SET AS R1 SEES IT (T == 0 only)  rank 3/5   <- NOT identified
```

TASK_043 asked for the rank check before measuring seven cells across a hundred
blobs, and it paid twice: **band N alone is rank 2** (which is why `sweep-l*` had
to cross `DST_CAP` rather than stop below it), and — the structural one —
**R1's design is rank 3 of 5 and can never be more.** R1 cannot be run on a
truncating blob at all, and among non-truncating rows `C == S − K` exactly, so
`C` and `T` are both unidentifiable for R1 *by construction*. That is
`.memory/03-measurement.md`'s "a law in SOMEBODY's counts" as a property of the
design rather than of an accident.

### 8b. The five-regressor law does not close, and that is the result

Fitted exactly (rational) on N+L, worst residual over the fit set:

| cell | worst in-sample residual | band T out-of-sample |
|---|---:|---:|
| `c-gcc` | — rank 3/5, NOT IDENTIFIED | — |
| `c-gcc-h` | 130.29 | 12.24 |
| `c-clang` | — rank 3/5, NOT IDENTIFIED | — |
| `c-clang-h` | 115.43 | 12.24 |
| `safe_naive` | 888.30 | 5.10 |
| `safe_tuned` | 115.43 | 5.10 |
| `unsafe` / `verus` | 115.43 | 5.10 |

**No cell has an exact integer linear cost model in these regressors**, and p13
is the first pattern here where that is true. The mechanism is the pattern's own
subject: `strncpy`'s two halves compile to **size-dispatched vector code**
(`memset`, `memcpy`, and `strlen` for the consumer), so the per-string cost is a
**step function** of the byte count, not a linear one — and there is a large
discontinuity at `slen == DST_CAP`, where the copy saturates, the zero-fill
disappears entirely and the consumer stops growing.

**No law is published for p13.** What is published is the piecewise structure
and the exact slopes inside each regime.

⚠ **And a limitation of what this delivers, stated rather than buried: the
out-of-sample test could not do its job here.** `.memory/03-measurement.md`
demands a blob that turns on every regressor at once, predicted before it is
measured; `sweep-t*` is that blob and its residuals (5.10 / 12.24) are *smaller*
than the in-sample ones (115.43 / 888.30). That is not the law surviving — it is
band T sitting close enough to the fit region that a wrong law misses it by less
than it misses its own fit set. **An out-of-sample test can only falsify a law
that holds in sample**, and p13 has none, so the mechanism p04's review built
this rule for is untested on p13. It would become testable if somebody found a
regressor set in which p13's cost IS linear — a `ceil(F/32)`-style step basis is
the obvious candidate and nobody has built it.

### 8c. What IS exact: the regime slopes on band L

`Ir` per call per unit `L`, `K = 8`, endpoint-to-endpoint over `L = 33..48`
(above the threshold, where copy/fill/consumer are all saturated and only the
**source scan** grows):

| cell | Ir/call per unit L | **Ir per source byte** |
|---|---:|---:|
| `c-gcc-h` | +40.000 | **5.00000** |
| `c-clang-h` | +48.000 | **6.00000** |
| `safe_naive` | +72.000 | **9.00000** |
| `safe_tuned` | +48.000 | **6.00000** |
| `unsafe` / `verus` | +48.000 | **6.00000** |

and the matched differences, exact because both cells print the same checksum on
the same blob:

```
safe_naive - unsafe      +24.000/L  = +3.00000 Ir per scanned source byte
safe_tuned - unsafe        0.000/L  =  0.00000   (the reslice deletes the check)
c-clang-h  - unsafe        0.000/L  =  0.00000   (same LLVM, same code)
c-gcc-h    - unsafe       -8.000/L  = -1.00000   (gcc's scan is 1 Ir/byte cheaper)
```

⚠ **The C-vs-Rust rows carry a driver term the Rust-vs-Rust rows do not.** C
prints with `printf` and Rust with `println!`, so the per-digit cost does not
cancel between languages: the *level* differences carry ±0.6 Ir/call of digit
noise (visible as the `.42`/`.58` fractional parts in the band-N series), while
the *slopes* above are clean because a per-call constant cancels in a slope.
TASK_026 §0 item 2, applied.

The **truncation cliff** at `L = 31 → 32`, where every string crosses `DST_CAP`
at once:

```
c-gcc-h   -72.00     c-clang-h  -128.00    safe_naive -112.00
safe_tuned +48.00    unsafe/verus -120.00
```

`safe_tuned` is the only cell that gets **more expensive** at the cliff — its
`copy_from_slice` widens to the full 32 bytes while the others lose a whole
`memset`.

---

## 9. PROOF MUTANTS — four, and one of them verifies cleanly

`controls/mutants.py`. Derived from the shipped `verus.rs` by exact-string
substitution with asserted hit counts, written to `.temp/p13/mutants/`
(`.memory/05-layout.md` item 11: a broken proof cannot live in the pattern dir).

| mutant | shipped cfg | `--cfg slb_twin` | caught by |
|---|---|---|---|
| **M1** delete the TERMINATION STORE from the exec code | 16 verified, **1 error** — `invariant not satisfied before loop` | 19 / 1 | **Verus** |
| **M2** weaken the trusted `dst_get_unchecked` `requires` to `i <= v@.len()` | **17 verified, 0 errors** | **20 / 0** | **`spec.md`'s `verus.items` pin alone** (check.py 5a) |
| **M2b** the same weakening applied to the trusted item *and* its twin | 17 / 0 | 19, **1 error** — `precondition not met: index in bounds for this access` | Verus (the **twin**) + the pin |
| **M3** delete the invariant `dst@[DST_CAP - 1] == 0` from the consumer loop, keeping the store | 16 verified, **1 error** — `assertion failed` | 19 / 1 | **Verus** |

**M1 is the pattern's own bug, in the rung that has a proof, and Verus refuses
it.** That is the relation an omitted line should have to a proof: not "the
postcondition is weaker" but "the memory-safety obligation is unprovable".

**M1 and M3 together separate the two sites.** M1 removes the fact at the
*write*; M3 leaves the write and removes the carrying of the fact into the
*read*. Each alone breaks the proof, which is what "two-site obligation" means
operationally.

**M2 is p02's M7 reproduced on p13**: a one-character weakening of a trusted
precondition that Verus accepts in **both** configurations, because the twin's
own contract was not touched and the call sites still prove the stronger fact.
Only `spec.md`'s item pin sees it (`dst_get_unchecked.requires: file says
['i <= v@.len()'], spec.md pins ['i < v@.len()']`). M2b then shows what the twin
regime is actually for: once the two configurations are made to agree, the
verified twin fails on the off-by-one.

---

## 10. THE R3-SIDE SPAN, AND THE FIXED-R4 BOUND

`controls/spellings.py`. Five in-contract R3 spellings, **each audited against
`harness/check.py::spelling_matches` for every backticked entry of `spec.md`'s
`idiom` before its number is quoted**, and each printing the shipped checksum on
both inputs.

| variant | `small.bin` | `large.bin` | in contract |
|---|---:|---:|---|
| `v0_shipped` | **1721.41** | **5997.30** | yes |
| `v1_onestep_reslice` | 1722.41 | 5998.30 | yes |
| `v2_takewhile_consumer` | 1721.41 | 5997.30 | yes |
| `v4_fill_explicit_end` | 1721.41 | 5997.30 | yes |
| `v3_byteloop_copy` | 2363.41 | 7671.30 | yes |
| R4 (`unsafe`, shipped) | 1938.41 | 7123.30 | — |

(whole-program `Ir` marginals, `n_iters` 100→200; the R3−R4 differences agree
exactly with the kernel-column differences in §4c.)

**The shipped R3 IS the cheapest found**, so the two bounds coincide and both are
stated anyway (`.memory/02-bench-rules.md`'s reporting corollary):

```
small.bin   fixed-R4 bound  R3ship - R4ship          = -217.00 Ir/call
            cheapest found  inf(in-contract) - R4ship = -217.00 Ir/call  (v0_shipped)
            R3-side span    1721.41 .. 2363.41, width 642.00 (v0_shipped .. v3_byteloop_copy)
large.bin   fixed-R4 bound                            = -1126.00 Ir/call
            cheapest found                            = -1126.00 Ir/call  (v0_shipped)
            R3-side span    5997.30 .. 7671.30, width 1674.00
```

The cheapest spelling is the same on both inputs here, which is **not** the case
on p03 and p16 — so the input is named anyway.

**The R4 side is not searched and no pair interval is published** (TASK_026 §0
item 4). p13's R4 is chained to the prover by the `identity: exact` pin, and
every candidate would need a byte-identical R5 twin that verifies at the pinned
vstd.

### 10a. `.memory/01-ladder.md` finding 3's two-step reslice reproduces here

`v1_onestep_reslice` respells only `buf.split_at(off).1.split_at(len).0` as
`&buf[off..off + len]` and is **+1.00 Ir/call on both inputs** — the same
`−1 Ir/call` lever finding 3 measured on p04, on a second pattern, at the same
magnitude, with the same two panic paths present in both. p13 spelled it the
cheap way from the start, so the lever costs p13 nothing and is measured rather
than inherited.
