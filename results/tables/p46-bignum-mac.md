# p46-bignum-mac — results

Generated 2026-08-25T08:22:25Z from `results/p46-bignum-mac.json` (git `3203dbbc6158`, working tree dirty).

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
| adversarial-nearmiss.bin | 100 | 1,576 | 1,576 | False | n_iters=100 n_blob=1568 stride=784 nwin=2 calls=100 macs/call=0 san=fires truncated=False expected=6350903166487370560 |
| adversarial-oob.bin | 100 | 2,904 | 2,904 | False | n_iters=100 n_blob=2896 stride=1448 nwin=2 calls=100 macs/call=0 san=fires truncated=False expected=6350903166487370560 |
| adversarial-shortlen.bin | 100 | 856 | 792 | True | n_iters=100 n_blob=784 stride=392 nwin=0 calls=0 macs/call=0 san=clean truncated=True expected=None |
| adversarial-tiny.bin | 100 | 264 | 264 | False | n_iters=100 n_blob=256 stride=4 nwin=64 calls=100 macs/call=0 san=clean truncated=False expected=0 |
| degenerate.bin | 2,000 | 1,576 | 1,576 | False | n_iters=2000 n_blob=1568 stride=392 nwin=4 calls=2000 macs/call=0 san=clean truncated=False expected=14562296563636660656 |
| large.bin | 1,000 | 12,424 | 12,424 | False | n_iters=1000 n_blob=12416 stride=776 nwin=16 calls=1000 macs/call=2304 san=clean truncated=False expected=5115297578987792189 |
| small.bin | 4,000 | 6,280 | 6,280 | False | n_iters=4000 n_blob=6272 stride=392 nwin=16 calls=4000 macs/call=576 san=clean truncated=False expected=17697127704422069934 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — every rung tests that the declared operands FIT IN THE WINDOW before it reads a limb, spelled `8 + 8 * (n + m) > len`. `c/kernel.c` HAS this one -- it is not the safety line, and pinning it is what keeps p46's bug an output-side miscount rather than an input-side over-read.
  - `rust` — every rung tests that the declared operands FIT IN THE WINDOW before it reads a limb, spelled `8 + 8 * (n + m) > len`.
- **required** — *per language:*
  - `c` — THE SAFETY LINE: the declared product must fit in the scratch, spelled `n + m > SLB_P46_OUTCAP`. `c/kernel_hardened.c` spells it; `c/kernel.c` DOES NOT, and that omission is the bug this pattern models. The idiom audit prints the absence, and the absence is the vulnerability.
  - `rust` — THE SAFETY LINE: the declared product must fit in the scratch, spelled `n + m > OUTCAP`. All four Rust rungs spell it, so all six rungs compute the same function on every input including the adversarial ones.
- **required** — *per language:*
  - `c` — the multiply-accumulate is a 128-BIT WIDENING one, spelled `(unsigned __int128)ai * bl[j]`; C's unsigned arithmetic wraps by definition (6.2.5p9) so the fold needs no special spelling.
  - `rust` — the multiply-accumulate is a 128-BIT WIDENING one, spelled `(ai as u128) * (bj as u128)`, and the checksum fold is spelled `acc.wrapping_mul(31).wrapping_add(` -- wrapping, not checked, so the kernel is total on VALUES and the only runtime obligation is the index.
- **required** — *per language:*
  - `c` — the product scratch is a FIXED-CAPACITY AUTOMATIC array, spelled `uint64_t out[SLB_P46_OUTCAP]`, never sized from `n + m`. Its capacity is a property of the PROGRAM; the limb counts are properties of the INPUT, and the whole pattern is the gap between them.
  - `rust` — the product scratch is a FIXED-CAPACITY array, spelled `[u64; OUTCAP] = [0u64; OUTCAP]`, never sized from `n + m`.
