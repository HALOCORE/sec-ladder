# p13 — `strncpy` truncation: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, and C spells the pair
out. C is handed the blob length and *both* C rungs ignore it — p13's contrast
with p02, p16 and p17, where the check the C rung skips is against a length it
was handed. **Here the number the programmer needed was `sizeof dst - 1`.**

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     nstr      u32 LE    DECLARED string count    ATTACKER DATA
byte 4..      packed, NUL-terminated strings
data_start = 4
DST_CAP = 32                      the destination's capacity AND the `n` every
                                  rung passes to `strncpy`; a compile-time
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

dst = [0; DST_CAP] ;  acc = 0 ;  p = 4                     # dst is a LOCAL
for s in 0 .. nstr:
    q = p
    while q < len and buf[off + q] != 0:      q += 1       # bounded in EVERY rung
    slen = q - p

    # --- the copy: EXACT strncpy(dst, src, sizeof dst) semantics ---
    n = min(slen, DST_CAP)
    for i in 0 .. n:         dst[i] = buf[off + p + i]
    for i in n .. DST_CAP:   dst[i] = 0                    # strncpy's zero-fill
    # >>> THE TERMINATION. R1 omits exactly this line and nothing else. <<<
    dst[DST_CAP - 1] = 0

    # --- the CONSUMER: the site where the harm lands ---
    d = 0 ; while dst[d] != 0:  d += 1                     # UNBOUNDED in C
    acc = acc *64 31 +64 d
    for i in 0 .. DST_CAP:  acc = acc *64 31 +64 dst[i]    # FULL-EXTENT fold

    if q >= len:   break                       # no terminator: last string
    p = q + 1
    if p >= len:   break
