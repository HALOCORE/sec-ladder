# p13 — `strncpy` truncation: what was measured

Numbers here were produced by `harness/check.py p13`, `harness/measure.py p13`
and the scripts under `controls/`. Where a number is not reproducible from the
committed tree, that is a defect; say so.

⚠ **EVERY PERFORMANCE NUMBER IN THIS FILE MOVED AT TASK_046**, because the fold
did. p13 shipped a two-term fold (`d` and `dst[0]`) at TASK_043's instruction,
against `.memory/02-bench-rules.md`, which has required the **full-extent** fold
since TASK_004_REVIEW. §1c has the repair, its cost and the two worries that
turned out to be unfounded. Do not compare a figure here with the same figure in
a pre-TASK_046 commit; compare the *differences*, which mostly survive.

---

## 0. PHASE 0 — the two things settled BEFORE five rungs were built on them

TASK_043 named two calls it was least sure of and asked for the measurement
first. Both were probed with `.temp/p13/phase0/probe.c` + `run.py`: one
translation unit, two `noinline` kernels differing in exactly the one line, the
window built in-process, `DST_CAP = 32`. `d` is recovered by **inverting the
checksum** (`acc == (d*31 + dst0)*31 + 1` at `nstr == 1`), so the consumer loop
is never instrumented and neither codegen nor frame layout is perturbed.

⚠ **The probe predates the full-extent fold and is not re-run**; it is a
two-kernel translation unit, not a rung, and its whole purpose was to price one
store before any rung existed. §4a re-measures the same quantity **on the
shipped cells under the shipped fold** and gets the identical 1.00000 Ir per
string, which is the number to quote.

⚠ **The first run of the probe was wrong and self-caught**: gcc reported
**6.28 Ir/call** for 64 strings. `__attribute__((noinline))` does **not** stop
gcc treating a pure call as loop-invariant and CSE-ing it out of the repetition
loop. Fixed with `__asm__ volatile("" : "+r"(w) :: "memory")` inside the probe's
own loop — identical in both modes, so the delta the probe exists for is
unaffected. The shipped driver defeats the same thing with a real data
dependence (`k` comes from `acc`), which is why `spec.md` says the loop cannot
evaporate. **`noinline` is not a barrier.**

### 0a. Is `dst[DST_CAP - 1] = 0` measurable at all? **Yes. +1 instruction, 1.00 Ir per string.**

Static, `body_len` from objdump, on the probe:

| build | `kernel_r1` | `kernel_r1h` | `body_len` delta | mnemonic delta |
|---|---:|---:|---:|---|
| gcc -O0 | 161 | 162 | +1 | `movb` +1 |
| gcc -O3 | 180 | 180 | **+0** | `movb` +1, `nop`/`cs` −1, `nopl` +1 |
| clang -O0 | 140 | 141 | +1 | `movb` +1, `data16` −1, `nopl` +1 |
| clang -O3 | 95 | 96 | +1 | `movb` +1, `data16` +1, `xchg` −1 |

gcc -O3's `+0` is **alignment padding rearranged, not the store elided**: the
`movb` is there and a multi-byte `nop` shrank to compensate. Read the histogram,
never `body_len` alone. On the **shipped** cells the same figure is `+1` static
instruction on both compilers (`c-gcc` 180 → `c-gcc-h` 181, `c-clang` 250 →
`c-clang-h` 251) — see §4.

So the manager's worry does not hold: **p13 does have a safety-tax axis**, and it
is this project's first that is a *store* rather than a compare-and-branch.

### 0b. Does C's runaway consumer leave the frame, and is it stable? **Yes, and stability is PER BINARY.**

R1, one string of `slen = 40` (no NUL anywhere in `dst`), 200 runs of each build
of the probe:

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
quote the table above as a compiler property.** §7 has the shipped-cell
measurement, and at TASK_046 it moved again — on an edit that does not touch the
consumer at all. The honest general statement, which has now survived three
different trees:

> Whether R1's wrong answer is reproducible is a property of the **individual
> binary's frame layout**, not of the compiler, not of the optimisation level and
> not of the pattern. It cannot be predicted — only measured, per cell, per
> build of that cell.

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
  the program exits 0. Expected, and worth writing down: this is an overread of
  **initialised** stack bytes inside the same frame, so V-bit tracking has
  nothing to flag. `.memory/00-environment.md`'s memcheck entry answers *"is
  anybody reading memory nobody wrote?"* and **p13's bug is not that**. ASan's
  redzones are the only oracle here.

---

## 1. THREE CORRECTIONS TO THE TASK FILES, all measured

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
| `adversarial-exact` | 4 × 31 B | 0 | `8714310972305648768` | agrees, ASan clean |
| `adversarial-truncate` | the same 31 B **+ 1** | 1 | `8714310972305648768` | reads OOB |
| `adversarial-truncate-alt` | the same 31 B **+ 9** | 9 | `8714310972305648768` | reads OOB |

Three windows, three different amounts of destroyed data, **one checksum**. That
is the p17-shaped harm on its own: *a correct, proven, memory-safe program
cannot tell them apart.* And `exact` is sanitizer-clean where the other two fire,
so the same triple attributes the second harm to the rung that has it.

