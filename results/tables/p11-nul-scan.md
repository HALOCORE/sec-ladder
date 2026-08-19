# p11-nul-scan — results

Generated 2026-08-19T15:01:06Z from `results/p11-nul-scan.json` (git `36b64ea403f2`, working tree dirty).

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
| adversarial-count.bin | 8 | 48 | 48 | False | n_iters=8 stride=40 n_blob=40 nwin=1 calls=8 work/call=40B san=fires truncated=False expected=11408910424468685312 |
| adversarial-empty.bin | 8 | 20 | 20 | False | n_iters=8 stride=12 n_blob=12 nwin=1 calls=8 work/call=12B san=clean truncated=False expected=227437609984 |
| adversarial-nonul.bin | 8 | 74 | 74 | False | n_iters=8 stride=66 n_blob=66 nwin=1 calls=8 work/call=66B san=fires truncated=False expected=18024987679707349248 |
| adversarial-stride3.bin | 8 | 38 | 38 | False | n_iters=8 stride=3 n_blob=30 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| adversarial-zerotail.bin | 8 | 48 | 48 | False | n_iters=8 stride=40 n_blob=40 nwin=1 calls=8 work/call=40B san=clean truncated=False expected=17859238140672197760 |
| large.bin | 1,500 | 8,290,008 | 8,290,008 | False | n_iters=1500 stride=4145 n_blob=8290000 nwin=2000 calls=1500 work/call=4145B san=clean truncated=False expected=1712828251200407713 |
| small.bin | 6,000 | 14,312 | 14,312 | False | n_iters=6000 stride=1192 n_blob=14304 nwin=12 calls=6000 work/call=1192B san=clean truncated=False expected=11230946376629265678 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — the scan and the fold are SEPARATE loops and the length is materialised between them: `slen = q - p;` in both C rungs.
  - `rust` — the scan and the fold are SEPARATE loops and the length is materialised between them: `let slen: usize = q - p;` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the fold is byte-at-a-time Horner over the measured span, spelled with the literal multiplier: `h = h * 31 + (uint64_t)buf[off + i];` in both C rungs.
  - `rust` — the fold is byte-at-a-time Horner over the measured span, spelled with the literal multiplier: `.wrapping_mul(31).wrapping_add(` in all four Rust rungs. safe_tuned.rs spells the LOOP as `.iter().fold(`, which is why only the operation and not the loop form is pinned here.
- **required** — *per language:*
  - `c` — the measured length is folded into the string's value, so a rung that folds the same bytes but finds a different terminator cannot produce the same checksum: `(h ^ (uint64_t)slen)` in both C rungs.
  - `rust` — the measured length is folded into the string's value, so a rung that folds the same bytes but finds a different terminator cannot produce the same checksum: `h ^ (slen as u64)` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the walk starts at the first byte after the header: `p = 4;` in both C rungs.
  - `rust` — the walk starts at the first byte after the header: `let mut p: usize = 4;` in all four Rust rungs.
- **required** — *per language:*
  - `c` — a string whose terminator is missing is the last string in the window: `if (q >= len)` in both C rungs.
  - `rust` — a string whose terminator is missing is the last string in the window: `if q >= len {` in all four Rust rungs. This line is also what makes `p = q + 1` provably overflow-free -- see verus.rs's header comment -- so it is required rather than conventional.
- **required** — *per language:*
  - `c` — the cursor steps PAST the terminator: `p = q + 1;` in both C rungs.
  - `rust` — the cursor steps PAST the terminator: `p = q + 1;` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the walk is bounded by the WINDOW and never by the declared count: `if (p >= len)` in both C rungs. `nstr` appears in no loop bound in any rung.
  - `rust` — the walk is bounded by the WINDOW and never by the declared count: `if p >= len {` in all four Rust rungs. `nstr` appears in no loop bound in any rung.
