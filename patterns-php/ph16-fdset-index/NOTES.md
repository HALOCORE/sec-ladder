# ph16-fdset-index — notes

`FD_SET(this_fd, fds)` with `this_fd` an `int` nothing bounds and `fds` an
`fd_set` in the **caller's** frame. `ext/standard/streamsfuncs.c:541`,
PHP 5.0.0, corpus row CRASH-098, tier `narrowed`.

---

## §0 `PROTOCOL.md` rule 6 — the `contract_sha256` disclosure

**As first written, before any cell was built:**
`a0629b5ecec20695ec1a111da29fc91334760b5435899da8e2b62dd68aaff865`

**As shipped:** `8d4d4948065b3152bc1a324d760a427106c96f63707745d2b4d1bdda25ccfe05`
— and the gate record is the authority. ⚠ **The block MOVED FIVE TIMES and
every move is disclosed here rather than quietly absorbed:**

| # | what moved | why |
|---|---|---|
| 1 | `idiom.forbidden[1]` and `[2]`, and `verus.unsafe_justifications` gained `aget_unchecked` | **the gate refused the first version.** `[idiom-forbidden]` fired **14** times because my forbidden entries quoted `sizeof(fd_set)`, `wfds` and `efds` **in their own explanatory prose**, and in a `forbidden` entry *every* backticked span becomes a banned token. That is `check.py`'s documented false-positive shape — *"an entry that backticks its REPLACEMENT"* — firing on a row for the first time. The backticks came off the prose; the banned spellings are unchanged. `[tcb-unsafe]` demanded the missing justification. |
| 2 | the `7.01 Ir per FD_SET` figure, in three places; and `identity[0].why`'s `426` / `533 vs 501` | **measurements falsified them.** 7.01 came from a standalone probe (`.temp/php25/fortify_probe.c`); the row's own `controls/fortify.py` measures **14.87** on `small.bin`. `426` / `533` / `501` were instruction counts from a hand build with different flags; the shipped record says **425** and **527 vs 488**. Corrected in `spec.md`'s prose, in `idiom.why`, in the `_FORTIFY_SOURCE` divergence entry, in `identity[0].why` and in `c/kernel.h`. `PROTOCOL.md` rule 6's addendum, on the first row that has had to apply it: *a frozen declaration is evidence about when it was written, not about whether it is still true.* |
| 3 | `idiom.required[2]`, `[3]` and `[5]` became **per-language** and lost the backticks on their explanatory quotes | **the gate's own audit reported them as `pins_nothing`** — 18 (spelling × language) pairs, which `check.py` calls *"the class that carries real defects"*. The three entries each said *"NO BACKTICKED SPELLING, deliberately"* **and then backticked five to seven things**, none of which any rung spells. What is pinned now: `fd_set rfds, wfds, efds;` (c) / `[u64; NW]` (rust); `PHP_SAFE_FD_SET`'s POSIX body (c only, scoped-absent from `c/kernel.c` by design); and the guard pair (rust only, each scoped-absent from the rungs that carry the other). ⚠ **No banned or required *property* changed — only which token each entry pins**, and the direction is NARROWER, not wider. |
| 4 | four more backticks, in the text move 3 added | **the same mistake one level down, and the audit caught it again.** The note I wrote to explain move 3 cited `check.py`'s `pins_nothing` class **by name in backticks**, which made it a pinned spelling; and the note appended to `required[5]` quoted the two guard spellings in backticks and was appended to **both** language values, so the C side went on pinning two spellings no C rung can have. ⚠⚠ **That second one would have made move 3's own disclosure FALSE** — it says the guard pair is pinned "rust only" — and `PROTOCOL.md` rule 6 is explicit that a false disclosure is worse than the stale thing it describes. Stripped by `.temp/php25/fix_pins.py`; the audit went **18 → 4 → 0** row-specific `pins_nothing`. |
| 5 | `provenance.divergences_note`'s own count | **it said *"SEVEN of these thirteen entries are SUBSTITUTIONS"* and the block holds EIGHT of TWELVE.** Found by §12's re-read, not by any check — the hash matched because nobody had edited the sentence while the list it describes grew and shrank underneath it. ⚠ The count is not decorative: the sentence's argument is *"more substitutions than any row so far, and the reason is structural"*, so a reader is meant to weigh it. `.temp/php25/fix_divcount.py` recomputes both numbers from the block rather than hard-coding the repair. **It is the ONLY wrong numeral the sweep found** — §12 lists what else was checked. |

Both hashes were computed with the gate's own regex
(`` ```slb-contract\s*\n(.*?)``` ``, which keeps the newline before the closing
fence; `PROTOCOL_PHP.md` §E). ⚠ **The `git show HEAD:… | diff` command
`PROTOCOL.md` rule 6 offers is VACUOUS on a new pattern** and this row does not
cite it: a pattern lands in one commit, so on a clean tree that diff always
prints nothing and always looks like it passed. The hash above is the only
evidence, which is why it was written down before the first build.

**Every numeral in the hashed block was re-derived against the shipped
measurement record before this row was finished** — §12 is that pass.

---

## §1 The row

| | |
|---|---|
| defect site | `ext/standard/streamsfuncs.c:541`, `FD_SET(this_fd, fds);` inside `stream_array_to_fd_set` (`:518-548`) |
| the object | `fd_set rfds, wfds, efds;` at **`:658`**, in `PHP_FUNCTION(stream_select)` (`:653-718`) |
| the guard site | **there is none in 5.0.0.** `FD_SETSIZE` does not occur in either function |
| the repair site | `main/php_network.h` — a file 5.0.0 does not have the macros in; `99e290f882c9` adds them |
| CWE | CWE-787, out-of-bounds **write**. Exactly one limb; nothing here reads out of bounds |

⚠ **`TASK_PHP_025` §1 and `.temp/mgr166/NOTES.md` both place the `fd_set`
declaration at `:657` and call `TASK_PHP_020_REPORT.md:131`'s `:658` "off by one
and harmless". The correction is INVERTED — `:658` is right and `:657` is
`struct timeval *tv_p = NULL;`.** Measured against the pinned tarball:

```
$ grep -a -n 'fd_set.*rfds' streamsfuncs-5.0.0.c
658:	fd_set			rfds, wfds, efds;
```

`:541` is exact.

