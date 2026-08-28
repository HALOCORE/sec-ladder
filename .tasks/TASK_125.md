# TASK_125 — make the `.temp/` convention CHECKABLE, and pay only the cheap half of the debt

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
**`.tasks/TASK_121_REPORT.md`'s `.temp/` section in full**, then `CLAUDE.md`
rule 1 and `.memory/00-environment.md` constraint 6.

Scratch in **`.temp/t125/`**.

⚠ **Needs the tree. It edits `harness/`, so it costs ONE 26-pattern gate sweep
and NO re-measure — provided you obey §C's exclusion list.**

---

## The policy, already adopted — you are IMPLEMENTING it, not deciding it

> ✅ **PROMOTE, DON'T PUBLISH.** **Do not commit `.temp/`.** **Any `.temp/` path
> cited from a COMMITTED file must be PROMOTED into the tree first** — kilobytes,
> not gigabytes. **`.tasks/*_REPORT.md` citations are EXEMPT: a report is a dated
> record of what was true when it was written.**

**Two precedents already worked:** `miri_leak_key.py` → `patterns/p42-goto-cleanup/controls/`,
and the layout populations → `common/layout/data/`.

⚠⚠ **THE HARM IS HISTORICAL, NOT HYPOTHETICAL. Manager-measured, and it is FAR
bigger than `TASK_121` reported:**

```
committed files (excluding .tasks/*_REPORT.md) citing .temp/ : 2454 distinct paths
                                              ALREADY DANGLING :   88, across 59 files
```

**The loss needed an `rm`, not a clone.** ⚠ **`TASK_122` could not raise an
18.9 M `Ir` drift from *sufficiency* to *actuality* because the probe source it
needed was one of these.**

## §A — ⚠⚠ THE CHECKER, AND THE IRONY IS THE POINT

**`TASK_121` wrote `.temp/t121/temp_citations.py`.** ⚠⚠ **A dangling-citation
checker that lives in `.temp/` IS ITSELF A DANGLING CITATION WAITING TO HAPPEN,
and the policy above cites it. It has to be promoted or the policy is
unenforceable.**

**Promote it to `harness/`.** ⚠ **Manager-verified cost: `check.py`'s gate-record
digest globs `harness/*.py`, so ADDING A FILE THERE STALES ALL 26 GATE RECORDS —
exactly like editing `check.py`. That is why this task is batched and why §B and
§C ride along in the same sweep.**

**Requirements:**
1. **Read the committed tree via `git ls-files`, not the working tree** — an
   untracked scratch file must not make the check pass.
2. **Exempt `.tasks/*_REPORT.md`.** ⚠ **Say so IN THE CODE with the reason**, or
   somebody will "fix" it later.
3. ⚠ **Skip documentation PLACEHOLDERS** (`.temp/pNN/`, `.temp/build/pNN/`).
   **The manager's first count called two of those "missing"; they are template
   text.** **Make the placeholder rule explicit and narrow.**
4. ⚠⚠ **AN ARM THAT MUST FIRE:** plant a citation to a path that does not exist,
   show the checker reports it, remove it, show the count returns. **A checker
   that has never failed is a checker you cannot trust** — and this project has a
   named class for that.
5. **Print the count and the file list; exit non-zero only on a NEW dangling
   citation** relative to a committed baseline you also add. ⚠ **Decide and
   defend whether the baseline is a file or a number** — a number is a cached
   derivation and this project has watched one rot three times.

## §B — the CHEAP half of the debt, and only the cheap half

**Of the 88, fix the ones whose files cost a GATE RUN and nothing more:**
`NOTES.md`, `README.md`, `controls/*`, `TOOLCHAIN.md`, `pilot/README.md`,
`common/layout/*`.

⚠ **"Fix" does NOT mean promote — the files are GONE and cannot be promoted.**
**It means make the citation honest.** ✅ **Prefer, in order:** *(a)* **the
generator is still there** → cite the generator and say what it regenerates;
*(b)* **the artefact is re-derivable** → cite the rebuild command;
*(c)* **neither** → mark it `(artefact deleted; NOT regenerable)` **and say what
it showed**, because that is strictly better than a path that silently resolves
to nothing.

⚠ **Do not delete the sentence around the citation.** **The claim it supports may
still be true and may be cited elsewhere.**

## §C — ⚠⚠⚠ THE EXCLUSION LIST. GET THIS WRONG AND THE TASK COSTS A RE-MEASURE.

**THREE of the 59 files are MEASUREMENT-HASHED and are OUT OF SCOPE:**

```
patterns/p22-hash-probe/model.py          1 dangling
patterns/p36-vtable-dispatch/verus.rs     1 dangling
patterns/p47-ct-compare/inputs/gen.py     1 dangling
```

