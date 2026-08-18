# p16-tlv-walk — results

Generated 2026-08-17T17:02:54Z from `results/p16-tlv-walk.json` (git `f473198bfcab`, working tree dirty).

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
| adversarial-overrun.bin | 8 | 3,080 | 3,080 | False | n_iters=8 stride=3072 n_blob=3072 nwin=1 calls=8 work/call=3072B san=fires truncated=False expected=8267139675305953920 |
| adversarial-stride2.bin | 8 | 72 | 72 | False | n_iters=8 stride=2 n_blob=64 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| adversarial-trunc.bin | 8 | 1,648 | 1,648 | False | n_iters=8 stride=41 n_blob=1640 nwin=40 calls=8 work/call=41B san=clean truncated=False expected=3988538283260473009 |
| large.bin | 20,000 | 8,384,508 | 8,384,508 | False | n_iters=20000 stride=4090 n_blob=8384500 nwin=2050 calls=20000 work/call=4090B san=clean truncated=False expected=16533539788217857060 |
| small.bin | 25,000 | 16,264 | 16,264 | False | n_iters=25000 stride=508 n_blob=16256 nwin=32 calls=25000 work/call=508B san=clean truncated=False expected=71049275114976110 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — every comparison is subtraction-first AND IS SPELLED AS THESE TOKENS -- `end - p >= 3` and `vlen > end - (p + 3)` -- in every rung (R1: fourth entry below). This entry names TOKENS, not the weaker property 'contains no additive comparison'. That is the named-spelling standard, adopted as POLICY at TASK_018 for all six patterns AFTER the alternate spellings had been measured -- it is not a disambiguation of what this entry always meant. The argument, the history of the sentence, and what the standard demonstrably does NOT buy are in `why`
- **required** — the tag byte is folded, and folded BEFORE the fit test
- **required** — nrec is folded into the result
- **required** — R1 omits only the second check -- it keeps `end - p >= 3`
- **FORBIDDEN** — the additive spellings `p + 3 <= end` and `p + 3 + vlen <= end`
- **FORBIDDEN** — tag dispatch or skipped records

