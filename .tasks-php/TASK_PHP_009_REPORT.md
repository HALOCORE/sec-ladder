# TASK_PHP_009 — adversarial review of `TASK_PHP_008`, and the last gate on Phase 0 — REVIEWER REPORT

**Role:** research reviewer. **Launched from a running count of 23.**
**Reconciliation is the manager's job.** What I refute is in §9.

> **VERDICT UP FRONT.** ⚠ **No blocker, under this project's own definition
> (`.tasks/PROTOCOL.md`: *blocker = invalidates results*). Nothing published is
> wrong and the PAT tree is untouched.** **Four majors**, two of them in the
> headline design and two in the deadlock repair. ⚠⚠ **But I am not returning a
> clean bill either: two of the four majors are in the enforcement layer the
> FIRST REAL ROW will lean on, both are cheap, and one of them is made MORE
> likely by `PROTOCOL_PHP.md` §B3 as written.** My recommendation is in §8:
> **close Phase 0, and land M1+M2 as a named precondition on the first row
> rather than as open items in a queue** — that is a fraction of a task, not a
> phase.
>
> **Bracket, first and last, both pasted.** `.temp/php9/01-bracket-open.log`,
> `.temp/php9/19-bracket-close.log`:
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
> ⚠ **And §4 asked what `0 STALE` now MEANS. The engineer's sentence is right
> and INCOMPLETE — see m3: it also does not mean "every pinned source still
> EXISTS".** Measured, not read.
>
> **No-touch, BY BYTES, control fired first, four baselines, open and close**
> (`02-snapshot-open.log`, `19-bracket-close.log`):
>
> ```
> $ python3 .temp/php5/snapshot.py control
> control: 27 files snapshotted, one byte-appended
>   CHANGED  common/slb.py  2abd87f76712 -> 27618554643a
> CONTROL FIRED
>
> .temp/php5/pat-snapshot.json            snapshot check: 2966 recorded, 2966 now, 0 difference(s)
> .temp/php7/pat-snapshot-007-start.json  snapshot check: 2966 recorded, 2966 now, 0 difference(s)
> .temp/php8/pat-snapshot-008-start.json  snapshot check: 2966 recorded, 2966 now, 0 difference(s)
> .temp/php9/pat-snapshot-009-start.json  snapshot check: 2966 recorded, 2966 now, 0 difference(s)   <-- mine
>
> $ git status --porcelain
> (empty)
> ```
>
> **Planting disclosure — FOUR plants into committed paths, every one restored
> in a `finally:` and verified BY BYTES.**
>
> | plant | probe | restore evidence |
> |---|---|---|
> | `results-php/ph99-ghost.json` created; 8 real `gate.py` runs appended to `results-php/preflight/*.json` | `a4_orphan_deadlock.py` | `RESTORE EXACT (sha256 per file, 7 file(s)): True`, `git status: (clean)` |
> | one comment line appended to `common-php/emalloc_shim.h` | `a6_shim_edit.py` | `RESTORED BY BYTES: True (aa9abf48535e8df9 -> aa9abf48535e8df9)` |
> | `patterns-php/ph00-smoke/c/emalloc_shim.h` moved aside | `a9_survival.py` | `islink=True readlink='../../../common-php/emalloc_shim.h' matches original: True` |
> | `patterns-php/.ph93-dotted/` created, real `gate.py --preflight` run on it | `a10_dotted_e2e.py` | `results-php/ exact = True`, `patterns-php/ listing unchanged = True`, `git status: (clean)` |
>
> ⚠ `a6` left one committed file modified (`results-php/preflight/_norow.preflight.json`,
> +52 lines) that its own `finally:` did not cover — **caught by the
> `git status` line in the same output** and restored byte-exactly from
> `git show HEAD:` (`095a83c9a7bdd3bf…` both sides). **That residue is itself
> m5.** The final `git status --porcelain` is empty.
>
> **Scratch:** `.temp/php9/` — **21 logs, 10 probes**, one PAT snapshot.
> Every fixture tree and both ELF binaries deleted (`fix/`, `survival/`, two
> `bin-v*`); `.temp/php5–8` re-run, never modified, never deleted — counts
> unchanged at **29 / 34 / 28 / 49**, `find -newermt` shows no file created
> in any of them.

---

## Summary

| § | attack | result |
|---|---|---|
| §1.1 | **is the row enumeration complete?** | ⚠⚠ **NO — M1.** A **dotted row directory** is invisible to `shim_link_audit`, `c_digest_audit`, `why_sizes` AND `preflight_coverage_audit`, while `build.py::pattern_dir` and `provenance.py` both resolve it. **`gate.py --preflight .ph93` returned rc=0 on a row carrying a REGULAR-FILE allocator copy and an unkeyed subdirectory source**, with the identically-defective normally-named row refused as the control. |
| §1.2 | does the link survive git/`cp -r`/`tar`? | ✅ **All five operations behave, and every failure mode is REFUSED.** git stores `120000`; a real `git clone` passes the audit; `cp -r`/`cp -a` keep the link but it dangles at the new depth → refused; a regular-file copy → refused; `tar -h` → refused. |
| §1.3 | is it the shim's BYTES in the digest? | ✅ **Yes, both digests, verified from the COMMITTED records:** `patterns/ph00-smoke/c/emalloc_shim.h = aa9abf48535e8df9 == sha256(common-php/emalloc_shim.h)`. |
| §1.4 | **FRESH + preflight passes + allocator bytes differ?** | ⚠⚠ **CONSTRUCTED — M2.** `c/kernel.c` → `#include "../aux/row_alloc.h"`. Compiles, runs the row's own allocator, is in **NEITHER** digest. Editing it changed the binary's behaviour (`tally=1 → tally=1000`) with **0 digest keys moved and 0 preflight problems**. |
| §2 | re-run `g4_selfdeadlock.py` | ✅ **Both arms reproduce**, unmodified: naive rule deadlocks (control fires), shipped rule converges in 2. |
| §2 | can the coverage discount be widened? | ✅ **NO.** AST over every `problems.append/extend` in `gate.py`: the **only** message that starts with author-controlled text is the coverage one itself. Both producers build from `_COVERAGE_TAG`; the one bare literal is a `print`. 5 cases run, incl. a crafted one. |
| §2 | **is there a SECOND deadlock?** | ⚠⚠ **YES — M3**, run end to end on the real tree. An orphan `results-php/<row>.json` makes the **global** coverage stage fail every invocation including the bracket, the prescribed repair **cannot** succeed, and the message printed at that moment says *"⚠ THERE IS NO DEADLOCK"*. ⚠ **M4** is the same shape through the provenance stage on a box with no tarball. |
| §3 | is `c_digest_audit` exhaustive? | ✅ **YES on all six classes the task names** — dotfile, dot-directory, symlinked directory, nested twice, link out of the row, broken link, FIFO — plus cycle-safety and two must-NOT-fires. 10 fixtures, all as expected. |
| §3 | are `extract_sha256` / `c_file` exact? | ✅ **Exact — about the CITATION, and silent about the KERNEL.** The demotion cost is real and the engineer priced it correctly; `g5` reproduces 89 % / 5 % / 5 %. |
| §3 | can the record grow without bound? | ⚠ **YES — m2.** `MAX_RUNS` exempts every evidence-carrying run: **1000 distinct failing runs → 1000 kept, 0 dropped.** The engineer's 120-run cap test used only no-problem runs. |
| §4 | the shim edit end to end | ✅ **RUN, and the inference is upheld.** Both records go **STALE** on `patterns/ph00-smoke/c/emalloc_shim.h`. `TASK_PHP_008` §9.10's one reasoned claim is now measured. |
| §4 | the record diff, spot-checked | ✅ **Reproduced leaf for leaf, independently.** Zero deterministic movement — and my own classifier's three "deterministic" hits are substring false positives, named in §7.9. |

