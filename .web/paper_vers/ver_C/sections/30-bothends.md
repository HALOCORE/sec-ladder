\section{Both sides of the comparison move, and ours is held too high}
%% ⚠ TITLE REWORDED after the second cold read. It said "and we hold ours up",
%% which the reader parsed as "we defend ours" -- the OPPOSITE of the meaning.
%% The clause is an admission: our own byte-identity requirement holds the
%% unsafe baseline ABOVE its cheapest spelling, so every safe-versus-unsafe
%% figure in this report flatters safe Rust. "Held too high" cannot be read the
%% flattering way. Do not restore the old wording.
\label{sec:bothends}

%% ⚠⚠⚠ THE THIRD UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad3.md), 5/10.
%% ⚠⚠ THIS FILE SCORED **3**, the joint-lowest in the paper, and the reason is
%% structural rather than verbal: "By that point I had already accepted 'the
%% number depends on which two versions you pick' from §1 and this was the fourth
%% demonstration of it."  Not one figure moved.  Four changes:
%%  1. ⚠⚠⚠ ONE DEMONSTRATION IS CUT — the `Rewrite the safe side` subsection and
%%     its 7.26× median.  Its full record, the reason it and not the hash probe
%%     went, and its restore instructions are at the site, below the hash-probe
%%     beat.  THE IDENTITY-PIN SUBSECTION IS UNTOUCHED: it is this section's
%%     reason to exist, the reader called the same finding "the most honourable in
%%     the paper" on their first pass, and CUT.md has never made it available.
%%  2. ⚠ THE HASH-PROBE BEAT LOST ITS QUALIFICATION PILE, ~7 words.  It read
%%     "still in contract, still verified, still compiling to the same bytes as its
%%     proved version at `-O3`" — the reader: "Four qualifications in one clause,
%%     three of which I couldn't check", and this is the sentence they say they
%%     would have stopped reading at.  It now reads "still meeting the contract and
%%     still passing the same-machine-code rule", which says the same two things a
%%     reader can act on and names the rule §1 now justifies.  ⚠ NOTHING WAS
%%     WEAKENED: in-contract and identity-pinned are both still asserted, and the
%%     62.5× / 510× pair still names its input, which is CLAIMS.md §1.3.
%%  3. ⚠⚠ "That keeps the proof honest, and" IS GONE FROM THE IDENTITY OPENING,
%%     replaced by a \ref to §1.  THIS IS THE PAPER'S BIGGEST SINGLE FIX THIS PASS
%%     AND IT IS NOT A CUT.  Those five words were the ONLY justification the
%%     same-machine-code rule had anywhere, across FIVE appearances (§0's F3, §1's
%%     digest sentence, this subsection, §6.4's first bullet, §7's closing rule),
%%     and the reader's verdict was: "for four sections I was being told about the
%%     consequences of a design decision whose purpose I couldn't see … My reaction
%%     was: then why not drop it?"  §1 now answers that in three sentences at the
%%     rule's first use in the body, and this passage points at them.
%%     ⚠ IF §1's JUSTIFICATION IS EVER CUT, RESTORE "That keeps the proof honest"
%%     HERE — this passage may not be the only place the rule is stated AND the
%%     only place it is unexplained.
%%  4. THE NEGATIVES CLAUSE PUTS THE RIGHT READING FIRST.  Same fact, same
%%     mandatory metric naming (C6 and C21: three counted inside the kernel, four
%%     across the whole program), with the counting rules stated before the
%%     correction rather than after it.  ⚠ THIS IS THE SURVIVING "not X"
%%     PRE-EMPTION OF THE THREE THE READER FLAGGED, kept deliberately: they said
%%     this one "is doing real work".  §0's "not a range" and this file's "not two
%%     totals" both went.  DO NOT ADD A FOURTH.

