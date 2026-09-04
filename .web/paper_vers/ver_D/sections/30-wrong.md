%% Story 4.  Adapted from ver_C's 70-caughtitself.md, which scored 7-9 on every
%% cold read and is the best writing in three framings of this report.  This is a
%% conversion of apparatus to prose, NOT a rewrite of the argument: the two rules
%% keep their exact wording, because they are the lines a reader quotes.
%%
%% ver_C carried these in \begin{retraction} environments.  A blog post has
%% paragraphs, so the environments are gone and the two rules are markdown
%% blockquotes -- which also keeps the "read the bold bits only" failure away.
%%
%% ⚠ PAST TENSE, AND SAY WHEN.  ver_B shipped the first trap in the present tense
%% and it had already gone false: synthesize.py reads the field today.  "22 gate
%% records" is a HISTORICAL figure, deliberately frozen, and under 100 so the
%% literal check does not see it.
%%
%% ⚠ CLAIMS.md 1.16: proof totals need the words "shipped versions".  With the
%% controls included the figures are 357/110/235, and this site once published
%% the larger while the research published the smaller.
%%
%% ⚠ The direction claim is sourced for FIVE omissions.  There were nine; the
%% four smaller ones are not graded for direction, so they are not counted in.
%%
%% ⚠ The withdrawn sentence is QUOTED.  A cold reader on the previous framing: "I
%% am told twice that a previous version of this document was biased, and never
%% once what it said.  Refusing to show me the gap it's derived from makes the
%% confession feel managed."
%%
%% ⚠ The memcpy scope is thin and ships with the claim: the discriminator is the
%% fortified symbol and NOT the compiler (CLAIMS.md 1.13, which also forbids
%% saying harness/build.py enables _FORTIFY_SOURCE -- it passes no such flag).
%%
%% Sources: FACTS.md H1-H5.
\section{The two checks we got wrong, and no number caught them}
\label{sec:wrong}

%% ⚠⚠ THE PROOF-OBLIGATION COUNT IS CUT, and this fixes a readability failure
%% and a CLAIMS violation with one edit.
%%  - The reader: "No idea.  Is that one per function?  Per line?  I can't tell
%%    if it's a big number or a small one, which makes the whole sentence do
%%    nothing for me."  They are right not to know.
%%  - CLAIMS.md §3.7: Verus's `N verified` counts ITEMS — functions, loop bodies,
%%    sub-proofs — NOT verification conditions, and a paper must say so ONCE
%%    before leaning on such a number.  This sentence leaned on it and never
%%    said so.  ver_D bans verifier counts everywhere else for the same reason;
%%    this was the last one standing.
%%  - CLAIMS.md §1.16 also required the words "shipped versions" on it, because
%%    the site once published 357/110/235 while the research published
%%    350/108/230.  Cutting the figure retires that hazard too.
%% WHAT SURVIVES is the half the reader could actually use: a pass count in
%% programs and a run count, both in units the post has already taught.
Start with what held. \num{totals.patterns_passing} of \num{totals.patterns} programs pass the gate, every proof in the shipped versions goes through with no errors, and \num{totals.adversarial_runs} hostile runs stand behind everything above. Now two traps in the apparatus that produced all of it, both ours.

%% ⚠ Tightened ~20 words.  "the field went in under one name, the generator
%% looked up another, and the new name appeared nowhere in it" restated "reading
%% a different key" three ways.  The load-bearing facts are unchanged and all
%% present: it could not have fired WHATEVER the change had been, and the tense
%% is still past with the correction attached (ver_B shipped this in the present
%% and it had already gone false).
We added a field to twenty-two of the gate's records, regenerated every table, and the output came back byte-identical. That was quoted at the time as evidence that nothing had moved. It came back byte-identical because the generator was reading a different key — the new name appeared nowhere in it — so the control couldn't have fired whatever the change had been. It reads the field today; it didn't then.

> Before you believe a check, ask what would make it fail — then make that happen. A residual of exactly zero is not a strong pass. It is the signature of a test that could not fail.

%% ⚠ FACT-CHECK 13: `\num{totals.patterns}` IS WRONG IN A SENTENCE ABOUT A PAST
%% EVENT.  If the corpus reaches 27 this silently becomes a false statement about
%% history.  results/SYNTHESIS.md:1250 freezes it as prose for exactly this
%% reason -- "The first version of this file compressed twenty-six patterns into
%% four results" -- and this file already freezes "twenty-two" for the gate
%% records two paragraphs up.  A live value is for a live count; this is neither.
The second trap is harder, because the document it happened to was correct. When this project compressed twenty-six programs into four headline results, its own later review found the omissions ran systematically one way: five reviewed, quotable results had gone missing, and every one of them flattered safe Rust.