---

# §1 PRIMARY TARGET — is the unconditional link actually unconditional?

## 1.1 ⚠⚠ M1 (major) — a row can hide from `glob`, and the hole is bigger than the task guessed

**`harness-php/gate.py:462`** (`shim_link_audit`) and **`harness-php/gate.py:352`**
(`c_digest_audit`) both iterate `glob.glob(os.path.join(patterns_dir, "*"))`.
`glob` never matches a leading dot. **The row resolvers the rest of the
programme uses do not agree with that:**

```
harness/build.py:81-89   pattern_dir()   -> os.listdir(PATTERNS)      SEES a dotted row
harness-php/provenance.py:841-843       -> glob(PATTERNS + row + "*") SEES it (the row string carries the dot)
harness-php/gate.py:462, :352           -> glob(PATTERNS + "/*")      BLIND
harness-php/gate.py:558  why_sizes()    -> glob("patterns-php/*/spec.md")  BLIND
harness-php/gate.py:809  coverage audit -> glob("results-php/*.json")      BLIND to its RECORD
harness/measure.py:303   check_stale()  -> glob("results/p*.json")         BLIND to its RECORD
```

`.temp/php9/16-dotted-chain.log` — the glob semantics, run:

```
   glob('patterns-php/*')        -> ['ph94-normal']
   glob('patterns-php/.ph93*')   -> ['.ph93-dotted']            <-- provenance's spelling
   os.listdir                    -> ['.ph93-dotted', 'ph94-normal']   <-- build.py's

   files on disk in results-php/ : ['.ph93-dotted.json', 'gate', 'ph94-normal.json', 'preflight']
   glob('results-php/*.json')    -> ['ph94-normal.json']
   preflight_coverage_audit sees: ["... 2 php record(s) have NO preflight record: ['results-php/ph94-normal..."]
```

⚠ **So the coverage audit — the *"cheapest honest substitute"* for the one
thing `PROTOCOL_PHP.md` §E marks ❌ NOT enforced — is blind to exactly the
record it exists to detect.**

### End to end, on the REAL tree, with a fired control (`17-dotted-e2e.log`)

I planted `patterns-php/.ph93-dotted/` carrying **two things the audits refuse
on a normally-named row**: a **regular-file copy** of `emalloc_shim.h`, and
`c/sub/payload.h` with no flat key.

```
=== the SAME two defects on a NORMALLY-NAMED row are refused -- the control ===
    shim_link_audit: 1   c_digest_audit: 1   CONTROL FIRED
      | allocator: ph93-dotted: ph93-dotted/c/emalloc_shim.h is a REGULAR FILE, not a symlink...
      | digest: ph93-dotted: c/sub/payload.h is COMPILED and in NO DIGEST.

=== the REAL gate, on the dotted row ===
    preflight
      ok   every patterns-php/*/c/ file has a digest key (RECAP_PHP.md open item 17)
      ok   <row>/c/emalloc_shim.h symlink, UNCONDITIONAL (PROTOCOL_PHP.md §B2, TASK_PHP_008 §0)
           | ph00-smoke: c/emalloc_shim.h OK -- symlink, in BOTH digests
      ok   provenance .ph93
           |   .ph93-dotted: NOT A PHP ROW -- php_provenance=false...
           | 1 row(s) checked, 0 FAILED
      ok   every php record has a CERTIFYING preflight record beside it
    preflight OK (nothing else run)
    rc=0
```

⚠⚠ **`ok every patterns-php/*/c/ file has a digest key` is a literally false
statement about the tree at the moment it is printed**, and the provenance
stage names the row on the line above it — so the operator can see the row
exists and see a green line about *"every"* row in the same block.

**Concrete failure scenario.** An author parks a work-in-progress row as
`patterns-php/.ph07-wip/` to keep it out of a sweep, builds and measures it
through the sanctioned `gate.py --tool measure .ph07` (provenance resolves it,
both audits are blind, the preflight is green), later renames it, and the
numbers were taken under whatever was in `c/`. Nothing in the programme ever
looked at that row's `c/`, and neither `--check-stale` nor `--audit` ever saw
its two records.

### ⚠ Where I disagree with the manager's own framing (§6 call 1)

> *"If a row can hide from `glob`, the whole argument collapses and we are back
> to whack-a-mole with a smaller board."*

**No — and the distinction matters more than the bug.** The idiom detector had
**no complete enumeration available**: there was no function anywhere that
returned "every way to spell an `#include`". Here there **is** one, it is one
call, and `build.py` already uses it. The audit and the builder can be made to
enumerate the *same set*, and that set is then provably complete against the
only resolver that decides what gets compiled. ⚠ **This is a wrong enumeration,
not an unboundable one — which is the exact property §B3 claims and the exact
property that makes the fix a substitution rather than a round of the game.**

**Fix (not applied — I do not fix):** in `shim_link_audit`, `c_digest_audit`
and `why_sizes`, iterate `os.listdir(patterns_dir)` rather than `glob(*)`; and
in `preflight_coverage_audit`, `os.listdir(rdir)` filtered on `.json`. Then add
one negative: a dotted row must be **refused by name** (it can never be keyed —
`glob` cannot reach its records either), which is the same verdict
`c_digest_audit` already gives a dotted *file*.

## 1.2 ✅ Clean negative — the link survives every operation the project performs

`.temp/php9/14-survival.log`, all run:

```
(A1) git ls-files -s
     120000 ee8edf56df4a1ee1b9e2455b43f5dd24c98ed46b 0  patterns-php/ph00-smoke/c/emalloc_shim.h

(A2) a real `git clone --no-hardlinks` of this repo
     islink: True   readlink: ../../../common-php/emalloc_shim.h
     resolves to a real file: True   sha256 aa9abf48535e8df9
     the audit run against the CLONE: 0 problem(s)

(A3) git checkout d493707^  (the commit before the link landed)
     c/emalloc_shim.h present: False
     the audit against that tree: 1 problem(s)
       | allocator: ph00-smoke: ph00-smoke/c/emalloc_shim.h IS ABSENT.

(A4) cp -r  (the default)       islink=True   regular file=False
     cp -a  (archive)           islink=True   regular file=False
     ⚠ but the relative target does not resolve from the new location: exists = False
     the audit on the `cp -r` copy: 1 problem(s)
       | allocator: ph01-cloned: ...-> '../../../common-php/emalloc_shim.h' resolves to ... not ...
     the audit on a REGULAR-FILE copy (`cp -L` / copyfile): 1 problem(s)
       | allocator: ph02-cloned: ...c/emalloc_shim.h is a REGULAR FILE, not a symlink...

(A5) tar -cf     lrwxrwxrwx ... ph00-smoke/c/emalloc_shim.h -> ../../../common-p
     tar -cf -h  -rw-rw-r-- ... 33522 ... ph00-smoke/c/emalloc_shim.h
```

