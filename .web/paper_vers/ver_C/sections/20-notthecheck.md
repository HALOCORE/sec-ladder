\section{On three of ten, the bounds check is the biggest cost}
\label{sec:notthecheck}

%% ⚠⚠⚠ THE THIRD UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad3.md), 5/10.
%% The reader scored this file 6 and called its caveat "the worst-supported box in
%% the paper".  THE CLAMP EXAMPLE IS UNTOUCHED — they named it as the clearest
%% mechanical explanation in the document.  No number, row, verdict, bucket or
%% reclassification moved.  Four changes, three of them in the caveat:
%%  1. ⚠⚠ THE 15% IS CUT, AND IT IS A CREDIBILITY FIX.  The box read "both check
%%     programs quoted above hide a search, one worth about 15% of its gap and one
%%     worth 98%".  The 98% is checkable four paragraphs up (`+13,756` → `+263`);
%%     THE 15% APPEARED NOWHERE ELSE IN THE PAPER.  The reader: "In a document
%%     that is otherwise obsessive about showing both ends of everything (§3
%%     literally has a rule called 'Publish the pair'), the one unbacked number is
%%     inside the box that's confessing an oversight.  That's the wrong place for
%%     it."  They are right, and the number is worse than unbacked: §3's own cut
%%     record says the five-per-probe figure and the "about a sixth" it comes from
%%     have ZERO GREP HITS IN THE TREE and must be marked as OUR subtraction.
%%     ⚠ WHAT REPLACED IT IS STRONGER AND IS CHECKABLE: CLAIMS.md §1.22 records
%%     the tree's own statement that the binary search "carries a FOUR-SPELLING
%%     search", and E4 §A6(b) that the shipped spelling is JOINT-dearest, tied
%%     with `r3_getunwrap` (`p07/NOTES.md:888-896`) — which is why the prose says
%%     "among the dearest" and NOT "the dearest of four", a form E4 calls wrong.
%%     The absence of a published size is now stated as an absence, which is what
%%     the box is for.  ⚠ DO NOT RESTORE 15% WITHOUT §3's WORKED SUBTRACTION AND
%%     E4 §A6's THREE PRECISION REQUIREMENTS; the number cannot ship alone.
%%     ⚠ BOTH SEARCHED CHECK ROWS ARE STILL NAMED, which is the second bias
%%     review §4.3 requirement this box exists to satisfy.
%%  2. ⚠ THE BOX NO LONGER ARGUES FROM A COLUMN THE READER CANNOT SEE.  It opened
%%     "Six of the ten print `undeclared` for spelling search" — and no table in
%%     the paper prints that column.  The reader: "I'm being asked to reason about
%%     data I can't see."  Same six of ten, same denominator, described instead of
%%     named.  ⚠⚠ CLAIMS.md §1.22 IS DISCHARGED WORD FOR WORD IN SUBSTANCE: the
%%     prose still says a blank means NOBODY WROTE AN ENTRY and that it has NEVER
%%     meant nobody searched, which is the tree's own verbatim correction.  A
%%     later editor restoring the word `undeclared` must restore that pair with it.
%%  3. ⚠⚠ "which makes three of ten a stronger result, not a weaker one" IS CUT.
%%     The reader flagged it as the one place the paper shapes a number: "being
%%     told which direction to read my own number, in the box that's supposed to be
%%     the section's admission against itself, is the one place the framing felt
%%     applied rather than earned."  ⚠ THE CENSUS FACT ITSELF IS UNTOUCHED —
%%     fourteen programs built with an out-of-range index, `SYNTHESIS.md:877-883`
%%     — and this box is still its only home, so C34 / bias review §3.7's evidence
%%     ships; what went is the sentence telling the reader which way to read it.
%%     ⚠ IF A LATER REVIEWER WANTS THE DIRECTION BACK, it belongs in §0's F2 as
%%     the census clause the final cut dropped, not in this box.
%%  4. `licenses` AND `license` AS VERBS ARE GONE (the reader's never-explained
%%     list: "I worked out roughly what it means from context but it's used as a
%%     technical term").  "so that licenses both compilers here" -> "so that lets
%%     us claim"; "does not license *safety is free here*" -> "does not let you
%%     say".  Neither claim changed.  ⚠ "fair to subtract" for "licensed for
%%     differencing" was already the plain-pass wording and is untouched.

%% ⚠⚠⚠ THE SECOND UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad2.md), 4/10.
%% No number, row, verdict, bucket or reclassification moved.  What changed:
%%  1. ⚠⚠ THE GLOSS BLOCK LOST `kernel` AND `pattern` AND `Ir`.  §0 defines
%%     `kernel` in its orientation paragraph and §1 re-glosses it once; those two
%%     are the paper's whole allowance.  This file's copy was the third of six in
%%     near-identical words, and the reader reported the repetition trained them
%%     to skip blocks that also carried new material — this file's block is
%%     immediately above the population sentence, which is new material.  `Ir` is
%%     glossed by this file's own table caption ("Instructions per call inside the
%%     kernel"), and `pattern` by §1's method paragraph; the prose says
%%     "programs" here now.  ⚠ DO NOT RESTORE THE BLOCK.
%%  2. ⚠⚠ THE POPULATION PARAGRAPH'S LAST SENTENCE IS SPLIT IN TWO.  This is the
%%     paragraph the reader STOPPED at — "I read the second sentence three times
%%     and I still cannot tell you what it says.  'That rule' — which rule?
%%     'those costs are out anyway' — out of what?"  Both fact-check corrections
%%     are intact: (a) the licence rule matches CALLS and not their COSTS, and
%%     (b) the hash probe's promotion to arm C is still disclosed in the sentence
%%     that states the ten.
%%  3. `clamp` IS GLOSSED in the example, which is the box the reader liked best
%%     in the paper and the one sentence in it they could not parse ("I don't know
%%     what a clamp is (never defined anywhere)").  The mechanism is stated the
%%     way they eventually reconstructed it.  `control` is glossed at its first
%%     use in the paper, three sentences later.
%%  4. `tree` IS GLOSSED at its first use in the paper, inside the tally
%%     paragraph, and §0 no longer uses the word at all.  The reader: "I don't
%%     know what 'our tree' is", of a sentence in the file that must stand alone.
%%  5. `axis` IS GONE from the caveat, replaced by what it means for these
%%     patterns.  It was the sentence the reader understood least in that box, and
%%     it is the sentence that makes three-of-ten the STRONGER result.
%%  6. ⚠ `row` IS NO LONGER USED FOR A PROGRAM-COMPARISON ANYWHERE IN THIS FILE.
%%     §1 now defines a row as one line of a printed table, once, for the whole
%%     report; the reader found three meanings and called it the worst single
%%     problem in the paper.  The caveat's title, the sweep, the magnitude
%%     paragraph and the figure caption all say "program" or "gap" instead.  The
%%     ⚠ marks and the table's own rows are still rows, which is the one sense
%%     left.  ⚠ "least-recorded" is still the rigour-B4 word and "least-searched"
%%     is still false.
%%  7. THE 98.6% / 99.2% PAIR SAYS IT IS ONE RESULT ON TWO INPUTS.  The reader
%%     read the two as a range or a before/after.  The admission is otherwise
%%     word for word what it was, and it is on their list of six sentences that
%%     bought the paper more trust than any number.

%% ⚠⚠ TITLE FIXED, rigour B4. It read "…and those three are the least-SEARCHED",
%% which is a search-state claim whose only evidence is the `undeclared` column —
%% and §3's caveat declares a sentence of exactly that shape, off exactly that
%% column, FALSE and bounding nothing. CLAIMS.md §1.22 is on §3's side. Worse,
%% this section's own instance refutes the old title: the binary search WAS
%% searched, and the search found the row inflated. "Least-recorded" is what the
%% column supports, and the caveat below now discharges the title instead of
%% undercutting it. §0's F3 took the same correction.
%%
%% ⚠⚠ TITLE SHORTENED AGAIN for the plain-language pass, and the second clause
%% MOVED, NOT DROPPED. It read "A bounds check is the dominant term on three of
%% ten large rows, and the numerator is the least-recorded part of the tally" —
%% 22 words, three of them jargon ("dominant term", "numerator", "tally"). The
%% least-recorded claim now lives where its evidence is, as the heading of the
%% caveat at the end of the section, which is what discharges it; the rigour-B4
%% wording is unchanged there. THE TITLE STILL MAY NOT SAY "least-searched".
%% ⚠ The brief's worked example, "On seven of ten, the bounds check is not the
%% cost", was REFUSED and must not be adopted: 7 = 5 something-else + 1
%% unattributed + 1 check-but-deletable, and on the unattributed row nothing in
%% the tree says what the cost is, while on the deletable row the cost IS the
%% check. The section's own tally forbids the sentence.

%% ══════════════════════════════════════════════════════════════════════════
%% ⚠⚠ THE TALLY IS 3 OF 10. IT IS NOT 2 OF 10. RULING C9, and C9 corrects the
%% plan outright — REWRITE_VERC_PLAN.md and ver_A/ver_B all say 2, and all
%% inherited it from `results/SYNTHESIS.md:287`, which explains an `R3−R4` row
%% with an `R2−R4` mechanism. A later agent WILL be tempted to "fix" this back.
%% Do not. The two defects that produced the old 2 are re-derived row by row in
%% `.temp/verc/E2-decomposition.md` §4.3 and §4.10, and I re-checked both
%% against the primary sources myself:
%%
%%   1. THE INDEX FLATTEN (p05) IS A CHECK ROW. `results/SYNTHESIS.md:287`
%%      gives it "a hoisted per-row trip count and a scalar epilogue", which is
%%      p05's R2−R4 mechanism. Its own `patterns/p05-index-flatten/NOTES.md:1897`
%%      says of the R3−R4 row: "The surviving five are the bounds check and
%%      nothing else." `NOTES.md:306-308`: R3−R4 is exactly `9 + 6·nrow`, "flat
%%      in `ncol`, flat in the residue" — so the scalar-epilogue term is PROVABLY
%%      ABSENT here. nrow = 19 / 65 → 123 / 399, of which 5·nrow = 95 / 325 =
%%      77.2% / 81.5% is the check. Read in the pattern's own NOTES, not a summary.
%%   2. THE FIELD SPLIT (p14) IS UNATTRIBUTED, not "something else".
%%      `results/SYNTHESIS.md:291` supports it with 6.456 → 3.506 `Ir`/line byte,
%%      and `patterns/p14-field-split/NOTES.md:1191` heads that very table
%%      "`R2 − R4` per call" — verified. No instruction-level R3−R4 attribution
%%      for the row exists anywhere in the tree (E2 searched both NOTES, both
%%      synthesis files and `.memory/`). Reporting it as unattributed is the
%%      honest bucket, and it is what makes the other nine credible.
%%
%% So: 3 check / 5 something else / 1 unattributed / 1 check-but-deletable.
%%
%% ⚠⚠ C29 IS SETTLED AND THE ROW STANDS — and it was settled by DERIVATION, not
%% by judgement, which is what C29 asked for. This note used to reach the right
%% conclusion by the weaker, statistical route ("0 of 288 triples moved").
%% Replaced with the construction, which closes it for good:
%% `synthesis/outward_ir.py:314-320` defines the flagged quantity as
%%     moves_by ≡ kernel_plus_callees − kernel_exclusive
%% so it is BY CONSTRUCTION the callee component of the pair difference and is
%% arithmetically independent of the kernel-exclusive column this section
%% differences. A non-zero flag there is a claim about callees; it cannot move
%% the bounded stack's 359 or 626, not by inference but by definition. The
%% fact-checker re-ran `calibrate_licence` after upstream moved again and got
%% 19 false-`LICENSED` rows, three of them on our `R3-R4` pair (p03 ×2 at −7.00,
%% p08 small at +0.0662), with the licensed population unchanged at 22 of 26.
%% ⚠ C29 itself was incomplete: TWO rows are false-`LICENSED` on our pair, not
%% one. Neither bites — p08's row is 26/26, nowhere near the 100 `Ir` cut.
%% ══════════════════════════════════════════════════════════════════════════

%% ⚠⚠⚠ THE UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad.md).  No number,
%% row, verdict or bucket moved.  What changed:
%%   * `kernel` DEFINED in the opening gloss block.  It was undefined in all nine
%%     files, is used twelve times in this one, and the cold reader read it as
%%     "operating system kernel" for the whole paper.
%%   * `residual` glossed where it is used, because §7's best line — "a residual
%%     of exactly zero is not a strong pass; it is the signature of a test that
%%     could not fail" — depends on the reader knowing what it is a residual OF,
%%     and §7 is protected from editing.  "13 pop densities" became "13 different
%%     rates of popping": the reader knew what a stack pop is and not what a pop
%%     DENSITY is.  Both figures and the zero-fitted-parameters clause stand.
%%   * "gcc shares no middle-end with rustc" -> "share no optimiser".  The reader
%%     did not know what a middle-end is; the licence claim is unchanged.
%%   * THE CAVEAT'S `prover` SENTENCE says what the prover is doing instead of
%%     naming it twice.  Same mechanism, same direction of bias.
%%   * the hash probe's cell says "a fresh sub-slice … does not take" rather than
%%     "a reslice": `reslice` is on the reader's never-explained list.
%% Beat 1 (S). Population derived, not asserted, with the counting rule in eye
%% range (convention 2.7) and the hash-routed re-gloss of rung/pattern/`Ir`
%% (convention 2.10.3). C4: name WHICH synthesis file, by full path, once.
%%
%% ⚠⚠ PLAIN-LANGUAGE PASS (.temp/brief/PLAIN.md), whole section. Every fact,
%% figure, reclassification and retraction is unchanged; the sentences are
%% shorter and the vocabulary is glossed at first use, because a reader lands
%% here by hash route. The substitutions a later editor must not undo:
%%   "licensed for differencing" -> "fair to subtract" (§0's F2 uses the same
%%       words; the RULE is still stated, and the licence caveat with it)
%%   "the numerator"             -> "the three check rows"
%%   "dominant term"             -> "the biggest cost" / "what the notes name"
%%   "unattributed"              -> "nothing in the tree says what the gap is"
%%   "trusted items"             -> "nothing the prover has to take on trust"
%%   `blob` and `contract`       -> glossed on first use (caption; beat 1)
%% ⚠⚠ THE CUT PASS (.temp/brief/CUT.md) then executed exactly that: the handle
%% table's decomposition is gone (~95 words) and the threshold sweep is two
%% sentences (~60). The file lands at ~1,215 against an 800 target, and the
%% arithmetic says where the rest would have to come from. CUT.md's keep-in-full
%% list here — the ten-row table with its caption, the dead-clamp example with
%% its surviving `+5`, the least-recorded caveat, the principle with its bound —
%% is ~565 prose words on its own; the buffer copy it orders kept is ~95; and the
%% magnitude paragraph is WELDED to §0's F2 clause and cannot be cut without
%% cutting that. That is ~780 before the gloss, the population, the tally, the
%% sweep, the figure caption and the takeaway (~350 together) are counted at all.
%% Reaching 800 needs a ruling that drops one of those five, not another trim.
%% ⚠⚠ TWO CORRECTIONS FROM THE FACT-CHECK, both in this paragraph.
%%  (a) "so the subtraction is like for like" is an INFERENCE from the licence
%%      rule, and the tree's own live calibration falsifies it on 3 of the 22
%%      `R3-R4` rows, one of them in the ten. The multisets are equal; the
%%      callees' COSTS are not. The rule's definition is true and stays; the
%%      inference is replaced by what the tally actually relies on.
%%  (b) The promotion is WELDED IN (fact-check §4.1, rigour M19). The census
%%      says nine of 22 exceed 100 `Ir`, and §3 prints nine; the ten is arm C,
%%      with the hash probe at its searched unsafe spelling. That was disclosed
%%      only in the table's caption two paragraphs later and in a `%%` comment,
%%      so a reader of §2 then §3 saw the paper print 9 and 10 for one quantity.
%% ⚠ TIGHTENED, ~12 words.  Both fact-check corrections stand: (a) the licence
%% rule matches CALLS and not their COSTS — "so the subtraction is like for like"
%% is an inference the tree's own calibration falsifies on 3 of the 22 rows — and
%% (b) the hash probe's promotion to arm C is disclosed HERE, in the sentence
%% that states the ten, not two paragraphs later, because §3 prints nine.
%% ⚠⚠ THE RULE NOW SAYS WHAT IT PROTECTS AGAINST, IN ONE CLAUSE, and it was the
%% fourth undergraduate pass's LARGEST hole — "I read this three times across two
%% sections and never got it … the rule is load-bearing and I cannot state what
%% it is protecting against."  The half-explanation was ours: we said the rule
%% matches calls and NOT their costs, and then that those costs never reach the
%% number — from which it follows, wrongly, that two versions calling different
%% outside code would be fair to subtract anyway.
%% THE MISSING STEP, and it is the one the count is kernel-EXCLUSIVE: work a
%% version hands to a callee leaves the measurement entirely, so a version that
%% calls out for work its opposite number does inline is credited for the whole
%% of that work.  Matching the call multisets is what forbids that.
%% ⚠ IT DOES NOT AND MAY NOT CLAIM THE HIDDEN WORK IS EQUAL.  That is fact-check
%% correction (a) above — the multisets are equal, the callees' COSTS are not,
%% and the tree's own calibration falsifies "like for like" on 3 of the 22 rows.
%% The first sentence still carries the calls/costs distinction verbatim, and the
%% new clause says only that one side must not look cheap, never that the two
%% sides hid the same amount.  ⚠ Do not upgrade "looks cheap" to a cost claim.
%% ⚠ §0's F2 states the rule without the calls/costs pair, so it reads as merely
%% unmotivated rather than as a contradiction; the hole was here and is fixed
%% here, at the point of use, which is where the reader hit it twice.
All \num{totals.patterns} programs ship both a tuned safe and an unsafe rung.
Subtracting one from the other is only fair when both make the same calls out of
the kernel, and **22 of those pairs are fair to subtract**. **Ten of the 22 clear
100 `Ir` per call on one of their two inputs**: nine as shipped, plus a hash
probe whose in-contract unsafe respelling moves it from `+2` to `+125`
(\ref{sec:bothends}). That fairness rule matches which calls each side makes, not
what those calls cost: we count only the instructions inside the kernel. The
calls must still match, or one side looks cheap for work it pushed out into a
callee.
Deltas come from the generated \src{results/synthesis.md},
attributions from the hand-written \src{results/SYNTHESIS.md}.

