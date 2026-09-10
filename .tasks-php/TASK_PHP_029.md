# TASK_PHP_029 — the R1h hunt for `ph73` and `ph21`, BEFORE either is built

**Role:** research **investigator**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_029_REPORT.md` — **write the FILE** (rule 10).

⚠⚠ **THIS TASK BUILDS NOTHING.** No pattern directory, no rung, no gate, no
measurement. It answers one question per row — *what is R1h?* — and stops.
**If you find yourself writing C, you have misread the task.**

Read `.tasks/PROTOCOL.md`, **`.tasks-php/PROTOCOL_PHP.md` §C in full — it is the
R1h rule and it is the authority here**, plus §F5(iii) and §G1,
`.memory-php/02-ladder.md` (authoritative; its warning that the `fix_commit`
column *"names **a** fix, not necessarily **the** fix"*), `patterns-php/SOURCES.md`
(how a `file:line` resolves against the pinned tarball),
`.tasks-php/FIXSURVEY_001.md`, and **`RECAP_PHP.md` F34/F38 — the two findings
this task exists to stop recurring.**

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **No edits under `patterns-php/` either** — including `CATALOGUE.md`. This
task **reports**; the manager lands. **Never touch `.web/`.**
⚠ **No `git add` / `git commit`.**
⚠ Scratch under `.temp/php29/`. **Never `/tmp`.**
⚠ **Another agent is building `ph29-recvfrom-alloc` right now.** Do not read or
write anything under `patterns-php/ph29*`, and do not touch `.temp/php27/`.
⚠ **`grep -a` ALWAYS** — plain `grep` dispatches to `ugrep` here and exits 1 with
no output on 41 non-UTF-8 corpus files, which reads exactly like "no match".

---

## §1 Why this task exists, and why it is cheap now and expensive later

`ph07`'s R1h took **an entire extra task and a manager bisect**, because the
answer was that the fix lived in the **caller, in another file** — invisible to
anyone searching by the defect's function name (F34/F38). `FIXSURVEY_001.md` was
written so that would be a **one-time** cost.

⚠⚠ **It is not one-time for these two rows, because for both the column is
suspect, and in different ways.** Answering it *now*, outside a build task,
means the build task starts with R1h in hand instead of stalling on it.

## §2 Row 1 — `ph73`, where the column names a fix in the WRONG FUNCTION

**This is open item 45, and it is F38's warning in its strong form.**

- `ph73` cites `Zend/zend_object_handlers.c:520-592`
  (`zend_std_call_user_call`).
- Its `fix_commit` is `3d7b0bab28e7` — *"Fixed memory allocation bugs related to
  magic object handlers"*, **3 Jun 2005, 5 files, and it DOES touch
  `zend_object_handlers.c`.**
- ⚠⚠ **But it contains ZERO occurrences of `call_user_call`.** The column names
  a commit that edits the right *file* and not the right *function*. A
  same-file verdict is exactly what `fixsurvey.py` reports for it, which is why
  a same-file verdict is a **starting point and not an answer**.
- ⚠ **`ph73` carries FIVE corpus ids** (`CRASH-052/051/027/032/100`), so it is a
  fat row and there may be **more than one** true fix. **Answer per id**, and say
  whether they agree.

⭐ **F58 already learned something about this row that you should not re-derive**:
three of `ph73`'s five `zval tmp_member` sites use the **byte-identical idiom**
and **never publish to userland** — *the idiom is not the defect, the
publication is.* **An idiom grep will hand you three false candidates.**

## §3 Row 2 — `ph21`, where the column is ELEVEN YEARS LATE

**New, found 2026-09-10 by the manager while discharging item 47.** `ph21` is in
`QUOTA_001.md` §4's standing batch, i.e. **queued to be built**, and:

```
ph21   c591f022f8ab   Sun, 10 May 2015   3 files   same-file
       "Fix bug #69403 and other int overflows"
