# TASK_PHP_008 — stop detecting, start guaranteeing

**Role:** research engineer. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_008_REPORT.md` — write the FILE.

Read `.tasks/PROTOCOL.md`, then **`.tasks-php/TASK_PHP_007_REPORT.md`** (the
review you are landing; every finding ships a generator under `.temp/php7/`),
then `TASK_PHP_006_REPORT.md`, `PLAN_PHP.md`, `.tasks-php/PROTOCOL_PHP.md`.

⚠⚠ **`RECAP_PHP.md` IS MANAGER-ONLY — do not edit it.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**

**Bracket**: `harness/measure.py --check-stale` → `66/0` and
`harness-php/gate.py --tool measure --check-stale` → `2/0`, first and last,
both pasted.

---

## §0 ⚠⚠⚠ READ THIS BEFORE ANYTHING ELSE: THE MANAGER IS CHANGING THE DESIGN, NOT THE FIX

**B1 has now been "closed" twice and reopened twice.**

| | mechanism | how it was bypassed |
|---|---|---|
| `TASK_PHP_004` | a mandatory symlink, checked by a **string search** of `c/*` | `#include "emalloc_shim.c"`; `c/<subdir>/*` |
| `TASK_PHP_006` | the string search replaced by **`gcc -MM`** | 2 of 8 preprocessor states; a fallback that fails open and that the row can *choose* |

**Both fixes answered the question *"does this row use the allocator?"*. That
question has an unbounded answer space — every preprocessor spelling, every flag
combination, every compiler — and each round we enumerate a few more of it.**
⚠ **A guard whose correctness depends on enumerating idioms will be reopened by
the next idiom.** Two rounds is enough evidence.

### The decision: make the question stop being load-bearing

**EVERY `patterns-php/` row carries `<row>/c/emalloc_shim.h` as a symlink to
`common-php/emalloc_shim.h` — unconditionally, whether or not it uses the
allocator.** Then there is nothing to detect.

✅ **Manager-verified that this works, from evidence already in the tree:**
- `TASK_PHP_005` `ph51-linked`: with the link, the allocator is in **both**
  digests (gate and measurement).
- `TASK_PHP_004` `ph96-orphanLink`: a row carrying the link **without using it**
  passes and was already classified *"harmless, but the record pins an allocator
  the row does not use"*.
- `results-php/gate/ph00-smoke.json` keys are `patterns/<row>/c/*`, and
  `check.py` hashes the **target's** bytes through the link (`59b146689d42`
  matched `common-php/emalloc_shim.h` in `TASK_PHP_004`'s own run).

**What this costs, stated honestly:** an `emalloc_shim.h` edit will mark **every**
php row stale, not only the allocating ones. That is a real cost in re-gates —
and it errs **safe**: it can over-re-gate, and can never leave a stale record
`FRESH`. That is the trade, and it is the manager's.

### What you must do

1. **Land the unconditional rule.** The audit becomes: for every
   `patterns-php/*/`, does `c/emalloc_shim.h` exist, is it a **symlink**, does it
   `realpath` to `common-php/emalloc_shim.h`? **No subprocess, no flag space, no
   compiler, no fallback, no regex.**
2. ⚠⚠ **DELETE `_tu_closure`, `_MM_CONFIGS`, `_INCLUDE_RX` and the `texty`
   fallback.** Do not keep the preprocessor closure "as a note". It emitted
   *"dead code … Not treated as a shim user"* about a row that allocates 1000
   times in half the measured cells (`TASK_PHP_007` §1.3), and **a wrong note is
   worse than no note** — it is the same shape as the `emalloc_shim.c` comment
   that caused the first hole. ⚠ **This task should REMOVE more code than it
   adds. If it does not, tell me why.**
3. **Re-run the reviewers' fixture rows from their unmodified generators** —
   `.temp/php5/b1_bypass.py` and `.temp/php7/01-flagmatrix` /
   `12-residuals` — and show that **every** row now either carries the link or is
   refused. ⚠ **`ph55-extern` and `ph95` (no shim, no link) must now be
   REFUSED too**, because the rule is unconditional; that is a deliberate change
   from a clean negative to a failure, and your report must say so.
4. **`uses_allocator` becomes DECLARED, not detected.** Add it to the
   `provenance` block (`PLAN_PHP.md` §6) as a field the row's author states and a
   reviewer checks. ⚠ It is **documentation, not a digest input** — nothing may
   depend on it being right.

## §1 The subdir ban — LIFTED, and the reviewer's audit replaces it

⚠ **My ban was both insufficient and over-strict, and the reviewer proved both.**

- **Insufficient**: `gate.py:345` skips a **symlinked** directory by name
  (`or os.path.islink(p)`), so `ln -s ../../../extract/Zend c/zend` compiles
  every header behind it into **neither digest**, unrefused (`ph81-dirlink`).
  A dotfile `c/.payload.h` walks round it too (`glob` never matches a leading
  dot). **Fix both — an unsound ban is worse than an over-strict one.**
- **Over-strict**: the reviewer **built** the 12-line flat-link audit I had
  accepted could not exist, and fired it in both directions (must-fire on the
  next-file-added case, must-not-fire on a fully linked tree).

**So: allow `c/<subdir>/`, gated on that audit** — every file under a `c/`
subdirectory must have a flat symlink beside it, or the preflight refuses.
⚠ **This is sound where the allocator detector was not, and the reason matters:
it enumerates FILES — a finite, observable set — not IDIOMS.** Say in
`PROTOCOL_PHP.md` §B3 that the layout is available and priced, not forbidden.

## §2 The overlap floor — REPORT IT, DO NOT GATE ON IT

`TASK_PHP_007` M2: the `#if 0` fix has **nine** more spellings, `#if 1 … #else`
is undisclosed and `#elif 0` is actively mishandled.

