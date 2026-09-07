# `patterns-php/CATALOGUE.md` — what the PHP 5.0.0 corpus offers this programme

**91 rows catalogued** — 38 spatial · 22 type/initialisation · 31 temporal, one
of them (`ph91`) **unresolved** — over the 166-row corpus at
`paper/evaluation/security/vuln-corpus-5.0/index.csv`. Against that:
**1 kill on criterion 3** (`CRASH-017`), **1 soft kill on criterion 2**
(`CRASH-021`, pending a run I did not take), and **12 exact-duplication merges**
that survive inside a catalogued row. ✅ **All 166 corpus ids accounted for** —
re-derivable with `python3 .temp/php11/coverage.py`, which parses this file and
diffs it against `index.csv` (output pasted in C.7).

**This is not a build order.** It is the complete, honest account of what the
corpus offers, so that the choice of what to *build* is visible and defensible.
`PLAN_PHP.md` §8 phase 2 picks from it; the PAT programme's ratio — 48 catalogued
against 33 built — is the healthy one.

**Every `file:line` below resolves against the pristine museum tarball**
(sha256 `5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919`),
never against a build tree. Read recipe: `patterns-php/SOURCES.md` §2. The
verification run, the count checked and every discrepancy found are in
`.tasks-php/TASK_PHP_011_REPORT.md` §2; the reader is
`.temp/php11/pristine.py`, which cross-checks each file against
`patterns-php/php-5.0.0.manifest` before serving a line.

---

## §0 How to read this file

### 0.1 ⚠ Three frames per row, and the provenance block names ONE of them

For most rows the **defect site**, the **guard site** and the **faulting site**
are three different places, and the corpus's `c_file_line` does not consistently
name any one of them.

> **Rule, applied throughout: `provenance.c_file` / `c_lines` name the DEFECT
> site.** The guard site and the faulting site appear in the row's block,
> labelled. Where the corpus's own `root_cause_id` or `c_file_line` is wrong,
> the row says so — that is corpus-quality evidence and it is worth keeping.

### 0.2 ⚠⚠ `tier` is a COST STATEMENT, NEVER A FILTER

`verbatim` / `narrowed` / `modelled` (`PLAN_PHP.md` §4.1) says how much C must
come along. **It has no bearing on admission.** Admission is the four C-side
criteria of `PLAN_PHP.md` §3 and nothing else. The mining wave lost ~17 rows by
writing a tier as a criterion-3 kill; this catalogue's Part C re-derives the
criterion for every kill precisely so that cannot recur.

### 0.3 `echoes`

The `pNN` PAT row with the same C mechanism, **as a cross-reference, never a
filter** (`PLAN_PHP.md` §3.1, `DP-03`). A php row that replicates a PAT
mechanism at a real call site is a *replication*, which is evidence. `—` means
no PAT row carries it, which is itself worth knowing.

### 0.4 ⚠ FORMAT — a deliberate deviation from `TASK_PHP_011` §1, stated

`TASK_PHP_011` §1 specifies Part B blocks of **up to 150 words**. At 91 rows
that is ~13 650 words / ~95 KB of prose *on top of* Part A and Part C, and
`.web/CLAUDE.md` records that this project's costliest reporting defect is
*"a document that is correct, fully qualified and unreadable"*. **Part B
therefore uses a fixed six-field micro-schema of ~80–110 words** — citation
line, mechanism, `▸ trigger`, `▸ benign + u64`, `▸ blob`, `⚠ risk` — grouped
under family headings **in table order**, so a reader navigates by mechanism
family (23 of them) rather than by 91 flat entries. Nothing is dropped; the
prose that would have padded to 150 words is the prose a reader skips. The
argument, and the measurement behind it, is `TASK_PHP_011_REPORT.md` §6.

---

## Part A — the table

`inv/obl` are the corpus's own blind-labelled invariant/obligation
(`paper/invariants-list.md`), carried across unmodified.

### Spatial (38)

| id | axis | mechanism (≤ 12 words) | tier | inv/obl | corpus rows | echoes | status |
|---|---|---|---|---|---|---|---|
| ph01 | spatial | limit initialised to the start; refill hook is a no-op | narrowed | I1/O3 | CRASH-066 | p16 | catalogued |
| ph02 | spatial | blind fixed `+2` advance of the caller's cursor | narrowed | I1/O1 | CRASH-120 | p16 | catalogued |
| ph03 | spatial | loop bound computed from a length byte inside the data | verbatim | I1/O2 | CRASH-115, V5C-116 | p16 | catalogued |
| ph04 | spatial | fixed forward peeks; then a length counter desynced from its cursor | narrowed | I1/O1, I11/O2 | CRASH-110, CRASH-073 | p16, p24 | catalogued |
| ph05 | spatial | end-pointer built from a clamp evaluated at 32 bits | verbatim | I11/O2 | CRASH-102 | p24 | catalogued |
| ph06 | spatial | the bound is not a parameter, so no bound is in scope | narrowed | I1/O1 | CRASH-091 | — | catalogued |
| ph07 | spatial | an `mblen_table` cursor loop whose only exit is `n > from` | narrowed | I1/O1 | CRASH-124 | p16 | catalogued |
| ph08 | spatial | lookahead consumes the NUL terminator as data | verbatim | I1/O3 | CRASH-016 | p16 | catalogued |
| ph09 | spatial | leading NUL is an in-band tag; the empty string collides | verbatim | I1/O1 | CRASH-033 | p35 | catalogued |
| ph10 | spatial | one bounds check serves two branches of different widths | narrowed | I1/O1 | CRASH-094 | p16 | catalogued |
| ph11 | spatial | one-sided compare on a signed index, no lower bound | verbatim | I1/O1 | CRASH-145, V5C-173 | p02 | catalogued |
| ph12 | spatial | guard short-circuited by an unrelated optional argument | verbatim | I1/O1 | CRASH-108 | p02 | catalogued |
| ph13 | spatial | base + attacker 32-bit offset, lower-bounded only | narrowed | I1/O1 | CRASH-136 | — | catalogued |
| ph14 | spatial | the overflowed product is used in its own bound check | narrowed | I11/O1 | CRASH-134 | p13 | catalogued |
| ph15 | spatial | ⚠ **MECHANISM REFUTED — see below. Do not build.** | — | I1/O1 | CRASH-096 | p24 | **unresolved** |
| ph16 | spatial | bit-set index straight from input, past an on-stack `fd_set` | verbatim | I1/O2 | CRASH-098 | p02 | catalogued |
| ph17 | spatial | code point over 0xFF sets a bit past a fixed-size bitset | narrowed | I1/O2 | CRASH-127 | p02 | catalogued |
| ph18 | spatial | sizing sum wraps; the pad loop that follows has no bound | verbatim | I11/O1, I11/O2 | CRASH-001, CRASH-011 | p13 | catalogued |
| ph19 | spatial | `count*(width-1)+base` wraps in `int`, emit pass unbounded | verbatim | I11/O1 | CRASH-006 | p13 | catalogued |
| ph20 | spatial | the wrap happens inside `safe_emalloc`'s own first argument | verbatim | I11/O1 | CRASH-007 | p13 | catalogued |
| ph21 | spatial | a 64-bit product narrowed by the store; guard's 2nd disjunct dead | verbatim | I11/O2 | CRASH-107 | p13 | catalogued |
| ph22 | spatial | two passes over one format string apply different clamps | verbatim | I11/O1 | CRASH-014, V5C-015 | p13 | catalogued |
| ph23 | spatial | the budget reserves 2 of the format's 4 literal characters | verbatim | I11/O3 | CRASH-157 | — | catalogued |
| ph24 | spatial | a constant reserve too small for what the emit pass formats | verbatim | I11/O3 | CRASH-008 | — | catalogued |
| ph25 | spatial | the +1 slack is lost in the grow path, terminator skips the check | verbatim | I11/O3 | CRASH-095 | p25 | catalogued |
| ph26 | spatial | negative `memmove` length into a fixed 80-byte static buffer | verbatim | I11/O2 | CRASH-149 | p13 | catalogued |
| ph27 | spatial | `1 + buf_len + 2*new_l` wraps; emit walks a bare output cursor | modelled | I11/O1 | CRASH-009 | p13 | catalogued |
| ph28 | spatial | `uint`→`int` store; the NEXT concat memcpys at a negative offset | verbatim | I11/O2 | CRASH-147 | p13 | catalogued |
| ph29 | spatial | `emalloc(n+1)` where the allocator truncates n mod 2^32 | narrowed | I11/O2 | CRASH-097 | — | catalogued |
| ph30 | spatial | an unclamped scale wraps the `length+scale` allocation size | narrowed | I11/O1 | CRASH-133 | p13 | catalogued |
| ph31 | spatial | `long` day number truncated to `int`, then `sprintf` into `char[16]` | verbatim | I11/O2 | CRASH-135 | p13 | catalogued |
| ph32 | spatial | a range declared in one place, a table literal sized in another | verbatim | I1/O2 | CRASH-089, CRASH-090 | p27 | catalogued |
| ph33 | spatial | a 2-byte buffer holding a lead byte that declares a longer one | verbatim | I1/O1 | CRASH-128 | p27 | catalogued |
| ph34 | spatial | an unvalidated user `long` used directly as a table index | narrowed | I1/O1 | CRASH-122 | p02 | catalogued |
| ph35 | spatial | `0xff *` where `0x100 *` was meant, over a signed `char` | verbatim | I11/O1 | CRASH-130 | p13 | catalogued |
| ph36 | spatial | a generated table indexed by an unbounded state + token sum | narrowed | I1/O2 | CRASH-005 | p19 | catalogued |
| ph37 | spatial | validate and execute passes compute one index differently | narrowed | I1/O1, I11/O1 | CRASH-018, CRASH-019 | p23 | catalogued |
| ph38 | spatial | in-place increment of an operand that aliases a shared literal | narrowed | I1/O4 | CRASH-077 | p49 | catalogued |

### Type / initialisation (22)

| id | axis | mechanism (≤ 12 words) | tier | inv/obl | corpus rows | echoes | status |
|---|---|---|---|---|---|---|---|
| ph39 | type | union member read with no tag check of any kind | narrowed | I4/O1 | CRASH-036, CRASH-037, CRASH-101 | p35 | catalogued |
| ph40 | type | presence checked, type not; the null-check cannot help | narrowed | I4/O3 | CRASH-093 | p35 | catalogued |
| ph41 | type | container checked, elements not | narrowed | I4/O1 | CRASH-039 | p35 | catalogued |
| ph42 | type | guard present and passing, but on the WRONG tag namespace | narrowed | I4/O1, I3 | CRASH-144 | p38 | catalogued |
| ph43 | type | a two-arm helper laundering the tag, misused both ways | narrowed | I4/O1, I4/O3 | CRASH-079, CRASH-111 | p35 | catalogued |
| ph44 | type | type inferred from the creation path, not from the tag | narrowed | I4/O1 | CRASH-085 | p35 | catalogued |
| ph45 | type | a heap pointer stored in an `int` field, cast back, freed and written | verbatim | pointer-value-integrity | CRASH-123 | p38 | catalogued |
| ph46 | type | one untagged union; one call site invents a discriminant, one omits it | narrowed | I4/O1 | CRASH-053, CRASH-056 | p35 | catalogued |
| ph47 | type | in-place retype through a value the separator refuses to separate | narrowed | I4/O2 | CRASH-104, CRASH-058 | p49 | catalogued |
| ph48 | type | the same helper used to FORCE the shared flag ON | narrowed | I4/O2 | LOGIC-017 | p49 | catalogued |
| ph49 | type | count decremented after the destructor, outside the blocked window | narrowed | I3/O3 | CRASH-153 | p34 | catalogued |
| ph50 | type | a discarded status code leaves an out-parameter unwritten | verbatim | I3/O1 | CRASH-153 | p42 | catalogued |
| ph51 | type | uninitialised struct fields consumed as function pointers | modelled | I3/O2 | CRASH-087 | p36 | catalogued |
| ph52 | type | an unconstructed caller slot destructed on an early-exit path | narrowed | I3/O1 | LOGIC-007 | p42 | catalogued |
| ph53 | type | storage grown to the COUNT; the tail is never written | verbatim | I19/O2 | CRASH-158 | p27 | catalogued |
| ph54 | type | guard at the wrong pointer depth — `!p` where `!*p` was meant | narrowed | I16 | CRASH-143 | — | catalogued |
| ph55 | type | early exit strides 1 over a two-word instruction | verbatim | I18, I12 | CRASH-023 | p19 | catalogued |
| ph56 | type | opcode selected by arithmetic; the guard is replicated on some arms | narrowed | I18, I12 | CRASH-041 | p19 | catalogued |
| ph57 | type | the same switch, a LOCK not taken on the string-offset arm | narrowed | I18/O2 | CRASH-028 | p19 | catalogued |
| ph58 | type | the emitter returns 0 without emitting the free the executor expects | narrowed | I18/O2 | CRASH-055 | p19 | catalogued |
| ph59 | type | `!f(x) == SUCCESS` — precedence makes the guard test the opposite | verbatim | I12/O1 | CRASH-082 | — | catalogued |
| ph60 | type | a fallible call's failure not tested before its result is used | verbatim | I12/O1, I16 | CRASH-088, CRASH-061, CRASH-126, CRASH-163 | — | catalogued |

### Temporal (31)

