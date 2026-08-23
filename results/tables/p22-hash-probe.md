# p22-hash-probe — results

Generated 2026-08-23T03:32:10Z from `results/p22-hash-probe.json` (git `cc270b61616c`, working tree dirty).

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
| adversarial-allempty.bin | 200 | 140 | 140 | False | n_iters=200 stride=132 n_blob=132 nwin=1 calls=200 work/call=132B nfill(w0)=0 maxprobe(w0)=0 san=clean hang=False truncated=False expected=4662693442260041728 |
| adversarial-full.bin | 1 | 140 | 140 | False | n_iters=1 stride=132 n_blob=132 nwin=1 calls=1 work/call=132B nfill(w0)=64 maxprobe(w0)=62 san=clean hang=True truncated=False expected=8190810770250117165 |
| adversarial-nearfull.bin | 200 | 140 | 140 | False | n_iters=200 stride=132 n_blob=132 nwin=1 calls=200 work/call=132B nfill(w0)=63 maxprobe(w0)=20 san=clean hang=False truncated=False expected=1685533861422832768 |
| adversarial-nkeybig.bin | 200 | 140 | 140 | False | n_iters=200 stride=132 n_blob=132 nwin=1 calls=200 work/call=132B nfill(w0)=23 maxprobe(w0)=3 san=clean hang=False truncated=False expected=11690051814024618624 |
| adversarial-stride3.bin | 100 | 11 | 11 | False | n_iters=100 stride=3 n_blob=3 nwin=0 calls=0 work/call=0B nfill(w0)=0 maxprobe(w0)=0 san=clean hang=False truncated=False expected=0 |
| degenerate.bin | 4,000 | 536 | 536 | False | n_iters=4000 stride=132 n_blob=528 nwin=4 calls=4000 work/call=132B nfill(w0)=16 maxprobe(w0)=2 san=clean hang=False truncated=False expected=17666168550866610390 |
| large.bin | 20,000 | 41,128 | 41,128 | False | n_iters=20000 stride=1028 n_blob=41120 nwin=40 calls=20000 work/call=1028B nfill(w0)=40 maxprobe(w0)=6 san=clean hang=False truncated=False expected=6415303255186503395 |
| small.bin | 20,000 | 5,288 | 5,288 | False | n_iters=20000 stride=132 n_blob=5280 nwin=40 calls=20000 work/call=132B nfill(w0)=32 maxprobe(w0)=4 san=clean hang=False truncated=False expected=12413078541623012263 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE SAFETY LINE, and the only thing c/kernel.c omits: the capacity conjunct, `if (k != SLB_P22_EMPTY && nfill < SLB_P22_TABCAP) {` in c/kernel_hardened.c. c/kernel.c writes `if (k != SLB_P22_EMPTY) {` there and is otherwise character-identical, so the scoped-absent audit pair this entry reports is on that rung and is correct.
  - `rust` — THE SAFETY LINE, present in ALL FOUR Rust rungs and written by hand in every one of them: `if k != EMPTY && nfill < TABCAP {`. Unlike every other pattern in this tree, no Rust rung gets this from the language -- see the why key.
- **required** — *per language:*
  - `c` — THE PROBE STEP, in both C rungs, and the reason the probe cursor cannot leave the table: `i = (i + 1) % SLB_P22_TABCAP;`.
  - `rust` — THE PROBE STEP, in all four Rust rungs: `i = (i + 1) % TABCAP;`.
- **required** — *per language:*
  - `c` — THE PROBE LOOP, and it is UNBOUNDED in both C rungs -- the hardened rung does not add a trip count, it adds the capacity conjunct above: `while (tab[i] != SLB_P22_EMPTY && tab[i] != k)`.
  - `rust` — The probe loop is unbounded in all four Rust rungs too, and its condition is the one place the SAFETY AXIS shows: the safe rungs index the table and the unsafe rungs read it through arr_get_unchecked, so this entry pins the property in prose and pins the STEP, in backticks, in the entry above. What all four spell is a test of the slot against EMPTY and against the key, WITH NO TRIP COUNT ANYWHERE. ⚠ It is this clause, in prose, that excludes a bounded probe -- not the two backticked entries in the forbidden list, which exclude the two ITERATOR spellings literally and match no hand-rolled counter at all: the control r3_bounded_kept writes a while loop against its own counter and matches neither of them. TASK_070_REVIEW F3; the why key gives the two separate reasons and prices what the exclusion costs. ⚠ NOTHING IN THIS SENTENCE IS BACKTICKED, deliberately: a backtick in a required entry PINS A SPELLING, and an earlier draft of this correction accidentally added three spellings no rung writes -- the same defect the take(nkey) entry below records and the gate reported it the same way, as required_pins_nothing.
