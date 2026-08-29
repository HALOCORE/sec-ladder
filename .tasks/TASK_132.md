# TASK_132 — REVIEW of `TASK_127` / finding 46, and the class it opened: numbers that come from GREPPING A LOG

**Role: research reviewer.** ⚠ **ATTACK. Finding 46 is landed in `RECAP.md`
UNREVIEWED and it carries a NEW FAILURE CLASS that is deliberately NOT yet in
`.memory/03-measurement.md` because of rule 9 — your review is what lets it
land.**

Read `.tasks/PROTOCOL.md`, then this file, then **`RECAP.md` finding 46 IN
FULL**, then **`.tasks/TASK_127_REPORT.md` IN FULL**, then `.tasks/TASK_127.md`
(what was asked), then **`harness/check.py::check_table_render` and
`harness/report.py::read_gate_loud`** (the two docstrings that carry the
mechanism), then `.memory/03-measurement.md`'s failure-class list (entries 9 and
10 landed in the last two tasks).

Scratch in **`.temp/t132/`**.

✅ **THE TREE IS YOURS. No other task is live.** ⚠ **So you MAY run
`harness/check.py`** — but read §E's budget first, and ⚠⚠ **DO NOT RUN
`harness/measure.py` (except `--check-stale`) OR `harness/build.py`, and DO NOT
EDIT any `patterns/*/{*.rs,c/*,model.py,inputs/gen.py}`: those are
measurement-hashed and a re-measure is not in this budget.**

---

## §A — ⚠⚠ THE TRADE THE ENGINEER ASKED YOU TO ATTACK, IN ITS OWN WORDS

> *"The one-run lag is kept deliberately and is not free; a reviewer should
> attack that trade, not the byte comparison."*

**Stage `9c` re-renders each table and compares bytes — but it runs MID-GATE and
reads the PREVIOUS run's `results/gate/<p>.json`. Moving it after the record
write would remove the lag AND REINTRODUCE THE SELF-REFERENCE, so the engineer
rejected that and documented why.**

⚠ **The engineer also left this open and unmeasured:** *"after any FULL failing
gate run, the next run's 9c may fire for fields that run changed. Judged
acceptable; frequency unmeasured."*

**Measure it.** ✅ **The fields `report.py` reads are known and small —
`{contract_sha256, controls_json, idiom_audit, loud}` — so the question is
narrow: WHICH OF THOSE FOUR CAN A GATE RUN CHANGE, and under what
circumstances?** ⚠⚠ **`loud` is the dangerous one: `rep.shout` writes it, and a
shout is exactly the kind of thing a run can start or stop doing.** **Find a
real case or show there is none.**

⚠ **And ask the sharper question the report does not: IS THE LAG EVEN THE RIGHT
FRAME? A user runs the gate, sees `PASS`, and commits. If 9c would have fired on
the NEXT run, the committed tree is stale and green.** ✅ **Stage 9 has had this
shape all along, so *"status quo"* is a true defence — ⚠ but *"the old check was
also wrong"* is not the same as *"this is fine", and the report leans on it.**

## §B — ⚠ IS THE SELF-REFERENCE ACTUALLY GONE, OR JUST THE ONE INSTANCE OF IT?

**`report.py` no longer renders `verdict`. The standing detector
`harness/tools/table_render_inputs.py --selfref` reports `0 of 26 × 9`.**