| id | axis | mechanism (≤ 12 words) | tier | inv/obl | corpus rows | echoes | status |
|---|---|---|---|---|---|---|---|
| ph61 | temporal | container doubles under a raw interior pointer the caller holds | verbatim | I10/O1, I10/O3 | CRASH-155, CRASH-075, CRASH-081, CRASH-083, CRASH-117 | p25 | catalogued |
| ph62 | temporal | the same growth, with the interior pointer cached across a callback | verbatim | I10/O1, I10/O3 | CRASH-046, CRASH-070 | p25 | catalogued |
| ph63 | temporal | the cursor type IS a bare node pointer, held across user code | narrowed | I10/O1, I10/O3 | CRASH-002, CRASH-022, CRASH-040 | p28 | catalogued |
| ph64 | temporal | the callee unlinks and frees the very element the loop holds | verbatim | I10/O1 | CRASH-086 | p28 | catalogued |
| ph65 | temporal | a back-reference table retains pointers the parser has freed | modelled | I5/O3, I5/O2 | CRASH-121, CRASH-118 | p27 | catalogued |
| ph66 | temporal | a numeric bucket's key is never compared; hash equality is identity | verbatim | I7/O2, I7/O3 | LOGIC-001 | p22 | catalogued |
| ph67 | temporal | the destructor runs while the bucket is still linked and advertised | verbatim | I10/O1, I5/O1 | CRASH-160, CRASH-154 | p28 | catalogued |
| ph68 | temporal | a recycled handle with no generation tag resolves to a dead slot | verbatim | I17/O4, I17/O1 | CRASH-030, CRASH-045, CRASH-044 | p27 | catalogued |
| ph69 | temporal | two owning slots, one allocation, no increment between them | narrowed | I7/O1 | CRASH-131 | p34 | catalogued |
| ph70 | temporal | a decrement taken by a party that never took the increment | narrowed | I7/O2, I9/O2 | CRASH-047, CRASH-099, CRASH-103, CRASH-080 | p34 | catalogued |
| ph71 | temporal | the container is destroyed, then a pointer derived from it is read | modelled | I2/O4, I2/O1 | CRASH-004, CRASH-003, CRASH-025, CRASH-067 | p28 | catalogued |
| ph72 | temporal | allocated on one arm, released on every arm | narrowed | I5/O2, I5/O1 | CRASH-074, CRASH-125, CRASH-112 | p42 | catalogued |
| ph73 | temporal | automatic storage published where user code can retain it | narrowed | I14/O1 | CRASH-052, CRASH-051, CRASH-027, CRASH-032, CRASH-100 | p34 | catalogued |
| ph74 | temporal | a non-owned literal adopted as an owned member, then freed | narrowed | I14/O4, I5/O4 | CRASH-139 | p49 | catalogued |
| ph75 | temporal | ownership taken, then a fallible commit that can be skipped entirely | narrowed | I9/O3, I6/O3 | CRASH-161, LOGIC-026, LOGIC-027, LOGIC-004 | p42 | catalogued |
| ph76 | temporal | engine-owned, non-allocator storage handed to the deallocator | verbatim | I14/O3, I5/O4 | CRASH-012, CRASH-148, CRASH-026, CRASH-078 | p32 | catalogued |
| ph77 | temporal | resurrect-and-queue into a fixed two-slot array, unchecked bump | narrowed | I7/O2, I7/O5 | CRASH-151, CRASH-057, CRASH-050, LOGIC-011, LOGIC-022 | p34 | catalogued |
| ph78 | temporal | a raw pointer latched across a call that can run user code | narrowed | I17/O1, I7/O4 | CRASH-042, CRASH-159, CRASH-035, CRASH-064, CRASH-010, CRASH-132, CRASH-113 | p28 | catalogued |
| ph79 | temporal | a cache that cannot tell a borrowed handler from a per-call one | narrowed | I20/O1, I20/O3 | CRASH-038, CRASH-069, CRASH-031, CRASH-072, LOGIC-025 | p27 | catalogued |
| ph80 | temporal | two subsystems disagree about who owns the block's lifetime | verbatim | I5/O3, I5/O2 | CRASH-084, CRASH-092, CRASH-114, CRASH-141 | p32 | catalogued |
| ph81 | temporal | the slot is released and left as a presence flag for what it held | verbatim | I5/O2, I5/O1 | CRASH-142, CRASH-140 | p32 | catalogued |
| ph82 | temporal | a loop temp acquired at use, released only at the textual loop end | modelled | I6/O1 | LOGIC-002, LOGIC-023, LOGIC-009, LOGIC-019, LOGIC-024, LOGIC-010, LOGIC-012, LOGIC-016, LOGIC-021 | p42 | catalogued |
| ph83 | temporal | a lock taken unconditionally, ignoring that the result is unused | narrowed | I6/O2, I17/O1 | LOGIC-011, LOGIC-022 | p34 | catalogued |
| ph84 | temporal | a deep copy with no matching destructor on the exit path | narrowed | I6/O1 | LOGIC-015 | p42 | catalogued |
| ph85 | temporal | the type tag overwritten over a live payload, with no dtor | narrowed | I6/O1 | LOGIC-006 | p35 | catalogued |
| ph86 | temporal | compile-time liveness marking stamps the wrong opcode | narrowed | I18/O2 | CRASH-065, CRASH-024 | p19 | catalogued |
| ph87 | temporal | release, then format the released buffer into the error message | verbatim | I5/O2, I12/O1 | CRASH-068, CRASH-129 | p32 | catalogued |
| ph88 | temporal | subsystem teardown ordered so one still names the other's storage | narrowed | I5/O3 | CRASH-062 | p32 | catalogued |
| ph89 | temporal | a by-ref parameter separates the very table a live alias names | narrowed | I2/O2 | CRASH-034 | p28 | catalogued |
| ph90 | temporal | the destructor is called on an out-parameter the failing call left NULL | verbatim | I12/O1 | CRASH-029 | — | catalogued |
| ph91 | temporal | ⚠ label and citation disagree — see the block | — | I5 | CRASH-071 | — | **unresolved** |

---

## Part B — the rows

Format per row: **id · name** — defect-site citation · corpus rows · tier ·
inv/obl · echoes; then the mechanism; then `▸ trigger` / `▸ benign + u64` /
`▸ blob` / `⚠ risk`. `GUARD:` and `FAULT:` name the other two frames when they
differ from the defect site (§0.1).

## SPATIAL

### S1 — unbounded cursor walk (`DP-07`'s pointer-cursor shape)

**ph01 · unserialize re2c lexer** — `ext/standard/var_unserializer.c:243`, `:106` · CRASH-066 · `narrowed` · I1/O3 · echoes p16
`limit = cursor = *p;` at `:243` sets the limit to the **start**, and `#define YYFILL(n) do { } while (0)` at `:106` makes the refill hook a no-op — so the lexer's only bound test, `if (YYLIMIT == YYCURSOR) YYFILL(1);`, is dead at `:400` and twelve further copies. The true end is the `max` parameter, which never appears on either side of a comparison anywhere in the file.
▸ trigger: a truncated serialised payload with no terminating `;` → `yy16: yych = *++YYCURSOR;` (`:390`) walks off the block.
▸ benign: a well-formed payload parses; `u64` = fold over the emitted token stream + `(allocs, frees)`.
▸ blob: the serialised bytes, verbatim.
⚠ risk: PHP hands the lexer a **NUL-terminated** zval string, so an extraction that keeps the terminator makes the over-read land in-bounds and the row look clean. The fixture must pass a non-terminated buffer.

**ph02 · unserialize `object_common1` blind advance** — `ext/standard/var_unserializer.c:208-210` · CRASH-120 · `narrowed` · I1/O1 · echoes p16
`elements = parse_iv2((*p) + 2, p);` then `(*p) += 2;` — a fixed advance of the caller's cursor with no check that two bytes remain. `object_init_ex` on the next line degenerates to a no-op in a kernel. FAULT: `:195`, `finish_nested_data`'s `*((*p)++)`.
▸ trigger: an `O:` header truncated inside the two skipped bytes.
▸ benign: an object header parses and its element count is returned; `u64` = element count fold.
▸ blob: the serialised bytes.
⚠ risk: sink differs from ph01's — do not merge the two into one kernel and then report one result. `object_init_ex` must be stubbed, not deleted, or the benign path stops allocating.

**ph03 · uudecode short-line bound** — `ext/standard/uuencode.c:141` · CRASH-115, V5C-116 · `verbatim` · I1/O2 · echoes p16
The output is sized `emalloc(ceil(src_len*0.75)+1)` at `:131` and the input's true end is `e = src + src_len` at `:133` — but the decode loop's bound is neither: `:141` computes `ee = s + (len == 45 ? 60 : (int) floor(len * 1.33))` from a **length byte inside the data**. Both an over-read (`*(s+1..3)`) and an over-write (through `p`) follow from the one wrong bound.
▸ trigger: a line whose length byte claims 45 while fewer bytes remain.
▸ benign: well-formed uuencoded input round-trips; `u64` = checksum of the decoded bytes.
▸ blob: the uuencoded text.
⚠ risk: the row's `cwe` is CWE-125 but the **write** fires first under ASan on most inputs. The oracle must record which, not pick one silently (spatial `NOTES.md` §5.6).

**ph04 · `php_url_parse_ex`: peeks and a desynced length** — `ext/standard/url.c:132`, `:139-144` · CRASH-110, CRASH-073 · `narrowed` · I1/O1 + I11/O2 · echoes p16, p24
**One extracted kernel, two triggers** (adjudication §4). (a) After `e = strchr(s, ':')` the scheme block probes `*(e+2)`, `*(e+3)`, `*(e+5)` with no bound test, while the true end `ue = s + length` computed at `:94` is never read in the block. (b) Eleven lines later the hand-maintained length counter desyncs: `:139 s = e + 1;` then `:143 length -= ++e - s;` — the same idiom that is correct at `:118`, because there `s` still held the old start. FAULT (b): `:292 estrndup(s, (ue-s))`.
▸ trigger: (a) `file:` with fewer than 6 bytes after the colon; (b) `x:/just-a-path`.
▸ benign: ordinary URLs parse; `u64` = fold of the component offsets and lengths.
▸ blob: the URL bytes.
⚠ risk: **do not split this into two rows** — one extraction, two triggers; two rows double-count a ladder cost paid once.

**ph05 · `php_strspn` end pointer from a 32-bit clamp** — `ext/standard/string.c:240` · CRASH-102 · `verbatim` · I11/O2 · echoes p24
`start` and `len` are `long`, but the clamp at `:240` evaluates them as `(unsigned)`: `if (((unsigned) start + (unsigned) len) > len1) { len = len1 - start; }`. A `len` of 2^32 becomes 0 under the cast, the clamp is false, and `len` keeps its full 64-bit value. The unclamped value builds the end pointer at `:245-248`, and `php_strspn` (`:1330-1336`) terminates on pointer **equality**, so a wrong end is not merely wrong but steppable past.
▸ trigger: `strspn($s, $mask, 0, 4294967296)`.
▸ benign: ordinary spans; `u64` = the span length.
▸ blob: haystack + mask + two `long`s.
⚠ risk: the equality termination is half the defect. An extraction that "tidies" `p != s1_end` to `p < s1_end` deletes the interesting half and keeps the boring one.

**ph06 · `get_next_char`: the bound is not a parameter** — `ext/standard/html.c:486-490` · CRASH-091 · `narrowed` · I1/O1 · echoes —
✅ Verified at source: `get_next_char(enum entity_charset, unsigned char *str, int *newpos, unsigned char *mbseq, int *mbseqlen)` takes **no length**. The bound is therefore not merely unchecked, it is **not in scope**; `:656 unsigned char next2_char = str[pos+1];` has nothing it could have been compared against. FAULT: `:655-656`.
▸ trigger: a string ending in a lone `0x8f` lead byte.
▸ benign: multibyte text classifies correctly; `u64` = fold of the decoded codepoints.
▸ blob: the byte string + a charset selector.
⚠ risk: the distinctness of this row **is the signature**. An extraction that adds a length parameter "for the kernel" has removed the mechanism and built ph10 instead.

**ph07 · `mbfl_strcut`: a cursor loop with no end test** — `ext/mbstring/libmbfl/mbfl/mbfilter.c:1200-1210` · CRASH-124 · `narrowed` · I1/O1 · echoes p16
```c
1202  for (;;) {
1203      m = mbtab[*p];        /* per-byte length, from a 256-entry static table */
1204      n += m;
1205      p += m;
1206      if (n > from) break;  /* the ONLY exit */
1209      start = n;
```
The walk advances `p` by a length **read out of the data** and stops only when the accumulated count passes `from` — `string->len` is never consulted in the loop. GUARD: `ext/mbstring/mbstring.c:1800-1805` clamps a negative `len` and **never clamps `from`**; `:1807` then calls in.
▸ trigger: `mb_strcut($s, strlen($s) + 1, 1)`.
▸ benign: ordinary cuts land on character boundaries; `u64` = fold of `(start, end)`.
▸ blob: the byte string + a `from` + a 256-entry length table.
⚠ risk: killed by the sentence that also killed **ph45** — *"the mbstring rows all require libmbfl's filter-chain object model"*. It requires neither: `mbfl_string` reduces to `{val, len}` and `mblen_table` is a static array. **A pure `DP-07` pointer cursor.**

