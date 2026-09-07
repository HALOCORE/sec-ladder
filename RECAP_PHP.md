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
> which **~11 003–11 006 bytes is that mandated block**, leaving a row-specific
> half of **exactly 200 words**.
>
> ⚠⚠ **DO NOT ARBITRATE THAT BYTE COUNT — IT HAS THREE ANSWERS AND THE
> DISAGREEMENT IS A DEFINITION, NOT AN ERROR.** The manager measured **11 004**
> (from the literal `NAMED-SPELLING STANDARD`), `PROTOCOL_PHP.md` and
> `ph00-smoke/NOTES.md` say **11 003**, and the manager's *longest-common-suffix
> against `p01`* — the only definition the gate's byte-identity actually pins —
> gives **11 006**. All three are right about different cuts. ✅ **The quantity
> the RULE needs is robust and was measured at all three: the row-specific half
> is 200 words.** ⚠ `TASK_PHP_004` recorded 11 003 as *"correct"* and the other
> as *"wrong"*; that was a false precision on a number nobody had defined, and it
> is withdrawn here rather than swapped for a fourth figure.
> ⚠⚠⚠ **AND THE *REPAIRED* RULE — *"the ROW-SPECIFIC half of `why` stays ≤ 200
> words"* — IS NOW WITHDRAWN TOO. THAT IS TWO FAILED VERSIONS OF ONE RULE, AND
> THE THIRD MUST NOT BE A NUMBER THE MANAGER INVENTS.** `TASK_PHP_005` F-5
> measured it against the corpus the 200 came from: **30 of 33 PAT rows break it,
> by up to 12× (2 533 words), and `p01` — the template every row clones — is
> 201.** The 200 was never a limit derived from anything; it was the measurement
> of the single row that had been measured, and it is **enforced by nothing**.
> ⚠ **The line below this one warns that a rule that cannot be met is worse than
> none. It was written in the same breath as a rule that could not be met.**
> → **open item 19**: `TASK_PHP_006` measures the distribution and proposes a
> limit *or* a structural rule, and whatever lands is enforced by a check or
> dropped. Until then there is **no size rule on `why`** — only the standing
> advice that anything long belongs in `.memory-php/` or the row's `NOTES.md`.
>
> ✅ The **byte count** above survived review unchanged (`TASK_PHP_005` §4): the
> 11 003/11 004 gap is a single `'.'` after `check.py`'s `END` marker, both cuts
> are right, and the 200 is exactly 200. **The withdrawal was the correct call;
> the rule built on it was not.**

---

## ▶ START HERE — the next action, in ≤ 20 lines

