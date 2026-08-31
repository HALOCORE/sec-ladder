# p25-realloc-growth — results

Generated 2026-08-31T17:00:38Z from `results/p25-realloc-growth.json` (git `bcfdfb94747d`, working tree dirty).

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
| adversarial-lateread.bin | 200,000 | 66 | 66 | False | n_iters=200000 stride=58 n_blob=58 nwin=1 calls=200000 work/call=58B san=fires truncated=False expected=14062580838451436544 |
| adversarial-many.bin | 20,000 | 176 | 176 | False | n_iters=20000 stride=168 n_blob=168 nwin=1 calls=20000 work/call=168B san=fires truncated=False expected=418471180153818624 |
| adversarial-move.bin | 200,000 | 56 | 56 | False | n_iters=200000 stride=48 n_blob=48 nwin=1 calls=200000 work/call=48B san=fires truncated=False expected=11296769385036522496 |
| adversarial-nogrow.bin | 200,000 | 36 | 36 | False | n_iters=200000 stride=28 n_blob=28 nwin=1 calls=200000 work/call=28B san=clean truncated=False expected=16907751744586910720 |
| adversarial-stride3.bin | 200,000 | 38 | 38 | False | n_iters=200000 stride=3 n_blob=30 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| degenerate.bin | 200,000 | 298 | 298 | False | n_iters=200000 stride=290 n_blob=290 nwin=1 calls=200000 work/call=290B san=clean truncated=False expected=14970537519737710592 |
| large.bin | 20,000 | 15,624 | 15,624 | False | n_iters=20000 stride=244 n_blob=15616 nwin=64 calls=20000 work/call=244B san=clean truncated=False expected=7796663744873786006 |
| small.bin | 200,000 | 424 | 424 | False | n_iters=200000 stride=52 n_blob=416 nwin=8 calls=200000 work/call=52B san=clean truncated=False expected=18234900705708003722 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE SAFETY LINE, and the only thing c/kernel.c omits: ONE conjunct on the READ path, `} else if (curbase == toks) {` in c/kernel_hardened.c, with a re-derive `v = (uint64_t)toks[curi];` in the `else` it guards. c/kernel.c is otherwise character-identical, and ../controls/safety_line.py preprocesses both shipped files and measures the difference rather than asserting it.
  - `rust` — THE SAFETY LINE HAS NO SITE IN ANY RUST RUNG, AND THAT IS THE ROW'S RESULT AND NOT AN OMISSION. ⚠⚠ R2 and R3 cannot hold `&toks[curi]` across `toks.push(a)` at all, and R4 and R5 could hold a raw `*const u8` but must not: `identity` pins R4 to R5, and Verus cannot license `*cur` because the permission is not obtainable for a `Vec`'s buffer and because address equality does not imply provenance equality. ../controls/rust_bug.py builds the excluded arm and measures it under Miri.
- **required** — *per language:*
  - `c` — THE SAVED REFERENCE IS AN INTERIOR POINTER, in both C rungs: `cur = &toks[curi];` beside `curbase = toks;`. The base and the index are MAINTAINED IN BOTH RUNGS and consulted only by the hardened one, which is what makes the two files differ by the conjunct and nothing else.
  - `rust` — THE SAVED REFERENCE IS AN INDEX, in all four Rust rungs: `curi = (a as usize) % toks.len();`. ⚠ There is no `curbase` in any Rust rung because there is nothing for it to guard -- that is the one place the rungs are not isomorphic and the why key argues it.
- **required** — *per language:*
  - `c` — THE GROWTH IS A REAL `realloc` OF THE TOKEN VECTOR, in both C rungs: `nt = (uint8_t *)realloc(toks, nc);` with `nc = tcap ? tcap * 2 : P25_SEED;`. A fixed-extent array or an arena would leave the stale use inside a live allocation and the row would be p32's.
  - `rust` — the growth, in all four Rust rungs, spelled as the language spells it: `toks.push(a);`. ⚠ `Vec::push` is a `realloc` through the same system allocator, with the same doubling policy and a different starting capacity; the why key prices the difference and NOTES.md 5 measures it.