**ph08 · printf modifier scanner consumes the NUL** — `ext/standard/formatted_print.c:599-600` · CRASH-016 · `verbatim` · I1/O3 · echoes p16
The modifier scanner at `:591-605` is a bare `for (;; inpos++)` whose only exit is `else break`; it relies entirely on the format string's NUL to fall out of the modifier set. The custom-padding arm does `padding = format[++inpos]` — consuming the **next** byte, which for a format ending in `'` is the terminator itself. FAULT: `:592`, one iteration later, with no stopping condition left.
▸ trigger: `sprintf("%'")`.
▸ benign: ordinary format strings; `u64` = the formatted output's checksum.
▸ blob: the format string + arguments.
⚠ risk: I1/O3 in its purest form; the fixture must not append a second NUL "to be safe".

**ph09 · `zend_unmangle_property_name`: the empty name collides with the tag** — `Zend/zend_compile.c:2611-2622` · CRASH-033 · `verbatim` · I1/O1 · echoes p35
PHP mangles a private property as `"\0Class\0prop"`, so **a leading NUL is the in-band marker for "mangled"**. For an *empty* name the first byte is not a marker — it is the string's own terminator — so `:2615 if (mangled_property[0]!=0)` classifies it as mangled, `:2620` forms `mangled_property+1` one past a 1-byte key, and `:2621 strlen()` walks from there. GUARD: `Zend/zend_object_handlers.c:201` (the corpus's *missing-guard* field). FAULT: `Zend/zend_compile.c:2621` — the same 12-line function, and the corpus **also** names it.
▸ trigger: `$obj->{""}` then any operation that unmangles the property table's keys (`var.c:78`, `zend_execute.c:3801`).
▸ benign: ordinary and mangled names split correctly; `u64` = fold of the two returned offsets.
▸ blob: a key buffer + its length.
⚠ risk: the corpus's `c_file_line` points at a frame 400 lines away in another file. Cite `zend_compile.c`.

### S2 — a guard that runs and is wrong

**ph10 · iptc: one check, two branch widths** — `ext/standard/iptc.c:339-347` · CRASH-094 · `narrowed` · I1/O1 · echoes p16
The tag loop performs one bounds check, `if ((inx + 4) >= length) break;`, then unconditionally consumes two bytes (`:342-343`), leaving three of the checked budget — and then serves two branches of different widths: the short-tag arm reads `buffer[inx..inx+1]`, the long-tag arm reads `buffer[inx+2..inx+5]`. The check was sized for the narrower branch and **the data picks the branch**.
▸ trigger: a long-tag marker within 6 bytes of the end.
▸ benign: well-formed IPTC parses; `u64` = fold of `(dataset, recnum, len)` triples.
▸ blob: the IPTC segment bytes.
⚠ risk: `:327`'s find-first-tag loop carries a **third** over-read the corpus does not record (`buffer[inx+1]` with only `inx < length` in scope). An extraction of the scan loop imports it silently and would misattribute it.

**ph11 · `isset`/`empty` string offset, one-sided compare** — `Zend/zend_execute.c:4033` · CRASH-145, V5C-173 · `verbatim` · I1/O1 · echoes p02
`if (offset->value.lval <= Z_STRLEN_PP(container) && Z_STRVAL_PP(container)[offset->value.lval] != '0')` — `lval` is a `long` carrying the user's subscript, so **any negative subscript passes trivially** and is then used directly as a byte index. Sibling at `:4028`.
▸ trigger: `empty($s[-4096])`.
▸ benign: in-range offsets answer correctly; `u64` = fold of the boolean answers.
▸ blob: a string + a list of `long` offsets.
⚠ risk: the `<=` (rather than `<`) is a *second*, one-past-the-end defect in the same line. Report both or the row understates itself.

**ph12 · `substr_compare`: the guard disabled by another argument** — `ext/standard/string.c:4786` · CRASH-108 · `verbatim` · I1/O1 · echoes p02
The only bound on `offset` is `if (len && offset >= s1_len)`, and its **first conjunct disables it**: when the optional `length` is absent or zero, `len == 0` and the check is skipped for both directions. `offset` is a `long`, never clamped, so `s1 + offset` at `:4794` is arbitrary.
▸ trigger: `substr_compare($a, $b, -1000000)` with `$length` omitted.
▸ benign: ordinary comparisons; `u64` = fold of the comparison results.
▸ blob: two strings + a `long` offset + an optional length.
⚠ risk: the declaration block is `:4776-4780` and the miner's quote omits `zend_bool cs=0;` at `:4779` — copy from the tarball, not from the report.

**ph13 · exif: base + attacker 32-bit offset, lower-bounded only** — `ext/exif/exif.c:3071-3079` · CRASH-136 · `narrowed` · I1/O1 · echoes —
`offset_of_ifd = php_ifd_get32u(CharBuf+4, …)` reads an unsigned 32-bit value **out of the image data** at `:3071`; `:3072` checks it **only** for `< 0x08`; `:3079` adds it to the base. `base + attacker-chosen offset, lower-bounded only` is a jump, where ph01–ph04 are walks. ✅ The defect completes at `:3079`, **before** the recursive call — none of `exif_process_IFD_in_JPEG`'s mutual recursion is needed.
▸ trigger: `bug48378.jpeg` (shipped in `input/crash/`), or any TIFF header with `offset_of_ifd = 0xFFFFFF00`.
▸ benign: an ordinary JPEG's IFD0 offset resolves; `u64` = fold of the bytes at the resolved offset.
▸ blob: the JPEG/TIFF header bytes.
⚠ risk: pricing the extraction at `exif_process_IFD_in_JPEG` rather than at `:3071-3079` is the error that killed this row once (Part C, F8).

**ph14 · exif: the overflowed product is used in its own guard** — `ext/exif/exif.c:2725-2731` · CRASH-134 · `narrowed` · I11/O1 · echoes p13
`byte_count = components * php_tiff_bytes_per_format[format];` (`:2725`) overflows, and `:2731 if (offset_val+byte_count > IFDlength || value_ptr < dir_entry)` then tests **the overflowed value** — a guard defeated by the very overflow it exists to detect. ⚠ `offset_val+byte_count` can wrap a **second** time.
▸ trigger: `bug54002_1.jpeg` / `bug54002_2.jpeg`, or `components` near `INT_MAX/8`.
▸ benign: ordinary tags read; `u64` = fold of `(tag, format, byte_count)`.
▸ blob: an IFD directory entry stream.
⚠ risk: distinct from ph18, where **two different** attacker integers defeat one guard; here **one** integer defeats it twice. Do not merge.

**ph15 · `zend_memnstr`: `end` underflows below the haystack** — `Zend/zend_operators.h:128-151` · CRASH-096 · **UNRESOLVED** · I1/O1 · echoes p24

> ⚠⚠⚠ **THE MECHANISM BELOW IS REFUTED. DO NOT BUILD THIS ROW.**
> `TASK_PHP_012` B1 measured it: with a **real zero-length haystack**,
> `end -= needle_len` makes `p <= end` **FALSE** and `zend_memnstr` returns
> correctly. The defect needs `haystack == NULL` — a wrap **through** zero, not
> an underflow below a live buffer. ⚠ **A kernel built to the `▸ blob` spec
> below would gate GREEN while modelling nothing**, which is the worst available
> outcome for a benchmark row.
> ✅ **What survives: the defect site is `zend_operators.h:134`, not the stream
> layer** — that conclusion is now three-for-three across independent readings.
> ⚠ **This is the THIRD wrong mechanism for CRASH-096** (two miners, then the
> manager's adjudication, then this). **A fourth reading is not the way to bet:
> re-derive it from a RUN, not from the source.** Text kept below, struck, so
> the next attempt can see what has already been tried.

~~✅ Settled here (adjudication left it open).~~ `zend_memnstr(haystack, needle, needle_len, end)` does `end -= needle_len` at `:134` with **no precondition that the haystack is at least `needle_len` long**, and no NULL/empty check. For a zero-length haystack `end` underflows below `haystack`, `while (p <= end)` at `:136` is true under unsigned pointer comparison, and `:137 memchr(p, *needle, (end-p+1))` gets a length of `(size_t)-1`. GUARD: `ext/standard/streamsfuncs.c:1047` — `if (max_length < 0)`, so **zero passes**. FAULT: `main/streams/streams.c:844`.
▸ trigger: `stream_get_line($f, 0, "xy")` — `php_stream_fill_read_buffer(stream, 0)` fills nothing, `readbuf` stays NULL, `readbuflen` 0.
▸ benign: ordinary substring searches; `u64` = the found offset, or a sentinel.
▸ blob: haystack bytes + a length field + needle bytes.
⚠ risk: **the harmful step is NOT in the stream layer** — that is where CRASH-097/098 were said to die. It is a 24-line `static inline` in a Zend header and is blob-pure.

**ph16 · `FD_SET` past an on-stack `fd_set`** — `ext/standard/streamsfuncs.c:541` · CRASH-098 · `verbatim` · I1/O2 · echoes p02
`FD_SET(this_fd, fds)` with `fds` an `fd_set` in the **caller's** frame and `this_fd` unchecked against `FD_SETSIZE`. ✅ Measured (`.temp/php11/fdset_probe.c`): `FD_SET` is a pure bit-set macro over the `fd_set` object and **never consults the fd table** — index 4096 into a 128-byte `fd_set` writes at byte offset 512 with only fds 0,1,2 open and no `RLIMIT_NOFILE` change.
▸ trigger: any index ≥ 1024 from the blob.
▸ benign: in-range indices set and read back; `u64` = fold of the set bits.
▸ blob: a list of 16-bit indices.
⚠⚠ risk: **stock ASan does not see this.** Measured: a write 8 bytes past the object reports `stack-buffer-overflow`; the same write 384 bytes past is **silent**, because it jumps clean over the redzone into unpoisoned stack. Glibc `_FORTIFY_SOURCE` *does* catch it (`*** bit out of range 0 - FD_SETSIZE on fd_set ***`). This row needs a canary/checksum oracle, not a sanitizer.

**ph17 · a code point over 0xFF into a fixed-size bitset** — `ext/mbstring/oniguruma/regparse.c:3581` · CRASH-127 · `narrowed` · I1/O2 · echoes p02
`BITSET_SET_BIT(cc->bs, (int )(*vs));` on the `CCV_SB` (single-byte) arm of `next_state_val`, where `*vs` is an `OnigCodePoint` an octal escape can push **over 0xFF** — the arm's whole premise is that it is not. The bitset `cc->bs` is fixed-size, so the write lands past it.
▸ trigger: a character class containing `\777`.
▸ benign: ordinary single-byte classes set the right bits; `u64` = fold of the bitset words.
▸ blob: a class-parse token stream carrying code-point values.
⚠ risk: **ph16's shape on a heap object rather than a stack one** — same obligation, different storage, so it is a `PLAN_PHP.md` §3.1 variation and its own row. It needs the bitset macro and `next_state_val`'s switch; **not the oniguruma matcher**, which is downstream of the parse.

### S3 — sizing arithmetic vs an unbounded emit cursor

**ph18 · `php_sprintf_appendstring`: one guard, two attacker integers** — `ext/standard/formatted_print.c:190` · CRASH-001, CRASH-011 · `verbatim` · I11/O1 + I11/O2 · echoes p13
`req_size = *pos + MAX(min_width, copy_len) + 1;` in `int`, and the doubling guard at `:192 if (req_size > *size)` is the only thing between the format arguments and three unbounded write loops. Two different attacker integers make it false: (a) `php_sprintf_getnumber` returns an unbounded `strtol` `long` (`:443`) narrowed to `int width` (`:614/:626`), so a large width wraps `req_size` negative and the pad loop at `:206-208` writes anyway; (b) a `long` precision narrows to a **negative** `copy_len`, which satisfies the guard honestly and becomes a ~1.8e19 `memcpy` length at `:211`.
▸ trigger: `sprintf("%2147483647d", 1)` / `sprintf("%.2147483648f", 1.0)`.
▸ benign: ordinary formats; `u64` = the output checksum.
▸ blob: the format string + arguments.
⚠ risk: the `erealloc` is never reached in (a) — the buffer is simply not grown. An extraction that "fixes" the allocator has changed nothing; the allocator is not in this row.

**ph19 · `php_char_to_str_ex` count×(width−1)** — `ext/standard/string.c:2946-2947` · CRASH-006 · `verbatim` · I11/O1 · echoes p13
A textbook two-pass size-then-emit. The counting pass (`:2935-2939`) walks `source < source_end` correctly; the sizing line computes `len + char_count * (to_len - 1)` entirely in `int`, wraps **down to a small positive**, and `emalloc` behaves perfectly. The emit pass at `:2950-2965` has no output bound; the OOB write is at `:2957`.
▸ trigger: 65 536 occurrences × a 65 537-byte replacement.
▸ benign: ordinary `str_replace`; `u64` = the result checksum.
▸ blob: haystack + needle + replacement.
⚠ risk: `emalloc_dependent` is **false** — the allocator sees an ordinary small request. Do not import ph29's allocator finding here.

**ph20 · `php_chunk_split`: the wrap is inside `safe_emalloc`'s argument** — `ext/standard/string.c:1781` · CRASH-007 · `verbatim` · I11/O1 · echoes p13
`dest = safe_emalloc((srclen + (chunks + 1) * endlen + 1), sizeof(char), 0);` — the overflow-checked wrapper **is present in 5.0.0** and is defeated by the caller's parentheses: the interesting arithmetic is collapsed into the first argument before `safe_emalloc` ever sees it. Emit loop `:1783-1796`, terminator `:1798`.
▸ trigger: a `chunklen` making `(chunks+1)*endlen` wrap.
▸ benign: ordinary chunking; `u64` = the result checksum.
▸ blob: the source string + chunklen + end string.
⚠ risk: the reproducer comment cites 4.0.2's plain `emalloc` (`SOURCES.md` §3). Pristine 5.0.0 is `safe_emalloc` and **that changes the analysis** — the row is about the wrapper being bypassed, not absent.

**ph21 · `str_repeat`: narrowed by the store, guard's second disjunct dead** — `ext/standard/string.c:4120`, `:4144-4145` · CRASH-107 · `verbatim` · I11/O2 · echoes p13
`int result_len;` (`:4120`) takes an `int × long` product computed in **64-bit** and narrowed **by the store** (`:4144`). The guard at `:4145`, `if (result_len < 1 || result_len > 2147483647)`, then has a **provably dead second disjunct** — an `int` can never exceed `INT_MAX`. *A guard killed by the type of the variable it tests*, which is not ph19's wrap-in-an-expression.
▸ trigger: `str_repeat($s, 2^32/strlen($s))`.
▸ benign: ordinary repeats; `u64` = the result checksum.
▸ blob: the source string + a `long` multiplier.
⚠ risk: **cite `:4120` / `:4144` / `:4145`.** `ADJUDICATION_001.md` §0 gives `:4119` / `:4143` / `:4144` — off by one on all three (report §2.3).

**ph22 · `pack`: two passes, different clamps** — `ext/standard/pack.c:247`, `:304` · CRASH-014, V5C-015 · `verbatim` · I11/O1 · echoes p13
`outputpos += (arg + 1) / 2;` in the sizing pass wraps `int`; `output = emalloc(outputsize + 1);` at `:304` then allocates the wrapped amount and the emit loop from `:309` writes the unwrapped one. The corpus's cleanest **two-pass** sizing mismatch, with the two passes 60 lines apart in one function.
▸ trigger: `pack("H2147483647", …)`.
▸ benign: ordinary pack formats; `u64` = the packed bytes' checksum.
▸ blob: the format codes + arguments.
⚠ risk: the `root_cause_id` says `line218`; the defect is at `:247`, and the CSV is right (spatial `NOTES.md` §5.2). Grep `c_file_line`, never the id.

**ph23 · `_build_trace_string`: 2 of 4 literal characters budgeted** — `Zend/zend_exceptions.c:310-311` · CRASH-157 · `verbatim` · I11/O3 · echoes —
`s_tmp = emalloc(Z_STRLEN_PP(file) + MAX_LENGTH_OF_LONG + 2 + 1);` then `sprintf(s_tmp, "%s(%ld): ", …)`. The format's literals are `(`, `)`, `:`, ` ` = **four**; the budget reserves **two**. A string, a long, an emalloc and a sprintf — **the backtrace is the CALLER**, not the kernel.
▸ trigger: any file name of the maximum length with a long line number.
▸ benign: ordinary trace lines format; `u64` = the emitted string's checksum.
▸ blob: a file-name string + a `long`.
⚠ risk: this row was killed with *"the blob would have to encode a backtrace"*. It does not — `TRACE_APPEND_*` and `zend_hash_apply_with_arguments` are one frame up.

**ph24 · `date()`: a constant reserve too small for the emit pass** — `ext/standard/datetime.c:358-359` · CRASH-008 · `verbatim` · I11/O3 · echoes —
The sizing pass is a `switch` over the format string adding a **hard-coded constant per conversion character**; `case 'U': size += 10;` reserves ten bytes for a value the emit pass then `sprintf`s as the `%ld` of a 64-bit `time_t`. **No arithmetic overflow at all**, which is what makes it distinct from every other sizing row here.
▸ trigger: `date("UUUU…", 99999999999)`.
▸ benign: ordinary date formats; `u64` = the formatted string's checksum.
▸ blob: the format bytes + a timestamp.
⚠ risk: this row was dropped by the wave with **no reason recorded anywhere** (adjudication §3a) — 1 of 43 uncovered rows. Its kernel shape is the best of the sizing set.

**ph25 · `metaphone`: the +1 slack lost in the grow path** — `ext/standard/metaphone.c:147-155`, `:185-189` · CRASH-095 · `verbatim` · I11/O3 · echoes p25
Initial `safe_emalloc(sizeof(char), n, 1)` reserves n+1 with `max_buffer_len = n`, so there is one byte of slack. `Phonize` grows with `erealloc(…, max_buffer_len + 2); max_buffer_len += 2;` — which **consumes the slack** — and `End_Phoned_Word` (`:155`) writes `(*phoned_word)[p_idx] = '\0'` as the one write that skips the grow check (`:465`).
▸ trigger: an input whose phonetic expansion exactly fills the buffer.
▸ benign: ordinary words; `u64` = the phonetic string's checksum.
▸ blob: the word bytes.
⚠ risk: no wrap anywhere — an extraction that looks for one will conclude the row is not reachable.

**ph26 · `php_convert_to_decimal`: a negative `memmove` length** — `ext/standard/formatted_print.c:94-99` · CRASH-149 · `verbatim` · I11/O2 · echoes p13
The integer part of a double is emitted **backwards** into a fixed 80-byte **static** buffer (`:37 #define NDIG 80`, `:73 static char cvt_buf[NDIG];`), with `p1` walking down from `&cvt_buf[NDIG]`. `ndigits` is clamped only from above (`:76-77`). When `p1` reaches the front, `mvl = NDIG - ndigits` goes negative and `memmove(&cvt_buf[mvl], &cvt_buf[0], NDIG-mvl-1)` writes before the object and past it.
▸ trigger: a large `%f` precision on a large double.
▸ benign: ordinary doubles convert; `u64` = the digit string's checksum.
▸ blob: a double + a precision.
⚠ risk: **no allocator at all** — static BSS. A row built with an `emalloc` fixture measures nothing.

**ph27 · `php_ereg_replace`: `1 + buf_len + 2*new_l`** — `ext/standard/reg.c:338` · CRASH-009 · `modelled` · I11/O1 · echoes p13
The sizing expression wraps in `int` at `:338` and the emit pass at `:349-359` walks a bare `walkbuf` output cursor with no bound. GUARD: `:337`, which the CSV cites. An F1+F2 hybrid with `ptr_cursor: true`.
▸ trigger: a pattern with many backreferences over a long subject.
▸ benign: ordinary `ereg_replace`; `u64` = the result checksum.
▸ blob: pattern + subject + replacement, with a stub matcher driven by an offset list in the blob.
⚠ risk: `modelled` **because the sizing pass consumes `regexec` match offsets** — a POSIX engine must come along or be replaced by a blob-supplied offset list, and the substitution is what decides reachability. Say which was done.

**ph28 · `concat_function`: the `uint`→`int` store** — `Zend/zend_operators.c:1168`, `:1178` · CRASH-147 · `verbatim` · I11/O2 · echoes p13
`uint res_len = op1->value.str.len + op2->value.str.len;` at `:1168`, then `result->value.str.len = res_len;` at `:1178` stores it into an `int`. At 2 GiB the store goes **negative**, and the *next* concatenation does `memcpy(result->value.str.val + result->value.str.len, …)` at `:1176` — a wild write 2 GiB **below** the buffer.
▸ trigger: `$a .= $b` twice, with `strlen($a)+strlen($b) == 2^31`.
▸ benign: ordinary concatenation; `u64` = the result checksum + length.
▸ blob: **two lengths and a fill byte** — the kernel materialises the strings; the blob is ~9 bytes.
⚠⚠ risk: **~2 GiB resident, twice over (the `erealloc` doubles it).** That is a resource cost, not a shape failure — but a row built from this needs a memory budget stated up front, and it is the only row in the catalogue that does.

