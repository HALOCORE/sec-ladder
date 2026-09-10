# TASK_PHP_031 — settle `ph64`'s R1h, and prepare the FIRST TEMPORAL ROW

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_031_REPORT.md` — **write the FILE** (rule 10).
**Model your report on `.tasks-php/TASK_PHP_029_REPORT.md`** — the R1h hunt that
worked, and the template for *"R1h stated with the artefact that decides it."*

⚠⚠ **THIS IS A HUNT AND A PREP TASK, NOT A BUILD.** Do **not** create
`patterns-php/ph64-<slug>/`. Do **not** run a gate on a new row. What you deliver is
an **answer** and a **build brief**, so that the build task after this one does
not stall the way `TASK_PHP_015` did.

Read `.tasks/PROTOCOL.md`, `.tasks-php/PROTOCOL_PHP.md` (**§C is the rule that
binds this task**, plus §F5), `.memory-php/00-corpus.md`, `.memory-php/01-extraction.md`,
`CATALOGUE.md`'s `ph64` rows (Part A `:170`, Part B `:795`), and
`patterns-php/SOURCES.md` §2 for the read recipe.

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **No `git add` / `git commit`.** Never touch `.web/`.
⚠ Scratch under `.temp/php31/`. **Never `/tmp`.**
⚠ **`grep -a` ALWAYS** — plain `grep` here dispatches to `ugrep` and exits 1
with no output on 41 of the 1170 corpus `.c`/`.h` files, which is
indistinguishable from *"not present"* (F35).

⚠⚠⚠ **ANOTHER TASK IS RUNNING CONCURRENTLY AND IT IS RE-GATING ROWS.**
`TASK_PHP_028` is discharging the spellings debt on `ph16`/`ph29`/`ph03`, so
`patterns-php/ph16*`, `ph29*` and `ph03*` are **being written while you work**.
Therefore, and unusually for this programme:

- ⚠⚠ **DO NOT run the staleness brackets** (`harness/measure.py --check-stale`,
  `harness-php/gate.py --tool measure --check-stale`). Every other php task
  file mandates them twice; **this one forbids them**, because a reading taken
  mid-re-gate is meaningless and would look exactly like real damage.
  **This is a hunt — it changes no measured artefact, so it needs no bracket.**
- ⚠ **Do not read `patterns-php/ph16*`, `ph29*` or `ph03*` for anything you
  intend to quote.** They are mid-edit. `ph07-strcut-cursor` is stable and is
  the row to copy conventions from.
- ⚠ **Touch NOTHING under `patterns-php/`.** You are not building a row.

---

## §1 Why this task exists

`RECAP_PHP.md`'s START HERE box names `ph64` as the first temporal row —
*"8-line, ONE id"*. **The cheapness is confirmed. The R1h is not.**

⚠⚠ **`TASK_PHP_015` lost an entire task to exactly this**, stalling on *"no fix
exists"* for `ph07`, later overturned twice over (F34/F38). ⭐ **The lesson is
that "no fix exists" is a CLAIM, and it needs the same quality of evidence as
"here is the fix."** The hunt is therefore owed **before** the build, not inside
it — which is what `TASK_PHP_029` did for `ph73`/`ph21`, successfully.

## §2 What is measured, what is mine, and what is unreviewed

⚠⚠ **EVERYTHING IN THIS SECTION IS MANAGER WORK FROM 2026-09-10 AND IS
UNREVIEWED (rule 9). Re-derive anything you lean on.** Probes and logs:
`.temp/mgr168/{item48_decide,enclosing_fn,spread_axis,sha_norm}.py` + `.log`,
all with `--selftest`.

**(a) `ph64` has ONE corpus id and ONE `fix_commit`, so it does NOT owe open
item 48.** `CRASH-086` → `562f886ecb14`. Of the corpus's 102 catalogued rows,
**30 name more than one fix commit and `ph64` is not among them**; the spread is
**68 % of the temporal axis** (21 of 31), so this is a genuinely lucky row and
the next temporal row probably will not be.

**(b) ⚠ THE PRE-IMAGE SCREEN IS INCONCLUSIVE ON `ph64`, NOT NEGATIVE:**

```
$ python3 .tasks-php/preimage_screen.py --row ph64
   NOT-THE-REPAIR   1
