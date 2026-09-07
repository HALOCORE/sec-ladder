# Spatial-axis mining over PHP 5.0.0 — reasoning, families, rejections, corrections

Scope: the 47 rows of `vuln-corpus-5.0/index.csv` with `cwe` in {CWE-125 (22), CWE-787 (12),
CWE-190 (13)}. Every line/quote below was read out of the pristine tarball
`.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz`
(sha256 `5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919`, 5595997 bytes).
No patched tree was consulted. `VERIFY.md` has the re-derivation commands.

Output: **16 candidates** covering **18 corpus rows**, **8 of them `ptr_cursor: true`**.

---

## 1. The question I was asked to check, and the answer

> "I believe `ext/standard/formatted_print.c` is the densest single site (four root causes in
> one function) and therefore the best spatial candidate. I may well be wrong."

**Half right, and the wrong half matters.**

**Right about density.** Spatial root causes per KLOC of pristine source:

| file | spatial causes | lines | per KLOC |
|---|--:|--:|--:|
| **ext/standard/formatted_print.c** | **4** | **896** | **4.46** |
| ext/standard/url.c | 2 | 655 | 3.05 |
| ext/standard/html.c | 3 | 1292 | 2.32 |
| ext/standard/var_unserializer.c | 2 | 944 | 2.12 |
| ext/standard/scanf.c | 2 | 1260 | 1.59 |
| ext/standard/string.c | 7 | 4808 | 1.46 |
| ext/exif/exif.c | 2 | 4048 | 0.49 |
| Zend/zend_execute.c | 2 | 4451 | 0.45 |

`formatted_print.c` is the densest file by a clear margin, and it is also the only file in the
corpus where **all** of its root causes are spatial (4 of 4; `string.c` is 7 of 9,
`zend_execute.c` is 2 of 27).

**Wrong about "one function."** The four causes are in **three** functions:

| row | line | enclosing function | span |
|---|--:|---|---|
| CRASH-149 | 96 | `php_convert_to_decimal` | 65–155 |
| CRASH-001 | 190 | `php_sprintf_appendstring` | 171–218 |
| CRASH-011 | 211 | `php_sprintf_appendstring` | 171–218 |
| CRASH-016 | 599 | `php_formatted_print` | 478–~700 |

**Wrong about "the four may be one mechanism"** — they are four distinct mechanisms, and this is
the file's real strength:

- `:96` negative-length `memmove` into an 80-byte **static** buffer (no allocator at all);
- `:190` signed wrap of a sizing sum defeats a grow guard, unbounded **pad loop** writes;
- `:211` `long`→`int` narrowing of a parsed precision produces a negative `copy_len` that both
  satisfies the guard honestly and becomes a ~1.8e19 `memcpy` length;
- `:599` a lookahead **consumes the NUL terminator as data**, leaving a scanner with no
  stopping condition.

Only `:190` and `:211` share a function, and even they are two mechanisms sharing one guard.

**Not too tangled to extract.** The 400-line `php_formatted_print` driver, which is the
intimidating part, is **not needed for any of the four**. `php_convert_to_decimal` is 90 lines
and depends only on `modf`/`memmove`. `php_sprintf_appendstring` is 48 lines and depends only on
`erealloc`/`memcpy`. The `:599` scanner is a 15-line `for(;;)` over a `char *` and an `int`. All
four are `verbatim`.

**But it is not "the best spatial candidate," for one specific reason:** *three of the four are
index-family*, and the fourth (`php_convert_to_decimal`) is the most equivocal `ptr_cursor: true`
call I made. If the goal is the missing pointer-offset-walk shape, `formatted_print.c` is close to
the worst place to look in the corpus, not the best. `var_unserializer.c`, `uuencode.c` and
`url.c` are where that shape lives. My ranking reflects both facts: formatted_print supplies
three candidates (ranks 4, 11, 12) but not the top three.

---

## 2. Mechanism families

I grouped the 47 rows into **nine** families. Ranked by how many distinct C mechanisms each
contains, not by row count.

### F1 — Unbounded cursor walk (the pointer-offset-walk family)  → candidates 1, 2, 3, 7, 6(sink)
The bound is absent, wrong, or present-but-unread while a pointer is advanced and dereferenced.
Rows: CRASH-066, CRASH-115, CRASH-110, CRASH-073, CRASH-120, CRASH-102 (sink half).
Sub-mechanisms, all genuinely different:
- the limit variable is *initialised to the wrong end* and the refill hook is a no-op, while the
  true end sits unused in a parameter (`var_unserializer.c:243` + `:106`, with `max` in
  `UNSERIALIZE_PARAMETER` at `:150` never compared to anything);
