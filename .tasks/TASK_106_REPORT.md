# TASK_106 — landing `TASK_105`'s corrections into `p23-partition`. Report.

**Role: research engineer.** All eight corrections are landed. Scratch is
`.temp/t106/`; its `NOTES.md` lists every file and its rebuild command, and every
binary has been deleted. **No `git add`, no `git commit`, no history-mutating
git.** `.memory/` and `RECAP.md` were not touched. `harness/` was not modified.

⚠⚠ **Four things in the task file did not survive contact with the record.** One
reverses the row's central number (§1), one turns the law it asked me to land
into a local one (§2), one names a file that has no such text (§3), and one is a
prescription that **cannot be carried out at all** (§4). They are first, because
the manager writes RECAP finding 38 from this. **Of the three calls the task file
named: call 1 — the one it refused to decide — came back YES and against the
headline; call 3 came back NO; call 2 was an instruction and I followed it, plus
one measurement of my own that strengthens it.**

---

## §1 ⚠⚠ M5 — **the `2991.00` spelling IS admissible, and p23's published R3 floor was wrong**

**This is the call the task file said must not be resolved by choosing the
reading that keeps the headline. It was resolved by measurement, and it goes
against the headline.**

`k_u1` (TASK_105's find) is **not** admissible: `required[0].rust` asks for the
conjunct `` `i < j &&` `` **on both inner scan conditions**, and `k_u1` spells its
upward one `m - g < j &&`. That reading stands. **But it decides nothing**,
because I built `k_u5` — `k_u1` **verbatim with `i < j &&` restored as a
redundant leading conjunct**:

```rust
let mut g: usize = m - i;
while i < j && m - g < j && scr[m - g] <= pv { g -= 1; }
i = m - g;
while i < j && scr[j - 1] >= pv { j -= 1; }
```

`i` does not move inside that scan and the outer `while i < j` has just tested
it, so the conjunct is a tautology at every evaluation. Its shape is `d5`'s (the
redundant `j <= SCR` range hint TASK_105 audited as in contract).

| test | result |
|---|---|
| `harness/check.py::spelling_matches`, all 8 `required` (rust) | **matches every one** |
| `forbidden` — all six entries | **no hit** |
| `required[0]`'s **English** — the conjunct on BOTH inner scan conditions | **satisfied, literally** |
| `harness/asm.py` vs `k_u1`, `-C opt-level=3` | **`md5_norm da08af26d9b1` on both, 249 instructions each — the SAME OBJECT CODE** |
| checksum vs every other kernel at ranks 0/3/50/97/100 | equal; `k_wrong` differs at all five |

**Marginal `Ir`/call, `NREC=4 NELEM=48 SEED=12345`, `rustc -O -C codegen-units=1`,
inline mode `isolated`, debug-assertions off — `NOTES.md` 9b's own probe band:**

```
spelling                                       in contract?  rank 0   rank 50  rank 100
base = k_r3c, the shipped R3 shape             gate+English  3140.30  3187.00  2563.70
u1   descending mirror, guard `m - g < j &&`   gate ONLY     2756.30  2991.00  2563.70
u5   u1 + a REDUNDANT LEADING `i < j &&`       gate+English  2756.30  2991.00  2563.70
u2   two cursors, guard `i < j &&`, ix `m - g` gate+English  3152.30  3432.00  2951.70
u3   identity subtraction `scr[m - (m - i)]`   gate+English  3140.30  3187.00  2563.70
u4   u2 with the downward scan mirrored too    gate+English  3161.30  3719.00  2944.70
r4b  both scans unchecked (R4 side)            gate+English  2768.30  3050.00  2575.70
```

**Consequences, all at the median band (rank 50):**

* the cheapest in-contract R3 is **2991.00**, not 3141.00 — **the published floor
  was 150.00 `Ir`/call too high**;
