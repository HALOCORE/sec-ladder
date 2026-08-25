# p46 -- schoolbook bignum multiply-accumulate into a fixed-capacity scratch: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

/!\ **This file is NOT generated.** `.memory/05-layout.md` records three tasks in
a row that shipped a `spec.md` edit a generator silently reverted; p46 has no
`controls/mkcontract.py` and nothing will revert an edit here. The shared
named-spelling paragraph inside `idiom.why` was spliced in once from a donor
`spec.md` (p19's) and its `sha256` is checked by
`harness/check.py::named_spelling_problem` on every run.

## What p46 is, and what it is NOT

p46 multiplies two bignums whose **limb counts arrive in the input**, schoolbook,
into a product scratch of **fixed** capacity:

```c
if (8 + 8 * (n + m) > len)   return 0;          /* the INPUT bound: every rung has it   */
if (n + m > OUTCAP)          return REJ;        /* c/kernel.c omits exactly this line   */
for (i = 0; i < n; i++) { carry = 0;
    for (j = 0; j < m; j++) {
        t = (unsigned __int128)a[i] * b[j] + out[i + j] + carry;
        out[i + j] = (uint64_t)t;  carry = (uint64_t)(t >> 64); }
    out[i + m] = carry; }
```

/!\ **THE UNFLATTERING SENTENCE COMES FIRST. p46's BUG CLASS IS THIS TREE'S
FOURTEENTH `index >= len`.** p01, p02, p03, p05, p07, p11, p12, p13, p14, p16,
p17, p19 and p36 are all *"an index or a length is not checked against a
buffer"*, and so is this. p19 shipped the thirteenth and said so; this is the
fourteenth and says so. **Its nearest sibling is `p05`** -- both index a scratch
with a two-term expression built from two loop counters -- and here is what is
*not* p05's:

| | measured in |
|---|---|
| **p05's INDEX arithmetic is nonlinear (`i*ncol + j`) and its DATA arithmetic is trivial. p46 is the MIRROR.** The index is `i + j`, purely linear; the nonlinear obligation is about the *value*, `a*b + c + carry <= 2^128 - 1`. p05 discharges its bound with `lemma_mul_inequality` on an ADDRESS; p46 discharges its with `by (nonlinear_arith)` + `by (compute)` on a VALUE, and the values are the attacker's | `NOTES.md` 6 |
| **the out-of-bounds access is a WRITE.** p05's is a read | `NOTES.md` 0a |
| **the tree's first `by (bit_vector)` and first `by (compute)` in executable position** -- 0 hits for either across all 23 pre-existing `patterns/*/verus.rs`, and ten of them carry a comment saying they deliberately avoid `bit_vector` | `NOTES.md` 2 |

/!\/!\ **AND THE MEMORY-UNSAFE FRAMING IS CONDITIONAL. THE CONDITION IS NAMED, IT
IS PINNED IN THE HASHED BLOCK BELOW, AND IT WAS SETTLED BY RUNS BEFORE ANY CELL
WAS BUILT** (`NOTES.md` 0a). A miscounted buffer index is a *memory-safety* bug
only if the index is left alone. Both of the following are `forbidden` entries:

| | measured in |
|---|---|
| **the index is NOT CLAMPED.** `out[(i + j) % OUTCAP]` is the identical miscount and it is **exit 0 with ASan and UBSan both silent** -- a wrong answer and no memory event. That is `p31`'s death, demonstrated rather than argued | `NOTES.md` 0a run D |
| **the product scratch is FIXED-CAPACITY, not sized from `n + m` at run time.** With a run-time-sized buffer the bug is unreachable by construction | `NOTES.md` 0a |

**The precedent is not hypothetical.** OpenSSL's `BN_mul()` calls
`bn_wexpand(rr, top)` before `bn_mul_normal()` writes `na + nb` words into `r`,
and `bn_mul_add_words()` then indexes `rp[]` and `ap[]` with no test at all. The
word counts come from the `BIGNUM`s the caller was handed, which on a TLS or
X.509 path are attacker-supplied. "Size the product buffer from the declared
limb counts, then index it unchecked" is the shipped kernel idiom, and it is
exactly this pattern's R4/R5 rung.

## Three things are new here and none of them is the bug class

| | measured in |
|---|---|
| **THE HARDEST PROOF OBLIGATION IS NOT THE ONE THE RUNGS DIFFER ON.** The MAC step cannot overflow 128 bits -- `(2^64-1)^2 + 2*(2^64-1) == 2^128 - 1`, exactly -- and **no rung checks it, in either language, at any optimisation level**. R5 must still discharge it, at the cost of a lemma and three proof modes. Beside it sits `i + j < OUTCAP`, trivial to prove, which is what all three per-step bounds checks cost money for. **The two cost columns come apart inside one kernel** | `NOTES.md` 6, 9 |
| **FOUR HARDENING STRATEGIES WITH FOUR DIFFERENT ASYMPTOTICS**, priced side by side: R5 `O(0)`, hardened C `O(1)` per call, R3 `O(n)` per call, R2 `O(n*m)` per call. p19 priced two; p46 prices four, and the C one is the cheapest of all because C can compare `n + m` against the capacity *before* it starts | `NOTES.md` 8, 9 |
| **SAFE RUST BEATS UNSAFE RUST, AND THE MECHANISM IS THE PROVER.** The cheapest unsafe spelling found is cheaper than every safe one and is **not an admissible rung**: it takes a mutable sub-slice, which the pinned vstd cannot specify. This is `.memory/01-ladder.md` finding 14's mechanism -- *the unsafe class is chained to the prover and the safe class is not* -- with a number on it | `NOTES.md` 0b, 0c |

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Three C arguments against three Rust ones, but the Rust kernel takes four
registers because `&[u8]` is a pointer *and* a length. That is p01's asymmetry
and it is the finding, not a rigging: the length is the thing C does not have
and therefore cannot check. Do not "fix" it by giving C a dead `buf_len`; the
contract forbids that by name.

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0        u8   n      a-limb count                          ATTACKER DATA
byte 1        u8   m      b-limb count                          ATTACKER DATA
byte 2 .. 8        unused (keeps the limbs 8-aligned)
byte 8 ..     u64 LE limbs: a[0..n] then b[0..m]                ATTACKER DATA

OUTCAP = 96    the product scratch capacity, in 64-bit limbs. A compile-time
               constant in every rung -- the buffer the product has to fit into.
BCAP   = 256   the b-operand scratch. Sized for the DECLARED TYPE's full range
               (`m` is a u8), which is why the pre-decode is NOT the bug.
REJ    = 0x9E3779B97F4A7C15   what an over-long product folds to.
```

`OUTCAP`, `BCAP` and `REJ` are compile-time constants in every rung. They are
properties of the *program*; `n_iters`, `stride`, `n_blob`, both limb counts and
every limb byte come from the file.

**One byte of the header is enough**: `n = 48, m = 48` is conforming and
`n = 48, m = 49` writes one limb past the array.

## Semantics

```
if len < 8:                                return 0
n = w[0] ; m = w[1]
if n == 0 or m == 0:                       return 0
if 8 + 8*(n + m) > len:                    return 0     # the INPUT bound

# >>> THE SAFETY LINE. c/kernel.c omits exactly this. <<<
if n + m > OUTCAP:                         return REJ   # the OUTPUT bound

for j in 0 .. m:   bl[j] = ld64(w, 8 + 8*(n + j))       # O(m), b pre-decoded
out[0 .. OUTCAP] = 0
for i in 0 .. n:
    ai = ld64(w, 8 + 8*i) ; carry = 0
    for j in 0 .. m:
        t        = ai*bl[j] + out[i+j] + carry          # 128-BIT, exact
        out[i+j] = t mod 2^64
        carry    = t div 2^64
    out[i+m] = carry
acc = 0
for k in 0 .. n+m:  acc = acc *64 31 +64 out[k]
return (acc *64 31 +64 n) *64 31 +64 m
```

`*64` and `+64` are wrapping `u64` operations. Wrapping, not checked, is
deliberate: it makes the *fold* total on values, so R5's only runtime obligation
is the memory-safety one. The MAC step itself is **not** wrapping and does not
need to be -- it provably cannot overflow -- which is the distinction `NOTES.md`
6 is about.

**The MAC is one 128-bit widening multiply-accumulate, on purpose.** It lowers
to `mulq` + `add` + `adc` + `add`-to-memory + `adc` -- ten instructions per step
including the loop, on this box. A heavier body would drown the three bounds
checks that separate safe Rust from unsafe Rust, and a 64-bit body would delete
the carry chain and the proof obligation with it.

**The inner loop is a SERIAL dependency chain through `carry`.** Step `j+1`'s
`add` needs step `j`'s `adc`, so the loop neither vectorises nor unrolls
usefully. That is why p46's `Ir` and `ns` columns are worth reading against each
other (`NOTES.md` 9) and it is the second reason the fold is this shape.

/!\ **Every rung tests `n + m > OUTCAP`** except `c/kernel.c`, so all six compute
the same function on every input including the adversarial ones, and R2-vs-R3 is
a comparison of two spellings rather than of two programs. `c/kernel.c` is the
one cell that does not, and that omission is the bug.

## The rungs, in one table

| rung | the inner step | how it knows `i + j < OUTCAP` | cost of knowing |
|---|---|---|---|
| R1 `c/kernel.c` | `out[i + j]` | **it does not** | -- |
| R1h `c/kernel_hardened.c` | `out[i + j]` | one compare, before the loops | `O(1)` per call |
| R2 `safe_naive.rs` | `out[i + j]`, `bl[j]` | the language checks it, per access | `O(n*m)` |
| R3 `safe_tuned.rs` | `out[i..i + m].iter_mut().zip(` | one reslice check per row | `O(n)` |
| R4 `unsafe.rs` | `arr_get_unchecked(&out, i + j)` | the author asserts it | `0` |
| R5 `verus.rs` | the same, verbatim | **Verus proves it** | `0` |

The measured figures, the two-parameter laws they are fitted from, and the
in-contract spread on both sides are in `NOTES.md` 8. **They are fitted from the
shipped binaries** -- `.memory/03-measurement.md`: a probe measures a slope, and
its intercept is a property of the probe.

## The adversarial rows

| input | `(n, m)` | where the nest writes | behaviour |
|---|---|---|---|
| `adversarial-nearmiss` | 48, 49 | scratch index **96** -- exactly one limb past a 96-limb array, and only on the row's final carry store | ASan `stack-buffer-overflow`, `WRITE of size 8` |
| `adversarial-oob` | 90, 90 | scratch index **179** -- 84 limbs (672 bytes) past, through the saved registers and the canary | ASan `stack-buffer-overflow` |
| `adversarial-tiny` | -- | stride 4, below the 8-byte header | every rung returns 0; the kernel's degenerate branch is reachable from the measured domain instead of being dead code the proof still carries |
| `adversarial-shortlen` | -- | `payload_len` declares 64 bytes more than the file carries | `slb_load` / `driver::load` exits 5 |

/!\ **`sanitizer_expect` is COMPUTED, not declared by name.** `model.py`
simulates the reach of `c/kernel.c` and reports whether the nest leaves
`[0, OUTCAP)`; `inputs/gen.py` re-implements the same detector independently and
refuses to write a blob whose declaration disagrees with it, down to the exact
index reached.

/!\ **THE REJ PATH IS ADVERSARIAL BY CONSTRUCTION.** `REJ` is returned exactly
when `n + m > OUTCAP` while `8 + 8*(n + m) <= stride`, which is precisely when
`c/kernel.c` writes out of bounds -- so no non-adversarial blob can exercise it,
and `inputs/gen.py` says so where it would otherwise look like an omission.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. The pins exist because a green verification and
a green gate are, separately, evidence of very little;
`patterns/p01-array-sum/spec.md` carries the table of which bypass each pin
closes and it is not repeated here.

Three pins are specific to p46 and worth reading before the block:

| pin | what it is doing here |
|---|---|
| `required[0]` vs `required[1]` | **two bounds, and only one of them is the bug.** `required[0]` -- the INPUT bound -- is present in `c/kernel.c` too; `required[1]` -- the OUTPUT bound -- is the line it omits. Pinning both is what makes p46 an output-side miscount rather than an input-side over-read, and the idiom audit prints `required[1]`'s absence from the buggy rung. |
| `forbidden[0]` and `[1]` | **the bug class's own preconditions, written as spellings.** The clamp and the run-time-sized buffer are each excluded because a rung that took either would still compute a product and would no longer model p46's bug. They forbid a spelling for being *safe* rather than for being *fast* -- p46 is the fourth pattern to do that, after p36, p03 and p19. |
| `identity` | pinned `exact` at O3. `unsafe.rs` takes its window through an out-of-line `subrange` function precisely so that it matches `verus.rs`'s `vstd::slice::slice_subrange`; p19 measured that the inline `&v[i..j]` spelling lands the pair at `differ`. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == bn_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (bn_fold). `requires` is about the WINDOW's placement in the blob and nothing else: the kernel is TOTAL on the contents of the window -- every declared limb count and every limb byte is inside the proof domain, which is what lets the adversarial inputs sit inside it rather than outside. WARNING: `bn_fold` is a recursive specification of the schoolbook ALGORITHM, not of the mathematical product; NOTES.md 6b says what that does and does not buy, and model.py's `_fold_bigint` closes the gap by testing (one Python big-integer multiply per window, cross-checked on every committed input) rather than by proof.",
  "idiom": {
    "required": [
      {
        "c": "every rung tests that the declared operands FIT IN THE WINDOW before it reads a limb, spelled `8 + 8 * (n + m) > len`. `c/kernel.c` HAS this one -- it is not the safety line, and pinning it is what keeps p46's bug an output-side miscount rather than an input-side over-read.",
        "rust": "every rung tests that the declared operands FIT IN THE WINDOW before it reads a limb, spelled `8 + 8 * (n + m) > len`."
      },
      {
        "c": "THE SAFETY LINE: the declared product must fit in the scratch, spelled `n + m > SLB_P46_OUTCAP`. `c/kernel_hardened.c` spells it; `c/kernel.c` DOES NOT, and that omission is the bug this pattern models. The idiom audit prints the absence, and the absence is the vulnerability.",
        "rust": "THE SAFETY LINE: the declared product must fit in the scratch, spelled `n + m > OUTCAP`. All four Rust rungs spell it, so all six rungs compute the same function on every input including the adversarial ones."
      },
      {
        "c": "the multiply-accumulate is a 128-BIT WIDENING one, spelled `(unsigned __int128)ai * bl[j]`; C's unsigned arithmetic wraps by definition (6.2.5p9) so the fold needs no special spelling.",
        "rust": "the multiply-accumulate is a 128-BIT WIDENING one, spelled `(ai as u128) * (bj as u128)`, and the checksum fold is spelled `acc.wrapping_mul(31).wrapping_add(` -- wrapping, not checked, so the kernel is total on VALUES and the only runtime obligation is the index."
      },
      {
        "c": "the product scratch is a FIXED-CAPACITY AUTOMATIC array, spelled `uint64_t out[SLB_P46_OUTCAP]`, never sized from `n + m`. Its capacity is a property of the PROGRAM; the limb counts are properties of the INPUT, and the whole pattern is the gap between them.",
        "rust": "the product scratch is a FIXED-CAPACITY array, spelled `[u64; OUTCAP] = [0u64; OUTCAP]`, never sized from `n + m`."
      },
      {
        "rust": "THE RUNG BOUNDARY INSIDE THE SAFE CLASS, and it is one construct. R2 spells the accumulator read `(out[i + j] as u128)`; R3 spells the whole inner walk `out[i..i + m].iter_mut().zip(`. Each is present in exactly one rung by construction, so the audit reports the other three as absent for both -- that is the declaration working, not failing."
      },
      "the Rust rungs take the window as a sub-slice of `buf` and index that, so the window offset is folded into the base pointer; the b operand is pre-decoded ONCE into a scratch sized by the TYPE of `m`, so the pre-decode is O(m) and is not part of the bug, and the MAC loop is the only O(n*m) thing in the kernel.",
      "the limb decode is the ADDITIVE spelling, byte-identical in all six rungs, so that no rung difference lives in the decoder. p09 spells it the same way and for the same reason: verus.rs's `u64_at` is additive and a shift-or exec spelling would need a bit-vector detour to be related to it."
    ],
    "forbidden": [
      {
        "c": "`% SLB_P46_OUTCAP` -- the clamped index. It is not slower and it is not wrong; it DELETES THE PATTERN, because a clamped index cannot leave the array and there is no memory-safety event at all. Measured, not argued: NOTES.md 0a run D, exit 0 with ASan and UBSan both silent and a wrong answer. This entry is the bug class's own precondition written as a spelling.",
        "rust": "`% OUTCAP` -- the same exclusion on the Rust side."
      },
      {
        "c": "`malloc(` -- a product buffer sized at run time from the declared limb counts. With one the bug is UNREACHABLE by construction, which is the other way this row would have died.",
        "rust": "`vec![0u64;` -- the same exclusion."
      },
      {
        "rust": "`.wrapping_mul(bj)` -- a 64-bit multiply-accumulate. Semantically a DIFFERENT ALGORITHM: it discards the high limb, so the carry chain and the whole nonlinear proof obligation disappear with it. Naming it keeps p46's numbers attached to p46's arithmetic."
      },
      "a dead `buf_len` parameter on the C kernel. The length is the thing C does not have and therefore cannot check; handing C one to make the signatures match would be Rust-in-C-syntax and would delete half the comparison."
    ],
    "why": "p46's whole question is where the fact `i + j < OUTCAP` comes from, and every entry above is about that. The kernel multiplies two bignums whose LIMB COUNTS arrive in the input, one schoolbook multiply-accumulate per (i, j) pair, into a product scratch of FIXED capacity -- so the index is loop-carried in neither sense p05's is: `i + j` is purely LINEAR, and what is nonlinear here is the VALUE, `a*b + c + carry`, not the address. Three rungs establish `i + j < OUTCAP` three ways and the pattern prices all three: R5 proves it statically (0 instructions), R3 amortises it to one reslice check per ROW, R2 tests it three times per MAC STEP -- read `bl[j]`, read `out[i + j]`, write `out[i + j]` -- and the hardened C rung tests it ONCE PER CALL, because C can compare `n + m` against the capacity before it starts. Those four are O(0), O(n), O(n*m) and O(1) and they are not interchangeable, which is the pattern's second result. THE OUTPUT-SIDE BOUND IS THE SAFETY LINE AND THE INPUT-SIDE BOUND IS NOT. `required[0]` pins `8 + 8 * (n + m) > len` in every rung INCLUDING the buggy C one: without it the kernel would read past the window and p46 would be a different, duller bug. `required[1]` pins `n + m > OUTCAP`, which `c/kernel.c` DOES NOT SPELL, and the idiom audit prints that absence -- the missing spelling is the vulnerability. C checks the read and forgets the write, which is the shape of the real bignum miscount. THE `forbidden` ENTRIES ABOUT THE BUG CLASS ARE CONDITIONS, NOT TASTE, AND BOTH WERE SETTLED BY RUNS BEFORE ANY CELL WAS WRITTEN (NOTES.md 0a). A miscounted buffer index is a MEMORY-SAFETY bug only if the index is left alone: with the clamp `out[(i + j) % OUTCAP]` the identical miscount is exit 0 with ASan and UBSan both SILENT -- a wrong answer and no memory event at all, which is `p31`'s death. And with a product buffer allocated from `n + m` at run time the bug is unreachable by construction. A rung that took either route would still compute a product and would no longer model p46's bug, which is exactly what a `forbidden` entry is for. AND THE PROOF OBLIGATION THE RUNGS DO NOT DIFFER ON IS PINNED TOO. `required[2]` pins the 128-bit widening multiply-accumulate in every rung, because a 64-bit MAC would be a different algorithm; `forbidden[2]` excludes it by name. That step cannot overflow -- `(2^64-1)^2 + 2*(2^64-1)` is `2^128 - 1` exactly -- and NO RUNG CHECKS IT, in either language, at any rung. verus.rs must still discharge it, with a lemma, a `by (nonlinear_arith)`, a `by (compute)` and a `by (bit_vector)`. So p46 carries an obligation that costs real proof and zero instructions, beside one that costs trivial proof and every instruction the safe rungs pay: the two cost columns come apart inside one kernel. p46's numbers are still a spelling's numbers, and the in-contract spread was measured on BOTH sides BEFORE the rungs were chosen (NOTES.md 0b), because on this pattern the safe rung is CHEAPER than the unsafe one and that is exactly the shape that has been wrong in the flattering direction five times in this project. Three R3 spellings span 9490 Ir/call at (n, m) = (48, 48) and three R4 spellings span 2750; NEITHER SIDE IS DEGENERATE. The cheapest R4 found is cheaper than the cheapest R3 found, and it is INADMISSIBLE: it takes a mutable sub-slice, which the pinned vstd cannot specify (`slice_subrange` is `&[T]`-only and `ExSliceIndex::index_mut` has a `requires` and no `ensures`), so its R5 twin cannot discharge the postcondition. THAT, AND NOT SAFETY, IS WHY SAFE RUST WINS HERE, and it is `.memory/01-ladder.md` finding 14's mechanism with a number on it. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      " as int": "",
      "buf@": "buf",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 21
    },
    "twin_obligations": {
      "verus.rs": 24
    },
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 21 shipped + 3 for the twins of the three contracted trusted items (`buf_get_unchecked`, `arr_get_unchecked`, `arr_set_unchecked`).",
    "items": {
      "verus.rs": {
        "u64_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "limb": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "mac_t": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "mac_lo": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "mac_hi": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "row": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "rows": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "ofold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "zeros": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "window_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "bn_fold": {
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
        "arr_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_arr_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "arr_set_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_arr_set_unchecked": {
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
        "lemma_mac_fits": {
          "external": null,
          "requires": [],
          "ensures": [
            "mac_t(a, b, c, d) <= u128::MAX as nat"
          ]
        },
        "mac": {
          "external": null,
          "requires": [],
          "ensures": [
            "(r.0 as nat) + (r.1 as nat) * 0x1_0000_0000_0000_0000nat == mac_t(ai, bj, c, carry)",
            "r.0 == mac_lo(ai, bj, c, carry)",
            "r.1 == mac_hi(ai, bj, c, carry)"
          ]
        },
        "load_u64": {
          "external": null,
          "requires": [
            "p + 8 <= w@.len()"
          ],
          "ensures": [
            "r == u64_at(w@, p as int)"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == bn_fold(buf@, off as int, len as int)"
          ]
        },
        "main": {
          "external": null,
          "requires": [],
          "ensures": []
        }
      }
    },
    "unsafe_justifications": {
      "verus.rs": {
        "arr_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the scratch and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `T` is a legal thing to store in a `T` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` reads `i < N`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, then p12, p06, p14, p27, p38 and p22, and p46 is the eighth. It is the SAME generic item as p22's, character for character."
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
    "canonical": [
      "n_blob = bytes . len ( ) ;",
      "buf = bytes . as_slice ( ) ;",
      "acc = 0 ;",
      "if stride_w > 0 && stride_w <= n_blob",
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100. A difference of two runs of the same binary, so the one-shot loader terms that make whole-program Ir unquotable cancel -- not EXACTLY, see p01's copy of this note for the two surviving terms and their measured size. The two probe inputs have different work per call (576 vs 2304 MAC steps), so check.py can also assert d(Ir)/d(work) >= ALPHA. The floor is NOT declared here: check.py derives it from model.py's work_per_call, which is denominated in MAC steps with work_unit_bits = 64."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost. The window is taken through an out-of-line `subrange` function in unsafe.rs precisely so that it matches verus.rs's `vstd::slice::slice_subrange`, which is an ordinary call at O0 -- p19 measured that the inline `&v[i..j]` spelling lands the pair at `differ`. At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."
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
    "reason": "R4 and R5 ARE byte-identical at O3 (`identity` above pins `exact`), and that does not make Miri optional: `.memory/02-bench-rules.md` makes it mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. The reason byte-identity is not an excuse: R4 inherits R5's proof, and R5's proof is only as good as its trusted `ensures`, which need not be COMPLETE with respect to the operations the trusted body performs. Miri is the only backstop for that class, and here it has a specific job: p46's unchecked access is a WRITE, indexed by a sum of two loop counters whose bound comes from a byte pair read out of the buffer, so a wrong invariant corrupts the stack rather than merely reading it.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). p46's inputs are sized for it -- the largest blob is 12 416 bytes and a call touches at most 776 -- so no row is expected to block. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  }
}
```

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p46's payload is p19's, p36's, p22's, p38's, p47's
and eleven others':

```
word 0     u64  stride     # bytes per window
byte 8..   u8[] blob       # the windows
```

Nothing is a compile-time constant: `n_iters`, `stride` and `n_blob` all come
from the file, and so do both limb counts and every limb byte.

## Driver loop

Identical in all five rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` step 6 normalises every copy -- the C one included --
with `harness/dloop.py` and diffs each against the canonical token sequence
pinned above.

```
n_blob := bytes.len()
buf    := bytes.as_slice()
acc    := 0
if stride_w > 0 and stride_w <= n_blob:
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

### Why this does not evaporate

`k` is derived from `acc`, and `acc` is derived from the previous call's result.
Call *i+1* therefore cannot begin until call *i* has returned, so LLVM can
neither CSE the calls nor hoist them out of the loop, and no `black_box` or
`asm volatile` is needed -- which matters, because those two are not equally
strong barriers and using them would put a C-vs-Rust asymmetry in the driver.
The mechanism is the same arithmetic in both languages.

### The barrier is a multiply-shift, not a modulo

`k = (acc * nwin) >> 64` in 128-bit arithmetic -- Lemire's map from a uniform
`u64` onto `[0, nwin)`. p01's `spec.md` carries the measurement that motivated
the swap: a 64-bit `div` is ~0.1 % of `Ir` but 20-40 cycles of latency on the
serial dependency chain, i.e. a rung-independent additive constant that
compresses every cross-rung wall-clock ratio toward 1 -- the direction that
flatters this project's own headline.

It costs three ghost `proof` blocks in R5, all of them nonlinear; they erase, so
R5's driver loop is byte-identical to R4's.

/!\ **p46 is the first pattern whose KERNEL needs `lemma_u128_shr_is_div` too.**
In every other pattern that broadcast is there for the driver's barrier alone;
here the kernel splits its own 128-bit accumulator, so the same lemma is
load-bearing in two places at once.

### The one guard, and why it is weak on purpose

`stride_w > 0` is there for the division alone. A stride below the 8-byte header
is **not** rejected here: it reaches the kernel, whose own `len < 8` test returns
0. That makes the kernel's degenerate branch reachable from the measured domain
instead of being dead code the proof still has to discharge, and
`adversarial-tiny.bin` is the input that exercises it.

`payload_len` declaring more bytes than the file carries is caught earlier, in
`slb_load` / `driver::load`, which exits `5`; `adversarial-shortlen.bin` is that
input.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success; checksum on stdout |
| 2 | wrong argument count |
| 3 | cannot open input file |
| 4 | file shorter than the 16-byte header |
| 5 | `payload_len` exceeds the bytes present |
| 6 | allocation failure (C only) |
