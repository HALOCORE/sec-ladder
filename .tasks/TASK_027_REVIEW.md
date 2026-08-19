# TASK_027_REVIEW — one inferential step, and whether it invalidates p05 and p17 too

**Role:** research reviewer. You do **not** fix; you report.
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_027.md` (the spec) and
`.tasks/TASK_025_REVIEW_REPORT.md` (which TASK_027 was landing), then
`patterns/p16-tlv-walk/spec.md`'s hashed `why` — specifically the sentence
**"AN R4-SIDE VARIANT MUST BE EXPRESSIBLE IN WHAT vstd CAN VERIFY, OR IT IS NOT A
RUNG"** and the paragraph around it.

## This review is deliberately NARROW. Read this before you plan.

Eleven consecutive tasks went to the spelling problem and six of 47 patterns
exist. The next task after this one is a **new pattern**, and this review exists
because one specific thing cannot wait: **a hashed contract changed, on the
manager's own least-certain call, justified by a rule that is itself flagged
PROVISIONAL and unreviewed.** That is the configuration this project has found
defects in more than any other.

**Do not re-open TASK_025_REVIEW's findings.** They are reviewed, landed and
reproduced — the null, the `−0.65625` arithmetic, the `try_into` control, the
`u_c32` Verus errors. TASK_027's own numbers are re-measured and green. **Four
questions, then stop.** If you finish early, say so; do not go looking for work.

## Q1 — the inferential step, which is the whole thing (highest value)

The gate checks that the **shipped** `unsafe.rs` and `verus.rs` produce identical
machine code (`identity: unsafe ≡ verus, O3 exact`). TASK_027 infers from that a
claim about **candidate** R4 spellings that were never shipped: that any
admissible R4 must be Verus-expressible, and therefore `u_c32` is not a rung at
all.

**Is that step valid?** The strongest case for it: an interval over "what an
admissible R4 could cost" is only meaningful over rungs you could actually ship,
and shipping one means satisfying the pin. The strongest case against: the pin
constrains a *pair of files*, not a *class of programs*, and reading it as a class
constraint is a new restriction wearing a consequence's clothes — which is
exactly the self-certification move `.memory/01-ladder.md` has a test for.

Note what turns on it. If the step is invalid, `u_c32` is an admissible R4 whose
R5 twin merely has not been written, TASK_025_REVIEW's blocker 1 weakens from
"not a rung" to "a gap in the pattern", and the sentence in the hashed block has
to come out. If it is valid, it stands — and Q2 becomes urgent.

Give me the argument, not a vote. If you can settle it by construction (does any
*other* pattern's `spec.md` or the gate itself already read a pin as a class
constraint?), do that.

## Q2 — does the same argument invalidate p05's and p17's published R4-side numbers?

**This is the one I most expect to land, and it is cheap.** If Q1's step is valid,
it applies to every pattern, because **all six pin `identity` exact**. Then:

- p05's R4 "moves 7 flat" via a respelled header read (TASK_022), and that figure
  is load-bearing in `.memory/01-ladder.md` and `RECAP.md`.
  **Is that respelling Verus-expressible at the pinned vstd?** If it is not, p05's
  R4-side number has the same defect p16's just had, and it is published.
- p16's own `r4_hdr` was already disqualified for exactly this reason
  (`read_unaligned` unsupported) — and `.memory/01-ladder.md` notes it was *"the
  same lever that moved p05's R4"*. **That sentence is a prediction. Test it.**
- p17's `−19.00` in-contract respelling: R3-side or R4-side? If R4-side, same
  question.

`./verus_run.py` and the existing `verus.rs` cells are all you need. A clean
negative here is worth as much as a finding — say which of the three are safe.

## Q3 — the two new committed scripts, run as committed

`controls/gen_controls.py`'s new `FOLD_CONTROLS` (18 variants) and the new
`controls/foldcmp.py` exist **because the artefact they replace printed the
opposite of the claim it was cited for**. Do not let the replacement have the same
defect.

Run both from a clean checkout path, as a reader would. Does `foldcmp.py` print
the table `NOTES.md` §10a.2 cites it for? Does `gen_controls.py` regenerate
variants that still compile and still match the gate's `spelling_matches`? Does
anything still carry a hardcoded absolute path? Does the new `inputs/gen.py` band
regenerate byte-identically twice, and do the 95 pre-existing blobs still hash the
same?

## Q4 — the band-cost claim, now in `.memory/05-layout.md` as a general rule

TASK_027 measured that appending a sweep band last costs a **gate re-run only, not
a re-measure**, because `check.inputs_of` and `measure.SKIP_INPUT_PREFIX` both
drop `sweep-*`. I landed that as a general rule that the **next pattern will rely
on** (p07 ships a sweep from day one). Verify it is general and not p16-specific —
read the two harness call sites, and say whether any pattern-specific config could
make a `sweep-*` blob reach the measurement matrix after all. If the rule is
wrong, p07's design changes, so this is worth ten minutes.

## Clean negatives are worth as much as findings

PROTOCOL rule 6. For anything you check that does **not** land, say so with the
evidence so the next agent does not re-run it.

## Constraints

No root; no `/tmp` — scratch under `.temp/r27/`, and per
`.memory/00-environment.md` constraint 6 **delete your binaries and generated
blobs when you finish, keep your scripts and notes**. **No `git add`/`git
commit`** — read-only git. Do not edit `pilot/`, `.memory/`, or anything under
`patterns/` — you report, you do not fix. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never
`pkill`/`killall`; confirm an exact PID's full command line before any kill.

**Run measurements in the FOREGROUND** — background `nohup` jobs on this box are
reported "completed" while still running, which corrupted a data point two tasks
ago. Per-PID scratch paths.

Notes to `.temp/r27/NOTES.md` as you go so you can be resumed; three agents on
this arc have died to transient API errors.

Report in PROTOCOL's format, severity-ranked, file:line and a concrete failure
scenario per finding. Paste actual command output.

**Contradicting the manager with a measurement is the highest-value thing you can
do.** Thirty-three agents have and all thirty-three were right — the last one
caught me pairing one rung at both inputs and calling it a minimum. The thing I am
least sure of is **Q1**, and I wrote the task that told the engineer to make that
edit, so I am the wrong person to clear it.
