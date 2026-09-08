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
STATE   ROWS BUILT 1 (ph03, reviewed) · CATALOGUED 91 · Phase 0 CLOSED.
        .memory-php/ EXISTS (00-corpus 01-extraction 02-ladder 03-numbers
        04-process) and is AUTHORITATIVE -- read it before any task report.
NEXT    TASK_PHP_016 RUNNING: build ph07 (mbfl_strcut). Review it next; then
        the batch ph21 -> ph16 -> ph12 -> ph29, pre-briefed in
        .tasks-php/UPSTREAM_001.md -- all 4 fixes already located (F36).
⚠ GREP  ALWAYS `grep -a` ON THE CORPUS. `grep` in a Bash call is a wrapper
        function -> ugrep: on string.c + 40 files it exits 1 with NO stdout
        and NO stderr = "absent". 13 rows cite one. rg, /usr/bin/grep and
        a script run by `sh` all SUCCEED, so a probe script lies. (F35)
ROW 1   ph03 gate PASS. PHP's real 2004 fix is BOTH DEAD AND INCOMPLETE --
        one hunk provably redundant, the other leaving 144 over-reads. (F29)
        Ladder (F33): naive +26.8% · tuned +3.7% · unsafe -7.6% · verus ==
        unsafe byte-identical · hardened C -0.4% (negative cost).
BAR     C-SIDE ONLY. Nothing about Rust/Verus/Miri/cost may kill a row.
        patterns-php/ is FRESH: duplication with patterns/ is NOT a filter.
⚠ OPS   .web/ is edited by a CONCURRENT SESSION -- NEVER `git add -A`.
        Commit with explicit paths or `git add -A -- . ':!.web'`.
READ    .memory-php/ · PLAN_PHP.md · .tasks/PROTOCOL.md (reused unchanged) ·
        CATALOGUE.md · then F1-F36 and the open items below.
