# ph45 — `int cache`: a heap pointer in a field too narrow to hold it

**PHP 5.0.0, `ext/mbstring/libmbfl/mbfl/mbfl_convert.h:49` with
`ext/mbstring/libmbfl/filters/mbfilter_htmlent.c:161`, `:169`, `:178`, `:183`,
`:249`, corpus row CRASH-123 / V5C-123, bug #30573, tier `narrowed`.**
`filter->cache` is an `int`; the HTML-ENTITIES decode filter stores its 17-byte
heap work buffer in it, reads it back through `(char*)` — which sign-extends —
dereferences it ten times and frees it.

⚠⚠ **The defect is not input-conditioned.** `:167`'s `if (filter->cache)`
rejects only zero, so `:169`'s free runs on every filter destruction for any
input at all — 60 SIGSEGVs in 60 runs on `"hello, world"`. **So this row's
placed arena (`c/arena.h`) exists to make the BENIGN case work, not the
adversarial one**, which is the opposite of what a forcing mechanism usually
does. Read `c/arena.h`'s header before anything else here.

⚠⚠ **On the measured placement R1 and R1h are bit-identical**, because
`(char*)(int)p == p` exactly below 2³². The published `u64` therefore carries no
evidence that the defect exists — that is `check.py` stage 7h being satisfied,
and it is `ph64`'s lesson arriving on a second row. The evidence is in
`inputs/adversarial-*.bin` and `controls/`; `NOTES.md` §5 and §9.

⭐⭐ **And the ladder result contradicts the brief this row was built from.**
Safe Rust *can* store a truncated pointer in an `i32` — `(&x[0] as *const u8) as
i32` compiles with zero diagnostics where the same C emits four. What it cannot
do is dereference the result. `NOTES.md` §10.

