# p17-http-range — results

Generated 2026-08-17T18:33:08Z from `results/p17-http-range.json` (git `712ca8501b8b`, working tree dirty).

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
| adversarial-leak.bin | 8 | 72 | 72 | False | n_iters=8 stride=64 n_blob=64 nwin=1 calls=8 work/call=64B san=clean truncated=False expected=13350769809739249920 |
| adversarial-nsuf.bin | 8 | 552 | 552 | False | n_iters=8 stride=34 n_blob=544 nwin=16 calls=8 work/call=34B san=clean truncated=False expected=0 |
| adversarial-oob.bin | 8 | 72 | 72 | False | n_iters=8 stride=64 n_blob=64 nwin=1 calls=8 work/call=64B san=fires truncated=False expected=13350769809739249920 |
| adversarial-stride1.bin | 8 | 120 | 120 | False | n_iters=8 stride=1 n_blob=112 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| large.bin | 12,000 | 8,390,658 | 8,390,658 | False | n_iters=12000 stride=4093 n_blob=8390650 nwin=2050 calls=12000 work/call=4093B san=clean truncated=False expected=10613012665269285418 |
| small.bin | 25,000 | 16,200 | 16,200 | False | n_iters=25000 stride=506 n_blob=16192 nwin=32 calls=25000 work/call=506B san=clean truncated=False expected=18416420189787787870 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — start and end are int64_t / i64 in every rung, and the spec functions are written over int, not nat
- **required** — *per language:*
  - `c` — the guard is the one conjunctive `if (start < end && start >= 0) {`, not two `continue`s
  - `rust` — the guard is the one conjunctive `if start < end && start >= 0 {`, not two `continue`s
- **required** — R1 omits only `&& start >= 0` -- it keeps `len < 2` and `2 + 2*nsuf > len`
- **required** — nserved is folded into the result
- **FORBIDDEN** — unsigned start/end
- **FORBIDDEN** — `Range:` text parsing -- the fields are bytes, not ASCII
- **FORBIDDEN** — a window-relative sign guard where a slice-relative one is meant, and vice versa

