%% Q4.  The node Q3's answer forced: it introduced `unsafe`, so the reader's next
%% sentence is that you have handed the safety back.  The answer is the sixth
%% version, and the ONLY answer that is not a dodge.
%%
%% ⚠⚠ STRUCTURE, AND IT IS THE OWNER'S INSTRUCTION RATHER THAN A PREFERENCE.
%% EVERY section and subsection here runs THREE MOVES AND NOTHING ELSE:
%%   1. THE ANSWER -- one short paragraph, the claim, no evidence and no hedge.
%%   2. WHY YOU SHOULD BELIEVE IT -- the smallest evidence carrying THAT claim.
%%   3. WHERE THAT ANSWER BREAKS -- as its own visibly separate final beat.
%% The test on every paragraph: does it support the move-1 sentence of the node
%% it sits in?  If it supports some other true and interesting thing, it becomes
%% a sub-objection or it goes.  This section was a fused stream before that rule;
%% the range parser has been promoted OUT of Q4.2 into its own objection for
%% exactly that reason, and Q4.2 now runs ONE demonstration end to end.
%%
%% ⚠⚠ AND THE RULE THAT IS ABSOLUTE: THE PAPER MAY NOT REFER TO EARLIER VERSIONS
%% OF ITSELF, anywhere, in any form.  No "an earlier draft", no "two drafts had
%% it backwards", no "three readers were misled".  A reader is owed the report,
%% not its revision history.  (The retractions in the *believe* section are a
%% different thing: those are the RESEARCH project's own apparatus.)
%%
%% ⚠ NO VERIFIER COUNTS in this paper.  "It will not build" plus the real error
%% text carries strictly more than "9 verified, 1 errors", which a reader cannot
%% interpret and which counts items rather than obligations discharged.
%%
%% ⚠ LEVEL-1 EDIT, MANDATED BY THE FACT-CHECK: the "will not build" claim NAMES
%% THE RECORD WALKER.  That same error string is the delete-arm in thirteen
%% patterns, so an unnamed claim is unlocatable and a reader cannot go check it.
%%
%% ⚠ CLAIMS.md:170-171 requires saying ONCE, before leaning on such a number,
%% that a verifier's count is of ITEMS -- functions, loop bodies, sub-proofs.
%% The count itself is cut entirely (it is a size proxy: it correlates 0.894 with
%% syntactic size and ranks a dead-code arm above the arm carrying the
%% mechanism), so what survives is the LESSON, folded into the closing line where
%% it costs six words instead of a paragraph in move 2 that answers nothing the
%% heading asked.
%% ⚠ IF A SUBSECTION IS EVER REORDERED, THAT CLOSING LINE MOVES WITH IT.  It is
%% the only place in the paper where a level-1 line enumerates its own children.
%% ⚠ "obligation" IS GLOSSED WHERE IT IS USED AND NOWHERE ELSE.  The vocabulary
%% rule in \ref{sec:setup} bans apparatus words in the answers; this one is the
%% prover's own word for the thing the reader has to understand, so it is glossed
%% in place ("one thing the prover has to show") rather than replaced.
\section{“Then you've given up the safety. That's just C with extra steps.”}
\label{sec:unsafe}

It would be, if `unsafe` were the last of the six versions. It isn't.

Verus is a verifier for Rust. Separately from the code, and in logic rather than in Rust, you write down what the function must do and where it is allowed to read; the prover then has to reconcile the two, and if it cannot, the code does not compile. Across the versions shipped here every obligation — one thing the prover has to show — is discharged, with no errors.

So the `unsafe` block is not unchecked. It is to-be-verified.

And the check stops being something anyone has to remember. Delete the bounds test out of the record walker's proved version and it does not panic — Rust's word for a program stopping itself on purpose — because it never runs. It will not build: `invariant not satisfied before loop`, an invariant being what a loop must keep true every time round. In C that check is a line somebody has to not forget, and nothing tells them when they did.

Three things before you believe any of it, and they are the rest of this section: that zero is ours rather than the world's; a proof proves only what somebody wrote down; and the price is real but is not counted in instructions.

%% ------------------------------------------------------------- LEVEL 2 ----
%% Q4.1.  Provoked by ONE sentence above: "the proved code compiles to the same
%% bytes as the unproved code".  A reader with twenty years of systems work does
%% not believe a difference of exactly zero; they ask whether it was measured or
%% arranged.  It was arranged, and they have to hear that from us first.
%%
%% MOVE 1 = the zero is a rule, not a result.  MOVE 2 = the rule, and why it earns
%% its place -- what it BUYS comes before what it COSTS, because a tautology
%% confessed with no reason attached reads as a rigged benchmark.  MOVE 3 = the
%% refused saving, which is what the rule costs us.
%%
%% ⚠⚠ NEVER "ours is held too high" -- readers take that phrasing as a BOAST.
%% Lead with "slower than it needed to be", the same fact pointed at ourselves.
%%
%% ⚠ FACT-CHECK, SCOPE THAT MUST SURVIVE: the digest pin is NOT universal.  25 of
%% 27 pin `-O3 exact`; the two that do not are p36 and p29, both `norel` on
%% purpose -- p36 because a `spec fn` declared in a trait is codegenned as a stub
%% occupying a vtable slot (re-checked this session against data/index.json's
%% `identity_o3`).  The \num{} pair carries that scope and BOTH ENDS ARE LIVE, so
%% the ratio cannot go stale as more programs land.  The
%% SENTENCE explaining p36's ghost stub is CUT: the earlier cost section already
%% tells the reader about it, and it answers nothing this heading asked.
%% ⚠ FACT-CHECK: "Verus cannot express C strings at all" is RETRACTED IN-TREE, so
%% the text says the twin "does not verify as written" and never states an
%% impossibility.  The paragraph pricing the route through -- four hand-written
%% trusted items -- is CUT under the move-2 test: it supports "Verus's limits are
%% priced rather than absolute", which is a different and later question.
%% ⚠⚠ THE 17,526 IS SIZED FROM ITS OWN SOURCE AND THE SIZING IS LOAD-BEARING:
%% p11-nul-scan/NOTES.md §10b is headed "the gap it hides is 35%", against a
%% shipped unsafe cell of 50,174 Ir/call -- so "about a third of that function's
%% entire cost" is the tree's own arithmetic, not ours.  Without it the reader
%% has a five-digit number and no way to tell whether we gave up anything.
%% ⚠ THE PULL-QUOTE NO LONGER SAYS "identity pin".  It said it, and it was the
%% one line in the section a reader could not decode without our vocabulary --
%% which is the exact defect this pass exists to remove.  The contrast survives
%% intact: not-looking-hard-enough versus not-being-allowed-to-look.
%% ⚠⚠⚠ THE DISCLOSURE MOVED TO \ref{sec:slower} AND MUST NOT COME BACK HERE.  The
%% target reader hit this subsection two thirds of the way through the paper and
%% wrote: "You told me a rule and let me read it as a result for two thirds of the
%% document... you let me spend it for 140 lines."  \ref{sec:slower} now states
%% the rule where the zero is first claimed; THIS node keeps the ARGUMENT -- what
%% the rule buys and the 17,526 it refused -- which is the part that needs the
%% reader to already believe the zero.  Move 1 is now a two-sentence handoff on
%% purpose.  ⚠ Do not restore the "\num{identity_exact} of \num{patterns}" recap
%% here: it is stated once, upstream, and a second denominator in this position is
%% exactly the bookkeeping the reader stopped tracking.
\subsection{“Is that zero real?”}

No, and section \ref{sec:slower} said so rather than leaving it to here. What it did not say is what the rule buys and what it costs.

It buys this: without it we would be pricing the proof's effect on the compiler rather than the cost of the code, and a proof that moved the code could hide the very difference being measured.

It costs one side of every comparison in this report. On the NUL-scan program somebody found a cheaper way to write the unsafe version — the standard library's own C-string scan, wrapped around the same fold — and measured it 17,526 instructions a call cheaper on the large input, about a third of that function's whole cost. Dearer on the small one, so the saving is the large input's. It was refused, because its proved twin does not verify as written. So the unsafe baseline there is slower than it needed to be, and every safe-versus-unsafe figure in this report reads more kindly to safe Rust than the program warrants.

> Not searching hard enough is one way to get a comparison wrong. This is the other one: on that side, we were **not allowed** to look.

%% Q4.2.  Provoked by level 1's closing line.  The reader's own form of this is
%% the sharpest sentence anyone said about the project -- "a wrong specification
%% in a proved kernel is silent memory corruption with a certificate attached.
%% How do you catch a wrong spec?" -- and it is answered head on, in their words,
%% before any evidence arrives.
%%
%% ⚠⚠ ONE DEMONSTRATION, RUN ALL THE WAY THROUGH.  This node used to open on the
%% range parser and then switch programs; that is two half-demonstrations of one
%% finding, and the range parser is its own objection below now.  The bitset is
%% the one that stays, because EVERY instrument in the project can be pointed at
%% it, which is what makes the table possible at all.
%%
%% ⚠ CLAIMS.md §1.17-18, three scopes discharged in seven words by "the same
%% character, in each version's own copy": the bounds-check verdict is on the
%% SAFE RUST mutants, the sanitizer verdict is on the HARDENED C one at gcc
%% `-O1`, and Miri ran the UNSAFE one, on THREE inputs.  And "Miri reported
%% nothing" -- never a clean verdict in our own voice.
%% ⚠ MIRI IS A BARE MENTION HERE ON PURPOSE: its full gloss lives at first use in
%% the limits section.  ONLY THE DEFINITION IS DROPPED -- all three scope clauses
%% survive, and none of them may be tidied away with it.
%%
%% ⚠ Do not say "wrong on every input": it is four of the five shipped ones.  On
%% the fifth EVERY version returns 0, correct ones included, because that input
%% declares a shape the window cannot hold and never reaches the query loop.
%%
%% ⚠⚠⚠ THE MOST DANGEROUS SENTENCE IN THIS SECTION.  BOTH proof rows carry the
%% same added hint line the shipped program never needed -- the memory-rules-only
%% variant is BUILT FROM the hinted one.  The pure one-character mutant fails on a
%% PRECONDITION, for a reason about the proof rather than about the bug, so
%% without the hint the memory-only proof does NOT cheerfully certify the typo
%% either.  ATTACH IT TO BOTH ROWS.  Attached to one it makes the prover look
%% better than the evidence does, and what survives is the DIFFERENCE BETWEEN THE
%% ROWS, which is all the story ever needed.
%% ⚠⚠ IT NOW LIVES IN MOVE 3, WHICH IS A DELIBERATE TRADE AND NOT AN OVERSIGHT.
%% A cold reader stopped at it when it sat one sentence after the payoff as a bare
%% retraction: "I do not know what a hint line is."  In move 3 it arrives under
%% its own framing, as a limit on the whole answer, which is the shape the owner
%% asked for.  Do NOT split it across both positions -- stating it twice is
%% exactly the repetition complaint.
%%
%% ⚠⚠ FACT-CHECK, AND "THREE ASSERTIONS AWAY" IS RETRACTED -- IT IS NOT IN THE
%% TREE.  The spec-move edit is exactly TWO added `assert`s over FOUR physical
%% lines (`controls/gen_controls.py`:371-394: a 3-line `assert(pow2(7) == 128) by
%% { lemma2_to64(); }` and a 1-line `assert((q >> 7) <= (q >> 6)) by
%% (bit_vector);`), plus `word_of` moving from `/ 64` to `/ 128` at :368-370.
%% Nothing anywhere states a "three assertions away from the shipped proof"
%% distance, and the two arithmetically available readings disagree (3 asserts in
%% the shipped index/mask chain; 2 obligations between `18 verified` and the
%% mutant's `20 verified`).  ⚠ THE SIZING THAT IS IN THE TREE AND IS BETTER:
%% p09/NOTES.md:491-493 -- the HONEST `q >> 6` obligation costs "three ghost
%% lines, no `nonlinear_arith`, no new trusted item, Z3 first try".  So the lie's
%% repair is LARGER than the whole correct proof of the same step, which is the
%% point the paragraph was making all along and now says with a number a reader
%% can hold.  ⚠ Do not reinstate a bare unsized "three assertions away".
%%
%% ⚠ \cite{msrc19}\cite{chromium} appear ONLY where we say this bug is not in the
%% class those papers count.  Never as motivation.
\subsection{“What does it actually prove?”}

Memory safety. Not that the answer is right — and you already know why that distinction is the whole game: a wrong specification inside a proved function is silent memory corruption with a certificate attached, which is worse than C, because in C nobody trusted it. So how do you catch a wrong specification?

Here is the sharpest case we have, one character wide. To find bit `q` in the bitset you go to word `q >> 6`, which is `q` divided by sixty-four. Here is the real line, from the tuned safe version, with the guard above it that keeps `q` inside the set:

```rust
        if q < nbits {
            let w: u64 = load_u64(win, ws + (8 * (q >> 6)) as usize);
```

Now type a `7` where the `6` is. Dividing by a hundred and twenty-eight instead of sixty-four gives a smaller word number, and a smaller number cannot overshoot where the right one did not, so the index is still inside the array. It is the wrong word, not an illegal one. The program answers the query and exits 0.

On four of the five inputs shipped with that program the answer is wrong; on the fifth nothing reaches the query loop and every version returns 0.

We put the same character into each version's own copy and pointed everything this project has at the result. Nothing ever leaves the allocation, so nothing that watches allocations has anything to say — including the sanitizer, a tool that checks every memory access as the program runs and shouts when one leaves its allocation, run here on the hardened C copy at `-O1`, and Miri on the unsafe copy, on the three inputs it was given.

| what was pointed at it | what it did |
|---|---|
| the bounds check safe Rust compiles in | never fires; exit 0, wrong answer |
| the sanitizer, on the flags our own checking script uses | silent on every input; exit 0 |
| Miri | exit 0, reported nothing, wrong answer |
| the proof, with only the memory rules written down | verifies the buggy version |
| the proof, with the answer written down too | refuses to build: `invariant not satisfied` |

The last two rows turn on the two halves of the definition above — what the function must do, and where it is allowed to read. You can write one without the other, and that is the whole difference: with only the memory half present the prover certifies the typo, because the typo breaks no memory rule.

So move the specification to match the typo, and the prover verifies the bug and reports nothing wrong. That edit is not one character either: it is the specification's own arithmetic, plus two more assertions over four lines of proof — more proof than the honest version of that same step ever needed, which was three lines. So this is not *one more character*. It is the author's misunderstanding reaching the specification, and paying for the privilege.

> A proof is a proof of what you wrote down.

That demonstration has a soft edge, in the two proof rows. Both carry an extra line put there only to help the prover along, which the shipped program never needed; take it away and the prover balks either way, for a reason about the proof rather than about the bug. So those two rows are worth the difference between them, not either row alone.

The table flatters the result too. Every instrument in it except the last watches the same boundary, the edges of an allocation, so four of them agreeing is not four independent confirmations. They are the right tools for the class of bug people mean when they say most serious security bugs are memory-safety bugs \cite{msrc19}\cite{chromium}; this one is not in that class, and no input could put it there, because the index never leaves the bitset. The broken copy rebuilds from a script we commit, and nothing certifies it.

%% Q4.3.  PROMOTED OUT OF Q4.2, where it was a second demonstration of the same
%% finding sitting in front of the first one as a preamble.  As its own objection
%% it earns its place: "you made that bug up in a lab" is exactly what a sceptic
%% says after being shown a one-character mutant, and this is the section's only
%% real-CVE artefact.
%%
%% ⚠ CLAIMS.md §1.7: NEVER "the CVE port verifies clean" unqualified.  With the
%% functional specification present exactly one obligation fails and it is the
%% FUNCTIONAL one; every memory-safety obligation discharges.
%% ⚠⚠ CLAIMS.md:206-209 -- AN OVER-GENERALISATION A REVIEWER ALREADY CAUGHT HERE
%% ONCE.  On a one-window input the excess bytes are the attacker's OWN
%% (`patterns/p17-http-range/NOTES.md` 253-261: *"'Leak' was the wrong word for
%% it; memory-safe and functionally wrong is the right one"*), and the row that
%% pattern shipped as its demonstration DISCLOSES NOTHING (:29-31).  Only the
%% cross-window pair reaches a victim.  That scope IS this node's move 3, which is
%% where it belongs and where it stops reading as a retraction.
%% ⚠ "no `unsafe` outside the one trusted accessor" -- NOT "no `unsafe` anywhere".
\subsection{“Is that just a toy typo?”}

No. The one-character version is a specimen, but the same shape shipped as a real vulnerability, and that program is here: the HTTP range parser, a port of a suffix-range parser missing one test. Guard the index against the window the function was handed — exactly what a bounds check buys you and no more — and every memory-safety obligation discharges. The only one that fails is the functional obligation, the one that says what the answer has to be. What comes out is memory-safe and functionally wrong: it reads outside the range it was asked for, with no panic, no sanitizer report, and no `unsafe` anywhere except the one accessor the proof takes on trust.

How much that costs you depends on who is at the other end, and that program's notes are stricter than a headline would be. On a single window the excess bytes are ones the caller wrote itself, so *leak* is the wrong word for that case. It takes a second window, belonging to somebody else, before the output becomes a function of a victim's bytes.

%% Q4.4.  Provoked by the three nodes above: the reader now accepts that the proof
%% is real and narrower than advertised, so the only question left is the price.
%% It ENDS ON A NAMED ABSENCE, which is also the handoff into Q5.
%%
%% ⚠⚠ FACT-CHECK, TWO CORRECTIONS THAT RUN AGAINST US AND ARE STATED IN OUR OWN
%% VOICE.  (1) "Proof text counts mostly comments" is FALSE -- comments are 38.2%
%% of the proof files, and stripping comments and blanks from BOTH sides moves the
%% multiple UP, not down.  (2) "No compile-time and no authoring-hours data
%% exists anywhere" is FALSE -- one pattern records ~2s of prover time, another ~8
%% minutes of engineer time.  The true and stronger form is the absence of a
%% COLUMN in any measured record.
%% ⚠⚠ THE STRIPPED FIGURE ITSELF (431.6%) IS NOW CUT, AND THIS IS A LIVE/FROZEN
%% CALL RATHER THAN A SOFTENING.  431.6% was computed when the with-comments
%% ratio was 404%; that ratio is a LIVE \num{} and reads 401% today, so printing
%% the frozen 431.6 beside it invites a reader to difference two numbers that
%% were never measured over the same set of programs.  THE FACT THAT CARRIES THE
%% PARAGRAPH IS THE DIRECTION -- the comments excuse makes it WORSE -- and the
%% direction is stated flatly.  ⚠ If you want the digit back, expose a
%% comments-stripped ratio as a \num{} path in build_data.py; do not retype 431.6.
%%
%% ⚠⚠ TWO PRICES HAVE BEEN CUT FROM THIS NODE AND NEITHER COMES BACK WITHOUT
%% SOMETHING ELSE GOING.  (a) The proof-enabling line on the NUL-scan program --
%% one instruction per scanned byte, 4,265 on the large input, 8.5% of that
%% kernel, shipped described as free until somebody deleted the line and measured,
%% with the range parser's zero-instruction route beside it.  All true and sourced
%% (`patterns/p11-nul-scan/NOTES.md` 432, 456); it goes because the finding under
%% it -- a proof is not free -- is already demonstrated once, in Q4.1, by the
%% refused saving, and because five qualifying clauses around one small figure is
%% exactly what "no number survives its own paragraph" describes.  (b) The `p42`
%% finding that nothing in the gate checks an `ensures` means what its prose says:
%% true, sharp, and a SECOND demonstration of the claim the `assume_specification`
%% trap below makes more concretely.  One demonstration beats two halves.
%%
%% ⚠ CLAIMS.md §1.16: the proof and trusted-base totals are the SHIPPED versions.
%% With the one control included they are 357/110/235.
\subsection{“What does it cost to write, and to keep?”}

Real, not in instructions, and the number that would actually decide it does not exist.

Across the shipped versions, proof text runs to \num{totals.passing.proof_text_ratio_pct}% of the unsafe versions' source lines — four times as much proof as code. The obvious escape hatch, that most of it is comments, goes the wrong way: strip the comments and the blanks off both sides and the ratio gets worse. It is not uniform either, and the cheap end is genuinely cheap: on two programs the proof went through first try and left the engineer session budgeted for it unused. Underneath all of it sits a base the prover takes on trust and never checks — \num{totals.passing.tcb_items} hand-written items, sitting in turn on a standard library whose own trusted surface is larger and is not counted here at all.

A trusted item is not only a price, though. It is the place where the proof stops and somebody's word starts, and Verus makes that easy to get wrong: meet a function it has no specification for and it prints one for you to paste, carrying no preconditions and no postconditions at all. Paste that for a raw-pointer read and a one-megabyte read off the end of an array verifies. So does a null dereference.

And the number you would actually want, we do not have. Two programs record a figure in prose — a couple of seconds of prover time on one, about eight minutes of somebody's time on another — but no measured record carries a compile-time or an effort column, and nobody ran the experiment you would ask for next: change one line in a verified function, and report how many lines of proof broke. So every price above is a floor, and what it takes to keep a proof alive across three years of changes is not in this report.
