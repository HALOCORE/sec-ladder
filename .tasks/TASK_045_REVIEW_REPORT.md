# TASK_045_REVIEW — report

p13 (`strncpy` truncation), reviewed against `.tasks/TASK_045_REVIEW.md`.
**Three blockers, six majors, three minors**, and a set of clean negatives that
close several attacks permanently. Scratch and generators: `.temp/r45/` (184 KB,
text only). The reviewer did **not** re-run `harness/check.py p13`; every number
below is a targeted re-measurement.

## BLOCKER 1 — the contract forbids the R4 side from the spelling the headline is about

`patterns/p13-strncpy-trunc/spec.md:374` and `:394` pin `while j < DST_CAP` and
`while i < n` in **`safe_naive.rs`, `unsafe.rs` and `verus.rs`**, exempting
`safe_tuned.rs` **by name** ("that is the measurement").

`NOTES.md:842` says the R4 side "is not searched" and attributes it to the
prover. **The prover does not bind.** The bulk-spelled pair was built and run:

```
./verus_run.py .temp/r45/bulk/verus_bulk.rs                -> 15 verified, 0 errors
./verus_run.py .temp/r45/bulk/verus_bulk.rs --cfg slb_twin -> 22 verified, 0 errors
md5_fn: R4bulk == R5bulk == c9bcab05fa82        (identity: exact holds)

cell        small.bin  large.bin   vs R4ship    vs R3ship
R3ship        1721.41    5997.30   -217/-1126     0/0
R4ship        1938.41    7123.30      0/0       +217/+1126
R4bulk        1833.41    6930.30   -105/-193    +112/+933
R5bulk        1832.41    6929.30   -106/-194    +111/+932
```

All six print the same checksum on both inputs. **`copy_nonoverlapping` and
`write_bytes` are NOT `is not supported` at the pinned vstd.** Cost: TCB 5 → 7.

**Failure scenario.** The published *"safe Rust beats unsafe by 13.6–17.3%"* is a
comparison in which **only the safe rung was permitted the winning spelling**.
With the pin relaxed symmetrically the figure is **−112.00 (−7.54%) / −933.00
(−14.74%)**: the sign survives, the magnitude does not — **48% (small) and 17%
(large) of the headline was the pin**, not the language.

## BLOCKER 2 — the named mechanism is wrong, and the true one is a better result

`NOTES.md:454-461` attributes the gap to R3's `copy_from_slice → memcpy` and
`fill(0) → memset` against R4's byte loops. **R4ship makes the same two library
calls at the same cost.** Every Rust rung — including "byte-loop" R4ship — calls
`memcpy@GLIBC_2.14` and `memset@GLIBC_2.2.5` from inside the kernel, with
**identical** libc marginals (190.00 + 143.00 on `small`, 324.00 + 264.00 on
`large`) across R3ship / R4ship / R4bulk / U_pos / S_walk.

```
R4ship -> R4bulk  bulk copy+fill on the unsafe side   -105 /  -193
R4bulk -> U_pos   consumer respelled position()       -156 / -1010
U_pos  -> R3ship  copy/fill back to the SAFE bulk      +44 /   +77
                                            total     -217 / -1126
```

**72% (small) and 90% (large) of the headline is the CONSUMER**, and its
direction is the reverse of the one published: **the bounds check tells LLVM
`d < 32`, LLVM fully unrolls to 32×(`cmpb`/`je`) = 2 Ir/byte, and the unchecked
unbounded walk stays a 4-instruction loop.** Band L, K=8, L=20..28, R4bulk vs
U_pos differing in *nothing* but the consumer: **+2.00000 Ir per consumed byte,
exactly.**

And the discriminator is the **check**, not the iterator:
`md5_fn(R3ship) == md5_fn(S_walk) == c936658a0e82` — respelling `position()` as
R2's unbounded *checked* `while dst[d] != 0 { d += 1 }` gives a **byte-identical
kernel**.

**Failure scenario.** A reader takes "bulk spellings beat byte loops" from p13
and applies it elsewhere. The real transferable result is **"a bound the
optimiser can see is worth more than the check costs"** — which p13 has, and does
not claim. (`spec.md:632` also cites `../NOTES.md 1` for the idiom-recognition
fact, which lives in §3d.)

## BLOCKER 3 — the kernel-exclusive column is not comparable across p13's rungs

The rungs dispatch **different work into libc**, all of it outside the `kernel`
symbol: c-gcc calls `strlen` only; c-clang calls `strlen` + `memcpy` + `memset`;
`safe_naive` calls `memset` only; R3/R4/R5 call `memcpy` + `memset`.

- `NOTES.md:387-390`: `c-clang 1264.00` vs `c-gcc 1758.00` reads as a **494**
  Ir/call compiler gap. On totals it is **188**.
