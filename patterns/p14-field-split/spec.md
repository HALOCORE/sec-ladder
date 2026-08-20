# p14 — delimiter-framed field splitter: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, and C spells the pair
out. C is handed the blob length and *both* C rungs ignore it — p06's and p12's
shape. **Here the number the programmer needed was `MAXTOK`, declared four lines
up in the same file.**

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     nline     u32 LE    DECLARED line count          ATTACKER DATA
byte 4..      lines, each:
                u32 LE  llen      DECLARED line length         ATTACKER DATA
                llen bytes        the line's bytes             ATTACKER DATA
data_start = 4
SCR    = 64                       the scratch's extent
MAXTOK = 16                       the field table's extent
DELIM  = ',' (0x2C)               the field separator
```

`SCR`, `MAXTOK` and `DELIM` are compile-time constants in every rung. They are
properties of the *program* — a CSV reader splits on comma into a fixed table —
and not of the input: `n_iters`, `stride`, `n_blob`, every `nline`, every `llen`
and every byte of every line come from the file.

**Honesty is a property of the file, not of the kernel.** No rung checks that
`nline` is truthful, no rung checks that `llen` fits the window, and — the part
that matters — *the specification does not assume a line holds at most `MAXTOK`
fields*. See "What the `ensures` is, and what it is not".

## Semantics

```
if len < 4:                                   return 0
nline from the header
if nline == 0:                                return 0     # present in EVERY rung

scr = [0; SCR] ; tl = [0; MAXTOK] ; acc = 0 ; p = 4        # both are LOCALS
for ln in 0 .. nline:
    if len - p < 4:      break                             # subtraction-first
    llen = u32le(buf[off+p ..]) ; p += 4
    m = min(llen, SCR)                         # THE CLAMP, present in EVERY rung
    if len - p < llen:   break                             # subtraction-first
    copy m bytes from buf[off+p ..] into scr[0..m]         # BULK, in EVERY rung
    p += llen

    # --- the split: one descriptor per field, into a FIXED table ---
    nt = 0 ; s = 0 ; i = 0
    while i <= m:                              # BOUNDED, in EVERY rung
        if i == m or scr[i] == DELIM:          # `i == m` is a VIRTUAL DELIMITER

            # >>> THE SAFETY LINE. R1 omits exactly this and nothing else. <<<
            if nt == MAXTOK: break

            flen = i - s ; tl[nt] = flen ; nt += 1 ; s = i + 1
        i += 1

    # --- the fold: ORDER-SENSITIVE, over the full recorded extent ---
    cur = 0
    for j in 0 .. nt:
        tj = tl[j]
        acc = acc *64 31 +64 tj                            # the field LENGTH
        for q in 0 .. tj:
            acc = acc *64 31 +64 scr[cur + q]              # the field CONTENT
        cur = cur + tj + 1                                 # step over the delimiter
    acc = acc *64 31 +64 nt                                # the field COUNT