%% Beat 2 (F). C9's derived sentence, used in substance. ⚠ Do NOT write "a
%% constant-time discipline" for the constant-time row — that is its R2→R3
%% spelling factor, a different rung pair (C9, E2 §4.9). ⚠ Do NOT write "none of
%% it is a bounds check" for the partition row — its fitted law has no check
%% coefficient, but an unquantified scan-side check is named as OPEN (E2 §4.8).
%% ⚠ COMPRESSED, ~40 words: the prose used to re-list all five "something else"
%% mechanisms and the ⚠ row, which is verbatim the table's own `the named term`
%% column three lines below. The BUCKET COUNTS stay in the prose because C9's
%% 3 / 5 / 1 / 1 is the finding; the mechanisms stay in the table, where a
%% reader can see them against their rows. Nothing is lost and the two warnings
%% above still bind, because both apply to TABLE CELLS.
%% ⚠⚠ FLAGGED, NOT FIXED — the constant-time row's cell. The second bias review
%% (§4.9) reads that row's published figure as p47's SAFETY factor measured at
%% matched constant-time spelling, never decomposed, and says the honest cell is
%% "unattributed at this rung pair" — which would make the tally 3 / 4 / 2 / 1.
%% That is C9's number, a ruling this pass has no mandate to move and no time to
%% re-derive from p47's primary tables. Recorded here so the next reviewer can
%% settle it; if they do, §0's F2 and this section's title move with it.
Of the ten, **a bounds check is the named biggest cost on three** — a binary
search, a bitset and an index flatten (**F2**). On five it is explicitly
something else. On one, nothing in the **tree** — the research repository these
numbers come from — says what the gap is. On the tenth
the cost *is* the check, but one provably dead line deletes the whole per-pop
term.

