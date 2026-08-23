# p38-alias-pun — results

Generated 2026-08-23T19:54:37Z from `results/p38-alias-pun.json` (git `50472d227f36`, working tree dirty).

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
| adversarial-huge.bin | 1 | 208 | 208 | False | n_iters=1 stride=200 n_blob=200 nwin=1 calls=1 work/call=200B rec(win0)=[(268435455, 48)] clamped=1 san=fires truncated=False expected=15963742333423663363 |
| adversarial-nrec.bin | 200 | 208 | 208 | False | n_iters=200 stride=200 n_blob=200 nwin=1 calls=200 work/call=200B rec(win0)=[(11, 11), (11, 11), (11, 11), (11, 11), (0, 0)] clamped=0 san=clean truncated=False expected=573548035304320128 |
| adversarial-oob.bin | 1 | 208 | 208 | False | n_iters=1 stride=200 n_blob=200 nwin=1 calls=1 work/call=200B rec(win0)=[(200, 48)] clamped=1 san=fires truncated=False expected=8516071857945885891 |
| adversarial-stale.bin | 1 | 208 | 208 | False | n_iters=1 stride=200 n_blob=200 nwin=1 calls=1 work/call=200B rec(win0)=[(60, 48)] clamped=1 san=clean truncated=False expected=10509230270850152637 |
| adversarial-stride7.bin | 100 | 15 | 15 | False | n_iters=100 stride=7 n_blob=7 nwin=0 calls=0 work/call=0B rec(win0)=[] clamped=0 san=clean truncated=False expected=0 |
| degenerate.bin | 4,000 | 808 | 808 | False | n_iters=4000 stride=200 n_blob=800 nwin=4 calls=4000 work/call=200B rec(win0)=[(5, 5), (5, 5)] clamped=0 san=clean truncated=False expected=15819171708748271115 |
| large.bin | 20,000 | 20,648 | 20,648 | False | n_iters=20000 stride=516 n_blob=20640 nwin=40 calls=20000 work/call=516B rec(win0)=[(15, 15), (15, 15), (15, 15), (15, 15), (15, 15), (15, 15)] clamped=0 san=clean truncated=False expected=6576101629690481408 |
| small.bin | 20,000 | 8,008 | 8,008 | False | n_iters=20000 stride=200 n_blob=8000 nwin=40 calls=20000 work/call=200B rec(win0)=[(11, 11), (11, 11), (11, 11), (11, 11)] clamped=0 san=clean truncated=False expected=8087734315336093952 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE PUN, and the whole of what c/kernel.c does differently: `return *(const uint32_t *)r;` in `rec_len`. The object is an array of `uint16_t` and the lvalue has type `uint32_t`; neither is a character type, so C99 6.5p7 does not permit the access. c/kernel_hardened.c writes the two-half spelling instead and is otherwise character-identical, so the scoped-absent audit pair this entry reports is on that rung and is correct.
  - `rust` — There is no Rust analogue of this entry and that is p38's result, so the entry pins the Rust rungs to the ABSENCE of the only spelling that could be one -- read_unaligned appears in no rung and is forbidden below.
- **required** — *per language:*
  - `c` — THE DEFINED READ, present in c/kernel_hardened.c and ABSENT from c/kernel.c: `return (uint32_t)r[0] + 65536 * (uint32_t)r[1];`. It reads the two 16-bit halves the wire format is defined in terms of and combines them, and it needs no build flag. It is NOT free -- see the why key -- and it is here rather than the free memcpy spelling because it is the one every Rust rung is forced into, so R1h stays idiom-matched to R2..R5.
  - `rust` — THE DEFINED READ, in all four Rust rungs and spelled the way the language forces (`sc` is an array of u16, so there is no cast to make): `65536 *` combines the two halves. It is the only spelling any Rust rung has, which is the pattern. TASK_067: the array type was written here as a BACKTICKED span reading [u16; 256], which is the element type only verus.rs spells -- safe_naive.rs, safe_tuned.rs and unsafe.rs all write [u16; SCRATCH_W] -- so an entry whose English said "all four Rust rungs" reported three required_absent pairs every gate run and nobody read them (TASK_066_REVIEW m8). The span is now prose; what this entry pins in all four rungs is the COMBINING, and that is what it always meant to pin.
- **required** — *per language:*
  - `c` — THE CLAMP, present in BOTH C rungs including the buggy one -- p38 models no MISSING check: `if (rec_len(&sc[i]) > room)`.
  - `rust` — the clamp, in all four Rust rungs, written through `u16` lvalues exactly as the C rungs write it: `> room`.
