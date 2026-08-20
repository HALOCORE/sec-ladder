# p14-field-split — results

Generated 2026-08-20T16:02:34Z from `results/p14-field-split.json` (git `59267028e55c`, working tree dirty).

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
| adversarial-alt33.bin | 8 | 81 | 81 | False | n_iters=8 stride=73 n_blob=73 nwin=1 calls=8 work/call=73B san=fires truncated=False expected=8006196804099674112 |
| adversarial-full65.bin | 8 | 80 | 80 | False | n_iters=8 stride=72 n_blob=72 nwin=1 calls=8 work/call=72B san=fires truncated=False expected=14129561520256 |
| adversarial-many.bin | 8 | 220 | 220 | False | n_iters=8 stride=212 n_blob=212 nwin=1 calls=8 work/call=212B san=fires truncated=False expected=3752889374227114752 |
| adversarial-run17.bin | 8 | 34 | 34 | False | n_iters=8 stride=26 n_blob=26 nwin=1 calls=8 work/call=26B san=fires truncated=False expected=16846452602349536768 |
| adversarial-stride3.bin | 8 | 38 | 38 | False | n_iters=8 stride=3 n_blob=30 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| degenerate.bin | 8 | 164 | 164 | False | n_iters=8 stride=156 n_blob=156 nwin=1 calls=8 work/call=156B san=clean truncated=False expected=14373129391870606336 |
| large.bin | 20,000 | 5,200,008 | 5,200,008 | False | n_iters=20000 stride=104 n_blob=5200000 nwin=50000 calls=20000 work/call=104B san=clean truncated=False expected=4888060440850947966 |
| small.bin | 60,000 | 13,256 | 13,256 | False | n_iters=60000 stride=207 n_blob=13248 nwin=64 calls=60000 work/call=207B san=clean truncated=False expected=12427448828275423027 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE SAFETY LINE, and the only line c/kernel.c omits: `if (nt == MAXTOK)` in c/kernel_hardened.c. c/kernel.c omits exactly this and nothing else, so the scoped-absent audit pair this entry reports is on that rung and is correct.
  - `rust` — THE SAFETY LINE: `if nt == MAXTOK {` in all four Rust rungs. In Rust it is a SEMANTIC line and not a safety line -- rustc's bounds check on `tl[nt]` is what makes the safe rungs safe -- so no Rust-vs-Rust comparison moves on it; see the why key.
- **required** — *per language:*
  - `c` — ...and the break that makes it a TRUNCATION rather than a skip, which is the answer the contract pins: `break;` in c/kernel_hardened.c.
  - `rust` — ...and the break that makes it a TRUNCATION rather than a skip, which is the answer the contract pins: `break;` in all four Rust rungs.
- **required** — *per language:*
  - `c` — THE CLAMP, present in EVERY rung including R1, so the COPY and the SCAN are bounded in every rung and the bug is the field count alone: `m = llen < SCR ? llen : SCR;` in both C rungs.
  - `rust` — THE CLAMP, present in EVERY rung, so the COPY and the SCAN are bounded in every rung and the bug is the field count alone: `let m: usize = if llen < SCR { llen } else { SCR };` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the scratch is a FIXED-SIZE LOCAL of SCR bytes, never an allocation and never a length from the file: `uint8_t scr[SCR];` in both C rungs.
  - `rust` — the scratch is a FIXED-SIZE LOCAL of SCR bytes, never an allocation and never a length from the file: `let mut scr: [u8; SCR] = [0; SCR];` in all four Rust rungs.
- **required** — *per language:*
  - `c` — THE FIELD TABLE is a FIXED-SIZE LOCAL of MAXTOK entries -- it is the destination the bug overflows and its extent is a compile-time constant, so R1's overrun is a property of the PROGRAM and not of an allocation the input chose: `size_t tl[MAXTOK];` in both C rungs.
  - `rust` — THE FIELD TABLE is a FIXED-SIZE LOCAL of MAXTOK entries -- it is the destination the bug overflows and its extent is a compile-time constant: `let mut tl: [usize; MAXTOK] = [0; MAXTOK];` in all four Rust rungs.