%% Beat 3 (F). Pattern names as nouns, not IDs (CLAIMS.md §3.3). Both
%% corrections ride in the table and its caption, where a reader can see them.
%% ⚠⚠ PLAIN-LANGUAGE PASS: THE TABLE'S HEADINGS AND CELL TEXT ARE REWORDED, THE
%% ROWS AND THE NUMBERS ARE NOT. `bucket` -> `is it the check?`, whose values are
%% now yes / yes ⚠ / yes, and deletable / no / nobody knows ⚠ — the last is the
%% UNATTRIBUTED row and "nobody knows" is exactly what unattributed means here
%% (nothing in the tree attributes it at this rung pair); do not promote it to
%% "not the check", which is the error C9 corrects one row over. `the named term`
%% -> `what the notes name as the cost`. Cell wording: "amortising along nothing"
%% -> "paid per probe, never amortised"; "established not assumed" -> "measured
%% rather than assumed"; "a dead clamp" -> "a clamp that never fires"; the
%% rotate's "`zip`/`Rev` adaptor exhaustion tests" -> "the iterator asking twice
%% per item whether it has run out" (PLAIN.md's own gloss for that phrase), "no
%% pad at a swap or fold site" -> "no check code at a swap or a fold"; "its
%% published mechanism is another pair's" -> "the published cause is another rung
%% pair's". The caption now also glosses *blob*, which this file used four times
%% and never defined — readers arrive here by hash route.
%% ⚠ THE PARTITION CELL DELIBERATELY DOES NOT CARRY THE PUBLISHED "≥150 `Ir`/call
%% of the safe side is spelling". That figure is real but is measured against a
%% DIFFERENT QUANTITY from this row — a whole-program median-pivot probe
%% (p23/NOTES.md:744-755, `.temp/t101/cost23.rs`, TASK_106, PROVISIONAL), not the
%% kernel-exclusive 305.74 / 443.55 differenced here, and its own source says
%% "There is no single number for how wrong the floor was" (E2 §4.8). Attaching
%% it to this row would be the same defect this section corrects one row over.
%% ⚠ And do NOT replace the cell with "none of it is a bounds check": the fitted
%% law has no check coefficient, but p23/NOTES.md:940 names an unquantified
%% scan-side check whose cause the file marks OPEN.
%%literal-ok 260  the state machine's small-blob delta, 260.00 `Ir`/call, results/synthesis.md:326 — it collides with totals.proof_text.min_pct, which is an unrelated percentage
%% ⚠⚠ THE FINAL CUT: "Compress the ten-row table's 'what the notes name' column
%% to short phrases."  Done, ~25 prose words, and NO ROW, NUMBER OR VERDICT
%% MOVED.  What went is qualification that the column's own heading already
%% implies: "never amortised", "rather than assumed", "zeroes the per-pop cost",
%% "no check code at a swap or a fold", "taking a sub-slice", "the published
%% cause is".  ⚠ TWO CELLS WERE NOT SHORTENED, on purpose:
%%   * the index flatten keeps "— 77.2% / 81.5%", which is the DERIVATION that
%%     moved that row into the check bucket (C9), not decoration;
%%   * the partition keeps "the fitted formula has no check term", because the
%%     short form "not a check" is the claim p23/NOTES.md:940 marks OPEN — an
%%     unquantified scan-side check is named there, and asserting its absence
%%     would be the same defect this section corrects one row over.
| kernel | small | large | is it the check? | what the notes name as the cost |
|---|---:|---:|---|---|
| a binary search | +3,015 | +10,025 | yes | the check, paid per probe |
| a bitset | +13,756 | +48,885 | yes | three checks, measured not assumed |
| an index flatten | +123 | +399 | yes ⚠ | five of every six instructions per matrix row — 77.2% / 81.5% |
| a bounded stack | +359 | +626 | yes, and deletable | a clamp that never fires |
| a rotate | +334 | +172 | no | the iterator asking twice per item whether it has run out |
| a state machine | +260 | +4,100 | no | one `and $0x7,%edi` — a bit mask |
| a hash probe | +125 | +1,021 | no | a fresh sub-slice the unsafe rung does not take |
| a partition | +306 | +444 | no | the shape of the data; the fitted formula has no check term |
| a constant-time compare | +90 | +142 | no | its one named cause favours safe Rust |
| a field split | +638 | +425 | nobody knows ⚠ | another rung pair's cause |

