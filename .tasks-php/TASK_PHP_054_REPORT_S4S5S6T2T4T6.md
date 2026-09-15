# TASK_PHP_054 — agent **C** report: **S4 · S5 · S6 · T2 · T4 · T6** (19 rows)

**Role:** research investigator, screening for **row 11**. **This is a ranked
shortlist with evidence, not a decision.** The manager picks.

**Scope reconciled, and the count printed** (§3.1's mandatory check):

```
S4: n=6  ph32 ph33 ph34 ph35 ph36 ph102
S5: n=1  ph37
S6: n=1  ph38
T2: n=5  ph47 ph48 ph99 ph100 ph101
T4: n=1  ph54
T6: n=5  ph59 ph60 ph96 ph97 ph98
MY ROW COUNT = 19          all Part B blocks = 102   grep -ac '^\*\*ph' = 102
```

✅ **Agrees with `python3 .tasks-php/quota.py` per family, row for row** (`S4 6 ·
S5 1 · S6 1 · T2 5 · T4 1 · T6 5`, all `OWES 2`). ✅ Agrees with the task file's
row list. **No row was dropped by a regex** (F35's class): the extractor walks
`### <fam> —` section boundaries and takes every line beginning `**ph`, and its
whole-file total is 102, which is `grep -ac '^\*\*ph'` and `quota.py`'s Part B
count.

**Every `file:line` below was read out of the pristine tarball**
(`sha256 5783e0c0…d6919`, re-verified this session). **Every patch was read from
the local cache — I made no network fetch.** Commands and the re-derivation
recipe: `.temp/php54C/NOTES.md`.

---

## §0 ⭐⭐⭐ HEADLINE — **THE CONTROL FIRES: P2 IS NOT SUPPORTED BY MY SET**

I am the control on **P2** (*"row 11 is a TEMPORAL row"*). ▶ **My set beats the
temporal candidates on every cost axis this programme has written down, and I
say so loudly.**

1. ⭐ **`T6` is the best family I screened and I believe it beats every `E`
   family**, on three grounds that are *measured*, not argued:
   - **Four of its five rows have a 1-file, same-file, one-id R1h from 2004–2005**,
     and **three of those are ONE LINE** (`ph97`, `ph59`) or **one hunk**
     (`ph96`). I read all five patches.
   - **Not one T6 row needs the allocator, a HashTable, the executor, stack
     garbage, a hash preimage or userland re-entry.** `PROTOCOL_PHP.md` §B1a
     says in terms: *"**Expect the [O(1)-allocation] precondition to fail on most
     `E*` rows**, so a row that satisfies it is the exception worth remarking
     on."* Every T6 row satisfies it trivially.
   - **T6 has 5 catalogued rows, so entering it can CLOSE the family** (2 of the
     30 owed), the way `ph55`+`ph56` closed T5.
2. ⭐ **The `ids → commits` load is structurally against the temporal axis, and
   `PROTOCOL_PHP.md` §C already measured it**: *"It applies to 30 of 102 rows
   and the load is NOT uniform — **21 of 31 temporal (68 %)**, 6 of 29 type,
   **3 of 42 spatial (7 %)**."* Every one of the 12 rows the task file listed as
   a multi-commit hazard in agents A and B's sets is temporal. **In my 19 rows
   only three carry >1 id** (`ph37`, `ph47`, `ph48`) and each resolves under §C
   in one sentence.
3. ⚠ **P2's own grounds are weakened by a gap in the evidence it rests on.**
   P2 says *"3 of the 5 best shapes are temporal"* — but those five came from
   `FIXSURVEY_001.md`'s per-row table, **which was built at 91 rows and contains
   none of `ph96`–`ph102`.** I ran `fixsurvey.py --offline` myself (§1.1): **`ph96`
   (`cf020f133487`, 2005-03-19, 1f, same-file) and `ph97` (`f7326d627962`,
   2005-01-28, 1f, same-file) have exactly the shape P2's ranking scored best
   on, and were invisible to it.** So does **`ph102`** (`46bc2c5ae2ae`,
   **2004-07-19**, 2f, same-file) — the **earliest fix date of any row in my
   set**. ▶ **The five "best mechanical picks" are a ranking over 91 of 102
   rows, and three of the missing eleven would have entered it.**

⛔ **What I am NOT claiming.** I did not read the `E` families — agents A and B
did. I am comparing my measured rows against the *stated, measured* cost
properties of the temporal axis in `PROTOCOL_PHP.md` §B1a and §C, not against
A's and B's findings, which I have not seen. **If A or B returns a temporal row
with a one-line 2004 R1h and no allocator, my refutation of P2 weakens to
"T6 ties" and the manager should say so.**

---

## §1 STAGE 1 — every row, from its own Part B entry

Legend for `needs` (§3.1's cost column; a tick means the kernel cannot omit it):
`zval` = a tagged value with a type byte / `alloc` = the allocator (with order)
/ `HT` = HashTable / `VM` = the executor / `user` = userland re-entry /
`stack` = stack garbage / `pre` = a hash preimage or other precomputation /
`fail` = failure injection / `2sys` = more than one subsystem.

### S4 — declared extent ≠ realised extent (6)

| row | tier | defect site | harm | needs | determ? | observable by | R1h (year · files · same? · ids→commits · screen) |
|---|---|---|---|---|---|---|---|
| **ph102** | verbatim | `ext/standard/html.c:155`, `:401`, `:900` | **silent wrong answer** (8 code points decode one low) **AND** OOB read `table[66]` of 66 | **— none** | ✅✅ all `static const`; no stack, no heap, no uninit | checksum divergence (layout-**independent**) + ASan global-buffer-overflow | `46bc2c5ae2ae` · **2004-07-19** · 2f · same · 1→1 · CANDIDATE |
| **ph35** | narrowed | `ext/pcre/php_pcre.c:448-449` | **OOB WRITE of a pointer** past `safe_emalloc(num_subpats, sizeof(char*))` | `alloc` **O(1)** | ✅ index is a pure function of the blob's name-table bytes | ASan heap-buffer-overflow + allocator ledger | `ae57857ebac7` · 2009-04-10 · 2f · same · 1→1 · CANDIDATE ⚠ **partial fix** |
| **ph34** | narrowed | `ext/ctype/ctype.c:99-100` | **silent wrong answer** from an OOB read of libc's `__ctype_b` | `2sys` (the host libc *is* the table) | ⛔ the **value** depends on the process image | checksum divergence; **not** ASan (libc is uninstrumented) | `9daaedc12526` · 2005-09-26 · 2f · same · 1→1 · CANDIDATE ⚠ 35-line macro rewrite |
| **ph32** | verbatim | `ext/standard/html.c:398`, `:401`, `:896`, `:900` | same pair of harms as ph102, ×3 tables | **— none** | ✅ | checksum + ASan | `bd2e99ee50ed` · 2005-05-11 · 1f · same · 1→1 · **INAPPLICABLE-SAME-FILE** ⛔ the row's real R1h is **4 commits** |
| **ph33** | verbatim | `ext/mbstring/php_mbregex.c:624`, `:663-667` | OOB read of a 2-byte **stack** buffer → `xmemcpy` past it | `2sys` (oniguruma's parser owns the `end` pointer) | ⚠ partly — the copied bytes are stack residue | ASan stack-buffer-overflow | `b7259b71b430` · **2016-09-04** · 3f · same · 1→1 · CANDIDATE |
| **ph36** | narrowed | `Zend/zend_language_parser.c:3518`, `:3534` | OOB read of `yycheck` → wrong "expecting…" list | `pre` (a bison state/`yypact` table + a reachable state) | ✅ | ASan global-buffer-overflow | ⛔⛔ **NO SHA** — `(bison-regeneration; no single commit)`, the **only** such row in all 102 |

**`⚠ risk` lines, quoted (§3.1's last column):**

- **ph102** — *"⚠ risk: **R1h is `35e43dabe16b` (PHP-5.0) / `46bc2c5ae2ae` (HEAD), 2004-07-19, bug #29199** — it inserts the missing `NULL` **and adds the `/* 8216 */` and `/* 8242 */` markers that were absent**, which is the row's whole point: the scaffolding that would have made the miscount visible was not there. ⚠ **Do not merge into ph32**… ⚠ Before the OOB read at `k = 8260`, the whole tail from U+2020 up **decodes to the wrong code point** — a silent correctness defect the corpus's `global-buffer-overflow` label does not name."*
- **ph35** — *"⚠ risk: PCRE's *matcher* is not needed; only the name table and this loop. An extraction that drags in `pcre_exec` has built a different, unbuildable row."*
- **ph34** — *"⚠ risk: whether this over-reads at all depends on the **host libc's** table layout, not on PHP. State the libc and the measured table bounds, or the row is unreproducible."*
- **ph32** — *"⚠⚠ risk: **the corpus records ONE short table for this row; there are THREE.**"* … *"⚠⚠⚠ **THE THREE TABLES DO NOT SHARE A FIX, AND AN EARLIER VERSION OF THIS BLOCK SAID THEY DID.**"* … *"⚠⚠ **R1h, AND IT IS FOUR COMMITS, NOT TWO.**"*
- **ph33** — *"⚠ risk: a **declared** length (from the lead byte's table entry) against a **realised** extent (2 bytes) — ph32/ph53's family, stack-side. The `FIXME: this code is not multibyte aware!` comment at `:661` is upstream's own admission."*
- **ph36** — *"⚠ risk: killed as *"the generator owns the table"*. The tables are **bytes of the pristine tarball**, in `php-5.0.0.manifest`, and lift verbatim; only the loop is `narrowed`. Provenance is not one of the four criteria."*

### S5 — two passes compute one index differently (1)

| row | tier | defect site | harm | needs | determ? | observable by | R1h |
|---|---|---|---|---|---|---|---|
| **ph37** | narrowed | `ext/standard/scanf.c:383` (validate) / `:734` (execute) | **OOB read of a `zval**` + a WRITE through it** (`:893`, `:1101`) | `alloc` **O(1)** | ✅ for the read; ⛔ the write **target** is heap residue | ASan heap-buffer-overflow | `7d109bc62761` · 2006-08-04 · **1f** · same · **2 ids → 2 commits** · CANDIDATE |

*"⚠ risk: the kill said *"modelling zvals faithfully"* is required. It is not —
`args` is an array of **pointers**; `struct { int len; char *p; }` preserves the
defect exactly."*

### S6 — an in-place write through an aliased operand (1)

| row | tier | defect site | harm | needs | determ? | observable by | R1h |
|---|---|---|---|---|---|---|---|
| **ph38** | narrowed | `ext/standard/array.c:1572` (GUARD `:1537`) | **write through a pointer into a shared READ-ONLY literal** → SIGSEGV | **— none** | ✅✅ **no uninitialised memory anywhere** | **SIGSEGV** (measured, §2.3) + checksum divergence + Miri | `ff1687731dee` · 2005-02-18 · 2f (**ONE line of `.c`** + a new `.phpt`) · same · 1→1 · CANDIDATE |

*"⚠ risk: routed away by the spatial miner as *"a value-model property, not a
spatial one"*, and never picked up by anyone. The **write to a shared read-only
object** is spatial; the aliasing is the *reason*, not the class. If the
extraction gives each operand its own buffer, the row evaporates — the shared
literal must be modelled."*

### T2 — a type-changing write through a value that was not separated (5)

| row | tier | defect site | harm | needs | determ? | observable by | R1h |
|---|---|---|---|---|---|---|---|
| **ph47** | narrowed | `Zend/zend.h:568-571` + `ext/standard/string.c:1935-1949`, `:2077` | **type confusion → wild `memcpy`** (`:2116-2126`) | `zval`, `HT` (array path only), `alloc` O(1) | ✅ | ASan + checksum | `cd32b4e2bb54` · 2007-08-05 · 3f (**ONE line of `.c`**) · same · **2 ids → 2 commits** · CANDIDATE |
| **ph99** | narrowed | `Zend/zend_object_handlers.c:296-300`, `:311` + `zend_execute.c:1266`, `:1277-1281` | **silent wrong answer** — the class default itself is incremented | `zval`, `VM`, `user` | ✅ | checksum | `33a1a4d39ae3` · 2006-07-21 · 3f · same · 1→1 · CANDIDATE |
| **ph100** | narrowed | `zend_object_handlers.c:797` + `zend_execute_API.c:430`, `:458` + `zend.h:554-566` | **silent wrong answer** — a deliberate reference set torn apart by a READ | `zval`, `HT`, `VM` | ✅ | checksum of `(value, is_ref, refcount)` | `248345d9208a` · 2005-09-01 · **10f** · same · `fixed-by-rewrite` · 1→1 · CANDIDATE |
| **ph101** | narrowed | `Zend/zend_compile.c:1899-1900` (+`:1967-1971`) | **silent wrong answer** — a child's declared default destroyed; two slots aliased | `zval`, **`HT` with a value destructor** | ✅ | checksum of `(value, identity)` | `0455ccb80552` · 2008-03-03 · 6f · same · 1→1 · ⛔ **NOT-THE-REPAIR (decisive)** |
| **ph48** | narrowed | `Zend/zend_execute_API.c:608-610` | **silent CoW break** — `is_ref` stamped on a caller's by-value slot | `zval` | ✅ | checksum of `(is_ref, refcount)` | `af05ce0af6d3` · 2008-07-26 · **17f** · same · `fixed-by-rewrite` · **2 ids → 2 commits** · CANDIDATE |

**`⚠ risk` lines, quoted:**

- **ph47** — *"⚠ risk: no refcounting GC is needed — a boolean `shared` bit reproduces it. Importing refcounts adds a second mechanism (ph69/ph70) to a row that is not about them."*
- **ph99** — *"⚠ risk: **a boolean `shared` bit is enough** — importing refcounts adds ph69/ph70's mechanism to a row that is not about them (ph47's rule). ⭐ **And the blast radius is larger than the trigger says**…"*
- **ph100** — *"⚠ risk: **the constant-resolution step is the trigger, not the mechanism** — model it as one bit, not as a constant table. `crashes_pristine_5_0_0` is `n/a` (non-crash class)…"*
- **ph101** — *"⚠ risk: ⚠ **cite `:1899-1900`, the primary site.** `TASK_PHP_012` M2 priced `:1967-1971` (the helper) and reached the right verdict from the wrong frame. … ⚠⚠ **`zend_hash_update`'s destroy-then-replace is load-bearing** — a dictionary without a value destructor deletes half the mechanism."*
- **ph48** — *"⚠ risk: `crashes_pristine_5_0_0 = n/a (non-crash class)` — the harm is a silently broken CoW separation, visible in the checksum, not in a sanitizer. Fold `(is_ref, refcount)` into the `u64` or the row measures nothing."*

### T4 — the guard is at the wrong depth (1)

| row | tier | defect site | harm | needs | determ? | observable by | R1h |
|---|---|---|---|---|---|---|---|
| **ph54** | narrowed | `Zend/zend_execute.c:3831-3832` (FAULT `:3850-3853`) | **NULL deref** | `fail` (a callback that can fail) — *iterators and exceptions are scenery* | ✅ | NULL deref / SIGSEGV | `fc96c7f7fa18` · 2005-02-07 · 5f · ⚠ **OTHER-FILE** · 1→1 · **INAPPLICABLE** ⛔ **and it is not the repair — §2.5** |

*"⚠ risk: only a two-level out-parameter and a callback that can fail are needed.
Iterators and exceptions are scenery."*

### T6 — a fallible call whose failure is not tested (5)

| row | tier | defect site | harm | needs | determ? | observable by | R1h |
|---|---|---|---|---|---|---|---|
| **ph97** | narrowed | `ext/mbstring/mbstring.c:3211`, `:3215`, `:3219` | **NULL deref** — the caller's own NULL into libc `strcasecmp` | **— none** | ✅ | SIGSEGV | `f7326d627962` · 2005-01-28 · **1f, 1 hunk, ONE LINE** · same · 1→1 · CANDIDATE |
| **ph60** | verbatim | `ext/standard/ftp_fopen_wrapper.c:649-652` | **NULL deref** | **— none** | ✅ | SIGSEGV | `60fc9c050a44` · **2004-08-16** · **1f, 2 hunks** · same · 1→1 · CANDIDATE |
| **ph96** | narrowed | `zend_object_handlers.c:509`, `:512-513` + `zend_execute_API.c:592-595` | **NULL deref** in `_zval_ptr_dtor` | `fail` (two *independent* flags) | ✅ | NULL deref | `cf020f133487` · 2005-03-19 · **1f, 1 hunk** · same · 1→1 · CANDIDATE |
| **ph59** | narrowed | `ext/standard/array.c:4085` (consumer `:4096`) | a **NULL zval enters the value graph** | `fail` | ✅ | NULL deref | `f046cdf3fa15` · 2005-12-27 · 3f (**ONE line of `.c`**) · same · 1→1 · CANDIDATE |
| **ph98** | narrowed | `Zend/zend.c:1074-1075`, `:1078`, `:1083` | **NULL deref** in `zend_exception_error` | `fail`, `user`, `2sys` (the callable machinery is what makes the call fail) | ✅ | NULL deref | `79ed194a64a9` · 2007-03-15 · 3f · same · 1→1 · CANDIDATE |

**`⚠ risk` lines, quoted:**

- **ph97** — *"⚠ risk: `zend_parse_parameters` must be **modelled with an optional spec**, not stubbed to always-write — the optionality is the defect."*
- **ph60** — *"⚠⚠ risk: ⚠⚠ **THE THREE MERGES ARE GONE — `CRASH-061` → `ph96`, `CRASH-126` → `ph97`, `CRASH-163` → `ph98`** … ⚠ The wave killed all four as *"ordinary null-deref"*: that is a **quality** judgement, which the bar does not carry."*
- **ph96** — *"⚠ risk: **the two flags must be independent in the blob** — a kernel that derives `wrote_out` from `status` has deleted the mechanism and rebuilt ph60."*
- **ph59** — *"⚠ risk: killed as *"a precedence typo, not a type mechanism"*. **Mechanism *quality* is not one of `PLAN_PHP.md` §3's four criteria**; mechanism *distinctness* is…"*
- **ph98** — *"⚠ risk: **the row is the save/clear/restore triple, not the null-deref** — a kernel that only omits a NULL check has rebuilt ph60."*

### §1.1 ⚠ `ph96`–`ph102` in `fixsurvey.py --offline` — **IT DOES SAY SOMETHING**

The task file flags that `ph96`–`ph102` are absent from `FIXSURVEY_001.md`'s
per-row table. **I ran the tool myself and they are NOT missing from the tool —
only from that document's frozen table.** They are in
`.temp/mgr/batch/fixsurvey.json`, which the run rewrites; they do not appear in
the *printed summary* only because the summary prints three filtered
populations (fat rows, other-file rows, ≥5-file fixes) and six of the seven
qualify for none of them. Read out of the JSON + the cached patches:

```
ph96  CRASH-061  cf020f133487  2005-03-19   1f  same-file   - Fix #31185
ph97  CRASH-126  f7326d627962  2005-01-28   1f  same-file   MFB: fix #31732
ph98  CRASH-163  79ed194a64a9  2007-03-15   3f  same-file   fix #40815 (using strings like "class::func" …)
ph99  LOGIC-003  33a1a4d39ae3  2006-07-21   3f  same-file   Changed error message (E_ERROR -> E_NOTICE) …
ph100 LOGIC-008  248345d9208a  2005-09-01  10f  same-file   Support for class constants and static members …
ph101 LOGIC-018  0455ccb80552  2008-03-03   6f  same-file   Remove inconsistent behaviour when a protected static prop …
ph102 CRASH-090  46bc2c5ae2ae  2004-07-19   2f  same-file   - Fix bug #29199 (html_entity_decode() misbehaves with UTF-8)
```

`ph100` **does** appear in the printed summary, in the `≥ 5 files` list — so the
count in that heading is now 23, not 12. ▶ **`FIXSURVEY_001.md`'s per-row table
should be regenerated at 102 rows**; two of its own summary numbers (the 91-row
header and the 12-file list) are already superseded by its successor block, and
this is a third.

### §1.2 ⛔⛔ A STRUCTURAL FACT ABOUT THREE OF MY SIX FAMILIES — from `quota.py`, not from me

`quota.py` prints `n` (catalogued rows) and `OWES 2` (built rows needed) per
family. For **S5, S6 and T4, `n = 1`.**

> ⛔ **Building the single catalogued row in `S5`, `S6` or `T4` leaves that
> family at 1 of 2 with NO second candidate in the catalogue. The min-2 floor is
> arithmetically unreachable for those three families as the catalogue stands.**

⚠⚠ **This is NOT a down-rank of `ph37`, `ph38` or `ph54`.** Admission is C-side
and all three pass; `ph38` is the single cheapest *row* I screened. It is a fact
about the **programme arithmetic** that the manager is entitled to weigh against
the *"13 unentered families"* framing in the START HERE box: entering `S5`/`S6`/
`T4` pays the first-in-family premium (`RECAP_PHP.md` prices `ph64`'s at ~4.00
tasks, n = 1) and buys a family that can never close without new mining.
`S4` (6), `T2` (5) and `T6` (5) can all close.

---

## §2 STAGE 2 — deep verification, one per family (+2)

Seven rows deep-verified. **Every cited line below is quoted from the pristine
tarball, not summarised.**

### 2.1 S4 top candidate — **`ph102`** ✅ clean

**a) Citations, quoted from `php-5.0.0/ext/standard/html.c`:**

```
 155  static entity_table_t ent_uni_punct[] = {
 160  	"lsquo", "rsquo", "sbquo", NULL, "ldquo", "rdquo", "bdquo",
 161  	"dagger", "Dagger",	"bull", NULL, NULL, NULL, "hellip",
 401  	{ cs_utf_8, 		8194, 8260, ent_uni_punct },
 890  	if (all) {
 896  		for (k = entity_map[j].basechar; k <= entity_map[j].endchar; k++) {
 900  			if (entity_map[j].table[k - entity_map[j].basechar] == NULL)
1219  	replaced = php_unescape_html_entities(str, str_len, &len, 1, quote_style, hint_charset TSRMLS_CC);
```

All exact. `:401` declares `8260 − 8194 + 1 = 67` slots; the literal at
`:155-166` has **66** — re-measured independently on the file I extracted
myself, with `.temp/mgr165/count_ent.py` (comment-aware): **`17 tables · 4
short · 0 UNEVALUATED`**, `ent_uni_punct has 66 … declares 67 SHORT by 1`.
The missing element is the `NULL` placeholder for U+201F, immediately before
`"dagger"` at `:161` — exactly as the block says.

**b) `▸ trigger` — (i) VERIFIED.** `html_entity_decode('&frasl;', ENT_QUOTES,
'UTF-8')`. Chain read end to end: `:1219` passes `all = 1` **unconditionally**,
so `:890 if (all)` is always taken; `:886 if (!retlen) goto empty_source;` is the
only escape and any non-empty string clears it; `:896`'s `k <= endchar` is
inclusive so `k` reaches 8260 and `:900` indexes `table[66]` of a 66-element
literal. The `&frasl;` in the input makes the **silent** half observable: `frasl`
sits at index 65, so it is emitted for `k = 8259` (U+2043) instead of U+2044.

**c) The R1h, read as bytes.** `preimage_screen.py --row ph102 --verbose` →
**`CANDIDATE`** (1 record). ⚠ `CANDIDATE` means only *"could not exclude"* and
**is not a proof of anything** — I am citing it with that qualification and no
other. `1 id → 1 commit`.
**What `46bc2c5ae2ae` actually changes, in one sentence:** in
`ext/standard/html.c` it inserts a single `NULL` after `"bdquo"` and adds the
`/* 8216 */` and `/* 8242 */` run markers (plus a **count-neutral** re-wrap of
the `/* 8242 */` run: one `NULL` moves up a line, 18 in and 18 out), taking the
literal from 66 to 67; the only other file is a new `bug29199.phpt`.
✅ **This confirms the block's own claim at the patch bytes**, including *"adds
the markers that were absent"*.

**d) Census?** The patch touches **2 sites** in `html.c`: the table hunk and a
**whitespace-only** hunk at `:899-901` that deletes two trailing-blank lines.
**No sibling defect is repaired, and — decisively — it does not touch
`ent_uni_338_402`, `ent_uni_spacing` or `ent_uni_8592_9002`.** That is ph32's
*"do not merge"* verified from the bytes rather than from prose.

⚠ **One honest caveat on framing, not on admission.** `46bc2c5ae2ae` is dated
**2004-07-19**, six days after the 5.0.0 release. **PHP shipped this defect for
about one point release**, so the row is a poor specimen for a *"how long did
PHP ship it"* headline — though it is an excellent one for *"the scaffolding
that would have made the miscount visible was not there"*, which is the row's
actual claim.

### 2.2 S5 — **`ph37`** ⛔ **its `▸ trigger` is WRONG**, and I supply the corrected one

**a) Citations, quoted from `php-5.0.0/ext/standard/scanf.c`:**

