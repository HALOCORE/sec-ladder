# TASK_154 report — `p34` built: manual reference counting, the temporal axis's fifth row

**Role: research engineer.** Everything below was run; command output is quoted
rather than described. `patterns/p34-refcount-stack/NOTES.md` is the durable
record and this file is the task-shaped one.

---

## 0. PROTOCOL definition-of-done rule 6 — the contract hash, and WHEN it was written

**`contract_sha256` as first written, before any measurement:**

```
1fa98c8af297710166a2c93731f12b45be7c2c9b4dc39331fcd06203fae8f3dd
```

Recorded in `.temp/t154/NOTES.md` at the moment the `slb-contract` block was
first written and **before `harness/build.py`, `harness/check.py` or
`harness/measure.py` had ever been run on p34** — at that point
`results/gate/p34-refcount-stack.json` and `results/p34-refcount-stack.json` did
not exist.

⚠ **TWO DISCLOSURES ABOUT THAT HASH, BOTH AGAINST ME:**

1. **The scratch note recorded the wrong SPAN.** It wrote
   `7216cbf11a642b3d8fe46150dc6ca3c7f7c5d98c2f05c0e2db4c50d3e4a1faa3`, which is
   the same block hashed one newline shorter than
   `check.py::read_contract`'s `r"```slb-contract\s*\n(.*?)```"`. Same bytes,
   different span. The figure above is the gate's convention and is what a
   reviewer should compare against; `.temp/t154/NOTES.md` is left as written.
2. ⚠⚠ **ONE PIN MOVED AFTER THE FIRST FULL GATE RUN, AND THE GATE IS WHAT
   MOVED IT.** The block as first written carried **all five** of vstd's
   `allocate` `ensures` on `rec_alloc`, on my reasoning that a copy of a vstd
   item should be a faithful copy. Stage 5c disagreed:

   ```
   [clause-mut] verus.rs rec_alloc ensures[1] is NOT load-bearing: deleting
   `pt.0.addr() + size <= usize::MAX + 1` still gives 24 verified, 0 errors.
   ```

   It was deleted — a strict WEAKENING of a trusted item, the direction the gate
   asks for. `contract_sha256` moved to
   **`f1537d7f601175122e67f9991a107449ad7ca52520b0484f5f014685369d2762`**;
   nothing else in the block changed. The edit also touched `verus.rs` and
   `unsafe.rs` doc comments, which are MEASUREMENT-hashed, so
   `harness/measure.py p34` was re-run: **every `Ir`, every static count and
   every md5 in `results/p34-refcount-stack.json` is unchanged** — an `ensures`
   is ghost and erases before codegen. `NOTES.md` §0 and §6d.

⚠ **Disclosed precisely rather than tidily**, because p46 shipped a rule-6
disclosure that reconstructed perfectly over a `why` measurement had already
falsified. **Three pins in that first block came from PRE-GATE probes rather than
from imagination:**

| pin | value | probe |
|---|---|---|
| `verus.obligations` | 24 | `.temp/t154/verus/obligations.{sh,log}` |
| `verus.twin_obligations` | 29 | `./verus_run.py verus.rs --cfg slb_twin` |
| `identity O0/O3` | `norel`/`norel` | `harness/asm.py diff` on hand-built `--cfg slb_isolated` pairs |

⚠ `git show HEAD:…/spec.md | diff -` is **VACUOUS on a new pattern** and is
deliberately not cited: it compares the working tree to HEAD, p34 lands in one
commit, and on a clean tree it always prints nothing. **The recorded hash is the
only evidence.** ⚠ **And the hash DID move once** — disclosure 2 above — so the
sentence a reader wants is: *the block was written once, edited once, and the
edit was deleting a conjunct the gate reported as not load-bearing.* Nothing was
strengthened and nothing was added.

⚠ **Rule 6's added step, applied**: every number in the hashed `why` and in every
rung source's doc comment was re-read against the measurements before finishing.
`+1 / −0`, `0.00`, *checksums bit-identical on two shapes*, *UBSan silent*,
*78 lines and no `Rc` spec*, *`global layout` checked by rustc* — all measured,
none falsified. `NOTES.md` §0.

---

## 0a. Deliverable coverage

