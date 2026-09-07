# ADJUDICATION_001 — the manager's adjudication of the `TASK_PHP_001` mining wave

**Status: MANAGER work, UNREVIEWED** (`PROTOCOL.md` rule 9 — none of it reaches
`.memory-php/` until it survives a review). **`TASK_PHP_008` reviews it** while
building `patterns-php/CATALOGUE.md` from it.

Summarised in `RECAP_PHP.md` as findings **F8** (the cost bias in the kills) and
**F9** (the ASan census). This file is the evidence; the RECAP is the pointer.

⚠ **This is a MANAGER decision that REVERSES engineer kills.** Rule 3 applies to
it: the manager wrote the admission bar in `PLAN_PHP.md` §3 *and* is now auditing
how three agents applied it. The reviewer of `TASK_PHP_006` must attack this file
directly.

---

## 0. What I re-derived myself, this session, from the pristine tarball

⚠ **This table is the FIRST pass. §7 adds twelve more rows read at source** —
read the two together before treating anything here as unverified. What remains
on the miners' word alone is marked in place.

| claim | pristine location | ✅ |
|---|---|---|
| CRASH-136's mechanism | `ext/exif/exif.c:3057` (`unsigned exif_value_2a, offset_of_ifd;`), `:3071` (`offset_of_ifd = php_ifd_get32u(CharBuf+4, …)`), `:3072` (`\|\| offset_of_ifd < 0x08`), `:3079` (`… CharBuf+offset_of_ifd, …`) | ✅ |
| the exif extraction-cost claim | `exif_process_IFD_in_JPEG` at `:2992`, `exif_process_IFD_TAG` at `:2706`, file is 4048 lines | ✅ |
| `EG(garbage)` is a fixed 2-slot array with an unchecked bump | `Zend/zend_globals.h:214-215`; `Zend/zend_execute.c:69` `EG(garbage)[EG(garbage_ptr)++] = z;`, drained `:73-77` | ✅ |
| CRASH-008's mechanism | `ext/standard/datetime.c:358-359` `case 'U': size += 10;` | ✅ |
| corpus size and coverage | `vuln-corpus-5.0/index.csv` = **166** rows; candidates mention **123**; **43** uncovered; exactly **1** of those 43 is named in no axis's `NOTES.md` | ✅ |
| CRASH-134's overflowed `byte_count` is used in its own guard | `ext/exif/exif.c:2725` `byte_count = components * php_tiff_bytes_per_format[format];` → `:2731` `if (offset_val+byte_count > IFDlength \|\| value_ptr < dir_entry)`. ⚠ **`offset_val+byte_count` can wrap a second time** | ✅ |
| CRASH-107's guard has a **provably dead disjunct** | `ext/standard/string.c:4119` `int result_len;` · `:4143` `result_len = Z_STRLEN_PP(input_str) * Z_LVAL_PP(mult);` (`int × long` → computed in `long`, **narrowed by the store**) · `:4144` `if (result_len < 1 \|\| result_len > 2147483647)` — the second disjunct **cannot fire for an `int`** | ✅ |
| CRASH-091's bound is not in scope | `ext/standard/html.c:486-490` — `get_next_char(charset, str, newpos, mbseq, mbseqlen)` takes **no length parameter**; `:656` `unsigned char next2_char = str[pos+1];` | ✅ |
| CRASH-096's guard lets zero through | `ext/standard/streamsfuncs.c:1047` `if (max_length < 0)` | ✅ |
| **CRASH-123's whole round trip** | `mbfl/mbfl_convert.h:49` `int cache;` · `filters/mbfilter_htmlent.c:161` `filter->cache = (int)mbfl_malloc(html_enc_buffer_size+1);` · `:169` `mbfl_free((void*)filter->cache);` · `:177` `char *buffer = (char*)filter->cache;` · `:181` `buffer[0] = '&';` | ✅ |

---

## 1. ⚠⚠⚠ THE FINDING: THE KILLS LEAK A COST BIAS, WEARING CRITERION 3'S CLOTHES

**All three miners were scrupulous about the thing the bar warns about.** Each
states in terms that no Rust-side, Verus-side, Miri-side or cost-gradient reason
entered any ranking, and I believe them — the reject tables carry a C-side reason
for every row.

