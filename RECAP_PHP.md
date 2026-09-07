# RECAP_PHP — the handoff document for the PHP programme (`patterns-php/`)

**Read this first, always.** The manager updates it at every task boundary.
For the *other* programme (`patterns/`) read `RECAP_PAT.md`; for the split
between them read `CLAUDE.md`'s top table.

> ⚠⚠ **SIZE DISCIPLINE, AND IT IS A MEASURED LESSON, NOT A PREFERENCE.**
> `RECAP_PAT.md` reached **560 KB** and one pattern's `why` field became a
> single ~7,000-word JSON string. **Both stopped being read**, which is how a
> published limitation that did not exist got copied out of a stale header
> (`.tasks/PROTOCOL.md` rule 13). **The START HERE box stays ≤ 20 lines.**
>
> ⚠⚠ **THIS RULE ALSO SAID *"a `spec.md` `why` stays ≤ 200 words"* AND THAT WAS
> UNSATISFIABLE — REFUTED AT `TASK_PHP_002`, ✅ MANAGER-VERIFIED.** The gate
> hard-requires a shared `NAMED-SPELLING STANDARD` paragraph, byte-identical
> across patterns: `ph00-smoke`'s `why` is **12 224 bytes / 2 056 words**, of
> which **11 004 bytes is that mandated block**, leaving a row-specific half of
> ~201 words. **The repaired rule: the ROW-SPECIFIC half of `why` stays ≤ 200
> words; the shared paragraph is gate-mandated and does not count against it.**
> ⚠ A size rule that cannot be met is worse than none — it gets ignored wholesale
> and takes the satisfiable half with it. Anything longer goes in
> `.memory-php/` or the row's `NOTES.md`, not here.

---

## ▶ START HERE — the next action, in ≤ 20 lines

```
STATE      NOTHING BUILT. The programme opened 2026-09-07.
           Renames landed (RECAP_PAT.md / PLAN_PAT.md); PLAN_PHP.md written.
           patterns-php/ harness-php/ results-php/ .tasks-php/ .memory-php/
           common-php/ DO NOT EXIST YET -- Phase 0 creates them.

MINED      TASK_PHP_001 DONE, all 3 axes. 54 candidates, evidence promoted to
           .tasks-php/TASK_PHP_001_MINE/. UNREVIEWED (rule 9).
             temporal 23 cands / 85 of 85 rows / 11 verbatim 10 narrowed 2 modelled
             spatial  16 cands / 18 rows / 8 ptr_cursor / 0 emalloc-dependent
             type     15 cands / 12 mechanism families
           ALL THREE REFUTED THE MANAGER CLAIM THEY WERE NAMED TO ATTACK.

BUILT      TASK_PHP_002 Phase 0 built + gated. TASK_PHP_003 REVIEWED IT:
           2 BLOCKERS, 6 majors, 7 minors, 6 against MANAGER design.
           ⚠ PHASE 0 IS NOT DONE until B1 and B2 close.
           B1 the "mandatory" c/ symlink is enforced by NOTHING
           B2 the emalloc shim INVENTS DEFECTS (wrong multiply predicate)

NEXT       (1) TASK_PHP_004 -- land the review. WRITTEN, ready to launch.
           (2) then adjudicate the 54 candidates into
               patterns-php/CATALOGUE.md, and review that.

BAR        C-SIDE ONLY. Nothing about Rust/Verus/Miri/cost may kill a row.
           patterns-php/ is FRESH: duplication with patterns/ is NOT a filter.

READ       PLAN_PHP.md (the design + all 10 decisions), then
           .tasks/PROTOCOL.md (reused unchanged), then .memory-php/.
```

---

## What is true now

| | |
|---|---|
| **rows built** | **0** — `ph00-smoke` is a relocated PAT calibration kernel, throwaway, **no PHP provenance**, and prices nothing |
| **tasks** | `TASK_PHP_001` mining wave **DONE, unreviewed** · `TASK_PHP_002` Phase 0 **built, REVIEWED at `TASK_PHP_003` — 2 blockers open** · `TASK_PHP_004` written |
| **infrastructure** | built: `harness-php/{root,gate,provenance}.py` · `common-php/` · `patterns-php/{SOURCES.md,php-5.0.0.manifest}` (1170 files, 109 KB) · `.tasks-php/PROTOCOL_PHP.md` · `results-php/` |
| **candidates** | **54** across three axes, covering 85/85 temporal rows. Evidence in `.tasks-php/TASK_PHP_001_MINE/` |
| **catalogue** | not yet written — Phase 1 |
| **infrastructure** | not yet built — Phase 0 |
| **citation base** | PHP 5.0.0, pristine tarball, sha256 `5783e0c0…d6919`, 5595997 B, 3815 entries. **4.0.x ignored** (`DP-06`) |
| **rungs** | all five, R4/R5 may land as findings (`DP-02`) |
| **PAT tree** | untouched and must stay so — `harness/*.py` and `common/*.py` are hashed into all 33 gate records (`PLAN_PHP.md` §2.1) |