- the loop bound is computed from a *length field inside the data* rather than from the buffer
  (`uuencode.c:141`, `ee = s + (len==45 ? 60 : floor(len*1.33))`);
- a *blind fixed-offset peek* forward from a found cursor (`url.c:132`, `*(e+5)`);
- a *blind fixed-offset advance* of the caller's cursor (`var_unserializer.c:208-210`, `(*p) += 2`);
- a hand-maintained *length counter desyncs from the cursor it shadows*, and a later
  `base + length` reconstruction inherits the drift (`url.c:139/:143/:167`);
- termination on pointer *equality* rather than `<`, so a wrong end pointer is not merely wrong
  but steppable-past (`string.c:1330`, `for (spanp = s2; p != s1_end && spanp != s2_end;)`).

### F2 — Sizing arithmetic wraps, allocation shrinks, unbounded output cursor writes anyway  → candidates 8, 9
Rows: CRASH-006, CRASH-007, CRASH-106, CRASH-107, CRASH-109 (+ CRASH-014 pack, CRASH-009 reg,
CRASH-147 concat, CRASH-017 rawurlencode). Five arithmetic shapes:
`count*(width-1)+base` (char_to_str), `base+(quotient+1)*width` (chunk_split),
`base+count*const` (nl2br), `len*mult` truncated from a 64-bit product into an `int` (str_repeat),
`textlen*(breakcharlen+1)` (wordwrap). Every one of them wraps **downward to a small positive**,
so the allocator behaves perfectly and the emit pass, whose output cursor has no bound, does the
damage. See §4 for the `emalloc` question, which is the interesting part of this family.

### F3 — A guard that runs but is wrong  → candidates 6, 14, 16, 5
- guard evaluated on *truncated* values: `((unsigned) start + (unsigned) len) > len1` where both
  are `long` (`string.c:240`);
- guard *sized for the narrower of two branches* while the data picks the branch
  (`iptc.c:339` reserving 4 bytes, `:346-347` reading 6);
- guard *short-circuited by an unrelated argument*: `if (len && offset >= s1_len)`
  (`string.c:4786`);
- guard *one-sided on a signed index*: `if (lval <= strlen)` with no `>= 0`
  (`zend_execute.c:4033`).

### F4 — In-band terminator mishandled  → candidate 11
`format[++inpos]` consumes the NUL as a padding character and steps past it
(`formatted_print.c:599-600`), leaving the `for(;;inpos++)` at `:591` with no exit.
I1/O3 in its purest form.

### F5 — Declared extent ≠ realised extent (static data)  → candidate 10
`entity_map` states a codepoint range in one place; the table literal has a different number of
entries in another; `for (k = basechar; k <= endchar; k++) table[k - basechar]`
(`html.c:392-410` vs `:108`/`:155` and the loop at `:896`).

### F6 — Reserve lost between the initial sizing and the growth path  → candidate 13
`safe_emalloc(1, n, 1)` reserves n+1 with `max_buffer_len = n`; `erealloc(max_buffer_len + 2)`
then sets `max_buffer_len += 2`, so the +1 slack is gone; the terminator write is the one write
that skips the grow check (`metaphone.c:147-155`, `:185-189`, `:465`).

### F7 — Unvalidated integer used directly as a table index  → candidate 15
`RETURN_BOOL(iswhat(Z_LVAL_P(c)))` (`ctype.c:99-100`), with the correct range reduction three
lines below at `:108`.

### F8 — Two passes disagree  → not built; see §3
The validate pass and the use pass compute the same index by different formulas
(`scanf.c:383` `objIndex = value - 1` vs `scanf.c:734` `objIndex = varStart + value`);
or the sizing pass and the emit pass apply different clamps (`pack.c:247` vs `:317-372`;
`datetime.c:359`).

### F9 — Pointer/integer representation defects  → not built; see §3
Sign-extended `char` in a byte-pair index decode (`php_pcre.c:448`,
`name_idx = 0xff * name_table[0] + name_table[1]` — note also the wrong multiplier, `0xff` for
`0x100`); a pointer stored into an `int` cache field and truncated on 64-bit
(`mbfilter_htmlent.c:161`); `base + attacker_32bit_offset` with only a lower-bound check
(`exif.c:3072`/`:3079`).

