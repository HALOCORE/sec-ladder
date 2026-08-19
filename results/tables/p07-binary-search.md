# p07-binary-search — results

Generated 2026-08-19T08:28:36Z from `results/p07-binary-search.json` (git `9a5cdb9afd9c`, working tree dirty).

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
| adversarial-count.bin | 8 | 96 | 96 | False | n_iters=8 stride=88 n_blob=88 nwin=1 calls=8 work/call=0probe san=fires truncated=False expected=0 |
| adversarial-stride7.bin | 8 | 64 | 64 | False | n_iters=8 stride=7 n_blob=56 nwin=0 calls=0 work/call=0probe san=clean truncated=False expected=0 |
| adversarial-unsorted.bin | 8 | 1,496 | 1,496 | False | n_iters=8 stride=1488 n_blob=1488 nwin=1 calls=8 work/call=522probe san=clean truncated=False expected=6484670710166908416 |
| adversarial-width.bin | 8 | 96 | 96 | False | n_iters=8 stride=88 n_blob=88 nwin=1 calls=8 work/call=0probe san=fires truncated=False expected=0 |
| adversarial-zero.bin | 8 | 48 | 48 | False | n_iters=8 stride=40 n_blob=40 nwin=1 calls=8 work/call=0probe san=clean truncated=False expected=0 |
| large.bin | 1,200 | 12,587,000 | 12,587,000 | False | n_iters=1200 stride=1048916 n_blob=12586992 nwin=12 calls=1200 work/call=1656probe san=clean truncated=False expected=18361155092924381683 |
| small.bin | 8,000 | 17,864 | 17,864 | False | n_iters=8000 stride=1488 n_blob=17856 nwin=12 calls=8000 work/call=522probe san=clean truncated=False expected=14645905038740535295 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — the midpoint is `lo + (hi - lo) / 2` in all six rungs and in the Verus spec function bsearch. The overflow-safe form; pinning it is what makes forbidden[0] settleable by grep instead of by argument.
- **required** — *per language:*
  - `c` — the search bounds are HALF-OPEN and the upper one is the COUNT, not the last index: `size_t hi = n;`. All six rungs; hi = n - 1 is not an admissible respelling, see why.
  - `rust` — the search bounds are HALF-OPEN and the upper one is the COUNT, not the last index: `let mut hi: usize = n;`. All six rungs; hi = n - 1 is not an admissible respelling, see why.
- **required** — the upper bound is ASSIGNED and never decremented: `hi = mid;` in all six rungs. hi = mid - 1 underflows at mid == 0, which any key below element 0 reaches on WELL-FORMED input.
- **required** — the lower bound moves past the probe: `lo = mid + 1;` in all six rungs.
- **required** — *per language:*
  - `c` — the compare is three-way with an early exit on equality: `if (v == key)` in both C rungs.
  - `rust` — the compare is three-way with an early exit on equality: `if v == key` in all four Rust rungs.
- **required** — *per language:*
  - `c` — and the ordering test that halves the range: `if (v < key)` in both C rungs.
  - `rust` — and the ordering test that halves the range: `if v < key` in all four Rust rungs.
- **required** — *per language:*
  - `c` — the length check is `if (4 * n + 4 * nq > avail)` in 64-bit size_t. Present in five of the six rungs; c/kernel.c omits exactly this line and nothing else, which IS the bug, so the one scoped-absent audit pair this declaration reports is on that rung and is correct.
  - `rust` — the length check is `if 4 * (n as u64) + 4 * (nq as u64) > avail as u64` -- widened to u64 because n and nq are u32 fields and 4*n + 4*nq needs 36 bits. All four Rust rungs.
- **required** — *per language:*
  - `c` — the probe index keeps the multiply and the base: `size_t ep = off + 8 + 4 * mid;` in both C rungs.
  - `rust` — the probe index keeps the multiply and the base: `let ep: usize = off + 8 + 4 * mid;` in all four Rust rungs. R3 may reslice [ep .. ep + 4] -- that moves the CHECK and keeps the INDEX, and it is the most a rung may do.
- **required** — the little-endian u32 decode is written out with + and * rather than | and <<, so it stays linear arithmetic: `+ 65536 *` in all six rungs.
- **required** — ...and its top byte: `+ 16777216 *` in all six rungs.
- **required** — *per language:*
  - `c` — the query result is folded as found + 1, so a rung returning a different index cannot produce the same checksum: `acc * 31 + (found + 1)` in both C rungs.
  - `rust` — the query result is folded as found + 1, so a rung returning a different index cannot produce the same checksum: `wrapping_add(found.wrapping_add(1))` in all four Rust rungs.