### The rename, and what it cost

`RECAP.md` → `RECAP_PAT.md`, `PLAN.md` → `PLAN_PAT.md`.

- ✅ **Zero gate runs, zero re-measures.** Measured: `grep -nE
  '(grep|awk|sed)[^|]*\b(RECAP|PLAN)\.md' harness/*.py` → **0 hits**, so no
  *runnable* citation lived in a hashed file. The prose mentions that do live
  there were deliberately left alone.
- ✅ **Seven runnable-command citations repaired and RE-RUN**, in
  `.tasks/PROTOCOL.md` (rules 1 and 10), `.memory/01-ladder.md`,
  `.memory/02-bench-rules.md`, `.memory/03-measurement.md` and `RECAP_PAT.md`
  ×2. Rule 1's loop prints only `p01` (the documented benign exception) and
  rule 10's prints only the three `TASK_NNN` placeholders — both exactly as
  `PROTOCOL.md` predicts, which is what a working check looks like.
- ⚠ **Two pre-existing drifts surfaced and were NOT repaired**, because they
  are numbers inside findings rather than paths:
  `.memory/03-measurement.md` says *"13 PROVISIONAL lines"* and the count is
  now **16**; `.memory/01-ladder.md`'s `NR>109 && NR<930` window is stale
  against a file this long and returns finding **21**, not the highest.
  Recorded here so they are not mistaken for rename damage.
- ⚠ Historical citations of the old names in `.tasks/`, `patterns/*/`,
  `pilot/` and inside findings are **left on purpose** and resolve to the
  `_PAT` files. Do not "fix" them.

---

## Findings

