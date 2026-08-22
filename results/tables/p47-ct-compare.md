# p47-ct-compare — results

Generated 2026-08-22T07:02:10Z from `results/p47-ct-compare.json` (git `59bd159ecefc`, working tree dirty).

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
| adversarial-equal.bin | 3,000 | 2,064 | 2,064 | False | n_iters=3000 stride=2056 n_blob=2056 nwin=1 calls=3000 work/call=1024cmp k(win0)=[None, None, None, None, None, None, None, None] san=clean truncated=False expected=15278858700986457088 |
| adversarial-k000.bin | 3,000 | 2,064 | 2,064 | False | n_iters=3000 stride=2056 n_blob=2056 nwin=1 calls=3000 work/call=1024cmp k(win0)=[0, 0, 0, 0, 0, 0, 0, 0] san=clean truncated=False expected=15618968502624590848 |
| adversarial-klast.bin | 3,000 | 2,064 | 2,064 | False | n_iters=3000 stride=2056 n_blob=2056 nwin=1 calls=3000 work/call=1024cmp k(win0)=[127, 127, 127, 127, 127, 127, 127, 127] san=clean truncated=False expected=15618968502624590848 |
| adversarial-stride7.bin | 2,000 | 48 | 48 | False | n_iters=2000 stride=7 n_blob=40 nwin=0 calls=0 work/call=0cmp k(win0)=[] san=clean truncated=False expected=0 |
| degenerate.bin | 4,000 | 272 | 272 | False | n_iters=4000 stride=88 n_blob=264 nwin=3 calls=4000 work/call=3cmp k(win0)=[None, 0, 0] san=clean truncated=False expected=13001800165042993012 |
| large.bin | 1,500 | 8,454,152 | 8,454,152 | False | n_iters=1500 stride=1032 n_blob=8454144 nwin=8192 calls=1500 work/call=512cmp k(win0)=[None, None, 37, 37, 37, 37, 37, 37] san=clean truncated=False expected=6032580231827418624 |
| small.bin | 20,000 | 19,208 | 19,208 | False | n_iters=20000 stride=200 n_blob=19200 nwin=96 calls=20000 work/call=96cmp k(win0)=[5, 5, 5, 5] san=clean truncated=False expected=6525366822079760384 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE TIMING LINE, and the whole of what c/kernel.c does differently: `memcmp(buf + off + p, buf + off + p + tlen, tlen) == 0`. c/kernel_hardened.c writes the or-accumulate instead and is otherwise character-identical, so the scoped-absent audit pair this entry reports is on that rung and is correct.
  - `rust` — THE TIMING LINE at R2, the idiomatic safe-Rust comparison and the LEAKING one: `if a == b {` in safe_naive.rs. It lowers to a `bcmp` call -- one R_X86_64_GLOB_DAT bcmp relocation reached from the kernel symbol on the shipped binary -- which is the same glibc routine c-clang enters. safe_tuned.rs, unsafe.rs and verus.rs write the or-accumulate instead.
- **required** — *per language:*
  - `c` — THE CONSTANT-TIME LINE, present in c/kernel_hardened.c and ABSENT from c/kernel.c: `d |= (uint8_t)(buf[off + p + i] ^ buf[off + p + tlen + i]);`. Every byte of the tag is read on every call whatever the data says.
  - `rust` — THE CONSTANT-TIME LINE. In safe_tuned.rs it is the fold, spelled with the `u8` accumulator the why key argues for: `fold(0u8, |acc, (x, y)| acc | (x ^ y))`. In unsafe.rs and verus.rs the language forces the other spelling -- there is no iterator over `get_unchecked` -- so those two write the same accumulation as an indexed loop and the entry scopes to R3. safe_naive.rs does NOT have it, and that is the pattern.
- **required** — *per language:*
  - `c` — the WINDOW GUARD, present in BOTH C rungs including the buggy one, so p47 models no spatial bug: `while (o < ntag && len - p >= 2 * tlen) {`. Subtraction-first, because p <= len is maintained by the guard itself so the subtraction cannot wrap, while the additive form can overflow and Verus rejects it.
  - `rust` — the window guard, subtraction-first, in all four Rust rungs: `while o < ntag && len - p >= 2 * tlen {`.
- **required** — *per language:*
  - `c` — the VERDICT FOLD, and it may not see a tag byte -- see the why key: `acc = acc * 31 + MATCH;` and `acc = acc * 31 + MISS;` in both C rungs.
  - `rust` — the verdict fold in all four Rust rungs, spelled with the literal multiplier: `.wrapping_mul(31).wrapping_add(MATCH)` and `.wrapping_mul(31).wrapping_add(MISS)`.
