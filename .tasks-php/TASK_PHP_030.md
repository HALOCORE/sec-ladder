# TASK_PHP_030 — the PRE-IMAGE SCREEN: mechanically exclude `fix_commit`s that cannot be the 5.0.0 repair

**Role:** research **investigator**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_030_REPORT.md` — **write the FILE** (rule 10).

⚠⚠ **THIS TASK BUILDS NOTHING.** No pattern directory, no rung, no gate, no
measurement, no C kernel. It writes **one screening tool** and reports what it
finds. **If you are writing a `kernel.c`, you have misread the task.**

Read `.tasks/PROTOCOL.md`, **`.tasks-php/PROTOCOL_PHP.md` §C in full** (the R1h
rule) plus **§H** (this task ships a validator, so §H binds it), **and
`.tasks-php/TASK_PHP_029_REPORT.md` in full — it is the origin of this task and
it contains your ground truth**. Then `patterns-php/SOURCES.md` (how a
`file:line` resolves against the pinned tarball), `.tasks-php/FIXSURVEY_001.md`,
and `RECAP_PHP.md` F34/F38.

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **No edits under `patterns-php/` either, including `CATALOGUE.md`.** You
report; the manager lands. **Never touch `.web/`.**
⚠ **No `git add` / `git commit`.**
⚠ Scratch under `.temp/php30/`. **Never `/tmp`.**
⚠ **Another agent may still be building `ph29-recvfrom-alloc`.** Do not read or
write anything under `patterns-php/ph29*` or `.temp/php27/`.
⚠ **`grep -a` ALWAYS** — plain `grep` dispatches to `ugrep` here and exits 1 with
**no output** on 41 non-UTF-8 corpus files, which reads exactly like "no match".

---

## §1 The idea, and why it is stronger than what it replaces

`TASK_PHP_029` refuted `ph21`'s `fix_commit` **from the commit's own bytes**:

```
pristine 5.0.0  ext/standard/string.c   result_len = Z_STRLEN_PP(input_str) * Z_LVAL_PP(mult);
                                        result = (char *)emalloc(result_len + 1);

c591f022f8ab (2015) PRE-IMAGE           result_len = input_len * mult;
                                        result = (char *)safe_emalloc(input_len, mult, 1);