* it is **59.00 below** the in-contract R4 spellings `r4b`/`r4d` (3050.00) and
  lands **inside** the published R4 span, so **p23's R3-side and R4-side spans
  OVERLAP**. It is still above the shipped R4 (2882.00) and `r4c` (2876.00);
* `spec.md`'s **one real bound** is **not falsified** — it is an upper bound and
  `inf ≤ R3ship` — but it is **loosened**: `R3ship − R4ship = 259.00` against
  `inf(found) − R4ship ≤ 109.00`, so **at least 150.00 of the published safe-side
  figure is spelling and not safety**;
* ⚠ **the size of the correction is itself rank-dependent** — against the shipped
  spelling `r3d` (3094.30 / 3141.00 / 2517.70), `u5` is **338.00 below at rank 0,
  150.00 below at rank 50, and 46.00 ABOVE at rank 100.** There is no single
  number for "how wrong the floor was".

⚠ **A second, independent error in the same line that nobody had flagged: the
span's TOP endpoint was also wrong.** `4208.00` is `r3b`, the
`.position(`/`.rposition(` spelling — which is `forbidden`. Audited with
`spelling_matches` over every `k_*` in `.temp/t101/cost23.rs`
(`.temp/t106/audit_cost23.log`): **`r3b` hits both `forbidden` entries and is
out.** The corrected span over the **twelve** in-contract spellings now searched
is **2991.00 … 3719.00** (`u5` … `u4`).

✅ **Clean negative, and it is the interesting half:** `u2`, `u3` and `u4` — the
three other in-contract ways I found to give the upward scan a descending,
subtracting index — are **all dearer than or equal to `base`** (3432.00 / 3187.00
/ 3719.00 against 3187.00). **Only the redundant-conjunct route recovers the
saving**, and it recovers it exactly. ⚠ **So the operative fact is not "the
declaration excludes the cheap spelling" — it is that a semantically-null
respelling walks straight around the declaration and the declaration cannot
tell.**

---

## §2 ⚠⚠ The 9c law the task asked me to land is **band-K-only**, and off band K it is wrong by up to 480 `Ir`/call

The task said to re-derive `R3 − R4 = 242 + 2·dn + 2·sw − 3·rounds` before
landing it, and asked whether it generalises. **It reproduces exactly on band K
and it does not generalise.**

I measured **all 109 shipped points** — band K's 31, band M's 47, band N's 24,
band X's 5, and `small`/`large` — for `safe_tuned`, `unsafe`, `c-gcc` and
`c-gcc-h` at `-O3 isolated` through `controls/sweep_fit.py::kernel_ir`
**imported**, with per-call `up`/`dn`/`sw`/`rounds`/`recs`/`mbytes` counted from
each blob's **bytes** by replaying the shipped driver loop.

```
                                            max |error|, Ir/call
form                                    K       M       N       X    small/large
242 + 2dn + 2sw - 3rounds  (TASK_105) 0.00   32.00  480.00  121.00   152.00
30.25recs + 2dn + 2sw - 3rounds       0.00   32.00    4.00   30.25    31.00
2 + 30recs + 2dn + 2sw - 3rounds + t  0.00    0.00    0.00    0.00     0.00
```

⚠ **The band-K spelling mispredicts the two SHIPPED matrix inputs by up to
152.00 `Ir`/call.** Band N re-fits to a *different* exact law of the same shape
(`2.00 + 5.75·dn + 2·sw − 3·rounds`, R²=1.0000) because band N holds `m = 16`,
making `dn ≡ 8·recs`. **Two exact laws that disagree is what a collinearity looks
like from inside one band.**

**The closed form that does hold, and it is the deliverable:**

> ### `R3 − R4 = 2 + 30·recs + 2·dn + 2·sw − 3·rounds + Σ_records τ(m mod 4)`
> ### `Ir` per call, `τ = {0 → 0, 1 → 2, 2 → 3, 3 → 4}`
> **max |residual| 0.0000 over all 109 shipped points**, response spanning
> 41.75 … 956.40 `Ir`/call. Conditions: `-O3 isolated`, inline mode `isolated`,
> kernel-exclusive `Ir` from the shipped `safe_tuned`/`unsafe` binaries,
> debug-assertions off.

