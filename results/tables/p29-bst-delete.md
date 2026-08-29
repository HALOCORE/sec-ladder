# p29-bst-delete — results

Generated 2026-08-29T17:28:13Z from `results/p29-bst-delete.json` (git `0f606bb03bdb`, working tree dirty).

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
| adversarial-many.bin | 200,000 | 76 | 76 | False | n_iters=200000 stride=68 n_blob=68 nwin=1 calls=200000 work/call=68B san=fires truncated=False expected=12727551634606393344 |
| adversarial-recycle.bin | 200,000 | 42 | 42 | False | n_iters=200000 stride=34 n_blob=34 nwin=1 calls=200000 work/call=34B san=clean truncated=False expected=6826524771972934656 |
| adversarial-stride3.bin | 200,000 | 38 | 38 | False | n_iters=200000 stride=3 n_blob=30 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| adversarial-succ.bin | 200,000 | 38 | 38 | False | n_iters=200000 stride=30 n_blob=30 nwin=1 calls=200000 work/call=30B san=fires truncated=False expected=3300925633855656960 |
| adversarial-uaf.bin | 200,000 | 50 | 50 | False | n_iters=200000 stride=42 n_blob=42 nwin=1 calls=200000 work/call=42B san=fires truncated=False expected=17864705736200262656 |
| degenerate.bin | 200,000 | 150 | 150 | False | n_iters=200000 stride=142 n_blob=142 nwin=1 calls=200000 work/call=142B san=clean truncated=False expected=13598031668219826176 |
| large.bin | 20,000 | 15,624 | 15,624 | False | n_iters=20000 stride=244 n_blob=15616 nwin=64 calls=20000 work/call=244B san=clean truncated=False expected=13741993300287794333 |
| small.bin | 200,000 | 424 | 424 | False | n_iters=200000 stride=52 n_blob=416 nwin=8 calls=200000 work/call=52B san=clean truncated=False expected=6652604492202774167 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE SAFETY LINE, and the only thing c/kernel.c omits: TWO conjuncts on the USE path, `if (g_saved != NULL && live[g_slot] == 1 && tab[g_slot][0] == g_key) {` in c/kernel_hardened.c. c/kernel.c writes `if (g_saved != NULL) {` there and is otherwise character-identical, so the scoped-absent audit pair this entry reports is on that rung and is correct.
  - `rust` — THE SAFETY LINE. In the unsafe rungs it is `if g_has && arr_get_unchecked(&live, g_slot as usize) == 1u8 {` followed by `if rr.key == g_key {`, and the NESTING is forced rather than chosen: at R5 the record read needs `perms.tracked_borrow(g_slot)`, whose precondition only the liveness test discharges. In the safe rungs the first conjunct is the `Option` discriminant -- `tab[g_slot].is_some()` in safe_naive.rs and the `Some(rec)` arm in safe_tuned.rs -- because safe Rust has no separate liveness array to test, **and the second conjunct has to be written out in full there too**: `rec.key == g_key`. That asymmetry is the pattern's whole subject; see the why key.
- **required** — *per language:*
  - `c` — THE LINE THE C RUNG MUST NOT FORGET, present in BOTH C rungs: `live[cur] = 0;` immediately after the `free`. R1's bug is NOT that it skips this -- it does not -- it is that its USE path never asks. Splitting the free from the invalidation is what makes forgetting possible at all.
  - `rust` — the same line in the unsafe rungs, `arr_set_unchecked(&mut live, cur as usize, 0u8);` -- and at R5 the proof FORCES it: without it the loop invariant cannot be re-established, because `rec_free` has consumed slot `cur`'s permission while the liveness array would still claim it exists. In the safe rungs there is no such line, because `tab[cur] = None` frees the record and invalidates the slot in ONE operation.
- **required** — *per language:*
  - `c` — THE SUBSTITUTION, in both C rungs, and it is the SECOND bug class's whole mechanism: `tab[cur][0] = tab[s][0];` copies the in-order successor's key INTO the victim's record. The victim's ALLOCATION is not freed, so nothing temporal happens and no allocation-shaped detector fires.
  - `rust` — the substitution in the unsafe rungs, `Rec { key: srec.key, val: srec.val, l: co.l, r: co.r }` written back through `rec_write`; in the safe rungs the same two fields are assigned to the live `Box`'s contents. Nothing is dropped in any rung.
