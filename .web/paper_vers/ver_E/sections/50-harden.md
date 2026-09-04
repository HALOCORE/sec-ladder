%% Q5.  PLACEMENT IS THE ARGUMENT.  This objection is only sharp AFTER the reader
%% has the whole Rust story, because now they can ask what all of it bought over
%% three lines of C -- and the honest answer is a tie on outcomes, which reads as
%% a concession here and would read as a retreat anywhere earlier.
%%
%% ⚠⚠ CLAIMS.md §2.4: these programs CANNOT distinguish hardened C from Rust on
%% outcomes.  That must be stated plainly, in our own voice, before the argument
%% that survives it.  Burying it is the cheapest attack on the whole report.
%% ⚠ CLAIMS.md §3.1: "plain, unchecked C", never "idiomatic C".
%%
%% ⚠⚠ EVERY NODE HERE RUNS THE THREE MOVES: the answer, then the smallest
%% evidence carrying THAT answer, then where that answer breaks as its own final
%% beat.  The five sub-objections are each a distinct reader move and the ladder
%% is right; what was wrong was INSIDE them.  Q5.1 was four topics fused into one
%% stream -- plain C crashing, the price of hardening, the ordering against Rust,
%% and the calibration pair -- and is now one answer with the spread as its
%% limit.  Q5.4's opener was a concession where the ANSWER belongs; the answer is
%% "they all need an input that reaches the bug", and the untouched half of the
%% toolbox is its move 3.
%% ⚠⚠ THE PAPER MAY NOT REFER TO EARLIER VERSIONS OF ITSELF.  The clause "and
%% this project has already had to withdraw it" is gone from the calibration-pair
%% scope for that reason -- it was ambiguous between the research project's own
%% published claims and this document's drafts, and only one of those is allowed.
%% The scope survives in the stronger form: two programs, and not a law.
%%
%% ⚠ LEVEL-1 EDIT, MANDATED BY THE FACT-CHECK: "those three lines" is gone.  The
%% hardened file's header says three lines, but that is a DIFF count -- two are
%% executable and one is a comment change -- so the sentence now names the check
%% rather than a line count nobody can reproduce.
%%
%% ⚠⚠⚠ THIS IS THE SECTION THE OWNER QUOTED WHEN THEY SAID THE ANSWERS WERE
%% WRITTEN FROM INSIDE THE PROJECT.  The old move 1 opened "on outcomes, this
%% corpus cannot tell the two apart" -- a sentence whose subject is our apparatus,
%% answering a question about the reader's code.  The concession is UNCHANGED and
%% is now stated about THEIR C, in their words, and every number in it is sized
%% where it lands: +24 instructions is "you will not find it in a profile", and
%% zero checks firing is "we have never watched the safety net catch anybody".
%% ⚠ DO NOT RE-ABSTRACT IT.  The concession is the reason the rest is believed.
\section{“Then why not just harden the C I already have?”}
\label{sec:harden}

Honestly? For these bugs, hardening your C works, and we are not going to pretend otherwise.

Write the missing check into the C and it gives the right answer on every hostile input we threw at it — every one. Across the programs here that ship a hardened version the middle one costs 24 instructions a call: on any function that does real work you will not find that in a profile. Meanwhile, across \num{totals.passing.adversarial_runs} hostile runs, not one Rust bounds check fires anywhere in the versions we ship. We have never once watched a check save anything.

So it is not a performance argument, and it is not an outcomes argument either: on what these programs do under attack, we cannot tell hardened C and Rust apart. The difference is that in C the check is optional, and nothing tells you when it is missing. The plain, unchecked C here ships with a comment sitting where the check should be — nobody deleted it; it was never written — and our own checking script reads the source, writes down that the C does not have it, and passes the build anyway. Nothing in this project fails because a check is absent from the C.

On the Rust side that is not true, for the reason the last section gave: the proved version does not build without it.

