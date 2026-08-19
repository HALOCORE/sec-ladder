# TASK_026_REVIEW — report

Reviewer's return message, recorded by the manager (the reviewer cannot commit).
Scratch: `.temp/r26/` (180 KB, all text) — `NOTES.md`, `decode_blobs.py`,
`altwork.py` + `altwork.json`, `pathfit.py`, `sweep_pathfit.py`, `layout_r2.py`,
`branchsim.py`, `cachesim.py`, `worklever.py`, `bugtable.py`,
`gen_r4_for_twin.py`, `twin/r4_for_twin.rs`.

**Verdict: p07's headline SURVIVES.** Two majors and five minors against the
prose around it; corrections are TASK_029.

## Did

Attacked p07 in the order the task gave, starting at the workload. Re-ran
`harness/check.py p07`, `./verus_run.py` (both configs), `build_controls.py`,
`layout_control.py`, `sweep_ir.py --report`, `gen_controls.py`, and regenerated
`inputs/gen.py --sweep` twice into isolated trees.

## Evidence

### The headline survives — no workload flattens or reverses it

Six deliberately different query distributions, same element arrays, `nq = 58`:

```
workload       n probes/call   f_lo   f_eq    R4/call  R4/probe     R3-R4  /probe  (R3-R4)/R4
ship        16385      781.52  0.482  0.037   10581.50   13.5396   4930.12  6.3084      46.59%
allmiss     16385      812.08  0.493  0.000   11116.84   13.6893   5113.48  6.2968      46.00%
allhit      16385      754.34  0.461  0.077   10080.96   13.3639   4767.04  6.3195      47.29%
allbelow    16385      870.00  0.000  0.000   11411.30   13.1164   5461.00  6.2770      47.86%
allabove    16385      812.00  1.000  0.000   11527.30   14.1962   5113.00  6.2968      44.36%
cluster     16385      782.75  0.251  0.039   10408.58   13.2975   4937.50  6.3079      47.44%
```

**Monotone rising in `n` in all six.** Workload verified by decoding the blobs,
not by reading `gen.py`: hit fraction **exactly 0.500000** on `small`, `large`,
`unsorted` and all 113 sweep blobs; exactly one below-min key per window; ≥1
above-max; strictly ascending with gaps ≥ 2. `gen.py` deterministic — two fresh
regenerations byte-identical to each other *and* to the shipped blobs (120 files).

**The exact-integer laws are real invariants, not fits.** Independent probe-count
implementation, predicting the *integer* Ir difference out of sample on 30 fresh
blobs:

```
  R3-R4 total over 100 calls == 900 + 400*nq + 6*(total probes):    True  (30/30)
  R2-R4 total over 100 calls == 3600 + 1100*nq + 11*(total probes): True  (30/30)
```

