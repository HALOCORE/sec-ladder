# TASK_PHP_054 — REPORT, agent **B**: families **E5 · E6 · E7 · E8** (`ph77`–`ph91`)

**Role:** research investigator. **Deliverable: a ranked shortlist with evidence,
not a decision.** Nothing in `patterns-php/`, `RECAP_PHP.md`, `.memory-php/`,
`harness/`, `common/`, `patterns/`, `results/`, `pilot/`, `common-php/` or
`.web/` was edited; no `git add`/`git commit`. Scratch: `.temp/php54B/`
(`NOTES.md` there re-derives every artefact).

---

## §0 ⭐ WHAT IS NEW IN THIS REPORT, IN FOUR LINES

1. ⭐⭐⭐ **The C-side bar is not argued here, it is MEASURED.** There is a working
   **PHP 5.0.0 CLI** on this box, and the corpus ships a **reproducer per id**.
   I ran **36 corpus reproducers** (every id in E5–E8 that has one) and **18 of
   my own transcriptions of the catalogue's `▸ trigger` lines**, under an
   `LD_PRELOAD` that prints `si_addr`. **14 of the 36 corpus reproducers
   SIGSEGV** — count it: `grep -ac 'rc=139' .temp/php54B/corpus_repro.log`.
2. ⭐⭐⭐ **`ph90`'s faulting address is `0x10`** = `offsetof(zval, refcount)` on
   x86-64 — a **deterministic NULL-pointer write**, on the corpus's own
   reproducer and on three of mine, including a **one-element** array.
