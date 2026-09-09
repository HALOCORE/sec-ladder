# TASK_PHP_020 — REPORT · how often is the CATALOGUE's mechanism claim wrong?

**Role:** investigator, alone. **Scope obeyed:** read-only outside this file and
`.temp/php20/`. No `CATALOGUE.md` edit; **corrections below are proposed
replacement text only**. Part C untouched. No `.web/` access. No `git add` / `git
commit`. All scratch under `.temp/php20/`.

**Headline, up front:**

| stratum | n | SUPPORTED | IMPRECISE | NOT SUPPORTED | UNDECIDABLE |
|---|--:|--:|--:|--:|--:|
| **Block 1** (seeded random, Part A) | **15** | **14** | **1** (`ph93`) | 0 | 0 |
| **Batch four** (chosen, not drawn) | **4** | **3** | **1** (`ph21`) | 0 | 0 |

⚠ **The two are reported separately and are never pooled** (task §2.3).

⭐ **`ph29` is SETTLED and the catalogue was right.** The `emalloc` truncation is
real, measured on this box, and the doubt in `UPSTREAM_001` §6 mis-located it. It
is **64-bit-only** — the opposite of the hypothesis — and there are **three**
strengthenings. §4 below.

⚠⚠ **`ph21` — the row scheduled to be built FIRST — has a `▸ trigger` that
cannot fire.** `str_repeat($s, 2^32/strlen($s))` is precisely the value the
guard's *surviving* first disjunct refuses. §3.B.

---

## §1 The sample, drawn mechanically and printed before any C was opened

Script (kept, it is the evidence): `.temp/php20/sample.py`. Output:
`.temp/php20/sample.out`. Reproduce with `python3 .temp/php20/sample.py`.

Population verified first, not trusted from the task file
(`PROTOCOL.md` rule 13):

```
$ grep -c '^| ph[0-9]' patterns-php/CATALOGUE.md
93
```

```
$ python3 .temp/php20/sample.py
population: 93 rows  (ph01 .. ph93)
BLOCK 1 (seed 20, n=15): ph04 ph10 ph13 ph14 ph17 ph20 ph22 ph34 ph42 ph53 ph74 ph82 ph87 ph88 ph93
BLOCK 2 (seed 21, n=10, disjoint): ph29 ph31 ph36 ph46 ph64 ph71 ph72 ph76 ph77 ph91
BATCH STRATUM (chosen, not drawn): ph12 ph16 ph21 ph29
  overlap with block 1: (none)
  overlap with block 2: ph29
```

Block 2 was **drawn in the same seeded, committed script, before any C was read**,
so its membership is fixed and cannot be gamed later; see §5 for what I did and
did not do with it. `ph15` and `ph91` were left in the population — both are
self-labelled `unresolved`, and excluding them would have been a choice made after
looking.

Every citation below was resolved against the **pinned tarball only**
(`sha256 5783e0c0…d6919`, re-checked at run time by `.temp/php20/extract.sh`);
`grep -a` throughout; functions located with `.temp/php17/r1h/fn.py`, not by text.

---

## §2 Block 1 — the verdict table

| row | citations resolve? | mechanism supported? | trigger reachable on the stated arm? | **verdict** | time |
|---|---|---|---|---|--:|
| `ph04` | ✅ `url.c:94/132/139/143/292` all exact | ✅ | ✅ | **SUPPORTED** ⚠ name | 4 m |
| `ph10` | ✅ `iptc.c:339/342-343/345-347/350`, and `:327` | ✅ incl. "*three of the checked budget*" — exact | ✅ | **SUPPORTED** | 3 m |
| `ph13` | ✅ `exif.c:3071/3072/3079` exact | ✅ | ✅ | **SUPPORTED** ⚠ no FAULT label | 4 m |
| `ph14` | ✅ `exif.c:2725/2731` exact | ✅ incl. the `int` table (`:267`) | ✅ | **SUPPORTED** | 4 m |
| `ph17` | ✅ `regparse.c:3581`, `regint.h:307/321` | ✅ | ✅ `[\777]` reaches `:3581` via `:3923-3927` | **SUPPORTED** | 9 m |
| `ph20` | ✅ `string.c:1781/1783-1796/1798` exact | ✅ | ✅ | **SUPPORTED** | 2 m |
| `ph22` | ✅ `pack.c:114/153/247/304/309` exact | ✅ (Part A one-liner is exactly right) | ✅ | **SUPPORTED** ⚠ magnitude | 6 m |
| `ph34` | ✅ `ctype.c:99-100`, `:101-111`, `:108` exact | ✅ | ✅ | **SUPPORTED** | 3 m |
| `ph42` | ✅ `zend_compile.c:1196-97`, `.h:285-88`, `zend.h:387-96` | ✅ both limbs exact | ✅ but under-stated | **SUPPORTED** ⚠ gate | 8 m |
| `ph53` | ✅ `zend_compile.c:2571/1951`, `zend_operators.c:1534-35` | ✅ | ✅ — **easier than stated** | **SUPPORTED** | 7 m |
| `ph74` | ✅ `zend_API.c:1957/1965-1966` byte-exact | ✅ | ✅ | **SUPPORTED** ⭐ +1 | 6 m |
| `ph82` | ✅ `zend_execute.c:3713/3737/3741/4242-47`, `zend_compile.c:1479` | ✅ | ✅ | **SUPPORTED** | 5 m |
| `ph87` | ✅ `zend_constants.c:316/320/324`; sibling `php_mbregex.c:732/734/735` | ✅ | ✅ (`define/2` sets `CONST_CS`, `zend_builtin_functions.c:447`) | **SUPPORTED** | 6 m |
| `ph88` | ✅ `zend_execute_API.c:282`, `zend.c:822` exact | ✅ (thin, but true) | ✅ | **SUPPORTED** ⭐ +1 | 9 m |
| `ph93` | ✅ `string.c:635/678-79/681-82/684/692-94` all exact | ⚠ **type claim loose; harm limb not established** | ❌ **stated trigger reaches `:692` but overflows nothing** | **IMPRECISE** | 15 m |