return acc *64 31 +64 nline
```

`*64`/`+64` are wrapping, as in every earlier pattern, so the kernel has **no
precondition on values** and every measured input is inside the verified domain
by construction. C's unsigned types wrap by definition (6.2.5p9) and the Rust
rungs write `wrapping_add`/`wrapping_mul`.

### The bound is a COUNT of a byte value, and every earlier one was a LENGTH

`nt` is one more than the number of `DELIM` bytes in `scr[0 .. m)`. Nothing in
the wire format declares that number, and **no length bounds it**: a 64-byte
line holds anywhere between 1 and 65 fields against a 16-entry table. That is
what makes p14's guard different in kind from p02's, p16's and p17's, all of
which compare a *declared length* against a *buffer extent*, and from p11's and
p13's, which are about a terminator.

Two consequences the pattern is built on:

- **the overflow's magnitude is set by delimiter DENSITY, not by data volume** —
  `adversarial-full65` is a 72-byte window that stores 392 bytes past `tl`; and
- **the safety line cannot be hoisted, folded into a length check, or proved
  from the header.** It has to be tested once per field, inside the scan.

### The library contract decides whether an input is dangerous

`strtok(3)` **collapses** a run of delimiters into a single separator. This
kernel's partition does not, and neither does `strsep(3)`, nor Rust's
`<[T]>::split`, nor Python's `bytes.split`, nor any CSV reader. On
`a,,,,,,,,,,,,,,,,z` — sixteen adjacent commas — `strtok` yields **2** fields and
this kernel yields **17**, against the same 16-entry table. Measured on real
glibc, `NOTES.md` 0.

**That is not a semantic curiosity: it is the difference between a correct parse
and a stack-buffer-overflow WRITE, on byte-identical input.** `adversarial-run17`
is that input.

⚠ **And the honest counterweight, which ships with the claim.** Collapse changes
*which* inputs are dangerous; it does not remove the need for the guard. An
**alternating** line, `a,a,a,...`, has no runs to collapse, so both contracts
produce the same field count — 33 on a 64-byte line, still more than double
`MAXTOK`. `adversarial-alt33` is that row and it is there to stop the overclaim.

### The scan IS bounded, and that is what keeps p14 out of p11's territory

`while i <= m` is present in every rung, R1 included. `.memory/02-bench-rules.md`
listed p14's guard as *"a delimiter is not a bound; the sentence reaches its
scan's `i < len`"* — **and that row is now settled as "not as stated", by
building it.** A tokenizer whose scan is bounded only by the delimiter *is* p11:
the omitted line is literally `i < m`, the harm is an out-of-bounds READ of the
scratch, and the loop body is p11's `strlen` shape. It was built as
`k_unbnd` in the §0 probe and rejected for exactly that reason (`NOTES.md` 0).
p14's bug is one level up, in the OUTER loop, and every read of `scr` in every
rung is in bounds.

### Truncation is the hardened behaviour, and the contract pins it

Once the table is full, R1h and all four Rust rungs stop recording fields and
fold the sixteen they have. That is what `strtok`, `getopt`, `argv` splitters and
every fixed-table CSV reader do, and it is p13's shape one level up: **the
hardened cell is memory-safe and LOSES DATA.** Pinning it here is what stops the
checked rungs from disagreeing about it, and it is why `ntok()` — the truncation
— is inside the *specification* rather than left to the rung.

### The fold must be order-sensitive, and p14 is the THIRD independent reason

TASK_004_REVIEW's reason for the full-extent fold is **elision**: a fold that
reads only part of the result lets the optimiser delete the rest. p06's is
**invariance**: three reverses compose to a permutation, so a sum- or xor-fold
could not tell the buggy scratch from the correct one on any input.

p14's is **partition-blindness**, and it is one level up from p06's:
**tokenising does not move any byte.** Every partition of the same line yields
the same bytes in the same order, so a fold over the concatenated *content*
alone is identical for every possible field boundary — it cannot see a boundary
bug at all. What makes a boundary visible is folding the **lengths in order**,
and what makes a *truncation* visible is folding the **count**. p14 folds all
three, and each is load-bearing against a different mutation:

| folded | what it catches |
|---|---|
| the field **count** `nt` | a rung that truncated at a different `MAXTOK`, or not at all |
| each field's **length** `tj`, in order | a rung that put a boundary in the wrong place |
| each field's **content**, in order | a rung that read the wrong bytes |

Say it beside the other two whenever the rule is quoted: three patterns, three
independent arguments, one rule.

### Load-bearing, do not "improve"

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug. Edit both or neither.

- **The scratch is a fixed-size local of `SCR` bytes in all seven rungs**, never
  an allocation and never a length from the file, and **zero-initialised on every
  call in every rung**.
- **The field table is a fixed-size local of `MAXTOK` `size_t`/`usize` entries in
  all seven rungs.** It is the destination the bug overflows, and its extent is a
  compile-time constant so that R1's overrun is a property of the *program*
  rather than of an allocation the input chose.
- **The kernel must not mutate `buf`.** The driver calls it `n_iters` times and
  every call must return the same value; the per-call scratch copy is what makes
  a tokenizer legal in this benchmark at all — and it is the measurement that
  excludes the catalogue's guessed bug class. `NOTES.md` 0.
- **The clamp `m = min(llen, SCR)` is present in every rung, R1 included**, so
  the copy and the scan are bounded everywhere and the bug is the field count
  alone.
- **The load into the scratch is the same bulk spelling in every rung** —
  `memcpy` in C and `scr_load`, whose body is the one bulk call
  `.copy_from_slice(&src[from..from + n]);` in all four Rust rungs. ⚠ **The
  receiver is scoped 2-and-2**, exactly as p06's: `safe_naive.rs` and
  `safe_tuned.rs` write `dst[..n]`; `unsafe.rs` and `verus.rs` write `a` after
  `let (a, _b) = s.split_at_mut(n);`. `RangeTo<usize>` has no
  `SliceIndexSpecImpl` at the pinned vstd, so `dst[..n]` cannot be *verified* at
  all, and R4 follows R5 because the `identity` pin makes them one program. The
  price is measured in `NOTES.md` 6a. ⚠ p13's review blocker 3: the libc routines
  each rung calls are listed beside every kernel-exclusive figure in `NOTES.md` 3.
- **`i == m` is the virtual delimiter, in all seven rungs.** It is what makes the
  tail field arrive at the *same call site* as every other field, and that is
  what keeps the safety line to **one line**: a spelling with a separate
  tail-append needs the guard twice, and then R1-vs-R1h stops being a one-line
  difference.
- **The cursor guards are subtraction-first** (`len - p < 4`, `len - p < llen`)
  in all seven rungs. `p <= len` is maintained by the guards themselves, so the
  subtraction cannot wrap; the additive `p + 4 > len` overflows `usize` and Verus
  rejects it. p07's lesson on a third pattern, and it is what keeps the kernel's
  `requires` at **one** clause.
- **The field length is bound to a local, `flen = i - s`, in all seven rungs.**
  This is not style: R5's store is a *call* (`tl_set_unchecked(&mut tl, nt,
  flen)`) and R4's is an assignment, so an expression argument is evaluated in a
  different order in the two and `-O0` `identity` drops to `differ`. Measured —
  `NOTES.md` 6a — and it is p06's TASK_048 wrinkle arriving one pattern later.
- **The SPELLING OF THE FOLD LOOP is deliberately NOT pinned**, only the
  operations: R1, R1h, R2, R4 and R5 write an indexed `while`, R3 writes
  `tl[..nt].iter()` and `scr[cur..cur+tj].iter().fold(...)`.
- Wrapping arithmetic throughout.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == split_fold(buf, off, len)
```

