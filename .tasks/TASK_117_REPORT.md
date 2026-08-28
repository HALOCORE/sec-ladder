# TASK_117 — review of `TASK_106`: `p23`, finding 38, and a ratio that does not survive its own caveat. Report.

**Role: research reviewer. Nothing was fixed.** Nothing under `patterns/`,
`.memory/`, `RECAP.md`, `results/`, `synthesis/`, `harness/` or `pilot/` was
written; `git status --porcelain` shows no file of mine outside `.temp/r117/`
and this report. I did not run `check.py`, `build.py` or `measure.py` except
`measure.py --check-stale` (**52 records, 0 STALE, `results/p23-partition.json`
FRESH** — I disturbed nothing the other three agents were reading). All scratch
is `.temp/r117/`; its `NOTES.md` lists every file and its rebuild command, and
every binary and blob has been deleted.

**Convention, stated once and true of every figure below unless the line says
otherwise: kernel-exclusive `Ir` per call, `-O3`, inline mode `isolated`,
debug-assertions OFF**, from
`patterns/p23-partition/controls/sweep_fit.py::kernel_ir` **imported** (only its
scratch dir redirected), on binaries built with `harness/build.py`'s own
`rust_flags(O3, isolated)`. That is finding 38's convention.

---

## Verdict

| | |
|---|---|
| blockers | **1** (B1) |
| major | **4** (M1–M4) |
| minor | **3** (m1–m3) |
| clean negatives | **5 named attacks that did not land** |
| `TASK_106`'s landing | **all eight `TASK_105` corrections are in the tree** (§C) |
| finding 38's PROVISIONAL marker | ⚠ **do NOT clear it. Correct the headline first.** |

**Answer to call 1 in one line: the `3.11×` does not survive, and the manager's
direction is wrong. The honest fixed-size ratio is `1.3148`, not `7.2`.**

---

# §A — ⚠⚠ B1 (blocker). THE `3.11×` IS A PROPERTY OF THE SHIPPED R3 SPELLING, AND THE SPELLING TERM IS NOT A CONSTANT — IT IS `2·dn − 2·recs`

## A.0 what I did

`TASK_106`'s `k_u5` lives in a **probe** (`.temp/t106/u2scan.rs`), at a
**different config** (`NREC=4 NELEM=48`), in a **different `Ir` convention**
(marginal whole-program), against **different kernels**. So I transplanted it
into the **shipped rung**: `.temp/r117/mk_rungs.py` reads
`patterns/p23-partition/safe_tuned.rs` read-only and writes `st_u5.rs` — the
shipped R3 with **only** the upward scan respelled —

```rust
            let mut g: usize = m - i;
            while i < j && m - g < j && scr[m - g] <= pv {
                g = g - 1;
            }
            i = m - g;
```

— plus verbatim copies of the shipped R3 and R4 and four control arms, and I
measured all of them on the **31 shipped band-K blobs** in finding 38's own
convention.

**Must-fire arm 1 (reproduction).** `st_base`/`un_base` reproduce all seven
published band-K rows:

```
  nlow    R3 pub      R3 mine     R4 pub      R4 mine   tax pub    tax mine     delta
  1       4296.41     4296.41     3590.04     3590.04     706.37      706.37     -0.00
  4       4355.62     4355.62     3714.29     3714.29     641.33      641.33      0.00
  8       4401.22     4401.22     3843.33     3843.33     557.89      557.89     -0.00
  16      4325.67     4325.67     3912.18     3912.18     413.49      413.49      0.00
  24      4018.86     4018.86     3715.91     3715.91     302.96      302.96     -0.00
  28      3787.46     3787.46     3532.46     3532.46     255.00      255.00      0.00
  31      3575.50     3575.50     3348.50     3348.50     227.00      227.00      0.00
```

and `un_base`'s `md5_fn` is `43acbc727fc6e61698308619fdc933a4`, the value
`TASK_105` published for the shipped R4 cell. **My build is the shipped one.**