- **required** — *per language:*
  - `c` — the CURSOR ADVANCE is by a whole record, so a rung that compared overlapping or misaligned tags cannot produce the same verdicts: `p += 2 * tlen;` in both C rungs.
  - `rust` — the cursor advance in all four Rust rungs: `p = p + 2 * tlen;`.
- **required** — *per language:*
  - `c` — the header is decoded with + and * and never with | and <<, so the whole specification stays inside linear arithmetic (.memory/04-verus.md): `256 * (size_t)buf[off + 1]` in both C rungs.
  - `rust` — the header decode, in all four Rust rungs: `256 *`.
- **required** — the number of comparisons actually performed is folded LAST, so a rung that stopped at a different point cannot produce the same checksum: `o` appears in the return expression of all eight rungs.
- **required** — the two header fields are rejected together and before any read of a tag, so no rung can divide by or index with zero: `ntag == 0` appears in all eight rungs.
- **FORBIDDEN** — `volatile`
- **FORBIDDEN** — `black_box`
- **FORBIDDEN** — `fold(0u64`
- **FORBIDDEN** — *per language:*
  - `rust` — `memcmp`
- **FORBIDDEN** — *per language:*
  - `rust` — `bcmp`
- **FORBIDDEN** — *per language:*
  - `rust` — `libc`
- **FORBIDDEN** — `starts_with`
- **FORBIDDEN** — `iter().eq(`
- **FORBIDDEN** — `subtle`
- **FORBIDDEN** — `chunks_exact`
- **FORBIDDEN** — `from_le_bytes`
- **FORBIDDEN** — `copy_from_slice`
- **FORBIDDEN** — `position(`

