# TASK_040_REVIEW — report

Reviewer's return message, recorded by the manager. Scratch `.temp/r40/` (184 KB,
all text): `struct/gen_row.py`, `struct/gen_capfold.py`, `mech/gen.py`,
`routeA/gen.py`, `poison/gen.py`, `mkblob.py`, `ir.py`, **`pads.py`**, `wall.py`.

**Two blockers, three majors. The headline mechanism survives, sharpened.**
`--check-stale`: both p12 records **FRESH**, 0 STALE over 22.

## blocker 1 — the structural claim is TRUE for p12 and FALSE in the general form shipped

`README.md:45-47` and `NOTES.md:83-88` publish *"a row on which a write bug fires
cannot also be a checksum-agreeing row … structural for a WRITE bug, no analogue
in the read patterns."*

**The attack as the task posed it fails — clean negative.**
`.temp/r40/struct/fillreject.bin` (64 windows, four 32-byte strings then an
8-byte one, so the check fires once per window at exactly +8):

```
c-gcc      10531535382307180616  rc=0   <- silent, wrong
c-clang    10531535382307180616  rc=0   <- silent, wrong
all others 13744965160093837641  rc=0   == model.py
```

**But the forcing agent is the FOLD, not the write.** One edit — zero-initialise
`dst`, fold `dst[0..DST_CAP]` instead of `dst[0..dlen]`, drop `dlen` from the
result:

```
kernel_capfold    (capacity check DELETED)  9617137326358488304
kernel_capfold_h  (capacity check KEPT)     9617137326358488304   IDENTICAL
n_iters 1/2/4/100/200/1000: 12605653696781812108 / 11109895781008428530 /
  11511695593773783267 / 7572596882302193833 / 8993073921421418394 /
  8990243233740411127   (both cells, identical, and NOT constant -> usable)
```

and the bug still fires:

```
kernel_capfold.c:63:16: runtime error: index 128 out of bounds for type 'uint8_t [128]'
AddressSanitizer: stack-buffer-overflow   WRITE of size 1   #0 in kernel ...:63
```
(the checked twin is ASan-clean, exit 0.)

**The sentence that should govern p13/p14/p23/p24/p25 is the first half only:**

> *For a write bug whose guard IS the destination's own bound, every input on
> which the guard fires is an input on which the unguarded rung executes an
> out-of-bounds store.* Forced; no read analogue.
>
> *Whether such an input can also be a checksum-agreeing row is a **design
> choice**, not a constraint.* It depends on whether the checksum is a function of
> state the OOB store cannot reach. p12's is not — and TASK_040 itself mandated
> that fold.

**Price**: the perf row executes UB on every call, so it is usable only while the
overflow stays in the silent regime (≤ +8 B here). Such a pattern must pin the
overflow, assert the marginal is non-zero, and say in `spec.md` that R1 executes
UB by construction.

**Two scope corrections**: the gate's checksum requirement is `check.py:471-472`
over `check.py:1249-1278`, but `check.py:469` and `measure.py:64` drop `sweep-*`
entirely — so it binds the **matrix** inputs, not "every non-adversarial input".
And on band A, R1's exclusion is caused by the **crash**, not the checksum: its 29
usable points are exactly the 29 non-overflowing ones.

## blocker 2 — §4's mechanism is contradicted by the attribution it declined to do

`NOTES.md:360-366` reads "the pad count stays at 2 across three fold spellings" as
*the fold's check survives*, and concludes "p03's result transplants".
`NOTES.md:368-370` calls the attribution "not attempted"; `safe_tuned.rs:24-33`
frames the rung around it. Attributed with `.temp/r40/pads.py` (decoding
`Location{file*, len, line, col}`):

```
safe_naive (R2)  pads=7  48:23 48:50 49:20 49:57 (header) 70:29 `buf[off+i]` 71:17 `dst[dlen]`
safe_tuned (R3)  pads=2  50:24 `&buf[off..off+len]`   71:54 `&w[p..q]`
s1_tuned_indexed_fold      pads=2  50:24  71:54   <- IDENTICAL pair
s2_tuned_bytefold_reslice  pads=2  50:24  71:54   <- IDENTICAL pair
s3_tuned_copy_byteloop     pads=3  50:24  74:17 `dst[dlen]=b`  73:29 `w[i]`
unsafe / verus             pads=0
```

