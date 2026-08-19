# TASK_032 — ship the layout harness, fix the ordering bug, and settle p01's caveat

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_031_REPORT.md`** (its
"Problems" and its item 6 are this task's design, already costed) and
`.tasks/TASK_030_REVIEW_REPORT.md` (the finding being made reproducible), then
`.memory/03-measurement.md`'s two sections *"Interleave by CELL, never by block"*
and *"Code layout: the 32-byte fetch grid"*.

**This is the last methodology task before patterns resume.** Seventeen
consecutive tasks have gone to methodology and correction against two patterns
produced. This one is owed because finding 16 currently lives entirely in
`.temp/` — which is gitignored scratch that has already been swept once — and
because every future pattern's wall-clock column depends on the tool.

## 1. Fix the ordering bug FIRST

`.temp/r30/layout_gen.py:203` iterates `for k, b in bins.items()` over a dict
filled cell-by-cell, so each cell gets a **contiguous block** of every rep. Its
docstring and its log both say "interleaved". That alone flipped a sign on
byte-identical copies and manufactured every reading TASK_030_REVIEW attributed to
p05's shipped layout.

**Build a flat interleaved list.** Then prove it: re-run the identical-copy probe
(`.temp/p31/order.py`) against the fixed builder and show the blocked/alternating
gap has gone. **Do not ship anything until this is done** — shipping it as-is
ships the artefact.

## 2. Settle p01's caveat, which the bug left open

p01's withdrawal is currently published with a hedge: its mode groups have
unbalanced lever composition (`%32=0` is 8 align + 8 order, `%32=16` is 1 align +
13 order), so with a blocked timer the mode label was partly confounded with build
slot. **Re-run p01's 30-layout population with the fixed builder** and report
whether `+5.24% / −4.10%` survives.

This matters more than it looks: p01 is the *calibration* pattern, and its
withdrawal is one of the two the project has published. If the mode survives, the
withdrawal is clean and the hedge comes out of `p01/NOTES.md` §3b,
`.memory/03-measurement.md` and `RECAP.md` finding 16. **If it does not survive,
say so loudly** — that would mean the only surviving instance of finding 16 is
p07, and the finding needs re-scoping rather than re-wording.

p07's numbers were already shown protocol-insensitive (+27.46…+27.77% blocked
*and* alternating), so p07 does not need re-running. Say so rather than doing it.

## 3. Ship it

**Home: `common/layout/`**, one copy, and **add `common/layout/*.py` to
`check.py`'s `srcs` glob** (`check.py:4751-4760`) so it is hashed into every
pattern's `source_sha256`. That is TASK_031's recommendation and I accept it: an
unhashed shipped control is exactly the gap TASK_021 closed, and the tool should
be stable enough that 7 gate runs per edit is a price paid a handful of times.

Minimum set, ~640 lines:

- **`loopfit.py`** — the mechanism. Enumerates **every** loop and fits
  `win32`/`jcc32` with zero parameters. Fold in `jcc.py`'s address and
  `md5_fn_norel` half. ⚠ **Do not ship `jcc.py`'s "tightest backward branch"
  heuristic** — it picks the 12-byte scalar tail over the 30-byte SSE loop on any
  vectorised kernel, and it is the defect that produced p07 §11e's wrong-loop
  negative.
- **`layout_gen.py`** — population builder plus its controls (`md5_fn_norel` and
  `n_fn` single-valued, stdout identical, callgrind `Ir` invariant), **after** the
  item-1 fix.
- **`predict_then_time.py`** — the pre-registration harness. This is what makes
  the finding falsifiable and it is the most valuable file in the set.
- **`order.py`** — the protocol and noise-floor control: N byte-identical copies,
  blocked vs alternating. Without it a population number cannot be trusted, which
  is the whole lesson of TASK_031.

Reporting extras (`analyze.py`, `survives.py`, `q3_convergence.py`,
`modesim2.py`) are optional — ship them if they cost nothing, and say what you
left out. Everything `sys.path`-inserts `harness/` and `import asm`; make the
paths `__file__`-derived, not absolute (`.memory/00-environment.md` constraint 6).

**Write `common/layout/README.md`** — what each file does, the one-command
recipe for reproducing finding 16, and the two rules that must not be lost:
interleave by cell, and measure the identical-copy noise floor before believing
an effect.

## 4. Ride-along, because all seven gates re-run anyway

`harness/check.py:1753`'s runtime string
`head("3c. structural identity R4-vs-R5 (recorded as a result)")` still carries
the phrase TASK_028 corrected in the comments beside it. It prints in every gate
transcript. It has been queued for three tasks because it was never worth seven
gate runs on its own; it is free here. **Display string only.**

## Done when

All seven gates green (expect p01 `PASS-WITH-BLOCKED-ROWS`); `md5_fn` unchanged
everywhere; `source_sha256` gains `common/layout/*.py` in all seven records;
tables regenerated with `harness/report.py`. Item 2's answer is in your report
either way.

Expect the churn class from `.memory/03-measurement.md` (ASan PIDs, p05's two
nondeterministic `adversarial-dims` stdouts, p08's `marginal_ir_per_call` jitter —
**quote the magnitude and re-measure the count**, the recorded values are 8 → 23 →
75 and each was written down as if it were the number).

## Constraints

No root; no `/tmp` (scratch `.temp/p32/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. **`harness/check.py` is in scope for exactly two
edits — the `srcs` glob (item 3) and the display string (item 4) — and nothing
else. No other harness logic, no rung source, no cell relinked.** Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill. **Measurements in the FOREGROUND**, per-PID scratch paths,
and **interleave by cell** — you of all tasks.

Per constraint 6, delete your binaries and blobs when the gates are green.
`.temp/build` (532 M) and `.temp/check` (302 M) are shared caches — **leave them**,
they are the manager's sweep call.

Notes to `.temp/p32/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Forty-one agents
have contradicted the manager and all forty-one were right; the last one showed
that a *reviewer's* blocker was an artefact of the reviewer's own timing loop, on
byte-identical binaries. What I am least sure of is **item 3's home**: hashing
`common/layout/*.py` means any edit to a research tool invalidates all seven
patterns' gate records, and if the tool turns out to want frequent iteration that
is a 10–15 minute tax per change and an incentive not to improve it. The
alternative — ship unhashed and accept no staleness detection on a control — is
what TASK_021 closed and I do not want to reopen it. If you think there is a third
option, argue it.
