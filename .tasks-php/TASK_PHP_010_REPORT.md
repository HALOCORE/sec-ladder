# TASK_PHP_010 — landing `TASK_PHP_009`'s four majors — ENGINEER REPORT

**Role:** research engineer. **One agent, alone. Launched from a running count of 26.**
**Reconciliation is the manager's job.** What I correct is in §7.

> **VERDICT UP FRONT.** ✅ **All four majors landed, all six minors landed, every
> must-fire and must-NOT-fire run and pasted.** ⚠⚠ **But the task's §2 fix is
> WRONG AS WRITTEN and I did not ship it as written**: a whitelist of exactly
> `{c, inputs, controls}` **refuses all 33 built PAT rows and would refuse every
> php row the moment `model.py` is imported**, because every row acquires a
> `__pycache__/`. Measured, 33/33. `__pycache__` is exempt in what shipped.
> ⚠⚠ **And the §3 fix does not make the orphan case "converge" — it makes it
> STOP BLOCKING.** A retired row's record never converges by repetition and must
> not: the repair is `git rm`, which is now what the message says. Both are in §7.
>
> **Bracket, first and last, both pasted** (`.temp/php10/01-bracket-open.log`,
> `19-bracket-close.log`):
>
> ```
> FIRST  python3 harness/measure.py --check-stale                  66 record(s) examined, 0 STALE
> FIRST  python3 harness-php/gate.py --tool measure --check-stale   2 record(s) examined, 0 STALE
> LAST   python3 harness/measure.py --check-stale                  66 record(s) examined, 0 STALE
> LAST   python3 harness-php/gate.py --tool measure --check-stale   2 record(s) examined, 0 STALE
>            FRESH  results/gate/ph00-smoke.json   29 source(s)
>            FRESH  results/ph00-smoke.json        19 source(s) + 8 input(s)
> ```
>
> **No-touch, BY BYTES, control fired first, FIVE baselines** (`02-snapshot-open.log`,
> `19-bracket-close.log`):
>
> ```
> $ python3 .temp/php5/snapshot.py control
> control: 27 files snapshotted, one byte-appended
>   CHANGED  common/slb.py  2abd87f76712 -> 27618554643a
> CONTROL FIRED
>
> .temp/php5/pat-snapshot.json             snapshot check: 2966 recorded, 2966 now, 0 difference(s)
> .temp/php7/pat-snapshot-007-start.json   snapshot check: 2966 recorded, 2966 now, 0 difference(s)
> .temp/php8/pat-snapshot-008-start.json   snapshot check: 2966 recorded, 2966 now, 0 difference(s)
> .temp/php9/pat-snapshot-009-start.json   snapshot check: 2966 recorded, 2966 now, 0 difference(s)
> .temp/php10/pat-snapshot-010-start.json  snapshot check: 2966 recorded, 2966 now, 0 difference(s)   <-- mine
> ```
>
> **Files changed — three, plus two committed records that RECORD MY OWN RUNS:**
>
> ```
>  .tasks-php/PROTOCOL_PHP.md                  |  75 +++-
>  harness-php/gate.py                         | 517 +++++++++++++++++++++++----
>  harness-php/root.py                         |   7 +-
>  results-php/preflight/_norow.preflight.json |  99 ++++++     <- 5 -> 7 runs, both clean
>  results-php/preflight/ph00.preflight.json   |  57 ++++++     <- 11 -> 12 runs, clean
> ```
>
> ✅ **No re-gate and no re-measure is owed**, and that is checked rather than
> assumed (`.temp/php10/22-no-digest.log`): the gate record's 29 `source_sha256`
> keys and the measurement record's keys contain **zero** `harness-php` entries.
> The closing bracket's `2 record(s), 0 STALE` is the same fact from the other side.
>
> **Scratch:** `.temp/php10/` — **23 logs, 5 probes**, one PAT snapshot; every
> fixture tree and the one ELF binary deleted. `.temp/php5–9` re-run, never
> modified: `.temp/php9/fix/`, which my re-runs of `a1`/`a2`/`a3`/`a8`
> **recreated**, is deleted again (php9 back to its 32 files), and
> `find .temp/php{0,1,2,3,4,5,6,7,8} -newermt '2026-09-07 13:25' -type f` is
> **empty**.

---

## §0 What shipped, by path

| # | fix | where |
|---|---|---|
| M1 | one row enumeration, `os.listdir`, shared by all four audits | `gate.py::_row_dirs` + `shim_link_audit`, `c_digest_audit`, `why_sizes`, `preflight_coverage_audit` |
| M1b | **a dotted row is refused BY NAME** | `gate.py::c_digest_audit` |
| M2 | **a row may contain only `{c, inputs, controls}`** (`__pycache__` exempt) | `gate.py::ROW_DIRS`, `_row_layout_problems`, called from `c_digest_audit` |
| M3+M4 | **the coverage stage reports PER-ROW**; `--audit` stays global | `gate.py::preflight_coverage_audit(row=None)`, both call sites |
| M3b | *"⚠ THERE IS NO DEADLOCK"* **deleted**; the retirement repair named | `gate.py::preflight_coverage_audit::_REPAIRS` |
| m1 | exact-match preflight lookup, not a prefix glob | `gate.py::_row_key` + the `hits` list |
| m2 | `MAX_RUNS` is an **absolute** bound; evidence is a priority, not an exemption | `gate.py::_collapse_and_cap`, `write_preflight_record` |
| m3 | *"`0 STALE` … still matches **or has been deleted**"* | `PROTOCOL_PHP.md` §E |
| m4 | the dangling `.temp/php0/pycdemo` citation repointed at the surviving evidence | `gate.py` docstring, `root.py` docstring |
| m5 | *"a failing run is not read-only"* | `PROTOCOL_PHP.md` §E table, `gate.py::write_preflight_record` |
| m6 | why `os.path.isfile` keeps a FIFO out of the key set | `gate.py::c_digest_audit`, beside the filter |
| doc | §B3a: **the danger is the SIBLING directory, not the `c/` subdirectory**; the `os.listdir` soundness sentence made TRUE rather than deleted | `PROTOCOL_PHP.md` §B3 |

