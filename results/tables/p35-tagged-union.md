# p35-tagged-union — results

Generated 2026-08-31T09:29:45Z from `results/p35-tagged-union.json` (git `9a91e8240025`, working tree dirty).

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
| adversarial-dbl-confusion.bin | 40 | 26 | 26 | False | n_iters=40 stride=18 n_blob=18 nwin=1 calls=40 work/call=18B san=clean confusions=[3] truncated=False expected=1278623759085878912 |
| adversarial-exhaust.bin | 40 | 68 | 68 | False | n_iters=40 stride=60 n_blob=60 nwin=1 calls=40 work/call=60B san=clean confusions=[3] truncated=False expected=10548210477984644096 |
| adversarial-ptr-confusion.bin | 40 | 26 | 26 | False | n_iters=40 stride=18 n_blob=18 nwin=1 calls=40 work/call=18B san=fires confusions=[2] truncated=False expected=6265551365163105920 |
| adversarial-ptr-deep.bin | 40 | 74 | 74 | False | n_iters=40 stride=66 n_blob=66 nwin=1 calls=40 work/call=66B san=fires confusions=[2] truncated=False expected=7846389847459590144 |
| adversarial-stride3.bin | 200 | 60 | 60 | False | n_iters=200 stride=3 n_blob=52 nwin=0 calls=0 work/call=0B san=clean confusions=[] truncated=False expected=0 |
| degenerate.bin | 200 | 44 | 44 | False | n_iters=200 stride=12 n_blob=36 nwin=3 calls=200 work/call=12B san=clean confusions=[] truncated=False expected=3452235395457817106 |
| large.bin | 200 | 15,624 | 15,624 | False | n_iters=200 stride=244 n_blob=15616 nwin=64 calls=200 work/call=244B san=clean confusions=[] truncated=False expected=3733036646187536480 |
| small.bin | 200 | 424 | 424 | False | n_iters=200 stride=52 n_blob=416 nwin=8 calls=200 work/call=52B san=clean confusions=[] truncated=False expected=751388249273516652 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE CELL IS A TAG PLUS A UNION, in both C rungs and in c/kernel.h: `uint8_t tag;` beside `union {`, `uint64_t i;`, `double d;`, `uint8_t *p;`. This is the representation the whole pattern is about -- eight bytes with no record of which member was last stored, and a tag that is the only claim about them.
  - `rust` — the same representation in R4 and R5: `union Pay {` with `i: u64`, `d: f64` and `o: u32`; and the SAFE ANSWER to it in R2 and R3, `enum Cell {` with `Int(u64)`, `Ptr(u32)` and `Dbl(f64)`. ⚠ The union's third member is the arena OFFSET where C's is a POINTER -- see the why key, which is where that substitution is argued and measured.
- **required** — *per language:*
  - `c` — THE SAFETY LINE. In c/kernel_hardened.c the tag store sits INSIDE the budget test, after the payload store: `cells[idx].u.p = &arena[P35_BUDGET - navail];` immediately followed by `cells[idx].tag = P35_T_PTR;`. c/kernel.c spells the SAME two statements in the OTHER ORDER and differs in nothing else. ⚠ **A text pin cannot express an ORDERING**, so both rungs contain both tokens and this entry pins the STATEMENTS, not the sequence; ../controls/safety_line.py preprocesses the two shipped files and measures the sequence (`+2 / -2` lines, a pure reorder at both sites). That division of labour is stated rather than left implicit.
  - `rust` — the same ordering, written by hand, in R4 and R5 only: `pay_set_unchecked(&mut pays, idx, Pay { o: (BUDGET - navail) as u32 });` immediately followed by `arr_set_unchecked(&mut tags, idx, T_PTR);`, inside `if navail > 0 {`. ⚠⚠ **R2 and R3 have NO SITE for this line and that is the row's safe-Rust result, not an omission**: `cells[idx] = Cell::Ptr((BUDGET - navail) as u32);` writes the discriminant and the payload as ONE value, so the two cannot come apart. See the why key.
- **required** — *per language:*
  - `c` — THE TAG IS PUBLISHED ONLY BY A STORE, NEVER CLEARED, in both C rungs. Nothing writes `cells[idx].tag` except the three SET arms, and a cell nothing has written keeps tag 0 and folds `P35_SENT`. That is what keeps p35's bug from being `read uninitialised` -- see the why key.
  - `rust` — the same in all four Rust rungs: the `T_UNSET` / `Cell::Unset` arm folds `SENT`.
