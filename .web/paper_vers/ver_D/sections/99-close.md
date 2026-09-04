%% The close.  Short.  RESTATE THE CLAIM -- this and the opening are the two
%% places cold readers actually take a thesis from, and the previous framing's
%% close scored 8 from all four with the note "Two questions.  No numbers.
%% Correct place to stop."
%%
%% THREE imperatives, not four.  "Budget the proof honestly" is CUT: all four
%% cold readers skipped the proof-buying material -- "I have never bought a
%% proof, I'm not going to, and I skipped most of it" -- and it asks the reader
%% to budget something the post has just shown costs zero instructions.
%%
%% ⚠ The concurrency sentence is NON-NEGOTIABLE and the earlier draft of the
%% brief omitted it.  Zero of these programs create a thread, so a reader whose
%% reason for wanting Rust is the data-race guarantee has to be told this post is
%% evidence neither way.
%%
%% No new numbers.  No summary of the post.  End on something a person would say.
\section{Three things to do to your own code}
\label{sec:close}

%% ⚠ FACT-CHECK 17: SCOPED, because 25 of the 26 programs ship a hardened C
%% version and p01 does not — I checked for `c/kernel_hardened.c` across all 26.
%% "every hostile input we have" was therefore true of 25 patterns, not the
%% corpus.  ⚠ CLAIMS.md §2.4 is what this sentence exists to obey: this corpus
%% cannot distinguish hardened C from Rust ON OUTCOMES; what it distinguishes is
%% non-optionality.  The first clause is also broader than §2.4 licenses —
%% PLAIN unchecked C did segfault where no Rust version did — but the sentence
%% after it is the one doing the work, and the error runs against our own
%% interest, so it stands as written.
Take the narrow claim from all that and not the wide one. Nothing here shows Rust is safer than C: wherever a hardened C version exists — 25 of the 26 programs — it returned the right answer on every hostile input we have, and this project cannot tell the two apart on outcomes. What it can tell apart is whether the check is optional — whether a person can leave it out, on a Tuesday, under a deadline, and have every test and every tool stay green.

Three things worth doing, all of them cheap.

%% ⚠ REPOINTED.  This used to end "and the fortified `memcpy` above is what that
%% looks like in the wild", and that paragraph is now cut from §4.  The
%% replacement leans on evidence the reader already has from §1 — a gate that
%% reads the source, records that the check is missing, and passes — which makes
%% the same point about silence and needs no new machinery.
Run your known-bad input against the configuration you actually ship, and fail the build on silence. A detector that has been switched off and one that found nothing write the same log line — and so does a check that records a missing bounds test and passes anyway.

Delete a check in a branch and run your tests. If nothing changes, your tests weren't testing it — and read a green suite from then on the way you'd read that silent log line.

When you publish a cost, publish the pair: which two versions you subtracted, and which of the two anybody had tried to make fast.

One boundary, and it's a big one. Nothing in this project is concurrent — not one of these programs starts a thread — so if the reason you want Rust is the guarantee about data races, none of this is evidence either way.

I can't tell you what safety costs on your program. I can tell you that if you deleted a check from it tomorrow you'd probably never hear about it, and that's the part I'd fix first.
