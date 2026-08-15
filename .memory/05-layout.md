# Repo layout & naming

```
sec-ladder/
  CLAUDE.md                 # entry point: links + DON'Ts only, keep it ~30 lines
  PLAN.md                   # research plan, feasibility argument, decisions
  TOOLCHAIN.md              # install record, how to run Verus, what's missing
  verus_run.py              # the only sanctioned way to invoke Verus
  .memory/                  # durable context for agents (this dir)
  .tasks/                   # TASK_NNN.md specs + PROTOCOL.md + reports
  .temp/                    # scratch, gitignored, one subdir per category
  pilot/                    # calibration kernel, 5 rungs — frozen, do not edit
  common/
    driver.rs               # shared Rust driver (see .memory/02-bench-rules.md)
    driver.c  driver.h      # shared C driver
    slb.py                  # input-file format read/write helper
  harness/
    build.py                # build one/all cells of a pattern
    check.py                # correctness gate: checksums agree, no constant-folding
    asm.py                  # extract + normalise + diff kernel assembly
    measure.py              # instruction counts, callgrind, timing -> results JSON
    report.py               # results JSON -> markdown tables
  patterns/pNN-<slug>/
    README.md               # what the pattern is, the C bug, expected findings
    spec.md                 # the exact kernel contract all 5 rungs implement
    inputs/gen.py           # deterministic input generation (.bin gitignored)
    c/kernel.c  c/kernel.h
    safe_naive.rs  safe_tuned.rs  unsafe.rs  verus.rs
    NOTES.md                # per-rung findings, proof sticking points, TCB tally
  results/
    pNN-<slug>.json         # raw, committed
    tables/                 # generated markdown, regenerable
```

## Naming

- Pattern dirs: `pNN-<slug>`, zero-padded, slug in kebab-case (`p17-http-range`).
- The measured function is named **`kernel`** in every rung and every language, so
  `harness/asm.py` can find it by substring across mangling schemes.
- Rung file stems are fixed: `c/`, `safe_naive.rs`, `safe_tuned.rs`, `unsafe.rs`,
  `verus.rs`. Do not invent variants; add an axis to `harness/build.py` instead.
- Build outputs go to `.temp/build/pNN/<rung>-<opt>-<mode>` — never into the
  pattern dir, never into git.

## What is committed

Committed: sources, `spec.md`, `README.md`, `NOTES.md`, `inputs/gen.py`,
`results/*.json`, harness code, `.memory/`, `.tasks/`.

Gitignored: `.temp/`, `inputs/*.bin`, build outputs, `results/tables/` is
regenerable but **is** committed for reviewability.

## Editing rules

- `pilot/` is frozen evidence for `PLAN.md`. Do not edit it; p01 is its successor.
- `CLAUDE.md` stays minimal — links and DON'Ts. New prose goes in a topic doc and
  gets a link line, never inline.
- Any agent that learns a durable fact (a Verus workaround, a measurement gotcha)
  writes it to the right `.memory/` file or `../LearnVeri/PITFALLS.md` and says so
  in its report. Facts that live only in a chat log are lost.
