# TASK_162 — review `p49`, and attack `model.py` first because it is the ONLY instrument

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read first: `.tasks/TASK_161_REPORT.md` **in full**;
`patterns/p49-interned-pool/` — **especially `NOTES.md` §10, where the engineer
lists the assumptions it wants attacked**; `.tasks/TASK_161.md` (what was asked);
`.temp/mgr161/NOTES.md` (**the manager's pre-build pass — its central claim was
already REFUTED; check whether anything else in it is wrong**);
`.tasks/TASK_160_REPORT.md`; `.memory/03-measurement.md` entries **19–23**;
`patterns/p08-overlap-move/` (item 1) and `patterns/p34-refcount-stack/` (item 3).

## ⚠⚠⚠ THE ONE THING YOU MAY NOT DO

**You may not recommend refusing, shrinking or retiring this row for any
RUST-SIDE, VERUS-SIDE or LADDER-SIDE reason.** *"Safe Rust expresses both sides"*,
*"the R5 is the largest in the tree"*, *"no detector sees it"* — **every one is a
FINDING, and the last is this row's HEADLINE.**
✅ **A row may fall on ONE ground only: its C MECHANISM duplicates a BUILT row's.**
That is item 1.

## 1. ⚠⚠ THE `p08` DISTINCTION — the only ground that can kill the row

`aliasing` now has two members and **`p08` is the other one**. The claimed
C-side distinction is measured rather than argued: `controls/no_overlap.py`
reports p49's record pairs as **11 084 exactly-coinciding, 892 352 disjoint,
0 PARTIAL**, against **9 partial** for `p08`'s control. **Equal-or-disjoint
versus partial-overlap.**

⚠ **Attack it.** Is *partial vs total overlap* a difference in the **C
mechanism**, or a difference in the **arithmetic of two particular kernels**?
⚠⚠ **And attack the direction nobody has: `p08`'s overlap is UB (C11 7.24.2.1p2)
and `p49`'s sharing is CORRECT C. Does that make them MORE distinct or does it
mean they are not the same axis at all — i.e. is `aliasing` the wrong class
rather than a widened one?** ⚠ Also try `p32` (whose aliasing IS the harm) and
`p28` (whose aliasing is the SETUP).

## 2. ⚠⚠ THE CLASSIFICATION IS THE MANAGER'S AND RULE 3 REQUIRES YOU TO ATTACK IT

The engineer argued **`logical`** fairly and proposed **`aliasing`**; **the
manager took `aliasing` and widened the class description to admit it**, which
the engineer named as the cost. ⚠ **`logical` is literally satisfied — nothing
allocated, nothing freed, every index in bounds, 216 + 18 detector cells with
0 diagnostics.** **Say which is right and why, and if it is `logical`, say what
that costs the row's story.**

## 3. ⚠⚠⚠ `model.py` IS THE ONLY INSTRUMENT ON THIS ROW — ATTACK IT HARDEST

**216 sanitizer cells and 18 Miri cells produce 0 diagnostics.** Every other
pattern has a detector as a second witness. Here **the model carries the entire
result**, so a defect in it is not a minor — it invalidates the row.

- ⚠ **Is `model.py` a TRANSLITERATION of the kernel?** `TASK_136`'s was, and
  that is how its bug went undetected.
- ⚠⚠ **Is any check a TAUTOLOGY of the model's own representation**
  (`.memory/03-measurement.md` entry **19**)? ⚠⚠⚠ **THE MANAGER HANDED THIS
  BUILD ONE INSTANCE OF EXACTLY THAT DEFECT AND GOT THE MECHANISM WRONG — see
  item 8. Check the Python did not reproduce it.**
- ⚠ **`sanitizer_expect` is `clean` on every input including the adversarial
  ones.** Confirm that is DECLARED and said plainly, not derived from something
  that cannot fire.
- ⚠ **Break the model deliberately and confirm every must-fire arm REPORTS
  rather than crashes.**

