# TASK_PHP_034_REPORT — `ph45`'s R1h, why `crashes_pristine_5_0_0` is `False`, and the build brief

**Role: research engineer. One agent, alone. NOTHING WAS BUILT.** No
`patterns-php/` directory, no rung, no `spec.md`, no gate, no measurement. The
only paths I created are this file and `.temp/php34/`. Per the task file I ran
neither staleness bracket (`TASK_PHP_033` is re-gating `ph29` concurrently);
`git status --porcelain` is in §8.7. I did not read `patterns-php/ph29*`.

---

## §0 Headline, before the detail

| | |
|---|---|
| **§3 — why `crashes_pristine_5_0_0 = False`** | ⭐⭐ **SETTLED, AND IT IS A BUILD-CONFIGURATION ARTEFACT WITH NOTHING TO DO WITH THE MECHANISM. The "pristine" binary was configured `--disable-all`, so `mb_convert_encoding()` DOES NOT EXIST in it and `CRASH-123.php` dies with `Fatal error: Call to undefined function` before one line of C in `mbfilter_htmlent.c` runs.** Three independent lines of evidence in §5, and **the corpus says so itself**: `paper/invariants-166.json`'s CRASH-123 entry opens *"the pristine `build/bin/php-5.0.0` has no mbstring, so the reproducer only prints `Fatal error: Call to undefined function mb_convert_encoding()`; on the corpus's own mbstring-enabled 5.0.0 build … it SIGSEGVs with a WRITE access to `0x000000014ae8` at `…mbfilter_htmlent.c:183`."* |
| **the field is `hard_crash` of the stock run** | Measured: `crashes_pristine_5_0_0` equals `validation/data/stock-run.json`'s `hard_crash` on **142 of 142** rows where both exist, and **all 15 `build: fullext` rows have `stock_rc = 255`** (PHP's fatal-error exit) and `crashes_pristine = False`. **15 of 15. The field is a property of the BINARY, not of the defect.** |
| **does the defect reproduce?** | ⭐ **YES, and the corpus's own `independent_rerun` says `reproduces: true`, `n_fault: 3/3`, `kind: SEGV`, `frame: mbfilter_htmlent.c:183`, `func: mbfl_filt_conv_html_dec`.** I reproduced it independently: **60 of 60 runs SEGV** under R1 with `common-php/emalloc_shim.h`, **0 of 60** under R1h. |
| ⚠⚠⚠ **the finding that changes the row's design** | **THE DEFECT IS NOT INPUT-CONDITIONED.** On a 64-bit box with a PIE heap, `mbfl_filt_conv_html_dec_dtor` frees the truncated pointer at `:169` **whether or not the input contains an `&` at all** — so a "benign" corpus faults too. Measured: `SHIM/BENIGN` (`"hello, world"`) prints `FED ok`, `FLUSHED ok`, then SEGVs in the dtor. **PHP 5.0.0's HTML-ENTITIES decode direction is totally broken on 64-bit, not broken on an adversarial input** — and the corpus's own Rust evaluation records the same thing: *"C-5.0.0-webext has no answer on the decode direction at all (rc 139 on every probe)"*. |
| **R1h** | ⭐⭐ **SETTLED. `e8901dc17087`, and the subject is misleading but the patch is a REAL AND COMPLETE FIX.** It is not a cast at the use site: it **adds a new `void *opaque;` member to `struct _mbfl_convert_filter`** (`mbfl_convert.h`) and moves **all six** `filter->cache` uses in `mbfilter_htmlent.c` onto it. **The truncation is removed, not silenced.** |
| **backport cost** | ⭐ **ZERO. `patch -p1` onto the pristine tarball: rc=0, NO FUZZ, NO OFFSET, both files.** The commit's pre-image **is** 5.0.0 byte-for-byte. Cleaner than `ph64`'s, which needed `fuzz 1`. |
| **tag bracket** | Guard **ABSENT** at php-5.0.0/.1/.2/.3, **PRESENT** at php-5.0.4 and at **every tag through `master`** (21 years, never reverted; only `mbfl_malloc`→`emalloc` since). Window **php-5.0.3 → php-5.0.4**; the commit's date (2005-02-21) sits inside it. The 5.0.3→5.0.4 diff of the file is this commit's hunks **plus exactly one unrelated line** (§4.4). |
| **is it correct and complete?** | ⭐ **YES on both — I attacked it on five fronts (§4) and it survived all five.** ⚠ *I am deliberately NOT giving this a position in a running tally* — `.memory-php/02-ladder.md` records `ph03`/`ph07` as neither minimal nor sufficient, `ph16` as complete and minimal, `ph29` as closed by neither stage, and `ph64` as unfaultable, and says in terms **"there is no run and never was one."** This is a sixth data point, not a trend. It covers all four uses the corpus cites **and two the corpus does not** (`:148`, `:249`). `mbfilter_htmlent.c` is the **only** file in the tarball that stores a pointer in `cache` (measured, whole-tree grep). It also incidentally removes an **aliasing double-free** in `mbfl_convert_filter_copy` (§4.3). |
| **tier** | ⚠ **`narrowed`, NOT the catalogue's `verbatim` — and this is a judgement call I want attacked** (§6.2). The four functions lift as-is; what forces `narrowed` is that the allocator substitution **cannot** be given a `why` ending in *"no semantics"*, because the address it returns **is** the mechanism. |
| **the oracle** | ⚠ **The catalogue's `u64 = decoded bytes + (allocs, frees)` MEASURES NOTHING** — `ph64`'s lesson repeating. Measured: in the lossless regime R1 and R1h give **bit-identical** folds on all four inputs and identical alloc/free counts. ⭐ **But a second oracle DOES measure, deterministically and WITHOUT faulting** — `alias_probe`: R1 decodes `&amp;` to **674** where R1h decodes it to **38**, fold `06990488588011114691` vs `06990488587375112783` (§6.4). |
| **size** | The catalogue says **five lines**. The **mechanism** touches **15** tarball lines (§2.1). The **extraction** is **477 raw lines / 441 code lines**, of which **254 are the entity table**; the logic is **~189 code lines** (§6.6). |
| ⚠ **the task file premises that are wrong** | §2's *"five lines … that is the whole mechanism"* (it is 15), §3's *"the trigger depends on where the allocator happens to put the block"* (it does not — it is deterministic on this box), and §5.1's off-by-one attribution is **right about `ADJUDICATION_001.md` and I confirm it**. Full list in §7. |
| ✅ **what held exactly** | Every measured claim in the task file's §2: `mbfl_convert.h:49`, `:161`, `:169`, `:178`, `:183`, the CSV fields, the `zval`-free include list, and the fix-survey row. And §5.2's catalogue claim — *"the only row in 166 with its own invariant"* — **is TRUE and now attributed rather than repeated** (§4.5). |

---

## §1 Method

`PROTOCOL_PHP.md` §C and §F5, in this order and no other:

1. the defect pinned by reading the **pinned tarball** (`SOURCES.md` §2 recipe;
   sha256 re-verified `5783e0c0ba94…d6919`, 5 595 997 B; every cited file
   checked against `patterns-php/php-5.0.0.manifest` — all eight present,
   §6.1);
2. the named commit's **patch bytes** read
   (`.temp/mgr/batch/patches/e8901dc17087.patch`, 74 lines, cached by the
   manager);
3. **then** applied to the pristine tarball and bracketed against 16 release
   tags (`raw.githubusercontent.com`, 3 paths each);
4. R1h stated with the artefacts that decide it;
5. everything the row's behaviour turns on **measured with a forked probe
   carrying declared expectations**, never argued.

⚠ **§C's *"scan tags until one suits"* trap was live and I did not take it.**
The verdict is decided by the **patch bytes** — the commit changes the type of
the storage — and the tags only confirm it. The confirmation is a *derivation*:
the php-5.0.3 → php-5.0.4 diff of both files **is** this commit's hunks, modulo
one unrelated line I name and attribute (§4.4).

⚠ `grep -a` throughout (F35). ⭐ And I asked about **functions, not text**:
`.temp/php34/fnbody.py` is a brace-matching extractor with **16 declared cases,
6 must-NOT-fire**, `--selftest` PASS — including, pre-emptively, `TASK_PHP_031`'s
case M (`f(...) /* {{{ */` before the brace, which made *its* first version
report ABSENCE for two functions that were plainly present).

---

## §2 The mechanism, verified line by line in the pinned tarball

```
mbfl_convert.h:49                int cache;                                  <== THE FIELD (32 bits)
mbstring.c:764                   __mbfl_allocators = &_php_mb_allocators;    (MINIT)
mbfl_allocators.h:48             #define mbfl_malloc (__mbfl_allocators->malloc)
mbstring.c:240-243               _php_mb_allocators_malloc -> emalloc        <== so mbfl_malloc IS emalloc
mbfilter_htmlent.c:161           filter->cache = (int)mbfl_malloc(16+1);     <== TRUNCATING STORE
mbfilter_htmlent.c:178           char *buffer = (char*)filter->cache;        <== CAST BACK #1 (sign-extends)
mbfilter_htmlent.c:183           buffer[0] = '&';                            <== WILD WRITE  (the corpus's frame)
mbfilter_htmlent.c:249           buffer = (char*)filter->cache;              <== CAST BACK #2 -- NOT CITED ANYWHERE
mbfilter_htmlent.c:169           mbfl_free((void*)filter->cache);            <== WILD FREE, and it is UNCONDITIONAL
```

