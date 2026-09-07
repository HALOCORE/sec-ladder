# TASK_PHP_002 — Phase 0: the foundation — ENGINEER REPORT

**Role:** research engineer, working alone. **Launched from a running count of 4.**
Reconciliation is the manager's job, not mine; §7 states what I refuted.

---

## Did

| # | deliverable | path |
|---|---|---|
| 1 | citation base | `patterns-php/SOURCES.md`, `patterns-php/php-5.0.0.manifest` (1170 files, 109,405 B), `patterns-php/manifest.sh`, `patterns-php/MANIFEST.sha256` |
| 2 | the symlink shim | `harness-php/root.py` — builds `.temp/php-root/`, **7 links, not 5** |
| 3 | the driver | `harness-php/gate.py` — preflight + `exec`; reimplements no gate stage |
| 4 | php shared code | `common-php/emalloc_shim.h` (the shim), `common-php/emalloc_shim.c` (probe TU), `common-php/emalloc_probe.c` (the evidence), `common-php/digest_bridge.py`, and symlink re-exports `driver.{c,h,rs}` + `slb.py` |
| 5 | the addendum | `.tasks-php/PROTOCOL_PHP.md` |
| 6 | the provenance validator | `harness-php/provenance.py` |
| 7 | the end-to-end proof | `patterns-php/ph00-smoke/` + `results-php/` |

Scratch and evidence under `.temp/php0/`. No file under `harness/`, `common/`,
`patterns/`, `results/` or `pilot/` was created, edited or deleted (T3).

---

## Evidence

### T1 — `measure.py --check-stale`, before

```
$ python3 harness/measure.py --check-stale
...
66 record(s) examined, 0 STALE
```

Tree clean at `4afcef235eeaf244506899db6172a99a7247ee8f`.

**What would make it fail:** any write into `patterns/*`, `common/*`,
`harness/{build,asm,measure}.py`, `verus_run.py` or a pattern's `inputs/`.
It is the check the whole no-touch rule reduces to.

*(T1-after: §6.)*

### T2 — shim digest fidelity, with a negative

Identity shim at `.temp/php0/probe-root/` (all five links pointing at the
**real** PAT dirs), `check.py::main`'s glob list reproduced verbatim,
compared against the **committed** `results/gate/p01-array-sum.json`:

```
### T2 POSITIVE (abspath, as check.py::main actually does)
   keys 35  identical: True  hashes differ: none
```

**What would make it fail** — and this is a real implementation, not a
hypothetical: if `REPO` or the per-file key used `os.path.realpath` instead of
`os.path.abspath`, every key would resolve out of the shim. Run on the same
sources:

```
### T2 NEGATIVE 1 -- the SAME sources, keyed the way a realpath-based
### harness would key them. This is the implementation T2 rules out.
   keys 35  identical: False
   e.g. ['../../../common/driver.c', '../../../common/driver.h', '../../../common/driver.rs']
```

The check is also sensitive to what the links point at: through the **php**
shim (`common -> common-php`) the eight `common/layout/*.py` keys disappear
and `common/digest_bridge.py` appears — see §3 "the key-set difference".

### T5 — the provenance validator, 2 accept / 10 reject

`.temp/php0/t5_provenance.py`. Fixtures under `.temp/php0/provfix/`; the
validator is driven through `check_row()` so no scratch row is ever created
under `patterns-php/`.

First, the slice is checked against **real `sed`**, because the whole
validator rests on `sed -n 'a,bp'` being 1-based and inclusive:

```
true excerpt sha256 for Zend/zend_alloc.c:142-217 = fa354ce8820e401c4d0de612dc43f6f48d6f5562ec1ecca606a7c0255ca64b72
real `sed -n '142,217p'` gives                = fa354ce8820e401c4d0de612dc43f6f48d6f5562ec1ecca606a7c0255ca64b72
SLICE AGREES WITH sed: True
```

Then, all twelve cases behaved as specified (`12 cases, 0 unexpected`):

| case | verdict |
|---|---|
| the real span `Zend/zend_alloc.c:142-217` (`_emalloc`) | **ACCEPT** |
| `php_provenance=false` with a `why` | **ACCEPT** |
| span off by one at the **end** (`142,218`) | REJECT — `2310 bytes` vs `2309` |
| span off by one at the **start** (`143,217`) | REJECT — `2231 bytes` |
| right span, **one flipped hex digit** in `extract_sha256` | REJECT |
| `extract_cmd` does not describe `c_lines` | REJECT — prints both spellings |
| a **different file**, same span | REJECT |
| `c_file` not in the corpus | REJECT — caught by the manifest, no tarball needed |
| wrong `tarball_sha256` | REJECT |
| `tier` not one of the three | REJECT |
| **no `provenance` object at all** | REJECT |
| `php_provenance=false` with **no `why`** | REJECT |

The last two matter: a row cannot opt out by omission, only by declaring
`php_provenance: false` *and* saying what it is instead.

### T6 — the emalloc shim, 16 checks / 4 positive controls, then ASan

`common-php/emalloc_probe.c`, built plain and under ASan.

```
php-5.0.0 emalloc shim probe -- sizeof(header)=24 padding=0

T1  zend_alloc.c:129/:135 -- `unsigned int real_size`
  ok   a) the 64-bit request truncates to 2 GiB       request 18446744071562067968 B (18.45 EB) -> real_size 2147483648 B (2.00 GiB)
  ok   b) ... and the allocation SUCCEEDS             emalloc returned non-NULL for an 18-EB request
  ok   c) ... and 2 GiB of it is really mapped        wrote and read back byte 0 and byte real_size-1
  ok   CONTROL: without the truncation it FAILS       malloc(18446744071562067968) returned NULL

T2  zend_alloc.h:53 -- `unsigned int size:31`
  ok   a) recorded size is (size & 0x7fffffff) = 0    T1 real_size = 2147483648, T2 recorded size = 0 -- DIFFERENT FIELDS
  ok   b) a 4-GiB request allocates 24 bytes          emalloc(0x100000018 = 4 GiB + 24) -> real_size 24 B
  ok   CONTROL: an in-range size records exactly      emalloc(40) records 40

T3  zend_alloc.c:295 -- `int final_size = size*nmemb`
  ok   a) a 4-GiB ecalloc succeeds with 0 bytes       ecalloc(0x40000000, 4) = 4 GiB requested, final_size = 0
  ok   b) ... and records 0
  ok   CONTROL: ecalloc(8,8) allocates 64 zeroed bytes

SE  zend_alloc.c:221-244 -- `_safe_emalloc` protects against neither
  ok   a) 4 GiB passes the 64-bit guard, then truncates safe_emalloc(0x20000000, 8, 0) = 4 GiB, real_size 0
  ok   CONTROL: a true 64-bit overflow IS refused     safe_emalloc returned NULL as PHP's E_ERROR path does

CA  zend_alloc.c:150-168,:263-279 -- the size-class cache
  ok   a) a freed 24-byte block is CACHED, not freed  n_cache_push=1 n_cache_hit=1 same ptr=yes
  ok   CONTROL: a 96-byte block is NOT cached (index 12 >= 11) real_size 96 -> cache_index 12 >= 11; n_cache_push=0
  ok   b) the LAST cached class is real_size 80 (index 10)
  ok   c) the FIRST uncached class is real_size 88 (index 11)

16 checks, 0 FAILED
```