**ph29 · `stream_socket_recvfrom`: `emalloc(to_read+1)`** — `ext/standard/streamsfuncs.c:321` · CRASH-097 · `narrowed` · I11/O2 · echoes —
`long to_read` comes from `zend_parse_parameters(…, "rl|lz", …)` at `:309` — i.e. **from userland, not from the socket**. `emalloc(to_read + 1)` at `:321` with `to_read` near `LONG_MAX` wraps to `LONG_MIN`, which as `size_t` is 2^63; `REAL_SIZE(2^63)` truncates to `unsigned int` = **0**, a header-sized block succeeds, and the receive writes into it. FAULT: `:332`.
▸ trigger: `stream_socket_recvfrom($s, PHP_INT_MAX)`.
▸ benign: ordinary reads; `u64` = the received bytes' checksum + `(allocs, frees)`.
▸ blob: a `long` length + the payload bytes that stand in for the socket.
⚠⚠ risk: **one of only two rows where the `_emalloc` truncation is load-bearing** (`PLAN_PHP.md` §4.3). Under plain `malloc`, `malloc(2^63)` fails and PHP exits at `zend_alloc.c:191` — the defect vanishes. This row **must** link `common-php/emalloc_shim.h` and say so.

**ph30 · `bcscale`: an unclamped scale wraps the allocation size** — `ext/bcmath/bcmath.c:542` · CRASH-133 · `narrowed` · I11/O1 · echoes p13
`BCG(bc_precision) = (Z_LVAL_PP(new_scale) < 0) ? 0 : Z_LVAL_PP(new_scale);` clamps **only from below**. `_bc_new_num_ex(length, scale)` (`libbcmath/src/init.c:48-74`) then computes `pemalloc(length+scale)` in `int`, and `_bc_do_add`'s zero-extension loop (`doaddsub.c:63-68`) writes `scale_min - sum_scale` bytes from `sum->n_value + sum_scale + sum_digits`.
▸ trigger: `bcscale(2147483647); bcadd("1","1");`
▸ benign: ordinary bc arithmetic; `u64` = the digit string + `(allocs, frees)`.
▸ blob: two operand digit strings + a scale.
⚠ risk: **no "arbitrary-precision library" is needed** — the defect completes in a 27-line allocator and a 6-line zero-fill, before a single digit is added. Part C records that the kill priced `libbcmath` as a whole.

**ph31 · `SdnToJulian` → `sprintf` into `char[16]`** — `ext/calendar/julian.c:154-199` · CRASH-135 · `verbatim` · I11/O2 · echoes p13
✅ Measured: `SdnToJulian` is a **46-line, fully self-contained function** — it includes only `sdncal.h`, uses three `#define`s and does pure integer arithmetic. `temp = (sdn + JULIAN_SDN_OFFSET) * 4 - 1;` in `long`, then `year = temp / DAYS_PER_4_YEARS;` **stores into `int year`**, so a large `sdn` produces garbage y/m/d. FAULT: `ext/calendar/calendar.c:280 sprintf(date, "%i/%i/%i", month, day, year)` into `char date[16]` declared at `:263`.
▸ trigger: `cal_from_jd(PHP_INT_MAX, CAL_JULIAN)`.
▸ benign: ordinary Julian day numbers convert; `u64` = fold of `(y, m, d)` + the string.
▸ blob: a `long` day number.
⚠ risk: killed as *"needs its own calendar library"*. `julian.c` is 250 lines total and this function is 46 of them with **zero** library dependencies. Part C, F8.

### S4 — declared extent ≠ realised extent

**ph32 · `entity_map`: a range declared here, a table sized there** — `ext/standard/html.c:398`, `:401`, `:896` · CRASH-089, CRASH-090 · `verbatim` · I1/O2 · echoes p27
Each `entity_map` row pairs a `char **` table with a `basechar`/`endchar` codepoint range declared **in a completely different place** from the table literal. The decode loop walks `k` from `basechar` to `endchar` inclusive and indexes `table[k - basechar]` at `:900` and `:905`, with no compiler or runtime relation between the count and the extent.
▸ trigger: any input reaching the top of a short table's range.
▸ benign: ordinary entity decoding; `u64` = fold of the decoded entities.
▸ blob: the text + a charset selector.
⚠⚠ risk: **the corpus records two short tables; there are four.** `ent_uni_spacing` (22 for 23) and `ent_uni_8592_9002` (410 for 411) are also short and are in no corpus row. A build fixing only CRASH-089/090 would still be defective. Cross-reference **ph53**: same C shape, storage sized from the other number, different vulnerability class.