The three blobs share **one draw** of the four 31-byte heads, so they differ only
in the tails (p11's TASK_034 lesson).

**And the triple survives the full-extent fold**, which was the worry that
produced the narrow one — see 1c.

### 1b. `large` cannot have "a different truncation ratio", and neither can `small`

`check.py` binds **every cell, R1 included**, to `model.py`'s checksum on every
non-`sweep-*` matrix input. By 1a, any truncating string puts R1 out of
agreement — and on some builds out of agreement *with itself between runs*
(§0b, §7). So `small` and `large` are both **0% truncating**; what differs
between them is the length distribution below `DST_CAP` (mean **7.00** against
**22.04**, straddling 16), the string count (13 against 24) and the working set
(14.8 KiB against 6.90 MiB). The truncation-ratio axis lives in `sweep-t*`, and
R1 is excluded from it — **by policy, not by impossibility; see §8a**.

This is p12's situation with a different mechanism: p12's obstruction is its
**fold**, p13's is that the harm is an out-of-bounds **read of memory outside the
program's control**.

### 1c. THE FOLD WAS TOO NARROW, and both reasons given for it were wrong

`.memory/02-bench-rules.md` has said *"keep the full-extent fold"* since
TASK_004_REVIEW. `TASK_043.md:106` specified `d` and `dst[0]` only and p13
shipped that. The attribution is the manager's, not the gate's, and it was
confirmed at TASK_045_REVIEW.

**What it cost, measured** (`controls/oracle_hole.py`): a rung that copies
`0xFF` into every destination slot but the first agreed with `model.py` on
**9 of 9** shipped inputs, so `check.py` stage 2 (checksum agreement) *and*
stage 5d (the `ensures` re-derived on sampled calls) both passed a rung that
copies the wrong bytes. Under the full-extent fold the same mutant is **caught
on 7 of 9**; the two that still agree are `adversarial-empty` (nothing is
copied) and `adversarial-stride3` (zero kernel calls), i.e. every row on which
the substitution changes a byte now fails.

**Both worries that produced the narrow fold are unfounded:**

- **The triple survives.** `exact` / `truncate` / `truncate-alt` still print one
  checksum (`8714310972305648768`), because `n = min(slen, DST_CAP)` caps the
  copy and `dst[DST_CAP - 1] = 0` overwrites the last slot, so `dst` is
  **byte-identical** across the three. The harm p13 models needs `dst` to be the
  same, not the fold to be weak.
- **No copy elision.** No C cell elides the copy or the fill in `whole` mode;
  `__memcpy_chk@plt` / `memcpy@plt` / `memset@plt` are all still present.

**What it costs in instructions**: the fold is `DST_CAP` extra byte reads and
`DST_CAP` extra Horner steps per string, unconditionally. On the Rust rungs that
is **+153.95 … +160.02 Ir per string** (5.00 Ir per folded byte); the kernel
roughly doubles (R3 1721.41 → 3762.70 whole-program, ×2.19; R4 1938.41 →
3939.70, ×2.03) and the fold becomes about **54% of the kernel**. That dilution
is real and it shrinks every percentage in this file. It is the price of an
oracle that can see the copy, and `.memory/02-bench-rules.md` has been asking
for it since TASK_004_REVIEW.

⚠ **One consequence worth flagging**: the oracle-hole result used to read *"R5's
`ensures` discriminates a copy error that the entire checksum apparatus cannot"*
— **that is no longer true on this mutant** (§6a). The proof is still strictly
stronger in general; it is no longer *demonstrated* to be, here.

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

**The full-extent fold added no trusted item.** It reads `dst` through the
accessor that already existed (`dst_get_unchecked`), under a loop bound
`fi < DST_CAP`, which is p03's easy shape. TCB is 5 before and after.

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
conjunct `i < v@.len()` takes the twin configuration from 22 verified / 0 errors
to 21 / 1.
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
from 22/0 to 21/1, which is the gate's own measurement of that.
(b) The `ensures` is complete: the body reads `v` at `i` and does nothing else.
**What makes this item different from item 1 is not its contract, it is its call
site.** It has two kinds of call site now and only one of them is hard. The easy
one is the FULL-EXTENT FOLD, `while fi < DST_CAP`, where the loop bound
discharges the `requires` in the same basic block. The hard one is the consumer
loop `while dst_get_unchecked(&dst, d) != 0 { d = d + 1; }`, which has **no
bound at all**, and there the `requires` is discharged from a fact about the
array's *contents* — `dst@[DST_CAP - 1] == 0`. That is the two-site obligation
this pattern exists for, and the `ensures` is what makes it work: without
`r == v@[i as int]` the loop body could not learn `dst@[d] != 0` from the
condition, and `d != DST_CAP - 1` — the step that re-establishes `d < DST_CAP` —
would not follow. **The two sites share one item and one contract, and that the
same clause is trivial at one and load-bearing at the other is the clearest
statement of what p13 is about.**
(c) Each clause means the same in both configurations. `v@.len()` for a
`&[u8; 32]` is 32 in both by `array_len_matches_n`; the second conjunct that
would say so is deliberately **not** written, because it is a tautology from the
parameter type and p03's gate run refused exactly that draft.

SLB-TRUSTED-ARGUMENT verus.rs dst_set_unchecked

(a) The twin's body is `v[i] = x` against the trusted
`*v.get_unchecked_mut(i) = x`. The checked indexed store is the exact stand-in:
same slot, same value, bounds-checked. Deleting `i < old(v)@.len()` takes the
twin configuration from 22/0 to 21/1.
(b) The `ensures` is complete with respect to every unchecked operation the body
performs, and the whole-sequence form is what makes it so:
`final(v)@ == old(v)@.update(i as int, x)` says both *slot `i` became `x`* and
*nothing else moved*. A per-slot `ensures` would be satisfied by a body that also
wrote `i + 1`, which is TASK_009_REVIEW's x4 and is invisible to the contract
pin, to the twin and to the `--cfg slb_twin` run alike. **On p13 the second half
is load-bearing in a way it is not on p12**: this one item performs the copy, the
zero-fill *and* the termination store, so the sentinel the consumer relies on is
a byte written by an earlier call to this item and required to still be there
after `DST_CAP - n` later calls to it. Only "nothing else moved" carries that —
**and since TASK_046 it carries more**, because the full-extent fold reads every
slot back and the `ensures` of the walk now constrains all 32 of them.
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

`controls/library_axis.py`, `nstr = 32`, one window, `Ir` marginal per
**string**. All six routines carry the termination store and therefore **print
the same checksum**, which is what makes every difference below a library
difference with both routines named (`.memory/01-ladder.md` finding 9).

⚠ **THIS CONTROL KEEPS THE NARROW `d` + `dst[0]` FOLD THE RUNGS DROPPED AT
TASK_046, deliberately, and its levels are therefore NOT comparable with §4's.**
`strlcpy` and `snprintf` do not zero-fill, so `dst[n+1 .. DST_CAP]` holds
whatever the previous string left there; a full-extent fold would make the six
routines print six different checksums for a reason that has nothing to do with
cost, and the matched comparison would be gone. Every **difference** inside the
tables below is unaffected, because the fold term is identical in all six
columns and cancels.

| `DST_CAP` | `slen` | hand | handnofill | memcpy | `strncpy` | `strlcpy` | `snprintf` |
|---|---:|---:|---:|---:|---:|---:|---:|
| 32 | 1 | 114.98 | 81.92 | 79.92 | **91.92** | 122.92 | 434.07 |
| 32 | 8 | 155.02 | 126.96 | 124.96 | **126.96** | 152.96 | 466.12 |
| 32 | 31 | 274.00 | 261.94 | 259.94 | **235.94** | 266.94 | 579.09 |
| 32 | 64 | 425.00 | 423.94 | 421.94 | **400.94** | 447.94 | 839.09 |
| 256 | 8 | 166.05 | 118.02 | 115.02 | **135.96** | 152.96 | 466.12 |

(gcc -O3; `hand` is the rungs' copy/fill/consumer spelling, `handnofill` is the
same with the zero-fill deleted, `memcpy` is `handnofill` with the byte copy
replaced.)

### 3a. The safe routine is the expensive one — and it holds on BOTH compilers

At `DST_CAP = 32`, `slen = 8`, matched:

```
              gcc                            clang
strncpy   126.96 Ir/string               124.24     does NOT terminate at slen >= DST_CAP
strlcpy   152.96  (+26.00, +20.5%)       154.24  (+30.00)   always terminates
snprintf  466.12  (+339.16, +267%)       467.24  (+343.00)  always terminates
```

**The routine that is unsafe-by-surprise is the cheapest of the three, on both
compilers.** `strlcpy` is dearer than `strncpy` despite doing *no* zero-fill
because glibc implements it as `strlen` + `memcpy` — two passes over the source
where `strncpy` makes one.

### 3b. The zero-fill's own cost, exactly isolated — and it is COMPILER-SPECIFIC

`k_hand − k_handnofill`, same source, same `slen`, same everything else:

| cc | `DST_CAP` | L=1 | L=4 | L=8 | L=16 | L=24 | L=31 | L=32 | L=64 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| gcc | 32 | +33.06 | +33.06 | +28.06 | +23.06 | +15.06 | +12.06 | +1.06 | +1.06 |
| gcc | 256 | +49.03 | +49.03 | +48.03 | +47.03 | +46.03 | +46.03 | +45.03 | +41.03 |
| **clang** | 32 | **+17.00** | **+17.00** | **+17.00** | **+17.00** | **+19.00** | **+23.00** | +0.00 | +0.00 |

⚠ **The sentence this file used to carry here — *"the shorter the string, the
more the copy costs"* — is GCC-ONLY and is withdrawn as a general claim.** gcc's
zero-fill cost falls monotonically from +33.06 to +1.06 as the source grows;
clang's is **flat at +17.000 for L1…L16 and then RISES** (+19.000 at L24,
+23.000 at L31) before collapsing to 0 at L32 where the fill disappears. Two
compilers, two shapes, one routine. What survives on both is only the
qualitative statement: **the padding is a real per-string term at short source
lengths and it vanishes at `slen >= DST_CAP`.**

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