```
 383  			objIndex = value - 1;
 384  			if ((objIndex < 0) || (numVars && (objIndex >= numVars))) {
 385  				goto badIndex;
 734  				objIndex = varStart + value;
 893  						current = args[objIndex++];
1101  							current = args[objIndex++];
1102  							convert_to_long( *current );
1103  							Z_LVAL(**current) = value;
```

All exact. `:565 badIndex:` returns `SCAN_ERROR_INVALID_FORMAT`; `:631-633`
makes `php_sscanf_internal` return on it. And `ext/standard/string.c:4536`
passes `varStart = 2`, with `args = safe_emalloc(argc, sizeof(zval **), 0)` at
`:4524`, so the valid index range is `0 .. argc−1 = 0 .. 1+numVars`.

**b) `▸ trigger` — (iii) WRONG.** The block says
*"`sscanf($s, '%2$d', $a)` with a positional index the second formula maps out
of range"*. **With one variable, `numVars = 1` and `value = 2`, so the VALIDATE
pass computes `objIndex = 1` and `numVars && (1 >= 1)` is true → `goto badIndex`
→ `ValidateFormat` returns `SCAN_ERROR_INVALID_FORMAT` at `:631` and the
function returns at `:633`. The defect at `:734` is never reached.**

> ▶ **Working trigger, derived from the C and then confirmed by the upstream
> fix: `sscanf($str, '%1$d', $a)`** — generally `%N$` with **`N == numVars`**,
> the largest index the validator accepts. Then `objIndex = varStart + value =
> 2 + numVars = argCount`, one past the end. ✅ `PHP_FE(sscanf,
> third_and_rest_force_ref)` (`basic_functions.c:297`) makes the `PZVAL_IS_REF`
> loop at `:642-648` pass, so nothing else blocks the path.