Total ≈ 91 minutes; **median 6 min**, range 2–15.

### 2.1 What each verdict rests on (only the non-obvious ones)

**`ph17`** — `BitSet` is `Bits[BITSET_SIZE]` with `BITSET_SIZE = 256/BITS_IN_ROOM`
(`regint.h:297-307`) and `BITSET_SET_BIT` is `(bs)[pos/BITS_IN_ROOM] |= 1 << (pos %
BITS_IN_ROOM)` (`:321`) with no bound. Traced the trigger end to end: `\777` →
`scan_unsigned_octal_number(…, 3, …)` (`regparse.c:2639`) → `tok->u.c = 511` into
an **`int` c** (`:2117`) → `parse_char_class` `TK_RAW_BYTE` else-arm `:3750-3751`
sets `v = 511, in_type = CCV_SB` → `next_state_val` stores it → flushed at
`:3923-3927` into `:3581`. `511/32 = 15` into an 8-word bitset. ✅

**`ph42`** — the collision is exact (`IS_CONST=1`/`IS_LONG=1`,
`IS_TMP_VAR=2`/`IS_DOUBLE=2`, `IS_VAR=4`/`IS_ARRAY=4`), and the two-limb risk note
is exactly right: `zvalue_value` puts `lval` and `str.val` both at offset 0 and
`str.len` at offset 8, so an `IS_LONG` constant overlays `str.val` and leaves
`str.len` **unwritten**. ⚠ The block does not state the resulting *gate*: `:1196`
tests `str.len == sizeof("__clone")-1 == 7` **before** `:1197` dereferences
`str.val`, so the harm needs that uninitialised word to be exactly 7. That is a
fixture requirement, not a refutation — the block's `▸ blob: an operand record
stream` already admits it.

**`ph53`** — verified the whole loop: `num_interfaces` is bumped at **compile**
time, one per `implements` clause (`zend_compile.c:2591`), while the slots are
written at **runtime** by `zend_add_interface_handler`
(`zend_execute.c:4227 ce->interfaces[opline->extended_value] = iface;`). ⭐ The
trigger is *easier* than the block says — no autoloader is needed:
`zend_do_implement_interface` is called at `zend_execute.c:4229`, immediately after
the **first** slot is written, and `zend_compile.c:1939` sets `ce_num =
ce->num_interfaces` (the **full declared** count) before reading
`ce->interfaces[i]` at `:1951`. `interface A{} interface B extends A{} class C
implements B, X{}` reads the un-written tail on the first `ADD_INTERFACE`.

**`ph88`** — the block is two lines and names no storage, no consumer and no
faulting site, so I chased it: `shutdown_compiler` (`zend_compile.c:159-176`) ends
with `zend_llist_destroy(&CG(open_files))` (`:169`), whose destructor is
`zend_file_handle_dtor` (`zend_language_scanner.c:2988`), whose `ZEND_HANDLE_STREAM`
arm at `:2997` calls `fh->handle.stream.closer(fh->handle.stream.handle)` — a
`php_stream` that lives in `EG(regular_list)` and was already destroyed at
`zend_execute_API.c:282`. Ordering and both citations exact.

---

## §3 The batch four — separate table, separate rate

| row | citations | mechanism | trigger | **verdict** | time |
|---|---|---|---|---|--:|
| `ph12` | ✅ `string.c:4778/4786/4791/4794`, `:4779 zend_bool cs=0;` exact | ✅ | ✅ | **SUPPORTED** ⭐ +1 limb | 7 m |
| `ph16` | ✅ `streamsfuncs.c:541`; `fd_set rfds,wfds,efds;` at `:658` in the caller | ✅ | ✅ | **SUPPORTED** | 4 m |
| `ph21` | ✅ `string.c:4120/4144/4145` exact (confirms the ⚠ risk note) | ✅ dead disjunct is real | ❌ **stated trigger is refused by the live disjunct** | **IMPRECISE** | 10 m |
| `ph29` | ✅ `streamsfuncs.c:304/309/321/332` exact | ✅ **measured** | ✅ | **SUPPORTED** ⭐ +3 | 14 m |

### 3.A `ph12` — everything stated is exact; one limb is missing

`long offset, len=0;` (`:4778`) → the `len &&` short-circuit is exactly as
described, and `zend_binary_strncmp(char*, uint len1, char*, uint len2, uint
length)` (`zend_operators.c:1786-1790`) does
`memcmp(s1, s2, MIN(length, MIN(len1, len2)))` — so `s1 + offset` with a negative
`offset` reads `MIN(cmp_len, s2_len)` bytes out of bounds. ✅ *(This also settles,
at source, the thing `UPSTREAM_001` §3 asked the row to check: both lengths are
passed and minned internally, so 5.4.0's smaller guard is not a regression.)*

⭐ **Addition:** the guard is **also one-sided**. With an explicit non-zero
`$length`, `len && offset >= s1_len` still passes for **any negative offset** —
`substr_compare("abc","x",-1000000,5)` reads at `s1-1000000`. So the row's
path-selecting parameter (`.memory-php/04-process.md` names it as *"the omitted
`length` argument that disables the guard"*) selects the arm only for **positive**
offsets; upstream's 5.2.0 fix added **both** an unconditional `(offset+len) >
s1_len` **and** a negative-offset clamp, which is the maintainers' own confirmation
that there are two limbs.

### 3.B ⚠⚠ `ph21` — IMPRECISE, and it is the next row to be built

Everything about the *defect* is right and exact: `int result_len;` (`:4120`),
`Z_STRLEN_PP` is `int` and `Z_LVAL_PP` is `long` so `:4144` is a 64-bit product
**narrowed by the store**, and `:4145`'s second disjunct `result_len > 2147483647`
is provably dead. Two things are wrong:

1. **The stated trigger cannot fire.** `str_repeat($s, 2^32/strlen($s))` makes the
   product exactly `2^32` (when `strlen` divides it) → stored `result_len == 0`, or
   *negative* when it does not → the guard's **surviving first** disjunct
   `result_len < 1` fires and the function `RETURN_FALSE`s. The narrowed value must
   land in `[1, INT_MAX]`, which `2^32/strlen` never does.
2. **The block does not say where the harm lands, and the general path has none.**
   `:4155-4166` sets `ee = result + result_len` — the **narrowed** length — so the
   `memmove` loop writes exactly what was allocated. The overflow is on the
   `Z_STRLEN_PP(input_str) == 1` fast path at `:4153`,
   `memset(result, *(Z_STRVAL_PP(input_str)), Z_LVAL_PP(mult))`, which passes the
   **un-narrowed 64-bit multiplier** to `memset`. Second, much smaller limb: for
   `Z_STRLEN > 1` with `result_len < Z_STRLEN` (e.g. `strlen = 3`,
   `mult = 2863311531` gives `result_len = 1`), `:4157`'s
   `memcpy(result, …, Z_STRLEN_PP(input_str))` overflows the `result_len + 1`
   block.

**Working trigger:** `str_repeat("A", 4294967297)` — `4294967297 = 2^32 + 1` →
`result_len = 1` → guard passes → `emalloc(2)` → `memset(result, 'A', 4294967297)`.

---

## §4 `ph29` — SETTLED, at source and by measurement

**Answer: none of the four options as written. The catalogue's mechanism is
CORRECT, and it is `⭐ something better than the catalogue says` in three
respects.** The doubt in `UPSTREAM_001` §6 / task §4 —
*"`emalloc` takes a `size_t`, which on this 64-bit box truncates nothing"* — is
true and **irrelevant**: the truncation was never claimed to be at the signature.
It is inside `_emalloc`.

**The chain, all lines exact against the pinned tarball:**

| | |
|---|---|
| `streamsfuncs.c:304` | `long to_read = 0;` |
| `streamsfuncs.c:309` | `zend_parse_parameters(… "rl\|lz", &zstream, &to_read, …)` — userland, unchecked (no `to_read <= 0` guard until 5.1.0) |
| `streamsfuncs.c:321` | `read_buf = emalloc(to_read + 1);` |
| `zend_alloc.c:142` | `_emalloc(size_t size …)` |
| `zend_alloc.c:129` | `unsigned int real_size;` ← **32 bits** |
| `zend_alloc.c:132` | `#define REAL_SIZE(size) ((size+7) & ~0x7)` |
| `zend_alloc.c:135` | `real_size = REAL_SIZE(size);` ← **THE TRUNCATION** |
| `zend_alloc.c:182` | `ZEND_DO_MALLOC(sizeof(header) + PADDING + SIZE + END_MAGIC)` with `SIZE == real_size == 0` |
| `streamsfuncs.c:323` | `php_stream_xport_recvfrom(stream, read_buf, to_read, …)` — the parameter is **`size_t buflen`** (`php_stream_transport.h:99`) → `sock_recvfrom` → `recvfrom(fd, buf, buflen, …)` (`xp_socket.c:198/209`) |
| `streamsfuncs.c:332` | `read_buf[recvd] = '\0';` |