1. ⚠⚠ **Where does the `9` come from?** **If the run-scoped key list is
   hand-written, the detector can only find self-references somebody already
   thought of — and this project has a named failure for that (*"a grep that can
   only find what you already thought of is not a census"*).** **Enumerate the
   gate record's keys and say which are run-scoped; compare with the detector's
   list.**
2. ⚠⚠ **GIVE THE DETECTOR A MUST-FIRE ARM.** **Put `verdict` back into the
   render in `.temp/t132/`, run `--selfref`, and show it exits 1.** ⚠ **The
   engineer disclosed that its FIRST `--reads` implementation was a control that
   could not fire; do not assume the second one can.**
3. ⚠ **The detector is OUTSIDE the gate on purpose** (wiring it in would put it
   in the digest and cost a sweep to maintain). ✅ **Say whether that is the
   right call. An opt-in detector for a defect that took a full task to find is
   a detector nobody will run.**

## §C — ⚠ SUBSUMPTION, AND `RENDER-ERROR`

- **The report says 9c subsumes 9 (a fresh render always carries the current
  contract line) and that 9 is kept anyway for three reasons.** ⚠ **Test the
  subsumption: construct a case where stage 9 FIRES and 9c does NOT, or show
  none exists.** ✅ **If one exists, the "subsumes" sentence in BOTH docstrings
  is wrong and it is the kind of sentence that gets believed.**
- ⚠⚠ **`report.py` RAISES on a malformed `idiom_audit` and 9c catches it as
  `RENDER-ERROR`. IS `RENDER-ERROR` A FAILING VERDICT?** **If it is recorded but
  does not fail the gate, then a pattern whose table cannot be rendered at all
  passes — which is worse than the `MISSING` case the stage was built for.**
  **Read the code and say.**

## §D — ⚠⚠⚠ THE CLASS `TASK_127` OPENED AND DID NOT SWEEP, AND IT IS THE BEST THING IN THIS TASK

**`TASK_127` found that `p42`'s and `p22`'s blocked-row counts were never
measurements at all: `TASK_125`'s sweep used `grep -c BLOCKED`, which matches the
VERDICT STRING `PASS-WITH-BLOCKED-ROWS`.** ✅ **Manager-verified from the JSON:
`p01 = 1`, `p42 = 1`, everything else `0`. `p22`'s "hit" was its own `NOTES.md`
prose echoed into the log.**

> ⚠⚠⚠ **SO: HOW MANY OTHER PUBLISHED NUMBERS IN THIS PROJECT COME FROM GREPPING
> A LOG RATHER THAN READING A RECORD?**

✅ **This is one pass over `.tasks/*.md`, `.memory/`, `RECAP.md`,
`patterns/*/NOTES.md` and `harness/tools/`, and it is the highest-value thing
here because the gate records are structured JSON and every number in them is
readable directly.** ⚠ **Report the SITES, not just a count — and ⚠⚠ for each
one say whether the grepped number AGREES with the record. A `grep` that happens
to be right is not a defect; a `grep` that is wrong is a published false
number.**

⚠ **Budget it. If the sweep is large, do the gate-record-derived numbers first
(`blocked`, `verdict`, `failures`, `loud`, `miri`, `sanitizer`) — those are the
ones with a record to check against.**

## §E — the ride-alongs, both FREE, and the reason they are free is measured

⚠⚠ **`check.py`'s digest globs are NON-RECURSIVE — ✅ manager-verified in the
source: `common/*.py`, `common/layout/*.py`, `harness/*.py`.** **So a NEW
directory `common/census/` is OUTSIDE the digest exactly as `harness/tools/`
is.** ⚠ **Price, and write it down where the files live: nothing under it may be
imported by `check.py`/`measure.py`/`build.py`, or it silently rejoins the
digest.**

1. ⚠⚠ **PROMOTE `TASK_129`'s THREE SHA256 MANIFESTS** (956 K, in gitignored
   scratch). **A census whose corpus cannot be re-identified is a census nobody
   can check, and two of the three corpora live under ANOTHER PROJECT'S
   `.temp/`, which that project's convention makes deletable at any time.**
   ⚠ **Judge the size: 956 K against a policy whose own words are *"kilobytes,
   not gigabytes"*. ✅ If you can get the same re-identification guarantee
   smaller — a sorted `path<TAB>sha256` list is already near-minimal, but a
   single digest-of-digests plus counts may be enough — TAKE IT AND SAY WHAT IS
   LOST.**
2. ⚠ **SHIP `TASK_131`'s CLASSIFIER-FREE REGEX AS A SCRIPT.** **`RECAP` finding
   45 published *"`845` over PHP, `0` over the kernels, both numbers exact"* and
   ⚠⚠ **THAT `845` CANNOT BE RE-DERIVED — the reviewer's reconstruction gives
   `854` and the original regex was never written down.** ✅ **Ship the script,
   re-run it, and put the number IT prints into the finding — the `0` is what
   carries the claim and it reproduces on three independent instruments.**
   ⚠ **Its must-fire arm already exists: `.temp/t131/planted/p01_ptr_kernel.c`.**

## §F — verification, and the budget

**A `check.py` edit is NOT expected in this task. If you make one, say why, and
then §F is a full 26-pattern sweep.** ✅ **If you make none — which is the
expected outcome — verification is:**

- **`harness/check.py p03` and one other pattern** (enough to prove nothing
  moved), **plus `harness/measure.py --check-stale`.**
- ⚠ **`common/census/` and `harness/tools/` are outside the digest, so adding
  files there costs NO sweep — ✅ CONFIRM THAT rather than assuming it: check
  `source_sha256`'s key set before and after.**
- **Expect `24 PASS + 2 PASS-WITH-BLOCKED-ROWS` if you do sweep, `52 records
  0 STALE`, `stage 9c FRESH`.** ⚠ **`blocked` is `p01 = 1`, `p42 = 1` and
  NOTHING ELSE — read it from the JSON, and if you find yourself typing
  `grep -c`, re-read §D.**