- `NOTES.md:429-430`: `R2 − R4 = +1119.00 (+70.3%) / +2817.00 (+43.2%)`. On
  totals: **+929.00 (+47.9%) / +2553.00 (+35.8%)**. The matched-spelling safety
  tax is **overstated by 190 / 264 Ir/call**, because R2 makes no `memcpy` call
  and R4 does.

**p13 is the first pattern here whose rungs differ in *which* library calls they
make**, so this is a new comparability rule, not a p13 slip.

## MAJOR 4 — the `strlen` term IS the whole C advantage, and the pin scope is narrow

clang `-fno-builtin-strlen` (one flag; gcc ignores it):

```
clang-h base      1807.44 / 5437.72   vs R4 unsafe: C -130.97 / -1685.58
clang-h no strlen 1976.44 / 7193.72   ->            C  +38.03 /   +70.42
```

**The sign of every same-backend C-vs-Rust row flips.** glibc `strlen` fitted on
the two inputs: **14.00 Ir per call, 0.00000 Ir per byte**. Finding 9's rule —
name the routine beside the rate — is not applied to p13's C rows.

**Scope of the `forbidden`-pin limitation, audited over all 12 patterns'
objects**: **p13 is the only pattern whose `forbidden` list is reintroduced by
the optimiser.** p12's `strlen(` / `strcat(` / `strncat(` / `snprintf(` appear in
**no** `-O3` object, and the other ten patterns forbid no library routine. The
limitation is real and its blast radius is one pattern.

## MAJOR 5 — `NOTES.md:314-317` is gcc-only and false on clang

`library_axis.py --cc clang --caps 32`, zero-fill cost: L1..L16 flat at
**+17.000**, L24 +19.000, L31 **+23.000**, L32 +0.000 — flat, then *rising*.
gcc's is +33.06 → +1.06, monotone falling. ***"The shorter the string, the more
the copy costs"* does not survive the second compiler.**

## MAJOR 6 — the named step-basis candidate is degenerate, and "no law" is estimator-dependent

Per string `ceil(f/32) = [f>0] = K − T` and `ceil(c/32) = [c>0] = K`, so
`B_ceil32` is **SINGULAR**. Every fit blob is length-homogeneous, so all
indicator bases (`B_thresh`, `B_buckets`) are singular too. The one
non-degenerate step basis (glibc size class, `ceil(log2)`) cuts the worst
residual ~30% (unsafe 36.85 → 26.10) and does not close the law.

Separately: the published residuals (115.43 / 888.30) come from **exact
interpolation on 5 chosen rows**; **ordinary least squares on the same data gives
36.85 / 442.57**. The "no law" verdict is estimator-dependent by ~3×.

## MAJOR 7 — the out-of-sample test cannot fail, provably

Every band-T row `= (t/8)·row(L=40) + ((16−t)/8)·row(L=8) − (1,0,0,0,0)`,
verified for all 17 values of `t`; and `(1,0,0,0,0)` is itself a difference of
two band-N rows. The fit set is **rank 5 in a 5-column design**, so its row space
is all of ℝ⁵ — **no blob is out of sample in regressor space.**

**Hold out a LENGTH, not a MIXTURE.** Leave-one-length-out on band L (fit
N+L\{L₀}, predict L₀), worst |residual|:

```
c-gcc-h 56.08 | c-clang-h 39.31 | safe_naive 454.14 | safe_tuned 38.50 | unsafe 39.21
```

— **5× to 90× band T's 5.10 / 12.24.**

## MAJOR 8 — M2's catcher is mis-attributed, and the review task's premise was wrong

`check.py` 5c-twin compares `vparse.norm_clause(twin.sig)` against the trusted
item's. Measured: shipped `signature_identical = True`, **M2 `= False`**, M2b
`= True`. **M2 is caught twice**, not "by `spec.md`'s pin alone".
`controls/mutants.py:97` reproduces stage 5a only, so its verdict column
understates the gate. **The task file's premise — that p13's twin cannot see a
weakened `requires` — is refuted**: the twin regime has two limbs and M2 trips
the signature one.

## MAJOR 9 — the R1 impossibility argument over-claims

R1 *can* be measured on truncating blobs; kernel `Ir` is bit-identical over 3
reps at L=36/40/44 on both compilers (c-gcc 2182/2342/2502, c-clang
2133/2325/2517) **even where c-clang's checksum is unstable**.
`sweep_fit.py:191` excludes R1 from `T>0` **by policy**, not by impossibility.
The defensible argument, which should replace it: *on a truncating blob R1's
consumer reads 1–7 bytes that are not a regressor, so a law fitted there fits an
unmodelled term.*

