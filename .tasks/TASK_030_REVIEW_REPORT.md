# TASK_030_REVIEW — report

Reviewer's return message, recorded by the manager. Scratch `.temp/r30/` (712 K,
all text — every binary deleted): `layout_gen.py`, `jcc.py`, `loopfit.py`,
`predictors.py`, `analyze.py`, `survives.py`, `q3_convergence.py`, `modesim2.py`,
`predict_then_time.py`, `repeat.py`, `interleave.py`, `timeit.py`, the
`layout_p*.json`/`.log` set, `predictions_p0{1,7}fresh.json`, and `NOTES.md` with
the recipes at the bottom.

**Two blockers, four majors, two minors. The mechanism is identified.**

## Scope

The TASK_029 layout finding, attacked on **six other patterns** (p01, p02, p05,
p08, p16, p17) plus an independent 3-pass / 2-CPU replication of p07. Controls
held everywhere: `md5_fn_norel` and `n_fn` single-valued per rung over 30 layouts
(`md5_fn` gave **28–29 distinct digests** — the trap was live on *every* pattern),
stdout identical, callgrind totals invariant to ≤0.003%.

## Q1 — the mode generalises to exactly one more pattern of six, and it is p01

```
### layout_p01.json
  small  safe_naive  bit4 [0,1]->x0.9569 *PERFECT*   jcc32 [0,1]->x1.0450 *PERFECT*
  small  safe_tuned  bit4 [0,1]->x0.9256 *PERFECT*
  small  unsafe      bit4 [0,1]->x1.0501 *PERFECT*
### layout_p16.json  (the pattern the task nominated)
  small  safe_naive  bit4 x0.9977 | safe_tuned x1.0002 | unsafe x0.9998
### layout_p02.json best bit x1.0021   ### layout_p17.json best x1.0015
### layout_p05b.json small  safe_naive x1.0031  safe_tuned x0.9907  unsafe x1.0146  (none perfect)
```

p01 is **worse than p07** in one respect: all three rungs have a mode (~4–8%) and
the two safe rungs' modes run *opposite* to R4's, so the published gap has no sign.

```
pattern in    rung        published   pooled    mode0    mode16    dom   verdict
p01    small safe_naive     +5.40%   +1.16%   +5.24%   -4.10%   4/30   SIGN FLIPS
p01    small safe_tuned     +4.72%   +1.44%   +7.01%   -5.67%  11/30   SIGN FLIPS
p16    small safe_naive     -0.41%   -0.03%   +0.08%   -0.13%   2/30   gap <1% either way
p02    small safe_naive    +18.04%  +16.75%  +16.68%  +17.03%  30/30   survives
p08    small safe_naive   +105.16% +104.77% +104.43% +110.05%  30/30   survives
p17    small safe_naive     -0.22%   -0.09%   -0.12%   -0.18%   0/30   gap <1% either way
```

p07 replicated, three passes, two CPUs; the mode is present on `large` too:

```
small  safe_naive bit4: x0.7863 / x0.7825 / x0.7865  all PERFECT  (cpu3, cpu3, cpu5)
large  safe_naive bit4: x0.9700 / x0.9686 / x0.9707  all PERFECT
cross-pass reproducibility, small: spearman rho +0.91..+0.97, median |Δ| 0.22..0.52%
cross-pass, large, unsafe (a <1% effect): rho +0.06 / +0.12 / -0.03  -> noise
```

## Q2 — "bit 4" is a PROXY; the mechanism is the 32-byte fetch/DSB window grid

Box is `Intel Xeon Gold 6230`, family 6 **model 85 stepping 7** (Cascade Lake),
microcode `0x5000024` — carrying the mitigated microcode for the **Jump
Conditional Code erratum (SKX102)**: a 32-byte chunk containing a jump that
crosses or ends on a 32-byte boundary is not cached in the DSB.

