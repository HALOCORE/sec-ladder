# TASK_PHP_011_REPORT — `patterns-php/CATALOGUE.md`, and the review of `ADJUDICATION_001.md`

**Role:** research engineer, one agent alone. **Status: delivered, NOT REVIEWED.**
**Deliverables:** `patterns-php/CATALOGUE.md` (91 rows) and this file.
**Scratch:** `.temp/php11/` — five generators, all re-runnable, all named below.

> ⚠ `PROTOCOL.md` rule 9: nothing here reaches `.memory-php/` until a review
> lands. ✅ marks something I **ran**; everything else is a reading.
> ⚠ I edited nothing under `harness/`, `common/`, `patterns/`, `results/`,
> `pilot/`, and did not touch `RECAP_PHP.md`. No `git add` / `git commit`.

---

## §0 The bracket, first and last

**Open** (before any work):

```
$ python3 harness/measure.py --check-stale
...
FRESH       results/p49-interned-pool.json             18 source(s) + 9 input(s)

66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
preflight
  ok   shim /home/apt/repos_common/sec-ladder/.temp/php-root
  ok   common-php/ digest bridge
  ok   every patterns-php/*/c/ file has a digest key (RECAP_PHP.md open item 17)
  ok   <row>/c/emalloc_shim.h symlink, UNCONDITIONAL (PROTOCOL_PHP.md §B2, TASK_PHP_008 §0)
  ok   provenance.py overlap self-test (9 cases)
  ok   patterns-php/MANIFEST.sha256
  ok   every php record has a CERTIFYING preflight record beside it
...
2 record(s) examined, 0 STALE
```

**Close** (after everything below):

```
$ python3 harness/measure.py --check-stale
FRESH       results/p49-interned-pool.json             18 source(s) + 9 input(s)
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
FRESH       results/gate/ph00-smoke.json               29 source(s)
FRESH       results/ph00-smoke.json                    19 source(s) + 8 input(s)
2 record(s) examined, 0 STALE
```

⚠ **One untracked file appeared and it is mine:**
`results-php/preflight/ph00-smoke.preflight.json`, written by the gate itself
when I ran `gate.py --preflight ph00-smoke` for the M2 control (§7.2). It is a
real certifying preflight record, not scratch; I left it for the manager to
decide.

⚠⚠ **AND FIVE FILES UNDER `.web/` WERE MODIFIED DURING THIS TASK AND THEY ARE
NOT MINE.** My launch snapshot said the tree was clean; at close:

```
$ git status --porcelain
 M .web/check.mjs
 M .web/content.js
 M .web/index.css
 M .web/index.js
 M .web/tools/responsive_audit.mjs
?? .tasks-php/TASK_PHP_011_REPORT.md
?? patterns-php/CATALOGUE.md
?? results-php/preflight/ph00-smoke.preflight.json

$ git diff --stat .web/
 5 files changed, 396 insertions(+), 3 deletions(-)
```

mtimes **14:25:18 – 14:28:45**, i.e. inside this task's window. **I never opened
`.web/`.** There is a concurrent writer — another agent or the user
(`DP-09` permits parallel read-only work, and this is not read-only). ⚠ **It did
not touch anything I read or wrote, so my results are unaffected** — but the
manager must not `git add -A` this tree, and should find out whose those are
before committing. `PROTOCOL.md` rule 11 in its widened form.

---

## §1 ⚠⚠⚠ THE HEADLINE — §5.1 attacked, and the answer is the OPPOSITE of the one feared

`TASK_PHP_011` §5.1 and §6 both say: *"If `criterion 3` vs `tier` is not as crisp
as the adjudication makes it, ~17 reversals are wrong and the catalogue is
inflated by a fifth. Attack this first, with source, not argument."*

✅ **I attacked it with source. The distinction holds, and the audit was
INCOMPLETE rather than wrong — in the direction opposite to the one feared.**

**The distinction is crisp, and here is the test that makes it so.** Criterion 3
asks *"can the harmful step be expressed as a pure computation over a flat blob,
producing a `u64`?"* — a question about the **defect**. Cost asks *"how much C
must come along?"* — a question about the **extraction**. The two come apart on
a measurable fact: open the defect site and count the lines the harmful step
actually needs. I did that for every §7 row and for every row the adjudication
**upheld**, and the answers were never ambiguous.

⚠⚠ **But the adjudication applied its own lens to ONE side of the ledger.**
`ADJUDICATION_001.md` §1 audits the miners' *kills* and reverses 17. It then
writes §3b — *"Kills UPHELD"* — **restating the miners' reasons without opening
the files.** Two of the five upheld classes are the exact defect §1 names, and
one more is a resource statement mislabelled criterion 3.

| upheld kill | the stated reason | ✅ what the tarball says |
|---|---|---|
| **CRASH-135** | *"the defect lives inside a … calendar library the corpus does not otherwise touch; a model would be a different program"* | `ext/calendar/julian.c` is **250 lines total** and `SdnToJulian` is **46 self-contained lines** (`:154-199`) — `#include "sdncal.h"`, three `#define`s, pure integer arithmetic, **zero library dependencies**. The sink is `sprintf(date, "%i/%i/%i", …)` into a `char date[16]` (`calendar.c:263`, `:280`). *There is no library.* |
| **CRASH-133** | *"…inside a bignum library…"* | the defect completes in `_bc_new_num_ex` (`libbcmath/src/init.c:48-74`, 27 lines, `pemalloc(length+scale)` computed in `int`) and `_bc_do_add`'s zero-extension block (`doaddsub.c:63-68`, 6 lines) — **before a single digit is added.** `bcscale` clamps only from below (`bcmath.c:542`). |
| **CRASH-097** | *"the defective quantity comes from a **socket**; there is no benign pure computation"* | ⚠ **the defective quantity is `long to_read`, and `streamsfuncs.c:309` reads it from `zend_parse_parameters(…, "rl\|lz", …)` — it comes from USERLAND.** The socket supplies only `recvd`, i.e. the bytes written, which a blob supplies just as well. The kill priced the wrong operand. |
| **CRASH-098** | *"needs `RLIMIT_NOFILE > ~1200` and real file descriptors"* | ✅ **measured, not argued** — see §4.1. `FD_SET` is a pure bit-set macro that never touches the fd table. |
| **CRASH-147** | *"the adversarial input is **irreducibly ~2 GiB**, so it cannot be carried by the blob path at all. That is criterion 3, C-side"* | ⚠ the **blob** is two lengths and a fill byte (~9 bytes); the kernel materialises the strings. The 2 GiB is an allocation the kernel *makes*, not an input it *carries*. That is a **resource budget**, which is real (~2 GiB resident, doubled by the `erealloc` at `zend_operators.c:1174`) and is **not** a kernel shape. |

