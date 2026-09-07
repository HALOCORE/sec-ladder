# TASK_PHP_005 — adversarial review of `TASK_PHP_004` — REVIEWER REPORT

**Role:** research reviewer. **Launched from a running count of 9**; this review
refutes **three** figures/claims (§ *What I refute*) and reconciliation is the
manager's job.

> **No-touch disclosure, verified by bytes, not by `git status`.** I snapshotted
> `harness/ common/ patterns/ results/ pilot/` (2966 paths, sha256 per file,
> symlink targets recorded) before touching anything and re-checked at the end,
> and I built a **positive control** for the snapshot tool first, because a
> checker that cannot fail proves nothing:
>
> ```
> snapshot: 2966 paths under ['harness','common','patterns','results','pilot'] -> .temp/php5/pat-snapshot.json
> control: 27 files snapshotted, one byte-appended
>   CHANGED  common/slb.py  2abd87f76712 -> 27618554643a
> CONTROL FIRED
>
> snapshot check: 2966 recorded, 2966 now, 0 difference(s)     (last command)
> git status --porcelain                                       (empty)
> ```
>
> Both staleness checks, first and last:
>
> ```
> python3 harness/measure.py --check-stale                 66 record(s) examined, 0 STALE   (first)
> python3 harness-php/gate.py --tool measure --check-stale  2 record(s) examined, 0 STALE   (first)
> python3 harness/measure.py --check-stale                 66 record(s) examined, 0 STALE   (last)
> python3 harness-php/gate.py --tool measure --check-stale   2 record(s) examined, 0 STALE   (last)
> ```
>
> **Planting disclosure.** I planted into exactly two places, both restored in a
> `finally:` and both verified afterwards: a `common-php/layout` directory
> symlink (F-9) and a mis-aimed link inside the gitignored `.temp/php-root/`
> shim (F-6). `git status --porcelain common-php` was empty after the first;
> the whole-tree `git status` is empty and the 2966-path snapshot is unchanged.
> I overwrote the gitignored `results-php/preflight/*.json` while measuring F-2
> and **restored the directory from a backup** (`.temp/php5/preflight-backup/`);
> `_norow.preflight.json` is mine (07:55, my first `--check-stale`), not the
> manager's.

**Everything below was run.** Scratch, generators and logs under `.temp/php5/`;
every binary deleted, every generator kept.

---

## Summary

| | rank | finding |
|---|---|---|
| **F-1** | **blocker** | §1's textual guard **is bypassable**. Two constructed rows link a live allocator, **build, link and run**, and put it in **NEITHER digest** — while `gate.py`'s preflight says nothing. `RECAP_PHP.md:58-59`'s *"B1 CLOSED"* does not hold. |
| **F-2** | major | The gitignored preflight record is worse than the manager feared: it is also **overwritten by the next invocation** (measured), nothing detects its absence, and the `.gitignore:24-26` churn rationale is **half wrong** — only `when` moves. |
| **F-3** | major | The fidelity claim *"0 disagreements on gcc/clang × `-O0`/`-O3` × `{-DSLB_ISOLATED,-flto}`"* (`RECAP_PHP.md:164`, and in the **digest-pinned** `common-php/emalloc_shim.h:462`) names 8 cells of which **5 were run**. I ran the other 3; they are 0/20 M. **And the engineer's disclosed limitation does not exist**: `clang -O3 -flto` links fine with `-fuse-ld=lld`, which is the flag `build.py:169-172` itself inserts. |
| **F-4** | major | `provenance.py`'s kernel-overlap floor is **satisfied by dead code**: a kernel that implements *division*, cites *multiplication*, and carries the citation behind `#if 0` scores **100 %** and is ACCEPTED. |
| **F-5** | major | `RECAP_PHP.md:30-31`'s repaired size rule (*row-specific `why` ≤ 200 words*) is calibrated on **n = 1** and is broken by **30 of 33** PAT rows (up to 2 533 words); `p01`, the template, is 201. Enforced by nothing. |
| F-6 | minor | The preflight's stage 1 **repairs the shim before it checks it**, so a mis-aimed link is silently fixed and recorded `shim_ok: true`. `root.py --check` catches it; the preflight cannot. |
| F-7 | minor | `gate.py <row> --preflight` silently forwards `--preflight` to the tool and runs it. **The manager's own 06:55 preflight record is an instance.** |
| F-8 | minor | `shim_link_audit` **false-positives** on a row that only *mentions* `emalloc_shim.h` in a comment, with a message asserting it `include(s)` it. |
| F-9 | minor | `digest_bridge.py`'s symlinked-directory refusal blocks `common-php/layout -> ../common/layout`, whose files **are** globbed by `check.py`; the refusal message's stated reason is false for that one name. |
| F-10 | minor | `--sweep` is quote-sensitive: single-quoted and f-string repo-root paths are invisible. `harness/limbs.py:66` is a live instance (benign today). |
| F-11 | minor | `RECAP_PHP.md` open item 13 describes a preflight record without saying it is uncommitted; open item 14 **understates** what F-4 shows. |
| F-12 | minor | `TASK_PHP_005.md:51`'s own ✅ cites `zend_alloc.c:295` for the second `ZEND_SIGNED_MULTIPLY_LONG` call site. It is **`:234`** (the dagger has it right); `:295` is `_ecalloc`'s T3. |

