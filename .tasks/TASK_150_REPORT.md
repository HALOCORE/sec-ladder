# TASK_150 — landing `p28`'s review corrections. Report

**Role: research engineer.** Everything claimed here was **run** and the output is
pasted. Scratch and generators: `.temp/t150/`. No `git add`/`git commit`; no
`.memory/`, `RECAP.md` or `results/SYNTHESIS.md` edited.

---

## ⚠⚠⚠ 0. THE HEADLINE: I REFUTED HALF OF MY OWN TASK FILE'S MAJOR 2

`PROTOCOL` rule 2 asks to be corrected with a measurement. **This is that, and it
changed what shipped.**

`TASK_150.md` states, as fact:

> *"because ASan structurally never reports a WRITE here (DEL must read `n->key`
> before it splices), **UBSan is the only witness of this row's WRITE harm shape
> anywhere in the tree**. Say that, with the counts and the mechanism."*

**I did not say that, because it is false.** `TASK_149` ran three of the four
adversarial blobs under `-fsanitize-recover=address` and **did not run
`adversarial-many.bin`**. I ran **all eight, on both compilers**
(`.temp/t150/asan_write_probe.sh`):

```
input                    cc     errs READ  WRITE  SEGV
adversarial-many         gcc    5    3     2      0     <<<
adversarial-many         clang  5    3     2      0     <<<
adversarial-uaf-write    gcc    7    6     0      1
adversarial-uaf-write    clang  7    6     0      1
adversarial-uaf-read     both   2    2     0      0
adversarial-uaf-head     both   2    2     0      0
the other four           both   0    0     0      0
HARDENED arm, all eight  gcc_h  0    0     0      0     <- negative control

every WRITE ASan reports:
  WRITE of size 1  c/kernel.c:143   n->val = (uint8_t)(a * 7u + 1u);   PUT's hit arm
  WRITE of size 8  c/kernel.c:213   n->hn->hp = n->hp;                 DEL's splice
```

**The second one is exactly the harm shape `c/kernel.h` tabulates.** So ASan
witnesses `p28`'s WRITE directly, on both compilers, reproducibly.

**What survives, and it is still a positive result — I shipped this instead:**

* the *ordering* half of the argument is right, and I confirmed it: in a
  **halting** build the first error is a `READ` on **all four** adversarial
  inputs, so **the gate's stage 7 can never show a WRITE**. That is a fact about
  the halting build, not about ASan;
* on **`adversarial-uaf-write.bin`** — the one input the header names for the
  WRITE shape — ASan gives 6 READs and a SEGV and no WRITE, because `n->lp` is
  tcache garbage and the splice faults first. **There, and only there, UBSan is
  the sole witness**, via clang's `store to misaligned address … for type
  'struct p28_obj *'`;
* ⚠ and what UBSan detects is **ALIGNMENT, not lifetime** — a different tcache
  word and it would be silent while the UAF was equally present. I wrote it as
  *UBSan sees an ARTEFACT of this row's harm*, not *UBSan detects it*.

**Second correction to the review, same finding:** `TASK_149`'s *"10/10 gcc and
9/10 clang"* is a **small-sample artefact**. Three samples of ten gave `(10,9)`,
`(9,10)`, `(9,8)`, so I measured the rate at 50 runs per compiler:

```
ubsan-only gcc,   adversarial-uaf-write   44/50  (88%)
ubsan-only clang, adversarial-uaf-write   45/50  (90%)
ubsan-only, the other 7 inputs, both cc    0/112
ubsan-only, HARDENED arm, 8 x 2 cells      0/16
```

The miss is the run where the SEGV wins the race. **`NOTES.md` 2b now says
"about nine runs in ten", not "10/10".**

---

## 1. MAJOR 1 — R1 DOUBLE-FREES. Reproduced, and landed.

Independently reproduced with the `-Wl,--wrap=malloc,--wrap=free` interposer
(copied from `.temp/t149/wrapfree.c`, which I did not modify; driver
`.temp/t150/repro_majors.sh`), **on the final sources**:

```
kernel           adversarial-uaf-write.bin  SLBWRAP DOUBLEFREE 0x5579604b84a0
                                            mallocs=4 frees=5 doublefree=1 livemallocs=0