| # | deliverable | where |
|---|---|---|
| 1 | build `patterns/p34-refcount-stack/`, gate PASS, `measure.py` records it | §1, §11 |
| 2 | `model.py` not transliterated, no tautological check, `sanitizer_expect` decided first | §3 of `NOTES.md`; **DERIVED, not declared — the task's prediction was wrong** |
| 3 | R5 ATTACK arm + VACUITY arm + `p35`'s `X1` | §6, `controls/proof_mutants.py`, 6 arms |
| 4 | two-sided spelling search before any rung-to-rung figure | §8, `controls/spellings.py` — **it caught one** |
| 5 | tell the manager the bug class for `composition.py` | §9 |
| 6 | rule-6 `slb-contract` sha256 recorded before building any cell | §0 — **with two disclosures against me** |
| — | novelty claim derived, not inherited | §5 — **FALSE on both halves** |
| — | the manager's named safe-Rust call | §2 — **CONFIRMED, stronger than predicted** |
| — | headline 1 (`0.00`) and headline 2 re-derived at both levels, both compilers | §3, §4 |
| — | stage `7h`, and `verus.assumptions` if any `assume(`/`admit(` | §11; **no `assume(` or `admit(` anywhere in p34, so no declaration is owed** |

---

## 1. What was built

`patterns/p34-refcount-stack/`, 34 committed files: seven rungs
(`c/kernel.c`, `c/kernel_hardened.c`, `c/main.c`, `c/kernel.h`, `safe_naive.rs`,
`safe_tuned.rs`, `unsafe.rs`, `verus.rs`), `spec.md` with the machine-readable
pins, `model.py`, `inputs/gen.py`, `NOTES.md`, `README.md`, and **seven controls**
(`safety_line`, `no_dup`, `detectors`, `safe_arms`, `rust_bug`, `spellings`,
`proof_mutants`) with their `.json` sidecars and five control arm sources.

Name kept as `p34-refcount-stack` (the task allowed confirm-or-improve).

---

## 2. THE MANAGER'S NAMED CALL — CONFIRMED, AND STRONGER THAN PREDICTED

> *"`p34` uses the real allocator, so an owned/`Rc` safe port should land in
> `p28`'s shape (cannot reproduce), while an INDEX-ARENA port recycles its own
> storage and should land in `p32`'s shape (reproduces exactly) — putting BOTH
> BRANCHES OF THE LAW IN ONE ROW, SELECTED BY THE PORT CHOICE."*

`controls/safe_arms.py`, exit 0:

```
BRANCH A -- the `Rc` port: is the SEPARATION available?
  safe_naive.rs            COMPILES   -
  arm_safe_rc_move.rs      REJECTED   E0507   cannot move out of `*t` which is behind a shared reference
  arm_safe_rc_borrow.rs    REJECTED   E0502   cannot borrow `objs` as mutable because it is also borrowed as immutable

BRANCH B -- the INDEX-ARENA port: does it reproduce c/kernel.c?
  input                          arena_bug             c/kernel.c          arena_retain               model
  adversarial-blind.bin       5576862673510090752   5576862673510090752  5576862673510090752  5576862673510090752  ==
  adversarial-blindread.bin  12442434272084377600  12442434272084377600 12442434272084377600 12442434272084377600  ==
  adversarial-many.bin        5628475829885786112   5628475829885786112  2893199866468423680  2893199866468423680  ==
  adversarial-recycle.bin    16102462438644451328  16102462438644451328  7544618244297525248  7544618244297525248  ==
  adversarial-stride3.bin                       0                     0                    0                    0  ==
  degenerate.bin             12018165609759525888  12018165609759525888 12018165609759525888 12018165609759525888  ==
  large.bin                   7726184805965551230   7726184805965551230  7726184805965551230  7726184805965551230  ==
  small.bin                  13533250923909195085  13533250923909195085 13533250923909195085 13533250923909195085  ==

Miri on the ARENA arm: no UB on all 8 inputs.
```

**Both branches of `.memory/01-ladder.md`'s temporal law, in ONE row, selected by
the PORT.** The prediction is confirmed; **the arena arm is stronger than
predicted** — it does not merely reproduce the bug, it reproduces the **recycle
divergence** (`16102462438644451328`), the one cell whose value depends on the
allocator handing the same block back. `#![forbid(unsafe_code)]` safe Rust
reproducing the exact output of a use-after-free.

⚠ Two must-fail arms rather than one, because a single rejection shows a spelling
is unavailable, not that the SEPARATION is. They cover the two ways a program can
hold a second reference — **own it** (E0507) or **borrow it** (E0502) — and safe
Rust closes both for different reasons. The sanity arm (`safe_naive.rs` compiling
on the same command line) is what stops two failing builds from proving nothing.

⚠ **What it does NOT settle**, said so nobody reads it as more: nothing here says
which port an author would choose. `Rc::clone` incrementing unconditionally is a
finding about **what safe Rust removes — the SITE of the bug** — and not a claim
that safe Rust removes the bug CLASS.

