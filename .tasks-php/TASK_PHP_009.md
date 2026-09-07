# TASK_PHP_009 — adversarial review of `TASK_PHP_008`, and the last gate on Phase 0

**Role:** research **reviewer**. Adversarial by design.
**Under review:** `TASK_PHP_008` — the unconditional-link design, the deleted
detector, the lifted subdir ban, the demoted overlap floor, M3/M4/M5, **and the
manager decisions on top of them.**
**Report:** `.tasks-php/TASK_PHP_009_REPORT.md` — write the FILE.

⚠⚠⚠ **THIS REVIEW DECIDES WHETHER PHASE 0 CLOSES.** The manager has ruled that
Phase 0 ends here **unless you find a blocker**; majors and minors will be
carried as open items and the programme moves to building rows. **Eight tasks
have gone to infrastructure and mining with zero rows built.**
⚠ **That is a reason to be thorough, not a reason to find something** — and it
is equally not a reason to wave anything through. **If Phase 0 is sound, saying
so with evidence is the most valuable outcome available**, and a review that
manufactures a blocker to look rigorous is a failed review in the other
direction.

Read `.tasks/PROTOCOL.md`, then **`.tasks-php/TASK_PHP_008_REPORT.md`** and
`TASK_PHP_008.md`, then `TASK_PHP_007_REPORT.md`, `PLAN_PHP.md`,
`.tasks-php/PROTOCOL_PHP.md`.

⚠⚠ **`RECAP_PHP.md` IS MANAGER-ONLY — do not edit it.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**

**Bracket**: `harness/measure.py --check-stale` → `66/0`, and
`harness-php/gate.py --tool measure --check-stale` → `2/0`, first and last.
⚠ **And `TASK_PHP_008` §6 changed what that bracket MEANS** — see §4.

---

## §0 RULE 3 — the manager's own, and one of them already blew up

| the manager decided | status |
|---|---|
| **the unconditional link, and deleting the detector** | ⚠ **the headline. Attack it.** |
| **"a missing preflight record is a FAILURE"** | ⚠⚠ **already refuted** — it deadlocked the fresh-clone path, and the engineer caught it *after building what the manager asked for* (§8b) |
| lifting the subdir ban for the flat-link audit | landed |
| demoting the overlap floor to reported-only | landed |
| Phase 0 closes after this review absent a blocker | **this task** |

⚠ **`TASK_PHP_008` refuted the manager twice and reversed one of its own
demotions.** Do not assume the remaining calls are sounder than those were.

## §1 PRIMARY TARGET — is the unconditional link ACTUALLY unconditional?

The claim: *every* `patterns-php/` row carries `c/emalloc_shim.h`, so the
allocator is in both digests **by construction**, and no detection is needed.

**Attack the construction, not the detector that is gone.**

1. ⚠⚠ **Can a row exist that the audit never iterates?** It loops
   `glob(patterns-php/*)`. **A dotted row directory** (`glob` never matches a
   leading dot), a row created *while* the gate runs, a symlinked row directory,
   a row whose `c/` is a symlink. **`TASK_PHP_007` found exactly this class
   twice** (`os.path.islink` skip, the dotfile) — the same blind spots may live
   in the new code.
2. **Does the link survive the operations the project actually performs?**
   `git clone` (does git preserve it?), `git checkout` of an older commit, a
   `cp -r` of a row to make the next one, `tar`. ⚠ **A row cloned with `cp -r`
   gets a copy, not a link** — and a regular-file copy was refused by the *old*
   audit. Is it still?
3. ⚠ **Does the digest actually contain the shim's BYTES, or the link?** Check
   `results-php/gate/ph00-smoke.json` and the measurement record now that
   `ph00` carries the link, and confirm the recorded hash equals
   `sha256(common-php/emalloc_shim.h)`.
4. **`--check-stale` blindness (§6) meets the new rule.** The engineer argues the
   preflight closes the gap the digest cannot see. **Test the composition**: can
   you produce a row whose measurement record is `FRESH`, whose preflight passes,
   and whose allocator bytes differ from `common-php/emalloc_shim.h`?

## §2 The deadlock repair — the highest-risk code in the tree

`_run_is_certifying` discounts problems tagged `_COVERAGE_TAG` so the
coverage audit does not fail on its own output. **This is subtle, it was written
under time pressure at the end of a long task, and it is load-bearing.**

