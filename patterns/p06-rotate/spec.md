# p06 — in-place rotate: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, and C spells the pair
out. C is handed the blob length and *both* C rungs ignore it — p12's shape.
**Here the number the programmer needed was `sizeof scr`, four lines up in the
same function.**

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     nrec      u32 LE    DECLARED record count       ATTACKER DATA
byte 4..      records, each:
                u32 LE  nelem     DECLARED element count      ATTACKER DATA
                u32 LE  r         THE ROTATE AMOUNT           ATTACKER DATA
                nelem bytes       the elements
data_start = 4
SCR = 64                          the scratch's extent, a compile-time constant
                                  in every rung
```

⚠ **The elements are `u8` and TASK_047 specified `u32`. That is a deliberate
deviation and it is forced by the `identity` pin.** `copy_from_slice` from
`&[u8]` into `&mut [u32]` does not typecheck, and every non-bulk route to a
`u8 → u32` little-endian decode — `chunks_exact`, `try_into`, `from_le_bytes` —
is `is not supported` at the pinned vstd, so with `u32` elements **R4 could not
have had a verifying twin** and the load could not have had one spelling in
every rung, which is the thing this pattern most needs held fixed. `u8` elements
give a genuine `memcpy` in C and a genuine `copy_from_slice` in all four Rust
rungs. The change costs nothing that p06 measures: with `u8` the three reverses
are **still three scalar swap loops** in both compilers, no `pshufb`, no vector
register (measured before the pattern was built — `NOTES.md` 10a). `SCR = 64`
still separates the two regimes, and the scratch is 64 bytes instead of 256.

**Honesty is a property of the file, not of the kernel.** No rung checks that
`nrec` is truthful, no rung checks that `nelem` fits the window, and — the part
that matters — *the specification does not assume `r` is in range*. See "What the
`ensures` is, and what it is not".

## Semantics

```
if len < 4:                                   return 0
nrec from the header
if nrec == 0:                                 return 0     # present in EVERY rung

scr = [0; SCR] ;  acc = 0 ;  p = 4                        # scr is a LOCAL
for rec in 0 .. nrec:
    if len - p < 8:      break                             # subtraction-first
    nelem = u32le(buf[off+p ..]) ; r = u32le(buf[off+p+4 ..]) ; p += 8
    m = min(nelem, SCR)                        # THE CLAMP, present in EVERY rung
    if len - p < nelem:  break
    copy m bytes from buf[off+p ..] into scr[0..m]         # BULK, in EVERY rung
    p += nelem

    # >>> THE SAFETY LINE. R1 omits exactly this and nothing else. <<<
    if m != 0 { r = r % m } else { r = 0 }

    # --- the kernel: rotate scr[0..m] left by r, as three in-place reverses ---
    reverse(scr, 0, r)                         # [0, r)
    reverse(scr, r, m)                         # [r, m)
    reverse(scr, 0, m)                         # [0, m)

    # --- the fold: ORDER-SENSITIVE, full extent of the live region ---
    for i in 0 .. m:  acc = acc *64 31 +64 scr[i]
    acc = acc *64 31 +64 m