⚠ **And a sixth, on a criterion that is not in the bar at all.** §3b disposes of
CRASH-061/082/088/126/163/021 as *"the 'ordinary null-deref' set — mechanism-quality
judgement on the C, **which the bar permits**"*. **It does not.** `PLAN_PHP.md`
§3 has four criteria and `CLAUDE.md` rule 6 names three C-side tests, of which
the only comparative one is **distinctness**. Mechanism *quality* is a fifth,
unwritten criterion. And one of the six is not even in the family: CRASH-082 is

```c
ext/standard/array.c:4085   if (!zend_call_function(&fci, &fci_cache TSRMLS_CC) == SUCCESS && result) {
```

— `!f(x) == SUCCESS` parses as `(!f(x)) == SUCCESS`, so with `SUCCESS == 0` a
**failed** call gives `!(-1) == 0` → true, `result` is NULL, `&& result` is
false, and the error branch is skipped *too*. **A guard whose parse differs from
its reading** is not "an ordinary null-deref".

⚠⚠ **And then my own coverage check found three more that nobody had a reject
entry for at all** — §5.2. Total: the catalogue is **larger** than `≈80`, not
inflated.

> **The reusable finding, and I believe it is new:** the adjudication's §1 lens
> is right and it was pointed at the kills only. **A kill list and an
> upheld-kill list are the same artefact and need the same audit.** The manager
> asked to be refuted on whether the lens was too sharp; the measurement says it
> was not sharp *enough*, because it was never turned around.

---

## §2 Citations verified against the pristine tarball

`TASK_PHP_011` §2.1: *"Verify every citation you catalogue against the pristine
tarball … This is the bulk of the task. Report the count checked and every
discrepancy."*

### 2.1 The reader

`.temp/php11/pristine.py` extracts the pinned tarball once into
`.temp/php11/_cache/` (a **derived artefact**, deleted at the end of this task,
rebuilt by the script) and **sha256-checks every file against
`patterns-php/php-5.0.0.manifest` before serving a single line**. It refuses a
`.c`/`.h` that is not in the manifest and refuses the tarball if its sha256 is
not `5783e0c0…d6919`. ✅ Confirmed on the file `SOURCES.md` §3 pins:

```
$ python3 .temp/php11/pristine.py --sha Zend/zend_alloc.c
fb4215f19dc2e68c66b0c675b8dc965c05fd6e2e6658af98d612518046719743  Zend/zend_alloc.c  (manifest: fb4215f19dc2e68c66b0c675b8dc965c05fd6e2e6658af98d612518046719743)
```

### 2.2 ✅ The catalogue's own citations — 222 / 222

```
$ python3 .temp/php11/verify_catalogue.py
=== CATALOGUE.md citations vs the pristine tarball ===
distinct source files cited : 52
file:line tokens checked    : 222
resolve (file exists, manifest-matched, line in range) : 222
FAIL                        : 0
```

⚠ **This check found two defects in my own catalogue and I fixed them before it
went green.** Both were `GUARD:`/`FAULT:` notes where a bare `:NNN` silently
inherited the wrong file from earlier in the same sentence — `ph09`'s
`FAULT: :2621` read as `zend_object_handlers.c:2621` (985 lines) when it meant
`zend_compile.c:2621`, and `ph77`'s four defect sites read as `zend_globals.h`
when they meant `zend_execute.c`. ⭐ **That is exactly `PLAN_PHP.md` §6's
recorded failure — an out-of-range span used to PASS because `sed` prints
nothing past EOF — caught by a check written to fail.**

### 2.3 ✅ The miners' quoted C — 51 / 53 exact, 2 correct-line paraphrases, 0 wrong lines

`.temp/php11/verify_cites.py` extracts every `<file>:<line> (\`verbatim C\`)`
triple from the three `candidates.json` and asks the tarball whether that C is
in a ±6-line band:

```
$ python3 .temp/php11/verify_cites.py
=== citation check vs pristine tarball (window +/-6 lines) ===
triples checked : 53
resolved OK     : 49
MISMATCH        : 4
```

All four were resolved by hand and **none is a wrong line**:

| triple | verdict |
|---|---|
| sp#10 `html.c:896` | ⚠ **paraphrase.** Source is `for (k = entity_map[j].basechar; k <= entity_map[j].endchar; k++)`; the miner dropped the `entity_map[j].` qualifier. Line correct. |
| sp#16 `string.c:4777` | ⚠ **elision.** The declaration block is `:4776-4780` and the miner's quote omits `zend_bool cs=0;` at `:4779`. Lines correct. |
| te#1 `zend_ptr_stack.h:64` | **my extractor's false positive** — it matched `64 (\`h = h*0x100000001b3 ^ payload\`)` out of a `u64` fold description, which is not a citation. |
| te#10 `zend_llist.c:2135` | **my extractor's false positive** — the miner wrote `ext/standard/basic_functions.c:2100-2137 (… at :2135 …)` and my regex attached the bare `:2135` to the candidate's default `c_file`. ✅ `basic_functions.c:2135` is `tick_fe->calling = 0;`, exact. |

✅ **So the miners' citation quality is very high: 53 quoted constructs, 51 exact,
2 correct-line paraphrases, zero wrong lines.** That reproduces the wave's own
headline (*"every CSV `c_file_line` I checked resolved exactly"*) from a
different direction.

### 2.4 ⚠⚠ THREE citation defects **in `ADJUDICATION_001.md` itself**

The adjudication is unreviewed manager work and this is its review, so these are
in scope. All three are in §0/§1b/§7 — the sections that carry the audit's
evidence.

| adjudication says | ✅ pristine tarball | where |
|---|---|---|
| CRASH-107: `string.c:4119 int result_len;` · `:4143 result_len = …` · `:4144 if (result_len < 1 \|\| …)` | **`:4120`** · **`:4144`** · **`:4145`** — off by one on **all three** | §0 row 7, §7 row 6 |
| CRASH-123: `mbfilter_htmlent.c:177 char *buffer = (char*)filter->cache;` | **`:178`** | §0 row 9, §1b |
| CRASH-123: `mbfilter_htmlent.c:181 buffer[0] = '&';` | **`:183`** | §0 row 9, §1b |