⚠ **This is §0's class again**, one level down: a floor whose correctness
depends on parsing every preprocessor conditional will be reopened by the next
one. And `RECAP_PHP.md` open item 14 already records what the check really is —
*it measures presence of text in a file, not presence of code in the benchmark.*

**Decision: `provenance.py` REPORTS the overlap percentage and STOPS REFUSING on
it.** Keep the "the citation names a different file" check (`c_file` /
`extract_sha256` — those are exact, not heuristic). ⚠ **Fix `#elif 0`'s
mishandling anyway**, because a *wrong* number is worse than an unenforced one —
the same reason as §0.2.

⚠ **This is the third check this programme has demoted from enforcing to
reporting** (the `why` size, the preflight-absence note, now this).
**If you think the pattern is now a habit rather than a principle, say so** —
that is a real risk and I would rather hear it than not.

## §3 The rest of the majors

- **M3 — the committed record grows without bound.** It collapses a run only
  against the *immediately preceding* one, so two alternating routine commands
  never collapse — and one of them is the bracket **every task file mandates
  twice**. Collapse on a **content key**, not on adjacency, and cap it.
- **M4 — the deadlock that justified "absence is a NOTE" does not exist.**
  `gate.py:972-978` writes the record on the failure path; the reviewer
  demonstrated it. ⚠ **So make a missing preflight record a FAILURE**, and if you
  still believe a note is right, say why **with the deadlock reproduced**, not
  asserted.
- **M5 — `--audit` is content-blind.** It asks only whether a file exists, so a
  row whose every recorded preflight FAILED reports `complete`. Read the verdict.
- **m1 and the minors** in `TASK_PHP_007` §8. ⚠ Correct `~115 ms/row` to the
  measured **~135**; the affordability conclusion is unchanged and stands.

## §4 Rules

- **No `git add` / `git commit`.** Read-only git is fine.
- Scratch under `.temp/php8/`. **Never `/tmp`.** ⚠ `.temp/php5/`, `.temp/php6/`
  and `.temp/php7/` hold the previous generators — **reuse, do not delete.**
  `.temp/php5/snapshot.py` is the byte-level PAT snapshot with its own control;
  ⚠ **use it — `TASK_PHP_006` skipped it and `TASK_PHP_007` did not.**
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — exact PID via
  `/proc/<pid>/cmdline`.
- Everything claimed must have been **RUN**, output pasted.

## §5 The calls I am least sure of

1. ⚠⚠ **That the unconditional link is right.** Its cost is that every php row
   re-gates when the shim changes, and I have **not** measured how often the shim
   will change once rows exist. **If you can show a cheaper design that is still
   correct by construction — not by enumeration — I want it.** ⚠ What I do not
   want is a third detector.
2. ⚠ **That deleting the preprocessor closure loses nothing worth keeping.** It
   is genuinely useful information when it is right. I am judging that a check
   which has been wrong in both directions (false positive at `TASK_PHP_005`
   F-8, false *reassurance* at `TASK_PHP_007` §1.3) should not be kept as
   advice. **Argue if you disagree.**
3. ⚠ **§2's demotion.** Three demotions in three rounds is either the right
   principle applied consistently or an excuse applied repeatedly, **and I cannot
   tell from the inside.**

---

**Running count: launched from 20.** `TASK_PHP_007` found **2 blockers** and
refuted the manager once (the subdir ban, both ways). ⚠ **It also upheld all
three of `TASK_PHP_006`'s refutations under attack** and verified the no-touch
claim **by bytes** over 2 966 paths with a fired control — the check the
previous engineer had disclosed it skipped. **Its eleven clean negatives are in
its §7: read them before re-running anything.**
**Reconciliation is the manager's job** — state what you refute and let the
manager carry it.