**c) The R1h.** `preimage_screen.py --row ph37 --verbose` → **2 records, both
`CANDIDATE`** (again: *could not exclude*, nothing more). **`2 ids → 2 distinct
commits`** — `CRASH-018 → 7d109bc62761` (2006-08-04, `scanf.c`) and
`CRASH-019 → 08841bf79c8f` (**2024-08-25**, *"Fix GH-15552: Signed integer
overflow in ext/standard/scanf.c"*). Under §C the R1h is `7d109bc62761`, the id
whose `c_file_line` the kernel extracts; **the manager should register that
decision before dispatch**, because the task file's one-id line did not flag
this row as multi-commit.
**What `7d109bc62761` actually changes:** it corrects the execute pass's formula
to `objIndex = varStart + value - 1` — **restoring the `- 1` the validate pass
has** — and adds `numVars && objIndex >= argCount` as an early `break` at every
consumer.

**d) ⭐ Census: YES, and it is the strongest in my set.** One file, and the guard
is added at **six** sites (`'n'`, two `%s` arms, the unsigned-int arm, the signed
arm, the double arm). The formula fix is the seventh hunk. **This is F50/F58's
channel: the commit is a census of its own defect's consumers, free to a build
task.**

### 2.3 S6 — **`ph38`** ✅ clean, and the **cheapest R1h in my set**

