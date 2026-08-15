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
    check.py                # correctness gate: checksums, anti-collapse, proof
                            #   domain, driver pin, sanitizers, Miri policy
    asm.py                  # extract + normalise + diff kernel assembly
    vparse.py               # Verus/Rust items, attributes, requires/ensures
                            #   clauses. `python3 harness/vparse.py selftest`
    dloop.py                # the driver loop -> a language-neutral token
                            #   sequence, so C and Rust are diffed mechanically
    fixture.py              # builds .temp/build/docrepro, the fixture
                            #   `asm.py selftest` measures. Run it on a fresh
                            #   checkout; check.py runs it for you
    measure.py              # instruction counts, callgrind, timing -> results JSON
    report.py               # results JSON -> markdown tables
  patterns/pNN-<slug>/
    README.md               # what the pattern is, the C bug, expected findings
    spec.md                 # the exact kernel contract all 5 rungs implement,
                            #   incl. a ```slb-contract block check.py parses.
                            #   That block is a set of PINS: obligation count,
                            #   every verus item's requires/ensures, the driver
                            #   loop, the Ir floor, identity levels, Miri policy
    model.py                # MANDATORY. The independent Python reference
                            #   implementation of spec.md; check.py imports it
                            #   and drives it over every input. See p01's for
                            #   the required API -- the model used to be
                            #   hard-coded in check.py, which would have forced
                            #   47 forks of the gate
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
    pNN-<slug>.json         # raw measurements, committed
    gate/pNN-<slug>.json    # what check.py *found* on a COMPLETE run, committed:
                            #   identity levels, marginal Ir per call, obligation
                            #   counts, TCB inventory, per-input requires/ensures
                            #   coverage, adversarial behaviour, the verdict
    gate/pNN-<slug>.partial.json   # the same, from a run that certified less
                            #   (`--skip`, `--no-build`, `--no-callgrind`,
                            #   `--cells measured`). A diagnostic run must never
                            #   overwrite the record of a full one — at TASK_003
                            #   a `--skip small --skip large --no-callgrind` run
                            #   clobbered a passing artefact with its own
                            #   deliberate FAIL. Both files carry
                            #   `complete_run` and the exact `invocation`.
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
  (`.memory/02-bench-rules.md` rule 2). `harness/check.py` step 6 normalises
  every copy — the C one included — with `harness/dloop.py` and diffs each
  against the canonical token sequence pinned in `spec.md`. **Never
  copy-against-copy**: that passes when the mutation is applied to all of them,
  demonstrated at TASK_003 by deleting the anti-collapse barrier from all five
  Rust rungs and watching the old gate print "5 Rust rungs share a
  byte-identical driver loop". `common/driver.{c,rs}` holds only the parts that
  *can* be shared: argv, file I/O, payload decoding, and printing.

## Adding a pattern — what the gate needs from you

`harness/check.py` is generic; everything pattern-specific lives in two files.
In order:

1. **`spec.md`** — prose contract, then the ```slb-contract``` block. Start by
   copying p01's and changing every value. The block's fields:
   `kernel`, `model`, `requires`, `ensures`, `verus.{call_site, kernel_item,
   translate, obligations, items, unsafe_justifications}`,
   `driver.{statements, c_source, regions, aliases, canonical}`,
   `collapse.{probe_inputs, probe_iters}`, `identity`,
   `miri.{pair, sources, required, reason, blocked_reason}`.

   `requires`/`ensures` are **derived** by the gate from `verus.rs`'s own clause
   text through `verus.translate`; the copies in the block must equal the
   derivation exactly, and the gate fails if they do not. The collapse floor is
   derived from `model.py`'s `work_per_call` and is not settable here at all.
   `collapse.probe_inputs` should name **two inputs with different
   `work_per_call`**, or the marginal-rate assertion cannot run.
2. **`model.py`** — a *second* implementation of `spec.md` in Python, from the
   file bytes alone. Required API is documented at the top of p01's. It must not
   share code with the rungs beyond `common/slb.py`.
3. Generate the driver pin: `python3 harness/dloop.py <rung>.rs` prints the
   canonical token sequence; paste it into `driver.canonical`. Run it on
   `c/main.c` too and add `driver.aliases.c` entries until the two agree.
4. Get the pins right by running the gate and reading what it says the values
   are: obligation counts, identity levels, the derived `Ir` floor and the
   translated contract are all reported before they are asserted. Do **not**
   re-pin an obligation count without first finding out which item moved
   (`verus_run.py <file> --verify-function <name> --verify-root`) — the count is
   a skeleton checksum, not a semantic one.
5. **Then mutate your own proof and check the gate fails.** A pattern whose
   `spec.md` pins are copied from p01 without being re-derived is a pattern
   whose gate certifies p01.

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
