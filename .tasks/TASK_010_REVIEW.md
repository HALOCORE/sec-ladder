# TASK_010_REVIEW — does the hardened gate let honest work through?

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_010.md` (the spec),
`git show 98da583` (the delivery), `.temp/p010/NOTES.md` (the engineer's notes),
then `.memory/02-bench-rules.md` **top section** and `.memory/04-verus.md`.

## Why this review is shaped differently

Every previous review on this project hunted **bypasses** — ways a defective
pattern could pass a green gate. That direction is now closed by decision, not by
exhaustion: the user has settled the gate's threat model as **honest mistake, not
malicious pattern author** (`.memory/02-bench-rules.md`, top). Residuals we are
deliberately leaving open are named there. **Do not spend this review inventing a
seventh bypass.** If you find one incidentally, report it as a one-line residual
and move on.

The direction that matters now is the opposite one, and it has never been
reviewed: `harness/check.py` is **4209 lines** guarding **two patterns**. Ten
tasks in, six went to gate hardening. The live risk to this programme is no
longer a fake pass — it is a gate that **fails, blocks, or misjudges honest
work**, and 45 unbuilt patterns behind it.

So: your job is to find where the TASK_010 gate is **wrong or obstructive**, and
to answer one concrete forward-looking question before an engineer hits it.

## Part 1 (highest value) — will this gate accept p16?

Read `.tasks/TASK_007.md`. It is the fully-specified next pattern: a TLV record
walker with a **data-dependent loop bound**, a trusted accessor, and a
`while end - p >= 3` loop. It is about to be built against the gate you are
reviewing. TASK_010 added four families of check that p16 must satisfy and that
**no existing pattern exercises**:

1. **Exactly-one-kernel-call, inside the region** (Part E structural). p16's
   driver loop has the same shape as p01/p02 — but check the rule as
   *implemented*, not as specified. What counts as "a call"? Does a call inside a
   `match`, a nested block, a `#[cfg]`-gated line, or a C macro count? What
   happens to the R1h hardened-C cell, which may wrap the call?
2. **Non-zero exclusive `Ir` + kernel's-only-caller** (Part E dynamic), read from
   callgrind. p16's kernel `break`s early on the `adversarial-overrun` input —
   TASK_007 requires that input be **exactly one window** so `k` is always 0.
   Trace what the dynamic check sees on an input where the kernel does almost no
   work. Does inlining at `-O3` in `inline` mode collapse the kernel symbol and
   make "the kernel's callers" unreadable or empty? That is the failure mode I
   most expect, and p01/p02 may pass only by accident.
3. **The twin regime**, now keyed on `external_body` + (`ensures` or `unsafe`),
   plus a whole-file and include-file `unsafe` token scan. p16's accessor takes
   **multiple `requires` clauses** (`off + len <= buf_len` and an index bound) —
   the first multi-clause trusted item on the project. TASK_010 Part D item 3 was
   supposed to make the twin deletion probe **per-conjunct** for exactly this
   case. Verify it actually is, by construction: build a two-clause trusted
   accessor that needs only one of its clauses and confirm the gate says so.
   `MAX_TWIN_JUSTIFICATIONS = 1` — does p16 need more than one trusted item? If
   it needs two, the cap blocks an honest pattern.
4. **Mandatory Miri whenever any trusted item exists**, with a 180 s budget. p16
   walks a blob. Estimate — or measure, if cheap — whether p16's inputs finish.
   p01's `large.bin` already does not. If p16 is born with blocked rows, say so
   now: the fix is an input-size decision in TASK_007, and I would rather change
   the spec than discover it at hour three of a build.

For each of the four: **PASS / WILL-BLOCK / NEEDS-SPEC-CHANGE**, with the
concrete reason. A WILL-BLOCK finding here is the most useful thing you can
return. Where the answer is a spec change to `TASK_007.md`, say exactly what to
change — I will edit it, you must not.

## Part 2 — verify the delivery, independently