The four `CONTROL:` lines are the must-fire half. Without them the headline
would be indistinguishable from "this box has generous overcommit": the same
18-EB request through an otherwise identical allocator **with no 32-bit
store** returns `NULL`.

**The ASan half, and the documented trap reproduces exactly.** First, with the
inherited `LD_PRELOAD`:

```
$ .temp/php0/emalloc_probe_asan uaf-plain
==853072==ASan runtime does not come first in initial library list; you should either
link runtime to your application or manually preload it with LD_PRELOAD.
exit=1 (WITH the inherited LD_PRELOAD)
grep AddressSanitizer -> 0
```

**Exit 1, zero reports.** An exit-code check reads that as "the bug fired".
With `env -u LD_PRELOAD`:

```
########## arm: uaf-plain  (env -u LD_PRELOAD) ##########
exit=1  AddressSanitizer lines=2
==853172==ERROR: AddressSanitizer: heap-use-after-free on address 0x50c000000058 ...
    #0 ... in arm_uaf_plain common-php/emalloc_probe.c:300
########## arm: overflow  (env -u LD_PRELOAD) ##########
exit=1  AddressSanitizer lines=2
==853177==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x504000000040 ...
    #2 ... in arm_overflow common-php/emalloc_probe.c:311
########## arm: uaf-cached  (env -u LD_PRELOAD) ##########
exit=0  AddressSanitizer lines=0
uaf-cached: wrote 'X' to a freed block; n_cache_push=1
```

⚠⚠ **The third arm is a finding, not a failure, and it is the strongest
evidence in this task for `PLAN_PHP.md` §4.3 / `RECAP_PHP` F3.** The *same*
use-after-free is **reported on a 96-byte block and SILENT on a 24-byte one**,
because `zend_alloc.c:270-279` puts the small block in the size-class cache
and never calls `free`. ASan is demonstrably not blind — the other two arms
fire on the same binary in the same session. **`crashes_pristine_5_0_0 =
False` is not evidence of absence, and now there is a controlled demonstration
of the mechanism rather than an inference from a percentage.**

### Other must-fire controls run

| control | fired? |
|---|---|
| `root.py --sweep` with `pilot` deleted from `LINKS` | ✅ `⚠ GAP pilot fixture.py:31`, rc=1 |
| `root.py --check` with `common` pointed at `../../common` | ✅ `BAD common: points at '../../common', want '../../common-php'` |
| `root.py --check` with the `pilot` link removed | ✅ `BAD pilot: ABSENT` |
| `manifest.sh` against a decoy tarball | ✅ `TARBALL SHA MISMATCH`, rc=3, manifest on disk unchanged |
| `manifest.sh` against a missing tarball | ✅ `MISSING TARBALL`, rc=2 |
| `digest_bridge.py --verify` after appending 2 lines to `emalloc_shim.h` | ✅ `MOVED: emalloc_shim.h 0d05c94ff579 -> ca6da0cc647c`, rc=1 |
| `gate.py --preflight ph00` with that same drift | ✅ `PREFLIGHT FAILED -- the tool was NOT run` |
| the T3 snapshot instrument (`pat_snapshot.py --selftest`) | ✅ `ADDED ['harness/__pycache__/x.pyc','results/new.json'] CHANGED ['harness/x.py']` |


---

## The sweep — §4 claim 1, and what the five-link list was missing

I re-derived the link list from the harness sources rather than from the four
modules' constants. `python3 harness-php/root.py --sweep` does it
reproducibly, so the answer ages with the harness instead of with a docstring:

```
first path component off the harness's repo root, from a source sweep
(9 modules; the link map has 7 entries)

  LINKED   .temp            asm.py:823, build.py:50, check.py:10531, check.py:10661, check.py:3722, check.py:4492
  LINKED   common           build.py:48, check.py:10190, check.py:10317, check.py:10322, check.py:10323, check.py:213
  LINKED   harness          check.py:10318, check.py:1033, check.py:1034, check.py:1231, check.py:214, fixture.py:26
  LINKED   patterns         build.py:49, report.py:238, report.py:89
  LINKED   pilot            fixture.py:31
  LINKED   results          check.py:10534, check.py:8903, check.py:9128, measure.py:49, report.py:31
  LINKED   verus_run.py     build.py:55, check.py:10324, check.py:5973, fixture.py:56, limbs.py:126, measure.py:106

no gaps: every repo-root-relative component the sweep finds is covered by the link map.
```

⚠ **The first spelling of that sweep printed four FALSE gaps** — `driver.c`,
`gate`, `tables`, `p*.json` — because it matched `os.path.join(COMMON, …)` and
`os.path.join(RESULTS, …)` as well as `os.path.join(REPO, …)`. Those are
second-level and already covered. Fixed and stated here rather than quietly,
because a sweep that cries wolf is one the next agent switches off.

### The full REPO-relative inventory, and where each lands

