# TASK_PHP_004 — landing `TASK_PHP_003`'s corrections — ENGINEER REPORT

**Role:** research engineer. **Launched from a running count of 8**; this task
refutes **one more** figure (below) and reconciliation is the manager's job.

> **No-touch disclosure.** Nothing under `harness/`, `common/`, `patterns/`,
> `results/` or `pilot/` was added, edited or deleted.
> `git status --porcelain -- patterns results harness common pilot` is **empty**
> at the end of the task, and the bracket held:
>
> ```
> python3 harness/measure.py --check-stale     (FIRST command of the task)
>   66 record(s) examined, 0 STALE
> python3 harness/measure.py --check-stale     (LAST command of the task)
>   66 record(s) examined, 0 STALE
> ```
>
> The php side is green too — `python3 harness-php/gate.py --tool measure
> --check-stale` → **`2 record(s) examined, 0 STALE`**.

**Everything below was run.** One script rebuilds all of it:
`sh .temp/php4/REBUILD.sh` (exit 0; log `.temp/php4/REBUILD.log`). Generators
kept, binaries deleted.

---

## Did

### The two blockers

| | what landed | must-fire negative |
|---|---|---|
| **B1** | `harness-php/gate.py::shim_link_audit`, wired into the preflight before every tool | `.temp/php4/b1_symlink_test.py` — 9 checks, 3 constructed refusals + a planted row under `patterns-php/` |
| **B2** | `common-php/emalloc_shim.h`'s `PHP_SHIM_SIGNED_MULTIPLY_LONG` + a faithful `php_shim_safe_emalloc` | `.temp/php4/mul_probe.c` — 20 M samples × 8 build configs, with the refuted spelling as the control |

### The majors (task §2)

| item | file | what |
|---|---|---|
| 3 (`M2`) | `harness-php/root.py` | deleted the four-name whitelist in `sweep()`; per-link negative `.temp/php4/m2_sweep_test.py` |
| 4 (`M5`) | `harness-php/provenance.py` | out-of-range / past-EOF / whitespace spans rejected; a **kernel-overlap** check added; `PLAN_PHP.md` §6 and `PROTOCOL_PHP.md` §D reworded to what it actually checks |
| 5 (`M6`) | `harness-php/gate.py` | `results-php/preflight/<row>.preflight.json` records the `harness-php/*.py` hashes, the manifest hash and whether `--no-provenance` was used; `MANIFEST.sha256` is now verified in the preflight |
| 6 (`M4`) | `ph00-smoke/README.md`, `PROTOCOL_PHP.md` §E, `gate.py` docstring | three → **six** commands, in all three places, headers included |
| 7 (`M3`) | `SOURCES.md` §3, `PLAN_PHP.md` §1, `emalloc_shim.h` | the tree-set settled and enumerated; the `REAL_SIZE` mechanism replaced with the measured one |

### The minors