**ph33 · a 2-byte buffer holding a byte that declares a longer one** — `ext/mbstring/php_mbregex.c:624`, `:663-667` · CRASH-128 · `verbatim` · I1/O1 · echoes p27
`char pat_buf[2];` at `:624`, filled at `:663-667` from an integer pattern argument: `pat_buf[0] = (char)Z_LVAL_P(arg_pattern_zval); pat_buf[1] = '\0'; arg_pattern = pat_buf; arg_pattern_len = 1;`. If the byte is a **UTF-8 lead byte** the compiler downstream takes its declared multibyte length from a table and reads that many bytes out of a two-byte stack buffer. FAULT: `k_strcpy`, `ext/mbstring/oniguruma/regparse.c:378`.
▸ trigger: `mb_ereg(0xC3, $s)` under a UTF-8 mbctype.
▸ benign: ASCII integer patterns compile; `u64` = fold of the compiled pattern bytes.
▸ blob: a `long` pattern byte + an encoding selector.
⚠ risk: a **declared** length (from the lead byte's table entry) against a **realised** extent (2 bytes) — ph32/ph53's family, stack-side. The `FIXME: this code is not multibyte aware!` comment at `:661` is upstream's own admission and belongs in the row's notes.

**ph34 · ctype: a user `long` straight into libc's classification table** — `ext/ctype/ctype.c:99-100` · CRASH-122 · `narrowed` · I1/O1 · echoes p02
The `CTYPE` macro's `IS_STRING` arm (`:101-111`) is careful — it casts each byte through `(unsigned char *)` so the argument is always 0..255. The `IS_LONG` arm passes `Z_LVAL_P(c)`, an arbitrary 64-bit user integer, straight into libc `is*()`, which indexes a table offset from `__ctype_b`.
▸ trigger: `ctype_alpha(-100000)`.
▸ benign: ordinary strings and small ints classify; `u64` = fold of the boolean answers.
▸ blob: a list of `long`s + a string.
⚠ risk: whether this over-reads at all depends on the **host libc's** table layout, not on PHP. State the libc and the measured table bounds, or the row is unreproducible.

**ph35 · pcre named-subpattern index: `0xff *` for `0x100 *`** — `ext/pcre/php_pcre.c:448-449` · CRASH-130 · `verbatim` · I11/O1 · echoes p13
`name_idx = 0xff * name_table[0] + name_table[1];` then `subpat_names[name_idx] = name_table + 2;` — the multiplier should be `0x100`, and `name_table[]` is `char`, so on a signed-char platform a high byte contributes a negative term. **The name table is exactly what a blob supplies.**
▸ trigger: a pattern with ≥ 256 named subpatterns, or a name-table byte ≥ 0x80.
▸ benign: ordinary named captures resolve; `u64` = fold of `(name_idx, offset)`.
▸ blob: the two-byte-prefixed name-table bytes + a count.
⚠ risk: PCRE's *matcher* is not needed; only the name table and this loop. An extraction that drags in `pcre_exec` has built a different, unbuildable row.

**ph36 · bison `yycheck[yyx + yyn]`** — `Zend/zend_language_parser.c:3518`, `:3534` · CRASH-005 · `narrowed` · I1/O2 · echoes p19
The generated error-reporting path loops `yyx` over the token names and tests `if (yycheck[yyx + yyn] == yyx)` with `yyn` derived from the parser state — the sum has no upper bound against `yycheck`'s length. Two identical instances.
▸ trigger: a parse error in a state whose `yypact` entry drives the sum past the table.
▸ benign: ordinary parse errors produce correct "expecting …" lists; `u64` = fold of the reported token ids.
▸ blob: a state number + a token id.
⚠ risk: killed as *"the generator owns the table"*. The tables are **bytes of the pristine tarball**, in `php-5.0.0.manifest`, and lift verbatim; only the loop is `narrowed`. Provenance is not one of the four criteria.

### S5 — two passes compute one index differently

**ph37 · `scanf`: validate vs execute** — `ext/standard/scanf.c:383`, `:734` · CRASH-018, CRASH-019 · `narrowed` · I1/O1 + I11/O1 · echoes p23
The validate pass computes `objIndex = value - 1;` (`:383`) **and bounds it** at `:384` (`if ((objIndex < 0) || (numVars && (objIndex >= numVars))) goto badIndex;`). The execute pass computes the same index differently — `objIndex = varStart + value;` (`:734`) — **and does not bound it at all**. FAULT: `:893 current = args[objIndex++];` then a write through `*current`.
▸ trigger: `sscanf($s, '%2$d', $a)` with a positional index the second formula maps out of range.
▸ benign: ordinary positional scanf; `u64` = fold of the assigned values.
▸ blob: format bytes + input bytes + a variable count.
⚠ risk: the kill said *"modelling zvals faithfully"* is required. It is not — `args` is an array of **pointers**; `struct { int len; char *p; }` preserves the defect exactly.

### S6 — an in-place write through an aliased operand

**ph38 · `range()` increments a shared literal in place** — `ext/standard/array.c:1572` · CRASH-077 · `narrowed` · I1/O4 · echoes p49
`for (; *low <= *high; (*low) += (unsigned int)lstep)` writes **into the operand's own buffer**, and an empty PHP string's `Z_STRVAL` points at the shared global `empty_string`. GUARD: `:1537`, the string-branch selector.
▸ trigger: `range("", "z")`.
▸ benign: ordinary character ranges; `u64` = fold of the emitted characters.
▸ blob: two operand strings + a step.
⚠ risk: routed away by the spatial miner as *"a value-model property, not a spatial one"* and never picked up by anyone. The **write to a shared read-only object** is spatial; the aliasing is the *reason*, not the class. If the extraction gives each operand its own buffer, the row evaporates — the shared literal must be modelled.

## TYPE / INITIALISATION

### T1 — a union member read without an adequate tag check

**ph39 · no tag check at all** — `Zend/zend_exceptions.c:551` · CRASH-036, CRASH-037, CRASH-101 · `narrowed` · I4/O1 · echoes p35
A zval is a hand-rolled tagged union (`Zend/zend.h:275-293`): a `zvalue_value` union plus a separate `zend_uchar type`. `Z_STRVAL_P` / `Z_ARRVAL_P` (`zend_operators.h:234-275`) expand **directly** to `(zval).value.str.val` / `.value.ht` and **consult no tag**. Near-duplicates at `:339` and `streamsfuncs.c:775,817`.
▸ trigger: an exception whose `file` property has been set to a `long`.
▸ benign: ordinary property reads; `u64` = fold of the read values.
▸ blob: a record stream of `(tag, payload)` pairs.
⚠ risk: the property table can be a fixed-slot array — a real `HashTable` is not needed and importing one buries the mechanism.

**ph40 · presence checked, type not** — `ext/standard/info.c:640-651` · CRASH-093 · `narrowed` · I4/O3 · echoes p35
Four consecutive blocks do `if (zend_hash_find(&EG(symbol_table), "PHP_SELF", …, &data) != FAILURE) …(Z_STRVAL_PP(data))`. The lookup establishes that the **key exists**; the code treats that as licence to read the **value** as a `char *`. FAULT: `:828`.
▸ trigger: `$PHP_SELF = 42;` then `phpinfo()`.
▸ benign: ordinary string variables print; `u64` = the output checksum.
▸ blob: a key/value record stream.
⚠⚠ risk: this row's distinctness rests entirely on the **presence check plus a null-check that cannot help**. `spec.md` must pin the useless null-check as mandatory; if the extraction drops it, ph40 **is** ph39 (adjudication §4).

**ph41 · container checked, elements not** — `Zend/zend_exceptions.c:293` · CRASH-039 · `narrowed` · I4/O1 · echoes p35
`_build_trace_string`'s first statement is `HashTable *ht = Z_ARRVAL_PP(frame);` — it assumes every element of the `trace` array is itself an array. `:304` then does `zend_hash_find(ht, "file", …)` on a wild pointer, and `:310-311` performs a **second** unguarded read on what it found. FAULT: `Zend/zend_hash.c:850`.
▸ trigger: a `trace` array with a `long` element.
▸ benign: ordinary traces render; `u64` = the rendered string's checksum.
▸ blob: a nested record stream — the malformed element is planted directly, which is simpler than the PHP reproducer.
⚠ risk: the container/element split is the mechanism. Do not fold into ph39.

**ph42 · a guard that passes, on the wrong tag namespace** — `Zend/zend_compile.c:1196-1197` · CRASH-144 · `narrowed` · I4/O1 + I3 · echoes p38
✅ PHP 5.0.0 has **two unrelated `IS_*` enumerations whose values collide**: `zend_compile.h:285-288` gives the *operand-kind* tag `IS_CONST=1, IS_TMP_VAR=2, IS_VAR=4, IS_UNUSED=8`; `zend.h:387-396` gives the *value-type* tag `IS_NULL=0, IS_LONG=1, IS_DOUBLE=2, IS_STRING=3, IS_ARRAY=4`. The guard tests `last_op->op2.op_type == IS_CONST` and then reads `op2.u.constant.value.str.val` / `.str.len` with **no `Z_TYPE` check**. A guard that is present and *passes* while interrogating the wrong namespace.
▸ trigger: a one-line script; it crashes during **compilation**.
▸ benign: ordinary method calls compile; `u64` = fold of the emitted opcodes.
▸ blob: an operand record stream.
⚠ risk: the harm has **two limbs in one expression** — `.str.val` overlays an attacker `lval` while `.str.len` reads bytes the `lval` write never touched. The only row labelled both `I4` and `I3`; report both limbs or the row understates itself.

**ph43 · `HASH_OF` laundering, misused in opposite directions** — `Zend/zend_API.h:519` with `ext/standard/array.c:2688-2695` and `ext/standard/url.c:612-613` · CRASH-079, CRASH-111 · `narrowed` · I4/O1 + I4/O3 · echoes p35
**One row, two limbs** (adjudication §4). `HASH_OF(p)` returns a valid `HashTable*` for **both** arrays and objects, and NULL otherwise. `array_unique` uses it *as its type check* — result null-checked, then over-concluded to be an array (`:2688-2695`, confused `Z_ARRVAL_P` read at `:2728/:2730`). `get_headers` does not check it **at all** and hands it straight to the hash walkers. FAULT: `Zend/zend_hash.c:460`.
▸ trigger: `array_unique([$obj])` / `get_headers()` on a wrapper whose `wrapperdata` is a scalar.
▸ benign: arrays work in both; `u64` = fold of the walked elements.
▸ blob: a `(tag, payload)` record stream + a call-site selector.
⚠ risk: **the pairing is the finding.** Two rows would double-count a ladder cost paid once — the laundering helper is extracted once and both call sites are three lines each.

**ph44 · type inferred from the creation path** — `ext/standard/basic_functions.c:2970-2978` · CRASH-085 · `narrowed` · I4/O1 · echoes p35
Find-or-create: the create arm calls `array_init` at `:2973`, so a created entry is certainly an array; the found arm is a bare `hash = *find_hash;` at `:2977` and asks no questions. The author's warrant is *"entries here are always arrays because THIS path made them"* — while another path inserts scalars. FAULT: `:2996 add_next_index_zval(hash, …)`.
▸ trigger: an ini file redeclaring a scalar key as a section.
▸ benign: ordinary sections parse; `u64` = fold of the parsed entries.
▸ blob: the record stream; the ini parser is not needed.
⚠ risk: the two insertion paths must both be present. An extraction with one path has no defect.

**ph45 · a heap pointer stored in an `int` field** — `ext/mbstring/libmbfl/mbfl/mbfl_convert.h:49` with `ext/mbstring/libmbfl/filters/mbfilter_htmlent.c:161`, `:169`, `:178`, `:183` · CRASH-123 · `verbatim` · pointer-value-integrity · echoes p38
`int cache;` (`mbfl_convert.h:49`) holds a **heap pointer**: `:161 filter->cache = (int)mbfl_malloc(html_enc_buffer_size+1);` truncates on 64-bit; `:169 mbfl_free((void*)filter->cache);` is a wild free; `:178 char *buffer = (char*)filter->cache;` sign-extends it back; `:183 buffer[0] = '&';` is a wild write. **Five lines**, spanning one struct field and two functions; the struct reduces to three fields.
▸ trigger: any `&`-containing input through the html-entity decode filter on a 64-bit build.
▸ benign: entity decoding round-trips; `u64` = the decoded bytes + `(allocs, frees)`.
▸ blob: the text bytes.
⚠ risk: **cite `:178` and `:183`.** `ADJUDICATION_001.md` §0/§1b give `:177` and `:181` — off by one and two (report §2.3); the CSV's `:183` is right. The row needs no filter chain, no encoding tables and no oniguruma. **The only row in 166 with its own invariant.**

**ph46 · one untagged union, two ways to get it wrong** — `Zend/zend_execute.c:138-151` and `:198-217` · CRASH-053, CRASH-056 · `narrowed` · I4/O1 · echoes p35
**Paired; do not split.** `temp_variable` (`zend_execute.h:30-43`) is a union whose live arm depends on how the operand was fetched — an ordinary variable populates `var`, a string offset (`$s[0]`) populates `str_offset` — and **it carries no tag**. Both call sites discriminate on `var.ptr_ptr`'s NULL-ness, a **sibling member**, not a tag. `zend_switch_free` (`:198-217`) reads that discriminant out of a temp slot the compiler never initialised. `_get_zval_ptr_ptr` (`:138-151`) uses it correctly for the unlock at `:141-146` and then **returns `T(...).var.ptr_ptr` unconditionally** at `:147` — i.e. returns the NULL it just detected. FAULT: `:283`, the first line of `make_real_object`.
▸ trigger: `$s = "x"; $s[0]->p += 1;` / a `switch` whose case body a function declaration splits.
▸ benign: ordinary variable and string-offset operands both work; `u64` = fold of the fetched values.
▸ blob: an operand record stream carrying `(op_type, arm, payload)`.
⚠⚠ risk: **the corpus's `root_cause_id` for CRASH-053 is wrong twice.** *"unchecked `make_real_object`"* — `:1635` **does** check `object->type != IS_OBJECT`, and `make_real_object` (`:280-292`) is a correct 12-line function guarding all three arms. `object_ptr` was never valid. ⚠ And `ADJUDICATION_001.md` §7b's *"reads the `var` arm with no test at all"* is also wrong: the test is at `:141`; the bug is that the **return** ignores it (report §3.2).

### T2 — a type-changing write through a value that was not separated

**ph47 · the separator that no-ops exactly when it matters** — `Zend/zend.h:568-571` with `ext/standard/string.c:1935-1949`, `:2077` · CRASH-104, CRASH-058 · `narrowed` · I4/O2 · echoes p49
`convert_to_long_ex` expands to `convert_to_ex_master` (`zend_operators.h:210-214`): `if (type != IS_LONG) { SEPARATE_ZVAL_IF_NOT_REF(ppzv); convert_to_long(*ppzv); }`. `SEPARATE_ZVAL_IF_NOT_REF` is `if (!PZVAL_IS_REF(*ppzv)) SEPARATE_ZVAL(ppzv);` — **a no-op exactly when `is_ref == 1`** — so the conversion degrades from copy-on-write to **in-place retype**, invalidating a check that did hold. Callee side (CRASH-104) and caller side (CRASH-058, `zend_execute_API.c:730-753`) of one defect. FAULT: `:2116-2126`, a `memcpy` bounded by a now-stale length.
▸ trigger: `substr_replace($s, $r, $lenRef)` with `$lenRef` a reference to an array element that also feeds the length.
▸ benign: ordinary conversions copy; `u64` = fold of the converted values + lengths.
▸ blob: a record stream with a `shared` bit per value.
⚠ risk: no refcounting GC is needed — a boolean `shared` bit reproduces it. Importing refcounts adds a second mechanism (ph69/ph70) to a row that is not about them.

**ph48 · the same helper used to FORCE the shared flag on** — `Zend/zend_execute_API.c:608-610` · LOGIC-017 · `narrowed` · I4/O2 · echoes p49
```c
608  SEPARATE_ZVAL_IF_NOT_REF(tmp_object_ptr);
609  fci->object_pp = tmp_object_ptr;
610  (*fci->object_pp)->is_ref = 1;
```
It **stamps `is_ref` ON** a caller's by-value slot, where ph47 fails to separate. Opposite direction, same invariant — `PLAN_PHP.md` §3.1's slight variation.
▸ trigger: `call_user_func_array([$obj, 'm'], …)` where `$obj` is a by-value copy shared with a live variable.
▸ benign: ordinary callable arrays dispatch; `u64` = fold of `(is_ref, refcount)` per slot.
▸ blob: a slot record stream + a call-site selector.
⚠ risk: `crashes_pristine_5_0_0 = n/a (non-crash class)` — the harm is a silently broken CoW separation, visible in the checksum, not in a sanitizer. Fold `(is_ref, refcount)` into the `u64` or the row measures nothing.

### T3 — initialised before read

**ph49 · the count is decremented after the destructor** — `Zend/zend_hash.c:466-497` · CRASH-153 · `narrowed` · I3/O3 · echoes p34
`zend_hash_del_key_or_index` fully unlinks the bucket from `arBuckets`, `pListHead`, `pListTail` and `pInternalPointer` at `:467-488`, calls the element destructor at `:489-491`, and only decrements `ht->nNumOfElements` at `:497` — **outside** the `HANDLE_BLOCK_INTERRUPTIONS` window opened at `:466`. At PHP 5.0 the destructor is arbitrary userland, so the count is observably too large for the duration of the call. CONSUMER: `ext/standard/array.c:1884-1894`.
▸ trigger: a `__destruct` that calls `array_pop` on the same array.
▸ benign: ordinary deletes; `u64` = fold of `(count, elements)` after each operation.
▸ blob: an operation stream; the destructor is a function pointer the kernel supplies.
⚠ risk: **no userland and no objects are needed** — the blob decides which callback the destructor pointer names. An extraction that reaches for the executor has built a different row.

**ph50 · a discarded status code leaves an out-parameter unwritten** — `ext/standard/array.c:1893-1894` · CRASH-153 · `verbatim` · I3/O1 · echoes p42
`_phpi_pop` gates on `zend_hash_num_elements(...) == 0` at `:1884`, positions the internal pointer, then calls `zend_hash_get_current_data(…, (void **)&val)` at `:1893` **without storing or testing its SUCCESS/FAILURE result**, and dereferences the never-assigned automatic at `:1894 *return_value = **val;`.
▸ trigger: any path where the emptiness gate and the real emptiness disagree — ph49 supplies one.
▸ benign: ordinary pops; `u64` = fold of the popped values.
▸ blob: an operation stream.
⚠ risk: **split from ph49 deliberately** (adjudication §4) — this kernel does not need re-entrancy at all; a stale count from any source will do. Merging them hides that.

**ph51 · uninitialised struct fields consumed as function pointers** — `ext/standard/dir.c:369`, `:394-395` · CRASH-087 · `modelled` · I3/O2 · echoes p36
`glob_t globbuf;` is a bare automatic at `:369` — no initialiser, no memset — and only `globbuf.gl_offs = 0;` is written, at `:394`. The `flags` argument is an unvalidated user `long` (`:368`, `:373`) and the mask it passes through, `GLOB_FLAGMASK`, is `(~0)` on the branch taken (`:164`) — it masks **nothing**. Setting `GLOB_ALTDIRFUNC` makes the callee call through fields the caller never wrote.
▸ trigger: `glob($p, 512)` on a build where `GLOB_ALTDIRFUNC` is 512.
▸ benign: ordinary globs; `u64` = fold of the matched names.
▸ blob: a pattern + a `long` flags word.
⚠ risk: `modelled` — the real defect needs libc's `glob()`. The extraction must supply its own callee honouring an ALTDIRFUNC-like bit, which is faithful to the mechanism (uninit fields consumed as callbacks) but is a re-implementation. **Say so in `spec.md`**, and do not claim `verbatim`.

**ph52 · an unconstructed caller slot destructed on an early exit** — `Zend/zend.c:242-247` · LOGIC-007 · `narrowed` · I3/O1 · echoes p42
`zend_make_printable_zval` receives `expr_copy`, an **uninitialised** zval the caller declared on its own stack (`zend_operators.c:1148`) for the callee to fill in. On the `IS_OBJECT` arm, a pending exception takes the early exit at `:242-247`, which calls `zval_dtor(expr_copy)` — a tag-dispatched teardown over a tag byte that was never written.
▸ trigger: a `__toString` that throws.
▸ benign: ordinary string conversions; `u64` = the printable string + `(allocs, frees)`.
▸ blob: a value record stream + a failure flag.
⚠ risk: no exceptions are needed; a failure flag suffices. The **uninitialised tag byte driving a switch** is the mechanism — an extraction that zero-initialises the slot for tidiness deletes it.

**ph53 · storage grown to the COUNT, tail never written** — `Zend/zend_compile.c:2569-2572` · CRASH-158 · `verbatim` · I19/O2 · echoes p27
`zend_do_end_class_declaration` ereallocs `ce->interfaces` to `sizeof(zend_class_entry*) * ce->num_interfaces` **without zeroing the new tail**, at a point where `num_interfaces` is already the full **declared** count while the slots are still filled one at a time by runtime `ZEND_ADD_INTERFACE` opcodes. FAULT: `Zend/zend_operators.c:1534-1535` (`instanceof_function_ex`); compare-only read at `zend_compile.c:1951`.
▸ trigger: an `instanceof` between the class declaration and the last `ADD_INTERFACE`.
▸ benign: ordinary class declarations; `u64` = fold of the interface pointers read.
▸ blob: `{ptr, count}` grown by `erealloc`, filled by a second pass, queried in between.
⚠⚠ risk: **axis reassigned** (adjudication §2 item 8) — both miners reached for spatial/temporal, but the read is *in bounds* (inside the reallocated block) and nothing is freed. CWE-824 and `I3` put it here. ⭐ **Same C shape as ph32**, differing only in which of two numbers the storage was sized from: ph32 sizes to the literal (excess is past the end → CWE-125), ph53 sizes to the count (excess is inside → CWE-824). **Cross-reference, do not merge.**

### T4 — the guard is at the wrong depth

**ph54 · `!p` where `!*p` was meant** — `Zend/zend_execute.c:3831-3832` · CRASH-143 · `narrowed` · I16 · echoes —
`value` is a `zval **`. `get_current_data(iter, &value)` at `:3831` sets `value` to point **at** the iterator's internal `zval *` slot, so `value` is unconditionally non-NULL; the guard at `:3832` is `if (!value)` — depth 1 — and can therefore **never fire**. The property that matters is `*value != NULL`. FAULT: `:3850-3853 (*value)->refcount++`.
▸ trigger: a user iterator whose `current()` throws.
▸ benign: ordinary iteration; `u64` = fold of the yielded values.
▸ blob: a record stream + a per-step failure flag.
⚠ risk: only a two-level out-parameter and a callback that can fail are needed. Iterators and exceptions are scenery.

### T5 — the emitted program is not the one the executor implements

**ph55 · an early exit strides 1 over a two-word instruction** — `Zend/zend_execute.c:1761-1770` · CRASH-023 · `verbatim` · I18 + I12 · echoes p19
Compound assignment to an array dimension is a **two-word** instruction: the opcode word plus a trailing `ZEND_OP_DATA` word carrying the extra operands (`zend_op *op_data = opline+1`, `:1742`); the handler sets `increment_opline = 1` at `:1749`. The error path exits via `NEXT_OPCODE()` (stride 1) at `:1761-1770` while the normal exit at `:1792-1795` correctly strides 2 — so the trailing **data** word is decoded as an instruction, and `zend_opcode_handlers[ZEND_OP_DATA] = NULL` (`:4427`) is then indirect-called.
▸ trigger: `$x = 1; $x[0] += 1;`
▸ benign: ordinary compound assignments; `u64` = fold of the executed opcodes.
▸ blob: **the instruction stream itself.**
⚠ risk: ⭐ the one candidate whose **original C shape IS the pinned kernel shape** — an instruction array, a PC, a dispatch table with a NULL entry, a two-word form. No zvals strictly required.

**ph56 · opcode selected by arithmetic, guard on some arms only** — `Zend/zend_compile.c:751-775` · CRASH-041 · `narrowed` · I18 + I12 · echoes p19
Opcode families are laid out at fixed strides and the compiler selects a variant by **arithmetic on the opcode value**: `-= 3` read, `+= 3` read-write, `+= 6` isset, `+= 9` func-arg, `+= 12` unset (`:756`, `:761`, `:764`, `:767`, `:774`). Two arms guard against the illegal append-dim combination (`:752-757`, `:770-775`); the arm at `:763-765` does not.
▸ trigger: `isset($a[])`.
▸ benign: ordinary dim fetches compile and execute; `u64` = fold of the emitted opcodes.
▸ blob: an AST-ish record stream.
⚠ risk: the executor must have **no handler** for the illegal combination — an extraction with a total dispatch table has removed the harm.

**ph57 · the same switch, a LOCK not taken on one arm** — `Zend/zend_compile.c:3271-3275` · CRASH-028 · `narrowed` · I18/O2 · echoes p19
`ZEND_FETCH_ADD_LOCK` is or-ed into `extended_value` **only** when the preceding `ZEND_FETCH_OBJ_W`'s `op1.op_type == IS_VAR` (`:3273-3274`). By-ref `foreach` over a string-offset container takes the other arm, the container is not locked, and the executor dereferences an invalid pointer.
▸ trigger: `foreach ($s[0] as &$v) {}`.
▸ benign: ordinary by-ref foreach; `u64` = fold of `(lock_taken, refcount)`.
▸ blob: an operand-kind record stream.
⚠ risk: `PLAN_PHP.md` §3.1's slight variation of ph56 — a lock **not taken** vs a guard **not replicated**. Legitimately its own row; do not re-tighten.

**ph58 · the emitter returns 0 without emitting the free** — `Zend/zend_compile.c:1451-1457` · CRASH-055 · `narrowed` · I18/O2 · echoes p19
`generate_free_switch_expr` returns 0 **without emitting `ZEND_SWITCH_FREE`** unless the switch operand is `IS_VAR` or `IS_TMP_VAR`. The executor still expects the free. An emitter with an operand-kind guard plus an executor expecting the emission — ph55/ph56's shape from the compiler side.
▸ trigger: a `switch` whose case body is split by a function declaration.
▸ benign: ordinary switches emit and free correctly; `u64` = fold of `(emitted_opcodes, frees)`.
▸ blob: an operand-kind record stream.
⚠ risk: killed as *"the defect is in the compiled program, not in a computation over a byte blob"* — refuted by ph55/ph56, whose blob **is** the instruction stream.

### T6 — a fallible call whose failure is not tested

**ph59 · precedence makes the guard test the opposite** — `ext/standard/array.c:4085` · CRASH-082 · `verbatim` · I12/O1 · echoes —
```c
4085  if (!zend_call_function(&fci, &fci_cache TSRMLS_CC) == SUCCESS && result) {
```
`!f(x) == SUCCESS` parses as `(!f(x)) == SUCCESS`. With `SUCCESS == 0`: a **successful** call gives `!0 == 0` → false (guard skipped, correct); a **failed** call gives `!(-1) == 0` → true, but `result` is then NULL so `&& result` is false and the error branch is **skipped too**. Execution continues with a NULL result.
▸ trigger: an `array_map` callback that cannot be called.
▸ benign: ordinary `array_map`; `u64` = fold of the mapped values.
▸ blob: a value stream + a per-element failure flag.
⚠ risk: killed as *"a precedence typo, not a type mechanism"*. **Mechanism *quality* is not one of `PLAN_PHP.md` §3's four criteria**; mechanism *distinctness* is, and a guard whose parse differs from its reading is distinct from every other row here. Part C, F9.

**ph60 · a fallible call's failure not tested before its result is used** — `ext/standard/ftp_fopen_wrapper.c:649-652` · CRASH-088, CRASH-061, CRASH-126, CRASH-163 · `verbatim` · I12/O1 + I16 · echoes —
One family, four sites, catalogued as **one** row (§3.1 exact-duplication kill applied *within* the family, not to it). `php_ftp_fopen_connect(...)` at `:649` can return NULL and `:652 php_stream_write_string(stream, "TYPE A\r\n")` uses it unconditionally. Siblings: `zend_object_handlers.c:513` (missing NULL check after `offsetUnset` bails), `mbstring.c:3219` (optional arg defaults to NULL, passed to `strcasecmp`), `zend.c:1083` (a failed user exception handler leaves `EG(exception)` NULL).
▸ trigger: a URL with no path / an `offsetUnset` that bails / a missing optional argument.
▸ benign: ordinary calls succeed and their results are used; `u64` = fold of the results.
▸ blob: a call-outcome stream.
⚠ risk: the wave killed all four as *"ordinary null-deref"*. That is a **quality** judgement, which the bar does not carry; the correct application is one family row plus three duplication kills. Cross-reference **ph87**'s CRASH-129 limb (`I12/O1`), which is the same obligation with a *stack* consumer.

## TEMPORAL

### E1 — a container reallocates under a live interior pointer

**ph61 · the argument stack doubles under a raw `zval **`** — `Zend/zend_ptr_stack.h:44-52` · CRASH-155, CRASH-075, CRASH-081, CRASH-083, CRASH-117 · `verbatim` · I10/O1 + I10/O3 · echoes p25
`EG(argument_stack)` is a `zend_ptr_stack`: a `void **elements` block plus `top`/`max`/`top_element`. `zend_ptr_stack_push` **doubles it with `erealloc` the moment `top >= max`** and fixes up only its own `top_element` — nothing else. `zend_get_parameters_ex` hands callers raw `zval **` into that block; five drivers hold one across a call that pushes.
▸ trigger: a callback invoked from a driver holding a parameter pointer, deep enough to force the double.
▸ benign: ordinary parameter fetches; `u64` = fold of the fetched values + `(allocs, frees)`.
▸ blob: an opcode stream; the re-entrant callee is one opcode.
⚠ risk: ✅ the whole header is **68 lines** (the miner said 60), with no zval, no TSRM and no `emalloc` beyond `erealloc`. The five call sites are `narrowed`; the container is `verbatim`.

**ph62 · the same growth under a cached interior pointer** — `Zend/zend_objects_API.c:129-165` · CRASH-046, CRASH-070 · `verbatim` · I10/O1 + I10/O3 · echoes p25
`zend_objects_store_del_ref` caches `obj = &object_buckets[handle].bucket.obj` at `:132`, then calls the **userland** destructor at `:144`. If that destructor allocates objects, `zend_objects_store_put` reaches `top == size` and ereallocs `object_buckets` (`:91-94`); `obj` now points into the freed block and `:147`/`:156` read and write through it. Sibling in a different container: `zend_compile.c:1301-1327` (cache at `:1305`, growth at `:1319` via `get_next_op` → `zend_opcode.c:259-280`).
▸ trigger: a `__destruct` that constructs objects.
▸ benign: ordinary object teardown; `u64` = fold of `(handle, refcount)` + `(allocs, frees)`.
▸ blob: an operation stream; the dtor is a function pointer.
⚠ risk: distinct from ph61 in **where the pointer came from** — cached by the same function vs handed out to a caller. Two rows, one shape; keep both (§3.1).

**ph63 · the cursor type IS a bare node pointer** — `Zend/zend_hash.h:88` · CRASH-002, CRASH-022, CRASH-040 · `narrowed` · I10/O1 + I10/O3 · echoes p28
✅ `typedef Bucket* HashPosition;` — the cursor is **not an index**, and `zend_hash_move_forward_ex` advances it by `*current = (*current)->pListNext`. `php_array_walk` holds one across `zend_call_function` (`array.c:1045`) and dereferences it at `:1062`. FAULT: `array.c:1062` — which is what the corpus's `c_file_line` names, while the **mechanism** is `zend_hash.h:88` (`RECAP_PHP.md` F1's original case).
▸ trigger: a callback that unsets the element the cursor names.
▸ benign: ordinary array walks; `u64` = fold of the visited keys.
▸ blob: an operation stream; the callback is kernel-supplied.
⚠ risk: `zend_hash` is a self-contained container and lifts whole; only the zval payload and the `zend_call_function` wrapper come off.