**Clean negatives — nine attacks that did NOT land** are in the last section.
Three of the five §1 candidates, and **all four** §2 attacks, failed.

---

# §1 — the allocator guard. TWO OF FIVE BYPASSES LAND.

`gate.py:182-188` classifies a row as a shim user by searching each `c/*` file
for the literal `emalloc_shim.h`. I built one row per candidate, ran
`shim_link_audit` on them, computed **check.py's own `srcs` glob** and
**`measure.py::measurement_sources`** over each, and compiled each with
`build_c`'s real flags. Generator: `.temp/php5/b1_bypass.py`,
`.temp/php5/buildtest.sh`. Log: `.temp/php5/01-b1-bypass.log`.

```
common-php/emalloc_shim.h sha256 = 59b146689d42

--- ph50-direct          (control: the known B1 case)
    shim reaches the TU      : True
    preflight DETECTS it     : True   (expected True)
    allocator in GATE digest : False      allocator in MEAS digest : False

--- ph51-linked          (control: the same row WITH the canonical symlink)
    shim reaches the TU      : True
    preflight DETECTS it     : False  (expected False)
    allocator in GATE digest : True       allocator in MEAS digest : True

--- ph52-indirect        (candidate 1: c/kernel.c -> c/row_alloc.h -> the shim)
    preflight DETECTS it     : True   (expected True)
    -> allocator: ph52-indirect: c/row_alloc.h include(s) emalloc_shim.h and ... IS ABSENT.

--- ph53-subdir          (candidate 2: c/sub/row_alloc.h)
    shim reaches the TU      : True   ['.../common-php/emalloc_shim.h']
    preflight DETECTS it     : False  (expected True)
    allocator in GATE digest : False      allocator in MEAS digest : False
    ⚠⚠ ALLOCATOR IN NEITHER DIGEST  <-- this is the B1 defect

--- ph54-dotc            (candidate 5: #include "emalloc_shim.c")
    shim reaches the TU      : True   ['.../emalloc_shim.c', '.../emalloc_shim.h']
    preflight DETECTS it     : False  (expected True)
    allocator in GATE digest : False      allocator in MEAS digest : False
    ⚠⚠ ALLOCATOR IN NEITHER DIGEST  <-- this is the B1 defect

--- ph55-extern          (candidate 3: extern decl, no #include)
    shim reaches the TU      : False

--- ph56-mention         (a comment that only NAMES the header)
    preflight DETECTS it     : True   (expected False)   <-- false positive, F-8

--- ph57-rust            (candidate 4: unsafe.rs carries the extern "C")
    preflight DETECTS it     : False
```

## F-1 (blocker) — `#include "emalloc_shim.c"` and `c/<subdir>/*.h` both bypass it

Both rows **build, link and run with a live allocator**
(`.temp/php5/buildtest.sh`, `02-buildtest.log`, `02b-buildtest-subdir.log`), at
`build_c`'s real flags (`gcc -std=c99 -Wall -Wextra -O3 -DSLB_ISOLATED -I COMMON
-I <row>/c`):

```
=== ph53-subdir ===
  LINKED ok  ->
alloc tally = 7688571
=== ph54-dotc ===
  LINKED ok  ->
alloc tally = 7688571
```

**Answer to the task's question — the allocator ends up in NEITHER digest for
both**, which the task file itself names as the unfixed B1 defect.

**Mechanism (a), `gate.py:134`.** `SHIM_HEADER = "emalloc_shim.h"`. The audit
knows only the `.h`, exactly as §1.5 suspected. `common-php/emalloc_shim.c` is
two lines — `#define PHP_SHIM_IMPL` / `#include "emalloc_shim.h"` — and lives on
`-I COMMON`, so `#include "emalloc_shim.c"` from `c/kernel.c` pulls the whole
allocator in while no `c/*` file contains the string `emalloc_shim.h`.
⚠ `emalloc_shim.c`'s own header comment says it *"IS NOT ON THE PATTERN BUILD
PATH AND CANNOT BE"* — true of `build.py`'s TU list, **false of the
preprocessor**, and that sentence is the reason the audit did not cover it.

**Mechanism (b), `gate.py:182`.** `glob(cdir + "/*")` is non-recursive **and so
are the two digests**. Measured:

```
check.py c/* glob returns : ['c/kernel.c', 'c/kernel.h', 'c/main.c', 'c/sub']
  of which isfile()       : ['c/kernel.c', 'c/kernel.h', 'c/main.c']
actual files under c/     : ['c/kernel.c', 'c/kernel.h', 'c/main.c', 'c/sub/row_alloc.h']
```