`m1` `RECAP_PHP.md` START HERE box + the duplicate `infrastructure` row ·
`m2` 11 004 → **11 003** (re-measured against `check.py`'s own pin) ·
`m3` `root.py`'s option-A rationale replaced with the reasons that hold ·
`m4` `php_shim_tally`'s doc comment (`bytes_requested_low` → `bytes_mallocked`) ·
`m5` `digest_bridge.py` now **refuses** a symlinked subdirectory instead of
being blind to it · `m6` `php_shim_shutdown()` added and the live-list hazard
documented · `m7` the rule-6 disclosure table now shows three states.

### Also (not asked for, free at the margin, disclosed)

`M1`'s uncorrected figures still sat in `ph00-smoke/README.md:37` and
`NOTES.md:116`. They are in the gate digest and the row was being re-gated
anyway, so they were fixed — **and re-measuring them refuted the reviewer.**
See *What I refute*.

---

## Evidence

### B1 — the symlink is now a check, and it fires

**Premise verified first, as §5 asked** (the manager assumed on the reviewer's
word that no harness edit was needed):

```
$ grep -rn 'emalloc_shim\|common-php\|patterns-php' harness/*.py common/*.py
(no output)
```

`harness/` and `common/` contain **zero** references to the php tree, so the
preflight in `harness-php/gate.py` is not merely *a* lever, it is the **only**
one. No harness edit; no 33-pattern re-gate. `check.py` globs `pdir/c/*` at
`:10189` and `:10314` and `measure.py::measurement_sources` globs `pdir/c/*`
too, which is what makes the symlink land in both digests.

`.temp/php4/b1_symlink_test.py`, seven fixture rows under `.temp/php4/`
(`patterns-php/` untouched for this half):

```
  --- problems ---
      allocator: ph90-noLink: c/kernel.c include(s) emalloc_shim.h and ph90-noLink/c/emalloc_shim.h IS ABSENT.
      allocator: ph91-copy: ph91-copy/c/emalloc_shim.h is a REGULAR FILE, not a symlink. ...
      allocator: ph92-wrongTarget: ph92-wrongTarget/c/emalloc_shim.h -> '../../../common-php/decoy.h' resolves to ...
  --- notes ---
      ph93-goodLink: c/emalloc_shim.h OK -- symlink, in BOTH digests, used by kernel.c
      ph94-absLink: ... resolves correctly but is not the canonical '../../../common-php/emalloc_shim.h'
      ph96-orphanLink: carries c/emalloc_shim.h but no c/ source mentions it -- harmless, but ...

  ok   ph90 (includes shim, NO link)  is REFUSED
  ok   ph91 (includes shim, REGULAR-FILE copy)  is REFUSED
  ok   ph92 (includes shim, symlink to a DECOY)  is REFUSED
  ok   ph93 (includes shim, canonical symlink)  PASSES
  ok   ph94 (includes shim, ABSOLUTE symlink)  passes with a note
  ok   ph95 (no shim, no link)  PASSES, no false positive
  ok   ph96 (link but nothing uses it)  passes with a note
  ok   exactly THREE rows refused    ['ph90-noLink', 'ph91-copy', 'ph92-wrongTarget']
  ok   common-php/emalloc_shim.h ABSENT  is REFUSED
```

The defect itself, reproduced, and the fix, in the same run:

```
=== B1: the PREMISE -- does the symlink really land in BOTH digests? ===
  ph93-goodLink    c/* -> ['emalloc_shim.h', 'kernel.c', 'main.c']
  ok   ph93-goodLink: allocator IS in the c/* digest        want 59b146689d42, got 59b146689d42
  ph90-noLink      c/* -> ['kernel.c', 'main.c']
  ok   ph90-noLink: allocator is NOT in the c/* digest      want 59b146689d42, got None   <- this is the B1 defect, reproduced
```

End to end, with a real row planted under `patterns-php/` and removed in a
`finally:`:

```
=== B1: END TO END -- a planted row under patterns-php/ blocks the tool ===
  preflight
    ok   shim /home/apt/repos_common/sec-ladder/.temp/php-root
    ok   common-php/ digest bridge
    FAIL <row>/c/emalloc_shim.h symlink (PROTOCOL_PHP.md §B2)
    ok   patterns-php/MANIFEST.sha256
    ok   provenance ph00

  PREFLIGHT FAILED -- the tool was NOT run:
    allocator: zzz-b1probe: c/kernel.c include(s) emalloc_shim.h and zzz-b1probe/c/emalloc_shim.h IS ABSENT.
         It BUILDS anyway (-I common-php), and that is the whole problem: the allocator then sits in
         NEITHER the gate digest nor the MEASUREMENT digest, so a later shim fix leaves this row's Ir
         numbers FRESH for ever under an allocator that no longer exists.
         Fix:  ln -s ../../../common-php/emalloc_shim.h patterns-php/zzz-b1probe/c/emalloc_shim.h

  ok   planted row -> gate.py --preflight exits 2           rc=2
  ok   planted row -> 'the tool was NOT run'
  ok   planted row -> names the row and the fix
  ok   preflight RECORD written and says allocator_symlink_ok=false results-php/preflight/ph00.preflight.json
  with the link:  ok   <row>/c/emalloc_shim.h symlink (PROTOCOL_PHP.md §B2)
  ok   with the link -> the allocator stage is ok
  ok   with the link -> zzz-b1probe no longer a problem
  ok   patterns-php/ restored: git status unchanged
  ok   planted row really gone
0 FAILED
```

⚠ **Design choice worth a reviewer's attention:** the audit runs over **every**
row on every invocation, not just the named one, and a **regular-file copy is
refused**. The copy would be hashed under the same key and look identical in
the record while holding a different allocator; only a symlink makes "the row's
allocator" and "the programme's allocator" the same bytes by construction. An
**orphan** link (present, unused) is a note and not a failure — deliberately, so
the check cannot block a row for something harmless.

### B2 — the overflow predicate

The pristine macro is **never retyped**: `.temp/php4/extract_pristine.sh` cuts
`zend_multiply.h:20-47` out of the pinned tarball (sha256 checked before it
writes) into a header the probe includes, `#if`/`#else` intact, so the probe
selects the same arm a real PHP build would.

**Before the fix** — the probe reproduces `TASK_PHP_003`'s number *exactly*, on
every build configuration, which is what establishes that my sample space is
theirs (same xorshift seed `88172645463325252`, same `1 + rnd()%62` draw, same
20 M):

```
### gcc-O0 / gcc-O3 / gcc-O3-lto / clang-O0 / clang-O3
   DISAGREEMENTS                         : 84523        (shim vs pristine ref)
   CONTROL DISAGREEMENTS (must be > 0)   : 84523  FIRED
```

**After the fix**, same probe, same command:

```
### gcc-O0
   agree                                 : 20000000
   DISAGREEMENTS                         : 0
   CONTROL DISAGREEMENTS (must be > 0)   : 84523  FIRED
### gcc-O3 / gcc-O3-lto / clang-O0 / clang-O3      -- identical
--- NOT used by harness/build.py; run to bound the claim ---
### gcc-O3-native / gcc-O3-ffast / gcc-O3-x87      -- identical
```

Full run at the harness's own flags:

```
=== mul_probe ===
shim predicate under test: PHP_SHIM_SIGNED_MULTIPLY_LONG (post-fix)
__i386__ defined here? no  (so PHP uses the GENERIC double-heuristic arm)
compiler: gcc 13.3.0   FLT_EVAL_METHOD=0   __FP_FAST_FMA=no
samples: 20000000

-- shim vs pristine ref (the claim under test) --
   agree                                 : 20000000
   ref says overflow, shim says fine     : 0
   shim says overflow, ref says fine     : 0
   lval differs where both say 'fine'    : 0
   DISAGREEMENTS                         : 0

-- MUST-FIRE CONTROL: __builtin_mul_overflow vs pristine ref --
   ref says overflow, builtin says fine  : 84523
   builtin says overflow, ref says fine  : 0
   CONTROL DISAGREEMENTS (must be > 0)   : 84523  FIRED

-- operand-type spelling: macro on `long` vs on `size_t` --
   verdict differs                       : 0

-- function level: php_shim_safe_emalloc vs zend_alloc.c:221-244 --
   nmemb                  size         ref      shim
   8                      8            1        1        benign
   2147483648             4            1        1        4 GiB, no overflow
   9007199254740993       3            0        0        TASK_PHP_003 case
   9007199254740993       5            0        0        TASK_PHP_003 case
   9007199254740995       7            0        0        TASK_PHP_003 case
   61170688267664500      12           0        0        TASK_PHP_003 first random disagreement
   4611686018427387904    4            0        0        true overflow
   9223372036854775807    2            0        0        true overflow
   3                      10           1        1        safe_emalloc(3, len, 1) -- ext/standard/url.c:499 shape
   0                      0            1        1        zero
   9223372036854775807    1            0        0        nmemb == LONG_MAX: guard REFUSES
   1                      1            0        0        offset == LONG_MAX: guard REFUSES
   fixed + 200000 random cases = 200012;  DISAGREEMENTS: 0

VERDICT: IDENTICAL   (macro 0 + lval 0 + function 0)
```

Three things about that probe that decide whether it means anything:

1. **The control is the refuted spelling itself.** If the probe reported 0 for
   `__builtin_mul_overflow` it would be a probe that cannot see a divergence.
   It reports 84 523 in **every** configuration.
2. **The function level distinguishes "took the `E_ERROR` path" from "reached
   the allocator and `malloc` failed"** — both return `NULL`, and conflating
   them would make the test unable to fail. It reads `php_shim_ag.n_alloc`.
   `TASK_PHP_003`'s three hand-picked disagreements and its first *random* one
   (`61170688267664500 * 12`) now all take PHP's `E_ERROR` path.
3. **`lval` is compared too**, not only the boolean, on every sample where both
   say "fine": 0 differences.

⚠ **Fidelity is more than the predicate.** The rewrite also corrects two
operand-type deviations the old spelling had. `_safe_emalloc` passes `size_t`
to the macro at `:234`, so `long __lres = (a)*(b)` is a **wrapping unsigned**
multiply narrowed to `long`; the old code did `long a = (long)nmemb` first,
which is **signed overflow, i.e. UB, at exactly the inputs the row is about**.
Likewise `:237`'s `LONG_MAX - offset` and `:238`'s `lval + offset` are `size_t`
arithmetic in the original and were signed here.

The pre-existing allocator probe still passes with the new predicate,
**including the arm that exercises the guard**:

```
SE  zend_alloc.c:221-244 -- `_safe_emalloc` protects against neither
  ok   a) 4 GiB passes the 64-bit guard, then truncates safe_emalloc(0x20000000, 8, 0) = 4 GiB, real_size 0
  ok   CONTROL: a true 64-bit overflow IS refused     safe_emalloc returned NULL as PHP's E_ERROR path does
16 checks, 0 FAILED
```

### M2 — the sweep, before and after, measured here

I did not take `4 of 7` on trust; `.temp/php4/m2_sweep_before.py` runs the
per-link negative against `git show HEAD:harness-php/root.py`:

```
PRE-FIX : 4 of 7 links the sweep CANNOT see: ['harness', 'common', 'patterns', 'results']
POST-FIX: 0 link(s) whose deletion the sweep CANNOT see
          (baseline, intact map: rc=0, no gaps -- so the check is not just always-red)
```

### M5 — the provenance validator

`.temp/php4/m5_prov_test.py`, 15 fixtures under `.temp/php4/`:

```
=== the two gaps TASK_PHP_003 found (both used to ACCEPT) ===
  ok   r11 span BEYOND end of file is REJECTED
  ok   r10 c_file names a DIFFERENT file (hash recomputed) is REJECTED
       r10-wrong-file: OK  Zend/zend_hash.c:1-20  1286 bytes  sha256 97c59b936f5aea61  tier=verbatim
       r10-wrong-file: kernel overlap 0% (0/12 excerpt lines in kernel.c)  floor 50% for tier=verbatim
       r10-wrong-file: KERNEL DOES NOT MATCH THE CITATION. ...
=== new negatives around the same two ===
  ok   r12 span RUNS PAST the end is REJECTED
  ok   r13 whitespace-only span (38,39) is REJECTED
  ok   r14 provenance with NO kernel source is REJECTED
  ok   r15 verbatim tier + UNRELATED kernel is REJECTED
=== positives: the check must NOT fire on a correct row ===
  ok   r16 verbatim row whose kernel IS the excerpt is ACCEPTED   overlap 100% (16/16)
  ok   r17 narrowed row (wrapper removed) is ACCEPTED             overlap  94% (15/16)
  ok   r18 modelled row: overlap REPORTED, no floor, ACCEPTED     overlap   0%
=== regression: TASK_PHP_002's negatives still fire ===
  ok   off-by-one at the start / at the end / wrong tarball_sha256 / non-canonical extract_cmd  -- all REJECTED
=== the real row is unaffected ===
  ok   provenance.py --all still exits 0
0 FAILED
```

⚠ **The kernel check is a heuristic and is labelled as one everywhere it
appears** — line overlap after dropping blanks, braces, comments and
preprocessor lines, floored at 50 % (`verbatim`) / 25 % (`narrowed`), with
`modelled` reported and not floored. It catches *"the citation names a different
file"*; it cannot prove an extraction. The measured percentage is printed on
every run so a reader can judge it rather than trust the boolean.

### M6 / m5 — traces and the bridge

`--no-provenance` now leaves a trace, and the thing it was invisible in still
is:

```
$ python3 harness-php/gate.py --preflight --no-provenance ph00
  !!   provenance SKIPPED for ph00 (--no-provenance). This run certifies nothing about where the kernel came from.
  -> results-php/preflight/ph00.preflight.json
     provenance_checked: False  provenance_skipped: True  gate_argv: ['--preflight', '--no-provenance', 'ph00']
$ (the GATE record's own field, unchanged and still blind)
     gate record invocation field: ph00
```

`.temp/php4/m5b_bridge_test.py` — the third row is the one that used to print
`digest bridge: current`:

```
  ok   baseline bridge is current
  ok   a new top-level .h: REFUSED               rc=1  NOT BRIDGED: zzz_probe.h is in no digest at all
  ok   a file in a REAL subdirectory: REFUSED    rc=1  NOT BRIDGED: zzz_sub/payload.h is in no digest at all
  ok   a file behind a SYMLINKED dir: REFUSED    rc=1  SYMLINKED DIRECTORY: zzz_symdir/ -- `os.walk` does not follow it ...
  ok   bridge is current again after every plant is removed
  ok   common-php/ byte-identical to baseline
0 FAILED
```

⚠ I chose **refuse** over `os.walk(followlinks=True)`: `common-php/` is a
directory of *file* symlinks into `common/`, so a directory symlink aimed back
at `common/` or `patterns/` would silently pull the PAT tree into the php bridge
table and make every `--regen` a cross-programme diff.

### M3 / §2.7 — the tree set, settled

```
$ find /home/apt/repos_common -path '*/php-5.0.0/Zend/zend_alloc.c' | wc -l
12
$ find /home/apt/repos_common -path '*/Zend/zend_alloc.c' -not -path '*/php-5.0.0/*'
./php-in-safe-rust/build/php-4.0.2/Zend/zend_alloc.c
```

pristine `zend_alloc.c` sha256 `fb4215f19dc2e68c…`; **8 of the 12 match it
byte for byte**, including all three `.app-tests/.temp/oracle/` trees that
`SOURCES.md` named as *"modern-gcc **and allocator**"* patched.

| n | hash | tree(s) | patch |
|--:|---|---|---|
| 8 | `fb4215f19dc2e68c` | 3 × `.app-tests/…oracle/build-5.0.0-mysql-webext*`, 3 × `.trash/temp-20260805-0920/build-5.0.0*`, `…-maxlto-asan`, `…-maxlto-hardened` | **none** |
| 2 | `d6245088682d2e00` | `…-maxlto-nocache`, `…-maxlto-nocache-asan` | `ZEND_DISABLE_MEMORY_CACHE 0 → 1` at `:40` and `:43` |
| 1 | `74a20877c68d1ff4` | `…-maxlto-nocache-detect-asan` | the above **plus** `REAL_SIZE(size) → (size)` at **`:132`** |
| 1 | `b817edb91015b918` | `…-maxlto-poison-asan` | `ASAN_{,UN}POISON_MEMORY_REGION` at `:35-41`, `:162`, `:284` |

**The `7 of 12` / `8 of 13` disagreement is a SCOPE disagreement, not a content
one.** There are 12 `php-5.0.0` trees and a 13th `zend_alloc.c` belonging to
`php-4.0.2`, which cannot be byte-identical to a 5.0.0 tarball. The manager's
**8** and **13** are each right about a different set; the reviewer's **12** is
right and their **7** is one short (their own listing accounts for 11 rows).

And the patch does **not** delete the truncation
(`.temp/php4/real_size_probe.c`):

```
requested size_t       pristine u32   patched u32    same?   case
18446744071562067968   2147483648     2147483648     YES     emalloc_probe.c:61's 18.45 EB request
18446744073709551615   0              4294967295     no      SIZE_MAX -- NOT the probe's value
4294967320             24             24             YES     4 GiB + 24
```

⚠ The reviewer wrote *"for the 18-EB probe the two spellings give the same
`real_size`"*. **That is correct for the value the probe actually uses**
(`0xFFFFFFFF80000000`) and **not general** — at `SIZE_MAX` they differ, and both
still truncate. The conclusion holds either way: `real_size` is `unsigned int`
and the **store** at `:129`/`:135` is the truncation.

### m6 — the live-list leak, with its must-fire half

`.temp/php4/shutdown_probe.c`, 20 000 "kernel calls" each leaking 64 × 4096 B:

```
arm B  shutdown()+reset()  : RSS 1448 -> 1900 KiB      (+452)      head=NULL
arm A  reset() only        : RSS 1900 -> 5161776 KiB   (+5159876)  head=NULL
MUST-FIRE (arm A climbs by > 1 MiB)  : FIRED
FIX      (arm B climbs by < 1/8 of A): OK
```

`php_shim_shutdown()` is `zend_alloc.c:469-569` projected onto the
`!ZEND_DEBUG && !ZEND_MM` arm, **including PHP's `for (i=1; …)`** — cache class
0 is never returned to `malloc` by shutdown, and that is reproduced rather than
"fixed". ⚠ `php_shim_reset()` deliberately still does **not** free the live
list: a kernel may hold a pointer across the reset, and freeing it there would
manufacture a use-after-free — `PLAN_PHP.md` §4.2's invented-defect failure.

### m2 — re-measured rather than taken on trust

```
check.py NAMED_SPELLING_LEN pin : 11003
measured paragraph len          : 11003     sha256[:12] 59748cce2db5
total why chars / words         : 12224 2056
row-specific prefix chars/words : 1220 200
```

The reviewer is right; `RECAP_PHP.md:17`'s 11 004 was wrong.

### The gate, twice, and what moved

Two full gates were run (the second because the M1 correction below moved two
hashed docs). Both:

```
check.py: PASS-WITH-BLOCKED-ROWS          (identical to the committed verdict)
== 9c.  ok  results/tables/ph00-smoke.md is byte-identical to a fresh render (6e772aadbbbd)
```

Stage 9c passing byte-identically means **no `report.py` re-render and no third
gate were owed** — the `gate → report → gate` chain does not fire for a
doc-only change here.

Gate-record diff, `git show HEAD:` vs the first re-gate, **6 of 1079 leaf values
moved**:

```
.source_sha256.common/digest_bridge.py        8f693aa5… -> c5321600…
.source_sha256.patterns/ph00-smoke/NOTES.md   5e61f554… -> 47df4477…
.source_sha256.patterns/ph00-smoke/README.md  f56e3def… -> 18a9418f…
.marginal_ir_env.bytes                        3294 -> 3303
.marginal_ir_env.envp_stack_bytes             3686 -> 3695
.miri.runs[1].seconds                         0.2 -> 0.1
verdict:  PASS-WITH-BLOCKED-ROWS -> PASS-WITH-BLOCKED-ROWS
contract: 91d88e1e18b1 -> 91d88e1e18b1      (spec.md untouched)
```

Exactly the three files I edited that are in the gate digest, plus two
environment terms and one wall-clock. **Zero `Ir`, zero checksum, zero
identity.** `common-php/emalloc_shim.h` is not among them because `ph00` does
not link the allocator — its content is pinned through `digest_bridge.py`,
whose hash *is* there, which is the bridge doing its job.

---

## What I refute (reconciliation is the manager's job)

**Launched from 8.** One new refutation, and it is against the **reviewer**:

⚠ **`TASK_PHP_003` M1's *"`envp_stack_bytes` is +33, caused by `gate.py`'s
`PYTHONDONTWRITEBYTECODE=1`"* attributes the right mechanism and the wrong
magnitude — and the magnitude is not a constant at all.** Measured directly,
same shell, the variable added and removed (`.temp/php4/m1_env_test.py`):

```
                         bytes  nvars  envp_stack_bytes
without the var           3279     48              3663
with    the var           3305     49              3697
DELTA                      +26     +1              +34
len('PYTHONDONTWRITEBYTECODE=1') + NUL + one 8-byte envp slot = 25 + 1 + 8 = 34
```

**The variable costs exactly +34 and +1 var.** The `+33` was a *record-to-record*
difference between two runs taken in two different shells — the 34 plus a
residue that is not constant:

| record | `repo_path_bytes` | `envp_stack_bytes` | `nvars` |
|---|--:|--:|--:|
| `p01`, committed | 33 | 3653 | 48 |
| `ph00`, the record `TASK_PHP_003` measured | 48 | 3686 | 49 |
| `ph00`, re-gated here | 48 | **3695** | 49 |

⚠⚠ **`ph00`'s own `envp_stack_bytes` moved 9 bytes between two runs of the same
gate on the same box with no source change**, so the p01→ph00 delta was +33 and
is now +42. **This strengthens the reviewer's conclusion rather than weakening
it**: not only is no php marginal `Ir` comparable to any PAT one, **two php runs
are not comparable to each other unless the invoking shell is byte-identical**,
and `repo_path_bytes` (+15) is the only one of the three domain terms that is a
property of the tree rather than of whoever typed the command. Landed in
`README.md`, `NOTES.md` and `RECAP_PHP.md` open item 9.

Two smaller corrections to the review, both minor and both in its favour
overall:

- **`7 of 12` pristine trees is 8 of 12** (above). The `12`/`13` half is a scope
  difference, not an error by either party.
- **"for the 18-EB probe the two `REAL_SIZE` spellings give the same
  `real_size`"** is true for the probe's value and not in general.

Everything else in the review I reproduced and landed as written.

---

## Problems

1. **`clang -O3 -flto` cannot link on this box** — `LLVMgold.so` is absent from
   `~/tools/llvm-22.1.6/lib/`. That configuration is therefore *not* in the
   B2 evidence (7 of 8 ran; `harness/build.py` does have a `-flto` clang path,
   guarded by `-fuse-ld=lld`, which my standalone probe does not use). The
   `clang -O3` and `gcc -O3 -flto` arms both report 0, so I do not think it
   changes anything, but I did not run it and I am not claiming it.
2. **`results-php/preflight/` is untracked and I did not decide its fate.** It
   is written on *every* `gate.py` invocation and carries a timestamp, so
   committing it means it churns on every run — like the gate records, but with
   no verdict to justify it. **The manager should decide: commit, or add to
   `.gitignore`.** I left it untracked rather than choosing.
3. **Two gates, ~24 min each, because I corrected M1 after the first one.** The
   protocol's own cost table would have predicted this; I did not batch the
   doc fixes tightly enough, and the second gate was avoidable had I re-measured
   `envp_stack_bytes` before writing it down. Nothing was lost but time.
4. The `-Walloc-size-larger-than` warning from `common-php/emalloc_probe.c:48`
   is **pre-existing** (it is the honest-allocation control asking for 18 EB)
   and is not mine.

---

## Unsure / not done

1. ⚠ **§5's question — is bit-exact reproduction of the double heuristic
   achievable? On this box, measured, YES; but the probe's residual weakness is
   not the one the manager named.** `FLT_EVAL_METHOD=0`, `__FP_FAST_FMA`
   undefined (no FMA in the x86-64 baseline `harness/build.py` targets), and the
   count stayed **0** under `-march=native`, `-ffast-math` **and**
   `-mfpmath=387` — the three things §5 worried about. So x87 excess precision,
   FMA contraction and fast-math do **not** move it here.

   **The residual gap is different and I want it on the record: `ref` and `shim`
   are compiled in the SAME translation unit with the SAME flags, so a shared
   miscompilation is invisible to the comparison.** The independent anchor
   against that is the control: under `-ffast-math` the heuristic *still*
   disagrees with the exact builtin 84 523 times, so it was demonstrably not
   collapsed into an exact test. **I have not compared against a real compiled
   PHP 5.0.0 binary**, which is the only test that would close it completely.

   ⚠ **I did NOT put a residual-disagreement figure in `spec.md`, because there
   is no disagreement to state and no php row has a `spec.md` yet.** If the
   manager wants the limitation pinned rather than documented, the place for it
   is the first allocating row's `provenance.deletions` — say so and I will
   write it there. What I did instead is state the scope in
   `common-php/emalloc_shim.h` (the compilers and flags the 0 covers) and in
   `RECAP_PHP.md` F6 (the same-TU caveat, in terms).

2. **The kernel-overlap check has never seen a real php row.** Its thresholds
   (50 / 25 / none) are my judgement, calibrated on two fixtures — a verbatim
   lift scores 100 %, a realistic `narrowed` lift with the wrapper removed
   scores 94 %. **The first row that trips a floor should be judged by a human,
   not auto-retiered to `modelled`.** Carried as `RECAP_PHP.md` open item 14.

3. **`harness-php/*.py` is still in no digest**, and I did not change that —
   it needs `check.py`'s `srcs` to reach `harness-php/`, i.e. a `harness/` edit
   and a 33-pattern re-gate. §2.5 said *"fix the trace at minimum; say what the
   digest costs"*, so I landed the trace and priced the rest. **The trade is the
   manager's** (`RECAP_PHP.md` open item 13). ⚠ The preflight record is
   **evidence, not a pin**: nothing hashes it, so it can prove
   `--no-provenance` *was* used and cannot prove it was not.

4. **I did not re-verify the reviewer's `1169/1170 manifest files identical`
   figure**, nor re-run their `e5`–`e9` experiments. I re-ran only the findings
   I was landing.

5. **`.tasks-php/TASK_PHP_002_REPORT.md:349` still says `repo_path_bytes` is 20
   bytes longer.** I left it: it is a historical report, and rewriting one is a
   different kind of act from correcting a live document. The manager may
   prefer an annotation.

6. **I did not touch `.memory-php/`** — it does not exist, and rules 4 and 9
   make it the manager's after review.

7. **`RECAP_PHP.md` edits.** §3 assigned me `m1` and `m2`, both of which live
   there, so I also updated the START HERE box's B1/B2 lines and open items
   9/10/11 and added 13/14/15 — **marked UNREVIEWED**. If the manager would
   rather own that file entirely, revert those hunks; the substance is all in
   this report.

---

## Memory updates

**None written.** `.memory-php/` does not exist, `.tasks/PROTOCOL.md` rule 4
makes it the manager's, and rule 9 says a finding does not enter the
authoritative layer until it has survived review — this task is engineer work
and is unreviewed.

Durable facts landed in the tree instead, where the gate hashes them:

| where | what |
|---|---|
| `common-php/emalloc_shim.h` | the corrected tree-set + `REAL_SIZE` mechanism; the `#else`-arm macro and why its inaccuracy is the fidelity; the tally's fourth field; the live-list hazard |
| `.tasks-php/PROTOCOL_PHP.md` | §B: the heuristic + *"modelled by an equivalent builtin needs a differential test"*; §B2: the symlink is now enforced; §D: what `extract_sha256` does and does not check; §E: six commands; §E1: the php `--check-stale` |
| `patterns-php/SOURCES.md` §3 | the 12-tree enumeration with each patch |
| `PLAN_PHP.md` §1, §4.3, §6 | the settled tree set; the shim's own invented-defect episode; the provenance checked/not-checked table |
| `harness-php/*.py`, `common-php/digest_bridge.py` | each fix carries the finding that motivated it and the path of its negative |

**Candidates for `.memory-php/`, in priority order:**

1. ⭐ *"Modelled by an equivalent builtin"* is a claim that needs a
   **differential test with a must-fire control**. The shim's original control
   (`a true 64-bit overflow IS refused`) was a real control that exercised only
   the region where the two predicates agree — **a control inside the agreeing
   region proves nothing about the disagreeing one.**
2. ⭐ **A word in a document is not an enforcement mechanism.** "Mandatory"
   appeared in two documents for one task and was checked by nothing. Every
   other "mandatory" in `PROTOCOL_PHP.md` should be read as a to-do.
3. **`envp_stack_bytes` is not stable across sessions** — `ph00`'s moved 9
   bytes between two runs of the same gate. `repo_path_bytes` is the only
   domain term that is a property of the tree. **Never difference two records
   taken in two shells and call the result a mechanism's cost**; measure the
   mechanism.
4. **Reproduce the reviewer's number before fixing what it measures.** The B2
   probe reproducing `84 523` exactly, on the pre-fix tree, is what made the
   post-fix `0` mean something; without it, `0` could have been a different
   sample space.
5. **The php measurement digest reaches `common-php/` only through the
   `<row>/c/` symlink**, and that is now checked in `gate.py`'s preflight.
6. **A php gate record still does not record whether its preflight ran**;
   `results-php/preflight/<row>.preflight.json` is the trace, and it is
   unhashed.