⚠ **The task's guess about `cp -r` is wrong and the truth is better.** GNU
`cp -r` **preserves** the symlink; what breaks is that the *relative* target
does not resolve from a new depth, so the copy carries a **dangling** link —
and `shim_link_audit`'s `realpath != want` arm catches it with the right
message. **The regular-file case (`cp -L`, `tar -h`, `shutil.copyfile`, a
"duplicate the row" script) is still refused, explicitly, by name.**

⚠ **One thing worth the manager knowing (informational, not a defect):** the
rule is **not retroactive**. Every checkout of a commit before `d493707` fails
the preflight on `ph00-smoke`. That is loud rather than silent and I think it
is correct — but a bisect over php history will hit it.

## 1.3 ✅ Clean negative — the digest carries the shim's BYTES

From the **committed** records, not from a re-run (`10-record-diff.log`):

```
gate         c/emalloc_shim.h = aa9abf48535e8df9   == sha256(common-php/emalloc_shim.h): True
measurement  c/emalloc_shim.h = aa9abf48535e8df9   == sha256(common-php/emalloc_shim.h): True

the committed gate record's c/ keys:
  ['patterns/ph00-smoke/c/emalloc_shim.h', '.../kernel.c', '.../kernel.h', '.../main.c']
measurement: identical set
```

## 1.4 ⚠⚠ M2 (major) — the composition §1.4 asks for, constructed and run

`c_digest_audit` is scoped to `<row>/c/`. **`#include "..."` is resolved
relative to the directory of the INCLUDING FILE**, so `c/kernel.c` reaches
`<row>/aux/` with `"../aux/x.h"` — and that file is in **no** gate digest
(`check.py:10313-10324`), **no** measurement digest
(`measure.py:224-235`), and **not walked** by `_walk_files(cdir)`.

`.temp/php9/04-upward-include.log`, built with `build.py`'s own flags and run:

```
=== (1) does the PREFLIGHT pass? ===
  shim_link_audit problems : 0   ['ph98-upward: c/emalloc_shim.h OK -- symlink, in BOTH digests']
  c_digest_audit  problems : 0
  -> PREFLIGHT WOULD PASS: True

=== (2) does it COMPILE, and does the row's own allocator run? ===
  gcc rc=0
  ./bin -> tally=1     (non-zero tally = the row's allocator was the one that ran)

=== (3) is aux/row_alloc.h in EITHER digest? ===
  gate digest keys        : ['c/emalloc_shim.h', 'c/kernel.c', 'c/kernel.h', 'c/main.c']
  measurement digest keys : ['c/emalloc_shim.h', 'c/kernel.c', 'c/kernel.h', 'c/main.c']
  'aux/row_alloc.h' in gate digest        : False
  'aux/row_alloc.h' in measurement digest : False
  c/emalloc_shim.h pinned as              : aa9abf48535e8df9   == the canonical shim: True

=== (4) EDIT THE ROW'S ALLOCATOR. Does any recorded hash move? ===
  gate digest keys that MOVED        : []
  measurement digest keys that MOVED : []
  ./bin after the edit -> tally=1000   (the BEHAVIOUR changed)
  preflight problems after the edit  : 0

⚠⚠ COMPOSITION LANDS

=== (5) MUST FIRE -- the same header one directory over, under c/ ===
  c/sub/row_alloc.h -> c_digest_audit problems: 1
    | digest: ph98-upward: c/sub/row_alloc.h is COMPILED and in NO DIGEST.
```

**So: a row whose preflight passes, whose records read FRESH for ever, and
whose effective allocator differs from `common-php/emalloc_shim.h` and can be
changed silently.** That is §1.4's question answered `yes`.

⚠⚠ **And this is not an exotic layout — `PROTOCOL_PHP.md` §B3 makes it MORE
likely, not less.** §B3 teaches the author that the danger is *"any source in a
`c/` **subdirectory**"*. The true statement is *"any source not matched by
`glob(<row>/c/*)`"*, and the natural php layout — extracted tarball sources at
`<row>/extract/Zend/…`, mirroring their origin, which is the layout that makes
provenance obvious — is one character away from the sanctioned
`c/zend -> ../../extract/Zend` and gets the opposite guarantee with no warning.

✅ **The `c/`-internal half is genuinely sound**: `ph98-upward`'s own must-fire
(5) shows the identical header one directory *down* is refused. **The audit is
not broken; its SCOPE is one directory too small.**

✅ **No PAT row is exposed.** `grep -rn '#include *"\.\./' patterns/*/c/` →
nothing; no `patterns/pNN/` has a directory other than `c/`, `inputs/`,
`controls/`, `__pycache__`. The defect is latent on both sides and live on
neither.

**Fix (not applied):** the finite-observable-set move one level up — refuse any
directory under `<row>/` other than `c/`, `inputs/` and `controls/`, which is a
`os.listdir` question with a bounded answer. ⚠ **Do NOT reach for `gcc -MD`
here**: it would be right in principle (the PAT gate already trusts the
compiler's own dependency output for the Rust rungs, `check.py:4471`
`--emit=dep-info`) but it needs a `build.py` edit, i.e. a 33-pattern
re-measure — and a *simulation* of it is the detector that was just deleted.

---

# §2 The deadlock repair

## 2.1 ✅ Clean negative — `g4_selfdeadlock.py` reproduces, both arms

Re-run **unmodified** (`md5 dafd0ff60c094c500c349e4358fe96fc`),
`.temp/php9/05-selfdeadlock-rerun.log`:

```
--- (a) MUST FIRE -- the naive rule ('a run that FAILED never certifies')
    run 1..6: coverage problems BEFORE the write = 1   verdict = 'PREFLIGHT FAILED'
    -> STILL FAILING after 6 runs. ⚠⚠ DEADLOCK.
--- (b) MUST NOT FIRE -- the rule actually shipped
    run 2: coverage problems BEFORE the write = 0   verdict = 'preflight only'
    -> CONVERGED after 2 run(s). NO DEADLOCK.
  naive rule deadlocks : True   CONTROL FIRED
  shipped rule converges: True
  real results-php/preflight/ byte-identical: True
```

## 2.2 ✅ Clean negative — the discount CANNOT be widened by any existing stage

I did not take the engineer's *"both message producers build from
`_COVERAGE_TAG`"* on trust. AST over every `problems.append` / `problems.extend`
in `gate.py`, printing each call's **literal first element**
(`.temp/php9/06-coverage.log`):