```

The 2015 commit's **pre-image** is already the post-5.2.0 form, so **it cannot be
repairing the 5.0.0 line**. Generalised:

> **THE SCREEN.** If a `fix_commit`'s patch **touches the defect's file** but its
> **pre-image** for that file does **not** contain the 5.0.0 text at the cited
> site, that commit is **not** the repair of that site.

⭐ **This is a PROOF OF EXCLUSION and that is what makes it worth a task.** The
two selectors on file — the fix **date** (31 rows) and **id-spread** (30 rows) —
only *rank*; `_029` measured them as nearly orthogonal (overlap 10) and
recommended **neither as a sweep**. A decisive negative test makes both largely
redundant. **Network-free: every patch is already cached under
`.temp/mgr/batch/patches/`.**

## §2 What to run it over

**All 169 resolved records**, not 102 rows. `python3 .tasks-php/fixsurvey.py
--offline` regenerates `.temp/mgr/batch/fixsurvey.json`; each record carries
`row`, `id`, `sha`, `defect_file`. ⚠ **The per-id walk is new as of today** —
before it, 68 of those 169 were never examined at all.

Resolve the 5.0.0 text per `SOURCES.md` (`tar -xzOf <tarball> php-5.0.0/<path> |
sed -n 'a,bp'`), tarball sha256 `5783e0c0…d6919`.

## §3 ⚠⚠ The traps, and the first one will bite you

1. ⚠⚠⚠ **MATCH TEXT, NEVER LINE NUMBERS.** Between 5.0.0 and a 2016 commit the
   same function has moved thousands of lines. `@@ -4949` in `c591f022f8ab` is
   **not** `ph21`'s `:4120`. **A screen keyed on line numbers will produce a
   confident, uniformly wrong answer.**
2. ⚠⚠ **"Pre-image" means context (` `) AND removed (`-`) lines, and ONLY within
   hunks whose `diff --git` names the defect's file.** Getting this wrong in the
   permissive direction makes everything look like a match.
3. ⚠ **Normalise whitespace before comparing, and say how.** PHP's tree mixes
   tabs and spaces and the indentation of a line changes when its enclosing
   block does. **But do not normalise so hard that different code compares
   equal** — state the normalisation and show one case it changes.
4. ⚠⚠ **A non-match is only decisive IF THE PATCH TOUCHES THE FILE.** If the fix
   is in another file entirely (the `ph07` shape — **19 records**, up from 8
   today) the screen must return **INAPPLICABLE**, not "not the repair".
   **Three outcomes, not two.**
5. ⚠ **`c_file_line` may name the FAULT site, not the MECHANISM.** `ph63` is the
   standing example (F1): the corpus names `array.c:1062` while the mechanism is
   `zend_hash.h:88`. **So a non-match may mean the screen looked in the right
   file at the wrong concept.** Report per-record, and do not aggregate a verdict
   you cannot defend per row.
6. ⚠ **A probe whose SETUP encodes the answer evaluates fine and is wrong** —
   **seven** shapes now (F52/F54, and two more in `.temp/mgr167/NOTES.md` §3c
   from the manager, today). **A screen is exposed to this**: choose the
   comparison so that a *no-op* implementation cannot pass §4's must-fire.

## §4 ⚠⚠⚠ §H — AND YOU HAVE GROUND TRUTH IN BOTH DIRECTIONS, WHICH IS RARE

**The screen is a validator. It ships with must-fire and must-NOT-fire cases,
run, output pasted.** Use these known answers — **do not invent new ones**:

| record | established by | the screen MUST say |
|---|---|---|
| `ph21` / CRASH-107 / `c591f022f8ab` | `_029`, and the manager re-checked the bytes | **NOT THE REPAIR** |
| `ph73` / CRASH-052 / `3d7b0bab28e7` | `_029`: exact fix, regression test in-commit | **CANDIDATE** |
| `ph73` / CRASH-051 / `235e6c0afe1d` | `_029`: bug #30562, 5.0.3→5.0.4 | **CANDIDATE** |
| `ph07` / CRASH-124 / `cb3cca21b345` | the fix is in the **caller, another file** | **INAPPLICABLE** |

⚠⚠ **IF YOUR SCREEN CANNOT REPRODUCE ALL FOUR, IT IS WRONG AND THE FINDING IS
THAT IT IS WRONG.** Say so and stop; a screen that gets `ph21` right by accident
while failing `ph07` is worse than none, because it will be trusted.

## §5 `ph95` — a row that owes this specifically

**Roll in what `_029`'s scope missed.** `ph95` has **THREE** candidate fixes and
no confirmed R1h:

- `6d98fc38b53` (2004) — repairs `:262`
- `db420cb6a14` (2019, bug #78833) — adds `if (currentarg > INT_MAX - arg)` before `:212`
- `865739e5b196` (2025) — what the **corpus column** names, and it is **neither**

⚠ Its catalogue block already says of the first two: *"neither repairs the
other."* **Run the screen on all three and report which survive.** ⚠⚠ **Do NOT
pick one because it is convenient** — §C's trap, refused twice in this programme
(`_018` §4.1, `_022` §5.1). **Name an upstream artefact or report UNSETTLED.**
⭐ **"UNSETTLED, and here is exactly what would settle it" is a FULL PASS.**

## §6 What ships

1. **The tool**, under `.temp/php30/`, with a `--selftest` carrying §4's four
   cases. ⚠ **If it is worth keeping, say so and the manager will promote it to
   `.tasks-php/`** — do not put it there yourself.
2. **A table of every record the screen calls NOT-THE-REPAIR**, with the 5.0.0
   text and the pre-image text side by side for each. **That table is the
   deliverable**; the counts are not.
3. **A count of INAPPLICABLE**, and whether it matches the 19 OTHER-FILE records
   the survey reports. ⚠ **If those two numbers disagree, that is a finding** —
   investigate before explaining it away.
4. **One paragraph** on whether the screen should run in `fixsurvey.py` on every
   run, or stay a separate tool. ⚠ **Argue the cost**: `fixsurvey.py` is run by
   agents mid-task and must stay fast.

## §7 ⚠ What I am least sure of

1. ⚠⚠ **That the screen is decisive as often as I think.** `ph21` is one clean
   case. It may turn out that most records are INAPPLICABLE or ambiguous, and
   **that is a perfectly good result** — it would say the R1h question genuinely
   has to be answered per row, which is `_029`'s recommendation and would confirm
   it. **Do not tune the screen until it produces a satisfying number.**
2. ⚠ **That "the 5.0.0 text" is well-defined.** For a one-line defect it is; for
   `ph73`-shaped rows citing a 70-line span it is not. **Say what you compared,
   per record, and flag the spans where you had to choose.**
3. ⚠ **That this does not simply re-derive the date selector.** If every
   NOT-THE-REPAIR record is also a late-dated one, the screen adds rigour but no
   coverage. **Cross-tab it against the 31 date-flagged and 30 id-spread rows and
   say so plainly** — `.temp/mgr167/fix_dates.txt` has the dates, and
   `fixsurvey.py` now prints the id-spread section.