- **required** — *per language:*
  - `c` — A FAILED STORE IS STILL ACCOUNTED FOR: the `else` arm folds `P35_SENT` in both C rungs, so the fold's length is a function of the op count alone and the bug is never `the fold lost an operation`.
  - `rust` — the same `SENT` arm in all four Rust rungs.
- **required** — *per language:*
  - `c` — THE BUDGET IS DECREMENTED ONLY BY A STORE THAT HAPPENED: `navail--;` inside the `if (navail > 0)` in both C rungs, so both return the same trailing term.
  - `rust` — the same, in all four Rust rungs: `navail = navail - 1;`.
- **required** — *per language:*
  - `c` — the cell index is `a % P35_CELLS`, so EVERY operand byte names a cell and no input is rejected for being malformed: `idx = (size_t)(a % P35_CELLS);` in both C rungs.
  - `rust` — the same, in all four Rust rungs: `(a % CELLS as u8) as usize`.
- **required** — *per language:*
  - `c` — the opcode is `c % 4`, so EVERY byte value is a legal opcode: `c % 4 == 0` in both C rungs.
  - `rust` — the opcode, in all four Rust rungs. ⚠ R3 spells it `match c % 4 {` rather than as a chain of `if`s, which is the R3 lever and is deliberately not pinned to one spelling -- see the why key.
- **required** — *per language:*
  - `c` — the fold is a serial Horner chain over `acc`, spelled with the literal multiplier, ONCE per operation: `acc = acc * 31 + ` in both C rungs.
  - `rust` — the fold, in all four Rust rungs, spelled with the literal multiplier: `acc.wrapping_mul(31).wrapping_add(`.
- **required** — *per language:*
  - `c` — the remaining budget is folded last, so a rung that served a different number of stores cannot produce the same checksum: `return acc * 31 + (uint64_t)navail;` in both C rungs.
  - `rust` — the same, in all four Rust rungs: `acc.wrapping_mul(31).wrapping_add(navail as u64)`.
- **required** — *per language:*
  - `c` — THE DBL PAYLOAD IS TWO LITERALS AND NOT `(double)a + 0.5`, in both C rungs: `(a % 2 == 0) ? 0.25 : 2.5`. This is a MEASUREMENT and not a preference -- see the why key.
  - `rust` — the same two literals in all four Rust rungs: `if a % 2 == 0 { 0.25 } else { 2.5 }` in R2/R3 and `Pay { d: 0.25 }` / `Pay { d: 2.5 }` in R4/R5.
- **FORBIDDEN** — `transmute`
- **FORBIDDEN** — `from_bits`
- **FORBIDDEN** — `to_bits`
- **FORBIDDEN** — `read_unaligned`
- **FORBIDDEN** — `align_to`
- **FORBIDDEN** — `memcpy(`
- **FORBIDDEN** — `malloc(`
- **FORBIDDEN** — `calloc(`
- **FORBIDDEN** — `realloc(`
- **FORBIDDEN** — `free(`
- **FORBIDDEN** — `std::alloc::`
- **FORBIDDEN** — `vstd::raw_ptr::`
- **FORBIDDEN** — `Box::new`
- **FORBIDDEN** — `Box::into_raw`
- **FORBIDDEN** — `ManuallyDrop`
- **FORBIDDEN** — `mem::forget`
- **FORBIDDEN** — `Rc<`
- **FORBIDDEN** — `RefCell`
- **FORBIDDEN** — `Vec::with_capacity`

