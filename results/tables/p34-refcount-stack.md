# p34-refcount-stack — results

Generated 2026-08-31T15:26:04Z from `results/p34-refcount-stack.json` (git `9aa425a398f6`, working tree dirty).

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
| adversarial-blind.bin | 200,000 | 44 | 44 | False | n_iters=200000 stride=36 n_blob=36 nwin=1 calls=200000 work/call=36B san=fires truncated=False expected=5576862673510090752 |
| adversarial-blindread.bin | 200,000 | 52 | 52 | False | n_iters=200000 stride=44 n_blob=44 nwin=1 calls=200000 work/call=44B san=fires truncated=False expected=12442434272084377600 |
| adversarial-many.bin | 20,000 | 396 | 396 | False | n_iters=20000 stride=388 n_blob=388 nwin=1 calls=20000 work/call=388B san=fires truncated=False expected=2893199866468423680 |
| adversarial-recycle.bin | 200,000 | 68 | 68 | False | n_iters=200000 stride=60 n_blob=60 nwin=1 calls=200000 work/call=60B san=fires truncated=False expected=7544618244297525248 |
| adversarial-stride3.bin | 200,000 | 38 | 38 | False | n_iters=200000 stride=3 n_blob=30 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| degenerate.bin | 200,000 | 80 | 80 | False | n_iters=200000 stride=72 n_blob=72 nwin=1 calls=200000 work/call=72B san=clean truncated=False expected=12018165609759525888 |
| large.bin | 20,000 | 15,624 | 15,624 | False | n_iters=20000 stride=244 n_blob=15616 nwin=64 calls=20000 work/call=244B san=clean truncated=False expected=7726184805965551230 |
| small.bin | 200,000 | 424 | 424 | False | n_iters=200000 stride=52 n_blob=416 nwin=8 calls=200000 work/call=52B san=clean truncated=False expected=13533250923909195085 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE SAFETY LINE, and the only thing c/kernel.c omits: ONE statement on the DUP path, `t->rc = t->rc + 1;` in c/kernel_hardened.c. c/kernel.c is otherwise character-identical, and ../controls/safety_line.py preprocesses both shipped files and measures the difference at `+1 / -0` lines -- the smallest safety line in this tree.
  - `rust` — THE SAFETY LINE, in R4 and R5 only, spelled as the call the C rung omits: `obj_retain(t);` immediately after `let t = arr_get_unchecked(&stk, ntop - 1);`. ⚠⚠ R2 AND R3 HAVE NO SITE FOR THIS LINE AND THAT IS THE ROW'S SAFE-RUST RESULT, NOT AN OMISSION -- see the next entry and the why key.
- **required** — *per language:*
  - `c` — THE OBJECT CARRIES ITS OWN COUNT, in both C rungs and in c/kernel.h: `size_t rc;` as the FIRST member of `struct p34_obj`. The position is load-bearing and disclosed -- it is what puts glibc's tcache words on `rc` and `len` and leaves `data` intact.
  - `rust` — the same in R4 and R5: `pub rc: usize,` as the first field of `#[repr(C)] pub struct Obj`. ⚠ In R2 and R3 the count is `Rc`'s own and this field does not exist -- `Rc::clone(` is where it is incremented and the `Drop` is where it is decremented. That is the one place the rungs are not isomorphic and the why key argues it.
- **required** — *per language:*
  - `c` — THE RELEASE IS A DECREMENT AND A FREE AT ZERO, CORRECT IN BOTH C RUNGS: `o->rc = o->rc - 1;` followed by `if (o->rc == 0)` and `free(o);`. R1's bug is NOT that it releases wrongly -- it does not -- it is that publishing a reference does not count it.
  - `rust` — the same in R4 and R5, through the accessor both rungs share: `let n = obj_dec(q);` followed by `if n == 0 {` and `obj_free(q);`.
