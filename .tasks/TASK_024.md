# TASK_024 — the unroll factor is unpinned, and we are not allowed to pin it

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_023_REVIEW_REPORT.md`
**in full** — blockers 1 and 2 and majors 3–5 are this task — and
`.memory/01-ladder.md`'s p16 entry and named-spelling-standard block, both
already corrected by the manager and the wording to follow.

## What was measured

p16's declaration licenses **unrolling** and pins no factor. LLVM unrolls the
shipped fold 4×, and the per-byte rate is **`5 + 3/K`** — 5.7500 at K=4, 5.1875
at K=16, 5.09375 at K=32, zero fitted parameters, confirmed in the disassembly.

So `sv_c32` — shipped `safe_tuned.rs`, **one substitution, zero `unsafe`, both
named tokens literal, 95/95 equivalent** — measures
`R4ship − sv_c32 = 51·nrec − 5` (`vlen ≡ 0 mod 4`) / `48·nrec − 5`, zero residual
over 22 blobs: **+199 at `small`, +2365 at `large`. Safe beats shipped unsafe on
all 24 points.**

p16's headline — *"R3's marginal rate is 5.7500, R4's exactly; safe Rust costs
zero per byte"* — is therefore **sign-wrong in contract**: −0.5625 Ir/byte.

## The decision, and why it goes the way you may not expect

The tempting fix is to pin the unroll factor, or to forbid a manually unrolled
fold, which would put `sv_c32` out of contract and restore `+27 / +77`.

**We are not allowed to do that, by our own rule.** `.memory/01-ladder.md`'s
**direction test** says an edit to a declaration is not self-certification only
if it **shrinks the admissible class** *and* **does not raise the pattern's own
published figure**. Excluding `sv_c32` shrinks the class **and raises the figure
from −199 back to +27**. It fails the test outright, and it is precisely the
retroactive exclusion the test was written to forbid.

So: **accept that per-byte rates are K-dependent and report them that way.** Do
not add a `forbidden` entry. If you think the direction test itself is wrong
here — that there is a principled reason a manually unrolled fold is a different
kernel rather than a cheaper spelling of the same one — **argue it with the
disassembly**, because that is a real position and I would rather hear it than
have the rule applied mechanically. It is not enough that the shipped number is
nicer.

## What to land

1. **p16's `NOTES.md` and `README.md`**: the `5 + 3/K` law with its three
   measured points; `sv_c32`'s law and its equivalence evidence; the headline
   restated as **K-dependent**, with "zero per byte" struck and −0.5625 given as
   the in-contract figure; and the plain statement that **p16 is the second
   pattern after p17 where an admissible safe rung beats its own R4**.
2. **The refuted interval**, in every file that carries it: published
   17…47 / 43…127 ("111%/109%"), measured **−239…+236 (1759%) /
   −2449…+2244 (6095%)**, bottom **negative on all 24 points**. Sites named in
   the review: `p16/NOTES.md:1312-1332`, hashed `spec.md:297`,
   `p05/NOTES.md:1752`, `p05/README.md:176`. (`.memory/` and `RECAP.md` are done.)
3. **The one-sided bound's number**: in-contract R3 minimum against shipped R4 is
   **−199 / −2365**, not `+19 / +45`. The bound survives; the value does not.
4. **`p16/NOTES.md:1334-1337`** says the per-byte null survives and is *"stated
   so nobody re-runs them"* — that sentence told the next agent not to run the
   experiment that broke it. Replace it with the opposite instruction.
5. **Withdraw, do not re-point, the "loosest declaration" comparison.** Its
   replacement compares a 2-lever p16 search against p05's 46-spelling one, which
   is the same error one level down.
6. **`p02/spec.md:227`** still says "is an UPPER BOUND" bare inside the hashed
   block whose shared paragraph now denies it. Inconsistent rather than false;
   fix while the gate runs.
7. **`r4_hdr` cannot be a p16 rung** and the files should say so where they
   currently imply symmetry: vstd does not support `read_unaligned` and the
   `identity` pin needs R5 ≡ R4, so it would need a **fourth trusted item** in a
   pattern whose whole claim rests on one trusted `requires`. The R3-side
   variants cost **zero TCB**. `gen_controls.py:69-71` already says this; §10a.1
   and the hashed `why` do not.

## The question I want answered next, but not in this task

`5 + 3/K` is **not p16-specific** — any pattern with an inner byte loop is
exposed, and **p17 and p02 both publish one-sided R3 bounds today**. Do not
measure them here. Say in your report which of the two you would probe first and
why, in one paragraph.

## Done when

All seven items land; p16, p05 and p02 gates green (others only if you touch
them); `md5_fn` unchanged. **Expect ~32 leaves of gate-record churn on an
unchanged tree** — p08 alone contributes 23 across all four opt/mode
combinations to ±0.08 (`.memory/03-measurement.md`). Subtract before attributing.

Prose first, gates last.

## Constraints

No root; no `/tmp` (scratch `.temp/p24/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. Prose and `controls/*.py` only — **nothing in
`harness/`, no cell source**. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never
`pkill`/`killall`; confirm an exact PID's full command line before any kill.
Check `git status` before finishing.

Notes to `.temp/p24/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Thirty agents
have contradicted the manager's written instructions and all thirty were right;
the last one confirmed the thing it was sent to attack and then broke everything
built on it. What I am least sure of is **whether "accept K-dependence" is a
finding or a surrender.** A per-byte rate that is a free parameter of the
spelling may mean this project cannot publish per-byte rates at all — which
would be a larger and more useful result than any single pattern's number, and
if the measurements support it, say so plainly.
