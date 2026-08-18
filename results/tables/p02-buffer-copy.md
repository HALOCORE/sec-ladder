# p02-buffer-copy — results

Generated 2026-08-17T18:00:05Z from `results/p02-buffer-copy.json` (git `712ca8501b8b`).

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
| adversarial-cap.bin | 8 | 12,556 | 12,556 | False | n_iters=8 cap=64 stride=66 n_src=12540 nrec=190 calls=8 work/call=64B san=clean truncated=False cap_bad=False expected=244239563421568 |
| adversarial-cap1.bin | 8 | 12,612 | 12,612 | False | n_iters=8 cap=64 stride=67 n_src=12596 nrec=188 calls=8 work/call=0B san=fires truncated=False cap_bad=False expected=0 |
| adversarial-capbig.bin | 8 | 520 | 520 | False | n_iters=8 cap=1099511627776 stride=63 n_src=504 nrec=0 calls=0 work/call=0B san=clean truncated=False cap_bad=True expected=None |
| adversarial-shortlen.bin | 8 | 4,616 | 520 | True | n_iters=8 cap=64 stride=63 n_src=504 nrec=0 calls=0 work/call=0B san=clean truncated=True cap_bad=False expected=None |
| adversarial-srcend.bin | 8 | 56 | 56 | False | n_iters=8 cap=64 stride=40 n_src=40 nrec=1 calls=8 work/call=0B san=fires truncated=False cap_bad=False expected=0 |
| adversarial-stride1.bin | 8 | 80 | 80 | False | n_iters=8 cap=64 stride=1 n_src=64 nrec=0 calls=0 work/call=0B san=clean truncated=False cap_bad=False expected=0 |
| adversarial.bin | 8 | 12,616 | 12,616 | False | n_iters=8 cap=64 stride=63 n_src=12600 nrec=200 calls=8 work/call=0B san=fires truncated=False cap_bad=False expected=0 |
| large.bin | 20,000 | 8,384,528 | 8,384,528 | False | n_iters=20000 cap=4096 stride=4094 n_src=8384512 nrec=2048 calls=20000 work/call=4092B san=clean truncated=False cap_bad=False expected=4856715052625337940 |
| small.bin | 200,000 | 12,616 | 12,616 | False | n_iters=200000 cap=64 stride=63 n_src=12600 nrec=200 calls=200000 work/call=61B san=clean truncated=False cap_bad=False expected=15997819096698035934 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — the fit check is subtraction-first -- `len > src_len - (src_off + 2)` -- spelled identically in every rung that HAS one. R1 (`c/kernel.c`) has no fit check at all: it casts `src_len` and `dst_cap` to `(void)` and that omission IS the bug this pattern models. R1h is R1 plus the three-term check `len > dst_cap || len > src_len - (src_off + 2)` and nothing else
- **required** — the u16 prefix is decoded with `+`, not `|`
- **required** — the result is folded over dst AFTER the copy, not over src
- **required** — the kernel is total in len: all 65536 values a u16 prefix can express are handled -- in every rung EXCEPT R1, which is defined only for the values that happen to fit and overruns `dst` for the rest. R1's partiality is the CWE-787 the pattern exists to exhibit (ASan fires on `adversarial-overrun.bin`, NOTES.md 1); do not 'fix' it
- **required** — R2 copies index-by-index; R3 reslices both sides once and copies with copy_from_slice
- **FORBIDDEN** — the additive check `src_off + 2 + len > src_len`