Instructions per call inside the kernel, `-O3`, inlining suppressed, tuned safe
minus unsafe, over each pattern's two committed blobs. The hash probe is
shown at the respelling named above; as shipped it
reads `+2` flat. **⚠ marks two rows we reclassified**: the cause each published
belongs to a different rung pair. The index flatten's own notes supply a
replacement; nothing replaces the field split's.

%% ⚠⚠ ADDED, RULING C34(b) AND THE COVERAGE-BIAS REVIEW. This section printed an
%% ABSOLUTE delta for every check row and a percentage for NONE of them, while
%% the paper prints percentages freely where the number is small (0.897%,
%% 0.324%) or where it damages our own instrument (35%). The two largest check
%% rows are +205.6% and 42.5–46.6% of their kernels and a reader could learn
%% neither; ver_B printed the second as summary bullet 2. The thesis survives
%% this — it says the check is a minority of ROWS, not that it is small where it
%% wins — and hiding the magnitude costs the paper its method.
%% ⚠ Both figures carry their scope in the sentence: the binary search's is band
%% A at nq = 58, rising in n, confirmed over six query distributions
%% (`p07/NOTES.md:450-481`); the bitset's is the small blob (199.4% on large,
%% `p09/NOTES.md:193-199`). The clock's verdict on both is §3's.
%% ⚠⚠ THE LAST SENTENCE IS ADDED, second coverage-bias review §4.3 / N2, and it
%% is NOT optional: printing the corpus's largest check magnitude while
%% withholding the one measured fact that bounds it is this paper's own thesis
%% violated by its own headline. `p09/NOTES.md:1123` — which I opened — tables
%% `r3_best` (`chunks_exact(4)` queries + a byte-offset clamp) at +263.00 small
%% and +854.00 large against the shipped +13756.00 / +48885.00, in contract by
%% `check.py::spelling_matches`, `=====` to `model.py` on all five inputs, and
%% CHEAPEST ON BOTH BLOBS. Two clauses of that entry are welded in because
%% without them the number is unfair in the other direction: `chunks_exact(4)`
%% is `is not supported` at the pinned vstd, so the UNSAFE class cannot answer
%% with it (the file's own "R4-by-permission" asymmetry, its fourth measured
%% instance), and the R4 side WAS searched — `m_clamp_u` +241 and `m_clampb_u`
%% +721 both RAISE it and no unsafe respelling that lowers it was found, so the
%% pair interval collapses onto the R3-side span. ⚠ The R3-side span is
%% +263…+16,992 small, a 65x spread the pattern calls its sharpest illustration
%% that a published spread cannot carry a safety claim; the span itself is §3's
%% territory and is deliberately not printed here.
**Where the check wins, it is not a small number.** The bitset's three checks are
**+205.6%** of its unsafe kernel on the small blob. The binary search's one check
runs from **42.5%** of its kernel at 7 elements to **46.6%** at 16,385, rising
with array size over six query distributions. Both are shares of kernels that do
nothing else, so both bound what that check costs inside a real function;
\ref{sec:bothends} puts a clock on them. Both are also the *shipped* way of
writing that program: write the bitset's safe rung the cheapest way that still
meets the contract and it goes from `+13,756` to `+263`.
The unsafe side cannot answer with that spelling, and its own search found
nothing cheaper \src{patterns/p09-bitset/NOTES.md}.