### §1a ⭐ The tier: `narrowed`, not the catalogue's `verbatim`

**Two tests, and they disagree.** Which one is applied decides this, so both are
named:

| test | applied to | verdict |
|---|---|---|
| `TASK_PHP_012` M4's — *is the defect site inside a `PHP_FUNCTION` / VM-handler / argument-parsing frame?* | `stream_array_to_fd_set` is a `static` helper | `verbatim` |
| `PLAN_PHP.md` §4.1 / `PROTOCOL_PHP.md` §A1's **definition** — *did a wrapper come off (zval unpacking, argument parsing), with the body unchanged?* | see below | **`narrowed`** |

**I applied the definition.** What the extraction removes is
`Z_TYPE_P(...) != IS_ARRAY`, the `zend_hash_internal_pointer_reset` /
`get_current_data` / `move_forward` triple, `php_stream_from_zval_no_verify` and
`php_stream_cast` — **zval unpacking, every one of them** — and what is left is
the body: `FD_SET(this_fd, fds); if (this_fd > *max_fd) { *max_fd = this_fd; }`,
unchanged. That is `narrowed`'s definition read out loud.

⚠ **The M4 test asks about the ENCLOSING FRAME and the definition asks about
WHAT CAME OFF, and this row is the case that separates them.** A `static` helper
can still be all wrapper. ⚠⚠ **`patterns-php/CATALOGUE.md` still says
`verbatim` for `ph16`** and this task was forbidden to edit it; the manager owns
that correction. `UPSTREAM_001.md` §6's table lists `ph16` as ✅ `verbatim` on
the M4 test and is right about the test.

⭐ **`modelled` was considered and refused.** `modelled` is *"the mechanism is
re-expressed because the original cannot be lifted"*, and the mechanism —
an index from outside used as a bit position — is **not** re-expressed:
`FD_SET(this_fd, fds)` is lifted with the platform macro intact, which is why
`controls/fortify.py` can measure what the toolchain does to it.

### §1b `PROTOCOL_PHP.md` §F item 9 — what I think of the overlap number

```
per-span overlap: span0 31% (5/16), span1 15% (6/39)
kernel overlap 20% (11/55)   tier=narrowed is expected to clear 25%
```

**It is below expectation and I am not repairing it by moving the tier.** The
gap is accounted for line by line:

* **span1 (the caller frame, 15 %)** is deliberate. The row lifts from
  `PHP_FUNCTION(stream_select)` exactly what decides the kernel's domain — the
  three `fd_set`s, the three `FD_ZERO`s, `max_fd`, the `sets` accumulation and
  the `RETURN_FALSE` arm — and drops `zend_parse_parameters`, the timeout
  construction, the read-buffer emulation, `php_select` and the three
  `stream_array_from_fd_set` calls, which are argument parsing and everything
  *downstream of the write*. A span pinned because it contains the OBJECT will
  always score low on TEXT.
* **span0 (31 %)** is the loop, and the 11 lines that do not survive are the
  three `zend_hash` cursor calls, the `Z_TYPE_P` test, the
  `php_stream_from_zval_no_verify` pair and the `php_stream_cast` line — i.e.
  **exactly the wrapper `narrowed` says comes off**, plus four braces.

⚠ **The alternative — dropping `extra_spans[0]` — would have raised the union
to 31 % and made the number better while making the row worse**, because the
caller frame is where the object lives and where a third of R1h goes. `ph07`
learned that at `TASK_PHP_017` M1. ⭐ **This is the first real row the
demoted floor has been read on** (`PROTOCOL_PHP.md` §F9 predicted that), and the
answer is: *the number is right, the tier is right, and a span pinned for its
DECLARATIONS rather than its statements is a shape the heuristic does not
model.*

`unevaluable_conditionals` = **1** (`#ifndef PH16_KERNEL_H`, an include guard).

---

## §2 ⚠⚠⚠ `_FORTIFY_SOURCE` — the row's own bound, inserted by the toolchain

**This is the row's most surprising result and nothing in the task file
anticipated it.** `controls/fortify.py`, all three controls green:

| cell | `_FORTIFY_SOURCE` | `FD_SET(2048)` on the adversarial input |
|---|---|---|
| gcc `-O0` | undefined | survives |
| **gcc `-O3`, no `#undef`** | **3** | ⚠ **`*** bit out of range 0 - FD_SETSIZE on fd_set ***: terminated`** (SIGABRT) |
| gcc `-O3`, with the `#undef` | 0 | survives |
| clang `-O0` | undefined | SIGABRT — `munmap_chunk(): invalid pointer`, and that is **the defect**, not a check: the wild write reached `main`'s frame (§3) |
| clang `-O3` | undefined | survives |

Ubuntu 24.04's gcc spec adds `-D_FORTIFY_SOURCE=3` whenever it is optimising,
and glibc's fortified `FD_SET` is `__FD_ELT` → `__fdelt_chk`, which tests
`d < FD_SETSIZE`. **That is the bound this whole row is about.**

**What it costs on BENIGN, in-range indices** — callgrind, whole-program, on
`small.bin`, denominator **counted from `model.py`'s own decode**:

```
gcc   -O3 with #undef     92 605 764 Ir
gcc   -O3 without         148 709 085 Ir      +56 103 321  =  +60.6 %
clang -O3 with #undef     90 887 777 Ir
clang -O3 without         90 887 763 Ir       -14 Ir total  --  clang never fortifies

benign FD_SET calls on small.bin = 3 773 157
                                  => 14.87 Ir per benign FD_SET (gcc)
                                  =>  0.00 Ir per benign FD_SET (clang)
```

⚠ **A standalone probe of a tight `FD_SET` loop and nothing else gives 7.01, and
the first draft of this row quoted THAT in four places.** It is a different code
shape. The row's own number is 14.87 and §0 records the correction.

**So both C kernels `#undef _FORTIFY_SOURCE` before the first system header.**
Without it `c-gcc-O3` would be **a hardened rung wearing R1's label**: it would
abort on the adversarial inputs, and it would charge every benign `FD_SET` for a
check `c-clang-O3` does not perform — a 60 % tax a reader would attribute to
C-versus-Rust. PHP 5.0.0 (2004) was built with no such thing.