**a) Citations, quoted from `php-5.0.0/ext/standard/array.c`:**

```
1537  	if (Z_TYPE_P(zlow) == IS_STRING && Z_TYPE_P(zhigh) == IS_STRING) {
1553  		low = (unsigned char *)Z_STRVAL_P(zlow);
1567  		} else if (*high > *low) {	/* Positive Steps */
1572  			for (; *low <= *high; (*low) += (unsigned int)lstep) {
1573  				add_next_index_stringl(return_value, low, 1, 1);
```

Exact. And the operand's buffer, quoted from `php-5.0.0/Zend/zend_variables.c`:

```
  29  ZEND_API char *empty_string = "";	/* in order to save emalloc() and efree() time for
```

— a **string literal**, i.e. `.rodata`.

**b) `▸ trigger` — (i) VERIFIED, and upstream's own regression test is the
oracle.** `range("", "z")`: `is_numeric_string("")` is 0 so neither `goto` at
`:1545`/`:1547` is taken; `convert_to_string` on an already-`IS_STRING` zval is a
no-op; `*low = '\0' = 0`, `*high = 'z' = 122`, so `:1567`'s positive-step arm
runs and `:1572` writes into `empty_string[0]`. The fix ships
`ext/standard/tests/array/bug32021.phpt` — *"Bug #32021 (Crash caused by
range('', 'z'))"*, expecting `array(1) { [0]=> int(0) }` and the literal string
`ALIVE`, i.e. upstream's own liveness assertion.

⭐ **Measured on this box** (`.temp/php54C/probe_emptystr.c`, gcc 13.3.0, `-O0`,
x86-64): the literal lands in `.rodata` (`objdump -h`), and performing exactly
ph38's write — `(*low) += 1` through `char *empty_string = "";` — **SIGSEGVs**
(exit 139). So the harm primitive is an immediate, deterministic fault with
**no** stack garbage, **no** allocator and **no** sanitizer required.

**c) The R1h.** `preimage_screen.py --row ph38` → **`CANDIDATE`**, `1 id → 1
commit`. **What `ff1687731dee` actually changes:** exactly one line at the
GUARD site the block names — `if (Z_TYPE_P(zlow) == IS_STRING && Z_TYPE_P(zhigh)
== IS_STRING` → `… && Z_STRLEN_P(zlow) >= 1 && Z_STRLEN_P(zhigh) >= 1)` — plus a
new `.phpt`. **Benign behaviour for non-empty operands is bit-identical**, which
is `check.py` stage 7h satisfied by construction (contrast `ph07`, `PROTOCOL_PHP`
§C).

**d) Census?** **No.** One hunk, one site. Clean negative.

⭐ **A LADDER FINDING, NOT A KILL** (`CLAUDE.md` rule 6): in safe Rust the shared
literal is `&'static str` and **the write cannot be written at all**, so R2/R3
must model the sharing with interior mutability or an index. *"Safe Rust can't
express it"* is a **FINDING** and, on this row, an unusually sharp one — the row
would publish a rung the language refuses to spell. **Do not read this as a
down-rank; I am flagging it so the build task is not surprised.**

### 2.4 T2 top candidate — **`ph47`** ⚠ mechanism confirmed, **trigger wrong as written**

**a) Citations, quoted:**

```
Zend/zend.h
 554  #define SEPARATE_ZVAL(ppzv)									\
 558  		if (orig_ptr->refcount>1) {							\
 568  #define SEPARATE_ZVAL_IF_NOT_REF(ppzv)		\
 569  	if (!PZVAL_IS_REF(*ppzv)) {				\
 570  		SEPARATE_ZVAL(ppzv);				\
 571  	}
Zend/zend_operators.h
 210  #define convert_to_ex_master(ppzv, lower_type, upper_type)	\
 211  	if ((*ppzv)->type!=IS_##upper_type) {					\
 212  		SEPARATE_ZVAL_IF_NOT_REF(ppzv);						\
 213  		convert_to_##lower_type(*ppzv);						\
 214  	}
ext/standard/string.c
1942  		convert_to_long_ex(from);
1947  			convert_to_long_ex(len);
2044  			convert_to_string_ex(tmp_str);
2077  					convert_to_long_ex(tmp_len);
2116  					memcpy(result, Z_STRVAL_PP(tmp_str), f);
2117  					memcpy((result + f), Z_STRVAL_PP(tmp_str) + f + l, Z_STRLEN_PP(tmp_str) - f - l);
```

All exact, including `zend.h:568-571`'s *"a no-op exactly when `is_ref == 1`"*.

**b) `▸ trigger` — (iii) WRONG as written.** The block says
*"`substr_replace($s, $r, $lenRef)` with `$lenRef` a reference to an array
element that also feeds the length"*. **That call has `argc == 3`, and `len` is
only read under `if (argc > 3)` at `:1945` and `:2075`** — with three arguments
`zend_get_parameters_ex` never writes `len` and the cited `:2077` is
unreachable. Two working triggers, both traced in the C:

> **(1) the `is_ref` path the block describes** —
> `$s = "abc"; $r = &$s; substr_replace($s, "X", 0, $r);`. `str` and `len` are
> the same zval with `is_ref == 1`, so `:1947 convert_to_long_ex(len)` finds
> `type != IS_LONG`, `SEPARATE_ZVAL_IF_NOT_REF` **no-ops on `is_ref`**, and
> `convert_to_long` retypes the STRING to LONG in place and frees its buffer;
> the code then reads `Z_STRVAL_PP(str)` — now the `lval` bytes — as a `char *`.
>
> **(2) upstream's own reproducer**, from `bug42208.phpt`:
> `$a = array(1, 2); $c = $a; substr_replace($a, 1, 1, $c);`. Here the two
> parameters share **one HashTable**; `:2044 convert_to_string_ex(tmp_str)`
> retypes an element to STRING in place and `:2077 convert_to_long_ex(tmp_len)`
> retypes **the same element** back to LONG, after which `:2116-2117` reads
> `Z_STRVAL_PP(tmp_str)`/`Z_STRLEN_PP(tmp_str)` out of an `IS_LONG` zval →
> a wild `memcpy` source and a garbage length.

**c) The R1h.** `preimage_screen.py --row ph47 --verbose` → **2 records, both
`CANDIDATE`**. **`2 ids → 2 distinct commits`**: `CRASH-104 → cd32b4e2bb54`
(2007-08-05, `string.c`) and `CRASH-058 → d6ba6c69fb30` (2009-08-18,
`Zend/zend_execute_API.c`, 5 files). Under §C the R1h is `cd32b4e2bb54`;
**register the decision.**
**What `cd32b4e2bb54` actually changes:** it inserts **one line**,
`SEPARATE_ZVAL(len);`, immediately before the `if (argc > 3)` conversion block
— i.e. it separates the **outer** parameter, whose `refcount > 1` is the thing
nobody tested. Plus `NEWS` and `bug42208.phpt`.

**d) Census?** **No.** One hunk, one site.

⚠ **A qualification on the block's risk line, which I checked and which SURVIVES.**
*"no refcounting GC is needed — a boolean `shared` bit reproduces it"* is right:
the fix's predicate is `refcount > 1`, and a boolean *"this value has more than
one holder"* bit is exactly that distinction. ⚠ What does **not** survive is the
implication that `is_ref == 1` is the only no-op mode — `SEPARATE_ZVAL`'s own
`refcount > 1` test is a second one, and it is the one upstream repaired.
**A kernel must model both or it reproduces half the row.**

### 2.5 T4 — **`ph54`** ⛔⛔ mechanism is the prettiest in my set; **the recorded R1h is not the repair**

**a) Citations, quoted:**

```
Zend/zend_execute.c
3831  			iter->funcs->get_current_data(iter, &value TSRMLS_CC);
3832  			if (!value) {
3850  		SEPARATE_ZVAL_IF_NOT_REF(value);
3851  		(*value)->is_ref = 1;
3853  	(*value)->refcount++;
Zend/zend_iterators.h
  39  	void (*get_current_data)(zend_object_iterator *iter, zval ***data TSRMLS_DC);
Zend/zend_interfaces.c
 160  	if (!iter->value) {
 161  		zend_call_method_with_0_params(&object, iter->ce, &iter->ce->iterator_funcs.zf_current, "current", &iter->value);
 162  	}
 163  	*data = &iter->value;
Zend/zend_execute_API.c
 592  	/* we may return SUCCESS, and yet retval may be uninitialized,
 593  	 * if there was an exception...
 594  	 */
 595  	*fci->retval_ptr_ptr = NULL;
 873  	return SUCCESS;
```

All exact. **`:163 *data = &iter->value;` runs unconditionally**, which is the
whole mechanism: `value` is always a non-NULL address, so the depth-1 guard at
`:3832` can never fire, and the property that matters is `*value != NULL`.

**b) `▸ trigger` — (i) VERIFIED.** *"a user iterator whose `current()` throws"*.
`zend_call_method` (`zend_interfaces.c:48`) sets
`fci.retval_ptr_ptr = &iter->value`; `zend_call_function` writes
`*fci->retval_ptr_ptr = NULL` at `:595` and returns **SUCCESS** at `:873` even
with `EG(exception)` set (`:870-872`). So `iter->value == NULL`, `value ==
&iter->value != NULL`, `:3832` passes, and `:3853 (*value)->refcount++` derefs
NULL. There is no `EG(exception)` test anywhere between `:3831` and `:3853`.

**c) ⛔⛔ The R1h — and this is the row's blocker.**
`preimage_screen.py --row ph54 --verbose` → **`INAPPLICABLE`**. ⚠ Per F68/F95
that verdict is **not** an exclusion and says nothing. **So I read the patch,
and the patch says something:**

> **`fc96c7f7fa18` touches `Zend/zend_compile.c`, `zend_compile.h`,
> `zend_language_parser.y`, `zend_vm_def.h` and `zend_vm_execute.h` — and NOT
> `Zend/zend_execute.c`.** `grep -ac get_current_data` over the patch is **0**.
> Its `ZEND_FE_FETCH` hunks restructure the handler to use an `OP_DATA` word
> instead of building a temporary array; **the `if (!value)` guard is not in any
> hunk, and `(*value)->is_ref = 1` / `(*value)->refcount++` survive verbatim in
> the post-image.** Its subject is *"foreash($a as $key => $val) optimization
> Removed temorary variable"*. **It is a performance refactor, not a repair.**

⚠ `FIXSURVEY_001.md` already warned *"`R1h` for these rows is not a line you can
add to the kernel"* — this is **stronger than that**: it is not the repair at
all, and the file it patches (`zend_vm_def.h`) **did not exist in 5.0.0**, whose
executor *is* `zend_execute.c`. That is F68's *"VM-GENERATION BOUNDARY"*
firing on a second row.

**d) Census?** N/A — the commit repairs nothing of this row.

▶ **`ph54` is BLOCKED-ON-A-DECISION.** The decision: *what is `ph54`'s R1h?*
Candidates a build task would have to search for are a later commit that changes
`if (!value)` to test `*value`, or a statement that no such commit exists and
the row publishes that as its result (§C: *"An upstream fix is not automatically
correct… That is a result, and one of the strongest a row can carry"* — here the
sharper version is *"there may be no upstream fix at all"*).

### 2.6 T6 — **`ph60`** ✅ clean, **with a free 7-site census**; and **`ph97`** ✅ clean

I deep-verified **two** T6 rows, because P1 obliges me to score `ph60` and
because `ph97` is my actual recommendation.

#### `ph60`

**a) Citations, quoted from `php-5.0.0/ext/standard/ftp_fopen_wrapper.c`:**

```
 129  	if (resource == NULL || resource->path == NULL)
 130  		return NULL;
 649  	stream = php_ftp_fopen_connect(wrapper, path, mode, options, opened_path, context, &reuseid, &resource, &use_ssl, &use_ssl_on_data TSRMLS_CC);
 651  	/* set the connection to be ascii */
 652  	php_stream_write_string(stream, "TYPE A\r\n");
```

Exact. **No NULL test between `:649` and `:652`.**

**b) `▸ trigger` — (i) VERIFIED for the first clause.** *"a URL with no path"*:
`php_ftp_fopen_connect` returns NULL at `:130` **before any socket is opened**,
so `opendir("ftp://example.com")` reaches `:652` with `stream == NULL`. ⚠ **The
other two clauses of the trigger line are stale** — *"an `offsetUnset` that
bails"* and *"a missing optional argument"* belong to `ph96` and `ph97`, which
the row's own `⚠⚠ risk` line says were split out. Harmless, but it is a line
that contradicts the line under it.

**c) The R1h.** `--row ph60` → **`CANDIDATE`**, `1 id → 1 commit`.
**What `60fc9c050a44` actually changes:** in one file, hunk B adds exactly
`if (!stream) { goto opendir_errexit; }` after `:649`, and hunk A repairs the
early-NULL path so it hands `*presource` back (`if (resource && presource)
*presource = resource;`) instead of leaking it.

**d) ⭐ Census — and I measured a better one in the pristine C than the patch
gives.** `php_ftp_fopen_connect` is called at **seven** sites: `:409`, `:649`,
`:735`, `:811`, `:884`, `:946`, `:1040`. **Six of the seven are followed
immediately by `if (!stream)`; `:649` is the single omission.** That is
free, checkable evidence that the row is a **missing replication**, not missing
knowledge — the same shape `ph56`/`ph57` publish from the compiler side, on a
different subsystem.

#### `ph97`

**a) Citations, quoted:**