**Trap §5.5 discharged, and it matters more than it looks.** `mbfl_malloc` is
**not** a function: `mbfl_allocators.h:48` is `#define mbfl_malloc
(__mbfl_allocators->malloc)`, an indirection through a table. libmbfl's own
default (`mbfl_allocators.c:62-77`) is plain `malloc`/`free`; **PHP rebinds the
whole table to `emalloc`/`efree`/`erealloc`/`ecalloc` at
`PHP_MINIT_FUNCTION(mbstring)`, `mbstring.c:764`.** So §B applies in full and
`common-php/emalloc_shim.h` is the right allocator for this row. (`ph07`'s
`c/main.c:19-20` already says this; I re-derived it rather than inheriting it.)

⭐ **The consequence nobody has written down: "which allocator" is UPSTREAM-PARAMETRIC here.** The extracted lines do not name an allocator; they name a
*table entry*. That is the ground on which §6.3's placement substitution stands.

### 2.1 ⚠ "Five lines" is wrong. The field is dereferenced ELEVEN times.

`grep -an 'buffer\[' mbfilter_htmlent.c` (`.temp/php34/logs/…`, and the source
is in `.temp/php34/src/`):

```
:183  buffer[0] = '&';                      the corpus's cited wild WRITE
:189  buffer[filter->status] = 0;
:190  if (buffer[1]=='#') {                 wild READ
:193  ent = ent*10 + (buffer[pos] - '0');   wild READ
:215  buffer[filter->status++] = ';';
:216  buffer[filter->status] = 0;
:223  buffer[filter->status++] = c;         <- the rust-eval's second cited write
:230  buffer[filter->status] = 0;
:236  buffer[0] = '&';
:253  CK((*filter->output_function)(buffer[pos++], …));   in _dec_flush
      + strcmp(buffer+1, entity->name) at :202            wild READ of a C string
```

**So the mechanism spans 15 tarball lines** — `:49` (declaration), `:161`
(store), `:169` (free), `:178` and `:249` (the two casts back), and ten
dereferences — **across TWO functions plus the flush, not "two functions" and
not "five lines".** The catalogue's five are the five *most legible* lines; a
row built to them would not lift `:249`, and `:249` is one of the two places the
patch changes.

### 2.2 ⚠ The ENCODE half of the same file carries a SECOND, UNCATALOGUED defect

