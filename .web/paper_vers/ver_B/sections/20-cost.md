\section{What safety costs}
\label{sec:cost}

%% ORDER IS LOAD-BEARING — OUTLINE §0.4 and THE ONE RULE. Problem, obvious
%% answer, the measurement that kills it, and only then the principle. ver_A's
%% `50-cost.md` opened with the `publish the pair` principle because a hostile
%% reviewer said the figures came first; undoing that inversion is why ver_B
%% exists. Do NOT move a principle back above the measurement that motivates it —
%% and that includes `Can the optimiser see the bound?`, which sat ABOVE its own
%% example until REVISE F19 and is now below it. That was the one place this file
%% broke its own header.
%% Every figure here is executed instructions per call at `-O3` in a mode that
%% suppresses inlining — §1 states the unit. Never write "faster" or "slower".
%%
%% ⚠ THE SEARCH-STATE BOOKKEEPING IS GONE ON PURPOSE (REVISE part D). The
%% `undeclared` column, the R-numbers and the 7/3/10 redistribution were the
%% artefact of the point, not the point, and a practitioner stopped reading here.
%% ⚠ If you restore any of it, remember R2: an `undeclared` means NOBODY WROTE AN
%% ENTRY and has never meant nobody searched.

The obvious way to settle that argument is to build both and measure, or to
read a published comparison. Across \num{totals.patterns}
patterns and \num{totals.cells} measured cells, here is what happens when you
try.

\subsection{The number is not a property of the languages}

**A hash probe's published safety cost is `+2` instructions per call, and
rewriting the `unsafe` side of the comparison makes the same cell read `+1021`.**
The safe kernel did not change; the program it was differenced against did — to
another in-contract spelling that verifies at `20 verified, 0 errors`. That is
510× the published figure on the large band, 62.5× on the small. Do the exercise
elsewhere and on two patterns the difference **changes sign**, on one of them
only on the large blob, where safe Rust had been the cheaper rung and on the
small was already the dearer \src{results/SYNTHESIS.md}.

**The safe side moves at least as much, for a reason that has nothing to do with
safety.** The mechanical port — `for i in 0..n { v[i] }`, what a Rust programmer
writes first — carries a median **7.26× the safety tax** the tuned rewrite
carries, across the 17 comparable rows where the tuned rung is the dearer of the
two on the large blob. That is a ratio of *taxes*, `(port − unsafe) / (tuned −
unsafe)`, not of kernels. The median survives searching the unsafe side, and the
port is what most published Rust-versus-C comparisons measure — which makes them
a measure of whether anybody tuned it.

\subsection{Five rungs, because two cannot state a difference}

Those two numbers moved by three orders of magnitude with the safe kernel
untouched, which is why nothing here compares *C* against *Rust*. Every pattern
is built at five rungs: **plain, unchecked C** carrying the bug the pattern is
about, built plain and again hardened by hand; **safe Rust, mechanically
ported**; **safe Rust, tuned** to help the optimiser, still zero `unsafe`;
**unsafe Rust**, `get_unchecked` and raw pointers, correct but unverified; and
**unsafe Rust with a machine-checked proof** of every unsafe precondition.

\figure{ladder}{The five rungs. A safety-cost figure is a difference between two of them, and which two decides the number.}
\label{fig:ladder}

\begin{principle}{Publish the pair, and name the side you did not search}
On most rows here one side was searched for a cheaper spelling and the other was
not \src{results/SYNTHESIS.md}. **A safety-cost number ships as a triple: the
number, the pair of spellings it is a difference of, and which side anybody
tried to make fast.** Without the
other two it is a bound with one endpoint held by decree. Never difference two
cheapest-found spellings — one upper bound minus another bounds nothing.
\end{principle}

\subsection{Where the cost comes from}

\begin{example}{The check that costs exactly nothing}
A bounded stack's tuned safe rung costs `+359` instructions per call on the
small blob and `+626` on the large one against its unsafe rung. Add one provably
dead line at the top of the loop — `if sp > STACK_CAP { return 0; }`, the
proof's own invariant handed to the optimiser as unreachable code — and the safe
rung goes from 17 instructions per executed pop to 13, the unsafe rung from 14
to 13. **The gap per pop becomes exactly zero, over 19 blobs, zero fitted
parameters, maximum residual 0.000000**
\src{patterns/p03-bounded-stack/NOTES.md}. Counting checks predicted `+626`.

Two qualifications make it a result. It is that invariant specifically:
`sp > 1000` leaves the binary byte-identical and `sp > 65` leaves the check
standing and costs more. And it is not about Rust: hand either gcc or clang the
same clamp and both delete all of it, which licenses **both compilers here**,
never *any compiler*.

One limit, pointing the other way: exactly zero is per *executed* pop. The dead
test costs `+2` per *dropped* push, so on a blob that overflows the stack the
clamped rung is `+502` per call.
\end{example}

\begin{principle}{Can the optimiser see the bound?}
A bounds check costs what the optimiser cannot delete. Where the fact that
discharges it is already in front of the middle-end — a clamp, a modulus, a
length the caller already tested — the tax is a per-call constant, flat in the
size of the data, often exactly zero. Where the fact is true but not derivable
there, the check survives as a per-element cost that amortises along no axis. So
ask of a rewrite not *how many bounds checks does it have* but **where does the
bound come from, and does the compiler get to see it there?**
\end{principle}

\begin{example}{The honest worst case, and the paper catching itself}
A binary search has `Θ(log n)` probes, no inner loop and nothing to hoist —
where the rule predicts a real tax, and the tax is there.
The shipped tuned safe rung costs exactly 6 instructions per probe more
than the unsafe one, and because everything that could dilute that constant is
`O(1)`, the tax rises as a share of the kernel: 42.5 % at `n = 7`, 46.6 % at
`n = 16 385`, still climbing, monotone across six different workloads
\src{patterns/p07-binary-search/NOTES.md}.

