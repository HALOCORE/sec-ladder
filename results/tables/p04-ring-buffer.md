# p04-ring-buffer — results

Generated 2026-08-20T01:52:23Z from `results/p04-ring-buffer.json` (git `e8f3c733a26f`, working tree dirty).

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
| adversarial-count.bin | 8 | 212 | 212 | False | n_iters=8 stride=204 n_blob=204 nwin=1 calls=8 work/call=204B win0={'xpush': 0, 'dpush': 0, 'xpop': 0, 'epop': 0} r1_overwrites=False san=clean truncated=False expected=0 |
| adversarial-overwrite.bin | 8 | 1,012 | 1,012 | False | n_iters=8 stride=1004 n_blob=1004 nwin=1 calls=8 work/call=1004B win0={'xpush': 63, 'dpush': 137, 'xpop': 0, 'epop': 0} r1_overwrites=True san=clean truncated=False expected=61209146786944 |
| adversarial-wrap.bin | 8 | 2,612 | 2,612 | False | n_iters=8 stride=2604 n_blob=2604 nwin=1 calls=8 work/call=2604B win0={'xpush': 261, 'dpush': 0, 'xpop': 259, 'epop': 0} r1_overwrites=False san=clean truncated=False expected=1291274053164148224 |
| large.bin | 1,500 | 8,308,008 | 8,308,008 | False | n_iters=1500 stride=4154 n_blob=8308000 nwin=2000 calls=1500 work/call=4154B win0={'xpush': 417, 'dpush': 0, 'xpop': 413, 'epop': 0} r1_overwrites=False san=clean truncated=False expected=1112210447576272499 |
| small.bin | 6,000 | 14,276 | 14,276 | False | n_iters=6000 stride=1189 n_blob=14268 nwin=12 calls=6000 work/call=1189B win0={'xpush': 119, 'dpush': 0, 'xpop': 118, 'epop': 0} r1_overwrites=False san=clean truncated=False expected=4685270296466038691 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE EMPTINESS CHECK, present in every rung including R1: `if (head != tail) {` in both C rungs.
  - `rust` — THE EMPTINESS CHECK, present in every rung: `if head != tail {` in all four Rust rungs.
- **required** — *per language:*
  - `c` — THE FULLNESS CHECK: `if ((tail + 1) % RING_CAP != head) {` in c/kernel_hardened.c. c/kernel.c omits it and omits NOTHING ELSE, which IS the bug -- so the one scoped-absent pair this declaration reports is on that rung and is correct.
  - `rust` — THE FULLNESS CHECK: `if (tail + 1) % RING_CAP != head {` in all four Rust rungs.
- **required** — the write cursor is advanced MODULO the capacity, spelled with `%` and not with a mask, in all six rungs: `tail = (tail + 1) % RING_CAP;`
- **required** — and so is the read cursor, in all six rungs: `head = (head + 1) % RING_CAP;`
- **required** — *per language:*
  - `c` — the ring is a fixed-size LOCAL array, not a heap allocation and not growable: `uint64_t ring[RING_CAP];` in both C rungs.
  - `rust` — the ring is a fixed-size LOCAL array, never a growable one: `let mut ring: [u64; RING_CAP] = [0; RING_CAP];` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the declared count is bounded by the window before the loop, in 64-bit arithmetic, in EVERY rung: `if (5 * (uint64_t)nops > (uint64_t)(len - 4))` in both C rungs.
  - `rust` — the declared count is bounded by the window before the loop, in 64-bit arithmetic, in EVERY rung: `if 5 * (nops as u64) > (len - 4) as u64 {` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the per-operation dispatch is a REAL BRANCH on the attacker's op byte and not a branchless select: `if (op == 0) {` in both C rungs.
  - `rust` — the per-operation dispatch is a REAL BRANCH on the attacker's op byte and not a branchless select: `if op == 0 {` in all four Rust rungs.
- **required** — the little-endian u32 decodes are written out with + and * rather than | and <<, so they stay linear arithmetic: `+ 65536 *` in all six rungs.
- **required** — ...and their top bytes: `+ 16777216 *` in all six rungs.
- **required** — *per language:*
  - `c` — BOTH CURSORS and the declared count are folded into the result, so a rung that wrapped differently -- which is exactly what the missing fullness check produces -- cannot produce the same checksum: `((acc * 31 + (uint64_t)head) * 31 + (uint64_t)tail) * 31` in both C rungs.
  - `rust` — BOTH CURSORS and the declared count are folded into the result, so a rung that wrapped differently cannot produce the same checksum: `.wrapping_add(head as u64).wrapping_mul(31)`, `.wrapping_add(tail as u64).wrapping_mul(31)` and `.wrapping_add(nops as u64)` in all four Rust rungs.
