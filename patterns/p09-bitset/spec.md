# p09 — a bitset probed by attacker-chosen bit indices: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, and C spells the pair
out. C is handed the blob length and both C rungs ignore it, so R1-vs-R1h is a
comparison with the calling convention, the argument count and the register
allocation all held fixed. The only difference between those two cells is one
`if`.

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     nbits     u32 LE    DECLARED bit count      ATTACKER DATA
byte 4..8     nq        u32 LE    DECLARED query count    ATTACKER DATA
data_start = 8 ;  avail = len - 8                 what ACTUALLY arrived
nwords     = (nbits + 63) >> 6
words   : nwords * 8 bytes at window byte 8               u64 LE
queries : nq * 4 bytes after them                         u32 LE bit indices
```

## Semantics

```
if len < 8:                                   return 0
nbits, nq from the header
if nbits == 0 || nq == 0:                     return 0
nwords = (nbits + 63) >> 6
if 8*nwords + 4*nq > avail:                   return 0     # in u64/size_t

acc = 0 ; hits = 0
for k in 0 .. nq:
    q = load_u32(queries + 4*k)
    # >>> THE GUARD. R1 omits exactly this line and nothing else. <<<
    if q < nbits:
        w = load_u64(words + 8*(q >> 6))       # SHIFT, not divide -- pinned
        if w & (1u64 << (q & 63)) != 0:  hits += 1
        acc = acc *64 31 +64 w
acc = acc *64 31 +64 hits
for i in 0 .. nwords:                          # THE POPCOUNT PASS
    acc = acc *64 31 +64 popcount(load_u64(words + 8*i))
return (acc *64 31 +64 nbits) *64 31 +64 nq
```

`*64`/`+64` are wrapping, as in every earlier pattern here, so the kernel has
**no precondition on values** and every measured input is inside the verified
domain by construction. C's unsigned types wrap by definition (6.2.5p9) and the
Rust rungs write `wrapping_add`/`wrapping_mul`.

**The return is read left to right, i.e. as a Horner chain**:
`(acc*31 + nbits)*31 + nq`. The C rungs write the parentheses explicitly so that
the two languages cannot differ by operator precedence.

### THE SAFETY CHECK IS NOT A BOUNDS CHECK

That is the sentence this pattern exists for, and it is the one thing not to
"improve". Every earlier pattern here guards a range that the access itself
mentions:

| pattern | guard | access |
|---|---|---|
| p16 | `end - p >= 3` | `buf[p]`, `buf[p+1]`, … |
| p17 | `start < end && start >= 0` | `buf[base + start]` |
| p05 | `i*ncol + j < avail` | `data[i*ncol + j]` |
| p07 | `lo < hi` | `elements[mid]` |
| p11 | `q < len` | `buf[q]` |
| p03 | `sp > 0` / `sp < STACK_CAP` | `stack[sp]` |
| **p09** | **`q < nbits`** | **`words[q >> 6]`** |

p09's guard bounds the **bit** index; the access is on the **word** index. The
fact the access needs is

```
q < nbits   ==>   q >> 6  <  (nbits + 63) >> 6   ==   nwords
```

which is derived **through a shift**, and in which neither the guard's operand
nor the array's length appears directly. That is p05's question
(`.memory/01-ladder.md` finding 6) on a different operator, and it is the third
data point after p03 showed the same class of failure is **not Rust-specific**
and is analysis *seeding* rather than an inability to prove the lemma.

**The pattern carries its own negative control.** The popcount pass reads the
same array, with the same byte-at-a-time decoder, into the same fold, through an
index `ws + 8*i` that is **linear in its own loop counter**. Any difference
between what a middle-end does to the two loops is attributable to the shift and
to nothing else. NOTES.md 4.

### ONE CHARACTER, IN ONE POSITION, DECIDES WHETHER ANYTHING CATCHES IT

```
words[q >> 6]   shipped
words[q >> 5]   q/32 >= q/64: OVERSHOOTS, a SPATIAL bug. Caught by the bounds
                check, by ASan, by Miri, and by `load_u64`'s precondition.
words[q >> 7]   q/128 <= q/64: ALWAYS a legal word index under `q < nbits`.
                Caught by NOTHING, at zero instruction cost, on an R4 kernel
                that differs from the shipped one in ONE BYTE of 368.