⚠ **The CRASH-123 pair matters more than its size**, because §1b's five-line
quote block is *the adjudication's headline exhibit* — the thing it calls *"the
single most valuable thing the mining wave produced"* — and two of its five
lines are mis-numbered. ✅ **The corpus CSV is right in both cases** (it says
`wild write observed at …mbfilter_htmlent.c:183`), and ✅ **the spatial miner was
right about CRASH-107** (its `NOTES.md` says `:4120` and `:4145`). **The
adjudication is the only artefact of the three that is wrong.** That is
`RECAP_PHP.md` F2 one level up: the CSV is authoritative, and so is the miner
who read it; the summary written from them is not.

`patterns-php/CATALOGUE.md` carries the corrected lines and says so in the
`⚠ risk` field of `ph21` and `ph45`, so a future engineer copying from the
adjudication is warned at the point of use.

---

## §3 The three the adjudication could not settle — all three settled

### 3.1 CRASH-033 — ✅ SETTLED, and the adjudication's §7a mechanism is CONFIRMED

`Zend/zend_compile.c:2611-2622`, read verbatim:

```
  2611  ZEND_API void zend_unmangle_property_name(char *mangled_property, char **class_name, char **prop_name)
  2613      *prop_name = *class_name = NULL;
  2615      if (mangled_property[0]!=0) {
  2616          *prop_name = mangled_property;
  2617          return;
  2620      *class_name = mangled_property+1;
  2621      *prop_name = (*class_name)+strlen(*class_name)+1;
```

✅ The mechanism holds and the row is admissible: PHP mangles a private property
as `"\0Class\0prop"`, so a **leading NUL is the in-band marker for "mangled"**;
for an *empty* name that byte is the string's own terminator, `:2615`
misclassifies, `:2620` forms a pointer one past a 1-byte hash key and `:2621`
`strlen()`s from there. ✅ Every caller passes a **hash key** —
`zend_object_handlers.c:251`, `zend_compile.c:1893/1910`, `zend_execute.c:3801`,
`ext/standard/var.c:78/352` — so `$obj->{""} = 1` plus any property-table walk
reaches it. `verbatim`, 12 lines, no class-entry machinery. → **ph09.**

⚠ **One correction to §7a's framing.** It says *"CRASH-033 shows the corpus's
`missing-guard` field can name a third frame that is none of them."* ✅ The
corpus's `c_file_line` reads, in full:

```
Zend/zend_object_handlers.c:199-201 (missing guard site; OOB read manifests at Zend/zend_compile.c:2621)
```

**It names both frames in one field, and `:2621` is the defect.** The corpus is
not wrong here; the adjudication read only the first half of its own citation.
The conclusion (*price the cost at the defect site*) stands; the supporting
claim about the corpus does not.

### 3.2 CRASH-053 — ✅ SETTLED, and ⚠ §7b's MECHANISM IS WRONG IN ONE CELL

✅ §7b is right that the corpus's `root_cause_id` — *"unchecked
`make_real_object`"* — is **wrong twice**: `zend_execute.c:1635` **does** test
`object->type != IS_OBJECT`, and `make_real_object` (`:280-292`) is a correct
12-line function guarding all three of its arms. Verified verbatim.

⚠ **But §7b's table says CRASH-053 *"reads the `var` arm with **no test at
all*** → wild `zval **`". That is not what the source says.** The defect site is
`_get_zval_ptr_ptr`, `Zend/zend_execute.c:138-151`:

```c
138  static inline zval **_get_zval_ptr_ptr(znode *node, temp_variable *Ts TSRMLS_DC)
140      if (node->op_type==IS_VAR) {
141          if (T(node->u.var).var.ptr_ptr) {          /* <-- the test IS here */
142              PZVAL_UNLOCK(*T(node->u.var).var.ptr_ptr);
143          } else {
144              /* string offset */
145              PZVAL_UNLOCK(T(node->u.var).str_offset.str);
146          }
147          return T(node->u.var).var.ptr_ptr;          /* <-- returns the NULL it just detected */
```

**The test is present at `:141`, it is the SAME sibling-NULL discriminant
CRASH-056 uses, and it is used correctly for the unlock. The bug is that the
`return` at `:147` ignores it** and hands back the NULL. So the result is a
**NULL-pointer dereference**, not a wild `zval **` — which is exactly what the
corpus records (`cwe = CWE-476 null-deref`, `SEGV at Zend/zend_execute.c:283`,
the first line of `make_real_object`).

⚠⚠ **This makes the CRASH-053 + CRASH-056 pairing STRONGER, not weaker, and
re-describes it.** Both call sites discriminate a **tagless union**
(`zend_execute.h:30-43`) on a **sibling member's** NULL-ness. `zend_switch_free`
(`:198-217`) reads that discriminant out of a temp slot the compiler never
initialised; `_get_zval_ptr_ptr` branches on it correctly and then returns it
anyway. *One union, no tag, two ways to get it wrong.* → **ph46**, paired, both
type axis, `narrowed`. `PROTOCOL.md` rule 12: the mechanism is the part a reader
disbelieves, so it had to be right.

### 3.3 CRASH-096 — ✅ SETTLED, and the answer is a THIRD one

The adjudication asked: *"does the harmful step survive as a pure computation
over a blob, or does it die on criterion 3 like CRASH-097/098?"*, reasoning that
`php_stream_get_record` puts it *"inside the stream layer"*.

✅ **Neither. The harmful step is not in the stream layer at all** — it is in a
24-line `static inline` in a Zend header, and it is blob-pure. Chain, read at
source:

1. `streamsfuncs.c:1047 if (max_length < 0)` — **zero passes** (the guard site).
2. `:1054 php_stream_get_record(stream, 0, …)`.
3. `streams.c:836 php_stream_fill_read_buffer(stream, 0)` — with `size == 0` the
   no-filter arm's `if (stream->writepos - stream->readpos < (off_t)size)` is
   `0 < 0`, **false**, so nothing is allocated: `readbuf` stays NULL,
   `readbuflen` 0 (`streams.c:510-537`).
