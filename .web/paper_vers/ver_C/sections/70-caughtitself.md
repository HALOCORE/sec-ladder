%% ver_C section 7 — the retractions, including this report's own.
%%
%% ⚠⚠ PLAIN-LANGUAGE PASS. Nothing factual was dropped; the sentences got
%% shorter and the two rules kept their exact wording, because they are the
%% lines a reader quotes. See .temp/brief/PLAIN.md before lengthening anything.
%%
%% TITLE: under 12 words and still the claim. "No number caught them" is the
%% old title's "had no arithmetic signature", in words an undergraduate reads
%% without stopping, and it is true of BOTH items: the first was caught by
%% asking what would make the check fail, the second by asking which way the
%% gaps point. Neither was caught by recomputing a figure.
%%
%% WHAT THIS SECTION IS, AND WHAT IT IS NOT (OUTLINE 0.4). ver_C has no
%% limitations section: a limitation says *our evidence does not reach X*, and
%% those are filed beside the claims they bound (CONVENTIONS 2.6). A retraction
%% says *we asserted X, it was false, here is what killed it and what stands
%% instead* — convention 2.8 makes that the source of this voice's authority, so
%% it keeps its section. Standalone caveat allowance here is ZERO: every limit
%% is welded into the sentence that carries it. ⚠ If this ever starts reading as
%% a limitations section, the fix is to restore the verb: we SAID it, it was
%% FALSE, here is what killed it.
%%
%% CONTENTS ARE FIXED AT FIVE ITEMS AND THERE IS NO THIRD RETRACTION.
%%  - No count of the form "eight claims were retracted". ver_A led with a bare
%%    count and the reader's advocate flagged it as trust-destroying —
%%    "nineteen of how many?" (CLAIMS.md §1.20). No ordinal replaces it either.
%%  - NOT the 31-layout wall-clock retraction, which ver_B carried here. Its
%%    evidence is a *finding* in §3 and its rule is an *action* in §6.2
%%    (OUTLINE 0.5 item 6). Do not bring it back.
%%  - No limitation that belongs beside a claim.
%%
%% SOURCES READ FIRST-HAND AT WRITING TIME, not taken from any summary:
%%   what held     data/index.json totals, checked this session:
%%                 patterns_passing 26 of 26 with patterns_not_passing empty;
%%                 verus_verified 350 is the SHIPPED-rung figure (+7 controls
%%                 = 357), which is why "across the shipped versions" is in the
%%                 sentence and is load-bearing (CLAIMS.md §1.16 — the site once
%%                 published the larger figures while the research published the
%%                 smaller). The pass line is written as N-of-M rather than
%%                 "all", so that one pattern failing upstream makes the
%%                 sentence change rather than go quietly false.
%%   retraction 1  ../.memory/03-measurement.md:2684-2688 — entry 1 of "THE
%%                 CONTROLS THAT COULD NOT HAVE FIRED". The field is
%%                 `axiom_decls` on 22 gate records; the generator read
%%                 `tcb_items` and the word "axiom" appeared zero times in
%%                 `synthesis/`.
%%   retraction 2  ../results/SYNTHESIS.md:1147-1162, "A gap in this document
%%                 rather than in the project" — FIVE reviewed, quotable
%%                 omissions, "all of them flattering to safe Rust, none of them
%%                 awkward", plus four smaller ones; all nine restored at
%%                 TASK_112 after TASK_111 found them. The direction claim is
%%                 sourced for the five; the four smaller ones are not graded
%%                 for direction, so they are not counted into it here.
%%   exhibit A     RULINGS.md C15
%%
%% ⚠ TENSE, re-checked in the parent (ver_B shipped this in the present tense
%% and it had already gone false). `synthesis/synthesize.py` now reads
%% `axiom_decls` and publishes an `axioms` column of its own (lines 1274,
%% 1306-1311), and states the moral itself: "nothing published read it, so a
%% byte-identical regeneration was **not** evidence that nothing moved". Past
%% tense throughout, and the sentence says when.
%%
%% ⚠ "22 gate records" is a HISTORICAL figure and is meant to be frozen — it is
%% not a corpus total and is under 100, so the literal check does not see it.
%%
%% ⚠ EXHIBIT A DOES NOT RESTATE THE MECHANISM. §4 owns the coverage-table
%% retraction and carries the `retraction` environment for it, beside the claim
%% it corrects (CONVENTIONS 2.6). Naming "six of twelve rows" here would tell
%% the same story twice and would move §4's evidence out of §4. What this
%% section owns is the *argument*: the check this paper recommends is the one
%% that caught this paper.
%%
%% ⚠ The closing paragraph cites F3 — old F5, renumbered by the cut pass when the
%% summary went from ten findings to six — with NO NUMBER. The identity pin's −17,526
%% is §3's, and §7 gets the consequence only (redundancy map). The pin is
%% spelled out in place — "the rule that ties each proved version to an unsafe
%% one" — because a reader can land on this view first and `identity pin` is not
%% on the re-gloss list. `the gate` and `rung` ARE, and both are glossed in the
%% opening sentence, in six words.
%%
%% ⚠ C29 (the false-`LICENSED` count moving upstream, and the bounded stack's
%% row with it) does NOT bite this section: nothing here rests on the licensed
%% population, the ten-row tally or any cost figure. Every number in it is a
%% \num{} against data/index.json, so if the corpus moves, the sentence moves.
%% The one frozen literal is the historical 22.