- **required** — *per language:*
  - `c` — ...and both are ZERO-INITIALISED ON EVERY CALL, so a rung's answer cannot depend on what the frame happened to hold: `memset(scr, 0, sizeof scr);` in both C rungs.
  - `rust` — ...and both are ZERO-INITIALISED ON EVERY CALL, so a rung's answer cannot depend on what the frame happened to hold: `[0; SCR];` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the load into the scratch is a BULK copy in every rung, so the measured difference is the SPLIT and not the load: `memcpy(scr, buf + off + p, m);` in both C rungs.
  - `rust` — the load into the scratch is a BULK copy in every rung, so the measured difference is the SPLIT and not the load: `.copy_from_slice(&src[from..from + n]);` in all four Rust rungs -- same call, same operands, same order, in the body of scr_load. THE RECEIVER IS SCOPED 2-AND-2, p06's TASK_048 scoping inherited: `dst[..n]` is the receiver in safe_naive.rs and safe_tuned.rs, and `s.split_at_mut(n)` is the receiver in unsafe.rs and verus.rs, because `..n` is a RangeTo<usize> and RangeTo has NO SliceIndexSpecImpl at the pinned vstd, so dst[..n] cannot be VERIFIED at all and R4 follows R5 because the identity pin makes them one program. The price is measured in ../NOTES.md 6a.
- **required** — *per language:*
  - `c` — THE VIRTUAL DELIMITER: the scan treats the end of the line as a separator, which is what makes the TAIL field arrive at the SAME call site as every other field and therefore what keeps the safety line to ONE line: `if (i == m || scr[i] == DELIM)` in both C rungs.
  - `rust` — THE VIRTUAL DELIMITER: the scan treats the end of the line as a separator, which is what makes the TAIL field arrive at the SAME call site as every other field and therefore what keeps the safety line to ONE line: `if i == m ||` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the scan IS BOUNDED by the live extent in EVERY rung, R1 included -- p14 is NOT p11, and this entry is what says so by grep: `while (i <= m)` in both C rungs.
  - `rust` — the scan IS BOUNDED by the live extent in EVERY rung, R1 included -- p14 is NOT p11, and this entry is what says so by grep: `while i <= m {` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the field length is bound to a LOCAL before the store, which is what keeps -O0 identity at norel (see the why key): `flen = i - s;` in both C rungs.
  - `rust` — the field length is bound to a LOCAL before the store, which is what keeps -O0 identity at norel (see the why key): `let flen: usize = i - s;` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the fold folds each field's LENGTH, in order, spelled with the literal multiplier: `acc = acc * 31 + (uint64_t)tj;` in both C rungs.
  - `rust` — the fold folds each field's LENGTH, in order: `.wrapping_add(tj as u64)` in all four Rust rungs.
- **required** — *per language:*
  - `c` — ...and each field's CONTENT, in order, over the full recorded extent: `acc = acc * 31 + (uint64_t)scr[cur + q];` in both C rungs.
  - `rust` — ...and each field's CONTENT, in order, over the full recorded extent, spelled with the literal multiplier: `.wrapping_mul(31)` in all four Rust rungs. safe_tuned.rs spells the LOOP as .iter().fold() over a reslice, which is why only the operation and not the loop form is pinned here.
