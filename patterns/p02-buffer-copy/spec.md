# p02 — length-prefixed record copy: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *src, size_t src_len, size_t src_off, uint8_t *dst, size_t dst_cap)` |
| R2/R3/R4/R5 Rust | `fn kernel(src: &[u8], src_off: usize, dst: &mut [u8]) -> u64` |

Five C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, `&mut [u8]` is a pointer
and a length, and C spells each pair out. This is the opposite of p01, where the
C kernel genuinely could not know the array's length and that asymmetry was the
finding. Here C is handed both sizes and R1 ignores them — which is the more
common and more damning shape of CWE-787, and it makes R1-vs-R1h a comparison
with the calling convention, the argument count and the register allocation all
held fixed. The only difference between those two cells is three lines of check.

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a five-argument call into a three-argument one. See "Driver loop".)

## Semantics

```
len = src[src_off] + 256 * src[src_off + 1]              # little-endian u16

if len <= dst_cap and len <= src_len - (src_off + 2):     # the record fits
    dst[0 .. len)  := src[src_off+2 .. src_off+2+len)
    return  the wrapping sum of the bytes now in dst[0 .. len)
else:                                                     # reject, untouched
    return 0
```

Four things about that are load-bearing.

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug. Edit both or neither (TASK_016_REVIEW m2).

- **The kernel is total in `len`.** Every one of the 65 536 values a `u16`
  prefix can express is handled. `.memory/02-bench-rules.md`: the attacker
  quantity is an *argument*, not an assumption. A contract that assumed
  `len <= dst_cap` would verify, would pass the gate, and would have assumed the
  vulnerability away. **R1 is the exception and it is the point**: `c/kernel.c`
  is total in nothing — it is defined only for the `len` values that happen to
  fit — and that is the CWE-787 being modelled, not a rung to repair.
- **The check is written subtraction-first.** `len > src_len - (src_off + 2)`,
  not `src_off + 2 + len > src_len`: the additive form can overflow `size_t`
  and wave the attack through. The subtraction cannot underflow, because
  `src_off + 2 <= src_len` is the structural precondition (below). Every rung
  that *has* the test spells it identically — R1 has no test at all, which is
  the bug; R1h is R1 plus those three lines.

  **This spelling has a measured codegen cost in R2, and it is a finding rather
  than a reason to change it** (`NOTES.md` §3a). Subtraction-first leaves LLVM
  unable to prove the copy loop's index in bounds, so rustc never rewrites
  R2's byte loop into a `memcpy`: one operator flips `bulk_calls []` →
  `['memcpy@GLIBC_2.14']` and 118 kernel instructions → 87, and that difference
  is 100% of R2's published delta. The additive form is the one `spec.md`
  forbids, so the honest reading is *the sound spelling of an overflow check
  costs rustc an idiom recognition*, not *bounds checks are expensive*. R3, R4
  and R5 write the same subtraction-first check and pay nothing, because their
  copies are not index-by-index.
- **The prefix is decoded with `+`, not `|`.** `b0 + 256*b1` and
  `b0 | (b1 << 8)` are the same function on bytes and LLVM emits the same
  instruction for both, but the additive form needs no bit-vector reasoning in
  R5. Choosing the spelling that is cheaper to prove is legitimate; choosing a
  weaker *specification* would not be.
- **The result is folded over `dst`, after the copy, not over `src`.** So the
  copy cannot be dead-coded: the return value depends on the bytes having
  actually arrived. `ensures` states the sum over `src`, which is what makes the
  postcondition also assert that the copy was correct.

Wrapping addition, as in p01, so the kernel has no precondition on *values* and
every measured input is inside the verified domain by construction.

## Contract

```
requires:  src_off + 2 <= src_len
ensures:   result == copy_sum(src, src_off, dst_after_len)
           dst_after == copy_dst(dst_before, src, src_off)
```

**Two clauses, not three.** There was a third, `dst_after_len == dst_len`, and
`harness/check.py` step 5c deleted it and found the file still verified with 0
errors: `copy_dst` returns a sequence of `dst_before`'s length on both branches,
so the security clause already entails it. `copy_bytes`'s trusted contract lost
its own copy of the same statement for the same reason. Saying an entailed fact
a second time does not strengthen a contract; it inflates the TCB tally, gives a
reviewer two claims to judge where there is one, and lets a later weakening of
the strong clause hide behind the weak one.