```
STATE      NO ROWS BUILT. Phase 0 infrastructure EXISTS and is gated.
           (⚠ this box said "NOTHING BUILT ... DO NOT EXIST YET" four lines
           above "TASK_PHP_002 Phase 0 built + gated" -- TASK_PHP_003 m1.)
           Renames landed (RECAP_PAT.md / PLAN_PAT.md); PLAN_PHP.md written.
           EXISTS: patterns-php/ harness-php/ results-php/ .tasks-php/
                   common-php/      NOT YET: .memory-php/ (open item 12)

MINED      TASK_PHP_001 DONE, all 3 axes. 54 candidates, evidence promoted to
           .tasks-php/TASK_PHP_001_MINE/. UNREVIEWED (rule 9).
             temporal 23 cands / 85 of 85 rows / 11 verbatim 10 narrowed 2 modelled
             spatial  16 cands / 18 rows / 8 ptr_cursor / 0 emalloc-dependent
             type     15 cands / 12 mechanism families
           ALL THREE REFUTED THE MANAGER CLAIM THEY WERE NAMED TO ATTACK.

BUILT      TASK_PHP_002 built Phase 0; _003 reviewed it (2 blockers);
           _004 landed them; _005 REVIEWED THAT: 1 BLOCKER, 4 majors,
           7 minors, 9 clean negatives, 3 refutations (2 engineer, 1 manager).
           B1 *NOT* CLOSED -- this box said "B1 CLOSED" and that was FALSE.
                      2 of 5 bypasses land: #include "emalloc_shim.c", and
                      c/<subdir>/*. Both BUILD, LINK and RUN a live allocator
                      into NEITHER digest with the preflight green. (F-1)
           B2 CLOSED  and now better: all 4 attacks on it were clean
                      negatives, and the 3 unrun matrix cells are run. (F-3)

NEXT       (1) TASK_PHP_006 -- LAND TASK_PHP_005's corrections (F-1 blocker
               first). Then review it.
           (2) then the catalogue: .tasks-php/ADJUDICATION_001.md is written
               and settles ~80 rows; TASK_PHP_008 builds
               patterns-php/CATALOGUE.md, and a review attacks both.

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
| **tasks** | `_001` mining wave DONE · `_002` Phase 0 built · `_003` reviewed it · `_004` landed the fixes · `_005` reviewed **those** — **1 blocker open (F-1)**. `_006` = land `_005`'s corrections |
| **infrastructure** | **built and reviewed TWICE**: `harness-php/{root,gate,provenance}.py` · `common-php/` · `patterns-php/{SOURCES.md,php-5.0.0.manifest}` (1170 files, 109 KB) · `.tasks-php/PROTOCOL_PHP.md` · `results-php/`. ⚠ **Reviewed is not the same as correct — the second review found a blocker in the first review's own fix.** ⚠ There used to be a SECOND row in this table also labelled `infrastructure` saying *"not yet built — Phase 0"* (`TASK_PHP_003` m1); it is gone |
| **candidates** | **54** delivered across three axes. ⚠ **`.tasks-php/ADJUDICATION_001.md` takes that to ≈ 80**: +6 splits, −2 merges, **+17 kills reversed**, +1 dropped with no reason recorded, +4 that fell between axes. Evidence in `.tasks-php/TASK_PHP_001_MINE/` |
| **catalogue** | not yet written — `TASK_PHP_008`. The **adjudication** that decides its contents is written and is `.tasks-php/ADJUDICATION_001.md` |
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

*(no ROW findings yet — the first row has not been built. F1–F7 are the mining
wave's and Phase 0's results; **F8–F10 are new this round.** F8 and F9 are
MANAGER work and are **unreviewed** — `TASK_PHP_008` attacks F8, and F9 is a
measurement anyone can re-run. `PROTOCOL.md` rule 9: none of this reaches
`.memory-php/` until it survives review.)*

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
false explanation of an upstream fix.

✅ **CLOSED at `TASK_PHP_004`, and CONFIRMED at `TASK_PHP_005`.**
`PHP_SHIM_SIGNED_MULTIPLY_LONG` is the `#else` arm transcribed character for
character, invoked on `size_t` operands the way `_safe_emalloc` does.
Differential probe over the review's **exact** sample space (same xorshift seed,
same draw, same 20 M): **0 disagreements**, with the `__builtin_mul_overflow`
**must-fire control reporting 84 523** every time.

⚠ **THE CONFIG CLAIM HERE SAID *"gcc/clang × `-O0`/`-O3` ×
`{-DSLB_ISOLATED,-flto}`"* — 8 cells — AND ONLY **5** HAD BEEN RUN
(`TASK_PHP_005` F-3). The same sentence is in `common-php/emalloc_shim.h:462`,
which `digest_bridge.py` pins into every php gate record.** The reviewer ran the
missing three (`gcc-O0-lto`, `clang-O0-lto`, `clang-O3-lto-lld`): **0/20 M,
control firing.** ✅ **The claim is now true and measured** — but it was written
before it was.

⚠⚠ **And `TASK_PHP_004`'s disclosed limitation *"`clang -O3 -flto` cannot link
on this box"* DOES NOT EXIST**: it links with `-fuse-ld=lld`, **the flag
`harness/build.py:169-172` itself inserts for exactly that cell.**
`PROTOCOL.md` rule 13's shape — a published limitation that is not real.

✅ **All four attacks the manager named on B2 were CLEAN NEGATIVES**
(`TASK_PHP_005` §2) and the row is stronger for them: **negative operands** (10 M
signed, control fires 21 170, shim 0); **`dval` compared bit-exactly** (45 M+
samples, 0) — so a `mul_function` row can use the macro as shipped;
**a directed sweep** of 28 900 targeted cases plus 20 M straddling `LONG_MAX`
(controls fire 414 and 3 692, shim 0).

