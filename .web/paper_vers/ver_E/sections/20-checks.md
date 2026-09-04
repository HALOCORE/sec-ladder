%% Q2 -- THE PAPER'S CENTRE.  It is what the reader says once the parity numbers
%% have landed: they concede the numbers and attack the mechanism instead, which
%% is the right move.
%%
%% ⚠⚠ THREE MOVES.  This section fused TEN separate points and was the worst
%% offender in the paper.  Move 1 is the claim and must be sayable from memory.
%% Move 2 is the table, the two numbers and the median -- NOTHING ELSE.
%% Move 3 is the three reversals, the clock, and what these programs are made of.
%% ⚠ THE MOVE-2 TEST, apply it to every paragraph: does this support the sentence
%% in move 1?  If it supports some other true and interesting thing, it is a
%% sub-objection or it goes.
%%
%% ⚠⚠ THE HARDENED-C ROWS STAY IN THE TABLE AND STOP BEING DISCUSSED HERE.
%% .memory/01-ladder.md:344-350: with only the plain rung, "C is faster" and "C
%% is unsafe" are the same sentence, so publishing plain clang C at −17/−37
%% without hardened clang C at +7/+17 is the most attackable move available.  The
%% ROWS discharge that.  The paragraph of analysis (+7/+17, "clang's hardening
%% costs more than that gap") is section 6's argument, not this one, and it was
%% winning that argument three sections before the reader is allowed to raise it.
%% One deferring clause in the table's lead-in, and out.
%% ⚠ THE TABLE'S LEAD-IN IS ALSO WHERE `hardened` IS GLOSSED, in level 1, so a
%% breadth-first read gets the word exactly once and \ref{sec:harden} can use it
%% bare.  Do not move that gloss.
%%
%% ⚠⚠⚠ THE WALL-CLOCK FACT IS MOVE 3, NOT MOVE 2.  p16-tlv-walk/NOTES.md:62-65 --
%% the port's +72% of instructions is +0.27% of wall clock, INSIDE a run-to-run
%% spread of 0.96-2.31%, because the fold is latency-bound on a serial Horner
%% chain.  ⚠⚠ "ONLY TWO PROGRAMS HERE CARRY A CLOCK" WAS FALSE:
%% `grep -l "wall clock" patterns/*/NOTES.md` returns SEVENTEEN, and the
%% counterexample is in the next section (p09/NOTES.md:438-451, +205.6% Ir against
%% +205.4-219.7% ns on `small`, "no discount at all").  Never restore a count of
%% clocked patterns without re-running that grep, and never state the overstate
%% direction as a law.
%% ⚠ THE RUN-TO-RUN SPREAD IS ALSO THE PAPER'S ONE MEASURED YARDSTICK FOR "you
%% would not find that in a profile", so it is worth its words twice over.
%%
%% ⚠⚠⚠ "+27 / +77 IS A CEILING" IS GONE, AND SO IS "FLOOR".  p16/NOTES.md:38-54
%% is STRUCK THROUGH and marked "WITHDRAWN AT TASK_028", and the withdrawal says
%% "+27 / +77 *is* an upper bound on inf(in-contract R3) − R4ship".  But :204-209
%% says "'The shipped R3 is the cheapest admissible spelling' is FALSE, not
%% unestablished" -- two admissible respellings came in cheaper.  Both directions
%% ship, no verdict word.  Both "ceiling" and "floor" were tried; both are wrong.
%%
%% ⚠⚠ THE 7.26x AND THE "17 rows" ARE FROZEN OUT OF results/SYNTHESIS.md:205 AND
%% THEIR DENOMINATOR IS `totals.passing.analysed`.  ⚠ AND 7.26x IS USELESS TO A
%% READER UNTIL SOMEBODY SAYS IT IS NOT 7.26%.  Both halves are mandatory.
%%
%% ⚠⚠ THE gcc-VERSUS-clang PARAGRAPH UNDER THE TABLE IS A COLD-READ REPAIR AND
%% ANSWERS THE READER'S SHARPEST QUESTION ABOUT THIS SECTION: "why should I trust
%% a 27-instruction figure in a world where the same source costs 1,069 more
%% depending on which compiler I invoked?"  The answer is in their interest and it
%% is arithmetic they can do off the table: 4,062 - 2,993 = 1,069, which is ~40x
%% the +27, AND the +27 is Rust-against-Rust through one backend, so none of that
%% spread is inside it.  Do not cut it as defensive -- unaddressed, it is the
%% largest number on the page with no owner.
%%
%% ⚠⚠⚠ "TEN OF THE EXPENSIVE PROGRAMS" WAS A SET-MEMBERSHIP ERROR AND IS FIXED.
%% There are NINE over 100 Ir/call at shipped spellings (SYNTHESIS.md:158-159).
%% The mechanism table has TEN rows because SYNTHESIS.md:288-291 adds p22 -- a
%% hash probe that is FLAT as shipped (+2.00/+2.00) and only exceeds 100 against
%% the cheaper admissible R4 in its own record -- "which would otherwise never get
%% a mechanism at all".  So: nine expensive, ten explained, seven not-a-check,
%% three the check.  ⚠ NEVER write "ten of the expensive programs"; p22 is not one
%% of them, and \ref{sec:slower} promises nine.  ⚠ Do NOT confuse this with
%% SYNTHESIS.md:178's "7 / 3 / 10", which is the flat/negative/expensive
%% distribution at SEARCHED values and is a different statement entirely.
%%
%% ⚠ THE 7.26x DENOMINATOR IS 17 OF THE 22 COMPARABLE, not 17 of the analysed set
%% (SYNTHESIS.md:204-207, `synthesis/census.py`:169-177 -- licensed rows only,
%% `large` only, filtered to R3-R4 > 0).  Stating it against the 22 also lets the
%% reader place it: 17 is a subset of a number they already have.
%%
%% ⚠ "re-slice" IS GLOSSED AT FIRST USE, WHICH IS IN LEVEL 1.  It used to be
%% glossed twelve lines later, in Q2.1, so a breadth-first reader never got it and
%% a linear one guessed.  The Q2.1 appositive is gone; do not restore it there.
%%
%% ⚠ "an afternoon" IS GONE from the tuning asymmetry.  It contradicted this
%% node's own closing paragraph -- "no measured record carries a column for
%% effort" -- four lines later.  The asymmetry survives without the duration.
%% ⚠ NO REFERENCE TO EARLIER VERSIONS OF THIS PAPER, ANYWHERE, IN ANY FORM.
\section{“Fine, but that's unsafe Rust. Safe Rust is C plus a check on every access.”}
\label{sec:checks}

It isn't — and the gap between two safe versions of the same program is wider than the gap between safe and unsafe.

Here are two of them, on one program: same guarantee, every access checked, neither containing the word `unsafe`. One costs 69% more than the unsafe version. The other costs 0.9%. Nobody removed a check to get from the first to the second, so the difference between them is not the price of safety. It is the price of how the code was written.

The program is a record walker: read a three-byte header, take a length off the wire, fold that many bytes into a checksum, repeat. One safe version is a line-for-line port of the C, statement by statement; the other is the same program written the way the language wants it written, and it is the one somebody made fast. Both do the same job under the same fixed specification, against the same reference implementation.

Here is every version, in instructions per call at `-O3`, with the two C ones built by both compilers. The proved version gets no row, being byte-identical to the unsafe one. The hardened C — the same C with the missing check written into it — is here because the plain C alone would flatter Rust, and it gets its own section later.

| version | small input | large input |
|---|---|---|
| unsafe Rust | 3,010 | 23,798 |
| safe Rust, ported line for line | 5,095 | 40,921 |
| safe Rust, tuned | 3,037 | 23,875 |
| plain, unchecked C — clang | 2,993 | 23,761 |
| plain, unchecked C — gcc | 4,062 | 32,694 |
| hardened C — clang | 3,017 | 23,815 |
| hardened C — gcc | 4,079 | 32,735 |

Against the unsafe version the port costs +2,085 and +17,123 instructions a call; the tuned version costs +27 and +77. That is +69% and +72% against +0.9% and +0.3%. One of those you would see in a profile and the other you would not.

Read down that table before you read across it, because the biggest number in it is not a language at all. The same C source costs 2,993 under clang and 4,062 under gcc — 1,069 instructions a call, forty times the +27 the entire safe-Rust question is worth here. Be suspicious of that, and then notice why the +27 survives it: both sides of that subtraction are Rust through one compiler, so none of the gcc-versus-clang spread is inside it. It is inside every C-against-Rust figure in this report, which is why each of those names its compiler.

One program is an anecdote. Across all of them, wherever safe Rust costs anything at all, the line-for-line port costs about **seven times** what the tuned version costs. Seven times, not seven percent. That median is 7.26×, taken over the 17 programs where the tuned version comes out dearer than the unsafe one at all on the large input — 17 of the 22 that can be subtracted at all.

> So when somebody hands you a benchmark showing safe Rust is slow, the first question is not *how slow*. It is *who wrote it, and did anyone tune it?*

Now the parts that cut against that.

On three of those seventeen it runs the other way and the ported version is the cheaper. On the bitset that is not noise: its own notes record the tuned version re-slicing the buffer — naming a shorter stretch of it by where that starts and how long it is, so the bounds get checked once rather than per access — in a way that stops the compiler merging two narrow loads into one wide one.

Those percentages are instruction counts, and on this program a stopwatch does not follow them: the +72% is +0.27% of wall clock, inside the 0.96% to 2.31% that separates two runs of the same binary, because that fold waits on a chain of arithmetic rather than on memory and the extra instructions fit in the gaps. An instruction count is not a time. It is not reliably an overstatement either, as the next section shows.

And the two versions in that table are choices, not limits. Each side has a cheaper version that was measured and not shipped: two other allowed ways of writing the safe one came in under the tuned version, and one cheaper unsafe one was refused because the proof cannot handle the unaligned read it needs.

Finally, these programs are narrower than "safe Rust" sounds. More than half are missing a check on where a read or write lands, and all but one of those turn on one question — is this index inside this array — against exactly one use-after-free and one type confusion. This is a bounds-check benchmark. It says very little about the parts of a safe rewrite the type system settles at compile time, which cost nothing at run time by construction and so have nothing to measure.

%% Q2.1 -- forced by move 1: "how the code was written" is an assertion until
%% somebody says where the check went.
%% ⚠⚠ THE 2.00 / 2.25 SPLIT STAYS CUT.  The arithmetic 4.25 = 2.00 + 2.25 is
%% exact, but p16/NOTES.md:524-532 says the terms are NOT independently
%% recoverable: forcing LLVM to unroll the *checked* loop recovers 0.50, not
%% 2.25.  A reader told "less than half is the check" subtracts 2.25 and is
%% wrong.  The notes' own word is "forecloses", and that is what ships.
%% ⚠ The sweep's apparatus -- 127 record lengths, six fold spellings, the fitted
%% slope and residual -- and the bare per-byte range 5.04688-6.62500 stay cut:
%% "five decimal places on an instruction rate reads as insecurity."
%% ⚠ WHAT MAY NOT GO: that only the MATCHED difference is a property of the
%% program.  A zero quoted without it is a zero somebody chose.
%% ⚠ 4.25 Ir/byte IS SIZED BY CASHING IT OUT INTO THE +17,123 THE READER ALREADY
%% HAS FROM THE TABLE.  That is the sizing this subsection was missing: a rate
%% nobody can multiply in their head is not evidence to them.
\subsection{“Why? Where does the check go?”}

Out of the loop, and into the per-record work.

In the tuned version an extra byte of payload costs the safe version exactly what it costs the unsafe one: the safe version's re-slice and the unsafe version's unchecked access both sit outside the fold loop, leaving the loop body instruction-for-instruction identical whatever the chunk size. The port leaves its check inside that loop and pays 4.25 instructions for every byte it folds, which is where its +17,123 on the large input comes from.

Two limits on that. The 4.25 is not all check: it also forecloses a four-times unroll the check could never have amortised, so the two are welded together and neither subtracts out. And the zero is a property of the program only because the two versions were matched line for line — compare unmatched ones and the per-byte rate moves far enough to invent a safety tax that is really your choice of idiom.

%% Q2.2 -- the reader's next move, and it is the sceptical one: they accept the
%% mechanism on this program and ask what the rest of the set was paying for.
%%
%% ⚠ SEVEN, NOT SIX.  An earlier fact pack said six and explicitly forbade seven.
%% ⚠ THE Ir COLUMN STAYS CUT.  The claim is that seven of ten rows are NOT the
%% check; the sizes are not evidence for it, and cutting it also retires the
%% partition row's mandatory domain caveat, because the numbers it qualified are
%% gone.
%%
%% ⚠⚠ THE TWO DISPUTED ROWS ARE THE PARTITION AND THE CONSTANT-TIME COMPARE,
%% identified from source:
%%   * results/SYNTHESIS.md:294 gives the partition cell as "the data's shape",
%%     while patterns/p23-partition/NOTES.md:938 heads the finding "one of the
%%     two scans is elided and the other is not.  ⚠ THE CAUSE IS **OPEN**" and
%%     :992 says "what ships is the phenomenon plus an OPEN mechanism".
%%   * results/SYNTHESIS.md:295 gives the constant-time cell as "the constant-time
%%     discipline"; that is its R2→R3 SPELLING factor, a different rung pair from
%%     the R3−R4 this table subtracts, and patterns/p47-ct-compare/NOTES.md:567
%%     carries a `safety` row measured AT MATCHED constant-time spelling that the
%%     cell does not mention.  The honest cell is "unattributed at this rung
%%     pair"; that has never been settled.
%% ⚠ The p47 figure itself (+20.7%) is NOT printed: a percentage with no clock
%% twin.  The dispute is carried by naming the rows, not by sizing them.
%% ⚠ "the synthesis" IS APPARATUS VOCABULARY.  It is "this project's own
%% write-up" everywhere in the reader's text; the term survives in these comments
%% only, where the next editor needs it to find the file.
\subsection{“Then what were all those big numbers?”}

Mostly not bounds checks.

All nine of the expensive ones have a written explanation of where the money went, and so does a tenth — a hash probe, flat as we ship it, which only turns expensive against a cheaper unsafe version found afterwards. On seven of those ten this project's own write-up names something other than a check.

| program | what the write-up says it pays for |
|---|---|
| an index flattener | a hoisted per-row trip count, and a scalar epilogue |
| a rotate | not a bounds check but the tests an iterator chain runs to ask whether it has run out |
| a field splitter | the unsafe version's foreclosed unroll |
| a protocol state machine | one `and $0x7,%edi` — a mask, not a check |
| a hash probe | the unsafe version's missing reslice; none of it is a bounds check |
| a partition | the shape of the data |
| a constant-time compare | the constant-time discipline — the port is cheaper precisely because it leaks |

Two of those seven are disputed inside this project. The partition's own notes head the finding with the cause marked open — one of its two scans is optimised away and the other is not, and nobody has said why. And the constant-time comparison's explanation belongs to a different pair of versions than the pair this table subtracts. The reading above is the write-up's; on those two rows the programs disagree with it.

Which leaves three where the write-up does put it down to the check, and that is what you should be objecting about next.

%% Q2.3 -- the real objection under this whole section, and the honest answer
%% costs us something.  The sceptic, verbatim: "'Tuned safe Rust' is a
%% per-function, forever cost paid by people who aren't the paper's authors, and
%% it never appears in a benchmark table."  Not quoted, because the subsection
%% title already is the objection.
%%
%% ⚠ NOT a one-string change: about ten lines, and the inner loop is rewritten.
%% ⚠⚠ THE RETRACTION STORY IS MOVE 3 AND IS THE BEST ADMISSION IN THE PAPER.  It
%% is about the RESEARCH PROJECT'S own published summaries, not about earlier
%% drafts of this document, so it is not covered by the no-self-reference rule.
%% ⚠⚠ THE AUTHORING-COST ADMISSION IS CORRECTED: "no authoring-hours data exists
%% anywhere" is FALSE, two patterns record informal figures.  The true and
%% stronger form is that no MEASURED RECORD carries an effort column and two
%% planning documents promise the metric.
\subsection{“Somebody had to go and tune it. Who pays for that?”}

You do, per function, forever — and it never appears in a table like the one above. That objection we cannot close.

What we can give you is the size of the edit. The tuned record walker differs from the ported one by about ten lines, the inner loop rewritten to take the bytes in chunks — not a flag, not a library swap. And the two sides are not equally easy to tune: rewriting the safe version costs somebody the edit and nothing else, while rewriting the unsafe version has to come back out through a machine-checked proof, and sometimes it does not.

So the side that goes unsearched here is systematically the unsafe one, and the errors in this report run one way, in safe Rust's favour. We learned that the expensive way: early on this project published *safe Rust beats unsafe Rust* three times and retracted it three times, each time because somebody wrote a cheaper version of one of the two. The answer was to settle each program's allowed way of writing it in advance, which is why every superlative here reads *cheapest found* and never *minimum*. That is not modesty; it is the status of every number in this report.

And the thing you actually asked about, we do not have. No measured record in this project carries a column for effort, though two of its own planning documents promise one. What it costs to get from the port to the tuned version is not measured here, and nothing in this report should be read as a claim about it.
