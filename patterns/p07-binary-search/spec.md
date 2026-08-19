# p07 — binary search: the kernel contract

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
held fixed. The only difference between those two cells is one `if`.

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     n         u32 LE    DECLARED element count   ATTACKER DATA
byte 4..8     nq        u32 LE    DECLARED query count     ATTACKER DATA
byte 8..      elements  u32 LE x n     -- SORTED ASCENDING
byte 8+4n..   queries   u32 LE x nq
data_start = 8 ;  avail = len - 8                what ACTUALLY arrived
```

**Sortedness is a property of the file, not of the kernel.** No rung sorts
anything, no rung checks it, and — the part that matters — *the specification
does not assume it*. See "What the `ensures` is, and what it is not".

## Semantics

```
if len < 8:                                   return 0
n, nq from the header
if n == 0 || nq == 0:                         return 0     # present in EVERY rung

# >>> THE CHECK. R1 omits exactly this line and nothing else. <<<
if 4*n + 4*nq > avail:                        return 0     # computed in u64/size_t

acc = 0                                                    # u64
for q in 0 .. nq:
    key   = load_u32(data_start + 4*n + 4*q)
    lo    = 0 ;  hi = n                                    # HALF-OPEN
    found = 0xffff_ffff_ffff_ffff                          # u64, "not found"
    while lo < hi:
        mid = lo + (hi - lo)/2                             # the safe midpoint
        v   = load_u32(data_start + 4*mid)
        if v == key:   found = mid ; break
        if v <  key:   lo = mid + 1
        else:          hi = mid
    acc = acc *64 31 +64 (found +64 1)
return acc *64 31 +64 (n *64 nq)
```

`*64`/`+64` are wrapping, as in p01/p02/p16/p17/p05, so the kernel has **no
precondition on values** and every measured input is inside the verified domain
by construction. C's unsigned types wrap by definition (6.2.5p9) and the Rust
rungs write `wrapping_add`/`wrapping_mul`. `found + 1` with
`found == u64::MAX` is 0, which is how "not found" folds.

### The search is a jump, not a fold, and that is the whole design

Every kernel this project has measured is a linear fold: p01, p02, p05, p08,
p16 and p17 are all `for each byte: acc = f(acc, b)`. A per-call safety constant
divided by `n` bytes goes to zero, which is *why* "safety is cheap" keeps coming
out. Binary search has `ceil(log2 n)` probes per query and **no inner loop at
all**, so a per-probe bounds check is a large *fraction* of the kernel rather
than a vanishing constant, and it is the first pattern where R3's cost cannot be
amortised away by making the input bigger. `NOTES.md` §3 states p07's answer as
a function of `n` and says whether it goes to zero, to a constant, or grows.

It is also the canonical unpredictable-branch kernel. This box has
`perf_event_paranoid = 3` and therefore no branch-miss counter
(`.memory/00-environment.md`), which makes a **branchless control mandatory
rather than optional** — `NOTES.md` §11 builds the `cmov` variant, confirms
`cmov` in the disassembly rather than assuming it, and says exactly what the
inference rests on.

### Load-bearing, do not "improve"

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug. Edit both or neither — TASK_016 *duplicated* this
section into p05's block rather than moving it, and one bullet was already
missing from the copy on the day it landed.

- **`mid = lo + (hi - lo)/2`, spelled exactly that way in every rung.** It is
  the overflow-safe midpoint; `(lo + hi)/2` is the `forbidden` spelling and it
  is the bug `.memory/06-catalogue.md` claims for p07. Pinning it means the
  midpoint question is settled by `grep`. See the next section for why the
  catalogue's claim is wrong.
- **The bounds are HALF-OPEN: `hi = n`, `while lo < hi`, `hi = mid`.** Not the
  textbook `hi = n - 1` / `while lo <= hi` / `hi = mid - 1`. This is `required`,
  not conventional, and the reason is measured rather than stylistic — see "The
  inclusive spelling is not an admissible respelling" below.
- **The length check is `4*n + 4*nq > avail` in 64-bit.** The width is half the
  pattern and it is **not p05's width**: `n` and `nq` are u32 fields, so the
  left-hand side reaches `4*(2^32-1)*2 = 34 359 738 360` and does **not** fit
  `uint32_t`. p05's `nrow*ncol` comes from u16 fields, tops out at
  4 294 836 225, and still fits `uint32_t` — so on p05 only the *signed* 32-bit
  spelling breaks, and on p07 the *unsigned* one breaks too.
  `adversarial-width.bin` is the input and `NOTES.md` §6 builds the narrow cell.
- **The little-endian decode is written out** — `b0 + 256*b1 + 65536*b2 +
  16777216*b3` — in every rung, and `from_le_bytes` is `forbidden`. Two reasons,
  and the second decides it: it would delete the decode every rung shares, and
  it **cannot be an R4/R5 spelling at the pinned vstd** (`from_le_bytes`,
  `TryFromSliceError` and `from_raw_parts` are all `is not supported`,
  TASK_027_REVIEW), so a rung using it would compare a safe cell against an
  unsafe cell that cannot exist. `.memory/01-ladder.md`: a rung covered by an
  `identity` pin is chained to the prover.
- **`found + 1` is folded**, so a rung that returns a different index cannot
  produce the same checksum, and **`n * nq` is folded**, so a rung that runs a
  different number of searches cannot either.
- **R3 may reslice `[ep .. ep + 4]`** with `ep = off + 8 + 4*mid` — that moves
  the *check* and keeps the *index*, and it is the most a rung may do. p05's
  `required[1]` is the same rule one dimension up.

### The catalogue's bug is unreachable, and the arithmetic is short

`.memory/06-catalogue.md` lists p07's bug as midpoint overflow `(lo+hi)/2`.
**It is not reachable at any size this wire format can express**, and RAM is not
the binding constraint — the header field width is:

```
n is a u32 field           ->  n <= 2^32 - 1
lo <= hi <= n - 1          ->  lo + hi <= 2*(2^32 - 2) = 8 589 934 588
2^64                       =                 18 446 744 073 709 551 616
                                             ------------------------
                                             2 147 483 649x short
