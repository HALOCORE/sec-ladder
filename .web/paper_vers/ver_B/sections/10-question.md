%% ver_B section 1.  It opens on the READER'S meeting, not on the corpus, and
%% that is the whole reason this version exists: ver_A opened on the field and
%% its owner's verdict was "I cannot understand anything".  The first sentence
%% is ver_A's best one, lifted from 15-whattodo.md, where it was wasted at the
%% back of the paper.
%%
%% ⚠ THE FIVE LEVELS OF SAFETY ARE NOT DEFINED HERE.  They arrive in section 2,
%% after the measurement that makes five of them necessary -- defining a ladder
%% before the reader has seen why two rows will not do is exactly the move this
%% rewrite exists to stop.  This file names the number five and nothing more.
%%
%% Method is ~130 words and is not a section (outline part 2).  It is here to
%% answer "where do the numbers come from", not to be complete: the apparatus
%% lives in the repository, and section 5 carries the limits.
%%
%% The closing paragraph ("the part that transfers is the mechanism, not the
%% magnitude") was CUT at the final trim: the paper said it four times and the
%% one that survives is \ref{sec:lied}'s closing pair, where it is the reader's
%% instruction for every figure above it.  Do not restore it here.
%%
%% The two scope sentences are MANDATORY and are not optional trims
%% (.temp/verify/RULINGS.md R9): a reader who takes "+626 instructions per call"
%% for a latency claim, or who thinks data races were covered, misreads
%% everything after this page.  Each states the scope here and forward-refs the
%% section that argues it, which is the paper's own "every number ships with its
%% scope" rule applied at document scale.

\section{The argument in the room}
\label{sec:question}

Suppose the decision is already yours. There is a C parser in production,
somebody has proposed rewriting it in Rust, and the argument in the room is
about a percentage — theirs off a blog post, yours off a benchmark somebody ran
once. Nothing here settles that argument, because the percentage is not a
constant. What the measurements supply instead is an order in which to ask three
questions.

**What will it cost me?** That is section \ref{sec:cost}. **Will the tools I
already run tell me if I am wrong?** — the sanitizers in CI, the fuzzer, the
dashboard that has been green all quarter: section \ref{sec:tools}. **And if it
comes out memory-safe, or even carries a machine-checked proof, am I done?**
Section \ref{sec:notdone}.

The evidence is \num{totals.patterns} patterns lifted out of ordinary C — a
buffer copy, a bounded stack, a binary search, an HTTP range parser, a
length-prefixed record walker — each rebuilt five times at increasing levels of
safety over two C compilers, two optimisation levels and two inlining modes:
\num{totals.cells} measured builds, every one driven against a Python reference
implementation sharing no code with any kernel, then attacked
\num{totals.adversarial_runs} times on inputs built to break that pattern in the
particular way it can be broken.

Two things to fix before the numbers start. **The unit is executed instructions
per call, not seconds** — and the two can disagree in *direction*, which section
\ref{sec:cantsay} measures. Every figure below is an instruction count at `-O3`,
from a build mode that suppresses inlining so a kernel's work is attributable at
all; this project tried to publish wall-clock figures and withdrew two rows of
them, and section \ref{sec:lied} says what went wrong.

**And nothing here is concurrent.** Zero of \num{totals.patterns} patterns
creates a thread, so if the guarantee you are buying is the one about data
races, this paper is evidence neither for it nor against it; section
\ref{sec:cantsay} draws the rest of that boundary.
