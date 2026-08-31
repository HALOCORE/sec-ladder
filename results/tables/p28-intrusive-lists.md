# p28-intrusive-lists — results

Generated 2026-08-31T02:06:16Z from `results/p28-intrusive-lists.json` (git `dff659297180`, working tree dirty).

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
| adversarial-many.bin | 200,000 | 52 | 52 | False | n_iters=200000 stride=44 n_blob=44 nwin=1 calls=200000 work/call=44B san=fires truncated=False expected=8660776832395219968 |
| adversarial-stride3.bin | 200,000 | 38 | 38 | False | n_iters=200000 stride=3 n_blob=30 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| adversarial-uaf-head.bin | 200,000 | 20 | 20 | False | n_iters=200000 stride=12 n_blob=12 nwin=1 calls=200000 work/call=12B san=fires truncated=False expected=11740759076003072000 |
| adversarial-uaf-read.bin | 200,000 | 20 | 20 | False | n_iters=200000 stride=12 n_blob=12 nwin=1 calls=200000 work/call=12B san=fires truncated=False expected=14476180526798907392 |
| adversarial-uaf-write.bin | 200,000 | 20 | 20 | False | n_iters=200000 stride=12 n_blob=12 nwin=1 calls=200000 work/call=12B san=fires truncated=False expected=14476180526798907392 |
| degenerate.bin | 20,000 | 272 | 272 | False | n_iters=20000 stride=264 n_blob=264 nwin=1 calls=20000 work/call=264B san=clean truncated=False expected=17281166933783909376 |
| large.bin | 20,000 | 15,624 | 15,624 | False | n_iters=20000 stride=244 n_blob=15616 nwin=64 calls=20000 work/call=244B san=clean truncated=False expected=6273464424967602007 |
| small.bin | 200,000 | 424 | 424 | False | n_iters=200000 stride=52 n_blob=416 nwin=8 calls=200000 work/call=52B san=clean truncated=False expected=18314675230631941442 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE SAFETY LINE, and the only thing c/kernel.c omits: the hash-chain splice in TRIM, `if (victim->hp != NULL)` followed by `victim->hp->hn = victim->hn;` and `bucket[vb] = victim->hn;` and `victim->hn->hp = victim->hp;` in c/kernel_hardened.c. c/kernel.c goes straight from `tail = victim->lp;` to `free(victim);` and is otherwise character-identical; controls/safety_line.py preprocesses both and measures a pure +9 / -0 addition.
  - `rust` — THE SAFETY LINE, in all four Rust rungs, spliced through SLOT NUMBERS because that is what the representation forces: three spellings, one per representation, each scoped-absent on the rungs that are not its own: `bucket[vb] = tab[v].as_ref().unwrap().hn;` in safe_naive.rs, `bucket[vb] = hnv;` in safe_tuned.rs, and `arr_set_unchecked(&mut bucket, vb, vo.hn);` in unsafe.rs and verus.rs. ⚠ Not one of the four gets any part of it from the language -- see the why key, and controls/arm_safe_bug.rs for what deleting it does in safe Rust.
- **required** — *per language:*
  - `c` — TRIM'S VICTIM IS THE EVICTION LIST'S OLDEST END AND IT IS REACHED WITHOUT A CHAIN CURSOR, in both C rungs: `victim = tail;`. That is why TRIM is the path that forgets and DEL is not.
  - `rust` — the same victim, in all four Rust rungs: `tail` is read into `v` and nothing on the path holds a bucket cursor.
- **required** — *per language:*
  - `c` — DEL SPLICES BOTH LISTS AND THEN FREES, in both C rungs -- it arrives ALONG the chain, so it is already holding the cursor TRIM lacks: `if (n->hp != NULL)`.
  - `rust` — the same splice in all four Rust rungs, on the victim's four links read out of the object.
