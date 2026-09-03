# p12-strcat-fixed — results

Generated 2026-09-02T07:44:40Z from `results/p12-strcat-fixed.json` (git `8fd484477573`, working tree dirty).

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
| adversarial-empty.bin | 8 | 20 | 20 | False | n_iters=8 stride=12 n_blob=12 nwin=1 calls=8 work/call=12B san=clean truncated=False expected=227437609984 |
| adversarial-exact.bin | 8 | 144 | 144 | False | n_iters=8 stride=136 n_blob=136 nwin=1 calls=8 work/call=136B san=clean truncated=False expected=16311784084208513152 |
| adversarial-nonul.bin | 8 | 148 | 148 | False | n_iters=8 stride=140 n_blob=140 nwin=1 calls=8 work/call=140B san=fires truncated=False expected=14418293520731682560 |
| adversarial-off1.bin | 8 | 146 | 146 | False | n_iters=8 stride=138 n_blob=138 nwin=1 calls=8 work/call=138B san=fires truncated=False expected=9290935638179312000 |
| adversarial-overflow.bin | 8 | 272 | 272 | False | n_iters=8 stride=264 n_blob=264 nwin=1 calls=8 work/call=264B san=fires truncated=False expected=12091237245548964864 |
| adversarial-stride3.bin | 8 | 38 | 38 | False | n_iters=8 stride=3 n_blob=30 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| large.bin | 40,000 | 7,950,008 | 7,950,008 | False | n_iters=40000 stride=159 n_blob=7950000 nwin=50000 calls=40000 work/call=159B san=clean truncated=False expected=2522496671672975921 |
| small.bin | 120,000 | 13,308 | 13,308 | False | n_iters=120000 stride=133 n_blob=13300 nwin=100 calls=120000 work/call=133B san=clean truncated=False expected=12909139622517405579 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — the SCAN is bounded by the WINDOW in every rung, R1 included -- p12's bug is the write and not the scan: `memchr(buf + off + p, 0, len - p)` in both C rungs.
  - `rust` — the SCAN is bounded by the WINDOW in every rung, R1 included -- p12's bug is the write and not the scan: `while q < len` in all four Rust rungs.
- **required** — *per language:*
  - `c` — THE CAPACITY CHECK, and the only line c/kernel.c omits: `if (dlen + slen <= DST_CAP) {` in c/kernel_hardened.c. c/kernel.c omits exactly this line and nothing else, so the scoped-absent audit pair this entry reports is on that rung and is correct.
  - `rust` — THE CAPACITY CHECK: `if slen <= DST_CAP && dlen + slen <= DST_CAP {` in all four Rust rungs. The left conjunct is the PROVER's and not the programmer's -- without it the additive sum is 'possible arithmetic underflow/overflow' at the pinned vstd and R4 would have no byte-identical R5 twin -- so C and Rust are pinned to different spellings here on purpose. See the why key.
- **required** — *per language:*
  - `c` — the destination is a FIXED-SIZE LOCAL of DST_CAP bytes, never an allocation and never a length from the file: `uint8_t dst[DST_CAP];` in both C rungs.
  - `rust` — the destination is a FIXED-SIZE LOCAL of DST_CAP bytes, never an allocation and never a length from the file: `let mut dst: [u8; DST_CAP] = [0; DST_CAP];` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the COPY is a byte loop and not a bulk call in R1, R1h and R2: `dst[dlen++] = buf[off + i];` in both C rungs.
  - `rust` — the COPY is a byte loop and not a bulk call in R1, R1h and R2: `dst[dlen] = b;` in safe_naive.rs. safe_tuned.rs spells it copy_from_slice and unsafe.rs/verus.rs an unchecked indexed store, deliberately -- that is the measurement (NOTES.md 3) -- so this entry scopes to ONE Rust rung and its three scoped-absent pairs are correct.
