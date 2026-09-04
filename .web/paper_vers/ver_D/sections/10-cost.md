%% Story 2.  THIS FILE WAS NINE BEATS IN THE PLAN THIS DESCENDS FROM AND IS NOW
%% SIX.  It is where all four cold readers quit the previous framing, and they
%% quit because it demonstrated ONE finding over and over -- one of them counted
%% eight appearances of "the number depends on which two versions you subtract"
%% and said "I would have closed the tab".  So: that finding is demonstrated
%% ONCE, in the four-costs paragraph, and the rest of the file is spent on things
%% that are not it.
%%
%% The opening move here is ver_B's meeting-room hook, MOVED from the top of the
%% post to the top of this half, because arguing about a percentage is what
%% motivates the cost question.  Each half opens on the reader's own situation.
%%
%% CAVEAT UP FRONT, not at the end.  A cold reader: "I spent the whole section
%% believing this was a representative program.  Finding out at the end that it
%% was deliberately chosen to be weird retroactively changed how I read the four
%% numbers I'd just been given."  It costs nothing and it is more honest early.
%%
%% NO PERCENTAGES AS COST FIGURES.  Not +69%, not +72%, not +0.897%.  The post's
%% own close says take the per-call constant, and printing a percentage here
%% would contradict it.  FACTS.md A3.
%%
%% The 17,526 admission LEADS WITH "slower than it needed to be".  Three of four
%% cold readers read the previous framing's "ours is held too high" as a BOAST,
%% exactly backwards.  Ceiling 80 words, past which an admission inverts into
%% backpedalling.
%%
%% Sources: FACTS.md A2, A3, A4, A7, B2, D, E, F.  The ten-row attribution table
%% is CUT; the corpus gets one sentence of one count of one thing.
\section{The cost of the check depends on what you subtract}
\label{sec:cost}

Suppose the decision is already yours. There is a C parser in production, somebody has proposed rewriting part of it in Rust, and the argument in the room is about a percentage — theirs off a blog post, yours off a benchmark somebody ran once. You can both be quoting real measurements and both be right.

%% ⚠ ~15 words trimmed, claim untouched.  Both halves of C7 survive: the program
%% was CHOSEN to be awkward, and this project's own grouping by gap size puts it
%% in none of the groups (results/SYNTHESIS.md:153-155).  ⚠ That is the census's
%% own count, NOT the cross-pattern distribution, which this post does not carry.
%% ⚠ Tightened ~12 words.  Both halves of the caveat survive intact: the program
%% was CHOSEN to be awkward, and this project's own grouping by gap size puts it
%% in none of the groups (results/SYNTHESIS.md:153-155, the census's own count,
%% not the cross-pattern distribution).
One warning first. This record walker was picked to be awkward — to break the comfortable rule that safety is cheap wherever the optimiser can see the whole loop — and this project's own grouping by gap size puts it in none of the groups. Don't generalise the size of anything below.

%% ⚠ FACT-CHECK 6: "which two of the SIX versions" was false for the -2,545.
%% That side is `s_c64`, a control generated from safe_tuned.rs, and
%% controls/gen_controls.py:275-276 banners it "a matched FOLD respelling.  NOT a
%% p16 cell".  The paragraph twenty lines down already describes it correctly as
%% a rewrite, so the draft contradicted itself.  "of the six" is dropped; "which
%% two versions" is true of all four pairings.
So what do those three lines cost? On this program, per call, on the larger of its two test inputs, the answer is −2,545, or 0, or +77, or +17,123 executed instructions — and the only thing changing between them is which two versions you subtract.

The +17,123 is the line-for-line port against the unsafe version, and the port is the one nobody tuned, so most of that number is not the check. The +77 is the tuned safe version against the unsafe one, which is the comparison people in that meeting actually mean.

%% ⚠ FACT-CHECK 15: the rule is an `-O3` rule.  results/gate/p16-tlv-walk.json
%% `identity[0]` is the same pair at `O0` with level and expectation both
%% `norel` -- the gate expects them NOT to match there.
The 0 is the proved version against the unsafe one, and it's enforced rather than discovered: this project requires the two to compile, at full optimisation, to identical machine code. You should have the reason before the price: without that rule you'd be pricing the proof's effect on the compiler rather than the cost of the code, and a proof that moved the code could hide the very difference being measured.

