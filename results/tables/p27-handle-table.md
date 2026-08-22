# p27-handle-table — results

Generated 2026-08-21T20:10:31Z from `results/p27-handle-table.json` (git `098237f4d531`, working tree dirty).

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
| adversarial-many.bin | 200,000 | 204 | 204 | False | n_iters=200000 stride=196 n_blob=196 nwin=1 calls=200000 work/call=196B san=fires truncated=False expected=6582356636790626304 |
| adversarial-noreuse.bin | 200,000 | 36 | 36 | False | n_iters=200000 stride=28 n_blob=28 nwin=1 calls=200000 work/call=28B san=fires truncated=False expected=3390747988282288128 |
| adversarial-stride3.bin | 200,000 | 38 | 38 | False | n_iters=200000 stride=3 n_blob=30 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| adversarial-uaf.bin | 200,000 | 72 | 72 | False | n_iters=200000 stride=64 n_blob=64 nwin=1 calls=200000 work/call=64B san=fires truncated=False expected=4295919549966416896 |
| degenerate.bin | 200,000 | 102 | 102 | False | n_iters=200000 stride=94 n_blob=94 nwin=1 calls=200000 work/call=94B san=clean truncated=False expected=8089868669041868800 |
| large.bin | 20,000 | 15,624 | 15,624 | False | n_iters=20000 stride=244 n_blob=15616 nwin=64 calls=20000 work/call=244B san=clean truncated=False expected=15348810832415442499 |
| small.bin | 200,000 | 424 | 424 | False | n_iters=200000 stride=52 n_blob=416 nwin=8 calls=200000 work/call=52B san=clean truncated=False expected=1331635740038472661 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE SAFETY LINE, and the only thing c/kernel.c omits: the liveness conjunct on the READ path, `if (h < ntab && live[h] == 1) {` in c/kernel_hardened.c. c/kernel.c writes `if (h < ntab) {` there and is otherwise character-identical, so the scoped-absent audit pair this entry reports is on that rung and is correct.
  - `rust` — THE SAFETY LINE: the liveness test on the READ path, `if h < ntab && arr_get_unchecked(&live, h) == 1u8 {` in unsafe.rs and verus.rs. In the safe rungs it is the `Option` discriminant instead -- `tab[h].is_some()` in safe_naive.rs and the `Some(rec)` arm in safe_tuned.rs -- because safe Rust has no separate liveness array to test: `Option<Box<u8>>` is niche-optimised to one pointer word and IS the hardened-C representation. That is the pattern's whole subject; see the why key.
- **required** — *per language:*
  - `c` — THE LINE THE C RUNG MUST NOT FORGET, present in BOTH C rungs: `live[h] = 0;` immediately after the `free`. R1's bug is NOT that it skips this -- it does not -- it is that its READ path never asks. Splitting the free from the invalidation is what makes forgetting possible at all.
  - `rust` — the same line in the unsafe rungs, `arr_set_unchecked(&mut live, h, 0u8);` in unsafe.rs and verus.rs -- and at R5 the proof FORCES it: without it the loop invariant cannot be re-established, because `rec_free` has consumed slot h's permission while the liveness array would still claim it exists. In the safe rungs there is no such line, because `tab[h] = None` and `tab[h].take()` free the record and invalidate the handle in ONE operation.
- **required** — *per language:*
  - `c` — THE REAL `free`, in both C rungs: `free(tab[h]);`. Not a freelist push into a slab -- see the why key.
  - `rust` — THE REAL free, in all four Rust rungs: `std::alloc::dealloc(p, layout);` inside rec_free in unsafe.rs and verus.rs (`vstd::raw_ptr::deallocate`'s six preconditions and its body, respelled but not weakened -- see the TCB section -- whose verified twin in verus.rs is vstd's own `deallocate`), and the drop of `Option<Box<u8>>` in safe_naive.rs and safe_tuned.rs.