**ph64 · the callee unlinks the element the loop holds** — `Zend/zend_llist.c` (`zend_llist_apply`) · CRASH-086 · `verbatim` · I10/O1 · echoes p28
`for (element = l->head; element; element = element->next) func(element->data)` — with **no protection against `func` unlinking `element`**. `user_tick_function_call` is such a `func`: its callback may call `unregister_tick_function`, which `zend_llist_del_element`s and frees the element the loop is standing on. FAULT: `ext/standard/basic_functions.c:2135 tick_fe->calling = 0;` — a **write** through the freed element.
▸ trigger: a tick function that unregisters itself.
▸ benign: ordinary tick dispatch; `u64` = fold of the invoked ids + `(allocs, frees)`.
▸ blob: a registration/unregistration stream.
⚠ risk: `zend_llist` is ~200 lines with an inline `char data[1]` payload and `zend_llist_apply` is eight lines. The **write after free** is the interesting half; an extraction that only reads understates it.

### E2 — released, then still named

**ph65 · a back-reference table retains what the parser freed** — `ext/standard/var_unserializer.c:875-893`, `:176-186` · CRASH-121, CRASH-118 · `modelled` · I5/O3 + I5/O2 · echoes p27
The unserializer keeps `var_hash`, a flat back-reference table of every zval it has produced so `r:N;` / `R:N;` can point back at entry N. The `r:` handler does `if (*rval != NULL) zval_ptr_dtor(rval);` at `:887` and then `*rval = *rval_ref; (*rval)->refcount++;` at `:889-890` — but the zval it just released is **still in `var_hash`**. CRASH-118: `zend_hash_update` at `:181` destroys a zval the table still tracks.
▸ trigger: `a:1:{i:0;r:1;}` shapes that back-reference a slot the handler has just released.
▸ benign: ordinary back-references resolve; `u64` = fold of the resolved values + `(allocs, frees)`.
▸ blob: the serialised bytes.
⚠ risk: `modelled` — the parser is a re2c state machine over zvals. **The mechanism narrows cleanly** to a growable table of raw pointers to values the parser also frees; the re2c body need not come along. Say which was built.

**ph66 · a numeric bucket's key is never compared** — `Zend/zend_hash.c:464-465` · LOGIC-001 · `verbatim` · I7/O2 + I7/O3 · echoes p22
```c
464  if ((p->h == h) && ((p->nKeyLength == 0) ||       /* Numeric index */
465      ((p->nKeyLength == nKeyLength) && (!memcmp(p->arKey, arKey, nKeyLength))))) {
```
For a **numeric** bucket `nKeyLength` is 0, so the left disjunct fires and the key is **never compared at all** — hash equality alone is treated as identity. A colliding string-key delete destroys an unrelated live element.
▸ trigger: a string key whose DJBX33A hash over `len+1` equals a live integer index.
▸ benign: ordinary deletes remove the right element; `u64` = fold of the surviving keys.
▸ blob: an insert/delete key stream.
⚠⚠ risk: **it produces no fault — a silent wrong answer.** ✅ That is a classification, not a kill (`CLAUDE.md` rule 6; `p29` shipped this shape) and it is the **best checksum-visible row in the corpus, with the allocator entirely out of the picture.** The DJBX33A preimage the fixture needs was never computed; compute it before building.

**ph67 · the destructor runs while the bucket is still linked** — `Zend/zend_hash.c:214-236` · CRASH-160, CRASH-154 · `verbatim` · I10/O1 + I5/O1 · echoes p28
The update arm of `_zend_hash_add_or_update` calls `ht->pDestructor(p->pData)` at `:229` while bucket `p` is **still linked into both of the table's lists and still advertises the dead payload**, then keeps using `p` at `:231` (`UPDATE_DATA`) and `:233` (`*pDest = p->pData`). Sibling: `Zend/zend_variables.c:47-56` — `zend_hash_destroy` at `:52` with `zvalue->type` still `IS_ARRAY` and `zvalue->value.ht` still live.
▸ trigger: a destructor that re-enters the same table.
▸ benign: ordinary updates; `u64` = fold of the stored payloads + `(allocs, frees)`.
▸ blob: an insert/update stream; the destructor is kernel-supplied.
⚠ risk: `verbatim` for CRASH-160 (zend_hash alone); `narrowed` for CRASH-154 (needs the zval tag). Declare the tier per limb or the provenance overlap will disagree with the claim.

**ph68 · a recycled handle with no generation tag** — `Zend/zend_execute_API.c:617-626` · CRASH-030, CRASH-045, CRASH-044 · `verbatim` · I17/O4 + I17/O1 · echoes p27
The object store recycles slots through a free list (`ZEND_OBJECTS_STORE_ADD_TO_FREE_LIST` sets `valid = 0` and pushes the handle; `zend_objects_store_put` pops it back at `:87-89`) but the handle carries **no generation tag**. A zval still holding the old handle resolves, through the same index, to a **different live object**. The missing `!object_buckets[handle].valid` guard is at `:617-626`; FAULT: `:625 Z_OBJCE_PP(fci->object_pp)`.
▸ trigger: destroy an object, allocate another, then call a method through the stale handle.
▸ benign: ordinary handle lookups; `u64` = fold of the resolved payload words.
▸ blob: a create/destroy/lookup stream.
⚠ risk: the handle table alone lifts; the class-entry dereference becomes a payload-word read. Do not import the object model.

### E3 — the reference count does not equal the number of holders

**ph69 · two owning slots, one allocation, no increment** — `ext/pcre/php_pcre.c:584-593` · CRASH-131 · `narrowed` · I7/O1 · echoes p34
In the `PREG_PATTERN_ORDER` tail each `match_sets[i]` (refcount 1, one owner) is written into the result array **twice** — under the subpattern name at `:587-588` and at the next integer index at `:590` — with **no `ZVAL_ADDREF` between**. Two owning slots now name one allocation with a count of one.
▸ trigger: any pattern with a named subpattern.
▸ benign: unnamed patterns store once; `u64` = fold of `(refcount, payload)` per slot + `(allocs, frees)`.
▸ blob: a `(named?, value)` record stream.
⚠ risk: **split from ph70 deliberately** (adjudication §2 item 6) — a **missing increment** breaks `I7` from the opposite direction to an **unmatched decrement**. Different C; two rows.

**ph70 · a decrement taken by a party that never incremented** — `Zend/zend_object_handlers.c:392-395` · CRASH-047, CRASH-099, CRASH-103, CRASH-080 · `narrowed` · I7/O2 + I9/O2 · echoes p34
The over-decrement half of `I7`: a releasing party drops a count it never took. Four sites — `zend_object_handlers.c:392-395`, `streamsfuncs.c:681`, `string.c:1412-1413`, `array.c:3804`.
▸ trigger: a path that reaches the release twice, or with a borrowed value.
▸ benign: matched increments and decrements; `u64` = fold of `(refcount)` + `(allocs, frees)`.
▸ blob: an acquire/release stream.
⚠ risk: the `u64` must carry the refcount, not just the payload — this row's harm is invisible in the payload until the free lands.

**ph71 · the container is destroyed, then a pointer derived from it is read** — `Zend/zend_execute.c:220-278` · CRASH-004, CRASH-003, CRASH-025, CRASH-067 · `modelled` · I2/O4 + I2/O1 · echoes p28
`zend_assign_to_variable_reference` decrements and, at zero, `zendi_zval_dtor` + `FREE_ZVAL`s the **destination container** at `:236-240`, and only then reads `value_ptr->is_ref` at `:242` — but `value_ptr` can be an element *inside* the container just destroyed (`$a = array(1); $a = &$a[0];`). CRASH-003: the destroy at `:629` / free at `:634`, the write through `*variable_ptr_ptr` at `:669`.
▸ trigger: `$a = array(1); $a = &$a[0];`
▸ benign: ordinary reference assignment; `u64` = fold of `(refcount, is_ref)` + `(allocs, frees)`.
▸ blob: an assignment stream over a container of boxes.
⚠ risk: `modelled` — the surrounding function is dense executor plumbing (`temp_variable`, `znode` operand kinds, `PZVAL_LOCK`). The mechanism re-expresses in a few lines; declare the deletions individually.

**ph72 · allocated on one arm, released on every arm** — `ext/standard/array.c:993-1063` · CRASH-074, CRASH-125, CRASH-112 · `narrowed` · I5/O2 + I5/O1 · echoes p42
`php_array_walk` declares `zval *key;` **uninitialised** at `:997`, calls `MAKE_STD_ZVAL(key)` only at `:1024` inside the else-arm, and does an unconditional `zval_ptr_dtor(&key)` at `:1061` on **every** arm — so the first iteration taking the `recursive && IS_ARRAY` arm frees an uninitialised stack pointer, and every later one frees the previous iteration's released key. Siblings: `mbstring.c:2196-2231` (`efree(list)` at `:2200` without `list = NULL`, second `efree` at `:2229-2230`), `user_filters.c:140`.
▸ trigger: a recursive `array_walk` over a nested array.
▸ benign: ordinary walks; `u64` = fold of the visited keys + `(allocs, frees)`.
▸ blob: a nested record stream.
⚠ risk: the **uninitialised** first free and the **double** later free are two different faults from one line. Record which fired.

### E4 — storage of the wrong provenance enters the value graph

**ph73 · automatic storage published where user code can retain it** — `Zend/zend_object_handlers.c:520-592` · CRASH-052, CRASH-051, CRASH-027, CRASH-032, CRASH-100 · `narrowed` · I14/O1 · echoes p34
✅ Five sites, **one idiom**, read at source: `zval local; publish(&local); run userland; return`. `zend_std_call_user_call` declares `zval method_name, method_args, __call_name;` at `:524`, publishes their addresses into `call_args` at `:561-570`, calls userland `__call`, and tears down at `:587-588`. Siblings: `zend_execute.c:1138` (`zval tmp` → `__get`), `zend_execute_API.c:881` (→ `__autoload`), `zend_objects.c:34` (→ dtor as `$this`), `streamsfuncs.c:728` (→ a userland notifier).
▸ trigger: a `__call` that stores its argument array in a global.
▸ benign: ordinary magic-method calls; `u64` = fold of the returned values + `(allocs, frees)`.
▸ blob: a call stream; the "userland" callee is kernel-supplied and its retention is one blob bit.
⚠ risk: **CRASH-139 is NOT in this idiom and is split out to ph74** (adjudication §2 item 6) — its CWE is 590, not 562.

**ph74 · a non-owned literal adopted as an owned member** — `Zend/zend_API.c:1957`, `:1965-1966` · CRASH-139 · `narrowed` · I14/O4 + I5/O4 · echoes p49
```c
1957  zval property, *value;
1965  ZVAL_STRINGL(&property, name, name_length, 0);
1966  value = Z_OBJ_HT_P(object)->read_property(object, &property, silent TSRMLS_CC);
```
The `dup = 0` argument makes `property.value.str.val` **alias a caller-owned literal**. The harm is not the stack escape — it is that userland's argument stack later **frees a pointer that was never an allocator return**.
▸ trigger: a `__get` that retains the property-name zval.
▸ benign: ordinary property reads; `u64` = fold of the read values + `(allocs, frees)`.
▸ blob: a property-name stream + a retention bit.
⚠ risk: routed to ph76's provenance family, not ph73's. If it is built beside ph73, the `spec.md` must say which invariant each is about or the pair reads as one row twice.