- **required** — *per language:*
  - `c` — THE REAL `free`, in both C rungs: `free(tab[cur]);`. Not a freelist push into a slab -- see the why key.
  - `rust` — THE REAL free, in all four Rust rungs: `std::alloc::dealloc(p, layout);` inside rec_free in unsafe.rs and verus.rs (`vstd::raw_ptr::deallocate`'s six preconditions and its body, respelled but not weakened, whose verified twin in verus.rs is vstd's own `deallocate`), and the drop of `Option<Box<Rec>>` in safe_naive.rs and safe_tuned.rs.
- **required** — *per language:*
  - `c` — ONE ALLOCATION PER RECORD, in both C rungs: `malloc(RECSZ)`.
  - `rust` — ONE ALLOCATION PER RECORD, in all four Rust rungs: `std::alloc::alloc(layout)` inside rec_alloc in unsafe.rs and verus.rs, and `Box::new(Rec {` in safe_naive.rs and safe_tuned.rs. Rust's default global allocator calls `malloc` for `align <= 8`, so all seven rungs hit the same glibc, in the same size class, once per record.
- **required** — *per language:*
  - `c` — THE WALK'S LIVENESS CONJUNCT AND ITS STEP BOUND, in every rung including R1: `while (cur != NIL && live[cur] == 1 && steps < TABCAP)`. Neither ever fires; both are what R5 needs. See the why key.
  - `rust` — the same walk guard in the unsafe rungs, `while cur != NIL && arr_get_unchecked(live, cur as usize) == 1u8 && steps < TABCAP`, and in the safe rungs the `Option` discriminant plays the liveness role -- `tab[cur].is_some()` in safe_naive.rs and a `match tab[cur].as_ref()` whose `None` arm breaks in safe_tuned.rs.
- **required** — *per language:*
  - `c` — the table's extent is a COMPILE-TIME CONSTANT and the capacity guard is in every rung including R1: `if (ntab < TABCAP)` in both C rungs.
  - `rust` — the capacity guard, in all four Rust rungs: `if ntab < TABCAP {`.
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
- **required** — the slot count is folded last so that a rung which allocated a different number of records cannot produce the same checksum: `ntab` appears in the return expression of all seven rungs.
- **FORBIDDEN** — `realloc(`
- **FORBIDDEN** — `calloc(`
- **FORBIDDEN** — `Vec::with_capacity`
- **FORBIDDEN** — `Rc<`
- **FORBIDDEN** — `RefCell`
- **FORBIDDEN** — `ManuallyDrop`
- **FORBIDDEN** — `mem::forget`
- **FORBIDDEN** — `Box::leak`
- **FORBIDDEN** — `Box::into_raw`