- **required** — *per language:*
  - `c` — n * nq is folded, so a rung running a different number of searches cannot produce the same checksum either: `(uint64_t)n * (uint64_t)nq` in both C rungs.
  - `rust` — n * nq is folded, so a rung running a different number of searches cannot produce the same checksum either: `(n as u64).wrapping_mul(nq as u64)` in all four Rust rungs.
- **FORBIDDEN** — `(lo + hi) / 2`
- **FORBIDDEN** — `binary_search`
- **FORBIDDEN** — `partition_point`
- **FORBIDDEN** — `chunks_exact`
- **FORBIDDEN** — `from_le_bytes`

> **Why**: each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). `(lo + hi) / 2` is the spelling `.memory/06-catalogue.md` names as p07's bug and it is forbidden here rather than measured, because NOTES.md 0 shows it is UNREACHABLE at every size this wire format can express: `n` is a u32 header field, so `lo + hi <= 2*(2^32 - 2) = 8589934588`, which is 2.1e9x short of 2^64 -- RAM is not the binding constraint, the field width is. Pinning the safe spelling is what makes the midpoint question settleable by grep instead of by argument, which is the whole point of the standard. `binary_search`, `partition_point`, `chunks_exact` and `from_le_bytes` delete the search or the written-out little-endian decode. `from_le_bytes` and the `try_into` route to it are additionally NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd -- both are `is not supported`, measured on p05 and p16 (TASK_027_REVIEW) -- so a rung using them would compare a safe cell against an unsafe cell that cannot exist, which is the `identity`-pin trap this file's own `identity` key sets. The half-open bounds (`hi = n`, `hi = mid`) are `required` and not merely conventional: the textbook inclusive form underflows `size_t` at `mid == 0`, which any key below element 0 reaches ON WELL-FORMED INPUT, so it is not an admissible respelling of this kernel -- it is a different and broken one, and NOTES.md 6 measures what it does. The declaration was written BEFORE any cell was built or measured, which is the one thing TASK_018's standard cannot retrofit onto p01, p02, p05, p08, p16 or p17. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p07-binary-search.json`, contract `164995db0bac`.