return acc *64 31 +64 nrec
```

`*64`/`+64` are wrapping, as in every earlier pattern, so the kernel has **no
precondition on values** and every measured input is inside the verified domain
by construction. C's unsigned types wrap by definition (6.2.5p9) and the Rust
rungs write `wrapping_add`/`wrapping_mul`.

### The safety line is a DIVISION, and every earlier one was a compare

`r %= m` is a hardware `div` on a runtime divisor. `.memory/03-measurement.md`
records that callgrind prices a `div` at exactly **1 `Ir`**; Cascade Lake prices
it at tens of cycles. So p06 is the first pattern here where the project's
primary metric understates the safety tax **by construction, with a known
mechanism** — and `.memory/01-ladder.md` finding 3's *"`Ir` and wall clock
disagreed in direction on the same source"* stops being an accident and becomes
the design.

Measured before any rung was written (`NOTES.md` 0), and **the prediction it was
built on is wrong in sign**:

| | `Ir` per record | ns per record | |
|---|---:|---:|---|
| clang `R1h − R1` | **−11.00** | **+2.3 (+5.5%)** | the two columns **disagree in sign** |
| gcc `R1h − R1` | **+1.00** | **+5.0 (+9%)** | `Ir` understates ≈ 60× |

The `div` itself costs exactly `+1.00 Ir` on both compilers, confirming
`.memory/03-measurement.md`'s rule on a second kernel. The rest is codegen:
reducing `r` proves `r < m <= 64`, which lets clang merge the four-byte
little-endian decode of `r` into one `mov` where the unreduced rung needs seven
instructions. **The safety line pays for itself twelve times over in
instructions and costs 5–9% in time.**

### Two regimes, separated by SCR, and only one is a memory-safety event

`reverse(scr, 0, r)` swaps `scr[i]` with `scr[r-1-i]`, so its highest index is
`r - 1`:

| regime | condition | what happens |
|---|---|---|
| **1** | `m <= r <= SCR` | the unreduced rotate stays **inside** the array. R1 computes `scr[i] = old[r - m + i]`, a rotation of bytes the record never wrote — a wrong answer with **no** out-of-bounds access. Both C rungs print the *same* wrong value; nothing panics, ASan+UBSan are clean, and the delete-the-check controls in every Rust rung reproduce C's answer bit-for-bit rather than panicking. |
| **2** | `r > SCR` | the first reverse leaves the fixed local. Magnitude- and compiler-dependent, p12's ladder. |

**The boundary is `r > SCR`, not `r >= SCR`**, and `adversarial-inarray.bin`'s
third record sits exactly at `r == SCR == 64` — the boundary from the safe side,
p12's `adversarial-exact` analogue.

**p06 does NOT inherit `.memory/02-bench-rules.md`'s WRITE rule.** That section's
threshold test is what decides it: the guard's threshold here is
`m = min(nelem, SCR)`, which is at most and usually strictly *inside* the
destination's extent, so *"the guard fired"* and *"the unguarded rung committed
UB"* are **independent** events. Regime 1 is exactly where they separate. p12,
p23 and p25 inherit because their threshold **is** the extent; p06 sits with
p24. This is the first time that test has been applied to a pattern being built
rather than to one being audited, and it changes the input design: p06 can have
an adversarial row where the guard fires and the sanitizer is silent, and p12
structurally cannot.

What p06 shares with p12 is the *other* half: `small` and `large` must be rows on
which R1 agrees, because `harness/check.py` holds every cell to `model.py` on
every non-adversarial matrix input. Here that is cheap rather than structural —
every `r < m` makes the reduction a no-op — which is why `degenerate.bin` can
also be an agreeing row while exercising `m == 0`, `r == 0`, `r == m` and
`nelem > SCR`.

### The rotate is three reverses, and the fold must be order-sensitive

`reverse(0,r) ; reverse(r,m) ; reverse(0,m)` is the standard in-place rotate:
`2m` element visits, no temporary. Two consequences the pattern is built on.

**First, the fold must be order-sensitive over the full live extent, and p06
supplies a second and independent reason for that rule.** TASK_004_REVIEW's
reason is **elision** — a fold that reads only part of the result lets the
optimiser delete the rest. p06's is **invariance**: three reverses compose to a
**permutation**, so whenever `r <= SCR` the buggy and the correct scratch are the
same *multiset*, and a sum-fold or an xor-fold could not tell them apart on any
input. A pattern about a rotation cannot be checked by a commutative fold.

**Second, the second reverse's range `[r, m)` is empty when `r > m`**, in every
rung, because `a < b` is false. That is not defensive coding: it is what makes
regime 1 well-defined rather than a crash, and it is why the unreduced triple
composes to a rotation of a window the record never wrote.

**That the decomposition survives `-O3` is measured and not assumed**
(`NOTES.md` 0 and 1): three scalar swap loops in both compilers and all four
Rust rungs, 8 instructions per swap under clang and 10 under gcc, no `memmove`,
no shuffle, no vector register anywhere in the rotate.

### The swap count is `m + [m even AND r odd]`, and TASK_047's law was wrong

A reverse of a half-open range of length `L` runs `ceil(L/2)` iterations, not
`L/2` and not `L`. So

```
swaps(m, r) = ceil(r/2) + ceil((m-r)/2) + ceil(m/2) = m + [ m even AND r odd ]
```

zero fitted parameters. The rotate amount therefore **does** enter the cost, as a
**parity term worth one swap per record** — 8 `Ir` under clang — and not as a
linear coefficient. `r == 0` is a third case, cheaper again by the first loop's
3-instruction preamble. Swept and exact on both parities of `m`: `NOTES.md` 2.

### Load-bearing, do not "improve"

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug. Edit both or neither.

- **The scratch is a fixed-size local of `SCR` bytes in all seven rungs**, never
  an allocation and never a length from the file, and **zero-initialised on every
  call in every rung**. The zero-initialisation is what makes regime 1
  deterministic and identical across rungs, which is the finding.
- **The kernel must not mutate `buf`.** The driver calls it `n_iters` times and
  every call must return the same value; the scratch *copy* is what makes an
  in-place pattern legal in this benchmark at all.
- **The clamp `m = min(nelem, SCR)` is present in every rung, R1 included**, so
  the copy is bounded everywhere and the bug is the rotate alone.
- **The load into the scratch is the same bulk spelling in every rung** —
  `memcpy` in C, `scr_load` (whose body is
  `dst[..n].copy_from_slice(&src[from..from + n]);`) in all four Rust rungs, and
  R5's trusted wrapper with that same body. ⚠ p13's review blocker 3: the libc
  routines each rung calls are listed beside every kernel-exclusive figure in
  `NOTES.md` 3, and every rung here calls exactly `memcpy` and nothing else.
- **The cursor guards are subtraction-first** (`len - p < 8`, `len - p < nelem`)
  in all seven rungs. `p <= len` is maintained by the guards themselves, so the
  subtraction cannot wrap; the additive `p + 8 > len` overflows `usize` and Verus
  rejects it. p07's lesson on a second pattern — the spelling that makes the
  proof trivial is the one that makes the bug impossible — and it is what keeps
  the kernel's `requires` at **one** clause.
- **The SPELLING OF THE SWAP is deliberately NOT pinned**, and that is the point
  of the pattern. R1, R1h, R2, R4 and R5 write the four-statement indexed swap;
  R3 writes `split_at_mut` + `zip` + `mem::swap`. **The same disjointness fact,
  discharged four ways, with four different trusted bases** — `NOTES.md` 6.
- Wrapping arithmetic throughout.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == rotate_fold(buf, off, len)
```

