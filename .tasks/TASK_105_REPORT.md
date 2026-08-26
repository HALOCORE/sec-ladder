# TASK_105 — review of `p23-partition`, the 25th pattern. Report.

**Role: research reviewer.** Nothing was fixed. Nothing under `patterns/`,
`.memory/`, `RECAP.md`, `harness/`, `pilot/`, `synthesis/` or `results/` was
written — `git status --porcelain` was empty at start and at end. **I did not run
`harness/check.py`, `harness/measure.py` or `harness/build.py`**, so
`results/gate/` was never rewritten and no `git checkout -- results/gate/` was
needed. All scratch is in `.temp/r105/`; its `NOTES.md` lists every file and its
rebuild command, and every binary has been deleted.

**§A does not land. `p23`'s shipped postcondition is not vacuous, and the row is
not blocked.** But §A's *reasoning* was right for a reason the manager did not
name: the experiment `TASK_101` used to justify dropping the multiset was itself
measuring a vacuous postcondition. Five other findings are `major`.

---

## Verdict

| | |
|---|---|
| blockers | **0** |
| major | **5** (M1–M5) |
| minor | **5** (m1–m5) |
| clean negatives | **6 named attacks that did not land** |
| the row | **ships**, with corrections to `NOTES.md`, `README.md` and the `p23` catalogue row |

---

# §A — the shipped postcondition is NOT vacuous. 9 mutants, 9 failures.

## A.0 the answer, plainly

`p24`'s row is about a postcondition that is a **property** (`is_heap`), which a
zeroing body satisfies. `p23`'s shipped `ensures` is an **exact value equality**:

```
kernel(buf, off, len) -> r    ensures  r == partition_fold(buf@, off, len)
```

`partition_fold` is a deterministic spec function that computes the *exact*
final scratch (`part`) and folds it with an order-sensitive Horner chain over
the full live extent **plus the returned index**. There is no room in it for a
degenerate body: any body that produces different bytes, or a different index,
produces a different `u64`. **That is what carries the anti-vacuity weight in
`p23`, and it is strictly stronger than a multiset clause** — a multiset is
invariant under permutation, and `fold_scr` is not.

⚠ **This is not an argument I am asking anyone to take on trust; it is measured
below.**

## A.1 the mutants, against the SHIPPED `verus.rs`

Generator `.temp/r105/mk_mutants.py` (+ `mk_mutants2.py`), reading
`patterns/p23-partition/verus.rs` read-only and splicing into `.temp/r105/`.
Verified with `./verus_run.py <f>.rs --multiple-errors 8` (single-file, pin
untouched).

**Baseline reproduces**: `m00_baseline.rs`, a byte-identical copy, →
`16 verified, 0 errors`.

| mutant | body | result |
|---|---|---|
| **c01 identity** | spliced through the same path, `diff` vs shipped empty | ✅ **16 verified, 0 errors** |
| **c02 ghost reorder** | cosmetic edit in the replaced region | ✅ **16/0** |
| **c03 shipped, tie `assert` deleted** | the shipped body without the hand-written `assert(walk(..)==walk(..))` | ✅ **16/0** |
| m01 | **zero the live prefix**, report `i = m` | ❌ 13/1 |
| m02 | **zero the live prefix**, report `i = 0` | ❌ 13/1 |
| m03 | **write the pivot everywhere**, report `i = m` | ❌ 13/1 |
| m04 | **swap nothing, return immediately, report `i = 0`** | ❌ 12/1 |
| m05 | correct partition, **fold the index as 0** | ❌ 15/1 |
| m06 | **upward scan only**, no downward scan, no exchange | ❌ 13/1 |
| m07 | delete the invariant conjunct `i == j \|\| scr@[i] > pv` | ❌ 15/1 |
| m08 | delete `j <= m <= SCR` from both inner-scan invariants | ❌ 14/2 |
| m09 | trusted setter's `ensures` weakened to slot-`i` only | ❌ 15/1 |

**Ratio: 9 of 9 mutants fail, 3 of 3 controls verify.** Against `p24`'s **7 of
8** and `p29`'s **3 of 4**, `p23` is the strongest mutation result in the tree.

⚠ **Two soft spots in round 1 were closed rather than reported as passes.**

* Four mutants first failed on the *hand-written* tie `assert`, which a
  degenerate author would simply delete. Re-run with it deleted
  (`*_noassert.rs`): all still fail, now on **`invariant not satisfied at end of
  loop body`** — i.e. on the loop invariant that carries the postcondition, not
  on a stale assertion. The control `c03` shows deleting that `assert` alone
  still verifies `16/0`, so the noassert arm is a real strengthening.
* Three mutants first failed on **`Resource limit (rlimit) exceeded`**, which is
  a timeout and **not a refutation**. Re-run at `--rlimit 200` and (for m04)
  `--rlimit 2000`: all three fail with `invariant not satisfied at end of loop
  body`. **Every one of the nine now fails for a proof reason.**