```
ext/mbstring/mbstring.c
3211  	char *typ = NULL;
3215  	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "|s", &typ, &typ_len) == FAILURE) {
3219  	if (!strcasecmp("all", typ)) {
Zend/zend_API.c
 485  			case '|':
 486  				min_num_args = max_num_args;
 487  				break;
 511  	if (num_args < min_num_args || num_args > max_num_args) {
 537  	while (num_args-- > 0) {
```

All exact.

**b) `▸ trigger` — (i) VERIFIED.** `mb_get_info()` with zero arguments. `"|s"`
puts the `|` first, so `min_num_args = 0` at `:486`; `:511`'s count test passes
with `num_args = 0`; the write loop at `:537` runs **zero** times; `typ` keeps
its `:3211` initialiser `NULL` and goes straight into libc `strcasecmp` at
`:3219`.

**c) The R1h.** `--row ph97` → **`CANDIDATE`**, `1 id → 1 commit`.
**What `f7326d627962` actually changes:** one file, one hunk, **one line** —
`if (!strcasecmp("all", typ))` → `if (!typ || !strcasecmp("all", typ))`. Benign
behaviour with `typ` supplied is unchanged.

**d) Census?** **No.** One hunk, one site. Clean negative.

### 2.7 ⛔ `ph32` — the row this task exists because of, read on its own terms

I read `RECAP_PHP.md` item 94, then `ph32`'s **own** Part B entry, then its
**own** R1h, then the pristine C. **The entry is accurate in every particular I
checked, and the row is expensive for exactly the reasons it states.**

- The three short tables are **reproduced** on the file I extracted myself:
  `ent_uni_338_402` **63 for 65**, `ent_uni_spacing` **22 for 23**,
  `ent_uni_8592_9002` **410 for 411** (plus ph102's `ent_uni_punct` 66 for 67) —
  `17 tables · 4 short · 0 UNEVALUATED`.
- The kinds are as stated. `:115-117` is `NULL ×21` under a `/* 354 - 375 */`
  marker that wants **22**; `:121-123` is `NULL ×24` under `/* 377 - 401 */`
  which wants **25**; `ent_uni_spacing`'s `:132-133` is `NULL ×20` under
  `/* 711 - 731 */` which wants **21**. All verbatim.
- The entry's own correction is right: **`int j, k;` is at `:878`**, not `:877`.
- `preimage_screen.py --row ph32 --verbose` → **`INAPPLICABLE-SAME-FILE`**, which
  per F68/F95 **is not an exclusion and says nothing.** ⚠ I am citing it as
  nothing. (F95 lists `ph32` among the 17 records that moved into that label.)
- **What `bd2e99ee50ed` actually changes**, at the bytes: it closes the
  `/* 376 (0x0178)` comment and removes the stray `*/` that had been placed
  after the swallowed block — i.e. it is the **un-swallowing** commit, the
  *fourth* in item 94's chain, and its pre-image is a 2005 layout that does not
  resemble 5.0.0's at all (5.0.0's `:108-125` uses `/* 338 */ … /* 402 */` run
  markers the pre-image has already lost).

▶ **`ph32` is ADMISSIBLE AND DEAR.** Criteria 1–3 all pass on the C. Rank it
low; do not kill it.

---

## §3 COST VERDICTS — in §3.3's four words

| family | verdict | the specific thing |
|---|---|---|
| **T6** | ⭐ **CHEAP** | `ph97`: one line of C is the R1h, one line of PHP is the trigger, and the kernel needs **none** of the nine cost ticks. `ph60` and `ph96` are the same shape. **Five catalogued rows, so the family can close.** |
| **S6** | ⭐ **CHEAP** | `ph38`: one-line R1h at the guard site, benign output bit-identical, trigger is upstream's own `.phpt`, harm is a measured SIGSEGV with zero uninitialised memory. ⚠ **But `n = 1`: the family cannot reach the min-2 floor** (§1.2). |
| **S4** | **CHEAP at `ph102`; the family is MEDIUM** | `ph102` needs nothing and carries **two** harms, one of them layout-independent. But `ph32` is DEAR (3 tables, 4 commits, one invisibly incomplete), `ph33` is DEAR (oniguruma), `ph34` is MEDIUM (host-libc dependence, measured), and **`ph36` is BLOCKED-ON-A-DECISION (no sha exists)**. |
| **S5** | **MEDIUM** | `ph37`'s mechanism and fault primitive are excellent and its R1h is a 6-site census — but the build task must be written with **a corrected trigger** and an **R1h decision** (`2 ids → 2 commits`) already made. ⚠ `n = 1` (§1.2). |
| **T2** | **MEDIUM** | Every row needs a zval-like value with `is_ref`/`refcount`; three need a HashTable, one of them with a working value destructor. `ph47` is the entry point (one-line R1h) but its trigger is wrong as written. **`ph101` is BLOCKED-ON-A-DECISION** (R1h decisively excluded) and `ph48`/`ph100` are DEAR (R1h deleted by a 17-file / 10-file rewrite). |
| **T4** | ⛔ **BLOCKED-ON-A-DECISION** | The mechanism deep-verifies perfectly and is the smallest in my set. **The decision is: what is `ph54`'s R1h?** The recorded `fix_commit` is a performance refactor that does not touch `zend_execute.c`, contains no `get_current_data`, and leaves the depth-1 guard and the faulting deref intact. ⚠ `n = 1` (§1.2). |

⛔ **No row in my set fails the C-side bar.** All 19 are correct on benign
inputs, exhibit their error on an adversarial input, and lift at a declarable
tier. **There is no kill in this report.**

---

## §4 THE RANKING, AND WHICH FAMILY I WOULD ENTER FIRST

Best first. One sentence each, written for a build-task author.

1. ⭐⭐⭐ **T6 — `ph97` first, `ph60` second.**
   *Build `ph97` as a kernel over a blob of `(argc_present_bitmap, bytes)` driving
   an argument parser with an optional spec that returns SUCCESS without writing
   the out-parameter, a consumer that dereferences it, and `c/kernel_hardened.c`
   = the single line `if (!typ || …)` from `f7326d627962`.*

2. ⭐⭐ **S6 — `ph38`.**
   *Build a `{len, ptr}` string value where two operands can point at one
   shared read-only buffer, walk `for (; *low <= *high; (*low) += step)`, and
   backport `ff1687731dee`'s one-line `Z_STRLEN >= 1` guard; the shared literal
   is the mechanism and giving each operand its own buffer deletes the row.*

3. ⭐ **S4 — `ph102`.**
   *Lift `ent_uni_punct` and the `entity_map` row verbatim, walk `k` from
   `basechar` to `endchar` inclusive indexing `table[k − basechar]`, fold the
   decoded code points into the `u64` so the layout-independent −1 drift is
   caught alongside the OOB read, and backport `46bc2c5ae2ae`'s single added
   `NULL`.*

4. **S5 — `ph37`.**
   *Two passes over one format string computing one index by two formulas, over
   an `args` array of plain `{int len; char *p;}` pointers — and write the task
   with the corrected trigger (`%N$` where `N == numVars`) and R1h
   `7d109bc62761` already decided.*

5. **T2 — `ph47`.**
   *A value with a type tag, a buffer and a `shared` bit, two parameters that can
   alias it, a `convert_to_long` that frees the buffer in place, and a consumer
   that `memcpy`s with the now-stale length — model **both** no-op modes of
   `SEPARATE_ZVAL_IF_NOT_REF`, not just `is_ref`.*

6. **T4 — `ph54`.**
   *A two-level out-parameter, a callee that writes the outer level
   unconditionally and the inner level only on success, and a caller that guards
   the outer — but do not dispatch it until the manager has decided what the R1h
   is, because the recorded one is not the repair.*

### ▶ WHICH ONE WOULD I ENTER FIRST, AND WHAT WOULD CHANGE MY MIND?

> ⭐ **`T6`, via `ph97`.** It is the only family in my set that simultaneously
> (a) has a one-line, one-file, one-hunk, 2005, same-file, single-id R1h whose
> patch I have read, (b) needs **none** of the nine cost ticks, (c) has a trigger
> I verified against the C rather than believed, (d) has **five** catalogued rows
> so entering it can discharge **2 of the 30 owed** the way T5 did, and (e) has a
> second row (`ph96`) whose repair is a *different hardening strategy for the
> same obligation* — *remove the output* rather than *test it* — which is a
> result the programme does not yet have.

**What would change my mind, stated so it can actually happen:**