```

That pair is what p09 is for, and the two spellings differ by one character in
one position. Beside it:

- **The spatial bug at rung level** — omit `q < nbits`, which is exactly and only
  what `c/kernel.c` does, and `q >> 6` walks off the word array. `q` is a `u32`,
  so the word index reaches 67 108 863 and the read reaches half a gigabyte past
  the blob. `adversarial-oob.bin` is that row and ASan fires on it.
- **The mask bug** — spell the mask `q & 31` instead of `q & 63`. The index stays
  in range, every rung **including R5** returns the same *wrong* answer, and no
  sanitiser, no bounds check and no memory-safety proof says anything. It is
  caught only by the functional `ensures`, and only because `model.py` and
  `bitset_fold` disagree with it. ⚠ It is a **two**-character substitution and it
  costs **+32% on R4**; the one-character mask edit `q & 3` costs **+57%**. So
  the mask bug is not the free one — `q >> 7` is.

⚠ **The task file proposed `q >> 5` as the arithmetic bug and that is measured
FALSE.** `q >> 5` names word indices up to roughly `2*nwords`, so it is a
**second spatial bug**, and R5 rejects it on **`load_u64`'s** *precondition* —
a verified item's, not the trusted accessor's — with the functional `ensures`
deleted. NOTES.md 6a has the fifteen-row mutant table and NOTES.md 6c the rest
of the invisible class — at least nine one-character index edits in that one
expression, of which the scale lever `4 * (q >> 6)` is measured too.

### The declared shape bounds both walks, and the bit index bounds neither

`nbits` and `nq` are attacker data, and unlike p11's `nstr` they **are** loop
bounds — but only after the length check `8*nwords + 4*nq > avail`, which is in
*every* rung including R1. Three adversarial inputs separate the three
quantities:

| input | what it attacks | R1 | every other rung |
|---|---|---|---|
| `adversarial-count` | the declared shape, `8*2 + 4*4096 > 96` | returns 0 | returns 0 |
| `adversarial-oob` | **the range check**, `q = 0x00FFFFFF` | reads 2 MiB past | skips it |
| `adversarial-edge` | the range check at `q == nbits`, `q == nbits-1` and one word past | **wrong answer, no diagnostic** | correct |

The first is a control: it attacks a check R1 *has*, and every cell agrees on
it. The last two are the bug, and they are two different harms — a heap
overflow a sanitiser sees, and an in-allocation over-read it does not.

### Load-bearing, do not "improve"

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug.

- **`q >> 6` and `q & 63`, spelled as a shift and a mask in every rung.** `/64`
  and `%64` are the `forbidden` spelling. ⚠ **Measured: they compile to
  byte-identical machine code** on rustc, clang *and* gcc, so this exclusion
  moves no number (NOTES.md 1a). It is kept because it holds the *source* form
  fixed, and that is what makes "the shift implements the division" a real
  obligation in `verus.rs` rather than a tautology — a pin whose entire effect
  is on proof burden.
- **The popcount pass is a separate loop from the query loop**, and its index is
  linear. Fusing them, or making it data-dependent, deletes the pattern's only
  within-kernel control.
- **`__builtin_popcountll` / `.count_ones()`, the intrinsic**, not a hand-rolled
  SWAR fold. NOTES.md 3d reports the instruction each rung actually emits and
  keeps that comparison separate from every safety number, because a rung
  emitting a software popcount against one emitting `popcnt` is a library/ISA
  difference (`.memory/03-measurement.md`, p11's rule).
- **`hits` and the popcount pass are both folded into the result**, so a rung
  that tests the wrong bit or reads the wrong word cannot produce the same
  checksum. This is what makes the arithmetic bug detectable at all.
- **The little-endian decodes are written out** — `+ 65536 *`,
  `+ 72057594037927936 *` — in every rung, and `from_le_bytes` is `forbidden`,
  for p03's two reasons; the second decides it, because `from_le_bytes`,
  `TryFromSliceError` and `from_raw_parts` are each `is not supported` at the
  pinned vstd, so a rung using one would compare a safe cell against an unsafe
  cell that cannot exist.
- **`align_to` / `from_raw_parts` are `forbidden`.** Reinterpreting the word
  region as a `&[u64]` deletes the byte-addressed index that *carries* the
  shift, and neither is expressible at the pinned vstd either.
- **The RESLICE and the QUERY CURSOR are deliberately NOT pinned**, and that is
  the point of the pattern. R2 indexes `buf` absolutely and R3 reslices the
  window once; `qs + 4*k` and a `chunks_exact(4)` walk of the query array are
  both in contract. Holding those fixed would hold fixed the one thing p09
  exists to compare, and NOTES.md 10a measures the alternates.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == bitset_fold(buf, off, len)
```

`bitset_fold` is the spec function; `model.py` is its independent Python twin.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on *every* input this benchmark
runs, `adversarial-*` included, and `harness/check.py` evaluates it at every one
of the kernel calls to prove that it does. `nbits`, `nq`, all 2^32 values of
each, and every query word are *arguments* of the problem; the kernel is total
in all of them.

**It is ONE clause, and both of p11's and p17's second ones are deliberately
absent.** p17 needed `buf_len <= 9223372036854775807` because it cast to `i64`;
p11 needed the same fact for its cursor step and bought it with a program
change. p09 needs neither: every index it forms is bounded by
`off + 8 + 8*nwords + 4*nq`, which the length check bounds by `off + len`, which
the structural `requires` already bounds by `buf@.len()`. **p09's hard
obligation is somewhere else entirely and it is `q >> 6 < nwords`.** NOTES.md 5.

### What the `ensures` is, and what it is not

p09 is p16's case rather than p17's: the harm is an ordinary out-of-range read,
so a discharged decoder precondition is the security property and the `ensures`
is what keeps the proof non-vacuous. ⚠ **On p09 that precondition is
`load_u64`'s — a VERIFIED item's, not the trusted accessor's** (NOTES.md 6a).
p09 is the only pattern here whose decoder wrappers carry their own `requires`,
and deleting `buf_get_unchecked`'s changes no count at all, so the trusted clause
is shadowed rather than dead and **the memory-safety obligation sits outside the
TCB boundary.**

