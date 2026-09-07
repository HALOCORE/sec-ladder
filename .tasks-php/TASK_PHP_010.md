# TASK_PHP_010 — land `TASK_PHP_009`'s four majors. Small, mechanical, bounded.

**Role:** research engineer. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_010_REPORT.md` — write the FILE.

Read `.tasks/PROTOCOL.md`, then **`.tasks-php/TASK_PHP_009_REPORT.md`** (the
review you are landing; every finding ships a generator under `.temp/php9/`),
then `PLAN_PHP.md` and `.tasks-php/PROTOCOL_PHP.md`.

⚠⚠ **`RECAP_PHP.md` IS MANAGER-ONLY — do not edit it.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**

**Bracket**: `harness/measure.py --check-stale` → `66/0`, and
`harness-php/gate.py --tool measure --check-stale` → `2/0`, first and last.

---

## §0 ⚠⚠ SCOPE — THIS TASK IS DELIBERATELY SMALL, AND THAT IS THE POINT

**Phase 0 is CLOSED.** `TASK_PHP_009` found **no blocker** and its verdict was
argued: *the thing that would justify a ninth infrastructure task is that the
enforcement layer is unsound in a way we cannot bound; that was true of B1 twice
and is not true now.*

⚠ **Nine tasks have gone to infrastructure and mining with ZERO rows built.**
This task exists because M1 and M2 sit in the layer the **first real row** leans
on, and both are minutes of work. **It is four fixes and their controls. Nothing
else.**

⚠⚠⚠ **DO NOT WIDEN SCOPE.** If you find something adjacent — and you will —
**report it, do not fix it.** A tenth infrastructure task that grows in flight
is how this phase fails to end. The next task builds the catalogue and then the
programme builds rows.

## §1 M1 — a row can hide from `glob`

`shim_link_audit`, `c_digest_audit`, `why_sizes` and `preflight_coverage_audit`
iterate `glob("patterns-php/*")`, which never matches a leading dot — while
`build.py:81-89` (`os.listdir`) and `provenance.py` both resolve a dotted row.
✅ Demonstrated end to end: `gate.py --preflight .ph93` → **rc=0** on a row
carrying a regular-file allocator copy *and* an unkeyed subdirectory source.

**Fix, exactly as the reviewer specifies:** `os.listdir` in place of
`glob("*")` in all four, and `os.listdir(rdir)` filtered on `.json` in
`preflight_coverage_audit`. **Then add one negative: a dotted row is REFUSED BY
NAME** — it can never be keyed, because `glob` cannot reach its records either.
That is the same verdict `c_digest_audit` already gives a dotted *file*.

⚠ **Use `.temp/php9/a1_row_enum.py` case 3 as the must-fire** — it already is
one. Do not write a new fixture where one exists.

⚠⚠ **This fix is the reason the design survives, so get the reasoning into the
code comment, not just the behaviour:** the idiom detector had **no** complete
enumeration; a row enumeration **exists**, is one call, and `build.py` already
uses it. **The audit and the builder must enumerate the same set.** A future
edit that reintroduces `glob` here should read why it must not.

## §2 M2 — an upward include escapes both digests

`c/kernel.c` → `#include "../aux/x.h"` compiles, runs the row's own allocator,
and is in **neither** digest. ✅ Measured: editing it moved behaviour
(`tally 1 → 1000`) with **0 digest keys moved and 0 preflight problems**.

**Fix: refuse any directory under `<row>/` outside `{c, inputs, controls}`.**
⚠⚠ **DO NOT REACH FOR `gcc -MD`** — the reviewer says so and it is the right
call: an include-closure detector is the thing this programme deleted two tasks
ago, and it would come back with the same unbounded input space.

⚠ **`.temp/php9/a2_upward_include.py` is the must-fire; its case (5) is the
must-NOT-fire.** Both already exist.