> **Why**: making start unsigned deletes the CVE: `start < 0` becomes unrepresentable and the leak row of the semantics table could not exist. ASCII parsing adds a second new variable (string parsing is p11-p15). The `continue` spelling is not expressible in Verus ('for-loops do not yet support continue') and the while workaround hoists the increment above the guard in all six rungs. The last forbidden entry is the one that already cost this pattern a retraction: `start >= -(body_start as i64)` and `start >= -((off + body_start) as i64)` differ by one token, both verify, and only the second is what a bounds check buys -- see NOTES.md 1c. RESTATED in this hashed block at TASK_016 from the prose section 'Load-bearing, do not improve' above -- restated, not moved: the prose is still there, says the same thing, and THIS block is the authoritative copy of it (TASK_016_REVIEW m2). Whoever edits one edits the other. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither. WHAT THE STANDARD SAYS ABOUT p17, and it withdraws a claim this project published one task ago. `.temp/p05r3/v17/tuned_suffix.rs` (NOTES.md 10 row 3) has NO `end` binding anywhere in its code -- the only two hits for the word are in doc comments -- and writes `start < content_len` where `required[1]` names `start < end`. Under the standard it is OUT OF CONTRACT on two entries. TASK_017 wrote the opposite into NOTES.md -- that it `satisfies all four of p17's required entries` including `the one conjunctive if start < end && start >= 0` -- in the same commit that ruled the analogous p16 spelling out (TASK_017_REVIEW B1). That sentence is false of the file and is corrected in NOTES.md 10. AND HERE IS WHAT THE EXCLUSION IS WORTH, measured at TASK_018: NOTHING, to any number. `.temp/p18/v17/r3_incontract.rs` keeps `let start: i64`, `let end: i64`, the literal `if start < end && start >= 0` and `n = end - start`, and respells ONLY the suffix-table walk (`chunks_exact(2)`) and the byte fold (a suffix reslice of the body) -- the two things this `why` says are not restricted. It compiles to machine code BYTE-IDENTICAL to `tuned_suffix.rs`: `md5_fn 532201c70eeb5fea622c8199d94edd99`, `md5_raw 12fd8faca909d0e087c517a0f1142d25`, `n_fn 135`, both at -O3 isolated. rustc erases the distinction the pin draws, so the excluded row's NUMBER is fully reachable in contract and it is the SHIPPED R3 that is off the floor: `R3ship - R3incontract = 51.00` Ir/call flat on both bands, `R3incontract - R4ship = -19.00` flat, 8/8 committed inputs identical. CONSEQUENCE: p17's published `R3 - R4 = +32 Ir/call` is not what safety costs on this kernel, it is what THIS R3 spelling costs, and an admissible spelling measures 51 cheaper. `The shipped R3 is the cheapest admissible one` is FALSE for p17, not merely unestablished. .memory/01-ladder.md finding 14 forbids reading `-19` as `safe beats unsafe`: R4 is a spelling too and its in-contract space has not been searched. Still NOT restricted: the R2/R3/R4 spelling of the byte fold and of the suffix-table walk -- which is precisely where all 51 Ir/call live.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p17-http-range.json`, contract `5c0e57e32b6c`.

`12` backticked spelling(s) over `6` rung(s) → **36** (spelling, rung) pair(s), **22** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 2 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 2 spelling(s) pin nothing**, 2 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - pins nothing — `continue` (required[1], c, 0 of 2 rungs)
  - pins nothing — `continue` (required[1], rust, 0 of 4 rungs)
  - absent — `if (start < end && start >= 0) {` (required[1], c, **c/kernel.c**)
  - absent — `&& start >= 0` (required[2], c, **c/kernel.c**)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## What the gate said out loud (reporting only)

From `results/gate/p17-http-range.json` — the `loud` and `controls_json` keys, at contract `5c0e57e32b6c`, verdict `PASS`. **These did not fail the gate and are not defects**; they are the conditions `check.py` refuses to be silent about. Each one is a caveat on a number below or on the declaration above.

- **`idiom-forbidden`** — idiom.forbidden[0] has NOT ONE backticked spelling, so the enforced audit never ranges over it and its share of the 0 hits above is vacuous: unsigned start/end. Backtick the spelling if it has one (p09 shipped 5 entries and 0 audited spellings; TASK_038_REVIEW) -- and if it has none, because the entry forbids a STRUCTURE rather than a token (p05's 'a running row pointer'), say so in `why`: this line is then permanent and correct, and it is what stops the pattern's `ok` above from reading as enforcement it does not have.
- **`idiom-forbidden`** — idiom.forbidden[2] has NOT ONE backticked spelling, so the enforced audit never ranges over it and its share of the 0 hits above is vacuous: a window-relative sign guard where a slice-relative one is meant, and vice versa. Backtick the spelling if it has one (p09 shipped 5 entries and 0 audited spellings; TASK_038_REVIEW) -- and if it has none, because the entry forbids a STRUCTURE rather than a token (p05's 'a running row pointer'), say so in `why`: this line is then permanent and correct, and it is what stops the pattern's `ok` above from reading as enforcement it does not have.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 64 | 61 | 0 | 217 | 176,275,000 | 686,916,000 | 375,059 | 180,059 | `c1660193` | `c1660193` | yes | - |
| c-clang | 105 | 101 | 1 | 343 | 128,750,000 | 494,652,000 | 350,061 | 168,061 | `3d55c912` | `efc40904` | yes | - |
| safe_naive | 90 | 88 | 5 | 315 | 220,475,000 | 858,708,000 | 350,275 | 168,275 | `11f40e77` | `bbf2778e` | yes | - |
| safe_tuned | 152 | 148 | 13 | 563 | 130,675,000 | 495,576,000 | 350,275 | 168,275 | `dc83df31` | `3c88407b` | yes | - |
| unsafe | 120 | 116 | 9 | 407 | 129,875,000 | 495,192,000 | 350,275 | 168,275 | `45064db2` | `c983a7bb` | yes | - |
| verus | 120 | 116 | 9 | 407 | 129,875,000 | 495,192,000 | 325,274 | 156,274 | `45064db2` | `c983a7bb` | yes | - |
| c-gcc-h | 67 | 63 | 0 | 217 | 176,500,000 | 687,024,000 | 375,059 | 180,059 | `f6aeafaa` | `f6aeafaa` | yes | - |
| c-clang-h | 114 | 110 | 1 | 362 | 129,225,000 | 494,880,000 | 350,061 | 168,061 | `c9c46710` | `3d0f6ee8` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 118 | 118 | 0 | 445 | 418,700,000 | - | 900,069 | - | `516f3302` | `516f3302` | yes | - |
| c-clang | 102 | 102 | 1 | 422 | 309,450,000 | - | 525,059 | - | `ac4fa9b4` | `71a69482` | yes | - |
| safe_naive | 168 | 168 | 3 | 861 | 485,600,000 | - | 625,081 | - | `9b9ab659` | `ff305300` | yes | - |
| safe_tuned | 247 | 247 | 0 | 1,328 | 512,650,000 | - | 625,081 | - | `8fca2753` | `8fca2753` | yes | - |
| unsafe | 129 | 129 | 7 | 633 | 441,100,000 | - | 625,081 | - | `4e4d8a5a` | `8bda29ea` | yes | - |
| verus | 129 | 129 | 7 | 633 | 441,100,000 | - | 625,060 | - | `38b25209` | `8815416f` | yes | - |
| c-gcc-h | 120 | 120 | 0 | 452 | 418,850,000 | - | 900,069 | - | `c2a7c4fb` | `c2a7c4fb` | yes | - |
| c-clang-h | 104 | 104 | 1 | 429 | 309,600,000 | - | 525,059 | - | `f31daedd` | `18c6d79d` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 282 | 279 | 0 | 1,104 | - | - | 176,450,129 | 687,000,129 | `c23a8d72` | `c23a8d72` | yes | - |
| c-clang | 318 | 313 | 0 | 1,229 | - | - | 128,400,185 | 494,484,185 | `1f9dba5c` | `1f9dba5c` | yes | xmm |
| safe_naive | 727 | 718 | 1 | 3,263 | - | - | 242,500,280 | 944,568,280 | `81fc0e51` | `b4f332c7` | yes | xmm |
| safe_tuned | 755 | 745 | 1 | 3,359 | - | - | 129,200,281 | 494,868,281 | `ca814365` | `73ce707f` | yes | xmm |
| unsafe | 727 | 716 | 1 | 3,231 | - | - | 134,425,280 | 516,180,280 | `11e75e3b` | `00f92f97` | yes | xmm |
| verus | 740 | 730 | 1 | 3,199 | - | - | 135,175,276 | 516,540,276 | `62ea0d20` | `b0e601eb` | yes | xmm |
| c-gcc-h | 284 | 281 | 0 | 1,104 | - | - | 176,600,129 | 687,072,129 | `80fe549b` | `80fe549b` | yes | - |
| c-clang-h | 319 | 314 | 0 | 1,229 | - | - | 128,475,185 | 494,520,185 | `0bffb12f` | `0bffb12f` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 103 | 103 | 0 | 439 | 418,700,000 | - | 900,069 | - | `cf9dd676` | `cf9dd676` | yes | - |
| c-clang | 70 | 70 | 0 | 301 | 309,450,000 | - | 525,058 | - | `dc2f5099` | `dc2f5099` | yes | - |
| safe_naive | 127 | 127 | 4 | 636 | 485,600,000 | - | 625,081 | - | `aab3f1b5` | `e5e87472` | yes | xmm |
| safe_tuned | 127 | 127 | 4 | 636 | 512,650,000 | - | 625,081 | - | `6b12c934` | `4781a915` | yes | xmm |
| unsafe | 127 | 127 | 4 | 636 | 441,100,000 | - | 625,081 | - | `d602e819` | `d82dac3c` | yes | xmm |
| verus | 90 | 90 | 11 | 453 | 441,100,000 | - | 625,060 | - | `a425f93e` | `7aa9a4ff` | yes | xmm |
| c-gcc-h | 103 | 103 | 0 | 439 | 418,850,000 | - | 900,069 | - | `33331aa7` | `33331aa7` | yes | - |
| c-clang-h | 70 | 70 | 0 | 301 | 309,600,000 | - | 525,058 | - | `741aedc0` | `741aedc0` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 129/129 vs 129/129 | 7 B vs 7 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 120/116 vs 120/116 | 9 B vs 9 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 76.91 | 79.32 | 3.1% | 20.17 | 20.52 | 1.7% |
| c-gcc | whole | 76.84 | 79.10 | 2.9% | 19.99 | 20.58 | 2.9% |
| c-clang | isolated | 77.22 | 79.51 | 3.0% | 20.11 | 20.48 | 1.8% |
| c-clang | whole | 77.09 | 79.55 | 3.2% | 20.12 | 20.48 | 1.8% |
| safe_naive | isolated | 77.18 | 79.26 | 2.7% | 20.30 | 20.61 | 1.6% |
| safe_naive | whole | 77.27 | 79.41 | 2.8% | 20.30 | 20.66 | 1.8% |
| safe_tuned | isolated | 77.45 | 79.16 | 2.2% | 20.24 | 20.59 | 1.7% |
| safe_tuned | whole | 77.24 | 79.44 | 2.8% | 20.28 | 20.61 | 1.6% |
| unsafe | isolated | 77.29 | 79.86 | 3.3% | 20.34 | 20.55 | 1.0% |
| unsafe | whole | 77.23 | 80.20 | 3.9% | 20.27 | 20.49 | 1.1% |
| verus | isolated | 77.84 | 80.92 | 4.0% | 20.26 | 20.59 | 1.6% |
| verus | whole | 77.17 | 80.31 | 4.1% | 20.36 | 20.56 | 1.0% |
| c-gcc-h | isolated | 76.43 | 78.52 | 2.7% | 20.16 | 20.44 | 1.4% |
| c-gcc-h | whole | 77.35 | 79.10 | 2.3% | 20.20 | 20.43 | 1.1% |
| c-clang-h | isolated | 77.29 | 80.10 | 3.6% | 20.15 | 20.38 | 1.1% |
| c-clang-h | whole | 77.34 | 80.35 | 3.9% | 20.16 | 20.40 | 1.2% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