`objdump` on the shipped cells (`bulk_calls` in `results/p13-strncpy-trunc.json`,
`-O3`, isolated):

| cell | bulk/library calls in the kernel at -O3 |
|---|---|
| `c-gcc`, `c-gcc-h` | `strlen@plt` |
| `c-clang`, `c-clang-h` | `memcpy@plt`, `memset@plt`, `strlen@plt` |
| `safe_naive` | `memset@GLIBC_2.2.5` |
| `safe_tuned`, `unsafe`, `verus` | `memcpy@GLIBC_2.14`, `memset@GLIBC_2.2.5` |

⚠ **`strlen(` is in `spec.md`'s `idiom.forbidden`, no C source contains it, the
gate's own audit reports 0 forbidden hits, and every C `-O3` cell calls it
anyway.** Both compilers recognise `d = 0; while (dst[d] != 0) d++;` and emit
`strlen`. **A text-level idiom pin binds the SOURCE, not the OBJECT.**

**Blast radius, audited across all thirteen patterns' built `-O3` objects**
(`.temp/p46/objaudit.py`): only p12 and p13 forbid a C library routine at all,
and **p13 is the only one where the optimiser puts one back** — `strlen` in
**8 of p13's 16** `-O3` objects (the eight C cells), **0 of p12's 16**, and no
other pattern forbids a routine. ⚠ **The audit must be scoped to the kernel and
the driver**: unscoped it also counts `std::env`, `std::sys::fs::canonicalize`,
the backtrace machinery and `io::Error`'s `Display`, all of which call `strlen`
in *every* Rust binary of *every* pattern, and it then reports p12 as a hit,
which it is not.

**This is why §4 reports the C column separately and names the routine beside
every C rate.** §4d prices it.

---

## 4. THE LADDER

`-O3`, `isolated`, kernel-symbol **exclusive** `Ir` from callgrind, and
**beside it the whole-program marginal (`marginal_ir_per_call` from the gate
record)**, because the two columns answer different questions here — §4b.

| rung | cell | static (nopad) | kernel `Ir`/call small | large | **total** small | **total** large | libc called from the kernel |
|---|---|---:|---:|---:|---:|---:|---|
| R1 | `c-gcc` | 180 | 5048.00 | 11135.00 | 5270.28 | 11534.72 | `strlen` |
| R1h | `c-gcc-h` | 181 | 5061.00 | 11159.00 | 5283.28 | 11558.72 | `strlen` |
| R1 | `c-clang` | 250 | 3279.00 | 8195.00 | 3807.28 | 9133.72 | `strlen`+`memcpy`+`memset` |
| R1h | `c-clang-h` | 251 | 3292.00 | 8219.00 | 3820.28 | 9157.72 | `strlen`+`memcpy`+`memset` |
| R2 | `safe_naive` | 456 | 4791.00 | 13178.00 | 4947.70 | 13516.30 | `memset` |
| R3 | `safe_tuned` | 383 | 3416.00 | 9163.00 | 3762.70 | 9765.30 | `memcpy`+`memset` |
| R4 | `unsafe` | 248 | 3593.00 | 10217.00 | 3939.70 | 10819.30 | `memcpy`+`memset` |
| R5 | `verus` | 248 | **3593.00** | **10217.00** | 3938.70 | 10818.30 | `memcpy`+`memset` |

`small` walks 13 strings per call, `large` 24.

### 4a. THE SAFETY TAX — `R1h − R1` is EXACTLY 1.00000 Ir PER STRING

```
small.bin  gcc   5061.00 - 5048.00 = +13.00 Ir/call = 13 strings x 1.00000
small.bin  clang 3292.00 - 3279.00 = +13.00 Ir/call = 13 strings x 1.00000
large.bin  gcc  11159.00 - 11135.00 = +24.00 Ir/call = 24 strings x 1.00000
large.bin  clang  8219.00 -  8195.00 = +24.00 Ir/call = 24 strings x 1.00000
```

**Unmoved by the fold**, which is the check that it really is the store: the
fold adds the same 32 reads to R1 and R1h alike and cancels exactly.

Across the sweep (`controls/sweep_fit.py`), on **55 further blobs**:

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
read off the kernel column, where both cells call the same libc routine.

Relative, and it shrank when the fold grew: **+0.26% (gcc, small), +0.22% (gcc,
large), +0.40% / +0.29% (clang)** on the kernel column. A tax that is a fixed
number of instructions per string gets cheaper as a *percentage* every time the
kernel does more work — which is a fact about percentages, not about safety, and
is why the per-string figure is the one this file leads with.

### 4b. ⚠ THE KERNEL-EXCLUSIVE COLUMN IS NOT COMPARABLE ACROSS p13's RUNGS

