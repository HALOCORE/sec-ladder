# p32-free-list-pool — results

Generated 2026-08-30T12:10:47Z from `results/p32-free-list-pool.json` (git `dc9ab9a56627`, working tree dirty).

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
| adversarial-alias.bin | 200,000 | 30 | 30 | False | n_iters=200000 stride=22 n_blob=22 nwin=1 calls=200000 work/call=22B san=clean truncated=False expected=8618832246808763392 |
| adversarial-doublefree.bin | 200,000 | 28 | 28 | False | n_iters=200000 stride=20 n_blob=20 nwin=1 calls=200000 work/call=20B san=clean truncated=False expected=7694399416035917824 |
| adversarial-many.bin | 200,000 | 96 | 96 | False | n_iters=200000 stride=88 n_blob=88 nwin=1 calls=200000 work/call=88B san=clean truncated=False expected=15810558800354073600 |
| adversarial-recycle.bin | 200,000 | 24 | 24 | False | n_iters=200000 stride=16 n_blob=16 nwin=1 calls=200000 work/call=16B san=clean truncated=False expected=408677925675887616 |
| adversarial-stale-read.bin | 200,000 | 20 | 20 | False | n_iters=200000 stride=12 n_blob=12 nwin=1 calls=200000 work/call=12B san=clean truncated=False expected=16295453347298233344 |
| adversarial-stride3.bin | 200,000 | 38 | 38 | False | n_iters=200000 stride=3 n_blob=30 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| degenerate.bin | 200,000 | 102 | 102 | False | n_iters=200000 stride=94 n_blob=94 nwin=1 calls=200000 work/call=94B san=clean truncated=False expected=9306778758387801088 |
| large.bin | 20,000 | 15,624 | 15,624 | False | n_iters=20000 stride=244 n_blob=15616 nwin=64 calls=20000 work/call=244B san=clean truncated=False expected=12301318280131401366 |
| small.bin | 200,000 | 424 | 424 | False | n_iters=200000 stride=52 n_blob=416 nwin=8 calls=200000 work/call=52B san=clean truncated=False expected=7818319352111584483 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE SAFETY LINE, and the only thing c/kernel.c omits: ONE conjunct at the ONE site where a handle is consumed, `} else if (gen[h] != g) {` in c/kernel_hardened.c. c/kernel.c goes straight from `if (h == NIL) {` to the opcode arms and is otherwise character-identical, so the scoped-absent audit pair this entry reports is on that rung and is correct. FREE, READ and WRITE share the decode, which is why one omitted line carries both bug classes.
  - `rust` — THE SAFETY LINE, in all four Rust rungs. `gen[h as usize] != g` in safe_naive.rs, `gen[h] != g` in safe_tuned.rs, and `arr_get_unchecked(&gen, h as usize) != g` in unsafe.rs and verus.rs -- the operand is the same, the accessor is what each rung forces. ⚠ **Not one of the four gets any part of it from the language.** safe_tuned.rs's `Option<(u8, u32)>` writes the `h == NIL` half for you, which is p29's `is_some()`; the generation half is written out by hand in every rung, because nothing in the type system knows that a live range of bytes has changed occupant. See the why key.
- **required** — *per language:*
  - `c` — THE HANDLE IS ISSUED BY ALLOC AND NAMED BY REGISTER, in both C rungs: `r = (size_t)(a % NREG);`. The file names the register; ALLOC writes `regs[r]` and `regg[r]`. This is what makes the generation unforgeable -- see the why key, which measures the alternative.
  - `rust` — the same, in all four Rust rungs: `let r: usize = (a % NREG as u8) as usize;`.
- **required** — *per language:*
  - `c` — THE GENERATION IS BUMPED BY EVERY FREE, IN BOTH C RUNGS: `gen[h] = gen[h] + 1;`. R1's bug is NOT that it skips this -- it does not -- it is that its handle-consuming path never asks. Splitting the bump from the check is what makes forgetting possible at all.
  - `rust` — the same bump in all four Rust rungs, spelled `wrapping_add(1)` because `-C debug-assertions=on` would otherwise panic and C wraps by definition.