4. `streams.c:844 php_memnstr(stream->readbuf /*NULL*/, delim, 2, stream->readbuf + 0 /*NULL*/)`.
5. `Zend/zend_operators.h:128-151`, the **defect**:

```c
131      char *p = haystack;                 /* NULL */
134      end -= needle_len;                  /* NULL - 2 : UNDERFLOWS */
136      while (p <= end) {                  /* 0 <= (uintptr)-2 : TRUE */
137          if ((p = (char *)memchr(p, *needle, (end-p+1))) && …   /* memchr(NULL, c, SIZE_MAX) */
```

**`zend_memnstr` computes `end -= needle_len` with no precondition that the
haystack is at least `needle_len` long and no NULL/empty check.** Blob = haystack
bytes + a length field + needle bytes; `u64` = the found offset. `verbatim`,
~24 lines. → **ph15.**

⚠ **This is the §6-addendum three-frame pattern in its purest form**: guard site
`streamsfuncs.c:1047`, faulting site `streams.c:844`, **defect site
`zend_operators.h:134`** — three files, and the corpus names the first two.

---

## §4 Measurements I ran that changed a verdict

### 4.1 ✅ CRASH-098 needs no file descriptors — and ASan cannot see it

`.temp/php11/fdset_probe.c` + `asan_control2.c`, both kept.

```
$ gcc -O0 -g -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fsanitize=address -static-libasan -o fdset_probeO0 fdset_probe.c
$ env -u LD_PRELOAD ./fdset_probeO0
FD_SETSIZE = 1024, sizeof(fd_set) = 128 bytes
open fds in this process: 0,1,2 only (no sockets, no RLIMIT change)
CONTROL (in-range indices)  acc=15765698056653848672
TRIGGER (index 4096)        acc=0
```

**`FD_SET` is a pure bit-set macro over the `fd_set` object; it never consults
the process fd table.** Index 4096 into a 128-byte stack `fd_set` writes at byte
offset **512** — 384 bytes past the object — with only fds 0,1,2 open and no
`RLIMIT_NOFILE` change. **The kill reason is a property of the PHP reproducer,
not of the C defect** — exactly the ground on which the adjudication already
reversed CRASH-056's *"requires writable /tmp"*.

⚠⚠ **And a second, separate finding a builder needs.** ASan is **silent** on
this write, and I proved the instrumentation is live rather than assuming it:

```
$ env -u LD_PRELOAD ./asan_control2 x     # bits[17] -> 8 bytes past the object
==...==ERROR: AddressSanitizer: stack-buffer-overflow on address 0x7ffa643000c8
    #0 ... in main .../asan_control2.c:8

$ env -u LD_PRELOAD ./asan_control2       # bits[64] -> 384 bytes past the object
writing bits[64] of a 128-byte fd_set (offset 512 bytes)
NO REPORT
```

**Fires at 8 bytes past, silent at 384 — the write jumps clean over the redzone
into unpoisoned stack.** ✅ Glibc `_FORTIFY_SOURCE` *does* catch it
(`*** bit out of range 0 - FD_SETSIZE on fd_set ***: terminated`), which is a
ready-made `kernel_hardened.c`. **A row built on CRASH-098 needs a
canary/checksum oracle, not a sanitizer** — this is `PLAN_PHP.md` §4.5's
*"reproducing a different signal is a finding to state"* and the type miner's
*"a detector that is not running looks exactly like a detector that found
nothing"*, on a new row.

### 4.2 ✅ CRASH-135 and CRASH-133 are small, measured by line count

```
$ python3 .temp/php11/pristine.py --nlines ext/calendar/julian.c ext/calendar/calendar.c \
      ext/bcmath/bcmath.c ext/bcmath/libbcmath/src/doaddsub.c
     250  ext/calendar/julian.c
     640  ext/calendar/calendar.c
     559  ext/bcmath/bcmath.c
     233  ext/bcmath/libbcmath/src/doaddsub.c
```

`SdnToJulian` occupies `julian.c:154-199` — **46 of those 250 lines** — and its
only `#include` is `sdncal.h`. `_bc_new_num_ex` is `init.c:48-74` (27 lines) and
`_bc_do_add`'s zero-extension block is `doaddsub.c:63-68` (6 lines). Neither
"library" is needed.

---

## §5 What the catalogue is, and the check that keeps it honest

### 5.1 Shape

**91 rows** — 38 spatial, 22 type/initialisation, 31 temporal — against the
manager's `≈80` estimate. The +11 is: **+5** from §1's reversal of upheld kills,
**+3** from §5.2's set-shaped kills, **+1** CRASH-082 out of the null-deref set,
**+1** the null-deref family row itself, **+1** CRASH-096 admitted rather than
left conditional.

### 5.2 ⚠⚠ THE FINDING I DID NOT EXPECT: a kill written as a SET hides its members

I wrote `.temp/php11/coverage.py` as a bookkeeping check — parse Part A's
`corpus rows` column out of the catalogue and diff it against `index.csv`. On
its first run it reported **five** corpus ids in no row and no kill list, and
three of them were real:

```
MISSING (in corpus, not in catalogue) : 5
   CRASH-017    <- a legitimate criterion-3 kill I had not written up
   CRASH-021    <- parser artefact (bold cell), fixed in the checker
   CRASH-124
   CRASH-127
   CRASH-128
```

✅ **CRASH-124/127/128 were killed by ONE sentence, jointly with CRASH-123:**

> *"CRASH-123, CRASH-124, CRASH-127, CRASH-128 — the mbstring rows all require
> libmbfl's filter-chain object model or a bundled oniguruma."*

**The adjudication reversed CRASH-123 out of that sentence and made it the
audit's headline exhibit — and nobody asked whether the other three fall the
same way.** They do, read at source:

| row | defect site | what it actually needs |
|---|---|---|
| **CRASH-124** | `libmbfl/mbfl/mbfilter.c:1200-1210` — `for(;;) { m = mbtab[*p]; n += m; p += m; if (n > from) break; start = n; }` | `mbfl_string` reduces to `{val, len}`; `mblen_table` is a static 256-entry array. `string->len` is **never consulted in the loop**. GUARD: `mbstring.c:1800-1805` clamps a negative `len` and never clamps `from`. **A pure `DP-07` pointer cursor.** → **ph07** |
| **CRASH-127** | `oniguruma/regparse.c:3581` — `BITSET_SET_BIT(cc->bs, (int )(*vs));` on the `CCV_SB` arm, `*vs` an `OnigCodePoint` an octal escape pushes over 0xFF | the bitset macro and one `switch`. **The matcher is downstream of the parse.** → **ph17** |
| **CRASH-128** | `php_mbregex.c:624 char pat_buf[2];` filled at `:663-667` from an integer argument with `arg_pattern_len = 1` | a 2-byte buffer, a UTF-8 lead byte, a length table. Upstream's own `FIXME: this code is not multibyte aware!` is at `:661`. → **ph33** |