- **required** — *per language:*
  - `c` — THE ALLOCATION BUDGET IS ALSO THE WALK'S FUEL, in both C rungs: `nmade < P28_SLOTS` and `steps < P28_SLOTS`. See the why key for why a C reader would not write the first.
  - `rust` — the same two, in all four Rust rungs: `nmade < SLOTS` and `steps < SLOTS`.
- **required** — *per language:*
  - `c` — the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the additive form's overflow never arises: `if (len - p < 2)` in both C rungs.
  - `rust` — the cursor guard, subtraction-first, in all four Rust rungs: `if len - p < 2 {`.
- **required** — *per language:*
  - `c` — the opcode is `c % 4`, so EVERY byte value is a legal opcode and no input is rejected for being malformed: `c % 4 == 0` in both C rungs.
  - `rust` — the opcode, in all four Rust rungs: `c % 4 == 0`.
- **required** — *per language:*
  - `c` — the bucket is the operand modulo the table width, so every operand lands somewhere: `a % P28_NB` in both C rungs.
  - `rust` — the bucket, in all four Rust rungs: `a % NB as u8`.
- **required** — *per language:*
  - `c` — a rejected operation folds the SENTINEL rather than being skipped, so the fold's length is a function of the op count alone: `SENT` in both C rungs.
  - `rust` — the sentinel fold, in all four Rust rungs: `SENT`.
- **required** — *per language:*
  - `c` — the fold is a serial Horner chain over `acc`, spelled with the literal multiplier, ONCE per operation: `acc = acc * 31 +` in both C rungs.
  - `rust` — the fold, in all four Rust rungs, spelled with the literal multiplier: `acc.wrapping_mul(31).wrapping_add`.
- **required** — *per language:*
  - `c` — the OBJECT COUNT is folded last, so a rung that made a different number of objects cannot produce the same checksum: `return acc * 31 + (uint64_t)nmade;` in both C rungs.
  - `rust` — the same, in all four Rust rungs: `acc.wrapping_mul(31).wrapping_add(nmade as u64)`.
- **required** — *per language:*
  - `c` — THE LINKS COME FIRST IN THE STRUCT, in both C rungs: `struct p28_obj *lp, *ln;`. It is what makes R1's stale read reproducible rather than ASLR-dependent -- c/kernel.h's LAYOUT NOTE, and controls/repro.py measures both sides of it.
  - `rust` — not applicable: the Rust rungs' links are slot numbers, so there is no layout question. The why key states the divergence and controls/arm_rawptr.rs measures it.
- **required** — THE EPILOGUE FREES EVERY OBJECT STILL ALIVE, in all seven rungs, so NEITHER C rung LEAKS, and NEITHER DOUBLE-FREES IN THE EPILOGUE -- TRIM unlinks its victim from the eviction list before freeing it, so the epilogue's walk cannot reach it. It is spelled three ways because the representation forces three: the C rungs walk the eviction list, unsafe.rs and verus.rs scan the slot table, and safe_naive.rs and safe_tuned.rs have no epilogue at all because dropping the table IS the loop. ⚠⚠ THIS ENTRY READ 'so NEITHER C rung leaks and neither double-frees', UNSCOPED, UNTIL TASK_150, AND THE SECOND HALF OF THAT WAS FALSE. R1's DEL double-frees: its walk can reach an object TRIM already released and then run the splice to completion, free(n) included. Measured on adversarial-uaf-write.bin with a --wrap=malloc,--wrap=free interposer under LEAKING semantics -- the semantics model.py and all four Rust rungs implement, since slots are never recycled -- R1 gives mallocs=4 frees=5 doublefree=1 where R1h gives 4/4/0, on the same input through the same driver, with the safety line as the only difference; every other shipped input is balanced in both arms. The real allocator masks it, because glibc's tcache overwrites the freed chunk's user offsets 0 and 8, which are exactly lp and ln, so the splice faults two statements before free(n). THE LEAK HALF OF THE OLD SENTENCE IS TRUE AND STAYS. This is PROTOCOL rule 6's second half -- the hash matched and the measurement refuted the claim -- and it is p46's shape on a second pattern. NOTES.md 2d and 10 carry the numbers and the sha256 disclosure.
- **FORBIDDEN** — `realloc(`
- **FORBIDDEN** — `calloc(`
- **FORBIDDEN** — `Vec::with_capacity`
- **FORBIDDEN** — `VecDeque`
- **FORBIDDEN** — `HashMap`
- **FORBIDDEN** — `Rc<`
- **FORBIDDEN** — `Weak<`
- **FORBIDDEN** — `RefCell`
- **FORBIDDEN** — `ManuallyDrop`
- **FORBIDDEN** — `mem::forget`
- **FORBIDDEN** — `Box::leak`
- **FORBIDDEN** — `Box::into_raw`