- **required** — ...and the cursor STEPS OVER THE DELIMITER between fields, which is what makes the recorded lengths a PARTITION of the line rather than a set of overlapping ranges: `cur = cur + tj + 1;` in all seven rungs.
- **required** — *per language:*
  - `c` — the FIELD COUNT is folded, so a rung that truncated at a different MAXTOK -- or not at all -- cannot produce the same checksum: `acc = acc * 31 + (uint64_t)nt;` in both C rungs.
  - `rust` — the FIELD COUNT is folded, so a rung that truncated at a different MAXTOK -- or not at all -- cannot produce the same checksum: `.wrapping_add(nt as u64)` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the declared line count is folded, so a rung that walked a different number of lines cannot produce the same checksum either: `* 31 + (uint64_t)nline` in both C rungs.
  - `rust` — the declared line count is folded, so a rung that walked a different number of lines cannot produce the same checksum either: `.wrapping_add(nline as u64)` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the cursor guards are SUBTRACTION-FIRST, which is what keeps the kernel's requires at ONE clause -- p <= len is maintained by the guards themselves so the subtraction cannot wrap, while the additive form p + 4 > len overflows usize and Verus rejects it: `if (len - p < 4)` in both C rungs.
  - `rust` — the cursor guards are SUBTRACTION-FIRST, which is what keeps the kernel's requires at ONE clause -- p <= len is maintained by the guards themselves so the subtraction cannot wrap, while the additive form p + 4 > len overflows usize and Verus rejects it: `if len - p < 4 {` in all four Rust rungs.
- **required** — ...and the second guard, which bounds the line's declared length by what the window holds: `len - p < llen` in all seven rungs.
- **required** — the little-endian u32 decode is written out with + and * rather than | and <<, so it stays linear arithmetic: `+ 65536 *` in all seven rungs.
- **required** — ...and its top byte: `+ 16777216 *` in all seven rungs.
- **FORBIDDEN** — `.split(`
- **FORBIDDEN** — `.split_terminator(`
- **FORBIDDEN** — `.splitn(`
- **FORBIDDEN** — `strtok(`
- **FORBIDDEN** — `strsep(`
- **FORBIDDEN** — `memchr(`
- **FORBIDDEN** — `from_le_bytes`
- **FORBIDDEN** — `chunks_exact`

