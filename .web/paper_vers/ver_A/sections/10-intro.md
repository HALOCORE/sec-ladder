%% ver_A -- the introduction.
%%
%% Para 2 is the RELOCATION THESIS in the intro's own voice.  It is the paper's
%% spine.  Each of the three results is headline + one number + one \ref; do NOT
%% re-inline what they gave up -- p02's `_FORTIFY_SOURCE` abort (sec:hostile),
%% p07's asymptote interval (sec:cost), p17's two binaries (sec:proof).
%%
%% Numbers: C's split comes from totals.plain_c.*, never typed.  "Nine of the 22
%% within +-32" is ARM A of `synthesis/census.py` -- do NOT re-derive it from
%% results/synthesis.md's licence column, which has THREE values; treating UNDEC
%% as licensed admits p36 and gives 10/23.

\section{Introduction}
\label{sec:intro}

Every team that has weighed rewriting a C parser in Rust, or putting a verifier
behind the `unsafe` it already ships, asks the same question: *what does memory
safety cost?* The answer usually on offer is a percentage, quoted as though it
were a property of the language.

**No rung of this ladder discharges a safety obligation; each one relocates it**
— off the wire and onto the programmer, off the programmer and onto the language,
off the language and onto a solver — and what is left over after each move is
predictable from the resource the new mechanism quantifies over. This paper
checks that claim rung by rung, in the two units a move is paid in: instructions
executed, and behaviour under an input written to break the kernel.

The percentage fails on its own terms too, and the argument against it is a
measurement rather than a taste. Across \num{totals.patterns} kernels the cost
of the check runs from **exactly zero instructions**, byte-for-byte, to **roughly
half of everything the kernel executes**, and the variable that decides which is
not the language: it is whether the optimiser can see the bound. A single
percentage averages over that distinction and tells a reader nothing they can act
on.

\figure{ladder}{The two climbs. C starts fast and unchecked and adds the check by
hand; Rust starts checked and takes the cost back out. Each row names where the
rung's check lives, and what you are still trusting when you stand on it.}
\label{fig:ladder}

\subsection{Hold the program fixed}

For the kernels measured here, *"C is fast"* and *"C is unsafe"* are the same
sentence: C is fast **precisely in that it skipped the check**. Benchmark a C
program against a Rust one and you have not measured safety — you have measured
two different programs, one that validates its input and one that does not.

So the comparison here holds the *program* fixed and varies only *what enforces
the check*. Every pattern that models a bug ships a **hardened C** rung: the same
kernel, same signature, same driver, plus the bounds check a careful C programmer
writes. That rung separates the two claims. On `p02`, a length-prefixed copy into
a fixed 64-byte destination, the hand-written check costs **+5 instructions per
call with gcc and +12 with clang**, unchanged between the pattern's two inputs;
well-written safe Rust on the same kernel costs **+11** against the unsafe rung.
Safety costs about the same in both languages. What Rust changes is that it is not
optional.
\src{results/synthesis.md}

\subsection{Three results}

**1. Plain, unchecked C fails silently far more often than it crashes.** Of the
\num{totals.plain_c.deviating} (pattern, hostile-input) rows on which it deviates
from the pattern's independent reference model, **\num{totals.plain_c.silent_first}
exit 0 with a plausible wrong answer**; the rest crash or hang. A row is scored by
its *worse* compiler, and worse runs the direction most readers do not expect — a
silent wrong answer is worse than a crash, because nothing collects it.
\ref{sec:hostile} has the denominator, the split under the opposite aggregation
rule, and three detectors' measured blind spots. \src{results/gate/}

**2. The safety tax has two regimes, and only one of them is a percentage.**
Where the optimiser can see the loop bound, well-written safe Rust costs a flat
per-call constant: nine of the 22 patterns licensed for differencing sit within
**±32 instructions per call** on both inputs, so doubling the data does not
double the tax. Where it cannot, the honest worst case is `p07`'s binary search —
`Θ(log n)` probes, no inner loop, nothing to hoist — whose tuned safe rung costs
**exactly 6 instructions per probe** more than the unsafe one and amortises along
nothing. \ref{sec:cost} gives the rule that predicts which regime a kernel is in.
\src{synthesis/census.py}

**3. A memory-safety proof buys memory safety and nothing else.** `p17` ports
CVE-2017-7529. Strip its functional specification and move its guard by one token
— from the logical start to the *slice*-relative index a bounds check actually
constrains — and Verus reports **`10 verified, 0 errors`** for a program that
serves an attacker a neighbouring caller's bytes, with no panic. The same
one-token move in plain safe Rust, in a file with **zero `unsafe` tokens**,
discloses the same window. \ref{sec:proof} has the controls, the other two
instances, and what the obligation count does not measure.
\src{patterns/p17-http-range/NOTES.md}

\subsection{What kind of object a "safety cost" is}

Every number above is a difference between a **pair of spellings**, one endpoint
held fixed by decree. There is no such thing here as *the* safe version of a
kernel — only a class of admissible safe spellings, a class of admissible unsafe
ones, and a difference between the two representatives somebody happened to
write. This project retracted nineteen published claims, and the commonest cause
was that one side had been searched harder than the other: five headlines went
out in the direction that flattered the authors' thesis and passed a fully green
gate doing it \ref{sec:cost}.

We therefore write *"cheapest found"* and never *"minimum"*, name the input as
well as the spelling, and publish the search state beside every row. A reader who
wants one number for the cost of safety is asking a question the record declines
to answer; \ref{sec:lies} says why, and is the section to read before reusing
anything here in an argument.

\subsection{Roadmap}

\ref{sec:whattodo} is the short version: six things to do to your own code, each
pointing at the section that establishes it. \ref{sec:ladder} defines the six
rungs (\ref{fig:ladder}) and names what each one still trusts;
\ref{sec:method} is the apparatus — what a cell is, and why the primary metric is
executed instructions rather than wall clock. Then, in turn: what unchecked C
does under hostile input, what safety costs where it costs anything, and what a
proof buys and forbids. Those feed the core — the **guarantee quadruple**
(property, bearer, quantifier, residual), and a taxonomy of property classes
against the mechanisms that can and cannot reach each — from which the principles
follow. It closes with what this instrument cannot price, how its numbers will
mislead you, what prior work already knew, and what survives all of that.
