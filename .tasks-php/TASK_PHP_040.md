# TASK_PHP_040 — the R1h hunt for **`ph52` AND `ph53`**, and the build brief for **ROW 7**

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_040_REPORT.md` — **write the FILE** (rule 10).

---

## §0 Why a row, and why now

`quota.py`: **6 rows built · floor 40 · 34 owed · 15 of 20 mechanism families
have ZERO rows.** The last row landed at `_036`; `_037`, `_038` and `_039` are
**three consecutive tasks with no row in them.**

⭐ **And a row is affordable.** Measured (`.temp/mgr174/task_cost.py`): of 39
task files, **19 are one-time** (Phase 0, the mining wave, the catalogue) and
**18 are row-attributable over 6 rows = 3.0 tasks per row**, matching
`PLAN_PHP.md` §8's PAT figure. ⚠ **`RECAP_PHP.md` currently says 6.2 and
rising; that is `total/rows` and it is the wrong quantity** — the correction is
staged in `.temp/mgr174/NOTES.md` §6. **Do not quote the 6.2.**

**Both candidates are in `T3 — initialised before read`, which has 0 built
rows**, and both extend the **type** axis, which has exactly one (`ph45`, `T1`).

---

## §1 ▶ THE TWO CANDIDATES, AND THEIR C SIDE IS ALREADY VERIFIED

⚠⚠ **Both were verified by the manager against the pristine tarball
(`5783e0c0…`, the `SOURCES.md` sha) immediately before writing this. The line
citations below are checked, not copied from `CATALOGUE.md`.** ⭐ **You are not
being asked to re-verify them** — you are being asked to settle the **R1h**,
which is the open part. ⓘ If you do spot-check and find a discrepancy, **say
so**: `PROTOCOL.md` rule 14 exists because a premise in a task file is one an
engineer has no reason to doubt.

### `ph53` · storage grown to the COUNT, tail never written · `verbatim`

| site | verified text |
|---|---|
| `Zend/zend_compile.c:2571` | `ce->interfaces = (zend_class_entry **) erealloc(ce->interfaces, sizeof(zend_class_entry *)*ce->num_interfaces);` — **no zeroing** |
| ⭐ `Zend/zend_compile.c:2591` | **the load-bearing claim, and it holds**: `opline->extended_value = CG(active_class_entry)->num_interfaces++;` — the count reaches its full **declared** value at **compile** time, one `++` per `implements` clause, while the slots are filled **later** by runtime `ZEND_ADD_INTERFACE` opcodes indexed by that `extended_value` |
| `Zend/zend_operators.c:1534-1535` | `for (i=0; i<instance_ce->num_interfaces; i++) if (instanceof_function(instance_ce->interfaces[i], ce …))` — iterates to the full count and **dereferences** |
| `Zend/zend_compile.c:1951` | `if (ce->interfaces[i] == entry)` — reads a slot and only **compares** it, bounded by `ce_num`, not `num_interfaces` |

⭐⭐ **Two consumers at DIFFERENT severities on one defect** — `:1951` compares an
indeterminate pointer; `:1534-1535` dereferences one. **A graded fault in the C
program itself.**
⭐ **Cleaner than `CATALOGUE.md` says**: `:3747` sets `num_interfaces = 0` at
class init, so `erealloc(NULL, n)` is a plain `malloc` and **no slot is written
until runtime** — the *whole* array is indeterminate, not just a tail.
ⓘ `TASK_PHP_020_REPORT.md:76` verified the same three sites independently and
marked the row **SUPPORTED** in 7 minutes (*"easier than stated"*). **Two
independent agreements, site for site.**

### `ph52` · an unconstructed caller slot destructed on an early exit · `narrowed`

| site | verified text |
|---|---|
| `Zend/zend_operators.c:1148` | `zval op1_copy, op2_copy;` — **bare automatics, uninitialised**, in `concat_function` |
| `:1152-1153` | `zend_make_printable_zval(op1, &op1_copy, &use_copy1);` — passed **by address** for the callee to fill |
| `Zend/zend.c:242-243` | `if (EG(exception)) { zval_dtor(expr_copy); …` — the early exit runs a **tag-dispatched teardown over a tag byte that was never written** |

⭐⭐ **AND A PATH CONDITION THE CATALOGUE DOES NOT STATE, WHICH THE BRIEF MUST
CARRY.** `:243` is reached only when the `:233` `get`-handler branch did **not**
return: either the object has no `get` handler, or `:235`'s `Z_TYPE_P(z) !=
IS_OBJECT` fails. The `:236` recursive call **does** write `expr_copy`, and it
`return`s at `:238`. ▶ **So on every path that reaches `:243`, `expr_copy` really
is unwritten — and an extraction that drops the `get`-handler branch changes the
reachability.**

---

## §2 ⭐⭐ THE JOB: SETTLE THE R1h ON BOTH, AND `ph53`'s IS THE DOUBTFUL ONE

`PROTOCOL_PHP.md` §F5 item 5 makes this **three-part and none of it optional**:
**(i)** read the `fix_commit` column; **(ii)** fetch
`https://github.com/php/php-src/commit/<sha>.patch` (a bare-SHA `git fetch` is
refused; **network works — manager-verified, HTTP 200**); **(iii)** ⚠ **confirm
against the release tags that the commit removes YOUR defect.**

