# TASK_PHP_008 — stop detecting, start guaranteeing — ENGINEER REPORT

**Role:** research engineer. **Launched from a running count of 20.**
**Reconciliation is the manager's job.** What I refute is in §10.

> **Bracket, first and last command, both pasted.** ⚠ The middle pair is not
> decoration: `ph00`'s records were *supposed* to go stale, because this task
> adds a file to `patterns-php/ph00-smoke/c/` and edits its `spec.md`.
>
> ```
> FIRST  python3 harness/measure.py --check-stale                  66 record(s) examined, 0 STALE
> FIRST  python3 harness-php/gate.py --tool measure --check-stale   2 record(s) examined, 0 STALE
>
> (after the symlink + the spec.md edit, BEFORE the re-measure)
>        python3 harness-php/gate.py --tool measure --check-stale
>          STALE  results/gate/ph00-smoke.json   patterns/ph00-smoke/spec.md
>          FRESH  results/ph00-smoke.json        18 source(s) + 8 input(s)
>          2 record(s) examined, 1 STALE
>        ⚠⚠ AND THE `FRESH` THERE IS A FINDING, NOT AN OVERSIGHT -- see §6.
>
> LAST   python3 harness/measure.py --check-stale                  66 record(s) examined, 0 STALE
> LAST   python3 harness-php/gate.py --tool measure --check-stale   2 record(s) examined, 0 STALE
>          FRESH  results/gate/ph00-smoke.json   29 source(s)     (was 28)
>          FRESH  results/ph00-smoke.json        19 source(s)     (was 18)
> ```
>
> **No-touch disclosure, BY BYTES, with the control fired first.**
> `.temp/php8/01-snapshot-start.log`:
>
> ```
> $ python3 .temp/php5/snapshot.py control
> control: 27 files snapshotted, one byte-appended
>   CHANGED  common/slb.py  2abd87f76712 -> 27618554643a
> CONTROL FIRED
>
> $ python3 .temp/php5/snapshot.py check .temp/php5/pat-snapshot.json          # TASK_PHP_005's
> snapshot check: 2966 recorded, 2966 now, 0 difference(s)
> $ python3 .temp/php5/snapshot.py check .temp/php7/pat-snapshot-007-start.json # TASK_PHP_007's
> snapshot check: 2966 recorded, 2966 now, 0 difference(s)
> $ python3 .temp/php5/snapshot.py write .temp/php8/pat-snapshot-008-start.json
> snapshot: 2966 paths under ['harness', 'common', 'patterns', 'results', 'pilot']
> $ git status --porcelain
> (empty)
> ```
>
> The closing check against my own baseline is in §8.
>
> **Planting disclosure.** One plant into a **committed** directory:
> `results-php/preflight/`, by re-running the reviewer's own
> `.temp/php7/a5_record_growth.py` **unmodified**. It backs the directory up,
> restores it in a `finally:` and re-verifies **by sha256 per file**
> (`RESTORE EXACT: True`, §5.3). Everything else rebinds
> `gate.PREFLIGHT_DIR` / `gate.REPO` **in process** to fixtures under
> `.temp/php8/`; the real directory is digested before and after and printed
> (`14-coverage-cap.log`, `byte-identical before/after: True`).
>
> **Scratch:** `.temp/php8/` — **34 logs, 5 generators** (`g1_elif_control.py`
> the `#elif` controls, `g2_digest_audit.py` the `c/` fixtures,
> `g3_coverage_and_cap.py` M4/M5/the cap, `g4_selfdeadlock.py` §8b,
> `g5_real_row_path.py` the real-tarball row path), one PAT snapshot, one
> pre-task backup of `results-php/preflight/`. ⚠ **Every fixture tree and
> binary deleted**, including the ones the re-runs recreated under
> `.temp/php5/fix`, `.temp/php7/fix` and `.temp/php7/resid` — two ELF binaries
> (`bin-ph70-optimize-gcc-O0/O3`) were left by `a1_flagmatrix.py` and are gone.
> Counts after cleanup: `php5` **29**, `php6` **34**, `php7` **28** — the same
> as `TASK_PHP_006` and `TASK_PHP_007` left them.
> ⚠ `snapshot.py`, `b1_bypass.py`, `a1_flagmatrix.py`, `a5_record_growth.py`
> and `b3_residuals.py` were **re-run, not modified**; nothing under
> `.temp/php5/`, `.temp/php6/` or `.temp/php7/` was deleted except those
> derived trees.

---

## Summary

| § | what landed | evidence |
|---|---|---|
| **§0** | **The unconditional link.** `_tu_closure`, `_MM_CONFIGS`, `_INCLUDE_RX`, `_text_mentions` and the `texty` fallback **deleted**; `shim_link_audit` is `islink` + `realpath`. All 12 of the reviewers' fixture rows now carry the link or are refused. | `08-b1-bypass-AFTER.log`, `09-flagmatrix-AFTER.log` |
| **§0.4** | `uses_allocator` is a **declared** `provenance` field. Reported, never read. | `06-preflight-after.log` |
| **§1** | The subdir ban is **lifted**; `c_digest_audit` replaces it. It closes M1 (symlinked directory) and m1 (dotfile), and **allows** the flat-link layout. 8/8 fixtures. | `11-digest-audit.log` |
| **§2** | The overlap floor **reports and no longer refuses**. `#elif 0` fixed, with a must-fire control against the `TASK_PHP_006` code and a must-NOT-fire against the lazy repair. | `03-overlap-selftest.log`, `04-elif-control.log` |
| **§3 M3** | Collapse on **content**, not adjacency, plus `MAX_RUNS`. Alternation growth **+2.0 runs / +2385 bytes per cycle → 0.0 / 0**. | `13-record-growth-AFTER.log`, `14-coverage-cap.log` |
| **§3 M4** | A missing preflight record is a **FAILURE**. The repair loop was run end to end on three uncovered rows and **converges**. The discarded return value is bound. | `14-coverage-cap.log` |
| **§3 M5** | `--audit` reads the **verdict**. Three must-fire cases and one must-NOT-fire. | `14-coverage-cap.log` |
| **m6** | The PAT `why` band is **computed** from `patterns/*/spec.md`, not a constant in an f-string — ⚠ and pinned to the published percentile convention, because computing it my way gave a **fourth** answer. | `07-why-band.log` |
| **§2.3** | ⚠ Everything §2 touched is **unreached** on `ph00-smoke` (it returns early). Three rows built against the **pinned tarball** exercise it: a real `verbatim` lift scores **89 %**, and the two rows `TASK_PHP_006` refused now **pass with a loud report**. | `28-real-row-path.log` |
| **§6** | ⚠ `measure.py --check-stale` **cannot see a file ADDED** to `<row>/c/`. `0 STALE` means "everything pinned still matches", not "everything is pinned". | `12-added-key-blindspot.log` |
| **§8b** | ⚠⚠⚠ **M4 + M5 as first written are a REAL, PERMANENT DEADLOCK on the fresh-clone path.** Found by running the loop, before shipping; repaired; the must-fire control still fires on the naive rule. **Read this one.** | `21-selfdeadlock-BEFORE.log`, `22-selfdeadlock-AFTER.log` |

⚠⚠ **§8b is the section to read first if you read only one.** §5 answers the
three calls; §10 has what I refute; §9 has the clean negatives.

---
# §0 The unconditional link — landed, and the detector is gone

## 0.1 What was deleted

`git show HEAD:harness-php/gate.py` vs the file now, counted by AST node with
comments and docstrings excluded (`.temp/php8/17-code-accounting.log`):

```
DELETED outright (79 code lines):
    -  38  c_subdir_audit          <-- §1, replaced
    -  30  _tu_closure
    -   6  _text_mentions
    -   2  _INCLUDE_RX
    -   1  SHIM_IMPL_TU
    -   1  ALLOC_FILES
    -   1  _MM_CONFIGS
CHANGED in place:
      -41  shim_link_audit  (97 -> 56)
```

`shim_link_audit` is now, in full: does `<row>/c/emalloc_shim.h` exist, is it a
symlink, does its `realpath` equal `common-php/emalloc_shim.h`. **No
subprocess, no flag space, no compiler, no fallback, no regex.** The `texty`
fallback and the *"dead code … Not treated as a shim user"* note are gone
outright — not kept as advice, per §0.2.

`grep -n '_tu_closure\|_MM_CONFIGS\|_INCLUDE_RX\|_text_mentions\|ALLOC_FILES\|SHIM_IMPL_TU\|texty' harness-php/gate.py`
returns **only prose**: six lines of historical commentary in docstrings, no
code.

## 0.2 ⚠ THE TASK PREDICTED A NET DELETION AND IT IS **NOT** ONE. Here is why, measured.

> *"⚠ This task should REMOVE more code than it adds. If it does not, tell me
> why."*

**It adds 90 net code lines** (`gate.py` +40, `provenance.py` +50). Attributed
by section, from the same per-function count
(`.temp/php8/26-code-accounting-final.log`):