- **required** — *per language:*
  - `rust` — THE RUNG BOUNDARY INSIDE THE SAFE CLASS, and it is one construct. R2 spells the accumulator read `(out[i + j] as u128)`; R3 spells the whole inner walk `out[i..i + m].iter_mut().zip(`. Each is present in exactly one rung by construction, so the audit reports the other three as absent for both -- that is the declaration working, not failing.
- **required** — the Rust rungs take the window as a sub-slice of `buf` and index that, so the window offset is folded into the base pointer; the b operand is pre-decoded ONCE into a scratch sized by the TYPE of `m`, so the pre-decode is O(m) and is not part of the bug, and the MAC loop is the only O(n*m) thing in the kernel.
- **required** — the limb decode is the ADDITIVE spelling, byte-identical in all six rungs, so that no rung difference lives in the decoder. p09 spells it the same way and for the same reason: verus.rs's `u64_at` is additive and a shift-or exec spelling would need a bit-vector detour to be related to it.
- **FORBIDDEN** — *per language:*
  - `c` — `% SLB_P46_OUTCAP` -- the clamped index. It is not slower and it is not wrong; it DELETES THE PATTERN, because a clamped index cannot leave the array and there is no memory-safety event at all. Measured, not argued: NOTES.md 0a run D, exit 0 with ASan and UBSan both silent and a wrong answer. This entry is the bug class's own precondition written as a spelling.
  - `rust` — `% OUTCAP` -- the same exclusion on the Rust side.
- **FORBIDDEN** — *per language:*
  - `c` — `malloc(` -- a product buffer sized at run time from the declared limb counts. With one the bug is UNREACHABLE by construction, which is the other way this row would have died.
  - `rust` — `vec![0u64;` -- the same exclusion.
- **FORBIDDEN** — *per language:*
  - `rust` — `.wrapping_mul(bj)` -- a 64-bit multiply-accumulate. Semantically a DIFFERENT ALGORITHM: it discards the high limb, so the carry chain and the whole nonlinear proof obligation disappear with it. Naming it keeps p46's numbers attached to p46's arithmetic.
- **FORBIDDEN** — a dead `buf_len` parameter on the C kernel. The length is the thing C does not have and therefore cannot check; handing C one to make the signatures match would be Rust-in-C-syntax and would delete half the comparison.

