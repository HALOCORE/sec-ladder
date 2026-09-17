# TASK_PHP_064 — **PROMOTE THE 14 FILES THAT 13 PUBLISHED FINDINGS REST ON.** ⭐ `PROMOTE_001`'s method, at 2.3× its scope — and this one is NUMBERED, which `PROMOTE_001` was not

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_064_REPORT.md` — **write the FILE**
(`PROTOCOL.md` rule 10). A report that exists only in your final message does
not exist.

⛔⛔ **YOU MAY NOT RUN `git add` OR `git commit`** (`CLAUDE.md` Don't #4). The
manager commits at task boundaries. Read-only git is fine and you will need it.

⛔ **DO NOT EDIT** `RECAP_PHP.md`, `.memory-php/`, `harness/`, `common/`,
`patterns/`, `results/`, `pilot/`, `common-php/`, or anything under
`patterns-php/*/` (a re-gate). Your whole working surface is `.tasks-php/`.

---

## §0 ⛔ READ THIS BEFORE PLANNING YOUR TIME

### 0.1 Why this task exists

`.memory-php/04-process.md` **law 11**: *a published finding whose only evidence
is a gitignored probe will not survive a clean checkout.* Open item 148
adjudicated every law-11 citation in the tree by unit text; the ruling is
`F150`, and it lives in `scratchdeps.ADJUDICATION` — a table keyed on
`(finding, cited file)`, each row carrying its reason.

▶ **17 citations over 14 files and 13 findings are ruled `RESTS`** — the
published number IS the gitignored file's output. **This task promotes them.**

⛔⛔ **AND THE SEVERITY IS NOT THE COUNT.** Of the 13 findings, **only `F89` and
`F95` have ever been reviewed**, and `F89`'s reviewer reproduced the *contrast*
by a different design while its two published figures still rest on the probe
alone. ▶ **For 11 of 13 there is no second method anywhere in the tree.**

⚠ **Nothing has been lost yet** — every target resolves today. This buys
durability, not recovery. But `CLAUDE.md` constraint 6 **mandates** deleting
`.temp/` once gates are green, so the expiry is scheduled, not hypothetical.

### 0.2 ⛔ GET THE LIST FROM THE TOOL, NOT FROM THIS FILE

```
python3 .tasks-php/probes/scratchdeps.py      # the `RESTS` block is your worklist
```

⚠⚠ **A count in a task file is a premise you have no reason to doubt, and this
programme has published three of them wrong** (`F4`'s *"123 ASan reports"*, the
`why`-size *"7,000 words"*, `F147`(c′)'s wrong finding range — **that last one
was my brief to `PROMOTE_001`, and its engineer caught it**). ▶ **If the tool
and this file disagree, the tool is right and I want that in your report.**

### 0.3 The three things `PROMOTE_001` established, which you inherit

1. ⭐ **A promotion is not a copy.** I told its engineer to copy `width.py`'s
   header as the precedent; the header claimed a guard *"does not fail"* and it
   did. **The engineer refused, checked the behaviour against the claim, and
   made its own guards return 0.** That refusal is the reason the promoted
   probes do not carry the defect. ▶ **Do the same to me.**
2. ⭐ **`NULLCTL_001.md` is the model for an evidence document** — a promoted
   `NOTES.md` with a header saying what it measured, when, and what is owed.
3. ⛔ **Two of the five probes it promoted CRASHED without their cache.** A
   probe that cannot run on a clean checkout is half-promoted. **Item 149 just
   settled what such a check returns: it REPORTS AND RETURNS 0, and says
   `NOT RUN -- NOT A PASS` in capitals.** `.tasks-php/width.py`'s `X3`/`X3d` is
   the worked example; `probes/inclusive_ir.py`'s `report_not_run` is the other.

---

## §1 THE WORK, IN THE ORDER I WANT IT DONE

⛔ **Order matters and it is not alphabetical.** Stop and report at any point;
a partial promotion in this order is worth more than a complete one in another.

### 1.1 ⛔⛔ FIRST: `F85` and `F74` — they share a file and `F85` is the biggest claim in the programme

`F85` is *"the programme's central claim"* (**29 of 38 sign flips are
cross-language**) and it is **UNREVIEWED**. Both of its named evidence sources
are in scratch:

* `.temp/mgr170/callee_share.py` — ⚠ **also `F74`'s**, so the two discharge
  together;
* `.temp/mgr172/STATISTIC-DECISION-DRAFT.md` — cited **by section** (`§5`). An
  **evidence document**, not an artefact: `NULLCTL_001.md`'s treatment applies.

`F74` additionally names `.temp/mgr170/spread_stat.py`.

⭐⭐ **NOTE WHAT THIS TELLS YOU BEFORE YOU START.** `F74` names **three** probes
— `spread_stat.py`, `callee_share.py`, `null_control.py` — and **`null_control.py`
is already promoted.** A sibling promotion took one of three and nobody noticed
for five days. ▶ **When you promote a file, check its siblings in the same
citing sentence**, and say in your report whether that rule would have caught
anything else here.

### 1.2 THEN, in this order

| # | file | findings | why here |
|---|---|---|---|
| 2 | `.temp/mgr173/ph64_draws.py` | `F89` **+** `F90` | one file, two findings, `--selftest` PASS with **5 negatives** that go with it |
| 3 | `.temp/mgr169/charlit_reach.py` | `F73` | the headline **`0 of 33 PAT and 0 of 6 PHP`** is its output; **6 must-fire negatives** and a DIFFERENTIAL design are why it is believable |
| 4 | `.temp/mgr168/item48_decide.py` | `F70` (section), **`F69` rests on it** | the measurement that **decided item 48** — `29 of 30` at `file:line`, `24 of 30` by enclosing function |
| 5 | `.temp/mgr166/asan_reach.c` **+** `.temp/mgr165/REFETCH.sh` | `F50` | the bytes × ASan × canary table and *"the cliff is at 32 bytes, not near 384"*. `REFETCH.sh` is the **named regenerator** for all of `F50`'s evidence |
| 6 | `.temp/mgr169/ph29_predict.py` | `F72` | the **six published prediction numbers** are its output |
| 7 | `.temp/php43/item83_sim.py` | `F100` | *"all six published A1 percentages re-derive to the digit"*, driving the row's **own** verdict functions |
| 8 | `.temp/php43/samefunc_hole.py` | `F95` | ⭐ **the REVIEWER's own counterexample.** `law 12`: the reviewer's INDEPENDENCE is the product, and this is the only copy |
| 9 | `.temp/php19/entcount.py` | `F53` | *"run at nine PHP-5.0 commits"* — the whole evidence that `ph32`'s stated R1h is wrong for two of three tables |
| 10 | `.temp/mgr165/count_ent.py` | `F44` | the four-table result `63/65 · 22/23 · 66/67 · 410/411`. ⚠ **`nm -S` corroborates**, so the loss here is the INDEPENDENT method |
| 11 | `.temp/mgr176/asanfill.c` | `F102` | 14 lines, and the **measured result changes the row** (a clean stack slot is `IS_NULL`) |

⚠ **`count_ent.py` is cited FOUR times and only ONE is a defect.** Under `F50`,
`F51` and `F52` it is ruled `HISTORY` — the subject of a sentence about a defect
class, not evidence. ▶ **Read `ADJUDICATION`'s reason line before you touch a
file**; the verdict is the sentence, not the bucket.

---

## §2 WHAT "PROMOTED" MEANS HERE

For each file:

1. **Land it under `.tasks-php/probes/`** (scripts) or `.tasks-php/` (evidence
   documents, `NULLCTL_001.md`-style).
2. **Give it a header** stating: what it measured · **when, as an event with a
   commit** · which finding(s) it backs · **what is still owed**. ⛔ Do not
   write a claim you have not checked — see §0.3.1.
3. **Run it.** If it needs a cache that is gone, apply item 149's rule:
   report, return 0, say `NOT RUN -- NOT A PASS`. ⛔ **Do not fabricate the
   cache and do not commit an artefact to satisfy a probe** — a callgrind
   profile or a `.bin` under `.temp/` is `CLAUDE.md` Don't #1 being **obeyed**.
4. **Register it** in `.tasks-php/checkers.py` with its filed `argv` and
   `expect`. ⚠ **`citecheck.py` is filed `expect=1`** and carries a standing
   rot; do not copy that without understanding it.
5. **Repoint the citation.** The finding's text is `RECAP_PHP.md`, which you
   **may not edit** — ▶ **list the exact line numbers and replacement strings in
   your report** and I will land them.

⭐ **Free**: `.tasks-php/*.py` is in no digest, so none of this costs a re-gate.

---

## §3 ⛔ THE ONE THING THAT WILL GO WRONG, AND HOW TO TELL

**`scratchdeps.py`'s `N20` asserts that every law-11 citation has a ruling.**
Promotions move citations from `LIVE` to `PROMOTED`, which is the point — but
**if you write a new `.temp/` path into a finding section, `N20` goes red.** It
already caught its own author once, on the four citations `F150`/`F151`
introduced. ▶ **If `N20` fires, that is the arm working. Read what it names.**

⚠⚠ **AND THE CENSUS READS `git ls-files`, so a promotion becomes visible when
the manager COMMITS, not when you write** (`F147`). Your run will still show the
file as `LIVE` until then. **Do not chase that.**

---

## §4 WHAT I WANT IN THE REPORT

1. **Per file**: promoted / partially promoted / refused, and **why**.
2. ⭐ **Every place this brief is wrong.** `PROMOTE_001`'s §4 carried five
   findings against my brief and one of them corrected a published finding
   range. **That section is the most valuable thing it produced.**
3. **The sibling rule from §1.1** — would it have caught anything beyond
   `null_control.py`?
4. **Anything you had to leave** — a probe whose cache is gone, a claim you
   could not verify. ⛔ **Say it plainly; do not round it off.**

---

## §5 ⓘ ON THIS TASK HAVING A NUMBER

`PROMOTE_001` was dispatched **without one**, so `task_cost.py` — keyed on
`TASK_PHP_NNN` — prices a real task at **zero**, and every ledger figure is
computed without it (open item **150**, `F142`'s defect in a new spelling).

⚠ **Numbering this one is an INTERIM CHOICE, NOT A RULING.** Item 150 routes the
policy question — *should a dispatched chore be numbered, or should the ledger
learn a second namespace?* — **to a reviewer**, because it prices the manager's
own work and `_057`'s engineer refused exactly that. ▶ **The reviewer's question
stands.** What I will not do is make the defect `n = 2` while it is open.

ⓘ **`PROMOTE_001` is NOT retro-numbered** — moving a denominator under a
published range is `F126`'s defect.