> **Why**: POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens below must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ONE OMITTED BLOCK, ON THE DESTROY PATH, AND THAT IS THE ROW. An object here carries TWO INTRUSIVE LINK SETS -- a doubly linked eviction list (`lp`/`ln`) and a doubly linked hash chain (`hn`/`hp`) -- so IT IS ALIASED BY TWO LISTS AT ONCE AND MEMBERSHIP IS NOT OWNERSHIP. TRIM reaches its victim through the EVICTION list, so it holds no chain cursor and has to go and get one; DEL reaches its victim by WALKING THE CHAIN, so it is already holding one. THE PATH THAT ARRIVES FROM THE OTHER LIST IS THE ONE THAT FORGETS, and that is the shape of this bug in real code rather than an arbitrary choice of arm. THE READ PATH IS CORRECT AND THE DESTROY PATH IS INCOMPLETE, which is the INVERSION of p27, p29 and p32 -- all three keep a correct free discipline and put the missing check on the READ. There is no test to add on this rung's read path. THE DANGLING POINTER ENDS UP INSIDE ANOTHER HEAP OBJECT'S `hn` FIELD, or in `bucket[]` when the victim was the chain head -- NOT in a stack table (p27's `tab[]`), NOT in a stack local (p29's `g_saved`), NOT in a program-owned pool (p32, which frees nothing). `controls/harm_sites.py` measures both sites separately, in the HARDENED arm and before any free, and ASan reports a heap-use-after-free on the buggy arm at each. AND THERE IS NOTHING THE INPUT CAN INDEX: the input names an object only by KEY and the program finds it by walking, so p27's `h < ntab && live[h] == 1` has NO ANALOGUE BECAUSE THERE IS NO `h`. Neither C rung contains a slot number, a liveness bit or a generation. THE ALLOCATION BUDGET `nmade < P28_SLOTS` IS THE CACHE'S ONLY SIZE LIMIT AND IT IS ALSO THE WALK'S FUEL. It is a budget per WINDOW rather than a live capacity, and it is spelled that way because R2-R5 hold their objects in a FIXED-SIZE TABLE with slots never recycled -- safe Rust cannot hold an intrusive pointer list, so every Rust rung indexes a slot table instead -- and all seven rungs must agree on every window. p29's C rungs carry `ntab < TABCAP` for exactly the same reason and say so. TRIM IS A SHRINKER: something outside the cache asks it to give storage back, which is why there is no capacity test and why TRIM is an opcode rather than a consequence of PUT. THE RUST RUNGS DIVERGE FROM THE C MECHANISM IN ONE DISCLOSED WAY AND IT IS MEASURED RATHER THAN ARGUED: the C rungs store the four links as POINTERS, and every Rust rung stores them as SLOT NUMBERS into a table. Safe Rust has no choice -- an object on two intrusive lists is an object with two owners -- and unsafe.rs and verus.rs follow it so that R4 and R5 stay byte-comparable and so that the proof can be carried by a per-slot invariant instead of the full doubly-linked-list well-formedness (`hn[hp[j]] == j` and its three siblings) that an address-keyed permission map would need. `controls/arm_rawptr.rs` is the FAITHFUL raw-pointer port of both C arms, from one macro expansion; it agrees with the shipped rungs on every input, and Miri reports undefined behaviour on its BUG arm on all four adversarial inputs and on nothing else. That is the measurement the divergence owes, and NOTES.md 5 prices it. THE ONE EXEC CONJUNCT THE C RUNGS CANNOT SPELL is the liveness half of a link test: the walk's `live[cur] == 1u8` and `alive_link`'s second half, ten sites in unsafe.rs and verus.rs. Not one of them can fire -- a correct chain holds only live objects -- and they are there because the alternative is the list invariant. p29 could put its liveness conjuncts in its C rungs too; p28 CANNOT, and the reason is this row's own headline: p28's C links are POINTERS and there is no `live[]` bit anywhere in either C rung. THE PROPERTY THAT MAKES THE ROW DISTINCT AT C LEVEL IS THE PROPERTY THAT MAKES THAT CONJUNCT UNSPELLABLE THERE. THIS PATTERN PUBLISHES NO RUNG-TO-RUNG COST AT ALL (NOTES.md 8), and the absence is stated rather than left to read as a zero. It is not shyness: `TASK_093_REVIEW` measured that a p28 with a safe index arena against a raw-pointer unsafe rung would have published `safe Rust is 6.02x CHEAPER than unsafe` with 108.4% of the gap IN THE ALLOCATOR and the bounds check at 3.0% of the magnitude AND THE OPPOSITE SIGN, and `TASK_091` measured that 4.0 of a 12.5 R3->R4 gap is INDEX SCALING rather than checking. The rungs here differ in ALLOCATION SIZE (40 bytes of pointers in C against 6 bytes of slot numbers in Rust), in EPILOGUE SHAPE (C walks the eviction list, R4/R5 scan the slot table, R2/R3 drop the table) and in the ten non-firing liveness conjuncts above. Any of the three would confound a spread, so none is published. p29 ships the same way. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p28-intrusive-lists.json`, contract `f0bd1f608df2`.

`56` backticked spelling(s) over `6` rung(s) → **162** (spelling, rung) pair(s), **78** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 24 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 0 spelling(s) pin nothing**, 12 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - absent — `if (victim->hp != NULL)` (required[0], c, **c/kernel.c**)
  - absent — `victim->hp->hn = victim->hn;` (required[0], c, **c/kernel.c**)
  - absent — `bucket[vb] = victim->hn;` (required[0], c, **c/kernel.c**)
  - absent — `victim->hn->hp = victim->hp;` (required[0], c, **c/kernel.c**)
  - absent — `bucket[vb] = tab[v].as_ref().unwrap().hn;` (required[0], rust, **safe_tuned.rs**)
  - absent — `bucket[vb] = tab[v].as_ref().unwrap().hn;` (required[0], rust, **unsafe.rs**)
  - absent — `bucket[vb] = tab[v].as_ref().unwrap().hn;` (required[0], rust, **verus.rs**)
  - absent — `bucket[vb] = hnv;` (required[0], rust, **safe_naive.rs**)
  - absent — `bucket[vb] = hnv;` (required[0], rust, **unsafe.rs**)
  - absent — `bucket[vb] = hnv;` (required[0], rust, **verus.rs**)
  - absent — `arr_set_unchecked(&mut bucket, vb, vo.hn);` (required[0], rust, **safe_naive.rs**)
  - absent — `arr_set_unchecked(&mut bucket, vb, vo.hn);` (required[0], rust, **safe_tuned.rs**)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## What the gate said out loud (reporting only)

From `results/gate/p28-intrusive-lists.json` — the `loud` and `controls_json` keys, at contract `f0bd1f608df2`. **These did not fail the gate and are not defects**; they are the conditions `check.py` refuses to be silent about. Each one is a caveat on a number below or on the declaration above. The run's **verdict** is deliberately not printed here: it is an output of the same gate run that checks this table is current (stage `9c`), and rendering it made the table an input to its own checker — see `read_gate_loud`. Read the verdict from `results/gate/p28-intrusive-lists.json`.

- **`collapse-ir`** — the derived floor is 186x below the tightest cell actually measured, so it rules out total collapse and essentially nothing else -- a cell could lose 99.46% of its work and still pass this stage. Read it as a smoke test, not as evidence that the work happened.
- **`tcb-unsafe`** — verus.rs:591 `arr_set_unchecked`'s `requires` constrains nothing about ['x'], which its trusted body uses. spec.md justifies it: `x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `T` is a legal thing to store in a `T` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` reads `i < N`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second, p06 the third, p14 the fourth, p27 the fifth, p29 the sixth, p32 the seventh and p28 the eighth.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 250 | 238 | 0 | 1,011 | 210,243,218 | 122,678,018 | 3,000,056 | 300,056 | `5428c482` | `5428c482` | yes | xmm |
| c-clang | 269 | 265 | 1 | 973 | 243,047,368 | 140,121,576 | 2,800,055 | 280,055 | `a66f3336` | `ff694acc` | yes | xmm |
| safe_naive | 532 | 522 | 6 | 2,266 | 386,910,519 | 211,267,507 | 2,800,275 | 280,275 | `54965f07` | `969804b4` | yes | - |
| safe_tuned | 534 | 526 | 7 | 2,217 | 436,272,774 | 236,511,509 | 2,800,275 | 280,275 | `ccdf394d` | `568317ce` | yes | - |
| unsafe | 360 | 356 | 11 | 1,429 | 299,017,209 | 185,227,142 | 2,800,275 | 280,275 | `e2cdf0f0` | `0af40ea7` | yes | xmm |
| verus | 360 | 356 | 11 | 1,429 | 299,017,209 | 185,227,142 | 2,800,270 | 280,270 | `4bfc0af7` | `e1944e0b` | yes | xmm |
| c-gcc-h | 264 | 250 | 0 | 1,086 | 209,859,062 | 122,303,688 | 3,000,056 | 300,056 | `1e29527f` | `1e29527f` | yes | xmm |
| c-clang-h | 289 | 285 | 2 | 1,059 | 247,629,241 | 141,906,810 | 2,800,055 | 280,055 | `cf7253e4` | `e6bbe7d2` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 396 | 395 | 0 | 1,905 | 399,125,744 | - | 7,200,066 | - | `001bb7f3` | `001bb7f3` | yes | - |
| c-clang | 378 | 378 | 1 | 1,951 | 470,222,745 | - | 4,200,052 | - | `d75a9a94` | `1f895cd3` | yes | - |
| safe_naive | 2,235 | 2,235 | 0 | 12,400 | 891,503,712 | - | 5,000,077 | - | `14f5cdaa` | `14f5cdaa` | yes | - |
| safe_tuned | 1,188 | 1,188 | 6 | 6,650 | 806,764,829 | - | 5,000,077 | - | `636ceaed` | `80d0e9ed` | yes | - |
| unsafe | 1,262 | 1,262 | 6 | 7,498 | 896,326,968 | - | 5,000,077 | - | `cc71703e` | `4d3cfb52` | yes | - |
| verus | 1,394 | 1,394 | 11 | 8,469 | 951,425,664 | - | 5,000,056 | - | `6de4880a` | `eaae74cb` | yes | - |
| c-gcc-h | 424 | 423 | 0 | 2,051 | 403,914,877 | - | 7,200,066 | - | `6f402972` | `6f402972` | yes | - |
| c-clang-h | 406 | 406 | 1 | 2,089 | 475,011,878 | - | 4,200,052 | - | `536af64d` | `448377d8` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 485 | 473 | 1 | 2,007 | - | - | 214,665,231 | 126,371,779 | `a2083f88` | `81e7b888` | yes | xmm |
| c-clang | 505 | 486 | 0 | 2,005 | - | - | 249,838,578 | 142,923,422 | `4c87f0ac` | `4c87f0ac` | yes | xmm |
| safe_naive | 1,163 | 1,143 | 1 | 5,423 | - | - | 399,582,361 | 217,445,977 | `e2ecad6e` | `4b8012c1` | yes | xmm |
| safe_tuned | 1,172 | 1,155 | 1 | 5,391 | - | - | 442,436,428 | 243,998,568 | `abd4303b` | `afd54b3f` | yes | xmm |
| unsafe | 1,010 | 987 | 1 | 4,591 | - | - | 303,555,761 | 185,990,497 | `4aa77380` | `9cde80f0` | yes | xmm |
| verus | 1,031 | 1,007 | 1 | 4,607 | - | - | 312,638,098 | 190,156,281 | `7a730cf0` | `87cbeeee` | yes | xmm |
| c-gcc-h | 498 | 485 | 1 | 2,055 | - | - | 217,324,831 | 127,219,961 | `4f31e9da` | `d25fcd66` | yes | xmm |
| c-clang-h | 523 | 503 | 0 | 2,087 | - | - | 252,448,583 | 143,699,895 | `16eaca6e` | `16eaca6e` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 399,125,744 | - | 7,200,066 | - | `523167c5` | `523167c5` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 458,165,148 | - | 4,200,051 | - | `05654ac6` | `05654ac6` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 891,503,712 | - | 5,000,077 | - | `e78962e4` | `1f6ee4fa` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 806,764,829 | - | 5,000,077 | - | `4c557d1b` | `1b855158` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 896,326,968 | - | 5,000,077 | - | `0f986f5b` | `f941138e` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 951,425,664 | - | 5,000,056 | - | `a331919f` | `c27df4da` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 403,914,877 | - | 7,200,066 | - | `7f4f63c2` | `7f4f63c2` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 462,954,281 | - | 4,200,051 | - | `1dd0eb12` | `1dd0eb12` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | no | no | 1262/1262 vs 1394/1394 | 6 B vs 11 B |
| unsafe vs verus | O3 | no | **yes** | no | 360/356 vs 360/356 | 11 B vs 11 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 45.42 | 46.01 | 1.3% | 36.94 | 37.46 | 1.4% |
| c-gcc | whole | 45.73 | 46.14 | 0.9% | 36.34 | 36.82 | 1.3% |
| c-clang | isolated | 48.19 | 49.40 | 2.5% | 37.76 | 38.91 | 3.0% |
| c-clang | whole | 48.94 | 49.48 | 1.1% | 38.34 | 39.62 | 3.3% |
| safe_naive | isolated | 58.50 | 60.28 | 3.0% | 52.74 | 54.62 | 3.6% |
| safe_naive | whole | 59.60 | 60.75 | 1.9% | 54.03 | 56.22 | 4.0% |
| safe_tuned | isolated | 60.81 | 61.52 | 1.2% | 52.07 | 53.10 | 2.0% |
| safe_tuned | whole | 60.96 | 61.79 | 1.4% | 51.51 | 52.26 | 1.5% |
| unsafe | isolated | 59.41 | 60.16 | 1.3% | 50.04 | 51.23 | 2.4% |
| unsafe | whole | 58.91 | 59.68 | 1.3% | 48.11 | 49.21 | 2.3% |
| verus | isolated | 58.36 | 59.43 | 1.8% | 46.79 | 48.37 | 3.4% |
| verus | whole | 60.78 | 61.84 | 1.7% | 50.27 | 51.41 | 2.3% |
| c-gcc-h | isolated | 45.86 | 46.94 | 2.4% | 36.15 | 36.80 | 1.8% |
| c-gcc-h | whole | 45.97 | 46.82 | 1.9% | 36.38 | 36.89 | 1.4% |
| c-clang-h | isolated | 49.02 | 49.81 | 1.6% | 38.30 | 39.21 | 2.4% |
| c-clang-h | whole | 48.73 | 49.57 | 1.7% | 38.59 | 39.86 | 3.3% |

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