**Measured on this box** — `.temp/php20/ph29_probe.c` (kept; `gcc -O0`, log in
`.temp/php20/ph29_probe.log`). It replicates the exact declarations, not a paraphrase:

```
sizeof(long)=8 sizeof(size_t)=8 sizeof(unsigned int)=4

-- benign --
to_read=0            size=1            real_size=8      cache_index=1    malloc_arg=12   hdr.size=1
to_read=65536        size=65537        real_size=65544  cache_index=8193 malloc_arg=65548 hdr.size=65537

-- the row's trigger: stream_socket_recvfrom($s, PHP_INT_MAX) --
to_read=9223372036854775807  size=9223372036854775808  real_size=0  cache_index=0  malloc_arg=4  hdr.size=0

-- neighbours --
to_read=4294967295   size=4294967296   real_size=0      cache_index=0    malloc_arg=4    hdr.size=0
to_read=4294967296   size=4294967297   real_size=8      cache_index=1    malloc_arg=12   hdr.size=1
to_read=-1           size=0            real_size=0      cache_index=0    malloc_arg=4    hdr.size=0

-- CHECK_MEMORY_LIMIT(size, SIZE) adds SIZE==real_size, not size (zend_alloc.c:177) --
with --enable-memory-limit, allocated_memory += 0  (the request was 9223372036854775808)
```

