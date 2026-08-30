# TASK_150 — land `p28`'s review corrections, bundled into ONE re-measure

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You own
`harness/check.py`, `harness/measure.py` and the records.

⚠⚠⚠ **EVERYTHING HERE IS BUNDLED BECAUSE EACH ITEM COSTS THE SAME RE-RUN.**
`c/kernel.c`, `c/kernel.h` and `model.py` are all in
`measure.py::measurement_sources`, so **majors 1 and 2 cost a `p28` RE-MEASURE**;
`spec.md`, `NOTES.md` and `controls/*` cost a **re-gate** only. **Budget one
re-measure and one re-gate. Do not run either twice.** (`TASK_141` and
`TASK_147` are the precedents.)

Read first: `.tasks/TASK_149_REPORT.md` **in full** — §6's two majors, §3, §4,
Deliverables 2–4 especially; `.tasks/TASK_146_REPORT.md`;
`patterns/p28-intrusive-lists/`; `RECAP.md` finding **56**;
`.memory/03-measurement.md` entries **12–19**; `PROTOCOL.md` **rule 6**.

## ⚠⚠⚠ MAJOR 1 — R1 DOUBLE-FREES, AND THE DENIAL IS INSIDE THE HASH

**`PROTOCOL` rule 6's second half exactly: the hash matches and the measurement
refutes the claim** (`p46`'s shape).

`c/kernel.c:200` is `free(n)` at the end of DEL's splice, and DEL's walk can
reach an object `TRIM` already freed — **that is the row's bug**, so the double
free is immediate from the source. Measured with `-Wl,--wrap=malloc,--wrap=free`
(`.temp/t149/wrapfree.c`; no `LD_PRELOAD`, so ASan blindness is not in play),
under the **leaking** allocator semantics `model.py` and **all four Rust rungs**
implement:

```
kernel            adversarial-uaf-write.bin   mallocs=4 frees=5 doublefree=1
kernel_hardened   adversarial-uaf-write.bin   mallocs=4 frees=4 doublefree=0
```

**Same input, same driver, same recipe; the only difference is the safety line.**
Every other input in both arms is balanced. **The LEAK half of the claim is true;
the DOUBLE-FREE half is false.** ⚠ The real allocator hides it — glibc's tcache
overwrites the freed chunk's user offsets 0 and 8, which are exactly `lp`/`ln`,
so `c/kernel.c:193` faults **two statements before** `free(n)`.

**Fix the two UNSCOPED spellings; the scoped ones are RIGHT and must stay:**

| file | text | |
|---|---|---|
| `spec.md` `idiom.required` (~line 213) | *"…so NEITHER C rung leaks and neither double-frees."* | ⚠⚠ **INSIDE `slb-contract`** |
| `c/kernel.c:37` | *"…neither rung leaks and neither double-frees."* | measurement-hashed |
| `c/kernel.c:231`, `c/kernel_hardened.c:225` | *"…neither leaks and neither double-frees **here**"* | ✅ **scoped to the epilogue — TRUE, leave alone** |

⚠⚠ **AND THE ROW HAS THREE HARM SHAPES, NOT TWO.** `c/kernel.h:80-93` tabulates
a UAF **READ** and a UAF **WRITE**; **CWE-415 double-free is a THIRD**, on the
same omitted block, and **no text in the pattern names it.** **Add it, and say
which instrument sees it** — note the wrap interposer is what made it visible.

## ⚠⚠⚠ MAJOR 2 — UBSan IS NOT SILENT, AND IT IS THE ONLY WITNESS OF THE WRITE

`NOTES.md` 2b — *"UBSan is silent here … no signed overflow, **no misaligned
access**, no out-of-range index"* — and `model.py:699` say the same. **Both are
false on `adversarial-uaf-write.bin`, at both compilers, reproducibly:**
`member access within misaligned address` at `c/kernel.c:193`, **10/10 gcc** and
**9/10 clang**, plus clang's `store to misaligned address … for type
'struct p28_obj *'`.

⚠⚠ **DO NOT JUST DELETE THE SENTENCE — THIS IS A POSITIVE RESULT AND IT IS THE
BEST THING IN THE REVIEW.** With `-fsanitize-recover`, **ASan never reports a
WRITE on any shipped input** (7 errors on `uaf-write`: 6 READs and a SEGV), and
that is **structurally forced** — DEL must read `n->key` before it can splice.
✅ **So UBSan is the ONLY witness of `p28`'s WRITE harm shape anywhere in the
tree.** **Say that, with the counts and the mechanism.**

## ⚠ MINORS, from `TASK_149_REPORT` §3 and its notes

1. **`BaseException` escapes both `except Exception` sites**, and
   `model.py:443`'s comment says otherwise. ⚠ **This is TREE-WIDE, not `p28`'s
   defect** — fix it here, report it as general.
2. **The must-fire arm licenses `_sim_buggy`, not `sanitizer_expect`** — a
   per-filename table is invisible to it. ⚠ **`.memory/03-measurement.md` entry
   19's rule is that whatever is DERIVED owes an arm that shows IT firing.**
   **Either extend the arm to the value `sanitizer_expect` actually returns, or
   say plainly which of the two the arm licenses.**
3. **Three of the five controls accept unknown arguments silently**, and
   **re-running any `p28` control rewrites its committed JSON**. Make the
   argument handling strict; note the rewrite behaviour where a reader will see
   it.

## ✅ RIDE-ALONGS the review earned — land these, they are the good half

1. **`B4`/`B5`/`B6`: deleting `rec_close` from `TRIM`, from `DEL`, **or** from
   the epilogue each verifies `23/0`. NOT ONE of the R5's three frees is
   forced.** ⚠ Fourth instance of the affine-token family after `p42`'s ghost
   ledger, `p32`'s `M4`, and `A6`. ✅ **`B3` (`ensures true`) fails in `main`,
   not in `kernel` — the driver consumes the postcondition, which is in `p28`'s
   favour and worth stating.** **Record all of it in `NOTES.md`; it is the
   honest scope of what this R5 proves.**
2. **Deliverable 4 is RESOLVED and the answer belongs in `NOTES.md` 8a**, which
   currently says *"mechanism not investigated"*. `safe_tuned` really is dearer
   than `safe_naive`, it is **in contract** (three variants, identical checksum
   on every probe), and **72% of the gap is the walk HOIST** — a fourth change
   its own header does not list — **paid per operation**: `+38%` with no walk,
   `+1.9%` with a 30-deep one. ⚠ **Say that the rung's NAME is aspirational and
   the port is fair.**
3. ⚠ **The headline attack FAILED, and that is a RESULT to write down, not a
   silence.** 3 257 436 **exhaustively enumerated** op sequences plus 20 000
   randomised across five attack-shaped generators: **0 value differences, 0
   counterexamples**, with **17 687/20 000 cases actually truncating the walk**,
   so the mechanism is exercised rather than dodged. ✅✅ **AND THE HEDGE CAN GO:
   `TASK_149` gives a THREE-STEP PROOF from slot-monotonicity + never-recycling.
   Replace *"an argument plus a measurement, not a proof"* with the proof, AND
   STATE ITS TWO HYPOTHESES** — they are the useful output, because a cache whose
   eviction order and chain order disagreed would not have it.

## ⚠ NOT in this task — recorded so it is not silently absorbed

- ⚠⚠ **The gate NEVER runs a detector on the HARDENED arm, for ANY pattern** —
  `check_sanitizers` builds `kernel.c` / gcc / `-O1` only. ✅ **`p28`'s own missed
  cell is CLEAN (0 defects over 88 cells, positive controls licensing each
  column), so this is not a `p28` defect** — it is a **gate** gap, `check.py` is
  in the gate digest, and it bundles with the other two owed gate repairs
  (finding 46 (iii); `assume(false)` shouting rather than failing — ⚠ **now
  confirmed on `p28`'s rung too, `B1` verifies `23/0`**). **Leave it. Report if
  you disagree.**
- **`RECAP` 56 and `CAVEATS["p28"]`** — the manager owns those and has applied
  the review's two corrections. Do not edit them.

## Then

`harness/check.py p28` → PASS · re-measure `p28` · `harness/report.py p28` if the
gate fails on `[tables]` · then `harness/measure.py --check-stale` (expect
**0 STALE**), `harness/tools/composition.py --check`,
`harness/tools/temp_citations.py`, and **`python3 synthesis/synthesize.py`** —
⚠⚠ **deliverable 2 said `p28` is NOT FINISHED because `results/synthesis.md`
still says *"Patterns: 28"* and contains no `p28`. That regeneration is part of
this task.** ⚠⚠ **`results/SYNTHESIS.md` (CAPITALS) is HAND-WRITTEN — NEVER
regenerate over it.**
⚠ **Read `blocked` out of the RECORD, never `grep` the log.** Expect `p01 = 1`,
`p42 = 1`; `p42` may legitimately be 2.

## Rules

- `.temp/t150/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`.** No `git add`/`git commit`.
- ⚠ **Do not touch `.temp/t136/ t137/ t139/ t140/ t141/ t142/ t143/ t144/ t145/
  t146/ t147/ t149/ t91/ mgr146/ mgr147/ mgr148/ mgr149/ mgr150/ mgr151/`** —
  cited evidence. **Copy from `t149/`; do not modify it.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate a sanitiser log
  with `head`; every harm probe owes a positive control that must fire, **in the
  detector whose column it licenses**.
- ⚠ **Generate control JSONs AFTER the sources are final.**
- ⚠ **State your re-measure prediction BEFORE you run it** — which leaves you
  expect to move and which you do not — then compare. `TASK_147` predicted
  `wall-clock/timestamps/hashes move, Ir/md5/identity/checksum do not` and got
  exactly that (103 of 1366). ⚠ **`model.py` changes here, so a `model_stdout`
  or `sanitizer_expect` move may be LEGITIMATE — say which you expect first.**
- ⚠ `python3 harness/tools/contract_diff.py p28` says what moved inside the
  hashed block, from `git` alone. Use it for your disclosure.
- Keep the generator, delete the artefact.
- ⚠ **If any item costs more than this file says, STOP AND REPORT rather than
  half-landing it.**
- Report to `.tasks/TASK_150_REPORT.md`. **PROTOCOL rule 2: the count is in
  `TASK_149_REPORT.md`'s closing paragraph — read it there, do not guess.**