`34` backticked spelling(s) over `6` rung(s) → **102** (spelling, rung) pair(s), **71** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 10 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 0 spelling(s) pin nothing**, 1 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - absent — `if (4 * n + 4 * nq > avail)` (required[6], c, **c/kernel.c**)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried. Use the `isolated` kernel-exclusive figure, which needs no correction.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 105 | 103 | 0 | 359 | 93,127,510 | 45,772,727 | 120,056 | 18,056 | `1314c0f3` | `1314c0f3` | yes | - |
| c-clang | 66 | 65 | 2 | 194 | 48,043,926 | 23,506,615 | 112,059 | 16,859 | `b9803de5` | `59559815` | yes | - |
| safe_naive | 172 | 171 | 4 | 700 | 98,569,648 | 48,106,714 | 112,275 | 17,075 | `b2fb8d1e` | `a1f1d8e5` | yes | - |
| safe_tuned | 99 | 97 | 10 | 326 | 76,614,958 | 37,653,579 | 112,275 | 17,075 | `de8111c4` | `09a16ff4` | yes | - |
| unsafe | 66 | 64 | 4 | 188 | 52,498,130 | 25,623,657 | 112,275 | 17,075 | `4f8c4436` | `2047737e` | yes | - |
| verus | 66 | 64 | 4 | 188 | 52,498,130 | 25,623,657 | 104,274 | 15,874 | `4f8c4436` | `2047737e` | yes | - |
| c-gcc-h | 115 | 112 | 0 | 404 | 93,183,510 | 45,781,127 | 120,056 | 18,056 | `f02d00b5` | `f02d00b5` | yes | - |
| c-clang-h | 71 | 70 | 2 | 209 | 48,083,926 | 23,512,615 | 112,059 | 16,859 | `645a5e63` | `2732ce8d` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 217 | 217 | 0 | 785 | 234,558,538 | - | 288,066 | - | `1c21f89f` | `1c21f89f` | yes | - |
| c-clang | 163 | 163 | 1 | 666 | 183,228,882 | - | 168,056 | - | `3c989b90` | `03f6766b` | yes | - |
| safe_naive | 369 | 369 | 4 | 2,012 | 295,943,798 | - | 200,077 | - | `526e1ff9` | `57789600` | yes | - |
| safe_tuned | 414 | 414 | 3 | 2,125 | 337,549,178 | - | 200,077 | - | `c1ae1d3d` | `080dcf29` | yes | - |
| unsafe | 271 | 271 | 10 | 1,446 | 279,871,246 | - | 200,077 | - | `83dc9f60` | `3bc8b12b` | yes | - |
| verus | 271 | 271 | 10 | 1,446 | 279,871,246 | - | 200,056 | - | `756c91d3` | `550edc55` | yes | - |
| c-gcc-h | 225 | 225 | 0 | 816 | 234,606,538 | - | 288,066 | - | `fe3c9a1c` | `fe3c9a1c` | yes | - |
| c-clang-h | 172 | 172 | 0 | 704 | 183,284,882 | - | 168,056 | - | `7eb369b1` | `7eb369b1` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 319 | 316 | 1 | 1,273 | - | - | 93,607,639 | 45,885,656 | `4314f4dd` | `d87db396` | yes | - |
| c-clang | 291 | 288 | 0 | 1,113 | - | - | 48,108,106 | 23,516,395 | `da0c8754` | `da0c8754` | yes | xmm |
| safe_naive | 800 | 791 | 1 | 3,551 | - | - | 98,601,926 | 48,111,792 | `239f4ed1` | `34d46d32` | yes | xmm |
| safe_tuned | 723 | 715 | 1 | 3,199 | - | - | 80,801,376 | 39,697,446 | `af957788` | `bb07b978` | yes | xmm |
| unsafe | 698 | 690 | 1 | 3,023 | - | - | 52,554,410 | 25,632,337 | `275c9222` | `511c9288` | yes | xmm |
| verus | 706 | 697 | 1 | 3,039 | - | - | 52,562,407 | 25,633,534 | `4f0a6ad9` | `706062ca` | yes | xmm |
| c-gcc-h | 329 | 324 | 1 | 1,304 | - | - | 93,647,643 | 45,891,660 | `96a1bd23` | `eda0607b` | yes | - |
| c-clang-h | 297 | 293 | 0 | 1,113 | - | - | 48,140,108 | 23,521,197 | `9cde72e3` | `9cde72e3` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 234,558,538 | - | 288,066 | - | `ea2cc697` | `ea2cc697` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 183,460,882 | - | 168,055 | - | `a59b3c78` | `a59b3c78` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 295,943,798 | - | 200,077 | - | `f9f487e3` | `dd2a7e92` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 337,549,178 | - | 200,077 | - | `2a3c720d` | `e25e1924` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 279,871,246 | - | 200,077 | - | `99184eaf` | `c5d4a761` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 279,871,246 | - | 200,056 | - | `38f684e2` | `4d43518b` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 234,606,538 | - | 288,066 | - | `aa65a6c3` | `aa65a6c3` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 183,516,882 | - | 168,055 | - | `8e0e5fca` | `8e0e5fca` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 271/271 vs 271/271 | 10 B vs 10 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 66/64 vs 66/64 | 4 B vs 4 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 25.46 | 25.82 | 1.4% | 21.04 | 21.30 | 1.2% |
| c-gcc | whole | 25.27 | 25.53 | 1.0% | 19.36 | 19.57 | 1.1% |
| c-clang | isolated | 21.54 | 21.74 | 0.9% | 14.80 | 15.13 | 2.3% |
| c-clang | whole | 20.83 | 21.05 | 1.0% | 11.34 | 11.64 | 2.7% |
| safe_naive | isolated | 22.54 | 22.86 | 1.4% | 17.72 | 17.90 | 1.0% |
| safe_naive | whole | 22.21 | 22.49 | 1.3% | 16.78 | 17.03 | 1.5% |
| safe_tuned | isolated | 22.12 | 22.31 | 0.9% | 15.64 | 15.84 | 1.3% |
| safe_tuned | whole | 22.31 | 22.57 | 1.2% | 16.37 | 16.66 | 1.8% |
| unsafe | isolated | 21.77 | 22.08 | 1.4% | 13.85 | 14.09 | 1.7% |
| unsafe | whole | 21.76 | 22.07 | 1.4% | 14.01 | 14.26 | 1.8% |
| verus | isolated | 21.85 | 22.04 | 0.9% | 13.84 | 14.10 | 1.8% |
| verus | whole | 21.57 | 21.89 | 1.5% | 13.88 | 14.05 | 1.2% |
| c-gcc-h | isolated | 25.41 | 25.64 | 0.9% | 20.49 | 20.69 | 1.0% |
| c-gcc-h | whole | 25.13 | 25.58 | 1.8% | 19.71 | 19.88 | 0.9% |
| c-clang-h | isolated | 21.19 | 21.39 | 0.9% | 12.16 | 12.46 | 2.4% |
| c-clang-h | whole | 21.09 | 21.37 | 1.3% | 12.21 | 12.43 | 1.8% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