> **Why**: each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). THE ONLY THING R1 OMITS IS THE FIELD-COUNT BOUND: the clamp `m = min(llen, SCR)` is present in every rung, so the COPY is bounded in every rung; the scan bound `i <= m` is present in every rung, so every read of `scr` is in bounds in every rung; both cursor guards are present in every rung, so `p` never leaves the window in any rung. R1-vs-R1h is therefore the cost of `if (nt == MAXTOK) break;` and nothing else. THE BOUND IS A COUNT OF A BYTE VALUE AND THAT IS WHY THIS PATTERN EXISTS: `nt` is one more than the number of DELIM bytes in `scr[0..m)`, which nothing in the wire format declares and no length bounds -- a 64-byte line holds between 1 and 65 fields against a 16-entry table -- so the guard cannot be hoisted out of the scan, folded into a length check or derived from the header, which is what every earlier pattern's guard could be. THE VIRTUAL DELIMITER `i == m` IS PART OF THE PINNED CONTRACT AND NOT A MATTER OF TASTE: it is what makes the TAIL field arrive at the same call site as every other field, and therefore what keeps the safety line to ONE line. A spelling that appends the tail separately needs the guard TWICE, and then R1-vs-R1h stops being a one-line difference and the pattern stops measuring what it says it measures. It is also what makes a TRAILING delimiter produce a trailing EMPTY field, which `degenerate.bin` exercises and which a `while i < m` scan silently drops. TRUNCATION AT MAXTOK IS THE SPECIFIED ANSWER, not an evasion: `ntok()` in verus.rs is `min(len(toks), MAXTOK)` and model.py takes `split(...)[:MAXTOK]`, so the checked rungs cannot disagree about it. It is what strtok, getopt, argv splitters and every fixed-table CSV reader do, and it is p13's shape one level up -- the hardened cell is memory-safe and LOSES DATA. `.split(`, `.split_terminator(` and `.splitn(` are forbidden because each is a single library call that deletes the SCAN this pattern measures: the per-field and per-byte decomposition, the sweep bands over `llen` and over the field count, and the whole amortisation result are statements about an explicit cursor scan, and a rung using one of them would measure `core::slice::Split`'s codegen instead, which is p11's comparison wearing p14's label. AND THE PROVER ALREADY EXCLUDES THEM FROM R4: the pinned vstd has no `assume_specification` for `<[T]>::split` at all (`vstd/std_specs/slice.rs` specifies `split_at`, `split_at_mut` and `split_at_checked` and nothing else), so an R4 using it could not have a verifying R5 twin and would not be a rung -- the `identity`-pin trap this block's own `identity` key sets, and p11's R4-by-permission result on a third pattern. That exclusion therefore costs NOTHING to keep, and ../NOTES.md 8 publishes the measurement rather than the assertion. `strtok(`, `strsep(` and `memchr(` are forbidden for the C rungs, and these ARE fiats with published prices rather than exclusions the prover makes -- C has no prover. `strtok` is forbidden because it COLLAPSES runs of delimiters, so a rung using it computes a DIFFERENT PARTITION of the same bytes; that difference is p14's headline and it belongs in an adversarial row and a priced control, not in a rung, because a rung that collapsed would disagree with model.py on `adversarial-run17` for a reason that is not the bug. `strsep` computes the same partition this kernel does but MUTATES ITS INPUT, and under the driver's repeat protocol that measures the WRONG WORKLOAD rather than being unmeasurable (../NOTES.md 0a; this sentence used to read `which the driver's repeat protocol forbids` and that is RETRACTED as of TASK_050, measured: nothing in harness/ enforces purity, the mutating kernel reaches a steady state after exactly ONE call and its measure.py marginal is exactly 9044.0000 Ir/call with zero residual -- what breaks is that calls 2..n tokenise an ALREADY-TOKENISED buffer, one field per line instead of four, so the benchmark would report a per-call cost for an operation the pattern does not name). `memchr` moves the scan into a libc IFUNC and makes the kernel-exclusive column a library comparison, which is p11's and p13's result and not p14's. All three are built and priced in controls/gen_controls.py and ../NOTES.md 8. `from_le_bytes` deletes the written-out little-endian header decode every rung shares AND is NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW and again on p06), so a rung using it would compare a safe cell against an unsafe cell that cannot exist. `chunks_exact` is forbidden for the fold because p16 measured that the chunk width moves that pattern's per-byte rate over a 31% range (5.04688...6.62500, `.memory/01-ladder.md`), and p14's published decomposition is into a per-copied-byte, a per-scanned-byte, a per-field and a per-line term. EVERY EXCLUSION HERE IS WHOLE-PATTERN AND NOT SCOPED TO SOME RUNGS, which is deliberate: `.memory/01-ladder.md`'s direction test fired on p13 exactly because three of its entries named some rungs and exempted `safe_tuned.rs`, so R3 was permitted a spelling R4 was forbidden and 48%/17% of the published margin was the pin. A whole-pattern exclusion keeps the two sides of the comparison equal. THE ONE SCOPED THING IN `required` IS THE LOAD'S RECEIVER, 2-AND-2, and it is p06's TASK_048 scoping inherited verbatim with its price re-measured on this pattern (../NOTES.md 6a): `dst[..n]` in safe_naive.rs and safe_tuned.rs, `s.split_at_mut(n)` in unsafe.rs and verus.rs, because `..n` is a `RangeTo<usize>` and `RangeTo` has NO `SliceIndexSpecImpl` at the pinned vstd, so the `dst[..n]` receiver cannot be VERIFIED at all and R4 follows R5 because the `identity` pin makes them one program. WHAT IS DELIBERATELY *NOT* PINNED is the SPELLING OF THE FOLD LOOP: R1, R1h, R2, R4 and R5 write an indexed `while` and R3 writes `tl[..nt].iter()` with `scr[cur..cur+tj].iter().fold(...)`, and holding those fixed would hold fixed one of the two things p14 exists to compare. What IS pinned instead is the OPERATIONS -- the field LENGTH, the field CONTENT, the cursor stepping over the delimiter, and the field COUNT, in that order. THE FOLD IS OVER THE FULL RECORDED EXTENT AND ORDER-SENSITIVE, AND p14 SUPPLIES A THIRD, INDEPENDENT REASON FOR THAT RULE. TASK_004_REVIEW's reason is ELISION: a fold that reads only part of the result lets the optimiser delete the rest. p06's is INVARIANCE: three reverses compose to a PERMUTATION, so a sum- or xor-fold could not tell the buggy scratch from the correct one. p14's is PARTITION-BLINDNESS, one level up from p06's: TOKENISING DOES NOT MOVE ANY BYTE, so every partition of the same line yields the same bytes in the same order and a fold over the concatenated CONTENT alone is identical for every possible set of field boundaries. Folding the LENGTHS IN ORDER is what makes a boundary bug visible and folding the COUNT is what makes a truncation visible; ../NOTES.md 2 tabulates which mutation each of the three catches. THE LOAD IS THE SAME BULK SPELLING IN EVERY RUNG -- `memcpy` in C and `scr_load`, whose body is the one bulk call `.copy_from_slice(&src[from..from + n]);` with the same operands in the same order, in all four Rust rungs -- so the measured difference between rungs is the SPLIT and not the load, which is p02's retraction applied in advance. THE FIELD LENGTH IS BOUND TO A LOCAL `flen = i - s` IN ALL SEVEN RUNGS AND THAT IS NOT STYLE: R5's store is a CALL and R4's is an assignment, so an expression argument is evaluated in a different order in the two and `-O0` identity drops from `norel` to `differ`. It was measured that way first and the repair is this line (../NOTES.md 6a); it is p06's TASK_048 wrinkle arriving one pattern later, and the price at -O3 is ZERO ON ALL EIGHT CELLS -- md5_fn_norel is identical with and without the entry in every one of c-gcc, c-gcc-h, c-clang, c-clang-h, safe_naive, safe_tuned, unsafe and verus (TASK_050, ../NOTES.md 6a'), so it moves no published p14 figure. At -O0 the price is NOT zero and NOT sign-neutral -- -3 static instructions on safe_naive, safe_tuned and unsafe, 0 on verus, and +1/+1/+2/+2 on c-gcc/c-gcc-h/c-clang/c-clang-h -- which is disclosed here rather than left to be found, because no p14 claim rests on an -O0 row and none may. WHEN THIS DECLARATION WAS WRITTEN, STATED EXACTLY BECAUSE p14 HAS A PRE-FLIGHT: it was written after the seven rungs, the R5 proof (19/0, twin 23/0), the `identity` pin and the checksums existed and BEFORE any p14 CELL had been measured for perf -- `harness/measure.py p14` had not been run and no `Ir` or `ns` figure for any of the eight cells existed. What DID exist is ../NOTES.md 0: `Ir`, sanitizer behaviour and checksums for a standalone SIX-KERNEL C PROBE with no driver and no pattern, which settled the bug class TASK_049 asked to be settled before five rungs were built on it. That probe is not a cell and none of its numbers is published as p14's, but it is not nothing either, and saying 'no number existed' would be false. What the probe DID influence is the CHOICE OF BUG CLASS and the wire format that expresses it; what it did not influence is any entry of `required` or `forbidden`, every one of which names a line the contract in ../spec.md's Semantics block already had. ONE ENTRY WAS HOWEVER ADDED IN RESPONSE TO A MEASUREMENT AND IT IS NAMED HERE RATHER THAN LEFT TO BE INFERRED, because a declaration that was quietly shaped by a measurement is the self-certification this whole mechanism exists to prevent: the `flen = i - s;` entry did NOT exist in the first draft, and it was added after `harness/check.py` reported `identity: unsafe vs verus O0 differ` (286 vs 289 static instructions) on a tree whose rungs wrote `tl[nt] = i - s;` directly. It is a CODEGEN measurement and not a PERF one -- no Ir or ns figure for any cell existed when it was added, and the -O3 bytes are identical with and without it (../NOTES.md 6a) -- but it is a measurement, and 'the declaration was written before anything was measured' would be false as a blanket sentence.. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p14-field-split.json`, contract `063afb50fc33`.