---

## Constraints

- **`.temp/t132/` only. No `/tmp`.** **Notes in `.temp/t132/NOTES.md` AS YOU GO.**
  **Keep the generator, delete the artefact.**
- ⚠⚠ **PROMOTE, DON'T PUBLISH — and §E is the promotion. Do not commit
  `.temp/`.** ✅ **Run `harness/tools/temp_citations.py` before finishing;
  expect `rc=0`.** ⚠ **It has TWO known defects: it matches `.temp/` anywhere in
  a line (so an absolute path into another repo's `.temp/` false-positives), and
  it cannot see a path a committed Python file ASSEMBLES with
  `os.path.join(REPO, ".temp", …)`. ✅ BOTH ARE FREE TO FIX — it is in
  `harness/tools/`. Fix them or say why not.**
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **`.memory/`, `RECAP.md` and `results/SYNTHESIS.md` are manager-only.**
  ⚠⚠ **`results/synthesis.md` (lower case) is GENERATED — never hand-edit it.**
- ⚠⚠ **DO NOT EDIT `harness/{build,asm,measure}.py`, `verus_run.py`, or ANY
  `patterns/*/{*.rs,c/*,model.py,inputs/gen.py}`.**
- ⚠ **The C corpora are OTHER PROJECTS' REPOSITORIES — READ ONLY.**
- ⚠ **Every probe needs an arm that MUST FIRE.** **Read the failure-class list
  at the end of `.memory/03-measurement.md` — ⚠ it carries no usable count.**
  ⚠⚠ **Entries 9 and 10 landed in the last two tasks and BOTH are about arms
  that ran: entry 9 (a calibration arm that was really a specificity control)
  and entry 10 (a control whose published table predated its own last fix).
  ⚠⚠⚠ Entry 10's defence is the one to apply to yourself: WRITE EVERY ARM TO A
  FILE AND REGENERATE THEM ALL FROM A `REBUILD.sh` BEFORE YOU WRITE THE
  REPORT — a number quoted from a terminal is undated.**
- ⚠ **The publishing chain's `--emit` TAKES A PATH.** **`synthesis/licence.py
  --emit synthesis/licence.json`, `synthesis/outward_ir.py --emit
  synthesis/outward_ir.json`.** ⚠⚠ **Bare `--emit` exits `rc=2` and writes
  NOTHING, and `synthesize.py` then rebuilds against a stale input — it cost
  `TASK_127` a run and produced 209 false `LICENCE STALE` lines. The wrong
  spelling is still in `TASK_121_REPORT.md` §A and in `TASK_127.md` §F.**
- `timeout <N> <cmd>`; never `pkill`/`killall`. ⚠⚠ **NO `nohup … &` — constraint
  2 forbids it BY NAME and `TASK_127` broke it and self-reported.**

Write your report to `.tasks/TASK_132_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count: the manager has NOT reconciled five
concurrent branches** (`TASK_127` 583→595, `TASK_128` 583→594, `TASK_130`
594→617, `TASK_129` and `TASK_131` both from 583). ⚠⚠ **Treat **617** as the
carried figure and DO NOT RE-ADD ACROSS BRANCHES — it is a rigour signal, not a
ledger, and reconciliation is the manager's.** The calls I am least sure of:

1. ⚠⚠ **That the one-run lag is acceptable.** **I accepted the engineer's
   *"status quo"* defence when I landed finding 46, and I am not sure I should
   have. *"The old check was also wrong"* is not *"this is fine"*, and the
   failure mode is a user seeing `PASS` and committing a tree that 9c would fail
   on the next run.** ⚠ **If §A finds a real case, the finding needs a caveat
   and the docstring needs a sentence.**
2. ⚠⚠ **That §D is one pass and not a rabbit hole.** **I think the grep-a-log
   class is the most valuable thing in this task and I have not scoped it. If it
   turns out to be 200 sites, DO THE GATE-RECORD-DERIVED ONES AND SAY YOU
   STOPPED — `.memory/`'s rule is NO SILENT CAPS.**
3. ⚠ **That the manifests are worth 956 K in the tree.** ⚠ **The policy says
   *"kilobytes, not gigabytes"* and this is neither. I lean promote, because the
   alternative is a published census nobody can re-identify — but if you find a
   smaller artefact with the same guarantee, take it, and if you think the whole
   promotion is wrong, SAY SO; it is one paragraph either way.**

Carry **617** forward, incremented by what you find.
