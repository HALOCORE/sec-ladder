# TASK_161 report — `p49` is built, and the task file's central premise is half false

**Role: research engineer.** Scratch and all evidence: `.temp/t161/`
(`NOTES.md` is the running log; `patterns/p49-interned-pool/NOTES.md` is the
pattern's own numbers; this file is the report).

---

## 0. TWO REFUTATIONS AND ONE CLEAN NEGATIVE, BEFORE THE BUILD

### 0a. ⚠⚠⚠ *"the guard `if (r_shared[i])` CAN NEVER BE FALSE"* — FALSE

`TASK_161.md` §"THE DEFECT YOU MUST FIX" and `.temp/mgr161/NOTES.md` §2 both
assert, verbatim:

> ⚠⚠⚠ **`r_shared[nrec]` is ALWAYS `1`, so `SLB_HARDEN == 1`'s guard
> `if (r_shared[i])` CAN NEVER BE FALSE. That is `.memory/03-measurement.md`
> entry 19 exactly.**

**The first clause is true. The second is not, and it is measured in the
reduction's OWN C** — two counters spliced into a COPY of
`.temp/t160/red/k40304.c` (never the original; every substitution asserted),
20 000 random op streams at `SLB_HARDEN=1`
(`.temp/t161/red_probe/probe.py`):

```
records BORN shared ............. 215 579
records BORN owned ..............       0      <-- the DEAD branch, and the real defect
guard `if (r_shared[i])` TRUE ...  67 195
guard `if (r_shared[i])` FALSE ..  30 263      <-- 31.1% of 97 458 evaluations
```

The reduction's own copy-on-write arm writes `r_shared[i] = 0;` when it
un-shares (`k40304.c:122`), so a **second** `BREAK` on a record the first one
copied takes the false branch.

⚠ **What IS true of the reduction as SHIPPED**: its two blobs evaluate the guard
**once between them** — benign 0, adversarial 1 — and it is TRUE that once. So
the demonstration never exercised the false branch even though the program can.

✅ **The precise defect is *no record is ever born owned*, not *the guard cannot
fire*, and the two need different repairs.** The fix the task asked for — derive
the width from the input — repairs the first, which is the one that matters: the
`INLINE_THRESHOLD` is the CVE's own precondition and a compile-time `if (3 < 5)`
is not a test of it. **The instruction was right; its stated reason was not.**

### 0b. ⚠⚠ *"THE FIX IS SMALL"* — FALSE, with a count

`.temp/mgr161/NOTES.md` §2: *"✅ **THE FIX IS SMALL AND IT MAKES THE ROW
BETTER**"*. The second half is right.

A constant width makes materialising, copying and folding a buffer
straight-line code. A variable width makes all three **loops**, and at R5 a loop
needs a recursive spec function, a loop invariant, and — for the copy — an
**induction lemma**:

| | `p49` | `p32` (the closest built row) |
|---|---|---|
| recursive spec fns for the byte loops | **3** | 0 |
| verified exec helpers containing loops | **4** | 0 |
| proof fns (induction / case split) | **3** | **0** |
| Verus obligations | **34** | 15 |
| `verus.rs` lines | **1 126** | 641 |

**34 is the largest count in the tree, and that is a census rather than an impression**: every `spec.md`'s `verus.obligations` summed gives p49 34, p29 25, p34 24, p28 23, p46 21 … p32 15, p25 10, p04 9. ⚠ It is the largest COUNT and not the largest FILE — `p28`'s `verus.rs` is 1709 lines and `p29`'s 1494 against p49's 1126. And it produced a Verus failure: the first complete `verus.rs` reported
`while loop: Resource limit (rlimit) exceeded` on the kernel's own op loop at
the default budget (§4c).

### 0c. ✅ A CLEAN NEGATIVE — the `p08`-distinctness argument STANDS

The task named it as a call to attack. **I attacked it and it holds**, and it is
now a number rather than an argument (`controls/no_overlap.py`, re-derived from
the shipped blobs every run, both semantics, every window):

```
p49   copies performed 6, of them DISJOINT 6
      record pairs COINCIDING EXACTLY .. 11 084
      record pairs DISJOINT ............ 892 352
      record pairs PARTIALLY overlapping        0
p08   partially-overlapping copies (the negative control)   9
      of which on its own adversarial-overlap.bin           4
```

**`p49`'s sharing is EXACT and `p08`'s is PARTIAL**, and partial is the only
kind `p08` has. The `p08` arm is synthesised from `p08`'s own documented decode
so it runs from a fresh clone, and the control FAILS if it finds no partial
overlap — a census that could only ever answer *no overlap here* would prove
nothing.

⚠ **The one place the manager's argument is incomplete**, and it is a
classification question rather than a distinctness one: `composition.py`'s
`aliasing` class is currently *"two live references to overlapping storage, one
of them mutable"* with `p08` its only member, and `p08`'s aliasing **is
undefined behaviour** while `p49`'s is not. Admitting `p49` forces that
description to widen. §5 states the case both ways and proposes wording.

---

## 1. WHAT WAS BUILT

`patterns/p49-interned-pool/` — **seven rungs, nine inputs, nine controls.**

| file | what |
|---|---|
| `c/kernel.h` | the contract in pseudocode, the four-line in-bounds proof, the `p08` argument |
| `c/kernel.c` / `c/kernel_hardened.c` | R1 and R1h; the difference is the copy-on-write block at the ONE mutation site |
| `c/main.c` | the driver, 12 canonical statements |
| `model.py` | **two implementations of different shapes** — buffer OBJECTS with identity (no offsets anywhere) and the OFFSET formulation that mirrors `verus.rs::run` — plus `Detector` and its must-fire arm |
| `inputs/gen.py` | 9 blobs + 2 sweep bands; refuses to emit a benign window that BREAKs a shared record |
| `safe_naive.rs` / `safe_tuned.rs` / `unsafe.rs` / `verus.rs` | R2–R5 |
| `spec.md` | the pins; `NOTES.md`; `README.md` |
| `controls/` | `safety_line`, `threshold`, `no_share_break`, `no_overlap`, `detectors`, `spellings`, `safe_arms`, `rust_bug`, `proof_mutants` + 3 `ctl_*.c` + 2 `arm_*.rs` |

### The mechanism, and the defect fixed before anything was measured

Content narrower than `THRESH` is INTERNED and DEDUPLICATED, so two records
legitimately borrow one buffer; the cycle-breaker writes through it.
**`w = 1 + a % MAXW`** with `MAXW = 6`, `THRESH = 4` — the width comes from the
file, so both branches of the threshold are live and the ownership flag varies.
`controls/threshold.py`, 20 000 random windows, both width rules on the **same**
streams:

```
                                shipped (w = 1 + a % 6)   reduction (w == 3)
intern / own branch taken            90 476 / 89 409        180 834 / 0    DEAD
records BORN shared / BORN owned     90 222 / 87 760        177 555 / 0    DEAD
guard TRUE / FALSE                   33 373 / 64 127         65 973 / 31 527
   guard FALSE on a record BORN owned    48 033                     0    IMPOSSIBLE
copy-on-write REFUSED                       412                     0
```

---

## 2. THE GATE

⚠ Read out of `results/gate/p49-interned-pool.json`, not grepped from the log.

```
results/gate/p49-interned-pool.json
  verdict       : PASS
  complete_run  : True
  failures      : []
  blocked       : []
  contract_sha256: d339ef900e0b2c59c1f8b3a851fdebe3b46ae8f999294e593a5dc5d7a667e0be
```

`harness/measure.py p49` wrote `results/p49-interned-pool.json`;
`harness/report.py p49` wrote `results/tables/p49-interned-pool.md`.

---

## 3. THE RESULTS

### 3a. ⚠⚠ Every detector is silent, and that is the row

```
controls/detectors.py:  216 kernel cells (R1 + R1h x gcc/clang x O0/O3
                        x plain/asan/ubsan x 9 inputs) -- 0 diagnostics
controls/rust_bug.py:   Miri, 18 bug-arm cells -- 0 undefined behaviour
gate stage 8:           Miri on the shipped R4, 9 inputs -- no UB
```

**With the controls FIRING**, which on this row is the whole of the evidence
that the silence is a fact about the program:

```
ctl_asan.c        heap use-after-free        FIRED under ASan   4/4 cells
ctl_asan_stack.c  c/kernel.c's own store,    FIRED under ASan   4/4
                  one byte outside a local   FIRED under UBSan  4/4
                  [u8; 64]
ctl_ubsan.c       signed integer overflow    FIRED under UBSan  4/4
                                        16 firings, 0 unexpected
```

⚠ **`ctl_asan_stack.c` is the row-specific one**: `c/kernel.c`'s harm is a store
into a LOCAL ARRAY, and without it *"ASan is silent on p49"* would be compatible
with *"ASan cannot see this class of object"*. Read the pair together: **p49's
store is in bounds and both sanitizers say nothing; the SAME store one byte out
is reported by both.**

⚠ **My own first expectation in that control was WRONG and is recorded rather
than quietly relaxed**: it required `ctl_asan_stack` to be SILENT under UBSan,
and the run said otherwise on both compilers at both levels — UBSan's
`-fsanitize=bounds` sees a constant-extent array indexed out of range. That makes
the control stronger, and the table now encodes the measurement.

✅ **The inverse of `p34`, as the task predicted**: there the checksums are
bit-identical and ASan is the only discriminator; here every detector is silent
and **the checksum is the only instrument**. `model.py` therefore DECLARES
`sanitizer_expect = "clean"` on every input (entry 19: *declaring is honest*) and
derives a different question instead — *what did the write REACH* — over two
integer lists, with a three-probe must-fire arm that answers three different
ways.

### 3b. The safety line is `cow`, measured, not inherited

`controls/spellings.py` builds the upstream `provenance` repair by ONE asserted
substitution and runs all three arms on all nine inputs:

```
benign inputs on which `cow` moves the answer        : 0 of 3
benign inputs on which `provenance` moves the answer : 3 of 3
```

**`TASK_160`'s port-level finding, reproduced inside the row.** Both repairs fix
every adversarial input except `adversarial-stride3.bin`.

Priced per cell (never maxed across one), and **THREE runs of this control agree
to 0.00 on all twelve marginal-`Ir` figures and on all twelve static counts** —
two before the `c/kernel.c` comment fix and one after, which is also what says
that fix moved no measured value:

```
                 static insns (isolated)      marginal Ir/call vs bug
cow          gcc O0 +66   O3 +136          gcc O0 +26.58   O3  -2.34
             clang O0 +48  O3 +131         clang O0 +17.72 O3 +14.73
provenance   gcc O0 -88   O3  -42          gcc O0 -513.79  O3 +17.34
             clang O0 -77  O3  -96         clang O0 -516.26 O3 -280.67
```

⚠ **The cheaper repair is the one that changes the answer.** `provenance`
deletes the dedup scan, so it is smaller and (at `-O0`) far faster — and it is
the one that moves a benign observable.

### 3c. The cost axis — and its SIGN REVERSES

`R1h − R1`, kernel-exclusive `Ir` per call, from
`results/p49-interned-pool.json`:

```
small.bin  gcc   O0 iso  +25.39 (+0.86%)   gcc   O3 iso   -2.79 (-0.14%)  <-- NEGATIVE
small.bin  clang O0 iso  +16.93 (+0.73%)   clang O3 iso  +13.87 (+0.61%)
large.bin  gcc   O3 iso  +31.41 (+0.62%)   clang O3 iso +171.15 (+2.92%)
```

⚠⚠ **At `-O3` on `small.bin` the hardened kernel is CHEAPER than the buggy one
under gcc and DEARER under clang.** That is `p35`'s trap live on this row, and
it is why **no single headline number for "the price of p49's safety line"
exists.**

⚠ **A per-guard decomposition was attempted and DOES NOT CLOSE, so it is not
published as a price.** The driver's window-visit orbit gives the guard
evaluations per call exactly (`.temp/t161/guard_per_call.py`: 4.232 on
`small.bin`, 22.351 on `large.bin`, 2.000 on `degenerate.bin`), and dividing
gives −0.66 … +7.66 Ir per guard — **and the figure moves as much across the two
INPUTS inside one (compiler, level) cell as it does across compilers**, so the
delta is not attributable to the guard alone.

**R4/R5**: `0.00` in every measured cell. ⚠ That is the **kernel-exclusive**
column from the measurement record and **not** `.memory/03-measurement.md` entry
23's `marginal_ir_per_call` null, which is a whole-program slope taken inside the
gate; `patterns/p49-interned-pool/NOTES.md` 4d says so explicitly.

**The R3 lever** also reverses: `+1617.26 Ir/call (+27.05%)` at `-O0` and
`−148.05 (−5.81%)` / `−612.20 (−9.18%)` at `-O3`. ⚠ **No second in-contract R3
spelling was built, so no R3-side spread is published.**

**Wall clock cannot resolve any of this**: the spread (0.78–3.10%) exceeds the
effect (0.6–2.9%) and the sign disagrees with `Ir` on `large.bin` for both
compilers.

### 3d. ⚠⚠ Safe Rust offers BOTH the bug and the repair

`controls/safe_arms.py`, all nine inputs:

```
A  index arena (the shipped R2)      == c/kernel_hardened.c   9/9
B  Rc<RefCell<Buf>>                  == c/kernel.c            9/9   THE BUG, SAFELY
C  Rc<Buf> + Rc::make_mut            == c/kernel_hardened.c   9/9   THE REPAIR, FROM std
```

**B and C differ in ONE TYPE.** `make_mut` *is* copy-on-write, so the safety line
is the standard library's; `RefCell` is exactly the "shared and mutable" the
pattern is about and the dynamic borrow check passes. ⚠ **That is the opposite
of `p34`**, where safe Rust cannot express the bug at all.

And `controls/rust_bug.py`: the shipped R2 with the safety line deleted has
**zero `unsafe` tokens** and reproduces `c/kernel.c` on 9/9 inputs.

⚠ **E0594 is NOT distinguishing.** Writing through a shared `Rc<Buf>` gives
`error[E0594]: cannot assign to data in an Rc` — and so does a NEGATIVE CONTROL
with no pool, no dedup and no second referent (`let r = Rc::new(5i32); *r = 6;`).
**Fifth time this project has been offered a rustc code that does not
distinguish** (p25's E0502, p28's E0382/E0499, p34's E0507).

### 3e. The R5 — a disjointness obligation, and a battery of nine

`34 verified, 0 errors` shipped; `37 verified, 0 errors` under `--cfg slb_twin`.
`identity`: **`exact` at `-O3`** (`md5_raw 563ecf2f…` on both binaries) and
`norel` at `-O0`. TCB five items.

⚠⚠ **`copy_bytes` carries `requires src + w <= dst` — the DISJOINTNESS /
PROVENANCE precondition `TASK_160` §8 predicted nothing in this tree states** —
discharged out of `wf_prov`'s clause that a SHARED buffer lies wholly inside the
arena.

⚠ **What the `ensures` deliberately does NOT say is "no record's content aliases
another's", because that is FALSE BY DESIGN.**

`controls/proof_mutants.py`, **9 of 9 arms as expected**:

```
M0-control              verify   34/0
M1-safety-line          fail     33/1   rlimit exceeded          ATTACK
M2-constant-body        fail     31/1   postcondition            VACUITY
M3-spec-weaken          VERIFY   34/0                            must-verify
X1-spec-only-weaken     fail     33/1   assertion failed
X2-provenance-invariant fail     33/1   postcondition (the lemma's)
X3-copy-disjointness    fail     33/1   invariant not satisfied before loop
M4-lemma-rec-in-pool    VERIFY   34/0                            must-verify
M5-both-hints           fail     33/1   rlimit exceeded
```

`M1` exec-only FAIL / `X1` spec-only FAIL / `M3` both VERIFY is the three-cell
form: **the safety line is load-bearing against the specification and against
nothing else**, which is `p32`'s finding on a different bug class. `X2`+`X3` are
this row's own pair on the disjointness obligation, from both sides.

---

## 4. THINGS THAT SURPRISED ME, RECORDED RATHER THAN SMOOTHED OVER

### 4a. A FALSE SENTENCE IN A SHIPPED RUNG SOURCE, caught by rule 6's second half

`c/kernel.c`'s header said *"**The copy loop below** is a BYTE LOOP over ranges
that cannot overlap"*. **`c/kernel.c` contains no copy at all** — the copy
belongs to `c/kernel_hardened.c`. The `contract_sha256` was matching perfectly
the whole time and no gate stage reads a comment for truth. **This is p46's
lesson exactly, and it cost one re-measure**; two more measurement-hashed files
were corrected in the same pass (`inputs/gen.py` repeated the *can never be
false* claim, `verus.rs` did not say `lemma_rec_in_pool` is a hint).

### 4b. ⚠⚠ `A && B` IN ONE `ensures` CLAUSE IS NOT `A`, `B` AS TWO CLAUSES

The first complete `verus.rs` failed with `Resource limit (rlimit) exceeded` on
the kernel's op loop at the default budget. Two independent edits were made; the
file then verified, and **the battery's `M4` arm — written expecting `fail` —
came back `verify`**, which forced the bisection (all at the DEFAULT rlimit):

```
lemma_rec_in_pool calls   lemma_find's 2nd ensures    result
  present                   TWO clauses               34 verified, 0 errors   <- shipped
  ABSENT                    TWO clauses               34 verified, 0 errors   (M4)
  present                   ONE clause (`A && B`)     34 verified, 0 errors
  ABSENT                    ONE clause (`A && B`)     33 verified, 1 error    rlimit exceeded
```

**Two independent edits cure the same solver blow-up and the shipped file carries
both, so neither is necessary given the other.** ✅ The rlimit exceedance was a
**missing case split, not genuine size** — p49 ships **no
`#[verifier::rlimit(..)]` attribute** where `p28` needs `400`, and the shipped
file verifies at the default budget in about four seconds. ⚠ **A `rlimit`
message is a diagnostic about the solver's SEARCH, not about the proof's
difficulty**, and reading it as the latter would have sent this build down a much
longer road.

### 4c. `M1`'s failure SITE is not established

At `--rlimit 200` its diagnostic is the solver's budget; a probe at
`--rlimit 4000` was still running after about twenty-five minutes and was
terminated. An earlier draft of the battery's own `why` claimed *"it fails on the
POSTCONDITION"*; **that claim is withdrawn** and the file now says what was
measured.

---

## 5. THE BUG CLASS (deliverable 5) — proposed, not applied

⚠ `harness/tools/composition.py` was **not edited**.

**Proposed: `aliasing`, with a caveat.** Full argument, both ways, in
`patterns/p49-interned-pool/NOTES.md` §9, with the exact wording to paste. The
short version:

* **for `aliasing`** — it is what `composition.py`'s own stated test selects
  (*what does the safety line ASK?* — `if (rshd[t])` asks an OWNERSHIP question
  about a live alias); it describes p49 literally; and `logical`'s three members
  (`p04`, `p06`, `p19`) have **no aliasing structure at all** while p49 cannot
  exist without one.
* **for `logical`** — *"wrong answer, memory-safe throughout"* is satisfied by a
  wide margin (216 + 18 silent detector cells), and `p08`'s aliasing IS undefined
  behaviour while p49's is not, so admitting p49 **forces the class description
  to widen**. That is a real cost and the manager may take it.
* ⚠ p49 would be the **third position** on this axis: `p28`'s aliasing is the
  SETUP, `p32`'s IS the harm, `p49`'s is the CONTRACT and the WRITE is the harm.

---

## 6. Problems, and what I did NOT do

* **No `--sweep` bands measured.** `inputs/gen.py --sweep` writes an
  operation-count band and a DEDUP band; neither was run, so **no figure here is
  a law with a domain** — every cost number is two input shapes, not a fit.
* **No second in-contract R3 spelling**, so no R3-side spread.
* **No `-O0d`, no `--panic abort`, no `safe_naive_verus.rs`.**
* **`large.bin` has no `-O0` `Ir` column** (measure.py's protocol), so §3c's
  `-O0` sign reversal rests on `small.bin` alone.
* **The `Rc` arms are checked for their ANSWER, not priced** — *"safe Rust offers
  both"* is a claim about EXPRESSIVENESS and carries no number.
* **`M1`'s failure site** (§4c).
* **The `provenance` arm is priced but never gated** — it is a control, not a
  rung, and no gate stage runs a detector on it.
* **`.temp/t160/` and `.temp/mgr161/` were never written**; the reduction was
  COPIED into `.temp/t161/red_probe/` and only the copy instrumented.
* **No `git add`, no `git commit`**, and `.memory/`, `RECAP.md`,
  `results/SYNTHESIS.md` and `harness/tools/composition.py` are untouched.
* **`harness/tools/composition.py --check` will FAIL** with `built but
  unclassified` until the manager applies §5. **That is the check working.**
* **Assumptions worth attacking** are listed in
  `patterns/p49-interned-pool/NOTES.md` §10 — the byte-packed 1–6-byte arena,
  the `(key, w)` dedup key having no collision path, and above all **the
  epilogue folding the ownership flag**, which is the modelling choice that makes
  `provenance` benign-observable and therefore decides §3b.

---

## 7. Deliverable checklist

| # | deliverable | status |
|---|---|---|
| — | fix the tautological guard BEFORE measuring | ✅ done first; §0a refutes the stated reason and §1 measures the fix |
| 1 | build `patterns/p49-interned-pool/`, gate + measure | ✅ **`harness/check.py p49` -> `PASS`, `complete_run: true`, `failures: []`, `blocked: []`** — read out of the record. `measure.py` and `report.py` both green. ⚠ The FIRST full gate run failed with exactly two `[tables]` entries, and both were the documented **stage-9c one-run lag on a NEW pattern**: `report.py` had run before any gate record existed, so the table carried no audit section. `report.py p49` + re-gate cleared it, which is the sequence `spec.md`'s *Reproducing* block already prints. |
| 2 | `model.py` not transliterated, no tautological check, `sanitizer_expect` declared | ✅ two implementations of different SHAPES (objects with identity vs offsets); `Detector` derives a different question and has a three-way must-fire arm; `clean` declared with the argument |
| 3 | R5 ATTACK arm that must FAIL + VACUITY arm | ✅ 9 arms, 9 as expected, incl. the three-cell spec-weaken experiment and this row's own X2/X3 pair |
| 4 | cost axis: both spellings, both levels, both compilers, a re-derivable control | ✅ §3b/§3c; `controls/spellings.py` re-derives; **the sign reverses and is reported per cell** |
| 5 | tell the manager the bug class, do not apply it | ✅ §5 + NOTES §9 with paste-ready wording |
| 6 | rule 6: record the contract sha256 and the block VERBATIM | ✅ `a297e6cb…`, text at `.temp/t161/contract_first_written.json`; **four moves disclosed with a key-by-key diff**, and the rule's second half caught §4a |

---

## 8. Housekeeping, checked rather than assumed

* **Staleness.** `harness/measure.py --check-stale`: `2 record(s) examined,
  0 STALE`. The gate record's own 49 `source_sha256` entries all match the tree
  (0 moved, 0 missing), and the measurement record's 18 sources + 9 inputs do
  too.
* **Artefacts deleted, generators kept.** `.temp/p49ctl/` (22 MB of control
  binaries) is gone and every control recreates it; `.temp/t161/`'s `.o` files,
  `__pycache__`, the instrumented probe binary and its scratch blob are gone.
  ⚠ **The generated `.rs` mutants are KEPT** — `.memory/00-environment.md`
  constraint 6 lists binaries, `.o`, `.pyc` and `.bin` as the deletable classes
  and says `.rs`/`.c` source is evidence — **and `.temp/t161/mk_bisect.py`
  regenerates and re-runs all four cells of §4b's 2×2 table from the shipped
  `verus.rs` in one command**, importing the substitution texts from
  `controls/proof_mutants.py` so the two cannot drift.
* **`.temp/t160/` and `.temp/mgr161/` were never written.** Checked, not
  assumed: `find .temp/t160 .temp/mgr161 -newermt '2026-09-01 07:00'` prints
  **nothing**, and this task started after 07:00. (Their newest files are
  06:53–06:54, the manager's own pre-build pass.) `probe.py` COPIES
  `k40304.c`/`demo.h` into `.temp/t161/red_probe/` and instruments the copy.
* **`../LearnVeri/` was never written.** `git status` there shows
  ` M PITFALLS.md`; it is **not mine** — mtime `2026-08-17 18:44:40`, two weeks
  before this session, and `TASK_160`'s report discloses the same file in the
  same state.
* **`git status` in sec-ladder** shows five untracked paths and nothing else:
  `.tasks/TASK_161_REPORT.md`, `patterns/p49-interned-pool/`,
  `results/gate/p49-interned-pool.json`, `results/p49-interned-pool.json`,
  `results/tables/p49-interned-pool.md`. **No `.memory/`, `RECAP.md`,
  `results/SYNTHESIS.md`, `harness/`, `synthesis/` or `pilot/` file was touched;
  no `git add`, no `git commit`.** The pattern directory contains **36 files**,
  no `.bin` and no `__pycache__`.
* **No waiter left running.** Every background wait used a `.done` sentinel or
  `until [ -f … ]`, never `pgrep -f`. Two long Verus probes were terminated by
  **exact PID after reading `/proc/<pid>/cmdline` and matching it**, never by
  name or substring.

---

**PROTOCOL rule 2 running count: launched from 914, +2 = 916.**
The two: *(1)* the task file's and `.temp/mgr161/NOTES.md`'s *"the guard
`if (r_shared[i])` CAN NEVER BE FALSE"* — false, 31.1% of 97 458 evaluations in
the reduction's own C; *(2)* `.temp/mgr161/NOTES.md`'s *"THE FIX IS SMALL"* —
false, and the count is in §0b.
⚠ **The `p08`-distinctness argument, the other call I was asked to attack, is a
CLEAN NEGATIVE: it stands, and it is now a number.**
⚠ **Reconciliation across branches is the manager's job, not mine.**