- **FORBIDDEN** — `& (RING_CAP - 1)`
- **FORBIDDEN** — `from_le_bytes`
- **FORBIDDEN** — `MaybeUninit`
- **FORBIDDEN** — `VecDeque`
- **FORBIDDEN** — `.push_back(`
- **FORBIDDEN** — `.pop_front(`

> **Why**: each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). THE INDEX IS MODULAR AND THE OPERATOR IS `%`: p05 asked whether the optimiser carries a bound through a MULTIPLY and p09 through a SHIFT; p04 asks through `%`, so `(tail + 1) % RING_CAP` and `(head + 1) % RING_CAP` are pinned literally in all six rungs and `& (RING_CAP - 1)` is `forbidden`. THE EXCLUSION MOVES NO MACHINE CODE AND THE DECLARATION SAYS SO: at `RING_CAP = 64` the masked spelling is BYTE-IDENTICAL to the `%` one (NOTES.md 1, `md5_fn_norel` equal, `n_fn` equal), so forbidding it removes nothing from the admissible class and protects no number -- it is forbidden because a mask ANSWERS A DIFFERENT QUESTION, which is the one p09 already answered. The same is true the other way at `RING_CAP = 60`, where `%` is a magic-number division and a mask is not even semantically available; `controls/gen_controls.py` builds that rung as a CONTROL and NOTES.md 1a reports it, because it is the largest single effect in this pattern and it must not be mistaken for a rung. BOTH GUARDS ARE THE PROGRAM: `if head != tail` on the pop and `if (tail + 1) % RING_CAP != head` on the push are not bounds checks a compiler inserted, they are the kernel's semantics, and exactly one of them -- the push's -- is absent from `c/kernel.c` and present everywhere else. That single scoped-absent pair IS the bug, and it is the one this declaration exists to report. `adversarial-wrap.bin` and `adversarial-count.bin` are the controls that make it a measurement rather than a claim about the source: they attack the modular arithmetic and the length check, both of which R1 HAS, and all eight cells agree on both. THE BUG STAYS IN BOUNDS, which is why the emptiness check being in every rung matters more here than p03's push guard did: with both cursors reduced mod `RING_CAP` every index either rung forms is in `[0, RING_CAP)` on every input, so `adversarial-overwrite.bin` is a CHECKSUM row and not a sanitiser row, and NOTES.md 6 measures that the memory-safety half of the R5 proof discharges the mutant that deletes the check. BOTH CURSORS ARE FOLDED INTO THE RESULT, and that is what makes the bug visible at all: a rung that wrapped differently ends with different `head` and `tail`, so `((acc*31 + head)*31 + tail)*31 + nops` cannot collide with the right answer -- measured before the rungs were written, 2153 against R1's 448 on `adversarial-overwrite.bin` window 0, and IDENTICAL on all 12 `small` and all 2000 `large` windows, which is the p12 interaction checked in the direction p12 learned it the hard way in. THE PER-OPERATION DISPATCH IS A REAL BRANCH: `if op == 0` is pinned literally because a rung that lowered it to a branchless select would be measuring a different kernel, and because p07 measured LLVM's X86CmovConverterPass doing the OPPOSITE transformation unasked, so this is a thing to check on the disassembly (NOTES.md 1) rather than to assume. THE RING IS A FIXED-SIZE LOCAL ARRAY: `uint64_t ring[RING_CAP]` / `[u64; RING_CAP]`. A `VecDeque` with `.push_back(`/`.pop_front(` moves the pattern to allocator behaviour, which is p02's axis and not this one, and it deletes the two explicit cursors that the result folds and that the proof's invariant is about -- so both method names and the type are `forbidden`. `MaybeUninit` is forbidden for a reason that runs the other way and is worth stating because it makes the Rust rungs DEARER: all four write `[0u64; RING_CAP]` since safe Rust has no uninitialised array, and C's is not initialised, so that per-call memset is a LANGUAGE difference which NOTES.md 3c prices separately -- letting the unsafe rung alone skip it would open an R4-vs-R3 gap that is not a safety gap and that no safe rung could close. `from_le_bytes` deletes the written-out little-endian decode every rung shares AND is NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW), so a rung using it would compare a safe cell against an unsafe cell that cannot exist -- the `identity`-pin trap this block's own `identity` key sets. WHAT IS DELIBERATELY *NOT* PINNED, and it is the point of the pattern: **the ACCESS spelling**. R2 and R3 index `ring[tail]`, R4 and R5 call `get_unchecked`, and holding those fixed would hold fixed the one thing p04 exists to compare -- and on this pattern the answer is that the two compile to the same bytes (NOTES.md 1). Nor is the opcode-stream cursor pinned: `w[4 + 5*k]` and `w[4..4 + 5*nops].chunks_exact(5)` are both in contract and NOTES.md 10a measures both, which is what makes the R3-side span a search rather than an assertion. WHEN THIS DECLARATION WAS WRITTEN, stated exactly because the ordering is what the direction test needs: it was written AFTER the phase-0 probes of NOTES.md 0 and BEFORE any rung existed. What was known when it was written is the whole of NOTES.md 0 -- that the safe and unsafe ring accesses are byte-identical at `RING_CAP = 64` and differ by 12 static instructions at 60, that p03's `m_clamp` control deletes the 60 check, that the memory-safety-only proof discharges the missing fullness check against five positive controls, and that the two cursors folded into the result separate R1 from the checked rungs on the adversarial window and on no matrix window. What was NOT known is any figure in NOTES.md 3, 4, 10 or 11, because no rung, no input file and no `model.py` existed yet. TASK_042 required those probes before five rungs were built on them, so this is a consequence of the task and not a choice; recording it is the only honest thing available, and `.memory/01-ladder.md`'s direction test is what a reviewer should apply to every entry above. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p04-ring-buffer.json`, contract `d0766c2f9136`.

