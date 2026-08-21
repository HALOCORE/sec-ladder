# p11 — findings

Written by the engineer who measured them (TASK_033). Every number here is
either pasted from a command's output or derived from a disassembly listing; a
five-decimal rate in this file always comes from `body_len / K` off the listing
and never from a two-point marginal (`.memory/03-measurement.md`, TASK_026 §0
item 2). Where a rate is quoted, **the spelling that produced it is named beside
it**; where two rates are differenced, they are at **matched spelling**.

**Two `Ir` conventions are in shipped patterns and this file says which, every
time. On p11 the choice is not cosmetic and §3 is where that is measured**: the
kernel-exclusive column is wrong for four of eight cells here, by up to 9830
Ir/call, because R1, R1h and R3 all call out of the `kernel` symbol. Every number
in §3, §4 and §10 is therefore the **whole-program marginal** (p05's, p17's,
p07's and `check.py` stage 3b's convention). `results/tables/p11-nul-scan.md`
carries the kernel-exclusive column because `harness/measure.py` records that for
every pattern; §3 is the correction.

## 0. What was checked before five rungs were built on it

TASK_033 named two premises it was least sure of and asked for them to be
settled on the disassembly first. Both were checked before any rung was written,
with `.temp/p11/probe_c.c` and `.temp/p11/probe_rs.rs` at `-O3`.

**(a) Does the two-loop split survive the optimiser?** Yes, in every rung, and
it is not close. §1.

