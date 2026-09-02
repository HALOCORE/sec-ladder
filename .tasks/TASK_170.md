# TASK_170 — close the queue: eight items, one sweep, and the sweep is the LAST thing you do

**Role: research engineer.** You are the only agent running.

⚠⚠⚠ **THIS CLOSES THE PROGRAMME'S OUTSTANDING WORK.** All 33 patterns are built,
reviewed, corrected and have findings; the four Results are re-derived at 33; the
gate bundle and the backlog bundle have landed and been reviewed. **What is left
is queue items 35–42, and item 43 is investigation only.**

Read first: `.tasks/TASK_169_REPORT.md` **in full** (it names most of these and
measured two of the manager's cost claims wrong); `RECAP.md` **Immediate queue
items 35–43**; `.temp/mgr164/QUEUE_TRIAGE.md`; `PROTOCOL.md` **rule 6**;
`.memory/05-layout.md`'s digest-cost section.

---

## ⚠⚠⚠ THE BUDGET, AND THE ORDER IS THE BUDGET

**ONE 33-pattern sweep + `report.py p35` + ONE re-gate of `p35`. ZERO
re-measures.**

Manager-verified against a committed record, not assumed:

```
harness/tools/  in gate digest?  False
synthesis/      in gate digest?  False
common/census/  in gate digest?  False
harness/*.py    in gate digest?  TRUE   -> the one sweep
patterns/p35/spec.md `why`       -> contract_sha256 moves -> report.py + re-gate
```

⚠⚠ **SO ITEMS A–D BELOW COST NOTHING AT ALL. Do them first, land them, and only
then touch `harness/`.** ⚠ **Freeze every `check.py`/`vparse.py` edit before the
sweep starts** — `TASK_164` lost a 22-pattern sweep to a late docstring fix and
disclosed it.
⚠ **If any item costs more than this file says, STOP AND REPORT.**

---

## A. ⚠⚠⚠ ITEM 40 — A ROTTEN CITATION IS IN A *PUBLISHED* ARTEFACT

`results/synthesis.md:224` carries **`check.py:3303`**, emitted by
`synthesize.py:659` and `:1400`. That line is now a docstring sentence about the
whole tree; the thing it means to cite is **`check_identity`**'s isolated-only
comparison.

⚠⚠ **`.memory/` recorded this exact coordinate as rotted and repaired it IN ITS
OWN COPY ONLY** — which is why this survived. ⚠ **`RECAP.md` carries six of its
own, ≥4 rotten; that is the manager's and you should REPORT them.**

✅ **Fix the generator, not the artefact** (`synthesis/` is in neither digest, so
one regeneration and no gate). **Name the FUNCTION and give no line number** —
`.memory/02-bench-rules.md`'s rule, because a function name cannot decay.

⚠⚠⚠ **AND THE WIDER FINDING, WHICH IS THE REAL ITEM:** stage `0c` enforces this
convention over **`check.py` ∩ `patterns/`** — one of thirteen modules and one of
six directories that carry it. ✅ **`harness/tools/temp_citations.py` is outside
the gate digest and already walks the whole repo, so it is the right home for the
tree-wide form.** **Add it there, with a must-fire arm**, covering every
`harness/*.py` module name and every committed directory. ⚠ **Decide and state
what an ESCAPE HATCH looks like** — `TASK_169` found three `.memory/` citations
that are **deliberate quotations of rotten coordinates**, and a check with no
hatch would destroy them.

## B. ITEM 35 — audit the 14 `undeclared` search-state rows

`p02 p04 p05 p07 p09 p14 p16 p18 p19 p23 p27 p38 p42 p46` print `undeclared` in
`results/synthesis.md`'s search-state column. **They are the same 14 as at 26
patterns and nobody has read their `NOTES.md` against
`synthesize.py::SEARCH_REVIEWED`.** ⚠ **When the seven NEW rows were audited the
same way, FOUR of seven were wrong.**

⚠⚠ **READ, DO NOT GREP.** The obvious detector — *"ships a `controls/spellings.py`
but has no entry"* — was measured at precision 1/2, recall 1/4, and `p49`'s
`undeclared` was **right** because its `spellings.py` is a repair-site control
rather than a rung search. ✅ **Each entry you add must cite a REVIEWED
artefact**, the way the existing ones do.

⚠ **Report the split** — how many of the 14 had a real search, how many a
reviewed declaration of *no* search, how many are genuinely undeclared — and
**say what the published sentence should read.** ⚠ **`TASK_167` settled that a
reviewed declaration of NO search counts as `declared`; keep that convention.**

## C. ITEM 36 — two published numbers rest on instruments in gitignored scratch

`TASK_129`'s bound-site classifier (behind *"0 of 255"*, now **0 of 464**) and
`TASK_131`'s size probe (behind *"`p ≈ 0.06`"*, now **`0.0123`**) **both still
run and both reproduce their published figures exactly as controls** — and both
live only under `.temp/`, which `CLAUDE.md` constraint 1 asks to be cleaned.

✅ **Promote them to `common/census/`, which is the precedent and is outside both
digests** (`TASK_132` §F). ⚠ **Carry the CONTROL with them**: each must
reproduce its 26-pattern published figure as well as give the 33-pattern one, or
the promotion is a copy rather than a check — that is exactly what
`census_filelists.py` does and why it exits 1 when a count moves.
⚠⚠ **Do not `import` anything from `common/census/` into `harness/`** or the
directory is pulled into the gate digest and a comment fix there starts costing
a sweep.

## D. ITEM 37 — re-pin `outward_ir.json`, and account for the four

It pins the **gate `source_sha256`**, so any `harness/*.py` edit stales all 33 —
and every one of those STALEs is **false**, because a docstring cannot move a
callgrind number. **Stage 9b's own docstring argues against this key in terms.**

⚠⚠ **The manager wrote *"the repair costs no sweep and no re-measure and clears
it"*; `TASK_169` measured the proposed pin and it STILL REPORTS 4 OF 33 STALE.**
✅ **33 false STALEs → 4 is a real improvement and not a fix.** **Name the four,
say why each still moves, and either widen the pin to cover them or record them
as known.** ⚠ **A pin whose STALE nobody believes is a pin that gets switched
off — that is the whole argument, so do not trade one for another.**

⚠ **Fix `outward_ir.py`'s own docstring in the same pass**: it says *"It carries
no staleness pin"*, false since `TASK_107` §F.
⚠⚠ **Do NOT re-emit the sidecar** — 352+ callgrind runs, and this task does not
need fresh numbers. **Re-pin the existing ones and say plainly that the values
are `TASK_166`'s.**

## E. ⚠⚠ THE `p42` MARKER — `TASK_169`'s deliverable 2, and the manager takes it

`results/synthesis.md` prints `p42`'s `+4160.00` in **bold**, in the
`≥ CONFIDENT` band whose legend says *"every row is real"*. It **is** real —
`safe_naive` does `vec![0u8; 4096]`, `unsafe` does `with_capacity` — but at
`1.0156 Ir`/byte it sits in the **byte-wise `rep` regime**, and a difference
taken across a libc bulk-routine threshold is not comparable with one that is
not.

✅ **Land `TASK_169`'s recommendation: keep the number, keep the band, and add a
THIRD marker beside the file's existing `†`/`‡`** — *"crosses a libc
bulk-routine threshold: regime-dependent, not comparable"*.
⚠⚠ **DO NOT publish a discount factor.** The *"~90% is counter, not code"* gloss
is **withdrawn** — its `≈426` was glibc **`memcpy`**'s figure re-badged as a
**`memset`** counterfactual. **There is no measured vector-path counterfactual
for this zeroing, so no percentage may be quoted.**
⚠ **Derive which rows the marker applies to** rather than marking `p42` alone —
the `Ir`/byte signature is the test (`≈1.00` byte-wise, `≈0.10` vector).

## F. ITEM 38 — widen stage `0c`'s regex

It fires on `check\.py:\d+`. ⚠ **The tree's own worst case was
`check.py:1249-1278` — a RANGE — and four of the eight fixed citations were
ranges.** **Widen it to the range form, to `harness/check.py:`, and to the other
harness modules** (item 37's `13 line citations into
`measure.py`/`build.py`/`dloop.py`, **two rotten now** — `measure.py:238`,
`build.py:66`). ⚠ **Those sites are `model.py`/`inputs/gen.py`, so FIXING them
costs a re-measure and is NOT in this task** — **make the stage SHOUT on them,
not FAIL**, and say so in the stage's own text. ✅ **A shout survives to the
verdict and reaches `results/tables/`.**

## G. ITEM 42 — `0c`/`0d` are the only arm sets with no `RAISED` guard

Every other `_*_CASES` table catches its own exception and reports `"RAISED"`;
these two do not, **so a throw inside one kills the gate at import rather than
failing a stage.** `.memory/03-measurement.md` entry 19: *reported, not crashed*.
✅ **One line each. Add a must-fire arm that plants a throw and confirms the
gate REPORTS it.**

## H. ITEMS 39 + 41 — `p35`'s stochastic arm, and it is the only contract move

The unsafe arm gives **SIGSEGV 37/40 and 38/40** on the two pointer inputs with
SIGBUS the rest, while **C is 40/40** — and **five documents, one of them a
hashed `why`, assert a single `rc=-11`.** `controls/rust_bug.py` **records**
`unsafe_reproduces_c` and **never asserts it**.

✅ **Say the arm is stochastic and give the distribution.** ⚠ **Do NOT re-roll
for the published draw.** ✅ **Add the assertion to `rust_bug.py` with a stated
tolerance**, and regenerate the sidecar.
⚠⚠ **This moves `p35`'s `contract_sha256`, so it owes `harness/report.py p35`
and a SECOND gate of `p35`** — that is the only such cost in this task and it is
budgeted. ⚠ **Record the pre-edit `slb-contract` block TEXT verbatim, not only
its hash** (`TASK_156`'s standard), and use
`python3 harness/tools/contract_diff.py p35` for the disclosure.

## ⚠ NOT in this task

- **Item 43** — `asm.py`'s `main` needle mis-resolving to `driftsort_main` in 31
  committed records. ⚠⚠ **`asm.py` is MEASUREMENT-hashed, so a fix is a full
  re-measure.** ✅ **INVESTIGATE AND REPORT ONLY: what does it change, and does
  any published number depend on it?** **Do not fix it.**
- **`.memory/`, `RECAP.md`, `results/SYNTHESIS.md`, `harness/tools/composition.py`**
  — manager-owned. ⚠ **NEVER regenerate over `results/SYNTHESIS.md` (CAPITALS)**;
  `results/synthesis.md` is generated and you own it.
- **Retiring queue groups C, D and E as stated limitations** — the manager's,
  next.
- **Any re-measure**, and **any re-emit of `outward_ir.json`**.

## Then, in this order

1. **A, B, C, D, E** — all zero-cost. Land and verify each.
2. **F, G** — `check.py`/`vparse.py`, frozen.
3. **H's edits**, then the sweep.
4. **The 33-pattern sweep**, once, in the background, waiting on the exact PID.
5. **`harness/report.py p35`**, then **re-gate `p35`**.
6. `harness/measure.py --check-stale` (⚠ **66 examined = gate PLUS measurement**)
   · `composition.py --check` · `temp_citations.py` ·
   `synthesis/licence.py --emit synthesis/licence.json` · `synthesize.py`.
7. ⚠⚠ **CHECK EACH SCRIPT'S OWN EXIT STATUS, NOT A PIPELINE'S OR AN `echo`'s.**

## Rules

- `.temp/t170/` for scratch. ⚠ **Do not modify any earlier `.temp/t*/` or
  `.temp/mgr*/`**; you may read them. **No `git add`/`git commit`.**
- ⚠⚠ **DO NOT LEAVE A `pgrep -f` WAITER RUNNING** — a waiter's own command line
  contains the string it greps for. **Use `wait <pid>` or a `.done` sentinel.**
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log.**
  ⚠ **Expected: `30 PASS + 3 PASS-WITH-BLOCKED-ROWS`, 0 failures, `blocked`
  `p01` 1 / `p35` 3 / `p42` 1** (`p42`'s may legitimately be 2).
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- **Keep the generator, delete the artefact.** A generator that edits source by
  string substitution **MUST ASSERT ITS SUBSTITUTION COUNT**.
- **Every new check owes a must-fire arm you have SEEN FAIL.**
- Report to `.tasks/TASK_170_REPORT.md`. **Write the file before citing it.**

**PROTOCOL rule 2 running count: launched from 948.**
⚠ **Reconciliation is the manager's job, not yours.**

⚠⚠ **Three consecutive reviews have each found a `✅ manager-re-derived` mark
the manager had not earned, and the last one found three in one bullet. The call
to attack here is item D's: I wrote that re-pinning `outward_ir.json` on
`measurement_sources` is *the* repair. `TASK_169` already showed it leaves 4 of
33 stale. If the right answer is a different pin, or no pin, say so.**