> **Why**: POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all eight rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ON p47 THE PINNED SPELLING IS THE SECURITY PROPERTY ITSELF, WHICH IS NEW. Every other pattern here pins spellings so that a COST comparison is between comparable programs; p47 pins them because the difference between `memcmp(a, b, tlen) == 0` and an or-accumulate over every byte IS the pattern, and it is invisible to every other check in the gate -- both expressions compute the same predicate, return the same value on every input, are memory-safe, are ASan/UBSan/Miri clean, and satisfy the same `ensures`. THE PIN IS THEREFORE THE ONLY THING IN THIS TREE THAT RECORDS WHICH RUNGS LEAK. WHY THE ACCUMULATOR IS NOT `volatile`, AND WHY `volatile` IS FORBIDDEN RATHER THAN MERELY UNUSED: the received advice for this idiom is to force the accumulator into memory. Measured on this toolchain it is unnecessary -- the plain accumulate is already constant in the first-mismatch position, to the instruction, at every optimisation level tested -- and it costs 6.35x, because it defeats vectorisation entirely in both gcc and clang. A cell that reached for it would be 6.35x dearer for no security gain and would make the R1-vs-R1h column mean something else; controls/gen_controls.py ships it as `h_vol` so the figure is checkable. WHY `fold(0u8` IS PINNED AND NOT MERELY `fold`: the identical algorithm with a `u64` accumulator lowers to a `movzwl/punpcklbw/punpcklwd/punpckldq` widening loop moving 4 bytes per iteration instead of 32, because LLVM vectorises the zero-extension rather than the xor. It is still constant-time; it is five times the work, and a rung that reached for it would put a codegen accident into the safety column. WHAT IS DELIBERATELY NOT PINNED is how the two tags are ADDRESSED -- R2 and R3 reslice with `&buf[a..b]` and R4/R5 index `buf` directly with `get_unchecked` -- because that is the SAFETY axis and it is the axis the R3-side span is measured along (../NOTES.md 8). R2 and R3 are pinned to the SAME addressing on purpose: they carry the identical panic-path structure on the shipped binaries (two `slice_index_fail` and eight `panic_bounds_check` call sites each), so `R2 - R3` differences the comparison idiom with the safety term cancelled exactly, and it is the only pair in this pattern that isolates the leak from everything else. WHY THE FOLD MAY NOT MIX IN A TAG BYTE: `acc = acc*31 + (MATCH|MISS)` folds the VERDICT and the number of comparisons performed and nothing else, so two windows with the same verdict sequence and different first-mismatch positions produce the SAME CHECKSUM in every rung. That is what makes `adversarial-k000.bin` and `adversarial-klast.bin` a timing row rather than a correctness row; a fold that could see a tag byte would turn p47 into a different pattern. WHY `memcmp` IS REQUIRED IN c/kernel.c AND FORBIDDEN EVERYWHERE ELSE: it is the bug. clang -O3 rewrites `memcmp(a,b,n) == 0` into a call to `bcmp`, which is the identical symbol rustc emits for `a == b` on slices, so the c-clang cell and the safe_naive cell enter one glibc routine and any difference between them is a LIBRARY difference (`.memory/03-measurement.md`, name the routine). NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p47-ct-compare.json`, contract `1f0b4ba6a961`.

`44` backticked spelling(s) over `6` rung(s) → **138** (spelling, rung) pair(s), **52** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 23 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 1 spelling(s) pin nothing**, 10 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - pins nothing — `bcmp` (required[0], rust, 0 of 4 rungs)
  - absent — `memcmp(buf + off + p, buf + off + p + tlen, tlen) == 0` (required[0], c, **c/kernel_hardened.c**)
  - absent — `if a == b {` (required[0], rust, **safe_tuned.rs**)
  - absent — `if a == b {` (required[0], rust, **unsafe.rs**)
  - absent — `if a == b {` (required[0], rust, **verus.rs**)
  - absent — `d |= (uint8_t)(buf[off + p + i] ^ buf[off + p + tlen + i]);` (required[1], c, **c/kernel.c**)
  - absent — `fold(0u8, |acc, (x, y)| acc | (x ^ y))` (required[1], rust, **safe_naive.rs**)
  - absent — `fold(0u8, |acc, (x, y)| acc | (x ^ y))` (required[1], rust, **unsafe.rs**)
  - absent — `fold(0u8, |acc, (x, y)| acc | (x ^ y))` (required[1], rust, **verus.rs**)
  - absent — `get_unchecked` (required[1], rust, **safe_naive.rs**)
  - absent — `get_unchecked` (required[1], rust, **safe_tuned.rs**)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 89 | 86 | 0 | 300 | 2,840,000 | 345,000 | 300,056 | 22,556 | `7a0f34c6` | `7a0f34c6` | yes | - |
| c-clang | 68 | 67 | 1 | 230 | 2,540,004 | 310,504 | 280,059 | 21,059 | `9ccefa3a` | `b7f3d31b` | yes | - |
| safe_naive | 194 | 193 | 9 | 823 | 5,080,000 | 597,000 | 280,275 | 21,275 | `d00867dc` | `bf652678` | yes | - |
| safe_tuned | 270 | 265 | 12 | 1,124 | 10,200,000 | 1,101,000 | 280,275 | 21,275 | `59f8cc5d` | `a7cb3d89` | yes | xmm |
| unsafe | 162 | 156 | 12 | 644 | 8,400,000 | 888,000 | 280,275 | 21,275 | `a3898fc7` | `4d99e76e` | yes | xmm |
| verus | 162 | 156 | 12 | 644 | 8,400,000 | 888,000 | 260,274 | 19,774 | `a3898fc7` | `4d99e76e` | yes | xmm |
| c-gcc-h | 215 | 212 | 0 | 772 | 8,140,000 | 946,500 | 300,056 | 22,556 | `e0eed3ed` | `e0eed3ed` | yes | xmm |
| c-clang-h | 175 | 170 | 1 | 662 | 8,560,000 | 912,000 | 280,059 | 21,059 | `75cf2dc9` | `7243402a` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 139 | 139 | 0 | 509 | 4,900,000 | - | 720,066 | - | `3c47e4a1` | `3c47e4a1` | yes | - |
| c-clang | 107 | 107 | 1 | 423 | 4,440,004 | - | 420,056 | - | `c91f36f2` | `3c53bc0a` | yes | - |
| safe_naive | 268 | 268 | 10 | 1,494 | 9,320,000 | - | 500,077 | - | `800131e3` | `88e72767` | yes | - |
| safe_tuned | 282 | 282 | 7 | 1,593 | 112,440,000 | - | 500,077 | - | `000cc0a3` | `b167a4eb` | yes | - |
| unsafe | 182 | 182 | 14 | 914 | 70,200,000 | - | 500,077 | - | `dbff7d2e` | `a74063c5` | yes | - |
| verus | 182 | 182 | 14 | 914 | 70,200,000 | - | 500,056 | - | `1875fbcc` | `674ebd44` | yes | - |
| c-gcc-h | 149 | 149 | 0 | 544 | 50,160,000 | - | 720,066 | - | `3e2e9a5e` | `3e2e9a5e` | yes | - |
| c-clang-h | 122 | 122 | 1 | 479 | 48,240,000 | - | 420,056 | - | `7e3841c8` | `46751d74` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 328 | 325 | 2 | 1,331 | - | - | 3,000,146 | 363,146 | `42171680` | `cedf0c01` | yes | - |
| c-clang | 285 | 283 | 0 | 1,132 | - | - | 2,520,189 | 315,189 | `20efb51c` | `20efb51c` | yes | xmm |
| safe_naive | 801 | 794 | 1 | 3,631 | - | - | 4,680,283 | 561,283 | `a0faa3cc` | `c0ea3847` | yes | xmm |
| safe_tuned | 866 | 857 | 1 | 3,887 | - | - | 9,580,279 | 1,072,779 | `9d40875f` | `76763466` | yes | xmm |
| unsafe | 785 | 773 | 1 | 3,487 | - | - | 8,040,282 | 903,282 | `70678ee3` | `218086ca` | yes | xmm |
| verus | 786 | 774 | 1 | 3,487 | - | - | 8,120,273 | 915,273 | `5d140fdf` | `2659b451` | yes | xmm |
| c-gcc-h | 434 | 429 | 2 | 1,701 | - | - | 8,040,132 | 933,132 | `ead096e3` | `9945a427` | yes | xmm |
| c-clang-h | 385 | 378 | 0 | 1,564 | - | - | 8,020,182 | 889,682 | `e266127a` | `e266127a` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 4,900,000 | - | 720,066 | - | `684b9896` | `684b9896` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 4,160,004 | - | 420,055 | - | `2c05388f` | `2c05388f` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 9,320,000 | - | 500,077 | - | `0255a386` | `78c2c184` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 112,440,000 | - | 500,077 | - | `e7d6f147` | `2cc26251` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 70,200,000 | - | 500,077 | - | `202494d1` | `4a535072` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 70,200,000 | - | 500,056 | - | `38f684e2` | `4d43518b` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 50,160,000 | - | 720,066 | - | `4463cdc6` | `4463cdc6` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 47,960,000 | - | 420,055 | - | `10db32c2` | `10db32c2` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 182/182 vs 182/182 | 14 B vs 14 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 162/156 vs 162/156 | 12 B vs 12 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 6.57 | 6.81 | 3.7% | 4.72 | 5.19 | 9.9% |
| c-gcc | whole | 6.56 | 6.81 | 3.8% | 4.73 | 5.18 | 9.3% |
| c-clang | isolated | 6.54 | 6.79 | 3.9% | 4.89 | 5.26 | 7.6% |
| c-clang | whole | 6.62 | 6.80 | 2.8% | 5.08 | 5.26 | 3.5% |
| safe_naive | isolated | 6.71 | 6.96 | 3.7% | 6.18 | 6.63 | 7.2% |
| safe_naive | whole | 6.78 | 6.96 | 2.6% | 6.09 | 6.52 | 7.0% |
| safe_tuned | isolated | 6.79 | 6.99 | 2.9% | 6.70 | 7.30 | 9.0% |
| safe_tuned | whole | 6.74 | 6.96 | 3.3% | 5.83 | 6.67 | **14.5% ✗** |
| unsafe | isolated | 6.71 | 6.96 | 3.7% | 5.95 | 6.37 | 7.0% |
| unsafe | whole | 6.71 | 6.99 | 4.1% | 5.98 | 6.28 | 5.1% |
| verus | isolated | 6.71 | 6.96 | 3.7% | 5.75 | 6.30 | 9.7% |
| verus | whole | 6.78 | 7.05 | 3.9% | 5.47 | 6.33 | **15.8% ✗** |
| c-gcc-h | isolated | 6.57 | 6.83 | 3.9% | 5.26 | 6.00 | **14.2% ✗** |
| c-gcc-h | whole | 6.57 | 6.83 | 4.0% | 5.63 | 6.26 | **11.1% ✗** |
| c-clang-h | isolated | 6.57 | 6.80 | 3.5% | 5.47 | 6.01 | 9.8% |
| c-clang-h | whole | 6.57 | 6.82 | 3.7% | 5.33 | 5.73 | 7.5% |

**4 of 32 wall-clock cells exceed the 10% min-to-median spread threshold and are DISCARDED** per `.memory/03-measurement.md` step 4. They are printed above marked ✗ rather than deleted, because a missing cell that looks like an omission is worse than a documented failure (`.memory/02-bench-rules.md`). **No claim in this report rests on a marked row.**

- `safe_tuned / whole` on `small.bin`: spread 14.5%
- `verus / whole` on `small.bin`: spread 15.8%
- `c-gcc-h / isolated` on `small.bin`: spread 14.2%
- `c-gcc-h / whole` on `small.bin`: spread 11.1%


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 6 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `degenerate.bin`
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `degenerate.bin`
- `O0 / whole` on `large.bin`
- `O3 / isolated` on `degenerate.bin`
- `O3 / whole` on `degenerate.bin`
