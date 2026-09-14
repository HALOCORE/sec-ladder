# TASK_PHP_050 — REPORT · **ITEM 112 SWEPT AND ANSWERED BY MEASUREMENT**, F109 / F107 / F96 behind it

**Role:** research reviewer, alone. **Job: falsify.**

---

## 0. BRACKETS — first and last

| | first (before any work) | last (after everything) |
|---|---|---|
| `python3 harness/measure.py --check-stale` | **`66 record(s) examined, 0 STALE`** | ✅ **`66 record(s) examined, 0 STALE`** |
| `python3 harness-php/gate.py --tool measure --check-stale` | **`20 record(s) examined, 0 STALE`** | ✅ **`20 record(s) examined, 0 STALE`** |

✅ **BOTH UNMOVED.**

**Nothing I did could move either.** I ran no gate, no measure and no re-measure.
Everything I measured ran **already-built binaries** out of
`.temp/php-scratch/build/<row>/` and wrote **only** under `.temp/php50/`.
`git status --short patterns-php/` was **clean** after the one section that
compiles anything (§5.1).

---

## 1. ⭐⭐⭐ THE HEADLINE — **ITEM 112 IS ANSWERED: THE ARTEFACT IS REAL, IT IS ON MORE ROWS THAN ANYONE KNEW, AND IT DOES NOT TOUCH `ph64`**

> ### ⛔ **`ph64`'s `R1h − R1` FIGURES ARE NOT AN ALIGNMENT ARTEFACT. MEASURED, NOT ARGUED.**
> Over a **full 32-byte period** (32 pads × 8 cells × 2 inputs × 2 iteration
> counts = **1 024 callgrind runs**), **every one of `ph64`'s family-B cells is
> invariant to the hundredth**, and every value reproduces
> `results-php/gate/ph64-callback-frees-cursor.json` **exactly**.
> **The measured step on `ph64` is `0.00 Ir/call` on all eight cells.**
>
> ### ✅ **AND THE INSTRUMENT IS NOT DEAD — `ph55` IS THE POSITIVE CONTROL AND IT FIRES.**
> The same sweep on `ph55` measures **exactly `7.00 Ir/call`** on `c-clang` and
> `c-clang-h`, **`0.00` on the other six cells**, with a **32-byte period, a
> window exactly 16 wide, and a phase that differs per binary** — which is the
> PAT-side model reproducing, in family B, on a row nobody had measured it on.

⭐⭐ **AND THE SWEEP FOUND A SECOND EXPOSED ROW NOBODY SUSPECTED.**
**`ph45`'s FOUR RUST cells all step by `7.00 Ir/call`** while its four C cells
step by `0.00` — **the exact mirror of `ph55`**, where the C cells move and the
Rust cells do not. ⛔ **And `ph45`'s four Rust cells do not share a phase**, so
`safe_tuned → unsafe` and `unsafe → verus` each have a sweep range of
**`14.00 Ir/call`**, which is §1.3's two-unequal-phases case occurring in real
data rather than in a synthetic test. ⓘ Both remain **RESOLVABLE** — the medians
are `+1 623.89` and `+106.25` — and **`ph45` publishes in A1 + W1, not in family
B**, so no published figure is affected. ▶ **But "only `ph55` is exposed" was
false, and the sweep is the only reason anyone knows.**

⭐ **So item 112's premise was right, its worry was aimed at the wrong row, and
its scope was too small.** Over the **complete corpus — all ten rows, both
inputs, 32 pads, `-O3 isolated`, 5 120 callgrind runs** — the sweep flags
**4 of 180 family-B differences**, and **every one of them is on `ph55` or
`ph07`.** ⛔ **None is on `ph64`.**

| exposed cell | step | row publishes family B? |
|---|---:|---|
| `ph55` `c-clang`, `c-clang-h` (both inputs) | `7.00` | **yes** |
| `ph45` `safe_naive`, `safe_tuned`, `unsafe`, `verus` (both inputs) | `7.00` | no |
| ⛔ `ph07` `verus` (`small.bin`) | **`34.49`** | no |
| `ph29` `safe_tuned`, `unsafe`, `verus` (`large.bin` only) | `0.02` | no |
| `ph07` `safe_tuned`, `unsafe`, `verus` (`large.bin` only) | `0.02` | no |
| everything else — **`ph00` `ph03` `ph16` `ph52` `ph53` `ph64` entirely** | `0.00` | — |

⭐⭐ **THE ONE ROW THAT PUBLISHES FAMILY B *AND* HAS AN EXPOSED CELL IS `ph55`,
AND `ph55` IS THE ROW THAT ALREADY CAUGHT IT AND ALREADY REFUSES TO QUOTE THE
FIGURE.** ▶ **No published family-B number in this corpus is wrong.**

### 1.0 What family B actually is, and why the artefact survives into it

`results-php/gate/<row>.json → marginal_ir_per_call` is
`(Ir@200 − Ir@100) / dcalls`, from `harness/check.py::check_marginal_ir`, which
calls `_callgrind_total` twice on probe files written by `_probe_input`.

⭐⭐ **THE MECHANISM, STATED AS A FACT ABOUT `check.py` AND NOT AS A GUESS.**
The two probe files are `probe.<input>.100.bin` and `probe.<input>.200.bin` —
**the same length, 23 characters, on all ten rows** (I extracted `probe_iters`
from every `patterns-php/ph*/spec.md`: all ten are `[100, 200]`). Both halves of
the slope therefore run with the **same argv length**, hence the **same stack
alignment**, so the alignment term is **identical in both runs and cancels from
the FIXED part while surviving in full in the PER-CALL part**.
`harness/check.py::_callgrind_total`'s own docstring says exactly this:

> *"The **PER-CALL** part does not cancel, and this docstring used to say 'every
> one of those terms cancels'… a kernel that `memset`s a stack array pays an
> alignment-dependent cost **per call**, and that term scales with the call count
> and therefore survives the subtraction. Measured across **four** patterns at
> **7 Ir/call**."*

▶ **So item 112's premise is sound and is already documented on the PAT side.**
What was missing was any measurement of *which php cells are exposed*.

### 1.1 ⭐ THE SWEEP TABLE — every row, every cell, with `|Δ| / step`

