# TASK_101 — `p23`, in-place quicksort partition. Report.

**Role: research engineer.** Built `patterns/p23-partition/`, **the 25th
pattern**. `harness/check.py p23` → **`check.py: PASS`, 32/32 cells, 0
failures**. `harness/measure.py p23 --cells all` → `results/p23-partition.json`;
`--check-stale` → **2 records examined, 0 STALE**.

**The row SHIPS.** §0 and §2 were done first and both came out favourable, but
neither came out the way the task file expected — the two calls the manager was
least sure of are answered below and **one of them is wrong**.

---

## §0 — the bug class and the novelty claim

### The multiset novelty claim: TRUE at the pinned-clause level, and WORTH LESS THAN IT SOUNDS

**The manager's grep was one file per pattern; I did the one the task file asked
for and one it did not.** `.temp/t101/s0_ensures.txt` dumps **every** pinned
`requires`/`ensures` from **every** `patterns/*/spec.md` `slb-contract` block —
`verus.items[*]`, 24 patterns.

```
grep -niE 'multiset|permut' .temp/t101/s0_ensures.txt   ->   0 hits
```

So the claim survives, and the manager's dismissals of `p14` and `p06` are
**upheld**: `p14`'s only hit is a comment in `verus.rs`, and `p06`'s kernel
`ensures` is `r == rotate_fold(...)` with lemmas that are exact positional
sequence equalities (`rot_left`, `rev_range`).

⚠ **But the instruction as literally written is trivially satisfiable and the
manager should know why.** *"Check `spec.md`'s pinned `ensures` for all 24"* —
the **top-level** `contract.requires` / `contract.ensures` are **identical across
all 24 patterns**: `["off + len <= buf_len"]` / `["result == <name>_fold(buf,
off, len)"]`. Those are the driver-level pins, not the R5 obligations. The
useful dump is `verus.items[*]`, which is what the file above holds.

⚠⚠ **AND THE FOLLOW-ON CLAIM — that p23's R5 obligation IS a multiset — DIES ON
A MEASUREMENT.** The nested-scan partition verifies **with** the multiset
postcondition (`.temp/t101/pA_hoare_nested.rs`, `6 verified, 0 errors`) **and
with every multiset clause deleted** (`.temp/t101/pA2_no_multiset.rs`,
`6 verified, 0 errors` — *same obligation count*). The multiset is **separable**:
not load-bearing for the partition postcondition, not load-bearing for memory
safety, because the guarded form's bound `i < j <= m <= SCR` is positional. p23
therefore **does not ship a multiset obligation** and does not claim one; it
ships the exact functional postcondition it actually needs (`part`).

**What the permutation does buy is the fold rule, in a stronger form than
p06's**: a partition is a permutation of the loaded prefix on *every* input, not
merely in one regime, so a sum- or xor-fold could not observe the partition at
all. p23's fold is order-sensitive Horner over the full live extent **plus the
partition point**, and `adversarial-inarray` separates R1 from R1h **on the
index alone**.

### The bug class: `index >= len`, the tree's FIFTEENTH — and that is not why it ships