%% ------------------------------------------------------------- LEVEL 2 ----
%% Q5.1.  Provoked by the concession itself.  "It cannot tell the two apart"
%% invites exactly one reply, and it is the reader's strongest move.
%%
%% ⚠⚠ FACT-CHECK, THE BIG ONE.  "0 of 4,104 hostile runs end loud" IS FALSE and
%% must never be written: 109 run instances end in a signal (SIGSEGV 92, SIGABRT
%% 17) and 8 hang, ALL of them on the plain unchecked C, all where the model says
%% exit 0.  The licensed form -- CLAIMS.md §2.2, and it is what level 1 already
%% says -- is that zero runs end with a version REFUSING TO CONTINUE.  A plain-C
%% SIGSEGV is a crash, not a check firing.  Dropping the crashes would throw away
%% a CORRECT thesis for a false sentence, and it gains us the sharper claim: the
%% programs DO separate plain C from everything else on outcomes.  What they
%% cannot separate is HARDENED C from Rust.
%%
%% ⚠ FACT-CHECK: the plain-C-versus-Rust comparison reverses on the rung the
%% project's own rule says to use (`.memory/01-ladder.md`): "with only the plain
%% rung, 'C is faster' and 'C is unsafe' are the same sentence."  Hardened clang C
%% is +7 / +17 DEARER than unsafe Rust on the record walker, because clang
%% hardening costs +24 / +54 -- more than the plain-C gap.  Publish the hardened
%% row or do not publish the plain one.
%% ⚠⚠ THAT PAIR IS DISCHARGED IN \ref{sec:checks} AND IS NOT REPEATED HERE.  The
%% rule binds where the PLAIN row is published, which is that section, and its
%% table now carries both rows.  What is left here is the one comparison that
%% table states nowhere: hardened C against TUNED SAFE RUST, +20 / +60.  Do not
%% re-derive +7 / +17 in this file.
%% ⚠ The gloss of `hardened` went with it -- \ref{sec:checks} now glosses it at
%% first use, in level 1, so a breadth-first read still gets it exactly once.
%%
%% ⚠ CLAIMS.md §1.5: "hardened C costs +5/+12, flat" is TRUE OF ONE PATTERN and
%% is on the retracted list.  The calibration-pair sentence is scoped to those
%% two programs IN THE SENTENCE AFTER IT, never in the same one.
%%
%% ⚠⚠ THE 109 AND THE 8 ARE NOW \num{} AND THE `%%literal-ok 109` IS GONE.  They
%% were literals with a literal-ok beside them, which is the same shape as the
%% stale 126 two subsections down: a literal-ok SUPPRESSES the one warning that
%% would catch the figure moving, so it is only ever right for a number that is
%% meant to be frozen, and a count of crashing runs is not.  `totals.crash` and
%% `totals.hung` are live paths and are used instead.
%% ⚠ SCOPE, AND IT IS THE ONE THING TO WATCH: those two paths are UNSCOPED --
%% every program in the tree, not just the passing ones -- while the run total in
%% the sentence above is `totals.passing.adversarial_runs`.  Today they coincide,
%% because the one program outside the passing set contributes no crash and no
%% hang.  If a failing program ever contributes one, this sentence needs a
%% passing-scoped path adding to build_data.py; do not fix it by retyping a
%% number.
%%
%% ⚠ THE CLANG HARDENING RANGE IS CUT and its `%%literal-ok 108` with it.  The
%% paragraph carried four range endpoints across two compilers, and a cold
%% reader's verdict on this document was that "no number survives its own
%% paragraph" -- eighty qualified numbers retain worse than thirty unqualified
%% ones.  One scoped range plus "negative on three" plus the outlier's mechanism
%% is the whole argument; the second compiler's endpoints only showed that the
%% set is large.  CLAIMS.md §1.5's corrected form gives both; giving gcc's and
%% SAYING it is gcc's is inside that rule.
\subsection{“So the C I already have is fine.”}

Not the one you have. The hardened one, yes.