- **required** — *per language:*
  - `c` — THE HASH, in both C rungs, spelled with / and % and never with >> and &: `* 2654435761u / 16777216u % SLB_P22_TABCAP`.
  - `rust` — THE HASH, in all four Rust rungs: `* 2654435761 / 16777216 % TABCAP`.
- **required** — *per language:*
  - `c` — THE TABLE IS CLEARED at the start of every call, so a call's answer does not depend on the previous call's table: `tab[j] = SLB_P22_EMPTY;` in both C rungs.
  - `rust` — the same, in all four Rust rungs, written the way the language supplies it: `[EMPTY; TABCAP]`.
- **required** — *per language:*
  - `c` — THE INSERT happens only into a slot the probe found EMPTY, so a key never overwrites a different key: `if (tab[i] == SLB_P22_EMPTY) {` in both C rungs, followed by `tab[i] = k;`.
  - `rust` — the same test and the same store in all four Rust rungs, spelled along the safety axis: an index in safe_naive.rs and safe_tuned.rs, arr_get_unchecked / arr_set_unchecked in unsafe.rs and verus.rs. Prose rather than a backtick for the reason the why key gives.
- **required** — *per language:*
  - `c` — the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the additive form's overflow never arises: `if (len - p < 1)` in both C rungs.
  - `rust` — the walk stops at the window in all four Rust rungs. safe_naive.rs, unsafe.rs and verus.rs write the same subtraction-first guard as C; safe_tuned.rs reaches the same set of keys with take(nkey) over a reslice, which is the R3-side lever and is exactly what this entry declines to pin. Prose, therefore, and not a backtick -- an earlier draft backticked take(nkey) here and the audit correctly reported it scoped-absent on the other three Rust rungs.
- **required** — *per language:*
  - `c` — a rejected key folds the SENTINEL rather than being skipped, so the fold's length is a function of the key count alone: `acc = acc * 31 + SLB_P22_SENT;` in both C rungs.
  - `rust` — the sentinel fold, in all four Rust rungs: `.wrapping_add(SENT)`.
- **required** — *per language:*
  - `c` — the fold is a serial Horner chain over `acc`, spelled with the literal multiplier: `acc = acc * 31 +` in both C rungs.
  - `rust` — the fold, in all four Rust rungs, spelled with the literal multiplier: `.wrapping_mul(31)`.
- **required** — *per language:*
  - `c` — the header is decoded with + and * and never with | and <<, so the whole specification stays inside linear arithmetic (.memory/04-verus.md): `256 *` in both C rungs.
  - `rust` — the same decode in all four Rust rungs: `256 *`.
- **required** — the declared key count is rejected before any key is read, so no rung can walk a header it has not validated: `nkey == 0` appears in all eight rungs.
- **required** — the number of slots filled is folded LAST, so a rung that inserted a different number of keys cannot produce the same checksum: `nfill` appears in the return expression of all eight rungs.
- **FORBIDDEN** — *per language:*
  - `rust` — `for _ in 0..TABCAP`
- **FORBIDDEN** — *per language:*
  - `rust` — `(0..TABCAP)`
- **FORBIDDEN** — *per language:*
  - `rust` — `probes < TABCAP`
- **FORBIDDEN** — *per language:*
  - `rust` — `#[verifier::exec_allows_no_decreases_clause]`
- **FORBIDDEN** — *per language:*
  - `rust` — `HashMap`
- **FORBIDDEN** — *per language:*
  - `rust` — `HashSet`
- **FORBIDDEN** — *per language:*
  - `c` — `probes < SLB_P22_TABCAP`
- **FORBIDDEN** — `>> 24`
- **FORBIDDEN** — `& 63`
- **FORBIDDEN** — `black_box`
- **FORBIDDEN** — `volatile`

