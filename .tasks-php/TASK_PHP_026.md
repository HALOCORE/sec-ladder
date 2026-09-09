# TASK_PHP_026 — is a fix commit a CENSUS of its defect's siblings?

**Role:** research **miner** (investigation, read-only on the tree).
**One agent.** ⚠ **Dispatch only AFTER `TASK_PHP_023` has landed the catalogue**
— this task counts rows and `_023` moves it from 93 to 102.
**Report:** `.tasks-php/TASK_PHP_026_REPORT.md` — **write the FILE** (rule 10).

Read `.tasks/PROTOCOL.md`, **`.memory-php/`** (authoritative), **`PLAN_PHP.md`
§3 and §3.1** (the bar), `.tasks-php/PROTOCOL_PHP.md`,
**`.tasks-php/FIXSURVEY_001.md`** (the fix commit for every catalogued row),
`.tasks-php/UPSTREAM_001.md`, and **`.temp/mgr166/NOTES.md`** — which is the
whole reason this task exists and has the one confirmed instance.

⚠⚠ **`RECAP_PHP.md`, `.memory-php/` and `patterns-php/CATALOGUE.md` ARE NOT
YOURS TO WRITE.** This task produces a **report**, not catalogue rows.
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **No `git add` / `git commit`.** Never touch `.web/`.
⚠ Scratch under `.temp/php26/`. **Never `/tmp`.**

---

## §1 The observation, and it is n = 1

`ph16`'s `fix_commit` `99e290f882c9` was on file, and `FIXSURVEY_001.md:67-81`
already recorded that it touches **10 files** — under a heading that reads that
number as a **cost**: *"⚠ 12 fixes touch ≥ 5 files (F34's 'inside a rewrite'
shape)"*, and `UPSTREAM_001.md:64`'s *"⚠ right fix, big commit; use it, and cite
the hunk, not the commit."*

**For `ph16` the extra files are not rewrite collateral. They are the same defect
at three other sites**, and the commit introduces one macro pair to fix all four:

| # | site in pristine 5.0.0 | primitive | catalogued? |
|---|---|---|---|
| 1 | `ext/standard/streamsfuncs.c:541` | OOB **write** | ✅ `ph16` |
| 2 | `ext/standard/streamsfuncs.c:577` | OOB **read** | ❌ |
| 3 | `ext/sockets/sockets.c:536` | OOB **write** | ❌ |
| 4 | `ext/sockets/sockets.c:563` | OOB **read** | ❌ |

⚠ **`ext/sockets/sockets.c` has ZERO rows in the entire catalogue.**

> **The hypothesis: a fix commit is a CENSUS of its defect's siblings, and this
> programme has only ever read it as a source of R1h.**

## §2 What to do

**Triage first, read patches second.** The cheap discriminator is the commit
**message**: `ph16`'s is a deliberate sweep (*"possibly unsafe select(2) usage.
We avoid… by using poll(2)"*), while `ph24`'s is *"Reimplemented date and gmdate
with new timelib code"* — a rewrite, which should yield nothing.

1. **Classify all 12 multi-file fixes** (`FIXSURVEY_001.md:67-81`: `ph48` 17f ·
   `ph24` 16f · `ph16` 10f · `ph26` 9f · `ph23` 8f · `ph83` 8f · `ph39` · `ph54`
   · `ph65` · `ph73` · `ph76` · `ph84`, 5f each) as **SWEEP** / **REWRITE** /
   **UNCLEAR** **from the message alone, and WRITE THE CLASSIFICATION DOWN BEFORE
   FETCHING ANY PATCH.** That makes the triage testable instead of retrofitted.
2. **Then fetch and read all 12** (`https://github.com/php/php-src/commit/<sha>.patch`;
   ⚠ `git fetch` of a bare SHA does **not** work). For each, list every hunk that
   applies **the same repair** as the row's own hunk, and resolve each to a
   `file:line` **in pristine 5.0.0** — not in the fixed tree.
3. **Report the triage's accuracy.** How many SWEEPs yielded siblings, how many
   REWRITEs yielded none? ⚠ **If the message does not predict the patch, say so
   — that kills the cheap version of the channel and is the more useful answer.**
4. **For every sibling site found, state whether it is catalogued**, by grepping
   `patterns-php/CATALOGUE.md` for the file and the line. ⚠ **`grep -a` ALWAYS.**

## §3 ⚠⚠ What you must NOT do

1. ⚠⚠⚠ **DO NOT ADJUDICATE.** Deliver **candidates with evidence**, each with
   the C quoted and the primitive named. Whether `sockets.c:536` is an `EXACT`
   duplicate of `ph16` or a `PLAN_PHP.md` §3.1 variation is decided by the rule
   `TASK_PHP_019` wrote — **and `TASK_PHP_023` was sent to attack that rule.
   Read `_023`'s verdict before you so much as use the words.** If `_023`
   changed the rule, apply the changed one; if it refuted it without replacing
   it, **say the candidates are unadjudicable until a rule exists** and stop
   there. That is a real answer.
2. ⚠⚠ **DO NOT KILL A CANDIDATE FOR A RUST, VERUS, MIRI, LADDER OR COST REASON**
   (`CLAUDE.md` rule 6). *"Safe Rust can't express it"*, *"no cost gradient"*,
   *"a worse kernel"*, *"needs a big input"* are **findings, never kills**.
   ⚠ **`patterns-php/` is FRESH** — duplication with `patterns/` is not a filter.
3. **Do not build anything** — no new row directory under `patterns-php/`.
4. ⚠ **Do not widen past the 12** until they are done. A 2-file fix can name a
   sibling too, and if the 12 pay off, **say what a full sweep over all ~91
   resolved fixes would cost** — do not run it.

## §4 My prediction, written down so it can be refuted

I expect **4 SWEEP, 6 REWRITE, 2 UNCLEAR** from the messages; the SWEEPs to name
**5–15** sibling sites in total; and **fewer than half** of those to survive as
anything but `EXACT` duplicates of their parent row.

⚠⚠ **If the answer is "`ph16` is the only one and the channel is dead", THAT IS
A GOOD RESULT AND I WANT IT PLAINLY.** A one-instance channel dressed up as a
programme is worse than a measured negative — `RECAP_PHP.md` F7 and F13. **The
manager has been wrong about this kind of projection before** (F32, F36, and the
`ph29` doubt that was wrong in all three limbs), so **the prediction above is a
target, not a floor.**

## §5 What I am least sure of

1. ⚠⚠ **That `ext/sockets/` is in scope at all.** It is in the pristine tarball,
   so it clears `SOURCES.md`. But **check whether it was in the built
   configuration the ASan census ran against** — if it was not, that explains its
   zero rows completely and innocently, and **it is a finding about the CENSUS's
   coverage rather than about the catalogue's.** Either way the C-side bar is
   unaffected; I want to know which.
2. ⚠ **That the message triage is worth doing separately from reading the patch.**
   It costs a few minutes and buys a testable claim. **If reading the patch is so
   cheap that the triage is ceremony, say so** and I will drop it.
3. ⚠⚠ **That this channel does not just re-derive the mining wave's kills.**
   `ADJUDICATION_001.md` reversed 17 kills; some of these "uncatalogued siblings"
   may be candidates that were mined, killed and never re-adjudicated. **Check
   the mining evidence in `.tasks-php/TASK_PHP_001_MINE/` before calling a site
   new** — *"nobody has looked at this"* and *"someone looked and said no" are
   different findings, and the second one is more interesting.*