**Not touched:** `harness/`, `common/`, `patterns/`, `results/`, `pilot/`,
`RECAP_PHP.md`, `.memory/`. No `git add`, no `git commit`.

---

## §1 M1 — a row can hide from `glob`

**Fixed exactly as specified**, plus the negative the task asks for. All four
audits now go through one function:

```python
def _row_dirs(patterns_dir):        # gate.py
    """Every row directory under `patterns_dir`. Returns `(rows, dotted)`."""
    entries = sorted(os.listdir(patterns_dir))          # <- build.py's resolver
```

⚠ **The reasoning is in the code, not only in the behaviour**, as §1 demands —
a 25-line comment block above `_row_dirs` carrying the invariant
(**THE AUDIT AND THE BUILDER MUST ENUMERATE THE SAME SET**), the reason it is a
substitution and not another round of whack-a-mole (a complete enumeration
exists, in one call, and `build.py` already makes it), and an explicit
*"do not put `glob("*")` back here for tidiness"*.

### 1.1 ✅ The must-fire the task named — `.temp/php9/a1_row_enum.py` case 3

Re-run **unmodified**. `.temp/php10/03-a1-rowenum.log`, diffed against the
reviewer's `.temp/php9/03-row-enum.log`: **exactly one case moved.**

```
=== (3) ⚠ A DOTTED ROW DIRECTORY -- `glob` never matches a leading dot ===
  PASS     ph93-dotted          refused=True  expected=True          <- was ⚠⚠ HOLE
           | allocator: .ph93-dotted: .ph93-dotted/c/emalloc_shim.h IS ABSENT.
           | digest: .ph93-dotted: A DOTTED ROW DIRECTORY HAS NO SANCTIONED FORM -- rename it...
           os.listdir sees the row : True
           glob sees the row       : False
```

⚠ **Case (6) still reports `⚠⚠ HOLE` and that is unchanged and benign** — a row
with no `c/` is skipped, which `TASK_PHP_009` §7 clean negative 15 already
settled (`build.py` compiles exactly `common/driver.c`, `<row>/c/<kernel>` and
`<row>/c/main.c`, so a row without `c/` builds no C). It is the probe's
expectation that is wrong, not the audit; I did not change the probe.

### 1.2 ✅ END TO END on the real tree — `.temp/php9/a10_dotted_e2e.py`, rc 0 → 2

Re-run unmodified. `.temp/php10/13-a10-dotted-e2e.log`:

```
=== the REAL gate, on the dotted row ===
      FAIL every patterns-php/*/c/ file has a digest key (RECAP_PHP.md open item 17)
           | digest: .ph93-dotted: A DOTTED ROW DIRECTORY HAS NO SANCTIONED FORM -- rename it...
           | digest: .ph93-dotted: c/sub/payload.h is COMPILED and in NO DIGEST.
      FAIL <row>/c/emalloc_shim.h symlink, UNCONDITIONAL (PROTOCOL_PHP.md §B2, TASK_PHP_008 §0)
      ok   every php record has a CERTIFYING preflight record beside it (scope: .ph93)
    PREFLIGHT FAILED -- the tool was NOT run:
    rc=2                                        <-- TASK_PHP_009 measured rc=0

RESTORE: results-php/ exact = True   patterns-php/ listing unchanged = True
```

Both defects the reviewer planted are now named, and the row is refused by name
as well. The plant is restored byte-exactly.

### 1.3 ✅ Attribution — the two enumerations differ by the dotted rows and by NOTHING else

New probe `.temp/php10/p5_enum_equiv.py`, log `17-enum-equiv.log`. This is what
makes *"no other probe result moved"* checkable rather than asserted:

```
  PASS      patterns-php/ (real, read-only)    old=  1 new=  1  new-only=[]  old-only=[]
  PASS      patterns/ (real, read-only)        old= 33 new= 33  new-only=[]  old-only=[]
  PASS      fixture, NO dotted row             old=  2 new=  2  new-only=[]  old-only=[]
  PASS      fixture + .ph03-hidden + __pycache__ old=  3 new=  3  new-only=['.ph03-hidden']  old-only=['__pycache__']

=== the invariant: build.py resolves every row _row_dirs returns ===
  PASS      build.pattern_dir('ph01-a'        ) -> ph01-a
  PASS      build.pattern_dir('ph02-b'        ) -> ph02-b
  PASS      build.pattern_dir('.ph03-hidden'  ) -> .ph03-hidden
```

