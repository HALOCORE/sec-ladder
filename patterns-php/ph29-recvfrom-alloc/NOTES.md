# ph29-recvfrom-alloc — measurements

Everything here was **run**. Commands are in `.temp/php27/` and the logs are
beside them. `README.md` is the reader's entry point; `spec.md` is the contract.

---

## §0 `PROTOCOL.md` rule 6 — the `slb-contract` hash, as first written

```
contract_sha256  da05b275bff68bf4957e48766dcfb3dbcc24520b4079e1c90c398f25f0fb9ddb
```

**as first written, before any cell was built.** Computed the way the gate
computes it — `re.search(r"```slb-contract\s*\n(.*?)```", txt, re.S)`, which
keeps the newline before the closing fence; the obvious spelling hashes one byte
less and gives a different number for every pattern in the tree
(`PROTOCOL_PHP.md` §E).

⚠ **IT HAS MOVED TWICE AND HERE IS EACH MOVE**, because a disclosure a
reviewer trusts *instead of* re-checking is worse than useless if it is
incomplete (`PROTOCOL.md` rule 6).

| | what moved |
|---|---|
| `da05b275bff68bf4…` | as first written, before any cell was built |
| `6668a4ed15fa8933…` | `identity[0]`'s `O0`/`O3` verdicts and its `why`, re-derived from the shipped measurement record — §12 |
| `a7a24972fa35ccd6…` | `verus.twin_obligations_note`, after `#[verifier::rlimit(30)]` was bisected away — §10b |
| `bb7fbb617e94d1f8…` | a twelfth `divergences` entry, for the `emalloc`/`efree` `#define` redirect — §11a |
| `5765a3cd4a94e1fa…` | the two per-language `idiom.required` entries lost their `why` key (the gate's schema admits only `c` and `rust`, and text under an unknown key **pins nothing**), and `vcopy_unchecked` lost a non-load-bearing `ensures` clause — §11d |
| `28a92facffb33148…` | `idiom.forbidden[0]` stopped backticking the expression it protects, and `forbidden[2]`/`[3]` gained one genuinely-absent banned token each — §12 items −3 and −2 |

**Move 4 is the gate's**, not mine, and both halves of it are the gate finding
a declaration that pinned nothing: a `why` key the idiom schema does not read,
and an `ensures` clause the proof does not use. **Move 1** is `identity[0]`. As first written the entry declared `O3: "norel"`
on the reasoning that `vec![0u8; cap]` reaches the global allocator through a
PLT entry, so the two cells must differ in relocation bytes. **The record says
`exact`.** **Move 2** is the note that defended a proof budget the row does not
need. **Move 3 ADDS a divergence entry** rather than withdrawing one, for a
`#define` redirect that made two cited lines verbatim.

⚠ **No move touched a `required`, a `forbidden` or the `idiom.why` prose.**
Moves 1 and 2 are declarations a measurement refuted — the direction rule 6's
addendum asks for; move 3 is the ledger growing, which is the direction §A2
wants (an entry cannot be quietly withdrawn, and this one was quietly
MISSING).

⚠ **The `git show HEAD:… | diff` test PROVES NOTHING ON A NEW PATTERN** and this
row does not pretend otherwise: a pattern lands in one commit, so on a clean
tree the command always prints nothing. The hash above is the only evidence, and
that is why rule 6 asks for it before any cell is built.

---

## §1 Reachability — deliverable #1, settled before any rung existed

`PROTOCOL_PHP.md` §A3 / `PLAN_PHP.md` §4.2. Probe:
`.temp/php27/reach.c`, which lifts `streamsfuncs.c:300-345` narrowed exactly as
`c/kernel.c` does and puts the allocator behind a `#define`.

**Citations, checked at source before anything else** (`.temp/php27/streamsfuncs.c`,
sha256 `b08f942de907…`, which is the manifest's entry for the file):

```
:304   long to_read = 0;
:309   if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "rl|lz", &zstream, &to_read, &flags, &zremote) == FAILURE) {
:321   read_buf = emalloc(to_read + 1);
:323   recvd = php_stream_xport_recvfrom(stream, read_buf, to_read, flags, NULL, NULL,
:332   read_buf[recvd] = '\0';
```

✅ `TASK_PHP_027` §1's `:309` and `:321` are exact, and `to_read` comes from
userland. ✅ **The tier is `narrowed` and the two tests agree** — the site is
inside a `PHP_FUNCTION` frame (the M4 test) *and* a `zend_parse_parameters`
wrapper comes off (`PLAN_PHP.md` §4's definition). Unlike `ph16`, there was
nothing to litigate.

⚠ **The truncation is `REAL_SIZE` at `zend_alloc.c:129`/`:135`, not `emalloc`'s
signature, and the row is 64-bit-only** (`RECAP_PHP.md` F46; F36 hypothesised
the opposite and is retracted). Re-run once, as the task asked, and pasted:

```
$ /usr/bin/gcc -O0 -o .temp/php27/ph29_probe .temp/php20/ph29_probe.c && ./.temp/php27/ph29_probe
.temp/php20/ph29_probe.c:68:49: warning: integer overflow in expression of type 'long int'
   68 |                 size_t size = (size_t)(LONG_MAX + 1L);
sizeof(long)=8 sizeof(size_t)=8 sizeof(unsigned int)=4 sizeof(zend_mem_header)=4

-- benign --
to_read=0                       size=1                       real_size=8            cache_index=1          malloc_arg=12     hdr.size=1
to_read=4095                    size=4096                    real_size=4096         cache_index=512        malloc_arg=4100   hdr.size=4096
to_read=65536                   size=65537                   real_size=65544        cache_index=8193       malloc_arg=65548  hdr.size=65537

-- the row's trigger: stream_socket_recvfrom($s, PHP_INT_MAX) --
to_read=9223372036854775807     size=9223372036854775808     real_size=0            cache_index=0          malloc_arg=4      hdr.size=0

-- neighbours: which to_read values truncate to a SMALL block? --
to_read=4294967295              size=4294967296              real_size=0            cache_index=0          malloc_arg=4      hdr.size=0
to_read=4294967296              size=4294967297              real_size=8            cache_index=1          malloc_arg=12     hdr.size=1
to_read=8589934591              size=8589934592              real_size=0            cache_index=0          malloc_arg=4      hdr.size=0
to_read=-1                      size=0                       real_size=0            cache_index=0          malloc_arg=4      hdr.size=0

-- CHECK_MEMORY_LIMIT(size, SIZE) adds SIZE==real_size, not size (zend_alloc.c:177) --
with --enable-memory-limit, allocated_memory += 0  (the request was 9223372036854775808)
```

⚠⚠ **THE FIRST VERSION OF THIS SECTION PASTED `.temp/php20/ph29_probe.log` —
`TASK_PHP_020`'s STORED OUTPUT — UNDER A `$ gcc … && ./ph29_probe` PROMPT, as
though it were a fresh run.** It was not; I had only `cat`-ed the log. The
block above is a real re-run, on this box, today, warning included. ⚠ The
warning is `ph29_probe.c:68`'s `LONG_MAX + 1L` — signed-overflow UB in the
PROBE, not in the row, and it is exactly why `RECAP_PHP.md` F46 prefers
`4294967295` as the trigger. **Everything else is byte-identical to the stored
log**, so the substance was right and only the provenance of the paste was
wrong — which is the half `TASK_PHP_027` §5 says to get right
(*"paste output you actually saw, never what a probe was meant to print"*).

**The reachability run itself**, `.temp/php27/reach.c`, with the REAL shim:

```
to_read        size=to_read+1         real_size    usable     wrote     case
63             64                     64           = real_size 64        benign, cached class (real_size 64 <= 87)
4095           4096                   4096         = real_size 65        benign, uncached class -> malloc/free
4294967295     4294967296             0            = real_size 65        ADVERSARIAL: to_read+1 == 2^32   (the row's trigger)
               ^^ WROTE 65 BYTES INTO A 0-BYTE BLOCK -- OUT-OF-BOUNDS WRITE.
-4294967297    18446744069414584320   0            = real_size 65        ADVERSARIAL: to_read+1 == -2^32  (SHIPPED)
               ^^ WROTE 65 BYTES INTO A 0-BYTE BLOCK -- OUT-OF-BOUNDS WRITE.
```

and under ASan, on the row's own trigger:

```
==3631730==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x503000000058
WRITE of size 64 at 0x503000000058 thread T0
0x503000000058 is located 0 bytes after 24-byte region [0x503000000040,0x503000000058)
    #1 0x… in php_shim_emalloc common-php/emalloc_shim.h:372
```

⭐ `0 bytes after a 24-byte region` is the shim's header-sized block, and it is
why this row has **no silent band**: `php_shim_emalloc` returns
`p + sizeof(header) + padding`, so the payload ends exactly where the malloc
region ends. Contrast `ph16`, whose over-write is invisible to stock ASan past
32 bytes.

---

## §2 The tier, and the one place a reader could reasonably object

`spec.md` declares `narrowed`, and the wrapper that comes off is
`zend_parse_parameters` itself. `TASK_PHP_027` §6.3 asked whether *"the blob
supplies the `long` directly"* is still the same defect, because the whole
defect is *"a `long` from userland"* and the parse is how it gets there.

**It is, and here is the argument rather than an assertion.**

1. `PROTOCOL_PHP.md` §A1 defines `narrowed` as *"a wrapper comes off (zval
   unpacking, **argument parsing**)"*. Argument parsing is named in the
   definition; this is the central case, not a stretch of it.
2. The parse is **correct**. `"l"` on a 64-bit build yields a full `long`
   (`Zend/zend_API.c`, `case 'l': convert_to_long_ex(arg)`), so what reaches
   `:321` is exactly what the caller wrote. There is no narrowing, no clamp and
   no validation in it to lose.
3. The defect is not *"an unvalidated parse"* — it is *"`emalloc(to_read + 1)`
   with no relation between the size asked for and the size returned"*, and
   that sentence does not mention the parse.
4. ⚠ `ph94` had to declare exactly this as a `projection` because its blob
   supplied a value the real parse could not produce. **This one can**: every
   `long` the window's eight bytes can hold is a value
   `stream_socket_recvfrom($s, $n)` can pass, including the negatives, because
   PHP's `long` is signed and the userland integer type is the same `long`.

⚠ **What IS a projection here is the failure arm**, and `spec.md` says so: the
`FAILURE` return of `zend_parse_parameters` is deleted rather than modelled,
because it is the wrapper. Its own `RETURN_FALSE` is not this row's arm.

---

## §3 Fidelity — what the shim reproduces, and what it does not

`PROTOCOL_PHP.md` §3 asks for this in `NOTES.md` explicitly, and `TASK_PHP_027`
§6.1 makes it a stopping condition: **if this row could only be made to fault by
a shim behaviour the real `zend_alloc.c` does not have, the row must stop and
report it.**

**It does not.** The behaviour the row depends on is ONE STORE, and it is
transcribed rather than modelled:

| | `Zend/zend_alloc.c` (pristine, sha256 `fb4215f19dc2…`) | `common-php/emalloc_shim.h` |
|---|---|---|
| T1 declare | `:129` `unsigned int real_size;` | `:349` `unsigned int real_size;` |
| T1 round | `:132` `#define REAL_SIZE(size) ((size+7) & ~0x7)` | `:217` `PHP_SHIM_REAL_SIZE` |
| T1 store | `:135` `real_size = REAL_SIZE(size);` | `:352` |
| allocate | `:182` `ZEND_DO_MALLOC(hdr + padding + SIZE + END_MAGIC)` | `:372-375` |
| T2 | `zend_alloc.h:53` `unsigned int size:31` | `:199` |

`controls/allocator.py --audit` re-derives the three cited lines **from the
tarball text rather than from the shim**, and refuses if they are not what
`spec.md` says:

```
== T1, re-derived from the pristine tarball rather than from the shim
  zend_alloc.c:129  OK    'unsigned int real_size;\t\t\\'
  zend_alloc.c:132  OK    '#define REAL_SIZE(size) ((size+7) & ~0x7)'
  zend_alloc.c:135  OK    'real_size = REAL_SIZE(size);\t\t\t\t\\'
```

**What the shim does NOT reproduce, and none of it is load-bearing here:**
`ZEND_DEBUG` (magic words, poison-on-free), `MEMORY_LIMIT`, ZTS/`TSRMLS_*` and
the `ZEND_MM` sub-allocator — all four are itemised in `emalloc_shim.h`'s own
"deliberately not modelled" block. ⚠ **One deviation IS reachable in principle
and is declared**: PHP `exit(1)`s when `malloc` returns NULL
(`zend_alloc.c:189-198`) and the shim returns NULL instead, because a kernel
that exits reports a build failure rather than a measurement. `inputs/gen.py`
refuses any benign window whose `real_size` exceeds 65 536, so that arm is
**unreachable on the measured corpus** — asserted, not assumed.

### §3a The control, both directions, run

`controls/allocator.py`, 18 (case × allocator) cells, ASan, `navail = 4`:

```
  to_read=-4294967297  [adversarial-trunc.bin]   shim          OVERFLOW       want OVERFLOW       PASS   heap-buffer-overflow  WRITE of size 4  0B after a 24B region
  to_read=-4294967297  [adversarial-trunc.bin]   plain malloc  ALLOC-REFUSED  want ALLOC-REFUSED  PASS
  to_read=-4294967297  [adversarial-trunc.bin]   shim+445daac  CLEAN          want CLEAN          PASS
  to_read=-1           [adversarial-neg.bin]     shim          OVERFLOW       want OVERFLOW       PASS   heap-buffer-overflow  WRITE of size 4  0B after a 24B region
  to_read=-1           [adversarial-neg.bin]     plain malloc  OVERFLOW       want OVERFLOW       PASS   heap-buffer-overflow  WRITE of size 4  0B after a 1B region
  to_read=4294967295   [the row's trigger]       shim          OVERFLOW       want OVERFLOW       PASS
  to_read=4294967295   [the row's trigger]       plain malloc  CLEAN          want CLEAN          PASS
  to_read=4294967295   [the row's trigger]       shim+445daac  OVERFLOW       want OVERFLOW       PASS
RESULT: PASS (0 problem(s))
```

and without a sanitizer, which is where the `u64` evidence comes from:

```
  [shim-plain  ] 2   -4294967297    18446744069414584320   0    5   ...
  [shim-plain  ]       ^^ WROTE 5 BYTES INTO A 0-BYTE BLOCK -- OUT-OF-BOUNDS WRITE.
  [shim-plain  ]       tally: n_alloc=1 n_free=1 n_cache_push=1 bytes_mallocked=0 bytes_requested=18446744069414584320
  [malloc-plain] 2   -4294967297    18446744069414584320   0    0   ...
  [malloc-plain]       ^^ ALLOCATION FAILED -- PHP exit(1)s at zend_alloc.c:189. NO DEFECT.
  [malloc-plain] 4   4294967295     4294967296        4294967296  5   ...
  [malloc-plain]       ^^ in bounds.
```

⭐⭐ **THREE OUTCOMES, NOT TWO, AND THE MIDDLE ONE IS WHY THIS CONTROL IS NOT A
BOOLEAN.** The first draft of `allocator.py` asked *"did the sanitizer print?"*
and scored ASan's *`requested allocation size … exceeds maximum supported size`*
— its own allocator limit, not an out-of-bounds access — as the defect firing.
That is `F52`'s shape inside the file written to test `F6`. The control now
reports `OVERFLOW` / `ALLOC-REFUSED` / `CLEAN`.

⭐ **The row disappears under plain `malloc` in TWO different ways, and
`TASK_PHP_027` §3 named only one.** The task file says *"`malloc(2^63)` simply
fails and PHP exits"*. True at `LONG_MAX` and at the shipped `-4294967297`. At
the row's own UB-free trigger `4294967295` the request is 4 GiB, plain `malloc`
**succeeds**, and the write is in bounds — the defect vanishes because the
request is HONOURED. Both are "no row", for opposite reasons.

---

## §4 R1h — two stages, which one ships, and what the other costs

`TASK_PHP_027` §2 asked the row to choose and defend, and to say what the
alternative costs. **Both commits were verified at the commit, not at the
column** (`PROTOCOL_PHP.md` §F5(iii)); both patch files are under `controls/`.

| stage | commit | date, author | subject | size |
|---|---|---|---|---|
| 1 | `445daac3ab1a` | 2004-07-28 Ilia Alshanetsky | *"Fixed possible crash in stream_socket_recvfrom() when length parameter has a negative value"* | 1 file, +5 |
| 2 | `6ac8ffdfea10` | 2006-12-25 Antony Dovgal | *"MFH"* | 1 file, +1/−1 |

Stage 1 is the corpus index's own `fix_commit` for CRASH-097 and the fetched
bytes are **byte-identical to the copy the manager cached independently**
(`sha256 48ac72d1…`, 807 B). ⭐ Unlike `ph12` and `ph21`, whose column entries
name a later hardening, this column is right: the commit is in the row's own
file and function and lands in the 5.0.0 → 5.1.0 window `UPSTREAM_001.md` §4
predicted. Stage 2 was found by fetching **every** commit touching
`ext/standard/streamsfuncs.c` between 2004-07 and 2009-07 (82 of them) and
grepping the patches for `safe_emalloc(1, to_read, 1)`: exactly two hits, and
`6ac8ffdfea10` is the earlier.

### §4a Are they the same rung? **No, and the answer is a count.**

`controls/fix_scope.py`, exact integer arithmetic over a structured 8 227-value
domain plus a `navail` sweep, checked against the compiled C on six values:

```
   R1 faults on             30
   stage 1 alone refuses    10 of those 30
   stage 2 alone refuses    12 of those 30
   stage 1 + stage 2 refuse 12 of those 30
   SURVIVE BOTH             18  e.g. [4294967288, 4294967289, …]

== Q3b  what does STAGE 2 buy OVER stage 1? 2 value(s): [9223372036854775806, 9223372036854775807]
```

**Stage 2's entire marginal contribution over stage 1 is two values of
`to_read`** — `LONG_MAX - 1` and `LONG_MAX` — and what it buys there is that
`safe_emalloc`'s 64-bit check refuses them before `to_read + 1` can be
evaluated, which in stage 1's spelling is signed-overflow UB. **It removes ZERO
truncation faults in `[1, LONG_MAX - 2]`**, because `_safe_emalloc` checks in
64-bit `long` and then calls the truncating `_emalloc` at `zend_alloc.c:238`
(`PROTOCOL_PHP.md` §B says so; this is that sentence measured on a row).

**So R1h is stage 1 alone.** Shipping stage 1 + stage 2 would price a checked
multiply that buys nothing this row can observe, and it would make the R1-vs-R1h
column a comparison of two things at once.

⚠ **This is NOT `ph07`'s situation and the row does not claim the precedent.**
`ph07` ships a SUBSET of one commit; ph29 ships the WHOLE of one commit and
cites a second, later, separate commit that it does not ship.
`PROTOCOL_PHP.md` §C's *"a row that wants to do the same brings it to the
manager as a proposal"* does not apply, because nothing is being subsetted.

### §4b What the fix costs, measured

`results-php/ph29-recvfrom-alloc.json`, `Ir(kernel)`, O3 / isolated:

| | `small.bin` | `large.bin` |
|---|---:|---:|
| `c-gcc` R1 | 39 273 585 | 120 800 132 |
| `c-gcc-h` R1h | 39 322 352 (**+0.124 %**) | 120 828 536 (**+0.024 %**) |
| `c-clang` R1 | 28 335 859 | 86 864 573 |
| `c-clang-h` R1h | 28 273 143 (**−0.221 %**) | 86 835 243 (**−0.034 %**) |

⭐ **The guard is free, and on clang it is NEGATIVE-cost** — the same shape
`ph03` records (F30/F33): the check lets the compiler drop work elsewhere.
⚠ These four numbers are a comparison of two runs of one program and are the
only R1-vs-R1h figures this row has; every other column below is a
cross-language comparison and must not be read as a safety cost.

### §4c ⚠⚠ The fix is incomplete, and that is the row's headline

**`445daac3ab1a` does not remove this row's defect.** It refuses `to_read <= 0`;
the row's own UB-free trigger is `4294967295`, which is positive.
`controls/allocator.py` runs the shipped kernel with the guard applied and ASan
reports `heap-buffer-overflow` anyway. Neither does `6ac8ffdfea10`. The defect
survives every upstream change to this function through 5.6.0 and is closed only
by the allocator rewrite, which `PLAN_PHP.md` §4.3 retires as *"a multiplier on
every sizing defect in the engine, not a pattern of its own"*.

⭐ **And the guard is wrong in BOTH directions at once.** It also refuses
`to_read == 0`, which was never a fault: `emalloc(1)` is honoured, `recvd` is 0
and `read_buf[0] = '\0'` is in bounds. 5.0.0 returned `""` there; 5.1.0 returns
`false` and raises `E_WARNING`. **Over-broad on the safe side, under-broad on
the unsafe side, in one line of C.** `.memory-php/02-ladder.md` records one
upstream fix that was *"half dead and half incomplete"* and another *"half
wrong"*; this is a third shape.

⚠ **Why the shipped adversarial inputs are the arm the fix DOES close.**
`check.py` stage 7h requires R1h to be clean on **every** input, so an input the
fix does not close cannot be in `inputs/`. `.memory-php/02-ladder.md` F31 is
the standing rule and it says the surviving-hole evidence belongs in
`controls/` — which is where it is. ⚠ This is a real limitation of the gate,
not of the row, and it means **a green gate on this row does not mean the
upstream fix is complete.**

---

## §5 The two limbs, and why R1h closes neither

`ph16` has exactly one limb and it is a write. This row has **two**, and both
are upstream's:

* the **write** — `php_stream_read` at `:323` copies `min(available, to_read)`
  bytes into a block of `real_size`, and `:332` writes the NUL at `read_buf[recvd]`;
* the **read** — `RETURN_STRINGL(read_buf, recvd, 0)` at `:340` hands the
  engine a zval string of length `recvd` over the same block.

`spec.md`'s `cwe_note` says so; `provenance.cwe` stays **CWE-787** because that
is what `index.csv` records and the write is the primary limb.

⚠ `ph03`'s shape, not `ph16`'s — and unlike `ph03`, where R1h closed the write
and left the read, here **R1h closes neither at the row's trigger** (§4c).

---

## §6 What R2–R5 are, and the reading a reviewer may disagree with

`.memory-php/02-ladder.md`: *"R2–R5 are not ports of R1h … the Rust rungs carry
whatever is actually memory-safe."* Here that is unusually sharp, because a
Rust rung built to `445daac3ab1a` **would still write out of bounds**.

**Every rung — C and Rust alike — computes PHP's own allocator arithmetic
explicitly:**

```
size      = to_read + 1                                streamsfuncs.c:321
real_size = ((size + 7) & ~7) stored in 32 bits        zend_alloc.c:129/:135
recorded  = size stored in 31 bits                     zend_alloc.h:53
```

`real_size` is **not a modelling choice**: it is the number of bytes
`_emalloc` returns (`zend_alloc.c:182` allocates `header + padding +
real_size`). R1 then hands the transport `to_read` — the number it asked for —
and the gap between the two is the entire defect. The Rust rungs bound the copy
by `read_buf.len()`, which is `real_size`, and there is no gap. **So R1..R5
differ in exactly one line**, `if n > cap { n = cap; }`.

⚠⚠ **THE ALTERNATIVE READING, STATED SO A REVIEWER CAN TAKE IT.** One can argue
the safe port of `emalloc(to_read + 1)` is `vec![0u8; to_read + 1]`, since
Rust's allocator has no 32-bit truncation, and that safe Rust therefore simply
does not have this bug. **That is true and it is unmeasurable**: on the row's
own trigger it allocates 4 GiB per kernel call, and on the shipped
`adversarial-trunc.bin` it asks for 18.4 EB and aborts. The shipped reading
isolates the defect; the alternative reading answers a different question
(*"does Rust's allocator truncate?"* — no) and cannot be put on a ladder.

⚠ **`vec![0u8; cap]` ZEROES and `emalloc` does not.** All four Rust rungs pay
that and neither C rung does. It is the same spelling `ph03` and `ph07` ship, it
is inside `real_size` bytes per call, and §8 prices it rather than hiding it.

---

## §7 `_FORTIFY_SOURCE` — checked on this row, not inherited

`RECAP_PHP.md` F56 is one row old and says explicitly not to inherit its answer:
`ph16`'s `FD_SET` became `__fdelt_chk` at `-O3` and cost **+60.6 %**.
`controls/fortify.py`, four arms:

```
== A  is -D_FORTIFY_SOURCE injected, with build.py's own flags?
   gcc    -O0  -> FORTIFY_IS_NOT_DEFINED
   gcc    -O3  -> FORTIFY_IS_DEFINED
   clang  -O0/-O3 -> FORTIFY_IS_NOT_DEFINED

== B  does ph29's OWN kernel object carry a fortify _chk symbol?
   -> 0 fortify check(s) across all 8 configurations

== C  MUST-FIRE: the same detector on a destination gcc CAN bound
   gcc    -O3  fortify _chk: ['__memcpy_chk'] <- MUST FIRE

== D  WHY: the mechanism, isolated. Two variants, one difference.
   gcc -O3  V=1  (php_shim_emalloc's shape: a size-class CACHE arm AND a malloc arm)
            fortify _chk: NONE
   gcc -O3  V=0  (the same function with the CACHE ARM DELETED)
            fortify _chk: ['__memcpy_chk']

VERDICT: ph29's kernel carries 0 fortify check(s) -- NO #undef is needed
```

⭐⭐ **AND THE MECHANISM IS A FINDING ABOUT PHP, NOT ABOUT GCC.**
`php_shim_emalloc` has two return paths — the size-class cache
(`zend_alloc.c:150-168`) and `malloc` (`:182`) — so the pointer reaching
`memcpy` is a PHI of two allocations and `__builtin_dynamic_object_size` of that
is unknown. **PHP 5.0.0's own size-class cache defeats a 2024 compiler
mitigation**, and it is the same feature that makes
`crashes_pristine_5_0_0 = False` unreliable (`PROTOCOL_PHP.md` §B1.1). Arm D is
a two-variant differential: the ONLY difference between them is the cache arm.

⚠ Every probe uses a **runtime** length, never a literal (F52). ⚠ Arm C exists
because arm B's silence is otherwise indistinguishable from a broken detector —
and the detector's first draft counted `__stack_chk_fail`, which is the stack
protector, is present at `-O0` where fortify is off, and would have reported the
opposite of the truth.

`spec.md` **forbids** a `#undef` here, for the reason that adding one would
suppress a mitigation that is not present and make this finding unfalsifiable.

---

## §8 The ladder, and what in it is NOT a safety effect

`results-php/ph29-recvfrom-alloc.json`, `Ir(kernel)`, **O3 / isolated**,
within-row ratios only (`.memory-php/03-numbers.md` forbids any comparison with
a `pNN` figure, and forbids differencing two php runs taken in two shells):

| cell | `small.bin` | vs `unsafe` | `large.bin` | vs `unsafe` |
|---|---:|---:|---:|---:|
| `c-gcc` (R1) | 39 273 585 | +57.4 % | 120 800 132 | +41.6 % |
| `c-gcc-h` (R1h) | 39 322 352 | +57.6 % | 120 828 536 | +41.7 % |
| `c-clang` (R1) | 28 335 859 | +13.6 % | 86 864 573 | +1.9 % |
| `c-clang-h` (R1h) | 28 273 143 | +13.3 % | 86 835 243 | +1.8 % |
| `safe_naive` (R2) | 28 068 358 | **+12.5 %** | 90 821 295 | **+6.5 %** |
| `safe_tuned` (R3) | 23 441 029 | **−6.1 %** | 79 788 966 | **−6.4 %** |
| `unsafe` (R4) | 24 951 895 | 0 | 85 283 038 | 0 |
| `verus` (R5) | 24 951 895 | **0, byte-identical** | 85 283 038 | **0, byte-identical** |

⚠⚠⚠ **`R3ship − R4ship` IS NEGATIVE, SO NO FIGURE IN THIS ROW IS A
`fixed-R4 bound`.** Safe-tuned measures **6.1 % / 6.4 % CHEAPER than unsafe**.
That is `ph16`'s situation exactly (`.memory-php/02-ladder.md`), and whether it
is a real non-monotone ladder or a spelling artefact is **unknown**, because
`controls/spellings.py` was not built. ▶ **THE DEBT IS DECLARED, NOT
DISCHARGED**: `TASK_PHP_027` §5 rules `controls/spellings.py` out of this task
and `TASK_PHP_028` discharges it across `ph03` + `ph16`; **ph29 now makes three
rows owing it and is the second whose R3−R4 gap is negative.**

⚠⚠ **TWO THINGS IN THAT TABLE ARE NOT SAFETY EFFECTS AND WILL BE MISREAD AS
SUCH.**

1. **`c-clang` beats `c-gcc` by 27.9 % / 28.1 %**, which is larger than every
   other movement in the row. `ph03` records the same warning at 15.4 %.
2. ⚠⚠⚠ **C IS SLOWER THAN EVERY RUST RUNG HERE, AND IT IS THE ALLOCATOR
   MODEL RATHER THAN THE LANGUAGE.** The C rungs run a faithful
   `php_shim_reset()` (which walks 11 cache classes), one `_emalloc`, one
   `_efree` and one `php_shim_shutdown()` (which walks the 11 classes again plus
   the live list) **per kernel call**; the Rust rungs run one `vec![0u8; cap]`
   and one drop. **The C rungs are paying for PHP's request boundary and the
   Rust rungs are not**, because there is nothing in a memory-safe translation
   for the size-class cache to be. **Do not read this row's C-vs-Rust column as
   a cost of C.**

### §8a The marginal, decomposed rather than labelled

`work_per_call` is the **window**, 550 and 4076 bytes. `inputs/gen.py` draws
both `navail` and `to_read` relative to `n_pay = stride − 12`, so the copy, the
fold **and** the allocation all scale with the denominator. ⚠ **There is also a
large FIXED per-call term and it is an allocator term** — `reset` + `emalloc` +
`efree` + `shutdown` happen on every call whatever the stride. The marginal is
therefore *not* a pure copy rate, and the ratio between the two probe shapes
shows it: `c-gcc` runs 39.3 M `Ir` at stride 550 × 25 000 calls and 120.8 M at
stride 4076 × 12 000 calls, i.e. **1 571 `Ir`/call at 550 B and 10 067 at
4076 B** — an 6.4× rise for a 7.4× rise in work, the shortfall being the fixed
term.

---

## §9 What the corpus reaches, and what it structurally cannot

`inputs/gen.py::_check_span` refuses to write a corpus that misses an arm, and
`model.py::selfcheck` check 2 re-asserts the same table **over the calls the
driver actually makes** (`PROTOCOL_PHP.md` §A2a, both rules). The arms:

* both sides of the **size-class cache** — `real_size <= 87` is pushed onto a
  per-class LIFO by `_efree` and never returned to `malloc`
  (`zend_alloc.c:270-279`); above it goes back to `malloc`. **That is the branch
  §B1.1 is about** and a corpus on one side of it exercises half the allocator;
* both arms of `if (recvd >= 0)` at `:328` — and the failing one is where 5.0.0
  **leaks** `read_buf`, which the kernel reproduces and `php_shim_shutdown()`
  reclaims at the request boundary;
* both arms of `if (zremote)` at `:315` and of
  `if (zremote && Z_STRLEN_P(zremote))` at `:329`;
* both directions of the transport's clamp (`to_read < navail` and not);
* `navail == 0` and `navail == n_pay`.

⚠⚠ **AND NEGATIVELY: no benign window may have `to_read <= 0` (the guard would
fire and R1h would stop agreeing with R1) or truncate (that is an
out-of-bounds write) or equal `LONG_MAX` (`to_read + 1` is then
signed-overflow UB).** All three are asserted.

⭐ **`inputs/` STRUCTURALLY CANNOT span the parameter the defect switches on**,
and that is worth stating because it is the sharpest instance of A2a rule 2 so
far: a *benign* corpus may not contain a truncating window **at all**, so the
model's synthetic sweep is the only thing that drives both sides of
`zend_alloc.c:135`. It spans `to_read ∈ {0, ±1, ±2, 7, 8, 86, 87, 88, 2^31−1,
2^31, 2^32−2, 2^32−1, 2^32, 2^33−1, LONG_MAX, LONG_MIN, −2^32−1, −2^32, −8, −9,
2^32−9, 2^32−8}` × `ctl ∈ 0..3`, plus a `navail` family and five strides — 176
synthetic windows, three implementations, on every one of the six inputs.

---

## §10 The proof

```
$ ./verus_run.py patterns-php/ph29-recvfrom-alloc/verus.rs
verification results:: 10 verified, 0 errors
$ ./verus_run.py patterns-php/ph29-recvfrom-alloc/verus.rs --cfg slb_twin
verification results:: 15 verified, 0 errors
```

**What is proved is a VALUE postcondition:**
`r == recv_fold(buf@, off as int, len as int)`, and `model.py` re-derives the
same `u64` from two further decompositions.

⚠⚠ **THE OBLIGATION THIS ROW IS ABOUT IS A BOUND BETWEEN TWO DERIVED
QUANTITIES, NOT AN INDEX AGAINST A CONSTANT — and that is its difference from
`ph16`.** `ph16`'s is `w < NW` on a straight-line path, with `NW` a platform
constant. Here `cap` is `rs_of(tr + 1)`, a **32-bit truncation of the number the
program asked for**, and every unchecked destination access is licensed by
`n <= cap`. The proof has to carry `rs_of` through the whole kernel; the
`decreases` clauses are the easy part.

**Four trusted `unsafe` items, four verified twins, and they rest on two
independent facts:**

| item | licensed by | which is |
|---|---|---|
| `vcopy_unchecked` | `n <= cap` | **PHP's missing comparison** |
| `vset_unchecked` | `recvd < cap` | ditto |
| `vget_unchecked` | `i < recvd <= cap` | ditto |
| `get_unchecked` | `off + len <= buf.len()`, `16 <= len`, `navail = want % (n_pay+1)` | **the harness's own contract**, not PHP's |

⚠ Keeping the two apart is the point: delete the clamp and the first three lose
their preconditions while the fourth is untouched.

**`lemma_foldb_ext` is the file's only lemma** and it exists because the exec
code folds the DESTINATION while the spec folds the WINDOW. `vcopy_unchecked`'s
`ensures` names the whole post-state in three clauses — length preserved, prefix
copied, suffix untouched — and the third is what lets the NUL store be
discharged without the copy having been allowed to scribble on the tail.

### §10a The mutants — `controls/negatives.py`

```
  must-NOT-fire  baseline     (10, 0)  PASS
  must-FAIL      noclamp      9 verified, 1 errors  PASS
  must-FAIL      nonul        9 verified, 1 errors  PASS
  must-FAIL      weakreq      14 verified, 1 errors  [--cfg slb_twin]  PASS
  must-FAIL      wrongrs      9 verified, 1 errors  PASS
  must-FAIL      wrongfold    7 verified, 3 errors  PASS
  must-FAIL      tautology    9 verified, 1 errors  PASS
  must-VERIFY    tautology-un 10 verified, 0 errors  PASS
  must-FAIL      zerobody     8 verified, 1 errors  PASS
RESULT: PASS (0 problem(s))
```

⭐ `wrongrs` is the one that matters most: it drops the `+ 7` from the **spec**
function `rs_of` and leaves the exec code alone. It FAILS, so the postcondition
really is pinning `zend_alloc.c:132`'s rounding and not merely bounding an
index. ⚠ `tautology-un` VERIFIES, which is the vacuity baseline — a tautological
`ensures` plus a deleted consuming assert is worth `10 verified, 0 errors`, and
that is what a green count is worth on its own.

### §10b The proof budget — there isn't one, and that is the result

⭐⭐ **`ph29` SHIPS NO `#[verifier::rlimit]` AT ALL.** `ph16` needs 30 and
`ph07` needs 9. Bisected on this box, both builds, every step:

```
  rlimit(30 ) plain: 10 verified, 0 errors    twin: 15 verified, 0 errors
  rlimit(10 ) plain: 10 verified, 0 errors    twin: 15 verified, 0 errors
  rlimit(4  ) plain: 10 verified, 0 errors    twin: 15 verified, 0 errors
  rlimit(2  ) plain: 10 verified, 0 errors    twin: 15 verified, 0 errors
  rlimit(1  ) plain: 10 verified, 0 errors    twin: 15 verified, 0 errors
  no attribute  plain: 10 verified, 0 errors  twin: 15 verified, 0 errors
```

⚠ **The row's first draft shipped `#[verifier::rlimit(30)]`, copied from
`ph16` by analogy, with a paragraph explaining why 30 was the right budget.**
Nothing had been bisected. **An unearned budget override is a claim about proof
cost**, and this row's actual claim is the opposite one: the obligation is a
single bound between two derived quantities, `n <= cap`, and once `cap` is
named there is nothing for a solver to search. The attribute is gone and this
paragraph replaces the one that defended it. `.tasks/PROTOCOL.md` rule 14 with
the roles reversed — a premise nobody ran.

---

## §11 ⚠ The kernel-overlap number, and what I think of it

`PROTOCOL_PHP.md` §F9 makes this a person's judgement rather than the tool's,
and asks for it here. **This is the first `narrowed` row it has ever been asked
about on real evidence** — `ph00-smoke` declares `php_provenance: false`, so the
floor never fired on anything but a fixture.

```
per-span overlap: span0 20% (6/30), span1 0% (0/9), span2 0% (0/4)
kernel overlap 14% (6/43 excerpt lines in kernel.c, kernel.h, kernel_hardened.c)
tier=narrowed is expected to clear 25% -- REPORTED, NOT ENFORCED
1 preprocessor condition(s) this heuristic CANNOT evaluate: ['#ifndef PH29_KERNEL_H']
```

**14 % against a 25 % expectation. I think the number is right, the tier is
right, and the expectation does not fit this shape of row.** The argument, so a
reviewer can disagree with it rather than take my word:

### §11a The six that match, and the twenty-four that do not — enumerated

⚠⚠ **I ENUMERATED THESE RATHER THAN DESCRIBING THEM, BECAUSE MY FIRST DRAFT
OF THIS SECTION DESCRIBED THEM AND WAS WRONG.** It said the matched lines were
*"exactly the four the defect is made of"*. They were not: two of the four were
declarations, and **`read_buf = emalloc(to_read + 1);` — the row's own defect
line — was a MISS.** That is `PROTOCOL.md` rule 14's shape inside a section
about a metric.

Matched (6 of 30):

```
long to_read = 0;
char *read_buf;
int recvd;
read_buf = emalloc(to_read + 1);
if (recvd >= 0) {
read_buf[recvd] = '\0';
```

⭐ **Two of those six are there BECAUSE of the miss.** Fixing the cause was a
fidelity gain, not a metric game: the kernel now spells the allocation
`read_buf = emalloc(to_read + 1);` through a `#define` redirect at the top of
the file — `ph03`'s sanctioned spelling — instead of
`(char *)php_shim_emalloc((size_t)(to_read + 1))`, and declares `long to_read =
0;` as `:304` does. **Both shipped benign checksums are byte-identical across
the change** (`5917653902369662825` / `3996271157387841948`), so it is a rename
and nothing else, and `spec.md`'s ledger itemises it as a `substitution`.

Unmatched (24 of 30), grouped:

| what | lines | why it is gone |
|---|---|---|
| zval / wrapper machinery | `zval *zstream, *zremote = NULL;`, `php_stream *stream;`, `zend_parse_parameters(…)`, `php_stream_from_zval(…)`, `zval_dtor(zremote);`, `ZVAL_NULL(zremote);`, `Z_STRLEN_P(zremote) = 0;`, `Z_TYPE_P(zremote) = IS_STRING;`, `RETURN_STRINGL(…)`, `RETURN_FALSE;`, `TSRMLS_CC);` | **this is what `narrowed` MEANS** |
| the `magic_quotes_runtime` arm | `if (PG(magic_quotes_runtime)) {`, the two `Z_*_P(return_value)` lines, `php_addslashes(…)`, `return;`, `} else {` | a `php.ini` setting, not attacker data; declared |
| the two `ctl`-bit tests | `if (zremote) {`, `if (zremote && Z_STRLEN_P(zremote)) {` | the ARMS are kept; the zval test is not |
| the transport call | `recvd = php_stream_xport_recvfrom(…)` and its three continuation lines | substituted, with `extra_spans[0]` pinning the original and `controls/oracle.py` as the differential |
| `long flags = 0;` | | `flags` is not attacker data on this path and the row does not carry it |

**So the unmatched 24 are the wrapper, and the tier's whole definition is that
the wrapper comes off.**

### §11b ⚠⚠ Citing more spans makes the statistic worse

The denominator is the **union**, 43 lines. `span1` is
`transports.c:381-392` and `span2` is `zend_alloc.c:128-137` — **the truncation
itself, which is the single most important citation in the row** — and both
score 0, because `span1` is substituted and `span2` lives in
`c/emalloc_shim.h`, which the heuristic does not read.

> **A row that cited only its defect site would score 20 %. Citing the two
> spans that make its claim checkable drops it to 14 %.**

That is a property of the metric, not of this row, and it is worth recording
because the demotion from a floor to a report (`TASK_PHP_008` §2) put the
judgement on a person and this is the first row where the person has to make
it. ⚠ It also means the 25 % expectation is not comparable between a row with
one span and a row with three.

### §11c The tier is not the problem

`modelled` is the honest answer for a **re-expressed mechanism**, and this
mechanism is not re-expressed: `long to_read = 0;`,
`read_buf = emalloc(to_read + 1);`, the `size_t` widening of `to_read` as the
transport's `buflen`, `if (recvd >= 0)` and `read_buf[recvd] = '\0';` are all
upstream's own text, and they are the whole of the defect.
`UPSTREAM_001.md` §6 independently checked ph29's tier against the M4 frame
test and agreed with `narrowed` — it is one of the two rows in that table that
were already right.

⚠ The residual is **one** unevaluable conditional and it is the header guard,
so the number is not being distorted by dead-code accounting.

---

## §11d The four trusted items, argued one at a time

`check.py` stage 5c-twin requires a written, per-item argument for the three
things no stage of the gate can judge, and prints it for a human. Each section
below is that.

---

SLB-TRUSTED-ARGUMENT verus.rs get_unchecked

**(a) Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*v.get_unchecked(i)`; the twin's body is `v[i]`, the same load
with the check. Verus checks that load's bound against the same `requires`.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes. The body performs exactly one unchecked operation, a
read at `i`, and the `ensures` `r == v@[i as int]` names its whole result. A
body that read some other index would violate it. ⚠ **What it does not exclude
is a SECOND unchecked read added to the same body** — `TASK_009_REVIEW`'s x4 —
which would be UB without moving the post-state. That is the residual for every
read wrapper in this project; `identity` and Miri are what cover it.

⚠ **This item is licensed by a fact that is not in PHP at all**, and keeping
that apart from the destination items is the point of §10's table: the window
reads rest on the driver's `off + len <= buf@.len()` and `16 <= len`, plus
`navail = want % (n_pay + 1)`. Delete the row's clamp and this item is
untouched.

**(c) Does the clause mean the same in both configurations?** Yes. `v@.len()`
is Verus's own view of a slice, `i` is a concrete `usize`, and neither mentions
anything `#[cfg]`-gated. The gate additionally forbids the token `slb_twin`
anywhere in the shipped configuration's reachable code.

---

SLB-TRUSTED-ARGUMENT verus.rs vget_unchecked

**(a)** Yes — `*v.get_unchecked(i)` against `v[i]` on a `&Vec<u8>`, the same
load with the check.

**(b)** Yes, and the argument is `get_unchecked`'s. ⭐ **What is different is
what this item MEANS here**: it is `RETURN_STRINGL(read_buf, recvd, 0)` at
`streamsfuncs.c:340`, i.e. **the second limb of the defect**. In R1 the same
read runs off the end of the block, because the engine is handed a string of
length `recvd` over a buffer that is not that long. So this wrapper's
`requires i < v@.len()` is the *read* half of what PHP does not check, exactly
as `vcopy_unchecked`'s is the *write* half.

**(c)** Yes; `Vec`'s view is not `#[cfg]`-dependent.

---

SLB-TRUSTED-ARGUMENT verus.rs vset_unchecked

**(a)** Yes. The unchecked operation is `*v.get_unchecked_mut(i) = x`; the
twin's body is `v.set(i, x)`, which is vstd's checked store with the identical
post-state.

**(b) ⚠ This is the one that matters for a WRITE wrapper**, and the answer is
yes as the body stands. The `ensures` is the WHOLE post-state,
`final(v)@ == old(v)@.update(i as int, x)`, not merely `final(v)@[i] == x`. A
body that also clobbered `v[i + 1]` would violate it and could not verify; so
would a body that stored something other than `x`, or at another index. ⚠ What
it does not exclude is an unchecked *read* added to the same body.

⚠ `x: u8` is a **pure value** and carries no precondition, which the gate
reports as `tcb-unsafe` — `verus.rs:293 vset_unchecked's requires constrains
nothing about ['x']`. That is correct and deliberate: the definedness of the
store depends on `i` and on nothing about the byte written. `spec.md` justifies
it and the gate prints it rather than failing it.

⭐ **This item is `streamsfuncs.c:332` — `read_buf[recvd] = '\0';` — which in
C carries no contract at all.** The whole defect is that C has nowhere to write
`recvd < cap` and no one to check it.

**(c)** Yes. `old(v)`/`final(v)` are Verus's own `&mut` forms and `u8` is
concrete.

---

SLB-TRUSTED-ARGUMENT verus.rs vcopy_unchecked

**(a) Is the twin's body the right checked stand-in?** Yes, and it is the one
item here where "the same operation with the check" is not a one-liner. The
unchecked operation is
`core::ptr::copy_nonoverlapping(s.as_ptr().add(from), v.as_mut_ptr(), n)`; the
twin's body is a `while i < n { v.set(i, s[from + i]); }` loop with an
invariant, which is the same byte-for-byte move performed through checked
accesses. ⚠ **A `copy_from_slice` twin would have been WRONG**, because it
carries a length-equality panic the unchecked form does not have and would have
been proving a different obligation.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** ⚠⚠ **This is where the gate corrected me, and the correction
is worth more than the clause was.** The item shipped with THREE clauses —
length preserved, prefix copied, **suffix untouched** — and a comment saying
the third *"is what a bulk-copy contract most easily gets wrong, and without it
the NUL store below could be discharged by a body that had already scribbled
over the tail."* `check.py` stage 5b deleted it and the file still gave
`10 verified, 0 errors`: **nothing in this kernel ever reads past `recvd`, so
the clause was an axiom nothing depended on.** It is gone.

So the honest answer to (b) is: **the `ensures` is complete for the part of the
post-state this proof uses, and NOT for the whole object.** A body that copied
the right `n` bytes and then scribbled at `n + 1` would satisfy the contract.
That is UB and the proof cannot see it. **What covers it is Miri** — which is
required on this row for exactly this reason (`spec.md`'s `miri.reason`) — and
`identity: exact`, which pins R4 and R5 to the same machine code so the wrapper
cannot differ between the measured and the proved configuration.

⚠ **The residual is bigger here than for the other three items**, because this
is the only wrapper whose body is a bulk operation rather than a single
indexed access, and it is stated rather than papered over.

**(c) Does each clause mean the same in both configurations?** Yes.
`old(v)@.len()`, `s@.len()` and `s@[from + j]` are Verus views of a `Vec` and a
slice; `n` and `from` are concrete `usize`. The twin needs one extra ghost fact
the shipped item does not — `s@.len() <= usize::MAX`, so `from + i` cannot
overflow in the checked loop — and that is an artefact of the twin's body, not
a difference in what the contract says.

---

## §12 The rule 6 addendum — every declaration re-read against the measurement

`PROTOCOL.md` rule 6 protects against a declaration edited **after** measuring.
It does nothing about a declaration measurement has **falsified** (`p46`, F54).
So, before shipping, every declaration in `spec.md` and every rung doc comment
was re-read against the record. **Nine were wrong and are corrected — and the gate found FOUR of them, which is what a gate is for:**

-3. ⚠⚠⚠ **`idiom.forbidden[0]` OPENED BY BACKTICKING `to_read + 1` — THE
   EXPRESSION IT EXISTS TO PROTECT — while its own last sentence warned against
   exactly that.** In a `forbidden` entry every backticked span is a banned
   token, so the gate refused the row twice, once per C rung, for spelling the
   thing the entry protects. ⚠ **I wrote the warning into the entry and then
   did it in the entry's first four characters.** `ph16`'s first draft lost
   fourteen (spelling × rung) obligations to the same shape; **a warning in the
   place where the mistake is made does not prevent the mistake**, and that is
   worth more than the warning.
-2. ⚠ **After the fix, `forbidden` had NO backticked token at all**, so the
   list pinned nothing mechanically — a quieter version of the same defect.
   `forbidden[2]` and `[3]` now carry one genuinely-absent token each
   (`calloc`, `#undef _FORTIFY_SOURCE`), verified absent from every audited
   source before being written.
-1. ⚠⚠ **`vcopy_unchecked` shipped a THIRD `ensures` clause with a comment
   arguing it was the important one.** `check.py` stage 5b deleted it and the
   file still verified: it was an axiom nothing depended on. Gone, and §11d
   states the larger residual that leaves.
0. ⚠⚠ **Two `idiom.required` entries carried a `why` key.** The gate's schema
   admits only `c` and `rust`, so **that text pinned nothing in either
   language** while reading like a pin. Folded into the `c`/`rust` strings.
1. ⚠⚠ **`verus.rs` shipped `#[verifier::rlimit(30)]`, copied from `ph16` by
   analogy, with a `spec.md` note defending 30 as the right budget. Nothing had
   been bisected.** It verifies with the attribute deleted — §10b. Removed, and
   the note now records the bisection instead.
2. ⚠ **`identity[0]` said `O3: "norel"`.** Reasoned, not measured: `vec![0u8;
   cap]` reaches the allocator through a PLT entry, so the two cells "must"
   differ in relocations. **The record says `md5_fn` is `a7adc5d4e32f` in
   BOTH** — `exact`. Corrected, and the `contract_sha256` move is disclosed in
   §0.
3. ⚠ **`identity[0]` said `O0: "differ"`**, by analogy with `ph03`, `ph07` and
   `ph16`. The record says the two O0 cells have the **same** instruction count
   (406), the same size (2 354 B) and the same `md5_fn_norel` — they differ only
   in relocations. `norel`. **The analogy was to three rows and it was still
   wrong**, because this kernel's helpers are called from inside a loop rather
   than inlined at one site.
4. ⚠⚠ **`NOTES.md` §1 pasted a STORED probe log under a shell prompt**, as
   though it were a fresh run. Re-run for real; §1 says so and shows the
   warning the stored log does not have.
5. ⚠⚠ **`inputs/gen.py`'s docstring claimed a 5-byte overflow keeps the process
   alive** — a plausible reading of glibc's chunk layout that nobody had run.
   **All four R1 cells abort** with `malloc(): invalid size (unsorted)` on the
   shipped adversarial inputs. Corrected in `gen.py`, `controls/allocator.py`
   and `controls/oracle.py`; the boundary is now measured by `oracle.py`'s sweep
   (silent at `navail <= 1` in that program, `corrupted top size` from 4 up)
   rather than asserted.

✅ Everything else re-read clean. The `why` prose in `spec.md` was written
**last**, after the record existed, and every numeral in it — `2^32`,
`4294967295`, the two commit shas, the 807-byte patch size, *"eight (compiler ×
opt × mode) configurations"*, *"no `__memcpy_chk`"* — was re-derived from the
run that produced this file rather than from the draft that preceded it.

---

## §13 Adversarial behaviour, per rung

Measured on the shipped binaries, O3 / isolated (`check.py` stage 4 records the
same thing across all 32 cells):

| rung | `adversarial-trunc.bin` | `adversarial-neg.bin` |
|---|---|---|
| `c-gcc`, `c-clang` (R1), O0 and O3 | `rc=134`, `malloc(): invalid size (unsorted)` | same |
| `c-gcc-h`, `c-clang-h` (R1h) | `rc=0`, `1176667978365039616` | same |
| `safe_naive` … `verus` (R2–R5) | `rc=0`, `2718404719748941824` | same |

⭐ **Three behaviours, not two**, and `spec.md`'s `note` says so: R1 corrupts
the heap and dies in the allocator, R1h returns its refusal sentinel, R2–R5
clamp. ⚠ The two adversarial inputs produce **identical** output in every rung,
because they differ only in the *request size* (`2^64 − 2^32` vs `0`) and both
truncate to `real_size = 0`. Their difference is entirely in what a
**substituted** allocator does, which is `controls/allocator.py`'s business and
not the gate's — and that is why the pair is shipped.

---

## §14 What is NOT here

* **`controls/spellings.py`** — ruled out of this task by `TASK_PHP_027` §5 and
  owed by `TASK_PHP_028`. §8 declares the debt. ⚠ **Three of four built rows
  now owe it.**
* **A comparison with any `pNN` figure.** `.memory-php/03-numbers.md` forbids
  it; nothing here does it.
* **A claim that the corpus's `crashes_pristine_5_0_0` column says anything.**
  `PROTOCOL_PHP.md` §B1.1 forbids using it as a filter and this row did not.
* **Any measurement of PHP itself.** Nothing here runs PHP; every figure is
  about the extracted kernel under the shim, and `controls/oracle.py` says in
  its own text what its differential can and cannot catch.
