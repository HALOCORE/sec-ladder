# p08-overlap-move — results

Generated 2026-08-18T03:14:40Z from `results/p08-overlap-move.json` (git `4ab7a5505ef4`, working tree dirty).

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
| adversarial-dbig.bin | 8 | 76 | 76 | False | n_iters=8 stride=68 n_blob=68 nwin=1 calls=8 work/call=68B san=clean truncated=False expected=0 |
| adversarial-dzero.bin | 8 | 76 | 76 | False | n_iters=8 stride=68 n_blob=68 nwin=1 calls=8 work/call=68B san=clean truncated=False expected=0 |
| adversarial-overlap.bin | 8 | 4,101 | 4,101 | False | n_iters=8 stride=4093 n_blob=4093 nwin=1 calls=8 work/call=4093B san=clean truncated=False expected=17006177784580028288 |
| adversarial-stride3.bin | 8 | 32 | 32 | False | n_iters=8 stride=3 n_blob=24 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| large.bin | 8,000 | 33,529,864 | 33,529,864 | False | n_iters=8000 stride=4093 n_blob=33529856 nwin=8192 calls=8000 work/call=4093B san=clean truncated=False expected=16961355432730674521 |
| small.bin | 25,000 | 16,072 | 16,072 | False | n_iters=25000 stride=502 n_blob=16064 nwin=32 calls=25000 work/call=502B san=clean truncated=False expected=5963384295905503290 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — R1 spells the move memcpy and R1h memmove -- that one token is the whole difference between them
- **required** — R2 shifts element-by-element in a backward loop, R3 uses copy_within, R4/R5 use core::ptr::copy; R2 and R3 differ in the body of move_right and in nothing else
- **required** — the bounds guard `m < 2 || d == 0 || d + nrep > m` is checked ONCE, outside the round loop, in every rung including R1
- **required** — dr = d + r, not a fixed d
- **required** — nrep = 1 + (nrep_w % 4), a mask and not a check, written `%` and not `&`
- **required** — scr is a fixed SCR = 4096 byte array LOCAL to the kernel in all six rungs, zero-initialised in all six, and m = min(avail, SCR)
- **FORBIDDEN** — a per-round bounds check -- do not push the guard into the loop
- **FORBIDDEN** — `nrep_w & 3`
- **FORBIDDEN** — a driver-owned &mut scratch argument
- **FORBIDDEN** — writing anything into the space the move opens

> **Why**: p08's result is that one token (memcpy vs memmove) is the whole bug and that safe Rust cannot express it, so a rung that spells the move differently is not a rung of p08. A fixed d makes every round after the first a no-op, the checksum stops depending on nrep, and LLVM is free to delete the rounds. `&` is the same instruction as `%` on unsigned values but drags `by (bit_vector)` into R5 -- a cheaper proof of an identical specification, which `.memory/04-verus.md` blesses. The scratch must be kernel-local because `driver.call_args` refuses to drop anything that is not a single bare identifier, so C's `scr` and Rust's `&mut scr` cannot be reconciled by the driver diff; making them so would be a harness/ change, and the zero-init keeps the memset a uniform per-call constant that cancels in every rung-to-rung comparison. Writing header bytes into the opened space is a second bounded loop that adds nothing to the aliasing axis. RESTATED in this hashed block at TASK_016 from the prose sections 'Load-bearing, do not improve' and 'The scratch buffer' above -- restated, not moved: the prose is still there, says the same thing, and THIS block is the authoritative copy of it (TASK_016_REVIEW m2). Whoever edits one edits the other. TASK_016 did not measure a spelling spread for p08 and none is claimed here. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p08-overlap-move.json`, contract `78f5575dee2d`.