```

---

## What is true now

| | |
|---|---|
| **rows built** | ⭐ **1 — `ph03-uudecode-bound`**, gate `PASS`, five rungs + R1h, R5 at 25/0. (`ph00-smoke` is a relocated PAT calibration kernel, throwaway, **no PHP provenance**, and prices nothing) |
| **tasks** | `_001` mining wave DONE · `_002` Phase 0 built · `_003` reviewed it · `_004` landed the fixes · `_005` reviewed **those** — **1 blocker open (F-1)**. `_006` = land `_005`'s corrections |
| **infrastructure** | **built and reviewed TWICE**: `harness-php/{root,gate,provenance}.py` · `common-php/` · `patterns-php/{SOURCES.md,php-5.0.0.manifest}` (1170 files, 109 KB) · `.tasks-php/PROTOCOL_PHP.md` · `results-php/`. ⚠ **Reviewed is not the same as correct — the second review found a blocker in the first review's own fix.** ⚠ There used to be a SECOND row in this table also labelled `infrastructure` saying *"not yet built — Phase 0"* (`TASK_PHP_003` m1); it is gone |
| **candidates** | **54** delivered across three axes. ⚠ **`.tasks-php/ADJUDICATION_001.md` takes that to ≈ 80**: +6 splits, −2 merges, **+17 kills reversed**, +1 dropped with no reason recorded, +4 that fell between axes. Evidence in `.tasks-php/TASK_PHP_001_MINE/` |
| **catalogue** | ✅ **`patterns-php/CATALOGUE.md` — 91 rows, UNREVIEWED.** Part A is a 113-line scannable table, Part B a 150-word block per row under 23 family headings, Part C the kill list with a re-derived criterion per kill. ⚠ **Size was measured, not argued: 1 304 B/row against `.memory/06-catalogue.md`'s 4 340 — 3.3× denser than the PAT catalogue that works.** Built from `.tasks-php/ADJUDICATION_001.md`, which it also reviews |
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
> batch's four fixes, and two of them DELETE the guard**

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

**Decisions:**
1. **`ph07` is built with R1h = the 5.4.0 clamp**, not as a hand-written control.
   ⚠ **The commit that introduced it is NOT yet identified** — bounded work for
   the build task — and `PROTOCOL_PHP.md` §F item 5's assumption that a
   `fix_commit` exists **survives**.
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
   The manager hit this while checking this very finding — `REFETCH.sh` printed
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

⚠ **And `ph29`'s catalogued mechanism is not yet verified.** The catalogue says
*"the allocator truncates n mod 2^32"*; `to_read` is a `long` and 5.0.0's
`emalloc` takes a `size_t`, which on this 64-bit box truncates nothing.
**Either the mechanism is 32-bit-only, or it is elsewhere, or the row is
mis-catalogued — a C-side question, so it can decide admission.** Settle it at
source before building.

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
| ~~10~~ | ✅ **CLOSED at `TASK_PHP_006` — `common-php/*.h` is in NO gate digest, and the `<row>/c/` symlink that was supposed to close the measurement half is BYPASSABLE** | `check.py`'s three `common/` globs are non-recursive and none matches `emalloc_shim.h`. The bridge half **fires** (F7). The symlink half was enforced by nothing (B1), was checked in `gate.py`'s preflight at `TASK_PHP_004` — and `TASK_PHP_005` **F-1** got round it twice, with rows that build, link and run a live allocator into neither digest. **`TASK_PHP_006` closes it** |
| 17 | ⚠ **PAT-SIDE, LATENT, DELIBERATELY NOT FIXED — and the php side now REFUSES the layout: `check.py:10314` and `measure.py:226` glob `<row>/c/*` NON-RECURSIVELY and drop the directory entry with `isfile()`** | so **every source file a row puts in a `c/` subdirectory is in no digest at all**, and `check.py`'s `--no-build` staleness scan misses it too, so editing one does not even mark a binary stale. ✅ **No row is affected today** — `find patterns patterns-php -mindepth 3 -maxdepth 3 -type d -path '*/c/*'` is empty. ⚠ **Fixing it is a `harness/` edit = a 33-pattern re-gate for zero present benefit.** Decision: **do not fix; FORBID the layout on the php side** (`TASK_PHP_006`), and carry this row so the next person to reach for `c/sub/` finds out first. ⚠ It matters more here than on PAT: php rows are *extracted* C and `c/zend/` is an ordinary thing to want |
| 11 | A new php row costs **six commands (~28 min)**, not three | `gate → report → gate` is irreducible and `measure.py` builds nothing. Budget it. ✅ The three places that said three/five now say six (`TASK_PHP_004`) |
| ~~12~~ | ✅ **CLOSED — `.memory-php/` EXISTS**: `00-corpus` `01-extraction` `02-ladder` `03-numbers` `04-process` | Open from the programme's first task to its sixteenth. It carries **only php-specific** findings that survived a full engineer→reviewer cycle; the PAT `.memory/` 00–06 applies unchanged and is **not** restated. ⚠ **It supersedes any task report it contradicts** (rule 9) |
| 13 | ⚠ **`harness-php/*.py` is in NO digest, and putting it in one costs a 33-pattern re-gate** | `check.py`'s `srcs` would have to reach `harness-php/`, i.e. a `harness/` edit (`PLAN_PHP.md` §2.1). `TASK_PHP_004` landed the **cheap half**: `gate.py` writes `results-php/preflight/<row>.preflight.json` with the `harness-php/*.py` hashes, the manifest hash and whether `--no-provenance` was used. ⚠ **That record is evidence, not a pin — nothing hashes it** — ⚠⚠ **and `TASK_PHP_005` F-2 found it is worse than that: it is written one file per ROW, not per run, so a later preflight ERASES `provenance_skipped: true`; nothing anywhere detects a missing record; and the manager had made it uncommitted.** Being fixed at `TASK_PHP_006` (item 18) |
| 14 | ⚠⚠ **`provenance.py`'s overlap floor is SATISFIED BY DEAD CODE — the risk is a false PASS, not a false refusal** | Added at `TASK_PHP_004` for `TASK_PHP_003` M5. ⚠ **This row used to say the danger was a good row tripping a floor. `TASK_PHP_005` F-4 shows the opposite**: a kernel that implements *division*, cites *multiplication*, and hides the citation behind `#if 0` scores **100 % and is ACCEPTED** (`_normalise` drops lines starting with `#`, so `#if 0`/`#endif` vanish and everything between them counts); the same kernel without the dead block is refused at 11 %. ✅ **The floor is not too high** — a realistic `verbatim` `mul_function` lift scores 68 %. ⚠ **The check never reads `main.c`, the driver loop or the build, so it measures presence of TEXT IN A FILE, not presence of code in the benchmark**: a pass is not even evidence that the cited lines are compiled |
| 16 | ⚠ **`TASK_PHP_004` edited `RECAP_PHP.md` — the manager's own handoff file** | `PROTOCOL.md` rule 4 reserves the state layer to the manager, and `TASK_PHP_004.md` did not forbid it explicitly. ✅ **The content is ACCEPTED — it is more accurate than what the manager was about to write** (the `+34` vs `+33` shell artefact, the `3686 → 3695` instability, items 13–15). ⚠ **But the boundary is real**: an engineer correcting the manager's numbers *in the manager's file* is how an unreviewed claim reaches the state layer without passing rule 9. **Future php task files must say explicitly that `RECAP_PHP.md` is manager-only** — the fix is one sentence in the task template, not a rollback of good work |
| ~~18~~ | ✅ **CLOSED at `TASK_PHP_006`. The record is COMMITTED (minus `when`), the per-row overwrite is fixed by appending, and an absence is now a preflight NOTE** | `.gitignore:24-26` justified it as *"carries a `when` timestamp and the literal `gate_argv`, so it churns"*. ⚠ **`TASK_PHP_005` F-2c measured it: only `when` moves.** `sha256(rest)` is identical across two runs (`d91ce008ad273b36`) and `gate_argv` is a function of the command, **which is exactly the evidence M6 wanted**. The split the manager asked the reviewer to price **exists and costs one field**. → `TASK_PHP_006` commits the record without `when` and fixes the per-row overwrite |
| ~~19~~ | ✅ **CLOSED: THERE IS NO SIZE RULE. The 200-word rule is withdrawn — it was calibrated on n = 1 and is broken by 30 of 33 PAT rows** | `TASK_PHP_005` F-5: up to **2 533** words, and **`p01` — the template every row clones, and the row `PROTOCOL_PHP.md` cites as complying — is 201.** The 200 was simply the measurement of the one row that had been measured. ⚠⚠ **This is the THIRD version of this rule and the second that could not be met**; `RECAP_PHP.md` itself warns that *"a size rule that cannot be met is worse than none"*. **The manager must not invent a fourth number** — `TASK_PHP_006` measures the corpus distribution and proposes a limit, or proposes a structural rule instead, **and whatever lands must be enforced by a check or dropped** |
| ~~20~~ | ✅ **CLOSED at `TASK_PHP_006`** (was: `gate.py <row> --preflight` silently forwarded the flag and ran the tool) | `argparse.REMAINDER` collects from the first positional (`TASK_PHP_005` F-7). ⚠⚠ **The manager's own 06:55 `ph00.preflight.json` — cited as manager-verified evidence for the gitignore decision — is an instance: a FAILED `check.py` launch (`tool_returncode 2`) recorded as a preflight.** Part of the evidence for a manager decision was an artefact of a CLI bug |
| 15 | ⚠ **The php staleness check is `gate.py --tool measure --check-stale`** and the mandated PAT `66/0` one does **not** examine `results-php/` at all | Both are now in `PROTOCOL_PHP.md` §E1 (`TASK_PHP_004`); today the php side is **2 records** |
| 21 | ⚠⚠ **`TASK_PHP_012` M4 — 12 rows declare `verbatim` whose defect site is inside a `PHP_FUNCTION` / VM-handler / arg-parsing frame, i.e. **`narrowed`** — and NONE has been corrected in `CATALOGUE.md`** | ✅ **Re-run and reproduced by the manager** (`.temp/mgr/batch/tier_recheck.log`): `ph05 ph11 ph12 ph21 ph22 ph24 ph35 ph50 ph55 ph59 ph76 ph80`. ⚠ **A cost statement, never a filter — no row's admission moves.** But `provenance.py` reports overlap **against the declared tier's expectation** (50 % / 25 %) and `TASK_PHP_008` made that a report rather than a floor, so **a mis-declared `verbatim` row hands its reviewer a scary number that is indistinguishable from a bad extraction.** `TASK_PHP_012` said *fix before the first row*; `ph03` was unaffected, **but `ph12` and `ph21` are in the NEXT BATCH.** ✅ **Landing is staged and mechanical**: `python3 .temp/mgr/land_m4.py --check\|--apply` edits Part A + Part B for all 12 and **refuses unless every row has exactly two occurrences** (dry-run: 24 edits, 2 each). **Blocked only by `PROTOCOL.md` rule 11** — `TASK_PHP_016` is reading `CATALOGUE.md`. **Land it the moment that task reports** |
| 22 | ⚠ **The rest of `TASK_PHP_012`'s catalogue corrections are still owed** — M1 (6 of 12 "merges" are silent drops), M2 (the four-`LOGIC` set kill), M3 (CRASH-021 reverses → a `ph60` merge, not a kill), M5 (CRASH-061/126 in the wrong family), and the minors m1/m5/m8 | Batch them with item 21's landing (`PROTOCOL.md` rule 6) — they are all `CATALOGUE.md` edits and share its rule-11 block. ⚠ **m8 and open item 4 point at the same place**: `CRASH-106`/`CRASH-109` killed as *exact* duplicates on a cost judgement `C.0` forbids, **the most likely place the spatial axis lost a real row** |