- **required** — *per language:*
  - `c` — the WINDOW/SCRATCH GUARD, in both C rungs: `while (o < nrec && i + 2 <= nw) {`. Additive rather than subtraction-first on purpose: i is the one quantity a miscompiled clamp can push PAST nw, and the subtraction-first form would then underflow into a second, unbounded walk. The loop invariant i <= nw keeps the addition from overflowing in the verified rungs.
  - `rust` — the same guard in all four Rust rungs: `while o < nrec && i + 2 <= nw`.
- **required** — *per language:*
  - `c` — the CURSOR ADVANCE is by a whole record including its length field, so a rung that walked overlapping or misaligned records cannot produce the same fold: `i = i + 2 + 2 * n;` in both C rungs.
  - `rust` — the cursor advance in all four Rust rungs: `i = i + 2 + 2 * n;`.
- **required** — *per language:*
  - `c` — the PAYLOAD FOLD, spelled with the literal multiplier: `acc = acc * 31 + (uint64_t)sc[i + 2 + k];` in both C rungs.
  - `rust` — the payload fold in all four Rust rungs: `.wrapping_mul(31).wrapping_add(`.
- **required** — *per language:*
  - `c` — the header and every word are decoded with + and * and never with | and <<, so the whole specification stays inside linear arithmetic (.memory/04-verus.md): `256 *` in both C rungs.
  - `rust` — the same decode in all four Rust rungs: `256 *`.
- **required** — the number of records actually walked is folded LAST, so a rung that stopped at a different point cannot produce the same checksum: `o` appears in the return expression of all eight rungs.
- **required** — the declared record count is rejected before any record is read, so no rung can walk a header it has not validated: `nrec == 0` appears in all eight rungs.
- **FORBIDDEN** — *per language:*
  - `rust` — `read_unaligned`
- **FORBIDDEN** — *per language:*
  - `rust` — `transmute`
- **FORBIDDEN** — *per language:*
  - `rust` — `align_to`
- **FORBIDDEN** — *per language:*
  - `rust` — `from_le_bytes`
- **FORBIDDEN** — *per language:*
  - `c` — `union`
- **FORBIDDEN** — *per language:*
  - `c` — `memcpy`
- **FORBIDDEN** — `copy_from_slice`
- **FORBIDDEN** — `chunks_exact`
- **FORBIDDEN** — `black_box`
- **FORBIDDEN** — `volatile`