⚠ `__pycache__` as `old-only` is deliberate and is not a verdict change: the old
glob returned it and both audits then skipped it for having no `c/`.

### 1.4 The dotted-row refusal, and why it is a refusal and not a repair

The record half **cannot** be repaired from `harness-php/`:
`harness/measure.py:303` — frozen, hashed into all 33 PAT measurement records —
globs `results/p*.json` + `results/gate/p*.json`, and `.ph93-dotted.json` matches
neither. So `--check-stale` would examine every other record, print `0 STALE`,
and never have looked at that row. That sentence is in the refusal message.

✅ **`why_band` is unchanged across the enumeration swap** — the published PAT
band is byte-for-byte the same, which is the regression that would have been
easy to miss:

```
why_band PAT: {'n': 33, 'min': 197, 'median': 989, 'p90': 1817, 'max': 3140}
```

---

## §2 M2 — an upward include escapes both digests

**Fixed by refusing any directory under `<row>/` outside `{c, inputs, controls}`
(+ `__pycache__`).** No `gcc -MD`; the reason is in the function's docstring.

### 2.1 ✅ The must-fire — `.temp/php9/a2_upward_include.py`, re-run unmodified

`.temp/php10/04-a2-upward.log`:

```
=== (1) does the PREFLIGHT pass? ===
  c_digest_audit  problems : 1
    | digest: ph98-upward: ph98-upward/aux/ IS NOT A SANCTIONED ROW DIRECTORY...
  -> PREFLIGHT WOULD PASS: False              <-- TASK_PHP_009 measured True

=== (4) EDIT THE ROW'S ALLOCATOR. Does any recorded hash move? ===
  preflight problems after the edit  : 1      <-- was 0

composition did not land: ...                 <-- was ⚠⚠ COMPOSITION LANDS

=== (5) MUST FIRE -- the same header one directory over, under c/ ===
  c/sub/row_alloc.h -> c_digest_audit problems: 2
    | digest: ph98-upward: ph98-upward/aux/ IS NOT A SANCTIONED ROW DIRECTORY...
    | digest: ph98-upward: c/sub/row_alloc.h is COMPILED and in NO DIGEST.
```

⚠ **On the task's *"case (5) is the must-NOT-fire"*:** case (5) is a
**must-FIRE** in that probe and still fires — `c/sub/row_alloc.h` is refused by
the `c/` walk exactly as before. It is a **must-NOT-fire for the NEW check**,
and it does not fire: the second line above comes from the pre-existing walk and
the whitelist says nothing about `c/sub/`. Both readings verified; see §7.3.

### 2.2 ✅ Is it over-strict? — 33 built PAT rows, read-only

`.temp/php10/p1_row_layout.py`, log `05-outside-row.log`:

```
=== MUST NOT FIRE -- the sanctioned shapes ===
  PASS      c/ only                                      fires=False want=False
  PASS      c/ + inputs/ + controls/                     fires=False want=False
  PASS      __pycache__ (every PAT row has one)          fires=False want=False
  PASS      §B3 tarball mirror: c/zend/ + flat symlink   fires=False want=False
            c_digest_audit on that row: 0 problem(s) -- the §B3 layout is still AVAILABLE AND PRICED

=== MUST FIRE ===
  PASS      <row>/aux/  (TASK_PHP_009 M2's shape)        fires=True  want=True
  PASS      <row>/extract/  (the 'natural php layout')   fires=True  want=True

=== ⚠ IS IT OVER-STRICT? All 33 BUILT PAT rows, read-only ===
    rows examined                : 33
    directory names in the corpus: {'__pycache__': 33, 'c': 33, 'inputs': 33, 'controls': 28}
    rows the whitelist REFUSES   : 0  []
    -> the whitelist admits every built PAT row
```

⚠⚠ **`{'__pycache__': 33}` is the refutation of the fix as specified** — see §7.2.

**Answer to §6 call 2, in one line: no plausible fourth directory, but the
whitelist as literally specified was one exemption short of refusing the entire
corpus.** The one layout the reviewer named as *"natural"* — `<row>/extract/Zend/…`
— is refused **on purpose**, and its sanctioned form costs one directory level:
`c/extract/Zend/…` plus a flat symlink per file, which `PROTOCOL_PHP.md` §B3
already prices and which the `ph63-mirror` case above proves still passes.

### 2.3 ⚠⚠ What the whitelist does NOT bound — measured, reported, NOT fixed

`.temp/php10/05-outside-row.log`, last block:

```
=== ⚠⚠ WHAT IT DOES **NOT** BOUND: `..` TWICE LEAVES THE ROW ===
    c/kernel.c includes ../../shared/row_alloc.h
    gcc rc=0   ./bin -> tally=7   (7 = the OUTSIDE allocator ran)
    the row's digest keys           : ['c/emalloc_shim.h', 'c/kernel.c']
    'shared/row_alloc.h' keyed      : False
    c_digest_audit refuses this row : False   <-- ⚠ NO
    `shared` enumerated as a row    : True (no c/ -> both audits skip it)
```