⚠ **The same-TU residual is now PRICED rather than open**: the pristine macro's
whole output stream hashes to `0e813d9ad6308e5a` across **six** configurations —
two compilers × two optimisation levels × `-fwrapv`/`-fno-strict-overflow` — and
`shim == ref` inside each. A shared miscompilation would have to be shared by
gcc and clang *and* be insensitive to `-fwrapv`. **Not zero without a compiled
PHP 5.0.0 binary, but far smaller than "one TU".**

⚠⚠ **THE REUSABLE RULE: *"modelled by an equivalent builtin"* is a claim that
needs a DIFFERENTIAL TEST WITH A MUST-FIRE CONTROL, not a comment.** The shim's
original `SE CONTROL: a true 64-bit overflow IS refused` was a real control and
exercised only the region where the two predicates agree — which is exactly why
it could not see this.

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

⚠⚠ **THE RUN LASTED EXACTLY ONE ROUND. `TASK_PHP_005` F-12 FOUND AN UNEARNED ✅,
AND IT IS THE MANAGER'S.** `TASK_PHP_005.md:51` cites `Zend/zend_alloc.c:295` as
the second `ZEND_SIGNED_MULTIPLY_LONG` call site. It is **`:234`**; `:295` is
`_ecalloc`'s `int final_size`, a *different* mechanism (F5's third truncation).
**The manager's own footnote on the same line had `:234` right**, so this was a
transcription slip between a grep that was run and a sentence that was written —
⚠ **which is the failure mode this project keeps rediscovering: the citation and
the story about it are two separate claims, and running the grep does not check
the prose.** The substance held (there really are exactly two call sites).

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

### F8 — ⚠⚠⚠ THE MINING WAVE'S *KILLS* WERE WHERE THE DEFECTS WERE: EXTRACTION COST WAS WRITTEN AS A CRITERION-3 FAILURE

**Manager audit, `.tasks-php/ADJUDICATION_001.md`. UNREVIEWED — `TASK_PHP_008`
attacks it.**

All three miners were scrupulous about the bias `CLAUDE.md` rule 6 names, and
each said so in terms; the reject tables carry a C-side reason for every row.
**But `PLAN_PHP.md` §3's criterion 3 is about the KERNEL SHAPE — flat blob in,
`u64` out. How much C you must carry along is the TIER.** The spatial reject
table's criterion-3 bucket is full of *"the surrounding machinery is the
program"*, *"mutually recursive over a 4000-line file"*, *"the blob would have to
encode a backtrace"* — **tier assignments wearing a kill's clothes.**

✅ **Fourteen were opened in the pristine tarball. TWELVE refute the reason that
killed them, and two of those are FIVE LINES:**

- **CRASH-123**, killed as *"a whole conversion framework"*: `mbfl_convert.h:49`
  `int cache;` · `mbfilter_htmlent.c:161` `filter->cache = (int)mbfl_malloc(…)`
  · `:169` `mbfl_free((void*)filter->cache)` · `:177` `char *buffer =
  (char*)filter->cache;` · `:181` `buffer[0] = '&';` — **a heap pointer stored in
  an `int`, cast back, freed and written through.** The corpus gives it the only
  bespoke invariant in 166 rows (`pointer-value-integrity`), and it was routed to
  the *spatial* miner, so the **type** miner never saw it.
- **CRASH-157**, killed as *"the blob would have to encode a backtrace"*:
  `zend_exceptions.c:310` reserves `+2` for a format string with **four** literal
  characters. **The backtrace is the caller.**

⚠⚠ **THE REUSABLE RULE, AND IT IS F1'S SIBLING: extraction cost, like the
citation, must be priced at the DEFECT SITE, not at the frame the defect flows
into.** F1 says `c_file_line` names the faulting frame; this is the same error
with cost substituted for citation.

