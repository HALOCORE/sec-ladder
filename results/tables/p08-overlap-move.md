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