## 4. ⚠⚠ THE POSITIVE CONTROLS ARE LOAD-BEARING HERE IN A WAY THEY ARE NOT ELSEWHERE

On a row where **every detector is expected silent**, the control is the only
thing separating *"silent"* from *"not linked in"* (RECAP trap 5;
`.memory/03-measurement.md` entry 14). **16 control firings are claimed across
three `ctl_*.c`.** ⚠ **Confirm each EXECUTES and licenses the detector column it
is quoted for**, and that **clang has not eliminated any** — `TASK_160` lost a
control to gcc `-O1` deleting an entire `malloc`/`free`/`free`.
✅ **The engineer disclosed that its own expectation was wrong —
`ctl_asan_stack` fires under UBSan too — and recorded rather than relaxed it.
Verify the record matches the runs.**

## 5. ⚠⚠ THE SAFE-RUST HEADLINE — *"both sides, one type apart"*

`Rc<RefCell<Buf>>` reproduces `c/kernel.c` **9/9**; `Rc<Buf>` + `make_mut`
reproduces `c/kernel_hardened.c` **9/9**. ⚠ **That is a strong claim and the
kind this project has been wrong about.** **Is the `RefCell` arm an honest
idiomatic port, or one built to match?** ⚠ **Demand the negative control:**
`E0594` is reported **not distinguishing** — the **fifth** instance of a rustc
code read as distinguishing when it is not (`p25`, `p28`, `p34`, `p49`'s own
earlier arm). **Confirm the negative control exists, runs, and prints the same
code.**

## 6. ⚠⚠ THE COST AXIS REVERSES BETWEEN **COMPILERS**, WHICH IS NEW

`R1h − R1` is **`−2.79` Ir/call under gcc `-O3`** and **`+13.87` under clang
`-O3`** on `small.bin`. ⚠ **Every previous reversal in this project was between
optimisation LEVELS (`p35`); a reversal between COMPILERS is a different claim
and needs its own mechanism.** ⚠⚠ **The flattering-direction trap has fired
SEVEN times and `−2.79` is the flattering direction.** **Search both sides,
count the levers, name the weaker endpoint**, and check the R3 lever figures
(+27 % at `-O0`, `−6…−9 %` at `-O3`) at both levels with the inline mode named.
✅ **The R4/R5 null is `0.00` in every cell — that clean negative is worth
confirming, since it is the axis `TASK_158`/`159` corrected three times.**

## 7. ⚠⚠ THE ASSUMPTION THE ENGINEER NAMED AS DECIDING THE ROW

`NOTES.md` §10: **the epilogue folds the ownership flag**, which is what makes
`provenance` benign-observable and therefore **decides the `cow`-vs-upstream
call** (`cow` moves 0 of 3 benign checksums; `provenance` moves 3 of 3).
⚠⚠⚠ **If that fold is an artefact of how the epilogue was written rather than a
property of the program, the row shipped the WRONG SAFETY LINE.** **This is the
single most consequential thing in the review — settle it with a run.**

## 8. ⚠ THE MANAGER'S PRE-BUILD CLAIM, ALREADY REFUTED — CHECK THE REST OF IT

`.temp/mgr161/NOTES.md` asserted *"`if (r_shared[i])` CAN NEVER BE FALSE"*.
**Measured: TRUE 67 195 / FALSE 30 263 — 31.1 % of 97 458 evaluations**, because
**the COW body itself writes `r_shared[i] = 0`, on a line the manager's own probe
printed.** ✅ The underlying defect was real (**records born owned: 0**) and the
engineer restated it correctly. ⚠ **Conclusion right, mechanism wrong, landed as
one — PROTOCOL rule 9's named failure mode.** **Check whether the SHIPPED kernel
inherited any of the manager's wrong reasoning**, and whether *"records born
owned"* is now genuinely non-zero on the shipped inputs.

## 9. ⚠ THE R5, THE LARGEST IN THE TREE