`split_fold` is the spec function; `model.py` is its independent Python twin —
and independent in a way that matters here: `model.py`'s *simulation* finds the
partition with `bytes.split(b",")`, the library's own splitter, while the helper
`split_fold` walks a cursor exactly as `verus.rs`'s `toks` does. The two agree on
every input, so the partition is checked two ways.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included, and `harness/check.py` evaluates it at every one of the
kernel calls to prove that it does. `nline`, `llen`, all 2^32 values of each, and
every byte of the window including every delimiter in it are *arguments* of the
problem; the kernel is total in all of them.

**It is ONE clause**, as on p03, p06, p11 and p12 and unlike p17 — and keeping it
at one cost a spelling choice (subtraction-first guards) rather than a
precondition.

### What the `ensures` is, and what it is not

**It is the FUNCTIONAL postcondition, and that is the whole point.** It says the
accumulator is the fold of the field table the line's delimiters determine —
count, then each field's length and its bytes, in order — not merely that nothing
was accessed out of bounds. A memory-safety-only spec accepts a kernel that
records the wrong lengths, or the right lengths in the wrong order, or that
truncates at a different `MAXTOK`; this one rejects all three. `NOTES.md` 10 is
where the mutants are.

**And there is a second thing the `ensures` deliberately does not say: that
`nline` is honest, that `llen` fits, or that a line holds at most `MAXTOK`
fields.** `adversarial-run17`, `-alt33`, `-full65`, `-many` and `degenerate` are
all inside the verified domain and every checked rung agrees with `model.py` on
all five. Writing the stronger precondition would have been an assumption about
the contents of a file that no honest loader can discharge
(`.memory/02-bench-rules.md`), and it would have deleted every row the pattern
exists for.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p14's payload is p06's, p11's, p03's, p12's, p16's,
p17's, p05's and p07's:

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes`, reused verbatim, with **nothing added to `common/` for
p14**.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here.

## Driver loop

Identical in all seven rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers, and byte-for-byte p06's and p12's. `harness/check.py` normalises every
copy — the C one included — and diffs it against `driver.canonical` below.

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

`stride_w >= 4` because p14's window header is the 4-byte `nline` field.
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
| `verus.obligations` = 19 | **`SCR` 1 + `MAXTOK` 1 + `DELIM` 1 + `toks` 1 + `fold_bytes` 1 + `fold_toks` 1 + `walk` 1 + `lemma_scan_exit` 1 + `scr_load` 1 + `kernel` 5 + `main` 5 = 19.** Every term was measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, and so were the zero terms. `kernel`'s 5 is 1 body + 1 per loop body (**four** loops: the line walk, the scan, the fold over fields and the fold over a field's bytes). **Three `const`s carry one query each**, which is the first pattern here with more than one — `.memory/04-verus.md` records the rule and p03/p06/p08 each had a single `SCR`-shaped constant. |
| `verus.twin_obligations` = 23 | the count under `--cfg slb_twin`. **19 shipped + 4**, one per trusted accessor twin, and it is +4 rather than +5 because `scr_load` is **not** a trusted item and needs no twin. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`, and since TASK_010 that does not make Miri optional: it is mandatory for any pattern with a trusted item. On p14 the argument is the usual one plus one specific to this kernel — the trusted **write** accessor is called once per field and its `requires` is the only thing between the proof and R1's bug. |