1. ⛔ **If the manager wants row 11 to be TEMPORAL for portfolio reasons**, that
   is a legitimate programme decision and nothing in my report contests it — I
   contest only the claim that the temporal rows are *cheaper*.
2. ⚠ **If `ph97`'s "needs none of the nine" is wrong because
   `zend_parse_parameters` cannot be narrowed without dragging in
   `EG(argument_stack)`.** I read `zend_API.c:480-545` and believe a
   `(spec, argc, bytes)` model is faithful, **but I did not build it.** If a
   build task finds the argument stack load-bearing, `ph97` drops behind `ph60`,
   which needs nothing at all.
3. ⚠ **If agent A or B returns a temporal row with a 2004–2005 one-file one-hunk
   R1h, O(1) allocations per call and a verified trigger**, T6's margin is gone
   and the choice becomes a portfolio one. **I have not read their reports and
   must not.**
4. ⭐ **If the manager values "two harms in one row" over cheapness**, `ph102` is
   the pick: it is the only row in my set whose `u64` catches a *silent wrong
   answer* and an *out-of-bounds read* from the same kernel call, and its silent
   half is layout-independent.

---

## §5 THE THREE PREDICTIONS, SCORED FOR MY SCOPE

### P1 — *"at least ONE of ph87, ph60, ph85, ph66, ph37 fails deep verification"*

Two of the five are mine.

| row | verdict |
|---|---|
| **`ph60`** | ✅ **SURVIVES.** Citations exact, trigger verified to reach the site by reading the C, R1h is one file and adds exactly the named guard, and the row gains a free 6-of-7 replication census I measured in the pristine source. |
| **`ph37`** | ⛔ **FAILS.** Its `▸ trigger` **cannot fire** — `%2$d` with one variable is refused by the validate pass at `:384-385` — and the row carries **2 ids → 2 distinct commits**, which the task file's one-id line did not show. Both are correctable in a paragraph; neither was visible from a one-line summary. |

▶ **P1 is CONFIRMED in my scope, by `ph37`.** The manager combines with A and B.

### P2 — *"row 11 is a TEMPORAL row"*

▶ ⛔ **NOT SUPPORTED by my scope, and I argue it is refuted.** Full argument in
§0. In one line: **T6 offers four rows with 2004–2005 one-file R1h patches, two
of them one-liners, none needing the allocator, a HashTable, the executor,
userland re-entry or stack garbage — while `PROTOCOL_PHP.md` §B1a predicts the
O(1)-allocation precondition to fail on *most* `E*` rows and §C measures the
multi-commit R1h load at 68 % temporal against 7 % spatial.** And P2's stated
grounds rest on a ranking built at **91 rows** that could not see `ph96`, `ph97`
or `ph102`, all three of which have the shape it scored best on.

### P3 — *"`▸ trigger` lines fail on roughly a third of rows deep-verified"*

| row | trigger |
|---|---|
| `ph102` | ✅ **(i) VERIFIED** |
| `ph37` | ⛔ **(iii) WRONG** — corrected trigger supplied and cross-checked against the upstream fix's own `- 1` |
| `ph38` | ✅ **(i) VERIFIED** — and upstream's `bug32021.phpt` is the independent oracle |
| `ph47` | ⛔ **(iii) WRONG as written** — 3 arguments, so `len` is never read; two working triggers supplied |
| `ph54` | ✅ **(i) VERIFIED** |
| `ph60` | ✅ **(i) VERIFIED** (first clause; the other two clauses are stale text from the pre-split row) |
| `ph97` | ✅ **(i) VERIFIED** |

**2 wrong of 7 = 29 %.** ▶ **P3 is SUPPORTED in my scope** and reproduces
F46/F49's 3-of-9 almost exactly. ⚠ **And the split repeats F46's shape: the
DEFECT SITE was wrong in 0 of 19 rows — I opened the `provenance` defect-site
citation of every row in my set and every one is exact — and in 0 of the ~40
further secondary citations I opened (see §7.12 for the ones I did NOT open).
The failures are all in the `▸ trigger` half.**

---

## §6 CATALOGUE DEFECTS FOUND

Every one of these was found by reading the C or the patch, not by inference.
**I have not edited `CATALOGUE.md`.**

1. ⛔⛔ **`ph54`'s R1h is not the repair.** `fc96c7f7fa18` does not touch
   `Zend/zend_execute.c`, contains **0** occurrences of `get_current_data`, and
   its `ZEND_FE_FETCH` hunks leave both the depth-1 guard and the faulting
   `(*value)->refcount++` intact. `FIXSURVEY_001.md`'s note (*"R1h for these rows
   is not a line you can add to the kernel"*) understates it. **Consequence: the
   row cannot be dispatched as written.**
2. ⛔ **`ph101`'s R1h is decisively excluded.** `preimage_screen.py --row ph101
   --verbose` returns **`NOT-THE-REPAIR`** with `decisive: True`,
   `same_function: True` — the pre-image reads
   `zend_hash_update(&ce->default_static_members, …)` where 5.0.0 reads
   `zend_hash_update(ce->static_members, …)`. This is one of F95's 25 genuine
   exclusions and nothing in the row's block mentions it.
3. ⛔ **`ph37`'s `▸ trigger` cannot fire** (§2.2), and the row carries **2 ids →
   2 commits** with the second one dated **2024** and repairing a *different*
   defect (signed overflow).
4. ⛔ **`ph47`'s `▸ trigger` has too few arguments** to reach its own cited line
   (§2.4). Its `⚠ risk` line survives, but the mechanism paragraph names only one
   of `SEPARATE_ZVAL_IF_NOT_REF`'s two no-op modes, and **upstream repaired the
   other one** (`SEPARATE_ZVAL(len)` on the outer parameter, `refcount > 1`).
5. ⭐⭐ **`ph59`'s title and Part A cell name the half upstream did NOT fix.**
   The fix `f046cdf3fa15` changes `&& result` → `|| !result` and **leaves
   `!zend_call_function(…) == SUCCESS` verbatim**. With `SUCCESS 0` / `FAILURE
   -1` (`Zend/zend.h:240-241`, verified) that expression is *accidentally
   equivalent* to `f() != SUCCESS`, so the defect is the `&& result` conjunct —
   which can never be true, because `result` is NULL exactly when the call
   failed. **The row's own block body already says this correctly; only its
   title, its 12-word Part A mechanism and its `⚠ risk` defence say
   "precedence".** ⭐ This makes the row *better*: *"a guard whose two conjuncts
   are mutually exclusive"* is sharper and more distinctive than a typo.
6. ⚠ **`ph35`'s upstream fix is PARTIAL, and the block does not say so.**
   `ae57857ebac7` adds the `(unsigned char)` casts and **leaves `0xff` where the
   block correctly says `0x100` was meant** — so the commit whose subject is
   *"support more than 127 named subpatterns"* still mis-maps every index at or
   above 256. This is `PROTOCOL_PHP.md` §C's *"an upstream fix is not
   automatically correct… Report it; do not repair it"*, available for free.
7. ⚠ **`ph60`'s `▸ trigger` line is stale after the split.** It still reads
   *"a URL with no path / an `offsetUnset` that bails / a missing optional
   argument"*, while the row's own `⚠⚠ risk` line two lines below says those two
   merges are gone (to `ph96` and `ph97`).
8. ⚠ **`ph99`'s `fix_commit` subject actively misdescribes the patch.**
   `33a1a4d39ae3` — *"Changed error message (E_ERROR -> E_NOTICE)…"* — **is** the
   repair: its first hunk inserts, at exactly the cited `if (rv) { retval = &rv;
   }` site, the missing separation for `BP_VAR_W|BP_VAR_RW|BP_VAR_UNSET`
   (`ALLOC_ZVAL(rv); *rv = *tmp; zval_copy_ctor(rv); rv->is_ref = 0; rv->refcount
   = 0;`). ⭐ **This is §0's rule cutting the other way from `ph32`'s: the summary
   makes a GOOD row look bad.** ⚠ Its second hunk **comments out** the E_ERROR at
   the old `:361-363` with `//` in a C file, so a backport must take hunk A only
   and say so.
9. ⚠ **`ph33`'s 12-year survival is readable from the patch and not stated.**
   `b7259b71b430`'s 2016 pre-image still reads `char pat_buf[2];` — the same as
   5.0.0's `:624` — so this is `FIXSURVEY_001.md`'s case **(a)**, *the defect
   really survived*, settled without a tag comparison. The fix is
   `pat_buf[2]` → `pat_buf[6]` plus four `'\0'` stores.