`58` backticked spelling(s) over `6` rung(s) → **178** (spelling, rung) pair(s), **120** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 16 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 0 spelling(s) pin nothing**, 10 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - absent — `if (nt == MAXTOK)` (required[0], c, **c/kernel.c**)
  - absent — `tl[nt]` (required[0], rust, **unsafe.rs**)
  - absent — `tl[nt]` (required[0], rust, **verus.rs**)
  - absent — `dst[..n]` (required[6], rust, **unsafe.rs**)
  - absent — `dst[..n]` (required[6], rust, **verus.rs**)
  - absent — `s.split_at_mut(n)` (required[6], rust, **safe_naive.rs**)
  - absent — `s.split_at_mut(n)` (required[6], rust, **safe_tuned.rs**)
  - absent — `..n` (required[6], rust, **unsafe.rs**)
  - absent — `..n` (required[6], rust, **verus.rs**)
  - absent — `while i <= m {` (required[8], rust, **verus.rs**)
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
| c-gcc | 188 | 184 | 0 | 715 | 234,180,000 | 41,480,000 | 900,056 | 300,056 | `c083179d` | `c083179d` | yes | xmm |
| c-clang | 215 | 205 | 1 | 776 | 176,280,000 | 34,860,000 | 840,059 | 280,059 | `38376c33` | `2c21abb4` | yes | xmm |
| safe_naive | 224 | 219 | 6 | 906 | 268,440,000 | 46,860,000 | 840,275 | 280,275 | `8b5defd1` | `3bae45d5` | yes | xmm |
| safe_tuned | 246 | 238 | 3 | 1,005 | 252,240,000 | 48,080,000 | 840,275 | 280,275 | `124646dc` | `65617c40` | yes | xmm |
| unsafe | 185 | 178 | 7 | 697 | 213,960,000 | 39,580,000 | 840,275 | 280,275 | `96d7e0c1` | `3cfea505` | yes | xmm |
| verus | 185 | 178 | 7 | 697 | 213,960,000 | 39,580,000 | 840,270 | 280,270 | `96d7e0c1` | `3cfea505` | yes | xmm |
| c-gcc-h | 190 | 187 | 0 | 708 | 248,460,000 | 43,300,000 | 900,056 | 300,056 | `1d9d1f8c` | `1d9d1f8c` | yes | xmm |
| c-clang-h | 179 | 171 | 0 | 656 | 216,060,000 | 39,600,000 | 840,059 | 280,059 | `02156a8e` | `02156a8e` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 226 | 224 | 0 | 1,168 | 392,040,000 | - | 2,160,066 | - | `48465492` | `48465492` | yes | - |
| c-clang | 179 | 179 | 1 | 998 | 364,560,004 | - | 1,260,056 | - | `2a131f05` | `686add2c` | yes | - |
| safe_naive | 349 | 349 | 11 | 2,069 | 507,480,000 | - | 1,500,077 | - | `64d324a6` | `e7470c42` | yes | - |
| safe_tuned | 347 | 347 | 11 | 2,005 | 623,880,000 | - | 1,500,077 | - | `b4cf169c` | `b7b8df6c` | yes | - |
| unsafe | 286 | 286 | 12 | 1,716 | 504,720,000 | - | 1,500,077 | - | `e15d9f1f` | `544ff2ca` | yes | - |
| verus | 286 | 286 | 12 | 1,716 | 504,720,000 | - | 1,500,056 | - | `3717b206` | `8142a829` | yes | - |
| c-gcc-h | 230 | 227 | 0 | 1,181 | 396,120,000 | - | 2,160,066 | - | `aff7b914` | `aff7b914` | yes | - |
| c-clang-h | 182 | 182 | 2 | 1,010 | 368,280,004 | - | 1,260,056 | - | `555e70f1` | `dfce6ef5` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 392 | 388 | 1 | 1,577 | - | - | 237,000,137 | 42,140,137 | `90499fcf` | `4ddfdd55` | yes | - |
| c-clang | 489 | 475 | 0 | 1,965 | - | - | 174,900,186 | 34,860,186 | `e06c0462` | `e06c0462` | yes | xmm |
| safe_naive | 849 | 836 | 1 | 3,903 | - | - | 266,880,281 | 45,740,281 | `914f337f` | `9575b44b` | yes | xmm |
| safe_tuned | 884 | 871 | 1 | 4,047 | - | - | 254,580,283 | 48,780,283 | `faa151b3` | `12541e66` | yes | xmm |
| unsafe | 811 | 799 | 1 | 3,679 | - | - | 221,400,284 | 40,040,284 | `1ccb5fb3` | `42279f40` | yes | xmm |
| verus | 825 | 812 | 1 | 3,695 | - | - | 222,360,282 | 40,720,282 | `b432e9a3` | `922c9bad` | yes | xmm |
| c-gcc-h | 393 | 390 | 1 | 1,558 | - | - | 251,700,135 | 44,220,135 | `5f036e15` | `48a22855` | yes | - |
| c-clang-h | 451 | 440 | 0 | 1,803 | - | - | 214,440,184 | 39,380,184 | `f0ecaf7f` | `f0ecaf7f` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 392,040,000 | - | 2,160,066 | - | `9501b248` | `9501b248` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 363,900,004 | - | 1,260,055 | - | `d0f0fae7` | `d0f0fae7` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 507,480,000 | - | 1,500,077 | - | `cabb1d40` | `d3813790` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 623,880,000 | - | 1,500,077 | - | `1eb5dc6d` | `3efab163` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 504,720,000 | - | 1,500,077 | - | `e275bdcf` | `a8fd7424` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 504,720,000 | - | 1,500,056 | - | `d8901cb6` | `9b2089b8` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 396,120,000 | - | 2,160,066 | - | `f7bf1b96` | `f7bf1b96` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 367,980,004 | - | 1,260,055 | - | `bb422e92` | `bb422e92` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 286/286 vs 286/286 | 12 B vs 12 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 185/178 vs 185/178 | 7 B vs 7 B |

