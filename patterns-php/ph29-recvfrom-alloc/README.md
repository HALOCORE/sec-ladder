# ph29 — `emalloc(to_read + 1)`, where the allocator truncates the size

**PHP 5.0.0, `ext/standard/streamsfuncs.c:300-345`
(`PHP_FUNCTION(stream_socket_recvfrom)`), corpus row CRASH-097, tier
`narrowed`, CWE-787.** Row 4 of the PHP programme, and the first outside the
spatial families `S1`/`S2` in the sense that matters here: the defective
quantity is not an index, it is a **size the allocator silently changes**.

```c
long to_read = 0;                                              /* :304 */
zend_parse_parameters(..., "rl|lz", &zstream, &to_read, ...)   /* :309  USERLAND */
read_buf = emalloc(to_read + 1);                               /* :321  THE DEFECT */
recvd = php_stream_xport_recvfrom(stream, read_buf, to_read,   /* :323  ...to_read */
                                  flags, NULL, NULL, ...);
read_buf[recvd] = '\0';                                        /* :332  THE FAULT */
```

`emalloc` is handed `to_read + 1` and returns a block of **`real_size`** bytes,
because `Zend/zend_alloc.c:129` declares `unsigned int real_size` and `:135`
assigns a 64-bit `size_t` expression into it. The caller then hands the
transport **`to_read`** — the number it *asked* for. **Nothing in PHP compares
the two.** `stream_socket_recvfrom($s, 4294967295)` asks for 4 GiB, gets a
24-byte block, and receives into it.

## Why this row exists

⚠⚠⚠ **It is the one row in the corpus that cannot pass without
`common-php/emalloc_shim.h`.** `PLAN_PHP.md` §4.3 has warned since Phase 0 that
a substituted allocator is not neutral — an earlier effort dropped plain
`malloc` in and reported a real defect as unreachable — and `RECAP_PHP.md` F6
records the shim itself *inventing* a defect once. Neither claim could be
falsified, because no row so far would have behaved differently under any
allocator. This one does, and `controls/allocator.py` runs it both ways:

| `to_read` | shim (PHP 5.0.0's `_emalloc`) | plain `malloc` |
|---|---|---|
| `4294967295` | **heap-buffer-overflow** | the 4 GiB request is **honoured** — no defect |
| `-4294967297` | **heap-buffer-overflow** | the 18.4 EB request **fails** — PHP `exit(1)`s |
| `-1` | heap-buffer-overflow | heap-buffer-overflow — the one value the shim is *not* needed for |
| benign | clean | clean |

## Three results a reader should not miss

1. ⚠⚠ **The real upstream fix does not remove the defect.** `445daac3ab1a`
   (2004-07-28) adds `if (to_read <= 0) RETURN_FALSE;` — exactly what its own
   subject says, *"when length parameter has a negative value"* — and the row's
   trigger is positive. The 2006 follow-up `6ac8ffdfea10` swaps in
   `safe_emalloc` and does not remove it either. Measured over the whole
   `to_read` domain: **stage 2's entire marginal contribution over stage 1 is
   two values.** `NOTES.md` §4, `controls/fix_scope.py`.
2. ⭐⭐ **PHP's own size-class cache defeats `-D_FORTIFY_SOURCE=3`.** gcc
   injects it at `-O3` and level 3 tracks allocation sizes — the exact check
   this row is about. It emits **no** `__memcpy_chk` here, in any of eight
   configurations, because `php_shim_emalloc` returns a pointer with two
   provenances. Delete the cache arm and the check appears. `NOTES.md` §7,
   `controls/fortify.py` (with a must-fire control, so the silence is not a
   broken detector).
3. ⚠⚠ **`safe_tuned` measures 6.1 % / 6.4 % CHEAPER than `unsafe`**, so no
   figure in this row is a `fixed-R4 bound`. `ph16` is in the same position and
   `TASK_PHP_028` owes both. `NOTES.md` §8 — which also says, loudly, that the
   C rungs are slower than every Rust rung here because they run PHP's request
   boundary per call and the Rust rungs have nothing to run.

## The ladder

| rung | file | what it is |
|---|---|---|
| R1 | `c/kernel.c` | PHP 5.0.0, narrowed. The bug. |
| R1h | `c/kernel_hardened.c` | + `445daac3ab1a`, the whole commit, sha-pinned |
| R2 | `safe_naive.rs` | safe Rust, index by index |
| R3 | `safe_tuned.rs` | safe Rust, `copy_from_slice` + iterator fold |
| R4 | `unsafe.rs` | `get_unchecked` / `copy_nonoverlapping` |
| R5 | `verus.rs` | R4 + the proof — `10 verified, 0 errors`, **no `rlimit` override** |

Every rung computes PHP's own allocator arithmetic explicitly; **they differ in
one line**, `if n > cap { n = cap; }`. `NOTES.md` §6 states the alternative
reading a reviewer may prefer, and why it is unmeasurable.

## Running it

```sh
python3 patterns-php/ph29-recvfrom-alloc/inputs/gen.py     # the .bin are gitignored
python3 harness-php/gate.py ph29-recvfrom-alloc            # never harness/check.py directly
python3 patterns-php/ph29-recvfrom-alloc/controls/allocator.py
python3 patterns-php/ph29-recvfrom-alloc/controls/fix_scope.py
python3 patterns-php/ph29-recvfrom-alloc/controls/fortify.py
python3 patterns-php/ph29-recvfrom-alloc/controls/oracle.py
python3 patterns-php/ph29-recvfrom-alloc/controls/negatives.py
python3 patterns-php/ph29-recvfrom-alloc/controls/spellings.py --verus
python3 patterns-php/ph29-recvfrom-alloc/controls/inside_share.py   # NOTES.md §15
```

⚠ **A green gate here does not mean the upstream fix is complete** — it cannot,
because `check.py` stage 7h requires R1h to be clean on every input, so the
inputs are the arm the fix *does* close. The surviving hole is in `controls/`,
which is where `.memory-php/02-ladder.md` F31 says that evidence belongs.
