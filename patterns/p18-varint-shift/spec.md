# p18 — LEB128 varint decoder: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, and C spells the pair
out. C is handed the blob length and *both* C rungs ignore it — p06's, p12's and
p14's shape. **Here the number the programmer needed was `VBITS`, declared four
lines up in the same file.**

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     nv        u32 LE    DECLARED varint count        ATTACKER DATA
byte 4..      the varint bytes                                 ATTACKER DATA
data_start = 4
VBITS  = 64                       the accumulator's width
```

`VBITS` is a compile-time constant in every rung. It is a property of the
*program* — a decoder targeting `uint64_t` has a 64-bit accumulator — and not of
the input: `n_iters`, `stride`, `n_blob`, `nv` and every byte of every varint
come from the file.

**Honesty is a property of the file, not of the kernel.** No rung checks that
`nv` is truthful, no rung checks that a varint terminates inside the window, and
— the part that matters — *the specification does not assume a varint fits in
sixty-four bits*. See "What the `ensures` is, and what it is not".

## Semantics

```
if len < 4:                                   return 0
nv from the header
if nv == 0:                                   return 0     # present in EVERY rung

acc = 0 ; p = 4
for v in 0 .. nv:
    if p == len:      break                                # present in EVERY rung
    val = 0 ; shift = 0 ; nb = 0                           # PER-VARINT LOCALS
    while p < len:                             # BOUNDED, in EVERY rung
        c = buf[off + p]
        p = p + 1
        nb = nb + 1

        # >>> THE SAFETY LINE. R1 omits exactly this line and nothing else. <<<
        if shift < VBITS:
            val = val | ((c & 0x7f) as u64) << shift

        shift = shift +32 7                    # WRAPPING, in every rung
        if c & 0x80 == 0:  break
    acc = acc *64 31 +64 val
    acc = acc *64 31 +64 nb