%% ⚠⚠ THIRD READER ACROSS THREE VERSIONS TO FAIL ON THIS NUMBER, so the edit is
%% now SHOWN rather than described.  ver_C's wording leaned on the identifier
%% (`chunks_exact(32)` -> `(64)`) and two readers could not parse the sentence at
%% all; this draft said "one string substituted" and the third asked "Substituted
%% where?  What string? … I couldn't picture the edit at all, and this is the
%% paragraph explaining your most surprising number."
%% ⚠ THE WIDTH MUST TRAVEL WITH THE INPUT (results/tables/p16-tlv-walk.md:37):
%% -2545 is a `chunks_exact(64)` LARGE-blob number; at small, `(64)` is 72 Ir/call
%% DEARER than `(32)`, and the cheapest found there is -199 at `(16)` or `(32)`.
%% No single spelling is cheapest on both blobs, which is exactly why the last
%% sentence exists.  CLAIMS.md §3.8: "cheapest found", never "minimum".
%% ⚠ THE LAST SENTENCE WAS ALSO A REREAD ("two reversals in one sentence, about a
%% number I was still holding") and is now two sentences with one reversal each.
%% ⚠⚠ TWO CORRECTIONS HERE, AND THE SECOND IS A FACTUAL ONE I INTRODUCED.
%%
%% (1) "ONE STRING SUBSTITUTED" IS RETIRED.  Three readers across three versions
%% have now failed on this number.  ver_C leaned on the identifier and two could
%% not parse the sentence; this draft said "one string substituted" and the third
%% said it "made me think it was a trivial edit".  IT IS NOT A TRIVIAL EDIT.  I
%% opened controls/gen_controls.py:305-315: the variant replaces the shipped
%% `.iter().fold(...)` with `chunks_exact(64)` + `try_into::<[u8; 64]>()` + an
%% inner byte loop + a `remainder()` fold — about ten lines.  The tree's own "one
%% substitution from the shipped one" (NOTES.md:216) is one substitution IN THE
%% GENERATOR, of the whole fold block.  Describing it as a changed string is
%% misleading in the reader's direction, so the prose now says what it does and
%% how big it is.  ⚠ Do not put a fabricated two-line code block here; I tried
%% one and it did not match the generator.
%%
%% (2) ⚠⚠ "on the smaller one a narrower fold beats it, and this one is dearer"
%% WAS FALSE and is corrected.  gen_controls.py:475 records
%% `u_ship - s_c64 = 127 / 2545`, so the 64-byte fold is 127 Ir/call CHEAPER than
%% the unsafe rung on `small` as well — it is dearer only than the NARROWER fold
%% (`chunks_exact(16)`/`(32)`, cheapest found at -199 there, NOTES.md:215).  The
%% old sentence read as "dearer than unsafe", which is the opposite of the
%% measurement.  The surviving claim is the one the artefact actually demands:
%% the WINNING WIDTH IS NOT THE SAME ON THE TWO INPUTS, which is why a
%% cheapest-found figure must name its input as well as its spelling.
%% ⚠ CLAIMS.md §3.8: "cheapest found", never "minimum".
%% ⚠ FACT-CHECK 14 / CLAIMS.md §3.2: never a bare "the shipped safe Rust" where
%% two safe versions ship.  The control is derived from the TUNED one only
%% (gen_controls.py:21,277).
And the −2,545 is a safe version beating the unsafe one. Take the tuned safe version, whose inner loop walks the value one byte at a time, and rewrite that loop to take sixty-four bytes at a time instead. It's about ten lines, it has no `unsafe` in it, and it meets the same contract and returns the same answers — and on the larger input it runs 2,545 instructions per call fewer than the unsafe version does.

That's the cheapest anyone has found, not a minimum: nobody has shown there's nothing better. And the winning width isn't the same on both inputs — on the smaller one a narrower fold is cheaper still, which is why a number like this is worth nothing unless you say which input it came from.

That's four answers to a question that sounds like it has one. Here's the version you probably meant, everything else held still: hardened C minus plain C, same compiler both sides, is +17 instructions per call small and +41 large under gcc, +24 and +54 under clang. %% ⚠ FACT-CHECK 8: "the only subtraction the source licenses" was too broad --
%% spec.md:375 licenses the proved-minus-unsafe pin and :70-72 licenses the
%% tuned-safe-minus-unsafe bound.  Narrowed to what is actually unique about it,
%% which is what kernel_hardened.c's header claims: the cost of the check "within
%% one language, with the signature, the calling convention, the header test, the
%% fold and the return all held fixed".
Same signature, same loop, same return; the diff is three lines. It's the only subtraction here where the source itself says, in as many words, that what you are measuring is the check and nothing else.

Now a different program, because one can't teach you a habit. A bounded stack — push, pop, refuse to run off either end — has a safe version costing +626 instructions per call more than its unsafe one on the large input. Count the bounds tests in the source and that's roughly what you'd predict, which is what makes it a trap.

%% ⚠⚠⚠ FACT-CHECK, MUST-FIX 2/3/4.  THREE ERRORS IN THREE SENTENCES, all
%% inherited from ver_C's example box, all verified at source in
%% patterns/p03-bounded-stack/NOTES.md, which I opened.
%%
%% (a) "DELETING THEM ANSWERED +5" DESCRIBES THE WRONG OPERATION.  Nothing is
%% deleted.  `m_clamp` is `safe_tuned` with one provably-dead line ADDED at the
%% top of the loop -- `if sp > STACK_CAP { return 0; }` (NOTES.md:366-371).  The
%% optimiser then deletes the real check.  NOTES.md:405: "It is not the dead test
%% executing -- the dead test is gone."
%%
%% (b) "NOBODY HAS EXPLAINED THAT +5" IS FALSE.  NOTES.md:1259-1260 names it: the
%% two clamped rungs "differ only in the per-call constant (46 against 41, THE
%% WINDOW-RESLICE CHECK)".  A SECOND, DIFFERENT check, not a residue of the one
%% being counted.  Only one half survives: results/SYNTHESIS.md:286 does round it
%% away as "deletes 100% of it".
%% ⚠⚠ AND NOTES.md:1263-1266 FORBIDS THE PUBLICATION OUTRIGHT, in bold: cheapest
%% R3 2889/8182 minus cheapest R4 2884/8177 is "exactly 5 on both blobs ... **Do
%% not publish that as p03's safety tax.**"  .memory/01-ladder.md:203-205 (the
%% authoritative layer) adds that min(R3)-min(R4) differences two UPPER bounds
%% and bounds nothing.  So the 5 may be named as an unswept remainder of a
%% comparison.  NEVER as what safety costs, and never as a headline pair with
%% the 626.
%%
%% (c) "SIX STACK SIZES" -- the stack size never varies.  c/kernel.c:43 is
%% `#define STACK_CAP 64`, one value for the whole pattern.  The sweep is 19
%% blobs: 13 pop densities plus six OPERATION COUNTS (NOTES.md:249-252, :375).
%%
%% (d) ⚠ AND THE TRICK IS NOT FREE, which the draft omitted in safe Rust's
%% favour -- the exact coverage-bias failure §4 retracts.  The dead line costs
%% 2.00000 Ir per DROPPED push, so on `large` (352 dropped pushes per call)
%% `m_clamp` lands +502 against the unsafe rung (NOTES.md:390-404).  It buys the
%% per-pop term and spends a per-push one.  That now ships.
Add a clamp — one extra line at the top of the loop, forcing the index back into range, which can never actually fire because the proof already shows the index is in range. Hand the optimiser that fact and it deletes the real check. The per-pop cost goes to exactly zero, across thirteen different rates of popping and six operation counts, with nothing fitted.