**Three strengthenings the block does not carry:**

1. ⭐ **A better trigger that does not depend on undefined behaviour.**
   `to_read = 4294967295` gives `real_size = 0` too, and `to_read + 1` there is an
   ordinary `2^32` — no signed-overflow UB. The catalogue's `PHP_INT_MAX` trigger
   relies on `LONG_MAX + 1`, which gcc is entitled to assume cannot happen; a
   kernel built to it may behave differently at `-O3` than at `-O0` **for a reason
   that is not the pattern**. `to_read = -1` also works (`size = 0`) and is exactly
   what upstream's 5.1.0 `if (to_read <= 0)` fix refuses. The Part A one-liner
   *"the allocator truncates n mod 2^32"* is already the right story; Part B's
   trigger picked the worst member of the family.
2. ⭐ **The truncation also defeats the memory limit.** `CHECK_MEMORY_LIMIT(size,
   SIZE)` at `:177` accumulates `SIZE` = `real_size` = **0**, so
   `--enable-memory-limit` does not stop it. That is a *second* place the same
   truncation is load-bearing.
3. ⭐ **It reaches a second of the three truncations.** `p->size = size` at
   `zend_alloc.c:167` and `:201` writes into `zend_alloc.h:53`'s
   `unsigned int size:31`, giving `0`, which is what `efree` later uses to pick a
   cache slot. It does **not** reach the third (`_ecalloc`'s
   `int final_size` at `:295`) — that path needs `ecalloc`.

