# TASK_065 — land p47's review, and fix the `main` term p27 got wrong

**Role:** research engineer (you built p47; this is its corrections task).
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_064_REVIEW_REPORT.md`
in full**, then your own `patterns/p47-ct-compare/NOTES.md`.

**The review returned 3 majors, 6 minors and 32 clean negatives, and it UPHELD
the two things the manager most suspected.** Do not re-measure what reproduced.

⚠ **A1 — your redenomination is VINDICATED, and with a mechanism you did not
have.** The manager suspected the direction test's shape: a definitional change
made after a measurement that moves a number across a threshold in the passing
direction. **It is the prescribed repair.** The review extracted the tag loops
independently — **11 insns / 64 window bytes (R3), 12 / 64 (R4) = 0.172–0.188
`Ir` per window byte asymptotically** — so a 0.25/window-byte floor **forbids the
shipped kernel outright**; `harness/check.py:1755-1760` prescribes redenomination
verbatim; and **p47 is the THIRD pattern to do it** (p07 at 4 B/unit, p10 at
2 B/unit, p13). ✅ **Put the mechanism into `NOTES.md`** — the delivery asserted
the unit and the review proved the alternative was impossible, which is the
difference between a choice and a forced move.
⚠ **But record the cost honestly**: p47's `collapse_tightest_margin` is **2.93×,
the tightest of all 19 patterns** (next 7.02; p27 134.45). Say so.

⚠ **A2 — verified to the instruction, and the framing is STRONGER than you
wrote.** The diff touches no `requires`/`ensures`: the shipped proof establishes
`d == xacc(…)` (the exact value), `m_leak` only `d == 0 <==> xacc(…) == 0`
(zero-ness). **Identical contract, strictly stronger intermediate.** Say it that
way — *"the proof certifies a leaking kernel"* is exactly right and now has the
precise reason.

⚠ **A3 — the review could not break it either, and its search is much larger
than yours.** 16 binaries × 7 C / 4 Rust spellings across **LTO, PGO trained
100% on mismatch-at-byte-0, AVX2, AVX-512, `__builtin_expect` in three
placements, and a branching caller**: `Ir(k=0) − Ir(k=n−1) = 0` **exactly**, per
function, with a detector control that fires (+18 448 `Ir` on `a == b`), and 0
data-dependent jumps in 33/33 functions on the AVX-512 builds. **Cite the
review's search, not just yours** — a negative claim is as strong as the widest
search behind it.

## The three majors

**M1 — the headline number is not reproducible from the tree.**
`controls/gen_controls.py:416-418` skips every `kind == "verus"` variant, so
**`m_leak`'s binary is never built** and `ir_table.py --leak-controls` prints
`MISSING`. The `+7088.000` in `README.md:69-75` and `NOTES.md:451` therefore
rests on a blob with **no generator** — `CLAUDE.md` "Don't" #1, *keep the
generator*. **The number is correct** (the review rebuilt it and got it exactly);
**the reproduction path is not.** Fix the generator, re-derive the number from
it, and paste the output.

**M2 — `main` is 5, not 4, and p27 is the outlier that needs fixing.** Your
`NOTES.md:257` / `spec.md:380` say the off-by-one *"ten patterns record"* is 4.
**Measured: p03, p05, p06, p07, p10, p11, p12, p14 and p17 all record `main` 5** —
so does p47. **Only p27 records 4, and p27 is wrong**, provably from its own
arithmetic: `spec.md:329` reads
`TABCAP 1 + RECSZ 1 + SENT 1 + run 1 + rec_open 1 + rec_close 1 + rec_read 1 +
kernel 3 + main 4 = 15`, **which sums to 14**, against a pinned and measured
**15**. With `main = 5` it is exactly 15.

> **Fix both**: invert p47's ⚠ note (5 is the rule, and no pattern records 4),
> and correct `patterns/p27-handle-table/spec.md` at **`:329` and `:421`** —
> `main 4` → `main 5`, and delete the sentence claiming eight named patterns
> record the same off-by-one, because **none of them does**. p27's
> `contract_sha256` will move; disclose it with the byte-provable undo, the way
> you did three times already. **The direction test passes trivially** — it
> corrects arithmetic and moves no published figure — but say so.
> ⚠ p27's gate must be re-run and green afterwards.

**M3 — a disclosure that says an edit was made when it was not.**
`spec.md:504`'s pinned `collapse.note` still says *"bytes of the window, 200 on
small and 1032 on large"*; the measured values are **96 and 512 byte
comparisons**. And `NOTES.md:902`'s definition-of-done disclosure table **claims
that note was changed** — verified against `git show HEAD:` that it was not.
**A false disclosure is worse than the stale note it describes**, because the
disclosure is what a reviewer trusts instead of re-checking. Fix both, and the
same staleness in `model.py:10-11`.

## The six minors

`work_unit_bits = 8` for a two-byte unit, against p10's precedent of 16; `m_hdr`
quoted as "2 errors" where the verification-results line says 1; `README.md`
carries **none** of `NOTES.md` §14's *necessary-not-sufficient* scoping — put it
there, since the README is what gets read; `NOTES.md:625`'s `u_winu` prose (it is
byte-identical to the shipped R4, `md5_raw 4d99e76e0b10`); `P(R3>R4) = 1.000` is
a **saturated** proportion, informationally identical to the disjoint-bands
statistic this project retracted — restate it as the review suggests or drop it;
and `NOTES.md` §1's "vector ops" column is **the one column the review could not
reproduce** — re-derive it or withdraw it.

## One thing to record that is not a correction

**`-march=native` binaries SIGILL under valgrind 3.27.1**, so **`Ir(k)` — p47's
entire instrument — does not exist for any AVX-512 build on this box.** That is a
**measurability limit**, not a defect, and nothing in `.memory/` says it. Put it
in `NOTES.md` in those terms; the manager will land it. `.memory/02-bench-rules.md`
already requires such a pattern to re-argue ALPHA — **it should also say the
figure cannot be taken at all**, which is a stronger and cheaper statement.

## Done when

Every item above is corrected in `NOTES.md`, `README.md`, `spec.md`, `model.py`,
the controls and `results/tables/p47-ct-compare.md`; **`check.py p47` green AND
`check.py p27` green** (M2 touches p27); `measure.py --check-stale` clean.
**Paste actual output of both gates.** ⚠ Doc edits make a gate record STALE —
re-run after editing, not before.

## Constraints

No root; no `/tmp` (scratch `.temp/p47c/` — **your own subdirectory**); **no
`git add`/`git commit`**; do not edit `pilot/`, `.memory/`, `harness/`,
`common/`, or any pattern other than **p47 and p27's `spec.md`** (M2 only — do
not touch p27's sources, controls or NOTES beyond what M2 requires). Verus only
via `./verus_run.py`; `~/tools/verus/vstd/` for vstd source. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never
`pkill`/`killall`; **no `nohup … &`**. Measurements in the FOREGROUND, per-PID
scratch paths. **You are the only agent running.**

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 130** — 128, plus the review refuting the manager's A1 premise (I suspected
a threshold was being defined past; the alternative unit is arithmetically
impossible), plus the valgrind/AVX-512 measurability limit nobody had named.