**Gate, proof, identity, bugs all reproduce.** `check.py p07: PASS` in 87 s, log
byte-identical to the engineer's `gate6.log` but for two ASan PIDs. `10 verified,
0 errors` / `11 verified, 0 errors` under the twin. `md5_raw` *and* `md5_fn`
identical for `unsafe`/`verus` (`4f8c443684e1…`, `n_fn` 66/64, pad 4). TCB
recount: exactly 3 `external_body` items, 6 body lines (1/4/1), `main` verified,
no `assume`/`admit`. Three-bugs table reproduces cell for cell, including
`R1 c-gcc` printing `250787114008174592` on `adversarial-count` and `k_incl`
SIGSEGVing on p07's own `small.bin`. `build_controls.py` reproduces §10a/§10b/§11a
to the instruction; `layout_control.py` reproduces §11d (`−14.41 / −9.13 / −2.57 /
−4.51%`, all four band pairs disjoint).

### major 1 — `NOTES.md:321,347` (also `README.md:117-118`, `RECAP.md:568`): "first counterexample to safety is cheap" is contradicted by `.memory/01-ladder.md`

`.memory/01-ladder.md` already records, for the **R2** rung: p16's *"R2's cost is
per byte, not per call — 10.00 Ir per folded byte against R3/R4's 5.75, over 68
consecutive value lengths in two bands 18× apart… least-squares residual 0.00"*,
i.e. `+2085 (+69%)` → `+17123 (+72%)`, **rising**, converging to `4.25/5.75` =
73.9%, mechanism-attributed (2.00 check + 2.25 foreclosed unroll) and confirmed by
construction with `-unroll-count=1`; and p17 reproducing 4.2500 on a different
kernel. For **R3**: p05's `6·nrow + 9`, and the file's own words *"the cost is
`O(nrow)`, **not zero**"*.

p16's R2 story is structurally identical to p07's R3 story one rung down.
*Failure scenario:* the manager lands "first counterexample" into `.memory/` and
the next reviewer opens finding 5 and finds a bigger, older, swept one — the fifth
consecutive `.memory` overclaim.

**What survives and is the sentence to publish:** p07 is the first pattern where
**R3's** tax has *no axis along which it amortises*. p16/p17's R3 tax is a
per-**call** constant (0.00000 Ir/byte swept — the reslice sits outside the fold
loop); p05's is `O(nrow)`, which vanishes along `ncol`. p07's is 6.0000 Ir per
**probe** with `probes = nq·⌈log2 n⌉`, so the fraction rises in both `n` and `nq`.

Secondary: **the asymptote is workload-dependent.** 47.99% = `6.0000/12.5035` is
the shipped workload's. Measured marginals per probe: **12.0017** on `allbelow`
(pure `hi = mid` arm), **13.0026** on `allabove` (pure `lo = mid+1` arm), so the
asymptote is `6/(12 + f_lo)` ∈ **[46.15%, 50.00%]**. `README.md:116` quotes 48.0%
as if the kernel fixed it.

### major 2 — `NOTES.md:178,182-186`: R2's `ns` numbers are unbracketed and do not survive bracketing

`§11c` runs the layout control on `unsafe` and `safe_tuned` only. The bolded
headline at `:182` rests on `safe_naive`, never built at more than one alignment.
Built at seven (identical `Ir/call` 12346.57 at every one):

```
-- small.bin, 31 reps interleaved, taskset -c 3
   >> safe_naive: layout band 14.038..18.034 ms  spread 28.47%
   >> safe_tuned: layout band 15.378..16.999 ms  spread 10.54%
   >> unsafe:     layout band 13.450..14.139 ms  spread  5.12%
     safe_naive   point(best-vs-best)   +4.37%   layout interval [-0.72%, +34.08%]   bands OVERLAP
     safe_tuned   point(best-vs-best)  +14.33%   layout interval [+8.77%, +26.39%]   bands DISJOINT
-- large.bin
     safe_naive   point(best-vs-best)   -0.03%   layout interval [-0.63%, +3.97%]    bands OVERLAP
     safe_tuned   point(best-vs-best)   +0.89%   layout interval [+0.28%, +3.12%]    bands DISJOINT
```

Replicated, 41 reps on CPU 5: safe_naive spread **29.66%**, both intervals still
span zero. **28.47% is the widest single-rung band this project has measured** —
wider than the 21% and 32% cross-binary figures §11c cites — and it is on the rung
the headline uses. Neither `+28.0%` nor `+3.5%` has an established sign, so the
`8×` ratio has no support. §11c's own rule ("the ns column of §3 must not be read
below ~6%") would independently forbid the `+3.5%`.

**Clean negative inside this:** §3c's R3 counterweight (`+13.0%` / `+1.6%`) *does*
survive — bands disjoint on both inputs in both runs.

### major 3 — `NOTES.md:200-222` §3a: the per-probe level is presented as a zero-parameter derivation and is a fit with a wrong mechanism

`:219` claims `lo` path 13 + `hi` path 12 at a 50/50 split = 12.5, matching the
swept 12.5035. Three errors: the 50/50 is the **hit/miss** ratio, not the branch
split (measured `lo 0.4591 / hi 0.4764 / break 0.0645`); the loop has **three**
exits (body 8 + entry test 2 + tail lo 3 / hi 2 / break 0, query 16 = head 6 +
fold 8 + not-found 2, so a break probe is `8 + 1 − 2 = 7`); and 12.5035 is an OLS
slope over blobs whose break fraction falls 0.19 → 0.037. Both candidate
hand-derivations (12.4591 two-path, 12.1367 three-path) differ from it.

```
=== NOTES 3b model: a + b*nq + c*probes (3 free) ===
  unsafe       a=   39.40 b= 13.2240 c= 12.5035 max|res|=  10.566