**`st_u5` is IN CONTRACT** (`.temp/r117/audit_u5.py`, using
`harness/check.py::spelling_matches` **itself** against p23's own declaration):
it matches **all 8** `required` (rust) spellings and hits **0 of 6** `forbidden`;
and `required[0]`'s **English** — *"the conjunct `i < j &&` on BOTH inner scan
conditions"* — is satisfied **literally**. Negative arm: a file with none of the
pinned tokens misses all 8. **`st_u5` contains zero `unsafe`.**

**`st_u5` is the same program.** Checksums equal `st_base`'s and `model.py`'s on
all 31 band-K blobs, on 24 further blobs I generated, **and on all nine non-sweep
gate inputs — `small`, `large`, `degenerate` and all six `adversarial-*`**
(`.temp/r117/equiv_all_inputs.log`).

⚠ **The obvious negative arm did not fire and that is finding m2 below.**

## A.1 ⚠⚠ THE RESULT

```
 nlow rank    R3ship     R3u5    R4ship |  tax_ship    tax_u5   SPELLING
    1 0.031  4296.41  3816.41  3590.04 |    706.37    226.37    +480.00
    4 0.125  4355.62  3923.62  3714.29 |    641.33    209.33    +432.00
    8 0.250  4401.22  4033.22  3843.33 |    557.89    189.89    +368.00
   16 0.500  4325.67  4085.67  3912.18 |    413.49    173.49    +240.00
   18 0.562  4278.35  4070.35  3897.71 |    380.64    172.64    +208.00
   24 0.750  4018.86  3906.86  3715.91 |    302.96    190.96    +112.00
   28 0.875  3787.46  3739.46  3532.46 |    255.00    207.00     +48.00
   31 0.969  3575.50  3575.50  3348.50 |    227.00    227.00      +0.00
                                          (all 31 rows in .temp/r117/bandk_u5.log)

published (shipped R3 - shipped R4): min   227.00  max   706.37  ratio  3.1117
in-contract floor  (u5 - shipped R4): min   172.64  max   227.00  ratio  1.3148
the SPELLING term        (R3 - u5):   min     0.00  max   480.00  spread 480.00
```

⚠⚠ **THE SPELLING TERM IS NOT CONSTANT IN THE PIVOT RANK. IT IS EXACTLY
`2·dn − 2·recs`** — proportional to `dn`, **the very regressor finding 38 says
carries the whole 3.11× swing** — so it is **maximal (480.00) exactly where the
published tax is maximal and exactly ZERO where the published tax is minimal.**

Checked with zero fitted parameters against the byte-counted
`recs`/`dn`/`sw`/`rounds` (`.temp/r105/band_counts.py::window_stats` imported):

```
A  published law   R3ship-R4 = 2 + 30recs + 2dn + 2sw - 3rounds     max|residual| = 0.0000
B  the SPELLING term  R3ship-R3u5 = 2dn - 2recs                     max|residual| = 0.0000
C  the residual tax   R3u5-R4     = 2 + 32recs + 2sw - 3rounds      max|residual| = 0.0000
D  NEGATIVE ARM for B: same law, response SHUFFLED                  max|residual| = 448.0000
```

**C is A minus B — arithmetic, not a fit — and it has NO `dn` TERM AT ALL.**
I then verified B and C **off band K** on ten more blobs spanning `m` 32…64 and
`recs` 8 and 20, predictions registered before measurement
(`.temp/r117/u5_offband.py`, which prints the predictions in step 1 and the
measurement in step 2):

```
blob         R3ship       R3u5     R4ship |  spelling       err |    tax_u5       err
z-m48       6118.52    5750.52    5608.37 |    368.00     +0.00 |    142.15     -0.00
z-m56       7021.24    6589.24    6463.29 |    432.00     +0.00 |    125.95     -0.00
z-m62       7754.70    7274.70    7133.86 |    480.00     +0.00 |    140.84     -0.00
z-m63       7919.90    7423.90    7277.71 |    496.00     +0.00 |    146.19     +0.00
z-m64       7885.74    7389.74    7275.54 |    496.00     +0.00 |    114.20     +0.00
z-m64r      8028.47    7404.47    7283.51 |    624.00     +0.00 |    120.96     -0.00
z-m64n     19716.45   18476.45   18202.31 |   1240.00     +0.00 |    274.14     +0.00
                                            max |error| spelling 0.00  tax_u5 0.00
```

> **`R3ship − R3u5 = 2·dn − 2·recs`** and
> **`R3u5 − R4ship = 2 + 32·recs + 2·sw − 3·rounds + Σ τ(m mod 4)`**,
> **max |residual| `0.0000` over 41 points** (31 band-K + 10 off-band),
> `-O3 isolated`, kernel-exclusive, debug-assertions off, shipped rungs.

## A.2 ⚠⚠ AND THE REGRESSOR INVERTS. THIS IS THE SHARPEST HALF.

Single-regressor R² over the 31 band-K points
(`.temp/r117/tax_u5_regressors.log`):

| response | `dn` | `sw` | `rounds` | `rank` | `3·rounds − 2·sw` |
|---|---|---|---|---|---|
| **tax_shipped** (published) | **0.9869** | 0.0132 | 0.0126 | **0.9869** | 0.0114 |
| **tax_u5** (in-contract floor found) | **0.0001** | **0.9930** | **0.9967** | **0.0001** | **1.0000** |
| the **spelling** term | **1.0000** | 0.0000 | 0.0000 | **1.0000** | 0.0001 |

⚠⚠ **`dn` explains 0.9869 of the published tax and `0.0001` of the in-contract
floor. `rank` — the axis the finding is named for — likewise 0.9869 → 0.0001.**
Finding 38's own clean negative (*"the swap-count confound is REFUTED … `sw`
alone R² 0.0132 … the 3.11× swing is carried by `dn`"*) is **true of the shipped
pair and false of the pattern**: once the R3 side is spelled at the cheapest
in-contract form found, **`sw` R² 0.9930 and `dn` R² 0.0001.**

## A.3 the mechanism, and it lands on 9d's OPEN cause

Two further arms on the shipped rung (`.temp/r117/bandk_dnunchk.log`,
`floor_arm.log`), both checksum-verified:

* **`st_dnunchk`** (shipped R3, only the downward read `get_unchecked`) minus
  shipped R4 is **`258.00` — EXACTLY, at every one of the 31 ranks.**
  `258 = 2 + 32·recs`. **Unchecking one read removes the ENTIRE rank-dependence
  of the published tax**, and what is left is per-record and rank-free (the
  checked window reslice, the checked header reads, the `iter().fold`).
* **`st_bothunchk`** (both scans and the exchange unchecked) `==` `st_dnunchk`
  **exactly at all 8 ranks measured.** ✅ **`NOTES.md` 9d's phenomenon,
  confirmed on the SHIPPED rung for the first time — it had only ever been shown
  on a probe.**
* ⚠ **And `st_u5` is BELOW `st_bothunchk` at every rank, by `31.00 … 85.36`
  `Ir`/call.** So on the shipped rung: **a fully safe, zero-`unsafe`,
  in-contract R3 is cheaper than the same rung with both scan reads and the
  exchange turned into `get_unchecked`.** 9d publishes that from the probe at
  *two of three* ranks; on the shipped rung it is **8 of 8**.

## A.4 ⚠⚠ M1 (major). THE MANAGER'S ARITHMETIC IS WRONG IN FOUR INDEPENDENT WAYS

`227 − 150` and `706 − 150` cannot be done, because the `150` and the `227/706`
are not the same kind of number:

1. **Different `Ir` convention.** `227/706` are **kernel-exclusive** (finding
   38's law says so). The `150` comes from `.temp/t101/cost23.py`, whose own
   header declares **marginal whole-program `Ir`/call, "(INCLUDES callee cost)"**.
2. **Different configuration.** `227/706` are `nrec = 8, m = 32, 256 B/call`
   (band K). The `150` is `NREC=4 NELEM=48` — and *"per call"* folds **4**
   records there and **8** here, so every per-record term is off by 2× before
   anything else.
3. **Different kernels.** `227/706` are the shipped `safe_tuned.rs`/`unsafe.rs`.
   The `150` is a probe pair — and see M3: **the probe kernel `NOTES.md` calls
   "the shipped R3 shape" is not it.**
4. ⚠ **It is not uniform, and TASK_106's own report says so** in §1's fourth
   bullet (*"the size of the correction is itself rank-dependent … there is no
   single number"*). Measured properly it is `2·dn − 2·recs`: **480.00 at
   `nlow=1`, 0.00 at `nlow=31`.**

**So the arithmetic `227−150 → 77` and `706−150 → 556` gives `7.2×`, and the
measurement gives `1.3148`.** The manager's direction was backwards, as it
suspected it might be. ✅ **I reproduced TASK_106's probe figures exactly in the
probe's own convention** (`.temp/r117/probe_repro.log`: `base` 3140.30 / 3187.00
/ 2563.70, `u1` = `u5` 2756.30 / 2991.00 / 2563.70, `r4b` 2768.30 / 3050.00 /
2575.70) — **TASK_106's numbers are right; only their combination with the
headline is not.** Note that in the probe too the saving at the top rank is
**exactly 0.00**, which agrees with my `nlow=31` row.

## A.5 ⚠ WHAT SURVIVES — and the task file was right to warn against overcorrecting

**The SHAPE axis is real and I am not withdrawing it:**

* `up + dn == mbytes` exactly at all 109 points — reproduced in my own design
  matrix; on band K `up` and `dn` each run `8.00 … 248.00` at `mbytes` fixed at
  256.00;
* the in-contract floor **still moves at fixed size** — `172.64 … 227.00`, a
  `54.36 Ir`/call swing with element count, record count and copied bytes all
  held constant, ratio **1.3148**;
* the published law survives twelve genuinely out-of-band points at `0.00`
  (§B).

**The honest headline, and I would write it exactly like this:**

> **p23's safety tax depends on the data's SHAPE at fixed SIZE, but the
> published `3.11×` is a property of TWO SHIPPED SPELLINGS and not of the
> pattern.** Respelling the **upward** scan alone — semantically null, zero
> `unsafe`, in contract on all eight `required` entries and on `required[0]`'s
> English — removes `2·dn − 2·recs` `Ir`/call, which is `480.00` at the band's
> top and `0.00` at its bottom, and collapses the fixed-size ratio to
> **`1.3148`** over a range of `172.64 … 227.00`. ⚠ **The rank-dependence
> belongs to the spelling: `rank` explains `0.9869` of the shipped tax and
> `0.0001` of the cheapest in-contract R3 found.** What survives at fixed size
> is a `54.36 Ir`/call swing whose regressor is the **exchange/round count**
> (`sw` R² `0.9930`), i.e. **the quantity finding 38 explicitly refutes as the
> driver.**

⚠ **And say "cheapest found", never "the honest tax".** `1.3148` is the ratio of
an **upper bound on `inf(in-contract R3) − R4ship`**, taken over the thirteen
in-contract spellings now searched. A cheaper R3 would move it again — in an
unknown direction, since the correction is rank-dependent.

---

# §B — the law. ⚠⚠ CLEAN NEGATIVE: I attacked it four ways and it did not move.

## B.1 ✅ CLEAN NEGATIVE — `0.0000` is NOT a collinearity. The design is rank 8/8.

`.temp/r117/design.py` builds the 109-point design
`[1, recs, dn, sw, rounds, τ₁, τ₂, τ₃]` from the **bytes** and computes rank in
**exact rational arithmetic** (no threshold):

```
  ALL 109                                n=109  rank 8/8   free cols: none
  M+N (the holdout's TRAINING set, 71)   n=71   rank 8/8   free cols: none
  band K alone (31)                      n=31   rank 4/8   free: recs, t1, t2, t3
      null direction: 0 = -8*1 + 1*recs        <- TASK_106's known degeneracy
  band M alone (47)                      n=47   rank 7/8   free: recs
  band N alone (24)                      n=24   rank 4/8   free: dn, t1, t2, t3
      null direction: 0 = -8*recs + 1*dn       <- TASK_106's other known one

  is `rounds` in the span of [1, recs, dn, sw]?
    ALL 109        rank 4 -> 5  ->  rounds is INDEPENDENT
    band K alone   rank 3 -> 4  ->  rounds is INDEPENDENT
```

**Rank 8/8 over the 109 points means the eight coefficients are UNIQUE**, so a
zero residual cannot be a collinearity; **rank 8/8 over the 71 M+N training
points means the published holdout's fit is identified too.** §B item 2 does not
land. ⚠ **Must-fire arm: the routine reproduces both degeneracies `TASK_106`
already named**, so it is not simply printing 8.

## B.2 ✅ CLEAN NEGATIVE — twelve out-of-band points, `max |error| 0.00`

The residue audit found **four** parameters the `τ` repair did not address:

| | degeneracy | where |
|---|---|---|
| **D1** | ⚠ **`τ` has only ever been observed at rank ≈ 1/2.** Band M — the only band that varies `m mod 4` at a uniform record shape — holds `nlow = m//2` at every point; band K, the only rank-sweep band, sits at `m = 32 ≡ 0 (mod 4)` where `τ = 0` | 102 of 109 |
| **D2** | **`recs ≤ 24`** everywhere; `30·recs` is never sampled above 24 | 109 of 109 |
| **D3** | **no uniform-shape point has `m > 48`**; `m ≡ 3 (mod 4)` above 48 is absent from the tree entirely | 109 of 109 |
| **D4** | ⚠ **`neq` (bytes EQUAL to the pivot) is FIXED AT 0 on all 102 points of bands K, M and N** | see m2 |

⚠ **Answering §B item 3 directly: the shipped 109 points FIX `sweep_fit.py`'s
`want_m` blindness** — band M ships all 47 values of `m` from 2 to 48, covering
every residue mod 4 many times over, which is exactly how `τ` was found. **They
do not fix D1–D4.**

I generated fourteen blobs breaking D1–D4, **registered the predictions in
`.temp/r117/oob_pred.json` before reading a single `Ir`** (`oob_gen.py` prints
"PREDICTIONS REGISTERED"; `oob_measure.py` only reads that file), then measured:

```
blob              R3         R4   measured  predicted     ERROR   breaks
c-k16        4330.27    3915.43     414.84     414.84     -0.00   CONTROL (must be 0.00)
c-m32        4311.54    3893.75     417.79     417.79     -0.00   CONTROL (must be 0.00)
o-m29lo      4076.12    3447.21     628.91     628.91     -0.00   D1  m=29 (1 mod 4) rank 0.103
o-m29hi      3517.06    3254.19     262.87     262.87     -0.00   D1  m=29 (1 mod 4) rank 0.897
o-m30lo      4201.81    3547.21     654.60     654.60     -0.00   D1  m=30 (2 mod 4) rank 0.100
o-m31hi      3745.36    3468.85     276.52     276.52     -0.00   D1  m=31 (3 mod 4) rank 0.903
o-m31lo      4339.53    3661.43     678.10     678.10     +0.00   D1  m=31 (3 mod 4) rank 0.097
o-m51        6572.54    6003.66     568.89     568.89     -0.00   D3  m=51, m > 48, uniform
o-m55lo      7031.10    6013.70    1017.40    1017.40     +0.00   D3  m=55 > 48 rank 0.09
o-m63hi      6847.79    6521.67     326.12     326.12     -0.00   D3  m=63 > 48 rank 0.87
o-r30       10177.23    8597.73    1579.50    1579.50     +0.00   D2  recs=30 > 24
o-eq32       4297.64    3776.93     520.71     520.71     -0.00   D4  neq=8 EQUAL to pivot
o-eq27       3688.45    3309.67     378.77     378.77     +0.00   D4  neq=6, m=27 (3 mod 4)
o-clamp      7959.72    7322.24     637.48     637.48     -0.00   DOMAIN nelem=100 > SCR
```

**12 out-of-band points, max |error| `0.00` `Ir`/call.** ⚠ **The set
discriminates** — the three superseded forms on the same 12 points:

```
  PUBLISHED  2 + 30recs + 2dn + 2sw - 3rounds + tau        max|error| =       0.00
  band-K collapse  242 + 2dn + 2sw - 3rounds  (TASK_105)   max|error| =     720.00
  no-tau           2 + 30recs + 2dn + 2sw - 3rounds        max|error| =      60.00
  30.25/record     30.25recs + 2dn + 2sw - 3rounds         max|error| =      54.50
  dn coeff 2 -> 2.01 (a 0.5% perturbation)                 max|error| =       4.00
```

**Answer to call 2: the law is the strongest thing in this pattern and I could
not break it.** ⚠ **It even extends outside its declared domain** — `o-clamp`
(`nelem = 100 > SCR = 64`, so the copy clamps and the cursor skips 36
undeclared bytes) lands at `0.00`, and **no point in the shipped 109 exercises
that regime at all.**

---

# §C — did `TASK_106` land `TASK_105`? ✅ Yes, all eight. Two labelling defects.

Checked **in the tree**, not in the report:

| # | claimed target | in the tree? |
|---|---|---|
| M1 | `NOTES.md` §7, `README.md` | ✅ §7 publishes the invariant and **no number** on the two run-dependent lines, plus the logged-run history; `README.md`'s harm row says *"seven or eight … and every cell's number moves on every rebuild"* |
| M2 | `NOTES.md` §3, catalogue | ✅ §3's table gives `R1 − R1h = +39.10 / +60.34` and the prose names **both** quantities beside every figure; the catalogue row carries `SIGN CORRECTED (TASK_105 M2)` |
| M3 | `NOTES.md` §3a, catalogue | ✅ new §3a exists with the 31-point table, both zero crossings, the refuted trip-bound mechanism (`dn` R² 0.023 / `sw` 0.973) and the band-X positives |
| M4 | `NOTES.md` §0 limb 3 + §9d, `spec.md` | ✅ limb 3 reads *"⚠ The CAUSE is OPEN"*; §9d withdraws the mechanism explicitly. ✅ **`spec.md` genuinely has no target** — I re-grepped the whole `slb-contract` block for `direction|induction|elid|elision|whole tax|monotonic`: **zero hits inside or outside the fence.** |
| M5 | `NOTES.md` §9b + §9b′ | ✅ §9b′ exists, corrects **both** endpoints, and states the overlap |
| A.2 | `NOTES.md` §0 | ✅ *"the multiset is separable"* is struck with the `pB1`/`pB2` evidence and the must-fire arm named |
| m1 | Rule-6 section | ✅ the headline now reads *"ONE of the five edits is a weakening"* and cites its own table row 1 |
| m5 | `NOTES.md` §10 | ✅ present |

**The hashed block.** `contract_sha256` is `8251a676…816af` in the tree and in
`results/gate/p23-partition.json`; `spec.md` was not edited, exactly as
`TASK_106` §3 says. ⚠ **No correction that needed to be inside the fence landed
outside it** — because none of the eight needed to be inside it. **Answer to
call 3: `TASK_106` IS a straightforward landing and would close cleanly on §C
alone. It does not close, because of §A.**

## ⚠ M3 (major). `NOTES.md` publishes `k_r3c` as "the shipped R3 shape". It is not — `k_r3d` is.

`patterns/p23-partition/safe_tuned.rs` uses the **two-step window reslice**
(`buf.split_at(off).1.split_at(len).0`) **and** `scr[..m].iter().fold(...)`.
In `.temp/t101/cost23.rs`:

| kernel | reslice | `iter().fold` | == shipped R3? |
|---|---|---|---|
| `k_r3c` | **no** | **no** | **NO** |
| `k_r3d` | yes | yes | **YES** |
| `k_r3e` | no | yes | no |
| `k_r3f` | yes | no | no |

`NOTES.md` **9b′**'s table header row says `base = k_r3c, the shipped R3 shape`,
and **9d**'s table says `base | the shipped R3 shape`. Both are wrong, and both
are in the shipped tree. ⚠ **`NOTES.md` §9b′ then, thirty lines later, correctly
calls `r3d` *"the shipped spelling"* and quotes its `3094.30 / 3141.00 /
2517.70`** — so **one section calls two different kernels the shipped R3**, and
the `338 / 150 / −46` rank-dependence figure is measured against `r3d` while the
table above it is `r3c`. The two levers `r3c` is missing are precisely the ones
`safe_tuned.rs`'s own doc comment prices at **−38.00** and **−16.00**; `r3d` is a
flat `46.00` below `r3c` at all three probe ranks. **PROTOCOL rule 13's shape,
landed at `TASK_106`.** ⚠ **9d's *conclusion* is unaffected — I confirmed it on
the shipped rung (§A.3) — but a reader cannot tell which kernel a 9d row is
about.**

## ⚠ M4 (major). `.memory/06-catalogue.md` asserts a claim and its refutation in the same row

The `p23` row contains

> ✅ **Clean negative alongside it: NO in-contract respelling elides the downward
> check** … **The tax is not a spelling cost inside the declaration.**

and, ~3 000 characters later in the same row,

> ⚠⚠ **M5 IS RESOLVED AND IT WENT AGAINST THE HEADLINE: THE `2991.00` SPELLING
> IS ADMISSIBLE.**

`TASK_105`'s clean negative was about respellings of the **downward** scan and is
still true as scoped; the sentence *"the tax is not a spelling cost inside the
declaration"* is a **general** claim and it is **false** — §A measures the
spelling at `480.00 Ir`/call at the band's top. It stands unqualified in **the
layer this project calls authoritative**, before the sentence that refutes it.
⚠ **`RECAP.md` finding 38 does NOT carry that sentence** — this defect is
catalogue-only.

---

# §D — the owed item. The manager's cost estimate is right and INCOMPLETE.

**Which generator writes the file:**
`patterns/p23-partition/controls/sweep_fit.py`, `main()`, final lines
(`json.dump(res, ...)` into `os.path.join(HERE, "sweep_fit.json")`).

**Which key it must carry:** a top-level **`gate_source_sha256`**, an object
equal to `results/gate/p23-partition.json`'s `source_sha256`.
`synthesis/licence.json` is the shape (I read it: a `gate_source_sha256` object
of `path → sha256`). `check.py::check_control_json_pins` reads exactly
`doc.get("gate_source_sha256")` and compares it to `source_sha`.

**✅ The manager's cost claim VERIFIED INDEPENDENTLY, from the two records'
bytes rather than from the docstring:**

```
results/gate/p23-partition.json    source_sha256 controls entries:
    patterns/p23-partition/controls/guard_equiv.py
    patterns/p23-partition/controls/sweep_fit.py           <- IN
results/p23-partition.json         source_sha256:  18 keys, NO controls/ entry
    (measure.py::measurement_sources globs pdir/*.rs, pdir/c/*, model.py,
     inputs/gen.py, common/driver.*, common/slb.py, harness/{build,asm,measure}.py,
     verus_run.py -- non-recursive, no controls/)
```

**and `sweep_fit.json` itself is in NEITHER record**, so writing the pin does not
create a fixpoint. **The one-off cost is one gate re-run plus one
`sweep_fit.py` run (26 blobs × 6 cells ≈ 2 min of callgrind) and no re-measure.**

## ⚠ m3 (minor). But the RECURRING cost is not one gate re-run, and it collides with `TASK_106` §4

Stage 9b **FAILS** on `pin != source_sha`. `source_sha256` covers
`NOTES.md`, `README.md`, `spec.md`, every rung `.rs`, `model.py`, `inputs/gen.py`
and both `controls/*.py`. So **once the pin exists, ANY edit to `NOTES.md` turns
the gate RED until someone re-runs `sweep_fit.py`.**

⚠⚠ **That is `TASK_106` §4's regress with a second turn added.** `NOTES.md` is in
the gate `source_sha256`, so every `NOTES.md` edit already forces a gate run;
with the pin live it also forces a 2-minute callgrind sweep, or a red gate. **A
prose fix to `p23` would cost a callgrind run.** ⚠ **A red gate nobody can
cheaply clear is the failure mode `check_control_json_pins`'s own docstring says
it is avoiding** — and the fix would reintroduce it one level up.

**Cheaper design, offered and not implemented:** pin against the **subset that
can move the file's numbers** — the rung `.rs`, `inputs/gen.py`,
`harness/build.py`, `common/driver.rs` — rather than the whole gate
`source_sha256`. That is the same set `measure.py::measurement_sources` already
computes, and it makes a `NOTES.md` edit free while still catching a rung edit.

## ⚠ Is the SHOUT visible anywhere a reader would see it? **No.**

`UNPINNED` appears in exactly two places, **both inside one JSON file**:
`results/gate/p23-partition.json`'s `controls_json` (`{"sweep_fit.json":
"UNPINNED"}`) and its `loud[1]`. `results/tables/p23-partition.md` does not
mention it; `results/synthesis.md`, `results/SYNTHESIS.md`, `harness/report.py`
and `synthesis/*.py` do not read `loud` or `controls_json`. **A shout nobody
reads is a check that cannot fail.**
⚠ **`TASK_114` (concurrent) reached the same conclusion at
`.tasks/TASK_114_REPORT.md:560-569`. I verified it independently; do not count
it twice.**

---

# Minor findings

## ⚠ m1 (minor). `README.md` puts the two conventions in adjacent table rows with no warning — and that is the trap the manager fell into

```
| R3 − R4              | +305.74 Ir/call on small, +443.55 on large … |
| in-contract R3 span  | 2991.00 … 3719.00 probe-Ir/call, twelve spellings, median band |
```

followed six lines later by the `227.00 … 706.37` headline. **Three different
conventions and three different configurations in one screen**: kernel-exclusive
on the matrix inputs, marginal whole-program at `NREC=4 NELEM=48`, and
kernel-exclusive on band K. Only the middle row is labelled. ⚠ **Every
number in `9b`/`9b′` — including the `150.00` finding 38 quotes — is
`probe-Ir` and none of them is comparable to the headline.** The suggested fix
is one word per row.

## ⚠ m2 (minor). The non-strict `<=` / `>=` pin is UNEXERCISED on 102 of the 109 points the law is fitted on

`inputs/gen.py` builds every `sweep-k*`, `sweep-m*` and `sweep-n*` record with
`neq = 0` — **no byte equals its pivot.** Demonstrated, not inferred: I built
`st_strict.rs` (the shipped R3 with `<` / `>`), which is **out of contract**
(`required[1]` MISS) and a **different program**, and it prints the **same
checksum as the shipped R3 on every band-K blob.** That was my first negative
arm and **it did not fire**; I replaced it with a deleted exchange, which does.
`spec.md`'s `why`(2) says the pin *"is what stops a rung comparison moving on
it"* — true, and on 102 of 109 points there is nothing for it to stop.
✅ **Only band X (5 points) and `small` carry `neq > 0`**, and my `o-eq32` /
`o-eq27` blobs (`neq` = 8 and 6) show the law holds there at `0.00`.

## Reviewer-checklist items checked and clean

* **Semantic equivalence.** `st_u5` == `st_base` == `model.py` on all 9 non-sweep
  gate inputs (incl. all six `adversarial-*` and `degenerate`), all 31 band-K
  blobs and all 24 blobs I generated.
* **Constant folding.** `has_loop: True`, 6/6/7 backward branches for
  `st_base`/`st_u5`/`un_base`; `off` still derives from the previous call's
  result. No rung became a constant.
* **Deterministic metric primary.** Every figure in this report is callgrind
  `Ir`. **No wall clock is quoted anywhere**, deliberately — three other agents
  were running.
* **`results/` untouched.** `measure.py --check-stale`: 52 records, **0 STALE**,
  `results/p23-partition.json` **FRESH**.

---

# ✅ Clean negatives — five named attacks that did NOT land

1. **The law is not a collinearity.** Design rank **8/8** over all 109 points
   *and* over the 71 M+N training points; `rounds` independent of
   `[1, recs, dn, sw]` over both. §B item 2 is answered: no.
2. **The law is not residue-blind in a new place.** Twelve out-of-band points
   breaking four separate degeneracies — `τ` at ranks 0.10 / 0.90, `m > 48`
   uniform, `recs = 30`, `neq > 0` — at **max |error| 0.00**, on a set that
   rejects three superseded forms by 720 / 60 / 54.5.
3. **The law survives outside its own declared domain.** `nelem = 100 > SCR`
   (the clamp regime, absent from all 109 shipped points) predicts to `0.00`.
4. **The in-contract safe rung never beat the shipped unsafe rung.** I chased a
   negative `tax_u5` deliberately — `3·rounds − 2·sw` approaches `2 + 32·recs`
   as `m → SCR` — over ten blobs at `m` up to 64 and `recs` up to 20. **Minimum
   `tax_u5` = 114.20 `Ir`/call at `m = 64`, rank 0.5. No sign change.** Nobody
   needs to re-run this.
5. **`TASK_106`'s landing is complete and its own numbers reproduce.** All eight
   corrections in the tree; `contract_sha256` unchanged and correct;
   `spec.md` genuinely had no target for M4; the probe figures reproduce to the
   hundredth in the probe's own convention.

---

# What I did NOT do / am unsure about

* **I did not search for a cheaper in-contract R3 than `u5`.** `1.3148` is the
  ratio of an **upper bound**, over thirteen spellings. If a cheaper one exists
  the ratio moves again, and — because the correction is rank-dependent — not
  necessarily downward.
* **I did not test `u5` against the R4 side's own respellings.** `spec.md`
  already discloses the R4 endpoint as fixed by fiat and `6.00 probe-Ir` above
  the cheapest R4 found; a symmetric treatment would move `tax_u5` down again.
* **I did not put `u5` through Verus, Miri or the gate**, and I make no claim
  that it *should* ship. It is a measurement instrument. In particular I have
  not checked that `g = g - 1` cannot underflow under `debug-assertions=on`
  (the shipped convention is off, and TASK_105 m5 already records that this
  column flips signs on p23).
* **The `τ` mechanism is still not established.** I extended its *domain*
  substantially; I did not disassemble to explain it.
* **I did not re-derive `TASK_105`'s Verus arms (A.1/A.2)** — `TASK_106` re-ran
  them and TASK_105 is itself a review. Out of this task's scope.
* **§B item 1's answer is partly negative-by-construction**: I broke the four
  degeneracies I could *find*. A fifth I did not think of would not show up here.
* **I did not check the `-O0` / `O0d` rows or the C rungs at all.** §A is a
  Rust-side result at one optimisation level.

---

⚠ **PROTOCOL rule 2 running count. Launched from 425, and reconciliation is the
MANAGER's job, not mine — `TASK_114`, `TASK_115` and `TASK_116` were live when I
started and all three have since written reports, so I carry no number of
theirs.** **This branch: 425 + 14.**

1. the spelling term is **`2·dn − 2·recs`**, not a constant — `480.00` at
   `nlow=1`, `0.00` at `nlow=31`, residual `0.0000` over 41 points;
2. the honest fixed-size ratio is **`1.3148`**, not `3.11` and not the manager's
   `7.2` — **the published headline OVERstates, and the manager's direction was
   backwards**;
3. **the regressor inverts**: `dn`/`rank` R² `0.9869` → `0.0001`, `sw` R²
   `0.0132` → `0.9930`;
4. **`R3u5 − R4ship = 2 + 32·recs + 2·sw − 3·rounds + Στ`**, zero fitted
   parameters, `0.0000` over 41 points — finding 38's law with its `dn` term
   gone;
5. **`st_dnunchk − R4ship = 258.00` flat at all 31 ranks** and
   `st_bothunchk == st_dnunchk` exactly — 9d's phenomenon on the **shipped**
   rung for the first time, and the whole rank-dependence located in one read;
6. a fully **safe, in-contract** R3 is cheaper than the same rung with both
   scans and the exchange `get_unchecked` — **8 of 8 ranks** on the shipped rung
   against 9d's 2 of 3 on the probe;
7. ✅ the 8-column design is **rank 8/8** over the 109 points and over the 71
   M+N training points, and `rounds` is independent — the `0.0000` is
   identified (clean negative);
8. ✅ twelve out-of-band points at **max |error| 0.00**, breaking four named
   degeneracies, on a set that rejects three superseded forms (clean negative);
9. `neq = 0` on **102 of 109** points, demonstrated by an out-of-contract strict
   `<`/`>` rung printing the shipped R3's checksum on every band-K blob —
   `required[1]` is unexercised on the law's whole domain;
10. `nelem > SCR` on **0 of 109** points; now tested out of band and the law
    holds at `0.00`;
11. **`k_r3c` is not the shipped R3 shape — `k_r3d` is** — and `NOTES.md` §9b′
    and §9d both publish it as such, while §9b′ also calls `r3d` the shipped
    spelling thirty lines later;
12. `.memory/06-catalogue.md`'s `p23` row asserts *"the tax is not a spelling
    cost inside the declaration"* and its refutation in the same row;
13. ✅ no negative in-contract tax exists up to `m = 64`, `recs = 20`; minimum
    `114.20` (clean negative on a named attack);
14. §D: the pin's **recurring** cost — once written, every `NOTES.md` edit makes
    `sweep_fit.json` STALE and **FAILS** the gate, which is `TASK_106` §4's
    regress with a second turn; a `measurement_sources`-scoped pin avoids it.

→ **439 on this branch.**