- **Re-run `.temp/php8/g4_selfdeadlock.py`** and confirm both arms: the naive
  rule still deadlocks (control), the shipped rule converges.
- ⚠ **Can the discount be widened by accident?** If a *substantive* problem's
  message happens to carry the coverage prefix, it is discounted. **Construct
  it.** The engineer says the tag and the filter cannot drift because both
  message producers build from `_COVERAGE_TAG` — verify that.
- **Is there a SECOND deadlock?** The same composition risk exists between the
  manifest check, the provenance check and the coverage audit. **Look for a
  cycle the engineer did not, then say whether you found one.**

## §3 The subdir audit, the overlap demotion, M3

- **`c_digest_audit`** replaced a ban with a rule over files. **Is the file
  enumeration exhaustive?** Dotfiles, symlinked directories, nested twice,
  a link whose target is outside the row, a broken link, a FIFO.
- **The overlap floor is now REPORTED, not enforced.** ⚠ Then the only thing
  standing between a citation and its kernel is `extract_sha256` and `c_file`.
  **Are those actually exact?** If they can be satisfied by a wrong kernel, the
  demotion cost something real and the manager should hear it.
- **M3's content-key collapse and `MAX_RUNS = 40`** — the engineer calls the 40 a
  guess. **Can the record still grow without bound, or lose the run a reader
  needs?** A cap that evicts the *failing* run is worse than a cap.

## §4 Phase 0's closing claims — verify them, they are what closes it

- ⚠ **Re-verify the no-touch claim BY BYTES** with `.temp/php5/snapshot.py` and
  its positive control. ⚠ `TASK_PHP_006` skipped it; `TASK_PHP_007` did it.
- **Both brackets** — and ⚠ **state in your report what `0 STALE` now means**,
  per `TASK_PHP_008` §6: *every source that was pinned still matches*, **not**
  *everything is pinned*. **Is that sentence right?** It is a `harness/`
  property affecting all 33 PAT rows and nobody has attacked it.
- **The gate chain**: `TASK_PHP_008` reports `PASS-WITH-BLOCKED-ROWS` unchanged
  and zero deterministic movement. **Spot-check the record diff yourself.**
- ⚠ **The engineer disclosed it did NOT run a shim edit end-to-end** to confirm
  it stales the measurement record — mechanism verified, end-to-end inferred
  (§9.10). **That is one command and it is the design's central claim. Run it**
  (and restore).

## §5 Rules

- **No `git add` / `git commit`.** Read-only git is fine.
- Scratch under `.temp/php9/`. **Never `/tmp`.** ⚠ `.temp/php5–8/` hold the
  previous generators — **reuse, do not delete.**
- ⚠ **You may PLANT into tracked files, but restore in a `finally:` and verify
  the restore BY BYTES.** Say so. The manager will not commit while you run.
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — exact PID via
  `/proc/<pid>/cmdline`.
- Everything claimed must have been **RUN**, output pasted.

## §6 The calls I am least sure of

1. ⚠⚠ **That the unconditional link is correct BY CONSTRUCTION and not merely
   by a shorter enumeration.** It enumerates *rows* instead of *idioms*, and
   rows are a finite observable set — **but only if the row enumeration itself
   is complete** (§1.1). **If a row can hide from `glob`, the whole argument
   collapses and we are back to whack-a-mole with a smaller board.**
2. ⚠ **That closing Phase 0 here is right.** The last three reviews each found
   blockers. **If you believe the infrastructure is still not sound enough to
   carry published numbers, say so plainly and say what it would take** — I will
   take that over a clean bill I have to retract.
3. ⚠ **That deleting the "dead code" note lost nothing.** The engineer agreed
   with me and gave a better reason than mine. **Two parties agreeing is not a
   measurement**, and the row author now has nothing telling them an
   `#include` is unreachable.

---

**Running count: launched from 23.** `TASK_PHP_008` refuted the manager twice —
the stated cost of the unconditional link (wrong in the manager's favour: the
gate half has been unconditional since `TASK_PHP_002`) and the *"three
demotions"* worry (it was two, and the one demoted on an unverified mechanism
had already been reversed on a measurement). ⚠ **It also disclosed against
itself**: the predicted net deletion did not happen (+90 lines, with AST
accounting), and it nearly published a **fourth** answer to a quantity
`RECAP_PHP.md` warns has three. **Reconciliation is the manager's job.**
