%% Q0 -- the setup.  NOT an objection; it is the situation that produces all
%% eight of them, and it earns its place by being the reader's own room rather
%% than the corpus.  ver_A opened on the field and its owner's verdict was "I
%% cannot understand anything"; ver_B opened on the meeting and that move worked.
%%
%% ⚠⚠⚠ THIS FILE WAS CUT FROM ~900 WORDS TO ~330 AND MUST NOT GROW BACK.  A cold
%% read by the target reader -- a senior C developer, twenty years of systems
%% work -- scored the paper 7/10 and THIS SECTION 5, the lowest of the eight, for
%% one reason stated three ways:
%%   "eleven paragraphs and roughly 900 words spent defending against objections
%%    I have not made, before a single measurement."
%%   "This is a man telling a stranger, unprompted, in the first minute, that he
%%    is honest."
%%   "My first note in the margin was 'why is the fifth thing you tell me a
%%    confession?', not 'how refreshing.'"
%% They nearly stopped reading here and were rescued by the first real number,
%% which was 900 words in.
%%
%% ⚠ FOUR PARAGRAPHS WERE REMOVED AND THREE WERE RELOCATED, NOT DELETED.  Each
%% now sits where it bites instead of where it had to be defended:
%%   * the instruction-versus-wall-clock warning -> \ref{sec:checks}, attached to
%%     the +72% that is +0.27%, where it has a number to be about.
%%   * "the worst number in here is a bitset at three times" -> \ref{sec:limits}
%%     demonstrates it in full; announcing it here spent the punchline early.
%%   * "published safe-beats-unsafe three times and retracted it three times" ->
%%     \ref{sec:checks}'s tuning subsection, which is ABOUT spellings and is
%%     where that story is the origin of the "cheapest found" rule.
%%   * the gate's description -> it is glossed at first use in \ref{sec:unsafe}.
%% ⚠ THE ONE THING THAT STAYED IS "what it is not", because a DIFFERENT reader
%% -- the sceptic persona whose ladder this paper is built on -- named its
%% absence a stop condition: "a paper that lets me DISCOVER on page 9 that these
%% are 40-line kernels has already told me it will hide the other things too."
%% Both readers are satisfied by keeping that one and moving the rest.
%%
%% ⚠ NO CVE PERCENTAGE ANYWHERE NEAR THIS FILE.  Same sceptic, on the 70%
%% statistic as motivation: "It tells me the author thinks my objection is
%% IGNORANCE rather than COST."  It is a stop-reading trigger and is banned.
%%
%% ⚠ THE SIX VERSIONS ARE NAMED HERE, and that is a comprehension repair: the
%% cold reader reached the middle of section 3 still not knowing what the six
%% were -- "I read the whole of section 2 not knowing what was being compared.
%% That is a structural failure, not a vocabulary one."
%%
%% ⚠⚠ THE BUILD MULTIPLIER IS SPELLED OUT BECAUSE THE TOTAL DID NOT RECONCILE.
%% The sentence used to read "Two C compilers, two optimisation levels, N builds
%% in all", and a reader who tried it got 27 x 6 x 2 = 324, or 432 doubling the C
%% rows: "860 is roughly twice that and I have no idea what's in the gap."  The
%% gap is INLINE MODE -- every cell is (version, opt, mode) and `mode` runs
%% `isolated` and `whole`, which is the ONE factor the prose never named.  Eight
%% build targets x 2 opt x 2 modes = 32 per program, and the totals are 32 x n
%% less a few (p01 ships 28).  "for most of these programs" is what makes the sum
%% come out UNDER rather than over, which is the honest direction.
%% ⚠ Verify with: sum of `cells_built` over data/patterns/*.json.
%%
%% ⚠⚠ THE TWO INPUTS ARE INTRODUCED HERE, IN THE PARAGRAPH THAT FIXES THE UNIT.
%% \ref{sec:slower} used to say "on both inputs" four paragraphs before anything
%% had said there were two, and the reader stopped and went looking for a
%% definition they thought they had missed.  All 27 patterns measure on exactly
%% `small.bin` and `large.bin`, so the sentence is corpus-true, not a sample.
%%
%% ⚠⚠ VOCABULARY, AND IT IS A STANDING RULE FOR EVERY FILE IN THIS VERSION.  The
%% owner's verdict on the previous pass was "the questions make sense, the
%% answers make no sense -- you think the audience will read our code?"  The
%% answers were written about the APPARATUS.  So: no `rung`, `spelling`, `cell`,
%% `band`, `corpus`, `kernel`, `the gate`, `licensed for differencing`, `in
%% contract`, `identity pin`, `the model`, `pattern` as a noun.  Say version,
%% way of writing it, build, input, these programs, the measured function, our
%% own checking script, the ones we could compare fairly, the same fixed
%% specification, a rule we imposed, the reference implementation, program.
%% Every fact stays; only the frame moves from our bench to the reader's desk.
\section{Somebody wants to rewrite your C in Rust}
\label{sec:setup}

There is a C parser in production, somebody has proposed rewriting it in Rust, and the argument in the room is about a percentage — theirs off a blog post, yours off a benchmark somebody ran once. You have objections, they are good ones, and they come in an order, because each is what you say after hearing a decent answer to the one before. This is that conversation, in that order.

Behind every answer: \num{totals.passing.patterns} small C programs, each carrying one real bug, each written six ways — the C with the bug in it, the same C with the check put back, safe Rust ported line for line, safe Rust tuned by hand, unsafe Rust, and unsafe Rust carrying a machine-checked proof. Every version is run against a separate reference implementation that decides what the right answer is, then attacked with inputs built to break that program the particular way it can be broken.

The unit throughout is instructions executed on one call, counted rather than timed. Where a program has a stopwatch figure too you get both, because on two of them they disagree.

%% ⚠⚠ THREE LIMITS, ONE SENTENCE EACH, AND THAT IS THE WHOLE BUDGET.  Every one
%% of these is mandated -- scale, concurrency, the inline mode -- and every one
%% used to have a paragraph.  A cold reader's verdict on the version that
%% explained them: "your bookkeeping, not my problem."  State the limit, not the
%% apparatus that produced it.
And three things it cannot tell you, now rather than on page nine. Nothing here is a whole system or a mixed C-and-Rust binary, so this prices a rewritten loop and not a rewritten daemon. Nothing here ever starts a thread, so if the guarantee you are buying is the one about data races, this has nothing in it for you. And your build inlines these functions, while ours deliberately did not — \ref{sec:future} says what that costs.
