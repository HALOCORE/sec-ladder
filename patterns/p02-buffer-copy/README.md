# p02 — length-prefixed buffer copy

The first pattern in this repo that models a **real memory-safety bug**, and the
first whose result is a security claim rather than a calibration number.

## The kernel

Copy one length-prefixed record out of a source blob into a fixed-capacity
destination buffer, and return a checksum of what was copied.

```
kernel(src, src_off, dst):
    len = little-endian u16 at src[src_off]
    if the record fits:  dst[0..len) := src[src_off+2 .. src_off+2+len)
                         return wrapping sum of dst[0..len)
    else:                return 0, dst untouched
```

`len` is attacker data — a `u16` prefix can say 65 535 and the destination is 64
bytes. The exact contract, the payload layout and the machine-readable pins are
in `spec.md`; the findings are in `NOTES.md`.

## The C bug

`c/kernel.c` is CWE-787 (out-of-bounds write) as it is actually written:

```c
size_t len = (size_t)src[src_off] + 256 * (size_t)src[src_off + 1];
(void)src_len;   /* the sizes are right here ...          */
(void)dst_cap;   /* ... and this rung never looks at them */
memcpy(dst, src + src_off + 2, len);
```

Note what it is *not*: it is not C being unable to know the buffer sizes. Both
are parameters. R1 has them and trusts the wire instead — which is the common
shape of the CVE and is what makes the comparison honest.

## The six cells

| cell | what it is |
|---|---|
| **R1** `c-gcc` / `c-clang` | the code above. The bug. |
| **R1h** `c-gcc-h` / `c-clang-h` | *new rung.* The same C plus the bounds check. |
| **R2** `safe_naive.rs` | indexed copy loop, checked by the language |
| **R3** `safe_tuned.rs` | `copy_from_slice` on a checked subslice |
| **R4** `unsafe.rs` | `copy_nonoverlapping`, check hoisted, unverified |
| **R5** `verus.rs` | R4's exec code, with the check proved sufficient |

**R1h is the point.** With only R1, "C is faster" and "C is unsafe" are the same
sentence, because C is faster precisely in that it skipped the check. R1-vs-R1h
is what the check costs inside one language; R1h-vs-R4 is what Rust's unsafe rung
costs against *safe* C; R1h-vs-R2/R3 is what Rust's extra machinery costs beyond
the bare check.

## Headline

- The check costs **5 instructions per call out of ~230** (2%) in C, and Rust's
  idiomatic safe rung (R3) lands within **+10 per call** of unsafe Rust. Safety
  costs about the same in both languages; Rust makes it non-optional.
- On a one-byte overflow, R1 is **silent in 7 of its 8 builds** — right answer
  shape, wrong number, exit 0. That is the row that matters. Delete the same
  check from safe Rust and you get exit 101 and `index out of bounds: the len is
  64 but the index is 64` instead.
- R4 and R5 are **byte-identical** machine code (`md5_fn 0e5b5936…`) on a kernel
  with raw pointer arithmetic and a nine-obligation proof. The proof still costs
  zero instructions.

Numbers, the full adversarial behaviour table, the TCB tally and the mutation
results are in `NOTES.md`.
