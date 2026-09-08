# ph07-strcut-cursor — results

Generated 2026-09-08T13:48:55Z from `results/ph07-strcut-cursor.json` (git `aac1442b1694`, working tree dirty).

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
| adversarial-empty.bin | 8 | 17 | 17 | False | n_iters=8 stride=9 n_blob=9 nwin=1 calls=8 work/call=9B san=fires truncated=False expected=11424172624523374464 |
| adversarial-nowin.bin | 8 | 81 | 81 | False | n_iters=8 stride=74 n_blob=73 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| adversarial-offbyone.bin | 8 | 113 | 113 | False | n_iters=8 stride=105 n_blob=105 nwin=1 calls=8 work/call=105B san=fires truncated=False expected=11424172624523374464 |
| adversarial-silent.bin | 8 | 113 | 113 | False | n_iters=8 stride=105 n_blob=105 nwin=1 calls=8 work/call=105B san=fires truncated=False expected=11424172624523374464 |
| adversarial-wild.bin | 8 | 113 | 113 | False | n_iters=8 stride=105 n_blob=105 nwin=1 calls=8 work/call=105B san=fires truncated=False expected=11424172624523374464 |
| large.bin | 12,000 | 8,351,708 | 8,351,708 | False | n_iters=12000 stride=4074 n_blob=8351700 nwin=2050 calls=12000 work/call=4074B san=clean truncated=False expected=7546772105060097026 |
| small.bin | 25,000 | 17,704 | 17,704 | False | n_iters=25000 stride=553 n_blob=17696 nwin=32 calls=25000 work/call=553B san=clean truncated=False expected=1771235065085513576 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — the start walk's only exit is the accumulated count, `if (n > from)` at mbfilter.c:1206, and `p` is never compared against `string->val + string->len`. The Rust spelling is the ROTATED form -- read once, then `while n <= frm` -- which performs the same reads in the same order (provenance.divergences)
  - `rust` — `while n <= frm`
- **required** — *per language:*
  - `c` — `m = mbtab[*p]`
  - `rust` — `MBTAB`
- **required** — *per language:*
  - `c` — `if (k >= (int)string->len)`
  - `rust` — `if k >= slen`
- **required** — *per language:*
  - `c` — `slen = (unsigned int)(len - 9)`
  - `rust` — `s.len() - 1`
