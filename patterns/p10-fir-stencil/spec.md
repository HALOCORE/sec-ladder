# p10 — weighted FIR / sliding-window stencil: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, and C spells the pair
out. C is handed the blob length and *both* C rungs ignore it — p06's, p12's,
p14's and p18's shape. **Here the number the programmer needed was `len`, the
window's own extent, which is already an argument.**

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4      n     u32 LE   DECLARED sample count           ATTACKER DATA
byte 4..8      r     u32 LE   DECLARED radius                 ATTACKER DATA
byte 8..8+taps       u8[]     the FIR coefficients            ATTACKER DATA
byte 8+taps..        u8[]     the samples                     ATTACKER DATA
data_start = 8
taps       = 2*r + 1          computed at 64 bits in every rung
```

**The radius is a RUNTIME value read out of the file**, not a compile-time
constant. That is what makes `r` a second structural parameter and what makes
`slice::windows(taps)` — which takes a runtime `usize` — the natural R3 idiom.
It is also what a compile-time radius would have destroyed: one cell per radius
instead of one binary over a sweep.

**The coefficients come first and the samples last**, so the sample array ends
at the window's end and an off-by-one leaves the window rather than landing on
a neighbouring field of the same record.

## Semantics

```
if len < 8:                                    return 0
n, r from the header
taps = 2*r + 1                                 # 64-bit in every rung
if n < taps:                                   return 0     # present in EVERY rung
last = 8 + taps + n - 1                        # window offset of the LAST sample byte

# >>> THE SAFETY LINE. c/kernel.c writes `last > len` and nothing else differs. <<<
if last >= len:                                return 0

nout = n - 2*r
sb   = 8 + taps
acc  = 0
for i in 0 .. nout:
    s = 0                                      # u32
    for j in 0 .. taps:
        s = s +32 (buf[off + sb + i + j] *32 buf[off + 8 + j])
    acc = acc *64 31 +64 s