%% Beat 4 (F). ⚠⚠ C10: THE SWEEP IS THE STRONGEST EVIDENCE HERE AND LEADS OVER
%% THE RATIO. E2 §5.3 printed T=50/100/150/300 signed n=10/9/8/8 and T=100/300
%% abs n=12/11, all with check={binary search, bitset} — that run PREDATES the
%% index-flatten reclassification, so its printed `check=2` reads as 3
%% throughout. I re-derived the denominators myself off `results/synthesis.md`'s
%% 22 licensed rows and reproduce them exactly; they are ARM A (shipped cells),
%% while the tally's denominator of 10 is ARM C (the hash probe promoted to its
%% searched value). Under ARM C the same sweep runs 11/10/9/9/13/12. THE CHECK
%% BUCKET IS THE SAME THREE ROWS UNDER BOTH ARMS AT EVERY THRESHOLD, which is
%% why the prose quotes the RANGE of denominators and not one arm's numbers.
%% ⚠⚠ CUT PASS (.temp/brief/CUT.md): "Compress the threshold sweep to two
%% sentences. The finding is that the same three rows come out at every cut-off.
%% The six populations do not need listing." ~60 prose words went. WHAT WENT:
%% the enumeration of the four thresholds and the two gap definitions as separate
%% sentences, and the closing pair — "counting by size above 100 also lets in
%% three rows where safe Rust is the *cheaper* rung; on each of those the
%% published margin is none of it safety, and the tally becomes THREE OF
%% THIRTEEN". RESTORE THE THREE-OF-THIRTEEN SENTENCE FIRST if words come back:
%% it is the one arm where the denominator moves and the numerator does not,
%% which is the sweep's own strongest form. The 8-to-13 range is kept in the
%% surviving sentence precisely so that restoring it changes nothing.
%% ⚠ TIGHTENED to two sentences, ~15 words.  "The cut-off is not doing the work"
%% is what the bolded clause already says.  Both sweep axes (signed gap, and size
%% regardless of sign) and both denominators (8 to 13) are still printed, which
%% is what makes the restoration of the three-of-thirteen sentence a no-op.
**The tally does not depend on where we drew the line.** Sweep the cut-off from
50 to 300 `Ir` per call, on the signed gap and then on its size regardless of
sign. The population moves between eight programs and thirteen. **The same three
programs are the check rows every time.**