**But the bar has a second failure mode the PAT audit never named, and this
corpus walked into it.** `PLAN_PHP.md` §3 criterion 3 is about the **kernel
shape** — *flat blob in, `u64` out, the shared driver loop*. It is not about how
much C you must carry along. **Extraction cost is a TIER (`verbatim` / `narrowed`
/ `modelled`), and §4 says so.** Yet the spatial reject table's criterion-3
bucket is full of reasons of the form *"the surrounding machinery is the
program"*, *"mutually recursive over a 4000-line file"*, *"needs the class-entry
hash machinery"*, *"the blob would have to encode a backtrace"*.

⚠ **Those are tier assignments written as kills.** The bar does not permit them,
for exactly the reason `CLAUDE.md` rule 6 gives: the bias lives **in the
application of the bar**, not in any one row, so row-level review cannot see it.
It took reading the *reasons* as a set to see it.

⚠⚠ **And the miners' own words refute two of them from inside the same wave:**

- *"the blob would have to encode a backtrace"* (CRASH-157, spatial) — the
  **temporal** miner's rank-20 blob is `0x102 TRACE (walk by descriptor and
  fold)`. A backtrace is blob-encodable; one axis said so while another axis
  killed a row for the opposite claim.
- *"the defect is in the compiled program, not in a computation over a byte
  blob"* (CRASH-055/056, spatial) — the **type** miner admitted `ty#3`
  (`opdata-stride-early-exit`) and `ty#14`
  (`opcode-tag-arithmetic-missing-arm-guard`), whose blob **is** the instruction
  stream, and called `ty#3` *"the one candidate whose original C shape IS the
  pinned kernel shape"*.

### 1b. ⚠⚠ THE CASE THAT SETTLES IT: CRASH-123, KILLED AS *"a whole conversion framework"*

✅ **I read the whole mechanism out of the pristine tarball and it is FIVE
LINES**, spanning one struct field and two functions:

```c
mbfl/mbfl_convert.h:49              int   cache;                                  /* an int */
filters/mbfilter_htmlent.c:161      filter->cache = (int)mbfl_malloc(n+1);        /* ptr -> int : TRUNCATES on 64-bit */
filters/mbfilter_htmlent.c:169      mbfl_free((void*)filter->cache);              /* wild FREE  */
filters/mbfilter_htmlent.c:177      char *buffer = (char*)filter->cache;          /* int -> ptr : sign-extended */
filters/mbfilter_htmlent.c:181      buffer[0] = '&';                              /* wild WRITE */
```

**A heap pointer stored in an `int` field, cast back, then freed and written
through.** It needs no filter chain, no encoding tables and no oniguruma — the
struct reduces to three fields. This is a `verbatim` extraction of ~25 lines that
was priced as a framework, and the corpus gives it **its own invariant**
(`pointer-value-integrity`), the only row in 166 that has one.

⚠ **It is also on the wrong axis**: it was routed to the spatial miner, whose
reject table is where it died, so the **type** miner — the one axis whose bar
would have recognised it instantly — never saw it.

**This is the single most valuable thing the mining wave produced, and it is
only visible because all three agents documented every rejection honestly.** A
wave that had simply reported its 54 winners would have hidden it.

### 1a. The reusable rule, and it is F1's sibling

`RECAP_PHP.md` F1 says **`c_file_line` names the faulting frame, not the
defect**. The exif reject is the same error one level up: the cost was priced at
the frame the defect *flows into* (`exif_process_IFD_in_JPEG`, mutually recursive,
4000 lines) rather than the frame the defect *is in* — `:3071-3079`, which is a
32-bit read, a one-sided compare and a pointer add. **Extraction cost, like the
citation, must be measured at the defect site.**

→ Proposed as the first `.memory-php/` entry once `TASK_PHP_006` is reviewed.

---

## 2. Open items 4, 5, 6, 8 — decided

### Item 4 — CRASH-136 (exif): **ADMIT**, and CRASH-134 with it

✅ Verified above. `offset_of_ifd` is an **unsigned 32-bit value read out of the
image data** at `:3071`, checked at `:3072` **only** for `< 0x08`, and added to
the base at `:3079`. `base + attacker-chosen offset, lower-bounded only` is a
distinct C mechanism: no admitted spatial candidate has it. sp#2's bound also
comes from inside the data but bounds a **loop**; this one is a **jump**.

⚠⚠ **CRASH-134 was rejected in the same table cell for the same impermissible
reason and nobody flagged it** — open item 4 named only CRASH-136. ✅ **Mechanism
verified at source** (§0, §7): `components * php_tiff_bytes_per_format[format]`
overflows **and is then used in the very bound check meant to catch it**
(`:2725 → :2727 → :2731`). A guard defeated by the overflow it exists to detect is
distinct from sp#4 (guard defeated by two *different* attacker integers).
→ **ADMIT both.** Tier: `narrowed`. **The recursion is not needed** — the defect
completes at `:3079`, before the call.