```
      Name                                 "Name(id='alloc_bad')"   (c_digest/shim/overlap/manifest/coverage sub-audits)
      concat                               'digest bridge:\n'
      concat                               'provenance:\n'
      f-string                             'allocator: '
      f-string                             'shim: '
      f-string starting with a VARIABLE    '_COVERAGE_TAG'
    problem messages that START with author-controlled text: ['_COVERAGE_TAG']

    `_COVERAGE_TAG` occurrences in gate.py source: 6
    literal 'preflight coverage:' NOT via the constant: 1
      gate.py:1206: print("preflight coverage: "        <-- a print, not a problem
```

**Every author-controlled string in a problem message sits behind a literal
stage prefix.** The two stages that embed subprocess output (`digest bridge:`,
`provenance:`) put the literal first, so a `provenance` failure whose text
*contains* the tag is not discounted — run, not read:

```
    PASS  certifying=True  (want True)  coverage-only failure
    PASS  certifying=False (want False) substantive + coverage
    PASS  certifying=False (want False) provenance problem that MENTIONS the tag mid-string
    PASS  certifying=True  (want True)  ⚠ a problem CRAFTED to start with the tag
    PASS  certifying=True  (want True)  clean run
```

⚠ The fourth case is the engineer's own disclosed residual (`TASK_PHP_008`
§11): a *crafted* prefix is discounted. **It is not reachable from any current
stage, and I could not make it reachable.** Named, not a finding.

## 2.3 ⚠⚠ M3 (major) — there IS a second deadlock, and the message printed at that moment denies it

`preflight_coverage_audit` is a **GLOBAL** stage: `gate.py:809-810` iterates
*every* `results-php/*.json` and `results-php/gate/*.json`, so **one** record
that cannot be certified fails **every** `gate.py` invocation. §8b's repair
makes a coverage-only failure certifying, which is what makes the fresh-clone
loop converge. ⚠ **It does not help when a record can never obtain a certifying
run at all**, and the cheapest such record is one **whose row no longer
exists**: the prescribed repair `gate.py --preflight <row>` fails on
**provenance**, which is a **substantive** problem.

Run end to end against the real tree, `.temp/php9/07-orphan-deadlock.log`:

```
=== (1) PLANT an orphan record ===
    gate.py --preflight ph00  ->  rc=2
      | preflight coverage: 1 php record(s) have NO preflight record: ['results-php/ph99-ghost.json']...
      | ⚠ THERE IS NO DEADLOCK: `main()` writes the record on the FAILURE path...

=== (2) FOLLOW THE PRESCRIBED REPAIR, verbatim ===
    gate.py --preflight ph99  ->  rc=2
      | FAIL provenance ph99
      | | provenance.py: 'ph99' matches nothing
    a record WAS written for ph99: True
      run[0] certifying=False   1 recorded problem(s), first: provenance:

=== (3) THE LOOP: repeat the repair. Does it converge? ===
    cycle 1: repair rc=2   ph00 preflight rc=2   coverage problems still reported=2
    cycle 2: identical
    cycle 3: identical
    -> ⚠⚠ DOES NOT CONVERGE.

=== (4) is the mandated BRACKET blocked too? ===
    gate.py --tool measure --check-stale  ->  rc=2

=== (5) THE ACTUAL FIX, which the message never names: delete the orphan record ===
    after `rm results-php/ph99-ghost.json`: rc=0   preflight OK (nothing else run)
```

**Three things make this a major and not a note.**

1. ⚠⚠ **The failure message asserts its own absence.** `gate.py:853-856`
   prints *"⚠ THERE IS NO DEADLOCK"* while the operator is standing in one.
   That is the shape `TASK_PHP_008` §5.2 deleted the *"dead code … Not treated
   as a shim user"* note for: **a reassurance that tells the reader not to look
   further.**
2. **The prescribed repair is the wrong command** and running it is
   indistinguishable from progress — it writes a record, exits 2, and the next
   run says the same thing.
3. **It blocks the mandated bracket**, so an agent whose first command is
   `--tool measure --check-stale` sees rc=2 and a wall of coverage text before
   it has done anything.

✅ **It is escapable** (delete the record), which is why it is not a blocker,
and the state is not reachable from a fresh clone. **It is reachable from
mining**: `PLAN_PHP.md` §3 expects rows to be refused and retired, and removing
a row directory while its committed records survive is the whole of it.

**Fix (not applied):** name the second repair in the message — *"or, if the row
was retired, delete `results-php/<row>.json` and `results-php/gate/<row>.json`
in the same commit"* — and **delete the "THERE IS NO DEADLOCK" sentence**,
which is now false about the case it is printed on.

## 2.4 ⚠ M4 (major) — §8b's convergence does not hold for a php row on a box with no tarball

Same shape, different stage. `.temp/php9/08-notarball-cap.log`:

```
=== (a) a php-provenance row on a box with NO TARBALL ===
    check_row(use_tarball=True)  ok=False
      | ph70-fixture: tarball not found at /nonexistent/php-5.0.0.tar.gz...
    -> recorded run certifying: (False, '1 recorded problem(s), first: provenance:')
    the `--no-provenance` escape, certifying: (False, 'provenance_skipped=true')
        (gate.py:751-752 rejects it BY CONSTRUCTION)
    `--no-tarball` (a provenance.py flag): ok=True
      gate.py's preflight spelling: False   <- the preflight has NO WAY to ask for it
```

**So on a box lacking `PHP500_TARBALL`, a `php_provenance: true` row can never
obtain a certifying run**, and the global coverage stage then blocks everything.
`--no-provenance` is explicitly non-certifying and `--no-tarball` is not
reachable from `gate.py` at all.

⚠ **Scope it honestly, because the common case is fine.** `_run_is_certifying`
reads **stored** runs, and `results-php/preflight/` is committed — so a fresh
clone inherits the certifying runs from the box that built the row and passes.
**The failure needs the record to be lost or regenerated**, which is *precisely
the fresh-clone scenario §8b was repaired for*: `TASK_PHP_008` proved
convergence on a fixture with **no provenance stage**, so the proof does not
carry to a php row. ⚠ **`ph00-smoke` is immune only because it declares
`php_provenance: false`. The first real row removes that immunity**, and the
first real row is the next thing this programme builds.

**Fix (not applied):** either forward `--no-tarball` from `gate.py` to
`provenance.py` and let a tarball-less run certify with a loud, recorded
`tarball_skipped: true` (the `--no-provenance` precedent, one notch weaker), or
make the coverage stage report `PER-ROW` rather than globally so an
uncertifiable *other* row does not block the row in hand. **I prefer the
second** — it removes the global-blocking property that both M3 and M4 depend
on, and it is the property that made §8b's deadlock permanent.

---

# §3 The subdir audit, the overlap demotion, M3

## 3.1 ✅ Clean negative — `c_digest_audit`'s file enumeration IS exhaustive

Every class the task names, plus the two must-NOT-fires.
`.temp/php9/11-digest-audit.log`:

```
=== MUST NOT FIRE ===
  PASS  ph10-clean       fires=False  digest keys=['emalloc_shim.h', 'kernel.c']
  PASS  ph11-flatlink    fires=False  digest keys=[..., 'zend__hash.h']

=== MUST FIRE ===
  PASS  ph12-dotfile     fires=True   | c/.payload.h is COMPILED and in NO DIGEST.
  PASS  ph13-dirlink     fires=True   | c/ext/outside.h is COMPILED and in NO DIGEST.
  PASS  ph14-nested2     fires=True   | c/a/b/deep.h is COMPILED and in NO DIGEST.
  PASS  ph15-linkout     fires=False  digest keys=[..., 'sub_outside.h']   <-- a FLAT link
                                       whose target is OUTSIDE the row IS keyed: correct
  PASS  ph16-dotdir      fires=True   | c/.hidden/x.h is COMPILED and in NO DIGEST.

  ph17-brokenlink  fires=True   -- isfile(dangling)=False so NOT keyed; _walk_files yields it -> REFUSED
  ph18-fifo        fires=True   -- isfile(FIFO)=False so NOT keyed -> REFUSED
  ph19-cycle       walker terminated, 0 problem(s)

ALL AS EXPECTED
```

⚠ **The FIFO case deserves one sentence the engineer did not write:
`sha256_file` on a FIFO BLOCKS FOR EVER, so a FIFO that *were* keyed would hang
the gate with no timeout.** It is not keyed and it *is* refused, so the tree is
safe — but that is the `os.path.isfile` filter doing it by accident, not by
design, and it is worth a comment beside the filter.

## 3.2 The overlap demotion — the citation half is exact, and it is about a different object

**`extract_sha256` and `c_file` are exact and cannot be satisfied by a wrong
citation**: the span must be in the manifest, in range, `extract_cmd` must be
the canonical spelling of `c_file`/`c_lines`, and the sha256 is over the exact
bytes of the pinned tarball (`provenance.py:703-761`). `excerpt()` refuses an
out-of-range span rather than hashing `b""` (TASK_PHP_003 M5's repair, still
in place). ✅ Self-test green, 9 cases, 0 FAILED (`12-provenance.log`).

⚠ **They are silent about the kernel, and after the demotion nothing else looks
at it.** `.temp/php8/g5_real_row_path.py` re-run unmodified
(`13-g5-rerun.log`):

```
(a) a plausible `verbatim` lift    check_row ok = True   overlap 89% (17/19)
(b) DIVIDES, cites multiplication  check_row ok = True   overlap  5% (1/19)
(c) the same behind `#elif 0`      check_row ok = True   overlap  5% (1/19)
3/3 as expected
```

**The engineer's §5.3 accounting of this cost is accurate and I have nothing to
add to it** — including the part that does not comfort them (*"currently free
expires at the first `verbatim` row"*). `PROTOCOL_PHP.md` §F item 9 exists and
says the right thing. ✅ And the `#elif 0` repair holds under its own control,
re-run unmodified (`18-misc.log`): must-fire on the `TASK_PHP_006` code
(100 % → 11 %), must-NOT-fire on the lazy repair (E2 stays 100 %), **exactly one
case moved**.

## 3.3 ⚠ m2 (minor) — `MAX_RUNS` is not a bound for the runs that actually accumulate

`_carries_evidence` (`gate.py:1010-1018`) is true for any run with a non-empty
`problems`, and `_collapse_and_cap` (`gate.py:1039-1046`) unions every such
index into `keep_idx` **before** the cap loop, so the cap can never drop one.
`.temp/php9/08-notarball-cap.log`:

```
    ordinary distinct runs (no problems)                 n= 1000 -> kept    40  dropped 960
    ⚠ runs that CARRY EVIDENCE (non-empty `problems`)    n= 1000 -> kept  1000  dropped 0
    ⚠ coverage-only failures (what M3's state produces)  n= 1000 -> kept  1000  dropped 0

    a MINIMAL failing entry is 100 bytes; a REAL one ~1400
      -> 1000 failing runs ~= 1367 kB in a COMMITTED file

=== MUST NOT FIRE -- the case the engineer measured ===
    120 genuinely distinct, no-problem runs -> kept 40, dropped 80
    the provenance_skipped entry survived: True
```

⚠ **The engineer's 120-run cap test used only NO-PROBLEM runs, which is the one
class the cap bounds.** The class that actually accumulates in practice — a
development session where every run fails and `harness_php_sha256` moves per
edit — is exempt. **This is a genuine answer to §3's question and it is a
minor**, because content-collapse still holds identical failing runs to one
entry (`ph00.preflight.json` today: **11 runs, 18.8 kB, 0 dropped**,
`18-misc.log`), so the realistic ceiling is tens, not thousands. **The manager
should know that `MAX_RUNS = 40` bounds the case that does not happen.**

---

# §4 Phase 0's closing claims

## 4.1 ✅ No-touch, by bytes, four baselines — §0 of this report

## 4.2 ⚠ m3 (minor) — the `0 STALE` sentence is right and incomplete

`harness/measure.py:270-278` iterates the **recorded** keys, so the engineer's
sentence — *"`0 STALE` means everything pinned still matches, not everything is
pinned"* — is **correct**. ⚠ **`measure.py:338-348` also shows `bad` is
incremented only by `stale or bstale`, so a pinned source that has been
DELETED does not fail either.** Run (`14-survival.log`, §B):

```
    moved patterns-php/ph00-smoke/c/emalloc_shim.h aside (a pinned key in BOTH records)
      FRESH       results/gate/ph00-smoke.json      29 source(s)
      MISSING     results/gate/ph00-smoke.json      patterns/ph00-smoke/c/emalloc_shim.h
      FRESH       results/ph00-smoke.json           19 source(s) + 8 input(s)
      MISSING     results/ph00-smoke.json           patterns/ph00-smoke/c/emalloc_shim.h
      2 record(s) examined, 0 STALE
      exit code = 0
      the PREFLIGHT does catch it: 1 problem(s)
```

⚠ **Note the record prints `FRESH` *and* `MISSING`**, and the summary line the
bracket quotes says `0 STALE`. **`PROTOCOL_PHP.md:449` should read *"…still
matches **or has been deleted**"*.** It is a `harness/` property, it affects all
33 PAT rows identically, and — agreeing with the engineer — it should be
**known, not fixed**: the fix is a `harness/` edit and a 33-pattern re-gate.

## 4.3 ✅ The gate chain — the record diff reproduces leaf for leaf

Independently, from `git show` (`.temp/php9/10-record-diff.log`):

```
results-php/gate/ph00-smoke.json   d493707^ -> d493707
    1079 leaf values before, 1097 after ;  moved 14   added 18   removed 0
    /verdict: PASS-WITH-BLOC -> PASS-WITH-BLOC
    source_sha256 movers: common/digest_bridge.py 298bac49->aaa5931d
                          patterns/ph00-smoke/spec.md a365d5d5->97e3259a
    source_sha256 ADDS:   patterns/ph00-smoke/c/emalloc_shim.h None -> aa9abf48

results-php/ph00-smoke.json
    1199 leaf values before, 1197 after ;  moved 87   added 2   removed 4
    source_sha256 movers: (none)
    source_sha256 ADDS:   patterns/ph00-smoke/c/emalloc_shim.h None -> aa9abf48
```