> **Why**: POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all eight rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ON p22 THE PINNED SPELLING IS A CONJUNCT THAT NO LANGUAGE SUPPLIES. `nfill < TABCAP` is not a bounds check and no compiler, checker or sanitizer emits it: every table access in every rung is `tab[i]` with `i` reduced modulo TABCAP, so the accesses are in bounds in the BUGGY rung too. What the conjunct buys is TERMINATION, and safety in the Rust sense says nothing about that. Measured (../NOTES.md 0): the safe-Rust rung with the conjunct deleted hangs at -O0 and at -O3 with Miri silent, and c/kernel.c hangs under gcc and clang at both levels with ASan+UBSan silent. THAT IS WHY THE ENTRY IS SCOPED TO ALL EIGHT RUNGS RATHER THAN TO THE HARDENED C ONE: on ten other patterns here the buggy rung omits a check its language would have supplied, and pinning it in the safe rungs would be pinning something they cannot avoid. Here every rung writes it by hand or hangs. WHY THE PROBE LOOP IS UNBOUNDED IN ALL EIGHT RUNGS -- ⚠ **TWO REASONS, BECAUSE ONE OF THEM IS FALSE OF HALF OF WHAT IS EXCLUDED** (TASK_070_REVIEW F3, which measured it; until then this paragraph gave only reason (1) and gave it for both). (1) THE BOUND WRITTEN *INSTEAD OF* THE CONJUNCT IS A DIFFERENT FUNCTION. A bounded trip count also makes the loop terminate and it is idiomatic safe Rust, but put in place of `nfill < TABCAP` it finds a key that is present in a full table, where the shipped semantics rejects every operation once the table is full and folds SENT. That is measured and not asserted: the control `r3_bounded` prints `8190810770250110748` on adversarial-full.bin against the shipped `8190810770250117165`, and agrees on the other seven matrix inputs. Shipping it in one rung would put a semantic difference inside p22's safety column. (2) THE BOUND WRITTEN *IN ADDITION TO* THE CONJUNCT IS THE SAME FUNCTION, AND IS EXCLUDED ON DIFFERENT GROUND. The control `r3_bounded_kept` agrees with the shipped R3 on ALL EIGHT matrix inputs, so calling it a different function is false. What excludes it is the PROBE-LOOP `required` entry -- `required[2]` in the gate record -- and its *no trip count anywhere* -- and the ground is the same one that forbids `probes < TABCAP` two sentences below: a trip count in the OBJECT CODE is the fix wearing the proof's clothes. p22 IS an unbounded probe loop whose termination follows from a global invariant; a bounded one is a different pattern. The two spellings are the same edit on opposite sides of the safety axis, so admitting it in R3 while forbidding it in R5 would be incoherent, and admitting it in R5 would let the `decreases` be discharged from the trip count and delete the pattern's result. ⚠ **THE PRICE OF EXCLUSION (2) IS PUBLISHED RATHER THAN HIDDEN.** The in-contract R3 span is 4401.6100 ... 4411.6100, width 10.00; admitting `r3_bounded_kept` would take it to 4401.6100 ... 4569.2600 -- width 167.65 on small and 1235.96 on large, 16.8x wider. ⚠ **The direction does NOT flatter**: `r3_bounded_kept` is DEARER, so `R3ship` remains the cheapest in-contract R3 found and `R3 - R4 = +2.00` is unaffected. A 16.8x span movement reads like a retraction and is not one. ⚠ **AND NO GREP SETTLES (2).** The two backticked entries below, `for _ in 0..TABCAP` and `(0..TABCAP)`, exclude the two ITERATOR spellings literally -- they are the ones measured in `.temp/p22/probe/probe_rs.rs` -- but `r3_bounded_kept` writes `while n < TABCAP` with its own counter and matches NEITHER. It is out of contract by the English of `required[2]` and by nothing a token test decides, which is the same class as the polarity and rung-scope readings the shared paragraph below already records under WHAT NO GREP SETTLES. Both controls are measured (../NOTES.md 8b), and what they price is exactly *what the proof buys over the bound*. WHY `probes < TABCAP` IS FORBIDDEN: an exec-side probe counter is the other way to satisfy Verus's `decreases`, and it is the one that would make the proof CIRCULAR WITH THE FIX -- the loop would be bounded in the object code and the termination measure would be proving something the loop no longer needed proved. verus.rs carries a GHOST unwrapped cursor and a GHOST witness for an EMPTY slot instead, so R4 and R5 stay byte-identical at O3 and the exec code gains nothing. WHY `#[verifier::exec_allows_no_decreases_clause]` IS FORBIDDEN: it is Verus's own opt-out from the termination obligation, printed in the error text when the clause is missing, and it is the one edit that would let R5 ship p22's bug. Forbidding it is what makes *only R5 catches it* a statement about this tree rather than about Verus's defaults. WHY THE HASH IS SPELLED `* 2654435761 / 16777216 % TABCAP` AND NEVER `* 2654435761 >> 24 & 63`: the two are the same function on unsigned values and lower to the same instructions, but only the first is linear arithmetic, so verus.rs carries no `by (bit_vector)` anywhere (.memory/04-verus.md). The same reason puts `256 *` in the header decode rather than `<< 8`. WHY THE TABLE IS A FIXED-CAPACITY ARRAY AND `HashMap` IS FORBIDDEN: p22 is about the probe loop, and a library hash table would move the whole question inside std -- where the load-factor invariant is maintained by code no rung wrote and no rung can omit. WHAT IS DELIBERATELY NOT PINNED is how the WINDOW and the TABLE are ADDRESSED -- R2 indexes both, R3 reslices the window once and iterates the keys, R4 and R5 use `get_unchecked` on both -- because that is the SAFETY axis and it is the axis the R3-side span is measured along (../NOTES.md 8). It is also why the insert, the EMPTY test and the probe loop's own condition are described in prose in the entries below rather than backticked on the Rust side: those three spellings are exactly where the safety axis lives, and a backtick there would pin the axis flat. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p22-hash-probe.json`, contract `09eea1c6f8ee`.

`39` backticked spelling(s) over `6` rung(s) → **116** (spelling, rung) pair(s), **64** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 0 hit(s)** of 15 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
- **required — 0 spelling(s) pin nothing**, 2 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - absent — `if (k != SLB_P22_EMPTY && nfill < SLB_P22_TABCAP) {` (required[0], c, **c/kernel.c**)
  - absent — `if (k != SLB_P22_EMPTY) {` (required[0], c, **c/kernel_hardened.c**)
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
| c-gcc | 91 | 87 | 0 | 325 | 68,930,994 | 567,678,454 | 300,056 | 300,056 | `6a1a6c88` | `6a1a6c88` | yes | xmm |
| c-clang | 72 | 69 | 1 | 248 | 75,207,304 | 637,055,864 | 280,059 | 280,059 | `7f179f87` | `c3af84b6` | yes | xmm |
| safe_naive | 109 | 107 | 1 | 415 | 93,487,304 | 780,775,864 | 280,275 | 280,275 | `d086bd6a` | `2f2f13bc` | yes | xmm |
| safe_tuned | 74 | 72 | 9 | 263 | 88,027,304 | 739,475,864 | 280,275 | 280,275 | `caf7701f` | `507f2352` | yes | xmm |
| unsafe | 76 | 74 | 6 | 250 | 87,987,304 | 739,435,864 | 280,275 | 280,275 | `4ac4bd13` | `68e9470b` | yes | xmm |
| verus | 76 | 74 | 6 | 250 | 87,987,304 | 739,435,864 | 260,274 | 260,274 | `4ac4bd13` | `68e9470b` | yes | xmm |
| c-gcc-h | 93 | 89 | 0 | 325 | 71,490,994 | 588,158,454 | 300,056 | 300,056 | `5e245909` | `5e245909` | yes | xmm |
| c-clang-h | 77 | 74 | 1 | 264 | 88,007,304 | 739,455,864 | 280,059 | 280,059 | `4cfb2c89` | `f8b56052` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 146 | 145 | 0 | 626 | 153,374,480 | - | 720,066 | - | `4304c217` | `4304c217` | yes | - |
| c-clang | 122 | 122 | 1 | 600 | 162,403,100 | - | 420,056 | - | `5f7b4137` | `bfd6f8ed` | yes | - |
| safe_naive | 203 | 203 | 3 | 1,037 | 182,162,972 | - | 500,077 | - | `57df75ca` | `4b2e2dcc` | yes | - |
| safe_tuned | 226 | 226 | 15 | 1,153 | 152,182,972 | - | 500,077 | - | `153e20bf` | `d1ec198c` | yes | - |
| unsafe | 154 | 154 | 13 | 803 | 174,422,972 | - | 500,077 | - | `723b5bff` | `5c98eb3b` | yes | - |
| verus | 154 | 154 | 13 | 803 | 174,422,972 | - | 500,056 | - | `321de4af` | `841315c7` | yes | - |
| c-gcc-h | 148 | 147 | 0 | 640 | 158,494,480 | - | 720,066 | - | `5da3d501` | `5da3d501` | yes | - |
| c-clang-h | 124 | 124 | 2 | 611 | 167,523,100 | - | 420,056 | - | `39234e29` | `d1c96cdb` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 299 | 295 | 1 | 1,178 | - | - | 71,331,125 | 587,998,585 | `3ba7e87a` | `dedd1cfc` | yes | xmm |
| c-clang | 289 | 284 | 0 | 1,125 | - | - | 75,917,420 | 637,936,044 | `66477555` | `66477555` | yes | xmm |
| safe_naive | 745 | 736 | 1 | 3,439 | - | - | 93,507,590 | 780,796,150 | `f0d7f874` | `534755a0` | yes | xmm |
| safe_tuned | 704 | 696 | 1 | 3,071 | - | - | 88,207,581 | 739,656,141 | `5d97076d` | `ef154903` | yes | xmm |
| unsafe | 702 | 694 | 1 | 3,119 | - | - | 88,087,586 | 739,536,146 | `f057d7f7` | `7de817a1` | yes | xmm |
| verus | 699 | 692 | 1 | 3,055 | - | - | 88,087,579 | 739,536,139 | `2f32fd0b` | `c6a11297` | yes | xmm |
| c-gcc-h | 302 | 297 | 1 | 1,194 | - | - | 73,911,125 | 608,498,585 | `5e572005` | `7949f211` | yes | xmm |
| c-clang-h | 291 | 288 | 0 | 1,122 | - | - | 88,087,484 | 739,536,044 | `0a758472` | `0a758472` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 153,374,480 | - | 720,066 | - | `4bf81479` | `4bf81479` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 153,041,571 | - | 420,055 | - | `7e826a0a` | `7e826a0a` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 182,162,972 | - | 500,077 | - | `224f92b1` | `7107e7f8` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 152,182,972 | - | 500,077 | - | `ee6f493c` | `1f298058` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 174,422,972 | - | 500,077 | - | `28c8111a` | `2bcc4e9b` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 174,422,972 | - | 500,056 | - | `fc8a90fb` | `cc35e4c8` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 158,494,480 | - | 720,066 | - | `d026c6bc` | `d026c6bc` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 158,161,571 | - | 420,055 | - | `7e826a0a` | `7e826a0a` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 154/154 vs 154/154 | 13 B vs 13 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 76/74 vs 76/74 | 6 B vs 6 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 113.69 | 114.78 | 1.0% | 11.42 | 12.09 | 5.9% |
| c-gcc | whole | 112.65 | 114.99 | 2.1% | 11.91 | 12.18 | 2.3% |
| c-clang | isolated | 124.31 | 127.88 | 2.9% | 15.79 | 16.19 | 2.5% |
| c-clang | whole | 126.44 | 131.35 | 3.9% | 16.55 | 16.87 | 2.0% |
| safe_naive | isolated | 130.11 | 133.65 | 2.7% | 16.42 | 16.70 | 1.7% |
| safe_naive | whole | 132.48 | 135.61 | 2.4% | 16.39 | 16.92 | 3.3% |
| safe_tuned | isolated | 123.17 | 126.48 | 2.7% | 15.46 | 16.03 | 3.7% |
| safe_tuned | whole | 129.77 | 134.04 | 3.3% | 16.02 | 16.36 | 2.1% |
| unsafe | isolated | 127.71 | 130.44 | 2.1% | 12.86 | 13.64 | 6.0% |
| unsafe | whole | 131.64 | 135.38 | 2.8% | 16.28 | 17.03 | 4.6% |
| verus | isolated | 127.52 | 130.27 | 2.2% | 13.37 | 13.64 | 2.0% |
| verus | whole | 131.53 | 134.76 | 2.5% | 17.00 | 17.27 | 1.6% |
| c-gcc-h | isolated | 109.74 | 112.84 | 2.8% | 11.25 | 11.68 | 3.8% |
| c-gcc-h | whole | 114.96 | 116.85 | 1.6% | 14.06 | 14.60 | 3.8% |
| c-clang-h | isolated | 136.41 | 139.87 | 2.5% | 17.26 | 17.75 | 2.8% |
| c-clang-h | whole | 125.97 | 129.09 | 2.5% | 15.86 | 16.30 | 2.8% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 6 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `degenerate.bin`
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `degenerate.bin`
- `O0 / whole` on `large.bin`
- `O3 / isolated` on `degenerate.bin`
- `O3 / whole` on `degenerate.bin`