- **required** — *per language:*
  - `c` — the string's LENGTH is folded whether or not the string was copied, so the checksum records that a rejected string was seen: `acc = acc * 31 + (uint64_t)slen;` in both C rungs.
  - `rust` — the string's LENGTH is folded whether or not the string was copied, so the checksum records that a rejected string was seen: `.wrapping_add(slen as u64)` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the destination's LIVE LENGTH is folded, so a rung that truncated a string instead of skipping it cannot produce the same checksum: `(acc * 31 + (uint64_t)dlen) * 31` in both C rungs.
  - `rust` — the destination's LIVE LENGTH is folded, so a rung that truncated a string instead of skipping it cannot produce the same checksum: `.wrapping_add(dlen as u64).wrapping_mul(31)` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the destination fold is byte-at-a-time Horner over the live prefix, spelled with the literal multiplier: `acc = acc * 31 + (uint64_t)dst[i];` in both C rungs.
  - `rust` — the destination fold is byte-at-a-time Horner over the live prefix, spelled with the literal multiplier: `.wrapping_mul(31).wrapping_add(` in all four Rust rungs. safe_tuned.rs spells the LOOP as .iter() over a reslice, which is why only the operation and not the loop form is pinned here.
- **required** — *per language:*
  - `c` — a string whose terminator is missing is the last string in the window: `if (q >= len)` in both C rungs.
  - `rust` — a string whose terminator is missing is the last string in the window: `if q >= len {` in all four Rust rungs. This line is also what makes `p = q + 1` provably overflow-free -- see verus.rs's header -- so it is required rather than conventional, exactly as on p11.
- **required** — the cursor steps PAST the terminator: `p = q + 1;` in all seven rungs.
- **required** — *per language:*
  - `c` — the walk is bounded by the WINDOW and never by the declared count: `if (p >= len)` in both C rungs. `nstr` appears in no loop bound in any rung.
  - `rust` — the walk is bounded by the WINDOW and never by the declared count: `if p >= len {` in all four Rust rungs. `nstr` appears in no loop bound in any rung.
- **required** — the little-endian u32 header decode is written out with + and * rather than | and <<, so it stays linear arithmetic: `+ 65536 *` in all seven rungs.
- **required** — ...and its top byte: `+ 16777216 *` in all seven rungs.
- **required** — *per language:*
  - `c` — the declared count is folded, so a rung that walked a different number of strings cannot produce the same checksum either: `* 31 + (uint64_t)nstr` in both C rungs.
  - `rust` — the declared count is folded, so a rung that walked a different number of strings cannot produce the same checksum either: `.wrapping_add(nstr as u64)` in all four Rust rungs.
- **FORBIDDEN** — `strcat(`
- **FORBIDDEN** — `strncat(`
- **FORBIDDEN** — `snprintf(`
- **FORBIDDEN** — `strlen(`
- **FORBIDDEN** — `chunks_exact`
- **FORBIDDEN** — `from_le_bytes`