p13 is the first pattern in this project whose rungs dispatch **different work
into libc** (§3d's table), all of it outside the `kernel` symbol. The
kernel-exclusive column silently credits a rung for the work it moved out.
Measured libc marginals, per kernel call, identical in every rung that makes the
call:

```
memcpy@GLIBC_2.14   190.00 (small)   264.00 (large)
memset@GLIBC_2.2.5  143.00 (small)   324.00 (large)
glibc strlen        182.00 (small)   336.00 (large)   -- C cells only
```

Two published figures move, and both are restated here **with the column named**:

| figure | kernel column | totals |
|---|---:|---:|
| gcc − clang (R1, the "compiler gap") | **+1769.00** / **+2940.00** | **+1463.00** / **+2401.00** |
| **R2 − R4** (the matched-spelling safety tax) | **+1198.00 (+33.34%)** / **+2961.00 (+28.98%)** | **+1008.00 (+25.59%)** / **+2697.00 (+24.93%)** |

The `R2 − R4` discrepancy is **exactly 190.00 / 264.00** — the `memcpy`
marginal, to the instruction — because **R2 makes no `memcpy` call and R4 does**.
The kernel column overstates that tax by precisely one library call.

**The rule, now in `.memory/03-measurement.md`**: before quoting the kernel
column for a cross-rung difference, list every cell's `@plt`/`@GLIBC` calls and
check the lists are equal. Equal lists is the licence; it is one `objdump` per
cell.

The per-scanned-byte component of `R2 − R4` is unaffected by any of this,
because it is a slope and the library terms are constant in `L` above the
threshold (`controls/sweep_fit.py`, band L, `L = 33..48`, `K = 8`):

```
safe_naive  +72.007 Ir/call per unit L = 9.001 per source byte
unsafe      +48.007                    = 6.001
                                 diff  = +3.00000 Ir per SCANNED SOURCE BYTE
```

**+3.00 Ir per source byte is the bounds check on the scan, exactly**, against
`unsafe`'s 6.00 Ir/byte for the same loop unchecked — a 50% surcharge on that
loop. This is p13's counter-example to "safety is free": it is not amortised
away by a bigger input, because the check is per byte and so is the work.

### 4c. R3 IS CHEAPER THAN R4 — and the mechanism is the CONSUMER, not the copy

```
kernel column   safe_tuned 3416.00 - unsafe 3593.00  = -177.00 Ir/call  (-4.93%)
                safe_tuned 9163.00 - unsafe 10217.00 = -1054.00 Ir/call (-10.32%)
totals          3762.70 - 3939.70   = -177.00 (-4.49%)
                9765.30 - 10819.30  = -1054.00 (-9.74%)
```

(The two columns agree to the instruction here, because R3 and R4 call the same
two libc routines at the same cost — §4b's licence, satisfied.)

⚠ **THE MECHANISM THIS FILE USED TO NAME IS WRONG AND IS WITHDRAWN.** It said the
gap was *"R3 spells the copy `copy_from_slice` → `memcpy` and the fill `fill(0)`
→ `memset`, while R4 spells them as unchecked byte loops"*. **R4 makes the same
two library calls at the same cost**: LLVM's loop-idiom recognition turns R4's
"unchecked byte loops" into `memcpy@GLIBC_2.14` and `memset@GLIBC_2.2.5`, and
the per-call libc marginals are **identical** across R3, R4, a bulk-spelled R4
and both consumer controls (§4b's table; `.temp/p46/mech.py`).

The gap decomposes, at matched checksum on every step
(`.temp/p46/mech.py`, whole-program marginal):

```
R4ship  -> R4bulk   copy and fill respelled bulk on the UNSAFE side   -92 /  -169
R4bulk  -> U_pos    the CONSUMER respelled position()                -129 /  -962
U_pos   -> R3ship   copy and fill back to the SAFE bulk spellings     +44 /   +77
                                                            total    -177 / -1054
```

**The CONSUMER is 73% (small) and 91% (large) of the headline**, and its
direction is the reverse of the one this file used to publish:

> **A bound the optimiser can SEE is worth 2.00000 Ir per consumed destination
> byte, exactly.** A consumer whose trip count is bounded by 32 is fully
> unrolled into a `cmpb`/`je` chain; R4's unbounded unchecked walk stays a
> scalar loop. Measured on band L (`K = 8`, `L = 20..28`) between two cells that
> differ in **nothing** but the consumer: `R4bulk − U_pos = +16.000` Ir/call per
> unit `L` = **+2.00000 per consumed byte**. Static histogram of the whole
> kernel: R3ship, U_pos and S_walk carry **30 `cmpb` / 33 `je`** and **2**
> backward branches; R4ship and R4bulk carry **2 `cmpb`** and **3–5** backward
> branches. (Both also unroll the full-extent fold, which uses `movzbl` and
> contributes no `cmpb`, so the 30 are the consumer.)

**And the discriminator is the BOUND, not the check and not the iterator.**
Three different bounded consumers all land on the same slope, to five decimals:

```
                                              slope, band L    Ir/call, small
R3ship   position(...).unwrap_or(DST_CAP)      +65.962          3762.70
S_walk   R2's UNBOUNDED but CHECKED walk       +65.962          3762.70
U_pos    R4bulk + position()                   +65.962          3718.70
u5       R4bulk + `while d < DST_CAP && ...`   (= U_pos)        3718.70
R4ship   unbounded UNCHECKED walk              +81.962          3939.70
R4bulk   unbounded UNCHECKED walk              +81.962          3847.70
```

`S_walk` is R3 with the consumer respelled as R2's **unbounded, bounds-checked**
`while dst[d] != 0 { d += 1 }`: it costs exactly what `position()` costs, because
the bounds check itself tells LLVM `d < 32`. `u5` is R4bulk with an **unchecked
but explicitly bounded** scan: it costs exactly what `position()` costs too, at
no check. So the check is *one way* of handing LLVM the bound and not the only
one, and it is the bound that is worth the 2.00 Ir/byte.

**This is p03's and p04's seeding result arriving from the other direction.**
There an invariant had to be *handed* to LLVM as dead code before it would
specialise; here the safety check **is** the seeding mechanism, and it more than
pays for itself. Fourth pattern in that family, and the first where safety is
net-negative *because* it is a check.

⚠ `md5_fn(R3ship) == md5_fn(S_walk)` was **byte-identical** under the narrow
fold. Under the full-extent fold it is not: 389 instructions and 1571 bytes in
both, **identical mnemonic multisets**, identical `Ir` on both inputs and
identical band-L slope, but the unrolled fold's `%rax`/`%rcx` rotation is one
step out of phase, so the bytes differ. The claim the result needs is exact `Ir`
equality and that holds; the stronger byte-identity claim does not survive the
fold and is not made.

### 4d. C's WHOLE advantage over Rust is one library call, and it is clang-only to price

Every C `-O3` cell calls glibc `strlen` for a consumer nobody wrote as `strlen`
(§3d). Priced with clang `-fno-builtin-strlen` — one flag, nothing else changed
(`.temp/p46/nostrlen.py`, totals, `-O3` isolated):

```
c-clang-h  base        3820.28 /  9157.72
c-clang-h  no strlen   3976.28 / 10889.72     => glibc strlen is worth 156.00 / 1732.00

vs R4 unsafe   (3939.70 / 10819.30):   C is -119.42 / -1661.58  WITH strlen
                                       C is  +36.58 /   +70.42  WITHOUT it
vs R3 safe_tuned (3762.70 / 9765.30):  C is  +57.58 /  -607.58  WITH
                                       C is +213.58 / +1124.42  WITHOUT
```

**The sign of every same-backend C-vs-Rust row flips.** clang 22.1.6 is rustc
1.97.1's LLVM, so this is a genuine same-backend comparison and what it says is
that p13's C-vs-Rust rows are a **library** comparison, not a language one.

glibc `strlen`'s own rate, fitted on the two inputs (`K` strings, `D` consumed
destination bytes; small `K = 13, D = 91`, large `K = 24, D = 529`):

```
182.00 = 13a + 91b ;  336.00 = 24a + 529b   =>   a = 14.00,  b = 0.00000
```

**14.00 Ir per call and 0.00000 Ir per byte** — one AVX2 vector covers all 32
destination bytes, so p11's 0.0788 Ir/byte in its limiting form. `.memory` finding
9's rule (name the routine beside the rate) applied.

⚠ **The price is CLANG-ONLY.** gcc ignores `-fno-builtin-strlen` — the flag
changes nothing at all (5283.28 / 11558.72 with and without) and gcc still emits
`strlen@plt`. The gcc knob was not found. **Do not generalise the number to
gcc**; what *is* true on gcc is only the qualitative half, that its C rungs also
call a `strlen` no source contains.

### 4e. R4 ≡ R5 — zero in the kernel, −1.00 in `main`

Kernel-exclusive `Ir` is **identical to the instruction**: 3593.00 both on small,
10217.00 both on large, `md5_fn a73b16fc01ea` both at `-O3`. The whole-program
marginal differs by exactly **−1.00 Ir/call**, and it is attributable: `main`'s
exclusive `Ir` is 780,274 (verus) against 840,275 (unsafe) on small, i.e. 60,001
fewer over 60,000 calls. **The proof costs zero in the kernel; the one
instruction is outside it**, in a `main` that reaches the file through a trusted
wrapper instead of inline. The `identity` pin covers the kernel symbol and is
`exact`.

### 4f. Wall clock — and it SURVIVES

**Raw levels, identical-copy protocol** (`common/layout/order.py --pattern
p13-strncpy-trunc --input small --copies 15 --reps 15 --orders alt,gen --cpu 3`;
15 byte-identical copies at one fixed layout, four passes). Frequency scaling is
on and cannot be disabled without root.

```
identical-copy NOISE FLOOR   0.54% .. 2.91%   (per cell, per pass)
R2 vs R4   +7.45% .. +7.61%   (medians over four passes)
R3 vs R4   -4.83% .. -5.18%   (medians over four passes)
gen agrees with alt on both, so the shipped scheduler is alternating
```

Both effects are **1.7× to 14× the floor**, so p13's wall-clock rows are not
withdrawn. `R3 − R4` is the striking one: **−4.9% `ns` against −4.93% `Ir`** on
the kernel column — the two agree to a tenth of a point, which is unusual on this
box and is what a genuine instruction-count effect looks like when nothing else
moves.

⚠ **The two ratios above are RAW-COLUMN ratios and `.memory/03-measurement.md`
RULE 1 forbids quoting them as ratios** — an earlier version of this section
quoted them and cited **rule 2**, which is about the ±9-point bar the
*correction* carries, not about the raw column. Corrected here
(`.temp/p46/wall.py`; 31 interleaved reps, `taskset -c 3`, `small.bin`, min,
`t(n_iters)` at 1 / 30000 / 60000):

| pair | raw % | `t(1)`-corrected % | slope % |
|---|---:|---:|---:|
| `verus − unsafe` (**NULL**, byte-identical kernels) | −0.24 | −0.51 | −0.51 |
| `safe_naive − unsafe` | +7.34 | **+7.64** | +7.64 |
| `safe_tuned − unsafe` | −4.98 | **−5.39** | −5.39 |
| `c-gcc-h − c-gcc` (the termination store) | −0.41 | −0.33 | −0.33 |

Correcting makes both effects **larger**, so the conclusion is unaffected — but
note the corrected column carries `.memory`'s **±9-point** bar, which +7.64 and
−5.39 do **not** clear. The quotable wall-clock evidence for p13 is therefore the
raw *level* with the identical-copy protocol, not the corrected ratio; the
corrected ratios are given because rule 1 asks for them and because they move in
the right direction.

⚠ **The termination store's `ns` cost is not resolvable.** The store's raw ratio
(−0.41%) is smaller than the byte-identical null pair's (−0.24% raw, −0.51%
corrected). Only `Ir` resolves 1.00 per string.

---

## 5. THE PROOF — one clause, SIX loops, and a two-site obligation

`./verus_run.py patterns/p13-strncpy-trunc/verus.rs` → **19 verified, 0 errors**,
first attempt (both before and after the fold repair). `--cfg slb_twin` →
**22 verified, 0 errors**.

```
DST_CAP 1 + scan_end 1 + copy_into 1 + fill_zero 1 + scan_dst 1 + fold_dst 1
        + walk 1 + kernel 7 + main 5 = 19
```

each measured with `--verify-function <name> --verify-root`. `kernel`'s **7** is
the highest in the project — one body plus **six** loop bodies (the string walk,
the source scan, the copy, the zero-fill, the consumer and the full-extent fold)
against p12's 5, p11's 4, p07's 3 and p03's 2. No `by (nonlinear_arith)` anywhere
in the kernel: every multiplication in it is by a literal.

The sixth loop and the sixth recursive spec function (`fold_dst`) both arrived
with TASK_046's fold repair, at **zero TCB cost** and with no new proof
technique: `fold_dst`'s loop invariant is `fill_zero`'s shape with the sequence
held fixed and the accumulator moving.

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

**The fold loop is the control for that claim**, and it is in the same function
on the same array through the same trusted accessor: `while fi < DST_CAP`
discharges `i < v@.len()` from its own loop bound, in the same basic block, with
no invariant at all. Same item, same contract, two call sites, one of them
trivial and one of them the pattern.

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

### 6a. ⚠ THE ORACLE HOLE, MEASURED, AND THEN CLOSED

`controls/oracle_hole.py` substitutes `dst[i] = if i == 0 { buf[off + p + i] }
else { 0xFF }` into R2's copy loop — every copied byte but the first replaced by
a non-zero constant, so `d` is unchanged and only the *contents* differ.

**Under the narrow `d` + `dst[0]` fold TASK_043 specified:**

```
identical on 9/9 shipped inputs
==> harness/check.py stage 2 (checksum agreement) and stage 5d (the `ensures`
    re-derived on 128 sampled calls) both pass a rung that copies the wrong
    bytes into the destination.
```

**Under the full-extent fold shipped at TASK_046:**

```
caught on 7/9 shipped inputs; identical on 2
  adversarial-empty     nothing is copied (every string is empty)   -- n/a
  adversarial-stride3   zero kernel calls                           -- n/a
==> every row on which the substitution changes a byte now FAILS stage 2.
```

**The hole was caused by the fold, not by the gate**, and closing it cost the
instructions §1c prices and nothing else. What `check.py` does is unchanged.

**What this costs the file, stated rather than quietly dropped**: the sharper
half of the old result — *"R5's `ensures` discriminates a copy error that the
entire checksum apparatus cannot"* — **no longer holds on this mutant**, because
the checksum apparatus now discriminates it too. Verus still refuses the
substitution (**18 verified, 1 errors**, `invariant not satisfied at end of loop
body`), so the proof is not weaker; it is simply no longer *strictly stronger
than the oracle* on the one demonstration p13 had. A pattern that wants that
demonstration needs a mutant the full-extent fold cannot see, and p13 no longer
has one.

---

## 7. THE ADVERSARIAL TABLE — per rung, and the two harms in separate columns

Every adversarial row is exactly one window (`n_blob == stride`), so R1's
overread happens on every call deterministically. Columns:
**TRUNC** = content silently discarded (memory-safe wrong answer);
**OOB** = out-of-bounds read of the frame.

| input | shape | TRUNC | OOB | checked rungs (R1h, R2–R5) | R1 `c-gcc` | R1 `c-clang` | ASan+UBSan |
|---|---|---|---|---|---|---|---|
| `adversarial-exact` | 4 × 31 B | no | no | `8714310972305648768` | agrees | agrees | clean |
| `adversarial-truncate` | 4 × 32 B | **1 B/string** | **yes** | `8714310972305648768` | wrong, 2 distinct values over the 4 builds | wrong, 3 distinct | **fires** |
| `adversarial-truncate-alt` | 4 × 40 B | **9 B/string** | **yes** | `8714310972305648768` | wrong, 2 distinct | wrong, 3 distinct | **fires** |
| `adversarial-nonul-dst` | 4 × 96 B | **65 B/string** | **yes** | `16725268236661028992` | wrong, 2 distinct | wrong, 3 distinct | **fires** |
| `adversarial-nonul-src` | 20,20,40 unterminated | **9 B** | **yes** | `11140422339664390272` | wrong, 2 distinct | wrong, 3 distinct | **fires** |
| `adversarial-empty` | 8 × 0 B | no | no | `227437609984` (= `nstr` folded) | agrees | agrees | clean |
| `adversarial-stride3` | stride 3 | — | — | `0`, zero kernel calls | agrees | agrees | clean |

**No specific wrong answer is quoted, deliberately: none of them is a number.**
The values differ between opt/mode variants of the same rung and between runs of
the same binary.

Read the first three rows together. **`exact`, `truncate` and `truncate-alt`
print the same checksum in every checked rung** while destroying 0, 1 and 9
bytes per string respectively — the memory-safe harm, isolated, and invisible to
a proven program. And `exact` is sanitizer-clean where the other two fire — the
memory-safety harm, attributed to the one rung that has it. **No single input
separates them, so the table does** (§1a). ⚠ **That is now true with a
FULL-EXTENT fold**, which is a stronger statement than the one this file used to
make: the three rows agree byte-for-byte in `dst`, not merely in two folded
scalars.

### 7a. ⚠ REPRODUCIBILITY IS A PROPERTY OF THE BINARY — and TASK_046 proved it again

60 and 300 runs of each single C binary on `adversarial-truncate.bin`
(`.temp/p46/repro.py`):

| cell | O0 isolated | O0 whole | O3 isolated | O3 whole |
|---|---|---|---|---|
| `c-gcc` (all four) | stable | stable | stable | stable |
| `c-clang`, **60 runs** | stable | **2 values** | stable | stable |
| `c-clang`, **300 runs** | **3 values (298/1/1)** | **2 values (170/130)** | stable | stable |

**Compare with the pre-TASK_046 tree**, where the same measurement gave
`c-clang` **2 values at O0-isolated, 2 at O0-whole, 2 at O3-isolated, stable at
O3-whole** (60 runs), and 3 / 2 / 2 / stable at 300. The fold repair **touches no
line of the consumer** and it still moved which builds are unstable — `O3
isolated` went from two values to stable.

Two consequences, and the second retires a sentence:

- **The general claim gets stronger.** Reproducibility is a property of the
  individual binary's frame layout; it is not predictable from the compiler, the
  optimisation level, the pattern, *or an unrelated edit elsewhere in the
  kernel*. Three trees now, three different tables.
- ⚠ **The sentence *"the COUNTS of distinct behaviours are what reproduce"* is
  FALSE and is withdrawn.** It is false twice over: the count is sample-size
  dependent (`c-clang` O0-isolated shows **1** distinct value in 60 runs and
  **3** in 300, the extra two appearing once each — a tail probability around
  0.7%), and the count of *unstable builds* moved from 3-of-4 to 2-of-4 on an
  edit that does not touch the consumer. **Quote the mechanism, never the
  counts.**

The gate's own per-row note — `opt/mode variants of this rung disagree (N
distinct behaviours)` — reports 2 for `c-gcc` and 3 for `c-clang` on all four
truncating rows, which is a comparison *across* builds and is stable.

**Nothing crashes.** Every R1 cell exits 0 on every row. p12's failure ladder
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

**The full-extent fold adds no regressor**: it reads exactly `DST_CAP` bytes per
string, i.e. `32 * K`, which is already a multiple of a column in the design.

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
to cross `DST_CAP` rather than stop below it), and — the structural one — **R1's
design is rank 3 of 5 as p13 runs it**, because among non-truncating rows
`C == S − K` exactly, so `C` and `T` are both unidentifiable for R1.

⚠ **The reason given for that used to be *"R1 cannot be run on a truncating blob
at all"*, and that OVER-CLAIMS.** It can:

```
kernel Ir/call, 3 reps each, sweep-l08L{36,40,44}.bin (all truncating)
  L=36  c-gcc 4207.0 x3    c-clang 3381.0 x3
  L=40  c-gcc 4367.0 x3    c-clang 3573.0 x3
  L=44  c-gcc 4527.0 x3    c-clang 3765.0 x3
