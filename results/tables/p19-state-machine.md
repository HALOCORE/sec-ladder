# p19-state-machine — results

Generated 2026-08-25T04:28:28Z from `results/p19-state-machine.json` (git `6e52208fc1cf`, working tree dirty).

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
| adversarial-confuse.bin | 100 | 2,568 | 2,568 | False | n_iters=100 n_blob=2560 stride=2560 nwin=1 calls=100 work/call=770 san=clean truncated=False expected=16962378195829258944 |
| adversarial-oob.bin | 100 | 2,568 | 2,568 | False | n_iters=100 n_blob=2560 stride=2560 nwin=1 calls=100 work/call=770 san=fires truncated=False expected=16962378195829258944 |
| adversarial-oobnear.bin | 100 | 2,568 | 2,568 | False | n_iters=100 n_blob=2560 stride=2560 nwin=1 calls=100 work/call=770 san=fires truncated=False expected=16962378195829258944 |
| adversarial-shortlen.bin | 100 | 4,680 | 4,616 | True | n_iters=100 n_blob=4608 stride=2304 nwin=0 calls=0 work/call=0 san=clean truncated=True expected=None |
| adversarial-tiny.bin | 100 | 264 | 264 | False | n_iters=100 n_blob=256 stride=64 nwin=4 calls=100 work/call=0 san=clean truncated=False expected=0 |
| degenerate.bin | 2,000 | 8,712 | 8,712 | False | n_iters=2000 n_blob=8704 stride=2176 nwin=4 calls=2000 work/call=2176 san=clean truncated=False expected=16891030843067612262 |
| large.bin | 2,000 | 98,312 | 98,312 | False | n_iters=2000 n_blob=98304 stride=6144 nwin=16 calls=2000 work/call=6144 san=clean truncated=False expected=18289686085753579055 |
| small.bin | 8,000 | 36,872 | 36,872 | False | n_iters=8000 n_blob=36864 stride=2304 nwin=16 calls=8000 work/call=2304 san=clean truncated=False expected=4421624378116726888 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — every rung validates the WHOLE transition table before the fold, and `>= SLB_P19_NST` is that test. `c/kernel_hardened.c` spells it; `c/kernel.c` DOES NOT, and that omission is the bug this pattern models. The idiom audit prints the absence, and the absence is the vulnerability.
  - `rust` — every Rust rung validates the WHOLE transition table before the fold, spelled `>= NST`. It is what makes `st < NST` true at the top of the fold in all four.
- **required** — *per language:*
  - `c` — the fold is one indexed load, one multiply and one add per message byte, spelled `acc * 31 + st`; C's unsigned arithmetic wraps by definition (6.2.5p9) so it needs no special spelling.
  - `rust` — the fold is one indexed load, one multiply and one add per message byte, spelled `acc.wrapping_mul(31).wrapping_add(` -- wrapping, not checked, so the kernel is total on VALUES and the only obligation is the index.
- **required** — *per language:*
  - `rust` — THE RUNG BOUNDARY INSIDE THE SAFE CLASS, and it is one token. R2 spells the row `st * 256 + b as usize`; R3 spells it `(st & (NST - 1)) * 256 + b as usize`. Each is present in exactly one rung by construction, so the audit reports the other three as absent for both -- that is the declaration working, not failing.
- **required** — the transition table is ATTACKER DATA read out of the window and is never a compile-time constant, and the decoder dispatches by INDEXING it rather than by switching on the state. Both halves are conditions on the BUG CLASS rather than on the cost, both are forbidden below by name, and both were settled by a run before any cell was written (NOTES.md 0a).
- **required** — the Rust rungs take the window as a sub-slice of `buf` and index that, so the table's length is a compile-time constant to LLVM and the masked index is provably in range. Absolute indexing is forbidden below and it is forbidden for a measured reason, not an aesthetic one.
- **FORBIDDEN** — *per language:*
  - `c` — `switch (st)` -- the hand-rolled dispatch. It is not slower and it is not wrong; it DELETES THE PATTERN, because an out-of-range state then falls to `default` and there is no memory-safety event at all. Measured, not argued: NOTES.md 0a run C, ASan and UBSan both silent. This entry is the bug class's own precondition written as a spelling.
  - `rust` — `match st {` -- the same exclusion on the Rust side.
