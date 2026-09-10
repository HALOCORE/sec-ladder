# RECAP_PHP — the handoff document for the PHP programme (`patterns-php/`)

**Read this first, always.** The manager updates it at every task boundary.
For the *other* programme (`patterns/`) read `RECAP_PAT.md`; for the split
between them read `CLAUDE.md`'s top table.

> ⚠⚠ **SIZE DISCIPLINE — AND EVERY NUMBER THIS BOX ONCE GAVE FOR IT WAS WRONG.**
> `RECAP_PAT.md` really did reach **560 KB**, and **the START HERE box stays
> ≤ 20 lines.** Everything else here was invented or miscalibrated:
>
> | this box said | measured |
> |---|---|
> | a `why` became *"a ~7,000-word JSON string"* | **no such row.** `p01`, the row meant, is **2 057**; the largest anywhere is `p16-tlv-walk` at **4 995** |
> | *"a `why` stays ≤ 200 words"* | unsatisfiable — the gate mandates an 11 003-byte shared block |
> | *"the ROW-SPECIFIC half stays ≤ 200 words"* | **30 of 33 PAT rows break it**; `p01`, the template, is 201 |
>
> ✅✅ **SETTLED AT `TASK_PHP_006` §5: THERE IS NO SIZE RULE ON `why`, AND THAT IS
> THE ANSWER, NOT A GAP.** Distribution over 33 PAT rows + `ph00`: **min 197 ·
> median 989 · p90 1817 · max 3140.** Any limit at or under q1544 refuses a
> quarter of the built corpus; any limit the corpus meets permits 3× the median.
> Imposing one on PAT means editing text *inside the hashed block* on 33 rows —
> **33 re-gates for a style rule.** The manager's structural alternative was
> **also** unsatisfiable (**not one `why` in either programme contains a single
> newline**, so no row has a second paragraph). What replaces it:
> `gate.py::why_sizes` **reports** each php row's size on every preflight and
> **cannot fail a run**. A reported size is not a rule — which is why it is safe.
>
> ⚠⚠⚠ **THE LESSON IS THE PROPAGATION, NOT THE ARITHMETIC.** The 7 000 went:
> manager task file (`TASK_PHP_002.md:149`) → this box → an engineer citing it
> back as *"the figure **that motivated the size rule**"*
> (`TASK_PHP_002_REPORT.md:492`). **Three versions of a rule were written, two
> failed, and the justification for all three was a number nobody had measured.**
> `PROTOCOL.md` rule 14, and the **second** time here — the first was *"123 ASan
> reports"* (F4). **A premise in a task file is one an engineer has no reason to
> doubt.**
>
> ⚠ Detail — the 11 003/11 004/11 006 byte count, its withdrawal, and
> `TASK_PHP_005` F-5's own wrong span (it measured the prefix only, making the
> corpus **maximum**, `p16-tlv-walk` at 3 140, look like the minimum at 109) — is
> in `TASK_PHP_005_REPORT.md` §4 and `TASK_PHP_006_REPORT.md` §5. ⚠ **This box
> had grown to 74 lines about keeping documents short.**

---

## ▶ START HERE — the next action, in ≤ 20 lines

```
STATE   ROWS BUILT 3 -- ph03+ph07 (S1) and ph16 (S2, FIRST NON-S1). 20 families,
        S2 now owes 1. CATALOGUED 102, VERIFIED. .memory-php/ is AUTHORITATIVE.
NEXT    NOTHING RUNNING. _023/_024/_025 ALL LANDED; gate PASS, brackets 66/0 and
        8/0. ONLY _026 (F50's census channel) is written+undispatched. Then pick
        row 4: ph29 -> ph12 -> ph21 (F46), or a NEW family. NOT ph21 first.
⚠ NEW   F56 ⚠⚠⚠ GCC WAS ALREADY ENFORCING ph16's OWN BOUND -- _FORTIFY_SOURCE=3
        makes FD_SET __fdelt_chk, +60.6%; R1 was not R1 in half the gcc cells.
        NOT ph03/ph07 (checked). F57 ASan BLIND, MIRI FIRES -- and the oracle was
        upstream's own wfds. F54 a why can be wrong in every number, right in
        every verdict -> §H. F52 a probe that MAKES the state it measures.
⚠ TRAPS `grep -a` ALWAYS (blind to 41 corpus files); ask about a FUNCTION, not
        text. ⚠⚠ A PROBE WHOSE SETUP ENCODES THE ANSWER evaluates fine and is
        wrong -- CHANGE THE SETUP'S ARBITRARY CONSTANT AND SEE IF IT MOVES (F52).
⚠ COST  ONLY ph07 searched spellings: +11.98% bound / +1.96% cheapest-found, R4
        degenerate. ph03 AND ph16 owe BOTH, so NO ph16 figure is a fixed-R4
        bound (item 26). F39 WITHDRAWN (F42).
BAR     C-SIDE ONLY: nothing about Rust/Verus/Miri/cost kills a row, and
        patterns-php/ is FRESH. ⚠ .web/ is CONCURRENT -- NEVER `git add -A`.
READ    .memory-php/ · PLAN_PHP.md · PROTOCOL.md · CATALOGUE.md · QUOTA_001.md
        · F1-F57 · items 1-44. CHECK .tasks-php/{box,cite,cover,quot}*.py.
```

---

## What is true now

