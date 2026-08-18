# p05-index-flatten — results

Generated 2026-08-17T20:26:54Z from `results/p05-index-flatten.json` (git `9d5c810bcc50`, working tree dirty).

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
| adversarial-dims.bin | 8 | 76 | 76 | False | n_iters=8 stride=68 n_blob=68 nwin=1 calls=8 work/call=68B san=fires truncated=False expected=0 |
| adversarial-ovf.bin | 8 | 80 | 80 | False | n_iters=8 stride=72 n_blob=72 nwin=1 calls=8 work/call=72B san=fires truncated=False expected=0 |
| adversarial-stride3.bin | 8 | 80 | 80 | False | n_iters=8 stride=3 n_blob=72 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| adversarial-zero.bin | 8 | 76 | 76 | False | n_iters=8 stride=68 n_blob=68 nwin=1 calls=8 work/call=68B san=clean truncated=False expected=0 |
| large.bin | 12,000 | 8,394,443 | 8,394,443 | False | n_iters=12000 stride=3969 n_blob=8394435 nwin=2115 calls=12000 work/call=3969B san=clean truncated=False expected=9972956928725141114 |
| small.bin | 25,000 | 15,944 | 15,944 | False | n_iters=25000 stride=498 n_blob=15936 nwin=32 calls=25000 work/call=498B san=clean truncated=False expected=1506433241298462329 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — i*ncol + j written out in every rung, not strength-reduced
- **required** — R3 may reslice [base .. base+ncol] with base = off + 4 + i*ncol -- that moves the CHECK and keeps the MULTIPLY, and it is the most a rung may do
- **required** — the fit check is nrow * ncol > avail in 64-bit; row is a u32 accumulator and acc a u64
- **required** — nrow * ncol is folded into the result, so a rung that walks a different number of elements cannot produce the same checksum even if the bytes happened to fold the same way
- **FORBIDDEN** — chunks_exact
- **FORBIDDEN** — a running row pointer