**Every count matches `TASK_PHP_008` §8.2 and §5.1 exactly.** ⚠ **My classifier
flagged three leaves as deterministic and all three are its own substring false
positives, which I am naming rather than reporting**: `/git/dirty_files` matched
on *"d-**ir**-ty"*, and `/marginal_ir_env/{bytes,envp_stack_bytes}` matched on
*"bytes"* — `check.py:3271-3351` documents that block as the **environment block
handed to the measured children**, which legitimately varies with the shell.
✅ **Zero `Ir`, checksum, md5, identity or input-hash movement. The engineer's
claim stands under an independent diff.**

## 4.4 ✅ The one claim `TASK_PHP_008` reasoned rather than ran — now RUN

§9.10 / §11: *"I did not verify that a shim edit stales the measurement
record."* One command. `.temp/php9/09-shim-edit.log`:

```
=== BEFORE ===  2 record(s) examined, 0 STALE   rc=0
=== PLANT: append one comment line to the shim ===
    shim sha256 aa9abf48535e8df9 -> b6fceb2ad8b9813a
    the row's symlink now hashes b6fceb2ad8b9813a   follows the target: True
=== AFTER ===
      STALE       results/gate/ph00-smoke.json    patterns/ph00-smoke/c/emalloc_shim.h
      STALE       results/ph00-smoke.json         patterns/ph00-smoke/c/emalloc_shim.h
      2 record(s) examined, 2 STALE    rc=1
RESTORED BY BYTES: True
```

✅✅ **The design's central claim is measured. The inference was correct.**

⚠ **One thing the engineer could not have predicted and the manager should
know: through `gate.py`, the DIGEST BRIDGE stage fires first** (`MOVED:
emalloc_shim.h`), the preflight refuses, and `--check-stale` never runs — so
the mandated bracket returns `PREFLIGHT FAILED`, not `2 STALE`. **That ordering
is correct** (a shim edit *should* stop everything until `--regen` is run) but
it means the staleness has to be read out of the shim directly, which is what
the log above does. Worth one line in §E beside the bracket.

---

# §5 The manager's §0 table — my verdict on each

| the manager decided | my verdict |
|---|---|
| **the unconditional link, and deleting the detector** | ✅ **Right, and I could not find a cheaper design either.** The construction is correct **given a complete row enumeration**, and the enumeration is incomplete in one bounded, fixable way (M1). ⚠ **It is a wrong enumeration, not an unboundable one** — §1.1. |
| **"a missing preflight record is a FAILURE"** | ⚠⚠ **Refuted a second time, from a second direction.** §8b caught the self-reference; **the GLOBAL scope of the stage is the part still standing, and it is what M3 and M4 both ride on.** The engineer repaired the cycle and left the blast radius. |
| lifting the subdir ban for the flat-link audit | ✅ **Right and well built.** 10/10 fixtures, including all six classes §3 names. The reviewer's objection at `TASK_PHP_006` (*"nothing forces the NEXT file"*) is genuinely answered. ⚠ Its **scope** is one directory too small (M2). |
| demoting the overlap floor to reported-only | ✅ **Right, for the structural reason, and the cost is priced honestly.** I re-ran the demoted path on a real tarball citation and reproduce 89/5/5 %. §F item 9 is the correct compensating control and it exists. |
| Phase 0 closes after this review absent a blocker | ⚠ **No blocker. See §8 for what I would attach to the close.** |

---

# §6 The three calls the manager was least sure of

## 6.1 ⚠⚠ *"Is the unconditional link correct BY CONSTRUCTION and not merely by a shorter enumeration?"*

**By construction, and the enumeration is currently wrong.** Those are two
different sentences and both are true.

- **The construction is right.** "The row's allocator" and "the programme's
  allocator" are the *same inode*, so there is nothing to keep in sync and
  nothing to detect. I tried and failed to find a fourth alternative past the
  engineer's three; the symlink is the only zero-machinery one.