%% ⚠⚠⚠ THE SECOND UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad2.md), 4/10.
%% THE TWO RULES ARE UNTOUCHED — the reader named them as one of the five passages
%% the thesis came from, and "which way do its gaps point?" as the best rule in
%% the paper.  ONE SENTENCE CHANGED, the closing pointer, and it is the fix the
%% reader cared most about:
%%   "I am told twice that a previous version of this document was biased, and
%%    never once what it said. … Refusing to show me the gap it's derived from
%%    makes the confession feel managed."
%% So the sentence now says "an earlier draft of this same document" in plain
%% words, names the mechanism in six ("six of the twelve rows were dropped"), and
%% points at §4 as the place that PRINTS the withdrawn sentence.  §4's retraction
%% box now quotes it and says whose it was.
%% ⚠ THE MECHANISM IS STILL NOT RESTATED HERE.  §4 owns the coverage-table
%% retraction (CONVENTIONS 2.6) and this section owns the ARGUMENT.  "Six of the
%% twelve rows" is the one detail imported, because without it the reader is told
%% a check was failed and never what failed it — which is the shape of hiding
%% something, in a section whose whole authority rests on not doing that.
\section{The claims withdrawn here are ours, and no number caught them}
\label{sec:caughtitself}

**Start with what held**. \num{totals.patterns_passing} of \num{totals.patterns} patterns pass the gate. \num{totals.verus_verified} items verify across the shipped versions at \num{totals.verus_errors|plain} errors, and \num{totals.adversarial_runs} hostile runs stand behind \ref{sec:nonoptional}. Now two traps in the apparatus that produced it, both ours.

\begin{retraction}{The control came back byte-identical, so nothing moved}
We added a field to 22 gate records, regenerated the tables, and the output came back byte-identical — quoted as evidence that nothing had moved. **It was byte-identical because the generator read a different key**. The field's name appeared nowhere in that generator at the time, so the control could not have fired whatever the change had been. That generator reads the field today. \src{.memory/03-measurement.md}

**The rule**. Before believing a check, ask what would make it fail — then make that happen. **A residual of exactly zero is not a strong pass; it is the signature of a test that could not fail**.
\end{retraction}

\begin{retraction}{The summary is faithful: every figure reproduces}
That was true, and it was not the question. When this project compressed \num{totals.patterns} patterns into four results, its own review found the omissions ran **systematically one way**: five reviewed, quotable results went missing, and every one of them flattered safe Rust. \src{results/SYNTHESIS.md}

**The rule, and it is the hardest one here. Coverage bias has no arithmetic signature**. Every figure in the biased version reproduced correctly on the pass that found the bias, so checking a document's numbers cannot detect it. The only check is a different question, asked of a finished document by someone who did not write it: **which way do its gaps point**?
\end{retraction}

**An earlier draft of this same document failed that check** — on its detector-coverage table, where six of the twelve rows were dropped and the gaps pointed one way. Section \ref{sec:allocation} prints the sentence we withdrew, beside the claim it corrects. The check this paper recommends is the one that caught this paper.

%% ⚠ rigour M15: this restated F5 with all three of §3's mandated corrections
%% dropped — a corpus-wide, direction-fixed, gate-certified-sounding bias claim
%% in the section whose whole subject is claims stated too broadly. §3 calls the
%% three non-optional: a SAVING FORGONE not a cost imposed, measured on ONE
%% pattern's large blob, and NOT gate-certified. All three are in the sentence
%% that follows the claim, which is where CLAIMS.md §3.4 as amended wants them.
%% ⚠⚠ FINAL CUT, ~46 words, and it is more than the ruling's "light only" for
%% this file.  The reason is the paper's own no-third-appearance rule: the
%% identity-pin finding is STATED in §3, SUMMARISED as **F3** in §0, and this
%% paragraph restated it a third time, in full, with §3's three mandated
%% corrections re-attached.  WHAT WENT: "The rule that ties each proved version
%% to an unsafe one holds our unsafe versions above the cheapest way of writing
%% them anyone has found, and it runs in safe Rust's favour throughout — a saving
%% forgone rather than a cost imposed, priced on one pattern, certified by no
%% gate."
%% ⚠ rigour M15 IS NOT VIOLATED: it forbids restating F3 WITHOUT §3's three
%% corrections, and the restatement is gone entirely rather than shortened.  The
%% **F3** citation stays on the rule it licenses, with no figure, which is the
%% redundancy map's own instruction for this section.
%% ⚠ IF IT IS RESTORED, ALL THREE CORRECTIONS COME BACK WITH IT — a SAVING
%% FORGONE not a cost imposed, priced on ONE pattern, NOT gate-certified — and
%% the pin must stay SPELLED OUT ("the rule that ties each proved version to an
%% unsafe one"), because a reader can land on this view first and `identity pin`
%% is not on the re-gloss list.
Ask it here too. **Read every figure as a bound with one endpoint held fixed by decree** (**F3**). And **quote the mechanism, not the magnitude**. Why a check survives or is optimised away reproduces on code this project never built; the magnitudes belong to one machine, one pinning rule and one pair of versions.