⭐ **The general lesson, and it is not about this row:** *`PROTOCOL_PHP.md` §A1's
substitution rule was written for things the EXTRACTION changes. This one is a
thing the extraction did not change and the TOOLCHAIN did.* A row that only
diffs its C against the tarball cannot see it; only running the binary can.

---

## §3 ⭐⭐ The oracle — PHP's own two other `fd_set`s, and no scaffolding

`TASK_PHP_025` §3 offered a `volatile` canary and asked whether it survives
contact with a real kernel. **It was not needed.** `PHP_FUNCTION(stream_select)`
already has two live neighbouring `fd_set`s and reads all three back at `:706`,
so the row's witness is *PHP's own data* and `idiom.forbidden[2]` bans a canary.

### 3a. The frame, measured

```
gcc   -O0 / -O3    &rfds +0   &wfds +128   &efds +256     span 384 B   LOWEST = rfds
clang -O0 / -O3    &rfds +0   &wfds -128   &efds -256     span 384 B   LOWEST = efds
```

Contiguous under both compilers — **in opposite order**. Which neighbour absorbs
the over-write is a stack-layout fact and the two compilers disagree about it.

### 3b. ⚠⚠ The oracle is not a story — it PREDICTS the corrupted checksum

`controls/oracle.py` models the frame as 48 contiguous 64-bit words and computes
what R1 must return. Against the built binaries:

| | predicted | measured | |
|---|---|---|---|
| `c-gcc-O3`, `adversarial-redzone.bin` | 16790048728120879104 | 16790048728120879104 | ✅ |
| `c-gcc-O3`, `adversarial-silent.bin` | 13722268663371347968 | 13722268663371347968 | ✅ |
| `c-clang-O3` (desc layout), `-redzone` | 18151814905338390528 | 18151814905338390528 | ✅ |
| `c-clang-O3` (desc layout), `-silent` | 15084034840588859392 | 15084034840588859392 | ✅ |

**Bit for bit, both compilers, from the layout alone.** There is nothing left
over: the corruption is exactly the write, in exactly the word the layout says.

⚠⚠ **F52 — the setup could have encoded the answer, and this is the check that
it did not.** R1 differs from R1h for **two** reasons: the write, *and*
`max_fd` going unclamped because guard (c) is absent (this row folds `max_fd`).
A control that merely said *"R1 ≠ R1h"* would have been satisfied by the second
alone, on a row whose whole claim is the first. So `oracle.py` never differences
the rungs; it predicts, and it ships three negatives:

* **must-fire** — predict with the write suppressed and only `max_fd` moving:
  `3831935670616942592` / `7552720107290115072`, **≠ measured**. ✅
* **must-fire #2** — predict against the gcc binary with *clang's* measured
  layout: **≠ measured**, and vice versa. ✅ The prediction is sensitive to the
  ordering, so it is measuring where the write lands.
* **must-NOT-fire** — on `small.bin` and `large.bin` the prediction, R1, R1h and
  `model.py` all agree and `escaped == 0`. ✅

### 3c. ⚠⚠ Where ASan stops, measured on THIS frame

One `FD_SET` per process, gcc `-O1 -fsanitize=address,undefined
-fstrict-aliasing`, three live `fd_set`s in the frame:

| index | byte offset past `rfds` | ASan | the row's own fold |
|---|---|---|---|
| ≤ 1023 | in bounds | silent | unchanged (correct) |
| **1024 … 1279** | 128 … 152 | ✅ **REPORTED** `stack-buffer-overflow` | — |
| **1280 … 3071** | 160 … 376 | ⚠ **SILENT** | ⭐ **value moved** |
| ≥ 4096 | ≥ 512 | ⚠ silent | unchanged — past the three sets |

Flip located at exactly 1279 → 1280, i.e. **ASan's redzone on this object is 32
bytes**. That reproduces `.temp/mgr166/asan_reach.c`'s figure **on a frame the
manager did not control**, and it gives the row two adversarial inputs that
differ in one number: `adversarial-redzone.bin` (1024) and
`adversarial-silent.bin` (2048).

⚠ **The completeness statement, and it is a range and not a claim:** *the oracle
is complete for `1024 ≤ idx < 3072`* — the two `fd_set`s of head-room PHP's own
frame provides — **and blind above it**. `escaped` counts the writes that leave
the block: 64 and 128 on the two adversarial inputs, which are the second and
third arms' over-writes going past the highest set. Those land elsewhere in the
frame and are why `c-clang-O0` aborts (§2).

### 3d. Why `model.py` derives `sanitizer_expect` from a REDZONE

⚠ This row's `sanitizer_expect` is `"fires"` iff some call writes into
`model.ASAN_REDZONE = range(1024, 1280)` — **not** iff some call writes out of
bounds. That is a weaker claim than any other row in this corpus makes, and it
is the row's headline rather than a concession: `adversarial-silent.bin` writes
128 bytes further out, is declared `clean`, exits 0, and **corrupts a live
object the function's own return value depends on**. `.memory-php/02-ladder.md`
already says *a sanitizer limb is a claim about YOUR allocator, not about PHP*;
this row is the same sentence about a **stack redzone**.

---

## §4 The fix — and it is THREE guards, not one