Do not trust the pasted output in the commit message. Re-run and paste your own.

- The four mirrors TASK_010 claims now **fail**: `.temp/review009/x1` (macro
  bypass), `x2` (cfg divergence), `x3` (justification hatch at n=0), `hc` (C-side
  decoy). Confirm each fails, and confirm it fails **for the stated reason** — a
  mirror that now fails on an unrelated stage is not a closed bypass. Note
  `mkmir.sh` copies `common/`, so a mirror can be stale with respect to today's
  `common/`; regenerate rather than reusing a stale tree if in doubt.
- `check.py p01` and `check.py p02`, complete runs. p01 is expected
  `PASS-WITH-BLOCKED-ROWS` (Miri, `large.bin`, 180 s). p02 expected `PASS`.
  R4≡R5 must be unchanged: p02 O3 `md5_fn 0e5b59364bb6`.
- Mirror gate runs write into the tracked `results/gate/` — that leak is a known
  open issue. **Check `git status` before you finish and move any record you
  created into `.temp/review010/`.** I committed two such files by accident once.

## Part 3 — the manager's own work, which I may not clear

Per `.tasks/PROTOCOL.md` rule 3, this must be said plainly and you are the one to
attack it:

- **I designed the verified-twin mechanism** (`slb_twin_` prefix, stage `5c-twin`,
  lift-and-compare, the deletion probe) **and I wrote its `.memory/04-verus.md`
  entry.** TASK_009's engineer implemented my design; TASK_009's reviewer found
  two blockers in it. Nobody independent has asked whether the mechanism is the
  *right* mechanism.
- **I finished part of TASK_009 myself** when three resumes died to API errors.
- **I wrote `MAX_TWIN_JUSTIFICATIONS = 1` and the Part B token-scan fix** into
  TASK_010 as my own calls, flagged there as the least certain things in the file.

The question I want answered, and it is a judgement call, not a check: **is the
verified twin worth its weight?** It costs a second Verus invocation, a `--cfg`
regime, a token scan, an obligation-count pin, a per-conjunct deletion probe, and
p02 9→12 obligations. What it buys is a signal that a *trusted* precondition is
load-bearing. Under "honest mistake, not malicious author":

- Would an honest author actually ship a too-weak trusted `requires`? Is there a
  recorded instance on this project, or is the whole mechanism defending a
  hypothetical?
- Is there a materially cheaper thing that catches the same honest mistake — e.g.
  the mandatory `SLB-TRUSTED-ARGUMENT` human-read text plus Miri, without the
  twin at all?
- If your answer is "keep it", say what specifically it would catch that the
  cheap alternative would not.

**"Simplify or delete part of the gate" is a legitimate and welcome finding.**
Recommending removal of something I designed will not be treated as out of scope.
Say so if the honest answer is "keep it" — a clean negative is worth as much.

## Part 4 — clean negatives

List, by name, the attacks and concerns you tried that did **not** land. Rule 6:
this is worth as much as a finding and stops the next agent re-running them.

## Deliverable

`.tasks/TASK_010_REVIEW_REPORT.md`, plus the report format in `PROTOCOL.md`.
Severities `blocker` / `major` / `minor`, with file:line and a concrete failure
scenario. Part 1's four verdicts must appear as a table. Do not pad — three real
findings beat twenty nitpicks, and a short review that answers Part 1 well is a
complete review.

## Constraints

No root; no `/tmp` (scratch `.temp/review010/`); **no `git add`/`git commit`**; do
not edit `pilot/`, `.memory/`, `harness/`, `patterns/`, or `.tasks/TASK_007.md` —
you report, I fix. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind` — not on PATH.
`timeout <N> <cmd>`; a full gate run is ~90–120 s, plus Miri.

Save notes to `.temp/review010/NOTES.md` as you go — five agents here have died
to transient API errors mid-task, and notes make a resume cheap.

**If a prescription in this file is wrong, say so with the measurement.** Seven
agents have contradicted my written instructions and were right all seven times.
