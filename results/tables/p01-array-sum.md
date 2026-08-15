# p01-array-sum — results

Generated 2026-08-15T14:13:25Z from `results/p01-array-sum.json` (git `5cd4d340e644`, working tree dirty).

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

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried. Use the `isolated` kernel-exclusive figure, which needs no correction.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 33 | 31 | 0 | 105 | 254,400,000 | 205,180,000 | 3,000,052 | 300,052 | `d2209fca` | `d2209fca` | yes | xmm |
| c-clang | 37 | 35 | 1 | 125 | 180,000,000 | 143,740,000 | 3,800,048 | 380,048 | `cb7ad6f3` | `c9ad71e5` | yes | xmm |
| safe_naive | 49 | 47 | 10 | 182 | 182,400,000 | 144,320,000 | 3,816,284 | 12,380,284 | `f8e1fe32` | `6c85987d` | yes | xmm |
| safe_tuned | 46 | 44 | 12 | 180 | 181,000,000 | 143,840,000 | 3,816,284 | 12,380,284 | `af2d4c0a` | `d1ee09f5` | yes | xmm |
| unsafe | 36 | 34 | 3 | 141 | 180,200,000 | 143,740,000 | 3,616,285 | 12,360,285 | `619b1d1b` | `fb90a96c` | yes | xmm |
| verus | 36 | 34 | 3 | 141 | 180,200,000 | 143,740,000 | 3,616,286 | 12,360,286 | `619b1d1b` | `fb90a96c` | yes | xmm |
| safe_naive_verus | 49 | 47 | 10 | 182 | 182,400,000 | 144,320,000 | 3,816,285 | 12,380,285 | `f8e1fe32` | `6c85987d` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 24 | 24 | 0 | 92 | 1,205,400,000 | - | 4,600,064 | - | `f33177c4` | `f33177c4` | yes | - |
| c-clang | 23 | 23 | 1 | 86 | 1,305,200,000 | - | 4,000,055 | - | `de6279c5` | `8025a602` | yes | - |
| safe_naive | 42 | 42 | 4 | 188 | 2,108,600,000 | - | 6,200,073 | - | `3ab6079d` | `e68a5b96` | yes | - |
| safe_tuned | 69 | 69 | 14 | 274 | 2,116,800,000 | - | 6,200,073 | - | `05c1a4fe` | `18c96051` | yes | - |
| unsafe | 36 | 36 | 12 | 164 | 2,008,400,000 | - | 6,200,073 | - | `1dffc20c` | `38891af3` | yes | - |
| verus | 36 | 36 | 12 | 164 | 2,008,400,000 | - | 6,200,052 | - | `779a1133` | `6c5b3ca2` | yes | - |
| safe_naive_verus | 42 | 42 | 4 | 188 | 2,108,600,000 | - | 6,200,052 | - | `3ab6079d` | `e68a5b96` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 259 | 257 | 0 | 1,024 | - | - | 255,000,134 | 205,260,134 | `c87b764f` | `c87b764f` | yes | xmm |
| c-clang | 253 | 249 | 0 | 1,010 | - | - | 183,000,166 | 144,000,166 | `164677c0` | `164677c0` | yes | xmm |
| safe_naive | 727 | 717 | 1 | 3,151 | - | - | 186,624,291 | 162,800,291 | `e58bb012` | `486961f0` | yes | xmm |
| safe_tuned | 711 | 701 | 1 | 3,071 | - | - | 183,816,286 | 156,080,286 | `aefc040c` | `1ed3505f` | yes | xmm |
| unsafe | 699 | 690 | 1 | 3,023 | - | - | 183,216,286 | 155,980,286 | `3119981f` | `f84ba3a7` | yes | xmm |
| verus | 696 | 686 | 1 | 3,055 | - | - | 183,016,285 | 155,960,285 | `85d6e419` | `86bbb0ac` | yes | xmm |
| safe_naive_verus | 707 | 697 | 1 | 3,135 | - | - | 185,216,288 | 156,660,288 | `16f5d251` | `0b2951db` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 85 | 85 | 0 | 347 | 1,205,400,000 | - | 4,600,064 | - | `3a7ee833` | `3a7ee833` | yes | - |
| c-clang | 65 | 65 | 0 | 269 | 1,305,200,000 | - | 3,800,055 | - | `ad425aa4` | `ad425aa4` | yes | - |
| safe_naive | 125 | 125 | 4 | 636 | 2,108,600,000 | - | 6,200,073 | - | `f5131744` | `e0f2cccc` | yes | xmm |
| safe_tuned | 125 | 125 | 4 | 636 | 2,116,800,000 | - | 6,200,073 | - | `64f574b6` | `c3a33e91` | yes | xmm |
| unsafe | 125 | 125 | 4 | 636 | 2,008,400,000 | - | 6,200,073 | - | `98cb4fcb` | `b6d4deb8` | yes | xmm |
| verus | 88 | 88 | 14 | 434 | 2,008,400,000 | - | 6,200,052 | - | `506b9992` | `d74471d2` | yes | xmm |
| safe_naive_verus | 88 | 88 | 14 | 434 | 2,108,600,000 | - | 6,200,052 | - | `74a83eb0` | `91d0be77` | yes | xmm |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 36/36 vs 36/36 | 12 B vs 12 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 36/34 vs 36/34 | 3 B vs 3 B |
| safe_naive vs safe_naive_verus | O0 | **yes** | **yes** | **yes** | 42/42 vs 42/42 | 4 B vs 4 B |
| safe_naive vs safe_naive_verus | O3 | **yes** | **yes** | **yes** | 49/47 vs 49/47 | 10 B vs 10 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 35.84 | 36.13 | 0.8% | 25.70 | 26.08 | 1.5% |
| c-gcc | whole | 36.52 | 36.86 | 0.9% | 25.65 | 26.10 | 1.8% |
| c-clang | isolated | 35.94 | 36.39 | 1.3% | 15.99 | 16.26 | 1.7% |
| c-clang | whole | 35.99 | 36.35 | 1.0% | 16.65 | 16.89 | 1.4% |
| safe_naive | isolated | 36.82 | 37.09 | 0.7% | 16.98 | 17.32 | 2.0% |
| safe_naive | whole | 36.86 | 37.14 | 0.8% | 16.90 | 17.09 | 1.2% |
| safe_tuned | isolated | 36.72 | 37.05 | 0.9% | 16.98 | 17.20 | 1.3% |
| safe_tuned | whole | 36.70 | 36.99 | 0.8% | 16.13 | 16.35 | 1.3% |
| unsafe | isolated | 36.62 | 37.07 | 1.2% | 16.20 | 16.94 | 4.6% |
| unsafe | whole | 36.75 | 37.03 | 0.8% | 15.98 | 16.42 | 2.8% |
| verus | isolated | 36.72 | 37.16 | 1.2% | 17.16 | 17.71 | 3.2% |
| verus | whole | 36.56 | 36.91 | 1.0% | 16.03 | 16.42 | 2.5% |
| safe_naive_verus | isolated | 36.57 | 36.93 | 1.0% | 17.32 | 17.59 | 1.6% |
| safe_naive_verus | whole | 36.48 | 36.75 | 0.7% | 16.19 | 16.47 | 1.7% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