`TASK_086` measured *"the unsentinelled scan running off the range = `index >=
len`, sharing with p07"*. **Confirmed, and refined.** The count: p36 was the
12th, p19 the 13th, p46 the 14th (RECAP), `p30`'s would have been the 15th and
`p30` is refused — so **p23 is the fifteenth**.

**Alternatives rejected by measurement, the way p10 §0 and p18 §0 do it:**

| candidate class | rejected because |
|---|---|
| *"aliasing"* (the catalogue's guess) | **overturned.** Nothing in p23 aliases: the exchange is two disjoint indexed accesses and the borrow checker never sees a live pair. Measured: `<[T]>::swap` and four indexed accesses are **byte-identical** and cost **0.00** (`.temp/t101` probe `k_r2 == k_r3c`, same padding-stripped normalised text). |
| *"permutation invariant"* (the catalogue's guess) | **overturned**, above: the obligation is separable and the pattern does not carry it. |
| unsigned underflow (p03/p07's class) | **half true and not the class.** The downward scan *does* wrap `j - 1` at `j == 0` — UBSan says `index 18446744073709551615` — but the wrap is *defined*; the UB is the load it then performs, so the class is the read. |
| non-termination (p22's class) | **rejected.** Both scans terminate in every rung; the unguarded one terminates by leaving the array. |
| a declared count trusted against a buffer (p05/p07/p16/p17's class) | **rejected.** No count is trusted here. `nrec` and `nelem` are both bounded by cursor guards every rung keeps. |

⚠ **The class is not why the row ships, and RECAP already says so.** RECAP
retired *"another `index >= len`?"* as the admission test and replaced it with
*"a new **mechanism** — a new operator on the safety line, a new source of the
bound, or a new reason the check is or is not elided."* p23 clears all three:
the guard compares **two loop variables**; **each cursor's bound is the other
cursor and both move**; and §9d below is a new elision reason nobody had.

---

## §2 — THE KILL RISK IS DEAD, AND THE MANAGER'S CALL 1 IS WRONG

> *"§2 — that the bug lives in the Hoare form and the verified form may not host
> it. This is my reasoning, not a measurement… If the two-index form hosts a
> perfectly good `index >= len` bug, say so plainly and I am wrong."*

**Outcome 1 of the three: the Hoare form verifies too, and the tension was
imaginary.** Run *before* any rung was built:

```
.temp/t101/pA_hoare_nested.rs   — NESTED-SCAN Hoare, guarded, two inner scan
                                  loops each with its own invariant and its own
                                  `decreases`, postcondition = multiset + p<=m +
                                  both sides partitioned + tail untouched
  verification results:: 6 verified, 0 errors          <- FIRST ATTEMPT
```

and the **shipped** R5, which is the nested-scan form, verifies
**`16 verified, 0 errors`, first attempt** (twin `19 verified, 0 errors`) with
**zero `proof fn`s**. Both spellings exist and both verify: the single-loop form
at `.temp/t86/v23_partition.rs` (`4/0`) and the nested-scan form here.

**And the manager is wrong in the sharper direction too.** The premise was *"the
bug may live in the form that does NOT verify easily."* The bug lives in the
form that **verifies most easily**, and the reason is structural: the spec
function `part` is the **single-loop three-way step** while the code is the
**nested scan**, and each inner scan step is exactly one of `part`'s first two
cases. Writing the spec in the shape the code moves in is what made the proof
lemma-free — p06 needs three `proof fn`s for a *simpler* obligation because
three reverses are not syntactically a rotation.

**Which spelling hosts the bug** (the second deliverable): **both**, and the
shipped one is the nested scan. `c/kernel.c` drops the `i < j` conjunct from
each inner scan; the guarded and unguarded cells are otherwise character-for-
character identical.

---

## Did

`patterns/p23-partition/` — 19 committed files:

```
spec.md  NOTES.md  README.md  model.py  inputs/gen.py
c/kernel.h  c/kernel.c  c/kernel_hardened.c  c/main.c
safe_naive.rs  safe_tuned.rs  unsafe.rs  verus.rs
controls/guard_equiv.py  controls/guard_variants.c  controls/run.sh
controls/sweep_fit.py  controls/controls.log  controls/sweep_fit.json
results/gate/p23-partition.json   results/p23-partition.json
```

Kernel: a 64-byte scratch, a record walk, Hoare's **nested-scan** partition
around a **record-supplied pivot**, an order-sensitive Horner fold plus the
partition point. p06's structural template; a new bound, a new bug and a new
elision mechanism.

---

## Evidence

### gate

```
check.py: PASS
    32/32 cells built
    3 inputs x 32 cells agree on the model's checksum
    3c. unsafe vs verus O0: norel · O3: exact (md5_fn 43acbc727fc6, md5_raw equal=True)
    5a. verus.rs: 16 verified, 0 errors -- matches the pinned obligation count; 5 TCB items
    5c. 4 `ensures` conjuncts deleted: every trusted `ensures` conjunct is load-bearing
    5c-req. 4 `requires` conjuncts probed, 1 deleted: no conjunct is a tautology
    5c-twin. 19 verified, 0 errors with --cfg slb_twin; all 3 twins fail when their
             conjunct alone is deleted
    5d. 80048 kernel calls across 9 inputs; `requires` on all, `ensures` on 304
    6. 5 driver loops normalise to the pinned 12-statement sequence
    7. C rung under ASan+UBSan: fired as declared on 4 inputs, clean on 5
    8. miri unsafe.rs: no UB on all 9 inputs, all checksums match the model
    0 FAILURES.  1 shout: [tcb-unsafe] scr_set_unchecked's `x` -- justified in spec.md
                          (the parameter-coverage false positive, 4th instance)
