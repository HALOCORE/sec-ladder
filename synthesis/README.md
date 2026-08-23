# `synthesis/` — the cross-pattern comparison, and the column it has to qualify

Three scripts and two sidecars. Nothing here is run by the gate, and nothing
here is hashed by anything.

| file | what it is |
|---|---|
| `synthesize.py` | **the artefact.** Reads committed records, writes `results/synthesis.md`. |
| `licence.py` | §0 option **(c)** prototype: the *static* outward-dispatch licence. `--emit licence.json`. |
| `outward_ir.py` | §0 option **(b)** prototype: the *dynamic* callee `Ir` column. `--emit outward_ir.json`. |
| `licence.json` | per-pattern outward call sets and per-pair verdicts, with the gate `source_sha256` they were taken against. |
| `outward_ir.json` | per-cell `kernel_exclusive` / `outward` / `kernel_inclusive` `Ir` per call, `-O3 isolated`, both blobs. |

```bash
synthesis/synthesize.py                              # -> results/synthesis.md
synthesis/licence.py --all                           # ~2 s, no callgrind
synthesis/licence.py --emit synthesis/licence.json
synthesis/outward_ir.py --emit synthesis/outward_ir.json   # 352 callgrind runs, needs the built matrix
```

Both sidecars need `harness/build.py pNN` to have produced
`.temp/build/pNN/<cell>-O3-isolated`. Neither reads or writes a measurement
record. `synthesize.py` prints `LICENCE STALE` for any pattern whose gate
`source_sha256` has moved since `licence.json` was emitted.

## Why this directory and not `harness/`

`harness/check.py::main` hashes into **every gate record**:

```
patterns/pNN/*.rs   patterns/pNN/c/*   patterns/pNN/*.md   patterns/pNN/model.py
common/driver.*     harness/*.py       patterns/pNN/inputs/gen.py
patterns/pNN/controls/*.py             common/*.py         common/layout/*.py
verus_run.py
```

and `harness/measure.py::provenance` hashes a subset into every **measurement
record**, including `harness/{build,asm,measure}.py`. A file in `harness/` or
`common/` therefore stales 22 gate records for a script the gate never runs; a
file that lands in the *measurement* list is far worse, because clearing those
records re-takes the wall-clock block, whose noise floor is a *session*
property (~18% shift measured on unchanged p08 cells).

`synthesis/*` and `results/synthesis.md` are in neither glob. That was checked
by evaluating both glob lists literally against the candidate paths, not by
reading the prose that describes them.

## The open decision this directory is holding

`.tasks/TASK_075.md` §0 asks whether the kernel-column licence should be **(a)**
a recorded column, **(b)** an on-demand tool, or **(c)** a static check. The
measured answer is **(c) as the trigger and (b) as the correction, and NOT (a)
in `measure.py`**:

* **(c) is cheap and almost never wrong in the dangerous direction.** Scored
  against a full callgrind caller→callee sweep over 176 pair/blob rows:
  **156 hits, 10 false LICENSED, 0 false alarms, 10 abstentions** (`154 / 12 /
  0 / 10` against a second independent sweep — the two-row difference is p03's
  and p04's non-reproducing `memset` term, below). It costs ~2 s for the tree
  and needs no run at all.
* **(c) is not sufficient, and the two ways it fails are named.** It abstains
  on p27 and p36 — the patterns with an indirect dispatch, and p36 is the
  pattern that caused this — and its misses are two cost-behind-an-equal-name
  mechanisms: glibc `memset`'s alignment-dependent path length (p03/p04,
  ±7.00 `Ir`/call) and gcc's 2-instruction PLT thunk (+2.00 `Ir` per libc call,
  gcc's column only, one of the two being an `endbr64`).
* **A licence does not give you the number.** On p11 the correction *reverses*
  `R3 − R4` on `small`. That is what (b) is for, and (b) needs no `harness/`
  edit whatsoever — 352 callgrind runs for the whole tree, minutes on this box.
* **(a) in `measure.py` is the expensive way round and cannot be back-filled.**
  `measure.py::callgrind_ir` reads only `callgrind_annotate`'s summary; the
  caller→callee edges live in a scratch `callgrind.out` that is not kept, so
  populating the column means re-running callgrind everywhere. And
  `measure.py` is hashed into all 22 measurement records *and* into all 22 gate
  records, so the edit forces the project's single most expensive operation and
  moves 22 patterns' published timing prose.
* **(a′) in `check.py` is nearly free and is the version worth landing.**
  `check.py::check_marginal_ir` **already writes a `callgrind.out` per probe run**
  (`cg_files[(c,o,m,nm,n)]`) and reads only its `summary:` line — the
  caller→callee edges are already on disk and are being discarded. A stage that
  parses them costs **zero additional callgrind runs**, records the licence and
  the outward `Ir` into `results/gate/pNN.json`, and rides the five-item
  `check.py` batch that is already owed. Gate re-runs do not re-take wall clock.
  The probe blobs are `small.bin` with `n_iters` rewritten, so per-call outward
  work on the probe is per-call outward work on `small.bin`.

Until that lands, the sidecars here are the licence, and `synthesize.py` says so
above every table that uses one.
