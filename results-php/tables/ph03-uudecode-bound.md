# ph03-uudecode-bound — results

Generated 2026-09-08T03:32:51Z from `results/ph03-uudecode-bound.json` (git `7e8602dd6d12`, working tree dirty).

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
| adversarial-floor.bin | 8 | 53 | 53 | False | n_iters=8 stride=45 n_blob=45 nwin=1 calls=8 work/call=45B san=fires truncated=False expected=10286939257659585152 |
| adversarial-nowin.bin | 8 | 130 | 130 | False | n_iters=8 stride=123 n_blob=122 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| adversarial-read.bin | 8 | 79 | 79 | False | n_iters=8 stride=71 n_blob=71 nwin=1 calls=8 work/call=71B san=fires truncated=False expected=9832046297558006400 |
| adversarial-shortsrc.bin | 8 | 28 | 28 | False | n_iters=8 stride=20 n_blob=20 nwin=1 calls=8 work/call=20B san=fires truncated=False expected=10969280517312833152 |
| adversarial-write.bin | 8 | 139 | 139 | False | n_iters=8 stride=71 n_blob=131 nwin=1 calls=8 work/call=71B san=fires truncated=False expected=9832046297558006400 |
| large.bin | 20,000 | 8,384,508 | 8,384,508 | False | n_iters=20000 stride=4090 n_blob=8384500 nwin=2050 calls=20000 work/call=4090B san=clean truncated=False expected=5544170072369974633 |
| small.bin | 25,000 | 17,800 | 17,800 | False | n_iters=25000 stride=556 n_blob=17792 nwin=32 calls=25000 work/call=556B san=clean truncated=False expected=5115966432339535952 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — the inner loop's bound comes from the DATA and the true end does not: `ee = s + (len == 45 ? 60 : (int) floor(len * 1.33))` at uuencode.c:141, with `e = src + src_len` computed at :133 and read only by the outer loop at :135
- **required** — *per language:*
  - `c` — `(int) floor(len * 1.33)`
  - `rust` — `(ln * 133) / 100`
- **required** — *per language:*
  - `c` — uuencode.c:158's tail block is lifted WITH its precedence bug -- `if ((len = total_len > (p - *dest)))`, so the assignment receives 0 or 1 and :160/:162 are dead -- in both C rungs
- **required** — R1h is the real upstream fix f95c1df58349 and NOTHING ELSE; R2-R5 carry 1e2818b14376 as well, because the 2004 fix alone does not make a rung memory-safe. NO BACKTICKED SPELLING, deliberately: this is a statement about WHICH ALGORITHM each rung implements, and no single token decides it. The mechanical check is controls/negatives.py --emit no2014, which must NOT verify.
- **required** — every rung allocates its destination once per call, at the size uuencode.c:131 asks for, and folds the first total_len bytes of it -- so the allocation size is pinned across every rung by the checksum, and sizing is half of this defect. NO BACKTICKED SPELLING: C writes the emalloc call and an int-indexed loop while the Rust rungs write an index loop, a slice iterator and an unchecked loop -- three legitimate spellings of one operation, which is what R2 / R3 / R4 ARE.
- **FORBIDDEN** — `len = total_len - (p - *dest)` -- the repair of uuencode.c:158's precedence bug. It would be an improvement in any other row; here it builds a different program, and the block is DEAD anyway (0 of 12 600 documents enter it).
- **FORBIDDEN** — `s + 4 > e` -- the additive spelling of the 2014 check 1e2818b14376. Every rung writes the subtraction-first form instead, because the additive one can overflow the index type on a window near the address-space limit and R5 cannot discharge it.
- **FORBIDDEN** — `(3 * src_len + 3) / 4` -- the obvious spelling of ceil(3n/4) at uuencode.c:131. The subtractive form is the same value on every integer and cannot overflow; safe_naive.rs's capacity() carries the argument.