**ph75 · ownership taken, then a commit that can be skipped** — `Zend/zend_variables.c:139-153` · CRASH-161, LOGIC-026, LOGIC-027, LOGIC-004 · `narrowed` · I9/O3 + I6/O3 · echoes p42
`zval_copy_ctor`'s array arm allocates `tmp_ht`, fills it with `zend_hash_copy` at `:151`, and only **then** writes `zvalue->value.ht = tmp_ht;` at `:152`. `zend_hash_copy` can `longjmp` (`zend_bailout`) or run a copy-ctor that re-enters — and on that path the caller's zval still names `original_ht`. LOGIC-004/027: `ALLOC_ZVAL` at `zend_compile.c:2942`, a switch with **no default arm** at `:2945-2957`, unchecked insert at `:2959`.
▸ trigger: an allocation failure or a re-entrant copy-ctor mid-copy.
▸ benign: ordinary deep copies; `u64` = fold of the copied payloads + `(allocs, frees)`.
▸ blob: a record stream with per-step failure bits.
⚠ risk: the failure injection is the row. Without a way to fail mid-copy from the blob, the kernel is correct and measures nothing.

**ph76 · engine-owned, non-allocator storage handed to the deallocator** — `ext/standard/array.c:2058-2061` · CRASH-012, CRASH-148, CRASH-026, CRASH-078 · `verbatim` · I14/O3 + I5/O4 · echoes p32
`EG(symbol_table)` is a `HashTable` **embedded in the executor-globals struct** — not an allocator return — and `$GLOBALS` is a zval whose `value.ht` is its address. `array_splice` destroys and `efree`s `Z_ARRVAL_P(array)` unconditionally at `:2059-2060`. Siblings: `zend_operators.c:661` adopts it as object properties; `array.c:3272-3274`'s `zval_copy_ctor` no-ops for it so the "copy" aliases it.
▸ trigger: `array_splice($GLOBALS, 0, 1);`
▸ benign: ordinary arrays splice; `u64` = fold of the surviving elements + `(allocs, frees)`.
▸ blob: an operation stream + a per-container "embedded?" bit.
⚠ risk: a struct with **one embedded container and one heap-allocated one**, and a function that frees "the container" without asking which kind it has. If the extraction heap-allocates both, there is no defect.

### E5 — the VM's own bookkeeping

**ph77 · resurrect-and-queue into a fixed two-slot array** — `Zend/zend_execute.c:63-78` · CRASH-151, CRASH-057, CRASH-050, LOGIC-011, LOGIC-022 · `narrowed` · I7/O2 + I7/O5 · echoes p34
✅ `zend_pzval_unlock_func` decrements and, at zero, does **not** free — it **resurrects** (`refcount = 1; is_ref = 0`) and pushes onto `EG(garbage)`, which `Zend/zend_globals.h:214-215` declares as `zval *garbage[2]` with `int garbage_ptr`; `:69 EG(garbage)[EG(garbage_ptr)++] = z;` is **unchecked**; `zend_clean_garbage` drains at `:73-78`. Defect sites: `Zend/zend_execute.c:374-381` (second unlock), `Zend/zend_execute.c:500-538` (the address of a **parameter** stored into the temp table at `:535`), and `Zend/zend_execute.c:196-218` + `Zend/zend_execute.c:3152-3170` (`zend_switch_free` re-run by brk/cont).
▸ trigger: three unlocks before a statement boundary.
▸ benign: ordinary lock/unlock/drain; `u64` = fold of `(refcount, garbage_ptr)` + `(allocs, frees)`.
▸ blob: a lock/unlock/drain opcode stream.
⚠⚠ risk: **two limbs, and both must be declared** (adjudication §2 item 5). The row is admitted for its **temporal** mechanism; the unchecked `garbage_ptr++` on a 2-element array is a **real spatial defect of the same C** and must be declared as a second limb with the oracle able to say which fired. ⚠ **Do not bound it** — that is `PLAN_PHP.md` §4.2's invented non-defect.

**ph78 · a raw pointer latched across a call that runs user code** — `Zend/zend_object_handlers.c:264-296` · CRASH-042, CRASH-159, CRASH-035, CRASH-064, CRASH-010, CRASH-132, CRASH-113 · `narrowed` · I17/O1 + I7/O4 · echoes p28
A caller latches a raw pointer to a heap object it holds **no reference to**, calls something that runs userland, and then uses the pointer. `zend_std_read_property` caches `zobj = Z_OBJ_P(object)` at `:274`, calls `__get` at `:293`, and then **writes** `zobj->in_get = 0` at `:294` into freed storage. Six siblings, largest family on the axis.
▸ trigger: a `__get` that reassigns the object it was called on.
▸ benign: ordinary property reads; `u64` = fold of the read values + `(allocs, frees)`.
▸ blob: a property-access stream; the callback is kernel-supplied.
⚠ risk: the **write** at `:294` is what makes CRASH-042 sharper than a read-only UAF. Keep it.

**ph79 · a cache that cannot tell borrowed from per-call** — `Zend/zend_execute_API.c:718-728` · CRASH-038, CRASH-069, CRASH-031, CRASH-072, LOGIC-025 · `narrowed` · I20/O1 + I20/O3 · echoes p27
`zend_call_function` caches the resolved handler **unconditionally** at `:718-723`. For `__call`/`__get` the resolved handler is a **trampoline `emalloc`'d by `get_method` for this one call** and `efree`'d when the call returns, so the next call takes the `:724-728` branch and reads a freed `zend_function` at `:733`. Siblings: `zend_execute.c:2767` (`efree(EX(fbc))` then `:2778` reads `EX(fbc)->common.fn_flags`), `streams.c:1395-1406`.
▸ trigger: two consecutive `__call`s through the same cache slot.
▸ benign: ordinary resolution and caching; `u64` = fold of the resolved ids + `(allocs, frees)`.
▸ blob: a call stream + a per-call "is trampoline" bit.
⚠ risk: **the whole defect is that the two kinds are the same C type.** An extraction that tags them has fixed it.

**ph80 · two subsystems disagree about the block's lifetime** — `ext/standard/basic_functions.c:1325-1385` · CRASH-084, CRASH-092, CRASH-114, CRASH-141 · `verbatim` · I5/O3 + I5/O2 · echoes p32
`putenv()` hands its `pe.putenv_string` to libc `putenv()`, which **does not copy** — `environ[]` now aliases PHP's `emalloc`'d buffer. The next `putenv()` for the same key does `zend_hash_del(&BG(putenv_ht), …)` at `:1376`, whose destructor `efree`s that buffer, while `environ` still points at it and `:1380-1382` scans it. GUARD: `:1333`, a guard that never fires.
▸ trigger: `putenv("A=1"); putenv("A=2"); getenv("A");`
▸ benign: ordinary env sets and gets; `u64` = fold of the read values + `(allocs, frees)`.
▸ blob: a set/get key-value stream.
⚠ risk: an owning hashtable with a destructor plus a **borrowing array of raw pointers**; `environ` is a second array. Nothing from libc is needed — and importing real `putenv` makes the row unmeasurable.

**ph81 · the slot is left as a presence flag for what it held** — `Zend/zend_execute.h:117-127` · CRASH-142, CRASH-140 · `verbatim` · I5/O2 + I5/O1 · echoes p32
`zend_ptr_stack_clear_multiple`'s loop at `:123-125` does `zval_ptr_dtor((zval **) --p)` on each slot and **never writes the slot** — it only moves `top`/`top_element`. Anything that walks the stack by **frame descriptor** rather than by `top` (a `debug_backtrace`, an error handler firing *during* teardown) reads released slots. CRASH-140: `zval *arg_array = NULL;` hoisted out of the per-frame loop at `zend_builtin_functions.c:1453`, so the previous frame's freed array is re-read and re-freed at `:1558-1559`.
▸ trigger: an error handler that calls `debug_backtrace()` during teardown.
▸ benign: ordinary teardown; `u64` = fold of the slot words + `(allocs, frees)`.
▸ blob: ⭐ `0x102 TRACE (walk by descriptor and fold)` — **a backtrace IS blob-encodable**, which is what refutes ph23's original kill.
⚠ risk: eleven lines; needs only a slot array and a release callback.

### E6 — allocation not released on every path that leaves the block

**ph82 · a loop temp acquired at use, released at the textual loop end** — `Zend/zend_execute.c:4235-4265` · LOGIC-002, LOGIC-023, LOGIC-009, LOGIC-019, LOGIC-024, LOGIC-010, LOGIC-012, LOGIC-016, LOGIC-021 · `modelled` · I6/O1 · echoes p42
The VM acquires a lock/addref at the **point of use** and relies on a release emitted at the **textually** matching point — `FE_RESET` locks the container and only the loop-end `SWITCH_FREE` (`zend_compile.c:1468-1480`) releases it. A throw jumps to `zend_handle_exception_handler`, which drains the argument stack at `:4242-4247` and **releases no loop temp**. Acquisitions at `:3713`, `:3737`, `:3741`.
▸ trigger: a `throw` inside a `foreach` body.
▸ benign: ordinary loops acquire and release in balance; `u64` = fold of `(allocs, frees)` per iteration.
▸ blob: an opcode stream with a throw bit.
⚠ risk: `modelled` — genuinely needs a loop construct with an unwind path. **Split from ph83/ph84/ph85** (adjudication §2 item 6): one `I6` invariant over four C shapes is a taxonomy, not a mechanism.

**ph83 · a lock taken unconditionally, ignoring that the result is unused** — `Zend/zend_execute.c:986-987`, `:448-452` · LOGIC-011, LOGIC-022 · `narrowed` · I6/O2 + I17/O1 · echoes p34
A bare `PZVAL_LOCK` that ignores `RETURN_VALUE_UNUSED` (`:986-987`), and a lock taken **despite a pending exception** (`:448-452`). The acquisition happens on a path whose matching release will never execute.
▸ trigger: an expression statement whose result is discarded / a lock after a throw.
▸ benign: ordinary locks pair with releases; `u64` = fold of `(refcount)` per slot.
▸ blob: an opcode stream with a "result used" bit.
⚠ risk: both rows also appear in ph77's member list as *sites*; here they are the **mechanism**. Say which reading a build takes.

**ph84 · a deep copy with no matching destructor** — `Zend/zend_execute.c:3142-3146` · LOGIC-015 · `narrowed` · I6/O1 · echoes p42
`zval tmp` is `copy_ctor`'d and **never `dtor`'d** on the exit path — the copy is made, the transfer never happens, and nothing releases it.
▸ trigger: any path reaching the exit without the transfer.
▸ benign: copies are matched by destructors; `u64` = `(allocs, frees)`.
▸ blob: an opcode stream.
⚠ risk: a pure leak — invisible to a checksum unless `(allocs, frees)` is in the `u64`. This row is the strongest argument for that convention.

**ph85 · the type tag overwritten over a live payload** — `Zend/zend_execute.c:914-926` · LOGIC-006 · `narrowed` · I6/O1 · echoes p35
`array_init` is called straight over a live `IS_STRING` payload with **no `zval_dtor`** — the tag is rewritten and the string's buffer becomes unreachable.
▸ trigger: an assignment that retypes a live string slot to an array.
▸ benign: retypes destroy the old payload first; `u64` = `(allocs, frees)` + the tag sequence.
▸ blob: a retype stream.
⚠ risk: sits between the leak family and ph39's tag family. Cross-reference both; catalogued here because the *harm* is the leak.

### E7 — the compiled program's metadata is wrong

**ph86 · compile-time liveness marking stamps the wrong opcode** — `Zend/zend_compile.c:885-899` · CRASH-065, CRASH-024 · `narrowed` · I18/O2 · echoes p19
`zend_do_free` decides **at compile time** which runtime temp is dead. When the result is not the operand it walks backwards through the emitted opcodes looking for `ZEND_JMP_NO_CTOR` (`:889-894`) and, on the **first one it finds**, stamps `EXT_TYPE_UNUSED` onto the *preceding* opcode's result and the *following* opcode's op1 (`:896-897`) — without checking that this `JMP_NO_CTOR` belongs to the expression being freed. CRASH-024: `zend_do_assign_ref` never sets `ZEND_RETURNS_FUNCTION`, consumed at `zend_execute.c:2241-2248`.
▸ trigger: a `new` expression nested inside another expression being freed.
▸ benign: ordinary temp liveness; `u64` = fold of the marked opcode indices.
▸ blob: an opcode buffer.
⚠ risk: ⚠ the one candidate whose natural kernel is **two passes** — a marking pass and a tiny interpreter. Budget for both.

**ph87 · release, then format the released buffer** — `Zend/zend_constants.c:310-326` · CRASH-068, CRASH-129 · `verbatim` · I5/O2 + I12/O1 · echoes p32
`zend_register_constant`'s duplicate arm releases the constant and then reports it: `name = c->name` at `:316` aliases the buffer on the `CONST_CS` path, `:320 free(c->name)` releases it, and `:324 zend_error(E_NOTICE, "Constant %s already defined", name)` formats the released pointer. Sibling (`I12`): `php_mbregex.c:732` — an unchecked `zend_eval_string`, then `convert_to_string(&v)` at `:734` and `Z_STRVAL(v)` at `:735` over a stack zval the failed eval never wrote.
▸ trigger: `define("X", 1); define("X", 2);`
▸ benign: ordinary constant registration; `u64` = the emitted message checksum + `(allocs, frees)`.
▸ blob: a define stream.
⚠ risk: ⚠ **the temporal miner retracted a claim of its own here, unprompted** — it first called `free(c->name)` an allocator mismatch, then killed that: every `c->name` comes from `zend_strndup`, so libc `free` is correct. Do not re-derive the retracted claim.

**ph88 · subsystem teardown ordering** — `Zend/zend_execute_API.c:282` · CRASH-062 · `narrowed` · I5/O3 · echoes p32
`zend_destroy_rsrc_list` runs before `Zend/zend.c:822`'s `shutdown_compiler`, so one subsystem is torn down while another still names its storage.
▸ trigger: a shutdown with a resource the compiler still references.
▸ benign: ordinary shutdown; `u64` = fold of the teardown order + `(allocs, frees)`.
▸ blob: a subsystem registration/teardown stream.
⚠ risk: **split from ph87** (adjudication §2 item 6) — the miner itself called this *"the weakest merge in this set"*; teardown-ordering shares only the error-handler framing.

### E8 — routed between axes and never picked up

**ph89 · a by-ref parameter separates the table a live alias names** — `Zend/zend_execute_API.c:733-745` with `Zend/zend.c:955-957` · CRASH-034 · `narrowed` · I2/O2 · echoes p28
`zend.c:955-957` publishes `EG(active_symbol_table)` into `$errcontext` (`z_context->value.ht = EG(active_symbol_table); z_context->type = IS_ARRAY;`). `zend_execute_API.c:733-745` then performs by-ref separation on a parameter — `ALLOC_ZVAL(new_zval); *new_zval = **fci->params[i]; zval_copy_ctor(new_zval); (*fci->params[i])->refcount--;` — and can release the table the live `$errcontext` alias names. CWE-822.
▸ trigger: an error handler taking `$errcontext` while a callee separates a by-ref parameter.
▸ benign: ordinary separation; `u64` = fold of `(refcount, is_ref)` + `(allocs, frees)`.
▸ blob: a parameter-passing stream.
⚠ risk: routed to temporal by the type miner and **picked up by nobody** (adjudication §3d). Note it cites the same lines as ph47's caller half — the *type-side* reading of `:730-753` is ph47; this is the *temporal* one. Two readings of one region; keep both, cross-referenced.

**ph90 · the destructor called on what the failing call left NULL** — `ext/standard/array.c:1045-1046` · CRASH-029 · `verbatim` · I12/O1 · echoes —
```c
1045  if (zend_call_function(&fci, &BG(array_walk_fci_cache) TSRMLS_CC) == SUCCESS) {
1046      zval_ptr_dtor(&retval_ptr);
```
The call returns `SUCCESS` even when the callback **threw**, and on that path `retval_ptr` was never written — so the guarded `zval_ptr_dtor` runs on an unwritten pointer.
▸ trigger: an `array_walk` callback that throws.
▸ benign: ordinary walks; `u64` = fold of the visited keys + `(allocs, frees)`.
▸ blob: a callback-outcome stream.
⚠ risk: routed to temporal by the type miner and **picked up by nobody**. Distinct from ph60 in that the guard **is** present and tests the wrong proposition ("the call completed" vs "the call produced a value").