`36` backticked spelling(s) over `6` rung(s) → **110** (spelling, rung) pair(s), **73** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 12 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 0 spelling(s) pin nothing**, 1 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - absent — `if ((tail + 1) % RING_CAP != head) {` (required[1], c, **c/kernel.c**)
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
| c-gcc | 83 | 81 | 0 | 313 | 23,052,000 | 20,004,000 | 90,056 | 22,556 | `c797ecb2` | `c797ecb2` | yes | - |
| c-clang | 56 | 54 | 1 | 184 | 17,232,000 | 14,968,500 | 84,059 | 21,059 | `83ca4dce` | `cfe89500` | yes | - |
| safe_naive | 132 | 131 | 2 | 526 | 48,714,000 | 42,417,000 | 84,275 | 21,275 | `777f3b3a` | `0dd946be` | yes | - |
| safe_tuned | 84 | 82 | 9 | 279 | 20,208,000 | 17,500,500 | 84,275 | 21,275 | `caefd9c5` | `abe69d82` | yes | - |
| unsafe | 74 | 72 | 15 | 241 | 20,178,000 | 17,493,000 | 84,275 | 21,275 | `c0573f69` | `1be59947` | yes | - |
| verus | 74 | 72 | 15 | 241 | 20,178,000 | 17,493,000 | 78,274 | 19,774 | `c0573f69` | `1be59947` | yes | - |
| c-gcc-h | 87 | 85 | 0 | 329 | 25,908,000 | 22,506,000 | 90,056 | 22,556 | `9ff16d9d` | `9ff16d9d` | yes | - |
| c-clang-h | 59 | 57 | 1 | 203 | 19,380,000 | 16,851,000 | 84,059 | 21,059 | `468db147` | `5d2e38bb` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 183 | 183 | 0 | 858 | 115,674,000 | - | 216,066 | - | `dd346fc9` | `dd346fc9` | yes | - |
| c-clang | 125 | 125 | 1 | 622 | 84,204,000 | - | 126,056 | - | `901d0349` | `bd26271c` | yes | - |
| safe_naive | 259 | 259 | 11 | 1,429 | 138,456,000 | - | 150,077 | - | `2a76fdfa` | `416d26c6` | yes | - |
| safe_tuned | 270 | 270 | 9 | 1,479 | 124,308,000 | - | 150,077 | - | `20b9bc35` | `e1e4ea0a` | yes | - |
| unsafe | 197 | 197 | 4 | 988 | 129,192,000 | - | 150,077 | - | `bb75b483` | `f0ff2f9c` | yes | - |
| verus | 197 | 197 | 4 | 988 | 129,192,000 | - | 150,056 | - | `6f202429` | `fdeaea60` | yes | - |
| c-gcc-h | 188 | 188 | 0 | 881 | 119,244,000 | - | 216,066 | - | `2ea506af` | `2ea506af` | yes | - |
| c-clang-h | 130 | 130 | 1 | 646 | 87,774,000 | - | 126,056 | - | `62d45685` | `de106a08` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 229 | 228 | 1 | 923 | 23,028,000 | 19,998,000 | 90,127 | 22,627 | `ae370922` | `bf5995c5` | yes | - |
| c-clang | 279 | 275 | 0 | 1,078 | - | - | 20,112,179 | 17,467,679 | `a57048de` | `a57048de` | yes | xmm |
| safe_naive | 779 | 770 | 1 | 3,551 | - | - | 57,318,279 | 49,927,779 | `0f213ff2` | `7b77d0a8` | yes | xmm |
| safe_tuned | 713 | 704 | 1 | 3,231 | - | - | 21,648,282 | 18,750,282 | `c4e025c8` | `44d17e41` | yes | xmm |
| unsafe | 719 | 713 | 1 | 3,247 | - | - | 33,768,284 | 29,374,784 | `74099ab2` | `7ea0fc49` | yes | xmm |
| verus | 724 | 716 | 1 | 3,231 | - | - | 33,774,278 | 29,376,278 | `9c47d921` | `253ef8c2` | yes | xmm |
| c-gcc-h | 229 | 228 | 1 | 923 | 25,170,000 | 21,874,500 | 90,127 | 22,627 | `ae370922` | `bf5995c5` | yes | - |
| c-clang-h | 282 | 278 | 0 | 1,110 | - | - | 22,266,178 | 19,351,678 | `664f253b` | `664f253b` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 115,674,000 | - | 216,066 | - | `d7420744` | `d7420744` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 84,204,000 | - | 126,055 | - | `ac8b0145` | `ac8b0145` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 138,456,000 | - | 150,077 | - | `8b346fd0` | `b3d54a5f` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 124,308,000 | - | 150,077 | - | `51d696d7` | `e9b24848` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 129,192,000 | - | 150,077 | - | `bf5ef4d5` | `122fdac7` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 129,192,000 | - | 150,056 | - | `fc8a90fb` | `cc35e4c8` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 119,244,000 | - | 216,066 | - | `2cc5fff7` | `2cc5fff7` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 87,774,000 | - | 126,055 | - | `be4661ef` | `be4661ef` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 197/197 vs 197/197 | 4 B vs 4 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 74/72 vs 74/72 | 15 B vs 15 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 31 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 12.13 | 12.31 | 1.5% | 4.94 | 5.44 | 10.0% |
| c-gcc | whole | 12.10 | 12.33 | 1.9% | 5.01 | 5.44 | 8.6% |
| c-clang | isolated | 12.03 | 12.21 | 1.6% | 6.43 | 6.91 | 7.5% |
| c-clang | whole | 12.47 | 12.76 | 2.3% | 6.16 | 6.93 | **12.5% ✗** |
| safe_naive | isolated | 13.42 | 13.65 | 1.7% | 7.03 | 7.75 | **10.3% ✗** |
| safe_naive | whole | 14.71 | 14.85 | 1.0% | 7.59 | 8.20 | 8.1% |
| safe_tuned | isolated | 12.28 | 12.56 | 2.3% | 5.38 | 5.91 | 9.8% |
| safe_tuned | whole | 12.56 | 12.76 | 1.6% | 5.69 | 6.13 | 7.9% |
| unsafe | isolated | 12.27 | 12.49 | 1.9% | 5.37 | 5.72 | 6.6% |
| unsafe | whole | 13.40 | 13.62 | 1.6% | 6.42 | 6.90 | 7.6% |
| verus | isolated | 12.27 | 12.51 | 2.0% | 5.36 | 5.98 | **11.5% ✗** |
| verus | whole | 13.31 | 13.56 | 1.8% | 6.66 | 7.08 | 6.3% |
| c-gcc-h | isolated | 12.12 | 12.35 | 1.9% | 5.07 | 5.60 | **10.4% ✗** |
| c-gcc-h | whole | 12.20 | 12.41 | 1.7% | 5.87 | 6.26 | 6.7% |
| c-clang-h | isolated | 12.09 | 12.32 | 1.9% | 6.87 | 7.48 | 8.9% |
| c-clang-h | whole | 12.57 | 12.74 | 1.4% | 6.02 | 6.65 | **10.6% ✗** |

**5 of 32 wall-clock cells exceed the 10% min-to-median spread threshold and are DISCARDED** per `.memory/03-measurement.md` step 4. They are printed above marked ✗ rather than deleted, because a missing cell that looks like an omission is worse than a documented failure (`.memory/02-bench-rules.md`). **No claim in this report rests on a marked row.**

- `c-clang / whole` on `small.bin`: spread 12.5%
- `safe_naive / isolated` on `small.bin`: spread 10.3%
- `verus / isolated` on `small.bin`: spread 11.5%
- `c-gcc-h / isolated` on `small.bin`: spread 10.4%
- `c-clang-h / whole` on `small.bin`: spread 10.6%


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
