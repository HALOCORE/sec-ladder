# TASK_013_REVIEW — p05: is the check really free, and is the model really predictive?

**Verdict, one line: `.memory/01-ladder.md` finding 6 OVERCLAIMS.** Every *number* in it
reproduced exactly on independently rebuilt binaries and on shapes the engineer never
measured — but four of its framing sentences overreach, one of them ("the wider the lane,
the cheaper safety gets") is **refuted by measurement**, and one ("4.25 is rustc's
per-element checked-scalar-fold cost") repeats verbatim the framing TASK_007_REVIEW already
corrected on p16. It also *under*claims in three places, the largest being that the
16-parameter model is really a **zero-parameter closed form** that falls out of the
disassembly.

Everything below was measured by this reviewer: fresh builds from the shipped sources with
`build.py`'s flags, own input generator, own callgrind runner, own arithmetic. Scratch,
scripts and raw logs: `.temp/review013/` (`NOTES.md`, `gen_probe.py`, `measure_ir.py`,
`wall.py`, `*.full` disassembly listings). Nothing under `patterns/`, `harness/`,
`.memory/`, `pilot/` was touched; `git status` is clean apart from the task file the
manager created; no `results/gate/` record was written (I never ran the gate).

---

## PART 1 — the mechanism. Where the bounds check went, and why it is free

This is the deliverable the task asked for. **It is not "it vanished": the check is hoisted
into a 22-instruction per-row trip-count computation and a scalar epilogue that still
carries it, and the whole published model is a closed-form consequence of that.**

### 1.1 The three loop shapes, from the disassembly (`-O3 isolated`)

`.temp/review013/{unsafe,safe_naive,safe_tuned}.full` are the address-annotated listings.

**R4 (`unsafe`), per call:** `and $0x7,%r8d` / `mov %r9,%rax` / `sub %r8,%rax` — `ncol & 7`
and the vector limit `ncol - (ncol&7)`, computed **once per call** and hoisted out of both
loops. Per row: `cmp $0x8,%r9d ; jae` (vector iff `ncol >= 8`), the 11-instruction vector
body, a 6-instruction horizontal reduce, `test %r8,%r8 ; je` (skip the epilogue entirely
when `ncol % 8 == 0`), a 5-instruction-per-element unchecked scalar epilogue, and a
10-instruction row tail. The index `i*ncol` is **strength-reduced to a running pointer**
(`add %r9,%r11 ; add %r9,%rdx`), so R4 executes no `imul` in the row loop at all.

**R2 (`safe_naive`), per row (`157d0`–`1581a`, 22 instructions):**

```
cmp %rcx,%rsi ; mov %rcx,%rax ; cmova %rsi,%rax ; add %r15,%rax      # bytes left from row start
cmp %rax,%rbx ; cmovb %rbx,%rax                                      # min(that, ncol-1)
mov %r9,%rdi  ; imul %r10,%rdi ; lea 0x4(%rdx),%r8 ; add %r8,%rdi    # rowbase = off+4+i*ncol
cmp %rdi,%rsi ; cmova %rsi,%rdi
mov 0x18(%rsp),%r8 ; imul %r10,%r8 ; add %rdx,%r8 ; sub %r8,%rdi
add $-4,%rdi  ; cmp %rdi,%rbx ; cmovb %rbx,%rdi ; inc %rdi           # N = min(ncol, len-rowbase)
cmp $0x9,%rdi ; jae <vector>                                         # vector iff N >= 9
```

That is the answer to "where did it go": **the per-element `j < len` test is turned into a
per-row `min`/`max` chain that computes `N`, the number of iterations provably in range.**
The vector loop then runs `N` iterations with no check in it, and the panic is still
reachable — it lives in the scalar epilogue, `cmp %rsi,%rdi ; jae <panic>` at `158c0`. Note
the two `imul`s: LLVM can strength-reduce the flattened index in R4 but not in R2, because
the bound test needs the absolute index.

**The smoking gun for `f(0)`,** at `15830`:

```
mov %edi,%r8d ; and $0x7,%r8d ; mov $0x8,%r11d ; cmove %r11,%r8      # remainder 0 -> 8
```

A remainder of zero is **forced to a full vector width**. R2 therefore always runs between
1 and 8 checked scalar iterations per row; R4 runs 0 when `ncol % 8 == 0`. This is LLVM's
"early-exit loop requires a scalar epilogue" policy: R2's row loop has two exits (`j==ncol`
and the panic), so the last vector chunk must be re-executable scalar-wise, and the
remainder can never be allowed to be 0.