---

## 3. HEADLINE 1 — `0.00` predicted from the proof, then MEASURED, at both levels and both compilers

`.temp/t154/marginal.py`, the same difference-of-two-runs method
`check.py::check_marginal_ir` uses (Ir at 200 iterations − Ir at 100, over 100):

**`R1h − R1 = +0.00` Ir/call on ALL SIXTEEN CELLS** — 2 inputs × 2 opt levels ×
2 inline modes × 2 compilers. Kernel-exclusive `Ir` in
`results/p34-refcount-stack.json` is bit-identical too (`c-gcc` and `c-gcc-h`
both `171,353,731` on small at `O3/isolated`; both `325,624,819` at
`O0/isolated`). Wall clock agrees inside its 1.3–2.9 % spread.

⚠ **And the GATE'S OWN `marginal_ir_per_call` corroborates it independently** —
`results/gate/p34-refcount-stack.json` carries all 16 R1 and 16 R1h figures and
`c-clang` equals `c-clang-h` (and `c-gcc` equals `c-gcc-h`) **to the last decimal
in every one of the eight (input × opt × mode) cells**, e.g.
`c-clang/O3/isolated/large.bin = c-clang-h/O3/isolated/large.bin = 11293.47`.
So the `+0.00` does not rest on my probe script alone.

⚠⚠ **AND THE STATIC COUNT IS NOT ZERO — the part worth publishing beside it:**

| | R1 | R1h | Δ |
|---|---:|---:|---:|
| gcc `-O3` `kernel`, pad-excluded | 286 | 287 | **+1** |
| clang `-O3` | 135 | 136 | **+1** |
| gcc `-O0` | 218 | 223 | **+5** |
| clang `-O0` | 203 | 208 | **+5** |

So *"the safety line is free"* is true of **executed** instructions and false of
**emitted** ones. p34 is the cleanest instance of that distinction in the tree.

**The hard constraint is enforced, not assumed.** `controls/no_dup.py` censuses
the shipped blobs by walking the cursor the rungs walk: **0 executed DUP ops on
every matrix input, 48 across the adversarial ones.** It is checked in three
independent places — `inputs/gen.py` cannot emit one and re-checks what it wrote,
`model.py::no_dup_problems` re-derives it from the shipped blob on **every gate
invocation**, and this control censuses the directory.

**The safety line is `+1 / −0` preprocessed lines** (`controls/safety_line.py`),
the smallest in the tree — **and p34 adds a second half `p32` does not have**:
`controls/arm_body.inc` is `TASK_143`'s include-twice body, and the control
requires it to preprocess to **each shipped file exactly** (`IDENTICAL 332/332`
and `333/333`). A diff of two hand-written files proves the difference is small;
it cannot prove it is the intended one.

---

## 4. HEADLINE 2 — re-derived at BOTH levels on BOTH compilers, as required

`.temp/mgr149/NOTES.md`'s table was **gcc `-O1` only**. `.temp/t154/demo/` is a
copy of its sources (mgr149 untouched) built at gcc/clang × `-O0`/`-O1`/`-O3`:
**all 48 rows reproduce identically; there is no compiler or level dependence at
all.** `controls/detectors.py` then re-derives it on the SHIPPED pattern inputs
across **twelve build lines** (plain/ASan/UBSan × gcc/clang × `-O0`/`-O3`), exit 0:

| input | R1 | R1h | | ASan | UBSan |
|---|---|---|---|---|---|
| `adversarial-blind` | 5576862673510090752 | 5576862673510090752 | **IDENTICAL** | fires | silent |
| `adversarial-blindread` | 12442434272084377600 | 12442434272084377600 | **IDENTICAL** | fires | silent |
| `adversarial-recycle` | 16102462438644451328 | 7544618244297525248 | diverges | fires | silent |
| `adversarial-many` | 5628475829885786112 | 2893199866468423680 | diverges | fires | silent |

**Two bug classes separated by which instrument sees them, and the pair is what a
checksum-only gate misses.** R1h is clean on every input on every one of the
twelve build lines.

**Three cells `.temp/mgr149` did not have:**

1. ⚠ **HIGH-ITERATION STABILITY.** R1's release path *writes* `o->rc - 1` into a
   freed block, onto glibc's tcache `next` word, and the harness calls the kernel
   up to 200 000 times per run. mgr149 ran `iters=1`. Measured at 10 / 1000 /
   200 000 on six builds: **no crash, no abort, identical checksums**, and
   `n = 1` in 20 runs at `iters = 200000`. Without this the adversarial inputs
   could not have carried the full `n_iters`.