return acc *64 31 +64 nv
```

`*64`/`+64` are wrapping, as in every earlier pattern, and `+32` is the wrapping
`u32` add C spells `shift += 7` and Rust spells `shift.wrapping_add(7)`. So the
kernel has **no precondition on values** and every measured input is inside the
verified domain by construction. C's unsigned types wrap by definition (6.2.5p9)
and the Rust rungs write `wrapping_add`/`wrapping_mul`.

### The bound is a SHIFT COUNT, and every earlier one was an index or a length

`shift` is `7 * nb`, where `nb` is the number of bytes consumed so far in the
current varint — and `nb` is decided by the attacker's *continue bits*, not by
any declared length. The canonical encoding of a `uint64_t` is at most **ten**
bytes and its last shift is exactly **63**, in range. The **eleventh** byte is
the first one that is not, and nothing in the wire format forbids one.

That is what makes p18's guard different in kind from every earlier one in this
project. p02's, p16's and p17's compare a *declared length* against a *buffer
extent*; p11's and p13's are about a terminator; p14's is a *count of a byte
value* against a table's extent; p09's is a bit index against a word count. All
of them are **spatial** — they decide whether an address is inside an
allocation. p18's decides whether an *arithmetic operation is defined at all*.

Three consequences the pattern is built on:

- **the bug touches no memory.** C99 6.5.7p3 makes `E1 << E2` undefined when
  `E2 >= width(E1)`; it addresses nothing, allocates nothing and stores nothing.
  ASan is silent on every rung and every input of p18. What fires is **UBSan**
  (`-fsanitize=undefined` implies `-fsanitize=shift`), and p18 is the first
  pattern here whose sanitizer row is UBSan's rather than ASan's.
- **the safety line cannot be hoisted, folded into a length check, or derived
  from the header.** It has to be tested once per byte, inside the scan — which
  is why p18's hardening cost is **per input byte** and not per record. Every
  earlier pattern's C hardening line runs once per call or once per record; this
  one runs once per byte, so it does not amortise as the input grows.
- **the checksum is not an oracle for it.** `|=` is idempotent, so a payload
  wrapped round into a bit that is *already set* changes nothing.
  `adversarial-sat.bin` is that input: ten bytes of undefined shift, UBSan
  fires, and R1 and R1h return the **same** value. This is a property of the
  **bug**, not of the fold, and no choice of fold could repair it — which is
  said here rather than left for a reviewer to find.

### The scan IS bounded, and that is what keeps p18 out of p11's and p16's territory

`while p < len` is present in every rung, R1 included, and so is the outer
`if p == len: break`. **Every read of `buf` is in bounds in every rung on every
input**, so p18 has no out-of-bounds read to model and no out-of-bounds write at
all: there is no destination buffer. A varint decoder whose scan were bounded
only by the continue bit *is* p11 — the harm would be an out-of-bounds read and
the loop body would be `strlen`'s — and it is rejected in `NOTES.md` 0b for
exactly that reason, with the measurement.

### Truncation is the hardened behaviour, the contract pins it, and it is the SECOND bug

Once `shift` reaches `VBITS`, R1h and all four Rust rungs keep consuming the
varint's bytes — so `nb` and the cursor are unchanged — and simply stop
accumulating. That is what the Linux kernel's `uleb128` reader, Go's
`binary.Uvarint` in its non-error path, and most hand-written protobuf readers
do, and it is p13's shape one level up: **the hardened cell is memory-safe,
well-defined, and LOSES DATA.**

Pinning truncation rather than rejection is a deliberate choice with a measured
reason (`NOTES.md` 0b): the rejecting spelling needs a second live variable and
a second test, so R1-vs-R1h would stop being a one-line difference.

**And truncation is not only the hardened *behaviour*, it is a second bug that
nothing in this project's toolkit catches.** A ten-byte varint ends at shift 63,
where only bit 0 of the seven payload bits survives a `u64` — so six bits of the
encoded integer are discarded by the shift itself, with `shift < VBITS` true and
no undefined behaviour anywhere. `truncating.bin` is that input: every rung
agrees, ASan and UBSan are clean, `debug-assertions=on` is clean, Miri is clean,
R5's proof discharges, and the decoded number is not the number that was
written. It is p17's limit arriving on arithmetic instead of on a range.

### The fold, and what p18 does NOT add to the full-extent argument

TASK_004_REVIEW's reason for the full-extent fold is **elision**: a fold that
reads only part of the result lets the optimiser delete the rest. p06's is
**invariance** under permutation; p14's is **partition-blindness**. p18 supplies
**no fourth independent argument**, and saying so is more useful than inventing
one: the quantity the bug corrupts is the decoded value itself, which the fold
reads directly. What p18 does add is the *counter*-observation above — that on
`adversarial-sat.bin` no fold whatsoever can see the bug, because the two
programs compute the same value.

Two quantities are folded per varint and each is load-bearing against a
different mutation:

| folded | what it catches |
|---|---|
| the decoded **value** `val` | a rung that shifted by the wrong amount, or masked the wrong bits |
| the **byte count** `nb`, in order | a rung that consumed a different number of bytes — a ten-byte cap instead of a shift guard, or a scan that stopped on the wrong bit |

and `nv` is folded once at the end, so a rung that decoded a different number of
varints cannot produce the same checksum either.

### Load-bearing, do not "improve"

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug. Edit both or neither.

- **`val`, `shift` and `nb` are reset at the top of every varint in all seven
  rungs**, and nothing crosses a call boundary: p18's kernel holds no scratch,
  no table and no static state, so it is a function of its arguments by
  construction. `NOTES.md` 0c measures that rather than asserting it — p14's §0
  found that a kernel which is *not* a function of its arguments fails silently
  under the driver's repeat protocol.
- **The scan is bounded by `p < len` in all seven rungs** and the outer cursor
  guard `p == len` is present in all seven, so no rung reads out of bounds and a
  dishonest `nv` cannot spin.
- **The shift step is WRAPPING in all seven rungs** — `shift += 7` on C's
  `unsigned` (6.2.5p9) and `shift.wrapping_add(7)` in Rust. This is not
  stylistic. It is what leaves the **shift itself** and the two cursor
  increments as the only arithmetic in this kernel that a Rust
  `-C debug-assertions=on` build can fire on, which is what makes p18's `O0d`
  measurement attributable at all (`NOTES.md` 5).
- **The payload mask is `& 0x7f` and the continue test is `& 0x80` in all seven
  rungs**, so no rung can accidentally be decoding a different wire format.
- **The cursor guards are DIRECT COMPARISONS, not subtraction-first.** p07's and
  p14's subtraction-first idiom exists because their cursors advance by a
  *declared* length and the additive form `p + 4 > len` can overflow `usize`.
  p18's cursor advances by **one**, so `p < len` and `p == len` involve no
  arithmetic at all, there is nothing to overflow, and the kernel's `requires`
  stays at **one** clause without needing the idiom. Stated here because the
  absence of a pin three patterns share would otherwise look like an oversight.
- **The scan's BOUND is pinned and its loop FORM follows from it.** `while p <
  len` is a `required` entry in all four Rust rungs, because that bound is the
  whole of what keeps p18 out of p11's territory — so an iterator-driven scan
  (`w[p..].iter()`) is **out of contract on every rung including R3**, and
  `NOTES.md` 8d prices it as such. What the declaration *does* leave free on R3
  is the **window reslice** and the **statement structure of the fold**, and
  those are the two in-contract alternates `NOTES.md` 8d publishes beside the
  shipped cell. ⚠ An earlier draft of this bullet called `t_iter` "the second
  in-contract R3 spelling"; the `idiom` block always said otherwise, the block
  wins, and the correction is disclosed in the block's own `why` and in
  `NOTES.md` 12.
- Wrapping arithmetic throughout.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == varint_fold(buf, off, len)
```

`varint_fold` is the spec function; `model.py` is its independent Python twin —
and independent in a way that matters here: `model.py`'s *simulation* decodes
with Python's arbitrary-precision integers and **no width test at all**, masking
to 64 bits once per varint, while the helper `varint_fold` carries the explicit
per-byte `shift < VBITS` exactly as `verus.rs`'s `vdec` does. The two agree on
every input, so the width truncation is checked two ways — as a final mask and
as a per-byte guard.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included, and `harness/check.py` evaluates it at every one of the
kernel calls to prove that it does. `nv`, all 2^32 values of it, and every byte
of the window including every continue bit in it are *arguments* of the problem;
the kernel is total in all of them.

**It is ONE clause**, as on p03, p06, p11, p12 and p14 and unlike p17 — and here
keeping it at one cost nothing at all, because the cursor advances by one.

### What the `ensures` is, and what it is not

**It is the FUNCTIONAL postcondition, and that is the whole point.** It says the
accumulator is the fold of the values the window's varints decode to and of the
bytes each consumed — not merely that nothing was accessed out of bounds. On
p18 a memory-safety-only spec would be **vacuously true of every rung including
R1**, because R1 accesses nothing out of bounds: its defect is arithmetic.
`NOTES.md` 10 is where the mutants are, and `NOTES.md` 6 is where the three
trusted bases for the one fact are tabulated.