- **required** — *per language:*
  - `c` — THE STACK IS A FIXED-EXTENT LOCAL AND EVERY ENTRY IS RELEASED EXACTLY ONCE, in both C rungs: `struct p34_obj *stk[P34_CAP];` plus the epilogue `while (ntop > 0) {`. The epilogue is what makes `0 -> underflow` reachable from every DUP and is why the bug has no benign input.
  - `rust` — the same array in R4 and R5, `[*mut Obj; CAP]`, with the same epilogue `while ntop > 0 {`. ⚠⚠ R2 AND R3 HAVE NO EPILOGUE: dropping `[Option<Rc<Obj>>; CAP]` IS that loop, written by the language. NOTES.md 5 prices the difference.
- **required** — *per language:*
  - `c` — THE STORAGE IS ONE `malloc` PER OBJECT AND A REAL `free`, in both C rungs: `malloc(sizeof *o)` and `free(o);`. A pool or a free list would leave the stale use inside a live allocation and the row would be p32's; see the why key, which measures both.
  - `rust` — the same in R4 and R5, through vstd's own allocation API copied for codegen: `std::alloc::alloc(layout)` and `std::alloc::dealloc(p, layout);`. In R2 and R3 it is `Rc::new(`, which is the same allocator and one allocation per object.
- **required** — *per language:*
  - `c` — the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the additive form's overflow never arises: `if (len - p < 2)` in both C rungs.
  - `rust` — the cursor guard, subtraction-first: `if len - p < 2 {` in R2, R4 and R5. ⚠ R3 does not write it -- `chunks_exact(2).take(nops)` carries the same bound inside the iterator, and the walk is the R3 lever the why key leaves deliberately unpinned.
- **required** — *per language:*
  - `c` — the opcode is `c % 4`, so EVERY byte value is a legal opcode and no input is rejected for being malformed: `c % 4 == 0` in both C rungs.
  - `rust` — the opcode, `c % 4`, in all four Rust rungs -- spelled `c % 4 == 0` in R2, R4 and R5 and `match c % 4 {` in R3, which is the R3 lever.
- **required** — *per language:*
  - `c` — the payload byte is a function of the operand that created the object, in both C rungs: `(uint8_t)(a * 7u + 1u)`. So a READ that returns a recycled block's payload returns a value no honest read of this reference's own object could produce.
  - `rust` — the same payload, in all four Rust rungs, spelled with the wrapping operators the language forces: `a.wrapping_mul(7).wrapping_add(1)`.
- **required** — *per language:*
  - `c` — the fold is a serial Horner chain over `acc`, spelled with the literal multiplier, ONCE per operation: `acc = acc * 31 + v;` in both C rungs.
  - `rust` — the fold, in all four Rust rungs, spelled with the literal multiplier: `acc.wrapping_mul(31).wrapping_add(`.
- **required** — *per language:*
  - `c` — the NEW count is folded last, so a rung that created a different number of objects cannot produce the same checksum: `return acc * 31 + (uint64_t)nnew;` in both C rungs.
  - `rust` — the same, in all four Rust rungs: `acc.wrapping_mul(31).wrapping_add(nnew as u64)`.
- **FORBIDDEN** — `transmute`
- **FORBIDDEN** — `Weak<`
- **FORBIDDEN** — `Arc<`
- **FORBIDDEN** — `RefCell`
- **FORBIDDEN** — `Rc::get_mut`
- **FORBIDDEN** — `Rc::strong_count`
- **FORBIDDEN** — `Rc::try_unwrap`
- **FORBIDDEN** — `Box::into_raw`
- **FORBIDDEN** — `Box::leak`
- **FORBIDDEN** — `ManuallyDrop`
- **FORBIDDEN** — `mem::forget`
- **FORBIDDEN** — `Vec::with_capacity`
- **FORBIDDEN** — `calloc(`
- **FORBIDDEN** — `realloc(`
- **FORBIDDEN** — `memmove(`