2. **UBSan is SILENT on every input at every level on both compilers**, and that
   is derived (p34's UB is purely temporal — every index is inside `stk[]` in
   both rungs) and **licensed**: `controls/ctl_ubsan.c` fires on all four UBSan
   lines and is silent on all four plain ones, while `controls/ctl_asan.c` fires
   on all four ASan lines and is **silent on every UBSan line**. That last row is
   the measured evidence for *a positive control licenses only the detector it
   fires in*, not an appeal to it.
3. **p27's `adversarial-noreuse` hazard does not reach p34** — the stale read's
   value is NOT a function of the optimisation level or of ASLR, because `data`
   starts at offset 16, clear of the tcache words.

---

## 5. ⚠⚠⚠ THE NOVELTY CLAIM IS FALSE ON BOTH HALVES — derived from `results/gate/p*.json`

The task wrote it as a belief to be attacked:

> *"no built temporal row has a cell that is reproducible AND checksum-divergent
> AND detector-firing at once, and nothing in the tree has the detector-only
> pair"*

`.temp/t154/novelty.py` derives both halves from **every** gate record.
Definitions, all read out of the RECORD and never from a log: *detector-firing* =
`sanitizer[<input>].fired`; *checksum-divergent* = `diverges` on the C R1 rows of
`adversarial[<input>/c-gcc|c-clang]`; *reproducible* = those rows carry exactly
ONE behaviour across opt × mode and both compilers agree.

**HALF 1 — FALSE.** The triple is not rare and it is not new to the temporal
axis: **31 cells tree-wide**, and **5 of them on BUILT TEMPORAL rows** —
`p27/adversarial-uaf.bin` and **all four** of `p28`'s adversarial inputs
(`-many`, `-uaf-head`, `-uaf-read`, `-uaf-write`).

**HALF 2 — ALSO FALSE.** The detector-only pair exists in **4 cells**:
`p18/adversarial-sat.bin` and all three of `p42`'s (`-mixed`, `-notag`,
`-win1`).

**What survives, stated narrowly and derived rather than asserted:**

* `p18` is the **`ub-not-mem`** axis (a saturating shift, UBSan) and `p42` is
  **`resource`** (a leak, LSan). **`p34` is the first TEMPORAL row with a
  detector-only cell** — and it has two of them.
* ⚠ **"Both shapes in one row" is NOT new either**: `p18` already has three
  triples and one pair. What `p34` adds is both shapes **where the detector is
  ASan and the harm is a use-after-free**, i.e. where the silent cell is a read
  of freed heap that happens to return the right byte.

**So the sentence to publish is the narrow one, and the manager's is retracted.**

---

## 6. The R5 — 24/0, seven trusted items, all twinned, and the first multiset obligation

`24 verified, 0 errors`; twin configuration `29 verified, 0 errors`. **TCB seven
items, exactly `p27`'s seven, and the reference-counting obligation costs none of
them. Every one has a verified twin and NONE is blocked.**

**The obligation is not `p27`'s and could not be.** A `PointsTo` is LINEAR and
p34's subject is ALIASING — two stack entries naming one object is the normal,
correct state — so the permission is keyed by OBJECT and the proof carries the
bridge:

```
perms[k].value().rc == cnt(ids, k)
```

`cnt` is an occurrence count over a `Seq<int>` with five supporting lemmas: **the
first multiset-flavoured obligation in this tree.** **Leak-freedom falls out as a
corollary** — `obj_ok` requires `cnt(ids,k) > 0` and the epilogue empties the
stack, so `perms.dom()` is empty when the kernel returns. ⚠ What that does NOT
say: Verus does not force a tracked resource to be consumed, so a rung that
dropped the map would verify.

`controls/proof_mutants.py`, 6 of 6 as expected:

```
  M0-control               control      expect=verify got=verify OK  24/0 []
  M1-delete-retain         attack       expect=fail   got=fail   OK  23/1 ['assertion failed']
  M2-constant-body         vacuity      expect=fail   got=fail   OK  21/1 ['postcondition not satisfied']
  X1-delete-rc-conjunct    attack       expect=fail   got=fail   OK  22/2 ['precondition not satisfied']
  X2-exec-and-spec         spec-weaken  expect=fail   got=fail   OK  22/2 ['precondition not satisfied']
  M3-delete-epilogue       deletion     expect=fail   got=fail   OK  23/1 ['assertion failed']
```

⚠⚠ **`X1` and `X2` are the two to read, and both come from other rows' results.**

