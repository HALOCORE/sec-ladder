# TASK_PHP_032 — BUILD `ph64`, the FIRST TEMPORAL ROW

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_032_REPORT.md` — **write the FILE** (rule 10).

⚠⚠⚠ **YOUR SPECIFICATION IS `TASK_PHP_031_REPORT.md` §6, AND IT IS NOT RESTATED
HERE.** That report settled `ph64`'s R1h, measured its oracle and computed every
`extract_sha256` you need. **Read §6.1–§6.6 and build to it.** This file carries
only what §6 does not: the manager's decisions on it, and the traps.

⚠ **Two copies of one specification is how both go stale** — this programme's own
standing lesson. **If §6 and this file disagree, §6 wins on anything technical
and this file wins on scope.** Say so if you find a disagreement.

**Read**, in this order:
1. **`.tasks-php/TASK_PHP_031_REPORT.md` in full** — §6 is the brief; §5 is why
   it is one row; §4.3 is the one thing left open; §7 is where the previous task
   file was wrong.
2. `.tasks/PROTOCOL.md` — rules 9, 10, 13, 14.
3. `.tasks-php/PROTOCOL_PHP.md` — **§C, §F5 and §A2a** all bind this build.
4. `.memory-php/` 00–04 **in full** — authoritative, and supersedes any task
   report it contradicts, **including `_031`'s**.
5. `patterns-php/ph07-strcut-cursor/` — ⭐ **the only row to copy conventions
   from.** It is discharged, re-gated, and has the spellings control.
   **Read it; do not touch it.**
6. `patterns-php/SOURCES.md` §2 — the tarball read recipe.

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **No `git add` / `git commit`.** Never touch `.web/`.
⚠ Scratch under `.temp/php32/`. **Never `/tmp`.** ⭐ **`.temp/php31/` holds the
oracle probe, the patch, the tag sweep and the span shas — reuse it, do not
re-derive it.**
⚠ **`grep -a` ALWAYS** (blind to 41 of 1170 corpus files, silently — F35).

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`10/0`**, first and last.
⚠ **`_028` may have moved the php figure** — it was discharging the spellings
debt and a `controls/*.py` addition re-gates a row. **If your FIRST reading is
not `10/0`, do not assume damage: check `git log` for `_028`'s landing and
report the figure you actually get.** ⚠ A row adds **two** measure records.

---

## §1 The manager's decisions on `_031`'s brief

All four verified independently before this task was written; the verification
is in `.temp/mgr168/NOTES.md` §10.

1. ✅ **ACCEPTED: R1h is `562f886ecb14`**, and it ships per §6.5. Verified from
   the patch itself — the subject names bug #41037, it adds a NEWS line, and it
   creates `bug41037.phpt` (23 lines): **three artefacts inside the commit.**
   The backport applies to pristine 5.0.0, whose `user_tick_function_compare`
   at `basic_functions.c:2146` is **byte-identical to the patch's pre-image**;
   the disclosed fuzz is one **trailing context line** (`php_call_shutdown_functions(void)`
   vs `(TSRMLS_D)`) in the *adjacent* declaration, outside the patched function.
2. ✅ **ACCEPTED: ONE ROW, primary span at L, C in `extra_spans`** (§5.1, §5.4).
   ⚠ **I had written *"I lean two"* and I was wrong.** The decisive point is
   that the fix's predicate `tick_fe1->calling` **is site C's own state
   variable**, so an L-only row has no predicate, therefore no R1h, therefore
   breaks §C. **Refuted on R1h grounds, which is stronger than §G.**
   ⚠ `_031` states plainly that **§G's letter would say "two rows"** and why it
   is not deciding there. **That tension is real and stays on the record** —
   do not paper over it.
3. ✅ **ACCEPTED: tier `narrowed`** (§6.2). ⚠ **`CATALOGUE.md:170` says
   `verbatim`** and is wrong about the row while right about the file. **That is
   a MANAGER landing, not yours** — build to `narrowed` and note the divergence.
4. ✅ **ACCEPTED: the oracle is §6.4's, NOT the catalogue's.** ⚠⚠⚠ **The `u64`
   the catalogue proposes MEASURES NOTHING** — request 39 → `REAL_SIZE` 40 →
   cached, payload untouched, so the visit fold is **bit-identical R1 vs R1h**
   on the corpus's own trigger. **This is F46's class on the first temporal row
   and it is exactly the half a build task runs on.** Also a manager landing.

## §2 What this task delivers

**A gated `patterns-php/ph64-<slug>/` at all five rungs plus R1h**, to
`PROTOCOL_PHP.md` and the `ph07` template, with `spec.md` + `model.py`, and
`results-php/` records. ⭐ **Name the slug for the MECHANISM, not the file** —
`ph07-strcut-cursor` is the pattern to follow.

⚠ **Budget six commands (~28 min) per open item 11**: `gate → report → gate` is
irreducible. ⚠ **And budget several re-gate rounds** — `TASK_PHP_018` needed
**eleven** and *every extra one caught a real defect.* **Rounds are not
failure.**

## §3 ⚠ The traps this specific build walks into

1. ⭐⭐ **STAGE 7h SHOULD BE GREEN FIRST TRY, AND THAT IS A PREDICTION YOU CAN
   FALSIFY.** §6.4 measured R1h as changing **nothing** on the benign domain
   (4 scenarios; fold, tally and count all equal). **If 7h fails, something in
   §6 is wrong — stop and report it rather than adjusting the corpus to suit.**
   ⚠⚠ `ph07` was rebuilt for exactly the opposite situation (its upstream fix
   changed benign output on 15 870 of 117 612 calls), so this is the property
   that made `ph64` buildable. **Check it, do not assume it.**
2. ⚠⚠ **THE FAITHFUL CHAIN IS ~140 LINES, NOT 8** (§5.3). The 8-line
   `zend_llist_apply` is the *defect*, not the *extraction*. ⚠ **I wrote "8
   lines, no PHP machinery" into `_031`'s task file and it is false.** Do not
   size the work off it.
3. ⚠⚠ **`provenance.py` scores overlap against the PRIMARY span**, and this row
   has **nine `extra_spans`** (§6.1) including the R1h frame `[2146,2161]`.
   That is open item 25's lesson applied in advance — ⭐ **but item 37(a)
   measured that adding a span can move the number **UP**, so the union
   fraction is not a monotone quality signal. Report the number; do not tune it.**
4. ⚠ **§A2a's four `DEL_LLIST_ELEMENT` arms** (§6.3) — all four are in the
   oracle's scope and R1 SIGSEGVs at three of them. **A trigger that reaches one
   arm is not a trigger that reaches the mechanism.**
5. ⚠⚠ **A PROBE WHOSE SETUP ENCODES THE ANSWER evaluates fine and is wrong —
   EIGHT shapes now.** ⭐ `_031` disclosed **two of its own** and an F35
   instance in its own `fnbody.py`, each caught only by a **declared
   expectation written before the run**. **Declare expectations first. Ship
   must-fire and must-NOT-fire.** §H binds every validator you add.
6. ⚠ **The gate hashes `controls/*.py` and never RUNS them** (`_022` m6), so
   your negatives are the only thing between a control and a silent wrong
   number.
7. ⚠ **Use the FULL row directory name** on every `harness-php/gate.py`
   invocation. The preflight record is keyed by the string you type (F55 / open
   item 42) and a short name silently forks the audit trail — **I did this
   myself on `ph29` and the engineer caught it, not me.**

## §4 §4.3 — the open incompleteness candidate. ORDER MATTERS.

`_031` found, by **inference and not by measurement**, that R1h's own refusal
path runs `php_error_docref(E_WARNING)` → `php_verror` → `php_error` →
`zend_error`'s **user-handler** arm — i.e. **arbitrary userland from inside
`zend_llist_del_element`'s walk**, which holds `current`/`next`. It is visible
in the patch hunk, and **master later upgraded it to `zend_throw_error`, which
cannot run userland.**

⚠⚠ **BUILD THE ROW FIRST. Do NOT resolve §4.3 before the row gates green.**
It is a *separate* question and it has a one-file test script in §4.3. If it is
measured and confirmed, `ph64` becomes the **fifth of five** built rows whose
upstream fix is incomplete or wrong (F43 `ph07`, F60 `ph16`, F65 `ph29`, and
`ph03`) — ⭐ **which at 5 of 5 stops being a per-row curiosity and becomes the
programme's most repeated result.** ⚠ **But an unbuilt row with a beautiful
finding is worth less than a built row with an open item.**

## §5 What I am least sure of

1. ⚠⚠ **That one task can build this row.** Four of four previous builds needed
   a second task for something (`ph07` a rebuild, `ph16` the spellings split,
   `ph29` the shim question, `ph03` the spread). ⭐ **If the ladder is honest
   and expensive, ship the rungs and say the spellings search needs its own
   task** — that is what `_025` did and it was right. **Do not carry the
   spellings debt silently**: `_028` exists because three rows did.
2. ⚠ **That `narrowed` is the right tier.** §6.2 argues it and I accept the
   argument, but **item 21 is a standing finding that 12 rows declare a tier
   their defect site contradicts**, and `provenance.py` reports overlap against
   the declared tier's expectation. **If the number looks wrong for `narrowed`,
   say so — the tier is a cost statement, never a filter, and no row's
   admission moves.**
3. ⭐ **That the temporal axis behaves like the spatial one at all.** Four rows
   built, all spatial, and **`.memory-php/02-ladder.md` records four rows with
   four different answers on fix-completeness — so there is no run and never
   was one.** **Do not expect this row to look like the others, and do not
   report a difference as an error.**

⚠⚠⚠ **NEVER refuse or drop a pattern for a Rust-side, Verus-side, ladder-side
or cost reason.** Admission is C-side only. *"Safe Rust can't express it"*,
*"there's no cost gradient"*, *"the R5 can't state the obligation"*, *"Miri
doesn't see it"* are **all FINDINGS, never kills** — and this bias has shaped
six of ten real temporal refusals, so it is **this axis** it damages most.
