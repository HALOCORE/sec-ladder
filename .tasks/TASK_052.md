# TASK_052 — p18's corrections, and the gate hole the review demonstrated

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_051_REVIEW_REPORT.md`
in full — it is your whole task** — then `.tasks/TASK_051.md` and
`.tasks/TASK_051_REPORT.md`, then `.memory/03-measurement.md`'s **null-control
section (already corrected by the manager from M1 — read it, do not re-derive
it)** and its hold-out rank rule, `.memory/02-bench-rules.md`'s **threat model
and rule 5**, and `.memory/01-ladder.md`'s direction-test block.

**Read the good news first.** **15 clean negatives**, several of them load-bearing:
band `y` was verified independently (7479.0000 measured against 7479.01
registered, genuinely 4× outside the hull); §0's 24 probe values reproduce across
three builds with `unbnd == guard`; **`R1h − R1 = 2·bytes` is exact, re-derived
from the reviewer's own listing, and survives the blocker**; `c_mask`'s identical
cost + identical wrong answer + silent sanitizer holds; `adversarial-sat`'s "no
fold can see it" is *literally* true (identical observable state); TCB = 3 with no
`assume`; R4/R5 kernels byte-identical. **And your own instinct to report the
leave-one-band-out as failed was right** — it just needs a different repair than
the one you shipped.

⚠ **Three of the manager's claims were wrong and are already corrected in
`RECAP.md` and `.memory/`** — the "Miri and a proof are blind" sentence, the
"0x20" offset, and "R4's advantage over R2 vanishes". **Do not restate any of
them.**

---

# Part A — p18

## The blocker: every published level law has an unstated domain

All 34 fit blobs and all three band-`y` blobs satisfy **`term == nv`**, and no
law says so. `degenerate.bin` — **a committed matrix input** — has
`term = 4 < nv = 5` and misses by **+2.00** (four cells) and **+8.00**
(`safe_tuned`) against a quoted max residual of **0.029**; and
**`R3 − R4 = +1·b − 6·v + 7` predicts −5.00 where the reviewer measures +1.00 —
the wrong sign.** The negative control `truncating.bin` (`term == nv`) is
predicted exactly, so the domain boundary is the explanation.

- **State the domain on every level law**, in `NOTES.md`, `README.md` and
  `spec.md`'s prose.
- **Build a `term < nv` band** and either derive the corrected law or state that
  it does not fit one and why. This is the same *class* of defect p14 had — a law
  fitted inside one regime — on a different axis, so **cite p14 and
  `.memory/02-bench-rules.md`** rather than presenting it as new.
- ⚠ **`degenerate.bin` is in the matrix, so a reader meets the counterexample
  before they meet the caveat.** Fix the ordering, not just the text.

## M4 — the pre-registration is tamper-evidence, not pre-registration

Re-running `predict.py register` **today** reproduces `ca0bbe26…`
byte-identically. A hash that anyone can recompute at any time proves the file
was not *altered*; it does **not** prove the predictions predate the
measurement. **Restate it as what it is.**

⚠ **And say what would make it real**, because this is now the third consecutive
pattern with no valid out-of-sample test (p13, p14, p18) and whatever you write
here will become the project's standard. Candidates worth pricing: registering
the hash in a **commit that precedes the measurement commit** (git gives the
ordering for free, and the manager commits at task boundaries — so this costs
one extra commit and nothing else); or generating the held-out band from a seed
committed earlier. **Recommend one and say why.**

## M5 — the "3 columns" caveat is wrong

The proposed rule (*a 3-column design makes every leave-one-band-out unable to
fail*) is **not** the mechanism: **band `x` alone is rank 3**, which is why
dropping any other band changes nothing. p06 is **rank 5/5** and its hold-out
*does* fail. Correct the wording in `NOTES.md`; the manager will lift the
corrected form into `.memory/`.

## M2 and M3 — two controls that do not say what they claim

- **`NOTES.md:958-959` quotes a command whose output is the opposite of the
  claim.** `wrapping_shl` verifying **is** true (the reviewer's probe: 2/0) —
  but **no committed generator produces that probe**, so the tree cannot
  reproduce a published fact. Commit the generator and fix the quoted command.
- **`m_noguard_ms` keeps all six functional loop invariants** — precisely the
  defect for which `m_wshl_ms` is withdrawn **twelve lines below it**. Withdraw
  it on the same grounds, or explain the asymmetry. **p17's control-2 lesson,
  now its fourth instance on this project.**

## The minors

- `README.md:20` ships **`shift +=32 7`** — pseudocode notation leaked into
  prose.
- Work through the review's remaining minors and its 15 clean negatives for any
  *wording* that needs to move even where the conclusion held.
- ⚠ **Record the process observation the reviewer could not check:** your claim
  that no `required`/`forbidden` entry moved during item 7's `why` correction is
  **not independently verifiable**, because p18 landed in a single commit with no
  pre-edit snapshot. Say so in `NOTES.md`. (This is a fact about commit
  granularity, not about your honesty — and it is the manager's problem to fix,
  not yours.)

---

# Part B — the gate hole, and this is the manager relaxing a standing constraint

**`check.py:4602-4620` never compares exit code or stdout when
`expected_exit != 0`.** The reviewer demonstrated it with a real Miri run
(rc=101, no UB) being reported as *"ok … matches the model"*, and it is
**reachable on p01 and p02 today**.

**It passes the threat model** (`.memory/02-bench-rules.md`): *could this happen
by accident?* — **yes.** A rung that panics for the *wrong reason*, exits with a
*different* nonzero code, or prints garbage before dying, currently passes an
adversarial row silently. That is an honest-mistake failure, not an adversarial
one, which is the standard this project set for gate work.

**So: you may edit `harness/check.py` for this one defect.** Conditions, all
binding:

1. **This defect only.** No refactoring, no adjacent improvements, nothing else
   in `harness/` or `common/`. If you find a second hole, **report it**.
2. **Commit the reviewer's reproduction as a regression check** — a mutant or
   fixture that fails the fixed gate and passed the old one, under
   `patterns/p18-varint-shift/controls/` or wherever the project already keeps
   such things. A fix with no reproduction is not done.
3. ⚠ **`check.py` is hashed into every gate record, so this makes all 16
   patterns STALE.** Re-run **every** pattern's gate and confirm
   `measure.py --check-stale` is clean at the end. Expect ~30 minutes; run them
   in the foreground.
4. **If any pattern's gate now FAILS, stop and report it before changing
   anything.** A newly-failing row is a finding — it means that pattern's
   adversarial expectation was never actually checked — and it is the manager's
   call what to do about it, not yours.

## Done when

Part A's items land and Part B's fix + reproduction land; `check.py p18` green on
a complete run; **all 16 patterns' gates re-run and `--check-stale` clean**;
tables regenerated; `contract_sha256` moves if you touch the hashed block. Every
figure that moved is restated everywhere it appears.

## Constraints

No root; no `/tmp` (scratch `.temp/p52/`, **per-PID paths**); **no
`git add`/`git commit`**; do not edit `pilot/` or `.memory/`. **Patterns you may
edit: p18 only.** **`harness/check.py`: the Part B defect only.** `common/`:
not at all. Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`,
valgrind `~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on
PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; no
self-matching `pgrep` wait-loops. **Measurements in the FOREGROUND, interleaved
by cell.** ⚠ `check.py` rewrites gate JSONs — with Part B you will be rewriting
all 16, so know which changes are the fix and which are ASLR noise.

⚠ **`.temp/p18/` contains an earlier task's files** (Aug 18). The reviewer's
scratch is `.temp/r51/` with `marg.py` (an independent reimplementation of the
differenced-marginal protocol), the p01/p16 `O3d` builds, the Miri gate-hole
mutant and `rebuild.sh` — **reuse rather than rebuild.**

Notes to `.temp/p52/NOTES.md`.

**If a prescription here is wrong, say so with the measurement.** Seventy-nine
agents have contradicted the manager and all seventy-nine were right — this
review refuted three manager claims that were live in `RECAP.md` and `.memory/`
at the time it ran, including one the manager had written **two commits
earlier**.

**What I am least sure of is Part B's condition 4.** I am assuming a
newly-failing gate row would be a genuine finding. It might instead be that
several patterns' adversarial rows have *deliberately* loose expectations that
the old code silently permitted, in which case tightening the comparison
produces a pile of false failures and the right fix is narrower — compare exit
code but not stdout, say. **If that is what you find, stop at the measurement and
tell me what the distribution of failures looks like before repairing anything.**