## A.2 ⚠ the finding §A actually produced: TASK_101's separability EXPERIMENT is invalid

`TASK_101_REPORT` §0, `NOTES.md` §0 and the `p23` catalogue row all rest on:

> *"the partition verifies `6/0` **WITH** the multiset postcondition and `6/0`
> with every multiset clause **DELETED** — it is SEPARABLE."*

Both probes re-run unmodified here and both do give `6 verified, 0 errors`. **But
that is not evidence of separability, because `pA2_no_multiset.rs`'s remaining
postcondition is VACUOUS in exactly `p24`'s sense.** Spliced a degenerate body
into `.temp/t101/pA2_no_multiset.rs` — zero `v[0..m)`, never compare against
`pv`, return `m`:

```
.temp/r105/pB2_no_multiset_DEGENERATE.rs   ->  verification results:: 4 verified, 0 errors
.temp/r105/pB1_multiset_DEGENERATE.rs      ->  3 verified, 1 errors
                                               error: postcondition not satisfied
```

`pB1` is the identical body against `pA`'s postcondition with the multiset
**kept** — the must-fire arm, and it fires. The mechanism is one line: with
`p = m`, `forall k in [p, m)` is vacuous, `forall k < m: v[k] == 0 <= pv` holds
for every `u8` pivot, the tail is untouched, and `p <= m`. **A body that never
looks at the pivot satisfies the whole thing.**

**So `p23` and `p24` are the same shape after all, at the probe level.** The
conclusion `TASK_101` drew (ship the exact functional postcondition, do not
claim a permutation obligation) is **right**, and A.1 shows the shipped
postcondition is sound. The *reason given for it* is not. This is PROTOCOL rule
9's conclusion-versus-mechanism split again: **land the conclusion, strike the
mechanism.**

`severity: minor` for the row (nothing shipped depends on it) but the sentence
is in `.memory/06-catalogue.md` and in `NOTES.md` §0 and should not stand.

**Suggested replacement text, measured:** *"the multiset is not shipped because
`partition_fold`'s exact-value `ensures` already implies it and more. The
`pA`/`pA2` pair does NOT show the multiset is separable — `pA2`'s postcondition
admits a body that zeroes the prefix and returns `m` (`4/0`), and `pA`'s refuses
it (`3/1`, `postcondition not satisfied`)."*

**Answer to the manager's call 1: §A was a real risk, correctly identified, and
the row survives it. The multiset analogy to `p24` was right about the PROBE and
wrong about the SHIPPED postcondition.**

---

# §B — the headline. Two clean negatives and three findings.

Every `Ir` number below comes from **the shipped binaries under
`.temp/build/p23/`**, measured through `controls/sweep_fit.py::kernel_ir`
**imported, not re-implemented**, so the valgrind/`callgrind_annotate` command
is the one that produced the published figures.

**Reproduction test first.** All seven published band-K rows re-measure to
`+0.00`:

```
 nlow      R3         R4      R3-R4    published   delta
    1    4296.41    3590.04     706.37     706.37    +0.00
    4    4355.62    3714.29     641.33     641.33    +0.00
    8    4401.22    3843.33     557.89     557.89    +0.00
   16    4325.67    3912.18     413.49     413.49    +0.00
   24    4018.86    3715.91     302.96     302.96    +0.00
   28    3787.46    3532.46     255.00     255.00    +0.00
   31    3575.50    3348.50     227.00     227.00    +0.00
```

I then measured the other **24** band-K points the shipped tree already contains
and `sweep_fit.py` does not read.

## B.1 ⚠ CLEAN NEGATIVE — the swap-count confound does NOT land, and the result is STRONGER than the report claims

`.temp/r105/band_counts.py` counts, from the **bytes** of the shipped
`sweep-k*.bin` and by replaying the shipped driver loop, the per-call cursor
moves, exchanges and outer rounds. Must-fire arm: its checksum is compared to
`model.py`'s and it refuses to print on a mismatch; a reversed window index is
the negative arm and differs.

The "all fixed" claim **survives reading the bytes**: across all 31 points,
`recs = 8.0`, `mbytes = 256.0`, `stride = 324`, `nwin = 8` — and, a fact nobody
had noticed, **`up + dn = 256.00` exactly at every point**. Total cursor work is
constant; only its *split* between the two scans moves.

The endpoints settle the confound outright:

```
  nlow=1  rank=0.03  up=  8.00 dn=248.00 sw= 7.63 rounds=15.63  ->  R3-R4 = 706.37
  nlow=16 rank=0.50  up=128.00 dn=128.00 sw=64.61 rounds=71.24  ->  R3-R4 = 413.49
  nlow=31 rank=0.97  up=248.00 dn=  8.00 sw= 7.75 rounds=15.50  ->  R3-R4 = 227.00
```

