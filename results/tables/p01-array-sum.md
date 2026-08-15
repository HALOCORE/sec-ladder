# p01-array-sum — results

Generated 2026-08-15T12:30:02Z from `results/p01-array-sum.json` (git `3e6ad8f77eb1`, working tree dirty).

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

| file | n_iters | declared payload | present | win_len | v_len | truncated |
|---|---:|---:|---:|---:|---:|---|
| adversarial-empty.bin | 1,000 | 0 | 0 | 0 | 0 | False |
| adversarial-headonly.bin | 1,000 | 8 | 8 | 8 | 0 | False |
| adversarial-shortlen.bin | 1,000 | 4,096 | 40 | 4 | 4 | True |
| adversarial-win0.bin | 1,000 | 520 | 520 | 0 | 64 | False |
| adversarial-winbig.bin | 1,000 | 520 | 520 | 1,099,511,627,776 | 64 | False |
| adversarial.bin | 0 | 520 | 520 | 8 | 64 | False |
| large.bin | 20,000 | 12,000,008 | 12,000,008 | 4,096 | 1,500,000 | False |
| small.bin | 200,000 | 16,008 | 16,008 | 501 | 2,000 | False |

## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

An `Ir` marked `*` is `main`-exclusive, not kernel-exclusive: the kernel was inlined and has no symbol left. **Read those rows with care.** `main`-exclusive counts whatever else was inlined into `main`, and that is not the same set in every language: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (visible as the `isolated` `main`-exclusive figures in the JSON: ~12.36 M vs ~0.38 M). So a starred row is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row. Subtract the same cell's `isolated` `main` figure first if you need the inlined kernel's cost.

### O3 / isolated — symbol: `kernel`

| rung | static raw | static pad-excl | sym bytes | Ir small | Ir large | md5_raw | md5_norel | loop | vec |
|---|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 33 | 31 | 105 | 254,400,000 | 205,180,000 | `d2209fca` | `35ff8090` | yes | xmm |
| c-clang | 38 | 35 | 128 | 180,000,000 | 143,740,000 | `c9ad71e5` | `e8ce0110` | yes | xmm |
| safe_naive | 59 | 47 | 192 | 182,400,000 | 144,320,000 | `6c85987d` | `09823d2b` | yes | xmm |
| safe_tuned | 58 | 44 | 192 | 181,000,000 | 143,840,000 | `d1ee09f5` | `547f4822` | yes | xmm |
| unsafe | 39 | 34 | 144 | 180,200,000 | 143,740,000 | `fb90a96c` | `f37ab80b` | yes | xmm |
| verus | 39 | 34 | 144 | 180,200,000 | 143,740,000 | `fb90a96c` | `f37ab80b` | yes | xmm |
| safe_naive_verus | 59 | 47 | 192 | 182,400,000 | 144,320,000 | `6c85987d` | `09823d2b` | yes | xmm |

### O0 / isolated — symbol: `kernel`

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | static raw | static pad-excl | sym bytes | Ir small | Ir large | md5_raw | md5_norel | loop | vec |
|---|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 24 | 24 | 92 | 1,205,400,000 | - | `f33177c4` | `8df8a232` | yes | - |
| c-clang | 24 | 23 | 96 | 1,305,200,000 | - | `8025a602` | `305b7568` | yes | - |
| safe_naive | 46 | 42 | 192 | 2,108,600,000 | - | `e68a5b96` | `f0a161f2` | yes | - |
| safe_tuned | 83 | 69 | 288 | 2,116,800,000 | - | `18c96051` | `0593c9a9` | yes | - |
| unsafe | 48 | 36 | 176 | 2,008,400,000 | - | `38891af3` | `0f0060ce` | yes | - |
| verus | 48 | 36 | 176 | 2,008,400,000 | - | `6c5b3ca2` | `0f0060ce` | yes | - |
| safe_naive_verus | 46 | 42 | 192 | 2,108,600,000 | - | `e68a5b96` | `f0a161f2` | yes | - |

### O3 / whole — symbol: `main (kernel inlined)`