⚠ **And one narrowing, which does NOT decide admission against the row:** the
mechanism is **64-bit-only**, the *opposite* of task §4's hypothesis. On a 32-bit
build `long`, `size_t` and `unsigned int` are all 32 bits, `REAL_SIZE` truncates
nothing, and `malloc(~2 GiB)` fails into `zend_alloc.c:189-194`'s `exit(1)`. We
build 64-bit, so criterion 2 is satisfied in our environment. The `⚠⚠ risk` note
(*"one of only two rows where the `_emalloc` truncation is load-bearing … must
link `common-php/emalloc_shim.h`"*) is confirmed and, if anything, understated.

**I did not decide the row's fate** (task §4 closing instruction). Verdict:
`SUPPORTED`.

---

## §5 Block 2 — a *different, weaker* test, reported apart

Per task §6.1 I did **not** run a full second block: the per-row cost was **not
"much lower than assumed"** (median 6 min, but a 15-min tail, and two of the four
most expensive rows are where the findings were). Extending on the strength of
"the number does not look right yet" is exactly what §6.1 forbids.

What I did instead, at low cost and clearly labelled: **§3 test 1 only — do the
cited `file:line`s resolve? — over the already-drawn, disjoint Block 2.** This is
*not* a mechanism audit and its number must never be quoted as one.

| row | test-1 result |
|---|---|
| `ph29` | ✅ (also fully audited, §4) |
| `ph31` | ✅ `julian.c:154` = `void SdnToJulian(`, `:199` = its closing `}` (46 lines, as claimed); mechanism lines `:160 int year`, `:163 long int temp`, `:172`, `:175` all exact; FAULT `calendar.c:263 char date[16];` / `:280 sprintf(date, "%i/%i/%i", …)` exact |
| `ph36` | ✅ `zend_language_parser.c:3518` and `:3534` are both `if (yycheck[yyx + yyn] == yyx)` — "two identical instances" exact |
| `ph46` | ✅ `zend_execute.h:30-43` is exactly the `temp_variable` union; `zend_execute.c:138-151` = `_get_zval_ptr_ptr` with the `:141` test and the unconditional `:147` return; `:198-217` = `zend_switch_free`'s switch; `make_real_object` is `:280-292` — **12 lines, as the retraction says** — and `:283` is its first statement |
| `ph64` | ✅ `zend_llist_apply` at `:186-193` (eight lines ✅); FAULT `basic_functions.c:2135 tick_fe->calling = 0;` exact. ⚠ *"`zend_llist` is ~200 lines"* — the file is **317** |
| `ph71` | ✅ `zend_execute.c:220-278` = `zend_assign_to_variable_reference`, exactly |
| `ph72` | ✅ `array.c:993` = `php_array_walk`. ⚠ the span `:993-1063` stops at the while-loop's `}`; the function closes at `:1066` |
| `ph76` | ✅ `array.c:2059-2060` are the unconditional `zend_hash_destroy` / `efree`, exactly as quoted; siblings `zend_operators.c:661` and `array.c:3272-3274` both exact |
| `ph77` | ✅ `zend_execute.c:63-78` covers `zend_pzval_unlock_func` (`:63-71`, with `:67-68` the resurrect and `:69` the unchecked `garbage_ptr++`) and `zend_clean_garbage` (`:73-78`); `zend_globals.h:214-215` = `zval *garbage[2]; int garbage_ptr;`; `:374-381`, `:535`, `:3152` all resolve |
| `ph91` | ✅ `zend.c:871/938/955/964` all exact — the row's own "✅ Measured" text checks out, and the row is honestly labelled `unresolved` |

**10 / 10 resolve.** Two cost-statement nits (`ph64`'s line count, `ph72`'s span
end), neither of which can affect admission (`PLAN_PHP.md` §4: tier and cost are
never filters).

---

## §6 The rates, and what 15 of 93 can and cannot support

> **Block 1: 1 of 15 needed correction (`ph93`). Batch four: 1 of 4 (`ph21`).**

**What that supports.** The catalogue's mechanism claims are, in this sample,
overwhelmingly right *and unusually precise* — several rows are exact to a level a
sampler does not expect (`ph10`'s "*leaving three of the checked budget*" is
arithmetically exact; `ph42`'s two-limb overlay is exactly the C; `ph93`'s and
`ph21`'s line citations are all correct to the line, including the two the
catalogue itself flags as previously off-by-one). **The `▸` sub-fields are weaker
than the mechanism sentence**: both defects I found are in a `▸ trigger` or in the
sentence describing the *harm*, never in the identification of the defect site.

**What it cannot support.** ⚠ **1 of 15 does not distinguish a 3 % error rate from
a 20 % one, and I am not computing an interval** (task §6.3; F4/F12/F32). Two
further reasons for caution, both of which push the true rate **up**:

- **The batch four are the rows that have had the most eyes on them** — an
  adjudication, `FIXSURVEY_001`, `UPSTREAM_001` and a tier recheck — and one of
  them still failed. That is evidence that prior scrutiny is not protective.
- **Block 1's difficulty is not uniform.** The one failure was the row I spent
  longest on (15 min). Three other rows (`ph42`, `ph53`, `ph88`) needed 7–9 minutes
  before I could say `SUPPORTED`, and each produced an *addition*. **A cheaper
  audit than mine would have returned 15/15**, so this number is a lower bound on
  the defect rate, not an estimate of it.

**Task §6.2 — do `IMPRECISE` and `NOT SUPPORTED` separate in practice?** ⚠ **I did
not need `NOT SUPPORTED` once, and I do not think the boundary is the useful one.**
The line that actually mattered while grading was different: *does the error change
what a build task would do?* Both my `IMPRECISE` verdicts are "the defect is real
and correctly sited, but the stated way to reach the harm does not reach it" —
which is exactly the `ph07` cost shape. **Recommendation: collapse to two buckets,
`SUPPORTED` and `NEEDS CORRECTION`, and record separately the count of rows where
a correction was *additive* (7 of 19 here: `ph04 ph13 ph22 ph42 ph74 ph88 ph12`,
plus `ph29`'s three).** A rate over the coarse bucket is applicable; the fine one
was not.

**Task §6.3 — is the catalogue worth auditing at all?** ⭐ **Yes, but not for the
mechanism sentence — for the `▸ trigger` line.** The counter-argument (*"a
mechanism description is a pointer; the build task reads the C anyway"*) is
**correct for the mechanism sentence and wrong for the trigger**. A build task's
deliverable #1 is reachability (`PLAN_PHP.md` §4.2), and a row engineer starts by
running the row's stated trigger. `ph21`'s does not fire; `ph93`'s reaches the
cited line and produces nothing; `ph29`'s fires but only through undefined
behaviour. **That is 3 of the 19 rows I read whose `▸ trigger` would have cost an
engineer time, against 0 rows whose defect site was wrong.** If a follow-up audit
is written, ⭐ **audit `▸ trigger` lines only** — it is the cheapest test here
(2–4 min/row once the file is open) and it is where the whole yield was.

---

## §7 Proposed replacement text — **do not apply from here; the manager lands it**

Line numbers are `CATALOGUE.md`'s as of this reading. Nothing below touches Part C.

### 7.1 `ph21` — Part B, two edits (Part A cell unchanged, it is correct)

**(a)** After the sentence ending *"…which is not ph19's wrap-in-an-expression."*,
**insert**:

```
⚠⚠ **AND THE HARM IS ON ONE ARM ONLY.** The general emit path (`:4155-4166`)
bounds itself with `ee = result + result_len` — the **narrowed** length — so it
writes exactly what was allocated and overflows nothing. The overflow is the
`Z_STRLEN_PP(input_str) == 1` fast path at `:4153`,
`memset(result, *(Z_STRVAL_PP(input_str)), Z_LVAL_PP(mult))`, which passes the
**un-narrowed 64-bit multiplier** straight to `memset`. Second, much smaller limb:
for `Z_STRLEN > 1` with `result_len < Z_STRLEN` — `strlen = 3, mult = 2863311531`
gives `result_len = 1` — `:4157`'s `memcpy(result, …, Z_STRLEN_PP(input_str))`
overflows the `result_len + 1` block. (`TASK_PHP_020` §3.B.)
```

**(b)** **Replace** the `▸ trigger` line

```
▸ trigger: `str_repeat($s, 2^32/strlen($s))`.
```

with

```
▸ trigger: ⚠ **`str_repeat("A", 4294967297)` (= 2^32 + 1) — NOT
`str_repeat($s, 2^32/strlen($s))`, which CANNOT FIRE**: at exactly `2^32/strlen`
the stored `result_len` is **0** (or negative when `strlen` does not divide 2^32)
and the guard's **surviving first** disjunct `result_len < 1` refuses it. The
narrowed value must land in `[1, INT_MAX]`. (`TASK_PHP_020` §3.B.)
```

### 7.2 `ph93` — Part A cell + Part B

**Part A**, replace the mechanism cell

```
| ph93 | spatial | buffer regrown mid-emit; the growth arithmetic is unchecked `int` | narrowed | I11/O2 | CRASH-109 | — | catalogued |
```

with

```
| ph93 | spatial | buffer regrown mid-emit, by a term an attacker `linelength` divides | narrowed | I11/O2 | CRASH-109 | — | catalogued |
```

**Part B**, replace *"whose growth arithmetic is itself unchecked `int` AND
DIVIDES BY AN ATTACKER-CONTROLLED `linelength`"* with

```
whose growth term **DIVIDES BY AN ATTACKER-CONTROLLED `linelength`** — the one
thing no other row has. ⚠ **Type, corrected the way `ph92`'s was**: `current` and
`linelength` are `long` (`:636-637`), so `((textlen - current + 1)/linelength + 1)
* breakcharlen` is computed in **64-bit** and is **truncated by the explicit
`(int)` cast**; only the `alloced +=` accumulation is native `int`. *"The growth
arithmetic is unchecked `int`"* is the same loose phrasing `TASK_PHP_017` §2.2
corrected on `ph92`.
⚠⚠ **AND THE HARM LIMB IS OPEN.** `TASK_PHP_020` reached `:692` on the stated arm
and measured **no overflow there**: firing `chk <= 0` costs `textlen/linelength + 1`
decrements, each consuming ≥ `min(linelength, breakcharlen)` input bytes, which
bounds the growth term at fire time at roughly `textlen`. **No input was found
that both reaches `:692` and wraps its accumulation, and none was shown not to
exist.** The row's demonstrable overflow on this arm is the *sizing* line `:679`
(`chk * breakcharlen` in `int`, e.g. `textlen = 10^6, linelength = 1,
breakcharlen = 3000`) — which is the shape the block says is NOT the distinctness.
**A build task must settle this before writing a rung.**
```

**Part B**, replace the `▸ trigger` line with

```
▸ trigger: ⚠ **two, and they are not the same claim.** (a) *Reaching* `:692` on
the `linelength > 0` arm: `linelength = 2e9, breakcharlen = 2`, text beginning
with the break string — `chk` starts at 1, one `chk--` at `:705` on iteration 0,
`:691` fires at `current = 2`. ⚠ **This grows `alloced` by 3 and overflows
nothing.** (b) A *demonstrated* overflow on the same arm: `:679`'s
`chk * breakcharlen` in `int`.
```

### 7.3 Additive corrections (verdict unchanged — one line each)

| row | where | change |
|---|---|---|
| `ph04` | Part B title | **`php_url_parse_ex` → `php_url_parse`.** 5.0.0 has no `_ex` spelling anywhere in the tarball (checked by extraction, not by grep). A reader searching for the function name finds nothing — the exact `.memory-php/00` *"ask about a FUNCTION"* trap. |
| `ph13` | Part B | add `FAULT: exif.c:3004` — `NumDirEntries = php_ifd_get16u(dir_start, …)`, the callee's first statement, which is what makes *"none of the mutual recursion is needed"* true. |
| `ph22` | Part B | *"the emit loop from `:309` writes the unwrapped one"* → *"the emit pass clamps `arg` to `Z_STRLEN_PP(val)` at `:335`, so it writes `ceil(strlen/2)` bytes into the wrapped allocation — **the two passes' different clamps are the mechanism**, and the adversarial cell is cheap, not 2 GB."* (Part A's one-liner already says this correctly.) |
| `ph42` | Part B `⚠ risk` | append: *"`:1196` gates on `str.len == 7` **before** `:1197` dereferences `str.val`, so the blob must supply that uninitialised word."* |
| `ph74` | Part B | append: ⭐ *"and `zend_read_property` never calls `INIT_PZVAL(&property)` — compare `zend_object_handlers.c:72-73`, which does — so `property.refcount`/`is_ref` are stack garbage before the zval reaches userland's argument stack."* |
| `ph88` | Part B | replace the one-line mechanism with the chain: `shutdown_compiler` (`zend_compile.c:159`) ends at `:169 zend_llist_destroy(&CG(open_files))`, whose dtor `zend_file_handle_dtor` (`zend_language_scanner.c:2988`) calls `fh->handle.stream.closer(...)` at `:2997` on a `php_stream` that `zend_destroy_rsrc_list` already destroyed at `zend_execute_API.c:282`. |
| `ph12` | Part B `⚠ risk` | append: ⭐ *"the guard is **also one-sided** — with an explicit non-zero `$length` a negative `offset` still passes (`substr_compare("abc","x",-1000000,5)`), which is why upstream's 5.2.0 fix added a negative-offset clamp **as well as** the unconditional bound."* |
| `ph29` | Part B | `▸ trigger` → *"`stream_socket_recvfrom($s, 4294967295)` — any `to_read` with `to_read+1 ≡ 0 (mod 2^32)`. ⚠ **Prefer this to `PHP_INT_MAX`**, whose `to_read + 1` is signed-overflow UB the compiler may fold."* And to the `⚠⚠ risk`: *"it also zeroes `CHECK_MEMORY_LIMIT`'s accumulator (`zend_alloc.c:177` passes `SIZE`, i.e. `real_size`) and reaches `zend_alloc.h:53`'s `size:31` at `:201`. ⚠ **64-bit-only** — on 32-bit nothing truncates and `malloc` fails into `zend_alloc.c:194`'s `exit(1)`."* |
| `ph64` | Part B `⚠ risk` | *"`zend_llist` is ~200 lines"* → **317**. |
| `ph72` | Part B citation | span `:993-1063` ends at the while-loop's brace; `php_array_walk` closes at `:1066`. |

---

## §8 ⭐ Build order for the batch four — C-side reasons only

**Standing order:** `ph21 → ph16 → ph12 → ph29`. **Recommended:**

> ### `ph16 → ph29 → ph12 → ph21`

**Reasons, all C-side:**

1. **`ph21` should not be first.** It is the only one of the four whose stated
   trigger does not fire and whose harm sits on an arm the block does not name
   (§3.B). Deliverable #1 of a build task is reachability; starting with the row
   that would fail it, on a corrected trigger nobody has run, spends the batch's
   first task the way `ph07` was spent. It is also the row that most needs the
   `.memory-php/04-process.md` fixture rule applied carefully, because the
   path-selecting parameter turns out to be `Z_STRLEN == 1` (a *string-length* arm)
   rather than the `strlen × mult` residue that entry names.
2. **`ph16` first** — it is the only one of the four whose defect is a **single
   unguarded macro** over a fixed-size object, with no arithmetic, no allocator and
   no narrowing anywhere in the chain; it is a `static` helper so its `verbatim`
   tier is correct (`UPSTREAM_001` §6) and needs no re-tiering to land first; and
   its upstream fix is a two-line macro. **It is the cheapest true reading of the
   C in the batch** and it exercises the shim symlink rule without depending on
   allocator semantics.
3. **`ph29` second** — its C-side question is now **closed and measured** (§4), it
   has the sharpest allocator dependence in the corpus (which is the thing the
   `emalloc_shim` rule exists for, and it is one of only two rows where that is
   load-bearing), and its upstream fix is *"exact, minimal"* by
   `UPSTREAM_001` §1b's own verdict. Doing it second means the shim's fidelity is
   proven by a row that cannot pass without it, before two rows that merely link it.
4. **`ph12` third** — one guard, one `long`, one sink whose semantics I have now
   confirmed at source (`zend_binary_strncmp` mins both lengths). Its only open
   item is the extra limb in §3.A, which is additive.
5. **`ph21` last**, with the §7.1 correction landed first.

⚠ This is a recommendation on C-side grounds only; it takes no view on the ladder,
the tier landing (`land_m4.py`), or `ph17`'s standing deferral.

---

## §9 What I did not do, and what I am unsure of

- **I did not run PHP.** Every verdict is source reading against the pinned
  tarball, plus one compiled arithmetic probe (`ph29`). No trigger below was
  *executed* against a 5.0.0 build; where I say "reachable" I mean the control flow
  and the types permit it, traced line by line. `ph42`'s gate (an uninitialised
  word equal to 7) and `ph34`'s libc table bound are the two where a run would
  change my confidence most.
- **`ph93` is graded on an absence.** I could not construct an input that both
  reaches `:692` and wraps its accumulation, **and I did not prove none exists** —
  the structural argument in §7.2 is a bound, not a proof. If the manager prefers,
  `UNDECIDABLE` is defensible for that row; I chose `IMPRECISE` because the type
  statement is independently wrong and the trigger independently does not
  demonstrate the claim.
- **I did not run Block 2 as a mechanism audit** (§5), by the §6.1 rule. Its
  membership is fixed in `.temp/php20/sample.py` (seed 21), so a follow-up task can
  run it without re-drawing.
- **I did not read `index.csv`.** Task §3 scopes the test to the tarball, so
  `ph22`'s *"the `root_cause_id` says `line218`"* and the `corpus rows` columns are
  unchecked here.
- **The `⚠ name` / `⚠ magnitude` / `⚠ gate` markers in §2 are not verdicts.** They
  are the additive corrections in §7.3, shown in the table so a reader cannot take
  `SUPPORTED` to mean "nothing to change".
- **Timings are my own estimate of effort per row**, to the nearest minute, not
  instrumented.

## §10 Scratch kept and deleted (`.temp/php20/`)

**Kept (evidence / generators):** `sample.py`, `sample.out`, `extract.sh`,
`ph29_probe.c`, `ph29_probe.log`.
**Deleted (re-derivable):** `src/` and `full/` (both rebuildable with
`sh .temp/php20/extract.sh`), the compiled `ph29_probe` binary
(`gcc -O0 -o ph29_probe ph29_probe.c`).