⚠⚠ **This is bigger than the allocator, and it is the accidental half.**
`check.py:10314` and `measure.py:226` both glob `<row>/c/*` and then drop
non-files with `if os.path.isfile(s)`, so **every source file a row puts in a
`c/` subdirectory is in no digest at all** — the directory entry is silently
discarded and the record shows no trace either way. The php corpus is
*extracted C*: a row lifting several PHP headers into `c/zend/` is an ordinary
organisational choice, not an attack, and `check.py`'s `--no-build` staleness
scan (`check.py:10187-10189`) misses those files too, so edits to them do not
even mark a binary stale. ✅ No row is affected today — `find patterns
patterns-php -mindepth 3 -maxdepth 3 -type d -path '*/c/*'` returns nothing —
so this is forward risk, not a corrupted record.

**Concrete failure scenario** (identical to the one B1 was opened for): row
`ph07` writes `#define PHP_SHIM_IMPL` / `#include "emalloc_shim.c"` in
`c/kernel.c` because that is the spelling `emalloc_shim.c`'s own docstring
advertises for "standalone consumers". Preflight: green. Gate: green. Six
months later `emalloc_shim.h`'s cache arm is corrected → `digest_bridge.py
--regen` → the *gate* record goes stale and re-gates, and **`ph07`'s measurement
record stays `FRESH` for ever**, carrying every `Ir` taken under an allocator
that no longer exists. That is verbatim the failure `RECAP_PHP.md` open item 10
and `gate.py:73-99` say is closed.

**What I am NOT claiming:** nothing published is wrong today (0 php rows built),
and the *sanctioned* spelling is fully protected — `ph51-linked` puts the
allocator in **both** digests. What is invalidated is the state-layer sentence
**`RECAP_PHP.md:58-59` "B1 CLOSED"**. Per the task file's own rubric
(*"Neither is the B1 defect, unfixed, and is a blocker"*), blocker.

## §1's second half — the preflight is skippable, and nothing shows it afterwards

```
$ python3 .temp/php-root/harness/measure.py --check-stale        # no gate.py
2 record(s) examined, 0 STALE
$ ls -la results-php/preflight/                                  # nothing new
```

- `PLAN_PHP.md:160-185` (§2.1a) documents exactly this spelling as the design,
  and `PROTOCOL_PHP.md:243` (*"Never run `harness/check.py` directly on a php
  row"*) is the only thing standing against it — **a word in a document**, which
  is `TASK_PHP_004`'s own `.memory-php/` candidate #2, applied to `gate.py`.
- **Nothing downstream records that the wrapper ran.** `grep -c preflight
  harness/{check,measure,report}.py` → `0 0 0`. The gate record's 37 top-level
  keys contain no preflight field, and its `invocation` is `ph00` — **byte-identical
  whether the run went through `gate.py` or not**.
- ⚠ Combined with F-2, a php row can be gated with no preflight, no provenance
  check and no symlink audit, and leave **no artefact either way**.

---

# §2 — B2. Four attacks, FOUR CLEAN NEGATIVES, and one refuted limitation.

`.temp/php5/mul_probe2.c` / `.sh`, log `04-mul_probe2.log`. It includes the
**pristine** macro straight out of the tarball (`extract_pristine.sh`, sha256
checked) and the shim's, and compares `usedval`, `lval` **and `dval`
bit-exactly** (`memcmp` on the double).

```
### gcc -O0                        (identical on gcc -O3, -fwrapv, -fno-strict-overflow, clang -O0, clang -O3)
  S1 non-negative (the 004 draw)   samples 20000000 overflow 9182490  usedval 0 lval 0 dval 0 | CONTROL(builtin) 84523
  S2 signed, both signs            samples 5000000  overflow 2294912  usedval 0 lval 0 dval 0 | CONTROL(builtin) 21170
  S2b signed, full 64-bit uniform  samples 5000000  overflow 5000000  usedval 0 lval 0 dval 0 | CONTROL(builtin) 0
  S3 directed cross product +-2    samples 28900    overflow 15308    usedval 0 lval 0 dval 0 | CONTROL(builtin) 414
  S3b straddling LONG_MAX          samples 20000000 overflow 8003659  usedval 0 lval 0 dval 0 | CONTROL(builtin) 3692
  OUTPUT-STREAM HASH (pristine macro, all spaces): 0e813d9ad6308e5a