> **Why**: POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ONE OMITTED SOURCE LINE CARRIES TWO BUG CLASSES SELECTED BY THE INPUT, AND THAT IS THE ROW. A victim with 0 or 1 child is unlinked and FREED, so R1's cached read is a genuine use-after-FREE; a victim with 2 children has the in-order successor's key and val copied INTO its record and the SUCCESSOR freed, so the record stays live at the same address holding somebody else's data and R1's read is an IN-BOUNDS use-after-RECYCLE. AND THE HALF EVERY DETECTOR SEES IS THE HALF THAT CANNOT BE GATED: ASan, Miri, safe Rust's `Option` discriminant and a linear `PointsTo` are all mechanisms about the ALLOCATION and see the FREE half only -- whose checksum is not reproducible run to run -- while the RECYCLE half is silent, stable and wrong (../controls/repro.json publishes the invariant and no pinned count). WHAT THIS FENCE CLAIMED HERE UNTIL TASK_141 AND IT IS FALSE, MEASURED AND RETRACTED AT TASK_140: ~~p29's safety line NEEDS two conjuncts where p27's needs one~~. ONE CONJUNCT IS ENOUGH -- two single-conjunct spellings built from c/kernel.c by substitution score 0 wrong and 0 ASan lines with the positive control firing, and one of them adds NO STATE, widening `live[]` from a bit to the occupant tag (which p27's own kernel calls a generation counter with slot reuse removed). The two-conjunct spelling is a CHOICE -- it buys a free `wf` at R5, ../NOTES.md 6c -- and the row is not a duplicate of p27 for the TWO-BUG-CLASS reason above, which is a reason the conjunct count was never evidence for. GIVEN THIS SPELLING THE ORDER IS FORCED, WHICH IS WHY THESE TWO ARE NOT INTERCHANGEABLE: `tab[g_slot]` is never reset, so `tab[g_slot][0]` is the same load from the same address as `g_saved[0]`; C's `&&` short-circuits, so with the liveness conjunct in front the identity test is not evaluated on exactly the inputs where the record has been freed, and without it the identity test is ITSELF a heap-use-after-free (measured: zero ASan lines against a hit on every use-after-free window; the counts live in ../NOTES.md 2b and ../controls/arms.json and are deliberately NOT transcribed into this hashed fence). At R5 the ordering is not even a choice: `perms.tracked_borrow(g_slot)` has `dom().contains(g_slot)` as a precondition and `live[g_slot] == 1` is the only thing that discharges it, so the identity test cannot be written first -- a fact about the TWO-CONJUNCT spelling and not about the pattern, since a single-conjunct spelling has no ordering to force. WHY `tab[h]` IS NOT NULLED ON THE FREE, and it is p27's reason with a measurement behind it: nulling the table slot would turn a stale read into a NULL dereference -- a crash, not a use-after-free, and a different bug class. Measured on this kernel: with `tab[cur] = NULL` added, the one-conjunct control stops reporting `heap-use-after-free` and starts reporting `SEGV` (../NOTES.md 2c). It also keeps `tab[]` WRITE-ONCE PER SLOT, which is what lets R5 know `g_saved` is slot `g_slot`'s record through an invariant that no operation has to re-establish. WHY EVERY WALK CARRIES `live[cur] == 1` AND A `steps` BOUND, IN EVERY RUNG INCLUDING R1: they never fire -- a correct tree never links to a retired slot and no path is longer than TABCAP -- and they are pinned because R5 needs them. The liveness conjunct licenses the record read through `live[i] == 1 <==> perms.dom().contains(i)`, a PER-SLOT fact; the alternative is proving the link structure IS A TREE (unique parents, acyclicity), which no per-slot invariant gives you. The step bound is the `decreases` measure. They are in EVERY rung so that no rung-to-rung comparison is confounded by them, and the safe rungs would need the liveness half anyway -- `Option::unwrap` on a `None` slot is a panic. THE FREE MUST BE A REAL `free`: if the records were one slab and the release were a freelist push, the stale read would be IN BOUNDS OF A LIVE ALLOCATION -- Miri would not flag it, `PointsTo` would license it, and the bug would be LOGICAL, which is p17's class and the tree already has one. That is what `Box::into_raw`, `ManuallyDrop`, `mem::forget` and `Box::leak` are forbidden for. `realloc`/`calloc`/`Vec::with_capacity` are forbidden because they change the allocator traffic and the fairness argument is that every rung makes exactly one allocation and one free per record; `Rc`/`RefCell` because they would move the liveness decision to run time inside the library and delete the comparison. SLOTS ARE NEVER RECYCLED, AND THAT IS NOT A PRESENTATIONAL CHOICE. It is p27's convention (`ntab` only grows, which is what reduces the generation counter to one bit) and it is what keeps the safe rung's answer a function of the operations rather than of the allocator. `TASK_137` measured the third spelling -- an arena in which the release does NOT destroy the record -- and it is wrong on BOTH bug classes and BIT-IDENTICAL to buggy C, which is verbatim p32/p33's already-refused result; choosing it would retire this row rather than present it differently. WHAT IS DELIBERATELY NOT PINNED is how the liveness half is SPELLED in the safe rungs -- `is_some()` + `unwrap()` in R2, a `match` arm in R3 -- exactly as p14 leaves its fold loop unpinned: those are the R3-side levers, they cost zero TCB, and the pattern reports the cheapest one FOUND on a named input rather than a minimum. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p29-bst-delete.json`, contract `a7249f0d60f3`.

