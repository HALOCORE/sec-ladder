%% Q1.  THREE MOVES: the answer, why you should believe it, where it breaks.
%% Nothing else.  A reader who stops after move 1 must be able to say what the
%% answer is -- the old opening ("Mostly it isn't, and on this corpus the
%% direction is not even reliably against Rust") was a hedge, and the actual
%% answer did not arrive for six paragraphs.
%%
%% ⚠⚠ MOVE 2 RUNS CLEAN.  Every scope, condition and exception belongs in move 3,
%% welded to the claim it qualifies.  A cold reader: "No number in this document
%% survives its own paragraph, so I stopped trying to carry any of them out."
%% That is what sentence-by-sentence qualifying costs.  It is NOT a licence to
%% drop one -- every word of them is still here, further down.
%%
%% ⚠⚠ THE gcc / `-fcf-protection=full` MATERIAL MOVED OUT to Q1.1.  It is not
%% evidence that Rust is not slower; it is a way of getting a big number out of
%% these programs, which is literally that subsection's subject.  It is stronger
%% there and it was fusing this section.
%%
%% ⚠⚠⚠ THE WHOLE-RUN TOTALS ARE GONE AND THEY MAY NOT COME BACK.  This paragraph
%% used to print 143,740,000 for both builds and call it "the same total, to the
%% digit, not a number close to it".  The target reader stopped dead:
%%   "The number as printed has four trailing zeros.  It is five significant
%%    figures.  You cannot claim 'to the digit' on a figure you rounded to the
%%    nearest ten thousand.  This is the one place in the document where I felt
%%    actively worked on."
%% The figure was NOT rounded -- it is 20,000 calls x 7,187 exactly -- but nothing
%% on the page said so, and a claim of exactness that LOOKS rounded is worse than
%% no claim.  ⚠ THE FIX IS THE PER-CALL FIGURE, WHICH IS EXACT AND LOOKS IT:
%% data/patterns/p01-array-sum.json, O3/isolated, c-clang and unsafe both read
%% kernel_per_call 7187.0 on large.bin, and 900.0 against 901.0 on small.bin.
%% ⚠ AND IT REPAIRS A SECOND DEFECT FOR FREE.  \ref{sec:setup} establishes the
%% unit as instructions on one call; the whole-run totals switched units without
%% a bridge, and then the SMALL input's total (180.0M / 180.2M) was LARGER than
%% the large input's, for a reason -- ten times as many calls -- that lived in a
%% dash.  Per call, small is 900 and large is 7,187, which is the order the reader
%% expects.  ⚠ SIZING IS NOW FREE TOO: "one instruction apart, 900 against 901"
%% needs no percentage.  Do not reintroduce a whole-run total anywhere.
%%
%% ⚠⚠ MOVE 3'S CONDITIONS ARE MANDATORY: large input only, and one backend.
%% CLAIMS.md §1.4 -- whether rustc's LLVM is bit-for-bit clang's is a LIVE
%% IN-TREE CONTRADICTION, so this claims the version and nothing else.
%% ⚠ CLAIMS.md §1.19: "zero executed instructions" holds everywhere;
%% *byte-identical* fails on the one vtable-stub pattern.  Both are in move 3.
%%
%% ⚠ THE SHIPPED-VERSIONS ADMISSION IS THE WHOLE DOUBT ABOUT THIS ANSWER and it
%% arrives ONCE, last, as its own beat.  Do not scatter it back through move 2.
%%
%% ⚠⚠ "22" AND THE 9/4/9 BUCKETS ARE FROZEN FIGURES OUT OF results/SYNTHESIS.md
%% AND THEIR DENOMINATOR IS `totals.passing.analysed`, NOT `.patterns`.  They
%% were derived over the analysed set and the corpus has since grown past it; a
%% live 27 standing next to a frozen 22 is the defect \ref{sec:setup}'s last
%% paragraph exists to prevent.  The literals themselves are still unguarded --
%% no \num{} path exposes them -- which is a known exposure.
%%
%% ⚠⚠⚠ 9 + 4 + 9 = 22 AND IT IS A COINCIDENCE, NOT A PARTITION -- SYNTHESIS.md
%% :162-164 says so in bold, and `synthesis/census.py`:138-140 shows why (the
%% three predicates are |v|<=32 on both, v<0 on both, v>100 on either; the first
%% two can hold at once).  THE OVERLAP IS EXACTLY p18, in both the flat and the
%% negative list; p16 (+27/+77) is in none.  THE EXPENSIVE BUCKET IS DISJOINT
%% FROM THE OTHER TWO BY CONSTRUCTION.
%% ⚠ THIS USED TO BE RETRACTED EIGHT LINES LATER ("they are not a partition"),
%% and the target reader had already banked the sum and gone back up to redo the
%% arithmetic on paper: "the single most expensive 40 seconds in the piece, and
%% it buys nothing."  ⚠ THE FIX IS TO CLOSE THE SUM WHERE IT IS TEMPTING, NOT TO
%% withdraw it afterwards.  The text now names both irregular rows in the same
%% breath as the counts, so 9 + 9 + 4 - 1 + 1 = 22 is a sum the reader can do and
%% it comes out right.  And the leftover row IS the record walker, which is the
%% subject of the very next section, so naming it costs nothing and buys a bridge.
%% ⚠ DO NOT "TIDY" THIS BACK INTO THREE CLEAN COUNTS.
%%
%% ⚠⚠⚠ THE PROOF'S ZERO IS DISCLOSED HERE AS A RULE, AND THAT PLACEMENT IS THE
%% FIX FOR THE PAPER'S WORST USED-BEFORE-GIVEN DEFECT.  It used to be stated here
%% as a FINDING ("the proof costs nothing... the compiler emits the same bytes")
%% and only admitted to be an imposed rule in \ref{sec:unsafe}'s first
%% subsection.  The reader, on reaching it: "You told me a rule and let me read
%% it as a result for two thirds of the document... you let me spend it for 140
%% lines."  ⚠ THE ARGUMENT STAYS IN \ref{sec:unsafe} -- what the rule buys, and
%% the 17,526 saving it refused.  Only the DISCLOSURE moved.  Do not move it back
%% and do not duplicate the argument here.
%%
%% ⚠⚠⚠ THE CLOSING CONCESSION PARAGRAPH IS A PLACEMENT SETTLEMENT BETWEEN TWO
%% READERS WHO ARE BOTH RIGHT, AND IT MAY NOT BE DELETED AS A DUPLICATE OF
%% \ref{sec:harden}.  One reader, given only the pitch, placed "why not just
%% harden my C" LATE and was right about why: asked first it is a shield, cheaply
%% answered, and it only becomes the sharp question once you already believe the
%% cost is small, nonzero and unevenly spread.  The target reader, having read the
%% whole thing, called it their FIRST objection stranded at seventh: "Had that
%% appeared right after section 2, I'd have read the rest with a completely
%% different posture.  Where it sits, it feels like it was held back."
%% ⚠ THEY WANT DIFFERENT THINGS: one wants the CONCESSION early, the other wants
%% the ARGUMENT late.  So the concession moves and the section does not.
%% ⚠⚠ IT MUST BE A REAL CONCESSION AND NOT A PROMISE TO CONCEDE LATER, or it reads
%% as exactly the holding-back being complained about.  Hence "it is not any
%% smaller in section 6" and hence the 17 / 41, which the reader can subtract off
%% \ref{sec:checks}'s table (4,079 - 4,062 and 32,735 - 32,694) two pages later.
%% ⚠ THE MEDIAN OF 24 IS DELIBERATELY NOT USED HERE: CLAIMS.md §1.5 requires its
%% range alongside it, and a range here would turn the concession into a hedge.
%% One program's two numbers concede more and qualify less.
%% ⚠ NO REFERENCE TO EARLIER VERSIONS OF THIS PAPER, ANYWHERE, IN ANY FORM.
\section{“It'll be slower.”}
\label{sec:slower}

No — and the number you are bracing for is mostly not there. On the simplest program here the C and the unsafe Rust execute the same number of instructions on a call, to the digit, not a number close to it. Most of the rest land within a few dozen instructions a call of each other, and on a few the safe Rust is the cheaper one.

That program is a sum over an array. Built with clang, on the large input the C runs 7,187 instructions on a call, and the unsafe Rust — `unsafe` being the keyword that opts you out of the automatic bounds checks, on the promise that you did the checking by hand — runs 7,187 too. All four digits, from two languages. On the small input they are one instruction apart: 900 against 901.

The machine-checked proof costs nothing on top of that — but not for the reason it looks like. We required it: a program's numbers do not count here unless the proved version and the unsafe one compile to the same machine code, byte for byte. So that zero is a rule, not a result, and \ref{sec:unsafe} is what the rule buys and what it made us refuse.

%% ⚠⚠⚠ THIS PARAGRAPH USED TO BE THE WORST IN THE PAPER AND IT MUST NOT GROW
%% BACK.  It ran 26 -> 22 -> nine -> nine -> four, told the reader "do not add
%% those up -- they are overlapping descriptions, not boxes", then explained
%% WHICH program was in two buckets and WHICH was in none.  That is our
%% bookkeeping, and a cold reader's verdict on exactly this was that redoing the
%% arithmetic on paper was "the single most expensive 40 seconds in the piece,
%% and it buys nothing".  THE ANSWER TO "your denominators do not reconcile" IS
%% NOT TO EXPLAIN THE DENOMINATORS.  IT IS TO STOP GIVING THEM.
%% ⚠ Nothing measured is lost: the nine expensive programs are the subject of the
%% next two sections and are named there one at a time, which is where a reader
%% can actually use them.  The four unlicensed rows are a fact about our
%% arithmetic, not about Rust, and they do not belong in front of a reader
%% deciding whether to rewrite a parser.
Across the rest, safe Rust mostly costs a few dozen instructions a call — flat in the size of the data, and nothing you would find in a profile. On a few it comes out cheaper than the unsafe version, and where anyone went and looked, none of that margin was safety either. On nine of them it costs real money, and those nine are what the next two sections are about.

Now, in one place rather than dripped through the section, the three things that make that thinner than it sounds.

The dead heat is the large input only, and it is one optimiser rather than two: the C went through clang and Rust goes through the same version of LLVM. Two front ends handing one back end the same problem is not two independent compilers agreeing.

The proof's zero is not byte-for-byte everywhere — that is the gap between \num{totals.passing.identity_exact} and \num{totals.passing.patterns} above — and where it is not, it still costs nothing to execute. On one program a piece of proof-only code, which should disappear entirely, is emitted as an empty function body: it is declared inside a trait, Rust's version of a struct full of function pointers, and every entry in such a table has to point at something, so the compiler leaves a body there for nobody to call. Forty bytes where there were thirty-two, and nothing ever calls it. Anywhere else the two builds part company, it is inside an address field rather than an instruction. Zero executed instructions holds on all \num{totals.passing.patterns}.

And the versions compared are ones we chose. On four of those 22 there is a cheaper way of writing the unsafe one that we measured, that passes the prover, and that does the same job under the same fixed specification. We did not ship it. Apply all four and three programs change group — every one of the four against safe Rust.

One more thing before the next objection, because you are already thinking it. Your instinct is to add the missing check to the C and keep the code, and that instinct is right: for these bugs, hardening your C works. It gives the right answer on every hostile input we threw at it, and on the record walker the next section takes apart, writing the check in costs 17 instructions a call on the small input and 41 on the large — a subtraction you can do off the table there yourself. On what these programs do under attack we cannot tell hardened C and Rust apart. That concession is not any smaller in section \ref{sec:harden}, and everything between here and there is what is left of the argument once you have granted it.

%% Q1.1 -- what the reader says the moment the parity numbers land, and they are
%% right to say it: they have a number of their own and it does not look like
%% ours.  THREE MOVES AGAIN.
%%
%% Move 2 is a parallel triple -- pair, compiler, input -- and it must stay
%% parallel.  The gcc material arrived here from §1 because it is the second of
%% the three, not because it needed a home.
%%
%% ⚠⚠ THE −2,545 IS CUT AND MUST NOT COME BACK.  The record walker's own notes
%% (NOTES.md:1948-1949) call the safe-beats-unsafe sentence "the sentence a
%% reader will quote and the sentence the measurement does not support": at
%% MATCHED spelling the unsafe side is still cheaper, +221 / +2,417
%% (NOTES.md:1885-1888), so that win is a permission artefact of the identity pin
%% rather than a code win -- and one of the four differences it belonged to is a
%% committed CONTROL, not a rung.  The four kept here are all gate-certified
%% rungs and all four are rows of the next section's table.
%% ⚠ The fitted law `2.25·m − 5647` stays cut: the crossing point is the finding,
%% the coefficients were apparatus.
%% ⚠ `-fcf-protection=full` must be named before ANY gcc-versus-clang gap in this
%% report is read as codegen.  It is NOT claimed to explain that gap: it is
%% measured, and it is small.  ⚠ SIZE IT: one instruction at the top of every
%% call is what the reader needs, not the flag name on its own.
%% ⚠ The sign-flip sentence is quoted exactly as the tree words it.  "Nothing in
%% that reversal is safety" is the half an editing pass drops.
%% ⚠ THE CROSSOVER IS THE READER-FACING FORM OF THE WHOLE SUBSECTION: 2,510 bytes
%% is not a fact about our two blobs, it is a fact about THEIR message sizes, and
%% the sentence saying so is what makes the paragraph an answer rather than a
%% report.  Do not cut it as editorialising -- it restates the measurement.
\subsection{“But I've seen benchmarks where it is slower.”}

%% ⚠⚠ THE HEADING AND THIS PARAGRAPH BOTH FAILED THE SAY-IT-OUT-LOUD TEST, and
%% the owner got lost here.  It read "But I measured a big number", and the
%% answer offered "which two versions you subtract" -- which presumes the reader
%% owns six versions of one program and is subtracting pairs off a bench.  THEY
%% DO NOT.  They have their C, a compiler, and a benchmark somebody sent them.
%% ⚠ The three choices below are unchanged and they are the right three; what
%% changed is WHOSE choices they are.  They are not things the reader got wrong.
%% They are the reasons two honest benchmarks disagree, which is the question
%% actually being asked.
You have, and most of them are honestly run. Three things move this answer and a benchmark almost never says which it picked.

**Which two things were compared.** On the record walker at the large input, four pairs of versions we ship differ by nothing at all, by +77, by +8,896 and by +17,123 instructions a call. Same program, same input, same machine. The next section is that table.

**Which compiler built the C.** gcc's column runs differently from clang's throughout this report, and part of that is a flag rather than code generation: gcc on this box defaults to `-fcf-protection=full`, so every gcc-compiled function opens with an `endbr64` landing pad — one instruction on every call, a control-flow-integrity feature neither clang nor rustc turns on.

**Which input it was run on.** On a protocol state machine, safe Rust's bounds check and the C's validation pass are the same test done at different moments: the C validates its whole table once per call, while the safe indexing becomes one range test paid once per message byte. One is O(table), once; the other is O(message). So the plain, unchecked C comes out 5,071 instructions a call cheaper than unsafe Rust on the small input and 3,569 dearer on the large, crossing over at a message of about 2,510 bytes — between the two inputs that program ships with. Which language wins there is a fact about your message sizes.

> Any percentage quoted at either input is wrong in sign at the other, and nothing in that reversal is safety.

Both state-machine figures are gcc's C against unsafe Rust, so that landing-pad instruction is inside them. It is small, and it is not zero.
