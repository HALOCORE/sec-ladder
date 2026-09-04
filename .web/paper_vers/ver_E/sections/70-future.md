%% Q7.  The last objection, and the reader only reaches it if the previous six
%% landed: they are now asking what they are committing to.
%%
%% ⚠ THE TITLE WAS "And what about all this expires?" AND IT BROKE THE CONCEIT
%% AT THE LAST POSSIBLE MOMENT.  The cold reader, who is the C developer whose
%% voice every heading is written in: "no C developer says that.  It is a
%% researcher's anxiety about their own tooling, wearing my voice, and it is the
%% note the piece ends on."
%%
%% ⚠⚠ RESTRUCTURED TO THE THREE-MOVE TEMPLATE (.temp/verE/CRISP.md).  This
%% section used to fuse FIVE things into one flat run: what expires, what does
%% not, the two absences, the transfer rule, and the Monday list.  Now:
%%   move 1  the answer -- two lists, and they differ in kind
%%   move 2  the evidence -- one paragraph each
%%   move 3  where the answer breaks -- the absences, which is where it breaks
%%           hardest, because a limit you can name is not the same as a limit you
%%           never measured
%%   then    one sub-objection, which is the reader's actual next question
%% ⚠ Do NOT generalise the Verus limits into a claim about provers.  They are
%% this verifier, this version, this year.
\section{“So what am I actually signing up for?”}
\label{sec:future}

Two bills, and they are different in kind. One is this year's tools and it will be a different bill in two years. The other is the shape of the thing and it does not go away.

%% ⚠⚠ FACT-CHECK REPAIR, AND THE RETRACTED FORM MUST NOT COME BACK.  This read
%% "cannot express C strings at all" and "cannot dereference a raw pointer".
%% BOTH ARE RETRACTED IN-TREE: p11/NOTES.md:1036-1042 records that all four
%% unsupported items take an `external_type_specification`/`assume_specification`
%% declaration and the escape then verifies FIRST TRY; and two shipped verified
%% rungs (p27, p42) reach raw-pointer memory through `vstd::raw_ptr`.
%% ⚠ A PRICE, NEVER AN IMPOSSIBILITY -- and it is the better sentence, because a
%% price is a thing the reader can decide about.
%% ⚠ Three tracked files upstream still print the retracted version, including
%% the published synthesis.  Do not restore it from there.
The tools first, because that is the bill people quote at you. The prover refuses C strings four different ways and will not dereference a raw pointer directly — but each is a price rather than a wall. Teach it the C-string case with four hand-written facts it then takes on trust and it verifies first try. And two of the proved versions here already reach raw-pointer memory the long way round: you may not write `*p` at all, but call the prover's own accessor and hand it, alongside the pointer, a proof-only token saying this address is yours — got when the memory was allocated, given up when it is freed. That bill is why the unsafe baseline in this report is slower than it needed to be. It is also one young verifier at one version, and the limits you hit will not be these.

What does not expire is underneath all of that. A proof rests on a base of hand-written facts the prover takes on trust and never checks. Somebody has to write the specification, it is a separate artefact from the code, and it can be wrong. No amount of tool maturity touches either.

%% ⚠⚠ MOVE 3, AND IT IS WHERE THIS ANSWER BREAKS HARDEST.  Both absences were
%% named by the target reader as things they would ask for; the second was their
%% NUMBER ONE actual blocker, above performance and above proof cost -- "A stated
%% limitation is worth more to me than a confident extrapolation, because it
%% tells me the rest of the numbers weren't extrapolated either."
%% ⚠⚠ THE THREAD PARAGRAPH IS A CALLBACK AND MUST STAY ONE.  \ref{sec:setup}'s
%% "here is what it is not" list now names the absence, because a cold read
%% caught its omission there as a broken promise -- that list advertises itself
%% as the page-nine-surprise list.  So this paragraph OPENS by referring back and
%% carries only the CONSEQUENCE.  Delete the callback and the paper states the
%% same absence twice as news, which is the complaint that moved it out here in
%% the first place.
So much for what we can price. The answer breaks on two things we never measured, and an unmeasured thing is worse than an expensive one because you cannot plan against it.

We told you at the start that nothing here ever starts a thread. Here is what that costs you: if the guarantee you are buying is the one about data races — and for most people proposing a rewrite it is — this report is evidence neither for it nor against it, and reading it more carefully will not change that.

And every program here is a single function: no mixed binary, no foreign-function boundary, no partial migration of anything into anything. So this tells you what a rewritten loop costs and not what a rewritten daemon costs, and the gap between those two is where your actual decision lives. We did not measure it and we will not extrapolate to it.

%% Q7.1.  The reader's real last question, and it is not about the future -- it
%% is about tomorrow.  Provoked directly by move 3: having been told what we
%% cannot tell them, they ask what is left that they can use.
%%
%% ⚠ CLAIMS.md §3.5: every limitation ships its DIRECTION.  A bare "these are
%% micro-kernels" reads as excuse-making; the direction is what makes it usable.
%% ⚠⚠ THE INLINING QUALIFICATION IS NOT A HEDGE.  Every figure here is inline
%% mode `isolated`; in `whole` mode results/SYNTHESIS.md:1237-1238 records 394 of
%% 414 `-O3` cell/input pairs with NO KERNEL SYMBOL AT ALL, and
%% p16/NOTES.md:441-448 measures the ported rung costing +10% MORE once inlined.
%% Without it "quote a constant" is advice that does not survive the reader's own
%% build.  ⚠ IN THE READER'S WORDS IT IS "the function mostly stops existing as a
%% symbol at all" -- the fact, not the mode name.
%% ⚠ CLAIMS.md §1.23: the delete-and-re-measure method ships with its bound.
%% ⚠ NO "budget the proof honestly" -- all four cold readers of earlier work
%% skipped the proof-buying material, and an instruction they skip spends the
%% ending.
\subsection{“Then what can I actually use on Monday?”}

Three habits, and none of them requires believing anything above.

Run your known-bad input against the configuration you actually ship — not the debug build, the one that goes out — and fail the build when nothing happens. A silent pass is a result, and it is the one this whole report is about.

Delete a check in a branch and run your tests, so you find out today whether anything is watching. Know its limit, which is the same one our own checking script has: nothing in it distinguishes a check you deleted from two builds that happened to compile to the same bytes.

And when somebody quotes you a number, ask which two versions they subtracted and which of the two anyone tried to make fast.

And if you take a figure from here rather than a habit, take a per-call constant and not a percentage: these programs do nothing but the loop, so every fraction in this report can only shrink against a function that does real work. Take the build with it, too. Every number here comes from a build that keeps the measured function out of line so it has a symbol to attribute work to; compile the same programs the way you ship and the function mostly stops existing as a symbol — and the line-for-line port gets about ten percent *worse* once inlined, the one case where the compiler can finally see the caller's bound and it still does not help.