The machine-readable contract follows.
`harness-php/gate.py ph45-htmlent-cache-int` enforces it; `README.md` is the
reader's entry point and `NOTES.md` carries the measurements.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len",
    "16 <= len",
    "len <= 268435456"
  ],
  "ensures": [
    "result == html_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (html_fold). ⚠⚠ `model.py`'s `html_fold` IS NOT `verus.rs`'s, AND THAT IS THE POINT: verus.rs defines it as the composition of a MEMORY MODEL -- `s_dec` steps a 17-byte buffer reached by an index through a `Seq<u8>` arena, exactly as the exec code does -- while model.py defines it as a STREAM DECODER with no buffer, no address, no allocator and no `status`, tokenising each filter's byte stream with a one-pass scanner. ⭐ model.py's stream decoder CANNOT EXPRESS THE DEFECT, because a stream decoder has no shared buffer to alias, which is exactly why it is a useful second opinion and is also a small statement of this row's ladder result. model.py's OTHER implementation, `_simulate`, is the memory model again in Python, driven at BOTH C rungs; `selfcheck()` drives the two against each other over 604 SYNTHETIC windows spanning every placement x every destruction order x a token grammar that reaches all nine arms of `mbfl_filt_conv_html_dec`, plus MUST-FIRE negatives requiring that each non-zero placement separate R1 from R1h on at least one window (measured: 126 windows each). THE SECOND HALF IS NOT OPTIONAL (PROTOCOL_PHP.md A2a rule 2): ph03 shipped for a whole task with its two implementations computing different functions, because its corpus took one arm of a two-armed branch and `inputs/` is not a domain. ⚠⚠ AND VERUS'S `tbl()` IS UNINTERPRETED WHERE model.py's table is CONCRETE: the proof holds for any 251-entry table and the contents are pinned by `controls/entity_table.py` -- all six shipped copies, byte for byte against the tarball, with a must-fire negative -- and by stage 2, which makes every rung agree on a u64 that depends on the table.",
  "idiom": {
    "required": [
      {
        "c": "`(int)mbfl_malloc` at mbfilter_htmlent.c:161 -- THE TRUNCATING STORE, obligation O1 of the corpus invariant pointer-value-integrity. ⚠ IT IS PINNED PRESENT IN c/kernel.c AND IT IS ABSENT FROM c/kernel_hardened.c BY DESIGN: removing that cast is the whole of e8901dc17087, so the hardened rung MUST NOT match this entry. The polarity and the set of rungs live in this English, which is what the named-spelling standard says about scope; c/kernel.h is a declaration header and matches no code spelling at all. ⚠ The Rust key pins a DIFFERENT expression on purpose: the C stores an ADDRESS and the four Rust rungs store an INDEX, so no single expression is common to all six. What IS common is that the value goes into a 32-bit signed field through a narrowing cast written at the store site.",
        "rust": "`idx as i32`"
      },
      {
        "c": "`(char*)filter->cache` -- mbfilter_htmlent.c:178 and :249, the two SIGN-EXTENDING read-backs, obligation O2. Same polarity as the entry above: present in c/kernel.c, absent from c/kernel_hardened.c, which reads through a void pointer instead.",
        "rust": "`f.cache as usize`"
      },
      {
        "c": "`mbfl_free((void*)filter->cache)` -- mbfilter_htmlent.c:169, the WILD FREE, obligation O3. Same polarity again.",
        "rust": "`ctx.free(f.cache)`"
      },
      "R1h is e8901dc17087 WHOLE AND UNMODIFIED -- a void-pointer member added to struct _mbfl_convert_filter and every decode-half use of the int field moved onto it -- and diff c/kernel.c c/kernel_hardened.c is that commit and only that commit, modulo the header and the comments that name it. FIVE of the commit's six mbfilter_htmlent.c rewrites are in this row's scope (161, 167, 169, 178, 249); the sixth, 148 in the encode half's flush, is in a half of the file this row MUST NOT lift, because line 123's tmp + sizeof(tmp) is a SEPARATE, UNCATALOGUED stack OOB write fixed in the same release window by a DIFFERENT commit nobody has identified (NOTES.md section 12). ⚠⚠ THE SUBJECT LINE IS NOT EVIDENCE ABOUT WHAT THE COMMIT DOES: it calls this a compiler-warning fix and the patch CHANGES THE STORAGE. ⭐ And there is no warning-fix-versus-real-fix distinction to draw here at all, because the warning and the memory-safety defect are the SAME EVENT -- gcc's pointer-to-int and int-to-pointer cast warnings fire at exactly the four sites the patch rewrites, four on R1 and zero on R1h, measured by controls/warnings.py in all eight cells of both compilers. ⚠ R2-R5 implement NEITHER rung's spelling of the fix, because none of them needs one: see the why. NO BACKTICKED SPELLING IN THIS ENTRY, deliberately -- it is a statement about which ALGORITHM each rung implements and no single token decides it.",
      "the WINDOW LAYOUT is two u32 head words followed by stride-8 text bytes; the text is fed ALTERNATELY, even indices to filter A and odd to filter B; and the first head word is A PLATFORM PARAMETER AND NOT ATTACKER DATA. No PHP input chooses where emalloc puts a block. It lives in the window because the harness gives a row exactly one channel and the row has to be able to say this is 2004 and this is 2026 about the same kernel. inputs/gen.py re-decodes what it emitted and asserts that every one of the 2 082 measured windows selects the low region, and refuses a corpus that misses any of the nine arms of the decode filter. NO BACKTICKED SPELLING: the C reads the head words with one helper and the Rust rungs with another, which is one fact in two spellings."
    ],
    "forbidden": [
      "e8901dc17087's added member, the pointer-typed home for the work buffer. It belongs in c/kernel_hardened.c and NOWHERE ELSE: a c/kernel.c that acquired it would be R1h wearing R1's name and would delete the row's primary span, and a RUST rung that acquired it would be measuring a different program from the one the C rungs measure -- none of the four needs it, because what makes the C unsafe is the SIZE OF THE VALUE and not the shape of the code. ⚠⚠ NO BACKTICKED SPELLING IN THIS ENTRY, AND IT IS FORCED RATHER THAN CHOSEN: harness/check.py::spelling_matches decides one spelling against EVERY rung of a language, so a backtick here would refuse c/kernel_hardened.c for containing its own fix -- and the gate did exactly that on this row's second run, which is how the shape of this entry was settled. The SCOPE lives in this English and a reviewer settles it with one grep, which is what the named-spelling standard says about the things no grep settles.",
      {
        "c": "`intptr_t` -- and uintptr_t, ptrdiff_t or any other pointer-width type in the FIELD's declaration. Widening it removes the defect WITHOUT being e8901dc17087, which is what upstream deliberately did not do: the field is still an int in master, because 26 other filters use it as a genuine integer accumulator. A rung that widened it would answer a question nobody asked. ⚠ ONLY THE ONE TOKEN IS BACKTICKED and the rest are named in prose, because size_t and int are everywhere in this row's C for unrelated reasons and pinning them absent would refuse every rung -- which is what the second gate run reported, six times.",
        "rust": "`i64` -- widening the cache field. The row is about a field that cannot represent every value put in it; a rung that made it wide enough would have no obligation to discharge and R5's wf_ptr would be vacuous. u64 and usize are NOT pinned here for the same reason the C entry pins only one token: both are everywhere in these rungs for unrelated reasons."
      },
      "`memcpy`, `memmove` and `copy_within` over the work buffer, on any rung. The filter writes its 17-byte buffer ONE BYTE AT A TIME, at an index derived from the filter's status field, and that is the row's whole exposure: a bulk copy has ONE bound to check where the shipped code has eleven, and it would also make the two filters' interleaved writes invisible to the aliasing oracle. ⭐ All three tokens are absent from all six rungs, which is what makes them safe to pin -- checked by grep before they were written here rather than after the gate said so."
    ],
    "why": "ph45 is PHP 5.0.0's HTML-ENTITIES decode filter, corpus row CRASH-123 / V5C-123, bug #30573, tier `narrowed`. THE IDIOM IS A HEAP POINTER STORED IN A FIELD THAT IS NARROWER THAN A POINTER. `ext/mbstring/libmbfl/mbfl/mbfl_convert.h:49` declares `int cache;` -- 32 bits -- and `ext/mbstring/libmbfl/filters/mbfilter_htmlent.c:161` stores a heap pointer in it: `filter->cache = (int)mbfl_malloc(html_enc_buffer_size+1);`. `:178` and `:249` read it back through `(char*)`, which SIGN EXTENDS, and `:169` hands it to the deallocator. ⚠ THE CATALOGUE SAYS FIVE LINES AND TWO FUNCTIONS; IT IS FIFTEEN TARBALL LINES ACROSS FOUR -- the declaration, the store, the free, TWO casts back and TEN dereferences (`:183 :189 :190 :193 :202 :215 :216 :223 :230 :236 :253`), in the ctor, the dtor, `mbfl_filt_conv_html_dec` and `mbfl_filt_conv_html_dec_flush`. `:249` is cited by NOBODY -- not `index.csv`, not `CATALOGUE.md`, not `ADJUDICATION_001.md` -- and it is one of the four sites the fix rewrites, so a row built to the catalogue's five lines would not be a faithful pre-image for its own R1h. ⚠⚠ AND THE DEFECT IS NOT INPUT-CONDITIONED. `:167`'s `if (filter->cache)` rejects only the value zero, so `:169`'s free runs on EVERY filter destruction whether or not the input contains an `&`: on a 2026 PIE heap that is 60 SIGSEGVs in 60 runs on the string `\"hello, world\"` (`TASK_PHP_034_REPORT` §5.4, measured, 40 of 40 `emalloc(17)` results above 2^32). ⚠⚠⚠ SO THE ROW'S PLACED ARENA EXISTS TO MAKE THE BENIGN CASE WORK, NOT THE ADVERSARIAL ONE, and that is the opposite of what a forcing mechanism usually does. `c/arena.h` maps two regions, `LO` under `MAP_32BIT` and `HI = LO + 2^32` under `MAP_FIXED_NOREPLACE`, once, from `main.c`, outside the measured loop; `place` -- the window's first head word -- says which region each of the two filters' work buffers comes from. ⭐ `LO` IS NOT A CONVENIENCE, IT IS 2004: a non-PIE `php` binary's `brk` heap sat below 2^32, `(char*)(int)p == p` EXACTLY, no implementation-defined conversion is even exercised, UBSan is silent, and that is precisely why this shipped and was reported as a COMPILER WARNING. `small.bin` and `large.bin` are that platform and `inputs/gen.py` asserts every one of their 2 082 windows carries `place == 0`; the other placements are in `adversarial-*.bin`, where `check.py` stage 4 records per-rung behaviour instead of requiring agreement. ⚠⚠ THE CONSEQUENCE FOR THE MEASURED NUMBER, STATED RATHER THAN LEFT TO BE NOTICED: on `LO` THE TRUNCATION IS THE IDENTITY, so R1 and R1h are BIT-IDENTICAL on every measured window and the published `u64` carries no evidence whatever that the defect exists. That is `check.py` stage 7h's requirement being SATISFIED, it is the catalogue's proposed oracle (`decoded bytes + (allocs, frees)`) measuring NOTHING, and it is `ph64`'s lesson arriving on a second row -- which is now twice and is worth saying out loud. The evidence lives in `inputs/adversarial-*.bin` and in `controls/`. ⭐⭐ AND THE ORACLE THAT DOES MEASURE IS NON-FATAL, DETERMINISTIC AND SILENT UNDER EVERY DETECTOR. Two filters whose work buffers are exactly 2^32 apart are ONE BUFFER under truncation: on `adversarial-alias.bin` filter A decodes `&amp;` to **65** where R1h gives **38**, because filter B's `&#65;` overwrote A's buffer index 1 with `#` and `:190`'s `buffer[1]=='#'` then selected the NUMERIC arm of a NAMED entity. `&amp;` decodes to `A`. No crash, no sanitizer diagnostic, no allocator damage -- a silent wrong answer delivered to the wrong converter, which is what a wild write into another live allocation actually costs. The frees move with it (one double free, one leak) and `adversarial-hi-both.bin` isolates the other half: both buffers in `HI`, the truncation shadows them onto `LO` INJECTIVELY, the decode is CORRECT and only the deallocator is wrong -- two frees of addresses the arena never issued. ⚠ `adversarial-noalias.bin` is the must-NOT-fire control beside it, byte for byte the same text and the same interleaving with `place == 0`, and every rung agrees there; without it the divergence could be the interleaving rather than the aliasing and nothing in the number would say which. ⚠⚠⚠ THE LADDER RESULT, AND IT CONTRADICTS THE BRIEF THIS ROW WAS BUILT FROM. `TASK_PHP_036.md` §1 and `TASK_PHP_034_REPORT` §6.8 both state that *\"safe Rust cannot store a pointer in an `i32` at all\"*. MEASURED FALSE on rustc 1.97.1: `(&x[0] as *const u8) as i32` is ordinary SAFE code, it truncates, and it compiles with ZERO diagnostics even under `-D warnings` -- where the same C emits FOUR, one `-Wpointer-to-int-cast` and three `-Wint-to-pointer-cast`, at exactly the four sites `e8901dc17087` rewrites. O1 is expressible in safe Rust and the compiler says LESS about it than C's does. ⭐⭐ WHAT SAFE RUST REFUSES IS O2, AND ONLY O2: `*(t as usize as *const u8)` is `error[E0133]`, and there is no safe expression that gets from an integer to a reference. So the immunity is on the DEREFERENCE side, the faithful safe port is forced to OWN its memory, and the value it stores in `cache` becomes an INDEX -- which round-trips through `i32` exactly, for any arena a program that owns its arena can have. All four Rust rungs therefore carry R1's OWN IDIOM and not R1h's: `cache` is an `i32`, the store is `idx as i32`, the read-back is `cache as usize` with its sign extension, `void *opaque` appears in no Rust rung, and none of it is unsafe. ⚠ The arena's five counters are written out in every rung and the `n_dfree` / `n_wfree` / leak arms are UNREACHABLE in all four -- that is the finding written as an arm that cannot be taken, not dead code. ⚠⚠ AND VERUS IS THE THIRD ANSWER: `(idx as i32) as usize == idx` VERIFIES under `idx < 0x8000_0000` and FAILS without it, with `recommendation not met: value may be out of range of the target type` at BOTH cast sites (`controls/o1_roundtrip.rs`). gcc warns, rustc is silent, Verus refuses -- three toolchains, three answers, on one five-line idiom, and that is the type axis's first real result. NOTES.md §10 and §11. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "html_fold": "html_fold",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 41
    },
    "twin_obligations": {
      "verus.rs": 43
    },
    "obligations_note": "41 verified / 0 errors in ~3 s at the DEFAULT rlimit for every item but `run`, and 43 under `--cfg slb_twin` -- TWO trusted accessors, therefore two twins, plus `ent_table`, which cannot have one. ⚠⚠ WHAT IS PROVED HERE IS THE CORPUS INVARIANT ITSELF, AND CRASH-123 IS THE ONLY ONE OF THE CORPUS'S 166 CASES WITH ITS OWN. `pointer-value-integrity` O1 -- *a pointer must not be stored into an integer field narrower than a pointer* -- is `alloc`'s third `ensures` (`r == 0 || (0 < r && r + BLOCK <= ASZ)`), and O2 -- *a value read back out of such a field must not be dereferenced without re-establishing that it designates the original object* -- is `wf_ptr`, which is what discharges `bget`/`bset`'s `i < ASZ` at all eleven dereference sites. O3 is NOT a memory-safety obligation in this representation -- freeing a wrong index is a wrong ANSWER, not a wrong ACCESS -- so it lives entirely in the value postcondition, via `s_free_n`'s ledger. ⚠⚠⚠ AND THE VACUITY IS MEASURED, WITH FIVE MUTANTS, AND ONE OF THEM DID NOT FIRE: V1 (kernel body -> `0u64`) fails `postcondition not satisfied`, V3 (`bset`'s `ensures` names only the written slot) fails, V4 (`wf_c`'s `bump[r] <= REGION` deleted) fails `possible arithmetic underflow/overflow`, V5 (`wf_ptr` weakened to `0 <= cache`) fails with three unmet preconditions -- and V2, which deletes `alloc`'s O1 `ensures`, STILL VERIFIES 41/0, because `r == s_alloc_r(g, n)` plus `wf_c` already pin the range. That clause is REDUNDANT and is kept because it is the only place O1 is legible as O1; what carries it is `wf_c`'s bump bound. NOTES.md section 11 and `.temp/php36/logs-04-vacuity.log`. ⚠ The value postcondition is discharged by a REMAINING-COMPUTATION invariant over `s_feed` -- `s_feed(g_entry, fa_entry, fb_entry, win, HEAD, len) == s_feed(ctx.g(), fa, fb, win, i, len)` -- which is ph64's lockstep-ghost-mirror shape and the only one that closes at `i == len` without a separate append lemma.",
    "twin_obligations_note": "`verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 41 shipped + 2 for `slb_twin_bget` and `slb_twin_bset`, whose bodies are `v[i]` and `v[i] = x` with the IDENTICAL contract -- so the two `external_body` items' `requires` and `ensures` are CHECKED against a safe implementation rather than asserted. ⚠ `ent_table` has NO twin and cannot: a safe body cannot prove `r@ == tbl()` about an uninterpreted function, and that is what makes the uninterpretation cheap -- the axiom says only that SOME table equals `tbl()`, which is satisfiable and constrains nothing. ⭐ THERE IS EXACTLY ONE `#[verifier::rlimit]` IN THIS FILE, on `run`, and it is 60. `kernel` is split from `run` and `run_spec` is `#[verifier::opaque]` for the reason ph64's own note records: with the whole composition inline, Z3 unfolds `run_spec` into `kernel`'s one-line postcondition, unfolds four recursive spec functions inside it once each by default fuel, and then matches that term tree against the same tree with differently-spelled arguments. Opaque and split, the match is two arguments and the file verifies in ~3 s.",
    "items": {
      "verus.rs": {
        "ent_table": {
          "external": "verifier::external_body",
          "requires": [],
          "ensures": [
            "r@ == tbl()"
          ]
        },
        "mix": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "sx": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_is_ec": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_emit": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_alloc_g": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_alloc_r": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_free_n": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_live_n": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_name_eq": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_lookup": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_num": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_flush_n": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_flush": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_dec": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_feed": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_dtor": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_init": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_rd32": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "run_spec": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "html_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "g": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "wf_c": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "wf_ptr": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "wf_f": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "bget": {
          "external": "verifier::external_body",
          "requires": [
            "i < ASZ"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_bget": {
          "external": null,
          "requires": [
            "i < ASZ"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "bset": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_bset": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "rd32": {
          "external": null,
          "requires": [
            "i + 4 <= w@.len()"
          ],
          "ensures": [
            "r == s_rd32(w@, i as int)"
          ]
        },
        "is_entity_char": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == s_is_ec(c)"
          ]
        },
        "new": {
          "external": null,
          "requires": [],
          "ensures": [
            "r.g() == s_init()",
            "wf_c(r)"
          ]
        },
        "alloc": {
          "external": null,
          "requires": [
            "wf_c(*old(self))"
          ],
          "ensures": [
            "final(self).g() == s_alloc_g(old(self).g(), n)",
            "r == s_alloc_r(old(self).g(), n)",
            "r == 0 || (0 < r && r + BLOCK <= ASZ)",
            "wf_c(*final(self))"
          ]
        },
        "free": {
          "external": null,
          "requires": [
            "wf_c(*old(self))"
          ],
          "ensures": [
            "final(self).g() == s_free_n(old(self).g(), p, 0)",
            "wf_c(*final(self))"
          ]
        },
        "live": {
          "external": null,
          "requires": [
            "wf_c(*self)"
          ],
          "ensures": [
            "r == s_live_n(self.g(), 0, 0)"
          ]
        },
        "emit": {
          "external": null,
          "requires": [],
          "ensures": [
            "final(self).g() == s_emit(old(self).g(), c)"
          ]
        },
        "dec_ctor": {
          "external": null,
          "requires": [
            "wf_c(*old(ctx))",
            "region < 2"
          ],
          "ensures": [
            "final(ctx).g() == s_alloc_g((G { region, ..old(ctx).g() }), REQ)",
            "final(f).cache == s_alloc_r((G { region, ..old(ctx).g() }), REQ)",
            "final(f).status == 0",
            "final(f).cache == 0 || (0 < final(f).cache && final(f).cache + BLOCK <= ASZ)",
            "wf_c(*final(ctx))"
          ]
        },
        "dec_dtor": {
          "external": null,
          "requires": [
            "wf_c(*old(ctx))"
          ],
          "ensures": [
            "final(ctx).g() == s_dtor(old(ctx).g(), *old(f))",
            "wf_c(*final(ctx))"
          ]
        },
        "name_eq": {
          "external": null,
          "requires": [
            "wf_c(*ctx)",
            "buffer + BLOCK <= ASZ"
          ],
          "ensures": [
            "r == s_name_eq(ctx.arena@, buffer as int, name@)"
          ]
        },
        "dec_flush": {
          "external": null,
          "requires": [
            "wf_c(*old(ctx))",
            "wf_ptr(*old(f))",
            "0 <= old(f).status <= HTML_ENC_BUFFER_SIZE - 1"
          ],
          "ensures": [
            "(final(ctx).g(), *final(f)) == s_flush(old(ctx).g(), *old(f))",
            "wf_c(*final(ctx))",
            "final(f).cache == old(f).cache",
            "final(f).status == 0"
          ]
        },
        "dec": {
          "external": null,
          "requires": [
            "wf_c(*old(ctx))",
            "wf_f(*old(f))",
            "0 <= c < 256"
          ],
          "ensures": [
            "(final(ctx).g(), *final(f)) == s_dec(old(ctx).g(), *old(f), c)",
            "wf_c(*final(ctx))",
            "wf_f(*final(f))"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()",
            "16 <= len",
            "len <= 268435456"
          ],
          "ensures": [
            "r == html_fold(buf@, off as int, len as int)"
          ]
        },
        "run": {
          "external": null,
          "requires": [
            "win@.len() == len",
            "16 <= len",
            "len <= 268435456"
          ],
          "ensures": [
            "r == run_spec(win@, len as int)"
          ]
        },
        "load_input": {
          "external": "verifier::external_body",
          "requires": [],
          "ensures": []
        },
        "emit_result": {
          "external": "verifier::external_body",
          "requires": [],
          "ensures": []
        },
        "main": {
          "external": null,
          "requires": [],
          "ensures": []
        }
      }
    },
    "twin_justifications": {
      "verus.rs": {
        "ent_table": "⚠⚠ THERE IS NO TWIN AND THERE CANNOT BE, AND THE REASON IS THE SAME FACT THAT MAKES THIS ITEM CHEAP. Its `ensures` is `r@ == tbl()` where `tbl()` is an UNINTERPRETED spec function (`verus.axioms`), so NOTHING is known about `tbl()` except what this item says. A `#[cfg(slb_twin)] fn slb_twin_ent_table` with a checked body would have to PROVE `r@ == tbl()` about a function with no definition, which no body can do -- this is a fact about the SHAPE of the abstraction, not about this row's spelling of it. ⭐ WHAT REPLACES THE TWIN, and it is stronger than a twin would be for this particular item: the twin's job is to check that the contract is strong enough to license the unchecked operation, and THERE IS NO UNCHECKED OPERATION HERE. The body is `&[ ...251 literals... ]`, a reference to a 'static array, defined for every input with no precondition to discharge. What the item really needs checking is that the CONTENTS are PHP's, and no Verus configuration can check that at all: `controls/entity_table.py` does it -- all six shipped copies against `html_entities.c:37-290` byte for byte, with a must-fire negative that rejects one bumped code in 6 of 6 -- and so does `check.py` stage 2, which makes every rung agree on a u64 that depends on the table. NOTES.md's `SLB-TRUSTED-ARGUMENT verus.rs ent_table` section carries the (a)/(b)/(c) argument."
      }
    },
    "axioms": {
      "verus.rs": [
        "tbl"
      ]
    },
    "axioms_note": "ONE body-less trusted declaration: `pub uninterp spec fn tbl() -> Seq<Ent>;`. ⚠⚠ AN AXIOM IS NOT A TRUSTED ITEM AND THE GATE IS RIGHT TO COUNT IT SEPARATELY -- Verus does not prove it, it adds no verified function so the obligation count does not move, it emits no instructions so `identity` does not move, and it carries no `#[verifier::external_body]` so the TCB tally above does not move either. ⭐ WHAT MAKES THIS ONE CHEAP IS THAT IT IS UNINTERPRETED AND CARRIES NO CLAUSES AT ALL: `tbl()` is a `Seq<Ent>` about which NOTHING is asserted, so no `requires` can be weakened and no `ensures` can be false. The only thing that mentions it is `ent_table`'s `ensures r@ == tbl()`, which says *some* table equals it -- satisfiable, and constraining nothing. ⚠ THE PRICE IS REAL AND IT IS NAMED: the proof holds for ANY 251-entity table, so Verus is not what says the SHIPPED table is PHP's. `controls/entity_table.py` is -- all six shipped copies, byte for byte against `html_entities.c:37-290`, with a must-fire negative that rejects a single bumped code in 6 of 6 -- and so is `check.py` stage 2, which makes every rung agree on a u64 that depends on the table's contents. NOTES.md section 11 carries the TCB tally and the demonstration.",
    "unsafe_justifications": {
      "verus.rs": {
        "ent_table": "⚠ NO `requires`, DELIBERATELY, AND THE GATE ASKS FOR THIS LINE BECAUSE A TRUSTED ITEM WITHOUT ONE IS AN AXIOM THAT ITS OPERATION IS ALWAYS DEFINED. Here the operation is `&[ ...251 literals... ]` -- constructing a reference to a `'static` array of `Ent` -- and it is defined unconditionally, for every input, with no caller obligation to discharge. There is nothing a `requires` could say. ⭐ AND THE `ensures` IS THE WEAKEST ONE THAT IS USEFUL: `r@ == tbl()`, where `tbl()` is UNINTERPRETED (see `axioms_note`), so this item asserts only that the table the exec code walks is the one the spec functions talk about. It asserts NOTHING about the contents, which is why the proof holds for any table and why the contents are pinned by `controls/entity_table.py` and by the gate's own cross-rung checksum instead. ⚠ IT HAS NO TWIN AND CANNOT: a safe body cannot prove `r@ == tbl()` about an uninterpreted function, which is the same fact from the other side.",
        "bget": "`v.get_unchecked(i)` is defined only while `i < ASZ`, and vstd ships no spec for it -- grepped `~/tools/verus/vstd/std_specs/slice.rs`, which has `index`, `index_mut`, `split_at`, `copy_from_slice` and `copy_within` and no `get_unchecked`, and `~/tools/verus/vstd/array.rs`, which has `array_index_get` and no unchecked form. ⭐ WHAT DISCHARGES THE PRECONDITION IS THE ROW'S OWN INVARIANT: `i` is `f.cache as usize + k` with `k <= 15`, and `wf_ptr(f)` -- `0 < f.cache && f.cache + BLOCK <= ASZ` -- is obligation O2 of the corpus's `pointer-value-integrity`, word for word. In C nothing establishes it; here it must be proved at every call. `slb_twin_bget` is the safe body with the same contract.",
        "bset": "`x: u8` is a PURE VALUE and needs no precondition: all 256 inhabitants are a legal store into a byte `[0u8; ASZ]` already initialised, so the precondition is about `i` alone. ⚠⚠ WHAT THE CONTRACT MUST NOT LEAVE OUT, AND THIS IS THE ROW WHERE IT BITES: the arena holds BOTH filters' work buffers, so an `ensures` naming only `v@[i] == x` would license a body that also moved the OTHER filter's buffer -- which is precisely the defect R1 has. The shipped `ensures` is the whole post-state, `old(v)@.update(i, x)`, and mutant V3 measures that the weaker one does not verify. Miri is the backstop for the class regardless (`miri` below)."
      }
    }
  },
  "driver": {
    "statements": 12,
    "c_source": "c/main.c",
    "regions": [
      "safe_naive.rs",
      "safe_tuned.rs",
      "unsafe.rs",
      "verus.rs",
      "c/main.c"
    ],
    "aliases": {
      "c": {
        "n_body": "bytes.len()",
        "bytes": "bytes.as_slice()",
        "inp.n_iters": "n_iters"
      }
    },
    "canonical": [
      "n_blob = bytes . len ( ) ;",
      "buf = bytes . as_slice ( ) ;",
      "acc = 0 ;",
      "if stride_w >= 16 && stride_w <= 268435456 && stride_w <= n_blob",
      "{",
      "stride = stride_w ;",
      "nwin = n_blob / stride ;",
      "it = 0 ;",
      "while it < n_iters",
      "{",
      "k = acc * nwin >> 64 ;",
      "r = kernel ( buf , k * stride , stride ) ;",
      "acc = acc * 31 + r ;",
      "it = it + 1 ;",
      "}",
      "}"
    ]
  },
  "collapse": {
    "probe_inputs": [
      "small.bin",
      "large.bin"
    ],
    "probe_iters": [
      100,
      200
    ],
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary so the one-shot loader terms cancel. They do NOT cancel exactly -- see p01's copy of this note for the environment-block and build-to-build residuals, measured at ~0.1 and ~0.2 Ir respectively. ph45's two probe shapes have different work per call (560 and 4 086 window bytes) so check.py can also assert d(Ir)/d(work) >= ALPHA. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call. ⚠ `work_per_call` is the WINDOW, and on this row that really is the unit of work: the kernel feeds EVERY byte past the two head words to a filter, one at a time, so `ntext = stride - 8` on every call of every input and nothing the attacker writes changes the count. What the attacker DOES change is the cost per byte -- a `;` that closes a named entity walks up to 251 table entries where an ordinary byte does not -- so the marginal is not a flat rate; NOTES.md section 8 decomposes it. The one-shot `mmap` pair in `ph45_arena_init()` is outside the loop and cancels in the difference, which is why it is in `main.c` and not in the kernel."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "differ",
      "O3": "differ",
      "why": "⚠⚠ R4 AND R5 DIFFER AT BOTH LEVELS, AND THE PIN IS `differ` BECAUSE THAT IS WHAT WAS MEASURED. results-php/ph45-htmlent-cache-int.json, O3/isolated, the `kernel` symbol: **313 instructions / 1 433 bytes for `unsafe` against 311 / 1 417 for `verus`**, so `md5_fn` and `md5_fn_norel` both differ and no `norel` claim is available. At O0 they differ for the ordinary reason -- nothing is inlined, so R5's two trusted accessors and its `run` helper survive as real calls where R4 open-codes them. ⚠⚠ AND THE PIN COMPARES A SYMBOL THAT HOLDS ONE TENTH OF THE WORK, WHICH IS WORTH KNOWING BEFORE READING IT: `check_identity` looks at `kernel`, and on this row `dec` is a SEPARATE symbol carrying ~90 % of every rung's instructions (it is `#[cfg_attr(slb_isolated, inline(never))]` in all four Rust rungs on purpose -- see `unsafe.rs`). Disassembled and compared directly, `unsafe::dec` is **282** instructions and `verus::dec` is **289** (`.temp/php36/dec.diff`). ⭐ AND THE RUN-TIME COST OF THE PROOF IS ZERO TO WITHIN A CODEGEN COIN FLIP: `kernel_exclusive_ir` on small.bin is 7 823 432 for R4 and 7 820 432 for R5, i.e. R5 is **3 000 Ir CHEAPER over 1 500 calls, -0.04 %**, and whole-program it is 82.19 M against 82.02 M, **+0.2 % dearer**. Neither is a result about verification; they are quoted here so that `differ` is not read as *the proof costs something*. NOTES.md section 8."
    }
  ],
  "miri": {
    "pair": [
      "unsafe",
      "verus"
    ],
    "sources": [
      "unsafe.rs"
    ],
    "required": true,
    "reason": ".memory/02-bench-rules.md makes Miri mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. ph45 has TWO and one of them WRITES (`bset`). ⚠⚠ It matters here for a reason specific to this row: the arena holds BOTH filters' work buffers, so an off-by-one in `bset`'s index is a write into the other filter's buffer -- the very defect R1 has -- and it would be invisible to the checksum on any window where the other filter's buffer is not read afterwards. Miri sees the write itself.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). check.py rewrites n_iters to 4 for every Miri run, so ph45's cost is 4 x (one window decoded through two filters), i.e. at worst 4 x 4 078 filter calls -- three orders of magnitude inside the 180 s budget. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  },
  "provenance": {
    "php_version": "5.0.0",
    "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
    "c_file": "ext/mbstring/libmbfl/filters/mbfilter_htmlent.c",
    "c_lines": [
      155,
      258
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/filters/mbfilter_htmlent.c | sed -n '155,258p'",
    "extract_sha256": "6aad722d2b6cf73ec987a7ced3bf590ac04821454eb52377edfcdf1c7acaf8b9",
    "extra_spans": [
      {
        "c_file": "ext/mbstring/libmbfl/mbfl/mbfl_convert.h",
        "c_lines": [
          40,
          54
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/mbfl/mbfl_convert.h | sed -n '40,54p'",
        "extract_sha256": "6586bd6948ccceaadfc63df7a1c4d5f123fdaeb3f7121cd9eddcff4a08fb3a0a",
        "why": "`struct _mbfl_convert_filter`, and ⚠⚠⚠ `:49 int cache;` IS THE DEFECT -- a 32-bit field holding a 64-bit pointer. ⭐ R1h's OTHER hunk lands HERE: e8901dc17087 adds `void *opaque;` after `:53` and LEAVES `int cache;` alone, because 26 other filters use it as a genuine integer accumulator and it is still an `int` in master. `TASK_PHP_022`'s open item 25 is that a row which does not cite the frame the fix goes in certifies a span containing neither the fix nor its frame; this row cites both frames. ⚠ The field is ONE LINE and 12 bytes, so it is cited as the whole struct rather than as a span of its own -- a `[49,49]` span would score ~0 on overlap and would say nothing about the field's OFFSET, which is half of what makes it a pointer-sized hole."
      },
      {
        "c_file": "ext/mbstring/libmbfl/filters/html_entities.h",
        "c_lines": [
          33,
          36
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/filters/html_entities.h | sed -n '33,36p'",
        "extract_sha256": "3528826585f2667f5e7010b9c3a31380f243151bb70263e227a387e758f8ea01",
        "why": "`mbfl_html_entity_entry` -- `{char *name; int code;}`, what `:200-206` walks. Flattened into `c/mbfl__html_entities.h` (PROTOCOL_PHP.md B3 spelling 1)."
      },
      {
        "c_file": "ext/mbstring/libmbfl/filters/html_entities.c",
        "c_lines": [
          37,
          290
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/filters/html_entities.c | sed -n '37,290p'",
        "extract_sha256": "734afebb8f33375d1de03bf47b9882ccc062315994ef328e5ff74cf1e4d66afb",
        "why": "`mbfl_html_entity_list` -- 251 entities plus the `{NULL,-1}` terminator. STATIC DATA, not input: the named-entity arm at `:202` is dead without it, and `&amp;` decoding to 38 rather than to 65 is the row's oracle. ⚠⚠ IT IS 254 OF THE ROW'S 477 CITED LINES AND IT IS THE CHEAP HALF -- `const` data with no control flow -- so the kernel-overlap number this provenance block reports is dominated by a table, and NOTES.md section 7 says what to think of that. GENERATED into all six shipped copies by `controls/entity_table.py`, which checks them byte for byte against these bytes with a must-fire negative; the longest name is EIGHT characters and that measurement is what bounds `strcmp`'s read of the work buffer."
      },
      {
        "c_file": "ext/mbstring/libmbfl/mbfl/mbfl_allocators.h",
        "c_lines": [
          36,
          54
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/mbfl/mbfl_allocators.h | sed -n '36,54p'",
        "extract_sha256": "289b5ecc8a164bffb67de188503ec4b04bf289e4726505056fd043227ed04fa0",
        "why": "⭐⭐ `mbfl_malloc` AND `mbfl_free` ARE `#define`s OVER A FUNCTION-POINTER TABLE (`:48`, `:51`), not functions. This is the span that makes the row's central divergence a REBINDING of the same table PHP itself rebinds at `mbstring.c:764`, rather than an edit to any extracted line: `c/arena.h` lifts `:36-44` verbatim, declares `__mbfl_allocators`, and points its `malloc`/`free` entries at the placed arena. The other five entries are NULL and unreachable from the decode path."
      },
      {
        "c_file": "ext/mbstring/mbstring.c",
        "c_lines": [
          240,
          283
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/mbstring.c | sed -n '240,283p'",
        "extract_sha256": "dff1cfd53b12bf788c1c153305bbc988bc65da4ab231d827cee865be39e7c273",
        "why": "`_php_mb_allocators` -- `malloc`->`emalloc`, `free`->`efree`, and the five others. **Why `common-php/emalloc_shim.h` is the right allocator for this row** (PROTOCOL_PHP.md B), and why the filter STRUCT comes from it even though the 17-byte work buffer comes from the arena."
      },
      {
        "c_file": "ext/mbstring/mbstring.c",
        "c_lines": [
          762,
          765
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/mbstring.c | sed -n '762,765p'",
        "extract_sha256": "2c7752b17cbb4466cfe41ed307a43482325e6a722e580720e3d2ee6f9a8a0485",
        "why": "`PHP_MINIT_FUNCTION(mbstring)`: `__mbfl_allocators = &_php_mb_allocators;` at `:764` -- where the binding actually happens, and the line `ph45_arena_init()` plays the part of."
      },
      {
        "c_file": "ext/mbstring/libmbfl/mbfl/mbfl_convert.c",
        "c_lines": [
          216,
          256
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/mbfl/mbfl_convert.c | sed -n '216,256p'",
        "extract_sha256": "b208a9247d05506b6610405031e79808d1d9a11404cd20b9e9dc10d7691e10ff",
        "why": "`mbfl_convert_filter_new` -- allocates the filter STRUCT with `mbfl_malloc` at `:226` and calls the ctor at `:255`. NARROWED: the `mbfl_no2encoding` lookup and `mbfl_convert_filter_reset_vtbl` come off, and the struct allocation goes to `php_shim_emalloc` so the row's placement projection is confined to the one allocation the defect reads."
      },
      {
        "c_file": "ext/mbstring/libmbfl/mbfl/mbfl_convert.c",
        "c_lines": [
          259,
          266
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/mbfl/mbfl_convert.c | sed -n '259,266p'",
        "extract_sha256": "79461e635638b0aa94f5c87147b930ae3e1bd3d1c715fa994a05a12732881886",
        "why": "`mbfl_convert_filter_delete` -- calls the dtor, i.e. reaches `:169`'s wild free, and then frees the struct."
      },
      {
        "c_file": "ext/mbstring/libmbfl/mbfl/mbfilter.c",
        "c_lines": [
          243,
          271
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/mbfl/mbfilter.c | sed -n '243,271p'",
        "extract_sha256": "7192691a09af5e1f54749e5933696e1c521c657386b9b2ea45a7e83ae1cedd7c",
        "why": "⭐ `mbfl_buffer_converter_feed` -- and its body `while (n > 0) { (*filter_function)(*p++, filter); n--; }` at `:262-267` IS the kernel's feed loop, one byte at a time with no look-ahead and no length handed to the filter. The `mbfl_memory_device_realloc` at `:255` and the `mbfl_filter_output_pipe` output function are PROJECTED to the fold."
      },
      {
        "c_file": "ext/mbstring/libmbfl/filters/mbfilter_htmlent.c",
        "c_lines": [
          85,
          91
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/filters/mbfilter_htmlent.c | sed -n '85,91p'",
        "extract_sha256": "de7bc3bc60a06877c07870aa273ac3f6677b50f6f63f73e728b9e7ee7e461998",
        "why": "`vtbl_html_wchar` -- the vtable wiring ctor, dtor, filter and flush together. It is a COMPILE-TIME CONSTANT for the one conversion this kernel performs, which is what licenses deleting `mbfl_convert_filter_reset_vtbl`'s dispatch."
      },
      {
        "c_file": "ext/mbstring/libmbfl/mbfl/mbfl_convert.c",
        "c_lines": [
          299,
          317
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/mbfl/mbfl_convert.c | sed -n '299,317p'",
        "extract_sha256": "b710d7ed81ad1bbd8af2f4bf53885199f1629bdee458c43810e70740a034aa3c",
        "why": "`mbfl_convert_filter_copy` -- `:312` copies `dist->cache = src->cache`, which before the fix ALIASES one heap work buffer into two filters, each of which frees it in its own dtor. ⚠ The row CITES it and does not PRICE it: `TASK_PHP_034_REPORT` §4.3 reads the double free at source and §8.4 says in terms that it is an INFERENCE and was not measured. It is here because e8901dc17087 removes it as a consequence -- `opaque` is simply not copied -- which makes the fix LARGER than the catalogued defect, and a row that cited only the four rewritten sites would not show that."
      }
    ],
    "extra_spans_note": "ELEVEN SPANS ACROSS SEVEN FILES, AND THE PRIMARY IS THE WHOLE DECODE HALF RATHER THAN THE CITED LINE. .memory-php/01-extraction.md F1: `provenance.c_file`/`c_lines` name the DEFECT site and the other frames go in the notes. Here the CSV's `c_file_line` is `mbfilter_htmlent.c:161` -- the STORE -- and the defect is the FIELD, `mbfl_convert.h:49`, which is `extra_spans[0]` because a one-line 12-byte span would score ~0 on overlap and would say nothing about the field's offset. ⚠ The primary is `[155,258]` and not `[158,172]`: the row lifts all four decode functions and both constants, and `:249` -- one of the four sites the fix rewrites -- is inside it and is cited by nobody. ⛔ `mbfilter_htmlent.c:99-150`, the ENCODE half, is DELIBERATELY NOT CITED AND NOT LIFTED: `:123`'s `int *p = tmp + sizeof(tmp)` is a separate, uncatalogued stack OOB write 192 `int`s past the end of an `int tmp[64]`, fixed in the same release window by a DIFFERENT commit nobody has identified, and lifting it would put a second memory-safety defect inside a row whose contract names one. NOTES.md section 12. Each entry is checked exactly as the primary is (in the manifest, in range, canonical extract_cmd, extract_sha256 over the bytes `sed` prints) and the kernel overlap is computed over the UNION -- which is why that number is dominated by a 254-line data table and why NOTES.md section 7 reads it rather than quoting it.",
    "tier": "narrowed",
    "divergences": [
      {
        "what": "mbfl_malloc / mbfl_free's TABLE ENTRIES -> a PLACED arena for the 17-byte work buffer",
        "kind": "projection",
        "where": "mbfl_allocators.h:48,:51; mbstring.c:764; mbfilter_htmlent.c:161,:169",
        "why": "⚠⚠⚠ THE ROW'S MOST IMPORTANT DIVERGENCE, AND ITS `why` CANNOT END IN \"NO SEMANTICS\" -- the address the allocator returns IS the mechanism. Upstream the target is a FUNCTION-POINTER TABLE ENTRY (`mbfl_allocators.h:36-44`) that PHP itself rebinds at `mbstring.c:764`; `c/arena.h` rebinds the same entry a third time, at an allocator whose returned address the row chooses. WHY: with glibc's address the R1 rung SIGSEGVs in `mbfl_filt_conv_html_dec_dtor` on EVERY input including `\"hello, world\"` -- 60 runs of 60, measured at `TASK_PHP_034_REPORT` §5.4 -- so there is no benign corpus, `check.py` stage 2's checksum agreement can never be reached, and the row cannot be measured at all. WHAT IT IS DEMONSTRATED TO PRESERVE, per PROTOCOL_PHP.md A1 clause (c) rather than asserted: at `place == 0` the mapping is `MAP_32BIT`, so `(char*)(int)p == p` EXACTLY, the implementation-defined conversion is the IDENTITY, UBSan is silent, and R1 and R1h are BIT-IDENTICAL on all 2 082 measured windows and on every one of 604 synthetic ones (`model.py::selfcheck`). ⚠⚠ TWO ALTERNATIVES WERE MEASURED AND BOTH ARE REJECTED, so nobody re-tries them: backing `common-php/emalloc_shim.h` itself from a placed arena would be MORE faithful and would STALE EVERY PHP ROW (the shim is in every row's gate and measurement digest, PROTOCOL_PHP.md B2), and building `-no-pie` is impossible because `harness/build.py` is frozen and passes no such flag. ⚠ THE TIER QUESTION THIS RAISES IS ANSWERED IN `divergences_note` AND THE ANSWER IS ARGUED, NOT ASSUMED."
      },
      {
        "what": "ph45_pl_free RECYCLES NOTHING and counts four outcomes instead",
        "kind": "projection",
        "where": "zend_alloc.c:248-289 via mbfl_allocators.h:51",
        "why": "PHP's `_efree` reads a block header at `ptr - 24` and links the block into `AG(cache)[real_size>>3]`, so on a truncated pointer it is a wild WRITE into whatever is at that address -- which is the fault the row cannot measure. `c/arena.h` projects it to four COUNTERS (`n_free`, `n_dfree`, `n_wfree`, and the leak) folded into the kernel's u64, which is how obligation O3 reaches the CHECKSUM the gate compares across rungs rather than only a sanitizer. ⚠ The counting is OBSERVATION and changes no control flow: `pl_free` does the same thing -- nothing -- whichever arm it counts. What the projection removes is `efree`'s RECYCLING, and the row does not model a use-after-free. `controls/fatal.c` builds the faithful spelling and records the SIGSEGV."
      },
      {
        "what": "the other five mbfl_allocators entries are NULL",
        "kind": "deletion",
        "where": "mbfl_allocators.h:38-43",
        "why": "`realloc`, `calloc`, `pmalloc`, `prealloc` and `pfree` are unreachable from the HTML-ENTITIES decode path -- measured by reading `[155,258]`, which calls exactly `mbfl_malloc` once and `mbfl_free` once. No semantics."
      },
      {
        "what": "the filter STRUCT comes from php_shim_emalloc, not from mbfl_malloc",
        "kind": "substitution",
        "where": "mbfl_convert.c:226, :265",
        "why": "`mbfl_convert_filter_new` really does `mbfl_malloc(sizeof(mbfl_convert_filter))` upstream, and `common-php/emalloc_shim.h` IS PHP 5.0.0's own `_emalloc`/`_efree`, line-cited to the same tarball -- so this is a redirection to the SAME code and not a substitution of a different allocator. What it buys is that the row's placement projection is confined to the one allocation the defect reads, and that `uses_allocator: true` is about a real allocation. No semantics."
      },
      {
        "what": "mbfl_convert_filter_reset_vtbl's dispatch",
        "kind": "deletion",
        "where": "mbfl_convert.c:252",
        "why": "the kernel is compiled for ONE conversion, `HTML-ENTITIES -> wchar`, whose vtbl is the compile-time constant `vtbl_html_wchar` (`mbfilter_htmlent.c:85-91`). The four function pointers are assigned directly from that constant and the indirect calls through `filter->filter_function` / `filter_flush` / `filter_ctor` / `filter_dtor` are KEPT. No semantics."
      },
      {
        "what": "mbfl_no2encoding and the from/to lookup",
        "kind": "deletion",
        "where": "mbfl_convert.c:232-239",
        "why": "`from` and `to` are never read on the decode path. All 13 struct members are kept and `mbfl_encoding` is forward-declared, so the STRUCT is unchanged and `int cache;` sits exactly where 5.0.0 puts it -- which is the one thing about the struct that matters. No semantics."
      },
      {
        "what": "mbfl_buffer_converter_feed's memory device and output pipe",
        "kind": "projection",
        "where": "mbfilter.c:255, :263",
        "why": "`mbfl_memory_device_realloc` and `mbfl_filter_output_pipe` are replaced by the fold, which is where every emitted wchar goes. The FEED LOOP at `:262-267` is kept verbatim. No semantics on the extracted domain: the row measures what the filter emitted and in what order, which is what the device would have held."
      },
      {
        "what": "the three commented-out php_error_docref calls",
        "kind": "deletion",
        "where": "mbfilter_htmlent.c:197,:212,:217,:231",
        "why": "ⓘ NOTHING IS DELETED -- they are ALREADY comments in 5.0.0, at all four lines, and the kernel carries them as comments too. The entry exists so a reviewer does not go looking for a removal that never happened. No semantics."
      },
      {
        "what": "TSRMLS_DC / TSRMLS_CC",
        "kind": "deletion",
        "where": "mbfilter_htmlent.c:197 and the mbstring.c frames",
        "why": "thread plumbing, no semantics"
      },
      {
        "what": "strchr(html_entity_chars, c) -> a RANGE PREDICATE in the four Rust rungs",
        "kind": "substitution",
        "where": "mbfilter_htmlent.c:225",
        "why": "The C keeps `strchr` verbatim; the Rust rungs spell the same predicate arithmetically, because a proof cannot read a `&'static [u8]` constant's contents and a 63-byte scan in spec mode would need the constant to be uninterpreted. ⚠⚠ IT IS DEMONSTRATED OVER THE WHOLE DOMAIN, NOT ASSERTED: `controls/strchr_equiv.c` drives ALL 256 byte values against the real `strchr` -- 0 disagreements -- with a MUST-FIRE negative that disagrees exactly once. ⭐ And the must-fire case is the point: `strchr(s, 0)` returns the TERMINATOR, which is non-NULL, so PHP treats a NUL byte inside an entity body as a LEGAL entity character. Every rung reproduces that; a port that spelled the predicate as \"is in this string\" would compute a different function from the C on any window containing a zero byte, and no shipped window has one, which is exactly how it would have survived. No semantics."
      },
      {
        "what": "strcmp's bound -> an explicit `name.len() + 2 <= REQ` guard in the four Rust rungs",
        "kind": "substitution",
        "where": "mbfilter_htmlent.c:202",
        "why": "`strcmp(buffer+1, entity->name)` gets its bound from the two NUL terminators, so it reads at most `strlen(name)+1` bytes of the work buffer. A proof cannot use a bound an argument merely happens to have, so every Rust rung states it. IT IS NEVER TAKEN: the longest name in `html_entities.c:37-290` is EIGHT characters, measured over the whole table by `controls/entity_table.py`, and `REQ` is 17. No semantics."
      },
      {
        "what": "the numeric accumulate is written in u32 in the four Rust rungs",
        "kind": "substitution",
        "where": "mbfilter_htmlent.c:193",
        "why": "`ent = ent*10 + (buffer[pos] - '0')` is `int` arithmetic, and `html_entity_chars` admits LETTERS, so `&#abcdefghijkl;` reaches ~7.4e12 and the C SIGNED-OVERFLOWS -- a second, uncatalogued defect in the same function (NOTES.md section 12). Rust has no undefined behaviour to reproduce, so the rungs write the two's-complement wrap explicitly: `(ent as u32).wrapping_mul(10).wrapping_add((d - 0x30) as u32) as i32`, which is bit-identical to what gcc and clang emit for the C. ⚠ `inputs/gen.py` refuses a corpus whose largest `|ent|` comes within 100x of `INT_MAX` on EITHER rung, so no shipped number is taken over that path at all. No semantics on the measured domain."
      },
      {
        "what": "the four Rust rungs store an INDEX in `cache`, and their two arena regions are 256 bytes apart rather than 2^32",
        "kind": "projection",
        "where": "mbfl_convert.h:49; mbfilter_htmlent.c:161,:178,:249; c/arena.h",
        "why": "⚠⚠ THE ONE DIVERGENCE THE ROW IS ABOUT, DECLARED RATHER THAN LEFT TO BE NOTICED. Safe Rust has no expression that turns an integer into a place -- `*(t as usize as *const u8)` is `error[E0133]` -- so the faithful safe port OWNS its arena and stores an OFFSET into it. The narrowing store and the sign-extending read-back are written exactly as the C writes them, in a field of exactly the same width; what changes is the VALUE, and an offset into a 512-byte array round-trips through `i32` for the same reason an address does not. ⭐ The 2^32 gap has no counterpart because an arena index space of 2^32 entries cannot exist in a program that owns its arena -- which is the row's ladder result stated as an arithmetic fact rather than as a check. ⚠ The consequence is that the four Rust rungs agree with R1h at EVERY placement and diverge from R1 wherever R1 truncates, and the arena ledger's `n_dfree` / `n_wfree` / leak arms are present in all four and unreachable in all four. NO semantics on the measured domain -- `place == 0` makes the C's own map the identity, so all six rungs compute one function there -- and a large finding about the ladder, which NOTES.md section 10 states."
      },
      {
        "what": "the four Rust rungs reproduce php_shim_ag's three COUNT fields arithmetically instead of linking the shim",
        "kind": "substitution",
        "where": "common-php/emalloc_shim.h:346-435, :225-238",
        "why": "`harness/build.py` compiles exactly three C translation units and no Rust rung links C. Each Rust rung folds the same constant `(2, 2, 0)` the C folds, because both C rungs make exactly two `php_shim_emalloc(sizeof(mbfl_convert_filter))` calls and two `php_shim_efree` calls per kernel call and neither size is cacheable. This pins the ALLOCATION SEQUENCE across rungs and is NOT evidence that any Rust rung ran PHP's allocator. No semantics."
      },
      {
        "what": "php_shim_tally()'s `bytes_mallocked` field is NOT folded into the u64",
        "kind": "projection",
        "where": "common-php/emalloc_shim.h:642-648",
        "why": "⚠⚠ PROTOCOL_PHP.md B1 RULE 2 SAYS FOLD `php_shim_tally()`, WHICH MIXES FOUR FIELDS, AND THIS ROW FOLDS THREE. The fourth is a property of `sizeof(mbfl_convert_filter)` -- and e8901dc17087 LEGITIMATELY GROWS that struct by 8 bytes, 88 to 96, when it adds `void *opaque;`. Folding it would make R1h differ from R1 on EVERY benign input for a reason that has nothing to do with the defect, and `check.py` stage 7h would refuse the row -- CORRECTLY. ⭐ A gate stage that refuses your row is a hypothesis about your row (.memory-php/02-ladder.md) and the hypothesis is right: a u64 that moves with `sizeof` is not measuring this defect. The row's allocator oracle is `c/arena.h`'s five counters, which are about the 17-byte WORK BUFFER -- the one allocation the defect reads -- and they ARE in the checksum. The 88-versus-96 measurement is NOTES.md section 8; it is a genuine cost of the upstream fix and the row REPORTS it rather than burying it in a number nobody can decompose."
      }
    ],
    "divergences_note": "`kind` is one of deletion / substitution / projection and is DECLARED, NEVER DETECTED -- provenance.py does not read this block at all (PROTOCOL_PHP.md D). Nothing may come to depend on it. ⚠⚠⚠ TWO OF THESE FIFTEEN ENTRIES HAVE A `why` THAT DOES NOT END IN \"NO SEMANTICS\", AND THE TIER QUESTION THEY RAISE IS ARGUED HERE RATHER THAN SMOOTHED OVER. They are the placed arena and `pl_free`'s projection. PROTOCOL_PHP.md A1 clause (b) is why the row is NOT `verbatim`: the substitution redirects `mbfl_malloc` at an allocator whose RETURNED ADDRESS the row chooses, and the returned address IS the mechanism, so no honest `why` can say it has no semantics. THE ARGUMENT FOR `narrowed` RATHER THAN `modelled`, so it can be attacked: (1) `modelled` means *the mechanism is re-expressed because the original cannot be lifted*, and the mechanism -- `(int)mbfl_malloc(...)`, `(char*)filter->cache`, `mbfl_free((void*)filter->cache)` -- IS lifted, character for character, along with all four decode functions at `[155,258]`; what is substituted is the allocator BEHIND it, and upstream that is a TABLE ENTRY which PHP itself rebinds at `mbstring.c:764`. (2) `narrowed` means *a wrapper comes off and the body is unchanged*, and two do: `mbfl_buffer_converter_feed`'s memory device and `mbfl_convert_filter_new`'s vtable dispatch. (3) The substitution is DEMONSTRATED behaviour-preserving on the measured domain rather than asserted, which is A1 clause (c): at `place == 0` the conversion is the IDENTITY and R1 equals R1h bit for bit on 2 082 measured and 604 synthetic windows. (4) ph64 already ships `narrowed` with one divergence whose `why` does not end in \"no semantics\" and says so in this same field, so this is the second row of that shape rather than a new liberty. ⚠⚠ WHAT WOULD MAKE IT `modelled`, stated because a reviewer should weigh it: the window's `place` word has NO PRE-IMAGE IN PHP AT ALL -- no input chooses where `emalloc` puts a block -- so R1's behaviour at `place != 0` is not PHP's behaviour on any input, it is PHP's behaviour on a DIFFERENT PLATFORM. The counter-argument is that the measured corpus is entirely `place == 0`, which is the platform the code was written for and shipped on, and that the other placements are `adversarial-*.bin`, where the gate RECORDS rather than requires. ⚠ A TIER IS A COST, NEVER A FILTER: if a reviewer reads (4) as precedent-stretching, the row is `modelled` and everything else about it stands.",
    "root_cause_ids": [
      "heap-pointer-stored-in-an-int-field-truncated-cast-back-dereferenced-and-freed"
    ],
    "cwe": "CWE-787",
    "cwe_note": "index.csv records `memory-corruption` / `wild-pointer-deref` / CWE-787 for CRASH-123, with `asan_kind` a SEGV WRITE at `mbfilter_htmlent.c:183`, and `TASK_PHP_034_REPORT` §5.5 reproduced exactly that -- same signal, same access type, same function, same line -- with the FAITHFUL allocator. `controls/fatal.c` is that build and it is where this row's PROTOCOL_PHP.md A4 evidence lives. ⚠⚠ THE MEASURED RUNGS FIRE NO SANITIZER ON ANY INPUT AND THAT IS A FINDING RATHER THAN A GAP. The defect is a TYPE error and the address it produces is a legitimately mapped page of the row's own arena: ASan does not track `mmap`, and UBSan has nothing to say because `(int)ptr` and `(char*)i` are IMPLEMENTATION-DEFINED (C99 6.3.2.3p5/p6) rather than undefined -- what is undefined is the DEREFERENCE, and no sanitizer has a check for it. ⭐ So on this row the detectors are silent and the CHECKSUM is the only observer, which is why the arena's five counters are folded into it (PROTOCOL_PHP.md B1 rule 2). NOTES.md section 9.",
    "fix_commit": "e8901dc17087",
    "fix_commit_note": "⭐ ONE COMMIT, TWO FILES, AND A BACKPORT THAT COSTS NOTHING. `e8901dc17087075645dc867a9b6d7d534673482b` -- Moriyoshi Koizumi <moriyoshi@php.net>, Mon 21 Feb 2005 10:12:43 +0000, \"- Fix bug #30573 (compiler warning due to invalid type cast)\". 2 files, 8 insertions, 7 deletions: `void *opaque;` added to `struct _mbfl_convert_filter` and six `filter->cache` uses moved onto it. `patch -p1 --dry-run` on the PRISTINE 5.0.0 tarball: rc=0, NO FUZZ, NO OFFSET -- the commit's pre-image IS 5.0.0, which is cleaner than ph07's, which took `fuzz 1`. Patch bytes at `controls/e8901dc17087.patch` so the citation survives without network. ⚠⚠ THE SUBJECT LINE IS NOT EVIDENCE ABOUT WHAT THE COMMIT DOES: it calls this a compiler-warning fix and the patch CHANGES THE STORAGE -- it is not a cast at the use site and it silences nothing. ⭐ AND THERE IS NO \"WARNING FIX VERSUS REAL FIX\" DISTINCTION TO DRAW HERE AT ALL, WHICH IS THE SHARPER READING: `-Wpointer-to-int-cast` and `-Wint-to-pointer-cast` fire at exactly the four sites the patch rewrites, FOUR on `c/kernel.c` and ZERO on `c/kernel_hardened.c` under `harness/build.py`'s own `-Wall -Wextra` (measured, `controls/warnings.py`), so the compiler warning and the memory-safety defect are the SAME EVENT and bug #30573 is the defect's own bug number. ⚠ `int cache;` STAYS: the commit does not touch `mbfl_convert.h:49`, because 26 other filters use `cache` as a genuine integer accumulator and it is still an `int` in master. ⭐ THE TAG BRACKET IS A DERIVATION AND NOT A SELECTION: the guard is ABSENT at php-5.0.0/.1/.2/.3 and PRESENT at php-5.0.4 and at every tag through master, 21 years, never reverted, with only `mbfl_malloc` -> `emalloc` since; the commit's date sits inside that window; and the php-5.0.3 -> php-5.0.4 diff of both files IS this commit's hunks plus exactly ONE unrelated line, which is the ENCODE half's `tmp + sizeof(tmp)` -> `tmp + sizeof(tmp)/sizeof(tmp[0])` and is NAMED here because the window is otherwise a one-candidate window and that is the second candidate in it. It cannot be this row's fix: it touches neither `cache` nor `opaque` nor any line the row cites. ⚠ ONE OF THE COMMIT'S SIX `mbfilter_htmlent.c` REWRITES IS OUT OF SCOPE -- `:148`, in the ENCODE half -- and the five in scope are all in `c/kernel_hardened.c`. ⚠⚠ IS THE FIX CORRECT AND COMPLETE? `TASK_PHP_034_REPORT` §4 attacked it on five fronts and it survived all five: it rewrites ALL FOUR sites a whole-tarball grep finds, `mbfilter_htmlent.c` is the ONLY file in the tarball that stores a pointer in `cache`, and it incidentally removes the `mbfl_convert_filter_copy` aliasing double free as well. That is a SIXTH data point and NOT a trend -- .memory-php/02-ladder.md records ph03 and ph07 as neither minimal nor sufficient, ph16 as complete and minimal, ph29 as closed by neither stage, ph64 as unfaultable, and says in terms \"there is no run and never was one\".",
    "invariant": "pointer-value-integrity",
    "obligation": "O1+O2+O3",
    "invariant_note": "⭐ THE ONLY ROW IN THE CORPUS'S 166 WITH ITS OWN INVARIANT, and the claim is ATTRIBUTED rather than repeated: the labels live in `paper/invariants-166.json`, not in `index.csv`, and over all 166 cases there are 20 distinct invariant ids of which exactly ONE is not of the form `I<n>` -- CRASH-123's `NEW:pointer-value-integrity` (`TASK_PHP_034_REPORT` §4.5). Its three obligations map ONE-TO-ONE onto three of the row's cited lines: O1 the store at `:161`, O2 the read-back-and-deref at `:178`/`:249`, O3 the free at `:169`. The same record lists `I1` -- *every read or write through a pointer lands strictly inside the allocation that pointer was derived from* -- as `role: contributing`.",
    "echoes": [
      "p38"
    ],
    "echoes_note": "p38-alias-pun is the closest PAT analogue -- a value reinterpreted through a type that cannot represent it. PLAN_PHP.md 3.1 makes the overlap a CROSS-REFERENCE and never a filter. ⚠ Not re-derived in this task: `echoes: [\"p38\"]` is the catalogue's and is carried forward.",
    "uses_allocator": true,
    "uses_allocator_why": "c/kernel.c makes exactly two `php_shim_emalloc(sizeof(mbfl_convert_filter))` calls and two `php_shim_efree` calls per kernel call, for `mbfl_convert.c:226`'s filter-struct allocation and `:265`'s free. The truncations T1/T2/T3 do NOT fire -- both requests are 88 or 96 bytes -- and neither size is cacheable (`REAL_SIZE(88) >> 3 == 11 == MAX_CACHED_MEMORY`), so this row exercises the plain-`malloc` arm of emalloc_shim.h and none of the overflow half and none of the cache half. ⚠⚠ THE ALLOCATION THE DEFECT READS IS NOT THIS ONE. The 17-byte work buffer comes from `c/arena.h`, a PLACED arena, and that substitution is the row's central divergence; the shim serves the struct because `mbfl_convert.c:226` really does allocate it and because confining the placement to the work buffer is what keeps the projection as small as it can be. ⚠ The kernel folds the shim's three COUNT fields and NOT `bytes_mallocked`; see the `divergences` entry that says why and NOTES.md section 8."
  }
}
```
