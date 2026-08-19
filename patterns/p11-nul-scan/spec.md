# p11 — NUL-terminated string scan: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, and C spells the pair
out. C is handed the blob length and R1 ignores it, so R1-vs-R1h is a comparison
with the calling convention, the argument count and the register allocation all
held fixed. The only difference between those two cells is one expression.

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     nstr      u32 LE    DECLARED string count    ATTACKER DATA
byte 4..      packed, NUL-terminated strings
data_start = 4 ;  avail = len - 4                 what ACTUALLY arrived
```

**Termination is a property of the file, not of the kernel.** No rung checks
that a terminator is present, no rung checks that `nstr` is honest, and — the
part that matters — *the specification does not assume either*. See "What the
`ensures` is, and what it is not".

## Semantics

```
if len < 4:                                   return 0
nstr from the header
if nstr == 0:                                 return 0     # present in EVERY rung

acc = 0                                                    # u64
p   = 4
for s in 0 .. nstr:
    # >>> THE SCAN. R1 omits the bound `q < len` and nothing else. <<<
    q = p
    while q < len and buf[off + q] != 0:
        q += 1
    slen = q - p
    h = 0                                                  # u64
    for i in p .. q:
        h = h *64 31 +64 buf[off + i]
    acc = acc *64 31 +64 (h ^ slen)
    if q >= len:   break                       # no terminator: last string
    p = q + 1
    if p >= len:   break