> **Why**: the additive comparisons can overflow size_t on an attacker-chosen vlen and wave the attack through, which is the whole check p16 is about; an unread tag is deleted by LLVM and the walk stops looking like a TLV walk; a `if tag != 0 { skip }` branch adds an unpredictable data-dependent branch, which is a second new variable and belongs to p19/p35 (this box cannot measure branch misses). RESTATED in this hashed block at TASK_016 from the prose section 'Five things are load-bearing' above -- restated, not moved: the prose is still there, says the same thing, and THIS block is the authoritative copy of it (TASK_016_REVIEW m2). NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes. Where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies. That clause was MEASURED, not granted: without it a literal reading puts EIGHT SHIPPED CELLS out of their own contract -- p02's four Rust rungs (`len > src.len() - (src_off + 2)`, where the entry says `src_len` and the Rust signature has no `src_len` to say) and p08's four Rust rungs (`let dr: usize = d + r;`, where the entry says `dr = d + r`) -- and no cell source may change. A difference the language does NOT force is not covered by that clause: Rust can write `let end: i64 = content_len;`, and four shipped p17 rungs do. An entry that names a rung pins that rung only, and an entry may carve a rung out (p05's second entry, p16's fourth, p17's third). WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle. WHAT THE STANDARD DOES NOT BUY, measured at TASK_018 and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call and p17's by 51 Ir/call flat, so `R3ship - R4ship` is an UPPER BOUND on the in-contract safety tax and never the tax itself. Every pattern owes an in-contract spelling spread beside its headline; p16 and p17 have one from TASK_018 (their NOTES.md 10a), p01, p02, p05 and p08 do not. WHAT THE STANDARD SAYS ABOUT p16: rows 3, 4 and 6 of NOTES.md 10 (`.temp/p05r3/v16/tuned_split.rs`, `tuned_splitat.rs`, `unsafe_consume.rs`) contain NEITHER named comparison and are OUT OF CONTRACT under it. WHAT THIS BLOCK USED TO SAY, AND WHEN AND WHY IT CHANGED -- restored here because TASK_017 deleted it and TASK_016_REVIEW's honesty verdict rested on it (TASK_017_REVIEW M1). Until 89f6598 (2026-08-17) this `why` said, in these words: `Note what is deliberately NOT restricted: the R2/R3/R4 spelling of THE WALK and of the value fold, beyond the comparisons above`, and `A consuming spelling (split_first_chunk::<3>() plus split_at) IS ADMISSIBLE under this declaration and measures 10*nrec + 9 CHEAPER than the shipped R3`. Both sentences were written at TASK_016 with the measurement already in hand, i.e. against the author's own interest. TASK_017 removed `the walk` from the first, dropped the second, and kept verbatim a third -- `the honest move is to declare the walk's spelling here BEFORE measuring` -- which under the new reading advises a future task to do, before measuring, what TASK_017 had just done after measuring. So: the consuming spelling WAS admissible when TASK_015 measured it at ad661ed, and stopped being admissible four tasks later at 89f6598. Nobody may read p16's `+27/+77` as a pre-registered matched pair; the walk's spelling was pinned AFTER the measurement, and this sentence is the record of that. THE FOUR GROUNDS TASK_017 GAVE, with what survived. (i) House convention (p05's `i*ncol + j written out in every rung`, p02's `spelled identically in every rung`, p17's `the one conjunctive if start < end && start >= 0`) -- TASK_017_REVIEW found the citation cuts the other way textually, every cited entry carrying an explicit strictness marker p16's did not have, which is exactly why this is now POLICY and not a reading. (ii) `p` and `end` ARE the traversal representation -- true, but the claim TASK_017 built on it, that pinning them `is what makes R3 - R4 a difference in safety rather than a difference in representation`, is REFUTED BY MEASUREMENT AT TASK_018 and is WITHDRAWN; see the in-contract spread below. (iii) The exclusion falls symmetrically -- true in EXISTENCE (the consuming R4 control goes out too) and misleading in EFFECT (TASK_017_REVIEW M4): the published pair is `7 + 5*nrec` / `7 + 7*nrec` (+27 small, +77 large) against the excluded matched consuming pair's `7` flat / `7 + nrec` (+7, +17), so the reading makes p16's published safety tax 3.9x (small) / 4.5x (large) LARGER, and removes 49 (small) / 109 (large) Ir/call of headroom from the SAFE side against 29 / 49 from the unsafe side. Quote the numbers, not the word. (iv) `inf(R4) <= inf(R3)` by construction (.memory/01-ladder.md finding 14) -- correct, and it proves too much: it selects the pin for every pattern equally, which is why TASK_018 applies the standard to all six rather than to p16 alone. THE IN-CONTRACT SPREAD, MEASURED AT TASK_018 -- this is what TASK_017 owed and did not do; the table is NOTES.md 10a. Three admissible respellings of the two things this block leaves free (the header read and the value fold), all keeping BOTH named comparisons literally, all identical to shipped R3 on 73/73 committed inputs: `r3_endslice` is `2*nrec - 2` Ir/call CHEAPER than shipped R3, `r3_window` is `4*nrec - 8` cheaper, `r3_hdrarray` is `nrec` DEARER. At `large` (nrec 10) that is a 42 Ir/call spread INSIDE the contract against a published `R3 - R4` of 77; at `small` (nrec 4), 12 against 27. `r3_endslice` keeps `p` absolute and `end = off + len`, so it satisfies even ground (ii)'s own gloss. CONSEQUENCE, plainly: `the shipped R3 is the cheapest admissible spelling` is not unestablished, it is FALSE. p16's published `+27/+77` is an UPPER BOUND on the in-contract safety tax, whose measured in-contract minimum is `+19` (small) / `+45` (large) against the shipped R4 -- and since the R4 side has not been searched in contract, that is a bound too, not a safety number. Still deliberately NOT restricted: the R2/R3/R4 spelling of the value fold and of the header read beyond the two comparisons, and unrolling.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried. Use the `isolated` kernel-exclusive figure, which needs no correction.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 44 | 42 | 0 | 152 | 101,550,000 | 653,880,000 | 375,056 | 300,056 | `f73811a0` | `f73811a0` | yes | - |
| c-clang | 93 | 89 | 1 | 327 | 74,825,000 | 475,220,000 | 350,059 | 280,059 | `0de16a44` | `6dc150b8` | yes | - |
| safe_naive | 66 | 64 | 10 | 246 | 127,375,000 | 818,420,000 | 350,275 | 280,275 | `8defbe76` | `c8b8c70e` | yes | - |
| safe_tuned | 117 | 113 | 6 | 410 | 75,925,000 | 477,500,000 | 350,275 | 280,275 | `07b07f1a` | `d50a00f9` | yes | - |
| unsafe | 92 | 88 | 12 | 324 | 75,250,000 | 475,960,000 | 350,275 | 280,275 | `852405e0` | `09dcfbae` | yes | - |
| verus | 92 | 88 | 12 | 324 | 75,250,000 | 475,960,000 | 325,274 | 260,274 | `852405e0` | `09dcfbae` | yes | - |
| c-gcc-h | 48 | 46 | 0 | 157 | 101,975,000 | 654,700,000 | 375,056 | 300,056 | `f1625f1d` | `f1625f1d` | yes | - |
| c-clang-h | 102 | 98 | 1 | 346 | 75,425,000 | 476,300,000 | 350,059 | 280,059 | `391ed37c` | `d940a72d` | yes | - |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 83 | 83 | 0 | 307 | 240,525,000 | - | 900,066 | - | `7a6db6f0` | `7a6db6f0` | yes | - |
| c-clang | 60 | 60 | 2 | 243 | 189,625,000 | - | 525,056 | - | `e3670d6a` | `c36ab8a2` | yes | - |
| safe_naive | 116 | 116 | 9 | 551 | 292,400,000 | - | 625,077 | - | `a71b5aef` | `115a9f22` | yes | - |
| safe_tuned | 145 | 145 | 1 | 671 | 298,900,000 | - | 625,077 | - | `f70c1048` | `7beae62f` | yes | - |
| unsafe | 85 | 85 | 2 | 398 | 266,300,000 | - | 625,077 | - | `3dfd3fac` | `1fdb97d5` | yes | - |
| verus | 85 | 85 | 2 | 398 | 266,300,000 | - | 625,056 | - | `7c1d83eb` | `8dbf8638` | yes | - |
| c-gcc-h | 90 | 89 | 0 | 328 | 241,050,000 | - | 900,066 | - | `134a3d13` | `134a3d13` | yes | - |
| c-clang-h | 68 | 68 | 1 | 269 | 190,325,000 | - | 525,056 | - | `2146affc` | `6cf27812` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 258 | 255 | 1 | 1,023 | - | - | 101,600,127 | 653,920,127 | `c403d795` | `aa403b52` | yes | - |
| c-clang | 307 | 302 | 0 | 1,185 | - | - | 74,800,182 | 475,200,182 | `6230aa0b` | `6230aa0b` | yes | xmm |
| safe_naive | 714 | 706 | 1 | 3,151 | - | - | 140,750,284 | 901,360,284 | `2b632b49` | `abfa8435` | yes | xmm |
| safe_tuned | 727 | 717 | 1 | 3,167 | - | - | 75,800,278 | 477,720,278 | `4ea62636` | `9d57ffac` | yes | xmm |
| unsafe | 708 | 698 | 1 | 3,103 | - | - | 75,225,281 | 475,940,281 | `cda0d193` | `effd2174` | yes | xmm |
| verus | 713 | 703 | 1 | 3,071 | - | - | 75,225,275 | 475,940,275 | `450c41e0` | `e2f742f7` | yes | xmm |
| c-gcc-h | 262 | 259 | 1 | 1,031 | - | - | 102,000,127 | 654,720,127 | `1d3a3e0f` | `41524305` | yes | - |
| c-clang-h | 311 | 307 | 0 | 1,201 | - | - | 75,300,181 | 476,200,181 | `d22e75fc` | `d22e75fc` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 240,525,000 | - | 900,066 | - | `c0db7b01` | `c0db7b01` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 189,625,000 | - | 525,055 | - | `1dc19436` | `1dc19436` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 292,400,000 | - | 625,077 | - | `f1f66836` | `e7ee6b0e` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 298,900,000 | - | 625,077 | - | `b63dabe9` | `6cc8336d` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 266,300,000 | - | 625,077 | - | `c836735c` | `21eef29b` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 266,300,000 | - | 625,056 | - | `38f684e2` | `4d43518b` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 241,050,000 | - | 900,066 | - | `39757241` | `39757241` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 190,350,000 | - | 525,055 | - | `2eec1d2d` | `2eec1d2d` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 85/85 vs 85/85 | 2 B vs 2 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 92/88 vs 92/88 | 12 B vs 12 B |

## Wall clock (secondary)

> taskset -c 5, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 74.07 | 75.03 | 1.3% | 12.73 | 12.87 | 1.2% |
| c-gcc | whole | 73.94 | 74.87 | 1.3% | 12.75 | 12.87 | 1.0% |
| c-clang | isolated | 73.88 | 74.74 | 1.2% | 12.73 | 12.91 | 1.4% |
| c-clang | whole | 73.80 | 74.80 | 1.4% | 12.70 | 12.91 | 1.7% |
| safe_naive | isolated | 73.90 | 75.04 | 1.5% | 12.79 | 12.99 | 1.6% |
| safe_naive | whole | 74.10 | 75.10 | 1.4% | 12.84 | 13.02 | 1.4% |
| safe_tuned | isolated | 74.23 | 75.00 | 1.0% | 12.84 | 12.97 | 1.0% |
| safe_tuned | whole | 74.02 | 74.86 | 1.1% | 12.80 | 13.09 | 2.3% |
| unsafe | isolated | 74.07 | 74.90 | 1.1% | 12.85 | 13.04 | 1.5% |
| unsafe | whole | 73.94 | 74.94 | 1.3% | 12.83 | 13.02 | 1.5% |
| verus | isolated | 74.15 | 74.95 | 1.1% | 12.82 | 13.01 | 1.5% |
| verus | whole | 73.88 | 74.87 | 1.3% | 12.78 | 13.03 | 1.9% |
| c-gcc-h | isolated | 73.56 | 74.67 | 1.5% | 12.69 | 12.89 | 1.6% |
| c-gcc-h | whole | 73.70 | 74.77 | 1.5% | 12.70 | 12.92 | 1.7% |
| c-clang-h | isolated | 73.70 | 74.79 | 1.5% | 12.72 | 12.89 | 1.3% |
| c-clang-h | whole | 73.57 | 74.90 | 1.8% | 12.76 | 12.91 | 1.2% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