10. ⚠ **`FIXSURVEY_001.md`'s `≥ 5 files` list is stale at 12; the tool now says
    23**, and `ph100`'s `248345d9208a` (10 files) is among the new entries. The
    per-row table should be regenerated at 102 rows (§1.1).
11. ⓘ **`ph34`'s stated risk is now DISCHARGED, in the affirmative.** *"State the
    libc and the measured table bounds, or the row is unreproducible."* Measured
    on this box (`.temp/php54C/probe_ctype.c`): **glibc 2.39, x86-64**; the
    `__ctype_b` table is valid over `-128 .. 255`; index `-100000` is **-200 000
    bytes** from the base, the read **succeeds without SIGSEGV** and returns
    `0x8553`, whose `_ISalpha` bit is **set** — so `ctype_alpha(-100000)` answers
    **true**. The harm is a silent wrong answer, and the *value* is
    image-layout-dependent, which is the row's real cost.
12. ⓘ **`ph36` is the only row in all 102 with no `fix_commit`** (`NO-SHA`, and
    `history_status: fixed-by-rewrite`). `PROTOCOL_PHP.md` §C defines
    `c/kernel_hardened.c` as *"the `fix_commit` patch backported and
    sha-pinned"*; that is unsatisfiable here. **Not a kill — a decision the
    manager owes before the row can ever be dispatched.**

---

## §7 ⭐ WHAT I AM UNSURE OF

Named, not omitted.

1. ⚠ **`ph102`'s second R1h spelling `35e43dabe16b` (the PHP-5.0 branch twin) is
   UNVERIFIED.** It is not in the patch cache and I did not fetch. I verified
   only `46bc2c5ae2ae`, the sha the corpus column carries.
2. ⚠ **I did not run PHP 5.0.0.** Every trigger classification is *"verified by
   reading the C"*, never *"observed"*. For `ph38` and `ph98` I have upstream
   regression tests as independent corroboration; for the others I do not.
3. ⚠ **`ph38`'s SIGSEGV is measured on a standalone probe (gcc 13.3.0, `-O0`,
   x86-64, PIE), not on PHP 5.0.0.** The write is UB and a different toolchain
   could place `""` in a writable section, in which case the harm becomes silent
   corruption rather than a fault. The row is admissible either way; the
   *observable* would change. I did not test a second compiler.
4. ⚠ **`ph47`'s trigger (1), the `is_ref` path, is traced but not run.** I am
   confident about the C; I am **not** certain that PHP 5.0's parameter passing
   hands `substr_replace` the *same* `zval **` for `$s` and `$r`. Trigger (2) is
   upstream's own `.phpt` and I trust it more.
5. ⚠ **`ph97`'s cost verdict assumes `zend_parse_parameters` narrows to a
   `(spec, argc, bytes)` model.** I read `zend_API.c:480-545` and the write loop,
   but the `EG(argument_stack)` access at `:527-528` is real and I did not price
   a substitute for it.
6. ⚠ **I did not read the `ph96` patch's pre-image against 5.0.0 line by line.**
   5.0.0's `zend_std_unset_dimension` lacks the `SEPARATE_ARG_IF_REF(offset)` /
   `zval_ptr_dtor(&offset)` lines the 2005 patch's context shows, so the backport
   is *not* a clean apply, though the three lines the fix removes are all present
   in 5.0.0.
7. ⚠ **`ph36`'s reachability is unverified.** I confirmed the two identical
   `yycheck[yyx + yyn]` instances at `:3518` and `:3534`, but I did **not** find
   a parse-error state whose `yypact` entry drives the sum past the table. The
   row's `▸ trigger` is **(ii) plausible but unverified** by me.
8. ⚠ **`ph33`'s harm depth is unverified.** I confirmed `pat_buf[2]` at `:624`,
   the fill at `:663-667` and `k_strcpy`'s `xmemcpy(dest, src, len)` at
   `regparse.c:378`, but I did **not** trace how oniguruma derives the `end`
   pointer from the lead byte's declared length. The row's `▸ trigger` is
   **(ii) plausible but unverified**.
9. ⚠ **`ph34`'s and `ph35`'s R1h shapes are read from the patches; neither row
   was deep-verified for trigger reachability.**
10. ⚠ **TWELVE ROWS HAVE NO TRIGGER CLASSIFICATION FROM ME** — `ph32`, `ph33`,
    `ph34`, `ph35`, `ph36`, `ph48`, `ph59`, `ph96`, `ph98`, `ph99`, `ph100`,
    `ph101`. For every one of them I opened the defect-site citation against the
    tarball (all exact) and read the fix patch; `ph32` additionally got a
    Stage-2-depth read in §2.7, and `ph96`'s callee half is verified through
    `ph54`'s chain (`zend_execute_API.c:592-595`, `:873`). **What is missing in
    all twelve is the trigger traced end to end.** On F46/F49/P3's base rate,
    **roughly four of the twelve should be expected to be wrong.**
11. ⚠ **My §0 refutation of P2 compares my measured rows against
    `PROTOCOL_PHP.md`'s stated properties of the temporal axis, not against
    agents A's and B's findings, which I have not read and must not.**
12. ⚠⚠ **SIX SECONDARY CITATIONS I DID NOT OPEN**, listed so §5's claim is
    bounded. I opened the **defect-site** citation of all 19 rows and ~40 of
    their secondary citations; these six I did not:
    `ph99` → `Zend/zend_execute.c:1266`, `:1277-1281`, `:1220`, `:2883-2886` and
    `zend_object_handlers.c:470-473`; `ph100` → `Zend/zend_execute.c:753`;
    `ph101` → `zend_object_handlers.c:783-784`; `ph98` →
    `zend_exceptions.c:519`, `zend_API.c:204`, `zend_builtin_functions.c:1038`.
    **Each is a CONSUMER or GUARD frame, not a defect site.** Nothing in my
    verdicts turns on them, but "every citation checked" would have been false
    and I am not writing it.
13. ⚠ **`ph98`: I tried to cheapen the trigger from the fix's own reproducer and
    it does NOT apply.** `set_exception_handler("ehandle::exh")` fails at
    registration on 5.0.0, because `zend_is_callable`'s `IS_STRING` arm
    (`zend_API.c:1649-1662`) looks the whole string up in `EG(function_table)`
    and 5.0.0's `zend_call_function` has **no** `strstr(fname, "::")` handling at
    all. **`TASK_PHP_021`'s constructed trigger stands.** Recorded as a checked
    negative so nobody repeats it.

---

## §8 WHERE MY DEPTH RAN OUT

**It did not run out inside a row; it ran out at the boundary in §7 items 10 and
12.** I completed Stage 1 for all 19 rows from their own Part B entries, opened
the **defect-site** citation of all 19 against the pristine tarball plus ~40 of
their secondary citations (all exact; the six I did not open are named in §7.12),
read the fix patch for 18 of the 19 records (`ph36` has none; `ph100`/`ph48`/
`ph99` read at the relevant hunk only), and completed Stage 2 for **seven** rows
— one per family plus `ph97` and `ph32`. **What I did not do is trace the
remaining twelve rows' `▸ trigger` lines end to end.** That is the half F46
measured as load-bearing, and on this task's own base rate ~4 of those 12 should
be expected to be wrong. **If the manager picks a row I did not deep-verify, the
trigger is the thing to check first.**

---

## §9 REPRODUCING THIS

`.temp/php54C/NOTES.md` carries every command. In short:

```sh
T=/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
sha256sum "$T"        # 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919
tar -xzOf "$T" php-5.0.0/<path>.c > .temp/php54C/src/<path>.c

python3 .tasks-php/fixsurvey.py --offline          # rewrites .temp/mgr/batch/fixsurvey.json
python3 .tasks-php/preimage_screen.py --row phNN --verbose
python3 .temp/mgr165/count_ent.py .temp/php54C/src/ext_standard_html.c
cc -O0 -o .temp/php54C/probe_ctype     .temp/php54C/probe_ctype.c     && ./.temp/php54C/probe_ctype
cc -O0 -o .temp/php54C/probe_emptystr  .temp/php54C/probe_emptystr.c  && ./.temp/php54C/probe_emptystr
```

**No network fetch was made.** All 22 patch records for my 19 rows resolved from
`.temp/mgr/batch/patches/` (163 cached) and `.temp/mgr165/`. The extracted `.c`
files and the two probe binaries are deleted; the two probe `.c` sources, the
survey log and the screen log stay.
