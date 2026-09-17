# PROMOTE_001 — five probes and their generator, out of `.temp/` and into `.tasks-php/probes/`

**Chore, not a research round.** Six published findings rested on scripts that
existed only under gitignored `.temp/`. `.memory-php/04-process.md` **law 11**:
*a published finding whose only evidence is a gitignored probe is a finding that
will not survive a clean checkout.* All six files are now committed-tree
resident, registered in `.tasks-php/checkers.py`, and `CHECKERS PASS`.

⚠⚠ **THE DISTINCTION THAT SHAPED EVERY JUDGEMENT CALL HERE.** A **script** in
scratch is the defect. A re-derivable **artefact** in scratch is **the rule**
(`CLAUDE.md` Don't #1, *keep the generator, delete the artefact*). ▶ **No
callgrind profile was committed.** The cache paths still point at
`.temp/mgr172/cg/`. What was repaired is that two probes **CRASHED** when that
cache was absent instead of saying they could not run.

---

## §1 Per file — what changed, and the before/after `--selftest` rc

Every rc below is measured, not assumed. "before" is the file at its `.temp/`
path immediately before the copy; "after" is the committed path.

| file | before | after | what changed |
|---|---|---|---|
| `.tasks-php/probes/identity_null.py` | **rc=0** (0.12 s) | **rc=0** (0.12 s) | promotion header; `Run:` lines → committed path; the `.temp/mgr170/null_control.py` cross-citation → `.tasks-php/probes/null_control.py` |
| `.tasks-php/probes/inclusive_ir.py` | **rc=0** (1.65 s) | **rc=0** (1.79 s) | promotion header; three `Run:` lines → committed path; ⛔ **cache guard added** (`missing_inputs` / `report_not_run`) |
| `.tasks-php/probes/bc_sweep.py` | **rc=0** (8.64 s) | **rc=0** (8.50 s) | promotion header; `Run:` lines → committed path; `sweep_cg.sh` citation → `.tasks-php/probes/sweep_cg.sh`; ⛔ **cache guard added**; ⛔ **one false count corrected in the docstring — see §4.1** |
| `.tasks-php/probes/flip_exact.py` | **rc=0** (0.07 s) | **rc=0** (0.07 s) | promotion header; `Run:` lines → committed path; the `callee_share.py` citation marked as **uncommitted scratch** |
| `.tasks-php/probes/null_control.py` | **rc=0** (0.09 s) | **rc=0** (0.09 s) | promotion header; `Run:` lines **added** (it had none); the `.temp/mgr170/callee_share.py` citation marked as **uncommitted scratch, not promoted, does not exist on a clean checkout** |
| `.tasks-php/probes/sweep_cg.sh` | n/a — no self-test | n/a; `sh -n` OK | promotion header; the `bc_sweep.py` / `inclusive_ir.py` / `STATISTIC-DECISION-DRAFT.md` citations qualified; the `ph45` exclusion re-stated as a **standing gap** (TASK_PHP_037 has landed) |

Bare runs also measured **rc=0** on all five `.py` from the committed path.

⭐ **`ROOT` needed no change, as briefed** — `dirname(dirname(dirname(abspath(
__file__))))` is the repo root from `.tasks-php/probes/` exactly as it was from
`.temp/mgr172/`. Confirmed by every run above resolving `results-php/`.

**The `.temp/` originals were copied, not moved, and are untouched.**

### What each file still needs that is NOT committed — stated, not discovered

| file | uncommitted dependency |
|---|---|
| `identity_null.py` | ✅ **none.** `results*/`, `patterns/p25-realloc-growth/spec.md`. Writes nothing. |
| `flip_exact.py` | ✅ **none.** `results-php/` only. Writes nothing. |
| `null_control.py` | ✅ **none.** `results-php/` only. Writes nothing. |
| `inclusive_ir.py` | ⛔ 11 gitignored files: 8 profiles + 3 `envctl.*` under `.temp/mgr172/cg/`, **plus** the build trees `.temp/php-root/.temp/build/ph03/` and `.temp/build/p25/` |
| `bc_sweep.py` | ⛔ 24 gitignored profiles under `.temp/mgr172/cg/`, **plus** 12 binaries under `.temp/php-root/.temp/build/` |
| `sweep_cg.sh` | ⛔ the php build trees, the **pinned** valgrind at `~/tools/valgrind/`, and ⛔⛔ a **hardcoded absolute `R=`** — see §4.3 |

---

## §2 The cache-guard transcripts — measured, verbatim

Method: `mv .temp/mgr172/cg .temp/mgr172/cg_HELD`, run both arms of both probes,
`mv` back, re-run. **The cache is restored** (39 files, verified;
`.temp/mgr173/cg` also verified at 80 — see §4.4 for why it was touched).

### 2.1 `inclusive_ir.py` — cache ABSENT

Both `--selftest` and the bare run produce **byte-identical output** and
**rc=0**:

```
### inclusive_ir.py --selftest  (CACHE ABSENT)
==============================================================================
⛔⛔ NOT RUN -- NO VERDICT WAS REACHED. THIS IS NOT A PASS.
==============================================================================
  11 input(s) this script reads are ABSENT. Every one of
  them is GITIGNORED and RE-DERIVABLE, so their absence is the
  expected state of a clean checkout and not a fault -- but it means
  THE CHECK COULD NOT RUN, WHICH IS ITSELF A RESULT TO REPORT
  (the rule .tasks-php/width.py's X3 already follows).

    missing  .temp/mgr172/cg/envctl.0.out
    missing  .temp/mgr172/cg/envctl.200.out
    missing  .temp/mgr172/cg/envctl.4000.out
    missing  .temp/mgr172/cg/p25.unsafe.large.out
    missing  .temp/mgr172/cg/p25.unsafe.small.out
    missing  .temp/mgr172/cg/p25.verus.large.out
    missing  .temp/mgr172/cg/p25.verus.small.out
    missing  .temp/mgr172/cg/ph03.unsafe.large.out
    missing  .temp/mgr172/cg/ph03.unsafe.small.out
    missing  .temp/mgr172/cg/ph03.verus.large.out
    missing  .temp/mgr172/cg/ph03.verus.small.out

  REBUILD THEM (none of this is committed, by design):
    sh .tasks-php/probes/sweep_cg.sh
        -- every ph* profile AND the envctl.* environment control
    python3 .tasks-php/probes/inclusive_ir.py --regen
        -- the p25 pair only; it does NOT write envctl.*
    python3 harness-php/gate.py --tool build ph03 --all   (php builds)
    python3 harness/build.py p25 --all                    (PAT builds)

  ⚠ F83's published numbers are NOT reproduced by this run and must
    not be quoted from it.
rc=0
```

**Before the guard** this same invocation died:
`TypeError: '>' not supported between instances of 'NoneType' and 'NoneType'`
at `N1` — because `needle_sum` returns `None` on an empty annotation.

**Cache RESTORED, same invocation:**

```
SELFTEST -- must-fire negatives
  PASS  N1: ph03 kernel inclusive 181733873 > exclusive 170434489 -- the kernel calls out
  PASS  N2: the annotation text DIFFERS between --inclusive=no and =yes -- so the flag is understood by this valgrind and is not being silently ignored
  PASS  N3: the verus profile's kernel row is mangled ['verus::kernel'] -- the needle matches it, so a cross-rung A difference of 0 is a real 0
  PASS  N4: ph03's on-disk binaries match the published record: [('unsafe', True), ('verus', True)]
  PASS  N5: large agrees to 0.000000 and small only to 0.076240 -- two DIFFERENT agreements, so B and C are genuinely separate computations and not one number twice
  PASS  N6: one binary at 3 environment sizes gives kernel inclusive {181733873} -- spread 0, so +265.924 is not environmental

SELFTEST PASS
rc=0
```

### 2.2 `bc_sweep.py` — cache ABSENT

```
### bc_sweep.py --selftest  (CACHE ABSENT)
============================================================================================
⛔⛔ NOT RUN -- NO VERDICT WAS REACHED. THIS IS NOT A PASS.
============================================================================================
  24 input(s) this script reads are ABSENT. Every one of
  them is GITIGNORED and RE-DERIVABLE, so their absence is the
  expected state of a clean checkout and not a fault -- but it means
  THE CHECK COULD NOT RUN, WHICH IS ITSELF A RESULT TO REPORT
  (the rule .tasks-php/width.py's X3 already follows).

    missing  .temp/mgr172/cg/ph00.unsafe.large.out
    missing  .temp/mgr172/cg/ph00.unsafe.small.out
    missing  .temp/mgr172/cg/ph00.verus.large.out
    missing  .temp/mgr172/cg/ph00.verus.small.out
    missing  .temp/mgr172/cg/ph03.unsafe.large.out
    missing  .temp/mgr172/cg/ph03.unsafe.small.out
    missing  .temp/mgr172/cg/ph03.verus.large.out
    missing  .temp/mgr172/cg/ph03.verus.small.out
    missing  .temp/mgr172/cg/ph07.unsafe.large.out
    missing  .temp/mgr172/cg/ph07.unsafe.small.out
    missing  .temp/mgr172/cg/ph07.verus.large.out
    missing  .temp/mgr172/cg/ph07.verus.small.out
    missing  .temp/mgr172/cg/ph16.unsafe.large.out
    missing  .temp/mgr172/cg/ph16.unsafe.small.out
    missing  .temp/mgr172/cg/ph16.verus.large.out
    missing  .temp/mgr172/cg/ph16.verus.small.out
    missing  .temp/mgr172/cg/ph29.unsafe.large.out
    missing  .temp/mgr172/cg/ph29.unsafe.small.out
    missing  .temp/mgr172/cg/ph29.verus.large.out
    missing  .temp/mgr172/cg/ph29.verus.small.out
    missing  .temp/mgr172/cg/ph64.unsafe.large.out
    missing  .temp/mgr172/cg/ph64.unsafe.small.out
    missing  .temp/mgr172/cg/ph64.verus.large.out
    missing  .temp/mgr172/cg/ph64.verus.small.out

  REBUILD THEM (none of this is committed, by design):
    sh .tasks-php/probes/sweep_cg.sh          -- the 24 profiles
    python3 harness-php/gate.py --tool build <row> --all  -- binaries

  ⚠ F84's published table is NOT reproduced by this run and must not
    be quoted from it.
rc=0
```

The bare run is byte-identical and also **rc=0**.

**Before the guard** this invocation died `KeyError: 'small'` at `N7` — ⚠⚠ **and
the worse half, which the brief did not mention: it printed `FAIL` on five arms
first**, over an empty collection. A probe whose evidence has been deleted was
saying *"F84 is refuted"*. **A missing input is not a refutation**, and that is
the stronger reason the guard runs *before* any arm rather than inside them.

**Cache RESTORED, same invocation:**

```
SELFTEST -- must-fire negatives
  PASS  N1: 12 cells collected, got 12
  PASS  N2: every binary matches its published record's md5_fn -- a stale one would make these numbers a measurement of a different program
  PASS  N3: C differs from A on 7 cells -- if this were 0, `--inclusive=yes` is being ignored and C is A under another name
  PASS  N4: 6 of 12 cells DISAGREE by >= 5 % -- so the sweep could have refuted F83's generalisation and did not merely echo it
  PASS  N5: disagreements run BOTH ways -- 4 where B is larger, 2 where C is larger; B does not merely over-charge
  PASS  N6: family A is exactly 0 on all 8 true-null cells, re-derived off the profiles rather than off results-php/
  PASS  N7: ph03/small still reads B +266.000 and C +265.924 -- F83's headline is reproduced here

SELFTEST PASS
rc=0
```

### 2.3 The *incomplete* half, tested separately

⭐ A guard that only fires on a **missing directory** would not be the brief's
guard. Measured with the directory present and **one** file moved aside:

```
$ mv .temp/mgr172/cg/ph29.verus.large.out ... ; bc_sweep.py --selftest
⛔⛔ NOT RUN -- NO VERDICT WAS REACHED. THIS IS NOT A PASS.
  1 input(s) this script reads are ABSENT.
    missing  .temp/mgr172/cg/ph29.verus.large.out
rc=0
```

⚠ **DESIGN NOTE, stated so it can be overruled.** The required set is
**wider than `CGDIR`**: it includes the gitignored **build trees**, because
`verify_binaries` / `fresh()` raise on an absent binary exactly as surely as the
arms raised on an absent profile. Repairing one limb of a mechanism and leaving
the other is the defect `checkers.py::_disk` was itself caught making. Today
the binaries are present, so the transcripts above list profiles only.

⚠ **`rc=0` HERE IS NOT A PASS AND MUST NEVER BE COUNTED AS ONE.** The banner
says so in capitals, and both files are filed `kind="tool"` — **out of the
routine sweep** — precisely so a green `NOT RUN` line can never be read as a
checker passing. That is `F135`'s class and it was the main hazard of adding
the guard at all.

---

## §3 The registry

| | before | after |
|---|---|---|
| `REGISTRY` filed | **36** | **42** |
| on disk | 36 | 42 |
| `kind="checker"` | 24 | **27** |
| of which flag-gated negatives | 10 | **12** |

Final line, `python3 .tasks-php/checkers.py`:

```
CHECKERS PASS
```

`python3 .tasks-php/checkers.py --selftest` → `SELFTEST PASS`.
`python3 .tasks-php/citecheck.py` → **rc=1, one ROT**, the same adjudicated
false positive as before (`TASK_PHP_048.md:337`). **No new rot.**

### How each was filed, and why

| entry | kind | argv | negatives | st_expect |
|---|---|---|---|---|
| `probes/identity_null.py` | checker | `--selftest` | flag | 0 |
| `probes/flip_exact.py` | checker | `--selftest` | flag | 0 |
| `probes/null_control.py` | checker | `[]` | **inline** | 0 |
| `probes/inclusive_ir.py` | **tool** | — | flag | — |
| `probes/bc_sweep.py` | **tool** | — | flag | — |
| `probes/sweep_cg.sh` | **tool** | — | none | — |

* The three **checkers** read only committed records, write nothing, and cost
  **0.28 s combined**. `identity_null` and `flip_exact` are swept under
  `--selftest` (the bare arm is a report — the defect this registry's header
  warns about); `null_control` is swept **bare** because its negatives really
  are inline: a bare run executes them first and refuses to print anything if
  one fails.
* The two **tools** are kept out of the sweep for the reason
  `probes/ph96_arrayaccess_matrix.sh` gives — ⛔ **not cost**, but that they
  need gitignored profiles *and* gitignored build trees, and a checker that
  reddens when scratch is cleaned is reporting on the scratch. **And now a
  second reason: with the guard they no longer redden, they go GREEN having
  checked nothing**, which is worse in a sweep. Both `why` entries record that
  each HAS a passing `--selftest` (measured rc=0, 1.79 s and 8.50 s) that is
  simply not swept — the item-140 conflation, named rather than hidden.
* `N12` (the arm-count derivation) verified both counts I filed against what the
  checkers actually print: `probes/flip_exact.py claims 6 observed 6`,
  `probes/identity_null.py claims 9 observed 9`. No count was filed for
  `null_control.py`, which prints **no arm names on a pass** — open item 131's
  dialect blind spot, recorded in its `why`.

---

## §4 ⚠ Things I found that I was not told — the part worth reading

### 4.1 ⛔⛔ `bc_sweep.py`'s docstring contradicted `bc_sweep.py`'s own output, and had since it was written

Its headline read **"Across 12 cells that statement is TRUE ON 7 AND FALSE ON 5"**.
Its own `report()` prints, on every run including today's:

```
  B and C agree (< 5 %)                 :  6 of 12
  B LARGER than C  (B charges extra)    :  4  ph00/small . ph00/large . ph07/small . ph29/small
  ⚠⚠ C LARGER than B (B MISSES work)    :  2  ph29/large . ph64/small
```

**6 and 6, not 7 and 5.** The manager's own round record,
`.temp/mgr172/NOTES.md` §9, **also says "TRUE ON 6 AND FALSE ON 6"** — so the
docstring was the only place carrying the wrong figure, and it disagreed with
both the script and the notes.

⭐ **The disputed cell is `ph64/small` at 10.05 %.** The docstring's prose says
*"`ph03`, `ph16` and `ph64` agree closely"*, which folds a 10.05 % cell into the
agreeing set; the `< 5 %` rule the script prints does not.

**Repaired in place, with the reason, in both sentences** — not appended beside
the stale claim (`F129`'s defect). ⚠ **Nothing measured changed**: the 12-cell
table is identical; a count in prose was wrong.

⭐⭐ **And note which arm did not catch it.** `N4` asserts only that **at least
one** cell disagrees. The split was never derived from the data the way
`checkers.py`'s `N12` derives an arm count — **law 6's class inside a probe's
own docstring**. ▶ **Suggested follow-up (not done, it is a measurement
decision): give `bc_sweep.py` an arm that derives the agree/disagree split and
pins the prose to it**, the way `N12` pins a `why`.

### 4.2 ⚠ F87 is **not** evidenced by any of these six files — the brief over-counts by one

The brief says F82–F87 "rest on five probes". Measured:

| finding | evidence among the promoted six |
|---|---|
| F82 | `identity_null.py` (and `null_control.py` as its subject) |
| F83 | `inclusive_ir.py` |
| F84 | `bc_sweep.py` |
| F85, F86 | `flip_exact.py` |
| **F87** | ⛔ **none of them** |

F87 is *"`ph45`'s R4 AND R3 both move, the bound's SIGN REVERSES, and
`get_unchecked` is the EXPENSIVE spelling — 44 pp dearer"*. The tokens
`get_unchecked` and `a1_spread_pp` appear **nowhere** in the six promoted files
or in `.temp/mgr172/NOTES.md`; they are in
`patterns-php/ph45-htmlent-cache-int/controls/spellings.py`,
`controls/spellings.json`, `controls/vacuity.py`, `NOTES.md` and `spec.md` —
**all committed** — and in `.tasks-php/TASK_PHP_037_REPORT.md`.

▶ **This is good news, and it is the kind that goes stale silently: F87's law-11
debt was already discharged before this task started.** It is worth recording
because the same six-finding list appears in the manager's companion document
`.tasks-php/NULLCTL_001.md` (see §4.5), where it would otherwise propagate.

### 4.3 ⛔⛔ `sweep_cg.sh` carries a hardcoded absolute path — and it is a CLASS, not a typo

```sh
R=/home/apt/repos_common/sec-ladder
```

It is **not** derived from `$0`, so the one script whose whole purpose is to
make a clean checkout able to rebuild its evidence **does not itself survive a
clean checkout at a different path**.

⛔ **Reported and NOT repaired**, deliberately, on two grounds: (a) it is what
produced every profile now on disk, and (b) `.tasks-php/probes/rebuild_hardened_php.sh`
— already committed, already registered — carries the identical shape
(`SEC=/home/apt/repos_common/sec-ladder`). ▶ **So it is a class to adjudicate,
not a line to quietly change**, and the call is the manager's. It is stated in
capitals in the file's own header so no reader is misled.

### 4.4 ⛔⛔⛔ `width.py`'s committed header makes a claim about its own degradation that is FALSE — and I was told to copy it

`.tasks-php/width.py` lines 17–23 say of its cross-session check:

> *…`X3`/`X3b`, which compares against `.temp/mgr173/cg/`, reports "the check
> could not run, which is itself a result to report" **and does not fail**.
> ✅ So the selftest degrades honestly rather than lying.*

**Measured 2026-09-17**, with `.temp/mgr173/cg` moved aside and restored:

```
 -- X3: is a profile from ANOTHER SESSION interchangeable? --
  FAIL  X3: no (row, cell, n) from .temp/mgr173/cg/ matches this sweep's endpoints -- the check could not run, which is itself a result to report

SELFTEST FAIL ['X3']
rc=1
```

`reuse_check` returns `("X3", False, …)` and `selftest`'s `check()` appends any
`False` to `fails`, so the message is right and **the verdict is red**. The
claim is half true: it *reports*, and it *does* fail.

⚠ **This is live, not cosmetic.** `width.py` is filed `st_expect=0`. `CLAUDE.md`
Don't #1 says `.temp/` blobs *"get deleted once your gates are green"* — so the
state that turns the routine sweep red on `width.py` is a state the project's
own rules invite. Its registry `why` says nothing about it.

⛔ **I did not repair it.** Deciding whether an unrunnable check should exit 0
(what my two guards do) or 1 (what `X3` does) is a policy call about what the
sweep means, not a promotion chore — and `width.py` carries `F92`. ▶ **Filed for
the manager.** ✅ **My guards do not inherit the defect**: they return `0` and
say in capitals that nothing was checked.

### 4.5 ⓘ A companion document appeared mid-task: `.tasks-php/NULLCTL_001.md`

Untracked, written **2026-09-17 02:15:55** while this task was running — it is
`.temp/mgr172/NOTES.md` promoted under `F147`, by the manager, not by me and not
by any probe (no probe here writes anything). ✅ **Its claim *"the five probes it
cites were promoted in the same pass … Guarded on promotion"* is now true.**
⚠ It carries the same six-finding list §4.2 corrects.

### 4.6 ⓘ `citecheck.py` cannot see `.temp/` citations in `.tasks-php/probes/`

Its `.temp/`-citation classes are scoped to rows' `spec.md` / `NOTES.md` and to
`controls/*` (45 citations across 24 files, 13 §H-at-risk). **`.tasks-php/probes/`
is outside all of them**, so `inclusive_ir.py` and `bc_sweep.py` citing
gitignored profiles is invisible to it — as is the `callee_share.py` citation I
marked by hand. ▶ Not a defect I introduced, and arguably correct scoping, but
it means **the six files just promoted are policed for this by nothing but the
guard and this report**.

---

## §5 Scratch

Evidence logs under `.temp/promote001/` (gitignored, generator-free by design —
they are transcripts, and CLAUDE.md constraint 6 keeps `.log`): the before/after
sweeps, the four guard transcripts, and `width_X3_absent.log` for §4.4. No
binary, `.o`, `.pyc` or `.bin` was produced by this task. Both caches were
restored and re-counted (`.temp/mgr172/cg` 39, `.temp/mgr173/cg` 80).

⛔ **No `git add`, no `git commit`, no history-mutating git command was run.**