| section | net code lines | what |
|---|---|---|
| **§0 the unconditional link** | **−82** | `_tu_closure` −30, `shim_link_audit` −41, `_text_mentions` −6, three constants −3, `_INCLUDE_RX` −2 |
| §1 `c_digest_audit` | **+18** | `c_subdir_audit` −38, `c_digest_audit` +40, `_walk_files` +16 |
| §3 M3 collapse + cap | **+35** | `_collapse_and_cap` +27, `_carries_evidence` +7, `MAX_RUNS` +1 |
| §3 M4/M5 coverage | **+60** | `preflight_coverage_audit` +38, `_run_is_certifying` +13, `preflight` +8, `_COVERAGE_TAG` +1 — ⚠ **+1 of that is the deadlock repair in §8b** |
| m6 `why_band` | **+9** | the PAT band, computed |
| §2 provenance | **+50** | `check_row` +19, `OVERLAP_CASES` +12, `unevaluable_conditionals` +12, `_strip_dead_conditionals` +6, `ALLOC_KEY` +1 |
| **total** | **+90** | (−82 +18 +35 +60 +9 +50 = +90, and gate.py's share sums to +40 exactly) |

✅ **The manager's prediction is right about §0 and only about §0: the design
change itself is −82 code lines, and it deletes the only two functions in the
programme that ever had to be right about an unbounded input space.** The +172
that follows is five *other* instructions in the same task file — M3, M4, M5,
m1 and m6 each ask for a check that did not exist, and §1 asks for an audit to
replace a ban.

⚠ **I am flagging this rather than presenting +89 as a win**, because
"this task should remove more than it adds" is a good instinct and the honest
answer is that §0 obeyed it and the task as a whole could not. If the manager
wants the *stated* property, the lever is not §0 — it is deciding that M3/M4/M5
are worth 95 lines of gate code. **I think they are**, for the reason in §5.3:
every one of them is a check on a FINITE, OBSERVABLE input (a JSON list, a set
of files, a recorded verdict), not on an idiom space. But that is a judgement
and it is the manager's to overturn.

## 0.3 The reviewers' fixture rows, re-run from their UNMODIFIED generators

### `.temp/php5/b1_bypass.py` — TASK_PHP_005's eight rows (`08-b1-bypass-AFTER.log`)

```
--- ph50-direct     refused: True    (link absent)
--- ph51-linked     refused: False   allocator in GATE digest: True   MEAS digest: True
--- ph52-indirect   refused: True
--- ph53-subdir     refused: True
--- ph54-dotc       refused: True
--- ph55-extern     refused: True    <-- ⚠ CHANGED: was a clean PASS
--- ph56-mention    refused: True    <-- ⚠ CHANGED: was a clean PASS (F-8's row)
--- ph57-rust       refused: True    <-- ⚠ CHANGED: was a clean PASS
```

⚠⚠ **The task asked me to say this out loud, so: `ph55-extern`, `ph56-mention`
and `ph57-rust` have gone from clean negatives to failures, deliberately.**
None of them allocates. Under the unconditional rule that is not a question the
audit asks, so a non-allocating row without the link is refused exactly like an
allocating one. **The script's `expected` column now disagrees with the tool on
those three rows and I left the script byte-identical rather than retuning it**,
so the log shows the mismatch honestly — the same choice `TASK_PHP_006` made
for `ph55`.

✅ **`ph51-linked`, the one row that carries the link, still passes and its
allocator is in BOTH digests.** That is the must-NOT-fire, and it is the whole
guarantee: if it broke, the rule would be refusing every row and pinning
nothing.

### `.temp/php7/a1_flagmatrix.py` — TASK_PHP_007's B1 and B2 (`09-flagmatrix-AFTER.log`)

```
=== SUMMARY: did gate.py refuse? (False = BYPASS) ===
  REFUSED  A1 ph70-optimize (__OPTIMIZE__)
  REFUSED  A2 ph71-clang    (__clang__)
  REFUSED  A3 ph72-hasinclude
  REFUSED  A4 ph73-fallback (row picks the text detector)
```

All four were **BYPASS** at `TASK_PHP_007`. The generator still measures the
real preprocessor states and they are unchanged — `ph70-optimize` is still live
in four of eight cells and still allocates for real —

```
=== does ph70-optimize really allocate at -O3? ===
    BUILD gcc-O0: ok    | alloc tally = 0
    BUILD gcc-O3: ok    | alloc tally = 1000
```

— but **the audit no longer has an opinion about which cells are live**, so the
gap between what it simulates and what `build.py` compiles cannot exist.

⚠ **And the note that made B1 worse than the hole it replaced is gone.** The
string `Not treated as a shim user` appears nowhere in `harness-php/`.

### `.temp/php7/b3_residuals.py` — ⚠ it CRASHES now, and that is the result

```
(1) one committed `runs[]` entry, by row count
  today (1 php row): 1519 bytes/entry
Traceback (most recent call last):
  File ".../b3_residuals.py", line 47, in <module>
    os.symlink(CANON, os.path.join(d, "emalloc_shim.h"))
FileExistsError: [Errno 17] File exists: ... /ph090-clone/c/emalloc_shim.h
```

Its row factory clones `patterns-php/ph00-smoke/c/` and *then* adds the
symlink, on the assumption that `ph00-smoke` has no `emalloc_shim.h`. **Under
the unconditional rule every row has one, so the assumption is now false for
every row in the corpus** — the generator is measuring a world that no longer
exists. I re-ran it unmodified, pasted the failure, and rebuilt its three
measurements against the new code instead:

- part (1), the record-entry size at scale → **superseded by §5.3**, because
  M3's fix changes the arithmetic it was extrapolating;
- part (2), *"with no `gcc`: NO problem raised for a row that allocates. FAIL
  OPEN"* → **structurally impossible now.** `_tu_closure` and `_text_mentions`
  do not exist, and `shim_link_audit` runs no subprocess at all, so there is no
  path on which a missing compiler changes a verdict. `grep -c subprocess`
  inside `shim_link_audit`: **0**.
- part (3), the text fallback vs a symlinked `c/` subdirectory → **§1**, where
  that layout is now refused unless every file behind it is keyed.

---

# §1 The subdir ban is lifted, and `c_digest_audit` replaces it

`c_subdir_audit` refused any `<row>/c/<subdir>/`. It is gone. `c_digest_audit`
asks a different question: **does every file under `<row>/c/` share a `realpath`
with some `glob("<row>/c/*")` entry `os.path.isfile` accepts** — which is
exactly, and only, what both digests are built from.

⚠ **It enumerates FILES — a finite, observable set — not IDIOMS.** That is the
whole reason it is sound where §0's detector was not, and it is worth stating
as the discriminator: `os.listdir` has a bounded answer; "every way to spell an
`#include`" does not.

The walker is `_walk_files`: recursive, **following directory symlinks**, with
a `seen` set of realpaths so a cycle terminates. `os.walk` does not follow a
directory symlink (M1) and `glob` never matches a leading dot (m1); those two
properties are the whole of what walked round the ban.

`.temp/php8/11-digest-audit.log`, eight fixtures, each also compiled for real
with `build.py`'s own `-I` flags and traced into both digests by running
`check.py`'s and `measure.py`'s own glob lists:

```
--- ph80-subdir      REFUSES True  (expected True)   compiled True   digests False/False
--- ph81-dirlink     REFUSES True  (expected True)   compiled True   digests False/False   <-- M1, was NOT refused
--- ph82-dotfile     REFUSES True  (expected True)   compiled True   digests False/False   <-- m1, was NOT refused
--- ph83-flatlink    REFUSES False (expected False)  compiled True   digests True/True     <-- MUST NOT FIRE
--- ph84-nextfile    REFUSES True  (expected True)                                         <-- the engineer's objection
--- ph85-dirlink-ok  REFUSES False (expected False)  compiled True   digests True/True     <-- MUST NOT FIRE
--- ph86-clean       REFUSES False (expected False)  compiled True   digests True/True
--- ph87-cycle       c/sub/loop -> ..   walker terminated, 1 problem
8/8 fixtures landed as expected
```

Two of those deserve naming:

- **`ph84-nextfile` is `TASK_PHP_006`'s exact stated reason for declining the
  hatch** — *"nothing would force the NEXT file added to that subdirectory to
  get a link"*. A directory with one linked file and one newly-added unlinked
  one is refused, naming the missing link and printing the `ln -s` that fixes
  it. The reviewer was right that twelve lines answer it; ⚠ **the reviewer's
  twelve lines and mine differ in one way that matters** — theirs walked with
  `os.walk`, which is what let `ph81-dirlink` through in the first place.
- **`ph85-dirlink-ok` is the layout a php row will actually want**:
  `c/zend -> ../../extract/Zend` plus a flat link per file. It passes, and the
  real bytes are in both digests.

The refusal message prices both ways out and prints the exact command:

```
digest: ph80-subdir: c/zend/payload.h is COMPILED and in NO DIGEST.
   Fix: EITHER flatten it to c/zend__payload.h and rewrite the #include,
        OR add the flat symlink beside it:
        ln -s zend/payload.h patterns-php/ph80-subdir/c/zend__payload.h
```

⚠ **`PROTOCOL_PHP.md` §B3 now says the layout is available and priced**, not
forbidden, with the unsound/over-strict argument spelled out.

---

# §2 The overlap floor: reported, not enforced — and `#elif 0` fixed anyway

`provenance.py::check_row` no longer returns `False` for a low overlap. It
prints the number, the tier's expectation, an explicit *"below what
`tier=verbatim` leads a reader to expect"* line when it is short, and — new —
**how many preprocessor conditions the heuristic could not evaluate**
(`unevaluable_conditionals`). ⚠ **The exact half is untouched**: `c_file` in
the manifest, span in range, `extract_sha256`, `extract_cmd` canonical, and a
row that declares PHP provenance and ships no kernel are all still refusals.

## 2.1 `#elif 0` — fixed, with the control that proves the fix

`_strip_dead_conditionals` treated `#elif` as *"stop skipping"*. A `#elif 0`
arm is dead whatever the preceding conditions were, so the old code turned
skipping **off** for a dead arm and counted the payload. Now: a literal-false
`#elif` **starts or continues** a skip at this depth; any other `#elif` ends
one.

Two regression cases, and **both directions are exercised**
(`03-overlap-selftest.log`, 9 cases, 0 FAILED):

```
  ok    B4 wrong kernel + `#elif 0`                          overlap  11%  want 0% <= x < 50%
  ok    E2 `#if 0` / `#elif COND` -- the possibly-live arm   overlap 100%  want 99% <= x < 101%
```

⚠ **A regression case that passes proves nothing unless the code it guards can
fail it.** `.temp/php8/g1_elif_control.py` re-implements
`_strip_dead_conditionals` **verbatim as `TASK_PHP_006` shipped it** and
re-scores, and separately implements the lazy repair (`elif → always skip`)
that would satisfy B4 (`04-elif-control.log`):

```
(1) MUST FIRE -- the TASK_PHP_006 code on the new case B4
    B4 under TASK_PHP_006's `_strip_dead_conditionals` : 100%
    B4 under the shipped one                           : 11%
    CONTROL FIRED -- the old code scores the dead payload as live

(2) MUST FIRE -- the OVER-fix (`elif` always dead) on case E2
    E2 under `elif -> always skip` : 11%   (want 100%)
    B4 under `elif -> always skip` : 11%   (it DOES satisfy B4)
    E2 under the shipped one       : 100%
    CONTROL FIRED -- E2 is what stops the lazy repair

(3) no other case moved
    cases whose score differs between TASK_PHP_006 and today:
      ['B4 wrong kernel + `#elif 0`']
```

**Exactly one case moved, and it is the one the bug was in.** E2 is the case
that matters most: without it, the cheap wrong fix passes.

## 2.2 What I did NOT do, deliberately: the other nine spellings

`#if 0L`, `#if (0)`, `#if 00`, `#if !1`, `#ifdef NEVER_DEFINED`,
`#ifndef __STDC__`, `#if defined(NOPE) && defined(NOPE2)` and
`#if 1 … #else <payload> #endif` still score 100 %. **I did not add eight
predicates**, because that is §0's mistake one level down and the next spelling
would reopen it.

⚠ **What I did instead is report the size of the residual.**
`unevaluable_conditionals()` counts every `#if`/`#elif` whose condition is not
literal `0`, plus every `#ifdef`/`#ifndef`, and prints it on every run:

```
<row>: ⚠ N preprocessor condition(s) in the kernel this heuristic CANNOT
evaluate: [...]. Anything inside a dead one of those is counted as live
(TASK_PHP_007 M2 measured nine such spellings). This is the size of the
residual, not a defect.
```

A number the reader can see beats a guarantee that is false. ⚠ It is **not** a
check and must never become one — a legitimate `verbatim` lift of PHP source is
full of `#ifdef`s.

✅ **And it counts exactly the right things** (`28-real-row-path.log`). Fed
`TASK_PHP_007` M2's own list of **nine** spellings it reports **eight**:

```
   8  TASK_PHP_007 M2's nine spellings
      ['#if 0L','#if (0)','#if 00','#if !1','#ifdef NEVER_DEFINED',
       '#ifndef __STDC__','#if 1','#if defined(NOPE) && defined(NOPE2)']
   1  a realistic verbatim PHP lift          ['#ifdef ZTS']
   0  only literal-false conditionals        (`#if 0` / `#elif 0`: both evaluable)
   0  a comment that LOOKS like a conditional  <-- must NOT fire
```

**Nine minus the one this task fixed is eight**, and the residual is now a
printed integer instead of an unstated assumption. ⚠ The last line is the
must-NOT-fire: `_strip_comments` runs first, so `/* #ifdef NEVER */` is not
counted.

## 2.3 ⚠⚠ The demoted path was UNREACHED by the preflight, so I built a row that reaches it

`ph00-smoke` declares `php_provenance: false` and `check_row` **returns before
the overlap is ever computed**. So every line §2 touched — the demoted floor,
the under-expectation message, `unevaluable_conditionals`, and the
`os.path.join(pdir, "c", f)` path reconstruction I added — **is dead code on
the only row that exists.** A change nobody runs is a change nobody has tested,
so `.temp/php8/g5_real_row_path.py` builds three rows against the **pinned
tarball** at `Zend/zend_operators.c:821-850` (`mul_function`), the real
citation the type axis is aimed at (`28-real-row-path.log`):

```
excerpt Zend/zend_operators.c:821-850  1046 bytes  sha256 c57f823dc5a5fe5c

(a) a plausible `verbatim` lift   check_row ok = True    overlap  89% (17/19)
(b) DIVIDES, cites multiplication check_row ok = True    overlap   5% (1/19)
(c) the same behind `#elif 0`     check_row ok = True    overlap   5% (1/19)
3/3 as expected
```

Three things this shows that no in-code fixture could:

- ✅ **A real `verbatim` lift of real PHP scores 89 %** — the 50 % expectation
  is not tight, which is what `TASK_PHP_005`'s clean negative 7 was about.
- ⚠⚠ **(b) and (c) PASS. Under `TASK_PHP_006` they were REFUSED.** That is the
  demotion, on a real row rather than a slogan, and the report says so at the
  top of its own output: *"⚠⚠ THE OVERLAP IS BELOW WHAT tier=verbatim LEADS A
  READER TO EXPECT (5% < 50%). This is REPORTED and does not refuse the row."*
- ✅ **(c) scores 5 %, not 100 %** — the `#elif 0` fix holds on a real excerpt
  and not only on the embedded self-test string.

⚠ **(b) and (c) also print `⚠ no uses_allocator declared`**, which is the
field's whole behaviour: loud, never fatal.

---

# §3 M3, M4, M5 — the preflight record

## 3.1 M3 — collapse on content, and a cap

Two changes, and they are different things:

- **Collapse.** `write_preflight_record` dropped a run only if it equalled the
  **immediately preceding** one. Now `_collapse_and_cap` removes any entry
  byte-identical to an **earlier** one, keeping the first. ⚠ Collapsing on
  FULL CONTENT can never lose a fact — two entries only merge when every field
  agrees, `provenance_skipped` included — which is why the key is the whole
  body and not a chosen subset.
- **Cap.** ⚠ *Collapse is not a bound.* A tree that genuinely differs between
  runs still adds an entry each time, and `TASK_PHP_007` M3 correctly noted
  that `gate.py` contained no `prune`/`MAX_RUNS`/`truncat`/`rotate`. `MAX_RUNS
  = 40`, keeping the first, the last, and **every entry that carries evidence**
  (`provenance_skipped`, a non-empty `problems`, a `shim_repaired`, a
  `PREFLIGHT FAILED` verdict, or the migrated pre-`TASK_PHP_006` record), with
  `_dropped_runs` recorded in the file.

The reviewer's **unmodified** `.temp/php7/a5_record_growth.py`
(`13-record-growth-AFTER.log`):

```
start: runs=4  bytes=4963

=== (i) REPEAT the same command 4x -- should collapse ===
  after `gate.py --preflight` #1..#4: runs=5 bytes=6318   (unchanged)

=== (ii) ALTERNATE two routine commands 6x ===
  A = `gate.py --preflight`
  B = `gate.py --tool measure --check-stale`   (the bracket every task mandates)
  cycle 1:  after A runs=5 bytes=6318   after B runs=5 bytes=6318
  cycle 2..6: identical, runs=5 bytes=6318 throughout

end: runs=5  bytes=6318   (+1 runs, +1355 bytes)
per-cycle growth: 0.2 runs, 226 bytes

=== does anything prune? ===
  gate.py contains 'prune': True     'MAX_RUNS': True
  'truncat': True                    'rotate': True
```

⚠ **Read the `+1 run` honestly: it is the FIRST `--preflight` of the run, whose
body differs from anything stored because this task changed the record's shape
(`c_digest_ok`, `why_band_pat`, the new coverage field).** The steady state is
what the cycles show: **cycles 1 through 6 are byte-identical, 0 runs and 0
bytes per cycle**, against the reviewer's measured **+2.0 runs and +2385 bytes
per cycle**. At the reviewer's own 80-row extrapolation that is ~19 kB/cycle →
**0**.

⚠⚠ **What DOES still grow the record legitimately, and it is worth naming
because it looks like M3 coming back: `harness_php_sha256` is part of the
body.** Every edit to `harness-php/*.py` makes every subsequent run a distinct
content key, so a *development* session adds one entry per tool version. That
is the record doing its job — it says which tool certified which run — and it
is exactly why the cap exists rather than collapse alone. This task's own
`ph00.preflight.json` ended at **10 runs**, one per version of `gate.py` /
`provenance.py` I gated against, with `gate_argv` and the hash both visible.
**Ordinary operation, where the tools do not change, collapses to nothing.**

The cap, exercised on 120 *genuinely distinct* runs (`14-coverage-cap.log`):

```
CAP -- content collapse is not a bound; MAX_RUNS=40 is
  wrote 120 GENUINELY DISTINCT runs (no two collapse)
  runs kept   : 40   (cap 40)
  _dropped_runs: 80
  first kept  : 0   last kept: 119
  the evidence-carrying entry (serial 7, provenance_skipped) survived: True
```

✅ **The `provenance_skipped` entry survives a 3× overflow.** That is the
must-not-lose: `TASK_PHP_005` F-2a is about exactly that entry being erased.

## 3.2 M4 — a missing preflight record is now a FAILURE, and the deadlock does not exist

`preflight_coverage_audit` returns **problems**; `preflight()` binds them
(⚠ it read `_cov_bad, cov_notes = ...` and **discarded** the problems, so the
stage could not have failed even if it had returned any — the reviewer's
parenthetical, and it really was two lines and not one).

⚠ **I did not take the deadlock on trust in either direction. I ran the repair
loop** (`14-coverage-cap.log`) on a fixture REPO with three uncovered records:

```
  start: 1 problem(s)   CONTROL FIRED
    | preflight coverage: 3 php record(s) have NO preflight record:
      ['results-php/ph01-a.json', 'results-php/ph02-b.json', 'results-php/ph03-c.json']

  the repair loop -- one `--preflight <row>` per uncovered row.
  ⚠ Each invocation is EXPECTED to fail (rc=2) while the OTHERS are still uncovered.
    The question is whether it WRITES anyway.
    after repair #1 (ph01): files on disk = ['ph01.preflight.json', 'ph01.when.json']
    after repair #2 (ph02): files on disk = [..., 'ph02.preflight.json', ...]
    after repair #3 (ph03): files on disk = [..., 'ph03.preflight.json', ...]
  ... then one CERTIFYING run each ->
    -> 0 problem(s)   CONVERGED -- NO DEADLOCK
```

**The mechanism the engineer asserted (*"would fail on every other uncovered
row before writing anything"*) is false, and the design that rested on it is
reversed.** No `--allow-uncovered` escape is needed; I did not add one.

⚠ **An intermediate state is worth naming because it looks like a deadlock and
is not.** After all three rows have a record, the audit *still* refuses — every
recorded run says `PREFLIGHT FAILED`, which is M5 working. The loop converges
once each row gets one *certifying* run, which is what a real repair does.
A reader who stops at the middle step will think it is stuck.

## 3.3 M5 — `--audit` reads the verdict

`_run_is_certifying` rejects a run whose verdict is `PREFLIGHT FAILED`, or that
has a non-empty `problems`, or `provenance_skipped: true`, or `shim_ok: false`.
A record covers its row iff **some** run in it certifies.

```
M5 -- does the audit read the VERDICT, or only the FILENAME?
  verdict=PREFLIGHT FAILED     -> audit refuses: True
  provenance_skipped=true only -> audit refuses: True
  shim_ok=false only           -> audit refuses: True
  a clean run                  -> audit refuses: False
```

⚠ **The last row is the must-NOT-fire and it is the one that makes the other
three mean something**: an audit that refuses everything measures nothing.

---

# §4 The minors

- **m1 — the dotfile.** Closed by `c_digest_audit` (§1, `ph82-dotfile`). A
  dotfile has no sanctioned form — `glob` cannot match it, so there is no flat
  key to give it — and the message says *rename it* rather than offering a link
  that would not work.
- **m6 — the hard-coded PAT band.** `preflight` printed
  `PAT corpus n=33: median 989, p90 1817, max 3140` as a **constant inside an
  f-string**, while `why_sizes` reads `patterns-php/` only. `why_band()` now
  computes it from `patterns/*/spec.md` on every run (read-only; `patterns/` is
  frozen and nothing writes there). ⚠ **See §10.3 — this nearly introduced a
  fourth answer to a quantity `RECAP_PHP.md` warns already has three.**
- **`~115 ms/row` → `~135`.** ⚠ The number's *home* is gone: it lived in
  `_tu_closure`'s docstring, which was deleted with the function, and the
  `gcc -MM` price is no longer a cost this programme pays at all. It survives
  in `RECAP_PHP.md:67` and `:351`, which is the manager's file — proposed
  wording in §7.
- **m5 — `PROTOCOL_PHP.md:325`'s ✅ enforced row.** Rewritten. It named *"the
  `c/` subdirectory ban, the allocator closure"*, both of which B1/B2/M1 had
  made half-true. It now names nine preflight stages, says **eight** can fail
  and which one cannot, and gains two ❌ rows for the checks this task demoted.
- **`common-php/emalloc_shim.c`'s comment.** ⚠ Its `TASK_PHP_006` replacement
  claimed `_tu_closure` meant *"both spellings AND ANY FUTURE ONE are seen"* —
  a prediction about an unbounded space, made by a guard that had enumerated
  two points of it, and **falsified within one task**. That is the same defect
  as the *"CANNOT BE"* sentence the same comment exists to record. Corrected,
  with the history left in place; `digest_bridge.py --regen` run
  (`emalloc_shim.c` `3dd92f81ad1c → 2e7a82b00294`), `--verify` green.
- **m2, m3, m4** are `RECAP_PHP.md` citations. **Not landed — manager's file.**
  §7 has the wording.
- ⚠ **An adjacent dangling citation I found and did NOT fix**, because it is
  not this task's and the correct repair is a wording change in three files:
  `.temp/php0/pycdemo` is cited by `harness-php/gate.py:180`,
  `harness-php/root.py:113` and `.tasks-php/TASK_PHP_002_REPORT.md:290`, and
  **`.temp/php0/` exists but `pycdemo` does not** — it was a scratch module
  deleted at cleanup. The measurement it names is real; the path is not. The
  honest fix is *"measured at `TASK_PHP_002`; the scratch module has since been
  cleaned up"*, in all three.

---

# §5 The three calls the manager was least sure of

## 5.1 ⚠⚠ Call 1 — *"is the unconditional link right? show me a cheaper design that is still correct by construction"*

**The design is right, I have no cheaper one that is correct by construction —
and the price you stated for it is wrong in your favour. Measured.**

### The stated cost, and the half of it you already pay

> *"an `emalloc_shim.h` edit will mark **every** php row stale, not only the
> allocating ones. That is a real cost in re-gates."*

⚠ **The GATE half of that has been unconditional since `TASK_PHP_002` and has
nothing to do with the symlink.** `common-php/digest_bridge.py` carries
`emalloc_shim.h`'s sha256 in its `BRIDGED` table, and `check.py`'s
`common/*.py` glob puts *digest_bridge.py's own hash* into **every** php gate
record. Read out of the committed records (`.temp/php8/02-digest-reality.log`):

```
=== gate record source_sha256 keys (28) ===
    common/digest_bridge.py                <-- HERE
    common/driver.c ... verus_run.py
=== measurement record source_sha256 keys (18) ===
    (no digest_bridge.py, no common-php/ anything)

common-php/digest_bridge.py sha256      = 298bac49524df1c5
gate record's common/digest_bridge.py   = 298bac49524df1c5
in MEASUREMENT record?                  = False
```

`TASK_PHP_006` measured the consequence without naming it as one: its shim edit
staled `ph00`'s gate record **while `ph00` carried no link at all**.

✅ **So the MARGINAL price of "every row" over "every allocating row" is the
MEASUREMENT half only: a re-measure plus a `report.py` render per row, on top
of a re-gate that was already owed.** Not a re-gate per row. The manager's
sentence describes a cost the tree has paid since Phase 0.

### The missing measurement: how often does the shim actually change?

The manager wrote *"I have **not** measured how often the shim will change once
rows exist."* It is one command:

```
$ git log --oneline -- common-php/emalloc_shim.h
be580da TASK_PHP_006: the blocker closed by asking the compiler, not by adding a spelling
bf99aaf TASK_PHP_004: both Phase 0 blockers closed, with must-fire negatives
53f4c2a TASK_PHP_002: Phase 0 built and gated green, with the PAT tree proved untouched
                                          +470/-0, +167/-20, +60/-9
```

**Three edits in the seven php tasks so far** — and ⚠ **two of the three were
PROSE**: `TASK_PHP_004`'s was the `PHP_SHIM_SIGNED_MULTIPLY_LONG` fix (real),
`TASK_PHP_006`'s was documentation in a digest-pinned file, and this task
touched `emalloc_shim.c` for a comment. So the honest rate is **~0.4
shim-touching tasks per task, most of them comments.**

⚠ **That cuts against the design and I am reporting it that way**: a file that
is edited in 3 of 7 tasks, mostly for prose, is a file whose edits will
routinely cost a corpus-wide re-measure. At 20 rows and ~8 minutes per
re-measure (see 5.1's measured figure below) that is **~2.7 hours per comment
fix**.

✅ **But the mitigation is already in the protocol and costs nothing: batch.**
`PROTOCOL.md` rule 6 says exactly this for rung sources — *"batch every
rung-source doc fix into ONE pass rather than avoiding them"* — and it applies
verbatim here. **A prose fix to `emalloc_shim.h` should never be landed alone.**

### The price, measured on the only row that exists

| step | wall clock | what moved |
|---|---|---|
| `--tool measure ph00` | **7 m 52 s** (10:30:24 → 10:38:16, file timestamps) | see below |
| `--tool report ph00` + gate chain | §8 | §8 |

The re-measure's record diff against `git show HEAD:` (`18-measure-diff.log`):

```
1199 leaf values before, 1197 after
  moved: 87   added: 2   removed: 4
MOVED by class: {'wall clock': 84, 'run metadata': 2, 'other': 1}
ADDED: ['/source_sha256/patterns/ph00-smoke/c/emalloc_shim.h',
        '/cells[11]/wall/small.bin/warning']
⚠ DETERMINISTIC leaves that moved (Ir / checksum / md5 / identity / inputs): 0
source_sha256 movers:
   /source_sha256/patterns/ph00-smoke/c/emalloc_shim.h  None -> aa9abf48535e8d
```

✅ **Zero `Ir`, zero checksum, zero md5, zero identity, zero input hash** —
exactly what `PROTOCOL.md` rule 6 predicts for a re-measure, and the one added
source key is the point of the whole exercise.

### The cheaper designs I considered and rejected, so nobody re-derives them

1. **Pin the shim into a GATE-only location for non-allocating rows** (e.g.
   `controls/`), keeping `c/` for allocating ones. ⚠ **This is a detector
   wearing a directory name.** Rejected.
2. **Version the shim** — `emalloc_shim_v1.h`, `v2.h`, each row links the
   version it measured under. Correct by construction and **cheaper**: no
   existing row ever goes stale. ⚠ **Rejected because it inverts the property
   we want.** A shim fix that does not propagate leaves rows measured under a
   known-wrong allocator, silently and for ever, which is the failure §B2
   exists to prevent — it converts a loud re-measure into a quiet divergence.
   It is worth knowing this option exists and *why* it is wrong.
3. **A recorded hash instead of the bytes** — `c/shim_pin.h` containing the
   shim's sha256, regenerated on change. Strictly more machinery than a
   symlink, and it needs something to check the regeneration happened. Not
   cheaper.

⚠ **I could not construct a fourth. The symlink is the only zero-machinery way
to make "the row's allocator" and "the programme's allocator" the same bytes,
because it is the only one that does not require anything to be *kept* in
sync.** And it is what `digest_bridge.py`'s own docstring already recommended,
before anyone tried to make it conditional.

## 5.2 ⚠ Call 2 — *"does deleting the preprocessor closure lose anything worth keeping?"*

**Agreed with the manager. It loses nothing, and my reason is narrower and
firmer than "it was wrong twice".**

The closure produced exactly one piece of information the symlink rule does
not: *"the text says `emalloc_shim.h` but no TU reaches it — dead code."*
⚠ **That statement is only useful if it is TRUE, and its truth depended on
`_tu_closure` simulating the same preprocessor states `build.py` compiles in.
It simulated 2 of 8.** So the note was not "useful information that is
sometimes wrong"; it was **a claim about eight states derived from two**, which
is not a weaker version of the claim — it is a different claim wearing the
strong one's words.

⚠ **And the specific failure mode is the worst available.** `TASK_PHP_005` F-8
was a false POSITIVE — noisy, self-correcting, a human investigates and finds
nothing. `TASK_PHP_007` §1.3 is a false NEGATIVE **that prints a reassurance**:
*"dead code … Not treated as a shim user"*, about `ph70-optimize`, which
allocates 1000 times in four of eight cells. **A reader who greps for the
allocator finds a sentence telling them not to look further.** That is the
exact shape of `emalloc_shim.c`'s *"CANNOT BE"*, which the project has now paid
for twice, and it is why I deleted the note rather than softening it.

⚠ **What is genuinely lost, and I want it on the record**: nothing now tells a
row's author that their `#include "emalloc_shim.h"` is unreachable. `spec.md`'s
declared `uses_allocator` is where that judgement lives now, and it is a human's.
If the manager wants it back, it belongs in a **row's `controls/`** — where a
per-row claim can be proved with that row's real build — and never in the
preflight, where it would be a third detector.

## 5.3 ⚠ Call 3 — *"three demotions in three rounds: principle or excuse? I cannot tell from the inside."*

**It is not three demotions, and the shape of the actual record is the answer.**

| # | check | demoted on | outcome |
|---|---|---|---|
| 1 | the `why` size rule | **measurement** — the corpus distribution, with both alternatives refuted (`TASK_PHP_006` §5) | stands |
| 2 | preflight absence → NOTE | **an asserted mechanism** — a deadlock nobody ran | ⚠⚠ **REVERSED THIS TASK.** The deadlock does not exist (§3.2) |
| 3 | the overlap floor | **structure** — the check's input space is unbounded (§2.2) | new |

⚠⚠ **One of the three has already been reversed, by this task, on a
measurement — and it is precisely the one that was demoted on an unverified
mechanism.** A habit does not do that. So the record reads as a process that
demotes for different reasons and reverses the bad one when someone runs it.

✅ **The discriminator I would hand the next manager, because "am I doing this
too often" is not answerable and this is:**

> **Demote on a MEASUREMENT or on a STRUCTURAL argument about the check's input
> space. Never on a mechanism nobody has run.** Demotion 2 was the only one
> whose justification was a mechanism, and it is the only one that was wrong.

**And the honest cost of demotion 3, which I do not want minimised.** The
overlap floor was the **only** mechanical check that looked at the row's C at
all. After the demotion, `provenance.py`'s enforcing half checks the
**citation** — is that span in that tarball — and nothing checks the
**kernel** except *"a row declaring PHP provenance ships one"*. `tier` was
already unvalidated; now the number that was evidence about it is advisory.

⚠ **Two things make me comfortable, and one does not.**
- ✅ The floor has **never adjudicated a real row.** `ph00-smoke` declares
  `php_provenance: false` and returns before the overlap is computed, so every
  firing in the project's history has been on a fixture. The demotion is
  *currently free*, measurably.
- ✅ It was demoted to a **louder** report, not to silence: the number, the
  tier's expectation, an explicit under-expectation line, and the count of
  conditions the heuristic cannot evaluate.
- ⚠ **What does not comfort me: "currently free" expires at the first
  `verbatim` row**, and that is the next row anyone builds. I added
  `PROTOCOL_PHP.md` §F item 9 — *read the overlap number and say what you think
  of it in `NOTES.md`* — because a judgement moved from a tool to a person and
  nothing else in the checklist would have caught that.

⚠⚠ **The risk the manager should actually worry about is not the count of
demotions. It is that the two things demoted for good reasons and the one
demoted for a bad one all LOOK THE SAME in `PROTOCOL_PHP.md` §E's table — a ❌
row.** That is why I made each ❌ row name *what* was demoted and *why*, rather
than listing them.

---

# §6 ⚠⚠ A finding neither the task nor the review has: `--check-stale` cannot see an ADDED file

**`harness/measure.py::_compare` iterates the RECORDED keys.** A file added to
`<row>/c/` has no key, so it cannot be stale:

```python
def _compare(rec, key):
    for rel, want in sorted((rec.get(key) or {}).items()):   # <-- recorded keys only
```

Observed, not reasoned (`.temp/php8/12-added-key-blindspot.log`, and the
bracket's own middle pair):

```
after adding patterns-php/ph00-smoke/c/emalloc_shim.h and editing spec.md:
  STALE  results/gate/ph00-smoke.json   patterns/ph00-smoke/spec.md
  FRESH  results/ph00-smoke.json        18 source(s) + 8 input(s)   <-- the symlink is invisible

  measurement record's c/ keys : ['.../c/kernel.c', '.../c/kernel.h', '.../c/main.c']
  files on disk in c/          : ['emalloc_shim.h', 'kernel.c', 'kernel.h', 'main.c']
  `c/emalloc_shim.h` recorded  : False
```

**Why it matters for §0's design, and it cuts both ways.**

- ✅ **It does not weaken the rule for its purpose.** Once the key exists (it
  does now — the record went from 18 sources to **19**), a shim EDIT moves the
  recorded value and the record goes STALE. That is the case the link is for.
- ⚠ **But a row measured BEFORE its link exists has a record `--check-stale`
  will never complain about**, for ever. **The PREFLIGHT is what closes that,
  not the digest**: `shim_link_audit` refuses the row, so the gate cannot pass
  in that state.

⚠⚠ **So `2 record(s) examined, 0 STALE` does not mean "every source is
pinned" — it means "every source that was pinned still matches".** That
sentence belongs in front of anyone reading the bracket, and I put it in
`PROTOCOL_PHP.md` §E. ⚠ It is a `harness/` property and affects the 33 PAT rows
identically; **I did not touch it** and I am not proposing to — the fix is a
`harness/` edit and a 33-pattern re-gate.

---

# §7 What I did NOT land: `RECAP_PHP.md`, the manager's file

Wording proposed, nothing edited.

- **m2 — `RECAP_PHP.md:188`** cites `harness/build.py:169-172` for the
  `-fuse-ld=lld` insert. `TASK_PHP_006` §3 refuted that span and the
  digest-pinned `common-php/emalloc_shim.h:492` carries the correct
  **168-171**. Two files in the tree disagree and the pinned one is right.
  ⚠ Re-verified by me: `sed -n '168,171p' harness/build.py` is the
  `if mode == "whole" and "clang" in ...` block. **Change `169-172` → `168-171`.**
- **m3 — `RECAP_PHP.md:180`** cites `common-php/emalloc_shim.h:462`; the
  sentence moved to `:463` at `TASK_PHP_006` and `:462` is now a bare `*`.
  ⚠ **And it has moved again** — this task did not touch `emalloc_shim.h`, so
  `:463` still holds. **Change `462` → `463`.**
- **m4 — `RECAP_PHP.md:158`** cites `emalloc_shim.h:340` for the
  `__builtin_mul_overflow` *"same predicate"* claim; that text now lives at
  `:454`/`:471`. **Change `340` → `454`, or drop the line number.**
- **`~115 ms/row` at `RECAP_PHP.md:67` and `:351`.** The measured figure is
  **~135 ms/row** (`TASK_PHP_007` §6, realistic rows including the 668-line
  shim). ⚠ **But the number is now historical in a stronger sense: `gcc -MM` is
  no longer run at all**, so both lines should say so. Suggested for `:351` →
  *"✅ Priced before it was adopted: 2 calls, ~115 ms/row — corrected to ~135 by
  `TASK_PHP_007` §6, and RETIRED by `TASK_PHP_008` §0, which deleted
  `_tu_closure`. The preflight now runs no compiler at all."*
- **Open items affected**, for the manager's reconciliation: **10** (the
  symlink — now unconditional), **13** (the preflight record — now a failure,
  content-collapsed and capped), **14** (the overlap — now reported, and the
  item's own text is the argument for the demotion), **17** (the `c/` subdir
  ban — **lifted**, replaced by `c_digest_audit`), **19** (the `why` band — now
  computed).

---

# §8 The gate, and the closing bracket

## 8.1 The chain, and what it cost

`PROTOCOL_PHP.md` §E's `gate → report → gate`, in full, timed by file
timestamp (⚠ `ps -o etime` is unusable in this sandbox — `TASK_PHP_006` §7):

| command | wall clock | outcome |
|---|---|---|
| `--tool measure ph00` | **7 m 52 s** | `wrote results/ph00-smoke.json`, 18 → **19** sources |
| `gate.py ph00` (pass 1) | **5 m 46 s** | `check.py: FAIL` — **tables only**, exactly as documented |
| `--tool report ph00` | seconds | `wrote results/tables/ph00-smoke.md` |
| `gate.py ph00` (pass 2) | **2 m 59 s** | `check.py: PASS-WITH-BLOCKED-ROWS` |

Pass 1's only two failures were the predicted ones:

```
FAIL [tables] results/tables/ph00-smoke.md is STALE: it cites contract
     ['91d88e1e18b1'] and `spec.md`'s `slb-contract` block now hashes to 191025e448f7.
FAIL [tables] results/tables/ph00-smoke.md is STALE IN ITS CONTENT: 42 line(s) differ
```

⚠ **The `contract_sha256` move is disclosed and is `PROTOCOL.md` rule 6's
subject.** `ph00-smoke`'s contract went
`91d88e1e18b192258a1acc577672b2989e33f84c112615b03090bb011dad5e8b` →
`191025e448f7514c5971f6a50749fbbe00577588eb4ab608c707ac6d5dc06e23`, and the
**only** change inside the fence is the two `uses_allocator` keys
(`.temp/php8/05-contract-move.log`, taken before any cell was built).
⚠ Rule 6's `git show HEAD:… | diff -` is **not vacuous here** — `ph00-smoke` is
an existing row, and `git diff patterns-php/ph00-smoke/spec.md` shows exactly
`+2 / -1` lines, all inside the `provenance` object.

## 8.2 What moved in the gate record — 32 of 1097 leaf values

`git show HEAD:results-php/gate/ph00-smoke.json` vs now
(`.temp/php8/33-gate-record-diff.log`):

```
1079 leaf values before, 1097 after
  moved: 14   added: 18   removed: 0
  verdict: PASS-WITH-BLOCKED-ROWS -> PASS-WITH-BLOCKED-ROWS
  contract_sha256: 91d88e1e18b1 -> 191025e448f7

  source_sha256 movers/adds:
    /source_sha256/common/digest_bridge.py               298bac49 -> aaa5931d
    /source_sha256/patterns/ph00-smoke/c/emalloc_shim.h  None     -> aa9abf48
    /source_sha256/patterns/ph00-smoke/spec.md           a365d5d5 -> 97e3259a

  ⚠ DETERMINISTIC leaves moved (Ir / checksum / md5 / identity / inputs): 0
  everything else that moved (12): contract_sha256, marginal_ir_env x2, miri x1,
    published_table x2, table_render x2, loud x4
```

✅ **Zero `Ir`, zero checksum, zero md5, zero identity, zero input hash, and
the verdict is unchanged from the committed record.** The three `source_sha256`
movers are exactly the three files this task touched that the gate digest
reaches, and `patterns/ph00-smoke/c/emalloc_shim.h` appearing as a **new key**
is §0 landing:

```
c/ keys in the gate record: ['patterns/ph00-smoke/c/emalloc_shim.h',
                             'patterns/ph00-smoke/c/kernel.c',
                             'patterns/ph00-smoke/c/kernel.h',
                             'patterns/ph00-smoke/c/main.c']
```

## 8.3 The closing bracket

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
FRESH       results/gate/ph00-smoke.json               29 source(s)
FRESH       results/ph00-smoke.json                    19 source(s) + 8 input(s)

2 record(s) examined, 0 STALE
```

⚠ **28 → 29 gate sources and 18 → 19 measurement sources.** That difference is
the whole of §0, expressed as a number.

## 8.4 The closing no-touch check, by bytes, against three baselines

```
$ python3 .temp/php5/snapshot.py control
control: 27 files snapshotted, one byte-appended
  CHANGED  common/slb.py  2abd87f76712 -> 27618554643a
CONTROL FIRED

$ python3 .temp/php5/snapshot.py check .temp/php5/pat-snapshot.json           # TASK_PHP_005
snapshot check: 2966 recorded, 2966 now, 0 difference(s)
$ python3 .temp/php5/snapshot.py check .temp/php7/pat-snapshot-007-start.json # TASK_PHP_007
snapshot check: 2966 recorded, 2966 now, 0 difference(s)
$ python3 .temp/php5/snapshot.py check .temp/php8/pat-snapshot-008-start.json # MINE
snapshot check: 2966 recorded, 2966 now, 0 difference(s)
```

✅ **`harness/`, `common/`, `patterns/`, `results/` and `pilot/` are
byte-identical to all three baselines, with the tool proved able to fail
first.** ⚠ That matters more this task than last, because `why_band()` **opens
33 files under `patterns/`** on every preflight — this is what proves it only
reads them.

The tree at the end:

```
$ git status --porcelain
 M .tasks-php/PROTOCOL_PHP.md          M results-php/gate/ph00-smoke.json
 M PLAN_PHP.md                         M results-php/ph00-smoke.json
 M common-php/digest_bridge.py         M results-php/preflight/_norow.preflight.json
 M common-php/emalloc_shim.c           M results-php/preflight/ph00.preflight.json
 M harness-php/gate.py                 M results-php/tables/ph00-smoke.md
 M harness-php/provenance.py          ?? .tasks-php/TASK_PHP_008_REPORT.md
 M patterns-php/ph00-smoke/spec.md    ?? patterns-php/ph00-smoke/c/emalloc_shim.h
```

**Nothing under `harness/`, `common/`, `patterns/`, `results/` or `pilot/`.**
`patterns-php/ph00-smoke/c/emalloc_shim.h` is the new symlink and the manager
stages it.

⚠ **One ordering note for the manager.** I edited `gate.py`'s docstring *after*
gate pass 2 (a dangling `.temp/php8/…` citation I had invented before the log
existed), which would have left the preflight record's `harness_php_sha256`
describing a different file. I re-ran `gate.py --preflight ph00` afterwards so
the last recorded run carries the shipped hash. ⚠ `harness-php/*.py` is **not**
in any gate record's `source_sha256` (that is `RECAP_PHP.md` open item 13's
whole point), so this cost a preflight and not a re-gate — but the record would
have been misleading and that is the thing the record exists not to be.


---

# §8b ⚠⚠⚠ THE FIX FOR M4 CREATED A REAL DEADLOCK, AND I FOUND IT BEFORE SHIPPING

**This is the most important thing in the report and it is about my own work.**

`TASK_PHP_007` M4 disproved a deadlock the engineer had **asserted**. M5 then
said a record whose every run FAILED counts as no record. ⚠ **Composed, those
two are self-referential:**

```
run 1   no record                     -> coverage problem -> PREFLIGHT FAILED
                                      -> writes a record whose ONLY run FAILED
run 2   record exists, only run FAILED (M5)
                                      -> coverage problem -> PREFLIGHT FAILED
run N   ... for ever, and NOTHING an operator can do fixes it
```

That is the **fresh-clone path**: delete or lose `results-php/preflight/` and
the programme is unrunnable, permanently, with no escape flag.

⚠ **I did not spot this by reading. I wrote the loop and ran it**
(`.temp/php8/g4_selfdeadlock.py`, `21-selfdeadlock-BEFORE.log`) — with the
*obvious* rule, which is what I had already written and was about to ship:

```
--- (a) MUST FIRE -- the naive rule ('a run that FAILED never certifies')
    run 1..6: coverage problems BEFORE the write = 1   verdict = 'PREFLIGHT FAILED'
    -> STILL FAILING after 6 runs. ⚠⚠ DEADLOCK.
--- (b) MUST NOT FIRE -- the rule actually shipped   [at that point, the same rule]
    -> STILL FAILING after 6 runs. ⚠⚠ DEADLOCK.
```

✅ **The repair, and it is also the honest reading of the record.** A run that
failed *only* on a coverage problem still verified the shim, the digest bridge,
the `c/` digest keys, the allocator symlink, the overlap self-test, the manifest
and provenance. **It certified THIS tree**; what it complained about was
another row's paperwork. So `_run_is_certifying` discounts problems tagged
`_COVERAGE_TAG` and judges only **substantive** ones. `22-selfdeadlock-AFTER.log`:

```
--- (a) MUST FIRE -- the naive rule
    -> STILL FAILING after 6 runs. ⚠⚠ DEADLOCK.        <-- control still fires
--- (b) MUST NOT FIRE -- the rule actually shipped
    run 1: coverage problems = 1   verdict = 'PREFLIGHT FAILED'
    run 2: coverage problems = 0   verdict = 'preflight only'
    -> CONVERGED after 2 run(s). NO DEADLOCK.
  naive rule deadlocks : True   CONTROL FIRED
  shipped rule converges: True
```

And M5 still fires on everything it should (`23-coverage-cap-AFTER.log`):
three must-fire cases (`PREFLIGHT FAILED` with a substantive problem,
`provenance_skipped`, `shim_ok=false`) and the must-NOT-fire clean run. The M4
repair loop now converges **at the third repair** rather than needing a
separate certifying pass.

⚠⚠ **THE LESSON, AND IT IS NOT "I MADE A MISTAKE".** `TASK_PHP_007` M4 was
right that the engineer's deadlock did not exist — **and the reviewer said in
terms *"I am not recommending the hard failure"***. The manager's §3 M4 asked
for the hard failure anyway and asked me to reproduce the deadlock if I still
believed in one. **I did not believe in one; I built the hard failure; and the
hard failure created a different deadlock that is real.** ⚠ **A refuted
mechanism is not a licence for the design it was arguing against — it only
removes one argument.** The engineer's *conclusion* (loud beats unrunnable) had
a case behind it that their *stated mechanism* got wrong, which is
`PROTOCOL.md` rule 9's conclusion-versus-mechanism split, arriving from the
other direction.

⚠ **`_run_is_certifying`'s docstring says "do not simplify this back to
`verdict == PREFLIGHT FAILED`", and `g4_selfdeadlock.py`'s must-fire control
exists to catch exactly that edit.** The two `preflight coverage:` message
producers now build their prefix from `_COVERAGE_TAG`, so the tag and the
filter cannot drift apart.

---

# §9 Clean negatives, and structural facts I verified rather than asserted

Re-running these is wasted time.

1. ✅ **The frozen PAT tree is untouched, BY BYTES, against three baselines.**
   `snapshot.py`'s control fired first (`CONTROL FIRED`), then 2 966 paths
   matched `TASK_PHP_005`'s baseline, `TASK_PHP_007`'s baseline, and my own —
   opening and closing (§8). ⚠ **`why_band()` READS `patterns/*/spec.md` on
   every preflight, and the closing snapshot is what proves it never writes.**
2. ✅ **`shim_link_audit`, `c_digest_audit` and `_walk_files` call no
   subprocess, no compiler and no regex.** Verified by AST with docstrings
   excluded, because a `grep` finds `gcc` three times in `shim_link_audit`'s
   docstring and would have supported the opposite conclusion
   (`.temp/php8/20-structural-checks.log`):
   ```
   shim_link_audit calls: ['glob.glob','notes.append','os.path.basename',
     'os.path.exists','os.path.isdir','os.path.islink','os.path.join',
     'os.path.realpath','os.path.relpath','os.readlink','problems.append','sorted']
   -> no subprocess / no regex / no compiler: True
   ```
3. ✅ **`Not treated as a shim user` survives only as history.** The one hit in
   `harness-php/` is `gate.py:414`, inside `shim_link_audit`'s docstring
   recording why the note was deleted. No code can emit it.
4. ✅ **`preflight()` has exactly EIGHT sites that can add a problem** (AST
   count of `problems.extend`/`append`), matching the docstring's *"NINE
   things, EIGHT of which can FAIL"* — the ninth is `why_sizes`, which by
   design cannot. ⚠ I wrote that number into the docstring and then counted it
   from the code, because `PROTOCOL.md` rule 13 is about exactly this line
   rotting: it said "FIVE, all of which can fail" and then "SEVEN" over a body
   of seven-plus-two. **The docstring now tells the reader to re-count.**
5. ✅ **`ph51-linked` still passes and is in both digests.** The
   must-NOT-fire for §0. Without it, "every row is refused" would look like a
   working guard.
6. ✅ **The `#elif 0` fix moved exactly ONE self-test case.** Verified by
   re-running all nine under a verbatim re-implementation of `TASK_PHP_006`'s
   `_strip_dead_conditionals`. A fix that moved others would have been
   retuning the normaliser, not repairing it.
7. ✅ **The overlap self-test's must-NOT-fire cases still hold at 100 %** (D, E
   and the new E2), so the demotion did not come with a normaliser that
   quietly stopped measuring.
8. ✅ **The real `results-php/preflight/` was byte-identical before and after
   every in-process probe** (`14-coverage-cap.log`), and the one genuine plant
   restored exactly (`RESTORE EXACT: True`).
9. ✅ **The naive `_run_is_certifying` still deadlocks, and the probe still
   sees it.** `g4_selfdeadlock.py`'s part (a) is a must-fire control that
   re-implements the rule I nearly shipped; it fires both before and after the
   repair (§8b). ⚠ **A repair whose control stops firing is a repair that
   deleted its own test.**
10. ⚠ **A clean negative I could NOT get, stated as such:** I did not verify
   that a *shim edit* stales the measurement record, because doing so means
   editing `common-php/emalloc_shim.h` and paying a second full re-measure and
   re-gate inside this task. **What I verified instead is the mechanism**:
   `patterns-php/ph00-smoke/c/emalloc_shim.h` and `common-php/emalloc_shim.h`
   hash identically (`aa9abf48535e8df9`) because the first is a symlink to the
   second, and the key is now in the record (18 → **19** sources), so
   `_compare` must move it. **That is one inference, and it is the one thing in
   this report I have reasoned rather than run.**

---

# §10 What I refute or correct

**Launched from 20. Reconciliation is the manager's, not mine.**

### Against the MANAGER (2)

1. ⚠⚠ **§0's stated cost is wrong, in the manager's favour.**
   *"An `emalloc_shim.h` edit will mark every php row stale … a real cost in
   **re-gates**."* **The gate half was already unconditional and has been since
   `TASK_PHP_002`**, through `digest_bridge.py`'s hash sitting in every php
   gate record's `source_sha256`; `TASK_PHP_006`'s own shim edit staled `ph00`'s
   gate record while `ph00` carried no link. **The marginal price of the
   unconditional link is a re-measure + a render, not a re-gate**
   (`02-digest-reality.log`, §5.1). ⚠ **And the measurement the manager said was
   missing is one command**: the shim has been edited in **3 of 7** php tasks,
   **two of the three for prose** — which argues for batching prose fixes, and
   I have put that in `PROTOCOL_PHP.md` §B2.
2. ⚠ **"This task should REMOVE more code than it adds" is true of §0 and false
   of the task.** §0 is **−82** code lines; the task is **+90**, because M3,
   M4, M5, m1 and m6 each add a check that did not exist. Per-section
   accounting in §0.2. I am not presenting this as a win.

### Corrected, not refuted (1)

3. ⚠ **`TASK_PHP_007`'s `~135 ms/row` correction is right and is now moot.**
   `gcc -MM` is not run at all; the preflight invokes no compiler. Both
   `RECAP_PHP.md` sites should say so rather than carry a corrected price for a
   thing that no longer happens (§7).

### A near-miss I caught in my own work (1)

4. ⚠⚠ **Fixing m6 nearly published a FOURTH answer to the `why` size.**
   `why_band()` computes the PAT band instead of quoting a constant — and my
   first spelling, `round(0.9*(n-1))`, printed **`p90 2062`** where the
   published band says **1817**. Both are correct percentiles of the same 33
   values (`.temp/php8/07-why-band.log`):
   ```
   p90 by floor(0.9*(n-1)) = vals[28] = 1817     <-- what TASK_PHP_006 published
   p90 by round(0.9*(n-1)) = vals[29] = 2062     <-- my first spelling
   linear interpolation                 = 2013
   ```
   `RECAP_PHP.md`'s size box **warns that this quantity already has three
   answers and that arbitrating it again is the wrong move**, and de-rotting a
   constant is exactly how a fourth gets in — silently, in a fix that looks
   like pure hygiene. Pinned to `floor`, with the reason in the code.
   ✅ **And while checking, I confirmed the quartiles `527 / 989 / 1544` quoted
   in `why_sizes` and `PROTOCOL_PHP.md` §E are CORRECT** — they are Tukey's
   hinges over the same 33 values (lower half median `(500+554)/2 = 527`, upper
   `(1509+1578)/2 = 1543.5`). I checked rather than assumed, because my first
   instinct was that they were wrong too.

### Against MY OWN work, found before shipping (1)

5. ⚠⚠⚠ **The M4 + M5 combination the task asked for is a REAL DEADLOCK, and I
   built it before I caught it.** `TASK_PHP_007` M4 disproved the deadlock the
   engineer *asserted*; ⚠ **the fix for that refutation creates a different one
   that is real** — a lost `results-php/preflight/` makes the programme
   permanently unrunnable, with no escape flag. Measured over six runs, then
   repaired, with the must-fire control retained (§8b). ⚠ **The reviewer's own
   sentence was *"I am not recommending the hard failure"*, and the task file
   asked for it anyway. A refuted mechanism removes one argument; it does not
   license the design that argument opposed.**

### Upheld against my own attempts to break them (3)

6. ✅ **`TASK_PHP_007` M1 and m1 both reproduce**, and both are closed
   (`11-digest-audit.log`).
7. ✅ **`TASK_PHP_007` M4's deadlock refutation reproduces end to end**, not
   just as a code reading: the repair loop converges on three uncovered rows
   (§3.2). ⚠ It is right about the deadlock it examined; §8b is a different one.
8. ✅ **`TASK_PHP_007` M2's `#elif 0` bug reproduces exactly** — 100 % under the
   `TASK_PHP_006` code, 11 % now (`04-elif-control.log`).

---

# §11 What I did NOT do, and what I am unsure about

- **I did not touch `harness/`, `common/`, `patterns/`, `results/` or
  `pilot/`.** Proved by bytes against three snapshots, with the tool's control
  fired (§9.1, §8). ⚠ `why_band()` **reads** 33 files under `patterns/`; the
  closing snapshot is the evidence that reading is all it does.
- **I did not edit `RECAP_PHP.md`.** Four citation corrections and five open
  items are proposed in §7.
- **I did not fix `--check-stale`'s added-file blindness** (§6). It is a
  `harness/` edit and a 33-pattern re-gate, and it affects PAT identically. I
  do not think it should be fixed for this; I think it should be *known*.
- **I did not add the other nine dead-conditional spellings** (§2.2), on
  purpose, and the manager may disagree. If the answer is "add them anyway",
  the place is `_strip_dead_conditionals` and the cost is that
  `unevaluable_conditionals`'s count becomes the only honest signal again the
  next time somebody writes a tenth.
- **I did not verify a shim EDIT stales the measurement record by running one**
  (§9.10). It costs a second full re-measure + re-gate inside this task. The
  mechanism is verified; the end-to-end run is not. **This is the one claim in
  the report I have reasoned rather than measured, and if the manager wants it
  measured it is one `touch`-and-re-gate away — ideally batched with the next
  real shim edit.**
- **`MAX_RUNS = 40` is a guess.** I have no measurement that says 40 rather
  than 20 or 200. What I measured is that the cap *fires*, that it keeps the
  evidence-carrying entries, and that with content-collapse in place ordinary
  use no longer approaches it at all (§3.1). ⚠ The number only matters on a
  tree that genuinely differs between runs, which is a state I did not model
  beyond the synthetic 120.
- **`c_digest_audit` follows directory symlinks.** I chose that over refusing
  them, because refusing would have been the over-strict half of the mistake
  `TASK_PHP_007` called out. ⚠ **The cost is that a row symlinking a large
  extracted subtree owes one flat link per file** — for `Zend/` that is
  ~100 links, not 8. I priced this as acceptable because the alternative is
  banning the layout again, but **nobody has built such a row and the number
  might be the thing that decides it.** Say so with the row.
- **`uses_allocator` is unvalidated by construction, and I deliberately did not
  put it in `REQUIRED`.** A missing one is a loud printed line, not a refusal.
  ⚠ If the manager wants it required, the *presence* check is safe and the
  *value* check is the third detector — the distinction is easy to lose and
  `provenance.py::ALLOC_KEY`'s comment is the only thing guarding it.
- **I did not re-run `.temp/php7/`'s other nine generators.** `a1`, `a5` and
  `b3` were re-run because §0.3 named them; the rest (`a2`, `a3`, `a4`, `a6`,
  `a7`, `a8`, `a9`, `b1`, `b2`, `b4`) measure code paths this task deleted or
  replaced, and their findings are addressed by construction rather than by
  re-measurement. ⚠ `a6_scaling.py` is the one I would re-run if the manager
  wants a number: it measured the `gcc -MM` price, which is now **zero**, and I
  have asserted that from the AST rather than from a stopwatch.
- **I did not re-render or re-gate anything but `ph00-smoke`.** It is the only
  php row.
- ⚠⚠ **`g4_selfdeadlock.py` drives `preflight_coverage_audit` +
  `write_preflight_record` in a loop; it does NOT shell out to
  `gate.py --preflight`.** The loop it models is `main()`'s failure path
  (`record["verdict"] = "PREFLIGHT FAILED"; write_preflight_record(record)`),
  which I read rather than executed for that probe. **I consider the deadlock
  and its repair established** — the subprocess version of the same loop was
  run in `g3` (§3.2) and behaves identically — **but the two halves were
  measured by different probes and a reviewer should know that.**
- ⚠ **`_run_is_certifying`'s coverage discount is a string prefix match.**
  `_COVERAGE_TAG` is used by both message producers so they cannot drift, but a
  future stage that emits a problem *starting with* `preflight coverage:` would
  be silently discounted. That is a small enumeration surface of exactly the
  kind this task spent its day removing, and I could not see a way to avoid it
  without giving problems a structured type — which is a bigger change than
  this task should make. **Named rather than hidden.**

---

# §12 Durable facts, and where I put them

⚠ I cannot write `.memory/` (subagent) and `RECAP_PHP.md` is the manager's, so
these went into the files this programme owns. Listed so the manager can lift
them.

| fact | where it now lives |
|---|---|
| A guard whose correctness depends on **enumerating idioms** is reopened by the next idiom; when a guard is reopened twice, **change what it asks**, do not sharpen how it asks it | `PROTOCOL_PHP.md` §B2 (as the durable lesson), `gate.py::shim_link_audit` docstring |
| **Enumerating FILES is sound where enumerating IDIOMS is not** — the discriminator between §B2's repeated failure and §B3's working audit | `PROTOCOL_PHP.md` §B3, `gate.py::c_digest_audit` docstring |
| The php **gate** digest has pinned the shim unconditionally since `TASK_PHP_002` via `digest_bridge.py`; only the **measurement** digest needs the per-row link | `PROTOCOL_PHP.md` §B2, `gate.py`'s header block |
| ⚠ `measure.py --check-stale` cannot see an **added** file — `0 STALE` means "everything pinned still matches", not "everything is pinned" | `PROTOCOL_PHP.md` §E |
| **Demote a check on a measurement or on a structural argument, never on an unrun mechanism** — the one demotion justified by a mechanism is the one that was reversed | this report §5.3; ⚠ **worth a `.memory/` line, and it is the manager's to write** |
| A percentile has conventions; **de-rotting a hard-coded statistic is how a fourth answer gets published** | `gate.py::why_band` |
| `uses_allocator` is **declared, never detected**, and acquiring a consumer makes it a third detector | `PLAN_PHP.md` §6, `provenance.py::ALLOC_KEY`, `PROTOCOL_PHP.md` §D |
| A regression case proves nothing until the code it guards is shown to **fail** it; the `#elif` fix needed a must-NOT-fire (E2) as much as a must-fire (B4) | `provenance.py::OVERLAP_CASES`, `.temp/php8/g1_elif_control.py` |
| ⚠⚠⚠ **A refuted mechanism is not a licence for the design it argued against.** `TASK_PHP_007` M4 disproved an asserted deadlock; building the hard failure it seemed to license created a real one | `gate.py::_run_is_certifying` docstring, this report §8b |
| ⚠ **Two checks that are each correct can deadlock when composed**, and neither one's tests would show it — the loop has to be run | `.temp/php8/g4_selfdeadlock.py`, `gate.py::_COVERAGE_TAG` |
| A regression case proves nothing until the code it guards is shown to **fail** it; the `#elif` fix needed a must-NOT-fire (E2) as much as a must-fire (B4) | `provenance.py::OVERLAP_CASES`, `.temp/php8/g1_elif_control.py` |