> ⚠⚠ **The reusable lesson, and I think it is new to this project: a kill
> written as a SET — *"the mbstring rows"*, *"the ordinary null-deref set"* —
> hides its members from row-level review, because there is no per-row entry to
> attack.** Both of this catalogue's largest recoveries came from set-shaped
> kills, and neither was findable by reading the reject tables: the only thing
> that found them was **diffing the catalogue against the corpus id list**. That
> is a cheap, mechanical check and it belongs in every mining wave's definition
> of done.

### 5.3 ✅ Final coverage — all 166 accounted for

```
$ python3 .temp/php11/coverage.py
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

The three `V5C-*` are the corpus's own `merged_members` field, carried across so
merges stay visible; the three double-claims are the deliberate splits the
adjudication ordered (ty#5/#11 both from CRASH-153) and the site/mechanism
double-reading of LOGIC-011/022. Both are documented in the catalogue's C.7.

### 5.4 Splits and merges applied, and whether any is wrong

| adjudication ordered | applied as | my verdict |
|---|---|---|
| rank 21 → 4 shapes | ph82, ph83, ph84, ph85 | ✅ right — one `I6` over four C shapes is a taxonomy |
| rank 8 → 2 | ph69, ph70 | ✅ right — missing increment vs unmatched decrement break `I7` from opposite directions |
| rank 23 → split CRASH-062 out | ph87, ph88 | ✅ right — the miner itself called it *"the weakest merge in this set"* |
| rank 12 → 5 + CRASH-139 | ph73, ph74 | ✅ **verified at source**: `zend_API.c:1957/1965/1966` is exactly as quoted, `ZVAL_STRINGL(&property, name, name_length, 0)` with `dup = 0`, and the CWE really is 590 not 562 |
| ty#4 / ty#13 **merge** | ph43 | ✅ **upheld, and I read both sites** — the manager flagged this as its remaining un-read overrule. `array.c:2688-2695` null-checks `HASH_OF`'s result and over-concludes; `url.c:612-613` does not check it at all. One helper (`zend_API.h:519`), two call sites of three lines each. **The cost is paid once and the pairing is the finding.** |
| sp#3 / sp#7 **merge** | ph04 | ✅ upheld — one extraction of `php_url_parse_ex`, two triggers eleven lines apart |
| ty#5 / ty#11 **split** | ph49, ph50 | ✅ upheld — ph50's kernel needs no re-entrancy at all, only a stale count from any source |
| CRASH-053 + CRASH-056 **pair** | ph46 | ✅ upheld as a pair; ⚠ **mechanism corrected**, §3.2 |
| CRASH-158 + sp#10 **cross-ref, do not merge** | ph53 ↔ ph32 | ⚠ **§5.5 below** |

### 5.5 ⚠ §5.4 of the task — the CRASH-158 / sp#10 pairing is a READING, and it survives, but I could not measure it either

The manager named this as least-sure call #4: *"it rests on a pairing with sp#10
that the manager reasoned from two candidate descriptions and did not measure."*

I read both at source. `zend_compile.c:2571` really does
`erealloc(ce->interfaces, sizeof(zend_class_entry *)*ce->num_interfaces)` with
`num_interfaces` already the full **declared** count and no zeroing;
`html.c:398/:401/:896` really do declare a range in `entity_map` and index a
separately-sized literal. **The shape claim — *a count declared in one place, an
extent realised in another, with no compiler or runtime relation between them* —
holds for both, and the class difference really does turn on which of the two
numbers the storage was sized from.**

⚠ **But "same C shape" is still a judgement, not a measurement, and I have no
instrument that would make it one.** What I can say that the adjudication could
not: the two rows differ in a third way it did not name — **ph32's excess is
read from a `char **` table of pointers (a NULL check at `:900` partially
covers it), ph53's is read from a `zend_class_entry **` with no check at all.**
The reassignment of CRASH-158 to the **type** axis I do endorse: the read is
in-bounds and nothing is freed, so neither spatial nor temporal fits, and
`CWE-824` + `I19` are the corpus's own view. `CLAUDE.md` rule 6 makes it a
classification either way, never a kill.

### 5.6 ⚠ Where the corpus's own labels are wrong — three, one of them new

| row | the disagreement |
|---|---|
| **CRASH-053** | `root_cause_id` = *"unchecked `make_real_object`"* — **wrong twice**: `:1635` checks, and `make_real_object` is correct. Found by the type miner, confirmed here. |
| **CRASH-009** | `c_file_line` = `reg.c:337`, which is the **guard** `if (new_l + 1 > buf_len)`; the wrapping expression is one line below at `:338`. The §6-addendum frame problem in miniature. |
| **CRASH-071** ⚠ **new** | `root_cause_id` = *"exception-ctor-debug-backtrace-copies-args-of-torn-down-executor-frame-during-shutdown-uaf"*; `c_file_line` = `Zend/zend.c:955`. ✅ `zend.c:955` is `z_context->value.ht = EG(active_symbol_table);`, inside the **error callback's `$errcontext` publication** (declarations `:871`, `ALLOC_INIT_ZVAL(z_context)` `:938`, `params[4] = &z_context` `:964`). **Nothing near `:955` is a backtrace, an exception constructor or a shutdown path.** The two fields describe different defects and I could not decide which is the row → catalogued as **ph91, `unresolved`**. |

⚠ Note the corpus is **not** wrong on CRASH-033: its `c_file_line` names both the
guard site and `zend_compile.c:2621`, which is the defect (§3.1).

---

## §6 ⚠ §5.2 of the task — the format judgement, and what I did instead

*"`≈80` rows may be the wrong size for a readable catalogue. If Part B at 150
words × 80 is unreadable, say so and propose the format that works — that
judgement is worth more than compliance."*

**Said: at 91 rows, 150-word blocks are unreadable, and I did not write them.**
The arithmetic: 91 × 150 ≈ 13 650 words ≈ **95 KB of Part B prose alone**, on
top of Part A and Part C. `.web/CLAUDE.md` names *"a document that is correct,
fully qualified and unreadable"* as this project's costliest reporting defect,
and `RECAP_PAT.md` reached 560 KB and stopped being read.

**What I shipped instead**, and it is a deviation I am stating rather than
hiding:

- **Part B blocks use a fixed six-field micro-schema of ~80–110 words** —
  citation line · mechanism · `▸ trigger` · `▸ benign + u64` · `▸ blob` ·
  `⚠ risk`. The fields are the ones §1 asks for; what is gone is the connective
  prose, which is the prose a reader skips.
- **Blocks are grouped under 23 mechanism-family headings, in table order** (the
  ordering §1 already mandates: axis then family). A reader navigates by family,
  not by 91 flat entries.
- Result: **`patterns-php/CATALOGUE.md` is 118 KB**, of which Part A — the whole
  navigation surface, one line per row — is ~16 KB. For comparison
  `RECAP_PHP.md` is 41 KB and `PLAN_PHP.md` 36 KB.

⚠ **If the manager wants it smaller, the lever is Part B, not Part A**, and the
honest way to pull it is to move the `⚠ risk` field into each row's future
`NOTES.md`. I did **not** do that, because the risk field is the only place a
future engineer learns *how an extraction of this row goes wrong*, and it is the
field that would have prevented at least three of the wave's kills.

---

## §7 ⚠ THE FOLDED REVIEW OF `TASK_PHP_010` — all four verified, two findings

`TASK_PHP_011` §7 folds `TASK_PHP_010`'s review into this task and asks whether
that compression was the right call.

**My answer: for these four fixes, yes — and I would not fold the next one.**
All four are mechanical, all four already had named controls, and re-running the
controls took minutes. ⚠ **But the compression cost something real: nobody
attacked the fixes' *design*, only their *behaviour*.** §7.5 is the one design
question I did look at and it produced a finding; there may be others.

### 7.1 M1 — one row enumeration (`_row_dirs`) ✅

```
$ python3 .temp/php9/a1_row_enum.py
=== (0) MUST NOT FIRE -- an ordinary, correctly linked row ===
  PASS     ph90-normal          refused=False expected=False