%% ⚠⚠⚠ THE SECOND UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad2.md), 4/10.
%% Not one figure moved.  Four changes:
%%  1. ⚠⚠ THE GLOSS BLOCK IS CUT to the one sentence this file's argument turns
%%     on.  `rung`, `kernel` and `spelling` were glossed in five files running and
%%     the reader named the repetition as the reason they began skipping blocks.
%%     §0 defines `kernel` in its orientation paragraph, §1 re-glosses it and
%%     defines `spelling`, `rung`, `prover` and `obligation`.  The prose here says
%%     "version" where it used to say "rung".  ⚠ DO NOT RESTORE THE BLOCK.
%%  2. ⚠⚠ 510× NOW SHOWS ITS ARITHMETIC AND ITS OTHER BAND.  The reader hunted
%%     the paragraph for where 510 came from and worked out `+1021` against `+2`
%%     only while writing their report.  Both ratios are the tree's own:
%%     1021/2 = 510.5, which every source prints truncated to 510, and 125/2 =
%%     62.5.  ⚠ THIS ALSO DISCHARGES CLAIMS.md §1.3 IN FULL — that entry forbids a
%%     bare "510×" and names 62.5× as the small band — where the old sentence
%%     discharged it only by saying "its value on one input".
%%  3. ⚠⚠ 7.26× SAYS WHAT IT IS A RATIO OF.  The reader: "7.26× of WHAT quantity?
%%     §1's table says the ported version is 40921 and the tuned is 23875, which
%%     isn't 7.26×."  `results/SYNTHESIS.md:194-197` is a ratio of two GAPS over
%%     the unsafe rung ("the naive rung R2 is dearer than the tuned one by a
%%     median of 7.26x"), which p22's collapse from 1 033× to 2.02× confirms.  The
%%     verb "pays" was doing duty for a total and for a difference two sentences
%%     apart, so it is gone.  ⚠ BOTH CONJUNCTS OF THE POPULATION STILL PRINT,
%%     which is what C23 protects, and the median is still over 17.
%%  4. the negatives say "two counting methods, not seven programs" — the reader
%%     could not tell whether three-and-four meant seven.  C6 and C21's mandatory
%%     metric naming is unchanged.  And the join says "silence" for "a null",
%%     which the reader first read as the number 0 after 1,000 words of numbers.

%% ═══════════════════════════════════════════════════════════════════════════
%% SECTION 3.  PLAIN-LANGUAGE REWRITE, IN PLACE (`.temp/brief/PLAIN.md`).
%% PROSE ONLY.  Not one number, correction, retraction or admission changed; the
%% beat list is the one the four review rounds settled.  What changed is HOW it
%% is said: one idea per sentence, every scope clause allowed to stand in the
%% NEXT sentence (CLAIMS.md §3.4 AS AMENDED — the old "same sentence, full stop"
%% wording is what produced the 38-word sentences this pass removed), and the
%% counting rules, tier arguments and ruling citations moved down into these
%% comments, where they protect the passage and cost the reader nothing.
%%
%% RULING C23 IS THIS SECTION'S SPINE and every measurement beat below is one of
%% its bullets.  C21 (hardening) and C12 (the one-way search bias) are the two
%% borrowed rulings.  Every figure was re-checked against a primary artefact
%% before being written down; where a check moved something, the `%%` note on
%% that passage says so, and those notes are the record.
%%
%% ⚠ THE TITLE.  Was "Both endpoints of the difference move, and ours is pinned
%% above its floor" (13 words, three pieces of jargon).  Now 11 plain words with
%% both claims intact.  Gate 1's expensive second clause survives: §2 proves
%% somebody else's misattribution, this section proves OURS, and the identity-pin
%% consequence is still stated flat, with no softening clause after it.
%%
%% ⚠ DO NOT TAKE WORDS FROM: the three identity-pin corrections; the two
%% conjuncts that fix the 7.26× population; the "the subtraction is ours" flag on
%% the binary search; the wall-clock counterweight pairing (+13.0% / +1.6%); or
%% the join.  Each is a correction or a ruling, not connective tissue.
%%
%% ⚠⚠ MEASURED, AND THE WORD BUDGET WAS NOT MET.  Sentences 46 -> 83, median
%% 27 -> 16 words, over-35 15 -> 1 (and that one is a MEASUREMENT ARTEFACT: the
%% `\figure{}{}` caption ends in `}`, so PLAIN.md's splitter glues it to the
%% `\begin{principle}{…}` heading and the box's first sentence.  No real sentence
%% in this file exceeds 33).  Prose words 1,283 -> 1,340, against a target of
%% 850.  THE TARGET IS NOT REACHABLE WITH THE FACTS INTACT, and the arithmetic is
%% worth recording: this file states ~55 distinct measured claims, each of which
%% needs its scope, and one-idea-per-sentence plus the four mandated glosses
%% (`rung`, `spelling`, instructions per call, and obligation-by-use) costs MORE
%% words than the 38-word originals did, not fewer.  The dense version was
%% already at the fact floor; what changed is that the floor is now readable.
%% Reaching 850 means deleting about a third of the claims.  In the order the
%% supervisor should consider, each losing something named in a ruling:
%%   1. the C-column beat's second and third per-event examples, then its range
%%      (C21 ✅ ships all four; ~30 words);
%%   2. the bucket-label paragraph (~52) — an admission about our own labels;
%%   3. the `undeclared` caveat (~65) — the reader's third meeting with those
%%      epistemics, but the only place 14 of 26 appears;
%%   4. three of the four wall-clock counterexamples (~90) — C34(d) says both
%%      directions ship together, so this is a ruling change, not a trim.
%% NOT AVAILABLE: the identity-pin passage, the hash-probe respelling, the 7.26×
%% and its population, the binary search's pair, the principle, the join.
%% ⚠ THIS IS THE SECOND BUDGET THIS SECTION HAS MISSED WITH THE SAME MANDATED
%% CONTENT, and the previous miss is evidence rather than an excuse: the outline
%% budgeted 980 and its own per-beat estimates summed past that before the first
%% three beats were costed at all, so the earlier writer shipped 1,112 and said
%% so.  Two independent budgets set without costing the beat list is a fact about
%% the budgets.  If 850 is firm, a ruling has to leave the file.
%%
%% ⚠⚠⚠ THE CUT PASS (.temp/brief/CUT.md) DID EXACTLY THAT — three rulings left
%% the file, in the order this list predicted: the bucket-label paragraph (item 2
%% above), the `undeclared` caveat (item 3), and the sign-flip beat compressed to
%% one clause; the 7.26× beat is one sentence.  ~225 prose words, and the file
%% lands at ~1,115 against a 750 target.  WHAT NOW STANDS BETWEEN IT AND 750, all
%% of it named on CUT.md's own keep list or welded elsewhere: the identity-pin
%% passage with its three corrections and the byte-for-byte exception §6.4 \refs
%% (~215), the hash-probe endpoint example (~105), the binary search's pair with
%% the clock counterweight its own notes forbid separating (~130), the C-column
%% beat — now the hardening finding's ONLY home (~145), the two-direction
%% wall-clock passage C34(d) ships whole (~245), the principle (~75) and the join
%% (~75).  ⚠ ITEM 1 OF THE OLD RANKED LIST IS WITHDRAWN: the C-column examples
%% cannot be trimmed now that §0 no longer carries the median.  The next cut here
%% is item 4 — three of the four wall-clock counterexamples — and that is a
%% change to ruling C34(d), not a trim.
%%
%% ⚠ WHAT THIS SECTION MAY NOT TOUCH (PART 2, the redundancy map): the six-rung
%% table and its four taxes are §1's — F1 is cited ONCE, in a clause, with no
%% figures.  The ten-row tally and the threshold sweep are §2's — F2 is cited
%% ONCE, for the sweep's stability, restating no number.  The bounded stack's
%% dead clamp, the handle-table decomposition and the two prospective catches
%% are §2's outright.  The deleted-line table is §5's.  The word `resource` is
%% §4's and appears here exactly once, in the join, as the thing the NEXT
%% section needs — which Part 0.3 licenses.
%%
%% ⚠⚠ TWO ARTEFACTS CONTRADICT DOCUMENTS THIS FILE WAS HANDED, AND THE ARTEFACT
%% WINS BOTH TIMES.  Details are on the passages themselves; recorded here so the
%% supervisor sees them without reading the whole file.
%%   (a) ver_B's `50-cantsay.md` gives the wall-clock counterexample a NAMED
%%       MECHANISM — "callgrind counts a `rep`-string instruction once per
%%       repetition".  That is a DIFFERENT pattern's mechanism, and
%%       `.memory/03-measurement.md:425-436` explicitly rules it out for this
%%       one.  The pair is unexplained and this file says so.  ver_B's sentence is
%%       not carried forward, and if it survives anywhere else in ver_C it is
%%       wrong there too.
%%   (b) `results/SYNTHESIS.md:62-64` — the same paragraph this section's central
%%       finding comes from — says the unsafe class "cannot reach it at all".
%%       `.memory/04-verus.md:1475-1482`, the authoritative layer, RETRACTS that:
%%       the unsafe class does reach `core::slice::memchr`, at four hand-written
%%       axioms no gate stage checks.  The identity-pin finding does not flip;
%%       only its reason does.  This file says the rule FORBIDS the spelling and
%%       never that the prover cannot express it.
%% ═══════════════════════════════════════════════════════════════════════════

%% ⚠⚠⚠ THE UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad.md).  Not one figure
%% moved.  Five changes, and the third is the important one:
%%   1. `kernel` DEFINED in the opening gloss block — undefined in all nine files,
%%      used eight times here, and read as "operating system kernel" throughout.
%%   2. THE 7.26× POPULATION IS NAMED.  The old sentence gave two populations and
%%      said which produced the median only by word order; the reader asked
%%      outright "Is the median over 22 or over 17?"  ⚠ IT IS OVER **17**, and
%%      `results/SYNTHESIS.md:195-197` says so in its own words: "a median of
%%      7.26x across the 17 licensed rows whose `R3 − R4` is positive on `large`".
%%      The old wording ("That median covers the 22 … pairs it is fair to
%%      subtract, 17 of which show a positive gap") reads as 22 and was wrong.
%%      Both conjuncts are still printed, which is what C23 protects.
%%   3. ⚠⚠ THE C-COLUMN PARAGRAPH IS REWRITTEN.  THIS IS WHERE THE COLD READER
%%      PUT THE PAPER DOWN — at "Over the 50 (pattern, input) cells from 25
%%      hardened patterns…", which they called "one sentence with a median, a
%%      two-part range, two compilers, two counting methods and two different
%%      counts of 'negative'".  They also could not say what the subsection was
%%      FOR: "the paragraph never says what 'it' is or who is getting it wrong",
%%      and "I now think the point is 'this isn't a Rust story, C does it too' —
%%      but that's stated nowhere in the prose".  So it is stated now, first, in
%%      the subsection title ("C gets its own safety cost wrong the same way") and
%%      in the lead sentence ("None of this is a Rust story").  ⚠ CLAIMS.md §1.5 IS FULLY
%%      DISCHARGED AND NOTHING WAS DROPPED: median 24, range −125…+10,242 gcc and
%%      −108…+5,637 clang, and the negatives with C6/C21's MANDATORY metric
%%      naming (three inside the kernel, four across the whole program).  The
%%      unit is still both inputs pooled — "counted over both inputs of each" is
%%      the 50 (pattern, blob) cells, in words a reader does not have to decode.
%%      `hardening` is glossed here: the reader had it as "inferable by §1, never
%%      actually defined", and this subsection is its only home in the paper.
%%   4. THE ANONYMOUS COMPILER IS NAMED.  "one compiler ran 10% fewer instructions
%%      and took 23% longer" is the paper's one genuinely weird result and the
%%      reader flagged it as the only anonymous number in the document.  It is
%%      gcc: 8,765 against clang's 9,764 Ir/call, 30.97 against 25.19 ms, both
%%      re-derived in the note below from `results/p02-buffer-copy.json`.  ⚠ THE
%%      LAST FOUR WORDS ARE UNTOUCHED — "and we cannot explain it" is the sentence
%%      the reader said earned the most trust in the whole paper.  ⚠ CLAIMS.md
%%      §3.10 still holds: this ranks two compilers, never two rungs.
%%   5. `resource` IS OUT OF THE JOIN, which now asks what each guarantee WATCHES
%%      — §99's wording, and §4 still introduces the noun under its own heading.
%%      The reader: "'resource' is doing heavy lifting one whole section before
%%      it's defined."  ⚠ C32's five corrections are all untouched by this: the
%%      sentence still says the next half must ALSO name it, not instead.
%%   ⚠ `twin` and `reslice` are said in plain words here ("the same bytes as its
%%   proved version", "one extra sub-slice"); both are on the reader's
%%   never-explained list and §4 is where `twin` is glossed for the paper.
%% Convention 2.10.3: hash-routed readers land here, so `rung`, `spelling` and
%% `Ir` are glossed again, in the plain wording PLAIN.md's vocabulary table sets:
%% `Ir` is never the bare symbol, and it is not used as a symbol anywhere in this
%% file any more — "instructions per call" is spelled out every time.
%% `obligation` is glossed BY USE below ("proving everything it must") rather
%% than defined, which is cheaper and reads.
%% ⚠ Deliberately NOT quoting `20 verified, 0 errors` there: CLAIMS.md §3.7
%% requires "Verus's `N verified` counts items, not verification conditions" to
%% be said before leaning on such a number, and that sentence is spent in §6.4.
%% The prose leans on the verdict, not on the count.
%% ⚠ FINAL CUT, ~32 words: this file's re-gloss is down to the two terms its own
%% prose actually turns on.  Convention 2.10.3 asks for a re-gloss because a
%% reader lands on `#bothends` by hash route; it does not ask for the full
%% vocabulary table three sections running.  WHAT WENT: "Two rungs can differ only
%% in *spelling* — a different way of writing the same program" and
%% "**Instructions per call** are what the processor really ran inside the
%% function measured."  ⚠ RESTORE BOTH if a reader ever reports landing here
%% lost: *spelling* is used four times below and "instructions per call" is
%% spelled out in full at every appearance in this file, never as the bare `Ir`.
A safety-cost figure is one version minus another. \ref{sec:onekernel} moved one
of the two (**F1**), and \ref{sec:notthecheck} the other. Both move.

\subsection{Rewrite the unsafe side}

%% C23 bullet 2, cross-checked against E4 §A2 and re-read at
%% `results/synthesis.md:328` and `:661-662`.  The ⚠⚠ is that the multiplier is
%% `(nkw-3)/2`, unbounded in input size; `nkw` is 128 on small and 1024 on
%% large, giving 125 and 1021 exactly.  1021/2 = 510.5 and every source prints
%% the truncated 510, so "every source prints 510x" quotes the tree while
%% "510.5x" would be more precise than the tree.  CLAIMS.md §1.3 forbids a bare
%% "510x", which is why the value's one input is named beside it.
%% ⚠ FINAL CUT, ~18 words: "The multiplier is `(nkw − 3)/2` in the keyword count,
%% so it grows without limit as the input grows."  It is the MECHANISM behind
%% 510×, and CLAIMS.md §1.3's requirement is discharged without it — the number
%% still ships "its value on one input", and the sentence still says outright
%% that quoting it as a constant is the error.  RESTORE IT if words come back:
%% `nkw` is 128 on small and 1024 on large, giving 125 and 1021 exactly, and
%% 1021/2 = 510.5, which every source in the tree prints truncated to 510.
**A hash probe's published cost for safe Rust over unsafe Rust is `+2`
instructions per call, on both inputs**. Now rewrite the *unsafe* side instead:
the shipped kernel plus one extra sub-slice, still meeting the contract and still
passing the same-machine-code rule. The cell
reads **`+125`** on the small input and **`+1021`** on the large, safe side
untouched. Against the published `+2` that is 62.5× on the small input and
**510×** on the large. Every source in the tree prints the 510
\src{results/synthesis.md}; quoting it as a constant is the error. Rewriting
one side also reverses the **sign** on exactly two programs, one on both inputs
and one on the large only.

%% C23 bullet 3 / E4 §A3.  Exactly two: one flips on both blobs, one on large
%% only.  Pattern IDs stay out of the prose per CLAIMS.md §3.3.
%% ⚠⚠ CUT PASS (.temp/brief/CUT.md): "Cut the sign-flip beat to one clause inside
%% another sentence." It is now the last clause of the paragraph above, ~40 prose
%% words lighter. WHAT WENT: "Neither rung was re-shipped", and the exclusion of
%% the third program — different quantity, different table, and not a pair we may
%% subtract. CLAIMS.md §1.2 records "the sign flips on p12, p13 and p42" as a
%% claim a draft actually made, and the surviving clause says **exactly two**,
%% which is the form §1.2 licenses; what is lost is the READER's ability to check
%% the exclusion, not the claim. RESTORE THE THREE REASONS FIRST if words come
%% back here, in one sentence, because the third program's reversal is a
%% published span's endpoints in a different table and it will be counted again.

%% ⚠⚠⚠ THE THIRD UNDERGRADUATE PASS: **THE `Rewrite the safe side` SUBSECTION IS
%% CUT ENTIRELY**, ~73 prose words with its heading.  This is the ruling's "cut
%% ONE of section 3's demonstrations" and it is the one that went; the reader
%% scored this file **3**, the joint-lowest in the paper, and the diagnosis was
%% not the writing but the count: "It has four demonstrations of 'the number moves
%% if you rewrite one side' (hash probe, 7.26×, the same-machine-code rule, the C
%% column).  §1 had already made that point."
%% WHAT IT SAID, in full, so it can be restored verbatim in substance:
%%   "**The safe side moves at least as much, and not for a safety reason**.  The
%%    mechanically ported version — the one written first — sits a median
%%    **7.26×** further above the unsafe version than the tuned rewrite does.
%%    That is a ratio of two gaps, not two totals.  The median is over 17 pairs:
%%    22 of our \num{totals.patterns} pairs are fair to subtract, and 17 of those
%%    also have a positive gap on the large input \src{results/SYNTHESIS.md}."
%% ⚠⚠ WHY THIS ONE AND NOT THE HASH PROBE, which is where the reader says they
%% would actually have quit.  The hash probe is WELDED TO §2: §2's population
%% sentence states the ten as "nine as shipped, plus a hash probe whose in-contract
%% unsafe respelling moves it from `+2` to `+125`", \refs this section for it, and
%% its table caption says the row is drawn "at the respelling named above".  Cut
%% the probe and §2's ten loses its explanation and its pointer.  The 7.26× has no
%% such tie: nothing \refs it, §0 is FORBIDDEN to print it, and CLAIMS.md mandates
%% no figure from it.
%% ⚠⚠ THE FINDING IS NOT LOST FROM THE PAPER, which is the other half of why this
%% was the affordable cut.  §2 prints a WORKED safe-side rewrite in the same
%% direction and larger — the bitset's shipped safe rung respelt in contract, from
%% `+13,756` to `+263` — and §1's opening prints a safe fold at `chunks_exact(64)`
%% that beats the unsafe rung outright.  So the section's opening now cites BOTH
%% neighbours ("\ref{sec:onekernel} moved one of the two, and \ref{sec:notthecheck}
%% the other"), which is what keeps "Both move" carrying its own weight after the
%% cut.  ⚠ IF THE OPENING'S SECOND \ref IS EVER REMOVED, THIS BEAT COMES BACK.
%% ⚠⚠ WHAT IS GENUINELY LOST, priced for whoever restores it: this was the only
%% CORPUS-WIDE statement that the safe side moves — a median over 17 pairs rather
%% than two instances — and C23 bullet 1 is its ruling.  Restore it FIRST of
%% everything cut from this file, with BOTH conjuncts of the population (fair to
%% subtract, and positive on the large input), which is what C23 protects, and
%% with the median over **17**, never 22 (`results/SYNTHESIS.md:195-197`, and the
%% first undergraduate pass corrected exactly that error).
%% ⚠ THE `not two totals` CLAUSE WENT WITH IT, which is also the third of the
%% three bolded "not X" pre-emptions the reader read as talking down.  Two are now
%% gone (this one and §0's "not a range"); the survivor is the negatives clause in
%% the C-column beat below, which the reader said was "doing real work".

%% C23 bullet 1, verified to the digit in E4 §A1 and read first-hand at
%% `results/SYNTHESIS.md:195-210`.  THE POPULATION IS TWO INDEPENDENT CONJUNCTS
%% and both are still in the prose, one clause each: the licence is a
%% DISASSEMBLY property (the two cells make the same calls out of the kernel —
%% §2 states that mechanism, this file gives the plain form "fair to subtract"),
%% the sign is a MEASUREMENT.  Two denominators, reasoning from the smaller
%% (convention 2.7).
%% ⚠⚠ "Quote the median, not the range" is VERBATIM at `SYNTHESIS.md:207-208`,
%% and the reason is at `:201-204` — the old range's low was a NOT-LIC row the
%% median's own rule excludes, so the two statistics were taken over two
%% different populations.
%% ⚠⚠ CUT PASS (.temp/brief/CUT.md): "the 7.26× median in ONE SENTENCE". The
%% beat is now one sentence and the second one went: *"We give the median and not
%% the range: an earlier median and range had been taken over two different sets
%% of rows."* ~20 prose words. That sentence was the reader's only way to check
%% WHY the range is absent, and the two conjuncts that define the population —
%% fair to subtract, and positive on the large input — are both still in the
%% surviving sentence, which is what C23 protects. RESTORE IT if words come back
%% here; it is the cheapest restoration in this file.
%% ⚠⚠⚠ CUT PASS (.temp/brief/CUT.md), TWO WHOLE BEATS, ~125 prose words, and
%% both cuts are rulings rather than trims.
%%
%% 1. THE BUCKET DISTRIBUTION IS CUT ENTIRELY. "`9/4/9 → 7/3/10`, the
%%    not-a-partition warning and the coincidence are pure internal bookkeeping —
%%    this is where the practitioner reviewer stopped reading. The finding it
%%    serves is already made by the endpoint examples."
%%    WHAT IT SAID: our bucket labels for these rows move at all four searched
%%    values on record and were never a partition — one program falls in two
%%    buckets, one in none, so 9+4+9 = 22 is a COINCIDENCE and not a
%%    redistribution of a fixed total (`SYNTHESIS.md:153-155` says so in its own
%%    voice); \ref{sec:notthecheck}'s tally survives every threshold swept while
%%    these labels do not; and the search behind them is one-sided BY
%%    CONSTRUCTION, two R3-side levers being on record and unapplied in arm C
%%    (`SYNTHESIS.md:180-186`).  E4 §A4 / C23 bullet 4.
%%    ⚠ IT TOOK THE **F2** CITATION WITH IT — the one contrast the redundancy map
%%    allowed this file to draw between the sweep's stability and the labels'
%%    instability. §2 still owns and prints the sweep; nothing else here needed
%%    the pointer. RESTORE THE ONE-SIDED-SEARCH SENTENCE FIRST: it is C12's own
%%    finding in this file, and it is the only place the two unapplied R3-side
%%    levers appear.
%%
%% 2. THE `caveat{The sentence we will not write}` IS CUT. "Its rule survives in
%%    section 6." WHAT IT SAID: fourteen of 26 rows print `undeclared` in the
%%    column that records spelling searches; *fourteen of twenty-six rows were
%%    never searched* would strengthen everything above, and it is false; an
%%    `undeclared` means nobody wrote an entry and the tree says in as many words
%%    that it has never meant nobody searched; the column itself was wrong by four
%%    rows one task ago (TASK_112, and the error ran toward understating the
%%    record); the count bounds nothing. Verified verbatim at
%%    `results/synthesis.md:641` and `:668`; C23; CLAIMS.md §1.22.
%%    ⚠ THE CORRECTION IS NOT LOST. §2's caveat states it on its own denominator
%%    — six of ten, all three check rows — and says `undeclared` means nobody
%%    wrote an entry and has never meant nobody searched. THIS box was the
%%    reader's THIRD meeting with those epistemics; §2's is the second and it is
%%    the one attached to the numerator that matters.
%%    ⚠ WHAT IS LOST, and it is the reason to restore this first if a standalone
%%    caveat is ever affordable again: 14 of 26 appears NOWHERE ELSE in the paper,
%%    and convention 2.8's "name the sentence you will not write" has no other
%%    exhibit in ver_C — this one was its best, because the false sentence would
%%    have STRENGTHENED the section that printed it.
%%    ⚠ It also carried the second `(**F3**)` citation, and old F3 no longer
%%    exists: the summary's ten findings became six by the same ruling and the
%%    least-recorded finding moved to §2's caveat.

\subsection{The side we hold up, and it flatters us}

%% ⚠⚠ C23's identity-pin bullet, E4 §A7, re-read first-hand at
%% `results/SYNTHESIS.md:57-70` and `patterns/p11-nul-scan/NOTES.md:948-953`.
%% The mechanism is now glossed in plain words FIRST and named nowhere: "we
%% require the proved version to compile to exactly the same machine code as the
%% unproved one" is PLAIN.md's own wording for `identity pin`, and the cold
%% reader could not parse the old sentence at all.
%% ALL THREE corrections are present and none is optional:
%%  (1) SAVING FORGONE, not cost imposed — the column is candidate minus shipped,
%%      so -17526.22 means the candidate is CHEAPER.  The rule refuses a
%%      subtraction; it adds no instructions.
%%  (2) LARGE-BLOB-ONLY — `small - R4` is +3447.56, so on the small blob the
%%      pinned rung is the cheaper one.  Mechanism at `.memory/01-ladder.md:1445`:
%%      the row changes sign at string length 17-18, at memchr's 16-byte
%%      threshold, and the two blobs sit on opposite sides of it.
%%  (3) NOT GATE-CERTIFIED — no gate record carries a mutant result, and the
%%      producing script was scratch, now deleted.  Both endpoints it is quoted
%%      AGAINST are gate data.
%%      ⚠ THIS NOTE USED TO SAY "`controls_json` is `{}`" FULL STOP, and the
%%      fact-check found that is no longer true: `results/gate/p23-partition.json`
%%      now carries `controls_json: {"sweep_fit.json": "FRESH"}`, the other 25
%%      being empty.  That entry is a freshness verdict on a control artefact, not
%%      a mutant result, so the substantive claim survives verbatim — but the
%%      premise as written was false and is the kind a later agent re-uses.
%%      CONVENTIONS.md §1 rule 12 states it the old way and needs the same fix;
%%      that file is not mine to edit.
%% ⚠ A CORRECTION THE RULINGS DO NOT CARRY: `SYNTHESIS.md:62-64` says the unsafe
%% class "cannot reach it at all".  That sentence is RETRACTED —
%% `.memory/04-verus.md:1475-1482`, the authoritative layer, rules that the
%% unsafe class DOES reach `core::slice::memchr`, at four hand-written axioms no
%% gate stage checks.  So this passage says the rule FORBIDS the spelling and
%% never that the prover cannot express it.  The finding stands; only the reason
%% moved.  35% is 17526/50174 against the gate's `unsafe/O3/isolated/large.bin`.
%% ⚠ rigour M14: "every unsafe rung is pinned BYTE-IDENTICAL" is a universal
%% CLAIMS.md §1.19 refutes — on one pattern a trait-declared ghost function is
%% codegenned as a vtable stub, 40 bytes against 32, and the executed count is
%% still zero.  §6.4 cited an exception §1 never documented; its \ref points here,
%% so the exception must stay in this passage.  It is now its own sentence at the
%% end, where it cannot swallow the finding.
%% ✅ THE PUBLISHABLE SENTENCE is the second paragraph, and it is the title's
%% second clause.  Wording from C23's "consequence is the one to publish" and
%% `SYNTHESIS.md:66-70`, and PLAIN.md's example 5 is this passage.  Stated flat,
%% no hedge after it: the OUTLINE says do not soften it.  The closing line is
%% `SYNTHESIS.md:69-70`'s own move — the finding is about the instrument, not
%% about which language won (CONVENTIONS.md §0.6).
We require the proved version of each program to compile to *exactly* the same
machine code as the unproved one; \ref{sec:onekernel} says what that buys. It has
a price: it rules out some faster ways of writing the unsafe version. On a NUL scan
the ruled-out way was **17,526 instructions per call cheaper, about 35% of that
kernel, on the large input** \src{patterns/p11-nul-scan/NOTES.md}.

So our unsafe baseline is slower than it needed to be, and **every
safe-minus-unsafe figure here is measured against it, so it reads more kindly to
safe Rust than the program warrants** (**F3**). Not that safe Rust is cheaper:
that our instrument is biased, one direction, on every row.

Three qualifications.

- A **saving refused, not a cost added**: the rule blocks a subtraction, it adds
  no instructions.
- Large input only. On the small input the pinned version is cheaper, by 3,448.
- No gate certifies it, though both figures it is set against are gate data.

The rule holds byte-for-byte on every program but one, where a function existing
only in the proof still takes a slot in a table of function pointers; no extra
instruction runs there either. It is also why proved minus unsafe is zero here:
that zero is enforced, not found.

\figure{identity}{What the same-machine-code rule certifies, and so what it forbids.}
\label{fig:identity}

%% E4 §A6.  The three precision requirements, all present:
%%  (a) 6.0000 is the DELTA per probe, not what the safe spelling pays — R3's own
%%      slope is ~18.5035 and R4's ~12.5035 (`p07/NOTES.md:381-385`).  The prose
%%      says so in its own short sentence rather than in an appositive.
%%  (b) JOINT-dearest, tied with `r3_getunwrap` at identical Ir on both blobs
%%      (`NOTES.md:888-896`).  "The dearest of four" is wrong.
%%  (c) ⚠⚠ 5 per probe and the "about a sixth" have ZERO grep hits in the tree.
%%      They follow from the documented 1.0000/probe span, which rests on TWO
%%      shipped blobs while the 6.0000 rests on the 113-blob sweep.  The
%%      paragraph MARKS THE SUBTRACTION AS OURS, in bold, per C23.
%% ⚠ E2 §4.1 adds a pairing the rulings omit and `p07/NOTES.md:511-518` makes it
%% a rule, in its own words: "A 46% instruction tax that is worth 1.6% of time
%% on the input where the kernel actually spends its time is not the same
%% statement as a 46% *cost*, and NEITHER NUMBER MAY BE QUOTED WITHOUT THE
%% OTHER."  +13.0% `small`, +1.6% `large`.  `SYNTHESIS.md:368-377` drops it; we
%% do not, and the counterweight is printed HERE — an earlier comment claimed it
%% was already carried when it was printed nowhere in the paper, so do not delete
%% it on the strength of a comment.
%% ⚠⚠ AND THE WITHDRAWAL DOES NOT EXCUSE DROPPING IT.
%% `.memory/03-measurement.md`'s 31-layout withdrawal covers **R2's** two `ns`
%% cells (bimodal at +26.42% / −0.93% by code layout).  `p07/NOTES.md:206-209`
%% explicitly PRESERVES R3's: "R3's two `ns` cells survive, and they are the ones
%% to quote… `safe_tuned` is slower than `unsafe` at 30 of 30 layouts on
%% `small`", mode-matched at +11.12% / +17.37% and +0.85% / +2.52%.  `:204` adds
%% that the withdrawal "does not touch the `Ir` half".  This is R3−R4; there was
%% never any ground to drop it.
%% ⚠ FINAL CUT, ~26 words, all of it wording rather than fact.  Every one of E4
%% §A6's three precision requirements is still here: (a) 6.0000 is the DELTA per
%% probe and not what the safe spelling pays — R3's own slope is ~18.5035 and
%% R4's ~12.5035 — and the prose still says so; (b) JOINT-dearest, tied with
%% `r3_getunwrap`, never "the dearest of four"; (c) the five-per-probe
%% subtraction is MARKED AS OURS, in bold.
%% ⚠ WHAT WENT: "That pattern's notes forbid quoting either without the other."
%% The rule is discharged by OBEYING it — both figures are printed, in one
%% sentence — and the sentence was the paper telling the reader about a source
%% file.  `p07/NOTES.md:511-518` still says it, in its own words, and a later
%% editor who separates the two figures is breaking it.  ⚠ DO NOT SPLIT
%% +13.0% AND +1.6%.  ⚠ Nor may the wall-clock half be dropped as "withdrawn":
%% `.memory/03-measurement.md`'s 31-layout withdrawal covers R2's `ns` cells;
%% `p07/NOTES.md:206-209` explicitly PRESERVES R3's, and this is R3−R4.
%% ⚠⚠⚠ THE FINAL CUT: **"OUR OWN WORST NUMBER" — THE BINARY SEARCH'S PAIR — IS
%% CUT**, ~106 prose words, and its WALL-CLOCK HALF IS MOVED rather than dropped
%% (it is now the last sentence of the clock subsection below).
%% WHAT WENT: "Our own worst number.  A binary search's shipped safe version is
%% the **joint-dearest** of the four we tried that fit the contract, costing
%% `6.0000` more instructions per probe than the unsafe version over a 113-input
%% sweep.  That six is the gap, not what the safe version pays.  The cheapest we
%% found sits `1.0000` instruction per probe below the shipped one
%% \src{patterns/p07-binary-search/NOTES.md}.  **We did that subtraction
%% ourselves, and neither figure is in the tree**: the tax is five per probe, and
%% \ref{sec:notthecheck}'s 42.5–46.6% kernel share falls by about a sixth."
%% ⚠ WHY THIS ONE.  It was the FOURTH instance of a finding this section already
%% makes three times — rewrite the unsafe side (the hash probe), rewrite the safe
%% side (7.26×), hold one side up (the identity pin).  And the fact it carries is
%% NOT LOST: §2's caveat states in its own words that both check rows quoted
%% there hide a search, "one worth about 15% of its row and one worth 98%", and
%% the 15% is exactly this row.  What is lost is the WORKED subtraction and the
%% "we did it ourselves, neither figure is in the tree" marking.
%% ⚠⚠ IF IT IS RESTORED, E4 §A6's three precision requirements come back with it,
%% and none is optional: (a) 6.0000 is the DELTA per probe, not what the safe
%% spelling pays — R3's own slope is ~18.5035 and R4's ~12.5035
%% (`p07/NOTES.md:381-385`); (b) JOINT-dearest, tied with `r3_getunwrap` at
%% identical Ir on both blobs (`NOTES.md:888-896`) — "the dearest of four" is
%% wrong; (c) the five-per-probe figure and the "about a sixth" have ZERO grep
%% hits in the tree and MUST be marked as our subtraction, in bold.
%% ⚠⚠ THE CLOCK PAIR DID NOT GO WITH IT, and it may not be split.
%% `p07/NOTES.md:511-518`: "A 46% instruction tax that is worth 1.6% of time on
%% the input where the kernel actually spends its time is not the same statement
%% as a 46% *cost*, and NEITHER NUMBER MAY BE QUOTED WITHOUT THE OTHER."  Both
%% +13.0% and +1.6% now sit in one sentence at the end of the clock subsection,
%% which is also what keeps §2's "\ref{sec:bothends} puts a clock on them" true
%% of BOTH magnitudes §2 prints.

\subsection{C gets its own safety cost wrong the same way}

%% C21, and this beat is partly an ANTIBODY (CONVENTIONS.md §0.6): a C-column
%% finding with the same shape as the Rust-column ones, which is why this
%% section is not a Rust story.  All four of C21's ✅ examples ship.
%% ⚠⚠ CUT PASS: THIS SUBSECTION IS NOW THE FINDING'S ONLY HOME. The summary went
%% from ten findings to six (.temp/brief/CUT.md) and the hardening median — old
%% **F4** — was dropped from it "to section 3". So the `(**F4**)` citation that
%% closed this paragraph is gone: under the new numbering F4 is the
%% remove-and-re-measure finding, which is a different claim. NOTHING ELSE IN
%% THIS BEAT MOVED, and its four C21 examples may not now be trimmed — the ranked
%% cut list at the top of this file offers them, and that offer is WITHDRAWN,
%% because a reader who never sees §0 on this subject has only this paragraph.
%% ⚠ §5's takeaway and §6.1's hardening bullet used to cite **F4** for this
%% finding; both now point at \ref{sec:bothends} instead.
%% ⚠ THE MEDIAN'S UNIT: 24 reproduces only by pooling both inputs — 50
%% (pattern, blob) cells, NOT 25 patterns; per pattern it is 17/19 small and
%% 41/54 large (E4 §B12).  Both compilers land on 24 and the claim attributes it
%% to neither, so that is said.
%% ⚠ NEGATIVES, AND THE METRIC IS NAMED (mandatory, C6 and C21): three under
%% kernel-exclusive `Ir` — "counted inside the kernel" — and FOUR under
%% `marginal_ir_per_call` — "counted across the whole program".  The RULE that
%% `.memory/03-measurement.md:654-655` makes the marginal the one to publish on
%% disagreement is a counting rule and lives here, not in the sentence.
%% ⚠⚠ The maxima are not checks: the largest is 2048 table entries x 5.00 Ir
%% under gcc, 2.75 under clang — a whole extra O(table) validation pass.
%% ⚠⚠ "SIX of the eight largest price a different program" DOES NOT REPRODUCE
%% and is gone (fact-check §1.1).  E4:1288 asserted it without deriving it and
%% the paper inherited it.  Ranking all 100 (pattern, blob, compiler) hardening
%% cells at `-O3 isolated` gives, in order: the state machine's four cells
%% (10242 gcc x2, 5637 clang x2), then a hash probe at 5120, a vtable dispatch
%% at 4096, a bitset at 2490, a vtable dispatch at 2047.  "Different program" in
%% the top eight is FOUR — all four of them the state machine's — and five under
%% the marginal metric, never six.  I re-derived this ranking myself from
%% `results/p*.json` before rewriting the clause, and the two rows that would
%% have to be reclassified to reach six are single conjuncts their own sources
%% call the only difference from the plain rung.  §0's F4 and §6.1 took the same
%% correction.  The argument is unharmed: the largest cell is still a pass over a
%% table and still not a check.
%%literal-ok 108  clang's hardening minimum, not `totals.tcb_items`
%% ⚠⚠⚠ THE FINAL CUT: "Compress the C-column subsection to three sentences."
%% Executed at five short ones and ~26 prose words lighter, which is as far as
%% CLAIMS.md §1.5 permits.  That entry is explicit that the claim which survives
%% needs the MEDIAN 24, the RANGE −125…+10,242 gcc / −108…+5,637 clang, and the
%% NEGATIVES — "hardened C costs +5/+12 instructions, flat" is true of ONE
%% pattern and is on the do-not-claim list.  C6 and C21 additionally make NAMING
%% THE METRIC on the negatives mandatory (three counted inside the kernel, four
%% counted across the whole program), so that clause is not available either.
%% WHAT WENT, in restore order: (1) two of C21's four per-event examples — the
%% bounded stack's `+2` per pop, and "per-call totals then grow only with the
%% event count"; (2) the validation pass's per-entry rates, `5.00` gcc and `2.75`
%% clang, leaving the table size.
%% ⚠⚠ THIS SUBSECTION IS STILL THE HARDENING FINDING'S ONLY HOME — §0 no longer
%% carries the median, and §5's takeaway and §6.1's hardening bullet both \ref
%% here.  It may not be cut further without a ruling that gives the finding
%% another home.
%% ⚠⚠ "SIX of the eight largest price a different program" DOES NOT REPRODUCE and
%% must not come back (fact-check §1.1).  Ranking all 100 (pattern, blob,
%% compiler) hardening cells at `-O3 isolated`: the state machine's four cells
%% (10242 gcc x2, 5637 clang x2), a hash probe at 5120, a vtable dispatch at
%% 4096, a bitset at 2490, a vtable dispatch at 2047.  "Different program" in the
%% top eight is FOUR, and five under the marginal metric.
**None of this is a Rust story.** *Hardening* means
adding to C, by hand, the check plain C leaves out. Where that adds one
comparison per event and nothing else, it costs single digits: `+5` under gcc,
`+12` under clang, on a buffer copy. Across the 25 programs shipping a hardened
version, over both inputs of each, the median is 24 instructions per call under
either compiler. The spread around it is enormous: −125 to +10,242
under gcc, −108 to +5,637 under clang. Negative means hardening ran *fewer*
instructions. Counting inside the kernel that happens on three programs; counting
across the whole program, on four — two counting methods, not seven
programs. **And the biggest
numbers are not checks**: the largest is a
whole extra validation pass over a 2,048-entry table, and one program owns four
of the eight largest cells here.

\subsection{The clock and the counter can disagree about direction}

%% C23's wall-clock bullet, E4 §A8, re-derived here from
%% `results/p02-buffer-copy.json`: gcc 175 300 000 / 20 000 = 8765.0 and clang
%% 195 280 000 / 20 000 = 9764.0 Ir/call; wall min 0.0309735 s vs 0.0251860 s at
%% reps = 30 — 10.2% fewer instructions, 23.0% longer.
%% ⚠ THE COMMITTED RECORD IS 30.97 / 25.19 AT 30 REPS.
%% `.memory/03-measurement.md:403-409`'s "30.8 vs 25.0, min of 15" has no
%% committed cell behind it, so it is an uncommitted 15-rep side probe.
%% ⚠⚠ ver_B's `50-cantsay.md` gave this pattern a NAMED MECHANISM — "callgrind
%% counts a `rep`-string instruction once per repetition".  THAT IS ANOTHER
%% PATTERN'S mechanism, and `.memory/03-measurement.md:425-436` EXPLICITLY RULES
%% IT OUT here (glibc memcpy stays on the vector path below 8192 B; these copies
%% are 4092 B).  The pair is unexplained and the prose says exactly that.
%% ⚠ Whole-process wall means the true kernel-time disagreement is LARGER.
%% ⚠ C21's counterweight: the rotate's clang hardened rung is -45.00 / -108.00 Ir
%% and +9.78% / +10.56% ns, all four surviving a 30-layout population
%% (`p06/NOTES.md:366-376`).  ⚠ `SYNTHESIS.md:996` says "10-20% slower"; the
%% pattern's own figures are 9.78-11.60%, so the pattern's own figures are used.
%% CLAIMS.md §3.10: no sentence here ranks two rungs by time.
%% ⚠⚠⚠ THE FINAL CUT: "Keep ONE wall-clock counterexample, not three."  This
%% whole paragraph is cut, ~85 prose words, and the three bullets below it are
%% cut with it; the subsection is now the agreeing case plus one disagreeing one.
%% ⚠⚠ WHICH ONE SURVIVES IS NOT FREE CHOICE.  The must-not-lose list pairs §2's
%% check magnitudes with "at least one wall-clock result showing INSTRUCTION
%% COUNTS CAN OVERSTATE THEM", and says dropping either alone re-creates a
%% documented bias.  Of the three counterexamples only the bounded stack runs
%% that way — more instructions, less time — so it is the one kept.  The two cut
%% here both run the other way (fewer instructions, MORE time).  The binary
%% search's +13.0% / +1.6% pair, four paragraphs up, is a second instance of the
%% surviving direction and is welded there.
%% WHAT WENT, in restore order:
%%  (1) THE COMPILER PAIR.  On identical C source one compiler ran **10% fewer
%%      instructions and took 23% longer** — 8,765 against 9,764 instructions per
%%      call, 30.97 against 25.19 ms as the best of 30 repetitions, re-derived
%%      here from `results/p02-buffer-copy.json` (175 300 000 / 20 000 = 8765.0
%%      gcc; 195 280 000 / 20 000 = 9764.0 clang; wall min 0.0309735 s vs
%%      0.0251860 s at reps = 30).  ⚠ THE COMMITTED RECORD IS 30.97 / 25.19 AT 30
%%      REPS; `.memory/03-measurement.md:403-409`'s rounder "30.8 vs 25.0, min of
%%      15" has no committed cell behind it and is an uncommitted side probe, so
%%      any restoration must carry the sentence saying so.
%%      ⚠⚠ AND THE PAIR IS UNEXPLAINED.  ver_B's `50-cantsay.md` gives it a NAMED
%%      MECHANISM — "callgrind counts a `rep`-string instruction once per
%%      repetition" — which is ANOTHER PATTERN'S mechanism;
%%      `.memory/03-measurement.md:425-436` explicitly rules it out here (glibc
%%      memcpy stays on the vector path below 8192 B; these copies are 4092 B).
%%      Never restore it with a mechanism attached.
%%  (2) C21's ROTATE COUNTERWEIGHT: the cheapest hardening here by instruction
%%      count, `−45` and `−108` instructions per call, costs `+9.78%` and
%%      `+10.56%` on the clock, all four surviving a 30-layout population
%%      (`p06/NOTES.md:366-376`).  ⚠ `SYNTHESIS.md:996` says "10-20% slower"; the
%%      pattern's own figures are 9.78–11.60%, and the pattern's own figures win.
%%  (3) THE WALKER'S NULL: \ref{sec:onekernel}'s kernel runs about 70% more
%%      instructions in its ported version, with all sixteen `-O3` timings inside
%%      a 1.3% band in one quiet session — and a later re-timing of the same
%%      binaries can NEITHER reproduce that band NOR refute it
%%      (`p16/NOTES.md:306-327`: the TASK_035 re-measure reads 12.28–13.28 ms,
%%      four `small` cells exceed the 10% min-to-median threshold and are
%%      DISCARDED, and the within-cell spread exceeds the between-cell band).
%%      BOTH HALVES of that last clause must travel together on any restoration.
%%  (4) THE RANGE PARSER'S NULL: a `+73%` tax landing inside a 1.1% band
%%      (`p17/NOTES.md:518-541`).
%% ⚠ The "whole-process minima" limitation is NOT lost — it is welded into the
%% surviving paragraph, and it still ships its DIRECTION (a kernel-only
%% disagreement would be larger, not smaller), which is CLAIMS.md §3.5.
%% ⚠ CLAIMS.md §3.10 still binds on what remains: no sentence ranks two rungs by
%% time, and "faster"/"slower" is not used as a cost verb.

%% ⚠⚠ RULING C34(b) AND (d), AND BOTH DIRECTIONS GO IN TOGETHER.  The
%% coverage-bias review found that the paper under-reports the check's magnitude
%% AND under-reports the evidence that instruction counts overstate it in time.
%% Fixing only the first would make the paper worse, so the agreeing case and
%% the disagreeing ones are one passage.  §2's table carries the magnitudes; this
%% is where the clock rules on them.
%% Sources, each read first-hand: p09/NOTES.md:436-455 (kernel-only ns
%% +205.4…+219.7% on `small` against +205.6% `Ir` — "no discount at all", and
%% the ILP excuse explicitly REFUTED; on `large` it keeps a 1.1x discount, which
%% is why the sentence names the blob); p16/NOTES.md:288-303 (all 16 `-O3` cells
%% within 1.3% and 0.9%, against a run-to-run spread of 1.2–1.3%);
%% ⚠⚠ THE p16 BAND IS SCOPED, and that scoping is an over-correction running the
%% OTHER way — a figure printed above its own record's confidence because it
%% supported the passage it sat in (second bias review §5.2).  `p16/NOTES.md:306-327`,
%% which I opened: the 1.3% reading is the TASK_007 quiet session's; a TASK_035
%% re-measure of the SAME binaries reads 12.28–13.28 ms (8.2%), **four `small`
%% cells now exceed the 10% min-to-median threshold and are DISCARDED**, and
%% "in the new session the within-cell spread exceeds the between-cell band, so
%% it cannot resolve 'all 16 cells within 1.3%' either way — **it does not
%% refute it**."  BOTH HALVES of that last sentence are in the prose, because
%% "unreproducible" would be as wrong as the flat statement was.  The
%% DETERMINISTIC half of the null (+72% `Ir`, written "about 70% more") is
%% untouched and is not scoped.
%% p17/NOTES.md:518-541 (spreads 1.1% and 1.8%, R2 faster on both blobs);
%% p03/NOTES.md:1433-1437 (−7.43/−14.69/−8.76/−14.73%, no sign flip, P(A>B)
%% 19.1/19.5%).  ⚠ p03's `large` R3-vs-R4 comparison is a NULL — the sign flips
%% between modes — so the sentence names `small` only.  ⚠ All four are
%% whole-process minima, which is the same limitation as the pair above.
%% ⚠ CLAIMS.md §3.10 forbids "faster"/"slower" as a cost verb; these sentences
%% report a measured clock, name the unit, and rank nothing across patterns.
%% ⚠⚠ THE COMPILER PAIR SURVIVES AS ONE CLAUSE, and it is NOT optional after the
%% cut above.  C34(d) requires both directions to ship together, and §0's scope
%% paragraph says in as many words that the counter and the clock disagree "in
%% both directions, and the report prints both".  With the compiler pair and the
%% rotate both cut as beats, every surviving instance ran ONE way — instructions
%% overstating time — so the section would have contradicted its own summary.
%% The clause below is the other direction, at 20 words instead of 85.  ⚠ IT
%% CARRIES NO MECHANISM: ver_B named one ("callgrind counts a `rep`-string
%% instruction once per repetition") and it belongs to a different pattern;
%% `.memory/03-measurement.md:425-436` rules it out here.  ⚠ The committed record
%% is 30.97 / 25.19 ms at 30 reps; the rounder figures in circulation are an
%% uncommitted 15-rep probe.  Do not restore either.
**The disagreement has no fixed direction, which is why we print both**. On
identical C source gcc ran 10% fewer instructions than clang and took 23% longer,
and we cannot explain it. Where the check dominates, the clock agrees: a bitset's
tuned safe version costs `+205.6%` of its unsafe kernel in instructions and
`+205.4…+219.7%` on the clock, on the small input. No discount at all, and that pattern's own notes refute the
excuse that the extra instructions are cheap ones. Where it
does not dominate, the clock can reverse the sign: on one bounded stack's small
input the safe version runs 7–15% quicker while executing 11.96% more
instructions.

And the binary search's 42.5–46.6% instruction tax is worth **+13.0%** of the
time on the small input and **+1.6%** on the large, where the kernel spends its
time.
%% ⚠⚠ THIRD UNDERGRADUATE PASS, ~11 words: "That pattern's notes forbid quoting
%% either of those without the other."  The cut was already RULED and recorded in
%% the note above — "the rule is discharged by OBEYING it … the sentence was the
%% paper telling the reader about a source file" — and the sentence had survived
%% the ruling.  ⚠⚠ THE RULE STILL BINDS AND IS STILL OBEYED: `p07/NOTES.md:511-518`
%% says "NEITHER NUMBER MAY BE QUOTED WITHOUT THE OTHER", and both figures are in
%% the one sentence above.  ⚠ DO NOT SPLIT +13.0% AND +1.6%.

All of these are best-of-30 interleaved repetitions, timed over the whole
process, so a kernel-only disagreement would be larger, not smaller. There
is no cross-pattern timing column here and no hardware counter on this machine.

\figure{spread}{The same comparisons over builds that produced identical machine code; the band is their spread.}
\label{fig:spread}

%% PROTECTED.  Carried from ver_B `20-cost.md` — three reviewers named it
%% load-bearing — with C23's "cheapest found, never minimum" clause in its
%% CORRECTED count: five published minima across three patterns, plus two more
%% elsewhere.  ⚠ "Four patterns' published minima" is the stalest version and
%% the tree disagrees with itself four/five/five/six across six sources; they are
%% minima, not patterns (E4 §A6).
\begin{principle}{Publish the pair, and name the side you did not search}
**A safety-cost number needs three parts: the number, the two versions it is the
difference of, and which of those two anyone tried to make fast**. Without the
other two it is a bound with one end held up by decree. Never subtract two
cheapest-found versions from each other. And write *cheapest found*, never
*minimum*: five published minima have been retracted here across three patterns,
plus two more elsewhere.
\end{principle}

%% Convention 2.5 — [scope] + [claim], no implication — with the outline's
%% amendment that every findings section ends in one takeaway pointing at the §6
%% subsection that spends it.  No number in it is new.
%% ⚠ FINAL CUT, ~14 words: the takeaway is one sentence.  "Both sides move" is
%% the section title and the opening line; the three-orders-of-magnitude figure
%% is the hash-probe beat two screens up.  The claim and the pointer both stand.
\begin{takeaway}
Both sides move, and our own rule holds one of them above its floor.
\ref{sec:measure} §"If you are publishing a number" says what to do.
\end{takeaway}

\subsection{Why the next half needs a word and this one did not}

%% ⚠⚠ THE JOIN.  RULING C32 and rigour B1, and the version before it failed on
%% five counts, all checkable against this document:
%%  (a) "The next half cannot run it" is FALSE, and §4 does it eighty lines
%%      later — the fortification finding, the thing §4's title promises, was
%%      found by flipping a hardening flag and re-measuring, which is one of the
%%      levers this very sentence lists.  So are the range parser's one-line
%%      change and the ghost ledger's planted line.
%%  (b) "at least six times" had NO SOURCE.  Deleted, not repaired: a census with
%%      a stated rule would be a finding, and nobody has run one.
%%  (c) the four "levers" were five different operations, only one of them a
%%      removal — a spelling is a SUBSTITUTION, a compiler is a swap this
%%      section calls unexplained, the same-machine-code rule removes a
%%      certification constraint and not a cost term.  Calling them one operation
%%      is the conflation §2 spends a section warning against, so the prose says
%%      "varies one thing", never "removes".
%%  (d) "it settles the attribution" full stop is contradicted by §2's own
%%      principle: a null is uninterpretable in BOTH halves, and the only reason
%%      it does not bite here is that this corpus happens to contain no zero.
%%  (e) "this half needed no vocabulary" is false of a half that glosses `rung`
%%      and legislates wording in bold.  C32: write "coined no new noun", which
%%      is true and checkable.
%% ✅ THE HONEST ASYMMETRY IS ABOUT THE INSTRUMENT, NOT THE OPERATION.  Half A's
%% observable is a scalar; Half B's is a boolean; a null tells you less there
%% than a zero does here — so Half B ALSO has to name the resource, not instead.
%% That keeps the transition, keeps `resource` a consequence rather than a
%% coinage, and stops §4's own headline being a counterexample to this section.
%% §4's opening bridge is written to match.
%% This is the ONE licensed appearance of `resource` outside §4 and §6.4.
%% ⚠⚠ THE FINAL CUT: "Compress the join to two [sentences]."  Executed at four
%% short ones, ~15 prose words lighter; two would have run past 35 words each.
%% ⚠ EVERY ONE OF C32's FIVE CORRECTIONS SURVIVES, and they are why this passage
%% cannot be compressed by rephrasing:
%%  (a) it does NOT say "the next half cannot run it" — §4's own headline finding
%%      was found by flipping a hardening flag and re-measuring;
%%  (b) no "at least six times", which had no source;
%%  (c) "varies one thing", never "removes" — a spelling is a SUBSTITUTION and a
%%      compiler is a swap this section calls unexplained;
%%  (d) the null clause, because §2's principle says a null is uninterpretable in
%%      BOTH halves;
%%  (e) the honest asymmetry is about the INSTRUMENT — scalar here, boolean there
%%      — which is why the next half must ALSO name the resource, not instead.
%% ⚠ WHAT WENT: "This half coined no new noun; the next needs exactly one."  It
%% is C32's own true-and-checkable replacement for a false sentence, but it
%% describes the PAPER rather than the evidence, and §4 introduces `resource`
%% under its own heading three lines later.  Restoring it restores nothing false.
Everything above varies one thing and re-reads a number: a spelling, a compiler,
a hardening flag, our same-machine-code rule. Where it moves, that settles the
cause; where it does not, \ref{sec:notthecheck}'s bound applies.
The next half varies things too, but its instruments answer yes or no. Silence
there tells you even less than a zero does here, so that half must also name what
each guarantee actually watches.