%% Beat 5 (F). ⚠⚠ C11: "one dead line deletes 100% of it" IS WRONG of this row
%% and must not come back. It is 98.6% / 99.2% (359 → 5, 626 → 5) and a +5
%% per-call constant survives on both blobs — 2889−2884 and 8886−8881, read at
%% patterns/p03-bounded-stack/NOTES.md:1258-1266. The 100% is correct of the C
%% check (NOTES.md:438-442, both compilers, byte-identical) where the phrasing
%% originated, and became wrong when carried onto the Rust column.
%% ⚠ "13 pop densities and 6 sizes", never "19 input sizes" (C11).
%% ⚠⚠ `xpop` IS GLOSSED, 3 words, and it was the fourth undergraduate pass's
%% never-explained list: "the prose explains the FORMULA but never says `xpop` is
%% the number of pops — I had to reverse-engineer the symbol from the gloss of
%% the formula."  The symbol stays because the law is quoted as the tree fits it
%% (`3.00000·xpop + 5`, one of the four clamped cell laws above); what was
%% missing was the binding between symbol and quantity.  ⚠ THE GLOSS IS THE
%% TREE'S OWN VARIABLE: `xpop` is the EXECUTED pop count, which is why the fit
%% is exact and why the per-pop gap can go to zero without the constant going
%% with it.  Do not rewrite it as "pops requested" or "stack depth".
%% ⚠ The four clamped cell laws are `11·xpush + 9·dpush + 13·xpop + 46` (safe)
%% and the same with `+41` (unsafe). The prose used to gloss the two cell
%% subtractions as "the clamped laws' per-call constants of 46 against 41"; that
%% gloss is CUT for length (12 words). The two subtractions themselves stay,
%% because they are what makes the surviving `+5` checkable, and PART E protects
%% the `+5` itself.
%% ⚠ Provenance: `controls/gen_controls.py` is committed — I checked — so
%% "reproducible from a committed generator" holds; `grep -c clamp` is 0 in both
%% gate records, so "not gate-certified" holds too. Both clauses are mandatory.
\begin{example}{The check that costs exactly nothing}
%% ⚠ FINAL CUT, ~22 words: "The safe rung falls from 17 `Ir` per executed pop to
%% 13 and the unsafe rung from 14 to 13" — the two cell laws' per-pop slopes.
%% The RESULT of that subtraction, the exactly-zero per-pop gap, is what the
%% paragraph is for and it is still bolded; the four clamped cell laws are
%% `11·xpush + 9·dpush + 13·xpop + 46` (safe) and the same with `+41` (unsafe).
%% ⚠ THE TWO SUBTRACTIONS IN THE NEXT PARAGRAPH ARE NOT THIS, and they stay:
%% 2889 − 2884 and 8886 − 8881 are what make the surviving `+5` checkable.
A bounded stack's tuned safe rung costs `+359` `Ir` per call on the small blob
and `+626` on the large, against its unsafe rung. The whole of that difference is
`3.00000·xpop + 5`, with `xpop` the number of pops executed: three instructions
per pop, plus five.
Now hand the optimiser the fact the proof already proves. Write it as a
**clamp** — a line forcing the index back into range that can never fire, because
the proof shows the index is in range already. The optimiser can then
drop the real check. **The per-pop gap becomes
exactly zero.** That holds at 13
different rates of popping and 6 stack sizes, with nothing fitted. The formula's
largest error against a measured cell — its *residual* — is 0.000000
\src{patterns/p03-bounded-stack/NOTES.md}.

**That is 98.6% of that gap on one input and 99.2% on the other, not all of it.**
The `+5` survives on both
blobs — 2889 − 2884 and 8886 − 8881. The hand-written synthesis never mentions
it, and nobody has searched it at all. The whole of it does go on this pattern's
C check: given the same clamp, both compilers delete the manual check
byte-identically. gcc and rustc share no optimiser, so that lets us claim **both
compilers here**, never *any compiler*. The clamp is a **control**: a copy of the
program altered to test one thing. It is reproducible from a committed generator,
and certified by no gate.
\end{example}