**Holdout, the must-fire arm:** fit the eight coefficients on **bands M and N
only (71 points)** — they come out `+2.0000, +30.0000, +2.0000, +2.0000,
−3.0000, +2.0000, +3.0000, +4.0000` — then **predict the 38 points nobody
fitted** (band K's 31, band X's 5, `small`, `large`): **max |error| 0.0000
`Ir`/call.** With the training response shuffled, **6050.96**.

⚠ **The `τ` term is new and neither band could see it.** Band M's residual under
the per-record form is not noise: over 47 consecutive points it is exactly
**0 / 16 / 24 / 32** as `m mod 4` is **0 / 1 / 2 / 3**, at `recs = 8` — a
per-record 0 / 2 / 3 / 4 `Ir`. Band K sits at `m = 32` and band N at `m = 16`,
both `≡ 0 mod 4`; and `sweep_fit.py` reads band M at `m = 2, 4, 8, 16, 24, 32,
40, 48`, **seven of them multiples of four**.

✅ **`up + dn == mbytes` EXACTLY at all 109 points** — the generalisation of
TASK_105's band-K `up + dn = 256.00`. Total cursor work is the live byte count;
only its split moves.

✅ **Swap-count confound REFUTED, reproduced:** at `nlow = 1` and `31` the swap
counts are **7.63 and 7.75 (within 1.6%)** while the tax differs **3.11×**.
Single-regressor R² over the 31 band-K points: `dn` 0.9869, `rank` 0.9869,
**`sw` 0.0132**, `rounds` 0.0126.

---

## §3 ⚠ M4's `spec.md` half had **no target**, so `contract_sha256` did **not** move

The task file says M4 touches `NOTES.md` §9d **and `spec.md`'s
`identity[0].why`**, and warns this moves the hash. **It does not.**
`identity[0].why` is about `R4 ≡ R5` byte-identity and says nothing about
elision. I parsed the whole `slb-contract` block and grepped every leaf:
`grep -i 'direction|induction variable|elid|elision|whole tax|safety tax|monotonic'`
over `spec.md` returns **nothing about the mechanism**, inside the fence or out.
The claim lives in `NOTES.md` §0 and §9d and in `README.md`, all three of which I
corrected.

**Rule 6 disclosure, before and after, computed from the bytes:**

```
BEFORE  slb-contract block  31085 bytes  sha256 8251a6762b1043e4f5b1d7ebeee174a263c3f43467b6befae615e370868816af
AFTER   slb-contract block  31085 bytes  sha256 8251a6762b1043e4f5b1d7ebeee174a263c3f43467b6befae615e370868816af
        == the gate record's contract_sha256, before and after.  `spec.md` was NOT edited.
```

⚠ **I also re-read the hashed `why` against my own measured numbers**, per rule
6's addendum. Its figures (219 insns / `5dca9d30a43c`; 4208.00 / 3141.00 at the
median pivot; 2812.30 / 3094.30 at the minimum-rank pivot; `6.00 probe-Ir/call`)
are all statements about *the shipped spelling* or *`r3b`* and are all still
true; §1's correction is to the **span**, which `idiom.why` states only as a
convention (*"Beside it goes the R3-SIDE SPAN"*) and not as p23 numbers. **So
nothing in the fence is refuted and I made no edit there.** ⚠ **If the manager
wants the overlap recorded inside the declaration, that is a deliberate
`contract_sha256` move and should be its own decision, not mine.**

---

## Did