- **required** — *per language:*
  - `c` — ONE ALLOCATION PER RECORD, in both C rungs: `malloc(RECSZ)`.
  - `rust` — ONE ALLOCATION PER RECORD, in all four Rust rungs: `std::alloc::alloc(layout)` inside rec_alloc in unsafe.rs and verus.rs, and `Box::new(a)` in safe_naive.rs and safe_tuned.rs. Rust's default global allocator calls `malloc` for `align <= 8`, so all seven rungs hit the same glibc, in the same size class, once per record.
- **required** — *per language:*
  - `c` — the handle table's extent is a COMPILE-TIME CONSTANT and the capacity guard is in every rung including R1: `if (ntab < TABCAP) {` in both C rungs.
  - `rust` — the capacity guard, in all four Rust rungs: `if ntab < TABCAP {`.
- **required** — *per language:*
  - `c` — the SLOT BOUND is in every rung including R1, so the bug is TEMPORAL and not spatial: `h < ntab` in both C rungs.
  - `rust` — the slot bound, in all four Rust rungs: `h < ntab`.
- **required** — *per language:*
  - `c` — the EPILOGUE frees every record still alive, so neither C rung leaks and the allocator state at the end of a call is the state at its start: `for (j = 0; j < ntab; j++) {` in both C rungs.
  - `rust` — the epilogue, in unsafe.rs and verus.rs: `while j < ntab {`. **safe_naive.rs and safe_tuned.rs deliberately do NOT have one** -- dropping the table is the epilogue, written by the language -- and that asymmetry is a measured result rather than an oversight (../NOTES.md 3).
- **required** — *per language:*
  - `c` — the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the additive form's overflow never arises: `if (len - p < 2)` in both C rungs.
  - `rust` — the cursor guard, subtraction-first, in all four Rust rungs: `if len - p < 2 {`.
- **required** — *per language:*
  - `c` — the opcode is `c % 4`, so EVERY byte value is a legal opcode and no input is rejected for being malformed: `c % 4 == 0` in both C rungs.
  - `rust` — the opcode, in all four Rust rungs: `c % 4 == 0`.
- **required** — *per language:*
  - `c` — a rejected operation folds the SENTINEL rather than being skipped, so the fold's length is a function of the op count alone: `acc = acc * 31 + SENT;` in both C rungs.
  - `rust` — the sentinel fold, in all four Rust rungs: `.wrapping_add(SENT)`.
- **required** — *per language:*
  - `c` — the fold is a serial Horner chain over `acc`, spelled with the literal multiplier: `acc = acc * 31 +` in both C rungs.
  - `rust` — the fold, in all four Rust rungs, spelled with the literal multiplier: `.wrapping_mul(31)`.
- **required** — the slot count is folded last so that a rung which opened a different number of records cannot produce the same checksum: `ntab` appears in the return expression of all seven rungs.
- **FORBIDDEN** — `realloc(`
- **FORBIDDEN** — `calloc(`
- **FORBIDDEN** — `Vec::with_capacity`
- **FORBIDDEN** — `Rc<`
- **FORBIDDEN** — `RefCell`
- **FORBIDDEN** — `ManuallyDrop`
- **FORBIDDEN** — `mem::forget`
- **FORBIDDEN** — `Box::leak`
- **FORBIDDEN** — `Box::into_raw`

