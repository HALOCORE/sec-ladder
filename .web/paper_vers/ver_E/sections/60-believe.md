%% Q6.  The reader has now been handed five answers and is entitled to ask what
%% the apparatus behind them is worth.  ver_C's version of this material scored
%% 7-9 on every cold read -- the best writing in three framings -- and it is here
%% as an ANSWER TO AN OBJECTION rather than as a confession appended to the end.
%%
%% ⚠ PAST TENSE, AND SAY WHEN.  ver_B shipped the first of these in the present
%% tense and it had already gone false: the generator reads the field today.
%% ⚠ "Twenty-two" and "twenty-six" are frozen as prose ON PURPOSE.  They describe
%% a past event, so a live \num{} would silently make them false as the corpus
%% grows -- which is the opposite of what the live-value format is for.  ⚠ THE
%% TWENTY-SIX IS ALSO THE ANALYSED SET \ref{sec:setup} WARNS ABOUT: the same
%% number, frozen for the same reason, and this is the one place where the event
%% being described is what makes it frozen rather than the denominator.
%% ⚠ THIS SECTION KEEPS ITS APPARATUS WORDS BECAUSE THE APPARATUS IS ITS SUBJECT
%% -- but they are still glossed: "our own machine-readable records", not "the
%% gate's records".  A reader who has come this far is being told how the
%% sausage failed, and they still should not need our vocabulary to follow it.
\section{“Why should I believe any of your numbers?”}
\label{sec:believe}

Not entirely, and here is the specific reason rather than a general disclaimer: twice, a check of ours turned out to be a check that could not have failed.

The small one first. We changed twenty-two of our own machine-readable records, regenerated every table, and quoted the byte-identical output as evidence that nothing had moved. It was byte-identical because the generator was reading a different key and could not have noticed whatever the change had been.

> A residual of exactly zero is not a strong pass. It is the signature of a test that could not fail.

%% ⚠⚠ FACT-CHECK REPAIR, AND THE NUMBER WAS UNDERCOUNTED.  This read "five
%% reviewed, quotable results had gone missing".  NINE went missing and were
%% restored; the DIRECTION claim is graded for five of them, the other four
%% being smaller and ungraded.  results/SYNTHESIS.md:36-37 and TASK_112 both use
%% the safer form -- "nine reviewed results, five of them in one direction" --
%% and it is the form to copy.  ⚠ Do NOT cite RECAP.md for this: it carries a
%% competing stale version ("39 findings to four results").
%% ⚠⚠ THE DIRECTION WAS INVERTED HERE AND THE GAPS REVIEW CAUGHT IT.  The
%% sentence used to end "of the five whose direction was graded, every one
%% flattered safe Rust" -- literally true, and a reader takes the opposite
%% meaning from it, because the results were MISSING.  Dropping five results that
%% flatter safe Rust makes a document biased AGAINST safe Rust.
%% results/SYNTHESIS.md:1250-1263 states the mechanism outright: "Nineteen
%% retractions had trained this project to distrust 'safety is cheap', and the
%% reflex removed the evidence for it."  ⚠ THE TRUE VERSION IS THE BETTER
%% ADMISSION, because it is the one a reader would not have guessed: our bias ran
%% against the conclusion we are accused of wanting.  Do not "simplify" it back.
The second one matters more, because the document it happened to was correct. When this project compressed twenty-six programs into four headline results, its own later review found nine reviewed results missing — and, worse than the count, a direction. Every one of the five whose direction was graded was a result that *flattered* safe Rust. Losing them made that document unfair in the direction nobody watches for: a long habit of retracting claims that safety was cheap had trained this project to distrust the sentence, and the reflex went on to delete the evidence for it.

> Coverage bias has no arithmetic signature. Every figure in the biased version reproduced correctly on the pass that found the bias, so checking a document's numbers cannot detect it. The only check is a different question, asked of a finished document by someone who did not write it: which way do its gaps point?

%% ⚠⚠ A THIRD BEAT WAS CUT HERE ON THE OWNER'S INSTRUCTION AND MUST NOT RETURN.
%% It narrated a claim a PREVIOUS DRAFT OF THIS PAPER had withdrawn -- a table of
%% what each tool catches, true only after six of its twelve rows were dropped.
%% The finding was real and the writing was good, and it goes anyway, because a
%% report has to be self-contained: a reader is owed the report, not its revision
%% history.  ⚠ Nothing measured is lost -- both retractions above are about the
%% RESEARCH's own apparatus, which is this section's actual subject.
%% ⚠ It also fixes a defect a cold reader named independently: the honesty stops
%% reading as honesty and starts reading as technique "roughly at the second
%% blockquote", so a third confession was past the point of return anyway.
%%
%% ⚠⚠⚠ THE CLOSING PARAGRAPH REPLACED A MOOD WITH TWO NAMED PROPS, AND THAT WAS
%% THE WHOLE COMPLAINT ABOUT THIS SECTION.  It scored 5/10 and was skimmed.  The
%% old ending -- "take every figure here as a bound with one end propped up by a
%% decision of ours" -- drew: "That is a mood, not a correction.  WHICH figures?
%% Propped WHICH WAY?"  Both answers exist and are already in the paper, so the
%% ending now names them: the identity rule holds the unsafe baseline high (the
%% 17,526 in \ref{sec:unsafe}), and the search was one-sided in the same direction
%% (\ref{sec:checks}'s tuning node).  Both props raise the unsafe side, so the
%% direction of our error is stateable and it is stated.  ⚠ Do not re-abstract it.
%% ⚠⚠ "NINETEEN RETRACTIONS" IS CUT, PER CLAIMS.md §1.20.  No source in the tree
%% gives a denominator for it -- SYNTHESIS.md:28-31 and :925-928 both state the
%% count bare, and §6 enumerates only eight numbered traps, so the figure cannot
%% even be checked by counting.  ⚠ THE TRAP: SYNTHESIS.md:1094-1097 has a DIFFERENT
%% nineteen that DOES carry a denominator -- 19 of 20 CVEs rejected at the
%% admission bar.  It is not this one.  The mechanism survives without the count,
%% and the count was reading to a cold reader as instability: "If nineteen
%% published results were wrong, I want to know whether any of them are in this
%% document."
%% ⚠ The first beat is COMPRESSED, not cut: the brief's instruction was to keep
%% the DIRECTION finding at full strength and shrink the internal process bug,
%% which the reader had no way to care about ("I have never seen that document").
So here is our answer for this document, and it names which figures are propped and which way rather than leaving you a mood. Every safe-against-unsafe number here has one end held up by the identity rule — that is the 17,526 instructions a call section \ref{sec:unsafe} describes being refused — and the searching leaned the same way, because a cheaper safe version costs somebody an edit while a cheaper unsafe one has to come back out through a proof. Both props raise the unsafe side. So where a figure in this report is wrong, the way to bet is that safe Rust comes out of it better than it deserves.

Ask the question of this document anyway. We cannot ask it of ourselves.