⚠ **And fix the documentation that makes this MORE likely.**
`PROTOCOL_PHP.md` §B3 teaches that the danger is subdirectories *of `c/`* — but
the natural php layout is a **sibling** directory mirroring the tarball, which
is precisely the one that escapes. §B3's soundness sentence also claims the
audit's input is `os.listdir`; **make that true (§1) rather than deleting the
claim.**

## §3 M3 + M4 — one change closes both

`preflight_coverage_audit` is **GLOBAL**: one uncertifiable record fails **every**
`gate.py` invocation, including the mandated bracket. An orphan
`results-php/<row>.json` — a **retired** row whose committed records survive,
which `PLAN_PHP.md` §3 expects to happen — can never obtain a certifying run,
because the prescribed repair fails on provenance, which is substantive.

**Fix: make the coverage stage report PER-ROW rather than globally.** The
reviewer names this as the one cheap change that closes M3 and M4 together, and
the global scope is the property `TASK_PHP_008` §8b's first deadlock also rode
on.

⚠⚠ **And DELETE the sentence *"⚠ THERE IS NO DEADLOCK"* from
`gate.py:853-856`.** It is printed at the exact moment an operator is standing
in one. **This is the third instance of the same defect in three tasks** — after
`emalloc_shim.c`'s *"CANNOT BE"* and the *"dead code … Not treated as a shim
user"* note — and all three are **a reassurance that tells the reader not to
look further**. Replace it with the repair the message currently never names:
*if the row was retired, delete `results-php/<row>.json` and
`results-php/gate/<row>.json` in the same commit.*

⚠ **Re-run `.temp/php9/07-orphan-deadlock.log`'s generator** and show it
converges. Keep the non-convergent arm as the control.

## §4 The minors, and one correction

Land `TASK_PHP_009` §7's minors. ⚠ **`m2` deserves attention**: `MAX_RUNS`'s
test measured the class the cap **exempts** — 120 no-problem runs cap at 40,
but **1000 evidence-carrying runs keep all 1000**, and evidence-carrying is the
state that actually occurs. Fix the cap or justify the exemption with the state
modelled.

## §5 Rules

- **No `git add` / `git commit`.** Read-only git is fine.
- Scratch under `.temp/php10/`. **Never `/tmp`.** ⚠ `.temp/php5–9/` hold the
  previous generators — **reuse them; several are named above; do not delete.**
- ⚠ **Use `.temp/php5/snapshot.py`** for the closing no-touch check, by bytes,
  with its control fired.
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — exact PID via
  `/proc/<pid>/cmdline`.
- Everything claimed must have been **RUN**, output pasted.

## §6 The calls I am least sure of

1. ⚠ **That per-row coverage really closes M4 as well as M3.** I am taking the
   reviewer's word that the global scope is the shared property. **Check it** —
   M4 is about a `php_provenance: true` row on a tarball-less box, and if
   per-row scope does not help there, say so and price the separate fix.
2. ⚠ **That refusing directories outside `{c, inputs, controls}` is not
   over-strict.** It is a whitelist, and whitelists age. **If a row will
   plausibly need a fourth directory, say which and why now** — the last
   whitelist-shaped decision I made (the `c/<subdir>` ban) was both insufficient
   and over-strict, and I would rather hear it before the catalogue than after.
3. ⚠ **That this task stays small.** If landing these four honestly requires
   more, **stop and report** rather than growing. I would rather run an eleventh
   task deliberately than discover one happened.

---

**Running count: launched from 26.** `TASK_PHP_009` refuted the manager twice —
⚠ **including the framing that mattered more than the bug**: *"a wrong
enumeration is not an unboundable one, and pricing the first as the second is
how a fixable bug gets priced as a phase."* It also **upheld five things under
its own attack**, including the one claim `TASK_PHP_008` had reasoned rather
than run. **Its twenty clean negatives are in §7 — read them before re-running
anything.** Reconciliation is the manager's job.