- **required** — *per language:*
  - `c` — THE SECOND LIVE GROWABLE ALLOCATION, in both C rungs, and it is what stops the first extending in place: `ns = (uint8_t *)realloc(strs, nc);`. Without it the token vector is the newest allocation, glibc extends it and the undefined behaviour is unobservable -- which is exactly the topology TASK_134 measured and mistook for a fact about C.
  - `rust` — the same second vector, in all four Rust rungs: `strs.push(a);`.
- **required** — *per language:*
  - `c` — THE CAPACITY GUARD, in both C rungs: `ntok < P25_MAXCAP` and `nstr < P25_MAXCAP`, so a push past the bound folds SENT in EVERY rung including R1 and the bug is not a write out of bounds.
  - `rust` — the same guard, in all four Rust rungs, with no capacity variable at all: `toks.len() < MAXCAP` and `strs.len() < MAXCAP`. ⚠ The equivalence is exact and load-bearing: MAXCAP is SEED * 2**k, so growth at `n == cap` from `cap = SEED` makes the acceptance guard fire at exactly `n == MAXCAP`.
- **required** — *per language:*
  - `c` — THE READ IS GUARDED AGAINST HAVING NO SAVED REFERENCE, in both C rungs: `if (cur == NULL)`, folding SENT. So R1's bug is not 'dereference an uninitialised pointer'.
  - `rust` — the same guard, in all four Rust rungs, over the flag the index needs: `if have {`.
- **required** — *per language:*
  - `c` — the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the additive form's overflow never arises: `if (len - p < 2)` in both C rungs.
  - `rust` — the cursor guard, subtraction-first: `if len - p < 2 {` in R2, R4 and R5. ⚠ R3 does not write it -- `chunks_exact(2).take(nops)` carries the same bound inside the iterator, and the walk is the R3 lever the why key leaves deliberately unpinned.
- **required** — *per language:*
  - `c` — the opcode is `c % 4`, so EVERY byte value is a legal opcode and no input is rejected for being malformed: `c % 4 == 0` in both C rungs.
  - `rust` — the opcode, `c % 4`, in all four Rust rungs -- spelled `c % 4 == 0` in R2, R4 and R5 and `match c % 4 {` in R3, which is the R3 lever.
- **required** — *per language:*
  - `c` — the fold is a serial Horner chain over `acc`, spelled with the literal multiplier, ONCE per operation: `acc = acc * 31 + v;` in both C rungs.
  - `rust` — the fold, in all four Rust rungs, spelled with the literal multiplier: `acc.wrapping_mul(31).wrapping_add(`.
- **required** — *per language:*
  - `c` — the two vector lengths are folded last, so a rung that accepted a different number of pushes cannot produce the same checksum: `return acc * 31 + (uint64_t)(ntok + nstr);` in both C rungs.
  - `rust` — the same, in all four Rust rungs: `acc.wrapping_mul(31).wrapping_add((toks.len() + strs.len()) as u64)`.
- **FORBIDDEN** — `transmute`
- **FORBIDDEN** — `with_capacity`
- **FORBIDDEN** — `reserve_exact`
- **FORBIDDEN** — `as_ptr()`
- **FORBIDDEN** — `as_mut_ptr()`
- **FORBIDDEN** — `ManuallyDrop`
- **FORBIDDEN** — `mem::forget`
- **FORBIDDEN** — `Box::leak`
- **FORBIDDEN** — `Rc<`
- **FORBIDDEN** — `calloc(`
- **FORBIDDEN** — `memmove(`
- **FORBIDDEN** — `alloca(`