> **Why**: either deletes the flattened index, which IS the pattern; a rung that does it is a different benchmark and its numbers are not comparable (this file's second sentence). RESTATED in this hashed block at TASK_016 from the prose section 'Load-bearing, do not improve' above, where contract_sha256 could not see it -- restated, not moved: the prose is still there and THIS block is the authoritative copy of it (TASK_016_REVIEW m2), and the copies had already drifted, the 'nrow * ncol is folded into the result' entry having been dropped on the day the block landed and restored at TASK_017 (m1). The declaration itself was made at TASK_013 BEFORE any of these spellings were measured, it was right both times it was tested, and two consecutive tasks measured a forbidden spelling anyway and published the result as p05's number (TASK_014_REVIEW B1 measured chunks_exact, TASK_015 measured the running row pointer; neither cited this file). NOTES.md 13 tabulates 11 measured spellings of this kernel with the contract-conformant cell marked -- none of the other ten is a p05 number. The gate checks that this key is present and hashes it; it does NOT check that a rung honours it. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 Ir/call flat and p02's by 3 to 4, so `R3ship - R4ship` is an UPPER BOUND on the in-contract safety tax and never the tax itself. Every pattern owes an in-contract spelling spread beside its headline; p16 and p17 have one from TASK_018 and p02 from TASK_019 (their NOTES.md 10a) and p05 from TASK_021 (its NOTES.md 14, which also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep); p01 and p08 do not.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p05-index-flatten.json`, contract `08d96ff2cb25`.

This declaration backticks **no spelling at all**, so the named-spelling standard's own trigger never fires on this pattern and there is nothing to audit. Its rungs are matched by the entries' English alone.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried. Use the `isolated` kernel-exclusive figure, which needs no correction.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 167 | 163 | 0 | 593 | 43,250,000 | 110,448,000 | 375,056 | 180,056 | `ecf1890a` | `ecf1890a` | yes | xmm |
| c-clang | 86 | 83 | 1 | 301 | 34,175,000 | 101,064,000 | 350,059 | 168,059 | `6a1bed4b` | `14345902` | yes | xmm |
| safe_naive | 168 | 164 | 3 | 653 | 51,675,000 | 135,804,000 | 350,275 | 168,275 | `290d8c70` | `5f6c1095` | yes | xmm |
| safe_tuned | 111 | 107 | 14 | 418 | 37,250,000 | 105,852,000 | 350,275 | 168,275 | `9de0ae49` | `bc7aaf6d` | yes | xmm |
| unsafe | 87 | 83 | 10 | 310 | 34,175,000 | 101,064,000 | 350,275 | 168,275 | `4a28657a` | `71d96f88` | yes | xmm |
| verus | 87 | 83 | 10 | 310 | 34,175,000 | 101,064,000 | 325,274 | 156,274 | `4a28657a` | `71d96f88` | yes | xmm |
| c-gcc-h | 178 | 173 | 0 | 646 | 43,425,000 | 110,532,000 | 375,056 | 180,056 | `0e458546` | `0e458546` | yes | xmm |
| c-clang-h | 91 | 87 | 1 | 310 | 34,225,000 | 101,088,000 | 350,059 | 168,059 | `b8c0b866` | `16742943` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 94 | 94 | 0 | 348 | 220,025,000 | - | 900,066 | - | `dbc62c63` | `dbc62c63` | yes | - |
| c-clang | 78 | 78 | 1 | 313 | 231,050,000 | - | 525,056 | - | `dde7717c` | `aab58d8c` | yes | - |
| safe_naive | 160 | 160 | 6 | 778 | 348,450,000 | - | 625,077 | - | `3a0f3262` | `1ea26ceb` | yes | - |
| safe_tuned | 176 | 176 | 0 | 832 | 308,800,000 | - | 625,077 | - | `476d289d` | `476d289d` | yes | - |
| unsafe | 117 | 117 | 10 | 534 | 306,375,000 | - | 625,077 | - | `a3fc07d5` | `b182413b` | yes | - |
| verus | 117 | 117 | 10 | 534 | 306,375,000 | - | 625,056 | - | `ce67fabc` | `2d7edbec` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 373 | 220,125,000 | - | 900,066 | - | `bcd531ad` | `bcd531ad` | yes | - |
| c-clang-h | 84 | 84 | 2 | 341 | 231,150,000 | - | 525,056 | - | `35c76c72` | `4c6152ec` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 382 | 378 | 1 | 1,496 | - | - | 42,775,134 | 109,668,134 | `55f4a692` | `8997e2bb` | yes | xmm |
| c-clang | 318 | 313 | 0 | 1,241 | - | - | 36,275,183 | 104,280,183 | `58ddfc5b` | `58ddfc5b` | yes | xmm |
| safe_naive | 768 | 759 | 1 | 3,439 | - | - | 46,175,280 | 127,092,280 | `7bf450f0` | `5f03f372` | yes | xmm |
| safe_tuned | 741 | 731 | 1 | 3,279 | - | - | 39,275,281 | 109,032,281 | `7f49eb67` | `818d51f7` | yes | xmm |
| unsafe | 725 | 714 | 1 | 3,231 | - | - | 37,750,281 | 108,984,281 | `d3acc1ec` | `dbf1838a` | yes | xmm |
| verus | 732 | 722 | 1 | 3,199 | - | - | 37,750,278 | 108,984,278 | `873b934e` | `7cee6a3b` | yes | xmm |
| c-gcc-h | 387 | 383 | 2 | 1,525 | - | - | 42,825,137 | 109,692,137 | `14934262` | `550c47c6` | yes | xmm |
| c-clang-h | 325 | 319 | 0 | 1,267 | - | - | 36,400,185 | 104,340,185 | `4b668df0` | `4b668df0` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 220,025,000 | - | 900,066 | - | `44b2130a` | `44b2130a` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 231,050,000 | - | 525,055 | - | `c60c668c` | `c60c668c` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 348,450,000 | - | 625,077 | - | `210cd5a8` | `8bc66adc` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 308,800,000 | - | 625,077 | - | `a89169ab` | `f4bf99d7` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 306,375,000 | - | 625,077 | - | `69353964` | `b303801e` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 306,375,000 | - | 625,056 | - | `38f684e2` | `4d43518b` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 220,125,000 | - | 900,066 | - | `9a1e639f` | `9a1e639f` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 231,150,000 | - | 525,055 | - | `895c7d9f` | `895c7d9f` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 117/117 vs 117/117 | 10 B vs 10 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 87/83 vs 87/83 | 10 B vs 10 B |

## Wall clock (secondary)

> taskset -c 5, interleaved round-robin, 31 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 16.59 | 16.81 | 1.3% | 5.71 | 6.84 | **19.9% ✗** |
| c-gcc | whole | 16.47 | 16.77 | 1.8% | 5.99 | 6.76 | **12.9% ✗** |
| c-clang | isolated | 15.87 | 16.10 | 1.5% | 5.29 | 5.79 | 9.4% |
| c-clang | whole | 16.14 | 16.38 | 1.5% | 5.51 | 6.04 | 9.7% |
| safe_naive | isolated | 18.15 | 18.40 | 1.4% | 7.24 | 7.81 | 8.0% |
| safe_naive | whole | 17.91 | 18.16 | 1.4% | 6.57 | 7.21 | 9.8% |
| safe_tuned | isolated | 16.09 | 16.38 | 1.8% | 5.54 | 6.04 | 8.9% |
| safe_tuned | whole | 16.52 | 16.70 | 1.1% | 5.79 | 6.11 | 5.6% |
| unsafe | isolated | 16.04 | 16.35 | 1.9% | 5.32 | 5.75 | 8.0% |
| unsafe | whole | 16.63 | 16.89 | 1.6% | 5.68 | 6.14 | 8.0% |
| verus | isolated | 16.07 | 16.34 | 1.6% | 5.54 | 5.90 | 6.5% |
| verus | whole | 16.69 | 16.86 | 1.0% | 5.84 | 6.33 | 8.3% |
| c-gcc-h | isolated | 16.44 | 16.73 | 1.8% | 6.43 | 6.92 | 7.7% |
| c-gcc-h | whole | 16.48 | 16.80 | 1.9% | 6.24 | 6.70 | 7.4% |
| c-clang-h | isolated | 15.89 | 16.12 | 1.5% | 5.47 | 5.83 | 6.7% |
| c-clang-h | whole | 16.07 | 16.37 | 1.8% | 5.36 | 5.99 | **11.8% ✗** |

**3 of 32 wall-clock cells exceed the 10% min-to-median spread threshold and are DISCARDED** per `.memory/03-measurement.md` step 4. They are printed above marked ✗ rather than deleted, because a missing cell that looks like an omission is worse than a documented failure (`.memory/02-bench-rules.md`). **No claim in this report rests on a marked row.**

- `c-gcc / isolated` on `small.bin`: spread 19.9%
- `c-gcc / whole` on `small.bin`: spread 12.9%
- `c-clang-h / whole` on `small.bin`: spread 11.8%


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