- **required** — *per language:*
  - `c` — the SCAN is bounded by the window in the hardened cell: `memchr(buf + off + p, 0, len - p)` in c/kernel_hardened.c. c/kernel.c bounds it by the SENTINEL instead (`strlen`) and that one expression is the whole difference, which IS the bug -- so the one scoped-absent audit pair this declaration reports is on that rung and is correct.
  - `rust` — the SCAN is bounded by the window: `while q < len` in safe_naive.rs, unsafe.rs and verus.rs. safe_tuned.rs bounds it by handing `CStr::from_bytes_until_nul` a reslice `&w[p..]` of known length, which is the same bound expressed by the type rather than by a comparison, and is why this entry's Rust spelling scopes to three rungs and not four.
- **required** — the little-endian u32 header decode is written out with + and * rather than | and <<, so it stays linear arithmetic: `+ 65536 *` in all six rungs.
- **required** — ...and its top byte: `+ 16777216 *` in all six rungs.
- **required** — *per language:*
  - `c` — the declared count is folded, so a rung that walks a different number of strings cannot produce the same checksum either: `acc * 31 + (uint64_t)nstr` in both C rungs.
  - `rust` — the declared count is folded, so a rung that walks a different number of strings cannot produce the same checksum either: `.wrapping_add(nstr as u64)` in all four Rust rungs.
- **FORBIDDEN** — `chunks_exact`
- **FORBIDDEN** — `from_le_bytes`
- **FORBIDDEN** — `split`
- **FORBIDDEN** — `strtok`