`rotate_fold` is the spec function; `model.py` is its independent Python twin —
and independent in a way earlier patterns' were not: `model.py`'s helper computes
the rotation in **closed form** (`out[i] = scr[i + r]` or `scr[i + r - m]`) and
reverses nothing, while its simulation performs the three reverses. The two agree
on every input, which is the `lemma_three_reverses` algebra checked a third way.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included, and `harness/check.py` evaluates it at every one of the
kernel calls to prove that it does. `nrec`, `nelem` and `r`, all 2^32 values of
each, and every byte of the window are *arguments* of the problem; the kernel is
total in all of them.

**It is ONE clause**, as on p03, p11 and p12 and unlike p17 — and keeping it at
one cost a spelling choice (subtraction-first guards) rather than a precondition.

### What the `ensures` is, and what it is not

**It is the FUNCTIONAL postcondition, and that is the whole point.** It says the
scratch ends up *rotated left by `r mod m`*, through `rot_left`, with
`lemma_three_reverses` connecting the three reverse loops to it. A
memory-safety-only spec **accepts** the buggy kernel in regime 1, where nothing
leaves the array; this one **rejects** it in both regimes. That is p06's
`_msonly` mutant and it is the first on this project that carries a *shipped,
realistic* bug rather than a constructed mutation (`NOTES.md` 7).

It is the complement of **p09**, where the bug went invisible *even to the spec*
once the spec moved with it. Here the two specs disagree on the same program.

**And there is a second thing the `ensures` deliberately does not say: that
`nrec` is honest, that `nelem` fits, or that `r` is in range.**
`adversarial-inarray.bin`, the three `adversarial-past*.bin` rows and
`degenerate.bin` are all inside the verified domain and every checked rung agrees
with `model.py` on all five. Writing the stronger precondition would have been an
assumption about the contents of a file that no honest loader can discharge
(`.memory/02-bench-rules.md`), and it would have deleted every row the pattern
exists for.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p06's payload is p11's, p03's, p12's, p16's, p17's,
p05's and p07's:

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes`, reused verbatim, with **nothing added to `common/` for
p06**.

Nothing is a compile-time constant except `SCR`, which is the *scratch's* extent
and a property of the program rather than of the input: `n_iters`, `stride`,
`n_blob`, every `nrec`, every `nelem`, every `r` and every byte come from the
file.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here.

## Driver loop

Identical in all seven rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers, and byte-for-byte p12's. `harness/check.py` normalises every copy — the
C one included — and diffs it against `driver.canonical` below.

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

`stride_w >= 4` because p06's window header is the 4-byte `nrec` field.
`adversarial-stride3.bin` attacks it. The comparison is in `u64` *before* the
`as usize` cast, so a truncating driver cannot sneak a 2^40 stride past it.

### Why this does not evaporate

Same mechanism as every earlier pattern: `k` is derived from `acc`, and `acc`
from the previous call's result, so call *i+1* cannot begin until call *i* has
returned. Nothing to CSE, nothing to hoist, no `black_box` and no `asm volatile`.

### Why every adversarial input is exactly one window

`k` is pseudo-random over `[0, nwin)`, so with several windows a malformed one
would be hit only probabilistically. With `nwin == 1`, `k` is always 0 and `off`
is always 0, so R1's overrun happens on every call deterministically.

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
| `verus.obligations` = 17 | **`SCR` 1 + `fold_scr` 1 + `walk` 1 + `lemma_rev_noop` 1 + `lemma_rev_step` 1 + `lemma_three_reverses` 1 + `kernel` 6 + `main` 5 = 17.** Every term was measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, and so were the zero terms. `kernel`'s 6 is 1 body + 1 per loop body (**five** loops: the record walk, the three reverses and the fold), the most of any pattern here. `rev_range` and `rot_left` are **closed forms** rather than recursions and contribute 0, which is the choice that made this proof cheap. |
| `verus.twin_obligations` = 22 | the count under `--cfg slb_twin`. **17 shipped + 5**, and it is +5 rather than +4 because `slb_twin_scr_load` is an indexed **loop**, so it carries two queries where the three accessor twins carry one each. ⚠ That is p02's wrinkle for a *narrower* reason than p02 and `.memory/04-verus.md` give: the pinned vstd **does** specify `<[T]>::copy_from_slice` (`vstd/std_specs/slice.rs:205`), and what `scr_load` axiomatises is the `&mut [u8; 64]` → `&mut [u8]` range **reborrow** write-back. `NOTES.md` 6. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`, and since TASK_010 that does not make Miri optional: it is mandatory for any pattern with a trusted item. On p06 the argument is stronger than usual, because one accessor **writes** and is called twice per swap, and a second axiomatises a **bulk** copy — see the `miri.reason` key. |


