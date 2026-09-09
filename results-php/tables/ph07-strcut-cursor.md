# ph07-strcut-cursor — results

Generated 2026-09-09T04:43:29Z from `results/ph07-strcut-cursor.json` (git `fd071760a687`, working tree dirty).

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
| large.bin | 12,000 | 8,351,708 | 8,351,708 | False | n_iters=12000 stride=4074 n_blob=8351700 nwin=2050 calls=12000 work/call=4074B san=clean truncated=False expected=2579958070518048867 |
| small.bin | 25,000 | 17,704 | 17,704 | False | n_iters=25000 stride=553 n_blob=17696 nwin=32 calls=25000 work/call=553B san=clean truncated=False expected=11803788199505851357 |

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
- **required** — R1h is the guard CONFIGURATION UPSTREAM CONVERGED ON -- php-5.2.12 .. php-5.2.17, PHP_FUNCTION(mb_strcut) body sha256 26e2099e33433c74, which is cb3cca21b345 hunk (a) and NOTHING ELSE -- and R2-R5 implement the same function, because that configuration is COMPLETE: unlike ph03's fix it leaves no residue (controls/fix_scope.py Q1: 15 333 over-reads become 0). ⚠⚠ WHAT WAS CHOSEN AND WHAT WAS CHOSEN AGAINST, because a row publishes both. THE ALTERNATIVE, and it is what this row shipped until TASK_PHP_018: cite the 2005 commit cb3cca21b345 entire -- BOTH hunks -- and disclose that hunk (b) changes benign output. It was rejected on THREE measurements, none of them about Rust or Verus. (i) hunk (b) removes NONE of the 15 333 out-of-bounds reads and hunk (a) removes ALL of them, so (b) is not part of the memory-safety fix (controls/fix_scope.py Q1). (ii) hunk (b) CHANGES the answer on 15 870 of 117 612 benign calls (13.5 %), so honouring the whole commit forced inputs/gen.py to exclude the region it fires in -- a corpus of 86.5 % of the benign domain, presented as the domain (Q2). (iii) UPSTREAM REMOVED IT: c2471b495009 (Moriyoshi Koizumi, 2009-09-23) deletes hunk (b) as bug #49354, 'mb_strcut() cuts wrong length when offset is within a multibyte character', and ships ext/mbstring/tests/bug49354.phpt with it. controls/bug49354.py replays those six expectations against all three configurations: hunk (a) alone agrees on all six, hunk (a)+(b) is WRONG on one, and R1 over-reads on one. ⚠ THE COST OF THE CHOICE, stated rather than smoothed over: a tag range is not a commit, and PROTOCOL_PHP.md C says R1h is the real upstream fix_commit. The argument is that what upstream SHIPPED AND KEPT is a stronger citation than what it once merged -- five tags carry this configuration byte-for-byte, and php-5.3.2 .. php-5.3.29 carry it respelled (body sha256 49ad3ab2796d63e4) -- and that a subset of a commit pinned by (tag range, function, body sha256) is more checkable than a commit id, not less. It is still a SUBSET of a labelled security fix and the row says so here rather than in a footnote. Both commits are cited in provenance.fix_commit and both patches are under controls/. NO BACKTICKED SPELLING IN THIS ENTRY, deliberately: it is a statement about WHICH ALGORITHM each rung implements and no single token decides it. The mechanical checks are controls/negatives.py --emit noguard, which must NOT verify, and forbidden[3], which pins hunk (b)'s own two spellings ABSENT from every rung.
- **required** — the mblen_table is STATIC DATA in every rung -- a 256-byte constant lifted verbatim from mbfilter_utf8.c:39-56, not part of the blob. NO BACKTICKED SPELLING: the C writes a file-scope `static const unsigned char`, the Rust rungs a `static [u8; 256]` and verus.rs a `pub const [u8; 256]`, which are three legitimate spellings of one fact. An attacker who could choose the table could put a zero in it and hang the start walk, which is a defect PHP does not have.
- **FORBIDDEN** — `if (n >= from)` -- relaxing the strict exit test. It moves the cut by one character and it would mask the terminator read the upstream clamp depends on. The strictness is the program.
- **FORBIDDEN** — `p - string->val < (int)string->len` -- the in-loop bound a reader adds on sight. Adding it to the start walk deletes the row: the whole point is that the bound is computed and then not consulted until `:1227`.
- **FORBIDDEN** — `frm = slen` -- the 2010 in-library CLAMP (d9dda48f8a7e's prologue) written into a Rust rung. It is a real upstream guard but it is NOT this row's fix_commit and it is a DIFFERENT function: cb3cca21b345 returns FALSE where the clamp returns a cut. controls/fix_scope.py measures both.
- **FORBIDDEN** — *per language:*
  - `c` — `((unsigned)from + (unsigned)length) > str_len` -- cb3cca21b345 HUNK (b), in the C rungs' own spelling. TASK_PHP_018 pins it ABSENT because upstream removed it (c2471b495009, bug #49354) and R1h is now hunk (a) alone: a rung that re-acquired it would compute a function upstream withdrew, and would silently re-impose the corpus restriction inputs/gen.py has just been rewritten to forbid. ⚠ PER-LANGUAGE because the C and Rust spellings share no token. ⚠ It pins the SPELLING and not the property: a rung could still clamp the length argument by some third expression, which is what a forbidden entry can and cannot do, and is why controls/negatives.py, controls/bug49354.py and controls/spellings.py sit beside it. Measured clean on all six rungs with harness/check.py::spelling_matches itself (.temp/php18/spellcheck.log).
  - `rust` — `frm.saturating_add(length) > slen` -- cb3cca21b345 HUNK (b), in the four Rust rungs' own spelling. TASK_PHP_018 pins it ABSENT because upstream removed it (c2471b495009, bug #49354) and R1h is now hunk (a) alone: a rung that re-acquired it would compute a function upstream withdrew, and would silently re-impose the corpus restriction inputs/gen.py has just been rewritten to forbid. ⚠ PER-LANGUAGE because the C and Rust spellings share no token. ⚠ It pins the SPELLING and not the property: a rung could still clamp the length argument by some third expression, which is what a forbidden entry can and cannot do, and is why controls/negatives.py, controls/bug49354.py and controls/spellings.py sit beside it. Measured clean on all six rungs with harness/check.py::spelling_matches itself (.temp/php18/spellcheck.log).

> **Why**: ph07 is `mbfl_strcut`'s mblen_table arm out of PHP 5.0.0, `ext/mbstring/libmbfl/mbfl/mbfilter.c:1179-1259`, corpus row CRASH-124, tier `narrowed`. THE IDIOM IS A CURSOR ADVANCED BY THE DATA WITH NO END TEST. `:1179` reads the true length into `len` and `:1202-1210` never looks at it: `for (;;) { m = mbtab[*p]; n += m; p += m; if (n > from) break; start = n; }` -- the only exit is the accumulated count passing the caller's `from`, and `p` is never compared against `string->val + string->len`. The clamps at `:1227-1241` do use `len`, but they run AFTER the walk, which is after the over-read. ⭐ AND THE SAME FUNCTION'S SECOND WALK IS BOUNDED: `:1213`'s `if (k >= (int)string->len)` means `:1217-1222` only ever runs while `n <= k < string->len`, so every byte IT reads is in range. One function, adjacent lines, one guarded search and one unguarded one -- that asymmetry is the row. ⚠ THERE IS EXACTLY ONE LIMB AND IT IS A READ: after the clamps `0 <= start <= end <= len`, so the copy at `:1248-1252` is always in bounds however wild the walk was, and the returned value is UNAFFECTED by the out-of-bounds bytes (controls/fix_scope.py Q3: 0 of 15 333 over-reading calls move under seven different fillers, with a must-fire control at 13 293). That is why it shipped byte-identical in six releases. ⚠ THE ZVAL TERMINATOR IS PART OF THE PROGRAM. `string->val` is a PHP string, `emalloc(len + 1)` with `val[len] == 0`, so a walk that reaches index `len` finds `mblen_table_utf8[0] == 1` and steps past `from`. Both upstream guards admit `from == string->len` for that reason, and `inputs/gen.py` writes the NUL into every window. ⚠ R1h IS A TAGGED CONFIGURATION AND IT IS IN THE CALLER, IN ANOTHER FILE -- `php-5.2.12 .. php-5.2.17`, `PHP_FUNCTION(mb_strcut)` in `ext/mbstring/mbstring.c`, body sha256 26e2099e33433c74, which is `cb3cca21b345` (2005-12-15) hunk (a) after `c2471b495009` (2009-09-23, bug #49354) removed hunk (b). That the fix is one file up is why `mbfl_strcut`'s body is byte-identical at NINE tags from php-5.0.0 to php-5.3.2. This row's `kernel()` wrapper IS that caller -- it already carries mbstring.c:1787-1805's two negative clamps, and the whole frame is pinned as `provenance.extra_spans[1]` -- so the guard lands in upstream's own position, immediately before the call at `:1807`. ⭐ THE ROW SHIPPED BOTH HUNKS UNTIL TASK_PHP_018 AND ITS OWN GATE HAD SAID WHY NOT: `check.py` stage 7h refuses an R1h that changes benign output, hunk (b) changes it on 13.5 % of benign calls while removing none of the 15 333 over-reads, and the row read the refusal as a harness limitation and restricted the corpus instead. Upstream reached the same verdict from a bug report four years later. `idiom.required[4]` states the choice and the alternative; `forbidden[3]` pins hunk (b)'s two spellings absent; controls/bug49354.py replays upstream's own six expectations; c/kernel_hardened.c and NOTES.md §4 state the residual fidelity question -- a subset of a labelled security fix, presented as an upstream configuration -- rather than smoothing it over. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/ph07-strcut-cursor.json`, contract `1f1508531bd4`.

`27` backticked spelling(s) over `6` rung(s) → **78** (spelling, rung) pair(s), **28** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 10 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
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

From `results/gate/ph07-strcut-cursor.json` — the `loud` and `controls_json` keys, at contract `1f1508531bd4`. **These did not fail the gate and are not defects**; they are the conditions `check.py` refuses to be silent about. Each one is a caveat on a number below or on the declaration above. The run's **verdict** is deliberately not printed here: it is an output of the same gate run that checks this table is current (stage `9c`), and rendering it made the table an input to its own checker — see `read_gate_loud`. Read the verdict from `results/gate/ph07-strcut-cursor.json`.

- **`doc-citation-other`** — 3 line citation(s) into harness modules other than `check.py`. NOT failed: these sit in measurement-hashed files, so re-citing them by function costs a re-measure (RECAP queue item 38). Cite the FUNCTION when one of these files is next re-measured anyway: patterns/ph07-strcut-cursor/c/emalloc_shim.h:117 -> build.py:163-165 . patterns/ph07-strcut-cursor/c/emalloc_shim.h:133 -> build.py:167 . patterns/ph07-strcut-cursor/c/emalloc_shim.h:492 -> build.py:168-171
- **`tcb-unsafe`** — verus.rs:380 `vset_unchecked`'s `requires` constrains nothing about ['x'], which its trusted body uses. spec.md justifies it: `x: u8` is a PURE VALUE and needs no precondition. The unchecked operation is `*v.get_unchecked_mut(i) = x`: its definedness depends on `i` being in bounds and on `v` being a live `Vec<u8>`, and on NOTHING about the byte being written -- every one of the 256 values of `x` is a legal `u8` store into a byte that is already initialised (`vec![0u8; cap]` initialised the whole buffer before the first call site is reached). Contrast the shape this stage exists to catch, `requires n >= 0` on a `usize`: there the unconstrained parameter was the one the body indexed with. Here the indexing parameter `i` IS constrained, by `i < old(v)@.len()`, and the `ensures` names `x` in the post-state -- `final(v)@ == old(v)@.update(i as int, x)` -- so a body that stored anything other than `x`, or stored it anywhere other than `i`, could not satisfy its own postcondition.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 315 | 308 | 0 | 1,204 | 62,059,566 | 204,276,445 | 350,053 | 168,053 | `89bcf4be` | `89bcf4be` | yes | xmm |
| c-clang | 419 | 403 | 1 | 1,789 | 51,962,042 | 166,347,465 | 350,054 | 168,054 | `40bc9615` | `37387f6a` | yes | xmm |
| safe_naive | 296 | 292 | 5 | 1,131 | 74,157,752 | 252,171,985 | 350,275 | 168,275 | `7853b32d` | `54413d23` | yes | xmm |
| safe_tuned | 292 | 288 | 10 | 1,126 | 51,533,587 | 176,532,665 | 350,275 | 168,275 | `eb967575` | `08146acc` | yes | - |
| unsafe | 251 | 247 | 7 | 953 | 46,261,358 | 157,761,386 | 350,275 | 168,275 | `909a1a4d` | `8f6740be` | yes | - |
| verus | 251 | 247 | 7 | 953 | 46,261,358 | 157,761,386 | 350,270 | 168,270 | `f6fec880` | `8b9a29fc` | yes | - |
| c-gcc-h | 323 | 317 | 0 | 1,242 | 62,129,977 | 204,313,326 | 350,053 | 168,053 | `2ee34f29` | `2ee34f29` | yes | xmm |
| c-clang-h | 427 | 412 | 1 | 1,821 | 52,116,699 | 166,420,720 | 350,054 | 168,054 | `cdda0d54` | `0fffa2b1` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 134 | 134 | 0 | 466 | 74,304,184 | - | 900,066 | - | `d85c994c` | `d85c994c` | yes | - |
| c-clang | 109 | 109 | 1 | 380 | 60,248,712 | - | 500,052 | - | `5b13148b` | `7797d878` | yes | - |
| safe_naive | 439 | 439 | 11 | 2,485 | 273,567,006 | - | 625,077 | - | `bf424e91` | `129e9862` | yes | - |
| safe_tuned | 489 | 489 | 1 | 2,783 | 249,603,042 | - | 625,077 | - | `193059ff` | `a107aeb9` | yes | - |
| unsafe | 427 | 427 | 0 | 2,432 | 331,177,162 | - | 625,077 | - | `d41bdd09` | `d41bdd09` | yes | - |
| verus | 449 | 449 | 7 | 2,585 | 377,936,070 | - | 625,056 | - | `0a32f353` | `7536d27f` | yes | - |
| c-gcc-h | 141 | 141 | 0 | 492 | 74,379,184 | - | 900,066 | - | `0567ff49` | `0567ff49` | yes | - |
| c-clang-h | 119 | 119 | 1 | 423 | 60,373,712 | - | 500,052 | - | `aeb0c62e` | `b68d0ff8` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 466 | 461 | 2 | 1,954 | - | - | 62,009,993 | 207,941,975 | `b8dcc367` | `e5922ee1` | yes | xmm |
| c-clang | 708 | 686 | 0 | 2,890 | - | - | 50,669,466 | 160,415,095 | `9a356d54` | `9a356d54` | yes | xmm |
| safe_naive | 959 | 949 | 1 | 4,175 | - | - | 74,151,246 | 252,119,303 | `2d405060` | `52859b51` | yes | xmm |
| safe_tuned | 934 | 925 | 1 | 4,095 | - | - | 51,801,865 | 176,661,183 | `2b4d314c` | `02c41414` | yes | xmm |
| unsafe | 875 | 866 | 1 | 3,807 | - | - | 46,549,963 | 157,899,391 | `0fb4cef1` | `bb59591d` | yes | xmm |
| verus | 883 | 872 | 1 | 3,839 | - | - | 46,429,632 | 157,841,900 | `41b17f3c` | `3501fd48` | yes | xmm |
| c-gcc-h | 472 | 467 | 2 | 1,970 | - | - | 62,342,527 | 208,098,913 | `6baef745` | `821b48f2` | yes | xmm |
| c-clang-h | 704 | 686 | 0 | 2,840 | - | - | 50,669,469 | 160,415,098 | `f0e5d6d9` | `f0e5d6d9` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 425 | 74,304,184 | - | 900,066 | - | `e90469d5` | `e90469d5` | yes | - |
| c-clang | 66 | 66 | 0 | 273 | 60,248,712 | - | 500,051 | - | `a5ab58a0` | `a5ab58a0` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 273,567,006 | - | 625,077 | - | `8cf626ed` | `f53675dc` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 249,603,042 | - | 625,077 | - | `7da43a57` | `13bebb20` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 331,177,162 | - | 625,077 | - | `eb010a08` | `fdc5feb4` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 377,936,070 | - | 625,056 | - | `bebefac2` | `97fbd1ee` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 425 | 74,379,184 | - | 900,066 | - | `c2d1dc7a` | `c2d1dc7a` | yes | - |
| c-clang-h | 66 | 66 | 0 | 273 | 60,348,712 | - | 500,051 | - | `cb371d5f` | `cb371d5f` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | no | no | 427/427 vs 449/449 | 0 B vs 7 B |
| unsafe vs verus | O3 | no | **yes** | no | 251/247 vs 251/247 | 7 B vs 7 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 49.91 | 51.36 | 2.9% | 15.15 | 16.27 | 7.4% |
| c-gcc | whole | 50.10 | 51.06 | 1.9% | 14.92 | 15.83 | 6.1% |
| c-clang | isolated | 50.48 | 51.81 | 2.6% | 15.07 | 16.33 | 8.4% |
| c-clang | whole | 50.45 | 51.76 | 2.6% | 15.01 | 16.34 | 8.8% |
| safe_naive | isolated | 50.80 | 51.83 | 2.0% | 16.07 | 17.18 | 6.9% |
| safe_naive | whole | 50.49 | 51.70 | 2.4% | 16.10 | 17.19 | 6.8% |
| safe_tuned | isolated | 50.60 | 52.07 | 2.9% | 15.78 | 17.06 | 8.1% |
| safe_tuned | whole | 50.26 | 52.17 | 3.8% | 15.81 | 16.88 | 6.8% |
| unsafe | isolated | 50.22 | 54.28 | 8.1% | 15.74 | 16.67 | 5.9% |
| unsafe | whole | 50.57 | 54.72 | 8.2% | 15.69 | 16.33 | 4.1% |
| verus | isolated | 50.97 | 55.58 | 9.0% | 16.01 | 16.74 | 4.5% |
| verus | whole | 50.08 | 55.59 | **11.0% ✗** | 15.72 | 16.89 | 7.4% |
| c-gcc-h | isolated | 49.89 | 54.76 | 9.8% | 14.99 | 16.05 | 7.0% |
| c-gcc-h | whole | 50.53 | 55.08 | 9.0% | 15.00 | 16.21 | 8.1% |
| c-clang-h | isolated | 50.56 | 52.92 | 4.7% | 14.93 | 16.09 | 7.7% |
| c-clang-h | whole | 50.36 | 52.34 | 3.9% | 15.06 | 16.12 | 7.0% |

**1 of 32 wall-clock cells exceed the 10% min-to-median spread threshold and are DISCARDED** per `.memory/03-measurement.md` step 4. They are printed above marked ✗ rather than deleted, because a missing cell that looks like an omission is worse than a documented failure (`.memory/02-bench-rules.md`). **No claim in this report rests on a marked row.**

- `verus / whole` on `large.bin`: spread 11.0%


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 2 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `large.bin`
