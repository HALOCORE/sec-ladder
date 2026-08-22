# p12 — `strcat` into a fixed buffer: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, and C spells the pair
out. C is handed the blob length and *both* C rungs ignore it — which is p12's
contrast with p02, p16 and p17, where the check the C rung skips is against a
length it was handed. **Here the number the programmer needed was `sizeof dst`,
three lines up in the same function.**

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     nstr      u32 LE    DECLARED string count    ATTACKER DATA
byte 4..      packed, NUL-terminated strings
data_start = 4
DST_CAP = 128                     the destination's capacity, a compile-time
                                  constant in every rung
```

**Termination and fit are properties of the file, not of the kernel.** No rung
checks that `nstr` is honest, no rung checks that a terminator is present, and
— the part that matters — *the specification does not assume that the strings
fit*. See "What the `ensures` is, and what it is not".

## Semantics

```
if len < 4:                                   return 0
nstr from the header
if nstr == 0:                                 return 0     # present in EVERY rung

dst = [0; DST_CAP] ;  dlen = 0 ;  acc = 0 ;  p = 4         # dst is a LOCAL
for s in 0 .. nstr:
    q = p
    while q < len and buf[off + q] != 0:      q += 1       # bounded in EVERY rung
    slen = q - p
    # >>> THE CAPACITY CHECK. R1 omits this line and nothing else. <<<
    if dlen + slen <= DST_CAP:
        for i in p .. q:  dst[dlen] = buf[off + i] ; dlen += 1
    acc = acc *64 31 +64 slen
    if q >= len:   break                       # no terminator: last string
    p = q + 1
    if p >= len:   break
for i in 0 .. dlen:                            # fold the destination
    acc = acc *64 31 +64 dst[i]