> **Why**: POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ONE OMITTED CONJUNCT ON THE READ PATH, AND THE HARM IS A READ OF STORAGE `realloc` TOOK BACK. The kernel saves `cur = &toks[curi]`, a later push grows the token vector, and `realloc` retires the old block as a SIDE EFFECT OF GROWTH -- the program never calls `free` on it. THAT IS THE C-MECHANISM DISTINCTION THIS ROW RESTS ON: p27's, p29's and p32's stale use follows an explicit free() of a whole object or a handle the read failed to revalidate, and p34's follows an explicit free() a refcount selected; p25 calls free() on nothing but the two vectors at the end, and what is stale is an INTERIOR pointer into the middle of a container. Measured rather than asserted (controls/no_reloc.py, re-derived every run, with comments and string literals blanked first): `realloc` is called by EXACTLY ONE pattern's c/ and it is this one, 1 of 32, and only 5 of 32 call `malloc` at all (p27, p28, p29, p34, p42). ⚠ .temp/mgr155/NOTES.md §6 published *p10 p27 p28 p29 p32 p42, 6 of 30* from a RAW grep, and both halves of that are wrong: p10's and p32's hits are PROSE -- p32's own kernel.h says *neither malloc'd nor free'd per use* -- and p34, which really does allocate, is missing. ⚠ And `free` is called by 32 of 32, because every c/main.c frees the driver payload, so *calls free* is not a distinguishing token and this row's distinction is stated about the KERNEL. ⚠⚠ THE HARDENED CELL RE-DERIVES IN ITS `else` BRANCH AND THAT IS FORCED, NOT CHOSEN. A rung that folded SENT on relocation would make the kernel's ANSWER a function of the ALLOCATOR -- model.py could not derive the checksum without simulating glibc, and the four Rust rungs, whose `Vec` grows on a different schedule, could not agree with the C ones on the adversarial input, so check.py stage 2 would be unsatisfiable in principle. Re-deriving is allocator-independent because `realloc` COPIES: `toks[curi]` after the move is the byte `*cur` named before it. ⚠ SO THE CONJUNCT BUYS MEMORY SAFETY AND BUYS NOTHING ELSE -- both branches compute the same value in every terminating execution -- which is why the R1-vs-R1h gradient is a clean price for memory safety alone. ⚠⚠ AND THE CONJUNCT IS NOT THE STANDARD-CLEAN REPAIR. C11 7.22.3.5p4 with DR 400 makes `cur` indeterminate the moment `realloc` returns, WHETHER OR NOT THE BLOCK MOVED, so the surviving `*cur` in the true branch is a use of an indeterminate value under the abstract machine even though no relocating allocator can observe it -- ASan moves on every realloc, so under ASan the true branch is taken only when no realloc happened at all. The standard-clean rung is the UNCONDITIONAL RE-DERIVE, i.e. the addressing-mode change TASK_134's kill named; controls/rederive.py builds it and prices it. BOTH HALVES OF THAT OLD KILL ARE ANSWERED AND THEY GO OPPOSITE WAYS: the conjunct EXISTS (the first half is refuted, and the shipped diff is it) and it is INSUFFICIENT (the second half is vindicated, for a reason nobody had stated). THE HARM WINDOW IS ONE GROWTH WIDE AND SAYING OTHERWISE MISLEADS. glibc's minimum chunk gives a 4-byte malloc 24 usable bytes, so 4->8 and 8->16 are satisfied in place and it is 16->32 that has to move, and only because the string vector was allocated after the token vector and is still live. The adversarial windows are TUNED to that growth; controls/reloc_probe.py measures which growth relocates under the SHIPPED driver rather than under a hand-rolled one, which is the mistake TASK_134 made. ⚠ ASan IS A BIASED INSTRUMENT FOR THIS ROW AND THE RESULT DOES NOT REST ON IT: its allocator moves on EVERY realloc, so its column would fire even under a topology where glibc never relocated. The unbiased evidence is the plain-build divergence between R1 and R1h, and NOTES.md 2 reports the two separately. It is also why model.py's derived `sanitizer_expect` models ASan and not glibc -- the gate compares against an ASan build, so modelling ASan is what makes the column checkable, and it is the CONSERVATIVE direction because every read it calls stale is a read C already calls undefined. ⚠⚠ NO BENIGN INPUT MAY GO STALE, AND IT IS ENFORCED IN THREE PLACES RATHER THAN ASSUMED: inputs/gen.py cannot emit a non-adversarial window that grows the token vector while a saved pointer is live, model.py::stale_free_problems re-derives the property from the SHIPPED blob every gate run, and controls/no_stale.py censuses the directory. ⚠ UNLIKE p34, p25's SAFETY LINE DOES EXECUTE ON EVERY BENIGN INPUT -- every READ evaluates the conjunct; what no benign input does is take the `else` branch -- so p25 has a real, non-zero benign cost gradient where p34's is 0.00, and NOTES.md 4 reports it at BOTH optimisation levels on BOTH compilers. SAFE RUST HAS NO SITE FOR THE SAFETY LINE, AND THE EVIDENCE FOR THAT IS NOT THE ERROR CODE. `&toks[curi]` cannot be held across `toks.push(a)`, so the safe port saves an INDEX -- and then `realloc` copies and the read is correct by construction, so the safe port IS the hardened rung. ⚠⚠ E0502 IS NOT DISTINGUISHING AND MUST NOT BE QUOTED AS IF IT WERE: controls/safe_arms.py compiles the &T-across-push spelling and gets E0502, AND compiles a NEGATIVE CONTROL that cannot have p25's bug -- no container, no growth, no saved reference -- and gets the same code and the same message. FOURTH TIME THIS PROJECT HAS READ A rustc CODE AS DISTINGUISHING WHEN IT WAS NOT (p25's own E0502 in the catalogue, p28's E0382/E0499, p34's E0507). ⚠ AND THE INDEX PORT HAS NO BUG AT ALL, WHICH IS A FINDING AND NOT A FAILURE: it is recorded here so nobody rediscovers it as new. WHAT THE R5 PROVES AND WHAT IT DOES NOT. ⚠⚠ THE TEMPORAL OBLIGATION HAS NO ANALOGUE AT R5 BECAUSE NO RUNG ABOVE R1 CAN HOLD THE STALE INTERIOR POINTER. Reading `*cur` needs a PointsTo permission, and no vstd API at the pin yields one for a `Vec`'s buffer; and the guard `curbase == toks.as_ptr()` is an ADDRESS comparison while Verus's pointers carry PROVENANCE, so address equality does not entail that the permission you hold names that byte -- the guard is exactly the fact the proof would need and exactly the fact address equality does not give. What is left is the spatial residue `have ==> curi < toks@.len()`, easy because a vector only grows. SO p25 IS THE FIRST ROW IN THIS TREE WHERE THE LADDER DELETES THE BUG ABOVE R1 RATHER THAN MAKING IT PROVABLE, AND THE HONEST STATEMENT IS THAT ITS R5 OBLIGATION IS SMALLER THAN p27's, p29's, p32's OR p34's. controls/rust_bug.py builds the R4 that DOES hold the pointer and measures it under Miri, so the claim is a measurement; controls/proof_mutants.py is the four-cell battery that says what is left is not vacuous. ⚠ p25's R5 IS ALSO THE FIRST IN THIS TREE TO CALL `Vec::push` IN EXEC CODE -- measured, not assumed -- and vstd's assume_specification for it carries `final(vec)@ == old(vec)@.push(value)` with NO `requires` at all, so the growth costs no trusted item; group_vec_axioms is what ties `vec.len()` to `vec@.len()` and no other pattern in the tree needs it. TCB IS FOUR ITEMS, THREE FEWER THAN p27's AND p34's SEVEN, and the reason is the same fact: this rung allocates through `Vec`, whose allocation and deallocation are vstd's problem rather than this file's, so there is no rec_alloc/rec_free pair to trust. WHAT IS DELIBERATELY NOT PINNED is how R3 walks the op stream -- `chunks_exact(2).take(nops)` against R2's cursor, and `match c % 4` against R2's `if` chain -- exactly as p32 leaves its handle-register spelling unpinned, p34 leaves its op walk and p14 leaves its fold loop. That is the R3 lever, it costs zero TCB, and NOTES.md 5 reports what it moves. ⚠ The consequence for the cursor-guard entry above is stated there rather than left implicit: R2, R4 and R5 write `if len - p < 2 {` and R3 does not write it at all, because the iterator carries the same bound. ⚠ THE `forbidden` LIST PINS THE GROWTH ITSELF: `with_capacity` and `reserve_exact` are excluded so that no Rust rung can pre-allocate the relocation away, and `as_ptr()`/`as_mut_ptr()` are excluded so that no Rust rung can reconstruct the interior pointer the identity pin forbids. `Rc<` is forbidden here and REQUIRED in p34 for the mirror-image reason: on p34 the library IS the comparison, and on this row it would move the storage decision into a library that has nothing to do with growth. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p25-realloc-growth.json`, contract `c41099be4dfd`.

`67` backticked spelling(s) over `6` rung(s) → **208** (spelling, rung) pair(s), **86** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 24 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 10 spelling(s) pin nothing**, 10 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - pins nothing — `&toks[curi]` (required[0], rust, 0 of 4 rungs)
  - pins nothing — `*const u8` (required[0], rust, 0 of 4 rungs)
  - pins nothing — `identity` (required[0], rust, 0 of 4 rungs)
  - pins nothing — `*cur` (required[0], rust, 0 of 4 rungs)
  - pins nothing — `curbase` (required[1], rust, 0 of 4 rungs)
  - pins nothing — `Vec::push` (required[2], rust, 0 of 4 rungs)
  - pins nothing — `realloc` (required[2], rust, 0 of 4 rungs)
  - pins nothing — `n == cap` (required[4], rust, 0 of 4 rungs)
  - pins nothing — `cap = SEED` (required[4], rust, 0 of 4 rungs)
  - pins nothing — `n == MAXCAP` (required[4], rust, 0 of 4 rungs)
  - absent — `} else if (curbase == toks) {` (required[0], c, **c/kernel.c**)
  - absent — `v = (uint64_t)toks[curi];` (required[0], c, **c/kernel.c**)
  - absent — `if len - p < 2 {` (required[6], rust, **safe_tuned.rs**)
  - absent — `chunks_exact(2).take(nops)` (required[6], rust, **safe_naive.rs**)
  - absent — `chunks_exact(2).take(nops)` (required[6], rust, **unsafe.rs**)
  - absent — `chunks_exact(2).take(nops)` (required[6], rust, **verus.rs**)
  - absent — `c % 4 == 0` (required[7], rust, **safe_tuned.rs**)
  - absent — `match c % 4 {` (required[7], rust, **safe_naive.rs**)
  - absent — `match c % 4 {` (required[7], rust, **unsafe.rs**)
  - absent — `match c % 4 {` (required[7], rust, **verus.rs**)
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
| c-gcc | 175 | 165 | 0 | 653 | 141,101,471 | 63,469,080 | 3,000,056 | 300,056 | `b061f12e` | `b061f12e` | yes | - |
| c-clang | 156 | 150 | 1 | 634 | 148,161,740 | 65,292,300 | 2,800,055 | 280,055 | `00456a51` | `35b45aae` | yes | - |
| safe_naive | 245 | 241 | 2 | 1,038 | 196,278,045 | 95,483,538 | 2,800,275 | 280,275 | `02b9c012` | `b6237c94` | yes | - |
| safe_tuned | 217 | 213 | 7 | 905 | 157,921,319 | 75,801,415 | 2,800,275 | 280,275 | `94ba846e` | `bfe5fd0a` | yes | - |
| unsafe | 189 | 189 | 1 | 751 | 170,010,087 | 83,037,860 | 2,800,275 | 280,275 | `b35af684` | `6ad46989` | yes | - |
| verus | 189 | 189 | 1 | 751 | 170,010,087 | 83,037,860 | 2,800,270 | 280,270 | `6dbbc8bd` | `b10967cd` | yes | - |
| c-gcc-h | 187 | 176 | 0 | 732 | 146,053,580 | 66,736,646 | 3,000,056 | 300,056 | `5006cf88` | `5006cf88` | yes | - |
| c-clang-h | 167 | 162 | 1 | 652 | 151,918,608 | 67,146,186 | 2,800,055 | 280,055 | `43b86fba` | `a7298cc6` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 219 | 218 | 0 | 1,002 | 275,455,826 | - | 7,200,066 | - | `ac0e71d2` | `ac0e71d2` | yes | - |
| c-clang | 209 | 209 | 1 | 1,007 | 283,931,186 | - | 4,200,052 | - | `2b6ef866` | `d2d71cb2` | yes | - |
| safe_naive | 337 | 337 | 9 | 1,911 | 342,261,490 | - | 5,000,077 | - | `ffa5c127` | `cd734812` | yes | - |
| safe_tuned | 392 | 392 | 2 | 2,206 | 340,358,579 | - | 5,000,077 | - | `3b3566f7` | `bfc868a6` | yes | - |
| unsafe | 313 | 313 | 1 | 1,791 | 362,590,864 | - | 5,000,077 | - | `a49ed7c6` | `fa964a78` | yes | - |
| verus | 313 | 313 | 1 | 1,791 | 362,590,864 | - | 5,000,056 | - | `76d0c154` | `06259873` | yes | - |
| c-gcc-h | 229 | 228 | 0 | 1,044 | 278,357,770 | - | 7,200,066 | - | `1945092a` | `1945092a` | yes | - |
| c-clang-h | 218 | 218 | 0 | 1,040 | 287,558,616 | - | 4,200,052 | - | `04c5915a` | `04c5915a` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 390 | 384 | 2 | 1,620 | - | - | 141,987,134 | 65,460,868 | `239dac69` | `a5082aee` | yes | - |
| c-clang | 386 | 379 | 0 | 1,610 | - | - | 155,554,083 | 69,047,028 | `ba28106b` | `ba28106b` | yes | xmm |
| safe_naive | 883 | 871 | 1 | 4,063 | - | - | 203,682,630 | 98,981,663 | `bf62fbfc` | `fe5f898c` | yes | xmm |
| safe_tuned | 859 | 850 | 1 | 3,919 | - | - | 166,579,431 | 80,261,422 | `71609828` | `384a4b00` | yes | xmm |
| unsafe | 820 | 808 | 1 | 3,759 | - | - | 180,410,368 | 87,918,141 | `2cf5aeca` | `0feaa08c` | yes | xmm |
| verus | 827 | 815 | 1 | 3,727 | - | - | 180,410,366 | 87,918,139 | `226a8822` | `de2ee2cc` | yes | xmm |
| c-gcc-h | 406 | 400 | 1 | 1,720 | - | - | 145,753,962 | 66,649,299 | `20037100` | `188ee09a` | yes | - |
| c-clang-h | 395 | 390 | 0 | 1,642 | - | - | 159,639,517 | 71,704,957 | `b423b448` | `b423b448` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 275,455,826 | - | 7,200,066 | - | `b245663a` | `b245663a` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 282,177,178 | - | 4,200,051 | - | `713f4207` | `713f4207` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 342,261,490 | - | 5,000,077 | - | `51ba1697` | `463b0315` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 340,358,579 | - | 5,000,077 | - | `b3bf4b64` | `fccc2cc9` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 362,590,864 | - | 5,000,077 | - | `a76f0991` | `4679a6e8` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 362,590,864 | - | 5,000,056 | - | `21eb0010` | `8c232477` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 278,357,770 | - | 7,200,066 | - | `4da740d6` | `4da740d6` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 285,804,608 | - | 4,200,051 | - | `faf64f22` | `faf64f22` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 313/313 vs 313/313 | 1 B vs 1 B |
| unsafe vs verus | O3 | no | **yes** | no | 189/189 vs 189/189 | 1 B vs 1 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 18.11 | 18.47 | 2.0% | 23.53 | 24.06 | 2.2% |
| c-gcc | whole | 17.35 | 17.74 | 2.3% | 23.38 | 23.77 | 1.6% |
| c-clang | isolated | 19.53 | 19.79 | 1.3% | 21.87 | 22.32 | 2.0% |
| c-clang | whole | 19.92 | 20.26 | 1.7% | 21.46 | 22.06 | 2.8% |
| safe_naive | isolated | 20.35 | 20.62 | 1.3% | 24.35 | 25.01 | 2.7% |
| safe_naive | whole | 20.89 | 21.33 | 2.1% | 24.11 | 24.81 | 2.9% |
| safe_tuned | isolated | 20.01 | 20.50 | 2.4% | 22.38 | 23.02 | 2.9% |
| safe_tuned | whole | 20.17 | 20.66 | 2.4% | 23.43 | 23.99 | 2.4% |
| unsafe | isolated | 20.93 | 21.35 | 2.0% | 23.56 | 24.10 | 2.3% |
| unsafe | whole | 21.78 | 22.17 | 1.8% | 23.51 | 24.31 | 3.4% |
| verus | isolated | 21.45 | 21.76 | 1.5% | 22.86 | 23.81 | 4.1% |
| verus | whole | 21.99 | 22.50 | 2.3% | 23.87 | 24.90 | 4.3% |
| c-gcc-h | isolated | 17.97 | 18.29 | 1.8% | 23.77 | 24.47 | 2.9% |
| c-gcc-h | whole | 20.36 | 20.51 | 0.8% | 23.98 | 24.40 | 1.7% |
| c-clang-h | isolated | 20.10 | 20.44 | 1.7% | 21.67 | 22.21 | 2.5% |
| c-clang-h | whole | 20.11 | 20.37 | 1.3% | 22.23 | 22.90 | 3.0% |

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