> **Why**: POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all eight rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ON p38 THE PINNED SPELLING IS THE UNDEFINED BEHAVIOUR ITSELF. `*(const uint32_t *)r` in c/kernel.c and `(uint32_t)r[0] + 65536 * (uint32_t)r[1]` in c/kernel_hardened.c compute the same function of the same two bytes on this target and differ only in that the first is undefined by C99 6.5p7. THEY ARE NOT THE SAME MACHINE CODE, AND THAT IS MEASURED RATHER THAN ASSUMED: the defined spelling costs 6 static instructions on gcc and 10 on clang, by two different routes -- clang and rustc MERGE the two 16-bit loads back into one 32-bit load and then fail to simplify `(x & 0xffff) + 65536 * (x >> 16)` back to `x`, while gcc does not merge at all and pays for two movzwl plus a shift and an add. rustc pays clang's 10 in every Rust rung (../NOTES.md 1). The defined spellings that ARE free are `memcpy(&v, r, 4)` and the union: on clang both are BYTE-IDENTICAL to c/kernel.c and on gcc one instruction from it. Neither is the shipped R1h, because neither is a spelling any Rust rung can write, and a C rung spelling the length read a way no Rust rung can would put a codegen difference into p38's safety column; they ship as the controls `c_memcpy` and `c_union`. Every other check in this gate is blind to that difference: both cells agree with model.py on every non-adversarial input, both are ASan- and UBSan-clean in the gate's own -O1 sanitizer build, and Miri never sees a C rung at all. THE PIN IS THEREFORE THE ONLY THING IN THIS TREE THAT RECORDS WHICH C RUNG HAS THE BUG. WHY THE CLAMP IS `required` IN BOTH C RUNGS AND NOT ABSENT FROM ONE: p38 is not a pattern with a missing bounds check -- ten of the twenty patterns here already are. The check is WRITTEN in c/kernel.c, character for character as in c/kernel_hardened.c, and the type rule licenses the compiler to ignore it. A `required` entry that scoped the clamp to the hardened rung only would have described a different pattern. WHY THE ACCESSOR PAIR IS SPLIT INTO A GETTER AND A SETTER, AND WHY THE GETTER IS CALLED TWICE: the clamp writes through `uint16_t` lvalues and the re-read loads through a `uint32_t` lvalue, and a compiler is entitled to answer the second call from the value the first returned. Fold the two calls into one local and the question cannot be asked; that variant is shipped as the control `c_once` in controls/gen_controls.py and it is measured, not asserted. WHY `rlen` COUNTS 32-BIT UNITS: every record header then sits at an even word index, so the punning load is ALIGNED. Misalignment is a second, different undefined behaviour, and UBSan's `alignment` check would otherwise take credit for catching p38's bug when it cannot see it at all (../NOTES.md 6). WHY THE DECODE LOOP IS WORD-AT-A-TIME AND NOT `memcpy`/`copy_from_slice`: a bulk copy in the C rungs against an indexed loop in the Rust rungs would put p12's lost-bulk-lowering finding inside p38's cost column. All eight rungs read two bytes and combine them with `+` and `*`. WHAT IS DELIBERATELY NOT PINNED is how the scratch and the window are ADDRESSED -- R2 indexes, R3 reslices once per record, R4 and R5 use `get_unchecked` -- because that is the SAFETY axis and it is the axis the R3-side span is measured along (../NOTES.md 8). WHY `read_unaligned` IS FORBIDDEN IN THE RUST RUNGS: it is the DIRECT analogue of the C pun and it is DEFINED in Rust, which is p38's headline -- but ../spec.md pins `identity: unsafe == verus, O3 exact`, and at the pinned vstd `as_ptr`, `add` and `read_unaligned` are each `is not supported`, so a rung that spelled it would have no verifying twin and would not be a rung (`.memory/01-ladder.md` finding 14). It ships as the control `r4_pun`, measured and run through Verus, and ../NOTES.md 8 records both numbers. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p38-alias-pun.json`, contract `314bf2e385d4`.

`36` backticked spelling(s) over `6` rung(s) → **108** (spelling, rung) pair(s), **62** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 14 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 0 spelling(s) pin nothing**, 2 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - absent — `return *(const uint32_t *)r;` (required[0], c, **c/kernel_hardened.c**)
  - absent — `return (uint32_t)r[0] + 65536 * (uint32_t)r[1];` (required[1], c, **c/kernel.c**)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 242 | 237 | 0 | 981 | 20,560,000 | 51,160,000 | 300,056 | 300,056 | `096a44a9` | `096a44a9` | yes | xmm |
| c-clang | 181 | 175 | 1 | 698 | 25,200,000 | 63,500,000 | 280,059 | 280,059 | `366e3be5` | `1733f85b` | yes | xmm |
| safe_naive | 233 | 229 | 11 | 965 | 31,260,000 | 79,440,000 | 280,275 | 280,275 | `f84943f8` | `9ee0fe38` | yes | xmm |
| safe_tuned | 233 | 226 | 2 | 958 | 26,540,000 | 65,720,000 | 280,275 | 280,275 | `41d6be2a` | `866c0924` | yes | xmm |
| unsafe | 192 | 185 | 10 | 774 | 26,120,000 | 65,220,000 | 280,275 | 280,275 | `59ee6732` | `bb91e15a` | yes | xmm |
| verus | 192 | 185 | 10 | 774 | 26,120,000 | 65,220,000 | 260,274 | 260,274 | `59ee6732` | `bb91e15a` | yes | xmm |
| c-gcc-h | 247 | 243 | 0 | 1,007 | 20,800,000 | 51,640,000 | 300,056 | 300,056 | `c8c25460` | `c8c25460` | yes | xmm |
| c-clang-h | 191 | 185 | 1 | 746 | 25,840,000 | 64,780,000 | 280,059 | 280,059 | `b95b356f` | `f2167709` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 167 | 167 | 0 | 833 | 87,520,000 | - | 720,066 | - | `3b868fbf` | `3b868fbf` | yes | - |
| c-clang | 148 | 148 | 1 | 739 | 88,140,000 | - | 420,056 | - | `c5fbd64c` | `d35bc32f` | yes | - |
| safe_naive | 304 | 304 | 2 | 1,742 | 130,180,000 | - | 500,077 | - | `711b2d73` | `d502a42f` | yes | - |
| safe_tuned | 343 | 343 | 4 | 1,996 | 118,120,000 | - | 500,077 | - | `cc5bf253` | `bc8d72ac` | yes | - |
| unsafe | 233 | 233 | 1 | 1,247 | 126,160,000 | - | 500,077 | - | `80c21bd4` | `b9175be6` | yes | - |
| verus | 233 | 233 | 1 | 1,247 | 126,160,000 | - | 500,056 | - | `f2b9c438` | `9f3520d4` | yes | - |
| c-gcc-h | 167 | 167 | 0 | 833 | 87,520,000 | - | 720,066 | - | `e7f3435e` | `e7f3435e` | yes | - |
| c-clang-h | 148 | 148 | 1 | 739 | 88,140,000 | - | 420,056 | - | `c89cf0b3` | `66ee09ee` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 229 | 228 | 1 | 923 | 20,460,000 | 51,060,000 | 300,127 | 300,127 | `00aee19b` | `a2bf1c19` | yes | - |
| c-clang | 448 | 440 | 0 | 1,809 | - | - | 25,320,190 | 63,380,190 | `bb9a1f01` | `bb9a1f01` | yes | xmm |
| safe_naive | 767 | 757 | 1 | 3,487 | - | - | 48,420,286 | 125,420,286 | `834b6f32` | `15851a6c` | yes | xmm |
| safe_tuned | 811 | 801 | 1 | 3,695 | - | - | 15,300,294 | 36,740,294 | `6ad95bb4` | `c5df5bbf` | yes | xmm |
| unsafe | 820 | 808 | 1 | 3,759 | - | - | 26,200,291 | 65,140,291 | `558c21cd` | `08e2d552` | yes | xmm |
| verus | 827 | 813 | 1 | 3,743 | - | - | 26,360,285 | 65,460,285 | `64335213` | `1411867d` | yes | xmm |
| c-gcc-h | 229 | 228 | 1 | 923 | 20,780,000 | 51,700,000 | 300,127 | 300,127 | `00aee19b` | `a2bf1c19` | yes | - |
| c-clang-h | 403 | 394 | 0 | 1,617 | - | - | 25,800,190 | 64,820,190 | `a3fb2c5e` | `a3fb2c5e` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 87,520,000 | - | 720,066 | - | `89d900e5` | `89d900e5` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 85,900,000 | - | 420,055 | - | `a59b3c78` | `a59b3c78` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 130,180,000 | - | 500,077 | - | `bea0a485` | `0786fa4b` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 118,120,000 | - | 500,077 | - | `09353b28` | `fb02b9b5` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 126,160,000 | - | 500,077 | - | `b1b773cb` | `57129361` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 126,160,000 | - | 500,056 | - | `fc8a90fb` | `cc35e4c8` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 87,520,000 | - | 720,066 | - | `14edf8c8` | `14edf8c8` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 85,900,000 | - | 420,055 | - | `b8e68317` | `b8e68317` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 233/233 vs 233/233 | 1 B vs 1 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 192/185 vs 192/185 | 10 B vs 10 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 7.17 | 7.31 | 2.0% | 5.06 | 5.57 | **10.1% ✗** |
| c-gcc | whole | 7.28 | 7.36 | 1.1% | 5.02 | 5.66 | **12.8% ✗** |
| c-clang | isolated | 9.93 | 10.08 | 1.5% | 6.56 | 7.04 | 7.3% |
| c-clang | whole | 9.86 | 10.01 | 1.5% | 6.40 | 7.03 | 9.8% |
| safe_naive | isolated | 9.96 | 10.13 | 1.8% | 6.80 | 7.11 | 4.5% |
| safe_naive | whole | 11.05 | 11.22 | 1.5% | 7.13 | 7.90 | **10.9% ✗** |
| safe_tuned | isolated | 10.00 | 10.17 | 1.7% | 6.15 | 6.70 | 8.9% |
| safe_tuned | whole | 6.83 | 7.00 | 2.5% | 4.79 | 5.16 | 7.8% |
| unsafe | isolated | 9.99 | 10.22 | 2.3% | 5.99 | 6.54 | 9.2% |
| unsafe | whole | 9.99 | 10.14 | 1.5% | 6.13 | 6.75 | **10.1% ✗** |
| verus | isolated | 10.00 | 10.16 | 1.6% | 6.34 | 6.71 | 5.9% |
| verus | whole | 9.95 | 10.17 | 2.2% | 6.14 | 6.60 | 7.5% |
| c-gcc-h | isolated | 7.16 | 7.37 | 2.9% | 4.90 | 5.23 | 6.8% |
| c-gcc-h | whole | 7.27 | 7.54 | 3.8% | 4.90 | 5.15 | 5.1% |
| c-clang-h | isolated | 9.90 | 10.12 | 2.2% | 5.96 | 6.65 | **11.5% ✗** |
| c-clang-h | whole | 9.85 | 10.07 | 2.3% | 6.23 | 6.71 | 7.7% |

**5 of 32 wall-clock cells exceed the 10% min-to-median spread threshold and are DISCARDED** per `.memory/03-measurement.md` step 4. They are printed above marked ✗ rather than deleted, because a missing cell that looks like an omission is worse than a documented failure (`.memory/02-bench-rules.md`). **No claim in this report rests on a marked row.**

- `c-gcc / isolated` on `small.bin`: spread 10.1%
- `c-gcc / whole` on `small.bin`: spread 12.8%
- `safe_naive / whole` on `small.bin`: spread 10.9%
- `unsafe / whole` on `small.bin`: spread 10.1%
- `c-clang-h / isolated` on `small.bin`: spread 11.5%


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 6 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `degenerate.bin`
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `degenerate.bin`
- `O0 / whole` on `large.bin`
- `O3 / isolated` on `degenerate.bin`
- `O3 / whole` on `degenerate.bin`