```
align1  kernel 0x157c0 %32=0  SLOW 17.62ms   loop 0x15900..0x15946
        0x1593e jcc fused=1 bytes[27.. 4] je ...   <== JCC-ERRATUM
align2  kernel 0x157d0 %32=16 FAST 14.43ms   branches in loop crossing 32B: 0
safe_tuned: %32=0 -> 0 hits (fast), %32=16 -> 1 hit (slow)   [opposite residue,
            matching the measured opposite-sign mode]
```

`loopfit.py` enumerates **every** loop and fits two zero-parameter static
properties out of the recorded addresses — `win32` (32-byte windows the body
occupies) and `jcc32` (branches crossing/ending on 32B). **Every mode found on
every pattern is perfectly separated by one of them, on all passes:**

```
p07 safe_naive loop3 [+0x148,+0x191)  73B win32[3,4] small x0.7863 *PERFECT* (3 passes; large x0.9700 *PERFECT*)
p07 safe_tuned loop2 [+0xa0,+0xd4)    52B jcc32[0,1] small x1.0605..x1.0657 *PERFECT*
p01 unsafe     loop0 [+0x40,+0x5e)    30B win32[1,2] small x1.0501 / x1.0583 *PERFECT*
p01 safe_tuned loop0 [+0x50,+0x6e)    30B win32[1,2] small x1.0803 / x1.0823 *PERFECT*
p08 safe_naive loop4 [+0x2d0,+0x321)  81B win32[3,4] small x0.9734 *PERFECT*
```

p01 `unsafe` disassembled at both residues: the SSE loop is 30 bytes, lands
**entirely inside one 32-byte window at %32=0** and **straddles two at %32=16**
(`movdqu` at `+0x4b` spans bytes 27..1). That is the whole mode.

**Out-of-sample, pre-registered** — predictions written and SHA-256'd *before* any
timing, on 20 fresh symbol orderings the hypothesis never saw:

```
p07 sha256 5fd5ebdce09bef14113dab07abc42d8e1e18696b2503b4a27c9e100b12fdc678
  safe_naive jcc32 -> x1.2932 / x1.2896   PREDICTION HELD (perfect separation), 2 passes
  safe_tuned jcc32 -> x1.0767 / x1.0784   OVERLAP (one crossing pair)
p01 sha256 1462aa5f37aaa2f3d4c2bfde9a9ef4c6befb89ebcc7d7370ed9a3973d89f812b
  safe_naive x1.0605 / x1.0661   safe_tuned x1.0546 / x1.0587   unsafe x1.0410 / x1.0502
  ALL THREE: PREDICTION HELD (perfect separation), both passes
```

Mitigation flag `-C llvm-args=-x86-branches-within-32B-boundaries`, p07, 30
layouts: R3's band **17.12% → 4.00%** and **18.6% faster overall** (median
15.75 → 12.82 ms); R2's band 31.76% → 13.82%. Caveat, and why this is not the
decisive test: the flag also forces 32-byte function alignment, so
`kernel%32 == 0` at all 30 layouts and bit 4 is pinned by construction; and it
does not touch the `win32` form.

**The mechanism of the clean negatives, which is the part that generalises**:
p02/p16/p17/p05 all have loops whose `win32`/`jcc32` flips with bit 4 exactly as
p01/p07 do — and the time does not move.

```
p16 safe_naive loop1 [+0x80,+0x9f)   31B win32[1,2]  small x0.9977  large x0.9996
p17 safe_tuned loop3 [+0x1b0,+0x1ca) 26B win32[1,2]  small x0.9999  large x0.9975
p02 safe_naive loop0 [+0x80,+0x93)   19B win32[1,2]  small x1.0021  large x0.9984
p05 unsafe     loop0 [+0x70,+0x124) 180B win32[6,7]  small x0.9856  large x1.0016
```

**The geometry flip is universal; what is pattern-specific is being
front-end-bound.** p07 is not special in layout — it is special in having a serial
73-byte loop where one extra fetch window is 33% more front-end work.