| construct | sites | under the shim | verdict |
|---|---|---|---|
| `REPO/harness` | `check.py::module-level sys.path setup,1033,1034,1231,10318`, `fixture.py:26`, `limbs.py:66` | the real, unmodified harness | ✅ link 1 |
| `REPO/common` | `build.py:48,163,167`, `check.py::module-level sys.path setup,6115,8312,8314,10190,10317,10322,10323` | `common-php/` | ✅ link 2 |
| `REPO/patterns` | `build.py:49,83-89`, `report.py:89,238` | `patterns-php/` | ✅ link 3 |
| `REPO/results` | `check.py::check_published_tables,9128,10534`, `measure.py:49,575`, `report.py:31,32,207,726` | `results-php/` | ✅ link 4 |
| `REPO/verus_run.py` | `build.py:55`, `check.py::_verus,10324`, `measure.py:106,235`, `fixture.py:56`, `limbs.py:126` | the real one, read-only | ✅ link 5 |
| **`REPO/pilot`** | **`fixture.py:31`**, reached from **`check.py::check_selftests`** | **MISSING → stage 0 FAILS** | ❌ **GAP 1** |
| **`REPO/.temp/…`** | `build.py:50`, `check.py::check_marginal_ir,4492,6110,8298,9809,10531,10661`, `measure.py:449`, `fixture.py:30`, `asm.py:822`, `dloop.py:744` | **nests under the shim** | ⚠ **GAP 2** |
| `git -C REPO` | `measure.py:129,130` | the shim is inside the worktree | ✅ works, verified |
| `cwd=REPO` for children | `build.py:195`, `check.py::_dep_info_files,5974`, `fixture.py:70`, `limbs.py:127` | the shim; every path passed is absolute | ✅ |

### ⚠⚠ GAP 1 — `pilot`, and it is a HARD FAILURE, not a hash question

`harness/check.py::check_selftests` calls `fixture.ensure()`. `harness/fixture.py:31` sets
`PILOT = REPO/pilot` and compiles six binaries out of it into
`REPO/.temp/build/docrepro/`, which `asm.selftest()` then re-derives every
pinned pilot number from. With no `pilot` link, `REPO/pilot` does not exist.
**Measured, on a shim built without it:**

```
fixture.REPO  = .../.temp/php0/nopilot-root
fixture.PILOT = .../.temp/php0/nopilot-root/pilot  exists: False
--- fixture.ensure() ---
  FAIL k_gcc              0.0s
       | cc1: fatal error: .../nopilot-root/pilot/k.c: No such file or directory
  FAIL k_clang            0.0s
  FAIL k_rust             0.0s
  FAIL k_unsafe           0.0s
  FAIL k_verus            0.1s
  FAIL k_unsafe_verus     0.1s
ensure() -> False
```

`check.py::check_selftests` then calls `rep.fail("fixture", "…step 0 cannot run")` and
returns — **the gate's verdict is FAIL and the php programme could not have
gated a single row.**

The link is **read-only on `pilot/`**: `fixture.py:30` writes to
`REPO/.temp/build/docrepro`, which the `.temp` link sends into
`.temp/php-scratch/`. So the php side builds its own six fixture binaries and
never touches the PAT tree — confirmed by T3.

### GAP 2 — `.temp`, and which of the three options I took, and why

**Chosen: `.temp/php-root/.temp -> ../php-scratch`, a php-only scratch root.**

| option | verdict |
|---|---|
| **A.** let it nest at `.temp/php-root/.temp/` | **REJECTED.** `root.py` *rebuilds* the shim — that is what makes it a derived artefact — so every rebuild would silently delete every build artefact, `docrepro` fixture and callgrind file underneath it and force a full recompile. **A scratch tree must not live inside the thing that gets thrown away.** Secondarily, a `.temp` inside a `.temp` is invisible to `ls .temp/` and to any "delete the artefact" sweep. |
| **B.** point it at the real `.temp/` | **REJECTED, and this is the dangerous one.** `build.py:119` keys the build dir on `pattern_id` = `basename.split("-")[0]`, so `ph00` and `p01` do not collide *today*. A collision would be silent and would swap a binary underneath a measurement. One directory buys that away. |
| **C.** its own `.temp` link → `.temp/php-scratch` | ✅ **CHOSEN.** Visible at `ls .temp/`, survives a shim rebuild, cannot collide. |

Verified in practice: `harness-php/gate.py --tool build ph00` put its binaries
in `.temp/php-scratch/build/ph00/`, and `ls .temp/build/ | grep ph00` is empty.

### ⚠ GAP 3 — a write into `harness/` that no `git status` can see

Not in the manager's list and not a link: **importing the harness through the
shim writes the bytecode cache into the REAL `harness/__pycache__/`** (the OS
resolves the link) **with the SHIM path recorded as `co_filename`**, so a
later *PAT* traceback would name `.temp/php-root/harness/check.py`. Measured
rather than reasoned, on a scratch module (`.temp/php0/pycdemo`):

```
m.__file__ = .../pycdemo/shim/real/m.py
pyc at pycdemo/real/__pycache__/m.cpython-312.pyc
  co_filename = .../pycdemo/shim/real/m.py      <- the SHIM path, in the REAL dir
```

It moves no hash (`__pycache__` is gitignored and outside every glob) and it
only bites when a php run is the **first** to import a freshly-edited harness
module — the existing `harness/__pycache__/*.pyc` all still carry the real
path, because a valid cache is not rewritten. `harness-php/gate.py` sets
`PYTHONDONTWRITEBYTECODE=1` so the php path never writes one at all. Cost: one
re-parse of a 600 KB source per run.

### A fourth construction, outside the four modules

`patterns/*/inputs/gen.py` builds its own repo root — `sys.path.insert(0,
<gen.py dir>/../../../common)` — rather than using `REPO`. It resolves to the
**real** `common/` when run from the tree and to `common-php/` when run
through the shim; both have `slb.py`, so both work. Noted because it is a
convention every php row inherits and it is not in any harness module.

---

## §4 — the three claims I was asked to refute

### Claim 1 — *"the shim needs only the five links in §2, plus a decision about `.temp`"*

**REFUTED.** It needs **seven**, and the one you did not know about is a hard
gate failure rather than a hash question: **`pilot`**. Plus a third escape
(`__pycache__`) that is not a link at all. Details, with the measurement, in
"The sweep" above.

The decision on `.temp` is option **C** — its own link to `.temp/php-scratch`
— and the reason that beats letting it nest is not tidiness: `root.py` rebuilds
the shim, so a nested scratch tree would be deleted on every rebuild.

### Claim 2 — *"relocating `p01` as `ph00-smoke` is the cheapest end-to-end proof"*

**UPHELD**, and I checked the specific worry before copying anything rather
than after. The pins you feared would drag do not:

| pin | drags? |
|---|---|
| `collapse` `Ir` floor | **no** — not declared at all. `check.py` derives it as `ALPHA_IR_PER_WORK * model.work_per_call` and asserts `d(Ir)/d(work) >= alpha` across two probe shapes. This was the pin most likely to break on a path change and **it does not exist**. |
| `identity` | **no** — `[{"a":"unsafe","b":"verus","O0":"norel","O3":"exact"}]`, a property of two binaries |
| `miri` | **no** — `pair:[unsafe,verus]`, `sources:[unsafe.rs]`, row-local |
| `verus.obligations` | **no** — a count over `verus.rs`, copied verbatim |
| `idiom.why` | **YES, and it is the only one** — 12,183 characters (~2,000 words) against `RECAP_PHP.md`'s 200-word cap |

So the whole cost was **one string edit plus a `provenance` object**, against a
minimal fresh row's `spec.md` contract + `model.py` + `inputs/gen.py` + five
rungs **+ a Verus proof**. Contract hash moved
`b5d7dc8dd173c5…` → `8c941e54f7ae3a…`; nothing in `required`, `forbidden`,
`identity`, `miri`, `collapse`, `verus` or `driver` was touched.

⚠ **But the claim omits one real cost, and it is not zero.** `check.py::_env_block`
records `repo_path_bytes = len(REPO)`, and through the shim `REPO` is
**20 bytes longer** than the PAT root. The gate's own `domain` string makes an
equal `repo_path_bytes` a **necessary** condition for comparing two records,
and `TASK_114` measured **±7 `Ir`/call** from a 2-character `argv` change. **So
no php row's marginal `Ir` is comparable to any PAT row's, by the harness's own
rule** — including `ph00`'s to `p01`'s. That is a property of the shim, not of
this row, and it should be written into `.memory-php/` before the first real
row is measured. Recorded in `patterns-php/ph00-smoke/NOTES.md` and
`README.md`.

### Claim 3 — *"`common-php/` re-exporting the PAT `common/` files via symlink will hash correctly"*

**HALF RIGHT, AND THE HALF THAT IS WRONG IS THE HALF YOU WERE WORRIED ABOUT.**

✅ **The symlink half works, and I measured it three ways.** `glob.glob`
returns symlinks, `os.path.isfile` follows them, `sha256_file` reads through
them, and `os.path.relpath(s, REPO)` yields the natural key. A symlinked
`driver.c` in `common-php/` therefore lands under `common/driver.c` with the
real file's hash. A symlink **to a symlink** also resolves —
`check.py::_mutant_path` builds one (`<clausemut>/common -> <shim>/common ->
common-php`) and it reaches `driver.h`, `slb.py` and `emalloc_shim.h`.

❌ **But the glob does not reach the files the php side actually adds.**
`check.py::main`'s three `common/` entries are:

```
glob(REPO/common/driver.*)      glob(REPO/common/*.py)      glob(REPO/common/layout/*.py)
```

**all non-recursive.** `common-php/emalloc_shim.h` is a `.h` at the top level
and matches **none** of them, so as specified in the task it would sit in **no
digest at all** — precisely the failure §1.4 named. `common/census/README.md`
states the same glob property from the other side, deliberately, to keep that
directory *out* of the digests.

**⚠⚠ CONSEQUENCE FOR TEST T4, AND THE TEST AS WORDED CANNOT PASS.** T4 asks
that *"every `common-php/` file appears in `ph00`'s gate `source_sha256`"*.
Three of the eight cannot, without editing `check.py` — which costs a
33-pattern re-gate. I did not edit it. What I built instead, and what it does
and does not buy:

1. **`common-php/digest_bridge.py`** — a top-level `.py`, so `common/*.py`
   **does** reach it, carrying the sha256 of every `common-php/` file the
   globs miss. Its own hash is in every php gate record, so no `common-php/`
   file's content can move without either moving a hash in every php record or
   making `--verify` fail loudly. `harness-php/gate.py` runs `--verify` before
   every tool, and refuses to run the tool if it fails (demonstrated above).
2. ⚠ **What it does NOT buy, said plainly:** the bridged files are **not
   keys**. A reader of a php gate record sees `common/digest_bridge.py`, not
   `common/emalloc_shim.h`, and has to come here to expand it.
3. ⚠⚠ **And a second gap the task did not ask about, which I think is the more
   serious one: the MEASUREMENT digest.**
   `measure.py:229-235`'s `measurement_sources()` globs `common/driver.*` and
   `common/slb.py` **and no other `.py`**, so neither `digest_bridge.py` nor
   anything it bridges is in a measurement record. **A row whose kernel
   `#include`s `emalloc_shim.h` would have an allocator its measurement record
   does not pin**, and the allocator is exactly the thing `PLAN_PHP.md` §4.3
   says is not neutral.
   ✅ **The fix needs no harness edit and I verified it:** `check.py::main`
   globs `<row>/c/*` and `measure.py:228` globs the row's own sources, so a
   symlink `patterns-php/<row>/c/emalloc_shim.h -> ../../../common-php/emalloc_shim.h`
   puts the real content under a natural key in **both** digests. Measured:

   ```
   glob returns the symlink        : ['emalloc_shim.h']
     os.path.isfile(symlink)       : True
     key os.path.relpath(s, REPO)  : .../phZZ-x/c/emalloc_shim.h
     sha256 through the symlink    : 0d05c94ff579cff80a4fdd0a8a6c141b43dd4c223005ce49daedf6c67f62233f
     sha256 of the real file       : 0d05c94ff579cff80a4fdd0a8a6c141b43dd4c223005ce49daedf6c67f62233f
   ```

   `.tasks-php/PROTOCOL_PHP.md` §B2 makes that symlink **mandatory** for any
   row that links the shim.

**A rejected alternative, recorded so it is not re-derived.** Naming the shim
`common-php/driver.emalloc.h` would put it in both digests by matching
`common/driver.*`, with zero machinery — genuinely simpler than the bridge.
I did not take it because it makes the glob's accident load-bearing in a
*filename*, generalises to nothing (`payload decoders`, `.rs` helpers,
subdirectories all fail the same way), and the name would be a permanent
puzzle. **If the manager prefers it, it is a rename and a `--regen`.**

### An extra correction, not in the three

⚠ `PLAN_PHP.md` §4.3 cites *"`zend_alloc.c:39-43` forces the size-class cache
on in both `#ifdef` arms"*. Measured against the pristine tarball it is
**`:40-44`**:

```
40  #ifdef ZEND_MM
41  #define ZEND_DISABLE_MEMORY_CACHE 0
42  #else
43  #define ZEND_DISABLE_MEMORY_CACHE 0
44  #endif
```

The claim is right; the coordinate is off by one. Corrected in
`common-php/emalloc_shim.h` and `.tasks-php/PROTOCOL_PHP.md`.