**Neither survivor is a destination check.** `dst[..dlen]` — the loop-carried case
§4 names — contributes **zero** pads in all three fold spellings, so the constant
2 is evidence the fold **never** contributed a pad. What survives is
`&buf[off..off+len]` (bound = the *caller's* precondition, unprovable inside
`kernel`) and `&w[p..q]` (bound `q ≤ len`, a runtime value). **The discriminator is
not locality**: `dlen ≤ DST_CAP` is bounded by a **constant** LLVM sees from the
guarded increments; `q ≤ len` by a **runtime value**. Sharper, and it does not
transplant p03.

## major 3 — the pair interval is not degenerate; route A verifies and moves 92.00

`NOTES.md:886-894` calls the R4 endpoint zero-width because route A's twin "does
not verify at the pinned vstd … not built or measured here". Built
(`.temp/r40/routeA/gen.py`: plain additive test, `requires buf@.len() <=
isize::MAX`, three loop invariants raised, one extra driver conjunct + invariant):

```
$ ./verus_run.py .temp/r40/routeA/a1_verus_routeA.rs             -> 15 verified, 0 errors
$ ./verus_run.py .temp/r40/routeA/a1_verus_routeA.rs --cfg slb_twin -> 18 verified, 0 errors
```

`md5_fn` R4 == R5 (so `exact` survives), `n_fn 140/135` vs shipped `142/138`,
same checksum on `small`.

| | small (K=6) | large (K=31) |
|---|---:|---:|
| shipped R4 (`&&`) | 1847.30 | 3317.70 |
| **route A R4** | **1830.30** | **3225.70** |
| shipped R3 | 1850.30 | 3291.70 |

**R4-side width is 17.00 / 92.00, not zero**, and on `large` the 92.00 is 3.5× the
`−26.00` headline and **flips its sign**: shipped R3 is **+66.00 dearer** than the
cheapest-found *verifying* R4. The published in-contract number survives (route A
misses `required[1]`); what falls is "zero measured width" and its stated reason.

## major 4 — "+2 instructions per string" is a static `n_fn` delta wearing a per-string label

Measured exact at four `K`, two never visited by p12's inputs:

| K | 6 | 12 | 20 | 31 | law |
|---|---:|---:|---:|---:|---|
| C shipped − A | **17.00** | **35.00** | **59.00** | **92.00** | `3.00·K − 1.00` |
| B subtraction-first − A | 24.00 | 48.00 | 80.00 | — | `4.00·K` |

The `identity` pin's price is **3.00 Ir per string walked**, 1.5× the published
figure, 92.00 Ir/call on `large`.

## major 5 — "where the check is" CONFIRMED; "on the destination" is not the rule

Six new cells, all printing `12909139622517405579` on `small`:

| cell | copy spelling | `memcpy`? | pads |
|---|---|---|---:|
| `m1_reslice_byteloop` | **safe BYTE LOOP**, no bulk call in source | **yes** | 2 |
| `m2_reslice_iterzip` | `iter_mut().zip()` | **yes** | 2 |
| `m3_u_dstchecked` | R4, only the **dst store** checked | **no** | 1 |
| `m4_u_srcchecked` | R4, only the **src load** checked | **no** | 1 |
| `m5_naive_copyfromslice` | R2 + `copy_from_slice` | **yes** | 6 |
| `m6_naive_reslice_byteloop` | R2 + dst reslice, src still indexed | **no** | 6 |

`m1`/`m2` are byte-identical. **So the recovery is about where the check is** — a
hand-written byte loop with no bulk call lowers to `memcpy@GLIBC_2.14`. **But
`m4` shows "on the destination" is not specific**: checking only the *source* per
byte also loses it. **The bulk lowering needs both ends free of a per-iteration
check.** `m1`/`m2` are in contract (miss only `required[3]`) and do not move the
R3-side span.

## Confirmations — do not re-run

- **All three out-of-sample predictions, independently re-measured**: gcc `large`
  **−125.00**, clang **+57.00**, `R3−R4` **−26.00**; `small` −25.00 / +7.00 /
  +3.00. Exact. Gate record agrees digit-for-digit.