=== three-path: a + b*nq + 13*P_lo + 12*P_hi + 7*P_eq (2 free) ===
  unsafe       a=  42.852 b= 16.0026                     max|res|=   0.4127
  safe_tuned   a=  51.852 b= 20.0026                     max|res|=   0.4127
  safe_naive   a=  78.852 b= 27.0026                     max|res|=   0.4127
  delta a=  9.000 delta b= 4.0000  delta per-probe lo/hi/eq = 6/6/6   [R3-R4]
  delta a= 36.000 delta b=11.0000  delta per-probe lo/hi/eq =11/11/11 [R2-R4]
```

25× better with **fewer** parameters, and it confirms the published differences
while showing why they are exact: R3's `+6` and R2's `+11` are identical on all
three arms, so the difference is path-independent where the level is not. The tell
was in §3b's own table — the branchless row's residual is 0.41 and the branchy
rows' 10.57. Listings otherwise check out: R3's `+6` is `lea, add, cmp, ja, cmp,
ja` at `0x15774–0x15789`; R2's `+11` is four one-sided index checks; LLVM merges
all four byte loads into one `movl` in R2 too.

### Attack 2 (`Ir`/`ns` reversal) — did NOT break; tightened three ways

1. **`callgrind --branch-sim=yes` works on this box** (vg 3.27.1) — this is what
   *is* available in place of the missing hardware counter:
   ```
   build                  input        Ir       Bc      Bcm  Bcm/Bc  Bcm/probe
   unsafe branchy         small   6582.98  1392.09   271.16  0.1948     0.5861
   unsafe branchless      small   7245.77   958.40    59.45  0.0620     0.1285
   unsafe branchy         large  21356.70  4825.21   853.98  0.1770     0.5314
   unsafe branchless      large  23691.98  3264.14    93.07  0.0285     0.0579
   ```
   +10.07% `Ir` buys −78.1% mispredicts on `small`, −89.1% on `large`; 0.586 per
   probe is exactly what a coin-flip branch should give.
2. **Isolation by measurement**: symbol-by-symbol instruction-stream diff of the
   two whole binaries — 559 symbols, **exactly one differs** (`kernel`, 70 → 68
   raw).
3. **`--cache-sim=yes` shows the lever locality-neutral**: `D1mr` 1076.82 on
   `large` for *both* builds, `DLmr` equal. Only branch counters move.

**And a lever `NOTES` does not have — the workload, program byte-identical:**

```
  workload   probes/call   Ir/call   D1mr    Bcm   ns/call  ns/probe
  ship            781.52  10581.50 300.52 422.78    2817.3    3.6049
  cluster         782.75  10408.58   1.60 273.35    1653.2    2.1121
  allbelow        870.00  11411.30   0.13  59.02     795.9    0.9148
  allbelow vs ship:  Ir/call +7.84%   ns/call -71.75%   ns/probe -74.62%