=== (3) ⚠ A DOTTED ROW DIRECTORY -- `glob` never matches a leading dot ===
  PASS     ph93-dotted          refused=True  expected=True
           | digest: .ph93-dotted: A DOTTED ROW DIRECTORY HAS NO SANCTIONED FORM -- rename it.
           os.listdir sees the row : True
           glob sees the row       : False
```

✅ Case 3 (the named must-fire) fires, with the by-name refusal the fix
specifies. Cases 0, 1, 2, 4, 5, 8 all PASS.

⚠ **Case (6) of the same probe still reports a HOLE**, and I flag it because the
task's must-fire list does not mention it:

```
=== (6) ⚠ a row with NO `c/` DIRECTORY AT ALL ===
  ⚠⚠ HOLE  ph96-noc             refused=False expected=True
           (a row with no c/ is SKIPPED -- `if not os.path.isdir(cdir): continue`, gate.py:466 and :354)
```

`TASK_PHP_010_REPORT.md:261` **does** disclose it in passing (*"`shared`
enumerated as a row: True (no c/ → both audits skip it)"*), so it is known, not
hidden. It is out of scope here; recording it so the next reader does not
re-derive it.

### 7.2 M2 — `ROW_DIRS = {c, inputs, controls}` ✅ both directions

Must-fire, from the named control:

```
$ python3 .temp/php9/a2_upward_include.py
  c_digest_audit  problems : 1
    | digest: ph98-upward: ph98-upward/aux/ IS NOT A SANCTIONED ROW DIRECTORY. A row may contain only c, inputs, controls/.
  -> PREFLIGHT WOULD PASS: False