```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == split_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (split_fold). p14's bindings are the READ-ONLY set p03, p06, p11, p12, p16, p17, p05 and p07 use and NOT p02's before/after set, and the reason is worth stating because p14 is a WRITE pattern: both destinations, the scratch `scr[SCR]` and the field table `tl[MAXTOK]`, are fixed-size LOCALS inside the kernel, so no buffer crosses the signature and there is nothing for an `after` binding to name. That is p03's, p06's and p12's shape. The security property is therefore carried by the trusted accessors' discharged `requires` -- and on p14 that includes a WRITE accessor, `tl_set_unchecked`'s `i < old(v)@.len()`, called once per field, which is what excludes the store R1 performs past `tl[MAXTOK]`. **The `ensures` is the FUNCTIONAL one and that is the whole point of the pattern**: it says the accumulator is the fold of the field table the line's DELIMITERS determine -- the count, then each field's LENGTH and its CONTENT, in order -- through `toks`, `ntok`, `fold_toks` and `fold_bytes`. A memory-safety-only spec accepts a kernel that records the wrong lengths, or the right lengths in the wrong order, or that truncates at a different MAXTOK; this one rejects all three (../NOTES.md 10). **What the `ensures` deliberately does NOT say is that `nline` is honest, that `llen` fits the window, or that a line holds at most MAXTOK fields.** `walk` specifies what the PROGRAM does -- stop when the window runs out, clamp the copy, split, truncate at MAXTOK, fold -- so adversarial-run17.bin, adversarial-alt33.bin, adversarial-full65.bin, adversarial-many.bin and degenerate.bin are all INSIDE the verified domain and every checked rung agrees with model.py on all five. A `requires` that a line held at most MAXTOK fields would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete every row the pattern exists for.",
  "idiom": {
    "required": [
      {
        "c": "THE SAFETY LINE, and the only line c/kernel.c omits: `if (nt == MAXTOK)` in c/kernel_hardened.c. c/kernel.c omits exactly this and nothing else, so the scoped-absent audit pair this entry reports is on that rung and is correct.",
        "rust": "THE SAFETY LINE: `if nt == MAXTOK {` in all four Rust rungs. In Rust it is a SEMANTIC line and not a safety line -- rustc's bounds check on `tl[nt]` is what makes the safe rungs safe -- so no Rust-vs-Rust comparison moves on it; see the why key."
      },
      {
        "c": "...and the break that makes it a TRUNCATION rather than a skip, which is the answer the contract pins: `break;` in c/kernel_hardened.c.",
        "rust": "...and the break that makes it a TRUNCATION rather than a skip, which is the answer the contract pins: `break;` in all four Rust rungs."
      },
      {
        "c": "THE CLAMP, present in EVERY rung including R1, so the COPY and the SCAN are bounded in every rung and the bug is the field count alone: `m = llen < SCR ? llen : SCR;` in both C rungs.",
        "rust": "THE CLAMP, present in EVERY rung, so the COPY and the SCAN are bounded in every rung and the bug is the field count alone: `let m: usize = if llen < SCR { llen } else { SCR };` in all four Rust rungs."
      },
      {
        "c": "the scratch is a FIXED-SIZE LOCAL of SCR bytes, never an allocation and never a length from the file: `uint8_t scr[SCR];` in both C rungs.",
        "rust": "the scratch is a FIXED-SIZE LOCAL of SCR bytes, never an allocation and never a length from the file: `let mut scr: [u8; SCR] = [0; SCR];` in all four Rust rungs."
      },
      {
        "c": "THE FIELD TABLE is a FIXED-SIZE LOCAL of MAXTOK entries -- it is the destination the bug overflows and its extent is a compile-time constant, so R1's overrun is a property of the PROGRAM and not of an allocation the input chose: `size_t tl[MAXTOK];` in both C rungs.",
        "rust": "THE FIELD TABLE is a FIXED-SIZE LOCAL of MAXTOK entries -- it is the destination the bug overflows and its extent is a compile-time constant: `let mut tl: [usize; MAXTOK] = [0; MAXTOK];` in all four Rust rungs."
      },
      {
        "c": "...and both are ZERO-INITIALISED ON EVERY CALL, so a rung's answer cannot depend on what the frame happened to hold: `memset(scr, 0, sizeof scr);` in both C rungs.",
        "rust": "...and both are ZERO-INITIALISED ON EVERY CALL, so a rung's answer cannot depend on what the frame happened to hold: `[0; SCR];` in all four Rust rungs."
      },
      {
        "c": "the load into the scratch is a BULK copy in every rung, so the measured difference is the SPLIT and not the load: `memcpy(scr, buf + off + p, m);` in both C rungs.",
        "rust": "the load into the scratch is a BULK copy in every rung, so the measured difference is the SPLIT and not the load: `.copy_from_slice(&src[from..from + n]);` in all four Rust rungs -- same call, same operands, same order, in the body of scr_load. THE RECEIVER IS SCOPED 2-AND-2, p06's TASK_048 scoping inherited: `dst[..n]` is the receiver in safe_naive.rs and safe_tuned.rs, and `s.split_at_mut(n)` is the receiver in unsafe.rs and verus.rs, because `..n` is a RangeTo<usize> and RangeTo has NO SliceIndexSpecImpl at the pinned vstd, so dst[..n] cannot be VERIFIED at all and R4 follows R5 because the identity pin makes them one program. The price is measured in ../NOTES.md 6a."
      },
      {
        "c": "THE VIRTUAL DELIMITER: the scan treats the end of the line as a separator, which is what makes the TAIL field arrive at the SAME call site as every other field and therefore what keeps the safety line to ONE line: `if (i == m || scr[i] == DELIM)` in both C rungs.",
        "rust": "THE VIRTUAL DELIMITER: the scan treats the end of the line as a separator, which is what makes the TAIL field arrive at the SAME call site as every other field and therefore what keeps the safety line to ONE line: `if i == m ||` in all four Rust rungs."
      },
      {
        "c": "the scan IS BOUNDED by the live extent in EVERY rung, R1 included -- p14 is NOT p11, and this entry is what says so by grep: `while (i <= m)` in both C rungs.",
        "rust": "the scan IS BOUNDED by the live extent in EVERY rung, R1 included -- p14 is NOT p11, and this entry is what says so by grep: `while i <= m {` in all four Rust rungs."
      },
      {
        "c": "the field length is bound to a LOCAL before the store, which is what keeps -O0 identity at norel (see the why key): `flen = i - s;` in both C rungs.",
        "rust": "the field length is bound to a LOCAL before the store, which is what keeps -O0 identity at norel (see the why key): `let flen: usize = i - s;` in all four Rust rungs."
      },
      {
        "c": "the fold folds each field's LENGTH, in order, spelled with the literal multiplier: `acc = acc * 31 + (uint64_t)tj;` in both C rungs.",
        "rust": "the fold folds each field's LENGTH, in order: `.wrapping_add(tj as u64)` in all four Rust rungs."
      },
      {
        "c": "...and each field's CONTENT, in order, over the full recorded extent: `acc = acc * 31 + (uint64_t)scr[cur + q];` in both C rungs.",
        "rust": "...and each field's CONTENT, in order, over the full recorded extent, spelled with the literal multiplier: `.wrapping_mul(31)` in all four Rust rungs. safe_tuned.rs spells the LOOP as .iter().fold() over a reslice, which is why only the operation and not the loop form is pinned here."
      },
      "...and the cursor STEPS OVER THE DELIMITER between fields, which is what makes the recorded lengths a PARTITION of the line rather than a set of overlapping ranges: `cur = cur + tj + 1;` in all seven rungs.",
      {
        "c": "the FIELD COUNT is folded, so a rung that truncated at a different MAXTOK -- or not at all -- cannot produce the same checksum: `acc = acc * 31 + (uint64_t)nt;` in both C rungs.",
        "rust": "the FIELD COUNT is folded, so a rung that truncated at a different MAXTOK -- or not at all -- cannot produce the same checksum: `.wrapping_add(nt as u64)` in all four Rust rungs."
      },
      {
        "c": "the declared line count is folded, so a rung that walked a different number of lines cannot produce the same checksum either: `* 31 + (uint64_t)nline` in both C rungs.",
        "rust": "the declared line count is folded, so a rung that walked a different number of lines cannot produce the same checksum either: `.wrapping_add(nline as u64)` in all four Rust rungs."
      },
      {
        "c": "the cursor guards are SUBTRACTION-FIRST, which is what keeps the kernel's requires at ONE clause -- p <= len is maintained by the guards themselves so the subtraction cannot wrap, while the additive form p + 4 > len overflows usize and Verus rejects it: `if (len - p < 4)` in both C rungs.",
        "rust": "the cursor guards are SUBTRACTION-FIRST, which is what keeps the kernel's requires at ONE clause -- p <= len is maintained by the guards themselves so the subtraction cannot wrap, while the additive form p + 4 > len overflows usize and Verus rejects it: `if len - p < 4 {` in all four Rust rungs."
      },
      "...and the second guard, which bounds the line's declared length by what the window holds: `len - p < llen` in all seven rungs.",
      "the little-endian u32 decode is written out with + and * rather than | and <<, so it stays linear arithmetic: `+ 65536 *` in all seven rungs.",
      "...and its top byte: `+ 16777216 *` in all seven rungs."
    ],
    "forbidden": [
      "`.split(`",
      "`.split_terminator(`",
      "`.splitn(`",
      "`strtok(`",
      "`strsep(`",
      "`memchr(`",
      "`from_le_bytes`",
      "`chunks_exact`"
    ],
    "why": "each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). THE ONLY THING R1 OMITS IS THE FIELD-COUNT BOUND: the clamp `m = min(llen, SCR)` is present in every rung, so the COPY is bounded in every rung; the scan bound `i <= m` is present in every rung, so every read of `scr` is in bounds in every rung; both cursor guards are present in every rung, so `p` never leaves the window in any rung. R1-vs-R1h is therefore the cost of `if (nt == MAXTOK) break;` and nothing else. THE BOUND IS A COUNT OF A BYTE VALUE AND THAT IS WHY THIS PATTERN EXISTS: `nt` is one more than the number of DELIM bytes in `scr[0..m)`, which nothing in the wire format declares and no length bounds -- a 64-byte line holds between 1 and 65 fields against a 16-entry table -- so the guard cannot be hoisted out of the scan, folded into a length check or derived from the header, which is what every earlier pattern's guard could be. THE VIRTUAL DELIMITER `i == m` IS PART OF THE PINNED CONTRACT AND NOT A MATTER OF TASTE: it is what makes the TAIL field arrive at the same call site as every other field, and therefore what keeps the safety line to ONE line. A spelling that appends the tail separately needs the guard TWICE, and then R1-vs-R1h stops being a one-line difference and the pattern stops measuring what it says it measures. It is also what makes a TRAILING delimiter produce a trailing EMPTY field, which `degenerate.bin` exercises and which a `while i < m` scan silently drops. TRUNCATION AT MAXTOK IS THE SPECIFIED ANSWER, not an evasion: `ntok()` in verus.rs is `min(len(toks), MAXTOK)` and model.py takes `split(...)[:MAXTOK]`, so the checked rungs cannot disagree about it. It is what strtok, getopt, argv splitters and every fixed-table CSV reader do, and it is p13's shape one level up -- the hardened cell is memory-safe and LOSES DATA. `.split(`, `.split_terminator(` and `.splitn(` are forbidden because each is a single library call that deletes the SCAN this pattern measures: the per-field and per-byte decomposition, the sweep bands over `llen` and over the field count, and the whole amortisation result are statements about an explicit cursor scan, and a rung using one of them would measure `core::slice::Split`'s codegen instead, which is p11's comparison wearing p14's label. AND THE PROVER ALREADY EXCLUDES THEM FROM R4: the pinned vstd has no `assume_specification` for `<[T]>::split` at all (`vstd/std_specs/slice.rs` specifies `split_at`, `split_at_mut` and `split_at_checked` and nothing else), so an R4 using it could not have a verifying R5 twin and would not be a rung -- the `identity`-pin trap this block's own `identity` key sets, and p11's R4-by-permission result on a third pattern. That exclusion therefore costs NOTHING to keep, and ../NOTES.md 8 publishes the measurement rather than the assertion. `strtok(`, `strsep(` and `memchr(` are forbidden for the C rungs, and these ARE fiats with published prices rather than exclusions the prover makes -- C has no prover. `strtok` is forbidden because it COLLAPSES runs of delimiters, so a rung using it computes a DIFFERENT PARTITION of the same bytes; that difference is p14's headline and it belongs in an adversarial row and a priced control, not in a rung, because a rung that collapsed would disagree with model.py on `adversarial-run17` for a reason that is not the bug. `strsep` computes the same partition this kernel does but MUTATES ITS INPUT, which the driver's repeat protocol forbids (../NOTES.md 0 measures it: the checksum stops being a function of the arguments). `memchr` moves the scan into a libc IFUNC and makes the kernel-exclusive column a library comparison, which is p11's and p13's result and not p14's. All three are built and priced in controls/gen_controls.py and ../NOTES.md 8. `from_le_bytes` deletes the written-out little-endian header decode every rung shares AND is NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW and again on p06), so a rung using it would compare a safe cell against an unsafe cell that cannot exist. `chunks_exact` is forbidden for the fold because p16 measured that the chunk width moves that pattern's per-byte rate over a 31% range (5.04688...6.62500, `.memory/01-ladder.md`), and p14's published decomposition is into a per-copied-byte, a per-scanned-byte, a per-field and a per-line term. EVERY EXCLUSION HERE IS WHOLE-PATTERN AND NOT SCOPED TO SOME RUNGS, which is deliberate: `.memory/01-ladder.md`'s direction test fired on p13 exactly because three of its entries named some rungs and exempted `safe_tuned.rs`, so R3 was permitted a spelling R4 was forbidden and 48%/17% of the published margin was the pin. A whole-pattern exclusion keeps the two sides of the comparison equal. THE ONE SCOPED THING IN `required` IS THE LOAD'S RECEIVER, 2-AND-2, and it is p06's TASK_048 scoping inherited verbatim with its price re-measured on this pattern (../NOTES.md 6a): `dst[..n]` in safe_naive.rs and safe_tuned.rs, `s.split_at_mut(n)` in unsafe.rs and verus.rs, because `..n` is a `RangeTo<usize>` and `RangeTo` has NO `SliceIndexSpecImpl` at the pinned vstd, so the `dst[..n]` receiver cannot be VERIFIED at all and R4 follows R5 because the `identity` pin makes them one program. WHAT IS DELIBERATELY *NOT* PINNED is the SPELLING OF THE FOLD LOOP: R1, R1h, R2, R4 and R5 write an indexed `while` and R3 writes `tl[..nt].iter()` with `scr[cur..cur+tj].iter().fold(...)`, and holding those fixed would hold fixed one of the two things p14 exists to compare. What IS pinned instead is the OPERATIONS -- the field LENGTH, the field CONTENT, the cursor stepping over the delimiter, and the field COUNT, in that order. THE FOLD IS OVER THE FULL RECORDED EXTENT AND ORDER-SENSITIVE, AND p14 SUPPLIES A THIRD, INDEPENDENT REASON FOR THAT RULE. TASK_004_REVIEW's reason is ELISION: a fold that reads only part of the result lets the optimiser delete the rest. p06's is INVARIANCE: three reverses compose to a PERMUTATION, so a sum- or xor-fold could not tell the buggy scratch from the correct one. p14's is PARTITION-BLINDNESS, one level up from p06's: TOKENISING DOES NOT MOVE ANY BYTE, so every partition of the same line yields the same bytes in the same order and a fold over the concatenated CONTENT alone is identical for every possible set of field boundaries. Folding the LENGTHS IN ORDER is what makes a boundary bug visible and folding the COUNT is what makes a truncation visible; ../NOTES.md 2 tabulates which mutation each of the three catches. THE LOAD IS THE SAME BULK SPELLING IN EVERY RUNG -- `memcpy` in C and `scr_load`, whose body is the one bulk call `.copy_from_slice(&src[from..from + n]);` with the same operands in the same order, in all four Rust rungs -- so the measured difference between rungs is the SPLIT and not the load, which is p02's retraction applied in advance. THE FIELD LENGTH IS BOUND TO A LOCAL `flen = i - s` IN ALL SEVEN RUNGS AND THAT IS NOT STYLE: R5's store is a CALL and R4's is an assignment, so an expression argument is evaluated in a different order in the two and `-O0` identity drops from `norel` to `differ`. It was measured that way first and the repair is this line (../NOTES.md 6a); it is p06's TASK_048 wrinkle arriving one pattern later, and the price at -O3 is ZERO because R4 and R5 are byte-identical there with and without it. WHEN THIS DECLARATION WAS WRITTEN, STATED EXACTLY BECAUSE p14 HAS A PRE-FLIGHT: it was written after the seven rungs, the R5 proof (19/0, twin 23/0), the `identity` pin and the checksums existed and BEFORE any p14 CELL had been measured for perf -- `harness/measure.py p14` had not been run and no `Ir` or `ns` figure for any of the eight cells existed. What DID exist is ../NOTES.md 0: `Ir`, sanitizer behaviour and checksums for a standalone SIX-KERNEL C PROBE with no driver and no pattern, which settled the bug class TASK_049 asked to be settled before five rungs were built on it. That probe is not a cell and none of its numbers is published as p14's, but it is not nothing either, and saying 'no number existed' would be false. What the probe DID influence is the CHOICE OF BUG CLASS and the wire format that expresses it; what it did not influence is any entry of `required` or `forbidden`, every one of which names a line the contract in ../spec.md's Semantics block already had. ONE ENTRY WAS HOWEVER ADDED IN RESPONSE TO A MEASUREMENT AND IT IS NAMED HERE RATHER THAN LEFT TO BE INFERRED, because a declaration that was quietly shaped by a measurement is the self-certification this whole mechanism exists to prevent: the `flen = i - s;` entry did NOT exist in the first draft, and it was added after `harness/check.py` reported `identity: unsafe vs verus O0 differ` (286 vs 289 static instructions) on a tree whose rungs wrote `tl[nt] = i - s;` directly. It is a CODEGEN measurement and not a PERF one -- no Ir or ns figure for any cell existed when it was added, and the -O3 bytes are identical with and without it (../NOTES.md 6a) -- but it is a measurement, and 'the declaration was written before anything was measured' would be false as a blanket sentence.. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither."
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
      "verus.rs": 19
    },
    "twin_obligations": {
      "verus.rs": 23
    },
    "obligations_note": "19 = SCR 1 + MAXTOK 1 + DELIM 1 + toks 1 + fold_bytes 1 + fold_toks 1 + walk 1 + lemma_scan_exit 1 + scr_load 1 + kernel 5 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained, and the zero terms are checkable the same way: u32_at, nline_at, zero_scr, load_into, ntok, line_fold and split_fold are NON-RECURSIVE spec fns and report 0, while toks, fold_bytes, fold_toks and walk are RECURSIVE and carry one termination query each; buf_get_unchecked, scr_get_unchecked, tl_get_unchecked, tl_set_unchecked, load_input and emit are external_body and report 0. **THREE `const`s carry one query each and p14 is the first pattern here with more than one** -- `.memory/04-verus.md` records that a `const` inside verus! is its own obligation (measured on p08's SCR and p03's STACK_CAP), and p14 declares SCR, MAXTOK and DELIM. kernel's 5 = body + FOUR loop bodies -- the line walk, the scan, the fold over fields and the fold over one field's bytes -- and there is no `by (nonlinear_arith)` sub-proof anywhere in the kernel because every multiplication in the decode is by a literal and the partition is stated with a cursor rather than with division. main's 5 is quoted AS MEASURED and does not decompose from the command line: body + driver loop + one per by-block would predict 6 and Verus reports 5, the identical off-by-one p03's, p05's, p06's, p07's, p11's, p12's and p17's spec.md record for the identical driver. `.memory/04-verus.md`'s one-query-per-function-plus-one-per-loop rule of thumb gives 14 here and is therefore not the derivation.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 19 shipped + 4, and each term is measured the same way: `--cfg slb_twin --verify-function slb_twin_<name> --verify-root` reports `1 verified` for slb_twin_buf_get_unchecked, slb_twin_scr_get_unchecked, slb_twin_tl_get_unchecked and slb_twin_tl_set_unchecked. It is +4 rather than +5 because **`scr_load` is NOT a trusted item on this pattern and never was** -- the pinned vstd specifies `<[T]>::copy_from_slice` (`vstd/std_specs/slice.rs:205`) AND `<[T]>::split_at_mut` with the write-back spelled out (`:185`) AND inserts `vstd::array::ref_mut_array_unsizing_coercion` (`vstd/array.rs:175`) for the array-to-slice reborrow, so nothing about the bulk load needs to be trusted at all. p06 reached that at TASK_048 by removing an item; p14 is the first pattern built with it from the start. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg.",
    "unsafe_justifications": {
      "verus.rs": {
        "tl_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `usize` is a legal thing to store in a `usize` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [usize; 16]` reads `i < 16`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second, p06 the third and p14 the fourth, and on p14 the item is the one the whole pattern is about -- it is called once per field and its `requires` is what excludes R1's out-of-bounds store. A second conjunct `old(v)@.len() == 16` is deliberately NOT written: for a `&mut [usize; 16]` it is a TAUTOLOGY discharged from the parameter type alone by vstd's `array_len_matches_n`, and p03's gate run refused exactly that draft (p03 NOTES.md 5b)."
      }
    },
    "items": {
      "verus.rs": {
        "u32_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "nline_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "zero_scr": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "load_into": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "toks": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "ntok": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold_bytes": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold_toks": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "line_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "walk": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "split_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "lemma_scan_exit": {
          "external": null,
          "requires": [
            "toks(scr, m, 0, 0) == tkg + toks(scr, m, i, s)",
            "i > m || tkg.len() == MAXTOK as int",
            "tkg.len() <= MAXTOK as int"
          ],
          "ensures": [
            "tkg.len() == ntok(scr, m)",
            "toks(scr, m, 0, 0).take(ntok(scr, m)) == tkg"
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
        "tl_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_tl_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "tl_set_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_tl_set_unchecked": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "scr_load": {
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
            "r == split_fold(buf@, off as int, len as int)"
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
    "note": "work_per_call is **bytes of the window** -- `stride`, 207 on small and 104 on large -- which is p16's, p05's, p11's, p12's and p06's denomination. WHICH WAY THE ESTIMATE ERRS: STRICT, by three corrections. It OVER-counts by the 4 window-header bytes and by the 4 bytes of each line header (decoded as u32s, never copied, scanned or folded) and, on a line with `llen > SCR` or more than MAXTOK fields, by the part the kernel skips. It UNDER-counts by the whole of the second and third passes: every copied byte is copied, SCANNED and FOLDED, i.e. visited three times, and the scan runs m+1 times per line rather than m. On small the visits are 179 copied + 185 scanned + 179 folded = 543 against a declared 207, and on large 52 + 64 + 52 = 168 against 104, so `stride` is well below the number of byte-visits on both and the derived floor is one the kernel must clear. work_unit_bits is 8, one window byte, so the effective absolute bound under min_ir_per_work is 0.001953125 x 8 = 0.015625. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged, and the argument is p14-specific: the fold is a serial Horner chain `acc = acc*31 + b`, so byte i+1's multiply depends on byte i's and there is no vector form at any -march, and the scan is a scalar byte loop with TWO exit tests (`i <= m` and the delimiter compare) in every rung and both compilers -- measured on the disassembly (../NOTES.md 1). The COPY alone can go far below 0.25 -- it is a `memcpy` in every rung -- which is exactly why the unit is denominated over the whole window and not over the copy. The two probe inputs differ in work_per_call (207 vs 104) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost, on the first kernel in this project whose postcondition is a PARTITION -- a `Seq<int>` of field lengths built by a recursive spec function, not a closed form. The byte-identity result now covers a kernel with four loops, one of which fills a fixed metadata table through a trusted setter and two of which are nested folds over that table. The pin has a MEASURED PRICE here and it is in the idiom why: binding the field length to a local `flen = i - s` before the store, because R5's store is a CALL and R4's is an assignment, so the argument evaluation order differs at -O0. Without it -O0 identity is `differ` (286 vs 289 static instructions, measured); with it the -O0 kernels are byte-identical once pc-relative fields are masked and the -O3 kernels are byte-identical outright. At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."
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
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. On p14 the specific reason is `tl_set_unchecked`: it WRITES, it is called once per field, and a trusted body that also wrote `i + 1` would satisfy this `ensures` on slot `i` and be invisible to Verus, to the twin, to the contract pin and to stages 5c/5c-req -- the p08 `copy_nonoverlapping` substitution passed all of those and was caught by the O3 identity pin and Miri alone. Cost: check.py rewrites n_iters to 4, so each row copies, scans and folds at most 4 x 3 x stride bytes -- about 2500 on small and 1300 on large, four orders of magnitude inside `.memory`'s measured 3.05 M budget. The only real cost is the 5.2 MB payload to_vec, and p07's 12 MB one passes.",
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

There is no exit 7 here, for p03's, p06's, p11's, p12's, p16's, p17's, p05's and
p07's reason: p14's payload names no allocation size, and both the scratch and
the field table are fixed-size locals in every rung, so p02's `SLB_MAX_CAP` check
would be dead code.

**These are the CHECKED rungs' exit codes.** R1's behaviour is a function of the
overflow magnitude and of the compiler, measured at the gate's own flags — see
`NOTES.md` 7 for the table and `results/gate/p14-field-split.json` for the
record.

## Degenerate shapes

`stride_w >= 4 && stride_w <= n_blob` is the driver's whole input validation. A
stride below 4 cannot hold the header (`adversarial-stride3.bin`); a stride above
`n_blob` leaves no whole window, so `nwin` would be 0 and `k` would have nothing
to index. Either way the loop is skipped and the driver prints `0` after **zero**
kernel calls.

`degenerate.bin` is one window carrying the six shapes the contract has to
decide, and **every rung including R1 agrees on it**, which is why it is not
named `adversarial-*` and the gate holds all eight cells to `model.py` on it:

| line | what it is |
|---|---|
| `llen = 0` | `m == 0`. The scan's `i == m` disjunct fires at `i == 0`, so the line yields **one field of length zero**. A kernel that yielded *zero* fields here would disagree with `bytes.split`, with Rust's `split` and with `strsep`. |
| `llen = 1`, no delimiter | one field, and the tail-append path with nothing before it. |
| leading delimiter | field 0 is empty and `cur` steps over a delimiter at offset 0. |
| trailing delimiter | the **last** field is empty — the case a `while i < m` scan silently drops, and the reason the scan is `i <= m`. |
| 15 delimiters | exactly `MAXTOK` fields: **the boundary from the safe side.** R1 fills the table exactly and stores nothing past it, so the two C cells agree here and diverge at 16. p12's `adversarial-exact` analogue. |
| `llen = 100 > SCR` | the clamp bounds the copy and the scan in every rung, so the 36 undeclared bytes are skipped by the cursor and never read. The clamp is not the safety line. |

The kernel's `len < 4` guard is, given the driver's `stride_w >= 4`, unreachable
in this benchmark. It is kept anyway so the kernel is **total** and its
`requires` stays purely structural; the alternative — a `len >= 4` precondition —
would be a precondition about the driver's own guard rather than about the
buffer.
