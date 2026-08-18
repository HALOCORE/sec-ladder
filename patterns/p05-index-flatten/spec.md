# p05 — 2-D index flattening: the kernel contract

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
byte 0..2    nrow    u16 LE    DECLARED row count      ATTACKER DATA
byte 2..4    ncol    u16 LE    DECLARED column count   ATTACKER DATA
byte 4..     data    u8[]
data_start = 4 ;  avail = len - 4                      what ACTUALLY arrived
```

## Semantics

```
if len < 4:                       return 0
nrow, ncol from the header
if nrow == 0 || ncol == 0:        return 0        # present in EVERY rung

# >>> THE CHECK. R1 omits exactly this line and nothing else. <<<
if nrow * ncol > avail:           return 0        # computed in u64/size_t

acc = 0                                           # u64
for i in 0 .. nrow:
    row = 0                                       # u32
    for j in 0 .. ncol:
        row = row +32 buf[off + 4 + i*ncol + j]   # ASSOCIATIVE — vectorises
    acc = acc *64 31 +64 row                      # serial across ROWS only
return acc *64 31 +64 (nrow *64 ncol)
```

`+32`/`*64`/`+64` are wrapping, as in p01/p02/p16/p17, so the kernel has **no
precondition on values** and every measured input is inside the verified domain
by construction. C's unsigned types wrap by definition (6.2.5p9) and the Rust
rungs write `wrapping_add`/`wrapping_mul`.

### The inner loop is a plain sum on purpose, and that is the whole design

Every fold this project has measured — p01, p02, p16, p17 — is a serial Horner
chain, so the safe-vs-unsafe gap has only ever been measured on a **scalar loop
on both sides**. p16 quantified what a bounds check costs when it blocks a 4×
unroll (2.25 of 4.25 Ir/byte). p05's inner loop is associative so that it *can*
vectorise, while the Horner step happens once per **row**, so the result still
depends on row order and the two loops cannot be re-associated into one flat
scan. That gives a vectorisable inner loop whose bound (`ncol`) comes from the
file but is loop-invariant *within* the inner loop — the "optimiser can see the
loop" case, now with a 2-D index on top.

### Load-bearing, do not "improve"

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug. Edit both or neither — TASK_016 *duplicated* this
section into the block rather than moving it, and one bullet was already missing
from the copy on the day it landed (TASK_016_REVIEW m1/m2; restored at
TASK_017).

- **`i*ncol + j` stays as written, in every rung.** Do not strength-reduce it to
  a running pointer and do not use `chunks_exact` — either deletes the pattern.
  R3 reslices `[base .. base+ncol]` with `base = off + 4 + i*ncol`, which moves
  the *check* and keeps the *multiply*, and that is the most a rung may do.
- **The check is `nrow * ncol > avail` in 64-bit.** The width is half the
  pattern: `nrow`, `ncol` are u16, so the product is at most
  65535·65535 = 4 294 836 225, which **fits `uint32_t`** (< 4 294 967 295) and
  **exceeds `INT_MAX`** by 2 147 352 577. So a `uint32_t` check is sound against
  everything this wire format can express and a signed `int` check is not — the
  common phrasing "int/u32 can overflow" is wrong by one type here.
  `adversarial-ovf.bin` is the input and `NOTES.md` §6 builds the wrong-width
  cell.
- **`nrow * ncol` is folded into the result**, so a rung that walks a different
  number of elements cannot produce the same checksum even if the bytes happened
  to fold the same way.
- **`row` is a `u32` accumulator, `acc` a `u64`.** This is the one place p05
  deviates from TASK_013's pseudocode, it is forced by measurement, and it is
  the difference between p05 measuring something and p05 measuring nothing. See
  the next section.

### Why the row accumulator is 32 bits — the measurement that forced it

TASK_013's pseudocode folds into a `u64` row accumulator. Built that way, at the
flags this project builds with (`-O3`, **no `-march`/`-C target-cpu`**, i.e.
baseline x86-64 = SSE2), **the inner loop does not vectorise in any LLVM rung**:

```
$ clang -std=c99 -O3 -S k.c -Rpass-missed=loop-vectorize
k.c:16:9: remark: the cost-model indicates that vectorization is not beneficial
```

and rustc emits `xmm`-free scalar code for R2, R3 and R4 alike. gcc vectorises
it anyway (2.13 Ir/byte, 34 instructions per 16 bytes). The reason is the
widening: `u8 -> u64` needs three levels of `punpck` per lane on SSE2, so LLVM's
cost model prices 2 elements per vector against 1 per scalar iteration and
declines. `-mavx2` flips it (VW 4, interleave 4) — but this project passes no
`-march`, `harness/build.py` is what decides that, and changing it would move
all 47 patterns and break comparability with p01/p02/p16/p17.

Narrowing the row accumulator to `u32` needs only two `punpck` levels and every
back end then vectorises:

| row accumulator | gcc 13.3 | clang 22.1.6 | rustc 1.97.1 (R2 / R3 / R4) |
|---|---|---|---|
| `u64` (TASK_013's) | vectorised, 16 B/iter, 34 insns | **scalar**, 8× unrolled | **scalar** in all three |
| **`u32` (shipped)** | vectorised, 16 B/iter, 17 insns | vectorised, 8 B/iter, 11 insns | vectorised, 8 B/iter, 12 insns |
| `u16` | — | — | vectorised, 16 B/iter, 9 insns |

Nothing else about the pattern moves: the fold is still associative, the index
is still `i*ncol + j`, the Horner step is still per row, the arithmetic is still
wrapping, and `nrow*ncol` is still folded into the result. A 32-bit per-row
checksum is also what a real row hash would use. `NOTES.md` §1 has the
disassembly for every cell in that table.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == grid_fold(buf, off, len)
```