✅ **Also measured against the corpus (166 rows in `index.csv`):** the 54
candidates mention **123**; **43** are covered by nothing; and of those 43,
**exactly one — CRASH-008, `datetime.c:359`, `case 'U': size += 10;` — is named
in no axis's `NOTES.md` at all.** ⚠ 42 of 43 carry a recorded reason, so the
silent-skip class fired **once**, not systematically — that is a good rigour
result and is recorded as one. ⚠ Five more rows were **routed** between axes and
never picked up by the receiving axis; **a routing decision is not a kill and is
not a delivery either.**

### F9 — ✅ NOT ONE SPATIAL ASan REPORT IN THE CENSUS IS IN THE CODE THE SPATIAL AXIS MINES

**Manager measurement. This CLOSES open item 7 — and the answer is that the
check cannot be done.**

✅ First, the wave's census is **confirmed exactly**: 2534 log files, **3199
reports** (567 logs hold more than one), split **2450** heap-buffer-overflow /
**490** heap-use-after-free over 336 logs / **189** use-after-poison / **70**
global-buffer-overflow. ⚠ `grep -c` returns **double** these; the wave counted
reports, and reports is right.

⚠⚠⚠ **Then the faulting frame, per report.** Of the 2520 *spatial* reports:
**2156 fault inside `libmysqlclient.so.14` — a different shared object** —
in its XML charset-file parser (`memcmp ← my_xml_scan ← my_xml_parse ←
my_parse_charset_xml ← my_read_charset_file`), and the other **364** in the regex
matcher reached from `ext/pcre/`. ⚠ I could **not** prove which function
`php_pcre_exec` is — it appears nowhere in 5.0.0's `ext/pcre/` sources, so the
name comes from the census build's own configuration. **The claim that does not
depend on that: ZERO of the 2520 spatial reports fault in `Zend/` or
`ext/standard/` — the code every one of the 16 spatial candidates is drawn
from.** The temporal mass, by contrast, is genuinely PHP engine code.

→ **Open item 7's action changes from *"go measure them"* to *"the census cannot
speak to this axis"*.** Every spatial `hotness` stays labelled **reasoned**, and
the census is struck as a possible source of spatial frequency evidence rather
than left as an open promise. ⚠ This is **not** the LTO story — those frames
resolve fine; they resolve to another library.

⚠ **What this does NOT license.** *"A corpus built by reading the source finds
what a sanitizer on real traffic does not"* is a **rhetorical** claim and this
programme has **not** demonstrated it — no php row is built. Keep it out of the
report until rows exist.

### F10 — a guard that is a string search is a guard with a spelling

`TASK_PHP_005` F-1: `gate.py`'s allocator audit decides "this row uses the shim"
by searching `<row>/c/*` for the literal `emalloc_shim.h`. Two spellings get
round it — `#include "emalloc_shim.c"` (the audit knows only the `.h`) and
`c/<subdir>/*` (the glob is non-recursive) — **and both rows build, link and run
a live allocator** (`alloc tally = 7688571`) into **neither digest**, preflight
green. ⚠ It also **false-positives** on a row that merely mentions the header in
a comment — which is the spelling `PLAN_PHP.md` §4.3 *tells* a non-allocating row
to use (F-8).

⚠⚠ **`TASK_PHP_004`'s own `.memory-php/` candidate #2 was *"a word in a document
is not an enforcement mechanism"*. F-10 is the sequel: _a check that greps for a
word is barely more of one._** The audit needs to key on what the *compiler*
sees, not on what the text says.

## Open items — carried, not closed

