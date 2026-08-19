# TASK_035 — give `results/*.json` a staleness detector, and re-measure the two records that drifted

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_034_REPORT.md`'s
"Problems" (where this was found in passing), then
`.memory/03-measurement.md`'s new section *"`results/*.json` has NO staleness
detector, and two records drifted"* — **already written by the manager and the
wording to follow** — and `.memory/02-bench-rules.md`'s paragraph on
`source_sha256`, which now records that staleness is detectable **only by hand**.

**This is a small, bounded task and it is the last one before patterns resume.**
`TASK_036` (p03) is already written and waiting.

## What was measured

`results/gate/*.json` carries `source_sha256` and all eight are fresh (0 stale).
**`results/*.json` — where every published `Ir` and `ns` lives — carries none**,
so a measurement record can disagree with the tree indefinitely and nothing says
so. It did: `results/p01-array-sum.json`'s `c-gcc/O0/whole` records
`md5_fn 2fe6ada73f90` where a rebuild deterministically gives `4104f39118e8`.
`n_fn` (98) and `fn_bytes` (411) are unchanged, so it is `call`/`jmp`
displacements only — `common/driver.c` gained 23 lines after that record was
written.

Scope, from each record's `git_state.commit` against `c623b22` (the last commit
touching `common/driver.c`): **p02, p05, p07, p08, p11, p17 were measured after
it and are fine. p01 and p16 were measured before it.**

## What to land

1. **Add `source_sha256` to `measure.py`'s output.** Mirror `check.py:4751-4760`'s
   approach but scope it to *what a measurement actually depends on* — the rung
   sources, `common/driver.*`, `inputs/gen.py`, and the harness files that decide
   what is built and counted (`build.py`, `measure.py`, `asm.py`). **Justify each
   line in a comment**, the way `check.py`'s glob does; the point of that comment
   block is that the next person can tell whether a file belongs.
   ⚠ Do **not** simply copy `check.py`'s glob — it hashes `harness/*.py` wholesale,
   and a `report.py` edit invalidating every measurement record is exactly the
   false-positive that makes people stop trusting the mechanism.
2. **Ship the checker.** `.memory/02-bench-rules.md` now carries a one-line
   staleness check for the *gate* records; extend it to cover measurement records
   too, and put the runnable version somewhere it will be found — a
   `--check-stale` flag on `measure.py` is the obvious home. Say in your report
   whether you think it should also be a `check.py` stage (my view: **no**, on the
   "could this happen by accident?" test — it is a reporting concern, not a
   correctness one, and the gate is 4900 lines already).
3. **Re-measure p01 and p16.** Both will redraw numbers their `NOTES.md` quotes.
   **Report every value that moved**, with a per-column verdict on whether any
   *published claim* changes — not just whether a number changed. Two specific
   things to check and state explicitly:
   - **p16's per-byte null (`0.00000` safe−unsafe at matched spelling) is one of
     this project's most-quoted results.** A driver change should cancel in a
     rung-to-rung *difference*. Confirm that it did.
   - p01 is the calibration pattern and `.memory/01-ladder.md`'s pilot table cites
     its digests. If `md5_fn` moves for a cell, check whether any `.memory/`
     figure cites the old one.
4. **If a published number moves, do not quietly update it** — report it, and let
   the manager decide what needs re-stating. A silently-corrected published figure
   is worse than a stale one.

## Done when

`measure.py` writes `source_sha256`; the checker runs and reports 0 stale across
all patterns; p01 and p16 re-measured with every moved value listed;
`results/tables/*.md` regenerated for the two. **Gates need re-running only for
what you touched** — `measure.py` is in `check.py`'s `harness/*.py` glob, so
touching it re-runs all eight; say so in your plan and budget the ~16 minutes.

## Constraints

No root; no `/tmp` (scratch `.temp/p35/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. `harness/measure.py` is in scope; **no other harness
logic, no rung source, no pattern prose except the two `NOTES.md` sections whose
numbers you moved** — and those only to state the new value beside the old, never
to erase the old. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`;
confirm an exact PID's full command line before any kill, **and do not write
monitor wait-loops with self-matching `pgrep` patterns**. **Measurements in the
FOREGROUND, interleaved by cell**, and note that a wall-clock re-measure is
subject to `.memory/03-measurement.md`'s layout rules — if p01's `ns` moves, that
is the *withdrawn* column and it should stay withdrawn.

Delete your binaries and blobs when the gates are green; keep scripts and notes.
Notes to `.temp/p35/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Forty-five
agents have contradicted the manager and all forty-five were right; the last one
showed p08 and not p11 was the sharpest instance of the defect it was sent to fix.
What I am least sure of is **item 1's scope**: I do not know whether
`inputs/gen.py` belongs — the blobs are gitignored and regenerated, so hashing the
generator catches "the inputs changed under this record", which is real; but it
also means a new sweep band invalidates every measurement record for that pattern,
which per `.memory/05-layout.md` currently costs only a gate re-run. If those two
facts conflict, say which one should give.