---

## 3. Rejections, and the **C-side** reason for each

I rejected nothing for a Rust-side, Verus-side, Miri-side or cost-gradient reason. The bar I
applied is the one in the brief: does the C program make sense, does it misbehave on an
adversarial input, and is its **C mechanism** distinct from a candidate I already have. Every
rejection below is **duplication of C mechanism** or **the C program does not fit a
blob-in/checksum-out shape**, and I say which.

**Rejected as C-side duplicates** (same mechanism as a candidate; listed as near-duplicates in
the candidate's `risks`, so the manager can promote any of them):

| row | file:line | duplicate of | why |
|---|---|---|---|
| CRASH-106 nl2br | string.c:3593 | candidate 8 | `base + count*const` in `int`; same wrap-down-then-unbounded-`*target++` story. Distinct only in that reaching the wrap needs a ~358 MB input (`repl_cnt` must exceed 357,913,942), which is a *worse* kernel, not a different mechanism. |
| CRASH-107 str_repeat | string.c:4144 | candidate 8 | Truncation of a 64-bit product into `int result_len` (:4120), making the `> 2147483647` half of the guard at :4145 dead. Genuinely a *narrowing* rather than a *wrap*, so it is the strongest promotion candidate of the three. |
| CRASH-109 wordwrap | string.c:682 | candidate 8/9 | `textlen * (breakcharlen + 1) + 1` in `int`. Same family; the function has a second, unrelated `alloced` growth path at :692 that muddies the extraction. |
| CRASH-090 html punct table | html.c:155/:401 | candidate 10 | Literally the same defect on a different table. Merged into candidate 10's `root_cause_ids`. |
| CRASH-120 unserialize `(*p) += 2` | var_unserializer.c:208-210 | candidate 1 | Same file, same cursor, and the blind `+2` advance is close enough to the `+5` peek of candidate 3 that I merged the *pattern* rather than the *row*. Worth promoting if the manager wants a second unserialize row — the sink (`finish_nested_data:195`, `*((*p)++)`) is different from candidate 1's lexer sink. |

**Rejected because the C program does not fit blob-in / u64-checksum-out** (admission criterion 3,
not a Rust-side reason):

| row | file:line | C-side reason |
|---|---|---|
| CRASH-097 stream_socket_recvfrom | streamsfuncs.c:321 | The defective quantity comes from a **socket**, not from the blob: `emalloc(to_read + 1)` then `php_stream_xport_recvfrom(...)`. There is no correct-on-benign-input pure computation here; without a live socket the kernel computes nothing. **But see §4** — this row is one of only two where the `_emalloc` truncation is load-bearing, so it should be recorded as a finding even though it is not buildable. |
| CRASH-098 FD_SET past `fd_set` | streamsfuncs.c:541 | Same: needs `RLIMIT_NOFILE > ~1200` and real file descriptors. |
| CRASH-005 bison `yycheck` table | zend_language_parser.c:3518 | The generator, not the C, owns the table; there is no kernel, only a generated parser. Also `crashes_pristine_5_0_0 = False` and the fix is "bison regeneration; no single commit". |
| CRASH-055, CRASH-056 | zend_compile.c:1456, zend_execute.c:200 | Both are *opcode-emission* defects — the compiler fails to emit a free, or emits a temp-var reference that is never initialised. The defect is in the compiled program, not in a computation over a byte blob. CRASH-056 additionally `requires: writable /tmp`. |
| CRASH-033 | zend_object_handlers.c:199-201 | Needs the class-entry/property-info hash machinery for the defect to exist at all; a modelled version would be a different program. |
| CRASH-157 | zend_exceptions.c:310-311 | `emalloc(strlen + MAX_LENGTH_OF_LONG + 2 + 1)` then `sprintf(s_tmp, "%s(%ld): ", ...)` — the budget covers 2 of the 4 literal format characters. Genuinely nice and genuinely small, but the surrounding `TRACE_APPEND_*` machinery and `zend_hash_apply_with_arguments` are the program; the blob would have to encode a backtrace. **Closest of the rejects to admissible** — if the manager wants a 17th, this is it. |
| CRASH-077 range() | array.c:1572 | The write is `(*low) += lstep` **into the operand's own buffer**, and the reason that is a defect is that an empty PHP string's `Z_STRVAL` points at the shared global `empty_string`. That is a value-model/ownership property, not a spatial one; without zval copy-on-write semantics the C is just a byte increment. |
| CRASH-133 bcmath, CRASH-135 calendar | bcmath.c:542, julian.c:172 | Both need their own arbitrary-precision / calendar libraries to come along; the defect lives in a library the corpus does not otherwise touch. |
| CRASH-123, CRASH-124, CRASH-127, CRASH-128 | mbstring/libmbfl, oniguruma | The mbstring rows all require libmbfl's filter-chain object model or a bundled oniguruma. CRASH-123 (`mbfilter_htmlent.c:161`, a `char *` stored into an `int` field, truncated on 64-bit) is a *lovely* mechanism and the corpus labels it with a NEW invariant (`pointer-value-integrity`) rather than I1/I11 — recorded here as a finding, rejected only because the machinery is a whole conversion framework. |
| CRASH-009 ereg_replace | reg.c:337 | `buf_len = 1 + buf_len + 2*new_l` wraps in `int`, and the emit pass at :349-359 uses a bare `walkbuf` output cursor — a good F1+F2 hybrid, and `ptr_cursor: true`. Rejected because the sizing pass depends on `regexec` match offsets: the C is correct-on-benign-input only if a POSIX regex engine comes along. `modelled`, and the model would decide the defect's reachability. |
| CRASH-130 pcre | php_pcre.c:448 | Same reason (needs PCRE's name table). The mechanism (`0xff *` where `0x100 *` is meant, on a signed `char`) is small enough to model, and I would promote it over CRASH-009 if the manager wants an F9 row. |
| CRASH-134, CRASH-136 exif | exif.c:2725, exif.c:3072/:3079 | **These two are the best of the rejects and I am least sure about them.** A JPEG is a flat byte blob, so `blob_drivability` is perfect, and CRASH-136's mechanism (`CharBuf + offset_of_ifd` where the guard at :3072 checks only `offset_of_ifd < 0x08` and never `> length`) is a clean `base + attacker 32-bit offset`. CRASH-134's is `components * php_tiff_bytes_per_format[format]` overflowing and then being used in the very bound check meant to catch it (:2725 → :2727 → :2731). Rejected on extraction cost only: `exif_process_IFD_in_JPEG` and `exif_process_IFD_in_MAKERNOTE` are mutually recursive over a 4000-line file with `ImageInfo` state throughout. Both `requires` fixtures that the corpus does ship (`bug48378.jpeg`, `bug54002_1.jpeg`, `bug54002_2.jpeg`). **If the manager will accept a `narrowed` extraction of ~200 lines, CRASH-136 belongs in the built set.** |
| CRASH-091 get_next_char | html.c:656 | Admissible, and I nearly built it. `unsigned char next2_char = str[pos+1];` at :656 with the enabling defect being the **signature** at :486-490 — `get_next_char(charset, str, newpos, mbseq, mbseqlen)` takes no length, so there is no bound in scope to check against. Rejected only because candidate 14 (iptc) already carries "reads k bytes ahead of a guard" in index spelling, and candidate 3 carries the peek in pointer spelling. **The "the bound is not a parameter" framing is distinct from both** and this is my strongest almost-promoted row. |
| CRASH-018, CRASH-019 scanf | scanf.c:734, scanf.c:383 | F8. CRASH-018 is a clean two-pass disagreement (`objIndex = value - 1` in validate at :383 vs `objIndex = varStart + value` in execute at :734, no bound check at all in the execute pass, and the OOB use at :893 `current = args[objIndex++]`). Rejected because the OOB object is an **array of `zval **` pointers** which is then dereferenced and written through — modelling that faithfully means modelling zvals, and modelling it unfaithfully changes what the defect is. |
| CRASH-014 pack | pack.c:247 | F8/F2. `outputpos += (arg + 1) / 2` wraps, then `emalloc(outputsize + 1)` at :304 and the emit loop at :309+ writes the unwrapped amount. Rejected as an F2 duplicate; noted because it is the corpus's cleanest *two-pass* sizing mismatch and the sizing pass and emit pass are 60 lines apart in the same function. |
| CRASH-147 concat | zend_operators.c:1168/:1178 | F2, but with a `uint`→`int` truncating store at :1178 rather than a wrap. Rejected because triggering it needs two ~1 GiB strings resident (`requires: ASAN_OPTIONS max_allocation_size_mb>=4096`), which makes it a bad micro-benchmark kernel. The mechanism (an allocation that genuinely succeeds at 2 GiB, followed by a length field that cannot represent it) is real and worth recording. |
| CRASH-017 rawurlencode | zend_alloc.c:129/:148/:182 | **Not rejected on mechanism — see §4.** It is the corpus's own relocation of a 4.0.2 defect onto the 5.0.0 allocator, and it is the one row where `emalloc_dependent` is unambiguously true. I did not make it a candidate because its "kernel" would be the allocator, not a computation. It belongs in the report as the evidence for §4. |
| CRASH-089's sibling short tables | html.c | Not rejected — folded into candidate 10, along with **two short tables the corpus does not record**. See §5. |
| CRASH-094's first-tag loop | iptc.c:327 | Not rejected — recorded in candidate 14's `risks` as a third over-read the corpus does not list. |

---

## 4. The allocator question, answered for every sizing candidate

**Verified first, in the pristine tarball.** `Zend/zend_alloc.c`:

```
129:	unsigned int real_size;		\
132:#define REAL_SIZE(size) ((size+7) & ~0x7)
135:	real_size = REAL_SIZE(size);				\
148:	CALCULATE_REAL_SIZE_AND_CACHE_INDEX(size);
182:		p  = (zend_mem_header *) ZEND_DO_MALLOC(sizeof(zend_mem_header) + MEM_HEADER_PADDING + SIZE + END_MAGIC_SIZE);
```

`_emalloc` takes `size_t size` (64-bit) and assigns `REAL_SIZE(size)` into a **32-bit
`unsigned int`**, and `:182` mallocs from the truncated value. `emalloc(2^32)` therefore
allocates a header-sized block and **returns a valid pointer**.

There is a **second** truncation the brief does not mention, and I found it in
`Zend/zend_alloc.h`:

```
	unsigned int size:31;
	unsigned int cached:1;
} zend_mem_header;
```

The *recorded* size is a **31-bit bitfield**. `p->size = size` therefore also truncates, so the
free/accounting path is wrong independently of the malloc path.

And `_safe_emalloc` (`zend_alloc.c:221-244`) does its overflow check in **64-bit `long`**
(`ZEND_SIGNED_MULTIPLY_LONG`, `lval < (long)(LONG_MAX - offset)`) and then calls
`emalloc_rel(lval + offset)`. So a request that safe_emalloc correctly judges representable is
handed straight to the truncating `_emalloc`. **`safe_emalloc` does not protect against the
truncation; it protects against a different thing.**

### Per-candidate answer

| candidate / row | wraps where | direction | `emalloc_dependent` |
|---|---|---|---|
| 4 · CRASH-001 appendstring | `int req_size` at :190, caller | to negative | **false** — `erealloc` is never reached; the buffer is simply not grown |
| 4 · CRASH-011 precision | `int copy_len` at :180, caller | to `INT_MIN` | **false** — the huge value goes to `memcpy`, not to the allocator |
| 8 · CRASH-006 char_to_str | `int` at :2946 | down to small positive | **false** — allocator sees an ordinary small request |
| 9 · CRASH-007 chunk_split | `int` inside safe_emalloc's *first argument*, :1781 | down to small positive | **false** — and instructively so: the overflow-checked wrapper is present and is defeated by the caller's parentheses, not by the truncation |
| 12 · CRASH-149 cvt_buf | `int mvl` at :95 | to a negative memmove length | **false** — static BSS buffer, no allocator at all |
| 13 · CRASH-095 metaphone | no wrap; a lost +1 | n/a | **false** |
| 6 · CRASH-102 strspn | `(unsigned)` cast inside a comparison, :240 | clamp bypassed | **false** — no allocation is sized from it |
| — CRASH-106 nl2br | `int` at :3593 | down | **false** |
| — CRASH-107 str_repeat | 64-bit product → `int result_len`, :4144 | truncated down | **false** |
| — CRASH-109 wordwrap | `int` at :682 | down | **false** |
| — CRASH-014 pack | `int outputpos` at :247 | down | **false** |
| — CRASH-009 ereg_replace | `int buf_len` at :338 | down | **false** |
| — CRASH-147 concat | `uint res_len` at :1168, then `uint`→`int` at :1178 | 2 GiB+1 | **false** — `2^31+2` fits in `unsigned int`, so no truncation; the 2 GiB `erealloc` genuinely succeeds. Depends on the allocator *not refusing large requests*, which is a different property. |
| — **CRASH-017 rawurlencode** | — | — | **TRUE** |
| — **CRASH-097 recvfrom** | `emalloc(to_read + 1)` at :321 | large positive `long` | **TRUE for the large-positive path** |

### The two true cases, in detail

**CRASH-017 is the case the brief warns about, and the warning is correct.** The reproducer's own
comment describes the **4.0.2** shape, `emalloc(3 * len + 1)` with `register int x, y`. Pristine
5.0.0 does **not** have that — `url.c:499` is `str = (unsigned char *) safe_emalloc(3, len, 1);`,
i.e. the `3*len+1` int overflow was already fixed. That is exactly why the corpus row's
`c_file_line` points at `Zend/zend_alloc.c:129 + :148 ... :182` and its `history_status` is
`fixed-by-rewrite`: on 5.0.0 the remaining defect **is** the allocator.

Chain, verified: `len = 1431655765` → `_safe_emalloc(3, 1431655765, 1)` computes
`3*len+1 = 4294967296` in 64-bit `long`, which passes both `< LONG_MAX` tests → `_emalloc(2^32)`
→ `real_size = (2^32 + 7) & ~7 = 2^32`, truncated to `unsigned int` = **0** → a header-sized
`malloc` **succeeds** → the encode loop writes ~4.29e9 bytes into it.

**Substituting plain `malloc` during extraction inverts the result.** `malloc(4 GiB)` on a 64-bit
Linux with overcommit succeeds and returns a real 4 GiB block, and the encode loop then runs to
completion with no overflow at all — the defect would be reported as unreachable. This is the
exact failure the brief describes as having already happened once.

**CRASH-097 is a second case, and it is not in the brief.** `streamsfuncs.c:321` is
`read_buf = emalloc(to_read + 1);` with `long to_read` from `zend_parse_parameters(..., "rl|lz", ...)`
and no range check. For a large positive `to_read` near `LONG_MAX`, `to_read + 1` wraps to
`LONG_MIN`, which as `size_t` is `2^63`; `REAL_SIZE(2^63) = 2^63`, truncated to `unsigned int` =
**0**, so a header-sized block is returned and the subsequent `recvfrom` writes into it. Under
plain `malloc`, `malloc(2^63)` fails and PHP exits at `zend_alloc.c:191`. I rejected this row for
a C-side reason (it needs a live socket), but the allocator finding stands and should be recorded
regardless.

**Conclusion for the manager.** Only 2 of the 14 sizing rows depend on the truncation, and neither
is among my 16 candidates. **Every candidate I propose is allocator-independent**, so an
extraction may use any allocator without changing the defect — *provided* it does not also import
CRASH-017 or CRASH-097 later on the strength of that conclusion.

---

## 5. Citations I had to correct against the pristine tarball

**All corrections are in the corpus's *secondary* fields — the `.re` cross-references, the
`root_cause_id` strings, and the `.php` reproducer comments. Every `c_file_line` in the CSV that
I checked resolved exactly.** That is the headline, and it is a good result for the corpus.

### 5.1 `var_unserializer.re` cross-references are off (CRASH-066)
CSV: *"root defect at `var_unserializer.c:243` … + no-op YYFILL at `:106` == `var_unserializer.re:243`/`:111`"*.

| claim | `.c` verified | `.re` claimed | `.re` actual | drift |
|---|---|---|---|---|
| `limit = cursor = *p;` | :243 ✓ | :243 | **:248** | +5 |
| `#define YYFILL(n) do { } while (0)` | :106 ✓ | :111 | **:105** | −6 |

`.re:243` is the `PHPAPI int php_var_unserialize(UNSERIALIZE_PARAMETER)` header; `.re:111` is a
blank line before `/*!re2c`. The `.c` citations are both correct. The **`.c`↔`.re` mapping for
CRASH-120 is exactly right** (`.c:208-210` == `.re:213-215`), so the drift is specific to
CRASH-066.

### 5.2 `root_cause_id` strings carry stale line numbers the CSV then corrects
- `scanf-internal-objindex-offbyone-line738` — the defect is at **:734**
  (`objIndex = varStart + value;`); :738 is a comment. The CSV's `c_file_line` says :734 and is
  right.
- `pack-hH-outsize-overflow-line218` — the defect is at **:247**
  (`outputpos += (arg + 1) / 2;`). The CSV says :247 and is right.

The id strings appear to be 4.0.2-era. Anyone grepping ids rather than `c_file_line` will publish
wrong lines.

### 5.3 The `.php` reproducer comments cite **4.0.2** line numbers and 4.0.2 code
This is systematic, not occasional, and it is the most likely way a wrong citation gets published
— the comments are the most readable thing in the corpus and they are about a different tree.
Every case below: **CSV right, comment wrong for 5.0.0.**

| row | comment says | pristine 5.0.0 | note |
|---|---|---|---|
| CRASH-001 | `formatted_print.c:183`, guard `(*pos + max_width) >= *size` | :190 `req_size = *pos + MAX(min_width, copy_len) + 1;`, guard `req_size > *size` at :192, sink :207 | comment is explicitly labelled "4.0.2 ground truth" |
| CRASH-011 | `:187`, `strncpy` | :211, **`memcpy`** | the call is not `strncpy` in 5.0.0 |
| CRASH-007 | `:993` / `:988`, plain `emalloc` | :1781, **`safe_emalloc`** | changes the analysis: the safe wrapper *is* present in 5.0.0 |
| CRASH-006 | `:1910-1911` / `:2018` | :2946 / :2947, sink :2957 | |
| CRASH-018 | `line 738` / `line 889` | :734 / :893 | |
| **CRASH-017** | `url.c:345`, `emalloc(3 * len + 1)`, `register int x, y` at `:342` | `url.c:499`, **`safe_emalloc(3, len, 1)`**; `register int x, y;` is at :496 | **the important one** — the 4.0.2 int overflow does not exist in 5.0.0; see §4 |

### 5.4 A count the corpus undercounts — **new finding**
The corpus records **two** short entity tables (CRASH-089 `ent_uni_338_402`, CRASH-090
`ent_uni_punct`). I counted every `static entity_table_t` literal against its declared
`entity_map` range. **Four are short:**

```
ent_uni_338_402        actual=63   declared 338..402   needs=65    SHORT by 2   (CRASH-089)
ent_uni_punct          actual=66   declared 8194..8260 needs=67    SHORT by 1   (CRASH-090)
ent_uni_spacing        actual=22   declared 710..732   needs=23    SHORT by 1   NOT IN CORPUS
ent_uni_8592_9002      actual=410  declared 8592..9002 needs=411   SHORT by 1   NOT IN CORPUS
ent_uni_greek          actual=70   declared 913..982   needs=70    ok
ent_uni_8465_8501      actual=37   declared 8465..8501 needs=37    ok
ent_uni_9674           actual=7    declared 9674..9674 needs=7     ok
ent_iso_8859_1         actual=96   declared 160..255   needs=96    ok
ent_cp_1252            actual=32   declared 128..159   needs=32    ok
```

The counter is trustworthy because five of nine tables come out **exactly** right. I confirmed
`ent_uni_spacing` by eye: `html.c:128-136` is `"circ"` + 20 `NULL` + `"tilde"` = 22 entries for a
23-slot range. A build that fixed only the two rows the corpus names would still be defective.

### 5.5 Two over-reads present in the pristine source that the corpus does not record
- `iptc.c:327` — the *find-first-tag* loop tests `buffer[inx+1]` with only `inx < length` in
  scope, so it reads one past the end when `inx == length-1`. This is a third over-read in the
  same function as CRASH-094, and any extraction of the scan loop will import it silently.
- `string.c:3575` and `:3580` — `nl2br`'s counting pass peeks `*(str+1)` with only `str < end`
  in scope. **This one is a near-miss, not a defect**: a PHP zval string is NUL-terminated, so
  the peek lands on the terminator, inside the allocation. I record it because an extraction that
  drops the terminator turns a benign peek into a real over-read and would misattribute it to
  CRASH-106.

### 5.6 One internal inconsistency, not a citation error
CRASH-115's `root_cause_id` is `uudecode-decode-loop-writes-past-emalloc-on-short-line` and its
`cwe` is **CWE-125** (read). Both happen: the loop at `uuencode.c:143-148` reads
`*(s+1)`/`*(s+2)`/`*(s+3)` past `e` **and** writes three bytes per iteration through an unbounded
`p`. Under ASan the write fires first on most inputs. An extraction must not silently pick one.

---

## 6. The pointer-cursor question

The census asked for the pointer-offset walk — `*(p+2)`, `p += n`, a cursor advanced and
dereferenced rather than an index compared against a length — reported as present in all 22
programs and absent from all 33 existing kernels.

**It is abundant in PHP 5.0.0's parsers, and 8 of my 16 candidates carry it.** Mechanical count
per enclosing function (pointer-deref-with-offset-or-advance forms vs `arr[i]` forms, comments
stripped):

| function | candidate | `*p±n`/`*p++`/`*++p` | `arr[i]` | call |
|---|---|--:|--:|---|
| `php_uudecode` | 2 | **17** | 0 | ptr-cursor |
| `nl2br` | (rejected, F2) | **13** | 0 | ptr-cursor |
| `php_var_unserialize` lexer | 1 | **7** | 0 | ptr-cursor |
| `php_convert_to_decimal` | 12 | 6 | 10 | mixed → called true |
| `php_url_parse_ex` | 3, 7 | **5** | 2 | ptr-cursor |
| `php_strspn`/`php_strcspn` | 6 | 2 | 0 | ptr-cursor |
| `php_ereg_replace` | (rejected) | 2 | 20 | mixed |
| `wordwrap` | (rejected, F2) | 1 | 6 | mixed |
| `php_char_to_str_ex` | 8 | 1 | 0 | ptr-cursor (5 declared cursors) |
| `php_chunk_split` | 9 | 0 (5 `p +=`/`q +=`) | 0 | ptr-cursor |
| `get_next_char` | (rejected) | 0 | 8 | index |
| `php_iptc_parse` | 14 | 0 | 13 | index |
| `php_formatted_print` | 11 | 0 | 31 | index |
| `php_sprintf_appendstring` | 4 | 0 | 0 | neither (`(*buffer)[(*pos)++]`) |
| `metaphone` | 13 | 0 | 0 | neither (`(*phoned_word)[p_idx]`) |
| `zend_isset_isempty_dim` | 5 | 0 | 0 | neither (one `buf[i]`) |

Caveats on the count, so it is not over-read: the regex only counts `*(p ± n)`, `*p++`, `*++p`,
`*--p`, `*p--`; it does **not** count `p += n` (too many false positives on integers), so
`php_chunk_split` scores 0 despite being pure pointer arithmetic — its five `p +=`/`q +=`
statements were counted by hand. The 0/0 rows are genuinely neither family and I classified them
by reading. `php_convert_to_decimal` is the one call I would most expect to be argued with: its
address-of-index forms (`&cvt_buf[NDIG]`, `p1 <= &cvt_buf[0]`) outnumber its derefs, but the
walk itself is `*--p1` and `*p++ = *p1++` between two converging cursors, and the defect is
pointer arithmetic (`p1 += mvl` past the end). I called it true; the manager may reasonably
call it mixed.

**The three highest-value pointer-cursor rows, in order:** `php_uudecode` (densest walk, four
cursors, no index variable at all, both an over-read and an over-write from one wrong bound);
`php_var_unserialize` (the limit variable is set to the wrong end and the correct end sits unread
in a parameter — the purest statement of "the bound exists and nobody looks at it"); and
`php_url_parse_ex` (the literal `*(e+2)` / `*(e+3)` / `*(e+5)` spelling the census names, plus a
second, different pointer/length desync eleven lines away).

---

## 7. Things I did not do

- I did not build or run PHP 5.0.0. Every claim here is from reading the pristine source and the
  corpus's own metadata; nothing was confirmed by execution. Where the corpus says
  `crashes_pristine_5_0_0`, I have propagated its value and not re-verified it.
- I did not open `.temp/san_tests/` (the 123 ASan reports on real traffic). My `hotness` fields
  are reasoned from where the function sits on the request path, not measured. **Anything I
  marked "hot" should be checked against that census before it is reported as frequency
  evidence.** The candidates whose hotness claim matters most are 4 (sprintf), 10 (htmlspecialchars),
  12 (double→string), 5 (`isset`/`empty` opcode) and 3/7 (parse_url).
- I did not read `php-rust/`, per the brief.