```

- **§2.1 negatives — refuted as a gap.** S1 reproduces `84 523` exactly, so the
  sample space is the review's. S2/S2b add **10 M signed** samples including
  `LONG_MIN`, `-1` and zero crossings; the builtin control **fires 21 170** there,
  so the negative region genuinely *is* a disagreement region — and the shim
  tracks PHP through all of it, `dval` included.
- **§2.2 `dval` — refuted as a gap.** Compared bit-exactly on every space above:
  0 differences on 45 M+ samples. A `mul_function` row can use the macro as
  shipped.
- **§2.3 directed — the uniform draw was brushing it, and the directed test
  agrees anyway.** S3 is a 34×34 cross product of `LONG_MAX`, `LONG_MIN`, ±2^53,
  ±2^62, `isqrt(LONG_MAX)`, `isqrt(2^53)` and the three hand-picked `TASK_PHP_003`
  cases, each ±2 on both operands: **53 %** of those samples overflow and the
  control fires on **1.43 %** of them, against 0.42 % for the uniform draw. S3b
  puts 20 M products within ±2 of `LONG_MAX/b`. Still 0.
- **§2.5 the same-TU residual, PRICED.** The engineer's honest worry was that
  `ref` and `shim` are one TU, so a shared miscompilation is invisible. The
  **whole output stream of the pristine macro hashes to `0e813d9ad6308e5a` on
  six configurations spanning two compilers, two optimisation levels and both
  `-fwrapv` and `-fno-strict-overflow`** — and within each configuration
  `shim == ref`, so the shim's output stream is that same invariant stream in
  all six. A shared miscompilation would now have to be shared by gcc and clang
  and be insensitive to `-fwrapv`. **The gap is not closable to zero without a
  compiled PHP 5.0.0 binary, but it is now much smaller than "one TU".**

## F-3 (major) — the 8-cell claim was a 5-cell measurement, and the stated limitation does not exist

`RECAP_PHP.md:164` and — this is the sharp half — **`common-php/emalloc_shim.h:462`,
which `digest_bridge.py` pins into every php gate record**, both say:

> *0 disagreements on gcc/clang × `-O0`/`-O3` × `{-DSLB_ISOLATED,-flto}`*

That product is 8 cells. `.temp/php4/mul_probe.sh:22-27` runs **five** of them
(`gcc-O0-iso`, `gcc-O3-iso`, `gcc-O3-lto`, `clang-O0-iso`, `clang-O3-iso`);
`gcc -O0 -flto` and `clang -O0 -flto` are **not in the script at all**, and
`clang -O3 -flto` failed to link:

```
$ cat .temp/php4/mp_clang-O3-lto.cc.log
/usr/bin/ld: .../lib/LLVMgold.so: error loading plugin: ... No such file or directory
clang: error: linker command failed with exit code 1
```

✅ `RECAP_PHP.md:62`'s *"8 build configs"* is **not** the overclaim — 8 runs did
produce output (5 matrix + 3 bounding). The Cartesian notation is.

**I ran the three missing cells with the engineer's own probe** so the numbers
are directly comparable (`.temp/php5/mul_probe_missing.sh`, log
`09-mul-missing-cells.log`):

```
### gcc-O0-lto        agree 20000000  DISAGREEMENTS 0   CONTROL 84523 FIRED
### clang-O0-lto      agree 20000000  DISAGREEMENTS 0   CONTROL 84523 FIRED
### clang-O3-lto-lld  agree 20000000  DISAGREEMENTS 0   CONTROL 84523 FIRED
```

**So the claim is now true — and `TASK_PHP_004_REPORT.md:494-499`'s Problem 1 is
refuted.** *"`clang -O3 -flto` cannot link on this box"* is false: it links with
`-fuse-ld=lld`, and `harness/build.py:169-172` **inserts exactly that flag for
every clang whole-mode cell**, so the engineer's probe was the only thing
missing it — the engineer even noted the guarded path existed and did not try
it. `PROTOCOL.md` rule 13's shape: **a stated limitation that does not exist**.

## §2.4 — the `__i386__` scope IS recorded, and is not enforced

`emalloc_shim.h:443-446` states it explicitly (*"on x86-64 `__i386__` IS NOT
DEFINED"*), so §2.4's worry is answered — but the shim hard-codes the `#else`
arm with **no `#if defined(__i386__) && defined(__GNUC__)` guard and no
`#error`** (`grep -n 'i386' common-php/emalloc_shim.h` → two hits, both prose).
On a `-m32` build the shim would keep the heuristic where real PHP takes the
exact `imul`, and the shim would then be wrong **in the opposite direction** —
refusing where PHP allocates. Nothing detects it. Low priority (`build.py` never
passes `-m32`); worth three lines of `#error`.

⚠ One tension for the TYPE axis, stated because the manager asked about it in
§7.3: `emalloc_shim.h:465-468` says *"Passing `long` here would be undefined
behaviour ... Do not 'simplify' the parameter types."* — but
`zend_operators.c:831`, the TYPE axis's own integer-overflow candidate, **does**
pass `long`, and that UB is PHP's, not the shim's. A faithful `mul_function` row
must pass `long` and will therefore contradict that sentence. My S2/S2b run *is*
the long-operand case: 10 M samples, 0 disagreements, hash unmoved under
`-fwrapv`. So the UB does not bite on this box — but the comment should say
"`_safe_emalloc` passes `size_t`; `mul_function` passes `long`", not "do not".

---

# §3 — the majors. Three attacked, four left unexamined.

## F-4 (major) — the kernel-overlap floor is satisfied by DEAD CODE

`.temp/php5/m5_overlap_attack.py`, log `05-m5-overlap.log`. The `verbatim` row is
`Zend/zend_operators.c:821-850`, `mul_function` — the TYPE axis's own leading
candidate and the call site of the macro B2 is about.

```
### A  plausible `verbatim` lift of mul_function
    overlap 68%  (13/19 excerpt lines)   verdict ACCEPT
### B  WRONG kernel (division) + the citation behind `#if 0`
    overlap 100% (19/19 excerpt lines)   verdict ACCEPT
### C  CONTROL: the same wrong kernel, no dead code
    overlap 11%  (2/19 excerpt lines)    verdict REFUSE
      | C-wrong-control: KERNEL DOES NOT MATCH THE CITATION. Only 11% ...