## Q3 — mode-matching converges; DOMINANCE DOES NOT

400 subsampled draws per size:

```
### layout_p01.json  small  safe_naive vs unsafe
  N |     band(A) % |     mode0 % |    mode16 % | dom vs worst | pairwise P(A>B)
  4 |   +6.52± 2.12 | +5.58± 1.05 | -4.29± 1.27 | +28.69±26.05 |  +58.09±20.32
  7 |   +8.07± 1.82 | +5.42± 0.80 | -4.22± 1.08 | +19.79±17.30 |  +58.18±14.74
 15 |   +9.84± 0.80 | +5.30± 0.51 | -3.99± 0.76 | +15.18± 7.78 |  +58.43± 7.89
 30 |  +10.42± 0.00 | +5.24± 0.00 | -4.10± 0.00 | +13.33± 0.00 |  +58.44± 0.00
### layout_p07.json  large  safe_tuned vs unsafe
  4 |   +1.70± 0.63 | +0.99± 0.41 | +2.42± 0.53 | +94.81±11.02 |  +97.36± 6.26
 30 |   +3.32± 0.00 | +0.95± 0.00 | +2.53± 0.00 | +90.00± 0.00 |  +97.33± 0.00
```

Mode-matched medians are **flat in N** with spread ~1/√N — they converge.
**Dominance drifts**: p01 R2 28.7% → 13.3%, p07 R3/`large` 94.8% → 90.0%, sd ±17
points at N=7. It is defined against `max(B)`, an **extremum**, so it inherits the
exact defect of the range rule it replaced. `pairwise P(A>B)` over all N² layout
pairs is a genuine proportion and is flat at every N (58.1→58.4, 97.4→97.3,
73.9→74.7).

## Q4 — the simulators are not blind; they are three orders of magnitude too coarse

Whole-program totals, `--cache-sim=yes --branch-sim=yes`, three mode pairs:

```
### p07 safe_naive  align1 vs align2 (kernel +16 bytes, md5_fn_norel identical)
  Ir  99054451 vs 99054451  +0.0000%   Dr/Dw/Bc/Bi/Bim  all +0.0000%
  I1mr 1875 -> 1881 +6   ILmr 1830 -> 1835 +5   D1mr 2608 -> 2603 -5   Bcm 2184897 -> 2184900 +3
### p01 safe_tuned  I1mr +2  D1mr +2  D1mw +1  ILmr -1  Bcm +4
### p01 unsafe      I1mr -1  D1mw -3  ILmr -3  Bcm +7
```

Callgrind's cache model is address-indexed and its branch predictor address-hashed,
so neither is *structurally* blind — both register the move. They are blind to the
**front end**: no model of instruction fetch, the uop cache, or the JCC mitigation,
which is where 100% of the effect lives.

## blocker 1 — the mode generalises to p01, and p01's published `ns` ranking has no sign

`results/p01-array-sum.json`, `results/tables/p01-array-sum.md:125-142`. Published
`small` minima give R2 +5.40% and R3 +4.72% over R4. Mode-matched over 30 layouts:
R2 **+5.24% / −4.10%**, R3 **+7.01% / −5.67%**; perfect separation on all three
rungs, confirmed out of sample on 20 fresh layouts, two passes. *Failure
scenario:* a reader takes "safe-naive costs 5.4% of wall clock" from the table,
rebuilds `p01/safe_naive.rs` with any different link order, and measures R2 **4%
faster** than `unsafe` — same source, same flags, same machine.

## blocker 2 — p05's published `small` `ns` cells are a shipped-layout artefact, and its R3 number does not reproduce

`results/p05-index-flatten.json` (R2 +36.01%, R3 +4.12% on `small`). Measured
inside **one** round-robin containing the shipped binary and its own 30-layout
population, two passes:

```
safe_naive   shipped 7.454 ms   population median 6.334   rank 30/30  (slowest of 31)
safe_tuned   shipped 5.138 ms   population median 5.922   rank  0/30  (fastest of 31)
unsafe       shipped 5.703 ms   population median 5.910   rank  1/30
safe_naive vs unsafe: SHIPPED +30.69% / +34.97%   population +7.17% / +6.96%
safe_tuned vs unsafe: SHIPPED  -9.91% / -11.57%   population +0.22% / +0.54%
```

This is **not** the bit-4 mode (p05 has none) but it is worse for the published
number: p05's R2 headline is measured at the **worst** R2 layout against a
**near-best** R4 layout, and the population value is ~5× smaller. Reproduced in a
second session (`align0` @0x15700 = 6.476 ms vs median 5.714). Separately, p05's
`small` cell drifts between sessions by 10–20 points on the *same* binaries:
R3-vs-R4 measured **+2.60…+6.56%** across 8 blocks in one session and
**−9.91%/−11.57%** at the identical binary in another. **p05's `small` wall-clock
row is not reproducible and should be withdrawn.**

## major 3 — `.memory/03-measurement.md:541` is wrong about dominance

The text says the two replacement statistics work "because both are proportions
rather than extremes"; p07 `NOTES.md:1318` says the same. Dominance is *"slower
than the **worst** layout of rung B"* — an extremum of B. Milder than the range,
same defect, and its small-N spread is ±26 points at N=4. `pairwise P(A>B)` is the
fix and costs one line.

## major 4 — `.memory/00-environment.md:181` "the simulators are blind to code layout" is false as stated

Every cache counter and `Bcm` moves across the mode boundary. TASK_029's "all
cache counters 0.00 both" were *per-call marginal* values rounded to two decimals;
the absolute counts are not zero. Surviving sentence: *"callgrind's simulators are
address-sensitive but model no part of the front end, so across a 27% layout mode
they move by ≤6 events in 10⁸ — use them to attribute a cache or branch mechanism,
never to detect or rank a layout effect."*

## major 5 — "bit 4 of the kernel's entry address" is a proxy and mislocates the mechanism

`.memory/03-measurement.md:451-499` and p07 `NOTES.md:1206+` publish it as the law
and say the mechanism is "narrowed, not identified". It **is** the front end,
specifically the 32-byte fetch/DSB window grid, in two forms (`win32`, `jcc32`),
both computable statically with zero fitted parameters. Two consequences: (a) bit
4 is only the law because every kernel is 16-byte aligned, so a 32-byte-granular
property takes exactly two values — the partition is *not* a property of the entry
address, and a toolchain with 32-byte function alignment would erase the proxy
while leaving the effect; (b) §11e's negative rests on the 70-byte loop
`[+0x140,+0x186)`, whose window count *is* 3 in both modes — but that loop's fused
`cmp;je` crosses a 32-byte boundary in exactly one mode, and a second back-edge
`[+0x148,+0x191)` (73 bytes) does go 3→4 windows. The geometry evidence points the
right way once the right loop and the right property are used.
`.temp/r30/jcc.py`'s "tightest backward branch" heuristic picks the **wrong** loop
on any vectorised kernel (p01: the 12-byte scalar tail instead of the 30-byte SSE
loop) — `loopfit.py` exists because of that and enumerates all of them.

## major 6 — `.memory/03-measurement.md:545` "memory-bound inputs are far safer" understates

p07 R2's mode is **perfectly separated on `large` as well**, all three passes
(x0.9700 / x0.9686 / x0.9707), and mode-matched R2-vs-R4 on `large` is **+3.28%
vs +0.38%** — an 8× swing, same partition. Smaller on `large`, not absent.

## minor 7 — `--symbol-ordering-file` is not a pure kernel-address lever