**`#include "../../shared/x.h"` from `<row>/c/` reaches `patterns-php/shared/x.h`,
compiles, runs, and is in neither digest — and it is not a directory under the
row, so nothing here sees it.** `../../../extract/…` reaches the repo root the
same way. This is `TASK_PHP_009` M2 with one more `..`, it is **latent on both
sides today** (no row has such an include), and per §0 of the task I am
**reporting it and not fixing it**. It is written into `_row_layout_problems`'s
docstring and into `PROTOCOL_PHP.md` §B3a so the next author is not told the
guard is stronger than it is.

⚠ **My honest view of the price**, for the manager to schedule or refuse: the
cheap bounded version is *"refuse a `..` that leaves `<row>/c/`"* computed from
`os.path.realpath` of every `#include "..."` target — but that needs to parse
includes, which is the idiom-enumeration class the programme deleted twice. The
version with no spelling is the compiler's own `-MD`, which needs a `build.py`
edit and a 33-pattern re-measure. **I do not recommend either now.** The
discipline (`<row>/c/` holds everything the row compiles, checked by eye in
review) costs nothing and is now written down.

---

## §3 M3 + M4 — one change, and it does close both, but not in the shape the task assumed

`preflight_coverage_audit(row=None)` returns `(problems, notes)`: **problems are
the row in hand's**, everything else is a **note that is printed and recorded and
does not fail the run**. `gate.py --audit` reports `problems + notes` and exits 1
on either, so the global question still has a command that asks it.

### 3.1 ✅ The generator the task named, re-run — `.temp/php9/a4_orphan_deadlock.py`

`.temp/php10/06-a4-orphan.log`. **Four rc values moved; every one of them is the
deadlock:**

```
=== (1) PLANT an orphan record ===
    gate.py --preflight ph00  ->  rc=0                      <-- was rc=2
      | | ⚠ OTHER ROW, not failed here: preflight coverage: results-php/ph99-ghost.json has NO preflight record...

=== (2) FOLLOW THE PRESCRIBED REPAIR, verbatim ===
    gate.py --preflight ph99  ->  rc=2                      (unchanged, and CORRECT)
      | (b) the row was RETIRED and its records outlived it (`PLAN_PHP.md` §3 expects retirement). Then (a) CANNOT succeed...

=== (3) THE LOOP ===
    cycle 1: repair rc=2   ph00 preflight rc=0   ...        <-- ph00 was rc=2
    cycle 2: identical     cycle 3: identical

=== (4) is the mandated BRACKET blocked too? ===
    gate.py --tool measure --check-stale  ->  rc=0          <-- was rc=2
      last line: 3 record(s) examined, 0 STALE

=== (5) delete the orphan record ===
    after `rm results-php/ph99-ghost.json`: rc=0

RESTORE EXACT (sha256 per file, 7 file(s)): True
```

⚠ **The probe's narration line still prints *"DOES NOT CONVERGE"*. It is a
hard-coded `print`, not a measurement**, and its own numbers on the line above
contradict it. See §7.4 — *"converges"* is the wrong word for this state and the
right thing happened.

### 3.2 ✅ The control, because the fix must be attributable — `.temp/php10/p2_scope_arms.py`

`07-m3m4.log`. Arm A drives the **old global rule** on the same fixture:

```
=== arm A -- CONTROL: the GLOBAL rule (problems + notes) ===
    cycle 1..5: gate.py <ph00> under the GLOBAL rule -> 2 problem(s) -> PREFLIGHT FAILED
    -> ⚠⚠ DOES NOT CONVERGE after 5 cycles -- CONTROL FIRED

=== arm B -- SHIPPED: per-row scope ===
    gate.py ph00      -> 0 problem(s), 2 other-row note(s)  ->  PASSES
    the BRACKET (no row) -> 0 problem(s), 2 note(s)  ->  PASSES
    gate.py ph99 (the RETIRED row itself) -> 1 problem(s)  ->  FAILS -- correct
    its message NAMES THE DELETION REPAIR : True
    the words 'THERE IS NO DEADLOCK' gone : True
    --audit (global, by construction)     : 2 problem(s) -> exit 1
```

### 3.3 ⚠ §6 call 1, answered with a measurement: **does per-row scope close M4 too?**

**Yes for the half that was a deadlock, and the other half was never a coverage
problem at all.** Same log, and `.temp/php10/08-a5-cap.log` for the provenance half:

```
=== ⚠ §6 call 1 -- does per-row scope close M4 as well as M3? ===
    (a) does ph70's HOLLOW record block OTHER rows?   NO -- closed
    (b) does it block the mandated bracket?           NO -- closed
    (c) does gate.py ph70 itself still fail?          YES  (1 problem(s))

.temp/php10/08-a5-cap.log  (.temp/php9/a5_notarball_and_cap.py, unmodified):
=== (a) a php-provenance row on a box with NO TARBALL ===
    check_row(use_tarball=True)  ok=False
      | ph70-fixture: tarball not found at /nonexistent/php-5.0.0.tar.gz...
```

⚠ **So (c) is not the coverage stage's doing.** On a tarball-less box that row's
**provenance stage** fails it directly, with or without a coverage stage — which
is the intended, loud behaviour, not a deadlock: nothing about it is
self-referential and no repair loop is prescribed that cannot work. **No separate
fix is owed for a deadlock.** What remains is a policy question the manager
should decide *when a box without the tarball actually needs to re-gate*, and I
priced it rather than doing it:

> **Option (not implemented):** forward `--no-tarball` from `gate.py` to
> `provenance.py` and let such a run certify with a recorded
> `tarball_skipped: true`. **Price: ~15 lines** (an argparse flag, one forward,
> one record field, one `_run_is_certifying` clause) **plus a must-fire control,
> ~1 hour.** ⚠ **Cost of taking it:** it is a second `--no-provenance`, one notch
> weaker, and `PROTOCOL_PHP.md` §D's whole argument for `extract_sha256` is that
> the tarball is what makes provenance a check rather than a claim. **I recommend
> not adding it until it blocks someone**, and the current failure is loud enough
> that it will be obvious when it does.

### 3.4 ✅ The §8b repair still holds under the new scope — and its control had to be rebuilt

⚠⚠ **`.temp/php8/g4_selfdeadlock.py` — the must-fire control for the
TASK_PHP_008 §8b repair — CAN NO LONGER FIRE**, because it calls
`preflight_coverage_audit()` **with no row**, so under the per-row scope both
arms converge at run 1 (`.temp/php10/11-regressions.log`):

```
  naive rule deadlocks : False   ⚠ the probe cannot see a deadlock
```

**A control that cannot fire is the silent-skip class**, so I re-asked the
question in the scope where it is live. `.temp/php10/p4_selfdeadlock_scoped.py`
is g4 verbatim with `preflight_coverage_audit("ph01")` — g4's own scenario is
`ph01`'s record, so `ph01` *is* the row in hand. `12-selfdeadlock-scoped.log`:

```
--- (a) MUST FIRE -- the naive rule, per-row scope
    run 1..6: coverage problems BEFORE the write = 1   verdict = 'PREFLIGHT FAILED'
    -> STILL FAILING after 6 runs. ⚠⚠ DEADLOCK.
--- (b) MUST NOT FIRE -- the rule actually shipped, per-row scope
    run 2: coverage problems BEFORE the write = 0   verdict = 'preflight only'
    -> CONVERGED after 2 run(s). NO DEADLOCK.
  naive rule deadlocks : True   CONTROL FIRED
  shipped rule converges: True
```

**Identical to the reviewer's numbers.** The `_COVERAGE_TAG` discount is
untouched and still necessary.

### 3.5 The message that asserted its own absence

Deleted. What replaces it names **both** repairs and says which is which:

```
       Fix, and there are TWO -- pick by WHY the record is here:
         (a) the row EXISTS and the run did not go through gate.py:
             python3 harness-php/gate.py --preflight <row>
         (b) the row was RETIRED and its records outlived it (`PLAN_PHP.md` §3
             expects retirement). Then (a) CANNOT succeed -- provenance fails on
             a row that is not there, which is a SUBSTANTIVE problem, so the run
             it writes never certifies. DELETE the records instead, in the same
             commit as the row:
             git rm results-php/<row>.json results-php/gate/<row>.json
```

A comment block above it records that this is **the third instance of one class
in three tasks** (`"CANNOT BE"`, `"dead code … Not treated as a shim user"`,
`"THERE IS NO DEADLOCK"`) and says *name the repairs; do not certify the absence
of a problem*.

---

## §4 The minors — all six, with the cap measured on the class that accumulates

### m1 ✅ exact match, not a prefix glob

`.temp/php10/p3_minors.py`, log `10-minors.log`:

```
=== m1 -- the record/preflight match is EXACT, not a prefix ===
  PASS      MUST FIRE: only ph100 exists; ph10 is NOT covered by it     problems=1
  PASS      MUST NOT FIRE: the id spelling  ph10.preflight.json         problems=0
  PASS      MUST NOT FIRE: the SLUG spelling ph10-victim.preflight.json problems=0
  PASS      MUST FIRE: nothing at all beside the record                 problems=1
```

⚠ **`.temp/php9/a3_coverage.py` §5 can no longer measure this** — it calls the
audit with no row, so its `covered = not bad` is now True for a different reason.
Its §5 line is stale evidence; `p3_minors.py` is the replacement. (§7.5.)

### m2 ✅ the cap now bounds the class that accumulates

The task said *"fix the cap or justify the exemption with the state modelled"*.
**I fixed it**, because the state the exemption protects (F-2a, a `--no-provenance`
run erased) and the state that accumulates (a repair session where every run
fails) are the same class and only one of them can win a bound. Priority order:
**first + last, then evidence-carrying newest-first, then everything else** — so
evidence is a *preference*, not an *exemption*, and an evidence entry is dropped
only past 40 distinct stored runs. `10-minors.log`:

```
=== m2 -- MAX_RUNS is an ABSOLUTE bound now ===
  PASS  no problems (the class the cap ALREADY bounded  n= 1000 -> kept   40  dropped  960  evidence dropped    0  first+last kept: True
  PASS  ⚠ CARRYING EVIDENCE (the class it exempted)     n= 1000 -> kept   40  dropped  960  evidence dropped  960  first+last kept: True
  PASS  ⚠ coverage-only failures (M3's state)           n= 1000 -> kept   40  dropped  960  evidence dropped  960  first+last kept: True

    MUST NOT FIRE -- F-2a's case
  PASS  120 distinct no-problem runs -> kept 40, dropped 80; the provenance_skipped entry survived: True

    ⚠ THE TRADE, DISCLOSED
    runs stored             : 40
    _dropped_runs           : 161
    _dropped_evidence_runs  : 161   <-- the erasure is VISIBLE, not silent
```

