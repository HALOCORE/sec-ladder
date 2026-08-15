# p02-buffer-copy — results

Generated 2026-08-15T16:58:24Z from `results/p02-buffer-copy.json` (git `273849cbdc3d`, working tree dirty).

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
| adversarial-cap.bin | 8 | 12,556 | 12,556 | False | n_iters=8 cap=64 stride=66 n_src=12540 nrec=190 calls=8 work/call=64w san=clean truncated=False cap_bad=False expected=244239563421568 |
| adversarial-cap1.bin | 8 | 12,612 | 12,612 | False | n_iters=8 cap=64 stride=67 n_src=12596 nrec=188 calls=8 work/call=0w san=fires truncated=False cap_bad=False expected=0 |
| adversarial-capbig.bin | 8 | 520 | 520 | False | n_iters=8 cap=1099511627776 stride=63 n_src=504 nrec=0 calls=0 work/call=0w san=clean truncated=False cap_bad=True expected=None |
| adversarial-shortlen.bin | 8 | 4,616 | 520 | True | n_iters=8 cap=64 stride=63 n_src=504 nrec=0 calls=0 work/call=0w san=clean truncated=True cap_bad=False expected=None |
| adversarial-srcend.bin | 8 | 56 | 56 | False | n_iters=8 cap=64 stride=40 n_src=40 nrec=1 calls=8 work/call=0w san=fires truncated=False cap_bad=False expected=0 |
| adversarial-stride1.bin | 8 | 80 | 80 | False | n_iters=8 cap=64 stride=1 n_src=64 nrec=0 calls=0 work/call=0w san=clean truncated=False cap_bad=False expected=0 |
| adversarial.bin | 8 | 12,616 | 12,616 | False | n_iters=8 cap=64 stride=63 n_src=12600 nrec=200 calls=8 work/call=0w san=fires truncated=False cap_bad=False expected=0 |
| large.bin | 20,000 | 8,384,528 | 8,384,528 | False | n_iters=20000 cap=4096 stride=4094 n_src=8384512 nrec=2048 calls=20000 work/call=4092w san=clean truncated=False cap_bad=False expected=4856715052625337940 |
| small.bin | 200,000 | 12,616 | 12,616 | False | n_iters=200000 cap=64 stride=63 n_src=12600 nrec=200 calls=200000 work/call=61w san=clean truncated=False cap_bad=False expected=15997819096698035934 |

## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried. Use the `isolated` kernel-exclusive figure, which needs no correction.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 153 | 150 | 0 | 593 | 40,400,000 | 175,300,000 | 3,200,064 | 320,064 | `694ccb6f` | `694ccb6f` | yes | xmm |
| c-clang | 66 | 64 | 2 | 213 | 38,600,000 | 195,280,000 | 3,200,069 | 320,069 | `1f6d48cb` | `80d3af53` | yes | - |
| safe_naive | 122 | 118 | 2 | 430 | 78,400,000 | 224,220,000 | 3,000,293 | 300,293 | `3bc4ef75` | `577a2a21` | yes | xmm |
| safe_tuned | 95 | 93 | 3 | 333 | 42,400,000 | 195,660,000 | 3,000,293 | 300,293 | `e207ec6c` | `40438eda` | yes | - |
| unsafe | 72 | 70 | 12 | 228 | 40,200,000 | 195,440,000 | 3,200,295 | 320,295 | `0e5b5936` | `03836d16` | yes | - |
| verus | 72 | 70 | 12 | 228 | 40,200,000 | 195,440,000 | 2,800,291 | 280,291 | `0e5b5936` | `03836d16` | yes | - |
| c-gcc-h | 153 | 151 | 0 | 610 | 41,400,000 | 175,400,000 | 3,200,064 | 320,064 | `29ab725d` | `29ab725d` | yes | xmm |
| c-clang-h | 75 | 73 | 2 | 244 | 41,000,000 | 195,520,000 | 3,200,069 | 320,069 | `6385306f` | `9a4c6f02` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 48 | 48 | 0 | 176 | 130,200,000 | - | 7,600,077 | - | `bc136206` | `bc136206` | yes | - |
| c-clang | 41 | 41 | 1 | 159 | 153,000,000 | - | 4,400,067 | - | `b12484c7` | `7e7d41d5` | yes | - |
| safe_naive | 127 | 127 | 11 | 629 | 598,600,000 | - | 5,400,093 | - | `afe5bb09` | `befd4fec` | yes | - |
| safe_tuned | 102 | 102 | 3 | 461 | 291,200,000 | - | 5,400,093 | - | `3789e442` | `159c1182` | NO | - |
| unsafe | 72 | 72 | 8 | 328 | 243,400,000 | - | 5,400,093 | - | `5c0d4e0b` | `65039c37` | yes | - |
| verus | 72 | 72 | 8 | 328 | 243,400,000 | - | 5,400,072 | - | `b0e44091` | `a9315683` | yes | - |
| c-gcc-h | 58 | 58 | 0 | 211 | 131,800,000 | - | 7,600,077 | - | `3a0a5049` | `3a0a5049` | yes | - |
| c-clang-h | 55 | 55 | 2 | 211 | 155,400,000 | - | 4,400,067 | - | `2ce3a840` | `df642369` | yes | - |

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
| c-gcc | 113 | 113 | 0 | 520 | 130,200,000 | - | 7,600,077 | - | `48402f94` | `48402f94` | yes | - |
| c-clang | 78 | 78 | 0 | 345 | 153,000,000 | - | 4,400,066 | - | `8a0fa704` | `8a0fa704` | yes | - |
| safe_naive | 149 | 149 | 2 | 766 | 598,600,000 | - | 5,400,093 | - | `cac1218c` | `9cedf5b8` | yes | xmm |
| safe_tuned | 149 | 149 | 2 | 766 | 291,200,000 | - | 5,400,093 | - | `d3396e1c` | `5b91340a` | yes | xmm |
| unsafe | 149 | 149 | 2 | 766 | 243,400,000 | - | 5,400,093 | - | `af955bce` | `625545fe` | yes | xmm |
| verus | 112 | 112 | 12 | 580 | 243,400,000 | - | 5,400,072 | - | `8869f0e9` | `2bcc6a63` | yes | xmm |
| c-gcc-h | 113 | 113 | 0 | 520 | 131,800,000 | - | 7,600,077 | - | `2f53f824` | `2f53f824` | yes | - |
| c-clang-h | 78 | 78 | 0 | 345 | 155,400,000 | - | 4,400,066 | - | `6bf51041` | `6bf51041` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 72/72 vs 72/72 | 8 B vs 8 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 72/70 vs 72/70 | 12 B vs 12 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 15 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 30.82 | 31.09 | 0.9% | 7.56 | 7.79 | 3.1% |
| c-gcc | whole | 30.89 | 31.09 | 0.6% | 7.53 | 7.70 | 2.3% |
| c-clang | isolated | 25.02 | 25.28 | 1.1% | 6.09 | 6.33 | 3.8% |
| c-clang | whole | 25.12 | 25.28 | 0.7% | 5.98 | 6.14 | 2.8% |
| safe_naive | isolated | 25.70 | 25.96 | 1.0% | 7.72 | 7.99 | 3.5% |
| safe_naive | whole | 25.47 | 25.74 | 1.1% | 6.34 | 6.74 | 6.4% |
| safe_tuned | isolated | 25.22 | 25.42 | 0.8% | 6.48 | 6.61 | 2.0% |
| safe_tuned | whole | 25.25 | 25.52 | 1.1% | 6.42 | 6.76 | 5.2% |
| unsafe | isolated | 25.34 | 25.56 | 0.9% | 6.67 | 6.97 | 4.5% |
| unsafe | whole | 25.29 | 25.44 | 0.6% | 6.58 | 6.86 | 4.3% |
| verus | isolated | 25.35 | 25.49 | 0.5% | 6.54 | 6.84 | 4.7% |
| verus | whole | 25.27 | 25.40 | 0.5% | 6.80 | 7.08 | 4.2% |
| c-gcc-h | isolated | 30.85 | 31.05 | 0.6% | 7.61 | 7.93 | 4.3% |
| c-gcc-h | whole | 30.73 | 31.05 | 1.0% | 7.55 | 7.67 | 1.6% |
| c-clang-h | isolated | 25.10 | 25.31 | 0.8% | 6.15 | 6.32 | 2.8% |
| c-clang-h | whole | 25.12 | 25.35 | 0.9% | 6.05 | 6.29 | 4.0% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
