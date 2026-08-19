# TASK_030_REVIEW — does the layout mode generalise? Every `ns` number in `results/` was measured at one layout

**Role:** research reviewer. You do **not** fix; you report.
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_029_REPORT.md`** (the
finding under review, item 2 and §11e), then
`patterns/p07-binary-search/NOTES.md` §11c–§11e, then
`.memory/03-measurement.md`'s *"Code layout selects between DISCRETE MODES"*
section and `.memory/00-environment.md`'s branch/cache-simulator section — the
last two are the manager's write-up of this finding and are **part of what you are
reviewing**.

## Why this is not a p07 review

TASK_029 measured, on p07, that code layout selects between **two discrete modes
on bit 4 of the kernel's entry address**, worth ~27% of wall clock, at an
**unchanged executed instruction stream** and with **every counter this box has
identical** (`Ir` Δ0.00, all cache counters 0.00 both, `Bcm` 273.93 vs 273.92).
It flips the sign of a rung-to-rung comparison.

**Every `ns` number in `results/` was measured at one layout.** If that mode
generalises past p07, the project's entire wall-clock column needs re-reading, and
several published `ns` claims across p01/p02/p05/p08/p16/p17 are one address bit
away from having no sign. That is the question, and it is worth more than
anything else currently in the queue.

It also already cost something: the finding **retracted a clean negative from
p07's own review** (R3-vs-R4 on `large` went DISJOINT → OVERLAP purely by
sampling more layouts) and **destabilised a `.memory/` rule one task after it was
written**. So this is a measurement that has already overturned two things, and
nobody has attacked it.

## The four questions

### Q1 — does the mode generalise? (the whole point)

Take **at least two other patterns** — p16 and p05 are the obvious pair (p16 is
latency-bound with a serial Horner chain, p05 is vectorised, so they are the two
least like p07) — and build each rung at a layout population using the lever
TASK_029 identified: `-C link-arg=-Wl,--symbol-ordering-file=<f>` under rust-lld,
which moves the kernel arbitrarily far at unchanged `n_fn`.

- Is there a bimodal structure at all, or is p07's binary search special?
- If there is, **is it the same bit**? p07 says bit 4 of the kernel entry
  address. Do not assume; partition by several bits and report which one
  separates, or that none does.
- **How much of each pattern's published `ns` gap survives mode-matching?**
  That is the number the project needs.

Verify invariance with **`md5_fn_norel`, not `md5_fn`** — p07's R2/R3 give 28
distinct `md5_fn` over 30 layouts at constant `n_fn` because the panic-path
`call rel32` moves. This is in `.memory/03-measurement.md` and it is the trap that
would make you abandon the control.

### Q2 — is "bit 4 of the kernel entry address" the right description?

Perfect separation on 30 points is strong, but 30 layouts of one binary is a small
population and the partition was found *after* looking. Specifically:

- Is it bit 4 of the **kernel's** address, or of something correlated with it —
  the driver's address, the loop head's address, a 32-byte boundary crossing
  somewhere inside the loop body?
- Does the partition survive **new** layouts drawn after the hypothesis was fixed?
  That is the honest test and it is cheap: generate 20 fresh orderings, predict
  each one's mode from the address *before* timing it, then time them.
- p07's engineer ruled out I-cache geometry and left "front end or an
  address-indexed predictor". Can you narrow it further with anything on this box?
  A negative is fine and useful; a wrong mechanism in `.memory/` is not.

### Q3 — do "mode-matching" and "dominance" actually converge?

TASK_029 replaced *"publish an interval, require disjoint bands"* with those two
because the worst-vs-best range demonstrably widened with more samples (28.91% →
30.78%) and flipped a verdict. **That is a good argument against the old rule and
not yet evidence for the new one.** Show that dominance and mode-matched
comparison are stable as the layout population grows — or show that they are not,
which would mean this project cannot publish a wall-clock ranking on an
L1-resident kernel at all, and that is a publishable result in itself.

### Q4 — the simulators' blind spot, stated correctly

`.memory/00-environment.md` now says callgrind's `--branch-sim`/`--cache-sim` are
"blind to code layout" on the strength of one minimal pair. Is that the right
statement? A predictor *model* has no notion of address, so being blind to an
address-indexed effect is expected and structural — but "blind to layout" is
broader than the evidence. Say what is actually established, in one sentence that
will survive.

## Clean negatives are worth as much as findings

PROTOCOL rule 6. If the mode does **not** generalise — if p07's binary search is
special — say so plainly with the evidence, because that is the outcome that lets
the project keep its published `ns` column, and it is just as valuable as the
alternative.

## Scope

**Four questions, then stop.** Do not re-open p07's headline (reviewed and
confirmed), its exact-integer laws (verified out of sample 30/30), or the spelling
arc. Do not fix anything — report.

## Constraints

No root; no `/tmp` — scratch under `.temp/r30/`, and per
`.memory/00-environment.md` constraint 6 **delete your binaries and generated
blobs when you finish, keep your scripts, notes and results**. Building a layout
population across several patterns' rungs will generate a lot of binaries; sweep
them. **No `git add`/`git commit`** — read-only git. Do not edit `pilot/`,
`.memory/`, or anything under `patterns/`. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never
`pkill`/`killall`; confirm an exact PID's full command line before any kill.

**Measurements in the FOREGROUND**, per-PID scratch paths, and pin with
`taskset`. Interleave rungs rather than running all reps of one then the next
(`.memory/03-measurement.md`). If you can afford a second CPU for replication,
do it — p07's mode was replicated on CPU 5 at 7 layouts but not at 30.

Reusable scratch: `.temp/p29/` (the 30-layout harness, the minimal-pair counter
runs) and `.temp/r26/` (`layout_r2.py`, `branchsim.py`, `cachesim.py`).
**Reuse them rather than rebuilding.**

Notes to `.temp/r30/NOTES.md` as you go so you can be resumed.

Report in PROTOCOL's format, severity-ranked, file:line and a concrete failure
scenario per finding. Paste actual command output.

**Contradicting the manager with a measurement is the highest-value thing you can
do.** Thirty-nine agents have and all thirty-nine were right; the last one
overturned a `.memory/` rule I had written one task earlier and a recipe inside it
that would have made anyone following it abandon the control. I have no
independent view of the layout finding — I am relaying it, and I wrote it into two
`.memory/` files on the strength of a single pattern.