kernel_hardened  adversarial-uaf-write.bin  mallocs=4 frees=4 doublefree=0 livemallocs=0
every other input, both arms                balanced, doublefree=0, livemallocs=0
```

**Real-allocator control, which is why nothing had seen it:** the same binary
without `SLBWRAP_NOFREE` exits **139 (SIGSEGV)** and never reaches the second
`free`; so does a plain build. The hardened arm exits 0.

**Which instrument sees it — I checked, rather than assumed:**

| instrument | verdict |
|---|---|
| the `--wrap` interposer | ✅ the only thing on this box that reports it |
| ASan **with `-fsanitize-recover`** | ✗ `grep -l 'double-free\|attempting free'` over every recovering log: **no match**. The SEGV is not recoverable |
| UBSan | ✗ does not look for it |
| Miri | ✗ drives the Rust rungs, which never recycle a slot |
| valgrind `memcheck` | ⚠ **cannot start here** — `Fatal error at startup … memcmp … ld-linux-x86-64.so.2`, the missing `libc6-dbg`. **UNTESTED, not silent** |

### What I changed

| file | change | cost |
|---|---|---|
| `spec.md` `idiom.required` (last entry) | the unscoped *"NEITHER C rung leaks and neither double-frees"* → scoped to the epilogue, with the measurement and the retraction | ⚠ **contract hash move, disclosed below** |
| `c/kernel.c` header | same sentence, plus *"ONE OMISSION, **THREE** HARM SHAPES"* | re-measure |
| `c/kernel.h:80-93` | the harm table gains a **CWE-415** row **and a "which instrument sees which" block** | re-measure |
| `spec.md` prose table (line 31) | two new rows: the PUT-hit WRITE and the double free | gate |
| `inputs/gen.py` | *"both harm shapes"* → *"ALL THREE"* | re-measure |
| `c/kernel.c:231`, `c/kernel_hardened.c:225` | ✅ **UNTOUCHED** — scoped to the epilogue and TRUE | — |

⚠ **A third harm shape I found that the task file did not name:** ASan's
`WRITE of size 1` at `c/kernel.c:143` is **PUT's hit arm storing `n->val` inside
the freed chunk** — a UAF write from a *third* opcode. `c/kernel.h`'s WRITE row
now names PUT as well as DEL.

---

## 2. MINORS

**1. `BaseException` — fixed, and the counterfactual is measured.** All **three**
catch sites (`detector_selftest` ×2, `_window` ×1) now spell
`except BaseException`, and `model.py:443`'s *"catches ANY exception"* comment is
corrected in place with a pointer from `NOTES.md` 7b to 7c.

```
the SAME planted SystemExit, against HEAD's model.py:  *** ESCAPED, diagnostic lost
                              against the file today:  returned, MUST-FIRE ARM BROKEN
```

⚠ **Reported as GENERAL, not `p28`'s**: every pattern with a must-fire arm spells
it `except Exception`. I fixed only `p28`, as scoped.

**2. The must-fire arm now licenses `sanitizer_expect` itself.** I took the
"extend" branch rather than the "say which" branch. `detector_selftest()` gained
**three cells**: it builds a real `Model` over each planted probe **from bytes —
no file opened, nothing under `inputs/` read** — and asserts the published string
**in both directions**. A new `_PROBE_QUIET` (same TRIM, then a different bucket)
supplies the `clean` half, because an arm that only ever expects `fires` is
satisfied by `return "fires"`.

**And the new arm owes the same test** (`.temp/t150/mustfire_probe3.py`):

```
mutation                             selfcheck   how        verdict
N0-control                           no problem  returned   OK
N2-per-filename-table                problem     returned   OK   <- INVISIBLE before
N3-expect-inverted                   problem     returned   OK
X1-always-fires                      problem     returned   OK   <- the QUIET probe catches it
X2-always-clean                      problem     returned   OK
N1-anyuaf-never-set                  problem     returned   OK
N4-detector-raises-BaseException     problem     returned   OK   <- ESCAPED before