## MINOR 10 — `NOTES.md:652` is falsified

*"The counts of distinct behaviours are what reproduce"*: c-clang-O0-isolated
gives **1** distinct value in 60 runs (delivery: 2, split 58/2) and **3** in 300
runs (296/2/2). The count is sample-size dependent (tail p ≈ 0.7%). The
3-of-4-unstable reading itself **does** reproduce at 300 runs.

## MINOR 11 — two wall-clock ratios quoted off the raw column

`.memory/03-measurement.md` rule 1 forbids it; `NOTES.md:504` cites rule 2, which
is about preferring the raw *level*. Correcting makes them **larger**
(+9.14 → +10.26, −7.30 → −8.84), so the conclusion is unaffected.

## MINOR 12 — `spelling_matches` does not blank `#[cfg(slb_twin)]` bodies

`verus_bulk.rs` scores 16/17 on the required list, matching `while i < n` and
`while j < DST_CAP` **in its twins**, while its exec code contains neither.
Honest-mistake threat model, so minor — but **the idiom audit on a Verus rung can
be satisfied by code no build contains.**

## Clean negatives — attacked, did not land

- **The full-extent fold does NOT break the exact/truncate/truncate-alt triple.**
  Under a full fold of `dst[0..DST_CAP]` it still prints one checksum
  (`8714310972305648768`), because `n = min(slen,32)` caps the copy and
  `dst[31]=0` overwrites the last slot. **§1 of the review task's stated worry is
  unfounded.** Cost: **+160.02 / +157.02 / +153.95 Ir per string** for R2/R3/R4 =
  5.00 Ir per folded byte (R3 ×2.19, R4 ×2.03); headline becomes
  **−177.00 / −1054.00**.
- **The manager's self-attribution on the narrow fold is correct.**
  `TASK_043.md:106` and its "Load-bearing" bullet do specify it.
- **No copy elision in `whole` mode on any C cell** — `__memcpy_chk@plt` /
  `memcpy@plt` / `memset@plt` all present in `main`. TASK_004_REVIEW's p02
  reasoning **does** extend to a fixed local array.
- **`NOTES.md:353-363`'s bulk/library call table reproduces exactly**, isolated
  and whole, all eight C/Rust cells.
- **The rank table reproduces exactly** (N 2/5, L 4/5, T 2/5, pooled 5/5, N+L
  5/5, R1-view 3/5). **Band L holds `K = 8` constant**, so the constant `8.00` is
  `K × 1.00` and identification comes from band N where `K` varies 1..24 — **not**
  a rank artefact.
- **The termination store**: `asm.py diff` shows exactly one `movb $0,(…)` added,
  straight-line, after the fill, in both compilers. **Not DSE'd because the
  fill's extent `DST_CAP − n` is a runtime value.** The review task's DSE
  prediction is **wrong**; the delivery's "per string" is right and now has its
  mechanism.
- **`strlcpy` dearer than `strncpy` survives on clang**: +30.00 (gcc +26.00);
  `snprintf` +343.00 (gcc +339.16). *"The unsafe routine is the cheapest"* holds
  on both compilers.
- **The anti-collapse floor** is cleared by 5–29× and is non-tautological (a
  constant-`Ir` kernel would fail), but is very weak — as `check.py:51` says of
  itself.
- **The direction test FIRES on p13**: the byte-loop copy/fill idiom entries move
  the headline by **105.00 / 193.00** Ir/call. (p04's moved by 0.00.)
- **Wall clock survives**: null pair `verus − unsafe` = −0.68% raw / −1.33%
  corrected / −1.82% slope; effects +10.96% and −9.59% clear it by 5–8×.

## Reviewer's "unsure / not done"

- **Did not run `harness/check.py p13`.** All numbers are targeted
  re-measurements; the gate's own record was not re-verified.
- The bulk R5's two new trusted items state their `ensures` in p13's own spec
  functions (`copy_into`, `fill_zero`) rather than p02's subrange form —
  legitimate, but **no `SLB-TRUSTED-ARGUMENT` was written** and `spec.md`'s
  item/obligation pins would all move (17→15, 20→22, TCB 5→7). **Admissibility
  was priced, not shipping.**
- `U_pos` and `S_walk` are controls, not rungs (`U_pos` is out of contract on the
  consumer entry).
- **gcc's `strlen` idiom is not gated on `-fno-builtin-strlen`**, so the §3 price
  is **clang-only**; the gcc knob was not found.
- `-fno-builtin` (all builtins) numbers exist in the notes but back no claim,
  because they also disable gcc's inlined copy/fill idiom.
- The reviewer's wall-clock session is not the delivery's; only raw ratios are
  comparable across sessions, and both are quoted.
