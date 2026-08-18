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
- **required** — the guard is the one conjunctive `if start < end && start >= 0 { ... }`, not two `continue`s
- **required** — R1 omits only `&& start >= 0` -- it keeps `len < 2` and `2 + 2*nsuf > len`
- **required** — nserved is folded into the result
- **FORBIDDEN** — unsigned start/end
- **FORBIDDEN** — `Range:` text parsing -- the fields are bytes, not ASCII
- **FORBIDDEN** — a window-relative sign guard where a slice-relative one is meant, and vice versa

> **Why**: making start unsigned deletes the CVE: `start < 0` becomes unrepresentable and the leak row of the semantics table could not exist. ASCII parsing adds a second new variable (string parsing is p11-p15). The `continue` spelling is not expressible in Verus ('for-loops do not yet support continue') and the while workaround hoists the increment above the guard in all six rungs. The last forbidden entry is the one that already cost this pattern a retraction: `start >= -(body_start as i64)` and `start >= -((off + body_start) as i64)` differ by one token, both verify, and only the second is what a bounds check buys -- see NOTES.md 1c. RESTATED in this hashed block at TASK_016 from the prose section 'Load-bearing, do not improve' above -- restated, not moved: the prose is still there, says the same thing, and THIS block is the authoritative copy of it (TASK_016_REVIEW m2). Whoever edits one edits the other. Note what is NOT restricted: the R2/R3/R4 spelling of the byte fold and of the suffix-table walk. NOTES.md 10 tabulates three measured spellings; the cheapest safe one is 17 Ir per suffix below the shipped R3, so p17's published R3 number is a spelling's number under this declaration, and it is a matched pair only against the R4 it ships beside.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried. Use the `isolated` kernel-exclusive figure, which needs no correction.

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
