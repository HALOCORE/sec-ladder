# `common/layout/` — the code-layout control

Two binaries built from **identical source**, differing only in where the linker
put the kernel — same `n_fn`, same `md5_fn_norel`, same executed instruction
stream — can differ by up to **27% of wall clock**, and the difference can
**flip the sign of a rung-to-rung comparison**. A single-layout `ns` number is a
sample of size one from a distribution the source does not determine.

This directory is the tool that measures that distribution. It is the
reproduction path for `.memory/03-measurement.md`'s *"Code layout: the 32-byte
fetch grid"* (RECAP finding 16) and for the two withdrawn `small` wall-clock
rows (p01 §3b, p07 §11e).

It is **not** part of the gate. `harness/check.py` never imports it. It is
hashed into every pattern's `source_sha256` (`check.py`'s `srcs` glob) for one
reason: it is a committed control, and a control whose source can change without
the record noticing is the staleness gap TASK_021 closed.

## The two rules that must not be lost

**1. Interleave by CELL, never by block.** Build one flat schedule in which every
cell is launched once before any cell is launched twice
(`layout_gen.round_robin`). Do *not* iterate a per-cell container: the same
`for k, b in bins.items()` idiom that is **correct** in `harness/measure.py`
(one binary per cell) is **wrong** here (31 binaries per cell) and silently
gives each cell a contiguous block. Measured cost of getting it wrong, on 31
**byte-identical copies** of p05 at one fixed layout:

| schedule | R2 − R4 | R3 − R4 | identical-copy floor |
|---|---|---|---|
| alternating (`measure.py`) | +30.31 / +30.07% | +4.22 / +4.15% | 7.0–14.8% |
| `round_robin` (shipped) | +30.08 / +30.25% | +3.92 / +3.46% | 4.2–12.6% |
| **blocked (the bug)** | **+7.56 / +7.93%** | **−0.09 / +0.36%** | 18.0–21.0% |

A 22-point error on R2 and no sign at all on R3, from the loop order alone.
Slot 0 of a block — which is where a "shipped" build naturally lands — read
rank 30/30 and 29/30 out of 31 identical copies. That artefact manufactured a
reviewer's blocker (TASK_030_REVIEW blocker 2, retracted at TASK_031).

**2. Measure the identical-copy noise floor before believing an effect.** Build
the *same* source N times, time the copies as a population, compare the spread
to the effect (`order.py`). p05's 30-layout "band" is **inside** its own
identical-copy floor, which is why its `small` row is withdrawn; p01's and
p07's floors are ~1–3% against 8–32% bands, which is why theirs are withdrawn
for a real reason.

## Files

| file | what |
|---|---|
| `loopfit.py` | **the mechanism.** Enumerates *every* loop in a kernel and computes two zero-parameter static properties per loop: `win32` (32-byte fetch windows the body occupies) and `jcc32` (branches crossing/ending on a 32-byte boundary — Intel SKX102, this box is Cascade Lake µcode `0x5000024`). Also the shared library: `kernel_report`, `load`, `stems`, `fit`. |
| `layout_gen.py` | **the population builder.** ~30 layouts per rung via `-align-all-functions` and `--symbol-ordering-file`, three controls, and `round_robin` — the interleaved schedule everything else imports. |
| `order.py` | **the protocol and noise-floor control.** N byte-identical copies, timed under `alt` / `blk` / the shipped `round_robin`. Run this before believing any population number. |
| `predict_then_time.py` | **the pre-registration harness.** Draws fresh symbol orderings, writes and SHA-256s the prediction *before* timing, then scores. This is what makes the finding falsifiable. |
| `analyze.py` | band, clustering, per-bit split, geometry fit, mode-matched gaps, cross-pass reproducibility. |
| `survives.py` | how much of each pattern's **published** `ns` gap survives its population. |
| `q3_convergence.py` | which statistic converges as N grows. Mode-matched median and pairwise `P(A>B)` do; band and dominance do not. |
| `modesim2.py` | what callgrind's simulators see across a mode boundary (answer: everything moves, by ≤6 events in 10⁸ — they model no front end). |