```

Bit-identical on both compilers — `Ir` is a simulator count and does not depend
on what the overread reads. `sweep_fit.py:191` excludes R1 from `T > 0` blobs by
**policy**. The defensible argument, and the one that replaces it:

> On a truncating blob R1's consumer reads **1–7 bytes past `dst`** that are not
> a regressor of this design and not under the program's control. A law fitted
> there is a law with an unmodelled term in it, and its coefficients would be
> about the frame layout rather than about the kernel.

### 8b. The five-regressor law does not close — and SAY WHICH ESTIMATOR

Fitted on N+L, worst residual over the fit set, **both estimators reported**
because the verdict depended on which one and the file did not say:

| cell | exact interpolation | **OLS** | band T | **leave-one-length-out** |
|---|---:|---:|---:|---:|
| `c-gcc`, `c-clang` | — rank 3/5, NOT IDENTIFIED | — | — | — |
| `c-gcc-h` | 111.57 | 51.72 | 14.40 | **55.30** (L₀=25) |
| `c-clang-h` | 136.31 | 36.15 | 14.40 | **38.47** (L₀=2) |
| `safe_naive` | 873.21 | 443.24 | 4.80 | **454.83** (L₀=17) |
| `safe_tuned` | 149.27 | 35.36 | 4.80 | **37.63** (L₀=2) |
| `unsafe` / `verus` | 124.13 | 36.54 | 4.80 | **38.88** (L₀=2) |

`solve()` is **exact interpolation on the first 5 independent rows** — it fits
those 5 perfectly and reports the worst residual over all rows, which is right
when a law is expected to hold exactly and is an artefact of row order when it
does not. OLS answers *"how far off is the best linear model?"* and gives
**2.0× to 4.2× smaller** numbers. **No cell has an exact integer linear cost
model in these regressors under either estimator**, which is the result; but the
size of the failure is estimator-dependent by up to 4.2× and must be labelled.

⚠ **AND THE BAND-T TEST CANNOT FAIL, PROVABLY.** The fit set N+L has rank 5 in a
5-column design, so its row space is all of ℝ⁵ — checked directly by the control:
**17 of 17 band-T rows lie inside the fit set's row space**. No blob is out of
sample in regressor space, band T is an *interpolation* check, and its residuals
came out **smaller** than in-sample, which is what a test that cannot fail looks
like.

**What does work: hold out a LENGTH, not a MIXTURE.** Fit on `N + L \ {L₀}`,
predict `L₀` — `L₀` is a structural parameter the model is linear in and dropping
every blob at that length removes a point the fit has never seen. Worst
|residual| is the last column above: **2.7× to 8.1× band T's**, and on
`safe_naive` **95×**. That is the number that can falsify a law here, and it is
now a flag on the shipped control (`sweep_fit.py`, section *OUT OF SAMPLE*).
The general rule is in `.memory/03-measurement.md`.

### 8c. The step basis §8b used to NAME is DEGENERATE

The candidate this file named and did not build was `ceil(F/32)`. It cannot
work, and the reason is arithmetic rather than empirical: every fit blob is
**length-homogeneous**, so per string `ceil(f/32) == [f > 0] == K − T` and
`ceil(c/32) == [c > 0] == K`, both already columns of the design. Measured
(`sweep_fit.py`, section *STEP BASES*):

| cell | `B0` (5 col, OLS) | `+ceil32` (7 col) | `+pow2` (7 col) |
|---|---:|---:|---:|
| `c-gcc-h` | 51.72 | **SINGULAR** | 51.17 |
| `c-clang-h` | 36.15 | **SINGULAR** | 25.64 |
| `safe_naive` | 443.24 | **SINGULAR** | 438.22 |
| `safe_tuned` | 35.36 | **SINGULAR** | 26.28 |
| `unsafe` / `verus` | 36.54 | **SINGULAR** | 25.96 |

Every indicator basis collapses the same way for the same reason. The one
non-degenerate step basis — glibc's own size class, `ceil(log2)` — cuts the worst
residual by **~29%** (unsafe 36.54 → 25.96) and **does not close the law**. So
p13's design cannot identify a step basis at all, and a pattern that wants to
test one needs **length-heterogeneous** blobs, which p13's bands are not.

### 8d. What IS exact: the regime slopes on band L

`Ir` per call per unit `L`, `K = 8`, over `L = 33..48` (above the threshold,
where copy/fill/consumer are all saturated and only the **source scan** grows):

| cell | Ir/call per unit L | **Ir per source byte** |
|---|---:|---:|
| `c-gcc-h` | +40.048 | **5.006** |
| `c-clang-h` | +48.048 | **6.006** |
| `safe_naive` | +72.007 | **9.001** |
| `safe_tuned` | +48.007 | **6.001** |
| `unsafe` / `verus` | +48.007 | **6.001** |

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
noise, while the *slopes* above are clean because a per-call constant cancels in
a slope. TASK_026 §0 item 2, applied.

The **truncation cliff** at `L = 31 → 32`, where every string crosses `DST_CAP`
at once:

```
c-gcc-h   -73.44     c-clang-h  -121.44    safe_naive -136.60
safe_tuned +47.40    unsafe/verus -112.60
```

`safe_tuned` is the only cell that gets **more expensive** at the cliff — its
`copy_from_slice` widens to the full 32 bytes while the others lose a whole
`memset`.

---

## 9. PROOF MUTANTS — four, and WHICH LIMB CATCHES EACH

`controls/mutants.py`. Derived from the shipped `verus.rs` by exact-string
substitution with asserted hit counts, written to `.temp/p13/mutants/`
(`.memory/05-layout.md` item 11: a broken proof cannot live in the pattern dir).

Baseline: **19 verified / 0 errors** shipped, **22 / 0** under `--cfg slb_twin`,
and all three twin signatures identical to their trusted items'.

| mutant | shipped cfg | `--cfg slb_twin` | caught by |
|---|---|---|---|
| **M1** delete the TERMINATION STORE from the exec code | 18 verified, **1 error** — `invariant not satisfied before loop` | 21 / 1 | **Verus, in the shipped configuration** |
| **M2** weaken the trusted `dst_get_unchecked` `requires` to `i <= v@.len()` | **19 verified, 0 errors** | **22 / 0** | **`spec.md`'s `verus.items` pin (5a)** *and* **5c-twin LIMB (i)** |
| **M2b** the same weakening applied to the trusted item *and* its twin | 19 / 0 | 21, **1 error** — `precondition not met: index in bounds for this access` | **5c-twin LIMB (ii)** + the pin |
| **M3** delete the invariant `dst@[DST_CAP - 1] == 0` from the consumer loop, keeping the store | 18 verified, **1 error** — `assertion failed` | 21 / 1 | **Verus, in the shipped configuration** |

⚠ **M2's attribution used to read *"caught by `spec.md`'s `verus.items` pin
ALONE"*, and that UNDERSTATED THE GATE.** `.memory/04-verus.md`: **stage 5c-twin
has two limbs and a mutation report must say which one fired.** They are

- **limb (i)** — signature identity, `vparse.norm_clause(twin.sig)` against the
  trusted item's (`check.py:3374`);
- **limb (ii)** — the twin verifying under `--cfg slb_twin`.

Measured per mutant, on the shipped file and on each mutant:
`signature_identical` is `True` for all three items on the shipped file, `True`
on M2b — and **`False` for `dst_get_unchecked` on M2**, because M2 weakens the
item and leaves the twin alone. **M2 is caught twice**, and the control now
reproduces both limbs rather than stage 5a only.

**M1 is the pattern's own bug, in the rung that has a proof, and Verus refuses
it.** That is the relation an omitted line should have to a proof: not "the
postcondition is weaker" but "the memory-safety obligation is unprovable".

**M1 and M3 together separate the two sites.** M1 removes the fact at the
*write*; M3 leaves the write and removes the carrying of the fact into the
*read*. Each alone breaks the proof, which is what "two-site obligation" means
operationally.

**M2b shows what the twin regime is for**: once the two configurations are made
to agree, the verified twin fails on the off-by-one, in the configuration where
the shipped file verifies cleanly.

---

## 10. THE IN-CONTRACT SPAN, ON BOTH SIDES

`controls/spellings.py`. Every variant is derived from a shipped rung by
exact-string substitution with an asserted hit count, is audited against
`harness/check.py::spelling_matches` for **every** backticked entry of
`spec.md`'s `idiom` before its number is quoted, and prints the shipped checksum
on both inputs. All eleven do.

⚠ **UNTIL TASK_046 THIS SECTION SEARCHED ONE SIDE AND BLAMED THE PROVER FOR THE
OTHER, and both halves of that were wrong.** `spec.md` pinned the byte-loop copy
and fill in `safe_naive.rs`, `unsafe.rs` and `verus.rs` and exempted
`safe_tuned.rs` **by name**, while p13's headline is `R3 − R4`: **only the safe
side of the comparison was permitted the spelling the headline is about.** This
file then said *"the R4 side is not searched"* and attributed it to `identity:
exact` chaining R4 to the prover. **The prover does not bind here**, and §10b
measures which exclusions do.

### 10a. The R3 side

| variant | `small.bin` | `large.bin` | in contract |
|---|---:|---:|---|
| `v0_shipped` | **3762.70** | **9765.30** | yes |
| `v1_onestep_reslice` | 3763.70 | 9766.30 | yes |
| `v2_takewhile_consumer` | 3762.70 | 9765.30 | yes |
| `v4_fill_explicit_end` | 3762.70 | 9765.30 | yes |
| `v3_byteloop_copy` | 4404.70 | 11439.30 | yes |

### 10b. The R4 side, and the three reasons a spelling can be out

| variant | `small.bin` | `large.bin` | admissible | why |
|---|---:|---:|---|---|
| `u0_shipped` | 3939.70 | 10819.30 | yes | — |
| `u1_bulk_copyfill` | **3847.70** | **10650.30** | **yes** | `copy_nonoverlapping` + `write_bytes`; **17 verified / 0 errors, twin 24/0**, `identity: exact` holds; **TCB 5 → 7** |
| `u2_bulk_copy` | 3887.70 | 10723.30 | yes | copy only |
| `u3_bulk_fill` | 3926.70 | 10795.30 | yes | fill only |
| `u4_bounded_consumer` | 3810.70 | 9873.30 | **FIAT** | `while d < DST_CAP && ...`; **19 / 0, twin 22 / 0** — the *shipped* counts, no new trusted item |
| `u5_bulk_and_bounded` | 3718.70 | 9688.30 | **FIAT** | both of the above |
| *R3's own consumer* | — | — | **NO** | `position` **is not supported** at the pinned vstd |

`controls/gen_bulk_r5.py` builds each candidate's R5 twin and runs Verus on it,
so *"reachable by an R5"* is a run and not a citation. The three exclusion
mechanisms are genuinely different and only one of them is the prover:

1. **The prover.** `dst.iter().position(|&b| b == 0)` gives
   `` `core::slice::iter::impl&%171::position` is not supported (note: you may
   be able to add a Verus specification to this function with
   `assume_specification`) ``. Read the **error text, not the exit code**: `is
   not supported` disqualifies, because it forces a new trusted item. So R3's
   consumer spelling is unavailable to R4/R5 whatever `spec.md` says, and the
   consumer entry's rung scoping is **not** a thumb on the scale.
   ⚠ **A prior form of the closure `|&b| b == 0` fails one step earlier still**
   (*"only variables are supported here, not general patterns"*), which is a
   different limitation; the `is not supported` above is measured on `|b| *b ==
   0u8` so that the iterator method is what is being tested.
2. **The contract, until TASK_046.** `copy_nonoverlapping` and `write_bytes`
   are **not** `is not supported`; the bulk pair verifies with a clean twin and
   `identity: exact` holding. **Nothing but the idiom pin excluded it**, and the
   pin bound the unsafe side while freeing the safe one. **Relaxed
   symmetrically at TASK_046**: the copy and fill entries now backtick no Rust
   spelling at all, so the loop form is free on every Rust rung.
3. **Fiat.** A *bounded unchecked* consumer verifies at the shipped counts with
   no new trusted item, so neither the token audit nor the prover excludes it.
   What excludes it is the consumer entry's English and the pattern's subject:
   bounding the consumer turns p13's two-site obligation into a loop bound and
   stops R4/R5 being a matched spelling against R1's runaway scan. **That is a
   fiat and it is priced below rather than asserted to be free.**

### 10c. THE TWO BOUNDS, AND THE THIRD NUMBER THAT MUST BE PUBLISHED BESIDE THEM

`.memory/02-bench-rules.md`'s reporting corollary: never re-ship a rung; publish
the fixed-R4 bound **and** the cheapest-found bound.

```
small.bin   fixed-R4 bound     R3ship - R4ship            = -177.00 Ir/call (-4.49%)
            cheapest-found     R3ship - inf(in-contract)  =  -85.00 Ir/call (-2.21%)  [u1_bulk_copyfill]
            R3-side span       3762.70 .. 4404.70   width  642.00
            R4-side span       3847.70 .. 3939.70   width   92.00