return acc *64 31 +64 nstr
```

`*64`/`+64` are wrapping, as in every earlier pattern, so the kernel has **no
precondition on values** and every measured input is inside the verified domain
by construction. C's unsigned types wrap by definition (6.2.5p9) and the Rust
rungs write `wrapping_add`/`wrapping_mul`.

### The bug is a CORRECTLY-CALLED LIBRARY FUNCTION, and the harm lands elsewhere

Every other R1 in this project omits a line a careful programmer would have
written: a length check, a capacity check, a signedness fix. p13's omits
nothing of the sort. `strncpy(dst, src, sizeof dst)` is textbook C and correct
by the letter of its man page; it simply **does not NUL-terminate when the
source is at least as long as `n`**, and the terminator a short string gets is a
side effect of the zero-*padding* rather than something `strncpy` wrote on
purpose.

Two consequences, and both are structural rather than choices:

- **The bug site and the harm site are different.** The copy writes exactly
  `DST_CAP` bytes into a `DST_CAP`-byte array, every time, on every input: it is
  memory-safe in R1 too. The out-of-bounds access is a **read**, it is of the
  *destination*, and it happens in the consumer. That is why the proof shape is
  new — the obligation is at the read and what discharges it is an invariant
  about the array's contents established at the write.
- **`small` and `large` must be 100% NON-TRUNCATING, and that is not
  negotiable.** `harness/check.py`'s `check_checksums` requires every cell, R1
  included, to print `model.py`'s checksum on every non-adversarial **matrix**
  input (`sweep-*` is dropped before it, at `check.py:469`). The source scan
  stops at the first zero byte, so every copied byte is non-zero, and the
  zero-fill is empty exactly when `slen >= DST_CAP`; `dst` therefore holds a NUL
  **iff** the string was short. On a truncating window R1's consumer reads past
  `dst[31]` and its answer is built from stack residue — and on some builds
  **that answer is not stable across runs of the same binary** (measured over 60
  runs each: 3 of `c-clang`'s 4 builds give two different answers, all 4 of
  `c-gcc`'s are stable; `NOTES.md` 0b and 7). So no truncating row can also be a
  checksum-agreeing one.

  ⚠ **This is where TASK_043's input table is wrong**, and the correction is a
  deliverable of the task that built this pattern: it asks `large` for "a
  different truncation ratio" from `small`. What differs between them instead is
  the **length distribution below `DST_CAP`** (mean 7.00 against 22.04), the
string count (13 against 24) and the
  working-set size. The truncation-ratio axis lives in `sweep-t*` and in the
  adversarial rows, and R1 is absent from the truncating part of both.

### THE TWO HARMS ARE NOT SEPARABLE BY INPUT. They separate by RUNG.

TASK_043 asks for an `adversarial-truncate` row on which "truncation changes the
answer while every rung stays memory-safe". **No such input exists**, and the
reason is one equivalence:

```
content is lost   <=>   slen >= DST_CAP   <=>   dst holds no NUL   <=>   R1 reads OOB
```

The two harms fire on **exactly the same inputs**. What separates them is which
rung shows which:

| harm | what it is | which rungs have it |
|---|---|---|
| **truncation** | a memory-safe **wrong answer** — everything past `DST_CAP` is discarded and nothing records that it existed | **every** rung, R5 included |
| **missing NUL** | an out-of-bounds **read** of the frame | **R1 only**; the checked rungs cannot express it |

`inputs/gen.py` builds a **controlled triple** to make the first one visible on
its own: `adversarial-exact` (four 31-byte strings), `adversarial-truncate` (the
same 31 bytes plus one) and `adversarial-truncate-alt` (the same 31 bytes plus
nine) share one draw of their heads and **print the identical checksum in every
checked rung**. Three inputs that differ in 0, 1 and 9 dropped bytes are
indistinguishable to a correct, proven, memory-safe program. `exact` is
sanitizer-clean and the other two are not — same triple, both harms, attributed.

### The source scan is bounded by the window in every rung, and that is deliberate

R1 keeps the window bound on the source scan, both outer bounds
(`if (q >= len) break;`, `if (p >= len) break;`), the `min(slen, DST_CAP)` cap
on the copy and the whole zero-fill. p11 already measured the unbounded *source*
scan; importing it here would put **two** bugs in one kernel and no adversarial
row could attribute a behaviour to either.

`adversarial-nonul-src.bin` is p11's malformed record arriving through p13's
bug: the source scan stops correctly at the window end, the measured length is
`len - p = 40`, and it is the **destination** scan that overruns.

### The scan, the copy, the fill and the consumer are four loops

Fusing any pair deletes the pattern. If the consumer were fused into the copy,
`d` would be `n` by construction and the missing terminator could not be
observed at all — the whole point is that the destination is written by one loop
and *read back as a C string* by another. If the zero-fill were fused into the
copy, `strncpy`'s O(`DST_CAP`) cost would disappear along with the only reason a
short string ends up terminated.

**That the split survives `-O3` is measured and not assumed** (`NOTES.md` 3d),
including which of the four loops each compiler turns into a library call.

### Load-bearing, do not "improve"

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug. Edit both or neither.

- **The destination is a fixed-size local of `DST_CAP` bytes in all eight
  rungs**, never an allocation and never a length from the file.
- **A string that does not fit is TRUNCATED, not skipped.** `n = min(slen,
  DST_CAP)`; there is no rejection anywhere. A *rejecting* kernel is p12 — that
  is the whole difference between the two patterns, and it is why p13 does not
  inherit p12's forced-adversarial-row rule (`.memory/02-bench-rules.md`: p13's
  guard-equivalent is a caller-supplied `n`, and `n <= sizeof dst` is the
  *correct* case).
- **`dst` is written in FULL on every iteration** — by the copy when
  `slen >= DST_CAP`, by the copy plus the zero-fill otherwise. That is real
  `strncpy` semantics and it is what keeps this pattern free of any
  uninitialised read (C's `uint8_t dst[32];` is never read before every byte of
  it has been written) and free of any dependence on the previous iteration's
  contents. **Do not "optimise" the zero-fill away in any rung**; it is the
  thing being measured.
- **The consumer is unbounded in C and in the unsafe rungs, and that asymmetry
  is the pattern rather than a rigged comparison.** The three answers a language
  gives to a destination with no terminator are C **reads the frame**, R2
  **panics**, R3 **returns `DST_CAP`** — reported as a *semantics* difference
  and not as a safety cost (`.memory/01-ladder.md` finding 9's rule),
  `NOTES.md` 4.
- **`d` is folded, and so is the destination's WHOLE EXTENT** — all `DST_CAP`
  bytes, in order — so a rung that terminated the destination somewhere else,
  copied nothing, or copied the *wrong bytes*, cannot produce the same
  checksum. ⚠ **Until TASK_046 the fold was `d` and `dst[0]` only** (TASK_043
  specified it; `.memory/02-bench-rules.md` has said *keep the full-extent
  fold* since TASK_004_REVIEW), and `NOTES.md` 6a measures what that cost: a
  rung copying `0xFF` into every slot but the first agreed with `model.py` on
  **all nine shipped inputs**. It does not now. The two worries that produced
  the narrow fold were both measured and both unfounded — the
  `exact`/`truncate`/`truncate-alt` triple still prints one checksum, and no C
  cell elides the copy in `whole` mode.
- **The library call itself is forbidden in every rung.** `strncpy(`, `strlcpy(`
  and `snprintf(` are measured as controls (`controls/library_axis.py`), where
  the routine can be named beside every rate; a rung that called one would turn
  R1-vs-R1h into p11's library-vs-safety comparison wearing p13's label.
- Wrapping arithmetic throughout.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == strncpy_fold(buf, off, len)
```

`strncpy_fold` is the spec function; `model.py` is its independent Python twin.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included, and `harness/check.py` evaluates it at every one of the
kernel calls to prove that it does. `nstr`, all 2^32 values of it, and every byte
of the window are *arguments* of the problem; the kernel is total in all of them.

**It is ONE clause**, as on p03, p11 and p12 and unlike p17 — and keeping it at
one cost **one** program line here (`if (q >= len) break;`) where p12 needed two:
p13's `min` against a compile-time constant is both the library's truncation and
the prover's overflow bound, so the second line p12 bought has no analogue.
`NOTES.md` 5.

### What the `ensures` is, and what it is not

p13 has a **local** destination, so its shape is p03's and p12's: the security
property is carried by the trusted accessors' discharged `requires`. **What is
new is which accessor is hard.** p12's is the *write*; p13's writes are
trivially in bounds (`i < n <= DST_CAP`, `j < DST_CAP`, both against a
compile-time constant in the same basic block). The hard one is
`dst_get_unchecked`'s `i < v@.len()`, at a call site inside a loop **with no
bound at all**, discharged from `dst@[DST_CAP - 1] == 0` — a fact about the
array's *contents*, established by the statement `c/kernel.c` omits.

The `ensures` is what keeps the proof non-vacuous and pins **where the consumer
stopped**: `walk` threads `dst` as a `Seq<u8>`, `copy_into` and `fill_zero` are
`strncpy`'s two halves byte at a time, and `scan_dst` is the consumer.

**And there is a second thing the `ensures` deliberately does not say: that
`nstr` is honest, that the strings are terminated, or that they fit.**
`adversarial-truncate.bin`, `adversarial-truncate-alt.bin`,
`adversarial-nonul-dst.bin` and `adversarial-nonul-src.bin` are all inside the
verified domain and every checked rung agrees with `model.py` on all four.
Writing the stronger postcondition would have forced a `requires` about the
contents of a file that no honest loader can discharge
(`.memory/02-bench-rules.md`), and it would have deleted the four rows the
pattern exists for.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p13's payload is p11's, p12's, p03's, p16's, p17's,
p05's and p07's:

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes`, reused verbatim, with **nothing added to `common/` for
p13**. All three are a bulk copy rather than an element-by-element decode, which
is what keeps every p13 row Miri-checkable.

Nothing is a compile-time constant except `DST_CAP`, which is the *destination's*
capacity and is a property of the program rather than of the input: `n_iters`,
`stride`, `n_blob`, every `nstr`, every string length and every byte come from
the file.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here and are
deliberately not copied across.

## Driver loop

Identical in all eight rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers, and byte-for-byte p11's and p12's. `harness/check.py` normalises every
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

`stride_w >= 4` because p13's window header is the 4-byte `nstr` field.
`adversarial-stride3.bin` attacks it. The comparison is in `u64` *before* the
`as usize` cast, so a truncating driver cannot sneak a 2^40 stride past it.

### Why this does not evaporate

Same mechanism as every earlier pattern: `k` is derived from `acc`, and `acc`
from the previous call's result, so call *i+1* cannot begin until call *i* has
returned. Nothing to CSE, nothing to hoist, no `black_box` and no `asm volatile`.

⚠ This matters more than usual here and it was measured: p13's **phase-0 probe**
used `__attribute__((noinline))` alone and gcc CSE'd the call out of its
repetition loop anyway, reporting 6.28 `Ir`/call for 64 strings. `noinline` is
not a barrier; the data dependence is. `NOTES.md` 0.

### Why every adversarial input is exactly one window

`k` is pseudo-random over `[0, nwin)`, so with several windows a malformed one
would be hit only probabilistically. With `nwin == 1`, `k` is always 0 and `off`
is always 0, so R1's overread happens on every call deterministically.

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
| `verus.obligations` = 19 | **`DST_CAP` 1 + `scan_end` 1 + `copy_into` 1 + `fill_zero` 1 + `scan_dst` 1 + `fold_dst` 1 + `walk` 1 + `kernel` 7 + `main` 5 = 19.** Every term was measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, and so were the zero terms. `kernel`'s 7 is 1 body + 1 per loop body (**six** loops: the string walk, the source scan, the copy, the zero-fill, the consumer and the full-extent fold), the highest in the project — p12's is 5, p11's 4, p07's 3, p03's 2. The sixth loop and the sixth recursive spec function both arrived at TASK_046 with the fold repair. **`main`'s 5 is quoted as measured** — the by-block rule of thumb predicts 6 — the identical off-by-one p03, p05, p07, p11, p12 and p17 record for the identical driver. |
| `verus.twin_obligations` = 22 | the count under `--cfg slb_twin`. **19 shipped + 3**, one per twin, each measured at `1 verified`. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`, and since TASK_010 that does not make Miri optional: it is mandatory for any pattern with a trusted item. On p13 the argument is stronger than usual, because the pattern's obligation is an **unbounded read loop** — see the `miri.reason` key. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == strncpy_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (strncpy_fold). p13's bindings are the READ-ONLY set p03, p11, p12, p16, p17, p05 and p07 use and NOT p02's before/after set: the destination is a fixed-size LOCAL inside the kernel, so no buffer crosses the signature and there is nothing for a `dst_after` binding to name. That is p12's shape exactly. **What is NOT p12's shape is where the security property lives.** p12's is carried by a trusted WRITE accessor's discharged `requires`; p13's copy and fill are trivially in bounds (`i < n <= DST_CAP` and `j < DST_CAP`, both against a compile-time constant in the same basic block) and the obligation that is hard is on a trusted READ accessor, `dst_get_unchecked`'s `i < v@.len()`, at a call site inside a loop WITH NO BOUND AT ALL. What discharges it is not a guard on the index but a fact about the array's CONTENTS -- `dst@[DST_CAP - 1] == 0` -- established by a different statement, the one c/kernel.c omits. That is the first two-site obligation in this project. The `ensures` is what keeps the proof non-vacuous and pins WHERE THE CONSUMER STOPPED: `walk` threads the destination as a `Seq<u8>`, `copy_into` and `fill_zero` are `strncpy`'s two halves byte at a time, and `scan_dst` is the consumer, so a rung that terminated the destination somewhere else, or copied a different number of bytes, cannot satisfy it. **What the `ensures` deliberately does NOT say is that `nstr` is honest, that the strings are terminated, or that they FIT.** `walk` specifies what the PROGRAM does -- truncate at `DST_CAP`, stop at the first zero byte or at the window end -- so adversarial-truncate.bin, adversarial-truncate-alt.bin, adversarial-nonul-dst.bin and adversarial-nonul-src.bin are all INSIDE the verified domain and every checked rung agrees with model.py on all four. A `requires` that the strings fit would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete the four rows the pattern exists for. **And the fold is FULL-EXTENT: `d`, then every one of the DST_CAP destination bytes.** Until TASK_046 it was `d` and `dst[0]` only -- TASK_043 specified that and this file inherited it, against `.memory/02-bench-rules.md`, which has said keep the full-extent fold since TASK_004_REVIEW. ../controls/oracle_hole.py measures what the narrow fold cost: a rung copying 0xFF into every slot but the first agreed with model.py on all NINE shipped inputs, so check.py stage 2 and stage 5d both passed a rung that copied the wrong bytes. Under the full-extent fold it does not. Both worries that produced the narrow fold were measured and both are unfounded: the exact/truncate/truncate-alt triple still prints ONE checksum, because n = min(slen, DST_CAP) caps the copy and the termination store overwrites the last slot so `dst` is byte-identical across the three, and no C cell elides the copy in whole mode. ../NOTES.md 6a.",
  "idiom": {
    "required": [
      {
        "c": "the SOURCE scan is bounded by the WINDOW in every rung, R1 included -- p13's bug is the destination read and not the source scan: `while (q < len)` in both C rungs.",
        "rust": "the SOURCE scan is bounded by the WINDOW in every rung, R1 included -- p13's bug is the destination read and not the source scan: `while q < len` in all four Rust rungs."
      },
      {
        "c": "THE TERMINATION, and the only line c/kernel.c omits: `dst[DST_CAP - 1] = 0;` in c/kernel_hardened.c. c/kernel.c omits exactly this statement and nothing else, so the scoped-absent audit pair this entry reports is on that rung and IS the pattern.",
        "rust": "THE TERMINATION: `DST_CAP - 1` in all four Rust rungs. The four spell the store three ways on purpose -- an indexed store in safe_naive.rs and safe_tuned.rs, get_unchecked_mut in unsafe.rs and the trusted setter dst_set_unchecked in verus.rs -- so what is pinned across all four is the INDEX, which no spelling of the store can avoid naming."
      },
      {
        "c": "strncpy's n: the copy is capped by the DESTINATION's capacity and a string that does not fit is TRUNCATED, never rejected and never skipped (a rejecting kernel is p12): `n = slen < DST_CAP ? slen : DST_CAP;` in both C rungs.",
        "rust": "strncpy's n: the copy is capped by the DESTINATION's capacity and a string that does not fit is TRUNCATED, never rejected and never skipped (a rejecting kernel is p12): `let n: usize = if slen < DST_CAP { slen } else { DST_CAP };` in all four Rust rungs."
      },
      {
        "c": "strncpy's ZERO-FILL, the half nobody expects, and the reason the per-string cost is O(DST_CAP) rather than O(slen): `for (i = n; i < DST_CAP; i++)` in both C rungs. It is also the ONLY reason a short string ends up terminated at all.",
        "rust": "strncpy's ZERO-FILL, the half nobody expects, and the reason the per-string cost is O(DST_CAP) rather than O(slen), runs in EVERY Rust rung -- but its LOOP FORM is deliberately not pinned in any of them, so this half of the entry backticks no spelling and pins nothing. Until TASK_046 it pinned the byte-loop spelling in safe_naive.rs, unsafe.rs and verus.rs and exempted safe_tuned.rs by name, while p13's headline is R3 - R4: a scoped entry that binds one side of a published comparison and frees the other. It was relaxed symmetrically rather than kept, and the direction was measured first -- ../NOTES.md 10. What the shipped rungs spell, as an observation and not as a pin: a byte loop in safe_naive.rs, unsafe.rs and verus.rs, fill(0) in safe_tuned.rs."
      },
      {
        "c": "THE CONSUMER, and it is UNBOUNDED: `while (dst[d] != 0)` in both C rungs. This is the site where p13's harm lands and it is NOT where the bug is written; bounding it would be a different and easier fix and would stop the cell being a matched spelling against R1.",
        "rust": "THE CONSUMER: `d = d + 1;` in safe_naive.rs, unsafe.rs and verus.rs -- an unbounded scan for the first zero byte of the DESTINATION, indexed in safe_naive.rs and UNCHECKED in unsafe.rs/verus.rs. safe_tuned.rs spells the whole loop with position(), so this entry scopes to THREE Rust rungs and its one scoped-absent pair is correct. UNLIKE the COPY and the ZERO-FILL entries this scoping is NOT a thumb on the scale, and the difference is measured rather than argued: position() is not supported at the pinned vstd, so no admissible R4/R5 pair can spell it whatever this block says (../NOTES.md 10b), where the bulk copy and fill spellings verify at 17/0 with a 24/0 twin. What this entry also does not do is BOUND the loop: a bounded indexed scan verifies at 19/0 -- the SHIPPED counts, unmoved -- with no new trusted item, so the unbounded form is held by FIAT and ../NOTES.md 10b prices it -- bounding the consumer would turn p13's two-site obligation into a loop bound and stop R4/R5 being matched spellings against R1's runaway scan."
      },
      {
        "c": "where the consumer STOPPED is folded, so a rung that terminated the destination somewhere else cannot produce the same checksum: `acc = acc * 31 + (uint64_t)d;` in both C rungs.",
        "rust": "where the consumer STOPPED is folded, so a rung that terminated the destination somewhere else cannot produce the same checksum: `.wrapping_add(d as u64)` in all four Rust rungs."
      },
      {
        "c": "the destination is folded over its WHOLE EXTENT -- every one of the DST_CAP bytes and not merely the first -- so a rung that copied the WRONG BYTES cannot produce the same checksum: `acc = acc * 31 + (uint64_t)dst[i];` in both C rungs.",
        "rust": "the destination is folded over its WHOLE EXTENT -- every one of the DST_CAP bytes and not merely the first -- so a rung that copied the WRONG BYTES cannot produce the same checksum: `while fi < DST_CAP` in all four Rust rungs. What each rung READS inside that loop differs by rung on purpose -- indexed in safe_naive.rs and safe_tuned.rs, get_unchecked in unsafe.rs, the trusted accessor in verus.rs -- which is the ladder itself, so what is pinned across all four is the EXTENT, which no spelling of the read can avoid naming."
      },
      {
        "c": "the destination is a FIXED-SIZE LOCAL of DST_CAP bytes, never an allocation and never a length from the file: `uint8_t dst[DST_CAP];` in both C rungs.",
        "rust": "the destination is a FIXED-SIZE LOCAL of DST_CAP bytes, never an allocation and never a length from the file: `let mut dst: [u8; DST_CAP] = [0; DST_CAP];` in all four Rust rungs."
      },
      {
        "c": "the COPY is a byte loop and not a bulk call in BOTH C rungs, so R1-vs-R1h carries no library term: `for (i = 0; i < n; i++)` in both C rungs.",
        "rust": "the COPY's LOOP FORM is deliberately not pinned in any Rust rung, so this half of the entry backticks no spelling and pins nothing. Until TASK_046 it pinned the byte-loop spelling in safe_naive.rs, unsafe.rs and verus.rs and exempted safe_tuned.rs by name, while p13's headline is R3 - R4: a scoped entry that binds one side of a published comparison and frees the other. An admissible bulk-spelled R4/R5 pair EXISTS -- copy_nonoverlapping plus write_bytes, 17 verified / 0 errors, twin 24/0, identity exact, TCB 5 to 7 -- so the prover was never what excluded it. Relaxed symmetrically; ../NOTES.md 10 has the direction and both bounds. What the shipped rungs spell, as an observation and not as a pin: a byte loop in safe_naive.rs, unsafe.rs and verus.rs, copy_from_slice in safe_tuned.rs."
      },
      {
        "c": "a string whose terminator is missing is the last string in the window: `if (q >= len)` in both C rungs.",
        "rust": "a string whose terminator is missing is the last string in the window: `if q >= len {` in all four Rust rungs. This line is also what makes `p = q + 1` provably overflow-free -- see verus.rs's header -- so it is required rather than conventional, exactly as on p11 and p12."
      },
      "the cursor steps PAST the terminator: `p = q + 1;` in all eight rungs.",
      {
        "c": "the walk is bounded by the WINDOW and never by the declared count: `if (p >= len)` in both C rungs. `nstr` appears in no loop bound in any rung.",
        "rust": "the walk is bounded by the WINDOW and never by the declared count: `if p >= len {` in all four Rust rungs. `nstr` appears in no loop bound in any rung."
      },
      "the little-endian u32 header decode is written out with + and * rather than | and <<, so it stays linear arithmetic: `+ 65536 *` in all eight rungs.",
      "...and its top byte: `+ 16777216 *` in all eight rungs.",
      {
        "c": "the declared count is folded, so a rung that walked a different number of strings cannot produce the same checksum either: `* 31 + (uint64_t)nstr;` in both C rungs.",
        "rust": "the declared count is folded, so a rung that walked a different number of strings cannot produce the same checksum either: `.wrapping_add(nstr as u64)` in all four Rust rungs."
      }
    ],
    "forbidden": [
      "`strncpy(`",
      "`strlcpy(`",
      "`snprintf(`",
      "`strcat(`",
      "`strlen(`",
      "`chunks_exact`",
      "`from_le_bytes`"
    ],
    "why": "each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). THE ONLY THING R1 OMITS IS THE TERMINATION STORE, AND THE HARM IT CAUSES IS AT A DIFFERENT SITE: every index into the SOURCE is correct in every rung, the source scan is bounded by the window in every rung, the copy is capped at `n = min(slen, DST_CAP)` in every rung and the zero-fill runs in every rung -- so the copy is memory-safe in R1 too, and R1-vs-R1h is the cost of `dst[DST_CAP - 1] = 0;` and nothing else. `strncpy(`, `strlcpy(` and `snprintf(` are forbidden because each of them moves the TERMINATION, or the absence of it, INSIDE libc: `strncpy` is the routine whose exact semantics every rung spells out by hand, so a rung that called it would make R1-vs-R1h a comparison against glibc's IFUNC-dispatched vector implementation rather than against one store; `strlcpy` ALWAYS terminates, so a rung using it could not express R1 at all; `snprintf` always terminates and also parses a format string. All three are measured as CONTROLS instead -- `controls/library_axis.py`, ../NOTES.md 3 -- where the routine is named beside every rate, which is `.memory/01-ladder.md` finding 9's rule, and where the four-way comparison is the pattern's largest single effect. `strcat(` is p12's bug and `strlen(` is p11's; a p13 rung using either would model TWO bugs at once -- an unbounded write or an unbounded SOURCE read on top of p13's unbounded DESTINATION read -- so no adversarial row could attribute a behaviour to either. `chunks_exact` is forbidden because p16 measured that the chunk width moves that pattern's per-byte rate over a 31% range (5.04688...6.62500, `.memory/01-ladder.md`), and p13's published decomposition is into a per-string, a per-scanned-byte, a per-copied-byte and a per-truncated-string term. `from_le_bytes` deletes the written-out little-endian header decode every rung shares AND is NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW), so a rung using it would compare a safe cell against an unsafe cell that cannot exist -- the `identity`-pin trap this block's own `identity` key sets. WHAT IS DELIBERATELY *NOT* PINNED, and it is the point of the pattern: **the COPY, the ZERO-FILL and the CONSUMER's loop form**. ON THE RUST SIDE THAT IS NOW SYMMETRIC AND UNTIL TASK_046 IT WAS NOT, which is a measured defect and not a rewording. This block used to pin the byte-loop copy and fill in safe_naive.rs, unsafe.rs and verus.rs and exempt safe_tuned.rs BY NAME, while p13's headline is R3 - R4: only the safe rung was permitted the spelling the headline is about. The direction test (`.memory/01-ladder.md`) fired on it -- see ../NOTES.md 10 for the number -- and the excuse that had been offered for the unsearched R4 side, that R4 is chained to the prover by the `identity` pin, is FALSE HERE and was measured to be: copy_nonoverlapping and write_bytes give an admissible R4/R5 pair at 17 verified / 0 errors, twin 24/0, identity exact, TCB 5 to 7. The copy and the fill entries are therefore relaxed symmetrically -- the Rust half of each backticks NO spelling -- and the shipped R4 is NOT re-spelled, so both bounds are published: R3ship - R4ship with R4 held fixed, and R3ship - inf(in-contract R4) beside it (`.memory/02-bench-rules.md`'s reporting corollary). THE CONSUMER IS A DIFFERENT CASE AND STAYS PINNED, because the exclusion is enforced one layer down rather than by this block: R3's position(...).unwrap_or(DST_CAP) is not supported at the pinned vstd, so no admissible R4/R5 pair can spell it, and `controls/gen_bulk_r5.py` is where that is a Verus run rather than a citation. The consumer is an indexed unbounded scan in R1/R1h/R2, an UNCHECKED unbounded scan in R4/R5 and position in R3, and the three spellings are the three answers a language gives to a destination with no terminator: C READS THE FRAME, R2 PANICS, R3 RETURNS `DST_CAP`. What the consumer entry holds by FIAT rather than by the prover is that the R4/R5 scan is UNBOUNDED -- a bounded indexed scan verifies at 19/0 with no new trusted item -- and ../NOTES.md 10b prices that fiat rather than asserting it is free, because bounding the consumer turns p13's two-site obligation into a loop bound and stops R4/R5 being matched spellings against R1's runaway scan. What IS pinned instead is that the destination is a fixed-size local of `DST_CAP` bytes in all eight rungs, that the copy is capped by `min(slen, DST_CAP)` rather than by a rejection, and that `d` and the destination's WHOLE EXTENT are folded. THE TERMINATION STORE IS PINNED PER LANGUAGE AND THE RUNGS SPELL IT THREE WAYS, WHICH IS ITSELF THE MEASUREMENT: `dst[DST_CAP - 1] = 0;` in c/kernel_hardened.c, safe_naive.rs and safe_tuned.rs; `*dst.get_unchecked_mut(DST_CAP - 1) = 0;` in unsafe.rs; `dst_set_unchecked(&mut dst, DST_CAP - 1, 0);` in verus.rs -- and ABSENT from c/kernel.c, which is the bug. The scoped-absent audit pairs this entry reports on c/kernel.c are therefore CORRECT and are the pattern. **p12's `slen <= DST_CAP` conjunct has no analogue here**, and that is a measured difference rather than an omission: p12 had to buy an extra conjunct because `dlen + slen` is a `usize` addition that nothing bounded, while p13's `n = min(slen, DST_CAP)` caps the copy against a compile-time constant BEFORE any addition happens, so Verus discharges the copy loop with no extra program text and p13's identity pin extracts no price from any shipped cell. THE DECLARATION WAS WRITTEN BEFORE ANY SHIPPED CELL WAS MEASURED FOR PERF, and what did exist first is stated exactly rather than glossed: a PHASE-0 PROBE (`.temp/p13/phase0/probe.c`, two `noinline` kernels in one translation unit, not rungs) had measured that the termination store survives at `-O3` on both compilers and costs 1.00 Ir per string, and that the runaway consumer leaves the frame by 1 to 7 bytes. That probe is what decided the pattern was worth building; it decided no spelling in this block. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither."
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
      "verus.rs": 22
    },
    "obligations_note": "19 = DST_CAP 1 + scan_end 1 + copy_into 1 + fill_zero 1 + scan_dst 1 + fold_dst 1 + walk 1 + kernel 7 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained, and the zero terms are checkable the same way: u32_at, nstr_at, zero_dst, fin and strncpy_fold are NON-RECURSIVE spec fns and report 0; buf_get_unchecked, dst_get_unchecked, dst_set_unchecked, load_input and emit are external_body and report 0; scan_end, copy_into, fill_zero, scan_dst, fold_dst and walk are RECURSIVE and carry one termination query each. DST_CAP's 1 is a `const` inside verus!, which `.memory/04-verus.md` records as its own query (measured on p08's SCR and p03's STACK_CAP); p13 is the fourth pattern with one. kernel's 7 = body + SIX loop bodies -- the string walk, the source scan, the copy, the ZERO-FILL, the CONSUMER and the FULL-EXTENT FOLD -- which is the highest in the project and is p13's contrast with p12's 5 (four loops), p11's 4, p07's 3 and p03's 2. The sixth arrived at TASK_046 with the fold repair: `.memory/02-bench-rules.md` has required the full-extent fold since TASK_004_REVIEW and p13 shipped a two-term one at TASK_043's instruction. There is no `by (nonlinear_arith)` sub-proof anywhere in the kernel because every multiplication in it is by a literal. main's 5 is quoted AS MEASURED and does not decompose from the command line: body + driver loop + one per by-block would predict 6 and Verus reports 5, the identical off-by-one p03's, p05's, p07's, p11's, p12's and p17's spec.md record for the identical driver. `.memory/04-verus.md`'s one-query-per-function-plus-one-per-loop rule of thumb gives 12 here and is therefore not the derivation.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 19 shipped + 3, and each of the 3 is measured the same way: `--cfg slb_twin --verify-function slb_twin_<name> --verify-root` reports `1 verified` for each of slb_twin_buf_get_unchecked, slb_twin_dst_get_unchecked and slb_twin_dst_set_unchecked -- one function, no loop body, no by-block. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg.",
    "unsafe_justifications": {
      "verus.rs": {
        "dst_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `u8` is a legal thing to store in a `u8` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [u8; 32]` reads `i < 32`. This is the parameter-coverage false positive `.memory/04-verus.md` names and p03 was the first pattern to exercise; p13 is the third. A second conjunct `old(v)@.len() == 32` is deliberately NOT written: for a `&mut [u8; 32]` it is a TAUTOLOGY discharged from the parameter type alone by vstd's `array_len_matches_n`, and p03's gate run refused exactly that draft (p03 NOTES.md 5b)."
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
        "fill_zero": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "scan_dst": {
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
        "strncpy_fold": {
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
            "r == strncpy_fold(buf@, off as int, len as int)"
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
    "note": "work_per_call is **`DST_CAP * strings-walked + source-bytes-scanned`** -- 520 on small and 1321 on large -- and NOT `stride`, which is what p11, p12, p16, p05 and p07 all use. ⚠ THAT SUBSTITUTION IS A MEASURED CORRECTION AND NOT A PREFERENCE, AND IT COST A SECOND ONE. `strncpy` writes DST_CAP bytes per string however short the source is, so p13 is the first kernel in this project whose per-call cost is NOT monotone in the window length. The first pick of small/large put the two at opposite ends of the count/length trade -- 20 strings of mean 6.35 in a 151-byte window against 10 of mean 23.60 in a 250-byte window -- and on a `stride` denomination check_marginal_ir's d(Ir)/d(work) came out NEGATIVE in 16 of the 32 cells (-2.09 to -10.83, `.temp/p13/gate1.log`), while on THIS denomination it came out negative in the OTHER 16 (`.temp/p13/gate2.log`). The Ir ORDERING between those two inputs is CELL-DEPENDENT, so no scalar work measure could have passed. inputs/gen.py now requires `large` to DOMINATE `small` componentwise -- 24 strings of mean 22.04 against 13 of mean 7.00, every large string at least as long as every small one -- and asserts it at generation time. The gate caught both defects, which is exactly what that assertion exists for. WHICH WAY THE ESTIMATE ERRS: STRICT. Per string the kernel visits (slen+1) source bytes scanned -- counted -- plus n copied and (DST_CAP - n) zero-filled -- counted, together exactly DST_CAP -- plus 1 termination store, (d+1) consumer bytes and DST_CAP bytes read by the FULL-EXTENT FOLD, and the last three are NOT counted. On small the visits are 104 + 91 + 325 + 13 + 104 + 416 = 1053 against a declared 520; on large 553 + 529 + 239 + 24 + 553 + 768 = 2666 against 1321. The over-counting terms -- the 4 header bytes are read as a u32 and are in neither column -- are tiny beside that. So the declared work is under the number of byte-visits on every input, the derived floor is one the kernel must clear, and it can never let a collapsed kernel through, which is the only direction that matters. The MINIMUM over visited windows is taken rather than the mean or the maximum, because a floor may not be raised by a window the driver never reaches; on every input this pattern ships all windows have the same shape, so the three agree. work_unit_bits is 8, one byte, so the effective absolute bound under min_ir_per_work is 0.001953125 x 8 = 0.015625. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged, and the argument is p13-specific: the OUTER fold is a serial Horner chain, `acc = acc*31 + x` DST_CAP+1 times per string since TASK_046's full-extent fold, so string i+1's multiply depends on string i's and there is no vector form at any -march -- unlike the COPY and the FILL, which rustc turns into `memcpy` and `memset` in every Rust rung including the ones whose source is a byte loop (../NOTES.md 3d). That is exactly why the unit is not denominated over the copy and the fill alone. The two probe inputs differ in work_per_call (520 vs 1321) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all -- and they differ in the RIGHT DIRECTION, which the `stride` denomination did not."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost, on the first kernel in this project whose obligation is discharged by a fact about the CONTENTS of the array being indexed rather than by a guard on the index. The byte-identity result now covers a kernel with SIX loops, five of them carrying relational invariants, one of them an UNBOUNDED scan whose only bound is a loop invariant, six recursive spec functions and ZERO nonlinear arithmetic. At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."
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
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. On p13 there is a second and stronger reason than on any earlier pattern: the pattern's whole obligation is an UNBOUNDED read loop, so an off-by-one anywhere in the sentinel argument is a genuine out-of-bounds access and not a wrong answer, and Miri on R4 is the only oracle that re-runs the real memory model over the real accessor bodies. A trusted `dst_set_unchecked` that wrote `i + 1` as well would satisfy this `ensures` on slot `i` and be invisible everywhere else -- and on p13 it would also silently move the sentinel. Cost: check.py rewrites n_iters to 4, so each row scans, copies, fills and consumes at most 4 x (stride + 34 x nstr) bytes -- about 3400 on small and 2400 on large, four orders of magnitude inside `.memory`'s measured 3.05 M budget. The only real cost is the 7.5 MB payload to_vec, and p07's 12 MB one passes.",
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
reason: p13's payload names no allocation size, and the destination is a
fixed-size local in every rung, so p02's `SLB_MAX_CAP` check would be dead code.

**These are the CHECKED rungs' exit codes, and on p13 R1's are the same.**
Unlike p12, whose overflow magnitude decides between a silent wrong answer, a
canary abort and a SIGSEGV, p13's overread is 1–7 bytes into the kernel's own
frame on every build measured, so **R1 exits 0 with a wrong answer on every
truncating row under both compilers**. `harness/check.py` records that in its
adversarial table rather than requiring it; `NOTES.md` 0 and 7 are where it is
read.

## Degenerate shapes

`stride_w >= 4 && stride_w <= n_blob` is the driver's whole input validation. A
stride below 4 cannot hold the header (`adversarial-stride3.bin`); a stride above
`n_blob` leaves no whole window, so `nwin` would be 0 and `k` would have nothing
to index. Either way the loop is skipped and the driver prints `0` after **zero**
kernel calls.

`adversarial-exact.bin` is the boundary from the safe side: four strings of
exactly `DST_CAP - 1` = 31 bytes, the zero-fill writes `dst[31] = 0`, nothing is
lost, every rung agrees and the sanitizer is clean. `adversarial-truncate.bin`
is the **same four strings plus one byte each** — one byte over — and it is the
sharpest row in the pattern: every checked rung prints the checksum
`adversarial-exact.bin` printed, having silently dropped one content byte per
string, while R1's consumer walks off `dst`.

`adversarial-empty.bin` is the degenerate copy: `nstr == 8` and eight zero bytes,
so every string is empty, `n` is 0, the zero-fill writes all 32 bytes, `d` is 0
and every folded byte is 0. It is the row where the per-string constant is measured with
the source terms set to zero, and it returns exactly `nstr == 8`.

The kernel's `len < 4` guard is, given the driver's `stride_w >= 4`, unreachable
in this benchmark. It is kept anyway so the kernel is **total** and its
`requires` stays purely structural; the alternative — a `len >= 4` precondition —
would be a precondition about the driver's own guard rather than about the
buffer.
