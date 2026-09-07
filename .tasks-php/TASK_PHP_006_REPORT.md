# TASK_PHP_006 — landing `TASK_PHP_005`'s corrections — ENGINEER REPORT

**Role:** research engineer. **Launched from a running count of 12.**
This task **refutes three figures** (§ *What I refute*) — two of them the
reviewer's, one the manager's — and **reconciliation is the manager's job.**

> **Bracket, first and last command, both pasted.** ⚠ The middle pair is not
> decoration: the php gate record was *supposed* to go stale, because this task
> edits the digest-pinned `common-php/emalloc_shim.h`.
>
> ```
> FIRST  python3 harness/measure.py --check-stale                   66 record(s) examined, 0 STALE
> FIRST  python3 harness-php/gate.py --tool measure --check-stale    2 record(s) examined, 0 STALE
>
> (after the shim edit + digest_bridge.py --regen, BEFORE the re-gate)
>        python3 harness-php/gate.py --tool measure --check-stale
>          STALE  results/gate/ph00-smoke.json    common/digest_bridge.py
>          FRESH  results/ph00-smoke.json         18 source(s) + 8 input(s)
>          2 record(s) examined, 1 STALE            <-- predicted, and the only mover
>        python3 harness/measure.py --check-stale                   66 record(s) examined, 0 STALE
>
> LAST   python3 harness/measure.py --check-stale                   SEE §7
> LAST   python3 harness-php/gate.py --tool measure --check-stale   SEE §7
> ```
>
> **No-touch disclosure.** Nothing under `harness/`, `common/`, `patterns/`,
> `results/` or `pilot/` was added, edited or deleted. `git status --porcelain`
> at the end lists only `.gitignore`, `.tasks-php/`, `common-php/`,
> `harness-php/` and the newly-committable `results-php/preflight/` — §7.
> ⚠ Two of my probes `import measure` out of the real `harness/`, which
> `root.py`'s docstring flags as the one thing that can write into that
> directory. **It did not:** every file in `harness/__pycache__/` is dated
> 09-02/09-03, so the existing cache was reused and nothing new was written.
> (It is gitignored and outside every glob either way.)
>
> **Planting disclosure.** Four plants, all restored in a `finally:` and all
> verified afterwards: a `common-php/layout` and a `common-php/census` directory
> symlink (F-9), a mis-aimed `results` link inside the gitignored
> `.temp/php-root/` shim (F-6), and the `results-php/preflight/` directory itself
> (overwritten while measuring F-2 and F-6, restored from
> `.temp/php6/pf-state-during-*`; the pre-task state is backed up at
> `.temp/php6/preflight-backup-before-006/`).
>
> **Scratch:** `.temp/php6/`. The reviewer's generators in `.temp/php5/` were
> **re-run, not replaced** — `b1_bypass.py`, `m5_overlap_attack.py`,
> `mul_probe_missing.sh` and `sweep_plant.sh` all ran again against the fixed
> code, unmodified. Nothing under `.temp/php5/` was deleted.

---

## Summary