`8` backticked spelling(s) over `6` rung(s) → **24** (spelling, rung) pair(s), **16** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 2 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 1 spelling(s) pin nothing**, 0 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - pins nothing — `&` (required[4], c, 0 of 2 rungs)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried. Use the `isolated` kernel-exclusive figure, which needs no correction.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 118 | 111 | 0 | 449 | 117,350,000 | 270,968,000 | 375,056 | 120,056 | `2e75e9df` | `2e75e9df` | yes | - |
| c-clang | 131 | 129 | 1 | 455 | 74,225,004 | 188,920,004 | 350,059 | 112,059 | `be02c922` | `408b866d` | yes | - |
| safe_naive | 269 | 263 | 11 | 1,077 | 351,500,000 | 924,568,000 | 350,275 | 112,275 | `3ce9c60e` | `d9810c88` | yes | - |
| safe_tuned | 205 | 204 | 15 | 817 | 75,250,000 | 189,248,000 | 350,275 | 112,275 | `9d8962a3` | `078ac88f` | yes | - |
| unsafe | 168 | 166 | 15 | 625 | 74,600,000 | 189,040,000 | 350,275 | 112,275 | `9259612a` | `44b63d20` | yes | - |
| verus | 168 | 166 | 15 | 625 | 74,600,000 | 189,040,000 | 350,270 | 112,270 | `9259612a` | `44b63d20` | yes | - |
| c-gcc-h | 118 | 111 | 0 | 449 | 117,350,000 | 270,968,000 | 375,056 | 120,056 | `c64258dd` | `c64258dd` | yes | - |
| c-clang-h | 131 | 129 | 1 | 455 | 74,225,008 | 188,920,008 | 350,059 | 112,059 | `2831c4e9` | `c428babb` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 135 | 135 | 0 | 678 | 203,550,000 | - | 900,066 | - | `849bdf7c` | `849bdf7c` | yes | - |
| c-clang | 104 | 104 | 1 | 557 | 153,025,004 | - | 525,056 | - | `35eea7fd` | `97f4c9c3` | yes | - |
| safe_naive | 241 | 241 | 7 | 1,385 | 770,425,000 | - | 625,077 | - | `00466200` | `398f2efc` | yes | - |
| safe_tuned | 207 | 207 | 8 | 1,160 | 229,425,000 | - | 625,077 | - | `e961e8f4` | `5707c96c` | yes | - |
| unsafe | 206 | 206 | 9 | 1,159 | 229,325,000 | - | 625,077 | - | `7bbb6ae9` | `9d7b97e3` | yes | - |
| verus | 206 | 206 | 9 | 1,159 | 229,325,000 | - | 625,056 | - | `7bbb6ae9` | `9d7b97e3` | yes | - |
| c-gcc-h | 135 | 135 | 0 | 678 | 203,550,000 | - | 900,066 | - | `0d39618a` | `0d39618a` | yes | - |
| c-clang-h | 104 | 104 | 1 | 557 | 153,025,008 | - | 525,056 | - | `29a1dc65` | `3315f5df` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 229 | 228 | 1 | 923 | 117,150,000 | 270,904,000 | 375,127 | 120,127 | `ae370922` | `bf5995c5` | yes | - |
| c-clang | 434 | 429 | 0 | 1,755 | - | - | 69,675,211 | 176,688,211 | `7c47156a` | `7c47156a` | yes | xmm |
| safe_naive | 878 | 864 | 1 | 4,111 | - | - | 265,175,299 | 695,680,299 | `10a2ff0b` | `c6ab2099` | yes | xmm |
| safe_tuned | 858 | 848 | 1 | 3,983 | - | - | 75,025,300 | 189,176,300 | `cbdda3e4` | `169bfb6a` | yes | xmm |
| unsafe | 818 | 808 | 1 | 3,759 | - | - | 74,550,296 | 189,024,296 | `3a2fabe8` | `f4c85a29` | yes | xmm |
| verus | 818 | 808 | 1 | 3,727 | - | - | 74,475,293 | 189,000,293 | `d51e5096` | `d9616053` | yes | xmm |
| c-gcc-h | 229 | 228 | 1 | 923 | 117,150,000 | 270,904,000 | 375,127 | 120,127 | `9a7376d4` | `b891f79e` | yes | - |
| c-clang-h | 434 | 429 | 0 | 1,755 | - | - | 69,675,215 | 176,688,215 | `8b3ecff0` | `8b3ecff0` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 203,550,000 | - | 900,066 | - | `54d124bf` | `54d124bf` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 152,975,004 | - | 525,055 | - | `273b5f18` | `273b5f18` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 770,425,000 | - | 625,077 | - | `97e0cb59` | `f2e1c45f` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 229,425,000 | - | 625,077 | - | `778c41d9` | `ac1c611a` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 229,325,000 | - | 625,077 | - | `a325bd16` | `aca80a8b` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 229,325,000 | - | 625,056 | - | `686f4703` | `bac78b04` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 203,550,000 | - | 900,066 | - | `9dbb8f7c` | `9dbb8f7c` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 152,975,008 | - | 525,055 | - | `273b5f18` | `273b5f18` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | **yes** | **yes** | **yes** | 206/206 vs 206/206 | 9 B vs 9 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 168/166 vs 168/166 | 15 B vs 15 B |

## Wall clock (secondary)

> taskset -c 5, interleaved round-robin, 31 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 72.73 | 73.51 | 1.1% | 13.89 | 14.11 | 1.6% |
| c-gcc | whole | 72.32 | 73.41 | 1.5% | 13.90 | 14.11 | 1.5% |
| c-clang | isolated | 72.24 | 73.26 | 1.4% | 13.70 | 13.89 | 1.4% |
| c-clang | whole | 72.69 | 73.56 | 1.2% | 13.73 | 13.93 | 1.5% |
| safe_naive | isolated | 109.17 | 110.28 | 1.0% | 28.44 | 28.74 | 1.1% |
| safe_naive | whole | 99.08 | 99.99 | 0.9% | 24.63 | 24.95 | 1.3% |
| safe_tuned | isolated | 72.80 | 73.63 | 1.1% | 13.83 | 14.09 | 1.8% |
| safe_tuned | whole | 72.57 | 73.76 | 1.6% | 13.81 | 14.10 | 2.1% |
| unsafe | isolated | 72.34 | 73.44 | 1.5% | 13.86 | 14.06 | 1.4% |
| unsafe | whole | 72.84 | 73.56 | 1.0% | 13.95 | 14.13 | 1.3% |
| verus | isolated | 72.40 | 73.22 | 1.1% | 13.88 | 14.08 | 1.4% |
| verus | whole | 72.88 | 73.41 | 0.7% | 13.97 | 14.12 | 1.1% |
| c-gcc-h | isolated | 72.47 | 73.41 | 1.3% | 13.89 | 14.15 | 1.8% |
| c-gcc-h | whole | 72.45 | 73.51 | 1.5% | 13.91 | 14.10 | 1.4% |
| c-clang-h | isolated | 72.01 | 73.40 | 1.9% | 13.67 | 13.91 | 1.7% |
| c-clang-h | whole | 71.97 | 73.25 | 1.8% | 13.80 | 13.99 | 1.4% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