| rung | static raw | static pad-excl | sym bytes | Ir small | Ir large | md5_raw | md5_norel | loop | vec |
|---|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 226 | 222 | 896 | 255,000,109 * | 205,260,109 * | `d29a72c7` | `3fe8c7d8` | yes | xmm |
| c-clang | 213 | 209 | 838 | 183,000,127 * | 144,000,127 * | `133526c6` | `a7ac98bc` | yes | xmm |
| safe_naive | 728 | 717 | 3,152 | 186,624,291 * | 162,800,291 * | `486961f0` | `1fd3c264` | yes | xmm |
| safe_tuned | 712 | 701 | 3,072 | 183,816,286 * | 156,080,286 * | `1ed3505f` | `e01dbb50` | yes | xmm |
| unsafe | 700 | 690 | 3,024 | 183,216,286 * | 155,980,286 * | `f84ba3a7` | `32b4f6c2` | yes | xmm |
| verus | 697 | 686 | 3,056 | 183,016,285 * | 155,960,285 * | `86bbb0ac` | `6b0def94` | yes | xmm |
| safe_naive_verus | 708 | 697 | 3,136 | 185,216,288 * | 156,660,288 * | `0b2951db` | `d6a9f18d` | yes | xmm |

### O0 / whole — symbol: `main (kernel inlined)`

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | static raw | static pad-excl | sym bytes | Ir small | Ir large | md5_raw | md5_norel | loop | vec |
|---|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 85 | 85 | 347 | 1,205,400,000 | - | `907e1d80` | `328bcd20` | yes | - |
| c-clang | 65 | 65 | 269 | 1,305,200,000 | - | `909271db` | `7adb28c7` | yes | - |
| safe_naive | 129 | 125 | 640 | 2,108,600,000 | - | `e0f2cccc` | `022902d5` | yes | xmm |
| safe_tuned | 129 | 125 | 640 | 2,116,800,000 | - | `c3a33e91` | `022902d5` | yes | xmm |
| unsafe | 129 | 125 | 640 | 2,008,400,000 | - | `b6d4deb8` | `022902d5` | yes | xmm |
| verus | 102 | 88 | 448 | 2,008,400,000 | - | `d74471d2` | `bad9b7e5` | yes | xmm |
| safe_naive_verus | 102 | 88 | 448 | 2,108,600,000 | - | `91d0be77` | `bad9b7e5` | yes | xmm |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol. `md5_raw` is bit-exact machine code; `md5_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest oracle when two binaries link the kernel's callees at different addresses (that happens at `O0`, where the Rust kernel still calls `Iterator::next`).

| pair | opt | md5_raw equal | md5_norel equal | raw counts |
|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | 48/36 vs 48/36 |
| unsafe vs verus | O3 | **yes** | **yes** | 39/34 vs 39/34 |
| safe_naive vs safe_naive_verus | O0 | **yes** | **yes** | 46/42 vs 46/42 |
| safe_naive vs safe_naive_verus | O3 | **yes** | **yes** | 59/47 vs 59/47 |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | small.bin min (ms) | small.bin median (ms) |
|---|---|---:|---:|---:|---:|
| c-gcc | isolated | 36.85 | 41.07 | 26.27 | 28.86 |
| c-gcc | whole | 37.61 | 41.48 | 26.00 | 29.74 |
| c-clang | isolated | 37.31 | 41.37 | 16.12 | 19.33 |
| c-clang | whole | 37.18 | 39.98 | 16.84 | 19.74 |
| safe_naive | isolated | 37.96 | 42.63 | 17.34 | 21.37 |
| safe_naive | whole | 37.95 | 41.10 | 17.15 | 20.23 |
| safe_tuned | isolated | 37.86 | 40.84 | 17.19 | 19.70 |
| safe_tuned | whole | 37.90 | 40.50 | 16.50 | 20.06 |
| unsafe | isolated | 37.94 | 41.61 | 16.87 | 20.03 |
| unsafe | whole | 37.76 | 41.57 | 16.32 | 20.18 |
| verus | isolated | 37.71 | 40.99 | 17.57 | 20.06 |
| verus | whole | 37.49 | 40.94 | 16.15 | 20.34 |
| safe_naive_verus | isolated | 37.64 | 40.31 | 17.48 | 20.44 |
| safe_naive_verus | whole | 37.71 | 40.18 | 16.42 | 18.28 |

## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