return acc *64 31 +64 nstr
```

`*64`/`+64` are wrapping, as in p01/p02/p16/p17/p05/p07, so the kernel has **no
precondition on values** and every measured input is inside the verified domain
by construction. C's unsigned types wrap by definition (6.2.5p9) and the Rust
rungs write `wrapping_add`/`wrapping_mul`.

### The loop bound is not known before the loop, and that is the design

p16's trip count is data-dependent but *read from a header*; p07's is
`ceil(log2 n)`; p01, p02, p05, p08 and p17 are all lengths. **A NUL scan has no
bound at all** — it runs until it finds a sentinel that may not be there. Two
consequences the earlier patterns could not produce:

- **Safe Rust cannot express the C loop.** `strlen` is bounded by the sentinel
  and by nothing else; every safe spelling of it is bounded by *something* —
  either a per-byte bounds check, or an idiom (`iter().position`,
  `CStr::from_bytes_until_nul`) that carries the bound implicitly in a slice.
  R2 is the first, R3 the second, and NOTES.md 3 measures the gap between them.
- **The proof needs a termination measure that the C does not have.**
  `scan_end` in `verus.rs` is `if q >= len { len } else if buf[off+q] == 0 { q }
  else { scan_end(q+1) }`; delete the first arm and it is R1's scan *and* a
  recursion with no `decreases`. NOTES.md 5.

### The scan and the fold are two loops, and that is `idiom.required`

Fusing them — `while (b != 0) h = h*31 + b;` — deletes the pattern: `slen` would
never exist as a value, `h ^ slen` could not be the fold, and the
`strlen`/`memchr`/`from_bytes_until_nul` idiom that R1, R1h and R3 each reach in
their own library would be foreclosed in all three.

**That the split survives `-O3` is measured and not assumed** (NOTES.md 1).
`harness/asm.py`'s `backward_branches` counts 2 loops in `c-gcc` — its scan is a
`call strlen@plt`, so only the outer walk and the fold have back edges — 3 in
`c-clang`, 4 in `c-gcc-h`, 3 in `c-clang-h`, 3 in `safe_naive`, 3 in
`safe_tuned` and 5 in `unsafe`, against a deliberately **fused** control at 2
whose fold sits inside its scan. Nothing fuses in any rung.

### Load-bearing, do not "improve"

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug. Edit both or neither — TASK_016 *duplicated* this
section into p05's block rather than moving it, and one bullet was already
missing from the copy on the day it landed.

- **The scan and the fold are separate loops and `slen` is materialised between
  them.** Above.
- **`slen` is folded into the string's value as `h ^ slen`**, so a rung that
  folds the same bytes but finds a *different terminator* cannot produce the
  same checksum, and **`nstr` is folded**, so a rung that walks a different
  number of strings cannot either.
- **The cursor steps past the terminator: `p = q + 1`, and the walk stops on
  `p >= len`.** The declared count is *not* a loop bound in any rung — see the
  next section.
- **A string whose terminator is missing is the last string in the window:
  `if q >= len: break`.** Required rather than conventional, and for a reason
  that is measured: without it the cursor step is `p = q + 1` with `q` possibly
  `len`, which **cannot be proved overflow-free** at the pinned vstd (no axiom
  that a slice is at most `isize::MAX` bytes; `usize` modelled as possibly
  32-bit). p17 bought its way out of the analogous obligation with a second
  `requires` and a third driver conjunct; this line costs neither. NOTES.md 5.
- **The little-endian header decode is written out** — `b0 + 256*b1 + 65536*b2 +
  16777216*b3` — in every rung, and `from_le_bytes` is `forbidden`. Two reasons,
  and the second decides it: it would delete the decode every rung shares, and
  it **cannot be an R4/R5 spelling at the pinned vstd** (`from_le_bytes`,
  `TryFromSliceError` and `from_raw_parts` are all `is not supported`,
  TASK_027_REVIEW), so a rung using it would compare a safe cell against an
  unsafe cell that cannot exist. `.memory/01-ladder.md`: a rung covered by an
  `identity` pin is chained to the prover.
- **The scan itself is deliberately NOT pinned**, and that is the point of the
  pattern. R1 spells it `strlen`, R1h `memchr`, R2/R4/R5 an indexed byte loop
  and R3 `CStr::from_bytes_until_nul`; holding those fixed would hold fixed the
  one thing p11 exists to compare. What *is* pinned is that the scan is bounded
  by the **window** in five of the six rungs and by the **sentinel** in the
  sixth, which is the bug.

### The declared count bounds nothing, and one input proves it

`nstr` is attacker data and it appears in no loop bound in any rung. What stops
the walk is the terminator (inner loop) and `p >= len` / `q >= len` (outer
loop). Three adversarial inputs separate the two quantities:

| input | header | tail bytes | R1 | every other rung |
|---|---|---|---|---|
| `adversarial-nonul` | **honest** (6 strings, 6 written) | last string unterminated | **overruns** | stops at the window end |
| `adversarial-count` | 4096 declared, 3 written | non-zero, unterminated | **overruns** | stops at the window end |
| `adversarial-zerotail` | 4096 declared, 3 written | **NUL** | fine | fine — 23 strings walked, 4073 short of the count, no error anywhere |

`count` and `zerotail` are the **same header lie** and differ only in the tail
bytes, which is what makes "the sentinel, not the count, is the bound" a
measurement rather than a remark. NOTES.md 7.

### What p11 is *not*: a wrong index, a wrong length, or an unbounded walk

p16's missing check made `end - p` underflow so the *walk* never terminated;
p17's let a signed index go negative so the read ran backwards; p07's underflows
an inclusive bound and jumps `2*n` bytes out; p05's is a nonlinear product.
**Here nothing is computed wrongly at all.** Every index is correct, every
subtraction is safe, every quantity is unsigned — the scan simply does not stop.
And unlike p16, R1 keeps the *outer* bound (`p >= len`), so it overruns **at
most once per call**: the string with no terminator. NOTES.md 7 records what
that did to the sanitiser row.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == nul_scan_fold(buf, off, len)
```

`nul_scan_fold` is the spec function; `model.py` is its independent Python twin.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included, and `harness/check.py` evaluates it at every one of the
kernel calls to prove that it does. `nstr`, all 2^32 values of it, and every byte
of the window are *arguments* of the problem; the kernel is total in all of them.