**ph91 · CRASH-071 — ⚠ UNRESOLVED, the corpus label and its citation disagree**
`root_cause_id` = `exception-ctor-debug-backtrace-copies-args-of-torn-down-executor-frame-during-shutdown-uaf`; `c_file_line` = `Zend/zend.c:955`. ✅ Measured: `zend.c:955` is `z_context->value.ht = EG(active_symbol_table);`, inside the **error-callback's `$errcontext` publication** (declarations at `:871`, `ALLOC_INIT_ZVAL(z_context)` at `:938`, `params[4] = &z_context` at `:964`). Nothing at or near `:955` is a `debug_backtrace`, an exception constructor, or a shutdown path. The two fields describe **different defects** and I could not decide which is the row.
⚠ **Third suspect corpus label found by this task**, after CRASH-053 (wrong twice) and CRASH-009 (the citation names the guard, the defect is one line below). Settling it needs the reproducer run, which this task did not do.

---

## Part C — the kill list

**Every corpus row not catalogued, with the `PLAN_PHP.md` §3 criterion it fails
and one sentence of evidence.** ⚠ This part is as important as Part A: the
adjudication exists because the mining wave's kill list is where the defects
were, and this task found five more there.

### C.0 The rule this list is derived under

**Criterion 3 is about the KERNEL SHAPE** — flat blob in, `u64` out, the shared
driver loop. It is **not** about how much C must come along; that is the tier.
*"The surrounding machinery is the program"*, *"mutually recursive over a
4000-line file"*, *"needs its own library"*, *"the blob would have to encode a
backtrace"* are **tier assignments wearing a kill's clothes**, and none of them
is in the bar. Nothing about Rust, Verus, Miri or cost gradients may kill a row.
**Mechanism *quality* is not a criterion either** — only mechanism
*distinctness* is (`CLAUDE.md` rule 6).

### C.1 Kills — exact C-side duplication (criterion: `PLAN_PHP.md` §3.1)

| row | duplicate of | evidence |
|---|---|---|
| CRASH-106 nl2br `string.c:3593` | **ph19** | `base + count*const` in `int`, same wrap-down-then-unbounded-`*target++`; distinct only in needing a ~358 MB input, which is a *worse* kernel, not a different mechanism |
| CRASH-109 wordwrap `string.c:682` | **ph19/ph20** | `textlen * (breakcharlen + 1) + 1` in `int`; the second `alloced` growth path at `:692` muddies the extraction without changing the mechanism |
| CRASH-090 `html.c:155/:401` | **ph32** | literally the same defect on a different table; folded into ph32's `corpus rows` |
| V5C-116 | **ph03** | same loop, same bound, merged by the corpus itself |
| V5C-173 | **ph11** | same one-sided compare, merged by the corpus itself |
| V5C-015 | **ph22** | same two-pass sizing mismatch, merged by the corpus itself |
| CRASH-037, CRASH-101 | **ph39** | same missing-tag-guard read; carried inside ph39's `corpus rows` |
| CRASH-061, CRASH-126, CRASH-163 | **ph60** | same "fallible call's failure not tested"; carried inside ph60's `corpus rows` |
| LOGIC-003, LOGIC-008, LOGIC-014, LOGIC-018 | **ph47** | all family E — `is_ref` stamped on, or not separated from, a live shared slot; LOGIC-017 was **kept** as ph48 because it forces the flag rather than failing to clear it |

⚠ These are the only kills in this catalogue that rest on §3.1, and every one of
them is a **merge** — the row survives inside another row's `corpus rows`, which
is how the temporal miner applied the rule and is the right shape.

### C.2 Kills — criterion 2, the error cannot be exhibited

| row | criterion | evidence |
|---|---|---|
| **CRASH-021** strftime `datetime.c:1033` | **2** | `strftime(buf, buf_len, format, ta)` with `ta` from `php_localtime_r`; the fault is **inside glibc's `strftime`**, and I did **not** run it on this box's glibc. Modern glibc is very likely to be clean. ⚠ **This is a soft kill: it is criterion 2 pending a measurement I did not take**, not a shape or cost judgement. If someone runs it and it faults, it is admissible and the kernel is ten lines. |

### C.3 Kills — criterion 3, the kernel shape genuinely does not fit

**Exactly one row in 166.**

| row | criterion | evidence |
|---|---|---|
| **CRASH-017** rawurlencode `Zend/zend_alloc.c:129 + :148`, consumed at `:182` | **3** | The corpus itself has relocated a 4.0.2 defect onto the 5.0.0 **allocator**: pristine `url.c:499` is `safe_emalloc(3, len, 1)`, so the `3*len+1` int overflow is already fixed and what remains is `unsigned int real_size = REAL_SIZE(size)`. ⚠ **Its "kernel" would BE the allocator, not a computation over a blob** — and `PLAN_PHP.md` §4.3 already retires the truncation as *"a multiplier on every sizing defect in the engine, not a pattern of its own"* and says **do not re-propose it as a row**. It is catalogued instead as the **evidence for §4.3**, and **ph29** is the row where the truncation is load-bearing. |

⚠ **That is the ONLY criterion-3 kill.** After opening every remaining candidate
at source, **no other corpus row in this catalogue's scope fails the kernel
shape.** The rows the adjudication upheld on criterion 3 — CRASH-097, CRASH-098,
CRASH-147, CRASH-133 and CRASH-135 — are catalogued as **ph29, ph16, ph28, ph30,
ph31**; see C.4.

### C.4 ⚠⚠ Kills REVERSED BY THIS TASK — nine more, all the same defect

The adjudication found that the mining wave wrote **extraction cost** as a
criterion-3 failure and reversed 17 rows. **It then applied that lens to the
reversal list and not to its own upheld list.** Opening the upheld rows at source
reverses five more:

| row | the upheld reason | what the tarball says | now |
|---|---|---|---|
| **CRASH-135** | *"needs its own calendar library; a model would be a different program"* | ✅ `ext/calendar/julian.c` is **250 lines** and `SdnToJulian` is **46 self-contained lines** — it includes only `sdncal.h`, uses three `#define`s and does pure integer arithmetic. The sink is `sprintf(date, "%i/%i/%i", …)` into a `char[16]` at `calendar.c:263/:280`. **There is no library** | **ph31**, `verbatim` |
| **CRASH-133** | *"needs its own arbitrary-precision library"* | ✅ the defect completes in `_bc_new_num_ex` (`init.c:48-74`, 27 lines, `pemalloc(length+scale)` in `int`) and `_bc_do_add`'s zero-extension block (`doaddsub.c:63-68`, 6 lines) — **before a single digit is added** | **ph30**, `narrowed` |
| **CRASH-097** | *"the defective quantity comes from a socket; without a live socket the kernel computes nothing"* | ✅ **the defective quantity is `long to_read`, which comes from `zend_parse_parameters` at `:309` — from USERLAND, not from the socket.** The socket supplies only `recvd`, i.e. the bytes written, which a blob supplies just as well | **ph29**, `narrowed` |
| **CRASH-098** | *"needs `RLIMIT_NOFILE > ~1200` and real file descriptors"* | ✅ **measured** (`.temp/php11/fdset_probe.c`): `FD_SET` is a pure bit-set macro that never consults the fd table; index 4096 into a 128-byte stack `fd_set` writes at offset 512 with only fds 0,1,2 open. The `requires` field is a property of the **PHP reproducer** — exactly the ground on which the adjudication already reversed CRASH-056's *"requires writable /tmp"* | **ph16**, `verbatim` |
| **CRASH-147** | *"the adversarial input is irreducibly ~2 GiB, so it cannot be carried by the blob path at all — criterion 3"* | ⚠ the **blob** is two lengths and a fill byte (~9 bytes); the 2 GiB is an allocation the **kernel makes**, not an input it carries. That is a resource budget, not a kernel shape. ⚠ It is a real constraint (~2 GiB resident, doubled by the `erealloc`) and the row carries it as its risk | **ph28**, `verbatim` |

⚠⚠ **And three the coverage check found, killed by ONE sentence with ph45.**
The spatial reject table disposed of four mbstring rows together — *"the
mbstring rows all require libmbfl's filter-chain object model or a bundled
oniguruma"*. The adjudication reversed **CRASH-123** out of that sentence and
made it the audit's headline exhibit (five lines, its own invariant) — and
**nobody asked whether the other three fall the same way.** They do; only my own
`coverage.py` diff against `index.csv` surfaced them, because a row killed
inside a sentence about a *different* row leaves no reject-table entry of its
own.

| row | the killing sentence | what the tarball says | now |
|---|---|---|---|
| **CRASH-124** | *"requires libmbfl's filter-chain object model"* | ✅ `mbfilter.c:1200-1210` is a bare `for(;;)` advancing `p` by `mbtab[*p]` whose only exit is `n > from`; `string->len` is never consulted. `mbfl_string` reduces to `{val, len}` and `mblen_table` is a static array. **A pure `DP-07` pointer cursor** | **ph07**, `narrowed` |
| **CRASH-127** | *"requires a bundled oniguruma"* | ✅ `regparse.c:3581 BITSET_SET_BIT(cc->bs, (int)(*vs));` on the single-byte arm, with `*vs` an `OnigCodePoint` an octal escape pushes over 0xFF. Needs the bitset macro and one switch — **the matcher is downstream of the parse** | **ph17**, `narrowed` |
| **CRASH-128** | *"requires a bundled oniguruma"* | ✅ `php_mbregex.c:624 char pat_buf[2];` filled at `:663-667` from an integer argument with `arg_pattern_len = 1`; a UTF-8 lead byte declares a longer one. Upstream's own `FIXME: this code is not multibyte aware!` sits at `:661` | **ph33**, `verbatim` |

⚠ **The reusable lesson, and it is new:** a kill written as a *set* — "the
mbstring rows", "the ordinary null-deref set" — hides its members from
row-level review, because there is no per-row entry to attack. **Both of this
catalogue's largest recoveries came from set-shaped kills**, and the only thing
that found them was diffing the catalogue against the corpus id list rather than
reading the reject tables.

⚠ And a sixth class, on a different criterion:

| row | the upheld reason | why it does not hold | now |
|---|---|---|---|
| **CRASH-082, CRASH-088, CRASH-061, CRASH-126, CRASH-163, CRASH-021** | *"the 'ordinary null-deref' set — mechanism-quality judgement on the C, which the bar permits"* | ⚠ **the bar does not permit mechanism quality.** `PLAN_PHP.md` §3 has four criteria and `CLAUDE.md` rule 6 names three C-side tests, of which the only comparative one is **distinctness**. Six rows were removed by a fifth, unwritten criterion. CRASH-082 is not even in the family — `!f(x) == SUCCESS` is a **precedence** defect in a guard that runs | **ph59** + **ph60** (one family row, three merges under C.1) + CRASH-021 under C.2 |

### C.5 Kills the adjudication reversed, and this task upholds the reversal

✅ Re-derived at source, independently, all twelve of `ADJUDICATION_001.md` §7
plus the two it left open. Every one of them refutes the machinery claim that
killed it, and all fourteen are catalogued: CRASH-123 (**ph45**), CRASH-136
(**ph13**), CRASH-134 (**ph14**), CRASH-157 (**ph23**), CRASH-130 (**ph35**),
CRASH-107 (**ph21**), CRASH-014 (**ph22**), CRASH-120 (**ph02**), CRASH-018/019
(**ph37**), CRASH-055 (**ph58**), CRASH-056 (**ph46**), LOGIC-017 (**ph48**),
CRASH-028 (**ph57**), CRASH-033 (**ph09**), CRASH-053 (**ph46**). Plus the two
the adjudication did not open: CRASH-005 (**ph36**) and CRASH-009 (**ph27**),
and the row dropped with no reason at all, CRASH-008 (**ph24**).

### C.6 Rows that fell between axes — all four now placed

`ADJUDICATION_001.md` §3d listed four rows routed away by one miner and never
picked up. All four are catalogued: CRASH-096 → **ph15**, CRASH-077 → **ph38**,
CRASH-034 → **ph89**, CRASH-029 → **ph90**. CRASH-071 → **ph91**, unresolved.

⚠ **The structural lesson stands and is worth keeping:** three parallel miners
with an axis each will drop whatever sits on a boundary, and each will have
behaved correctly. Only a reconciliation pass finds them.

### C.7 What is NOT killed and NOT catalogued

Nothing. ✅ **Measured with `python3 .temp/php11/coverage.py`, which parses
Part A's `corpus rows` column out of this file and diffs it against
`index.csv`:**

```
corpus rows in index.csv : 166
Part A distinct corpus ids : 161
Part C kill-table ids      : 30

accounted for              : 166 / 166
MISSING (in corpus, not in catalogue) : 0
ids the catalogue names that the corpus does not have : 3  ['V5C-015', 'V5C-116', 'V5C-173']

ids claimed by MORE THAN ONE catalogue row : 3
   CRASH-153   ['ph49', 'ph50']
   LOGIC-011   ['ph77', 'ph83']
   LOGIC-022   ['ph77', 'ph83']

catalogue rows in Part A : 91  (ids ph01..ph91, gaps: none)
Part B blocks            : 91  (in Part A but not Part B: none)
```

**91 catalogued rows carry 161 of the 166 corpus ids.** The remaining five are
`CRASH-017` (the one criterion-3 kill, C.3), `CRASH-021` (the one soft
criterion-2 kill, C.2), and `CRASH-037` / `CRASH-101` / `CRASH-126` — which,
together with `CRASH-061`, `CRASH-090`, `CRASH-106`, `CRASH-109`, `CRASH-163`
and the four LOGIC family-E rows, are the C.1 exact-duplication **merges**: each
survives inside a catalogued row's `corpus rows` and is named in Part C so the
merge is auditable.

⚠ **Three corpus ids are deliberately claimed by two rows each, and that is not
double-counting:**

| id | rows | why |
|---|---|---|
| CRASH-153 | **ph49**, **ph50** | the adjudication ordered ty#5/#11 split; the corpus merges two independently-extractable links into one row |
| LOGIC-011, LOGIC-022 | **ph77**, **ph83** | they are *sites* of ph77's protocol and the *mechanism* of ph83. A build must say which reading it takes |

⚠ `V5C-015`, `V5C-116` and `V5C-173` appear in Part A but are **not** `input_id`s
— they are the corpus's own `merged_members` field, carried across so the merge
is visible. `coverage.py` reports them as "ids the catalogue names that the
corpus does not have"; that is correct and expected.

---

## §9 What this catalogue does NOT establish

1. **No row here has been built, and nothing here is a build order.** Every
   tier is an estimate read off the source, not a measurement.
2. **`crashes_pristine_5_0_0` is carried from the corpus and was re-verified for
   no row.** ⚠ It must not be used as an admission filter — `PLAN_PHP.md` §4.3
   measures 63.5 % of PHP's heap traffic never reaching `malloc`, so a C kernel
   on plain `malloc`/`free` will reproduce **more** of these than pristine PHP.
3. **`hotness` is absent from this catalogue on purpose.** The ASan census
   cannot speak to the spatial axis at all: ✅ **zero of its 2520 spatial
   reports fault in `Zend/` or `ext/standard/`** — 2156 fault inside
   `libmysqlclient.so.14`'s XML charset parser and 364 in the regex matcher
   (`ADJUDICATION_001.md` §8b, re-derived from `.temp/san_tests/asan-logs`).
   Frequency evidence for spatial rows does not exist yet.
4. **`echoes` is a reading, not a measurement.** No `pNN` was re-opened to
   confirm the mechanism match; treat every one as a hypothesis to check when
   the row is built.
5. **`inv/obl` is the corpus's blind labelling, carried across unmodified.** It
   was produced by analysts forbidden to read the Rust port, which is why it is
   worth carrying — but this task did not re-derive a single label.