**But p09 splits that sentence in a way no earlier pattern could, and the split
is the pattern's second axis.** The two obligations catch different bugs — the
`q >> 5` bug is caught by the *precondition* with the functional spec deleted;
`q >> 7` and `q & 31` are caught only by the *postcondition*, and both survive
even that once the specification is written from the same misunderstanding
(`20 verified, 0 errors` twice). NOTES.md 6a is the fifteen-row table.

**And there is a second thing the `ensures` deliberately does not say: anything
about which bits are set.** `qrun` in `verus.rs` specifies what the *program*
does — take the guard or do not, exactly as the exec code does — so
`adversarial-oob.bin` and `adversarial-edge.bin` are inside the verified domain
and every checked rung agrees with `model.py` on both. Writing the stronger
postcondition would have forced a `requires` about the contents of a file that
no honest loader can discharge (`.memory/02-bench-rules.md`), and it would have
deleted the rows that are the pattern.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p09's payload is p16's, p17's, p05's, p07's, p11's
and p03's:

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes` — the functions p16 added to `common/`, reused verbatim,
with **nothing added to `common/` for p09**. All three are a bulk copy rather
than an element-by-element decode, which is what keeps every p09 row
Miri-checkable.

Nothing is a compile-time constant: `n_iters`, `stride`, `n_blob`, every
`nbits`, every `nq`, every bitset word and every query come from the file.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here and are
deliberately not copied across.

## Driver loop

Identical in all six rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` normalises every copy — the C one included — and
diffs it against `driver.canonical` below. It is **p03's, with one constant
changed**: `stride_w >= 8` because p09's window header is the two 4-byte fields
`nbits` and `nq`, where p03's and p11's was one.

```
n_blob := bytes.len()
buf    := bytes
acc    := 0
if stride_w >= 8 and stride_w <= n_blob:
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

The comparison is in `u64` *before* the `as usize` cast, so a truncating driver
cannot sneak a 2^40 stride past it.

### Why this does not evaporate

Same mechanism as every earlier pattern: `k` is derived from `acc`, and `acc`
from the previous call's result, so call *i+1* cannot begin until call *i* has
returned. Nothing to CSE, nothing to hoist, no `black_box` and no `asm
volatile`. `k = (acc * nwin) >> 64` is Lemire's map onto `[0, nwin)`.

### Why every adversarial input is exactly one window

`k` is pseudo-random over `[0, nwin)`, so with several windows a malformed one
would be hit only probabilistically. With `nwin == 1`, `k` is always 0 and the
gate records one behaviour per cell rather than a mixture.

The related trap, from p17 and non-obvious: **window 0 must serve something**,
because a window returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is
then 0 for ever — the driver's Lemire index has an absorbing state at
`acc == 0`. Here a window can return 0 only by failing the length check, which
is exactly and only what `adversarial-count.bin` does, and that file has one
window so `k` is 0 regardless. `inputs/gen.py` records both constraints.

### Why every query in `small` and `large` is in range

`.memory/02-bench-rules.md` requires all rungs — **R1 included** — to print the
same checksum on the two measured inputs, and R1 has no `q < nbits` test. A
single out-of-range query on `small` or `large` would make R1 fold a word the
checked rungs skip. So the measured inputs are **100% guarded**, and R1-vs-R1h
there is the cost of a check that is always taken.

The consequence is a real limitation of the shipped matrix and is stated rather
than hidden: on `small` and `large` the regressors `nq` and `xguard` (guarded
queries) are the **same number**, so neither shipped input can separate them.
`sweep-d*` is what separates them and `sweep-w*` what separates either from
`nwords`; NOTES.md 4 reports the **rank of the pooled design** before it reports
a coefficient.

### The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(buf, n_blob, k * stride, stride)` and the Rust loop
calls `kernel(buf, k * stride, stride)`. `driver.aliases` cannot reconcile that
— both sides of an alias are a dotted identifier path, so an alias renames and
can do nothing else. `driver.call_args` declares which argument *positions* of a
named call are the canonical ones (`{"c": {"kernel": [0, 2, 3]}}`), and
`harness/dloop.py` refuses to drop anything that is not a single bare
identifier.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. What is worth saying here is the arithmetic
behind the two obligation counts, because a declared number a reviewer cannot
check from `spec.md` alone is exactly what `.memory/02-bench-rules.md` forbids.