* **`X1` is `p35`'s arm** — strike the central obligation out of the invariant and
  see whether anything but a hand-written pin notices. **On p35 it VERIFIED at
  the pinned count.** **On p34 it FAILS, on `precondition not satisfied`.**
* **`X2` is `p32`'s arm** — weaken the exec code AND the invariant together.
  **On p32 it VERIFIES**, which p32 publishes as *the safety line is load-bearing
  against the SPECIFICATION alone*. **On p34 it FAILS, again on a precondition.**
  **That is the sharpest difference between the two rows' R5 results, and it is
  exactly the difference the storage makes.**

**What the pinned vstd does not have, reported as a RESULT:**
`~/tools/verus/vstd/std_specs/smart_ptrs.rs` is **78 lines** with **zero**
occurrences of `strong_count`, `Rc::clone`, `into_raw`, `from_raw` or
`increment_strong_count` — and `grep -rn` over the whole of `std_specs/` finds
none either. So the R5 models the counter itself, which is what the C rung does.

⚠⚠ **NEW, AND WORTH THE MANAGER'S ATTENTION: THE LAYOUT FACT IS A `global layout`
DIRECTIVE, NOT AN AXIOM.** `vstd::layout::size_of` is **uninterpreted** for a
user struct, so neither `rec_alloc`'s `size != 0` nor
`PointsToRaw::into_typed`'s alignment precondition can be discharged without
telling Verus the layout. `global layout Obj is size == 24, align == 8;` does
that at **zero obligations and zero trusted items**, and **rustc CHECKS it at
codegen** — measured: with `size == 32` the file still reports `9 verified,
0 errors` and then fails with `error[E0080]: evaluation panicked: does not have
the expected size` (`.temp/t154/verus/probe3.rs` vs `probe3_bad.rs`). It is the
one layout fact in this tree the COMPILER rather than a reviewer is responsible
for. ⚠ **ADJACENT, reported not fixed: `harness/vparse.py::axiom_decls` does not
recognise `global layout`**, so it is a fifth body-less form the gate is blind to
— defensible here because rustc checks it, but not in general.

---

## 7. Miri