> **Why**: POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. Here that clause is load-bearing and it IS the pattern. THE FREE AND THE INVALIDATION ARE ONE OPERATION IN SAFE RUST AND TWO IN C: `tab[h] = None` frees the record and invalidates the handle together, and `free(tab[h]); live[h] = 0;` is the same thing written twice, which is what makes forgetting the second half possible. So the safe rungs have no `live[]` array and cannot be asked to spell one, and the unsafe rungs have no `Option` and cannot be asked to spell that. THE HANDLE IS AN INTEGER AND THAT IS WHY NULLING IS NOT A DEFENCE: the op stream comes out of a file and a file cannot name a pointer, so the READ has an index and must consult something to learn whether the record is there. Nulling `tab[h]` on close would make a stale read a NULL DEREFERENCE -- a crash, a different bug class -- rather than a use-after-free, and it would leave the epilogue unable to tell a closed slot from a live one without the very bit it is trying to avoid carrying. `live[]` is a generation counter with slot reuse removed, and every real handle table carries one. THE FREE MUST BE A REAL `free`: if the slab were one allocation and 'close' were a freelist push, the stale read would be IN BOUNDS OF A LIVE ALLOCATION -- Miri would not flag it, `PointsTo` would license it, and the bug would be LOGICAL, which is p17's class and the tree already has one (TASK_055 §2.8 caveat 1). That is what `Box::into_raw`, `ManuallyDrop`, `mem::forget` and `Box::leak` are forbidden for: each is a route to holding a record past its free without the allocator knowing, i.e. to turning the temporal bug back into a logical one. `realloc`/`calloc`/`Vec::with_capacity` are forbidden because they change the allocator traffic and the pattern's fairness argument is that every rung makes exactly one allocation and one free per record; `Rc`/`RefCell` because they would move the liveness decision to run time inside the library and delete the comparison. WHAT IS DELIBERATELY NOT PINNED is how the liveness test is SPELLED -- `is_some()` in R2, a `match` arm in R3, `take().is_some()` in R3's CLOSE -- exactly as p14 leaves its fold loop unpinned: those are the R3-side levers, they cost zero TCB, and the pattern reports the cheapest one FOUND on a named input rather than a minimum (../NOTES.md 8). NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p27-handle-table.json`, contract `01e2137f9a1b`.