### ph64 · CRASH-086 · 562f886ecb14 · ext/standard/basic_functions.c [[2135,2135]]
    5.0.0     :2135  tick_fe->calling = 0;
    pre-image      ~  zval *func2 = tick_fe2->arguments[0];
    DECISIVE: False  [same_function=False] [bracketed=False]
```

⚠⚠ **Read that correctly.** F64 is that the screen **excludes**; `DECISIVE:
False` is a **rank, not a verdict.** The file drifted so far between 5.0.0 and
`562f886ecb14` that line 2135 is a different statement — the drift case (open
item 49), **not** an exclusion. **So `ph64` has no established R1h and that is
the question you are answering.**

**(c) The cited line is NOT the defect — F1, landing where F1 predicted.**
`CATALOGUE.md` puts the defect in `Zend/zend_llist.c` (`zend_llist_apply`); the
corpus's `c_file_line` is `ext/standard/basic_functions.c:2135`, whose enclosing
function is `user_tick_function_call` — **the callee, i.e. the faulting frame.**

**(d) The kernel is as cheap as advertised.** `Zend/zend_llist.c` is **317
lines** and this is the whole of `zend_llist_apply`, `:186-193`, sha256 of
exactly those 8 lines `fce26e38389ba9fb…`:

```c
ZEND_API void zend_llist_apply(zend_llist *l, llist_apply_func_t func TSRMLS_DC)
{
	zend_llist_element *element;

	for (element=l->head; element; element=element->next) {
		func(element->data TSRMLS_CC);
	}
}
```

**(e) The chain, end to end, all four frames in the pinned tarball:**

```
basic_functions.c:2139  run_user_tick_functions
                          -> zend_llist_apply(BG(user_tick_functions),
                                              user_tick_function_call)
zend_llist.c:190        for (element=l->head; element; element=element->next)
zend_llist.c:191            func(element->data)            <- runs USERLAND PHP
                              -> unregister_tick_function() frees the element