`99e290f882c9` (Wez Furlong, 2004-09-17, *"Bug #24189: possibly unsafe select(2)
usage. Where possible we avoid it by using poll(2)."*), first shipped in
php-5.1.0. **Ten files, 27 368 B — `controls/99e290f882c9.patch`, sha256
`b9d7ac6cbbe2017839d24ff7b35ecde8fb3803a2c22f27ef994fb512d070ffde`.**
⚠ Cite the hunk, not the commit.

⚠⚠ **`TASK_PHP_025` §2 names TWO guards. The patch has THREE, and the third is
in the caller's frame** — the frame this row lifts:

```c
#ifdef PHP_WIN32                                    /* counted array of SOCKETs */
# define PHP_SAFE_FD_SET(fd, set)   FD_SET(fd, set)                        /* NO CHECK */
# define PHP_SAFE_MAX_FD(m, n)      do { if (n + 1 >= FD_SETSIZE) { _php_emit_fd_setsize_warning(n); }} while(0)
#else
# define PHP_SAFE_FD_SET(fd, set)   do { if (fd < FD_SETSIZE) FD_SET(fd, set); } while(0)
# define PHP_SAFE_MAX_FD(m, n)      do { if (m >= FD_SETSIZE) { _php_emit_fd_setsize_warning(m); m = FD_SETSIZE - 1; }} while(0)
#endif
```

| | guard | where | what it is for |
|---|---|---|---|
| (a) | `&& this_fd >= 0` | `streamsfuncs.c:540` | a negative fd from a failed cast |
| (b) | `PHP_SAFE_FD_SET` | `:541` | **the memory-safety half** |
| (c) | `PHP_SAFE_MAX_FD(max_fd, max_set_count)` | `PHP_FUNCTION(stream_select)` | `php_select(max_fd + 1, …)`'s `nfds` |

⭐ **(c) is not about the write, and that is worth saying plainly**:
`*max_fd = this_fd` sits *inside* the arm (b) protects but is **not bounded by
it**, so (b) alone still hands `select(2)` an out-of-range `nfds`. This row
folds `max_fd`, so (c) is observable in the checksum and
`controls/fix_scope.py` prices it apart from (b).

### 4a. What each guard buys — `controls/fix_scope.py`, all four controls green

```
Q1  the SHIPPED BENIGN corpus            small.bin  (a) 0  (b) 0  (c) 0
                                         large.bin  (a) 0  (b) 0  (c) 0
Q2  1536 synthetic windows (every tag x 16 indices straddling FD_SETSIZE x 6 ctl)
      R1  (no guards)      out-of-bounds writes 2880   max_fd out of range on 880 windows
      R1 + (a)                                  2880   -- (a) fired 0 times
      R1 + (b)                                     0   -- (b) fired 2880
      R1 + (c)                                  2880
      R1h (a+b+c)                                  0
      b_too_wide (fd<2048)                      1440   <- the must-fire INCOMPLETE control
Q3  guard (a) fired 0 times over the WHOLE domain
Q4  (b) alone still differs from (a+b+c) on 880 of 1536 windows
```

⭐ **The fix is COMPLETE** — (b) removes 2880 of 2880 illegal writes and no
guard fires on a benign window — which is what licenses R2–R5 implementing
R1h's function rather than a further one. ⚠ Unlike `ph03`, whose 2004 fix was
half dead and half incomplete, and unlike `ph07`, half of whose fix upstream
later deleted as a bug: **`ph16`'s is the first of the three that is neither.**
That is a third data point for `.memory-php/02-ladder.md`'s *"NEITHER WAS
MINIMAL NOR SUFFICIENT AS SHIPPED"* — and it is the counter-example, so the
sentence needs its `n` said.

### 4b. ⚠ Guard (a) is DEAD in this kernel, measured

`this_fd` is `PH16_IDX(e)`, a 14-bit field: `0 ..= 16383`, never negative.
Q3 above is the count, over the whole domain, rather than the argument. It is
carried anyway because it is the shipped POSIX configuration — and gcc removes
it entirely (§8b).

**Negative `this_fd` is OUT of this row's contract, and the reason is measured
rather than aesthetic:** `FD_SET(-1, &fds)` expands to `1UL << (-1 % 64)`, a
shift by a negative count — **undefined behaviour in the SHIFT**, not the
out-of-bounds WRITE this row models, and compiler-dependent in a way the row's
oracle could not predict. `PLAN_PHP.md` §3.1 admits it as a variation and its
own row; it is not this one.

### 4c. ⚠ What is NOT verified about the `fix_commit`

`provenance.fix_commit` is `index.csv`'s own value and its patch really does add
the guard at `:541`; the code is unguarded at php-5.0.0 and guarded at
php-5.1.0 (`UPSTREAM_001.md` §4). **What was NOT done is a tag-by-tag bisect of
5.0.x branch backports.** `PROTOCOL_PHP.md` §F5(iii) asks for confirmation
against the tags; this row confirms the **window** (5.0.0 → 5.1.0), not the
exact commit. Stated in `fix_commit_note` too.

---

## §5 Reachability and fidelity — `PROTOCOL_PHP.md` §A3/§A4, before any rung

Settled in writing before a rung existed (`.temp/php25/reach.c`, and its
verbatim transcript is in `.tasks-php/TASK_PHP_025_REPORT.md`):

```
Q1 PASS  R1 == R1h on benign input, nothing corrupted
Q2 PASS  R1 corrupts a set no legitimate FD_SET could reach; R1h does not.
         THE VERDICT MOVES WITH THE GUARD (F52).
Q3 PASS  the corruption is visible in the RETURNED u64
Q4       oracle fires over index [1024 .. 3064] (step 8, sweep 0..3071)
Q4 PASS  complete exactly over [1024, 3072) -- the two neighbouring fd_sets
         PHP's own frame provides
Q5       benign sweep idx 0..1023: R1 corrupt on 0, R1 != R1h on 0
Q5 PASS  the upstream guard is DEAD on the whole benign domain and removes
         every out-of-range write
RESULT: PASS
```

⚠⚠ **THIS TRANSCRIPT IS FROM THE SECOND VERSION OF THE PROBE AND THE FIRST ONE
NEVER PRINTED ITS LAST FOUR LINES.** The first `reach.c` swept the index to
8192, walked past the three `fd_set`s into the stack protector, and died with
`*** stack smashing detected ***` **after Q4's flip lines and before Q4's
summary and the whole of Q5**. I had already written those lines into this file
and into the task report *from what the probe was designed to print*. Caught by
re-running it. The sweep now stops at 3071 — the out-of-frame behaviour is
`oracle_sweep.c`'s and `controls/fortify.py`'s job, not this probe's — and every
line above was emitted by the run whose command is in `.temp/php25/REFETCH.sh`.
**A transcript written from a probe's intent rather than its output is the same
defect as a stale figure, one step earlier.**

**Fidelity (§A4):** the corpus records CWE-787, an out-of-bounds write, and the
row reproduces `AddressSanitizer: stack-buffer-overflow` on
`adversarial-redzone.bin` and nothing else. ⚠ **It reproduces a DIFFERENT
signal on `adversarial-silent.bin` — none at all — and that is the row's
finding rather than a failure to hide.**

⚠⚠ **The PHP-level trigger and the kernel-level trigger are two different
things and the row does not blur them.** Reaching `this_fd >= 1024` in a real
PHP process needs more than 1024 open streams and an `RLIMIT_NOFILE` to match;
the *extracted kernel* takes indices from a blob and any index ≥ 1024 is out of
bounds. `FD_SET` never consults the fd table (`.temp/php11/fdset_probe.c`,
`.temp/mgr166/fdfacts.c`). Both are true; `PLAN_PHP.md` §4.2's reachability
deliverable is about the kernel, and the PHP-level statement is this paragraph.

---

## §6 The corpus, and the arms it must reach

`inputs/gen.py::_check_span` refuses to write a corpus that misses an arm, and
`model.py::selfcheck` check 2 re-asserts the same table **over the calls the
driver actually makes** — which is the sharper condition, because windows are
picked from a checksum-derived index and need not all be visited.
`PROTOCOL_PHP.md` §A2a rule 1's load-bearing half is the assertion, and this
row has it twice.

Arms asserted: all four entry tags (both success encodings, so a rung testing
`tag == 2` is wrong); index 0 **and 1023** (the guard's test is `<`, not `<=`);
`X_array == NULL` and `!= IS_ARRAY` for all three arrays; `sets == 0`
(`RETURN_FALSE`) and `sets == 3`; an empty array and three non-empty ones; the
FALSE arm of `if (this_fd > *max_fd)`; and — negatively — **no window on which
any of the three guards fires**.

`model.py::selfcheck` also drives its three implementations over a synthetic
domain `inputs/` cannot carry: every `ctl` in 0..63, every tag × ten indices
straddling `FD_SETSIZE`, every split of five strides, and the `%` on the split
words past one wrap (`PROTOCOL_PHP.md` §A2a rule 2 — `ph03` shipped for a task
with two implementations computing different functions).

---

## §7 The allocator

**This row allocates nothing.** `stream_array_to_fd_set` fills an `fd_set` the
caller declared as a stack local; the wrapper does the same. No `emalloc`, no
`php_shim_reset`, no `php_shim_tally`, and `provenance.uses_allocator` is
`false` with a reason. ⚠ **`c/emalloc_shim.h` is symlinked anyway** — that rule
is unconditional (`PROTOCOL_PHP.md` §B2), and the preflight confirms it is in
both digests.

⭐ It is also why this row has no analogue of §B1.2's tally fold: there is no
allocator activity to land in the checksum, and **the three `fd_set`s are what
the checksum carries instead** — which is exactly what makes the oracle work.

---

## §8 The measurement, and a mechanism for every delta

`results-php/ph16-fdset-index.json`, **O3 / isolated**, `kernel_exclusive_ir`.
⚠ **Within-row ratios only** — `.memory-php/03-numbers.md` forbids comparing any
`phNN` figure with a `pNN` one.

| rung | `large.bin` | vs `c-gcc` | `small.bin` | vs `c-gcc` | insns |
|---|---:|---:|---:|---:|---:|
| `c-gcc` (R1) | 317 708 014 | — | 92 081 388 | — | 369 |
| `c-clang` (R1) | 320 046 417 | +0.74 % | 90 365 805 | −1.86 % | 285 |
| `safe_naive` (R2) | 416 298 533 | **+31.03 %** | 118 269 785 | +28.44 % | 479 |
| `safe_tuned` (R3) | 305 508 386 | **−3.84 %** | 88 874 724 | −3.48 % | 474 |
| `unsafe` (R4) | 311 246 696 | −2.03 % | 89 974 452 | −2.29 % | 425 |
| `verus` (R5) | 311 246 696 | −2.03 % | 89 974 452 | −2.29 % | 425 |
| `c-gcc-h` (R1h) | 352 560 086 | **+10.97 %** | 101 993 201 | +10.76 % | 400 |
| `c-clang-h` (R1h) | 341 130 813 | +7.37 % | 95 936 934 | +4.19 % | 291 |

⭐ **`verus` is byte-identical to `unsafe`** — `md5_fn 659d7b4b4168` on both,
425 instructions, 1775 bytes, and the gate pins `identity: exact`. **The proof
costs nothing at run time.** At O0 the two genuinely differ (527 vs 488
instructions): nothing is inlined there, so R5's three trusted wrappers survive
as real calls where R4's `#[inline(always)]` helpers do not. That is codegen,
not layout — which is why the pin is `exact` at O3 and `differ` at O0, and why
it is `exact` rather than `norel`: **this kernel calls out to nothing**, so
there are no relocation bytes to differ.

### 8a ⭐⭐ THE SAFETY CHECK COSTS +10.97 %, AND HERE IS THE MECHANISM

`PROTOCOL_PHP.md` §F8: *a cost with no mechanism is an incomplete row.* Read off
`objdump` of `c-gcc-O3-isolated` and `c-gcc-h-O3-isolated`, the hot per-entry
loop of the read arm:

```
R1  (19 instructions on the writing path)      R1h (21)
    movzbl 0x7(%rax),%r9d                          movzbl 0x7(%rax),%r10d
    movzbl 0x6(%rax),%ecx                          movzbl 0x6(%rax),%ecx
    shl    $0x8,%r9d                               shl    $0x8,%r10d
    or     %r9d,%ecx                               or     %r10d,%ecx
    cmp    $0x7fff,%r9d       <- the tag test      cmp    $0x7fff,%r10d
    jbe    ...                                     jbe    ...
    mov    %ecx,%r12d                              mov    %ecx,%r10d
    mov    %rbp,%r15                               and    $0x3fff,%r10d
    and    $0x3fff,%r12d                       +   test   $0x3c,%ch      <-- GUARD (b)
    shl    %cl,%r15                            +   jne    ...
    mov    %r12d,%r9d                              mov    %r10d,%r12d
    sar    $0x6,%r9d                               mov    %rbp,%r15
    movslq %r9d,%r9                                sar    $0x6,%r12d
    or     %r15,0x10(%rsp,%r9,8)  <- FD_SET        shl    %cl,%r15
    cmp    %r12d,%edi                              movslq %r12d,%r12
    cmovl  %r12,%rdi           <- max_fd           or     %r15,0x10(%rsp,%r12,8)
    add    $0x2,%rax                               cmp    %r10d,%edi
    cmp    %r11,%rax                               cmovl  %r10,%rdi
    jne    ...                                     add    $0x2,%rax
                                                   cmp    %rbx,%rax
                                                   jne    ...
```

**+2 instructions per entry on 19 = +10.5 %, against a measured +10.76 % /
+10.97 %.** The mechanism accounts for the number.

⭐⭐ **And the two instructions are not the ones you would write.** gcc turned
`this_fd < FD_SETSIZE` into **`test $0x3c,%ch`** — a bit test on bits 10..13 of
the *raw entry word*, before `this_fd` is ever materialised, because
`this_fd = e & 0x3FFF` makes `this_fd >= 1024` exactly *"any of bits 10..13 is
set"*. **The compiler proved the guard without computing the quantity it
guards.**

⭐ **Guard (a) is gone entirely** — no `test`/`js` anywhere — which is §4b's
deadness, confirmed in the codegen and not only in the model.
**Guard (c) is branchless and once per call**: `mov $0x3ff,%ecx; cmp %ecx,%edi;
cmovle %rdi,%rcx`, three instructions amortised over 2035 entries, i.e. ~0.001 %.
**So essentially all of the 10.97 % is guard (b), two instructions, in the
loop.**

### 8b ⚠⚠ R3 IS FASTER THAN C, AND THE MECHANISM IS A CHECK THAT MOVED

`safe_tuned` is **−3.84 %** against `c-gcc`, **−26.6 %** against `safe_naive`
and **−1.84 %** against `unsafe`, all on `large.bin`. The R2→R3 lever is one
respelling:

```
R2   if this_fd < FD_SETSIZE { fds[(this_fd / 64) as usize] |= 1u64 << (this_fd % 64); }
R3   let w = (this_fd / 64) as usize; if w < NW { fds[w] |= 1u64 << (this_fd % 64); }
```

They are the same predicate on a `u32` — `controls/guard_equiv.py` proves it
over all 16 384 reachable values against a build of the C, with four negatives.
What changes is what **rustc** can see: in R2 the guard bounds `this_fd` and the
index is `this_fd / 64`, and rustc emits a *second* bounds check on `fds[..]`;
in R3 the guard bounds the index itself and there is nothing left to check.
⚠ **That is a check MOVED, not deleted** — the reviewer's question — and the
check that remains is `PHP_SAFE_FD_SET` itself, which no rung may remove.

⚠ **`safe_naive` at +31 % is therefore NOT "the bounds-check tax".** It is one
redundant bounds check per entry, on a loop whose useful body is ~13
instructions. Quoting +31 % as the cost of safe Rust would be quoting the cost
of a spelling.

### 8b-bis ⚠⚠ AND ONE COLUMN IN THE PUBLISHED TABLE IS NOT A SAFETY EFFECT

`results-php/tables/ph16-fdset-index.md`'s `vec` column, O3/isolated:

```
c-gcc      -        c-clang    xmm      safe_naive xmm     safe_tuned xmm
c-gcc-h    -        c-clang-h  xmm      unsafe     xmm     verus      xmm
```

**Both gcc cells vectorise nothing and every other cell uses `xmm`.** The
vectorisable work in this kernel is the three `FD_ZERO`s — 384 bytes of zeroing
per call, a fixed term §8's `collapse.note` already flags — and rustc and clang
emit SIMD stores for it where gcc emits `rep stos`/scalar.

⚠ **So `safe_tuned` being −3.84 % against `c-gcc` is NOT purely the respelling
in §8b.** Part of that gap is a codegen difference on a term that has nothing to
do with safety, and it is *the same term for all six non-gcc cells*, so it
cancels in every Rust-vs-Rust delta (R2→R3→R4→R5) and does **not** cancel in the
C-vs-Rust one. `.memory-php/02-ladder.md` records exactly this trap on `ph03`
— *"`c-clang` beats `c-gcc` by 15.4 %, larger than every safety effect on the
row"* — and it is live here too: `c-clang` is +0.74 % on `large.bin` and
−1.86 % on `small.bin`, so the compiler difference alone changes sign with the
input.

⭐ **What survives the confound is the R1-vs-R1h number**, +10.97 %, because it
compares two gcc cells that differ only in the guard, and §8a reads its
mechanism off their disassembly. **That is the row's headline cost figure, and
the Rust-vs-C ones are not.**

### 8c ⚠ What these numbers are NOT

* **Not a `c-gcc` vs `c-clang` result.** `c-clang` is +0.74 % on `large.bin` and
  −1.86 % on `small.bin` — the sign flips with the input, so this row supports
  no compiler claim.
* **Not comparable to `ph03`'s or `ph07`'s ladder**, and certainly not to any
  `pNN`: different kernels, different work per call
  (`.memory-php/03-numbers.md`).
* **Not a `fixed-R4 bound` with a counterpart.** `controls/spellings.py` was NOT
  built — see §11. The `R3ship − R4ship` figure below is **the cost of THESE
  spellings of these rungs** and nothing more.
* ⚠⚠ **`R3ship − R4ship` is NEGATIVE on this row**: `safe_tuned` is
  **1.84 % cheaper than `unsafe`** on `large.bin` (305 508 386 vs 311 246 696).
  A safe rung beating the unsafe one is a real measurement and it is what the
  unsearched endpoint is worth here; **do not publish it as a bound**, because
  neither side has been searched.

### 8d ⚠ The wall clock says nothing here

Recorded in the record; not read. 16 O3 cells × 30 reps interleaved on cpu 3,
and the effects being measured are 2 instructions in a loop.

---

## §9 Scope — what this row deliberately does NOT model

* **`streamsfuncs.c:577`'s `FD_ISSET`.** The same commit patches **four**
  unchecked fd-set sites and the catalogue has **one**: `:541` (write, this
  row), `:577` (read, no row), and `ext/sockets/sockets.c:536` / `:563` (write
  and read, no rows — and `sockets.c` has **no rows at all**). ⚠ **This row does
  not adjudicate them**: `TASK_PHP_026` owns that question and `.temp/mgr166/`
  §2 is the manager's note. What this row's reading adds is one paragraph:
  reading the patch confirms all four sites and confirms that the *fix* is
  three macros rather than the two `TASK_PHP_025` §2 names, which is a fact
  about the commit and therefore about all four.
* **negative `this_fd`** — §4b.
* **the PHP-level trigger** — §5.
* **`select(2)` itself.** `php_select` is deleted as downstream; the row stops
  at the value `stream_select` would hand it.

---

## §10 R5 — Verus

`15 verified, 0 errors`; `18 verified, 0 errors` under `--cfg slb_twin`.

### 10a ⭐ The obligation is an INDEX BOUND, and there is no walk in it

`ph03`'s and `ph07`'s proof obligations are *termination* obligations about a
cursor advanced by data. **This row's is one line on a straight-line path**:
`walk`'s `decreases` is the trivial `n - i` of a counted loop, and everything
that needs an argument is `w < NW` licensing `aset_unchecked`. **That test IS
`99e290f882c9` guard (b)**, and `controls/negatives.py --emit noguard` deletes
it and the proof fails.

The exec code's two unchecked classes rest on **two independent facts**:

| unchecked | licensed by | comes from |
|---|---|---|
| `aget_unchecked` / `aset_unchecked` on the `fd_set` | `w < NW` | **a 2004 security patch** |
| `get_unchecked` on the window | `off + len <= buf@.len()` and `m = (len - 6) / 2` | **the harness's own contract** — not PHP at all |

An editor who removed the 2004 patch would remove the precondition of one class
and not the other, which is why they are kept apart here.

### 10b The proof-budget finding — and the expensive side is the TWIN

| version | plain | `--cfg slb_twin` |
|---|---|---|
| as first written | needs 16 (FAILS at 14) | 1 |
| + nine `let ghost` bindings naming what `fdset_win` names | needs 6 (FAILS at 4) | 1 |
| + `arm_state` / `arm_sets` hiding the three arms' `if` | **needs 2** | **needs 10, FAILS at 8** |

⭐ **The cost was attacked first and the attack worked on the side it could
reach: 16 → 2 plain.** What it could not reach is the twin build, where three
more verified functions add to the module's SMT context. Verus's default is 10,
so the twin would *just* scrape it — **a proof that passes on one side of a coin
flip is not a proof** — and the shipped budget is `#[verifier::rlimit(30)]`,
3× the worst measured requirement. `harness/check.py::_verus` passes no
`--rlimit`, so it has to be an attribute.

⚠ **This is the inverse of `ph07`**, whose plain side was the expensive one.
The lever there was getting a 256-element `array_view` out of the spec; here it
was naming intermediates so the postcondition is a chain rather than a search.

### 10c TCB — five trusted items

`get_unchecked`, `aget_unchecked`, `aset_unchecked` (three verified twins),
`load_input`, `emit`. `spec.md` carries `unsafe_justifications` for
`aget_unchecked` and `aset_unchecked`.

### 10d The mutants — `controls/negatives.py`: seven mutants and one baseline, all green

```
must-NOT-fire  baseline      (15, 0)                            PASS
must-FAIL      noguard       14 verified, 1 errors              PASS
must-FAIL      nomaxfd       14 verified, 1 errors              PASS
must-FAIL      weakreq       17 verified, 1 errors  [twin]      PASS
must-FAIL      wrongwalk     13 verified, 2 errors              PASS
must-FAIL      tautology     14 verified, 1 errors              PASS
must-VERIFY    tautology-un  15 verified, 0 errors              PASS
must-FAIL      zerobody      13 verified, 1 errors              PASS
```

⭐ **`tautology` was expected to VERIFY and does not, and that is a result.**
`.memory/04-verus.md` warns that replacing an `ensures` with `r == r` verifies
with the same green count and no diagnostic. On this row it fails — **in
`main`'s `while` loop**, because the driver's `assert(r == fdset_fold(...))`
*consumes* the postcondition and has nothing left to discharge it with. So the
consuming assert is load-bearing here and not decoration, which is the claim its
own comment makes. `tautology-un` — the same edit **plus** deleting that assert
— verifies `15 / 0`, and **that** is the vacuity baseline.

### 10e ⚠ A `vparse` interaction, found and worked around

`to_fd_set`'s `ensures` was first written with `if … { … } else { … }` block
expressions. **`vparse` truncates a clause at the first `{`**, so the derived
pin came out as `"r == if not_an_array"` — a prefix. Verus was unaffected (it
reads the source), but the `spec.md` pin would have under-described the contract
while the gate compared it and passed. The `ensures` is now written through two
spec helpers (`arm_sets`, `arm_state`) and contains no braces. **Reported to the
manager as a minor harness observation; nothing was edited under `harness/`.**

---

## §11 What I did NOT do

* ⚠⚠ **`controls/spellings.py` — NOT BUILT. The debt is now three rows old**
  (`ph03` owes both sides, `ph16` owes both, `ph07` has discharged it).
  `TASK_PHP_025` §6.2 asked to be told if carrying it turned this into two
  tasks, and it did: this row cost a re-measure for the R1h restructure, a
  second for the `kernel.h` correction, five `report.py` renders and SEVEN gate rounds. **§8c states the
  consequence in terms**: no figure here is a `fixed-R4 bound`, and the
  R3-vs-R4 number is *negative*, which makes searching both sides more
  interesting on this row than on either predecessor and not less.
* **No tag-by-tag bisect of the `fix_commit`** — §4c.
* **No adjudication of the three uncatalogued sibling sites** — §9.
* **`adversarial-far.bin`** (an index past the frame) was designed and dropped:
  `.temp/php25/reach.c` showed a sweep past 3072 hits the stack protector, so
  such an input would record `*** stack smashing detected ***` in some cells and
  a wild write in others — recorded behaviour, but it adds a fifth adversarial
  file whose result is "the layout beyond the frame", which the row does not
  claim to model. §3c's `escaped` counts state the same fact.

---

## §12 `PROTOCOL.md` rule 6's addendum — the hashed block re-read against the record

Every numeral inside the `slb-contract` block, checked against
`results-php/ph16-fdset-index.json` and the control logs **after** the last
measurement:

| where | numeral | checked against |
|---|---|---|
| `identity[0].why` | 426 instructions, byte-identical disassembly | ⚠ **CORRECTED to the record**: the shipped record says **425** instructions / **1775** bytes and `md5_fn 659d7b4b4168` on both cells. 426 was a pre-gate count from a hand build with different flags. |
| `identity[0].why` | O0 533 vs 501 | ⚠ **CORRECTED to the record**: **527 vs 488**. |
| `idiom.why`, `divergences`, `c/kernel.h` | 14.87 Ir per benign `FD_SET`, +60.6 % | `controls/fortify.py`, §2 |
| `idiom.why` | ASan redzone 1024…1279 / silent 1280…3071 | §3c |
| `provenance.extract_sha256` ×2 | `e3fbdff6…`, `bad87d1a…` | `harness-php/provenance.py`, green |
| `collapse.note` | strides 550 / 4076 | `inputs/gen.py`, and the gate's own `work_per_call` |
| `verus.obligations` | 15 / 18 | `verus_run.py`, §10 |
| `verus.twin_obligations_note` | 16 / 14 / 6 / 4 / 2 / 10 / 8 / 30 | the rlimit bisect, §10b |
| `idiom.forbidden[1]` | "fourteen (spelling × rung) obligations" | gate 1's `[idiom-forbidden]` count |
| `idiom.required[3]` / `[5]` | "the other four" / "five spellings pinning nothing" | gate 2's audit lines |
| `provenance.fix_commit_note` | TEN files, 27 368 B, FOUR sites | `controls/99e290f882c9.patch` |
| `provenance.cwe_note` | 32-byte redzone | §3c |
| ⚠ `provenance.divergences_note` | ~~SEVEN of thirteen~~ → **EIGHT of TWELVE** | **the one that was WRONG** — see §0 move 5 |

**How the sweep was done, so it can be repeated:** every string in the hashed
block was walked and every numeral and every spelled-out count extracted
(`SEVEN`, `THIRTEEN`, `FOUR`, …), then each checked against the artefact it
names. **One of them was wrong**, and it was a self-description — the count of
the list it sits at the bottom of — which is the class no other check in this
project looks at.

---

## Trusted-item arguments

The gate requires one section per trusted item and prints it; only a human can
judge it.

SLB-TRUSTED-ARGUMENT verus.rs get_unchecked

**(a) Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*v.get_unchecked(i)`; the twin's body is `v[i]`. The standard
library documents `get_unchecked(i)` as `index(i)` with the bounds check
removed, so it is the same operation on the same slice at the same index, and
Verus checks the bound `v[i]` needs against the same `requires`. A defensive
twin — `if i < v.len() { v[i] } else { 0 }` — cannot satisfy the `ensures` and
fails the stage rather than passing it.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes *as the body stands*: one expression, one unchecked read,
at index `i` of slice `v`, and `ensures r == v@[i as int]` names that index and
that slice. ⚠ **Nothing mechanical enforces it.** A second unchecked read the
`ensures` never mentions — `let _peek = *v.get_unchecked(i + 1);` — is invisible
to 5a, 5c, 5c-req and 5c-twin alike.

⭐ **This row's backstop is stronger than `ph07`'s and the reason is worth
recording**: `identity` here is `exact` at O3, not `norel`, because the kernel
calls out to nothing. So an extra read added to `verus.rs` alone moves `md5_fn`
and stage 3c fails on a **byte** comparison rather than a normalised one. Miri
is the other backstop, and on this row it reaches the boundary on *every*
input: `get_unchecked(win, j)` runs `m` times per call with `j` up to
`2m + 5 == len - 1`, i.e. the last byte of the window, on `small.bin` and
`large.bin` alike. **Read the body, every time.**

**(c) Does the clause mean the same in both configurations?** Yes. `i < v@.len()`
mentions only `i`, `v` and vstd's `@`/`len()`, and `v: &[u8]` / `i: usize` are
concrete types with no generic or associated item a `#[cfg]` could redefine.

SLB-TRUSTED-ARGUMENT verus.rs aget_unchecked

**(a) Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*a.get_unchecked(i)` on `&[u64; NW]`; the twin's body is `a[i]`,
which is the same read with the bounds check rustc inserts. `[u64; 16]` derefs
to a slice for `get_unchecked`, so the two go through the same path with and
without the check.

**(b) Is the `ensures` complete?** Yes as the body stands: one expression, one
unchecked read, at index `i` of array `a`, and `ensures r == a@[i as int]` names
both. ⚠ Same standing gap as above — a second unchecked read the `ensures` never
mentions is invisible to every stage — with the same two backstops (`exact` O3
identity, and Miri, which exercises this item 48 times per call in `fold_set`
alone).

**(c) Does the clause mean the same in both configurations?** Yes, and here it
needs one extra sentence that `get_unchecked`'s does not. The `requires` is
`i < NW`, a comparison against a `const usize`, and `NW` is defined once inside
`verus!` with no `#[cfg]` on it. **The array's own length is not in the clause
because it is in the TYPE** — `vstd::array::array_len_matches_n` gives
`a@.len() == NW` for every `a` this signature admits — which is exactly the
argument `spec.md`'s `unsafe_justifications` entry makes, and it is why this
item needed one and `get_unchecked` did not.

SLB-TRUSTED-ARGUMENT verus.rs aset_unchecked

**(a) Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*a.get_unchecked_mut(i) = x`; the twin's body is `a[i] = x`, the
same store with the check. Verus checks that store's bound against the same
`requires`.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** ⚠ **This is the one that matters on this row**, and the answer
is yes *as the body stands*, with the argument written out because a write
wrapper is where an incomplete `ensures` is dangerous. The `ensures` is the
WHOLE post-state — `final(a)@ == old(a)@.update(i as int, x)` — not merely
`final(a)@[i] == x`. A body that also clobbered `a[i + 1]` would violate it and
could not verify. A body that stored something other than `x`, or stored it at
some other index, likewise. **What it does not exclude is an unchecked *read*
added to the same body**, which would be UB without moving the post-state; that
is the residual, and `identity: exact` plus Miri are what cover it.

⭐ **The reason this item is the row's own subject, one level down:**
`FD_SET(d, s)` in C is exactly this operation — a store into a fixed-size object
at a caller-supplied index — and it carries **no contract at all**. The whole
defect is that C has nowhere to write `i < NW` and no one to check it.
`controls/miri_vs_asan.py` is that observation as a measurement: with `w < NW`
deleted, Miri reports `Undefined Behavior: `assume` called with `false`` inside
`core::slice`'s own precondition assertion, on the same input where ASan on the
C rung says nothing at all.

**(c) Does the clause mean the same in both configurations?** Yes, for the same
reason as `aget_unchecked`: `i < NW` names a `const usize` defined once inside
`verus!`, `old(a)`/`final(a)` are Verus's own `&mut` forms, and `x: u64` is a
concrete type. The gate additionally forbids the token `slb_twin` anywhere in
the shipped configuration's reachable code.