`requires` is the whole of it: **the two prefix bytes are inside the source
buffer.** That is structural — it is about the shape of the buffers the driver
built, not about their contents — so it holds on every input this benchmark
runs, `adversarial-*` included, and `harness/check.py` evaluates it at every one
of the 220 032 kernel calls to prove that it does.

The security property is in the `ensures`, and specifically in the second
clause, which pins the **entire** destination sequence rather than the copied
prefix:

> `dst_after == copy_dst(dst_before, src, src_off)`, where `copy_dst` is the
> record followed by *the bytes that were already there*.

So it says both "the record landed where it should" and "not one byte outside
`dst[0..len)` moved" — and on a record that does not fit, `copy_dst` is the
identity, i.e. *nothing at all was written*. That is the clause R1 violates.

`harness/check.py` derives these three Python expressions from `verus.rs`'s own
clause text through the `verus.translate` table below, drives `model.py` over
**every** input file, and evaluates them at every call. `dst_before`/`dst_after`
are the whole buffer, before and after, as `bytes`.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p02's payload is:

```
word 0     u64  cap        # destination buffer capacity, in bytes
word 1     u64  stride     # bytes per record
byte 16..  u8[] src        # the record blob; n_src = payload_len - 16
```

decoded by `slb_head2_u64_bytes` / `driver::head2_u64_bytes` /
`slb.head2_u64_bytes` — one function per language, added to `common/` for this
pattern. Every record is `stride` bytes: a little-endian `u16` length prefix and
then that many data bytes. Nothing is a compile-time constant: `n_iters`, `cap`,
`stride`, `n_src` and every length prefix come from the file.

`cap` is an attacker-controlled allocation size, so both drivers reject it
outside `1 ..= SLB_MAX_CAP` (64 MiB) **before allocating**, with the same exit
code. Otherwise C's `calloc` returns `NULL` where Rust's allocator aborts, and a
driver difference reads as a rung difference.

## Driver loop

Identical in all six rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` normalises every copy — the C one included — and
diffs it against `driver.canonical` below.

```
n_src := bytes.len()
src   := bytes
dst   := dbuf                        # cap zeroed bytes, allocated before the region
acc   := 0
if stride_w >= 2 and stride_w <= n_src:
    stride := stride_w as usize
    nrec   := (n_src / stride) as u64
    it     := 0
    while it < n_iters:
        k   := ((acc as u128 * nrec as u128) >> 64) as usize
        r   := kernel(src, k * stride, dst)
        acc := acc *64 31 +64 r
        it  := it + 1
emit(acc)
```

### Why this does not evaporate

Same mechanism as p01: `k` is derived from `acc`, and `acc` from the previous
call's result, so call *i+1* cannot begin until call *i* has returned. Nothing
to CSE, nothing to hoist, no `black_box` and no `asm volatile` — the same
arithmetic in both languages, so neither gets a stronger barrier than the other.
`off = (acc * nrec) >> 64` is Lemire's map onto `[0, nrec)`; see p01's `spec.md`
for why it is a multiply-shift and not a modulo.

The record index also means every call reads a *different* 4 KiB of an 8 MiB
blob on `large`, which is what makes that input memory-bound.

### Why the structural precondition holds

`k < nrec` because `(acc * nrec) >> 64 < nrec` for `nrec >= 1`, and
`k * stride + 2 <= n_src` because `k <= nrec - 1` and `nrec * stride <= n_src`
(integer division rounds down). Both steps are nonlinear, so R5 spells them out
in ghost code; that is where three of this pattern's nine obligations live.

### The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(src, n_src, k * stride, dst, dst_cap)` and the Rust
loop calls `kernel(src, k * stride, dst)`. `driver.aliases` cannot reconcile
that — both sides of an alias are a dotted identifier path, so an alias renames
and can do nothing else. `driver.call_args` declares which argument *positions*
of a named call are the canonical ones (`{"c": {"kernel": [0, 2, 3]}}`), and
`harness/dloop.py` refuses to drop anything that is not a single bare
identifier, so no prefetch, no side effect and no extra statement can hide in
the arguments the diff stops looking at. Keeping the wrong positions raises
rather than quietly matching.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes;
the two entries that are new here:

| pin | why |
|---|---|
| `driver.call_args` | the C kernel takes the two slice lengths Rust carries inside `&[u8]`, so the C call has five arguments and the Rust call has three. Declared positionally and checked structurally (above). |
| `miri.required: true` | R4 and R5 are byte-identical at `-O3`, so `.memory/02-bench-rules.md` does **not** require Miri here. It is switched on anyway: this is the project's first rung-4 with raw pointer arithmetic (`copy_nonoverlapping`, `as_ptr().add()`), and a UB test over all nine inputs costs a minute. Turning it off would be a weakening. |

```slb-contract
{
  "kernel": "kernel(src: &[u8], src_off: usize, dst: &mut [u8]) -> u64",
  "model": "model.py",
  "requires": ["src_off + 2 <= src_len"],
  "ensures": ["result == copy_sum(src, src_off, dst_after_len)",
              "dst_after == copy_dst(dst_before, src, src_off)"],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (src/src_off/src_len/dst_len/dst_after_len/dst_before/dst_after/result) plus the helpers it supplies (copy_dst, copy_sum). dst_before and dst_after are the WHOLE destination buffer as bytes: the security property is an equality on all of it, not on the copied prefix.",

  "idiom": {
    "required": [
      {"c": "the fit check is subtraction-first -- `len > src_len - (src_off + 2)` -- spelled identically in every rung that HAS one. R1 (`c/kernel.c`) has no fit check at all: it casts `src_len` and `dst_cap` to `(void)` and that omission IS the bug this pattern models. R1h is R1 plus the three-term check `len > dst_cap || len > src_len - (src_off + 2)` and nothing else",
       "rust": "the fit check is subtraction-first -- `len > src.len() - (src_off + 2)` -- and every Rust rung HAS one: all four write the three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` and nothing else. This entry is per-language because the C kernel takes `src_len` and `dst_cap` as parameters and the Rust signature does not carry them; the operands are the same two values. A Rust rung that spells the guard the C way instead is OUT of contract even though it is byte-identical to the shipped cell (TASK_019, `md5_fn e207ec6c8697...`)"},
      "the u16 prefix is decoded with `+`, not `|`",
      "the result is folded over dst AFTER the copy, not over src",
      "the kernel is total in len: all 65536 values a u16 prefix can express are handled -- in every rung EXCEPT R1, which is defined only for the values that happen to fit and overruns `dst` for the rest. R1's partiality is the CWE-787 the pattern exists to exhibit (ASan fires on `adversarial-overrun.bin`, NOTES.md 1); do not 'fix' it",
      "R2 copies index-by-index; R3 reslices both sides once and copies with copy_from_slice"
    ],
    "forbidden": [{"c": "the additive check `src_off + 2 + len > src_len`",
                   "rust": "the additive check `src_off + 2 + len > src.len()`"}],
    "why": "the additive form can overflow size_t and wave the attack through, so it is the spelling this pattern exists to reject. The `+` decode and the `|` decode are the same function and lower to the same instruction; `+` is chosen because it needs no bit-vector reasoning in R5, which is a cheaper PROOF and not a weaker specification. Folding dst after the copy is what stops the copy being dead code. The last required entry is the one that already cost this pattern a retraction and must not be quietly 'fixed': R2's index-by-index copy is why rustc never forms a memcpy there, one operator flips `bulk_calls []` to `['memcpy@GLIBC_2.14']` and 118 kernel instructions to 87, and that difference was 100% of R2's retracted delta (NOTES.md 3a). Swapping a bulk copy into R2, or an indexed copy into R3, deletes p02's only decomposition and its finding with it. RESTATED in this hashed block at TASK_016 from the 'Four things about that are load-bearing' prose above -- restated, not moved: the prose is still there, says the same thing, and THIS block is the authoritative copy of it (TASK_016_REVIEW m2). Whoever edits one edits the other. TASK_016 did not measure a spelling spread for p02; TASK_019 did, and it is NOTES.md 10a. Three admissible respellings of the two things this block leaves free -- the u16 header read and the fold's spelling -- all identical to shipped R3 on 77/77 committed inputs, and SWEPT over 16 consecutive record lengths (two full cycles of the 8-periodicity NOTES.md 3b measured) with zero residual: `r3_splitat` is byte-identical to the shipped kernel, `r3_forloop` is 1-2 Ir/call cheaper and `r3_hdrslice` is 3-4 cheaper. So p02's published `R3ship - R4ship = +10` (`+8` at `len` a multiple of 8) is an UPPER BOUND whose measured in-contract minimum is `+6` / `+5`. And the exclusion in `forbidden[0]` costs that floor NOTHING: the forbidden additive guard is 3 Ir/call cheaper than shipped R3, FLAT, while the IN-CONTRACT `r3_hdrslice` is 4 cheaper at 14 of the 16 swept lengths and 3 at the other 2, so the cheapest admissible spelling is strictly cheaper than the cheapest forbidden one at 14 of 16 lengths and ties at the rest. Contrast p16, where the analogous exclusion makes the published tax 4.5x LARGER: an exclusion's cost to the pattern's own headline is measurable, and is the test that separates a pin from a self-certification. The R4 side has not been searched in contract, so `+6` is an R3-side bound and not p02's safety number. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 Ir/call flat and p02's by 3 to 4, so `R3ship - R4ship` is an UPPER BOUND on the in-contract safety tax and never the tax itself. Every pattern owes an in-contract spelling spread beside its headline; p16 and p17 have one from TASK_018 and p02 from TASK_019 (their NOTES.md 10a) and p05 from TASK_021 (its NOTES.md 14, which also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep); p01 and p08 do not."
  },

  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "final(dst)@.len()": "dst_after_len",
      "old(dst)@.len()": "dst_len",
      "final(dst)@": "dst_after",
      "src@.len()": "src_len",
      "old(dst)@": "dst_before",
      " as int": "",
      "src@": "src",
      "=~=": "==",
      "r": "result"
    },
    "obligations": {"verus.rs": 9},
    "twin_obligations": {"verus.rs": 12},
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 9 shipped + 3: slb_twin_get_unchecked (1 query) and slb_twin_copy_bytes (1 for the fn + 1 for its loop body). Pinned for the same reason the shipped count is: `tv > base_v` only says something extra compiled, and a twin that quietly lost its loop body, or an item that exists only under the cfg, moves this number and nothing else.",
    "items": {
      "verus.rs": {
        "rec_len":      {"external": null, "requires": [], "ensures": []},
        "fits":         {"external": null, "requires": [], "ensures": []},
        "copy_dst":     {"external": null, "requires": [], "ensures": []},
        "sum_bytes":    {"external": null, "requires": [], "ensures": []},
        "copy_sum":     {"external": null, "requires": [], "ensures": []},
        "lemma_sum_congruent": {
            "external": null,
            "requires": ["0 <= n",
                         "forall|j: int| 0 <= j < n ==> #[trigger] a[fa + j] == b[fb + j]"],
            "ensures": ["sum_bytes(a, fa, n) == sum_bytes(b, fb, n)"]},
        "get_unchecked": {"external": "verifier::external_body",
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "slb_twin_get_unchecked": {"external": null,
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "copy_bytes":   {"external": "verifier::external_body",
                         "requires": ["from + n <= src@.len()",
                                      "n <= old(dst)@.len()"],
                         "ensures": ["final(dst)@ =~= src@.subrange(from as int, from + n as int) + old(dst)@.subrange( n as int, old(dst)@.len() as int, )"]},
        "slb_twin_copy_bytes": {"external": null,
                         "requires": ["from + n <= src@.len()",
                                      "n <= old(dst)@.len()"],
                         "ensures": ["final(dst)@ =~= src@.subrange(from as int, from + n as int) + old(dst)@.subrange( n as int, old(dst)@.len() as int, )"]},
        "load_input":   {"external": "verifier::external_body",
                         "requires": [], "ensures": []},
        "emit":         {"external": "verifier::external_body",
                         "requires": [], "ensures": []},
        "kernel":       {"external": null,
                         "requires": ["src_off + 2 <= src@.len()"],
                         "ensures": ["r == copy_sum(src@, src_off as int, final(dst)@.len() as int)",
                                     "final(dst)@ =~= copy_dst(old(dst)@, src@, src_off as int)"]},
        "main":         {"external": null, "requires": [], "ensures": []}
      }
    }
  },

  "driver": {
    "statements": 13,
    "c_source": "c/main.c",
    "regions": ["safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs",
                "c/main.c"],
    "aliases": {"c": {"n_body": "bytes.len()",
                      "bytes": "bytes.as_slice()",
                      "dbuf": "dbuf.as_mut_slice()",
                      "inp.n_iters": "n_iters"}},
    "call_args": {"c": {"kernel": [0, 2, 3]}},
    "canonical": [
      "n_src = bytes . len ( ) ;",
      "src = bytes . as_slice ( ) ;",
      "dst = dbuf . as_mut_slice ( ) ;",
      "acc = 0 ;",
      "if stride_w >= 2 && stride_w <= n_src",
      "{",
      "stride = stride_w ;",
      "nrec = n_src / stride ;",
      "it = 0 ;",
      "while it < n_iters",
      "{",
      "k = acc * nrec >> 64 ;",
      "r = kernel ( src , k * stride , dst ) ;",
      "acc = acc * 31 + r ;",
      "it = it + 1 ;",
      "}",
      "}"
    ]
  },

  "collapse": {
    "probe_inputs": ["small.bin", "large.bin"],
    "probe_iters": [100, 200],
    "note": "work_per_call is BYTES COPIED (61 on small, 4092 on large) and model.py declares min_ir_per_work = 0.0625 Ir per byte beside it, replacing the harness default of 0.25. The default is derived in 64-bit-lane terms and is unsound for a byte: glibc memcpy moves a byte in 0.104 instructions on this box (re-measured at TASK_006), so a bulk-copy kernel scores 0.118 and 0.25 would fail it at 0.47x while it is the fastest correct implementation there is. 0.0625 is the fused AVX-512 lower bound -- load, store, vpsadbw, vpaddq per 64-byte lane. The shipped rungs measure 2.25 to 6.67 Ir/byte, 36x to 107x clear, because the byte fold does not vectorise in rustc. Neither the rate nor the unit is settable from this file: both live in model.py, which the gate drives in a sandbox, and the gate prints the rate and its justification in every verdict."
  },

  "identity": [
    {"a": "unsafe", "b": "verus", "O0": "norel", "O3": "exact",
     "why": "R4 == R5: the proof licenses unsafe code at zero cost, on a kernel with a raw copy_nonoverlapping and a real proof (9 obligations, an induction lemma, two nonlinear steps in the driver) rather than p01's single get_unchecked. At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."}
  ],

  "miri": {
    "pair": ["unsafe", "verus"],
    "sources": ["unsafe.rs"],
    "required": true,
    "reason": "R4 and R5 ARE byte-identical at O3. That used to make Miri optional; since TASK_010 `.memory/02-bench-rules.md` makes it mandatory for any pattern with a trusted `unsafe` item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs (TASK_009_REVIEW x4). It was required here anyway even under the old policy: R4 is the project's first rung-4 carrying raw pointer arithmetic (`src.as_ptr().add(src_off + 2)`, `dst.as_mut_ptr()`, `copy_nonoverlapping`), where p01's was a single `get_unchecked`, and the adversarial inputs drive it down the rejection path that the proof is about. A UB test over all nine inputs costs about a minute.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed -- but note the pattern is NOT exempt from the policy on identity grounds alone in spirit: R4 here is materially more unsafe than p01's."
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
| 7 | declared `cap` is 0 or above `SLB_MAX_CAP` |

## Degenerate shapes

The guard `stride_w >= 2 && stride_w <= n_src` is the driver's whole input
validation and it is what `adversarial-stride1` attacks: a stride below 2 cannot
hold a length prefix, and a stride above `n_src` leaves no whole record, so
`nrec` would be 0 and `k` would have nothing to index. When it fails the loop is
skipped entirely — rather than entered and broken out of, which would put a
branch in the measured loop — and the driver prints `0`. `n_iters == 0` is
handled by the `while` itself. Comparison is in `u64` *before* the `as usize`
cast, so a truncating driver cannot sneak a 2^40 stride past it.

`cap` outside `1 ..= SLB_MAX_CAP` exits 7 before anything is allocated;
`payload_len` declaring more bytes than the file carries is caught earlier still,
in `slb_load` / `driver::load`, which exits 5.