=== VERDICT ===
  A plausible verbatim lift : overlap  68%  accepted
  B wrong kernel + `#if 0`  : overlap 100%  ACCEPTED -- FALSE NEGATIVE
  C control (must refuse)   : overlap  11%  refused -- CONTROL FIRED
```

`provenance.py:190-207` `_normalise` drops lines that **start with** `#`, so
`#if 0` and `#endif` vanish and every line between them counts. Kernel `B`
implements division, cites multiplication, and passes at 100 % while the same
kernel without the dead block is refused at 11 % — the control proves the floor
works and proves what it is measuring.

**A fortiori, and this is the accidental version:** the check never consults
`main.c`, the driver loop or the build, so a kernel that keeps the extracted
function as an *unused static function* beside the one the driver actually calls
scores the same 100 %. `build.py` passes `-Wall -Wextra` and not `-Werror`, so
`-Wunused-function` does not stop it either. **The floor measures presence of
text in a file, not presence of code in the benchmark.**

**Failure scenario:** a row cites 30 lines of `zend_hash.c`, keeps them verbatim
for reference, and benchmarks a simplified re-expression. Tier stays `verbatim`,
provenance is green, and the published table attributes PAT-comparable numbers
to code the citation does not describe. `RECAP_PHP.md` open item 14 says the
check *"cannot prove an extraction"*; it should say **a pass is not even
evidence that the cited lines are compiled**.

⚠ **My false-refusal attack did NOT land** — see the clean negatives. The floor
is not too high; it is too easy.

## F-10 (minor) — `--sweep` derives an eighth link, but only in one spelling

`.temp/php5/sweep_plant.sh` builds a fake REPO of symlinks (root.py's REPO is
`dirname(dirname(abspath(__file__)))`, and `abspath` does not resolve links) and
plants four spellings of an eighth repo-root-relative path into a copy of
`dloop.py`:

```
  ⚠ GAP    corpus_a         dloop.py:843      # os.path.join(REPO, "corpus_a")
  ⚠ GAP    corpus_d         dloop.py:846      # os.path.join(REPO, "corpus_d", "sub")
  (corpus_b -- SINGLE quotes -- and corpus_c -- f-string -- are NOT reported)
```

✅ **So M2's fix is real: the sweep genuinely discovers an eighth, not merely a
deletion.** The gap is that `_JOIN_REPO`/`_JOIN_FILE` (`root.py:224-227`) require
double quotes. An independent extraction over the same nine modules
(`07-sweep-residue.log`) finds **6 REPO-path lines the sweep does not match**:
five are `os.path.join(REPO, <variable>)` (inherently underivable — the
component is a `source_sha256` key at run time, all covered today), and one is
**`harness/limbs.py:66: sys.path.insert(0, os.path.join(REPO, 'harness'))`** —
a live single-quoted instance, benign only because `harness` is already linked.
One `'` in a future harness edit and the sweep goes quiet.

## F-9 (minor) — `digest_bridge.py` refuses a layout its own reason does not cover

Planted `common-php/layout -> ../common/layout` and restored it
(`08-bridge-layout.log`):

```
  check.py's own glob common-php/layout/*.py sees:
     ['modesim2.py','layout_gen.py','predict_then_time.py','analyze.py',
      'survives.py','loopfit.py','order.py','q3_convergence.py']
  digest_bridge --verify rc = 1
  BAD  SYMLINKED DIRECTORY: layout/ -- `os.walk` does not follow it, so
       everything behind it is in NO digest ...
  git status common-php: ''      (restored)
```

**Refusing is the right default** and the cross-programme argument in
`digest_bridge.py:134-140` is sound. But `layout/` is the *one* subdirectory
name `check.py` globs (`check.py:10323`), so those eight files would be real
`common/layout/*.py` keys in every php gate record — the message's *"everything
behind it is in NO digest"* is measurably false for exactly that name. If the
php side ever needs `common/layout/`, the sanctioned repair (per-file symlinks)
costs eight links and a `--regen`; the check should special-case `layout/`
against `GLOB_PATTERNS` rather than assert something untrue.

## Left unexamined (declared, per the task)

M6's trace (covered indirectly by F-2), M3's tree set, M4's doc corrections
beyond the header/body pass I read, minors `m3`, `m4`, `m6`, `m7`.

---

# §4 — the manager's three decisions

## F-2 (major) — yes, the preflight gitignore is a major, and it is worse than "not committed"

**1. Is it a `major`? Yes.** Not a blocker — no published number depends on it —
but `TASK_PHP_003` M6 asked for the trace on the ground that *"a run certified by
a tool nobody can pin is not certified"*, and the trace now lives only in an
uncommitted file that `git clean -xdf` removes. Three measured facts, in
increasing order of how much they matter:

**(a) It is last-write-wins.** Measured, `.temp/php5/03-*`:

```
after --no-provenance : {'provenance_checked': False, 'provenance_skipped': True,
                         'gate_argv': ['--preflight','--no-provenance','ph00']}
after the next run    : {'provenance_checked': True,  'provenance_skipped': False,
                         'gate_argv': ['--preflight','ph00']}
```