%% ⚠⚠ R2 (RULINGS.md). The outline's version of this beat — "the search state is
%% `undeclared`, so neither side was searched" — is FALSE and must not come
%% back. `results/synthesis.md:668`: "An `undeclared` in this column means
%% nobody wrote an entry, and it has never meant nobody searched." The truth is
%% p07 NOTES §10a: four in-contract safe spellings, the shipped one dearest,
%% span exactly the probe count per call. Write "cheapest found", NEVER
%% "minimum" — six published minima on this project have been refuted.
%% ⚠ PROTECTED PASSAGE (REVISE part E). Three reviewers named this beat.
Now apply this section's rule to this section's worst number. The shipped safe
spelling is the dearest of four that satisfy the pattern's contract; the
cheapest found, `&buf[ep..][..4]`, pays 5 per probe, and the span between them
is exactly the probe count per call: one instruction per probe and nothing else.
**The honest worst case is about 5 instructions per probe for the cheapest safe
spelling anybody has found, and 6 for the one that shipped**, moving the
asymptotic share from `[46 %, 50 %]` to `[38 %, 42 %]`. The rule moved this
paper's own headline by a sixth.

That share is of a kernel that does nothing else. The per-probe constant
transfers to your code; the percentage does not, and it can only shrink, because
your function does other work.
\end{example}

\subsection{Writing the check is cheap; forgetting it is not}

%% ⚠⚠ R3 (RULINGS.md). +5/+12 is ONE pattern; FACTS.md B-5 forbids it unscoped.
%% Re-derived here against `results/p*.json` (O3, isolated, per call): 25
%% patterns ship a hardened rung, median 24, gcc −125…+10242, clang −108…+5637,
%% negative in 4 of the 50 (pattern × compiler) columns over 3 patterns (p06,
%% p12, p23). Do not drop the median sentence: +5/+12 is not publishable alone.
%% ⚠ REVISE part C2: gcc DEFAULTS to `-fcf-protection=full` here, so its column
%% carries an `endbr64` landing pad clang's and rustc's do not, and
%% `results/synthesis.md` §4 forbids attributing a gcc-vs-clang gap to codegen
%% without naming it. The within-compiler clause below is mandatory.
%%literal-ok 108
**On a buffer copy — where the hardened C rung differs from the plain one by the
check and nothing else — the check costs `+5` instructions per call under gcc
and `+12` under clang, flat from a 61-byte copy to a 4,092-byte one, against the
same pattern's tuned safe Rust at `+11`.** A check is a compare and a branch in
both languages. Each figure is a difference taken **within one compiler**,
because gcc on this box defaults to `-fcf-protection=full` and opens every
function with a landing pad clang's column and rustc's do not carry.

That is one pattern, and the scope is the point. Across the 25 that ship a
hardened rung the hardened-minus-plain difference has a median of 24
instructions per call, runs −125 to +10,242 under gcc and −108 to +5,637 under
clang, and is negative in four of the fifty pattern-and-compiler columns. What
survives is **writing the check is cheap where the check is all you are adding**
— not that hardening is free, because a hardened rung means different work in
different kernels.

\begin{takeaway}
Writing the check costs about the same in both languages. What Rust changes is
not the price of the check but the possibility of forgetting it, and
\ref{sec:tools} is what you would see if it were.
\end{takeaway}

\subsection{The spread is the finding}

\figure{rungcost}{Tuned safe Rust against unsafe Rust, one bar per pattern, on the small blob at one inlining mode. The spread, not the centre, is the finding.}
\label{fig:rungcost}

Eight tuned-against-unsafe rows, and two more showing what the untuned port
costs, because every other cost figure in this paper is the tuned rung
\src{results/SYNTHESIS.md}:

| pattern | small | large | what the difference is |
|---|---:|---:|---|
| \pat{p22} | +2 | +2 | against another in-contract unsafe rung, +125 / +1021 |
| \pat{p04} | +5 | +5 | `urem`'s known-bits fact; at capacity 60, +479 |
| \pat{p02} | +11 | +11 | the check itself, flat in the copy length |
| \pat{p17} | +32 | +32 | one spelling, not a law: a respelling is −19 flat |
| \pat{p27} | +110 | +662 | drop glue, and **not a licensed difference**: only one rung dispatches indirectly |
| \pat{p03} | +359 | +626 | 0 per pop once the optimiser has the invariant |
| \pat{p07} | +3015 | +10025 | a real per-probe check, 5 to 6 instructions |
| \pat{p13} | −177 | −1054 | flips to +44 / +77 against a searched unsafe rung |
| \pat{p02}, mechanical port | +191 | +1439 | the same kernel, untuned |
| \pat{p04}, mechanical port | +4756 | +16616 | the same kernel, untuned |

Of the 22 rows that can honestly be differenced, nine sit within ±32
instructions per call on both blobs and nine exceed 100 on at least one, and the
two groups overlap. Read the big ones before calling them safety: that handle
table is drop glue with the allocator calls equal to the last digit between the
rungs \src{patterns/p27-handle-table/NOTES.md}, a rotate's difference is an
iterator adaptor's two exhaustion tests per item, and a bignum
multiply-accumulate's negative row is one unrolling decision whose per-MAC
safety tax is exactly zero.

\begin{takeaway}
Not one of those three is a bounds check. Before attributing a gap to memory
safety, find the instructions and read them. Then walk your own hot loops
and ask where the bound comes from — and where the compiler cannot see it there,
put the fact in front of it and measure again.
\end{takeaway}