`grid_fold` is the spec function; `model.py` is its independent Python twin.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included, and `harness/check.py` evaluates it at every one of
the kernel calls to prove that it does. Both declared dimensions, all 2^32 pairs
of them, are *arguments* of the problem; the kernel is total in all of them.

**p17's second clause is deliberately not carried forward.** p17 needed
`buf_len <= 9223372036854775807` because it cast to `i64` and vstd has no axiom
that a slice is at most `isize::MAX` bytes. p05 is unsigned end to end, so that
clause would constrain nothing this proof uses — and the driver conjunct that
discharged it goes with it. Copying a dead precondition across from the template
would be the "a `requires` no caller should have to discharge" failure
`.memory/02-bench-rules.md` warns about, in miniature.

### What the `ensures` is, and what it is not — p05 is p16's case, not p17's

p16's `spec.md` says, correctly for p16, that a read-only kernel's `ensures`
cannot be its security property, because "no byte outside the window was read"
is not a property of the return value; the trusted accessor's discharged
`requires i < v@.len()` is what carries the safety claim. **p05 is that case.**
Its harm is an ordinary out-of-bounds read — the declared matrix is bigger than
the buffer that arrived — so the accessor precondition is exactly what excludes
it.

p17 was the exception, and it is worth restating why so that p05 is not
mis-filed with it: p17 had a *second* harm that was memory-safe (a read of the
window's own metadata, in bounds of the allocation) and only the functional
`ensures` could exclude that one. p05 has no such regime. Every index it can be
made to form is either inside the window or outside the buffer; there is no
"inside the buffer but outside the window" band, because `avail` *is* the
window's tail.

So p05's `ensures` does the job it does on p16: it keeps the proof non-vacuous
and it pins *which* bytes the result is a fold of, which is what makes the
element count in the return value meaningful. It is not the security property.

### The zero guard is a DoS guard, and it changes no answer

`if nrow == 0 || ncol == 0: return 0` is kept in every rung, R1 included — and
it is **semantically dead**. With `nrow == 0` the outer loop does not run and
the fold returns `0*31 + 0 == 0`; with `ncol == 0` every row folds to 0, so `acc`
stays 0 and the fold returns `0*31 + 0 == 0`. Either way the guard's answer and
the loop's answer agree.

What it is not dead for is *work*. `nrow*ncol == 0` passes the size check for
**any** `nrow`, so a window declaring `nrow = 65535, ncol = 0` costs 65 535 empty
outer iterations per call without it. That is attacker-controlled work with no
memory error anywhere, and `adversarial-zero.bin` is the input that makes the
guard load-bearing. `NOTES.md` §6 measures the variant with the guard removed.

It is kept rather than removed for the reason p17 kept its unreachable `len < 2`:
the alternative is a `requires` about the driver's guard rather than about the
buffer, and `.memory/02-bench-rules.md` is explicit that a precondition narrow
enough to make the proof easy is one no caller should have to discharge.

### What p05 is *not*: an unbounded walk, or a signed underflow

p16's missing check made `end - p` underflow `size_t` so the walk never
terminated; p17's let a signed index go negative so the read ran *backwards*.
Neither happens here. Every loop in p05 has a trip count fixed before it starts
(`nrow`, then `ncol`), every quantity is unsigned, and the read runs **forwards**
off the end — `avail` bytes are there and `nrow*ncol` are read. ASan reports it
as `N bytes after` the region, which is p16's message and not p17's.

What is new is that the index is formed by **multiplication**. That is why the
proof needs nonlinear reasoning where p16's and p17's did not (`NOTES.md` §5),
and it is why the check itself can overflow in a narrower type, which no earlier
pattern's check could.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p05's payload is p16's and p17's:

```
word 0     u64  stride      # bytes per window; the kernel folds one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes` — the functions p16 added to `common/`, reused verbatim,
with **nothing added to `common/` for p05**. All three are a bulk copy rather
than an element-by-element decode, which is what keeps every p05 row
Miri-checkable (`.memory/02-bench-rules.md`: `head_u64_body`'s per-element loop
is why p01's `large.bin` blocks).

Nothing is a compile-time constant: `n_iters`, `stride`, `n_blob` and every
`nrow`/`ncol` come from the file.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here and are
deliberately not copied across, exactly as for p16 and p17.

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

Two differences from p17's, both deliberate:

- **`stride_w >= 4`** rather than `>= 2`: p05's window header is the 4-byte
  `nrow`/`ncol` pair, not a 2-byte count. `adversarial-stride3.bin` attacks it.
- **`n_blob <= 9223372036854775807` is gone**, with the `requires` clause it
  discharged. See "Contract" above.

The comparison is in `u64` *before* the `as usize` cast, so a truncating driver
cannot sneak a 2^40 stride past it. (Unchanged from p16 and p17, and still
load-bearing.)

### Why this does not evaporate

Same mechanism as p01, p02, p16 and p17: `k` is derived from `acc`, and `acc`
from the previous call's result, so call *i+1* cannot begin until call *i* has
returned. Nothing to CSE, nothing to hoist, no `black_box` and no `asm volatile`
— the same arithmetic in both languages, so neither gets a stronger barrier than
the other. `k = (acc * nwin) >> 64` is Lemire's map onto `[0, nwin)`; see p01's
`spec.md` for why it is a multiply-shift and not a modulo.

### Why every adversarial input is exactly one window

`k` is pseudo-random over `[0, nwin)`, so with several windows a malformed one
would be hit only probabilistically — and an overrun from a *middle* window
stays inside the allocation, which is a silent wrong answer with no ASan and a
gate that passes by luck. With `nwin == 1`, `k` is always 0 and `off` is always
0, so `adversarial-dims`'s overrun leaves the allocation deterministically.

The related trap, from p17 and non-obvious: **window 0 must serve something**,
because a window returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is
then 0 for ever — the driver's Lemire index has an absorbing state at
`acc == 0`. On `small` and `large` every window folds a full matrix, so this is
satisfied by construction; on the adversarial inputs there is only one window,
so `k == 0` regardless. `inputs/gen.py` records both constraints.

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
| `verus.obligations` = 12 | **`row_fold` 1 + `grid_walk` 1 + `kernel` 5 + `main` 5 = 12.** Every term is checkable with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained, and the four zero terms are checkable the same way: `nrow_at`, `ncol_at` and `grid_fold` are non-recursive spec fns and report **0**; the three `external_body` items report **0**; the two *recursive* spec fns carry one termination query each. `kernel`'s 5 is 1 body + 1 per loop body (two loops) + 1 per `by (nonlinear_arith)` sub-proof (two of them: the `usize` product bound and the distributivity step). `.memory/04-verus.md`'s rule of thumb — one query per function plus one per loop — gives **8** here and is therefore not the derivation, exactly as on p16 and p17. **`main`'s 5 does not decompose further from the command line and is quoted as measured**: the by-block rule of thumb would predict 6 (1 body + 1 loop + 4 `by`-blocks) and Verus reports 5, so at least one sub-proof is not its own query. p17's `spec.md` asserts the same decomposition for the identical driver and has the same off-by-one; see `NOTES.md` §9. |
| `verus.twin_obligations` = 13 | the count in the **other** configuration, `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. **12 shipped + 1**, and the 1 is measured the same way: `--cfg slb_twin --verify-function slb_twin_get_unchecked --verify-root` reports `1 verified` — one function, no loop body, no `by`-block. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`. Since TASK_010 that no longer makes Miri optional: it is mandatory for any pattern with a trusted item, because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`. `check.py` derives this from `verus.rs` rather than reading the flag. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": ["off + len <= buf_len"],
  "ensures": ["result == grid_fold(buf, off, len)"],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (grid_fold). p05 is p16's shape and NOT p17's: the harm is an ordinary read past the end of the buffer, so the trusted accessor's discharged `i < v@.len()` is the security property and the `ensures` is what keeps the proof non-vacuous and pins WHICH bytes the answer is a fold of. There is no memory-safe harm here for the ensures to be the only guard against -- p05 has no 'inside the buffer but outside the window' band, because avail IS the window's tail. See the prose above.",

  "idiom": {
    "required": [
      "i*ncol + j written out in every rung, not strength-reduced",
      "R3 may reslice [base .. base+ncol] with base = off + 4 + i*ncol -- that moves the CHECK and keeps the MULTIPLY, and it is the most a rung may do",
      "the fit check is nrow * ncol > avail in 64-bit; row is a u32 accumulator and acc a u64",
      "nrow * ncol is folded into the result, so a rung that walks a different number of elements cannot produce the same checksum even if the bytes happened to fold the same way"
    ],
    "forbidden": ["chunks_exact", "a running row pointer"],
    "why": "either deletes the flattened index, which IS the pattern; a rung that does it is a different benchmark and its numbers are not comparable (this file's second sentence). RESTATED in this hashed block at TASK_016 from the prose section 'Load-bearing, do not improve' above, where contract_sha256 could not see it -- restated, not moved: the prose is still there and THIS block is the authoritative copy of it (TASK_016_REVIEW m2), and the copies had already drifted, the 'nrow * ncol is folded into the result' entry having been dropped on the day the block landed and restored at TASK_017 (m1). The declaration itself was made at TASK_013 BEFORE any of these spellings were measured, it was right both times it was tested, and two consecutive tasks measured a forbidden spelling anyway and published the result as p05's number (TASK_014_REVIEW B1 measured chunks_exact, TASK_015 measured the running row pointer; neither cited this file). NOTES.md 13 tabulates 11 measured spellings of this kernel with the contract-conformant cell marked -- none of the other ten is a p05 number. The gate checks that this key is present and hashes it; it does NOT check that a rung honours it. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4 -- and it moves the UNSAFE rung too, by the same lever: p16's R4 by `4*nrec` (TASK_023) and p05's by 7 flat (TASK_022). So `R3ship - R4ship` is NOT an upper bound on the in-contract safety tax, which is what this sentence claimed until TASK_023. Both rungs are spellings, so with both free the quantity is an INTERVAL and the published pair sits INSIDE it -- p05's is `2*nrow - 2` ... `6*nrow + 20` around a published `6*nrow + 9`, and its bottom endpoint is measured at exactly 0.00. Publish that interval. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel, and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither."
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
    "obligations": {"verus.rs": 12},
    "twin_obligations": {"verus.rs": 13},
    "obligations_note": "12 = row_fold 1 + grid_walk 1 + kernel 5 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`. nrow_at, ncol_at and grid_fold are non-recursive spec fns and carry 0; get_unchecked, load_input and emit are external_body and carry 0; row_fold and grid_walk are recursive and carry one termination query each. kernel's 5 = body + 2 loop bodies + 2 `by (nonlinear_arith)` sub-proofs. main's 5 is quoted AS MEASURED and does not decompose from the command line: body + driver loop + one per by-block would predict 6 and Verus reports 5. `.memory/04-verus.md`'s one-per-function-plus-one-per-loop rule of thumb gives 8 here and is therefore not the derivation.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. 12 shipped + 1, and the 1 is measured: `--cfg slb_twin --verify-function slb_twin_get_unchecked --verify-root` reports `1 verified` -- one function, no loop body, no `by`-block. Pinned for the same reason the shipped count is: `tv > base_v` only says something extra compiled, and a twin that quietly lost its body, or an item that exists only under the cfg, moves this number and nothing else.",
    "items": {
      "verus.rs": {
        "nrow_at":    {"external": null, "requires": [], "ensures": []},
        "ncol_at":    {"external": null, "requires": [], "ensures": []},
        "row_fold":   {"external": null, "requires": [], "ensures": []},
        "grid_walk":  {"external": null, "requires": [], "ensures": []},
        "grid_fold":  {"external": null, "requires": [], "ensures": []},
        "get_unchecked": {"external": "verifier::external_body",
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "slb_twin_get_unchecked": {"external": null,
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "load_input": {"external": "verifier::external_body",
                       "requires": [], "ensures": []},
        "emit":       {"external": "verifier::external_body",
                       "requires": [], "ensures": []},
        "kernel":     {"external": null,
                       "requires": ["off + len <= buf@.len()"],
                       "ensures": ["r == grid_fold(buf@, off as int, len as int)"]},
        "main":       {"external": null, "requires": [], "ensures": []}
      }
    }
  },

  "driver": {
    "statements": 12,
    "c_source": "c/main.c",
    "regions": ["safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs",
                "c/main.c"],
    "aliases": {"c": {"n_body": "bytes.len()",
                      "bytes": "bytes.as_slice()",
                      "inp.n_iters": "n_iters"}},
    "call_args": {"c": {"kernel": [0, 2, 3]}},
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
    "probe_inputs": ["small.bin", "large.bin"],
    "probe_iters": [100, 200],
    "note": "work_per_call is the WINDOW in bytes -- the stride, 498 on small and 3969 on large -- and the two differ precisely so that check.py's d(Ir)/d(work) assertion has two probe shapes and can run at all. The matrix tiles the window exactly on both (19x26 = 494 = 498-4 and 65x61 = 3965 = 3969-4), so the unit is a STRICT OVER-estimate of the bytes folded, by exactly the four header bytes, and the derived floor errs strict -- p16's direction, not p17's. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged. THAT ARGUMENT IS DIFFERENT FROM p16's AND p17's AND HAS TO BE: they could say the fold is a serial Horner chain with no vector form, and p05's inner loop is the first in this project that actually vectorises. It is still sound at the flags this project builds with (-O3, no -march, i.e. SSE2): measured, rustc and clang take 8 bytes per vector iteration in 12 and 11 instructions (1.50 / 1.38 Ir/byte) and gcc 16 bytes in 17 (1.06), i.e. 4.2x above the floor at worst before the per-row Horner step and the scalar epilogue are counted. An AVX-512 vpsadbw form would reach 0.0625 and would need a declaration, but harness/build.py passes no -march so no rung can get there. Measured margins are in NOTES.md 9."
  },

  "identity": [
    {"a": "unsafe", "b": "verus", "O0": "norel", "O3": "exact",
     "why": "R4 == R5: the proof licenses unsafe code at zero cost, on the first kernel in this project whose measured loop is VECTORISED -- so the byte-identity result now covers a vector body and its scalar epilogue, not only scalar code (12 obligations, two recursive spec functions, a nested loop invariant and three nonlinear steps). At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."}
  ],

  "miri": {
    "pair": ["unsafe", "verus"],
    "sources": ["unsafe.rs"],
    "required": true,
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. On p05 there is a second reason worth stating: the unchecked index is a PRODUCT of two attacker u16s plus an offset, so an off-by-one in the nonlinear reasoning would not be visible as a small constant shift the way p16's and p17's would. Every input here is Miri-checkable: the cost is 4 iterations x nrow*ncol bytes, and the largest is 3965 against a budget of ~3 M.",
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

There is no exit 7 here, for p16's and p17's reason: p05's payload names no
allocation size, so p02's `SLB_MAX_CAP` check would be dead code.

## Degenerate shapes

`stride_w >= 4 && stride_w <= n_blob` is the driver's whole input validation. A
stride below 4 cannot hold the header (`adversarial-stride3.bin`); a stride above
`n_blob` leaves no whole window, so `nwin` would be 0 and `k` would have nothing
to index. Either way the loop is skipped and the driver prints `0` after **zero**
kernel calls.

A window whose matrix does not fit (`adversarial-dims.bin`) is different and the
difference is deliberate: there the calls *do* happen and the **kernel** is what
rejects, on `nrow * ncol > avail` — the one test R1 does not have — so the seven
checked cells return 0 on every call while the two R1 cells read past the
allocation. `adversarial-zero.bin` is the control for it: the same "the header
lied" shape with the *product* innocent, so every cell including R1 returns 0.

The kernel's `len < 4` guard is, given the driver's `stride_w >= 4`, unreachable
in this benchmark. It is kept anyway so the kernel is **total** and its
`requires` stays purely structural; the alternative — a `len >= 4` precondition
— would be a precondition about the driver's own guard rather than about the
buffer. `NOTES.md` §9 records that it is dead and why it stays.