So even on the machine that ran it, **any later preflight erases the record that
provenance was skipped.** `gate.py:344-362` writes one file per *row*, not per
run. This is independent of the gitignore and would be a defect either way.

**(b) Nothing detects the absence of a record for a gated row.** `grep -c
preflight harness/{check,measure,report}.py` → `0 0 0`; nothing outside
`gate.py`, `root.py` and the prose mentions it. With §1's second half, a gate
record and no preflight record is indistinguishable from a gate record whose
preflight file was deleted, or never written.

**(c) The stated churn is one field, not two.** `.gitignore:24-26` says the file
*"carries a `when` timestamp and the literal `gate_argv`, so it churns on every
run — measured, two consecutive identical-source runs differ."* Two identical
runs, measured here:

```
33c33
<   "when": "2026-09-07T07:58:34"
---
>   "when": "2026-09-07T07:58:36"

.temp/php5/pf1.json   when=...07:58:34  sha256(rest)=d91ce008ad273b36
.temp/php5/pf2.json   when=...07:58:36  sha256(rest)=d91ce008ad273b36
```

**`when` is the only mover. `gate_argv` is a function of the command, not of the
run** — and *that* is precisely the evidence M6 wanted. The churn measurement
was right; the inference from it ("and `gate_argv`") was not.

**2. Is there a split that gets both? Yes, and it is one field.** Everything
except `when` is byte-identical across two runs (`d91ce008ad273b36` twice), and
across *different* runs only the four fields that carry information move:

```
fields differing between my run and the manager's 06:55 record:
   gate_argv       ['ph00','--preflight']  ->  ['--preflight','ph00']
   tool_argv       ['ph00','--preflight']  ->  ['ph00']
   tool_returncode 2                       ->  None
   verdict         'tool exited'           ->  'preflight only'
```

Committing `{row, shim_ok, digest_bridge_ok, allocator_symlink_ok, manifest,
provenance_checked, provenance_skipped, harness_php_sha256, tool, gate_argv,
verdict}` and dropping `when` (or splitting it into an ignored sidecar) gives a
file that moves **only when something a reader should notice moved**. It would
still need (a) fixing — append, or key on run, not on row.

**3.** Answered in (b): nothing.

## The withdrawn byte count — SUPPORTED, and here is the missing byte

Re-measured (`patterns-php/ph00-smoke/spec.md`, `check.py:1865-1910`):

```
total why: 12224 chars, 2056 words
row-specific prefix : 1220 chars, 200 words
shared block        : 11004 chars, 1856 words
BEGIN idx 1220  END idx 12204  len('p01 and p08 neither') 19
check.py's slice length : 11003
marker->EOS length      : 11004
the residue after the END marker: '.'
```

✅ **The manager's withdrawal is right and the mechanism is a single full stop.**
11 003 is `check.py`'s pinned slice (`BEGIN` → end of the `END` marker); 11 004 is
`BEGIN` → end of string; the difference is the `'.'` that closes the sentence.
Both are correct about different cuts, exactly as `RECAP_PHP.md:20-29` now says,
and `TASK_PHP_004_REPORT.md:406`'s *"the reviewer is right; 11 004 was wrong"* is
the false precision the manager withdrew. **The 200 is right**: exactly 200 words.

## F-5 (major) — but the *repaired rule* is still unsatisfiable

`RECAP_PHP.md:30-31`: *"the ROW-SPECIFIC half of `why` stays ≤ 200 words"*, and
`RECAP_PHP.md:32-33` warns in the same breath that *"a size rule that cannot be
met is worse than none"*. Measured over the corpus the 200 was derived from:

```
patterns/p01-array-sum/spec.md         row-specific: 1177 chars, 201 words
patterns-php/ph00-smoke/spec.md        row-specific: 1220 chars, 200 words

PAT rows whose row-specific half exceeds 200 words: 30
   p49-interned-pool  2533   p18-varint-shift 2172   p36-vtable-dispatch 2062
   p34-refcount-stack 1817   p14-field-split  1722   p35-tagged-union    1604
   p09-bitset         1577   p06-rotate       1508   p25-realloc-growth  1473
   p10-fir-stencil    1453   ...
```

**30 of 33 rows break it, by up to 12×**, and `p01` — the template every row
clones, and the row `PROTOCOL_PHP.md:304` cites as already complying — is **201**.
The 200 is not a limit derived from anything; it is the measurement of the single
row that happened to be measured. **And it is enforced by nothing**: the only
`why` check in the tree is `check.py::named_spelling_problem`, which pins the
shared 11 003-byte tail and says nothing about length. §1's lesson, third
instance this programme.

## Accepting `TASK_PHP_004`'s `RECAP_PHP.md` edits — review of the hunks