Of those same hostile runs, \num{totals.passing.crash} killed the program outright and \num{totals.passing.hung} hung — every one on the plain, unchecked C, and every one on an input where the right answer was to finish quietly and exit 0. So these programs do separate plain C from everything else, loudly. What they cannot separate is hardened C from Rust.

And hardening is cheap. On the record walker the same check is +24 and +54 under clang, which lands hardened C between the two Rust versions — unsafe Rust very slightly in front of it, tuned safe Rust 20 and 60 instructions a call behind. On the two simplest programs the price of safety is flat however big the data gets and about the same size in both languages: single figures a call on the Rust side, single figures to a dozen on the C side. What differs is not the price. It is that in one of them it is optional.

That is two programs, not a law. The middle figure of 24 hides a range from 125 instructions a call cheaper to 10,242 dearer under gcc, and on three programs hardening comes out free or better. The dearest is not a check at all, but a whole extra validation pass over a 2,048-entry table.

%% Q5.2.  ⚠⚠⚠ HEADING AND FRAMING BOTH REWRITTEN AFTER A COLD READ, AND BOTH
%% CHANGES ARE LOAD-BEARING.
%% (1) THE OLD HEADING -- "Is there anything on your list I can't just write in
%% C?" -- is a question the target reader said they would never ask.  In a section
%% about hardening, their actual next move is whether hardening REACHES these two,
%% and it does not, because neither is a missing check.  That is also the true
%% claim: `p08`'s own `c/kernel.c`:9-14 says in terms "This rung is NOT missing a
%% bounds check... Nothing leaves an allocation."
%% (2) ⚠⚠ THE OLD OVERLAP FRAMING WAS BACKWARDS ON TWO POINTS AND THE READER GOT
%% BOTH.  It said the copy "has no version to price, because safe Rust will not
%% compile one" -- FALSE: `safe_tuned.rs`:53 ships `v.copy_within(0..m-dr, dr)`,
%% priced at +0.36% / +0.09% against R4 (`NOTES.md`:32-33), and p08 is in the flat
%% bucket.  And it presented the borrow checker's refusal as the finding, which a
%% C developer reads as a LIMITATION -- "that's what `memmove` is for", which is
%% exactly right and which the tree agrees with: `c/kernel_hardened.c`:1 is
%% `memcpy`->`memmove` and nothing else, and :16-18 records that on this glibc
%% `dlsym("memcpy")` and `dlsym("memmove")` RETURN ONE ADDRESS, so the fix costs
%% nothing.  ⚠ THE ARGUMENT THAT SURVIVES, AND IT IS STRONGER: the correct
%% spelling is free in both languages, and the difference is that C's requires
%% somebody to remember.  rustc's own diagnostic is the evidence (`NOTES.md`:630,
%% 634-636) -- it does not say "you cannot", it NAMES `copy_within`.
%% ⚠ And unsafe Rust DOES reopen the bug, via `copy_nonoverlapping`
%% (`unsafe.rs`:71-72), where Miri catches it (`NOTES.md`:653).  The shipped
%% unsafe rung uses `ptr::copy` and is correct.  Do not write "unsafe Rust
%% reintroduces it" unqualified, and do not write "safe Rust cannot express it".
\subsection{“Are there bugs on your list that adding a check doesn't fix?”}

Two, and neither one is a missing bounds check.

The first is a buffer shift written with `memcpy` where source and destination overlap. Nothing leaves the allocation and no test is missing — `memcpy` is simply undefined when its ranges overlap, and what you get is silent corruption inside a buffer the program owns. You are ahead of us and you are right: that is what `memmove` is for, the hardened C here is exactly that one token, and on this machine's C library the two resolve to the same address, so the correct spelling costs nothing measurable. Which is the trouble — the wrong one runs, returns a plausible answer, and nothing objects.

Safe Rust cannot write that transliteration, needing two names into one buffer with one of them writing. But read what the compiler says rather than that it refused, because it is not *you cannot do this*: it names `copy_within`, which is `memmove` semantics by definition and costs 0.4% and 0.1% more than the unsafe version. Both languages land on the same machine instruction; in only one did somebody have to remember. Unsafe Rust puts the bug straight back with one token, and Miri catches it when it does.

The second is a strict-aliasing miscompile, where the compiler is entitled to assume two pointers of different types never address the same memory and quietly optimises on that assumption. It is the first bug class here where the unsafe Rust does not reintroduce the bug either. Its price runs backwards: the punned version costs 6 instructions a call *more* than five separate ways of not writing it, one of which is just a compiler flag. It buys nothing and costs 6.

%% ⚠⚠ THE LAST SENTENCE IS A GAPS-REVIEW REPAIR AND IT MAY NOT BE DROPPED.
%% p38-alias-pun/NOTES.md:958-975 prints all seven neighbours, and its own bolded
%% summary states BOTH halves: six defined spellings are cheaper than the
%% undefined one, AND "the only defined spelling that costs more is the two-half
%% read the Rust rungs are FORCED INTO" -- `c_halves`, +12.00 gcc / +32.00 clang.
%% Publishing the -6.00 without it is precisely the omission shape this paper's
%% own review exists to catch: our figure printed, the neighbouring one against
%% us left out, from one table we had already opened.  ✅ Verified at source.
One entry in that comparison counts against us, though. The safe versions cannot express the single read at all; they are forced into a two-half read, and of every well-defined way of writing it we measured, that is the only one dearer than the undefined one — by 12 instructions a call under gcc and 32 under clang. So this is a bug class C can avoid for free, and Rust avoids by construction at a price.

%% Q5.3.  Provoked by level 1's last line: "the proved version does not build
%% without it."  The reader's move is to ask whether that generalises, and the
%% answer is that it is PARTIAL.
%%
%% ⚠⚠ CLAIMS.md §1.6, MANDATORY AND MAY NOT BE SMOOTHED.  Eight patterns carry
%% the deleted-check control.  Four turn silent corruption into a stop; two
%% depend on the input; TWO DO NOTHING, and the two failures are different from
%% each other -- one stripped safe rung is BIT-IDENTICAL to C at both measured
%% optimisation levels, and another HANGS.
%% ⚠ CLAIMS.md §1.15: NEVER "nothing catches an infinite loop."  A `decreases`
%% clause catches it at compile time and a plain `timeout` at run time.  The
%% honest form is that nothing on this ladder EMITS the capacity check -- the
%% versions that terminate write it by hand -- and that form is written below.
%% ⚠ CLAIMS.md §1.21: the Rust rows are deletions re-run from a committed script
%% and gate-certified by nothing; the C rows are the shipped program and are
%% gate-certified.  BOTH clauses are mandatory wherever this control is used.
%%
%% ⚠⚠⚠ THE 126 WAS STALE AND IS NOW LIVE.  This paragraph printed "126
%% required-but-absent spellings" as a literal with a `%%literal-ok 126` beside
%% it, which SUPPRESSED the very warning that would have caught it: the field is
%% `totals.idiom.required_absent` and it reads 175 today.  A `literal-ok` line is
%% a promise that a number is meant to be FROZEN, and this one never was.  It is
%% a \num{} now.  ⚠ Before declaring any future literal ok, check whether the
%% number is a corpus total that will move -- if it is, expose the path instead.
\subsection{“So the whole argument is that Rust makes you write it. Does it?”}

On four of the eight programs that carry the experiment, yes. Here is each side of the fence.

First the C side. The only thing that fails a run is a line we have explicitly *forbidden*; a required line that is missing fails nothing, and across these programs the audit has written down \num{totals.idiom.required_absent} of those, several per program, none of which stops anything.

Then the Rust side. Delete the check out of the safe version and on four of the eight it turns a silently wrong answer into a stop. On two more it depends on the input: inside the in-bounds regime the stripped version prints C's answer, bit for bit, and exits 0.

On the last two, nothing at all, and they fail differently. One stripped safe version compiles to the same bytes as the C at both optimisation levels, so there was no check in the machine code to delete. The other is a hash probe, and it hangs: the sanitizer and Miri are both silent on it, though the proof does catch that one — a verified loop has to arrive with an argument that it ends — and a plain `timeout` catches it at run time. What nothing here does is *emit* the capacity check. The versions that terminate write it by hand.

The two halves do not weigh the same, either. The C half is the programs we ship, and they pass the checking script. The Rust half is deletions re-run from a script we commit, and nothing certifies them.

%% Q5.4.  ADDED AFTER A COLD READ, AND IT REPAIRS A STRAWMAN.  The sentence that
%% provoked it -- level 1's "the only thing that knows the check is missing is a
%% person reading the file", now deleted -- drew the reader's sharpest response:
%% "No it is not.  Coverity, CodeQL, `-Wall -Wextra` with the right analysers, a
%% fuzzer in CI.  Static analysis and fuzzing are not mentioned once in 8,300
%% words.  And the document's own evidence refutes the claim: 109 end in a signal
%% and eight hang, every one on the plain, unchecked C.  That is a fuzzer finding
%% the missing check, 117 times, in their own harness."  They are right, and the
%% honest version is stronger than the strawman was.
%%
%% ⚠ TWO SCOPES, BOTH CHECKED THIS SESSION.  (1) `harness/build.py:128` passes
%% `-Wall -Wextra` on every C build, so "no static analysis was run" is FALSE and
%% the claim is scoped past the compiler's own warnings.  (2) Nothing under
%% `harness/` or any `spec.md` mentions coverity, codeql, clang-tidy, cppcheck or
%% scan-build, so the honest statement is an ABSENCE OF EVIDENCE, not a result.
%% ⚠ Our adversarial inputs are hand-built per pattern (`inputs/gen.py`), NOT a
%% fuzzer.  The concession is stronger for saying so, and "that is a fuzzer" would
%% have been the fourth wrong claim of this kind in the paper's history.
%% ⚠ The bitset is a CALLBACK here and may not be re-demonstrated: one sentence,
%% no table, no second telling.  A cold reader of an earlier framing counted eight
%% demonstrations of one finding and said "I would have closed the tab."
\subsection{“That’s your checking script. I have static analysis and a fuzzer.”}

You do, and they work. They also all need an input that reaches the bug.

Point a sanitizer at the plain C record walker and it fires on the first input that reaches it, and the crashes and hangs above are what a fuzzing harness exists to produce — ours came out of hostile inputs written by hand rather than a fuzzer, but they came out. Then take the bitset typo: no input takes that index outside its allocation, so there is nothing for the sanitizer to see, nothing for Miri to report, and no crash for a fuzzer to find. A tool that watches for a boundary being crossed is blind to a bug that never goes near one.

And half your toolbox we never touched. Every C build here goes through `-Wall -Wextra`; beyond that nothing runs a static analyser, so on Coverity and CodeQL this report is evidence in neither direction.

\subsection{“So instead of a wrong answer I get an outage.”}

Sometimes, yes. That is a trade rather than a win, and it is one we did not measure.

A bounds check turns a memory-safety bug into a reliable abort, which in a network daemon is a remote denial of service and in firmware is a device that does not come back. Plenty of people should still take that trade; nobody should take it without noticing they made one. And not one check fired in all those hostile runs, so we have no more evidence about what it would cost you than about what it would save you.

There is one version where the objection does not land. Whatever the specification covers cannot abort at run time on the proved version: the prover has already shown the bad case does not arise, which is stronger than "a check will catch it". If it cannot show that, you do not get a binary. The failure moved from run time to build time.

That is the proved version only, and only as far as somebody wrote it down. Everything the specification does not say is still yours to get wrong at three in the morning.
