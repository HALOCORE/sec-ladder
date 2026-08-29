# TASK_135 — adjudicate the PROVISIONAL debt: which markers stand, which are stale

**Role: research reviewer.** ⚠⚠ **This is a task the manager cannot do itself.**
PROTOCOL rule 3 — *never clear your own design or your own objection* — and most
of these markers are the manager's, on reviews the manager commissioned. **The
manager has TRIAGED them below and must not be the one to clear them.**

Read first: `.tasks/PROTOCOL.md` (rules 3 and 9 especially), `RECAP.md`'s
findings section at the line numbers given, and each named task's `_REPORT.md`.

## What a PROVISIONAL marker means here, and why stale ones are expensive

Rule 9: a finding is not authoritative until a **different** agent has attacked
it. A `PROVISIONAL` marker is the project's promissory note that this has not
happened. ⚠⚠ **The debt being CLEAR is true of TASKS and false of FINDINGS —
`TASK_113` closed the task-level debt, and the finding-level markers survived
it. That distinction is load-bearing and has already confused one session.**

⚠ **A stale marker is not harmless.** It spends a reader's trust on the wrong
claims and hides the live ones among them. **But clearing one that should stand
is much worse**, so the default on doubt is STANDS.

## The manager's triage — VERIFY IT, do not inherit it

Nine finding-level sites. ⚠ **`RECAP`'s box says *"clear the 12 PROVISIONALs"*
and the manager could only locate NINE at finding level (plus three in box and
rules prose). ✅ **Re-derive the count yourself; `grep -n PROVISIONAL RECAP.md`
is the whole command.** If it is twelve, the manager missed three and they are
the interesting ones.

| # | RECAP line | rests on | manager's triage — **attack this** |
|---|---|---|---|
| 1 | ~1588 | `TASK_088` | **LIVE.** `p19`'s re-fitted laws, two-cause decomposition, CVE correction, harness changes. Never reviewed. |
| 2 | ~1704 | `TASK_092` | **LIVE.** `p46`'s headline ground moved: `r4_mutreslice`'s exclusion reason was refuted (the `std_specs/` confusion, second instance) and its full R5 verifies `21 verified, 0 errors`. |
| 3 | ~1883 | `TASK_106` | ⚠⚠ **THE MANAGER BELIEVES THIS IS STALE.** The marker says *"`TASK_106`, which is unreviewed"*. **`.tasks/TASK_117.md`'s own title is *"review `TASK_106`"*** and RECAP's very next paragraph says the headline was corrected by `TASK_117`, manager-re-measured. ✅ **Verified to that extent and no further — whether the review was ADEQUATE is your call, not the manager's.** |
| 4 | ~2108 | `TASK_118` | **LIVE, NARROW.** The *conclusion* (encoding 3 fails) is manager-verified; the *rule* about unforgeable ledgers is `TASK_118`'s reading and is unreviewed. Only the rule is in debt. |
| 5 | ~2139 | `TASK_116` | ⚠⚠ **STANDS BY INSTRUCTION — `TASK_116` says explicitly: do NOT clear them.** Do not clear it because it looks tidy. If you think that instruction is wrong, say so and give the reason; do not act on it. |
| 6 | ~2422 | finding 41 | **PROBABLY NOT DEBT.** The marker is historical: finding 41 was published PROVISIONAL *so it could be attacked*, `TASK_122` attacked it, and it **died**. A marker on a retracted claim is narrative, not a promissory note. ⚠ **Check that the retraction is complete before agreeing.** |
| 7 | ~3772 | `TASK_111` | **LIVE.** The correction-reflex-becomes-bias finding; that review is itself unreviewed. ⚠ **This is the one whose subject is the project rather than a pattern, so a reviewer has the least to measure against — say so if it is unfalsifiable as stated.** |
| 8 | ~4265 | `p17` §10b | **LIVE.** The re-fitted band in `patterns/p17-http-range/NOTES.md` §10b, awaiting review per rule 9. ✅ No published `p17` number depends on it. |
| 9 | ~4490 | three claims | **LIVE ×3, and one is checkable in one command**: `R5 − R4 = 0.00` on all 40 rows; `R3 − R4` NEGATIVE on 5 of 20 patterns. ⚠ **`R3 − R4 < 0` on a quarter of the tree contradicts a sentence this project says often** — if it holds, it is a result, not a footnote. |

## Deliverables

1. **Per site: `STANDS` / `STALE — the named ground is gone` / `CLEARED — attacked and survives` / `RETRACT`.** With the evidence. ⚠ **`STALE` and `CLEARED` are different**: the first says the marker's *stated reason* evaporated, the second says you *did the review*. **Do not report the first as the second.**
2. ⚠⚠ **You may CLEAR a marker only by actually attacking the claim.** For sites you cannot attack in this task, say `STANDS — not attacked here` and estimate the cost. **A marker removed because a task report exists is not a review; that is exactly the `TASK_113` gap this project already has open.**
3. **The count**: is it nine or twelve? Name any the manager missed.
4. ⚠ **Site 9's `R3 − R4 < 0` on 5 of 20** — check it against the committed records and say whether the project's prose is consistent with it.

## Rules

- `.temp/t135/` only. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`** — the manager applies those. No `git add`/`git commit`.
- **Do not run `harness/check.py` or `harness/measure.py`** — two concurrent
  agents are running. **Read the committed records** (`results/gate/*.json`,
  `results/measure/`) rather than re-running anything; site 9 is a record read,
  not a sweep. ⚠ **`harness/measure.py --check-stale` is READ-ONLY and allowed.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- ⚠ **Read `blocked` out of the RECORD, never `grep` the log** — `grep -c BLOCKED`
  matches the verdict string `PASS-WITH-BLOCKED-ROWS` and decodes as `2N+1`.
- Report to `.tasks/TASK_135_REPORT.md`. **PROTOCOL rule 2: you carry 634.**
  Close with your branch delta and the sum. ⚠ **Two concurrent branches also
  carry 634; reconciliation is the manager's, not yours.**