> **Why**: POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ONE STATEMENT ORDERING CARRIES TWO BUG CLASSES SELECTED BY THE INPUT, AND THAT IS THE ROW. When the budget is exhausted, `c/kernel.c` publishes a tag whose payload never landed; a GET then reads the union AT THE CLAIMED TYPE. tag PTR over an int payload DEREFERENCES AN ATTACKER-DERIVED INTEGER -- SIGSEGV, exit 139, and ASan reports it. tag DBL over an int payload compares a GARBAGE DOUBLE and produces a SILENT WRONG VALUE that NOTHING reports: not ASan, not UBSan, not gcc or clang at -Wall -Wextra, and not Miri on the Rust reproduction. Which harm the input gets is chosen by which opcode the failing store carries, and the ordering is the same one. THE SAFETY LINE IS A SEQUENCING CONSTRAINT AND THAT IS A THIRD SHAPE FOR THIS TREE: p27's is a CONJUNCT, p13's is a STORE, p35's is an ORDER. The preprocessed diff between the two shipped C files is `+2 / -2` lines and a PURE REORDER at both sites, measured by controls/safety_line.py rather than asserted -- nothing is added, no test is introduced, no load and no branch. ⚠⚠ THIS SENTENCE IS CORRECTED AFTER MEASURING AND THE ORIGINAL IS STRUCK RATHER THAN QUIETLY REPLACED (PROTOCOL rule 6's added step; p46's defect, caught here by the author before shipping). It read: ~~the R1-vs-R1h cost of this pattern's safety is a SCHEDULING difference and nothing more, which is why NOTES.md 4 reports it as a per-call figure with its own noise floor rather than as a headline~~. MEASURED, R1h is CHEAPER than R1 on ALL SIXTEEN cells -- 2 compilers x 2 opt levels x 2 inline modes x 2 inputs -- and the mechanism is NOT scheduling: c/kernel.c performs the tag store on the FAILURE path too, 32.90 times per call on large.bin and 3.67 on small.bin over the MARGINAL window the figure is per (calls 100..199; .temp/t153/failed_stores_t153.py, which reproduces both published checksums). ⚠⚠ A SECOND CLAUSE OF THIS SENTENCE IS RETRACTED AT TASK_153 AND THE ORIGINAL IS STRUCK RATHER THAN DELETED (TASK_152 M2). It read: ~~-13.71 to -215.86 Ir/call, four figures, every one of them outside the coin-flip band results/synthesis.md publishes~~. THAT IS FALSE OF ONE OF THE FOUR: |-13.71| = 13.71 sits INSIDE the 2.00 ... 16.00 band that document labels *a coin flip -- do not quote alone*. SO SAY WHICH BAND EACH FIGURE IS IN RATHER THAN ASSERTING A BLANKET: at -O3, -85.91, -40.40 and -215.86 are in the >= 16.00 band (*every one is real*) and -13.71 alone is in the coin-flip band; at -O0, where the build report took no figure at all, the delta is -18.35 on small and -164.50 on large, IDENTICAL on gcc and clang and in both inline modes, and all eight are in the >= 16.00 band. ⚠ The band is calibrated on the DERIVED environment-block correction column, so it is a borrowed yardstick even where it is satisfied; the direction, 16 of 16, is the part that does not depend on it. ✅✅ AND THE `MECHANISM OPEN` HEDGE IS RETIRED. It read ~~what NOTES.md 4 marks OPEN is the MECHANISM, because the implied per-store cost is 2.62 Ir on gcc/large against 3.74 on gcc/small and is therefore not stable~~; 32.76 was the wrong denominator (the mean over all 200 calls, where marginal Ir is per calls 100..199). With 32.90 the mechanism CLOSES at -O0: EXACTLY 5.0000 Ir per failed tag store on ALL EIGHT -O0 cells, both compilers, both modes, and the ratio 164.50/18.35 equals 32.9000/3.6700 to six decimals independently of the constant. ✅ AND IT IS CLOSED AT THE INSTRUCTION LEVEL TOO, NOT ONLY ARITHMETICALLY: `harness/asm.py diff` on the two -O0 kernels moves a FIVE-INSTRUCTION block and nothing else, on BOTH compilers, and the static count is identical either side -- gcc `mov/shl/add/sub/movb`, clang `mov/lea/shl/add/movb` (.temp/t153/asm_O0_gcc.diff, .temp/t153/asm_O0_clang.diff). So the safety line is BETTER THAN FREE and NOTES.md 4 reports it as a headline; what remains OPEN is only -O3, where the optimiser restructures around the removed store and the implied constant spans 2.61 to 11.01. NOTHING IS ALLOCATED, FREED, RECYCLED OR ALIASED IN ANY RUNG, AND THE ROW IS NOT TEMPORAL. The cells and the arena are locals whose extent is a compile-time constant. p35 was carried in TASK_143's temporal re-adjudication list only because its old refusal was VERUS-side; the axis is TYPE, and this is the tree's second type row. THE NEAREST BUILT ROWS AND WHY THIS DUPLICATES NEITHER: p19 is a state machine with no union and no reinterpretation of one object's bytes at a second type; p16's variant selector bounds a LENGTH rather than choosing a TYPE; and p38 -- the other TYPE row -- turns on C99 6.5p7 EFFECTIVE TYPE and its harm is a MISCOMPILE, while p35 executes NO aliasing violation at all. Reading a union member other than the one last stored is DEFINED in C99 6.2.6.1p7 and 6.5.2.3, and the shipped kernels are built `-fstrict-aliasing` in the sanitizer stage without a word from either compiler. p38's answer was that Rust has NO type-based aliasing rule for `unsafe` to unlock; p35's is the opposite and that is why it is a row -- Rust DOES have a correct-variant rule for unions, `unsafe` IS required to break it, and Verus checks it NATIVELY. THE C UNION HOLDS A POINTER AND THE FOUR RUST RUNGS HOLD THE ARENA OFFSET, DISCLOSED HERE BECAUSE IT IS THE ONE PLACE THE RUNGS ARE NOT ISOMORPHIC. `.memory/01-ladder.md`'s own rule decides it: a rung covered by an `identity` pin is CHAINED TO THE PROVER, this pattern pins `identity: unsafe == verus`, and R5 cannot hold a `*const u8` and dereference it without `vstd::raw_ptr`'s `PointsTo` machinery -- which is p27's and p29's row and would put an allocation proof inside a type-confusion pattern. `*p` and `arena[o]` name the same byte, so every checksum agrees on every input including the adversarial ones; what the substitution changes is the addressing mode, and -- the part that matters and is stated rather than buried -- IT CHANGES THE CLASS OF THE LOUD HARM AND THEREFORE WHICH INSTRUMENT REPORTS IT. ⚠⚠ THIS SENTENCE IS ALSO CORRECTED AFTER MEASURING, ORIGINAL LEFT VISIBLE: it read ~~IT REMOVES THE LOUD HARM FROM THE RUST SIDE ENTIRELY~~, and controls/rust_bug.py refutes the natural reading of that -- the unsafe arm DIES ON A SIGNAL on adversarial-ptr-confusion and adversarial-ptr-deep, as c/kernel.c does. ⚠⚠ AND THIS CLAUSE IS ITSELF CORRECTED AT TASK_170, ORIGINAL LEFT VISIBLE: it read ~~rc=-11, exactly as c/kernel.c does~~, and that is ONE DRAW quoted as a constant. The arm's signal is STOCHASTIC -- 33/40 and 38/40 SIGSEGV over 40 draws per input at TASK_170, 37/40 and 38/40 at TASK_168, SIGBUS the rest -- while c/kernel.c is 40/40 SIGSEGV, and controls/rust_bug.json has shipped rc=-7 with unsafe_reproduces_c false on adversarial-ptr-confusion. THE MECHANISM IS THIS PARAGRAPH'S OWN SUBSTITUTION AND THAT IS WHY THE CORRECTION BELONGS IN THE FENCE: C dereferences an attacker-derived INTEGER, which faults at the same address every run, while the Rust arm indexes an arena-relative OFFSET whose faulting address moves with ASLR, so which signal the kernel delivers is a draw. controls/rust_bug.py ASSERTS the invariant rather than the sample -- every draw dies on a signal, every signal is SIGSEGV or SIGBUS, C is 40/40, and the SIGSEGV share clears a stated floor of 0.50 -- because until TASK_170 it RECORDED unsafe_reproduces_c and never CHECKED it, which is .memory/03-measurement.md entry 19's family. QUOTE THE MECHANISM AND THE FLOOR, NEVER THE COUNTS: the shares move between sessions, which is the result. What changes is the CLASS: an offset read at the wrong type is a WRONG INDEX and not a WILD POINTER, so the Rust arm's crash is an out-of-bounds `get_unchecked` that MIRI REPORTS as Undefined Behaviour -- where Miri says nothing at all about the union read itself -- and the safe arm turns the same step into a PANIC. The CWE-822 dereference-of-an-attacker-derived-integer does not survive into any Rust rung; a crash does. That is why `vstd::raw_ptr::`, `malloc(`, `free(`, `std::alloc::` and `Box::new` are forbidden: a rung that allocated would be measuring a different pattern. THE DBL PAYLOAD IS TWO LITERALS RATHER THAN `(double)a + 0.5`, AND THAT IS A MEASUREMENT. At the pinned Verus/vstd, `f64` ARITHMETIC carries an `add_req` precondition nothing discharges (vstd/std_specs/ops.rs) and `u8 as f64` is specified as a *(possibly) non-deterministic Rust cast* (vstd/float.rs), while an `f64` LITERAL verifies -- four probes, .temp/t148/verus/probe3.rs and probe4.rs, NOTES.md 6c. Every rung spells the same conditional, so no rung is disadvantaged, and the confusion is still detectable: the correct value is `2.5 > 1.0` for an odd operand and the confused one is a subnormal that is not. `from_bits` AND `to_bits` ARE FORBIDDEN FOR A SHARPER REASON THAN TIDINESS: they are safe Rust's TOTAL reinterpretation -- every bit pattern is a valid `f64` -- so a rung spelling them would delete the correct-variant obligation altogether and the pattern with it, while looking like the same algorithm. `transmute`, `read_unaligned` and `align_to` are forbidden as the other routes to the same deletion, and `memcpy(` because copying the payload out is a third. WHAT IS DELIBERATELY NOT PINNED is how R3 walks the op stream -- `chunks_exact(2).take(nops)` against R2's cursor -- exactly as p32 leaves its handle-register spelling unpinned and p14 leaves its fold loop. That is the R3 lever, it costs zero TCB, and NOTES.md 3 reports what it moves. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p35-tagged-union.json`, contract `9ad1219ef1d9`.

`88` backticked spelling(s) over `6` rung(s) → **264** (spelling, rung) pair(s), **97** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 38 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 9 spelling(s) pin nothing**, 35 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - pins nothing — `uint8_t tag;` (required[0], c, 0 of 2 rungs)
  - pins nothing — `union {` (required[0], c, 0 of 2 rungs)
  - pins nothing — `uint64_t i;` (required[0], c, 0 of 2 rungs)
  - pins nothing — `double d;` (required[0], c, 0 of 2 rungs)
  - pins nothing — `uint8_t *p;` (required[0], c, 0 of 2 rungs)
  - pins nothing — `+2 / -2` (required[1], c, 0 of 2 rungs)
  - pins nothing — `read uninitialised` (required[2], c, 0 of 2 rungs)
  - pins nothing — `the fold lost an operation` (required[3], c, 0 of 2 rungs)
  - pins nothing — `(double)a + 0.5` (required[9], c, 0 of 2 rungs)
  - absent — `union Pay {` (required[0], rust, **safe_naive.rs**)
  - absent — `union Pay {` (required[0], rust, **safe_tuned.rs**)
  - absent — `i: u64` (required[0], rust, **safe_naive.rs**)
  - absent — `i: u64` (required[0], rust, **safe_tuned.rs**)
  - absent — `d: f64` (required[0], rust, **safe_naive.rs**)
  - absent — `d: f64` (required[0], rust, **safe_tuned.rs**)
  - absent — `o: u32` (required[0], rust, **safe_naive.rs**)
  - absent — `o: u32` (required[0], rust, **safe_tuned.rs**)
  - absent — `enum Cell {` (required[0], rust, **unsafe.rs**)
  - absent — `enum Cell {` (required[0], rust, **verus.rs**)
  - absent — `Int(u64)` (required[0], rust, **unsafe.rs**)
  - absent — `Int(u64)` (required[0], rust, **verus.rs**)
  - absent — `Ptr(u32)` (required[0], rust, **unsafe.rs**)
  - absent — `Ptr(u32)` (required[0], rust, **verus.rs**)
  - absent — `Dbl(f64)` (required[0], rust, **unsafe.rs**)
  - absent — `Dbl(f64)` (required[0], rust, **verus.rs**)
  - absent — `pay_set_unchecked(&mut pays, idx, Pay { o: (BUDGET - navail) as u32 });` (required[1], rust, **safe_naive.rs**)
  - absent — `pay_set_unchecked(&mut pays, idx, Pay { o: (BUDGET - navail) as u32 });` (required[1], rust, **safe_tuned.rs**)
  - absent — `arr_set_unchecked(&mut tags, idx, T_PTR);` (required[1], rust, **safe_naive.rs**)
  - absent — `arr_set_unchecked(&mut tags, idx, T_PTR);` (required[1], rust, **safe_tuned.rs**)
  - absent — `cells[idx] = Cell::Ptr((BUDGET - navail) as u32);` (required[1], rust, **unsafe.rs**)
  - absent — `cells[idx] = Cell::Ptr((BUDGET - navail) as u32);` (required[1], rust, **verus.rs**)
  - absent — `T_UNSET` (required[2], rust, **safe_naive.rs**)
  - absent — `T_UNSET` (required[2], rust, **safe_tuned.rs**)
  - absent — `Cell::Unset` (required[2], rust, **unsafe.rs**)
  - absent — `Cell::Unset` (required[2], rust, **verus.rs**)
  - absent — `match c % 4 {` (required[6], rust, **safe_naive.rs**)
  - absent — `match c % 4 {` (required[6], rust, **unsafe.rs**)
  - absent — `match c % 4 {` (required[6], rust, **verus.rs**)
  - absent — `if a % 2 == 0 { 0.25 } else { 2.5 }` (required[9], rust, **unsafe.rs**)
  - absent — `if a % 2 == 0 { 0.25 } else { 2.5 }` (required[9], rust, **verus.rs**)
  - absent — `Pay { d: 0.25 }` (required[9], rust, **safe_naive.rs**)
  - absent — `Pay { d: 0.25 }` (required[9], rust, **safe_tuned.rs**)
  - absent — `Pay { d: 2.5 }` (required[9], rust, **safe_naive.rs**)
  - absent — `Pay { d: 2.5 }` (required[9], rust, **safe_tuned.rs**)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## What the gate said out loud (reporting only)

From `results/gate/p35-tagged-union.json` — the `loud` and `controls_json` keys, at contract `9ad1219ef1d9`. **These did not fail the gate and are not defects**; they are the conditions `check.py` refuses to be silent about. Each one is a caveat on a number below or on the declaration above. The run's **verdict** is deliberately not printed here: it is an output of the same gate run that checks this table is current (stage `9c`), and rendering it made the table an input to its own checker — see `read_gate_loud`. Read the verdict from `results/gate/p35-tagged-union.json`.

- **`tcb-unsafe`** — verus.rs:404 `arr_set_unchecked`'s `requires` constrains nothing about ['x'], which its trusted body uses. spec.md justifies it: `x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for. The `requires` constrains `i`, which is the only parameter the unchecked operation depends on. This is the false positive of the parameter-coverage rule and it is the same one p32 and p38 declare.
- **`tcb-unsafe`** — verus.rs:431 `pay_set_unchecked`'s `requires` constrains nothing about ['x'], which its trusted body uses. spec.md justifies it: `x` is a pure VALUE parameter, exactly as for arr_set_unchecked -- a whole `Pay` value moved into the slot. ⚠ Note what is NOT unsafe here: WRITING a union member is safe Rust, so the only unchecked operation in this body is the INDEX, and `i < old(v)@.len()` is the whole of what licenses it. That is why this item, unlike the three readers, HAS a verified twin.
- **`twin`** — verus.rs:482 trusted item `pay_i` has NO verified twin `slb_twin_pay_i`. spec.md justifies it: THERE IS NO SAFE RUST SPELLING OF A UNION READ. `v.get_unchecked(i).i` and `v[i].i` are BOTH `error[E0133]: access to union field is unsafe`, and `_TWIN_BANNED` forbids `unsafe` in a twin, so no `slb_twin_pay_i` can exist -- this is a fact about the LANGUAGE, not about this pattern's spelling. ⚠⚠ AND THE CONFIGURATION THAT WOULD NOT NEED A TWIN IS THE STRONGER ONE AND THE GATE REFUSES IT: Verus supports `union` NATIVELY, so the same read left in VERIFIED code is checked at the operation (`requirement not met: to access this field, the union must be in the correct variant`) -- but `_scan_unsafe_sites` requires every `unsafe` token to sit inside an `#[verifier::external_body]` body, which is exactly what turns the checked read into an axiom. controls/union_oracle.py runs both configurations with a must-fail arm on each. ⚠ What is NOT unchecked here: the `requires` `v@[i as int] is i` is verified AT EVERY CALL SITE, so the tag/variant agreement is proved; controls/proof_mutants.py arm M1 deletes the tag test and Verus reports `precondition not satisfied`. ⚠⚠ WHAT THE AXIOM ASSERTS -- CORRECTED AT TASK_153, ORIGINAL STRUCK (TASK_152 M5). This entry ended ~~What the axiom asserts is only that this body reads the member its name says~~, and that names ONE of TWO unchecked operations. `unsafe { v.get_unchecked(i).i }` is an unchecked INDEX and a union FIELD READ, and the axiom asserts BOTH: that the member read is the one this item's name says, AND that `i < v@.len()` is the whole of what licenses get_unchecked. Neither clause's STRENGTH is tested for this item, which is what its BLOCKED row says. ⚠ A NARROWER CONFIGURATION C EXISTS, IS GATE-LEGAL AND IS NOT SHIPPED: split the index into `fn pay_ref(v, i) -> &Pay` -- which DOES have a safe twin, `&v[i]`, and verifies -- and axiomatise only the bare field read; that is the split pay_set_unchecked already uses on the WRITE side. Measured at .temp/t152/verus/c4_split.rs: `2 verified, 0 errors` shipped and `3 verified, 0 errors` with the twin, and the real check._scan_unsafe_sites returns 0 failures on it. It does NOT reduce `blocked` -- the three readers still have no twin -- and it adds a TENTH trusted item, so p35 keeps nine and states the axiom's true width here instead. NOTES.md 6a records the choice. ⚠⚠ AND THE `requires` ITSELF IS DELETABLE WITHOUT THE PROOF NOTICING: controls/proof_mutants.py arm X1 strikes `v@[i as int] is {i,o,d}` from all three readers and the file still reports `16 verified, 0 errors` at the pinned count; only this spec.md item pin catches it, while configuration B FAILS AT THE READ.
- **`twin`** — verus.rs:494 trusted item `pay_o` has NO verified twin `slb_twin_pay_o`. spec.md justifies it: Same as pay_i, for the `o: u32` member. `error[E0133]` for every safe spelling; the `requires` `v@[i as int] is o` is checked at every call site; controls/union_oracle.py measures the refused configuration. The axiom is the same WIDTH as pay_i's -- the unchecked index AND the field read, not the field read alone (TASK_153, TASK_152 M5) -- and arm X1 applies to this item too.
- **`twin`** — verus.rs:511 trusted item `pay_d_gt1` has NO verified twin `slb_twin_pay_d_gt1`. spec.md justifies it: Same as pay_i, for the `d: f64` member, PLUS a second axiom this one alone carries: that the exec comparison `d > 1.0f64` agrees with the spec function `dbl_gt1`. ⚠ At the pinned vstd that link cannot be proved -- `f64` comparison is specified through `partial_cmp`'s existential and its arithmetic through an undischargeable `add_req` (.temp/t148/verus/probe3.rs). A twin would fail on the SECOND axiom even if the union read were safe, so this item is doubly untwinnable and the two reasons are independent. NOTES.md 6c. ⚠ COUNTED PROPERLY THIS ITEM AXIOMATISES THREE THINGS AND NOT TWO (TASK_153, TASK_152 M5): the unchecked INDEX, the union FIELD READ, and the exec-versus-spec comparison. Arm X1 applies to this item too.
- **`twin`** — stage 5c-twin ran but certified 4 twin(s) for 7 trusted item(s), with 3 justified away (['verus.rs:pay_d_gt1', 'verus.rs:pay_i', 'verus.rs:pay_o']). No strength claim is being made about the justified ones.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 139 | 133 | 0 | 591 | 140,232 | 619,620 | 3,056 | 3,056 | `364a1576` | `364a1576` | yes | xmm |
| c-clang | 142 | 137 | 1 | 534 | 152,124 | 713,706 | 2,859 | 2,859 | `ccae6ba0` | `ca36600c` | yes | xmm |
| safe_naive | 180 | 176 | 10 | 742 | 170,726 | 786,144 | 3,075 | 3,075 | `d430a7f8` | `df7320f5` | yes | xmm |
| safe_tuned | 141 | 138 | 2 | 622 | 134,208 | 608,923 | 3,075 | 3,075 | `be72f892` | `6bd36e00` | yes | xmm |
| unsafe | 112 | 112 | 13 | 435 | 139,509 | 643,034 | 3,075 | 3,075 | `6beb2748` | `102675d3` | yes | xmm |
| verus | 112 | 112 | 13 | 435 | 139,509 | 643,034 | 2,874 | 2,874 | `6beb2748` | `102675d3` | yes | xmm |
| c-gcc-h | 137 | 131 | 0 | 591 | 137,496 | 602,517 | 3,056 | 3,056 | `e18452bd` | `e18452bd` | yes | xmm |
| c-clang-h | 142 | 137 | 1 | 569 | 144,096 | 670,493 | 2,859 | 2,859 | `23504bb9` | `f4dffa2c` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 293 | 292 | 0 | 1,374 | 308,071 | - | 7,266 | - | `4e2a02f6` | `4e2a02f6` | yes | xmm |
| c-clang | 257 | 257 | 2 | 1,284 | 339,801 | - | 4,256 | - | `288e094b` | `ad77b685` | yes | xmm |
| safe_naive | 366 | 366 | 6 | 2,026 | 384,437 | - | 5,077 | - | `3b2b3211` | `70590c86` | yes | xmm |
| safe_tuned | 399 | 399 | 0 | 2,160 | 366,005 | - | 5,077 | - | `54d70742` | `54d70742` | yes | xmm |
| unsafe | 329 | 329 | 8 | 1,848 | 373,477 | - | 5,077 | - | `704e6f5d` | `a0841234` | yes | xmm |
| verus | 329 | 329 | 8 | 1,848 | 373,477 | - | 5,056 | - | `cd014e57` | `e6347379` | yes | xmm |
| c-gcc-h | 293 | 292 | 0 | 1,374 | 304,401 | - | 7,266 | - | `66bbee26` | `66bbee26` | yes | xmm |
| c-clang-h | 257 | 257 | 2 | 1,284 | 336,131 | - | 4,256 | - | `bbaf7929` | `112eb753` | yes | xmm |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 351 | 349 | 1 | 1,467 | - | - | 143,504 | 628,534 | `30894b3c` | `5ec6cb6d` | yes | xmm |
| c-clang | 354 | 348 | 0 | 1,441 | - | - | 157,664 | 738,439 | `d76fdc4e` | `d76fdc4e` | yes | xmm |
| safe_naive | 821 | 811 | 1 | 3,839 | - | - | 177,843 | 826,047 | `35f0bc3a` | `688f4815` | yes | xmm |
| safe_tuned | 771 | 761 | 1 | 3,631 | - | - | 138,732 | 632,633 | `a747e81b` | `6fff69d1` | yes | xmm |
| unsafe | 746 | 735 | 1 | 3,359 | - | - | 148,992 | 682,945 | `4cc569af` | `a4080be1` | yes | xmm |
| verus | 763 | 752 | 1 | 3,375 | - | - | 150,757 | 690,338 | `35d83078` | `3b9f7365` | yes | xmm |
| c-gcc-h | 349 | 347 | 2 | 1,460 | - | - | 140,768 | 611,431 | `8a74d50a` | `ba37ad31` | yes | xmm |
| c-clang-h | 367 | 363 | 0 | 1,473 | - | - | 145,916 | 678,648 | `4a1ae8ec` | `4a1ae8ec` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 308,071 | - | 7,266 | - | `3ba36934` | `3ba36934` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 336,113 | - | 4,255 | - | `a46d146d` | `a46d146d` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 384,437 | - | 5,077 | - | `ee891385` | `5af2ab15` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 366,005 | - | 5,077 | - | `b70051e3` | `f04840c6` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 373,477 | - | 5,077 | - | `d7f1b5f4` | `13ba4346` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 373,477 | - | 5,056 | - | `605209a4` | `c48a6eb8` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 304,401 | - | 7,266 | - | `3ba36934` | `3ba36934` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 332,443 | - | 4,255 | - | `a46d146d` | `a46d146d` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 329/329 vs 329/329 | 8 B vs 8 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 112/112 vs 112/112 | 13 B vs 13 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 4.80 | 4.89 | 1.7% | 4.08 | 4.16 | 2.1% |
| c-gcc | whole | 4.73 | 4.87 | 2.9% | 4.06 | 4.17 | 2.6% |
| c-clang | isolated | 4.85 | 5.02 | 3.6% | 3.89 | 4.19 | 7.8% |
| c-clang | whole | 4.93 | 5.04 | 2.3% | 4.06 | 4.19 | 3.3% |
| safe_naive | isolated | 5.48 | 5.59 | 1.9% | 4.61 | 4.73 | 2.7% |
| safe_naive | whole | 5.48 | 5.62 | 2.5% | 4.63 | 4.71 | 1.7% |
| safe_tuned | isolated | 5.16 | 5.55 | 7.5% | 4.59 | 4.74 | 3.3% |
| safe_tuned | whole | 5.23 | 5.61 | 7.3% | 4.62 | 4.74 | 2.5% |
| unsafe | isolated | 5.13 | 5.55 | 8.0% | 4.55 | 4.72 | 3.7% |
| unsafe | whole | 4.54 | 5.52 | **21.6% ✗** | 4.56 | 4.70 | 3.2% |
| verus | isolated | 4.53 | 5.54 | **22.1% ✗** | 4.42 | 4.70 | 6.5% |
| verus | whole | 4.88 | 5.55 | **13.8% ✗** | 4.60 | 4.73 | 2.8% |
| c-gcc-h | isolated | 4.40 | 4.89 | **11.0% ✗** | 4.08 | 4.20 | 2.9% |
| c-gcc-h | whole | 4.58 | 4.86 | 6.0% | 4.07 | 4.19 | 3.1% |
| c-clang-h | isolated | 4.31 | 5.09 | **18.1% ✗** | 4.08 | 4.19 | 2.9% |
| c-clang-h | whole | 4.85 | 5.01 | 3.2% | 4.10 | 4.20 | 2.3% |

**5 of 32 wall-clock cells exceed the 10% min-to-median spread threshold and are DISCARDED** per `.memory/03-measurement.md` step 4. They are printed above marked ✗ rather than deleted, because a missing cell that looks like an omission is worse than a documented failure (`.memory/02-bench-rules.md`). **No claim in this report rests on a marked row.**

- `unsafe / whole` on `large.bin`: spread 21.6%
- `verus / isolated` on `large.bin`: spread 22.1%
- `verus / whole` on `large.bin`: spread 13.8%
- `c-gcc-h / isolated` on `large.bin`: spread 11.0%
- `c-clang-h / isolated` on `large.bin`: spread 18.1%


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 6 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `degenerate.bin`
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `degenerate.bin`
- `O0 / whole` on `large.bin`
- `O3 / isolated` on `degenerate.bin`
- `O3 / whole` on `degenerate.bin`