> **Why**: each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). THE DESTINATION IS A FIXED-SIZE LOCAL AND THE ONLY THING R1 OMITS IS THE CAPACITY CHECK ON THE WRITE: every index into the SOURCE is correct in every rung, the scan is bounded by the window in every rung, and both outer bounds are kept in every rung, so R1-vs-R1h is the cost of the check and nothing else. `strcat(` and `strncat(` and `snprintf(` are forbidden because each of them moves the bound: `strcat` has none at all, so a rung using it could not express R1h; `strncat` and `snprintf` carry one INSIDE libc, so a rung using either would compare a hand-written check against a library's and the R1-vs-R1h column would become p11's library-vs-safety comparison wearing p12's label. `strlen(` is forbidden for the mirror-image reason: it is p11's bug, and a p12 rung that scanned with it would model TWO bugs at once -- an unbounded read AND an unbounded write -- so no adversarial row could attribute a behaviour to either. `chunks_exact` is forbidden for the destination fold because p16 measured that the chunk width moves that pattern's per-byte rate over a 31% range (5.04688...6.62500, `.memory/01-ladder.md`), and p12's whole published decomposition is into a per-scanned-byte, a per-copied-byte and a per-string term. `from_le_bytes` deletes the written-out little-endian header decode every rung shares AND is NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW), so a rung using it would compare a safe cell against an unsafe cell that cannot exist -- the `identity`-pin trap this block's own `identity` key sets. WHAT IS DELIBERATELY *NOT* PINNED, and it is the point of the pattern: **the COPY**. R1, R1h and R2 spell it as a byte loop and that IS pinned for them, because p02's retraction is the precedent -- one operator flips `bulk_calls` and 100% of the delta -- but R3 spells it `copy_from_slice` and R4/R5 spell it an unchecked indexed store, and holding those fixed would hold fixed the one thing p12 exists to compare. What IS pinned instead is that the DESTINATION is a fixed-size local of `DST_CAP` bytes in all seven rungs and that a string which does not fit is SKIPPED rather than truncated, because `dlen` is folded and a truncating rung would produce a different checksum. THE CAPACITY CHECK IS PINNED PER LANGUAGE AND THE TWO SPELLINGS DIFFER, WHICH IS ITSELF A MEASUREMENT: C writes `if (dlen + slen <= DST_CAP) {` and the four Rust rungs write `if slen <= DST_CAP && dlen + slen <= DST_CAP {`. The left conjunct is redundant as a test (`dlen >= 0`) and necessary as a proof obligation -- without it Verus rejects the additive sum with `possible arithmetic underflow/overflow`, because nothing at the pinned vstd bounds `slen` below `usize::MAX` (measured: 14 verified, 1 errors, ../NOTES.md 5). R4 must have a byte-identical R5 twin, so R4 carries it; R2 and R3 carry it so that the matched-spelling R2-vs-R4 difference really is matched; R1h does not, because R1h is not chained to the prover and putting it there would charge the C column for a Verus concession. That price -- +2 STATIC instructions, and 3.00 Ir PER STRING WALKED when measured as a whole-program marginal, `3.00*K - 1.00` exact at five K (../NOTES.md 5; p12 first published the static delta as if it were the per-string rate, corrected at TASK_040_REVIEW) -- is the FIRST MEASURED PRICE THE `identity` PIN HAS EXTRACTED FROM A SHIPPED CELL rather than from a rejected variant. The declaration was written BEFORE any cell was measured for perf -- the R5 proof, the checksums and the disassembly existed, no `Ir` and no `ns` did. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p12-strcat-fixed.json`, contract `809c0d6041f5`.

`41` backticked spelling(s) over `6` rung(s) → **124** (spelling, rung) pair(s), **83** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 12 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 0 spelling(s) pin nothing**, 5 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - absent — `if (dlen + slen <= DST_CAP) {` (required[1], c, **c/kernel.c**)
  - absent — `dst[dlen] = b;` (required[3], rust, **safe_tuned.rs**)
  - absent — `dst[dlen] = b;` (required[3], rust, **unsafe.rs**)
  - absent — `dst[dlen] = b;` (required[3], rust, **verus.rs**)
  - absent — `.wrapping_add(nstr as u64)` (required[12], rust, **verus.rs**)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## What the gate said out loud (reporting only)

From `results/gate/p12-strcat-fixed.json` — the `loud` and `controls_json` keys, at contract `809c0d6041f5`. **These did not fail the gate and are not defects**; they are the conditions `check.py` refuses to be silent about. Each one is a caveat on a number below or on the declaration above. The run's **verdict** is deliberately not printed here: it is an output of the same gate run that checks this table is current (stage `9c`), and rendering it made the table an input to its own checker — see `read_gate_loud`. Read the verdict from `results/gate/p12-strcat-fixed.json`.

- **`doc-citation-other`** — 1 line citation(s) into harness modules other than `check.py`. NOT failed: these sit in measurement-hashed files, so re-citing them by function costs a re-measure (RECAP queue item 38). Cite the FUNCTION when one of these files is next re-measured anyway: patterns/p12-strcat-fixed/README.md:48 -> measure.py:64
- **`tcb-unsafe`** — verus.rs:327 `dst_set_unchecked`'s `requires` constrains nothing about ['x'], which its trusted body uses. spec.md justifies it: `x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `u8` is a legal thing to store in a `u8` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [u8; 128]` reads `i < 128`. This is the parameter-coverage false positive `.memory/04-verus.md` names and p03 was the first pattern to exercise; p12 is the second, and on p12 the item is the one the whole pattern is about. A second conjunct `old(v)@.len() == 128` is deliberately NOT written: for a `&mut [u8; 128]` it is a TAUTOLOGY discharged from the parameter type alone by vstd's `array_len_matches_n`, and p03's gate run refused exactly that draft (p03 NOTES.md 5b).


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 139 | 137 | 0 | 514 | 164,880,000 | 110,280,000 | 1,800,056 | 600,056 | `06c55975` | `06c55975` | yes | - |
| c-clang | 146 | 143 | 2 | 517 | 124,920,004 | 85,440,004 | 1,680,059 | 560,059 | `e5287c37` | `38be9c51` | yes | - |
| safe_naive | 231 | 224 | 15 | 897 | 311,040,000 | 197,200,000 | 1,680,275 | 560,275 | `06d0c70a` | `aa4991cf` | yes | xmm |
| safe_tuned | 164 | 160 | 14 | 610 | 211,080,000 | 111,360,000 | 1,680,275 | 560,275 | `5bcd8cd2` | `fe0d4a3e` | yes | xmm |
| unsafe | 142 | 138 | 9 | 503 | 210,720,000 | 112,400,000 | 1,680,275 | 560,275 | `f2572cd5` | `f154b78f` | yes | xmm |
| verus | 142 | 138 | 9 | 503 | 210,720,000 | 112,400,000 | 1,560,274 | 520,274 | `f2572cd5` | `f154b78f` | yes | xmm |
| c-gcc-h | 136 | 132 | 0 | 531 | 161,880,000 | 105,280,000 | 1,800,056 | 600,056 | `1f0e59b6` | `1f0e59b6` | yes | - |
| c-clang-h | 145 | 141 | 2 | 517 | 125,760,004 | 87,720,004 | 1,680,059 | 560,059 | `d2317e52` | `dd68cab1` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 160 | 158 | 0 | 806 | 489,120,000 | - | 4,320,066 | - | `ba88cd43` | `ba88cd43` | yes | - |
| c-clang | 123 | 123 | 1 | 650 | 451,560,004 | - | 2,520,056 | - | `593df4d6` | `c9be4189` | yes | - |
| safe_naive | 218 | 218 | 6 | 1,242 | 975,120,000 | - | 3,000,077 | - | `0883f50f` | `1d4af432` | yes | - |
| safe_tuned | 231 | 231 | 10 | 1,238 | 663,960,000 | - | 3,000,077 | - | `a51f4fd5` | `352be600` | yes | - |
| unsafe | 172 | 172 | 5 | 939 | 914,280,000 | - | 3,000,077 | - | `a6677ac3` | `f8e13558` | yes | - |
| verus | 172 | 172 | 5 | 939 | 914,280,000 | - | 3,000,056 | - | `89a3f3a5` | `d6cacbf5` | yes | - |
| c-gcc-h | 165 | 163 | 0 | 831 | 492,720,000 | - | 4,320,066 | - | `9b2bde5e` | `9b2bde5e` | yes | - |
| c-clang-h | 128 | 128 | 2 | 674 | 455,160,004 | - | 2,520,056 | - | `06a6d9ec` | `4b5d183f` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 348 | 345 | 2 | 1,412 | - | - | 164,400,133 | 111,120,133 | `0ff45aa7` | `7775da1c` | yes | - |
| c-clang | 421 | 418 | 0 | 1,622 | - | - | 120,480,187 | 83,800,187 | `c58a454c` | `c58a454c` | yes | xmm |
| safe_naive | 854 | 841 | 1 | 3,919 | - | - | 310,560,279 | 195,920,279 | `171231ef` | `0bf614d3` | yes | xmm |
| safe_tuned | 797 | 785 | 1 | 3,647 | - | - | 211,080,278 | 110,360,278 | `67eb7fb7` | `2774c280` | yes | xmm |
| unsafe | 764 | 753 | 1 | 3,503 | - | - | 224,040,278 | 113,880,278 | `20dedade` | `a8fdfb2e` | yes | xmm |
| verus | 773 | 762 | 1 | 3,503 | - | - | 223,800,284 | 113,800,284 | `a92a3cda` | `2ef13417` | yes | xmm |
| c-gcc-h | 367 | 363 | 2 | 1,509 | - | - | 161,640,131 | 105,200,131 | `c8afb69e` | `d80e7600` | yes | - |
| c-clang-h | 416 | 411 | 0 | 1,623 | - | - | 120,720,187 | 84,840,187 | `f6b7fb50` | `f6b7fb50` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 489,120,000 | - | 4,320,066 | - | `141c813e` | `141c813e` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 450,120,004 | - | 2,520,055 | - | `624e4384` | `624e4384` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 975,120,000 | - | 3,000,077 | - | `52377124` | `cd4b912e` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 663,960,000 | - | 3,000,077 | - | `ea48a915` | `28da6c47` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 914,280,000 | - | 3,000,077 | - | `450ce6cc` | `ece2be7f` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 914,280,000 | - | 3,000,056 | - | `fc8a90fb` | `cc35e4c8` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 492,720,000 | - | 4,320,066 | - | `80e67e05` | `80e67e05` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 453,720,004 | - | 2,520,055 | - | `8844209c` | `8844209c` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 172/172 vs 172/172 | 5 B vs 5 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 142/138 vs 142/138 | 9 B vs 9 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 28.85 | 29.25 | 1.4% | 24.37 | 24.74 | 1.5% |
| c-gcc | whole | 28.91 | 29.63 | 2.5% | 24.30 | 24.81 | 2.1% |
| c-clang | isolated | 27.10 | 27.60 | 1.8% | 23.34 | 23.71 | 1.6% |
| c-clang | whole | 27.54 | 28.13 | 2.1% | 23.47 | 23.94 | 2.0% |
| safe_naive | isolated | 30.96 | 31.60 | 2.1% | 36.85 | 37.32 | 1.3% |
| safe_naive | whole | 30.55 | 31.06 | 1.7% | 36.64 | 37.20 | 1.5% |
| safe_tuned | isolated | 27.35 | 27.99 | 2.3% | 30.42 | 30.71 | 0.9% |
| safe_tuned | whole | 27.22 | 27.61 | 1.4% | 30.39 | 30.77 | 1.2% |
| unsafe | isolated | 26.57 | 27.48 | 3.4% | 30.14 | 30.67 | 1.8% |
| unsafe | whole | 27.04 | 27.65 | 2.3% | 31.49 | 32.07 | 1.8% |
| verus | isolated | 26.49 | 27.03 | 2.0% | 30.40 | 30.75 | 1.2% |
| verus | whole | 27.02 | 27.89 | 3.2% | 31.94 | 32.36 | 1.3% |
| c-gcc-h | isolated | 28.18 | 29.02 | 3.0% | 24.28 | 24.62 | 1.4% |
| c-gcc-h | whole | 28.27 | 28.82 | 1.9% | 24.21 | 24.60 | 1.6% |
| c-clang-h | isolated | 27.26 | 27.84 | 2.1% | 23.61 | 24.11 | 2.1% |
| c-clang-h | whole | 27.22 | 27.87 | 2.4% | 23.52 | 23.89 | 1.6% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
