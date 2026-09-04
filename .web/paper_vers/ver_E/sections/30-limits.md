%% Q3.  This node exists BECAUSE Q2's answer was incomplete: "the compiler proves
%% it away" invites exactly one question -- and when it can't?  The reader is
%% right, and conceding it immediately is what buys the rest of the paper.
%%
%% ⚠⚠ THREE MOVES.  Move 1 is the shape of the whole section -- three programs
%% are the check, one survives a search of both sides -- and it is not three
%% instances of one finding.  Move 2 is the three, one at a time.  Move 3 is
%% what they say together.
%% ⚠⚠ THE ALIASING-AND-MIRI BLOCK MOVED OUT INTO Q3.1.  It was ~300 words
%% answering a question this section never asks, arriving after the section had
%% already landed.  It is the reader's NEXT objection and it now has a heading.
%% Every scope clause travelled with it unchanged.
%%
%% ⚠⚠ THE BITSET IS NOT THE ROW WHERE "IT IS THE CHECK" IS ESTABLISHED.  It is the
%% opposite, and the opposite is the better sentence.  p09/NOTES.md:1121-1133
%% lists FIVE in-contract safe spellings against the same unsafe rung; the
%% SHIPPED one at +13,756 / +48,885 is the SECOND DEAREST, the cheapest found is
%% +263 / +854, and the ported rung (+9,936 / +36,409) is cheaper than the
%% shipped tuned one.  The notes call it a 65x span and "the sharpest
%% illustration this project has of why a published spread cannot carry a safety
%% claim".  The unsafe side really was searched and really is degenerate, so the
%% whole span lives on the SAFE side.
%% ⚠ THE +263 SHIPS WITH ITS ASYMMETRY OR NOT AT ALL: it comes from
%% `chunks_exact(4)`, unsupported at the pinned vstd, so the safe class reaches a
%% spelling the unsafe class cannot.  A permission artefact, not a code win.
%% ⚠ SIZING, ADDED AND SOURCED: +48,885 against an unsafe cell of 24,519.3
%% Ir/call (data/index.json, tax, isolated/large.bin) is THREE TIMES the unsafe
%% version's whole cost.  "+48,885" alone is a number the reader cannot place,
%% and this is the one place in the paper where the safety figure is enormous.
%% ⚠⚠⚠ AND ITS CLOCK PARAGRAPH IS THE PAPER'S ONE COUNTEREXAMPLE TO ITSELF.
%% Without it the paper gives one wall-clock case -- the record walker, +72%
%% shrinking to +0.27% -- and teaches that instruction counts overstate.  They do
%% not always.  p09/NOTES.md:438-451: R3 − R4 on `small` is +205.6% Ir against
%% +205.4-219.7% kernel-only ns, "no discount at all"; on `large` only a 1.1x
%% discount.  ⚠ NAME THE INPUT; the two do not agree.
%% ⚠⚠ BOTH HALVES STAY.  The shipped version was a choice AND its cost is real
%% in time.  Keep one and drop the other and the section is wrong either way.
%%
%% ⚠⚠ THE BINARY SEARCH CARRIES THIS SECTION.  p07/NOTES.md:890-906: four
%% in-contract safe spellings, and cheapest-found to shipped is EXACTLY ONE
%% INSTRUCTION PER PROBE -- the two differ by one `lea`.  Both unsafe candidates
%% were searched too: one is dearer, and the only cheaper one is disqualified
%% because the version carrying the proof cannot dereference a raw pointer.
%% ⚠⚠ THE DISQUALIFIED CANDIDATE'S −461 / −1,605 STAYS CUT, AND SO DOES THE BAND-
%% CONVENTION CLAUSE THAT HAD TO SHIP WITH IT: those figures are in the notes'
%% convention, not the synthesis convention the headline +3,015 / +10,025 uses.
%% DO NOT REINTRODUCE +3,017.14 / +10,019.42 EITHER.  "One instruction per probe"
%% is convention-independent, which is why it carries the claim.
%% ⚠⚠ 42.5% / 46.6% AND ITS CLOCK TWIN (+13.0% / +1.6%) ARE NOW BOTH PRINTED,
%% TOGETHER, AND THAT IS A DELIBERATE REVERSAL OF THE EARLIER "cut them both".
%% p07/NOTES.md:511-518 forbids quoting either WITHOUT the other -- both is
%% compliant, and both is now REQUIRED by a different rule: +3,015 / +10,025 is a
%% number no reader can size, and the pair is the only sizing the tree licenses.
%% Source: NOTES.md:452-462 (42.53% at n=7 rising to 46.63% at n=16,385, monotone
%% in all six query distributions) and :511-513 for the ns twin.  ⚠ IF YOU EVER
%% CUT ONE, CUT BOTH, and then the search's cost is unsized again -- say so.
%%
%% ⚠⚠⚠ THE BOUNDED STACK CARRIES THREE CORRECTIONS AND ALL THREE BIND:
%%   (a) the clamp is a line ADDED -- one provably-dead line at the top of the
%%       loop, after which the optimiser removes the real test.  NOT a deletion.
%%   (b) it is NOT free: 2 instructions per DROPPED push, +502 against unsafe on
%%       the large input.
%%   (c) the surviving +5 IS explained -- the window-reslice check, a different
%%       check.  Not a residue.
%% ⚠ That pattern's notes say IN BOLD: "Do not publish that as the safety tax."
%% ⚠ The input carrying the +5 is NOT stated in any source read for this draft,
%% so this file does not assign it to one.  Do not "tidy" that by guessing.
%%
%% ⚠⚠⚠ Q3.1'S SECOND PARAGRAPH IS THE MOST IMPORTANT SENTENCE IN THE PAPER FOR
%% ITS TARGET READER AND IT MAY NOT BE CUT, SOFTENED OR MOVED.  A senior C
%% developer read the whole report and named its ABSENCE the biggest single hole:
%%   "§4.1 tells me what the rules are.  It does not tell me what happens when I
%%    break them.  Nowhere does this document say plainly: a mistake inside
%%    `unsafe` is the same class of memory corruption you get in C.  It's implied,
%%    never stated.  That is the single most important sentence for a C developer
%%    and it is missing."
%% ⚠ NO CODE SPAN INSIDE THE BOLD.  LESSONS.md #13: a `code span` inside `**...**`
%% terminates the emphasis early and leaves literal asterisks on the page, and
%% check.mjs fails on a surviving `**`.  The word `unsafe` is bare inside the bold
%% and backticked outside it, on purpose.
%% ⚠ The closing clause ("the size of what you have to get right, not what happens
%% when you get it wrong") replaced a repeat of level 1's "a region you can point
%% at and put a reviewer in front of", which sat two paragraphs above.
%%
%% ⚠⚠ THE "WHAT FRACTION OF A REAL PARSER IS UNSAFE" ADMISSION IS ALSO A COLD-READ
%% REPAIR: "If the answer is 'every hot path', then I'm on unsafe Rust's rules
%% across the codebase and section 3 was decoration."  This corpus cannot answer
%% it.  Saying so in one paragraph costs less than the reader noticing we did not.
%%
%% ⚠⚠ THE BINARY SEARCH'S Ir-VERSUS-CLOCK GAP IS UNEXPLAINED AND THE TEXT NOW SAYS
%% SO.  It used to end "neither means anything without the other", which is a rule
%% and not an explanation; the reader called it the most interesting fact in the
%% section and the explanation a non-answer.  ⚠⚠ DO NOT SUPPLY A MECHANISM.
%% p07/NOTES.md gives none for the R3 gap: the one conversion-factor sentence that
%% ever existed is WITHDRAWN (:193-196, :1200-1205); the branch-mispredict result
%% (:1149-1151) and the dead cache explanation (:1155-1159) are about the `cmov`
%% control, a different rung pair; and :1418 records an 8% unexplained layout band
%% on R4 alone, larger than R3's published `large` gap.  The only licensed extra
%% is NOTES.md:511-518's "the input where the kernel actually spends its time",
%% which is why the large input is named.  An honest "we cannot explain it" is the
%% strongest thing available and it is what ships.
%%
%% ⚠ GLOSSES ADDED AT FIRST USE: "window" (the stretch of buffer the function was
%% handed) and "pinned" (dissolved into "the prover's library" -- the term is
%% gone, so do not re-add a gloss for a word that is no longer there).
%% ⚠ THE \src{} MARKER IS DELETED.  Repo paths the reader does not have "read like
%% a build artifact leaked into the prose"; two of a hundred claims carried one.
%% ⚠ NO REFERENCE TO EARLIER VERSIONS OF THIS PAPER, ANYWHERE, IN ANY FORM.
\section{“The compiler can't always see what I can.”}
\label{sec:limits}

Correct — and where it cannot see it, you pay on every operation. Three of those ten really are the check. Go looking for a cheaper way to write both versions of each, and one of the three survives the search.

Start with the one that does not survive at all. A bounded stack pays 359 instructions a call on the small input and 626 on the large, and that is the check. You can make it vanish, and how you do it should bother you: add one line at the top of the loop that can never fire — a clamp the code already guarantees — and the optimiser then removes the real test, all of it, on both sides. Note the direction: a line added, not a check deleted. Nor is it free, the clamp costing two instructions for every push it turns away, which on the large input leaves the clamped version +502 against unsafe Rust. The bill moved rather than went. And the +5 that survives is a different check, guarding the reslice of the window — the stretch of buffer the function was handed to work inside.

Next, the one where the number turns out to be about us. A bitset — one bit per member, packed sixty-four to a machine word — ships at +13,756 and +48,885 instructions a call; on the large input that difference alone is twice what the whole unsafe version costs, so the safe one costs three times as much all in. It is also the second dearest of five allowed ways of writing the safe version. The cheapest is +263 and +854 — a fiftieth of what we shipped — and the line-for-line port from the last section is another of the five, cheaper again than the one we shipped as tuned. Its own notes call that span the sharpest illustration in this project of why a published spread cannot carry a safety claim. The other side was searched and came back empty: every route to a wider load is either unsupported by the prover's library or ruled out by the specification. So the whole span sits on the safe side, which makes a safety number here mostly a statement about which safe version somebody picked. And the +263 does not ship without this — it comes from a chunked fold the prover's library has no specification for, so the safe versions can reach a way of writing it the unsafe ones are not allowed to use. A permissions artefact, not a code win.

Do not read that span as meaning the bill is imaginary, though, because this is the program where a stopwatch agrees with the instruction count: on the small input the shipped version's +205.6% of instructions buys the same figure again in measured time, which its own notes call no discount at all, and on the large it keeps only about a tenth off.

Now the one that survives. A binary search pays 3,015 instructions a call on the small input and 10,025 on the large, and it jumps around the array by a rule the optimiser cannot follow, so there is nothing to hoist the test out of and nothing to fold it into. Four safe versions were tried, and the distance from the cheapest to the one shipped is one instruction per probe — a single `lea`. Both candidate unsafe versions were tried too: one is dearer, and the only cheaper one is disqualified because the version carrying the proof cannot dereference a raw pointer directly. Swept across array sizes the gap settles between 42% and 47% of the work, and it climbs with the array rather than shrinking, in all six query distributions.

Then put a stopwatch on it, and the same gap is +13% of the time on the small input and +1.6% on the large — and the large is where this function actually spends its time. That is the most interesting fact in this section and we cannot explain it: this project measured both figures, checked that both survive re-running, and never established where the rest goes. What it insists on is that neither number may be quoted without the other. Quote the instruction figure alone and you are quoting a cost nobody here has shown anybody paying.

So the rule underneath is real: when the fact that justifies the check is not something the optimiser can see, you pay for it on every operation. What the three say together is more awkward. A check's bill can be dissolved by one added line, or be mostly a matter of which safe version somebody wrote, or be genuine and survive a clock — and you cannot tell which from the number. Where you can tell, `unsafe` is the answer: a block in which you tell the compiler you have checked this by hand, scoped to a region you can point at.

%% Q3.1 -- the objection the section's last sentence just created, and a sceptic
%% named its absence as a reason to discard the whole report: "Any document that
%% presents `unsafe` as a clean hatch you open once, and never discusses that
%% unsafe Rust's aliasing and provenance rules are in places stricter and less
%% settled than C's, is a document written by someone who hasn't had to defend
%% the hard case."
%%
%% ⚠⚠ IT MAY NOT BE ASSERTED IN OUR OWN VOICE -- CLAIMS.md §3.9 forbids
%% editorialising about a language without a measurement.  It is attached instead
%% to the two things that ARE evidence: the published discipline Miri checks
%% \cite{stackedborrows20}, and what Miri reported.
%% ⚠⚠ MIRI'S SCOPE IS MOST OF ITS MEANING AND EVERY CLAUSE IS MANDATORY: the
%% blocked runs at the 180-second budget, no seed pinned, no flags set, and Miri
%% ONLY EVER RUNS THE UNSAFE RUNG (CLAIMS.md §1.18).  And §1.11: "reported
%% nothing", never a clean verdict in our own voice.
%% ⚠ THIS IS MIRI'S FIRST USE AND THEREFORE ITS GLOSS.  §5 glosses it a second
%% time, nearly verbatim; that duplicate is the one to delete, not this one.
%%
%% ⚠⚠⚠ THE ARITHMETIC TRAP HERE HAS NOW FIRED TWICE AND THE FIX IS STRUCTURAL.
%% This paragraph used to print a live `\num{totals.passing.miri_runs}` and then
%% break it down as "192 executed and 2 blocked".  192 + 2 = 194, which was the
%% total WHEN THE BREAKDOWN WAS WRITTEN; the corpus has since gone 26 -> 27
%% passing programs and the live total is 202, so the page said 202 and then
%% accounted for 194 of them.  ⚠ THE FIX IS NOT TO FREEZE THE TOTAL.  It is to
%% state only the part that does not need adding up: the total stays live, and
%% the exception is stated as a count of blocked runs, which is re-derivable and
%% needs no subtraction to be true.  Re-derived this session against
%% results/gate/*.json: 202 runs, 200 executed, 2 blocked (p01 on `large.bin`,
%% p42 on `large.bin`, both the real 180 s budget, both declared in advance in
%% `miri.blocked_reason`).  ⚠ If you ever want the executed count on the page,
%% expose it as a `\num{}` path in build_data.py first -- do not type it.
%% ⚠⚠ NO CODE SPAN IN A HEADING, EVER.  Section and subsection titles render
%% twice: through inline()/md() in the h2/h3, and RAW into the outline that
%% paper.js:262-267 builds from b.text.  The outline does not run md(), so a
%% `code span` in a title reaches the page as two literal backticks and
%% check.mjs fails with "a code span reached the page through something that
%% does not run md()".  This heading said `unsafe` in backticks and did exactly
%% that.  The word is glossed twice before this point and needs no markup.
\subsection{“So I write unsafe and I'm back on C's rules.”}

No. You are on stricter rules, on rules that are still being written down — and the price of breaking them is the one you already know.

Say that plainly, because nothing else in this report does: **a mistake inside an unsafe block is the same class of memory corruption you get in C.** The same overwritten neighbour, the same quietly wrong answer, the same thing an attacker can stand on. There is no net under the block; the compiler stopped checking because you told it to. What the keyword changes is the size of what you have to get right — not what happens when you get it wrong.

What unsafe Rust holds you to about aliasing and provenance — which references may be live at the same time, and where a pointer is allowed to have come from — is not C's rule set. The discipline Miri enforces by default arrived as a research paper \cite{stackedborrows20} rather than as a clause in a standard, which is the sense in which it is unfinished. Every unsafe version here was run under Miri — an interpreter that executes Rust hunting for undefined behaviour, the class of mistake where the language stops promising anything about what happens next — with that discipline enforced as it goes. \num{totals.passing.miri_runs} runs, no undefined behaviour reported.

The small print is most of what that is worth. Two of those runs never actually ran: they hit a three-minute budget and were killed, so those inputs were never checked. Nobody pinned a random seed or turned on any of Miri's optional checks. And Miri only ever runs the unsafe version, so no safe version here has been under it. What the number says is that these functions satisfy today's version of a rule set that is not the one you know and is not finished. It does not say that rule set is easy to live with, and nothing here measures how often somebody gets it wrong.

And the question that decides how much of this matters to you, we cannot answer: what fraction of a real parser ends up inside `unsafe`. Every program here is one function, and which version it is was our choice rather than the code's. If for your parser the answer is *every hot path*, you are on the rules above across your codebase and section \ref{sec:checks} was decoration. Nothing in this set would tell you, and we will not guess.