> Coverage bias has no arithmetic signature. Every figure in the biased version reproduced correctly on the pass that found the bias, so checking a document's numbers cannot detect it. The only check is a different question, asked of a finished document by someone who did not write it: which way do its gaps point?

An earlier draft of this post failed that check. Its table of what each tool catches printed this as the result:

> No cell reads "silent, and it should have seen this", and that is the result.

It was true only after six of that table's twelve rows had been dropped, five of them rows where a detector had looked straight at a bug it was built for and not seen it. Drop every row where a detector looked and did not see, and no row is left where one did. That's a circle and not a result.

%% ⚠⚠ THE FIRST COLD READ STOPPED HERE, and this is the repair.  The reader
%% scored the post 8/10 and named exactly one paragraph they gave up on — the
%% old second paragraph below, which ran four clauses deep on three unglossed
%% terms (`fortified symbol`, `interceptor`, `fortification`): "I stopped
%% parsing partway through and skipped to the next paragraph.  If this paragraph
%% had been in section 2, I'd have closed the tab."
%% NOTHING FACTUAL IS DROPPED.  CLAIMS.md §1.13 makes two things mandatory and
%% both survive, each now in its own short sentence: (a) the discriminator is the
%% `_chk` SYMBOL and NOT the compiler — clang with fortification forced on goes
%% blind the same way; (b) the clang half is LOGGED, NOT REPRODUCED.  §1.13 also
%% forbids saying `harness/build.py` enables `_FORTIFY_SOURCE`; it passes no such
%% flag, and the prose says "switched on by default", which is what happens.
%% ⚠ `interceptor` is glossed in place rather than cut: it is what makes the
%% sentence explain a mechanism instead of asserting an outcome.
%% ⚠⚠ THE `memcpy` FORTIFICATION PARAGRAPH IS CUT ENTIRELY, ~150 prose words,
%% and this is a RULING, not a trim.  It is the most striking single fact in the
%% dropped rows and it goes anyway, for three reasons that agree:
%%
%%  1. THE FIRST COLD READER STOPPED HERE.  It was the one paragraph in the post
%%     they named giving up on: "I stopped parsing partway through and skipped to
%%     the next paragraph.  If this paragraph had been in section 2, I'd have
%%     closed the tab."  I rewrote it and it got clearer, but see 2.
%%  2. IT IS THIS SECTION'S THIRD CONFESSION, and the same reader said the
%%     honesty stops reading as honesty and starts reading as technique "roughly
%%     at the second blockquote" — which is one paragraph ABOVE this one.  A
%%     third instance is past the point of diminishing return by their own
%%     account, in the section they scored lowest (6, "written for other
%%     researchers").
%%  3. ver_D does not have to be complete, because ver_C is.  ver_C's
%%     `40-allocation.md` carries this in full, with the twelve-row table it
%%     belongs to, and the site has the pattern page.
%%
%% WHAT WENT, so it can be restored verbatim in substance: a genuinely
%% overlapping `memcpy` draws no sanitizer report — not for want of a check, but
%% because `_FORTIFY_SOURCE`, on by default at these levels, rewrites the call to
%% `__memcpy_chk`, which never reaches the sanitizer's `memcpy` interceptor.
%% Flip it off and the same program reports `memcpy-param-overlap` at exit 1.
%% THE BLIND SPOT WAS MADE BY A SECOND SAFETY MECHANISM.
%% ⚠ IF IT IS EVER RESTORED, BOTH SCOPE CLAUSES COME BACK WITH IT (CLAIMS.md
%% §1.13): the discriminator is the `_chk` SYMBOL and NOT the compiler — clang
%% with fortification forced on goes blind the same way — and the clang half is
%% LOGGED, NOT REPRODUCED.  And never say `harness/build.py` enables
%% `_FORTIFY_SOURCE`; it passes no such flag, Ubuntu gcc's default does.
%% ⚠ 99-close.md's first imperative pointed at this paragraph ("the fortified
%% `memcpy` above is what that looks like in the wild") and has been repointed at
%% §1's evidence, which the reader already has.

%% ⚠ TRIMMED, and `pinning rule` is gone with it — the first cold reader listed
%% it among the terms they guessed at and were never confident about, and it is
%% the last unglossed piece of this project's own vocabulary in the post.  The
%% claim is unchanged: mechanism transfers, magnitude does not.
So read every figure here as a bound with one end held up by a rule of ours. And quote the mechanism, not the magnitude: why a check survives or gets optimised away will reproduce on code we never built, while the numbers themselves belong to this machine and this pair of versions.
