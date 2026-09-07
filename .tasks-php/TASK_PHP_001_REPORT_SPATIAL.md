# TASK_PHP_001_REPORT_SPATIAL — the SPATIAL axis mining report

**Agent:** research engineer (read-only). **Status:** delivered, **NOT REVIEWED**.
**Evidence:** `.tasks-php/TASK_PHP_001_MINE/spatial/{candidates.json,NOTES.md,VERIFY.md}`
— promoted out of gitignored `.temp/`.

> ⚠ **`PROTOCOL.md` rule 9: nothing here goes into `.memory-php/` until a review
> lands.** ✅ marks the three things the manager re-derived itself. Nothing else
> carries one.

## Delivered

**16 candidates over 18 corpus rows**, nine mechanism families, all 20 required
keys present. ✅ Manager-verified from the artefact: `16 candidates`,
**`ptr_cursor: true` on 8**, `emalloc_dependent: true` on **0**.

## ⚠⚠ THE MANAGER'S NAMED CLAIM WAS REFUTED — RIGHT ABOUT DENSITY, WRONG ABOUT THE CONCLUSION

`TASK_PHP_001` asked the agent to attack: *"`formatted_print.c` is the densest
site (four root causes in one function) and therefore the best spatial
candidate."*

- ✅ **Densest file: upheld.** 4.46 spatial causes/KLOC over 896 lines, against
  `url.c` 3.05, `html.c` 2.32, `string.c` 1.46 — and the only file whose causes
  are *all* spatial (4/4).
- ⚠ **"one function" is wrong: they sit in THREE.** `php_convert_to_decimal`
  (`:96`), `php_sprintf_appendstring` (`:190` **and** `:211`),
  `php_formatted_print` (`:599`) — four genuinely distinct mechanisms.
- ⚠ **"too tangled" was also wrong**, in the other direction: the 400-line
  driver is needed by none of them; all four rate `verbatim`.
- ⚠⚠ **But it is NOT the best spatial candidate, and the reason is the thing the
  manager asked for in the first place.** Mechanical count over
  `php_formatted_print`: **0 pointer-offset derefs, 31 `arr[i]`.** Three of the
  four are index-family. **For the shape the census says is missing,
  `formatted_print.c` is close to the worst place in the corpus.**

The agent's top 3 instead: `var_unserializer.c`, `uuencode.c`, `url.c`.

## The pointer-cursor finds (`DP-07`)

Agent-reported, manager **not** independently re-derived except where marked:

- **`php_var_unserialize`** — `#define YYFILL(n) do { } while (0)` (`:106`) and
  `limit = cursor = *p;` (`:243`): **the limit is set to the start.** `grep -n
  'max'` over the whole file returns **4 hits** — a declaration, a passthrough
  macro, two recursive calls. **The true end is a parameter and never appears on
  either side of a comparison.** 7 pointer derefs, 0 index forms.
- **`php_uudecode`** — the densest walk in the set: **17** `*(s+1)` / `*(s+2)` /
  `*(s+3)` / `*p++` forms, 0 index forms, and
  `ee = s + (len == 45 ? 60 : floor(len*1.33))` — **the loop bound comes from a
  length byte inside the data**, not from `e`.
- **`url.c:132`** — the census idiom literally: `*(e+2)`, `*(e+3)`, `*(e+5)`,
  with `ue = s + length` computed at `:94` and **never read in the whole block**.

## ✅✅ THE PROGRAMME-LEVEL FINDING, MANAGER-RE-DERIVED

**The corpus's reproducer `.php` comments describe PHP 4.0.2, not 5.0.0 — and
following one would have inverted a verdict.**

✅ Verified by the manager directly. `CRASH-017.php`'s comment reads:

```
 * php-4.0.2:ext/standard/url.c:345:  str = emalloc(3 * len + 1);   // int arith
```

— it **self-labels as 4.0.2**. Pristine 5.0.0 `ext/standard/url.c:499` is:

```c
	str = (unsigned char *) safe_emalloc(3, len, 1);
```

**The `int` overflow is already fixed at 5.0.0.** What remains is the
*allocator*, which is why the CSV points at `zend_alloc.c` and not at `url.c`.
⚠ **Substituting plain `malloc` inverts the verdict**: `malloc(4 GiB)` succeeds
under overcommit and the defect vanishes. This is `PLAN_PHP.md` §4.3 firing
before a single kernel was extracted.

⚠ **It is systematic, not occasional: six reproducer comments cite 4.0.2**
(CRASH-001, -006, -007, -011, -017, -018). CRASH-007's says plain `emalloc`;
5.0.0 is `safe_emalloc`.