> **Why**: p46's whole question is where the fact `i + j < OUTCAP` comes from, and every entry above is about that. The kernel multiplies two bignums whose LIMB COUNTS arrive in the input, one schoolbook multiply-accumulate per (i, j) pair, into a product scratch of FIXED capacity -- so the index is loop-carried in neither sense p05's is: `i + j` is purely LINEAR, and what is nonlinear here is the VALUE, `a*b + c + carry`, not the address. Three rungs establish `i + j < OUTCAP` three ways and the pattern prices all three: R5 proves it statically (0 instructions), R2 and R3 write it three times per MAC STEP -- read `bl[j]`, read `out[i + j]`, write `out[i + j]` -- and the hardened C rung tests it ONCE PER CALL, because C can compare `n + m` against the capacity before it starts. THREE STRATEGIES, AND TWO OF THE THREE ARE ZERO: O(0) by proof, O(1) in hardened C, and O(0) again in both safe rungs because LLVM discharges the obligation itself and deletes every check. THIS SENTENCE SAID FOUR STRATEGIES WITH FOUR ASYMPTOTICS UNTIL TASK_092, THE FOURTH BEING R3's `O(n)` RESLICE CHECK, AND THERE IS NO SUCH CHECK IN THE MACHINE CODE (TASK_089_REVIEW M2, re-derived at TASK_092): `safe_naive` and `safe_tuned` have the IDENTICAL conditional-branch multiset `ja:2 jae:2 jb:1 jbe:1 je:6 jne:5`, and the measured `R3 - R2 = 2n - 2` (m even) / `-2` (m odd) is ADDRESS ARITHMETIC -- a `lea`/`add` row-base pair this rung hoists into the row header and `safe_naive` computes inside its odd-`m` remainder block, which is exactly why the law has two branches on `m` parity (NOTES.md 8e). R3's `2n` is a spelling cost. `required[4]` still pins the two inner-walk spellings, because they are what makes R2 and R3 different rungs; what it does not do is buy a third asymptotic. THE OUTPUT-SIDE BOUND IS THE SAFETY LINE AND THE INPUT-SIDE BOUND IS NOT. `required[0]` pins `8 + 8 * (n + m) > len` in every rung INCLUDING the buggy C one: without it the kernel would read past the window and p46 would be a different, duller bug. `required[1]` pins `n + m > OUTCAP`, which `c/kernel.c` DOES NOT SPELL, and the idiom audit prints that absence -- the missing spelling is the vulnerability. C checks the read and forgets the write, which is the shape of the real bignum miscount. THE `forbidden` ENTRIES ABOUT THE BUG CLASS ARE CONDITIONS, NOT TASTE, AND BOTH WERE SETTLED BY RUNS BEFORE ANY CELL WAS WRITTEN (NOTES.md 0a). A miscounted buffer index is a MEMORY-SAFETY bug only if the index is left alone: with the clamp `out[(i + j) % OUTCAP]` the identical miscount is exit 0 with ASan and UBSan both SILENT -- a wrong answer and no memory event at all, which is `p31`'s death. And with a product buffer allocated from `n + m` at run time the bug is unreachable by construction. A rung that took either route would still compute a product and would no longer model p46's bug, which is exactly what a `forbidden` entry is for. AND THE PROOF OBLIGATION THE RUNGS DO NOT DIFFER ON IS PINNED TOO. `required[2]` pins the 128-bit widening multiply-accumulate in every rung, because a 64-bit MAC would be a different algorithm; `forbidden[2]` excludes it by name. That step cannot overflow -- `(2^64-1)^2 + 2*(2^64-1)` is `2^128 - 1` exactly -- and NO RUNG CHECKS IT, in either language, at any rung. verus.rs must still discharge it, with a lemma, a `by (nonlinear_arith)`, a `by (compute)` and a `by (bit_vector)`. So p46 carries an obligation that costs real proof and zero instructions, beside one that costs trivial proof and every instruction the safe rungs pay: the two cost columns come apart inside one kernel. p46's numbers are still a spelling's numbers, and the in-contract spread was measured on BOTH sides BEFORE the rungs were chosen (NOTES.md 0b), because on this pattern the safe rung is CHEAPER than the unsafe one and that is exactly the shape that has been wrong in the flattering direction five times in this project. BOTH IN-CONTRACT SPANS ARE DEGENERATE, AND THE TWO NUMBERS THAT SAID OTHERWISE WERE THE PRE-BUILD PROBE'S. Until TASK_092 this sentence read `three R3 spellings span 9490 Ir/call at (n, m) = (48, 48) and three R4 spellings span 2750; NEITHER SIDE IS DEGENERATE`. Neither figure appears anywhere in NOTES.md; both come from `.temp/t89/cost.rs`, the pre-build probe whose slope NOTES.md 0b retracts (TASK_089_REVIEW M1). Measured on the SHIPPED shape over the 49-blob sweep band, with the shipped flag set, every admissible lever on both sides is FLAT in `n` and in `m`: the R4 side spans 2 Ir/call and the R3 side spans 0 (NOTES.md 8b). So the pair interval collapses onto the R3-side span, which is itself zero, and the published `R3 - R4` law does not depend on which spelling ships. THE CHEAPEST R4 FOUND IS STILL CHEAPER THAN THE CHEAPEST R3 FOUND AND IS STILL NOT A RUNG, BUT NOT FOR THE REASON THIS BLOCK GAVE. It said the pinned vstd cannot specify a mutable sub-slice. IT CAN: `~/tools/verus/vstd/std_specs/slice.rs` ships `assume_specification[ <Range<usize> as SliceIndex<[T]>>::index_mut ]` with a full VALUE-LEVEL `final(r)@ == final(slice)@.subrange(..)`, `vstd/slice.rs`'s `ExSliceIndex` is a trait declaration and not the specification, and `r4_mutreslice`'s FULL R5 verifies -- `21 verified, 0 errors`, mutation tested twice (TASK_089_REVIEW B1, settled at TASK_092; NOTES.md 0c). What disqualifies it is measured instead, and both halves are things this project already treats as disqualifying: (a) it costs TWO NEW TRUSTED ITEMS, an unchecked read and an unchecked write through a `&mut [u64]`, because the pinned vstd has ZERO occurrences of `get_unchecked` anywhere -- taking p46 from 5 `external_body` / 3 contracted to 7 / 5, which is exactly what the paragraph below records as having disqualified `r4_hdr` on p16; and (b) its R4/R5 pair is `differ` at -O3, `R5 - R4 = 15n + 1` Ir/call, against the `identity: unsafe == verus, O3 exact` pin all six patterns carry. SO THE REASON SAFE RUST WINS HERE IS THE TRUSTED BASE AND THE IDENTITY PIN, NOT SAFETY AND NOT A MISSING SPECIFICATION -- still `.memory/01-ladder.md` finding 14's shape, but a weaker and more specific claim than the one this block used to make, and one that INVERTS if either constraint is relaxed: `r4_mutreslice` at 5923 and even its R5 at 6284 are below `safe_naive`'s 6453 and `safe_tuned`'s 6499 on `sweep-n024m024`. NOTES.md 0c says so out loud. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p46-bignum-mac.json`, contract `43925b2955e0`.

`29` backticked spelling(s) over `6` rung(s) → **88** (spelling, rung) pair(s), **47** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 7 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 5 spelling(s) pin nothing**, 7 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - pins nothing — `c/kernel.c` (required[0], c, 0 of 2 rungs)
  - pins nothing — `c/kernel_hardened.c` (required[1], c, 0 of 2 rungs)
  - pins nothing — `c/kernel.c` (required[1], c, 0 of 2 rungs)
  - pins nothing — `u64_at` (required[6], c, 0 of 2 rungs)
  - pins nothing — `u64_at` (required[6], rust, 0 of 4 rungs)
  - absent — `n + m > SLB_P46_OUTCAP` (required[1], c, **c/kernel.c**)
  - absent — `(out[i + j] as u128)` (required[4], rust, **safe_tuned.rs**)
  - absent — `(out[i + j] as u128)` (required[4], rust, **unsafe.rs**)
  - absent — `(out[i + j] as u128)` (required[4], rust, **verus.rs**)
  - absent — `out[i..i + m].iter_mut().zip(` (required[4], rust, **safe_naive.rs**)
  - absent — `out[i..i + m].iter_mut().zip(` (required[4], rust, **unsafe.rs**)
  - absent — `out[i..i + m].iter_mut().zip(` (required[4], rust, **verus.rs**)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## What the gate said out loud (reporting only)

From `results/gate/p46-bignum-mac.json` — the `loud` and `controls_json` keys, at contract `43925b2955e0`, verdict `PASS`. **These did not fail the gate and are not defects**; they are the conditions `check.py` refuses to be silent about. Each one is a caveat on a number below or on the declaration above.

- **`tcb-unsafe`** — verus.rs:285 `arr_set_unchecked`'s `requires` constrains nothing about ['x'], which its trusted body uses. spec.md justifies it: `x` is a pure VALUE parameter: it is stored into the scratch and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `T` is a legal thing to store in a `T` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` reads `i < N`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, then p12, p06, p14, p27, p38 and p22, and p46 is the eighth. It is the SAME generic item as p22's, character for character.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 526 | 521 | 0 | 2,408 | 33,084,000 | 28,866,000 | 56,053 | 14,053 | `378efa00` | `378efa00` | yes | xmm |
| c-clang | 153 | 150 | 2 | 546 | 24,432,004 | 23,088,004 | 56,057 | 14,057 | `9ba39db3` | `eb1d994b` | yes | - |
| safe_naive | 179 | 174 | 5 | 651 | 24,964,000 | 23,341,000 | 56,273 | 14,273 | `7ae1f42b` | `3221061b` | yes | - |
| safe_tuned | 177 | 172 | 5 | 651 | 25,148,000 | 23,435,000 | 56,273 | 14,273 | `eebc6c15` | `b65c4929` | yes | - |
| unsafe | 150 | 147 | 5 | 539 | 25,624,000 | 24,250,000 | 56,273 | 14,273 | `dc8e3fa8` | `bed0ef27` | yes | - |
| verus | 150 | 147 | 5 | 539 | 25,624,000 | 24,250,000 | 56,268 | 14,268 | `dc8e3fa8` | `bed0ef27` | yes | - |
| c-gcc-h | 530 | 524 | 0 | 2,440 | 33,100,000 | 28,869,000 | 56,053 | 14,053 | `7ce8dfdb` | `7ce8dfdb` | yes | xmm |
| c-clang-h | 157 | 154 | 2 | 562 | 24,440,004 | 23,090,004 | 56,057 | 14,057 | `a662f3c7` | `489759ff` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 167 | 167 | 0 | 887 | 103,612,000 | - | 144,066 | - | `a9d0470b` | `a9d0470b` | yes | - |
| c-clang | 130 | 130 | 1 | 729 | 75,680,004 | - | 80,056 | - | `7ee9f930` | `9bc41d95` | yes | - |
| safe_naive | 525 | 525 | 11 | 3,061 | 126,364,000 | - | 100,077 | - | `6d4bed68` | `3f37842a` | yes | - |
| safe_tuned | 528 | 528 | 3 | 3,069 | 95,196,000 | - | 100,077 | - | `e5d0737b` | `6acf2796` | yes | - |
| unsafe | 383 | 383 | 4 | 2,172 | 139,188,000 | - | 100,077 | - | `28dee777` | `2189e8b4` | yes | - |
| verus | 383 | 383 | 4 | 2,172 | 139,188,000 | - | 100,056 | - | `860c94c5` | `cf82b879` | yes | - |
| c-gcc-h | 174 | 174 | 0 | 925 | 103,632,000 | - | 144,066 | - | `29e8c616` | `29e8c616` | yes | - |
| c-clang-h | 137 | 137 | 0 | 768 | 75,696,004 | - | 80,056 | - | `034e95f5` | `034e95f5` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 228 | 227 | 2 | 915 | 33,080,000 | 28,865,000 | 60,126 | 15,126 | `79193a23` | `b1cfe6e5` | yes | - |
| c-clang | 415 | 410 | 0 | 1,607 | - | - | 24,388,185 | 23,059,185 | `47b4cd4d` | `47b4cd4d` | yes | xmm |
| safe_naive | 796 | 785 | 14 | 3,634 | - | - | 25,208,283 | 23,474,283 | `b60fd8db` | `65f91f4c` | yes | xmm |
| safe_tuned | 796 | 786 | 14 | 3,618 | - | - | 25,216,283 | 23,476,283 | `e49273b7` | `066cc671` | yes | xmm |
| unsafe | 773 | 762 | 14 | 3,538 | - | - | 25,792,283 | 24,340,283 | `474b0f3b` | `2fa0a29a` | yes | xmm |
| verus | 781 | 770 | 14 | 3,538 | - | - | 25,792,283 | 24,340,283 | `d8a94490` | `0b1096b5` | yes | xmm |
| c-gcc-h | 228 | 227 | 2 | 915 | 33,092,000 | 28,868,000 | 60,126 | 15,126 | `79193a23` | `b1cfe6e5` | yes | - |
| c-clang-h | 418 | 413 | 0 | 1,654 | - | - | 24,404,186 | 23,063,186 | `9537af92` | `9537af92` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 424 | 103,612,000 | - | 144,066 | - | `88da8cd6` | `88da8cd6` | yes | - |
| c-clang | 66 | 66 | 0 | 273 | 70,976,004 | - | 80,055 | - | `75cc012b` | `75cc012b` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 126,364,000 | - | 100,077 | - | `a9c07d16` | `e3e35580` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 95,196,000 | - | 100,077 | - | `0077ec11` | `899657f9` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 139,188,000 | - | 100,077 | - | `85b85fbb` | `bd8edfc4` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 139,188,000 | - | 100,056 | - | `f6bc74d4` | `565d1e2b` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 424 | 103,632,000 | - | 144,066 | - | `40b3acae` | `40b3acae` | yes | - |
| c-clang-h | 66 | 66 | 0 | 273 | 70,992,004 | - | 80,055 | - | `130cbeb5` | `130cbeb5` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 383/383 vs 383/383 | 4 B vs 4 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 150/147 vs 150/147 | 5 B vs 5 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 5.86 | 6.27 | 7.1% | 6.62 | 7.15 | 8.0% |
| c-gcc | whole | 6.06 | 6.41 | 5.9% | 6.82 | 7.34 | 7.6% |
| c-clang | isolated | 5.75 | 6.17 | 7.2% | 5.29 | 5.81 | 9.8% |
| c-clang | whole | 5.90 | 6.24 | 5.8% | 5.35 | 5.87 | 9.8% |
| safe_naive | isolated | 6.09 | 6.50 | 6.6% | 5.73 | 6.13 | 7.1% |
| safe_naive | whole | 6.09 | 6.72 | **10.3% ✗** | 5.66 | 6.22 | 10.0% |
| safe_tuned | isolated | 5.41 | 6.57 | **21.4% ✗** | 5.78 | 6.32 | 9.5% |
| safe_tuned | whole | 5.39 | 6.44 | **19.5% ✗** | 5.78 | 6.41 | **11.1% ✗** |
| unsafe | isolated | 5.56 | 6.73 | **21.2% ✗** | 6.04 | 6.76 | **12.0% ✗** |
| unsafe | whole | 5.60 | 6.84 | **22.1% ✗** | 6.00 | 6.59 | 9.8% |
| verus | isolated | 5.97 | 6.63 | **11.0% ✗** | 6.06 | 6.69 | **10.5% ✗** |
| verus | whole | 6.14 | 6.67 | 8.7% | 6.09 | 6.60 | 8.4% |
| c-gcc-h | isolated | 5.76 | 6.20 | 7.6% | 6.90 | 7.26 | 5.3% |
| c-gcc-h | whole | 5.83 | 6.19 | 6.1% | 6.61 | 7.08 | 7.2% |
| c-clang-h | isolated | 5.75 | 6.08 | 5.7% | 5.44 | 5.88 | 8.0% |
| c-clang-h | whole | 5.65 | 6.08 | 7.5% | 5.51 | 5.80 | 5.1% |

**9 of 32 wall-clock cells exceed the 10% min-to-median spread threshold and are DISCARDED** per `.memory/03-measurement.md` step 4. They are printed above marked ✗ rather than deleted, because a missing cell that looks like an omission is worse than a documented failure (`.memory/02-bench-rules.md`). **No claim in this report rests on a marked row.**

- `safe_naive / whole` on `large.bin`: spread 10.3%
- `safe_tuned / isolated` on `large.bin`: spread 21.4%
- `safe_tuned / whole` on `large.bin`: spread 19.5%
- `safe_tuned / whole` on `small.bin`: spread 11.1%
- `unsafe / isolated` on `large.bin`: spread 21.2%
- `unsafe / isolated` on `small.bin`: spread 12.0%
- `unsafe / whole` on `large.bin`: spread 22.1%
- `verus / isolated` on `large.bin`: spread 11.0%
- `verus / isolated` on `small.bin`: spread 10.5%


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 6 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `degenerate.bin`
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `degenerate.bin`
- `O0 / whole` on `large.bin`
- `O3 / isolated` on `degenerate.bin`
- `O3 / whole` on `degenerate.bin`