%% Beat 6 (F). ⚠ C14 picks these three. The handle table is CONFIRMED and closed
%% in the strong sense (sum over EVERY function = whole-program delta; verified
%% at patterns/p27-handle-table/NOTES.md:789-812). The NUL scan's claimed
%% 12.0×/5.3× split is NOT closed — its third term is an additive rate from a
%% different rung pair — so this uses its §4a, which is clean (verified at
%% p11/NOTES.md:252-278). The buffer copy is CONFIRMED verbatim and the symmetry
%% control is its best line (p02/NOTES.md:387-396, p02/README.md:81).
%% ⚠ The handle table's mechanism is the FLAT per-function self-cost table, NOT
%% "callgrind's caller→callee edges" as results/SYNTHESIS.md:427 says.
%% ⚠ PLAIN PASS: "whole-program marginal" is spelled out as "measured over the
%% whole program" (PLAIN.md bars the bare noun), and `drop glue` now carries a
%% four-word gloss — it is Rust-specific and this is the only place it appears.
%% ⚠ The NUL scan's and the buffer copy's decompositions are both of a
%% MECHANICALLY PORTED safe rung against the unsafe one — a different pair from
%% the ten-row table — and the prose says so each time, because conflating two
%% rung pairs is precisely the defect this section is about.
%% ⚠ m6: the old lead sentence declared "all three in whole-program marginal `Ir`
%% per call" under a table captioned kernel-exclusive, and the NUL scan's rates
%% are PER-BYTE off a disassembly. The metric now attaches to each row.
%% ⚠ CUT FOR LENGTH, and recorded so nobody thinks it was missed: the NUL scan's
%% §4a decomposition — fold `4.25 = 2.00 check + 2.25 foreclosed unroll`, scan
%% `3.00` all check, total 7.25, every rate off the disassembly, max residual
%% 0.000 over 61 points (C14's ✅ replacement for that pattern's broken 12.0x /
%% 5.3x split, which is NOT a closed decomposition and must never come back).
%% It was the third of three instances of ONE finding; the finding survives on
%% two, and the handle table's is the one the cold reader called the most
%% convincing single piece of evidence in the paper. If words come back here,
%% this is the first thing to restore.
%% ⚠ ALSO CUT FOR LENGTH, and it is the SECOND thing to restore: the buffer
%% copy's own quoted line, *"The indexed fold's bounds checks cost zero
%% instructions — LLVM hoisted every one of them."* It is a good sentence and it
%% is the same fact §1 already publishes as 0.00000 `Ir` per folded byte on a
%% different kernel, so it was the one clause here that repeats another
%% section's finding rather than adding to it. The paragraph's own payload —
%% the copy, not the fold, was what was priced — is untouched, as is the
%% hardened-C antibody, which is the reason this row is in the section at all.
%% ⚠⚠ CUT PASS (.temp/brief/CUT.md), AND THIS IS THE SECTION'S BIGGEST CUT:
%% "Cut two of the three decompositions. KEEP THE BUFFER COPY, because its C
%% symmetry control ('in a language with no bounds checks at all') is the best
%% line in the section and it is the only one that lands without new vocabulary.
%% Drop the handle table and the NUL scan." The NUL scan went in the previous
%% pass (its note is above); THE HANDLE TABLE GOES HERE, ~95 prose words.
%% WHAT IT SAID: the handle table publishes its numbers measured over the whole
%% program, not just the kernel, and its difference is
%%   230.0694 = 109.6476 kernel + 120.4218 drop glue + 0.0000 allocator
%% (drop glue = the code Rust runs to release a value); the sum over EVERY
%% function equals that delta to the last digit, so the three terms are not
%% picked out of many; and the allocator zero is a difference of calls that are
%% present, large and equal on both sides — `malloc` 421.1211 either way, `free`
%% 310.2635 either way — not a missing symbol. Verified at
%% patterns/p27-handle-table/NOTES.md:789-812.
%% ⚠⚠ THIS CUT COSTS THE MOST OF ANY IN THE PASS AND THE RULING IS EXPLICIT
%% ANYWAY. The cold reader called this decomposition "the most convincing single
%% piece of evidence in the paper", and it is the only CLOSED one (sum over every
%% function = whole-program delta). RESTORE IT FIRST, ahead of anything else in
%% this file. It also carries the mechanism correction that
%% results/SYNTHESIS.md:427 gets wrong — the evidence is the FLAT per-function
%% self-cost table, NOT callgrind's caller→callee edges.
%% ⚠ THE ALLOCATOR ZERO IS NOT LOST: §1's prior-work paragraph publishes
%% `0.0000 Ir per call` as the point on which we and \cite{userstudy25} agree by
%% different methods, and §0's F4 note points there. The three-term split is what
%% went. ⚠ The lead sentence moved with it: two rows became one, so the paragraph
%% now leads on the operation ("change one thing at a time") rather than on a
%% count of rows, and no sentence in this file claims two decompositions.
%% ⚠⚠⚠ THE FINAL CUT (target 6,200 prose words for the paper): **THE BUFFER-COPY
%% DECOMPOSITION IS CUT**, 103 prose words with its lead sentence.  It was the
%% last of the section's three decompositions — the NUL scan went two passes ago
%% and the handle table one pass ago, and both their records are above.
%% WHAT IT SAID: "**Change one thing at a time and the gap names itself.**  A
%% buffer copy's `+178` / `+1,025` is measured against its MECHANICALLY PORTED
%% safe rung — a different pair of rungs from the ten above, which is the very
%% confusion this section is about.  It is an inline byte copy against a
%% `memcpy`: change only the fold and nothing moves, change only the copy and it
%% reads `+10` flat.  **Take that pattern's hardened C rung and replace its
%% `memcpy` with the same byte loop**: it pays +905.6 under gcc and +527.6 under
%% clang on the large blob.  That is in a language with no bounds checks at all.
%% \src{patterns/p02-buffer-copy/NOTES.md}"  Verified at p02/NOTES.md:387-396 and
%% p02/README.md:81.
%% ⚠⚠ WHAT THIS COSTS, stated plainly so the next reviewer can price restoring
%% it: the C SYMMETRY CONTROL was the best line in the section and it is the
%% section's own antibody — a C-column instance of the same misattribution, in a
%% language with no bounds checks, which is what stops the finding reading as a
%% Rust story.  §1's compiler-gap beat and §3's whole C-column subsection still
%% carry that argument, so the antibody survives in the paper; it no longer
%% survives in this section.  RESTORE THIS FIRST OF ALL CUTS IN THIS FILE.
%% ⚠ WHAT DOES NOT NEED RESTORING WITH IT: nothing \refs this paragraph, and no
%% other sentence in the paper quotes +178 / +1,025, +10, +905.6 or +527.6.
%% ⚠ THE "different pair of rungs" WARNING IS NOT LOST: the section's opening
%% beat, the table caption and the two ⚠ rows all turn on which rung pair a cause
%% was measured at, which is this section's whole subject.

%% ⚠⚠ BEAT 7, `example{The row that was caught before it was built}`, IS CUT —
%% 128 prose words, the single cheapest cut on the previous revision's own
%% ranked list, and the trim brief names it. WHAT IT WAS: C13's two prospective
%% catches — an intrusive list reading "safe Rust is 6.02x cheaper", whose exact
%% decomposition `-9 - 16 + 321 = +296` puts 108.4% of the gap in the allocator
%% and the bounds check at 9.00, i.e. 3.0% of the magnitude with the opposite
%% sign; and a flexible array member's 9.6% that is 100% safe-side spelling,
%% respelled to the safe rung beating the unsafe one by 17.00 `Ir`/call.
%% WHY IT COSTS THE ARGUMENT NOTHING: every figure survives in §0's F7, which
%% keeps C13's licensed sentence verbatim ("Both were caught before
%% publication") and its **Do:**; §6 is FORBIDDEN from citing F7 at all
%% (redundancy map), so nothing else pointed here.
%% ⚠ AND IT REMOVES A COVERAGE-BIAS ITEM RATHER THAN LEAVING ONE. Second bias
%% review §4.7: this example and F7 both turn on the refusal record, and
%% `results/SYNTHESIS.md:867-873` — unchanged, and I re-read it — says "of four
%% refusal reasons ever checked against their artefacts, three did not survive",
%% calling it "strong evidence that this project's REASONS were held to a lower
%% standard than its FINDINGS". The featured example was the heaviest user of
%% that record. §0's F7 states only that the measurement would have been wrong
%% and was caught, which is C13's licensed shape and does not lean on a stated
%% reason, so the residue there is small; if this example is ever restored, it
%% must ship the audit clause with it.