contract_sha256 in the gate record == recomputed from spec.md: 8251a676…
measure.py --check-stale: 2 records examined, 0 STALE
```

### the harm, per direction (gate stages 4 and 7)

| input | R1 (both C rungs, all 4 opt×mode) | R1h / R2–R5 |
|---|---|---|
| `adversarial-allbelow` (`pv=255`) | **exit −11 SIGSEGV**; UBSan `kernel.c:96 index 64 out of bounds`; ASan `stack-buffer-overflow` | exit 0, model checksum |
| `adversarial-allabove` (`pv=0`) | **exit −11 SIGSEGV**; UBSan `kernel.c:101 index 18446744073709551615` — the wrapped `j-1`; ASan `stack-buffer-UNDERflow` | exit 0, model checksum |
| `adversarial-single` (`m==1`) | **exit 0, silent, EIGHT CELLS → EIGHT DISTINCT WRONG CHECKSUMS** | exit 0, model checksum |
| `adversarial-inarray` | **exit 0, wrong answer, ASan+UBSan CLEAN** — the in-bounds middle regime | exit 0, model checksum |

**Both directions from one omitted pair of conjuncts**, reachable at a single
header byte (no `u8` is above 255 or below 0).

⚠ **`m == 1` cannot be made benign** and that is the sharpest row in the file:
one byte cannot be both strictly above and strictly below the pivot. Nothing
about the input is malformed. All eight C cells print a different wrong number
and none crashes, and the numbers are **unstable under a comment-only edit** —
the first gate run of the same sources, with three comment lines different in
`c/kernel.c`, gave gcc 3 distinct values instead of 4 and moved every one of the
eight. The output is a property of the binary's layout, not of the program.

### §3/§4 — levers counted on BOTH sides, and the law re-fitted from a shipped band

Probe (`.temp/t101/cost23.rs`, marginal whole-program `Ir`/call, `-O` isolated,
**debug-assertions OFF**, inline mode **isolated**): **6 R3 spellings** (3141.00
… 4208.00 at the median band) against **4 R4 spellings** (2876.00 … 3050.00).
Comparable, and the shipped R4 sits 6.00 **above** the cheapest R4 found — the
lever not taken (resliced-window addressing) is declared in `unsafe.rs` and in
`spec.md`'s `why`, because R4 must be byte-identical to R5 and `split_at` on the
window has not been shown to verify at the pinned vstd. **No pair interval is
published.**

Closed decomposition of R2 → R3, each lever alone (probe, median band):
`<[T]>::swap` **0.00** (byte-identical), two-step reslice **−38.00**,
`iter().fold` **−16.00**, both **−46.00** → **+8.00 interaction, not additive**.
**So R3's whole advantage over R2 is the header reslice and the fold, and none
of it is the exchange** — the operation the pattern is named for.

**Shipped cells**, kernel-exclusive `Ir`/call, `-O3 isolated`:

| | `small` (5 rec / 157 B) | `large` (12 rec / 54 B) |
|---|---|---|
| R2 − R4 | +350.69 | +531.17 |
| **R3 − R4** | **+305.74** | **+443.55** |
| R2 − R3 | +44.95 | +87.62 |
| **R4 − R5** | **0.00** | **0.00** (tautology, forced by `identity`) |
| `c-gcc-h` − R4 | +390.77 | +91.50 |
| **`c-clang-h` − R4** | **−33.79** | **−72.00** |

⚠ **R1 − R1h is NEGATIVE on gcc, on both inputs: −39.10 / −60.34**, and the
hardened kernel is also *smaller* (157 vs 160 static instructions). Adding the
guard lets gcc prove the scan is bounded by `j - i` and rotate the loop. **Clang
flips sign between inputs** (−3.12 on `small`, +23.14 on `large`). Any p23 claim
about *"the price of the guard"* that quotes one compiler or one input is wrong
at the sign level. ⚠ Likewise **C-vs-Rust: hardened clang C is cheaper than
unsafe Rust on both inputs and hardened gcc C is dearer on both.**

### ⚠⚠ THE HEADLINE, and it is a DOMAIN result

`controls/sweep_fit.py` re-fits from the **committed** sweep bands (`gen.py
--sweep`), which is the step §4 demands and p19 skipped.

Band M (`nrec=8`, **rank held at 0.50**, `m` 2…48):
`R3 − R4 = 29.430/record + 0.7066/byte`, residuals −8.9 … +19.3.

**Band K holds `m = 32`, `nrec = 8` and 256 copied bytes per call and sweeps
ONLY the pivot's rank:**

```
 nlow  rank        R3-R4
    1  0.03       706.37
    4  0.12       641.33
    8  0.25       557.89
   16  0.50       413.49
   24  0.75       302.96
   28  0.88       255.00
   31  0.97       227.00