| item | verdict |
|---|---|
| **9** (`+34`, `+1 nvar`, `3686 → 3695`, `repo_path_bytes +15`) | ✅ **supported.** I re-ran `.temp/php4/m1_env_test.py` in my own shell and got the same numbers (`3279/48/3663` → `3305/49/3697`, delta `+26/+1/+34`), and `25 + NUL + 8 = 34` is the right derivation. `+15` is `len('/.temp/php-root')`. |
| **13** (`harness-php/*.py` in no digest; the preflight is evidence, not a pin) | ⚠ **supported but now incomplete** — it was written before the gitignore and does not say the record is uncommitted, overwritten per row, or absent from a fresh clone. `.gitignore:27-28` points *at* item 13; item 13 does not point back. (F-11) |
| **14** (overlap floor is a heuristic; no row has exercised it) | ⚠ **says LESS than the evidence.** F-4 shows a pass can be manufactured with dead code, so *"the first row that trips a floor should be judged"* is the wrong half of the risk — the first row that **passes** one needs judging too. |
| **15** (php `--check-stale` is a different command; 2 records) | ✅ **supported**, re-run: `2 record(s) examined, 0 STALE`. |
| **F6's rewrite** | ⚠ **overclaims on the config matrix** — see F-3. Everything else in it (the `#else` arm, the 84 523, the *"needs a differential test with a must-fire control"* rule, the same-TU caveat) is supported and, after my three extra cells and six-config hash, is now *more* supported than when it was written. |

**The boundary itself (open item 16): I agree with the manager's call.** The
content is accurate and the one-sentence fix in the task template is the right
remedy, not a rollback. This report is that rule-9 review; nothing in the five
hunks needs reverting, item 13 needs a clause and item 14 needs strengthening.

---

# The remaining minors

**F-6 (minor) — the preflight repairs before it checks.** `gate.py:287-292` calls
`rootmod.build()` and *then* `rootmod.check()`, so stage 1 verifies the state it
just created. Planted `.temp/php-root/results -> ../../results` (the **frozen PAT
results tree**) and restored it; `10-preflight-stage1.log`:

```
planted: results -> ../../results
root.py --check on the planted shim:
   rc=1  BAD  results: points at '../../results', want '../../results-php'
gate.py --preflight on the planted shim:  rc=0
     ok   shim /home/apt/repos_common/sec-ladder/.temp/php-root
   link after the preflight: ../../results-php
with a stray FILE in the shim:  rc=2
     FAIL shim /home/apt/repos_common/sec-ladder/.temp/php-root
restored: results -> ../../results-php
```

The preflight is **strictly weaker than the tool it wraps**, and `shim_ok: true`
in the record is a statement about the state *after* an unlogged repair. It errs
safe (it repairs to the correct target), but `gate.py:46` — *"The preflight is
FIVE things, all of which can fail"* — is not true of stage 1 for the mis-aimed
case, and the only surviving failure mode is the stray-entry one. One `check()`
before the `build()`, recorded as a note, costs nothing.

**F-7 (minor) — `gate.py <row> --preflight` runs the tool.** `argparse.REMAINDER`
starts collecting at the first positional, so any flag *after* the row is
forwarded verbatim and `a.preflight` stays `False`:

```
$ python3 harness-php/gate.py ph00 --preflight
$ .../.temp/php-root/harness/check.py ph00 --preflight
check.py: error: unrecognized arguments: --preflight
record: {'gate_argv': ['ph00','--preflight'], 'verdict': 'tool exited', 'tool_returncode': 2}
```

⚠ **The manager's own 06:55 `ph00.preflight.json` — the one `TASK_PHP_005.md:47`
counts as manager-verified — is exactly this**: `gate_argv ['ph00','--preflight']`,
`verdict 'tool exited'`, `tool_returncode 2`. It is a *failed check.py launch*
recorded as a preflight, not a preflight-only run. Same trap for
`--no-provenance` after the row (which fails safe: provenance still runs), and
for any value-taking flag before it — `--tool measure --reps 31 ph00` makes
`row = '31'` (`gate.py:383`) and the preflight refuses. All loud; none silent
except this one.

**F-8 (minor) — false positive on a mention.** `ph56-mention`, whose `c/kernel.c`
contains only the comment *"this row allocates nothing and deliberately does NOT
include emalloc_shim.h"*, is **refused**, with:

```
allocator: ph56-mention: c/kernel.c include(s) emalloc_shim.h and ph56-mention/c/emalloc_shim.h IS ABSENT.
```

`PLAN_PHP.md` §4.3 and `emalloc_shim.h:6-9` tell a non-allocating row to *say why
it does not link the shim*; if that sentence lands in a `c/` file the row is
blocked, the message asserts an include that does not exist, and the offered fix
is to symlink an allocator the row never uses — which then pins it into both
digests and earns the "orphan" note. Cheap fix: require the string inside an
`#include` on the same line.

**F-12 (minor) — `TASK_PHP_005.md:51`'s own citation.** Checked the way §0 asked:

```
$ grep -rn 'ZEND_SIGNED_MULTIPLY_LONG' php-5.0.0/     (pristine, sha256 5783e0c0...)
Zend/zend_multiply.h:24    #define ... (the __i386__ arm)
Zend/zend_multiply.h:36    #define ... (the #else arm)
Zend/zend_alloc.c:234      ZEND_SIGNED_MULTIPLY_LONG(nmemb, size, lval, dval, use_dval);
Zend/zend_operators.c:831  ZEND_SIGNED_MULTIPLY_LONG(op1->value.lval,op2->value.lval, ...);
$ sed -n '295p' Zend/zend_alloc.c
	int final_size = size*nmemb;
```