**R3 (`safe_tuned`), per row:** `mov %r15,%rax ; imul %r11,%rax ; add %rsi,%rax ;
lea (%rax,%r11,1),%rdx ; cmp %r8,%rdx ; ja <panic>` — **6 instructions**, the reslice's
single `base+ncol <= len` test, and then R4's loop verbatim.

**Epilogue cost per element: R2 8 Ir (`cmp,jae,movzbl,add,inc,inc,dec,jne`), R4 5 Ir
(`movzbl,add,inc,cmp,jne`).** The 3-instruction difference is 2 for the check plus 1 for the
second induction variable the check forces (R2 must keep both a pointer for the load and an
index for the comparison). That 3 is exactly the `3·(ncol mod 8)` term of the published model.

### 1.2 The whole model, with zero fitted parameters

Let `q = ncol div 8`, `r = ncol mod 8`, `e = ((ncol-1) mod 8) + 1`, `V = (ncol-e)/8`.
Counting instructions off the listings — **including two alignment `nopw`s that sit on the
executed path** (`15855`, `158ba` in R2; `156ca`, `15724` in R4), which callgrind counts and
a naive static count drops:

| rung | Ir per call |
|---|---|
| R4 / R5 / c-clang | `37 + nrow·(27 + 11q + 5r)`, `r >= 1`; `37 + nrow·(25 + 11q)`, `r = 0` |
| R3 | `46 + nrow·(33 + 11q + 5r)` / `46 + nrow·(31 + 11q)` |
| R2 | `72 + nrow·(56 + 11V + 8e)` — for `ncol >= 9`; below that R2 takes the scalar-only path |

Subtracting: **`R2 − R4 = 35 + nrow·(29 + 3r)` for `r >= 1`, and `35 + nrow·84` at `r = 0`;
`R3 − R4 = 9 + nrow·6`.** The published `f = [84,32,35,38,41,44,47,50]` is `29+3r` with one
structural discontinuity, and `f(0) = 84` decomposes as `29 + 64 − 11 + 2`: R2 runs 8 checked
scalar elements (**+64**), gives up one vector iteration to pay for them (**−11**), and R4
skips its epilogue-entry `nop`+`jmp` (**+2**).

Checked against the shipped table and my own runs — every one exact, no residual:

| shape | R2 pred/meas | R3 pred/meas | R4 pred/meas |
|---|---|---|---|
| 19×26 (`small`) | 2067 / **2067** | 1490 / **1490** | 1367 / **1367** |
| 65×61 (`large`) | 11317 / **11317** | 8821 / **8821** | 8422 / **8422** |
| 53×32 | 8181 / **8181** | 4021 / **4021** | 3694 / **3694** |
| 7×129 | 1752 / **1752** | 1544 / **1544** | 1493 / **1493** |
| 496×9 | 37272 / **37272** | — | 21365 / **21365** |
| 496×16 | 65048 / **65048** | — | 23349 / **23349** |

**So `f` is not absorbing anything.** The write-up's "16 parameters solved from 16 points"
is an *under*claim: it is a 0-parameter derivation, and stating it that way removes the
degrees-of-freedom objection entirely. This is the single change I would most like made to
`NOTES.md` §2a and finding 6.

### 1.3 Why the cost exists at all — and it connects to R5's proof

The kernel already checked `nrow*ncol <= avail`, so **every row is provably in range and
R2's panic is dead on every execution**. LLVM cannot use that fact, because
`nrow*ncol <= avail ⟹ i*ncol + j < avail` is **nonlinear in two variables** — the exact
obligation `verus.rs` needs `lemma_mul_inequality` plus a `by (nonlinear_arith)` for
(`NOTES.md` §5a). The 29+3r Ir/row is the price of the optimiser failing the lemma the proof
discharges. R3 costs 6 because the reslice makes the same fact *linear per row*: one
comparison instead of a min/max chain over a product. **That sentence is p05's best result
and it is not in the write-up.**