**Method.** `.tasks-php/php50_align_sweep.py` (new, §9). For each row it rebuilds
`check.py`'s own probe files, pads the **argv path** by `0…31` bytes, runs
`callgrind` on the already-built `-O3 isolated` binary at 100 and 200 iterations,
and divides by `dcalls` taken from **the row's own `model.py`**. It reproduces
the committed `marginal_ir_per_call` to the hundredth wherever I checked
(`ph64` all 8 cells × 2 inputs; `ph52` `c-gcc` `5833.79` / `c-gcc-h` `5813.39`;
`ph55` `c-gcc→c-gcc-h` `−20.07` / `−66.14`, which is `TASK_PHP_048_REPORT.md`
§3c's published pair).

⚠ **THE STEP IS MEASURED PER ROW AND PER CELL AND IS NEVER BORROWED.**
`ph55`'s `7.0029` is not assumed to transfer, and the table says `0.00` where
nothing moved rather than `UNTESTED` — because a **full 32-residue** sweep *is*
the complete detector (§1.3), so a `0.00` here is a measurement and not a gap.

#### Per-CELL measured step (Ir/call), -O3 isolated, 32 pads = a full 32-byte period

| row / input | pub B? | c-gcc | c-gcc-h | c-clang | c-clang-h | safe_naive | safe_tuned | unsafe | verus |
|---|---|---|---|---|---|---|---|---|---|
| `ph00-smoke/large.bin` | no | 0.00 | n/a | 0.00 | n/a | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph00-smoke/small.bin` | no | 0.00 | n/a | 0.00 | n/a | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph03-uudecode-bound/large.bin` | no | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph03-uudecode-bound/small.bin` | no | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph07-strcut-cursor/large.bin` | no | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.02** | **0.02** | **0.02** |
| `ph07-strcut-cursor/small.bin` | no | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **34.49** |
| `ph16-fdset-index/large.bin` | no | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph16-fdset-index/small.bin` | no | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph29-recvfrom-alloc/large.bin` | no | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.02** | **0.02** | **0.02** |
| `ph29-recvfrom-alloc/small.bin` | no | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph45-htmlent-cache-int/large.bin` | no | 0.00 | 0.00 | 0.00 | 0.00 | **7.00** | **7.00** | **7.00** | **7.00** |
| `ph45-htmlent-cache-int/small.bin` | no | 0.00 | 0.00 | 0.00 | 0.00 | **7.00** | **7.00** | **7.00** | **7.00** |
| `ph52-concat-copy-uninit/large.bin` | **yes** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph52-concat-copy-uninit/small.bin` | **yes** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph53-iface-tail-uninit/large.bin` | **yes** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph53-iface-tail-uninit/small.bin` | **yes** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph55-opdata-stride/large.bin` | **yes** | 0.00 | 0.00 | **7.00** | **7.00** | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph55-opdata-stride/small.bin` | **yes** | 0.00 | 0.00 | **7.00** | **7.00** | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph64-callback-frees-cursor/large.bin` | **yes** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `ph64-callback-frees-cursor/small.bin` | **yes** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

#### Every family-B difference, against its OWN measured step

| row / input | pair | median Ir/call | sweep range | `|d|/step` | magnitude | sign |
|---|---|---:|---:|---:|---|---|
| `ph00-smoke/large.bin` | `safe_naive->safe_tuned` | -24.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph00-smoke/large.bin` | `safe_tuned->unsafe` | -5.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph00-smoke/large.bin` | `unsafe->verus` | -1.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph00-smoke/small.bin` | `safe_naive->safe_tuned` | -7.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph00-smoke/small.bin` | `safe_tuned->unsafe` | -4.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph00-smoke/small.bin` | `unsafe->verus` | -1.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/large.bin` | `c-clang->c-clang-h` | 199.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/large.bin` | `c-clang-h->safe_tuned` | 13871.97 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/large.bin` | `c-clang-h->unsafe` | 7795.97 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/large.bin` | `c-gcc->c-gcc-h` | -202.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/large.bin` | `c-gcc-h->safe_tuned` | 6405.97 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/large.bin` | `c-gcc-h->unsafe` | 329.97 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/large.bin` | `safe_naive->safe_tuned` | -12659.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/large.bin` | `safe_tuned->unsafe` | -6076.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/large.bin` | `unsafe->verus` | -31.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/small.bin` | `c-clang->c-clang-h` | 28.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/small.bin` | `c-clang-h->safe_tuned` | 1697.19 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/small.bin` | `c-clang-h->unsafe` | 866.36 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/small.bin` | `c-gcc->c-gcc-h` | -31.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/small.bin` | `c-gcc-h->safe_tuned` | 627.02 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/small.bin` | `c-gcc-h->unsafe` | -203.81 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/small.bin` | `safe_naive->safe_tuned` | -1715.39 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/small.bin` | `safe_tuned->unsafe` | -830.83 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph03-uudecode-bound/small.bin` | `unsafe->verus` | 266.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/large.bin` | `c-clang->c-clang-h` | 6.11 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/large.bin` | `c-clang-h->safe_tuned` | 1428.76 | 0.02 | 71438.00 | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/large.bin` | `c-clang-h->unsafe` | -103.03 | 0.02 | 5151.50 | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/large.bin` | `c-gcc->c-gcc-h` | 3.05 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/large.bin` | `c-gcc-h->safe_tuned` | -1508.13 | 0.02 | 75406.50 | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/large.bin` | `c-gcc-h->unsafe` | -3039.92 | 0.02 | 151996.00 | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/large.bin` | `safe_naive->safe_tuned` | -5741.05 | 0.02 | 287052.50 | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/large.bin` | `safe_tuned->unsafe` | -1531.79 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/large.bin` | `unsafe->verus` | 0.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-ZERO |
| `ph07-strcut-cursor/small.bin` | `c-clang->c-clang-h` | 6.19 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/small.bin` | `c-clang-h->safe_tuned` | 299.86 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/small.bin` | `c-clang-h->unsafe` | 101.08 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/small.bin` | `c-gcc->c-gcc-h` | 2.85 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/small.bin` | `c-gcc-h->safe_tuned` | -130.41 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/small.bin` | `c-gcc-h->unsafe` | -329.19 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/small.bin` | `safe_naive->safe_tuned` | -934.07 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/small.bin` | `safe_tuned->unsafe` | -198.78 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph07-strcut-cursor/small.bin` | `unsafe->verus` | 71.83 | 34.49 | 2.08 ⛔ | NOT RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/large.bin` | `c-clang->c-clang-h` | 1889.97 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/large.bin` | `c-clang-h->safe_tuned` | -3118.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/large.bin` | `c-clang-h->unsafe` | -2630.53 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/large.bin` | `c-gcc->c-gcc-h` | 2995.82 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/large.bin` | `c-gcc-h->safe_tuned` | -4007.21 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/large.bin` | `c-gcc-h->unsafe` | -3519.74 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/large.bin` | `safe_naive->safe_tuned` | -9711.28 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/large.bin` | `safe_tuned->unsafe` | 487.47 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/large.bin` | `unsafe->verus` | 0.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-ZERO |
| `ph16-fdset-index/small.bin` | `c-clang->c-clang-h` | 208.88 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/small.bin` | `c-clang-h->safe_tuned` | -273.28 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/small.bin` | `c-clang-h->unsafe` | -229.49 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/small.bin` | `c-gcc->c-gcc-h` | 401.72 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/small.bin` | `c-gcc-h->safe_tuned` | -529.97 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/small.bin` | `c-gcc-h->unsafe` | -486.18 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/small.bin` | `safe_naive->safe_tuned` | -1134.10 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/small.bin` | `safe_tuned->unsafe` | 43.79 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph16-fdset-index/small.bin` | `unsafe->verus` | 0.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-ZERO |
| `ph29-recvfrom-alloc/large.bin` | `c-clang->c-clang-h` | -2.54 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/large.bin` | `c-clang-h->safe_tuned` | 2216.00 | 0.02 | 110800.00 | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/large.bin` | `c-clang-h->unsafe` | 2690.16 | 0.02 | 134508.00 | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/large.bin` | `c-gcc->c-gcc-h` | 2.16 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/large.bin` | `c-gcc-h->safe_tuned` | -717.02 | 0.02 | 35851.00 | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/large.bin` | `c-gcc-h->unsafe` | -242.86 | 0.02 | 12143.00 | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/large.bin` | `safe_naive->safe_tuned` | -802.04 | 0.02 | 40102.00 | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/large.bin` | `safe_tuned->unsafe` | 474.16 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/large.bin` | `unsafe->verus` | 0.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-ZERO |
| `ph29-recvfrom-alloc/small.bin` | `c-clang->c-clang-h` | -2.62 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/small.bin` | `c-clang-h->safe_tuned` | 44.87 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/small.bin` | `c-clang-h->unsafe` | 115.45 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/small.bin` | `c-gcc->c-gcc-h` | 1.72 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/small.bin` | `c-gcc-h->safe_tuned` | -458.49 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/small.bin` | `c-gcc-h->unsafe` | -387.91 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/small.bin` | `safe_naive->safe_tuned` | -160.97 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/small.bin` | `safe_tuned->unsafe` | 70.58 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph29-recvfrom-alloc/small.bin` | `unsafe->verus` | 8.83 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/large.bin` | `c-clang->c-clang-h` | 0.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-ZERO |
| `ph45-htmlent-cache-int/large.bin` | `c-clang-h->safe_tuned` | -417872.14 | 7.00 | 59696.02 | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/large.bin` | `c-clang-h->unsafe` | -404741.28 | 7.00 | 57820.18 | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/large.bin` | `c-gcc->c-gcc-h` | -337.21 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/large.bin` | `c-gcc-h->safe_tuned` | -426451.58 | 7.00 | 60921.65 | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/large.bin` | `c-gcc-h->unsafe` | -413320.72 | 7.00 | 59045.82 | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/large.bin` | `safe_naive->safe_tuned` | -93062.50 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/large.bin` | `safe_tuned->unsafe` | 13130.86 | 14.00 | 937.92 | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/large.bin` | `unsafe->verus` | 794.86 | 14.00 | 56.78 | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/small.bin` | `c-clang->c-clang-h` | 0.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-ZERO |
| `ph45-htmlent-cache-int/small.bin` | `c-clang-h->safe_tuned` | -55429.13 | 7.00 | 7918.45 | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/small.bin` | `c-clang-h->unsafe` | -53805.24 | 7.00 | 7686.46 | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/small.bin` | `c-gcc->c-gcc-h` | -45.56 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/small.bin` | `c-gcc-h->safe_tuned` | -56627.58 | 7.00 | 8089.65 | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/small.bin` | `c-gcc-h->unsafe` | -55003.69 | 7.00 | 7857.67 | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/small.bin` | `safe_naive->safe_tuned` | -12280.61 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/small.bin` | `safe_tuned->unsafe` | 1623.89 | 14.00 | 115.99 | RESOLVABLE | SIGN-STABLE |
| `ph45-htmlent-cache-int/small.bin` | `unsafe->verus` | 106.25 | 14.00 | 7.59 | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/large.bin` | `c-clang->c-clang-h` | -83.26 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/large.bin` | `c-clang-h->safe_tuned` | -7314.09 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/large.bin` | `c-clang-h->unsafe` | -7652.24 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/large.bin` | `c-gcc->c-gcc-h` | -33.15 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/large.bin` | `c-gcc-h->safe_tuned` | -8323.75 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/large.bin` | `c-gcc-h->unsafe` | -8661.90 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/large.bin` | `safe_naive->safe_tuned` | -382.97 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/large.bin` | `safe_tuned->unsafe` | -338.15 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/large.bin` | `unsafe->verus` | 0.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-ZERO |
| `ph52-concat-copy-uninit/small.bin` | `c-clang->c-clang-h` | -40.90 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/small.bin` | `c-clang-h->safe_tuned` | -3283.48 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/small.bin` | `c-clang-h->unsafe` | -3414.20 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/small.bin` | `c-gcc->c-gcc-h` | -20.40 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/small.bin` | `c-gcc-h->safe_tuned` | -3707.51 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/small.bin` | `c-gcc-h->unsafe` | -3838.23 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/small.bin` | `safe_naive->safe_tuned` | -145.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/small.bin` | `safe_tuned->unsafe` | -130.72 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph52-concat-copy-uninit/small.bin` | `unsafe->verus` | 0.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-ZERO |
| `ph53-iface-tail-uninit/large.bin` | `c-clang->c-clang-h` | 20.60 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/large.bin` | `c-clang-h->safe_tuned` | 966.12 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/large.bin` | `c-clang-h->unsafe` | 517.01 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/large.bin` | `c-gcc->c-gcc-h` | -20.11 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/large.bin` | `c-gcc-h->safe_tuned` | 450.25 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/large.bin` | `c-gcc-h->unsafe` | 1.14 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/large.bin` | `safe_naive->safe_tuned` | -481.91 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/large.bin` | `safe_tuned->unsafe` | -449.11 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/large.bin` | `unsafe->verus` | -14.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/small.bin` | `c-clang->c-clang-h` | 19.40 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/small.bin` | `c-clang-h->safe_tuned` | 403.24 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/small.bin` | `c-clang-h->unsafe` | 129.49 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/small.bin` | `c-gcc->c-gcc-h` | 2.80 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/small.bin` | `c-gcc-h->safe_tuned` | 14.31 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/small.bin` | `c-gcc-h->unsafe` | -259.44 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/small.bin` | `safe_naive->safe_tuned` | -212.69 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/small.bin` | `safe_tuned->unsafe` | -273.75 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph53-iface-tail-uninit/small.bin` | `unsafe->verus` | -14.00 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/large.bin` | `c-clang->c-clang-h` | 0.00 | 14.00 | 0.00 ⛔ | NOT RESOLVABLE | SIGN-UNSTABLE |
| `ph55-opdata-stride/large.bin` | `c-clang-h->safe_tuned` | 361.44 | 7.00 | 51.63 | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/large.bin` | `c-clang-h->unsafe` | -145.82 | 7.00 | 20.83 | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/large.bin` | `c-gcc->c-gcc-h` | -66.14 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/large.bin` | `c-gcc-h->safe_tuned` | 263.40 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/large.bin` | `c-gcc-h->unsafe` | -243.86 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/large.bin` | `safe_naive->safe_tuned` | -913.26 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/large.bin` | `safe_tuned->unsafe` | -507.26 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/large.bin` | `unsafe->verus` | 4.48 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/small.bin` | `c-clang->c-clang-h` | 0.00 | 14.00 | 0.00 ⛔ | NOT RESOLVABLE | SIGN-UNSTABLE |
| `ph55-opdata-stride/small.bin` | `c-clang-h->safe_tuned` | 1.33 | 7.00 | 0.19 ⛔ | NOT RESOLVABLE | SIGN-UNSTABLE |
| `ph55-opdata-stride/small.bin` | `c-clang-h->unsafe` | -117.08 | 7.00 | 16.73 | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/small.bin` | `c-gcc->c-gcc-h` | -20.07 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/small.bin` | `c-gcc-h->safe_tuned` | -126.69 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/small.bin` | `c-gcc-h->unsafe` | -245.10 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/small.bin` | `safe_naive->safe_tuned` | -255.30 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/small.bin` | `safe_tuned->unsafe` | -118.41 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph55-opdata-stride/small.bin` | `unsafe->verus` | 1.14 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/large.bin` | `c-clang->c-clang-h` | 18.33 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/large.bin` | `c-clang-h->safe_tuned` | -262722.08 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/large.bin` | `c-clang-h->unsafe` | -272092.64 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/large.bin` | `c-gcc->c-gcc-h` | 16.95 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/large.bin` | `c-gcc-h->safe_tuned` | -271697.36 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/large.bin` | `c-gcc-h->unsafe` | -281067.92 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/large.bin` | `safe_naive->safe_tuned` | -17888.35 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/large.bin` | `safe_tuned->unsafe` | -9370.56 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/large.bin` | `unsafe->verus` | -28.77 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/small.bin` | `c-clang->c-clang-h` | 18.34 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/small.bin` | `c-clang-h->safe_tuned` | -32095.05 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/small.bin` | `c-clang-h->unsafe` | -33459.47 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/small.bin` | `c-gcc->c-gcc-h` | 15.98 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/small.bin` | `c-gcc-h->safe_tuned` | -33249.64 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/small.bin` | `c-gcc-h->unsafe` | -34614.06 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/small.bin` | `safe_naive->safe_tuned` | -3056.32 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/small.bin` | `safe_tuned->unsafe` | -1364.42 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |
| `ph64-callback-frees-cursor/small.bin` | `unsafe->verus` | 193.36 | 0.00 | n/a (step 0) | RESOLVABLE | SIGN-STABLE |

#### ⛔ FLAGGED: `|d|/step` under 3x -- 4 of 180 pairs

* `ph07-strcut-cursor/small.bin` `unsafe->verus` -- median **71.83** Ir/call against a **34.49** Ir/call step, ratio **2.08x** -- **NOT RESOLVABLE / SIGN-STABLE**
* `ph55-opdata-stride/large.bin` `c-clang->c-clang-h` -- median **0.00** Ir/call against a **14.00** Ir/call step, ratio **0.00x** -- **NOT RESOLVABLE / SIGN-UNSTABLE**
* `ph55-opdata-stride/small.bin` `c-clang->c-clang-h` -- median **0.00** Ir/call against a **14.00** Ir/call step, ratio **0.00x** -- **NOT RESOLVABLE / SIGN-UNSTABLE**
* `ph55-opdata-stride/small.bin` `c-clang-h->safe_tuned` -- median **1.33** Ir/call against a **7.00** Ir/call step, ratio **0.19x** -- **NOT RESOLVABLE / SIGN-UNSTABLE**

#### Rows where NO cell moved at all (step 0 everywhere)

* `ph00-smoke/large.bin`
* `ph00-smoke/small.bin`
* `ph03-uudecode-bound/large.bin`
* `ph03-uudecode-bound/small.bin`
* `ph16-fdset-index/large.bin`
* `ph16-fdset-index/small.bin`
* `ph29-recvfrom-alloc/small.bin`
* `ph52-concat-copy-uninit/large.bin`
* `ph52-concat-copy-uninit/small.bin`
* `ph53-iface-tail-uninit/large.bin`
* `ph53-iface-tail-uninit/small.bin`
* `ph64-callback-frees-cursor/large.bin`
* `ph64-callback-frees-cursor/small.bin`

### 1.2 ⛔⛔ THE ROW THE MANAGER WAS WORRIED ABOUT — **`ph64`: REFUTED AS A WORRY, BY MEASUREMENT**

**What I tested, named exactly:** `patterns-php/ph64-callback-frees-cursor/
NOTES.md:414-415`'s `R1h − R1` table — **family B1, `marginal_ir_per_call`,
`-O3 / isolated`**, base = the C cell of the **same compiler**
(`c-gcc` for the gcc row, `c-clang` for the clang row).
⛔ **This is NOT `ph64`'s B1 headline** (`safe_tuned` vs `unsafe`, checked
separately at `0.0087 pp` in F89's table). I did not touch that quantity.

| `ph64` `R1h − R1`, family B1, `-O3 isolated` | published | **my median over 32 pads** | **sweep range** | verdict |
|---|---:|---:|---:|---|
| **gcc**, `small.bin` (base `c-gcc`) | `+15.98` | **`+15.98`** | **`0.00`** | RESOLVABLE / SIGN-STABLE |
| **gcc**, `large.bin` (base `c-gcc`) | `+16.95` | **`+16.95`** | **`0.00`** | RESOLVABLE / SIGN-STABLE |
| **clang**, `small.bin` (base `c-clang`) | `+18.34` | **`+18.34`** | **`0.00`** | RESOLVABLE / SIGN-STABLE |
| **clang**, `large.bin` (base `c-clang`) | `+18.33` | **`+18.33`** | **`0.00`** | RESOLVABLE / SIGN-STABLE |

▶ **`|Δ| / step` is undefined because the step is zero — not because the figure
is large, but because `ph64` has no alignment-sensitive cell at all.**
**The figures are real. They may be published.**

#### ⛔ AND I MUST REFUTE HALF OF THE ARGUMENT THAT WAS OFFERED FOR THEM

Item 112 defends the figures with: *"four cells across **two compilers** and
**two inputs** agreeing within `2.4 Ir`, all the same sign — which an alignment
artefact would not produce."* **The two-compiler half is good evidence. The
two-input half is not evidence at all**, and this is structural, not arithmetic:

* `probe.small.bin.100.bin` and `probe.large.bin.100.bin` are **the same length
  (23)**, so **`small` and `large` are run at the SAME stack alignment on the
  same binary.** The alignment contamination of a given cell is therefore
  **the same constant on both inputs**.
* ⭐ **Confirmed on `ph55`, where an artefact does exist:** its `c-clang` step is
  `7.00 Ir/call` on `small.bin` **and** `7.00 Ir/call` on `large.bin`, and the
  `c-clang→c-clang-h` pair is `NOT RESOLVABLE / SIGN-UNSTABLE` on **both**.
  **The artefact agrees across the two inputs perfectly.**

▶ **"It agrees on two inputs" cannot discriminate a real effect from this
artefact, and `ph55` is the counter-example that proves it.** The verdict for
`ph64` stands — but it stands on the sweep, not on that argument.
⭐ **The pattern worth naming is not "the conclusion was wrong" — it was right —
but "the SUPPORT offered for it was not support".** `_049` found the same shape
(the effect upheld, the story about it refuted). ▶ **A correct conclusion resting
on a bad reason is still a defect, because the reason is what gets reused.**

### 1.3 ⭐⭐ THE TWO-VERDICT DESIGN, CLONED — **AND ONE CORRECTION TO THE PAT RULE IT RESTS ON**

`.tasks-php/php50_align_sweep.py` reports **both** verdicts per pair, exactly as
`controls/argv_align.py` does and for the reason `_048` §4c gives.
It also differs from `argv_align.py` in three ways, each a correction:

1. ⭐⭐ **IT MEASURES FAMILY B, NOT W1.** `argv_align.py` differences
   `PROGRAM TOTALS` — family **W1**, a *level*. Item 112 is about family **B**, a
   *slope*. They are contaminated differently (a slope kills the one-shot term),
   so **an `argv_align.py` verdict is not a verdict about family B.** Nothing in
   the corpus had measured family B under a sweep before this round.
2. ⭐⭐ **IT SWEEPS A FULL 32-BYTE PERIOD; `argv_align.py` SWEEPS 14 BYTES.**
   `argv_align.py` uses eight path lengths in steps of 2 — a span of **14**.
   `harness/check.py::check_marginal_ir` measured the effect as **bistable with a
   32-byte period and a window exactly 16 wide**. ⛔ **A 14-byte span is narrower
   than the window, so a bistable cell can sit in one state throughout and be
   reported stable.** `argv_align.py` got away with it because its cells happened
   to straddle an edge; that is luck, not design.
3. **IT REPORTS THE STEP IT MEASURED**, per cell, so `|Δ|/step` is computed
   against the pair's own step and never borrows `ph55`'s.

> #### ⛔⛔ **AND A REFINEMENT OF THE PAT RULE THAT MY OWN SELFTEST FORCED ON ME**
> `check.py`'s docstring concludes that **"a 16-apart two-pad screen is a
> COMPLETE detector, not a lower bound"**. ✅ **That is right for ONE CELL** — a
> 16-wide window in a 32-period puts `p` and `p+16` in opposite states always.
> ⛔ **It is NOT right for a DIFFERENCE of two cells, and every family-B figure
> any row publishes is a difference of two cells.** The same docstring records
> that **the phase differs per binary** (`p03 unsafe` flips over pads 6…21,
> `p03 verus` over 8…23, `p03 safe_tuned` over 14…29). Two cells with unequal
> phases give a difference taking up to **four** values over a period, and since
> the phases are not known in advance **no strict subset of the 32 residues is
> guaranteed to sample every arc**.
>
> ⭐ **I wrote a `P3` asserting the PAT screen was complete, my own selftest
> refused it, and the refusal was right.** The arm survives as must-fire `N7`
> in `php50_align_sweep.py`: on a synthetic pair whose cells flip 8 bytes apart,
> the two-pad screen `[0,16]` measures `RESOLVABLE` (delta 18 twice) and the full
> 32-residue sweep measures `NOT RESOLVABLE` (deltas 11, 18, 25).
> **A two-pad screen would have certified a number that is not one.**
> ⚠ This is a statement about a **difference**; it does not disturb PAT's census,
> which screened **cells**.

### 1.4 ⭐ THE RULING OWED — may a family-B figure be published without a control?

> **RULING: YES, WITH ONE CONDITION, AND THE CONDITION IS NOT A PER-ROW CONTROL
> AND NOT A MAGNITUDE FLOOR.**
>
> **A family-B difference may be published iff the two cells it spans have a
> measured step of `0.00 Ir/call` over a full 32-residue pad sweep, or the
> difference exceeds that step by the `STABLE_RATIO` the sweep applies.**
> The sweep costs **~1 024 callgrind runs per row** on already-built binaries —
> **minutes for a cheap row, up to ~1 h for the dearest (`ph45`)** — and needs
> **no build, no gate and no re-measure**.

**⛔ THE CHEAPER ALTERNATIVE — A MAGNITUDE FLOOR — WAS CONSIDERED AND IS REFUTED
BY MEASUREMENT, NOT DECLINED ON TASTE.** The task asks whether there is a
magnitude below which a family-B difference is simply not publishable, the way
`.memory-php/03-numbers.md` treats W1 (*"do not quote to more than 2 dp"*).

* A floor would have to be **at least `7 Ir/call`** to protect `ph55`'s clang
  cells (and `14` to protect their *difference*, whose range is `14.00`).
* ⛔ **But `ph53/small.bin` publishes `c-gcc → c-gcc-h` at `+2.80 Ir/call` with a
  measured sweep range of `0.00`, and it is perfectly resolvable.** A `7 Ir/call`
  floor would refuse a sound figure. `ph53/large.bin`'s `c-gcc-h → unsafe` at
  `+1.14`, range `0.00`, is a second such cell.
* ⛔ **And a floor cannot save `ph55/small.bin`'s `c-clang-h → safe_tuned`
  (`+1.33`, range `7.00`) *as a magnitude*, while the sweep shows the useful
  thing about it — that it is `SIGN-UNSTABLE` — which no floor expresses.**

▶ **The quantity that decides publishability is the ROW'S OWN STEP, and the step
is not a constant.** Measured over the whole corpus it takes **four distinct
values — `0.00`, `0.02`, `7.00` and `34.49`** — and the largest is **not a
multiple of the `7 Ir` constant** (§2.3c). **A constant floor is therefore both too strict and
too loose at once, which is why the ruling is a sweep and not a number.**
⭐ **And note what a floor would have missed entirely:** `ph45`'s
`unsafe → verus` is `+106.25` — far above any floor anyone would set — yet it
carries a `14.00` sweep range, because its two cells have **different phases**.
**Its `|Δ|/step` is `7.59`, the tightest RESOLVABLE margin in the corpus.**
A floor sees magnitude; only a sweep sees phase.

⭐ **And the sweep is cheap enough that this is not an expensive ruling:**
`0.2–0.5 s` per callgrind run on these kernels, so a whole row is minutes.
**The corpus-wide sweep in this report cost under two hours of wall time and
zero gate rounds.**

⚠ **SCOPE OF THE RULING.** It is derived from **all ten rows**, both inputs, at
`-O3 isolated` with `probe_iters [100, 200]`, on this box, with this environment
block — **5 120 callgrind runs, 180 family-B differences.** It says
nothing about `-O0` (never a performance column here) and nothing about `whole`.

---

## 2. ⭐⭐ WHAT ELSE THE SWEEP FOUND — five things nobody was looking for

### 2.1 ⛔ A pair that is `SIGN-UNSTABLE` in family B and published `SIGN-STABLE` in W1

`ph55/small.bin`, `c-clang-h → safe_tuned`:

| statistic | median | range | magnitude | sign | source |
|---|---:|---:|---|---|---|
| **W1** (level) | — | — | NOT RESOLVABLE | **SIGN-STABLE** | `controls/argv_align.small.json` `CLAIMS` |
| **B** (slope) | `+1.33` Ir/call | `7.00` | NOT RESOLVABLE | ⛔ **SIGN-UNSTABLE** | `.temp/php50/sw_ph55.json` |

⚠⚠ **THIS IS NOT A CONTRADICTION AND MUST NOT BE REPORTED AS ONE.** W1 and B are
different quantities: W1 carries a **language-dependent fixed term** measured at
**≈176 k Ir** (`STATISTICS_001.md` §2, `_038` §1.3), which over `ph55`'s 20 000
calls is **≈8.8 Ir/call** — *larger than the 7.00 step*. So the two statistics
can legitimately disagree in sign on a pair this small.
▶ **But `NOTES.md` §8d's F108 headline (*`safe_tuned` is faster than gcc and
slower than clang*) rests on the W1 sign for this pair, and the fact that the
gate's own statistic does not reproduce that sign on `small.bin` is not recorded
anywhere.** ⓘ On `large.bin` family B gives `+361.44`, range `7.00`,
**RESOLVABLE / SIGN-STABLE** — so the headline's clang half is solid on one
input and unsupported-by-B on the other. **This is a caveat, not a refutation.**

### 2.2 ⭐ Item 99's mechanism is over-attributed by exactly a factor of two

`controls/argv_align.py`'s docstring and `_048` §4c attribute the step to
*"the 1 024-byte `[Op; 64]` **and** the 42-slot zval store, **both** zeroed on
every call"*. Under `check.py`'s measured rule — **"a pattern's step is
`7 × (per-call stack arrays)`, not a flat 7"**, with `p46` moving by `14` for two
arrays — **two arrays predict a `14 Ir/call` step and a three-level sweep.**

**Measured over a full period: the step is `7.00`, and each clang cell takes
exactly TWO values, not three.**
▶ **So at most ONE of the two named arrays is alignment-sensitive.** The
mechanism sentence names two contributors and the measurement supports one.
⚠ I did not identify *which*; that needs per-symbol differencing and is
**UNTESTED**.

### 2.3 ✅ The PAT 32/16 bistability model reproduces on the PHP side

From `.temp/php50/ph55.log`, `small.bin`, `-O3 isolated`:

| cell | low state | high state | high band (pads) | width | step |
|---|---:|---:|---|---:|---:|
| `c-clang` | `1742.79` | `1749.79` | `17…31, 0` | **16** | **7.00** |
| `c-clang-h` | `1742.79` | `1749.79` | `13…28` | **16** | **7.00** |

**Period 32, window exactly 16, phase differing by 4 bytes between two binaries
built from sources that differ by one hunk.** That is PAT's model — measured on
`p03`/`p04`'s *Rust* cells at `TASK_098/099` — reproducing on **php C cells, in a
different statistic, in a different programme.** ⭐ **An independent corroboration
of a PAT finding that neither programme had.**

### 2.3b ⭐ A THIRD EXPOSURE CLASS, AND IT IS PAT's `p08` CLASS TO THE HUNDREDTH

Not every exposed cell moves by `7.00`. The sweep separates **three** classes:

| class | step | cells | PAT's name for it |
|---|---:|---|---|
| stack `memset` | **`7.00 Ir/call`** | `ph55` `c-clang` `c-clang-h`; `ph45` `safe_naive` `safe_tuned` `unsafe` `verus` (both inputs) | *"`7 Ir` per per-call stack array"* — `p03` `p04` `p38` `p46` |
| ⭐ **heap** | **`0.02 Ir/call`** | `ph29` `safe_tuned` `unsafe` `verus`, **`large.bin` ONLY** | *"`p08`'s work is a heap `memmove`, which is why `p08` moves in hundredths"* |
| none | **`0.00`** | everything else | — |

⭐⭐ **`harness/check.py` predicts exactly this split and names the discriminator:
*"The mechanism is a stack array, not a heap one."*** `ph29` is
`recvfrom`-allocation — its per-call work is on the **heap** — and it moves in
**hundredths**, `0.02`, which is `2 Ir` over the whole 100-call probe difference.
▶ **A second PAT constant reproducing on the php side, in a different statistic,
on a row nobody had measured.**

⚠ **AND IT IS `large.bin` ONLY** — `ph29/small.bin` is `0.00` on every cell.
⭐ **That is the one place where "it agrees on two inputs" DOES carry information**
(§1.2): the heap class depends on allocation size, which the input controls,
whereas the stack class does not. **`ph45` and `ph55` step identically on both
inputs; `ph29` steps on one.** ▶ **So the two-input agreement argument is not
uniformly worthless — it is worthless for the STACK class, which is the class
that is large enough to matter.**

### 2.3c ⛔⛔ AND A **FOURTH** CLASS THAT IS NOT A MULTIPLE OF 7 — `ph07`'s `verus` CELL STEPS **`34.49 Ir/call`**

**The largest step in the corpus, and it is on a pair the gate pins to be the
same machine code.** `ph07-strcut-cursor / small.bin / -O3 isolated`:

| cell | values over 32 pads | step |
|---|---|---:|
| `unsafe` | `2365.28` — **one value, rock steady** | `0.00` |
| `verus` | ⛔ **`2402.62` and `2437.11`** | ⛔ **`34.49`** |

▶ **So `unsafe → verus` on that cell is `+37.34` OR `+71.83` Ir/call depending on
where the probe path lands — the magnitude very nearly DOUBLES.**
⛔ **Median `71.83` against a `34.49` range: `|Δ|/step = 2.08`, NOT RESOLVABLE —
and it is `SIGN-STABLE`, which is exactly the two-verdict case `_048` §4c
describes: the sign is publishable and the number is not.**

⚠⚠ **AND `ph07`'s `identity` pin at `-O3` is `norel`** — R4 and R5 are the same
machine code modulo relocations. ⭐ **This is `harness/check.py`'s documented
*"the R4/R5 pair has a NON-ZERO NULL CONTROL"* — `marginal_ir_per_call` is a
whole-program slope and charges the callees — with BIMODALITY on top of it.**

⛔⛔ **AND IT BREAKS ANY MAGNITUDE FLOOR SET FROM THE `7 Ir` CONSTANT.** A floor
of `7` or `14` — the only values the `ph55` evidence suggests — **would have
passed a `+37.34` figure whose true sweep range is `34.49`.** ▶ **§1.4's ruling
does not depend on knowing the step's size in advance; a floor does. That is the
argument for the sweep, made by the corpus rather than by me.**

ⓘ ✅ **`ph07` publishes in `A3`, not in family B**, so nothing shipped is wrong.
⚠ I did **not** identify the mechanism for `34.49`; it is **not** a multiple of
`7`, so it is **not** the stack-`memset` class. **UNTESTED.**

### 2.4 ⭐⭐ THE SHIM ADDS **EXACTLY 15 BYTES** AND THE ALIGNMENT WINDOW IS **16 WIDE**

`marginal_ir_env.repo_path_bytes` is **`48`** in all ten php gate records.
`len('/home/apt/repos_common/sec-ladder')` is **33**, and
`len('/.temp/php-root')` is **15**. ▶ **Running the gate through
`harness-php/root.py`'s shim lengthens every REPO-relative path — including the
probe argv — by exactly 15 bytes**, against a bistable window that is **16 wide**.

⛔ **SO `PROTOCOL_PHP.md` §E's *"never run `harness/check.py` directly on a php
row"* IS NOT ONLY A PROVENANCE CONVENTION.** `harness-php/gate.py:135-137` calls
it *"a convention, not a mechanism"* — true as to enforcement — **but on any
alignment-exposed row it is also a MEASUREMENT-STABILITY rule**, because
15 of the 16 possible offsets put the probe in a different alignment state from
the shimmed run. ⓘ It bites exactly two rows today (`ph55`'s C cells, `ph45`'s
Rust cells) and nothing else, so no published figure is affected — **but the
reason the convention matters is wider than the reason given for it.**

### 2.5 ⛔ `envp_stack_bytes` IS **NOT** CONSTANT ACROSS THE TEN RECORDS, AND THE RECORDS' OWN DOMAIN SAYS THAT MATTERS

`marginal_ir_env.domain`, in every record: *"Comparable **ONLY** against a record
with the same `envp_stack_bytes` … the same `tuning_vars` and the same
`repo_path_bytes`."*

| `envp_stack_bytes` | rows |
|---:|---|
| **3685** | `ph55` |
| **3695** | `ph03` |
| **3697** | `ph00` `ph07` `ph16` `ph29` `ph45` `ph64` |
| **3698** | `ph52` `ph53` |

▶ **By the records' own stated domain, a family-B comparison ACROSS rows is out
of domain** — four distinct environments, spanning **13 bytes**, inside a 16-wide
window. ⚠⚠ **This does NOT touch any published figure**, because every family-B
figure any row publishes is a difference of two cells **from one record**, which
is exactly the case the domain permits. ▶ **It is a constraint on a comparison
nobody has yet made, recorded before someone makes it.**
⭐ And `ph55`, the one alignment-exposed C row, is the outlier at **3685**.


---

## 3. §1.4's ruling as a `PROTOCOL_PHP.md` §B candidate

▶ *(manager's to land or not; offered as text, not as an edit — I write nothing
into `PROTOCOL_PHP.md`, `RECAP_PHP.md` or `.memory-php/`.)*

> **§B — publishing a family-B (`marginal_ir_per_call`) difference.**
> A family-B difference may be published as a **number** only when the two cells
> it spans have been swept over a **full 32-residue argv pad range** and the
> difference's sweep range satisfies `|median| ≥ 4 × range`. It may be published
> as a **sign** when every delta in that sweep has the same sign and none is
> zero. **Report both verdicts; they differ, and collapsing them discards a real
> result to avoid quoting an unreal one** (`_048` §4c).
> ⛔ **A two-pad screen is NOT sufficient for a difference** — complete for a
> cell, incomplete for a pair, because the phase differs per binary
> (`TASK_PHP_050` §1.3).
> ⛔ **There is no magnitude floor**: `ph53` publishes `+2.80 Ir/call` soundly
> and `ph55` cannot publish `+1.33`; the discriminator is the row's own measured
> step, which the corpus measures at **`0.00`, `0.02`, `7.00` and `34.49`** on
> different cells — **four values, the largest not a multiple of the others.**

---

## 4. ⚠⚠ **F109** — ROW 9. **THE MATERIAL BEING HELD BACK SHOULD MOSTLY STAY HELD BACK, BUT NOT FOR THE REASON GIVEN**

### 4.1 ⭐⭐ THE `inside_share` REFINEMENT — ⛔ **REFUTED AS A CHANGE TO THE LAYER. THE LAYER ALREADY SAYS IT.**

**The claim**, as the RULE-9 block states it (`RECAP_PHP.md:137`): *"`03-numbers.md`'s
`inside_share` rule **needs** 'a HIGH share is NOT a certificate — what matters is
whether **the DIFFERENCE** lands inside the symbol, not how much of the cell A1
sees'."*

**First, the evidence, re-derived from named artefacts:**

| F109 sub-claim | my re-derivation | source |
|---|---|---|
| `c/kernel.c` and `c/kernel_hardened.c` give a **byte-identical `kernel` symbol** under both compilers | ✅ **at `-O3 isolated`**: `md5_fn` `11d21e546a4f5cfd…` for **both** gcc cells (460 insns, 2 194 B) and `55caf689768d03e5…` for **both** clang cells (168 insns, 718 B) | `results-php/ph55-opdata-stride.json` → `cells[].static.md5_fn` |
| A1 reports the fix at **`0.000 %`** on every C cell | ✅ **exactly `+0.000000 %` on all four** C cells (`small` gcc `1553.3484 → 1553.3484`, clang `1340.5866 → 1340.5866`; `large` gcc `3774.0946 → 3774.0946`, clang `3678.3816 → 3678.3816`) | same file → `cells[].ir[input].kernel_exclusive_ir / n_iters` |
| `inside_share` **74–83 %** on the C cells | ✅ as published (`c-gcc` 81.75/73.97, `c-gcc-h` 82.61/74.94, `c-clang` 76.20/74.37, `c-clang-h` 76.20/74.37) | `NOTES.md` §8a |
| one of the two binaries **SEGVs** on `adversarial-nullcall.bin` | ✅ **reproduced by independent rebuild** — §5.1 | `.temp/php50/ub_repro.json` |

⚠ **ONE NARROWING ON THE BYTE-IDENTITY.** The claim is true **at `-O3 isolated`**,
which is the published column — but it is **not** true of the raw digest in every
configuration. Across the eight C cell-configurations, `md5_fn` is equal in
**4 of 8** (`gcc O3 iso`, `gcc O3 whole`, `clang O0 iso`, `clang O3 iso`) and
`md5_fn_norel` is equal in **8 of 8**. ▶ **F108's own rule — name WHICH OPT/MODE —
applies to F109's own sentence.** `NOTES.md` §8b names the instruction counts,
which pins the column implicitly; the RECAP summary does not.

**Now the verdict, and it is a refutation of the LAYER CHANGE and not of the finding:**

> ⛔⛔ **`.memory-php/03-numbers.md` ALREADY CARRIES THE REFINEMENT, IN THE WORDS
> F109 PROPOSES TO ADD.** Lines 44–46:
>
> > *"**Family A resolves a difference exactly to the extent the difference lands
> > INSIDE THE KERNEL SYMBOL.**"*
>
> and, 80 lines later, explicitly guarding against the misreading F109 warns of:
>
> > *"**The rule above is right as written — *to the extent the difference lands
> > inside the kernel symbol* — but `ph45` (9.5 %), `ph53` (89.5 %) and `ph52` were
> > all first discussed as ONE number per row, and that is the reading to drop.**"*
>
> ▶ **The layer already says "the DIFFERENCE", not "the cell". There is nothing to
> add.**

⭐ **The engineer's own hedge was right and was righter than the engineer knew.**
`_048` §12 / `NOTES.md` §8b guessed that *"`STATISTICS_001.md` §4 may already say
this"*. It does (§4: *"deciding whether A is safe to publish requires computing
the statistic the rule would let you skip"*) — **and so does the authoritative
layer, which `STATISTICS_001.md` explicitly is not.** `NOTES.md` §8b already
calls the row *"a clean worked instance of it"*. **The row's own prose is
correctly narrowed; the RECAP's RULE-9 summary of it is not.**

⭐ **WHAT IS GENUINELY NEW, AND IT IS EVIDENCE AND NOT A RULE.** The layer's
worked examples span `inside_share` **9.5 %** (`ph45`, published W1), **22.24 %**
(`ph52` C, W1), **89.5 %** (`ph53`, A1) and **98.6 %** (`ph52` Rust, A1).
**`ph55` at 74–83 % is the first cell in the corpus in the high-but-not-extreme
band where A1 reads exactly `0.000 %` against a defect that segfaults.** That
widens the evidence range and is worth one line as an instance.

**VERDICT: ⚠ UPHELD-NARROWED.** The finding is true, the numbers re-derive
exactly, and it is a **worked instance of a rule already in the layer**, not a
change to it.

### 4.2 ITEM 99's CLOSURE — ✅ **UPHELD, AND STRENGTHENED FROM "INFERRED" TO "MEASURED", WITH ONE CLAUSE NARROWED**

**The claim:** the W1 instability is `len(argv[1])`, a `7 Ir/call` step,
*"inferred from the step's size and shape and explicitly NOT PROVEN"*.
**The question:** sound, or a plausible story fitted to a step?

**It is sound, and it is now better supported than the finding claims, on four
independent legs:**

1. ⭐⭐ **THE SHAPE IS THE ALIGNMENT SIGNATURE, MEASURED OVER A FULL PERIOD.**
   §2.3: period **32**, window **exactly 16**, phase **differing per binary** by
   4 bytes. A "plausible story fitted to a step" does not predict a period, a
   window width and a per-binary phase; an alignment mechanism does, and all
   three came out right.
2. ⭐⭐ **THE MAGNITUDE IS A PRE-EXISTING CONSTANT FROM ANOTHER PROGRAMME.**
   `harness/check.py::check_marginal_ir` measured **`7 Ir/call` per per-call
   stack array** on **four PAT patterns** (`p03`, `p04`, `p38`, `p46`), and
   `TASK_098` attributed **100 % of the swing** to **one libc symbol**,
   `__memset_avx2_unaligned_erms`, by per-symbol differencing.
   **`ph55` measures `7.00`.** ▶ **The "not proven" hedge is over-modest: the
   mechanism was proven elsewhere and neither `NOTES.md` §13 nor `_048` §12 cites
   that work.**
3. ✅ **THE CORPUS-WIDE PREDICTION HOLDS.** The mechanism predicts exposure only
   where a kernel `memset`s a per-call **stack** array. Across ten rows × 8 cells
   × 2 inputs, **exactly two cells move**, and they are the two C cells of the row
   whose frame is a 1 024-byte `[Op; 64]`. **Eight rows move nothing.**
4. ✅ **`marginal_ir_env.domain`, in every gate record, already names the number**:
   *"`bytes` alone was believed sufficient and **TASK_114 falsified it at ±7
   Ir/call**. **argv beyond the repo prefix … are not recorded here.**"*
   ▶ **The record's own metadata predicted item 99 before item 99 was opened.**

⛔ **THE ONE CLAUSE THAT DOES NOT SURVIVE** is §2.2: the mechanism sentence names
**two** per-call stack arrays, which under PAT's measured `7 × (arrays)` rule
predicts a **14 Ir/call** step and a three-level sweep. **Measured: `7.00`, two
levels.** The attribution is right; the **count of contributors is over-stated by
two**, and which array is responsible is **UNTESTED**.

**VERDICT: ⚠ UPHELD-NARROWED** — sound, and stronger than stated, with the
two-array clause withdrawn.

### 4.3 THE REST OF F109, AT THE BOUNDED BAR

| F109 claim | (i) number re-derived from | (ii) scope | (iii) verdict |
|---|---|---|---|
| *"two blobs ONE BYTE apart"* | `inputs/adversarial-{nullcall,opdatalive}.bin`: **exactly one differing byte**, file offset **40**, `0x07 → 0x03`. ⓘ `gen.py:363` asserts `diff == [16]` — offset into the parsed `model.Model(...).buf`, **not** the raw file; both are right | the row's premise | ✅ **UPHELD** |
| *"C SEGFAULTS on one and silently returns a WRONG VALUE on the other"* | `SIGNAL-11` / `17484701542569762048` exit 0 — **reproduced by independent rebuild** (§5.1) | one input pair, gcc `-O2` | ✅ **UPHELD** |
| *"safe Rust PANICS, then returns the same wrong value BIT FOR BIT"* | `safe_naive-bug` and `safe_tuned-bug` both `exit 101` PANIC on `nullcall`; both `17484701542569762048` on `opdatalive` | two safe rungs + the `Option<fn>` control | ✅ **UPHELD**, reproduced |
| ⭐ *"unsafe Rust with the bug is STRICTLY WORSE THAN C"* | **§5.1 — reproduced on a fresh compile, both halves** | one input, one toolchain | ✅ **UPHELD** |
| *"Verus refuses fn pointers"* | ⚠ **re-derived from a committed artefact, not from a run I made.** `controls/negatives.json → fnptr` carries `rc 1` and the verbatim text *"The verifier does not yet support the following Rust feature: **function pointer types**"* at `fnptr.rs:69:13`. ✅ **Its `derived_from_sha256` pins match the files on disk byte for byte** (`fnptr.rs` `ac6fb62c…`, `verus.rs` `7b8dc911…`), so the record describes the shipped source | Verus `0.2026.08.09.92f466f`; a **type-level** refusal, not a proof failure | ⚠ **UPHELD on the record; I did not run Verus myself** |
| *"A1 blind at `inside_share` 74–83 %"* | §4.1 | `-O3 isolated`, C cells | ✅ **UPHELD** |
| *"99 CLOSED: W1 moves with `len(argv[1])`"* | §4.2 | — | ⚠ **UPHELD-NARROWED** |

---

## 5. ⭐ THE ONE THING I REBUILT — *"unsafe Rust is strictly worse than C"*

### 5.1 Independent reproduction

`.tasks-php/php50_ub_repro.py` (new, §9). It **imports `controls/stride_bug.py`
and drives that file's own `FIX_SUBS`, `materialise`, `build_c`, `build_rs`,
`run` and `classify`** — so the mutation and the compiler flags are the row's,
not mine — and **never calls its `main()`**, which is the only thing that writes
into `patterns-php/`. It writes to `.temp/php50/ub_repro/` only.

⚠⚠ **WHY A REBUILD AND NOT A RE-READ.** The claim's value rests on a number
produced by **taking undefined behaviour**. `controls/stride_bug.json` records it,
but that file *is* the single observed run — re-reading it is not a second
observation, and **a UB value has no guarantee of stability across a recompile.**
So the probe scores the two halves separately:

```
1. INDEPENDENT REBUILD + RUN on adversarial-nullcall.bin
   c-R1               class=SIGNAL-11    exit= -11 stdout=''
   safe_naive-bug     class=PANIC        exit= 101 stdout=''
   safe_tuned-bug     class=PANIC        exit= 101 stdout=''
   unsafe-bug         class=ANSWERED     exit=   0 stdout='11370550710093900800'

2. VERDICT
   HALF 1  'unsafe Rust does not crash where C does' : UPHELD
   HALF 2  'and prints 11370550710093900800'         : UPHELD
```

▶ ✅ **BOTH HALVES REPRODUCE, INCLUDING THE EXACT UB VALUE, ON A FRESH COMPILE.**
**`git status --short patterns-php/` is clean.**

⚠ **SCOPE, AND IT IS NARROW.** One input, one rustc, one `opt-level=3`, one box.
**It is `n = 2` observations of a UB outcome, not a guarantee.** The sentence
*"unsafe Rust carrying the bug is strictly worse than C here"* is safe; a
sentence asserting that `11370550710093900800` is *what LLVM does* is not.

---

## 6. **F107** — THE `_047` REVIEW ROUND

### 6.1 ⭐⭐ §1.7, *"option (b) does not exist"* — ✅ **UPHELD. ALL THREE GROUNDS RE-DERIVED BY ME, AND A FOURTH FOUND.**

| ground | F107's claim | my re-derivation |
|---|---|---|
| **1** | `gate.py`'s header forbids it hosting a gate stage | ✅ `harness-php/gate.py:43-48`, verbatim: *"It REIMPLEMENTS NO GATE STAGE and must never grow one … a php-only stage here would be a second, unvalidated gate wearing the first one's name. If a php row needs a check the PAT gate does not have, it goes in that row's `controls/` or in a separate tool"* |
| **2** | it cannot make itself mandatory; no record could witness it | ✅ `grep -c preflight harness/{check,measure,report}.py` → **`0 0 0`**, re-run by me. ✅ `gate.py:130-137` verbatim. ✅ `grep -n 'common-php\|patterns-php\|harness-php\|emalloc_shim' harness/*.py` → **zero hits** |
| **3** | `root.py` rebinds **paths**, not verdicts | ✅ `harness-php/root.py:10-24`: the entire mechanism is `REPO = dirname(dirname(abspath(__file__)))` plus *"`os.path.abspath` **does not resolve symlinks**"*, so *"every REPO-relative path follows"* |

⭐⭐ **AND A FOURTH GROUND F107 DID NOT HAVE, WHICH I WENT LOOKING FOR AS AN
ATTACK AND WHICH ENDED UP STRENGTHENING THE VERDICT.** I checked whether a
php-side *substituted* `check.py` could be slipped in through the shim — that
would be an option (b) by another route:

* `.temp/php-root/harness` is a **whole-directory symlink** (`harness -> ../../harness`), not file-by-file, so no single harness file can be swapped without editing `harness/`.
* And if one were: `results-php/gate/ph64-callback-frees-cursor.json → source_sha256` carries **`harness/check.py`** among its 40 keys (with `asm.py`, `build.py`, `measure.py`, `report.py`, `vparse.py`, `dloop.py`, `fixture.py`, `limbs.py` and five `common/` files). **A substituted harness would change the record and be caught.**

⚠ I also attacked ground 1 from inside `check.py`: `_scan_unsafe_sites` takes
`contract`, so I checked whether a **per-row `spec.md` hatch** already exists —
which would be an option neither (a), (b) nor (c). **It does not.** `contract`
supplies only the *file list* (`verus.obligations`); every `unsafe` token outside
a trusted body is an unconditional `rep.fail`, and the `common/` scan is
unconditional over `_path_includes`.

▶ ⛔ **(b) DOES NOT EXIST. The manager has told the user correctly.** Proceeding
under (c) is right, and (c) is what `gate.py`'s header prescribes.

### 6.2 ⚠ THE *"three of four refutations came from a second input or a second document"* GENERALISATION — **UPHELD-NARROWED, and the count does not reproduce**

**Three problems, in increasing order of importance:**

1. ⚠ **The count does not reproduce from the RECAP's own list.** The paragraph
   names four things — F105's `97.6 %` (second input), F103's decomposition
   (second input), F106's relocation objection (second document), and option (b)
   (second document). **That is four of four, not three of four.** Meanwhile the
   RECAP's own verdict table contains exactly **two** entries marked REFUTED
   (F105 in part, F103). ▶ **"Three of the four" is not recoverable from either
   enumeration**, which is `PROTOCOL.md` rule 13's shape again.
2. ⚠ **The dichotomy is close to exhaustive by construction.** A refutation must
   rest on evidence; evidence is either a new measurement (*another input, another
   row*) or a citation (*another document*). The only excluded category is *a
   cleverer argument over the same evidence*. **So the claim has low falsifying
   power** — which does not make it false, but does mean it cannot be strongly
   confirmed by counting.
3. ✅ **It nonetheless survives a fresh test — my own round — with one
   counter-instance.** Of five refutations/corrections here: F109's layer change
   died on **a second document** (`03-numbers.md` itself); `ph64`'s worry died on
   **a new measurement**; F96 result 3's trend died on **another row** (`ph55`);
   `argv_align.py`'s 14-byte span died on **a second document** (`check.py`'s
   docstring). ⛔ **But §1.3 — the PAT two-pad screen is not a detector for a
   difference — came from an ARGUMENT over evidence already in hand**, formalised
   as a synthetic selftest arm. ▶ **So this round is 4 of 5**; combined with the
   4 of 4 I recount in point 1, that is **8 of 9 across two rounds, with one
   explicit counter-example.** ⚠ And see §10.7: **this is my own classification
   of my own work**, which is exactly the weakness point 2 describes.

▶ **The operative advice — *"cheapest next method first: another input, another
document, another row"* — is sound and I used it. The COUNT should not be quoted.**

---

## 7. **F96** — ⭐⭐ `ph55` **DOES** SUPPLY A SECOND METHOD, FOR ONE RESULT, AND IT **REFUTES** IT

### 7.1 The four-prediction ledger and the build record: still **UNREVIEWED**, for the third time, and I say so plainly

F96's core is (a) a build record and (b) a four-prediction ledger about `ph53`'s
own rungs (R2 ≈ R1h, R3 cheapest, R4 elides, R5 no ghost state). **These are
row-specific facts about one kernel.** `_047` checked whether `ph52` supplies a
second method and it does not. **`ph55` does not either, and the task's premise
that it might is itself questionable:** the RECAP classifies `ph55` as **`T5`**,
not `T3` (`ph52` and `ph53` are the `T3` pair), so it is a *different family*,
not *"a third `T3`-ish row"*. Its kernel is an opcode dispatcher, not an
interface-table tail read.

⛔ **So for the ledger, `UNREVIEWED` is the honest answer for the third time, and
I am not going to manufacture a bar it can clear.** Re-deriving the ledger needs
`ph53`'s rungs re-measured or re-read at the source level — a task, not a
paragraph, exactly as `_047` §12 said.

### 7.2 ⭐⭐ BUT F96's **RESULT 3** IS GENERALISABLE, `ph55` TESTS IT, AND **IT GOES THE OTHER WAY**

F96 result 3: *"**THE PROVED RUNG IS CHEAPER THAN THE UNSAFE ONE** — a THIRD row,
and by the largest margin of the three (`A1 −1.253 %`). F82's observation on
`ph45` and `ph64`, now `n = 3`."*

**Re-derived across all ten rows** (family **A1** = `kernel_exclusive_ir / n_iters`,
**`-O3 isolated`**, base = that row's own `unsafe` cell; source
`results-php/<row>.json`), and **cross-checked against family B1** from my own
sweep (median over 32 pads, `.temp/php50/sw_*.json`):

| row | **A1** `small` | **A1** `large` | **B1** `small` | **B1** `large` | identity @ O3 | direction (A1) |
|---|---:|---:|---:|---:|---|---|
| `ph45-htmlent-cache-int` | `−0.0383 %` | `−0.0054 %` | `+106.25` | *(§1.1)* | `differ` | verus **cheaper** |
| `ph53-iface-tail-uninit` | **`−1.2534 %`** | `−0.4937 %` | **`−14.00`** | **`−14.00`** | `differ` | verus **cheaper** |
| `ph64-callback-frees-cursor` | `−0.0067 %` | `−0.0009 %` | ⛔ **`+193.36`** | ⛔ **`−28.77`** | `differ` | verus **cheaper** |
| ⛔ **`ph55-opdata-stride`** | ⛔ **`+0.0715 %`** | ⛔ **`+0.0955 %`** | `+1.14` | `+4.48` | `differ` | ⛔ **verus DEARER** |
| `ph00` `ph03` `ph07` `ph16` `ph29` `ph52` | `0.0000 %` | `0.0000 %` | `0.00` | `0.00` | `exact`/`norel` | **not evidence** |

⭐ **FOUR THINGS THIS SETTLES, AND TWO OF THEM ARE REFUTATIONS:**

1. ✅ **F96's `−1.253 %` re-derives EXACTLY** — `1116.947 → 1102.947` Ir/call on
   `ph53/small.bin`, a difference of **exactly `−14.000` Ir/call**, and **family
   B1 independently gives `−14.00` on both inputs.** ⭐ **That is a second method
   for F96's own headline number, and it agrees to the instruction.**
2. ⛔⛔ **`ph55` IS THE FOURTH ROW AND THE FIRST COUNTEREXAMPLE.** It was built at
   `_048`, *after* F96 was written, and its proved rung is **dearer** than its
   unsafe one on **both** inputs and in **both** statistics (`A1 +0.0715 %` /
   `+0.0955 %`; `B1 +1.14` / `+4.48`). ▶ **F82/F96's observation is `3 of 4`, not
   `n = 3` of 3.**
3. ⚠⚠ **AND THE DENOMINATOR IS 4, NOT 10.** Only **four** rows have
   `unsafe vs verus` pinned `differ` at `-O3` (`ph45`, `ph53`, `ph55`, `ph64`);
   the other six are `exact` or `norel`, so their `0.0000 %` is **true by
   construction and is not evidence in either direction.** Quoting *"and six more
   rows show no difference"* would be quoting the identity pin.
4. ⛔⛔ **`ph64`'s B1 CONTRADICTS ITS OWN A1 — AND IT IS THE ONLY ROW THAT DOES.**
   See §7.3.

### 7.3 ⭐⭐⭐ AN UNASKED-FOR SECOND METHOD FOR F96's **RESULT 2**, AND IT **CONFIRMS** IT

F96 **result 2** is the row's most transferable claim: *"**A and B agree in sign
and closely in magnitude on EVERY cross-language cell of this row** … **and the
reason is that §B1a's O(1)-allocation precondition HOLDS here**, so there is no
allocator term for B to include and A to miss."* ▶ Its own stated test (item 78)
is **a row where the callee work diverges.**

**The corpus now contains that row, and my sweep priced it.** On `unsafe → verus`:

| row | §B1a O(1)-allocation precondition | A1 | B1 `small` | B1 `large` | **A and B?** |
|---|---|---:|---:|---:|---|
| `ph53` | ✅ **holds** (F96's own statement) | `−14.000` | `−14.00` | `−14.00` | ✅ **agree to the instruction, both inputs** |
| `ph55` | — | `+1.127` / `+4.523` | `+1.14` | `+4.48` | ✅ **agree, both inputs** |
| `ph52` | — | `0.000` | `0.00` | `0.00` | ✅ agree (pinned `norel`) |
| ⛔ **`ph64`** | ⛔ **BROKEN — this is the row that broke it** (item 54) | `−0.510` both inputs | ⛔ **`+193.36`** | ⛔ **`−28.77`** | ⛔ **DISAGREE IN SIGN on `small`, and B FLIPS SIGN between the two inputs while A does not** |

▶ ⭐⭐ **THE ONE ROW WHERE THE PRECONDITION FAILS IS THE ONE ROW WHERE A AND B
DISAGREE.** That is F96 result 2's mechanism tested on its own stated falsifier
and **surviving** — and it is exactly `harness/check.py`'s documented reason:
*"`marginal_ir_per_call` is a **WHOLE-PROGRAM SLOPE**, so it charges everything
the kernel calls — **glibc malloc internals above all** … **So the R4/R5 pair has
a NON-ZERO NULL CONTROL.**"*

⚠⚠ **SCOPE, AND IT IS A REAL LIMIT.** F96 result 2 is about **cross-language**
cells; `unsafe → verus` is **same-language**. **So this is the same MECHANISM on
a different comparison, not a replication of the claim.** It is `n = 4` rows for
*"where the callee work diverges, A and B diverge"* and `n = 0` new rows for
result 2 as written. ⭐ **It is still the closest thing to a second method F96 has
had in three rounds, and it points the confirming way.**

⛔ **AND A CONSEQUENCE FOR THE ROW'S OWN NUMBERS:** `ph64`'s `unsafe → verus`
must **not** be published in family B. `harness/check.py`'s OPERATIVE RULE says
so in terms — *"for a cross-RUNG comparison use `kernel_exclusive_ir`; use
`marginal_ir_per_call` for anti-collapse, which is what it was built for"* — and
`ph64` is precisely a pattern *"whose kernel calls out of itself"*.
ⓘ ✅ **`ph64`'s NOTES does not publish that pair in B**, so nothing shipped is
wrong; this is a guard-rail for the next row, not a defect report.

⚠ **ONE THING I COULD NOT RULE OUT, AND IT TOUCHES F96's HEADLINE NUMBER.**
`ph53`'s A1 difference is **exactly `−14.000` Ir/call on both inputs**, and `14`
is exactly `2 × 7`, the PAT step for a two-stack-array kernel. I could not
exclude by my own measurement that this is the alignment effect, **because my
sweep measures the whole-program slope and not `kernel_exclusive_ir`.**
ⓘ The PAT census is direct evidence the other way — **`kernel_exclusive_ir`
moved in `0` of `288` (pattern, input, cell) triples** and is called
*"structurally immune"* — so the coincidence is very probably just a coincidence.
**But it is UNTESTED here and I flag it rather than assume it.**

**VERDICT on F96: ⛔ UNREVIEWED** — the four-prediction ledger and the build
record still have no cheap second method, and this is the third round to say so.
⚠ **Two of its four "measured results beyond the row" moved anyway, in opposite
directions, and neither is a review of the finding:** **result 3 is REFUTED as a
generalisation** (§7.2) by a row that did not exist when it was written, and
**result 2's mechanism is CONFIRMED on its own stated falsifier** (§7.3).
⭐ **Result 1 (the two consumers) and result 4 (`[100, 200]` is not on a
transient) I did not test at all.**


## 8. ⛔⛔ COVERAGE TABLE — what may and may not enter `.memory-php/`

⛔ **Each subject gets EXACTLY ONE verdict from the required vocabulary.**
Sub-verdicts are stated underneath, never substituted for the headline one.

| subject | ⭐ **THE ONE VERDICT** | what it means |
|---|---|---|
| **item 112** | ✅ **UPHELD** | ⛔ **NOT `UNDECIDABLE-WITHOUT-A-BUILD` — no build was needed.** Every binary already existed under `.temp/php-scratch/build/`, so the whole sweep was read-only and cost zero gate rounds. The phenomenon is **real**, it **survives into family B by construction** (§1.0), and the sweep found it on **three rows nobody suspected** — `ph45` (`7.00`), `ph07` (**`34.49`**, the largest and not a multiple of 7) and `ph29` (`0.02`). **Complete corpus: `4` of `180` family-B differences flagged, all on `ph55` and `ph07`.** ⛔ **Its `ph64` sub-worry is REFUTED**: step `0.00` over a full period, all four published figures reproduced exactly (§1.2). ✅ **And no published family-B number in the corpus is wrong** — the only row that both publishes family B and has an exposed cell is `ph55`, which already refuses to quote it |
| **F109** | ⚠ **UPHELD-NARROWED** | every re-derivable number re-derives exactly; the headline sentence is **reproduced on a fresh compile** (§5.1). ⛔ Narrowed in two places: the `inside_share` refinement is a **worked instance of a rule already in the layer, not a change to it** (§4.1), and item 99's mechanism sentence **over-counts its contributing arrays by two** (§4.2) |
| **F107** | ⚠ **UPHELD-NARROWED** | its **load-bearing** claim — §1.7, *option (b) does not exist* — is ✅ **fully UPHELD**, all three grounds re-derived by me plus a fourth (§6.1). ⛔ Its **secondary** *"three of four refutations"* generalisation is narrowed: sound advice, **a count that does not reproduce**, and a counter-instance from this round (§6.2) |
| **F96** | ⛔ **UNREVIEWED** | third round running. The four-prediction ledger and build record still have **no cheap second method**, and `ph55` does not supply one for them (§7.1) — it is a `T5` row, not the *"third `T3`-ish"* row the task supposed. ⓘ **Two of its bullets moved anyway, in opposite directions, and neither is a review of the finding:** *result 3* is ⛔ **REFUTED as a generalisation** by `ph55` (§7.2), and *result 2*'s mechanism is ✅ **CONFIRMED on its own stated falsifier** by `ph64` (§7.3) |

### 8.1 ⭐ WHAT MUST **NOT** ENTER `.memory-php/`

1. ⛔⛔ **The F109 `inside_share` "refinement" as a NEW RULE or an EDIT to
   `03-numbers.md`.** The layer already says *"Family A resolves a difference
   exactly to the extent the difference lands INSIDE THE KERNEL SYMBOL"*
   (`03-numbers.md:44-46`) and already guards the misreading
   (*"…all first discussed as ONE number per row, and that is the reading to
   drop"*). ▶ **Adding it would be item 73's shape in reverse — appending a
   correction that is already applied.** ✅ **What MAY enter is one clause of
   EVIDENCE**: *"`ph55`'s C cells at 74–83 % are the corpus's first high-share
   cells where A1 still reads `0.000 %`"* — an instance, appended to the
   existing rule, **not a new bullet**.
2. ⛔ **Item 99's mechanism sentence as written** — *"the `[Op; 64]` **and** the
   42-slot zval store, **both** zeroed on every call"*. The measured step is
   `7.00` with **two** levels, not `14.00` with three. **At most one array
   contributes.** If item 99 enters the layer, it enters with the count removed.
3. ⛔ **Item 112's *"four cells across two compilers and two inputs agreeing…
   which an alignment artefact would not produce"* as a reason to trust a
   family-B figure.** §1.2: **the two-input half is not evidence**, and `ph55`
   is the counter-example. The conclusion is right; this support for it is not.
4. ⛔ **F96's result 3 as a trend** (*"the proved rung is cheaper… now `n = 3`"*).
   §7.2: it is **3 of 4** on the only four rows that can speak to it, and the
   fourth was built after it was written. It may enter as *"3 of the 4 rows whose
   R4 and R5 differ at `-O3`"*, never as a direction.
5. ⛔ **F107's *"three of the four refutations"* count.** §6.2 — not recoverable
   from either of the RECAP's own enumerations. The **advice** may enter; the
   **count** may not.
6. ⛔ **Any future family-B figure for an `unsafe → verus` (R4/R5) pair on a row
   whose kernel allocates.** §7.3: `ph64`'s B1 for that pair is **`+193.36` on
   `small` and `−28.77` on `large`** while A1 is `−0.510` on both — **B disagrees
   with A in sign and flips between inputs.** `check.py`'s OPERATIVE RULE already
   forbids it (*"for a cross-RUNG comparison use `kernel_exclusive_ir`"*).
   ⓘ ✅ Nothing shipped violates this; it is a guard-rail for the next row.
7. ⛔ **`harness/check.py`'s *"a 16-apart two-pad screen is a COMPLETE detector"*
   applied to a DIFFERENCE.** §1.3. It is complete for a **cell**. ⚠ **This is a
   PAT-side docstring and I did not edit it** (frozen infrastructure); it is
   flagged here so the php layer does not inherit the wider reading.

---

## 9. THE CHECKERS I WROTE — all in `.tasks-php/`, no digest, free

| file | what it is | §H |
|---|---|---|
| `.tasks-php/php50_align_sweep.py` | the item-112 sweep: family-B slopes over a full 32-byte argv pad period, per row, per cell; two verdicts per pair; reports the step it measured | **10 arms (7 must-FIRE, 3 must-NOT) + 9 unit arms**, all inside the file; **refuses to measure if the verdict arm is broken** |
| `.tasks-php/php50_ub_repro.py` | independent rebuild + run of `ph55`'s bug mutants, driving `controls/stride_bug.py`'s own recipe and never its `main()` | **6 arms (4 must-FIRE, 2 must-NOT)** |
| `.tasks-php/php50_table.py` | pure renderer for §1.1; recomputes verdicts from raw sweep arrays so a verdict fix needs no re-run | *(renders only; decides nothing)* |

⭐⭐ **BOTH CHECKERS CAUGHT ME, WHICH IS THE POINT OF §H:**

* `php50_align_sweep.py`'s **`N7`** refused my first claim that the PAT two-pad
  screen is a complete detector. **The arm stayed; the claim changed** (§1.3).
* Its **`SIGN-ZERO`** arm exists because `ph52` exposed that my first verdict
  function labelled a *pinned, exact, measured null* as `SIGN-UNSTABLE`.
  **Six of ten rows are pinned `exact`/`norel` and would all have been
  mislabelled.** ⚠ I fixed the **function**, added three unit arms, and made the
  renderer recompute from raw arrays — **I did not relabel the output.**
* Its `build_dir` error path printed *"no binary at &lt;path&gt;"* eight times when I
  had the build-directory naming wrong, instead of returning a figure-shaped `0`.

⚠ **`.temp/php50/` keeps the generators and the evidence and deletes the
artefacts — `52 MB → 296 KB`.** Every callgrind out-file is `unlink`ed by
`_total` as it is read and every padded probe blob after its pad; the mutant
binaries under `ub_repro/` and the padded-probe tree under `sweep/` are deleted
and **re-derivable by re-running the two checkers**. What stays is the evidence:
**10 `.log` files, 10 `.json` sweep records, `ub_repro.json`**, and the two
runner scripts.

⭐ **Anyone can re-render §1.1 from those records without re-measuring:**
`python3 .tasks-php/php50_table.py`. It recomputes the verdicts from the raw
sweep arrays, so a future correction to the verdict function costs nothing.

---

## 10. ⚠ WHAT I AM UNSURE OF

1. ⛔⛔ **MY SWEEP PERTURBS `argv`, AND THE GATE'S OBSERVED BIMODALITY WAS
   ACROSS `envp`.** `_048` §3c saw `ph55`'s clang cell move `+7.00 → +0.00`
   between two **gate runs** with a **fixed** probe path — so what moved there was
   the environment block, not `argv[1]`. Both shift the initial stack pointer and
   my `ph55` control shows argv reproduces the same `7.00` step with the same
   period and window, **so I believe they are the same knob** — but I did not
   sweep `envp` and **I did not prove they are interchangeable.** ▶ If some cell
   were sensitive to `envp` and not to `argv`, my `0.00`s would understate.
   ⓘ Against that: PAT measured this effect by padding **`envp`** and got the same
   32/16/7 constants I got by padding **`argv`**. **UNTESTED all the same.**
2. ⚠ **`ph53`'s A1 `unsafe → verus` is exactly `−14.000` Ir/call on both inputs,
   and `14 = 2 × 7`.** §7.2. `kernel_exclusive_ir` is PAT-measured immune
   (`0 of 288`), so this is very probably a real code difference — **but my sweep
   measures the whole-program slope, not `kernel_exclusive_ir`, so I did not test
   it myself.** F96's headline `−1.253 %` rests on it.
3. ⚠ **I swept `-O3 isolated` only.** That is the column every published
   family-B performance figure lives in, but `whole` is unswept and `O0` is
   unswept. **A row could be exposed there and this report would not know.**
4. ⚠ **`STABLE_RATIO = 4.0` is inherited from `argv_align.py`, not derived.**
   I kept it so the two files' verdicts are comparable. **It is a convention.**
5. ⚠ **The UB reproduction is `n = 2` observations, one toolchain, one box.**
   §5.1. *"Strictly worse than C here"* is safe; *"LLVM produces
   `11370550710093900800`"* is not.
6. ⚠ **F109's *"Verus refuses fn pointer types"* rests on a committed artefact
   I hash-verified, not on a Verus run I made** (§4.3). The artefact is a
   must-fire negative that `controls/negatives.py --verus` re-runs, so it is well
   guarded — **but I did not independently execute Verus, and a toolchain drift
   since 2026-09-14 would not show up in this report.**
7. ⚠ **§6.2's counter-instance count (`8 of 9` over two rounds) is my own
   classification of my own work** and is exactly the kind of self-scored
   generalisation §6.2 criticises. **Treat it as illustrative, not as data.**

---

## 11. ⛔ AND A PROCESS FAILURE OF MY OWN — item 113's family, from the other direction

⚠⚠ **I WROTE A `pgrep` GUARD AND IT MATCHED ITS OWN LAUNCHER.** My first
corpus-sweep runner waited with
`while pgrep -f 'php50_align_sweep.py --row ph64-…'; do sleep 10; done`.
The **parent shell's own command line contained that literal string**, so the
`pgrep` matched the wrapper that had spawned it and **the loop never exited** —
the whole corpus sweep sat idle behind a completed job.

▶ **Item 113 is *a truncated liveness check reports LESS than it found*. This is
the mirror image: an UNtruncated liveness check reporting MORE than exists,
because the pattern was visible in the searching process's own ancestry.**
⭐ **Both failures come from `pgrep -f` matching command TEXT rather than
identifying a process.** I fixed it the way the rule implies: **I confirmed the
exact command line of the exact PID** (`/proc/3034573/cmdline` →
`bash .temp/php50/runall.sh`, PPid `3034570`), killed **that PID only**, verified
with an untruncated `pgrep -a -f runall.sh` that the only remaining match was my
own verifying shell, and **rewrote the runner as `runall2.sh` with no `pgrep` at
all** — a plain sequential loop and a sentinel file.
**No `pkill`, no `killall`, no substring match.**

ⓘ Cost: one idle interval, no corrupted data — the ph64 sweep had already
completed and written its JSON before the guard was consulted.

---

## 12. WHERE I STOPPED

⭐ **THE SWEEP IS COMPLETE: all ten rows, both inputs, 32 pads, `-O3 isolated` —
`5 120` callgrind runs, `180` family-B differences, no row left `UNTESTED`.**
Every step in §1.1 is a measurement; none is borrowed from `ph55` and none is a
gap. **§§2–7 are complete to the bar each was set.**

What I did **not** do, named:

* **An independent Verus run** for F109's `fn`-pointer refusal — I verified the
  committed artefact and its hashes instead (§4.3). **Not independently executed.**
* **F96's four-prediction ledger** — **UNREVIEWED** for the third time, by
  decision and not by fatigue (§7.1).
* **An `envp` sweep** (§10.1) and a **`kernel_exclusive_ir` sweep** (§10.2).
  Both are cheap and both would close a stated uncertainty; neither was in scope.
* **`-O3 whole` and `-O0`** (§10.3).