⚠ **And a truncation neither `PLAN_PHP.md` nor the task file knows about.**
`zend_alloc.c:295`, in `_ecalloc`:

```c
int final_size = size*nmemb;
```

Two `size_t` multiplied and stored in a **SIGNED 32-bit `int`**, then
`_emalloc(final_size)` at `:298` and `memset(p, 0, final_size)` at `:303`. It
is a *third* truncation, on a different path, with a different modulus and a
sign — a negative `final_size` sign-extends to a huge `size_t` in **both**
calls. `ecalloc(0x40000000, 4)` — a 4 GiB array — allocates **0 bytes and
succeeds**, demonstrated above. Also `_estrndup`'s `uint length` parameter
(`:392`) narrows at the API boundary and `length+1` wraps at `UINT_MAX`.

---

## Building `ph00-smoke` — four things the plan does not know, all found by running it

The relocation itself was one string edit (§4 claim 2). **Getting it green was
not**, and every obstacle is a fact about the harness that the next php row
will hit too.

### 1. ⚠⚠ `RECAP_PHP.md`'s *"a `spec.md` `why` stays ≤ 200 words"* IS UNSATISFIABLE AS WORDED

Gate run 1 hard-failed:

```
[idiom-named-spelling] idiom.why does NOT carry the shared named-spelling
paragraph (11003 bytes, sha256 59748cce2db5..., from 'NAMED-SPELLING STANDARD'
to 'p01 and p08 neither'). Every pattern's `why` ends with it, byte-identical,
and it is what DEFINES what a backticked `required`/`forbidden` entry pins ...
Without it this pattern's backticked pins are undefined by its own contract.
```

Measured, on the actual strings:

| | chars | words |
|---|---:|---:|
| p01's `idiom.why`, total | 12,181 | ~2,000 |
| … of which the **mandatory shared paragraph** | **11,003** | — |
| … of which **p01's own row-specific prose** | **1,177** | **201** |
| ph00's row-specific prose | 1,220 | **200** |

⚠⚠ **So p01 already complies with the 200-word rule, on the only half a row
controls** — and the "~7,000-word JSON string" that motivated the size rule is
**90 % a gate-required constant shared byte-identically by all 33 patterns.**
The rule can only mean *200 words of row-specific prose before the mandatory
paragraph*, and `RECAP_PHP.md` needs that qualification or the next agent
deletes the paragraph exactly as I did.

⚠ **A second trap inside it, also measured:** the gate's own reproduction
command uses `str.find`, so it takes the **first** occurrence of the literal
`NAMED-SPELLING STANDARD` in `spec.md`. My first fix mentioned that phrase in
the row-specific prose above it, and the check's set went from size 1 to
**size 2** — i.e. it would have hashed my prose. Reworded to lowercase; now:

```
the gate's own reproduction command, over all 33 specs + ph00: {'59748cce2db5'} -> size 1
```

### 2. ⚠⚠ `contract_sha256` HAS A SPELLING, AND THE OBVIOUS ONE IS WRONG

`check.py::read_contract` matches `` r"```slb-contract\s*\n(.*?)```" `` —
**the capture keeps the newline before the closing fence.** The obvious
spelling `` r"```slb-contract\n(.*?)\n```" `` hashes one byte less. Verified
against a committed record:

```
p01 committed contract_sha256: 5360d6f3dd7a4607eaf3599433ca95c0ed43dd66fe20fc85c86d52661597e1e7
  naive  `\n``` spelling     : b5d7dc8dd173c583b9918d1a1f2e952f8160437322158343194dc8ebce2ce3c2
  check.py::read_contract    : 5360d6f3dd7a4607eaf3599433ca95c0ed43dd66fe20fc85c86d52661597e1e7
  they differ by             : '\n'
```

⚠ **My first `PROTOCOL.md` rule-6 disclosure used the naive spelling and was
therefore a number that matches nothing.** It is disclosed and corrected in
`patterns-php/ph00-smoke/NOTES.md` rather than quietly replaced — a false
disclosure is worse than the stale thing it describes, because a reviewer
trusts it *instead of* re-checking. **Anyone writing a rule-6 disclosure in
this repo should use `check.py::read_contract`'s regex.**

⚠ **And the two regexes disagree about more than a hash.** My repair script
rewrote the fence with the gate's regex and so dropped the newline before the
closing fence — `}` and ` ``` ` on one line. `check.py` still parsed it;
`harness-php/provenance.py`, on the naive regex, ran on to the **next** fence
in the file and reported `Extra data: line 206 column 2`. ✅ **`gate.py`'s
preflight caught it and refused to run the gate at all** — the first time the
preflight earned its keep:

```
preflight
  ok   shim ...
  ok   common-php/ digest bridge
  FAIL provenance ph00
       |   BAD  ph00-smoke: Extra data: line 206 column 2 (char 21909)
PREFLIGHT FAILED -- the tool was NOT run:
```

`provenance.py` now uses `check.py`'s spelling. **A validator that disagrees
with the gate about where the contract ENDS cannot be trusted about what is
IN it.**

### 3. ⚠ A BRAND-NEW ROW COSTS SIX COMMANDS, NOT THREE

`check.py::check_published_tables`'s own message says *"three commands, not
two"*, and that is about a different case (no measurement record at all). The
full loop, measured:

```
1. gate.py --tool build   ph00 --all   28 builds        ~2 min
2. gate.py --tool measure ph00         28 cells x 2 in  ~11 min
3. gate.py --tool report  ph00         the table exists
4. gate.py                ph00         FAILS: [tables] cites no contract_sha256
5. gate.py --tool report  ph00         re-render, now with the audit section
6. gate.py                ph00         green
```

Steps 4→6 cannot be reordered away: `report.py`'s audit section renders from
`results/gate/<row>.json`, which does not exist until a gate has run, and
stage 9c compares the published table against a fresh render of **this run's**
record. `check.py::check_table_render` says so itself — *"`harness/report.py
<row>` reads that record only after this run has written it, which is why
`report.py` comes after the gate and not before."*

⚠ **And step 1 is not optional.** `measure.py` **builds nothing**. My first
`measure` run, before any build, reported `static: 1 cells` and **wrote a
one-cell record without complaining**.

### 4. The gate enforces the citation convention, and it caught me

Two of gate run 1's six failures were:

```
[doc-citation] patterns/ph00-smoke/NOTES.md:72 cites `check.py:3392` -- a line
citation into check.py rots (it has grown every task). Name the FUNCTION and
give no line number: `check.py::<function>`.
```

I had already found and fixed this by reading `.memory/02-bench-rules.md`
before the gate reported it; **21 `check.py:NNNN` citations across 6 of my
files became `check.py::<function>`.** ⚠ **`PLAN_PHP.md` §2.1a itself carries
three** — `check.py:8903`, `:9128`, `:10534` — plus `report.py:89`/`:238`. The
`report.py` ones are within the project's own current practice for the small
stable modules; **the three `check.py` ones will rot** and the manager should
convert them to `check.py::check_published_tables`,
`check.py::check_table_render` and `check.py::main`.

The sixth failure was `[twin] NOTES.md carries no `SLB-TRUSTED-ARGUMENT
verus.rs get_unchecked` section` — self-inflicted, by replacing p01's NOTES.md
wholesale. p01's argument is carried over verbatim and labelled as p01's,
because `verus.rs` and the trusted wrapper are byte-identical, so rewriting it
would be a different argument about the same bytes.

---

## §1.7 acceptance — `harness-php/gate.py ph00` is GREEN

```
check.py: PASS-WITH-BLOCKED-ROWS          (gate.py exit 0)