| # | file | what landed |
|---|---|---|
| **M1** | `NOTES.md` §7 (table row + the whole "one-element row" block), `README.md` harm row | see §4 below — **the correction the task asked for is itself unstable, and I landed the invariant instead** |
| **M2** | `NOTES.md` §3 | the guard's price is **−39.10 / −60.34**, i.e. **`R1 − R1h = +39.10 / +60.34`**; both quantities now named beside every figure. Substance kept: hardened gcc IS cheaper and smaller |
| **M3** | `NOTES.md` new §3a | the 31-point guard-price table, the two zero crossings, the refuted trip-bound mechanism, the disassembly reading **as a candidate** |
| **M4** | `NOTES.md` §0 limb 3 and §9d, `README.md` | phenomenon landed and **upgraded**; cause marked **OPEN**; `spec.md` untouched (§3) |
| **M5** | `NOTES.md` §9b + new §9b′, `README.md` | §1 |
| **A.2** | `NOTES.md` §0 | *"the multiset is separable"* struck; the 9/9 mutation result landed with its failure-reason breakdown |
| **m1** | `NOTES.md` rule-6 section | headline corrected: **one** of the five edits is a weakening |
| **m5** | `NOTES.md` §10 | the debug-assertions column, the sign flip and its location |
| **+9c** | `NOTES.md` §9c′ and §9c″ | §2 |

## Evidence

**Gate, run after every edit:**

```
$ timeout 3000 harness/check.py p23
check.py: PASS
    32/32 cells built
    idiom forbidden: 0 hit(s) over 12 forbidden spelling(s)
    !! [tcb-unsafe] verus.rs `scr_set_unchecked` ... spec.md justifies it   (the known 4th-instance false positive)
    note: adversarial-single.bin/c-gcc:   opt/mode variants disagree (3 or 4 distinct behaviours -- see §4)
    note: adversarial-single.bin/c-clang: opt/mode variants disagree (4 distinct behaviours)
contract_sha256 = 8251a6762b1043e4f5b1d7ebeee174a263c3f43467b6befae615e370868816af   (UNCHANGED)
```

The gate was re-run after **every** edit to `NOTES.md`/`README.md`. Closing
check, so the manager is committing a record that describes the tree:

```
MATCH  patterns/p23-partition/NOTES.md
MATCH  patterns/p23-partition/README.md
MATCH  patterns/p23-partition/spec.md
contract_sha256: 8251a6762b1043e4f5b1d7ebeee174a263c3f43467b6befae615e370868816af
verdict: PASS      ALL SOURCE HASHES MATCH
```

**Verified by hash, not asserted.**

**M1, from the committed record's bytes (`.temp/t106/m1_record.py`):**

```
adversarial-single.bin, C rungs:  c-gcc 4 cells 3 distinct, c-clang 4 cells 4 distinct
8 buggy C cells -> DISTINCT OVERALL: 7          model stdout: 2705683097473408
NOTES.md 7's eight published values present in the record: 1 of 8
gate1.log   15:44  gcc 3  clang 4  total 7
gate2.log   16:01  gcc 4  clang 4  total 8   <- the eight numbers NOTES.md published
gate_final  16:07  gcc 3  clang 4  total 7   <- mtime == results/gate/p23-partition.json
cells that took more than one value across the three runs: 8 of 8
```

⚠ **That output was taken while `results/gate/p23-partition.json` was still
TASK_101's.** Re-running `m1_record.py` now reads whatever the latest gate run
wrote — **which is the finding, not a defect in the script.** The three
`.temp/t101/gate*.log` lines are stable because logs do not get rewritten.

**M2, from `results/p23-partition.json` (`.temp/t106/m2_record.py`):**

```
small.bin   R1 - R1h:  gcc +39.10  clang  -3.12        guard price R1h-R1: gcc -39.10  clang +3.12
large.bin   R1 - R1h:  gcc +60.34  clang +23.14        guard price R1h-R1: gcc -60.34  clang -23.14
small.bin  R2-R4 +350.69  R3-R4 +305.74  R2-R3 +44.95  R4-R5 +0.00  gcch-R4 +390.77  clangh-R4 -33.79
large.bin  R2-R4 +531.17  R3-R4 +443.55  R2-R3 +87.62  R4-R5 +0.00  gcch-R4  +91.50  clangh-R4 -72.00
```