Everything derives its paths from `__file__`, writes under `.temp/layout/` by
default (`--out`), and deletes its own binaries. Nothing here needs `harness/`
except `loopfit.py`, which imports `asm` — the project's only `objdump` caller.

`data/` holds the committed evidence, so the finding can be **audited** and not
only re-derived — `.temp/` is gitignored and has been swept once already. It is
matched by no `source_sha256` glob (those are `*.py`), so adding to it costs no
gate runs.

| file | what |
|---|---|
| `data/layout_p01.json` | p01's 30-layout + shipped population, 3 rungs × `small`/`large` × 2 passes, built by the **fixed** (interleaved) builder at TASK_032. |
| `data/predictions_p01oos.json` | the pre-registration for 20 fresh orderings. **Its file sha256 *is* the hash `predict_then_time.py` printed before timing** — `5c5c2a8cbfa81d1e199e1374dbcfaa65ba5c37290cdaea8117189b9b155eb4a9` — because the harness writes the hashed blob verbatim. Check it. |
| `data/predtimes_p01oos.json` | the same 60 builds' measured times, added afterwards. |

Only p01 is here. The other six populations in `.temp/r30/` were produced by the
**blocked** builder and their cross-rung columns inherit an error measured at up
to 22 points; they are not evidence and must not be committed as such.

```bash
# the published p01 table, from committed data, with no measurement at all
python3 common/layout/survives.py --dir common/layout/data p01
python3 common/layout/loopfit.py  common/layout/data/layout_p01.json
sha256sum common/layout/data/predictions_p01oos.json   # the pre-registration
```

## Reproducing finding 16

```bash
# 0. the control that licenses everything below (~2 min)
python3 common/layout/order.py --pattern p01-array-sum --copies 31 --reps 31

# 1. the population: 30 layouts x 3 rungs, 2 passes, small+large (~10 min)
python3 common/layout/layout_gen.py --pattern p01-array-sum --tag p01 \
    --seeds 21 --aligns 9 --reps 31 --passes 2

# 2. the mechanism, and how much of the published gap survives
python3 common/layout/loopfit.py  .temp/layout/layout_p01.json
python3 common/layout/analyze.py  .temp/layout/layout_p01.json
python3 common/layout/survives.py --dir .temp/layout p01

# 3. out of sample: prediction hashed before any timing (~5 min)
python3 common/layout/loopfit.py --loops <any build>        # pick the loop index
python3 common/layout/predict_then_time.py --pattern p01-array-sum \
    --rules safe_naive=win32@0,safe_tuned=win32@0,unsafe=win32@0
```

`p07-binary-search` is the largest effect (R2 ×0.786 on `small`); `p01-array-sum`
is the one whose three rungs all have a mode, two of them running *opposite* to
R4's, so its published gap has no sign.

## Reading the output

- **`win32` / `jcc32` are the law; "bit 4 of the kernel entry address" is a
  proxy.** It works only because every kernel here is 16-byte aligned, so a
  32-byte-granular property takes exactly two values. A toolchain with 32-byte
  function alignment would erase the proxy and leave the effect.
- **The geometry flip is universal; being front-end-bound is not.** p02, p05,
  p16 and p17 all have loops whose `win32`/`jcc32` flips with layout exactly as
  p01's and p07's do, and their time does not move. p07 is special only in
  having a serial 73-byte loop where one extra fetch window is 33% more
  front-end work.
- **Never pick "the inner loop" by a heuristic.** `loopfit` enumerates all of
  them and makes the caller name an index. The predecessor's "tightest backward
  branch" rule picks a 12-byte scalar tail over a 30-byte SSE loop on any
  vectorised kernel, and that is what produced p07 §11e's wrong-loop negative.
- **Publish mode-matched medians and pairwise `P(A>B)`.** A band is an extremum
  pair and widens with N; dominance-vs-worst is also defined against an extremum
  and does not converge (±26 points at N=4). Both are retracted.
- **A sign that flips between modes is not a sign.**