✅ **The good half, and it is what makes the corpus usable: every CSV
`c_file_line` the agent checked resolved EXACTLY.** The drift is entirely in the
comments and in two `root_cause_id` strings (`…line738` → really `:734`;
`…line218` → really `:247`).

**→ Landed as a rule in `PLAN_PHP.md` §1: the CSV `c_file_line` is authoritative;
the reproducer comment is NOT a citation.**

## ✅ The allocator, re-derived — and a SECOND truncation the brief did not know about

✅ Verified in the pristine tarball:

```
Zend/zend_alloc.c:129   unsigned int real_size;
Zend/zend_alloc.c:132   #define REAL_SIZE(size) ((size+7) & ~0x7)
Zend/zend_alloc.h:53    unsigned int size:31;      <-- the SECOND one
```

⚠⚠ **The *recorded* size is a 31-bit bitfield**, a truncation distinct from
`real_size` and absent from `PLAN_PHP.md` §4.3 as first written. And
`_safe_emalloc` checks in 64-bit `long` and **then calls the truncating
`_emalloc`**, so it does not protect against this.

**Answered for all 14 sizing rows: only 2 are allocator-dependent, and neither is
a candidate.** All 16 candidates are allocator-independent. The two exceptions
are CRASH-017 and — not in the brief — **CRASH-097** (`emalloc(to_read + 1)` with
`long to_read` near `LONG_MAX` truncates to 0, a tiny block succeeds, where plain
`malloc(2^63)` would fail).

## Other findings the agent reported

- **The corpus undercounts the `html.c` short tables: it records 2, there are 4.**
  `ent_uni_spacing` (22 entries for 23) and `ent_uni_8592_9002` (410 for 411) are
  also short. The counter is exactly right on 13 of 17 tables, so it is
  trustworthy. ⚠ **A build fixing only CRASH-089/090 would still be defective.**
- Two over-reads present in pristine source that the corpus does **not** record:
  `iptc.c:327` (`buffer[inx+1]` at `inx == length-1`) and `string.c:3575/:3580`.
  ⚠ The latter is a **near-miss only because zvals are NUL-terminated**, so an
  extraction that drops the terminator would **manufacture** a defect and
  misattribute it to CRASH-106. That is `PLAN_PHP.md` §4.2's hazard, named
  before it fired.
- `CRASH-066`'s `.re` cross-references drift by +5 and −6; the `.c` lines are
  right and CRASH-120's `.re` mapping is exact.

## Unsure / not done (the agent's own list)

- ⚠ **PHP was never built or run.** `crashes_pristine_5_0_0` is propagated from
  the corpus, **not re-verified**.
- ⚠⚠ **`.temp/san_tests/` was never opened.** Every `hotness` field is *reasoned
  from request-path position, not measured*, and **must not be quoted as
  frequency evidence** until checked. Matters most for candidates 4, 10, 12, 5, 3/7.
- **The reject most likely to be wrong: CRASH-136 (exif).** A JPEG *is* a flat
  blob and `CharBuf + offset_of_ifd` with only a lower-bound check at `:3072` is
  a clean mechanism; rejected on extraction cost (mutually recursive over a
  4000-line file). ⚠ **If a ~200-line `narrowed` extraction is acceptable it
  belongs in the built set** — and under the C-side-only bar, extraction cost is
  a *tier*, not a kill. **Manager must re-adjudicate this one.**
  Second-closest: CRASH-091 (`get_next_char` has **no length parameter** — the
  bound is not in scope at all) and CRASH-157.
- Candidate 12's `ptr_cursor` is the shakiest call (6 derefs vs 10
  address-of-index forms); mixed is defensible.
- Candidates 3/7 are two mechanisms in **one function** — one extraction, two
  triggers. ⚠ **Do not double-count them as two patterns.**

## Manager's adjudication

**Accepted as an engineer report; not yet authoritative.** ✅ marks cover the
candidate/`ptr_cursor`/`emalloc_dependent` counts recomputed from the artefact,
the CRASH-017 reproducer drift, and the three allocator lines. Nothing else.

**Owed to the review:** the `formatted_print` 0-vs-31 count, the
`var_unserializer` `limit = cursor` claim, the `html.c` 4-not-2 recount, and the
CRASH-136 re-adjudication — ⚠ **which the manager flags now as the most likely
place this axis lost a real row, because the stated reason was extraction cost
and the bar does not permit that as a kill.**