**It is ONE clause, and p17's second one is deliberately absent.** p17 needed
`buf_len <= 9223372036854775807` because it cast to `i64`; p11 needs the same
fact for a different reason — the cursor step `p = q + 1` with `q` possibly
`len` — and gets it for free from the `if q >= len: break` line above instead of
paying for it with a precondition and a driver conjunct. Reported in NOTES.md 5,
because "the spelling that makes the proof go through is the one that names the
bug" is p07's finding arriving on a completely different kernel.

### What the `ensures` is, and what it is not — p11 is p16's case, not p17's

p16's `spec.md` says, correctly for p16, that a read-only kernel's `ensures`
cannot be its security property, because "no byte outside the window was read"
is not a property of the return value; the trusted accessor's discharged
`requires i < v@.len()` is what carries the safety claim. **p11 is that case.**
Its harm is an ordinary out-of-bounds read, so the accessor precondition is
exactly what excludes it.

**And there is a second thing the `ensures` deliberately does not say: that the
declared count is honest, that the strings are terminated, or that the window
ends on a terminator.** `str_walk` in `verus.rs` specifies what the *program*
walks — stop at the first zero byte or at the window end, whichever comes first
— so `adversarial-count.bin` and `adversarial-zerotail.bin` are inside the
verified domain and every checked rung agrees with `model.py` on both. Writing
the stronger postcondition would have forced a `requires` about the contents of
a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it
would have deleted the two rows that show the count is not a bound.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p11's payload is p16's, p17's, p05's and p07's:

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes` — the functions p16 added to `common/`, reused verbatim,
with **nothing added to `common/` for p11**. All three are a bulk copy rather
than an element-by-element decode, which is what keeps every p11 row
Miri-checkable (`.memory/02-bench-rules.md`: `head_u64_body`'s per-element loop
is why p01's `large.bin` blocks).

Nothing is a compile-time constant: `n_iters`, `stride`, `n_blob`, every `nstr`,
every string length and every byte come from the file.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here and are
deliberately not copied across, exactly as for p16, p17, p05 and p07.

## Driver loop

Identical in all six rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` normalises every copy — the C one included — and
diffs it against `driver.canonical` below.

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

One difference from p07's: **`stride_w >= 4`** rather than `>= 8`, because p11's
window header is the 4-byte `nstr` field rather than the 8-byte `n`/`nq` pair.
`adversarial-stride3.bin` attacks it.

The comparison is in `u64` *before* the `as usize` cast, so a truncating driver
cannot sneak a 2^40 stride past it. (Unchanged from p16, p17, p05 and p07, and
still load-bearing.)

### Why this does not evaporate

Same mechanism as p01, p02, p16, p17, p05 and p07: `k` is derived from `acc`,
and `acc` from the previous call's result, so call *i+1* cannot begin until call
*i* has returned. Nothing to CSE, nothing to hoist, no `black_box` and no
`asm volatile` — the same arithmetic in both languages, so neither gets a
stronger barrier than the other. `k = (acc * nwin) >> 64` is Lemire's map onto
`[0, nwin)`; see p01's `spec.md` for why it is a multiply-shift and not a
modulo.

### Why every adversarial input is exactly one window

`k` is pseudo-random over `[0, nwin)`, so with several windows a malformed one
would be hit only probabilistically — and, worse here than anywhere, **a scan
that runs out of a *middle* window lands in the next window and stays inside the
allocation**, which is a silent wrong answer with no ASan and a gate that passes
by luck. With `nwin == 1`, `k` is always 0 and `off` is always 0, so
`adversarial-nonul`'s and `adversarial-count`'s overruns leave the allocation
deterministically.

The related trap, from p17 and non-obvious: **window 0 must serve something**,
because a window returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is
then 0 for ever — the driver's Lemire index has an absorbing state at
`acc == 0`. Here no window *can* return 0: the return is `acc*31 + nstr` and the
kernel has already rejected `nstr == 0`. `inputs/gen.py` records both
constraints.

