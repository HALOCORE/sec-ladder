# p23 — in-place Hoare partition of a fixed scratch: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

`buf_len` is present in the C signature and ignored by both C rungs — p23's
bound is not the source buffer's length, it is the scratch's **live extent**,
carried by the two cursors. That is p03's, p06's and p12's shape and the
contrast with p02, p16 and p17, where the check the C rung skips is against a
length it was handed.

## Semantics

```
window = buf[off .. off+len)
nrec        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
data_start  = 4
record      = u32 LE nelem ; u8 pivot ; u8 pad[3] ; nelem bytes
SCR = 64                                     a compile-time constant

scr[SCR] = {0} ; acc = 0 ; p = 4
for rec in 0 .. nrec:
    if len - p < 8: break
    nelem = u32le(buf[off+p]) ; pv = buf[off+p+4] ; p += 8
    m = min(nelem, SCR)             <<< the CLAMP, present in EVERY rung
    if len - p < nelem: break
    memcpy(scr, buf + off + p, m)   <<< bulk, in EVERY rung
    p += nelem
    i = 0 ; j = m
    while i < j:
        while (i < j &&) scr[i] <= pv:     i++   <<< SAFETY LINE, half 1
        while (i < j &&) scr[j - 1] >= pv: j--   <<< SAFETY LINE, half 2
        if i < j: swap(scr[i], scr[j-1]) ; i++ ; j--
    for q in 0 .. m: acc = acc*31 + scr[q]     u64, wrapping
    acc = acc*31 + i                           the PARTITION POINT
return acc*31 + nrec
```

All arithmetic on `acc` is wrapping (`+64`, `*64`). C's `uint64_t` wraps by
definition (6.2.5p9), so R1 needs no special spelling; the Rust rungs use
`wrapping_mul` / `wrapping_add`.

### The bound on one cursor is the other cursor

This is the row's reason to exist, and it is a **new source of the bound** for
this tree rather than a fifteenth instance of an old one. Every earlier bound
here comes from outside the loop: a header field (p05, p07, p16, p17, p19,
p36), a compile-time capacity (p03, p06, p12), a live length (p04, p14). Here
`i` is bounded by `j`, `j` is bounded by `i`, and **both move**. The fact that
makes the pair sufficient — `j <= m <= SCR` — is established once, before the
loop, and never re-read.

Delete the two conjuncts and the loop's only remaining stopping condition is a
property of the **data**: an element strictly above the pivot for the upward
scan, one strictly below it for the downward one. Textbook Hoare partition gets
that property for free by taking the pivot *from* the sub-array; this kernel is
handed one, so it does not — and the code that relies on it looks identical.

### Three regimes upward, two downward

Write `hi` for *"some byte of `scr[0..m)` is strictly above `pv`"* and `lo` for
*"some byte of `scr[0..m)` is strictly below `pv`"*.

| scan | condition | what R1 does |
|---|---|---|
| upward | `hi` | stops where R1h stops — **agreement** |
| upward | `!hi`, but the stale tail `scr[m..SCR)` holds a byte above `pv` | stops **inside** the array past `j`: wrong answer, exit 0, ASan/UBSan clean, no panic in any Rust rung. `adversarial-inarray` |
| upward | no byte of `scr[0..SCR)` above `pv` | reads `scr[SCR]`. `adversarial-allbelow` |
| downward | `lo` | **agreement** (even when the only such byte is below the upward cursor — see `inputs/gen.py`) |
| downward | `!lo` | reaches `j == 0`, evaluates `scr[j-1]` with `j-1` **wrapped**, walks away from the frame, and the exchange that follows **writes** there. `adversarial-allabove` |

There is no in-bounds middle regime downward: the downward scan starts at the
top of the live prefix and never enters the stale tail.

### `m == 1` cannot be made benign, and that is the sharpest row

One byte cannot be both strictly above and strictly below the pivot, so a
one-element record has no sentinel in one direction whatever it contains.
Nothing about such an input is malformed. It ships as `adversarial-single`.
`m == 0` is safe for a structural reason instead: the outer `while (i < j)`
never runs.