```

⚠⚠ **`R3 − R4` moves by a factor of 3.11 with every size regressor held
constant.** The band-M law predicts **416.32** for all seven rows. **p23 is the
first pattern in this tree whose safety tax is a function of the data's SHAPE
rather than its SIZE**, and any p23 number quoted without its rank is quoted
without its domain. `small` and `large` are built at mean ranks 0.44 and 0.28
and `gen.py::_check_residues` refuses to write them otherwise.

### ⚠⚠ THE MECHANISM (PROTOCOL rule 12), isolated rather than argued

Probe kernels differing in **one** scan's checkedness:

```
RANK    k_r3c     k_up      k_dn      k_r4b
  3%   4460.00   4460.00   3972.00   3972.00
 50%   4492.00   4492.00   4308.00   4308.00
 97%   3764.00   3764.00   3778.00   3778.00
```

`k_up` (upward unchecked) **== `k_r3c` exactly at all three ranks**;
`k_dn` (downward unchecked) **== `k_r4b` exactly at all three**. Therefore:

> **LLVM already elides the UPWARD scan's bounds check and does not elide the
> DOWNWARD one's. The whole of p23's scan-side safety tax is `scr[j - 1]`, at
> ≈2.00 `Ir` per downward step.**

`scr[i]`: `i` starts at 0, increases monotonically, and `i < j <= m <= 64` — the
induction variable's own recurrence proves it. `scr[j - 1]`: `j` starts at a
runtime `m` and **decreases**, and the index is an unsigned **subtraction**, so
the same expression additionally has to be shown not to wrap. **The direction of
the induction variable decides whether the check survives** — and that is why
the tax tracks `m − nlow`, the downward scan's step count, and nothing else.
That is a new entry in this project's list of elision reasons; the earlier ones
(p19's state-range `cmp $0x8`, p05's per-row hoist, p46's header-derived range
facts) are all about where the bound *comes from*.

### a claim I shipped in draft and my own control refuted, BEFORE measuring

`c/kernel_hardened.c` originally said the alternative guard `i < m` / `j > 0`
was *"safe, and WRONG"*. **False.** `controls/guard_equiv.py`:

```
  full 0..255    trials=400000 differing=0
  narrow 0..4    trials=400000 differing=0
  must-fire arm: … differs: True
  verdict: EQUIVALENT
