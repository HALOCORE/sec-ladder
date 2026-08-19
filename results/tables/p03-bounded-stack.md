# p03-bounded-stack — results

Generated 2026-08-19T18:57:24Z from `results/p03-bounded-stack.json` (git `7e4ff0b8e75a`, working tree dirty).

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
| adversarial-allpop.bin | 8 | 1,012 | 1,012 | False | n_iters=8 stride=1004 n_blob=1004 nwin=1 calls=8 work/call=1004B win0_xpops=0 san=fires truncated=False expected=5685940249600 |
| adversarial-count.bin | 8 | 212 | 212 | False | n_iters=8 stride=204 n_blob=204 nwin=1 calls=8 work/call=204B win0_xpops=0 san=clean truncated=False expected=0 |
| adversarial-overflow.bin | 8 | 812 | 812 | False | n_iters=8 stride=804 n_blob=804 nwin=1 calls=8 work/call=804B win0_xpops=64 san=clean truncated=False expected=2401459682193218816 |
| adversarial-underflow.bin | 8 | 212 | 212 | False | n_iters=8 stride=204 n_blob=204 nwin=1 calls=8 work/call=204B win0_xpops=11 san=fires truncated=False expected=7473563764999086208 |
| large.bin | 1,500 | 8,308,008 | 8,308,008 | False | n_iters=1500 stride=4154 n_blob=8308000 nwin=2000 calls=1500 work/call=4154B win0_xpops=207 san=clean truncated=False expected=12657562225574543262 |
| small.bin | 6,000 | 14,276 | 14,276 | False | n_iters=6000 stride=1189 n_blob=14268 nwin=12 calls=6000 work/call=1189B win0_xpops=118 san=clean truncated=False expected=4507875919703971017 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE PUSH GUARD, present in every rung including R1: `if (sp < STACK_CAP) {` in both C rungs.
  - `rust` — THE PUSH GUARD, present in every rung: `if sp < STACK_CAP {` in all four Rust rungs.
- **required** — *per language:*
  - `c` — THE POP GUARD: `if (sp > 0) {` in c/kernel_hardened.c. c/kernel.c omits it and omits NOTHING ELSE, which IS the bug -- so the one scoped-absent pair this declaration reports is on that rung and is correct.
  - `rust` — THE POP GUARD: `if sp > 0 {` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the stack is a fixed-size LOCAL array, not a heap allocation and not growable: `uint64_t stack[STACK_CAP];` in both C rungs.
  - `rust` — the stack is a fixed-size LOCAL array, never a growable one: `let mut stack: [u64; STACK_CAP] = [0; STACK_CAP];` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the declared count is bounded by the window before the loop, in 64-bit arithmetic, in EVERY rung: `if (5 * (uint64_t)nops > (uint64_t)(len - 4))` in both C rungs.
  - `rust` — the declared count is bounded by the window before the loop, in 64-bit arithmetic, in EVERY rung: `if 5 * (nops as u64) > (len - 4) as u64 {` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the per-operation dispatch is a REAL BRANCH on the attacker's op byte and not a branchless select: `if (op == 0) {` in both C rungs.
  - `rust` — the per-operation dispatch is a REAL BRANCH on the attacker's op byte and not a branchless select: `if op == 0 {` in all four Rust rungs.
- **required** — the stack pointer is decremented BEFORE the slot is read, so that every read is of the slot the pointer names and no rung indexes one below it: `sp = sp - 1;` in all six rungs.
- **required** — and incremented AFTER the slot is written: `sp = sp + 1;` in all six rungs.
- **required** — the little-endian u32 decodes are written out with + and * rather than | and <<, so they stay linear arithmetic: `+ 65536 *` in all six rungs.
- **required** — ...and their top bytes: `+ 16777216 *` in all six rungs.
- **required** — *per language:*
  - `c` — the final stack depth and the declared count are both folded into the result, so a rung that ended at a different depth or ran a different number of operations cannot produce the same checksum: `(acc * 31 + (uint64_t)sp) * 31 + (uint64_t)nops` in both C rungs.
  - `rust` — the final stack depth and the declared count are both folded into the result, so a rung that ended at a different depth or ran a different number of operations cannot produce the same checksum: `.wrapping_add(sp as u64).wrapping_mul(31)` and `.wrapping_add(nops as u64)` in all four Rust rungs.