large.bin   fixed-R4 bound                                = -1054.00 Ir/call (-9.74%)
            cheapest-found                                =  -885.00 Ir/call (-8.31%)  [u1_bulk_copyfill]
            R3-side span       9765.30 .. 11439.30  width 1674.00
            R4-side span      10650.30 .. 10819.30  width  169.00
```

**The idiom pin was worth 92.00 (small) and 169.00 (large) Ir/call**, i.e. **52%
of the small margin and 16% of the large one.** The sign survives; the magnitude
does not. This is the **direction test's first fire on this project**
(`.memory/01-ladder.md`), and the shape it caught — *an idiom entry whose scope
names some rungs and excludes others* — is new.

⚠ **AND THE SIGN DOES NOT SURVIVE THE FIAT.** The cheapest R4 anyone here has
built is `u5_bulk_and_bounded`, and against it:

```
R3ship - u5_bulk_and_bounded   =  +44.00 Ir/call (small)   +77.00 (large)
```

**Positive.** Give R4 the bound that R3's `position()` supplies for free and R3
is no longer the cheaper rung. So p13's headline is exactly this and nothing
more:

> **Under p13's contract**, in which the unsafe rung's consumer is unbounded
> because that unboundedness *is* the pattern, safe Rust is 2.2–8.3% cheaper
> than unsafe Rust. The margin is **not** a language result and **not** a safety
> result: it is the price of a bound, and it reverses by +44 / +77 Ir/call the
> moment the unsafe rung is allowed one.

`u5` is **not** an endpoint of any published interval — it is out of contract by
the consumer entry's English — but a reader who is not told its number cannot
tell a language result from a contract artefact, and on p13 it is the latter.

### 10d. `.memory/01-ladder.md` finding 3's two-step reslice reproduces here

`v1_onestep_reslice` respells only `buf.split_at(off).1.split_at(len).0` as
`&buf[off..off + len]` and is **+1.00 Ir/call on both inputs** — the same
`−1 Ir/call` lever finding 3 measured on p04, on a second pattern, at the same
magnitude, with the same two panic paths present in both, and **unmoved by the
fold**. p13 spelled it the cheap way from the start, so the lever costs p13
nothing and is measured rather than inherited.

---

## 11. GATE-ADJACENT: what `spelling_matches` does not blank

**Reported, not fixed — `harness/` was out of scope for TASK_046.**

`harness/check.py::spelling_matches` blanks comments, string literals and Verus
ghost clauses, and deletes whitespace. It does **not** blank
`#[cfg(slb_twin)]` bodies — and those are exec code that **no measured build
contains**, because the gate itself relies on `slb_twin` being unset everywhere
except stage 5c-twin. So a Verus rung's idiom audit can be satisfied by code
that ships in no binary.

Demonstrated rather than described (`.temp/p46/cfgaudit.py`): take the shipped
`verus.rs`, respell the consumer's pinned `d = d + 1;` as `d += 1;` in the exec
kernel, and put the pinned spelling inside `slb_twin_buf_get_unchecked`'s body:

```
exec-only respelling, no twin   : spelling_matches('d = d + 1;', ...) = False
same, with the twin carrying it : spelling_matches('d = d + 1;', ...) = True
```

**Blast radius on the shipped tree: zero.** Of the 15 backticked Rust spellings
`spec.md` pins, **0** match `verus.rs`'s twins alone. (Before TASK_046 relaxed
the copy and fill entries there was a live instance: a bulk-spelled R5 scored
16/17 by matching `while i < n` and `while j < DST_CAP` **in its twins** while
its exec code contained neither. Those two spellings are no longer pinned, so
that particular instance is gone — by accident, not by repair.)

Threat model is honest mistake (`.memory/02-bench-rules.md`), and blanking
`#[cfg]`-gated bodies is a one-line change to a matcher with a 20-case selftest,
so this is a **minor**: the fix belongs to whoever next has `harness/` in scope,
and the check to add beside it is *"the spelling occurs in code some measured
build compiles"*.