path             results-php/gate/ph00-smoke.json 54640 bytes
pattern          ph00-smoke
verdict          PASS-WITH-BLOCKED-ROWS
complete_run     True
contract_sha256  91d88e1e18b192258a1acc577672b2989e33f84c112615b03090bb011dad5e8b
failures         0
blocked          [('miri', 'unsafe.rs on large.bin')]
loud             ['section', 'section']
source_sha256    28 keys
```

⚠ **`PASS-WITH-BLOCKED-ROWS` is the green verdict here, not a hedge** — it is
exactly what the committed `results/gate/p01-array-sum.json` carries, for
exactly the same reason. Side by side:

```
                   p01 (committed)              ph00 (this run)
verdict            PASS-WITH-BLOCKED-ROWS       PASS-WITH-BLOCKED-ROWS
complete_run       True                         True
failures           0                            0
blocked            ['unsafe.rs on large.bin']   ['unsafe.rs on large.bin']
loud sections      ['section', 'section']       ['section', 'section']
source keys        35                           28
```

The one blocked row is `miri did not finish within 180s` on `large.bin` — a
property of the 12 MB payload under interpretation, identical to p01's.

### The 35 → 28 key difference, itemised (nothing is unexplained)

| | keys | why |
|---|---|---|
| in p01, not ph00 | 13 × `patterns/p01-array-sum/*` | the row is a different row |
| | **8 × `common/layout/*.py`** | ⚠ **deliberate.** `common-php/layout/` does not exist, so `glob(common/layout/*.py)` returns `[]`. `common/layout/` is the PAT loop-geometry study; no php row uses it, and linking it would make every php record claim a dependency it does not have. **This is the only structural difference between a PAT gate record and a php one.** |
| in ph00, not p01 | 13 × `patterns/ph00-smoke/*` | the row |
| | 1 × `common/digest_bridge.py` | the digest bridge, §4 claim 3 |

Everything else — the 9 `harness/*.py`, `verus_run.py`, `common/driver.{c,h,rs}`
and `common/slb.py` — is present in both **with identical hashes**, verified
against the committed PAT *measurement* record too:

```
shared keys, php vs PAT p01 measurement record:
  SAME  common/driver.c   f21be5c4a8dab98b        SAME  harness/asm.py      85ea334dc96abfcf
  SAME  common/driver.h   57f72fffa54edc44        SAME  harness/build.py    456e8f95323bcad9
  SAME  common/driver.rs  595de2393cfa0beb        SAME  harness/measure.py  0b6c5cfd3620ee6b
  SAME  common/slb.py     2abd87f76712ac0c        SAME  verus_run.py        5d1b8b2446fa1486
```

**That is claim 3's symlink half, verified in a real record rather than a
probe:** `common-php/driver.c` is a symlink to `common/driver.c` and lands
under the key `common/driver.c` with the real file's hash.

### T4 — is every `common-php/` file in a digest?

```
ph00 GATE record: 28 source_sha256 keys
ph00 MEAS record: 18 source_sha256 keys

common-php/ file           in gate?  in meas?  hash matches?  how
  digest_bridge.py         yes      NO       yes            GLOBBED
  driver.c                 yes      yes      yes            GLOBBED
  driver.h                 yes      yes      yes            GLOBBED
  driver.rs                yes      yes      yes            GLOBBED
  slb.py                   yes      yes      yes            GLOBBED
  emalloc_probe.c          NO       NO       yes            BRIDGED via digest_bridge.py
  emalloc_shim.c           NO       NO       yes            BRIDGED via digest_bridge.py
  emalloc_shim.h           NO       NO       yes            BRIDGED via digest_bridge.py

VERDICT: every common-php/ byte is pinned somewhere
```

**T4 as worded — "every `common-php/` file appears in `ph00`'s gate
`source_sha256`" — is FALSE for three of eight and cannot be made true without
editing `check.py`.** What holds instead: no `common-php/` byte can move
without either moving a hash that is in every php gate record, or making
`digest_bridge.py --verify` fail — and `gate.py`'s preflight refuses to run
the tool when it does. See §4 claim 3.

### T3 — no write escaped the php tree

The **before** snapshot was taken before the first build. It hashes every file
under `patterns/`, `results/`, `harness/`, `common/` and `pilot/`, **including
`__pycache__`**, because `git status` is blind to gitignored writes and a
clean `git status` after a run that wrote nothing proves nothing.

```
files before 3044  after 3044
ADDED: 0
REMOVED: 0
CHANGED: 0
CLEAN
```

Across 28 builds, one full measurement (56 callgrind runs + 1680 timed reps),
two renders and **three full gate runs**. `git status --short` gained only
`.tasks-php/PROTOCOL_PHP.md`, `.tasks-php/TASK_PHP_002_REPORT.md` and
`results-php/`; `git status --short -- patterns results harness common pilot`
is **empty**.

**What would make it fail** — verified, because a differ that always says
CLEAN is worth nothing (`pat_snapshot.py --selftest`):

```
selftest ADDED  : ['harness/__pycache__/x.pyc', 'results/new.json']
selftest CHANGED: ['harness/x.py']
MUST-FIRE CONTROL: FIRED (the instrument works)
```

### T1 — `measure.py --check-stale`, after

```
$ python3 harness/measure.py --check-stale
...
66 record(s) examined, 0 STALE
```

Unchanged from the first command of the task. **The 33-pattern PAT programme
is exactly as it was.**

### `.web/` is still blind to the php tree — checked, not assumed

`PLAN_PHP.md` §2.2 says `results-php/` is invisible to the report. Verified by
reading every repo-rooted path `.web/build_data.py` constructs: `patterns/`,
`results/`, `results/gate/`, `results/SYNTHESIS.md`, `common/layout/data/`,
`synthesis/`. **No `patterns-php` or `results-php` anywhere.** Nothing was run
in `.web/` and nothing there was touched.

### Cost, for planning

| step | wall |
|---|---|
| `build ph00 --all` (28 cells, incl. 8 Verus) | ~2 min |
| `measure ph00` (28 cells × 2 inputs callgrind + 1680 timed reps) | ~11 min |
| `report ph00` | seconds |
| one full `check.py` run | **~6 min**, of which 3 min is the blocked Miri row |
| **a green new row, end to end (6 commands)** | **~28 min** |

---

## Problems

1. **My own `PROTOCOL.md` rule-6 disclosure was wrong on first writing.** I
   recorded `contract_sha256` with the obvious fence regex, not
   `check.py::read_contract`'s. Corrected and *disclosed* in
   `patterns-php/ph00-smoke/NOTES.md` rather than replaced. See §"Building
   `ph00-smoke`" 2.
2. **I edited files under a running gate**, which `.tasks/PROTOCOL.md` rule 11
   warns against — the doc-citation fixes and two `.md` rewrites landed while
   gate run 1 was in its Miri stage, so run 1's record hashed sources its
   earlier stages had not seen. **Mitigation: that record was discarded and
   the tree was re-gated twice from a frozen state.** The shipped record is
   gate run B's, taken with nothing changing underneath it.
3. ⚠⚠ **I leaked eleven stuck background shells, and the mechanism is worth
   knowing because it produced SILENCE THAT LOOKS LIKE PROGRESS.** My waiter
   loops were `until ! pgrep -f "php-root/harness/check.py ph00"; do sleep; done`
   — and `pgrep -f` matches **whole command lines, including the waiter's own
   and those of sibling shells in this harness**, every one of which embeds the
   command text verbatim. So each loop matched itself (and its siblings) and
   could never exit.

   **Consequence, and it is not cosmetic:** I twice read "gate RUNNING" when
   the gate had already finished — once for **eight minutes** while gate run 2
   had in fact died in the preflight *seconds* after starting. Only a direct
   `ps` for the actual `python3 … check.py` process found it. ⚠ This is the
   harness note in my own task prompt (*"a completion notification means an
   agent stopped, not that it finished"*) with the sign flipped: **a waiter
   that never fires reads exactly like a job that never finishes.**

   Cleaned up by reading each candidate's `/proc/<pid>/cmdline`, matching it
   against the literal loop text, and killing that exact PID — never a
   substring match, never `pkill` (`CLAUDE.md` constraint 2). Zero skipped,
   zero collateral, and `ps` for `finish.sh|check.py ph00|until ! pgrep`
   returns **0** now.

   ⚠ **The rule for the next agent: never `pgrep -f` a pattern that appears in
   your own command line.** Match the interpreter and script instead
   (`pgrep -f '^/usr/bin/python3 .*/check\.py'`), or poll a file the job
   writes.