> **Why**: each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). THE SCAN AND THE FOLD ARE TWO LOOPS AND `slen` IS MATERIALISED BETWEEN THEM: fusing them (`while (b != 0) h = h*31 + b;`) deletes the pattern outright -- the length would never exist as a value, `h ^ slen` could not be the fold, and the `strlen`/`memchr`/`from_bytes_until_nul` idiom that R1, R1h and R3 each reach in their own library would be foreclosed in all three. That the split SURVIVES -O3 is measured rather than assumed (NOTES.md 1): `asm.backward_branches` counts 2 loops in c-gcc (its scan is a `call strlen@plt`), 3 in c-clang, 4 in c-gcc-h, 3 in c-clang-h, 3 in safe_naive, 3 in safe_tuned and 5 in unsafe, against a deliberately fused control at 2 with its fold inside its scan. `chunks_exact` is forbidden for the fold because p16 measured that the chunk width moves that pattern's per-byte rate over a 31% range (5.04688...6.62500, `.memory/01-ladder.md`), and p11's whole published quantity is a decomposition into a per-scanned-byte rate and a per-folded-byte rate -- a chunked fold would move one of the two axes by more than the difference being reported. `from_le_bytes` deletes the written-out little-endian header decode every rung shares AND is NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW), so a rung using it would compare a safe cell against an unsafe cell that cannot exist -- the `identity`-pin trap this block's own `identity` key sets. `split` and `strtok` delete the explicit cursor `p = q + 1`, and with it the behaviour `adversarial-zerotail.bin` exists to show, namely that the walk is bounded by the terminator and by `p >= len` and never by `nstr`. WHAT IS DELIBERATELY *NOT* PINNED, and it is the point of the pattern: **the scan itself**. R1 spells it `strlen`, R1h `memchr`, R2/R4/R5 an indexed byte loop and R3 `CStr::from_bytes_until_nul`, and holding those fixed would be holding fixed the one thing p11 exists to compare. What is pinned instead is that the scan is BOUNDED BY THE WINDOW in five of the six rungs and by the sentinel in the sixth, which is the bug. The declaration was written BEFORE any cell was measured -- the R5 proof and the checksums existed, no `Ir` and no `ns` did -- which is the one thing TASK_018's standard cannot retrofit onto p01, p02, p05, p08, p16 or p17. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p11-nul-scan.json`, contract `277a725a25ab`.

`37` backticked spelling(s) over `6` rung(s) → **114** (spelling, rung) pair(s), **78** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 8 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 0 spelling(s) pin nothing**, 12 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - absent — `.iter().fold(` (required[1], rust, **safe_naive.rs**)
  - absent — `.iter().fold(` (required[1], rust, **unsafe.rs**)
  - absent — `.iter().fold(` (required[1], rust, **verus.rs**)
  - absent — `memchr(buf + off + p, 0, len - p)` (required[7], c, **c/kernel.c**)
  - absent — `strlen` (required[7], c, **c/kernel_hardened.c**)
  - absent — `while q < len` (required[7], rust, **safe_tuned.rs**)
  - absent — `CStr::from_bytes_until_nul` (required[7], rust, **safe_naive.rs**)
  - absent — `CStr::from_bytes_until_nul` (required[7], rust, **unsafe.rs**)
  - absent — `CStr::from_bytes_until_nul` (required[7], rust, **verus.rs**)
  - absent — `&w[p..]` (required[7], rust, **safe_naive.rs**)
  - absent — `&w[p..]` (required[7], rust, **unsafe.rs**)
  - absent — `&w[p..]` (required[7], rust, **verus.rs**)
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
| c-gcc | 81 | 79 | 0 | 279 | 75,276,000 | 50,985,000 | 90,056 | 22,556 | `a7be7589` | `a7be7589` | yes | - |
| c-clang | 104 | 101 | 1 | 331 | 68,250,004 | 37,668,004 | 84,059 | 21,059 | `b57fccc3` | `7d4506a0` | yes | - |
| safe_naive | 117 | 113 | 2 | 414 | 147,348,000 | 118,872,000 | 84,275 | 21,275 | `ac055b33` | `1d0750ae` | yes | - |
| safe_tuned | 134 | 129 | 10 | 486 | 79,812,000 | 38,485,500 | 84,275 | 21,275 | `87d0dd7f` | `1f24bb67` | yes | - |
| unsafe | 123 | 117 | 3 | 429 | 114,420,000 | 75,240,000 | 84,275 | 21,275 | `9145e570` | `2aa0a49f` | yes | - |
| verus | 123 | 117 | 3 | 429 | 114,420,000 | 75,240,000 | 78,274 | 19,774 | `9145e570` | `2aa0a49f` | yes | - |
| c-gcc-h | 104 | 101 | 0 | 364 | 82,482,000 | 51,478,500 | 90,056 | 22,556 | `eb88c3fd` | `eb88c3fd` | yes | - |
| c-clang-h | 113 | 110 | 1 | 363 | 76,566,004 | 38,221,504 | 84,059 | 21,059 | `3ea10de7` | `22efb7db` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 121 | 119 | 0 | 444 | 150,240,000 | - | 216,066 | - | `94e283b9` | `94e283b9` | yes | - |
| c-clang | 98 | 98 | 1 | 395 | 125,208,004 | - | 126,056 | - | `1e8ae67f` | `8899779a` | yes | - |
| safe_naive | 171 | 171 | 7 | 905 | 285,576,000 | - | 150,077 | - | `efb2a59d` | `ad617c59` | yes | - |
| safe_tuned | 202 | 202 | 9 | 1,031 | 241,800,000 | - | 150,077 | - | `ea06ef73` | `8c20636e` | yes | - |
| unsafe | 135 | 135 | 0 | 656 | 258,846,000 | - | 150,077 | - | `b6f13a77` | `b6f13a77` | yes | - |
| verus | 135 | 135 | 0 | 656 | 258,846,000 | - | 150,056 | - | `b442d77f` | `b442d77f` | yes | - |
| c-gcc-h | 134 | 132 | 0 | 491 | 161,040,000 | - | 216,066 | - | `aa228592` | `aa228592` | yes | - |
| c-clang-h | 108 | 108 | 2 | 437 | 131,508,004 | - | 126,056 | - | `53588939` | `72c14808` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 293 | 291 | 2 | 1,169 | - | - | 73,464,129 | 50,859,129 | `90344124` | `ff335795` | yes | - |
| c-clang | 315 | 310 | 0 | 1,180 | - | - | 69,162,184 | 37,785,184 | `765d3efb` | `765d3efb` | yes | xmm |
| safe_naive | 745 | 735 | 1 | 3,279 | - | - | 151,770,279 | 124,897,779 | `3f5abc1b` | `dbad3411` | yes | xmm |
| safe_tuned | 767 | 755 | 1 | 3,407 | - | - | 79,074,276 | 38,412,276 | `019b4b86` | `284ea550` | yes | xmm |
| unsafe | 764 | 751 | 1 | 3,407 | - | - | 135,162,278 | 89,688,278 | `af1afd20` | `c857ad55` | yes | xmm |
| verus | 759 | 747 | 1 | 3,311 | - | - | 132,198,274 | 89,439,274 | `aa1f87c6` | `39c58946` | yes | xmm |
| c-gcc-h | 325 | 321 | 2 | 1,299 | - | - | 81,600,133 | 51,421,633 | `dc769a57` | `811afb16` | yes | - |
| c-clang-h | 323 | 318 | 0 | 1,196 | - | - | 76,362,184 | 38,277,184 | `31207bf3` | `31207bf3` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 150,240,000 | - | 216,066 | - | `438a5c29` | `438a5c29` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 122,520,004 | - | 126,055 | - | `aeb34402` | `aeb34402` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 285,576,000 | - | 150,077 | - | `af66996d` | `c1fb584f` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 241,800,000 | - | 150,077 | - | `d728a43c` | `5dd5676d` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 258,846,000 | - | 150,077 | - | `53d4194a` | `84dfa276` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 258,846,000 | - | 150,056 | - | `38f684e2` | `4d43518b` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 161,040,000 | - | 216,066 | - | `2d1a7f52` | `2d1a7f52` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 129,708,004 | - | 126,055 | - | `8933e7bc` | `8933e7bc` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 135/135 vs 135/135 | 0 B vs 0 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 123/117 vs 123/117 | 3 B vs 3 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 31 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 12.15 | 12.56 | 3.4% | 13.41 | 13.84 | 3.2% |
| c-gcc | whole | 12.20 | 12.52 | 2.6% | 13.83 | 14.27 | 3.2% |
| c-clang | isolated | 12.20 | 12.47 | 2.3% | 10.38 | 10.63 | 2.4% |
| c-clang | whole | 12.27 | 12.45 | 1.5% | 11.18 | 11.39 | 1.9% |
| safe_naive | isolated | 16.03 | 16.33 | 1.8% | 16.65 | 16.90 | 1.5% |
| safe_naive | whole | 16.22 | 16.47 | 1.5% | 16.80 | 16.99 | 1.1% |
| safe_tuned | isolated | 13.76 | 14.03 | 2.0% | 19.61 | 19.85 | 1.3% |
| safe_tuned | whole | 13.76 | 13.92 | 1.1% | 18.33 | 18.73 | 2.2% |
| unsafe | isolated | 15.04 | 15.31 | 1.8% | 15.89 | 16.37 | 3.0% |
| unsafe | whole | 15.86 | 16.12 | 1.6% | 17.38 | 17.75 | 2.1% |
| verus | isolated | 15.05 | 15.28 | 1.6% | 15.97 | 16.37 | 2.5% |
| verus | whole | 15.75 | 16.12 | 2.3% | 15.82 | 16.11 | 1.8% |
| c-gcc-h | isolated | 12.22 | 12.42 | 1.6% | 13.75 | 14.13 | 2.8% |
| c-gcc-h | whole | 12.24 | 12.45 | 1.7% | 13.93 | 14.18 | 1.8% |
| c-clang-h | isolated | 12.22 | 12.53 | 2.5% | 11.19 | 11.36 | 1.5% |
| c-clang-h | whole | 12.26 | 12.52 | 2.1% | 11.05 | 11.41 | 3.3% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