**(b) Does an idiomatic safe Rust scan reach `memchr`?** *One* spelling does and
*one does not*, and they are 5.3× apart. §2. **The R1-vs-R3 scan gap is a
library and dispatch difference, not a safety cost**, and §2 separates the three
terms instead of quoting the ratio — this project retracted "C beats Rust" once
for exactly that class of error (`.memory/01-ladder.md`, p02's `memcpy` idiom).

## 1. The scan/fold split survives -O3 in all six rungs

`harness/asm.py`'s `backward_branches`, `-O3 isolated`, kernel only:

| cell | loops | why |
|---|---|---|
| `c-gcc` | 2 | its scan is `call strlen@plt`, so only the outer walk and the fold have back edges |
| `c-clang` | 3 | same `call strlen@plt`, plus a scalar fold remainder |
| `c-gcc-h` | 4 | `call memchr@plt` |
| `c-clang-h` | 3 | `call memchr@plt` |
| `safe_naive` | 3 | scan, fold, walk |
| `safe_tuned` | 3 | `call <CStr>::from_bytes_until_nul`, fold, walk |
| `unsafe` / `verus` | 5 | scan, 4×-unrolled fold, fold remainder, walk |
| **fused control** | **2** | `u_fused`, the deliberately-fused kernel |

The fused control is the falsifier: it is the shape the pattern must not
collapse to, and it has *fewer* back edges than every split rung. Nothing fuses.

**A finding while checking this, and it is about C rather than Rust: clang
rewrites a hand-written NUL byte loop into a `strlen` call.**
`controls/gen_controls.py` builds `k_byteloop.c` — R1 with
`while (buf[off + q] != 0) q++;` and **no library call anywhere in the source**,
`<string.h>` not even included — and clang emits

```
$ objdump -dr probe_c_clang.o | grep R_X86_64_PLT32
    45: R_X86_64_PLT32  strlen-0x4        <- kernel        (source says strlen)
   19d: R_X86_64_PLT32  memchr-0x4        <- kernel_h_memchr
   305: R_X86_64_PLT32  strlen-0x4        <- kernel_byteloop (source says a LOOP)
$ objdump -dr probe_c_gcc.o | grep R_X86_64_PLT32
    8c: R_X86_64_PLT32  strlen-0x4
   1c1: R_X86_64_PLT32  memchr-0x4        <- and no third: gcc keeps the loop
```

So R1's `strlen` is **not** an advantage handed to it by spelling: under clang
the naive C loop gets there anyway, by loop-idiom recognition. Under gcc it does
not (`add;cmpb;jne`, 3.00000 Ir/byte), which is one more instance of
`.memory/01-ladder.md`'s rule that a gcc-only gap is a pass default and not a
capability.

## 2. The R1-vs-R3 scan gap is 12x or 64x depending on the R3 SPELLING

…and neither figure is a safety cost. 12x against the shipped R3
(`CStr::from_bytes_until_nul`), 64x against the `iter().position()` spelling
of the same rung.

Every figure is `body_len / K` read off the listing, so each is exact as a
disassembly quantity. The spelling is named beside every one.

| scan spelling | rung | what it lowers to | Ir per scanned byte |
|---|---|---|---|
| `strlen` | **R1** | glibc IFUNC → AVX2; main loop `vmovdqa/vpminub×3/vpcmpeqb/vpmovmskb/sub/test/je` = **10 insns / 128 B** at `libc+0x18b880` | **0.078125** |
| `memchr` | **R1h** | glibc IFUNC → AVX2 as well, at `libc+0x188080`, **but it must also test its count** | **0.1023** (measured; not `strlen`'s rate) |
| `CStr::from_bytes_until_nul` | **R3** | `core::slice::memchr`, SWAR on 2 × `u64`, **15 insns / 16 B**, no `xmm`/`ymm` | **0.937500** (spans ≥ 16 B) |
| `iter().position(\|&b\| b == 0)` | `r3_position` | scalar byte loop `cmpb;je;inc;cmp;jne` | **5.00000** |
| `iter().take_while(..).count()` | `r3_takewhile` | the same loop | **5.00000** |
| `while q < len { if b == 0 break; q += 1 }` + `get_unchecked` | **R4, R5** | `cmpb;sete;je;inc;cmp;jne` | **6.00000** |
| the same, indexed | **R2** | `lea;cmp;jae;cmpb;sete;je;inc;cmp;jne` | **9.00000** |
| `while (buf[off+q] != 0) q++` under **gcc** | `k_byteloop` | scalar byte loop `add;cmpb;jne` | **3.00000** |
| the same under **clang** | `k_byteloop` | *rewritten to `call strlen@plt`* | **0.078125** |

Independent check of the top two rows, and it is a *measurement* rather than a
second reading of the same listing: 64 × `strlen` over a 65 536-byte string under
callgrind is **330 616 Ir over 4 194 304 bytes = 0.0788 Ir/byte**, against
0.078125 predicted. The same probe on `memchr` (`.temp/r33/mcprobe.c`, re-run at
TASK_034) gives **429 184 Ir over the same 4 194 304 bytes = 0.1023**, i.e. **31%
dearer than `strlen` and not the same row**, which is what item (3) of this
section already says in prose — `memchr` tests a count as well as a sentinel.
Until TASK_034 the table put R1h's `memchr` on `strlen`'s 0.078125
(TASK_033_REVIEW minor 4); both are AVX2 out of the same IFUNC mechanism, so the
qualitative claim was right and the rate was not. **Nothing in the decomposition
below rests on the `memchr` rate** — the 12.0× is `strlen` against
`core::slice::memchr`, and §3's per-string R1-vs-R1h figures are marginals, not
rates.

**The decomposition, which does not say what the bare ratio says.**
`0.078125` against `5.00000` is 64×, and the safety term is the *smallest* of the
three factors it is made of:

- **SIMD width and dispatch: 0.078125 vs 0.937500 = 12.0×.** glibc resolves
  `strlen` through an **IFUNC at load time** to a hand-written AVX2 routine;
  `core::slice::memchr` is compiled once for baseline `x86-64` and is therefore
  SWAR-on-`u64`. Nothing in this repo builds with `-march`. This term is a
  property of *how the two standard libraries are shipped*, not of Rust, and
  not of safety.
- **Spelling, inside safe Rust: 0.937500 vs 5.00000 = 5.3×**, between two
  spellings of one rung, both in contract, neither containing `unsafe`.
- **The safety term — the bounds CHECK — is 3.00000 Ir/byte**, and it is measured
  at matched spelling *within one backend*: §4a's `9.00000 − 6.00000`, R2's
  indexed scan against R4's `get_unchecked` scan, same loop, same unroll factor
  (none), same language, same compiler.

So the sentence p11 supports is: *C finds a NUL byte 64× faster per byte than one
idiomatic safe-Rust spelling; 12× of that is which routine the platform ships,
5.3× is which Rust spelling you pick, and the bounds check is 3.00000 Ir/byte.*

⚠ **What p11 CANNOT price is the bound itself** — the `q < len` exit test that
R1 lacks — **because LLVM will not emit an unbounded byte scan.** clang rewrites
`k_byteloop.c`'s hand-written loop into `call strlen@plt` (byte-identically to
`c-clang`, §1) and safe Rust cannot express one at all, so the only unbounded
byte scan on this box is gcc's 3.00000. `5.00000 − 3.00000 = 2.00000` is
therefore a **cross-backend** figure (rustc/LLVM against gcc) and is labelled as
one; it is *not* the matched-spelling number and must not be quoted beside p16's
and p05's 2.0000, which are same-compiler differences. §4a has p11's
same-compiler reproduction of that constant, on the **fold** loop, where it is
exact.

## 3. Performance — and the column this pattern must NOT be read from

**⚠ On p11 the kernel-exclusive `Ir` column is wrong for four of eight cells, and
by up to 9830 instructions per call.** `.memory/03-measurement.md` says it in
advance — *"kernel-exclusive `Ir` is the right level for a self-contained kernel,
and the wrong one for a kernel that calls out"* — and p11 is the pattern where it
bites hardest, because **R1's `strlen`, R1h's `memchr` and R3's
`<CStr>::from_bytes_until_nul` are all outside the `kernel` symbol**:

| cell | input | kernel-exclusive /call | whole-program marginal /call | outside the symbol |
|---|---|---:|---:|---:|
| c-gcc | small | 12546 | 14966.13 | 2420 |
| c-clang | small | 11375 | 13494.13 | 2119 |
| c-gcc-h | small | 13747 | 16922.55 | 3176 |
| c-clang-h | small | 12761 | 15635.55 | 2875 |
| **safe_tuned** | **small** | **13302** | **23131.56** | **9830** |
| safe_naive | small | 24558 | 24572.00 | 14 (the driver loop) |
| unsafe | small | 19070 | 19084.00 | 14 |
| **safe_tuned** | **large** | **25657** | **32787.78** | **7131** |
| unsafe | large | 50160 | 50174.00 | 14 |

Read off the kernel-exclusive column, R3 looks **30% cheaper** than R4 on
`small`; on the correct column it is **21% dearer**, which is also what the wall
clock says (+23.35%). `results/tables/p11-nul-scan.md` reports the
kernel-exclusive column because that is what `harness/measure.py` records for
every pattern; **this section is the correction, and every number below is the
whole-program marginal.**

Until TASK_034 the shipped table also *told the reader to use that column* —
`harness/report.py`'s boilerplate ended "Use the `isolated` kernel-exclusive
figure, which needs no correction", i.e. the table instructed the reader to get
p11's headline comparison backwards (TASK_033_REVIEW minor 3). It now states the
condition and gives a check that needs no disassembly, because *"do the rungs
call the same routines?"* is not a question the table can answer: **every rung
runs the same input the same number of times, so rung-to-rung RATIOS of the
kernel-exclusive column are comparable with the same ratios of
`marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program
slope**. Measured over all eight patterns at `O3 / isolated / small`
(`.temp/p34/colcheck.py`): five agree to a worst ratio disagreement of 0.0052,
p02 distorts by 0.19 without reordering anything, and **p08 (10 inverted rung
pairs, worst 2.23) and p11 (3, worst 0.78) reverse real comparisons** — p08's is
the larger instance, and it inverts C-vs-Rust rather than R3-vs-R4.

`-O3 isolated`, `panic=unwind`. Wall clock is `taskset -c 3`, interleaved
round-robin, min of 31 reps; frequency scaling is on and cannot be disabled
without root; the box is shared. §11 is what licenses the `ns` column.

| rung | `n_fn`/nopad | small Ir/call | ns small | large Ir/call | ns large |
|---|---|---:|---:|---:|---:|
| R1 c-gcc | 81/79 | 14 966.13 | 13.408 ms | 35 446.38 | 12.154 ms |
| R1h c-gcc-h | 104/101 | 16 922.55 | 13.750 ms | 36 121.15 | 12.223 ms |
| R1 c-clang | 104/101 | 13 494.13 | 10.380 ms | 26 485.38 | 12.198 ms |
| R1h c-clang-h | 113/110 | 15 635.55 | 11.194 ms | 27 200.15 | 12.219 ms |
| **R2 safe-naive** | 117/113 | 24 572.00 | 16.647 ms | 79 262.00 | 16.033 ms |
| **R3 safe-tuned** | 134/129 | 23 131.56 | 19.606 ms | 32 787.78 | 13.756 ms |
| **R4 unsafe** | 123/117 | 19 084.00 | 15.895 ms | 50 174.00 | 15.040 ms |
| **R5 verus** | 123/117 | 19 083.00 | 15.973 ms | 50 173.00 | 15.048 ms |

Against R4:

| rung | `Ir` small | ns small | `Ir` large | ns large |
|---|---:|---:|---:|---:|
| c-gcc | −21.58% | −15.65% ⚠ | −29.35% | −19.19% ⚠ |
| c-gcc-h | −11.33% | −13.49% ⚠ | −28.01% | −18.73% ⚠ |
| c-clang | −29.29% | −34.70% ⚠ | −47.21% | −18.90% ⚠ |
| c-clang-h | −18.07% | −29.58% ⚠ | −45.79% | −18.76% ⚠ |
| **R2** | **+28.76%** | **+4.73%** | **+57.97%** | **+6.60%** |
| **R3** | **+21.21%** | **+23.35%** | **−34.65%** | **−8.54%** |
| R5 | −0.01% | +0.49% ⚠ | −0.00% | +0.05% ⚠ |

⚠ marks a cell with **no layout bracket**: `-align-all-functions` is an LLVM
knob so it reaches `c-clang` and not `c-gcc`, and a `c-gcc`-vs-`rustc`
comparison needs both endpoints bracketed by the same lever. Read the C `ns`
column as *not ranked* — p07's caveat, unchanged. R5's ⚠ is different and
weaker: R4 and R5 are byte-identical (§8), so the ±0.5% is the measurement's
own noise and the `Ir` **−1.00 per call** is the driver's, exactly as p16
records.

**Three results, in order of size.**

**(1) `Ir` and `ns` agree in direction on every rung and both inputs — once the
right column is used.** That is worth stating because the wrong column would
have produced a spectacular false disagreement (−30.25% `Ir` against +23.35%
`ns` for R3 on `small`). p11 therefore does **not** add to findings 5/6's list of
`Ir`-vs-`ns` direction reversals; it adds to the list of ways to manufacture one.

**(2) R3 crosses zero between the two inputs**, +21.21% on `small` and −34.65%
on `large`, and §4 shows the crossing is at a string length of **17–18 bytes**
with a named mechanism. This is the first pattern in this project where the
safety comparison **changes sign with the shape of the data rather than with the
rung**.

**(3) R1-vs-R1h, i.e. what the bound costs inside C**, and it is a per-**string**
constant, not a per-byte one:

| compiler | small (150 strings) | large (41 strings) |
|---|---|---|
| gcc | +1956.42 = **+13.04 /string** | +674.77 = **+16.46 /string** |
| clang | +2141.42 = **+14.28 /string** | +714.77 = **+17.43 /string** |

p02 measured the analogous figure as +5 (gcc) / +12 (clang) per *call*, flat in
the size of the copy. p11's is per *string* because the bound is inside the
per-string scan, and it is not quite flat in the length (13.04 → 16.46) because
`memchr` must also test its count where `strlen` tests only the sentinel.

## 4. The swept laws, and the safety tax decomposed to zero residual

`inputs/gen.py --sweep` band A: **64 consecutive string lengths** L = 1..64 at a
fixed 24 strings per window, so the scan's trip count is a constant of the file.
Whole-program marginal; a rung-to-rung difference on the *same* input is **exact**
because both rungs print the same checksum and the driver's `println!` digit term
cancels identically (`.memory/03-measurement.md`).

### 4a. R2 − R4 = 7.25000 Ir per byte of string, and every term is derived

```
R2 − R4 = 174.00000·L + c(r)        MAX RESIDUAL 0.000   over L = 4..64,
                                     all four residue classes, 61 points
c(0) = −255   c(1) = −357   c(2) = −411   c(3) = −465
```

`L = 1, 2, 3` are the only points off the line, each by exactly **+216**, and
they are off it for a reason rather than noisily: below `L = 4` the 4×-unrolled
fold body never executes at all, so both rungs take a different path. The
`−54·r` between the residue classes is R4's fold-remainder penalty (24 strings ×
2.25 Ir/byte × r) exactly, and the further −48 at `r ≥ 1` — `c(1) − c(0) = −102 =
−54 − 48` while `c(2) − c(1) = c(3) − c(2) = −54` — is consistent with that
loop's entry test, 2 instructions × 24 strings.

Divided by the 24 strings, **the tax is 7.25000 Ir per byte of string, flat in
L**, and it decomposes against the loop bodies of §2 with **zero fitted
parameters**:

| loop | R2 | R4 | difference | of which |
|---|---:|---:|---:|---|
| fold | 10.00000 | 5.75000 | **4.25000** | 2.00 check (`cmp;jae`) + 2.25 foreclosed unroll |
| scan | 9.00000 | 6.00000 | **3.00000** | 3.00 check (`lea;cmp;jae`), no unroll term |
| | | | **7.25000** | |

**4.25000 is p16's and p17's swept constant, reproduced on a third kernel** —
`.memory/01-ladder.md` finding 4 already generalised it ("4.25 is a property of
*rustc's checked indexed byte fold*, not of p16"), and p11 is the third
independent sighting, *including its 2.00 + 2.25 split*.

**3.00000 is new**, and it is the same bounds check costing one instruction
*more*. The mechanism is in the listing: the fold's induction variable is
blob-absolute (`add %rdx,%rax` is hoisted out of the loop), so its bound test is
two instructions; the scan's is window-relative, because the scan's own exit
test is `q < len`, so the check must first materialise `off + q` with a `lea`.
**The cost of a bounds check is not a constant of the language; it is a constant
of what the loop's induction variable already holds.**

### 4b. R3 − R4 changes SIGN at a string length of 17–18, and the mechanism is a threshold in `core::slice::memchr`

| L | R3 − R4 (Ir/call) | regime |
|---:|---:|---|
| 1 … 15 | **+524 … +697, no slope** | below the threshold: R3 pays an out-of-line call (**+25 Ir per string**) and buys nothing |
| 16 | +272 | |
| 17 | +113 | |
| **18** | **−95** | **sign change** |
| 24 | −1288 | |
| 64 | −5556 | |
| 20 … 64 (fit) | `−117.4·L + 1750 … 1858` | **−4.89 Ir per byte per string** |

`core::slice::memchr` reads two `u64`s per iteration (15 insns / 16 B =
0.937500 Ir/byte) **above 15 bytes** and takes a scalar byte loop below, which is
the `cmp $0xf,%rsi ; ja` at its entry. So the whole of R3's advantage is bought
above that threshold, and **`small` (mean 6.92) and `large` (mean 100.0) sit on
opposite sides of it**. That is why `spec.md` requires the two measured inputs to
have different mean string lengths, and it is the mechanism behind §3's result 2.

### 4c. C against R4, with both slopes falling out of the listing

⚠ **These two are FITS, and this file's opening rule says a five-decimal rate
here comes off a listing.** They are quoted at five decimals below because they
*agree* with a listing count to 0.04%, not because a listing produced them —
TASK_033_REVIEW minor 7, and the presentation is what was wrong rather than the
number. Recomputed at TASK_034 from the stored band-A marginals
(`.temp/p34/fit4c.py`, `.temp/p11/sweep_A.json`), **per residue class**, which is
the only honest way to fit a difference whose classes are staggered by 54 Ir:

| pair | 5 ≤ L ≤ 15, per class | per byte, per class | 20 ≤ L ≤ 64 | per byte |
|---|---|---:|---|---:|
| c-clang − R4 | slope −143.895 … −144.053, intercept +74 … +75 | **−5.99563 … −6.00219** | `−136.7·L − 59` | −5.68 … −5.71 |
| c-gcc − R4 | slope −89.895 … −90.053, intercept **+39 … −170** | **−3.74563 … −3.75219** | `−82.8·L − 202` | −3.43 … −3.46 |

(The intercept range on the `c-gcc` row used to read "−60 … −170"; the `r = 0`
class is **+39**, and dropping it made the stagger look one-sided.)

**So: R4's scan rate is 6.00000 Ir/byte off the listing (§2), and the C-vs-R4
fit corroborates it to 0.04% rather than measuring it.** Below 32 bytes glibc's
AVX2 `strlen` costs ≈0 per byte — one `vpcmpeqb` covers the whole string — so
the difference is R4's byte loop with essentially nothing left over. **And
3.75 = 6.00 − 2.25**, the 2.25 being gcc's *rolled* fold against clang's
4×-unrolled one: **the gcc-vs-clang gap on this kernel is the unroll factor and
nothing else.** `.memory/01-ladder.md` asks that a gcc-vs-clang gap be
established as a default or a capability before it is reported; here it is a
default, and the same one p16 and p17 found.

⚠ **"Nothing left over" needs one qualification, from §5a.** 1.00000 of R4's
6.00000 Ir/byte scan is the `if q >= len { break; }` guard — bookkeeping the C
rungs do **not** pay per byte, because `strlen`/`memchr` return the length
already. So the fit's agreement is *arithmetic* agreement: the C rungs pay ≈0
per byte for the scan, R4 pays 5.00 for the scan proper plus 1.00 for the guard
every rung in this pattern is required to carry.

## 5. The proof

`./verus_run.py patterns/p11-nul-scan/verus.rs` → **`12 verified, 0 errors`**.

Decomposition, each term measured with `--verify-function <name> --verify-root`:

```
scan_end 1 + fold_str 1 + str_walk 1 + kernel 4 + main 5 = 12
```

`u32_at`, `nstr_at` and `nul_scan_fold` are non-recursive spec fns and report 0;
`get_unchecked`, `load_input` and `emit` are `external_body` and report 0.
`--cfg slb_twin` gives **13**, the +1 being `slb_twin_get_unchecked` at
`1 verified`.

**The invariant shape.** There is no closed form for where a NUL scan stops —
the path is the data — so all three loops carry the relational invariant p16
found for its walk:

```
scan_end(buf, off, len, q) == scan_end(buf, off, len, p)      the scan
fold_str(buf, off, i, q, h) == fold_str(buf, off, p, q, 0)    the fold
str_walk(.., s, .., p, acc) == str_walk(.., 0, .., 4, 0)      the string walk
```

Two of the three exit two ways, so they need `invariant_except_break` plus a
loop `ensures`. The kernel carries **zero** nonlinear arithmetic: every
multiplication in it is by a literal, which is p11's contrast with p05 (two
`by (nonlinear_arith)` sub-proofs for `i*ncol + j`).

### 5a. The one thing that did not verify, and the fix is a program change

First run: **`9 verified, 3 errors`**, all three `possible arithmetic
underflow/overflow`. Two were mine (the invariants had dropped
`buf@.len() <= usize::MAX`). The third is real and is a result:

```
error: possible arithmetic underflow/overflow
   --> patterns/p11-nul-scan/verus.rs:370:13        <-- the PRE-FIX file
    |
370 |         p = q + 1;
    |             ^^^^^
```

(That paste is of a file that no longer exists — the one without the guard — so
its line number is not re-derivable from the tree and is left as it was recorded.
The shipped `verus.rs` writes the same statement at line 396.)

The scan may legitimately stop at `q == len` — that is what a window with no
terminator left does — so `q + 1` is `len + 1`. vstd has **no axiom that a slice
is at most `isize::MAX` bytes** (`.memory/04-verus.md`) and models `usize` as
possibly 32-bit, so nothing bounds `len` below `usize::MAX` and the obligation
is not dischargeable.

p17 bought its way out of the analogous obligation with a **second `requires`**
(`buf@.len() <= 9223372036854775807`) and a **third driver conjunct**. p11 does
not need to. Inserting

```rust
if q >= len {
    break;
}
```

*before* the cursor step makes `q < len`, and the obligation disappears — at zero
extra preconditions and zero driver statements. **And the inserted line is not a
prover concession**: it is the sentence *"a string whose terminator is missing is
the last string in the window"*, which is precisely the case R1 cannot represent.
It is in `idiom.required` for that reason.

**It is not free in instructions, and this file said it was until TASK_034.**
The sentence above used to end "…zero driver statements, *and zero
instructions*", and the header comments of `unsafe.rs` and `verus.rs` said the
same (at `unsafe.rs:38` and `verus.rs:32-34` as those files were shipped before
this task); `c/main.c`'s was the only one that was right, because it claims zero
cost in driver statements and preconditions only. TASK_033_REVIEW deleted the three
lines (`.temp/r33/u_noqguard.rs`) and measured the difference; the static counts
and the two marginals were re-measured from a fresh build at TASK_034
(`.temp/p34/guardcost.py`, interleaved by cell) and the four-length law is that
review's. Checksums are unchanged on every input:

```
static   kernel 123 -> 114 insns (nopad 117 -> 109), md5_fn 9145e57079d2 -> 54f39868dbf4
scan     6 insns (cmpb sete je inc cmp jne)  ->  5 (cmpb je inc cmp jne)
marginal small  19084.00 -> 17481.00   (+1603.00 = +8.4% of R4)
marginal large  50174.00 -> 45909.00   (+4265.00 = +8.5% of R4)
   L    u_baseline   u_noqguard  guard cost  scanned B  per byte
   8       3329.00      3040.00      289.00        216    1.3380
  16       5585.00      5104.00      481.00        408    1.1789
  24       7841.00      7168.00      673.00        600    1.1217
  64      19121.00     17488.00     1633.00       1560    1.0468
```

**`guard = 24·L + 97` at `k = 24`, zero residual over four string lengths =
1.00000 Ir per scanned byte + 3 per string + 1 per call.** Cross-check on
`large`: `4100 + 41` scanned bytes `+ 3·41 + 1 = 4265`, measured **4265**.

**Mechanism**: with the guard the scan loop has to carry its *exit reason* out
in a register — the `sete %bpl` of §2's R4 row exists only so the post-loop
`test %bpl,%bpl; je` can implement `if q >= len`. Delete the guard and the loop
falls through and the `sete` disappears.

**So publish the trade, not the retraction, because the corrected result is the
better one.** p17 and p11 buy the *same* fact — that the cursor step cannot
overflow — and they buy it in different currencies:

| route | preconditions | driver | instructions |
|---|---|---|---|
| p17 — a second `requires` | **+1 clause** | +1 conjunct | **0** |
| p11 — a guard in the program | 0 | 0 | **+1.00000 Ir/scanned byte, 8.5%** |

Neither is free, and the table is now in `.memory/04-verus.md`. Where the cost
lands matters too: **the C rungs do not pay it per byte**, because their scan is
a libcall that already returns the length, so of R4's 6.00000 Ir/byte scan
**1.00000 is shared-idiom bookkeeping that `strlen`/`memchr` get for free** —
which qualifies §4c, and §4c says so.

⚠ **The line stays.** It is in `idiom.required` for all six rungs, every cell
pays it, and it does **not** contaminate §4a's 3.00000: without the guard the
two scan loops are 8 (R2) and 5 (R4) instructions and the difference is
`lea; cmp; jae` either way (TASK_033_REVIEW's clean negative, on
`.temp/r33/r2_noqguard.rs`). The defect was the word "free", not the line.

This is p07's finding — *the spelling that makes the proof go through is the one
that names the bug* — arriving on a completely different kernel and a completely
different obligation (p07's was an `usize` underflow in an inclusive bound;
p11's is an `usize` overflow in a cursor step).

### 5b. TCB tally

```
$ grep -c 'assume('              patterns/p11-nul-scan/verus.rs   -> 0
$ grep -c 'assume_specification' patterns/p11-nul-scan/verus.rs   -> 0
$ grep -c 'verifier::external\]' patterns/p11-nul-scan/verus.rs   -> 0
$ grep -n  'verifier::external_body' ...                          -> 217, 266, 278
```

**TCB: 6 lines across 3 items.**

| item | lines | `unsafe`? | `requires` | `ensures` |
|---|---:|---|---|---|
| `get_unchecked` | 1 | yes — the only `unsafe` token in the file | `i < v@.len()` | `r == v@[i as int]` |
| `load_input` | 4 | no | — | — (deliberately: an `ensures` here would be an axiom about a file's contents) |
| `emit` | 1 | no | — | — |

Every `external_body` item is counted, not just the interesting one
(`.memory/04-verus.md`: the pilot was published as "one 3-line wrapper" and the
true tally was three items, one of which was `main`).

### SLB-TRUSTED-ARGUMENT verus.rs get_unchecked

(a) *Is the twin's body the right checked stand-in?* The trusted body is
`unsafe { *v.get_unchecked(i) }` and the twin's is `v[i]`. Those are the same
operation with and without the bounds check that `<[T]>::get_unchecked`'s
documented contract makes the caller's responsibility, so a `requires` too weak
to license the first is too weak to license the second, and Verus can see the
second. Nothing else is in either body: no arithmetic, no second read, no side
effect.

(b) *Is the `ensures` complete with respect to every unchecked operation the
body performs?* The body performs exactly one unchecked operation — a read of
`v` at index `i` — and the single `ensures` clause `r == v@[i as int]` names it
and its result. There is no second index, no write, no aliasing and no
provenance step for a clause to be missing. This is the labelled blind spot in
`.memory/04-verus.md` (a body that also read `i + 1` would pass every mechanical
check), and the only backstop for it is Miri on `unsafe.rs`, which this pattern
runs on all seven inputs (§8).

(c) *Does each clause mean the same in both configurations?* Yes, and it is
checkable rather than asserted — **but count the token the way the gate counts
it, which this paragraph did not until TASK_034.** Three counts, all measured on
the shipped file and all different:

```
$ grep -c -o 'slb_twin'      patterns/p11-nul-scan/verus.rs   -> 3   (246, 248, 249)
$ grep -c -o -E '\bslb_twin\b' ...                            -> 2   (246, 248)
```

Line 246 is a **comment** explaining the attribute, 248 is the attribute, and
249 is the twin's own name `slb_twin_get_unchecked`, which is a different
identifier because `_` is a word character. What `harness/check.py` scans is
`vparse.blank_noncode(...)`, i.e. the token stream with comments and string
literals blanked, and there the count is **1 — the attribute, and nothing else**,
which is what the gate prints (`the token slb_twin occurs nowhere but on the 1
twin #[cfg(slb_twin)] attribute(s)`). A comment cannot change codegen, so the
argument is unaffected and is in fact tighter than "once" was: the two
compilations differ in nothing but the twin's existence. `i`, `v` and `v@.len()`
denote the same values in both, there is no `#[cfg]`-varying `const`, `type` or
`use` anywhere in `verus.rs`, and the file includes nothing but
`common/driver.rs`, which is outside `verus!` and carries no `slb_twin`.

### 4d. Band B — the per-STRING term, and the two bands cross-check exactly

Band B holds the length at 24 and walks the string count K over 16 values, which
is what separates the per-**call** term from the per-**string** one
(`.memory/01-ladder.md`: separating those is where p16's `nrec + 3` and p05's
"+11.00 flat" both died).

```
R2 − R4     =    9.0000 + 163.00000·K     MAX RESIDUAL 0.000   (16 points)
R3 − R4     =   −3.2714 −  53.50725·K     max residual 1.533
c-clang − R4 =   2.5221 − 140.92301·K     max residual 1.832
c-gcc − R4  =   15.5221 −  88.92301·K     max residual 1.832
```

**The two bands agree to the instruction where they meet.** At `K = 24, L = 24`
band B predicts `24 × 163 + 9 = 3921` and band A's `r = 0` law predicts
`174 × 24 − 255 = 3921`. Neither was fitted to the other.

Two things this settles that band A alone could not:

- **The per-CALL term is ≤ 16 Ir on every pair.** p11's whole safety tax is
  per-string and per-byte; there is essentially no constant to amortise, which
  is the opposite of p16's and p17's shape (`O(1)` per call, 0 per byte).
- **Does R3's tax amortise?** It does better than amortise: it is a per-string
  constant of ≈ +25 Ir below the 16-byte threshold — so per byte it *decays* as
  1/L — and it is **negative and linear in L above it**. R3's cost does not go to
  zero along the input axis; it goes through zero and keeps going.

## 6. The proof mutants — three, and each fails for a different reason

`.memory/05-layout.md` item 11: a Verus file that does not verify cleanly cannot
live in the pattern directory, so each mutant is generated into `.temp/` from the
**shipped** `verus.rs` by exact-string substitution with an asserted hit count
(`controls/gen_controls.py`), and this section carries the commands and the
output.

⚠ **The line numbers below are `verus.rs`'s, plus the mutant's own offset, so an
edit to the file's header comment moves them and the paste goes stale in a way
no gate stage can see.** TASK_033_REVIEW found all three stale by +2; they were
re-derived at TASK_034 *after* the §5a correction had moved them again, by
regenerating and re-running rather than by arithmetic:

```
$ python3 patterns/p11-nul-scan/controls/gen_controls.py
$ ./verus_run.py .temp/p11/controls/m1_weak_requires.rs [--cfg slb_twin]
```

The verdicts and the counts are what the section is about; treat a drifted line
number as a stale citation and re-run the two commands above.

### 6a. `m1_weak_requires` — one character; the twin is the sole VERUS-LEVEL catcher, and the pin catches it too

`i < v@.len()` → `i <= v@.len()` in the trusted item **and** its twin, so the
signatures still match (5c-twin's limb (i) does **not** fire).

```
$ ./verus_run.py .temp/p11/controls/m1_weak_requires.rs
verification results:: 12 verified, 0 errors                 <-- SHIPPED CONFIG PASSES

$ ./verus_run.py .temp/p11/controls/m1_weak_requires.rs --cfg slb_twin
error: precondition not met: index in bounds for this access
   --> .temp/p11/controls/m1_weak_requires.rs:267:5
    |
267 |     v[i]
    |     ^^^^
verification results:: 12 verified, 1 errors
```

R5's trusted base would otherwise axiomatise that **reading one byte past the end
of a slice is defined and equals `v@[i]`** — which is CWE-125, the bug class p11
exists to model. The tautology probe cannot see it (it is not a tautology),
parameter coverage cannot see it (both parameters appear), and deletion is not
applied to trusted items by construction. **Among the Verus stages the verified
twin is the only mechanism that catches it** (`.memory/04-verus.md`), and this is
the first time p11 could have shown that, so it is stated rather than assumed.

⚠ **CORRECTED AT TASK_056. Until then this paragraph read *"The contract pin does
not move (both clauses change together)"* and *"The verified twin is the only
mechanism in this project that catches it"*. The first is FALSE.** Both clauses
changing together is exactly what makes the pin fire twice, because `spec.md`'s
`verus.items` pins the clause text of **`slb_twin_get_unchecked` as well as
`get_unchecked`**. Stage 5a therefore fails, and it runs **before** 5c-twin.
Measured with `harness/limbs.py` on the mutant this pattern's own
`controls/gen_controls.py` produces:

```
$ python3 harness/limbs.py patterns/p11-nul-scan verus.rs \
      patterns/p11-nul-scan/verus.rs .temp/p11/controls/m1_weak_requires.rs
=== verus.rs                 shipped 12/0   twin 13/0   NO LIMB FIRES
=== m1_weak_requires.rs      shipped 12/0   twin 12/1
      [5a-clause] get_unchecked.requires          ['i <= v@.len()'] != pinned ['i < v@.len()']
      [5a-clause] slb_twin_get_unchecked.requires ['i <= v@.len()'] != pinned ['i < v@.len()']
      [5ct-run]   --cfg slb_twin: 12 verified, 1 errors
                  error: precondition not met: index in bounds for this access
```

**Two limbs fire, not one: 5a with two clause diffs, and 5c-twin limb (ii).**
The rule (TASK_054, TASK_056, measured on six patterns): **the twin is the sole
catcher only of a mutant that edits `spec.md` in the same commit** —
TASK_008_REVIEW's original attack, and the reason the twin exists. p16, p17, p09
and p02 build theirs that way and say so; this one does not. **The `identity` pin
does not move either**: a `requires` is ghost and cannot reach codegen (measured
on p12 at TASK_054 and on p03 at TASK_056, byte-identical kernels from
equal-length source paths). An exec-code edit can move it; this cannot.

⚠ **`controls/gen_controls.py`'s own header comment for this mutant repeats the
overclaim** — *"The twin is the only mechanism in the project that catches it"* —
and it is generated text, so it is reproduced in every regenerated copy of
`.temp/p11/controls/m1_weak_requires.rs`. It is left alone here because editing a
generator is out of TASK_056's scope; read it as *sole Verus-level* catcher.

### 6b. `m2_unbounded_scan` — deleting the bound from the SPEC is a termination failure

The `q >= len` arm is deleted from `scan_end`, which turns the spec function into
`strlen` — R1's scan, exactly.

```
$ ./verus_run.py .temp/p11/controls/m2_unbounded_scan.rs
error: could not prove termination
   --> .temp/p11/controls/m2_unbounded_scan.rs:140:9
    |
140 |         scan_end(buf, off, len, q + 1)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
error: loop invariant not satisfied
   --> .temp/p11/controls/m2_unbounded_scan.rs:348:15
...
362 |                 q as int == scan_end(buf@, off as int, len as int, p as int),
    |                 ------------------------------------------------------------ failed this invariant
verification results:: 10 verified, 2 errors
```

**This is the sharpest statement of what p11's bug is: a scan with no bound is a
recursion with no termination argument.** R1's `strlen` is not merely an
unchecked read — it is a function that cannot be *written down* as a total spec
function, and the `decreases` clause is what says so. `.memory/04-verus.md`
records p16's `decreases` catching a hang with no test run; this is the same
mechanism aimed at the specification rather than at the code, and it is the
cheapest honest demonstration on this pattern of something a proof gives that a
test suite does not.

### 6c. `m3_exec_offbyone` — R1's bug written into R5

The exec scan bound `while q < len` widened to `while q < len + 1`.

```
$ ./verus_run.py .temp/p11/controls/m3_exec_offbyone.rs
error: possible arithmetic underflow/overflow          (`len + 1`)
error: invariant not satisfied at end of loop body     (`p <= q <= len`)
error: precondition not satisfied
   --> .temp/p11/controls/m3_exec_offbyone.rs:361:16
    |
229 |         i < v@.len(),
    |         ------------ failed precondition
...
361 |             if get_unchecked(buf, off + q) == 0 {
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^
verification results:: 11 verified, 1 errors
```

The failing precondition is `get_unchecked`'s `i < v@.len()` — the obligation
that carries p11's entire memory-safety claim — so this mutant confirms the
claim is load-bearing rather than decorative.

## 7. The adversarial table, per rung

`-O3 isolated`, `.temp/p11/gate.log` stages 4 and 7. `=` means "agrees with
`model.py`".

| input | model's answer | c-gcc / c-clang (R1) | R1h ×2, R2, R3, R4, R5 | ASan on R1 |
|---|---|---|---|---|
| `adversarial-nonul` | 18024987679707349248 | **1078694406687294464** | = | **heap-buffer-overflow, READ of size 13, 0 bytes after a 66-byte region, `__interceptor_strlen` ← `c/kernel.c:68`** |
| `adversarial-count` | 11408910424468685312 | **7133615092521126400** | = | **heap-buffer-overflow, READ of size 21, 0 bytes after a 40-byte region, same frame** |
| `adversarial-zerotail` | 17859238140672197760 | = | = | clean, exit 0 |
| `adversarial-empty` | 227437609984 | = | = | clean, exit 0 |
| `adversarial-stride3` | 0 (zero kernel calls) | = | = | clean, exit 0 |

Four things worth stating.

**1. `nstr` bounds nothing, and `zerotail` is the measurement that says so.**
`adversarial-count` and `adversarial-zerotail` carry the **identical header**
(`nstr = 4096` against three strings written) and identical first three strings;
they differ in **20 tail bytes and nothing else** — non-zero filler in one, NUL
in the other. The first overruns R1; the second is clean in every cell, walks 23
strings, stops on `p >= len` **4073 strings short of the declared count**, and
returns the model's answer. So the loop is bounded by the *sentinel* and by the
*window*, never by the count, and that is a controlled comparison rather than a
remark. TASK_033 predicted `adversarial-count` as "the scan walks past the
window"; that is right, but only because its tail is unterminated — the count
lie on its own does nothing, which is what `zerotail` was added to show.

⚠ **That sentence was FALSE about the shipped tree until TASK_034, and `cmp`
found it in ten seconds** (TASK_033_REVIEW major 2). `inputs/gen.py` drew the
three strings **twice**, once per blob, from the same sequentially advancing
RNG, so the two windows shared their string *lengths* (4/6/3) and terminator
positions but **not their bytes**: 33 differing bytes, not 20. The generator now
draws them once and reuses them (`shared = strings(rng, COUNT_LENS)`), which is
the fix the reviewer asked for — weakening the sentence instead would have
thrown away the only controlled row in the table. Re-measured on the regenerated
blobs with `.temp/p34/paircmp.py`:

```
count    64 B          n differing bytes: 20
zerotail 64 B          indices: [44 … 63]        (all 20 in the tail)
a payload: 00100000 8d6df4cd 00 1357338d5973 00 2b49f9 00 <20 non-zero>
b payload: 00100000 8d6df4cd 00 1357338d5973 00 2b49f9 00 <20 NUL>
```

The conclusion never depended on it — string content cannot change whether
`strlen` runs off the end — but "a controlled comparison rather than a remark"
did. **Regenerating moved exactly three blobs**: `adversarial-zerotail.bin` (the
point), `adversarial-stride3.bin` (random filler, **zero** kernel calls, answer
still 0) and `sweep-len01k24.bin`, both of the last two only because the RNG
stream shifted; `adversarial-count.bin` is byte-identical to the one every
earlier number was measured on. Nothing downstream of `sweep-len01k24.bin`
moved, and the reason is worth writing down because it looks like a bug and is
not: `random.shuffle` uses rejection sampling, so its *word* consumption is
data-dependent, and the two streams — 4 words apart after the deleted draw —
re-converge inside that file's shuffles (MT index 343 vs 339 before it, and the
**entire state** equal after it). Band A's lengths are constant within a file, so
`sweep-len01k24`'s trip counts, and therefore §4a's laws, cannot move either;
only its bytes and its checksum do. `zerotail`'s model answer is now
**17859238140672197760** (was 6311443662811229568) and both of R1's wrong
answers are unchanged.

**2. R1 overruns AT MOST ONCE PER CALL, unlike p16.** R1 keeps
`if (p >= len) break`, so the *cursor* is bounded even though the *scan* is not:
the first unterminated string sets `q > len` and the very next test ends the
walk. p16's missing check made `end - p` underflow and the walk ran **200 MiB /
6459 records** past the window without terminating (`.memory/01-ladder.md`).
Same CWE, opposite blast radius, and the difference is which loop lost its
bound.

**3. `_FORTIFY_SOURCE` does not blind ASan here, and it was worth checking.**
`.memory/00-environment.md` records that this box's gcc rewrites `memcpy` to
`__memcpy_chk`, which ASan does not intercept, so gate stage 7 (gcc-only, box
defaults) is structurally blind to that class. glibc ships **no fortified
`strlen`**, so R1's call reaches `__interceptor_strlen` and fires. Checked on
the ASan build's own backtrace, not assumed.

**4. R1's two wrong answers were deterministic here** — gcc and clang print the
same value, and it reproduces across runs, because the bytes just past a small
`malloc` block are stable in this driver. That is luck and not a property; the
gate records the value rather than requiring it, and a reviewer should expect it
to move on a different allocator or a different `.bss` layout.

## 8. Identity, Miri, and the twin (still idle, sixth pattern running)

**R4 ≡ R5, `-O3 isolated`, `exact`:** `md5_fn 9145e57079d2` and
`md5_raw_equal=True`, 123 instructions each, 3 instructions of padding each. At
`O0` it is `norel` — the crate names differ in length so the `call`
displacements do, which is link layout and not codegen. So the project's
headline structural result now covers a kernel with **three nested loops, two of
them carrying `invariant_except_break` plus a loop `ensures`, three recursive
spec functions and zero nonlinear arithmetic**. Whole-program the pair differs by
**−1.00 Ir/call** on both inputs; that is the driver's, exactly as p16 records,
and finding 1 rests on the raw-byte digest and not on it.

**Miri: 7 of 7 inputs, no UB, no blocked rows, and it is FAST.** Reproduced with
`.temp/p11/miri_time.py`, which is `check.py`'s invocation verbatim
(`n_iters` rewritten to 4):

```
adversarial-count.bin      0.2 s    adversarial-zerotail.bin   0.2 s
adversarial-empty.bin      0.1 s    large.bin                  1.8 s
adversarial-nonul.bin      0.1 s    small.bin                  0.5 s
adversarial-stride3.bin    0.1 s
```

`.memory/02-bench-rules.md` puts the budget at ~3.05 M folded bytes in 180 s;
p11's worst row visits `4 × 4145` bytes twice = 33 160, i.e. **~100× inside it**,
and `large.bin`'s 1.8 s is almost entirely the 8 MB payload `to_vec`. Sizing this
in `inputs/gen.py` rather than discovering it afterwards is `.memory/05-layout.md`
demand 8 and it cost nothing here.

**The twin is idle, for the sixth pattern running.** p11 wraps the same
single-clause `<[u8]>::get_unchecked` that p01, p02, p16, p17, p05 and p07 wrap,
so 5c-twin's green line is not evidence that anything hard was checked — except
that §6a *did* exercise it, on a mutant, where it was the only **Verus** stage
that moved (stage 5a's contract pin moved too, twice — corrected at TASK_056; the
sentence here used to read *"it was the only stage that moved"* and that is
false).
`.memory/04-verus.md`'s standing item still applies: the twin's value accrues
from the first pattern needing a **multi-clause** trusted accessor, which is a
property of the intrinsic being wrapped and not of the pattern number.
Manufacturing one here to exercise the mechanism would be gaming the gate.

### 8b. What the anti-collapse stage actually certifies here

```
probe small.bin   work_per_call=1192 byte(s)  => derived floor  298.0 Ir/call
probe large.bin   work_per_call=4145 byte(s)  => derived floor 1036.2 Ir/call
ok  64 cell/probe pairs: marginal Ir per call 13494...269106, all above the
    derived floor (tightest margin 25.6x over a declared 0.25 Ir/byte);
    d(Ir)/d(work) 3.27...65.18 (rate 0.25)
```

`.memory/02-bench-rules.md` asks every pattern to say **which way
`work_per_call` errs** and how loosely the floor is cleared. p11's errs
**strict** — `spec.md`'s `collapse.note` has the arithmetic: `stride`
over-counts by the 4 header bytes and by one terminator per string (12.6% of
`small`, 1.0% of `large`, neither folded) and under-counts by the whole second
pass over every byte, and the under-count is the larger term on both inputs. The
tightest margin is **25.6×**, i.e. this stage tolerates a ~96% loss of work
before it objects, which is why it is a *not-collapsed smoke test* and not an
anti-collapse gate. What certifies that the work happened is step 2, the model
checksum.

### 8a. A harness observation, reported at TASK_033 and FIXED at TASK_034

`harness/asm.py::is_bulk_symbol` recognised the `mem*` family and **not the
`str*` family**:

```
$ python3 -c "import sys;sys.path.insert(0,'harness');import asm
> for s in ['strlen','strlen@plt','__strlen_avx2','memchr@plt','strnlen','__strlen_chk']:
>     print(s, asm.is_bulk_symbol(s))"
strlen         False        <-- before TASK_034; all five str* rows are now True
strlen@plt     False
__strlen_avx2  False
memchr@plt     True
strnlen        False
__strlen_chk   False
```

Stage 3a's structural anti-collapse check accepts *"a backward branch **or** a
call to a known bulk-memory routine"*, and that alternative exists because a
`memcpy`-shaped kernel has no back edge of its own (TASK_005). p11's C kernels
were unaffected — they keep the fold loop, so they have a real back edge, and
`c-gcc-h`/`c-clang-h` showed `memchr@plt` in the gate's own table — but **a
kernel whose only work is a `strlen` would have neither, and stage 3a would fail
a perfectly healthy cell**, which is the exact false-failure the bulk-memory
alternative was added to prevent, one function family short.

TASK_033 reported it rather than editing it (that task's constraint).
**TASK_034 landed it**: `_BULK_STR_WORDS` covers the search, copy and compare
routines whose body is a loop over the caller's buffer — `strlen`, `strnlen`,
`strchr`, `strstr`, `strcpy`, `strcmp` and the rest, in all three spellings
(`strlen@plt`, glibc's `__strlen_avx2`, fortify's `__strcpy_chk@plt`) — while
the *conversions* stay out, because a kernel whose only call is `strtoul` really
has done no bulk work: `strtoul`, `strtol`, `strtod`, `strerror`, `strsignal`
and `__strtol_internal` all still answer `False`. 27 selftest cases were added
beside the `mem*` family's 20, run at gate stage 0 and therefore inside
`source_sha256`. **Visible effect on this pattern**: `c-gcc` and `c-clang` now
report `bulk=['strlen@plt']` in the gate's own table where they reported nothing,
which is what §12a describes.

## 9. Dead code that is kept on purpose

`if len < 4 { return 0; }` is unreachable in this benchmark, because the driver
guard is `stride_w >= 4` and `len` is always `stride`. It is kept so the kernel
is **total** and its `requires` stays purely structural: the alternative — a
`len >= 4` precondition — would be a precondition about the driver's own guard
rather than about the buffer, and `.memory/02-bench-rules.md` is explicit that a
`requires` narrow enough to make the proof easy is a `requires` no caller can
discharge. It costs one compare per call.

The `nstr == 0` guard is *not* dead in the same way. It is reachable from the
wire format — any window may declare zero strings — and it is what makes the
`0 < nstr` invariant available to the proof. No shipped input happens to take
it: `adversarial-empty.bin` declares 8 strings of length 0, not 0 strings.

## 10. The spelling spread

`.memory/05-layout.md` item 13 makes this section mandatory for any pattern with
more than one measured spelling, and `.memory/01-ladder.md` finding 3 requires
**at least two independent in-contract R3 spellings, with the cheaper quoted**.
All numbers are the whole-program marginal Ir/call, built by
`controls/gen_controls.py` and measured by `.temp/p11/run_controls.py`. Every
control prints `model.py`'s answer on all seven inputs.

### 10a. The R3 side — four in-contract spellings, and the cheapest changes with the input

| spelling | small | small − R4 | large | large − R4 | in contract? |
|---|---:|---:|---:|---:|---|
| `safe_tuned` (**shipped**), `CStr::from_bytes_until_nul` + `iter().fold` | 23131.56 | +4047.56 | **32787.78** | **−17386.22** | yes — **cheapest found on `large`** |
| `r3_takewhile`, `iter().take_while(..).count()` | **18618.00** | **−466.00** | 46210.00 | −3964.00 | yes — **cheapest found on `small`** |
| `r3_position`, `iter().position(\|&b\| b == 0)` | 19146.00 | +62.00 | 46374.00 | −3800.00 | yes |
| `r3_nowin`, no window reslice | 24345.56 | +5261.56 | 33129.78 | −17044.22 | yes |
| `r3_idxfold`, shipped scan + indexed fold | 24591.56 | +5507.56 | 49351.78 | −822.22 | yes — dearest found |
| `u_fused`, fold inside scan | 16090.00 | −2994.00 | 50218.00 | +44.00 | **no** — deletes `slen` |

* **fixed-R4 bound** (`R3ship − R4ship`, R4 held by fiat — the only sound
  quantity per `.memory/01-ladder.md`): **+4047.56 on `small`, −17386.22 on
  `large`**.
* **R3-side span**, cheapest-found to dearest-found in contract:
  **−466.00 … +5507.56** on `small` (width 5973.56) and
  **−17386.22 … −822.22** on `large` (width 16564.00).
  On `large` **both endpoints are negative**: every in-contract R3 spelling
  measured is cheaper than the shipped R4.
* Write **"cheapest found"**, never "minimum". Five p05/p16/p07 minima have been
  published and every one was refuted by the next agent's first lever.
* ⚠ **No single spelling is cheapest on both blobs**: `r3_takewhile` is 4513.56
  Ir/call **cheaper** than the shipped cell on `small` and 13 422.22
  **dearer** on `large`. Mechanism: `take_while().count()`
  and `position()` are scalar byte loops (5.00000 Ir/byte) with no call, so they
  win where the strings are short and the call dominates, and lose where they are
  long and `core::slice::memchr` engages. **So a cheapest-found figure must name
  its INPUT as well as its spelling** — p16's TASK_027 finding, reproduced here
  with a *mechanism* rather than a remainder-tail accident.
* The **out-of-contract** fused spelling is cheaper on `small` (−2994) and
  dearer on `large` (+44). On p05 and p16 the excluded spellings were uniformly
  cheaper, which made the declaration look like it might be protecting a number;
  here the exclusion cuts both ways.

### 10b. The R4 side — degenerate, fourth pattern running, and this time the gap it hides is 35%

TASK_026 §0 item 3 and `.memory/01-ladder.md`: **a rung covered by an `identity`
pin is chained to the prover**, so an R4 candidate is not a rung until its R5
twin verifies. All three candidates have a twin in `controls/gen_controls.py`
and all three have been run.

| spelling | small − R4 | large − R4 | Verus verdict |
|---|---:|---:|---|
| `r4_forfold` — fold loop as `for i in p..q` | **0.00** | **0.00** | **`12 verified, 0 errors`** — admissible, and it does not move |
| `r4_ptr` — `as_ptr()` / `add()` | 0.00 | 0.00 | **DISQUALIFIED** |
| `r4_cstr` — R3's scan, R4's fold | +3447.56 | **−17526.22** | **DISQUALIFIED** |

```
$ ./verus_run.py .temp/p11/controls/r4_forfold_twin.rs
verification results:: 12 verified, 0 errors

$ ./verus_run.py .temp/p11/controls/r4_ptr_twin.rs
error: The verifier does not yet support the following Rust feature:
dereferencing a raw pointer. Currently, Verus only supports raw pointers
through the permissioned raw_ptr interface

$ ./verus_run.py .temp/p11/controls/r4_cstr_twin.rs
error: `core::ffi::c_str::CStr` is not supported (note: you may be able to add a
Verus specification to this type with the `external_type_specification` attribute)
error: `core::ffi::c_str::FromBytesUntilNulError` is not supported ...
error: `core::ffi::c_str::impl&%5::from_bytes_until_nul` is not supported (note:
you may be able to add a Verus specification to this function with
`assume_specification`) ...
error: `core::ffi::c_str::impl&%5::to_bytes` is not supported ...
error: aborting due to 4 previous errors
```

**So the pair interval is DEGENERATE — the only R4 shown admissible besides the
shipped cell measures exactly `R4ship`, so the R4 endpoint has zero measured
width and the interval collapses onto the R3-side span.** That is the fourth
pattern running (p05, p16, p07, p11) and it is stated as degeneracy rather than
as unavailability, because it stops being degenerate the day somebody builds an
admissible R4 that moves.

It is degenerate in the strongest available sense here: `r4_forfold` is not
merely equal in `Ir`, it is **byte-identical to the shipped R4** —
`md5_fn 9145e57079d2`, `n_fn 123`, `asm.identity_level` `exact`. Verus derives
`p <= i` and the `decreases` for a range `for`, so the twin needed only those two
ghost deletions and LLVM emits the same machine code either way.

**The spelling that would settle the question HAS now been built, and it is
inadmissible by measurement rather than by expectation** (TASK_033_REVIEW; the
twin re-run at TASK_034). The candidate is specific: a **hand-written SWAR scan
in unsafe Rust**, reading the window eight bytes at a time and applying
`core::slice::memchr`'s own `(x − 0x01…01) & ~x & 0x80…80` test. It needs a `u64`
load out of a `&[u8]`, and at the pinned vstd every route to one is closed:

```
$ ./verus_run.py .temp/r33/r4_swar_twin.rs
error: `core::num::impl&%9::from_le_bytes` is not supported (note: you may be
able to add a Verus specification to this function with `assume_specification`)
error: aborting due to 1 previous error
```

`read_unaligned` is `is not supported` too (measured on p05 and p16), and the
`vstd::raw_ptr` `PointsTo` model is a new trusted item by construction. So the
paragraph that used to end "*likely* inadmissible … and **likely is not
measured**" is retired: all three routes are closed **by measurement**, and
`from_le_bytes` is *separately* forbidden by p11's own `idiom.forbidden[1]`, so
the spelling is doubly out of the admissible class.

⚠ What survives is the weaker, still-true version of the caveat: an *exec* SWAR
R4 has still not been compiled and priced, so nobody knows how much it would
have moved — pricing it would describe a cell that cannot ship. And
`.memory/01-ladder.md`'s other two instances of the gap stand: p05's unbuilt
zero-guard deletion and p16's unbuilt hand-unrolled 32× fold. The claim p11 is
entitled to remains *no admissible R4 has been **shown** to move*, not *none
can*.

⚠ **What is new here is the SIZE of what the pin excludes.** On p05 and p16 the
inadmissible R4 spellings moved the number by a header read — `4·nrec`, `7 flat`.
On p11 the inadmissible spelling is `r4_cstr`, and it is **17 526 Ir/call, 35% of
the kernel**, on `large`. R4 is defined by *permission*, so `r4_cstr` is
textually a perfectly good unsafe rung: it uses `get_unchecked` for the fold and
the standard library's bounded NUL search for the scan, and it is *correct*.
What disqualifies it is that `CStr` has no vstd specification, and shipping it
would cost **four new trusted items** on a pattern whose entire memory-safety
claim is one trusted `requires`.

**This is the sharpest instance in the project of `.memory/01-ladder.md`'s
R4-by-permission paragraph.** The safe class can reach `core::slice::memchr` at
zero TCB and the unsafe class cannot reach it at all; the two classes are
**incomparable**, and on p11 the incomparability is worth a third of the kernel
rather than a handful of instructions. It is also why R3-beats-R4 on `large` is
*not* a defect in R4: no admissible R4 can close it.

## 11. Wall clock — the noise floor first, then the mode, then the statistic

`.memory/03-measurement.md` and TASK_033: run `common/layout/order.py` **before**
believing any `ns` number, and `layout_gen.py` + `loopfit.py` if a mode shows.
Both were run. `taskset -c 3`, 31 reps, interleaved by cell.

### 11a. Identical-copy noise floor, and p11 is protocol-INSENSITIVE

`python3 common/layout/order.py --pattern p11-nul-scan --copies 31 --reps 31`,
31 **byte-identical** copies, four passes over three schedules, `small.bin`:

| pass | schedule | R2 floor | R3 floor | R4 floor | R2 − R4 | R3 − R4 |
|---|---|---:|---:|---:|---:|---:|
| 0 | `round_robin` (shipped) | 4.25% | 1.46% | 3.46% | +3.96% | +22.18% |
| 1 | alternating (`measure.py`) | 4.95% | 1.76% | 1.45% | +3.96% | +22.07% |
| 1 | **blocked (the bug)** | 1.39% | 1.15% | 1.41% | **+3.97%** | **+22.06%** |
| 1 | `round_robin` | 1.25% | 1.46% | 3.37% | +4.04% | +22.03% |

**p11 is protocol-insensitive**: blocked and alternating agree to 0.01 and 0.04
points, so it joins p01, p02, p07, p08, p16 and p17 and not p05
(`.memory/03-measurement.md`). The identical-copy *range* reaches 4.95%, but the
statistic being compared is the **median of 31 copies**, which reproduces to
**±0.08 points** across four passes — so R3's +22% is not in doubt and R2's +4%
is quoted with the caveat that it is the same size as a single copy's range.

### 11b. A layout mode exists, it belongs to R4 alone, and it is on `small` only

`layout_gen.py --seeds 21 --aligns 9 --reps 31 --passes 2` (31 layouts per rung),
then `analyze.py` / `loopfit.py`:

```
unsafe   bit4: x1.0640 PERFECT (n=19/12)      small, pass 0
unsafe   bit4: x1.0585 PERFECT (n=19/12)      small, pass 1
safe_naive / safe_tuned: no (loop, property) pair moves the time by >1%
large:   no rung has a mode
```

⚠ **The mechanism is identified but not attributed to one loop, and the count of
pairs that fail to attribute it is SEVEN rather than the four this file used to
say** (TASK_033_REVIEW minor 6; re-run at TASK_034, `.temp/p34/analyze-p11.log`).
`analyze.py` separates the population perfectly and identically on

```
unsafe   loop0 [+0x40,+0x189) 329B  jcc32[1,4]   x0.9399 / x0.9447   *PERFECT*
unsafe   loop1 [+0x50,+0x63)   19B  win32[1,2]   x0.9399 / x0.9447   *PERFECT*
unsafe   loop1 [+0x50,+0x63)   19B  jcc32[0,1]   x0.9399 / x0.9447   *PERFECT*
unsafe   loop2 [+0xd0,+0x124)  84B  win32[3,4]   x0.9399 / x0.9447   *PERFECT*
unsafe   loop2 [+0xd0,+0x124)  84B  jcc32[0,1]   x0.9399 / x0.9447   *PERFECT*
unsafe   loop3 [+0x140,+0x15a) 26B  win32[1,2]   x1.0640 / x1.0585   *PERFECT*
unsafe   loop4 [+0x15a,+0x192) 56B  jcc32[0,1]   x1.0640 / x1.0585   *PERFECT*
```

— in **two opposite orientations** (`×0.9399` and `×1.0640`, and
`1 / 1.0640 = 0.9398`: it is the same partition read from either side), because
the kernel is a single function moved as a unit, so every loop's 32-byte geometry
flips together. **The conclusion is strengthened, not weakened**: the population
identifies the **mode** and cannot identify **which loop**, and seven
indistinguishable candidates say that more sharply than four. This write-up will
not pretend otherwise.

What the population *does* say is that the mode is on `small` and not on `large`,
and that fits the kernel: `small`'s mean string length is 6.92, so the
4×-unrolled fold body rarely runs and the 26-byte **rolled remainder** loop is
the hot one — one or two 32-byte fetch windows depending on residue. On `large`
(mean 100) the 84-byte unrolled body dominates and spans 3 windows either way.

### 11c. The statistic: mode-matched, and pairwise P(A > B)

| input | pass | rung | pooled | mode 0 | mode 16 | P(A>B) |
|---|---|---|---:|---:|---:|---:|
| small | 0 | R2 | +10.48% | +11.36% | +4.22% | 100.0% |
| small | 1 | R2 | +10.54% | +11.11% | +4.70% | 100.0% |
| small | 0 | **R3** | +26.12% | **+27.43%** | **+18.81%** | 100.0% |
| small | 1 | **R3** | +25.73% | **+26.40%** | **+19.25%** | 100.0% |
| large | 0 | R2 | +6.39% | +6.00% | +6.59% | 100.0% |
| large | 1 | R2 | +6.52% | +6.19% | +6.66% | 100.0% |
| large | 0 | **R3** | −8.75% | **−9.16%** | **−8.50%** | 0.0% |
| large | 1 | **R3** | −8.61% | **−9.03%** | **−8.46%** | 0.0% |

**No sign flips, in either mode, on either input, in either pass, and P(A>B) is
0 or 100 in all eight rows.** Both `ns` comparisons survive, so unlike p01's and
p07's `small` rows nothing here is withdrawn. The shipped single-layout readings
(§3) all sit inside their populations; **R2's `small` +4.73% sits at the mode-16
end and must not be quoted alone** — the mode-matched pair is +11.1…+11.4% and
+4.2…+4.7%.

### 11d. What the `ns` column says that `Ir` does not

R3 is **−34.65% of instructions and only −8.5% of time** on `large`, and
**+21.21% of instructions and +23.35% of time** on `small`. The direction agrees
everywhere (§3), but the *conversion factor* does not: 4.1× on `large` against
1.1× on `small`. Mechanism, and it is the same one all the way through: on
`large` the instructions R3 removes are `core::slice::memchr`'s, i.e. two
independent `u64` loads and a SWAR test per 16 bytes, which the machine overlaps;
the instructions it keeps are the **serial Horner fold**, `h = h*31 + b`, which
has a hard 3-cycle dependent latency per byte and is what the clock is actually
set by. Removing instructions from the non-critical path buys time at a
discount. This is p16's latency-bound-Horner finding on a kernel where the
*other* loop is the one that changed.

## 12. `vector_regs`, the prediction I got wrong, and what is not here

### 12a. Does any rung reach SIMD? Not one, in its own code

`vector_regs` from `harness/asm.py`, `-O3 isolated`, **kernel symbol only**:

```
c-gcc []   c-clang []   c-gcc-h []   c-clang-h []
safe_naive []   safe_tuned []   unsafe []   verus []
```

**8 of 8 empty.** In `whole` mode five cells show `['xmm']`, and that is the
driver's payload `memcpy`, not the kernel — the same 23-of-32 caveat p16 records.
So every rung's *own* code is scalar, and the AVX2 in this pattern is entirely
inside glibc:

- **R1 and R1h call out.** `c-gcc-h`/`c-clang-h` show `bulk=['memchr@plt']` in
  the gate's own table, and since TASK_034 `c-gcc`/`c-clang` show
  `bulk=['strlen@plt']` there too — they showed `bulk=[]` **only because
  `harness/asm.py::is_bulk_symbol` did not know the `str*` family** (§8a), never
  because the call was absent: the relocation is there (`R_X86_64_PLT32 strlen`,
  §1) and the IFUNC resolves to the AVX2 implementation at `libc+0x18b7c0`,
  confirmed by disassembling libc (`vpcmpeqb %ymm`, `vpminub`, `vpmovmskb`) and
  by the 0.0788 Ir/byte measurement.
- **R3 calls out too, to `core::slice::memchr`, which uses no vector register at
  all** — it is SWAR on two `u64`s (`movabs $0x8080808080808080`, `sub`, `or`,
  `and`), 15 instructions per 16 bytes.
- **R2, R4 and R5 emit a byte loop**, 9.00000 and 6.00000 Ir/byte.

So the answer to TASK_033's question 2 is: **no Rust rung reaches SIMD, and one
reaches a word-at-a-time routine.** The 12× that separates `core::slice::memchr`
from glibc's `strlen` is `-march` and IFUNC dispatch, and it is available to
neither the safe nor the unsafe Rust class on this box.

### 12b. The prediction, and it was wrong by exactly one instruction

The probe-stage note (`.temp/p11/NOTES.md`, written before any rung existed) put
the separable safety term at **2.00000 Ir/byte**, p16's and p05's constant, on
the reasoning that the mechanism is the same compare-and-branch. Measured on the
shipped rungs that is **right on the fold (10.00000 − 8.00000 = 2.00000) and
wrong on the scan (9.00000 − 6.00000 = 3.00000)**. The missing instruction is the
`lea (%rdx,%rbx,1),%r14` that
materialises `off + q`: the fold's induction variable is already blob-absolute
because LLVM hoisted `add %rdx,%rax` out of the loop, and the scan's is
window-relative because the scan's own exit test is `q < len`. **A bounds check
costs two instructions when the loop already holds the address it needs to check
and three when it does not**, and which of those you get is decided by the *other*
test in the loop.

### 12c. Does R3's cost amortise? It goes through zero

p07 asked this and answered "no axis along which it amortises". p11's answer is
different again, and §4b is the measurement: R3 − R4 is a **per-string constant
of +25 Ir below a 16-byte string length** (so per byte it decays as `1/L`) and
**−4.89 Ir per byte above it**. It does not amortise to zero; it crosses zero, at
L = 17–18, and keeps going. The axis is the *mean string length*, which is a
property of the data and not of the input size — making `large` bigger at the
same mean length would not move it.

### 12d. What is NOT here

- **No cycles/byte.** `.memory/00-environment.md`: ns is a measurement on this
  box and cycles is an inference that spans ±15% within one session, and the
  clock was not measured interleaved with these reps. ns only.
- **No branch or cache simulation.** `.memory/00-environment.md` records that
  callgrind's `--branch-sim`/`--cache-sim` do run here and were missed for 28
  tasks. p11 makes no branch claim, so none was run; if a reviewer wants the
  `Ir`-to-`ns` conversion factor of §11d attributed, `--cache-sim` on
  `safe_tuned` vs `unsafe` at `large` is the experiment, and it is cheap.
- **No C layout bracket** (§3, §11c) — the lever is LLVM-side and cannot reach
  `c-gcc`.
- **`O0` rows are built and gate-checked but no number here comes from one.**

## 13. The declaration, and how to re-check it from the tree alone

`spec.md`'s `idiom` block was written **before any cell was measured** -- the R5
proof and the checksums existed; no `Ir` and no `ns` did. That is the one thing
TASK_018's standard cannot retrofit onto p01, p02, p05, p08, p16 or p17, and it
is stated inside the hashed `why` so it travels with the numbers.

### 13a. The shared paragraph is byte-identical, and the check needs no scratch file

`.temp/p11/make_spec.py --check` does this, but so does a tree-only script that
reads every `spec.md`, takes the `idiom.why` from the `NAMED-SPELLING STANDARD`
marker onward, and compares each against p07's:

```
p01-array-sum          identical=True  len=11004
p02-buffer-copy        identical=True  len=11004
p05-index-flatten      identical=True  len=11004
p07-binary-search      identical=True  len=11004
p08-overlap-move       identical=True  len=11004
p11-nul-scan           identical=True  len=11004
p16-tlv-walk           identical=True  len=28847
p17-http-range         identical=True  len=13113
```

p16 and p17 carry pattern-specific text *after* the shared paragraph, which is
why their lengths differ; the first 11 004 characters are identical in all eight.

**Where `spec.md` came from, recorded as a known asymmetry.** It is composed by
`.temp/p11/make_spec.py` from `.temp/p11/spec_prose.md` plus that paragraph, read
out of p07's own block, so 11 004 characters were never retyped. `spec.md` is
committed and self-contained and the check above needs neither file -- but p11 is
the only pattern whose `spec.md` has a build script, and that script lives under
`.temp/`.

### 13b. The stage-0b audit: 0 pin nothing, 0 forbidden hits, 12 scoped-absent

```
audit  37 backticked spelling(s) over 6 rung(s) -> 114 (spelling, rung) pair(s), 78 present
audit  forbidden: 8 spelling(s), 0 hit(s)   (decidable)
audit  required : 0 pin nothing, 12 scoped-absent pair(s)
```

`pins_nothing = 0` is the signal that matters (`.memory/01-ladder.md`: an entry
matching *no* rung of a language it declares is a bug in the **ruler**). All 12
scoped-absent pairs are correct and each is scoped by its entry's English:

| pairs | what |
|---:|---|
| 3 | `required[1]`'s `.iter().fold(` -- illustrative, present only in `safe_tuned`; the entry pins the Horner *operation* (`.wrapping_mul(31).wrapping_add(`) for all four Rust rungs and says so |
| **2** | `required[7]`'s `memchr(...)` absent from `c/kernel.c` and `strlen` absent from `c/kernel_hardened.c` -- **this pair IS the bug**, and it is the one scoped-absent pair the declaration exists to report |
| 1 | `required[7]`'s `while q < len` absent from `safe_tuned`, which bounds its scan by the type of the reslice instead |
| 6 | `required[7]`'s `CStr::from_bytes_until_nul` and `&w[p..]`, each absent from the three Rust rungs that are not R3 |

`.memory/01-ladder.md` measured 41 such misses over 158 obligations on the other
patterns, all non-defects; p11's 12 of 114 is the same rate and the same kind.