### Item 5 — `EG(garbage)`: **extract faithfully, declare BOTH limbs**

✅ Verified: `zval *garbage[2]` (`zend_globals.h:214-215`) with an unchecked
`EG(garbage)[EG(garbage_ptr)++]` (`zend_execute.c:69`).

**Decision: do not bound it.** Bounding it silently is `PLAN_PHP.md` §4.2's
invented-non-defect, and `CLAUDE.md` rule 6 forbids removing a limb for a
ladder-side reason. The te#16 row is admitted for its **temporal** mechanism
(deferred free via a resurrect-and-queue protocol) and **`spec.md` must declare
the spatial limb as a second, real defect of the same C**, with the oracle able
to say which limb fired. ⚠ **Two limbs in one kernel is a REPORTING obligation,
not a reason to split or to trim.**

### Item 6 — the four flagged temporal merges: **SPLIT three, KEEP one**

`PLAN_PHP.md` §3.1: only **exact** C-side duplication is a kill; a slight
variation is its own row.

| merge | decision | reason |
|---|---|---|
| **rank 21** (14 CWE-401 rows) | **SPLIT into the 4 named shapes** | the miner itself names four distinct C shapes; one `I6` invariant over four shapes is a taxonomy, not a mechanism |
| **rank 8** (5 rows) | **SPLIT into 2** | `I7/O1` missing increment (CRASH-131) vs `I7/O2` unmatched decrement (047/099/103/080) break one invariant from **opposite directions** — different C |
| **rank 23** (3 rows) | **SPLIT CRASH-062 out** | the miner calls it *"the weakest merge in this set"*; teardown-ordering shares only the error-handler framing |
| **rank 12** (6 CWE-562 rows) | **KEEP FIVE as one row; SPLIT CRASH-139 out** | ⚠ **corrected after reading all six** — see below |

⚠⚠ **The rank-12 call, re-decided after actually reading the six sites.** I had
kept all six on the strength of the miner's one-line description, and named that
as least-sure call #2. Reading them moves it:

| row | pristine | the idiom |
|---|---|---|
| CRASH-027 | `zend_execute_API.c:881` `zval class_name, *class_name_ptr = &class_name;` | stack zval → userland `__autoload` |
| CRASH-032 | `zend_objects.c:34` `zval zobj, *obj = &zobj;` | stack zval → userland dtor **as `$this`** |
| CRASH-051 | `zend_object_handlers.c:524` `zval method_name, method_args, __call_name;` | stack zvals → `__call` |
| CRASH-052 | `zend_execute.c:1138` `zval tmp;` → `:1146-1149` `offset = &tmp;` | stack zval → `__get` |
| CRASH-100 | `streamsfuncs.c:728` | stack zvals → userland notifier |
| **CRASH-139** | `zend_API.c:1957` `zval property;` · **`ZVAL_STRINGL(&property, name, name_length, 0)`** · `:1966` `read_property(object, &property, …)` | ⚠ **NOT the same defect** |

✅ **Five are one idiom** — `zval local; publish(&local); run userland; return` —
and stay one kernel with five `root_cause_ids`.

⚠ **CRASH-139 is a different mechanism and the corpus already says so: its CWE is
590, not 562.** The `dup=0` argument makes `property.value.str.val` alias a
**caller-owned literal**; the harm is that userland's argument stack later
**frees a pointer that was never an allocator return**. That is te#14's
provenance family (`engine-owned-table-adopted-and-then-freed`), not a
stack-escape. → **split out, route to te#14's family.**

⚠ **This is my own least-sure call #2 closing against me**, and it is the second
time in this adjudication that reading the source moved the answer. Both times
the miner's prose was accurate and my *use* of it was not.

### Item 8 — rank 15 (CRASH-158): **neither spatial nor temporal — it is INITIALISATION**

Both miners were reaching for the wrong pair. The read is **in bounds** (inside
the reallocated block) and **nothing is freed** — so it is neither. Its `CWE-824`
and the project's own `I3 — initialised before read` put it with `ty#10`,
`ty#11`, `ty#15`, all on the **type** axis.

⚠ **And the reassignment turns up a better finding than the routing does.**
CRASH-158 and `sp#10` (`entity-table-declared-range-exceeds-literal`) are **the
same C shape** — *a count declared in one place, an extent realised in another,
with no compiler or runtime relation between them.* They differ only in the
storage:

| | storage | the excess is | class |
|---|---|---|---|
| `sp#10` | static, sized to the **literal** | past the end of the object | **spatial** (CWE-125) |
| CRASH-158 | heap, grown to the **count** | inside the allocation, never written | **initialisation** (CWE-824) |

**One C shape, two vulnerability classes, decided by which of the two numbers the
storage was sized from.** That is a paper-level observation and it is exactly
what a cross-axis catalogue is for. → both rows carry `echoes` at each other.

⚠ `CLAUDE.md` rule 6 names *"the bug is in-bounds so it's logical, not temporal"*
as a finding and never a kill. This is a **classification**, not a kill: the row
is admitted either way.

---

## 3. The rejection audit — 43 uncovered rows, re-adjudicated

✅ Measured: the corpus is **166** rows; the 54 candidates mention **123**; **43**
are covered by no candidate.

### 3a. ⚠ ONE row was dropped with no reason recorded anywhere: **CRASH-008**

✅ Measured — of the 43, exactly one is named in **no** axis's `NOTES.md`. It is
`CRASH-008`, `datetime.c:359`, corpus confidence **high**.

✅ Verified in the pristine tarball: the sizing pass is a `switch` over the format
string adding a **hard-coded constant per conversion character**, and
`:358-359` is `case 'U': size += 10;` — ten bytes reserved for a value the emit
pass then `sprintf`s as a `%ld` of a 64-bit `time_t`.