```

After an exchange `scr[j] > pv` and `scr[i-1] < pv`, so each scan stops at the
other cursor whatever its guard says — the cursors cannot cross. `spec.md` pins
a **spelling** there, not a semantics, and it now says so. Corrected in the C
comment, in `controls/guard_variants.c` and in `NOTES.md` 8.

### harm probes: the positive controls, and the one that could not have failed

Every sanitiser run used `env -u LD_PRELOAD`; every log was `grep`ed, never
`head`ed. **Positive controls that FIRED, in the same binary and on the same
command line as the probe:** `.temp/t101/harms.c`'s `k_ctl` (a deliberate
one-past-the-end read) → ASan `stack-buffer-overflow` + UBSan `index 64`, exit 1,
on all three inputs; and `controls/run.sh`'s `bug` cell → ASan overflow *and*
underflow, exit 1, with `ij`/`mz` clean on the identical runs. Control B has a
**must-be-clean arm** as well: `k_selfpivot` on a mixed record exits 0 on plain,
ASan and UBSan.

**`valgrind` memcheck is still unavailable** — `Fatal error at startup: a
function redirection … memcmp … libc6-dbg`. That **confirms** PROTOCOL rule 14's
correction (it is genuinely `libc6-dbg`, not the `LD_PRELOAD` blindness).
`callgrind` works and is what every `Ir` here uses.

---

## Problems

1. **`check.py`'s three known defects did not bite, and one was checked rather
   than assumed.** No `include!` anywhere, so `_check_opaque_includes` is not
   reached; only a plain `#[path]`, so `_path_includes` is not reached. For the
   `MIRIFLAGS` seed-dependence I ran `unsafe.rs` under Miri at
   `-Zmiri-seed=` 0/1/2/3 × three inputs: **0 UB in twelve runs, all twelve
   checksums equal `model.py`'s.** It cannot bite here because every unchecked
   access is a `u8` on a `[u8; 64]` or `&[u8]` — no alignment for the seed to
   randomise. Recorded in `NOTES.md` 10 as a clean negative.