**The substance is earned — there are exactly two call sites** — but the row's
main text cites `zend_alloc.c:295`, which is `_ecalloc`'s T3 truncation, a
*different* mechanism; only the dagger has `:234`. The citation and the story
about it are two different claims, and here the citation is the wrong one.

---

# Clean negatives — nine attacks that did NOT land

Named so the next agent does not re-run them.

1. **§1.1 indirection through a `c/` header — the guard HOLDS.** `c/kernel.c ->
   c/row_alloc.h -> emalloc_shim.h` is detected, because `row_alloc.h` is itself a
   `c/*` file and the audit reads every one of them. It is also in both digests.
2. **§1.3 `extern` with no `#include` — structurally impossible.** Every shim
   entry point is `static inline` (`emalloc_shim.h:263,297,346,404,488,515,528,575,
   591,601,612`), so there is no external symbol anywhere to link against:
   `undefined reference to 'php_shim_emalloc'`. There is no way to reach the
   allocator except by including something.
3. **§1.4 the Rust rungs — unreachable, and this was the manager's top
   suspicion.** `build.py:172-175 build_rust` is `rustc <one .rs> -o out` and
   `build.py:162-167 build_c` compiles exactly three fixed TUs, so no Rust rung
   can link a C object without a `harness/build.py` edit. The audit's blindness to
   `*.rs` is real and currently unreachable; note that `*.rs` **is** in both
   digests anyway (`check.py:10313`, `measure.py:225`), so a Rust-side allocator
   model would be pinned.
4. **§2.1 negative operands** — 10 M signed samples, control fires 21 170, shim 0.
5. **§2.2 `dval`** — bit-exact on 45 M+ samples, 0.
6. **§2.3 the directed region** — 28 900 targeted cases + 20 M straddling
   `LONG_MAX`, control fires 414 and 3 692, shim 0.
7. **§3 M5's floor is not too HIGH.** A realistic `verbatim` lift of
   `mul_function` — `ZEND_API`, `TSRMLS_DC`, the two
   `zendi_convert_scalar_to_number` macros and `zend_error(E_ERROR,…)` all removed
   because none of them is extractable — scores **68 %**, comfortably over the
   50 % floor. I could not build a plausible `verbatim` row that scored under it.
8. **§4's byte count** — the manager's withdrawal is supported and the residue is
   a single `'.'`; the 200 is exact.
9. **§5's protective claims** — PAT tree byte-identical over 2 966 paths with a
   fired positive control; `66/0` and `2/0` at both ends; `git status` empty.

---

# What I refute (reconciliation is the manager's job)

**Launched from 9.** Three refutations, two against the **engineer** and one
against the **manager**:

1. ⚠ **`RECAP_PHP.md:58-59` "B1 CLOSED" is refuted** (F-1). Two constructed rows
   put a live allocator in neither digest with the preflight green.
2. ⚠ **`TASK_PHP_004_REPORT.md:494-499`'s Problem 1 is refuted** (F-3):
   `clang -O3 -flto` **does** link here, with the `-fuse-ld=lld` that
   `build.py:169-172` inserts for exactly that cell. The disclosed limitation does
   not exist, and the three unrun cells are now run: 0/20 M, control firing.
3. ⚠ **`.gitignore:24-26`'s stated churn is half wrong** (F-2c): `when` moves,
   `gate_argv` does not. The rest of the record is byte-identical across runs
   (`d91ce008ad273b36` twice), so the split the manager asked for in §4.2 exists
   and costs one field.

A fourth, softer: **`RECAP_PHP.md:30-31`'s repaired size rule is still
unsatisfiable** (F-5) — 30 of 33 rows break it and nothing enforces it.

---

# Evidence index — `.temp/php5/`

| file | what |
|---|---|
| `snapshot.py` | the PAT-tree byte snapshot **and its positive control** (`control` subcommand) |
| `pat-snapshot.json` | 2 966 paths, taken first, re-checked last |
| `b1_bypass.py` | §1 — eight fixture rows, the audit, both digests, `gcc -MM` |
| `buildtest.sh` | §1 — do the bypass rows LINK and allocate (`alloc tally = 7688571`) |
| `mul_probe2.c` / `.sh` | §2 — negatives, zero crossings, bit-exact `dval`, directed, cross-config hash |
| `mul_probe_missing.sh` | §2.5 — the three matrix cells `TASK_PHP_004` never ran |
| `m5_overlap_attack.py` | §3 — the `#if 0` false pass and its must-refuse control |
| `sweep_plant.sh` | §3 — does `--sweep` derive an eighth link (four spellings) |
| `zend_multiply_pristine.h` | regenerated by `.temp/php4/extract_pristine.sh` (tarball sha256 checked) |
| `00-…10-*.log` | every run above, verbatim |
| `preflight-backup/` | the `results-php/preflight/` state I found, restored afterwards |

All binaries deleted; every generator kept and re-runnable.