4. **`harness-php/gate.py --tool measure ph00` on an unbuilt tree writes a
   one-cell record and says so only in a line nobody reads** (`static: 1
   cells`). That is a `measure.py` property, not something I can fix without
   touching it; `PROTOCOL_PHP.md` §E now leads with `build --all`.
5. `results-php/tables/ph00-smoke.md` is **28,986 bytes** for a throwaway row,
   because `report.py` renders p01's full `idiom.why`. It is derived, and it
   goes when `ph00-smoke` goes.

## Unsure / not done

1. **`.memory-php/` does not exist.** `PLAN_PHP.md` §2.2 lists it; the task
   file does not, and `.tasks/PROTOCOL.md` rule 4 makes `.memory/` the
   **manager's** to write. Everything durable I learned is in this report and
   in `.tasks-php/PROTOCOL_PHP.md`. **The manager owes the `.memory-php/`
   layer**, and §"Memory updates" below lists what should go in it.
2. **The digest bridge covers the GATE digest only.** Nothing in
   `common-php/` other than `driver.*` and `slb.py` reaches
   `measure.py::measurement_sources`. The row-level `c/`-symlink route closes
   it and is verified, but **no row exercises it yet** — `ph00-smoke` does not
   allocate. The first allocating php row is where it gets tested for real.
3. **The `driver.emalloc.h` rename is a live alternative I did not take.** It
   would put the shim in both digests with zero machinery, at the cost of a
   permanently puzzling filename. Manager's call; it is a rename plus a
   `--regen`.
4. **`emalloc_shim.h` is faithful to `_emalloc`, `_efree`, `_safe_emalloc`,
   `_ecalloc`, `_erealloc` and `_estrndup` on the non-`ZEND_MM`, non-`ZEND_DEBUG`
   arm only.** `ZEND_MM`'s sub-allocator (`zend_alloc.c:46-49` → `zend_mm.c`) is
   **not modelled at all**, and I did not establish which arm the shipped 5.0.0
   build actually compiles. Every "deliberately not modelled" decision is listed
   in the header, but ⚠ **a row whose defect lives inside `zend_mm` cannot use
   this shim and I have not checked whether any candidate does.**
5. **The tally `php_shim_tally()` is a mixing function I invented**, not
   anything PHP does. It is instrumentation for folding allocator behaviour
   into a kernel's `u64` (`PLAN_PHP.md` §4.3). No row uses it yet, so its
   sensitivity is untested.
6. **I did not verify the `provenance` validator against a real php kernel** —
   there is none. T5's passing case is `Zend/zend_alloc.c:142-217` (`_emalloc`),
   a real span from the real tarball, but it is not attached to a row.
7. **`harness-php/gate.py` strips a literal `--` from its pass-through
   arguments.** No harness tool needs one today; if one ever does, that is a
   bug.
8. **I did not re-run `.web/build_data.py` or `.web/check.mjs`.** I established
   by reading that `.web/` cannot see `results-php/`, and running it was
   outside the task.
9. **The `[idiom-forbidden]` and `[twin] safe_naive_verus.rs` shouts in
   `ph00`'s record are p01's, inherited verbatim.** The committed
   `results/gate/p01-array-sum.json` carries the same two `loud` entries. I did
   not attempt to fix them: doing so would edit a pin, and the whole point of
   the relocation is that no pin moved.