> **Why**: POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ONE OMITTED SOURCE LINE, AND THE HARM LANDS AN UNBOUNDED DISTANCE AWAY FROM IT. `DUP` publishes a SECOND reference to the object on the top of the stack and R1 does not retain it, so every later release over-decrements: the object is freed while a live stack entry still names it, and the next use of that entry -- a release that reads `o->rc`, or a READ that reads `o->data[0]` -- touches a freed block. THE READ PATH IS CORRECT IN c/kernel.c AND ASKS NOTHING WRONG, AND THAT IS THE C-MECHANISM DISTINCTION THIS ROW RESTS ON. p27's, p29's and p32's stale use is a READ that failed to revalidate, and each is repaired by growing a conjunct on the read path; a refcounted pointer is valid BY CONSTRUCTION, so no test the READ could grow would repair p34 without becoming a liveness table. The free happens EARLY rather than the read happening LATE. ⚠⚠ THE ACQUIRE IS THE ONLY ZERO-COST REPAIR SITE, NOT THE ONLY REPAIR SITE, AND THAT IS MEASURED (TASK_155_REPORT M1, re-derived at TASK_156 in .temp/t156/csite/): a DESTROY-side repair that leaves DUP untouched and decides the free by scanning stk[0..ntop) for the object -- p28's repair site, an ownership test at the free -- matches R1h's checksum on 8/8 inputs and is ASan-clean where R1 fires, and costs +160.64 Ir/call (+7.28%) on small and +2403.83 (+21.64%) on large at -O3, +164.70 (+5.24%) and +2953.27 (+18.96%) at -O0. The cost grows with the INPUT and not with the optimisation level, because the scan is O(ntop) on EVERY release while the retain runs only on a DUP, which no benign input contains -- which is WHY the acquire is the idiomatic site, and pricing two repair sites is a better result than asserting one. p32 is the furthest thing from this row in the tree: it allocates nothing at all. THE SAFETY LINE IS `+1 / -0` PREPROCESSED LINES, THE SMALLEST IN THIS TREE, and controls/safety_line.py measures it on the two SHIPPED files with `cc -E -P` rather than asserting it. ⚠⚠ THERE IS NO BENIGN INPUT THAT EXECUTES THE SAFETY LINE, AND THAT IS PROVED RATHER THAN SEARCHED. `t->rc = t->rc + 1` is the ONLY increment in the kernel, so in R1 every object's `rc` is permanently 1; any executed DUP therefore leaves TWO stack entries naming a ONE-reference object, and the two releases that must follow -- each entry is released exactly once, by POP or by the epilogue -- go `1 -> 0` (*free*) and then `0 -> underflow`, reading `o->rc` out of a freed block. **So the R1-vs-R1h benign cost gradient is `0.00` BY CONSTRUCTION**, a statement about WHICH STATEMENTS EXECUTE and never about the NUMBER, and inputs/gen.py, model.py::no_dup_problems and controls/no_dup.py enforce the corollary mechanically: NO MATRIX INPUT MAY CONTAIN A DUP OP. ⚠ `0.00` IS STILL MEASURED AND NOT ASSUMED -- R1h is a different compiled function and a never-executed statement can still move layout, register allocation and inlining. ⚠⚠ AND THAT IS NOT HYPOTHETICAL: TASK_155 planted a DIFFERENT never-executed statement on the same dead DUP path and moved the -O3 cell by -14.22 Ir/call through layout alone, while a HOT plant moved it 34x, so the cell is neither a plumbing tautology nor a number the construction decides. *0.00 BY CONSTRUCTION, NOT BY MEASUREMENT* is WITHDRAWN (TASK_155_REPORT M2). NOTES.md 4 reports the measured R1-R1h delta at BOTH optimisation levels on BOTH compilers beside the prediction. TWO BUG CLASSES SEPARATED BY WHICH INSTRUMENT SEES THEM, AND THE PAIR IS THE ROW'S MOST INTERESTING EVIDENCE. On `DUP POP POP` and `DUP POP READ` the two rungs' checksums are BIT-IDENTICAL and ASan is the ONLY discriminator: the refcount header comes first and `data` starts at offset 16, clear of glibc's tcache `next`/`key` words at user offsets 0 and 8, so the stale read returns the RIGHT byte and the release path folds a constant that does not depend on `rc` or on whether `free` ran. On `DUP POP NEW READ` the next NEW RECYCLES the freed block and the checksum DIVERGES. Both are shipped, adversarial-blind / adversarial-blindread and adversarial-recycle, each `sanitizer_expect: fires`. THE LAYOUT IS DISCLOSED HERE THE WAY p28 DISCLOSES ITS OWN, and it is the idiomatic layout for a refcounted buffer rather than a layout chosen to hide the harm; `size_t rc; size_t len; uint8_t data[8];` is what SDS, PyBytesObject and GBytes all look like. UBSAN IS SILENT ON EVERY INPUT AT EVERY OPTIMISATION LEVEL ON BOTH COMPILERS, and that is derived rather than observed: R1's undefined behaviour is entirely TEMPORAL. Every index the kernel forms is inside `stk[]` in both rungs -- DUP reads `ntop - 1` under `ntop > 0`, POP reads `ntop` after decrementing it under `ntop > 0`, and READ's index is `a % ntop` under `ntop > 0` -- so there is no spatial violation for UBSan to see. A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN (RECAP trap 5), so controls/detectors.py ships one control per detector and the UBSan one is not an ASan one. THE STORAGE IS `malloc`/`free` PER OBJECT AND THAT IS THE PATTERN RATHER THAN A CHOICE: a reference count exists to decide WHEN TO FREE, and a slot that is never freed has nothing to decide. `.memory/01-ladder.md`'s law -- safe Rust's temporal guarantee is a guarantee about the ALLOCATOR, and a structure that recycles its own storage gets no guarantee at all -- is what makes the storage choice load-bearing, and controls/safe_arms.py measures BOTH branches of it in ONE ROW: the `Rc` port CANNOT REPRODUCE the bug (p28's shape) and an index-arena port REPRODUCES IT BIT FOR BIT (p32's shape), on the same inputs, in the same file. SAFE RUST HAS NO SITE FOR THE SAFETY LINE, AND THAT IS A FINDING AND NOT AN OMISSION. `Rc::clone` publishes the second reference and increments the count in ONE operation; there is no way to obtain a second `Rc<Obj>` without it -- and controls/safe_arms.py MEASURES that attribution rather than assuming it: replace arm_safe_rc_move.rs's whole DUP arm with the SENT fold the same file already writes when its guard fails, giving a program that CANNOT have p34's bug, and it COMPILES, so the E0507 is caused by the two edited lines. ⚠⚠ THE BORROW ROUTE IS CLOSED AT THE OWNER MUTATION AND NOT AT THE DUPLICATION, AND THE SENTENCE THAT SAID OTHERWISE IS WITHDRAWN (TASK_155_REPORT B1, landed TASK_156). Until TASK_156 this block read `a borrow cannot be stored in the stack array because the borrow checker ties it to the array it came from`, and that is FALSE: controls/arm_safe_rc_borrow_frozen.rs stores a SECOND `&Obj` into the stack array over a pre-built owner and compiles and runs. What safe Rust refuses is MUTATING THE OWNER while those borrows are live -- and a free IS an owner mutation -- so arm_safe_rc_borrow.rs's E0502 fires on the NEW path (the `objs.push` against the live `&objs[..]` borrows) and is IDENTICAL, at the IDENTICAL LINE, with the DUP body deleted; that arm measures WHERE the route closes, not that duplication is closed. ⚠ AND THE ERROR CODE CARRIES NO INFORMATION ABOUT REFERENCE COUNTING: 12-line programs with no `Rc`, no container and no count print the same E0507 and the same E0502. THIRD TIME THIS PROJECT HAS READ A rustc CODE AS DISTINGUISHING WHEN IT WAS NOT (p25's E0502, p28's E0382/E0499). c/kernel.c's bug is exactly the separation of *publish a reference* from *count it*, and safe Rust does not offer that separation IN A PROGRAM THAT ALSO DESTROYS THE OBJECT -- which is the precise form of the claim, because the frozen control shows the PUBLICATION alone is legal and it is the DESTRUCTION that the borrow checker stops. That is why `Rc<` is REQUIRED in R2 and R3 here and FORBIDDEN in p29 and p32: on those rows it would move the liveness decision into a library and delete the comparison, and on this row the library IS the comparison. WHAT THE R5 PROVES AND WHAT IT COSTS. A `PointsTo` is LINEAR and p34's subject is ALIASING -- two stack entries naming one object is the normal, correct state of this kernel -- so the permission cannot be held per stack entry the way p27 holds one per slot. It is keyed by OBJECT, and the proof carries the bridge: `perms[k].value().rc == cnt(ids, k)`, the count stored in the object's own first word equals the NUMBER OF STACK ENTRIES naming it. `cnt` is an occurrence count over a `Seq<int>` and it is the first multiset-flavoured obligation in this tree. ⚠⚠ LEAK-FREEDOM FALLS OUT AS A COROLLARY rather than as a second obligation: `obj_ok` requires `cnt(ids, k) > 0` for every key, and the epilogue runs until the stack is empty, so the permission map is EMPTY when the kernel returns -- `assert(perms.dom() =~= Set::empty())` is that statement. ⚠ What it does NOT say is that any rung's map must be empty: Verus does not force a tracked resource to be consumed, so a rung that dropped the map would verify. THE PINNED vstd HAS NO `Rc` SPECIFICATION AND THAT IS A RESULT, NOT A REASON TO SHRINK THE ROW: `~/tools/verus/vstd/std_specs/smart_ptrs.rs` is 78 lines with no `strong_count`, no `Rc::clone`, no `into_raw`/`from_raw` and no `increment_strong_count`, so an R5 must model the counter itself in a raw-pointer rung -- which is what the C rung does anyway. NOTES.md 6. THE LAYOUT FACT IS A `global layout` DIRECTIVE AND NOT AN AXIOM. `vstd::layout::size_of` is UNINTERPRETED for a user struct at the pinned vstd, so neither `rec_alloc`'s `size != 0` nor `PointsToRaw::into_typed`'s alignment precondition can be discharged without telling Verus the layout. `global layout Obj is size == 24, align == 8;` does that, and RUSTC CHECKS IT AT CODEGEN -- with a wrong number the file still verifies and then fails to compile with `evaluation panicked: does not have the expected size`, measured. It is the one layout fact in this tree the COMPILER rather than a reviewer is responsible for, and it is why this rung costs no extra trusted item. NOTES.md 6a. WHAT IS DELIBERATELY NOT PINNED is how R3 walks the op stream -- `chunks_exact(2).take(nops)` against R2's cursor, and `match c % 4` against R2's `if` chain -- exactly as p32 leaves its handle-register spelling unpinned and p14 leaves its fold loop. That is the R3 lever, it costs zero TCB, and NOTES.md 5 reports what it moves. ⚠ The consequence for the cursor-guard entry below is stated there rather than left implicit: R2, R4 and R5 write `if len - p < 2 {` and R3 does not write it at all, because the iterator carries the same bound. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p34-refcount-stack.json`, contract `329c786f99c8`.

`78` backticked spelling(s) over `6` rung(s) → **234** (spelling, rung) pair(s), **92** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 30 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 4 spelling(s) pin nothing**, 40 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - pins nothing — `+1 / -0` (required[0], c, 0 of 2 rungs)
  - pins nothing — `#[repr(C)] pub struct Obj` (required[1], rust, 0 of 4 rungs)
  - pins nothing — `Drop` (required[1], rust, 0 of 4 rungs)
  - pins nothing — `0 -> underflow` (required[3], c, 0 of 2 rungs)
  - absent — `t->rc = t->rc + 1;` (required[0], c, **c/kernel.c**)
  - absent — `obj_retain(t);` (required[0], rust, **safe_naive.rs**)
  - absent — `obj_retain(t);` (required[0], rust, **safe_tuned.rs**)
  - absent — `obj_retain(t);` (required[0], rust, **verus.rs**)
  - absent — `let t = arr_get_unchecked(&stk, ntop - 1);` (required[0], rust, **safe_naive.rs**)
  - absent — `let t = arr_get_unchecked(&stk, ntop - 1);` (required[0], rust, **safe_tuned.rs**)
  - absent — `pub rc: usize,` (required[1], rust, **safe_naive.rs**)
  - absent — `pub rc: usize,` (required[1], rust, **safe_tuned.rs**)
  - absent — `Rc` (required[1], rust, **unsafe.rs**)
  - absent — `Rc` (required[1], rust, **verus.rs**)
  - absent — `Rc::clone(` (required[1], rust, **unsafe.rs**)
  - absent — `Rc::clone(` (required[1], rust, **verus.rs**)
  - absent — `let n = obj_dec(q);` (required[2], rust, **safe_naive.rs**)
  - absent — `let n = obj_dec(q);` (required[2], rust, **safe_tuned.rs**)
  - absent — `let n = obj_dec(q);` (required[2], rust, **verus.rs**)
  - absent — `if n == 0 {` (required[2], rust, **safe_naive.rs**)
  - absent — `if n == 0 {` (required[2], rust, **safe_tuned.rs**)
  - absent — `obj_free(q);` (required[2], rust, **safe_naive.rs**)
  - absent — `obj_free(q);` (required[2], rust, **safe_tuned.rs**)
  - absent — `obj_free(q);` (required[2], rust, **verus.rs**)
  - absent — `[*mut Obj; CAP]` (required[3], rust, **safe_naive.rs**)
  - absent — `[*mut Obj; CAP]` (required[3], rust, **safe_tuned.rs**)
  - absent — `while ntop > 0 {` (required[3], rust, **safe_naive.rs**)
  - absent — `while ntop > 0 {` (required[3], rust, **safe_tuned.rs**)
  - absent — `[Option<Rc<Obj>>; CAP]` (required[3], rust, **unsafe.rs**)
  - absent — `[Option<Rc<Obj>>; CAP]` (required[3], rust, **verus.rs**)
  - absent — `std::alloc::alloc(layout)` (required[4], rust, **safe_naive.rs**)
  - absent — `std::alloc::alloc(layout)` (required[4], rust, **safe_tuned.rs**)
  - absent — `std::alloc::dealloc(p, layout);` (required[4], rust, **safe_naive.rs**)
  - absent — `std::alloc::dealloc(p, layout);` (required[4], rust, **safe_tuned.rs**)
  - absent — `Rc::new(` (required[4], rust, **unsafe.rs**)
  - absent — `Rc::new(` (required[4], rust, **verus.rs**)
  - absent — `if len - p < 2 {` (required[5], rust, **safe_tuned.rs**)
  - absent — `chunks_exact(2).take(nops)` (required[5], rust, **safe_naive.rs**)
  - absent — `chunks_exact(2).take(nops)` (required[5], rust, **unsafe.rs**)
  - absent — `chunks_exact(2).take(nops)` (required[5], rust, **verus.rs**)
  - absent — `c % 4 == 0` (required[6], rust, **safe_tuned.rs**)
  - absent — `match c % 4 {` (required[6], rust, **safe_naive.rs**)
  - absent — `match c % 4 {` (required[6], rust, **unsafe.rs**)
  - absent — `match c % 4 {` (required[6], rust, **verus.rs**)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## What the gate said out loud (reporting only)

From `results/gate/p34-refcount-stack.json` — the `loud` and `controls_json` keys, at contract `329c786f99c8`. **These did not fail the gate and are not defects**; they are the conditions `check.py` refuses to be silent about. Each one is a caveat on a number below or on the declaration above. The run's **verdict** is deliberately not printed here: it is an output of the same gate run that checks this table is current (stage `9c`), and rendering it made the table an input to its own checker — see `read_gate_loud`. Read the verdict from `results/gate/p34-refcount-stack.json`.

- **`collapse-ir`** — the derived floor is 166x below the tightest cell actually measured, so it rules out total collapse and essentially nothing else -- a cell could lose 99.40% of its work and still pass this stage. Read it as a smoke test, not as evidence that the work happened.
- **`tcb-unsafe`** — verus.rs:550 `arr_set_unchecked`'s `requires` constrains nothing about ['x'], which its trusted body uses. spec.md justifies it: `x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `T` is a legal thing to store in a `T` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` reads `i < N`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second, p06 the third, p14 the fourth, p27 the fifth, p29 the sixth, p32 the seventh, p35 the eighth and p34 the ninth.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 303 | 286 | 0 | 1,305 | 171,353,731 | 80,386,175 | 3,000,056 | 300,056 | `4e4380d1` | `4e4380d1` | yes | xmm |
| c-clang | 136 | 135 | 1 | 463 | 183,531,969 | 87,968,338 | 2,800,055 | 280,055 | `d2fb68a4` | `f81c48a0` | yes | - |
| safe_naive | 277 | 273 | 3 | 1,149 | 239,988,702 | 115,459,755 | 2,800,275 | 280,275 | `9589926d` | `8412c17f` | yes | xmm |
| safe_tuned | 237 | 234 | 6 | 1,018 | 194,705,899 | 92,260,716 | 2,800,275 | 280,275 | `3b6a4471` | `fb7a8279` | yes | xmm |
| unsafe | 180 | 179 | 10 | 678 | 185,367,394 | 87,680,915 | 2,800,275 | 280,275 | `e5e04e57` | `96a41f7b` | yes | xmm |
| verus | 180 | 179 | 10 | 678 | 185,367,394 | 87,680,915 | 2,800,270 | 280,270 | `b35427f5` | `4d791caa` | yes | xmm |
| c-gcc-h | 304 | 287 | 0 | 1,305 | 171,353,731 | 80,386,175 | 3,000,056 | 300,056 | `eeda05e0` | `eeda05e0` | yes | xmm |
| c-clang-h | 137 | 136 | 2 | 466 | 183,531,969 | 87,968,338 | 2,800,055 | 280,055 | `f83db4c4` | `e2e95668` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 219 | 218 | 0 | 1,162 | 325,624,819 | - | 7,200,066 | - | `e10bee29` | `e10bee29` | yes | - |
| c-clang | 203 | 203 | 2 | 1,076 | 337,827,734 | - | 4,200,052 | - | `7879a713` | `8a450911` | yes | - |
| safe_naive | 534 | 534 | 6 | 3,098 | 485,893,980 | - | 5,000,077 | - | `efe340e7` | `1cd6a3ed` | yes | - |
| safe_tuned | 565 | 565 | 12 | 3,252 | 476,733,188 | - | 5,000,077 | - | `e50d7a6a` | `0850a9fa` | yes | - |
| unsafe | 332 | 332 | 7 | 1,817 | 466,666,813 | - | 5,000,077 | - | `65fdee21` | `71e6bf08` | yes | - |
| verus | 332 | 332 | 7 | 1,817 | 466,666,813 | - | 5,000,056 | - | `83590df8` | `ea626e60` | yes | - |
| c-gcc-h | 224 | 223 | 0 | 1,190 | 325,624,819 | - | 7,200,066 | - | `ad313ea3` | `ad313ea3` | yes | - |
| c-clang-h | 208 | 208 | 0 | 1,104 | 337,827,734 | - | 4,200,052 | - | `43ad6c09` | `43ad6c09` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 547 | 541 | 2 | 2,340 | - | - | 165,258,184 | 77,478,786 | `d1ba14b4` | `2dacdd56` | yes | xmm |
| c-clang | 368 | 356 | 0 | 1,488 | - | - | 192,208,978 | 92,093,092 | `fe129aba` | `fe129aba` | yes | xmm |
| safe_naive | 921 | 910 | 1 | 4,319 | - | - | 249,788,986 | 120,280,039 | `36327070` | `215a6110` | yes | xmm |
| safe_tuned | 877 | 867 | 1 | 4,111 | - | - | 203,585,924 | 97,167,264 | `2a87f57d` | `b0913e94` | yes | xmm |
| unsafe | 818 | 806 | 1 | 3,743 | - | - | 210,210,565 | 99,931,306 | `a80a9acc` | `e121c394` | yes | xmm |
| verus | 820 | 807 | 1 | 3,759 | - | - | 209,081,578 | 99,632,508 | `1d647429` | `8e636f9a` | yes | xmm |
| c-gcc-h | 548 | 542 | 2 | 2,340 | - | - | 165,258,184 | 77,478,786 | `17e8f616` | `b9e7d85b` | yes | xmm |
| c-clang-h | 368 | 357 | 0 | 1,488 | - | - | 192,208,978 | 92,093,092 | `3a9e1ed4` | `3a9e1ed4` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 325,624,819 | - | 7,200,066 | - | `588192c0` | `588192c0` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 334,901,656 | - | 4,200,051 | - | `4d0f41d0` | `4d0f41d0` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 485,893,980 | - | 5,000,077 | - | `f39ebade` | `52f5ea4d` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 476,733,188 | - | 5,000,077 | - | `eeb5813f` | `4872d4e5` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 466,666,813 | - | 5,000,077 | - | `193f4f2a` | `4eaae3fb` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 466,666,813 | - | 5,000,056 | - | `d66c1992` | `9cd2b652` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 325,624,819 | - | 7,200,066 | - | `ce910bd6` | `ce910bd6` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 334,901,656 | - | 4,200,051 | - | `bede53b9` | `bede53b9` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 332/332 vs 332/332 | 7 B vs 7 B |
| unsafe vs verus | O3 | no | **yes** | no | 180/179 vs 180/179 | 10 B vs 10 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 31.03 | 31.51 | 1.6% | 40.68 | 41.26 | 1.4% |
| c-gcc | whole | 31.09 | 31.65 | 1.8% | 40.52 | 41.25 | 1.8% |
| c-clang | isolated | 32.35 | 32.92 | 1.8% | 43.11 | 44.34 | 2.9% |
| c-clang | whole | 32.89 | 33.31 | 1.3% | 43.61 | 45.13 | 3.5% |
| safe_naive | isolated | 35.22 | 35.82 | 1.7% | 55.84 | 56.88 | 1.9% |
| safe_naive | whole | 36.14 | 36.70 | 1.5% | 56.30 | 57.66 | 2.4% |
| safe_tuned | isolated | 34.19 | 34.66 | 1.4% | 52.50 | 53.54 | 2.0% |
| safe_tuned | whole | 33.61 | 33.98 | 1.1% | 52.05 | 53.26 | 2.3% |
| unsafe | isolated | 32.83 | 33.49 | 2.0% | 48.57 | 49.79 | 2.5% |
| unsafe | whole | 34.29 | 35.07 | 2.3% | 50.49 | 51.90 | 2.8% |
| verus | isolated | 32.70 | 33.13 | 1.3% | 48.38 | 49.45 | 2.2% |
| verus | whole | 34.39 | 34.88 | 1.4% | 50.49 | 51.64 | 2.3% |
| c-gcc-h | isolated | 31.07 | 31.57 | 1.6% | 40.65 | 41.15 | 1.2% |
| c-gcc-h | whole | 31.20 | 31.82 | 2.0% | 40.46 | 41.16 | 1.7% |
| c-clang-h | isolated | 32.46 | 33.00 | 1.7% | 43.24 | 44.43 | 2.8% |
| c-clang-h | whole | 33.11 | 33.36 | 0.8% | 43.16 | 44.82 | 3.8% |

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