- **FORBIDDEN** — `from_le_bytes`
- **FORBIDDEN** — `& (STACK_CAP - 1)`
- **FORBIDDEN** — `MaybeUninit`
- **FORBIDDEN** — `.push(`
- **FORBIDDEN** — `.pop(`

> **Why**: each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). THE OPERATION SEQUENCE IS IN THE FILE, AND BOTH GUARDS ARE THE PROGRAM: `if sp < STACK_CAP` on the push and `if sp > 0` on the pop are not bounds checks a compiler inserted, they are the kernel's semantics, and exactly one of them -- the pop's -- is absent from `c/kernel.c` and present everywhere else. That single scoped-absent pair IS the bug, and it is the one this declaration exists to report. `adversarial-overflow.bin` and `adversarial-count.bin` are the controls that make it a measurement rather than a claim about the source: they attack the push guard and the length check, both of which R1 HAS, and all eight cells agree on both. THE PER-OPERATION DISPATCH IS A REAL BRANCH: `if op == 0` is pinned literally because a rung that lowered it to a branchless select would delete the branch-predictability axis `sweep-bpred`/`sweep-brand` exist for, and because p07 measured LLVM's X86CmovConverterPass doing the OPPOSITE transformation unasked, so this is a thing to check on the disassembly (NOTES.md 1) rather than to assume. THE STACK IS A FIXED-SIZE LOCAL ARRAY: `[u64; STACK_CAP]` / `uint64_t stack[STACK_CAP]`. A `Vec` with `.push(`/`.pop(` moves the pattern to allocator behaviour, which is p02's axis and not this one, and it deletes the explicit `sp` that the result folds and that the proof's invariant is about -- so both method names are `forbidden`. MASKING IS FORBIDDEN: `stack[sp & (STACK_CAP - 1)]` removes 1.00000 of the surviving check's 3.00000 Ir (NOTES.md 4d) and is not the same program, because it silently turns an out-of-range access into an in-range one, which is the opposite of what this pattern models. `MaybeUninit` is forbidden for a reason that runs the other way and is worth stating because it makes the Rust rungs DEARER: all four write `[0u64; STACK_CAP]` since safe Rust has no uninitialised array, and C's is not initialised, so that per-call memset is a LANGUAGE difference which NOTES.md 3c prices separately -- letting the unsafe rung alone skip it would open an R4-vs-R3 gap that is not a safety gap and that no safe rung could close. `from_le_bytes` deletes the written-out little-endian decode every rung shares AND is NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW), so a rung using it would compare a safe cell against an unsafe cell that cannot exist -- the `identity`-pin trap this block's own `identity` key sets. WHAT IS DELIBERATELY *NOT* PINNED, and it is the point of the pattern: **the ACCESS spelling**. R2 and R3 index `stack[sp]`, R4 and R5 call `get_unchecked`, and holding those fixed would hold fixed the one thing p03 exists to compare. Nor is the opcode-stream cursor pinned: `w[4 + 5*k]` and `w[4..4 + 5*nops].chunks_exact(5)` are both in contract and NOTES.md 10a measures both, which is what makes the R3-side span a search rather than an assertion. WHEN THIS DECLARATION WAS WRITTEN, stated exactly because p11's could claim something stronger and p03's cannot: it was written AFTER the phase-0 probe of NOTES.md 0 and BEFORE any rung existed. What was known when it was written is the whole of NOTES.md 0 -- the underflow's address arithmetic, that STACK_CAP=64 keeps the array real, that a 5-byte op dominates the per-call constant, and probe figures for six candidate spellings including 3.00000 Ir per executed pop. What was NOT known is any figure in NOTES.md 3, 4, 10 or 11, because no rung, no input file and no `model.py` existed yet. TASK_036 required that probe before five rungs were built on the sizes, so this is a consequence of the task and not a choice; recording it is the only honest thing available, and `.memory/01-ladder.md`'s direction test is what a reviewer should apply to every entry above. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p03-bounded-stack.json`, contract `c51288b0c9f6`.

`31` backticked spelling(s) over `6` rung(s) → **94** (spelling, rung) pair(s), **63** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 10 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 0 spelling(s) pin nothing**, 1 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - absent — `if (sp > 0) {` (required[1], c, **c/kernel.c**)
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
| c-gcc | 74 | 72 | 0 | 297 | 21,600,000 | 14,896,500 | 90,056 | 22,556 | `29e14fb4` | `29e14fb4` | yes | - |
| c-clang | 46 | 45 | 0 | 160 | 15,798,000 | 11,622,000 | 84,059 | 21,059 | `1df68371` | `1df68371` | yes | - |
| safe_naive | 131 | 129 | 3 | 541 | 48,672,000 | 38,431,500 | 84,275 | 21,275 | `f73287f3` | `dda72632` | yes | - |
| safe_tuned | 82 | 80 | 10 | 278 | 20,166,000 | 13,515,000 | 84,275 | 21,275 | `a5a47dba` | `91a3b081` | yes | - |
| unsafe | 66 | 64 | 2 | 206 | 18,012,000 | 12,576,000 | 84,275 | 21,275 | `52432361` | `1a9c2380` | yes | - |
| verus | 66 | 64 | 2 | 206 | 18,012,000 | 12,576,000 | 78,274 | 19,774 | `52432361` | `1a9c2380` | yes | - |
| c-gcc-h | 76 | 74 | 0 | 297 | 23,016,000 | 15,517,500 | 90,056 | 22,556 | `12fbe4a2` | `12fbe4a2` | yes | - |
| c-clang-h | 51 | 49 | 1 | 183 | 17,214,000 | 12,243,000 | 84,059 | 21,059 | `8a0024bd` | `37a3d082` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 169 | 169 | 0 | 791 | 110,670,000 | - | 216,066 | - | `5a5e7607` | `5a5e7607` | yes | - |
| c-clang | 118 | 118 | 1 | 584 | 81,360,000 | - | 126,056 | - | `086bed57` | `5017ca0c` | yes | - |
| safe_naive | 250 | 250 | 5 | 1,387 | 134,166,000 | - | 150,077 | - | `ee2b8e8b` | `ce9a92a2` | yes | - |
| safe_tuned | 261 | 261 | 8 | 1,416 | 120,018,000 | - | 150,077 | - | `fdc32e2a` | `edd13ccf` | yes | - |
| unsafe | 188 | 188 | 15 | 945 | 124,902,000 | - | 150,077 | - | `c4d02fc3` | `3b22b961` | yes | - |
| verus | 188 | 188 | 15 | 945 | 124,902,000 | - | 150,056 | - | `0c372b3e` | `3ede7bb8` | yes | - |
| c-gcc-h | 171 | 171 | 0 | 801 | 112,086,000 | - | 216,066 | - | `292a65dc` | `292a65dc` | yes | - |
| c-clang-h | 121 | 121 | 2 | 596 | 83,484,000 | - | 126,056 | - | `12ab1f53` | `ad2d959d` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 229 | 228 | 1 | 923 | 21,588,000 | 14,893,500 | 90,127 | 22,627 | `ae370922` | `bf5995c5` | yes | - |
| c-clang | 265 | 263 | 0 | 1,014 | - | - | 17,256,177 | 12,876,177 | `5ed6b0a8` | `5ed6b0a8` | yes | xmm |
| safe_naive | 786 | 777 | 1 | 3,599 | - | - | 53,010,282 | 40,017,282 | `ab0ca503` | `b9bfa4c9` | yes | xmm |
| safe_tuned | 712 | 704 | 1 | 3,215 | - | - | 21,594,278 | 14,761,778 | `d8e3ba46` | `c70c6ffa` | yes | xmm |
| unsafe | 705 | 698 | 1 | 3,215 | - | - | 30,156,284 | 20,355,284 | `3f6718f0` | `75d06a99` | yes | xmm |
| verus | 709 | 701 | 1 | 3,183 | - | - | 30,156,278 | 20,355,278 | `471a7bae` | `b7e07f87` | yes | xmm |
| c-gcc-h | 229 | 228 | 1 | 923 | 23,004,000 | 15,514,500 | 90,127 | 22,627 | `ae370922` | `bf5995c5` | yes | - |
| c-clang-h | 271 | 267 | 0 | 1,046 | - | - | 19,380,177 | 13,807,677 | `aeff4857` | `aeff4857` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 110,670,000 | - | 216,066 | - | `9e6aa388` | `9e6aa388` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 81,360,000 | - | 126,055 | - | `87686ecb` | `87686ecb` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 134,166,000 | - | 150,077 | - | `17e7411f` | `4d953275` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 120,018,000 | - | 150,077 | - | `5a0453b3` | `9e0859f1` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 124,902,000 | - | 150,077 | - | `190a3e3d` | `7f089687` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 124,902,000 | - | 150,056 | - | `fc8a90fb` | `cc35e4c8` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 112,086,000 | - | 216,066 | - | `41cdd4f2` | `41cdd4f2` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 83,484,000 | - | 126,055 | - | `7e826a0a` | `7e826a0a` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 188/188 vs 188/188 | 15 B vs 15 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 66/64 vs 66/64 | 2 B vs 2 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 8.76 | 8.89 | 1.5% | 5.00 | 5.41 | 8.3% |
| c-gcc | whole | 8.73 | 8.93 | 2.3% | 5.19 | 5.59 | 7.5% |
| c-clang | isolated | 8.53 | 8.69 | 1.8% | 4.71 | 5.04 | 7.0% |
| c-clang | whole | 8.84 | 9.01 | 2.0% | 5.42 | 5.79 | 6.8% |
| safe_naive | isolated | 10.08 | 10.25 | 1.7% | 8.00 | 8.54 | 6.7% |
| safe_naive | whole | 10.28 | 10.47 | 1.8% | 8.46 | 9.27 | 9.5% |
| safe_tuned | isolated | 8.98 | 9.13 | 1.7% | 5.90 | 6.56 | **11.2% ✗** |
| safe_tuned | whole | 8.98 | 9.14 | 1.8% | 5.98 | 6.38 | 6.5% |
| unsafe | isolated | 9.13 | 9.32 | 2.1% | 6.51 | 7.11 | 9.2% |
| unsafe | whole | 9.29 | 9.47 | 1.9% | 6.07 | 6.52 | 7.4% |
| verus | isolated | 9.08 | 9.27 | 2.1% | 6.34 | 6.93 | 9.3% |
| verus | whole | 9.24 | 9.45 | 2.3% | 5.93 | 6.45 | 8.8% |
| c-gcc-h | isolated | 8.67 | 8.88 | 2.5% | 4.93 | 5.27 | 7.0% |
| c-gcc-h | whole | 8.79 | 8.96 | 2.0% | 5.04 | 5.37 | 6.5% |
| c-clang-h | isolated | 8.79 | 8.94 | 1.8% | 6.53 | 7.03 | 7.6% |
| c-clang-h | whole | 8.75 | 8.90 | 1.6% | 5.93 | 6.41 | 8.2% |

**1 of 32 wall-clock cells exceed the 10% min-to-median spread threshold and are DISCARDED** per `.memory/03-measurement.md` step 4. They are printed above marked ✗ rather than deleted, because a missing cell that looks like an omission is worse than a documented failure (`.memory/02-bench-rules.md`). **No claim in this report rests on a marked row.**

- `safe_tuned / isolated` on `small.bin`: spread 11.2%


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