The reviewer's own generator, re-run unmodified (`08-a5-cap.log`), shows the same
from the other side — **1000 evidence-carrying runs now keep 40, not 1000** —
and its must-NOT-fire (120 clean runs → 40, `provenance_skipped` survives) still
holds.

⚠ **Disclosed trade, in the code and here:** past 40 distinct stored runs an OLD
evidence entry *can* now be dropped, which the exemption existed to prevent. It
is counted in a new `_dropped_evidence_runs` field, so the erasure is in the
record rather than silent. ⚠ **`_collapse_and_cap`'s return shape is unchanged**
(the new count goes through an optional `stats` dict) precisely so that
`.temp/php8/g3_*` and `.temp/php9/a5_*` — the controls this fix is measured
against — still run.

### m3 ✅ `PROTOCOL_PHP.md` §E: *"still matches **or has been deleted**"*

Added, with the reviewer's measurement (a pinned-but-deleted source prints
`FRESH` **and** `MISSING` and exits 0) and the note that the bracket quotes the
summary line, which is exactly where that does not show.

### m4 ✅ the dangling citation, in both places

`gate.py` and `root.py` now cite `.tasks-php/TASK_PHP_002_REPORT.md:290-295` —
the pasted output, which exists — and say the probe tree was deleted under
`.memory/00-environment.md` constraint 6. ⚠ I did **not** edit
`TASK_PHP_002_REPORT.md`: it is the historical record and the destination of the
citation.

### m5 ✅ *"a failing run is not read-only"*, and I reproduced it accidentally

A row in `PROTOCOL_PHP.md` §E's table, plus a paragraph in
`write_preflight_record`. ⚠⚠ **And it bit me during this task, which is the best
evidence for it**: re-running `.temp/php4/b1_symlink_test.py` (a regression
check) planted a fixture row, ran the real gate, and appended **two runs about a
row that never existed** to the committed `results-php/preflight/ph00.preflight.json`
(+117 lines). Caught by `git status` in the same output, restored byte-exactly
(`.temp/php10/15-restore-residue.log`, `16-php4-b1.log`):

```
before  f2556e68d3da4a25...   after  0e880916f3182b96...   == git show HEAD:  0e880916f3182b96...
```

### m6 ✅ the FIFO comment

Beside the `os.path.isfile` filter in `c_digest_audit`: `sha256_file` on a FIFO
blocks for ever with no timeout, `isfile` is what keeps it out of the key set,
`_walk_files` still yields it so the row is refused — *"do not 'fix' this filter
to `os.path.exists`"*.

---

## §5 Regressions — everything I could re-run, re-run

| probe | result |
|---|---|
| `.temp/php9/a8_digest_audit.py` (10 `c/` fixtures) | ✅ **ALL AS EXPECTED**, unchanged — dotfile, dot-dir, dir-symlink, nested, link-out, broken link, FIFO, cycle, 2 must-NOT-fires (`11-regressions.log`) |
| `.temp/php8/g2_digest_audit.py` (8 fixtures + cycle) | ✅ **8/8 landed as expected** (`14-regressions2.log`) |
| `.temp/php9/a3_coverage.py` | ✅ §3's five behavioural cases **5/5 PASS**; §5 no longer measurable (§7.5) |
| `.temp/php8/g4_selfdeadlock.py` | ⚠ control can no longer fire — replaced by `p4` (§3.4) |
| `.temp/php9/a1`, `a2`, `a4`, `a5`, `a10` | ✅ the four must-fires moved and nothing else did (§1–§4) |
| `.temp/php4/b1_symlink_test.py` | ⚠ **`5 FAILED`, and every one attributed to pre-existing staleness — none to this task** (§7.6) |
| the real tree | `gate.py --audit` → `preflight coverage: complete`, rc=0; `gate.py --preflight ph00` → all stages ok, rc=0; `gate.py --preflight` (no row) → `(scope: none -- no row named; --audit asks this globally)`, rc=0 (`18-preflight-real.log`, `21-rowless-scope.log`) |

---

## §6 The three calls the manager was least sure of

**1. Does per-row coverage close M4 as well as M3?** — **Yes for the deadlock,
and M4's remainder was never a coverage problem.** Measured in §3.3: the hollow
record no longer blocks other rows or the bracket; the row itself is failed by
the **provenance stage**, directly, which is intended. The separate fix is priced
in §3.3 and I recommend **not** taking it yet.

**2. Is `{c, inputs, controls}` over-strict?** — **Not for any layout this
project has ever used (33/33 PAT rows admitted), and it was one exemption short
of refusing all of them.** ⚠⚠ `__pycache__` exists in **33 of 33** rows; the
whitelist as written in the task would have refused the entire corpus and every
php row the moment a `model.py` is imported. Shipped with `__pycache__` exempt.
**No plausible fourth directory**: the one the reviewer named (`<row>/extract/`)
is refused deliberately and its sanctioned form is `c/extract/…` + flat symlinks
(measured to pass). ⚠ **The real weakness is not strictness, it is reach** —
§2.3, `..` twice.

