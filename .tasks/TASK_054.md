# TASK_054 — a false claim is published in p12, and the same sentence shape is unaudited across 16 patterns

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_047_REVIEW_REPORT.md`
**M3** (where the defect was first measured, on p06) and
`.tasks/TASK_051_REVIEW_REPORT.md`, then `.memory/04-verus.md`'s **twin section**
(*"stage 5c-twin has TWO LIMBS"*) and `.memory/01-ladder.md`'s **finding 15**,
which records the correction for p06.

## The known defect

p06's `NOTES.md` claimed a mutant was caught by **the twin alone**, and p12's
`NOTES.md:1046-1049` makes the same claim. **Both are false in the same way**:
the mutant *also* fails the **contract pin** (measured on p06 with `check.py`'s
own clause comparator — 2 clause diffs), and on p06 a second mutant additionally
broke the **identity pin**. p06's wording was corrected at TASK_048 to
***Verus-level* sole catcher**. **p12's was reported and never fixed.**

p02's equivalent sentence is a **clean negative** — already correct, because its
table header says the mutants edit `verus.rs` *and* the `spec.md` pins in one
commit. So the shape is real but not universal, and it must be **measured per
pattern, not pattern-matched**.

## What to do

1. **Fix p12.** Measure it first: reproduce the mutant, run it through
   `check.py`'s own pin comparator the way TASK_048 did (`.temp/p48/pinsim.py`
   is the precedent — reuse or re-derive), and establish **which limbs actually
   fire**. Then correct `NOTES.md:1046-1049` and anywhere else in p12 that
   repeats it (`README.md`, `spec.md` prose). ⚠ **Do not just append the words
   "Verus-level"** — if the measurement says something different from p06's,
   report that instead.
2. **Audit the shape across all 16 patterns.** Any sentence claiming a mutant,
   a control or a check is caught by exactly one mechanism — "the twin alone",
   "only the pin", "nothing but", "the sole catcher", "caught only by". For each
   hit: **measure which mechanisms fire**, and classify as `correct` /
   `overstated` / `understated`.
3. ⚠ **REPORT the audit; fix ONLY p12.** Every other pattern is reviewed and
   published, and changing one is a decision for the manager with the measurement
   in hand. If you find a second false one, say so with the evidence and stop.
4. **Say what the general rule is**, in a form that could go in `.memory/`. My
   reading is *"a sole-catcher claim must name the layer — Verus-level, gate-level
   or pin-level — because a mutant that edits a proof usually also moves a pin"*.
   **If the audit says something sharper, write that instead.**

## Done when

p12's claim is corrected from a measurement, `check.py p12` green on a complete
run, and the cross-pattern audit table is in `.tasks/TASK_054_REPORT.md` with a
verdict per hit.

**Write `.tasks/TASK_054_REPORT.md` yourself before your final message**
(PROTOCOL rule 10).

## Constraints

No root; no `/tmp` (scratch `.temp/p54/`, **per-PID paths**); **no `git
add`/`git commit`**; do not edit `pilot/`, `.memory/`, `harness/`, `common/`.
**The only pattern you may edit is p12.** ⚠ `check.py p12` rewrites
`results/gate/p12-strcat-fixed.json` — that is expected and is the only gate JSON
you may touch. Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`,
valgrind `~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on
PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; no
self-matching `pgrep` wait-loops. ⚠ **Other agents are running concurrently.**
Stay inside `.temp/p54/`, `patterns/p12-strcat-fixed/` and that one gate JSON.
⚠ **Do not run timing/wall-clock measurements** — another agent may be measuring
and concurrent timing jobs corrupt each other (it destroyed a whole sweep on
p14). Verus runs and `Ir` counts are fine; **wall clock is not.**

Notes to `.temp/p54/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Eighty agents
have contradicted the manager and all eighty were right. **What I am least sure
of is item 2's scope** — I am assuming the phrase-hunt finds real instances, but
it may find only prose that is already correctly hedged, in which case the honest
answer is "p12 was the last one" and the general rule is not worth a `.memory/`
entry. **Tell me which, with the table.**