Every published shipped figure reproduces from the record to the hundredth.

**M3, over all 31 band-K points (`.temp/t106/band_all.py`, `fit.py`):**

```
 nlow rank      dn      sw  rounds      c-gcc   c-gcc-h   guard price
    1 0.03  248.00    7.63   15.63    4218.67   4387.15     +168.48
    7 0.22  200.00   42.78   50.16    4524.52   4511.65      -12.87
   16 0.50  128.00   64.61   71.24    4686.41   4541.82     -144.59
   27 0.84   40.00   33.51   40.52    4291.40   4292.84       +1.45
   31 0.97    8.00    7.75   15.50    3991.88   4131.75     +139.87
zero crossings: between nlow 6 (+11.54) and 7 (-12.87); between 26 (-36.74) and 27 (+1.45)
regressors:  dn R^2=0.0227 max|res| 196.65 | sw R^2=0.9730 27.19 | rounds R^2=0.9739 22.90
             dn+sw R^2=0.9955 17.67      ->  price ~ +195 flat - 5.2 Ir per exchange
band X (mixed): +46.91 +61.84 +61.23 +60.20 +19.57   -- POSITIVE at every point
```

⚠ **The band-X column is mine and is new**: the review measured band K only. **On
p23's own mixed band the gcc guard's price is positive everywhere**, which
strengthens M3 — the negative sign is not merely rank-dependent, it is absent
from the one band that mixes record shapes.

**M4, reproduced from my own build (`.temp/t106/u2scan_O3.log`), `-C opt-level=3`,
NREC=8 NELEM=32, ranks 3/50/97:**

```
base                     4460 / 4492 / 3764
d2  (cursor ASCENDING)   5276 / 6106 / 5077   -> +816 / +1614 / +1313 DEARER
d6  (subtraction gone)   4444 / 4480 / 3744   -> recovers 16 / 12 / 20 of a 488 / 184 / -14 gap
u5  (the UPWARD scan given that same shape)
                         3948 / 4230 / 3749   -> 512 / 262 / 15 CHEAPER, and BELOW r4b at two ranks
r4dn 3972 / 4308 / 3778  ==  r4b 3972 / 4308 / 3778
```

⚠ **The `u5` row is mine and it is the sharpest of the three.** 9d blamed the
downward scan's descending cursor and unsigned subtraction for the *lost*
elision; giving the **upward** scan exactly that shape makes it **cheaper**, and
at two of the three ranks **cheaper than the fully unchecked kernel.** The two
isolations TASK_105 ran say the named causes do not produce the effect; this one
says they produce the opposite effect on the other scan.

✅ **Upgrade to 9d's phenomenon, and it is stronger than `Ir` equality:**
`harness/asm.py` gives `k_r4dn` and `k_r4b` **the same relocation-masked
disassembly — `md5_norm 5b245ea73c9a`, 251 instructions each.** Unchecking the
downward read alone does not *approach* the fully-unchecked floor, it **is** it.

**m5, `-C opt-level=3 -C debug-assertions=on`, my own build
(`.temp/t106/u2scan_O3da.log`):**

```
RANK    base (R3, checked)   r4b (unchecked)    R3 - R4
  3%          5192.00            4618.00        +574.00
 50%          6226.00            4892.00       +1334.00
 97%          4157.00            4403.00        -246.00   <- R4 is DEARER
r4dn == base EXACTLY at all three ranks (5192 / 6226 / 4157)
```

**A.2, re-run (`.temp/t106/verus_a2.log`, `./verus_run.py`, single-file, pin
untouched):**