### The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(buf, n_blob, k * stride, stride)` and the Rust loop
calls `kernel(buf, k * stride, stride)`. `driver.aliases` cannot reconcile that
— both sides of an alias are a dotted identifier path, so an alias renames and
can do nothing else. `driver.call_args` declares which argument *positions* of a
named call are the canonical ones (`{"c": {"kernel": [0, 2, 3]}}`), and
`harness/dloop.py` refuses to drop anything that is not a single bare
identifier, so no prefetch, no side effect and no extra statement can hide in
the argument the diff stops looking at.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes;
what is worth saying here is the arithmetic behind the two obligation counts,
because a declared number a reviewer cannot check from `spec.md` alone is
exactly what `.memory/02-bench-rules.md` forbids.

| pin | why |
|---|---|
| `verus.obligations` = 12 | **`scan_end` 1 + `fold_str` 1 + `str_walk` 1 + `kernel` 4 + `main` 5 = 12.** Every term is checkable with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained, and the zero terms are checkable the same way: `u32_at`, `nstr_at` and `nul_scan_fold` are non-recursive spec fns and report **0**; the three `external_body` items report **0**; the three *recursive* spec fns carry one termination query each. `kernel`'s 4 is 1 body + 1 per loop body (**three** loops), and that is p11's contrast with p07's 3 and p05's 5: p11 has one more loop than p07 because the idiom requires the scan and the fold to be separate, and two fewer `by (nonlinear_arith)` sub-proofs than p05 because every multiplication in this kernel is by a literal. **`main`'s 5 does not decompose further from the command line and is quoted as measured**: the by-block rule of thumb would predict 6 and Verus reports 5, the identical off-by-one p05's, p17's and p07's `spec.md` record for the identical driver. `.memory/04-verus.md`'s one-query-per-function-plus-one-per-loop rule gives **9** here and is therefore not the derivation. |
| `verus.twin_obligations` = 13 | the count in the **other** configuration, `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. **12 shipped + 1**, and the 1 is measured the same way: `--cfg slb_twin --verify-function slb_twin_get_unchecked --verify-root` reports `1 verified` — one function, no loop body, no `by`-block. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`. Since TASK_010 that no longer makes Miri optional: it is mandatory for any pattern with a trusted item, because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`. `check.py` derives this from `verus.rs` rather than reading the flag. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == nul_scan_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (nul_scan_fold). p11 is p16's, p05's and p07's shape and NOT p17's: the harm is an ordinary read outside the buffer -- a scan looking for a sentinel that is not there -- so the trusted accessor's discharged `i < v@.len()` is the security property and the `ensures` is what keeps the proof non-vacuous and pins WHICH bytes the answer is a function of. There is no 'inside the buffer but outside the window' band here for the ensures to be the only guard against: every checked rung stops the scan at `q == len`. **What the `ensures` deliberately does NOT say is that `nstr` is honest, that the strings are terminated, or that the window ends on a terminator.** `str_walk` specifies what the PROGRAM walks -- stop at the first zero byte or at the window end, whichever comes first -- so adversarial-count.bin and adversarial-zerotail.bin, whose headers both declare 4096 strings against three written, are INSIDE the verified domain and every checked rung agrees with model.py on both. A `requires` that the count is honest would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete the two rows that show the count is not a bound.",
  "idiom": {
    "required": [
      {
        "c": "the scan and the fold are SEPARATE loops and the length is materialised between them: `slen = q - p;` in both C rungs.",
        "rust": "the scan and the fold are SEPARATE loops and the length is materialised between them: `let slen: usize = q - p;` in all four Rust rungs."
      },
      {
        "c": "the fold is byte-at-a-time Horner over the measured span, spelled with the literal multiplier: `h = h * 31 + (uint64_t)buf[off + i];` in both C rungs.",
        "rust": "the fold is byte-at-a-time Horner over the measured span, spelled with the literal multiplier: `.wrapping_mul(31).wrapping_add(` in all four Rust rungs. safe_tuned.rs spells the LOOP as `.iter().fold(`, which is why only the operation and not the loop form is pinned here."
      },
      {
        "c": "the measured length is folded into the string's value, so a rung that folds the same bytes but finds a different terminator cannot produce the same checksum: `(h ^ (uint64_t)slen)` in both C rungs.",
        "rust": "the measured length is folded into the string's value, so a rung that folds the same bytes but finds a different terminator cannot produce the same checksum: `h ^ (slen as u64)` in all four Rust rungs."
      },
      {
        "c": "the walk starts at the first byte after the header: `p = 4;` in both C rungs.",
        "rust": "the walk starts at the first byte after the header: `let mut p: usize = 4;` in all four Rust rungs."
      },
      {
        "c": "a string whose terminator is missing is the last string in the window: `if (q >= len)` in both C rungs.",
        "rust": "a string whose terminator is missing is the last string in the window: `if q >= len {` in all four Rust rungs. This line is also what makes `p = q + 1` provably overflow-free -- see verus.rs's header comment -- so it is required rather than conventional."
      },
      {
        "c": "the cursor steps PAST the terminator: `p = q + 1;` in both C rungs.",
        "rust": "the cursor steps PAST the terminator: `p = q + 1;` in all four Rust rungs."
      },
      {
        "c": "the walk is bounded by the WINDOW and never by the declared count: `if (p >= len)` in both C rungs. `nstr` appears in no loop bound in any rung.",
        "rust": "the walk is bounded by the WINDOW and never by the declared count: `if p >= len {` in all four Rust rungs. `nstr` appears in no loop bound in any rung."
      },
      {
        "c": "the SCAN is bounded by the window in the hardened cell: `memchr(buf + off + p, 0, len - p)` in c/kernel_hardened.c. c/kernel.c bounds it by the SENTINEL instead (`strlen`) and that one expression is the whole difference, which IS the bug -- so the one scoped-absent audit pair this declaration reports is on that rung and is correct.",
        "rust": "the SCAN is bounded by the window: `while q < len` in safe_naive.rs, unsafe.rs and verus.rs. safe_tuned.rs bounds it by handing `CStr::from_bytes_until_nul` a reslice `&w[p..]` of known length, which is the same bound expressed by the type rather than by a comparison, and is why this entry's Rust spelling scopes to three rungs and not four."
      },
      "the little-endian u32 header decode is written out with + and * rather than | and <<, so it stays linear arithmetic: `+ 65536 *` in all six rungs.",
      "...and its top byte: `+ 16777216 *` in all six rungs.",
      {
        "c": "the declared count is folded, so a rung that walks a different number of strings cannot produce the same checksum either: `acc * 31 + (uint64_t)nstr` in both C rungs.",
        "rust": "the declared count is folded, so a rung that walks a different number of strings cannot produce the same checksum either: `.wrapping_add(nstr as u64)` in all four Rust rungs."
      }
    ],
    "forbidden": [
      "`chunks_exact`",
      "`from_le_bytes`",
      "`split`",
      "`strtok`"
    ],
    "why": "each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). THE SCAN AND THE FOLD ARE TWO LOOPS AND `slen` IS MATERIALISED BETWEEN THEM: fusing them (`while (b != 0) h = h*31 + b;`) deletes the pattern outright -- the length would never exist as a value, `h ^ slen` could not be the fold, and the `strlen`/`memchr`/`from_bytes_until_nul` idiom that R1, R1h and R3 each reach in their own library would be foreclosed in all three. That the split SURVIVES -O3 is measured rather than assumed (NOTES.md 1): `asm.backward_branches` counts 2 loops in c-gcc (its scan is a `call strlen@plt`), 3 in c-clang, 4 in c-gcc-h, 3 in c-clang-h, 3 in safe_naive, 3 in safe_tuned and 5 in unsafe, against a deliberately fused control at 2 with its fold inside its scan. `chunks_exact` is forbidden for the fold because p16 measured that the chunk width moves that pattern's per-byte rate over a 31% range (5.04688...6.62500, `.memory/01-ladder.md`), and p11's whole published quantity is a decomposition into a per-scanned-byte rate and a per-folded-byte rate -- a chunked fold would move one of the two axes by more than the difference being reported. `from_le_bytes` deletes the written-out little-endian header decode every rung shares AND is NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW), so a rung using it would compare a safe cell against an unsafe cell that cannot exist -- the `identity`-pin trap this block's own `identity` key sets. `split` and `strtok` delete the explicit cursor `p = q + 1`, and with it the behaviour `adversarial-zerotail.bin` exists to show, namely that the walk is bounded by the terminator and by `p >= len` and never by `nstr`. WHAT IS DELIBERATELY *NOT* PINNED, and it is the point of the pattern: **the scan itself**. R1 spells it `strlen`, R1h `memchr`, R2/R4/R5 an indexed byte loop and R3 `CStr::from_bytes_until_nul`, and holding those fixed would be holding fixed the one thing p11 exists to compare. What is pinned instead is that the scan is BOUNDED BY THE WINDOW in five of the six rungs and by the sentinel in the sixth, which is the bug. The declaration was written BEFORE any cell was measured -- the R5 proof and the checksums existed, no `Ir` and no `ns` did -- which is the one thing TASK_018's standard cannot retrofit onto p01, p02, p05, p08, p16 or p17. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither."
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
    "obligations_note": "12 = scan_end 1 + fold_str 1 + str_walk 1 + kernel 4 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`. u32_at, nstr_at and nul_scan_fold are NON-RECURSIVE spec fns and carry 0; get_unchecked, load_input and emit are external_body and carry 0; scan_end, fold_str and str_walk are RECURSIVE and carry one termination query each. kernel's 4 = body + 3 loop bodies, and the THREE loops are p11's contrast with p07 (two) and p05 (two plus two `by (nonlinear_arith)` sub-proofs): the scan, the fold and the string walk are separate loops because ../spec.md's idiom requires them to be, and every multiplication in this kernel is by a literal so Z3 takes all the index arithmetic for free. main's 5 is quoted AS MEASURED and does not decompose from the command line: body + driver loop + one per by-block would predict 6 and Verus reports 5 -- the identical off-by-one p05's, p17's and p07's spec.md record for the identical driver. `.memory/04-verus.md`'s one-per-function-plus-one-per-loop rule of thumb gives 9 here and is therefore not the derivation.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. 12 shipped + 1, and the 1 is measured: `--cfg slb_twin --verify-function slb_twin_get_unchecked --verify-root` reports `1 verified` -- one function, no loop body, no `by`-block. Pinned for the same reason the shipped count is: `tv > base_v` only says something extra compiled, and a twin that quietly lost its body, or an item that exists only under the cfg, moves this number and nothing else.",
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
        "scan_end": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold_str": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "str_walk": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "nul_scan_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_get_unchecked": {
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
            "r == nul_scan_fold(buf@, off as int, len as int)"
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
    "note": "work_per_call is **bytes of the window** -- `stride`, 1192 on small and 4145 on large -- and p11 is back to p16's and p05's denomination after p07 had to leave it (p07 counts PROBES, because a binary search reads 0.63% of its window). Every byte of a well-formed p11 window is scanned once and every non-terminator byte is folded once, so the kernel visits the window's bytes about twice. WHICH WAY THE ESTIMATE ERRS: STRICT, and by two corrections that pull opposite ways and do not cancel evenly -- `stride` OVER-counts by the 4 header bytes and by one terminator per string (12.6% of small, 1.0% of large, neither folded) and UNDER-counts by the whole second pass, which is the larger term on both inputs. So `stride` is at most the number of byte-visits and the derived floor is one the kernel must clear; it can never let a collapsed kernel through, which is the only direction that matters. work_unit_bits is 8, one window byte, so the effective absolute bound under min_ir_per_work is 0.001953125 x 8 = 0.015625. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged, and the argument is p11-specific: the FOLD is a serial Horner chain `h = h*31 + b`, so byte i+1's multiply depends on byte i's and there is no vector form at any -march -- unlike p02's copy, which is why p02 had to declare 0.0625. The SCAN alone does go below 0.25 (glibc's AVX2 strlen measures 0.078125 Ir/byte, NOTES.md 2), which is exactly why the unit is denominated over the whole window and not over the scan. The two probe inputs differ in work_per_call (1192 vs 4145) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost, on the first kernel in this project whose loop bound is not known before the loop -- the scan stops at a sentinel that may not be there, so there is no closed form for where it stops and the invariant has to be relational (`scan_end(q) == scan_end(p)`). The byte-identity result now covers a kernel with THREE nested loops, two of them carrying `invariant_except_break` plus a loop `ensures`, three recursive spec functions and ZERO nonlinear arithmetic. At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."
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
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. On p11 there is a second reason worth stating: the unchecked index is `off + q` where `q` is where a SCAN stopped, i.e. a function of the data rather than of the header, so an off-by-one in the scan bound would show up on some strings and not others rather than as a fixed shift the way p16's and p17's would. Cost: check.py rewrites n_iters to 4, so each row scans and folds 4 x stride bytes -- 9536 on small and 33 160 on large, ~100x inside `.memory/02-bench-rules.md`'s measured 3.05 M budget. The only real cost is the 8 MB payload to_vec, and p07's 12 MB one passes.",
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

There is no exit 7 here, for p16's, p17's, p05's and p07's reason: p11's payload
names no allocation size, so p02's `SLB_MAX_CAP` check would be dead code.

## Degenerate shapes

`stride_w >= 4 && stride_w <= n_blob` is the driver's whole input validation. A
stride below 4 cannot hold the header (`adversarial-stride3.bin`); a stride above
`n_blob` leaves no whole window, so `nwin` would be 0 and `k` would have nothing
to index. Either way the loop is skipped and the driver prints `0` after **zero**
kernel calls.

A window whose last string has no terminator (`adversarial-nonul.bin`,
`adversarial-count.bin`) is different and the difference is deliberate: there the
calls *do* happen, and the **kernel** is what either stops or does not — the
seven checked cells stop the scan at `q == len` and agree with `model.py`, while
the two R1 cells scan out of the allocation. They differ in *why*: `nonul`'s
header is honest and its last declared string is malformed; `count`'s header
declares 4096 strings against three written, so R1 walks into filler that was
never a string at all.

`adversarial-zerotail.bin` is the control for `count`, and it is the sharpest row
here: **the same header lie with a NUL tail**, on which every cell including R1
stays in bounds, walks 23 strings, and returns the model's answer. Between the
two, the declared count is held fixed and only the tail bytes move — which is
what makes "the sentinel is the bound and the count is not" a measurement.

`adversarial-empty.bin` is the degenerate scan: `nstr == 8` and eight zero bytes,
so every string is empty, `h` and `slen` are both 0, and every cell returns
exactly `nstr`. It is the row where the per-string constant is measured with the
per-byte term set to zero.

The kernel's `len < 4` guard is, given the driver's `stride_w >= 4`, unreachable
in this benchmark. It is kept anyway so the kernel is **total** and its
`requires` stays purely structural; the alternative — a `len >= 4` precondition
— would be a precondition about the driver's own guard rather than about the
buffer. NOTES.md 9 records that it is dead and why it stays.