*(none yet — the first row has not been built. What follows are the mining
wave's results: engineer work, **UNREVIEWED**, `PROTOCOL.md` rule 9.)*

### F1 (PROVISIONAL) — `c_file_line` names the FAULTING FRAME, not the defect

Grouped by mechanism rather than by file, the temporal axis is **23 families,
11 `verbatim` / 10 `narrowed` / 2 `modelled`** — nine in ten lift. ✅
Manager-recomputed. The manager had predicted the opposite and would have
written off the richest axis in the corpus. The defect usually sits one call
below the crash, in a standalone container (`zend_ptr_stack.h`, 68 lines;
`zend_hash.h:88`'s `typedef Bucket* HashPosition;`). → `PLAN_PHP.md` §4.2a.

### F2 (PROVISIONAL) — the CSV is authoritative; the reproducer comment is not

Found independently by two agents on two axes. Every `index.csv` `c_file_line`
resolved exactly; **six `input/crash/*.php` header comments describe 4.0.2**,
and `CRASH-017.php` self-labels as such. ✅ Manager-verified: following it
instead of the CSV **inverts the verdict**. → `PLAN_PHP.md` §1.

### F3 (PROVISIONAL) — `crashes_pristine_5_0_0 = False` is not evidence of absence

40 of 85 temporal rows are `False`, mostly because PHP's size-class cache keeps
**63.5 % of heap traffic away from `malloc`**. A C kernel on plain
`malloc`/`free` reproduces **more** of these than pristine PHP does. **Not an
admission filter.** A second allocator truncation was also found —
`zend_alloc.h:53`'s `unsigned int size:31` (✅ verified). → `PLAN_PHP.md` §4.3.

### F6 — ⚠⚠ THE ALLOCATOR SHIM INVENTED DEFECTS, IN THE FILE WRITTEN TO PREVENT THAT

`common-php/emalloc_shim.h:340` claimed `__builtin_mul_overflow` is the *"same
predicate"* as PHP's `ZEND_SIGNED_MULTIPLY_LONG`. ✅ **Manager-verified false:**
`Zend/zend_multiply.h:22` guards the exact `imul` arm with
`#if defined(__i386__) && defined(__GNUC__)`, so on **x86-64** PHP falls to the
`#else` at `:34` — a **double-precision heuristic** (`__dres + __delta != __dres`),
not an exact test. Measured: **84 523 disagreements in 20 M samples, 100 % one
way — PHP raises `E_ERROR` where the shim allocates.**

⚠⚠⚠ **This is `PLAN_PHP.md` §4.3's own failure mode — a substituted primitive
inventing a defect — inside the file that exists to prevent it**, and it is the
same shape as the earlier PHP effort's `malloc`-for-`emalloc`, which published a
false explanation of an upstream fix. **Blocker; `TASK_PHP_004` closes it.**

### F7 — the manager's stated expectation was REFUTED, and that is the good news

The manager predicted Phase 0 would fall over on the `common-php/*.h` digest gap
and asked for a constructed case. **It fires**: planting `MAX_CACHED_MEMORY
11→12` makes the preflight refuse (`exit 2`, tool not run), and with `--regen`
the gate record goes `STALE`. ⚠ **What is NOT protected is the second half** —
B1, the unenforced `<row>/c/` symlink.

✅ **And the run of four is broken: `TASK_PHP_003` checked every `file:line` the
manager marked ✅ and found ZERO unearned.** ⚠ The *reasoning* around two of them
was still wrong (the `REAL_SIZE` story, `repo_path_bytes` 20 vs 15) — **the marks
were on the citations, and the citations held.**

### F5 (PROVISIONAL) — a THIRD allocator truncation, and the calloc path

`Zend/zend_alloc.c:295` in `_ecalloc` is `int final_size = size*nmemb;` — a
**signed 32-bit** product passed straight to `_emalloc`, so
`ecalloc(0x40000000, 4)` allocates **0 bytes and succeeds**. ✅ Manager-verified.
With `real_size` (`:129`) and `size:31` (`zend_alloc.h:53`) that is **three**
truncations; the plan knew of one when it was written. → `PLAN_PHP.md` §4.3.

⚠ Demonstrated with controls rather than argued: 18.45 EB → 2 GiB succeeds while
the no-truncation control returns `NULL`, and under ASan **the same UAF is
reported on a 96-byte block and silent on a 24-byte one** — the mechanism behind
F3, measured instead of inferred from a percentage.

### F4 — a manager error, corrected by an agent

The manager told all three agents `.temp/san_tests/` holds *"123 ASan reports"*.
✅ Verified wrong: 123 is one curated pass, the column beside it says **7
distinct sites**, and the real population is **2534 log files**. `PROTOCOL.md`
rule 14's shape — a premise stated as fact in a task file is one an engineer has
no reason to doubt. → `PLAN_PHP.md` §1 corrected.

---

## Open items — carried, not closed

| # | item | note |
|---|---|---|
| 1 | The pristine tarball lives under **another project's gitignored `.temp/`** and is deletable at any time | Phase 0 must land `patterns-php/SOURCES.md` with the sha256 + a per-file manifest before anything cites it |
| 2 | *"Where does the existing Rust port land on these scales?"* | **deferred, not deleted** (`DP-05`). Well-posed once the corpus exists |
| 3 | `.web/` does not know `results-php/` exists | deliberate. Do not teach it until there is something worth publishing |
| 4 | **CRASH-136 (exif) was rejected on EXTRACTION COST** | ⚠ the bar does not permit that as a kill — cost is a *tier*, not a filter. **Manager must re-adjudicate.** The most likely place the spatial axis lost a real row |
| 5 | `EG(garbage)` is `zval *garbage[2]` with an unchecked `EG(garbage)[EG(garbage_ptr)++]` | a faithful temporal extraction **inherits a SPATIAL overflow**. Flagged, not bounded away — bounding it silently would be §4.2's invented non-defect. Manager decides |
| 6 | Four temporal merges flagged as probably wrong | ranks 21, 8, 12, 23. Split decisions owed at catalogue adjudication |
| 7 | All `hotness` fields on the SPATIAL axis are **reasoned, not measured** | that agent never opened `.temp/san_tests/`. **Must not be quoted as frequency evidence** until checked |
| 8 | Rank 15 (CRASH-158) may be spatial, not temporal | cross-check the two miners' lists at adjudication |
| 9 | ⚠⚠ **No php marginal `Ir` is comparable to any PAT one** | `repo_path_bytes` is **15** bytes longer through the shim (⚠ this said **20**; corrected at `TASK_PHP_003`), and `gate.py`'s own `PYTHONDONTWRITEBYTECODE=1` moves `envp_stack_bytes` **+33** as well — a second term nobody had named. The gate's domain rule makes layout part of the measurement. **Never quote a php figure against a `pNN` one** |
| 10 | ⚠⚠ **`common-php/*.h` is in NO gate digest, and cannot be without a harness edit** | `check.py`'s three `common/` globs (`driver.*`, `*.py`, `layout/*.py`) are all non-recursive and none matches `emalloc_shim.h`. Closed with a digest bridge (gate half) + a mandatory `<row>/c/` symlink (measurement half). **The review must attack this** — it is the exact "unhashed shared file" gap that cost the PAT side ten control sources |
| 11 | A new php row costs **six commands (~28 min)**, not three | `gate → report → gate` is irreducible and `measure.py` builds nothing. Budget it |
| 12 | `.memory-php/` **does not exist yet** | `PLAN_PHP.md` lists it, `TASK_PHP_002` did not ask for it, and rule 4 makes it the manager's. Create it when the first finding survives review |