**And there are two things the `ensures` deliberately does not say.** First,
that `nv` is honest or that a varint terminates inside the window —
`adversarial-*`, `truncating.bin` and `degenerate.bin` are all inside the
verified domain and every checked rung agrees with `model.py` on all of them.
Second, and this is the honest limit, **it does not say that the decoded value
is the integer the encoder wrote.** `varint_fold` specifies the *truncating*
decode because that is what the program does, so the proof is silent on
`truncating.bin`. Writing the stronger postcondition would require a
specification of the encoder, which no honest loader has
(`.memory/02-bench-rules.md`), and it is p17's limit in a new place.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p18's payload is p14's, p06's, p11's, p03's, p12's,
p16's, p17's, p05's and p07's:

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes`, reused verbatim, with **nothing added to `common/` for
p18**.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here. p18's
kernel allocates nothing at all: it has no buffer of any kind.

## Driver loop

Identical in all seven rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers, and byte-for-byte p06's, p12's and p14's. `harness/check.py` normalises
every copy — the C one included — and diffs it against `driver.canonical` below.

```
n_blob := bytes.len()
buf    := bytes
acc    := 0
if stride_w >= 4 and stride_w <= n_blob:
    stride := stride_w as usize
    nwin   := (n_blob / stride) as u64
    it     := 0
    while it < n_iters:
        k   := ((acc as u128 * nwin as u128) >> 64) as usize
        r   := kernel(buf, k * stride, stride)
        acc := acc *64 31 +64 r
        it  := it + 1
emit(acc)
```

`stride_w >= 4` because p18's window header is the 4-byte `nv` field.
`adversarial-stride3.bin` attacks it. The comparison is in `u64` *before* the
`as usize` cast, so a truncating driver cannot sneak a 2^40 stride past it.

### Why this does not evaporate

Same mechanism as every earlier pattern: `k` is derived from `acc`, and `acc`
from the previous call's result, so call *i+1* cannot begin until call *i* has
returned. Nothing to CSE, nothing to hoist, no `black_box` and no `asm volatile`.

### Why every adversarial input is exactly one window

`k` is pseudo-random over `[0, nwin)`, so with several windows a malformed one
would be hit only probabilistically. With `nwin == 1`, `k` is always 0 and `off`
is always 0, so R1's undefined shift happens on every call deterministically.

The related trap, from p17: **window 0 must serve something**, because a window
returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever — the
driver's Lemire index has an absorbing state at `acc == 0`. `inputs/gen.py`
**checks** it, by running a twenty-line copy of the checked kernel over every
window of every blob it emits.

### The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(buf, n_blob, k * stride, stride)` and the Rust loop
calls `kernel(buf, k * stride, stride)`. `driver.call_args` declares which
argument *positions* of a named call are the canonical ones
(`{"c": {"kernel": [0, 2, 3]}}`), and `harness/dloop.py` refuses to drop anything
that is not a single bare identifier.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes;
what is worth saying here is the arithmetic behind the two obligation counts.