```

**5.0.0 shipped 13 July 2004.** A 2015 fix is **not** automatically wrong — a
long-lived bug corpus is *supposed* to contain bugs that survived for years —
but *"and other int overflows"* is a **sweep**, and F58 measured that a sweep
subject is a **good positive predictor and a bad negative one**. **The specific
question: does `c591f022f8ab` remove `ph21`'s 5.0.0 defect, or does it remove a
LATER one in the same neighbourhood?** ⚠ **Only a tag comparison settles that** —
`fixsurvey.py`'s own docstring says so and it is right.

## §4 The method — and ⚠ its one real trap

For each row, and **for each corpus id on a fat row**:

1. **Pin the defect.** Resolve the `c_file_line` against the pristine tarball
   per `SOURCES.md` (`tar -xzOf … | sed -n 'a,bp'`) and paste the actual 5.0.0
   text. **Do not work from the catalogue's prose.**
2. **Read the named commit's patch.** Cached under
   `.temp/mgr/batch/patches/<sha>.patch` — `python3 .tasks-php/fixsurvey.py
   --offline` regenerates the index without network. Say **what it changes** and
   **whether the 5.0.0 text is among what it changes**.
3. **Bracket it against tags.** Find the first release whose text no longer has
   the defect. 5.0.0 → 5.1.0 → 5.2.x → 5.3.0 is the ladder `UPSTREAM_001.md` §4
   already uses. ⚠ **Report the WINDOW, not a guess** — "gone by 5.1.0, present
   in 5.0.5" is an answer; "probably 5.1" is not.
4. **State R1h** in §C's terms: the patch to backport, sha-pinned, and what it
   costs to apply to the 5.0.0 text.

⚠⚠⚠ **THE TRAP, AND IT IS THE ONE THAT MAKES THIS TASK WORTH DOING CAREFULLY.**
§C is explicit that *"cite a tagged configuration"* **lets an engineer scan tags
until one suits** — choosing the fix to fit the corpus instead of the corpus to
fit the fix. **Two drafts of a permission to do that were written and BOTH were
refused** (`_018` §4.1, `_022` §5.1). So:

> **You may report that the named `fix_commit` is not R1h. You may NOT pick a
> replacement because it is convenient.** A replacement is admissible only if an
> **upstream artefact** decides it — a later removal, a regression test, a bug
> number, a NEWS entry. **Name the artefact, or report that R1h is UNSETTLED.**

⭐ **"UNSETTLED, and here is exactly what would settle it" is a FULL PASS on this
task.** It is worth more than a confident answer, because the next agent inherits
the question instead of inheriting a wrong answer with a sha on it.

## §5 What ships

Per row (and per id where a row is fat), a short block:

```
row · corpus id · defect file:line (pasted from the tarball)
named fix_commit  -> does it touch the defect text?   YES / NO / PARTLY
first tag without the defect        -> window
R1h VERDICT       -> the named commit | a different artefact (named) | UNSETTLED
what a build task must do about it
```

Plus **one paragraph** on whether the method above is worth running over the
**31 rows whose `fix_commit` is dated 2010 or later** (the manager's list is
`.temp/mgr167/fix_dates.txt`, regenerate with `fixsurvey.py`). ⚠ **Do not run
it over all 31.** Say what it would cost per row and whether the date is
actually predictive on the two you did — **n = 2 is not a validation, and say
that too.**

## §6 ⚠ What I am least sure of

1. ⚠⚠ **That the date selector is worth anything at all.** I found it by
   sorting a column, and F58 is a standing lesson about exactly this: the
   ≥5-file selector *looked* principled and carried **no signal**. **`ph73`'s
   fix is 2005 — an ordinary date — and it is the WORST case on file.** So the
   date demonstrably does not catch everything, and it may catch nothing.
   **Your two rows are a test of it; report the test, not a promotion.**
2. ⚠ **That `ph73`'s five ids are one row.** If the hunt shows they have
   **different** fixes in different functions, that is a catalogue question and
   **§G1 applies: a shared fix is NOT evidence for SAME, and a distinct fix IS
   evidence for DIFFERENT.** ⚠⚠ **Report it; do not re-file it** — `CATALOGUE.md`
   is off-limits to this task and the manager lands catalogue moves.
3. ⚠ **That this is one task and not two.** `ph73` is fat and may eat the whole
   budget. **If it does: stop, ship `ph73`, and say `ph21` needs its own task.**
   `TASK_PHP_025` did exactly that and it was the right call.