2. **The `contract_sha256` moved once**, after the first gate run and before any
   measurement: `22240ee4…` (30741 B) → `8251a676…` (31085 B). Five edits, all
   disclosed with reasons in `NOTES.md`'s Rule-6 section: one dead pin removed
   (the gate's own audit reported *`p <= len`* as *"pins nothing"*), three probe
   figures relabelled as probe figures, one loop recount. **No `required`,
   `forbidden`, `obligations`, `identity` or `miri` entry changed meaning.**
3. **`controls/` gains two artefact files** (`controls.log`, `sweep_fit.json`)
   and one `.c`, where the tree's other 92 `controls/` files are 85 `.py` + 7
   `.sh`. Deliberate: `sweep_fit.json` costs ~30 min of callgrind to regenerate
   and `NOTES.md` cites both for published numbers. **Flagging it as a
   convention deviation for the manager to accept or reject** — deleting them
   dangles two `NOTES.md` citations.
4. **`.memory/03-measurement.md`'s pre-registered mechanism for p23 is not what
   a correct rung does.** It says *"`while v[i] < pivot { i += 1 }` has no upper
   guard: the bounds check **IS** the termination bound and cannot be deleted."*
   A rung that relies on a panic for termination is not correct, so the shipped
   rungs carry `i < j` explicitly. **The conclusion — LOW collapse exposure —
   still holds and is measured** (R2 217 insns / R3 196 / R4 160; the check
   survives). **The mechanism sentence should be corrected**, and the correct
   one is §9d above.

## Unsure / not done

- **No `-C debug-assertions=on` column.** §3 warned that it enables
  `assert_unsafe_precondition!` inside `get_unchecked` and that on 3 of 3
  patterns R4 becomes dearer than R3 at `-O3`. Every p23 figure is
  debug-assertions **OFF** (the gate's own setting) and the alternative column
  was **not run**. Named at every figure in `NOTES.md`; a reviewer could add it.
- **Bands N and X are shipped and were not fitted.** `sweep_fit.py` reads bands
  M and K only.
- **The band-K fit `R3 − R4 = 187.3 + 16.01·(m − nlow)` has ±30 residuals** over
  a 227…706 range. It is a good description, not a law; the curvature is not
  modelled and is probably the exchange count `∝ r(1−r)`. **Do not quote it as a
  law.**
- **The `<`/`>` comparison variant is not built as a rung** — it is a different
  program (its partition point differs by one on any record holding a byte equal
  to its pivot) and is excluded by contract, not measured.
- **The probe `Ir` figures in `spec.md`'s `why` and in two rung doc comments are
  a PROBE's**, relabelled as such after `.memory/03-measurement.md`'s p46
  lesson. The shipped-cell figures in `NOTES.md` 9a and the band fits in 9c are
  the ones to quote.
- **Wall clock is not a headline.** `unsafe` and `verus` are byte-identical and
  read 519.25 vs 554.29 ns/call on `small isolated` — the source-path-length
  artefact, a biased draw of size one. No p23 claim rests on it.
- **I did not touch `harness/`, `pilot/`, `.memory/`, `RECAP.md` or the Verus
  pin, and ran no history-mutating git.** (`git add -An` is `--dry-run`; the
  index was verified empty afterwards.)

## Memory updates

**None written — `.memory/` is manager-only.** Durable facts the manager may
want, after review:

1. **`.memory/06-catalogue.md` `p23`:** BUILT at TASK_101 as `p23-partition`,
   the 25th pattern. Gate `PASS`, 32/32, 0 failures. Verus **16/0 first
   attempt** (twin 19/0), **zero `proof fn`s**, TCB 5 (3 contract-bearing),
   `identity` O0 `norel` / O3 `exact`. Catalogue guess *"aliasing, permutation
   invariant"* **OVERTURNED on both limbs** — nothing aliases (`swap` and four
   indexed accesses are byte-identical, 0.00) and the permutation obligation is
   **separable** (`6 verified, 0 errors` with and without it). Bug class the
   tree's **15th** `index >= len`; it ships on RECAP's *replacement* bar.
2. **`.memory/06-catalogue.md` / `04-verus.md`, `p23`'s kill risk:** **DEAD.**
   The nested-scan Hoare form verifies `6/0` first attempt as a probe and `16/0`
   first attempt as the shipped R5. Both spellings verify. The `04-verus.md` row
   saying *"the two-index multiset loop invariant … nowhere — it was the easy
   part"* should gain: *the nested-scan form is easier still, because the spec
   can be written in the shape the loop nest moves in, which removes the lemmas
   entirely.*
3. **`.memory/03-measurement.md`, the p23 row of the probe-shape table:** the
   **conclusion** (LOW exposure) is upheld by the shipped cells; the
   **mechanism** (*"the bounds check IS the termination bound and cannot be
   deleted"*) does not describe a correct rung and should be replaced by §9d's:
   **LLVM elides the UPWARD scan's check and not the DOWNWARD one's, because the
   direction of the induction variable decides.** ⚠ Two parts, different
   evidence — land the conclusion, mark the mechanism as p23's finding.
4. **`.memory/01-ladder.md`, a NEW finding shape:** *a safety tax can be a
   function of the data's SHAPE and not its SIZE.* p23's `R3 − R4` moves 3.11×
   across the pivot-rank band with `n`, records and bytes all fixed. **Every
   published p23 number owes its rank.**
5. **`.memory/03-measurement.md`:** `valgrind` memcheck's failure is `libc6-dbg`,
   re-confirmed at TASK_101 with the full error text.
6. **`.memory/02-bench-rules.md`'s write rule:** p23's row is upheld and the
   mechanism is worth one clause — the threshold is the scratch's live extent,
   and the out-of-bounds **write** is reached because a missing **read** guard,
   one loop earlier, let `j` wrap.
7. **A gate-audit note:** an `idiom.required` entry that backticks a *property*
   rather than a *spelling* is reported as *"pins nothing"* — `p <= len` did
   that on p23's first gate run. Cheap to catch; worth a line wherever the
   named-spelling standard is explained.

---

⚠ **PROTOCOL rule 2 running count.** Launched from **332** (stated in
`TASK_101.md`). I was the only agent running, so no reconciliation is owed.
Carrying forward **+11** for this task: the multiset claim settled at the pinned
level; the multiset shown **separable**; §2's kill risk killed and the manager's
call 1 refuted; the `i < m`/`j > 0` *"safe and wrong"* claim refuted by its own
control; the rank-dependence (3.11× at fixed size); the elision mechanism
isolated; R1 − R1h **negative** on gcc; the C-vs-Rust sign flipping with the
compiler; `m == 1` structurally adversarial with an eight-way build-dependent
split; `.memory/03-measurement.md`'s pre-registered p23 mechanism shown not to
describe a correct rung; and the top-level `contract.requires`/`ensures` shown
identical across all 24 patterns. → **343**.