```

and the length check forbids declaring an `n` whose elements are not present, so
the count cannot be inflated past what the file carries. The cheapest index type
that *could* wrap is `int` — the historical JDK/Bentley bug — and it needs
> 2^30 elements, i.e. **4 GiB of u32 data**, which cannot be a benchmark input
here: the gate builds 32 cells and runs every one of them on every input under
callgrind (~100x) and Miri (~1000x). `uint32_t` needs 8 GiB. `NOTES.md` §0 has
the table and the probe that produced it.

**The overflow that IS reachable in this kernel is in the other
multiplication** — the length check, at a window of 88 bytes. That is the same
CWE-190-feeding-CWE-125 the catalogue meant, on the multiplication that is
actually reachable, and it is what `adversarial-width.bin` and `NOTES.md` §6
demonstrate.

### The inclusive spelling is not an admissible respelling

The textbook form

```
lo = 0 ; hi = n - 1
while lo <= hi:
    mid = lo + (hi - lo)/2
    if v <  key: lo = mid + 1
    else:        hi = mid - 1        # <-- underflows at mid == 0
```

has an unsigned underflow that fires on **well-formed input**. `mid == 0`
requires only `lo == 0 && hi <= 1`, so any key below `elements[0]` sets
`hi = SIZE_MAX` and the next probe is at index `2^63 - 1`. That is half of an
ordinary miss workload, not an attack. Built as a p07 rung it would make C
SIGSEGV and safe Rust panic on `small.bin`, so no checksum could agree, and
`sanitizer_expect` for `small`/`large` could not be `"clean"`.

So it is excluded by `idiom.required` rather than measured as a spelling. It is
still *built* — `NOTES.md` §6 derives it from `c/kernel.c` by exact-string
substitution with an asserted hit count (`.memory/05-layout.md` item 11's shape)
and records what it does on `small.bin` and on `adversarial-zero.bin`.

### The zero guard is dead here, and that is the result

`if n == 0 || nq == 0: return 0` is kept in every rung, R1 included — and in the
half-open spelling it is **completely dead**. With `n == 0` the bounds are
`lo = 0, hi = 0`, the loop does not run, every query folds `NOT_FOUND + 1 == 0`,
and `n*nq == 0`, so the guard's answer and the loop's answer agree. Unlike
p05's, it is not even a *work* guard: `nq` is bounded by `avail/4`, so a window
cannot declare unbounded work.

It is kept because its deadness is exactly the finding. In the *inclusive*
spelling the same line is the only thing between `n == 0` and `hi = SIZE_MAX`;
in the half-open spelling it is decoration. **The loop-bound spelling, not the
guard, is what makes `n == 0` safe** — and `adversarial-zero.bin` is the input
that shows both halves of that sentence at once (`NOTES.md` §6).

### What p07 is *not*: an unbounded walk, a signed underflow, or a sequential overrun

p16's missing check made `end - p` underflow so the walk never terminated;
p17's let a signed index go negative so the read ran *backwards*; p05's and
p16's overruns are **forward and sequential**, first byte one past the end.
None of those happens here. Every loop in p07 has a bound that strictly
decreases (`nq - q`, then `hi - lo`), every quantity is unsigned, nothing
subtracts anything that can underflow, and the read that leaves the buffer is a
**single wild jump**: R1's first out-of-bounds access is `2*n` bytes past the
window with nothing touched in between. `NOTES.md` §7 records whether that made
it easier for a sanitiser to catch than p02's one-byte overflow — p02's whole
result is that a small overrun usually goes unnoticed.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == search_fold(buf, off, len)
```

