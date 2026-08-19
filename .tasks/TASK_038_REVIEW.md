# TASK_038_REVIEW — p09 claims a bug a memory-safety proof cannot see. Check that the proof isn't just weak.

**Role:** research reviewer. You do **not** fix; you report.
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_038.md` (the spec), then
**`patterns/p09-bitset/NOTES.md` in full**, then its `spec.md`, `model.py`,
`inputs/gen.py`, `controls/gen_controls.py`, and `.memory/01-ladder.md` findings 5
(p17 — memory-safe but wrong) and 10 (p03 — the seeding result p09 says does not
transplant).

p09 is the tenth pattern: gate `PASS` on a complete run, R5 18/0, R4 ≡ R5 `exact`,
**unreviewed**. Per rule 9 none of its findings are in `.memory/` — this review
decides what goes in.

## The claim to attack first

**`q & 31` is invisible to a memory-safety proof** — `m_mask31_msonly` verifies
`19/0` with the functional spec stripped, and `m_mask31_spec` verifies `20/0` once
the spec moves to match. That is p17's result made concrete and it will be quoted.

**The obvious failure mode is that the proof is simply weak**, and the engineer
anticipated it with a positive control (`m_control_msonly`, 18/0). Push harder:

- **Is the memory-safety-only spec actually asserting anything?** Strip it further
  and find the point where the proof *should* fail but doesn't. A `msonly` spec
  that has become vacuous would produce 19/0 for the wrong reason, and this
  project has six recorded instances of "a vacuous truth in a log reads like a
  discharged obligation".
- **Does the trusted accessor's `requires` still bite under `m_mask31`?** The
  whole claim is that the *access* stays in bounds. Verify that by deletion — the
  gate's own per-conjunct twin probe is the tool.
- **`q >> 5` is `q/32 ≥ q/64`, so it is a second SPATIAL bug**, and the engineer
  says so. Then what is the *arithmetic* bug on this kernel — is there one at all,
  or does every index error on a bitset degenerate to a spatial one? If the answer
  is "there isn't one", p09's second axis is `q & 31` alone and the pattern should
  say that rather than implying a family.

## The rest, in order

1. **The three-way check decomposition** (+19 / +11 / +45, cheapest in-contract
   0.00000 / −3.00000 / +4.00000). Pooled rank 4/4 with **every band alone at
   2/4** — so the design carries the result, not the residual. Verify the rank
   claim and that the regressors are not collinear in the shipped bands. p03's
   review found exactly this shape of problem.
2. **"p03's seeding control does not transplant."** A dead clamp on the *word
   index* is +461 **dearer**; on the *byte offset* it deletes 49% of the kernel;
   one that says nothing is byte-identical to shipped R3. The conclusion drawn is
   that **the failed inference is the composition through the multiply, not the
   shift**. That is a strong mechanistic claim about LLVM and it now qualifies
   finding 10 — re-derive it from the listing. And check every clamp control
   against `check.py::spelling_matches` before crediting it; p03 shipped two that
   the ruler rejects.
3. **R3 dearer than R2 — a first.** 20448 vs 16628 on `small`. The mechanism given
   is a reslice hoisting eight address computations above eight checks and
   spilling (82-instruction body with a stack reload vs 65). Confirm it, and say
   whether it is a p09 fact or a *general* hazard of the reslice idiom this
   project has recommended since p16.
4. **`q >> 6` ≡ `q / 64` on three compilers.** Cheap to re-check and it decides
   whether a `forbidden` entry that moves no number should exist at all.
5. **The intrinsic row.** No rung emits `popcnt`; clang's builtin and rustc's
   `count_ones()` lower to the same 23-instruction SWAR; gcc calls
   `__popcountdi2` at +29.00/word, invisible to the kernel-exclusive column.
   Confirm, and confirm the gcc marginal is what p09 publishes.
6. **The disclosed harness trap.** `_blank_ghost` does not blank `spec fn` bodies,
   so a `forbidden` entry could fire on p09's own `verus.rs`. The engineer avoided
   it by spelling the spec `q as int / 64` and **disclosed it as the thing to
   attack**. Attack it: is the avoidance robust, or does some other pattern's
   declaration already trip it?

## Also

The engineer flagged two things it could not settle: `m_clampb_lo` (one byte short
of what the access needs) behaves like `m_clampb`, so **p03's "one past the
invariant" negative control does not separate here**, and a +3-instruction static
difference at −1.00 Ir is unexplained. And `x_mask31_n`'s +3827 on R2 has no
mechanism. Either would be a good find.

## Clean negatives are worth as much as findings

PROTOCOL rule 6. **And if the invisibility claim holds, say so plainly** — "a
one-character edit that no sanitiser, no bounds check and no memory-safety proof
detects, one character away from one they all catch" is the sharpest statement
this project has about what verification does *not* buy.

## Constraints

No root; no `/tmp` — scratch `.temp/r38/`, delete binaries and blobs when done.
**No `git add`/`git commit`** — read-only git. Do not edit `pilot/`, `.memory/`,
or anything under `patterns/`. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`.
**No `nohup … &` background jobs** — one reported exit 0 after finishing 1 of 8
cells on this very pattern. **Measurements in the FOREGROUND, interleaved by
cell**; `harness/measure.py --check-stale` before quoting a record.

Notes to `.temp/r38/NOTES.md`. Report in PROTOCOL's format, severity-ranked, with
file:line and a concrete failure scenario per finding.

**Contradicting the manager with a measurement is the highest-value thing you can
do.** Forty-nine agents have and all forty-nine were right — p09's own engineer
refuted both premises I gave it, including my belief about which spelling was the
arithmetic bug. I have no independent view of its numbers; I am relaying them.
