# `synthesis/` — the cross-pattern comparison, and the column it has to qualify

Three scripts and two sidecars. Nothing here is run by the gate, and nothing
here is hashed by anything.

| file | what it is |
|---|---|
| `synthesize.py` | **the artefact.** Reads committed records, writes `results/synthesis.md`. |
| `licence.py` | the *static* outward-dispatch licence: **may this row be differenced at all**. `--emit licence.json`. |
| `outward_ir.py` | the *dynamic* callee `Ir` sweep. **No longer a published column** — it calibrates one, and it names callees. `--emit outward_ir.json`. |
| `licence.json` | per-pattern outward call sets and per-pair verdicts, with the gate `source_sha256` they were taken against. |
| `outward_ir.json` | per-cell `kernel_exclusive` / `outward` / `kernel_inclusive` `Ir` per call **and per-callee call counts**, `-O3 isolated`, both blobs. |

```bash
synthesis/synthesize.py                              # -> results/synthesis.md
synthesis/licence.py p13                             # ~2 s for ONE pattern
synthesis/licence.py --all                           # ~43 s for the 22-pattern tree
synthesis/licence.py --emit synthesis/licence.json
synthesis/outward_ir.py --emit synthesis/outward_ir.json   # 352 callgrind runs, ~4m40s
```

⚠ **`~2 s for the tree` was wrong in three files** and is `~2 s` for **one**
pattern; `--all` is 43.4 s / 43.7 s measured twice (TASK_075_REVIEW m1). It
is still cheap enough that the decision below is unaffected.

Both sidecars need `harness/build.py pNN` to have produced
`.temp/build/pNN/<cell>-O3-isolated`. Neither reads or writes a measurement
record.

## The number is DERIVED FROM COMMITTED RECORDS, and that is the whole point

`results/gate/pNN.json` carries **`marginal_ir_per_call`** per
`(cell, opt, mode, input)`. It is whole-program and therefore
symbol-independent, so it already contains exactly the callee work the
kernel-exclusive column drops:

```
(marg[A] − marg[B]) − (kex[A] − kex[B])   =   the callee correction
```

`synthesize.py` computes that on every run. **The artefact is therefore
self-contained from `git`**: it needs no build, no callgrind and no sidecar to
produce a corrected figure.

⚠ **An earlier version of `synthesize.py` printed *"the licence is not in the
committed records and cannot be derived from them"* and scheduled two sidecars
on the strength of it.** That was false, it was the sentence the delivery
rested on, and it is `.memory/03-measurement.md`'s own prescribed
*"author-checkable test, which needs no disassembly"* (TASK_075_REVIEW B1).
**No figure in any table moved** — the provenance claim was the defect.

**Three measured bands, recomputed by `synthesize.py` on every run** (176 rows
against the callgrind sweep):

| `\|correction\|` | rows | real | spurious | reading |
|---|---:|---:|---:|---|
| `< 2.00` | 120 | **0** | 120 | nothing real hides below the floor |
| `2.00 … 16.00` | 22 | 8 | 14 | a coin flip — printed with a **?** |
| `≥ 16.00` | 34 | **34** | 0 | every one real, smallest 17.00 |

⚠ **2.00 is the only threshold at which it misses nothing.** At 3.0 and 5.0 it
misses two rows — `p02 gcc-clang`, worth exactly `+2.00` each, the PLT thunk.
TASK_075_REVIEW B1 and `.memory/03-measurement.md` say *"zero misses at every
threshold"*; that scores the oracle at the same threshold as the estimate.
Re-measured at `.temp/p76/derived_probe.py`.

## Why the sidecars are still here, and what changed

The manager's question at TASK_076 was whether the derived route should be the
**only** route, with both sidecars demoted to `.temp/` probes — *"one number
that is always recomputed rather than three that disagree in a year."*
**Answered by splitting it, because there were never three routes to one
number.** There is one magnitude and two other questions:

| question | who answers it | in the artefact? |
|---|---|---|
| **by how much is this row wrong?** | the derived column, from committed records | **yes, and it is the ONLY route — this is the part that was three-way and is now one-way** |
| **may this row be differenced at all?** | `licence.py`, from the disassembly | yes: the tag and its `why` |
| **which callee, and how many calls?** | `outward_ir.py`, from callgrind | **no.** It supplies no published figure; it calibrates the derived column's bands, live, on every run |

So `outward_ir.json` was demoted exactly as the manager suggested — it is now a
probe whose only output in the artefact is a score — while `licence.py` was
**not**, because it answers a different question and produces the *mechanism*,
which PROTOCOL rule 12 says is the difference between a finding and one a
reader disbelieves. The full argument, including the case for demoting the
licence too and why it loses, is in this task's report.

⚠ **`outward_ir.json` carries no staleness pin.** `licence.json` carries the
gate `source_sha256` and `synthesize.py` prints `LICENCE STALE` on a mismatch;
the callgrind sidecar has nothing equivalent, and re-emitting it costs 352
runs. That asymmetry is the second reason it calibrates rather than publishes.
It re-emitted **bit-identically on all 348 cells** at TASK_076 (a fourth
independent reproduction), so it is stable in a fixed environment — it is
*provenance* it lacks, not reproducibility.

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
reading the prose that describes them — and re-checked independently at
TASK_075_REVIEW, which evaluated all eleven globs and
`measure.py::measurement_sources` and got **zero hits**.

## Owed to `harness/`, REPORTED not built

1. **`asm.py::is_bulk_symbol` does not recognise `bcmp`** (measured:
   `is_bulk_symbol('bcmp@plt') = False`), so `results/p47-ct-compare.json`
   records `c-gcc: ['memcmp@plt']`, `c-clang: []`, `safe_naive: []` for three
   cells calling the **same** glibc entry point (`0x188320`). `__popcountdi2`
   is absent too (p09, all eight cells `[]`), and p11's four plain C cells
   record `[]` while calling `strlen@plt` — a stale record, not a whitelist
   gap. ⚠ `asm.py` is measurement-hashed, so bundle with a re-measure or
   accept that only the gate record improves.
2. **A `check.py` stage that parses the callgrind files it already writes.**
   `check_marginal_ir` writes `cg_files[(c,o,m,nm,n)]` per probe run and reads
   only its `summary:` line — the caller→callee edges are on disk and
   discarded. Cost: **zero additional callgrind runs**, one gate sweep, no
   re-measure. ⚠ Its probe blobs are **both** `small.bin` and `large.bin`
   (every pattern declares `probe_inputs: ["small.bin", "large.bin"]`, and
   `.temp/check/p13/` holds 64 `small` + 64 `large` `.out` files), so the stage
   would cover both — which matters, because most of the large corrections are
   `large` rows. An earlier version of this file said "the probe blobs are
   `small.bin`" and understated its own case (TASK_075_REVIEW m2).

   ⚠ **This is now a REFINEMENT, not the fix.** The derived column above
   already makes the artefact self-contained; a `check.py` stage would add the
   callee *names* and the +2.00/±7.00 terms the derived route cannot resolve.
   Schedule it on that basis, not as a dependency.