### 1.4 The per-element rate: measured, not rounded

Own zero-residue lag pairs at `nrow = 53` (a value no band used), `ncol ∈ {32,64,96,128}`,
all `≡ 0 (mod 32)`, **kernel-exclusive Ir** (so the driver's `println!` digit-count term is
not merely cancelled, it is not present):

| cell | 3272→ | Δ per +32 ncol | Δ elements | Ir/element |
|---|---|---|---|---|
| safe_naive | 8181, 10513, 12845, 15177 | **2332** each | 1696 | **1.375000** = 11/8 |
| safe_tuned | 4021, 6353, 8685, 11017 | **2332** | 1696 | **1.375000** |
| unsafe = c-clang | 3694, 6026, 8358, 10690 | **2332** | 1696 | **1.375000** |
| c-gcc | 3272, 5074, 6876, 8678 | **1802** | 1696 | **1.062500** = 17/16 |

`0.0000` is **`2332 − 2332` on integers**, not a difference of rounded rates. The denominator
is right: at fixed `nrow`, `Δelements = nrow·Δncol` exactly — header bytes and Horner steps
are constant across the pair. Checksums identical in all five rungs on every input.

**Identical mnemonics: true.** c-clang, safe_naive, safe_tuned, unsafe and verus all emit the
same 11-instruction body (`movd,movd,punpcklbw,punpcklwd,paddd,punpcklbw,punpcklwd,paddd,
add,cmp,jne`), differing only in which GP registers carry base and index. gcc's is a
different 17-instruction/16-element body plus a narrower `movq` second vector loop.

---

## PART 2 — the `u64 → u32` deviation

### 2.1 The `u64` claim is confirmed

Rebuilt every rung with a `u64` row accumulator (exact-string substitution,
`.temp/review013/u64/`), `-O3`, no `-march`:

```
safe_naive64  n_fn_nopad=83   xmm_insns=0    vector_regs=[]
safe_tuned64  n_fn_nopad=121  xmm_insns=0    vector_regs=[]
unsafe64      n_fn_nopad=79   xmm_insns=0    vector_regs=[]
c-clang64     n_fn_nopad=91   xmm_insns=0    vector_regs=[]
c-gcc64       n_fn_nopad=184  xmm_insns=39   vector_regs=['xmm']
```

```
u64: remark: the cost-model indicates that vectorization is not beneficial [-Rpass-missed=loop-vectorize]
u32: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]
```

VW4×IC2 = 8 elements/iteration, matching the disassembly. The engineer's `xmm=39` for gcc
reproduces to the instruction.

### 2.2 The deviation is *sounder than the write-up claims*, and the write-up left its best
argument on the table

`NOTES.md` §1 defends `u32` with "a 32-bit per-row checksum is also what a real row hash
would use" — an aesthetic argument. The available argument is a proof: **`ncol` is a `u16`,
so `ncol <= 65535`; elements are `u8`, so a row sum is at most `65535·255 = 16 711 425 <
2^32`. The `u32` accumulator can never wrap on any input this wire format can express.** The
`u32` and `u64` builds are therefore not "equal on the shipped inputs", they are equal on
*every representable input*. Confirmed empirically anyway: identical checksums on
`small`/`large`/`adversarial-zero`/`adversarial-stride3` for all three Rust rungs.
`model.py` masks with `MASK32`, so it is faithful and the mask is provably never live.