3. ⭐⭐⭐ **`ph90`'s `fix_commit` column is wrong for its own cited site**, and I
   found the right commit: **`0542a6f2c2a5`** (2005-02-10, Rob Richards,
   *"MFH: fix segfault in array_walk when retval_ptr is empty - such as when
   exception thrown"*) — **1 file, 3 insertions, 1 deletion, at `array.c:1045-1046`
   exactly, and it applies to the pristine tarball with `git apply` strict,
   bytes verified moved.**
4. ⭐⭐ **All five R1h patches I tested apply CLEANLY to pristine 5.0.0** —
   `ph55` needed a hand backport and a whole control to record the failure;
   none of these does.

---

## §0.5 ⛔ THE MANAGER'S MID-TASK ALERT — CHECKED INDEPENDENTLY, AND AGENT A IS **RIGHT**

The manager relayed agent A's finding that **3 of the 163 patches cached under
`.temp/mgr/batch/patches/` are stored under a sha the file itself does not
carry**, naming `ph78` and `ph79` as mine, and instructed me to **check the
binding myself rather than adopt the claim**. I did.

**The test I ran** (`.temp/php54B/patch_binding.py`, log alongside it): for
**every id of every row in ph77–ph91**, take the `fix_commit` from `index.csv`,
open the cached file, and compare the **file's own `From <40-hex-sha>` header**
against the sha the filename claims. **44 records checked.**

```
mismatches in ph77..ph91: 2
```

| row | id | filename claims | the file's own `From` header says | subject |
|---|---|---|---|---|
| **ph78** | **CRASH-159** | `abb09693ac4d` | ⛔ **`6a6c27389317`** | *"Fixed bug #66609 (php crashes with `__get()` and ++ …)"* |
| **ph79** | **LOGIC-025** | `49bd45a2c175` | ⛔ **`bc9f2fb8dfad`** | *"Fixed bug #69212"* |

✅ **A's claim is INDEPENDENTLY REPRODUCED for both of my rows**, by a different
route (A read the live fetch; I read the cached bytes' own header). **42 of 44
bind correctly.**

⭐ **ONE NARROWING A DID NOT HAVE, offered and not pursued** (the manager said
the tool is his to route, so I stop here): **both of my mismatches carry the
RIGHT BUG in their subject line** — `#66609` is exactly what `CRASH-159` is
about and `#69212` exactly what `LOGIC-025` is. So the defect looks like a
**sha↔file binding** error over *the same change on another branch* (an MFH /
cherry-pick twin), **not** an unrelated patch landing under the wrong name. ▶ If
that holds, the *contents* may well still be the right repair while the *id* is
wrong — which is a different and cheaper repair than a refetch of everything,
and it is testable by diffing the two shas.

### ▶ WHAT THIS TOUCHES IN THIS REPORT — the exhaustive list

⭐⭐ **NOTHING IN §4 (the deep verification) IS AFFECTED.** All six patches
behind my four deep checks bind correctly — `ph81`/`8df40bdb313d`,
`ph81`/`1088e28dfa6a`, `ph85`/`196e54fc43dd`, `ph87`/`1ea22c90046b`,
`ph87`/`3e0680f2ee00`, `ph90`/`32c2e664a6ec` — and so does the patch I fetched
myself, `0542a6f2c2a5` (its first line is
`From 0542a6f2c2a5f5264f56a85bae1bf4bf202a20e1`). **Every §4 claim stands.**

| statement in this report | rests on a mis-keyed patch? |
|---|---|
| `ph78`'s and `ph79`'s **`n ids → n distinct commits`** (7→7, 5→5) | ❌ **No** — derived by `.temp/php54B/ids2commits.py` from `index.csv`'s `fix_commit` column, which never reads the cache |
| `ph78`'s / `ph79`'s R1h cells in §3 (*"2008 · 2f · same"*, *"2005 · 3f · same"*) | ❌ **No** — those are `CRASH-042`/`41ad9b4d1fdd` and `CRASH-038`/`6319efa013ec`, both **OK** above |
| §5's DEAR verdicts on `ph78`/`ph79` | ❌ **No** — they rest on the ids→commits counts and on the entries' own risk lines |
| any `preimage_screen.py` outcome for `ph78`/`ph79` | ❌ **Not quoted** — I ran the screen only on `ph81`, `ph85`, `ph87`, `ph90` |
| any statement about what `abb09693ac4d` or `49bd45a2c175` **contains** | ❌ **Not made** — I did not read either patch's body, and §3.5's crash table for those two ids is a **run of the corpus reproducer**, not a patch read |

⚠ **What IS now marked UNVERIFIED**: `fixsurvey.py --offline`'s "fix touches"
file-lists for `ph78`/`CRASH-159` and `ph79`/`LOGIC-025` in its OTHER-FILE
table, because that column is computed from the mis-keyed bytes. **I do not
quote those two cells anywhere in this report**, and anyone who later screens
`CRASH-159` or `LOGIC-025` should treat the result as meaningless — not
wrong-in-a-known-direction — until the cache is repaired.

---

## §1 ROW COUNT — printed and reconciled (§3.1's ⛔)

```
$ sed -n '997,1110p' patterns-php/CATALOGUE.md | grep -ac '^\*\*ph'
15
$ sed -n '997,1110p' patterns-php/CATALOGUE.md | grep -ao '^\*\*ph[0-9]*'
ph77 ph78 ph79 ph80 ph81 ph82 ph83 ph84 ph85 ph86 ph87 ph88 ph89 ph90 ph91
```

`python3 .tasks-php/quota.py` per-family `n`: **E5 5 · E6 4 · E7 3 · E8 3 = 15**.
✅ **Reconciled. 15 of 15 rows are in the Stage-1 table below.**
(⚠ `ph91`'s Part B block has no `·`-delimited citation line — it is a prose
block. `grep -ac '^\*\*ph'` still finds it; a regex keyed on the `—` separator
would not. That is F35's class one more time and it is why the count command in
§3.1 is the right one.)

---

## §2 ⛔ WHAT IS MEASURED AND WHAT IS READ — the honesty boundary

| claim class | how I got it | strength |
|---|---|---|
| every `file:line` in every entry | **read from the pristine tarball** (`sha256 5783e0c0…d6919`, verified before extraction) and **quoted** below | strong |
| "this input crashes 5.0.0" | **run** on a built PHP 5.0.0 CLI, `si_addr` captured | strong for PRESENCE |
| "this input does not crash" | same run | ⛔ **NOT evidence of absence** — `RECAP_PHP.md` **F3**, and the oracle build is `-O3 -march=native -flto`, mysql+webext, **not** a museum-default build |
| "the R1h applies / does not apply" | `git apply` in a **standalone `git init` repo**, verdict taken from the **BYTES** not the exit status (`ph55` NOTES §5's gitignore trap) | strong |
| "the hardened build still crashes" | **NOT MEASURED** — I cannot rebuild PHP 5.0.0. Derived from the applied post-image + a measured one-element crash. Labelled everywhere it appears. | inference |

⚠ **No gdb and no working memcheck on this box** — valgrind 3.27.1 refuses to
start memcheck (*"a function redirection which is mandatory … memcmp … in
ld-linux-x86-64.so.2 … cannot be set up"*, needs glibc debuginfo). I wrote two
`LD_PRELOAD` shims instead: `segaddr.so` (SIGSEGV `si_addr`) and `maxrss.so`
(`getrusage`). Both are in `.temp/php54B/` with their sources.

---

## §3 STAGE 1 — all 15 rows, from their OWN Part B entries

`needs` ticks: **Z**vals · **A**llocator · **H**ashTable · **V**M/executor ·
**U**serland re-entry · **G**arbage (uninitialised memory) · **P**recomputation
(hash preimage etc.) · **F**ailure injection · **2+** more than one subsystem.
`R1h` = year · files · same-file? · **ids→commits** (derived by
`.temp/php54B/ids2commits.py`, which reads **all three** id namespaces —
`fixsurvey.py`'s summary only prints rows with ≥3 distinct commits).

### E5 — the VM's own bookkeeping

| row | tier | defect site (as the entry gives it) | harm | needs | determ.? | observable by | R1h | measured |
|---|---|---|---|---|---|---|---|---|
| **ph77** | narrowed | `Zend/zend_execute.c:63-78` (+ `:374-381`, `:500-538`, `:196-218`, `:3152-3170`) | **OOB write** (`garbage[2]`, `garbage_ptr++` unchecked) **+** UAF, two limbs | Z A V | yes for the bump; the UAF limb depends on what `garbage[]` overruns into | ASan / a `(refcount, garbage_ptr)` fold | 2008 · 4f · same · **5 ids → 5 commits** | 2 of 5 corpus reproducers SIGSEGV (`CRASH-057` `si_code=128 si_addr=nil`; `CRASH-050` wild) |
| **ph78** | narrowed | `Zend/zend_object_handlers.c:264-296` | **UAF-write** (`zobj->in_get = 0` at `:294`) | Z A H V U | yes given the callback | ASan | 2008 · 2f · same · **7 ids → 7 commits** | 2 of 7 SIGSEGV; `CRASH-042` itself clean |
| **ph79** | narrowed | `Zend/zend_execute_API.c:718-728` | **UAF-read** of a freed `zend_function` at `:733` | Z A H V U | yes | ASan / a resolved-id fold | 2005 · 3f · same · **5 ids → 5 commits** | **3 of 5 SIGSEGV** (`CRASH-038`, `-031`, `-072`) |
| **ph80** | narrowed | `ext/standard/basic_functions.c:1325-1385` | **UAF-read** of an `efree`d buffer still in `environ[]` | A H 2+ (libc `environ`) | ⚠ depends on what `unsetenv` did first (see §7) | ASan / `(allocs, frees)` | 2014 ⚠late · 2f · same · **4 ids → 4 commits** | `CRASH-084` itself **clean**; 2 of 4 siblings SIGSEGV |
| **ph81** | verbatim | `Zend/zend_execute.h:117-127` | **UAF-read + double free**; also a **silent wrong answer** | Z A V (U for `CRASH-142`) | ⭐ **yes, and measured both ways** | ⭐ stdout divergence **and** SIGSEGV | 2006 · 2f · same · **2 ids → 2 commits** | ⭐ `CRASH-142` SIGSEGV; `CRASH-140` prints a **wrong backtrace** |

> **entry's own ⚠ risk, quoted**
> `ph77` — *"⚠⚠ risk: **two limbs, and both must be declared** (adjudication §2 item 5). … the unchecked `garbage_ptr++` on a 2-element array is a **real spatial defect of the same C** and must be declared as a second limb with the oracle able to say which fired. ⚠ **Do not bound it**"*
> `ph78` — *"⚠ risk: the **write** at `:294` is what makes CRASH-042 sharper than a read-only UAF. Keep it."*
> `ph79` — *"⚠ risk: **the whole defect is that the two kinds are the same C type.** An extraction that tags them has fixed it."*
> `ph80` — *"⚠ risk: an owning hashtable with a destructor plus a **borrowing array of raw pointers**; `environ` is a second array. Nothing from libc is needed — and importing real `putenv` makes the row unmeasurable."*
> `ph81` — *"⚠ risk: eleven lines; needs only a slot array and a release callback."* ⭐ **the shortest risk line in my 15**

### E6 — allocation not released on every path that leaves the block

| row | tier | defect site | harm | needs | determ.? | observable by | R1h | measured |
|---|---|---|---|---|---|---|---|---|
| **ph82** | modelled | `Zend/zend_execute.c:4235-4265` | **leak** (a loop temp's lock never released on the unwind path) | Z A V F | yes | `(allocs, frees)` / a refcount fold | 2005 · 1f · ⚠**OTHER file** · **9 ids → 9 commits** | no crash; reproducer's own note: *"Observed on the ZEND_DEBUG 5.0.0 build"* |
| **ph83** | narrowed | `Zend/zend_execute.c:986-987`, `:448-452` | **leak** — an unbalanced `PZVAL_LOCK` | Z V 2+ (the compiler sets `EXT_TYPE_UNUSED`) | ⭐ **yes, measured** | ⭐ **stdout**: `debug_zval_dump` shows `refcount(1005)` after 1000 unused reads | 2011 ⚠late · 8f · ⚠**OTHER** · **2 ids → 2 commits** | ⭐ refcount inflation visible; no crash |
| **ph84** | narrowed | `Zend/zend_execute.c:3142-3146` | **leak** of an object-store ref **+ a type-confusion wrong answer** | Z A V 2+ (object store) | ⭐ **yes, measured, on both limbs** | ⭐ **stdout**: destructor order **and** *"Cannot break/continue **7** levels"* | 2010 ⚠late · 5f · same · **1 id → 1 commit** | ⭐ both limbs fire |
| **ph85** | narrowed | `Zend/zend_execute.c:914-926` (corpus: `:924`) | **leak** of a 1-byte string buffer | Z A | ⭐ **yes, measured, linear, two flat controls** | `(allocs, frees)` / RSS | **2005 · 1f · same · 1 id → 1 commit** ⭐ | ⭐ **~47 B/iteration**, controls flat |

> **entry's own ⚠ risk, quoted**
> `ph82` — *"⚠ risk: `modelled` — genuinely needs a loop construct with an unwind path. **Split from ph83/ph84/ph85** (adjudication §2 item 6): one `I6` invariant over four C shapes is a taxonomy, not a mechanism."*
> `ph83` — *"⚠ risk: both rows also appear in ph77's member list as *sites*; here they are the **mechanism**. Say which reading a build takes."*
> `ph84` — *"⚠ risk: a pure leak — invisible to a checksum unless `(allocs, frees)` is in the `u64`. This row is the strongest argument for that convention."*
> `ph85` — *"⚠ risk: sits between the leak family and ph39's tag family. Cross-reference both; catalogued here because the *harm* is the leak."*

### E7 — the compiled program's metadata is wrong

| row | tier | defect site | harm | needs | determ.? | observable by | R1h | measured |
|---|---|---|---|---|---|---|---|---|
| **ph86** | narrowed | `Zend/zend_compile.c:885-899` | a **wrong liveness mark** → later UAF / double free | V 2+ (**two passes**: a marker and an interpreter) | unknown to me | a fold of the marked opcode indices | 2005 · 2f · same · **2 ids → 2 commits** | ⚠ **neither reproducer crashes** — F3, not absence |
| **ph87** | verbatim | `Zend/zend_constants.c:310-326` | **UAF-read** — a released buffer formatted into the message | A (+H only as "did the insert fail") | ⭐ **fault yes, measured 50/50; VALUE no** (§4.3) | ⭐ **stdout** (the constant's name is garbage) + ASan + `(allocs, frees)` | **2004 · 1f · same · 2 ids → 2 commits, but only ONE is in the defect's file** ⭐ | ⭐ 50 of 50 duplicate defines emit a corrupted name |
| **ph88** | narrowed | `Zend/zend_execute_API.c:282` | **UAF-call** through a destroyed stream's `closer` | A H 2+ (**3 subsystems**: resources, compiler, streams) | unknown to me | ASan / a teardown-order fold | 2007 · 3f · ⚠**OTHER** · **1 id → 1 commit** | reproducer prints the fix's own symptom (*"Class declarations may not be nested"*), **no crash** |

> **entry's own ⚠ risk, quoted**
> `ph86` — *"⚠ risk: ⚠ the one candidate whose natural kernel is **two passes** — a marking pass and a tiny interpreter. Budget for both."*
> `ph87` — *"⚠ risk: ⚠ **the temporal miner retracted a claim of its own here, unprompted** — it first called `free(c->name)` an allocator mismatch, then killed that: every `c->name` comes from `zend_strndup`, so libc `free` is correct. Do not re-derive the retracted claim."*
> `ph88` — *"⚠ risk: **split from ph87** (adjudication §2 item 6) — the miner itself called this *"the weakest merge in this set"*; teardown-ordering shares only the error-handler framing."*

### E8 — routed between axes and never picked up

| row | tier | defect site | harm | needs | determ.? | observable by | R1h | measured |
|---|---|---|---|---|---|---|---|---|
| **ph89** | narrowed | `Zend/zend_execute_API.c:733-745` + `Zend/zend.c:955-957` | **wild-pointer deref** (corpus's `category`) | Z A H V U | yes given the handler | ASan / SIGSEGV | 2005 · 2f · ⚠**OTHER** · **1 id → 1 commit** | ⭐ SIGSEGV at a **wild** address; a by-value 5th arg is clean (my control) |
| **ph90** | verbatim | `ext/standard/array.c:1045-1046` | ⭐ **NULL-pointer WRITE** (CWE-476) | Z A H V U (≤3 at `narrowed`) | ⭐⭐ **yes — garbage-independent, allocator-independent, ASLR-independent** | ⭐ **SIGSEGV at `si_addr=0x10`** | **2005 · 1f · same-file · 1 id → 1 commit** — ⚠ **after correcting the column, §4.4** | ⭐⭐ **4 of 4 inputs SIGSEGV at `0x10`**, incl. a **1-element** array |
| **ph91** | — | ⚠ **label vs citation disagree** | ⛔ see §6 | — | — | — | 2009 · 2f · same · **1 id → 1 commit** | ⭐ corpus reproducer SIGSEGV at **`si_addr=0x20`**, the exact address its own comment predicts |

> **entry's own ⚠ risk, quoted**
> `ph89` — *"⚠ risk: routed to temporal by the type miner and **picked up by nobody** (adjudication §3d). Note it cites the same lines as ph47's caller half — the *type-side* reading of `:730-753` is ph47; this is the *temporal* one. Two readings of one region; keep both, cross-referenced."*
> `ph90` — *"⚠ risk: routed to temporal by the type miner and **picked up by nobody**. Distinct from ph60 in that the guard **is** present and tests the wrong proposition (\"the call completed\" vs \"the call produced a value\")."* ⭐ **that clause is exactly right and it is the row**
> `ph91` — *"⚠ **Third suspect corpus label found by this task** … Settling it needs the reproducer run, which this task did not do."*

### 3.5 ⭐ THE RAW CRITERION-2 EVIDENCE — all 36 corpus reproducers, one line each

Built PHP 5.0.0 CLI, `LD_PRELOAD=segaddr.so`, `timeout 15`. Full output:
`.temp/php54B/corpus_repro.log`. **`rc=139` = SIGSEGV.**

| row | id | rc | `si_addr` | note |
|---|---|---|---|---|
| ph77 | CRASH-151 | 0 | — | warns and completes |
| ph77 | **CRASH-057** | **139** | `(nil)`, `si_code=128` | SI_KERNEL — not a plain bad address |
| ph77 | **CRASH-050** | **139** | `0x55a1e1bbbea8` | wild |
| ph77 | LOGIC-011 | 0 | — | ⭐ prints `refcount(1005)` — visible leak |
| ph77 | LOGIC-022 | 0 | — | prints the refcount ladder |
| ph78 | CRASH-042 | 0 | — | the row's own id does **not** fire |
| ph78 | CRASH-035 | 0 | — | |
| ph78 | **CRASH-064** | **139** | `0x558800000001` | wild |
| ph78 | CRASH-010 | 0 | — | |
| ph78 | **CRASH-132** | **139** | `0x55801c9fc780` | wild |
| ph78 | CRASH-113 | 0 | — | |
| ph79 | **CRASH-038** | **139** | `0x564c00000000` | ⭐ the row's own id fires |
| ph79 | **CRASH-031** | **139** | `0x558cffffffff` | wild |
| ph79 | **CRASH-072** | **139** | `0x55febff8c` | wild |
| ph79 | LOGIC-025 | 0 | — | |
| ph80 | CRASH-084 | 0 | — | ⚠ the row's own id does **not** fire (§9.2) |
| ph80 | CRASH-092 | 0 | — | |
| ph80 | **CRASH-114** | **139** | `(nil)` | |
| ph80 | **CRASH-141** | **139** | `0x55ee245afedc` | wild |
| ph81 | **CRASH-142** | **139** | `0x564078eb5531` | ⭐ the row's own id fires |
| ph81 | CRASH-140 | 0 | — | ⭐ **wrong answer in stdout**: `#1 eval(1, 2, 3)` |
| ph82 | LOGIC-002 | 0 | — | leak; reproducer says *"Observed on the ZEND_DEBUG build"* |
| ph82 | LOGIC-009 | 0 | — | |
| ph82 | LOGIC-012 | 0 | — | |
| ph83 | LOGIC-011 | 0 | — | ⭐ **`refcount(1005)` after 1000 unused reads** |
| ph83 | LOGIC-022 | 0 | — | |
| ph84 | LOGIC-015 | 255 | — | ⭐ **both limbs fire**: deferred `DTOR bad`, and *"Cannot break/continue **7** levels"* |
| ph85 | LOGIC-006 | 0 | — | leak; measured by RSS instead (§4.2b) |
| ph86 | CRASH-065 | 0 | — | ⚠ neither id fires |
| ph86 | CRASH-024 | 0 | — | |
| ph87 | CRASH-068 | 0 | — | ⚠ silent only because default `error_reporting` hides `E_NOTICE`; with `E_ALL`, **50/50 corrupted** (§4.3b) |
| ph87 | **CRASH-129** | **139** | `0x556c5d244aa0` | the `php_mbregex` sibling |
| ph88 | CRASH-062 | 255 | — | prints the fix's own symptom, no crash |
| ph89 | **CRASH-034** | **139** | `0x65320c9ae77` | ⭐ wild; my by-value control is clean |
| ph90 | **CRASH-029** | **139** | ⭐⭐ **`0x10`** | = `offsetof(zval, refcount)` |
| ph91 | **CRASH-071** | **139** | ⭐ **`0x20`** | the address its own reproducer comment predicts |

**14 of 36 SIGSEGV.** ⚠ Every `rc=0` above is **NOT evidence of absence** (F3),
and the build is `-O3 -march=native -flto`, not a museum default.

---

## §4 STAGE 2 — DEEP VERIFICATION, one per family

### 4.1 E8 — **`ph90`** (the top candidate in my whole set)

**(a) Every cited `file:line`, quoted from the pristine tarball.**

`ext/standard/array.c` — the catalogue's code block is **character-for-character
correct**:

```
1044  			/* Call the userland function */
1045  			if (zend_call_function(&fci, &BG(array_walk_fci_cache) TSRMLS_CC) == SUCCESS) {
1046  				zval_ptr_dtor(&retval_ptr);
1047  			} else {
```

Three more lines the entry does **not** cite and the build task needs:

```
 996  		  *retval_ptr,			/* Return value - unused */      <- no initialiser
1039  			fci.retval_ptr_ptr = &retval_ptr;
1042  			fci.no_separation = 0;
```

`Zend/zend_execute_API.c`, `zend_call_function` (`:554`):

```
 592  	/* we may return SUCCESS, and yet retval may be uninitialized,
 593  	 * if there was an exception...
 594  	 */
 595  	*fci->retval_ptr_ptr = NULL;
...
 870  	if (EG(exception)) {
 871  		zend_throw_exception_internal(NULL TSRMLS_CC);
 872  	}
 873  	return SUCCESS;
```

`Zend/zend_execute_API.c`, `_zval_ptr_dtor` (`:384`):

```
 389  	(*zval_ptr)->refcount--;            <- no NULL test
```

⛔ **FINDING — the catalogue's second clause is FALSE.** The entry says *"on that
path `retval_ptr` was never written"*. **It is written**, to `NULL`, at
`zend_execute_API.c:595`, by a statement whose own comment names the hazard.
The harm is a **NULL dereference**, which is also what the corpus itself says:
`cwe = CWE-476`, `category = null-deref`. ▶ **The row is stronger for it** —
a NULL deref is garbage-independent where an unwritten pointer is not — but
under `PROTOCOL_PHP.md` §G2 (*"stop on kind, not on count"*) this is a
correction that **changes what the row claims**.

**(b) The `▸ trigger` line: `"an array_walk callback that throws."` — VERIFIED.**

Measured, on the built PHP 5.0.0 CLI with `segaddr.so`:

| input | result |
|---|---|
| the corpus's own `input/crash/CRASH-029.php` (3 elements, throws on #1) | **SIGSEGV `si_code=1 si_addr=0x10`** |
| mine, 3 elements, throws on #2 | **SIGSEGV `si_addr=0x10`** |
| mine, 3 elements, throws on every element | **SIGSEGV `si_addr=0x10`** |
| ⭐ mine, **1 element**, throws on it | **SIGSEGV `si_addr=0x10`** |
| control: 3 elements, callback returns normally | **clean, `rc=0`** |

`0x10` is `offsetof(zval, refcount)` on x86-64 (`zvalue_value` is a 16-byte
union). ▶ **The measured faulting address IS the line `zend_execute_API.c:389`
predicts.** Corpus `crashes_pristine_5_0_0 = True` — independently confirmed.

**(c) The R1h, read as bytes. ⛔ AND THE COLUMN IS WRONG.**

`preimage_screen.py --row ph90` → **`INAPPLICABLE`**, 1 record.
⛔ Per **F68 / F95** that is **not an exclusion and says NOTHING about the
commit** — it is `INAPPLICABLE` because `32c2e664a6ec` does not touch
`ext/standard/array.c` at all. I do not cite it as evidence either way.

What `32c2e664a6ec` **actually changes** (from the cache,
`.temp/mgr/batch/patches/32c2e664a6ec.patch`; Marcus Boerger, 2005-03-19,
1 file, 4 insertions, 0 deletions): it inserts, at the **top of
`zend_call_function`**,

```c
+	if (EG(exception)) {
+		return FAILURE; /* we would result in an instable executor otherwise */
+	}
```

I applied it to the pristine file and read the post-image: the guard lands at
`:573-575`, `*fci->retval_ptr_ptr = NULL;` still stands at `:599`, and
`return SUCCESS;` at the exit is untouched.

⛔⛔ **THEREFORE IT CANNOT BE THE REPAIR OF `array.c:1046`.** It guards *entry
with an exception already pending*. My **one-element** measurement shows the
crash happens with **no re-entry at all**: the first and only
`zend_call_function` is entered with `EG(exception) == NULL`, the callback
throws inside it, and the function still returns `SUCCESS` with
`retval_ptr == NULL`.
⚠ **This half is an INFERENCE, not a measurement** — I cannot rebuild PHP 5.0.0
to run the hardened binary. What is measured is (i) the one-element crash and
(ii) the applied post-image.

⭐⭐⭐ **AND I FOUND THE COMMIT THAT IS THE REPAIR.** Fetched 2026-09-15 (the
cache did not have it) from the GitHub API, branch `PHP-5.0`, path
`ext/standard/array.c`:

> **`0542a6f2c2a5`** — Rob Richards, **2005-02-10** — *"MFH: fix segfault in
> array_walk when retval_ptr is empty  - such as when exception thrown"*
> **1 file · 3 insertions · 1 deletion**

```diff
 			if (zend_call_function(&fci, &BG(array_walk_fci_cache) TSRMLS_CC) == SUCCESS) {
-				zval_ptr_dtor(&retval_ptr);
+				if (retval_ptr) {
+					zval_ptr_dtor(&retval_ptr);
+				}
 			} else {
```

✅ **It applies to the pristine tarball**: standalone `git init` repo,
`git apply` **strict** (no `-C1`, no `--3way`), `rc=0`, **bytes verified
moved**, post-image at `:1045-1049`. Its hunk is **at the cited lines**, its
context is 5.0.0's verbatim, it is **same-file**, it is **one month EARLIER**
than the column's commit, and its subject names the trigger.

▶ **That is `PROTOCOL_PHP.md` §G1's warning firing on a real row**: *"the column
names **a** fix for the row's function, NOT necessarily the one that removes the
5.0.0 defect."* The R1h **decision** is therefore trivial once the manager
accepts the correction — and **it is a decision, so I flag it, I do not take
it.**

**(d) ⭐ Does the fix look like a CENSUS? — the answer is IN THE 5.0.0 FILE
ITSELF, and it is the `ph55` signature.**

`0542a6f2c2a5` touches one site. But **pristine 5.0.0's own
`ext/standard/array.c` has FIVE `zend_call_function` call sites and FOUR of
them already test the out-parameter**:

| line | function | guard |
|---|---|---|
| `:559-560` | `php_array_user_compare` | `== SUCCESS **&& retval_ptr**` ✅ |
| `:1045-1046` | `php_array_walk` | ⛔ **nothing** |
| `:3842` | `array_reduce` | `== SUCCESS **&& retval**` ✅ |
| `:3922` | `array_filter` | `== SUCCESS **&& retval**` ✅ |
| `:4085` | `array_map` | `if (**!**zend_call_function(…) == SUCCESS && result)` ⚠ present, with a **precedence bug** — that is **`ph59`'s** mechanism (`CRASH-082`), at a fifth site in the same file |

⭐⭐ **Four of five sites in one file shout the invariant; the fifth is silent.**
That is verbatim `ph55`'s finding (*"the codebase shouts the invariant at the
two sites that get it right, and is silent at the site where it became
conditional"*), measured here on a different file and a different mechanism.
**It gives the row an upstream-authored in-file control for free**, and it
answers "was this a known idiom in 2004?" with a documented yes.

**Cost of the `needs` ticks, honestly.** At `verbatim` the row drags Z A H V U.
At `narrowed` it needs only **Z A U**: a refcounted cell, a callee that returns
a status and writes an out-parameter, and a "the callee threw" bit in the blob —
the HashTable becomes the flat blob and the VM becomes that bit.
⚠ **`PROTOCOL_PHP.md` §B1a's O(1) precondition FAILS**: `php_array_walk`
`MAKE_STD_ZVAL(key)`s and `zval_ptr_dtor`s **per element**, so allocations are
O(n) per kernel call — `ph64`'s situation. **A finding to declare, never a
kill** (§B1a decision 1).

---

### 4.2 E6 — **`ph85`**

**(a) Cited lines, quoted.** `Zend/zend_execute.c`, inside
`zend_fetch_dimension_address`:

```
 914  	if (container->type==IS_NULL
 915  		|| (container->type==IS_BOOL && container->value.lval==0)
 916  		|| (container->type==IS_STRING && container->value.str.len==0)) {
 917  		switch (type) {
 918  			case BP_VAR_RW:
 919  			case BP_VAR_W:
 920  				if (!PZVAL_IS_REF(container)) {
 921  					SEPARATE_ZVAL(container_ptr);
 922  					container = *container_ptr;
 923  				}
 924  				array_init(container);
 925  				break;
 926  		}
```

✅ Exact. The corpus is more precise than the catalogue here and names `:924`
alone; `array_init(container)` with **no `zval_dtor` before it** is the defect,
on a container that still owns a heap string buffer.

**(b) The `▸ trigger` line: ⛔ WRONG AS WRITTEN.**

The entry says *"an assignment that retypes a live string slot to an array."*
Transcribed literally that is `$x = ""; $x[0] = 1;` — **and it leaks nothing**,
because at 5.0.0 the literal `""` is the shared `empty_string` global. The
corpus's own reproducer says so in an `NB`. Measured, `maxrss.so`, same binary,
three scripts, three sizes:

| script | N=1 000 | N=200 000 | N=1 000 000 |
|---|---|---|---|
| **defect** — `$t = "" . ""; $t[0] = 1;` | 5 904 KiB | **15 500** | **52 656** |
| control — container already an array | 5 900 | 6 532 | 5 912 |
| control — bare `""` (the **shared** `empty_string`) | 5 928 | 5 928 | 5 904 |

Slope: **(52 656 − 5 904)/10⁶ = 46.8 B/iteration**;
**(15 500 − 5 904)/2·10⁵ = 48.0 B/iteration.** Linear, and **both controls are
flat**. ▶ **The leak is real, unbounded and per-operation**; the trigger needs
an **engine-produced** empty string (`"" . ""` goes through
`concat_function`, `Zend/zend_operators.c:1181`, and carries a real 1-byte
`emalloc`'d buffer). ⭐ **This is F46's class, caught before a build task
started**: an engineer following the `▸ trigger` line verbatim gets a flat line
and concludes the row is dead.

**(c) The R1h.** `preimage_screen.py --row ph85` → **`CANDIDATE`**, 1 record.
Per F68 that means only *"could not exclude"*; I do not quote it as
confirmation. What the patch **actually changes** (Sara Golemon, 2005-09-12,
**1 file, 1 insertion, 0 deletions**):

```diff
 					SEPARATE_ZVAL(container_ptr);
 					container = *container_ptr;
 				}
+				zval_dtor(container);
 				array_init(container);
 				break;
```

⭐ **A single inserted line, and its three context lines are pristine 5.0.0's
`:921-923` character for character.** ✅ Applies to the tarball, `git apply`
strict, bytes moved. **The cleanest R1h in either programme alongside `ph87`'s.**
⚠ Subject is *"Plug leak of 1/2 bytes when converting from string/**unicode**"*
and is an `MFH(r-1.719)` — the 1/2 byte spread is `char` vs `UChar` on the
branch it came from; the 5.0.0 arm leaks **1**.

**(d) Census.** 1 file, 1 hunk, 1 site, no named wrapper, message is a merge-from-head
rather than a sweep. ▶ **No census. No sibling sites owed** — that is free
information (F50/F58: a `≥5 files` selector carries no signal, a **named
wrapper** does, and there is neither here).

---

### 4.3 E7 — **`ph87`**

**(a) Cited lines, quoted.** `Zend/zend_constants.c`, the whole function is
`:300-331`:

```
 315  	} else {
 316  		name = c->name;
 317  	}
 318  
 319  	if (zend_hash_add(EG(zend_constants), name, c->name_len, (void *) c, sizeof(zend_constant), NULL)==FAILURE) {
 320  		free(c->name);
 321  		if (!(c->flags & CONST_PERSISTENT)) {
 322  			zval_dtor(&c->value);
 323  		}
 324  		zend_error(E_NOTICE,"Constant %s already defined", name);
 325  		ret = FAILURE;
 326  	}
```

✅ Every one of the entry's three citations (`:316`, `:320`, `:324`) is exact,
and the whole mechanism fits in **11 lines of one 31-line function**. The
`CONST_CS` path — which is PHP's **default** for `define()` — is the one where
`name` aliases `c->name`.

**(b) The `▸ trigger` line: `define("X", 1); define("X", 2);` — VERIFIED,
with one qualifier.** Measured: 50 duplicate defines → **50 of 50** emit
`Notice: Constant <garbage> already defined`, the name replaced by a short
pointer-shaped byte string. ⭐ **The UAF-read is visible in the program's own
output**, not only to a sanitizer.
⚠ **Qualifier**: 5.0.0's default `error_reporting` suppresses `E_NOTICE`, so the
corpus's own two-line reproducer prints nothing and exits 0. The trigger needs
`error_reporting(E_ALL)`. (Corpus `crashes_pristine_5_0_0 = False`; consistent.)

**⛔ (b2) — THE ORACLE COST, AND IT IS THIS ROW'S REAL PRICE.** I swept the
constant-name length 1…31 over three runs. The corruption is **100 %
reproducible in its PRESENCE and NOT reproducible in its VALUE**: the bytes
differ every run (a heap pointer written by `free()`; ASLR). ▶ **The
catalogue's `u64` — *"the emitted message checksum + `(allocs, frees)`"* — is
half unusable as written.** And it is worse than that in both directions:

* on **libc** `malloc`/`free` (which is what upstream uses — `c->name` comes
  from `zend_strndup`) the freed bytes get a heap pointer → ASLR-varying;
* under **`common-php/emalloc_shim.h`** a freed block under 88 bytes goes to
  PHP's **size-class cache** and its contents are **not touched at all**
  (`PROTOCOL_PHP.md` §B1.1, F3) → the message would be **CORRECT and the defect
  SILENT**.

⚠⚠ **That is `ph52`'s *"silent on a clean stack"* in heap form**, and it is the
concrete reason this row is not cheap. **The workable oracle is `(allocs, frees)`
+ ASan, and the row publishes *"the checksum does not move"* as a result** —
which is a real finding about UAF-**reads** and is the same shape as `ph55`'s
*"the `Option` caught the NULL; it did not catch the wrong PC."* **Not a kill,
a price.**

**(c) The R1h — ⭐ the best-shaped patch I have seen in this programme.**
`preimage_screen.py --row ph87` → **`CANDIDATE`**, 2 records (per F68: *"could
not exclude"*, nothing more). What `1ea22c90046b` **actually changes** (Marcus
Boerger, **2004-07-13** — the day 5.0.0 shipped; **1 file, 1 insertion,
1 deletion**): it **moves** the `zend_error` call to *before* `free(c->name)`.
Nothing is added; a single statement is reordered. ✅ Applies to the tarball,
`git apply` strict, bytes moved; post-image:

```
 319  	if (zend_hash_add(…)==FAILURE) {
 320  		zend_error(E_NOTICE,"Constant %s already defined", name);
 321  		free(c->name);
```

⭐⭐ **Consequence for the ladder that no other candidate offers**: R1 and R1h
have **identical instruction inventories in a different order**, so the
"what does the safety check cost?" column is about scheduling alone. `ph55` and
`ph52` both refuted the prediction *"the upstream fix costs something"*; this
row would be the sharpest possible **n = 3**.

**(d) Census.** `1ea22c90046b` touches **1 file, 1 hunk, 1 site**, no named
wrapper. ▶ **No census.** ⭐ **And the R1h decision is already made by
§C**: `ph87`'s 2 ids name 2 commits, but only `CRASH-068` has its `c_file_line`
in the defect's file (`zend_constants.c:320`); `CRASH-129` is
`ext/mbstring/php_mbregex.c:732`, a different function in a different
extension. **R1h = `1ea22c90046b`, no ambiguity.**

---

### 4.4 E5 — **`ph81`** ⚠ two candidates, and I do both because they are not tied — they are two DIFFERENT DEFECTS

**(a) Cited lines, quoted.** `Zend/zend_execute.h`, eleven lines:

```
 117  static inline void zend_ptr_stack_clear_multiple(TSRMLS_D)
 118  {
 119  	void **p = EG(argument_stack).top_element-2;
 120  	int delete_count = (ulong) *p;
 121  
 122  	EG(argument_stack).top -= (delete_count+2);
 123  	while (--delete_count>=0) {
 124  		zval_ptr_dtor((zval **) --p);
 125  	}
 126  	EG(argument_stack).top_element = p;
 127  }
```

✅ Exact, and the entry's *"eleven lines"* is literally right. The sibling:

```
1453  	zval *arg_array = NULL;                          <- hoisted OUT of the frame loop
1557  		if (arg_array) {
1558  			debug_print_backtrace_args(arg_array TSRMLS_CC);
1559  			zval_ptr_dtor(&arg_array);
```

✅ Exact. `arg_array` is assigned only at `:1511` or `:1545`, and
`zval_ptr_dtor` does **not** NULL the caller's pointer — so a frame that
assigns neither re-reads and re-frees the previous frame's zval.

**(b) The `▸ trigger` line: `"an error handler that calls debug_backtrace() during teardown."` — VERIFIED for the harm, with a CORRECTION to the wording.**

Measured, with a control:

```
control  (no error handler)   #0  b(1) called at [SCRIPT:4]
                              #1  a(1, 2) called at [SCRIPT:5]

probe    (error handler)      #0  h() called at [SCRIPT:6]
                              #1  b() called at [SCRIPT:6]
                              #2  b(8, Undefined variable: …, SCRIPT, 6, Array ([x] => 1)) called at [SCRIPT:5]
                              #3  a(1) called at [SCRIPT:7]
```

⭐ `b` appears **twice**, its printed arguments are **the error handler's five
arguments**, and `a(1,2)` prints as **`a(1)`**. A deterministic **wrong answer**
in stdout, with no sanitizer and no allocator ledger.
▶ **The correction**: no *request* teardown is needed. `CRASH-142`'s own
reproducer uses a `__destruct` (object teardown), and my probe needs no teardown
at all. And `CRASH-142`'s reproducer **SIGSEGVs** (`si_code=1`, wild address),
so the family carries **both** harms.

**(c) The R1h — ⛔ and this is why the family is BLOCKED.**
`preimage_screen.py --row ph81` → **2 records, both `CANDIDATE`** (F68: nothing
excluded, nothing confirmed). **2 ids → 2 distinct commits, and they repair two
DIFFERENT SITES:**

| id | `c_file_line` (corpus) | `fix_commit` | what it actually changes |
|---|---|---|---|
| `CRASH-142` | `zend_execute.h:117-127` (*"defective free loop at `:124`"*) | `8df40bdb313d` 2006, Dmitry Stogov, **2 files, 10+/4−** | `zend_execute.h`: `zval *q = *(zval**)(--p); *p = NULL; zval_ptr_dtor(&q);` **and** `zend_builtin_functions.c`: wraps the reader in `if (*arg) { … } else { add_next_index_null(…) }` |
| `CRASH-140` | `zend_builtin_functions.c:1453` | `1088e28dfa6a` 2005, Stanislav Malyshev, **1 file, 1 insertion** | `+ arg_array = NULL;` at the top of `debug_print_backtrace`'s frame loop |

Both apply to the pristine tarball, `git apply` strict, bytes moved.

⛔ **`CRASH-142`'s fix is TWO COUPLED HUNKS.** The writer half (null the slot)
and the reader half (tolerate a NULL slot) are **not independent** — nulling
without the reader guard makes `debug_backtrace_get_args` dereference NULL.
That is `ph07`'s two-hunk problem **one level worse**: `ph07` could ship hunk
(a) alone because the hunks were separable; here they are not.
⭐ **`CRASH-140`'s fix is ONE LINE.**

⚠⚠ **And §G's burden is not discharged for merging them.** Different unchecked
predicate (a slot not nulled vs a variable not reset), different attacker
quantity, different file, different fix, different `root_cause_id`. **The
manager must pick which site `ph81`'s kernel extracts** — §C makes R1h a
function of that choice, and the two choices have very different prices.

**(d) Census.** `8df40bdb313d` touches **2 sites** — `zend_execute.h:124` (the
writer) and `zend_builtin_functions.c:debug_backtrace_get_args` (the reader).
That is free sibling evidence, and it is also the reason the row is dear.
`1088e28dfa6a` touches 1 site, 1 line. Neither has a named wrapper.

---

## §5 ⭐ THE COST VERDICT — in §3.3's four words

| family | verdict | the specific thing |
|---|---|---|
| **E8** | ⭐ **MEDIUM** | `php_array_walk` allocates a `key` zval **per element**, so `PROTOCOL_PHP.md` §B1a's **O(1)-allocation precondition fails** — the cross-language column carries `ph64`'s caveat and must be labelled. **Declare it, do not refuse it.** Everything else on this row is the cheapest in my set: 2-line defect site, deterministic NULL write at a known address, 3-line same-file R1h that applies clean, four in-file sibling controls. ⚠ **AND ONE DECISION IS OWED FIRST**: the `fix_commit` column must be corrected to `0542a6f2c2a5` (§4.1c), or the row must publish that the column's commit does not close the site. |
| **E6** | **MEDIUM** | The **harm is a leak**, so the `u64` must carry `(allocs, frees)` and the row's checksum column will not move — `ph84`'s risk line says so and `ph85` inherits it. Plus: the **`▸ trigger` line does not fire as written**, so the build task's deliverable #1 starts with a correction (§4.2b). The R1h is a **one-line, one-file, same-file 2005 insert that applies clean** — the cheapest half of any row here. |
| **E7** | **MEDIUM** | The **oracle**. `ph87`'s harm is a UAF-**read** whose value is ASLR-varying on libc and **completely silent under `common-php/emalloc_shim.h`**'s size-class cache (§4.3 b2) — the catalogue's *"emitted message checksum"* half of the `u64` is not usable. The row's workable oracle is `(allocs, frees)` + ASan, and *"the checksum does not move"* becomes one of its results. Against that: the **smallest `needs` footprint in my 15** (no zvals, no VM, no userland re-entry) and **the best-shaped R1h in either programme** (one moved statement, 2004, applies clean, R1h unambiguous under §C). |
| **E5** | ⛔ **BLOCKED-ON-A-DECISION** | **Which site does `ph81` extract?** `CRASH-142` (`zend_execute.h:124`, fix = 2 coupled hunks across 2 files) or `CRASH-140` (`zend_builtin_functions.c:1453`, fix = **one line**)? The two are different defects with different fixes and §G's *"can I show these are the SAME?"* burden is **not discharged**. ▶ **On `CRASH-140` this family is the cheapest in my set after E8; on `CRASH-142` it is DEAR.** Not a kill — a fork the manager owns. The other four E5 rows are each **DEAR**: `ph77` two declared limbs + 5→5 commits; `ph78` 7→7 commits; `ph79` 5→5 commits **and** its risk line says an extraction that tags the two function kinds has already fixed it; `ph80` needs `environ` as a second, borrowing array and 4→4 commits. |

⛔ **No row in my 15 fails the C-side bar.** Every one of the 15 passes criteria
1 and 3 on reading, and **14 of the 36 corpus reproducers I ran produce a
SIGSEGV**; the non-crashing ones are leak-class rows whose harm I measured by
other means (`ph83` refcount, `ph84` destructor order, `ph85` RSS) or rows where
I simply did not reach the arm (**F3: that is not evidence of absence**).

---

## §6 ⚠ §3.6 — `ph91` / CRASH-071: the disagreement, stated precisely

**⛔ BLOCKED-ON-A-DECISION. I did not resolve it and I am not asking the
manager to read my run as a resolution.**

**What the corpus row says, field by field** (from `index.csv`, all three id
namespaces):

| field | value |
|---|---|
| `input_id` / `v5c_id` | `CRASH-071` / `V5C-071` |
| `root_cause_id` | `exception-ctor-debug-backtrace-copies-args-of-torn-down-executor-frame-during-shutdown-**uaf**` |
| `vuln_class` | `memory-corruption` |
| `cwe` | **`CWE-476`** |
| `category` | **`null-deref`** |
| `c_file_line` | **`Zend/zend.c:955`** |
| `fix_commit` | `e8359d3f904cf7232aa70ddf1e5d20fa936795fd` (2009, 2 files, same file) |
| `crashes_pristine_5_0_0` | `True` |
| `merged_members` | `V5C-177` |

**What `zend.c:955` actually is** — re-read from the pristine tarball, and the
catalogue's measurement is **exactly right**:

```
 938  			ALLOC_INIT_ZVAL(z_context);
...
 955  			z_context->value.ht = EG(active_symbol_table);
 956  			z_context->type = IS_ARRAY;
 957  			ZVAL_ADDREF(z_context); /* we don't want this one to be freed */
...
 964  			params[4] = &z_context;
```

That is inside `zend_error`'s **`$errcontext` publication**. Nothing at or near
`:955` is a `debug_backtrace`, an exception constructor or a shutdown path.

**The disagreement, in three parts — and the catalogue records only the first:**

1. **`root_cause_id` vs `c_file_line`.** The label describes an Exception
   constructor fetching a backtrace of a **torn-down executor frame during
   shutdown**; the citation points at the error handler's `$errcontext`
   publication. These are different defects in different functions.
2. ⭐ **NEW — the corpus row is inconsistent with ITSELF in a second way the
   catalogue does not note.** `root_cause_id` ends in **`-uaf`** while `cwe` is
   **`CWE-476`** and `category` is **`null-deref`**. Three fields, two
   different harm classes.
3. ⭐ **NEW — evidence, offered as evidence and NOT as an adjudication.** I ran
   the corpus's own `input/crash/CRASH-071.php` on the built 5.0.0 oracle. It
   **SIGSEGVs at `si_addr=0x20`**, and the reproducer's own header comment
   predicts precisely that: *"zend_hash_copy reads a dangling arg HashTable
   (**source == 0x20**)"*, via `zend_fetch_debug_backtrace`. ▶ **The behaviour
   the LABEL describes is the behaviour that occurs.** ⚠ That does **not**
   settle the row: `zend.c:955` is genuinely **on the path** (the reproducer's
   `eh()` handler is reached through `zend_error`, which publishes
   `$errcontext` at `:955` before calling the handler that constructs the
   Exception), so `:955` may be a *participating* frame that the corpus filed
   as the defect site. **Which of the three frames (§0.1: defect / guard /
   fault) `:955` is, is exactly the open question, and it is the manager's.**

**The decision the manager owes**: does `ph91` become (a) the label's row, with
`c_file_line` corrected to the `zend_fetch_debug_backtrace` /
`_zval_copy_ctor` / `zend_hash_copy` chain; (b) the citation's row, i.e. the
`$errcontext` publication — **which is already `ph89`'s and `ph91` would then be
a duplicate of a row in the same family**; or (c) two rows. **Until that is
decided `ph91` cannot be dispatched**, and it is *not* a kill.

---

## §7 ⭐ THE RANKING

Best first. One sentence each, written for a build-task author.

| # | family | row | the one sentence |
|---|---|---|---|
| **1** | **E8** | **`ph90`** | Lift `array.c:1045-1046` plus the three lines of `zend_call_function` that make it lethal (`:595` `*retval_ptr_ptr = NULL`, `:873` `return SUCCESS`, `_zval_ptr_dtor:389`'s unguarded `(*p)->refcount--`); the adversarial input is *a callback that throws*, the harm is a **NULL write at offset 0x10** that I measured four ways including on a one-element array, and the R1h is **`0542a6f2c2a5`** (not the column's `32c2e664a6ec`) — 1 file, 3+/1−, at the cited lines, applies to the tarball clean. |
| **2** | **E6** | **`ph85`** | Lift `zend_execute.c:914-926`'s autovivify arm; the container must be an **engine-produced** empty string (`"" . ""`, not the shared `empty_string` — the catalogue's trigger is wrong here), the harm is a measured **~47 B/iteration unbounded leak** with two flat controls, the `u64` must carry `(allocs, frees)`, and the R1h is **one inserted line** that applies clean. |
| **3** | **E7** | **`ph87`** | Lift the whole 31-line `zend_register_constant` — it needs **no zvals, no VM and no userland re-entry**, the duplicate-`define` path frees `c->name` at `:320` and `%s`-formats it at `:324` (measured: 50/50 corrupted names in stdout), and the R1h `1ea22c90046b` is **one moved statement** — but budget for the oracle, because the corrupted *value* is ASLR-varying on libc and would be **silent** under the `emalloc` shim's size-class cache. |
| **4** | **E5** | **`ph81`** | Ask the manager which of the family's two defects the kernel extracts **before** writing anything: `CRASH-140` (`arg_array` not reset per frame — 1-line fix, measured wrong-answer harm in stdout) is cheap, `CRASH-142` (`zend_ptr_stack_clear_multiple` leaves released slots as presence flags — 2 coupled hunks across 2 files, measured SIGSEGV) is dear, and they are not the same defect. |

### ▶ WHICH FAMILY WOULD I ENTER FIRST, AND WHAT WOULD CHANGE MY MIND

**E8, with `ph90`.** Three reasons, in order:

1. ⭐⭐ **The harm is the most deterministic thing in my 15 rows.** It is a NULL
   write at a **fixed address**, independent of stack garbage (unlike `ph52`),
   independent of the allocator (unlike `ph87`), independent of ASLR, and
   independent of how many elements the input has. `model.py`'s
   `sanitizer_expect` is trivially derivable, and the "does it fire?" question
   has a one-bit answer.
2. ⭐⭐ **The R1h is ideal once the column is corrected** — same file, at the
   cited lines, 3 insertions, applies with `git apply` strict — **and the
   correction itself is a publishable result** (`PROTOCOL_PHP.md` §G1's warning,
   firing on a real row, with the right commit named and its patch on disk).
3. ⭐ **The sibling census is already in the file**: four of five
   `zend_call_function` call sites in pristine `array.c` guard the
   out-parameter and the fifth does not. That is `ph55`'s "the codebase shouts
   the invariant where it holds" signature reproduced on a second row, which is
   exactly the kind of thing the programme is for, and it costs nothing.

**What would change my mind, concretely:**

* ⛔ **If the manager declines the R1h correction.** If `ph90` must cite
  `32c2e664a6ec` as written, then `c/kernel_hardened.c` carries a guard that (on
  my reading) does **not** close the site, `check.py` stage 7h refuses the row,
  and E8 becomes DEAR. ▶ **In that case I would enter E6 with `ph85` instead.**
* ⛔ **If §B1a's O(n)-allocation caveat is judged too expensive for a
  first-in-family row.** `ph64` already pays it, and `RECAP_PHP.md` notes that
  the cross-language column on such rows is *"largely a comparison of an
  allocator against arithmetic"*. Two rows with that caveat and one without
  would be a worse portfolio than the reverse. ▶ **Then E7 (`ph87`), which
  allocates O(1) per call — one `zend_strndup` — jumps to first**, and its
  one-moved-statement R1h is the compensation.
* ⛔ **If someone shows my one-element measurement is confounded** — e.g. that
  the 5.0.0 oracle build's `-flto -march=native` changes the path. ▶ The cheap
  disconfirmation is to rebuild 5.0.0 at `-O0` and re-run
  `input/crash/CRASH-029.php`; if it stops crashing, everything in §4.1 needs
  re-doing.
* ✅ **What would NOT change my mind**: `ph90` being "a near-twin" of `ph60` or
  of any `T6` row. `CLAUDE.md` rule 6's last line and `PLAN_PHP.md` §3 make
  C-side duplication **not a kill in `patterns-php/`**, and the entry's own risk
  line already states the distinction (`ph60` has no guard; `ph90`'s guard is
  **present and tests the wrong proposition**). A near-twin is *cheaper* to
  build, not weaker.

---

## §8 ⭐ THE THREE REGISTERED PREDICTIONS, SCORED FOR MY ROWS

### P1 — *"at least ONE of the five top mechanical picks (ph87, ph60, ph85, ph66, ph37) fails deep verification"*
**In my scope: `ph87` and `ph85`. Verdict: SUPPORTED, but NOT in the `ph32` way.**

* **`ph85` — FAILS on a stated line.** Its `▸ trigger` **does not fire as
  written**; the bare `""` control is flat at 10⁶ iterations. The mechanism, the
  citation and the R1h all survive and are excellent. ▶ **P1's letter is
  satisfied by this row.**
* **`ph87` — SURVIVES on admission and on R1h, FAILS on its `u64`.** The
  catalogue's *"emitted message checksum"* is not a usable oracle half
  (§4.3 b2). Everything else about the row got **better** on inspection, not
  worse.

⚠ **The honest scoring note:** neither is a `ph32`-class failure — `ph32`'s
problem was that the *cost* was the opposite of what one line of another row's
prose said. Here both rows' costs came out roughly where the mechanical shape
predicted, and **both are in my top three**. ▶ **So P1 is technically upheld and
its underlying worry — "the mechanical shape misleads" — is NOT reproduced in
my set.** The mechanical R1h shape was a **good** predictor here: the three
best R1h shapes in my 15 (`ph87` 2004/1f/same, `ph85` 2005/1f/same,
`ph90` 2005/1f) are three of my top four rows.

### P2 — *"row 11 is a TEMPORAL row (an `E` family)"*
**I cannot be the control** — all four of my families are temporal. What I can
say is that **P2 is not weakened from my side**: `ph90` is, on my evidence, a
strong row on its own merits (deterministic harm, ideal R1h, free in-file
census, 2-line defect site) and I would rank it against anything. ▶ **Agent C
is the test; if an `S`/`T` family beats it, that is the more valuable result and
I would not argue with it.**

### P3 — *"`▸ trigger` lines fail on roughly a third of rows deep-verified"*
**Scored on my four deep checks: 1 WRONG, 3 VERIFIED = 25 %.** Consistent with
F46/F49's 3-of-9 (33 %).

| row | trigger | verdict |
|---|---|---|
| `ph90` | *"an array_walk callback that throws"* | ✅ **(i) VERIFIED** — 4 inputs, SIGSEGV `si_addr=0x10` on every one |
| `ph85` | *"an assignment that retypes a live string slot to an array"* | ⛔ **(iii) WRONG as written** — needs an engine-produced empty string; measured with two controls |
| `ph87` | *"`define(\"X\", 1); define(\"X\", 2);`"* | ✅ **(i) VERIFIED** — 50/50 corrupted names. ⚠ needs `error_reporting(E_ALL)`; the corpus's own reproducer prints nothing without it |
| `ph81` | *"an error handler that calls `debug_backtrace()` during teardown"* | ✅ **(i) VERIFIED for the harm, wording corrected** — no request teardown needed; measured against a clean control |

⭐ **Bonus data at no extra cost (not deep checks, so kept separate):** of the
other 11 rows' triggers I transcribed and ran, `ph82`/`ph83`/`ph84` are
leak-class and produced no visible signal from my transcription (`ph83`/`ph84`
*did* fire on the corpus's own reproducers, so my transcriptions were the weak
link, not the rows); `ph77`/`ph78`/`ph79`/`ph80`/`ph86`/`ph88`/`ph89`/`ph91`
needed the corpus's reproducer to fire. ▶ **The general lesson: a `▸ trigger`
line is a sentence and the corpus ships a FILE. Use the file.** The reproducers
under `…/vuln-corpus-5.0/input/{crash,logic}/<ID>.php` are richly commented —
several of them name the line numbers, the mechanism and the real fix commit —
and **nothing in `CATALOGUE.md`, `PROTOCOL_PHP.md` or `RECAP_PHP.md` points a
row engineer at them.** That is the single cheapest process improvement I found.

---

## §9 ⭐ WHAT I AM UNSURE OF — named, not omitted

1. ⛔ **I did NOT measure that `ph90`'s hardened arm still crashes.** §4.1c's
   claim that `32c2e664a6ec` does not close `array.c:1046` is an **inference**
   from (i) the measured one-element crash and (ii) the applied post-image.
   Rebuilding PHP 5.0.0 with the guard would settle it and I did not do that.
2. ⚠ **`ph80`'s mechanism is not confirmed and I think the catalogue's chain has
   a gap.** The destructor `php_putenv_destructor` (`:888-925`) calls
   `unsetenv(pe->key)` at `:901` **before** `efree(pe->putenv_string)` at `:923`
   on the `HAVE_UNSETENV` path — so on glibc `environ` should no longer name the
   buffer when it is freed, and the `:1380-1385` scan should find nothing. The
   catalogue's *"while `environ` still points at it"* may hold only on the
   `previous_value`-non-NULL path (where `putenv(pe->previous_value)` re-installs
   a possibly-already-freed older string) or on platforms without `unsetenv`.
   **I did not trace it to a conclusion**, and `CRASH-084`'s own reproducer ran
   clean. ▶ **A build task must settle this first.**
3. ⚠ **`ph86` is the row I understand least.** Neither of its reproducers
   crashed, and I did not trace what consumes `EXT_TYPE_UNUSED` once
   `zend_do_free` stamps the wrong opcode. Its citation is exact
   (`zend_compile.c:894-897`) and its risk line (*"two passes … budget for
   both"*) is the honest cost. **Trigger: (ii) plausible but unverified.**
4. ⚠ **`ph89`'s crash mechanism is not the one the catalogue states, and I could
   not finish the trace.** See §10 item 6. I measured the crash and the control;
   I did not identify the faulting frame.
5. ⚠ **`ph77`'s `garbage[2]` limb**: `Zend/zend.c:969-973` and the matching
   restore are the **only** place in the tree that saves and restores
   `EG(garbage)` around a call, and `ph77`'s entry does not mention them. I
   noticed this and did not pursue it; it may be a site the row owes.
6. ⚠ **`preimage_screen.py` told me nothing decisive on any of my four.**
   Three `CANDIDATE` and one `INAPPLICABLE` — per F68/F95 **zero exclusions**,
   and I have quoted none of them as confirmation anywhere.
7. ⚠ **The oracle binary is not a museum-default build** (`-O3 -march=native
   -fomit-frame-pointer -flto`, mysql+webext). Every crash I report is evidence
   of **presence**; no clean run in this report is evidence of absence.
8. ⚠ **`ph87`'s `crashes_pristine_5_0_0 = False`** is consistent with what I saw
   (no crash, corrupted output). **Per F3 that is not an admission filter**, and
   I have not treated it as one.
9. ⚠ **I did not read the R1h patches for the 11 non-deep rows** beyond their
   `fixsurvey`/`ids2commits` metadata and, for `ph82`/`ph83`/`ph84`, the corpus
   reproducers' own commentary.
10. ⛔ **Two cached patches in my scope are mis-keyed** (`ph78`/`CRASH-159`,
    `ph79`/`LOGIC-025`) — §0.5. I verified the binding of all 44 records and of
    every patch §4 rests on; nothing in this report depends on the two bad ones.
    **I did not investigate the cache tool** — the manager reserved that.

### ⭐ WHERE MY DEPTH RAN OUT, EXACTLY

**It did not run out inside the four deep checks** — §5's definition of done is
met for all four, including the four `preimage_screen.py` labels, the
`ids→commits` counts and the census reads.

It ran out in **two named places**:

* **`ph80`'s `unsetenv`/`environ` ordering** (§9.2). I read the destructor and
  formed a specific doubt; I stopped rather than guess.
* **`ph89`'s faulting frame** (§9.4, §10.6). I established that the corpus's own
  `c_file_line` points at a *different* statement from the one the catalogue
  describes, measured the crash and a clean control, and stopped rather than
  invent a chain.

---

## §10 ⭐⭐ CATALOGUE DEFECTS FOUND

*(§5.8: this section has paid for itself on every task that had one. Everything
below was read from the pristine tarball or measured on the oracle.)*

1. ⛔⛔ **`ph90`'s mechanism sentence is FALSE in its second clause.**
   *"on that path `retval_ptr` was never written"* — it **is** written, to
   `NULL`, at `Zend/zend_execute_API.c:595`, by a statement whose own comment
   says *"we may return SUCCESS, and yet retval may be uninitialized, if there
   was an exception..."*. The harm is a **NULL dereference**, which is what the
   corpus's own `cwe`/`category` fields (`CWE-476` / `null-deref`) already say.
   ▶ Under §G2 this is a correction that **changes what the row claims**. ⭐ It
   makes the row *better* — the harm is garbage-independent.
2. ⛔⛔ **`ph90`'s `fix_commit` is not the repair of its own cited site.**
   `32c2e664a6ec` adds an **entry** guard in `zend_execute_API.c`; the cited
   `array.c:1046` is repaired by **`0542a6f2c2a5`** (2005-02-10, 1 file, 3+/1−,
   same file, applies to the tarball clean). Measured support: a **one-element**
   array with a throwing callback SIGSEGVs, so no re-entry is involved and the
   corpus's `root_cause_id` (*"call-function-**reentered**-with-pending-
   exception"*) mis-describes the path its own reproducer takes.
3. ⛔ **`ph83`'s second cited site does not say what the entry says it says.**
   The entry describes `Zend/zend_execute.c:448-452` as *"a lock taken **despite
   a pending exception**"*. The text at those lines is
   `if (result) { T(result->u.var).var.ptr = value; …; SELECTIVE_PZVAL_LOCK(value, result); }`
   — **there is no exception test in the cited lines**. The claim is about the
   *context* (`:444`'s `write_dimension` handler can throw), not about the
   quoted text. The first site (`:986-987`, a bare `PZVAL_LOCK(container)` where
   the selective form is used elsewhere) **is** exactly as described.
4. ⛔ **`ph85`'s `▸ trigger` does not fire as written** (§4.2b, measured with two
   controls). The row needs an **engine-produced** empty string; the literal
   `""` is the shared `empty_string` global at 5.0.0. The corpus's own
   reproducer says so in an `NB` and the catalogue does not carry it.
5. ⚠ **`ph84`'s mechanism sentence is under-specified, and the row has a second
   harm the entry does not mention.** `convert_to_long_base` **does** release the
   copy on the `IS_STRING` arm (`STR_FREE` at `zend_operators.c:313`) and on the
   `IS_ARRAY` arm (`zval_dtor` at `:317`). The leak exists only on the
   **`IS_OBJECT`, non-`ze1_compatibility_mode`** arm, which returns at `:341`
   with the tag unchanged. ⭐ **Measured**: the destructor of an object passed to
   `break $o` is deferred to request shutdown (`DTOR bad` prints last), **and**
   the raw object handle is consumed as the loop-nest count — *"Cannot
   break/continue **7** levels"*. The second limb is a **type-confusion wrong
   answer** and is not in the entry.
6. ⛔⛔ **`ph89`'s mechanism is at odds with the corpus's own `c_file_line`, and
   the path the entry describes is unreachable from the trigger it gives.**
   The entry puts the defect at the by-ref **separation** in
   `zend_execute_API.c:733-745`; the corpus says **`:738-739`**, which is
   `if (fci->no_separation) { return FAILURE;` — an early return **inside** the
   parameter-pushing loop, leaving `EG(argument_stack)` partially pushed with no
   count sentinel. And `zend_error` calls, at `Zend/zend.c:975`,
   `call_user_function_ex(CG(function_table), NULL, orig_user_error_handler,
   &retval, 5, params, **1**, NULL TSRMLS_CC)` — whose 7th parameter is
   `int no_separation` (`Zend/zend_API.h:301`, `zend_execute_API.c:536`), so
   **`no_separation = 1`** and the `ALLOC_ZVAL(new_zval) … zval_copy_ctor …
   refcount--` sequence the entry quotes at `:741-745` is **never reached** from
   the error handler; `:738-739` returns `FAILURE` first, which is exactly what
   the corpus cites. ▶ Measured: a by-ref 5th argument SIGSEGVs at a **wild**
   address; a
   by-value 5th argument is clean. **The harm is real; the stated mechanism is
   not the one that produces it.**
7. ⚠ **`ph80`'s `GUARD: :1333, a guard that never fires` is at best loose.**
   `:1333` is `if (Z_STRVAL_PP(str) && *(Z_STRVAL_PP(str)))`, which **does** fire
   on an empty string. The corpus describes the same line as *"enabling missing
   guard at `:1333`"* — i.e. the guard is **missing a case**, not inert.
8. ⚠ **`ph91`'s corpus row is inconsistent in a THIRD way the catalogue does not
   record**: `root_cause_id` ends in `-uaf` while `cwe = CWE-476` and
   `category = null-deref` (§6).
9. ⚠ **Not a catalogue defect but a corpus one, worth the manager's eye:**
   `LOGIC-011`'s reproducer names `8aad91d14a0d` + `ca4de03eed5b` as the
   upstream fix in its own header comment, while `index.csv`'s `fix_commit`
   column says `07b7ba8b4004` — whose subject is *"Improved ternary operator
   performance when returning arrays"* (2011, 8 files), a **performance
   refactor**. Since `LOGIC-011` is an id of **both `ph77` and `ph83`**, that
   column feeds two rows. **The corpus contradicts itself here and the
   reproducer is the more careful half.**
10. ⭐ **Process, not a defect:** the corpus ships a **commented reproducer per
    id** at `…/vuln-corpus-5.0/input/{crash,logic}/<ID>.php`, several of which
    carry line numbers, the mechanism and the real fix commit — and **no
    standing document in this repo points a row engineer at them**. Adding one
    line to `PROTOCOL_PHP.md` §A3 would have saved this task an hour and would
    have caught defects 4, 5 and 9 at mining time.

---

## §11 HOW TO REPRODUCE EVERY NUMBER IN THIS REPORT

```sh
cd /home/apt/repos_common/sec-ladder
cat .temp/php54B/NOTES.md          # the tar recipe + what each probe is

gcc -shared -fPIC -O0 -o .temp/php54B/segaddr.so .temp/php54B/segaddr.c
gcc -shared -fPIC -O0 -o .temp/php54B/maxrss.so  .temp/php54B/maxrss.c

python3 .temp/php54B/mk_triggers.py       # the catalogue's trigger lines, as .php
sh      .temp/php54B/triggers.sh          # -> triggers.log
sh      .temp/php54B/corpus_repro.sh      # the CORPUS's reproducers -> corpus_repro.log
python3 .temp/php54B/ids2commits.py       # n ids -> n distinct commits, per row
python3 .temp/php54B/r1h_apply.py         # does each R1h apply to the tarball?
python3 .temp/php54B/patch_binding.py     # §0.5 -- does each cached patch carry its own sha?
python3 .tasks-php/fixsurvey.py --offline
python3 .tasks-php/preimage_screen.py --row ph90 --verbose   # INAPPLICABLE, not an exclusion
```

⚠ **Fetched from the network on 2026-09-15** (the task file records that it was
reachable, and it was): `github.com/php/php-src/commit/0542a6f2c2a5.patch`,
`raw.githubusercontent.com/php/php-src/PHP-5.{0,1,2}/ext/standard/array.c`, and
one GitHub API call listing commits on branch `PHP-5.0` touching
`ext/standard/array.c`. All three artefacts are in `.temp/php54B/`. Everything
else came from the cache at `.temp/mgr/batch/patches/` or from the pinned
tarball.

⚠ **The extracted `.c` files were deleted** when the task finished (trap 5); the
one-line `tar` recipe that regenerates all fifteen of them is at the top of
`.temp/php54B/NOTES.md`.