- **required** — R1h is the real upstream fix cb3cca21b345 and NOTHING ELSE, and R2-R5 implement the same function, because that fix is COMPLETE -- unlike ph03's, it leaves no residue (controls/fix_scope.py Q1: 15 333 over-reads become 0). NO BACKTICKED SPELLING, deliberately: this is a statement about WHICH ALGORITHM each rung implements and no single token decides it. The mechanical check is controls/negatives.py --emit noguard, which must NOT verify.
- **required** — the mblen_table is STATIC DATA in every rung -- a 256-byte constant lifted verbatim from mbfilter_utf8.c:39-56, not part of the blob. NO BACKTICKED SPELLING: the C writes a file-scope `static const unsigned char`, the Rust rungs a `static [u8; 256]` and verus.rs a `pub const [u8; 256]`, which are three legitimate spellings of one fact. An attacker who could choose the table could put a zero in it and hang the start walk, which is a defect PHP does not have.
- **FORBIDDEN** — `if (n >= from)` -- relaxing the strict exit test. It moves the cut by one character and it would mask the terminator read the upstream clamp depends on. The strictness is the program.
- **FORBIDDEN** — `p - string->val < (int)string->len` -- the in-loop bound a reader adds on sight. Adding it to the start walk deletes the row: the whole point is that the bound is computed and then not consulted until `:1227`.
- **FORBIDDEN** — `frm = slen` -- the 2010 in-library CLAMP (d9dda48f8a7e's prologue) written into a Rust rung. It is a real upstream guard but it is NOT this row's fix_commit and it is a DIFFERENT function: cb3cca21b345 returns FALSE where the clamp returns a cut. controls/fix_scope.py measures both.

> **Why**: ph07 is `mbfl_strcut`'s mblen_table arm out of PHP 5.0.0, `ext/mbstring/libmbfl/mbfl/mbfilter.c:1179-1259`, corpus row CRASH-124, tier `narrowed`. THE IDIOM IS A CURSOR ADVANCED BY THE DATA WITH NO END TEST. `:1179` reads the true length into `len` and `:1202-1210` never looks at it: `for (;;) { m = mbtab[*p]; n += m; p += m; if (n > from) break; start = n; }` -- the only exit is the accumulated count passing the caller's `from`, and `p` is never compared against `string->val + string->len`. The clamps at `:1227-1241` do use `len`, but they run AFTER the walk, which is after the over-read. ⭐ AND THE SAME FUNCTION'S SECOND WALK IS BOUNDED: `:1213`'s `if (k >= (int)string->len)` means `:1217-1222` only ever runs while `n <= k < string->len`, so every byte IT reads is in range. One function, adjacent lines, one guarded search and one unguarded one -- that asymmetry is the row. ⚠ THERE IS EXACTLY ONE LIMB AND IT IS A READ: after the clamps `0 <= start <= end <= len`, so the copy at `:1248-1252` is always in bounds however wild the walk was, and the returned value is UNAFFECTED by the out-of-bounds bytes (controls/fix_scope.py Q3: 0 of 15 333 over-reading calls move under seven different fillers, with a must-fire control at 13 293). That is why it shipped byte-identical in six releases. ⚠ THE ZVAL TERMINATOR IS PART OF THE PROGRAM. `string->val` is a PHP string, `emalloc(len + 1)` with `val[len] == 0`, so a walk that reaches index `len` finds `mblen_table_utf8[0] == 1` and steps past `from`. Both upstream guards admit `from == string->len` for that reason, and `inputs/gen.py` writes the NUL into every window. ⚠ R1h IS `cb3cca21b345` AND IT IS IN THE CALLER, IN ANOTHER FILE -- `PHP_FUNCTION(mb_strcut)` in `ext/mbstring/mbstring.c`, 2005-12-15, first shipped in php-5.1.2. That is why `mbfl_strcut`'s body is byte-identical from php-5.0.0 to php-5.3.2. This row's `kernel()` wrapper IS that function -- it already carries mbstring.c:1787-1805's two negative clamps -- so the fix lands in upstream's own position, immediately before the call at `:1807`. c/kernel_hardened.c and NOTES.md §4 state the residual fidelity question rather than smoothing it over. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/ph07-strcut-cursor.json`, contract `be5f5818ffa6`.

`25` backticked spelling(s) over `6` rung(s) → **72** (spelling, rung) pair(s), **28** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 8 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 7 spelling(s) pin nothing**, 0 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - pins nothing — `string->val + string->len` (required[0], c, 0 of 2 rungs)
  - pins nothing — `while n <= frm` (required[0], c, 0 of 2 rungs)
  - pins nothing — `static [u8; 256]` (required[5], c, 0 of 2 rungs)
  - pins nothing — `pub const [u8; 256]` (required[5], c, 0 of 2 rungs)
  - pins nothing — `static const unsigned char` (required[5], rust, 0 of 4 rungs)
  - pins nothing — `static [u8; 256]` (required[5], rust, 0 of 4 rungs)
  - pins nothing — `pub const [u8; 256]` (required[5], rust, 0 of 4 rungs)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## What the gate said out loud (reporting only)

From `results/gate/ph07-strcut-cursor.json` — the `loud` and `controls_json` keys, at contract `be5f5818ffa6`. **These did not fail the gate and are not defects**; they are the conditions `check.py` refuses to be silent about. Each one is a caveat on a number below or on the declaration above. The run's **verdict** is deliberately not printed here: it is an output of the same gate run that checks this table is current (stage `9c`), and rendering it made the table an input to its own checker — see `read_gate_loud`. Read the verdict from `results/gate/ph07-strcut-cursor.json`.

- **`doc-citation-other`** — 3 line citation(s) into harness modules other than `check.py`. NOT failed: these sit in measurement-hashed files, so re-citing them by function costs a re-measure (RECAP queue item 38). Cite the FUNCTION when one of these files is next re-measured anyway: patterns/ph07-strcut-cursor/c/emalloc_shim.h:117 -> build.py:163-165 . patterns/ph07-strcut-cursor/c/emalloc_shim.h:133 -> build.py:167 . patterns/ph07-strcut-cursor/c/emalloc_shim.h:492 -> build.py:168-171
- **`tcb-unsafe`** — verus.rs:371 `vset_unchecked`'s `requires` constrains nothing about ['x'], which its trusted body uses. spec.md justifies it: `x: u8` is a PURE VALUE and needs no precondition. The unchecked operation is `*v.get_unchecked_mut(i) = x`: its definedness depends on `i` being in bounds and on `v` being a live `Vec<u8>`, and on NOTHING about the byte being written -- every one of the 256 values of `x` is a legal `u8` store into a byte that is already initialised (`vec![0u8; cap]` initialised the whole buffer before the first call site is reached). Contrast the shape this stage exists to catch, `requires n >= 0` on a `usize`: there the unconstrained parameter was the one the body indexed with. Here the indexing parameter `i` IS constrained, by `i < old(v)@.len()`, and the `ensures` names `x` in the post-state -- `final(v)@ == old(v)@.update(i as int, x)` -- so a body that stored anything other than `x`, or stored it anywhere other than `i`, could not satisfy its own postcondition.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 315 | 308 | 0 | 1,204 | 59,411,690 | 191,792,843 | 350,053 | 168,053 | `89bcf4be` | `89bcf4be` | yes | xmm |
| c-clang | 419 | 403 | 1 | 1,789 | 50,664,535 | 158,738,416 | 350,054 | 168,054 | `40bc9615` | `37387f6a` | yes | xmm |
| safe_naive | 301 | 297 | 5 | 1,147 | 70,457,098 | 236,039,298 | 350,275 | 168,275 | `f706aeb5` | `c4943f3a` | yes | xmm |
| safe_tuned | 297 | 293 | 10 | 1,142 | 50,735,617 | 169,914,706 | 350,275 | 168,275 | `78787f9e` | `8f9b0790` | yes | - |
| unsafe | 255 | 252 | 7 | 953 | 44,906,123 | 149,805,421 | 350,275 | 168,275 | `b20b2fd9` | `f4715986` | yes | - |
| verus | 255 | 252 | 7 | 953 | 44,906,123 | 149,805,421 | 350,270 | 168,270 | `b3ecc80e` | `5d9457de` | yes | - |
| c-gcc-h | 322 | 316 | 0 | 1,254 | 59,593,760 | 191,878,756 | 350,053 | 168,053 | `bb36c25e` | `bb36c25e` | yes | xmm |
| c-clang-h | 431 | 417 | 1 | 1,837 | 50,895,761 | 158,847,918 | 350,054 | 168,054 | `a1e5661e` | `f422eafc` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 134 | 134 | 0 | 466 | 65,568,088 | - | 900,066 | - | `d85c994c` | `d85c994c` | yes | - |
| c-clang | 109 | 109 | 1 | 380 | 53,150,634 | - | 500,052 | - | `5b13148b` | `7797d878` | yes | - |
| safe_naive | 454 | 454 | 9 | 2,583 | 252,275,013 | - | 625,077 | - | `c609e1b7` | `ce623c14` | yes | - |
| safe_tuned | 504 | 504 | 15 | 2,881 | 231,577,965 | - | 625,077 | - | `12e694fb` | `f292537d` | yes | - |
| unsafe | 442 | 442 | 14 | 2,530 | 301,676,919 | - | 625,077 | - | `8f459829` | `251d782f` | yes | - |
| verus | 464 | 464 | 5 | 2,683 | 346,231,283 | - | 625,056 | - | `3b8aafc9` | `25b43ea7` | yes | - |
| c-gcc-h | 150 | 150 | 0 | 516 | 65,793,088 | - | 900,066 | - | `62c25dc7` | `62c25dc7` | yes | - |
| c-clang-h | 126 | 126 | 1 | 443 | 53,375,634 | - | 500,052 | - | `e98284e8` | `9bc5e02c` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 466 | 461 | 2 | 1,954 | - | - | 59,831,864 | 196,773,433 | `b8dcc367` | `e5922ee1` | yes | xmm |
| c-clang | 708 | 686 | 0 | 2,890 | - | - | 49,565,093 | 153,578,517 | `9a356d54` | `9a356d54` | yes | xmm |
| safe_naive | 956 | 946 | 1 | 4,175 | - | - | 70,570,362 | 236,023,024 | `f55b26b6` | `c7732cab` | yes | xmm |
| safe_tuned | 934 | 925 | 1 | 4,095 | - | - | 51,001,615 | 170,042,483 | `a21c55e9` | `0f8006bf` | yes | xmm |
| unsafe | 875 | 866 | 1 | 3,791 | - | - | 45,212,783 | 149,952,708 | `72e828d1` | `8836ccd6` | yes | xmm |
| verus | 888 | 877 | 1 | 3,855 | - | - | 45,093,972 | 149,895,711 | `787b2ff2` | `503cd4e0` | yes | xmm |
| c-gcc-h | 472 | 467 | 1 | 1,983 | - | - | 60,284,390 | 196,990,660 | `e5249bdb` | `b043416d` | yes | xmm |
| c-clang-h | 708 | 690 | 0 | 2,872 | - | - | 49,665,096 | 153,626,520 | `d42a2e9e` | `d42a2e9e` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 425 | 65,568,088 | - | 900,066 | - | `e90469d5` | `e90469d5` | yes | - |
| c-clang | 66 | 66 | 0 | 273 | 53,150,634 | - | 500,051 | - | `a5ab58a0` | `a5ab58a0` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 252,275,013 | - | 625,077 | - | `e4d50d18` | `3db9a97d` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 231,577,965 | - | 625,077 | - | `6a90b60b` | `ebbd97a5` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 301,676,919 | - | 625,077 | - | `7a0016f0` | `77681d04` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 346,231,283 | - | 625,056 | - | `bebefac2` | `97fbd1ee` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 425 | 65,793,088 | - | 900,066 | - | `96aae5f2` | `96aae5f2` | yes | - |
| c-clang-h | 66 | 66 | 0 | 273 | 53,350,634 | - | 500,051 | - | `901b4415` | `901b4415` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | no | no | 442/442 vs 464/464 | 14 B vs 5 B |
| unsafe vs verus | O3 | no | **yes** | no | 255/252 vs 255/252 | 7 B vs 7 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 50.03 | 51.39 | 2.7% | 15.57 | 16.06 | 3.1% |
| c-gcc | whole | 50.14 | 53.28 | 6.3% | 15.21 | 15.84 | 4.2% |
| c-clang | isolated | 50.66 | 52.46 | 3.6% | 15.51 | 16.42 | 5.8% |
| c-clang | whole | 50.77 | 53.31 | 5.0% | 15.36 | 16.14 | 5.0% |
| safe_naive | isolated | 50.73 | 56.94 | **12.2% ✗** | 16.18 | 17.03 | 5.2% |
| safe_naive | whole | 50.72 | 56.96 | **12.3% ✗** | 16.29 | 16.76 | 2.9% |
| safe_tuned | isolated | 50.65 | 57.61 | **13.7% ✗** | 16.08 | 16.81 | 4.5% |
| safe_tuned | whole | 50.63 | 57.39 | **13.4% ✗** | 16.16 | 16.66 | 3.1% |
| unsafe | isolated | 50.34 | 54.38 | 8.0% | 16.03 | 16.58 | 3.4% |
| unsafe | whole | 50.68 | 51.58 | 1.8% | 16.12 | 16.64 | 3.2% |
| verus | isolated | 50.96 | 51.93 | 1.9% | 16.25 | 16.73 | 3.0% |
| verus | whole | 50.29 | 51.51 | 2.4% | 16.09 | 16.89 | 5.0% |
| c-gcc-h | isolated | 50.09 | 51.11 | 2.1% | 15.45 | 15.94 | 3.1% |
| c-gcc-h | whole | 50.79 | 51.58 | 1.6% | 15.49 | 15.84 | 2.3% |
| c-clang-h | isolated | 50.66 | 51.46 | 1.6% | 15.65 | 15.92 | 1.7% |
| c-clang-h | whole | 50.47 | 51.21 | 1.5% | 15.50 | 16.15 | 4.2% |

**4 of 32 wall-clock cells exceed the 10% min-to-median spread threshold and are DISCARDED** per `.memory/03-measurement.md` step 4. They are printed above marked ✗ rather than deleted, because a missing cell that looks like an omission is worse than a documented failure (`.memory/02-bench-rules.md`). **No claim in this report rests on a marked row.**

- `safe_naive / isolated` on `large.bin`: spread 12.2%
- `safe_naive / whole` on `large.bin`: spread 12.3%
- `safe_tuned / isolated` on `large.bin`: spread 13.7%
- `safe_tuned / whole` on `large.bin`: spread 13.4%


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