## Wall clock (secondary)

> taskset -c 5, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 8.37 | 8.54 | 2.0% | 18.24 | 18.46 | 1.2% |
| c-gcc | whole | 8.45 | 8.78 | 3.9% | 20.64 | 21.26 | 3.0% |
| c-clang | isolated | 8.05 | 8.46 | 5.1% | 15.15 | 15.34 | 1.3% |
| c-clang | whole | 8.15 | 8.59 | 5.3% | 15.56 | 15.81 | 1.6% |
| safe_naive | isolated | 8.88 | 9.26 | 4.2% | 19.39 | 19.64 | 1.3% |
| safe_naive | whole | 8.82 | 9.05 | 2.6% | 19.26 | 19.44 | 1.0% |
| safe_tuned | isolated | 8.99 | 9.13 | 1.5% | 18.97 | 19.25 | 1.4% |
| safe_tuned | whole | 9.13 | 9.27 | 1.6% | 19.11 | 19.35 | 1.3% |
| unsafe | isolated | 8.66 | 8.83 | 2.0% | 17.57 | 17.78 | 1.2% |
| unsafe | whole | 8.63 | 8.78 | 1.8% | 18.35 | 18.60 | 1.4% |
| verus | isolated | 8.96 | 9.15 | 2.2% | 18.84 | 19.05 | 1.1% |
| verus | whole | 8.92 | 9.07 | 1.7% | 19.39 | 19.81 | 2.2% |
| c-gcc-h | isolated | 8.47 | 8.67 | 2.4% | 19.70 | 20.15 | 2.3% |
| c-gcc-h | whole | 8.62 | 8.76 | 1.7% | 19.15 | 19.38 | 1.2% |
| c-clang-h | isolated | 8.46 | 8.62 | 1.9% | 17.32 | 17.75 | 2.5% |
| c-clang-h | whole | 8.87 | 8.97 | 1.2% | 17.85 | 17.96 | 0.6% |

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
