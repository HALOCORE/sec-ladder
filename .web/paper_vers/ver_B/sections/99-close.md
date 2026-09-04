%% ver_B section 7.  The structural template is ver_A's 15-whattodo.md, which is
%% the one section of ver_A its hostile reader did not object to.  Two rules
%% carried over from it and one added:
%%   - it ASSEMBLES and introduces no evidence: every figure here is already
%%     published, in the same units, in the section the item \refs;
%%   - every item is something the reader does to their own code, never a number
%%     to quote -- which is what the closing line, kept verbatim, says;
%%   - NO SUMMARY OF THE PAPER.  A reader who wanted the summary read it on page
%%     one; repeating it here would spend 250 words telling them what they were
%%     just told instead of what to do next.
%%
%% ver_A's opening sentence ("Suppose the decision is already yours…") is NOT
%% reused here: it has moved to section 1, where it opens the paper, and a
%% second appearance would blunt it.
%%
%% ⚠ "None of this decides the rewrite for you" USED TO OPEN THIS SECTION and is
%% gone (REVISE part D). The paper said it three times -- twice in section 1 and
%% once here. Once is honest; three times reads as defensive. The one that
%% survives is section 1's "Nothing here settles that argument, because the
%% percentage is not a constant", which is load-bearing there because it sets up
%% the three questions.
%%
%% The six are the outline's six, in the order the paper establishes them: two
%% from cost, two from tools, two from what a proof does not do.  ver_A's thesis
%% sentence is deliberately omitted: it is still an abstraction competing with
%% the last line of the paper.

\section{Six things to do}
\label{sec:close}

What is left is an order in which to ask the questions.

1. **Ask where the bound comes from before you count bounds checks.** If the
   fact that discharges it is already in front of the optimiser — a clamp, a
   length the caller already tested — it costs a flat per-call constant, often
   exactly zero. \ref{sec:cost}
2. **Where the bound is true but not derivable, expect a per-element tax that
   amortises along nothing.** Take the fraction of your own kernel: ours does
   nothing but the loop. \ref{sec:cost}
3. **If you are not going to rewrite it, harden it.** Every build above plain,
   unchecked C matched the model on every hostile input here, at about the same
   cost in either language. \ref{sec:tools}
4. **Put a known-bad input in the sanitizer job and fail the build when nothing
   is reported.** Then delete a check in a branch: if your tests stay green, that
   check is untested. \ref{sec:tools}
5. **Budget a proof at zero extra instructions, about four times the source
   text, and \num{totals.tcb_lines} lines of trusted code somebody has to read.**
   Buy it for memory safety and nothing else. \ref{sec:notdone}
6. **Before trusting any mechanism, name what its guarantee ranges over** —
   values, the execution trace, allocations from this allocator, stack frames,
   the clock. \ref{sec:notdone}

Every step is something you do to your own code. Not one of them is a number you
can quote.