return (acc *64 31 +64 dlen) *64 31 +64 nstr
```

`*64`/`+64` are wrapping, as in every earlier pattern, so the kernel has **no
precondition on values** and every measured input is inside the verified domain
by construction. C's unsigned types wrap by definition (6.2.5p9) and the Rust
rungs write `wrapping_add`/`wrapping_mul`.

### The bug is a WRITE, and that changes what an input can be

Every other bug this project models is a read. p11's scan runs off the end
looking for a sentinel; p03's pop reads eight bytes below its array; p17's index
goes negative; p16 walks past a length whose subtraction wrapped; p02's write is
a bulk `memcpy` into a **caller-supplied** buffer whose length came from the
file. p12 is the textbook case that was missing: an unbounded append into a
**fixed local**, in the same frame as the return address.

Two consequences, and both are structural rather than choices:

- **The failure mode is a function of the overflow MAGNITUDE**, not of the
  input's position in the blob. `NOTES.md` 0 has the ladder measured at the
  gate's own flags; the short form is that **≤ +8 bytes past is silent under
  both compilers**, **+9 … +56** aborts under gcc's canary and silently corrupts
  the caller's frame under clang, and **+57** and up destroys the return
  address. (Boundaries re-scanned at step 1 at TASK_041; the first published
  ladder sampled a coarse grid and put them one step off.) `inputs/gen.py`
  builds one adversarial row per regime.
- **`small` and `large` must be 100% accept, and that is not negotiable.**
  `harness/check.py`'s `check_checksums` requires every cell, R1 included, to
  print `model.py`'s checksum on every non-adversarial **matrix** input
  (`sweep-*` is dropped before it, in **`inputs_of`** at `check.py:495`). R1 omits the capacity
  check, so on any window where the check fires R1 copies bytes the checked
  rungs skip *and* ends with a larger `dlen` — and **p12's fold takes both**, so
  no such row can also be a checksum-agreeing one **here**. ⚠ That is a property
  of this fold and not of the bug being a write: TASK_040_REVIEW built a
  fixed-extent fold on which the checked and unchecked cells agree while the
  unchecked one still executes an out-of-bounds store, at the price of the perf
  row executing UB on every call (`NOTES.md` 1a). p11 has
  `adversarial-zerotail`, a header lie on which every rung including R1 agrees;
  **p12 has no such row, and the reason is the fold.** The consequence is stated
  rather than hidden:
  the two perf rows exercise the check on the **accept path only** and are
  therefore **rank-deficient for "per what?"** — with everything accepted, *per
  string* and *per accepted string* are the same regressor. `sweep-a*` is the
  band that separates them, and R1 is absent from it for the same reason.

### The scan is bounded by the window in every rung, and that is deliberate

R1 keeps the window bound on the scan (`memchr(..., len - p)`), both outer
bounds (`if (q >= len) break;`, `if (p >= len) break;`) and every source index.
p11 already measured the unbounded scan; importing it here would put **two** bugs
in one kernel and no adversarial row could attribute a behaviour to either.

`adversarial-nonul.bin` is p11's malformed record arriving through p12's bug: the
scan stops correctly at the window end, the measured length is `len - p`, and it
is the **copy** that overruns.

### The scan, the copy and the destination fold are three loops

Fusing any pair deletes the pattern. If the copy were fused into the scan,
`slen` would never exist as a value and the capacity check could not be written
at all — the check is *about* a length that has to be known before the first
byte moves, which is precisely what `strcat` gets wrong. If the destination fold
were fused into the copy, `dst` would never be read back and nothing in the
checksum would depend on what was written.

**That the split survives `-O3` is measured and not assumed** (NOTES.md 1),
including which of the three loops each compiler turns back into a library call.

### Load-bearing, do not "improve"

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug. Edit both or neither.

- **The destination is a fixed-size local of `DST_CAP` bytes in all seven
  rungs**, never an allocation and never a length from the file. That is what
  makes the bug a *stack* overflow and it is why p02's `SLB_MAX_CAP`/exit 7 has
  no analogue here.
- **A string that does not fit is SKIPPED, not truncated.** `dlen` is folded, so
  a truncating rung produces a different checksum and cannot be mistaken for
  this one. (A truncating rung is a different pattern — that is p13.)
- **The rejected string's LENGTH is still folded**, so the checksum records that
  the string was seen while recording none of its bytes. This is what makes
  `adversarial-off1` a one-byte difference in the destination rather than a
  whole-window one.
- **The check is `dlen + slen <= DST_CAP` in `size_t`/`usize`.** The same test in
  a narrower type wraps: `unsigned char sum = dlen + slen; if (sum <= DST_CAP)`
  accepts a 256-byte string outright, so the check is present, looks right, and
  waves the attack through. That variant is built and measured as a **control**
  (`controls/gen_controls.py`, NOTES.md 8) rather than shipped, because it is a
  third C rung and not this one.
- **The Rust rungs spell the check `slen <= DST_CAP && dlen + slen <= DST_CAP`
  and the C rungs do not**, and the difference is a measurement rather than an
  inconsistency. Without the left conjunct Verus rejects the additive sum with
  `possible arithmetic underflow/overflow` — nothing at the pinned vstd bounds
  `slen` below `usize::MAX` — and R4 must have a byte-identical R5 twin. So all
  four Rust rungs carry it (which keeps R2-vs-R4 matched) and R1h does not
  (which keeps the C column from being charged for a Verus concession). It costs
  **+2 static instructions and, measured as a marginal, 3.00 Ir per string
  WALKED** (`3.00·K − 1.00`, exact at five `K`; NOTES.md 5 — p12 first published
  the static delta as if it were the per-string rate). NOTES.md 5 prices the two
  alternatives on the same scale: p17's second `requires` plus a third driver
  conjunct is **0**, and the subtraction-first respelling
  `slen <= DST_CAP - dlen` is **+4 static and 4.00 Ir per string walked**.
- **The copy is a byte loop in R1, R1h and R2**, for p02's reason: one operator
  flips `bulk_calls` and 100% of the delta. R3 spells it `copy_from_slice` and
  R4/R5 an unchecked indexed store, deliberately — **that is the measurement**,
  and it is reported as a spelling difference with the routine named, not as a
  safety one (p11's rule).
- **The scan is held FIXED across R2, R3, R4 and R5** — the same indexed byte
  loop — because p11 exists to vary it. p12 varies the copy.
- Wrapping arithmetic throughout.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == strcat_fold(buf, off, len)
```

`strcat_fold` is the spec function; `model.py` is its independent Python twin.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included, and `harness/check.py` evaluates it at every one of the
kernel calls to prove that it does. `nstr`, all 2^32 values of it, and every byte
of the window are *arguments* of the problem; the kernel is total in all of them.