| | |
|---|---|
| **rows built** | **3 — `ph03`, `ph07` (both `S1`) and ⭐ `ph16` (`S2`, the FIRST outside `S1`)**. ⚠ Kept below because its lesson outlived the arithmetic: **2, and ⚠⚠ THEY WERE THE SAME FAMILY** — `ph03-uudecode-bound` and `ph07-strcut-cursor` are **both `S1`, unbounded cursor walk**, 1 of the catalogue's **20**. Both reviewed; `ph07` is being **rebuilt** at `TASK_PHP_018` (F43). Each five rungs + R1h. ⚠ **This row said *"2"* for four tasks and no document said they were one family** — the cost of that, and the quota rule that comes out of it, are open item 34 / `QUOTA_001.md`. (`ph00-smoke` is a relocated PAT calibration kernel, throwaway, **no PHP provenance**, and prices nothing) |
| **tasks** | **26 written, `_001`–`_026`; 25 have reported; NOTHING RUNNING.** ▶ **`_026` (F50's census channel) is the only one left undispatched.** `_001` mining · `_002`–`_011` Phase 0, built and reviewed twice · `_012` catalogue corrections + row-1 prep · `_013`/`_014` **`ph03` built and reviewed** · `_015` `ph07` prep (**stalled on *"no fix exists"*, overturned — F34/F38**) · `_016`/`_017` **`ph07` built and reviewed** · **`_018` `ph07` REBUILT** (new R1h, spellings control, `extra_spans`) and **`_022` reviewed it** · `_019` the C.1/C.4 mechanism test (**9 new rows adjudicated**) · `_020` the catalogue's error rate · **`_021` STOPPED ITSELF** — 3 of 9 triggers failed, so the catalogue is **unchanged at 93** and `land_019_020.py` waits. ▶ **`_023` (review the nine, then land) is RUNNING. `_024` (`ph07`'s hashed `why` + `extra_spans`), `_025` (BUILD `ph16` — row 3, and the first outside family `S1`) and `_026` (F50's census channel, ⚠ **dispatch after `_023` lands**, because it counts catalogue rows) are WRITTEN and NOT DISPATCHED.** ⚠ **≈ 3.5 tasks per built row** against `PLAN_PHP.md` §8's PAT-measured ~3, and ⚠ **the *"and falling"* is a projection with n = 2, not a measurement** (`QUOTA_001.md` §2). ⚠ **This row was stuck at `_006` for fourteen tasks** — rule 13 |
| **infrastructure** | **built and reviewed TWICE**: `harness-php/{root,gate,provenance}.py` · `common-php/` · `patterns-php/{SOURCES.md,php-5.0.0.manifest}` (1170 files, 109 KB) · `.tasks-php/PROTOCOL_PHP.md` · `results-php/`. ⚠ **Reviewed is not the same as correct — the second review found a blocker in the first review's own fix.** ⚠ There used to be a SECOND row in this table also labelled `infrastructure` saying *"not yet built — Phase 0"* (`TASK_PHP_003` m1); it is gone |
| **candidates** | **54** delivered across three axes. ⚠ **`.tasks-php/ADJUDICATION_001.md` takes that to ≈ 80**: +6 splits, −2 merges, **+17 kills reversed**, +1 dropped with no reason recorded, +4 that fell between axes. Evidence in `.tasks-php/TASK_PHP_001_MINE/` |
| **catalogue** | ✅ **`patterns-php/CATALOGUE.md` — 102 rows, LANDED AND VERIFIED** by `TASK_PHP_023` (⚠ this line has said **91** and **93**; count it, do not trust it: `python3 .tasks-php/quota.py`). **20 mechanism families**, unchanged by the landing — spatial **42** · type **29** · temporal **31**. ✅ **Part A and Part B agree row-for-row, and every row is filed under the same axis in both** — the `ph92`/`ph93` mismatch is gone. ✅ `coverage.py` **166/166, MISSING 0**; all 8 withdrawn `C.1` kills present in place with their notes. ⚠⚠ **Two landed sentences were measured FALSE and are corrected in `CATALOGUE.md` AND in `land_019_020.py`** (F52 `ph94`'s trigger, F53 `ph32`'s *"one commit"*) — a landing script left carrying a refuted claim is a cited artefact. ⚠ **`_023` reviewed the nine admissions and would overturn NONE of `_019`'s reversals**; ~70 citations opened across 15 files, including the ones `_019` called correct. ⚠ **Parts A/B beyond the nine are still UNREVIEWED**, and `_020` measured the mechanism sentences right and the `▸ trigger` lines wrong (F46). Part A is a scannable table, Part B a ~150-word block per row, Part C the kill list with a re-derived criterion per kill |
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

> **Index** — F1 citation frames · F2 CSV authoritative · F3 `crashes_pristine`
> not absence · F4 the 123-ASan misread · F5 third allocator truncation · F6 the
> shim invented defects · F7 the digest gap fires · **F8 kills priced at the wrong
> frame** · **F9 no spatial ASan report is in PHP code** · F10 a grepping guard has
> a spelling · F11 ask the compiler · F12 three size rules on an invented number ·
> **F13 a refuted mechanism is not a licence** · F14 `0 STALE` ≠ pinned · F15 the
> cheapest correct design · **F16 wrong enumeration ≠ unboundable** · F17 the
> deadlock that denies itself · F18 whitelists fail on contact · F19 success
> conditions do not travel · F20 one `..` too few · **F21 auditing only what you
> doubt** · **F22 a kill written as a set** · F23 citations inside the citation
> finding · F24 shared header, not directory · F25 the `ph11` measurement · F26
> the fix is a 1.4 KB fetch · F27 set-kills, three instances · F28 demotion cost ·
> **F29 the 2004 fix is dead AND incomplete** · F30 negative-cost safety check ·
> F31 two frozen-harness limits · F32 ⚠ the manager arbitrated the un-arbitrable ·
> **F33 the first ladder** · **F34 the guard moved to the prologue** ·
> **F35 ⚠⚠ this box's `grep` is silently blind to `string.c`** · **F36 the next
> batch's four fixes, and two of them DELETE the guard** · **F37 the kills that
> survived the audit are the ones written down as settled** · **F38 ⚠⚠ the
> `fix_commit` was a column in the corpus index, and it is not always THE fix** ·
> **F39 ⚠⚠ ph03's ladder is a pair of spellings and its own contract says so** ·
> **F40 the fix hunt is done for the whole catalogue, once** · **F41 row 2, and
> the two rows disagree about what safety costs** · **F42 ⚠⚠ row 2's headline
> refuted by construction, and F39's direction withdrawn** · **F43 ⭐⭐⭐ PHP
> deleted half its own security fix, and stage 7h had already said why** ·
> **F44 ⚠⚠⚠ 2 of 13 kills correct as written; the rate tracks the TEST, not the
> rows; and "merged by the corpus itself" is the weakest evidence there was** ·
> **F45 ⭐⭐⭐ a defect made invisible by the commit that fixed its warning** ·
> **F46 ⭐⭐ the catalogue's mechanism sentences hold; its `▸ trigger` lines do
> not, and that is the half a build task runs** · **F47 ⭐⭐⭐ row 2 rebuilt: it
> was shipping a rung PHP itself calls a bug, and no strength of
> memory-safety-only proof would have moved** · **F48 ⚠⚠⚠ I accepted a refusal and then landed the
> same rule with the verbs changed** · **F49 ⭐⭐⭐ the stop condition fired: 3 of
> 9 new rows' triggers failed, and F46 predicted which half would** · **F50 ⭐⭐ a
> fix commit is a CENSUS of its defect's siblings — `ph16`'s patches four sites
> and we catalogued one (MANAGER, UNREVIEWED, n = 1)** · **F51 ⚠⚠ the committed
> claim layer rests on gitignored scratch in ten places, two already gone —
> including the catalogue's own coverage claim** · **F52 ⚠⚠⚠ the probe made the
> state it was measuring, and so did mine, twice, the same week — `ph94`'s
> original claim is restored** · **F53 ⚠⚠⚠ a shared upstream fix is not evidence
> of a shared mechanism; `PROTOCOL_PHP.md` §G replaces the folklore rule** ·
> **F54 ⭐⭐ a declaration can be wrong in every number and right in every verdict** ·
> **F55 ⚠ the preflight record is keyed by the name you typed** ·
> **F56 ⚠⚠⚠ the compiler was already enforcing the bound the row is about, at +60.6 %** ·
> **F57 ⭐⭐⭐ row 3: ASan blind, Miri fires, and the oracle was in upstream's own frame**

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

### F11 — the guard that closed B1 asks the COMPILER, and that is the transferable part

`TASK_PHP_006` closed F-1 by **replacing the string search with `gcc -MM`** over
`build.py`'s own TU list under both `-DSLB_ISOLATED` states, intersected by
`realpath`. ✅ **Priced before it was adopted: 2 calls, ~115 ms/row** — the
manager had worried it would be unaffordable and was wrong. All eight of the
reviewer's fixture rows land from their **unmodified** generator, and **F-8's
false positive closes as a side effect**, because a comment is not an include.

⚠⚠ **The manager's suggested fallback would NOT have worked.** `TASK_PHP_006.md`
called *"require the name inside an `#include` on the same line"* the obvious
repair; it would have left `ph53-subdir` open, because that bypass is about
**where the file is**, not how the include is spelled.

⭐ **The rule: a guard that greps has a spelling, and its spelling is a
vulnerability. Ask the tool that actually decides.** This is the third step of
one staircase — `TASK_PHP_004`: *a word in a document is not an enforcement
mechanism* → `TASK_PHP_005` F-10: *a check that greps for a word is barely more
of one* → here: *ask the compiler.*

### F12 — three size rules were justified by a figure nobody had measured

Detailed in the size box above. ✅ `p01`'s `why` is **2 057 words**, not the
*"~7,000"* the manager wrote into a task file, copied into the state layer, and
an engineer then cited back as the rule's motivation. **The lesson is `PROTOCOL.md`
rule 14 and this is its second instance on this programme** (after F4's *"123
ASan reports"*): a premise stated as fact in a task file is one an engineer has
no reason to doubt, and it comes back as evidence.

⚠ **The reviewer's own correction was also mis-measured** — `TASK_PHP_005` F-5
took the row-specific half as the *prefix only*, so `p16-tlv-walk`, the corpus
**maximum** at 3 140 words, appears in its table as the **minimum** at 109.
**Three parties measured this quantity and all three got a different span.**

### F13 — ⚠⚠⚠ A REFUTED MECHANISM IS NOT A LICENCE FOR THE DESIGN IT ARGUED AGAINST

**The manager's own error, caught by an engineer before it shipped, and the most
useful thing this round produced.**

`TASK_PHP_006` justified *"a missing preflight record is a NOTE, not a failure"*
with an **asserted** deadlock. `TASK_PHP_007` M4 **disproved** it by running it —
and said in terms *"I am not recommending the hard failure."* ⚠ **The manager
asked for the hard failure anyway**, reading a refuted mechanism as a cleared
design.

Composed with M5 (*a record whose every run FAILED counts as no record*) the hard
failure is **self-referential** and deadlocks the **fresh-clone path** for ever,
with no escape flag:

```
run 1  no record          -> coverage problem -> PREFLIGHT FAILED -> writes a record whose only run FAILED
run 2  record exists, only run FAILED (M5) -> coverage problem -> PREFLIGHT FAILED
run N  ... and nothing an operator can do fixes it
```

✅ **The engineer did not find this by reading. It wrote the loop, ran it,
watched six runs never converge, and repaired it before shipping** — by
discounting the audit's *own* coverage problems, on the honest reading that a run
which failed only on another row's paperwork still certified **this** tree. The
naive rule survives as a **must-fire control**, and `_run_is_certifying`'s
docstring forbids simplifying it back.

⚠⚠ **The rule: refuting the ARGUMENT for a decision does not establish its
opposite.** The original engineer's *conclusion* — loud beats unrunnable — had a
real case behind it that its *stated mechanism* got wrong. That is
`PROTOCOL.md` rule 9's conclusion-versus-mechanism split arriving from the other
side, and the manager walked into it while holding a correct refutation.

### F14 — `0 STALE` does not mean "everything is pinned"

`harness/measure.py::_compare` iterates the **recorded** keys, so **a file ADDED
to a row is invisible to `--check-stale`** — it has no key, so it cannot be
stale. ✅ Observed, not reasoned: adding `c/emalloc_shim.h` to `ph00` left the
measurement record `FRESH` while the file sat on disk unrecorded.

⚠⚠ **This is the bracket every task file in this programme mandates twice**, and
its true meaning is *"every source that was pinned still matches"*. What closes
the gap is the **preflight**, not the digest — `shim_link_audit` refuses the row,
so a gate cannot pass in that state.

⚠ It is a `harness/` property and affects **all 33 PAT rows identically**. Not
fixed: the fix is a `harness/` edit and a 33-pattern re-gate. → `PROTOCOL_PHP.md`
§E carries the sentence.

### F15 — the cheapest correct design was the one already in the docstring

✅ **Manager cost claim refuted, in the manager's favour.** *"An `emalloc_shim.h`
edit will re-gate every php row"* — the **gate** half has been unconditional
since `TASK_PHP_002`, because `digest_bridge.py`'s own hash is in every php gate
record. The marginal price of *"every row"* over *"every allocating row"* is the
**measurement** half only: a re-measure (~8 min) plus a render.

⚠ **And the measurement the manager said it had not made is one command**:
`git log -- common-php/emalloc_shim.h` → **3 edits in 7 php tasks, two of the
three for PROSE.** That cuts *against* the design — a comment fix costing a
corpus-wide re-measure — and the mitigation is already protocol: **batch prose
fixes, never land one alone** (`PROTOCOL.md` rule 6, verbatim).

Three cheaper designs were considered and rejected, recorded so nobody
re-derives them. ⚠ **The instructive rejection is versioning the shim**
(`emalloc_shim_v1.h`, each row links what it measured under): correct by
construction *and* cheaper, and **wrong, because it inverts the property we
want** — a shim fix that does not propagate leaves rows measured under a
known-wrong allocator silently and for ever, converting a loud re-measure into a
quiet divergence.

### F16 — ⚠⚠ A WRONG ENUMERATION IS NOT AN UNBOUNDABLE ONE

**The manager had this backwards, and the correction is worth more than the bug
it is about.**

`TASK_PHP_009` M1: a **dotted row directory** hides from `glob("patterns-php/*")`,
so all four audits skip it while `build.py::pattern_dir` (`os.listdir`) and
`provenance.py` both resolve it. ✅ Demonstrated end to end on the real tree —
`gate.py --preflight .ph93` returns **rc=0** on a row carrying a regular-file
allocator copy *and* an unkeyed subdirectory source, printing *"ok every
`patterns-php/*/c/` file has a digest key"*, with the identically-defective
normally-named row refused as the fired control.

⚠ **The manager wrote: *"if a row can hide from `glob`, the whole argument
collapses and we are back to whack-a-mole with a smaller board."* That is
wrong:**

> The idiom detector's defining property was that **no complete enumeration
> existed** — no function anywhere returns "every way to spell an `#include`".
> For rows one **does**, it is a single call, and `build.py:81-89` already uses
> it. The audit and the builder can be made to enumerate **the same set**, and
> that set is provably complete against the only resolver that decides what gets
> compiled.

⚠⚠ **Treating a wrong enumeration and an unboundable one as the same failure is
how a fixable bug gets priced as a phase.** The fix is a substitution
(`os.listdir` for `glob`), not another round of the game — which is exactly the
property the unconditional-link design was adopted for, and it survives.

### F17 — the second deadlock, and its message denies it

`TASK_PHP_009` M3: `preflight_coverage_audit` is a **GLOBAL** stage, so **one**
uncertifiable record fails **every** `gate.py` invocation — including the
bracket every task file mandates twice. An orphan `results-php/<row>.json` (a
retired row whose committed records survive — `PLAN_PHP.md` §3 *expects* rows to
be retired) cannot obtain a certifying run, because the prescribed repair fails
on **provenance**, which is substantive. ✅ Run end to end: three cycles,
non-convergent; the actual fix (delete the record) appears nowhere in the
message.

⚠⚠ **And the message printed at that moment says *"⚠ THERE IS NO DEADLOCK"*** —
the same shape as the *"dead code … Not treated as a shim user"* note that
`TASK_PHP_008` deleted for exactly this reason: **a reassurance that tells the
reader not to look further.** ⚠ It is escapable and destroys nothing, which is
why it is not a blocker.

⭐ **One change closes M3 and M4 together: make the coverage stage report
PER-ROW rather than globally.** The global scope is what turns any single
uncertifiable record into a programme-wide stop, and it is the property §8b's
first deadlock also rode on.

### F18 — both whitelists this manager wrote were wrong on first contact with the corpus

⚠ **`{c, inputs, controls}` as specified refused ALL 33 BUILT PAT ROWS** — every
one carries `__pycache__/`. Measured 33/33 before shipping, and exempted.

That is the **second** whitelist-shaped decision in this programme and the second
to fail: the `c/<subdir>` ban was **both insufficient and over-strict**
(`TASK_PHP_009`), and this one was over-strict the moment it met the tree.
⭐ **The transferable part: a whitelist written from the layouts you INTEND is
not a whitelist over the layouts that EXIST. Run it against the corpus before
shipping it** — which is what caught this, and cost one command.

✅ The manager named it as a least-sure call both times, and both times that was
the right instinct and the wrong artefact.

### F19 — *"show it converges"* was the wrong success condition

⚠ The manager's `TASK_PHP_010` §3 asked the engineer to *"show it converges"*.
**A retired row's orphan record never converges by repetition, and must not** —
the repair is **deletion**, not iteration. The right condition was *"it stops
blocking"*, and the engineer supplied it.

⚠ **This is the same error as F13, one level down.** There the manager read a
refuted mechanism as a cleared design; here it carried a success condition
(*convergence*) from the **fresh-clone** deadlock, where repetition **is** the
repair, into the **orphan-record** one, where it never can be. **A success
condition is part of a design and does not travel with the shape of a bug.**

### F20 — one `..` too few

⚠ `#include "../../shared/x.h"` from `<row>/c/` reaches `patterns-php/shared/`,
**compiles, runs the outside allocator (`tally=7`), and is in neither digest** —
and it is not a directory *under* the row, so `ROW_DIRS` cannot see it. It is
`TASK_PHP_009` M2 with one more `..`.

✅ **Latent on both sides today: no row has such an include.** Reported and
deliberately **not fixed**, because both repairs are worse than the risk: parsing
`#include` targets is the **idiom-enumeration class this programme has deleted
twice**, and the spelling-free version (`-MD`) needs a `harness/` edit and a
33-pattern re-measure. ⚠ **The discipline is written into `PROTOCOL_PHP.md` §B3a
instead — `<row>/c/` holds everything the row compiles, checked by eye at
review** — so the next author is not told the guard is stronger than it is.

### F21 — ⚠⚠⚠ THE AUDIT LOOKED AT THE KILLS IT SUSPECTED AND NEVER AT THE KILLS IT UPHELD

**`ADJUDICATION_001.md` §1's whole finding was that extraction cost had been
written as a criterion-3 failure. The manager wrote `TASK_PHP_011` expecting
that finding to be attacked as an OVER-reach — *"if the distinction does not
hold, ~17 reversals are wrong and the catalogue is inflated by a fifth."*
✅ The distinction holds. The error was the opposite one and it was in where the
lens was pointed.**

The adjudication produced a `§3b Kills UPHELD` list and **never re-opened it at
source**. Doing so reverses **five more**:

| row | the kill said | at source |
|---|---|---|
| **CRASH-097** | *"the quantity comes from a socket"* | ⚠⚠ **it comes from `zend_parse_parameters`.** The kill priced the **wrong operand** — F1 landing on the manager's own upheld list |
| **CRASH-098** | *"needs real file descriptors"* | measured: **`FD_SET` never touches the fd table** |
| **CRASH-135** | *"needs a calendar library"* | `SdnToJulian` is **46 self-contained lines** of a 250-line file |
| **CRASH-133** | *"needs bcmath"* | same shape |
| **CRASH-147** | *"irreducibly ~2 GiB"* | a **resource budget**, not a kernel shape — criterion 3 is about shape |

Plus **six killed on *"mechanism quality"***, which is **not in the bar at all**.
**The catalogue is 91 rows, not the ~80 predicted.**

⚠⚠ **The transferable rule: an audit that only re-examines the decisions it
already doubts measures its own priors.** The adjudication's §6 said *"the thing
to attack first is whether the criterion-3-vs-tier distinction is crisp"* — it
was, and asking that question is what stopped anyone asking the cheaper one:
*did I apply it everywhere, or only where I expected to find something?*

### F22 — ⭐ A KILL WRITTEN AS A SET HIDES ITS MEMBERS

**`CRASH-124`, `CRASH-127` and `CRASH-128` were killed by the SAME SENTENCE as
`CRASH-123`** — the row `ADJUDICATION_001.md` §1b made its **headline
reversal**, the five-line pointer-in-an-`int`. Nobody asked whether the other
three fell the same way. **They do.**

⚠ **This is unfindable by reading reject tables**, which is how both the
adjudication and every review before it worked. It was found by **diffing
catalogue coverage against `index.csv`** — a mechanical set difference.
⭐ **When a rejection covers N rows in one sentence, reversing it must
re-adjudicate all N, and the only reliable way to enumerate them is against the
corpus index, not against the prose.**

### F23 — the document that made the citation point had citation defects

⚠ **Three, in `ADJUDICATION_001.md` itself**: `CRASH-107` off by one on **all
three** lines, and `CRASH-123` off by one and by two — **inside §1b's five-line
headline exhibit**, the very passage arguing that a kill had priced the wrong
frame. ✅ **The CSV and the miners were right both times.**

That is `RECAP_PHP.md`'s own standing lesson — *the citation and the story about
it are two separate claims* — landing on the document that restated it. ⚠ **The
substance survived every time; only the line numbers moved.** ✅ And the
catalogue's own citations were then checked properly: **222/222 resolve against
the pinned tarball across 52 sha256-checked files, 51/53 miner quotes exact, two
correct-line paraphrases, ZERO wrong lines.**

✅ **`§7b`'s mechanism is also corrected**: the NULL test **is** present at
`zend_execute.c:141`; the bug is the `return` at `:147`. **That makes the
`CRASH-053`/`CRASH-056` pairing stronger, not weaker.** And `CRASH-096` gets a
**third** answer — `zend_memnstr`'s `end -= needle_len` underflow, blob-pure,
**not** the stream layer where the manager had left it conditional.

### F24 — ~12 rows need a shared header; none needs a shared directory

The question `TASK_PHP_011` was asked because **a catalogue can answer it and an
infrastructure task cannot**: would any real row want `patterns-php/shared/`?

✅ **Measured: ~12 type rows genuinely need a shared `zval.h` — and none needs a
shared DIRECTORY.** `common-php/x.h` symlinked as `<row>/c/x.h` lands in **both
digests**, which is the mechanism already sanctioned for the allocator.
→ **F20 stays latent and correctly so; what is owed is one clause in
`PROTOCOL_PHP.md` §B2, not an infrastructure task.**

### F25 — ⚠⚠ THE MANAGER'S FIRST-ROW PICK WAS REFUTED BY A MEASUREMENT, AND THE MEASUREMENT IS ITSELF A RESULT

The manager's prior was `ph11` — *"the smallest possible spatial defect, no
arithmetic, no cursor, no allocation"*. ✅ **Measured at `-O3`: safe Rust and
unsafe Rust emit BYTE-IDENTICAL kernel `Ir` (11 010 064), and BOTH BEAT C
(11 534 345).**

**Mechanism:** LLVM folds Rust's `0 ≤ o < len` into **one unsigned compare**,
which C's **one-sided signed** test cannot fold, and then unrolls 2×.

⚠ **So `ph11` would publish ONE number across four rungs** — which is a genuine
finding and a terrible row to prove the pipeline *measures* anything with.
**Keep it; do not build it first.** ⭐ And note what it says on its own: **the
safety check is not merely free, it is faster than the unchecked C**, because a
two-sided unsigned bound is more optimisable than a one-sided signed one.

### F26 — the real upstream fix is a 1.4 KB fetch, not a 1 GB clone

`TASK_PHP_012` M7: **no `php-src` clone exists on this box**, so
`PROTOCOL_PHP.md` §F5's *"sha-pinned `fix_commit`"* was unmeetable and **R1h had
never been built php-side at all** — which would have failed `PLAN_PHP.md` §3
criterion 4 on the first row.

✅ **Manager-resolved, and verified before being written down:**
`https://github.com/php/php-src/commit/<sha>.patch` returns the real commit.
For `ph03`'s `f95c1df58349` that is **Ilia Alshanetsky, 2004-08-24, bug
#29821**, `ext/standard/uuencode.c`, +17 lines — adding exactly:

```c
if (len > src_len) { goto err; }          /* before total_len += len */
ee = s + (len == 45 ? 60 : (int) floor(len * 1.33));
if (ee > e) { goto err; }                 /* <-- the bound the mining report predicted */
```

⚠ Fetching a bare sha by `git fetch` does **not** work (the server refuses
arbitrary-SHA wants); the `.patch` URL does. **R1h is buildable verbatim, for
real, on every row whose `fix_commit` the corpus records.**

### F27 — *"a kill written as a set hides its members"* has now fired THREE times

F22 found it once (`CRASH-124/127/128` behind `CRASH-123`'s sentence).
`TASK_PHP_012` found it **twice more**:

- **M1** — the catalogue's claim that every §3.1 kill *"survives inside another
  row's `corpus rows`"* is **false for 6 of 12**. ⚠⚠ **And the tool built to
  check coverage could not see it, because `coverage.py` counts a mention in the
  KILL TABLE as coverage** — a checker that accepts the artefact it is checking.
- **M2** — the four-`LOGIC` set kill into `ph47` is the same shape re-committed,
  and **3 of 4 are refuted by the catalogue's own discriminator**.

⭐ **Three instances make it a rule, not an anecdote: a rejection covering N rows
must enumerate the N against `index.csv`, and any coverage checker must count
ADMISSIONS ONLY.** → the correction task must fix `coverage.py` first, because
every later count depends on it.

### F28 — demoting the overlap floor cost more than the manager priced

`TASK_PHP_012` M4: **12 of 41 `verbatim` tiers are mis-declared**, measured
mechanically. ⚠⚠ **And the manager's own decision is why that matters now**:
`TASK_PHP_008` demoted `provenance.py`'s overlap check from **enforcing** to
**reporting**, so the **hand-declared tier is the only surviving fidelity
signal** — and it is wrong on 29 % of the rows that claim the strictest tier.

⚠ The demotion itself still looks right (its input space was unbounded). **What
was wrong was pricing it as free.** → the correction task must decide whether
the reported overlap is printed *beside the declared tier* so a mismatch is
visible, which is the cheap half of what the floor used to do.

### F29 — ⭐⭐⭐ THE FIRST ROW'S RESULT: A STATED OBLIGATION CAUGHT IN 2026 WHAT A PATCH MISSED FOR TEN YEARS

**`ph03`'s `c/kernel_hardened.c` is the REAL upstream fix** —
`f95c1df58349`, Ilia Alshanetsky, 2004-08-24, bug #29821 — and **it is
incomplete.** ✅ **REVIEWED at `TASK_PHP_014`: the headline survives every
attack, and got STRONGER** — see the two amendments below the three limbs.

1. **Counted.** Over 12 600 documents the fix closes **every write**
   (3 352 → 0) and leaves **144 over-reads**. `ee` bounds where the loop
   *tests*; the body reads `*(s+3)`. Smallest surviving case: `src_len = 2`,
   `len = 1` → `ee == e`, so hunk 2 never fires.
2. **ASan**, on the *fixed* decoder, at `uuencode.c:144` — with a must-fire
   control proving the detector is live and a benign case staying silent.
3. ⭐ **Verus refuses it in one line.** Deleting **only** the four lines of
   PHP's *2014* check from `verus.rs` — leaving exactly the algorithm the 2004
   fix implements — fails `i < v@.len()` on `get_unchecked(buf, s + 1)`: **the
   same byte ASan reports.**

⚠ PHP did not complete this fix until **2014** (`1e2818b14376`, bug #67252),
and **that commit's own `.phpt` reproducer is the same `fl == 1, ee == e` shape
the count found independently.** Ten years.

⭐⭐ **AMENDMENT 1 — it is worse than incomplete: HALF THE 2004 FIX IS DEAD.**
`TASK_PHP_014` M5 proves hunk 1 (`if (len > src_len) goto err;`) **redundant**
three ways: deleting it from the Verus exec still gives **25/0**, neutralising
it in the spec still gives **25/0**, and **all 1 953 of its C firings would also
be refused by hunk 2.** So of a two-hunk fix, one hunk is dead and the other is
incomplete.

⚠ **AMENDMENT 2 — limb 2 is HARNESS-CONDITIONAL and *"measured twice, two ways"*
over-promised.** With the source allocated the way PHP's `emalloc` actually
allocates a zval string (`ALIGN8(len + 1)`), **ASan is silent** — the over-read
lands in the padding. ✅ **Limbs 1 (the count) and 3 (Verus) are
allocator-independent, so F29 stands** — but the ASan limb says *"a detector
fires under this allocator"*, not *"PHP faults"*.

⭐⭐ **This is the crash course's argument in one row, and it is not "the proof
is cheap": it is that the OBLIGATION IS STATED AT ALL.** A `requires` clause
caught in 2026 what a careful maintainer's patch missed for a decade.

⚠⚠ **And it reshapes the ladder: R2–R5 are NOT ports of R1h.** With only the
2004 pair a safe-Rust rung **panics** on those 144 documents — and *a rung that
panics is not a translation of the C*. So R2–R5 carry **both** fixes, R1h
carries 2004 only, and **only R1 diverges** on the shipped inputs. That is a
general rule for this corpus, not a quirk of `ph03`.

### F30 — the 2004 safety check has a NEGATIVE cost on gcc

✅ Measured on `ph03`: **−3.0 `Ir`/line on gcc**, +3.0 on clang. With the check
present, gcc's `setae` and two `cmove`s **disappear** (3 → 0, counted).
Rung deltas: **R2−R4 = +18.9 `Ir`/group** (one `cmp`/`jae` per checked access);
**R3−R4 = +6.1** (the reslice adds a wrap test R2 never had).

⚠ **Do not quote these against any `pNN` figure** (open item 9). And no ratio
here is *the* cost of safety — `controls/spellings.py` was not built.

### F31 — two frozen-harness limits only a real row could find, and both are DECIDED

**B1 — `harness/build.py` links no `-lm`.** ✅ Manager-verified independently:
`floor()` emits a real call at **-O0** and is inlined at **-O3**, and **libm was
never merged into libc** — so a `verbatim` libm kernel fails to link in the -O0
cells. **Decision: keep `ph03`'s macro substitution** (shipped with a
differential and a must-fire control, and in the deletion ledger), **and BATCH
the `-lm` edit** rather than pay a 33-row re-gate + re-measure now.
⭐ **Worth recording for whoever does it: `-lm` is a LINK-ONLY flag, so for
every pattern that calls no libm function the re-measured numbers must be
byte-identical — which makes that re-measure self-verifying rather than
risky.**

**B2 — `check_sanitizers_hardened` hard-fails on any R1h diagnostic.** That is
right for a hand-written PAT R1h and **wrong for a shipped upstream fix that is
incomplete** — i.e. it structurally forbids a row from carrying
`PROTOCOL_PHP.md` §C's strongest result as *gate* evidence. **Decision: no
harness edit.** The evidence lives in `controls/` and the report, and this is a
**standing limitation of the gate, recorded here**: ⚠ **a green php gate does
not mean the upstream fix is complete, and cannot.**

### F32 — ⚠⚠⚠ THE MANAGER ARBITRATED THE ONE NUMBER THIS FILE SAYS NOT TO ARBITRATE, AND WAS WRONG

**Retracted, and replaced by what actually happened.**

This entry said *"`PROTOCOL_PHP.md` §E says the named-spelling tail is 11 003
bytes; it is 11 004 — a fourth wrong value."* ✅ **Verified independently:
`harness/check.py:1910` is `NAMED_SPELLING_LEN = 11003`. §E was RIGHT. There is
no fourth value.** `TASK_PHP_005_REPORT.md:487-490` had already settled it —
*"both are correct about different cuts"* — and this file's own size box says so
at line 14.

⚠⚠ **So the manager took an engineer's claim on trust, wrote it into the state
layer as a finding, and thereby made this document contradict itself** — line 14
carrying the right number while this entry declared it wrong.

⭐ **The lesson is sharper than the error.** The size box's standing instruction
is *"DO NOT ARBITRATE THAT BYTE COUNT — IT HAS THREE ANSWERS AND THE DISAGREEMENT
IS A DEFINITION, NOT AN ERROR."* **The manager arbitrated it anyway, in the same
document, four sections below the warning.** ⚠ A rule written for other people is
not a rule you have read.

⚠ **And the mechanism is the one this programme already knows**: a claim arrived
in a report, was plausible, matched a pattern the manager was primed for (*"this
number keeps being wrong"*), and went into the authoritative layer **without the
one command that would have checked it** — `grep -n NAMED_SPELLING_LEN
harness/check.py`. That is `PROTOCOL.md` rule 14's shape with the roles
reversed: **an engineer premise the MANAGER had no reason to doubt, and did not
check.**

### F33 — the first PHP ladder, read off the gate's own table

`results-php/tables/ph03-uudecode-bound.md`, **`Ir(kernel)`, `small.bin`,
`O3 / isolated`** — the row's own rungs against each other. ⚠ **These are
within-row ratios only**; open item 9 forbids any comparison with a `pNN`
figure.

| rung | `Ir(kernel)` | vs `c-gcc` | `md5_fn` |
|---|---:|---:|---|
| `c-gcc` | 165 650 000 | — | `a970030d` |
| `c-clang` | 140 125 004 | −15.4 % | `1d3044b1` |
| **`safe_naive`** | 210 100 000 | **+26.8 %** | `59bd6d88` |
| **`safe_tuned`** | 171 700 000 | **+3.7 %** | `9a762cc4` |
| **`unsafe`** | 153 125 000 | **−7.6 %** | `33850579` |
| **`verus`** | 153 125 000 | **−7.6 %** | `33850579` |
| `c-gcc-h` (real 2004 fix) | 165 025 000 | **−0.4 %** | `4224991b` |

**What row 1 says, and it is the shape the crash course needs:**

1. **Naive safe Rust costs +26.8 %. Tuned safe Rust costs +3.7 %** — ✅ the
   tuning recovers **86.4 %** of the naive gap (measured, not estimated), so
   *"safe Rust is 27 % slower"* and *"safe Rust is ~free"* are **the same
   pattern written two ways.**
2. ⭐ **Unsafe Rust is 7.6 % FASTER than gcc C**, and **`verus` is byte-identical
   to `unsafe`** (`md5_fn 33850579` on both) — **the proof costs nothing at
   run time**, which is what R4≡R5 means concretely.
3. ⭐ **The hardened C — carrying the REAL 2004 safety check — is 0.4 % faster
   than the unchecked C.** The safety check is not merely free here; it is
   negative-cost, because it lets gcc drop a `setae` and two `cmove`s (F30).
4. ⚠ **`c-clang` beats `c-gcc` by 15.4 %, which is larger than every safety
   effect on this row.** **A compiler difference, not a safety difference** —
   quote a rung against a rung, never against "C".
5. ⚠ The `vec` column: **both C compilers vectorise (`xmm`); no Rust rung
   does.** That is likely most of the naive gap and is a property of *how the
   translation is written*, not of Rust.

⚠⚠ **CAVEAT, and it is the engineer's own**: `controls/spellings.py` was **not**
built, so **no ratio here is *the* cost of safety** — each is the cost of *these
spellings* of these rungs. A different safe-tuned spelling moves row 2's number
and would move this one.

⚠⚠⚠ **UPGRADED BY F39 — READ THAT BEFORE QUOTING ANY NUMBER ABOVE.** The caveat
is right and it is **weaker than the situation**. Three things it does not say:

1. **These are `fixed-R4 bound`s** — PAT's term (`.memory/02-bench-rules.md`),
   and the rule is that a bound ships **labelled, beside a cheapest-found
   counterpart**. **Above, seven numbers ship unlabelled with no counterpart.**
2. ⚠ **The obligation is inside `ph03`'s OWN hashed `why`**: *"Every pattern
   owes an in-contract spread beside its headline."* This is undischarged, not
   unforeseen.
3. ⚠⚠ **The missing number's direction is not a coin flip.** On the four PAT
   rows where anyone searched the R4 side, **three moved out of their buckets and
   every one moved against safe Rust** — `p22` by **510×** on the large band,
   `p12` and `p13` **sign-flipping**. **So point 1's *"tuning recovers 86.4 %"*
   is the single most likely claim on this row to move**, and it is the one the
   crash course would most want to quote.

### F34 — ⚠ `ph07` DOES have a fix, and the manager found it by disbelieving the engineer

`TASK_PHP_015` stopped before building `ph07` and reported that **no
`fix_commit` could be identified** — that 5.0.0's `for(;;)` survives byte-for-byte
to 5.3.0, that 5.4.0 rewrites it and *"still never consults `string->len`"*, and
that this might be **a stronger finding than `ph03`'s**. It disclosed that it had
**not bisected history**.

✅ **Manager-verified against three upstream tags. The first two claims hold; the
third is wrong, and a fix exists.**

```
php-5.0.0  mbfl_strcut body 4708 B   for(;;) present
php-5.3.0  mbfl_strcut body 4708 B   BYTE-FOR-BYTE IDENTICAL to 5.0.0
php-5.4.0  mbfl_strcut body 7065 B   rewritten
```

The 5.0.0 walk, quoted — **its only exit is `n > from`, and `p` is never compared
against `string->val + string->len`:**

```c
for (;;) { m = mbtab[*p]; n += m; p += m; if (n > from) break; start = n; }
```

⚠ `len = string->len` **is** read at the top, but only for the clamps *after* the
walk (`if (start > len) start = len;`) — **too late; the over-read has happened.**
⭐ And the same function's **second** walk *is* bounded (`if (k >= (int)string->len)`),
so `mbfl_strcut` bounds its end search and not its start search.

**But 5.4.0's prologue carries exactly the missing guard:**

```c
if (from < 0 || length < 0) { return NULL; }
if (from >= string->len)    { from = string->len; }   /* <-- the bound */
```

so `q = p + from` can no longer pass the buffer end. ⚠ **The engineer read the
5.4.0 *walk* (which is still expressed in terms of `from`) and missed the
*prologue* that makes `from` safe** — the guard moved, it did not vanish.

> ⚠⚠⚠ **SUPERSEDED IN PART BY F38 — READ THAT FIRST.** The facts above about
> the 5.0.0/5.3.0/5.4.0 *code* all hold. **The conclusion drawn from them does
> not: the real fix is `cb3cca21b345` (Ilia Alshanetsky, 2005-12-15, *"Fixed
> possible memory corruption inside mb_strcut()"*), and it is in
> `PHP_FUNCTION(mb_strcut)` in `ext/mbstring/mbstring.c` — THE CALLER, IN
> ANOTHER FILE:**
>
> ```c
> if (from > Z_STRLEN_PP(arg1)) { RETURN_FALSE; }
> if (((unsigned) from + (unsigned) len) > Z_STRLEN_PP(arg1)) { len = Z_STRLEN_PP(arg1) - from; }
> ret = mbfl_strcut(&string, &result, from, len);
> ```
>
> ⭐ **That is WHY `mbfl_strcut`'s body is byte-identical 5.0.0 → 5.3.0** — the
> bound was restored one function up and one file away, in 2005, under an
> explicit security subject line. The 5.4.0 prologue clamp is a **second, later**
> restoration of the same bound inside `mbfl_strcut` itself.
> ⚠ **So this finding's own lesson must be widened**: a missing bound is often
> restored in the prologue — **or in the CALLER, in a different file, under the
> caller's name.** A search keyed on the defect's function cannot find it, which
> is exactly what happened (F38).
> ⚠ **And the row must ask whether the caller-side guard is COMPLETE**: with
> `from == string->len` permitted, the start walk still advances `p` by `m` while
> `n <= from`, so `p` can pass the buffer end. **`ph03`'s shape — a real fix that
> is incomplete — is live here and is the row's job to settle by measurement.**

**Decisions:**
1. ⚠ **SUPERSEDED: `ph07`'s R1h is `cb3cca21b345`**, the real 2005 caller-side
   fix — not the 5.4.0 clamp, and not a hand-written control. The running build
   task was sent this correction mid-flight. `PROTOCOL_PHP.md` §F item 5's
   assumption that a `fix_commit` exists **survives, and F38 shows it holds for
   142 of the 145 ids the catalogue cites.**
2. ⚠ **The finding is NOT *"PHP never fixed this"*.** It is weaker and still
   worth having: **the fix arrived inside an unlabelled rewrite, and the
   vulnerable code shipped byte-identical from 5.0.0 through 5.3.x.**
3. ⭐ **The reusable lesson is about where a guard is looked for.** Both the
   engineer and the catalogue characterised this row by *the loop*, so both
   checked the loop in the fixed version. **A missing bound is often restored in
   the PROLOGUE, not at the site** — `F1`'s three-frames problem arriving in the
   *repair* rather than in the defect.

### F35 — ⚠⚠⚠ THIS BOX'S `grep` REPORTS **NOTHING** IN THE CORPUS'S MOST-CITED FILE

⚠ **The mechanism is NOT "the box has a weird grep" — that was the manager's
first framing and it was wrong.** `/usr/bin/grep` is **GNU grep 3.11 and handles
this file perfectly**. What an agent gets in a `Bash` call is a **shell function**
from the interactive profile that dispatches to **`ugrep 7.8.4`**, and *that*
exits **1** with **no stdout and no stderr** on a file holding one non-UTF-8
byte — **indistinguishable from a true absence.** Measured, same file, same
pattern:

```
$ grep       -n "PHP_FUNCTION(str_repeat)" .../ext/standard/string.c ; echo $?
1                                    <-- no output, no stderr, "not found"
$ grep      -an "PHP_FUNCTION(str_repeat)" ...                       ; echo $?
4115:PHP_FUNCTION(str_repeat)                                            0
$ /usr/bin/grep -n "PHP_FUNCTION(str_repeat)" ...                    ; echo $?
4115:PHP_FUNCTION(str_repeat)                                            0
$ rg         -n "PHP_FUNCTION\(str_repeat\)" ...                     ; echo $?
4115:PHP_FUNCTION(str_repeat)                                            0
```

✅ **Trigger isolated to ONE BYTE.** Copy `string.c`, replace `S\xe6ther` with
`Saether`, change nothing else → the wrapper `grep` finds line 4115 and exits 0.

⚠⚠ **Three consequences, and the third is the one that will waste a day:**

1. **The two search tools every agent has disagree**, and the one that fails,
   fails silently. The `Grep` tool is ripgrep-backed and sees the line; `grep`
   in a `Bash` call does not. **An engineer who greps the pinned tarball and
   finds nothing has learned nothing.**
2. **`grep -a` fixes it** through the wrapper, and so does `/usr/bin/grep`.
3. ⚠⚠ **THE SAME COMMAND BEHAVES DIFFERENTLY TYPED THAN IN A SCRIPT.** A shell
   function is not exported to `sh`, so `sh probe.sh` gets GNU grep and
   **succeeds** where the identical line pasted into a `Bash` call **fails**.
   The manager hit this while checking this very finding — `refetch.sh` printed
   a match for the file it had just been told was unsearchable. **A probe script
   is therefore NOT a faithful reproduction of what an agent sees**, which
   undercuts the usual "wrap it in a script and re-run it" repair.

**Priced against the corpus** — `iconv -f UTF-8 -t UTF-8` over all 1 170 `.c`/`.h`:

| | |
|---|---|
| non-UTF-8 files | **41 of 1 170** |
| of those, **cited by `CATALOGUE.md`** | **5**: `ext/standard/{string,html,reg,formatted_print}.c`, `ext/calendar/calendar.c` |
| catalogued rows citing one | **13 of 91** — `ph05 ph06 ph08 ph12 ph18 ph19 ph20 ph21 ph26 ph27 ph31 ph32 ph47` |
| **including, in the next batch** | ⚠ **`ph12` and `ph21`** (both `ext/standard/string.c`) |

✅ **No built row is affected**: `uuencode.c` (`ph03`) and `mbfilter.c` (`ph07`)
are both clean UTF-8, checked.

⭐ **Where the bad bytes are decides how bad this is, and it is two different
problems.** In four of the five files it is **one line of the licence header** —
an author's name in ISO-8859-1 (`Stig S\xe6ther Bakken`, `Jaakko Hyv\xe4tti`,
lines 15–17). **`ext/calendar/calendar.c:123` is the exception and it is live
code**: `static char alef_bet[25] = "0\xe0\xe1\xe2…"`. So:

1. **The search hazard is total** — the header byte poisons the *whole file* for
   `grep`, regardless of where you are looking. **Rule: always `grep -a` against
   the pinned corpus.** Landing in `PROTOCOL_PHP.md` (staged — `TASK_PHP_016`
   is reading that file; `PROTOCOL.md` rule 11).
2. **The decode hazard is narrow and latent** — `harness/check.py` reads row
   sources with **strict** UTF-8 (`open(path).read()`, e.g. `:824`, `:2416`), so
   a row whose extraction *region* contains such a byte raises
   `UnicodeDecodeError` **in the frozen PAT gate we may not edit**. Only
   `calendar.c` (**`ph31`**) has one in code. ⚠ `harness-php/provenance.py` is
   safe — `:478` and `:780` pass `errors="replace"` — **but that means the
   overlap score for an affected file is computed on mangled text on both
   sides**; equal-and-mangled still matches, so it is a hazard only if one side
   is re-typed rather than copied.

⚠ **This is the THIRD silent false negative of the same shape in this project** —
`copy_from_slice` (*"no spec exists"*, stood TASK_004→048), `index_mut`
(TASK_089), and F34's *"no fix exists"*. **The first two needed a human to
misread a tree. This one needs nobody to make a mistake at all.**

### F36 — the next batch's four upstream repairs, found BEFORE the tasks were written

F34 cost a task: `ph07` stalled at *"no `fix_commit` exists"* and the manager had
to overturn it. So the manager surveyed the **whole** next batch first. ✅ **All
four citations verified byte-exact against the pinned tarball, and all four
fixes exist**, each inside the 5.0 → 5.2 window:

| row | 5.0.0 defect (verified line) | fixed by | what upstream actually did |
|---|---|---|---|
| **ph16** | `FD_SET(this_fd, fds)` — `streamsfuncs.c:541` | **5.1.0** | `PHP_SAFE_FD_SET` + `&& this_fd >= 0` |
| **ph29** | `emalloc(to_read + 1)`, `to_read` a `long` — `streamsfuncs.c:321` | **5.1.0** | `if (to_read <= 0) RETURN_FALSE;` — **then 5.3.0 adds** `safe_emalloc(1, to_read, 1)` |
| **ph12** | `if (len && offset >= s1_len)` — `string.c:4786` | **5.2.0** | the `len &&` short-circuit **deleted** → `if ((offset + len) > s1_len)` |
| **ph21** | `int result_len` `:4120` · product `:4144` · dead disjunct `:4145` | **5.2.0** | `int`→`size_t`, **the guard DELETED**, `emalloc`→`safe_emalloc(len, mult, 1)` |

⭐⭐ **Two of the four repairs REMOVE the guard, and that is the finding.**
`ph21`'s `if (result_len < 1 || result_len > 2147483647)` and `ph12`'s
`if (len && …)` are not strengthened upstream — they are **thrown away** and the
obligation moved into a type (`size_t`) or an allocator wrapper
(`safe_emalloc`). **The catalogue called `ph21` *"a guard killed by the type of
the variable it tests"*; upstream's own fix was to change the type and delete the
guard, which is that reading confirmed by the maintainers.**

⭐ **`ph16`'s fix is not a check — it is a check on one platform.** `PHP_SAFE_FD_SET`
is `#ifdef PHP_WIN32` → bare `FD_SET`, `#else` →
`do { if (fd < FD_SETSIZE) FD_SET(fd, set); } while(0)`
(`main/php_network.h:194-204`, 5.1.0). ⚠ **The macro's name promises safety
unconditionally and its POSIX branch alone delivers it** — correctly, because
Win32's `fd_set` is a counted array rather than a bitmap, and the source says so
in a comment. **R1h must state which branch it compiles.**

⚠ **`ph29`'s repair is two-stage** (guard in 5.1, wrapper in 5.3), so *"the
fix"* is a choice the row has to make and justify — like `ph03`'s two hunks.

⚠ **What is NOT done: none of the four commits is pinned**, only the tag window.
That is the row engineer's job, and the window is the expensive half.

> ✅✅ **SETTLED AT `TASK_PHP_020` → F46, AND THE CATALOGUE WAS RIGHT WHILE I
> WAS WRONG. Read that, not this.** This entry said *"`ph29`'s catalogued
> mechanism is not yet verified — `to_read` is a `long` and 5.0.0's `emalloc`
> takes a `size_t`, which on this 64-bit box truncates nothing. **Either the
> mechanism is 32-bit-only, or it is elsewhere, or the row is
> mis-catalogued.**"* **The measurement matched none of the three.**
>
> A probe replicating `zend_alloc.c:129/132/135/182/201` verbatim: `to_read =
> LONG_MAX` → `size = 2^63` → **`real_size = 0`** → a header-sized `malloc`
> **succeeds**. ⚠ **The truncation is `REAL_SIZE` at `:129`** — F5's family,
> already in this file — **and never was at `emalloc`'s signature, which is
> where I looked.** ⚠⚠ **And the row is 64-bit-ONLY: the exact opposite of the
> "32-bit-only" limb I offered.** ⭐ Three strengthenings came with it — a
> **UB-free** trigger (`to_read = 4294967295`, avoiding a `LONG_MAX + 1` gcc
> may fold), it **zeroes `CHECK_MEMORY_LIMIT`'s accumulator**, and it **reaches
> the second truncation** (`zend_alloc.h:53`'s `size:31`).
>
> ⭐ **The transferable part is not the arithmetic.** I doubted a catalogue row
> because *a mechanism I could not see at the frame I was looking at* — and F1
> is this project's oldest finding: **the citation names one frame and the
> defect lives in another.** **I applied F1 to kills and to fixes and did not
> apply it to my own doubt.**

### F57 — ⭐⭐⭐ ROW 3, THE FIRST OUTSIDE `S1`: THE SANITIZER IS BLIND, MIRI IS NOT, AND THE ROW'S ORACLE WAS ALREADY IN UPSTREAM'S OWN FRAME

`TASK_PHP_025`. `ph16-fdset-index`, gate **PASS**, `provenance --all` 4 rows
0 FAILED, brackets **66/0** (PAT untouched) and **8/0**. **Six controls, each
with a must-fire AND a must-not-fire case** — §H, landed the same morning.

⭐⭐ **THE CANARY I DESIGNED WAS NEVER NEEDED, AND THE REASON IS BETTER THAN THE
CANARY.** I measured that a `volatile` canary catches what ASan misses and told
the task to build on it. **`stream_select`'s own `wfds` and `efds` ARE the
witnesses**: `PHP_FUNCTION(stream_select)` declares `fd_set rfds, wfds, efds;`
at `:658` and reads **all three** back at `:706`, so an over-index into `rfds`
lands in a live object *the function's own result depends on*. ⚠ **`spec.md`'s
`forbidden[2]` now BANS a canary**, and `controls/oracle.py` **predicts R1's
corrupted checksum bit-for-bit under both compilers** from the measured frame
layout. ⭐ **It never differences the rungs** — otherwise `max_fd` would be
mistaken for the memory error, which is F52's trap avoided by construction.
⚠⚠ **And the three `fd_set`s being SEPARATE LOCALS is now a pinned obligation**:
packing them into an array or shipping one instead of three **deletes the row.**

⭐⭐⭐ **THE HEADLINE ASYMMETRY, MEASURED: ASan is silent at index 2048 on R1;
MIRI FIRES on an R4 mutant at the same index.** The mechanism is read off Miri's
own diagnostic — `core::slice::get_unchecked`'s precondition — **not** from
provenance. **A real memory-safety defect that C's standard detector misses and
Rust's does not.** ⚠ The redzone geometry is exact: index **1024–1279** is
`REPORTED`, index **1280–3071** is **SILENT** because the write has landed in
`wfds`. `adversarial-redzone.bin` and `adversarial-silent.bin` **differ in that
one number and nothing else.**

**The ladder** (whole-program `Ir`, vs `c-gcc`): R2 **+28.4 %** · R3 **−3.5 %** ·
R4/R5 **−2.3 %** · R1h **+10.8 %**. ✅ **`unsafe` and `verus` are byte-identical**
(`md5_fn 659d7b4b`, `identity: exact`) — the first php row to achieve that on
the shipped cell. ⚠⚠ **Only the R1-vs-R1h figure is confound-free**: both gcc
cells vectorise nothing while every other rung uses `xmm`.

⭐ **`ph16`'s upstream fix is COMPLETE and MINIMAL — the counter-example
`.memory-php/02` needed.** That entry generalised from two rows that *"neither
was minimal nor sufficient"*. **n = 3, and the third breaks it.**

⚠ **`controls/spellings.py` was NOT built.** I asked to be told if carrying it
made this two tasks; **it did.** Debt declared in three places, and ⚠⚠ **no
figure in this row is a `fixed-R4 bound`** — `R3ship − R4ship` is *negative*.
**So all three built rows now owe an R4-side search** (item 26).

### F56 — ⚠⚠⚠ THE COMPILER WAS ALREADY ENFORCING THE BOUND THE ROW IS ABOUT, AND CHARGING 60 % FOR IT

`TASK_PHP_025`, and it is the finding that reaches past its own row.

**Ubuntu's gcc injects `-D_FORTIFY_SOURCE=3` whenever it optimises**, and glibc's
fortified `FD_SET` is **`__fdelt_chk`** — a bounds check on **exactly the
quantity this row's defect is about**. Measured: `c-gcc-O3` **aborted** on the
adversarial input with *"bit out of range 0 - FD_SETSIZE on fd_set"*, and on the
**benign** input charged **14.87 `Ir` per `FD_SET`** — 92 605 764 → 148 709 085
`Ir` over 3 773 157 calls, **+60.6 % whole-program, counted rather than
estimated.**

> ⚠⚠⚠ **WITHOUT THE `#undef` BOTH C KERNELS NOW CARRY, R1 WAS NOT R1 IN HALF THE
> GCC CELLS — AND THE TAX WOULD HAVE READ AS C-VERSUS-RUST.**

✅ **Verified independently by the manager, with both halves.** ⚠ **A constant
index elides the check and would have hidden it** — F52's trap — so the probe
uses an `atoi`'d index: `-O0` clean, **`-O2` and `-O3` emit `__fdelt_chk`**,
`-D_FORTIFY_SOURCE=0` clean. Then the must-fire control: **defeat `ph16`'s
`#undef` and `__fdelt_chk` returns.**

✅✅ **IT DOES NOT REACH `ph03` OR `ph07`.** Both call `memcpy` and `memset` and
**neither carries an `#undef`**, so I compiled both kernels at `-O3`: **no `_chk`
symbols in either.** ⚠ This was worth checking rather than assuming — level **3**
uses `__builtin_dynamic_object_size` and tracks allocation sizes that level 2
cannot. **Their published C numbers stand.**

⚠⚠ **AND R1h IS THREE GUARDS, NOT TWO — I had it wrong in the task file.**
`99e290f882c9` also adds **`PHP_SAFE_MAX_FD`, in the caller's frame**, and it is
**not about the write**: `*max_fd = this_fd` sits *inside* the arm
`PHP_SAFE_FD_SET` protects but **is not bounded by it**. ⚠ Guard (a),
`&& this_fd >= 0`, is **DEAD here** — `this_fd` is a 14-bit field — **and the row
says so and measures it rather than banking it.**

⚠⚠ **MY OWN ERROR, IN THREE FILES: the caller's `fd_set` is at `:658`.** I wrote
`:657` and called `TASK_PHP_020`'s `:658` *"off by one and harmless"*. **`_020`
was right; I mis-read my own `sed -n '655,660p'`, whose fourth line is 658.**
⭐ **An inverted correction is worse than the drift it claims to fix** — it
converts a correct citation into a wrong one *and* spends the reviewer's credit
doing it. **Corrected in `RECAP_PHP.md`, `TASK_PHP_025.md` and
`.temp/mgr166/NOTES.md`.**

⭐ **The tier is `narrowed`, decided from `PLAN_PHP.md` §4's DEFINITION.** The M4
enclosing-frame test says `verbatim`; **this row is the case that separates the
test from the definition**, exactly as I suspected when I withdrew my *"already
tier-checked"*. ✅ Corrected in both catalogue parts. ⚠ Overlap **20 %** against
`narrowed`'s 25 % is **accounted for line by line, not repaired by moving the
tier** — which is the honest direction.

### F55 (MANAGER, UNREVIEWED) — ⚠ THE PREFLIGHT RECORD IS KEYED BY THE NAME YOU TYPED, NOT THE ROW IT RESOLVED TO — AND ONE WRONGLY-KEYED DUPLICATE IS COMMITTED

Found verifying `TASK_PHP_024`, which left an untracked
`results-php/preflight/ph07.preflight.json` beside the real
`ph07-strcut-cursor.preflight.json` and correctly called it the manager's call.
**It is not a stray file; it is a defect with a committed instance.** Measured:

| file | `row` field | runs | tools |
|---|---|---:|---|
| `ph00.preflight.json` ⚠ **committed** | `ph00` | **12** | check, measure, report |
| `ph00-smoke.preflight.json` | `ph00-smoke` | **1** | check |
| `ph07.preflight.json` ⚠ untracked, stale | `ph07` | **4** | build, check, measure, report |
| `ph07-strcut-cursor.preflight.json` | `ph07-strcut-cursor` | **16** | build, check, measure, report |

⚠⚠ **`harness-php/` resolves an abbreviated row through `glob(<row>*)` for the
WORK and then keys the record on the STRING YOU TYPED**, so `provenance.py ph07`
operates on `ph07-strcut-cursor` and writes its history to a different file.
**The two then diverge**, and `ph00.preflight.json` — a wrongly-keyed record with
**twelve** runs against the real row's one — has been in the repository since
`TASK_PHP_010`.

✅ **Nothing published rests on it**: the gate reads `results-php/gate/`, and
`--check-stale` is 6/0 either way. ⚠ **What it costs is the audit trail** — a
row's preflight history is silently split by how someone typed its name.
⚠⚠ **I am NOT fixing it here.** `_024` §5.3's rule, which I asked for and am
landing, says a validator change lands **with its must-fire negatives or not at
all**; this needs a control that types both spellings and asserts one file.
**Queued as item 42.**

### F54 — ⭐⭐ A DECLARATION CAN BE WRONG IN EVERY NUMBER AND RIGHT IN EVERY VERDICT, AND THAT IS THE CONFIGURATION NO CHECK HERE CAN SEE

`TASK_PHP_024`. `TASK_PHP_022` M1 checked the hashed `why`'s **first sentence**
and found four stale figures (item 36). Re-deriving **every cell the entry
names** found **nine**, and ⚠⚠ **all eleven numerals reproduce exactly against
`git show 8214b5f:`** — **it is not typos, it is a whole pre-rebuild snapshot**
that was never re-read after the rebuild.

⚠⚠⚠ **WHY NOTHING CAUGHT IT, PRECISELY: every *qualitative* claim survived.** At
O3/isolated the two cells still have equal `n_fn` and equal `fn_bytes`,
`md5_fn_norel` is still identical and `md5_fn` still differs — **so `norel` was
the right level before and after, and no gate verdict ever moved.** The hash
still matched because the text was never edited. ⭐ **A row can publish six wrong
numbers and be right about everything they were cited to support.**

⭐ **AND THE WRONG-COMMIT DEFECT HAD A SECOND COPY THE REVIEW MISSED.**
`c/kernel.h` named `d9dda48f8a7e` as R1h while shipping `cb3cca21b345` hunk (a)
— and so did **`safe_naive.rs`**, ⚠ **also a `measurement_sources` file**, ⚠⚠
**contradicting the ladder table four lines below it.** `TASK_PHP_022` looked at
`c/` and **nobody grepped the rungs**; `_024` found it with a 3-line hash sweep
run *after* its first re-measure, which cost a second full pass.

⭐ **The `extra_spans` disclosure was worse than I reported.** I said *"adding a
span cannot make the number go up for free"* was false in one measured case.
Swept over all seven subsets: **5 of 9 single-span additions RAISE it.** The
union overlap is a **weighted mean and is non-monotone** — so the claim was not
imprecise, it was **false in the common case**.

⭐⭐ **THE PROCESS RULE, AND IT IS NARROWER AND BETTER THAN THE ONE I OFFERED.**
I asked whether I should have committed a `harness-php/` change before review.
The answer: *no, but that is not the mechanism.* **All four defects were in the
harness half; the row half survived intact.** The row shipped with `.temp/php18/`
full of controls; **the validator change shipped with none** — its only artefact
is a 16-line derivation log with no mutation, no expectation and no control in
it, and the eleven must-fire negatives were written **by the reviewer, after the
commit.** ⚠ **A gate run EXERCISES a validator on three rows; it does not ATTACK
it**, and I let the row's green gate stand as evidence about the validator.

> ⭐ **`PROTOCOL_PHP.md` §H, landed: A CHANGE TO A VALIDATOR LANDS WITH ITS
> MUST-FIRE NEGATIVES IN THE SAME CHANGE, OR IT DOES NOT LAND.** All four
> defects were minutes of probe work — ~250 lines caught every one.

⚠ **The `why`-staleness check is priced and deliberately NOT landed**: ~28 lines,
fires on exactly this defect with **zero false alarms across all three rows**,
goes silent after the repair. `_024` refused to land its own new gate stage in
the task that argues the manager should not have — *"landing mine in the same
task would refute the argument by example."* ✅ **Correct, and it is `PROTOCOL.md`
rule 3 applied to itself.** ⭐ **The tree then proved its own point**: the gate
caught two citations `_024` introduced, and then caught its *disclosure* of the
first — which is why the check must be **reported, never enforced**.

### F53 — ⚠⚠⚠ A SHARED UPSTREAM FIX IS NOT EVIDENCE OF A SHARED MECHANISM, AND THE RULE THAT SAID OTHERWISE HAD ALREADY PUT A FALSE SENTENCE IN THE CATALOGUE

`TASK_PHP_023` §2.6 and §4.3. **The landed `ph32` block said all three short
entity tables *"are repaired by ONE commit … which is why they are one row"*.**
✅ **Measured at each commit** (`entcount.py` run at nine PHP-5.0 commits
touching `html.c` between 5.0.3 and 5.0.4): at **`b9ff04703f16` (2005-01-11)**,
two months earlier, `ent_uni_spacing` and `ent_uni_8592_9002` are **already
`ok`** while `ent_uni_338_402` is still **63/65**. **`56adfe1f3cf1` repairs one
of the three.** ⚠ **So `ph32`'s stated R1h is wrong for two of the three tables
it claims** — and `_019` §10.3's quoted *"spacing"* diff is `b9ff04703f16`'s,
misattributed. ✅ **No `phNN` moves**; neither table is a corpus row, and `ph102`
is unaffected and now rests on stronger evidence.

⭐⭐ **THE RULE FIRED CORRECTLY FOR `ph102` AND INCORRECTLY FOR `ph32` IN THE
SAME PARAGRAPH.** The culprit is `TASK_PHP_019`'s second disjunct — *"different
upstream fixes, each leaving the other standing"* — and `_023`'s attack on it
holds:

> ✅ **A DISTINCT fix is evidence for DIFFERENT.**
> ⚠⚠⚠ **A SHARED fix is NOT evidence for SAME.** One commit routinely repairs
> unrelated errors in one file — `56adfe1f3cf1` fixes `ent_uni_338_402`'s
> **count** and, in the same patch, two pure **name** typos in a correctly-sized
> table. **Absence of a distinguishing fix is not presence of a shared
> mechanism.**

⚠ It is also **not a C-side test**, **contingent** on what a maintainer noticed,
**often counterfactual**, and **silent on a large part of the corpus** (`ph36`
has no sha, 17 rows are `fixed-by-rewrite`, 31 % of fixes are 2010+).
⚠⚠ **And `.memory-php/02-ladder.md` ALREADY WARNED** that the `fix_commit`
column *"names **a** fix … NOT necessarily the one that removes the 5.0.0
defect"* — **§2.6 is that warning firing on a hand-bisected chain.**

⭐ **Landed as `PROTOCOL_PHP.md` §G/§G1** — *one test, one burden: can I show
these are the SAME?* — ⚠⚠ **and the rule it replaces was never in a standing
document at all.** `_019` wrote it in a report, **I adopted it without review
and then used it myself to overturn a verdict**, and it has been operating as
folklore ever since. ⚠ **§G is marked UNREVIEWED and owes a second pair of
eyes.** ⚠⚠⚠ **It is a CHECKLIST, NOT A DECISION PROCEDURE**: (a)(b)(c) have no
stated level of abstraction, so **the verdict is a function of the description,
not of the C** — `_019` §7 concedes it returns *both* answers on `CRASH-090` and
breaks the tie from outside itself. ✅ **The half that was always right is the
BURDEN** — kill only on a proof of *same*, the correct inversion of the corpus's
own `merged_members` predicate.

⭐ **This lands on F50 immediately, and helpfully**: the census channel is **good
for FINDING sibling sites and useless for deciding whether they are
duplicates.** Finding is what it is for.

### F52 — ⚠⚠⚠ THE PROBE MADE THE STATE IT WAS MEASURING, AND SO DID MINE, TWICE, THE SAME WEEK

`TASK_PHP_023` §2.2, answering the starred question I put to it — *"`_021`
measured that gcc zeroes the padding `ph94` is about; is the row still
admissible?"* ⭐ **The answer is that the measurement was wrong.**

`TASK_PHP_021`'s probe opened each trial with

```c
zval arg;
memset(&arg, 0, sizeof arg);            /* labelled "zend_API.c:692" */
```

⚠⚠ **There is no such `memset` in PHP, and `zend_API.c:692` is the function's
signature line, not a statement.** The zval reaches `_object_and_properties_init`
from `zend_execute.c:3245 ALLOC_ZVAL` — `emalloc`, contents unspecified — and
`zend_API.c:708` writes only `arg->type`. **Nothing zeroes `value`. The probe
was reading its own zeroes**, and could not distinguish *"the store wrote a
zeroed high half"* from *"the store never touched the padding."*

✅ **Re-run with a `0xAA` poison and the zval from the allocator, nothing else
changed: WILD READ at `-O0`, `-O1`, `-O2` and `-O3`.** ⭐ **The `-O0`
disassembly is the mechanism and it is toolchain-independent**: the store at
`zend_API.c:710` is `mov %ecx,(%rbx)` (4-byte handle) + `mov %rax,0x8(%rbx)`
(handlers) — **bytes 4–7 are never written by anything.** `_021`'s
`mov %esi,%eax` is in the *callee's* return and is irrelevant, because the
caller never stores RAX's high half into the zval at all.

**So `ph94`'s ORIGINAL claim is restored** — *the index is uninitialised memory,
not a program value* — and the corpus's own valgrind *"Use of uninitialised
value of size 8"* at `:4033` is **corroborated, not contradicted.** ⭐ The blob
advice survives for a different reason: not *"a faithful producer gives zeros"*
(false) but *"a faithful producer gives whatever `emalloc` left, which is
neither reproducible nor measurable"* — **a `projection`, and it must be
declared in the divergence ledger with that `kind`.**

⚠⚠⚠ **THE PATTERN IS THE FINDING, AND IT IS MINE TOO.** Three probes, one week,
all of them **constructing the state they were measuring** and rendering it as a
confident result:

| probe | the construction | what it claimed |
|---|---|---|
| `_021`'s `ph94_probe2.c` | a `memset` PHP does not do | *"no OOB read at any `-O`"* — ⚠ **published as a ⭐ headline** |
| my `asan_reach.c` | `CANARY_BYTE 0xA5`, bit 0 already set, so `|= 1` was a **no-op** | *"canary INTACT — nothing saw it"* (F50) |
| my `V5C` check | `re.sub(r'\D','',…)`, turning `V5C-001` into `5001` | *"absent from `v5c_id`"* (F51) |

⚠⚠ **`count_ent.py` last session was the fourth.** ⭐ **The common shape is not
"a bug in a probe" — it is a probe whose SETUP encodes the answer, so both the
true and the false world render identically.** ⚠ **`.memory-php/00`'s rule
(*"a probe that cannot evaluate must say so"*) does not catch this class**: these
probes *could* evaluate, and did, on a world they built. **The check that works
is the one `_023` used — change the setup's arbitrary constant and see whether
the verdict moves.**

### F51 (MANAGER, UNREVIEWED) — ⚠⚠ THE COMMITTED CLAIM LAYER RESTS ON GITIGNORED SCRATCH IN TEN PLACES, AND **TWO ARE ALREADY GONE**

`CLAUDE.md` rule 1 makes everything under `.temp/` re-derivable and **mandates
deleting it once the gates are green.** So a committed document that cites
`.temp/` is a claim with a scheduled expiry, and `citecheck.py` could not see it
— the path *resolves today*, which is all `os.path.exists` asks.

⚠⚠ **The sharpest instance: `CATALOGUE.md` C.7's coverage claim** — *"Nothing is
NOT killed and NOT catalogued. ✅ Measured with `python3
.temp/php11/coverage.py`"* — **rested entirely on a script the repo does not
carry, which existed in four divergent scratch copies (85 / 75 / 39 / 19
lines), none authoritative.** ✅ **Promoted to `.tasks-php/coverage.py` and the
`166/166` re-derived and CONFIRMED**, so the claim is now reproducible.

⚠ **And the pasted output block is stale**: it says **91 rows / 161 ids**; the
file has **93 / 163**. A number pasted into a document does not track the
document — the same shape as F14 (`0 STALE` ≠ pinned) and the `why`-block hole
at item 36. **Queued as item 39; `CATALOGUE.md` belongs to `TASK_PHP_023` today.**

⭐ **Two repairs to `coverage.py` came with the promotion, both from F49:** the
row regexes were `ph\d\d` (blind to `ph100`+), and **`gaps:` was computed from
`range(1, len(rows)+1)` — its own hit count — so a row it could not see shrank
the expected set by exactly one and the gap list stayed empty. The check could
not report its own blindness.** ✅ **F49's claim that the `166/166` was
unaffected is CORRECT**, verified by keeping both computations side by side.

⭐ **A third defect the promotion found, and it was MINE.** The tool reported
*"3 ids the catalogue names that the corpus does not have"* — `V5C-015`,
`V5C-116`, `V5C-173` — and `CATALOGUE.md` had pasted that line in unexplained.
They are **legitimate**: the corpus's own `merged_members` column, ids merged
away into a surviving row (`V5C-116` → `CRASH-115`, cited by `ph03`). **The
corpus has a THIRD namespace and the checker knew two of them.** ⚠⚠ **My first
probe "confirmed" they were absent from `v5c_id` too — using
`re.sub(r'\D','',...)`, which turns `V5C-001` into `5001`.** A wrong comparison
rendered as a confident negative, **the exact failure `count_ent.py` produced
last session**, caught only because the *"numeric range 5001–5191"* it printed
beside the verdict was visibly absurd. **The verdict happened to be right; the
evidence for it was nonsense.**

⚠ **The general form: a checker that lives in scratch cannot outlive the claim
it certifies.** `boxcheck.py` and `citecheck.py` were in `.temp/mgr165/` too and
are now `.tasks-php/` alongside `quota.py`, `coverage.py`, `fixsurvey.py` and
the landing scripts.

### F50 (MANAGER, UNREVIEWED, n = 1) — ⭐⭐ A FIX COMMIT IS A **CENSUS** OF ITS DEFECT'S SIBLINGS, AND WE HAVE ONLY EVER READ IT AS A SOURCE OF R1h

Found while prepping `ph16`'s build task — evidence and a `REFETCH.sh` that
regenerates all of it in `.temp/mgr166/`. ⚠ **`PROTOCOL.md` rule 3: this is my
own observation and I have not cleared it. `TASK_PHP_026` is written to attack
it, and my prediction is written down there so it can be refuted.**

`ph16`'s `fix_commit` `99e290f882c9` was already on file, and
`FIXSURVEY_001.md:67-81` already recorded that it touches **10 files** — under a
heading that reads that number as a **cost**: *"⚠ 12 fixes touch ≥ 5 files
(F34's 'inside a rewrite' shape)"*, and `UPSTREAM_001.md:64`'s *"⚠ right fix,
big commit; cite the hunk, not the commit."*

⭐ **For `ph16` the extra files are not rewrite collateral. They are the same
defect at three other sites.** The commit adds one macro *pair* —
`PHP_SAFE_FD_SET` **and `PHP_SAFE_FD_ISSET`** — and applies it at four places:

| # | site in pristine 5.0.0 | primitive | catalogued? |
|---|---|---|---|
| 1 | `ext/standard/streamsfuncs.c:541` | OOB **write** | ✅ **`ph16`** |
| 2 | `ext/standard/streamsfuncs.c:577` | OOB **read** | ❌ |
| 3 | `ext/sockets/sockets.c:536` | OOB **write** | ❌ |
| 4 | `ext/sockets/sockets.c:563` | OOB **read** | ❌ |

⚠⚠ **`ext/sockets/sockets.c` has ZERO rows in the entire catalogue.**

> **The number we recorded as a liability is a lead.** Every one of the ~91
> resolved rows has a `fix_commit` on file, so the channel costs a patch fetch
> and a read — **and the discriminator is the commit MESSAGE**: `ph16`'s is a
> deliberate sweep (*"we avoid… by using poll(2)"*), `ph24`'s is *"Reimplemented
> date and gmdate with new timelib code"* and will yield nothing.

⚠⚠⚠ **n = 1, AND I EXPECT IT TO BE A MINORITY.** ✅ **"`ph16` is the only one
and the channel is dead" is a good result and `_026` is told to say it plainly**
— a one-instance channel dressed up as a programme is worse than a measured
negative (F7, F13), and this manager's projections have been wrong before (F32,
F36, and the `ph29` doubt that was wrong in all three limbs).

⚠ **This does NOT reopen the admission bar.** Every candidate it yields still
faces `PLAN_PHP.md` §3 on the C alone.

⭐⭐ **AND `TASK_PHP_023` HAS SINCE SETTLED HOW TO READ IT, IN THE DIRECTION THAT
MAKES THE CHANNEL MORE USEFUL.** I had flagged #1 vs #2 as a sharp test of
`_019`'s rule, because they **share one upstream fix** while differing in fault
primitive. `_023` measured that disjunct and it failed: **a *distinct* fix is
evidence for DIFFERENT; a *shared* fix is NOT evidence for SAME** — one commit
routinely repairs unrelated errors in one file, and that exact inference put a
false sentence into `ph32` (F53). **So the fix commit is good for FINDING
sibling sites and useless for deciding whether they are duplicates.** A clean
division of labour, and finding is what the channel is for. ⚠ **`_026` is told
not to report *"these four share a fix, therefore one mechanism"*** — the
refuted inference, in this task's own subject matter. **The finding is the
CHANNEL, not a row count.**

⭐ Also re-confirmed at source, and the catalogue is **exact**: `:541`, the
caller's `fd_set` at `:658` (⚠⚠ **this said `:657` and called `_020`'s `:658` an off-by-one; `_020` WAS RIGHT and the error was mine** — `TASK_PHP_025` caught it, F56),
`FD_SETSIZE 1024`, `sizeof(fd_set) 128`, index 4096 → **byte offset 512, past
the object**. ⚠ And `PHP_SAFE_FD_SET`'s safety is `#ifdef`-conditional — **Win32
gets the unguarded spelling and the comment saying so is CORRECT**, because
Win32's `fd_set` is a counted array of `SOCKET`s. **R1h must state which branch
it compiles.**

⭐⭐ **AND THE ROW'S ORACLE PROBLEM IS SOLVED, BY MEASUREMENT** (rule 14 —
`.temp/mgr166/asan_reach.c`, one write per process past a 128-byte on-stack
`fd_set`, **identical at `-O0`, `-O1`, `-O3`**):

| bytes past the object | ASan | canary |
|---|---|---|
| 8, 16 | ✅ **REPORTED** `stack-buffer-overflow` | — |
| **32 … 512** | ⚠ **SILENT** | ⭐ **CAUGHT IT** |
| 4096 | ⚠ SILENT | INTACT — past the canary's own 512 B |

✅ **The catalogue's premise holds. But the cliff is at 32 bytes, not near 384**
— the redzone is 32 B wide, and the block's two data points leave the boundary
unspecified across a 47× range. ⭐⭐ **The canary oracle works across the whole
range where ASan fails, and for exactly the reason ASan fails**: past the
redzone the write lands in a **live neighbouring object**, so the address is
legitimate and there is nothing for a sanitizer to report — but it is an object
we control. **`TASK_PHP_025` §3 now carries this as a measurement rather than a
recommendation**, with the two caveats it earns: reach is bounded by the canary
and not by the defect, and `volatile` is load-bearing.

⚠⚠ **MY FIRST VERSION OF THAT PROBE PRINTED A CONFIDENT WRONG NEGATIVE.**
`CANARY_BYTE` was `0xA5`, bit 0 already set, so the kernel's `|= 1` was a
**no-op** and every distance reported *"canary INTACT — nothing in this frame
saw it"*. It said the opposite of the truth and looked clean. **Same class as
`count_ent.py`, and as the `re.sub(r'\D','',…)` V5C check in F51 the same
afternoon — three in two sessions, every one a broken computation rendering as
a positive claim.** ⚠ **`.memory-php/00`'s rule already covers it and I keep
writing probes that violate it; the rule is not the gap, the habit is.**

### F49 — ⭐⭐⭐ THE STOP CONDITION FIRED, AND THE AUDIT'S OWN FINDING PREDICTED WHICH HALF WOULD FAIL

`TASK_PHP_021` was told to land `_019`+`_020` into `CATALOGUE.md` **and then
trigger-test the nine rows the same batch creates**, with the rule *"more than
two need a correction → STOP the landing."* ⚠⚠ **THREE OF NINE FAILED —
`ph94`, `ph98`, `ph101` — SO THE CATALOGUE IS BYTE-UNCHANGED AT 93 ROWS.**

⭐ **F46 predicted exactly this half.** It measured *"the defect site was wrong
in 0 of 19 rows; the `▸ trigger` line would have cost an engineer time in 3"* and
recommended auditing triggers only. **Applied to the very next batch, the
trigger test fails on a third of it** — while the tiers were re-derived and **all
nine confirmed**. The rate is not a property of an adjudicator; **it is a
property of which half of a row anybody checks.**

| row | what the trigger claimed | what the C does |
|---|---|---|
| **`ph94`** | a wild read | ⚠ **reaches the line and produces nothing.** gcc returns the 16-byte `zend_object_value` in `RAX:RDX` and narrows through **`mov %esi,%eax`**, *zeroing the very padding the row is about*, at **`-O0` through `-O3`** — so `lval == handle` and the read lands **inside** the string. ⭐ **The layout claim is exactly right** (4 bytes into an 8-byte slot, confirmed in the disassembly); **the wild read is a codegen accident.** The kernel must take the un-written half from the blob |
| **`ph98`** | *"a handler that cannot be called"* | ⚠ **`ph21`'s shape** — `set_exception_handler` validates at **registration** (`zend_is_callable`), so such a handler cannot be installed. It must be broken *after* registration, via `zval_copy_ctor` sharing element zvals by refcount |
| **`ph101`** | a PHP snippet | ⚠ **not runnable as written** — `A::$x` is `protected` (E_ERROR from global scope) and the second clause's `class C` is never declared |

⭐⭐ **AND THE ENGINEER DISCLOSED THAT ITS OWN VERDICT WAS DECISIVE**, which is
the thing I most want from a stop condition: *"`ph101` is the marginal one;
scoring it 'additive' would give 2/9 and let the landing proceed — the decision
turns on this row alone."* ✅ **Verdict UPHELD**: a trigger that raises `E_ERROR`
and names an undeclared class is a *failed* trigger, not an incomplete one.

**Delivered and ready**: `.tasks-php/land_019_020.py` — **45 anchors, each
resolving exactly once**, 93 → 102, refuses on re-application, verified against a
scratch copy, **with the three corrected triggers already in its text.** It is
one command *after* the nine rows get a review cycle.

⚠⚠ **A MANAGER DECISION THE ROW FORCED, AND IT REACHES MOST OF FAMILY `S3`.**
`ph95` **passes** — the `pack.c:214` guard is defeated identically at `-O0`,
`-O3` **and `-O3 -fwrapv`**, with `arg = INT_MAX-1` refused as the control —
⚠ **but there is no UB-free trigger, because the signed wrap IS the mechanism**,
and `harness/build.py` is frozen and passes no `-fwrapv`.

> ✅ **DECISION: do NOT add `-fwrapv`** (a `harness/` edit = a 33-pattern
> re-gate, the same call as F31's `-lm`). **A row whose mechanism is signed
> overflow measures what the compiler actually did, and must ship a
> flag-differential control saying so.** ⭐ **`ph95` already supplies the evidence
> that makes this safe**: the mechanism is *stable across `-fwrapv`*, so the
> measurement is not an artefact of the flag's absence. **A row where it is not
> stable is a different row and must say so.**

⚠⚠ **AND A FOURTH *"CHECKER THAT CANNOT SEE ITS OWN BLINDNESS"*.**
`coverage.py`'s row-count regex is **`ph\d\d`** — blind to `ph100`–`ph102` — and
its `gaps:` set is built **from its own hit count**, so on a 102-row file it
prints **`99 … gaps: none`** and *structurally cannot report the blindness*.
✅ Its `166/166` is unaffected. **That is `TASK_PHP_012` M1's shape
(*a checker that accepts the artefact it is checking*) and F17's
(*a reassurance that tells the reader not to look*), for the fourth time.**

✅ **Two small things settled.** Part A's headings summed to 91 because
**`ph92`/`ph93` are `spatial` rows sitting under the `Temporal` heading** — the
landing moves them so heading = section = axis. And the two blank `tier` cells
are **`ph15` and `ph91`, the two `unresolved` rows** — **deliberate, not a
defect**, and the landing leaves them alone.

### F48 — ⚠⚠⚠ I ACCEPTED A REFUSAL AND THEN LANDED THE SAME RULE WITH THE VERBS CHANGED

> ⚠⚠⚠ **AND I ACTED ON THIS REVIEW WHILE IT WAS STILL WRITING.** `TASK_PHP_022`
> notified at **1087** lines; the report finished at **1225**. I committed it
> inside `8e2d834` and then landed findings, acted on §5.1 and opened item 36
> from the partial text — **four commits against a file whose author had not
> finished.** ⚠ **That is `PROTOCOL.md` rule 11's own shape with the roles
> reversed**: the rule forbids editing a file a running agent *reads*, and the
> live hazard turned out to be *acting on* a file a running agent is *writing*.
> ✅ Nothing landed was unfaithful and nothing was lost — **but four findings
> arrived after my commit and are carried below rather than in anything I
> landed**, and the reviewer had to **withdraw its own `m5`** (*"the finding is
> committed and the row is not"*) because I fixed it out from under the review.
> ⭐ **A completion notice is not a completion**, and the cheap guard is the one
> I did not use: **re-read the file's line count before acting on it.**

`TASK_PHP_022`, the review of the rebuild. **It confirmed F47's headline by
construction, refuted the sentence I built on it, and answered the question I
was least sure of with *"you were half right, and the half you got wrong is the
one you asked about."***

⚠⚠⚠ **§5.1 — THE DEFERRAL.** `TASK_PHP_018` refused my protocol extension
(4.1-B) and proposed landing 4.1-A as *"an observation, not a general
permission"*. **I accepted within minutes and said so.** ✅ **Holding 4.1-B was
right. Landing 4.1-A is not, because 4.1-A IS A NORM:**

1. **Its head clause is a deontic permission, in capitals, first** — *"**AND A
   ROW MAY SHIP A SUBSET OF ITS `fix_commit`, IF IT SAYS SO AND SAYS WHY.**"*
   Everything after it *qualifies a permission the preceding sentence has
   already granted.*
2. **It carries a requirement schedule for future rows** — *"a row that wants to
   do the same **owes** … all four of (i)–(iv)"*. **An observation does not tell
   future rows what they owe. That sentence is the definition of a norm.**
3. **It goes into `PROTOCOL_PHP.md` §C**, immediately under the sentence that
   *defines* R1h, in a document every later builder reads as rules.
4. ⚠ **The difference between 4.1-A and 4.1-B is PLACEMENT, NOT SUBSTANCE.**
   Both grant it, both attach the same four disclosures, both make (iii)
   mandatory.

⚠⚠ **And the engineer's own argument for holding refutes landing**: *"holding
costs `ph07` nothing, because the row does not need the protocol to change in
order to ship."* **By exactly that argument, landing 4.1-A buys nothing** — the
only thing it does is tell *future* rows what they may do, which is the thing
the programme had just decided it lacked the evidence for. ⚠ **And (iii) does
not close (a)'s objection**: *any* later upstream change to the function
satisfies it, and `UPSTREAM_002` §1 is itself a demonstration that this
function's guard set moves across many tags.

> ✅ **ACCEPTED. The reviewer's replacement lands instead: the same facts, past
> tense, descriptive, no deontic verbs, no owed-list — plus one sentence saying
> the generalisation is OPEN at n = 1 and that a second row brings it to the
> manager as a proposal.** ⚠ **The asymmetry is the argument**: an under-stated
> observation costs one task when a second row needs it; **an over-stated norm
> is, on this project's own record, what has to be un-landed.**

⭐⭐ **THE PATTERN IS THE FINDING, AND IT IS ABOUT ME.** `TASK_PHP_017` refused
a rule invented to make one row gateable. `TASK_PHP_018` refused mine. **I agreed
with both — and then re-published the second one with softer wording.**
**Agreeing with a refusal and re-wording the refused thing is not accepting it**,
and I could not see it from where I was standing, which is exactly why §5.1 was
in the task file.

**✅ WHAT SURVIVED A HARD ATTACK** — the review re-derived rather than re-read:

- **§2 — the R1h decision holds, on an independent transcription.** Hunk (b)
  **alone removes 0 of 396** over-reads; hunk (a) **alone removes 396 of 396**,
  and it is *structural* — the start walk never reads `length`. The corpus is
  genuinely unrestricted (**read from the `.bin` files**, not from `gen.py`).
  ⭐ **`bug49354.py` is a faithful replay, authenticated against the patch's own
  git blob sha1** and checked against the real C on 18/18 cells.
- **§3 — every published ladder figure reproduces exactly**, and ⭐⭐ **the
  DEGENERATE R4 claim survived a real attack**: three further spellings
  (`copy_from_slice`, fold-from-source, raw-pointer walk) at **+0.001 %,
  −0.003 %, +1.965 %** — none cheaper — **and the metric objection was tested
  too** (whole-program `Ir` beside kernel-exclusive) **and failed.** It now
  stands on **seven spellings from two agents.** `r4_index0`'s byte-identical
  claim checked independently and **true**.
- **§4 — `extra_spans` validates an extra span as strictly as the primary**
  (negatives built), and `ph03`/`ph00` really are byte-identical.

⚠⚠ **MY OWN PREMISE ABOUT THE BOUNDARY IS WRONG, and it is one I put in a task
file.** I wrote that `from == string->len` is safe *"because
`mblen_table_utf8[0] == 1` at the terminator"*. **It is not.** ⭐ **Any step ≥ 1
is in bounds; a step of 0 gives NON-TERMINATION, not an over-read.** The
operative premise is **`mbtab[b] >= 1`** — which is what the proof actually uses.
✅ All **11** `mblen_table`s in 5.0.0 are 256 entries with minimum 1.

⚠⚠ **TWO MAJORS NOBODY ASKED FOR, both on the row as committed:**

1. **`spec.md`'s HASHED `identity[0].why` cites FOUR figures the rebuild
   refuted** — 255 instructions and three hashes, all pre-rebuild. **The hash
   still matches**, so no gate can see it, ⚠ **and `NOTES.md` claims the
   addendum pass covered it, which is a false disclosure.** `PROTOCOL.md` rule
   6's documented hole, reproduced live.
2. **`c/kernel.h:20-25` names `d9dda48f8a7e` as R1h** while the file ships
   `cb3cca21b345` hunk (a) — ⚠ **and `spec.md`'s own `forbidden[2]` calls
   `d9dda48f8a7e` a *different function*.** It is inside `source_sha256` and
   predates the rebuild.

⚠ **Minors worth carrying**: `bug49354.py`'s docstring says it *"shares no code
with `fix_scope.py`"* and **the table and clamps are byte-identical copies** — a
**false disclosure**, though the conclusion is safe because three independent
checks agree; `spellings.py` **re-implements** `measure.py`'s statistic rather
than importing it; and ⚠ **the gate hashes `controls/*.py` and never runs them.**

### F47 — ⭐⭐⭐ ROW 2 REBUILT: THE ROW WAS SHIPPING A RUNG PHP ITSELF CALLS A BUG, AND **NO STRENGTH OF MEMORY-SAFETY-ONLY PROOF WOULD HAVE MOVED**

> ⚠⚠⚠ **THIS HEADING SAID *"AND ONLY A VALUE POSTCONDITION COULD HAVE NOTICED"*.
> THAT IS FALSE AND IT WAS MY AMPLIFICATION** (`TASK_PHP_022` §1). **The gate's
> own stage 2 separates the two configurations** on the rebuilt corpus — **4/32
> windows move on `small.bin`, 297/2050 on `large.bin`**, and the final `u64`
> differs on both. ⚠ **`NOTES.md:70` said only the true half — that the *proof*
> does not move — and I turned it into a claim about every observer.**
> ✅ The corrected claim is narrower, was **confirmed by construction**, and is
> quantified below.

`TASK_PHP_018`. Gate **PASS**, contract `be5f5818ffa6…` → **`1f1508531bd4…`**,
both brackets **66/0** and **6/0** first and last. ⚠ **UNREVIEWED** — nothing
here is in `.memory-php/` (rule 9), and the review is the next task.

**§1a — the question that could have killed the plan: YES, ALL OF THEM DID.**
All four Rust rungs carried hunk (b)'s clamp, **and so did `verus.rs`'s spec
function `strcut_fold`** and all three `model.py` implementations. Removing it
did **not** break the proof — **it made it cheaper**: the `rlimit` requirement
went from ~10–12 plain / **15** twin to **9 on both**.

> ⭐⭐⭐ **AND THAT IS THE ROW'S STRONGEST RESULT, ARRIVING FROM A DIRECTION
> NOBODY DESIGNED: a memory-safety-only `ensures` WOULD HAVE STAYED GREEN
> THROUGH THE ENTIRE REBUILD.** The clamp was never a memory-safety bug — it is
> a *wrong answer*. **That is the concrete case for proving what a function
> computes rather than merely that it does not fault**, and it was produced by
> an accident of the rebuild rather than by an argument.

✅✅ **CONFIRMED BY CONSTRUCTION AT `TASK_PHP_022` §1 — the proof nobody had
written was written, and the result is STRONGER than the assertion.** A
mechanical weakening of the row's own `verus.rs`, audited for value tokens:
**`ms_hunkab` (the pre-rebuild exec, both hunks) and `ms_hunka` (hunk (a) alone)
BOTH verify 17/0 plain and 20/0 twin**, and the `diff` between them is *comments
plus hunk (b)'s six exec lines* — **not one invariant, assert, ghost binding or
`decreases` differs.** Must-fire control holds: delete hunk (a) and both regimes
fail at `frm <= slen`.

⭐⭐ **AND THE ANSWER TO *"what did memory-safety-only cost to define?"* IS THE
BETTER HALF: NOTHING, BECAUSE THERE IS NOTHING TO DEFINE.** The kernel returns a
`u64` and writes no caller-visible memory, **so the honest memory-safety-only
spec is the EMPTY postcondition** — safety lives in the trusted items'
`requires`, the `decreases`, and Verus's built-in checks. ✅ **Vacuity measured
rather than argued: the same kernel with its body replaced by `0u64` verifies
13/0.** ⚠ The reviewer also built the *stronger* reading — an explicit ghost
*"no read past `slen`"* postcondition — **and it too verifies in both
configurations, and even with all four instrumentation points deleted.** *Even
that postcondition is bookkeeping nothing forces.*

> ⭐⭐⭐ **THE NUMBER THAT SAYS IT BEST: the memory-safety-only proof verifies at
> `rlimit` 1, against the row's 9. Essentially the ENTIRE proof budget is the
> value postcondition.**

⚠⚠ **What this does NOT license, and I claimed it did: *"only a value
postcondition could have noticed."*** **The GATE would have** — stage 2's
identity check moves on 4/32 and 297/2050 windows. **The correct statement is
about PROOFS, not about observers**: no strength of memory-safety-only
postcondition distinguishes the two rungs, and the row's `NOTES.md` said exactly
that and no more.

⭐⭐ **I OFFERED A STOPPING POINT AND IT WAS DECLINED ON EVIDENCE BETTER THAN MY
ARGUMENT.** `UPSTREAM_002` reasoned from archaeology. `controls/bug49354.py`
**replays upstream's own regression test** against all three configurations:

```
R1h_ab (the shipped two-hunk fix)   FAILS case 3   <- that IS bug #49354
R1     (5.0.0)                      FAILS case 6   <- that is CRASH-124
R1h    (hunk (a) alone)             agrees on all six
```

**The row was shipping, as "the real upstream fix", a rung PHP itself files as a
bug** — demonstrated behaviourally, not inferred from a tag sweep.

**THE NEW LADDER** (`Ir`/window byte vs R4; `-O3 isolated`; within-row only):
**R2 +59.77 %** (was +57.67) · **R3 +11.98 %** (was +13.50) · **R4 ≡ R5**
**byte-identical up to relocations**. F41's claims **(a)** and **(b)** survive
**unchanged**. ⚠ **This said *"byte-identical"* flat, and `TASK_PHP_022` is
right that the record does not support it: `md5_fn` DIFFERS between R4 and R5
and only `md5_fn_norel` matches, at `O3 / isolated` only.** `spec.md`'s
`identity` entry had it right and `.memory-php/` is clean — **the handoff was
the only place that overstated it.**

⚠⚠ **(c) SURVIVES, HALVED — AND GOT SMALLER WITHOUT GETTING CLEANER, WHICH IS
THE OPPOSITE OF WHAT MY TASK FILE PREDICTED.** One guard instead of two:
**+2.78 `Ir`/call gcc, +6.20 clang** (was +7.30 / +9.27). But the marginal
residual got **2.1× worse on gcc** and 1.5× better on clang.
⚠⚠⚠ **And the cross-check `TASK_PHP_017` §5c rested on has EVAPORATED**: the two
compilers' residuals were `−3.504e−05` and `−3.518e−05`, *identical to three
significant figures*, and §5c read that agreement as proof the residual is a
decomposition artefact. **They are now `+7.3e−05` and `−2.3e−05` — different
magnitudes, opposite signs. That agreement was a coincidence of one corpus.**
✅ The conclusion survives on a replacement argument that does not sit on a
rounding boundary (the marginal moves < 0.002 % on both compilers while the
delta holds across a **7.4×** range of window size); **the four-decimal-place
wording is retired.** ⭐ **A cross-check that only worked on one corpus is worth
more retired loudly than quietly.**

**§2 — `controls/spellings.py`, THE FIRST IN `patterns-php/`, and `ph07` is the
first php row to discharge F39's obligation.** ⚠ B1's `+2.62 %` is **not**
carried over — it was measured against the corpus §1c deleted.

```
fixed-R4 bound              R3ship - R4ship          +11.98 %
cheapest-found in-contract  inf(R3 found) - R4ship    +1.96 %   (r3_reslice)
```

⭐⭐ **AND THE R4 SIDE WAS SEARCHED AND IS DEGENERATE — a clean negative, which
is exactly the half F39's withdrawal said was missing.** Four R4 spellings, none
cheaper than a tie. **`ph07` makes it 12 of 20 rows where an R4-side search
found nothing**, which is `SYNTHESIS.md`'s *"degenerate more often than not"*
confirmed from inside this programme. ⭐ **So this `fixed-R4 bound` is a bound
over a SEARCHED endpoint** — materially stronger than the same number was a task
ago. ⚠ **Not exhausted**: four R4 and five R3 spellings over about one session.

⭐ **`r4_index0` is FREE and STRICTLY BETTER ON THE TRUSTED SIDE** — `s[0]`
instead of `*s.get_unchecked(0)` compiles to **the same bytes at the same
addresses**, verifies 21/0, and **removes one of `get_unchecked`'s four call
sites**. ⚠ Not shipped (the bench rule forbids re-shipping) — **and it is not
even cheaper; it is a smaller trusted surface at the same price**, which is a
different axis from the one the rule is about.

⚠ **A first draft measured the WRONG STATISTIC and said so** — `check.py`'s
100-vs-200 marginal, landing **1 %** off the shipped record. Not a discrepancy:
the driver picks its window from a checksum, so 200 iterations sample different
windows than 25 000. **A control quoted beside the row's headline must compute
the row's headline**; switched, and it now reproduces at **0.000 %** on all four
cells. ⭐ **Reported because it is exactly the size of error that gets absorbed
as noise.**

**§3 — `extra_spans` landed in `harness-php/provenance.py`** (additive, ~60
lines, **no PAT re-gate**, `ph03`/`ph00` byte-identical). ⚠⚠ **It exposed
something worse than it fixed.** The row's overlap headline falls **75 % → 61 %**
and the interesting number is `span2` at **15 %** — **the caller frame, which is
where R1h lives.** It is `modelled` text inside a row whose single `tier` word
says `narrowed`; the three lines that match are the two clamps and the call.
⭐ **The finding: a single `tier` word is the wrong shape for a multi-span row.**
`ph07` cites three spans at three fidelities — **100 % / 75 % / 15 %**. The
schema now lets a row say it lifts three; **it does not let it say at what
fidelity each.** ✅ Deliberately **not** extended — that is a second schema
change on n = 1.

⚠⚠ **§4.1 — I PROPOSED A PROTOCOL EXTENSION AND THE ENGINEER REFUSED IT, AND IT
IS RIGHT.** It ran `TASK_PHP_017`'s own three tests against `UPSTREAM_002` §4's
claim. **(b) and (c) pass** — and (b) is the strongest part of my case: *if
stage 7h learned tomorrow to express "this R1h legitimately differs on benign
inputs", `ph07`'s R1h would still be hunk (a) alone*, so unlike the §A2a clause
it does not retire with the gate check. ⚠⚠ **(a) FAILS.** A permission to cite
*"a tagged upstream configuration"* lets the next engineer **scan tags until one
is convenient** — *"instead of choosing the corpus to fit the fix, choose the fix
to fit the corpus."* **My distinction is true of this row and not true of the
rule unqualified.** ⭐ **And by the criterion `TASK_PHP_017` §3.2 landed — an
observation is settled by one command, a norm needs n ≥ 2 — a permission about
what a row MAY ship is a NORM, and it is on n = 1.**

> ✅ **ACCEPTED, as recommended: land 4.1-A (the worked example, with four
> MANDATORY disclosures) and HOLD the general permission until a second row
> needs it.** Disclosure **(iii) — *an upstream artefact decides it, not the
> row's convenience*** — is the load-bearing one. **Holding costs `ph07`
> nothing**: `spec.md` already discloses that R1h is a subset of `fix_commit`,
> why, and what it was chosen against. ⚠ **This is the second time in three
> tasks that a rule invented to make one row work has been refused, and this
> time the rule was mine.**

⚠ **F31 is PARTLY RETRACTED** (§4.3): stage 7h and `check_sanitizers_hardened`
are **not** the same defect on the same axis. One asks whether R1h changes
benign output — *a property of the fix*; the other whether it still faults — *a
property of the fix's completeness*. **Stage 7h was right; the analogy
`TASK_PHP_017` §4b drew was wrong**, and I had adopted it.

⚠ **THE WALL CLOCK NOW CONTRADICTS A FACT YOU CAN COUNT.** R4 and R5 are
byte-identical and their wall marginals differ by **2.73 %**; on this corpus the
wall clock says safe Rust is **5–6 % FASTER** than unsafe while the instruction
count says it executes **12 % more**. **A measurement that reverses a fact you
can count is measuring the box.**

⚠ **The gate cost 11 rounds, not the budgeted 6 — and every extra one caught a
real defect**, including `spellings.json` pinning **five sources that were
ABSENT** because it used row-relative keys where stage 9b wants repo-relative.
⭐ **That is open item 33's rebound-namespace hazard biting a second time, on a
new file, within a day of being written down.**

⚠ **`r202895` stays unresolved** — no `git-svn-id` trailers, `svn.php.net` dead —
**and it is not in the row.** ⭐ One thing did come out of the hunt: the removal
was committed **three times in the same second**, once per live branch.

### F46 — ⭐⭐ THE CATALOGUE'S MECHANISM SENTENCES HOLD. ITS `▸ trigger` LINES DO NOT, AND THAT IS THE HALF A BUILD TASK RUNS

`TASK_PHP_020`, on a seeded sample **drawn and printed before any C was
opened**. ⚠ **Two rates, never pooled** — the batch four are *chosen*, not drawn.

| stratum | needs correction | |
|---|---|---|
| **block 1**, n = 15, seed 20 | **1** (`ph93`) | 14 `SUPPORTED`, median **6 min/row** |
| **batch four** (`ph12 ph16 ph21 ph29`) | **1** (`ph21`) | the next rows to be built |

**No `NOT SUPPORTED`. No `UNDECIDABLE`.** ✅ **The catalogue's mechanism claims
are overwhelmingly right, and several are exact to a level a sampler does not
expect.** That is the answer I said would be the useful one, and it licenses
writing build tasks against a Part B block.

⭐⭐ **BUT THE RATE IS NOT THE FINDING. THE DEFECT SITE WAS WRONG IN 0 OF 19
ROWS; THE `▸ trigger` LINE WOULD HAVE COST AN ENGINEER TIME IN 3.**

> **The mechanism sentence is a POINTER — a build task re-reads the C anyway, so
> an error there is cheap. The `▸ trigger` line is LOAD-BEARING**: reachability
> is a build task's deliverable #1 (`PLAN_PHP.md` §4.2) and a row engineer
> starts by running the stated trigger. **`ph21`'s does not fire · `ph93`'s
> reaches the cited line and produces nothing · `ph29`'s fires only through UB.**

**→ Any follow-up audit should test `▸ trigger` lines ONLY** — 2–4 min/row once
the file is open, and it is where the entire yield was. ⚠ **This refutes half of
my own §6.3 hypothesis and confirms the other half**, which is the shape of a
question worth having asked.

⚠⚠ **AND THE RATE IS A LOWER BOUND, for two reasons the report states against
its own headline.** *"A cheaper audit than mine would have returned 15/15"* —
the one failure was the row it spent longest on (15 min), and three
`SUPPORTED` rows took 7–9. ⚠ **And the batch four are the rows with the most
eyes already on them** — an adjudication, `FIXSURVEY_001`, `UPSTREAM_001`, a
tier recheck — **and one still failed. Prior scrutiny is not protective.**

**`ph21` — the row that was going to be built FIRST — has a trigger that cannot
fire.** `str_repeat($s, 2^32/strlen($s))` makes `result_len` exactly 0, which
the guard's **surviving** first disjunct `result_len < 1` refuses. ⭐ **And the
block never says where the harm lands**: the general emit path bounds itself
with the *narrowed* `result_len` (`:4160`) and overflows nothing — **the
overflow is the `Z_STRLEN == 1` fast path at `:4153`, whose `memset` takes the
UN-NARROWED 64-bit `Z_LVAL_PP(mult)`.** Working trigger:
`str_repeat("A", 4294967297)`.

⭐ **`ph29` IS SETTLED, THE CATALOGUE WAS RIGHT, AND THE DOUBT WAS MINE.** F36
said *"`to_read` is a `long` and `emalloc` takes a `size_t`, which on this
64-bit box truncates nothing — either the mechanism is 32-bit-only, or it is
elsewhere, or the row is mis-catalogued."* ✅ **Measured on this box** with a
probe replicating `zend_alloc.c:129/132/135/182/201` verbatim: `to_read =
LONG_MAX` → `size = 2^63` → **`real_size = 0`** → a header-sized `malloc`
succeeds. ⚠⚠ **My doubt mis-located the truncation** — it was never at
`emalloc`'s signature; it is `REAL_SIZE` (F5's family). **And the row is
64-bit-ONLY, the exact opposite of the hypothesis I offered**, and satisfied in
our environment. Three strengthenings came with it: a **UB-free** trigger
(`to_read = 4294967295`, avoiding a `LONG_MAX + 1` gcc may fold), it **zeroes
`CHECK_MEMORY_LIMIT`'s accumulator**, and it **reaches the second truncation**
(`zend_alloc.h:53`'s `size:31`).

**→ BUILD ORDER CHANGED, on C-side grounds: `ph16 → ph29 → ph12 → ph21`.**
⚠ **`ph21` goes last precisely because its reachability claim is the one that
failed** — the standing order had it first.

⚠ **Two methodological corrections I am adopting.** (1) **`IMPRECISE` vs `NOT
SUPPORTED` did not separate** — the useful line is *does the error change what a
build task would do?* **Collapse to `SUPPORTED` / `NEEDS CORRECTION`, and count
*additive* corrections separately** (7 of 19 here). (2) ⚠ **Block 2 (n = 10,
seed 21) was NOT run as a mechanism audit** — per-row cost was not lower than
assumed, so it got the **weaker citation test only: 10/10 resolve**, plus two
cost nits. **It is a different test and must never be quoted as a mechanism
rate.** ✅ **The report labels it as such itself**, which is the discipline the
sampling design existed to protect.

### F44 — ⚠⚠⚠ THE MECHANISM TEST: 2 OF 13 KILLS ARE CORRECT AS WRITTEN, AND THE EVIDENCE THAT LOOKED STRONGEST WAS THE WEAKEST

`TASK_PHP_019` ran the test `ADJUDICATION_002` never ran — *does the C support
the mechanism claim?* — on all 13 `C.1` kills and `C.4`'s set, at the pinned
tarball. ⚠ **NOT LANDED**: `TASK_PHP_020` is drawing a sample from Part A and
eight new rows would corrupt its draw. Catalogue **93 → 101** when it does.

**Only 2 of 13 are correct as written** (`CRASH-090 → ph32`, `CRASH-037 →
ph39`). **Two more are right verdicts merged into the WRONG ROW** — `CRASH-101`
is `ph41`'s mechanism, *and `ph41`'s own block says "Do not fold into ph39"*;
`LOGIC-014` is `ph48`'s, *and `ph48` is the row `C.1`'s own sentence says was
**kept** for that reason.* **Nine fail**, eight becoming `ph94`–`ph101`.
⭐ The ninth, `V5C-116`, reverses and gets **no row**: `ph03` is built over both
defects and **has already measured them apart** — 144 of 12 600 documents still
read past the source with the other's complete fix applied.

⭐⭐ **THE ANSWER TO THE QUESTION I MOST WANTED: *"merged by the corpus itself"*
IS THE WEAKEST EVIDENCE IN `C.1`, NOT THE STRONGEST.** Three kills rested on it.

1. **The predicate is different.** The corpus merges on *root cause*
   (`validation/REPORT.md` §2a); `PLAN_PHP.md` §3.1 kills only on *exact C
   mechanism* and **explicitly admits a slight variation**. A corpus merge is
   evidence of relatedness, never of exactness.
2. ⚠⚠ **The burden is INVERTED.** *"Dedup burden of proof was set on 'distinct',
   not 'same'."* Ours splits unless *exact* is proven. **Citing the cell to
   support a kill cites a `not-proven-distinct` as a `proven-same`.**
3. ⚠⚠⚠ **And the corpus's own per-case validators flagged all three, in
   writing, in `verdicts.json`, BEFORE the merge** — *"distinct missing guards,
   verified by arithmetic … a dedup pass should keep them separate"* ·
   *"genuinely distinct (different fix commit) … keep `:212` as the
   distinguishing member"* · *"genuinely two distinct source-level mistakes on
   one line"*. **Three for three.**

⭐ **The three kills that looked strongest because they cited an external
authority were the three where that authority had written down the
counter-evidence.** ⚠ And the `index-other.csv` note that reads *"the SAME
defective construct as V5C-0NN"* is **boilerplate emitted by
`rebuild_corpus.py`**, identical on all three — a template, not a judgement.

**THE BASE RATE, AND ITS LESSON IS NOT THE NUMBER.** Of the **46** distinct ids
ever written down as killed in this programme, **6 survive** — **40 / 46 ≈ 87 %
reversed**, enumerated id-by-id so it can be checked. ⚠⚠ **But the informative
row is the outlier**: every deliberate pass reversed a majority *except*
`TASK_PHP_017`'s, which got **17 %** — and it was testing for a **cost word**.
The mechanism test on that same population returns **8**.

> ⚠⚠⚠ **THE RATE TRACKS THE TEST, NOT THE ROWS. It is not a property of the
> kill lists; it is a property of whether anyone opened the C.**

**And the test's own limit, found by running it.** `C.2` is **one** row and its
kill note already names the missing step — *"a 20-minute measurement, not an
adjudication"*, standing since `TASK_PHP_011`. `C.3` is one row and
`TASK_PHP_012` m3 already showed it does **not** fail criterion 3 — the honest
statement is **zero criterion-3 kills; one kill on a design decision**, owed a
landing, not a re-run. ⚠⚠ **What NOBODY has audited is the 93 catalogued rows'
`corpus rows` cells** — this task found **two** mis-merges there, **and
`coverage.py` cannot see them by construction**: it proves every id is
*somewhere*, never that it is in the *right* somewhere.

⭐ **`C.4`'s set: 6 members, and the enumeration finds no hidden seventh — a
clean negative.** But 3 were never individually adjudicated, because **`C.4`
reversed a set kill straight into another set kill.** → **F22 gains a rider:
*reversing a set into a set is not a reversal.*** ⚠ And `TASK_PHP_012` M2 was
**attacked rather than applied**: its count (3 of 4) is right and was reached
independently, but **two of its four cells are wrong.**

**⚠⚠ MY OWN TWO CORRECTIONS TO THE REPORT, both unreviewed and sent back to it:**

1. **§7 called `CRASH-090` undecidable and asked me to settle a bar question —
   *is a data object part of a C mechanism?* — but the report's OWN §1 rule
   decides it.** Its second disjunct is *"different upstream fixes each of which
   leaves the other standing"*, and ✅ I verified the disjointness at source:
   `46bc2c5ae2ae` (2004-07-19) touches **only** `ent_uni_punct`;
   `bd2e99ee50ed` (2005-05-11) **only** `ent_uni_338_402`. **10 of 13, and the
   bar question does not block the row.** ⚠ **The caution that cuts against my
   own argument**: `bd2e99ee50ed`'s pre-image does **not** match 5.0.0 — the
   comment bug it repairs is a **later** regression (*"merge error from 4.3"*) —
   so it is *a* fix, not demonstrably *the* fix. **F38 half 2 landing on the
   evidence I used to make the point.**
2. ⭐ **It is FOUR tables, not two.** `.temp/mgr165/count_ent.py`, comment-aware,
   at 5.0.0: `ent_uni_338_402` **63/65**, `ent_uni_spacing` **22/23**,
   `ent_uni_punct` **66/67**, `ent_uni_8592_9002` **410/411**; **the other
   thirteen are exact**, and all four are repaired by 5.0.5. ✅ **This
   reproduces the report's `nm -S` figures exactly by a different method**, and
   confirms `ph32`'s own `⚠ risk` line. **→ Settled at F45.**

> ⚠⚠⚠ **AND THE SENTENCE THAT USED TO END THAT PARAGRAPH — *"the other six
> mapped tables are exact; 7 more are not in entity_map at all"* — WAS FALSE,
> AND IT WAS MY SCRIPT SAYING IT.** `declared()` matched bounds with `(\d+)`, so
> it could not read the **15** `entity_map[]` rows whose bounds are hex
> (`0x80`, `0xff`, …), returned `None` for the **8** tables those rows name —
> **and then printed *"(not in entity_map — unused?)"*.** ✅ Measured after the
> fact: **all 17 tables are in `entity_map[]`; 24 rows, 0 unevaluated, 4 short.**
> ⚠ I pasted that output into `RECAP_PHP.md` **and** into a message to the agent.
>
> ⭐⭐ **The defect is not the arithmetic — it is that BOTH failure paths
> rendered as a POSITIVE CLAIM ABOUT THE C instead of *"I could not evaluate
> this"*** (the other one printed `ok`). **That is F17's shape — a reassurance
> that tells the reader not to look — produced by F10/F11's mechanism: I parsed
> C with a regex to decide a C fact.** `TASK_PHP_019` §10 caught it by
> **re-deriving every number with the compiler**, which is F11's rule verbatim:
> *ask the tool that actually decides.* ⚠ **The staircase now has a fourth
> step, and the fourth is the manager's own probe.** The script is fixed to
> print `CANNOT EVALUATE` and exit non-zero; ✅ **all four of my figures were
> right**, which is exactly why the false sentence beside them survived.

⚠ **The bar question still stands and is mine to settle**: `PLAN_PHP.md` §3.1
and `CLAUDE.md` rule 6 both say *"its C mechanism"* and **neither says whether a
data object is part of one.** The catalogue answers it one way everywhere
already (`ph60` is four sites in one row, `ph61` five, `ph43` two limbs), so the
cheap fix is to **write down the reading we already use** — but it multiplies
`ph32`, `ph39` and `ph41` if decided the other way, so it is not free either.

### F45 — ⭐⭐⭐ A DEFECT MADE INVISIBLE BY THE COMMIT THAT FIXED ITS WARNING

`TASK_PHP_019` §10, on the split F44 sent back. **The answer is TWO rows, not
one and not four** — and the archaeology on the way is worth more than the split.

| row | tables | the commit that removes the **5.0.0** shortfall |
|---|---|---|
| **`ph32`** (keeps `CRASH-089`) | `ent_uni_338_402` **+ `ent_uni_spacing` + `ent_uni_8592_9002`** | **one** commit — `56adfe1f3cf1`, 2005-03-09, bug #28067 |
| **`ph102`** (takes `CRASH-090`) | `ent_uni_punct` | `46bc2c5ae2ae`, 2004-07-19, bug #29199 |

**Both disjuncts of the rule fire, in opposite directions**: the three share a
fix, so they **merge** on the first; `punct`'s fix touches none of them and
theirs touches not `punct`, so it **splits** on the second. ⭐ **So `CRASH-090`
reverses after all** — and *not* on the bar question `TASK_PHP_019` §7 raised,
which now scopes only to three tables that are in **no corpus row** and blocks
nothing.

⚠⚠⚠ **THE FINDING, AND IT IS A THIRD INSTANCE OF THIS PROGRAMME'S SHARPEST
SHAPE.** The repair is a **four-commit chain**, and step 3 is
`bd07142b9128`, 2005-03-10 — *"fix `/*`-within-comment warning"*. It closes the
comment **after** the swallowed block. **The compiler goes quiet; the 24
initialisers stay inside the comment; and php-5.0.4 ships `ent_uni_338_402` at
41 for a declared 65** — ⚠ **twelve times worse than 5.0.0's 63** — **with
`gcc -Wall` silent** (measured by the agent; ✅ **the 41/65 independently
reproduced here by the fixed counter**, 5.0.0 **63** → 5.0.4 **41** → 5.0.5
**65**).

> **A warning was the only thing pointing at the defect, and the fix for the
> warning is what hid it.**

⭐ **So `ph32`'s R1h is TWO commits, and stopping at the first passes every
syntactic check and is still wrong** — `ph03`'s two-hunk finding arriving at an
unrelated site, by an unrelated mechanism. **Three rows now say the same thing
from three directions**: `ph03` (a fix half dead, half incomplete), `ph07`
(a fix half *wrong*, deleted by upstream — F43), `ph32` (a fix whose second half
is invisible because the first half silenced the diagnostic).
⚠ **And it is the same family as `ph07`'s own headline** — *the clamp that
arrives too late to prevent the over-read is exactly the clamp that hides it*
(F41). **The mechanism that suppresses the symptom keeps turning up adjacent to
the defect**, and that is now a claim with four instances rather than a
flourish.

⭐ **Three kinds of shortfall, not one, and the kind explains the history.**
`338_402` and `spacing` are **miscounted NULL runs under explicit range
comments**; `punct` is the only `cs_utf_8` table with **no run markers at all**,
missing one placeholder; `8592_9002` is **compensating errors netting to −1**.
**The 2005 audit commit catches the three *labelled* tables in one pass, while
the unlabelled one had to be found by a user bug report nine months earlier —
and its fix adds the missing run markers.** ⚠ **My guess that the kinds differ
was a guess; it is now measured, and it was the right thing to send back.**

✅ **Three independent methods agree on every localisation** — the corpus's
`nm -S` control binaries, the agent's compiler-evaluated
`sizeof/sizeof[0]` walk, and my regex counter — **and each localisation was
predicted before the patch was read** (*"the omission is immediately before
`dagger`"* → `46bc2c5ae2ae` inserts a `NULL` there; *"`crarr` is one early"* →
`56adfe1f3cf1` moves it).

**Restated: 10 of 13 fail, and only `CRASH-037 → ph39` is correct exactly as
written. Nine new rows `ph94`–`ph102`. Catalogue 93 → 102. 41 of 46 ≈ 89 % of
everything ever killed in this programme is reversed.**

### F43 — ⭐⭐⭐ PHP DELETED HALF ITS OWN SECURITY FIX, AND OUR GATE HAD ALREADY SAID WHY

**Manager work, `.tasks-php/UPSTREAM_002.md`. ⚠ UNREVIEWED — `TASK_PHP_018`
builds on it and the review after it must attack it (rule 3).**

`TASK_PHP_017` §4 refused to land `ph07`'s proposed §A2a clause, noting that
hunk (b) of `cb3cca21b345` is **absent from php-5.2.17 and every later tag it
checked**. It verified the fact and stopped. **I went looking for the commit
that removed it.**

`PHP_FUNCTION(mb_strcut)`, brace-matched and hashed at **nineteen tags** (⚠ **not
grepped** — a grep for the hunk's own source line reports it **absent from
php-5.3.0**, where it is present and respelled `(unsigned int)from`; F35's trap
fired on me *inside* the document that restates it):

| tag | body sha256/16 | hunk (a) | hunk (b) |
|---|---|:---:|:---:|
| `php-5.1.2` … `php-5.2.11` | `a971fe…` / `ec8b60…` | ✅ | ✅ |
| **`php-5.2.12`** … `php-5.2.17` | **`26e2099e33433c74`** | ✅ | ❌ |
| `php-5.3.0`, `php-5.3.1` | `08719ef4…` | ✅ | ✅ *(respelled)* |
| **`php-5.3.2`** … `php-5.3.29` | **`49ad3ab2…`** | ✅ | ❌ |

**The removal is `c2471b495009`** — Moriyoshi Koizumi, 2009-09-23, the only
non-cosmetic commit on that file in the window. Its `mbstring.c` diff is
**exactly hunk (b) and nothing else**, its subject is *"Fixed bug #49354
(`mb_strcut()` cuts wrong length when offset is within a multibyte character)"*,
and it adds **a regression test** pinning six answers hunk (b) got wrong.

⚠⚠⚠ **SO `check.py` STAGE 7h WAS NOT A HARNESS LIMITATION. It detected the same
defect PHP's own maintainers detected — four years later, from a bug report —
and it detected it in the first hour row 2 existed.** The row read a true
refusal as an obstacle and proposed protocol to route around it (open item 24);
`TASK_PHP_017` declined the protocol on other grounds and was **right for a
stronger reason than it gave**. ⭐ **Open item 24 now closes by DELETION rather
than by a rule** — the best available outcome for a rule invented on n = 1.

⭐⭐ **And it is `ph03`'s finding from the opposite direction.** There a stated
obligation caught in 2026 what a patch missed for ten years: the fix was
**incomplete**. Here the fix was **too big**, and the excess was not merely dead
— it was **wrong**, and upstream removed it. Set beside `ph03`'s dead hunk:
**two rows, two shipped security fixes, NEITHER minimal NOR sufficient as
shipped.** That is a result about security patches rather than about PHP, and it
is now n = 2.

⚠ **The blame id is UNRESOLVABLE, and the finding does not need it.** The
removal commit says *"(This bug was introduced by the commit by r202895. Please
double-check the specification of the function you are going to \*fix\*.)"*.
✅ Measured: **php-src's git mirror carries no `git-svn-id` in any commit
message** (sampled across the SVN era), so `r202895` cannot be resolved from the
mirror at all, and I am **not** asserting it is `cb3cca21b345`. ⭐ **What
replaces it is stronger than the blame line, and is measured**: on `PHP-5.2` —
**the branch the removal is on** — `PHP_FUNCTION(mb_strcut)`'s body is
**byte-identical from php-5.1.2 to php-5.2.6** and changes by one unrelated
token to php-5.2.11, so **the three lines deleted in 2009 were added by
`cb3cca21b345` and by no other commit.** The *identity* of the removed code is
established; only the maintainer's *reference* to it is not. ⚠ **The same commit
message appears verbatim on the 5.3 branch as `0c974164e248`**, and 5.3's clamp
is respelled, so the two branches acquired it separately — one more reason the
single revision id cannot carry the claim. ⚠ **And the decision this licenses is a rebuild of row 2**, with its
own risk stated at `UPSTREAM_002.md` §4 — a subset of a commit is not a commit,
and calling a tagged upstream *configuration* an R1h is a protocol extension
invented to make one row work, **which is the exact shape `TASK_PHP_017`
refused.** The claimed difference — §A2a narrowed the *evidence* to fit the
artefact, this widens the *artefact* to fit the evidence — **is the thing to
attack.**

### F42 — ⚠⚠⚠ ROW 2's HEADLINE IS REFUTED BY CONSTRUCTION, AND SO IS F39's DIRECTION

`TASK_PHP_017` did what a review is for. **Three of my own claims and the row's
headline are wrong.** Every number below was re-derived by the reviewer, who
**first reproduced the shipped R3 exactly** (`2029.42` against the record's
`2029.4`) — which is what licenses the comparison.

**B1 — *"the row's cost sits exactly where safe Rust cannot reach it"* is FALSE.**
A hoisted re-slice reaches 80.6 % of it:

```rust
let w0: &[u8] = &s[..=frm];      // ONE check, hoisted OUT of the loop
while n <= frm { start = n; let m = mbtab(w0[n]) as usize; n = n + m; }
```

| | `Ir`/window byte | vs R4 |
|---|--:|--:|
| shipped `safe_tuned` (R3) | 3.4451 | **+13.50 %** |
| **`v1`, safe, in contract** | **3.1151** | **+2.62 %** |
| `unsafe` (R4) | 3.0354 | — |

**Zero `unsafe`. Identical checksums on all seven inputs, adversarial cells
included. In contract by `harness/check.py::spelling_matches` itself** — every
backticked Rust spelling the shipped R3 satisfies, no `forbidden` match. In the
disassembly the `cmp`/`jae` panic pair vanishes from **both** walks and **`v1`'s
start walk is instruction-for-instruction R4's**, seven opcodes, different
register allocation.

⚠ **The right action is NOT to re-ship R3** — `.memory/02-bench-rules.md`
forbids re-shipping for a cheaper spelling. **`v1` ships beside it as the
cheapest-found in-contract R3**, which makes `ph07` **the first php row that can
discharge F39's own obligation.**

**F39's direction claim is WITHDRAWN — it was a theorem, not an observation.**
The reviewer confirmed every one of my figures (`p22`'s **510.5×** exact, all
four directions correct, the PAT set exactly `p13 p34 p42 p49`) **and then
showed the inference does not follow:**

1. ⚠⚠⚠ **The statistic is `R3ship − min(R4 found)` with R3 held fixed, and a
   minimum can only fall. A row in that column that moved *toward* safe Rust
   CANNOT EXIST.** *"Every one against safe Rust"* is arithmetic.
2. ⚠⚠ **The base rate was hidden.** *"Four rows of 22"* implied four searches;
   `results/synthesis.md:369-401` records an R4-side search on **19 of 33 rows,
   and eleven found nothing.** The R4 endpoint is degenerate more often than not.
3. ⚠⚠ **Three of the four counterparts are OUT OF CONTRACT** by their own
   patterns' records (`p13`, `p12`, `p10` — `.memory/01-ladder.md` calls `p10`'s
   *"the **rejected** R4 candidate"*). **Only `p22`'s is admissible.**
4. ⚠⚠ **`SYNTHESIS.md:271-277` ALREADY SAYS IT IS A SEARCH-EFFORT ARTEFACT** —
   *"the R3-side levers … are easy to find; the R4-side levers have to clear the
   prover"*. **I converted a statement about which side got searched into a prior
   about the true value.** On the R3 side the PAT record moves **≥ 9 rows toward
   safe Rust**, often bigger (`p16 +27/+77 → −199/−2545`).
5. ⭐⭐ **And B1 is the direct confirmation from inside this programme**: an
   R3-side search on `ph07` moved **+13.50 % → +2.62 %**, *for* safe Rust, and
   **larger than three of the four R4-side moves the withdrawn claim rested on.**

**What survives, and it is the part that mattered**: both rows' ladders are
`fixed-R4 bound`s with **no search on either side**, `ph03`'s own hashed `why`
already demands *"an in-contract spread beside its headline"*, and **a row that
has searched neither side is unbounded in BOTH directions.**

⚠ **Two smaller corrections of mine, same review:** F38/F40's *"3 of 5 commits
name a later fix"* is **2 of 5** — `ph12`'s `896a5216d73d` **is** the fix; and
F39's *"byte-identical across six PAT patterns"* repeats the paragraph's **own
stale self-description** — it is in all **33**, in four variants.

⭐ **What survived a hard attack**, listed because clean negatives are the
review's other half: the proof killed **22 of 22** mutants, **ten of them
spec-side**, so R5's postcondition pins the function and not merely memory
safety; `lemma_mbtab_matches` verified with no `assume` and no sixth trusted
item; the `broadcast use` scoping did **not** weaken a spec; R1h's positional
fidelity holds — the reviewer brace-matched `PHP_FUNCTION(mb_strcut)` across
**nine** tags and the guard lands where upstream put it; and the `memcpy`
(~2 %) and wall-clock (5.4 %) caveats re-derive to the digit. **Eighteen clean
negatives in all.**

### F41 — ⭐⭐ ROW 2 IS BUILT, AND THE TWO ROWS DISAGREE ABOUT WHAT SAFETY COSTS

> ⚠⚠⚠ **EVERY NUMBER BELOW WAS MEASURED ON A CORPUS THAT NO LONGER EXISTS.
> `TASK_PHP_018` REBUILT THIS ROW (F43/F47) — read F47 for the live ladder.**
> The shipped R1h is now hunk (a) alone, `inputs/gen.py`'s restriction is gone,
> and the benign domain grew by the 13.5 % the withdrawn hunk changed.
> **R2 +57.67 → +59.77 · R3 +13.50 → +11.98 · R4 ≡ R5 still byte-identical
> UP TO RELOCATIONS** (`md5_fn_norel`; ⚠ `md5_fn` itself differs — F47).
> ✅ **Claims (a) and (b) below survive unchanged; (c) halved and its
> cross-check evaporated.** ⚠ **And B1's `+2.62 %` is superseded by `+1.96 %`,
> re-derived — do not quote the old figure.**

`ph07-strcut-cursor` — `mbfl_strcut`'s `mblen_table` arm, `mbfilter.c:1179-1259`,
CRASH-124, tier `narrowed`. **Gate `PASS`**, contract `be5f5818ffa625c7`, R5
**21/0**, 2 justified `loud`. ⚠ **UNREVIEWED** — nothing here is in
`.memory-php/` yet (rule 9). `-O3 isolated`, `Ir`/window byte, **within-row
only**:

| `c-gcc` | `c-gcc-h` | `c-clang` | `safe_naive` | `safe_tuned` | `unsafe` | `verus` |
|---:|---:|---:|---:|---:|---:|---:|
| +27.31 % | **+27.31 %** | +4.81 % | **+57.68 %** | **+13.50 %** | — | **0.00 %** |

⚠⚠⚠ **THE HEADLINE PUBLISHED HERE IS RETRACTED — SEE F42.** It read: *"`R3`'s
two walks are BYTE-FOR-BYTE `R2`'s … no safe spelling removes that check … the
row's cost sits exactly where safe Rust cannot reach it."* **`TASK_PHP_017`
refuted it by construction**: a hoisted `&s[..=frm]` re-slice reaches **80.6 %**
of the R3→R4 gap in safe, in-contract Rust (**+13.50 % → +2.62 %**), and its
start walk is instruction-for-instruction R4's.

**What survives is the measurement and the mechanism, not the impossibility
claim**: the *shipped* R3's two walks are byte-for-byte the shipped R2's — start
walk **9 insns + 1 bounds branch** in both, **7 + 0** in R4/R5 — so **the shipped
R3's entire gain over R2 is the copy and the fold**, and the mechanism predicts
the measurement to **2 %** with no fitting. ⚠ **The error was quantifying over
all safe spellings after searching one.** *"Nobody found one"* and *"none
exists"* are different claims and only the first was ours.

⚠⚠ **SO THE TWO BUILT ROWS ANSWER THE SAME QUESTION WITH OPPOSITE SHAPES, AND
THAT IS THE PROGRAMME'S FIRST REAL COMPARATIVE RESULT:**

| | `ph03` | `ph07` |
|---|---|---|
| what tuning recovers | **86.4 %** of the naive gap | **76.6 %** shipped — ⚠ **and the *"none of it from the pattern's own loop"* leg is GONE**: `v1` recovers the walks too (F42) |
| the upstream fix costs | a **RATE**: ∓3.0 `Ir`/line, **sign depends on the compiler** | a **CONSTANT**: +7.3 `Ir`/call gcc, +9.2 clang — both guards sit **outside both loops** |
| the fix is | **dead in one hunk, incomplete in the other** | ✅ **complete** — 15 333 over-reads → **0**, no residue |
| `R2`–`R5` vs `R1h` | must diverge (a rung built to the fix would panic) | **are ports of it** — because the fix is complete |

⭐ **`.memory-php/02`'s rule *"R2–R5 are NOT ports of R1h"* held by its
conditional, not its conclusion** — here they *are* ports, and the reason is a
measurement rather than a preference.

**Three more results, each measured rather than argued:**

1. ⭐⭐ **THE OVER-READ DOES NOT CHANGE THE ANSWER, AND THE CLAMP THAT ARRIVES
   TOO LATE TO PREVENT IT IS EXACTLY THE CLAMP THAT HIDES IT.** 15 333
   over-reading calls re-run under **seven** different out-of-bounds fillers:
   **0 answers move.** Must-fire control (delete `mbfilter.c:1227`'s
   `start > len`): **13 293 of 15 333 move.** ⚠ **That is why this shipped
   byte-identical in six releases and why no test suite could have seen it** —
   and it is a sharper statement of the same shape as `ph03`'s dead hunk.
2. ⭐ **THE 2010 WALK REWRITE IS NOT THE FIX.** `d9dda48f8a7e` made the walk test
   before it reads; **that rewrite alone still over-reads on 13 293 of the same
   calls.** **The loop shape is not the fix; the bound on `from` is.**
3. ⭐⭐ **ONE FUNCTION, ONE GUARDED WALK AND ONE UNGUARDED ONE** — and the
   asymmetry is **three asymmetries at three scales**, with **the correct code
   ADJACENT to the incorrect code at every scale**: the end walk is bounded three
   lines below an unbounded start walk; the sibling entry point `mb_strimwidth`
   **already clamped `from` from above in the pinned 5.0.0 tarball**; and the fix
   arrived in the caller. ⚠ **It is not "the author forgot"** — the start search
   *is* compared against `from`, and **a comparison against an attacker-controlled
   scalar reads as a bounds check.**

**Two convergences with manager findings, reached independently:**

- ⭐ **F35's family, at row scale.** The engineer's history table was **wrong in
  both directions** — one spelling reported absence where the guard had been
  *renamed*, one unanchored pattern reported presence where the hit was in a
  *different function* — **and neither error is visible from its own output. The
  first version passed a green gate.** ✅ Caught, corrected, re-gated, and kept
  in `NOTES.md`. **Ask about a FUNCTION, not about text.**
- ⚠ **F39, confirmed from the other side**: `ph07` also ships **no
  `controls/spellings.py`**, so *"no ratio is the cost of safety"* — **the debt
  is now on both built rows**, and the engineer flagged it unprompted.

⚠ **Three caveats the row states rather than hides:** `memcpy` is outside
`kernel_exclusive_ir` and **three rungs call it and three do not** — measured, the
hidden term is **~2 %** (R2-vs-R4 is +55.4 % total `Ir` against +57.7 %
kernel-exclusive); **the wall clock can decide nothing here** — R4 and R5 are the
same 255 instructions and their medians differ **5.4 %**, more than any
difference in the table; and `provenance.c_lines` **pins one span while this row
lifts two**, a schema gap now wanted by a second row.

### F40 — the fix hunt is now done for the WHOLE catalogue, once — `.tasks-php/FIXSURVEY_001.md`

`ph07` cost a task to *"where is the upstream fix?"*. **That question is now
answered mechanically for every catalogued row** (`python3
.tasks-php/fixsurvey.py`): **91 of 91, zero unmapped, zero fetch failures.**
Only what changes a decision:

- ⚠ **8 rows have the `ph07` shape — the fix is in ANOTHER FILE**: `ph07 ph27
  ph54 ph82 ph83 ph88 ph89 ph90`.
- ⭐⭐ **THREE of those are one sub-pattern: an EXECUTOR defect fixed in the
  COMPILER.** `ph54`, `ph82`, `ph83` all cite `Zend/zend_execute.c` and are all
  fixed in `Zend/zend_compile.c` (+ the parser). **For VM-level defects the
  repair is often in the code that EMITS the opcodes, not the code that runs
  them.** ⚠ **`R1h` for these is not a line you can add to the kernel**, and each
  must say so. ⭐ `ph27`'s file was **also moved** (`ext/standard/reg.c` →
  `ext/ereg/ereg.c`), so a path search fails on it too.
- ⚠ **12 fixes touch ≥ 5 files** — `ph48` **17**, `ph24` 16, `ph16` 10, `ph26` 9,
  `ph23`/`ph83` 8, then `ph39 ph54 ph65 ph73 ph76 ph84`. ✅ `ph24` and `ph26` are
  **independently** `history_status: fixed-by-rewrite`; the two fields agree.
- ⚠⚠ **`ph36` has no sha at all** — `(bison-regeneration; no single commit)`,
  **the only such row in the corpus**, so §F5 needs one escape hatch (F38).
- ⭐⭐ **28 of 90 rows (31 %) were fixed in 2010 or later**, against a 5.0.0
  release of 2004-07-13. **Each is either *the defect survived 6–21 years* or
  *the named commit is a later hardening*, and the survey cannot tell them
  apart — only the tag check can.** ⚠⚠ ⚠ **This finding said *"every case tested has come out the second
  way — `ph12`, `ph21`, `ph22`"*; `TASK_PHP_017` refuted `ph12`: `896a5216d73d`
  **is** the fix. It is **2 of 5**, not 3 of 5** — still enough to make the tag
  check mandatory, and the correction is exactly why it is. That is what makes the
  per-row tag check mandatory rather than cautious.
- ⭐ **`ph22` was the standout — fix dated 2025 — and settling it produced the
  third instance rather than a headline.** Traced across eight tags: the
  memory-safety hole closed in **5.1.0**, when `INC_OUTPUTPOS` arrived with an
  explicit `INT_MAX` guard; the expression then sat unchanged ~15 years. **`ph22`'s
  R1h is the 5.1.0 macro, not the 2025 commit**, and *"PHP shipped it for 21
  years"* — which this finding published — **is withdrawn.**
  ⭐ **What the 2025 commit really fixes is better**: signed-overflow UB **in the
  macro's ARGUMENT**, `(arg + (arg % 2))` wrapping at `INT_MAX` *before*
  `INC_OUTPUTPOS`'s guard runs — **an overflow-checking macro handed an
  already-wrapped value.** ⚠⚠ **That is `ph20`'s catalogued shape in a second
  function**, surviving nineteen years **inside the guard meant to prevent it**.
- ✅ **A clean negative worth recording.** The 7 rows an earlier version called
  *"unmapped"* are the `LOGIC-`-prefixed ones — the corpus uses **three** id
  prefixes and the parse knew two. ⚠ **Checked deliberately, because `LOGIC-`
  ids also appear under `rust-eval/`, which would have put seven rows'
  provenance on the Rust port** — against `SOURCES.md` and against the standing
  instruction that the port is a reference, never ground truth. **It does not:
  all 24 `LOGIC-` rows are in `index.csv` with ordinary `c_file_line` and
  `fix_commit` cells, and `ph48` cites the `c_file_line` `V5C-166` carries.**
- ⚠ `ph49` and `ph50` resolve to **one** corpus id and commit (CRASH-153). Two
  rows from one report is legitimate — the catalogue splits by mechanism — **but
  nobody has checked these two are distinct.** Flagged, not judged.

### F39 — ⚠⚠⚠ `ph03`'s LADDER IS A PAIR OF SPELLINGS, ITS OWN CONTRACT SAYS SO, AND THE PAT RECORD SAYS THE MISSING NUMBER MOVES **AGAINST SAFE RUST**

**This is not a new caveat. It is an obligation `ph03` already carries, in its
own hashed block, undischarged.** `spec.md`'s `why` — the NAMED-SPELLING
STANDARD paragraph, byte-identical across six PAT patterns — ends:

> *"**Every pattern owes an in-contract spread beside its headline**; on the R3
> side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from
> TASK_021 …, on the R4 side ONLY p05 and p16, and p01 and p08 neither."*

`ph03` ships a headline (F33's ladder) and **no spread**. Its `controls/` holds
`negatives.py`, `fix_incomplete.c` and two patches — **no `spellings.py`**,
though the control is a solved, shipped thing on **four PAT rows** (`p13 p34 p42
p49`).

> ⚠⚠⚠ **THE DIRECTION CLAIM BELOW IS WITHDRAWN AT F42.** Every figure in it is
> exact and was re-verified; **the inference is not.** The statistic is
> `R3ship − min(R4 found)` with R3 held fixed, so a minimum can only fall and
> *"every one against safe Rust"* is a theorem. `SYNTHESIS.md:271-277` already
> says the asymmetry is a **search-effort artefact**, and on the R3 side the
> record moves **≥ 9 rows toward safe Rust**. **Read F42 before quoting any of
> this.** ⚠ The **obligation** half of this finding stands untouched.

⚠⚠ **And PAT's own headline result is that this is the biggest term.**
`results/SYNTHESIS.md` **Result 1: *"the safety tax is a property of a pair of
spellings, and the check is rarely the biggest term."*** Where anyone searched
the R4 side — **four rows of 22** — applying the result moved **three out of
their buckets, every one against safe Rust**:

| row | shipped | cheapest admissible R4 found |
|---|---|---|
| **p22** | `+2.00 / +2.00` | **`+125.00 / +1021.00`** — **510× on the large band** |
| **p13** | `−177 / −1054` | `+44.00 / +77.00` — **sign flip** |
| **p12** | `+3.00 / −26.00` | `+20.00 / +66.00` — **sign flip on `large`** |
| **p10** | `−323 / −603` | `−129.00 / −241.00` — **60 % of the margin was R4 spelling** |

**So the prior is not neutral.** `ph03`'s `safe_tuned +3.7 %` and *"tuning
recovers 86.4 % of the naive-safe gap"* are exactly the shape of claim that a
searched counterpart has moved before — and `.memory-php/02-ladder.md` publishes
them **in the authoritative layer**, where rule 9 makes them supersede.

⚠ **What is NOT claimed**: no figure is retracted. PAT's rule is *never re-ship a
rung because a cheaper spelling was found* — the shipped cell stays and is
published as a **`fixed-R4 bound`**, with the cheapest-found beside it, **and
neither is "the true one"**. **`ph03`'s numbers are fixed-R4 bounds that are not
labelled as such**, which is the one thing `SYNTHESIS.md` §2 says loses
information.

⚠ **Nor is `ph03` uniquely at fault** — the same paragraph records `p01` and
`p08` owing both sides. **But `ph03` is the template 90 php rows will clone**, so
an unlabelled headline here propagates in a way it does not on a finished corpus.

**→ Two actions, neither urgent enough to interrupt a build, both before any
number reaches the crash course:** (1) **label `ph03`'s ladder `fixed-R4
bound`** wherever it is published — `.memory-php/02-ladder.md`, F33, the START
HERE box; (2) **a task that ports `controls/spellings.py` to `ph03`** and
publishes the spread. ⚠ **(1) is cheap and (2) is not, so do (1) first** and do
not let (2)'s cost delay it — an unlabelled number is the defect, not a missing
control.

### F38 — ⚠⚠⚠ THE `fix_commit` WAS IN A COLUMN OF THE CORPUS INDEX ALL ALONG — AND IT IS NOT ALWAYS *THE* FIX

**Both halves of this finding matter and the second is the one that saves a row.**

**Half 1 — the lookup nobody did.**
`paper/evaluation/security/vuln-corpus-5.0/index.csv` has a **`fix_commit`
column**. Measured: **all 166 corpus rows carry one**, and **142 of the 145 ids
`CATALOGUE.md` cites resolve to one** (the 3 that do not are `V5C-015`,
`V5C-116`, `V5C-173` — ⭐ **exactly the three C.1 kills that say "merged by the
corpus itself", so the CSV's `merged_members` column independently confirms all
three**). `CRASH-124`'s cell is `cb3cca21b345`; `CRASH-115`'s is
`f95c1df58349`, the commit `ph03` ships as its R1h.

⚠ **That is NOT two independent sources agreeing, and this line said it was.**
`TASK_PHP_013` took `ph03`'s sha from **the corpus's own history layer**
(`TASK_PHP_012` §7.3 *"predicted this from the corpus's history layer"*), so
CSV and row share a source. **What calibrates the column is weaker and more
useful than agreement: the identifier survived BEHAVIOURAL verification.**
`TASK_PHP_013` applied the patch and measured its effect over 12 600 documents,
and `TASK_PHP_014` attacked the result. **The column has been confirmed correct
exactly once, by measurement, on one row** — which is precisely why half 2 below
is not paranoia.

⚠ **Nobody joined the two halves that were both already found.**
`TASK_PHP_012` **M7 counted this very column** (*"166 distinct fix_commit
values… and no repository to resolve them against"*) and correctly called the
blocker *resolution*; `TASK_PHP_013` **solved resolution** (F26, the `.patch`
URL). **From task 13 the answer was one lookup away, and at task 15 an engineer
searched the GitHub commit API and five tag snapshots instead, and the manager
then bisected five tags on top of that.**

⭐ **Why the search HAD to fail, and it is not carelessness.** Everyone reasoned
about the row as *`mbfl_strcut`*, so everyone searched **by function name**. The
fix's subject says **`mb_strcut()`** and its diff touches **`mbstring.c`**.
`TASK_PHP_015`'s search was correct and its corpus was wrong — and it bounded its
own claim explicitly (*"'no fix_commit exists' is **not** proved"*), which is why
this cost a task and not a row. **The key you hold is not the key the answer is
filed under** — `F1`'s three-frames problem, arriving in the *tooling*.

**Half 2 — ⚠⚠ THE COLUMN NAMES *A* FIX, NOT NECESSARILY *THE* MEMORY-SAFETY FIX.**
All five commits fetched and read. **Two of four batch rows would have shipped a
wrong R1h if the column had been taken on faith:**

| row | CSV `fix_commit` | what it actually is |
|---|---|---|
| `ph29` | `445daac3ab1a` (2004-07-28, Ilia) | ✅ **exact and minimal** — adds `if (to_read <= 0) … RETURN_FALSE;` and nothing else |
| `ph16` | `99e290f882c9` (2004-09-17, Wez) | ✅ **the right fix, inside a 10-file 27 KB change** — *"Bug #24189: possibly unsafe select(2) usage. We avoid the problem by using poll(2)"*; it **introduces** `PHP_SAFE_FD_SET` and applies it at the row's line |
| `ph12` | `896a5216d73d` (2006-04-25, Tony) | ❌ **a LATER fix.** Its own pre-image is already `if ((offset + len) >= s1_len)` — **the `len &&` short-circuit, which is the 5.0.0 defect, was gone before this commit.** This one fixes bug #33605, a negative offset with `len == 0` |
| `ph21` | `c591f022f8ab` (2015-05-10, Stas) | ❌ **a later fix, nine years on.** *"Fix bug #69403 and other int overflows"* adds `if (result_len > INT_MAX)` to a function that by then is **already** `size_t` + `safe_emalloc` — the 5.2.0 change that removed the defect |

⭐⭐ **So the column and the tag bisect are COMPLEMENTARY, and neither alone is
sufficient.** The column hands you a real sha with a security-sounding subject
that touches the right function; **only the bisect tells you whether it removes
*your* defect.** The `UPSTREAM_001` survey is not made redundant by this finding
— **it is what caught it.**

**Half 3 — the same CSV has a `history_status`, and ⚠ IT IS NOT THE SHORTCUT IT
LOOKS LIKE.** Two values: **`historical-known` 149**, **`fixed-by-rewrite` 17**.

- ✅ **Useful**: **10 catalogued rows are `fixed-by-rewrite`** — `ph24 ph26 ph36
  ph46 ph63 ph67 ph71 ph76 ph78 ph80`. **Expect F34's shape on every one of
  them**, and budget the archaeology before picking one.
- ✅ **Bounded**: **exactly ONE corpus row has a non-sha `fix_commit`** —
  `bison-yycheck-table-oob` (**`ph36`**), whose cell literally reads
  `(bison-regeneration; no single commit)`. **So `PROTOCOL_PHP.md` §F5's
  "sha-pinned real fix" needs ONE documented escape hatch, not a redesign** —
  and the corpus tells you in advance which row needs it.
- ⚠⚠ **The negative result, and it is the one that matters: neither field
  discriminates half 2.** All four batch rows are `historical-known` **with
  `confidence: high`** — **including `ph12` and `ph21`, whose commits I proved
  are later fixes.** **`historical-known` + `high` does NOT mean "this commit
  removes the 5.0.0 defect".** Nobody may use these fields to skip the check.

⚠ *Coverage note*: 81 of the 91 Part A rows expose a corpus id to a simple
parse; the other 10 (`ph48 ph52 ph66 ph75 ph77 ph79 ph82 ph83 ph84 ph85`) are a
**limit of the parse, not of the corpus** — resolve them by hand when reached.

**→ The pre-build checklist gains the item `TASK_PHP_015` asked for**, in the
form its own evidence now demands: *"read `index.csv`'s `fix_commit` for this
id, fetch the patch, **and confirm against the tags that it is the commit which
removes the 5.0.0 defect** — if it is not, cite both. Check `history_status`
too, but **never as a substitute for that confirmation**."*

### F37 — the two kills that survived the audit are the two that were written down as settled

`ADJUDICATION_001` closed with *"**four** instances in one audit (CRASH-136,
CRASH-157, CRASH-033, CRASH-053) — enough that it is the audit's main result"*:
each a kill whose stated reason the C-side bar forbids. ⚠⚠ **It is six.**
`CATALOGUE.md`'s `C.1` — headed *"Kills — **exact** C-side duplication"* — still
holds **`CRASH-106`** and **`CRASH-109`**, and **neither note claims exactness**:

| | the note's own words | what that is |
|---|---|---|
| CRASH-106 `nl2br` | *"distinct only in needing a ~358 MB input, **which is a worse kernel**"* | **cost** |
| CRASH-109 `wordwrap` | *"the second `alloced` growth path at `:692` **muddies the extraction**"* | **cost** |

**Both name the distinguishing feature and then discount it for cost** — and
`PLAN_PHP.md` §3.1 admits a *slight variation* as its own row here, on an
explicit user decision. ✅ **Both admitted, verified at source**
(`ADJUDICATION_002.md` §2): `ph92` `nl2br` `string.c:3593` — the corpus's **only**
sizing wrap where the multiplier is a constant, so the attacker has **one** free
value and the ~614 MB input is *a consequence of the mechanism*; `ph93`
`wordwrap` `string.c:679` + **`:692-694`** — the corpus's **only** buffer
**regrown mid-emit**, by arithmetic that is itself unchecked `int` and divides by
an attacker-controlled `linelength`.

⚠⚠ **AND BOTH OF THOSE TWO LINES USED TO CARRY A WRONG FACT, which is the
finding's own point landing on the finding.** This entry said **307 MB** (it is
`2^32/7 = 613 566 757`; at `2^31/7` the store goes negative and the allocation
simply fails) and cited `ph93`'s **`:682`** (the else-arm, in which `:692` —
the row's whole distinctness — is **unreachable**). ✅ Corrected in
`CATALOGUE.md` at `TASK_PHP_017` §2.2, and the evidence document's own §2 is
now marked in place rather than silently rewritten. ⚠ **`ph92`'s mechanism also
changed class**: `sizeof` yields `size_t`, so the RHS is 64-bit and is
**truncated by the store** into `int new_length` — **`ph21`'s class, not
`ph19`'s**, which *strengthens* the admission.

⭐⭐ **The reusable result is where the survivors were.** The audit found what it
went looking for; **the two it missed were sitting in the kill list under a
heading that asserts the criterion they fail.** `.memory-php/01-extraction.md`
already says *"an audit that re-examines only what it doubts measures its own
priors"* — **this is that finding's second confirmation, from the opposite
direction.** ⚠ **The remaining `C.1` rows are NOT re-examined**; four say
*"merged by the corpus itself"*, a stronger claim than a reviewer's judgement,
**and nobody has checked that either.**

## Open items — carried, not closed

| # | item | note |
|---|---|---|
| 1 | The pristine tarball lives under **another project's gitignored `.temp/`** and is deletable at any time | Phase 0 must land `patterns-php/SOURCES.md` with the sha256 + a per-file manifest before anything cites it |
| 2 | *"Where does the existing Rust port land on these scales?"* | **deferred, not deleted** (`DP-05`). Well-posed once the corpus exists |
| 3 | `.web/` does not know `results-php/` exists | deliberate. Do not teach it until there is something worth publishing |
| ~~4~~ | ✅ **CLOSED — and it had been closed for four tasks without the table knowing.** `ADJUDICATION_001.md` item 4 admitted CRASH-136; it is `ph13` (`CATALOGUE.md:91`, `:288`) | ⭐ **And it recovered CRASH-134 too, which no open item ever named.** ⚠ **The lesson is the table, not the row**: `PROTOCOL.md` rule 13 one level up — **when you close a finding, re-read the open-items table.** The successor item (m8) was real and is settled at `ADJUDICATION_002.md` |
| 5 | `EG(garbage)` is `zval *garbage[2]` with an unchecked `EG(garbage)[EG(garbage_ptr)++]` | a faithful temporal extraction **inherits a SPATIAL overflow**. Flagged, not bounded away — bounding it silently would be §4.2's invented non-defect. Manager decides |
| 6 | Four temporal merges flagged as probably wrong | ranks 21, 8, 12, 23. Split decisions owed at catalogue adjudication |
| ~~7~~ | ✅ **CLOSED at F9 — and the check turned out to be impossible.** All spatial `hotness` fields stay **reasoned** | The census holds **zero** spatial reports from `Zend/` or `ext/standard/`: 2156 of 2520 fault inside `libmysqlclient.so.14`, the rest in the regex matcher. **The census is struck as a source of spatial frequency evidence** rather than left as an open promise |
| 8 | Rank 15 (CRASH-158) may be spatial, not temporal | cross-check the two miners' lists at adjudication |
| 9 | ⚠⚠ **No php marginal `Ir` is comparable to any PAT one — and no two php runs are comparable to each other either** | `repo_path_bytes` is **15** bytes longer through the shim (⚠ this said **20**; corrected at `TASK_PHP_003`), and `gate.py`'s own `PYTHONDONTWRITEBYTECODE=1` adds `nvars` **+1** and `envp_stack_bytes` **+34** — measured directly at `TASK_PHP_004` (`25 + NUL + one 8-byte envp slot`). ⚠ **`TASK_PHP_003` gave that as +33 and that was a record-to-record difference between two SHELLS, not the variable's cost**: `ph00`'s own `envp_stack_bytes` moved **3686 → 3695** across two runs of the same gate with no source change, so the p01 delta was +33 and is now +42. **Never quote a php figure against a `pNN` one, and re-check the env block before quoting one php figure against another** |
| ~~10~~ | ✅ **CLOSED at `TASK_PHP_006` — `common-php/*.h` is in NO gate digest, and the `<row>/c/` symlink that was supposed to close the measurement half is BYPASSABLE** | `check.py`'s three `common/` globs are non-recursive and none matches `emalloc_shim.h`. The bridge half **fires** (F7). The symlink half was enforced by nothing (B1), was checked in `gate.py`'s preflight at `TASK_PHP_004` — and `TASK_PHP_005` **F-1** got round it twice, with rows that build, link and run a live allocator into neither digest. **`TASK_PHP_006` closes it** |
| 11 | A new php row costs **six commands (~28 min)**, not three | `gate → report → gate` is irreducible and `measure.py` builds nothing. Budget it. ✅ The three places that said three/five now say six (`TASK_PHP_004`) |
| ~~12~~ | ✅ **CLOSED — `.memory-php/` EXISTS**: `00-corpus` `01-extraction` `02-ladder` `03-numbers` `04-process` | Open from the programme's first task to its sixteenth. It carries **only php-specific** findings that survived a full engineer→reviewer cycle; the PAT `.memory/` 00–06 applies unchanged and is **not** restated. ⚠ **It supersedes any task report it contradicts** (rule 9) |
| 13 | ⚠ **`harness-php/*.py` is in NO digest, and putting it in one costs a 33-pattern re-gate** | `check.py`'s `srcs` would have to reach `harness-php/`, i.e. a `harness/` edit (`PLAN_PHP.md` §2.1). `TASK_PHP_004` landed the **cheap half**: `gate.py` writes `results-php/preflight/<row>.preflight.json` with the `harness-php/*.py` hashes, the manifest hash and whether `--no-provenance` was used. ⚠ **That record is evidence, not a pin — nothing hashes it** — ⚠⚠ **and `TASK_PHP_005` F-2 found it is worse than that: it is written one file per ROW, not per run, so a later preflight ERASES `provenance_skipped: true`; nothing anywhere detects a missing record; and the manager had made it uncommitted.** Being fixed at `TASK_PHP_006` (item 18) |
| 14 | ⚠⚠ **`provenance.py`'s overlap floor is SATISFIED BY DEAD CODE — the risk is a false PASS, not a false refusal** | Added at `TASK_PHP_004` for `TASK_PHP_003` M5. ⚠ **This row used to say the danger was a good row tripping a floor. `TASK_PHP_005` F-4 shows the opposite**: a kernel that implements *division*, cites *multiplication*, and hides the citation behind `#if 0` scores **100 % and is ACCEPTED** (`_normalise` drops lines starting with `#`, so `#if 0`/`#endif` vanish and everything between them counts); the same kernel without the dead block is refused at 11 %. ✅ **The floor is not too high** — a realistic `verbatim` `mul_function` lift scores 68 %. ⚠ **The check never reads `main.c`, the driver loop or the build, so it measures presence of TEXT IN A FILE, not presence of code in the benchmark**: a pass is not even evidence that the cited lines are compiled |
| 15 | ⚠ **The php staleness check is `gate.py --tool measure --check-stale`** and the mandated PAT `66/0` one does **not** examine `results-php/` at all | Both are now in `PROTOCOL_PHP.md` §E1 (`TASK_PHP_004`); today the php side is **2 records** |
| 16 | ⚠ **`TASK_PHP_004` edited `RECAP_PHP.md` — the manager's own handoff file** | `PROTOCOL.md` rule 4 reserves the state layer to the manager, and `TASK_PHP_004.md` did not forbid it explicitly. ✅ **The content is ACCEPTED — it is more accurate than what the manager was about to write** (the `+34` vs `+33` shell artefact, the `3686 → 3695` instability, items 13–15). ⚠ **But the boundary is real**: an engineer correcting the manager's numbers *in the manager's file* is how an unreviewed claim reaches the state layer without passing rule 9. **Future php task files must say explicitly that `RECAP_PHP.md` is manager-only** — the fix is one sentence in the task template, not a rollback of good work |
| 17 | ⚠ **PAT-SIDE, LATENT, DELIBERATELY NOT FIXED — and the php side now REFUSES the layout: `check.py:10314` and `measure.py:226` glob `<row>/c/*` NON-RECURSIVELY and drop the directory entry with `isfile()`** | so **every source file a row puts in a `c/` subdirectory is in no digest at all**, and `check.py`'s `--no-build` staleness scan misses it too, so editing one does not even mark a binary stale. ✅ **No row is affected today** — `find patterns patterns-php -mindepth 3 -maxdepth 3 -type d -path '*/c/*'` is empty. ⚠ **Fixing it is a `harness/` edit = a 33-pattern re-gate for zero present benefit.** Decision: **do not fix; FORBID the layout on the php side** (`TASK_PHP_006`), and carry this row so the next person to reach for `c/sub/` finds out first. ⚠ It matters more here than on PAT: php rows are *extracted* C and `c/zend/` is an ordinary thing to want |
| ~~18~~ | ✅ **CLOSED at `TASK_PHP_006`. The record is COMMITTED (minus `when`), the per-row overwrite is fixed by appending, and an absence is now a preflight NOTE** | `.gitignore:24-26` justified it as *"carries a `when` timestamp and the literal `gate_argv`, so it churns"*. ⚠ **`TASK_PHP_005` F-2c measured it: only `when` moves.** `sha256(rest)` is identical across two runs (`d91ce008ad273b36`) and `gate_argv` is a function of the command, **which is exactly the evidence M6 wanted**. The split the manager asked the reviewer to price **exists and costs one field**. → `TASK_PHP_006` commits the record without `when` and fixes the per-row overwrite |
| ~~19~~ | ✅ **CLOSED: THERE IS NO SIZE RULE. The 200-word rule is withdrawn — it was calibrated on n = 1 and is broken by 30 of 33 PAT rows** | `TASK_PHP_005` F-5: up to **2 533** words, and **`p01` — the template every row clones, and the row `PROTOCOL_PHP.md` cites as complying — is 201.** The 200 was simply the measurement of the one row that had been measured. ⚠⚠ **This is the THIRD version of this rule and the second that could not be met**; `RECAP_PHP.md` itself warns that *"a size rule that cannot be met is worse than none"*. **The manager must not invent a fourth number** — `TASK_PHP_006` measures the corpus distribution and proposes a limit, or proposes a structural rule instead, **and whatever lands must be enforced by a check or dropped** |
| ~~20~~ | ✅ **CLOSED at `TASK_PHP_006`** (was: `gate.py <row> --preflight` silently forwarded the flag and ran the tool) | `argparse.REMAINDER` collects from the first positional (`TASK_PHP_005` F-7). ⚠⚠ **The manager's own 06:55 `ph00.preflight.json` — cited as manager-verified evidence for the gitignore decision — is an instance: a FAILED `check.py` launch (`tool_returncode 2`) recorded as a preflight.** Part of the evidence for a manager decision was an artefact of a CLI bug |
| ~~21~~ | ✅ **LANDED** — `TASK_PHP_012` M4 — 12 rows declare `verbatim` whose defect site is inside a `PHP_FUNCTION` / VM-handler / arg-parsing frame, i.e. **`narrowed`** — and NONE has been corrected in `CATALOGUE.md`** | ✅ **Re-run and reproduced by the manager** (`.temp/mgr/batch/tier_recheck.log`): `ph05 ph11 ph12 ph21 ph22 ph24 ph35 ph50 ph55 ph59 ph76 ph80`. ⚠ **A cost statement, never a filter — no row's admission moves.** But `provenance.py` reports overlap **against the declared tier's expectation** (50 % / 25 %) and `TASK_PHP_008` made that a report rather than a floor, so **a mis-declared `verbatim` row hands its reviewer a scary number that is indistinguishable from a bad extraction.** `TASK_PHP_012` said *fix before the first row*; `ph03` was unaffected, **but `ph12` and `ph21` are in the NEXT BATCH.** ✅ **Landing is staged and mechanical**: `python3 .tasks-php/land_m4.py --check\|--apply` edits Part A + Part B for all 12 and **refuses unless every row has exactly two occurrences** (dry-run: 24 edits, 2 each). **Blocked only by `PROTOCOL.md` rule 11** — `TASK_PHP_016` is reading `CATALOGUE.md`. **Land it the moment that task reports** |
| ~~22~~ | ✅ **m8 LANDED (`ph92`/`ph93`, kills withdrawn IN PLACE, `ph28` narrowed). ⚠ M1/M2/M3/M5 and m1 STILL OWED** — was: the rest of `TASK_PHP_012`'s catalogue corrections — M1 (6 of 12 "merges" are silent drops), M2 (the four-`LOGIC` set kill), M3 (CRASH-021 reverses → a `ph60` merge, not a kill), M5 (CRASH-061/126 in the wrong family), and the minors m1/m5/m8 | Batch them with item 21's landing (`PROTOCOL.md` rule 6) — they are all `CATALOGUE.md` edits and share its rule-11 block. ✅ **m8 is ADJUDICATED** (`ADJUDICATION_002.md` §2, F37): `CRASH-106` → **`ph92`**, `CRASH-109` → **`ph93`**, both admitted, mechanisms and citations verified at source, §4 gives the exact Part A / Part B / Part C edits. **What is owed is the LANDING, not the judgement** — and the catalogue goes **91 → 93** |
| ~~23~~ | ✅ **ALL SIX LANDED** the moment `TASK_PHP_016` reported — was: blocked by `PROTOCOL.md` rule 11 — `TASK_PHP_016` is reading `CATALOGUE.md`, `.memory-php/` and `PROTOCOL_PHP.md`. **Land all five in ONE pass the moment it reports** (rule 6) | **(a)** `python3 .tasks-php/land_m4.py --apply` — the 12 mis-tiered rows (item 21). **(b)** `ADJUDICATION_002.md` §4 — add `ph92`/`ph93`, delete their `C.1` kills **and record the re-adjudication in place** (a kill that vanishes is worse than a kill that was wrong — M1), narrow `ph28`'s uniqueness claim to *resident*. Catalogue **91 → 93**. **(c)** `.memory-php/02-ladder.md` — F34's *"the guard moved to the PROLOGUE"* is **superseded**: it moved to the **CALLER, in another file** (F38), and the entry names `ph07`'s R1h, which is now `cb3cca21b345`. **(d)** `.memory-php/00-corpus.md` — its header says findings run *"F1–F34"* (rule 13: headers rot), and it should carry the **`fix_commit` column** and the **`grep -a`** hazard. **(e)** `PROTOCOL_PHP.md` — the `grep -a` rule (F35) and the pre-build item `TASK_PHP_015` asked for, in F38's stronger form: *read the CSV's `fix_commit`, fetch the patch, **and confirm against the tags that it removes the 5.0.0 defect**; if not, cite both*. **(f)** `.memory-php/02-ladder.md` again — **label row 1's table `fixed-R4 bound`** and carry F39's direction prior; the caveat there is the engineer's and is weaker than the situation |
| ~~24~~ | ✅✅ **CLOSING BY DELETION, NOT BY A RULE — `TASK_PHP_018` §1.** `TASK_PHP_017` §4 found hunk (a) alone is memory-safety-complete and is what PHP shipped from 5.2.17, so the clause rescued an avoidable R1h choice; **F43 then found WHY — upstream deleted hunk (b) in `c2471b495009` as bug #49354, with a regression test. Stage 7h was right.** With R1h re-pinned to the converged configuration the corpus restriction goes away and **no clause is needed at all.** ⚠ **The reviewer's guard clause is kept in `TASK_PHP_017_REPORT.md` §4 unlanded**, as the fallback if `TASK_PHP_018` §5.1 declines the rebuild. Was: **`ph07` is built and unreviewed, and its report proposes a `PROTOCOL_PHP.md` §A2a addition that was LOAD-BEARING for the row** | The row gates green only because `inputs/gen.py` keeps the upstream fix's guards **dead** on the measured corpus: `cb3cca21b345` hunk (b) **changes benign output on 15 870 of 117 612 non-crashing calls**, and `check.py` stage 7h requires R1h ≡ R1 on every non-adversarial input. **Proposed clause**: *where the upstream fix changes benign behaviour, the measured corpus must leave its guards dead, `gen.py` must assert it, and the behaviour change is measured in `controls/` where it cannot contaminate the ladder.* ⚠ **NOT LANDED — rule 9.** The manager landed only its own verified items (§F 5–6). **`TASK_PHP_017` must attack this clause specifically**: it is a rule invented to make one row gateable, which is exactly the shape that needs a second row before it becomes protocol |
| ~~25~~ | ✅ **CLOSED at `TASK_PHP_018` §3 — `extra_spans` landed in `harness-php/provenance.py`, additive, ~60 lines, NO PAT re-gate, `ph03`/`ph00` byte-identical.** ⚠⚠ **And it exposed something worse than it fixed**: the row's overlap headline falls **75 % → 61 %** and the caller frame — **the span R1h lives in** — scores **15 %**. It is `modelled` text inside a row whose single `tier` word says `narrowed`. ⭐ **A single `tier` word is the wrong shape for a multi-span row** (100 % / 75 % / 15 % here); the schema now lets a row say it lifts three spans and **not at what fidelity each**. ✅ Deliberately not extended — a second schema change on n = 1. Was:; `ph07` lifts THREE — and the UNPINNED one is where R1h lives** (⚠ this said TWO; `TASK_PHP_017` M1 counted three) | `TASK_PHP_015` §2.5 deferred the schema change; a second row now wants it. ⚠ **It is a `harness-php/` edit, so it costs no PAT re-gate** — but it moves the php preflight record. Decide at the review |
| 26 | ⚠⚠ **THE SPELLINGS DEBT IS NOW ON BOTH BUILT ROWS** (F39) | `controls/spellings.py` exists and works on **four PAT rows** (`p13 p34 p42 p49`); neither php row has one. **Two actions, and the first is cheap**: (a) ✅ **DONE** — both ladders are now labelled `fixed-R4 bound` in `.memory-php/02` and F33/F41; (b) ▶ **`TASK_PHP_018` §2 ports it to `ph07`; `ph03`'s half stays OWED.** ⚠ **Do (b) before any number reaches the crash course.** ⚠⚠ **The reason given here was WITHDRAWN at F42** — it said *"the PAT record is that the missing number moves against safe Rust, three times out of four"*, which is a theorem about taking a minimum, not evidence. **The real reason is stronger and has no direction in it: a row that has searched NEITHER side is unbounded in BOTH**, and `ph07`'s own R3-side search then moved **+13.50 % → +2.62 %**, *toward* safe Rust |
| ~~27~~ | ✅✅ **DONE at `TASK_PHP_018` §2 — and BOTH SIDES were searched.** `controls/spellings.py` is the **first in `patterns-php/`**. **`fixed-R4 bound +11.98 %` · `cheapest-found in-contract +1.96 %` (`r3_reslice`)**, both labelled, `safe_tuned.rs` **not** re-shipped. ⚠ B1's `+2.62 %` is **superseded, not carried** — it was measured on the corpus the rebuild deleted. ⭐⭐ **The R4 side is DEGENERATE** (four spellings, none better than a tie), making `ph07` **12 of 20** rows where an R4 search found nothing — so this bound is over a **searched** endpoint. Was: | +13.50 % → **+2.62 %**, safe, in contract by the gate's own matcher, checksums identical on all seven inputs. ⚠ **Do NOT re-ship R3** (`.memory/02-bench-rules.md`); publish **both, labelled**, which is what `ph03`'s own `why` has demanded all along. ⭐ **This makes `ph07` the first php row that can discharge F39's obligation** — and it should be done before `ph03`'s, because the code already exists |
| 28 | ▶ **`TASK_PHP_019`.** ⚠⚠ **Two MORE `C.1` kills reverse — `CRASH-126` and `CRASH-163`** (`ADJUDICATION_002.md` §5) | Killed **twice** for reasons the bar forbids: once in `C.4`'s set-shaped *"ordinary null-deref"* kill, then again under `C.1` as *"same fallible call's failure not tested"* — **and in both the failure IS tested.** `TASK_PHP_012` M5 is the same finding independently. ⚠ **`CRASH-101` and `CRASH-061` are *slight variations*, which §3.1 admits, so they are candidates too and nobody has looked.** Catalogue **93 → 95+** |
| 29 | ✅ **DISCHARGED at `TASK_PHP_019` → F44 — and the answer is that the rate tracked the TEST.** The mechanism test on the same population the cost-word test scored 17 % on returns **8 reversals**; across the programme **40 of 46 kills ever written down are now reversed**. ⚠ **Landing is BLOCKED on `TASK_PHP_020`** (it is sampling Part A; +8 rows would corrupt its draw). Was: | *"ZERO of the remaining `C.1` notes contains a cost word, so `ADJUDICATION_002`'s predicted re-read finds nothing. The two that DO reverse need a DIFFERENT test — **does the C support the mechanism claim?** — which that document never runs on anything, **including on its own two admissions**."* ⚠ **I audited for a WORD and called it an audit for a REASON.** The cost-word test found the two kills it was shaped to find and is now exhausted; **the mechanism test is unrun on all 12** |
| 30 | ⚠⚠ **A SECOND ADMISSIBLE FORM OF R1h — a TAGGED UPSTREAM CONFIGURATION, pinned by `(tag range, function, body sha256)`** | `PROTOCOL_PHP.md` §C says R1h is *the real upstream `fix_commit`*. F43 makes `ph07`'s R1h a **subset** of one — hunk (a) of `cb3cca21b345`, which is byte-for-byte what four tags shipped and kept. **My argument is that what upstream KEPT is a stronger citation than what it once committed.** ⚠⚠ **It is still a protocol extension invented to make one row work — the exact shape `TASK_PHP_017` refused for the §A2a clause**, and the claimed difference (§A2a narrowed the evidence to fit the artefact; this widens the artefact to fit the evidence) is **unreviewed and is the thing to attack.** `TASK_PHP_018` §4.1 proposes the wording; **nobody lands it before a reviewer has hit it** (rule 9) |
| ~~31~~ | ✅ **DISCHARGED at `TASK_PHP_020` → F46. The mechanism sentences hold (1 of 15 on a seeded block, 1 of 4 on the chosen batch); the `▸ trigger` lines do not (3 of 19 would have cost an engineer time, against 0 wrong defect sites).** ⚠ **The rate is a LOWER bound** — *"a cheaper audit than mine would have returned 15/15"* — and the batch four, the most-scrutinised rows in the corpus, still yielded one. **Any follow-up audits `▸ trigger` lines only.** Was: | Every build so far has found the claim wrong or incomplete, and **three of the four instances were found by accident while doing something else** (`ph07`'s frame, `ph92`'s class, `ph93`'s unreachable arm; `ph29`'s is open — F36). **93 rows are catalogued and 2 are built**, so the rate decides how much a build task may lean on a Part B block. ⚠ **A sample that comes back clean is the useful outcome**, not a disappointing one — F21/F37's lesson applies to this audit as much as to the kills it was derived from |
| 32 | ⚠ **TWO CITATION ROTS, both found by a mechanical sweep of every rooted path in the manager docs — batch them** (rule 6; `.memory-php/` and `PROTOCOL_PHP.md` are open in running agents) | ✅ **First, the clean negative that is the point of running it: of ~500 backticked paths, the ONLY unresolved ones are row-relative (`c/kernel.c`), deliberately hypothetical (`patterns-php/shared/` — the thing F24 says nobody needs) or reports not yet written. No dangling pointer.** ⚠ **(a) `.temp/san_tests/` does not exist in this repo.** It is `/home/apt/repos_common/php-in-safe-rust/.temp/san_tests/` — **484 MB in ANOTHER project's gitignored scratch**, i.e. open item 1's hazard applied to F9's ASan census, which no document says. `.memory-php/00-corpus.md` carries the unrooted path, so an agent following it finds nothing — **and F35's whole lesson is that "found nothing" is indistinguishable from "isn't there".** ✅ `patterns-php/SOURCES.md` is the exception and does it right, both for the census trees and for the tarball (**re-checked today: 5595997 B, sha256 `5783e0c0…d6919`, matches the pin**). ⭐ **And F9's census re-derives EXACTLY, two months on: 2534 logs, 3199 reports, 2450 / 490 / 189 / 70.** ⚠ **(b) `.ph93` is used as the name of a DEMONSTRATION dotted row** in F16 and `PROTOCOL_PHP.md:431`, and `ph93` is now a real catalogued row (`wordwrap`). Rename the demo |
| 33 | ⚠⚠ **A php GATE RECORD IS WRITTEN IN THE REBOUND NAMESPACE AND IS READ IN THE REAL ONE — and it names the one directory `CLAUDE.md` most loudly forbids touching** | ✅ Measured on all **3** php gate records: every one keys its sources as **`common/digest_bridge.py`**, `common/driver.c`, `common/driver.h`, `common/driver.rs`. **Those files do not exist.** They are `common-php/`, and the key is correct *inside* `harness-php/root.py`'s rebinding — which is exactly how the php side reuses the frozen harness without editing it (`PLAN_PHP.md` §2). ⚠ **The hazard is a reader outside that namespace**: someone chasing a STALE key goes looking in `common/`, the **frozen PAT** tree, for a file that is not there — and this project's own F35 finding is that *"not there"* and *"I looked in the wrong place"* are indistinguishable from the output. ⭐ **`TASK_PHP_002_REPORT.md` §3 spotted it and said a reader *"has to come here to expand it"*; it then reached NEITHER `.memory-php/` NOR `PROTOCOL_PHP.md`** — grep confirms neither carries the words *rebind*, *rebound* or *namespace*. **A hazard that lives only in a task report is a hazard nobody will find.** ⚠ **Do NOT fix it**: the keys come from `check.py`'s root-relative derivation, so changing them is a `harness/` edit and a 33-pattern re-gate (items 13/17's decision shape). **Document it, in the batch** |
| 34 | ⚠⚠⚠ **BOTH BUILT ROWS ARE IN THE SAME FAMILY, THIS FILE HAS SAID *"rows built: 2"* FOR FOUR TASKS, AND NO DOCUMENT ANYWHERE SAYS IT** | `CATALOGUE.md` Part B is **93 rows in 20 mechanism families**; `ph03` and `ph07` are **both `S1` — unbounded cursor walk**, a family of 9. **So F41's *"the two rows disagree about what safety costs"* is a WITHIN-family result**, and every use of it as *"two rows"* overstates the spread it covers. ⭐⭐ **Read the other way it is the most useful thing the programme has produced**: two rows from ONE family disagreed on **four properties** — which map onto `PLAN_PHP.md` §9 items **2, 3 and 4** only; ⚠ **items 1, 5 and 6 have never been compared across the two rows, and item 5 cannot be until a spellings search exists on either** (F42) — so **the within-family variance is large on the half we measured, and the between-family variance has never been measured at all.** ⚠⚠ **One row per family — the obvious plan — would have published S1's answer as whichever of the two we happened to pick.** → `.tasks-php/QUOTA_001.md` turns that accident into the method: **an adaptive quota, minimum 2 per family, a family stays OPEN until a new row moves none of the six answers, cap 4.** Floor **40 rows ≈ 140 tasks**, and that price should be visible here rather than discovered at row 30. ⚠ **S1 is NOT settled and owes a third row — record the debt, do not pay it next.** ⚠⚠ **UNREVIEWED, and `TASK_PHP_019`/`_020` are attacking the family boundaries right now — re-derive it after they report, do not defend it** |
| 35 | ⚠⚠ **NOBODY HAS AUDITED THE 93 ROWS' `corpus rows` CELLS, AND `coverage.py` CANNOT SEE THE DEFECT** | `TASK_PHP_019` found **two** ids merged into the wrong surviving row (`CRASH-101` into `ph39` when `ph41`'s own block says *"Do not fold into ph39"*; `LOGIC-014` into `ph47` when `C.1`'s own sentence says `ph48` was **kept** for that mechanism). ⚠⚠ **The coverage checker proves every corpus id is SOMEWHERE; nothing checks it is in the RIGHT somewhere** — and that is by construction, not a bug. ⭐ This is the same shape as `TASK_PHP_012` M1 (*a checker that accepts the artefact it is checking*) on a different field. **It is the next audit after `_019`/`_020`, and it is mechanical: for each id, does the surviving row's mechanism match?** |
| 36 | ⚠⚠ **`ph07` CARRIES FOUR REFUTED FIGURES INSIDE ITS HASHED `why`, AND NO GATE CAN SEE THEM** — ▶ **`TASK_PHP_024`, written** | `TASK_PHP_022` M1/M2. **(a)** `spec.md`'s `identity[0].why` cites **255 instructions** and three hashes, **all pre-rebuild values the rebuild refuted** — ⚠ **the hash still matches**, because the text was never edited, **and `NOTES.md` claims the addendum pass covered it, which is a false disclosure.** `PROTOCOL.md` rule 6's documented hole, reproduced live on a row we are quoting. **(b)** `c/kernel.h:20-25` names **`d9dda48f8a7e`** as R1h while the file ships `cb3cca21b345` hunk (a) — ⚠ **and `spec.md`'s own `forbidden[2]` calls `d9dda48f8a7e` a *different function*.** It is inside `source_sha256` and predates the rebuild. **Both fixes cost a `ph07` re-gate**, plus the minors: `bug49354.py`'s *"shares no code with `fix_scope.py`"* is **false** (byte-identical table and clamps — conclusion still safe, three independent checks agree), `NOTES.md`'s rule-6 fence names 4 against 27 moved, §10d quotes a pre-rebuild log, and `spellings.py` **re-implements** `measure.py`'s statistic rather than importing it |
| 37 | ⚠⚠ **FOUR DEFECTS IN `harness-php/provenance.py`'s NEW `extra_spans`, all found AFTER I committed it** — ▶ **`TASK_PHP_024`, written** | `TASK_PHP_022`'s post-notification half. **(a)** ⚠⚠ **`provenance.py:836-837`'s disclosure *"adding a span cannot make the number go up for free"* is measurably FALSE.** Union overlap is `|hit|/|want|` over deduplicated sets, so **a span above the current fraction RAISES it** — measured on `ph07`'s own excerpts: primary alone **75 % (39/52)** → primary + the 100 % table span **77 % (44/57)**. `ph07` only lands at 61 % because span 2 happens to be 15 %. ✅ The set semantics *do* defend against citing the same span twice (measured: unchanged at 61 %) — **it is the general claim that fails.** **(b)** ⚠ **A `php_provenance: false` row short-circuits before any `extra_spans` validation**, so a wholly bogus extra span passes. **(c)** `gate.py:300` cites `provenance.py:841-843` for the dotted-row glob; the +60 lines moved it to **`:924`** — **citation rot introduced BY the change and not repaired.** **(d)** *"byte-identical"* holds for the **default invocation only**: under `--no-tarball`, `ph03` gains `for any of 1 span(s)` |
| 38 | ⚠ **`ext/sockets/sockets.c` HAS ZERO CATALOGUE ROWS, AND THE FIX COMMIT THAT NAMES IT WAS ALREADY ON FILE** — ▶ **`TASK_PHP_026`, written; dispatch AFTER `_023` lands** | F50, **manager, unreviewed, n = 1**. `ph16`'s `fix_commit` `99e290f882c9` patches **four** unchecked fd-set sites and the catalogue has **one**; the other three are `streamsfuncs.c:577` (`FD_ISSET`, a read) and `sockets.c:536,563`. ⚠⚠ **`FIXSURVEY_001.md:67-81` had already recorded the *10 files* — as a COST** (*"F34's inside-a-rewrite shape"*, *"right fix, big commit"*). **The channel: for each of the ~91 resolved rows, does its fix name siblings we never catalogued?** ⚠ **Expected to be a MINORITY** — the discriminator is the commit *message*, sweep vs rewrite — and *"the channel is dead"* is an outcome `_026` is told to report plainly. ⚠ **Does not reopen the bar**: every candidate still faces `PLAN_PHP.md` §3 on the C alone, and `sockets.c:536` looks `EXACT` against `ph16` under `_019`'s rule. ⚠⚠ **`:541` vs `:577` is a sharp test of that rule — one upstream fix, two fault primitives — so `_026` reads `_023`'s verdict first.** ⚠ First check whether `ext/sockets/` was in the **built configuration the ASan census ran**; if not, its zero rows are explained innocently and the finding is about the census's coverage |
| 39 | ⚠⚠ **`CATALOGUE.md` C.7's COVERAGE CLAIM RESTED ON GITIGNORED SCRATCH, AND ITS PASTED OUTPUT IS STALE** — ▶ **fix when `_023` releases the file** | F51. **(a)** ✅ **Done**: `.temp/php11/coverage.py` promoted to `.tasks-php/coverage.py`, `166/166` re-derived and confirmed, F49's two regex/gap defects repaired, and the corpus's **third namespace** (`merged_members` — `V5C-116` → `CRASH-115`) taught to the checker, which resolves the three *"ids the corpus does not have"* the catalogue had pasted in unexplained. **(b)** ⚠ **Still owed, in `CATALOGUE.md` itself**: C.7 cites `.temp/php11/coverage.py` and quotes **91 rows / 161 ids** against the file's **93 / 163**. Repoint at `.tasks-php/coverage.py` and refresh the block — ⚠ **after the landing, so it is refreshed once at 102.** **(c)** ⚠ **Nine more committed-claim citations into `.temp/`, two ALREADY GONE** (`patterns-php/SOURCES.md` ×4, `PLAN_PHP.md` ×3, `CATALOGUE.md` ×3, `.memory-php/00-corpus.md` ×1). `citecheck.py` now reports them as a **warning, not a failure** — they are evidence with a scheduled expiry, not broken pointers, and the fix is a committed generator per `CLAUDE.md` rule 1, not a whitelist. **(d)** ⚠ **`ph03` and `ph22`'s `corpus rows` cells cite merged-away ids** — legitimate, but F44 rates `merged_members` the WEAKEST evidence in C.1 and **these are the three merges C.1's kills rest on**; `TASK_PHP_019` reports the corpus's own validators flagged all three. **Not reopened here** |
| 40 | ⚠ **`ph98`'s TRIGGER HAS AN UNSTATED RESIDUE DEPENDENCE — F52's CLASS AT A THIRD SITE** | `TASK_PHP_023` §2.5.1. `zend_builtin_functions.c:1054` tests `Z_STRLEN_PP(exception_handler)==0` and for the trigger's `array($o,'m')` that reads `value.str.len` at offset 8 of a zval whose `_array_init` (`zend_API.c:644-651`) writes **only** `value.ht` (offset 0–7) and `type`. ⚠ **If the residue is 0 the handler is silently never stored and the trigger no-ops** — so the row's witness is allocator-dependent in exactly the way `ph94`'s was (F52), at a third site. ✅ **Not a kill and not a block**: the C-side mechanism is unaffected. **A build task on `ph98` must know this before it spends an hour on a trigger that sometimes does nothing.** ⚠ Additive, and `ph100` is *understated* the same way — `zend_execute_API.c:450 INIT_PZVAL(p)` clears `is_ref` and `:451` restores only `refcount`, so the binding breaks even where `SEPARATE_ZVAL` no-ops |
| 41 | ⚠ **`PROTOCOL_PHP.md` §G IS ONE REVIEWER'S RESTATEMENT AND THE MANAGER LANDED IT** | F53. `TASK_PHP_023` §4.3 attacked `TASK_PHP_019`'s duplication rule, measured its second disjunct false, and proposed a replacement; I landed it as `PROTOCOL_PHP.md` §G/§G1 **marked UNREVIEWED**. ⚠⚠ **This is the shape F48 warns about** — I have twice now taken one agent's construction into a standing document without a second pair of eyes, and the rule it replaces got there the same way. ✅ **The difference I am claiming**: the old rule was folklore in a report and is now in a document where it can be attacked, and it had a **measured** defect. ⚠ **If that reasoning is wrong, §G should come back out** — it is one paragraph. **Give it to the next reviewer whose task touches admission** |
| 42 | ⚠ **THE PREFLIGHT RECORD IS KEYED BY THE TYPED NAME, NOT THE RESOLVED ROW** | F55, **manager, unreviewed**. `harness-php/` resolves an abbreviated row through `glob(<row>*)` for the WORK and keys the record on **the string you typed**, so `provenance.py ph07` operates on `ph07-strcut-cursor` and writes its history elsewhere. **Measured**: `ph00.preflight.json` (`row: ph00`, **12 runs**) beside `ph00-smoke.preflight.json` (**1 run**), and `ph07.preflight.json` (**4**) beside `ph07-strcut-cursor.preflight.json` (**16**). ⚠⚠ **The `ph00` one is COMMITTED**, since `TASK_PHP_010`. ✅ **Nothing published rests on it** — the gate reads `results-php/gate/` and `--check-stale` is 6/0 either way; **what it costs is the audit trail**, silently split by how someone typed the name. ⚠ **The fix needs a control that types both spellings and asserts one file** — §H, so not a one-liner. ⚠ **Decide whether the committed `ph00.preflight.json` is deleted or kept as the record of the defect** |
| 43 | ⚠ **`ph00-smoke` IS NOW RETIRABLE AND NOBODY HAS RETIRED IT** | Its own `README.md` and `NOTES.md` say to delete it **once a real php row has gated green**; `ph03` and `ph07` both have. ⚠ It is a relocated PAT calibration kernel with **no PHP provenance** (`php_provenance: false`), it prices nothing, and it is **one of the 3 rows every `provenance.py --all` and every `--check-stale` bracket counts** — so the *6 records* and *3 rows checked* figures both include a fixture. ⚠⚠ **It is also the ONLY row the `php_provenance: false` path is exercised on** (item 42's sibling defect lives on that path), so retiring it removes the only live test of that branch. **Decide deliberately; do not just delete it** |
| 44 | ⚠⚠ **`vparse` TRUNCATES A VERUS CLAUSE AT THE FIRST `{`, AND THE GATE COMPARES THE PREFIX AND PASSES** | `TASK_PHP_025` §15.5. An `ensures` written with an `if … { … } else { … }` block expression derives as a **prefix** — the reporter's came out as `"r == if not_an_array"`. ⚠⚠ **Verus is unaffected** (it reads the source), **but the `spec.md` item pin under-describes the contract and the gate passes it** — a **false-PASS** shape, not a false-fail. ✅ Worked around in `ph16` by routing the conditional through two spec helpers, so no shipped clause contains a brace; **`harness/` untouched**. ⚠⚠⚠ **The fix is in `harness/vparse.py`, which is hashed into all 33 PAT gate records — a 33-pattern re-gate for a defect no built row currently trips.** Record it, price it, do not pay it on impulse. ⚠ Sibling, same report §15.6: **a `forbidden` entry bans every backticked span in its own PROSE** — documented in `check.py`, and `ph16` is the first row to *fire* on it (**14 refusals**), with the same mistake recurring inside the text that fixed it. **Write `forbidden` prose without backticks.** ⚠ And §15.7: **foreground `sleep` is blocked here, so an `until … sleep` poll loop returns INSTANTLY and reads exactly like a completed wait** — the third distinct shape of the poller hazard, after the `pgrep` self-match (four leaked loops killed 2026-09-09) and a waiter dying while its gate succeeded |