%% Beat 8 (L, 90 words — this section's entire standalone caveat allowance).
%% ⚠ C12, and it is NOT optional: it is what the title's second clause promises.
%% ⚠⚠ `undeclared` means NOBODY WROTE AN ENTRY and has never meant nobody
%% searched (CLAIMS.md §1.22, results/synthesis.md:668). Any sentence of the form
%% "N rows were never searched" is false and the tree says so explicitly — §3's
%% caveat is built on that, so do not pre-empt it with a count here.
%% ⚠⚠ "two of the three check rows" WAS WRONG AND THE CORRECTION STRENGTHENS THE
%% BOX. The fact-checker read the search-state column at
%% `results/synthesis.md:310-335` for all ten rows: p05, p07 and p09 all print
%% `undeclared`, so ALL THREE check rows are among the six, not two. The "two"
%% was a survival from the 2-of-10 draft — ruling C9 moved the index flatten into
%% the check bucket and that row also prints `undeclared`. §0's F3 took the same
%% correction. The numerator is now ENTIRELY undeclared, which is exactly what
%% this box's title claims.
%% ⚠ PLAIN PASS: the box's HEADING carries the title's second clause, which the
%% short new \section title had to shed — "The three check rows are the
%% least-recorded part of the tally". "Numerator" is gone from the prose; the
%% rigour-B4 word "least-recorded" is not, and "least-searched" is still false.
%% ⚠⚠ THE BOX NOW NAMES BOTH SEARCHED CHECK ROWS, not just the binary search.
%% Second bias review §4.3: this caveat named the binary search as the one
%% `undeclared` row hiding a search worth ~15%, and did not name the bitset,
%% whose `undeclared` hides a 98% one — printed four paragraphs above as
%% +13,756 → +263. Naming both costs nothing (it is shorter than the old
%% wording) and it is what makes the box's own title true of the numerator it
%% describes. "Both check rows quoted above" is exact: those are the two rows the
%% magnitude paragraph prints; the index flatten is the third check row and its
%% search state is not what is claimed here.
%% ⚠ The last sentence is C34 / bias review §3.7: F2 used to open "It
%% generalises", against `results/SYNTHESIS.md:592-599`'s own "so it is not a
%% score. Read the entries, not the tally" and `:877-883`'s "fourteen of its
%% patterns carry an `index >= len` axis". Note it cuts BOTH ways and the clause
%% says so — a corpus weighted toward bounds bugs finding the check dominant on
%% three of ten is a stronger result, not a weaker one.
%% ⚠⚠ CUT PASS: THIS BOX IS NOW THE FINDING'S ONLY HOME. The summary's ten
%% findings became six by ruling (.temp/brief/CUT.md), and the least-recorded
%% finding — old **F3** — was one of the four dropped, "to section 2's caveat,
%% where its evidence already is". So the `(**F3**)` citation that used to sit on
%% the mechanism sentence is gone: it would now resolve to the identity-pin
%% finding, which is a different claim. NOTHING ELSE IN THE BOX MOVED. If the
%% summary ever regains the bullet, the citation comes back with it.
\begin{caveat}{The three check programs are the least-recorded part of the tally}
For six of the ten, nobody recorded whether a cheaper spelling was ever looked
for — **all three check programs among them**, and the unexplained one too. That
blank has never meant nobody searched. The record was wrong by four entries
recently, and both check programs quoted above hide a search. The bitset's is the
`+13,756` → `+263` above, 98% of its gap. The binary search's own notes record a four-spelling
search in which the shipped one is among the dearest, and the tree publishes no
figure for what that search is worth. The bias has a mechanism. Our top rung
carries a machine-checked proof, and a cheaper safe spelling adds nothing the
proof must take on trust; a cheaper unsafe one has to be proved
again. Nor are these ten a sample: fourteen of this corpus's programs were built
with an out-of-range index as their bug. Read the entries, not the tally
\src{results/SYNTHESIS.md}.
\end{caveat}

%% Beat 9 (I). ⚠ THE METHOD IS DEFINED HERE AND ONLY HERE (OUTLINE PART 2).
%% §4 names it and says where it FAILS, §5 BOUNDS it, §6 OPERATIONALISES it —
%% each adds something. Do not pre-empt them, and there is no fifth appearance.
%% ⚠ CLAIMS.md §1.23 requires the bound to ship WITH the method. ⚠ E4 B14 adds
%% the precision that the hypothetical has no instance here: the only zero
%% differences in the corpus are proved-minus-unsafe, which the identity pin
%% makes a tautology. So it bounds the method; it is not a defect observed.
\begin{principle}{Remove the mechanism and re-measure}
A cost belongs to a mechanism only if removing the mechanism moves the number.
Counting checks predicted `+626` on the bounded stack; deleting them answered
`+5`. Nothing in this gate can tell a
deleted check apart from two versions that happened to compile to the same bytes,
so a zero difference does not let you say *safety is free here*. No safe-minus-unsafe
difference in this corpus is zero, so that bounds the method rather than naming a
defect we saw.
\end{principle}

%% ⚠ THE FIGURE MARKER BELOW MUST STAY ON ONE LINE — a wrapped one vanishes
%% silently (the marker is not written out here, because build_data.py scans the
%% raw body for figure ids and does not strip these comments first) and takes
%% its \label with it; two figures shipped that way. The chart is R3−R4 on
%% `isolated/small.bin`, one bar per pattern, sorted, diverging (index.js:2805),
%% so it draws the SHIPPED delta — +2 for the hash probe, not the +125 the table
%% above uses. The caption says so rather than letting a reader find it.
%% ⚠ PLAIN PASS: the caption's "rows the licence rule excludes" is now "rows that
%% are not fair to subtract", the same words beat 1 uses for the rule.
\figure{rungcost}{Tuned safe Rust minus unsafe Rust, one bar per pattern, small blob, inlining suppressed. The hash probe is drawn at its shipped +2, and four bars are programs that are not fair to subtract.}
\label{fig:rungcost}

%% ⚠ FINAL CUT, ~28 words: the takeaway is one sentence.  What went is the
%% restatement of the tally — "A bounds check is the named biggest cost on three
%% of these ten rows, and on a fourth one provably dead line deletes almost all
%% of it" — which is the section's own headline, its title, and §0's F2, all
%% within one screen.  Convention 2.5 is still satisfied: the box carries a claim
%% and points at the §6 subsection that spends it.
\begin{takeaway}
Find the instructions and read them before you blame a gap on memory safety —
\ref{sec:measure}, *"If you are publishing a number"*, says how.
\end{takeaway}