| pin | why |
|---|---|
| `verus.obligations` = 12 | **`VBITS` 1 + `vdec` 1 + `vbytes` 1 + `vwalk` 1 + `kernel` 3 + `main` 5 = 12.** Every term was measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, and so were the zero terms. `kernel`'s 3 is 1 body + 1 per loop body (**two** loops: the varint walk and the byte scan). `u32_at`, `nv_at` and `varint_fold` are NON-RECURSIVE spec fns and report 0, while `vdec`, `vbytes` and `vwalk` are RECURSIVE and carry one termination query each; `buf_get_unchecked`, `load_input` and `emit` are `external_body` and report 0. **One `const` carries one query**, `VBITS`, which is the shape p03, p06 and p08 have and not p14's three. |
| `verus.twin_obligations` = 13 | the count under `--cfg slb_twin`. **12 shipped + 1**, one per trusted accessor twin, and it is +1 rather than +3 because `load_input` and `emit` state no `ensures` and contain no `unsafe`, so they are outside the twin regime. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`, and since TASK_010 that does not make Miri optional: it is mandatory for any pattern with a trusted item. On p18 there is a second, pattern-specific reason and it is worth stating: **Miri runs with `debug-assertions` ON**, so the Miri row is simultaneously the only place in the gate where an oversized shift in a *Rust* rung would be caught. It is silent on every p18 input precisely because all four Rust rungs carry the safety line, and `NOTES.md` 7 shows what it does when they do not. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == varint_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (varint_fold). p18's bindings are the READ-ONLY set p03, p06, p11, p12, p14, p16, p17, p05 and p07 use and NOT p02's before/after set, and the reason is stronger here than on any of them: p18's kernel WRITES NOTHING ANYWHERE. It has no scratch, no output buffer and no table -- `val`, `shift`, `nb`, `p` and `acc` are scalars -- so there is no buffer for an `after` binding to name and no store of any kind to exclude. **THE SECURITY PROPERTY IS THEREFORE NOT CARRIED BY A TRUSTED ACCESSOR'S `requires` AT ALL**, which is a first for this project and is the thing to read this pin for. `buf_get_unchecked`'s `i < v@.len()` excludes an out-of-bounds READ; R1's defect is an out-of-range SHIFT, and the two are about different facts. Weakening or deleting that `requires` neither admits nor excludes R1's bug (measured, ../NOTES.md 10), and a memory-safety-only specification of this kernel is VACUOUSLY TRUE OF R1. What rejects the deletion of the safety line is Verus's own arithmetic obligation on `<<`, `possible bit shift underflow/overflow`, raised on the operator with no accessor and no `ensures` involved. **The `ensures` is the FUNCTIONAL one and on p18 that is not a preference but the only option that says anything**: it states that the accumulator is the fold of the values the window's varints decode to and of the bytes each consumed, through `vdec`, `vbytes` and `vwalk`. **What the `ensures` deliberately does NOT say** is that `nv` is honest, that a varint terminates inside the window, or -- and this is the honest limit -- that the decoded value is the integer the ENCODER wrote. `varint_fold` specifies the TRUNCATING decode because that is what the program does, so adversarial-shift11.bin, adversarial-shift20.bin, adversarial-many.bin, adversarial-sat.bin, truncating.bin and degenerate.bin are all INSIDE the verified domain, every checked rung agrees with model.py on all six, and the proof is SILENT on truncating.bin's wrong answer. A `requires` that a varint fitted in sixty-four bits would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete every row the pattern exists for.",
  "idiom": {
    "required": [
      {
        "c": "THE SAFETY LINE, and the only line c/kernel.c omits: `if (shift < VBITS)` in c/kernel_hardened.c. c/kernel.c omits exactly this and nothing else.",
        "rust": "THE SAFETY LINE: `if shift < VBITS {` in all four Rust rungs. In Rust at the flags this benchmark measures (-C debug-assertions=off, all 24 cells) it is NOT a safety line -- deleting it produces no panic and no bounds-check failure, only the same silently wrong integer C produces, because `<<` MASKS the count. It becomes a safety line only under -C debug-assertions=on, under Miri and under Verus. ../NOTES.md 7."
      },
      {
        "c": "the shift is applied with `<<` and combined with `|`, spelled out rather than through a library helper, so that the operator carrying the undefined behaviour is visible in the source of the rung that commits it: `val |= (uint64_t)(c & 0x7f) << shift;` in both C rungs.",
        "rust": "the shift is applied with `<<` and combined with `|`, spelled out rather than through the wrapping_shl / checked_shl / unchecked_shl family, all of which are forbidden and priced: `val = val | (((c & 0x7f) as u64) << shift);` in all four Rust rungs."
      },
      {
        "c": "THE SCAN IS BOUNDED BY THE WINDOW IN EVERY RUNG, R1 included -- p18 is NOT p11 and NOT p16, and this entry is what says so by grep: `while (p < len)` in both C rungs.",
        "rust": "THE SCAN IS BOUNDED BY THE WINDOW IN EVERY RUNG, R1 included: `while p < len` in all four Rust rungs. The opening brace is deliberately NOT part of the quoted spelling: verus.rs puts its invariant block between the loop condition and the brace, so a pin that included the brace would put R5 out of its own pattern's declaration.."
      },
      {
        "c": "...and the OUTER CURSOR GUARD, present in every rung, so a dishonest `nv` cannot spin over an exhausted window: `if (p == len)` in both C rungs.",
        "rust": "...and the OUTER CURSOR GUARD, present in every rung, so a dishonest `nv` cannot spin over an exhausted window: `if p == len {` in all four Rust rungs."
      },
      "the payload is the low SEVEN bits, so no rung can be decoding a different wire format: `c & 0x7f` in all seven rungs.",
      {
        "c": "...and the CONTINUE BIT is bit 7, which is what decides a varint's length and therefore what decides the shift count: `if (!(c & 0x80))` in both C rungs.",
        "rust": "...and the CONTINUE BIT is bit 7, which is what decides a varint's length and therefore what decides the shift count: `if c & 0x80 == 0 {` in all four Rust rungs."
      },
      {
        "c": "THE SHIFT STEP IS WRAPPING in every rung, which is what leaves the shift itself and the two cursor increments as the only arithmetic a debug-assertions=on build can fire on: `shift += 7;` in both C rungs (unsigned, 6.2.5p9).",
        "rust": "THE SHIFT STEP IS WRAPPING in every rung, which is what leaves the shift itself and the two cursor increments as the only arithmetic a debug-assertions=on build can fire on: `shift = shift.wrapping_add(7);` in all four Rust rungs."
      },
      {
        "c": "`val`, `shift` and `nb` are RESET AT THE TOP OF EVERY VARINT in every rung, so no state crosses a varint boundary and none crosses a call boundary: `shift = 0;` in both C rungs.",
        "rust": "`val`, `shift` and `nb` are RESET AT THE TOP OF EVERY VARINT in every rung, so no state crosses a varint boundary and none crosses a call boundary: `let mut shift: u32 = 0;` in all four Rust rungs."
      },
      {
        "c": "the DECODED VALUE is folded, so a rung that shifted by the wrong amount or masked the wrong bits cannot produce the same checksum: `acc = acc * 31 + val;` in both C rungs.",
        "rust": "the DECODED VALUE is folded, so a rung that shifted by the wrong amount or masked the wrong bits cannot produce the same checksum: `.wrapping_add(val)` in all four Rust rungs."
      },
      {
        "c": "...and the BYTE COUNT is folded, in order, so a rung that consumed a different number of bytes -- a ten-byte cap instead of a shift guard, or a scan that stopped on the wrong bit -- cannot either: `acc = acc * 31 + (uint64_t)nb;` in both C rungs.",
        "rust": "...and the BYTE COUNT is folded, in order, so a rung that consumed a different number of bytes cannot either: `.wrapping_add(nb as u64)` in all four Rust rungs."
      },
      {
        "c": "the declared varint count is folded, so a rung that decoded a different number of varints cannot produce the same checksum either: `* 31 + (uint64_t)nv` in both C rungs.",
        "rust": "the declared varint count is folded, so a rung that decoded a different number of varints cannot produce the same checksum either: `.wrapping_add(nv as u64)` in all four Rust rungs."
      },
      "the little-endian u32 header decode is written out with + and * rather than | and <<, so it stays linear arithmetic and the ONLY `<<` in the kernel is the one the pattern is about: `+ 65536 *` in all seven rungs.",
      "...and its top byte: `+ 16777216 *` in all seven rungs."
    ],
    "forbidden": [
      "`wrapping_shl`",
      "`checked_shl`",
      "`overflowing_shl`",
      "`unchecked_shl`",
      "`from_le_bytes`",
      "`chunks_exact`",
      "`take_while`",
      "`.position(`"
    ],
    "why": "each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (../spec.md's second sentence). THE ONLY THING R1 OMITS IS THE SHIFT BOUND: the scan bound `p < len` is present in every rung, so every read of `buf` is in bounds in every rung and p18 has NO out-of-bounds access to model on any input; the outer cursor guard `p == len` is present in every rung, so a dishonest `nv` cannot spin; `val`, `shift` and `nb` are reset at the top of every varint in every rung. R1-vs-R1h is therefore the cost of `if (shift < VBITS)` and nothing else. THE BOUND IS A SHIFT COUNT AND THAT IS WHY THIS PATTERN EXISTS: every earlier bound in this project is SPATIAL -- p02's, p16's and p17's compare a declared length against a buffer extent, p11's and p13's are about a terminator, p14's is a count of a byte value against a table's extent, p09's is a bit index against a word count -- and all of them decide whether an ADDRESS is inside an ALLOCATION. p18's decides whether an ARITHMETIC OPERATION IS DEFINED AT ALL. `shift` is `7 * nb` and `nb` is decided by the attacker's continue bits, not by any declared length: the canonical encoding of a `uint64_t` is at most TEN bytes and its last shift is exactly 63, in range, and the ELEVENTH byte is the first one that is not. So the guard cannot be hoisted out of the scan, folded into a length check or derived from the header, and it runs ONCE PER INPUT BYTE rather than once per call or once per record -- which is why p18's hardening cost does not amortise as the input grows and every earlier pattern's does. THE BUG TOUCHES NO MEMORY, AND THE CONSEQUENCE FOR THE TOOLKIT IS THE RESULT: ASan is silent on every rung and every input of p18, rustc's bounds checks are silent, and a memory-safety-only specification is VACUOUSLY TRUE OF R1. What catches it is UBSan on the C side (`-fsanitize=undefined` implies `-fsanitize=shift`, measured at harness/check.py's own flags), `-C debug-assertions=on` and Miri on the Rust side, and Verus (`possible bit shift underflow/overflow`). All four are outside the 24-cell matrix; ../NOTES.md 0.2 and 7 have the measurements. THE CHECKSUM IS NOT AN ORACLE FOR THIS BUG CLASS, AND THAT IS A PROPERTY OF THE BUG RATHER THAN OF THE FOLD: `|=` is idempotent, so a payload wrapped round into a bit that is ALREADY SET changes nothing, and `adversarial-sat.bin` is a twenty-byte varint of `0x7f` payloads on which ten undefined shifts execute, UBSan fires, and R1 and R1h return the SAME value. No choice of fold could repair that, which is why the fold entries below are justified by what they DO catch and not by a claim to catch everything. TRUNCATION AT VBITS IS THE SPECIFIED ANSWER, not an evasion, and it is ALSO THE SECOND BUG: once `shift` reaches VBITS the hardened rung keeps consuming the varint's bytes -- so `nb` and the cursor are unchanged -- and stops accumulating, which is what the Linux kernel's uleb128 reader and most hand-written protobuf readers do, and it is p13's shape one level up (the hardened cell is memory-safe, well-defined, and LOSES DATA). Rejecting instead was built and rejected in ../NOTES.md 0b for a measured reason: it needs a second live variable and a second test, so R1-vs-R1h would stop being a one-line difference. And a TEN-byte varint whose last payload is `0x7f` ends at shift 63 -- in range, no undefined behaviour, guard never fires -- and six bits of the encoded integer are discarded by the shift itself; `truncating.bin` is that input, every rung agrees on it, ASan, UBSan, `debug-assertions=on` and Miri are all clean and R5's proof discharges, because `varint_fold` specifies what the PROGRAM does. That is p17's limit arriving on arithmetic instead of on a range and it is stated in the `ensures` section of ../spec.md rather than left to be discovered. THE CURSOR GUARDS ARE DIRECT COMPARISONS AND NOT SUBTRACTION-FIRST, and the absence of a pin that p07, p14 and three other patterns carry is deliberate rather than an oversight: their cursors advance by a DECLARED length, so the additive form `p + 4 > len` can overflow `usize` and Verus rejects it. p18's cursor advances by ONE, so `p < len` and `p == len` involve no arithmetic at all, there is nothing to overflow, and the kernel's `requires` stays at ONE clause without needing the idiom. `wrapping_shl`, `checked_shl`, `overflowing_shl` and `unchecked_shl` are forbidden because each REPLACES the safety line with a library call and each does so in a different and separately interesting way, so a rung using one would be measuring a different question: `wrapping_shl` makes the oversized shift DEFINED with exactly x86's masking semantics, i.e. it writes R1's realised behaviour on purpose and would be silent under debug-assertions, under Miri and under Verus while still returning the wrong number; `checked_shl` IS the guard, in library form, so a rung using it would price `Option` codegen rather than the branch this pattern is about; `unchecked_shl` is the Rust spelling of C's undefined behaviour and would put the UB inside an `unsafe` block, which is a DIFFERENT experiment (it would make R4 and R1 commit the same UB and make the safe rungs incomparable to both). All four are built and priced in controls/gen_controls.py and ../NOTES.md 9, and their prover disposition is MEASURED there rather than asserted. `from_le_bytes` deletes the written-out little-endian header decode every rung shares AND is NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW and again on p06 and p14), so a rung using it would compare a safe cell against an unsafe cell that cannot exist. `chunks_exact` is forbidden because p16 measured that the chunk width moves that pattern's per-byte rate over a 31% range (5.04688...6.62500, `.memory/01-ladder.md`), and p18's published decomposition is into a per-varint-byte and a per-varint term. `take_while` and `.position(` are forbidden because each turns the scan into a LIBRARY iterator whose exit condition is the continue bit: `position` in particular computes the varint's LENGTH in one pass and would then decode in a second, which is a different program with a different cost model, and this pattern's whole per-byte law is a statement about a single-pass explicit cursor. EVERY EXCLUSION HERE IS WHOLE-PATTERN AND NOT SCOPED TO SOME RUNGS, which is deliberate: `.memory/01-ladder.md`'s direction test fired on p13 exactly because three of its entries named some rungs and exempted `safe_tuned.rs`, so R3 was permitted a spelling R4 was forbidden and 48%/17% of the published margin was the pin. A whole-pattern exclusion keeps the two sides of the comparison equal. NOTHING IN `required` IS SCOPED TO A SUBSET OF RUNGS ON p18, which is a difference from p06 and p14 worth naming: both of those scope their bulk load's RECEIVER 2-and-2 because `RangeTo` has no `SliceIndexSpecImpl` at the pinned vstd, and p18 has no bulk load and no receiver -- its kernel performs exactly one kind of memory access, a byte read of the input window, so there is nothing to scope. WHAT IS AND IS NOT PINNED ABOUT THE SCAN LOOP, STATED PRECISELY BECAUSE AN EARLIER DRAFT OF ../spec.md's PROSE GOT IT WRONG AND THE BLOCK IS WHAT DECIDES: the scan's BOUND is pinned -- `while p < len` in all four Rust rungs and `while (p < len)` in both C rungs, entry `required[2]` -- because that bound is the whole of what keeps p18 out of p11's territory, and a rung whose scan is bounded by the continue bit instead is a DIFFERENT PATTERN with a different harm (../NOTES.md 0b builds it and rejects it). So an iterator-driven scan such as `w[p..].iter()` is OUT of contract on every rung including R3, and ../NOTES.md 8d prices it as such rather than pretending it is admissible. What the declaration DOES leave free on R3 is the WINDOW RESLICE -- named nowhere here, so the two-step `split_at` form that ships, the one-step `&buf[off..off + len]` form and no reslice at all are all admissible -- and the STATEMENT STRUCTURE OF THE FOLD, since only its operations are pinned; those are p18's two in-contract R3 spellings besides the shipped one and ../NOTES.md 8d publishes all three with the input named. What IS pinned instead of the loop form is the OPERATIONS and the BOUND -- the payload mask, the continue test, the wrapping shift step, the guard, the scan bound and the cursor guard. THE FOLD IS OVER THE FULL RECORDED EXTENT AND ORDER-SENSITIVE, AND p18 SUPPLIES NO FOURTH INDEPENDENT REASON FOR THAT RULE -- saying so is more useful than inventing one. TASK_004_REVIEW's reason is ELISION: a fold that reads only part of the result lets the optimiser delete the rest. p06's is INVARIANCE: three reverses compose to a permutation, so a sum- or xor-fold could not tell the buggy scratch from the correct one. p14's is PARTITION-BLINDNESS: tokenising moves no byte, so a fold over the concatenated content is identical for every possible set of field boundaries. p18's bug corrupts the DECODED VALUE, which the fold reads directly, so elision alone justifies the rule here. What p18 adds is the COUNTER-observation above -- that on `adversarial-sat.bin` no fold whatsoever can see the bug. The two folded quantities each catch a different mutation and ../NOTES.md 2 tabulates them: the VALUE catches a rung that shifted by the wrong amount or masked the wrong bits, and the BYTE COUNT catches a rung that consumed a different number of bytes -- a ten-byte cap instead of a shift guard, or a scan that stopped on the wrong bit. `nv` is folded once at the end so a rung that decoded a different number of varints cannot produce the same checksum either. THE SHIFT STEP IS WRAPPING IN ALL SEVEN RUNGS AND THAT IS NOT STYLISTIC: `shift += 7` on C's `unsigned` wraps by 6.2.5p9 and Rust spells it `shift.wrapping_add(7)`, and the effect is that the SHIFT ITSELF and the two cursor increments are the ONLY arithmetic in this kernel that a Rust `-C debug-assertions=on` build can fire on. p18 is the first pattern in this project to measure the `O0d` axis at all, and that axis is only attributable because of this entry. ../NOTES.md 5 decomposes the O0d-minus-O0 delta mnemonic by mnemonic and reports what fraction of it is the shift check rather than the increments. WHEN THIS DECLARATION WAS WRITTEN, STATED EXACTLY BECAUSE p18 HAS A PRE-FLIGHT: it was written after the seven rungs, the R5 proof (12/0 on the second attempt, twin 13/0) and the checksums existed and BEFORE any p18 CELL had been measured for perf -- `harness/measure.py p18` had not been run and no `Ir` or `ns` figure for any of the eight cells existed. What DID exist is ../NOTES.md 0: `Ir`, sanitizer behaviour and checksums for a standalone SIX-KERNEL C PROBE with no driver and no pattern, which settled the bug class TASK_051 asked to be settled before five rungs were built on it, plus the three-premise `O0d` probe of ../NOTES.md 0.1. Neither is a cell and no number from either is published as p18's, but they are not nothing either, and saying 'no number existed' would be false. What the probe DID influence is the CHOICE OF BUG CLASS, the choice of TRUNCATION over rejection as the hardened answer, and the wire format that expresses both; what it did not influence is any entry of `required` or `forbidden`, every one of which names a line the contract in ../spec.md's Semantics block already had. NO ENTRY OF `required` OR `forbidden` WAS ADDED IN RESPONSE TO A MEASUREMENT ON p18, and that is stated as a fact about this pattern rather than as a general claim: p14 had to disclose one (`flen = i - s;`, added after an `identity` failure) and p18 had no such repair -- its `-O0` identity came out `norel` and its `-O3` identity `exact` on the first build of the pair, before any entry of this declaration was edited. ONE EDIT TO THIS `why` KEY WAS HOWEVER MADE AFTER THE CONTROLS WERE BUILT, AND IT IS NAMED HERE RATHER THAN LEFT TO BE INFERRED: the paragraph above about the scan loop originally read `WHAT IS DELIBERATELY NOT PINNED is the SPELLING OF THE SCAN LOOP: ... and the second in-contract R3 spelling drives it from w[p..].iter()`, which CONTRADICTED this block's own `required[2]` (`while p < len`). Building `t_iter` is what surfaced the contradiction. NO ENTRY of `required` or `forbidden` moved -- `required[2]` is exactly what it was, and `t_iter` is out of contract now as it was then; what changed is that the prose now says so. The corresponding sentence in ../spec.md's prose and in safe_tuned.rs's header was wrong the same way and was corrected in the same commit (../NOTES.md 12). NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither."
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 12
    },
    "twin_obligations": {
      "verus.rs": 13
    },
    "obligations_note": "12 = VBITS 1 + vdec 1 + vbytes 1 + vwalk 1 + kernel 3 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained, and the zero terms are checkable the same way: u32_at, nv_at and varint_fold are NON-RECURSIVE spec fns and report 0, while vdec, vbytes and vwalk are RECURSIVE and carry one termination query each; buf_get_unchecked, load_input and emit are external_body and report 0. ONE `const` carries one query, VBITS -- `.memory/04-verus.md` records that a `const` inside verus! is its own obligation (measured on p08's SCR and p03's STACK_CAP), and p18 has the single-constant shape p03, p06 and p08 have rather than p14's three. kernel's 3 = body + TWO loop bodies (the varint walk and the byte scan), and there is no `by (nonlinear_arith)` and no `by (bit_vector)` anywhere in the kernel -- the spec is written with the SAME `&`/`|`/`<<` the exec code uses, which is what keeps the solver in the fragment it is good at, and the only multiplications are by literals. main's 5 is quoted AS MEASURED and does not decompose from the command line: body + driver loop + one per by-block would predict 6 and Verus reports 5, the identical off-by-one p03's, p05's, p06's, p07's, p11's, p12's, p14's and p17's spec.md record for the identical driver. `.memory/04-verus.md`'s one-query-per-function-plus-one-per-loop rule of thumb gives 9 here and is therefore not the derivation.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 12 shipped + 1, and the term is measured the same way: `--cfg slb_twin --verify-function slb_twin_buf_get_unchecked --verify-root` reports `1 verified`. It is +1 rather than +3 because load_input and emit state NO `ensures` and contain NO `unsafe`, so they are outside the twin regime (`.memory/04-verus.md`: the regime is keyed on `external_body` + a non-empty `ensures` OR `unsafe`). **p18 has the smallest trusted base of any pattern in this project -- 3 items, 1 with a `requires` -- and for a structural reason rather than by cleverness**: its kernel performs exactly ONE kind of memory access, a byte read of the input window, so there is exactly one accessor to trust. There is no scratch, no output buffer, no bulk copy and no write of any kind. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg.",
    "unsafe_justifications": {},
    "items": {
      "verus.rs": {
        "u32_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "nv_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "vdec": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "vbytes": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "vwalk": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "varint_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "buf_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_buf_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "load_input": {
          "external": "verifier::external_body",
          "requires": [],
          "ensures": []
        },
        "emit": {
          "external": "verifier::external_body",
          "requires": [],
          "ensures": []
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == varint_fold(buf@, off as int, len as int)"
          ]
        },
        "main": {
          "external": null,
          "requires": [],
          "ensures": []
        }
      }
    }
  },
  "driver": {
    "statements": 12,
    "c_source": "c/main.c",
    "regions": [
      "safe_naive.rs",
      "safe_tuned.rs",
      "unsafe.rs",
      "verus.rs",
      "c/main.c"
    ],
    "aliases": {
      "c": {
        "n_body": "bytes.len()",
        "bytes": "bytes.as_slice()",
        "inp.n_iters": "n_iters"
      }
    },
    "call_args": {
      "c": {
        "kernel": [
          0,
          2,
          3
        ]
      }
    },
    "canonical": [
      "n_blob = bytes . len ( ) ;",
      "buf = bytes . as_slice ( ) ;",
      "acc = 0 ;",
      "if stride_w >= 4 && stride_w <= n_blob",
      "{",
      "stride = stride_w ;",
      "nwin = n_blob / stride ;",
      "it = 0 ;",
      "while it < n_iters",
      "{",
      "k = acc * nwin >> 64 ;",
      "r = kernel ( buf , k * stride , stride ) ;",
      "acc = acc * 31 + r ;",
      "it = it + 1 ;",
      "}",
      "}"
    ]
  },
  "collapse": {
    "probe_inputs": [
      "small.bin",
      "large.bin"
    ],
    "probe_iters": [
      100,
      200
    ],
    "note": "work_per_call is **bytes of the window** -- `stride`, 116 on small and 45 on large -- which is p16's, p05's, p11's, p12's, p14's and p06's denomination. WHICH WAY THE ESTIMATE ERRS: HIGH, BY EXACTLY FOUR BYTES, and it is stated in the direction it really goes rather than in the comfortable one. The 4 window-header bytes are decoded as a u32 and are never scanned; every other window byte is visited EXACTLY ONCE, because `nv` is honest on small, large, truncating and every sweep blob, so the cursor reaches `len`. There is no second pass and no third: p18's kernel does not copy and does not re-read, so unlike p14 there is no under-count to set against the over-count. The derived floor is therefore 1.00 Ir/call too high out of 29.00 on small and 11.25 on large -- against a kernel that executes about eleven instructions per scanned byte, so it is cleared by roughly 40x either way (../NOTES.md 3). A floor that errs HIGH can produce a false FAILURE and never a false pass, which is the safe direction for this check, and the margin above says by how much. work_unit_bits is 8, one window byte, so the effective absolute bound under min_ir_per_work is 0.001953125 x 8 = 0.015625. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged, and the argument is p18-specific and stronger than any earlier pattern's: **a varint's length is not known until its last byte has been read**, so the scan is not merely un-vectorised, it is unvectorisABLE at any -march -- the loop-carried dependence is the continue bit of the byte just loaded -- and the fold on top of it is a serial Horner chain `acc = acc*31 + x`. No compiler emitted a vector instruction in any of the eight cells (measured on the disassembly, ../NOTES.md 1). The two probe inputs differ in work_per_call (116 vs 45) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost, on the first kernel in this project whose load-bearing obligation is ARITHMETIC rather than spatial. The byte-identity result now covers a kernel whose postcondition is a recursive fold written with `&`, `|` and `<<` -- the operators this project has kept out of its specs on eleven previous patterns -- and it holds with no `by (bit_vector)` anywhere in the file. **The pin has NO measured price on p18**, which is worth recording because p06's and p14's did: both had to bind a value to a local before a store, because R5's store is a CALL and R4's is an assignment. p18 has no store at all, so the argument evaluation order that broke their -O0 identity has nothing to act on here, and `norel`/`exact` came out on the FIRST build of the pair with no edit to any rung. At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."
    }
  ],
  "miri": {
    "pair": [
      "unsafe",
      "verus"
    ],
    "sources": [
      "unsafe.rs"
    ],
    "required": true,
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. **On p18 there is a second reason, specific to this pattern and to nothing else in the project: Miri runs with `debug-assertions` ON.** So the Miri row is simultaneously the only place inside the gate where an oversized shift in a RUST rung would be caught -- it panics with `attempt to shift left with overflow` rather than reporting `Undefined Behavior`, so check.py's `ub` flag stays false and the row fails on the exit code instead (measured, ../NOTES.md 0.2). It is silent on every p18 input precisely because all four Rust rungs carry the safety line, and ../NOTES.md 7 shows what it does when they do not. Cost: check.py rewrites n_iters to 4, so each row scans at most 4 x stride bytes -- 464 on small and 180 on large, five orders of magnitude inside `.memory`'s measured 3.05 M budget. The only real cost is the 5.2 MB payload to_vec, and p07's 12 MB one passes.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed."
  }
}
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success; checksum on stdout |
| 2 | wrong argument count |
| 3 | cannot open input file |
| 4 | file shorter than the 16-byte header |
| 5 | `payload_len` exceeds the bytes present |
| 6 | allocation failure (C only) |

There is no exit 7 here, for p03's, p06's, p11's, p12's, p14's, p16's, p17's,
p05's and p07's reason: p18's payload names no allocation size, and the kernel
has no buffer at all, so p02's `SLB_MAX_CAP` check would be dead code.

**These are the CHECKED rungs' exit codes — and on p18 they are also R1's, on
every input.** R1's undefined behaviour is a masked shift, which faults nothing
and aborts nothing, so every C cell exits 0 on every row including the
adversarial ones. That is the whole point of the pattern: see `NOTES.md` 7 for
the table and `results/gate/p18-varint-shift.json` for the record.

## Degenerate shapes

`stride_w >= 4 && stride_w <= n_blob` is the driver's whole input validation. A
stride below 4 cannot hold the header (`adversarial-stride3.bin`); a stride above
`n_blob` leaves no whole window, so `nwin` would be 0 and `k` would have nothing
to index. Either way the loop is skipped and the driver prints `0` after **zero**
kernel calls.

`degenerate.bin` is one window carrying the shapes the contract has to decide,
and **every rung including R1 agrees on it**, which is why it is not named
`adversarial-*` and the gate holds all eight cells to `model.py` on it.

> ⚠ **AND IT IS THE ONE INPUT IN THIS PATTERN THAT IS OUTSIDE THE DOMAIN OF
> EVERY PUBLISHED PER-CALL `Ir` LAW.** Its last varint runs off the end of the
> window (`cut = 1`) and it declares nine varints while holding five
> (`brk = 1`); every other input here, and all 34 blobs of sweep bands b/v/x/y,
> have `cut = brk = 0`. Read `../NOTES.md` **4a0 before 4a1** — the level laws
> are stated with those two columns since TASK_052, and the two-column form is
> their restriction to `cut = brk = 0`. Sweep band `t` is the band that
> establishes it. **This paragraph is here because a reader meets this blob in
> the results table before they meet the caveat** (TASK_051_REVIEW blocker 1).

The five varints: 

| varint | what it is |
|---|---|
| `00` | one byte, payload 0. `val == 0`, `nb == 1`. |
| `80 80 00` | a padded zero — legal LEB128 that decodes to 0 through three bytes. A decoder that rejected non-canonical encodings would disagree. |
| `ff*9 01` | ten bytes, last shift **exactly 63**: the boundary from the safe side. R1 and R1h agree here and diverge at eleven bytes. |
| `b9 60` | an ordinary two-byte varint. |
| `ff ff` | the continue bit is still set on the **last byte of the window**, so the scan exits on `p < len` rather than on a terminator — the truncated-tail case, i.e. **`cut = 1`**. |

and `nv` is declared **9** against five varints, so the outer `p == len` guard
fires after the fifth — i.e. **`brk = 1`**. Those last two rows are what put the
blob outside the level laws' domain.

The kernel's `len < 4` guard is, given the driver's `stride_w >= 4`, unreachable
in this benchmark. It is kept anyway so the kernel is **total** and its
`requires` stays purely structural; the alternative — a `len >= 4` precondition —
would be a precondition about the driver's own guard rather than about the
buffer.