- **The enumeration is wrong in one bounded way** (M1) and **the scope is wrong
  in one bounded way** (M2). ⚠ **Neither is whack-a-mole**, and the test for
  that is concrete: for both, there exists a single call that returns the
  complete set (`os.listdir` on rows; `os.listdir` on the row's directories),
  and `build.py` already uses one of them. **The detector had no such call.
  That is the whole difference and it is why I am not calling this a
  collapse.**

## 6.2 ⚠ *"Is closing Phase 0 here right?"* — see §8. Yes, with one named precondition.

## 6.3 ⚠ *"Did deleting the 'dead code' note lose anything?"*

**Agreed with the engineer, and the manager's residual worry is real but points
at the wrong artefact.**

- The note's failure mode was a **false negative wearing a reassurance**, and
  M3 shows the codebase still has one of those (*"⚠ THERE IS NO DEADLOCK"*),
  which is evidence that the *class* is the problem and not that one instance.
- ✅ **I verified the replacement is inert, by grep**: every occurrence of
  `uses_allocator` / `ALLOC_KEY` in `harness-php/` and `common-php/` is a
  comment, the constant, or a `msgs.append` (`.temp/php9/15-code-accounting.log`
  §c and the grep in `18-misc.log`). **`PLAN_PHP.md:554` lists it under
  ✗ not checked.** It has not acquired a consumer.
- ⚠ **What is genuinely gone is per-row evidence, and the cheap replacement is
  the one the engineer already named**: a row that declares
  `uses_allocator: true` should show the **tally from its own build** in
  `NOTES.md`. That is a per-row control with the row's real flags, it cannot be
  a "third detector" because it has no global claim to make, and it costs the
  author one paste. **I would add it to `PROTOCOL_PHP.md` §F item 6.** Two
  parties agreeing is not a measurement — so this is what I would measure
  instead.

---

# §7 Clean negatives — attacks that did NOT land

Re-running these is wasted time.

1. ✅ **The PAT tree is untouched, BY BYTES, against FOUR baselines**, control
   fired first, open and close (§0).
2. ✅ **The link survives git / clone / `cp -r` / `cp -a` / `tar`**, and every
   way of breaking it — dangling, regular-file copy, absent — is **refused with
   the correct message** (§1.2). ⚠ The task's `cp -r` premise was wrong in the
   design's favour and the truth is better.
3. ✅ **Both digests carry the shim's bytes**, verified from the committed
   records, `aa9abf48535e8df9` on both sides (§1.3).
4. ✅ **A shim EDIT stales BOTH records** — the one thing `TASK_PHP_008`
   inferred, now run (§4.4).
5. ✅ **`c_digest_audit` is exhaustive** on dotfile, dot-directory, symlinked
   directory, doubly-nested, out-of-row link, broken link, FIFO and cycle, with
   two must-NOT-fires (§3.1).
6. ✅ **The coverage discount cannot be widened by any existing stage** — AST
   over every problem producer, plus five behavioural cases (§2.2).
7. ✅ **`g4_selfdeadlock.py` reproduces both arms**, unmodified (§2.1).
8. ✅ **`g1_elif_control.py` reproduces**: must-fire, must-not-fire, exactly one
   case moved (§3.2).
9. ✅ **The record diffs reproduce leaf for leaf** under an independent
   differ, with **zero deterministic movement**; my classifier's three hits are
   named substring false positives (§4.3).
10. ✅ **The detector is gone from CODE, not just from `grep`.** AST with
    docstrings stripped (`15-code-accounting.log`): `_tu_closure`,
    `_MM_CONFIGS`, `_INCLUDE_RX`, `_text_mentions`, `ALLOC_FILES`,
    `SHIM_IMPL_TU`, `texty`, `"Not treated as a shim user"` — **0 occurrences in
    code, every one**; and `shim_link_audit`, `c_digest_audit`, `_walk_files`,
    `_run_is_certifying`, `_collapse_and_cap` call **no** subprocess, regex or
    compiler.
11. ✅ **`preflight()` has exactly EIGHT problem-adding sites** (AST), matching
    the docstring's *"NINE things, EIGHT of which can FAIL"*. Recounted, not
    trusted.
12. ✅ **`uses_allocator` has no consumer** (§6.3).
13. ✅ **`why_band` reproduces the published band from the live PAT corpus** —
    `PAT corpus n=33: median 989, p90 1817, max 3140`, printed by the real
    preflight in the opening bracket. The `floor` pin holds.
14. ✅ **A row created WHILE the audit runs is not a hole.** `glob` is a
    snapshot, the gate re-runs the preflight on every invocation, and the next
    one sees it. Run (`03-row-enum.log` §8).
15. ✅ **A row with no `c/` directory is skipped by both audits, and that is
    benign** — `build.py:163-165` compiles exactly `common/driver.c`,
    `<row>/c/<kernel>` and `<row>/c/main.c`, so a row without `c/` builds no C
    at all. The skip cannot hide an allocator.
16. ✅ **A row whose `c/` is a symlinked directory, and a row directory that is
    itself a symlink, are both iterated and both refused** — `os.path.isdir`
    follows links (`03-row-enum.log` §4, §5). Only the *dotted* name escapes.
17. ✅ **No PAT row is exposed to M2**: no upward relative include anywhere in
    `patterns/*/c/`, no sibling directory but `__pycache__`.
18. ✅ **`extract_sha256` / `c_file` are exact** and an out-of-range span is
    refused rather than hashed as `b""` (§3.2).
19. ✅ **`results-php/preflight/` was byte-identical before and after every
    in-process probe**, and all four plants restored exactly (§0).
20. ✅ **Running the mandated bracket on a clean tree changes NOTHING** —
    `git status --porcelain` was empty after the opening bracket, because
    content-collapse held the run to an existing entry. That is `TASK_PHP_008`
    M3 working in production, not on a fixture.

---

# §8 ⚠⚠ Should Phase 0 close? — the answer, plainly

**Yes. Close it. And attach ONE precondition rather than a queue entry.**

**Why close.** Eight tasks and zero rows is a real cost, and the thing that
would justify a ninth infrastructure task is *"the enforcement layer is
unsound in a way we do not know how to bound"*. That was true of B1 twice. **It
is not true now**, and I tried hard to make it true: the two structural findings
(M1, M2) each have a **single complete enumeration** available, one of which the
codebase already calls. Everything else I found is operational — two deadlocks
that block work loudly and destroy nothing, and three hygiene items. **No number
this programme could publish today is wrong**, and the PAT tree is provably
untouched across four baselines.

**Why a precondition and not an open item.** M1 and M2 both live in the layer
the **first real row** will lean on, both are minutes of work, and ⚠ **M2 is
made more likely by the documentation as written** — §B3 teaches the author
that the danger is subdirectories *of `c/`*, and the natural php layout
(extracted sources in a sibling directory, mirroring the tarball) is the one
that escapes. An open item in a queue is read after the row is built; this
needs to be true before it. **Concretely, the precondition I would set:**

1. **M1** — `os.listdir` in place of `glob("*")` in `shim_link_audit`,
   `c_digest_audit`, `why_sizes` and `preflight_coverage_audit`, plus one
   must-fire fixture (`.temp/php9/a1_row_enum.py` case 3 already is one).
2. **M2** — refuse any directory under `<row>/` outside `{c, inputs, controls}`,
   plus `.temp/php9/a2_upward_include.py` as the must-fire and its case (5) as
   the must-NOT-fire. ⚠ **Do not reach for `gcc -MD`.**
3. **§B3's soundness sentence** — it currently says the audit's input is
   `os.listdir`. Make that true (1) and make its scope claim match its scope
   (2), or the document over-states the guarantee in exactly the two places I
   could break it.

**M3 and M4 I would carry as open items**, not preconditions: both are loud,
both are escapable, neither can corrupt a record. ⚠ **But if the manager wants
one cheap change that closes both, it is making the coverage stage report
per-row instead of globally** — the global scope is what turns any single
uncertifiable record into a programme-wide stop, and it is the property §8b's
deadlock also depended on.

**What would have made me say "do not close":** a finding that the *link
itself* can be satisfied while the allocator differs **within the layout the
protocol prescribes**. I built the strongest version of that I could (§1.4) and
it needed a directory the protocol does not sanction. **That is a scope bug in
an audit, not a hole in the design.**

---

# §9 What I refute or correct

**Launched from 23. Reconciliation is the manager's, not mine.**

### Against the MANAGER (2)

1. ⚠⚠ **§6 call 1's "the whole argument collapses" is too strong, and the
   correction matters more than the bug it is about.** A row *can* hide from
   `glob` (M1) — and this is **not** a return to whack-a-mole, because a
   **complete** row enumeration exists in one call and `build.py:81-89` already
   uses it. **The idiom detector's defining property was that no complete
   enumeration existed.** Treating a wrong enumeration and an unboundable one as
   the same failure is how a fixable bug gets priced as a phase.
2. ⚠ **§1.2's `cp -r` premise is wrong, in the design's favour.** *"A row
   cloned with `cp -r` gets a copy, not a link"* — GNU `cp -r` **preserves** the
   symlink; the copy dangles because the *relative* target does not resolve at
   the new depth, and `shim_link_audit`'s `realpath` arm catches it
   (`14-survival.log` A4). The regular-file case is real and is refused by name.

### Against the ENGINEER (2)

3. ⚠⚠ **`TASK_PHP_008` §8b repaired the cycle and left the blast radius.** The
   coverage stage is **global**, and that property — not the naive certifying
   rule — is what M3 and M4 both ride on. §8b's own convergence proof was run on
   a fixture with **no provenance stage**, so it does not carry to a php row
   (M4). ⚠ **The lesson the report itself draws — *"two checks that are each
   correct can deadlock when composed"* — is right, and there is a third check
   in the composition it did not enumerate.**
4. ⚠ **`MAX_RUNS`'s test measured the class the cap bounds.** 120 *no-problem*
   runs cap at 40; **1000 evidence-carrying runs keep all 1000**. The engineer
   wrote *"the number only matters on a tree that genuinely differs between
   runs, which is a state I did not model beyond the synthetic 120"* — the state
   that actually occurs is the one that is exempt.

### Upheld against my own attempts to break them (5)

5. ✅ **The unconditional link is correct by construction**, and I could not
   construct a fourth cheaper design past the engineer's three.
6. ✅ **`TASK_PHP_008` §9.10's one inference is TRUE**, now measured (§4.4).
7. ✅ **The `_COVERAGE_TAG` discount cannot drift**, verified by AST rather than
   by the engineer's assertion (§2.2).
8. ✅ **The record-diff accounting reproduces exactly** under an independent
   differ (§4.3).
9. ✅ **`c_digest_audit` is exhaustive on every class §3 names** (§3.1).

### A near-miss in my own work, disclosed (1)

10. ⚠ **My own record differ over-matched three leaves as "deterministic"**
    (`dirty_files` on *"ir"*, `marginal_ir_env.*bytes*` on *"bytes"*) and I
    nearly reported *"3 deterministic leaves moved"* against a report that says
    zero. **I chased all three to their definitions before writing** — §4.3.
    The engineer's number is right and mine was the artefact.

---

# §10 What I did NOT do, and what I am unsure about

- **I did not fix anything.** Four plants, four byte-verified restores, final
  `git status --porcelain` empty (§0).
- **I did not edit `RECAP_PHP.md`, `.memory/`, `harness/`, `common/`,
  `patterns/`, `results/` or `pilot/`.** Proved by bytes against four
  snapshots with the control fired.
- ⚠ **M1 is proved end to end for the PREFLIGHT half and by component for the
  MEASURE half.** I ran the real `gate.py --preflight .ph93` and it returned
  rc=0; I did **not** run a full `--tool measure` on a dotted row, because that
  is ~8 minutes plus a ~24-minute gate and would leave a dotted directory in a
  committed tree for the duration. **The measure half rests on three component
  runs** — `build.pattern_dir('.ph93') -> .ph93-dotted`, the record name
  `f"{pid}-{slug.split('-',1)[1]}.json"` at `measure.py:576`, and the two
  record globs shown blind in `16-dotted-chain.log`. **A reviewer should know
  those are three inferences chained, not one run.**
- ⚠ **M2 is proved with `build.py`'s flags reproduced by hand, not by calling
  `build.py`.** I used `-std=c99 -Wall -Wextra -O3 -flto -I common-php -I
  <row>/c`, which is `c_flags("O3","whole")` plus `build_c`'s `-I` pair; I did
  not exercise the other seven cell configurations. The escape is a
  preprocessor property and does not depend on flags, but I did not measure
  that.
- **I did not attack the R1h / tier / deletion-ledger machinery**, the manifest
  generator, or `PLAN_PHP.md` §2.1's shim argument. `TASK_PHP_002`–`007`
  covered them and my task did not name them.
- **I did not re-run `.temp/php7/`'s generators** beyond what §2/§3 needed;
  `TASK_PHP_008` re-ran `a1`, `a5`, `b3` and the rest measure deleted code.
- ⚠ **`.temp/php0/pycdemo` still dangles** from `harness-php/gate.py:180`,
  `harness-php/root.py:113` and `.tasks-php/TASK_PHP_002_REPORT.md:290` — the
  engineer disclosed it and correctly did not fix it (m4). ✅ **It is the only
  one**: a sweep of every `.temp/` path cited by `harness-php/*.py`,
  `common-php/*.py`, `PROTOCOL_PHP.md` and `PLAN_PHP.md` found three other
  "missing" hits and **all three are false alarms** — suffixes of the absolute
  `PHP500_TARBALL` path, which contains `.app-tests/.temp/oracle/…`.
- ⚠ **I did not decide whether M3's orphan-record state is reachable from
  `git` operations**, only from a row deletion. A `git checkout` that moves rows
  and records together does not produce it; I did not enumerate every history
  shape that could.
- **`_RUN_SLOT`'s interaction with content-collapse** — I read it and convinced
  myself the `slot is None` path is correct (it appends rather than overwriting
  a stranger's entry), but I did not construct a case for it. Named as
  unattacked.

---

# §11 Minors, in full

- **m1 — `preflight_coverage_audit`'s row match is a PREFIX glob.**
  `harness-php/gate.py:816-817` globs `f"{rid}*.preflight.json"` where
  `rid = stem.split("-")[0]`. Run (`06-coverage.log` §5): a record
  `results-php/ph10-victim.json` with **no** preflight record of its own reports
  **covered**, because `ph10*` matches `ph100.preflight.json`. Needs an
  inconsistent id length (`ph10` vs `ph100`), which the two-digit convention
  makes unlikely — but the audit's whole job is to answer this one question and
  it can answer it wrongly. **Fix: exact-match `f"{rid}.preflight.json"` plus
  the full-slug spelling.**
- **m2 — `MAX_RUNS` is not a bound for evidence-carrying runs** (§3.3).
- **m3 — `0 STALE` also does not mean "every pinned source still exists"**
  (§4.2). `PROTOCOL_PHP.md:449`.
- **m4 — `.temp/php0/pycdemo` still dangles** in three places (§10).
- **m5 — a preflight FAILURE permanently grows a COMMITTED file.** Measured on
  my own plant: one failing `gate.py --tool measure --check-stale` added **52
  lines** to `results-php/preflight/_norow.preflight.json`, and
  `_carries_evidence` exempts it from the cap for ever. ⚠ **I caught it only
  because `a6_shim_edit.py` printed `git status` in its own `finally:`** —
  a probe that plants into `common-php/` also dirties `results-php/`, and that
  second-order effect is easy to miss. **Worth a line in `PROTOCOL_PHP.md` §E:
  a failing run is not read-only.**
- **m6 — `sha256_file` on a FIFO would block for ever** (§3.1). Not reachable
  today because `os.path.isfile` excludes FIFOs from the key set, but that is
  an accident of the filter rather than a stated property. One comment.

---

# §12 Durable facts worth lifting (manager's call — I cannot write `.memory/`)

| fact | evidence |
|---|---|
| ⚠⚠ **A WRONG enumeration and an UNBOUNDABLE one are different failures.** The test is whether a single call returns the complete set. `glob("*")` vs `os.listdir` is a substitution; *"every way to spell an `#include`"* is a game. **Do not price the first as the second.** | §1.1, §6.1 |
| ⚠⚠ **An audit's SCOPE is as load-bearing as its LOGIC.** `c_digest_audit` is exhaustive inside `<row>/c/` and blind one directory up, and the documentation that describes it makes the escape *more* likely by naming the subdirectory rather than the glob. | M2, `PROTOCOL_PHP.md` §B3 |
| ⚠⚠ **A GLOBAL stage turns any single uncertifiable record into a programme-wide stop.** Both deadlocks found here ride on that property, and so did §8b's. **Scope a stage to the row in hand unless it must be global.** | M3, M4 |
| ⚠⚠⚠ **A failure message that asserts its own absence is the reassurance class again.** *"⚠ THERE IS NO DEADLOCK"* is printed to an operator standing in one — the same shape as *"CANNOT BE"* and *"Not treated as a shim user"*, which this project has now paid for three times. | M3 |
| ⚠ **Test a cap on the class that ACCUMULATES, not the class it bounds.** 120 clean runs cap at 40; 1000 failing ones keep all 1000. | m2 |
| ⚠ **A convergence proof inherits the stages it was run against.** §8b converged on a fixture with no provenance stage; a real row has one. | M4 |
| ⚠ **A probe that plants into one committed directory can dirty another.** Print `git status` inside every `finally:`, not only the sha256 of what you meant to touch. | m5 |