`controls/rust_bug.py`, exit 0. `controls/arm_unsafe_bug.rs` is `unsafe.rs` with
`obj_retain(t);` deleted and nothing else, and the control **re-derives that at
every run** rather than shipping a hand-maintained copy (p35's shape), so the two
cannot drift.

* **Miri REPORTS UB on exactly the four inputs `model.py` derives as `fires`** in
  the bug arm, and on none of the others — so the firing is the missing retain
  and not the arm being a control. Diagnostic: `constructing invalid value of
  type &Obj` / `&mut Obj`, i.e. a dangling reference.
* **Miri is SILENT on the shipped `unsafe.rs` on all 8 inputs**, which is what
  `spec.md`'s `miri.reason` claims.
* The bug arm also **reproduces `c/kernel.c` bit for bit on all 8 inputs.**

---

## 8. The cost axis — and `controls/spellings.py` CAUGHT A FLATTERING-DIRECTION ERROR IN MY OWN HEADLINE

Deliverable 4. Both endpoints were searched over their in-contract spellings,
each variant produced by TEXT SUBSTITUTION from the shipped rung so it cannot
drift, and **each R4 candidate put through Verus**, because `identity: unsafe ≡
verus` makes an unverified R4 a control and not a rung.

| variant | side | small `-O0` | small `-O3` | large `-O0` | large `-O3` | Verus |
|---|---|---:|---:|---:|---:|---|
| `safe_tuned` (shipped R3) | R3 | 8,243.33 | 2,558.38 | 38,129.31 | 12,623.43 | — |
| `r3_cursor` | R3 | **6,133.33** | 2,775.04 | **28,339.31** | 13,716.39 | — |
| `unsafe` (shipped R4) | R4 | 5,631.32 | **2,364.59** | 27,058.04 | **11,906.72** | `24/0` |
| `r4_checked` | R4 | **5,227.32** | 2,417.61 | **25,048.44** | 12,174.14 | **`24/0`** |
| `r4_readdirect` | R4 | 5,515.19 | **2,364.59** | 26,446.94 | **11,906.72** | **`24/0`** |

**Two corrections, both against the author:**

1. ⚠⚠ **The shipped-pair R3−R4 figure at `-O0` OVERSTATES the gap by ~3×.**
   Shipped-pair: `2,612.01` (small) and `11,071.27` (large). Cheapest-found in
   contract on each side: `906.01` and `3,290.87`. **2.88× and 3.36× too large,
   in the direction that flatters `unsafe`.** The `-O0` shipped-pair number is
   therefore NOT published as a result. ⚠ At `-O3` the shipped pair IS the
   cheapest-found pair on both sides and the figure stands.
2. ⚠ **The shipped R4 is NOT the cheapest admissible R4 found at `-O0`.**
   `r4_readdirect` ties it exactly at `-O3` and beats it by `116.13`/`611.10` at
   `-O0`, **and it verifies at the pinned obligation count**.

**Which endpoint is weaker-searched: the R4 side**, structurally — every R4
candidate must also verify. **Two were put through Verus and both passed**, which
is more than p05 and p16 managed (`is not supported` at the pinned vstd), so
**p34 is the first pattern in this project with more than one R4 spelling SHOWN
admissible and a measured R4-side width** (`53.02`/`267.42` at `-O3`,
`404.00`/`2,009.60` at `-O0`). ⚠ Still a **found** minimum, not a minimum.

⚠⚠ **THE COMPARISON REVERSES BETWEEN OPTIMISATION LEVELS — TWICE**, which is
p35's lesson and p34 has two independent instances:

* **R2 vs R3**: R3 is **8.14 % cheaper** at `-O3` and **31.58 % DEARER** at
  `-O0`. Mechanism: `chunks_exact(2).take(nops)`'s iterator machinery is not
  inlined at `-O0`.
* **R4's stack accessor**: `arr_get_unchecked` is **2.24 % cheaper** at `-O3` and
  **7.17 % DEARER** at `-O0` than plain indexing. Same mechanism in mirror.
  ⚠ **So p27's `41.62 Ir/call` figure does not transfer** and this row does not
  inherit it.

Cross-language, `-O3`, cheapest-found in contract, `isolated`: C(gcc) 2,207.05 /
11,106.93 · R4 2,364.59 / 11,906.72 · R3 2,558.38 / 12,623.43 · R2 2,785.16 /
13,782.86. ⚠ The **C endpoint has had no spelling search at all** and is named as
the weakest-searched of the four.

---

## 9. Deliverable 5 — the bug class for `harness/tools/composition.py`

**p34 belongs on the `temporal` axis — its FIFTH row** (`p27 p28 p29 p32` today).
Sub-class: **premature free / improper reference-count update (CWE-911 → CWE-416)**,
distinguished from the four built temporal rows by the repair SITE: p27, p29 and
p32 are all repaired by a conjunct on the READ path, p34 only by a statement on
the ACQUIRE path. **The file was NOT edited** (task rule).

---

## 10. Adjacent work, reported and not done

1. ⚠ **`harness/vparse.py::axiom_decls` does not recognise `global layout`.**
   It matches `assume_specification`, `axiom fn`, `uninterp spec fn`,
   `external_trait_specification` and `external_type_specification`. `global
   layout T is size == n, align == m;` is a **sixth** body-less form that
   exports axioms (`size_of::<T>() == n`, `align_of::<T>() == m`) — so
   `verus.axioms` neither sees it nor could declare it (declaring more than the
   scan finds FAILS). ⚠ **On p34 that is defensible and I did not declare it**,
   because unlike the other five forms **rustc CHECKS this one at codegen**; but
   it is a form the gate is blind to, and the next pattern that uses it may not
   have that defence. **Manager's call, not mine.**
2. **`harness/tools/composition.py` needs a `p34` entry** — see §9. It will FAIL
   with `built but unclassified` until then; that is the check working.
3. **The `.temp/t154/` citations in `NOTES.md`.** `harness/tools/temp_citations.py`
   reports `new=0 unclassified=0` today because the files exist on this box, but
   the manager's baseline will want the new destinations classified. It also
   reports one pre-existing RESOLVED entry (`.temp/build/p28-repro`) that
   `--update` would prune; **not mine, not touched.**
4. **`results/SYNTHESIS.md` is not updated** — forbidden to me by the task rules.

---

## 11. Verdicts, read out of the RECORDS

All figures below come from `results/gate/p34-refcount-stack.json`, never from
the log (`.memory/03-measurement.md` entries 21–22).

**Gate run 2** (the one that produced the record the table was rendered from):

```
verdict          FAIL
blocked          []
complete_run     True
contract_sha256  f1537d7f601175122e67f9991a107449ad7ca52520b0484f5f014685369d2762
failures         [tables]  results/tables/p34-refcount-stack.md does NOT EXIST
loud             [collapse-ir]  the derived floor is 166x below the tightest cell
                 [tcb-unsafe]   arr_set_unchecked's `requires` constrains nothing about ['x']
```

⚠ **`blocked` is `[]`** — the figure the task asked to be read out of the record
rather than grepped (`p01 = 1`, `p42 = 1`, `p35 = 3`; **`p34 = 0`**). The one
failure is the new-pattern table lag the `Reproducing` section documents:
`report.py` renders from the gate record, so it cannot run before the first gate
run. Both `loud` notes are the standard ones every pattern in this family
carries.

Stages that were GREEN on that run and are the ones worth naming:

* **5c** — all four remaining `rec_alloc` `ensures` load-bearing, plus
  `buf_get_unchecked`, `arr_get_unchecked`, `arr_set_unchecked` and `kernel`;
  `assert(false)` at the call site unprovable. **8 conjuncts deleted, 0 free.**
* **5c-req** — 12 conjuncts probed, none a tautology under bare Z3,
  `by (nonlinear_arith)` or `by (bit_vector)`.
* **5c-twin** — `slb_twin` occurs nowhere but on the 5 twin attributes; all five
  twins verify against their trusted item's own contract; **`29 verified,
  0 errors` with `--cfg slb_twin`, matching the pin**; and each of the 12
  `requires` conjuncts, deleted alone, makes its twin FAIL.
* **7** — ASan fires on exactly the four inputs `model.py` derives as `fires`.
* **7h** — **R1h clean under ASan + UBSan on all 7 inputs, adversarial
  included** — the stage that did not exist before `TASK_151`.
* **8** — Miri: no UB on any input, and stdout matches the model on all seven.
* **9b** — all seven `controls/*.json` sidecars pin their sources by
  `derived_from_sha256`, all matching this tree.

**FINAL RUN** (after `harness/report.py p34`, full — no `--skip`, no
`--no-build`, no `--no-callgrind`, no `--no-verus-mutants`):

```
verdict          PASS
failures         []
blocked          []
complete_run     True
contract_sha256  f1537d7f601175122e67f9991a107449ad7ca52520b0484f5f014685369d2762
loud             ['collapse-ir', 'tcb-unsafe']     <- the two every pattern in this family carries
identity         unsafe vs verus  O0 norel (expected norel)  counts 332/332/1817 both sides
                 unsafe vs verus  O3 norel (expected norel)  counts 180/179/678  both sides
```

`check.py: PASS`, `exit=0`.

**`harness/tools/composition.py --check`**, as the task predicted:

```
FAIL: built but unclassified: ['p34'] -- add them to CLASSES in harness/tools/composition.py
```

**That is the check working**, and the file was **not** edited (§9 says which
axis).

**`harness/tools/temp_citations.py`**: `OK (new=0 unclassified=0 resolved=1)` —
every `.temp/t154/` path this pattern cites resolves on this box; the one
`resolved` entry is pre-existing (`p28`'s) and was not touched.

---

## 12. Reproducing

```sh
python3 patterns/p34-refcount-stack/inputs/gen.py
harness/build.py p34 && harness/measure.py p34 && harness/report.py p34
harness/check.py p34
for c in safety_line no_dup detectors safe_arms rust_bug spellings proof_mutants; do
  python3 patterns/p34-refcount-stack/controls/$c.py || echo "FAILED: $c"
done
python3 .temp/t154/novelty.py          # the novelty derivation, §5
python3 .temp/t154/marginal.py         # the marginal-Ir table, §3 and §8
.temp/t154/demo/repro.sh               # mgr149's table at 3 levels x 2 compilers
.temp/t154/demo/repro_hi.sh            # the high-iteration stability cell
```

⚠ **On a brand-new pattern the gate must run TWICE**: `report.py` renders from
the gate record, so stage 9/9c cannot be green until a record exists. That is
what the `Reproducing` block in `spec.md` says and it is not a defect.

---

## 13. What I did NOT do, and what I am unsure about

**Not done, deliberately:**

* **No edit to `.memory/`, `RECAP.md`, `results/SYNTHESIS.md`, `pilot/` or any
  earlier `.temp/t*/` or `.temp/mgr*/`** — task rules. `.temp/mgr149/` was copied
  into `.temp/t154/demo/`, never modified.
* **No edit to `harness/tools/composition.py`** — task rule; §9 names the axis.
* **No `git add` / `git commit`.**
* **No C-side spelling search.** `NOTES.md` §5d names the C endpoint as the
  weakest-searched of the four and publishes no C-to-Rust ratio as a bound.
* **No `-O1` column.** The tree measures `-O0` and `-O3`; `-O1` appears only in
  `.temp/t154/repro_t154.log`, where the demonstration table was re-derived and
  agrees with both.
* **No leak axis.** `.memory/01-ladder.md`'s outcome 4 is the `Rc` CYCLE leak and
  is a different class; the task scoped p34 to premature-free only. Reported as
  adjacent in `NOTES.md` §9: neither C rung leaks on any shipped input, and R1
  *cannot* leak — it frees too EARLY.

**Unsure, stated so nobody quotes it as settled:**

1. ⚠ **`identity` is `norel`, not `exact`, at BOTH levels**, where `p27`, `p32`
   and `p35` reach `exact` at `-O3`. I believe the mechanism is link layout —
   `md5_raw_norel`, `md5_fn_norel`, `md5_norm`, instruction count (180/179) and
   byte count (678) are IDENTICAL on both sides, and the differing byte is a
   rip-relative `lea` to the four-way opcode jump table, 0x20 apart. **I did not
   try to make it `exact`**; whether a spelling exists that would (removing the
   jump table, say) is unmeasured, and I would rather ship the honest weaker pin
   than tune the kernel to a digest.
2. ⚠ **The `0.10 Ir/call` R4-vs-R5 residue on the two `large` cells.** One part
   in 119 000, inside the coin-flip band, and the identity pin's assembly
   evidence is what carries R4 ≡ R5. **I did not chase the 10 instructions.**
3. ⚠ **The two-sided spelling search is ONE lever per side, not exhaustive.**
   `NOTES.md` §5c says *cheapest FOUND*, never *minimum*, and names the R4 side
   as the weaker-searched endpoint with the structural reason.
4. ⚠ **`model.py`'s `sanitizer_expect` derivation models glibc's LIFO recycling,
   which ASan's quarantine does NOT do.** So the simulation and ASan can disagree
   about *which access* fires while agreeing about *whether* one does — which is
   all the flag claims. I argued (`NOTES.md` §3) that a window with a successful
   DUP always fires because releases exceed credits by the DUP count; **that
   argument is mine and has not been reviewed.**
5. ⚠ **`global layout` and `harness/vparse.py`.** I did not declare it in
   `verus.axioms` (the scan does not see it, and declaring more than the scan
   finds FAILS). I think that is right *because rustc checks it*; a reviewer may
   disagree, and it is the manager's call whether `vparse.axiom_decls` should
   learn the form. §10.
6. ⚠ **`p34` is the first pattern with more than one R4 spelling SHOWN
   admissible** (`r4_checked` and `r4_readdirect`, both `24 / 0`). I did not
   check whether their R5s are still machine-code-identical to their R4s — the
   `identity` pin was only re-derived for the SHIPPED pair. **So "admissible" here
   means "verifies", not "verifies AND pairs"**, and `NOTES.md` §5c should be read
   with that caveat.

---

**PROTOCOL rule 2 running count: launched from 882, and this task adds SIX
manager claims contradicted by measurement** — the novelty claim's two halves
(both FALSE, §5), *"Python has no dangling pointers, so p34's harm is very likely
UNREPRESENTABLE in the model"* (it is representable; `sanitizer_expect` is
DERIVED, §0a), *"p27's checked-indexing figure transfers"* (it does not, and the
comparison REVERSES between optimisation levels, §8), *"the shipped-pair R3−R4
figure is the result"* (it overstates by ~3× at `-O0`, §8), and *"all five of
vstd's `ensures` should be kept"* — my own claim, refuted by the gate's stage 5c
(§0). **Reconciliation across branches is the manager's job, not mine.**

---

## 14. One process slip of my own, disclosed

After the final PASS I appended a section to `patterns/p34-refcount-stack/NOTES.md`
— and `NOTES.md` is in the gate record's `source_sha256`, so that single edit put
the committed record out of step with the tree. I caught it by re-deriving the
hashes from the record (`MISMATCHED NOW: ['patterns/p34-refcount-stack/NOTES.md']`)
and **reverted the addition**; the content lives in §3 of this report instead.
`source_sha256` now re-derives clean: `MISMATCHED NOW: []`.

⚠ **The general shape is worth the manager's attention because it is cheap to
repeat**: `NOTES.md` and `README.md` are gate-hashed, so *any* prose fix after a
green run silently invalidates the record, and nothing prints a warning — the
next full gate run is what would notice. PROTOCOL's rule-6 budget table already
says a `NOTES.md` fix "costs a gate re-run"; what it does not say is that
**skipping the re-run leaves a record that LOOKS green and no longer describes
the tree.** The one-command check is:

```bash
python3 -c "
import json,hashlib,os
d=json.load(open('results/gate/p34-refcount-stack.json'))
print([k for k,v in d['source_sha256'].items()
       if os.path.exists(k) and hashlib.sha256(open(k,'rb').read()).hexdigest()!=v])"
```