⚠ **At `nlow=1` and `nlow=31` the swap counts are 7.63 and 7.75 — within 1.6% —
and the tax differs by a factor of 3.11.** Swaps peak in the middle where the tax
is middling; they are symmetric about rank 0.5 and the tax is monotone. **The
swap count cannot be the regressor.**

Single-regressor fits over all 31 points (`.temp/r105/band_fit.py`, with a
shuffled-response arm beside each):

```
model             coefficients                       R^2   max|res| | R^2 shuf
rank              +689.5958 -511.5507             0.9869      32.97 |   0.0951
dn (down steps)   +178.0450 +1.9982               0.9869      32.97 |   0.0951
sw (swaps)        +474.1137 -0.9211               0.0132     239.97 |   0.0034
rounds            +480.7213 -0.9277               0.0126     240.15 |   0.0038
dn + sw           +218.0596 +1.9980 -0.9141       0.9999       3.69 |   0.0985
dn + sw + rounds  +242.0000 +2.0000 +2.0000 -3.0000  1.0000     0.00 |   0.1090
```

⚠⚠ **There is an EXACT law, and `NOTES.md` 9c's "do not quote it as a law"
disclaimer can be replaced by one:**

> **`R3 − R4 = 242 + 2·dn + 2·sw − 3·rounds` Ir per call**
> (8 records/call: **30.25 per record + 2 per downward-scan step + 2 per
> exchange − 3 per outer partition round**)

**max|residual| = 0.00 over all 31 points.** Holdout, the must-fire arm: fit on
the 16 odd `nlow`, **predict the 15 even ones — max |error| = 0.0000 Ir/call**;
with the training response shuffled, max |error| = 306.16. The shipped
`187.3 + 16.01·(m − nlow)` with ±30 residuals is that law with the `sw` and
`rounds` terms dropped.

**Answer to the manager's call 2: the tax tracks the DOWNWARD-SCAN STEP COUNT
(at exactly +2.00 `Ir`) and the EXCHANGE COUNT (at exactly +2.00), and rank is a
proxy for both. Swaps are not a confound — they are a separately identified,
second-order term whose sign is the same. The 3.11× swing is carried by `dn`
alone, with swaps held to within 1.6%. ⚠ This is a STRONGER result than the
report claims and it should be said louder.** `severity: n/a — upgrade, not
defect.`

## B.2 the mechanism — the PHENOMENON reproduces exactly; the STATED CAUSE does not survive isolation

I re-derived TASK_101's `k_up`/`k_dn` table from a probe I wrote myself
(`.temp/r105/dnscan.rs`, `-C opt-level=3`, driver copied byte-for-byte from
`.temp/t101/cost23.rs`, measured through `cost23.py`, must-fire arm = all
equivalent kernels print one checksum and `k_wrong` differs):

```
RANK    base(R3)   r4dn(=k_dn)   r4b       TASK_101's k_r3c / k_dn / k_r4b
  3%    4460.00     3972.00     3972.00       4460.00 / 3972.00 / 3972.00
 50%    4492.00     4308.00     4308.00       4492.00 / 4308.00 / 4308.00
 97%    3764.00     3778.00     3778.00       3764.00 / 3778.00 / 3778.00
```

**Independent reproduction, to the instruction, of all nine cells.** The
phenomenon is real: unchecking the downward read alone reaches the fully
unchecked floor. `severity: n/a — confirmed.`

### ⚠ M4 (major). `NOTES.md` 9d's *"the direction of the induction variable decides"* is not what the isolations show

9d names two causes. I built one respelling per cause and neither behaves as 9d
predicts (all at `-O3`, same probe, same checksum):

| kernel | what it changes | rank 3% | 50% | 97% |
|---|---|---|---|---|
| `base` | shipped R3 shape | 4460 | 4492 | 3764 |
| `d2` | **cursor made ASCENDING** (`t` counts up, index `m-1-t`) — removes the descent | **5276** | **6106** | **5077** |
| `d6` | **subtraction removed from the index** (`d == j-1` carried) — keeps the descent | 4444 | 4480 | 3744 |
| `r4b` | unchecked floor | 3972 | 4308 | 3778 |

* Making the induction variable **ascend** does not recover the elision — it
  costs **+816 / +1614 / +1313** more.
* Removing the **unsigned subtraction** at the index recovers **16 / 12 / 20**
  of a **488 / 184 / −14** gap. Essentially nothing.

**Neither named cause survives its isolation.** The correct statement is the
*phenomenon* plus an OPEN mechanism. Given PROTOCOL rule 9's refinement, 9d's
conclusion should be landed and its mechanism sentence marked OPEN, in
`NOTES.md`, in `spec.md`'s `identity[0].why` prose, and in the catalogue row
(which asserts *"the DIRECTION OF THE CURSOR IS THE WHOLE TAX"*).

### ⚠ CLEAN NEGATIVE — no IN-CONTRACT respelling elides the downward check

I audited each variant with **`harness/check.py::spelling_matches` itself**
against `p23`'s own `required`/`forbidden`. Of the six respellings, two are
unambiguously in contract:

| kernel | in contract | rank 3% | 50% | 97% |
|---|---|---|---|---|
| `d1` reslice `&mut scr[..m]`, bound becomes `m` | **YES** | 4740 | 4952 | 4286 |
| `d5` redundant `j <= SCR` hint in the condition | **YES** | 4460 | 4492 | 3764 |
| `d3` `for k in (i..j).rev()` | no (`>= pv` absent) | 4220 | 4796 | 4264 |
| `d4` hoisted local in a `loop` | no (`>= pv` absent) | 4460 | 4492 | 3764 |

**Not one of them is cheaper than `base` at any rank, and `d1` is dearer at
every rank.** So the downward check is **not** a spelling cost inside the
declaration. §B2's named attack does not land; the tax is real.

### ⚠ M5 (major). The published R3-side span's FLOOR is wrong by 150 `Ir`/call

Reproduced NOTES 9b's spans on their own probe band (`NREC=4 NELEM=48 RANK=50
SEED=12345`, `rustc -O -C codegen-units=1`, the header's own convention):

```
r3d 3141.00  r3f 3149.00  r3e 3171.00  r2/r3c 3187.00  r3a 3535.00  r3b 4208.00   <- published R3 span 3141..4208 ✓
r4c 2876.00  r4a 2882.00 (SHIPPED R4)  r4b/r4d 3050.00                            <- published R4 span 2876..3050 ✓
```

Then, from `.temp/r105/dnscan.rs` on the identical band:

```
base 3187.00   d1 3530.00   d5 3187.00   r4b 3050.00
u1   2991.00   <-- a fully SAFE, zero-`unsafe` R3 spelling
```

⚠⚠ **`k_u1` is 150.00 `Ir`/call BELOW the cheapest published in-contract R3, 59
below the in-contract R4 spelling `r4b`, and lands INSIDE the published R4 span
(2876…3050).** It is `base` with the **upward** scan given the downward one's
descending-mirror shape (`g = m - i`, index `scr[m - g]`) — one hour of
searching by a reviewer, on the side the report says was searched with six
spellings.

`k_u1` passes `spelling_matches` on **every** `required` spelling and hits **no**
`forbidden` one. Its admissibility turns on `required[0]`'s *English* — *"the
conjunct `i < j &&` on BOTH inner scan conditions"* — where `k_u1` writes
`m - g < j &&` on the upward scan (semantically identical, `i == m - g`) and
`i < j &&` on the downward one. **No gate stage reproduces that reading, and
`spec.md`'s own `why` says so** (*"which spelling and which rung is a reading,
and no gate stage reproduces it"*). So the finding stands either way:

* **if admissible** → NOTES 9b's *"The R3-side span, cheapest to dearest found in
  contract: 3141.00 … 4208.00"* is false, and the *one real bound* `spec.md`
  claims (`R3ship − R4ship` bounds `inf(in-contract R3) − R4ship`) **overstates
  the safety tax by ≥ 150 `Ir`/call** — because an in-contract R3 sits below two
  of the four R4 spellings;
* **if not admissible** → `p23`'s R3 endpoint is fixed by a pin that only prose
  enforces, which is the same disclosure `.memory/01-ladder.md` demands for a
  fixed-by-fiat R4 endpoint, and `p23` makes it for R4 and not for R3.

### B.3 — lever counts, both sides

Counted from `.temp/t101/cost23.rs`'s source, audited with `spelling_matches`:
**12 of the 14 probe kernels are in contract — 6 R3-side (`r2`, `r3a`, `r3c`,
`r3d`, `r3e`, `r3f`) and 4 R4-side (`r4a`, `r4b`, `r4c`, `r4d`), plus `up`/`dn`.**
`r3b` is out (hits `.position(`/`.rposition(`) and `k_bug` is R1-shaped. **The
counts in the report are correct and the two sides are comparably searched by
count.** They are **not** comparably searched by *result*: M5 shows the R3 side's
floor was not found. `severity: see M5.`

---

# §C — the numbers that look fragile. Three of the four are worse than flagged.

## ⚠ M1 (major). *"eight C cells, eight distinct wrong checksums"* is FALSE of the shipped tree

§C asked *"what exactly is pinned for that input, and does the gate depend on a
layout-dependent value?"* — **nothing is pinned and the gate does not depend on
them.** `model.expected_exit` returns 0, R1's adversarial stdout is *recorded*
under `adversarial/…/stdout` with `diverges: true` and never *required*, and
none of the eight numbers appears in `spec.md`, `model.py`, `gen.py` or either
`results/*.json`. **§C's stated worry is a clean negative.**

The real defect is that **the published numbers are from a superseded gate run**.
Computed from the committed record's bytes:

```
results/gate/p23-partition.json, adversarial-single.bin, the C rungs
  c-gcc    O0/isolated,O3/isolated  exit=0  stdout=2770019511397632
  c-gcc    O3/whole                 exit=0  stdout=2770900832136320
  c-gcc    O0/whole                 exit=0  stdout=2776188756568448
  c-clang  O0/isolated              exit=0  stdout=2762087624749440
  c-clang  O3/whole                 exit=0  stdout=2785001963955328
  c-clang  O0/whole                 exit=0  stdout=2797397313699423
  c-clang  O3/isolated              exit=0  stdout=2812321731838034

8 C cells -> distinct gcc 3, distinct clang 4, DISTINCT OVERALL 7
NOTES.md 7's eight listed values present in the committed record: 1 of 8
```

And the three gate logs the engineer kept show what happened:

| log | gcc distinct | clang distinct | total |
|---|---|---|---|
| `.temp/t101/gate1.log` | 3 | 4 | 7 |
| `.temp/t101/gate2.log` | **4** | 4 | **8** ← the eight published numbers |
| `.temp/t101/gate_final.log` (== the committed record) | **3** | 4 | **7** |

⚠⚠ **`NOTES.md` 7 quotes `gate2`'s eight numbers as the headline and then
describes `gate_final` — the LATER run, and the one that produced the committed
artefact — as *"an earlier gate run … gave gcc only 3 distinct values instead of
4"*. The two runs are the wrong way round, and the shipped tree gives SEVEN.**

The *qualitative* claim survives untouched and is still the sharpest row in the
file: all eight cells exit 0, no signal, every one diverges from the model, and
the values move between builds of identical sources. Only the count and the
numbers are wrong.

**Propagated to:** `patterns/p23-partition/NOTES.md` §7 (×3),
`patterns/p23-partition/README.md:44`, `.tasks/TASK_101_REPORT.md` (×3), and
`.memory/06-catalogue.md`'s `p23` row (*"eight C cells, eight distinct wrong
checksums"*). This is `.memory/03-measurement.md`'s newest lesson —
**compute from the bytes, not from the prose describing them** — landing on the
task that recorded it.

## ⚠ M2 (major). `R1 − R1h` carries the WRONG SIGN in the report and in `.memory/`

From `results/p23-partition.json`, kernel-exclusive `Ir`/call, `-O3 isolated`:

```
small.bin  c-gcc=2816.81  c-gcc-h=2777.71   R1 - R1h = +39.10
large.bin  c-gcc=1650.81  c-gcc-h=1590.47   R1 - R1h = +60.34
small.bin  c-clang=2350.03 c-clang-h=2353.15 R1 - R1h =  -3.12
large.bin  c-clang=1450.11 c-clang-h=1426.97 R1 - R1h = +23.14
```

`NOTES.md` §3 has this right (`+39.10 / +60.34`, headline *"a negative price"*,
i.e. `R1h − R1 < 0`). **`.tasks/TASK_101_REPORT.md` and `.memory/06-catalogue.md`
both write *"`R1 − R1h` is NEGATIVE on gcc (`−39.10`/`−60.34`)"*** — the same
paragraph that quotes clang's `−3.12 / +23.14` with the *opposite* convention.
The conclusion is right, the expression is inverted, and it is inverted on **the
one quantity whose entire point is its sign**. (`TASK_105.md` §C repeats it, so
the manager inherited it.) This is precisely PROTOCOL rule 9's cause: the
`.memory/` row was written from the report, not from the measurement.

## ⚠ M3 (major). The gcc guard's price flips sign TWICE across `p23`'s own rank band, and NOTES §3's mechanism is refuted

§C asked for a mechanism for the negative gcc price. I measured `c-gcc` and
`c-gcc-h` across all 31 band-K points, same pipeline as B.1:

```
GUARD PRICE on gcc = c-gcc-h minus c-gcc, kernel-exclusive Ir/call (m=32, nrec=8, 256 B)
  nlow rank      up      dn      sw  rounds      c-gcc   c-gcc-h   guard price
     1 0.03    8.00  248.00    7.63   15.63    4218.67   4387.15     +168.48
     4 0.12   32.00  224.00   27.23   34.37    4384.68   4457.73      +73.04
     6 0.19   48.00  208.00   39.26   46.12    4488.43   4499.98      +11.54
     7 0.22   56.00  200.00   42.78   50.16    4524.52   4511.65      -12.87
    16 0.50  128.00  128.00   64.61   71.24    4686.41   4541.82     -144.59
    24 0.75  192.00   64.00   48.73   54.84    4462.70   4393.14      -69.56
    27 0.84  216.00   40.00   33.51   40.52    4291.40   4292.84       +1.45
    31 0.97  248.00    8.00    7.75   15.50    3991.88   4131.75     +139.87
```

⚠⚠ **The guard costs +168 at rank 0.03, −145 at rank 0.50 and +140 at rank 0.97.
Two zero crossings.** `small` and `large` sit at mean ranks **0.44 and 0.28** —
both inside the negative window — and `gen.py::_check_residues` *enforces* that
they straddle 0.35, i.e. it enforces that both stay in the middle. So
`NOTES.md` §3's *"⚠⚠ THE SAFETY LINE HAS A NEGATIVE PRICE ON gcc, ON BOTH
INPUTS"* is **a property of the two shipped inputs' pivot ranks, not of the
kernel**, and `p23`'s own headline warning — *"any p23 number quoted without its
rank is quoted without its domain"* — was never applied to its own C-side row.

**And the mechanism given is wrong.** `NOTES.md` §3 says *"gcc can prove the scan
is bounded by `j − i` and rotates the loop"*, which predicts a saving
proportional to **scan steps**. Fitted:

```
model                coefficients                      R^2   max|res|
dn (scan steps)      -58.3744 +0.1992                0.0227     196.65
sw (exchanges)      +194.4765 -5.1970                0.9730      27.19
rounds              +237.6494 -5.3508                0.9739      22.90
dn + sw             +169.0928 +0.1981 -5.1963        0.9955      17.67
```

⚠ **Scan steps explain 2% of the variance; exchanges explain 97%.** The gcc
guard's price is ≈ **+195 flat per call − 5.2 `Ir` per exchange**. The
disassembly agrees in direction (`harness/asm.py`, `-O3 isolated`, whole `kernel`
extent): the `cmp` count is **identical** (14 vs 14) and the guarded kernel has
**four fewer `mov`s**; per *scan iteration* the guarded loops are **bigger**
(up 5 vs 4 insns, down 6 vs 5), so the saving cannot be in the scans at all. It
is in the round/exchange path — R1's downward loop carries the cursor as
`mov %rcx,%rax ; lea -0x1(%rcx),%rcx` with the load at `-0x1(%r9,%rax,1)`, so the
exchange has to reconstruct `j` and `j−1`, while R1h decrements `%r13` in place
and loads at `(%rax,%r13,1)`. **I offer that reading as consistent with the
regression, not as proved; what IS measured is that the published mechanism
predicts the wrong regressor.**

## m5 (minor). The missing `-C debug-assertions=on` column DOES hide a sign flip — at high rank

Built `.temp/r105/dnscan.rs` at `-C opt-level=3 -C debug-assertions=on`:

```
RANK    base (R3, checked)   r4b (unchecked)    R3 - R4
  3%          5192.00            4618.00        +574.00
 50%          6226.00            4892.00       +1334.00
 97%          4157.00            4403.00        -246.00   <- R4 is DEARER
```

⚠ **At rank 0.97 the sign flips: with debug-assertions on, unsafe Rust costs
MORE than safe Rust**, matching the "3 of 3 patterns" warning §3 raised. Also
measured: with debug-assertions on, `r4dn` (downward read unchecked) is
**exactly equal** to `base` at all three ranks — `assert_unsafe_precondition!`
reinstates precisely the check `get_unchecked` was bought to remove. This is a
**probe**, so the intercepts are the probe's; the transferable claim is the sign
flip and its location. The shipped inputs' mean ranks (0.44, 0.28) are in the
non-flipping region, so the absent column probably would not reverse the shipped
headline — but it reverses inside `p23`'s own shipped band, and the disclosure
should say where.

## `contract_sha256` and bands N/X — checked, mostly clean

* **The current hash reproduces from the bytes**: the `slb-contract` block plus
  its trailing newline is 31085 B, sha256
  `8251a6762b1043e4f5b1d7ebeee174a263c3f43467b6befae615e370868816af` — equal to
  the gate record and to `NOTES.md`'s second hash. ✅
* **The first hash `22240ee4…` (30741 B) is not verifiable and `NOTES.md` says
  so correctly.** Edits 2–4 are prose insertions whose exact text is not
  recorded, so the block cannot be reconstructed; the byte delta (+344) is
  consistent with two backticks removed and ~346 bytes of relabelling, which is
  a plausibility check and not a proof. `NOTES.md`'s statement that the
  `git show HEAD: | diff -` command is **vacuous on a new pattern** is correct
  and correctly declines to cite it. ✅
* **bands N and X are genuinely unfitted** — `sweep_fit.py`'s `want_m`/`want_k`
  read bands M and K only, and band M reads 8 of its 47 shipped points and band
  K 7 of its 31. Disclosed. ✅ (I measured band K at all 31; band N and X remain
  unfitted.)
* **the ±30 band-K fit is not quoted as a law anywhere.** `16.01`/`187.3` occur
  in exactly two places (`NOTES.md:529` and `TASK_101_REPORT.md:352`), both with
  the disclaimer attached. ✅ **B.1 now supplies a law that does not need one.**

### ⚠ m1 (minor). The Rule-6 disclosure's HEADLINE contradicts its own table

`NOTES.md` line 27 asserts *"Five edits, **all of them disclosures rather than
weakenings**, and **no `required` … entry changed meaning**"*. Row 1 of the table
immediately below says `required[7]` had backticks removed from `p <= len`, and
that *"removing it makes the declaration **weaker** in exactly one direction:
fewer pins"*.

Both cannot be true. Under the declaration's own named-spelling standard,
backticks are the trigger — `harness/check.py`'s own selftest case reads *"an
entry with no backticks pins nothing and reports nothing"* — so removing them
un-pins a spelling, which is a `required` entry that changed meaning and a
weakening. **The edit itself is defensible** (the gate reported the pin as
matching 0 of 2 C rungs). **The headline is not**, and PROTOCOL rule 6 is
explicit that a false disclosure is worse than the thing it describes, because a
disclosure is what a reviewer trusts *instead of* re-checking. This is also
rule 13's shape: the summary line asserts what the body underneath refutes.

---

# §D — ⚠ CLEAN NEGATIVE. The correction landed, in FOUR places, and nothing derived still assumes the false version

The `i < m` / `j > 0` *"safe, and WRONG"* retraction is present and correctly
framed in:

1. `c/kernel_hardened.c:9–20` — states the alternative is **EQUIVALENT, not
   weaker**, names the missed invariant, cites the control;
2. `controls/guard_variants.c:17–26` — *"THE ANSWER IS NOT THE ONE THIS FILE WAS
   WRITTEN TO SHOW"*;
3. `controls/guard_equiv.py:6–24` — **a fourth place the report did not count**;
4. `NOTES.md` §8.

Every occurrence of the string is a retraction; **there is no surviving
assertion of the false claim anywhere in `patterns/`, `.memory/` or the report**.
No derived sentence assumes it: `spec.md`'s `required[0]` and `why`(1) pin the
*spelling* and speak only of deleting the conjuncts entirely, which is R1 and is
correct.

⚠ One loose end, `severity: minor` and not counted: `c/kernel_hardened.c` says
*"`../spec.md` pins a SPELLING here and not a semantics, **and it says so**"*.
`spec.md` says so only through the generic NAMED-SPELLING STANDARD paragraph
shared by six patterns; there is no p23-specific sentence at `required[0]`. The
claim is true by inheritance, not by local text.

**Bonus check, from the bytes.** `kernel_hardened.c`'s opening claim *"the only
differences are the two `i < j &&` conjuncts"* is exactly right — a
comment-stripped, whitespace-normalised diff of the two C kernels is **two lines,
both the conjunct, 53 code lines each side**.

---

# Reviewer-checklist items checked and clean

* **Verus soundness.** `grep 'assume\|external_body\|external\b\|assume_specification'`
  → **5 hits, all `#[verifier::external_body]`, all justified in a comment and in
  `spec.md`'s `unsafe_justifications`. No `assume`, no `assume_specification`, no
  bare `external`.** `NOTES.md` §6's TCB tally of 5 (3 contract-bearing) is
  **accurate on a recount**.
* **R5 exec == R4 exec.** `harness/asm.py`: `raw_bytes` equal `True`,
  `md5_fn 43acbc727fc6…` both, 157 insns / 647 B both, `identity_level` →
  **`exact`**. No drift. ✅
* **Are the `requires` satisfiable / is the kernel dead?** One structural clause
  (`off + len <= buf@.len()`), discharged at the real call site inside verified
  `main`; the gate evaluated it on 80 048 calls across 9 inputs. Not vacuous.
* **Deterministic metrics primary?** Yes; the only wall-clock statement in
  `NOTES.md` is the disclaimer that R4/R5 read 519 vs 554 ns for a
  byte-identical kernel and that no claim rests on it. ✅
* **Any C-vs-Rust claim without a clang column?** No — `NOTES.md` 9a carries
  both and flags the sign dependence. ✅
* **Constant-folding / data really from the file?** `off` is derived from the
  previous call's result through `(acc * nwin) >> 64`; five backward branches in
  every C cell and 6–7 in every Rust cell (`has_loop: true`, `n_backward_branches`
  5–11); no `vector_regs` anywhere. ✅
* **PROTOCOL rule 1's loop check** reports no pattern missing from RECAP's
  findings — but ⚠ it passes for `p23` only because another finding's prose names
  `p23` at `RECAP.md:890`. **`p23` still has no finding of its own**; step 4 of
  the loop is owed after this review (manager's job, and due now).

---

# The three calls the manager was least sure of

**1. Was §A a real risk or a manager panic?** ⚠ **A real risk, correctly
identified — and the analogy to `p24` was right about the probe and wrong about
the shipped row.** `p23`'s shipped `ensures` is an exact-value equality and
refuses all nine mutants including all four degenerate bodies §A named (9/9,
against `p24`'s 7/8 and `p29`'s 3/4). **But `pA2`'s postcondition — the one whose
`6/0` was published as proof that the multiset is separable — IS vacuous**: a
body that zeroes the prefix and returns `m` verifies `4/0` against it and `3/1`
against `pA`. **So §A found a defect, just not in the shipped rung.** Not a
blocker; the mechanism sentence in `NOTES.md` §0 and in the catalogue row should
be struck and replaced with A.2's text.

**2. Does the shape-not-size headline survive the swap-count confound?** ⚠ **Yes,
and it survives in a stronger form than the report claims — the manager's
suspicion is REFUTED by the endpoints.** At `nlow = 1` and `nlow = 31` the swap
counts are 7.63 and 7.75 while the tax is 706.37 and 227.00. Swaps are a
separately identified **+2.00 `Ir` per exchange** term, not a confound. The full
31-point band yields an exact identity — **`R3 − R4 = 242 + 2·dn + 2·sw −
3·rounds`, max residual 0.00, holdout error 0.0000** — replacing the ±30 fit that
`NOTES.md` says must not be quoted as a law. **Say it louder, and drop the
disclaimer.** ⚠ **But the mechanism sentence attached to it (9d, "the direction
of the induction variable decides") does not survive isolation (M4), and the
gcc-side sign claim is rank-dependent in exactly the way the headline warns about
and does not apply to itself (M3).**

**3. Was `p23` worth building at all?** ⚠ **Yes — but on two of finding 37's
three limbs, not three, and the bar is not what needs correcting.** Limb 1 (a new
operator: the guard compares two loop variables) and limb 2 (a new source of the
bound: each cursor's bound is the other cursor, and both move) are true, checkable
from the sources, and unique in the tree. **Limb 3 — "a new reason the check is
or is not elided" — ships a PHENOMENON with an unverified CAUSE**: the phenomenon
reproduced exactly under my own probe, but the cause named for it fails both of
its isolations. Limb 3 should be restated, not withdrawn — an elision asymmetry
between two scans of the same array, with an open cause, is still a new entry in
the list. **Finding 37's bar is fine; what this row shows is that the bar needs a
companion rule** — *a limb that claims a new **reason** owes an isolation, not
just a measurement.* That is PROTOCOL rule 12's "ask for the mechanism" plus
rule 9's "mechanisms need their own evidence", and `p23` is the case that shows
the two combine.

---

# Corrections owed (manager applies; I fixed nothing)

| # | file | what |
|---|---|---|
| M1 | `NOTES.md` §7 (×3), `README.md:44`, `.memory/06-catalogue.md` p23 | **seven** distinct values over eight cells, gcc 3 / clang 4; quote the committed record's numbers; the "earlier run" sentence has the two runs reversed |
| M2 | `.memory/06-catalogue.md` p23 (and any future citation) | `R1 − R1h` on gcc is **+39.10 / +60.34**; the *guard's price* is −39.10 / −60.34 |
| M3 | `NOTES.md` §3, catalogue row | the negative gcc price holds only for rank ≈0.22–0.84; it is **+168** at rank 0.03 and **+140** at 0.97. Replace the trip-bound mechanism: scan steps R²=0.023, exchanges R²=0.973 |
| M4 | `NOTES.md` §9d, `spec.md` `identity[0].why`, catalogue row | land the phenomenon, mark the cause **OPEN**: an ascending respelling is dearer and removing the subtraction moves 12–20 `Ir` |
| M5 | `NOTES.md` §9b | the R3-side span floor is not 3141.00; an in-contract-by-the-gate spelling reaches 2991.00, inside the published R4 span |
| A.2 | `NOTES.md` §0, catalogue row | strike *"the multiset is separable"*; `pA2`'s postcondition is vacuous |
| m1 | `NOTES.md` Rule-6 section | the headline contradicts table row 1: `required[7]` **did** change meaning and the declaration **is** weaker by one pin |
| m5 | `NOTES.md` §10 | the debug-assertions column flips sign at rank 0.97 (probe-measured) |

---

⚠ **PROTOCOL rule 2 running count.** Carried forward from **343**, and
reconciliation is the manager's job, not mine — I was the only agent running, so
none is owed. **+13** for this review: `pA2`'s postcondition shown vacuous; the
shipped R5 shown non-vacuous at 9/9; the eight-distinct-checksums claim shown
false of the shipped tree (7 of 8, and the two gate runs reversed); the
`R1 − R1h` sign inverted in the report and in `.memory/`; the gcc guard price
shown to flip sign twice across `p23`'s own rank band; `NOTES.md` §3's trip-bound
mechanism refuted (2% vs 97% of variance); the exact four-term identity
`242 + 2·dn + 2·sw − 3·rounds` with a 0.0000 holdout; the swap-count confound
refuted at the endpoints; `NOTES.md` §9d's direction mechanism refuted by two
isolations; an in-contract R3 spelling found 150 `Ir` below the published R3
floor and inside the R4 span; the debug-assertions sign flip measured at rank
0.97; the Rule-6 disclosure headline shown to contradict its own table; and
independent reproduction of the `k_up`/`k_dn` mechanism table and of all seven
published band-K rows to `+0.00`. → **356**.