```

`cluster` separates locality from branches: at `D1mr ≈ 0` for both, adding 214.3
mispredicts/call costs 857.3 ns/call ≈ **4.0 ns ≈ 14 cycles per simulated
mispredict**, the textbook penalty.

### minor 4 — `NOTES.md:740` "Both candidates were" is false

`gen_controls.py` generates `r4_ptr_twin` only; `r4_for`'s "admissible" verdict at
`:744` was an inspection standing beside a Verus run. Built the twin
(`gen_r4_for_twin.py`, same substitution discipline): **`10 verified, 0 errors`**.
Verdict stands; the claim of having checked it did not. `:748` also cites
`.temp/p07/twin/r4_ptr_twin.rs`, which never existed — the file is
`.temp/p07/controls/r4_ptr_twin.rs`.

### minor 5 — `NOTES.md:382-384` §4's gate numbers predate the input fix

Those are `gate1.log`/`gate2.log` (07:07, 07:10); `inputs/` was regenerated at
07:30. `gate3–6` and my run all say `6021…216053`, `46.1x`, `11.96…131.97`.

### minor 6 — "`4·n + 4·nq` needs 36 bits" — it needs 35

`4·(2³²−1)·2 = 34 359 738 360`, `bit_length` 35, `2³⁵ = 34 359 738 368`.
`NOTES.md:58`, `README.md:79`, `verus.rs:179`, `c/kernel_hardened.c:15`,
`inputs/gen.py:332`, and `spec.md:385` (hashed). Conclusion unaffected; the rest
of §0's arithmetic checks out (`2⁶⁴/(2·(2³²−2)) = 2147483649`; min `n` per width
`2⁶³+1 / 2³¹+1 / 2³⁰+1 / 2¹⁵+1`; u32 LHS = 4 at `n = 2³⁰, nq = 1`; first probe at
2 GiB, key read at 4 GiB).

### minor 7 — stale probe/window arithmetic

`NOTES.md:139`: "6428 bytes probed out of a 1 048 916 byte window, 0.61%" → it is
**6624** and **0.63%**. `model.py:287-290`'s `work_per_call` docstring carries
`nq = 99` numbers (1782 probes, 7128 bytes, 1 048 840-byte window, `0.25 ×
1048840 = 262210`) against the shipped 1656 / 6624 / 1 048 916 / 262 229.

### minor 8 — `NOTES.md:180`: R5 is 0.0% kernel-exclusive but −1.00 whole-program

`build_controls.py` marginal: R5 `−1.00 / −1.00` Ir/call vs R4 on both inputs. The
kernel is byte-identical; the difference is outside it. §3b's laws are
whole-program marginals and §3's table is kernel-exclusive.

## Problems

None blocking. The only tree change was `results/gate/p07-binary-search.json`,
rewritten by `check.py` with fresh ASan PIDs; restored with `git show HEAD:… >`.

## Unsure / not done

- **`c-gcc`/`c-clang` `ns` claims are still unbracketed.** `-align-all-functions`
  is an LLVM knob; only the three Rust rungs were bracketed. §3's `c-gcc +51.9%`
  has no measured band (the clang row is already hedged).
- **The front-end alternative in §11d(i) is narrowed, not eliminated.**
  `--cache-sim` rules out the data-cache explanation and `--branch-sim` quantifies
  mispredicts, but a decode/uop-throughput effect from the shorter body is not
  excluded by simulation, and callgrind's predictor is a model, not this CPU's.
- **`4.0 ns per mispredict` is an attribution, not an isolation** — the
  predictable workload also gains cross-probe speculation.
- Miri wall times not independently timed (bounded only by the 87 s whole gate).
- The alt-workload sweep used `nq = 58` only (5 values of `n`), so it re-tests the
  `n` axis under six distributions but not the `nq` axis. The exact-integer laws
  were checked on all 30.
- Did not re-derive §3b's `c-gcc`/`c-clang` laws in three-path form.

## Memory updates

None — reviewers do not write `.memory/`. Recommended to the manager:

- **Land** the R3-scoped headline with the workload-dependent asymptote and the
  six-workload confirmation.
- **Do not land** "first counterexample to safety is cheap".
- **Do not land** any p07 R2 `ns` number or the "8× conversion factor" without the
  28.47% band beside it.
- **Correct** R4's per-probe mechanism to the three-path `13/12/7` + `16`/query
  form before quoting 12.5035 as derived.