`mbfilter_htmlent.c:101` declares `int tmp[64]`; `:123` is
`int *p = tmp + sizeof(tmp);` — **`tmp + 256`, i.e. 192 `int`s past the end of
the array** — and `:129` immediately does `*(--p) = '\0'`, a stack write 768
bytes out of bounds. php-5.0.4 carries `tmp + sizeof(tmp)/sizeof(tmp[0])`, and
that one-line change is the **only** difference between patched-5.0.0 and
php-5.0.4 in this file. It is **not** in `e8901dc17087` and **not** in
`index.csv` (the only corpus row citing `mbfilter_htmlent.c` is CRASH-123).
⚠ **Reported, not pursued** (`PROTOCOL.md` *"do not improve scope; if you see
adjacent work, report it"*). **It is also why the row must NOT lift
`mbfilter_htmlent.c:99-150`** — doing so would put a second, different
memory-safety defect inside a row whose contract names one.

---

## §3 R1h — the verdict, `_029`/`_031` shape

```
ph45 · CRASH-123 / V5C-123
   ext/mbstring/libmbfl/mbfl/mbfl_convert.h:49            (the FIELD -- the defect)
   ext/mbstring/libmbfl/filters/mbfilter_htmlent.c:161    (the truncating STORE -- the CSV's c_file_line)
   ext/mbstring/libmbfl/filters/mbfilter_htmlent.c:183    (the wild WRITE -- the corpus's ASan frame #0)
   BOTH of those files are WHERE THE REPAIR LANDS
```

| | |
|---|---|
| named `fix_commit` | **`e8901dc17087075645dc867a9b6d7d534673482b`** — Moriyoshi Koizumi `<moriyoshi@php.net>`, **Mon, 21 Feb 2005 10:12:43 +0000** |
| subject | *"- Fix bug #30573 (compiler warning due to invalid type cast)"* |
| files | `ext/mbstring/libmbfl/filters/mbfilter_htmlent.c` (14 lines: 7+/7−) and `ext/mbstring/libmbfl/mbfl/mbfl_convert.h` (1+) — **2 files, 8 insertions, 7 deletions** |
| does it touch the **cited** store `:161`? | ✅ **YES** — it is one of the seven deleted lines |
| does it touch the **field declaration** `mbfl_convert.h:49`? | ⚠ **NO — and that is the interesting part.** It **leaves `int cache;` in place** and **adds a new member `void *opaque;`** at the end of the struct. `cache` is still an `int` in `master` today, because **26 other filters use it as an actual integer accumulator** |
| does it **remove the defect**? | ✅ **YES, completely** — §4 |
| backport | ⭐ `patch -p1 --dry-run` on the pristine tarball: **`rc=0`, both files, NO FUZZ, NO OFFSET.** The commit's pre-image **is** php-5.0.0 |
| tag window | **php-5.0.3 → php-5.0.4**, and the commit's date is inside it |
| **R1h VERDICT** | ⭐ **`e8901dc17087`, WHOLE, UNMODIFIED — all three `mbfilter_htmlent.c` hunks and the `mbfl_convert.h` hunk.** No subset question arises: the four hunks are one change and no later commit removes any of it |

### The patch (all four hunks, abridged to the changed lines)

```diff
--- a/ext/mbstring/libmbfl/mbfl/mbfl_convert.h        @@ -51,6 +51,7 @@
  	int illegal_substchar;
+ 	void *opaque;
  };
--- a/ext/mbstring/libmbfl/filters/mbfilter_htmlent.c @@ -145,7 +145,7 @@   (_enc_flush)
- 	filter->cache = 0;
+ 	filter->opaque = NULL;
                                                      @@ -158,24 +158,24 @@  (ctor/dtor/_dec)
- 	filter->cache = (int)mbfl_malloc(html_enc_buffer_size+1);
+ 	filter->opaque = mbfl_malloc(html_enc_buffer_size+1);
- 	if (filter->cache)                                    +	if (filter->opaque)
- 		mbfl_free((void*)filter->cache);                  +		mbfl_free((void*)filter->opaque);
- 	filter->cache = 0;                                    +	filter->opaque = NULL;
- 	char *buffer = (char*)filter->cache;                  +	char *buffer = (char*)filter->opaque;
                                                      @@ -246,7 +246,7 @@   (_dec_flush)
- 	buffer = (char*)filter->cache;
+ 	buffer = (char*)filter->opaque;
```

### The tag bracket (`.temp/php34/fetch.sh`, `fnbody.py`, `logs/03-tagbracket.log`)

`mbfl_filt_conv_html_dec_ctor`'s body, brace-matched and hashed, beside the
struct's own members:

```
tag         struct member(s)            ctor body sha16      the ctor's store
php-5.0.0   int cache;                  899efed33cfb6d1d     filter->cache = (int)mbfl_malloc(html_enc_buffer_size+1);
php-5.0.1   int cache;                  899efed33cfb6d1d     "
php-5.0.2   int cache;                  899efed33cfb6d1d     "
php-5.0.3   int cache;                  899efed33cfb6d1d     "   <- LAST tag with the defect
php-5.0.4   int cache; + void *opaque;  54215dd5ddf6f07f     filter->opaque = mbfl_malloc(html_enc_buffer_size+1);
php-5.0.5   int cache; + void *opaque;  54215dd5ddf6f07f     "   <- FIRST tag with the fix
php-5.1.0 … php-7.0.0  (6 tags)         54215dd5ddf6f07f     "   byte-identical
php-8.3.0   int cache; + void *opaque;  6225002b5733ef35     filter->opaque = emalloc(html_enc_buffer_size+1);
master      int cache; + void *opaque;  6225002b5733ef35     "
```

⭐ **The repair survives 21 years unreverted, and the only later change is
`mbfl_malloc` → `emalloc`** when libmbfl stopped being a separable library.
**That is an independent upstream artefact that this is the accepted repair** —
the same kind of evidence `ph64`'s guard-strengthening gave, and it is what
makes the misleading subject line safe to discount.

### The backport, and it costs nothing

```
$ patch -p1 --dry-run < patches/e8901dc17087.patch     # onto the pristine tarball
checking file ext/mbstring/libmbfl/filters/mbfilter_htmlent.c
checking file ext/mbstring/libmbfl/mbfl/mbfl_convert.h
rc=0
$ diff patched-5.0.0/…/mbfl_convert.h  tags/php-5.0.4--…mbfl_convert.h      -> IDENTICAL
$ diff patched-5.0.0/…/mbfilter_htmlent.c  tags/php-5.0.4--…mbfilter_htmlent.c
   ONE hunk, at :123, and it is §2.2's UNRELATED array-size bug fix
$ diff pristine-5.0.0/…/mbfilter_htmlent.c tags/php-5.0.3--…              -> IDENTICAL
```

**No fuzz, no offset, no witness tag needed.** This is the cleanest R1h backport
in the programme so far — cleaner than `ph64`'s, which took `fuzz 1`.

---

## §4 Is the fix CORRECT, and is it COMPLETE?

⚠ `PROTOCOL_PHP.md` §C: *"an upstream fix is not automatically correct."*
`.memory-php/02-ladder.md` at n = 4: *"four rows, four different answers … the
honest reading is that there is no run and never was one."* I attacked it on
five fronts and it survived all five. ⚠ **That is evidence about THIS fix and
about nothing else; do not let it become a prior.**

### 4.1 It is minimal

Eight insertions, seven deletions, two files. Every added line is either the new
member or one of six mechanical `cache` → `opaque` rewrites. **Nothing else in
the commit touches C** — no NEWS entry, no test, no refactor. ⚠ **The absence of
a test and a NEWS entry is the one place `ph64`'s evidence was stronger**, and
it is what makes the tag bracket load-bearing here rather than merely
confirmatory.

### 4.2 It is complete FOR THE FILE, and the coverage is measured, not argued

`grep -arn '(int)mbfl_malloc|(char\*)filter->cache|(void\*)filter->cache'` over
**the whole tarball**:

```
ext/mbstring/libmbfl/filters/mbfilter_htmlent.c:161   filter->cache = (int)mbfl_malloc(...)
ext/mbstring/libmbfl/filters/mbfilter_htmlent.c:169   mbfl_free((void*)filter->cache)
ext/mbstring/libmbfl/filters/mbfilter_htmlent.c:178   char *buffer = (char*)filter->cache
ext/mbstring/libmbfl/filters/mbfilter_htmlent.c:249   buffer = (char*)filter->cache
```

**Four sites, one file, and the patch rewrites all four.** 26 other filters
touch `filter->cache` (up to 30 times each) and **every one of them uses it as
an integer**, which is why `int cache;` correctly stays. ⭐ **The patch also
rewrites two uses the corpus never cites** — `:148` (`_enc_flush`) and `:249`
(`_dec_flush`) — so it is **larger** than the catalogued defect, not smaller.

### 4.3 ⭐ It removes a SECOND defect nobody attributed to it

`mbfl_convert.c:299-317` `mbfl_convert_filter_copy` copies
`dist->cache = src->cache` (`:312`) and — before the fix — that **aliases one
heap work buffer into two filters**, each of which will `mbfl_free` it in its
own dtor: a **leak of the destination's own buffer plus a double free**. The
copy is reachable with an HTML-ENTITIES filter: `mbfilter.c:1434` /`:1525`
/`:1539` back up and restore `pc->decoder` inside `mbfl_strimwidth`, and
`mbfilter.c:1309-1331` does the same in the `mbfl_convert_encoding`
length-detection loop. **After the fix, `opaque` is simply not copied** — the
two filters keep their own buffers, and `dist->opaque` is never uninitialised
because the ctor always sets it and no other filter reads it.

⚠ **The honest residue:** post-fix, `copy` still transfers `status` without the
buffer it indexes, so a backed-up partial entity is restored against the wrong
bytes. **That is a correctness defect, not a memory-safety one, and it was
equally wrong before the fix** (the aliased buffer had also moved on). **The fix
is strictly better on both axes.** I did not measure this; it is read at source.

### 4.4 ⚠ One thing in the release window is NOT this commit, and I name it

php-5.0.4's `mbfilter_htmlent.c` differs from patched-5.0.0 by exactly one line —
§2.2's `tmp + sizeof(tmp)` → `tmp + sizeof(tmp)/sizeof(tmp[0])`, in the ENCODE
function. **It is a different defect, in a different function, in a different
direction of the filter, and it is not in `e8901dc17087`.** I did not identify
its commit. ⚠ **Naming it matters because the tag bracket is otherwise a
one-candidate window and this is the second candidate in it** — it just cannot
be this row's fix, since it touches neither `cache` nor `opaque` nor any line
the row cites.

### 4.5 ✅ `pointer-value-integrity` — the catalogue's strong claim is TRUE, and here is the attribution

`CATALOGUE.md` calls `ph45` *"the only row in 166 with its own invariant"* and
`ADJUDICATION_001.md:89` says the same. **Do not repeat it; cite this.** The
labels live in **`paper/invariants-166.json`** (not in `index.csv`), which
labels all 166 cases. Measured over all of them:

```
distinct invariant ids across 166 cases : 20
of which NOT of the form I<n>           : 1
  CRASH-123 | NEW:pointer-value-integrity
    "A pointer stored into a field and read back designates the same object it
     did when stored; no storage or conversion step on that round trip
     discards part of its value."
```

⭐⭐ **And it carries THREE obligations that map ONE-TO-ONE onto the row's three
cited lines** — which is the strongest thing the row has for its R5 rung:

| oid | text (verbatim) | the line |
|---|---|---|
| `O1` | *"a pointer must not be stored into an integer field narrower than a pointer, nor otherwise round-tripped through a type that cannot represent every pointer value"* | `:161` |
| `O2` | *"a value read back out of such a field must not be converted to a pointer and dereferenced without re-establishing that it designates the original object"* | `:178`/`:249` → the ten derefs |
| `O3` | *"a value that is not an address returned by the allocator must not be handed to the deallocator (composes with I5/O4)"* | `:169` |

The same record lists `I1` (*"every read or write through a pointer lands
strictly inside the allocation that pointer was derived from"*) as
**`role: contributing`**. So the row's `inv/obl` cell should read
**`pointer-value-integrity/O1+O2+O3, I1/O1 (contributing)`**, not the bare
`pointer-value-integrity` the catalogue carries.

---

## §5 ⭐⭐ THE TASK FILE'S §3, ANSWERED

### 5.1 What `crashes_pristine_5_0_0` actually is

`SUMMARY.md:147` gives the column as *"crashes pristine php-5.0.0"* vs *"silent
(needs the detector build)"*, and `:173` defines the sibling column:
**`build` — `asan` (default, `--disable-all`) or `fullext`.** Three independent
derivations, all pointing the same way:

**(1) The field IS the stock run's `hard_crash`.** Measured over the whole
corpus (`.temp/php34/logs/01-pristine-field.log`):

```
crashes_pristine_5_0_0 == stock-run.json.hard_crash :  agree=142  disagree=0
                                            (the other 24 are `n/a (non-crash class)`)
```

**(2) Every `fullext` row is `False`, and every one exits 255.** `rc 255` is
PHP's fatal-error exit, not a crash:

```
build=fullext, crashes_pristine=False : 15 of 15
fullext stock rc histogram            : {255: 15}       <- ALL of them
asan    stock rc histogram            : {-11: 67, 0: 49, -6: 6, 255: 4, None: 1}
```

**(3) CRASH-123's own ASan log says it in English.**
`validation/logs/CRASH-123.asan.log` is **four lines**, and they are:

```
=== STDOUT ===
Fatal error: Call to undefined function mb_convert_encoding() in …/CRASH-123.php on line 3
=== STDERR ===
```

⭐ **And `paper/invariants-166.json`'s CRASH-123 entry states the whole thing as
its `observed_effect`**, quoted in §0.

> ⚠⚠ **SO `crashes_pristine_5_0_0 = False` HERE IS NOT `PROTOCOL_PHP.md`
> §B1.1's CASE.** §B1.1's reason — *"the size-class cache hands the freed block
> straight back, so the violation is silent"* — is a real mechanism and it is
> the right reading for **temporal** rows (it is exactly `ph64`'s, `_031` §6.4).
> **It is the WRONG reading for `ph45`.** Here the reason is that the function
> under test **did not exist in the binary**. **§B1.1's conclusion survives
> untouched — the field is never an admission filter — but its stated MECHANISM
> does not generalise to the 15 `fullext` rows, and a future agent reading
> §B1.1 alone would reach for a cache explanation that is not true of any of
> them.** This is a `.memory-php/` note the manager may want; I am not writing
> it (§8.1).

### 5.2 The manager's four candidate explanations, adjudicated

| candidate | verdict |
|---|---|
| *"the corpus's crash determination used a build where the filter path was never reached"* | ✅ **RIGHT, and in its strongest form**: not merely unreached — **not compiled in** |
| *"the truncated value happened to stay mappable"* | ❌ **Refuted.** The corpus's own fullext rerun faults 3/3 at `:183`, and my probe faults 60/60 |
| *"the build was 32-bit"* | ❌ **Refuted.** The fullext ASan log's frame addresses are 48-bit (`0x558c23efc714`) and the faulting address is a truncated-then-sign-extended 64-bit pointer |
| *"the `False` is about the shipped input rather than the mechanism"* | ❌ **Refuted, and inverted**: the field is about the **binary**, and the mechanism does not depend on the input at all (§5.4) |

And the manager's framing — *"on a modern 64-bit Linux the heap sits far above
2³², so truncation should be close to guaranteed, which would make `False`
surprising"* — ✅ **CONFIRMED BY MEASUREMENT** (§5.3). The surprise was real; the
explanation is bookkeeping.

### 5.3 What the truncation actually does on this box — measured

`.temp/php34/probe/addr_recon.c`, built with `harness/build.py`'s own flags
(`-std=c99 -Wall -Wextra -O3 -DSLB_ISOLATED`), over 40 process launches with
ASLR on:

```
php_shim_emalloc(17) samples                 : 40
that FIT in 32 bits (truncation lossless)    :  0        <- ZERO
bit 31 of the low word set / clear           : 21 / 19   <- both sign-extension regimes occur
min / max                                    : 0x5555f42532c8 / 0x56512f1442c8
real_size(17)=24  cache_index=3 (<11)        : the block is CACHED, never returned to malloc
```

⚠ **Both sign-extension regimes fault, for different reasons**, and the row
should say which it is showing:
* bit 31 **clear** → `(char*)(int)p` is a **low** address in `[0, 2^31)` — nothing
  is mapped there in a PIE process whose heap is at `0x55xx…`;
* bit 31 **set** → sign-extends to `0xFFFFFFFF_xxxxxxxx`, i.e. **kernel space**.

### 5.4 ⚠⚠⚠ The finding that decides the row's design: the defect is NOT input-conditioned

`.temp/php34/probe/htmlent_probe.c` — the four decode functions transcribed
verbatim, **R1 vs R1h × 4 placements × 4 inputs, forked so a SIGSEGV is a
reported outcome, every cell carrying a declared expectation**. `logs/06`,
`logs/07` (gcc/clang × `-O0`/`-O3`, **8 of 8 PASS**), `logs/09`.

| placement | `(char*)(int)p` | BENIGN `"hello, world"` | `"&#20013;"` (CRASH-123's own) | `"&amp;"` | MIXED |
|---|---|---|---|---|---|
| **SHIM** — `php_shim_emalloc`, i.e. faithful | `0xffffffff fd1b22c8` | ⚠ **SEGV** *(in the DTOR)* | **SEGV** *(at `:183`)* | **SEGV** | **SEGV** |
| **LOW** — arena at `0x10000000` | **identity** | clean | clean | clean | clean |
| **HI31CLR** — arena at `0x110000000` | `0x10000000` | clean¹ | **SEGV** | **SEGV** | **SEGV** |
| **HI31SET** — arena at `0x180000000` | `0xffffffff80000000` | clean¹ | **SEGV** | **SEGV** | **SEGV** |

¹ clean **only because the arena's free is a no-op**, so nothing dereferences the
wild value. This is where **two of my declared expectations were WRONG and the
probe caught them** (`logs/05`, 2 MISMATCHes). The reason is now a comment in
`pl_free`, because the grid is unreadable without it.

**R1h is CLEAN in all 16 cells, at both `-O` levels, on both compilers.**

⭐ **Read the SHIM/BENIGN cell first, because it is what a build task would
otherwise discover at the gate.** With stage markers:

```
[SHIM / BENIGN]  stage: FED ok      <- no '&', so `buffer` is never dereferenced in _dec
                 stage: FLUSHED ok  <- status==0, so _dec_flush's loop does not run
                 -> SIGNAL 11       <- mbfl_filt_conv_html_dec_dtor  ==  :169's free
```

**`if (filter->cache) mbfl_free((void*)filter->cache)` runs on EVERY filter
destruction**, and the truncated value is non-zero, so **the wild free is
unconditional.** Under ASan (`logs/11-asan.log`) the benign cell is
`SEGV … READ`, frame #0 `php_shim_efree` at `emalloc_shim.h:414` — PHP's own
`_efree` reading the block header at `ptr − 24`.

Repeated 15× per input per rung (`logs/09-shim-determinism.log`):

```
R1  SHIM: 15/15 SEGV on BENIGN · 15/15 AMPNUM · 15/15 AMPNAME · 15/15 MIXED   (60/60)
R1h SHIM:  0/15          ·  0/15         ·  0/15          ·  0/15            ( 0/60)
```

> ⚠⚠ **THEREFORE: `ph45` CANNOT BE BUILT WITH THE ALLOCATOR LEFT WHERE `malloc`
> PUTS IT. There is no benign corpus in that configuration — the R1 rung dies in
> the dtor on every input, so stage 2's checksum agreement (*"the gate's only
> load-bearing correctness check"*, `check.py:2893`) can never be reached.**
> **The row must place its work buffer, and the placement is the row's straddle
> parameter** — the same role `REAL_SIZE`'s boundary plays in `ph29` and
> `FD_SETSIZE` in `ph16`. §6.3 says exactly what it must guarantee.

⭐ **The manager's §3 intuition — "`ph45` plausibly needs a forcing mechanism" —
is RIGHT, and points the OPPOSITE WAY from the way it was written.** The forcing
is not needed to make the fault happen; it is needed **to make the benign case
work**.

### 5.5 §A4 fidelity — and this one MATCHES, which is new

| build | result |
|---|---|
| corpus, `php-5.0.0-fullext` + ASan, `CRASH-123.php` | `SEGV on unknown address 0x14ba8`, **WRITE**, `#0 mbfl_filt_conv_html_dec … mbfilter_htmlent.c:183` |
| my probe, faithful shim + ASan, `"&#20013;"` | `SEGV on unknown address 0x68`, **WRITE**, `#0 mbfl_filt_conv_html_dec … :183`-equivalent |
| my probe, faithful shim + ASan, **benign** | `SEGV`, **READ**, `#0 php_shim_efree` ← `mbfl_filt_conv_html_dec_dtor`, i.e. `:169` |
| my probe, UBSan, LOW placement, both rungs, all four inputs | ✅ **SILENT** |

⭐ **Signal, access type, function and line all match the corpus's recorded
category.** `ph64` had to report a *different* signal from its corpus row; this
row does not. ⚠ The addresses differ only because ASan's allocator is not
glibc's — an artefact of the detector, not of the defect.

### 5.6 ⚠ F46 — which step is implementation-defined and which is undefined

The task file's §5.3 asks for precision here, so:

| step | status |
|---|---|
| `:161` `(int)ptr` | **implementation-defined** (C99 6.3.2.3p6). gcc and clang define it as truncation |
| `:178`/`:249` `(char*)i` | **implementation-defined** (6.3.2.3p5) — "might not point to an entity of the referenced type… might be a trap representation" |
| the ten **dereferences** | ⚠ **this is where the standard stops defining anything.** The pointer has no provenance in the abstract machine |
| `:169` `free(truncated)` | **undefined** — 7.20.3.2, the argument was not returned by an allocation function |

⭐ **The benign corpus stays on the defined side by construction, and it is
stronger than "no UB": in the LOW placement `(char*)(int)p == p` EXACTLY, so
gcc's implementation-defined conversion is the IDENTITY and the C the benign
corpus evaluates is ordinary.** Measured: `logs/13-placement.log` shows every
`MAP_32BIT` result lossless, and `logs/12-ubsan.log` shows UBSan silent on both
rungs over all four inputs in that placement.

---

## §6 THE BUILD BRIEF

### 6.1 `provenance` — every `extract_sha256` computed (`.temp/php34/spans.sh`)

Canonical recipe, `SOURCES.md` §2: `tar -xzOf <tarball> php-5.0.0/<path> | sed -n 'a,bp'`.
All eight files verified present in `patterns-php/php-5.0.0.manifest`.

**PRIMARY — the DEFECT site** (`.memory-php/01-extraction.md`: `c_file`/`c_lines`
name the **defect** site; F1's *"the cited line is the faulting frame"* applies —
the CSV's `c_file_line` is `:161`, the *store*, and the defect is the *field*):

| field | value |
|---|---|
| `c_file` | `ext/mbstring/libmbfl/filters/mbfilter_htmlent.c` |
| `c_lines` | `[155, 258]` |
| `extract_cmd` | `tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/filters/mbfilter_htmlent.c \| sed -n '155,258p'` |
| `extract_sha256` | `6aad722d2b6cf73ec987a7ced3bf590ac04821454eb52377edfcdf1c7acaf8b9` |

⚠ **Cite the whole decode half `[155,258]`, not `[158,172]`.** The row lifts all
four functions and both constants, `:249` is inside it and is one of the four
patched sites, and a `[161,161]` or `[49,49]` span would score ~0 on overlap.
⚠ **`mbfl_convert.h:49` is ONE LINE (12 bytes) and must NOT be a span on its
own** — cite `[40,54]` and name `:49` in the `why`.

**`extra_spans` — MUST cite**

| `c_file` | `c_lines` | L | `extract_sha256` | `why` |
|---|---|--:|---|---|
| `…/mbfl/mbfl_convert.h` | `[40, 54]` | 15 | `6586bd6948ccceaadfc63df7a1c4d5f123fdaeb3f7121cd9eddcff4a08fb3a0a` | **`struct _mbfl_convert_filter`, and `:49 int cache;` IS THE DEFECT.** ⭐ **R1h's other hunk lands HERE** — `e8901dc17087` adds `void *opaque;` after `:53`. Open item 25's lesson: cite the frame the fix goes in |
| `…/filters/html_entities.h` | `[33, 36]` | 4 | `3528826585f2667f5e7010b9c3a31380f243151bb70263e227a387e758f8ea01` | `mbfl_html_entity_entry` — `{char *name; int code;}`, what `:200-206` walks |
| `…/filters/html_entities.c` | `[37, 290]` | 254 | `734afebb8f33375d1de03bf47b9882ccc062315994ef328e5ff74cf1e4d66afb` | `mbfl_html_entity_list` — **251 entities + the NULL terminator**. Static data, not input; the named-entity arm at `:202` is dead without it |
| `…/mbfl/mbfl_allocators.h` | `[36, 54]` | 19 | `289b5ecc8a164bffb67de188503ec4b04bf289e4726505056fd043227ed04fa0` | ⭐ **`mbfl_malloc`/`mbfl_free` are `#define`s over a FUNCTION-POINTER TABLE** (`:48`, `:51`). This is the span that makes §6.3's placement a substitution rather than an invention |
| `ext/mbstring/mbstring.c` | `[240, 283]` | 44 | `dff1cfd53b12bf788c1c153305bbc988bc65da4ab231d827cee865be39e7c273` | `_php_mb_allocators` — `malloc`→`emalloc`, `free`→`efree`. **Why `emalloc_shim.h` is the right allocator** |
| `ext/mbstring/mbstring.c` | `[762, 765]` | 4 | `2c7752b17cbb4466cfe41ed307a43482325e6a722e580720e3d2ee6f9a8a0485` | `PHP_MINIT_FUNCTION(mbstring)`: `__mbfl_allocators = &_php_mb_allocators;` at **`:764`** — where the binding actually happens |

**`extra_spans` — SHOULD cite (only if the kernel lifts them)**

| `c_file` | `c_lines` | L | `extract_sha256` | what |
|---|---|--:|---|---|
| `…/mbfl/mbfl_convert.c` | `[216, 256]` | 41 | `b208a9247d05506b6610405031e79808d1d9a11404cd20b9e9dc10d7691e10ff` | `mbfl_convert_filter_new` — allocates the **filter struct itself** with `mbfl_malloc` and calls the ctor |
| `…/mbfl/mbfl_convert.c` | `[259, 266]` | 8 | `79461e635638b0aa94f5c87147b930ae3e1bd3d1c715fa994a05a12732881886` | `mbfl_convert_filter_delete` — calls the dtor, i.e. reaches `:169` |
| `…/mbfl/mbfilter.c` | `[243, 271]` | 29 | `7192691a09af5e1f54749e5933696e1c521c657386b9b2ea45a7e83ae1cedd7c` | ⭐ `mbfl_buffer_converter_feed` — the corpus's ASan **frame #1** (`:263`), and its body `while (n>0) { filter_function(*p++, filter); n--; }` **IS the driver loop** |
| `…/filters/mbfilter_htmlent.c` | `[85, 91]` | 7 | `de7bc3bc60a06877c07870aa273ac3f6677b50f6f63f73e728b9e7ee7e461998` | `vtbl_html_wchar` — the vtable wiring ctor/dtor/filter/flush together |
| `…/mbfl/mbfl_convert.c` | `[299, 317]` | 19 | `b710d7ed81ad1bbd8af2f4bf53885199f1629bdee458c43810e70740a034aa3c` | `mbfl_convert_filter_copy` — §4.3's second defect. **Cite only if the row prices it** |

⛔ **DO NOT cite or lift `mbfilter_htmlent.c:99-150`** (`a8a129162e74ab4a…`) — the
ENCODE half, which carries §2.2's **separate** stack OOB write at `:123`.

### 6.2 Tier — ⚠ **`narrowed`**, and the argument, with the counter-argument

`CATALOGUE.md:139`/`:591` say `verbatim`. `ph64`'s was corrected `verbatim →
narrowed` during its build and I am proposing the same correction, for a
**different** reason — so **this is a judgement call and I want it attacked.**

**For `verbatim`:** the four functions at `[155,258]` lift **character for
character**. The entity table lifts as data. Nothing is deleted from any body.
`mbfl_malloc`/`mbfl_free` are already macros upstream, so redirecting them is
`ph03`'s libm case (§A1's admitted substitution), not a rewrite.

**For `narrowed` — and this is what I recommend:**

1. ⚠⚠ **§A1 clause (a) requires a `why` that ends in *"no semantics"*, and the
   allocator substitution's CANNOT.** The row does not merely redirect
   `mbfl_malloc` at a different implementation; it redirects it at one whose
   **returned address** it chooses, **and the returned address is the entire
   mechanism** (§5.3/§5.4). Declaring `verbatim` would require asserting that
   the substitution has no semantics, which is **false and is the row's central
   finding**. `_031` hit the identical shape (`php_error_docref` on R1h's
   refusal path) and reached `narrowed` too.
2. A **wrapper comes off**: `mbfl_buffer_converter_feed`'s memory-device and
   `mbfl_convert_filter_new`'s vtable dispatch become the driver loop and a
   direct ctor call. That is §A1's definition of `narrowed` verbatim — *"a
   wrapper comes off … the body is unchanged"*.

⚠ **A tier is a COST, never a filter.** `narrowed` costs a 25 % overlap
expectation instead of 50 % (reported, not enforced since `TASK_PHP_008` §2).
⭐ **With the entity table in the union, the overlap number will be HIGH and
partly meaningless** — 254 of ~477 cited lines are a data table that the kernel
lifts byte-for-byte. **§F9 requires the builder to read that number and say what
they think of it; say exactly this.**

**`divergences` the row owes, at minimum** (one entry each, §A2):

| what | kind | where | note |
|---|---|---|---|
| ⚠⚠ **`mbfl_malloc`/`mbfl_free` → a PLACED arena for the 17-byte work buffer** | **`projection`** | `mbfl_allocators.h:48,51`; `mbfilter_htmlent.c:161,169` | ⚠⚠⚠ **THE ROW'S MOST IMPORTANT DIVERGENCE, AND ITS `why` CANNOT END IN "NO SEMANTICS".** Upstream the target is a table entry PHP rebinds at `mbstring.c:764`; the row rebinds it again, at an address it chooses. **Say why: with glibc's address the R1 rung faults on every input and the row cannot be measured at all (§5.4).** |
| the other five `mbfl_*` table entries | `deletion` | `mbfl_allocators.h:36-44` | `realloc`/`calloc`/`pmalloc`/`prealloc`/`pfree` are unreachable from the decode path. No semantics |
| the six unused `mbfl_convert_filter` members | `deletion` | `mbfl_convert.h:41-46,50-53` | the vtable pointers and `from`/`to` — only if the row reduces the struct. ⭐ **Cheaper not to: lift all 13 members and forward-declare `mbfl_encoding`, and this entry disappears** |
| `mbfl_convert_filter_new`'s vtable dispatch | `deletion` | `mbfl_convert.c:250-253` | the kernel is compiled for ONE conversion, `HTML-ENTITIES → wchar`, whose vtbl is the compile-time constant `vtbl_html_wchar` (`mbfilter_htmlent.c:85-91`). No semantics |
| `mbfl_buffer_converter_feed`'s memory device | `projection` | `mbfilter.c:254` | `mbfl_memory_device_realloc` replaced by the fold. The `output_function` is `mbfl_filter_output_pipe` upstream; the kernel's folds into the `u64` |
| the three commented-out `php_error_docref` calls | *(none owed)* | `:197,:212,:217,:231` | ⓘ **they are ALREADY comments in 5.0.0** — nothing to delete. Worth a line in `NOTES.md` so a reviewer does not go looking |

### 6.3 ⭐⭐ THE PLACEMENT — what it must guarantee, measured

This is the thing a build task will otherwise stall on. **Measured under all
four `harness/build.py` flag combinations** (`-std=c99 -Wall -Wextra
{-O0|-O3} {-DSLB_ISOLATED|-flto}`), `.temp/php34/logs/13-placement.log`:

```
#define _GNU_SOURCE            /* -std=c99 sets __STRICT_ANSI__, which hides both flags */
LO = mmap(NULL, n, …, MAP_PRIVATE|MAP_ANONYMOUS|MAP_32BIT, -1, 0)
        -> always in [0x40000000, 0x42000000) : bit 31 CLEAR, `(int)p` is the IDENTITY
HI = mmap(LO + (1ULL<<32), n, …, MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE, -1, 0)
        -> (int)HI == (int)LO  : the truncation maps HI onto LO EXACTLY
```

**Four requirements, and each is load-bearing:**

1. **The BENIGN corpus must allocate from `LO`.** Then `(char*)(int)p == p`
   exactly, R1 and R1h are **bit-identical** (measured: all four inputs, folds
   `13809678534597872799` / `05752608758558424950` / `05752608758558404975` /
   `13129849808939318271` on both rungs), stage 2's checksum agreement is
   reachable, UBSan is silent, and no UB is evaluated (§5.6).
   ⭐ **This is not a convenience: it is 2004's 64-bit Linux.** A non-PIE
   `php` binary's `brk` heap sat below 2³², `(int)p` was lossless, and that is
   why the defect shipped and was reported as *a compiler warning*.
2. **The ADVERSARIAL inputs must allocate from `HI`.** `HI` alone (no `LO`
   mapped) gives the corpus's own signal: SEGV, WRITE, at `:183`.
   `HI` **with `LO` also mapped and live** gives §6.4's non-fatal oracle.
3. **The `mmap` must happen ONCE, outside the measured region.** The bump
   pointer resets per kernel call (beside `php_shim_reset()`, §B1.3); the
   mapping does not. A per-call `mmap` would put a syscall in the marginal-`Ir`
   subtraction.
4. **The FILTER STRUCT should still come from `php_shim_emalloc`** — upstream
   `mbfl_convert_filter_new` really does `mbfl_malloc(sizeof(mbfl_convert_filter))`,
   and that allocation is faithful and harmless. So `uses_allocator: true`, with
   the work buffer's placement as the single itemised projection.

⚠ **Two alternatives, both measured and both rejected, so nobody re-tries them:**
* **edit `emalloc_shim.h` to take its backing from a placed arena** — it would
  be more faithful, and it **stales every php row** (`PROTOCOL_PHP.md` §B2: the
  shim is in every row's gate *and* measurement digest). ⛔
* **build `-no-pie` so the ordinary heap sits below 2³²** — `harness/build.py`
  is frozen and passes no such flag. ⛔

### 6.4 ⭐⭐ THE ORACLE — measured, and the catalogue's proposal measures NOTHING

The catalogue proposes `u64 = decoded bytes + (allocs, frees)`.
**Measured (`logs/06-oracle-probe-v2.log`), in the LOW placement:**

```
              R1 fold                 R1h fold                alloc/free
BENIGN        13809678534597872799    13809678534597872799    1/1   1/1
"&#20013;"    05752608758558424950    05752608758558424950    1/1   1/1
"&amp;"       05752608758558404975    05752608758558404975    1/1   1/1
MIXED         13129849808939318271    13129849808939318271    1/1   1/1
```

⚠⚠ **Every column is identical. `ph64`'s catalogue oracle measured nothing and
so does this one** — and here that is **correct behaviour, not a defect**: it is
`check.py` stage 7h's exact requirement (*"R1h must not change benign output"*)
being satisfied. **But it means the measured `u64` carries NO evidence that the
defect exists.** That evidence has to come from somewhere, and there are two
places:

**Oracle 1 — `controls/`, FATAL, and it matches the corpus exactly.** Allocate
from `HI` with nothing at the image. R1 SEGVs at `:183` (WRITE) on any input
containing `&`, and in the dtor on any input at all; R1h is clean. 60/60 vs
0/60. ⚠ **A row cannot MEASURE a faulting cell**, so this belongs in
`controls/` — except as a declared `adversarial-*.bin`, where `check.py` stage 4
**records** per-rung behaviour rather than requiring agreement (`check.py:4102`).

**Oracle 2 — ⭐⭐ MEASURABLE, NON-FATAL, DETERMINISTIC, AND IT IS THE REAL HARM.**
`.temp/php34/probe/alias_probe.c`. Two live filters whose buffers are exactly
2³² apart, so the truncation makes them **alias**:

```
bufA = 0x0000000010000000   bufB = 0x0000000110000000   (int)bufA == (int)bufB
input: A gets "x&amp;y" with B's "&#65;" interleaved after A's "&a"

R1h  emitted [120, 65, 38, 121]    bufA = "&amp"   bufB = "&#65"   fold 06990488587375112783
R1   emitted [120, 65, 674, 121]   bufA = "&#mp"   bufB = (untouched, zeros)
                                                                   fold 06990488588011114691
```

⭐ **The mechanism, exactly** — and `PROTOCOL.md` rule 12 wants the mechanism,
not the number. Under R1 both filters write through the same 17 bytes. B
overwrites A's `&a` with `&#`, so when A's `m`, `p`, `;` arrive the buffer reads
`&#mp`; `:190`'s `buffer[1]=='#'` selects the **numeric** arm, and `:193`
computes `('m'-'0')*10 + ('p'-'0')` = `61*10 + 64` = **674**. **`&amp;` decodes
to U+02A2 instead of `&`.** No crash, no sanitizer diagnostic, no allocator
damage — a silent wrong answer, which is what a wild write into another live
allocation actually costs.

⚠ **The must-NOT-fire control the row owes beside it** (`_031` §6.4's S4 in a
different dress): **the same two filters, the same interleaving, both buffers in
`LO` so they do not alias** — `fold`, `emitted` and both buffers must be
identical between R1 and R1h. Without it the divergence could be the
interleaving rather than the aliasing, and nothing in the number says which.

**Recommendation:** ship **both**. Oracle 2 in the measured `u64` (`fold` of the
emitted wchars `⊕ php_shim_tally()` `⊕` the filter count), Oracle 1 as
`inputs/adversarial-*.bin` plus `controls/`.

### 6.5 §A2a — the two rules, instantiated

**Rule 1 — the fixture must reach every arm of the branch the defect lives on,
and `inputs/gen.py` must ASSERT it.** `mbfl_filt_conv_html_dec` is a state
machine with **six** reachable arms, and a corpus of `&#NNN;` alone (which is
all `CRASH-123.php` has) takes **two** of them:

| arm | line | reached by |
|---|---|---|
| pass-through, `!status && c != '&'` | `:185` | any ordinary byte |
| entity start | `:183` | `&` |
| **numeric** `buffer[1]=='#'` | `:190-196` | `&#20013;` |
| **named HIT** | `:200-211` | `&amp;` |
| **named MISS → flush** | `:213-219` | `&nosuchthing;` |
| **illegal char / buffer-full / `&`-restart** | `:221-239` | `&ab cd`, a >15-char name, `&&` |

⚠ **`:225`'s `filter->status+1 == html_enc_buffer_size` arm is the one a casual
corpus misses**, and it is the arm that bounds the 17-byte buffer. `gen.py` must
re-derive from what it emitted that all six are reached, in the shape of
`ph03`'s `_check_span`.

**Rule 2 — `model.py::selfcheck` must sweep a domain it constructs.** The probe's
4 × 4 grid is the shape; the model's should be larger — every entity name length
`1..20`, every numeric value `0..65535` at a sample, both placements, with the
must-NOT-fire controls in the same table. Milliseconds, no `.bin`.

### 6.6 Size — measure the EXTRACTION, not the mechanism

`.temp/php34/logs/16-extraction-size.log`:

| | raw lines | code lines |
|---|--:|--:|
| `mbfl_convert.h:40-54` (the struct) | 15 | 15 |
| `mbfilter_htmlent.c:155-258` (all four functions + 2 constants) | 104 | 85 |
| `mbfilter_htmlent.c:94` (the `CK` macro) | 1 | 1 |
| `html_entities.h:33-36` | 4 | 4 |
| **`html_entities.c:37-290` (the 251-entity table)** | **254** | **254** |
| `mbfl_allocators.h:36-54` | 19 | 17 |
| `mbfl_convert.c:216-266` (new/delete) | 51 | 40 |
| `mbfilter.c:243-271` (the feed loop) | 29 | 25 |
| **TOTAL** | **477** | **441** |
| **of which LOGIC (total − the table)** | **223** | **189** |

**Say both numbers**: the *mechanism* is **15** tarball lines (§2.1, not the
catalogue's five); the *extraction* is **477 raw / 441 code**, and **254 of
those are a data table.** ⭐ `ph64` was billed at 8 lines and measured ~140; this
one is billed at 5 and measures ~190 lines of logic plus a table. **The table is
the cheap part — it is `const` data with no control flow — so the real cost is
closer to `ph64`'s than the raw number suggests.**

### 6.7 R1h — exactly what to ship

`c/kernel_hardened.c` = `c/kernel.c` **plus `e8901dc17087` and nothing else**:

```c
/* struct _mbfl_convert_filter, mbfl_convert.h -- KEEP `int cache;`, ADD: */
    void *opaque;                                    /* + e8901dc17087 */

    filter->opaque = mbfl_malloc(html_enc_buffer_size+1);   /* was :161's (int) cast */
    if (filter->opaque) { mbfl_free((void*)filter->opaque); }
    filter->opaque = NULL;                                  /* was :169, :171 */
    char *buffer = (char*)filter->opaque;                   /* was :178 */
    buffer       = (char*)filter->opaque;                   /* was :249 */
```

`spec.md`'s hashed block records: `fix_commit: "e8901dc17087"`, the author and
date, the tag window **php-5.0.3 → php-5.0.4**, that the patch applies to the
pristine tarball with `patch -p1` **rc=0, no fuzz and no offset**, that the
result is byte-identical to php-5.0.4's `mbfl_convert.h` and differs from
php-5.0.4's `mbfilter_htmlent.c` by **one unrelated line in the ENCODE
function** (§4.4), that the repair **survives into `master` unreverted**, and
⚠ **that the commit's SUBJECT calls it a compiler-warning fix while the patch
changes the STORAGE — so the subject is not evidence about what it does.**

**Two things for `controls/`, not `spec.md`:**
* `controls/e8901dc17087.patch` — the 74 patch bytes, the way `ph07` keeps
  `cb3cca21b345.patch`, so the citation survives without network.
* ⭐ `controls/warnings.py` — **the row can measure bug #30573 itself.** Under
  `harness/build.py`'s own `-Wall -Wextra`, R1 emits exactly **two** diagnostic
  classes and R1h emits none:
  `-Wpointer-to-int-cast` at `:161` and `-Wint-to-pointer-cast` at `:169`,
  `:178`, `:249` — **four warnings, and they are the four sites the patch
  rewrites.** ⚠ `check.py` does not test warnings (`check_build` fails only on a
  non-zero compiler exit), so this is a control, not a gate stage. **It is also
  the cleanest possible statement of what the row is about: the compiler said
  so, in 2005, and the fix's subject line is that warning.**

### 6.8 ⚠ The ladder — a RESULT to report, not an admission question

**CLAUDE.md rule 6: admission is decided SOLELY on the C program**, and the C
program clears the bar — it is correct on benign inputs *in the regime the row
measures*, it exhibits CWE-787 on an adversarial one, and its C mechanism
(a pointer round-tripped through a narrower type) is shared with **no** built or
catalogued row. **Everything below is a prediction for the build task and
several parts are unmeasured; none of it bears on admission.**

* **R2/R3 (safe Rust) — structurally immune, and this is the row's headline.**
  Safe Rust **cannot store a pointer in an `i32` at all**: there is no pointer
  to store and no `as` cast from a reference to an integer. The faithful safe
  model is an **index into an owned `Vec<u8>`**, and an index round-trips through
  `i32` losslessly for any arena this row can build. Measured, trivially
  (`logs/18-rustcheck.log`): `0 -> 0i32 -> 0`, lossless. **So R2/R3 agree with
  R1h on every input, by typing, with no check and no cost** — which is a much
  stronger statement than any of the four built rows can make.
* **R4 (unsafe Rust) — CAN reproduce it exactly, and `rustc` says NOTHING.**
  Measured: `let t: i32 = p as i32; let b = t as *mut u8;` compiles with
  **zero diagnostics at default lint levels**, and truncates:
  `0x55fb4689dd60 -> 0x4689dd60 -> lossless=false`. ⭐ **gcc emits two warnings
  for the same C and rustc emits none** — worth reporting, because the usual
  story is the other way round. ⚠ Per `.memory-php/02-ladder.md`, **R4 is not a
  port of R1**: it should carry the memory-safe spelling (keep the `*mut u8`),
  and the truncation should appear only in R1.
* **R5 (Verus) — ⚠ predict a VACUITY problem and budget for it.** The
  obligation to state is `pointer-value-integrity/O1+O2`, and Verus's raw-pointer
  API carries provenance, so *"the value read back designates the same
  allocation"* may be **true by typing and therefore unstateable**. `ph07`
  measured its own vacuity by replacing the kernel body with `0u64`
  (`.memory-php/02-ladder.md`); **this row owes the same measurement**, and the
  answer — whichever way it goes — is the type axis's first real result.

### 6.9 Mechanical items a build task will otherwise trip on

* `ln -s ../../../common-php/emalloc_shim.h patterns-php/ph45-*/c/emalloc_shim.h`
  — **unconditional** (§B2), and this row **does** allocate, so
  `uses_allocator: true` with §6.3(4)'s reason.
* `php_shim_reset()` **and** the arena bump-pointer reset at the top of every
  kernel call (§B1.3); the `mmap` itself exactly once (§6.3(3)).
* `#define _GNU_SOURCE` at the top of `c/kernel.c` — `-std=c99` hides
  `MAP_32BIT` and `MAP_FIXED_NOREPLACE`. **Verified under all four flag
  combinations** (`logs/13`).
* Only `c/`, `inputs/`, `controls/` (§B3a / `ROW_DIRS`). Five cited tarball
  files → **flatten** (`c/htmlent__html_entities.h`) or flat-symlink beside;
  never `<row>/extract/`.
* `model.py` must set `sanitizer_expect` to `"clean"` on `small.bin`/`large.bin`
  (the LOW placement is clean under both ASan and UBSan — measured) and
  `"fires"` on the adversarial ones.
* Six commands, in order, ~28 min (§E); the first gate **must** fail on tables.
* `idiom.why`'s mandatory 11 003-byte named-spelling tail, and
  `contract_sha256` via `check.py::read_contract`'s regex (keeps the newline
  before the closing fence).
* `echoes: ["p38"]` per the catalogue — **not re-derived in this task.**

---

## §7 ⚠ Where the task file is wrong

### 7.1 ⚠⚠ §2's *"Five lines … That is the whole mechanism"* — wrong, and it would have under-specified the row

The five cited lines miss **`:249`, the second cast back**, which is one of the
four sites `e8901dc17087` rewrites, and they miss **nine of the ten
dereferences**. §2.1 has the enumeration. ⚠ **A row built to the five would not
lift `_dec_flush`, and would therefore not be a faithful pre-image for its own
R1h.** The catalogue's Part B block repeats the same five and inherits the same
gap. (The catalogue's *"two functions"* is also short by one — it is
ctor, dtor, `_dec` **and** `_dec_flush`.)

### 7.2 ⚠⚠⚠ §3's premise — *"the trigger depends on where the allocator happens to put the block"* — is wrong in BOTH directions

It is **not** a matter of happenstance: measured 40/40, **every** `emalloc(17)`
on this box exceeds 2³², and **60/60** R1 runs SEGV. And it is **not** a
*trigger* condition at all: §5.4 shows the wild free at `:169` fires on an input
with no `&` in it. ⭐ **The correct statement is the opposite one: the defect is
unconditional and it is the BENIGN case that needs forcing.**

The sub-clause *"the sign-extension back through `(char*)` only goes wild when
bit 31 is set"* is also wrong: **both** regimes go wild, for different reasons
(§5.3), and both were measured faulting.

### 7.3 ⚠ §2's *"the subject calls it a COMPILER-WARNING fix"* — the warning is REAL and is the defect

The manager's counter-evidence (*"it touches BOTH cited files"*) is right and
the conclusion holds. But there is a sharper reading available: **the compiler
warning and the memory-safety defect are the same event.** `-Wall -Wextra`
reports `-Wpointer-to-int-cast` and `-Wint-to-pointer-cast` at exactly the four
sites the patch rewrites (§6.7). Bug #30573 was filed about the warning; fixing
the warning **properly** — by giving the pointer a pointer-typed home — removes
the defect as a consequence. **There is no "compiler-warning fix vs real fix"
distinction to draw here.**

### 7.4 ⚠ §1's *"it sidesteps F24's shared-`zval.h` prerequisite entirely"* — TRUE for the DEFECT file, INCOMPLETE for the ROW

`zval` occurrences in `mbfilter_htmlent.c`: **0**, confirmed. But the row's
allocator provenance runs through **`ext/mbstring/mbstring.c`**, and that file
is full of Zend machinery. ⚠ **The row does not need to LIFT any of it** — the
two spans it should cite (`[240,283]`, `[762,765]`) are `emalloc` wrappers and
one assignment, all zval-free — **so the conclusion stands and only the
justification needs widening.** Checked deliberately, because "no Zend header in
the defect file" and "no Zend anywhere in the row" are different claims.

### 7.5 ✅ What held, exactly as written

* **Every line of §2's tarball read** — `mbfl_convert.h:49`, `:161`, `:169`,
  `:178`, `:183`, re-derived byte-exactly.
* **Every field of §2's `index.csv` table** — `memory-corruption`, `pure-ext`,
  `CWE-787`, `wild-pointer-deref`, `e8901dc17087`, `historical-known`, empty
  `merged_members`, `confidence: high`, `crashes_pristine_5_0_0: False`. ⓘ One
  wrinkle worth a line: `paper/invariants-166.json` records CRASH-123 at
  `confidence: "medium"` where `index.csv` says `high`. Noted, not pursued.
* **§2's include list** — `config.h`, `string.h`, `strings.h`, `mbfilter.h`,
  `mbfilter_htmlent.h`, `html_entities.h`; no Zend header. Confirmed.
* **§2's fix-survey row** — sha, author, date, subject, 2 files. Confirmed
  against the patch bytes.
* **§5.1's off-by-one warning** — confirmed: `ADJUDICATION_001.md` §0 and §1b
  both give `:177` and `:181`; the tarball says `:178` and `:183`; the
  CATALOGUE's `risk` line and the CSV are both **right**. **Use `:178`/`:183`.**
* **§5.2's catalogue claim** — *"the only row in 166 with its own invariant"* is
  **TRUE**, and §4.5 attributes it to `paper/invariants-166.json` with the count
  (20 distinct ids, 1 non-`I<n>`, on CRASH-123 alone) so it need never be
  repeated on trust again.
* **§5.5** — `mbfl_malloc` established: a macro over a function-pointer table,
  rebound to `emalloc` at `mbstring.c:764`.
* **§5.6** — `html_enc_buffer_size` is `16` (`mbfilter_htmlent.c:155`), so the
  request is **17 bytes** → `real_size` 24 → `cache_index` 3 < 11 → **the block
  is cached and never returned to `malloc`**.
* **§1's cheapness claim** — `ph45` is `CANDIDATE` in the manager's own
  pre-image screen (1/2 cited lines in the pre-image, and the missing one is
  `:183`, which the patch does not touch), so **it is NOT in `_031` §7.1's
  17-row false-exclusion class** and nothing there needs re-deciding for it.

---

## §8 What I did NOT do, and what I am unsure of

1. ⚠ **I wrote nothing to `.memory-php/` or `RECAP_PHP.md`** (manager-only).
   §5.1's boxed note — that §B1.1's *conclusion* is right while its *mechanism*
   does not explain the 15 `fullext` rows — is exactly `PROTOCOL.md` rule 9's
   conclusion/mechanism split and is offered as a candidate, not landed.
2. ⚠⚠ **I did not build PHP and did not run any reproducer.** `CRASH-123.php`,
   `V5C-123.json`, the two validation logs and the rust-eval row are **read and
   quoted**; none was executed. The corpus's `n_fault: 3/3` is **its** measurement,
   not mine. **Mine is the transcribed-C probe**, and the two agree on signal,
   access type, function and line.
3. ⚠⚠ **§6.3's placement design is MINE and is unreviewed.** I measured that it
   works (`logs/13`), that it makes R1 ≡ R1h benign (`logs/06`), and that the
   two alternatives are blocked. **I did not build a row with it**, and whether
   a placed arena is an acceptable `projection` under §A2 is a **manager
   call** — the rule says a divergence that changes behaviour is a `modelled`
   tier, and I am arguing this one changes *which platform state* is evaluated
   rather than *what the code does*. ⚠ **If that argument is rejected, the row
   is `modelled`, and it is still a row** — a tier is a cost, never a filter.
4. ⚠ **I did not measure §4.3.** That `mbfl_convert_filter_copy` aliases the
   work buffer pre-fix, and that `mbfl_strimwidth` can carry an HTML-ENTITIES
   decoder into it, are **read at source**. The double free is an inference
   (conclusion landed, mechanism OPEN).
5. ⚠ **I did not identify the commit for §2.2's ENCODE-side `tmp + sizeof(tmp)`
   bug**, only that it is in the php-5.0.3 → php-5.0.4 window and is not in
   `e8901dc17087`. **Nobody should act on it without doing so.**
6. ⚠ **I did not test the Rust or Verus rungs.** §6.8 is a prediction with one
   30-second measurement behind its R4 half. The R5 vacuity call in particular
   is a guess.
7. ⚠ **I ran no `gate.py`, no `check.py`, no measurement, and neither staleness
   bracket**, per the task file (`TASK_PHP_033` is mid-re-gate).
   `git status --porcelain` **during** the task (mid-way, before this report
   existed) — every line `TASK_PHP_033`'s, none mine:

   ```
    M patterns-php/ph29-recvfrom-alloc/spec.md
    M results-php/gate/ph29-recvfrom-alloc.json
    M results-php/preflight/ph29-recvfrom-alloc.preflight.json
    M results-php/tables/ph29-recvfrom-alloc.md
   ?? .tasks-php/TASK_PHP_033_REPORT.md
   ```

   and **after writing this report** — the manager committed `_033`'s work in
   between, so the tree is now clean apart from this one file:

   ```
   ?? .tasks-php/TASK_PHP_034_REPORT.md
   ```

   ⓘ `.temp/` is gitignored, so `.temp/php34/` does not appear. ⭐ **Exactly one
   line is mine, and it is this report.** I touched nothing under `patterns-php/`,
   `harness/`, `common/`, `patterns/`, `results/`, `results-php/`, `pilot/`,
   `.web/`, `RECAP_PHP.md`, `.memory-php/` or `CATALOGUE.md`. No `git add`, no
   `git commit`. I did **not** read `patterns-php/ph29-*`.
8. ⚠ **Two of my own declared expectations were wrong and the probe caught
   both** (`logs/05-oracle-probe.log`, kept on purpose). Both were the same
   error — I declared CRASH for an arena placement's benign cell, forgetting
   that the arena's `free` is a no-op so nothing dereferences the wild value.
   ⭐ **Neither would have been visible from the output alone**; the
   expectations, and only the expectations, are what caught them.
9. ⚠ **The probe's own CRASH/CLEAN verdict is wrong under ASan**, harmlessly:
   ASan `_exit(1)`s rather than re-raising, so `WIFSIGNALED` is false and the
   cell prints MISMATCH. `ASAN_OPTIONS=abort_on_error=1` restores it. **The ASan
   report is the evidence, not the verdict line.**
10. ⚠ **I did not verify the release DATES of php-5.0.3 and php-5.0.4**, only
    the tag ordering and the commit's own date. The window claim rests on the
    tag contents, which I fetched and hashed.
11. ⚠ `clang` is not on `PATH`; the sweep used `harness/build.py:53`'s
    `~/tools/llvm/bin/clang`. All 8 cells PASS.

---

## §9 Evidence index — everything under `.temp/php34/`

| path | what |
|---|---|
| `NOTES.md` | how to regenerate every byte; the two times an expectation caught me |
| `fetch.sh` | 16 tags × 3 libmbfl paths |
| `spans.sh` + `logs/14-spans.log` | **every candidate span's canonical `extract_sha256`** — §6.1's tables |
| `fnbody.py` + `logs/02` | brace-matching function extractor, **16 cases, 6 must-NOT-fire**, `--selftest` PASS |
| `logs/01-pristine-field.log` | **§5.1**: `crashes_pristine == stock-run.hard_crash` 142/142; all 15 `fullext` rows at `rc 255` |
| `logs/03-tagbracket.log` | §3's tag bracket, 16 tags, function bodies hashed |
| `logs/04-addr-recon.log` | where `php_shim_emalloc(17)` lands, 3 runs |
| `logs/05-oracle-probe.log` | ⭐ **the two WRONG expectations, kept on purpose** |
| `logs/06-oracle-probe-v2.log` | **the oracle**: 4 placements × 4 inputs × 2 rungs, 0 mismatches, with stage markers |
| `logs/07-sweep.log` | the same probe over gcc/clang × `-O0`/`-O3` × R1/R1h — **8/8 PASS** |
| `logs/08`, `logs/09` | 40 address samples (0/40 lossless, 21/19 bit-31 split); **60/60 vs 0/60 SEGV** |
| `logs/10-alias-probe.log` | ⭐⭐ **the non-fatal oracle**: `&amp;` → **674** vs **38** |
| `logs/11-asan.log` | §5.5's fidelity: SEGV/WRITE at `:183`, and SEGV/READ in `_efree` on the benign input |
| `logs/12-ubsan.log` | UBSan **silent** on the LOW placement, both rungs, all four inputs |
| `logs/13-placement.log` | `MAP_32BIT` / `MAP_FIXED_NOREPLACE` under all four `build.py` flag combinations |
| `logs/15-invariant-claim.log` | §4.5: 20 distinct invariant ids over 166 cases, **1 non-`I<n>`**, and its three obligations |
| `logs/16-extraction-size.log` | §6.6's size table |
| `logs/17-preimage-ph45.log` | the manager's pre-image screen record for `ph45` — `CANDIDATE`, not an exclusion |
| `logs/18-rustcheck.log` | §6.8: `p as i32` truncates and `rustc` emits **zero** diagnostics |
| `patches/e8901dc17087.patch` | the fix, 74 lines |
| `applytest/a/` | the backport: `patch -p1` **rc=0, no fuzz, no offset** |
| `tags/` | 16 tags × `mbfl_convert.{h,c}`, `mbfilter_htmlent.c` |
| `src/` | the 8 tarball files, `SOURCES.md` §2 recipe |
| `probe/*.c`, `probe/*.rs`, `probe/sweep.sh`, `probe/entity_table.inc` | the probes and the generator for every log above |

⚠ Per `CLAUDE.md` rule 1 every binary, `__pycache__/` and the 37 MB `full/`
tarball extraction is deleted; `fetch.sh`, `spans.sh`, `probe/sweep.sh`, the
build lines in `NOTES.md` and the `tar`/`sed` recipe re-derive all of it.
**832 KB remain, all of it evidence or generator.**