`search_fold` is the spec function; `model.py` is its independent Python twin.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included, and `harness/check.py` evaluates it at every one of
the kernel calls to prove that it does. `n`, `nq`, every element and every query
value are *arguments* of the problem; the kernel is total in all of them.

**p17's second clause is deliberately not carried forward.** p17 needed
`buf_len <= 9223372036854775807` because it cast to `i64` and vstd has no axiom
that a slice is at most `isize::MAX` bytes. p07 is unsigned end to end, so that
clause would constrain nothing this proof uses — and the driver conjunct that
discharged it goes with it.

### What the `ensures` is, and what it is not — p07 is p16's case, not p17's

p16's `spec.md` says, correctly for p16, that a read-only kernel's `ensures`
cannot be its security property, because "no byte outside the window was read"
is not a property of the return value; the trusted accessor's discharged
`requires i < v@.len()` is what carries the safety claim. **p07 is that case.**
Its harm is an ordinary out-of-bounds read — the declared array is bigger than
the buffer that arrived — so the accessor precondition is exactly what excludes
it.

**And there is a second thing the `ensures` deliberately does not say: that the
search finds the key.** `bsearch` in `verus.rs` specifies what the *program*
returns — the half-open descent, probe by probe — not "the position of `key` in
a sorted array". Writing the stronger postcondition would have forced a
`requires` that the elements are sorted, which is a precondition about the
contents of a file that no honest loader can discharge
(`.memory/02-bench-rules.md`), and it would have put `adversarial-unsorted.bin`
*outside* the verified domain — deleting the row that shows the difference
between a correctness violation and a safety violation. The weaker spec is the
honest one here, and it is still load-bearing: it pins which bytes the answer is
a function of and it is consumed by a ghost `assert` in the driver.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p07's payload is p16's, p17's and p05's:

```
word 0     u64  stride      # bytes per window; the kernel searches one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes` — the functions p16 added to `common/`, reused verbatim,
with **nothing added to `common/` for p07**. All three are a bulk copy rather
than an element-by-element decode, which is what keeps every p07 row
Miri-checkable (`.memory/02-bench-rules.md`: `head_u64_body`'s per-element loop
is why p01's `large.bin` blocks).

Nothing is a compile-time constant: `n_iters`, `stride`, `n_blob`, every `n`,
every `nq`, every element and every query come from the file.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here and are
deliberately not copied across, exactly as for p16, p17 and p05.

## Driver loop

Identical in all six rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` normalises every copy — the C one included — and
diffs it against `driver.canonical` below.

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

One difference from p05's: **`stride_w >= 8`** rather than `>= 4`, because p07's
window header is the 8-byte `n`/`nq` pair, not the 4-byte `nrow`/`ncol` one.
`adversarial-stride7.bin` attacks it.

The comparison is in `u64` *before* the `as usize` cast, so a truncating driver
cannot sneak a 2^40 stride past it. (Unchanged from p16, p17 and p05, and still
load-bearing.)

### Why this does not evaporate

Same mechanism as p01, p02, p16, p17 and p05: `k` is derived from `acc`, and
`acc` from the previous call's result, so call *i+1* cannot begin until call *i*
has returned. Nothing to CSE, nothing to hoist, no `black_box` and no
`asm volatile` — the same arithmetic in both languages, so neither gets a
stronger barrier than the other. `k = (acc * nwin) >> 64` is Lemire's map onto
`[0, nwin)`; see p01's `spec.md` for why it is a multiply-shift and not a
modulo.

### Why every adversarial input is exactly one window

`k` is pseudo-random over `[0, nwin)`, so with several windows a malformed one
would be hit only probabilistically — and an overrun from a *middle* window
stays inside the allocation, which is a silent wrong answer with no ASan and a
gate that passes by luck. With `nwin == 1`, `k` is always 0 and `off` is always
0, so `adversarial-count`'s and `adversarial-width`'s overruns leave the
allocation deterministically.

The related trap, from p17 and non-obvious: **window 0 must serve something**,
because a window returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is
then 0 for ever — the driver's Lemire index has an absorbing state at
`acc == 0`. On `small` and `large` every window runs a full query batch, so this
is satisfied by construction; on the adversarial inputs there is only one
window, so `k == 0` regardless. `inputs/gen.py` records both constraints.

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
| `verus.obligations` = 10 | **`bsearch` 1 + `query_walk` 1 + `kernel` 3 + `main` 5 = 10.** Every term is checkable with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained, and the zero terms are checkable the same way: `u32_at`, `n_at`, `nq_at`, `elem_at`, `key_at` and `search_fold` are non-recursive spec fns and report **0**; the three `external_body` items report **0**; the two *recursive* spec fns carry one termination query each. `kernel`'s 3 is 1 body + 1 per loop body (two loops) — and the **absence of a fourth term is p07's contrast with p05**, whose kernel is 5 because a `i*ncol + j` index needs two `by (nonlinear_arith)` sub-proofs. Every multiplication in p07's kernel is by the literal 4. **`main`'s 5 does not decompose further from the command line and is quoted as measured**: the by-block rule of thumb would predict 6 and Verus reports 5, the identical off-by-one p05's and p17's `spec.md` record for the identical driver. `.memory/04-verus.md`'s one-query-per-function-plus-one-per-loop rule gives **7** here and is therefore not the derivation. |
| `verus.twin_obligations` = 11 | the count in the **other** configuration, `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. **10 shipped + 1**, and the 1 is measured the same way: `--cfg slb_twin --verify-function slb_twin_get_unchecked --verify-root` reports `1 verified` — one function, no loop body, no `by`-block. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`. Since TASK_010 that no longer makes Miri optional: it is mandatory for any pattern with a trusted item, because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`. `check.py` derives this from `verus.rs` rather than reading the flag. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == search_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (search_fold). p07 is p16's and p05's shape and NOT p17's: the harm is an ordinary read outside the buffer, so the trusted accessor's discharged `i < v@.len()` is the security property and the `ensures` is what keeps the proof non-vacuous and pins WHICH bytes the answer is a function of. There is no memory-safe harm here for the ensures to be the only guard against -- p07 has no 'inside the buffer but outside the window' band, because the length check bounds every index by `avail`. **What the `ensures` deliberately does NOT say is that the search finds the key.** `bsearch` specifies what the PROGRAM returns, not the position of `key`, so the specification needs no sortedness precondition, `adversarial-unsorted.bin` is inside the verified domain, and the correctness/safety distinction that input exists to show is visible instead of assumed away. A `requires` about the sortedness of a file is exactly the precondition no honest loader can discharge that `.memory/02-bench-rules.md` warns about.",
  "idiom": {
    "required": [
      "the midpoint is `lo + (hi - lo) / 2` in all six rungs and in the Verus spec function bsearch. The overflow-safe form; pinning it is what makes forbidden[0] settleable by grep instead of by argument.",
      {
        "c": "the search bounds are HALF-OPEN and the upper one is the COUNT, not the last index: `size_t hi = n;`. All six rungs; hi = n - 1 is not an admissible respelling, see why.",
        "rust": "the search bounds are HALF-OPEN and the upper one is the COUNT, not the last index: `let mut hi: usize = n;`. All six rungs; hi = n - 1 is not an admissible respelling, see why."
      },
      "the upper bound is ASSIGNED and never decremented: `hi = mid;` in all six rungs. hi = mid - 1 underflows at mid == 0, which any key below element 0 reaches on WELL-FORMED input.",
      "the lower bound moves past the probe: `lo = mid + 1;` in all six rungs.",
      {
        "c": "the compare is three-way with an early exit on equality: `if (v == key)` in both C rungs.",
        "rust": "the compare is three-way with an early exit on equality: `if v == key` in all four Rust rungs."
      },
      {
        "c": "and the ordering test that halves the range: `if (v < key)` in both C rungs.",
        "rust": "and the ordering test that halves the range: `if v < key` in all four Rust rungs."
      },
      {
        "c": "the length check is `if (4 * n + 4 * nq > avail)` in 64-bit size_t. Present in five of the six rungs; c/kernel.c omits exactly this line and nothing else, which IS the bug, so the one scoped-absent audit pair this declaration reports is on that rung and is correct.",
        "rust": "the length check is `if 4 * (n as u64) + 4 * (nq as u64) > avail as u64` -- widened to u64 because n and nq are u32 fields and 4*n + 4*nq needs 35 bits. All four Rust rungs."
      },
      {
        "c": "the probe index keeps the multiply and the base: `size_t ep = off + 8 + 4 * mid;` in both C rungs.",
        "rust": "the probe index keeps the multiply and the base: `let ep: usize = off + 8 + 4 * mid;` in all four Rust rungs. R3 may reslice [ep .. ep + 4] -- that moves the CHECK and keeps the INDEX, and it is the most a rung may do."
      },
      "the little-endian u32 decode is written out with + and * rather than | and <<, so it stays linear arithmetic: `+ 65536 *` in all six rungs.",
      "...and its top byte: `+ 16777216 *` in all six rungs.",
      {
        "c": "the query result is folded as found + 1, so a rung returning a different index cannot produce the same checksum: `acc * 31 + (found + 1)` in both C rungs.",
        "rust": "the query result is folded as found + 1, so a rung returning a different index cannot produce the same checksum: `wrapping_add(found.wrapping_add(1))` in all four Rust rungs."
      },
      {
        "c": "n * nq is folded, so a rung running a different number of searches cannot produce the same checksum either: `(uint64_t)n * (uint64_t)nq` in both C rungs.",
        "rust": "n * nq is folded, so a rung running a different number of searches cannot produce the same checksum either: `(n as u64).wrapping_mul(nq as u64)` in all four Rust rungs."
      }
    ],
    "forbidden": [
      "`(lo + hi) / 2`",
      "`binary_search`",
      "`partition_point`",
      "`chunks_exact`",
      "`from_le_bytes`"
    ],
    "why": "each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). `(lo + hi) / 2` is the spelling `.memory/06-catalogue.md` names as p07's bug and it is forbidden here rather than measured, because NOTES.md 0 shows it is UNREACHABLE at every size this wire format can express: `n` is a u32 header field, so `lo + hi <= 2*(2^32 - 2) = 8589934588`, which is 2.1e9x short of 2^64 -- RAM is not the binding constraint, the field width is. Pinning the safe spelling is what makes the midpoint question settleable by grep instead of by argument, which is the whole point of the standard. `binary_search`, `partition_point`, `chunks_exact` and `from_le_bytes` delete the search or the written-out little-endian decode. `from_le_bytes` and the `try_into` route to it are additionally NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd -- both are `is not supported`, measured on p05 and p16 (TASK_027_REVIEW) -- so a rung using them would compare a safe cell against an unsafe cell that cannot exist, which is the `identity`-pin trap this file's own `identity` key sets. The half-open bounds (`hi = n`, `hi = mid`) are `required` and not merely conventional: the textbook inclusive form underflows `size_t` at `mid == 0`, which any key below element 0 reaches ON WELL-FORMED INPUT, so it is not an admissible respelling of this kernel -- it is a different and broken one, and NOTES.md 6 measures what it does. The declaration was written BEFORE any cell was built or measured, which is the one thing TASK_018's standard cannot retrofit onto p01, p02, p05, p08, p16 or p17. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither."
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
    "obligations_note": "10 = bsearch 1 + query_walk 1 + kernel 3 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`. u32_at, n_at, nq_at, elem_at, key_at and search_fold are NON-RECURSIVE spec fns and carry 0; get_unchecked, load_input and emit are external_body and carry 0; bsearch and query_walk are RECURSIVE and carry one termination query each. kernel's 3 = body + 2 loop bodies, and the absence of a fourth term is the p05 contrast worth reading: p05's kernel is 5 because it carries two `by (nonlinear_arith)` sub-proofs for a `i*ncol + j` index, while every multiplication in p07's kernel is by the literal 4 and Z3 takes all of them for free. main's 5 is quoted AS MEASURED and does not decompose from the command line: body + driver loop + one per by-block would predict 6 and Verus reports 5 -- the identical off-by-one p05's and p17's spec.md record for the identical driver. `.memory/04-verus.md`'s one-per-function-plus-one-per-loop rule of thumb gives 7 here and is therefore not the derivation.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. 10 shipped + 1, and the 1 is measured: `--cfg slb_twin --verify-function slb_twin_get_unchecked --verify-root` reports `1 verified` -- one function, no loop body, no `by`-block. Pinned for the same reason the shipped count is: `tv > base_v` only says something extra compiled, and a twin that quietly lost its body, or an item that exists only under the cfg, moves this number and nothing else.",
    "items": {
      "verus.rs": {
        "u32_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "n_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "nq_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "elem_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "key_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "bsearch": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "query_walk": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "search_fold": {
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
            "r == search_fold(buf@, off as int, len as int)"
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
    "note": "work_per_call is **PROBES, not bytes** -- `nq * ceil(log2(n+1))`, 522 on small and 1656 on large -- and p07 is the first pattern in this project that CANNOT be denominated in bytes. Binary search reads `4*ceil(log2 n)` bytes out of a `4*n`-byte array: on large.bin that is 6624 bytes touched out of a 1 048 916-byte window, so a byte-denominated unit would put the derived floor at 0.25 * 1048916 = 262229 Ir/call against a kernel that legitimately executes tens of thousands, and the gate would fail a healthy pattern -- the same shape as MIN_DECLARABLE_IR_PER_WORK forbidding p09's bit-denominated model (`.memory/02-bench-rules.md`). work_unit_bits is 32, one u32 element compared per probe, so the effective absolute bound under min_ir_per_work is 0.001953125 x 32 = 0.0625. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per PROBE applies unchanged, and the argument for it is easier than any earlier pattern's: probe i+1's ADDRESS is not known until probe i's comparison retires, so there is no vector form and no unrolled form of a dependent search step at any -march. The cheapest imaginable correct implementation is several instructions per probe, not a fraction of one. WHICH WAY THE ESTIMATE ERRS: STRICT. `ceil(log2(n+1))` is the MAXIMUM trip count and a query that hits exits early, so the kernel makes at most this many probes -- p16's and p05's direction, not p17's, and the measured ratio is in NOTES.md 4. The two probe inputs differ in work_per_call (522 vs 1656) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost, on the first kernel in this project whose measured loop has a DATA-DEPENDENT trip count and an unpredictable branch -- so the byte-identity result now covers a loop with a `break`, an `invariant_except_break` and a loop `ensures` (10 obligations, two recursive spec functions, a nested loop, and ZERO nonlinear steps in the kernel, which is p07's contrast with p05). At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."
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
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. On p07 there is a second reason worth stating: the unchecked index is `off + 8 + 4*mid` where `mid` is computed from the DATA, so an off-by-one in the search bounds would not be visible as a fixed shift the way p16's and p17's would -- it would show up on some queries and not others. Every input here is cheap to Miri: the kernel probes 4*work_per_call bytes per call, i.e. 2088 on small and 6624 on large at 4 iterations, which is the smallest per-call figure in the project; the only cost is the payload `to_vec`, which is a bulk copy.",
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

There is no exit 7 here, for p16's, p17's and p05's reason: p07's payload names
no allocation size, so p02's `SLB_MAX_CAP` check would be dead code.

## Degenerate shapes

`stride_w >= 8 && stride_w <= n_blob` is the driver's whole input validation. A
stride below 8 cannot hold the header (`adversarial-stride7.bin`); a stride above
`n_blob` leaves no whole window, so `nwin` would be 0 and `k` would have nothing
to index. Either way the loop is skipped and the driver prints `0` after **zero**
kernel calls.

A window whose array does not fit (`adversarial-count.bin`,
`adversarial-width.bin`) is different and the difference is deliberate: there
the calls *do* happen and the **kernel** is what rejects, on
`4*n + 4*nq > avail` — the one test R1 does not have — so the seven checked
cells return 0 on every call while the two R1 cells jump outside the
allocation. The two differ in *how far*: `count` declares 4096 elements and
lands ~16 KiB out, still inside the process heap, so a plain build reads memory
it does not own and prints a wrong number; `width` declares 2^30 and lands
4 GiB out, which no plain build survives. They also differ in what a
**narrower** check would do — `count` is rejected by a 32-bit check and `width`
is waved through by one — which is the variant `NOTES.md` §6 builds.

`adversarial-zero.bin` is the control for both: the same "the header lied" shape
with the *product* innocent, so every cell including R1 returns 0. What it is
really the control for is the **loop-bound spelling** — see "The zero guard is
dead here".

`adversarial-unsorted.bin` is the odd one out and is here on purpose: it
violates the algorithm's *assumption* and nothing else. Every rung stays in
bounds, every rung agrees with `model.py`, ASan is silent, and the answer is
simply not the answer a sorted array would have given. It is the pattern's
correctness-versus-safety row, and it exists because `verus.rs` specifies what
the search returns rather than where the key is — see "What the `ensures` is,
and what it is not".

The kernel's `len < 8` guard is, given the driver's `stride_w >= 8`, unreachable
in this benchmark. It is kept anyway so the kernel is **total** and its
`requires` stays purely structural; the alternative — a `len >= 8` precondition
— would be a precondition about the driver's own guard rather than about the
buffer. `NOTES.md` §9 records that it is dead and why it stays.