From `.tasks-php/FIXSURVEY_001.md`:

| row | fix_commit | year | files | file | message |
|---|---|---|---|---|---|
| **`ph52`** | `7412202c43e7` | **2006** | **1** | same | ⭐ ***"no need to destroy the zval here"*** |
| **`ph53`** | `be8daf1f47fa` | **2008** | 4 | same | ⚠⚠ *"Optimized ZEND_FETCH_CLASS + ZEND_ADD_INTERFACE into sin…"* |

⭐ **`ph52`'s looks like the strongest R1h in the family**: one file, and **the
commit message is the fix**. ▶ **Confirm it** — it should be the cheap half.

⚠⚠⚠ **`ph53`'s IS AN OPTIMISATION FOUR YEARS LATE, AND THAT IS THE INTERESTING
CASE.** A refactor that merges two opcodes may **close the window as a side
effect** rather than repair it. **Three outcomes and you must say which:**

1. **It closes the window** → ⭐ **a MORE interesting R1h than `ph52`'s**: the
   upstream repair is *"delete the second pass"*, not *"add a check"*, and **no
   built row has that shape.** Say so loudly.
2. **It does not** → the row needs a different `fix_commit`, or R1h is recorded
   as **not found** with the evidence. ⓘ `ph36` is the documented precedent for
   a row with no single commit.
3. **`preimage_screen.py` excludes it** → `NOT-THE-REPAIR`, and that is a proof,
   not a ranking.

⚠ **Run `python3 .tasks-php/preimage_screen.py` on both.** It needs the fetched
`.patch` and **no repository and no network**; it is **TEXT-ONLY and never looks
at a line number** (between 5.0.0 and a 2008 commit the function has moved
thousands of lines). ⛔ **`CANDIDATE` IS NOT A VERDICT OF CORRECTNESS** — it
means the screen could not exclude the commit, and §F5(iii) still owes an answer.

### ⚠⚠ THE LESSON THIS TASK IS SHAPED BY

**`_029` hunted the R1h for `ph73` AND `ph21` and BUILT NEITHER.** ▶ **So: hunt
both, and the task succeeds if ONE survives.** `ph52` is the fallback precisely
because its R1h is the stronger on paper. ⛔ **Do not spend the whole task on
`ph53` because it is the more interesting one.** Settle `ph52` first, then
spend what is left on `ph53`.

---

## §3 ⭐ BATCHED: open item **D11**

`preimage_screen.py` is being run anyway. **Item D11 is its third label:
`INAPPLICABLE-SAME-FILE`** — today `INAPPLICABLE` means *"no pre-image hunk for
the defect's file at all"* (the `ph07` shape, where the fix is in the caller in
another file), and it conflates that with a patch that **does** touch the file
but has no hunk covering the cited site. ▶ **Propose the third label, with
must-fire negatives, and say whether either of your two rows exercises it.**

⛔⛔ **DO NOT ADD THE REFUTED `.phpt` SIGNAL** (item D11's own note). It was
tried and it does not work; re-adding it is the one move this item forbids.

⚠ **`preimage_screen.py` is a VALIDATOR, so `PROTOCOL_PHP.md` §H binds**: a
change to it **lands with its must-fire negatives, or it does not land.** *"A
gate run exercises a validator on the rows that pass. It does not attack it."*

---

## §4 ⛔⛔⛔ THE ADMISSION BAR IS **C-SIDE ONLY**, AND BOTH ROWS WILL TEST YOUR NERVE

**Admission is decided SOLELY on the C program**: is it correct on benign
inputs, does it exhibit the target error on an adversarial one, and is its **C
mechanism** distinct from a built row's. (`CLAUDE.md` rule 6, `RECAP_PHP.md`
finding 53.)

⚠⚠⚠ **AND HERE IS THE TRAP, NAMED IN ADVANCE, BECAUSE BOTH CANDIDATES WALK
STRAIGHT INTO IT.** Both mechanisms are **inexpressible in safe Rust** — an
`enum`'s discriminant is always valid and an uninitialised pointer cannot be
named, so R2/R3 **must change the program**. ▶ ⭐⭐ **THAT IS THE FINDING THESE
ROWS EXIST TO PRODUCE. IT IS NOT A REASON TO HESITATE OVER EITHER.**