return acc *64 31 +64 nout
```

`*64`/`+64` and `*32`/`+32` are wrapping, as in every earlier pattern. C's
unsigned types wrap by definition (6.2.5p9) and the Rust rungs write
`wrapping_add`/`wrapping_mul`. So the kernel has **no precondition on values**
and every measured input is inside the verified domain by construction.

### The bug is ONE CHARACTER, and it is in a comparison BOTH C rungs perform

`last` is an **index** — the window offset of the last sample byte the kernel
will read. The test that keeps it inside the window is therefore `last >= len`.
`c/kernel.c` writes `last > len`, which admits `last == len`: **exactly one
byte past the window, and not a byte more.**

That is a different shape from every earlier pattern here. p02's, p07's, p16's,
p17's and p18's R1 **omits a line**, so hardening *adds* instructions — +5
(gcc) / +12 (clang) on p02, `+2.00` per executed pop on p03, once per input
byte on p18. **p10's R1 already executes the comparison and merely relates its
two operands wrongly**, so R1h is the same instruction stream with one opcode
byte changed (`ja` → `jae`) and the hardening cost is expected to be **zero**.
`NOTES.md` 4 measures it rather than assuming it.

### The bug is CONDITIONAL, and the gate forces that

`harness/check.py` stage 2 requires every cell **including R1** to print
`model.py`'s checksum on every non-`adversarial-*` input, so a bug that fired on
a well-formed window could not be shipped at all. `inputs/gen.py` packs every
benign window exactly full — `stride == 8 + taps + n`, so `last == len - 1` —
and the two C rungs are then behaviourally identical on every benign input.

That is also what makes the **R1-vs-R1h cost comparison legal here** where
`.memory/02-bench-rules.md`'s first rule forbids it on p12 and p13: on every
input the cost is measured on, the unhardened rung commits no undefined
behaviour and refuses no work.

`adversarial-fencepost.bin` is a window truncated by **exactly one byte** — it
declares `n` samples and carries `n - 1`. R1 accepts it; every other rung
returns 0.

### The harm is one byte, and whether it is observable is a property of the
### ALLOCATION and not of the program

An off-by-one at a boundary cannot reach further than one element by
definition, and `adversarial-farover.bin` is the row that says so: a window
declaring `n` far beyond what it holds is rejected by R1 and R1h **alike**. R1's
defect buys an attacker one byte and nothing more.

| input | where the stolen byte lives | what fires |
|---|---|---|
| `adversarial-fencepost` | one past the payload allocation | **ASan** |
| `adversarial-fenceslack` | a trailing payload byte that forms no further window | **nothing** — exit 0, wrong answer |

This is p02's result on the read side, at the smallest possible magnitude.

### The algorithm is a WEIGHTED FIR and not a box filter

A box filter (all weights equal) has an **O(n)** running-accumulator form — add
the entering sample, subtract the leaving one — and an **O(n·r)** tap-loop
form. A ladder in which any rung reached for the first while the others used the
second would be comparing two different algorithms with different complexities,
and every number in the pattern would be void. A per-tap coefficient `w[j]`
makes the incremental form **impossible for every rung in every language at
once**, so `O(nout · taps)` is honest by construction and the "you pessimised
C" objection has no purchase. It is also the shape real DSP and image code has.
`NOTES.md` 0 records the rejected candidates.

### There is no division anywhere on the output path

A FIR is normally normalised by the coefficient sum. A per-output `div` would
cost **one `Ir`** to callgrind (`.memory/03-measurement.md`, the `div` pricing
section) and tens of variable cycles to the machine — nearly free in the column
this project publishes and expensive in the one it cannot measure well — and it
would sit inside every per-tap law p10 fits. The kernel sums into a `u32` and
folds the raw sums. The disassembly of all eight cells is checked for
`div`/`idiv` and contains none (`NOTES.md` 1).

### The fold, and what it can and cannot see

TASK_004_REVIEW's reason for the full-extent fold is **elision**: a fold that
read only part of the output would let the optimiser delete the rest of the tap
loop, which is the entire kernel. p10 adds one reason of its own: **the bug
changes whether the kernel runs at all** on the input that triggers it — R1h
returns 0 where R1 returns a fold — so the fold sees it *structurally* and not
only through the value of the one stolen byte, whose coefficient may be small
and whose value may be zero.

| folded | what it catches |
|---|---|
| the output value `s`, in order | a rung that applied the coefficients in the wrong order, dropped a tap, or read the wrong sample |
| the output count `nout`, once at the end | a rung that computed a different number of outputs — which is exactly what an off-by-one does |

p06's lesson is that a sum-fold cannot observe a permutation; the analogue here
would be a fold that could not observe a single extra tap. `NOTES.md` 2 checks
it rather than asserting it.

### Load-bearing, do not "improve"

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug. Edit both or neither.

- **The window guard `n < taps` is present in every rung, R1 included**, so
  `nout = n - 2*r` cannot underflow and p10 has **no wild index to model on any
  input**. An underflowed `nout` would be a different and much larger bug, and
  excluding it in every rung is what keeps the two C cells one character apart.
- **`taps = 2*r + 1` is computed at 64 bits in every rung**, so a declared
  radius near 2³² cannot wrap it into a small one.
- **`last` is computed as an index and given a name**, because that is where the
  fencepost lives and naming it is what makes the one-character difference
  legible.
- **The tap loop's SPELLING is deliberately NOT pinned, and that freedom is the
  experiment.** p10 exists to ask whether safe Rust's tax is proportional to the
  number of indexing operations or flat, and the three spellings that answer it
  — index every tap, slice the window once and reduce it, `get_unchecked` —
  differ in nothing but that. What *is* pinned is that every rung computes the
  same `2r+1` products of the same operands in the same order into the same
  wrapping `u32`.
- Wrapping arithmetic throughout, and `.sum(` is forbidden because `Sum for u32`
  uses `+`, which panics under `-C debug-assertions=on` and under Miri.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == fir_fold(buf, off, len)
```

`fir_fold` is the spec function; `model.py` is its independent Python twin.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included, and `harness/check.py` evaluates it at every one of the
kernel calls to prove that it does. `n`, `r` and every byte of the window are
*arguments* of the problem; the kernel is total in all of them.

**It is ONE clause**, as on p03, p06, p11, p12, p14 and p18.

### What the `ensures` is, and what it is not

It is the **functional** postcondition. A memory-safety-only specification would
be blind to p10's functional mutant class — a rung that folds `nout + 1`
outputs, or applies the coefficients in reverse, stays in bounds — which is p09's
result and the reason p10 does not take the cheaper spec.

**What it deliberately does not say**: that `n` or `r` is honest, or that the
coefficients mean anything. Every adversarial input is inside the verified
domain and the proof is silent about whether the answer is the one the encoder
meant. That is p17's limit.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p10's payload is p18's, p14's, p06's, p11's, p03's,
p12's, p16's, p17's, p05's and p07's:

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes`, reused verbatim, with **nothing added to `common/` for
p10**.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here. p10's
kernel allocates nothing at all and writes nothing anywhere.

## Driver loop

Identical in all seven rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers, and byte-for-byte p06's, p12's, p14's and p18's apart from the stride
floor. `harness/check.py` normalises every copy — the C one included — and diffs
it against `driver.canonical` below.

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

`stride_w >= 8` because p10's window header is the 8-byte `(n, r)` pair.
`adversarial-stride7.bin` attacks it. The comparison is in `u64` *before* the
`as usize` cast, so a truncating driver cannot sneak a 2^40 stride past it.

### Why this does not evaporate

Same mechanism as every earlier pattern: `k` is derived from `acc`, and `acc`
from the previous call's result, so call *i+1* cannot begin until call *i* has
returned. Nothing to CSE, nothing to hoist, no `black_box` and no `asm volatile`.

### Why every adversarial input is exactly one window

`k` is pseudo-random over `[0, nwin)`, so with several windows a malformed one
would be hit only probabilistically. With `nwin == 1`, `k` is always 0 and `off`
is always 0, so R1's overread happens on every call deterministically.

`adversarial-fenceslack.bin` is the one place this is used as a *lever* rather
than a hazard: its payload carries three trailing bytes that do not form a
further window, so `nwin` is still 1 and `k` is still 0, and the byte R1 steals
is a real payload byte instead of a redzone.

The related trap, from p17: **window 0 must serve something**, because a window
returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever.
`inputs/gen.py` **checks** it, by running a copy of the checked kernel over
every window of every blob it emits.

### The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(buf, n_blob, k * stride, stride)` and the Rust loop
calls `kernel(buf, k * stride, stride)`. `driver.call_args` declares which
argument *positions* of a named call are the canonical ones
(`{"c": {"kernel": [0, 2, 3]}}`), and `harness/dloop.py` refuses to drop anything
that is not a single bare identifier.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes.

**The block is generated by `controls/mkcontract.py`, not hand-edited**, so the
byte-identical shared paragraph of `idiom.why` is byte-identical by construction
— it is read out of `patterns/p18-varint-shift/spec.md` at generation time and
appended verbatim. `NOTES.md` 0 records the block's sha256 as first written and
the `idiom` object's own sha256, which is the one that does not move.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == fir_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (fir_fold). p10's bindings are the READ-ONLY set p03, p06, p11, p12, p14, p16, p17, p05, p07 and p18 use and NOT p02's before/after set: p10's kernel WRITES NOTHING ANYWHERE -- no destination buffer, no scratch, no table; `s`, `acc`, `i` and `j` are scalars -- so there is no buffer for an `after` binding to name. THE SECURITY PROPERTY HERE IS SPATIAL AND IS CARRIED BY THE TRUSTED ACCESSOR'S `requires` (`i < v@.len()`), which is p10's difference from p18: p18's bug is an out-of-range SHIFT that no accessor precondition can exclude, while p10's is an out-of-bounds READ, exactly what that precondition excludes. The `ensures` is nevertheless the FUNCTIONAL one and not a memory-safety-only one, for the reason p09 established: a memory-safety-only specification is blind to every functional change, and p10 has a functional mutant class -- a rung that folds `nout + 1` outputs, or that applies the coefficients in reverse -- that stays in bounds. What the `ensures` deliberately does NOT say is that `n` or `r` is honest, or that the coefficients sum to anything in particular: every adversarial input is INSIDE the verified domain and the proof is silent about whether the answer is the one the encoder meant, which is p17's limit.",
  "idiom": {
    "required": [
      {
        "c": "THE SAFETY LINE, and it is ONE CHARACTER rather than a whole line: `if (last >= len)` in c/kernel_hardened.c. c/kernel.c writes `if (last > len)` -- the same comparison between the same two operands, with the wrong relation -- and that single character is the whole difference between the two cells. `last` is an INDEX (the window offset of the last sample byte the kernel reads), so last == len is already one past the window.",
        "rust": "THE SAFETY LINE: `if last >= len {` in all four Rust rungs. In Rust it is not the only thing standing between the program and the overread -- the bounds check is -- but it is what makes the four Rust rungs return 0 where c/kernel.c returns a fold, so it is what keeps the checksum comparable across all seven rungs on the benign inputs."
      },
      {
        "c": "THE WINDOW GUARD, present in every rung including R1, so that `nout = n - 2*r` cannot underflow and p10 has NO wild index to model on any input: `if (n < taps)` in both C rungs. p10's bug is an off-by-one and its harm is one byte; an underflowed `nout` would be a different and much larger bug, and excluding it in every rung is what keeps the two cells one character apart.",
        "rust": "THE WINDOW GUARD, present in every rung including R1: `if n < taps {` in all four Rust rungs."
      },
      "THE TAP COUNT IS TWICE THE RADIUS PLUS ONE AND IS COMPUTED AT 64 BITS IN EVERY RUNG, so a declared radius near 2^32 cannot wrap it into a small one: `2 * r + 1` in all seven rungs.",
      "THE LAST-SAMPLE OFFSET IS COMPUTED AS AN INDEX AND GIVEN A NAME, because that is where the fencepost lives and naming it is what makes the one-character difference legible: `+ taps + n - 1` in all seven rungs.",
      "THE COEFFICIENTS COME FIRST IN THE WINDOW AND THE SAMPLES LAST, so the sample array ends at the window's end and an off-by-one leaves the window rather than landing on a neighbouring field: `8 + taps` is the sample base in all seven rungs.",
      {
        "c": "EVERY TAP IS A PRODUCT OF ONE SAMPLE AND ONE COEFFICIENT, ACCUMULATED INTO A 32-BIT WRAPPING SUM, and the tap loop's SPELLING is deliberately not pinned because comparing spellings is what p10 is for: `s = s + (uint32_t)` in both C rungs (unsigned, 6.2.5p9).",
        "rust": "EVERY TAP IS A PRODUCT OF ONE SAMPLE AND ONE COEFFICIENT, ACCUMULATED INTO A 32-BIT WRAPPING SUM: `s = s.wrapping_add(` in all four Rust rungs, and the product is `.wrapping_mul(`. The tap loop's SPELLING is not pinned -- indexed, windows() and get_unchecked are all in contract -- and that freedom is the experiment."
      },
      {
        "c": "...and the multiplication is the one operation the loop performs. Rust spells it wrapping_mul; C has no such spelling and writes the operator: `* (uint32_t)` in both C rungs.",
        "rust": "...and the product: `.wrapping_mul(` in all four Rust rungs."
      },
      {
        "c": "THE OUTPUT VALUE IS FOLDED, in order, so a rung that applied the coefficients in the wrong order or dropped a tap cannot produce the same checksum: `acc = acc * 31 + (uint64_t)s;` in both C rungs.",
        "rust": "THE OUTPUT VALUE IS FOLDED, in order: `.wrapping_add(s as u64)` in all four Rust rungs."
      },
      {
        "c": "...and the OUTPUT COUNT is folded once at the end, so a rung that computed a different number of outputs -- which is exactly what an off-by-one does -- cannot produce the same checksum either: `* 31 + (uint64_t)nout` in both C rungs.",
        "rust": "...and the OUTPUT COUNT is folded once at the end: `.wrapping_add(nout as u64)` in all four Rust rungs."
      },
      "the little-endian u32 header fields are decoded with + and * rather than | and <<, so the header decode is linear arithmetic and stays out of the way of the tap loop this pattern measures: `+ 65536 *` in all seven rungs.",
      "...and their top bytes: `+ 16777216 *` in all seven rungs."
    ],
    "forbidden": [
      "`chunks_exact`",
      "`from_le_bytes`",
      "`.sum(`",
      "`step_by(`",
      "`copy_from_slice`"
    ],
    "why": "each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (../spec.md's second sentence). THE ONLY THING R1 GETS WRONG IS ONE CHARACTER, AND IT IS IN A COMPARISON BOTH C RUNGS ALREADY PERFORM. `last` is the window offset of the LAST sample byte the kernel will read, so the test that keeps it inside the window is `last >= len`; c/kernel.c writes `last > len`, which admits `last == len` -- EXACTLY ONE BYTE past the window and not a byte more. Every other line of the two C cells is character for character identical, so `c-gcc-h` minus `c-gcc` is the price of that one character and of nothing else. THAT IS A DIFFERENT SHAPE FROM EVERY EARLIER PATTERN HERE: p02's, p07's, p16's, p17's and p18's R1 OMITS A LINE, so hardening adds instructions (+5 gcc / +12 clang on p02, +2.00 per executed pop on p03, per input byte on p18). p10's R1 already executes the comparison and merely relates its two operands wrongly, so the hardened cell is the same instruction stream with one opcode byte changed (`ja` -> `jae`) and the hardening cost is expected to be ZERO. ../NOTES.md 4 measures it rather than assuming it. THE BUG IS CONDITIONAL ON ATTACKER DATA AND THAT IS FORCED BY THE GATE, not chosen for elegance: `harness/check.py` stage 2 requires every cell including R1 to print `model.py`'s checksum on every non-`adversarial-*` input, so a bug that fires on a well-formed window could not be shipped at all. `inputs/gen.py` packs every benign window exactly full (`stride == 8 + taps + n`, so `last == len - 1`), and the two rungs are then behaviourally identical on every benign input -- which is also what makes the R1-vs-R1h COST comparison legal here where `.memory/02-bench-rules.md`'s first rule forbids it on p12 and p13: on every input the cost is measured on, the unhardened rung commits no undefined behaviour and refuses no work. THE HARM IS EXACTLY ONE BYTE OF OVERREAD, WHICH IS THE POINT AND NOT A WEAKNESS. An off-by-one at a boundary cannot reach further than one element by definition, and `adversarial-farover.bin` is the row that says so: a window declaring `n` far beyond what it holds is rejected by R1 and R1h ALIKE, so R1's defect buys an attacker one byte and nothing more. Whether that byte is observable is a property of the ALLOCATION and not of the program, which is p02's result on the read side: `adversarial-fencepost.bin` puts the window at the very end of the payload so the read leaves the allocation and ASan fires, and `adversarial-fenceslack.bin` is the SAME window with three trailing payload bytes that do not form a further window, where the identical off-by-one reads a byte that is merely the wrong one -- ASan clean, UBSan clean, exit 0, and a wrong answer. THE ALGORITHM IS A WEIGHTED FIR AND NOT A BOX FILTER, AND THAT IS A CORRECTNESS REQUIREMENT ON THE COMPARISON RATHER THAN A TASTE. A box filter (all weights equal) has an O(n) running-accumulator form -- add the entering sample, subtract the leaving one -- and an O(n*r) tap-loop form, and a ladder in which any rung reached for the first while the others used the second would be comparing two different algorithms with different complexities. A per-tap coefficient `w[j]` makes the incremental form impossible for every rung in every language at once, so O(nout * taps) is honest by construction and the `you pessimised C` objection has no purchase. It is also the shape real DSP and image code has. ../NOTES.md 0 records the rejected candidates. THERE IS NO DIVISION ANYWHERE ON THE OUTPUT PATH, DELIBERATELY. A FIR is normally normalised by the coefficient sum, and a per-output `div` would cost ONE `Ir` to callgrind (`.memory/03-measurement.md`, the `div` pricing section) and tens of variable cycles to the machine -- so it would be nearly free in the column this project publishes and expensive in the one it cannot measure well, and it would sit inside every per-tap law p10 fits. The kernel sums into a `u32` and folds the raw sums; the disassembly of all eight cells is checked for `div`/`idiv` and contains none (../NOTES.md 1). ALL ARITHMETIC IS WRAPPING, SO THERE IS NO OVERFLOW OBLIGATION TO DISCHARGE AND NO PRECONDITION ON VALUES. `s` is a `u32` accumulated with `wrapping_add`/`wrapping_mul` in Rust and with C's unsigned arithmetic (6.2.5p9) in C, and the fold is the project's usual wrapping Horner chain. `.sum(` is forbidden for exactly this reason: `Sum for u32` uses `+`, which panics under `-C debug-assertions=on` and under Miri, so a rung using it would behave differently in two of the gate's own configurations while looking identical in the twenty-four measured cells. WHAT IS PINNED IS THE OPERATIONS AND THE TWO GUARDS; WHAT IS DELIBERATELY LEFT FREE IS THE SPELLING OF THE TAP LOOP, AND THAT FREEDOM IS THE EXPERIMENT. p10 exists to ask whether safe Rust's tax is proportional to the NUMBER OF INDEXING OPERATIONS or flat, and the three spellings that answer it -- index every tap (`sam[i + j]`), slice the window once and reduce it (`sam.windows(taps)`), and `get_unchecked` -- differ in nothing but that. Pinning a loop form would delete the question. What is pinned instead is that every rung computes the same `2r+1` products of the same operands in the same order into the same wrapping `u32`, that both guards are present in every rung, and that the header is decoded the same way. `windows(` is NOT forbidden and NOT required: it is the R3 idiom this project has never used, `grep -rn 'windows(' patterns/*/*.rs` returned nothing before p10, and it takes a RUNTIME size -- verified by compiling `sam.windows(taps)` where `taps` is read out of the file (../NOTES.md 0.1) -- so it needs no compile-time radius and costs no `div`, which `chunks_exact` with a runtime size does (`.memory/03-measurement.md`). `chunks_exact` is forbidden because a RUNTIME chunk size computes `len - len % chunk_size` and lowers to a hardware `div`, which callgrind prices at 1 `Ir` and the machine at tens of cycles -- it would sit inside p10's per-tap law and be invisible in the column that law is fitted on -- and because p16 measured that the chunk width alone moves that pattern's per-byte rate over a 31% range. `from_le_bytes` deletes the written-out little-endian header decode every rung shares AND is not available to an R4 at all at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW and again on p06, p14 and p18), so a rung using it would compare a safe cell against an unsafe cell that cannot exist. `.sum(` is forbidden for the wrapping reason above. `step_by(` is forbidden because it would let a rung visit a subset of the taps and still satisfy every other entry here. `copy_from_slice` is forbidden because p10's kernel WRITES NOTHING ANYWHERE -- it has no destination buffer, no scratch and no table -- and a rung that materialised the window would be measuring an allocation this pattern does not have. EVERY EXCLUSION HERE IS WHOLE-PATTERN AND NOT SCOPED TO SOME RUNGS, which is deliberate: `.memory/01-ladder.md`'s direction test fired on p13 exactly because three of its entries named some rungs and exempted `safe_tuned.rs`, so R3 was permitted a spelling R4 was forbidden and 48%/17% of the published margin was the pin. A whole-pattern exclusion keeps the two sides of the comparison equal. Nothing in `required` is scoped to a subset of rungs either; the per-language keys on entries 0 and 5..8 exist because C and Rust spell the same operation differently, not because some rungs are exempt. THE FOLD IS OVER THE FULL RECORDED EXTENT AND ORDER-SENSITIVE, and p10's reason is TASK_004_REVIEW's ELISION reason plus one that is p10's own. Elision: a fold that read only part of the output would let the optimiser delete the rest of the tap loop, which is the entire kernel. p10's own: the bug changes WHETHER THE KERNEL RUNS AT ALL on the input that triggers it -- R1h returns 0 where R1 returns a fold -- so the fold sees it structurally and not only through the value of the one stolen byte, and `nout` is folded at the end so a rung computing a different number of outputs cannot produce the same checksum either. That matters because the stolen byte MAY be zero, and its coefficient may be small: p06's lesson is that a sum-fold cannot observe a permutation, and the analogue here would have been a fold that could not observe a single extra tap. Checked in ../NOTES.md 2 rather than asserted.. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither."
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
      "verus.rs": 10
    },
    "twin_obligations": {
      "verus.rs": 11
    },
    "obligations_note": "10 = u32_at 0 + dotp 1 + fwalk 1 + fir_fold 0 + kernel 3 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained, and the zero terms are checkable the same way: u32_at and fir_fold are NON-RECURSIVE spec fns and report 0, while dotp and fwalk are RECURSIVE and carry one termination query each; buf_get_unchecked, load_input and emit are external_body and report 0. kernel's 3 = body + TWO loop bodies (the output walk and the tap loop), and BOTH loops exit exactly one way, so neither needs `invariant_except_break` -- which is a difference from p18, whose two loops both exit early. There is no `by (bit_vector)` and no `|` or `<<` anywhere in this file: the header decode is written with + and * and the kernel performs no other bit operation at all, so the whole proof stays in linear arithmetic. p10 declares NO `const`, so there is no const query -- unlike p03, p06, p08 and p18 -- and `global size_of usize == 8;` carries none either, which is checkable by the arithmetic above summing to exactly 10. **That declaration is p10's one genuinely new Verus fact and it was MEASURED, not guessed**: Verus treats `usize` as architecture-independent, so `2 * r + 1` on a `usize` built from four header bytes is `possible arithmetic underflow/overflow` without it (exact error text in ../NOTES.md 6), and p07 dodged the identical obligation by computing its length check in `u64` -- a route p10 cannot take, because ../spec.md pins the spelling `2 * r + 1` in all seven rungs. It is CHECKED against the compilation target rather than assumed, so it adds nothing to the TCB. main's 5 is quoted AS MEASURED and does not decompose from the command line: body + driver loop + one per by-block would predict 6 and Verus reports 5, the identical off-by-one p03's, p05's, p06's, p07's, p11's, p12's, p14's, p17's and p18's spec.md record for the identical driver. `.memory/04-verus.md`'s one-query-per-function-plus-one-per-loop rule of thumb gives 8 here and is therefore not the derivation.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 10 shipped + 1, and the term is measured the same way: `--cfg slb_twin --verify-function slb_twin_buf_get_unchecked --verify-root` reports `1 verified`. It is +1 rather than +3 because load_input and emit state NO `ensures` and contain NO `unsafe`, so they are outside the twin regime (`.memory/04-verus.md`: the regime is keyed on `external_body` + a non-empty `ensures` OR `unsafe`). p10 has the same three-item trusted base as p18, one item with a `requires`, and for the same structural reason: its kernel performs exactly ONE kind of memory access, a byte read of the input window, so there is exactly one accessor to trust. There is no scratch, no output buffer, no bulk copy and no write of any kind. **What differs from p18 is that on p10 that one `requires` IS the pattern's bug** -- `i < v@.len()` is exactly what `c/kernel.c`'s `last > len` fails to establish -- where p18's accessor precondition had nothing to do with its arithmetic defect. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg.",
    "unsafe_justifications": {},
    "items": {
      "verus.rs": {
        "u32_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "dotp": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fwalk": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fir_fold": {
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
            "r == fir_fold(buf@, off as int, len as int)"
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
    "note": "work_per_call is **taps** -- one multiply-accumulate -- i.e. `nout * taps`, and NOT bytes of the window. p10's kernel reads every sample byte `taps` times and every coefficient byte `nout` times, so a floor denominated in window bytes would understate the work by a factor of `taps` and would be cleared on every input without testing anything -- exactly the 'skipping walker denominated in buffer bytes' shape harness/check.py names. WHICH WAY THE ESTIMATE ERRS: it is EXACT on both probe inputs and LOW elsewhere. model.py takes the MINIMUM over the blob's windows, because the driver's `k` is pseudo-random and the model cannot know which windows a given `n_iters` visits; inputs/gen.py emits small.bin and large.bin with every window carrying the same `(n, r)`, so the minimum IS the value for every call. small is 96 windows of (n=72, r=4): taps 9, nout 64, 576 taps/call. large is 32768 windows of (n=136, r=8): taps 17, nout 120, 2040 taps/call. The two shapes differ in BOTH structural parameters, which is what check.py's d(Ir)/d(work) assertion across two probe shapes needs. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per tap applies unchanged, and the margin is stated as a MEASUREMENT rather than as an argument that the loop cannot vectorise: **p10's tap loop DOES vectorise** at -O3 to an SSE2 body of 17 instructions per 8 samples, i.e. 2.125 Ir/tap, which is the smallest per-tap figure any p10 cell reaches and is 8.5x the floor (../NOTES.md 8). That is the opposite of p18's argument for the same default and is the honest form of it here. work_unit_bits is 16 -- one sample byte and one coefficient byte are consumed per tap -- so the effective absolute bound under min_ir_per_work would be 0.001953125 x 16 = 0.03125 if p10 declared one, which it does not."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost, on a kernel whose load-bearing obligation is the SPATIAL one `c/kernel.c` gets wrong by a single character. The byte-identity result now covers a nested loop over a RUNTIME radius whose safety rests on `8 + taps + n - 1 < len` -- an index bound, not a length bound -- and it holds with no lemma in the kernel at all: the only ghost lines in `kernel` are two `assert`s unfolding a recursive spec fn at its base case, plus the `spec_slice_len` mention. **The pin has no measured price on p10**, which is worth recording because p06's and p14's did: both had to bind a value to a local before a store, because R5's store is a CALL and R4's is an assignment. p10 has no store at all -- it writes nothing anywhere -- so the argument-evaluation-order problem that broke their -O0 identity has nothing to act on here. At O0 the crate names differ in length so call displacements differ -- link layout, not codegen -- which is why O0 is pinned `norel` and O3 `exact`."
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
    "reason": "R4 and R5 ARE byte-identical at O3, and since TASK_010 that does not make Miri optional: it is mandatory for any pattern with a trusted item.",
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
p05's, p07's and p18's reason: p10's payload names no allocation size, and the
kernel has no buffer at all.

**These are the CHECKED rungs' exit codes — and on p10 they are also R1's, on
every input.** R1's defect is a one-byte overread, which faults nothing on a
heap allocation of any realistic size, so every C cell exits 0 on every row
including the adversarial ones. What sees it is ASan, and only when the byte is
outside the allocation. See `NOTES.md` 7.

## Degenerate shapes

`stride_w >= 8 && stride_w <= n_blob` is the driver's whole input validation. A
stride below 8 cannot hold the header (`adversarial-stride7.bin`); a stride above
`n_blob` leaves no whole window, so `nwin` would be 0 and `k` would have nothing
to index. Either way the loop is skipped and the driver prints `0` after **zero**
kernel calls.

`degenerate.bin` carries the shapes the contract has to decide, and **every rung
including R1 agrees on it**, which is why it is not named `adversarial-*` and
the gate holds all eight cells to `model.py` on it:

| window | what it is |
|---|---|
| `r = 0` | `taps = 1`, a one-tap "FIR": a pointwise multiply. `nout = n`, and `windows(1)` is the R3 spelling's own degenerate case. |
| `n == taps` | exactly one output — the sliding window does not slide. |
| `n < taps` | the window guard fires and the call returns 0 without touching a sample. |

The kernel's `len < 8` guard is, given the driver's `stride_w >= 8`, unreachable
in this benchmark. It is kept anyway so the kernel is **total** and its
`requires` stays purely structural.