zend_llist.c:190            element->next                  <- READ-AFTER-FREE
basic_functions.c:2135      tick_fe->calling = 0;          <- WRITE-AFTER-FREE
```

## §3 ⭐⭐ THE QUESTION I MOST WANT ANSWERED

**(e) contains TWO fault primitives, at two sites, in one chain:**

| | site | primitive | oracle |
|---|---|---|---|
| **L** the loop | `zend_llist.c:190` | **read**-after-free of a *link pointer*, then the loop follows it | the walk visits a freed node / diverges |
| **C** the callee | `basic_functions.c:2135` | **write**-after-free into a freed struct field | the store lands in freed memory |

⚠ **The catalogue names L as the defect and the corpus's `c_file_line` names C**,
and **both are real.** So:

1. ⭐ **Which one should the row be built at?** Argue it on the C, and say what
   each choice costs the ladder. **L is the standalone container** (F1's shape,
   8 lines, no PHP machinery) and is my prior; **C needs the tick-function
   registry and a zval**, so it carries more C along — but C is what the corpus
   cites and what `provenance.py` will score overlap against.
2. ⚠⚠ **Are L and C one row or two?** They are different primitives with
   different oracles, which under §G1 is evidence for **DIFFERENT**. ⭐ **In
   `patterns-php/` a slight variation is admissible as its own row** — the
   corpus is FRESH and duplication with `patterns/` is not considered at all
   (`PLAN_PHP.md` §3). **So "this is two rows" is an available and possibly
   correct answer.** Say which, with the C in front of you.
3. ⚠ Whichever you pick, `provenance.py` scores against the **cited** span, and
   this row's kernel may come from a different file. That is `ph07`'s multi-span
   shape (open item 25) arriving on the first temporal row. **Say what
   `extra_spans` needs to declare** so the build task is not surprised.

## §4 What you must deliver

1. **The R1h verdict for `ph64`, with the artefact that decides it.** Follow
   `_029`: name the commit, its author and date, the pre-image bytes, the tag
   pair that brackets it, and *what makes it the repair rather than a commit
   that merely touches the area.*
2. ⚠⚠ **If the answer is "no upstream commit fixes it", that is an ADMISSIBLE
   and REPORTABLE result** — but it must be evidenced to the standard §C
   demands, because this exact claim has been overturned before. **Show where
   you looked, over what tag range, with what queries, and what a fix would
   have had to look like.** ⭐ Specifically: **does `zend_llist_apply` ITSELF
   ever get repaired upstream?** The defect is in it, so that is the first place
   to look, and the corpus's column points somewhere else.
3. **A build brief**: the exact `c_file`/`c_lines` spans, the `extra_spans` the
   row needs, the tier you would declare and why, the trigger, and the oracle
   that distinguishes R1 from R1h.
4. **Your answer to §3.**

## §5 ⚠ The traps this specific task walks into

1. ⚠⚠⚠ **§C's "SCAN TAGS UNTIL ONE SUITS" TRAP, WHICH HAS BEEN REFUSED TWICE.**
   Picking the tag at which the row happens to behave is not evidence about the
   repair. **Decide from the commit and its pre-image, then confirm against the
   tags** — in that order.
2. ⚠⚠ **`562f886ecb14` is named by the corpus and the corpus's column is not
   always THE fix** (F38 — that column is *a* commit, not *the* repair). Treat
   it as the first hypothesis, not the answer. ⚠ Nor is an upstream fix
   automatically **correct** or **complete**: `ph07`'s upstream fix was
   half-deleted by upstream itself (F43), `ph16`'s prices two of four repairs
   (F60), and **neither stage of `ph29`'s fix removes the defect** (F65). **In
   four built rows the fix has been incomplete or wrong FOUR TIMES — there is
   no run here, and no prior you may lean on.**
3. ⚠ **A subject line is not a patch.** Measured today: **11 of 163** corpus
   `fix_commit`s have subjects claiming they are optimisations or rewrites
   rather than repairs, so a defect can be removed *incidentally*. Read the
   hunk, not the headline — in either direction.
4. ⚠⚠ **A PROBE WHOSE SETUP ENCODES THE ANSWER evaluates fine and is wrong —
   EIGHT shapes now**, the newest being a **manager** probe this week that
   compared prose-bearing cells and returned a suspiciously perfect 30/30
   (`.temp/mgr168/NOTES.md` §1a). ⭐ **A result that is too clean is the only
   warning this shape gives.** If you build a probe, ship its must-fire.
5. ⚠ **`unregister_tick_function` is the freeing path and it is userland-reachable.**
   Confirm in the tarball that it really frees the element the loop holds; do
   not assume it from the name. **Ask about the FUNCTION, not the text** — a
   grep for a name reported absence *and* presence wrongly at `TASK_PHP_016`.

## §6 What I am least sure of

1. ⭐⭐ **§3.2 — whether L and C are one row or two.** I lean two, and I am
   aware that *"the manager leans"* is how `ph03`/`ph07` ended up as one family
   nobody noticed for four tasks (item 34). **Attack it.**
2. ⚠ **That `ph64` is the right first temporal row at all.** The alternative is
   **`ph73`/CRASH-051, whose R1h `_029` has ALREADY settled and tag-pinned**, so
   it needs no hunt — but its kernel is `zend_std_call_user_call`'s magic-`__call`
   machinery, far more C than an 8-line loop. **My call is `ph64`, because an
   8-line standalone container is the cheapest possible opening for an axis with
   zero rows and it is the axis's characteristic shape (F1).** ⚠ **If your hunt
   shows `ph64`'s R1h is genuinely unresolvable, say so and recommend `ph73`
   — do NOT build a fiction to keep `ph64`.**
3. ⚠ **That the 8 lines are extractable as a `u64`-out kernel.** The loop's
   observable is *which elements got visited*; a faithful driver has to make a
   userland re-entry that frees, from C. **If that forces the kernel to carry
   the tick registry after all, §3.1 changes answer** — and that is a finding,
   not a problem.
