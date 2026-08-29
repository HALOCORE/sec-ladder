# p01-array-sum — results

Generated 2026-08-19T17:06:10Z from `results/p01-array-sum.json` (git `79950f694cff`, working tree dirty).

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
| adversarial-empty.bin | 1,000 | 0 | 0 | False | n_iters=1000 v_len=0 win=0 calls=0 work/call=0 truncated=False expected=0 |
| adversarial-headonly.bin | 1,000 | 8 | 8 | False | n_iters=1000 v_len=0 win=8 calls=0 work/call=0 truncated=False expected=0 |
| adversarial-shortlen.bin | 1,000 | 4,096 | 40 | True | n_iters=1000 v_len=4 win=4 calls=0 work/call=0 truncated=True expected=None |
| adversarial-win0.bin | 1,000 | 520 | 520 | False | n_iters=1000 v_len=64 win=0 calls=0 work/call=0 truncated=False expected=0 |
| adversarial-winbig.bin | 1,000 | 520 | 520 | False | n_iters=1000 v_len=64 win=1099511627776 calls=0 work/call=0 truncated=False expected=0 |
| adversarial.bin | 0 | 520 | 520 | False | n_iters=0 v_len=64 win=8 calls=0 work/call=8 truncated=False expected=0 |
| large.bin | 20,000 | 12,000,008 | 12,000,008 | False | n_iters=20000 v_len=1500000 win=4096 calls=20000 work/call=4096 truncated=False expected=8088771909753396726 |
| small.bin | 200,000 | 16,008 | 16,008 | False | n_iters=200000 v_len=2000 win=501 calls=200000 work/call=501 truncated=False expected=17245669606222259694 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — wrapping, not checked, addition in every rung -- the kernel is total on VALUES and R5's only obligation is off + len <= v.len()
- **required** — the C kernel takes (v, off, len) and has no length to check; the Rust kernels take &[u64], i.e. a pointer AND a length
- **required** — R2 indexes v[i] element by element; R3 reslices the window once and folds it with an iterator
- **FORBIDDEN** — a dead v_len parameter on the C kernel

> **Why**: wrapping addition is what keeps the proof obligation exactly the memory-safety property, with no value bound smuggled in that the input generator would then have to be trusted to respect -- the pilot did the opposite and its own measured inputs violated it. The C/Rust arity asymmetry is the finding and not a rigging: the length is the thing C does not have and therefore cannot check, so handing C a dead v_len to make the signatures match would be Rust-in-C-syntax and would delete the comparison. Both are also written out in the prose above ('Kernel signature' and 'Semantics'); TASK_016 RESTATED them here rather than moving them, so p01 states its idiom twice and THIS block is the authoritative copy (TASK_016_REVIEW m2). Whoever edits one edits the other. Note how weak this declaration deliberately is: p01 is the CALIBRATION pattern, it models no bug, and its inner fold is an associative sum with no bulk-memory idiom to lose, so beyond the three required entries no spelling of the fold is excluded and p01's numbers are a spelling's numbers. TASK_016 did not measure a spelling spread for p01; one is owed before any p01 number is quoted as what safe Rust costs. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p01-array-sum.json`, contract `5360d6f3dd7a`.

This declaration backticks **no spelling at all**, so the named-spelling standard's own trigger never fires on this pattern and there is nothing to audit. Its rungs are matched by the entries' English alone.


## What the gate said out loud (reporting only)

From `results/gate/p01-array-sum.json` — the `loud` and `controls_json` keys, at contract `5360d6f3dd7a`. **These did not fail the gate and are not defects**; they are the conditions `check.py` refuses to be silent about. Each one is a caveat on a number below or on the declaration above. The run's **verdict** is deliberately not printed here: it is an output of the same gate run that checks this table is current (stage `9c`), and rendering it made the table an input to its own checker — see `read_gate_loud`. Read the verdict from `results/gate/p01-array-sum.json`.

- **`idiom-forbidden`** — idiom.forbidden[0] has NOT ONE backticked spelling, so the enforced audit never ranges over it and its share of the 0 hits above is vacuous: a dead v_len parameter on the C kernel. Backtick the spelling if it has one (p09 shipped 5 entries and 0 audited spellings; TASK_038_REVIEW) -- and if it has none, because the entry forbids a STRUCTURE rather than a token (p05's 'a running row pointer'), say so in `why`: this line is then permanent and correct, and it is what stops the pattern's `ok` above from reading as enforcement it does not have.
- **`twin`** — safe_naive_verus.rs: no trusted item with an `ensures` or an `unsafe` body (`_is_trusted`), so no twin is required and NOTHING in this stage checked this file. external_body items: ['emit', 'load_input']


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

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
| c-gcc | 98 | 98 | 0 | 411 | 1,205,400,000 | - | 6,800,066 | - | `4104f391` | `4104f391` | yes | - |
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
| c-gcc | isolated | 33.55 | 35.29 | 5.2% | 24.27 | 25.74 | 6.1% |
| c-gcc | whole | 34.15 | 35.73 | 4.6% | 24.59 | 25.82 | 5.0% |
| c-clang | isolated | 32.86 | 34.94 | 6.3% | 15.02 | 15.55 | 3.5% |
| c-clang | whole | 34.02 | 34.83 | 2.4% | 15.78 | 16.61 | 5.3% |
| safe_naive | isolated | 35.12 | 35.97 | 2.4% | 15.56 | 16.60 | 6.7% |
| safe_naive | whole | 35.26 | 35.95 | 2.0% | 15.94 | 16.35 | 2.5% |
| safe_tuned | isolated | 35.21 | 35.95 | 2.1% | 15.35 | 16.47 | 7.3% |
| safe_tuned | whole | 34.09 | 35.89 | 5.3% | 15.38 | 16.34 | 6.3% |
| unsafe | isolated | 34.73 | 36.11 | 4.0% | 14.72 | 15.85 | 7.7% |
| unsafe | whole | 34.40 | 36.18 | 5.2% | 15.66 | 16.68 | 6.5% |
| verus | isolated | 35.07 | 36.21 | 3.2% | 15.08 | 15.97 | 5.9% |
| verus | whole | 34.37 | 35.68 | 3.8% | 15.65 | 16.67 | 6.5% |
| safe_naive_verus | isolated | 34.37 | 35.88 | 4.4% | 14.54 | 15.73 | 8.2% |
| safe_naive_verus | whole | 34.37 | 35.77 | 4.1% | 15.70 | 16.86 | 7.3% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