`60` backticked spelling(s) over `6` rung(s) → **188** (spelling, rung) pair(s), **86** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 18 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 3 spelling(s) pin nothing**, 36 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - pins nothing — `vstd::raw_ptr::deallocate` (required[2], rust, 0 of 4 rungs)
  - pins nothing — `malloc` (required[3], rust, 0 of 4 rungs)
  - pins nothing — `align <= 8` (required[3], rust, 0 of 4 rungs)
  - absent — `if (h < ntab) {` (required[0], c, **c/kernel_hardened.c**)
  - absent — `if h < ntab && arr_get_unchecked(&live, h) == 1u8 {` (required[0], rust, **safe_naive.rs**)
  - absent — `if h < ntab && arr_get_unchecked(&live, h) == 1u8 {` (required[0], rust, **safe_tuned.rs**)
  - absent — `Option` (required[0], rust, **unsafe.rs**)
  - absent — `Option` (required[0], rust, **verus.rs**)
  - absent — `tab[h].is_some()` (required[0], rust, **safe_tuned.rs**)
  - absent — `tab[h].is_some()` (required[0], rust, **unsafe.rs**)
  - absent — `tab[h].is_some()` (required[0], rust, **verus.rs**)
  - absent — `Some(rec)` (required[0], rust, **safe_naive.rs**)
  - absent — `Some(rec)` (required[0], rust, **unsafe.rs**)
  - absent — `Some(rec)` (required[0], rust, **verus.rs**)
  - absent — `Option<Box<u8>>` (required[0], rust, **unsafe.rs**)
  - absent — `Option<Box<u8>>` (required[0], rust, **verus.rs**)
  - absent — `arr_set_unchecked(&mut live, h, 0u8);` (required[1], rust, **safe_naive.rs**)
  - absent — `arr_set_unchecked(&mut live, h, 0u8);` (required[1], rust, **safe_tuned.rs**)
  - absent — `rec_free` (required[1], rust, **safe_naive.rs**)
  - absent — `rec_free` (required[1], rust, **safe_tuned.rs**)
  - absent — `tab[h] = None` (required[1], rust, **safe_tuned.rs**)
  - absent — `tab[h] = None` (required[1], rust, **unsafe.rs**)
  - absent — `tab[h] = None` (required[1], rust, **verus.rs**)
  - absent — `tab[h].take()` (required[1], rust, **safe_naive.rs**)
  - absent — `tab[h].take()` (required[1], rust, **unsafe.rs**)
  - absent — `tab[h].take()` (required[1], rust, **verus.rs**)
  - absent — `std::alloc::dealloc(p, layout);` (required[2], rust, **safe_naive.rs**)
  - absent — `std::alloc::dealloc(p, layout);` (required[2], rust, **safe_tuned.rs**)
  - absent — `deallocate` (required[2], rust, **safe_naive.rs**)
  - absent — `deallocate` (required[2], rust, **safe_tuned.rs**)
  - absent — `deallocate` (required[2], rust, **unsafe.rs**)
  - absent — `Option<Box<u8>>` (required[2], rust, **unsafe.rs**)
  - absent — `Option<Box<u8>>` (required[2], rust, **verus.rs**)
  - absent — `std::alloc::alloc(layout)` (required[3], rust, **safe_naive.rs**)
  - absent — `std::alloc::alloc(layout)` (required[3], rust, **safe_tuned.rs**)
  - absent — `Box::new(a)` (required[3], rust, **unsafe.rs**)
  - absent — `Box::new(a)` (required[3], rust, **verus.rs**)
  - absent — `while j < ntab {` (required[6], rust, **safe_naive.rs**)
  - absent — `while j < ntab {` (required[6], rust, **safe_tuned.rs**)
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
| c-gcc | 154 | 146 | 0 | 638 | 168,913,692 | 68,801,730 | 3,000,056 | 300,056 | `a3b91914` | `a3b91914` | yes | xmm |
| c-clang | 147 | 141 | 1 | 599 | 173,918,253 | 72,836,379 | 2,800,055 | 280,055 | `e828ef00` | `84240989` | yes | xmm |
| safe_naive | 210 | 206 | 15 | 897 | 208,228,514 | 91,247,591 | 2,800,275 | 280,275 | `079519b5` | `b6620e25` | yes | xmm |
| safe_tuned | 213 | 209 | 15 | 913 | 206,325,767 | 90,607,591 | 2,800,275 | 280,275 | `05dbebfc` | `edff3df5` | yes | xmm |
| unsafe | 154 | 150 | 7 | 633 | 184,330,754 | 77,371,189 | 2,800,275 | 280,275 | `38ae720c` | `7f7d4ec7` | yes | xmm |
| verus | 154 | 150 | 7 | 633 | 184,330,754 | 77,371,189 | 2,800,270 | 280,270 | `38ae720c` | `7f7d4ec7` | yes | xmm |
| c-gcc-h | 155 | 149 | 0 | 646 | 172,899,171 | 70,617,758 | 3,000,056 | 300,056 | `3ec8a3fc` | `3ec8a3fc` | yes | xmm |
| c-clang-h | 146 | 142 | 1 | 599 | 174,914,776 | 72,905,833 | 2,800,055 | 280,055 | `f785f3fc` | `6777646c` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 221 | 220 | 0 | 1,095 | 300,823,006 | - | 7,200,066 | - | `6cf0fa4a` | `6cf0fa4a` | yes | - |
| c-clang | 174 | 174 | 1 | 922 | 304,554,831 | - | 4,200,052 | - | `4039a8dd` | `263be7b7` | yes | - |
| safe_naive | 434 | 434 | 10 | 2,486 | 480,165,220 | - | 5,000,077 | - | `0a101c20` | `fad7694f` | yes | - |
| safe_tuned | 392 | 392 | 11 | 2,245 | 452,364,506 | - | 5,000,077 | - | `8498eb21` | `1cfb3c1c` | yes | - |
| unsafe | 271 | 271 | 13 | 1,427 | 459,039,230 | - | 5,000,077 | - | `14da8205` | `cddead1c` | yes | - |
| verus | 271 | 271 | 13 | 1,427 | 459,039,230 | - | 5,000,056 | - | `0451fa67` | `77f1159e` | yes | - |
| c-gcc-h | 227 | 226 | 0 | 1,116 | 309,962,380 | - | 7,200,066 | - | `1eeae974` | `1eeae974` | yes | - |
| c-clang-h | 178 | 178 | 1 | 942 | 310,647,747 | - | 4,200,052 | - | `386c75f5` | `4ad20858` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 379 | 375 | 1 | 1,578 | - | - | 160,994,054 | 64,476,670 | `3b2cd545` | `213679d9` | yes | - |
| c-clang | 385 | 376 | 0 | 1,627 | - | - | 178,061,497 | 75,087,507 | `6542cee2` | `6542cee2` | yes | xmm |
| safe_naive | 843 | 833 | 1 | 4,015 | - | - | 215,721,552 | 95,089,770 | `287489e7` | `0dfb2d56` | yes | xmm |
| safe_tuned | 845 | 835 | 1 | 3,999 | - | - | 213,172,995 | 94,018,823 | `791cf7ee` | `72ca70d8` | yes | xmm |
| unsafe | 795 | 784 | 1 | 3,711 | - | - | 196,458,875 | 83,325,483 | `045a236f` | `f56b41aa` | yes | xmm |
| verus | 811 | 797 | 1 | 3,711 | - | - | 195,503,551 | 83,156,429 | `e299d68a` | `4b2ba469` | yes | xmm |
| c-gcc-h | 381 | 377 | 1 | 1,595 | - | - | 166,512,673 | 66,909,590 | `232ea324` | `1f142ff9` | yes | - |
| c-clang-h | 381 | 373 | 0 | 1,633 | - | - | 181,160,767 | 75,816,961 | `58d2925d` | `58d2925d` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 300,823,006 | - | 7,200,066 | - | `d1c57d4e` | `d1c57d4e` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 304,754,831 | - | 4,200,051 | - | `73d6d3a7` | `73d6d3a7` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 480,165,220 | - | 5,000,077 | - | `4d648185` | `2e75a48b` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 452,364,506 | - | 5,000,077 | - | `647bd6e5` | `fafdf07d` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 459,039,230 | - | 5,000,077 | - | `86245bd5` | `cf65c2b4` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 459,039,230 | - | 5,000,056 | - | `a331919f` | `c27df4da` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 309,962,380 | - | 7,200,066 | - | `29c7be96` | `29c7be96` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 310,847,747 | - | 4,200,051 | - | `5078de89` | `5078de89` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 271/271 vs 271/271 | 13 B vs 13 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 154/150 vs 154/150 | 7 B vs 7 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 26.85 | 27.09 | 0.9% | 35.49 | 36.03 | 1.5% |
| c-gcc | whole | 27.82 | 28.16 | 1.2% | 36.20 | 36.54 | 0.9% |
| c-clang | isolated | 27.74 | 28.04 | 1.1% | 33.87 | 34.21 | 1.0% |
| c-clang | whole | 29.71 | 29.99 | 1.0% | 33.96 | 34.45 | 1.5% |
| safe_naive | isolated | 29.63 | 29.92 | 1.0% | 39.08 | 40.53 | 3.7% |
| safe_naive | whole | 31.58 | 31.82 | 0.8% | 40.25 | 40.67 | 1.1% |
| safe_tuned | isolated | 29.69 | 30.02 | 1.1% | 39.81 | 40.23 | 1.0% |
| safe_tuned | whole | 31.20 | 31.63 | 1.4% | 39.86 | 40.34 | 1.2% |
| unsafe | isolated | 30.14 | 30.39 | 0.8% | 37.37 | 37.78 | 1.1% |
| unsafe | whole | 31.31 | 31.59 | 0.9% | 38.22 | 38.66 | 1.2% |
| verus | isolated | 29.52 | 29.93 | 1.4% | 37.42 | 37.90 | 1.3% |
| verus | whole | 31.43 | 31.72 | 0.9% | 38.34 | 38.78 | 1.2% |
| c-gcc-h | isolated | 27.55 | 27.73 | 0.7% | 35.95 | 36.35 | 1.1% |
| c-gcc-h | whole | 28.46 | 28.78 | 1.1% | 36.80 | 37.29 | 1.3% |
| c-clang-h | isolated | 27.61 | 27.90 | 1.1% | 34.10 | 34.56 | 1.3% |
| c-clang-h | whole | 28.27 | 28.61 | 1.2% | 34.38 | 34.83 | 1.3% |

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