*"Safe Rust can't express it"*, *"there's no cost gradient"*, *"the R5 can't
state the obligation"*, *"no column moves"* and *"Miri doesn't see it"* are **ALL
FINDINGS, NEVER KILLS.** ⚠ **This bias produced six of ten real refusals and
went uncaught for many sessions, because it lived in the ADMISSION BAR rather
than in any single row** — so row-level review could not see it.

⭐ **What the brief SHOULD say about the Rust side**: what R2 and R3 will have to
do instead, and what R4 (`MaybeUninit`) and R5 (the obligation *"the tag is
initialised before the switch"*) will look like. **A prediction, clearly labelled
as one, so the build task can be measured against it.**

---

## §5 Traps

1. ⚠⚠⚠ **`grep -a` ALWAYS.** A plain `grep` here dispatches to `ugrep`, and on a
   file with **one** non-UTF-8 byte it exits `1` with no stdout and no stderr —
   which reads exactly like *"not present"*. **41 of the corpus's 1 170 `.c`/`.h`
   files are such files.** ⚠ **A probe script does NOT reproduce the failure**,
   so you cannot test your way out of this one.
2. ⚠ **Read the pristine tarball, not an extracted tree.** `SOURCES.md`: there
   are **12** `php-5.0.0` trees on this box and **8 of 12** are byte-identical
   to the tarball. Use
   `tar -xzOf <tarball> php-5.0.0/<path> | sed -n '<a>,<b>p'`.
3. ⚠ **Cite the primary site.** `TASK_PHP_012` M2 priced `ph101`'s *helper* and
   *"reached the right verdict from the wrong frame"*.
4. ⚠ **`CATALOGUE.md`'s `▸ trigger` lines are the unreliable part** — F46
   measured the mechanism sentences right and the trigger lines wrong. **The
   mechanism claims above are verified; the PHP-level triggers are not.**
   ⓘ And a PHP-level trigger's reachability is **provenance, not admission** —
   the kernel is a C program and the blob decides when the query happens.
5. ⚠ **Keep the generator, delete the artefact** (`CLAUDE.md` constraint 6).
   Fetched `.patch` files go to `.temp/php40/patches/` — the established
   convention (`.temp/php31/patches/562f886ecb14.patch`) — and **stay**, because
   they are evidence a fetch cannot re-derive identically. `.pyc` and scratch
   blobs go.
6. ⚠ **`timeout <N> <cmd>`**; never `pkill`/`killall`/substring match.
7. ⚠ **`.temp/` is gitignored** — put the NUMBERS and the SHAs in the report, not
   a pointer to a log (open item **65**).

---

## §6 ⛔ Scope

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `common-php/`, `patterns/`,
`patterns-php/`, `results/`, `results-php/`, `pilot/`.** ⛔ **This task BUILDS NO
ROW** — it settles provenance and writes a brief. **No gate run, no `spec.md`.**
✅ **You MAY edit `.tasks-php/preimage_screen.py`** for §3, **with negatives**
(§H). Other writes go to `.temp/php40/`.
⚠ **No `git add` / `git commit`.** Never touch `.web/`.
ⓘ `TASK_PHP_039` may still be running; it touches **only** `.temp/php39/` and
its own report, so there is no overlap. **Do not read or modify its files.**

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`14/0`**, **first and
last**. Manager-verified immediately before writing this. ⚠ **Nothing in your
scope can move either.**

---

## §7 Definition of done

1. **A verdict on `ph52`'s R1h and on `ph53`'s**, each with: the fetched patch's
   sha, the `preimage_screen.py` label, and the **§F5(iii) tag comparison** —
   *does this commit remove the 5.0.0 defect at the cited site?* ⚠ **Not the
   screen alone: `CANDIDATE` is not an answer.**
2. ▶ **A RECOMMENDATION for row 7, with the reason**, and it must be one of the
   two. ⚠ **If both R1h survive, recommend on `verbatim` over `narrowed` and
   say so**; if only one survives, that is the recommendation.
3. **The build brief** for the recommended row: tier, the deletions to itemise,
   the kernel's C shape, the blob format, the benign corpus, the adversarial
   input and what it triggers, the `u64` the gate will compare, and §4's
   **labelled prediction** for the five rungs.
4. §3's third label, **proposed with must-fire negatives**, and whether either
   row exercises it.
5. ⭐⭐ **`NOT FOUND` IS A VALUED ANSWER for an R1h.** `ph36` is the precedent and
   `_029` is the warning. ⛔ **Do not promote a commit to R1h to make the task
   look finished** — `PLAN_PHP.md` §4.3 records an earlier effort that *"reported
   a real defect as unreachable and then invented an explanation for the upstream
   fix."*
6. ⚠ **Declare your expectations before fetching either patch**, in the report,
   and say afterwards whether they held.