```
.temp/t101/pA_hoare_nested.rs             ->  6 verified, 0 errors
.temp/t101/pA2_no_multiset.rs             ->  6 verified, 0 errors
.temp/r105/pB2_no_multiset_DEGENERATE.rs  ->  4 verified, 0 errors   <- pA2's postcondition is VACUOUS
.temp/r105/pB1_multiset_DEGENERATE.rs     ->  3 verified, 1 errors   error: postcondition not satisfied
patterns/p23-partition/verus.rs           -> 16 verified, 0 errors
.temp/r105/c01_identity.rs                -> 16 verified, 0 errors   (diff vs shipped verus.rs: EMPTY)
.temp/r105/m04_nothing_noassert.rs --rlimit 2000 -> 12 verified, 1 errors
                                             error: invariant not satisfied at end of loop body
```

**The 9 mutants' failure REASONS, recounted from the logs** (this is what makes
9/9 worth quoting, and it is not in the review's summary): **7 × `invariant not
satisfied at end of loop body`, 1 × `precondition not satisfied`, 1 × `assertion
failed`. No timeouts.**

---

## §4 ⚠⚠ Problems — M1 as specified is **impossible**, and I found out by doing it

The task said: *"Quote the committed record."* I did, and then ran
`harness/check.py p23` as the definition of done. **The gate rebuilt the C cells
and moved seven of the eight checksums**, so the sentence I had just corrected
was stale again before I finished. I then deleted the transcription and ran the
gate again — **and that run, the same command on the same sources minutes later,
moved all eight AND changed the distinct count**:

```
run 3 (TASK_101's committed record)   gcc 3 / clang 4 / 7 overall
run 4 (TASK_106 gate)                 gcc 3 / clang 4 / 7 overall   -- 7 of the 8 values moved
run 5 (TASK_106 gate)                 gcc 4 / clang 4 / 8 overall   -- all 8 moved again
run 6 (TASK_106 gate)                 gcc 4 / clang 4 / 8 overall   -- moved again
... and every further run of this task moved them again.
```

⚠⚠ **Those are the same command, on the same sources, in the same task, minutes
apart, and they disagree on the distinct COUNT.** So *"seven distinct"* — the
correction the task file asked for, and the one TASK_105 measured — **is not a
stable fact either.** `NOTES.md` now gives the logged-run history table and puts
**no number** on the run-dependent lines, so the next run cannot make it wrong.

**The regress is structural and cannot be broken:** `NOTES.md` is hashed into the
gate record's `source_sha256`, so **every edit to `NOTES.md` forces a gate
re-run**, and **every gate re-run moves these eight values**. The last gate run
always postdates the last edit to the sentence describing it.

**So I did not land the correction as specified. I landed the invariant and
deleted the transcription**, with a history table of the logged runs (which is
about past runs and therefore cannot go stale) and an explicit statement of why
no values appear. What `NOTES.md` §7 now publishes:

```
8 buggy C cells on adversarial-single.bin, all four (opt x mode) each compiler
  exit 0, no signal, no sanitizer output in the plain build      -- every run
  all 8 diverge from the model's 2705683097473408                -- every run
  both hardened C rungs print the model's value in all 8 cells   -- every run
  the number of DISTINCT values                                  -- RUN-DEPENDENT
  the per-cell values                                            -- MOVE EVERY RUN
```

⚠ **I put no number on the two run-dependent lines**, precisely because run 5
falsified the number I had just written there. The logged-run history sits in a
table beside it; the next run is free to differ and the prose would not need
editing. **Replacing one over-confident number with another is how this row got
here.**

⚠ **This also means `results/gate/p23-partition.json` is MODIFIED in the working
tree and the manager will commit it.** That is unavoidable and correct: the
committed record's `source_sha256` for `NOTES.md`/`README.md` would otherwise be
stale. `git checkout -- results/gate/` would have restored the old checksums at
the price of a lying source hash, so I did not.

## Other problems

* The first `k_u5` I generated carried a **stale `i`** in its guard, which is a
  different program (the upward scan runs unbounded — it is R1's bug). **The
  probe's checksum must-fire arm caught it at rank 100 with a panic, after it had
  agreed with every other kernel at ranks 0 and 50.** Regenerated and re-measured;
  every number in §1 is from the corrected file. ⚠ **A must-fire arm at one rank
  would have passed this.**
* `harness/asm.py`'s `Kernel` exposes `backward_branches`/`md5_norm` as attributes
  and has no `n_backward_branches` / `.get()`; three probe scripts failed on that
  before I read the class. Not a defect, just an undocumented shape.

## Unsure / not done

* **I did not touch `c/kernel*.c`, any rung `.rs`, `model.py` or `inputs/gen.py`.**
  I grepped all of them for the refuted claims (`3141.00`, `187.3`, `16.01`,
  `4208.00`, `elid*`, `multiset is`, `induction variable`, and the eight
  checksums) and **found no hit that a correction would need to touch**, so no
  measurement-hashed file was edited and `results/p23-partition.json` is not
  stale. The one `elision` hit in `verus.rs` is about fold elision and unrelated.
* **I did not edit `spec.md`** — see §3. `contract_sha256` is unchanged.
* **I did not edit `controls/sweep_fit.py`.** Its docstring still describes the
  two-term records/bytes fit, which is an accurate description of what it does;
  the 109-point sweep lives in `.temp/t106/band_all.py`. ⚠ **Adjacent work I am
  reporting rather than doing: `sweep_fit.py`'s `want_m`/`want_k` still read 8 and
  7 points, and running it at every point is a two-line change that would make the
  τ term visible from `controls/` rather than from `.temp/`.**
* **`τ(m mod 4)`'s mechanism is not established.** I know it is per-record and
  periodic in `m mod 4` with values 0/2/3/4; I have not disassembled to say
  whether it is the `copy_from_slice` tail, the `iter().fold` tail, or both.
  **Landed as a measured term, not as an explanation.**
* **M3's replacement mechanism is landed as a CANDIDATE**, exactly as instructed.
  The regressor (`sw`, R²=0.9730) is measured; the `mov`/`lea` reading is
  TASK_105's and I did not re-derive it. What is mine and measured is that the
  published mechanism predicts the wrong regressor.
* **2991.00 is not claimed to be the infimum.** It is the cheapest of twelve
  in-contract spellings now searched. This pattern has published a wrong floor
  once; I have written "cheapest found" into the file rather than "the cheapest".
* **The four-term law's `0.0000` holdout inside band K is real** and I reproduced
  it — it is simply a holdout inside the band that makes the law degenerate.
  A within-band holdout cannot detect a within-band collinearity, which is the
  transferable half of §2.

## Memory updates

**None** — `.memory/` and `RECAP.md` are manager-only and I did not touch them.
Durable facts for the manager to consider landing, in priority order:

1. **A number that only a rebuild can produce must not be transcribed into a file
   that a rebuild re-hashes** (§4). This is a `.memory/03-measurement.md`
   candidate and it is a *general* rule, not a p23 one.
2. **A band that holds a regressor FIXED cannot give you the coefficient of
   anything collinear with it, and a within-band holdout will not tell you**
   (§2). p23 produced three mutually inconsistent "exact" laws before the right
   one.
3. **A `required` spelling pin can be satisfied by a tautological conjunct**
   (§1). `spelling_matches` is a token test; `k_u5` adds `i < j &&` to a
   condition where it is always true and the compiler deletes it. The declaration
   admits a program it was believed to exclude, and the gate cannot see the
   difference.

---

## The three calls the manager was least sure of

**1. Is the `2991.00` spelling admissible?** ⚠⚠ **YES — via `k_u5`, and the
headline moves.** `k_u1` itself is not (its upward guard is `m - g < j &&`), but
`k_u5` is `k_u1` plus a redundant tautological `i < j &&`, satisfies the English
*and* `spelling_matches`, and has **the same object code** (`md5_norm
da08af26d9b1`). **The published R3-side floor 3141.00 was 150.00 `Ir`/call too
high at the median band** (338.00 at rank 0, −46.00 at rank 100), **the R3 and R4
spans overlap**, and the span's **top** endpoint was independently wrong because
4208.00 is a `forbidden` spelling. All conditions: probe, `-O -C
codegen-units=1`, isolated, debug-assertions off, `NREC=4 NELEM=48 SEED=12345`,
**rank 50 unless stated**.

**2. M3's replacement mechanism.** Landed as a **candidate**, not promoted, not
dropped. The measured part is the regressor: **`sw` R²=0.9730 against `dn`
R²=0.0227** over the 31 band-K points, price ≈ `+195` flat `− 5.2 Ir` per
exchange. ⚠ **And I added a measurement the review did not make: the gcc guard's
price is POSITIVE at all five band-X points**, so the negative sign is absent
from p23's own mixed band as well as from both ends of the rank band.

**3. Does the exact four-term law generalise beyond band K?** ⚠⚠ **NO. It fails
by up to 480 `Ir`/call on band N and by 152 on the two SHIPPED matrix inputs.**
Bands N and X are now fitted, band M at all 47 points instead of 8, and the
correct closed form is
**`2 + 30·recs + 2·dn + 2·sw − 3·rounds + Σ τ(m mod 4)`**, `τ = {0,2,3,4}`,
**residual 0.0000 on all 109 shipped points**, with the coefficients fitted on
bands M+N and the other **38 points predicted to 0.0000**. **The task file was
right that this was better found now than quoted in the synthesis.**

---

⚠ **PROTOCOL rule 2 running count.** Carried forward from **356**, as the task
file states; I was the only agent running, so no reconciliation is owed and
reconciliation is the manager's job in any case. **+12** for this task:

1. `k_u5` — an **in-contract** spelling at 2991.00, same object code as `k_u1`;
   the published R3-side floor was 150 `Ir`/call too high and the R3/R4 spans
   overlap;
2. the R3-side span's **top** endpoint was also wrong — 4208.00 is `r3b`, which
   hits both `forbidden` entries;
3. `u2`/`u3`/`u4` — three in-contract respellings of the same idea, all dearer
   than or equal to `base`: **only the tautological conjunct recovers the
   saving**, which is what makes it a hole in the declaration rather than a
   spelling preference;
4. the TASK_105 four-term law **does not generalise** — 480 off on band N, 152
   off on the shipped matrix inputs;
5. the closed form `2 + 30·recs + 2·dn + 2·sw − 3·rounds + Σ τ(m mod 4)`,
   residual **0.0000** on all 109 shipped points, with a 71→38 holdout at
   **0.0000** against a shuffled arm at 6050.96;
6. the `τ(m mod 4)` term itself — a per-record 0/2/3/4 `Ir` periodicity that
   bands K and N are structurally blind to;
7. `up + dn == mbytes` exactly at all 109 points, generalising band K's 256.00;
8. the gcc guard's price is **positive at all five band-X points** — the negative
   sign is absent from p23's own mixed band;
9. `k_r4dn` and `k_r4b` are **`md5_norm`-identical**, not merely equal in `Ir`;
10. ⚠ **a THIRD refutation of 9d's mechanism, and it points the opposite way**:
    giving the **upward** scan the descending cursor and the unsigned
    subtraction that 9d blames for the *lost* elision makes it **512 / 262 / 15
    `Ir`/call CHEAPER** and takes it **below the fully unchecked kernel at two of
    the three ranks**;
11. ⚠ **the `adversarial-single` checksums cannot be transcribed into `NOTES.md`
    at all** — `NOTES.md` is in the gate record's `source_sha256`, so every edit
    forces a gate run and every gate run moves them; demonstrated twice on this
    task, and **the DISTINCT COUNT is not stable either**: two gate runs minutes
    apart on identical sources gave 7 and 8, so `TASK_105`'s *"seven distinct"*
    is a better correction than *"eight"* but is still not a fact;
12. `spec.md`'s `identity[0].why` does not contain the direction mechanism, so
    M4's `spec.md` half had no target and `contract_sha256` did not move.

→ **368.**