`34 verified / 0 errors`, `identity: exact` at `-O3`, 34 obligations against
`p29`'s 25 and `p32`'s 15. ⚠ **Verify the battery's 9 arms fail for the reasons
given**, and try what it lacks: `assume(false)` (must FAIL unless declared),
an unreachable body, a `requires` nothing can discharge.
⚠ **Two engineer-disclosed items to settle:** `M1`'s failure **site** is not
established (rlimit at 200; a 4000 probe ran ~25 min without answering), and
**`lemma_rec_in_pool` is claimed to be a solver HINT rather than load-bearing**,
which surprised the engineer via arm `M4`. ✅ **The new Verus fact — `A && B` in
one `ensures` is NOT the same as two clauses for the solver, bisected 2×2 — is
worth `.memory/04-verus.md` if it survives you. Re-derive it.**

## 10. ⚠ A FALSE SENTENCE SHIPPED UNDER A MATCHING `contract_sha256`

`c/kernel.c` said *"the copy loop below"* and there is no copy. It survived rule
6's hash and was caught only by rule 6's **second half** (re-read the declaration
against your own measured numbers). **Two more measurement-hashed files were
wrong the same way.** ⚠ **Sweep the whole pattern for citations of things that do
not exist and claims no control records** — `TASK_156` found three on `p34` after
its review, so *"the engineer already swept"* is not evidence.

## Deliverables

1. **Per item: `SURVIVES` / `FALLS` / `SURVIVES, NARROWED`**, with the run.
2. **Is `p49` FINISHED?** ⚠ Gate-green is not finished. **Use the ANCHORED
   completeness check** (`PROTOCOL` rule 1 — finding HEADERS, not mentions) and
   check `results/synthesis.md`. **It will need regenerating — say so, do not do
   it.**
3. ⚠⚠ **ANYTHING THE MANAGER OVERSTATED.** Fresh places: the **`afe63d9` commit
   message**, **`CAVEATS["p49"]`**, the **widened `aliasing` description**, and
   the **`.memory/02-bench-rules.md`** edit. ⚠⚠ **The manager has been refuted
   in every one of the last seven tasks. Assume the same here.**
4. ✅ **CLEAN NEGATIVES ARE WORTH AS MUCH AS FINDINGS** — name the attacks that
   did not land so the next agent does not re-run them.

## Rules

- `.temp/t162/` only. **You may not edit `.memory/`, `RECAP.md`,
  `results/SYNTHESIS.md`, `harness/`, `synthesis/`, or `patterns/p49-*/`.**
  No `git add`/`git commit`.
- ✅ **You MAY run `harness/check.py` and `harness/measure.py`** — a single
  pattern, never the tree. ⚠ A single pattern's gate can take **30+ minutes**;
  run it in the background and **wait on the exact PID**.
- ⚠ **If you plant into `patterns/p49-*/`, restore in a `finally:` and verify by
  BYTES against HEAD**, then re-derive the record's `source_sha256`.
- ⚠⚠ **DO NOT LEAVE A `pgrep -f` WAITER RUNNING** — a waiter's own command line
  contains the string it greps for, so its exit condition can never be true.
  **Use `wait <pid>` or a `.done` sentinel** (`.memory/00-environment.md`).
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log**, and
  ⚠ **`rc=$?` after a PIPE reads the LAST command's status.**
- ⚠ **Do not touch any earlier `.temp/t*/` or `.temp/mgr*/`** — cited evidence.
- ⚠⚠ **`../LearnVeri/` IS ANOTHER PROJECT'S REPOSITORY — READ ONLY.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`.
- ⚠ `python3 harness/tools/contract_diff.py p49` says what moved inside the
  hashed block, from `git` alone.
- Report to `.tasks/TASK_162_REPORT.md`.

**PROTOCOL rule 2 running count: launched from 916**
(`.tasks/TASK_161_REPORT.md`'s closing paragraph). Carry it forward.
⚠ **Reconciliation across branches is the manager's job, not yours.**