It permutes all 582 text symbols, moving the driver, libstd and startup too. The
`order` sub-population differs systematically from the `align` one independently
of bit 4: p05 R3 `order/align` **+5.05% / +5.27% / +9.85%**, p07 R3 **+5.02% /
+5.01% / +4.36%**, p01 R4 **+3.62% / +3.50%**. Fine for *detecting* a
per-kernel-address mode; a pooled median or band over the mixed population is a
mixture of two perturbations and should not be quoted as "the layout band".

## minor 8 — p07's `unsafe` rung has an 8–9% layout band nothing here explains

`unsafe`/`small` spread 7.68–9.33% across every pass and both CPUs, reproducible
(rho +0.92…+0.96), not separated by any bit, and `jcc32` flips on it with no
effect (+0.5%). p07 `NOTES.md:1206+` records R4 as "0.4%, no mode" from the bit-4
partition only; the band is real and larger than several published gaps.

## Unsure / not done

- **The JCC erratum is confirmed as a mechanism, not proven as *the* mechanism.**
  The clean causal test — remove the erratum while holding bit 4 free — is not
  available: the mitigation flag also forces 32-byte function alignment. What is
  established is a zero-parameter static predictor separating every mode
  perfectly on two patterns including out of sample, plus a large band collapse
  when the predicate is removed. The `win32` form is a DSB/fetch-window argument
  by construction and geometry, not by an instrument.
- Magnitudes not derived — why one extra fetch window costs 27% on p07 R2, 8% on
  p01 R3 and 0.4% on p07 R4 is "front-end-bound or not" plus loop sizes and
  `Ir`/call as circumstantial support. No uop counts on this box.
- C rungs still unbracketed — `--symbol-ordering-file` needs `-fuse-ld=lld` under
  gcc, not run. Six unbracketed `ns` cells per pattern remain.
- Verus/R5 rungs not swept; R5 byte-identical to R4 on p07, unchecked on p01/p05.
- p05's shipped-layout penalty (~15%, three sessions) has **no** identified
  mechanism — not 32-byte, not 64-byte, not bit-indexed.
- p05's session-level drift (10–20 points, same binaries) documented, not
  diagnosed. `interleave.py` rules out round-robin width (R2/R4 = +33.75 / +31.24
  / +29.25 / +30.26% at widths 1/5/15/30 on byte-identical copies), so it is
  something slower-moving — frequency, an SMT sibling on cpu 3/43, thermal. No
  root, so no way to pin it.
- Did not re-open p07's headline, its exact-integer laws, or the spelling arc; did
  not edit `.memory/`, `patterns/` or `pilot/`; no `git add`/`commit`.

## Memory updates

None written (forbidden). Six corrections for the manager — see the landing in
`.memory/03-measurement.md` and `.memory/00-environment.md`:

1. **Scope**: measured on all seven patterns. Real on **p07 and p01**, marginal on
   p08 (R2, ~3%), **absent on p02, p05, p16, p17** (best bit ratio ≤ x1.003, never
   perfect). p02/p08/p16/p17 `ns` columns survive intact; **p01's `small` R2/R3
   cells must be withdrawn like p07's**, and **p05's for a different reason**.
2. **Replace "bit 4"** with the 32-byte fetch/DSB window grid via `win32`/`jcc32`
   (Intel SKX102 on this Cascade Lake box, µcode 0x5000024). Bit 4 is a proxy that
   works only because kernels are 16-byte aligned. The geometry flips on *every*
   pattern; being front-end-bound is what makes it cost time.
3. **Correct the dominance rule** — defined against an extremum, does not
   converge. Keep mode-matching; replace dominance with pairwise `P(A>B)`.
4. **Correct "memory-bound inputs are far safer"** — p07 R2's mode is perfect on
   `large` too.
5. **Correct "the simulators are blind to layout"** — they are blind to the *front
   end*; every counter moves, by ≤6 events in 10⁸.
6. **Add the lever caveat** for `--symbol-ordering-file`.