```

Must-NOT-fire — the task names *"all 33 PAT rows, every one of which carries
`__pycache__/`"*. ⚠ **That control is vacuous under the php gate**: I measured
`gate._row_dirs(patterns-php)` and it returns **only** `patterns-php/ph00-smoke`;
the php gate never iterates `patterns/`, and `harness/check.py` has no
`ROW_DIRS`. So I ran the exemption on the row that *is* audited:

```
$ mkdir -p patterns-php/ph00-smoke/__pycache__ && touch patterns-php/ph00-smoke/__pycache__/x.pyc
$ python3 harness-php/gate.py --preflight ph00-smoke
  ok   every patterns-php/*/c/ file has a digest key
  ok   <row>/c/emalloc_shim.h symlink, UNCONDITIONAL
  ...
preflight OK (nothing else run)
rc=0
```

✅ The exemption is real (`gate.py:389 if e == "__pycache__": continue`) and the
row is still admitted. `__pycache__` removed afterwards; tree clean.

### 7.3 M3 + M4 — per-row coverage ✅

```
$ python3 .temp/php9/a4_orphan_deadlock.py
=== (1) ... under a planted orphan results-php/ph99-ghost.json ===
    gate.py --preflight ph00  ->  rc=0
      | | ⚠ OTHER ROW, not failed here: preflight coverage: results-php/ph99-ghost.json has NO preflight record beside it.
=== (4) is the mandated BRACKET blocked too? ===
    gate.py --tool measure --check-stale  ->  rc=0
      last line: 3 record(s) examined, 0 STALE
RESTORE EXACT (sha256 per file, 9 file(s)): True
```

✅ Both the must-fire (the orphan is still *reported*) and the must-NOT-fire (it
no longer *blocks* another row, and the mandated bracket returns rc=0) hold.

⚠ **MINOR finding, and it will mislead the next reader.** The same probe's §3
still prints a hard-coded verdict its own §1 and §4 measurements now contradict:

```
    cycle 3: repair rc=2   ph00 preflight rc=0   coverage problems still reported=1
    -> ⚠⚠ DOES NOT CONVERGE. The coverage stage is GLOBAL, so this blocks EVERY row's gate, including the mandated bracket.
```

**The numbers on the line above the verdict say `ph00 preflight rc=0`.** The
control was re-run and its conclusion string was not updated. Anyone re-running
the named control reads the verdict, not the numbers. `.temp/php9/` is another
task's evidence and I did not edit it; the manager should.

### 7.4 `MAX_RUNS` bounds evidence-carrying runs ✅

```
$ python3 .temp/php9/a5_notarball_and_cap.py
    gate.MAX_RUNS = 40
    ⚠ runs that CARRY EVIDENCE (non-empty `problems`)    n= 1000 -> kept    40  dropped 960
    ⚠ coverage-only failures (what A4's state produces)  n= 1000 -> kept    40  dropped 960
=== (b2) MUST NOT FIRE -- the cap still fires on the case the engineer measured ===
    120 genuinely distinct, no-problem runs -> kept 40, dropped 80
    the provenance_skipped entry survived: True
```

✅ Evidence-carrying runs are bounded, and the must-not-fire holds.

### 7.5 ⭐ THE QUESTION ONLY A CATALOGUE CAN ANSWER — would a row want a shared directory?

`RECAP_PHP.md` F20: `#include "../../shared/x.h"` escapes the row, compiles, runs
the outside allocator, and is in **no digest**. Reported, deliberately not fixed.
The task asks: *"say whether any row in this catalogue would plausibly want a
shared directory. If several would, the manager's 'latent, leave it' is wrong."*

**Answer, in two parts, and the second part is the one that matters.**

**(a) Far more than "several" rows want shared CODE.** Counted mechanically over
Part B's 91 blocks (⚠ this counts *mentions*, so read it as an upper bound on
"needs the definition" and a lower bound on "the question will come up"):

| shared thing | blocks naming it | which |
|---|---|---|
| the `zval` struct + `Z_*` accessors (`zend.h:275-293`, `zend_operators.h:234-275`) | **29 / 91** | ph01 ph11 ph23 ph30 ph33 ph34 ph38 ph39 ph40 ph41 ph42 ph43 ph52 ph54 ph61 ph63 ph65 ph67 ph68 ph72–ph78 ph81 ph84 ph87 |
| `zend_hash`'s `Bucket` / `HashTable` | **14 / 91** | ph23 ph39 ph40 ph41 ph43 ph49 ph50 ph63 ph65 ph66 ph67 ph75 ph76 ph80 |
| `zend_ptr_stack.h` | **2** | ph61, ph81 |
| the `temp_variable` union | **2** | ph46 (both limbs), ph71 |
| the exif blob readers `php_ifd_get{16,32}u` | **2** | ph13, ph14 |
| `common-php/emalloc_shim.h` | every allocating row | **already shared, already solved — and it is the proof that the door works** |

⚠ Some of those 29 are incidental (`ph01`'s risk note says PHP hands the lexer a
*"NUL-terminated zval string"*, which needs no definition). **The load-bearing
core is the ~12 type rows ph39–ph52, which cannot be written at all without the
tagged union and its accessors** — and twelve rows wanting one header is already
past "several".

**(b) ✅ But none of them wants a shared DIRECTORY, and I measured the door that
already exists.** `.temp/php11/shared_dir_probe.py`, on a throwaway row,
restoring the tree exactly:

```
=== (A) a SIBLING shared dir inside the row: <row>/shared/x.h ===
    c_digest_audit problems for this row: 1
      | digest: ph89-sharedprobe: ph89-sharedprobe/shared/ IS NOT A SANCTIONED ROW DIRECTORY.
    -> REFUSED BY ROW_DIRS: True

=== (B) an include that escapes the ROW: ../../../<dir>/x.h ===
    c_digest_audit problems for this row: 0
    gcc rc=0
    ./bin -> tally=1
    'shared-probe-tmp/x.h' in ANY row digest: False
    -> ESCAPES BOTH DIGESTS AND COMPILES: True

=== (C) the SANCTIONED door: common-php/x.h SYMLINKED as <row>/c/x.h ===
    c_digest_audit problems for this row: 0
    gcc rc=0
    files the c/ digest can see: ['c/_probe_shared.h', 'c/bin', 'c/emalloc_shim.h', 'c/kernel.c']
    -> a shared FILE arrives inside c/ and is hashed like any other: True

RESTORE EXACT: True
```

**Three results, and they settle the question:**

1. ✅ **`TASK_PHP_010`'s M2 has already closed F20's *in-row* spelling** — a
   `<row>/shared/` directory is now refused by name. The RECAP's *"deliberately
   not fixed"* is **partly obsolete** and should say so.
2. ⚠ **F20's repo-level spelling is still live**: an `#include` that leaves the
   row entirely compiles, runs, and sits in neither digest with **zero**
   preflight problems.
3. ✅ **The sanctioned door works and needs no new mechanism.**
   `common-php/<file>` symlinked as `<row>/c/<file>` lands inside `c/` and is
   hashed exactly like `emalloc_shim.h` already is — **in both digests**.

> **So the manager's *"latent, leave it"* is right about the risk and wrong about
> the reason, and the correct action is not an infrastructure task.** The 17 rows
> that want a shared `zval.h` will get it through a door that already exists and
> is already audited. ⚠ **What they need is one sentence of documentation, and
> they need it BEFORE the first sharing row is built**, because the two natural
> mistakes are exactly the two that fail: an engineer extracting
> `Zend/zend_hash.c` will want to mirror the tarball layout
> (`<row>/Zend/zend_hash.h` — now refused, loudly, which is fine) or reach up to
> a repo-level `shared/` (**invisible**, which is not). `PROTOCOL_PHP.md` §B2
> already documents the symlink for the allocator; it needs one clause saying
> *"and this is how a row shares ANY file"*.

---

## §8 What I did NOT do, and what I am unsure about

1. **I built nothing and ran no PHP.** Every tier in the catalogue is an estimate
   read off the source. `crashes_pristine_5_0_0` is carried from the corpus and
   re-verified for **no** row.
2. **I did not run a single reproducer.** ⚠ Three claims would be settled by
   doing so and are not settled now: **CRASH-021** (does this box's glibc
   `strftime` actually fault? — the row's status turns on it), **ph91/CRASH-071**
   (which of its two disagreeing fields is the row), and **ph63/LOGIC-001**'s
   DJBX33A preimage, which nobody has computed.
3. **`echoes` is a reading, not a measurement.** I did not open one `pNN` to
   confirm a mechanism match. Every `echoes` value in the catalogue is a
   hypothesis for the builder to check, and I say so in the catalogue's §9.
4. **`inv/obl` is carried across from the corpus's blind labelling unmodified.**
   I re-derived no label.
5. **I did not verify the miners' quoted C for the rows I added.** §2.3's 53
   triples come from `candidates.json`; the 22 rows I reversed or added have
   their citations checked for *existence and range* (§2.2's 222/222) and their
   *defect sites* read by hand, but there is no mechanical quote check for them
   because there is no quote artefact to check against.
6. **`patterns-php/CATALOGUE.md` is 118 KB and I am not certain that is small
   enough.** §6 gives the argument and the lever. It is the judgement in this
   task I would most like attacked.
7. ⚠ **`.temp/php11/_cache/` (the extracted tarball) is deleted.** It is a
   derived artefact; `pristine.py` rebuilds it on first use. Everything under
   `.temp/php11/` that is evidence — the five `.py` generators, `fdset_probe.c`,
   `asan_control{,2}.c`, `CATALOGUE.pre-insert.md` and the batch files — stays.
8. **I did not re-run the ASan census.** §9.3 of the catalogue quotes
   `ADJUDICATION_001.md` §8b's *"zero of 2520 spatial reports fault in `Zend/` or
   `ext/standard/`"* on the adjudication's word. That number decides whether
   `hotness` can exist for the spatial axis at all and **it deserves an
   independent re-derivation that this task did not give it.**
9. **Two of my own reversals rest on a reading, not a run.** CRASH-133's chain
   (unclamped scale → `int` wrap in `pemalloc(length+scale)` → the zero-fill
   loop) I traced by hand but did not execute; CRASH-147's second-concat wild
   write likewise. Both are catalogued with the trigger stated so a builder can
   falsify them cheaply.

---

## §9 Everything I refute, in one list

`PROTOCOL.md` rule 2. **Reconciliation is the manager's job; this is what I am
handing over.**

| # | claim | source | verdict |
|---|---|---|---|
| 1 | *"if criterion-3-vs-tier is not crisp, ~17 reversals are wrong and the catalogue is inflated by a fifth"* | `TASK_PHP_011` §5.1, §6 | ⚠ **inverted.** The distinction is crisp; the audit was applied to the kills only. The catalogue is **larger** by 11, not smaller by 17 |
| 2 | *"Kills UPHELD (the C program genuinely fails criterion 1 or 3)"* — CRASH-133/135, 097, 098, 147 | `ADJUDICATION_001.md` §3b | ⚠ **all five refuted at source**, §1 |
| 3 | *"the 'ordinary null-deref' set — mechanism-quality judgement on the C, **which the bar permits**"* | `ADJUDICATION_001.md` §3b | ⚠ **the bar does not permit it.** Quality is not one of the four criteria; distinctness is |
| 4 | CRASH-107 is at `string.c:4119/:4143/:4144` | `ADJUDICATION_001.md` §0, §7 | ⚠ **`:4120/:4144/:4145`** — off by one on all three. The miner was right |
| 5 | CRASH-123 is at `mbfilter_htmlent.c:177` and `:181` | `ADJUDICATION_001.md` §0, §1b | ⚠ **`:178` and `:183`** — in the audit's headline exhibit. The CSV was right |
| 6 | CRASH-053 *"reads the `var` arm with no test at all"* → wild `zval **` | `ADJUDICATION_001.md` §7b | ⚠ **the test is at `zend_execute.c:141`**; the bug is the `return` at `:147`. The result is a NULL deref, as the corpus says. **The pairing survives and is stronger** |
| 7 | *"CRASH-033 shows the corpus's `missing-guard` field can name a third frame that is none of them"* | `ADJUDICATION_001.md` §7a | ⚠ the corpus field names **both** frames and `:2621` is the defect. The conclusion stands; this supporting claim does not |
| 8 | CRASH-096 *"lands inside the stream layer, which is where CRASH-097/098 legitimately died"* | `ADJUDICATION_001.md` §3d | ⚠ **third answer**: the defect is `Zend/zend_operators.h:134`, a 24-line inline, blob-pure. **Admitted as ph15** |
| 9 | the `≈80` catalogue size | `ADJUDICATION_001.md` §5 | ⚠ **91** |
| 10 | *"all 33 PAT rows"* is M2's must-not-fire | `TASK_PHP_011` §7 | ⚠ **vacuous** — the php gate never iterates `patterns/`. Ran the real control on `ph00-smoke` instead |
| 11 | F20 *"`#include "../../shared/x.h"` … deliberately not fixed"* | `RECAP_PHP.md` F20 | ⚠ **partly obsolete** — M2 now refuses the in-row spelling. The repo-level spelling is still live, and **the sanctioned door already exists** (§7.5) |
| 12 | *"a shared directory would need scheduling now"* | `TASK_PHP_011` §7 | ⚠ **no.** 17 rows want shared *files*; `common-php/x.h` → `<row>/c/x.h` carries them into both digests today. What is owed is one clause in `PROTOCOL_PHP.md` §B2 |
| 13 | ✅ **upheld, and I read the sites the manager had not** — the ty#4/#13 merge | `ADJUDICATION_001.md` §6 call #2 | ✅ the merge is right; one helper, two three-line call sites |
| 14 | ⚠ the CRASH-158 / sp#10 pairing | `ADJUDICATION_001.md` §6 call #3 | ⚠ **survives as a reading; still not measured, and I have no instrument that would measure it.** §5.5 |

---

## §10 Memory updates

**None written.** `PROTOCOL.md` rule 9: nothing here reaches `.memory-php/`
until this report is reviewed. ⚠ **Three things I would propose for it once it
is**, in priority order:

1. **A kill written as a SET hides its members from row-level review** (§5.2).
   The check is one script and it found three rows nobody had looked at.
2. **An audit of a kill list must also audit the UPHELD list** (§1). The same
   lens, turned around, moved five rows.
3. **The defect site, the guard site and the faulting site are three different
   places**, and this catalogue has a fourth instance the adjudication does not:
   **CRASH-009**, whose `c_file_line` names the guard (`reg.c:337`) while the
   wrapping expression is at `:338`.

⚠ **One thing I am asking the manager to decide, not to record:** whether the
`TASK_PHP_010` fixes need a review of their own beyond §7. **My answer is no for
these four** — they are mechanical, their controls pre-existed, and I re-ran
every one. ⚠ **But the fold reviewed BEHAVIOUR and not DESIGN**, and the one
design question I did ask (§7.5) produced a finding that changes a standing
decision. If the manager wants the design attacked, that is a different task and
it should be scoped as one.