- **required** — *per language:*
  - `c` — THE FREE LIST IS INTRUSIVE AND LIFO, in both C rungs: `nx[h] = freehead;` followed by `freehead = h;`. It is the intrusive spelling that makes the double push a SELF-LOOP rather than a duplicate entry, and the self-loop is what produces the aliasing.
  - `rust` — the same push in all four Rust rungs: `nx[h as usize] = freehead;` in safe_naive.rs, `nx[h] = freehead;` in safe_tuned.rs, `arr_set_unchecked(&mut nx, h as usize, freehead)` in unsafe.rs and verus.rs.
- **required** — THE HANDLE REGISTER IS NOT CLEARED ON THE FREE, in all seven rungs. Nothing writes `regs[]`/`regg[]`/`reg[]` except ALLOC. See the why key for why clearing it would be a different bug class.
- **required** — *per language:*
  - `c` — the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the additive form's overflow never arises: `if (len - p < 2)` in both C rungs.
  - `rust` — the cursor guard, subtraction-first, in all four Rust rungs: `if len - p < 2 {`.
- **required** — *per language:*
  - `c` — the opcode is `c % 4`, so EVERY byte value is a legal opcode and no input is rejected for being malformed: `c % 4 == 0` in both C rungs.
  - `rust` — the opcode, in all four Rust rungs: `c % 4 == 0`.
- **required** — *per language:*
  - `c` — a rejected operation folds the SENTINEL rather than being skipped, so the fold's length is a function of the op count alone: `v = SENT;` in both C rungs.
  - `rust` — the sentinel fold, in all four Rust rungs: `SENT`.
- **required** — *per language:*
  - `c` — the fold is a serial Horner chain over `acc`, spelled with the literal multiplier, ONCE per operation: `acc = acc * 31 + v;` in both C rungs.
  - `rust` — the fold, in all four Rust rungs, spelled with the literal multiplier: `acc = acc.wrapping_mul(31).wrapping_add(v);`.
- **required** — *per language:*
  - `c` — the ALLOC count is folded last, so a rung that served a different number of allocations cannot produce the same checksum -- which is what puts the SELF-LOOPED free list in the answer: `return acc * 31 + (uint64_t)nalloc;` in both C rungs.
  - `rust` — the same, in all four Rust rungs: `acc.wrapping_mul(31).wrapping_add(nalloc as u64)`.
- **FORBIDDEN** — `malloc(`
- **FORBIDDEN** — `calloc(`
- **FORBIDDEN** — `realloc(`
- **FORBIDDEN** — `free(`
- **FORBIDDEN** — `std::alloc::`
- **FORBIDDEN** — `vstd::raw_ptr::`
- **FORBIDDEN** — `Box::new`
- **FORBIDDEN** — `Box::into_raw`
- **FORBIDDEN** — `Box::leak`
- **FORBIDDEN** — `ManuallyDrop`
- **FORBIDDEN** — `mem::forget`
- **FORBIDDEN** — `Rc<`
- **FORBIDDEN** — `RefCell`
- **FORBIDDEN** — `Vec::with_capacity`