## Adjacent work seen, not done

1. ⚠ **`PLAN_PHP.md` §2.1a carries three `check.py:NNNN` citations** —
   `:8903`, `:9128`, `:10534` — against `.memory/02-bench-rules.md`'s *"name
   the FUNCTION and give NO LINE NUMBER AT ALL"*. They are
   `check.py::check_published_tables`, `check.py::check_table_render` and
   `check.py::main`. The gate enforces this rule on `patterns/*/`docs and it
   failed me for it; `PLAN_PHP.md` is not under that check.
2. ⚠ **`PLAN_PHP.md` §4.3's `zend_alloc.c:39-43`** is `:40-44` in the pristine
   tarball.
3. ⚠ **`RECAP_PHP.md`'s size rule needs the "row-specific" qualification**, or
   the next agent deletes an 11 KB gate-required paragraph exactly as I did.
4. **`RECAP_PHP.md` open item 4** (CRASH-136 rejected on extraction cost) is
   still owed a manager re-adjudication; `PROTOCOL_PHP.md` §A1 restates that
   a tier is a cost and never a filter.
5. **`_ecalloc`'s signed truncation (T3) and `_estrndup`'s `uint` narrowing
   are candidate mechanisms in their own right**, and `PLAN_PHP.md` §4.3's
   note that the truncation is "a multiplier on every sizing defect, not a
   pattern of its own" was written about `real_size` only. Whether the
   *signed* one deserves the same treatment is a catalogue question.

## Memory updates

**None written — `.memory-php/` does not exist and rule 4 makes it the
manager's.** Durable facts landed in files instead:

| fact | where I put it |
|---|---|
| the 7-link shim, the `pilot` gap, the `.temp` decision, the `__pycache__` escape | `harness-php/root.py` module docstring (+ `--sweep`, which re-derives it) |
| the six-command loop for a new row; the `contract_sha256` spelling; the 11,003-byte `why` tail | `.tasks-php/PROTOCOL_PHP.md` §E |
| the three allocator truncations, `_safe_emalloc`'s uselessness, the size-class cache, the `c/`-symlink requirement | `.tasks-php/PROTOCOL_PHP.md` §B + `common-php/emalloc_shim.h` |
| the `common/` glob's reach and what the bridge does and does not buy | `common-php/digest_bridge.py` docstring |
| the citation base, the no-build-tree rule, the manifest's size justification | `patterns-php/SOURCES.md` |
| the rule-6 disclosure and its correction; why relocating p01 was right; `repo_path_bytes` | `patterns-php/ph00-smoke/NOTES.md` |

**Candidates for `.memory-php/` when the manager writes it**, in priority
order:

1. **`repo_path_bytes` differs by 20 through the shim, so no php marginal `Ir`
   is comparable to any PAT one** by the gate's own `domain` rule. This is a
   property of *every* php row and it should be written down before the first
   real measurement, not after somebody quotes a cross-programme ratio.
2. **The `contract_sha256` spelling** (`check.py::read_contract`).
3. **`RECAP_PHP.md`'s `why` cap means row-specific prose only.**
4. **A new row costs six commands and ~28 min**, with `gate → report → gate`
   irreducible.
5. **`common/layout/*.py` is absent from php gate records by design** — the
   only structural difference between a PAT record and a php one.
6. **The ASan/cache finding**: the same UAF is reported on a 96-byte block and
   silent on a 24-byte one under the faithful allocator. This is the concrete
   mechanism behind `RECAP_PHP` F3 and it is now demonstrated rather than
   inferred.

## Scratch

`.temp/php0/` — 868 K, all evidence. `REBUILD.sh` rebuilds every deleted
artefact (both probe binaries, the two shim trees, the `pycdemo` and
`symlinktest` fixtures) and was **re-run and re-verified** after the deletion:
16/16 probe checks, 12/12 provenance cases, ASan `uaf-plain` 2 lines /
`uaf-cached` 0 lines. Kept: `pat_before.json`, `pat_after.json`,
`pat_snapshot.py`, `t4_digest.py`, `t5_provenance.py`, `fix_ph00.py`,
`named_spelling.txt`, the three ASan captures, and the build / measure /
gate / report logs. Deleted: every binary, the callgrind outputs
(`.temp/php-scratch/` is down from 145 M to 64 K) and the throwaway symlink
trees.

---

**Running count: launched from 4.** Refuted this task: claim 1 (the shim needs
7 links, not 5, and one of the two missing ones is a hard stage-0 failure);
claim 3's second half (`common-php/emalloc_shim.h` is in **no** digest under
the glob as written, and T4 as worded is unachievable); `PLAN_PHP.md` §4.3's
`zend_alloc.c:39-43` (it is `:40-44`); and `RECAP_PHP.md`'s 200-word `why`
cap (unsatisfiable as worded — the gate hard-requires an 11,003-byte tail).
Claim 2 was **upheld** with a measurement, plus one cost it omitted
(`repo_path_bytes`). ⚠ **Reconciliation is the manager's job, not mine.**

---

## Post-report checks (run after the report was first written)

**A defect in my own driver, found by running my own docstring.**
`harness-php/gate.py --tool measure --check-stale` — an invocation the module
advertises — was rejected: `argparse.REMAINDER` only starts collecting at the
first *positional*, so a tool flag with no positional after it never reached
the tool. Fixed with `parse_known_args`; `gate.py` is in no digest, so this
cost nothing. All documented forms re-run and verified.

**And the fix immediately paid for itself — the php tree has its own
staleness check, and it is green:**

```
$ python3 harness-php/gate.py --tool measure --check-stale
FRESH       results/gate/ph00-smoke.json               28 source(s)
FRESH       results/ph00-smoke.json                    18 source(s) + 8 input(s)

2 record(s) examined, 0 STALE
```

⚠ **That is a stronger statement than the gate's own PASS**: it says the two
shipped `results-php/` records still hash the tree as it stands *now*, after
every edit made since they were written. It also means the php programme
inherits the PAT programme's staleness discipline for free, through the shim,
with no new tool.

**Rule 10** — every `.tasks-php/TASK_PHP_*.md` cited from `.tasks-php/`,
`patterns-php/`, `common-php/`, `harness-php/`, `RECAP_PHP.md` and
`PLAN_PHP.md` resolves; the check prints nothing, and this report file was
written before anything cited it.