### `<=` and `>=`, not `<` and `>`

Pinned for every rung. With `<=`/`>=` a run of elements equal to the pivot is
consumed by whichever scan reaches it first, so `j - i == 1` always collapses to
`i == j` and the cursors **meet** rather than cross; `i <= j` is then an
invariant rather than a hope, and it is what lets R5 carry `decreases j - i` at
all three loops. With `<`/`>` an element exactly equal to the pivot stops both
scans, the exchange is a no-op and `i` steps past `j`. Both spellings are in the
wild. This one is pinned so that no rung comparison moves on it.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == partition_fold(buf, off, len)
```

`harness/check.py` parses the block below, drives `model.py` against **every**
input file — `adversarial` included — and evaluates `requires` at every call the
benchmark actually makes and `ensures` against every value it actually returns.
That is the mechanical enforcement of `.memory/02-bench-rules.md` "Proof domain
must cover the measured domain" rules 1 and 3.

**The proof assumes nothing about the pivot.** `pv == 0` and `pv == 255` are
exactly the two values on which R1 leaves the scratch, and both are inside R5's
verified domain; so are `nrec`, `nelem` and every byte of the window.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. The pins exist because a green verification and
a green gate are, separately, evidence of very little; `patterns/p01-array-sum/spec.md`
tabulates which bypass each pin closes and that table is not repeated here.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == partition_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (partition_fold). p23's bindings are the READ-ONLY set p03, p06, p11, p12, p16, p17, p05 and p07 use and NOT p02's before/after shape: the destination is a LOCAL scr[SCR] inside the kernel, so no buffer crosses the signature and there is nothing for a scr_after binding to name. The security property is carried by the trusted accessors' `i < v@.len()` / `i < old(v)@.len()`, discharged at every scan step and at both stores of the exchange.",
  "idiom": {
    "required": [
      {
        "c": "THE SAFETY LINE, and the only thing c/kernel.c omits: the conjunct `i < j &&` on BOTH inner scan conditions in c/kernel_hardened.c. c/kernel.c omits exactly those two conjuncts and nothing else, so the scoped-absent audit pair this entry reports is on that rung and is correct.",
        "rust": "THE SAFETY LINE: the conjunct `i < j &&` on BOTH inner scan conditions, in all four Rust rungs. In Rust it is a SEMANTIC line and not a safety line -- rustc's bounds check is what makes the safe rungs safe and R5's proof is what makes the unsafe ones safe -- so no Rust-vs-Rust comparison moves on it; see the why key."
      },
      {
        "c": "THE COMPARISONS ARE NON-STRICT, in every rung including R1: `<= pv` on the upward scan and `>= pv` on the downward one.",
        "rust": "THE COMPARISONS ARE NON-STRICT, in every rung: `<= pv` on the upward scan and `>= pv` on the downward one."
      },
      {
        "c": "THE CLAMP, present in EVERY rung including R1, so the COPY is bounded in every rung and the bug is the two scans alone: `m = nelem < SCR ? nelem : SCR;` in both C rungs.",
        "rust": "THE CLAMP, present in EVERY rung, so the COPY is bounded in every rung and the bug is the two scans alone: `let m: usize = if nelem < SCR { nelem } else { SCR };` in all four Rust rungs."
      },
      {
        "c": "the scratch is a FIXED-SIZE LOCAL of SCR bytes, never an allocation and never a length from the file: `uint8_t scr[SCR];` in both C rungs.",
        "rust": "the scratch is a FIXED-SIZE LOCAL of SCR bytes, never an allocation and never a length from the file: `let mut scr: [u8; SCR] = [0; SCR];` in all four Rust rungs."
      },
      {
        "c": "...and it is ZERO-INITIALISED ON EVERY CALL, which is what makes the STALE TAIL -- and therefore the in-bounds middle regime -- deterministic and identical across rungs: `memset(scr, 0, sizeof scr);` in both C rungs.",
        "rust": "...and it is ZERO-INITIALISED ON EVERY CALL, which is what makes the STALE TAIL -- and therefore the in-bounds middle regime -- deterministic and identical across rungs: `[0; SCR];` in all four Rust rungs."
      },
      {
        "c": "the load into the scratch is a BULK copy in every rung, so the measured difference is the PARTITION and not the load: `memcpy(scr, buf + off + p, m);` in both C rungs.",
        "rust": "the load into the scratch is a BULK copy in every rung, so the measured difference is the PARTITION and not the load: `copy_from_slice(&src[from..from + n]);` in all four Rust rungs."
      },
      {
        "c": "THE PARTITION POINT IS FOLDED, not just the bytes -- without it a rung could return any index and no checksum would move: `acc = acc * 31 + (uint64_t)i;` in both C rungs.",
        "rust": "THE PARTITION POINT IS FOLDED, not just the bytes -- without it a rung could return any index and no checksum would move: `acc.wrapping_mul(31).wrapping_add(i as u64)` in all four Rust rungs."
      },
      {
        "c": "the cursor guards are SUBTRACTION-FIRST, so p <= len is maintained by the guards themselves and no subtraction can wrap: `len - p < 8` in both C rungs.",
        "rust": "the cursor guards are SUBTRACTION-FIRST, so p <= len is maintained by the guards themselves and no subtraction can wrap and the additive form does not verify: `len - p < 8` in all four Rust rungs."
      }
    ],
    "forbidden": [
      "`.position(`",
      "`.rposition(`",
      "`.select_nth_unstable`",
      "`.partition_point(`",
      "`.sort_unstable`",
      "`qsort(`"
    ],
    "why": "p23's declaration exists to hold seven things fixed across all seven cells so that exactly ONE thing varies. (1) THE SAFETY LINE IS TWO CONJUNCTS AND NOTHING ELSE. `diff c/kernel.c c/kernel_hardened.c` is two occurrences of `i < j &&` plus the comments that say so; every other character of the two cells -- signature, clamp, cursor guards, outer loop, exchange, fold, return -- is identical. So `c-gcc-h` minus `c-gcc` is the price of the scan guard and of nothing else. (2) THE COMPARISONS ARE NON-STRICT IN EVERY RUNG. `<=` / `>=` is what makes `j - i == 1` collapse to `i == j` instead of letting the cursors cross, which is what makes `i <= j` an invariant and lets R5 carry `decreases j - i` at all three loops; `<` / `>` is equally common in the wild and is a DIFFERENT program, whose partition point differs by one on any record containing a byte equal to its pivot. Pinning it is what stops a rung comparison moving on it. (3) THE CLAMP AND THE ZERO-FILL ARE IN EVERY RUNG INCLUDING R1. The clamp bounds the COPY, so every read of the SOURCE window is in bounds in every rung and the only out-of-bounds access any cell can make is the scan's; the zero-fill makes the STALE TAIL `scr[m..SCR)` deterministic, which is what makes the in-bounds middle regime -- `adversarial-inarray` -- reproducible rather than a property of whatever was on the stack. (4) THE BULK LOAD IS ONE SPELLING. p02's retraction is the precedent: one operator flips `bulk_calls` and 100% of the delta, so a rung that copied byte-at-a-time would be measuring the copy and calling it the partition. The RECEIVER is scoped 2-and-2 -- safe_naive.rs and safe_tuned.rs write `dst[..n]`, unsafe.rs and verus.rs write the `split_at_mut(n)` form -- because `..n` is a `RangeTo<usize>` and `RangeTo` has no `SliceIndexSpecImpl` at the pinned vstd, so `dst[..n]` cannot be VERIFIED at all and R4 must follow R5 to keep the identity pin. p06 measured that receiver's price at ZERO at -O3. (5) THE PARTITION POINT IS IN THE FOLD. A partition is a PERMUTATION of the loaded prefix, so the partitioned and the unpartitioned scratch are the same MULTISET on EVERY input -- not merely on some regime, which is the stronger form of p06's lesson -- and a sum- or xor-fold could not observe the partition at all. The fold is therefore an order-sensitive Horner chain over the full live extent, and the returned index is folded on top of it because the index is the kernel's other output and nothing else would move if a rung got it wrong. (6) WHAT IS DELIBERATELY LEFT FREE, and it is the operation the pattern is named for: THE EXCHANGE. safe_tuned.rs writes `scr.swap(i, j - 1)` and safe_naive.rs writes four indexed accesses, and no entry pins either, because the two are BYTE-IDENTICAL at -O3. MEASURED ON A PROBE AND SAID SO: `.temp/t101/cost23.rs`'s `k_r2` and `k_r3c` differ only in that one spelling and have the same padding-stripped normalised disassembly (219 instructions, `5dca9d30a43c`) and the same marginal `Ir` to the instruction at three separate pivot ranks. A probe measures a SLOPE and its intercept is a property of the probe (`.memory/03-measurement.md`), so what transfers is the EQUALITY, not the 219. Pinning a spelling whose price is zero would buy nothing and would exclude an idiom for no reason. (7) WHAT IS FORBIDDEN, AND ITS PRICE IS PUBLISHED. `.position(` / `.rposition(` is the most idiomatic Rust for `advance while`, and it is excluded IN EVERY RUNG rather than in some -- a whole-pattern exclusion, which stays visible and keeps the two sides equal, unlike the scoped kind `.memory/01-ladder.md` caught on p13. The reason is the reason to publish: measured ON A PROBE against a fixed driver (`.temp/t101/cost23.rs`, marginal whole-program `Ir`/call, `-O` isolated, debug-assertions off), the iterator-scan spelling is the DEAREST R3 found at a median pivot (4208.00 against 3141.00 for the shipped spelling) and the CHEAPEST at the minimum-rank pivot (2812.30 against 3094.30). THE TRANSFERABLE CLAIM IS THE ORDERING FLIP, NOT THE FOUR NUMBERS: a rung built on it would make p23's safe-side headline a function of WHICH BAND was measured rather than of the pattern. ../NOTES.md 9 has the table. `.select_nth_unstable` and `.partition_point(` are std's own partitioning primitives and would delete the kernel; `.sort_unstable` and `qsort(` would replace it with a different algorithm entirely. NOTHING HERE PINS A RUNG'S ADVANTAGE. R2-vs-R3 is measured at matched semantics with three levers priced separately (../NOTES.md 9), and the R4 side names a lever it did NOT take -- resliced-window addressing, cheaper than the shipped R4 by 6.00 probe-`Ir`/call at all three probe bands, held out because R4 must be byte-identical to R5 and `split_at` on the window has not been shown to verify at the pinned vstd. That is `.memory/01-ladder.md`'s rule for a fixed-by-fiat R4 endpoint, and saying it here is the whole of the compliance. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
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
      "verus.rs": 16
    },
    "twin_obligations": {
      "verus.rs": 19
    },
    "obligations_note": "16 = SCR 1 + part 1 + fold_scr 1 + walk 1 + scr_load 1 + kernel 6 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained, and the zero terms are checkable the same way: u32_at, nrec_at, zero_scr, load_into, swap2 and partition_fold are NON-RECURSIVE spec fns and report 0; part, fold_scr and walk are RECURSIVE and carry one termination query each; buf_get_unchecked, scr_get_unchecked, scr_set_unchecked, load_input and emit are external_body and report 0. THE COUNT IS LOWER THAN p06's 18 AND THE PATTERN IS HARDER, which is worth one sentence: p06 needs THREE proof fns because three reverses are not syntactically a rotation, and p23 needs ZERO because `part` is written in the shape the loop nest moves in -- its three cases ARE the upward scan step, the downward scan step and the exchange. The proof burden of this pattern is therefore in the INVARIANT (one sentence, repeated at three loops) and not in a lemma library, which is the opposite of where TASK_047 expected a permutation-flavoured obligation to put it.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. 16 shipped + 3, one per twin: slb_twin_buf_get_unchecked, slb_twin_scr_get_unchecked and slb_twin_scr_set_unchecked, each a single-query body. p23 ships no safe_naive_verus.rs, so there is no second file to count.",
    "unsafe_justifications": {
      "verus.rs": {
        "scr_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `u8` is a legal thing to store in a `u8` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [u8; 64]` reads `i < 64`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second and p06 the third. On p23 the item carries the WRITE half of the bug: it is called twice per exchange, and the store R1 gets wrong is the one it reaches after its DOWNWARD scan has wrapped `j` -- so this `requires` is what excludes an out-of-bounds write that a missing READ guard, one loop earlier, made reachable. A second conjunct `old(v)@.len() == 64` is deliberately NOT written: for a `&mut [u8; 64]` it is a TAUTOLOGY discharged from the parameter type alone by vstd's `array_len_matches_n`, and p03's gate run refused exactly that draft (p03 NOTES.md 5b)."
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
        "load_into": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "swap2": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "part": {
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
        "partition_fold": {
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
            "r == partition_fold(buf@, off as int, len as int)"
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100. A difference of two runs of the same binary, so the one-shot loader terms that make whole-program Ir unquotable cancel. They do NOT cancel EXACTLY -- patterns/p01-array-sum/spec.md's copy of this note has the two surviving terms and their measured sizes, and nothing about p23 changes them. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call, and the two probe inputs have different work per call (201 vs 154 window bytes) so it can also assert d(Ir)/d(work) >= alpha. p23's floor is TIGHTER than p06's on the same unit, because a partition's two scans together visit each live byte exactly once where three reverses visit it about twice; model.py's work_per_call docstring gives the byte-visit arithmetic on both inputs and it is strict on both."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost, on the first kernel in this project whose loop nest is bounded by ITSELF -- two cursors that bound each other, with no length available to either. The byte-identity result covers a kernel with five loops, two of them data-dependent scans whose trip counts are a function of the input bytes, one mutating a fixed-size array through a trusted setter called twice per exchange, three recursive spec functions and ZERO nonlinear arithmetic and ZERO proof fns. At O0 the crate names differ in length so the call displacements differ -- link layout, not codegen -- which is p06's and p01's O0 row exactly."
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
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be COMPLETE with respect to the operations the trusted body performs. On p23 there are two stronger reasons. First, one of the three accessors WRITES and is called twice per exchange, so a trusted setter whose body also touched a neighbouring slot would pass every Verus stage with its contract, twin and pins unchanged. Second, and specific to this row: both of R1's overruns are READS that escalate, and the downward one WRAPS `j - 1` through `usize`, which is exactly the shape a provenance-checking interpreter sees and a bounds proof about `scr` does not. Miri on unsafe.rs is the only backstop for either class here, and byte-identity propagates R4's reads to R5 rather than excusing them.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). p23's `large.bin` is 7.7 MB of records that the driver walks one byte at a time, so that row may exceed check.py's MIRI_TIMEOUT under interpretation; a timeout is recorded as a BLOCKED row for that input, never as a pattern failure, and the verdict then reads PASS-WITH-BLOCKED-ROWS. The size of an input file must not decide whether the gate is green."
  }
}
```

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p23's payload is:

```
word 0     u64  stride     bytes per window; the kernel walks one window
byte 8..   u8[] blob       the windows; n_blob = payload_len - 8
```

Nothing is a compile-time constant: `n_iters`, `stride`, `nrec`, `nelem` and
every pivot come from the file.

## Driver loop

Identical in all five rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` diffs the copies.

```
n_blob := bytes.len()
buf    := bytes.as_slice()
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

`off` is derived from `acc`, and `acc` is derived from the previous call's
result, so call *i+1* cannot begin until call *i* has returned and LLVM can
neither CSE the calls nor hoist them; no `black_box` and no `asm volatile` is
needed, which matters because those two are not equally strong barriers and
using them would put a C-vs-Rust asymmetry in the driver.

`stride_w >= 4` is the guard, because p23's window header is the 4-byte `nrec`
field. `adversarial-stride3.bin` attacks it. There are **two** conjuncts and not
p17's three: p23's cursor guards are subtraction-first and maintain `p <= len`
themselves.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success; checksum on stdout |
| 2 | wrong argument count |
| 3 | cannot open input file |
| 4 | file shorter than the 16-byte header |
| 5 | `payload_len` exceeds the bytes present |
| 6 | allocation failure (C only) |