`68` backticked spelling(s) over `6` rung(s) → **220** (spelling, rung) pair(s), **97** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 18 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 5 spelling(s) pin nothing**, 49 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - pins nothing — `perms.tracked_borrow(g_slot)` (required[0], rust, 0 of 4 rungs)
  - pins nothing — `vstd::raw_ptr::deallocate` (required[3], rust, 0 of 4 rungs)
  - pins nothing — `deallocate` (required[3], rust, 0 of 4 rungs)
  - pins nothing — `malloc` (required[4], rust, 0 of 4 rungs)
  - pins nothing — `align <= 8` (required[4], rust, 0 of 4 rungs)
  - absent — `if (g_saved != NULL && live[g_slot] == 1 && tab[g_slot][0] == g_key) {` (required[0], c, **c/kernel.c**)
  - absent — `if (g_saved != NULL) {` (required[0], c, **c/kernel_hardened.c**)
  - absent — `if g_has && arr_get_unchecked(&live, g_slot as usize) == 1u8 {` (required[0], rust, **safe_naive.rs**)
  - absent — `if g_has && arr_get_unchecked(&live, g_slot as usize) == 1u8 {` (required[0], rust, **safe_tuned.rs**)
  - absent — `if rr.key == g_key {` (required[0], rust, **safe_naive.rs**)
  - absent — `if rr.key == g_key {` (required[0], rust, **safe_tuned.rs**)
  - absent — `Option` (required[0], rust, **unsafe.rs**)
  - absent — `Option` (required[0], rust, **verus.rs**)
  - absent — `tab[g_slot].is_some()` (required[0], rust, **safe_tuned.rs**)
  - absent — `tab[g_slot].is_some()` (required[0], rust, **unsafe.rs**)
  - absent — `tab[g_slot].is_some()` (required[0], rust, **verus.rs**)
  - absent — `Some(rec)` (required[0], rust, **safe_naive.rs**)
  - absent — `Some(rec)` (required[0], rust, **unsafe.rs**)
  - absent — `Some(rec)` (required[0], rust, **verus.rs**)
  - absent — `rec.key == g_key` (required[0], rust, **safe_naive.rs**)
  - absent — `rec.key == g_key` (required[0], rust, **unsafe.rs**)
  - absent — `rec.key == g_key` (required[0], rust, **verus.rs**)
  - absent — `arr_set_unchecked(&mut live, cur as usize, 0u8);` (required[1], rust, **safe_naive.rs**)
  - absent — `arr_set_unchecked(&mut live, cur as usize, 0u8);` (required[1], rust, **safe_tuned.rs**)
  - absent — `rec_free` (required[1], rust, **safe_naive.rs**)
  - absent — `rec_free` (required[1], rust, **safe_tuned.rs**)
  - absent — `tab[cur] = None` (required[1], rust, **unsafe.rs**)
  - absent — `tab[cur] = None` (required[1], rust, **verus.rs**)
  - absent — `Rec { key: srec.key, val: srec.val, l: co.l, r: co.r }` (required[2], rust, **safe_naive.rs**)
  - absent — `Rec { key: srec.key, val: srec.val, l: co.l, r: co.r }` (required[2], rust, **safe_tuned.rs**)
  - absent — `rec_write` (required[2], rust, **safe_naive.rs**)
  - absent — `rec_write` (required[2], rust, **safe_tuned.rs**)
  - absent — `Box` (required[2], rust, **unsafe.rs**)
  - absent — `Box` (required[2], rust, **verus.rs**)
  - absent — `std::alloc::dealloc(p, layout);` (required[3], rust, **safe_naive.rs**)
  - absent — `std::alloc::dealloc(p, layout);` (required[3], rust, **safe_tuned.rs**)
  - absent — `Option<Box<Rec>>` (required[3], rust, **unsafe.rs**)
  - absent — `Option<Box<Rec>>` (required[3], rust, **verus.rs**)
  - absent — `std::alloc::alloc(layout)` (required[4], rust, **safe_naive.rs**)
  - absent — `std::alloc::alloc(layout)` (required[4], rust, **safe_tuned.rs**)
  - absent — `Box::new(Rec {` (required[4], rust, **unsafe.rs**)
  - absent — `Box::new(Rec {` (required[4], rust, **verus.rs**)
  - absent — `while cur != NIL && arr_get_unchecked(live, cur as usize) == 1u8 && steps < TABCAP` (required[5], rust, **safe_naive.rs**)
  - absent — `while cur != NIL && arr_get_unchecked(live, cur as usize) == 1u8 && steps < TABCAP` (required[5], rust, **safe_tuned.rs**)
  - absent — `Option` (required[5], rust, **unsafe.rs**)
  - absent — `Option` (required[5], rust, **verus.rs**)
  - absent — `tab[cur].is_some()` (required[5], rust, **safe_tuned.rs**)
  - absent — `tab[cur].is_some()` (required[5], rust, **unsafe.rs**)
  - absent — `tab[cur].is_some()` (required[5], rust, **verus.rs**)
  - absent — `match tab[cur].as_ref()` (required[5], rust, **safe_naive.rs**)
  - absent — `match tab[cur].as_ref()` (required[5], rust, **unsafe.rs**)
  - absent — `match tab[cur].as_ref()` (required[5], rust, **verus.rs**)
  - absent — `None` (required[5], rust, **unsafe.rs**)
  - absent — `None` (required[5], rust, **verus.rs**)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## What the gate said out loud (reporting only)