Counting bounds tests predicted +626 per call. Making one fact visible to the optimiser answered nothing per pop at all.

Two things that stops short of, and both run against the neat version. The clamp isn't free: the dead line costs two instructions every time a push gets dropped, which on the larger input leaves the clamped version +502 against the unsafe one. And a five-instruction difference per call survives, which this project's own summary rounds away as "deletes 100% of it" — it's a second, different check, on the window rather than the stack, and it was never the one anybody was counting.

%% ⚠ THREE SENTENCES, DELIBERATELY.  The rule is the most quotable thing in the
%% post and it was buried in a 50-word sentence with its own bound welded on as a
%% subordinate clause.  Rule alone, then bound alone.  ⚠ THE BOUND MAY NOT BE
%% DROPPED — CLAIMS.md §1.23 requires it to ship WITH the method, because nothing
%% in the gate distinguishes a deleted check from two rungs that happened to
%% compile alike.  ⚠ Also cut: "Which gives the most portable sentence I know how
%% to write" — a sentence whose subject is the post, and self-congratulatory
%% about the line it introduces.
%% ⚠⚠ FACT-CHECK, MUST-FIX 5.  IT IS SEVEN OF TEN, NOT SIX -- and my own fact
%% pack said six and explicitly forbade seven, which is how it reached the draft.
%% Counting results/SYNTHESIS.md:284-295's own verdicts, which I opened: THE
%% CHECK on p03, p07, p09; NOT a bounds check on p05 ("a hoisted per-row trip
%% count and a scalar epilogue"), p06 ("none of it is a bounds check"), p14
%% ("R4's foreclosed unroll"), p19 ("a mask, not a check"), p22 ("the unsafe
%% rung's missing reslice"), p23 ("the data's shape"), p47 ("the constant-time
%% discipline").  Three and seven.
%% ⚠ WHY IT IS ATTRIBUTED TO THE SUMMARY RATHER THAN ASSERTED FLAT.  ver_C
%% RECLASSIFIED two of those rows on the patterns' own notes -- p05 to the check,
%% p14 to unattributed -- which would give six.  CLAIMS.md's authority order puts
%% SYNTHESIS.md ABOVE a pattern's NOTES.md, so the published table wins here; but
%% the reclassification is a live disagreement and ver_D has one sentence, not a
%% paragraph, to spend.  Saying whose count it is makes the sentence true either
%% way and checkable in one place.  ⚠ Do not flatten this to a bare "on seven".
%% ⚠ The denominator behind "ten" is the 22 LICENSED rows, not the 26 programs
%% (SYNTHESIS.md:98,138) -- which is why the sentence says "of these programs"
%% and never "of the 26".
This project's own summary then goes through the ten programs whose gap is big enough to be worth explaining, one row at a time. On seven of them, the thing it names is not a bounds check.

So: a cost belongs to a mechanism only if removing the mechanism moves the number. With one bound on that, which you need before you use it — nothing in our checking can tell a deleted check apart from two versions that happened to compile to the same bytes. A difference of zero never licenses "safety is free here".

One thing to hold against every safe-versus-unsafe figure above, mine included. Our unsafe baseline is slower than it needed to be: the rule tying each proved version to an identical unsafe one rules out faster ways of writing the unsafe side, and on a NUL scan the ruled-out way was 17,526 instructions per call cheaper on the large input, about 35% of everything that function executes. A saving refused, not a cost added, and on the small input the pinned version is cheaper. But every safe-versus-unsafe number here reads more kindly to safe Rust than it should.

%% ⚠⚠ FACT-CHECK 9: THE SCOPE WAS OWED AND IS NOW IN THE SENTENCE.  This is
%% p02's buffer copy on its LARGE blob only (p02/NOTES.md:527-534).  Unscoped, a
%% reader attaches it to the record walker they have just spent a section on,
%% WHERE THE SIGN IS REVERSED -- gcc is 36% dearer than clang there
%% (p16/NOTES.md:281-286) -- and on p02's own small blob gcc is dearer too.
%% .memory/01-ladder.md:629: "Neither compiler is reliably ahead."
%% ⚠ results/synthesis.md:58 stands over any gcc-vs-clang sentence: never
%% attribute such a gap to codegen without naming gcc's `-fcf-protection=full`
%% landing pad.  This sentence attributes it to nothing, which is the safe move
%% and the honest one, since the whole point is that we do not know.
And one measurement I'd rather not have. On one of these programs, on its larger input, from identical C source, gcc ran 10% fewer instructions than clang and took 23% longer. We cannot explain it.