> **Why**: the additive form can overflow size_t and wave the attack through, so it is the spelling this pattern exists to reject. The `+` decode and the `|` decode are the same function and lower to the same instruction; `+` is chosen because it needs no bit-vector reasoning in R5, which is a cheaper PROOF and not a weaker specification. Folding dst after the copy is what stops the copy being dead code. The last required entry is the one that already cost this pattern a retraction and must not be quietly 'fixed': R2's index-by-index copy is why rustc never forms a memcpy there, one operator flips `bulk_calls []` to `['memcpy@GLIBC_2.14']` and 118 kernel instructions to 87, and that difference was 100% of R2's retracted delta (NOTES.md 3a). Swapping a bulk copy into R2, or an indexed copy into R3, deletes p02's only decomposition and its finding with it. RESTATED in this hashed block at TASK_016 from the 'Four things about that are load-bearing' prose above -- restated, not moved: the prose is still there, says the same thing, and THIS block is the authoritative copy of it (TASK_016_REVIEW m2). Whoever edits one edits the other. TASK_016 did not measure a spelling spread for p02 and none is claimed here. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes. Where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies. That clause was MEASURED, not granted: without it a literal reading puts EIGHT SHIPPED CELLS out of their own contract -- p02's four Rust rungs (`len > src.len() - (src_off + 2)`, where the entry says `src_len` and the Rust signature has no `src_len` to say) and p08's four Rust rungs (`let dr: usize = d + r;`, where the entry says `dr = d + r`) -- and no cell source may change. A difference the language does NOT force is not covered by that clause: Rust can write `let end: i64 = content_len;`, and four shipped p17 rungs do. An entry that names a rung pins that rung only, and an entry may carve a rung out (p05's second entry, p16's fourth, p17's third). WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle. WHAT THE STANDARD DOES NOT BUY, measured at TASK_018 and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call and p17's by 51 Ir/call flat, so `R3ship - R4ship` is an UPPER BOUND on the in-contract safety tax and never the tax itself. Every pattern owes an in-contract spelling spread beside its headline; p16 and p17 have one from TASK_018 (their NOTES.md 10a), p01, p02, p05 and p08 do not.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried. Use the `isolated` kernel-exclusive figure, which needs no correction.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 153 | 150 | 0 | 593 | 40,400,000 | 175,300,000 | 3,200,064 | 320,064 | `41231363` | `41231363` | yes | xmm |
| c-clang | 66 | 64 | 2 | 213 | 38,600,000 | 195,280,000 | 3,200,069 | 320,069 | `14046564` | `75e65627` | yes | - |
| safe_naive | 122 | 118 | 2 | 430 | 78,400,000 | 224,220,000 | 3,000,293 | 300,293 | `3bc4ef75` | `577a2a21` | yes | xmm |
| safe_tuned | 95 | 93 | 3 | 333 | 42,400,000 | 195,660,000 | 3,000,293 | 300,293 | `e207ec6c` | `40438eda` | yes | - |
| unsafe | 72 | 70 | 12 | 228 | 40,200,000 | 195,440,000 | 3,200,295 | 320,295 | `0e5b5936` | `03836d16` | yes | - |
| verus | 72 | 70 | 12 | 228 | 40,200,000 | 195,440,000 | 2,800,291 | 280,291 | `0e5b5936` | `03836d16` | yes | - |
| c-gcc-h | 153 | 151 | 0 | 610 | 41,400,000 | 175,400,000 | 3,200,064 | 320,064 | `2034ed0c` | `2034ed0c` | yes | xmm |
| c-clang-h | 75 | 73 | 2 | 244 | 41,000,000 | 195,520,000 | 3,200,069 | 320,069 | `ca37a0e5` | `8bf12e31` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 48 | 48 | 0 | 176 | 130,200,000 | - | 7,600,077 | - | `f85e9034` | `f85e9034` | yes | - |
| c-clang | 41 | 41 | 1 | 159 | 153,000,000 | - | 4,400,067 | - | `e5333d17` | `7fc6e63e` | yes | - |
| safe_naive | 127 | 127 | 11 | 629 | 598,600,000 | - | 5,400,093 | - | `afe5bb09` | `befd4fec` | yes | - |
| safe_tuned | 102 | 102 | 3 | 461 | 291,200,000 | - | 5,400,093 | - | `3789e442` | `159c1182` | NO | - |
| unsafe | 72 | 72 | 8 | 328 | 243,400,000 | - | 5,400,093 | - | `5c0d4e0b` | `65039c37` | yes | - |
| verus | 72 | 72 | 8 | 328 | 243,400,000 | - | 5,400,072 | - | `b0e44091` | `a9315683` | yes | - |
| c-gcc-h | 58 | 58 | 0 | 211 | 131,800,000 | - | 7,600,077 | - | `2f28d8ef` | `2f28d8ef` | yes | - |
| c-clang-h | 55 | 55 | 2 | 211 | 155,400,000 | - | 4,400,067 | - | `8013b441` | `03a914e8` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 389 | 386 | 1 | 1,615 | - | - | 41,400,144 | 175,400,144 | `48a696cc` | `1869bfc1` | yes | xmm |
| c-clang | 308 | 304 | 0 | 1,220 | - | - | 38,800,194 | 195,300,194 | `6c31a6d7` | `6c31a6d7` | yes | xmm |
| safe_naive | 807 | 797 | 1 | 3,551 | - | - | 54,600,295 | 214,400,295 | `813623bc` | `9bf79e99` | yes | xmm |
| safe_tuned | 794 | 786 | 1 | 3,599 | - | - | 43,000,301 | 195,720,301 | `8ab88893` | `78a0766d` | yes | xmm |
| unsafe | 764 | 756 | 1 | 3,471 | - | - | 40,800,302 | 195,500,302 | `e48553cb` | `07ab9351` | yes | xmm |
| verus | 785 | 778 | 1 | 3,503 | - | - | 40,800,298 | 195,500,298 | `4f229736` | `3df51e1a` | yes | xmm |
| c-gcc-h | 403 | 399 | 1 | 1,662 | - | - | 44,000,145 | 175,660,145 | `0e53ac29` | `4cb9ea42` | yes | xmm |
| c-clang-h | 341 | 338 | 0 | 1,371 | - | - | 41,800,202 | 195,600,202 | `321a866a` | `321a866a` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 113 | 113 | 0 | 520 | 130,200,000 | - | 7,600,077 | - | `d5eca909` | `d5eca909` | yes | - |
| c-clang | 78 | 78 | 0 | 345 | 153,000,000 | - | 4,400,066 | - | `8a0fa704` | `8a0fa704` | yes | - |
| safe_naive | 149 | 149 | 2 | 766 | 598,600,000 | - | 5,400,093 | - | `cac1218c` | `9cedf5b8` | yes | xmm |
| safe_tuned | 149 | 149 | 2 | 766 | 291,200,000 | - | 5,400,093 | - | `d3396e1c` | `5b91340a` | yes | xmm |
| unsafe | 149 | 149 | 2 | 766 | 243,400,000 | - | 5,400,093 | - | `af955bce` | `625545fe` | yes | xmm |
| verus | 112 | 112 | 12 | 580 | 243,400,000 | - | 5,400,072 | - | `8869f0e9` | `2bcc6a63` | yes | xmm |
| c-gcc-h | 113 | 113 | 0 | 520 | 131,800,000 | - | 7,600,077 | - | `ef7d1484` | `ef7d1484` | yes | - |
| c-clang-h | 78 | 78 | 0 | 345 | 155,400,000 | - | 4,400,066 | - | `6bf51041` | `6bf51041` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 72/72 vs 72/72 | 8 B vs 8 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 72/70 vs 72/70 | 12 B vs 12 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 30.97 | 31.30 | 1.1% | 7.56 | 8.06 | 6.6% |
| c-gcc | whole | 31.00 | 31.33 | 1.1% | 7.50 | 7.96 | 6.1% |
| c-clang | isolated | 25.19 | 25.46 | 1.1% | 5.97 | 6.24 | 4.6% |
| c-clang | whole | 25.27 | 25.49 | 0.9% | 5.99 | 6.20 | 3.6% |
| safe_naive | isolated | 25.85 | 26.15 | 1.1% | 7.59 | 7.93 | 4.4% |
| safe_naive | whole | 25.56 | 25.96 | 1.6% | 6.43 | 6.63 | 3.2% |
| safe_tuned | isolated | 25.47 | 25.71 | 0.9% | 6.42 | 6.65 | 3.6% |
| safe_tuned | whole | 25.45 | 25.75 | 1.2% | 6.42 | 6.70 | 4.4% |
| unsafe | isolated | 25.40 | 25.77 | 1.4% | 6.43 | 6.78 | 5.5% |
| unsafe | whole | 25.33 | 25.68 | 1.4% | 6.50 | 6.88 | 5.8% |
| verus | isolated | 25.53 | 25.71 | 0.7% | 6.51 | 6.87 | 5.4% |
| verus | whole | 25.41 | 25.66 | 1.0% | 6.57 | 6.89 | 4.8% |
| c-gcc-h | isolated | 30.90 | 31.34 | 1.4% | 7.56 | 7.82 | 3.4% |
| c-gcc-h | whole | 31.05 | 31.45 | 1.3% | 7.59 | 7.77 | 2.3% |
| c-clang-h | isolated | 25.18 | 25.49 | 1.2% | 6.06 | 6.32 | 4.2% |
| c-clang-h | whole | 25.22 | 25.55 | 1.3% | 6.04 | 6.34 | 5.1% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