⚠⚠ **`measure.py::measurement_sources` globs `*.rs`, `c/*`, `model.py` and
`inputs/gen.py`. A COMMENT-ONLY EDIT TO ANY OF THEM STALES THE MEASUREMENT
RECORD** — that is `CLAUDE.md`'s own rule and this project has paid for it.
**LEAVE ALL THREE ALONE. List them in your report as owed-and-costed, to be
bundled with the next re-measure of those patterns.**

⚠ **`synthesis/synthesize.py` and `results/synthesis.md`: `synthesis.md` is
GENERATED — never hand-edit it. Fix the citation in `synthesize.py` and
regenerate.**

## §D — the general form, and it is worth one paragraph in your report

⚠ **`TASK_121` found that `results/tables/*.md` is pinned on the CONTRACT, not
the CONTENT, and caught it live: stage 9 said `FRESH` while `p23-partition.md`
published a now-false sentence.** **It called that the THIRD instance of the
class.** ⚠⚠ **Your checker is a FOURTH instance of the same family: a claim in a
committed file, with nothing that detects it going false.** **Say whether the
family has a common fix or only case-by-case ones. Do not force an answer.**

---

## Constraints

- **`.temp/t125/` only. No `/tmp`.** **Notes in `.temp/t125/NOTES.md` AS YOU GO.**
- **No `git add` / `git commit`.** Read-only git is fine, and §A needs
  `git ls-files`.
- **`.memory/`, `RECAP.md` and `results/SYNTHESIS.md` are manager-only.**
  ⚠⚠ **`results/synthesis.md` (lower case) is GENERATED — never hand-edit it.**
- ✅ **You MAY edit `harness/`, `patterns/*/NOTES.md`, `patterns/*/README.md`,
  `patterns/*/controls/*`, `TOOLCHAIN.md`, `pilot/README.md`, `common/layout/*`
  and `synthesis/synthesize.py`.**
- ⚠⚠ **DO NOT TOUCH `harness/{build,asm,measure}.py`, `verus_run.py`, or ANY
  `patterns/*/{*.rs,c/*,model.py,inputs/gen.py}`** — every one is
  measurement-hashed. **§C names the three that tempt you.**
- ⚠ **Cite `check.py` by FUNCTION NAME, never a line number.** ⚠ **And note
  `TASK_121` found `_check_controls_json` cited in a task file resolves NOWHERE;
  the real name is `check_control_json_pins`. Verify any name you cite.**
- ⚠ **Every acceptance test needs an arm that FAILS.** Read the failure-class
  list at the end of `.memory/03-measurement.md` — ⚠ **it carries no usable
  count; read the list.**
- **§E, last: full 26-pattern `harness/check.py`, then `report.py` where tables
  moved, then `synthesis/licence.py --emit` BEFORE `synthesize.py`, then
  `outward_ir.py --emit`, then `synthesize.py` AGAIN, then
  `measure.py --check-stale`.** **Expect `24 PASS + 2 PASS-WITH-BLOCKED-ROWS`,
  0 failures, `52 records 0 STALE`.** ⚠ **`p42`'s blocked-row count may be 1 or
  2 for environment reasons — do NOT chase a Miri block.** **Anything else red:
  STOP AND REPORT.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_125_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 551** (`TASK_124` 526→536, then
`TASK_121` 536→551, sequential; ⚠ **a rigour signal, not a ledger — do not
re-add it**). The calls I am least sure of:

1. ⚠⚠ **That §B is worth doing at all.** **88 dangling citations across 59 files
   is a lot of prose churn for modest per-instance value, and the FORWARD rule in
   §A is where nearly all the value is — it prevents the 89th.** ⚠ **If your read
   after §A is that §B should be a baseline-and-freeze (record the 88, fail only
   on new ones, fix them opportunistically when a file is next touched for
   another reason), SAY SO AND DO THAT.** **I would not argue.**
2. ⚠ **That the checker belongs in `harness/`.** **It is a DOCUMENTATION check,
   not a gate stage, and putting it in `harness/` costs a 26-pattern sweep and
   implies it certifies measurements.** ⚠ **I could not find a better home that
   is not a new top-level directory — if you can, take it, and say what it costs
   instead.**
3. ⚠⚠ **That "promote, don't publish" is right.** **The alternative the manager
   framed for the user was committing the 1.2 MB of CITED evidence. `TASK_121`
   measured the true tree-wide figure at ~5.1 GB over 1412 paths, so the 1.2 MB
   was a subset and the framing was too optimistic.** ⚠ **But promotion has a
   cost the manager has not measured: how many of the 2454 cited paths would a
   strict forward rule force into the tree, and how big are they? IF THAT NUMBER
   IS LARGE, THE POLICY NEEDS A SIZE BOUND AND I HAVE NOT SET ONE. Measure it.**

Carry **551** forward, incremented by what you find.
