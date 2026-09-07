# TASK_PHP_003 — adversarial review of Phase 0 — REVIEWER REPORT

**Role:** research reviewer. **Launched from a running count of 8.**
Reconciliation is the manager's job; §"What I refuted" lists what moved.

> **Rule 3 disclosure.** Six of the thirteen findings below are against the
> **manager's own design**, not the engineer's: `M1` (the `repo_path_bytes`
> figure and the domain analysis), `M3` (`PLAN_PHP.md` §1 / `SOURCES.md` §3's
> allocator-patch mechanism), `M4` (`PROTOCOL_PHP.md` §E's header), `M5`
> (`PLAN_PHP.md` §6's schema claim), `m1` (`RECAP_PHP.md`'s START HERE box) and
> half of `B1` (the "mandatory symlink" wording in `RECAP_PHP.md` open item 10).
> They are marked ⚙ below.

> **Planting disclosure.** I planted into five tracked files —
> `common-php/emalloc_shim.h`, `common-php/digest_bridge.py`,
> `patterns-php/ph00-smoke/verus.rs`, `harness/vparse.py`, and a gitignored
> `harness/__pycache__/zzz_probe.pyc` — plus three throwaway files under
> `common-php/`. **Every one was restored in a `finally:` and verified BY
> BYTES** against a sha256 taken before anything was touched
> (`.temp/php3/BASELINE.sha256`). Final state: all seven baseline hashes `OK`,
> `git status --short` **empty**, and the engineer's own `pat_snapshot.py`
> reports the PAT tree **byte-identical to their post-task snapshot** (3044
> files, 0 added / 0 removed / 0 changed) after everything this review ran.

---

## Did

Attacked Phase 0 along the seven axes of `TASK_PHP_003.md`, with eight
constructed experiments under `.temp/php3/` (all regenerable —
`.temp/php3/REBUILD.sh`; binaries deleted, generators kept):

| script | attacks |
|---|---|
| `plant_shim.py` | §1.1 the `common-php/*.h` digest gap, both arms (no-regen / regen) |
| `e3_symlink.py` | §1.3 is the `<row>/c/` symlink mandatory or conventional? |
| `e4_sweep.py` | §2 `root.py --sweep`'s must-fire, once per link |
| `e5_p01digest.py` | §2 re-derive the manager's `p01` digest proof, plus its negative |
| `e6_mutate_proof.py` | §3 break `ph00`'s proof; does the gate fail? |
| `e7_prov.py` | §5 13 provenance cases, incl. 3 the engineer did not test |
| `e8_pat_untouched.py` | §7 PAT tree untouched, **with the positive control** |
| `e9_bridge_root.py` | `root.py`'s rebuild claim; which artefact kinds the bridge sees |
| `mul_fidelity.c` / `mul_scan.c` | §4 `_safe_emalloc`'s overflow predicate vs the pristine macro |

---

## Problems

### 🔴 B1 (blocker) ⚙ — the `<row>/c/emalloc_shim.h` symlink is MANDATORY in prose and enforced by NOTHING, and it is the only thing pinning the allocator into a measurement record

`.tasks-php/PROTOCOL_PHP.md:122-135` — *"⚠⚠ **AND THE ROW MUST CARRY THE
SYMLINK** … This is not cosmetic and not optional"*; `RECAP_PHP.md:165` —
*"a **mandatory** `<row>/c/` symlink (measurement half)"*.

Nothing reads it. `harness-php/gate.py`, `common-php/digest_bridge.py`,
`harness-php/provenance.py` and the PAT gate all ignore it. I built a row that
links the shim and omits the symlink (`.temp/php3/e3_symlink.py`, behind a
second shim so `patterns-php/` was never touched):

```
row c/ contents: ['kernel.c', 'kernel.h', 'main.c']       # no symlink

=== (a) does it BUILD with no c/ symlink? `-I COMMON` is build.py::build_c ===
all builds ok
build exit 0

allocator in GATE digest        : NO -- NOTHING
allocator in MEASUREMENT digest : NO -- NOTHING
```

The gate `srcs` list was **lifted verbatim out of `harness/check.py`'s own
source text and evaluated**, not retyped, so it cannot have drifted from what
the gate does. `#include "emalloc_shim.h"` resolves through `-I COMMON`
(`harness/build.py::build_c`), which is `<shim>/common` → `common-php/`, so the
symlink is load-bearing for **nothing at build time** — it is pure convention.

**Concrete failure scenario, and it is one this very review makes likely.**
Fix `B2` below in `common-php/emalloc_shim.h`. `digest_bridge.py --verify`
fails, so you run `--regen` as its own message instructs. That moves
`digest_bridge.py`'s hash, so the row's **gate** record goes `STALE` and you
re-run `gate.py phNN`, which refreshes it. `measurement_sources()` contains
neither `common/*.py` nor anything under `common-php/`, so the **measurement**
record — the one carrying every `Ir` — stays `FRESH` for ever, while the
allocator its numbers were taken with no longer exists. I measured exactly this
staleness asymmetry (`.temp/php3/plant_shim.log`):

```
STALE       results/gate/ph00-smoke.json               common/digest_bridge.py
FRESH       results/ph00-smoke.json                    18 source(s) + 8 input(s)
```

**The fix needs no harness edit**: `gate.py`'s preflight already runs before
every tool — have it grep each row's `c/*.c` for `emalloc_shim.h` and fail if
`<row>/c/emalloc_shim.h` is absent. Two dozen lines, and it turns "mandatory"
from prose into a check.

⚠ **This is the one place the manager's stated expectation was refuted rather
than confirmed** — see `CN1`. The gate half of the two-mechanism fix works. The
measurement half is a naming convention.

---

### 🔴 B2 (blocker) — `emalloc_shim.h`'s `_safe_emalloc` uses a DIFFERENT overflow predicate from PHP 5.0.0's, in the direction that manufactures a defect PHP does not have

`common-php/emalloc_shim.h:340-344`:

> *"`ZEND_SIGNED_MULTIPLY_LONG` (Zend/zend_multiply.h) is modelled by the
> `__builtin_mul_overflow` below: **same predicate**, same `use_dval`
> fall-through to the error path."*

On x86-64 `__i386__` is **not** defined, so PHP 5.0.0 takes
`Zend/zend_multiply.h:36-45`, a **double-precision heuristic**, not an exact
test. Pasting the pristine macro in verbatim beside the shim's spelling
(`.temp/php3/mul_fidelity.c`):

```
a                      b                      PHP    shim   case
8                      8                      0      0      benign
2147483648             4                      0      0      4 GiB, no overflow
9007199254740993       3                      1      0      ...   <== DISAGREE
9007199254740993       5                      1      0      ...   <== DISAGREE
9007199254740995       7                      1      0      ...   <== DISAGREE
4611686018427387904    4                      1      1      true overflow
9223372036854775807    2                      1      1      true overflow
1 = 'overflow, take the E_ERROR path'.  disagreements: 3
__i386__ defined here? no (PHP therefore uses the GENERIC arm)
```

Randomised over the domain PHP's own `< LONG_MAX` guard admits
(`.temp/php3/mul_scan.c`, 20 M samples):

```
samples 20000000   agree 19915477
PHP says overflow, shim says fine : 84523   (first: 61170688267664500 * 12)
shim says overflow, PHP says fine : 0
```

**0.42 % of the admitted domain diverges, 100 % of it one way: PHP raises
`E_ERROR` and returns `0`; the shim allocates and hands the value to the
truncating `_emalloc`.** That is `PLAN_PHP.md` §4.3's own failure mode — *"a
substituted allocator is not neutral … reported a real defect as unreachable
and then invented an explanation for the upstream fix"* — one level down, and
in the *inventing* direction: a row at a `safe_emalloc` call site (the corpus
has 13 CWE-190 rows, and `ext/standard/url.c:499` is `safe_emalloc(3, len, 1)`)
would show a reachable truncation that pristine PHP's guard refuses.

The probe's own `SE CONTROL` — *"a true 64-bit overflow IS refused"* — only
exercises the region where the two predicates agree, so it cannot see this.

**Fix:** paste `zend_multiply.h:36-45` in verbatim, the way every other line of
this file is treated. Cost: a `digest_bridge.py --regen` and a re-gate of any
row that links it (today: none).

---

### 🟠 M1 (major) ⚙ — `repo_path_bytes` is **15** bytes longer through the shim, not 20; and it is not the only domain mover

Claimed in four places: `patterns-php/ph00-smoke/README.md:37`,
`patterns-php/ph00-smoke/NOTES.md:116`, `RECAP_PHP.md:164` (open item 9),
`.tasks-php/TASK_PHP_002_REPORT.md:349`. Measured from the two committed
records:

```
p01  gate record : repo_path_bytes 33   envp_stack_bytes 3653  nvars 48  bytes 3269
ph00 gate record : repo_path_bytes 48   envp_stack_bytes 3686  nvars 49  bytes 3294
'/home/apt/repos_common/sec-ladder'                 33
'/home/apt/repos_common/sec-ladder/.temp/php-root'  48   delta 15
```

Two things are wrong, and the second is the more useful one:

1. **15, not 20.** The conclusion (*no php marginal `Ir` is comparable to any
   PAT one*) stands; the magnitude does not.
2. ⚠ **`repo_path_bytes` is not the only term that moved.** `check.py`'s own
   `domain` string requires *"the same `envp_stack_bytes` … the same
   `tuning_vars` and the same `repo_path_bytes`"*, and `envp_stack_bytes` is
   **+33** with `nvars` **+1** — because `harness-php/gate.py:139` injects
   `PYTHONDONTWRITEBYTECODE=1` into every child. **The mitigation for the
   `__pycache__` escape is itself a second domain violation, and nobody named
   it.** A future agent who "fixes" the path length (by shortening the shim
   name, say) would still not have comparable records, and would not know why.

`NOTES.md` and `README.md` are both in `results-php/gate/ph00-smoke.json`'s
`source_sha256`, so this correction costs a gate re-run (`PROTOCOL.md` rule 6's
cost table).

---

### 🟠 M2 (major) — `root.py --sweep` CANNOT FAIL for four of its seven links

`harness-php/root.py:241-252`:

```python
covered = {n for n, _, _ in LINKS}
...
    if comp in covered:                                          print("LINKED ...")
    elif comp in ("common", "harness", "patterns", "results"):   print("LINKED ...")
    else:                                                        print("⚠ GAP ...")
```

The `elif` is a hard-coded whitelist of four link names that are *also* in
`LINKS`, so it is unreachable today — and it defeats the control. Repeating the
engineer's own must-fire test once per link (`.temp/php3/e4_sweep.py`):

```
link deleted from LINKS  sweep rc  says
harness                  0         LINKED   harness    check.py:10318, 1033, 1034
common                   0         LINKED   common     build.py:48, check.py:10190, ...
patterns                 0         LINKED   patterns   build.py:49, report.py:238, 89
results                  0         LINKED   results    check.py:10534, 8903, 9128
verus_run.py             1         ⚠ GAP    verus_run.py
pilot                    1         ⚠ GAP    pilot      fixture.py:31
.temp                    1         ⚠ GAP    .temp      asm.py:823, build.py:50, ...
```

**The engineer's control was run on `pilot` — one of the three links the
whitelist does not cover — so the whitelist was never exercised.** This is the
silent-skip class the task file names: `--sweep` is the mechanism that is
supposed to make the link list age with the harness, and for the four links
that carry the gate it is a tautology. Delete the `elif`.

---

### 🟠 M3 (major) ⚙ — the "every extracted tree is patched / `REAL_SIZE(size)→(size)` deletes the truncation" mechanism is wrong, in three documents

`PLAN_PHP.md` §1 (`⚠⚠ Every extracted tree on this box is patched … carry
modern-gcc **and allocator** patches (`REAL_SIZE(size)→(size)`, which is
exactly the mechanism §4.3 is about)`), `patterns-php/SOURCES.md:52-66`, and
`common-php/emalloc_shim.h:19-24`. Measured against the pinned manifest over
all 12 extracted 5.0.0 trees on this box:

```
sha256(zend_alloc.c)  has pristine REAL_SIZE?   tree
fb4215f19dc2e68c  1   .app-tests/.temp/oracle/build-5.0.0-mysql-webext-maxlto/...
fb4215f19dc2e68c  1   .app-tests/.temp/oracle/build-5.0.0-mysql-webext-O3lto/...
fb4215f19dc2e68c  1   .app-tests/.temp/oracle/build-5.0.0-mysql-webext/...
fb4215f19dc2e68c  1   .temp/san_tests/oracle/build-5.0.0-mysql-webext-maxlto-asan/...
fb4215f19dc2e68c  1   .temp/san_tests/oracle/build-5.0.0-mysql-webext-maxlto-hardened/...
   (+2 more identical)                            <- fb4215f19dc2 IS the manifest hash
d6245088682d2e00  1   ...-nocache , ...-nocache-asan
b817edb91015b918  1   ...-poison-asan
74a20877c68d1ff4  0   ...-nocache-detect-asan
```

Three separate errors:

1. **7 of 12 trees carry a byte-identical pristine `zend_alloc.c`** — including
   **all three under `.app-tests/.temp/oracle/`, which `SOURCES.md`'s table
   names as "modern-gcc **and allocator**" patched.**
2. **`REAL_SIZE(size)→(size)` exists in exactly ONE tree**
   (`-nocache-detect-asan`), at line **132**, not `:135`. The other two patched
   variants are `ZEND_DISABLE_MEMORY_CACHE 0→1` (`-nocache`) and ASan
   poison annotations (`-poison-asan`) — **neither is mentioned anywhere**, and
   the cache patch is far more consequential for `RECAP_PHP` F3 than the one
   that is.
3. ⚠ **`REAL_SIZE(size)→(size)` does NOT "delete the 32-bit truncation".**
   `real_size` is still `unsigned int` and `real_size = REAL_SIZE(size)` still
   truncates mod 2^32; all the patch removes is the round-up-to-8, so ASan's
   redzone starts at the requested size. For the 18-EB probe the two spellings
   give the *same* `real_size`.

And how patched are these trees actually? Against the manifest:

```
build-5.0.0-mysql-webext-maxlto/php-5.0.0
  manifest files 1170  identical 1169  DIFFERENT 1   differing: ['Zend/zend_modules.h']
build-5.0.0-mysql-webext-maxlto-nocache-detect-asan/php-5.0.0
  manifest files 1170  identical 1168  DIFFERENT 2   differing: ['Zend/zend_alloc.c', 'Zend/zend_modules.h']
```

**I am not asking for the rule to be relaxed** — "cite the pristine tarball,
never a build tree" is right, cheap and should stay. The finding is that the
*evidence given for it* is wrong in a checkable way, in the one document whose
job is to justify it, and that a future agent reading *"the allocator patch
deletes the truncation"* will mis-model the shim. Replace the mechanism with
the measured one: *one* tree changes `REAL_SIZE`, *two* disable the cache, and
`Zend/zend_modules.h` moves in all of them.

---

### 🟠 M4 (major) ⚙ — `ph00-smoke/README.md` ships the command loop this very task REFUTED, and `PROTOCOL_PHP.md` §E's header contradicts its own body

Three numbers for one procedure, in three files landed in the same task:

| file | says |
|---|---|
| `patterns-php/ph00-smoke/README.md:17-27` | *"**Three commands, not two**"* + a 3-command list |
| `harness-php/gate.py:11-18` (docstring) | *"⚠ THE **THREE-COMMAND LOOP** … and it is three and not two"* + a 3-command list |
| `.tasks-php/PROTOCOL_PHP.md:194` (header) | *"A BRAND-NEW ROW COSTS **FIVE** COMMANDS, NOT THREE … `ph00-smoke` needed all five"* |
| `.tasks-php/PROTOCOL_PHP.md:197-204` (body) | **six** numbered commands |
| `.tasks-php/PROTOCOL_PHP.md:221` | *"the **five**-command figure is the one to plan against"* |
| `RECAP_PHP.md:166` (open item 11) | *"**six commands** (~28 min)"* |

`README.md`'s three-command list omits `build --all`, which the engineer
measured as **not optional** (`measure.py` builds nothing and silently wrote a
one-cell record), and omits the irreducible `gate → report → gate` tail. **A
reader who follows the row's own README on the first real php row gets the
sequence this task proved wrong**, and `README.md` is in the hashed
`source_sha256`.

`PROTOCOL_PHP.md` §E is `.tasks/PROTOCOL.md` rule 13's exact failure mode — *"in
a long doc item, only the body gets maintained; the header rots"* — reproduced
in a **brand-new** document, within one task of the rule being restated.

---

### 🟠 M5 (major) ⚙ — the provenance validator accepts an out-of-range span, and `PLAN_PHP.md` §6's headline claim is not what it checks

`.temp/php3/e7_prov.py`, 13 cases, all 10 of the engineer's negatives reproduce.
Two more that do not:

```
ACCEPT   ⚠ span BEYOND end of file (sed prints nothing; hash of b'')
           | r11: OK  Zend/zend_alloc.c:99999-100000  0 bytes  sha256 e3b0c44298fc1c14
ACCEPT   ⚠ c_file names a DIFFERENT file, hash recomputed to match it
           | r10: OK  Zend/zend_hash.c:1-20  1286 bytes  sha256 97c59b936f5aea61
```

1. **`harness-php/provenance.py:118-123` returns `b""` for `a > len(lines)` and
   the caller accepts `sha256(b"")` as a match.** The module's own comment says
   *"a wrong span lands here often"* — and then does nothing about it. A row
   that copy-pastes a line number from the wrong file, or transposes digits,
   verifies **green** and prints `0 bytes`. **A validator whose most likely
   wrong-span case passes is not a must-fire.** Two lines fix it: reject an
   empty excerpt, and reject `b > len(lines)`.
2. ⚙ `PLAN_PHP.md` §6 and `provenance.py:16-17` both say `extract_sha256` makes
   *"**this kernel** came from those lines of that tarball"* a one-command
   check. It does not. **The validator never opens `c/kernel.c` — the string
   `kernel` appears in the module only inside that sentence.** What it checks is
   *"those lines hash to that"*, which is worth having and is not the claim.
   The kernel↔citation link is entirely unverified, and `provenance.tier`
   (`verbatim`/`narrowed`/`modelled`) is a free-text declaration nothing tests.
   Say so in §6, or add the check.

---

### 🟠 M6 (major) — the php toolchain is in NO digest, and a php gate record carries no evidence that its preflight ran

Answering §1.4's question — *enumerate the artefact kinds a php row can ship and
say which digest, if any, covers each* (glob lists lifted from the two modules'
source text, verified in `.temp/php3/e3_symlink.py`):

| artefact | gate digest | measurement digest |
|---|---|---|
| `<row>/*.rs`, `<row>/model.py`, `<row>/inputs/gen.py`, `<row>/c/*` | ✅ | ✅ |
| `<row>/*.md` | ✅ | ✗ |
| `<row>/controls/*` (not `.json`/`.log`) | ✅ | ✗ |
| `common-php/driver.*`, `common-php/slb.py` | ✅ | ✅ |
| `common-php/*.py` (incl. `digest_bridge.py`) | ✅ | ✗ |
| `common-php/*.h`, `*.c`, `*.rs` | ✗ **bridged only** | ✗ (unless `<row>/c/` symlink — `B1`) |
| `common-php/<real subdir>/*` | ✗ bridged | ✗ |
| ⚠ `common-php/<SYMLINKED subdir>/*` | ✗ **and not bridged either** (`m5`) | ✗ |
| `<row>/*.py` other than `model.py`; `<row>/*.c`/`*.h` outside `c/`; `<row>/inputs/*.py` other than `gen.py` | ✗ | ✗ |
| ⚠ **`harness-php/root.py`, `gate.py`, `provenance.py`** | ✗ | ✗ |
| ⚠ **`patterns-php/php-5.0.0.manifest`, `SOURCES.md`, `manifest.sh`** | ✗ | ✗ |

Two consequences:

- **`digest_bridge.py` is correctly in the digest it maintains (§1.2 answered:
  yes, key `common/digest_bridge.py`, hash `8f693aa5fe34`, verified present in
  `results-php/gate/ph00-smoke.json`) — but the *requirement to run it* lives in
  `harness-php/gate.py`, which is in no digest.** `harness/check.py` can be run
  through the shim directly, and then nothing verifies the bridge at all.
- **`gate.py --no-provenance` leaves no trace.** The record's `invocation` field
  is `check.py`'s `argv`, not `gate.py`'s: `ph00`'s reads `"ph00"`. A record
  taken with provenance skipped is byte-indistinguishable in that field from one
  taken with it checked. The loud line goes to stdout and dies there.
- `provenance.py` consults `patterns-php/php-5.0.0.manifest` to decide whether
  `c_file` is in the corpus. **A tampered manifest changes verdicts and moves no
  hash anywhere.** (`MANIFEST.sha256` covers it, but nothing runs that check.)

Cheap repairs, no harness edit: have `gate.py` write a small
`results-php/gate/<row>.preflight.json` (or extend the bridge to cover
`harness-php/*.py` and `patterns-php/*.manifest`), and check `MANIFEST.sha256`
in the preflight.

---

### 🟡 m1 (minor) ⚙ — `RECAP_PHP.md`'s START HERE box contradicts the four lines under it

`RECAP_PHP.md:29-32`: *"`STATE  NOTHING BUILT` … `patterns-php/ harness-php/
results-php/ .tasks-php/ .memory-php/ common-php/` **DO NOT EXIST YET** — Phase 0
creates them"*, immediately above `RECAP_PHP.md:41-44`: *"`BUILT  TASK_PHP_002
DONE. Phase 0 green`"*. And the "What is true now" table has **two rows both
labelled `infrastructure`** (`:66` *"built: …"*, `:69` *"not yet built — Phase
0"*). The box is the ≤20 lines the document says a reader reads first.

### 🟡 m2 (minor) ⚙ — the mandated `why` paragraph is 11,003 bytes, not 11,004

`RECAP_PHP.md:17` says *"of which **11 004 bytes** is that mandated block"*.
Measured with `check.py`'s own span (`why[find(BEGIN):find(END)+19]`):

```
paragraph len (check.py's own span) : 11003    NAMED_SPELLING_LEN = 11003
tail after paragraph                : '.'
total why chars/words               : 12224 2056     <- both correct
row-specific prefix chars/words      : 1220 200      <- the repaired rule IS satisfiable
```

`PROTOCOL_PHP.md:239` and `ph00-smoke/NOTES.md` both say 11,003 and are right.
This is `PROTOCOL.md` rule 14's shape — the same off-by-one class the manager
corrected in the engineer at `zend_alloc.c:39-43`.

### 🟡 m3 (minor) — `root.py`'s docstring argues its `.temp` decision from a behaviour the code does not have

`harness-php/root.py:56-65` rejects option A because *"This script REBUILDS the
shim by removing and recreating it … so every rebuild would silently delete
every build artefact … underneath it"*, and `:159-162`'s error message repeats
*"the shim is a derived artefact that this script rebuilds"*. Measured
(`.temp/php3/e9_bridge_root.py`):

```
before: scratch marker exists True | stray dir in shim exists True
after  root.py build():
   scratch marker still there : True
   stray dir still there      : True
   root.py --check says       : ["unexpected entries in the shim: ['zzz_stray_dir']"]
   there is no rmtree anywhere in root.py: True
```

`build()` is `makedirs(exist_ok=True)` plus per-link `unlink` only when the
target differs. **Option C is still the right choice** (option B's
`pattern_id` collision hazard is real and I verified the separation holds) —
but the stated reason is fiction, and `check()` catching the stray entry is
what actually protects the shim.

### 🟡 m4 (minor) — `php_shim_tally()`'s documented contract names a field the code does not use

`emalloc_shim.h:116-118` says the tally is *"(allocs, frees, cache_hits,
**bytes_requested_low**)"*; `:444-450` mixes **`bytes_mallocked`**. Those are
the two sides of truncation T1 and they differ by exactly the amount a
truncation defect moves. A row folding the tally into its checksum on the
strength of the doc comment would be folding the wrong quantity.

### 🟡 m5 (minor) — `digest_bridge.py` is blind to a symlinked subdirectory

`.temp/php3/e9_bridge_root.py`:

```
a new top-level .h:                     rc=1  NOT BRIDGED: zzz_probe.h is in no digest at all
a file in a REAL subdirectory:          rc=1  NOT BRIDGED: zzz_sub/payload.h is in no digest at all
a file behind a SYMLINKED subdirectory: rc=0  digest bridge: current
```

`all_files()` uses `os.walk`, which does not follow directory symlinks. The two
cases that matter today fire; this one is the third row of the enumeration in
`M6` and belongs in the docstring.

### 🟡 m6 (minor) — `php_shim_reset()` frees the cache but not the live list

`emalloc_shim.h:218-234` frees every cached block and then sets `head = NULL`
without freeing the list it was heading. The header warns about the cache
(*"a long driver loop leaks the whole cache"*) and not about this. `PLAN_PHP.md`
§1 counts **15 CWE-401 rows**; a leak row driven thousands of times per
measurement will be limited by RSS, not by instruction count — the exact hazard
the cache note exists for, one field over.

### 🟡 m7 (minor) — the rule-6 disclosure table shows two contract states; there were at least three

`ph00-smoke/NOTES.md:5-8` records *as first written* → *as shipped*. The
engineer's own report (`TASK_PHP_002_REPORT.md`, "Building `ph00-smoke`" §1)
describes an intermediate state whose row-specific prose contained the literal
`NAMED-SPELLING STANDARD` and was then reworded. The disclosure is honest and
the shipped hash verifies (`91d88e1e…`, reproduced below); the table just does
not describe the trajectory it claims to.

---

## Evidence — clean negatives (attacks that did NOT land)

**Name them so nobody re-runs them.**

### CN1 ⚠ — the manager's stated expectation is REFUTED: the `common-php/*.h` digest gap DOES fire

`.temp/php3/plant_shim.py` plants `PHP_SHIM_MAX_CACHED_MEMORY 11 → 12` into
`common-php/emalloc_shim.h` — a change that moves which blocks are cached, i.e.
malloc traffic, `Ir`, the tally and whether ASan sees a UAF.

*Arm 1, no `--regen`:*

```
$ python3 harness-php/gate.py --preflight ph00
  FAIL common-php/ digest bridge
PREFLIGHT FAILED -- the tool was NOT run:
  BAD  MOVED: emalloc_shim.h 0d05c94ff579 -> f948347eafa6. Run --regen, ...
  -> exit 2
$ python3 harness-php/gate.py --tool measure --check-stale
PREFLIGHT FAILED -- the tool was NOT run           -> exit 2
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE                     -> exit 0    (correct: not a PAT file)
```

*Arm 2, with `--regen`:*

```
$ python3 common-php/digest_bridge.py --regen        regenerated: 3 bridged file(s)
$ python3 harness-php/gate.py --preflight ph00       preflight OK
$ python3 harness-php/gate.py --tool measure --check-stale
STALE       results/gate/ph00-smoke.json               common/digest_bridge.py
FRESH       results/ph00-smoke.json                    18 source(s) + 8 input(s)
```

**Both mechanisms work.** The gate literally cannot be run behind a drifted
header, and after a `--regen` the gate record goes stale. `digest_bridge.py`'s
own hash is in every php gate record (§1.2: yes). The residual holes are `B1`
(the measurement half) and the boundary condition that all of this is enforced
by `gate.py`, which is in no digest (`M6`), and that the php `--check-stale` is
**not** in `PROTOCOL_PHP.md` §E1 — only the PAT one is, and it does not examine
`results-php/` at all.

### CN2 — the manager's `p01` digest proof re-derives, independently

`.temp/php3/e5_p01digest.py`, with `check.py`'s `srcs` expression **lifted from
its own source text** rather than retyped, against the *committed* record:

```
POSITIVE  (abspath keying, what check.py::main does)
  shim keys 35   committed keys 35
  KEYS IDENTICAL : True      HASHES DIFFERING: none
  only-in-shim: none         only-in-committed: none
NEGATIVE  (realpath keying -- the implementation this rules out)
  KEYS IDENTICAL : False     e.g. ['../../../common/driver.c', ...]
```

### CN3 — the smoke row checks something: a broken proof FAILS the gate

`.temp/php3/e6_mutate_proof.py` weakens `ph00-smoke/verus.rs`'s loop invariant
(`i as int` → `0 as int`) — a mutation that touches **no** clause text `spec.md`
pins, so it tests the proof stage rather than the pin comparison. Seven stages
fired and the gate failed (`.temp/php3/e6_gate.log`):

```
[proof-verify] verus.rs: 5 verified, 2 errors
[proof-rule2]  `verus --verify-function kernel` reports 0 verified
[clause-mut]   the UNMUTATED copy ... does not verify
[req-mut]      ... every mutant below would 'fail' for the wrong reason
[twin]         with `--cfg slb_twin` Verus reports 6 verified, 2 errors
[driver]       verus.rs: ... Verus never verified this file
[miri]         no identity measurement for the R4/R5 pair
check.py: FAIL          GATE EXIT: 1
```

Run as `--skip large`, so the record went to `.temp/php-scratch/gate-partial/`
and the committed `results-php/gate/ph00-smoke.json` was **not** overwritten
(verified: `sha256sum -c` OK on all three `results-php/` artefacts).

### CN4 — the PAT tree really is untouched, with the positive control

`.temp/php3/e8_pat_untouched.py`, and the engineer's own instrument re-run:

```
[baseline] git status --porcelain --ignored -- patterns results harness common pilot
       (only gitignored blobs and __pycache__ dirs)
=== POSITIVE CONTROL ===
[planted]  M harness/vparse.py
MUST-FIRE CONTROL: FIRED  (2220 -> 2221 lines)
RESTORE harness/vparse.py 276191cf6a6d... match=True     restored == baseline: True

$ python3 .temp/php0/pat_snapshot.py .temp/php3/pat_now2.json --diff .temp/php0/pat_after.json
files before 3044  after 3044    ADDED: 0  REMOVED: 0  CHANGED: 0    CLEAN
```

⚠ **And `PYTHONDONTWRITEBYTECODE` held under a real full gate run through the
shim**, which is stronger than the engineer's scratch-module demo:

```
harness/__pycache__ mtimes, AFTER my 05:53 full gate through .temp/php-root/:
   2026-09-02 05:55  asm   2026-09-02 05:35  build   2026-09-03 03:18  check
   2026-09-02 07:55  dloop 2026-09-02 07:55  fixture 2026-09-02 05:57  measure
   2026-09-02 07:55  report 2026-09-02 07:55  vparse        (none is today)
```

§2 asked whether the variable is set on *every* path into the harness: it is —
`gate.py:138-139` sets it once, in the single `subprocess.run` all four tools go
through, and children inherit it. The `common-php/` half is safe for a different
reason: `common-php/` is a **real** directory whose *files* are symlinks, so a
`.pyc` for `slb.py` lands in `common-php/__pycache__/`, never `common/`.
(Confirmed: one appeared there during my own un-guarded import, and `common/`
did not move.)

### CN5 — 66 / 0 STALE, three times, and no eighth shim link

```
python3 harness/measure.py --check-stale          -> 66 record(s) examined, 0 STALE  (×3)
python3 harness-php/gate.py --tool measure --check-stale -> 2 record(s) examined, 0 STALE
```

**No eighth link.** `root.py::_MODULES` is exactly `harness/*.py` (9 files, and
`check.py` never imports or executes anything under `harness/tools/` — verified).
Every path the harness builds outside `REPO` is a toolchain location shared with
the PAT programme by design: `~/tools/llvm`, `~/tools/valgrind`, `~/.cargo`,
`~/.rustup`, `/usr/bin/gcc`, and the `SLB_*` env overrides. No `sys.argv[0]`
derivation exists. The seven links are complete.

### CN6 — `.temp` option C works, and `pilot` really is required

```
.temp/php-scratch/build/  -> docrepro  ph00        (php builds, incl. the pilot fixture)
.temp/build/ | grep ph    -> (none)                (PAT scratch uncontaminated)
```

`harness/fixture.py:31` is `PILOT = os.path.join(REPO, "pilot")` — confirmed, and
`check.py::check_selftests` calls `fixture.ensure()`, so the link is a hard
stage-0 requirement, not a hash question. The php side builds its own six
`docrepro` binaries into `.temp/php-scratch/`; `pilot/` itself is byte-identical
(CN4).

### CN7 — every manager-verified **citation** resolves against the pristine tarball

sha256 `5783e0c0…d6919`, 5595997 B, checked directly. All ✅:

| citation | pristine text |
|---|---|
| `zend_alloc.c:40-44` | `#ifdef ZEND_MM` / `#define ZEND_DISABLE_MEMORY_CACHE 0` / `#else` / `…0` / `#endif` — the manager's `:39-43`→`:40-44` correction is **right** |
| `zend_alloc.c:129` | `unsigned int real_size;` |
| `zend_alloc.c:132` | `#define REAL_SIZE(size) ((size+7) & ~0x7)` |
| `zend_alloc.c:135` | `real_size = REAL_SIZE(size);` |
| `zend_alloc.c:295` | `int final_size = size*nmemb;` — **third truncation confirmed, and the manager's description of it (signed, 32-bit, straight into `_emalloc` at :298 and `memset` at :303) is right, not just the line number** |
| `zend_alloc.h:53` | `unsigned int size:31;` |
| `zend_alloc.c:221-244` | `_safe_emalloc`; guard `:224-237`; `emalloc_rel(lval+offset)` at `:238` — protects against neither |
| `zend_alloc.c:150-168`, `:263-279`, `zend_alloc.h:63` | the size-class cache; `MAX_CACHED_MEMORY 11`; and `_efree:263` really does recompute the index from the **31-bit recorded** `p->size` |
| `zend_ptr_stack.h:44-49` | `zend_ptr_stack_push` with the `erealloc` doubling |
| `zend_hash.h:88` | `typedef Bucket* HashPosition;` |
| `zend_compile.h:285/287` | `IS_CONST (1<<0)` / `IS_VAR (1<<2)` |
| `zend.h:388/391` | `IS_LONG 1` / `IS_ARRAY 4` |
| `zend_compile.c:1196-1197` | the `IS_CONST` + `__clone` compare |

**Zero unearned ticks among the citations.** The four consecutive PAT reviews
that each found an unearned ✅ do not repeat here. The ticks that did not survive
are `M1` (`repo_path_bytes` 20), `m2` (11 004) and `M3` (the allocator-patch
mechanism) — none of them a `file:line`.

### CN8 — the allocator probe and the ASan finding reproduce exactly

Rebuilt from source and re-run: `16 checks, 0 FAILED`, all four `CONTROL:` lines
firing. `env -u LD_PRELOAD` used throughout; grepped for `AddressSanitizer`:

```
uaf-plain  (96 B, cache_index 12 >= 11 -> real free())  exit=1  AddressSanitizer lines=2
    heap-use-after-free ... #0 in arm_uaf_plain common-php/emalloc_probe.c:300
overflow   (T1: 4 GiB+24 -> 24 B)                        exit=1  AddressSanitizer lines=2
    heap-buffer-overflow ... #0 in memset
uaf-cached (24 B, cache_index 3 -> AG(cache))            exit=0  AddressSanitizer lines=0
    uaf-cached: wrote 'X' to a freed block; n_cache_push=1
```

The two UAF arms are identical code differing only in the requested size (96 vs
24), which is what decides cached-vs-freed — so `RECAP_PHP` **F3's mechanism is
demonstrated, not inferred**. And the documented `LD_PRELOAD` trap reproduces:

```
$ ./emalloc_probe_asan uaf-plain          # with the inherited LD_PRELOAD
==942872==ASan runtime does not come first in initial library list...
exit=1   AddressSanitizer lines: 0
```

⚠ Related clean negative: `PLAN_PHP.md` §4.3's **63.5 %** figure is properly
sourced. `san_tests/REPORT.md:55-60` derives it from the `-nocache` build, which
exists *as the control for exactly this*. The `nocache` trees being patched
(`M3`) does **not** undermine it — it is why they exist.

### CN9 — `ph00-smoke`'s pins were not silently rewritten, and the row-specific `why` rule is satisfiable

Running `NOTES.md`'s own published check:

```
keys only in ph00 : ['provenance']      keys only in p01 : []
differing keys    : ['idiom']           idiom subkeys    : ['why']
```

and byte-comparing every non-`.md` file: `model.py`, `safe_naive.rs`,
`safe_naive_verus.rs`, `safe_tuned.rs`, `unsafe.rs`, `verus.rs`, `c/kernel.c`,
`c/kernel.h`, `c/main.c`, `inputs/gen.py` — **all SAME**. So the copied pins
(obligation counts 7/7/8, `identity` `norel`/`exact`, `miri`, the absent `Ir`
floor) are re-derived *by the gate* over byte-identical sources; `.memory/05-layout.md`
step 5's hazard — *"a gate that certifies p01"* — is here the deliberate point,
not an accident. Also verified: `copied_at_commit 4afcef23…` is a real commit and
`git diff 4afcef23 HEAD -- patterns/p01-array-sum/` is empty.

The rule-6 disclosure verifies where it can:

```
p01 gate-spelling  : 5360d6f3dd7a…   == its committed record   ✅
p01 naive-spelling : b5d7dc8dd173…   (matches nothing)
ph00 shipped       : 91d88e1e18b1…   == results-php/gate/ph00-smoke.json  ✅
```

The *first-written* hash `6e20789e…` is, as `NOTES.md` itself says, unverifiable
on a new row — and the file says so instead of citing the vacuous `git show
HEAD:` command. That is the right handling of rule 6's hole.

`ph00`'s `provenance` block does say it in terms:
`"php_provenance": false`, `why` = *"THROWAWAY INFRASTRUCTURE SMOKE ROW — NOT A
PHP ROW. No PHP source, no root_cause_id, no CWE, no fix_commit, no security
claim, no measured result…"* ✅.

And its verdict matches p01's exactly — `PASS-WITH-BLOCKED-ROWS`, 0 failures,
same single blocked Miri row (same `reason` string), same two `loud` sections
(`idiom-forbidden`, `twin`). The 35→28 key difference is the 13 row files, the 8
absent `common/layout/*.py` and the added `common/digest_bridge.py`, exactly as
itemised.

### CN10 — the manifest, the miners' recounts, and rule 10

```
patterns-php/php-5.0.0.manifest  1170 files  109,405 B
MANIFEST.sha256  2047b49d0302…  == sha256 of the manifest        ✅
sh patterns-php/manifest.sh  ->  files 1170  bytes 109405  2047b49d0302…   (byte-identical regen)
```

`.tasks-php/TASK_PHP_001_MINE/temporal/NOTES.md`'s ranked table, recounted:
**23 rows, 11 `verbatim` / 9 `narrowed` / 2 `modelled` / 1 `narrowed/modelled`**,
and the file discloses that rank 21 straddles and is counted `narrowed` → the
published **11/10/2** is right. `asan-logs/` really holds **2534** files (F4).
`grep`ing every `.tasks-php/TASK_PHP_*.md` cited from the php tree: the only
missing one is `TASK_PHP_003_REPORT.md`, i.e. this file, written before anything
cites it.

### CN11 — the provenance validator's ten negatives all fire

Reproduced independently against fixtures outside `patterns-php/`: off-by-one at
either end, a flipped hex digit, a mismatched `extract_cmd`, a wrong file with
the *old* hash, `c_file` absent from the manifest, a wrong `tarball_sha256`, a
bad `tier`, no `provenance` object, and `php_provenance:false` with no `why` —
all REJECT, each with the right message. The `_FENCE` fix holds: a fixture with a
second ```` ```json ```` fence later in the file still parses correctly. It **is**
wired in — `gate.py:90-99` runs it before every tool and refuses on a non-zero
exit — which answers §5's *"a standalone script nobody runs"*. Its two gaps are
`M5`.

---

## Unsure / not done

1. **No php row allocates yet**, so `B1` and `B2` invalidate **no published
   number today**. I rank them blockers because both are cheap now and expensive
   after the first allocating row is measured, and because `B1` is the exact
   determination §1.3 commissioned.
2. **I did not run a full green `gate.py ph00`.** My gate run was
   `--skip large` (PARTIAL, so it could not overwrite the committed record) and
   deliberately mutated. The committed record's own freshness is established by
   `gate.py --tool measure --check-stale` = 2 examined / 0 STALE, which is a
   stronger statement than a re-run would be.
3. **I did not audit `emalloc_shim.h` line-by-line against `_erealloc`'s and
   `_estrndup`'s full bodies** beyond the truncation sites and the control flow;
   I read both against the pristine text and found no further divergence, but I
   did not build differential tests for them the way I did for
   `_safe_emalloc`. `_estrdup` (`zend_alloc.c:374-389`, `int length =
   strlen(s)+1` — a *fifth* narrowing, signed) is not modelled and not claimed.
4. **`ZEND_MM` is unmodelled** and the engineer flagged that nobody has checked
   whether any of the 54 candidates has a defect inside it. Still true; it is a
   Phase-1 adjudication question, not a Phase-0 one.
5. **I did not attack `TASK_PHP_001`'s mining beyond the recounts and the
   citations §0 named.** The candidate lists are unreviewed and remain so.
6. **`.web/`**: I confirmed by reading that `build_data.py` constructs no
   `patterns-php`/`results-php` path, matching the engineer; I ran nothing there.
7. **The `driver.emalloc.h` rename** the engineer left open: I did not evaluate
   it. Note that it would put the shim in **both** digests by name and would
   therefore also close `B1` — which changes the trade-off the engineer's
   rejection was written against.

---

## What I refuted (reconciliation is the manager's job)

Launched from **8**. This review refutes, each with a run:

1. ⚙ *"`repo_path_bytes` is **20** bytes longer through the shim"* — it is **15**,
   and it is not the only domain mover (`M1`).
2. ⚙ *"`REAL_SIZE(size)→(size)` … deletes the very truncation"*, and *"every
   extracted tree … carries modern-gcc **and allocator** patches"* — 7 of 12
   trees have a pristine `zend_alloc.c`, the patch is in **one**, at `:132`, and
   it does not delete the 32-bit truncation (`M3`).
3. ⚙ *"a **mandatory** `<row>/c/` symlink (measurement half)"* — nothing enforces
   it and a row without one builds and gates (`B1`).
4. *"`ZEND_SIGNED_MULTIPLY_LONG` … same predicate"* — 84,523 disagreements in
   20 M samples, all one way (`B2`).
5. *"`root.py --sweep` re-derives the link list"* — it cannot fail for four of
   seven links (`M2`).
6. ⚙ *"the mandated paragraph is 11 004 bytes"* — 11,003 (`m2`).
7. ⚙ *"three commands, not two"* (`ph00-smoke/README.md`, `gate.py`) and
   *"FIVE COMMANDS"* (`PROTOCOL_PHP.md` §E header) — six, as `RECAP_PHP.md` open
   item 11 and the same task's own measurement say (`M4`).
8. ⚙ *"`extract_sha256` … makes 'this kernel came from those lines' a
   one-command check"* — it checks the lines, never the kernel; and an
   out-of-range span passes (`M5`).
9. *"`root.py` rebuilds the shim by removing and recreating it"* — it does not
   (`m3`).

And it **upholds**, with measurements the manager can re-run:

- the symlink-shim mechanism itself (`CN2`, 35/35 keys and hashes, with the
  realpath negative);
- the digest bridge, both arms — **the manager's stated expectation that §1 is
  where this falls over is refuted for the gate half** (`CN1`);
- the seven-link map as complete, and `pilot` as a hard stage-0 requirement
  (`CN5`, `CN6`);
- the no-touch rule in practice — 66/0 STALE ×3 and a byte-identical PAT tree
  after a full gate, 28 builds' worth of scratch and five plants (`CN4`);
- every `file:line` the manager marked ✅ (`CN7`);
- the third truncation, its description, and `zend_alloc.c:40-44` (`CN7`);
- `RECAP_PHP` F3's ASan mechanism, reproduced (`CN8`);
- `ph00-smoke` as a real regression test, not a pipeline demo (`CN3`, `CN9`);
- the miners' 11/10/2 recount and the 2534-file F4 correction (`CN10`).

---

## Memory updates

**None written.** `.memory-php/` does not exist and `.tasks/PROTOCOL.md` rule 4
makes it the manager's; rule 9 says a finding does not enter the authoritative
layer until it has survived review — these findings *are* the review.

Candidates for `.memory-php/`, in priority order:

1. **The php measurement digest does not reach `common-php/` at all**, and the
   `<row>/c/` symlink that closes it is enforced by nothing (`B1`). Write this
   before the first allocating row, not after.
2. **`emalloc_shim.h`'s `_safe_emalloc` is not faithful** until the pristine
   `ZEND_SIGNED_MULTIPLY_LONG` is pasted in (`B2`) — and, generally, *"modelled
   by an equivalent builtin" is a claim that needs a differential test, not a
   comment*.
3. **Two domain terms move through the shim, not one**: `repo_path_bytes` +15
   **and** `envp_stack_bytes` +33 / `nvars` +1, the latter caused by `gate.py`'s
   own `PYTHONDONTWRITEBYTECODE=1` (`M1`).
4. **A php gate record does not record whether its preflight ran**, and
   `harness-php/*.py` is in no digest (`M6`).
5. **The php staleness check is `gate.py --tool measure --check-stale`, and it
   is not in `PROTOCOL_PHP.md` §E1** — the mandated 66/0 check does not examine
   `results-php/` at all.
6. **Build trees are ~99.9 % pristine**: 1169/1170 manifest files identical in
   the `.app-tests` trees, the movers being `Zend/zend_modules.h` everywhere and
   `Zend/zend_alloc.c` in three san_tests variants (two `cache-off`, one
   `REAL_SIZE` identity, one ASan-poison). The citation rule stands; the reason
   changes (`M3`).