> **Why**: ph03 is `php_uudecode` out of PHP 5.0.0, `ext/standard/uuencode.c:126-171`, corpus row CRASH-115, tier `verbatim`. The idiom is a LOOP BOUND COMPUTED FROM THE DATA: `:133` computes the true end `e = src + src_len` and only the OUTER loop ever reads it, while the INNER loop's bound is `ee = s + (len == 45 ? 60 : (int) floor(len * 1.33))` at `:141`, derived from a length byte the attacker wrote one line earlier. Both an over-read and an over-write follow from the one wrong bound, and WHICH ONE A DETECTOR SEES IS DECIDED BY THE SOURCE BUFFER RATHER THAN BY THE DEFECT: `adversarial-read.bin` and `adversarial-write.bin` differ in 60 bytes of slack after the window and nothing else, and ASan reports a READ at uuencode.c:144 on the first and a WRITE at :146 on the second. That is why the corpus can carry `cwe = CWE-125` and a `root_cause_id` saying `writes past emalloc` and be right twice. THE FLOATING POINT IS PART OF THE MECHANISM AND STAYS IN R1/R1h: an extraction that tidies `(int) floor(len * 1.33)` to integer arithmetic changes which `len` values trigger. The Rust rungs use `(ln * 133) / 100` because Verus has no f64 at all; the two agree on the whole reachable domain (`dec` masks with `077`, so `ln` is 0..63) and `model.py::selfcheck` re-derives that from the float on every gate run. `uuencode.c:158`'s `if ((len = total_len > (p - *dest)))` keeps its precedence bug and is DEAD -- measured over 12 600 documents, not argued -- and is pinned dead. R1h IS THE REAL UPSTREAM FIX, f95c1df58349 (2004), all three hunks, and IT IS INCOMPLETE: `ee > e` bounds where the inner loop tests while the body reads `*(s+3)`, so 144 of those 12 600 documents still read past the source. R2-R5 therefore carry PHP's own 2014 fix 1e2818b14376 as well, and deleting those four lines from verus.rs makes `get_unchecked(buf, s + 1)`'s `i < v@.len()` fail -- the proof refuses the shipped fix for the reason the second commit exists. AND THE OTHER HALF OF THAT FIX IS DEAD: of hunk 1's 1953 firings over the same 12600 documents, hunk 2 would have refused all 1953, and deleting hunk 1 from verus.rs still gives 25 verified / 0 errors (controls/negatives.py --emit no2004a, a control whose declared expectation is that it STILL VERIFIES). So of a two-hunk fix one hunk is dead and the other is incomplete. ⚠ READ THE `sanitizer_hardened` BLOCK OF THIS RECORD WITH THAT IN MIND: it reads `expect: clean, fired: false` on every adversarial input, and that is NOT evidence the fix is complete -- check.py stage 7h HARD-FAILS on any R1h diagnostic, so an input demonstrating the residual is structurally unshippable under inputs/ and lives in controls/fix_incomplete.c instead (NOTES.md 5d). A machine consumer reading those four clean rows alone would draw the wrong conclusion; this sentence is in the hashed block because the gate record does not echo `provenance` at all. ⚠⚠ AND THE BENIGN CORPUS TAKES BOTH ARMS OF `:141` SINCE TASK_PHP_015: it used to declare 45 on every line, so it never once reached the floor() arm this row is named for, and `45 % 3 == 0` hid a real defect in model.py's second implementation for a whole task (TASK_PHP_014 M1). inputs/gen.py::_check_span now REFUSES to write a corpus that misses the floor() arm, the strict case declared < emitted, or the equality case declared == emitted. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither.

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/ph03-uudecode-bound.json`, contract `2fcd6802b904`.

`11` backticked spelling(s) over `6` rung(s) → **30** (spelling, rung) pair(s), **12** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 6 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 0 spelling(s) pin nothing**, 0 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## What the gate said out loud (reporting only)

From `results/gate/ph03-uudecode-bound.json` — the `loud` and `controls_json` keys, at contract `2fcd6802b904`. **These did not fail the gate and are not defects**; they are the conditions `check.py` refuses to be silent about. Each one is a caveat on a number below or on the declaration above. The run's **verdict** is deliberately not printed here: it is an output of the same gate run that checks this table is current (stage `9c`), and rendering it made the table an input to its own checker — see `read_gate_loud`. Read the verdict from `results/gate/ph03-uudecode-bound.json`.

- **`doc-citation-other`** — 4 line citation(s) into harness modules other than `check.py`. NOT failed: these sit in measurement-hashed files, so re-citing them by function costs a re-measure (RECAP queue item 38). Cite the FUNCTION when one of these files is next re-measured anyway: patterns/ph03-uudecode-bound/NOTES.md:1127 -> build.py:161-165 . patterns/ph03-uudecode-bound/c/emalloc_shim.h:117 -> build.py:163-165 . patterns/ph03-uudecode-bound/c/emalloc_shim.h:133 -> build.py:167 . patterns/ph03-uudecode-bound/c/emalloc_shim.h:492 -> build.py:168-171
- **`tcb-unsafe`** — verus.rs:440 `vset_unchecked`'s `requires` constrains nothing about ['x'], which its trusted body uses. spec.md justifies it: `x: u8` is a PURE VALUE and needs no precondition. The unchecked operation is `*v.get_unchecked_mut(i) = x`: its definedness depends on `i` being in bounds and on `v` being a live `Vec<u8>`, and on NOTHING about the byte being written -- every one of the 256 values of `x` is a legal `u8` store into a byte that is already initialised (`vec![0u8; cap]` initialised the whole buffer before the first call site is reached). Contrast the shape this stage exists to catch, `requires n >= 0` on a `usize`: there the unconstrained parameter was the one the body indexed with. Here the indexing parameter `i` IS constrained, by `i < old(v)@.len()`, and the `ensures` names `x` in the post-state -- `final(v)@ == old(v)@.update(i as int, x)` -- so a body that stored anything other than `x`, or stored it anywhere other than `i`, could not satisfy its own postcondition. That postcondition is what makes the value parameter safe to leave free, and it is why the `ensures` is the WHOLE post-state rather than `v@[i] == x`.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 284 | 280 | 0 | 1,161 | 184,243,120 | 1,058,278,800 | 350,053 | 280,053 | `a970030d` | `a970030d` | yes | xmm |
| c-clang | 407 | 392 | 1 | 1,784 | 156,117,231 | 901,018,804 | 350,053 | 280,053 | `1d3044b1` | `5c829e6f` | yes | xmm |
| safe_naive | 276 | 273 | 14 | 1,010 | 234,092,227 | 1,372,658,800 | 350,273 | 280,273 | `59bd6d88` | `bbf0473d` | yes | - |
| safe_tuned | 248 | 245 | 3 | 909 | 191,208,596 | 1,119,478,800 | 350,273 | 280,273 | `9a762cc4` | `df56bde6` | yes | - |
| unsafe | 200 | 198 | 12 | 708 | 170,434,489 | 997,958,800 | 350,273 | 280,273 | `33850579` | `a8d33cc9` | yes | - |
| verus | 200 | 198 | 12 | 708 | 170,434,489 | 997,958,800 | 350,268 | 280,268 | `33850579` | `a8d33cc9` | yes | - |
| c-gcc-h | 334 | 330 | 0 | 1,396 | 183,468,120 | 1,054,238,800 | 350,053 | 280,053 | `4224991b` | `4224991b` | yes | xmm |
| c-clang-h | 460 | 444 | 1 | 2,059 | 156,817,231 | 904,998,804 | 350,053 | 280,053 | `0ee8674a` | `3c9f2eda` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 61 | 61 | 0 | 228 | 171,560,380 | - | 900,066 | - | `a0769285` | `a0769285` | yes | - |
| c-clang | 45 | 45 | 1 | 170 | 131,188,820 | - | 500,052 | - | `05957de7` | `67892e36` | yes | - |
| safe_naive | 365 | 365 | 5 | 2,027 | 758,980,220 | - | 625,077 | - | `e86df4c8` | `75d07812` | yes | - |
| safe_tuned | 404 | 404 | 7 | 2,105 | 803,655,220 | - | 625,077 | - | `20813db3` | `5bda9285` | yes | - |
| unsafe | 335 | 335 | 14 | 1,906 | 845,925,060 | - | 625,077 | - | `6be31d16` | `a3f839c2` | yes | - |
| verus | 352 | 352 | 6 | 2,042 | 926,870,760 | - | 625,056 | - | `c95ac993` | `0b6ebe31` | yes | - |
| c-gcc-h | 74 | 74 | 0 | 271 | 171,610,380 | - | 900,066 | - | `3aa8772c` | `3aa8772c` | yes | - |
| c-clang-h | 61 | 61 | 1 | 228 | 131,288,820 | - | 500,052 | - | `d93731fb` | `470aaae8` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 527 | 522 | 2 | 2,242 | - | - | 184,818,261 | 1,062,158,941 | `bc461272` | `b0d1870a` | yes | xmm |
| c-clang | 686 | 663 | 0 | 2,877 | - | - | 152,242,448 | 878,659,021 | `438b18bd` | `438b18bd` | yes | xmm |
| safe_naive | 893 | 882 | 1 | 3,935 | - | - | 243,517,518 | 1,430,359,091 | `826d68bc` | `5bb11412` | yes | xmm |
| safe_tuned | 860 | 851 | 1 | 3,743 | - | - | 200,108,885 | 1,174,479,089 | `2051e746` | `8607461d` | yes | xmm |
| unsafe | 823 | 812 | 1 | 3,647 | - | - | 179,434,779 | 1,053,039,090 | `79a3e350` | `9b0442d5` | yes | xmm |
| verus | 818 | 807 | 1 | 3,567 | - | - | 179,409,774 | 1,053,019,085 | `a818b2fa` | `cd7ebf31` | yes | xmm |
| c-gcc-h | 578 | 573 | 1 | 2,491 | - | - | 184,543,263 | 1,060,798,943 | `b20a1088` | `9a1f8952` | yes | xmm |
| c-clang-h | 756 | 732 | 0 | 3,189 | - | - | 152,958,817 | 882,659,021 | `b91adb37` | `b91adb37` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 424 | 171,560,380 | - | 900,066 | - | `847db30c` | `847db30c` | yes | - |
| c-clang | 66 | 66 | 0 | 273 | 131,163,820 | - | 500,051 | - | `e3c05d56` | `e3c05d56` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 758,980,220 | - | 625,077 | - | `df7a86a8` | `e57b14aa` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 803,655,220 | - | 625,077 | - | `126c8594` | `8875bed0` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 845,925,060 | - | 625,077 | - | `e8bfc3e5` | `18ebe784` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 926,870,760 | - | 625,056 | - | `095168a9` | `51ddb980` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 424 | 171,610,380 | - | 900,066 | - | `905577dd` | `905577dd` | yes | - |
| c-clang-h | 66 | 66 | 0 | 273 | 131,238,820 | - | 500,051 | - | `681c2638` | `681c2638` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | no | no | 335/335 vs 352/352 | 14 B vs 6 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 200/198 vs 200/198 | 12 B vs 12 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 92.12 | 97.98 | 6.4% | 17.98 | 18.19 | 1.2% |
| c-gcc | whole | 93.38 | 98.41 | 5.4% | 17.88 | 18.45 | 3.2% |
| c-clang | isolated | 91.70 | 94.15 | 2.7% | 17.75 | 18.23 | 2.7% |
| c-clang | whole | 91.56 | 96.85 | 5.8% | 17.65 | 18.38 | 4.2% |
| safe_naive | isolated | 124.49 | 131.68 | 5.8% | 23.49 | 24.08 | 2.5% |
| safe_naive | whole | 119.50 | 122.10 | 2.2% | 22.58 | 24.24 | 7.4% |
| safe_tuned | isolated | 103.17 | 108.92 | 5.6% | 19.61 | 20.68 | 5.4% |
| safe_tuned | whole | 106.21 | 115.05 | 8.3% | 20.21 | 20.86 | 3.2% |
| unsafe | isolated | 97.98 | 103.40 | 5.5% | 19.05 | 19.37 | 1.7% |
| unsafe | whole | 101.84 | 104.31 | 2.4% | 19.64 | 20.20 | 2.9% |
| verus | isolated | 98.10 | 99.78 | 1.7% | 19.44 | 19.86 | 2.2% |
| verus | whole | 104.48 | 109.71 | 5.0% | 20.24 | 20.75 | 2.6% |
| c-gcc-h | isolated | 92.31 | 95.95 | 3.9% | 18.10 | 18.34 | 1.4% |
| c-gcc-h | whole | 92.74 | 98.77 | 6.5% | 17.88 | 18.21 | 1.9% |
| c-clang-h | isolated | 91.33 | 99.02 | 8.4% | 17.85 | 18.10 | 1.4% |
| c-clang-h | whole | 91.40 | 97.09 | 6.2% | 17.63 | 17.93 | 1.7% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