- **FORBIDDEN** — *per language:*
  - `c` — `static uint8_t` -- a compile-time transition table. With one, every entry is in range by construction and the bug is UNREACHABLE: NOTES.md 0a run A checks all 2048 state-byte successors exhaustively and drives 1e6 adversarial bytes without leaving state 7.
  - `rust` — `const TABLE` -- the same exclusion.
- **FORBIDDEN** — *per language:*
  - `rust` — `buf[off +` -- absolute indexing instead of a sub-slice. Measured (NOTES.md 10): +2.25 Ir/byte on the UNSAFE rung, because the window offset cannot be folded into the base pointer and the fold unrolls 2x instead of 4x; and +10.87 Ir/byte on the MASKED safe rung, because the blob length is a runtime value so the bounds check stops being elidable. It would turn the safe-vs-unsafe comparison into a comparison of base-pointer arithmetic. NOTE the backticked span is the WHOLE of what this entry pins: no other word here is in backticks, because a stray pair around a common identifier is audited as a forbidden spelling in its own right and hit all four Rust rungs on this pattern's first gate run.
- **FORBIDDEN** — *per language:*
  - `rust` — `st % NST` -- the modulo clamp. Semantically identical to the mask under this contract, and a different instruction at a different price; naming it keeps R3's number attached to R3's spelling.
- **FORBIDDEN** — a dead `buf_len` parameter on the C kernel. The length is the thing C does not have and therefore cannot check; handing C one to make the signatures match would be Rust-in-C-syntax and would delete half the comparison.

> **Why**: p19's whole question is where the fact `st < NST` comes from, and every entry above is about that. The kernel folds a message through a transition table that arrives IN THE INPUT, one indexed load per byte, and `st` is loop-carried and data-dependent -- so no bounds check on `tbl[st * 256 + b]` can be hoisted, and the check's exit edge forecloses the 4x unroll the unchecked spelling gets. Three rungs establish the same fact three ways and the pattern prices all three: R5 proves it statically (0 instructions), R3 re-establishes it dynamically with a mask (1 instruction per message byte), R2 tests it per access (measured 6.25 per message byte against R4, of which 3.00 is the check and 3.25 is the unroll it forbids). THE MASK IS A RESPELLING AND NOT A DIFFERENT PROGRAM, AND THE REASON IS THE VALIDATION PASS: after it, `st < NST` holds on every path that reaches the fold, so `st & (NST - 1) == st` identically on every input this benchmark can present, adversarial ones included -- and that equality IS the loop invariant verus.rs discharges. Delete the validation pass and the claim fails: the mask would silently remap an out-of-range state where the checked spelling panics, and R2 and R3 would be two different benchmarks rather than two spellings of one. That is why `required[0]` pins the validation pass in every rung and why the C rung that omits it is the BUG rather than a cheaper rung. THE TWO `forbidden` ENTRIES ABOUT THE BUG CLASS ARE CONDITIONS, NOT TASTE. A textbook "state confusion" bug is a LOGIC bug with no out-of-bounds access, and p19 escapes that only because the table is loaded data and the dispatch is an index. Both were settled by runs before any cell was written (NOTES.md 0a): with a tool-generated table, all 2048 state-byte successors are in range by construction and 1e6 adversarial bytes never leave state 7; with a `switch`, the same bad entry falls to `default` and ASan and UBSan are both silent. A rung that took either route would still compute the pattern's function and would no longer model the pattern's bug, which is exactly what a `forbidden` entry is for. WHAT THE BACKTICKED PINS COST IN AUDIT NOISE, SAID HERE RATHER THAN DISCOVERED: `required[2]` backticks two spellings that are present in exactly one rung each, by construction -- they are the R2/R3 boundary -- so the idiom audit reports each as absent from the other three Rust rungs. That is the declaration working. `required[0]`'s C spelling is absent from `c/kernel.c` for the same kind of reason and it is the sharpest line the audit prints about this pattern: the missing spelling is the vulnerability. p19's numbers are still a spelling's numbers, and the in-contract spread is measured on BOTH sides rather than one (NOTES.md 10): three R2 spellings span 12 Ir/call, three R3 spellings span 11, and three R4 spellings span 11, at m = 4096 -- comparable lever counts, all three degenerate. A fourth R3 spelling, the branch clamp `if st < NST { st } else { 0 }`, is 8.25 Ir/byte dearer than R4, i.e. dearer than the bounds check it replaces; it is in contract and it is not shipped, and saying so is the point of the spread. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p19-state-machine.json`, contract `db6e6c5184e9`.

