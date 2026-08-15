# p01-array-sum — results

Generated 2026-08-15T16:01:11Z from `results/p01-array-sum.json` (git `19e3f6c9e001`, working tree dirty).

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
| c-gcc | 33 | 31 | 0 | 105 | 254,400,000 | 205,180,000 | 2,800,052 | 280,052 | `d2209fca` | `d2209fca` | yes | xmm |
| c-clang | 37 | 35 | 1 | 125 | 180,000,000 | 143,740,000 | 2,600,052 | 260,052 | `cb7ad6f3` | `c9ad71e5` | yes | xmm |
| safe_naive | 49 | 47 | 10 | 182 | 182,400,000 | 144,320,000 | 2,616,286 | 12,260,286 | `12d307f2` | `f1e7f951` | yes | xmm |
| safe_tuned | 46 | 44 | 12 | 180 | 181,000,000 | 143,840,000 | 2,616,286 | 12,260,286 | `499ab455` | `9eb333b2` | yes | xmm |
| unsafe | 36 | 34 | 3 | 141 | 180,200,000 | 143,740,000 | 2,616,286 | 12,260,286 | `619b1d1b` | `fb90a96c` | yes | xmm |
| verus | 36 | 34 | 3 | 141 | 180,200,000 | 143,740,000 | 2,416,291 | 12,240,291 | `619b1d1b` | `fb90a96c` | yes | xmm |
| safe_naive_verus | 49 | 47 | 10 | 182 | 182,400,000 | 144,320,000 | 2,616,287 | 12,260,287 | `12d307f2` | `f1e7f951` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 24 | 24 | 0 | 92 | 1,205,400,000 | - | 6,800,066 | - | `f33177c4` | `f33177c4` | yes | - |
| c-clang | 23 | 23 | 1 | 86 | 1,305,200,000 | - | 3,800,055 | - | `de6279c5` | `8025a602` | yes | - |
| safe_naive | 42 | 42 | 4 | 188 | 2,108,600,000 | - | 4,800,073 | - | `bf555ac4` | `32dd86ab` | yes | - |
| safe_tuned | 69 | 69 | 14 | 274 | 2,116,800,000 | - | 4,800,073 | - | `33f80521` | `7e1d442f` | yes | - |
| unsafe | 36 | 36 | 12 | 164 | 2,008,400,000 | - | 4,800,073 | - | `78b8c557` | `5abf0ea1` | yes | - |
| verus | 36 | 36 | 12 | 164 | 2,008,400,000 | - | 4,800,052 | - | `a5bbe0c0` | `7a961606` | yes | - |
| safe_naive_verus | 42 | 42 | 4 | 188 | 2,108,600,000 | - | 4,800,052 | - | `bf555ac4` | `32dd86ab` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 256 | 255 | 1 | 1,014 | - | - | 254,800,133 | 205,240,133 | `7ef08e5f` | `0aff704c` | yes | xmm |
| c-clang | 242 | 239 | 0 | 962 | - | - | 181,400,169 | 143,880,169 | `06d2a24e` | `06d2a24e` | yes | xmm |
| safe_naive | 712 | 703 | 1 | 3,135 | - | - | 185,622,294 | 161,140,294 | `c64c96b6` | `43e25b00` | yes | xmm |
| safe_tuned | 689 | 680 | 1 | 3,007 | - | - | 182,416,289 | 155,940,289 | `5625249a` | `c7c834d1` | yes | xmm |
| unsafe | 687 | 677 | 1 | 3,007 | - | - | 181,616,289 | 155,840,289 | `40f1f18f` | `3cab7870` | yes | xmm |
| verus | 684 | 674 | 1 | 2,991 | - | - | 181,616,288 | 155,840,288 | `893735f0` | `c3b956f7` | yes | xmm |
| safe_naive_verus | 697 | 688 | 1 | 3,087 | - | - | 183,816,290 | 156,460,290 | `53ee383a` | `3658d4e1` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 98 | 98 | 0 | 411 | 1,205,400,000 | - | 6,800,066 | - | `3374cc79` | `3374cc79` | yes | - |
| c-clang | 65 | 65 | 0 | 270 | 1,305,200,000 | - | 3,800,055 | - | `77f37e64` | `77f37e64` | yes | - |
| safe_naive | 113 | 113 | 2 | 574 | 2,108,600,000 | - | 4,800,073 | - | `0cc27eb0` | `1d0eea59` | yes | xmm |
| safe_tuned | 113 | 113 | 2 | 574 | 2,116,800,000 | - | 4,800,073 | - | `9bef66b4` | `954b18e1` | yes | xmm |
| unsafe | 113 | 113 | 2 | 574 | 2,008,400,000 | - | 4,800,073 | - | `14ea0864` | `87e8cfc5` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 2,008,400,000 | - | 4,800,052 | - | `d78a5de2` | `6369b1eb` | yes | - |
| safe_naive_verus | 86 | 86 | 7 | 329 | 2,108,600,000 | - | 4,800,052 | - | `73b40249` | `255954b4` | yes | - |

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
| c-gcc | isolated | 37.51 | 38.10 | 1.6% | 24.51 | 24.77 | 1.1% |
| c-gcc | whole | 38.29 | 38.68 | 1.0% | 24.60 | 24.85 | 1.0% |
| c-clang | isolated | 37.77 | 38.11 | 0.9% | 15.08 | 15.31 | 1.5% |
| c-clang | whole | 37.71 | 38.15 | 1.2% | 15.96 | 16.17 | 1.4% |
| safe_naive | isolated | 38.51 | 38.92 | 1.1% | 16.11 | 16.26 | 0.9% |
| safe_naive | whole | 38.58 | 38.98 | 1.0% | 15.92 | 16.22 | 1.8% |
| safe_tuned | isolated | 38.46 | 38.83 | 1.0% | 15.97 | 16.16 | 1.2% |
| safe_tuned | whole | 38.10 | 38.76 | 1.7% | 15.82 | 16.01 | 1.2% |
| unsafe | isolated | 38.51 | 38.88 | 0.9% | 15.36 | 15.58 | 1.5% |
| unsafe | whole | 38.44 | 38.83 | 1.0% | 16.05 | 16.38 | 2.0% |
| verus | isolated | 38.31 | 38.72 | 1.1% | 15.40 | 15.61 | 1.4% |
| verus | whole | 38.14 | 38.71 | 1.5% | 16.02 | 16.34 | 2.0% |
| safe_naive_verus | isolated | 38.23 | 38.71 | 1.3% | 15.02 | 15.20 | 1.2% |
| safe_naive_verus | whole | 38.26 | 38.70 | 1.2% | 16.06 | 16.33 | 1.7% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