mutations that ESCAPED the arm or crashed it: 0
```

Mechanism: `Model.__init__` gained `_file=None`, which only `_model_over()`
passes; `build(path)` — the gate's only entry point — is unchanged. Nothing in
the model sandbox's ban list is touched.

**3. Strict arguments on the three loose controls.** `harm_sites.py`,
`rust_arms.py`, `safety_line.py` gained an `_args()` that `argparse`-rejects
anything. Verified on all five:

```
harm_sites  rc=2 unrecognized arguments: --no-such-flag
rust_arms   rc=2 unrecognized arguments: --no-such-flag
safety_line rc=2 unrecognized arguments: --no-such-flag
proof_mutants rc=2 …        repro rc=2 …
git status patterns/: no controls/*.json touched   <- nothing ran
```

⚠ **Deliberately no `--list` literal anywhere**, because
`synthesis/synthesize.py:558` runs only scripts whose source contains it. The
rewrite behaviour is documented **where a reader will hit it**: `NOTES.md`'s
opening block (not a footnote) *and* each `_args()` docstring.

---

## 3. RIDE-ALONGS — all four landed

1. **`B4`/`B5`/`B6` + `B3` + `B1`/`B2`** → `NOTES.md` **6a-bis**, with the
   `rec_close`-at-three-sites table and the honest scope statement (*"licences to
   read, not obligations to release"*), flagged as the **fourth** affine-token
   instance. `B3`'s *fails in `main`, not `kernel`* is recorded as **in `p28`'s
   favour** and as an arm the battery does not have.
2. **Deliverable 4** → `NOTES.md` **8a**, `*"mechanism not investigated"*`
   struck: the walk **HOIST** at **72%**, paid per operation (`+38%` no walk,
   `+1.9%` 30-deep), R3 5% **cheaper** on the TRIM path, and *"the rung's NAME is
   aspirational and the port is fair"*. Also written into `safe_tuned.rs`'s
   header as **the fourth lever it did not list**.
3. **The failed attack** → `NOTES.md` **4c**: 3 257 436 exhaustive + 20 000
   randomised, 0 VALDIFF, 0 SUFFIX, **17 687/20 000 truncating**. ✅ **The hedge
   is replaced by the three-step proof AND ITS TWO HYPOTHESES** (eviction order =
   chain order; slots never recycled), in `NOTES.md`, `arm_safe_bug.rs` and
   `safe_naive.rs`. The *"only trace"* wording is narrowed to **80% of random
   windows**.
4. **`miri_iters = 4`** disclosed where the Miri silence is claimed (§4b).

**Free corrections I took because the file was already being re-measured** (all
reported, none scope creep):

* `c/kernel.c:45`'s *"a variable the freeing code CAN see"* clause — **measured
  wrong twice over** (`bucket[]` is a stack array in that very frame, and
  `kernel_hardened.c` writes `bucket[vb]` from inside TRIM). Rewritten around the
  **cursor**, which is the true distinction.
* `rust_arms.py`'s pinned `invariant`: the retracted *"or a wrong answer"* and the
  garbled *"its checksum and its checksum differs"*.
* `model.py`'s `_window` docstring (2-tuple → 3), and its `sanitizer_expect`
  docstring naming **two** firing inputs where the derivation fires on **four**.
* `NOTES.md` §5's *"BUG arm equals `c/kernel.c` on the benign ones"* — **I
  re-derived it: 16 cells, `raw_bug != c_bug` in 0**, `adversarial-uaf-write` is
  `[-11, '']` on both sides. It equals on all eight, SIGSEGV included.
* `model.py`'s module docstring gained the honest limit that **the model cannot
  represent the double free at all** — a `released` flag has no allocator.

---

## 4. RULE 6 DISCLOSURE — and `p28` never had one

⚠⚠ **`p28` SHIPPED WITH NO `PROTOCOL` RULE 6 DISCLOSURE AT ALL.**
`grep -n 'sha256' patterns/p28-intrusive-lists/NOTES.md` was **empty**. `TASK_146`
never recorded the pre-build hash and `TASK_149` did not raise it. **That evidence
is unrecoverable** — the pattern landed in one commit, so `git show HEAD:` cannot
distinguish *first written* from *shipped*. Recorded as such in `NOTES.md` §10 so
nobody reads the table below as a pre-build snapshot.

`python3 harness/tools/contract_diff.py p28`:

```
block sha256  HEAD:  5c92154096baea5de8f8fd4c24a16c6d285000687bd6006782837db00d724455
block sha256  tree:  f0bd1f608df27895eed33e180bc1ba75b7c87f2a83b13829acbbc8ac778a081c

collapse IDENTICAL · driver IDENTICAL · ensures IDENTICAL · identity IDENTICAL
idiom.forbidden IDENTICAL · idiom.why IDENTICAL · kernel IDENTICAL · miri IDENTICAL
model IDENTICAL · note IDENTICAL · requires IDENTICAL · verus IDENTICAL
idiom.required ⚠ MOVED      2 path(s) moved: ['idiom', 'idiom.required']
```

**One entry moved: the epilogue entry the measurement refuted.** ✅ **It pins no
new spelling** — `required` carried **32** backticked spellings before and **32**
after, over the same 12 entries, so no rung gained or lost an obligation
(checked against `git show HEAD:` programmatically, not by eye).

---

## 5. THE RE-MEASURE — prediction first, then the comparison

⚠ The prediction is in **`.temp/t150/measure_prediction.md`**, written **before**
the run; the outcome was appended after.

**Predicted to move:** 6 `source_sha256` entries, timestamps/git, every wall-clock
leaf. **Predicted NOT to move:** every `Ir`, every `md5_fn`, every checksum,
identity, **every `model` string and therefore `sanitizer_expect`**, adversarial
rows. I checked the model strings against `git show HEAD:results/…json` *before*
running rather than reasoning about it.

```
leaves: HEAD=1349  NEW=1349  MOVED=105  only-in-HEAD=0  only-in-NEW=0
   source_sha256       6
   timestamp/git       3
   wall-clock         96
every OTHER leaf: (none)

every Ir leaf        97 leaves, moved=0        every md5/asm hash  160, moved=0
every checksum       64 leaves, moved=0        model strings         8, moved=0
input blob hashes     8 leaves, moved=0        adversarial rows         moved=0
```

✅ **Exact hit, including the part the task file flagged as possibly legitimate:
`model.py` changed and no `model_stdout` / `sanitizer_expect` moved.** And the
comment lines I added shifted every statement in `c/kernel.c` and `c/kernel.h`
down by 22 without moving a single `md5_fn`, which is the one outcome that would
have been a finding. (`p46` moved 111/1371, `TASK_147` 103/1366 — same shape a
third time.)

### ⚠⚠ MY ONE PROCESS ERROR, AND IT COST A SECOND MEASURE RUN

**I edited `model.py` while `measure.py` was running.** `measure.py` calls
`provenance()` at **line 450, before the measurement loop**, so the completed
record carried the pre-edit hash and `--check-stale` reported
`STALE … model.py`. **The task file said budget one re-measure; I spent two**
(4 m 34 s + 4 m 32 s).

I could have reverted the edit to save the run. I did not, because the edit fixed
`detector_selftest()`'s docstring still saying *"Four cells"* for what is now a
seven-cell arm — header rot in the very file this task exists to correct
(`PROTOCOL` rule 13). **I then re-read the whole of `model.py`'s diff and made it
final before re-running, so it happened exactly twice and not three times.**
The lesson generalises and is worth a `.memory/` line: **`measurement_sources` is
hashed at the START of `measure.py`, so any edit to a hashed file during the run
silently invalidates it.**

---

## 6. CONTROL SIDECARS — regenerated after the sources were final

`c/kernel.c`, `c/kernel.h` and three `controls/*.py` are pinned by four of the
five sidecars, so they had to be regenerated (a stale pin is `rep.fail("tables")`,
not a warning).

```
safety_line.py   0.14 s   +9 / -0, 392 / 401 preprocessed  <- UNCHANGED
harm_sites.py    0.94 s   ctl fires both compilers; head/interior both reached
repro.py        20.3 s    every cell 1 distinct behaviour; ASLR control 20/20 FIRED
rust_arms.py    13.9 s    raw_fix==c_fix on all 8; Miri ub=True on 4 raw_bug cells only

pin check:  harm_sites 3/0 stale · proof_mutants 2/0 · repro 7/0 · rust_arms 6/0 · safety_line 4/0
```

**Leaf diff of the sidecars against `HEAD` — nothing measured moved:**

```
harm_sites     52 leaves  moved=2  {derived_from_sha256:1, measured_utc:1}
repro         114 leaves  moved=3  {derived_from_sha256:2, measured_utc:1}
rust_arms     332 leaves  moved=6  {derived_from_sha256:4, invariant:1, measured_utc:1}
safety_line    20 leaves  moved=4  {derived_from_sha256:3, measured_utc:1}
proof_mutants  81 leaves  moved=0
```

The single `invariant` move is the retracted-prediction rewrite I made
deliberately. **`proof_mutants.json` is untouched and still FRESH**, which is why
I did not spend its ~40 minutes.

---

## 7. THE GATE

### Run 1 — FAIL, on `[tables]` only, which is the flow the task file predicted

`harness/check.py p28`, **36 m 33 s**. Read out of the RECORD, never grepped:

```
verdict   FAIL      failures 2      blocked []   (i.e. 0)
loud      2         [collapse-ir]  [tcb-unsafe]   <- both documented, both expected
contract  f0bd1f608df27895eed33e180bc1ba75b7c87f2a83b13829acbbc8ac778a081c
```

**Both failures are the same thing and both are `section: "tables"`:**

1. `results/tables/p28-intrusive-lists.md` *"cites contract `5c92154096ba` and
   `spec.md`'s `slb-contract` block now hashes to `f0bd1f608df2`"*;
2. the same table *"is STALE IN ITS CONTENT: 40 line(s) differ"* — and the
   diff is exactly my edit: the old unscoped *"NEITHER C rung leaks and neither
   double-frees"* against the new scoped sentence, plus the contract short-hash
   in two footers and the generation timestamp.

**Nothing else failed.** The task file anticipated this precisely
(*"`harness/report.py p28` if the gate fails on `[tables]`"*), and stage 9c's own
message prescribes the fix: *"it is the same two commands as stage 9:
`harness/report.py p28`, then gate again."* So this is the designed path for a
contract move, not a defect.

**Everything substantive was green in run 1**, and it is worth listing because it
is the evidence that my edits changed no behaviour:

```
0b   idiom: 12 required / 12 forbidden; forbidden 0 hit(s) over 24 spellings
     (and `c/kernel.h` is in the forbidden scan -- my new comment adds none)
     audit 162 (spelling, rung) pairs, 12 scoped-absent -- unchanged shape
1    32/32 cells built
2    all 32 cells agree on small / large / degenerate
3a   unsafe O3 isolated 360/356 == verus O3 isolated 360/356   <- identity pin holds
4    adversarial table records the expected divergences
5a   verus.rs: 23 verified, 0 errors -- matches the pinned obligation count
5c   8 clause deletions, every one load-bearing; control 23/0
5c-req  13 `requires` conjuncts, none a tautology
5c-twin 28 verified, 0 errors with --cfg slb_twin -- matches the pin; all 5
        twins fail when their conjunct alone is deleted
```

`harness/report.py p28` → `wrote results/tables/p28-intrusive-lists.md`.

### Run 2 — ✅ **PASS**

`harness/check.py p28`, **36 m 46 s**, `GATERC=0`. Read out of the RECORD:

```
verdict   PASS
failures  0     []
blocked   []    -> 0
loud      2     ['collapse-ir', 'tcb-unsafe']    <- both documented, both expected
contract  f0bd1f608df27895eed33e180bc1ba75b7c87f2a83b13829acbbc8ac778a081c
```

⚠ **On the `blocked` expectation in the task file** (*"expect `p01 = 1`,
`p42 = 1`"*): that is a whole-tree figure. I ran **`check.py p28` only**, as the
task file's *Then* section specifies, and `p28`'s own `blocked` is **0** — the
same as the reviewer's run. I did not run the full-tree gate and cannot speak to
`p01` or `p42`.

---

## 8. THE FOUR DOWNSTREAM CHECKS — all green

```
harness/measure.py --check-stale     58 record(s) examined, 0 STALE      <- as required
harness/tools/composition.py --check OK: published composition table matches
                                     the tree (29 patterns, 10 classes)   rc=0
harness/tools/temp_citations.py      OK  (new=0 unclassified=0 resolved=1) rc=0
python3 synthesis/synthesize.py      wrote results/synthesis.md (80756 bytes, 596 lines)
```

### ⚠ Deliverable 2 — RESOLVED

```
BEFORE:  Patterns: **28**   p28 mentions: 0
AFTER:   Patterns: **29**   p28 mentions: 10
```

✅ **And `results/SYNTHESIS.md` (CAPITALS, hand-written) is byte-identical** —
`md5 47e5a863043fbf723af6646c77396230` before and after, checked explicitly
because the task file flags it twice. It does not appear in `git status`.

⚠ **One note on `temp_citations.py`'s `resolved=1`.** It reports
`.temp/build/p28-repro` as *"NO LONGER DANGLING"* — because **I ran
`controls/repro.py`, which creates that directory**. It is `OK`, not a failure,
and it is the same mechanism `TASK_149` documented from the other side
(`proof_mutants.py` *deletes* the directory it cites, so *dangling* is the
correct steady state and *present* is the transient). **Pruning it needs
`--update`, which edits `harness/tools/temp_citations_baseline.json` — the
manager's file, added by the manager mid-review — so I left it alone.** If the
directory is removed again the entry goes back to dangling and the baseline is
correct as written.

---

## 9. WHAT I DID NOT DO

* **I did not run `controls/proof_mutants.py`** (~40 min; `A3` alone is ~25 of
  it). Its JSON is FRESH — `verus.rs` and `proof_mutants.py` are both untouched
  by me — so `B3` is **not** added to the battery, the mutant file name is still
  not held at `verus.rs`, and its `invariant`'s retracted `A6` prediction still
  stands. All three are recorded in `NOTES.md` §9 as owed, with the price.
* **I did not run the full-tree gate**, only `check.py p28`.
* **I did not touch `.memory/`, `RECAP.md` or `results/SYNTHESIS.md`.** `RECAP`
  56's dangling-pointer overstatement and `CAVEATS["p28"]` are the manager's.
* **I did not re-run `TASK_149`'s attacks** — the exhaustive/fuzz sweep, the
  `alive_link` instrumentation, the `B0`–`B6` proof arms and the lever
  experiment are **quoted** from `TASK_149`, attributed as such in `NOTES.md`,
  and not re-derived. It called the safe-Rust attack a clean negative; I took it.
* **I did not add a `--list` literal to any control**, deliberately:
  `synthesis/synthesize.py:558` runs only scripts whose source contains it.
* **valgrind `memcheck` is UNTESTED, not silent** — it cannot start on this box
  (`libc6-dbg`). I recorded that distinction rather than writing it into the
  instrument table as a negative.

## 10. UNSURE / OWED

1. ⚠ **The `.memory/` write-up of Major 2 must not say *"UBSan is the only
   witness of the WRITE anywhere in the tree"*.** My measurement refutes it
   (§0). The true statement is narrower and is in `NOTES.md` 2b.
2. ⚠ **`.memory/03-measurement.md` deserves the process line from §5**:
   `measure.py` hashes `measurement_sources` at line 450, **before** the
   measurement loop, so editing a hashed file mid-run silently produces a STALE
   record. That cost me a run and is not written down anywhere.
3. ⚠ **The `except Exception` hole is TREE-WIDE.** I fixed `p28` only. Every
   pattern with a must-fire arm has it, and so does the last-hop gap.
4. **The UBSan diagnostic is ~88–90%, not deterministic.** If anyone wants a
   pinned figure they should run more than ten.

---

**PROTOCOL rule 2 running count: launched from 769
(`TASK_149_REPORT.md`'s closing paragraph), carried to 785** — branch delta
**+16**. ⚠ Reconciliation across any concurrent branch is the manager's job, not
mine.

1. ⚠⚠⚠ **The task file's Major 2 is HALF WRONG and I did not ship it.** ASan
   **does** report heap-use-after-free WRITEs — two, on `adversarial-many.bin`,
   on both compilers — at `c/kernel.c:143` (PUT) and `:213` (the DEL splice).
   `TASK_149` never ran that blob under `-fsanitize-recover`.
2. **What survives is narrower and still a result**: on `adversarial-uaf-write`
   ASan gives 6 READs + a SEGV and no WRITE, so **there** UBSan is the only
   witness; and in the gate's HALTING build the first error is a READ on all
   four adversarial inputs, so the gate can never show a WRITE.
3. **`TASK_149`'s "10/10 gcc, 9/10 clang" is a small-sample artefact** — the
   rate is **44/50 and 45/50** over 50 runs.
4. **R1's double free reproduced independently**: `mallocs=4 frees=5
   doublefree=1` against R1h's `4/4/0`, and the real allocator SEGVs (rc 139)
   before reaching it.
5. **No instrument on this box sees the double free except an allocator
   interposer** — ASan never reaches it even with `-fsanitize-recover`, and
   valgrind cannot start. **A harm can be structurally invisible because an
   earlier harm on the same path crashes first.**
6. ⚠ **`p28` had NO `PROTOCOL` rule 6 disclosure at all**, and that evidence is
   unrecoverable. Recorded as such rather than faked.
7. **The contract moved `5c921540…` → `f0bd1f60…`, one entry, `idiom.required`,
   and it pins no new spelling** (32 backticked spellings before and after).
8. **The `BaseException` hole is measured, not argued**: the same planted
   `SystemExit` escapes `HEAD`'s `model.py` and is caught by today's.
9. **The must-fire arm now licenses the PUBLISHED string**, in both directions,
   and its own 7-mutation battery has **0 escapes** — including `N2`, which
   `TASK_149` measured invisible.
10. **The re-measure prediction was an exact hit**: 105 of 1349 leaves, all
    source hashes / timestamps / wall clock; zero `Ir`, md5, checksum, identity,
    model string or adversarial movement — **`model.py` changed and
    `sanitizer_expect` did not move.**
11. ⚠ **My one process error, disclosed**: I edited `model.py` mid-run and spent
    two measure runs instead of one. `measurement_sources` is hashed at the
    START of `measure.py`.
12. **`NOTES.md` §5 understated the raw-pointer port**: `raw_bug == c_bug` on
    **16 of 16** cells, SIGSEGV included, not just the benign ones.
13. **`c/kernel.c:45`'s distinction was wrong twice over** — `bucket[]` is a
    stack array in that frame *and* the freeing code writes it. Rewritten around
    the **cursor**, which is the real difference.
14. **Deliverable 2 resolved**: `results/synthesis.md` now carries `p28`,
    `Patterns: 29`, with `SYNTHESIS.md` byte-identical.
15. **Gate PASS**, 0 failures, 0 blocked, 2 documented louds — after one
    `[tables]`-only failure that the task file predicted and `report.py` fixed.
16. **All five controls now reject unknown arguments**, and the fact that they
    rewrite committed JSON is documented where a reader will hit it.

⚠ **A rigour signal, not a ledger.**
