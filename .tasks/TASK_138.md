# TASK_138 — the two PROVISIONAL markers INSIDE hashed contract fences

**Role: research engineer.** ⚠⚠ **You are the only agent permitted to run
`harness/check.py` and `harness/measure.py` right now.** A concurrent reviewer is
working under `.temp/t137/` and is barred from both.

## What this is

`TASK_135` found debt nobody had counted: **`patterns/p09-bitset/spec.md` and
`patterns/p16-tlv-walk/spec.md` each carry a `PROVISIONAL` marker INSIDE the
`slb-contract` fence** — inside the block whose bytes are hashed into
`contract_sha256` — and both **propagated into gate records and published
tables**. Every previous triage looked at `RECAP.md` and `.memory/` and missed
them.

Both markers say the same thing: that `.memory/01-ladder.md`'s **direction-test
repair** is *"unattacked"*, and `p16`'s goes further — *"must not be cited here
again until a reviewer has attacked it."*

## ⚠⚠⚠ DELIVERABLE 1 — SETTLE WHETHER THE MARKERS ARE ACTUALLY FALSE. VERIFY BEFORE YOU EDIT.

**`TASK_135` reports they are false**, citing `TASK_045_REVIEW` blocker 1.
✅ **The manager verified one line of that**: `.tasks/TASK_045_REVIEW_REPORT.md:214`
reads *"**The direction test FIRES on p13**: the byte-loop copy/fill idiom
entries move the headline by 105.00 / 193.00 Ir/call. (p04's moved by 0.00.)"*

⚠⚠ **BUT THE MANAGER IS NOT CONFIDENT THAT SETTLES IT, AND SAYS SO RATHER THAN
LETTING YOU INHERIT IT.** *"A reviewer APPLIED the test and it FIRED"* and
*"a reviewer ATTACKED the repair"* **are different claims**, and
`.memory/03-measurement.md` entry 13 plus `TASK_135`'s own brief both turn on
exactly that distinction. ⚠ **Note also that `.memory/01-ladder.md` records an
attack on the PROVENANCE GUARD — *"the engineer who was asked to attack it took
it apart"* — which is a DIFFERENT object from the direction test itself. Do not
let those two merge.**

**So: read `.memory/01-ladder.md`'s direction-test section, `TASK_045_REVIEW.md`
and its `_REPORT.md`, and `TASK_019`. Decide, on the evidence:**

- **`MARKERS ARE FALSE`** — the repair was attacked; the markers must go.
- **`MARKERS ARE STALE AS WORDED`** — the repair has been exercised but not
  adversarially attacked; **reword to say what is actually true** rather than
  deleting.
- **`MARKERS STAND`** — `TASK_135` and the manager are both wrong. ⚠ **This is a
  perfectly acceptable answer and you should say so plainly if it is what you
  find.**

⚠⚠ **DO NOT EDIT A HASHED FENCE UNTIL DELIVERABLE 1 IS DECIDED.** The edit costs
two `contract_sha256` moves and two gate re-runs, and a wrong edit is expensive
to unwind because it churns published tables.

## Deliverable 2 — land whatever deliverable 1 licenses

If the markers change: edit **only** the marker text in the two `slb-contract`
blocks, re-run `harness/check.py p09` and `harness/check.py p16`, and confirm
both go green with the new `contract_sha256`.

⚠ **This is a CONTRACT move, NOT a re-measure.** `measurement_sources` covers
per-pattern `*.rs`, `c/*`, `model.py`, `inputs/gen.py` — **`spec.md` is not in
it**, so no measurement record should go STALE. ✅ **Verify that claim rather
than trusting it: run `harness/measure.py --check-stale` before and after and
show both.** If anything goes STALE, **stop and report** — that would itself be
a finding about what the contract hash reaches.

⚠ **Diff the two gate records before/after and say which fields moved.** A gate
record is not byte-reproducible (`.memory/03-measurement.md`), so expect
`sanitizer diagnostic` strings, `miri.runs[].seconds`, adversarial group order
and the `N distinct behaviours` note to move for reasons that are **not** your
edit. **Do not report those as consequences of the change.**

## Deliverable 3 — is there more of this class?

⚠⚠ **The interesting question is not these two.** `TASK_135` counted markers in
`RECAP.md`, `.memory/` and `SYNTHESIS.md` **and found these two only because it
went looking inside `patterns/`.** **Sweep `patterns/` properly** — all of
`spec.md`, `NOTES.md`, `controls/`, and the `.rs`/`.c` sources — for
`PROVISIONAL`, `UNREVIEWED`, `TODO`, `FIXME`, `XXX` and `unattacked`, and report
what is **inside a hashed region** versus merely nearby. **Publish the command
so the sweep is repeatable.**

## Rules

- `.temp/t138/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`** — the manager applies those. No `git add`/`git commit`.
- ⚠ **Do not touch `.temp/t136/` or `.temp/t137/`** — one is evidence under
  review, the other is a live agent's workspace.
- ⚠ **Read `blocked` out of the RECORD, never `grep` the log** —
  `grep -c BLOCKED` matches `PASS-WITH-BLOCKED-ROWS` and decodes as `2N+1`.
  Expect `p01 = 1` and `p42 = 1` and **do not read a second `p42` block as a
  regression** (the Miri slowdown is environment-selected).
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Keep the generator, delete the artefact (`.memory/00-environment.md`
  constraint 6).
- Report to `.tasks/TASK_138_REPORT.md`. **PROTOCOL rule 2: you carry 664.**
  Close with your branch delta and the sum. ⚠ **A concurrent branch also carries
  664; reconciliation is the manager's.**
