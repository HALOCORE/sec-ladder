# p23-partition — results

Generated 2026-08-26T15:50:26Z from `results/p23-partition.json` (git `ff625eab1d5e`, working tree dirty).

## Toolchain

- **gcc**: gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
- **clang**: clang version 22.1.6 (https://github.com/llvm/llvm-project fc4aad7b5db3fff421df9a9637605b9ca5667881)
- **rustc**: rustc 1.97.1 (8bab26f4f 2026-07-14)
- **rustc_llvm**: LLVM version: 22.1.6
- **verus**: verus binary : /home/apt/tools/verus/verus
- **valgrind**: valgrind-3.27.1
- **objdump**: GNU objdump (GNU Binutils for Ubuntu) 2.42
- **host**: Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz, governor `powersave`

## Inputs

| file | n_iters | declared payload | present | truncated | model |
|---|---:|---:|---:|---|---|
| adversarial-allabove.bin | 8 | 52 | 52 | False | n_iters=8 stride=44 n_blob=44 nwin=1 calls=8 work/call=44B san=fires truncated=False expected=6934588237357035520 |
| adversarial-allbelow.bin | 8 | 52 | 52 | False | n_iters=8 stride=44 n_blob=44 nwin=1 calls=8 work/call=44B san=fires truncated=False expected=7996702914333622784 |
| adversarial-both.bin | 8 | 92 | 92 | False | n_iters=8 stride=84 n_blob=84 nwin=1 calls=8 work/call=84B san=fires truncated=False expected=4195944775957882752 |
| adversarial-inarray.bin | 8 | 92 | 92 | False | n_iters=8 stride=84 n_blob=84 nwin=1 calls=8 work/call=84B san=clean truncated=False expected=4207864700635266816 |
| adversarial-single.bin | 8 | 21 | 21 | False | n_iters=8 stride=13 n_blob=13 nwin=1 calls=8 work/call=13B san=fires truncated=False expected=2705683097473408 |
| adversarial-stride3.bin | 8 | 38 | 38 | False | n_iters=8 stride=3 n_blob=30 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| degenerate.bin | 8 | 166 | 166 | False | n_iters=8 stride=158 n_blob=158 nwin=1 calls=8 work/call=158B san=clean truncated=False expected=3110811304049497088 |
| large.bin | 20,000 | 7,700,008 | 7,700,008 | False | n_iters=20000 stride=154 n_blob=7700000 nwin=50000 calls=20000 work/call=154B san=clean truncated=False expected=11079489060389925304 |
| small.bin | 60,000 | 12,872 | 12,872 | False | n_iters=60000 stride=201 n_blob=12864 nwin=64 calls=60000 work/call=201B san=clean truncated=False expected=7635784890701216837 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE SAFETY LINE, and the only thing c/kernel.c omits: the conjunct `i < j &&` on BOTH inner scan conditions in c/kernel_hardened.c. c/kernel.c omits exactly those two conjuncts and nothing else, so the scoped-absent audit pair this entry reports is on that rung and is correct.
  - `rust` — THE SAFETY LINE: the conjunct `i < j &&` on BOTH inner scan conditions, in all four Rust rungs. In Rust it is a SEMANTIC line and not a safety line -- rustc's bounds check is what makes the safe rungs safe and R5's proof is what makes the unsafe ones safe -- so no Rust-vs-Rust comparison moves on it; see the why key.
- **required** — *per language:*
  - `c` — THE COMPARISONS ARE NON-STRICT, in every rung including R1: `<= pv` on the upward scan and `>= pv` on the downward one.
  - `rust` — THE COMPARISONS ARE NON-STRICT, in every rung: `<= pv` on the upward scan and `>= pv` on the downward one.
- **required** — *per language:*
  - `c` — THE CLAMP, present in EVERY rung including R1, so the COPY is bounded in every rung and the bug is the two scans alone: `m = nelem < SCR ? nelem : SCR;` in both C rungs.
  - `rust` — THE CLAMP, present in EVERY rung, so the COPY is bounded in every rung and the bug is the two scans alone: `let m: usize = if nelem < SCR { nelem } else { SCR };` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the scratch is a FIXED-SIZE LOCAL of SCR bytes, never an allocation and never a length from the file: `uint8_t scr[SCR];` in both C rungs.
  - `rust` — the scratch is a FIXED-SIZE LOCAL of SCR bytes, never an allocation and never a length from the file: `let mut scr: [u8; SCR] = [0; SCR];` in all four Rust rungs.
- **required** — *per language:*
  - `c` — ...and it is ZERO-INITIALISED ON EVERY CALL, which is what makes the STALE TAIL -- and therefore the in-bounds middle regime -- deterministic and identical across rungs: `memset(scr, 0, sizeof scr);` in both C rungs.
  - `rust` — ...and it is ZERO-INITIALISED ON EVERY CALL, which is what makes the STALE TAIL -- and therefore the in-bounds middle regime -- deterministic and identical across rungs: `[0; SCR];` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the load into the scratch is a BULK copy in every rung, so the measured difference is the PARTITION and not the load: `memcpy(scr, buf + off + p, m);` in both C rungs.
  - `rust` — the load into the scratch is a BULK copy in every rung, so the measured difference is the PARTITION and not the load: `copy_from_slice(&src[from..from + n]);` in all four Rust rungs.
- **required** — *per language:*
  - `c` — THE PARTITION POINT IS FOLDED, not just the bytes -- without it a rung could return any index and no checksum would move: `acc = acc * 31 + (uint64_t)i;` in both C rungs.
  - `rust` — THE PARTITION POINT IS FOLDED, not just the bytes -- without it a rung could return any index and no checksum would move: `acc.wrapping_mul(31).wrapping_add(i as u64)` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the cursor guards are SUBTRACTION-FIRST, so p <= len is maintained by the guards themselves and no subtraction can wrap: `len - p < 8` in both C rungs.
  - `rust` — the cursor guards are SUBTRACTION-FIRST, so p <= len is maintained by the guards themselves and no subtraction can wrap and the additive form does not verify: `len - p < 8` in all four Rust rungs.
- **FORBIDDEN** — `.position(`
- **FORBIDDEN** — `.rposition(`
- **FORBIDDEN** — `.select_nth_unstable`
- **FORBIDDEN** — `.partition_point(`
- **FORBIDDEN** — `.sort_unstable`
- **FORBIDDEN** — `qsort(`

> **Why**: p23's declaration exists to hold seven things fixed across all seven cells so that exactly ONE thing varies. (1) THE SAFETY LINE IS TWO CONJUNCTS AND NOTHING ELSE. `diff c/kernel.c c/kernel_hardened.c` is two occurrences of `i < j &&` plus the comments that say so; every other character of the two cells -- signature, clamp, cursor guards, outer loop, exchange, fold, return -- is identical. So `c-gcc-h` minus `c-gcc` is the price of the scan guard and of nothing else. (2) THE COMPARISONS ARE NON-STRICT IN EVERY RUNG. `<=` / `>=` is what makes `j - i == 1` collapse to `i == j` instead of letting the cursors cross, which is what makes `i <= j` an invariant and lets R5 carry `decreases j - i` at all three loops; `<` / `>` is equally common in the wild and is a DIFFERENT program, whose partition point differs by one on any record containing a byte equal to its pivot. Pinning it is what stops a rung comparison moving on it. (3) THE CLAMP AND THE ZERO-FILL ARE IN EVERY RUNG INCLUDING R1. The clamp bounds the COPY, so every read of the SOURCE window is in bounds in every rung and the only out-of-bounds access any cell can make is the scan's; the zero-fill makes the STALE TAIL `scr[m..SCR)` deterministic, which is what makes the in-bounds middle regime -- `adversarial-inarray` -- reproducible rather than a property of whatever was on the stack. (4) THE BULK LOAD IS ONE SPELLING. p02's retraction is the precedent: one operator flips `bulk_calls` and 100% of the delta, so a rung that copied byte-at-a-time would be measuring the copy and calling it the partition. The RECEIVER is scoped 2-and-2 -- safe_naive.rs and safe_tuned.rs write `dst[..n]`, unsafe.rs and verus.rs write the `split_at_mut(n)` form -- because `..n` is a `RangeTo<usize>` and `RangeTo` has no `SliceIndexSpecImpl` at the pinned vstd, so `dst[..n]` cannot be VERIFIED at all and R4 must follow R5 to keep the identity pin. p06 measured that receiver's price at ZERO at -O3. (5) THE PARTITION POINT IS IN THE FOLD. A partition is a PERMUTATION of the loaded prefix, so the partitioned and the unpartitioned scratch are the same MULTISET on EVERY input -- not merely on some regime, which is the stronger form of p06's lesson -- and a sum- or xor-fold could not observe the partition at all. The fold is therefore an order-sensitive Horner chain over the full live extent, and the returned index is folded on top of it because the index is the kernel's other output and nothing else would move if a rung got it wrong. (6) WHAT IS DELIBERATELY LEFT FREE, and it is the operation the pattern is named for: THE EXCHANGE. safe_tuned.rs writes `scr.swap(i, j - 1)` and safe_naive.rs writes four indexed accesses, and no entry pins either, because the two are BYTE-IDENTICAL at -O3. MEASURED ON A PROBE AND SAID SO: `.temp/t101/cost23.rs`'s `k_r2` and `k_r3c` differ only in that one spelling and have the same padding-stripped normalised disassembly (219 instructions, `5dca9d30a43c`) and the same marginal `Ir` to the instruction at three separate pivot ranks. A probe measures a SLOPE and its intercept is a property of the probe (`.memory/03-measurement.md`), so what transfers is the EQUALITY, not the 219. Pinning a spelling whose price is zero would buy nothing and would exclude an idiom for no reason. (7) WHAT IS FORBIDDEN, AND ITS PRICE IS PUBLISHED. `.position(` / `.rposition(` is the most idiomatic Rust for `advance while`, and it is excluded IN EVERY RUNG rather than in some -- a whole-pattern exclusion, which stays visible and keeps the two sides equal, unlike the scoped kind `.memory/01-ladder.md` caught on p13. The reason is the reason to publish: measured ON A PROBE against a fixed driver (`.temp/t101/cost23.rs`, marginal whole-program `Ir`/call, `-O` isolated, debug-assertions off), the iterator-scan spelling is the DEAREST R3 found at a median pivot (4208.00 against 3141.00 for the shipped spelling) and the CHEAPEST at the minimum-rank pivot (2812.30 against 3094.30). THE TRANSFERABLE CLAIM IS THE ORDERING FLIP, NOT THE FOUR NUMBERS: a rung built on it would make p23's safe-side headline a function of WHICH BAND was measured rather than of the pattern. ../NOTES.md 9 has the table. `.select_nth_unstable` and `.partition_point(` are std's own partitioning primitives and would delete the kernel; `.sort_unstable` and `qsort(` would replace it with a different algorithm entirely. NOTHING HERE PINS A RUNG'S ADVANTAGE. R2-vs-R3 is measured at matched semantics with three levers priced separately (../NOTES.md 9), and the R4 side names a lever it did NOT take -- resliced-window addressing, cheaper than the shipped R4 by 6.00 probe-`Ir`/call at all three probe bands, held out because R4 must be byte-identical to R5 and `split_at` on the window has not been shown to verify at the pinned vstd. That is `.memory/01-ladder.md`'s rule for a fixed-by-fiat R4 endpoint, and saying it here is the whole of the compliance. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p23-partition.json`, contract `8251a6762b10`.

`30` backticked spelling(s) over `6` rung(s) → **90** (spelling, rung) pair(s), **53** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 12 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 0 spelling(s) pin nothing**, 1 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - absent — `i < j &&` (required[0], c, **c/kernel.c**)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## What the gate said out loud (reporting only)

From `results/gate/p23-partition.json` — the `loud` and `controls_json` keys, at contract `8251a6762b10`, verdict `PASS`. **These did not fail the gate and are not defects**; they are the conditions `check.py` refuses to be silent about. Each one is a caveat on a number below or on the declaration above.

- **`tcb-unsafe`** — verus.rs:325 `scr_set_unchecked`'s `requires` constrains nothing about ['x'], which its trusted body uses. spec.md justifies it: `x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `u8` is a legal thing to store in a `u8` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [u8; 64]` reads `i < 64`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second and p06 the third. On p23 the item carries the WRITE half of the bug: it is called twice per exchange, and the store R1 gets wrong is the one it reaches after its DOWNWARD scan has wrapped `j` -- so this `requires` is what excludes an out-of-bounds write that a missing READ guard, one loop earlier, made reachable. A second conjunct `old(v)@.len() == 64` is deliberately NOT written: for a `&mut [u8; 64]` it is a TAUTOLOGY discharged from the parameter type alone by vstd's `array_len_matches_n`, and p03's gate run refused exactly that draft (p03 NOTES.md 5b).
- **`tables`** — patterns/p23-partition/controls/sweep_fit.json carries NO staleness pin, so nothing can tell whether its numbers were taken against the sources that are in the tree now. `synthesis/licence.json` is the shape to copy: a top-level `gate_source_sha256` equal to this record's `source_sha256`, written by the generator that emits the file. Until then treat every figure quoted from it as UNDATED.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 163 | 160 | 0 | 589 | 169,008,325 | 33,016,113 | 900,056 | 300,056 | `349a9af1` | `349a9af1` | yes | xmm |
| c-clang | 153 | 146 | 2 | 546 | 141,001,601 | 29,002,147 | 840,059 | 280,059 | `cad7b87b` | `0954a8dc` | yes | xmm |
| safe_naive | 255 | 248 | 4 | 1,068 | 164,257,508 | 40,602,727 | 840,275 | 280,275 | `bf7224f9` | `a88d5a75` | yes | xmm |
| safe_tuned | 231 | 223 | 8 | 936 | 161,560,772 | 38,850,373 | 840,275 | 280,275 | `f1eb24cd` | `5c72e840` | yes | xmm |
| unsafe | 165 | 157 | 9 | 647 | 143,216,305 | 29,979,420 | 840,275 | 280,275 | `43acbc72` | `b3b67e72` | yes | xmm |
| verus | 165 | 157 | 9 | 647 | 143,216,305 | 29,979,420 | 840,270 | 280,270 | `43acbc72` | `b3b67e72` | yes | xmm |
| c-gcc-h | 160 | 157 | 0 | 587 | 166,662,302 | 31,809,341 | 900,056 | 300,056 | `ce98adcb` | `ce98adcb` | yes | xmm |
| c-clang-h | 161 | 154 | 1 | 570 | 141,189,050 | 28,539,420 | 840,059 | 280,059 | `abc1898f` | `d53f4e7e` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 221 | 219 | 0 | 988 | 290,504,440 | - | 2,160,066 | - | `0e4c45d6` | `0e4c45d6` | yes | - |
| c-clang | 180 | 180 | 1 | 911 | 268,244,834 | - | 1,260,056 | - | `65050eea` | `c705928b` | yes | - |
| safe_naive | 392 | 392 | 8 | 2,296 | 434,240,220 | - | 1,500,077 | - | `9f7757b1` | `e313e7e0` | yes | - |
| safe_tuned | 338 | 338 | 3 | 1,917 | 449,718,184 | - | 1,500,077 | - | `1a1ce546` | `88d55ca5` | yes | - |
| unsafe | 309 | 309 | 11 | 1,797 | 438,803,145 | - | 1,500,077 | - | `a078f097` | `da0d0582` | yes | - |
| verus | 309 | 309 | 11 | 1,797 | 438,803,145 | - | 1,500,056 | - | `57cb01cb` | `fb822241` | yes | - |
| c-gcc-h | 227 | 225 | 0 | 1,008 | 318,354,627 | - | 2,160,066 | - | `77c6c02c` | `77c6c02c` | yes | - |
| c-clang-h | 200 | 200 | 2 | 997 | 359,028,166 | - | 1,260,056 | - | `f40e350d` | `94ee097b` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 377 | 373 | 1 | 1,512 | - | - | 169,368,462 | 33,076,250 | `9b312466` | `709eae56` | yes | - |
| c-clang | 423 | 416 | 0 | 1,673 | - | - | 139,507,305 | 29,030,051 | `c70fcaab` | `c70fcaab` | yes | xmm |
| safe_naive | 878 | 864 | 1 | 4,015 | - | - | 163,661,054 | 40,310,655 | `010fa5f1` | `65e0a224` | yes | xmm |
| safe_tuned | 867 | 852 | 1 | 3,935 | - | - | 162,401,052 | 39,410,653 | `175d4a62` | `b3e4eb59` | yes | xmm |
| unsafe | 796 | 781 | 1 | 3,567 | - | - | 143,396,584 | 30,039,699 | `7386a75f` | `051b53a8` | yes | xmm |
| verus | 799 | 786 | 1 | 3,519 | - | - | 143,276,586 | 29,999,701 | `60a3cca1` | `23338067` | yes | xmm |
| c-gcc-h | 370 | 365 | 1 | 1,482 | - | - | 174,633,853 | 33,233,815 | `4c98008a` | `8a054b5d` | yes | - |
| c-clang-h | 434 | 423 | 0 | 1,737 | - | - | 141,674,553 | 28,587,618 | `6f04b804` | `6f04b804` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 290,504,440 | - | 2,160,066 | - | `cead0a9b` | `cead0a9b` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 267,704,834 | - | 1,260,055 | - | `7a11476b` | `7a11476b` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 434,240,220 | - | 1,500,077 | - | `6e02531f` | `7dec2324` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 449,718,184 | - | 1,500,077 | - | `8b3175c7` | `f388db99` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 438,803,145 | - | 1,500,077 | - | `5b2db597` | `b30375b3` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 438,803,145 | - | 1,500,056 | - | `fe533dc3` | `e64748cc` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 318,354,627 | - | 2,160,066 | - | `655d1157` | `655d1157` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 329,113,937 | - | 1,260,055 | - | `d0f0fae7` | `d0f0fae7` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 309/309 vs 309/309 | 11 B vs 11 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 165/157 vs 165/157 | 9 B vs 9 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 10.37 | 10.57 | 1.9% | 32.38 | 33.11 | 2.3% |
| c-gcc | whole | 10.61 | 10.81 | 1.9% | 32.71 | 33.07 | 1.1% |
| c-clang | isolated | 10.67 | 10.89 | 2.0% | 25.64 | 26.83 | 4.7% |
| c-clang | whole | 10.80 | 11.05 | 2.3% | 32.63 | 33.23 | 1.8% |
| safe_naive | isolated | 11.41 | 11.69 | 2.5% | 28.57 | 28.91 | 1.2% |
| safe_naive | whole | 11.40 | 11.68 | 2.4% | 32.71 | 33.15 | 1.3% |
| safe_tuned | isolated | 11.17 | 11.46 | 2.6% | 28.47 | 28.90 | 1.5% |
| safe_tuned | whole | 11.19 | 11.54 | 3.2% | 28.87 | 29.43 | 2.0% |
| unsafe | isolated | 11.06 | 11.29 | 2.2% | 30.86 | 31.16 | 0.9% |
| unsafe | whole | 11.20 | 11.37 | 1.5% | 34.17 | 34.53 | 1.1% |
| verus | isolated | 11.01 | 11.19 | 1.6% | 32.78 | 33.26 | 1.5% |
| verus | whole | 10.96 | 11.23 | 2.4% | 34.01 | 34.38 | 1.1% |
| c-gcc-h | isolated | 10.35 | 10.56 | 2.1% | 31.51 | 31.83 | 1.0% |
| c-gcc-h | whole | 10.56 | 10.72 | 1.5% | 35.26 | 35.60 | 0.9% |
| c-clang-h | isolated | 10.61 | 10.79 | 1.7% | 30.27 | 30.63 | 1.2% |
| c-clang-h | whole | 10.61 | 10.86 | 2.4% | 32.53 | 32.76 | 0.7% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 6 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `degenerate.bin`
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `degenerate.bin`
- `O0 / whole` on `large.bin`
- `O3 / isolated` on `degenerate.bin`
- `O3 / whole` on `degenerate.bin`