| pin | why |
|---|---|
| `verus.obligations` = 18 | **popcnt 1 + wrun 1 + qrun 1 + five lemmas 5 + load_u32 1 + load_u64 1 + kernel 3 + main 5 = 18.** Every term is checkable with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained, and the zero terms are checkable the same way: `u32_at`, `u64_at`, `nwords_of`, `word_of`, `bit_of` and `bitset_fold` are non-recursive spec fns and report **0**; the four `external_body` items report **0**; `popcnt`, `wrun` and `qrun` are the three *recursive* spec fns and each carries one termination query. **`kernel`'s 3 is 1 body + 2 loop bodies** — p09 is the first pattern here with two kernel loops, and the second one is the popcount pass, which exists to be a control. p09 has **zero nonlinear arithmetic in the kernel**; its hard fact is bit-arithmetic, and it costs **five proof fns**, the largest lemma count of any kernel in this project. `main`'s 5 is quoted as measured and does not decompose from the command line — the by-block rule of thumb would predict 6 and Verus reports 5, the identical off-by-one p03's, p05's, p17's, p07's and p11's `spec.md` record for the identical driver. |
| `verus.twin_obligations` = 21 | the count in the **other** configuration, `verus.rs --cfg slb_twin`. **18 shipped + 3**, and p09 is the first pattern whose twin count moves by an amount that is *not* the number of twins: `slb_twin_buf_get_unchecked` carries 1 and `slb_twin_popcount64` carries **2**, because it has to *implement* the trusted contract with a loop rather than restate it with one indexed read. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`. Since TASK_010 that no longer makes Miri optional: it is mandatory for any pattern with a trusted item. p09 has a second reason: the unchecked index is `q >> 6`, two operators away from the guard, so an off-by-one in the derivation shows up only on queries near a word boundary — and `adversarial-edge.bin` sits exactly there. |
| `verus.unsafe_justifications` = {} | empty, and that is the healthy state. p09's one trusted `unsafe` item is the single-clause `buf_get_unchecked` p01/p02/p03/p05/p07/p11/p16/p17 all ship, whose `requires` names both parameters its body uses. p09's *other* trusted item, `popcount64`, contains no `unsafe` at all — it is trusted because vstd ships no specification for `u64::count_ones`, which is p08's `copy_in` situation and not a safety hatch. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == bitset_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (bitset_fold). p09 is p16's, p05's, p07's, p11's and p03's shape and NOT p17's: the harm is an ordinary out-of-range read, so a discharged decoder precondition is the security property and the `ensures` is what keeps the proof non-vacuous and pins WHICH values the answer is a function of. **THE PRECONDITION THAT FIRES IS `load_u64`'s -- A VERIFIED ITEM'S, NOT THE TRUSTED ACCESSOR'S** (TASK_038_REVIEW B2; this note said 'the accessor's' until TASK_039 and that was a mis-attribution). The error points at `p + 8 <= buf@.len()` in `load_u64`; deleting `buf_get_unchecked`'s `requires` changes nothing at all (18/0 -> 18/0 shipped, 19/0 -> 19/0 on the mask mutant, 17/1 -> 17/1 on the shift mutant), while deleting the DECODERS' and keeping the accessor's makes the failure reappear inside `load_u32`/`load_u64` -- so the trusted clause is SHADOWED, not dead. p09 is the only pattern here whose decoder wrappers carry their own `requires` (0 in all nine others), and this is the first time the memory-safety obligation sits OUTSIDE the TCB boundary. **And p09 splits the non-vacuity sentence in a way no earlier pattern could**, which is the pattern's point: ONE CHARACTER IN ONE POSITION decides whether anything catches the bug. `q >> 5` is caught by `load_u64`'s PRECONDITION with the functional `ensures` deleted (17 verified, 1 errors, *precondition not satisfied*) -- it OVERSHOOTS, so it is a spatial bug, not an arithmetic one, and the task file's premise that it stays in bounds is measured FALSE. **`q >> 7` UNDERSHOOTS** (q/128 <= q/64 < nwords) **and is therefore caught by NOTHING**: `19 verified, 0 errors` with the functional spec stripped, `20 verified, 0 errors` with the specification moved to match (`word_of = q as int / 128`), zero instruction cost, one differing byte in a 368-byte R4 kernel, silent under ASan+UBSan and Miri on every input including `thin.bin`, and a different answer on `small`. `q & 31` is the same story on the MASK and it ends the same way (`19 verified, 0 errors` stripped, `20 verified, 0 errors` with `bit_of = q % 32`) -- a program proved to meet its specification, whose specification is the bug -- but it is a TWO-character substitution costing +32% on R4, where `q >> 7` is one character costing nothing. NOTES.md 6a has all fifteen rows, NOTES.md 6c the rest of the invisible class (at least nine one-character index edits, the scale lever `4 * (q >> 6)` measured too), and `controls/gen_controls.py` regenerates every one of them. **What the `ensures` deliberately does NOT say is anything about which bits are set**: `nbits`, `nq` and every query word are attacker data, `qrun` specifies what the PROGRAM does -- take the guard or do not, exactly as the exec code does -- so `adversarial-oob.bin` and `adversarial-edge.bin` are INSIDE the verified domain and every checked rung agrees with model.py on both. A `requires` that every query is in range would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete the two rows that are the pattern.",
  "idiom": {
    "required": [
      {
        "c": "THE GUARD, and it is a range check on a VALUE rather than a bound on an index: `if (q < nbits) {` in c/kernel_hardened.c. c/kernel.c omits it and omits NOTHING ELSE, which IS the bug -- so the one scoped-absent pair this entry reports is on that rung and is correct.",
        "rust": "THE GUARD, and it is a range check on a VALUE rather than a bound on an index: `if q < nbits {` in all four Rust rungs."
      },
      "THE SHIFT. The access is on the word index and the guard is on the bit index, so the bound the access needs is derived through this operator: `q >> 6` in all six rungs.",
      "THE MASK, spelled as a mask and not as a remainder: `q & 63` in all six rungs.",
      "the word count is a shift too, and it is where the ceiling lives: `(nbits + 63) >> 6` in all six rungs.",
      {
        "c": "the declared shape is bounded by the window before either loop, in 64-bit arithmetic, in EVERY rung: `if (8 * nwords + 4 * nq > (uint64_t)(len - 8))` in both C rungs.",
        "rust": "the declared shape is bounded by the window before either loop, in 64-bit arithmetic, in EVERY rung: `if 8 * nwords + 4 * nq > (len - 8) as u64 {` in all four Rust rungs."
      },
      {
        "c": "THE POPCOUNT PASS IS A SEPARATE LOOP whose index is linear in its own counter -- the pattern's negative control: `for (i = 0; i < nwords; i++)` in both C rungs.",
        "rust": "THE POPCOUNT PASS IS A SEPARATE LOOP whose index is linear in its own counter -- the pattern's negative control: `while i < nwords {` in all four Rust rungs."
      },
      {
        "c": "the population count is the INTRINSIC and not a hand-rolled SWAR fold, because that comparison is the pattern's third axis: `__builtin_popcountll` in both C rungs.",
        "rust": "the population count is the INTRINSIC and not a hand-rolled SWAR fold, because that comparison is the pattern's third axis: `.count_ones()` in all four Rust rungs."
      },
      "the little-endian decodes are written out with + and * rather than | and <<, so they stay linear arithmetic: `+ 65536 *` in all six rungs.",
      {
        "c": "...and their top byte, which is what makes the u64 decode eight terms rather than four. C needs the `ULL` suffix on a literal above 2^31 and Rust does not, which is exactly what per-language entries exist for (TASK_019): `+ 72057594037927936ULL *` in both C rungs.",
        "rust": "...and their top byte, which is what makes the u64 decode eight terms rather than four: `+ 72057594037927936 *` in all four Rust rungs."
      },
      {
        "c": "the hit count is folded before the popcount pass, so a rung that tested the wrong bit cannot produce the same checksum: `acc = acc * 31 + hits;` in both C rungs.",
        "rust": "the hit count is folded before the popcount pass, so a rung that tested the wrong bit cannot produce the same checksum: `acc = acc.wrapping_mul(31).wrapping_add(hits);` in all four Rust rungs."
      },
      {
        "c": "and both declared counts are folded last, so a rung that read the header differently cannot produce the same checksum either: `(acc * 31 + nbits) * 31 + nq` in both C rungs.",
        "rust": "and both declared counts are folded last, so a rung that read the header differently cannot produce the same checksum either: `.wrapping_add(nbits).wrapping_mul(31).wrapping_add(nq)` in all four Rust rungs."
      }
    ],
    "forbidden": [
      "`q / 64`",
      "`q % 64`",
      "`from_le_bytes`",
      "`align_to`",
      "`from_raw_parts`"
    ],
    "why": "each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). THE GUARD IS NOT A BOUNDS CHECK, AND THAT IS WHY THIS PATTERN EXISTS: `q < nbits` bounds the BIT index and the access is `words[q >> 6]`, a WORD index, so the fact the access needs is one the guard does not state and has to be derived THROUGH A SHIFT. Every earlier pattern here guards a range the access mentions -- p16's `end - p >= 3`, p17's `start < end`, p05's `i*ncol + j`, p07's `lo < hi`, p11's `q < len`, p03's `sp > 0`. So `q >> 6` and `q & 63` are pinned literally, in every rung, and `q / 64` and `q % 64` are FORBIDDEN. AND HERE IS THE MEASUREMENT THAT ENTRY MUST BE READ WITH, because the task file asked for it and the answer is a null: **`q >> 6` and `q / 64` COMPILE TO BYTE-IDENTICAL MACHINE CODE**, and so do `q & 63` and `q % 64`, on rustc 1.97.1, clang 22.1.6 AND gcc 13.3.0, at `usize` and at `u32`, checked and unchecked, in the direct `&[u64]` shape and in the byte-addressed shape this kernel actually uses (NOTES.md 1a; the two unchecked Rust forms were folded into ONE symbol by the linker, which is the same fact stated by the toolchain). **So this forbidden entry pins NOTHING at the machine-code level and moves no number**, exactly as p17's excluded spelling compiles to the same 478 bytes as an admissible one. What it does buy is on the PROOF side and is measurable there: `verus.rs` writes the specification in DIVISION (`nwords_of`, `word_of`, `bit_of`) and the exec code in SHIFTS, so 'the shift implements the division' is a real obligation discharged by `lemma_shr6_is_div64` and `lemma_and63_is_mod64`, and a rung that spelled the exec side `q / 64` would need neither. A pin whose whole effect is on proof burden and none of it on instructions is a new shape for this project and is stated here rather than implied. A DISCLOSURE ABOUT THIS DECLARATION, because a reviewer should attack it: `check.py::exec_code` blanks Verus ghost CLAUSES (`requires`/`ensures`/`invariant`/`decreases`) and does NOT blank a `spec fn` BODY, so a forbidden entry of `q / 64` would fire on p09's own `verus.rs` if the specification spelled the index that way -- p16's `verus.rs:275` trap exactly. p09's spec functions therefore spell it `q as int / 64` and `(q as int % 64) as u64`, which do not contain the forbidden token once whitespace is deleted. That is a real interaction between the declaration and the matcher, it was found before the block was written rather than after, and `.memory/01-ladder.md` cites 'forbidden: 0 hits on all six' as the reproducible core of TASK_019's number -- so the honest thing is to keep the 0 and say how it was kept. AND UNTIL TASK_039 THE GATE COULD NOT HAVE SPRUNG IT, because these five entries were BARE STRINGS: `check.py:929`'s audit keys on `_TICK.findall`, so a forbidden entry without backticks is audited ZERO times while the verdict line two above still reports 'N forbidden spelling(s)' (TASK_038_REVIEW M4). p09 was the only pattern with a non-empty `forbidden` list and 0 audited spellings, i.e. its 'forbidden: 0 hits' was kept BY AUDITING NOTHING. The entries are now backticked, the audit is real, and it was RUN with the specification left exactly as it was: `audit 33 backticked spelling(s) over 6 rung(s) -> 98 (spelling, rung) pair(s), 67 present` and `audit forbidden: 10 spelling(s), 0 hit(s)` -- 10 rather than 5 because a plain-string entry is read against both languages. The 0 is now earned. Read `audit forbidden: N spelling(s)` and never the declaration line above it. ONE CHARACTER, IN ONE POSITION, DECIDES WHETHER ANYTHING CATCHES THE BUG -- and it is NOT the pair the task file named, nor the pair this file named until TASK_039; the correction is a measurement (NOTES.md 6, TASK_038_REVIEW B1). `q >> 5` OVERSHOOTS (`q/32 >= q/64`, up to ~2*nwords), so it is a SECOND SPATIAL bug: R5 rejects it on `load_u64`'s PRECONDITION with the functional spec deleted (`17 verified, 1 errors`, *precondition not satisfied*), i.e. memory safety alone catches it, on every input, and moving the specification to match it does not help. `q >> 7` UNDERSHOOTS (`q/128 <= q/64 < nwords`), so under the guard it is ALWAYS a legal word index and NOTHING catches it: no bounds check, no ASan, no UBSan, no Miri, no memory-safety proof (`19 verified, 0 errors` stripped; `20 verified, 0 errors` with `word_of = q as int / 128`), at ZERO instruction cost, on an R4 kernel one byte different from the shipped one, with a different answer on `small` and on every other blob. The MASK bug `q & 31` is the same result on a different operator -- invisible to memory safety, caught only by an independently written `ensures`, and not even by that once the misunderstanding reaches the spec -- but it is a TWO-character substitution costing +32% on R4, and the one-character mask edit `q & 3` costs +57%, so the mask is NOT the free bug and this file's earlier 'two one-character bugs' was wrong on both counts. The SPATIAL bug at rung level is R1's: delete `q < nbits` and `q >> 6` walks off the word array. All of them are built as controls in `controls/gen_controls.py` and none is a rung. THE POPCOUNT PASS IS SEPARATE FROM THE QUERY LOOP and its index is linear in its own loop counter: `for (i = 0; i < nwords; i++)` / `while i < nwords {` is pinned because it is THE NEGATIVE CONTROL for the whole pattern. Same array, same byte-at-a-time decoder, same fold, same rung, same call -- and an index that did NOT come through a shift. A rung that fused it into the query loop, or that made it data-dependent, would delete the only within-kernel control p09 has. It is also the intrinsic comparison (`__builtin_popcountll` vs `.count_ones()`), and NOTES.md 3d reports the emitted instruction per rung and keeps it apart from every safety number, because a rung emitting a software popcount against one emitting `popcnt` is a LIBRARY/ISA difference (`.memory/03-measurement.md`, p11's rule). THE LITTLE-ENDIAN DECODES ARE WRITTEN OUT with `+` and `*` -- `+ 65536 *` and `+ 72057594037927936 *` are pinned -- and `from_le_bytes` is forbidden, for p03's two reasons and the second decides it: it would delete the decode every rung shares, and it CANNOT BE AN R4/R5 SPELLING at the pinned vstd (`from_le_bytes`, `TryFromSliceError` and `from_raw_parts` are all `is not supported`, TASK_027_REVIEW), so a rung using it would compare a safe cell against an unsafe cell that cannot exist. `align_to` and `from_raw_parts` are forbidden for the same two reasons at once: reinterpreting the word region as a `&[u64]` deletes the byte-addressed index that CARRIES the shift, and neither is expressible at the pinned vstd. WHAT IS DELIBERATELY *NOT* PINNED: the QUERY CURSOR. `qs + 4*k` and a `chunks_exact(4)` walk of the query array are both in contract and NOTES.md 10a measures both, which is what makes the R3-side span a search rather than an assertion. Nor is the RESLICE pinned -- R2 indexes `buf` absolutely and R3 reslices the window, and holding that fixed would hold fixed one of the two things p09 exists to compare. WHEN THIS DECLARATION WAS WRITTEN, stated exactly: it was written AFTER the two phase-0 probes of NOTES.md 1a and 5, and BEFORE any measurement of any cell. What was known when it was written is that `>>6` and `/64` are codegen-identical on three compilers, that `lemma_u64_shr_is_div` discharges `q >> 6 < nwords` in three ghost lines, that vstd has no `count_ones` specification, and the seven mutant rows NOTES.md 6a had at that point (the `q >> 7` and `4 * (q >> 6)` rows were added at TASK_039, after the review, and nothing in this declaration turns on them). What was NOT known is any figure in NOTES.md 3, 4, 10 or 11, because no rung had been built, no input file existed and `model.py` had not been written. `.memory/01-ladder.md`'s direction test is what a reviewer should apply to every entry above, and it is flagged BROKEN there, so apply the PROVISIONAL repair and note that the one entry with a measured direction -- the `/ 64` exclusion -- moves p09's published figure by ZERO, which is neither for nor against interest. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither."
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
      "verus.rs": 18
    },
    "twin_obligations": {
      "verus.rs": 21
    },
    "obligations_note": "18 = popcnt 1 + wrun 1 + qrun 1 + lemma_and63_is_mod64 1 + lemma_shr6_is_div64 1 + lemma_guard_bounds_word 1 + lemma_popcnt_le 1 + lemma_popcnt_pos 1 + load_u32 1 + load_u64 1 + kernel 3 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`. u32_at, u64_at, nwords_of, word_of, bit_of and bitset_fold are NON-RECURSIVE spec fns and carry 0; buf_get_unchecked, popcount64, load_input and emit are external_body and carry 0; popcnt, wrun and qrun are the three RECURSIVE spec fns and each carries one termination query. **kernel's 3 = body + TWO loop bodies**, which is p09's contrast with p03's 2 (one loop) and p11's 4 (three loops): the second loop is the popcount pass and it exists to be a control. p09 has ZERO nonlinear arithmetic in the kernel and zero `by (nonlinear_arith)` there -- the hard fact is `q >> 6 < nwords`, which is bit-arithmetic rather than nonlinear, and it costs FIVE proof fns, which is the largest lemma count of any kernel in this project. main's 5 is quoted AS MEASURED and does not decompose from the command line: the by-block rule of thumb would predict 6 and Verus reports 5, the identical off-by-one p03's, p05's, p17's, p07's and p11's spec.md record for the identical driver. `.memory/04-verus.md`'s one-per-function-plus-one-per-loop rule gives 15 here and is therefore not the derivation.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`. 18 shipped + 3: `slb_twin_buf_get_unchecked` 1 (one function, no loop) and `slb_twin_popcount64` 2 (one function plus ONE LOOP BODY), each measured with `--cfg slb_twin --verify-function slb_twin_<name> --verify-root`. p09 is the first pattern whose twin count moves by an amount that is not the number of twins, because its second twin has to *implement* the trusted contract with a loop rather than restate it with one indexed read -- and pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body.",
    "unsafe_justifications": {
      "verus.rs": {
        "popcount64": "`popcount64` has NO parameter a caller could usefully be constrained on: it takes one `u64` by value and returns the number of its set bits, which is defined for all 2^64 of them. There is no index, no length, no address and no partiality -- so a `requires` here could only be a tautology, and `.memory/04-verus.md` records that a tautological conjunct on a TRUSTED item is exactly the shape that reads as strength and is not (stage 5c-req's probe exists for it). **And note what this item is NOT: it contains no `unsafe`.** It is `external_body` because vstd ships no specification for `u64::count_ones` (`vstd/std_specs/bits.rs` has `trailing_zeros` and `leading_zeros` and nothing else), which is p08's `copy_in` situation -- 'trusted means unchecked by the verifier, not unsafe'. p09 is the first pattern in this project whose trusted item models a **CPU instruction** rather than a memory operation, and the gate's own message ('it is therefore an axiom that the unchecked operation is always defined') is written for the memory case; here the axiom is 'count_ones returns the population count', which is the function's documented contract and is what `slb_twin_popcount64` DISCHARGES by implementing it in checked code with `/ 2` and `% 2` and verifying against the same `ensures`. That twin is the real defence and it is not optional: `verus.twin_obligations` pins it at 2 of the 3 obligations `--cfg slb_twin` adds. NOTES.md 5b's SLB-TRUSTED-ARGUMENT is the human reading of the same three questions."
      }
    },
    "items": {
      "verus.rs": {
        "u32_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "u64_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "nwords_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "word_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "bit_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "popcnt": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "wrun": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "qrun": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "bitset_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "lemma_and63_is_mod64": {
          "external": null,
          "requires": [],
          "ensures": [
            "(q & 63) == q % 64",
            "(q & 63) == bit_of(q)",
            "(q & 63) < 64"
          ]
        },
        "lemma_shr6_is_div64": {
          "external": null,
          "requires": [],
          "ensures": [
            "(x >> 6) == x as int / 64"
          ]
        },
        "lemma_guard_bounds_word": {
          "external": null,
          "requires": [
            "q < nbits"
          ],
          "ensures": [
            "(q >> 6) == word_of(q)",
            "(q >> 6) < nwords_of(nbits)"
          ]
        },
        "lemma_popcnt_le": {
          "external": null,
          "requires": [],
          "ensures": [
            "0 <= popcnt(x) <= x"
          ]
        },
        "lemma_popcnt_pos": {
          "external": null,
          "requires": [
            "x != 0"
          ],
          "ensures": [
            "popcnt(x) >= 1"
          ]
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
        "popcount64": {
          "external": "verifier::external_body",
          "requires": [],
          "ensures": [
            "r == popcnt(x)"
          ]
        },
        "slb_twin_popcount64": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == popcnt(x)"
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
        "load_u32": {
          "external": null,
          "requires": [
            "p + 4 <= buf@.len()"
          ],
          "ensures": [
            "r == u32_at(buf@, p as int)",
            "r <= 0xffff_ffff"
          ]
        },
        "load_u64": {
          "external": null,
          "requires": [
            "p + 8 <= buf@.len()"
          ],
          "ensures": [
            "r == u64_at(buf@, p as int)"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == bitset_fold(buf@, off as int, len as int)"
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
      "if stride_w >= 8 && stride_w <= n_blob",
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
    "note": "work_per_call is **bytes of the window** -- `stride`, 1108 on small and 4328 on large -- p16's, p05's, p11's and p03's denomination. WHICH WAY THE ESTIMATE ERRS: **LOOSE**, and by one term. Every byte of a well-formed p09 window is read at least once (the 8 header bytes as two u32s, every word byte by the popcount pass, every query byte by the query loop), so there is NO over-count; but a guarded query RE-READS the eight bytes of its word, so the true visit count is `stride + 8*xguard` -- 3020 on small (2.73x) and 10968 on large (2.53x). p16 errs strict, p17 loose, p05 strict, p03 strict, p09 loose: five patterns, and they do not agree, which is why `.memory/02-bench-rules.md` asks for the direction rather than assuming it. work_unit_bits is 8, one window byte, so the effective absolute bound under min_ir_per_work is 0.001953125 x 8 = 0.015625. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged. **`.memory/02-bench-rules.md` predicted otherwise and the prediction is retired**: MIN_DECLARABLE_IR_PER_WORK was fixed at TASK_009/TASK_010 *for p09*, on the assumption that p09 would be denominated in BITS and would want an AVX-512 `vpopcntq` floor of 0.0059 Ir/bit. It is not, it does not, and the hatch built for it is unused -- p09's query loop is a data-dependent branch on an attacker word with a serial dependence through `acc` and a byte-at-a-time decoder inside it, so there is no vector form at any -march. The two probe inputs differ in work_per_call (1108 vs 4328) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost, on the first kernel in this project whose safety obligation is not a bounds check. The guard is `q < nbits` and the access is `words[q >> 6]`, so the fact discharged is `q >> 6 < nwords` -- derived through a shift, from a guard on a different quantity. The byte-identity result now also covers a kernel with a TRUSTED ITEM THAT IS NOT A MEMORY OPERATION (`popcount64`, trusted because vstd has no specification for `u64::count_ones`), and a specification written in DIVISION against exec code written in SHIFTS, so the erased ghost material includes two bridge lemmas and not only invariants. At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."
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
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. On p09 there is a second reason: the unchecked index is `q >> 6`, a function of an ATTACKER WORD two operators away from the guard, so an off-by-one in the derivation would show up only on queries near a word boundary rather than as a fixed shift the way p16's and p17's would -- and `adversarial-edge.bin` is built to sit exactly there. Cost: check.py rewrites n_iters to 4, so each row reads 4 x stride bytes -- 4432 on small and 17 312 on large, ~180x inside `.memory/02-bench-rules.md`'s measured 3.05 M budget. The only real cost is the 8.2 MB payload to_vec, and p07's 12 MB one passes.",
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

There is no exit 7 here, for p16's, p17's, p05's, p07's, p11's and p03's reason:
p09's payload names no allocation size, so p02's `SLB_MAX_CAP` check would be
dead code.

## Degenerate shapes

`stride_w >= 8 && stride_w <= n_blob` is the driver's whole input validation. A
stride below 8 cannot hold the header; a stride above `n_blob` leaves no whole
window, so `nwin` would be 0 and `k` would have nothing to index. Either way the
loop is skipped and the driver prints `0` after **zero** kernel calls. p09 ships
no input for it — p11's `adversarial-stride3.bin` covers the identical driver
and the identical guard, and duplicating it here would add a matrix row that
tests the driver rather than the kernel.

`adversarial-count.bin` is the kernel's own version of the same thing and it is
a **control**: `nq` is 4096 against a window holding 20 queries, so
`8*nwords + 4*nq = 16400 > avail = 96` and every rung — R1 included — returns 0
after reading the header and nothing else. A checksum of 0 is a weak oracle, and
this row is here for the *behaviour* and *sanitiser* tables rather than for its
value: it is the input that would fire ASan in R1 if the missing check were the
length one, and it does not.

`adversarial-oob.bin` and `adversarial-edge.bin` are the bug, and they are two
different harms rather than two spellings of one. The first sends one query of
`0x00FFFFFF` at a two-word bitset: `q >> 6` is 262 143, the read is 2 MiB past a
208-byte allocation, and ASan reports `heap-buffer-overflow`. The second sends
99, 100, 127 and 128 at a `nbits = 100`, `nwords = 2` bitset: R1 reads words 1,
1, 1 and 2, and **word 2 is inside the same allocation** because the query array
follows the word array — so R1 returns a different answer with **no diagnostic
from any sanitiser**. That is p17's shape arriving on a pattern whose other
adversarial row does fire, and it is why `model.py` derives `sanitizer_expect`
from "does R1 leave the blob" rather than from "does R1 disagree".

The kernel's `len < 8` guard is, given the driver's `stride_w >= 8`, unreachable
in this benchmark. It is kept anyway so the kernel is **total** and its
`requires` stays purely structural; the alternative — a `len >= 8` precondition
— would be a precondition about the driver's own guard rather than about the
buffer. The `nbits == 0 || nq == 0` guard is *not* dead in the same way: it is
reachable from the wire format, and no shipped input takes it.