**It is ONE clause**, as on p03 and p11 and unlike p17 — and keeping it at one
cost two program lines rather than a precondition, both of them priced in
NOTES.md 5 rather than described as free.

### What the `ensures` is, and what it is not

p12 is a **write** pattern with a **local** destination, which is a combination
no earlier pattern has. p02 writes into a caller-supplied `&mut [u8]`, so its
security property is an equality on the destination *after* the call, stated in
the `ensures`. p12 has no such buffer in its signature: `dst` is born and dies
inside the kernel. So p12's shape is **p03's**, and the security property is
carried by the trusted accessors' discharged `requires` — one of which,
`dst_set_unchecked`'s `i < old(v)@.len()`, is a **write** precondition. That is
exactly what excludes the store past `dst[DST_CAP]` that R1 performs.

The `ensures` is what keeps the proof non-vacuous and pins **which bytes ended up
in the destination**: `walk` threads `dst` as a `Seq<u8>` and `copy_into` is the
byte-at-a-time append, so a rung that copied a string it should have skipped, or
truncated one it should have rejected, cannot satisfy it.

**And there is a second thing the `ensures` deliberately does not say: that
`nstr` is honest, that the strings are terminated, or that they fit.**
`adversarial-off1.bin`, `adversarial-nonul.bin` and `adversarial-overflow.bin`
are all inside the verified domain and every checked rung agrees with `model.py`
on all three. Writing the stronger postcondition would have forced a `requires`
about the contents of a file that no honest loader can discharge
(`.memory/02-bench-rules.md`), and it would have deleted the three rows the
pattern exists for.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p12's payload is p11's, p03's, p16's, p17's, p05's
and p07's:

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes`, reused verbatim, with **nothing added to `common/` for
p12**. All three are a bulk copy rather than an element-by-element decode, which
is what keeps every p12 row Miri-checkable.

Nothing is a compile-time constant except `DST_CAP`, which is the *destination's*
capacity and is a property of the program rather than of the input: `n_iters`,
`stride`, `n_blob`, every `nstr`, every string length and every byte come from
the file.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here and are
deliberately not copied across.

## Driver loop

Identical in all seven rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers, and byte-for-byte p11's. `harness/check.py` normalises every copy — the
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

`stride_w >= 4` because p12's window header is the 4-byte `nstr` field.
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
driver's Lemire index has an absorbing state at `acc == 0`. p11 argued this from
the shape of the return value; `inputs/gen.py` **checks** it, by running a
twenty-line copy of the checked kernel over every window of every multi-window
blob it emits.

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
| `verus.obligations` = 15 | **`DST_CAP` 1 + `scan_end` 1 + `copy_into` 1 + `fold_dst` 1 + `walk` 1 + `kernel` 5 + `main` 5 = 15.** Every term was measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, and so were the zero terms. `kernel`'s 5 is 1 body + 1 per loop body (**four** loops: the string walk, the scan, the copy and the destination fold), which is p12's contrast with p11's 4, p07's 3 and p03's 2. `DST_CAP`'s 1 is the `const`-inside-`verus!` query `.memory/04-verus.md` records; p12 is the third pattern to have one. **`main`'s 5 is quoted as measured** — the by-block rule of thumb predicts 6 — the identical off-by-one p03, p05, p07, p11 and p17 record for the identical driver. |
| `verus.twin_obligations` = 18 | the count under `--cfg slb_twin`. **15 shipped + 3**, one per twin, each measured at `1 verified`. p12 is the first pattern with **three** twins, and `slb_twin_dst_set_unchecked` is the first write twin outside p03. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`, and since TASK_010 that does not make Miri optional: it is mandatory for any pattern with a trusted item. On p12 the argument is stronger than usual, because one of the three accessors **writes** — see the `miri.reason` key. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == strcat_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (strcat_fold). p12's bindings are the READ-ONLY set p03, p11, p16, p17, p05 and p07 use and NOT p02's before/after set, and the reason is worth stating because p12 is a WRITE pattern: the destination is a fixed-size LOCAL inside the kernel, so no buffer crosses the signature and there is nothing for a `dst_after` binding to name. That is p03's shape exactly. The security property is therefore carried by the trusted accessors' discharged `requires` -- and on p12 that includes a WRITE accessor, `dst_set_unchecked`'s `i < old(v)@.len()`, which is what excludes the store past `dst[DST_CAP]` that R1 performs. The `ensures` is what keeps the proof non-vacuous and pins WHICH bytes ended up in the destination: `walk` threads the destination as a `Seq<u8>` and `copy_into` is the byte-at-a-time append, so a rung that copied a string it should have skipped, or truncated one it should have rejected, cannot satisfy it. **What the `ensures` deliberately does NOT say is that `nstr` is honest, that the strings are terminated, or that they FIT.** `walk` specifies what the PROGRAM does -- skip a string that would overflow, stop at the first zero byte or at the window end -- so adversarial-off1.bin, adversarial-nonul.bin and adversarial-overflow.bin are all INSIDE the verified domain and every checked rung agrees with model.py on all three. A `requires` that the strings fit would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete the three rows the pattern exists for.",
  "idiom": {
    "required": [
      {
        "c": "the SCAN is bounded by the WINDOW in every rung, R1 included -- p12's bug is the write and not the scan: `memchr(buf + off + p, 0, len - p)` in both C rungs.",
        "rust": "the SCAN is bounded by the WINDOW in every rung, R1 included -- p12's bug is the write and not the scan: `while q < len` in all four Rust rungs."
      },
      {
        "c": "THE CAPACITY CHECK, and the only line c/kernel.c omits: `if (dlen + slen <= DST_CAP) {` in c/kernel_hardened.c. c/kernel.c omits exactly this line and nothing else, so the scoped-absent audit pair this entry reports is on that rung and is correct.",
        "rust": "THE CAPACITY CHECK: `if slen <= DST_CAP && dlen + slen <= DST_CAP {` in all four Rust rungs. The left conjunct is the PROVER's and not the programmer's -- without it the additive sum is 'possible arithmetic underflow/overflow' at the pinned vstd and R4 would have no byte-identical R5 twin -- so C and Rust are pinned to different spellings here on purpose. See the why key."
      },
      {
        "c": "the destination is a FIXED-SIZE LOCAL of DST_CAP bytes, never an allocation and never a length from the file: `uint8_t dst[DST_CAP];` in both C rungs.",
        "rust": "the destination is a FIXED-SIZE LOCAL of DST_CAP bytes, never an allocation and never a length from the file: `let mut dst: [u8; DST_CAP] = [0; DST_CAP];` in all four Rust rungs."
      },
      {
        "c": "the COPY is a byte loop and not a bulk call in R1, R1h and R2: `dst[dlen++] = buf[off + i];` in both C rungs.",
        "rust": "the COPY is a byte loop and not a bulk call in R1, R1h and R2: `dst[dlen] = b;` in safe_naive.rs. safe_tuned.rs spells it copy_from_slice and unsafe.rs/verus.rs an unchecked indexed store, deliberately -- that is the measurement (NOTES.md 3) -- so this entry scopes to ONE Rust rung and its three scoped-absent pairs are correct."
      },
      {
        "c": "the string's LENGTH is folded whether or not the string was copied, so the checksum records that a rejected string was seen: `acc = acc * 31 + (uint64_t)slen;` in both C rungs.",
        "rust": "the string's LENGTH is folded whether or not the string was copied, so the checksum records that a rejected string was seen: `.wrapping_add(slen as u64)` in all four Rust rungs."
      },
      {
        "c": "the destination's LIVE LENGTH is folded, so a rung that truncated a string instead of skipping it cannot produce the same checksum: `(acc * 31 + (uint64_t)dlen) * 31` in both C rungs.",
        "rust": "the destination's LIVE LENGTH is folded, so a rung that truncated a string instead of skipping it cannot produce the same checksum: `.wrapping_add(dlen as u64).wrapping_mul(31)` in all four Rust rungs."
      },
      {
        "c": "the destination fold is byte-at-a-time Horner over the live prefix, spelled with the literal multiplier: `acc = acc * 31 + (uint64_t)dst[i];` in both C rungs.",
        "rust": "the destination fold is byte-at-a-time Horner over the live prefix, spelled with the literal multiplier: `.wrapping_mul(31).wrapping_add(` in all four Rust rungs. safe_tuned.rs spells the LOOP as .iter() over a reslice, which is why only the operation and not the loop form is pinned here."
      },
      {
        "c": "a string whose terminator is missing is the last string in the window: `if (q >= len)` in both C rungs.",
        "rust": "a string whose terminator is missing is the last string in the window: `if q >= len {` in all four Rust rungs. This line is also what makes `p = q + 1` provably overflow-free -- see verus.rs's header -- so it is required rather than conventional, exactly as on p11."
      },
      "the cursor steps PAST the terminator: `p = q + 1;` in all seven rungs.",
      {
        "c": "the walk is bounded by the WINDOW and never by the declared count: `if (p >= len)` in both C rungs. `nstr` appears in no loop bound in any rung.",
        "rust": "the walk is bounded by the WINDOW and never by the declared count: `if p >= len {` in all four Rust rungs. `nstr` appears in no loop bound in any rung."
      },
      "the little-endian u32 header decode is written out with + and * rather than | and <<, so it stays linear arithmetic: `+ 65536 *` in all seven rungs.",
      "...and its top byte: `+ 16777216 *` in all seven rungs.",
      {
        "c": "the declared count is folded, so a rung that walked a different number of strings cannot produce the same checksum either: `* 31 + (uint64_t)nstr` in both C rungs.",
        "rust": "the declared count is folded, so a rung that walked a different number of strings cannot produce the same checksum either: `.wrapping_add(nstr as u64)` in all four Rust rungs."
      }
    ],
    "forbidden": [
      "`strcat(`",
      "`strncat(`",
      "`snprintf(`",
      "`strlen(`",
      "`chunks_exact`",
      "`from_le_bytes`"
    ],
    "why": "each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). THE DESTINATION IS A FIXED-SIZE LOCAL AND THE ONLY THING R1 OMITS IS THE CAPACITY CHECK ON THE WRITE: every index into the SOURCE is correct in every rung, the scan is bounded by the window in every rung, and both outer bounds are kept in every rung, so R1-vs-R1h is the cost of the check and nothing else. `strcat(` and `strncat(` and `snprintf(` are forbidden because each of them moves the bound: `strcat` has none at all, so a rung using it could not express R1h; `strncat` and `snprintf` carry one INSIDE libc, so a rung using either would compare a hand-written check against a library's and the R1-vs-R1h column would become p11's library-vs-safety comparison wearing p12's label. `strlen(` is forbidden for the mirror-image reason: it is p11's bug, and a p12 rung that scanned with it would model TWO bugs at once -- an unbounded read AND an unbounded write -- so no adversarial row could attribute a behaviour to either. `chunks_exact` is forbidden for the destination fold because p16 measured that the chunk width moves that pattern's per-byte rate over a 31% range (5.04688...6.62500, `.memory/01-ladder.md`), and p12's whole published decomposition is into a per-scanned-byte, a per-copied-byte and a per-string term. `from_le_bytes` deletes the written-out little-endian header decode every rung shares AND is NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW), so a rung using it would compare a safe cell against an unsafe cell that cannot exist -- the `identity`-pin trap this block's own `identity` key sets. WHAT IS DELIBERATELY *NOT* PINNED, and it is the point of the pattern: **the COPY**. R1, R1h and R2 spell it as a byte loop and that IS pinned for them, because p02's retraction is the precedent -- one operator flips `bulk_calls` and 100% of the delta -- but R3 spells it `copy_from_slice` and R4/R5 spell it an unchecked indexed store, and holding those fixed would hold fixed the one thing p12 exists to compare. What IS pinned instead is that the DESTINATION is a fixed-size local of `DST_CAP` bytes in all seven rungs and that a string which does not fit is SKIPPED rather than truncated, because `dlen` is folded and a truncating rung would produce a different checksum. THE CAPACITY CHECK IS PINNED PER LANGUAGE AND THE TWO SPELLINGS DIFFER, WHICH IS ITSELF A MEASUREMENT: C writes `if (dlen + slen <= DST_CAP) {` and the four Rust rungs write `if slen <= DST_CAP && dlen + slen <= DST_CAP {`. The left conjunct is redundant as a test (`dlen >= 0`) and necessary as a proof obligation -- without it Verus rejects the additive sum with `possible arithmetic underflow/overflow`, because nothing at the pinned vstd bounds `slen` below `usize::MAX` (measured: 14 verified, 1 errors, ../NOTES.md 5). R4 must have a byte-identical R5 twin, so R4 carries it; R2 and R3 carry it so that the matched-spelling R2-vs-R4 difference really is matched; R1h does not, because R1h is not chained to the prover and putting it there would charge the C column for a Verus concession. That price -- +2 STATIC instructions, and 3.00 Ir PER STRING WALKED when measured as a whole-program marginal, `3.00*K - 1.00` exact at five K (../NOTES.md 5; p12 first published the static delta as if it were the per-string rate, corrected at TASK_040_REVIEW) -- is the FIRST MEASURED PRICE THE `identity` PIN HAS EXTRACTED FROM A SHIPPED CELL rather than from a rejected variant. The declaration was written BEFORE any cell was measured for perf -- the R5 proof, the checksums and the disassembly existed, no `Ir` and no `ns` did. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither."
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
      "verus.rs": 15
    },
    "twin_obligations": {
      "verus.rs": 18
    },
    "obligations_note": "15 = DST_CAP 1 + scan_end 1 + copy_into 1 + fold_dst 1 + walk 1 + kernel 5 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained, and the zero terms are checkable the same way: u32_at, nstr_at, zero_dst, fin and strcat_fold are NON-RECURSIVE spec fns and report 0; buf_get_unchecked, dst_get_unchecked, dst_set_unchecked, load_input and emit are external_body and report 0; scan_end, copy_into, fold_dst and walk are RECURSIVE and carry one termination query each. DST_CAP's 1 is a `const` inside verus!, which `.memory/04-verus.md` records as its own query (measured on p08's SCR and p03's STACK_CAP); p12 is the third pattern with one. kernel's 5 = body + FOUR loop bodies -- the string walk, the scan, the copy and the destination fold -- which is p12's contrast with p11's 4 (three loops), p07's 3 and p03's 2 (one loop): p12 has one more loop than p11 because the copy is a loop of its own, and no `by (nonlinear_arith)` sub-proof anywhere in the kernel because every multiplication in it is by a literal. main's 5 is quoted AS MEASURED and does not decompose from the command line: body + driver loop + one per by-block would predict 6 and Verus reports 5, the identical off-by-one p03's, p05's, p07's, p11's and p17's spec.md record for the identical driver. `.memory/04-verus.md`'s one-query-per-function-plus-one-per-loop rule of thumb gives 11 here and is therefore not the derivation.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 15 shipped + 3, and each of the 3 is measured the same way: `--cfg slb_twin --verify-function slb_twin_<name> --verify-root` reports `1 verified` for each of slb_twin_buf_get_unchecked, slb_twin_dst_get_unchecked and slb_twin_dst_set_unchecked -- one function, no loop body, no by-block. p12 is the first pattern with THREE twins, and the third of them is the first WRITE twin outside p03. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg.",
    "unsafe_justifications": {
      "verus.rs": {
        "dst_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `u8` is a legal thing to store in a `u8` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [u8; 128]` reads `i < 128`. This is the parameter-coverage false positive `.memory/04-verus.md` names and p03 was the first pattern to exercise; p12 is the second, and on p12 the item is the one the whole pattern is about. A second conjunct `old(v)@.len() == 128` is deliberately NOT written: for a `&mut [u8; 128]` it is a TAUTOLOGY discharged from the parameter type alone by vstd's `array_len_matches_n`, and p03's gate run refused exactly that draft (p03 NOTES.md 5b)."
      }
    },
    "items": {
      "verus.rs": {
        "u32_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "nstr_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "zero_dst": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "scan_end": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "copy_into": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold_dst": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fin": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "walk": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "strcat_fold": {
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
        "dst_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_dst_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "dst_set_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_dst_set_unchecked": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
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
            "r == strcat_fold(buf@, off as int, len as int)"
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
    "note": "work_per_call is **bytes of the window** -- `stride`, 133 on small and 159 on large -- which is p16's, p05's and p11's denomination. WHICH WAY THE ESTIMATE ERRS: STRICT, and by three corrections. It OVER-counts by the 4 header bytes and by one terminator per string (neither is copied or folded) and, on a REJECTING window, by every byte of a string that was scanned but not copied. It UNDER-counts by the whole of the second and third passes: every ACCEPTED byte is scanned, copied and folded, i.e. visited three times. On the two probe inputs -- which are 100% accept by construction, see inputs/gen.py -- the visits are 133 + 123 + 123 = 379 against a declared 133 and 159 + 124 + 124 = 407 against 159, so the under-count dominates by 2.8x and 2.6x, `stride` is well below the number of byte-visits, and the derived floor is one the kernel must clear. It can never let a collapsed kernel through, which is the only direction that matters. work_unit_bits is 8, one window byte, so the effective absolute bound under min_ir_per_work is 0.001953125 x 8 = 0.015625. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged, and the argument is p12-specific: the DESTINATION FOLD is a serial Horner chain `acc = acc*31 + b`, so byte i+1's multiply depends on byte i's and there is no vector form at any -march -- unlike the COPY, which is a `memcpy` in the rungs that spell it as one and in the rungs that do not, since both compilers rewrite the byte loop (NOTES.md 1). That is exactly why the unit is denominated over the whole window and not over the copy. The two probe inputs differ in work_per_call (133 vs 159) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost, on the first kernel in this project whose obligation is a WRITE whose guard sits a loop level above the store. The byte-identity result now covers a kernel with four loops, three of them carrying relational invariants, one of them mutating a fixed-size array through a trusted setter, four recursive spec functions and ZERO nonlinear arithmetic. At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."
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
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. On p12 there is a second and stronger reason: one of the three accessors WRITES, and `.memory/04-verus.md` records that the only backstop for a trusted body that does more than its `ensures` says is Miri on R4 -- the p08 `copy_nonoverlapping` substitution passed Verus, the twin, the contract pin and stages 5c/5c-req, and was caught by the O3 identity pin and Miri alone. A trusted `dst_set_unchecked` that wrote `i + 1` as well would satisfy this `ensures` on slot `i` and be invisible everywhere else. Cost: check.py rewrites n_iters to 4, so each row scans, copies and folds at most 4 x 3 x stride bytes -- about 1600 on small and 1900 on large, four orders of magnitude inside `.memory`'s measured 3.05 M budget. The only real cost is the 7.95 MB payload to_vec, and p07's 12 MB one passes.",
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

There is no exit 7 here, for p03's, p11's, p16's, p17's, p05's and p07's reason:
p12's payload names no allocation size, and the destination is a fixed-size local
in every rung, so p02's `SLB_MAX_CAP` check would be dead code.

**These are the CHECKED rungs' exit codes.** R1 exits 134 under gcc (the
`-fstack-protector-strong` canary) and 139 under clang (the return address is
gone) on `adversarial-overflow.bin`, and 0 with a wrong answer on
`adversarial-off1.bin` and `adversarial-nonul.bin`. `harness/check.py` records
that in its adversarial table rather than requiring it; `NOTES.md` 0 and 7 are
where it is read.

## Degenerate shapes

`stride_w >= 4 && stride_w <= n_blob` is the driver's whole input validation. A
stride below 4 cannot hold the header (`adversarial-stride3.bin`); a stride above
`n_blob` leaves no whole window, so `nwin` would be 0 and `k` would have nothing
to index. Either way the loop is skipped and the driver prints `0` after **zero**
kernel calls.

`adversarial-exact.bin` is the boundary from the safe side: four 32-byte strings
total **exactly** `DST_CAP`, every rung accepts all four, every rung agrees, and
the sanitizer is clean. `adversarial-off1.bin` is the **same four strings** plus
one string of length 1 — one byte over — and it is the sharpest row in the
pattern: the checked rungs reject the fifth string, R1 writes `dst[128]`, and R1
**exits 0 with a wrong answer under both compilers**. The two blobs share one
draw of their first four strings, so they differ in the two extra bytes and in
nothing else.

`adversarial-empty.bin` is the degenerate copy: `nstr == 8` and eight zero bytes,
so every string is empty, every one of them is *accepted* (`0 + 0 <= 128`),
`dlen` stays 0 and the destination fold never runs. It is the row where the
per-string constant is measured with both byte terms set to zero, and it returns
exactly `nstr == 8`.

The kernel's `len < 4` guard is, given the driver's `stride_w >= 4`, unreachable
in this benchmark. It is kept anyway so the kernel is **total** and its
`requires` stays purely structural; the alternative — a `len >= 4` precondition —
would be a precondition about the driver's own guard rather than about the
buffer.