`20` backticked spelling(s) over `6` rung(s) → **62** (spelling, rung) pair(s), **19** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 9 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 3 spelling(s) pin nothing**, 7 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - pins nothing — `c/kernel_hardened.c` (required[0], c, 0 of 2 rungs)
  - pins nothing — `c/kernel.c` (required[0], c, 0 of 2 rungs)
  - pins nothing — `st < NST` (required[0], rust, 0 of 4 rungs)
  - absent — `>= SLB_P19_NST` (required[0], c, **c/kernel.c**)
  - absent — `st * 256 + b as usize` (required[2], rust, **safe_tuned.rs**)
  - absent — `st * 256 + b as usize` (required[2], rust, **unsafe.rs**)
  - absent — `st * 256 + b as usize` (required[2], rust, **verus.rs**)
  - absent — `(st & (NST - 1)) * 256 + b as usize` (required[2], rust, **safe_naive.rs**)
  - absent — `(st & (NST - 1)) * 256 + b as usize` (required[2], rust, **unsafe.rs**)
  - absent — `(st & (NST - 1)) * 256 + b as usize` (required[2], rust, **verus.rs**)
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
| c-gcc | 26 | 25 | 0 | 91 | 22,648,000 | 90,142,000 | 112,053 | 28,053 | `9bdef5e7` | `9bdef5e7` | yes | - |
| c-clang | 76 | 74 | 2 | 276 | 18,080,000 | 71,720,000 | 112,057 | 28,057 | `be3dc1f4` | `12c8f298` | yes | - |
| safe_naive | 61 | 59 | 8 | 232 | 75,968,000 | 134,192,000 | 112,273 | 28,273 | `a8775111` | `54f33c0b` | yes | - |
| safe_tuned | 110 | 107 | 3 | 429 | 65,296,000 | 91,204,000 | 112,273 | 28,273 | `3376c0aa` | `c649a836` | yes | - |
| unsafe | 103 | 101 | 5 | 411 | 63,216,000 | 83,004,000 | 112,273 | 28,273 | `0ddbc538` | `af3cb7f3` | yes | - |
| verus | 103 | 101 | 5 | 411 | 63,216,000 | 83,004,000 | 112,268 | 28,268 | `0ddbc538` | `af3cb7f3` | yes | - |
| c-gcc-h | 36 | 34 | 0 | 123 | 104,584,000 | 110,626,000 | 112,053 | 28,053 | `ff8b6221` | `ff8b6221` | yes | - |
| c-clang-h | 92 | 89 | 2 | 372 | 63,176,000 | 82,994,000 | 112,057 | 28,057 | `08e778de` | `f925cffa` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 53 | 53 | 0 | 196 | 53,472,000 | - | 288,066 | - | `bf25a167` | `bf25a167` | yes | - |
| c-clang | 40 | 40 | 2 | 163 | 39,088,000 | - | 160,056 | - | `1952cde0` | `013238de` | yes | - |
| safe_naive | 152 | 152 | 15 | 801 | 336,528,000 | - | 200,077 | - | `b9cb5014` | `f49e71e2` | yes | - |
| safe_tuned | 153 | 153 | 11 | 805 | 338,576,000 | - | 200,077 | - | `043414df` | `effdf928` | yes | - |
| unsafe | 83 | 83 | 5 | 395 | 299,344,000 | - | 200,077 | - | `3a651a6a` | `2d85dea7` | yes | - |
| verus | 83 | 83 | 5 | 395 | 299,344,000 | - | 200,056 | - | `5e643064` | `6341bc56` | yes | - |
| c-gcc-h | 66 | 66 | 0 | 257 | 200,960,000 | - | 288,066 | - | `e7fd2241` | `e7fd2241` | yes | - |
| c-clang-h | 56 | 56 | 1 | 233 | 235,720,000 | - | 160,056 | - | `f1554181` | `b4231b4a` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 247 | 245 | 1 | 982 | - | - | 22,712,126 | 90,158,126 | `f6aefd68` | `c611667a` | yes | - |
| c-clang | 297 | 293 | 0 | 1,142 | - | - | 18,152,180 | 71,738,180 | `923d1e05` | `923d1e05` | yes | xmm |
| safe_naive | 692 | 684 | 1 | 3,055 | - | - | 76,048,274 | 134,212,274 | `9233842c` | `33d38a0d` | yes | xmm |
| safe_tuned | 736 | 729 | 1 | 3,199 | - | - | 65,312,282 | 91,208,282 | `193043b8` | `abf9d589` | yes | xmm |
| unsafe | 732 | 723 | 1 | 3,183 | - | - | 63,264,281 | 83,016,281 | `b3a556c0` | `2980f413` | yes | xmm |
| verus | 735 | 726 | 1 | 3,151 | - | - | 63,256,277 | 83,014,277 | `6700e882` | `686ffe62` | yes | xmm |
| c-gcc-h | 256 | 253 | 1 | 1,019 | - | - | 104,640,127 | 110,640,127 | `a519382f` | `98fcc9e0` | yes | - |
| c-clang-h | 324 | 320 | 0 | 1,270 | - | - | 57,088,182 | 81,472,182 | `bc2bf901` | `bc2bf901` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 424 | 53,472,000 | - | 288,066 | - | `b957b5d1` | `b957b5d1` | yes | - |
| c-clang | 66 | 66 | 0 | 273 | 39,088,000 | - | 160,055 | - | `17022df8` | `17022df8` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 336,528,000 | - | 200,077 | - | `10f411f4` | `923b7556` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 338,576,000 | - | 200,077 | - | `10f411f4` | `923b7556` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 299,344,000 | - | 200,077 | - | `cf62559e` | `e391374c` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 299,344,000 | - | 200,056 | - | `adb2809a` | `030bf7ca` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 424 | 200,960,000 | - | 288,066 | - | `d77e90c6` | `d77e90c6` | yes | - |
| c-clang-h | 66 | 66 | 0 | 273 | 235,720,000 | - | 160,055 | - | `28b15415` | `28b15415` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 83/83 vs 83/83 | 5 B vs 5 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 103/101 vs 103/101 | 5 B vs 5 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 18.11 | 18.37 | 1.4% | 6.58 | 6.78 | 3.0% |
| c-gcc | whole | 18.08 | 18.31 | 1.3% | 6.60 | 6.92 | 4.9% |
| c-clang | isolated | 18.34 | 18.56 | 1.2% | 6.84 | 7.12 | 4.1% |
| c-clang | whole | 18.36 | 18.61 | 1.4% | 6.73 | 6.91 | 2.7% |
| safe_naive | isolated | 19.54 | 19.74 | 1.0% | 11.65 | 11.97 | 2.7% |
| safe_naive | whole | 19.40 | 19.72 | 1.6% | 11.49 | 11.63 | 1.3% |
| safe_tuned | isolated | 22.10 | 22.38 | 1.3% | 12.30 | 12.45 | 1.2% |
| safe_tuned | whole | 22.13 | 22.35 | 1.0% | 12.19 | 12.42 | 1.9% |
| unsafe | isolated | 19.50 | 19.74 | 1.2% | 11.68 | 11.85 | 1.5% |
| unsafe | whole | 19.55 | 19.71 | 0.8% | 11.43 | 11.63 | 1.7% |
| verus | isolated | 19.57 | 19.82 | 1.3% | 11.67 | 11.80 | 1.1% |
| verus | whole | 19.67 | 19.83 | 0.8% | 11.68 | 11.78 | 0.9% |
| c-gcc-h | isolated | 19.43 | 19.63 | 1.0% | 12.13 | 12.29 | 1.3% |
| c-gcc-h | whole | 19.46 | 19.74 | 1.4% | 12.06 | 12.25 | 1.6% |
| c-clang-h | isolated | 19.58 | 19.83 | 1.3% | 11.59 | 11.74 | 1.3% |
| c-clang-h | whole | 19.49 | 19.65 | 0.8% | 11.26 | 11.44 | 1.7% |

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