> **Why**: POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens below must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ONE OMITTED SOURCE LINE CARRIES TWO BUG CLASSES SELECTED BY THE INPUT, AND THAT IS THE ROW. A FREE through a handle whose block has been recycled pushes that block onto the free list a SECOND time; `nx[h] = freehead` with `freehead == h` SELF-LOOPS the list, every later ALLOC returns the same slot, TWO LIVE HANDLES ALIAS ONE BLOCK and the rest of the list is lost. A READ through such a handle returns the NEW OCCUPANT's payload. Which harm the input gets is chosen by whether it frees again or reads again, and the omitted conjunct is the same one. THE ALIASING HARM HAS NO ANALOGUE IN p27 OR p29 AND THAT IS WHY THIS IS A ROW: p27 consults `live[h]` on its FREE path so it cannot double-free at all, has no free list, no recycling and no generation; p29 frees a record with a real `free()` and holds a stale ADDRESS. Neither can produce two live handles naming one block. NOTHING IS ALLOCATED AND NOTHING IS FREED, IN ANY RUNG, AND THAT IS THE POINT RATHER THAN A SIMPLIFICATION. The pool is a local array alive for the whole call, which is what a free-list allocator IS. Its consequence is that R1 executes NO undefined behaviour -- `regs[r]` is NIL or a real slot, `freehead` is NIL or a real slot, `nx[]` holds only values drawn from those two -- so ASan, UBSan and Miri are silent on every input this pattern ships, while the answer is WRONG on four of them and two handles alias on two of them. `model.py` DERIVES the spatial half of that silence rather than declaring it, AND THE CHECK IS ONE THAT CAN FIRE: its simulation carries a handle through the index path AS THE RUNGS CARRY IT -- a slot number or the NIL sentinel 255 -- and touches every index R1 forms from one, `gen[h]`, `nx[h]`, `pool[h*BLK]` and `pool[h*BLK+1]`, on ALLOC's `freehead` side as well as on FREE/READ/WRITE's; `model.py::detector_selftest()` deletes each of the two NIL guards in turn and the detector reports `fires`, and `selfcheck()` runs that arm on every gate invocation. CORRECTED AT TASK_147, AND THE OLD SENTENCE IS RETRACTED RATHER THAN QUIETLY REPLACED: until then this read `its simulation computes every index the buggy rung would compute and reports whether one escapes`, and TASK_145_REPORT 4b measured that false four ways -- the guard `0 <= s < SLOTS` was a TAUTOLOGY of the simulation's own representation with 0 firings in 20 000 fuzzed buggy windows, the one case that would have set it crashed the model with IndexError before the flag was read, `gen[h]`/`nx[h]`/`regs[r]` were not indexes that simulation computed at all, and M3-nil-test's failure mode was unrepresentable because an empty register was None rather than slot 255. THE CONCLUSION WAS AND IS TRUE; WHAT WAS FALSE WAS THAT model.py ESTABLISHED IT. The same 20 000-window sweep now fires 19 622 times with the `h == NIL` test deleted and 0 times with both guards present (NOTES.md 11). `controls/storage_arms.py` is the other cell of the experiment -- the same algorithm with per-block `malloc`/`free` storage -- and it is what makes this a controlled two-cell measurement of DETECTOR COVERAGE rather than an anecdote. That is why `malloc(`, `free(`, `std::alloc::` and `vstd::raw_ptr::` are forbidden here: a rung that allocated would be measuring a different pattern, and `Box::new`, `Rc<`, `RefCell` and `Vec::with_capacity` are forbidden for p29's reason as well -- they would move the liveness decision into a library and delete the comparison. THE FILE NAMES A HANDLE REGISTER, NEVER A SLOT AND NEVER A GENERATION, AND THAT IS LOAD-BEARING RATHER THAN PRESENTATIONAL. It is p29's corrected sentence -- a file cannot name a pointer, but it CAN name an operation that saves one -- and here it is what makes the generation UNFORGEABLE. Measured (NOTES.md 1b): with a file-supplied `(slot, generation)` byte the attacker can always spell the CURRENT incarnation of a block that is already on the free list, so the HARDENED kernel self-loops its own free list on an input of five operations -- FIVE, corrected at TASK_147 from `four`, which contradicted NOTES.md 1b, README.md, c/kernel.h and the control's own `op0..op4` transcript (TASK_145_REPORT 8). That variant is not a harder version of this row, it is a broken R1h, and admission question 1 asks the C kernel to be correct. `regs[r]` IS DELIBERATELY NOT CLEARED ON THE FREE, and it is p27's and p29's reason: clearing it would turn every stale use into the `h == NIL` case, which folds SENT in BOTH rungs -- a defined operation and a different bug class. Splitting the release from the invalidation is what makes forgetting possible at all. THE GENERATION IS `u32` AND IT WRAPS. `gen[h]` is bumped once per FREE of slot `h` and a window holds `(len - 4) / 2` operations, so a wrap needs 2^32 frees of one slot inside one window; the largest window this pattern ships is 244 bytes. Both C rungs, all four Rust rungs, `model.py` and the Verus spec all wrap, so they agree by construction and not by the size of the inputs. WHAT IS DELIBERATELY NOT PINNED is how the handle register is SPELLED in the safe rungs -- a NIL-sentinel pair of parallel arrays in R2, `Option<(u8, u32)>` in R3 -- exactly as p14 leaves its fold loop unpinned and p29 leaves its liveness half. Those are the R3-side levers, they cost zero TCB, and THIS PATTERN PUBLISHES NO RUNG-TO-RUNG COST AT ALL (NOTES.md 8), so no spread is being reported as a number and the absence is stated rather than left to read as a zero. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p32-free-list-pool.json`, contract `4611eff514dc`.

`66` backticked spelling(s) over `6` rung(s) → **200** (spelling, rung) pair(s), **69** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 28 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 8 spelling(s) pin nothing**, 21 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - pins nothing — `is_some()` (required[0], rust, 0 of 4 rungs)
  - pins nothing — `-C debug-assertions=on` (required[2], rust, 0 of 4 rungs)
  - pins nothing — `regs[]` (required[4], c, 0 of 2 rungs)
  - pins nothing — `regg[]` (required[4], c, 0 of 2 rungs)
  - pins nothing — `reg[]` (required[4], c, 0 of 2 rungs)
  - pins nothing — `regs[]` (required[4], rust, 0 of 4 rungs)
  - pins nothing — `regg[]` (required[4], rust, 0 of 4 rungs)
  - pins nothing — `reg[]` (required[4], rust, 0 of 4 rungs)
  - absent — `} else if (gen[h] != g) {` (required[0], c, **c/kernel.c**)
  - absent — `gen[h as usize] != g` (required[0], rust, **safe_tuned.rs**)
  - absent — `gen[h as usize] != g` (required[0], rust, **unsafe.rs**)
  - absent — `gen[h as usize] != g` (required[0], rust, **verus.rs**)
  - absent — `gen[h] != g` (required[0], rust, **safe_naive.rs**)
  - absent — `gen[h] != g` (required[0], rust, **unsafe.rs**)
  - absent — `gen[h] != g` (required[0], rust, **verus.rs**)
  - absent — `arr_get_unchecked(&gen, h as usize) != g` (required[0], rust, **safe_naive.rs**)
  - absent — `arr_get_unchecked(&gen, h as usize) != g` (required[0], rust, **safe_tuned.rs**)
  - absent — `Option<(u8, u32)>` (required[0], rust, **safe_naive.rs**)
  - absent — `Option<(u8, u32)>` (required[0], rust, **unsafe.rs**)
  - absent — `Option<(u8, u32)>` (required[0], rust, **verus.rs**)
  - absent — `h == NIL` (required[0], rust, **safe_tuned.rs**)
  - absent — `nx[h as usize] = freehead;` (required[3], rust, **safe_tuned.rs**)
  - absent — `nx[h as usize] = freehead;` (required[3], rust, **unsafe.rs**)
  - absent — `nx[h as usize] = freehead;` (required[3], rust, **verus.rs**)
  - absent — `nx[h] = freehead;` (required[3], rust, **safe_naive.rs**)
  - absent — `nx[h] = freehead;` (required[3], rust, **unsafe.rs**)
  - absent — `nx[h] = freehead;` (required[3], rust, **verus.rs**)
  - absent — `arr_set_unchecked(&mut nx, h as usize, freehead)` (required[3], rust, **safe_naive.rs**)
  - absent — `arr_set_unchecked(&mut nx, h as usize, freehead)` (required[3], rust, **safe_tuned.rs**)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## What the gate said out loud (reporting only)

From `results/gate/p32-free-list-pool.json` — the `loud` and `controls_json` keys, at contract `4611eff514dc`. **These did not fail the gate and are not defects**; they are the conditions `check.py` refuses to be silent about. Each one is a caveat on a number below or on the declaration above. The run's **verdict** is deliberately not printed here: it is an output of the same gate run that checks this table is current (stage `9c`), and rendering it made the table an input to its own checker — see `read_gate_loud`. Read the verdict from `results/gate/p32-free-list-pool.json`.

- **`tcb-unsafe`** — verus.rs:343 `arr_set_unchecked`'s `requires` constrains nothing about ['x'], which its trusted body uses. spec.md justifies it: `x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `T` is a legal thing to store in a `T` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` reads `i < N`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second, p06 the third, p14 the fourth, p27 the fifth, p29 the sixth and p32 the seventh.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 124 | 118 | 0 | 484 | 141,848,340 | 59,875,957 | 3,000,056 | 300,056 | `3184a529` | `3184a529` | yes | xmm |
| c-clang | 100 | 97 | 1 | 393 | 143,849,933 | 63,708,087 | 2,800,059 | 280,059 | `c36b5c0b` | `ec0e17ff` | yes | xmm |
| safe_naive | 154 | 152 | 9 | 647 | 184,550,523 | 82,445,887 | 2,800,275 | 280,275 | `5fd0d9d2` | `f2d6530f` | yes | xmm |
| safe_tuned | 165 | 162 | 8 | 744 | 192,698,372 | 85,276,910 | 2,800,275 | 280,275 | `8ce31898` | `63beaf53` | yes | xmm |
| unsafe | 106 | 103 | 15 | 417 | 153,924,236 | 68,745,766 | 2,800,275 | 280,275 | `cf0875f0` | `2918e89d` | yes | xmm |
| verus | 106 | 103 | 15 | 417 | 153,924,236 | 68,745,766 | 2,600,274 | 260,274 | `cf0875f0` | `2918e89d` | yes | xmm |
| c-gcc-h | 132 | 127 | 0 | 516 | 148,747,688 | 62,745,528 | 3,000,056 | 300,056 | `b4242274` | `b4242274` | yes | xmm |
| c-clang-h | 109 | 106 | 1 | 427 | 149,524,236 | 66,385,766 | 2,800,059 | 280,059 | `f3bdda99` | `1ddd6096` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 243 | 242 | 0 | 1,208 | 368,116,641 | - | 7,200,066 | - | `4ce710b5` | `4ce710b5` | yes | - |
| c-clang | 215 | 215 | 1 | 1,118 | 365,805,301 | - | 4,200,056 | - | `a1ee24a1` | `bcbc27e1` | yes | - |
| safe_naive | 426 | 426 | 3 | 2,285 | 457,421,537 | - | 5,000,077 | - | `8d46cc8c` | `9459c017` | yes | - |
| safe_tuned | 429 | 429 | 3 | 2,269 | 486,177,133 | - | 5,000,077 | - | `fc1bd7ff` | `1f36f636` | yes | - |
| unsafe | 341 | 341 | 9 | 1,703 | 477,742,314 | - | 5,000,077 | - | `e21b5838` | `ae81efbd` | yes | - |
| verus | 341 | 341 | 9 | 1,703 | 477,742,314 | - | 5,000,056 | - | `1d56fcd8` | `a3cb65da` | yes | - |
| c-gcc-h | 250 | 249 | 0 | 1,245 | 373,490,861 | - | 7,200,066 | - | `85221aa4` | `85221aa4` | yes | - |
| c-clang-h | 222 | 222 | 2 | 1,155 | 371,179,521 | - | 4,200,056 | - | `dd665a77` | `78c98615` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 341 | 339 | 1 | 1,400 | - | - | 148,848,451 | 62,684,199 | `b287040c` | `ffddc324` | yes | xmm |
| c-clang | 323 | 318 | 0 | 1,316 | - | - | 151,650,088 | 66,596,373 | `b18fb807` | `b18fb807` | yes | xmm |
| safe_naive | 790 | 781 | 1 | 3,631 | - | - | 192,074,153 | 85,452,991 | `2ca37f2d` | `8e8d8adc` | yes | xmm |
| safe_tuned | 801 | 792 | 1 | 3,791 | - | - | 202,525,912 | 89,112,378 | `8bc4870f` | `d864332f` | yes | xmm |
| unsafe | 732 | 723 | 1 | 3,295 | - | - | 162,124,490 | 71,674,151 | `2db00342` | `b1e9032b` | yes | xmm |
| verus | 740 | 731 | 1 | 3,231 | - | - | 162,124,487 | 71,674,148 | `11fd127e` | `795ef4ae` | yes | xmm |
| c-gcc-h | 349 | 347 | 1 | 1,487 | - | - | 149,671,199 | 62,984,382 | `d0bce41e` | `637d77be` | yes | xmm |
| c-clang-h | 332 | 328 | 0 | 1,369 | - | - | 157,124,394 | 69,254,055 | `096e908b` | `096e908b` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 368,116,641 | - | 7,200,066 | - | `cf1ad787` | `cf1ad787` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 359,081,956 | - | 4,200,055 | - | `f2dcc007` | `f2dcc007` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 457,421,537 | - | 5,000,077 | - | `b39dcc74` | `8289d1fe` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 486,177,133 | - | 5,000,077 | - | `c5b3b75e` | `83931fb5` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 477,742,314 | - | 5,000,077 | - | `b747cd67` | `f308ad39` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 477,742,314 | - | 5,000,056 | - | `fc8a90fb` | `cc35e4c8` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 373,490,861 | - | 7,200,066 | - | `b3f5b58b` | `b3f5b58b` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 364,456,176 | - | 4,200,055 | - | `90648887` | `90648887` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 341/341 vs 341/341 | 9 B vs 9 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 106/103 vs 106/103 | 15 B vs 15 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 14.27 | 15.26 | 7.0% | 14.15 | 14.65 | 3.5% |
| c-gcc | whole | 14.80 | 15.43 | 4.2% | 15.31 | 15.85 | 3.5% |
| c-clang | isolated | 15.37 | 15.92 | 3.6% | 13.99 | 14.39 | 2.9% |
| c-clang | whole | 15.78 | 16.37 | 3.8% | 14.18 | 14.71 | 3.8% |
| safe_naive | isolated | 15.47 | 16.25 | 5.0% | 15.59 | 16.09 | 3.2% |
| safe_naive | whole | 16.60 | 17.41 | 4.9% | 16.39 | 17.01 | 3.8% |
| safe_tuned | isolated | 15.82 | 16.50 | 4.3% | 16.39 | 16.89 | 3.0% |
| safe_tuned | whole | 16.58 | 17.29 | 4.3% | 17.38 | 17.83 | 2.6% |
| unsafe | isolated | 15.19 | 15.89 | 4.6% | 14.27 | 14.73 | 3.2% |
| unsafe | whole | 15.48 | 16.07 | 3.8% | 14.79 | 15.16 | 2.5% |
| verus | isolated | 15.24 | 15.83 | 3.8% | 14.48 | 14.70 | 1.6% |
| verus | whole | 15.48 | 16.15 | 4.3% | 14.87 | 15.32 | 3.1% |
| c-gcc-h | isolated | 13.32 | 13.80 | 3.6% | 13.85 | 14.85 | 7.2% |
| c-gcc-h | whole | 14.69 | 15.22 | 3.6% | 15.62 | 16.15 | 3.4% |
| c-clang-h | isolated | 15.59 | 16.20 | 3.9% | 14.02 | 14.49 | 3.3% |
| c-clang-h | whole | 15.42 | 16.70 | 8.3% | 14.13 | 14.57 | 3.1% |

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
