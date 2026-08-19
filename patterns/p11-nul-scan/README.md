# p11 — NUL-terminated string scan

**Family B, and it is the first pattern in it.** Seven patterns existed before
this one and all seven were in Family A (buffers) or Family C (parsing).
NUL-termination is the most notorious bug family in C and this project had not
touched it.

## What the kernel does

A window declares a count of packed, NUL-terminated strings. The kernel measures
each string, folds its bytes into a per-string hash, mixes the *length* into
that hash, and steps the cursor past the terminator.

```
byte 0..4   nstr   u32 LE    DECLARED string count    ATTACKER DATA
byte 4..    packed, NUL-terminated strings

acc = 0 ; p = 4
for s in 0 .. nstr:
    q = p ; while q < len and buf[off+q] != 0: q += 1      # THE SCAN
    slen = q - p
    h = 0 ; for i in p .. q: h = h*31 + buf[off+i]         # THE FOLD
    acc = acc*31 + (h ^ slen)
    if q >= len: break
    p = q + 1
    if p >= len: break
return acc*31 + nstr
```

Full contract, and the pins the gate enforces: `spec.md`. Findings and the
proof's sticking points: `NOTES.md`.

## The C bug — CWE-125 via a missing sentinel

R1 (`c/kernel.c`) writes the scan the way a competent C programmer writes it:

```c
q = p + strlen((const char *)(buf + off + p));
```

`strlen` is bounded by the terminator and by nothing else. R1h
(`c/kernel_hardened.c`) is the same file with one expression changed:

```c
const void *z = memchr(buf + off + p, 0, len - p);
q = (z == NULL) ? len : (size_t)((const unsigned char *)z - (buf + off));
```

**Nothing is computed wrongly in R1.** Every index is correct, every subtraction
is safe, every quantity is unsigned. That is what makes this a structurally new
bug for this project: p16 walks one step past a *length* whose subtraction
wrapped, p17 computes a wrong-but-in-bounds *index*, p07 underflows an
*inclusive bound*, p05 forms a nonlinear *product*. Here the loop simply does
not stop.

`adversarial-nonul.bin` is the input: one window, six declared strings, six
written, and the sixth has no terminator. ASan reports

```
ERROR: AddressSanitizer: heap-buffer-overflow ... READ of size 13
    #0 __interceptor_strlen
    #1 kernel patterns/p11-nul-scan/c/kernel.c:65
0x... is located 0 bytes after 66-byte region
```

## What is new here that no earlier pattern could measure

1. **The loop bound is not known before the loop.** Every earlier kernel's trip
   count is a length, a header field or `ceil(log2 n)`. This one runs until it
   finds a sentinel that may not be there, so safe Rust cannot express the C
   loop at all: every safe spelling is bounded by *something*.
2. **The C rung calls a hand-written SIMD libc routine and Rust has to match
   it.** p02 had `memcpy`, but as a bulk *copy*; this is a bulk *search*.
   `NOTES.md` §2 decomposes the R1-vs-R3 gap into a library term and a safety
   term rather than quoting a ratio — the distinction this project retracted a
   "C beats Rust" headline over once already.
3. **The declared count bounds nothing**, and `adversarial-zerotail.bin` proves
   it: the same 4096-string lie as `adversarial-count.bin` with a NUL tail
   instead of a non-zero one, and every rung including R1 stays in bounds.

## Rungs

| Rung | File | The scan |
|---|---|---|
| R1 | `c/kernel.c` | `strlen` — bounded by the **sentinel**. The bug. |
| R1h | `c/kernel_hardened.c` | `memchr(.., len - p)` — bounded by the **window**. |
| R2 | `safe_naive.rs` | indexed `while q < len { if buf[off+q] == 0 { break } .. }` |
| R3 | `safe_tuned.rs` | `CStr::from_bytes_until_nul(&w[p..])` |
| R4 | `unsafe.rs` | R2's loop with `get_unchecked` |
| R5 | `verus.rs` | R4's exec code, plus the proof. `12 verified, 0 errors`. |

## Inputs

| stem | shape |
|---|---|
| `small` | 12 windows x 1192 B = 14.0 KiB (L1), 150 strings/window, **mean length 6.92** |
| `large` | 2000 windows x 4145 B = 7.9 MiB (past L2), 41 strings/window, **mean length 100.0** |
| `adversarial-nonul` | honest count, last string unterminated — **R1 overruns** |
| `adversarial-count` | 4096 declared / 3 written, non-zero tail — **R1 overruns** |
| `adversarial-zerotail` | 4096 declared / 3 written, NUL tail — every rung agrees |
| `adversarial-empty` | eight zero-length strings — the degenerate scan |
| `adversarial-stride3` | a window too small for the header — zero kernel calls |
| `sweep-len*` | string length 1..64 at fixed count, and count 4..36 at fixed length |

The two measured inputs sit on **opposite sides of 16**, which is where
`core::slice::memchr` switches from a scalar byte loop to its word-at-a-time
path. That is not decoration: R3's scan is a different algorithm on the two
inputs, from the same source.