**Judgement: the deviation is fine.** It changes no answer, it is not a fitted-to-hypothesis
choice in the semantic sense, and the honest alternative the engineer names in §11 ("gcc
vectorises, LLVM does not") is a strictly worse experiment.

### 2.3 But it does narrow the result, and the write-up's generalisation is refuted

`NOTES.md:14` and finding 6's headline generalise to **"the wider the lane, the cheaper
safety gets."** That is measurable, and it is false. Built the *shipped* sources with
`-C target-feature=+avx2` (`vpmovzxbd`, 32 elements/iteration), `nrow = 53`,
kernel-exclusive Ir/call:

| ncol | SSE2 R2 | SSE2 R4 | gap | AVX2 R2 | AVX2 R4 | gap |
|---|---:|---:|---:|---:|---:|---:|
| 128 (`≡0 mod 32`) | 15177 | 10690 | 4487 | **18674** | **4073** | **14601** |
| 160 (`≡0 mod 32`) | — | — | — | 19257 | 4656 | 14601 |
| 129 (`≡1`) | 12792 | 11061 | 1731 | 6113 | 4603 | 1510 |

Widening the lane makes **safe Rust absolutely slower** (15177 → 18674 Ir/call) while unsafe
gets 2.6× faster, and the safe/unsafe ratio goes **1.42× → 4.58×**. The mechanism is exactly
the one in Part 1: the forced scalar peel is *VF elements long*, so it grows with the lane
while the vector loop shrinks. Per element the check is still `0.0000` at AVX2 (the gap is
identical at ncol 128 and 160), so the *narrow* claim survives — the *generalisation* does
not. p05 measures "the check is free per element at SSE2 width 8, and the residual is a
per-row peel that gets worse as the lane widens".

### 2.4 The two-sided control: the objection does not land, and a one-sided control *does*
exist and was not run

`NOTES.md` §11 says p16's `-unroll-count=1` was better because it was a bit-for-bit no-op on
R2, and that p05 has no such control. **That is wrong.** Applying `-unroll-count=1` on top of
the no-vectorise flags gives R2 `md5_fn = 76d7c2380278`, **identical to the no-vectorise-only
build** — a bit-for-bit no-op, exactly as on p16. Running it (nrow 53, zero-residue pair):

| fold | Ir/element |
|---|---:|
| R2, rolled + checked | **7.0000** |
| R4, rolled + unchecked (`-unroll-count=1`) | **5.0000** |
| R4, novec 4×-unrolled + unchecked | **2.7500** |
| c-gcc, novec rolled + unchecked | **5.0000** (free corroboration) |

**`4.2500 = 2.0000 (the check) + 2.2500 (the unroll it forecloses)`, zero residual — the
identical split TASK_007_REVIEW derived on p16.** So:

- the vectorisation-off control's two-sidedness does **not** weaken the 4.25 attribution
  (both rungs are at the same flag; the comparison is same-source, check-only);
- but finding 6's sentence *"So 4.25 is rustc's per-element checked-scalar-fold cost"*
  (`.memory/01-ladder.md:453`) is the exact framing that review corrected. Only 2.00 of it is
  the check.

---

## PART 3 — the predictive model

### 3.1 Held-out prediction, 16 new points, error 0.0000

`nrow ∈ {53, 7}` (bands A/B/C used 19/65/41) and `ncol ∈ {32,64,96,128,129…136}` (bands used
24–87 / 56–119 / 24–39). Predicted from the published `35 + nrow·f(ncol mod 8)` /
`9 + nrow·6`, measured with my own runner:

```
nrow=53: ncol 129..136 -> R2-R4 meas 1731 1890 2049 2208 2367 2526 2685 4487
                          pred      1731 1890 2049 2208 2367 2526 2685 4487   err 0
         ncol 32/64/96/128 -> 4487 4487 4487 4487 (pred 4487)                 err 0
         R3-R4 = 327 at all 12 points (pred 9+53*6 = 327)                     err 0
nrow=7:  ncol 129 -> 259 (pred 259);  ncol 136 -> 623 (pred 623)              err 0
         R3-R4 = 51 at both (pred 9+7*6 = 51)                                 err 0
```

**16/16 exact.** The model predicts, it does not interpolate.

### 3.2 `f(0) = 84` — explained (Part 1.2). And the model has an unstated domain

`f(0)=84` is `29 + 64 − 11 + 2`, derived above and confirmed to the instruction. But the
model is published unconditionally, and it is **false for `ncol <= 8`**, because R2's guard
is `N >= 9` where R4's is `ncol >= 8`:

```
nrow=496, ncol=8:  R2 52648  R4 17893  ->  R2-R4 = 34755
                   published model:  35 + 496*84 = 41699   (16.6% error)
nrow=496, ncol=7:  R2 48680  R4 25333  ->  R2-R4 = 23347   (model 24835, wrong)
```

Both bands started at `ncol = 24`, so the boundary was never sampled. Domain: `ncol >= 9`.

### 3.3 Back-end periods: both confirmed

Own sweep, `nrow = 53`, `ncol` 160…192, kernel-exclusive Ir/call:

- **c-clang: period 8.** Drops at 160/168/176/184/192; `168 − 160 = 583 = 53·11`, i.e. one
  11-instruction vector iteration per row → 1.375 Ir/element.
- **c-gcc: period 16.** `176 − 160 = 901 = 53·17` → 1.0625 Ir/element, plus a *secondary*
  drop at multiples of 8 from its narrower `movq` epilogue loop. So gcc has structure at both
  8 and 16, and `NOTES.md` §1b already says why; the "period 16" headline is right.

### 3.4 The aspect ratio is the model's most important consequence, and it is not drawn

The cost is `O(nrow)`, so at a fixed element count it depends entirely on the shape. Measured
at ~3968 elements/call — the same size as shipped `large`:

| shape | R2 | R3 | R4 | R2/R4 | R3 vs R4 |
|---|---:|---:|---:|---:|---:|
| 496×8 (`ncol` a power of two) | 52648 | 20878 | 17893 | **2.94×** | **+16.7%** |
| 496×16 | 65048 | 26334 | 23349 | **2.79×** | **+12.8%** |
| 331×12 | 32841 | 21230 | 19235 | 1.71× | +10.4% |
| 65×61 (shipped `large`) | 11317 | 8821 | 8422 | 1.34× | +4.7% |
| 31×128 | 8907 | 6463 | 6268 | 1.42× | +3.1% |

**And at `ncol = 8` exactly, the bounds check does block vectorisation**: R2 needs `N >= 9`,
R4 needs `ncol >= 8`, so R4 takes the vector path and R2 does not — the commissioned
hypothesis, confirmed in a one-value band that is also the most likely tile width a real
kernel would use. "The hypothesis is inverted" is right for the swept range and wrong at the
boundary.

---

## PART 4 — standard validity

All confirmed, on my own rebuilds:

- **R1 vs R1h are one line apart.** `diff c/kernel.c c/kernel_hardened.c` is comments plus
  `(void)avail;` → `if (nrow * ncol > avail) return 0;`.
- **The `int`-width variant fires UBSan then ASan**, reproduced byte for byte including the
  address: `runtime error: signed integer overflow: 65535 * 65535 cannot be represented in
  type 'int'`, then `heap-buffer-overflow ... 0x507000000148 is located 0 bytes after 72-byte
  region`. The shipped 64-bit check prints `0`, clean.
- **`adversarial-zero` amplification is real.** Guard deleted: gcc **786 467** Ir/call
  kernel-exclusive against `c-gcc-h`'s **28** (28 088×); clang 19 against 13 (+6). The
  engineer's 43 → 786 482 (18 290×) is the same measurement with the marginal-whole-program
  denominator, which adds ~15 driver Ir to both sides. Both correct; the clang **delta of 6**
  is identical in both methods.
- **19 of 32 cells, and the per-cell counts, are exact** (recounted with `asm.py`,
  kernel-only in `isolated`, `main`-only in `whole`): gcc 50/49, clang and all Rust 17/27,
  and the three `O0 whole` hits are exactly `movups 0xc0(%rsp),%xmm0 ; movaps %xmm0,0xa0(%rsp)`
  — an aggregate stack move, not the fold.
- **The whole §2c Ir table reproduces to the instruction** on freshly built binaries:
  1730/1367/1737/1369/2067/1490/1367/1367 (`small`), 9204/8422/9211/8424/11317/8821/8422/8422
  (`large`), with identical checksums in all eight cells.
- **`R4 ≡ R5` byte-identical**: `md5_fn = 4a28657ae7e4` *and* `md5_raw = 71d96f8891d5` equal.
- **Verus: `12 verified, 0 errors`**, reproduced. TCB recounted: 3 `external_body` items,
  bodies of 1 + 4 + 1 = **6 lines**, one `unsafe` token, all inside a trusted body. Correct.
- **Wall clock survives its spreads.** Independent run, cpu 5, 21 reps, round-robin,
  `n_iters` 12000→36000, raw sample-set spreads 0.7–1.7%: safe_naive **+32.9%**, safe_tuned
  **+0.2%**, c-clang **+1.5%** vs unsafe. The engineer got +30.5 / +1.3 / −0.8 on cpu 3. The
  conclusion (`Ir` converts to time here) holds; the *single decimal* does not.

---

## Findings, by severity

No blockers. The measurements are sound; the framing is where the defects are.

**MAJOR 1 — `patterns/p05-index-flatten/NOTES.md:14`, `.memory/01-ladder.md:439-442`:
"the wider the lane, the cheaper safety gets" is refuted by measurement.** At AVX2 the
safe/unsafe gap at `ncol ≡ 0 (mod 32)` is **14601 Ir/call against SSE2's 4487**, and safe
Rust is *absolutely slower* than it was at SSE2 (18674 vs 15177). Failure scenario: a
numerical-computing reader — exactly the audience `TASK_013.md` names — reads this as
"compile with `-march=native` and the safety tax goes away", enables AVX-512, and lands on a
64-element forced scalar peel per row. Replace with: *per element the check is free at any
width; the residual is a per-row peel of VF elements, which grows with the lane.*

**MAJOR 2 — `.memory/01-ladder.md:453`, `NOTES.md:345`: 4.2500 is attributed to the check.**
Measured decomposition on p05, with a one-sided control (`-unroll-count=1`, bit-for-bit
no-op on R2, `md5_fn 76d7c2380278`): rolled+checked 7.0000, rolled+unchecked 5.0000,
novec-unrolled unchecked 2.7500 → **4.2500 = 2.0000 + 2.2500**, the same split
TASK_007_REVIEW derived on p16 and which finding 4 states as the transferable lesson ("a
safety tax must be attributed to a mechanism, never to a comparison"). Failure scenario: the
project publishes "the bounds check costs 4.25 Ir/byte" three patterns running while its own
memory file says it costs 2.00. `NOTES.md` §11's claim that no one-sided control is available
on p05 is also false and should be struck.

**MAJOR 3 — `NOTES.md:192`, `.memory/01-ladder.md:463`: the model is published without its
domain and is false for `ncol <= 8`.** Measured 34755 against a predicted 41699 at 496×8
(16.6% error). Both fitted bands start at `ncol = 24`, so the failure was unsampled. Add
`ncol >= 9` to the model statement.

**MAJOR 4 — `NOTES.md:13-14`, `.memory/01-ladder.md:440-442`: "the hypothesis is inverted" is
true in the swept range and false at `ncol = 8`.** R2's vector guard is `N >= 9`, R4's is
`ncol >= 8` — a direct consequence of the forced scalar epilogue, i.e. of the check — so at
`ncol = 8` the check *does* block vectorisation and costs **2.94×** (52648 vs 17893). This is
the result the pattern was commissioned to find, and it is one input file away. Recommend
shipping a third measured input at 496×8 rather than only reporting it.

**MAJOR 5 — `.memory/01-ladder.md:487`: "R3 is free for the sixth pattern in a row" flattens
an `O(nrow)` cost.** On p16 and p17 R3's cost was `O(1)` per call; on p05 it is `9 + 6·nrow`.
At 496×8 R3 is **+16.7%**, at 496×16 **+12.8%**, against +4.7% on the shipped `large`. "Free"
is a property of the shipped aspect ratio, not of the rung. The `Ir`-per-row row of the
headline table already says 6; the summary sentence does not inherit it.

**MINOR 1 — `NOTES.md:22`: the headline "Ir per element" row is a marginal derivative, not an
average.** Average Ir/element on `large` is 2.854 (R2) vs 2.124 (R4), a 34% gap; the table
prints `1.3750 / 1.3750 / 1.3750`. One word — "marginal" — fixes it. Same for finding 6's
"**The bounds check costs 0.0000 Ir per element.**"

**MINOR 2 — `NOTES.md:372`, `.memory/01-ladder.md:480`: "+30.5% time" is over-precise.** My
independent run gives +32.9% with comparable spreads. Quote +30–33%, or "+31% ±2".

**MINOR 3 — `NOTES.md:873-877`: `f(0) = 84` is listed as measured-not-explained.** It is now
explained exactly (Part 1.2): `29 + 64 − 11 + 2`, with `mov $0x8,%r11d ; cmove %r11,%r8` at
`safe_naive+0x157` as the instruction that does it.

**MINOR 4 — `NOTES.md:94`: the `u32` deviation's justification is weaker than the available
one.** It is provably semantics-preserving on every representable input (`65535·255 < 2^32`),
not merely plausible.

**MINOR 5 — `TASK_013.md:84-86` asked for it and `NOTES.md` does not report it: LLVM
strength-reduces `i*ncol` to a running pointer in R4/R5/c-clang** (`add %r9,%r11`) and cannot
in R2/R3, which recompute it with `imul` (twice per row in R2) because the bound test needs
the absolute index. The task said "that is a finding to report".

**MINOR 6 — a static instruction count of these kernels is off by one per row.** Two
alignment `nopw`s lie on the executed path in each of R2, R3 and R4. Any future hand-count
against callgrind needs them; dropping them gives `f(0) = 83`.

---

## Clean negatives — attacks that did not land

Named so nobody re-runs them.

1. **"`0.0000` is a subtraction of rounded numbers."** No. Kernel-exclusive Ir, integers,
   `2332 − 2332` on four consecutive lag pairs at a new `nrow`.
2. **"The denominator was chosen to make 11/8 come out."** No. At fixed `nrow` the lag pair's
   `Δelements = nrow·Δncol` exactly; header bytes and Horner steps are constant across the
   pair; and 11/8 and 17/16 are read straight off the two vector bodies.
3. **"The five rungs' mnemonics are not really identical."** They are — same 11 instructions
   in the same order in c-clang, safe_naive, safe_tuned, unsafe and verus.
4. **"The `Ir` table is stale / not reproducible."** All 16 shipped cell/input figures
   reproduce exactly on binaries I rebuilt from source, with identical checksums.
5. **"R5 drifted from R4."** `md5_fn` and `md5_raw` both equal.
6. **"The 4.2500 is a coincidence of the shipped shape."** Reproduced exactly at
   `nrow = 53`: 7.0000 / 2.3750 / 2.7500 / 2.3750 / 5.0000 for R2/R3/R4/c-clang/c-gcc.
7. **"The 19/32 count is inflated by the `whole`-mode artefact again."** It is not; the
   3 `O0 whole` hits are printed, are 2 instructions each, and are excluded from the headline.
8. **"The `u64` claim was asserted, not measured."** It measures; I reproduced it including
   gcc's `xmm=39` and both `-Rpass` remarks.
9. **"Verus doesn't actually verify / the TCB tally is short."** 12 verified, 0 errors;
   3 items, 6 lines, recounted.
10. **"The model is a 16-parameter overfit."** The opposite — it is a zero-parameter
    consequence of the codegen.

---

## Not done / unsure

- **I did not run `harness/check.py p05`.** Part 4 said to skip what the gate certifies, and
  a gate run writes into `results/gate/`. Consequently I did not re-verify Miri, the mutant
  gate transcripts (§10), the driver-loop token pins, or `model.py`'s self-check.
- **I did not re-run the mutants** (M0–M3). I did re-run plain Verus (12 verified).
- **The AVX2 and `-unroll-count=1` experiments are off this project's flags**, deliberately,
  as controls. They are not proposals to change `harness/build.py`.
- **The "requires scalar epilogue" attribution is my reading of LLVM policy**; what is
  *measured* is the `cmove` that forces the remainder to 8 and the `N >= 9` guard. The
  arithmetic consequences do not depend on the naming.
- **Wall clock was re-run on cpu 5 only, 21 reps**, not the engineer's 31 on cpu 3. No cycles
  figure is quoted anywhere in this report.
- `results/gate/p05-index-flatten.partial.json` is a leftover **mutant** (M3) record in the
  results tree. It is gitignored, so it is not a commit hazard — noted only so it is not
  mistaken later for a real p05 run.
