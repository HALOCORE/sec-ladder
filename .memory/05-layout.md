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
    spec.md                 # the exact kernel contract all 5 rungs implement,
                            #   incl. a ```slb-contract block check.py parses
    inputs/gen.py           # deterministic input generation (.bin gitignored)
    c/kernel.c  c/kernel.h  # the kernel, its own TU
    c/main.c                # the C driver loop, a second TU so `isolated`
                            #   builds put a real call between them
    safe_naive.rs  safe_tuned.rs  unsafe.rs  verus.rs
    safe_naive_verus.rs     # OPTIONAL R2v control: safe Rust + the same proof.
                            #   Not a rung, not in the measured 6-cell matrix;
                            #   built via `build.py --cell safe_naive_verus`.
                            #   It exists to hold up finding 2 in 01-ladder.md.
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
- Build outputs go to `.temp/build/pNN/<cell>-<opt>-<mode>[-abort]` — never into
  the pattern dir, never into git. Cell names are `c-gcc`, `c-clang`,
  `safe_naive`, `safe_tuned`, `unsafe`, `verus` (+ `safe_naive_verus` control).
- **The driver loop is duplicated, on purpose, once per rung**, between
  `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END` markers. It cannot be shared: R5's copy
  has to sit inside `verus!` so the kernel call site is verified
  (`.memory/02-bench-rules.md` rule 2). `harness/check.py` step 6 diffs the Rust
  copies (Verus `invariant`/`decreases` clauses stripped) and requires the C copy
  to contain the same arithmetic. `common/driver.{c,rs}` holds only the parts
  that *can* be shared: argv, file I/O, payload decoding, and printing.

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
