%% Lessons: implications for three named audiences, each rule pointing back at
%% the finding that earned it.  Nothing here is new evidence.
%% ⚠ CLAIMS.md 1.23: the delete-and-measure habit ships with its bound, HERE
%% and not again in Threats (a cold reader found it verbatim in both).
%% ⚠ The "for benchmark authors" paragraph is CUT: it was written for the
%% authors, and its one anecdote was opaque to anyone else.
\section{Lessons}
\label{sec:lessons}

**For anyone publishing a safety number.** Name the two programs. "Safe Rust costs X%" is not a quantity; it is a quantity of a pair, and the pair must say which safe Rust, whether anyone tuned it, and which compiler built the C (Findings 1 and 5). Search both sides: most times a side that had not been searched was searched properly here the number moved, and the side that goes unsearched is usually the unsafe one, because a cheaper safe version costs an edit while a cheaper unsafe one has to come back out through a proof (Finding 9). Name the input, since one program's percentage is wrong in sign at the other input. Ship the wall clock beside the instruction count, and the layout noise beside the wall clock (Finding 3).

**For anyone maintaining C.** Run your known-bad input against the build you ship and fail when nothing happens; a silent pass is a result, and it is the result this paper is about (Finding 6). Delete a check in a branch and run the tests, to find out today whether anything is watching (Finding 7), knowing the limit: nothing distinguishes a deleted check from two builds that happened to compile alike, so a difference of zero never means the check was free. Harden the C you are not rewriting; on these bugs it works, at a price of the same order as the Rust check (Finding 4).

**For anyone buying a proof.** Ask what the specification says, not how many items it verified (Finding 10). Ask which resource the obligations range over: a memory-safety specification is silent on every wrong answer that stays in bounds, on every leak, and on every property of the trace. Read the trusted items as the place where the proof stops and somebody's word starts, and refuse a pasted specification with an empty contract (Finding 11).
