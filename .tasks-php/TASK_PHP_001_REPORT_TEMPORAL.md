# TASK_PHP_001_REPORT_TEMPORAL — the TEMPORAL axis mining report

**Agent:** research engineer (read-only). **Status:** delivered, **NOT REVIEWED**.
**Evidence:** `.tasks-php/TASK_PHP_001_MINE/temporal/` — `candidates.json`,
`NOTES.md`, `VERIFY.md`, plus the **generators** `mk_candidates.py`,
`extract_src.sh`, `rows.json`, `invmap.json`. Promoted out of gitignored
`.temp/`. The extracted `src/` blob was deleted and is re-derivable from
`extract_src.sh` — *keep the generator, delete the artefact.*

> ⚠ **`PROTOCOL.md` rule 9: nothing here reaches `.memory-php/` until a review
> lands.** ✅ marks what the manager re-derived itself. Nothing else carries one.

## Delivered

**23 ranked candidates covering 85/85 rows. Zero rejections.**

✅ **Manager-recomputed from the artefact:** `23 candidates`, `85 distinct rows
covered`, and the tier tally **11 `verbatim` / 10 `narrowed` / 2 `modelled`** —
`MATCHES: True`.

The only kill available on this axis was C-side duplication, and the agent
applied it as **merging** rather than dropping, with the merged member list and
a `risks` note on every debatable merge. ✅ That is the bar applied correctly.

## ⚠⚠ THE MANAGER'S NAMED CLAIM WAS REFUTED, AND THE MECHANISM OF THE ERROR IS THE FINDING

`TASK_PHP_001` asked the agent to attack: *"the CWE-416 mass in
`zend_execute.c` collapses to 3–5 distinct C mechanisms, most requiring the whole
executor and rating `modelled`."*

- ✅ **Right about `zend_execute.c` itself**: its 14 CWE-416 rows do collapse to
  4 mechanisms + 1 ambiguous row, and 3 of the 4 need executor context.
- ⚠⚠ **Wrong about the axis, and wrong in the expensive direction.** Grouped by
  mechanism the axis is **23 families**, and **nine in ten lift**: 11 `verbatim`,
  10 `narrowed`, only **2 `modelled`**. The manager's prediction would have
  written off the richest axis in the corpus.

⚠⚠⚠ **WHY THE PREDICTION READ PLAUSIBLE, AND THIS IS THE REUSABLE LESSON:
`c_file_line` NAMES THE FAULTING FRAME, NOT THE DEFECT.** The faulting frame is
nearly always executor code; the defect is usually one call down, in a
standalone container. CRASH-002's line is `array.c:1062`; **its mechanism is
`zend_hash.h:88`.**

→ **Landed as a rule in `PLAN_PHP.md` §4.2.** Reading the axis by `c_file_line`
measures where PHP *crashes*, not where it is *wrong*, and the two are not the
same file.

## ✅ The containers, re-derived from the pristine tarball

✅ `Zend/zend_ptr_stack.h:44-49`, verified verbatim:

```c
static inline void zend_ptr_stack_push(zend_ptr_stack *stack, void *ptr)
{
	if (stack->top >= stack->max) {		/* we need to allocate more memory */
		stack->elements = (void **) erealloc(stack->elements, (sizeof(void *) * (stack->max *= 2 )));
		stack->top_element = stack->elements+stack->top;
	}
```

✅ The whole header is **68 lines** (the agent said "60"; the substance — a small
standalone header, no zval, no TSRM — holds, and the number is 68). It carries
**5 rows** (CRASH-155/075/081/083/117). Same shape in the object store
(`zend_objects_API.c:91-94`, CRASH-046) and the opcode array
(`zend_opcode.c:271-272`, CRASH-070).

✅ `Zend/zend_hash.h:88`, verified verbatim: `typedef Bucket* HashPosition;`

## ✅✅ THE AGENT CORRECTED THE MANAGER'S OWN BRIEF — THE "123 ASan REPORTS" FIGURE IS A MISREAD

`TASK_PHP_001` told **all three** agents that `.temp/san_tests/` holds *"123 ASan
reports from ordinary page renders"*. ✅ **Manager-verified: that is wrong.**
`.temp/san_tests/REPORT.md` reads:

```
| ASan, cache ON  |  93 | 5 |  4 |
| ASan, cache OFF | 123 | 7 | 31 |
```

— 123 is the **report count of one curated pass** (18 apps × 8 pages), and the
column beside it says **7 distinct sites**. ✅ The real log population is
`asan-logs/` = **2534 files**. **"7 distinct sites" is the right number for how
many independent defects fire**; 123 is not a census.

⚠ **This is a manager error that reached three task prompts at once**, and it is
`PROTOCOL.md` rule 14's shape exactly — a premise stated as fact in a task file
is one an engineer has no reason to doubt. **Corrected in `PLAN_PHP.md` §1.**

## Hotness — the census refuted the agent's own ranking

490 heap-use-after-free occurrences over 336 of 2534 logs, in four top-frame
shapes:

```
 280  zend_do_fcall_common_helper <- zend_do_fcall_handler <- execute  (freed by _zval_ptr_dtor)
  98  _zval_ptr_dtor <- zend_switch_free_handler <- execute            (freed by _efree)
  70  xbuf_format_converter <- php_error_cb <- zend_error              (freed by zend_register_constant)
  42  memcpy <- xbuf_format_converter <- php_error_cb                  (freed by zend_register_constant)
```

57 % sit in call teardown (its rank 18 / rank 1), 20 % in the switch/foreach temp
free (rank 16), and **the remaining 112 are rank 23 firing on real page renders —
a family the agent had ranked LAST on "error paths are cold". They are not cold.**

## Problems the agent reported

- ⚠⚠ **It retracted a claim of its own**, unprompted: it first wrote that
  CRASH-068's `free(c->name)` was an allocator mismatch, then killed it — every
  `c->name` comes from `zend_strndup`, so libc `free` is correct. Recorded in
  `NOTES.md` §4.3 **because it is the error shape most likely to survive in the
  parts it did not re-check.** That is the disclosure the PAT programme rewards.
- ⚠⚠ **40 of 85 rows are `crashes_pristine_5_0_0 = False`, and mostly that is an
  ALLOCATOR ARTEFACT, not an absent defect.** `zend_alloc.c:39-43` forces the
  size-class cache on in both `#ifdef` arms, and `san_tests/REPORT.md` §2
  measures **63.5 % of PHP's heap traffic never reaching `malloc`.** ⚠ **A C
  kernel on plain `malloc`/`free` will reproduce MORE of these than pristine PHP
  does** — so `crashes_pristine` is not a proxy for "is this a real defect", and
  must not be used as an admission filter. Every candidate's `benign_behaviour`
  therefore folds an `(allocs, frees)` tally into the `u64` **so the defect lands
  in the checksum rather than only in a sanitizer.**
- ⚠ **`EG(garbage)` is `zval *garbage[2]`** (`zend_globals.h:214-215`) with an
  unchecked `EG(garbage)[EG(garbage_ptr)++]`. A faithful rank-16 extraction
  **inherits a SPATIAL overflow inside a temporal kernel.** Flagged, not bounded
  away — **the manager must decide**, because silently bounding it would be
  `PLAN_PHP.md` §4.2's invented-non-defect.
- **Four merges the agent thinks are probably wrong**, flagged for splitting:
  rank 21 (14 CWE-401 rows, ≥4 shapes), rank 8 (breaks `I7` from opposite
  directions — missing vs extra increment), rank 12 (six CWE-562 sites, one
  idiom), rank 23 (CRASH-062 is teardown-ordering and shares only the framing).

## Citations

Every `index.csv` line checked resolves correctly in the pristine tarball. Three
discrepancies, **all outside `index.csv`**, recorded not fixed — chiefly
`input/crash/CRASH-012.php`'s header citing `array.c:1645`, which in pristine is
the `}` of an unrelated function, while `index.csv`'s `:2060` is correct.

⚠ **This is the SAME drift the spatial agent found independently**, from a
different direction. Two agents, two axes, one conclusion: **the CSV is
authoritative; the reproducer `.php` header is not.**

## Unsure / not done (the agent's own list)

- ⚠⚠ **The one admission it wants the manager to make explicitly rather than
  inherit: rank 5 (LOGIC-001).** `zend_hash_del_key_or_index`'s
  `(p->nKeyLength == 0)` left disjunct means a numeric bucket's key is never
  compared, so a colliding string-key delete **destroys an unrelated live
  element**. It produces **no fault — a silent wrong answer.** The agent admitted
  it (the C is correct on benign input and wrong on adversarial input, which is
  the bar) and it is **the best checksum-visible candidate in the set, with the
  allocator entirely out of the picture.** ✅ **Manager: ADMIT.** *"It is a
  silent wrong answer, not a crash"* is a classification, not a defect — the bar
  names that explicitly, and `p29` shipped precisely this shape.
- Rank 15 (CRASH-158) may belong on the **spatial** list — CWE-824 and `I19` put
  it here, but *"erealloc without zeroing the tail"* reads spatial. **Cross-check
  against the spatial miner.**
- CRASH-040 could not be placed cleanly: named mechanism is rank 3/6, exercised
  site is rank 16. Filed under rank 3.
- Did **not** compute the DJBX33A preimage rank 5's fixture needs.
- ⚠ **Cannot attribute the 280 census reports to a line** — the logs are LTO'd
  and stripped, so `zend_do_fcall_common_helper` is a 40-line region, not a site.

## Manager's adjudication

**Accepted as an engineer report; not yet authoritative.** ✅ marks cover the
candidate/row/tier recount, `zend_ptr_stack.h:44-49`, `zend_hash.h:88`, and the
ASan misread. Nothing else.

**Owed to the review:** the four flagged merges, the `EG(garbage)` spatial-limb
decision, the rank-15 axis reassignment, and the hotness attribution.