**3. Did the task stay small?** — **Yes, and I stopped where §0 said to.** One
code file (+1 comment in `root.py`), one doc file, no new preflight stage, no new
gate stage, no re-gate, no re-measure, ~25 minutes of runs. ⚠ **What grew and
why:** I wrote **five** probes rather than reusing four, because **three of the
reviewer's controls stopped being able to fire** once the coverage stage took a
scope (g4, a3 §5) or measured a shape the fix creates (the cap, the layout).
Rebuilding a control that the fix disabled is not scope growth — leaving it
disabled would have been the defect. **I found one adjacent hole (§2.3) and did
not fix it.**

---

## §7 What I correct, and what I could not do as written

**Launched from 26. Reconciliation is the manager's, not mine.**

### Against the TASK FILE (4)

1. ⚠⚠ **§2's whitelist, as literally specified, refuses every row in the
   project.** *"Refuse any directory under `<row>/` outside `{c, inputs,
   controls}`"* — **33 of 33 built PAT rows carry a `__pycache__/`**
   (`05-outside-row.log`), created by Python whenever a `model.py` or an
   `inputs/gen.py` is imported. Shipped with `__pycache__` exempt, and the
   exemption is in `ROW_DIRS`'s comment so the next reader does not remove it.
   ⚠ **This is the same shape as the whitelist mistake the manager warned about
   in §6 call 2 — and it was in the fix, not in a future row.**
2. ⚠⚠ **§3's *"show it converges"* asks for the wrong outcome, and the right one
   happened.** An orphan record from a **retired** row must **never** converge by
   repetition — repeating `--preflight <retired-row>` is exactly the loop the
   reviewer showed cannot work, and it still exits 2. What the fix does is
   **stop it blocking**: `gate.py <other-row>` and the bracket go rc=2 → **rc=0**,
   and the retired row's own message now names `git rm` as the repair. ⚠ *"It
   converges"* would mean the wrong thing had been built.
3. ⚠ **§2's *"`a2`'s case (5) is the must-NOT-fire"* is half right.** Case (5) is
   a **must-FIRE** for `c_digest_audit` (it still fires) and a **must-NOT-FIRE**
   for the new whitelist (it does not fire). Both measured (§2.1, §2.2's
   `§B3 tarball mirror` row) — worth stating because a reader chasing "case 5
   must not fire" against the a2 log would see `problems: 2` and think the fix
   was wrong.
4. ⚠ **§4 cites *"`TASK_PHP_009` §7's minors"*; §7 is the CLEAN NEGATIVES.** The
   minors are §11 (m1–m6). I landed §11's six.

### Against the CODEBASE / earlier evidence (2)

5. ⚠⚠ **`_collapse_and_cap`'s `MAX_RUNS` was never a bound, and the reviewer's
   `m2` understates it slightly**: it is not only *evidence-carrying* runs that
   escaped — `_carries_evidence` is true of any run with a non-empty `problems`
   **or** a `PREFLIGHT FAILED` verdict **or** a `shim_repaired` **or** a
   `_schema`, i.e. of every run in a failing tree, which is the tree you are in
   while repairing. Fixed, with the trade disclosed and counted.
6. ⚠ **`.temp/php4/b1_symlink_test.py` reports `5 FAILED` on a healthy tree, and
   has since `TASK_PHP_008`.** Attributed, in full (`16-php4-b1.log`): three
   expectations encode the **TASK_PHP_004 detector** semantics that
   `TASK_PHP_008` §0 replaced (`ph95-noShimNoLink` *"PASSES, no false positive"*
   — under the unconditional rule it is correctly REFUSED; `ph96-orphanLink`;
   *"exactly THREE rows refused"*, now four); one reads
   `allocator_symlink_ok` at the **top level** of a preflight record, where it
   stopped living at `TASK_PHP_006` when the file became `{"row":…, "runs":[…]}`;
   one is `git status unchanged`, which cannot hold while any task is in
   progress. ⚠ **None is caused by TASK_PHP_010** — proved independently by
   §1.3: on a tree with no dotted rows the two enumerations are the same list, so
   no verdict can differ. **Not fixed** (frozen scratch, and out of scope).

### Upheld against my own attempts to break them (3)

7. ✅ **The `_COVERAGE_TAG` discount survives the scope change** — `a3`'s five
   behavioural cases still 5/5, and `p4` shows the naive rule still deadlocks and
   the shipped one still converges, per-row.
8. ✅ **The published PAT `why` band does not move** across the enumeration swap:
   `n=33, median 989, p90 1817, max 3140`, identical.
9. ✅ **`c_digest_audit`'s file-level exhaustiveness is untouched** — all ten of
   the reviewer's fixtures and all eight of `TASK_PHP_008`'s behave exactly as
   recorded.

### A near-miss in my own work, disclosed (1)

10. ⚠ **I wrote the coverage emitter as
    `(problems if mine else notes).append(text)`, which is INVISIBLE to
    `TASK_PHP_009` §2.2's AST scan** over every `problems.append`/`.extend` —
    the scan that verified the discount cannot be widened. Its output silently
    went from `['_COVERAGE_TAG']` to `[]`, which reads like a stronger result and
    is actually a blind one. **Caught by re-running `a3` and reading the diff**;
    respelled as two explicit `.append` calls, with a comment saying why. ⚠ The
    scanner still cannot resolve the message (it now reports `Name(id='text')`),
    so **the behavioural cases in `a3` §3, not the AST list, are what measure
    this property now.**

---

## §8 Adjacent, found, NOT fixed (§0 of the task)

1. ⚠⚠ **`..` twice leaves the row** (§2.3) — compiles, runs, in no digest, not
   refused. Measured. Written into the code docstring and `PROTOCOL_PHP.md` §B3a.
2. ⚠ **A non-row directory under `patterns-php/` is enumerated as a row with no
   `c/` and skipped by both audits** — which is benign as a *build* target
   (clean negative 15) and is **not** benign as an *include* target (item 1).
   The two interact; neither is closed.
3. ⚠ **`.temp/php4/b1_symlink_test.py` is stale in four ways** (§7.6). A probe
   that always says `5 FAILED` trains the reader to ignore it.
4. ⚠ **`.temp/php8/g4_selfdeadlock.py` and `.temp/php9/a3_coverage.py` §5 now
   measure nothing** (§3.4, §4/m1). Replacements exist under `.temp/php10/`; the
   originals are untouched, as the task requires.
5. ⚠ **`TASK_PHP_009` §4.4's suggestion — one line in §E noting that through
   `gate.py` the DIGEST BRIDGE stage fires before `--check-stale`, so a shim edit
   surfaces as `PREFLIGHT FAILED` and not as `2 STALE`** — is **not landed**. It
   is not one of the six numbered minors and I did not widen to it.
6. ⚠ **`uses_allocator` per-row tally evidence** (`TASK_PHP_009` §6.3's
   suggestion for §F item 6) — not landed, same reason.

---

## §9 What I did NOT do, and what I am unsure about

- **I did not run a full gate (`gate.py ph00`, ~24 min) or a re-measure.** Not
  owed: `harness-php/*.py` is in **no** digest — the gate record's 29 source keys
  and the measurement record's keys contain zero `harness-php` entries
  (`22-no-digest.log`) — and the closing bracket reads `2 record(s), 0 STALE`.
  ⚠ **If the manager wants belt-and-braces, the command is `gate.py ph00`** and I
  did not spend the 24 minutes.
- **I did not edit `RECAP_PHP.md`, `.memory/`, `harness/`, `common/`,
  `patterns/`, `results/` or `pilot/`.** Proved by bytes against five snapshots
  with the control fired.
- ⚠ **Two committed preflight records grew, and every appended entry is MINE,
  CLEAN, and from a real command** — audited leaf by leaf rather than asserted
  (`20-record-delta.log`, `23-record-audit.log`):

  ```
  grep -c 'zzz-b1probe|ph93-dotted|ph99-ghost|ph98-upward'  ->  0  0   (no fixture residue)

  ph00.preflight.json:   HEAD 11 runs -> now 12
     appended run[11]: verdict='preflight only' tool='check'  problems=0 other_rows=0 argv=['--preflight','ph00']
     HEAD runs still present, in order, unchanged: True
  _norow.preflight.json: HEAD  5 runs -> now  7
     appended run[5]: verdict='tool exited'    tool='measure' problems=0 other_rows=0 argv=['--tool','measure','--check-stale']
     appended run[6]: verdict='preflight only' tool='check'   problems=0 other_rows=0 argv=['--preflight']
     HEAD runs still present, in order, unchanged: True
  ```

  They did not collapse because `harness_php_sha256` moved with my edit — which
  is the record working as designed. **The fixture-row residue from
  `.temp/php4/b1_symlink_test.py` was restored byte-exactly and is NOT among
  them.** ⚠ `16-php4-b1.log` was truncated on the console side by a `head -60`
  (SIGPIPE cut `tee`); the restore's verification is appended to that log by
  hand and says so.
- ⚠ **M2's fix is a directory whitelist, so it is exactly as good as its
  enumeration of the row's own directories** — one `os.listdir`, which is finite,
  but §2.3 is the honest boundary and I would rather the manager priced it than
  discovered it.
- ⚠ **I did not attack the per-row scope from the direction of `--audit` being
  forgotten.** The global question now lives in a command nobody is obliged to
  run; the preflight still prints every other row's finding on every invocation,
  which is the compensating control, but *printed* is weaker than *failed* and I
  am naming the trade rather than hiding it.
- **I did not model a `results-php/gate/<row>.json` whose stem differs from its
  measurement record's stem.** `_row_key` splits on `-`, so `ph10-victim` and
  `ph10` key the same; a row whose id contains no `-` and whose slug does is the
  only shape I did not build.
- **I did not re-run `.temp/php5–php7`'s generators** beyond `php4/b1` and
  `php8/g2`, `php8/g4`. They measure deleted machinery or PAT-side properties my
  change cannot reach.

## §10 Memory updates

**None** — `.memory/` is the manager's under `PROTOCOL.md` rule 4/9, and
`RECAP_PHP.md` is manager-only. Durable facts I would lift are in §7 and §8;
`PROTOCOL_PHP.md` §B3a, §E already carry the two that are procedural.