```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == rotate_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (rotate_fold). p06's bindings are the READ-ONLY set p03, p11, p12, p16, p17, p05 and p07 use and NOT p02's before/after set, and the reason is worth stating because p06 is a WRITE pattern: the scratch is a fixed-size LOCAL inside the kernel, so no buffer crosses the signature and there is nothing for a `scr_after` binding to name. That is p03's and p12's shape. The security property is therefore carried by the trusted accessors' discharged `requires` -- and on p06 that includes a WRITE accessor, `scr_set_unchecked`'s `i < old(v)@.len()`, called TWICE per swap, which is what excludes both of the stores R1 performs past `scr[SCR]`. **The `ensures` is the FUNCTIONAL one and that is the whole point of the pattern**: it says the scratch ends up ROTATED LEFT BY `r mod m`, via `rot_left`, and `lemma_three_reverses` is what connects the three reverse loops to it. A memory-safety-only spec ACCEPTS the buggy kernel in regime 1 (`m <= r <= SCR`), where nothing leaves the array; this one rejects it in BOTH regimes. That is the mutant that earns its keep (../NOTES.md 7), and it is the complement of p09, where the bug went invisible even to the spec once the spec moved with it. **What the `ensures` deliberately does NOT say is that `nrec` is honest, that `nelem` fits the window, or that `r` is in range.** `walk` specifies what the PROGRAM does -- stop when the window runs out, reduce the rotate amount, rotate, fold -- so adversarial-inarray.bin, the three adversarial-past*.bin rows and degenerate.bin are all INSIDE the verified domain and every checked rung agrees with model.py on all five. A `requires` that `r` were in range would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete every row the pattern exists for.",
  "idiom": {
    "required": [
      {
        "c": "THE SAFETY LINE, and the only line c/kernel.c omits: `r %= m;` in c/kernel_hardened.c. c/kernel.c omits exactly this and nothing else, so the scoped-absent audit pair this entry reports is on that rung and is correct.",
        "rust": "THE SAFETY LINE: `r = r % m;` in all four Rust rungs. In Rust it is a SEMANTIC line and not a safety line -- rustc's bounds check is what makes the safe rungs safe -- so no Rust-vs-Rust comparison moves on it; see the why key."
      },
      {
        "c": "...and its zero arm, which is not decoration: r %= 0 is undefined behaviour and degenerate.bin declares a record with nelem == 0. `if (m != 0)` in c/kernel_hardened.c.",
        "rust": "...and its zero arm, which is not decoration: r % 0 panics and degenerate.bin declares a record with nelem == 0. `if m != 0 {` in all four Rust rungs."
      },
      {
        "c": "THE CLAMP, present in EVERY rung including R1, so the COPY is bounded in every rung and the bug is the rotate alone: `m = nelem < SCR ? nelem : SCR;` in both C rungs.",
        "rust": "THE CLAMP, present in EVERY rung, so the COPY is bounded in every rung and the bug is the rotate alone: `let m: usize = if nelem < SCR { nelem } else { SCR };` in all four Rust rungs."
      },
      {
        "c": "the scratch is a FIXED-SIZE LOCAL of SCR bytes, never an allocation and never a length from the file: `uint8_t scr[SCR];` in both C rungs.",
        "rust": "the scratch is a FIXED-SIZE LOCAL of SCR bytes, never an allocation and never a length from the file: `let mut scr: [u8; SCR] = [0; SCR];` in all four Rust rungs."
      },
      {
        "c": "...and it is ZERO-INITIALISED ON EVERY CALL, which is what makes regime 1 deterministic and identical across rungs: `memset(scr, 0, sizeof scr);` in both C rungs.",
        "rust": "...and it is ZERO-INITIALISED ON EVERY CALL, which is what makes regime 1 deterministic and identical across rungs: `[0; SCR];` in all four Rust rungs."
      },
      {
        "c": "the load into the scratch is a BULK copy in every rung, so the measured difference is the ROTATE and not the load: `memcpy(scr, buf + off + p, m);` in both C rungs.",
        "rust": "the load into the scratch is a BULK copy in every rung, so the measured difference is the ROTATE and not the load: `dst[..n].copy_from_slice(&src[from..from + n]);` in all four Rust rungs (the body of `scr_load`, which in verus.rs is the trusted wrapper itself)."
      },
      "the rotate is three reverses and the second one runs over the range r..m, which is what makes the UNREDUCED triple compose to a rotation of a window the record never wrote instead of failing: `a = r;` in all seven rungs.",
      "...and the third runs over the range 0..m: `b = m;` in all seven rungs.",
      {
        "c": "the fold is byte-at-a-time Horner over the LIVE PREFIX, order-sensitive, spelled with the literal multiplier: `acc = acc * 31 + (uint64_t)scr[i];` in both C rungs.",
        "rust": "the fold is byte-at-a-time Horner over the LIVE PREFIX, order-sensitive, spelled with the literal multiplier: `.wrapping_mul(31)` in all four Rust rungs. safe_tuned.rs spells the LOOP as .iter().fold() over a reslice, which is why only the operation and not the loop form is pinned here."
      },
      {
        "c": "the live extent is folded, so a rung that rotated a different number of bytes cannot produce the same checksum: `acc = acc * 31 + (uint64_t)m;` in both C rungs.",
        "rust": "the live extent is folded, so a rung that rotated a different number of bytes cannot produce the same checksum: `.wrapping_add(m as u64)` in all four Rust rungs."
      },
      {
        "c": "the declared record count is folded, so a rung that walked a different number of records cannot produce the same checksum either: `* 31 + (uint64_t)nrec` in both C rungs.",
        "rust": "the declared record count is folded, so a rung that walked a different number of records cannot produce the same checksum either: `.wrapping_add(nrec as u64)` in all four Rust rungs."
      },
      {
        "c": "the cursor guards are SUBTRACTION-FIRST, which is what keeps the kernel's requires at ONE clause -- p <= len is maintained by the guards themselves so the subtraction cannot wrap, while the additive form p + 8 > len overflows usize and Verus rejects it: `if (len - p < 8)` in both C rungs.",
        "rust": "the cursor guards are SUBTRACTION-FIRST, which is what keeps the kernel's requires at ONE clause -- p <= len is maintained by the guards themselves so the subtraction cannot wrap, while the additive form p + 8 > len overflows usize and Verus rejects it: `if len - p < 8 {` in all four Rust rungs."
      },
      "...and the second guard, which bounds the record's declared length by what the window holds: `len - p < nelem` in all seven rungs.",
      "the little-endian u32 decode is written out with + and * rather than | and <<, so it stays linear arithmetic: `+ 65536 *` in all seven rungs.",
      "...and its top byte: `+ 16777216 *` in all seven rungs."
    ],
    "forbidden": [
      "`.rotate_left(`",
      "`.rotate_right(`",
      "`.reverse()`",
      "`.copy_within(`",
      "`memmove(`",
      "`from_le_bytes`",
      "`chunks_exact`"
    ],
    "why": "each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). THE ONLY THING R1 OMITS IS THE REDUCTION OF THE ROTATE AMOUNT: the clamp `m = min(nelem, SCR)` is present in every rung, so the COPY is bounded in every rung; both cursor guards are present in every rung, so `p` never leaves the window in any rung; every read of the SOURCE is in bounds in every rung. R1-vs-R1h is therefore the cost of `r %= m` and nothing else. THE SAFETY LINE IS A DIVISION AND THAT IS WHY THIS PATTERN EXISTS: callgrind prices a hardware `div` at exactly 1 Ir (`.memory/03-measurement.md`) and Cascade Lake at tens of cycles, so p06 is the pattern where the project's primary metric and its clock disagree BY CONSTRUCTION rather than by accident -- and measured, they disagree in SIGN on clang (../NOTES.md 0). THE `m != 0` ARM IS PART OF THE PINNED CONTRACT AND NOT A MATTER OF TASTE: `r %= 0` is undefined behaviour in C and a panic in Rust, `degenerate.bin` declares a record with `nelem == 0`, and a hardened rung without the arm would introduce a SECOND bug while removing the first. `.rotate_left(`, `.rotate_right(` and `.reverse()` are forbidden because each is a single library call that deletes the three-reverse decomposition the pattern measures -- the `2m` swap law, the `r`-parity term and the whole `sweep-m*`/`sweep-r*` design are statements about that decomposition, and a rung using one of them would measure the standard library's rotate instead, which is p11's comparison wearing p06's label. `.copy_within(` is forbidden for the mirror-image reason: it is the OUT-OF-PLACE rotate (rotate through a temporary), which is a different algorithm with different memory traffic and no in-place aliasing question at all -- and the aliasing question is p06's TCB result. `memmove(` is forbidden on the same ground for the C rungs. `from_le_bytes` deletes the written-out little-endian header decode every rung shares AND is NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW), so a rung using it would compare a safe cell against an unsafe cell that cannot exist -- the `identity`-pin trap this block's own `identity` key sets. `chunks_exact` is forbidden for the fold because p16 measured that the chunk width moves that pattern's per-byte rate over a 31% range (5.04688...6.62500, `.memory/01-ladder.md`), and p06's published decomposition is into a per-copied-byte, a per-swap and a per-record term. EVERY EXCLUSION HERE IS WHOLE-PATTERN AND NOT SCOPED TO SOME RUNGS, which is deliberate: `.memory/01-ladder.md`'s direction test fired on p13 exactly because three of its entries named `safe_naive.rs`, `unsafe.rs` and `verus.rs` and exempted `safe_tuned.rs`, so R3 was permitted a spelling R4 was forbidden and 48%/17% of the published margin was the pin. A whole-pattern exclusion keeps the two sides of the comparison equal. IT IS STILL A FIAT AND ITS PRICE IS STILL PUBLISHED (../NOTES.md 8): `<[T]>::reverse()` and `<[T]>::rotate_left()` are each built on R3 and measured against the shipped cell, and each is separately put through `./verus_run.py` on an R5 twin to find out whether the PROVER already excludes it from R4 -- p13's three-way disposition, applied before the number is published rather than after. WHAT IS DELIBERATELY *NOT* PINNED, and it is the point of the pattern: **the SPELLING OF THE SWAP**. R1, R1h, R2, R4 and R5 write the four-statement indexed swap and R3 writes `split_at_mut` + `zip` + `mem::swap`, and holding those fixed would hold fixed the one thing p06 exists to compare -- the SAME DISJOINTNESS FACT DISCHARGED FOUR WAYS, with four different trusted bases: rustc's bounds check (R2, TCB 0), `core`'s own `unsafe` inside `split_at_mut` and `ptr::swap_nonoverlapping` (R3, TCB = the standard library and audited by nobody in this repository), the programmer's comment (R4, TCB = the whole function), and `scr_set_unchecked`'s discharged `i < old(v)@.len()` (R5, TCB = one clause). ../NOTES.md 6 tabulates them. What IS pinned instead is that the SCRATCH is a fixed-size local of `SCR` bytes, zero-initialised on every call in every rung -- the zero-initialisation is what makes REGIME 1 deterministic and identical across rungs, which is the finding -- and that the rotate is three reverses over `[0,r)`, `[r,m)`, `[0,m)` in that order. THE FOLD IS OVER THE FULL LIVE EXTENT AND ORDER-SENSITIVE, AND p06 SUPPLIES A SECOND, INDEPENDENT REASON FOR THAT RULE. TASK_004_REVIEW's reason is ELISION: a fold that reads only part of the result lets the optimiser delete the rest. p06's is INVARIANCE: three reverses compose to a PERMUTATION, so whenever `r <= SCR` the buggy and the correct scratch are the same MULTISET, and a sum-fold or an xor-fold could not tell them apart on any input. ../NOTES.md 2. THE LOAD IS THE SAME BULK SPELLING IN EVERY RUNG -- `memcpy` in C, `scr_load` (whose body is `dst[..n].copy_from_slice(&src[from..from + n]);`) in all four Rust rungs, and R5's trusted `scr_load` wrapper whose body is that same line -- so the measured difference between rungs is the ROTATE and not the load, which is p02's retraction applied in advance. THAT DECISION HAS A PRICE AND IT IS MEASURED: routing R4's load through the helper rather than writing `scr[..m].copy_from_slice(...)` inline changes LLVM's inlining order and takes R4's kernel from 179 to 208 instructions (`md5_fn f7b24db6bfd9` to `897c52ff4005`), because the helper form lets LLVM clone the record loop for `nelem >= SCR` and inline the 64-byte copy as four `movups`. It is the second measured price the `identity` pin has extracted from a shipped cell, after p12's. ../NOTES.md 3. WHEN THIS DECLARATION WAS WRITTEN, STATED EXACTLY BECAUSE p06 HAS A PRE-FLIGHT: it was written after the five rungs, the R5 proof (17/0), the `identity` pin and the checksums existed and BEFORE any p06 CELL had been measured for perf -- `harness/measure.py p06` had not been run and no `Ir` or `ns` figure for any of the eight cells existed. What DID exist is ../NOTES.md 0: `Ir` and `ns` for a standalone six-kernel C PROBE with no driver, which settled the three prescriptions TASK_047 asked to settle before five rungs were built on them. That probe is not a cell and none of its numbers is published as p06's, but it is not nothing either, and saying 'no number existed' would be false. What the probe could and did influence is the CHOICE OF PATTERN SHAPE (u8 elements rather than u32, so that the bulk load has one spelling in every rung); what it did not influence is any entry of `required` or `forbidden`, every one of which names a line the contract in ../spec.md's Semantics block already had.. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither."
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
      "verus.rs": 17
    },
    "twin_obligations": {
      "verus.rs": 22
    },
    "obligations_note": "17 = SCR 1 + fold_scr 1 + walk 1 + lemma_rev_noop 1 + lemma_rev_step 1 + lemma_three_reverses 1 + kernel 6 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained, and the zero terms are checkable the same way: u32_at, nrec_at, zero_scr, rev_range, rot_left, load_into and rotate_fold are NON-RECURSIVE spec fns and report 0 -- rev_range and rot_left are `Seq::new` CLOSED FORMS rather than recursions, which is the choice that makes this proof cheap and is why p06 has three proof obligations where a recursive spelling would have had five; fold_scr and walk are RECURSIVE and carry one termination query each; buf_get_unchecked, scr_get_unchecked, scr_set_unchecked, scr_load, load_input and emit are external_body and report 0. SCR's 1 is a `const` inside verus!, which `.memory/04-verus.md` records as its own query (measured on p08's SCR and p03's STACK_CAP); p06 is the fourth pattern with one. kernel's 6 = body + FIVE loop bodies -- the record walk, the THREE reverses and the fold -- which is the most loops of any pattern here (p12 has four, p11 three, p07 three, p03 two), and no `by (nonlinear_arith)` sub-proof anywhere in the kernel because `rot_left` is stated with a branch on `i + r < m` instead of a modulo and every multiplication in the decode is by a literal. main's 5 is quoted AS MEASURED and does not decompose from the command line: body + driver loop + one per by-block would predict 6 and Verus reports 5, the identical off-by-one p03's, p05's, p07's, p11's, p12's and p17's spec.md record for the identical driver. `.memory/04-verus.md`'s one-query-per-function-plus-one-per-loop rule of thumb gives 13 here and is therefore not the derivation.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 17 shipped + 5, and each term is measured the same way: `--cfg slb_twin --verify-function slb_twin_<name> --verify-root` reports `1 verified` for slb_twin_buf_get_unchecked, slb_twin_scr_get_unchecked and slb_twin_scr_set_unchecked and **`2 verified` for slb_twin_scr_load**, which is the +5 rather than +4: the checked stand-in for the bulk load is an INDEXED LOOP and the loop body is its own query. That is p02's wrinkle, for a NARROWER reason than p02 and `.memory/04-verus.md` give: the pinned vstd DOES specify `<[T]>::copy_from_slice` at `vstd/std_specs/slice.rs:205`, and what verus.rs's `scr_load` axiomatises is the `&mut [u8; 64]` -> `&mut [u8]` range REBORROW write-back, not the copy (measured at TASK_047, ../NOTES.md 6). Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg.",
    "unsafe_justifications": {
      "verus.rs": {
        "scr_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `u8` is a legal thing to store in a `u8` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [u8; 64]` reads `i < 64`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second and p06 the third, and on p06 the item is the one the whole pattern is about -- it is called TWICE per swap and its `requires` is what excludes both of R1's out-of-bounds stores. A second conjunct `old(v)@.len() == 64` is deliberately NOT written: for a `&mut [u8; 64]` it is a TAUTOLOGY discharged from the parameter type alone by vstd's `array_len_matches_n`, and p03's gate run refused exactly that draft (p03 NOTES.md 5b)."
      }
    },
    "items": {
      "verus.rs": {
        "u32_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "nrec_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "zero_scr": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "rev_range": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "rot_left": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "load_into": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold_scr": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "walk": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "rotate_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "lemma_rev_noop": {
          "external": null,
          "requires": [
            "hi <= lo"
          ],
          "ensures": [
            "rev_range(s, lo, hi) == s"
          ]
        },
        "lemma_rev_step": {
          "external": null,
          "requires": [
            "0 <= a",
            "a < b",
            "b <= s.len()"
          ],
          "ensures": [
            "rev_range(s.update(a, s[b - 1]).update(b - 1, s[a]), a + 1, b - 1) == rev_range( s, a, b, )"
          ]
        },
        "lemma_three_reverses": {
          "external": null,
          "requires": [
            "0 <= r <= m <= s.len()"
          ],
          "ensures": [
            "rev_range(rev_range(rev_range(s, 0, r), r, m), 0, m) == rot_left(s, m, r)"
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
        "scr_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_scr_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "scr_set_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_scr_set_unchecked": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "scr_load": {
          "external": "verifier::external_body",
          "requires": [
            "n <= old(dst)@.len()",
            "from + n <= src@.len()"
          ],
          "ensures": [
            "final(dst)@ == load_into(old(dst)@, src@, from as int, n as int)"
          ]
        },
        "slb_twin_scr_load": {
          "external": null,
          "requires": [
            "n <= old(dst)@.len()",
            "from + n <= src@.len()"
          ],
          "ensures": [
            "final(dst)@ == load_into(old(dst)@, src@, from as int, n as int)"
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
            "r == rotate_fold(buf@, off as int, len as int)"
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
    "note": "work_per_call is **bytes of the window** -- `stride`, 201 on small and 152 on large -- which is p16's, p05's, p11's and p12's denomination. WHICH WAY THE ESTIMATE ERRS: STRICT, by three corrections. It OVER-counts by the 4 header bytes and by the 8 bytes of each record header (decoded as u32s, never copied, rotated or folded) and, on a record with `nelem > SCR`, by the undeclared tail the cursor skips. It UNDER-counts by the whole of the second and third passes: every copied byte is copied, swapped about once by the three reverses and folded, i.e. visited at least three times. On small the visits are 157 + ~157 + 157 = 471 against a declared 201, and on large 52 + ~52 + 52 = 156 against 152, so `stride` is at or below the number of byte-visits on both and the derived floor is one the kernel must clear. large's margin is thin BY DESIGN -- its records are 1..8 bytes, so the 8-byte record header is most of the window -- which makes the floor tighter there than on any earlier pattern, and tighter is the safe direction: it can never let a collapsed kernel through. work_unit_bits is 8, one window byte, so the effective absolute bound under min_ir_per_work is 0.001953125 x 8 = 0.015625. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged, and the argument is p06-specific: the fold is a serial Horner chain `acc = acc*31 + b`, so byte i+1's multiply depends on byte i's and there is no vector form at any -march, and the three reverses are SCALAR SWAP LOOPS in every rung and both compilers -- measured on the disassembly (../NOTES.md 1), which is the pre-flight question TASK_047 asked to be settled before anything was built. The COPY alone can go far below 0.25 -- it is a `memcpy` in every rung -- which is exactly why the unit is denominated over the whole window and not over the copy. The two probe inputs differ in work_per_call (201 vs 152) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost, on the first kernel in this project whose postcondition is a PERMUTATION. The byte-identity result now covers a kernel with five loops, three of them two-cursor reverses carrying the same relational invariant, one mutating a fixed-size array through a trusted setter called twice per iteration, two recursive spec functions, two closed-form ones and ZERO nonlinear arithmetic. The pin has a MEASURED PRICE here and it is in the idiom why: the bulk load has to be spelled as a call to a plain-Rust helper because a range-index inside `verus!` is macro-rewritten even in an external_body item, and giving R4 the same helper takes its kernel from 179 to 208 instructions. At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."
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
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. On p06 there are TWO stronger reasons. First, one of the four accessors WRITES and is called twice per swap: a trusted `scr_set_unchecked` that also wrote `i + 1` would satisfy this `ensures` on slot `i` and be invisible to Verus, to the twin, to the contract pin and to stages 5c/5c-req -- the p08 `copy_nonoverlapping` substitution passed all of those and was caught by the O3 identity pin and Miri alone. Second, `scr_load` axiomatises a BULK copy, and an `ensures` that under-describes what `copy_from_slice` touches is exactly the shape `.memory/04-verus.md` says only Miri on R4 can catch. Cost: check.py rewrites n_iters to 4, so each row copies, rotates and folds at most 4 x 3 x stride bytes -- about 2400 on small and 1800 on large, four orders of magnitude inside `.memory`'s measured 3.05 M budget. The only real cost is the 7.6 MB payload to_vec, and p07's 12 MB one passes.",
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

There is no exit 7 here, for p03's, p11's, p12's, p16's, p17's, p05's and p07's
reason: p06's payload names no allocation size, and the scratch is a fixed-size
local in every rung, so p02's `SLB_MAX_CAP` check would be dead code.

**These are the CHECKED rungs' exit codes.** R1's behaviour is a function of the
overflow magnitude and of the compiler, measured at the gate's own flags:

| input | `r` | bytes past `scr` | c-gcc | c-clang |
|---|---:|---:|---|---|
| `adversarial-inarray` | 40, 50, 64 | **0** | exit 0, wrong answer | exit 0, **the same** wrong answer |
| `adversarial-past1` | 65 | 1 | exit 0, wrong answer | exit 0, a *different* wrong answer |
| `adversarial-past48` | 112 | 48 | **134**, `*** stack smashing detected ***` | exit 0, wrong answer |
| `adversarial-pastfar` | 100000 | 99 936 | **139** | **139** |

`harness/check.py` records that in its adversarial table rather than requiring
it; `NOTES.md` 0 and 7 are where it is read. Note the discriminator the first two
rows give for free: **in regime 1 the two compilers agree with each other and in
regime 2 they do not**, because regime 1's extra bytes are the zero-initialised
scratch and regime 2's are the frame.

## Degenerate shapes

`stride_w >= 4 && stride_w <= n_blob` is the driver's whole input validation. A
stride below 4 cannot hold the header (`adversarial-stride3.bin`); a stride above
`n_blob` leaves no whole window, so `nwin` would be 0 and `k` would have nothing
to index. Either way the loop is skipped and the driver prints `0` after **zero**
kernel calls.

`degenerate.bin` is one window carrying the four shapes the contract has to
decide, and **every rung including R1 agrees on it**, which is why it is not
named `adversarial-*` and the gate holds all eight cells to `model.py` on it:

| record | what it is |
|---|---|
| `nelem = 0, r = 0` | `m == 0`. The hardened rungs would **divide by zero** here; the contract pins the answer, `r = 0`. R1 has no division at all, so this is the record where R1h's guard does work R1 never needed. |
| `nelem = 20, r = 0` | `r == 0`: the first reverse is skipped entirely, which is a *third* case of the `sweep-r*` law and must not be pooled with "r even". |
| `nelem = 12, r = 12` | `r == m`. Reduced it is 0; **unreduced** the triple is `reverse(0,12) ; no-op ; reverse(0,12)` = the identity, so R1 agrees here by composition rather than by luck. |
| `nelem = 100, r = 7` | `nelem > SCR`. The clamp bounds the copy in every rung, so the 36 undeclared bytes are skipped by the cursor and never read. The clamp is not the safety line. |

The kernel's `len < 4` guard is, given the driver's `stride_w >= 4`, unreachable
in this benchmark. It is kept anyway so the kernel is **total** and its
`requires` stays purely structural; the alternative — a `len >= 4` precondition —
would be a precondition about the driver's own guard rather than about the
buffer.