- **The gcc sign mechanism, off the listing**: with no dominating branch gcc
  computes the copy length *and* the `dlen` update branchlessly (`setae`, spill,
  two `cmove`) around an unconditional `call memcpy`; the capacity test supplies
  the branch, the work moves out-of-line, the `cmove`s vanish. Net −4.00/string.
  (Also explains `c-gcc-h`'s "6 loops": 4 real + 2 out-of-line re-entries.)
- **Exact rational refit of the 48-row sweep**: `R1h−R1 gcc = −4.0K − 1.0`
  (maxres 0.000000), `clang = +2.0K − 5.0`, `R3−R4 = 5.0 − 4.0K + 3.0·nacc +
  4.0·[dlen%4]`, ranks **2/5, 4/5, 5/5** as published.
- **§3d's "no per-byte law" — confirmed and sharpened.** At constant `nacc` the R2
  increment per 24 copied bytes is `24.750 24.750 24.750 24.737` (**exactly
  linear**) against R4's `13.750 11.750 8.750 11.737`. **The non-law is entirely
  R4's `memcpy` size dispatch; R2 alone has a clean 24.75 Ir/byte law.**
- **§0's regimes reproduce**, and `-fno-stack-protector` is genuinely
  unnecessary. ⚠ **The boundaries are one step off**: gcc is silent to +8 and
  fires from **+12** (NOTES jumps +8→+16); clang's loop is destroyed **+12…+48**
  and SIGSEGVs from +64.
- **Verus recount exact**: 15/0, twin 18/0; per item 1+1+1+1+1+5+5 = 15; gate
  `tcb_items` 5 items / 10 lines. All four mutants reproduce with the cited lines;
  `p1` fails on the **write bound**.
- **§7/§8 reproduce**, including `d2` printing byte-for-byte C's wrong answer, and
  `n1_uchar_sum` aborting identically to no check at all.
- **§10a poisoning reproduced.** View asked for: in every observed case the whole
  `Ir` total is constant so the marginal is exactly 0 and `usable()` catches it —
  but that is empirical, not a theorem, and nothing cross-checks the executed call
  count against `n_iters`. A three-point slope test does **not** help (honest cells
  disagree ~0.1% from the Lemire window mix). **Practically moot for p12: all 29
  usable R1 points are non-overflowing.**

## minor 6 — §3e is not reproducible at the quoted precision, and §3a cites it anyway

| | session A | session B | NOTES §3e |
|---|---:|---:|---:|
| `R5 − R4` (must be 0) | **+5.89%** | **+5.94%** | +0.59% |
| R2 vs R4 | +35.72% | +25.75% | +23.76% |
| R3 vs R4 | +3.89% | **−1.05%** | +0.29% |

The live error bar is ±9 points, and `NOTES.md:328-333` says so and is vindicated.
But `NOTES.md:173-174` quotes *"within 0.4% of the unsafe rung on wall clock"* in
the §3a headline — two sessions straddle zero. Delete it or move it behind §3e.

## minor 7 — `n1_uchar_sum` narrows the *variable*, not the sum via a cast

Louder than the field form; result unaffected.

## Unsure / not done

- **Did not run `harness/check.py p12`** — the record is `FRESH` and every
  re-measured number matched; a full gate run would cost ~an hour to certify what
  staleness already certifies.
- Did not run Miri (confirmed native `d1`/`d2` behaviour instead); did not measure
  route A's wall clock (minor 6 makes it useless at 17/92 Ir).
- **Route A is out of contract as p12 declares it** (`required[1]`). No claim it
  *should* ship — only that the stated reason for excluding it is false and the
  endpoint it collapsed is 92.00 wide.
- The benign-row counter-design executes UB on every call; verified stable and
  non-poisoning at +8 on this box with both compilers, but that is a frame-layout
  property, not a guarantee.
- Did not attempt a checksum *collision* under p12's own fold — arithmetically
  reachable, but a hash coincidence rather than a usable design.

## Memory updates

None — reviewers do not write `.memory/`. Landed by the manager: the first half
only of the structural claim plus the measured counter-design and its UB cost
(`02-bench-rules.md`); the pad-decoding technique (`03-measurement.md`); p12's
corrected finding with the both-ends rule, the 3.00/string price and the fixed-R4
qualifier on `−26.00` (`01-ladder.md`).