| finding | what landed | evidence |
|---|---|---|
| **F-1** blocker | **CLOSED, by changing the question.** The allocator detector is no longer a string search: `gate.py::_tu_closure` asks `gcc -MM` for the real TU closure. All eight of the reviewer's fixture rows now land correctly, including the two bypasses. | `.temp/php6/04-b1-AFTER.log` |
| **§1.2** | `gate.py::c_subdir_audit` **refuses** any `patterns-php/*/c/<subdir>/`, with a message that prices three ways out — one of them **measured**. ⚠ I think the trade is right *today* and say why, and I say what would change it. | `.temp/php6/05-b1-rerun.log` |
| **§1.3** | Not closable without a `harness/` edit; **not attempted**. Instead: the record is committed, absence is detected, and `PROTOCOL_PHP.md` §E now has an enforced/not-enforced table. | `.temp/php6/10-coverage.log` |
| **F-2** major | All three parts landed: record **committed** minus `when`; **per-run append**, never overwrite; **absence detected** by `gate.py --audit` and by every preflight. | `.temp/php6/09-f2-record.log` |
| **F-3** major | `emalloc_shim.h` (digest-pinned) now states what was run, by whom, with which flags — and that `TASK_PHP_004`'s Problem 1 is a limitation that does not exist. The three missing cells **re-run here** and reproduced byte-for-byte. `emalloc_shim.c`'s "CANNOT BE" comment corrected. | `.temp/php6/11-mul-missing-RERUN.log` |
| **F-4** major | Normaliser fixed for `#if 0` **and for block comments, which F-4 did not name**; seven regression cases including **two must-NOT-fire**; run on every preflight. The "a pass is not evidence the cited lines are compiled" correction is now in three places the tool prints. | `.temp/php6/06-overlap-selftest.log`, `07-m5-overlap-AFTER.log` |
| **F-5** major | Measured; **recommendation is (c) NO RULE**, argued from the distribution, with a **reported-not-enforced** number in its place. ⚠ Both of the manager's alternatives are refuted by measurement, and so is F-5's own corpus table. | `.temp/php6/15,16,17,19-*.log` |
| F-6 | `check()` before `build()`; a repair is printed and recorded in `shim_repaired`. | `.temp/php6/20-f6-stage1.log` |
| F-7 | `--preflight` / `--no-provenance` / `--audit` are reclaimed from the tool remainder wherever they appear, with a note. | `.temp/php6/09-f2-record.log` §c |
| F-8 | Closed **as a side effect of F-1** — the preprocessor does not see comments. | `.temp/php6/04-b1-AFTER.log` |
| F-9 | `digest_bridge.py` special-cases `GLOBBED_SUBDIRS` against `GLOB_PATTERNS`; both message branches exercised. | `.temp/php6/12-bridge-layout.log` |
| F-10 | `--sweep` learns single quotes, string prefixes **and the f-string spelling**; the 5 underivable sites are now **reported** instead of silent. All four planted spellings found. | `.temp/php6/13-sweep-after.log`, `14-sweep-plant.log` |
| F-11 | **Wording proposed in §6; not landed** (manager's file). |  |
| F-12 | **Treatment proposed in §6, not applied to the task file**; the durable correction landed in the digest-pinned shim instead. | verified against the pristine tarball |

---

# §1 F-1 — the blocker. Closed by changing the question, not by adding a spelling.

## 1.0 The baseline, reproduced first

Before touching anything I re-ran the reviewer's own generator against the
**unfixed** code and got their result exactly (`.temp/php6/02-b1-BEFORE.log`):

```
  b0 ph50-direct   : (detected=True,  reaches=True,  in_gate=False, in_meas=False)
  b0b ph51-linked  : (detected=False, reaches=True,  in_gate=True,  in_meas=True)
  b1 ph52-indirect : (detected=True,  reaches=True,  in_gate=False, in_meas=False)
  b2 ph53-subdir   : (detected=False, reaches=True,  in_gate=False, in_meas=False)   <-- BYPASS
  b5 ph54-dotc     : (detected=False, reaches=True,  in_gate=False, in_meas=False)   <-- BYPASS
  b3 ph55-extern   : (detected=False, reaches=False, ...)
  fp ph56-mention  : (detected=True,  reaches=False, ...)                            <-- FALSE POSITIVE
  b4 ph57-rust     : (detected=False, reaches=False, ...)
```

## 1.1 The detector: I took the preprocessor, and here is the price

The task asked me to price `gcc -MM` and to say out loud if I rejected it.
**I did not reject it.** Measured, `.temp/php6/03-mm-price-batched.log`:

```
  ph00-smoke       2 call(s)   134.1 ms      ph54-dotc      2 call(s)  120.6 ms
  ph50-direct      2 call(s)   110.3 ms      ph55-extern    2 call(s)  102.7 ms
  ph51-linked      2 call(s)   119.9 ms      ph56-mention   2 call(s)  105.6 ms
  ph52-indirect    2 call(s)   113.0 ms      ph57-rust      2 call(s)  107.2 ms
  ph53-subdir      2 call(s)   119.7 ms
TOTAL 18 gcc -MM calls, 1033.0 ms  (nine rows)
```

**~115 ms and two `gcc` calls per row**, batched over every TU at once, against
a gate that takes ~24 minutes. Fifty rows would cost about **5.8 s per
preflight**. That is affordable, and the manager's suspicion that it might not
be does not survive the measurement.

**What it does.** `build.py::build_c`'s own TU list — `common/driver.c` plus
every `<row>/c/*.c` — preprocessed with `-I common-php -I <row>/c` under **both**
`-DSLB_ISOLATED` and without it, and the closure `realpath`ed and intersected
with `{common-php/emalloc_shim.h, common-php/emalloc_shim.c}`.

Three design points, each of which is a defect avoided:

- **Both `-D` states are swept and unioned.** `build.py::c_flags` passes
  `-DSLB_ISOLATED` in isolated mode and not in whole mode. A row that writes
  `#ifdef SLB_ISOLATED / #include "emalloc_shim.h" / #endif` is a shim user in
  half its cells, and a single-config `-MM` would miss it.
- **`driver.c` is in the sweep** even though it is frozen PAT code, because
  `build_c` compiles it with `-I <row>/c` and a row could shadow a driver header.
- **`realpath`, not basename.** In the sanctioned layout the closure names
  `<row>/c/emalloc_shim.h` (the symlink), because a quoted `#include` searches
  the includer's directory first. Comparing realpaths makes the linked and
  unlinked cases the same question.

## 1.2 The result: all eight rows, and the two bypasses are shut

`.temp/php6/04-b1-AFTER.log`, from the reviewer's **unmodified** generator:

```
--- ph50-direct     detected True  (expected True)   -> refused, ORIGINAL reason:
    allocator: ph50-direct: the TU(s) kernel.c REACH an emalloc_shim source
    (preprocessor) and ph50-direct/c/emalloc_shim.h IS ABSENT.
--- ph51-linked     detected False (expected False)  gate digest True, meas digest True
--- ph52-indirect   detected True  (expected True)   refused
--- ph53-subdir     detected True  (expected True)   refused   <-- WAS A BYPASS
--- ph54-dotc       detected True  (expected True)   refused   <-- WAS A BYPASS
       shim reaches the TU : True  ['.../emalloc_shim.c', '.../emalloc_shim.h']
--- ph55-extern     detected False                   passes
--- ph56-mention    detected False (expected False)  passes    <-- F-8 CLOSED
--- ph57-rust       detected False (expected False)  passes
```

Against the task's acceptance condition, item by item: **`ph53-subdir` refused
✅, `ph54-dotc` refused ✅, `ph51-linked` still passes and is in both digests ✅,
`ph55-extern` still passes ✅, `ph50-direct` still fails for the original reason
✅.** No clean negative broke.

⚠ **`ph55-extern`'s expectation in the reviewer's script is `True`, and it is
the script that is wrong, not the fix.** The reviewer's own clean negative 2
proves the case is structurally impossible — every shim entry point is
`static inline`, so `extern void *php_shim_emalloc(size_t)` gives
`undefined reference` and there is nothing to link. `shim reaches the TU:
False`. The task file agrees (*"`ph51-linked` and `ph55-extern` still pass"*).
I left the reviewer's script byte-identical rather than retuning its
expectation, so the log shows the mismatch honestly.

## 1.3 F-8, and why the answer is "the preprocessor", not "an `#include` guard"

The task offered two repairs and asked me to price the stronger one. The
`#include`-on-the-same-line guard would have closed F-8 and `ph54-dotc` but
**not `ph53-subdir`** (the glob is still non-recursive) and it would still have
had a spelling. The preprocessor closes **1, 2 and F-8 together and has no
spelling.**

⚠ **The text detector survives as a FALLBACK, for one case only: a row that
does not preprocess.** It is not a union — a union would resurrect F-8. When it
fires it says so, loudly, in the notes. Must-fire negative, `.temp/php6/05-b1-rerun.log` §B:

```
=== B. a row that does not preprocess ===
  _tu_closure errors: 2
      | gcc -MM (no -D) exited 1: .../ph62-broken/c/kernel.c:1:10: fatal error:
        no_such_header.h: No such file or directory
  refused anyway (fallback)   : True   OK
  says it fell back           : True
      | ph62-broken: ⚠ PREPROCESSOR COULD NOT DECIDE -- ... Falling back to the
        TEXT detector, which only sees the name inside an #include ...
      | allocator: ph62-broken: the TU(s) kernel.c REACH an emalloc_shim source
        (text fallback) and ph62-broken/c/emalloc_shim.h IS ABSENT.
```

**A failure to preprocess is never read as "no allocator"** — that was the
single most likely way to reintroduce the blocker.

There is one more thing the preprocessor knows and the string search did not:
if a row's text says `#include "emalloc_shim.h"` but no TU reaches it, that is
**dead or unreachable code** and the audit now says so as a note rather than
refusing. That is the F-4 shape, one directory over.

## 1.4 §1.2 — the `c/` subdirectory refusal, and whether I think it is right

Landed as `gate.py::c_subdir_audit`, a separate preflight stage.
Must-fire and must-not-fire, `.temp/php6/05-b1-rerun.log` §A:

```
  ph60-clean   (must NOT fire): 0 problem(s)   OK
  ph61-subdir  (MUST fire)    : 1 problem(s)   CONTROL FIRED
      | allocator/digest: ph61-subdir: c/sub/ IS A DIRECTORY, and no file under
        it is in ANY digest.
      |        2 file(s): ['sub/aux.h', 'sub/aux2.h']
      |        check.py:10314 and measure.py:226 glob `<row>/c/*` NON-RECURSIVELY
        and drop the directory with isfile(), so these files are compiled
        (build_c passes -I <row>/c) and pinned by nothing: no gate digest, no
        measurement digest, and not even check.py's --no-build staleness scan.
        Editing one would not mark a single binary stale.
```

The message names the cost, names open item 17, and prices **three** ways out:
flatten (`c/zend__zend_hash.h`, one deletion-ledger line); a flat symlink; or
pay the re-gate.

### ⚠ §5 call 1 — the manager asked to be told if this trade is wrong. My answer, with the measurement.

**Today it is right, and it is right for a reason narrower than "it is cheaper".
Tomorrow it may not be, and here is the escape hatch, measured, so nobody has
to rediscover it under pressure.**

I could not find a php row that *needs* the directory. Extracted PHP headers
have unique basenames across `Zend/` and `ext/standard/`, and `build_c` passes
`-I <row>/c`, so a flat `c/zend__zend_hash.h` compiles identically; the only
forced change is rewriting the row's own `#include`, which is a
deletion-ledger line, not a semantic change. **The layout is wanted, not
needed** — and that is the whole of why the trade holds.

⚠ **But the second option is real and I measured it rather than reasoning about
it** (`.temp/php6/05-b1-rerun.log` §C):

```
=== C. does a FLAT SYMLINK to c/<subdir>/x land in both digests? ===
  sha256(c/zend/zend_hash.h)      = 46d5e2757731
  gate digest keys                = ['c/kernel.c', 'c/kernel.h', 'c/main.c',
                                     'c/zend__zend_hash.h']
  flat link in GATE digest        : True
  flat link in MEASUREMENT digest : True
  the SUBDIR file itself keyed    : False   (expected -- the glob never sees it)
```

**A `c/zend/foo.h` with a `c/zend__foo.h -> zend/foo.h` beside it is in both
digests, with no harness edit at all.** So if a row does need the layout, the
answer is **not** the 33-pattern re-gate; it is eight symlinks and a check that
every file under the subdirectory has one. ⚠ **I did not enable it**, and the
reason is the one that decides it: nothing would force the *next* file added to
that subdirectory to get a link, so the guarantee would hold exactly as long as
somebody remembered it — which is the "mandatory in two documents and enforced
by nothing" failure this programme has already paid for once (`PROTOCOL_PHP.md`
§B2). If a row needs it, it comes with the check.

**What would change my answer:** a row that must keep an extracted file's
original `#include "Zend/x.h"` spelling verbatim to stay in the `verbatim` tier.
I do not think that case exists — `PROTOCOL_PHP.md` §A2 already treats include
plumbing as a deletion — but I have not built twenty rows and the manager should
not treat my answer as more than one engineer's search.

## 1.5 §1.3 — the preflight is skippable. I did not try to close it.

`grep -c preflight harness/{check,measure,report}.py` → `0 0 0`, and closing it
means teaching `check.py` about `harness-php/`. **Not attempted**, per the task.

What landed instead is the honest substitute, in three parts:

1. the record is **committed**, so a fresh clone has it (F-2);
2. **absence is detected** — `gate.py --audit` exits 1, and every preflight
   prints it (F-2 part 3, §2 below);
3. `PROTOCOL_PHP.md` §E now carries an explicit **enforced / recorded / detected
   / NOT enforced / NOT a pin** table, and `gate.py`'s own docstring says
   *"it cannot make itself mandatory"* in terms.

⚠ **The residual, stated plainly: a green php gate record means the tree passed
the PAT gate. The preflight record beside it is evidence the php-specific checks
also ran; its absence is evidence they did not.** That is weaker than a pin and
it is the strongest thing available from outside `harness/`.

---

# §2 F-2 — the preflight record. Three parts, all measured.

## (a) Committed, minus `when`

`.gitignore`'s `results-php/preflight/` line is gone; the wrong rationale with
it. What is ignored now is `results-php/preflight/*.when.json` — a sidecar
carrying the one field the reviewer measured as the only mover.

```
$ git check-ignore -v results-php/preflight/ph00.when.json results-php/preflight/ph00.preflight.json
.gitignore:36:results-php/preflight/*.when.json    results-php/preflight/ph00.when.json
(the .preflight.json is NOT matched -- it is committable)
```

**And the churn claim is now enforced rather than asserted**
(`.temp/php6/09-f2-record.log`):

```
=== (a) two identical `--preflight ph00` runs ===
  run 1: sha256 9836302c1ea270bc  runs=2
  run 2: sha256 9836302c1ea270bc  runs=2
  COMMITTED RECORD BYTE-IDENTICAL: True   OK
  the gitignored sidecar carries the timestamp:
    {'row': 'ph00', 'last_run_slot': 1, 'when': '2026-09-07T09:21:25'}
```

## (b) The per-row overwrite — fixed by appending, and the evidence survives

The file is now `{"row": …, "runs": [ … ]}`; a run is appended, and a run that
repeats the previous one collapses (which is what keeps (a) byte-identical).

```
=== (b) does a later run ERASE `provenance_skipped: true`? ===
  after --no-provenance:       runs=3  provenance_skipped at [2]
  after the NEXT ordinary run: runs=4  provenance_skipped at [2]
  EVIDENCE SURVIVED: True   OK
```

⚠ **The manager's own 06:55 record is preserved, not discarded.** A
pre-TASK_PHP_006 single-record file is migrated into `runs[0]` and tagged
`"_schema": "pre-TASK_PHP_006 single-record file, migrated"` — including its
`tool_returncode: 2`, which F-7 shows is a failed `check.py` launch recorded as
a preflight. Deleting it would have been the same erasure F-2a is about.

## (c) Absence is detectable — and it is a NOTE, not a failure, for a measured reason

`gate.py::preflight_coverage_audit` cross-checks every `results-php/*.json` and
`results-php/gate/*.json` against `results-php/preflight/<row>*.preflight.json`.

```
=== must-NOT-fire: records present ===
  --audit rc=0   OK        | preflight coverage: complete

=== must-FIRE: the row's preflight record is gone ===
  --audit rc=1   CONTROL FIRED
   | ⚠ 2 php record(s) have NO preflight record:
     ['results-php/ph00-smoke.json', 'results-php/gate/ph00-smoke.json'] ...

  and the preflight itself says so, without failing:
  --preflight rc=0   OK -- loud but runnable
```

⚠ **I deliberately did not make it a preflight failure, and the reason is a
deadlock I ran into while designing it:** if a missing record failed the
preflight, the repair (`gate.py --preflight <row>`) is itself a preflight and
would fail on every *other* uncovered row before writing anything. **Loud beats
unrunnable.** `--audit` is the same check with an exit code for anyone who wants
it as a gate — including a future CI-free local script.

---

# §3 F-3 — the fidelity claim, in the digest-pinned file

## What I re-ran rather than copied

The reviewer ran the three missing cells; I am about to write their result into
a file that is hashed into every php gate record, so I ran them again
(`.temp/php6/11-mul-missing-RERUN.log`) — **byte-identical to
`.temp/php5/09-mul-missing-cells.log`**:

```
### gcc-O0-lto        agree 20000000  DISAGREEMENTS 0   CONTROL 84523 FIRED
### clang-O0-lto      agree 20000000  DISAGREEMENTS 0   CONTROL 84523 FIRED
### clang-O3-lto-lld  agree 20000000  DISAGREEMENTS 0   CONTROL 84523 FIRED
```

And the refuted limitation, re-measured directly:

```
$ clang -O3 -flto ... (no -fuse-ld=lld)
/usr/bin/ld: .../llvm-22.1.6/bin/../lib/LLVMgold.so: error loading plugin: ...
clang: error: linker command failed with exit code 1
$ clang -O3 -flto -fuse-ld=lld ...
LINKED ok
$ ls -la ~/tools/llvm/bin/ld.lld
lrwxrwxrwx ... /home/apt/tools/llvm/bin/ld.lld -> lld          (it exists)
$ sed -n '168,171p' harness/build.py
    if mode == "whole" and "clang" in os.path.basename(cc):
        lld = os.path.expanduser("~/tools/llvm/bin/ld.lld")
        if os.path.exists(lld):
            cmd.insert(1, "-fuse-ld=lld")
```

⚠ **Note the line numbers**: `build.py` inserts it at **168-171**, not
169-172 as `TASK_PHP_005_REPORT.md` and `TASK_PHP_006.md` both say. Cosmetic,
but the shim now cites 168-171 because that is what the file says today.

## What the file now says

`common-php/emalloc_shim.h:463-511`. The old sentence — *"reports 0 for this
spelling on gcc/clang x O0/O3 x {-DSLB_ISOLATED,-flto}"* — is replaced by an
**itemised list of every cell, who ran it, and what happened**: the five
`TASK_PHP_004` matrix cells, the three non-`build.py` bounding cells, the one
that failed to link, the two that were never in the script, and the three
`TASK_PHP_005` cells re-run here. It ends:

> ✅ SO THE EIGHT-CELL CLAIM IS NOW TRUE, AND IT IS TRUE BECAUSE THE CELLS WERE
> RUN AND NOT BECAUSE THE NOTATION WAS TIDY.

and then states that `TASK_PHP_004_REPORT.md` Problem 1's limitation **does not
exist**, with the mechanism.

## The parameter-types comment

`emalloc_shim.h:499-511` replaces *"Do not 'simplify' the parameter types"*.
Verified against the pristine tarball myself before writing it:

```
$ grep -n ZEND_SIGNED_MULTIPLY_LONG php-5.0.0/Zend/zend_alloc.c
   234    ZEND_SIGNED_MULTIPLY_LONG(nmemb, size, lval, dval, use_dval);
$ sed -n '295p' php-5.0.0/Zend/zend_alloc.c
    int final_size = size*nmemb;                      (this is _ecalloc's T3)
```

The comment now describes **both** call sites — `zend_alloc.c:234`
(`_safe_emalloc`, `size_t`, wrapping unsigned) and `zend_operators.c:831`
(`mul_function`, `long`, signed UB) — says that the UB is PHP's and that a
faithful `mul_function` row **must** pass `long`, and records that the reviewer
measured 10 M signed + 20 M straddling samples with 0 disagreements and a
`0e813d9ad6308e5a` output hash stable across six configurations including
`-fwrapv`. It closes with *"that is an observation about this compiler, not a
guarantee"*.

## `emalloc_shim.c`'s comment — the sentence that caused the hole

`emalloc_shim.c:4-9` said *"THIS FILE IS NOT ON THE PATTERN BUILD PATH AND
CANNOT BE"*. It now says it is not a TU `build.py` compiles, and then says why
the second half was false and expensive:

> ⚠ **The audit did not cover this spelling BECAUSE OF THIS COMMENT.** A
> "cannot" that is only a "does not" is how a guard acquires a hole.

## What it cost

Exactly what the task budgeted: `digest_bridge.py --regen` (3 bridged files,
`emalloc_shim.c` `c9636c1e9dc2 → 3dd92f81ad1c`, `emalloc_shim.h`
`59b146689d42 → aa9abf48535e`), one `ph00` gate record STALE on
`common/digest_bridge.py`, one re-gate. **The measurement record stayed FRESH,
as predicted** — `ph00-smoke` does not link the shim, so
`measurement_sources` never sees it. No re-measure, no re-render.

⚠ **Line-number drift the manager owns:** `RECAP_PHP.md:164` and `:188` cite
`common-php/emalloc_shim.h:462`. That sentence is now at **:463** and the
surrounding block runs to :511.

---

# §4 F-4 — the overlap floor. Two bypasses, not one.

## The fix

`provenance.py::_normalise` now runs `_strip_comments` (translation phase 3,
with string/char-literal tracking) and then `_strip_dead_conditionals`
(`#if 0` regions, nesting-aware, `#else` arms preserved) before the existing
per-line filter.

⚠ **F-4 named `#if 0`. It is not the only spelling, and the second one is
easier.** `_normalise` dropped lines *starting with* `/*`, `*` or `//`, which is
not the same as dropping comments: a citation pasted inside

```c
/*
result->value.lval = op1->value.lval * op2->value.lval;
*/
```

counted in full, because the continuation lines start with neither. That is
case **B2** below and it was found here, not by the review.

## The regression test — and it is RUN, on every preflight

`provenance.py::OVERLAP_CASES`, seven cases, no tarball, no filesystem, no
compiler (~1 ms), run by `gate.py`'s preflight and by
`python3 harness-php/provenance.py --selftest`
(`.temp/php6/06-overlap-selftest.log`):

```
  ok    A verbatim lift, plausible             overlap  68% (13/19)  want 50% <= x < 101%
  ok    B wrong kernel + `#if 0`               overlap  11% (2/19)   want 0% <= x < 50%
  ok    B2 wrong kernel + block comment        overlap  11% (2/19)   want 0% <= x < 50%
  ok    B3 wrong kernel + nested `#if 0`       overlap  11% (2/19)   want 0% <= x < 50%
  ok    C control: wrong kernel, no dead code  overlap  11% (2/19)   want 0% <= x < 50%
  ok    D the excerpt itself                   overlap 100% (19/19)  want 99% <= x < 101%
  ok    E `#if 0` / `#else` -- the LIVE arm    overlap 100% (19/19)  want 99% <= x < 101%

7 overlap case(s), 0 FAILED
```

⚠⚠ **D and E are the half that matters and neither is in F-4.** Without them a
`_normalise` that returned the **empty set** would satisfy B, B2, B3 and C
vacuously and the self-test would go green on a normaliser that had stopped
measuring anything. That is `PROTOCOL.md` rule 1's *"before believing a check,
ask what would make it FAIL"*, applied to my own fix. **E** guards the opposite
error: the `#else` arm of a `#if 0` **is** compiled, so stripping it too would
refuse honest rows.

⚠ **Case A is kept at the reviewer's own realistic `verbatim` lift and still
scores exactly 68 %** — the floor did not get higher while it got harder to
fool. The reviewer's clean negative 7 survives.

## The reviewer's live attack, re-run unmodified

`.temp/php6/07-m5-overlap-AFTER.log`, `python3 .temp/php5/m5_overlap_attack.py`:

```
=== VERDICT ===
  A plausible verbatim lift : overlap 68%  accepted
  B wrong kernel + `#if 0`  : overlap 11%  refused        <-- was 100% ACCEPTED
  C control (must refuse)   : overlap 11%  refused -- CONTROL FIRED
```

## The claim itself, corrected in three places the tool prints

The task asked for this and it is the part that outlives the fix:

- `provenance.py`'s docstring itemisation gains a **`✗ NOT CHECKED  THAT THE
  CITED LINES ARE COMPILED`** entry — *"a pass measures TEXT IN A FILE, NOT CODE
  IN THE BENCHMARK"*;
- `kernel_overlap`'s docstring says the function reads `c/kernel*.{c,h}` and
  nothing else — not `main.c`, not the driver loop, not `build.py` — and that an
  unused `static` beside the driver's real callee scores the same;
- **every run prints it**, pass or fail:
  `⚠ the overlap measures TEXT IN kernel.c, not code in the benchmark -- it
  never reads main.c, the driver loop or the build, so a PASS is not evidence
  that the cited lines are COMPILED (TASK_PHP_005 F-4).`

---

# §5 F-5 — the size rule. ⚠ The answer is NO RULE, and both alternatives are refuted by measurement.

The manager asked for the distribution and one of (a) a limit, (b) a structural
rule, (c) no rule — **with the check that enforces it, or explicitly unenforced.**

## The distribution, over all 33 built PAT rows plus `ph00-smoke`

`.temp/php6/15-f5-why-sizes.log`, `19-f5-final-numbers.log`. Cut with
`wc -w`, the same cut the 200 and the 201 were taken with — ⚠ `RECAP_PHP.md`'s
size box warns that this quantity already has three answers and that arbitrating
it again is the wrong move, so I did **not** introduce a fourth definition.

```
PAT n=33   min 197   q1 527   median 989   q3 1544   p90 1817   MAX 3140
ph00-smoke 201  (200 words before the shared block + the single `.` after it)
```

## ⚠⚠ First: F-5's own corpus table is wrong, and so is open item 19's

`TASK_PHP_005` F-5 and `RECAP_PHP.md` open item 19 both measure the row-specific
half as `why[:why.find('NAMED-SPELLING STANDARD')]` — **the PREFIX ONLY** — and
report `p49-interned-pool` at **2 533** as the corpus maximum, with
`p16-tlv-walk` at **109** as the smallest.

**Two rows carry prose AFTER the shared block.** `check.py:1866` says so in one
clause (*"p17 carries pattern text after it"*), and it understates it
(`.temp/php6/17-f5-tail.log`):

```
row                          prefix w  block B  TAIL w  row-specific w
p16-tlv-walk                      109    11003    3031            3140
p17-http-range                    154    11003     346             500
(every other row: tail = 1, which is the single `.` that closes the sentence)
```

⚠ **`p16-tlv-walk`'s row-specific half is 3 140 words — the LARGEST in the
corpus — where F-5's table lists it as the smallest at 109.** The corpus maximum
is 3 140, not 2 533. Every block is exactly 11 003 bytes, matching the pin.

## (a) A word limit — REJECTED, and the numbers say why

```
  > 200 words: 30 of 34 rows break it (88%)     > 1000: 14 of 34 (41%)
  > 500 words: 24 of 34 rows break it (71%)     > 1500:  8 of 34 (24%)
  > 800 words: 19 of 34 rows break it (56%)     > 2000:  3 of 34 ( 9%)
```

Anything at or below the upper quartile (1 544) refuses a quarter of the built
corpus. Anything the corpus meets (≥ 3 140) permits **more than three times the
median** and would not have prevented the failure the rule exists for. And
imposing one on PAT means editing text **inside the hashed block** on 33 rows —
33 `contract_sha256` moves and 33 re-gates for a style rule.

## (b) A structural rule — REJECTED, and the manager's own phrasing is unsatisfiable

The task's example was *"the first paragraph is a self-contained summary,
unbounded thereafter"*. Measured (`.temp/php6/16-f5-structure.log`):

```
1. NEWLINES INSIDE `why`
   rows whose `why` contains ANY newline: NONE -- 0 of 34
```

⚠⚠ **No `why` in either programme contains a single newline.** None of them
*has* a second paragraph. The rule would be broken by **34 of 34 rows on day
one**, and giving them paragraph breaks is the same 33 re-gates. This is the
third version of this rule that cannot be met, and it would have been the
fourth failure.

The first-**sentence** variant *is* satisfiable — median 26 words, max 80, 0 of
34 over 80 — and it is **vacuous**:

```
  11x  each deletes something this pattern IS, and a rung that does ...
  11x  POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` findi ...
  14 distinct openers across 34 rows; 22 rows share one with another row
```

**22 of 34 rows open with one of exactly two boilerplate sentences.** A check
that they pass by sharing a sentence which says nothing about any of them
measures nothing. That is the same defect as the size rule, wearing a structure.

## (c) NO RULE — recommended, and here is what replaces it

`RECAP_PHP.md` already has no size rule and says so; the task file itself calls
that "a stable state, not an emergency". **I recommend leaving it there.**

⚠ **But "no rule" is not "no check", and the task's condition is met.**
`gate.py::why_sizes` computes each php row's row-specific size (prefix + tail),
prints it on **every** preflight, and writes it into the **committed** preflight
record:

```
  --   `idiom.why` row-specific size (REPORTED, NO LIMIT -- RECAP_PHP.md open item 19)
       | ph00-smoke: 201 words (200 before the shared block + 1 after).
         PAT corpus n=33: median 989, p90 1817, max 3140. NO LIMIT.
```

It **cannot fail a run** and the docstring says it must never grow the ability
to. **An unenforced size rule is what produced both previous failures; a
reported size is not a rule at all**, which is exactly why it is safe. The
number is in front of whoever writes the next `why`, and its history is in git.

## ⚠ A fourth wrong figure in the same box, for the manager

`RECAP_PHP.md`'s size-discipline box says *"one pattern's `why` field became a
single ~7,000-word JSON string"*. Measured over both programmes
(`.temp/php6/16-f5-structure.log` §3): the **largest total `why` is 4 995
words** (`p16-tlv-walk`); the smallest is 2 052; the median is 2 840. **No row
is over 7 000, or over 5 000.** I do not know what the 7 000 refers to and I am
not guessing — it may be a different artefact or a since-trimmed row. Flagging
it, not correcting it.

---

# §6 The minors

**F-6 — the preflight repairs before it checks. LANDED.** `check()` → `build()`
→ `check()`, with the difference recorded in `shim_repaired` and printed.
Re-ran the reviewer's plant (`.temp/php6/20-f6-stage1.log`):

```
planted: results -> ../../results          (the FROZEN PAT results tree)
root.py --check: rc=1  BAD  results: points at '../../results', want '../../results-php'
gate.py --preflight:
     ok   shim /home/apt/repos_common/sec-ladder/.temp/php-root
          | ⚠ REPAIRED BY THIS PREFLIGHT (was: results: points at '../../results',
            want '../../results-php') -- `shim_ok` below is a statement about the
            state AFTER the repair (TASK_PHP_005 F-6)
   recorded shim_ok=True  shim_repaired=["results: points at '../../results', ..."]
   REPAIR IS VISIBLE: True   OK -- TASK_PHP_005 F-6 closed
```

⚠ A repair is a **note**, not a failure: it errs safe and the shim is a derived
artefact. What was wrong was that it was **invisible**. `gate.py`'s docstring no
longer claims "FIVE things, all of which can fail" — it says seven, six of which
can fail, and names the exception.

**F-7 — `gate.py <row> --preflight`. LANDED.** `--preflight`,
`--no-provenance` and `--audit` are now reclaimed from the `REMAINDER`
wherever they appear, with a printed note (`.temp/php6/09-f2-record.log` §c):

```
$ python3 harness-php/gate.py ph00 --preflight
note: --preflight appeared after the row and is gate.py's own flag, not the
      tool's -- taken here rather than forwarded (TASK_PHP_005 F-7).
preflight OK (nothing else run)
  last run verdict='preflight only' tool_returncode=None tool_argv=['ph00']
```

⚠ The manager's 06:55 record — the instance — is **kept** in `runs[0]`, tagged
as migrated, `tool_returncode: 2` intact.

**F-8 — the false positive. CLOSED as a side effect of F-1.** `ph56-mention`,
whose only mention is the comment `PLAN_PHP.md` §4.3 tells a non-allocating row
to write, is no longer detected: the preprocessor does not read comments.

**F-9 — `digest_bridge.py`'s message. LANDED.** `GLOBBED_SUBDIRS` is derived
from `GLOB_PATTERNS` (not hand-listed, so it ages with it), and the refusal has
two texts. Both branches exercised by planting and restoring
(`.temp/php6/12-bridge-layout.log`):

```
=== planted common-php/layout -> ../common/layout   rc=1 ===
  BAD  SYMLINKED DIRECTORY: layout/ -- REFUSED, but not for the usual reason.
  check.py globs ['layout/*.py'] and FOLLOWS the link, so the files it matches
  WOULD be real `common/layout/…` keys in every php gate record. What is blind
  is THIS bridge: ... anything under layout/ that those globs do NOT match is in
  no digest and --verify would print `current` over it. ...

=== planted common-php/census -> ../common/census   rc=1 ===
  BAD  SYMLINKED DIRECTORY: census/ -- `os.walk` does not follow it, so
  everything behind it is in NO digest ...        (the original text, still true)

git status common-php after restore: only my three intended edits
```

The refusal is unchanged; only the reason is now true for the one name it was
false for.

**F-10 — `--sweep` is quote-sensitive. LANDED, and one step further.** The
patterns take `['"]` with an optional `rRfFbBuU` prefix, and a third pattern
handles the f-string spelling. The reviewer's own plant, re-run unmodified
(`.temp/php6/14-sweep-plant.log`):

```
  ⚠ GAP    corpus_a         dloop.py:841     (double quotes -- found before)
  ⚠ GAP    corpus_b         dloop.py:842     (SINGLE quotes -- was INVISIBLE)
  ⚠ GAP    corpus_c         dloop.py:843     (f-string    -- was INVISIBLE)
  ⚠ GAP    corpus_d         dloop.py:844     (two components -- found before)
```

All four spellings now derive. `harness/limbs.py:66`'s live single-quoted
`os.path.join(REPO, 'harness')` is attributed to `harness` rather than dropped.
The real tree is still clean:

```
$ python3 harness-php/root.py --sweep
  LINKED  .temp / common / harness / patterns / pilot / results / verus_run.py
  ⚠ 5 `os.path.join(REPO, <computed>)` site(s) this sweep CANNOT derive a component for:
    ? DYNAMIC  f      check.py:4524     ? DYNAMIC  k    check.py:9508
    ? DYNAMIC  k      check.py:9507     ? DYNAMIC  k    check.py:9510
    ? DYNAMIC  rel    measure.py:274
no gaps: every repo-root-relative component the sweep finds is covered by the link map.
rc=0
```

⚠ **Exactly five, matching the reviewer's independent count** — and they are now
**printed** rather than silently skipped, so the sweep's residual is visible to
its reader. ⚠ A gap-finding regex I wrote first reported **54** false DYNAMIC
lines because `\s*` backtracked to zero width and the negative lookahead was
evaluated at a space; the fix (`(?=\S)`) and the reason are in the source, since
that is exactly the class of silent error this sweep exists to avoid.

**F-11 — open items 13 and 14. PROPOSED, NOT LANDED** (`RECAP_PHP.md` is the
manager's). Both are now out of date in the *other* direction, because the
things they describe are fixed:

> **item 13** — proposed replacement for the tail: *"✅ `TASK_PHP_006` landed
> the rest of the cheap half: the record is **committed** (open item 18), holds
> **one entry per run** so a `--no-provenance` run can no longer be erased, and
> its **absence is detected** by `gate.py --audit` and by every preflight.
> ⚠ It is still evidence and not a pin — nothing hashes it — and making it one
> still costs a 33-pattern re-gate. The item stays OPEN for that reason and that
> reason only."*
>
> **item 14** — proposed replacement for the tail: *"✅ `TASK_PHP_006` fixed the
> normaliser (`#if 0` regions **and block comments**, `#else` arms preserved)
> and added **seven** regression cases run on every preflight, two of them
> must-NOT-fire so a normaliser that stopped measuring could not pass.
> ⚠ **The item stays open on the part no normaliser can fix**: the check reads
> `c/kernel*.{c,h}` and never `main.c`, the driver loop or `build.py`, so a pass
> is not evidence that the cited lines are compiled. That sentence is now
> printed by the tool on every run, which is the most that can be done about
> it."*

Open items **10**, **17**, **18**, **19** and **20** are also affected; the
manager owns the reconciliation, and §*What I refute* lists what changed.

**F-12 — `TASK_PHP_005.md:51`'s citation. TREATMENT PROPOSED, TASK FILE
UNTOUCHED.** Verified against the pristine tarball myself:

```
$ grep -n ZEND_SIGNED_MULTIPLY_LONG php-5.0.0/Zend/zend_alloc.c
   234    ZEND_SIGNED_MULTIPLY_LONG(nmemb, size, lval, dval, use_dval);   (the only one)
$ sed -n '295p' php-5.0.0/Zend/zend_alloc.c
    int final_size = size*nmemb;                                (_ecalloc's T3)
```

The reviewer is right: the main text cites `:295` for the second
`ZEND_SIGNED_MULTIPLY_LONG` call site and only the dagger has `:234`; `:295` is
a different mechanism.

**Proposed treatment — do NOT edit `TASK_PHP_005.md`.** `CLAUDE.md` keeps stale
citations in `.tasks*/` on purpose as the historical record, and a task file is
the record of what was *asked*, not of what is *true*. The durable correction
belongs where a reader will meet the fact, and **that is where I put it**:
`common-php/emalloc_shim.h:499-511` now names both call sites with the right
line numbers, inside the digest-pinned file. What I suggest the manager add is
one line in `RECAP_PHP.md`'s findings — *"`TASK_PHP_005.md:51` cites
`zend_alloc.c:295` for the `_safe_emalloc` call site; it is `:234`, and `:295`
is `_ecalloc`'s T3 — the dagger in that same line is correct"* — and nothing
else. ⚠ `PROTOCOL_PHP.md` §B's T3 row cites `:295` and is **correct**; do not
"fix" it.

---

# §7 The gate, and the closing bracket

## The re-gate the shim edit bought

`python3 harness-php/gate.py ph00`, PID 1181942, `.temp/php6/23-gate1.log`,
724 lines. **One gate run, no re-measure, no re-render** — as predicted from
`measurement_sources` not reaching `common-php/`. ⚠ Wall clock **≈5 minutes**
(the preceding preflight log is stamped 09:32:08 and the gate record 09:38:21),
well under the ~24 min the task budgets, because the build root was already
populated. ⚠ **Do not use `ps -o etime` in this sandbox to time a run** — it
reported `441077182-22:26:08` for this PID, and `kill -0` kept succeeding for
~15 minutes after the process had written its last byte. The file timestamps
are the only trustworthy clock here.

```
check.py: PASS-WITH-BLOCKED-ROWS
```

⚠ **The verdict is unchanged from the committed record** (`PASS-WITH-BLOCKED-ROWS`
before and after; the blocked row is the known `[miri] unsafe.rs on large.bin`
180 s timeout). Stage 9c passed with no re-render needed:

```
ok   results/tables/ph00-smoke.md exists and cites contract 91d88e1e18b1, which is this run's
ok   results/tables/ph00-smoke.md is byte-identical to a fresh render (6e772aadbbbd) ...
```

**What moved in the record — 2 of 1 079 leaf values**, diffed against
`git show HEAD:results-php/gate/ph00-smoke.json`:

```
1079 leaf values; 2 moved
  /source_sha256/common/digest_bridge.py
     c5321600ab44e054...  ->  298bac49524df1c5...     (the intended one)
  /miri/runs[7]/seconds
     1.1  ->  1.3                                     (wall clock)
verdict old: PASS-WITH-BLOCKED-ROWS -> new: PASS-WITH-BLOCKED-ROWS
```

Zero `Ir`, zero checksum, zero identity, zero contract hash.

## The closing bracket

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
preflight
  ok   shim /home/apt/repos_common/sec-ladder/.temp/php-root
  ok   common-php/ digest bridge
  ok   no patterns-php/*/c/ subdirectory (RECAP_PHP.md open item 17)
  ok   <row>/c/emalloc_shim.h symlink (PROTOCOL_PHP.md §B2)
  ok   provenance.py overlap self-test (7 cases)
  ok   patterns-php/MANIFEST.sha256
  --   `idiom.why` row-specific size (REPORTED, NO LIMIT -- RECAP_PHP.md open item 19)
       | ph00-smoke: 201 words (200 before the shared block + 1 after).
         PAT corpus n=33: median 989, p90 1817, max 3140. NO LIMIT.
  ok   every php record has a preflight record beside it

FRESH       results/gate/ph00-smoke.json               28 source(s)
FRESH       results/ph00-smoke.json                    18 source(s) + 8 input(s)

2 record(s) examined, 0 STALE
```

## The tree at the end

```
$ git status --porcelain
 M .gitignore
 M .tasks-php/PROTOCOL_PHP.md
 M common-php/digest_bridge.py
 M common-php/emalloc_shim.c
 M common-php/emalloc_shim.h
 M harness-php/gate.py
 M harness-php/provenance.py
 M harness-php/root.py
 M results-php/gate/ph00-smoke.json
?? .tasks-php/TASK_PHP_006_REPORT.md
?? results-php/preflight/
```

**Nothing under `harness/`, `common/`, `patterns/`, `results/` or `pilot/`.**
`results-php/preflight/` is newly untracked-and-committable — that is F-2 part
(a) landing, and the manager stages it.

```
$ git diff --stat
 .gitignore                  |  21 +-
 .tasks-php/PROTOCOL_PHP.md  | 150 +++++++++-
 common-php/digest_bridge.py |  56 +++-
 common-php/emalloc_shim.c   |  24 +-
 common-php/emalloc_shim.h   |  69 ++++-
 harness-php/gate.py         | 658 +++++++++++++++++++++++++++++++++++++++++---
 harness-php/provenance.py   | 346 ++++++++++++++++++++++-
 harness-php/root.py         |  51 +++-
```
(plus `results-php/gate/ph00-smoke.json`, 2 leaf values.)

## Scratch, per `CLAUDE.md` constraint 1

`.temp/php6/` keeps **23 logs and 10 generators**; every derived fixture tree
was deleted after its gates went green (`.temp/php6/fix`, and the trees my
re-runs recreated under `.temp/php5/`: `fix`, `fakerepo`, `m5fix`). No binaries
were left anywhere. ⚠ **Every generator in `.temp/php5/` is intact** — 29 entries,
including all ten of the reviewer's logs and `pat-snapshot.json`.
`.temp/php6/preflight-backup-before-006/` is the pre-task `results-php/preflight/`
state, kept.

---

# §8 What I refute

**Launched from 12. Three refutations, and a fourth figure flagged.**

1. ⚠ **Against the REVIEWER — `TASK_PHP_005` F-5's corpus table is measured on
   the wrong span.** It reports the row-specific half as the PREFIX only.
   `p16-tlv-walk` carries **3 031 words after** the shared block, so its
   row-specific half is **3 140 — the corpus MAXIMUM — where F-5 lists it as the
   minimum at 109**, and the corpus maximum is 3 140 rather than the reported
   2 533. `p17-http-range` is the second case (346). This propagates into
   `RECAP_PHP.md` open item 19.
2. ⚠ **Against the MANAGER — the structural rule the task file proposes is
   unsatisfiable.** *"The first paragraph is a self-contained summary,
   unbounded thereafter"* is broken by **34 of 34 rows**, because **not one
   `why` in either programme contains a single newline**. It would have been the
   fourth failed version of this rule. The first-sentence variant is
   satisfiable and **vacuous** — 22 of 34 rows share one of two boilerplate
   openers.
3. ⚠ **Against the MANAGER — `gcc -MM` is affordable**, contrary to §5 call 2's
   worry: **2 calls and ~115 ms per row**, batched. I did not need the
   string-detector fallback as the primary, and the `#include`-guard repair the
   task called "the obvious one" would have left `ph53-subdir` open.

**Flagged, not refuted** (I do not know what it refers to): `RECAP_PHP.md`'s
size-discipline box says a pattern's `why` became *"a single ~7,000-word JSON
string"*. The largest total `why` in either programme is **4 995 words**.

**Agreed with the reviewer, re-measured rather than taken on trust:** F-1's two
bypasses and the F-8 false positive (reproduced exactly before fixing); F-3's
three missing cells (byte-identical re-run) and the `-fuse-ld=lld` refutation;
F-4's `#if 0` false pass and its 68 % clean negative; F-6's silent repair;
F-7's flag forwarding; F-9's `layout/` message; F-10's five underivable sites.

---

# §9 What I did NOT do, and what I am unsure about

- **I did not touch `harness/`, `common/`, `patterns/`, `results/` or
  `pilot/`.** In particular I did **not** fix `check.py`/`measure.py`'s
  non-recursive `c/*` glob (§1.2, open item 17), as instructed.
- **I did not edit `RECAP_PHP.md`.** All state-layer wording is proposed in §6
  and §8.
- **I did not edit `TASK_PHP_005.md`** (F-12) — treatment proposed instead.
- **I did not add the `#error` guard for `-m32`** that `TASK_PHP_005` §2.4
  suggests for `emalloc_shim.h`'s hard-coded `#else` arm. It is adjacent work,
  not in this task, and it is a **behaviour** change to a digest-pinned file
  where everything else I did there was prose. ⚠ It is still open: on a `-m32`
  build the shim would keep the heuristic where real PHP takes the exact `imul`,
  and nothing detects it. Cost if the manager wants it: three lines and the
  same re-gate I have already paid, so it is cheapest to batch with the *next*
  shim edit.
- **`--audit` is not run by anything automatically.** It is a flag; the
  preflight prints the same information as a note. I judged a preflight failure
  to be a deadlock (§2c) and I may be wrong — if the manager prefers a hard
  failure, the change is one line and the deadlock needs an `--allow-uncovered`
  escape.
- **The `_norow.preflight.json` file will accumulate one entry per distinct
  no-row command line** (`--check-stale` variants). It is stable across repeats
  and small, but it is now committed and it is the one place this design can
  grow noise. Watch it.
- **`why_sizes` reads `patterns-php/` only**, and quotes the PAT band from a
  constant in the printed string. That constant will go stale if PAT ever gains
  a row. It is a message, not a check, and nothing depends on it — but it is a
  hard-coded number in a printed line, which is the rot class this project
  keeps finding, so I am naming it.
- **I did not re-verify the reviewer's PAT-tree byte snapshot.** I relied on
  `git status --porcelain` plus the fact that every command I ran against
  `harness/` was a read. That is weaker than `.temp/php5/snapshot.py`, which is
  still there and re-runnable.
- **`_tu_closure` hard-codes `gcc`.** `build.py` builds C cells with both `gcc`
  and `clang`, and the include closure is compiler-independent for the
  constructs in play, but a row using a GCC-only `__has_include` idiom could in
  principle differ. Not exercised, not guarded.