From `results/gate/p29-bst-delete.json` — the `loud` and `controls_json` keys, at contract `a7249f0d60f3`. **These did not fail the gate and are not defects**; they are the conditions `check.py` refuses to be silent about. Each one is a caveat on a number below or on the declaration above. The run's **verdict** is deliberately not printed here: it is an output of the same gate run that checks this table is current (stage `9c`), and rendering it made the table an input to its own checker — see `read_gate_loud`. Read the verdict from `results/gate/p29-bst-delete.json`.

- **`collapse-ir`** — the derived floor is 277x below the tightest cell actually measured, so it rules out total collapse and essentially nothing else -- a cell could lose 99.64% of its work and still pass this stage. Read it as a smoke test, not as evidence that the work happened.
- **`tcb-unsafe`** — verus.rs:510 `arr_set_unchecked`'s `requires` constrains nothing about ['x'], which its trusted body uses. spec.md justifies it: `x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `T` is a legal thing to store in a `T` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` reads `i < N`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second, p06 the third, p14 the fourth, p27 the fifth and p29 the sixth.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 363 | 350 | 0 | 1,453 | 412,356,197 | 237,785,511 | 3,000,056 | 300,056 | `57ee4859` | `57ee4859` | yes | xmm |
| c-clang | 360 | 355 | 0 | 1,440 | 432,738,432 | 253,376,134 | 2,800,055 | 280,055 | `354b75e7` | `354b75e7` | yes | xmm |
| safe_naive | 504 | 495 | 1 | 2,239 | 453,778,017 | 285,577,382 | 2,800,275 | 280,275 | `03594551` | `871fd7d2` | yes | xmm |
| safe_tuned | 548 | 533 | 3 | 2,413 | 447,988,102 | 283,693,368 | 2,800,275 | 280,275 | `526e77f2` | `8d9f3e41` | yes | xmm |
| unsafe | 596 | 587 | 15 | 2,785 | 434,578,501 | 265,741,451 | 2,800,275 | 280,275 | `6b7c8cf6` | `e24fc411` | yes | xmm |
| verus | 596 | 587 | 15 | 2,785 | 434,578,501 | 265,741,451 | 2,800,270 | 280,270 | `4776eb76` | `02fd34b9` | yes | xmm |
| c-gcc-h | 376 | 363 | 0 | 1,526 | 408,664,771 | 237,830,495 | 3,000,056 | 300,056 | `4ef10371` | `4ef10371` | yes | xmm |
| c-clang-h | 365 | 360 | 1 | 1,502 | 427,307,832 | 251,479,250 | 2,800,055 | 280,055 | `897f3c83` | `eb7e5a90` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 577 | 576 | 0 | 2,907 | 695,175,459 | - | 7,200,066 | - | `41b853c8` | `41b853c8` | yes | - |
| c-clang | 529 | 529 | 1 | 2,830 | 839,475,625 | - | 4,200,052 | - | `c0a1c204` | `cbbbb08e` | yes | - |
| safe_naive | 1,907 | 1,907 | 6 | 10,778 | 1,423,922,521 | - | 5,000,077 | - | `8ab4f244` | `0e8116ad` | yes | - |
| safe_tuned | 1,145 | 1,145 | 5 | 6,667 | 1,090,757,669 | - | 5,000,077 | - | `9e4f3c18` | `51ca8f81` | yes | - |
| unsafe | 857 | 857 | 13 | 5,059 | 1,072,020,686 | - | 5,000,077 | - | `3f85ce96` | `d3f7c506` | yes | - |
| verus | 899 | 899 | 1 | 5,359 | 1,096,251,878 | - | 5,000,056 | - | `b74e2921` | `1316bb4e` | yes | - |
| c-gcc-h | 588 | 587 | 0 | 2,959 | 696,287,779 | - | 7,200,066 | - | `2afe199c` | `2afe199c` | yes | - |
| c-clang-h | 539 | 539 | 1 | 2,879 | 840,486,825 | - | 4,200,052 | - | `32c38ea4` | `4b655070` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 567 | 562 | 1 | 2,315 | - | - | 405,941,604 | 235,256,763 | `4a002d45` | `61f1f0c3` | yes | - |
| c-clang | 614 | 594 | 0 | 2,633 | - | - | 435,559,433 | 253,347,042 | `275c054f` | `275c054f` | yes | xmm |
| safe_naive | 1,145 | 1,129 | 1 | 5,455 | - | - | 454,360,566 | 287,769,246 | `eb1c40b6` | `b2e44c20` | yes | xmm |
| safe_tuned | 1,161 | 1,144 | 1 | 5,503 | - | - | 449,996,750 | 286,089,393 | `d73c4021` | `30eb7d6c` | yes | xmm |
| unsafe | 1,249 | 1,218 | 1 | 6,063 | - | - | 424,779,256 | 263,692,089 | `3884cfce` | `719ca6bf` | yes | xmm |
| verus | 1,303 | 1,272 | 2 | 6,094 | - | - | 445,741,401 | 273,030,779 | `3b064267` | `5647e03f` | yes | xmm |
| c-gcc-h | 582 | 575 | 1 | 2,458 | - | - | 411,510,622 | 239,641,755 | `ae7d0264` | `76078a7c` | yes | - |
| c-clang-h | 598 | 582 | 0 | 2,628 | - | - | 429,601,391 | 253,392,737 | `2684df8c` | `2684df8c` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 695,175,459 | - | 7,200,066 | - | `c9863a08` | `c9863a08` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 790,575,005 | - | 4,200,051 | - | `344173a6` | `344173a6` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 1,423,922,521 | - | 5,000,077 | - | `9e6a2ad9` | `49a327ba` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 1,090,757,669 | - | 5,000,077 | - | `d7ac1133` | `1ff1957f` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 1,072,020,686 | - | 5,000,077 | - | `c477ba51` | `84d1f6d3` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 1,096,251,878 | - | 5,000,056 | - | `a331919f` | `c27df4da` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 696,287,779 | - | 7,200,066 | - | `ccda2270` | `ccda2270` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 791,586,205 | - | 4,200,051 | - | `c3b9d28c` | `c3b9d28c` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | no | no | 857/857 vs 899/899 | 13 B vs 1 B |
| unsafe vs verus | O3 | no | **yes** | no | 596/587 vs 596/587 | 15 B vs 15 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 85.79 | 87.05 | 1.5% | 58.17 | 59.01 | 1.4% |
| c-gcc | whole | 86.27 | 87.61 | 1.6% | 58.18 | 58.76 | 1.0% |
| c-clang | isolated | 90.67 | 91.89 | 1.3% | 58.98 | 60.44 | 2.5% |
| c-clang | whole | 89.31 | 90.52 | 1.3% | 58.02 | 59.13 | 1.9% |
| safe_naive | isolated | 94.25 | 95.28 | 1.1% | 64.46 | 65.47 | 1.6% |
| safe_naive | whole | 95.41 | 96.73 | 1.4% | 63.75 | 65.18 | 2.2% |
| safe_tuned | isolated | 95.14 | 96.68 | 1.6% | 65.98 | 66.90 | 1.4% |
| safe_tuned | whole | 96.04 | 97.36 | 1.4% | 62.85 | 64.43 | 2.5% |
| unsafe | isolated | 94.55 | 95.90 | 1.4% | 63.82 | 65.32 | 2.3% |
| unsafe | whole | 95.32 | 96.69 | 1.4% | 62.21 | 63.82 | 2.6% |
| verus | isolated | 95.35 | 96.84 | 1.6% | 63.31 | 65.21 | 3.0% |
| verus | whole | 94.36 | 95.95 | 1.7% | 62.64 | 63.73 | 1.7% |
| c-gcc-h | isolated | 85.93 | 87.35 | 1.7% | 55.91 | 56.63 | 1.3% |
| c-gcc-h | whole | 86.51 | 87.43 | 1.1% | 57.82 | 58.92 | 1.9% |
| c-clang-h | isolated | 87.71 | 89.24 | 1.7% | 57.16 | 58.52 | 2.4% |
| c-clang-h | whole | 88.71 | 90.15 | 1.6% | 56.40 | 58.44 | 3.6% |

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