**ADMIT.** The mechanism is *"a constant reserve that is simply too small for
what the second pass formats"* — **no arithmetic overflow at all**, which makes
it distinct from every sizing candidate in the set (sp#4 wrap-defeats-guard,
sp#8/sp#9 int product wrap, sp#13 one-byte slack lost in a grow path). Kernel
shape is excellent and `verbatim`: blob = format bytes + timestamp, two passes,
checksum the output.

⚠ **42 of 43 carry a recorded reason. That is a good rigour result and I want it
recorded as such** — the silent-skip class this project has found ten times fired
**once** here, not systematically.

### 3b. Kills UPHELD (the C program genuinely fails criterion 1 or 3)

| row | reason, as corrected |
|---|---|
| CRASH-097 | the defective quantity comes from a **socket**; there is no benign pure computation. ⚠ Keep as **evidence for §4.3** — one of only two rows where the `_emalloc` truncation is load-bearing |
| CRASH-098 | needs `RLIMIT_NOFILE > ~1200` and real file descriptors |
| CRASH-147 | ⚠ **reason corrected.** Not *"a bad micro-benchmark"* (that is a cost reason and impermissible) but: the adversarial input is **irreducibly ~2 GiB**, so it cannot be carried by the blob path at all. That is criterion 3, C-side |
| CRASH-133, CRASH-135 | the defect lives inside a bignum / calendar library the corpus does not otherwise touch; a model would be a different program |
| the "ordinary null-deref" set (CRASH-061, 082, 088, 126, 163, 021) | mechanism-quality judgement on the C, which the bar permits |

### 3c. Kills REVERSED — cost or intra-php duplication, neither of which is a kill

**Tier, not filter.** Each goes to `TASK_PHP_006` for cataloguing at the stated
tier; none is pre-approved for building.

| row | miner's stated reason | why it does not hold | tier |
|---|---|---|---|
| **CRASH-134, CRASH-136** exif | extraction cost | §2 item 4 | `narrowed` |
| **CRASH-091** get_next_char | *"cand. 14 already carries reads-k-ahead"* | intra-php near-dup; **the miner's own next sentence** says *"the 'bound is not a parameter' framing is distinct from both"*. §3.1 admits a variation. ✅ **Verified: `html.c:486-490`'s signature really has no length parameter** — the bound is not merely unchecked, it is **not in scope** | `narrowed` |
| **CRASH-157** | *"the blob would have to encode a backtrace"* | refuted by te#20's own blob (§1) | `narrowed` |
| **CRASH-055, CRASH-056** | *"the defect is in the compiled program, not a computation over a blob"* | refuted by ty#3 / ty#14 (§1). ⚠ CRASH-056's *"requires writable /tmp"* is a property of the **reproducer**, not of the kernel | `narrowed` |
| **CRASH-123** mbfilter_htmlent | *"the machinery is a whole conversion framework"* | ✅ **refuted by reading it — §1b. The mechanism is FIVE LINES** and needs none of the framework. Route to the **type** axis | ⚠ `verbatim`, not `narrowed` |
| **CRASH-130** pcre | *"needs PCRE's name table"* | cost; the miner adds *"small enough to model, and I would promote it over CRASH-009"*. `0xff *` where `0x100 *` was meant, on a **signed char** | `modelled` |
| **CRASH-018, CRASH-019** scanf | *"modelling zvals faithfully"* | cost. Two passes computing one index differently (`value - 1` at `:383` vs `varStart + value` at `:734`) with **no bound check in the execute pass** | `narrowed` |
| **CRASH-014** pack | *"an F2 duplicate"* | intra-php dup; the miner calls it *"the corpus's cleanest two-pass sizing mismatch"* with the passes 60 lines apart. §3.1 | `verbatim` |
| **CRASH-107** str_repeat | *"duplicate of cand. 8"* | ✅ **verified, and it is sharper than the miner said.** `int result_len` (`:4119`) takes an `int × long` product computed in **64-bit** and narrowed **by the store** (`:4143`); the guard `result_len < 1 \|\| result_len > 2147483647` (`:4144`) then has a **provably dead second disjunct** — an `int` can never exceed `INT_MAX`. *A guard killed by the type of the variable it tests* is not sp#8's wrap-in-an-expression | `verbatim` |
| **CRASH-120** unserialize `+2` | *"merged into cand. 1"* | miner: *"the sink is different from candidate 1's"*. Blind fixed advance vs unbounded lexer | `narrowed` |
| **CRASH-028** | *"duplicate of ty#14, different arm"* | §3.1 — a different arm of a guard-replication defect **is** the slight variation the rule admits | `narrowed` |
| **CRASH-053** | *"too entangled with the compound-assign machinery"* | cost. ⚠ Note the miner **corrected the corpus** here: `:1632` **is** followed by a type check at `:1635`, so the `root_cause_id` is misleading. Re-adjudicate on the real mechanism, not the label | `modelled` |
| **LOGIC-017** | *"family E duplicate"* | miner: *"if the manager wants a second write-side row, take LOGIC-017"* — it **forces** `is_ref` onto a caller's by-value slot rather than failing to separate. Opposite direction, §3.1 | `narrowed` |
| **CRASH-033, CRASH-005, CRASH-009** | cost / *"the generator owns the table"* | cost. ⚠ CRASH-005's reason is also refuted by sp#10, which is **also** a static-table row and was admitted with a blob that selects which table rows to walk | `modelled` |

### 3d. Rows that fell BETWEEN axes — routed, but nobody caught them

⚠ **A routing decision is not a kill, and it is not a delivery either.** These
were routed away by one miner and never picked up:

| row | routed by | to | picked up? |
|---|---|---|---|
| **CRASH-096** | type (*"a range-guard boundary — route to spatial"*) | spatial | ❌ **no** — appears in no spatial candidate and in no spatial reject table. ⚠ **but see below** |
| **CRASH-077** range() | spatial (*"a value-model/ownership property, not a spatial one"*) | type/temporal | ❌ **no** |
| **CRASH-034** | type (*"temporal axis"*) | temporal | ❌ **no** |
| CRASH-029, CRASH-071 | type | temporal | ❌ no |

✅ **CRASH-096 re-derived by me**: `streamsfuncs.c:1047` really is
`if (max_length < 0)`, so **zero passes**. ⚠ **But I am NOT admitting it here.**
The value then goes to `php_stream_get_record(stream, max_length, …)` at `:1054`
— i.e. the defect lands **inside the stream layer**, which is where CRASH-097 and
CRASH-098 legitimately died on criterion 3. **`TASK_PHP_006` must decide whether
the harmful step is expressible as a pure computation over a blob**; if it is
not, this is an *upheld* kill and the finding is only that no one had checked.
The other four go to `TASK_PHP_006` for adjudication.

⚠⚠ **The lesson is structural, not per-row: three parallel miners with an axis
each will drop whatever sits on a boundary, and each will have behaved
correctly.** Fixing this needs a reconciliation pass that the wave did not have
and `TASK_PHP_006` now is.

---

## 4. Type-axis groupings — decided

| question | decision | reason |
|---|---|---|
| **#4 / #13** (`HASH_OF` misused in opposite directions) | **ONE row, two limbs** | one kernel — the laundering helper plus two call sites. Two rows would **double-count the ladder cost**, which is paid once. Both cited; the pairing is the finding |
| **#5 / #11** (both from CRASH-153) | **SPLIT confirmed — two rows** | distinct C mechanisms and distinct obligations, and #11's kernel does not need re-entrancy at all. §3.1 |
| **#8 vs #1** | keep both; **pin the useless null-check as mandatory in #8's `spec.md`** | #8's distinctness rests entirely on the presence-check plus a null-check that cannot help. If the extraction drops it, #8 **is** #1 |
| **#9 vs #1/#8** | keep | the container/element split is its own C mechanism |
| **sp#3 / sp#7** (both `php_url_parse_ex`) | **ONE row, two triggers** | same extracted kernel; the miner's own warning is against double-counting one kernel as two patterns. Cost is paid once |
| **sp#8 / sp#9** | keep both | different arithmetic **and** different allocator entry points (`emalloc` vs `safe_emalloc`) |

---

## 5. What this does to the corpus size

Nothing here is a build order. It is an **admission** decision; `TASK_PHP_006`
turns it into a catalogue with a provenance block per row, and a reviewer attacks
both.

| | rows |
|---|---|
| candidates delivered by the wave | 54 |
| **+** splits ordered (§2 item 6: rank 21 → 4, rank 8 → 2, rank 23 → 2, **rank 12 → 2**; ty #5/#11 already split) | **+6** |
| **−** merges ordered (#4/#13, sp#3/sp#7) | **−2** |
| **+** kills reversed (§3c) | **+17** |
| **+** dropped with no reason (§3a) | **+1** |
| **+** fell between axes (§3d) | **+4**, and **+1 conditional** (CRASH-096) |
| **≈ catalogue size to adjudicate** | **≈ 80** |

⚠ **`≈80` is a CATALOGUE size, not a build target.** `PLAN_PHP.md` §8's phases
build a small number of rows; the catalogue's job is to be the complete, honest
account of what the corpus offers so the choice of what to build is visible and
defensible. The PAT programme's `.memory/06-catalogue.md` carries 48 rows against
33 built, and that ratio is the healthy one.

---

## 6. The calls I am least sure of

1. ⚠⚠ **§1 is an audit of how three agents applied a bar I wrote.** If the
   distinction between *"criterion 3: does not fit the kernel shape"* and
   *"extraction cost, which is a tier"* is not as crisp as I have made it, then
   several §3c reversals are wrong and I have inflated the catalogue by ~17 rows.
   **This is the thing to attack first.**
2. ✅ **CLOSED — and it closed against me.** The rank-12 keep is now read at
   source: five sites are one idiom, **CRASH-139 is not** and splits out (§2).
   ⚠ The remaining overrule is the **#4/#13 MERGE**, which I have *not* read at
   source and which points the other way — I am merging where a miner wanted two.
3. ⚠ **The CRASH-158 → type reassignment (§2 item 8)** invents a third answer
   where two agents offered two. The `sp#10` pairing is what convinces me, and
   that pairing is my own reading of two candidate descriptions, **not measured**.

5. ⚠ **§8c point 4 — *"a corpus built by reading the source finds what a
   sanitizer on real traffic does not"* — is a RHETORICAL claim, not a
   measurement.** What I measured is that the census's spatial mass is not in
   `Zend/` or `ext/standard/`. That the *reading* approach finds more is the
   thing this programme is supposed to demonstrate, and it has not demonstrated
   it yet — **no php row is built.** Do not let it into the report as evidence
   until rows exist.
4. ⚠ I have re-derived **eleven** things in the pristine tarball (§0) and taken
   everything else on the miners' word. The `≈80` therefore still rests mostly on
   unverified descriptions. `TASK_PHP_006`'s first job is to check every citation
   it catalogues.

⚠ **I named a sampling bias here and then removed it rather than declaring it.**
§3c's rows are no longer argued from the miners' prose — see §7. Twelve of
fourteen are now read in the pristine source; two are unresolved and say so.

---

## 7. §3c re-checked AT SOURCE — 12 of 14 refute their own kill

I said in §6 that §3c rested on the miners' prose. It no longer does. Each row
below was opened in the pristine tarball and asked **one** question: *does a
faithful kernel of the DEFECT need the machinery the rejection cited?*

| row | pristine evidence | machinery really needed? | tier |
|---|---|---|---|
| **CRASH-123** | `mbfl_convert.h:49` + `mbfilter_htmlent.c:161/169/177/181` | ❌ **5 lines** — §1b | `verbatim` |
| **CRASH-136** | `exif.c:3071/3072/3079` | ❌ completes **before** the recursive call | `narrowed` |
| **CRASH-134** | `exif.c:2725` → `:2731` `if (offset_val+byte_count > IFDlength …)` | ❌ one multiply, one compare. ⚠ **two** wraps in one guard | `narrowed` |
| **CRASH-157** | `zend_exceptions.c:310` `emalloc(len + MAX_LENGTH_OF_LONG + 2 + 1)` · `:311` `sprintf(s_tmp, "%s(%ld): ", …)` | ❌ the format's literals are `(`,`)`,`:`,` ` = **4**; the budget reserves **2**. A string, a long, an emalloc, a sprintf. **The backtrace is the CALLER** — F1 again | `verbatim` |
| **CRASH-130** | `php_pcre.c:448` `name_idx = 0xff * name_table[0] + name_table[1];` · `:449` `subpat_names[name_idx] = name_table + 2;` | ❌ **the name table is exactly what a blob supplies.** `0xff` where `0x100` was meant | `verbatim` |
| **CRASH-107** | `string.c:4119/4143/4144` | ❌ — and the guard's 2nd disjunct is **dead by typing** | `verbatim` |
| **CRASH-014** | `pack.c:247` `outputpos += (arg + 1) / 2;` → `:304` `emalloc` → `:309+` emit | ❌ two loops over one formatcodes array | `verbatim` |
| **CRASH-120** | `var_unserializer.c:208` `parse_iv2((*p) + 2, p)` · `:210` `(*p) += 2;` | ❌ a byte blob and a cursor; `object_init_ex` degenerates to a no-op | `narrowed` |
| **CRASH-018/019** | `scanf.c:383` `objIndex = value - 1;` **+ bound check** vs `:734` `objIndex = varStart + value;` **no check**; `:893` `current = args[objIndex++]` then write through `*current` | ❌ ⚠ **the rejection's premise is wrong**: `args` is an array of *pointers*. `struct { int len; char *p; }` preserves the defect exactly — *"modelling zvals"* is not required | `narrowed` |
| **CRASH-055** | `zend_compile.c:1455` — `generate_free_switch_expr` returns 0 **without emitting the free** unless the operand is `IS_VAR`/`IS_TMP_VAR` | ❌ an emitter with an operand-kind guard + an executor expecting the free = `ty#3`/`ty#14`'s shape | `narrowed` |
| **CRASH-056** | `zend_execute.c:199-203` — `if (!T(…).var.ptr_ptr) { … PZVAL_UNLOCK(T->str_offset.str); }` | ❌ **a union member selected by a NULL test on a SIBLING member.** ⚠ **This is a TYPE row, not spatial**, and *"requires writable /tmp"* is a property of the reproducer | `narrowed` |
| **LOGIC-017** | `zend_execute_API.c:608-610` — `SEPARATE_ZVAL_IF_NOT_REF(…)` then `(*fci->object_pp)->is_ref = 1;` | ❌ **stamps `is_ref` ON** a caller's slot; `ty#7` **fails to separate**. Opposite direction | `narrowed` |
| **CRASH-028** | `zend_compile.c:3271-3275` — `ZEND_FETCH_ADD_LOCK` added only on the `IS_VAR` arm | ❌ §3.1 variation of `ty#14`: a lock **not taken** vs a guard not replicated | `narrowed` |

**Two I could NOT settle, and I am not claiming them:**

| row | what I found | status |
|---|---|---|
| **CRASH-033** | `zend_object_handlers.c:201` hashes over `Z_STRLEN_P(member)+1` — deliberately including the terminator. ⚠ For an **empty** name that reads `empty_string[0]`, which is **in bounds**, so I cannot see the OOB from these lines; the corpus puts the manifestation at `zend_compile.c:2621` | **unresolved** — `TASK_PHP_006` decides |
| **CRASH-053** | ✅ the type miner's correction of the corpus **is right**: `:1632` *is* followed by `object->type != IS_OBJECT` at `:1635`. The real defect is inside `make_real_object`'s string-offset path | **unresolved** — and the corpus's own `root_cause_id` is misleading, which is a corpus-quality finding to carry |

**CRASH-005** (bison `yycheck`) and **CRASH-009** (ereg_replace) I did not open;
both are `modelled` on any reading and neither changes the count.

⚠⚠ **Result: of the fourteen §3c reversals, twelve are now read at source and
every one of them refutes the machinery claim that killed it.** The two
five-line rows — CRASH-123 and CRASH-157 — are the ones that should be
uncomfortable: both were priced at the cost of the **frame the defect flows
into**, which is `RECAP_PHP.md` F1's error with cost substituted for citation.

---

## 8. Open item 7 — CLOSED by measurement, and the answer is *the check is impossible*

Open item 7 said the spatial axis's `hotness` fields are *"reasoned, not
measured"* and *"must not be quoted as frequency evidence until checked"*.
✅ **I ran the check. It cannot be done, and the reason is worth more than the
answer would have been.**

### 8a. ✅ First, the temporal miner's census is CONFIRMED, exactly

Re-derived from `.temp/san_tests/asan-logs` (2534 files, **3199 reports** — 567
logs hold more than one):

| class | reports | ✅ vs the wave's figure |
|---|---|---|
| heap-buffer-overflow | **2450** | matches the type miner |
| heap-use-after-free | **490** over **336** logs | matches the temporal miner exactly |
| use-after-poison | **189** | matches |
| global-buffer-overflow | **70** | matches |

and its four UAF top-frame shapes re-derive as `280 zend_do_fcall_common_helper`
/ `98 _zval_ptr_dtor` / `42 memcpy` / `56 __interceptor_strlen` — the miner's
`70 xbuf_format_converter` is the same mass read one frame deeper.
⚠ **Note for anyone re-running this: `grep -c` gives DOUBLE these numbers**
(ASan prints each class string twice per report), and a per-*log* count gives
2352/336/140/70. The wave counted **reports**, and reports is right.

### 8b. ⚠⚠⚠ AND THEN: NOT ONE SPATIAL REPORT IN THE CENSUS IS IN PHP CODE

Faulting frame (`#0`) per report:

| class | reports | where it faults |
|---|---|---|
| heap-buffer-overflow | 2450 | **2156 `MemcmpInterceptorCommon`** · **294 `php_pcre_exec`** |
| global-buffer-overflow | 70 | **70 `php_pcre_exec`** |
| heap-use-after-free | 490 | PHP engine — `zend_do_fcall_common_helper`, `_zval_ptr_dtor`, … |
| use-after-poison | 189 | PHP engine — same two |

✅ **The 2156 chain, read out of a sample log:**

```
#0 MemcmpInterceptorCommon   #1 memcmp
#2 my_xml_scan  #3 my_xml_parse  #4 my_parse_charset_xml
#5 my_read_charset_file  #6 init_available_charsets  #7 get_charset_by_csname
        ... all in  libmysqlclient.so.14  (mysql-4.1.15)
```

**That is not PHP. It is a different shared object**, and its XML charset-file
parser accounts for **88 % of every heap-buffer-overflow in the census**.

The other 364 spatial reports are all `php_pcre_exec`, in the PHP binary, reached
`preg_replace_impl → php_replace_in_subject → php_pcre_replace → php_pcre_exec`
— i.e. the **regex matcher** called from `ext/pcre/php_pcre.c`.
⚠ **I could not prove which function that symbol is**: `php_pcre_exec` does not
appear anywhere in 5.0.0's `ext/pcre/` sources (`config.m4` compiles
`pcrelib/pcre.c` unrenamed), so the name comes from the census build's own
configuration, which I cannot see from the tarball. The call chain places it at
the match step, which makes bundled `pcrelib` the strong reading — **but I am
not claiming it.**

⚠⚠ **The claim that does not depend on that, and is airtight: ZERO of the 2520
spatial reports fault in `Zend/` or in `ext/standard/` — the code EVERY ONE of
the 16 spatial candidates is drawn from.** 2156 fault in a different shared
object; 364 fault in the regex matcher. The temporal mass, by contrast, is
genuinely PHP engine code.

### 8c. What follows

1. **Open item 7's action changes from *"go measure them"* to *"the census
   cannot speak to this axis at all"*.** Every spatial `hotness` stays labelled
   **reasoned**, and the census is struck as a possible source of spatial
   frequency evidence rather than left as an open promise.
2. ⚠ `PLAN_PHP.md` §1's corrected *"7 distinct sites"* needs one more clause:
   **most of those sites are not in PHP.** F4 fixed the count; it did not ask
   what the sites were.
3. ⚠ It is **not** the LTO story. The type miner's *"max-LTO, so
   `zend_hash_find` returns zero hits — inlining, not absence"* is true and
   separate. Here the frames resolve fine; **they resolve to another library.**
4. ⭐ **And it is an argument FOR the programme, which is why it belongs in the
   eventual report.** PHP 5.0.0's own spatial defects are real — 166 corpus rows
   and a tarball full of unbounded cursors — yet **ordinary traffic under ASan
   surfaces none of them.** A corpus built by *reading the source* finds what a
   sanitizer on real page renders demonstrably does not. That is the strongest
   available justification for the whole extraction approach, and nobody has
   written it down.