| # | item | note |
|---|---|---|
| 1 | The pristine tarball lives under **another project's gitignored `.temp/`** and is deletable at any time | Phase 0 must land `patterns-php/SOURCES.md` with the sha256 + a per-file manifest before anything cites it |
| 2 | *"Where does the existing Rust port land on these scales?"* | **deferred, not deleted** (`DP-05`). Well-posed once the corpus exists |
| 3 | `.web/` does not know `results-php/` exists | deliberate. Do not teach it until there is something worth publishing |
| 4 | **CRASH-136 (exif) was rejected on EXTRACTION COST** | ⚠ the bar does not permit that as a kill — cost is a *tier*, not a filter. **Manager must re-adjudicate.** The most likely place the spatial axis lost a real row |
| 5 | `EG(garbage)` is `zval *garbage[2]` with an unchecked `EG(garbage)[EG(garbage_ptr)++]` | a faithful temporal extraction **inherits a SPATIAL overflow**. Flagged, not bounded away — bounding it silently would be §4.2's invented non-defect. Manager decides |
| 6 | Four temporal merges flagged as probably wrong | ranks 21, 8, 12, 23. Split decisions owed at catalogue adjudication |
| ~~7~~ | ✅ **CLOSED at F9 — and the check turned out to be impossible.** All spatial `hotness` fields stay **reasoned** | The census holds **zero** spatial reports from `Zend/` or `ext/standard/`: 2156 of 2520 fault inside `libmysqlclient.so.14`, the rest in the regex matcher. **The census is struck as a source of spatial frequency evidence** rather than left as an open promise |
| 8 | Rank 15 (CRASH-158) may be spatial, not temporal | cross-check the two miners' lists at adjudication |
| 9 | ⚠⚠ **No php marginal `Ir` is comparable to any PAT one — and no two php runs are comparable to each other either** | `repo_path_bytes` is **15** bytes longer through the shim (⚠ this said **20**; corrected at `TASK_PHP_003`), and `gate.py`'s own `PYTHONDONTWRITEBYTECODE=1` adds `nvars` **+1** and `envp_stack_bytes` **+34** — measured directly at `TASK_PHP_004` (`25 + NUL + one 8-byte envp slot`). ⚠ **`TASK_PHP_003` gave that as +33 and that was a record-to-record difference between two SHELLS, not the variable's cost**: `ph00`'s own `envp_stack_bytes` moved **3686 → 3695** across two runs of the same gate with no source change, so the p01 delta was +33 and is now +42. **Never quote a php figure against a `pNN` one, and re-check the env block before quoting one php figure against another** |
| 10 | ⚠⚠⚠ **STILL OPEN — `common-php/*.h` is in NO gate digest, and the `<row>/c/` symlink that was supposed to close the measurement half is BYPASSABLE** | `check.py`'s three `common/` globs are non-recursive and none matches `emalloc_shim.h`. The bridge half **fires** (F7). The symlink half was enforced by nothing (B1), was checked in `gate.py`'s preflight at `TASK_PHP_004` — and `TASK_PHP_005` **F-1** got round it twice, with rows that build, link and run a live allocator into neither digest. **`TASK_PHP_006` closes it** |
| 17 | ⚠⚠ **PAT-SIDE, LATENT, AND DELIBERATELY NOT FIXED: `check.py:10314` and `measure.py:226` glob `<row>/c/*` NON-RECURSIVELY and drop the directory entry with `isfile()`** | so **every source file a row puts in a `c/` subdirectory is in no digest at all**, and `check.py`'s `--no-build` staleness scan misses it too, so editing one does not even mark a binary stale. ✅ **No row is affected today** — `find patterns patterns-php -mindepth 3 -maxdepth 3 -type d -path '*/c/*'` is empty. ⚠ **Fixing it is a `harness/` edit = a 33-pattern re-gate for zero present benefit.** Decision: **do not fix; FORBID the layout on the php side** (`TASK_PHP_006`), and carry this row so the next person to reach for `c/sub/` finds out first. ⚠ It matters more here than on PAT: php rows are *extracted* C and `c/zend/` is an ordinary thing to want |
| 11 | A new php row costs **six commands (~28 min)**, not three | `gate → report → gate` is irreducible and `measure.py` builds nothing. Budget it. ✅ The three places that said three/five now say six (`TASK_PHP_004`) |
| 12 | `.memory-php/` **does not exist yet** | `PLAN_PHP.md` lists it, `TASK_PHP_002` did not ask for it, and rule 4 makes it the manager's. Create it when the first finding survives review |
| 13 | ⚠ **`harness-php/*.py` is in NO digest, and putting it in one costs a 33-pattern re-gate** | `check.py`'s `srcs` would have to reach `harness-php/`, i.e. a `harness/` edit (`PLAN_PHP.md` §2.1). `TASK_PHP_004` landed the **cheap half**: `gate.py` writes `results-php/preflight/<row>.preflight.json` with the `harness-php/*.py` hashes, the manifest hash and whether `--no-provenance` was used. ⚠ **That record is evidence, not a pin — nothing hashes it** — ⚠⚠ **and `TASK_PHP_005` F-2 found it is worse than that: it is written one file per ROW, not per run, so a later preflight ERASES `provenance_skipped: true`; nothing anywhere detects a missing record; and the manager had made it uncommitted.** Being fixed at `TASK_PHP_006` (item 18) |
| 14 | ⚠⚠ **`provenance.py`'s overlap floor is SATISFIED BY DEAD CODE — the risk is a false PASS, not a false refusal** | Added at `TASK_PHP_004` for `TASK_PHP_003` M5. ⚠ **This row used to say the danger was a good row tripping a floor. `TASK_PHP_005` F-4 shows the opposite**: a kernel that implements *division*, cites *multiplication*, and hides the citation behind `#if 0` scores **100 % and is ACCEPTED** (`_normalise` drops lines starting with `#`, so `#if 0`/`#endif` vanish and everything between them counts); the same kernel without the dead block is refused at 11 %. ✅ **The floor is not too high** — a realistic `verbatim` `mul_function` lift scores 68 %. ⚠ **The check never reads `main.c`, the driver loop or the build, so it measures presence of TEXT IN A FILE, not presence of code in the benchmark**: a pass is not even evidence that the cited lines are compiled |
| 16 | ⚠ **`TASK_PHP_004` edited `RECAP_PHP.md` — the manager's own handoff file** | `PROTOCOL.md` rule 4 reserves the state layer to the manager, and `TASK_PHP_004.md` did not forbid it explicitly. ✅ **The content is ACCEPTED — it is more accurate than what the manager was about to write** (the `+34` vs `+33` shell artefact, the `3686 → 3695` instability, items 13–15). ⚠ **But the boundary is real**: an engineer correcting the manager's numbers *in the manager's file* is how an unreviewed claim reaches the state layer without passing rule 9. **Future php task files must say explicitly that `RECAP_PHP.md` is manager-only** — the fix is one sentence in the task template, not a rollback of good work |
| 18 | ⚠ **The manager GITIGNORED `results-php/preflight/` and that was WRONG — reversed** | `.gitignore:24-26` justified it as *"carries a `when` timestamp and the literal `gate_argv`, so it churns"*. ⚠ **`TASK_PHP_005` F-2c measured it: only `when` moves.** `sha256(rest)` is identical across two runs (`d91ce008ad273b36`) and `gate_argv` is a function of the command, **which is exactly the evidence M6 wanted**. The split the manager asked the reviewer to price **exists and costs one field**. → `TASK_PHP_006` commits the record without `when` and fixes the per-row overwrite |
| 19 | ⚠⚠ **The 200-word `why` rule is WITHDRAWN as a number — it was calibrated on n = 1 and is broken by 30 of 33 PAT rows** | `TASK_PHP_005` F-5: up to **2 533** words, and **`p01` — the template every row clones, and the row `PROTOCOL_PHP.md` cites as complying — is 201.** The 200 was simply the measurement of the one row that had been measured. ⚠⚠ **This is the THIRD version of this rule and the second that could not be met**; `RECAP_PHP.md` itself warns that *"a size rule that cannot be met is worse than none"*. **The manager must not invent a fourth number** — `TASK_PHP_006` measures the corpus distribution and proposes a limit, or proposes a structural rule instead, **and whatever lands must be enforced by a check or dropped** |
| 20 | ⚠ **`gate.py <row> --preflight` silently forwards `--preflight` to the tool and runs it** | `argparse.REMAINDER` collects from the first positional (`TASK_PHP_005` F-7). ⚠⚠ **The manager's own 06:55 `ph00.preflight.json` — cited as manager-verified evidence for the gitignore decision — is an instance: a FAILED `check.py` launch (`tool_returncode 2`) recorded as a preflight.** Part of the evidence for a manager decision was an artefact of a CLI bug |
| 15 | ⚠ **The php staleness check is `gate.py --tool measure --check-stale`** and the mandated PAT `66/0` one does **not** examine `results-php/` at all | Both are now in `PROTOCOL_PHP.md` §E1 (`TASK_PHP_004`); today the php side is **2 records** |
